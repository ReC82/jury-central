"""Ticket #92 — BLOQUANT démarrage : rendre la génération de session asynchrone pour
supprimer les 504.

Bug réel reproduit en staging : `504 Gateway Time-out` sur `/uaa/ampcr-mc38/exam/start`
— cette route restait SYNCHRONE pendant toute la sélection banque/génération IA/
composition MC38/validation/persistance. Le ticket #71 (spinner, anti-double-clic) ne
résout que l'UX, jamais le timeout HTTP lui-même. Correctif : `POST .../start` ne
construit plus jamais la session dans la requête — il crée/retrouve un `SessionBuildJob`
persistant (`app.v1.session_service.enqueue_session_build`) et redirige IMMÉDIATEMENT
vers une page d'attente qui interroge `GET /session-build-jobs/{id}/status`. La
construction réelle (`start_session`/`_start_mc38_transversal_session`, INCHANGÉES depuis
#55/#58/#64/#68/#69/#70/#71/#82) est exécutée par le même worker que #88
(`app.v1.correction_worker`, étendu pour traiter aussi cette file), jamais dans le cycle
requête/réponse HTTP.

Aucun appel OpenAI réel : `FakeAIProvider` partout (et une variante délibérément ralentie
pour la preuve de non-blocage, § 14 du ticket).
"""

import re
import time

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.models import (
    QuestionnaireSession,
    SessionBuildJob,
    SessionBuildJobStatus,
    SessionDifficultyRequest,
    SessionMode,
    User,
)
from app.v1.session_service import (
    SessionBuildJobNotFailedError,
    claim_next_pending_build_job,
    enqueue_session_build,
    get_session_build_job,
    recover_stale_build_jobs,
    retry_session_build_job,
    run_session_build_job,
)

# =============================================================================================
# Helpers
# =============================================================================================


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch, fake=None):
    fake = fake if fake is not None else FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _seed_mc01(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    return ampcr, mc01


def _seed_francais(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    return francais, c01


def _register_and_login(client, email="ticket92-http@example.test"):
    r = client.get("/register")
    token = _csrf(r.text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "T92",
        },
    )


def _run_pending_build_job(db_session, provider):
    job = claim_next_pending_build_job(db_session)
    if job is not None:
        run_session_build_job(db_session, job=job, provider=provider)
    return job


class _SlowFakeAIProvider(FakeAIProvider):
    """FakeAIProvider dont la génération est délibérément ralentie — utilisé pour prouver
    (§ 14 du ticket) que `POST .../start` ne dépend plus de la durée du fournisseur IA."""

    def __init__(self, delay_seconds: float = 0.3):
        super().__init__()
        self._delay_seconds = delay_seconds

    def generate_questionnaire(self, request):
        time.sleep(self._delay_seconds)
        return super().generate_questionnaire(request)


# =============================================================================================
# 1. Le POST .../start ne bloque jamais — création de job, jamais d'appel IA
# =============================================================================================


def test_practice_start_creates_pending_job_without_calling_ai(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    user = User(email="t92@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    job = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    assert job.status == SessionBuildJobStatus.PENDING
    assert len(fake.questionnaire_calls) == 0, "enqueue_session_build ne doit jamais appeler l'IA"


def test_practice_start_http_response_is_fast_even_with_slow_provider(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    slow = _SlowFakeAIProvider(delay_seconds=2.0)
    _patch_fake_provider(monkeypatch, slow)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)

    t0 = time.monotonic()
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0

    assert r.status_code == 303
    assert r.headers["location"].startswith("/session-build-jobs/")
    assert elapsed < 1.0, f"le POST start a pris {elapsed:.2f}s — ne doit jamais attendre le fournisseur IA (2s)"


def test_exam_start_http_response_is_fast_even_with_slow_provider(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    slow = _SlowFakeAIProvider(delay_seconds=2.0)
    _patch_fake_provider(monkeypatch, slow)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/exam")
    token = _csrf(r.text)

    t0 = time.monotonic()
    r = client.post("/uaa/ampcr-mc01/exam/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0

    assert r.status_code == 303
    assert r.headers["location"].startswith("/session-build-jobs/")
    assert elapsed < 1.0


# =============================================================================================
# 2. MC38 et Français : architecture générique, aucune logique spécifique
# =============================================================================================


def test_mc38_exam_start_nonblocking_and_completes(client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc38/exam")
    token = _csrf(r.text)
    t0 = time.monotonic()
    r = client.post("/uaa/ampcr-mc38/exam/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0
    assert r.status_code == 303
    assert elapsed < 1.0
    job_url = r.headers["location"]
    assert job_url.startswith("/session-build-jobs/")

    job_id = int(job_url.rstrip("/").split("/")[-1])
    job = get_session_build_job(db_session, job_id=job_id)
    assert job.uaa_code == "MC38"

    _run_pending_build_job(db_session, fake)
    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.READY
    assert job.created_session_id is not None

    session = db_session.get(QuestionnaireSession, job.created_session_id)
    assert session.question_count >= 1


def test_francais_practice_start_nonblocking_and_completes(client, db_session, monkeypatch):
    _seed_francais(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/francais-c01/practice")
    token = _csrf(r.text)
    t0 = time.monotonic()
    r = client.post("/uaa/francais-c01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0
    assert r.status_code == 303
    assert elapsed < 1.0
    job_url = r.headers["location"]
    assert job_url.startswith("/session-build-jobs/")

    job_id = int(job_url.rstrip("/").split("/")[-1])
    _run_pending_build_job(db_session, fake)
    job = get_session_build_job(db_session, job_id=job_id)
    assert job.status == SessionBuildJobStatus.READY
    assert job.created_session_id is not None


def test_global_ampcr_practice_start_nonblocking(client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/modules/ampcr/practice")
    token = _csrf(r.text)
    t0 = time.monotonic()
    r = client.post("/modules/ampcr/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0
    assert r.status_code == 303
    assert elapsed < 1.0
    assert r.headers["location"].startswith("/session-build-jobs/")


def test_global_ampcr_exam_start_nonblocking(client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/modules/ampcr/exam")
    token = _csrf(r.text)
    t0 = time.monotonic()
    r = client.post("/modules/ampcr/exam/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    elapsed = time.monotonic() - t0
    assert r.status_code == 303
    assert elapsed < 1.0
    assert r.headers["location"].startswith("/session-build-jobs/")


# =============================================================================================
# 3. Idempotence : double start = 1 job = 1 session
# =============================================================================================


def test_double_enqueue_at_service_level_creates_single_job(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    user = User(email="t92b@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    job_1 = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    job_2 = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.EASY, question_count=10,
    )
    assert job_1.id == job_2.id
    assert (
        db_session.query(SessionBuildJob)
        .filter_by(user_id=user.id, module_id=ampcr.id, uaa_id_key=mc01.id, mode=SessionMode.PRACTICE)
        .count()
        == 1
    )


def test_double_post_start_creates_single_job_and_single_created_session(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)

    first = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    second = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    assert first.status_code == 303
    assert second.status_code == 303
    assert first.headers["location"] == second.headers["location"]

    job_id = int(first.headers["location"].rstrip("/").split("/")[-1])
    assert db_session.query(SessionBuildJob).count() == 1

    _run_pending_build_job(db_session, fake)
    job = get_session_build_job(db_session, job_id=job_id)
    assert job.status == SessionBuildJobStatus.READY
    assert db_session.query(QuestionnaireSession).count() == 1


def test_different_uaa_or_mode_gets_independent_jobs(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    user = User(email="t92c@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    job_practice = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    job_exam = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    assert job_practice.id != job_exam.id


# =============================================================================================
# 4. Page d'attente : refresh, READY redirect, FAILED, retry
# =============================================================================================


def test_wait_page_survives_refresh(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]

    r1 = client.get(job_url)
    r2 = client.get(job_url)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert "Préparation de l'entraînement" in r1.text
    assert db_session.query(SessionBuildJob).count() == 1


def test_ready_job_redirects_to_created_session(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]

    job = _run_pending_build_job(db_session, fake)
    assert job.status == SessionBuildJobStatus.READY

    r = client.get(job_url, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{job.created_session_id}"


def test_failed_job_shows_failure_page_with_retry_button(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]
    job_id = int(job_url.rstrip("/").split("/")[-1])

    job = get_session_build_job(db_session, job_id=job_id)
    job.status = SessionBuildJobStatus.FAILED
    job.error_message = "panne simulée"
    db_session.commit()

    r = client.get(job_url)
    assert r.status_code == 200
    assert "a échoué" in r.text
    assert "Réessayer" in r.text
    assert "/session-build-jobs/" in r.text and "/retry" in r.text


def test_retry_reuses_same_job_and_eventually_succeeds(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]
    job_id = int(job_url.rstrip("/").split("/")[-1])

    job = get_session_build_job(db_session, job_id=job_id)
    job.status = SessionBuildJobStatus.FAILED
    job.error_message = "panne"
    db_session.commit()

    r = client.get(job_url)
    token = _csrf(r.text)
    r = client.post(f"/session-build-jobs/{job_id}/retry", data={"csrf_token": token}, follow_redirects=False)
    assert r.status_code == 303

    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.PENDING
    assert job.error_message is None

    _run_pending_build_job(db_session, fake)
    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.READY
    assert db_session.query(SessionBuildJob).filter_by(user_id=job.user_id).count() == 1, "jamais une seconde session fantôme"


def test_retry_raises_when_job_not_failed(db_session, monkeypatch):
    import pytest

    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    user = User(email="t92d@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    job = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    run_session_build_job(db_session, job=job, provider=fake)

    with pytest.raises(SessionBuildJobNotFailedError):
        retry_session_build_job(db_session, job=job)


# =============================================================================================
# 5. Crash / job bloqué (stale recovery)
# =============================================================================================


def test_stale_running_build_job_requeued_to_pending(db_session, monkeypatch):
    from datetime import UTC, datetime, timedelta

    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    user = User(email="t92e@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    job = claim_next_pending_build_job(db_session)
    job.started_at = datetime.now(UTC) - timedelta(seconds=999)
    db_session.commit()

    report = recover_stale_build_jobs(db_session, stale_after_seconds=300, max_attempts=3)
    assert report["requeued"] == 1
    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.PENDING


def test_stale_build_job_becomes_failed_after_max_attempts(db_session, monkeypatch):
    from datetime import UTC, datetime, timedelta

    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    user = User(email="t92f@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    job = claim_next_pending_build_job(db_session)
    job.attempt_count = 3
    job.started_at = datetime.now(UTC) - timedelta(seconds=999)
    db_session.commit()

    report = recover_stale_build_jobs(db_session, stale_after_seconds=300, max_attempts=3)
    assert report["failed"] == 1
    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.FAILED


# =============================================================================================
# 6. Anti-doublon intra-session (#82) toujours actif via le nouveau chemin
# =============================================================================================


def test_intrasession_dedup_still_applies_through_async_path(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    user = User(email="t92g@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    job = enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )
    run_session_build_job(db_session, job=job, provider=fake)
    db_session.refresh(job)
    session = db_session.get(QuestionnaireSession, job.created_session_id)

    version_ids = [sq.question_version_id for sq in session.session_questions]
    question_ids = [sq.question_version.question_id for sq in session.session_questions]
    assert len(version_ids) == len(set(version_ids))
    assert len(question_ids) == len(set(question_ids))


# =============================================================================================
# 7. Logout/login pendant une préparation en cours
# =============================================================================================


def test_logout_login_resumes_build_wait_state(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]

    r = client.get(job_url)
    logout_token = _csrf(r.text)
    client.post("/logout", data={"csrf_token": logout_token})

    r = client.get(job_url, follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers["location"]

    r = client.get("/login")
    token = _csrf(r.text)
    client.post("/login", data={"csrf_token": token, "email": "ticket92-http@example.test", "password": "test-password-1234"})

    r = client.get(job_url)
    assert r.status_code == 200
    assert "Préparation" in r.text


def test_mes_sessions_shows_build_in_progress(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)

    r = client.get("/mes-sessions")
    assert r.status_code == 200
    assert "en préparation" in r.text


def test_status_endpoint_requires_ownership(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client, email="owner92@example.test")

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    job_url = r.headers["location"]

    _register_and_login(client, email="intruder92@example.test")
    r = client.get(f"{job_url}/status")
    assert r.status_code == 404


# =============================================================================================
# 8. Worker (module.app.v1.correction_worker étendu)
# =============================================================================================


def test_worker_loop_processes_build_jobs_too(db_session, monkeypatch):
    from app.v1.correction_worker import run_worker_loop

    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: fake)
    user = User(email="t92h@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    enqueue_session_build(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc01.id, uaa_code="MC01",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, question_count=10,
    )

    run_worker_loop(poll_interval_seconds=0, stale_check_interval_seconds=9999, max_iterations=1)

    job = db_session.query(SessionBuildJob).first()
    db_session.refresh(job)
    assert job.status == SessionBuildJobStatus.READY


def test_worker_process_one_build_job_returns_false_when_idle():
    from app.v1.correction_worker import process_one_build_job

    assert process_one_build_job() is False

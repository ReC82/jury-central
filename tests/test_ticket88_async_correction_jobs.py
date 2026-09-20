"""Ticket #88 — BLOQUANT correction : supprimer les 504 avec une correction asynchrone
persistée.

Bug réel reproduit en staging : `504 Gateway Time-out` sur `POST /sessions/{id}/submit`
— cette route restait SYNCHRONE pendant toute la correction batch IA ; si OpenAI +
post-traitement dépasse le timeout nginx/upstream, nginx coupe la connexion même si le
backend continue de travailler. Correctif : `POST /sessions/{id}/submit` ne fait plus
JAMAIS l'appel IA — il verrouille la session, crée/retrouve un `CorrectionJob` persistant
(`app.v1.session_service.enqueue_correction`) et redirige IMMÉDIATEMENT vers une page
d'attente qui interroge `GET /sessions/{id}/correction-status`. La correction réelle est
exécutée par un worker séparé (`app.v1.correction_worker`), jamais dans le cycle
requête/réponse HTTP.

`submit_session`/`_correct_and_finalize_claimed_session` (tickets #55/#62/#70/#71)
restent INCHANGÉS — réutilisés tels quels par `run_correction_job` comme corps réel du
travail de correction. Aucun appel OpenAI réel : `FakeAIProvider` partout.
"""

import re
import time

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AIProviderError
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import (
    CorrectionJob,
    CorrectionJobStatus,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.session_service import (
    CorrectionJobNotRetryableError,
    claim_next_pending_correction_job,
    enqueue_correction,
    get_correction_job,
    recover_stale_correction_jobs,
    retry_correction_job,
    run_correction_job,
    submit_session,
)

# =============================================================================================
# Helpers
# =============================================================================================


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch, fake=None):
    fake = fake or FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _seed_mc01(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    return ampcr, mc01


def _build_minimal_session(db_session, ampcr, mc01, *, question_type="short_answer", content=None):
    user = User(email="ticket88@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    content = content or {"prompt": "Question de test #88.", "rubric": "Grille."}
    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type=question_type,
        content_json=content, generation_source="manual",
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=ampcr.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0)
    )
    db_session.commit()
    return user, session


def _register_and_login(client, email="ticket88-http@example.test"):
    r = client.get("/register")
    token = _csrf(r.text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "T88",
        },
    )


def _start_practice_and_answer_all(client, *, uaa_slug="ampcr-mc01"):
    r = client.get(f"/uaa/{uaa_slug}/practice")
    token = _csrf(r.text)
    r = client.post(
        f"/uaa/{uaa_slug}/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_url = r.headers["location"]
    session_id = int(session_url.rstrip("/").split("/")[-1])

    position = 1
    while True:
        r = client.get(f"{session_url}?q={position}")
        if r.status_code != 200:
            break
        token = _csrf(r.text)
        direction = "submit" if "Terminer" in r.text else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if 'name="option_id"' in r.text:
            m = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', r.text)
            if m:
                data["option_id"] = m.group(1)
        elif 'name="text"' in r.text:
            data["text"] = "Reponse de test couvrant plusieurs aspects."
        r = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        if direction == "submit":
            break
        position += 1

    return session_id, session_url


class _SlowFakeAIProvider(FakeAIProvider):
    """FakeAIProvider dont la correction sémantique est délibérément ralentie —
    utilisé pour prouver (§ 13 du ticket) que `POST /sessions/{id}/submit` ne dépend plus
    de la durée du fournisseur IA. Délai court (secondes, pas 60s) : suffisant pour
    distinguer "réponse HTTP quasi instantanée" de "appel IA effectivement exécuté",
    jamais un test qui ralentit réellement la suite."""

    def __init__(self, delay_seconds: float = 0.3):
        super().__init__()
        self._delay_seconds = delay_seconds

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        time.sleep(self._delay_seconds)
        return super().correct_semantic_batch(questions, answers, severity, contexts)


# =============================================================================================
# 1. Le POST /submit ne bloque jamais — création de job, pas d'appel IA
# =============================================================================================


def test_submit_creates_pending_job_and_locks_session_without_calling_ai(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)

    job = enqueue_correction(db_session, session=session, severity_ui=3)

    assert job.status == CorrectionJobStatus.PENDING
    assert job.session_id == session.id
    db_session.refresh(session)
    assert session.status == SessionStatus.CORRECTING
    assert len(fake.semantic_calls) == 0, "enqueue_correction ne doit jamais appeler l'IA"


def test_submit_http_response_is_fast_even_with_slow_provider(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    slow = _SlowFakeAIProvider(delay_seconds=2.0)
    _patch_fake_provider(monkeypatch, slow)

    _register_and_login(client)
    _session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)

    t0 = time.monotonic()
    r = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    elapsed = time.monotonic() - t0

    assert r.status_code == 303
    assert elapsed < 1.0, f"le POST submit a pris {elapsed:.2f}s — ne doit jamais attendre le fournisseur IA (2s)"
    assert len(slow.semantic_calls) == 0, "l'appel IA ne doit jamais avoir lieu dans la requête HTTP"


# =============================================================================================
# 2. États du job : PENDING -> RUNNING -> COMPLETED, résultats corrects
# =============================================================================================


def test_job_transitions_pending_running_completed(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)

    job = claim_next_pending_correction_job(db_session)
    assert job is not None
    assert job.status == CorrectionJobStatus.RUNNING
    assert job.started_at is not None
    assert job.attempt_count == 1

    result = run_correction_job(db_session, job=job, provider=fake)
    assert result.status == CorrectionJobStatus.COMPLETED
    assert result.completed_at is not None

    db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED
    assert session.score is not None


def test_claim_next_pending_returns_none_when_nothing_to_do(db_session):
    assert claim_next_pending_correction_job(db_session) is None


def test_worker_produces_correct_score_and_feedback(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)

    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=fake)

    db_session.refresh(session)
    answer = session.session_questions[0].answer
    assert answer.feedback_json is not None
    assert "correct" in answer.feedback_json


def test_original_severity_persisted_after_async_correction(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=5)

    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=fake)

    db_session.refresh(session)
    assert (session.parameters_json or {}).get("severity") == 5


# =============================================================================================
# 3. Idempotence : double POST = 1 job = 1 appel IA
# =============================================================================================


def test_double_enqueue_at_service_level_creates_single_job(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)

    job_1 = enqueue_correction(db_session, session=session, severity_ui=3)
    job_2 = enqueue_correction(db_session, session=session, severity_ui=4)

    assert job_1.id == job_2.id
    assert db_session.query(CorrectionJob).filter_by(session_id=session.id).count() == 1


def test_double_post_submit_creates_single_job_and_single_ai_call(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)

    first = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    second = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    assert first.status_code == 303
    assert second.status_code == 303

    assert db_session.query(CorrectionJob).filter_by(session_id=session_id).count() == 1

    job = get_correction_job(db_session, session_id=session_id)
    run_correction_job(db_session, job=job, provider=fake)

    assert len(fake.semantic_calls) == 1, "un seul appel IA malgré le double POST"


# =============================================================================================
# 4. Page d'attente : refresh, /mes-sessions, logout/login
# =============================================================================================


def test_correcting_page_survives_refresh(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    r1 = client.get(session_url)
    r2 = client.get(session_url)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert "Correction en cours" in r1.text
    assert "Correction en cours" in r2.text
    assert db_session.query(CorrectionJob).filter_by(session_id=session_id).count() == 1


def test_my_sessions_shows_correcting_state(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    _session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    r = client.get("/mes-sessions")
    assert r.status_code == 200
    assert "Correction en cours" in r.text


def test_logout_login_resumes_correcting_state(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    _session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    r = client.get(session_url)
    logout_token = _csrf(r.text)
    client.post("/logout", data={"csrf_token": logout_token})
    r = client.get(session_url, follow_redirects=False)
    assert r.status_code == 303  # redirigé vers /login, plus de session active

    r = client.get("/login")
    token = _csrf(r.text)
    client.post("/login", data={"csrf_token": token, "email": "ticket88-http@example.test", "password": "test-password-1234"})

    r = client.get(session_url)
    assert r.status_code == 200
    assert "Correction en cours" in r.text


# =============================================================================================
# 5. FAILED + retry
# =============================================================================================


def test_unexpected_exception_marks_job_failed_not_ai_provider_error(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)

    def _boom(*a, **k):
        raise RuntimeError("panne inattendue simulée")

    monkeypatch.setattr("app.v1.session_service.correct_session_hybrid_resumable", _boom)
    result = run_correction_job(db_session, job=job, provider=fake)

    assert result.status == CorrectionJobStatus.FAILED
    assert "panne inattendue simulée" in result.error_message
    db_session.refresh(session)
    assert session.status == SessionStatus.CORRECTING, "réponses restent verrouillées, jamais IN_PROGRESS"


def test_ai_provider_error_on_semantic_question_is_incomplete_not_completed(db_session, monkeypatch):
    """Corrigé par le ticket #90 (§ AUCUN FAUX 0 SI CORRECTION IA INDISPONIBLE) : ce test
    affirmait à l'origine (#88) qu'`AIProviderError` était toujours absorbée par un repli
    local qui finalisait `COMPLETED` — exactement le bug réel rapporté en staging (un 0
    fabriqué pour une question qui avait réellement besoin de l'IA). La question par
    défaut de `_build_minimal_session` (`short_answer` sans `accepted_answers`) a
    réellement besoin de l'IA (`requires_ai_correction() == True`) : le job devient
    désormais `INCOMPLETE`, jamais `COMPLETED` avec un score inventé — voir
    `tests/test_ticket90_correction_failure_integrity.py` pour la couverture complète
    (le repli local existant reste inchangé pour les questions déterministes déjà
    correctement notées, dont le score ne dépend jamais de l'IA)."""
    ampcr, mc01 = _seed_mc01(db_session)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)

    class _FailingProvider(FakeAIProvider):
        def correct_semantic_batch(self, *a, **k):
            raise AIProviderError("service indisponible")

    result = run_correction_job(db_session, job=job, provider=_FailingProvider())
    assert result.status == CorrectionJobStatus.INCOMPLETE
    db_session.refresh(session)
    assert session.status == SessionStatus.CORRECTION_INCOMPLETE
    assert session.score is None


def test_failed_job_shows_failure_page_with_retry_button(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    job = get_correction_job(db_session, session_id=session_id)
    job.status = CorrectionJobStatus.FAILED
    job.error_message = "panne simulée"
    db_session.commit()

    r = client.get(session_url)
    assert r.status_code == 200
    assert "n&#39;a pas pu être terminée" in r.text or "n'a pas pu être terminée" in r.text
    assert "Réessayer la correction" in r.text
    assert "retry-correction" in r.text


def test_retry_failed_job_resets_to_pending_without_touching_answers(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    job.status = CorrectionJobStatus.FAILED
    job.error_message = "panne"
    db_session.commit()

    original_answer = session.session_questions[0].answer

    retried = retry_correction_job(db_session, job=job, session=session)
    assert retried.status == CorrectionJobStatus.PENDING
    assert retried.error_message is None
    assert retried.attempt_count == 0
    db_session.refresh(session)
    assert session.session_questions[0].answer is original_answer or session.session_questions[0].answer is None


def test_retry_raises_when_job_not_failed(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=fake)

    import pytest

    with pytest.raises(CorrectionJobNotRetryableError):
        retry_correction_job(db_session, job=job, session=session)


def test_retry_route_does_not_duplicate_a_successful_correction(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    job = get_correction_job(db_session, session_id=session_id)
    run_correction_job(db_session, job=job, provider=fake)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text) if "csrf_token" in r.text else token
    r = client.post(f"{session_url}/retry-correction", data={"csrf_token": token}, follow_redirects=False)
    assert r.status_code == 303

    assert db_session.query(CorrectionJob).filter_by(session_id=session_id).count() == 1
    assert len(fake.semantic_calls) == 1


# =============================================================================================
# 6. Crash / job bloqué (stale recovery)
# =============================================================================================


def test_stale_running_job_requeued_to_pending(db_session, monkeypatch):
    from datetime import UTC, datetime, timedelta

    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    job.started_at = datetime.now(UTC) - timedelta(seconds=999)
    db_session.commit()

    report = recover_stale_correction_jobs(db_session, stale_after_seconds=300, max_attempts=3)
    assert report["requeued"] == 1
    assert report["failed"] == 0
    db_session.refresh(job)
    assert job.status == CorrectionJobStatus.PENDING
    assert job.started_at is None


def test_stale_job_becomes_failed_after_max_attempts(db_session, monkeypatch):
    from datetime import UTC, datetime, timedelta

    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    job.attempt_count = 3
    job.started_at = datetime.now(UTC) - timedelta(seconds=999)
    db_session.commit()

    report = recover_stale_correction_jobs(db_session, stale_after_seconds=300, max_attempts=3)
    assert report["failed"] == 1
    assert report["requeued"] == 0
    db_session.refresh(job)
    assert job.status == CorrectionJobStatus.FAILED
    assert job.error_message


def test_recent_running_job_not_touched_by_stale_recovery(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)

    report = recover_stale_correction_jobs(db_session, stale_after_seconds=300, max_attempts=3)
    assert report["requeued"] == 0
    assert report["failed"] == 0
    db_session.refresh(job)
    assert job.status == CorrectionJobStatus.RUNNING


# =============================================================================================
# 7. Réponses immuables dès submit
# =============================================================================================


def test_answers_immutable_once_correcting(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    _session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    r = client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "next", "text": "tentative de modification"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == session_url, "redirigé vers la page de session, jamais une écriture acceptée"


def test_autosave_still_works_while_in_progress(client, db_session, monkeypatch):
    """Non-régression : le flux normal (répondre pendant IN_PROGRESS) n'est pas affecté."""
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_url = r.headers["location"]
    r = client.get(f"{session_url}?q=1")
    assert r.status_code == 200
    token = _csrf(r.text)
    data = {"csrf_token": token, "position": 1, "direction": "next"}
    if 'name="option_id"' in r.text:
        m = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', r.text)
        if m:
            data["option_id"] = m.group(1)
    elif 'name="text"' in r.text:
        data["text"] = "Reponse normale."
    r = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
    assert r.status_code == 303
    assert "?q=2" in r.headers["location"]


# =============================================================================================
# 8. Export après correction
# =============================================================================================


def test_export_works_after_async_correction(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    job = get_correction_job(db_session, session_id=session_id)
    run_correction_job(db_session, job=job, provider=fake)

    r = client.get(f"{session_url}/export.md")
    assert r.status_code == 200
    assert len(r.text) > 0


# =============================================================================================
# 9. Non-régression #70/#71 : submit_session (fonction synchrone) reste directement utilisable
# =============================================================================================


def test_submit_session_function_unchanged_and_still_directly_usable(db_session, monkeypatch):
    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _, session = _build_minimal_session(db_session, ampcr, mc01)

    result = submit_session(db_session, session=session, provider=fake, severity_ui=3)
    assert result.status == SessionStatus.COMPLETED
    assert result.score is not None


# =============================================================================================
# 10. Endpoint de polling
# =============================================================================================


def test_correction_status_endpoint_reports_states(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client)
    session_id, session_url = _start_practice_and_answer_all(client)

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    r = client.get(f"{session_url}/correction-status")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"

    job = get_correction_job(db_session, session_id=session_id)
    run_correction_job(db_session, job=job, provider=fake)

    r = client.get(f"{session_url}/correction-status")
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_correction_status_endpoint_requires_ownership(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    _register_and_login(client, email="owner88@example.test")
    _session_id, session_url = _start_practice_and_answer_all(client)
    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    # `/register` réauthentifie sur le nouveau compte quel que soit l'état de connexion
    # précédent (écrase le cookie de session) — pas besoin d'un `/logout` explicite ici.
    _register_and_login(client, email="intruder88@example.test")
    r = client.get(f"{session_url}/correction-status")
    assert r.status_code == 404


# =============================================================================================
# 11. Worker : boucle bornée (module.app.v1.correction_worker)
# =============================================================================================


def test_worker_loop_processes_pending_jobs_and_stops_at_max_iterations(db_session, monkeypatch):
    from app.v1.correction_worker import run_worker_loop

    ampcr, mc01 = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: fake)
    _, session = _build_minimal_session(db_session, ampcr, mc01)
    enqueue_correction(db_session, session=session, severity_ui=3)

    run_worker_loop(poll_interval_seconds=0, stale_check_interval_seconds=9999, max_iterations=1)

    db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED


def test_worker_process_one_job_returns_false_when_idle(monkeypatch):
    from app.v1.correction_worker import process_one_job

    assert process_one_job() is False

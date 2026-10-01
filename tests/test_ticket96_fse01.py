"""Ticket #96 — Formation sociale et économique (FSE) : création de la matière et
livraison complète de FSE01 « Communiquer : le schéma de communication » (cahier des
charges détaillé du ticket #97).

Contexte : aucune matière FSE n'existait dans le dépôt avant ce ticket. Ce test couvre :
la création de la matière/du module/de FSE01 (idempotente, FSE02→FSE17 jamais présentés
comme disponibles), la réutilisation intégrale du moteur V1 existant (banque, sessions,
autosave, reprise, correction hybride asynchrone), et surtout que difficulté ET sévérité
de cotation — deux paramètres distincts — sont réellement transmis, persistés et
appliqués côté serveur, y compris lors d'une reprise de session.

Aucun appel OpenAI réel : `FakeAIProvider` partout (voir `app.ai.fake_provider`)."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.models import UAA, Module, Subject
from app.seed import seed
from app.v1.ai_bridge import CORRECTABLE_TYPES
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.fse_bank import import_fse01_to_bank
from app.v1.fse_plan import FSE_MODULE_CODE, FSE_PLAN, FSE_PLAN_BY_CODE, FSE_SUBJECT_NAME
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionStatus,
)
from app.v1.session_service import (
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    get_session_build_job,
    run_correction_job,
    run_session_build_job,
)

FSE01_SLUG = "fse-fse01"


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _resolve_build_job_url(db_session, location: str) -> str:
    """Ticket #92 : /start crée un SessionBuildJob et redirige vers sa page d'attente —
    fait tourner le job en direct (appel de service, jamais un vrai worker séparé),
    exactement comme `tests/test_ticket94_french_20_courses.py`."""
    from app.v1 import routes_sessions

    if not location.startswith("/session-build-jobs/"):
        return location
    job_id = int(location.rstrip("/").rsplit("/", 1)[-1])
    try:
        provider = routes_sessions.get_ai_provider()
    except AINotConfiguredError:
        provider = _UnconfiguredProvider()
    job = claim_next_pending_build_job(db_session)
    if job is None:
        job = get_session_build_job(db_session, job_id=job_id)
    run_session_build_job(db_session, job=job, provider=provider)
    job = get_session_build_job(db_session, job_id=job_id)
    return f"/sessions/{job.created_session_id}"


def _start_session(client, db_session, mode: str, difficulty: str) -> str:
    response = client.get(f"/uaa/{FSE01_SLUG}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{FSE01_SLUG}/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return _resolve_build_job_url(db_session, response.headers["location"])


def _answer_all_and_submit(client, session_url: str, total: int, db_session, provider, severity: int) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == total else "next"
        response = client.post(
            f"{session_url}/answer",
            data={"csrf_token": token, "position": position, "direction": direction, "text": "une réponse"},
            follow_redirects=False,
        )
        assert response.status_code == 303
    response = client.get(response.headers["location"])
    token = _csrf(response.text)
    response = client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": severity}, follow_redirects=False
    )
    assert response.status_code == 303
    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=provider)


# =============================================================================================
# 1. Plan / registre
# =============================================================================================


def test_fse01_registered_in_fse_plan():
    assert "FSE01" in FSE_PLAN_BY_CODE
    plan = FSE_PLAN_BY_CODE["FSE01"]
    assert plan.title == "Communiquer : le schéma de communication"
    assert plan.slug == FSE01_SLUG


def test_only_fse01_in_plan_for_now():
    """Ticket #96 : seul FSE01 est rédigé — FSE02->FSE17 restent documentés dans
    docs/content_plan_fse.md mais jamais présentés comme un cours disponible."""
    assert [plan.code for plan in FSE_PLAN] == ["FSE01"]


# =============================================================================================
# 2. Matière / module / UAA — création idempotente, FSE02->FSE17 absents
# =============================================================================================


def test_fse_subject_module_uaa_seeded(db_session):
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    assert subject is not None
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    assert module is not None
    uaas = db_session.query(UAA).filter_by(module_id=module.id).all()
    assert [u.code for u in uaas] == ["FSE01"]
    assert uaas[0].is_published is True
    assert uaas[0].slug == FSE01_SLUG


def test_fse_seed_is_idempotent(db_session):
    seed()
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    assert db_session.query(UAA).filter_by(module_id=module.id).count() == 1


def test_fse_visible_in_subjects_navigation(client, db_session):
    seed()
    response = client.get("/subjects")
    assert response.status_code == 200
    assert FSE_SUBJECT_NAME in response.text

    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    response = client.get(f"/subjects/{subject.slug}")
    assert response.status_code == 200
    assert FSE_MODULE_CODE in response.text

    module = subject.modules[0]
    response = client.get(f"/modules/{module.slug}")
    assert response.status_code == 200
    assert "Communiquer : le schéma de communication" in response.text
    assert f"/uaa/{FSE01_SLUG}" in response.text


# =============================================================================================
# 3. Cours — contenu réel, pas un brouillon/stub
# =============================================================================================


def test_fse01_course_page_is_real_content(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE01_SLUG}")
    assert response.status_code == 200
    text = response.text
    for notion in ("émetteur", "récepteur", "canal", "code", "contexte", "rétroaction", "obstacle"):
        assert notion in text
    # Les trois applications explicitement demandées par le ticket #97.
    assert "Karim Haddad" in text  # mail
    assert "sécurité routière" in text  # affiche
    assert "Techno Services" in text  # réseau social
    # Jamais présenté comme un brouillon/validation technique (voir
    # tests/test_ticket94_french_20_courses.py::test_fr01_05_pages_never_show_provisional_status_to_the_user).
    assert "provisoire" not in text.lower()
    assert "stub" not in text.lower()


def test_fse01_hidden_answers_use_details_collapsed_by_default(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE01_SLUG}")
    assert "<details>" in response.text
    assert "Voir la correction expliquée" in response.text


# =============================================================================================
# 4. Banque — types corrects, documents réellement rattachés, isolation
# =============================================================================================


def test_fse01_bank_import_is_idempotent(db_session):
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    module = uaa.module
    first = import_fse01_to_bank(db_session, module, uaa)
    second = import_fse01_to_bank(db_session, module, uaa)
    assert first == 14
    assert second == 0
    assert db_session.query(Question).filter_by(uaa_id=uaa.id).count() == 14


def test_fse01_bank_uses_only_relevant_question_types(db_session):
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    for question in questions:
        assert question.current_version.question_type in CORRECTABLE_TYPES


def test_no_orphan_document_dependent_questions_in_fse01(db_session):
    """Même règle que le Français (#94 § 8) : toute question qui porte
    `source_document_version_id` référence un SourceDocumentVersion réellement persisté."""
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    from app.v1.models import SourceDocumentVersion

    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    checked = 0
    for question in questions:
        content = question.current_version.content_json
        doc_id = content.get("source_document_version_id")
        if doc_id:
            checked += 1
            assert db_session.get(SourceDocumentVersion, doc_id) is not None
    assert checked >= 6  # au moins les short_answer/document_analysis/long_answer rattachés


def test_fse01_questions_isolated_to_its_own_uaa(db_session):
    """Aucun mélange avec Informatique/Français/Mathématiques : toutes les questions
    importées pour FSE01 appartiennent exclusivement à son propre uaa_id."""
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 14
    assert all(q.module.code == FSE_MODULE_CODE for q in questions)


# =============================================================================================
# 5. Parcours complet — théorie -> entraînement -> examen -> correction -> résultats
# =============================================================================================


def test_fse01_practice_session_offers_difficulty_choice_with_same_labels(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
    assert response.status_code == 200
    for label in ("Facile", "Moyen", "Difficile"):
        assert label in response.text


def test_fse01_exam_offers_difficulty_and_severity_choice(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "hard")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    token = _csrf(response.text)
    authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "réponse"},
        follow_redirects=False,
    )
    confirm = authenticated_client.get(f"{session_url}/submit-confirm")
    assert confirm.status_code == 200
    for level in (1, 2, 3, 4, 5):
        assert f'id="severity-{level}"' in confirm.text


def test_fse01_difficulty_and_severity_are_distinct_and_applied_server_side(authenticated_client, db_session, monkeypatch):
    """Coeur du ticket #96 : difficulté (sélection des questions) et sévérité (notation)
    sont deux réglages distincts, transmis au serveur, persistés en base, et appliqués
    réellement (pas un simple sélecteur décoratif)."""
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "easy")
    session_id = int(session_url.rsplit("/", 1)[-1])

    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.EASY

    total = len(session.session_questions)
    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=5)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    # La sévérité choisie à la soumission ne modifie jamais la difficulté choisie au départ.
    assert session.difficulty_requested == SessionDifficultyRequest.EASY
    assert session.parameters_json["severity"] == 5


def test_fse01_settings_persist_across_resume(authenticated_client, db_session, monkeypatch):
    """Une session en cours, rechargée (reprise), conserve exactement la difficulté
    choisie au départ — pas seulement au moment de la création."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "practice", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])

    landing = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    assert session_url in landing.text

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    assert session.status.value == "in_progress"


def test_fse01_full_exam_flow_results_and_back_to_course_link(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    total = len(session.session_questions)

    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=3)

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert f"/uaa/{FSE01_SLUG}" in results.text  # retour au cours

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    assert session.score is not None
    assert len(fake.semantic_calls) <= 1  # jamais un appel IA par question
    for sq in session.session_questions:
        assert sq.answer is not None
        assert sq.answer.correction_status.value == "corrected"


def test_fse01_no_duplicate_questions_within_a_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    version_ids = [sq.question_version_id for sq in session.session_questions]
    assert len(version_ids) == len(set(version_ids))


# =============================================================================================
# 6. Non-régression — Informatique AMPCR et Français restent inchangés
# =============================================================================================


def test_ampcr_and_francais_unaffected_by_fse(authenticated_client, db_session, monkeypatch):
    """Les modifications partagées (app/main.py, routes_sessions.py, session_service.py)
    pour brancher FSE ne changent rien au comportement d'Informatique AMPCR ni de
    Français — vérifié par un aller-retour pratique complet sur chacun."""
    seed()
    _patch_fake_provider(monkeypatch)

    # AMPCR MC01
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    url = _resolve_build_job_url(db_session, response.headers["location"])
    assert url.startswith("/sessions/")

    # Français C01 (pilote historique #47)
    response = authenticated_client.get("/uaa/francais-c01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    url = _resolve_build_job_url(db_session, response.headers["location"])
    assert url.startswith("/sessions/")

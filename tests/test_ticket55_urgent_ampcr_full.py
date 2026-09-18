"""Ticket #55 — MVP urgent AMPCR complet (MC01→MC38) : parcours de session V1 de bout en
bout (banque #41, sessions #42, génération batch #43, correction globale #44, UX #24/#25).

Aucun appel OpenAI réel : toutes les générations/corrections passent par
`app.ai.fake_provider.FakeAIProvider`, monkeypatché sur `app.v1.routes_sessions.
get_ai_provider` (le seul point d'entrée que les routes utilisent réellement)."""

import re

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.ampcr_plan import AMPCR_PLAN
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import Question, QuestionnaireSession, SessionStatus


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, uaa_slug: str, mode: str = "practice", difficulty: str = "medium") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


def _answer_all_and_submit(client, session_url: str, total: int) -> None:
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
    response = client.post(f"{session_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303


# --- 1. Les 38 contextes présents, codes MC01→MC38 sans trou, titres présents -----------------


def test_ampcr_plan_has_38_entries_no_gaps():
    codes = [plan.code for plan in AMPCR_PLAN]
    assert codes == [f"MC{n:02d}" for n in range(1, 39)]
    assert all(plan.title for plan in AMPCR_PLAN)
    assert all(plan.category for plan in AMPCR_PLAN)


def test_all_38_uaas_are_seeded_and_published(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    codes = {uaa.code for uaa in ampcr.uaas}
    assert codes == {f"MC{n:02d}" for n in range(1, 39)}
    assert all(uaa.is_published for uaa in ampcr.uaas)


# --- 2. Auth requise ---------------------------------------------------------------------------


def test_anonymous_user_rejected_from_mc_practice(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc17/practice", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_anonymous_user_rejected_from_global_practice(client, db_session):
    seed()
    response = client.get("/modules/ampcr/practice", follow_redirects=False)
    assert response.status_code == 303


# --- 3. Cours public -----------------------------------------------------------------------


def test_course_page_still_public_for_any_ampcr_mc(client, db_session):
    seed()
    response = client.get("/uaa/ampcr-mc17")
    assert response.status_code == 200


# --- 4./5. Session practice/exam par MC, 10 questions -------------------------------------------


@pytest.mark.parametrize("uaa_slug", ["ampcr-mc01", "ampcr-mc17", "ampcr-mc38"])
def test_session_practice_created_with_ten_questions(authenticated_client, db_session, monkeypatch, uaa_slug):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, uaa_slug, mode="practice")

    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10
    assert len(session.session_questions) == 10
    assert session.status == SessionStatus.IN_PROGRESS
    # Jamais plus d'un appel de génération par création de session.
    assert len(fake.questionnaire_calls) <= 1


@pytest.mark.parametrize("uaa_slug", ["ampcr-mc01", "ampcr-mc25"])
def test_session_exam_created_with_ten_questions(authenticated_client, db_session, monkeypatch, uaa_slug):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, uaa_slug, mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.mode.value == "exam"
    assert session.question_count == 10


# --- 6. Génération bornée : un seul appel batch quand nécessaire ------------------------------


def test_generation_called_at_most_once_for_an_empty_bank_mc(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    _start_session(authenticated_client, "ampcr-mc22", mode="practice")
    assert len(fake.questionnaire_calls) == 1
    assert fake.questionnaire_calls[0].question_count <= 10


def test_generation_still_bounded_to_one_call_even_with_a_populated_bank(
    authenticated_client, db_session, monkeypatch
):
    """La banque MC01 a 12 questions (>= 10), mais sa répartition réelle (5 long_answer +
    2 diagnostic = 7 sémantiques, 5 seulement non-sémantiques) ne permet pas d'atteindre
    10 questions en respectant le plafond strict de 3 sémantiques (§ 14) : un complément
    non-sémantique est généré — mais toujours en UN SEUL appel, jamais un par question
    manquante ni un par question totale."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()

    fake = _patch_fake_provider(monkeypatch)
    _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    assert len(fake.questionnaire_calls) == 1
    request = fake.questionnaire_calls[0]
    assert request.question_count < 10
    from app.v1.session_service import LONG_SEMANTIC_TYPES

    assert not (set(request.allowed_types) & LONG_SEMANTIC_TYPES)


# --- 7. Fallback IA (génération indisponible) --------------------------------------------------


def test_session_still_created_from_partial_bank_when_generation_unavailable(
    authenticated_client, db_session
):
    """Avec OPENAI_API_KEY="" (garanti par tests/conftest.py) et sans fournisseur factice,
    `get_ai_provider()` lève `AINotConfiguredError` — si la banque contient déjà des
    questions (même moins de 10), la session se crée quand même avec ce qui est
    disponible plutôt que d'échouer (§ GÉNÉRATION du ticket #55)."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()

    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.IN_PROGRESS
    assert len(session.session_questions) >= 1


def test_session_creation_fails_gracefully_when_bank_empty_and_generation_unavailable(
    authenticated_client, db_session
):
    """Cas limite honnête (§ 6/§ BANQUE MVP) : un mini-cours sans aucune question en
    banque et sans fournisseur IA disponible ne peut produire aucune session — l'échec
    est explicite (503, message clair), jamais une erreur serveur brute ni un
    questionnaire inventé."""
    seed()
    response = authenticated_client.get("/uaa/ampcr-mc30/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc30/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 503
    assert db_session.query(QuestionnaireSession).count() == 0


# --- 8. Aucun feedback avant soumission / aucune fuite de solution ------------------------------


def test_no_correction_or_solution_visible_before_submission(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")

    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        text = response.text
        for leaked in (
            "correct_option_ids", "correct_categories", "correct_order", "correct_pairs",
            "correct_value", "correct_zone_ids", "correct_mapping", "accepted_answers", "rubric",
            "points_awarded", "Points forts", "Erreurs", "Éléments manquants",
        ):
            assert leaked not in text, f"fuite potentielle « {leaked} » à la question {position}"


# --- 9. Autosave ---------------------------------------------------------------------------


def test_autosave_persists_answer_without_correction(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    first_question = min(session.session_questions, key=lambda sq: sq.position)

    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "next", "text": "ma réponse autosauvée"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    saved_question = next(sq for sq in session.session_questions if sq.id == first_question.id)
    if saved_question.question_version.question_type in (
        "long_answer", "diagnostic", "short_answer", "vocabulary",
    ):
        assert saved_question.answer is not None
        assert saved_question.answer.answer_json.get("text") == "ma réponse autosauvée"
        assert saved_question.answer.correction_status.value == "pending"


def test_json_autosave_api_never_reveals_correctness(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    sq = min(session.session_questions, key=lambda s: s.position)

    response = authenticated_client.post(
        f"/api/v1/sessions/{session_id}/answers/{sq.id}",
        json={"answer_json": {"text": "reponse via api"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {"saved": True}
    assert "correct" not in body
    assert "score" not in body
    assert "solution" not in body


# --- 10. Reprise --------------------------------------------------------------------------


def test_resume_shows_existing_in_progress_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")

    landing = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    assert session_url in landing.text


def test_exam_in_progress_prevents_a_second_concurrent_exam(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    first_url = _start_session(authenticated_client, "ampcr-mc01", mode="exam")

    token = _csrf(authenticated_client.get("/uaa/ampcr-mc01/exam").text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/exam/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == first_url  # redirigé vers l'examen déjà en cours


# --- 11. Correction locale / IA batch unique / immutabilité -------------------------------------


def test_submit_runs_local_and_one_batch_semantic_call(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])

    _answer_all_and_submit(authenticated_client, session_url, 10)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    assert session.completed_at is not None
    assert session.score is not None
    assert len(fake.semantic_calls) <= 1  # jamais un appel par question

    for sq in session.session_questions:
        assert sq.answer is not None
        assert sq.answer.correction_status.value == "corrected"


def test_completed_session_is_immutable(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    _answer_all_and_submit(authenticated_client, session_url, 10)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.is_locked() is True

    # Une tentative d'autosave après complétion doit être refusée.
    sq = session.session_questions[0]
    response = authenticated_client.post(
        f"/api/v1/sessions/{session_id}/answers/{sq.id}", json={"answer_json": {"text": "trop tard"}}
    )
    assert response.status_code == 409


def test_results_page_shows_user_answer_and_feedback(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    _answer_all_and_submit(authenticated_client, session_url, 10)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "Score" in response.text
    assert "une réponse" in response.text or "Ta réponse" in response.text


# --- 12. Practice et exam restent distincts -----------------------------------------------------


def test_practice_and_exam_sessions_are_distinct_modes(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    practice_url = _start_session(authenticated_client, "ampcr-mc02", mode="practice")
    exam_url = _start_session(authenticated_client, "ampcr-mc02", mode="exam")
    assert practice_url != exam_url

    practice_id = int(practice_url.rsplit("/", 1)[-1])
    exam_id = int(exam_url.rsplit("/", 1)[-1])
    assert db_session.get(QuestionnaireSession, practice_id).mode.value == "practice"
    assert db_session.get(QuestionnaireSession, exam_id).mode.value == "exam"


# --- 13. Parcours global AMPCR + examen blanc global ---------------------------------------------


def test_global_ampcr_practice_session(authenticated_client, db_session, monkeypatch):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get("/modules/ampcr/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/modules/ampcr/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10


def test_global_ampcr_exam_has_twenty_questions(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/modules/ampcr/exam")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/modules/ampcr/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 20
    assert session.mode.value == "exam"


# --- 14. MC01-MC03 non régressés (contenu/données) ----------------------------------------------


def test_mc01_mc02_mc03_course_content_unaffected(client, db_session):
    seed()
    for slug, expected in [
        ("ampcr-mc01", "Architecture générale d'un PC"),
        ("ampcr-mc02", "Carte mère"),
        ("ampcr-mc03", "CPU"),
    ]:
        response = client.get(f"/uaa/{slug}")
        assert response.status_code == 200
        assert expected in response.text


def test_mc01_legacy_editorial_content_preserved_in_db(db_session):
    seed()
    from app.editorial_exercise import EditorialExerciseBlockConfig
    from app.models import BlockType
    from app.seed import MC01_BLOCKS

    editorial_blocks = [b for b in MC01_BLOCKS if b["type"] == BlockType.EDITORIAL_EXERCISE]
    assert len(editorial_blocks) == 12
    for block in editorial_blocks:
        config = EditorialExerciseBlockConfig.from_json(block["content"])
        assert len(config.items) == 1


# --- 15. Mobile HTML cohérent ------------------------------------------------------------------


def test_session_question_page_has_viewport_meta_and_no_correction_buttons(
    authenticated_client, db_session, monkeypatch
):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    assert 'name="viewport"' in response.text
    assert "Corriger" not in response.text
    assert "Vérifier ma réponse" not in response.text
    assert "Précédent" in response.text or "Suivant" in response.text


# --- Bootstrap : au moins un utilisateur, une question, ne créent pas de doublon --------------


def test_bank_import_is_idempotent(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    first = import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    second = import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    assert first == 12
    assert second == 0
    assert db_session.query(Question).filter_by(uaa_id=mc01.id).count() == 12

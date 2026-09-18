"""Ticket #47 — Français V1 : premier parcours complet (pilote technique provisoire).

Aucun contenu Français officiel ou brouillon ChatGPT n'existait dans le dépôt avant ce
ticket (voir `docs/content_plan_informatique_francais.md` § 3.3) — l'utilisateur a validé
explicitement la création d'une UAA pilote de VALIDATION TECHNIQUE (texte original,
jamais présenté comme un examen CESS officiel, voir `app.v1.francais_content`), pour
prouver que tout le parcours (SourceDocument partagé, practice/exam, autosave, reprise,
correction batch IA, résultats détaillés) fonctionne réellement.

Aucun appel OpenAI réel : toutes les corrections passent par `FakeAIProvider`."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.francais_content import MAIN_DOCUMENT_TITLE, SECOND_DOCUMENT_TITLE
from app.v1.models import QuestionnaireSession, SourceDocument, SourceDocumentVersion


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, mode: str = "practice", difficulty: str = "medium") -> str:
    response = client.get(f"/uaa/francais-c01/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/francais-c01/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


def _answer_payload_for(html: str) -> dict:
    if 'name="option_id"' in html:
        match = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', html)
        return {"option_id": match.group(1)}
    category_names = re.findall(r'name="(category__\d+)"', html)
    if category_names:
        data = {}
        for name in category_names:
            block = re.search(rf'name="{name}".*?</select>', html, re.DOTALL)
            values = re.findall(r'<option value="(\d+)"', block.group(0))
            data[name] = values[0]
        return data
    return {"text": "Réponse de test couvrant plusieurs phrases pour valider la correction."}


def _answer_all_and_submit(client, session_url: str, total: int) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == total else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303, response.text
    response = client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = client.post(f"{session_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303


# --- 1. SourceDocument partagé, banque hand-authored ----------------------------------------


def test_francais_bank_import_creates_shared_source_documents(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    imported = import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    assert imported == 11

    documents = db_session.query(SourceDocument).all()
    assert len(documents) == 2
    titles = {doc.current_version.title for doc in documents}
    assert titles == {MAIN_DOCUMENT_TITLE, SECOND_DOCUMENT_TITLE}


def test_francais_bank_import_is_idempotent(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    second = import_francais_c01_to_bank(db_session, francais, c01)
    assert second == 0
    assert db_session.query(SourceDocumentVersion).count() == 2


def test_multiple_questions_reference_the_same_document(db_session):
    """§ « DOCUMENT SOURCE » du ticket : un même texte doit pouvoir servir à plusieurs
    questions, jamais dupliqué."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()

    from app.v1.models import Question

    questions = db_session.query(Question).filter_by(uaa_id=c01.id).all()
    referencing_main_doc = [
        q for q in questions
        if q.current_version.content_json.get("source_document_version_id")
        or q.current_version.content_json.get("source_document_version_ids")
    ]
    # document_analysis x2 + source_comparison x1 référencent le document principal.
    assert len(referencing_main_doc) == 3
    # Aucun texte long dupliqué dans une question : seule une référence (id), jamais
    # `content_text`, n'apparaît dans le content_json d'une question.
    for question in referencing_main_doc:
        assert "content_text" not in question.current_version.content_json
        assert MAIN_DOCUMENT_TITLE not in str(question.current_version.content_json)


# --- 2. Course page publique, statut provisoire affiché --------------------------------------


def test_course_page_is_public_and_marked_provisional(client, db_session):
    seed()
    response = client.get("/uaa/francais-c01")
    assert response.status_code == 200
    assert "validation technique provisoire" in response.text
    assert "PAS un examen CESS officiel" in response.text


def test_practice_and_exam_require_authentication(client, db_session):
    seed()
    response = client.get("/uaa/francais-c01/practice", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


# --- 3. Practice : 10 questions, aucune correction avant submit, autosave --------------------


def test_practice_session_has_ten_questions_from_shared_bank(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10
    assert session.status.value == "in_progress"


def test_no_correction_or_solution_visible_before_submit(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    forbidden_fields = (
        "rubric", "expected_points", "correct_option_ids", "correct_categories",
        "accepted_answers", "explanation",
    )
    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        for field in forbidden_fields:
            assert field not in response.text, (position, field)
        assert "Corriger" not in response.text
        assert "Vérifier ma réponse" not in response.text


def test_autosave_persists_a_long_answer_across_requests(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")

    long_text = "Ceci est une réponse longue de validation. " * 60  # largement > 300 mots
    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        if 'name="text"' in response.text and 'rows="8"' in response.text:
            data = {"csrf_token": token, "position": position, "direction": "next", "text": long_text}
            authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
            break

    reloaded = authenticated_client.get(f"{session_url}?q={position}")
    assert long_text in reloaded.text, "la réponse longue autosauvegardée doit être intégralement relue, non tronquée"


def test_resume_offers_the_in_progress_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = session_url.rsplit("/", 1)[-1]

    landing = authenticated_client.get("/uaa/francais-c01/practice")
    assert "Reprendre" in landing.text
    assert f"/sessions/{session_id}" in landing.text


# --- 4. Exam : 10 questions minimum, immuable après soumission --------------------------------


def test_exam_session_has_at_least_ten_questions(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count >= 10
    assert session.mode.value == "exam"


def test_exam_prevents_duplicate_in_progress_sessions(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    first_url = _start_session(authenticated_client, mode="exam")
    response = authenticated_client.get("/uaa/francais-c01/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.headers["location"] == first_url


def test_exam_session_immutable_after_submission(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count)
    db_session.refresh(session)
    assert session.status.value == "completed"

    # Toute tentative de modification après soumission est sans effet (§ 55/56, réutilisé).
    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text) if "csrf_token" in response.text else None
    if token:
        authenticated_client.post(
            f"{session_url}/answer",
            data={"csrf_token": token, "position": 1, "direction": "next", "text": "modification tardive"},
            follow_redirects=False,
        )
    db_session.refresh(session)
    assert session.status.value == "completed"


# --- 5. Correction batch unique, résultat détaillé, réponse longue non tronquée ---------------


def test_submission_triggers_exactly_one_semantic_batch_call(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count)
    assert len(fake.semantic_calls) == 1


def test_document_context_is_provided_once_per_document_not_per_question(authenticated_client, db_session, monkeypatch):
    """§ CORRECTION du ticket : « le document partagé ne doit pas être dupliqué inutilement
    question par question dans le contexte envoyé à l'IA »."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    from app.v1.session_service import _document_contexts_for

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    contexts = _document_contexts_for(db_session, session_questions)
    # Au plus 2 documents existent dans ce pilote (principal + second) — jamais un
    # contexte par QUESTION qui les référence.
    assert len(contexts) <= 2
    for context in contexts:
        # Le texte n'apparaît qu'une fois dans le contexte de ce document.
        assert context.constraints.count(context.course_title) <= 1


def test_long_answer_is_not_truncated_end_to_end(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    long_text = "Argument développé sur plusieurs phrases pour tester la longueur. " * 80
    assert len(long_text) > 2000  # dépasse largement le max_length par défaut (2000)

    long_answer_position = None
    for sq in sorted(session.session_questions, key=lambda sq: sq.position):
        if sq.question_version.question_type == "long_answer":
            long_answer_position = sq.position
            break
    assert long_answer_position is not None

    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if position == long_answer_position:
            data["text"] = long_text
        else:
            data.update(_answer_payload_for(response.text))
        response = authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303

    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    authenticated_client.post(f"{session_url}/submit", data={"csrf_token": token}, follow_redirects=False)

    db_session.refresh(session)
    answer = next(
        sq.answer for sq in session.session_questions if sq.position == long_answer_position
    )
    assert answer.answer_json["text"] == long_text, "la réponse longue soumise ne doit jamais être tronquée"


def test_results_show_detailed_feedback_structure(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "Ta réponse" in response.text
    assert "point(s)" in response.text  # POINTS (en-tête accordéon)


def test_no_public_solution_leak_anywhere_in_results(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count)

    response = authenticated_client.get(session_url)
    for field in ("correct_option_ids", "correct_categories", "accepted_answers"):
        assert field not in response.text


# --- 6. Document reste lisible pendant la question (accordéon, mobile-first) ------------------


def test_source_document_panel_is_shown_for_document_referencing_questions(
    authenticated_client, db_session, monkeypatch
):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    doc_position = None
    for sq in sorted(session.session_questions, key=lambda sq: sq.position):
        if sq.question_version.question_type in ("document_analysis", "source_comparison"):
            doc_position = sq.position
            break
    assert doc_position is not None

    response = authenticated_client.get(f"{session_url}?q={doc_position}")
    assert response.status_code == 200
    assert "accordion" in response.text
    assert "inutile de revenir en arrière" in response.text


def test_mobile_viewport_meta_present(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert 'name="viewport"' in response.text


# --- 7. Non-régression AMPCR (le parcours Français ne casse rien d'existant) ------------------


def test_ampcr_mc01_practice_still_works(authenticated_client, db_session, monkeypatch):
    from app.v1.bank import import_mc01_legacy_to_bank

    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303

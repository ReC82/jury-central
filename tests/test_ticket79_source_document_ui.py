"""Ticket #77+#79 — Français : SourceDocument visible, accessible pendant la question ET
la correction.

Complète `tests/test_ticket77_hidden_source_document.py` (garde structurelle générique,
`_referenced_document_ids`, décision A pour long_answer) avec ce que #79 ajoute :

1. Audit systématique de la banque Français (§ 4) : toute question dont le prompt contient
   une formulation qui suppose un texte lisible (« D'après le texte », « Selon le
   texte », etc.) possède désormais un rattachement structuré — corrigé dans
   `francais_bank.py` (29 questions), jamais par une inférence runtime par regex.
2. `short_answer`/`vocabulary`/`classification` gagnent le même document optionnel que
   `long_answer` (#77) — `SourceDocumentRequirement.OPTIONAL` — car l'audit a révélé un
   vrai besoin répété (29 cas), pas un cas isolé (contrairement à `diagnostic`/
   `procedure`/`troubleshooting`, toujours à 0 cas, non généralisés).
3. `document_analysis` reste REQUIRED : une question sans document est invalide (rejetée
   à la validation), jamais servie.
4. `source_comparison` : les 2 documents sont étiquetés A/B dans l'ordre authored (jamais
   trié par id, voir `resolve_documents_in_order`), jamais mélangés.
5. Route `/documents/{version_id}` (lecture seule, § 7) : titre + texte complet
   uniquement, aucun feedback, aucune solution, utilisable en nouvel onglet
   (`target="_blank"`) depuis la question et les résultats.
6. `course_title`/`course_slug` exposés par ligne de résultat (§ 13) — donnée seulement,
   aucun bouton « Relire le cours » (scope #74).

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

import pytest
from markupsafe import escape

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
)
from app.v1.question_engine import (
    QUESTION_TYPE_REGISTRY,
    ContentValidationError,
    SourceDocumentRequirement,
    validate_content,
)

_TRIGGER_PHRASES = (
    "d'après le texte",
    "selon le texte",
    "en t'appuyant sur le texte",
    "identifie un passage",
    "compare le texte",
    "texte principal",
    "second texte",
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


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
    response = client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303


def _import_francais_bank(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    return c01


def _build_single_existing_question_session(db_session, question: Question, mode=SessionMode.PRACTICE) -> int:
    user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    assert user is not None, "authenticated_client doit avoir déjà créé ce compte"
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=question.module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(
            session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
        )
    )
    db_session.commit()
    return session.id


# =============================================================================================
# 1. Audit du contrat (§ 1) — SourceDocumentRequirement correspond au comportement réel
# =============================================================================================


def test_short_answer_vocabulary_classification_are_optional_not_required():
    """Décision § 2/4 du ticket : OPTIONAL pour les 3 types où l'audit a révélé un vrai
    besoin répété (29 cas dans la banque Français) — jamais REQUIRED (ça casserait les
    questions qui n'ont pas de document, largement majoritaires)."""
    for type_id in ("short_answer", "vocabulary", "classification"):
        assert QUESTION_TYPE_REGISTRY.get(type_id).source_document_requirement == (
            SourceDocumentRequirement.OPTIONAL
        )


def test_diagnostic_procedure_troubleshooting_still_none_not_generalised():
    """Aucun cas réel trouvé pour ces 3 types (Informatique, jamais utilisés avec un
    SourceDocument) — pas de généralisation injustifiée."""
    for type_id in ("diagnostic", "procedure", "troubleshooting"):
        assert QUESTION_TYPE_REGISTRY.get(type_id).source_document_requirement == SourceDocumentRequirement.NONE


def test_document_analysis_required_source_comparison_multiple_unchanged():
    assert QUESTION_TYPE_REGISTRY.get("document_analysis").source_document_requirement == (
        SourceDocumentRequirement.REQUIRED
    )
    assert QUESTION_TYPE_REGISTRY.get("source_comparison").source_document_requirement == (
        SourceDocumentRequirement.MULTIPLE
    )


# =============================================================================================
# 2. document_analysis sans document => rejet (§ 10)
# =============================================================================================


def test_document_analysis_without_document_is_rejected():
    with pytest.raises(ContentValidationError):
        validate_content("document_analysis", 1, {"prompt": "Analyse.", "rubric": "Grille."})


def test_document_analysis_with_invalid_document_id_is_rejected():
    with pytest.raises(ContentValidationError):
        validate_content(
            "document_analysis", 1, {"prompt": "Analyse.", "source_document_version_id": 0, "rubric": "Grille."}
        )


# =============================================================================================
# 3. Audit systématique de la banque (§ 4) : plus aucune question orpheline
# =============================================================================================


def test_no_francais_question_with_a_text_reference_phrase_lacks_a_source_document(db_session):
    """Pour CHACUNE des formulations listées au § 4 du ticket, toute question de la
    banque Français qui l'utilise doit avoir un rattachement structuré — sinon régression
    du bug exact que ce ticket corrige (29 cas trouvés et corrigés dans francais_bank.py).
    """
    c01 = _import_francais_bank(db_session)

    checked = 0
    for question in db_session.query(Question).filter_by(uaa_id=c01.id):
        content = question.current_version.content_json
        prompt = content.get("prompt", "").lower()
        has_phrase = any(phrase in prompt for phrase in _TRIGGER_PHRASES)
        if not has_phrase:
            continue
        checked += 1
        has_doc = bool(
            content.get("source_document_version_id") or content.get("source_document_version_ids")
        )
        assert has_doc, (question.id, question.current_version.question_type, content.get("prompt"))

    assert checked >= 15, "l'audit devrait couvrir un nombre substantiel de questions"


def test_at_least_29_francais_questions_have_a_structured_source_beyond_the_original_9(db_session):
    """9 questions référençaient déjà un document avant ce ticket (4 document_analysis +
    4 source_comparison + 1 long_answer id=170, voir #77). L'audit § 4 en a ajouté 29 —
    total 38/40 (2 questions d'opinion citent leur affirmation en entier dans le prompt,
    volontairement laissées sans document, voir francais_bank.py)."""
    c01 = _import_francais_bank(db_session)
    with_source = 0
    for question in db_session.query(Question).filter_by(uaa_id=c01.id):
        content = question.current_version.content_json
        if content.get("source_document_version_id") or content.get("source_document_version_ids"):
            with_source += 1
    assert with_source == 38


# =============================================================================================
# 4. source_comparison : A/B jamais mélangés (§ 9)
# =============================================================================================


def test_source_comparison_documents_labeled_a_and_b_in_authored_order(
    authenticated_client, db_session, monkeypatch
):
    from app.v1.francais_content import MAIN_DOCUMENT_TITLE, SECOND_DOCUMENT_TITLE

    c01 = _import_francais_bank(db_session)
    question = next(
        q for q in db_session.query(Question).filter_by(uaa_id=c01.id)
        if q.current_version.question_type == "source_comparison"
    )
    _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert "Document A : " + MAIN_DOCUMENT_TITLE in response.text
    assert "Document B : " + SECOND_DOCUMENT_TITLE in response.text
    # Étiquettes indépendantes : chaque document a son propre bouton "Voir le document"
    # et son propre lien nouvel onglet (jamais un seul bouton partagé).
    assert response.text.count("Voir le document") == 2
    assert response.text.count("Ouvrir dans un nouvel onglet") == 2


# =============================================================================================
# 5. Route /documents/{version_id} (§ 7)
# =============================================================================================


def test_document_view_route_shows_title_and_full_text_no_feedback_no_solution(
    authenticated_client, db_session
):
    from app.v1.francais_content import MAIN_DOCUMENT_TEXT, MAIN_DOCUMENT_TITLE
    from app.v1.models import SourceDocumentVersion

    _import_francais_bank(db_session)
    main_doc = db_session.query(SourceDocumentVersion).filter_by(title=MAIN_DOCUMENT_TITLE).first()
    assert main_doc is not None

    response = authenticated_client.get(f"/documents/{main_doc.id}")
    assert response.status_code == 200
    assert str(escape(MAIN_DOCUMENT_TITLE)) in response.text
    assert str(escape(MAIN_DOCUMENT_TEXT)) in response.text
    for leaked_field in ("correct_option_ids", "correct_categories", "accepted_answers", "points_awarded"):
        assert leaked_field not in response.text


def test_document_view_route_requires_authentication(client, db_session):
    from app.v1.francais_content import MAIN_DOCUMENT_TITLE
    from app.v1.models import SourceDocumentVersion

    _import_francais_bank(db_session)
    main_doc = db_session.query(SourceDocumentVersion).filter_by(title=MAIN_DOCUMENT_TITLE).first()
    response = client.get(f"/documents/{main_doc.id}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_document_view_route_404_for_unknown_id(authenticated_client, db_session):
    _import_francais_bank(db_session)
    response = authenticated_client.get("/documents/999999")
    assert response.status_code == 404


# =============================================================================================
# 6. Nouvel onglet (§ 7, § 8) : lien target="_blank" correct depuis la question ET les
# résultats
# =============================================================================================


def test_new_tab_link_present_and_correct_on_question_page(authenticated_client, db_session, monkeypatch):
    from app.v1.models import SourceDocumentVersion

    c01 = _import_francais_bank(db_session)
    question = next(
        q for q in db_session.query(Question).filter_by(uaa_id=c01.id)
        if q.current_version.question_type == "document_analysis"
    )
    doc_id = question.current_version.content_json["source_document_version_id"]
    assert db_session.get(SourceDocumentVersion, doc_id) is not None

    _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert f'href="/documents/{doc_id}"' in response.text
    assert 'target="_blank"' in response.text
    assert 'rel="noopener"' in response.text


def test_new_tab_link_present_on_results_page(authenticated_client, db_session, monkeypatch):
    c01 = _import_francais_bank(db_session)
    question = next(
        q for q in db_session.query(Question).filter_by(uaa_id=c01.id)
        if q.current_version.question_type == "document_analysis"
    )
    doc_id = question.current_version.content_json["source_document_version_id"]

    fake = _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)
    session_url = f"/sessions/{session_id}"

    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "Reponse de validation."},
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    assert len(fake.semantic_calls) == 1

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert f'href="/documents/{doc_id}"' in results.text
    assert 'target="_blank"' in results.text


# =============================================================================================
# 7. Scénario complet (§ 15) : texte visible avant réponse, puis encore accessible aux
# résultats
# =============================================================================================


def test_text_visible_before_answering_and_still_accessible_at_results(
    authenticated_client, db_session, monkeypatch
):
    """Simule exactement le scénario demandé § 15 : une question « D'après le texte » —
    le texte est visible AVANT que l'élève réponde, puis encore accessible au moment des
    résultats, sans avoir à deviner ou revenir en arrière."""
    from app.v1.francais_content import DIGITAL_LIFE_DOCUMENT_TEXT

    c01 = _import_francais_bank(db_session)
    question = next(
        q for q in db_session.query(Question).filter_by(uaa_id=c01.id)
        if "D'après le texte, cite deux démarches" in q.current_version.content_json.get("prompt", "")
    )
    fake = _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)
    session_url = f"/sessions/{session_id}"

    escaped_text = str(escape(DIGITAL_LIFE_DOCUMENT_TEXT))

    # Avant réponse : le texte complet est déjà là.
    before = authenticated_client.get(f"{session_url}?q=1")
    assert before.status_code == 200
    assert escaped_text in before.text

    token = _csrf(before.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={
            "csrf_token": token, "position": 1, "direction": "submit",
            "text": "Les demarches administratives et la gestion bancaire.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    assert len(fake.semantic_calls) == 1

    # Aux résultats : le même texte complet reste accessible (panneau intégré).
    after = authenticated_client.get(session_url)
    assert after.status_code == 200
    assert escaped_text in after.text


# =============================================================================================
# 8. Rattachement au cours (§ 13) : données exposées, réutilisées depuis par #74
# =============================================================================================


def test_course_mapping_data_exposed_in_results_rows(authenticated_client, db_session, monkeypatch):
    """§ 79.13 : `_build_results_rows` expose `course_title`/`course_slug` par question —
    à l'origine « sans bouton construit ici » (le bouton « Relire le cours » était hors
    scope de #79) ; #74 (mergé depuis) construit effectivement ce bouton à partir de ces
    mêmes données, donc ce test ne peut plus supposer son absence dans le HTML des
    résultats — seule l'exposition correcte de la donnée reste vérifiée ici, la présence
    du bouton lui-même étant du ressort des tests dédiés de #74
    (`tests/test_ticket74_course_recommendations.py`)."""
    c01 = _import_francais_bank(db_session)
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get("/uaa/francais-c01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    from app.v1.routes_sessions import _build_results_rows

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    rows = _build_results_rows(db_session, session_questions)
    # Ticket #82 : 9 ou 10 selon le tirage (garde anti-doublon intra-session finale) —
    # comparé à question_count réel, jamais une valeur codée en dur.
    assert len(rows) == session.question_count
    assert 9 <= len(rows) <= 10
    for row in rows:
        assert row["course_title"] == c01.title
        assert row["course_slug"] == c01.slug

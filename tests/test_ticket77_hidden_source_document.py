"""Ticket #77 — BUG Français : long_answer avec SourceDocument invisible à l'élève.

Contexte (découvert en validation staging du 2026-09-19, voir
docs/claude-reports/2026-09-19_francais-overnight-functional.md et
docs/claude-reports/2026-09-19_ticket-77_hidden-source-document.md) : la question
`long_answer` id=170 (« faut-il enseigner les bases de la programmation... ») référençait
un document dans son `content_json` (`source_document_version_id`), mais
`LongAnswerContent` (app/v1/question_types.py) ne déclarait pas ce champ. Conséquence :
Pydantic le supprimait silencieusement du payload public envoyé au navigateur — l'élève ne
voyait jamais le document — alors que `_document_contexts_for` (contexte de correction IA)
lisait alors `content_json` BRUT directement, et le recevait quand même. L'élève était donc
corrigé sur un document qu'il n'avait jamais pu lire — interdit pédagogiquement.

Fix (voir app/v1/question_types.py, app/v1/session_service.py, app/v1/routes_sessions.py) :

1. Décision A (pas B) : `LongAnswerContent` supporte désormais un
   `source_document_version_id` OPTIONNEL (`SourceDocumentRequirement.OPTIONAL`, valeur
   du contrat #40 déjà définie mais jamais utilisée jusqu'ici) — jamais REQUIRED comme
   `document_analysis`. La question 170 n'a PAS été retypée : son `rubric` traite
   explicitement la référence au document comme facultative pour le barème (« référence
   possible (mais pas obligatoire) aux arguments du texte »), ce qui est la sémantique de
   `long_answer` (expression personnelle), pas celle de `document_analysis` (analyse
   OBLIGATOIRE d'un document précis).
2. Garde structurelle générique (§ 4 du ticket, pas un fix ad hoc sur l'id 170) :
   `build_question_display` (ce que voit l'élève) et `_document_contexts_for` (contexte
   envoyé à l'IA) dérivent désormais TOUS LES DEUX les identifiants de document du MÊME
   payload public, via `session_service._referenced_document_ids` — jamais du
   `content_json` brut. Un document qu'un type ne déclare pas dans son modèle Pydantic ne
   peut structurellement plus atteindre l'IA sans être aussi montré à l'élève, quel que
   soit le type, présent ou futur — plus une question de discipline au cas par cas.
3. Résultats/export/impression (§ 6 du ticket) : `_build_results_rows`
   (app/v1/routes_sessions.py) expose désormais une référence courte
   (`source_documents`, titres uniquement, jamais le texte complet redupliqué) pour toute
   question qui en référence, affichée sur l'écran de résultats et dans l'export
   Markdown.

Audit du contrat (§ 2 du ticket) : recherche en base de toute question, tous types et
toutes UAA confondus, ayant un `source_document_version_id(s)` dans son `content_json`
brut mais non exposé par `public_payload` — un seul cas trouvé (id=170, long_answer,
Français), désormais corrigé. `diagnostic`/`procedure`/`troubleshooting` n'ont aucun cas
similaire actuellement (vérifié par le test générique ci-dessous, qui couvrirait
n'importe quel type futur).

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from markupsafe import escape

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.francais_content import CODING_DEBATE_DOCUMENT_TITLE
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
)
from app.v1.question_engine import QUESTION_TYPE_REGISTRY, SourceDocumentRequirement, public_payload
from app.v1.question_types import LongAnswerContent
from app.v1.session_service import _document_contexts_for, build_question_display


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _build_single_existing_question_session(db_session, question: Question, mode=SessionMode.PRACTICE) -> int:
    """Session à une seule question référençant une question RÉELLE déjà en base
    (jamais une question synthétique) — déterministe."""
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


def _import_francais_bank(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    return c01


def _find_question_170_equivalent(db_session, c01) -> Question:
    for question in db_session.query(Question).filter_by(uaa_id=c01.id):
        content = question.current_version.content_json
        if question.current_version.question_type == "long_answer" and "faut-il enseigner les bases " \
                "de la programmation" in content.get("prompt", ""):
            return question
    raise AssertionError("la question long_answer id=170 (programmation) est introuvable dans la banque")


# =============================================================================================
# 1. Audit du contrat (§ 2 du ticket) — SourceDocumentRequirement
# =============================================================================================


def test_long_answer_source_document_requirement_is_optional_not_required():
    """Décision A du ticket : OPTIONAL (facultatif), jamais REQUIRED comme
    document_analysis — long_answer sans document reste parfaitement valide."""
    spec = QUESTION_TYPE_REGISTRY.get("long_answer")
    assert spec.source_document_requirement == SourceDocumentRequirement.OPTIONAL


def test_document_analysis_and_source_comparison_requirements_unchanged():
    assert QUESTION_TYPE_REGISTRY.get("document_analysis").source_document_requirement == (
        SourceDocumentRequirement.REQUIRED
    )
    assert QUESTION_TYPE_REGISTRY.get("source_comparison").source_document_requirement == (
        SourceDocumentRequirement.MULTIPLE
    )


def test_diagnostic_procedure_troubleshooting_remain_none_no_generalisation():
    """Ticket #77 § 3 : « ne généralise pas long_answer inutilement » — seul long_answer a
    un vrai cas d'usage constaté (id=170). Les 3 autres types restent NONE tant qu'aucun
    contenu réel n'en a besoin."""
    for type_id in ("diagnostic", "procedure", "troubleshooting"):
        assert QUESTION_TYPE_REGISTRY.get(type_id).source_document_requirement == SourceDocumentRequirement.NONE


# =============================================================================================
# 2. long_answer sans document => inchangé
# =============================================================================================


def test_long_answer_without_document_defaults_to_none():
    content = LongAnswerContent(prompt="Ecris un texte.", rubric="Grille de correction.")
    assert content.source_document_version_id is None


def test_long_answer_without_document_public_payload_unchanged():
    payload = public_payload("long_answer", 1, {"prompt": "Ecris.", "rubric": "Grille."})
    assert "source_document_version_id" not in payload
    assert payload["prompt"] == "Ecris."
    assert payload["max_length"] == 20000


# =============================================================================================
# 3. long_answer AVEC document => visible ; document_analysis/source_comparison inchangés
# =============================================================================================


def test_long_answer_with_document_is_visible_in_public_payload():
    payload = public_payload(
        "long_answer", 1, {"prompt": "Ecris.", "rubric": "Grille.", "source_document_version_id": 7}
    )
    assert payload["source_document_version_id"] == 7


def test_document_analysis_with_document_still_visible():
    payload = public_payload(
        "document_analysis",
        1,
        {"prompt": "Analyse.", "source_document_version_id": 3, "rubric": "Grille."},
    )
    assert payload["source_document_version_id"] == 3


def test_source_comparison_documents_still_visible():
    payload = public_payload(
        "source_comparison",
        1,
        {"prompt": "Compare.", "source_document_version_ids": [1, 2], "rubric": "Grille."},
    )
    assert payload["source_document_version_ids"] == [1, 2]


# =============================================================================================
# 4. Aucune source silencieusement supprimée (garde générique, § 4 du ticket)
# =============================================================================================


def test_no_hidden_source_document_anywhere_in_francais_bank(db_session):
    """Pour TOUTE question de la banque Français, si son content_json BRUT référence un
    document, le PAYLOAD PUBLIC doit exposer exactement la même référence — sinon c'est
    une source cachée (le bug exact de ce ticket). Aurait échoué avant le fix (id=170)."""
    c01 = _import_francais_bank(db_session)

    checked_with_document = 0
    for question in db_session.query(Question).filter_by(uaa_id=c01.id):
        version = question.current_version
        content = version.content_json
        raw_single = content.get("source_document_version_id")
        raw_multi = content.get("source_document_version_ids")
        if not raw_single and not raw_multi:
            continue
        checked_with_document += 1
        payload = public_payload(version.question_type, version.schema_version, content)
        if raw_single:
            assert payload.get("source_document_version_id") == raw_single, (question.id, version.question_type)
        if raw_multi:
            assert payload.get("source_document_version_ids") == raw_multi, (question.id, version.question_type)

    # Au moins document_analysis (4) + source_comparison (4) + long_answer id=170 (1).
    assert checked_with_document >= 9


def test_ai_correction_context_never_exceeds_what_student_sees(authenticated_client, db_session, monkeypatch):
    """Pour une session réelle mélangeant tous les types, l'ensemble des documents envoyés
    à l'IA (`_document_contexts_for`) doit être EXACTEMENT celui que l'élève a pu voir
    (`build_question_display`, question par question) — jamais un sur-ensemble caché."""
    c01 = _import_francais_bank(db_session)
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get("/uaa/francais-c01/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    session_questions = list(session.session_questions)

    student_doc_ids: set[int] = set()
    for sq in session_questions:
        display = build_question_display(db_session, sq)
        student_doc_ids.update(document.id for document in display.source_documents)

    ai_contexts = _document_contexts_for(db_session, session_questions)
    ai_doc_ids = {int(context.course_key.removeprefix("source-document-")) for context in ai_contexts}

    assert ai_doc_ids == student_doc_ids
    assert len(ai_doc_ids) >= 1, (c01.id, [sq.question_version.question_type for sq in session_questions])


# =============================================================================================
# 5. Question 170 : corrigée (décision A), plus jamais une source cachée, bout en bout
# =============================================================================================


def test_question_170_document_visible_end_to_end_practice_and_exam(
    authenticated_client, db_session, monkeypatch
):
    c01 = _import_francais_bank(db_session)
    question = _find_question_170_equivalent(db_session, c01)
    # Décision A du ticket, pas B : le rubric de la question traite explicitement la
    # référence au document comme facultative pour le barème — ce n'est pas une tâche
    # d'analyse de document obligatoire, donc la question reste long_answer, pas
    # retypée en document_analysis.
    assert question.current_version.question_type == "long_answer"

    fake = _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)
    session_url = f"/sessions/{session_id}"

    escaped_title = str(escape(CODING_DEBATE_DOCUMENT_TITLE))  # Jinja échappe l'apostrophe (&#39;)

    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    assert "source-document-panel" in response.text
    assert "Document de référence" in response.text
    assert "Voir le document" in response.text
    assert "/documents/" in response.text
    assert escaped_title in response.text
    assert "answer-textarea" in response.text

    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={
            "csrf_token": token, "position": 1, "direction": "submit",
            "text": "Reponse argumentee de validation qui se refere au texte source fourni.",
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
    assert len(fake.semantic_calls) == 1  # un seul appel batch (§ ticket #55/#62), inchangé

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert "Ta réponse" in results.text
    assert "Document(s) de référence :" in results.text
    assert f"Document de référence : {escaped_title}" in results.text
    assert "Voir le document" in results.text
    assert "/documents/" in results.text
    assert "window.print()" in results.text
    assert "@media print" in results.text

    export = authenticated_client.get(f"{session_url}/export.md")
    assert export.status_code == 200
    assert "## Question 1" in export.text
    assert "Document(s) de référence :" in export.text
    assert f"- Document de référence : {CODING_DEBATE_DOCUMENT_TITLE}" in export.text
    # Référence courte, jamais le texte complet du document redupliqué dans l'export.
    assert export.text.count(CODING_DEBATE_DOCUMENT_TITLE) == 1


# =============================================================================================
# 6. Non-régression : practice/exam Français, correction batch, export, print
# =============================================================================================


def test_francais_practice_still_composes_normally(authenticated_client, db_session, monkeypatch):
    _import_francais_bank(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/francais-c01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    # Ticket #82 : 9 ou 10 selon le tirage (garde anti-doublon intra-session finale) —
    # voir tests/test_ticket47_francais_v1.py::test_exam_session_has_twenty_questions.
    assert 9 <= session.question_count <= 10


def test_francais_exam_still_composes_normally(authenticated_client, db_session, monkeypatch):
    _import_francais_bank(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/francais-c01/exam")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    # Ticket #82 : 19 ou 20 selon le tirage (garde anti-doublon intra-session finale).
    assert 19 <= session.question_count <= 20


def test_results_and_export_unaffected_for_questions_without_any_document(
    authenticated_client, db_session, monkeypatch
):
    """Non-régression explicite : une question sans document ne doit montrer AUCUNE ligne
    « Document(s) de référence » — ni sur les résultats, ni dans l'export."""
    c01 = _import_francais_bank(db_session)
    question = None
    for candidate in db_session.query(Question).filter_by(uaa_id=c01.id):
        content = candidate.current_version.content_json
        has_doc = content.get("source_document_version_id") or content.get("source_document_version_ids")
        if candidate.current_version.question_type == "short_answer" and not has_doc:
            question = candidate
            break
    assert question is not None, "aucune question short_answer sans document trouvée (voir francais_bank.py)"

    _patch_fake_provider(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)
    session_url = f"/sessions/{session_id}"

    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "Reponse courte de test."},
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303

    results = authenticated_client.get(session_url)
    assert "Document(s) de référence" not in results.text

    export = authenticated_client.get(f"{session_url}/export.md")
    assert "Document(s) de référence" not in export.text

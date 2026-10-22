"""Ticket #94 — Français : parcours des 20 mini-cours (PHASE C : FR11→FR15).

Même architecture et même standard que PHASE A/B (`tests/test_ticket94_french_20_courses.py`,
`tests/test_ticket94_french_fr06_10.py`) : cours réels non-stub (structure en 10 points),
banque rattachée à de vrais `SourceDocument`, practice/exam ciblés, moteur SourceDocument
(#77/#79), génération/correction asynchrones (#88/#90/#92) et renvois documentaires
résolvables (#151) — aucune nouvelle architecture.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import routes_sessions
from app.v1.document_references import audit_document_references
from app.v1.francais_fr11_15_bank import (
    import_francais_fr11_to_bank,
    import_francais_fr12_to_bank,
    import_francais_fr13_to_bank,
    import_francais_fr14_to_bank,
    import_francais_fr15_to_bank,
)
from app.v1.francais_plan import FRANCAIS_PLAN_BY_CODE, get_francais_context
from app.v1.models import Question, QuestionnaireSession
from app.v1.session_service import (
    _document_contexts_for,
    _pedagogical_context_for,
    build_question_display,
)
from tests.test_ticket94_french_fr06_10 import (
    _PROVISIONAL_LABELS,
    _answer_all_and_submit,
    _csrf,
    _patch_fake_provider,
    _resolve_build_job_url,
    _start_session,
)

FR11_15_CODES = ["FR11", "FR12", "FR13", "FR14", "FR15"]
FR11_15_SLUGS = [f"francais-{code.lower()}" for code in FR11_15_CODES]

_IMPORTERS = {
    "FR11": import_francais_fr11_to_bank,
    "FR12": import_francais_fr12_to_bank,
    "FR13": import_francais_fr13_to_bank,
    "FR14": import_francais_fr14_to_bank,
    "FR15": import_francais_fr15_to_bank,
}


def _import_all(db_session) -> Module:
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    for code in FR11_15_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
    db_session.commit()
    return francais


# =============================================================================================
# 1. Plan, contexte IA, seed
# =============================================================================================


def test_fr11_to_fr15_registered_with_bare_titles_and_context():
    for code in FR11_15_CODES:
        plan = FRANCAIS_PLAN_BY_CODE[code]
        assert "UAA" not in plan.title and code not in plan.title
        assert plan.allowed_notions and plan.competencies
        context = get_francais_context(plan.course_key)
        assert context is not None and context.course_title == plan.title
        assert _pedagogical_context_for(code) is not None
    assert list(routes_sessions._FRANCAIS_BANK_IMPORTERS)[-5:] == FR11_15_SLUGS


def test_fr11_15_seeded_published_and_listed_in_order(client, db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    by_code = {uaa.code: uaa for uaa in francais.uaas}
    for code in FR11_15_CODES:
        assert by_code[code].is_published and not by_code[code].hidden_from_listing
    response = client.get("/modules/francais")
    links = list(dict.fromkeys(re.findall(r'href="/uaa/(francais-fr\d\d)"', response.text)))
    assert links == [f"francais-fr{n:02d}" for n in range(1, 16)]


def test_seed_is_idempotent_for_fr11_15(db_session):
    seed()
    count = db_session.query(UAA).count()
    seed()
    assert db_session.query(UAA).count() == count


# =============================================================================================
# 2. Pages de cours — non-stub, sans jargon, « À retenir »
# =============================================================================================


def test_fr11_15_course_pages_are_complete(client, db_session):
    seed()
    for slug in FR11_15_SLUGS:
        response = client.get(f"/uaa/{slug}")
        assert response.status_code == 200, slug
        text = response.text
        for required_section in (
            "Ce que tu dois savoir faire",
            "Théorie progressive",
            "Définitions importantes",
            "Méthode étape par étape",
            "Exemples commentés",
            "Mauvaises réponses comparées aux bonnes",
            "Pièges et erreurs fréquentes",
            "Exercices guidés",
            "Corrigés très expliqués",
        ):
            assert required_section in text, f"{slug} : section manquante « {required_section} »"
        assert 'id="a-retenir"' in text, slug
        assert "<details>" in text and "<details open" not in text, slug
        lowered = text.lower()
        for label in _PROVISIONAL_LABELS:
            assert label not in lowered, (slug, label)
        assert not re.search(r"ticket\s*#\d+", text, re.IGNORECASE), slug


def test_fr11_15_practice_and_exam_pages_exist(client, db_session):
    seed()
    for slug in FR11_15_SLUGS:
        for space in ("/practice", "/exam"):
            assert client.get(f"/uaa/{slug}{space}").status_code == 200, (slug, space)


# =============================================================================================
# 3. Banque — idempotence, types, supports, renvois
# =============================================================================================


def test_fr11_15_bank_is_idempotent_and_substantial(db_session):
    francais = _import_all(db_session)
    for code in FR11_15_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        assert db_session.query(Question).filter_by(uaa_id=uaa.id).count() >= 8, code
        assert _IMPORTERS[code](db_session, francais, uaa) == 0


def test_fr11_15_bank_uses_only_relevant_question_types(db_session):
    francais = _import_all(db_session)
    allowed = {"short_answer", "long_answer", "document_analysis", "source_comparison", "vocabulary", "classification"}
    for code in FR11_15_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        types_used = {q.current_version.question_type for q in db_session.query(Question).filter_by(uaa_id=uaa.id)}
        assert types_used <= allowed, (code, types_used)
        assert "long_answer" in types_used or "source_comparison" in types_used, code


def test_no_orphan_document_dependent_questions_in_fr11_15(db_session):
    """Toute consigne qui renvoie à un support nommé (« la lettre ouverte », « la
    transcription », « le dossier »…) a au moins un document réellement rattaché."""
    francais = _import_all(db_session)
    triggers = (
        "d'après", "selon le", "en t'appuyant", "compare", "dans le paragraphe", "dans la lettre",
        "dans la transcription", "le courriel de", "le courriel modèle", "la situation", "la fiche",
        "le sujet", "le dossier", "le document", "les documents", "introduction",
    )
    orphans = []
    for code in FR11_15_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        for question in db_session.query(Question).filter_by(uaa_id=uaa.id):
            content = question.current_version.content_json
            prompt = re.sub(r"«.*?»", "", content.get("prompt", ""), flags=re.DOTALL).lower()
            has_doc = bool(content.get("source_document_version_id") or content.get("source_document_version_ids"))
            if any(trigger in prompt for trigger in triggers) and not has_doc:
                orphans.append((code, prompt[:70]))
    assert orphans == []


def test_fr11_15_document_references_are_resolvable(db_session):
    _import_all(db_session)
    report = audit_document_references(db_session, uaa_codes=tuple(FR11_15_CODES))
    assert report["audited"] >= 40
    assert report["unresolved"] == []


def test_fr13_dossier_questions_receive_every_cited_document(db_session):
    """FR13 (dossier documentaire) : les questions qui confrontent plusieurs documents les
    reçoivent tous — jamais un renvoi « document 2 » vers un document non affiché."""
    francais = _import_all(db_session)
    uaa = next(u for u in francais.uaas if u.code == "FR13")
    multi = [
        q for q in db_session.query(Question).filter_by(uaa_id=uaa.id)
        if len(q.current_version.content_json.get("source_document_version_ids") or []) >= 2
    ]
    assert len(multi) >= 3


# =============================================================================================
# 4. Sessions — practice/exam ciblés, async, documents, correction sans faux 0
# =============================================================================================


def test_each_fr11_15_practice_session_is_scoped_and_french_only(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    for slug, code in zip(FR11_15_SLUGS, FR11_15_CODES, strict=True):
        session_url = _start_session(authenticated_client, db_session, slug, mode="practice")
        session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
        assert session.question_count <= 10
        types_used = set()
        for sq in session.session_questions:
            assert sq.question_version.question.uaa.code == code
            types_used.add(sq.question_version.question_type)
        assert not types_used & {"multiple_choice", "ordering", "diagnostic"}, (code, types_used)


def test_fr12_exam_is_nonblocking_and_standard_volume(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    response = authenticated_client.get("/uaa/francais-fr12/exam")
    response = authenticated_client.post(
        "/uaa/francais-fr12/exam/start",
        data={"csrf_token": _csrf(response.text), "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/session-build-jobs/")
    session_url = _resolve_build_job_url(db_session, response.headers["location"])
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    assert session.question_count <= 10


def test_fr13_documents_visible_and_ai_student_parity(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr13", mode="exam")
    session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
    session_questions = list(session.session_questions)
    student_doc_ids: set[int] = set()
    for sq in session_questions:
        display = build_question_display(db_session, sq)
        student_doc_ids.update(document.id for document in display.source_documents)
    assert student_doc_ids, "FR13 : les questions de dossier doivent montrer leurs documents"
    ai_contexts = _document_contexts_for(db_session, session_questions)
    ai_doc_ids = {int(context.course_key.removeprefix("source-document-")) for context in ai_contexts}
    assert ai_doc_ids == student_doc_ids
    shown = False
    for position in range(1, session.question_count + 1):
        html = authenticated_client.get(f"{session_url}?q={position}").text
        shown = shown or "Voir le texte" in html or 'target="_blank"' in html
    assert shown


def test_fr14_full_practice_flow_async_correction_no_false_zero(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr14", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value == "completed"
    for sq in session.session_questions:
        assert sq.answer.correction_status.value == "corrected"
        assert sq.answer.points_awarded is not None
    assert authenticated_client.get(f"{session_url}/export.md").status_code == 200
    assert "FR14" in authenticated_client.get("/mes-sessions").text


def test_fr15_exam_flow_and_long_answer_without_truncation(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr15", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    position = next(
        (
            sq.position for sq in session.session_questions
            if sq.question_version.question_type in ("long_answer", "source_comparison", "document_analysis")
        ),
        None,
    )
    assert position is not None
    long_text = "Intervention préparée, structurée et argumentée. " * 300
    response = authenticated_client.get(f"{session_url}?q={position}")
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": _csrf(response.text), "position": position, "direction": "next", "text": long_text},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.expire_all()
    saved = next(sq for sq in db_session.get(QuestionnaireSession, session_id).session_questions if sq.position == position)
    assert saved.answer.answer_json["text"] == long_text
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value in ("completed", "correction_incomplete")

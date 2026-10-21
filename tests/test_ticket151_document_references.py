"""Ticket #151 — références documentaires résolvables.

Garanties vérifiées :
- toute question FSE active de la banque fraîchement importée a des renvois résolvables
  (« document 3 » affiché sous ce numéro, « la note de direction » et « le forum » affichés
  ensemble, « les trois documents » réellement fournis) ;
- la réparation d'une banque déjà importée crée une NOUVELLE version (idempotente) et ne
  touche jamais une version déjà servie dans une session ;
- élève, correcteur, résultats et export voient les mêmes documents, sous le même libellé.
"""

import re

import pytest

from app.models import UAA
from app.seed import seed
from app.v1 import fse_bank
from app.v1.document_references import (
    audit_document_references,
    dossier_repairs,
    repair_dossier_references,
)
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocumentVersion,
    User,
    add_question_version,
)
from app.v1.question_engine import validate_content
from app.v1.routes_sessions import _FSE_BANK_IMPORTERS
from app.v1.session_service import _document_contexts_for

FSE_CODES = tuple(f"FSE{n:02d}" for n in range(1, 17))


def _import_fse_banks(db_session) -> None:
    seed()
    for slug, importer in _FSE_BANK_IMPORTERS.items():
        uaa = db_session.query(UAA).filter_by(slug=slug).first()
        importer(db_session, uaa.module, uaa)
    db_session.commit()


def _question(db_session, code: str, prompt_start: str) -> Question:
    uaa = db_session.query(UAA).filter_by(code=code).first()
    for question in db_session.query(Question).filter_by(uaa_id=uaa.id):
        if question.current_version.content_json.get("prompt", "").startswith(prompt_start):
            return question
    raise AssertionError(prompt_start)


def _shown_titles(db_session, content: dict) -> list[str]:
    ids = content.get("source_document_version_ids") or (
        [content["source_document_version_id"]] if content.get("source_document_version_id") else []
    )
    return [db_session.get(SourceDocumentVersion, doc_id).title for doc_id in ids]


def _session(db_session, question_version_id: int, module_id: int, mode=SessionMode.EXAM) -> QuestionnaireSession:
    user = (
        db_session.query(User).filter_by(email="eleve-test@example.test").first()
        or db_session.query(User).filter_by(email="eleve-151@example.test").first()
    )
    if user is None:
        user = User(email="eleve-151@example.test", password_hash="x", display_name="t")
        db_session.add(user)
        db_session.flush()
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(SessionQuestion(
        session_id=session.id, question_version_id=question_version_id, position=1, points_max=1.0,
    ))
    db_session.commit()
    return session


def test_fresh_fse_bank_has_no_unresolved_document_reference(db_session):
    _import_fse_banks(db_session)
    report = audit_document_references(db_session, uaa_codes=FSE_CODES)
    assert report["audited"] > 200
    assert report["with_reference"] >= 15
    assert report["unresolved"] == []


def test_every_repair_is_exactly_what_the_fresh_bank_creates(db_session):
    _import_fse_banks(db_session)
    for repair in dossier_repairs():
        question = _question(db_session, repair.uaa_code, repair.new_prompt)
        content = question.current_version.content_json
        assert content["prompt"] == repair.new_prompt
        assert _shown_titles(db_session, content) == (
            list(repair.document_titles) if repair.document_titles else []
        ), repair.new_prompt
    # Rien à réparer sur une banque déjà correcte.
    assert repair_dossier_references(db_session) == {"repaired": 0, "unresolved": 0}


def test_capture_cases_show_document_3_and_both_forum_and_note(db_session):
    _import_fse_banks(db_session)
    limit = _question(db_session, "FSE16", "D'après le document 3")
    assert "(réactions des groupes concernés)" in limit.current_version.content_json["prompt"]
    # Ticket #152 : la proposition (document 1) accompagne le document 3 (« Cette aide… »).
    assert _shown_titles(db_session, limit.current_version.content_json) == [
        fse_bank.FSE16_PROPOSAL_TITLE, fse_bank.FSE16_REACTIONS_TITLE,
    ]
    fact = _question(db_session, "FSE07", "Le forum affirme que Lucas")
    assert _shown_titles(db_session, fact.current_version.content_json) == [
        fse_bank.FSE07_SCHOOL_TITLE, fse_bank.FSE07_FORUM_TITLE,
    ]


def test_repair_adds_a_new_version_and_never_touches_a_served_one(db_session):
    _import_fse_banks(db_session)
    question = _question(db_session, "FSE07", "Le forum affirme que Lucas")
    content = dict(question.current_version.content_json)
    forum_id = content["source_document_version_id"]
    # État d'une banque importée avant le ticket : seul le forum est relié.
    content.pop("source_document_version_ids")
    old = add_question_version(
        db_session, question, question_type="short_answer", content_json=content,
        source_document_version_id=forum_id,
    )
    db_session.commit()
    served = _session(db_session, old.id, question.module_id)

    assert repair_dossier_references(db_session)["repaired"] == 1
    db_session.commit()
    db_session.refresh(question)
    assert question.current_version_id != old.id
    assert _shown_titles(db_session, question.current_version.content_json) == [
        fse_bank.FSE07_SCHOOL_TITLE, fse_bank.FSE07_FORUM_TITLE,
    ]
    assert db_session.get(SessionQuestion, served.session_questions[0].id).question_version_id == old.id
    assert old.content_json.get("source_document_version_ids") is None
    assert repair_dossier_references(db_session) == {"repaired": 0, "unresolved": 0}


def test_the_corrector_receives_every_document_shown_with_its_number(db_session):
    _import_fse_banks(db_session)
    fact = _question(db_session, "FSE07", "Le forum affirme que Lucas")
    session = _session(db_session, fact.current_version_id, fact.module_id)
    titles = [context.course_title for context in _document_contexts_for(db_session, session.session_questions)]
    assert titles == [fse_bank.FSE07_SCHOOL_TITLE, fse_bank.FSE07_FORUM_TITLE]

    limit = _question(db_session, "FSE16", "D'après le document 3")
    session = _session(db_session, limit.current_version_id, limit.module_id)
    titles = [context.course_title for context in _document_contexts_for(db_session, session.session_questions)]
    assert titles == [
        f"Document 1 — {fse_bank.FSE16_PROPOSAL_TITLE}",
        f"Document 3 — {fse_bank.FSE16_REACTIONS_TITLE}",
    ]


def test_session_page_shows_the_note_and_the_forum(authenticated_client, db_session):
    _import_fse_banks(db_session)
    fact = _question(db_session, "FSE07", "Le forum affirme que Lucas")
    session = _session(db_session, fact.current_version_id, fact.module_id)
    html = authenticated_client.get(f"/sessions/{session.id}?q=1").text
    assert html.count('class="jc-sd source-document-panel') == 2
    assert "Athénée du Parc" in html and "Encore une école qui ne fait rien" in html


def test_results_and_export_use_the_session_label(authenticated_client, db_session, monkeypatch):
    from app.ai.fake_provider import FakeAIProvider
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    _import_fse_banks(db_session)
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    limit = _question(db_session, "FSE16", "D'après le document 3")
    session = _session(db_session, limit.current_version_id, limit.module_id, mode=SessionMode.PRACTICE)
    page = authenticated_client.get(f"/sessions/{session.id}?q=1")
    token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
    authenticated_client.post(
        f"/sessions/{session.id}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "La capacité du réseau."},
    )
    confirm = authenticated_client.get(f"/sessions/{session.id}/submit-confirm")
    token = re.search(r'name="csrf_token" value="([^"]+)"', confirm.text).group(1)
    authenticated_client.post(f"/sessions/{session.id}/submit", data={"csrf_token": token, "severity": "3"})
    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)
    results = authenticated_client.get(f"/sessions/{session.id}").text
    assert "Revoir le document — Document 3 : Réactions des groupes concernés" in results
    export = authenticated_client.get(f"/sessions/{session.id}/export.md").text
    assert "- Document 3 : Réactions des groupes concernés" in export


@pytest.mark.parametrize("question_type", ["short_answer", "long_answer", "classification", "document_analysis"])
def test_document_list_must_contain_the_primary_document(question_type):
    base = {
        "short_answer": {"prompt": "p", "rubric": "r"},
        "long_answer": {"prompt": "p", "rubric": "r"},
        "classification": {"prompt": "p", "categories": ["a", "b"], "elements": ["x", "y"], "correct_categories": [0, 1]},
        "document_analysis": {"prompt": "p", "rubric": "r"},
    }[question_type]
    validate_content(question_type, 1, {**base, "source_document_version_id": 1, "source_document_version_ids": [1, 2]})
    with pytest.raises(ValueError):
        validate_content(question_type, 1, {**base, "source_document_version_id": 3, "source_document_version_ids": [1, 2]})
    with pytest.raises(ValueError):
        validate_content(question_type, 1, {**base, "source_document_version_id": 1, "source_document_version_ids": [1, 1]})

"""Ticket #152, retour du propriétaire du 22/10 — question FSE16 « D'après le document 3… »
vue sans le document 1 dans un examen blanc FSE17.

Cause établie sur la base réelle : la session d'examen avait été créée AVANT la mise à jour
(#152 du 21/10) et avait gardé, comme prévu, la version 1 de la question (document 3 seul).
Garanties vérifiées :
- une ancienne session garde sa version figée (réponses, notes et version intactes), mais
  montre aussi — signalés « ajouté » — les documents de contexte ajoutés depuis par la version
  courante de la MÊME question, dans l'ordre du dossier (document 1 puis document 3) ;
- la correction reçoit exactement ces mêmes documents ;
- un changement de version qui retire ou remplace un document n'est jamais mélangé ;
- les nouvelles sessions (FSE17, FSE16) servent toujours la version courante ;
- la note budgétaire FSE16 (document 2, « La subvention serait financée… ») est montrée avec
  la proposition, et l'audit repère un document d'accompagnement servi seul ;
- la consigne FSE09 « Et pour ces trois autres demandes » (cas #129) est autonome.
"""

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA
from app.v1 import fse_bank
from app.v1.models import (
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocumentVersion,
    User,
    add_question_version,
)
from app.v1.prompt_clarity import audit_prompt_clarity, clarity_problems
from app.v1.routes_sessions import _build_results_rows
from app.v1.session_service import _document_contexts_for, build_question_display, start_session
from tests.test_ticket152_prompt_clarity import _import_fse_banks, _question, _shown

LIMIT_PROMPT = "D'après le document 3 (réactions des groupes concernés), quelle limite"


def _student(db_session) -> User:
    user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    if user is None:
        user = User(email="eleve-test@example.test", password_hash="x", display_name="t")
        db_session.add(user)
        db_session.flush()
    return user


def _old_session_on_reactions_only(db_session):
    """Reproduit la session du retour : version servie = document 3 seul, puis la banque
    passe à une version qui montre la proposition (document 1) avant le document 3."""
    _import_fse_banks(db_session)
    question = _question(db_session, "FSE16", LIMIT_PROMPT)
    current = dict(question.current_version.content_json)
    proposal_id, reactions_id = current["source_document_version_ids"]
    old_content = {k: v for k, v in current.items() if k != "source_document_version_ids"}
    old_content["source_document_version_id"] = reactions_id
    old_version = add_question_version(
        db_session, question, question_type="short_answer", content_json=old_content,
        source_document_version_id=reactions_id,
    )
    db_session.flush()
    session = QuestionnaireSession(
        user_id=_student(db_session).id, mode=SessionMode.EXAM, module_id=question.module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1, parameters_json={"scope": "fse17_transversal"},
    )
    db_session.add(session)
    db_session.flush()
    session_question = SessionQuestion(
        session_id=session.id, question_version_id=old_version.id, position=1, points_max=1.0,
        source_document_version_id=reactions_id,
    )
    db_session.add(session_question)
    db_session.flush()
    db_session.add(SessionAnswer(session_question_id=session_question.id, answer_json={"text": "réponse"}))
    add_question_version(
        db_session, question, question_type="short_answer", content_json=current,
        source_document_version_id=current["source_document_version_id"],
    )
    db_session.commit()
    return session, session_question, old_version, proposal_id, reactions_id


def test_old_session_shows_the_proposal_before_the_reactions_marked_as_added(db_session):
    _session, session_question, old_version, proposal_id, reactions_id = _old_session_on_reactions_only(db_session)
    display = build_question_display(db_session, session_question)
    assert [doc.id for doc in display.source_documents] == [proposal_id, reactions_id]
    assert display.added_context_document_ids == [proposal_id]
    # Rien n'est modifié dans la session : version figée, réponse conservée.
    db_session.refresh(session_question)
    assert session_question.question_version_id == old_version.id
    assert session_question.answer.answer_json == {"text": "réponse"}


def test_correction_receives_the_same_documents_as_the_student(db_session):
    _session, session_question, _old, proposal_id, reactions_id = _old_session_on_reactions_only(db_session)
    keys = {context.course_key for context in _document_contexts_for(db_session, [session_question])}
    assert keys == {f"source-document-{proposal_id}", f"source-document-{reactions_id}"}
    rows = _build_results_rows(db_session, [session_question])
    assert [(d["id"], d["added_context"]) for d in rows[0]["source_documents"]] == [
        (proposal_id, True), (reactions_id, False),
    ]


def test_session_page_announces_the_restored_context(authenticated_client, db_session):
    session, *_rest = _old_session_on_reactions_only(db_session)
    html = authenticated_client.get(f"/sessions/{session.id}").text
    assert "data-context-restored" in html and "Contexte complété" in html
    assert html.count("data-context-added") == 1
    assert html.index("revenus modestes") < html.index("ménage concerné")


def test_documents_of_incompatible_versions_are_never_mixed(db_session):
    _session, session_question, _old, proposal_id, reactions_id = _old_session_on_reactions_only(db_session)
    question = session_question.question_version.question
    # Version courante qui REMPLACE le document 3 : la session garde ses seuls documents.
    content = dict(question.current_version.content_json)
    content["source_document_version_id"] = proposal_id
    content.pop("source_document_version_ids")
    add_question_version(db_session, question, question_type="short_answer", content_json=content)
    db_session.commit()
    display = build_question_display(db_session, session_question)
    assert [doc.id for doc in display.source_documents] == [reactions_id]
    assert display.added_context_document_ids == []


def test_new_fse17_and_fse16_sessions_serve_current_versions_with_document_1(db_session):
    _import_fse_banks(db_session)
    user = _student(db_session)
    seen_fse16_dossier = 0
    for code, count in (("FSE17", 20), ("FSE17", 20), ("FSE16", 10), ("FSE16", 10)):
        uaa = db_session.query(UAA).filter_by(code=code).one()
        session = start_session(
            db_session, user=user, module_id=uaa.module_id, uaa_id=uaa.id, uaa_code=code,
            mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest.ADAPTIVE, provider=FakeAIProvider(),
            question_count=count,
        )
        for session_question in session.session_questions:
            question = session_question.question_version.question
            assert session_question.question_version_id == question.current_version_id
            display = build_question_display(db_session, session_question)
            assert display.added_context_document_ids == []
            titles = [doc.title for doc in display.source_documents]
            if fse_bank.FSE16_REACTIONS_TITLE in titles or fse_bank.FSE16_BUDGET_NOTE_TITLE in titles:
                assert titles[0] == fse_bank.FSE16_PROPOSAL_TITLE
                seen_fse16_dossier += 1
        session.status = SessionStatus.ABANDONED
        db_session.commit()
    assert seen_fse16_dossier > 0


def test_fse16_budget_note_is_shown_with_the_proposal(db_session):
    _import_fse_banks(db_session)
    for start in ("D'après la note budgétaire (document 2)", "Analyse la note budgétaire (document 2)"):
        content = _question(db_session, "FSE16", start).current_version.content_json
        assert [doc.title for doc in _shown(db_session, content)] == [
            fse_bank.FSE16_PROPOSAL_TITLE, fse_bank.FSE16_BUDGET_NOTE_TITLE,
        ]


def test_audit_flags_an_accompanying_document_served_alone(db_session):
    _import_fse_banks(db_session)
    question = _question(db_session, "FSE16", "Analyse la note budgétaire (document 2)")
    content = dict(question.current_version.content_json)
    content.pop("source_document_version_ids")
    note = db_session.query(SourceDocumentVersion).filter_by(title=fse_bank.FSE16_BUDGET_NOTE_TITLE).first()
    content["source_document_version_id"] = note.id
    version = add_question_version(db_session, question, question_type="document_analysis", content_json=content)
    db_session.commit()
    assert "« la subvention/la proposition… » sans document qui la présente" in clarity_problems(db_session, version)
    assert audit_prompt_clarity(db_session)["flagged"]


def test_fse09_permanence_prompt_names_the_requests(db_session):
    _import_fse_banks(db_session)
    content = _question(db_session, "FSE09", "D'après les fiches de la permanence").current_version.content_json
    assert "demandes 1, 6 et 7" in content["prompt"]
    assert [e.split(" — ")[0] for e in content["elements"]] == ["Demande 1", "Demande 6", "Demande 7"]

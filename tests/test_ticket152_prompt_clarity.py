"""Ticket #152 — consignes FSE autonomes et contexte des questions extraites de dossiers.

Garanties vérifiées :
- la banque FSE neuve ne contient plus de consigne dépendante d'un contexte absent
  (« maintenant… ces trois autres », méthode non nommée, « cette aide » sans antécédent) ;
- les cas des captures : FSE16 Q2 (effets/limites avec la proposition), FSE06 Q3 (méthode
  nommée, étapes contraintes), FSE15 Q7 (deux actions séparées, usage partiel accepté),
  FSE09 Q8 (tâche autonome, document sans le niveau de pouvoir écrit) ;
- une banque déjà importée est mise à niveau par une NOUVELLE version (idempotente), sans
  toucher une version ou un document déjà servis dans une session ;
- une remise en ordre laissée vide ou avec des positions en double n'est plus enregistrée
  dans l'ordre de la banque (fausse réussite) : elle reste sans réponse, choix conservés.
"""

import pytest

from app.ai.local_correction import correct_locally
from app.models import UAA
from app.seed import seed
from app.v1 import fse_bank
from app.v1.ai_bridge import answer_json_to_submitted, content_to_questionnaire_question
from app.v1.fse09_content import FSE09_SITUATIONS_EXAM_TEXT, FSE09_SITUATIONS_TEXT
from app.v1.models import (
    ContentStatus,
    Question,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocumentVersion,
    User,
)
from app.v1.prompt_clarity import audit_prompt_clarity, clarity_repairs, repair_prompt_clarity
from app.v1.routes_sessions import _FSE_BANK_IMPORTERS


def _import_fse_banks(db_session) -> None:
    seed()
    for slug, importer in _FSE_BANK_IMPORTERS.items():
        uaa = db_session.query(UAA).filter_by(slug=slug).first()
        importer(db_session, uaa.module, uaa)
    db_session.commit()


def _questions(db_session, code: str) -> list[Question]:
    uaa = db_session.query(UAA).filter_by(code=code).first()
    return (
        db_session.query(Question)
        .filter_by(uaa_id=uaa.id, status=ContentStatus.ACTIVE)
        .order_by(Question.id)
        .all()
    )


def _question(db_session, code: str, prompt_start: str) -> Question:
    for question in _questions(db_session, code):
        if question.current_version.content_json.get("prompt", "").startswith(prompt_start):
            return question
    raise AssertionError(prompt_start)


def _shown(db_session, content: dict) -> list[SourceDocumentVersion]:
    ids = content.get("source_document_version_ids") or (
        [content["source_document_version_id"]] if content.get("source_document_version_id") else []
    )
    return [db_session.get(SourceDocumentVersion, doc_id) for doc_id in ids]


def _session(db_session, user: User, question: Question) -> QuestionnaireSession:
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.EXAM, module_id=question.module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(SessionQuestion(
        session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
    ))
    db_session.commit()
    return session


def _legacy_bank(db_session, monkeypatch) -> None:
    """Banque telle qu'importée avant #152 : consignes d'origine, document FSE09 du cours."""
    monkeypatch.setattr(fse_bank, "apply_clarity", lambda db, uaa, question_type, content: content)
    monkeypatch.setattr(fse_bank, "FSE09_SITUATIONS_EXAM_TEXT", FSE09_SITUATIONS_TEXT)
    _import_fse_banks(db_session)
    monkeypatch.undo()


# --- Banque neuve --------------------------------------------------------------------------


def test_fresh_fse_bank_has_no_context_dependent_prompt(db_session):
    _import_fse_banks(db_session)
    report = audit_prompt_clarity(db_session)
    assert report["audited"] > 200
    assert report["flagged"] == []


def test_every_repair_matches_exactly_one_fresh_question(db_session):
    _import_fse_banks(db_session)
    for repair in clarity_repairs():
        matches = [
            q for q in _questions(db_session, repair.uaa_code)
            if q.current_version.question_type == repair.question_type
            and all(q.current_version.content_json.get(k) == v for k, v in repair.fields.items())
        ]
        assert len(matches) == 1, repair.fields["prompt"]


def test_method_orderings_are_announced_recalls_with_named_course(db_session):
    _import_fse_banks(db_session)
    orderings = [
        (code, q.current_version.content_json)
        for code in (f"FSE{n:02d}" for n in range(2, 17))
        for q in _questions(db_session, code)
        if q.current_version.question_type == "ordering"
        and "méthode" in q.current_version.content_json["prompt"]
    ]
    assert len(orderings) == 15
    for code, content in orderings:
        assert content["prompt"].startswith(f"Rappel de méthode (cours {code} «"), code
        assert "scénario en ligne" not in content["prompt"]
        assert "vues en cours" not in " ".join(item["label"] for item in content["items"])
        assert 3 <= len(content["items"]) <= 4


def test_capture_q2_fse16_reactions_are_analysed_with_the_proposal(db_session):
    _import_fse_banks(db_session)
    question = _question(db_session, "FSE16", "Le document 1 présente une proposition")
    content = question.current_version.content_json
    assert content["categories"] == ["Effet attendu", "Limite ou coût"]
    assert "Association" not in content["categories"]
    assert [doc.title for doc in _shown(db_session, content)] == [
        fse_bank.FSE16_PROPOSAL_TITLE, fse_bank.FSE16_REACTIONS_TITLE,
    ]
    # Les deux autres questions sur le document 3 montrent aussi la proposition.
    for start in ("D'après le document 3", "Analyse la réaction de l'entreprise"):
        shown = _shown(db_session, _question(db_session, "FSE16", start).current_version.content_json)
        assert shown[0].title == fse_bank.FSE16_PROPOSAL_TITLE


def test_capture_q3_fse06_method_names_course_and_categories(db_session):
    _import_fse_banks(db_session)
    content = _question(db_session, "FSE06", "Rappel de méthode").current_version.content_json
    assert "FSE06" in content["prompt"] and "comportement en ligne" in content["prompt"]
    labels = [item["label"] for item in content["items"]]
    assert "simple critique ou opinion" in labels[1] and "cyberharcèlement" in labels[1]


def test_capture_q7_fse15_separates_the_two_actions_and_accepts_partial_use(db_session):
    _import_fse_banks(db_session)
    content = _question(db_session, "FSE15", "D'après le document, l'État verse").current_version.content_json
    assert "(a)" in content["prompt"] and "(b)" in content["prompt"]
    assert "premier flux" not in content["prompt"]
    assert "PARTIEL" in content["rubric"]


def test_capture_q8_fse09_tasks_are_autonomous_and_document_hides_the_level(db_session):
    _import_fse_banks(db_session)
    content = _question(db_session, "FSE09", "Pour chacune des situations 5, 6 et 7").current_version.content_json
    assert all(element.startswith("Situation ") and " — " in element for element in content["elements"])
    document = _shown(db_session, content)[0]
    assert document.content_text == FSE09_SITUATIONS_EXAM_TEXT
    for revealing in ("Une région", "Une communauté", "Une commune", "Une province", "L'État décide"):
        assert revealing not in document.content_text
    mcq = _question(db_session, "FSE09", "Dans la situation 9").current_version.content_json
    assert "province" not in mcq["prompt"]


# --- Banque déjà importée ------------------------------------------------------------------


def test_repair_upgrades_a_legacy_bank_by_new_versions_and_is_idempotent(db_session, monkeypatch):
    _legacy_bank(db_session, monkeypatch)
    assert audit_prompt_clarity(db_session)["flagged"]
    user = User(email="eleve-152@example.test", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.flush()
    served = _question(db_session, "FSE09", "Associe maintenant ces trois autres situations")
    served_version_id = served.current_version_id
    served_document_id = served.current_version.content_json["source_document_version_id"]
    session = _session(db_session, user, served)

    result = repair_prompt_clarity(db_session)
    db_session.commit()
    # 15 méthodes + 9 consignes, et les 5 autres questions FSE09 qui montrent le document,
    # réorientées vers sa version d'examen.
    assert result == {"repaired": 29, "unresolved": 0, "documents": 1}
    assert repair_prompt_clarity(db_session) == {"repaired": 0, "unresolved": 0, "documents": 0}
    assert audit_prompt_clarity(db_session)["flagged"] == []

    db_session.refresh(served)
    assert served.current_version_id != served_version_id
    new_content = served.current_version.content_json
    assert new_content["prompt"].startswith("Pour chacune des situations 5, 6 et 7")
    assert db_session.get(SourceDocumentVersion, new_content["source_document_version_id"]).content_text == (
        FSE09_SITUATIONS_EXAM_TEXT
    )
    # La session déjà générée garde la version et le document servis.
    session_question = db_session.query(SessionQuestion).filter_by(session_id=session.id).one()
    assert session_question.question_version_id == served_version_id
    old = session_question.question_version.content_json
    assert old["prompt"].startswith("Associe maintenant")
    assert db_session.get(SourceDocumentVersion, served_document_id).content_text == FSE09_SITUATIONS_TEXT
    # Chaque question FSE09 qui montre le document montre la version d'examen.
    for question in _questions(db_session, "FSE09"):
        for document in _shown(db_session, question.current_version.content_json):
            assert document.content_text == FSE09_SITUATIONS_EXAM_TEXT


def test_repaired_legacy_content_equals_the_fresh_bank(db_session, monkeypatch):
    _legacy_bank(db_session, monkeypatch)
    repair_prompt_clarity(db_session)
    db_session.commit()
    for repair in clarity_repairs():
        matches = [
            q for q in _questions(db_session, repair.uaa_code)
            if all(q.current_version.content_json.get(k) == v for k, v in repair.fields.items())
        ]
        assert len(matches) == 1, repair.fields["prompt"]


# --- Remise en ordre : pas de fausse réussite ----------------------------------------------


def _ordering_session(db_session):
    _import_fse_banks(db_session)
    user = db_session.query(User).filter_by(email="eleve-test@example.test").one()
    question = _question(db_session, "FSE12", "Rappel de méthode")
    return _session(db_session, user, question), question


def _score(question: Question, answer_json: dict) -> float:
    version = question.current_version
    content = version.content_json
    item = content_to_questionnaire_question(
        question_id="q", question_type="ordering", content=content, points_max=1.0,
    )
    return correct_locally(item, answer_json_to_submitted("ordering", content, answer_json)).points_awarded


@pytest.mark.parametrize(
    "positions",
    [
        {},  # navigation sans rien choisir
        {"e1": "1", "e2": "1", "e3": "1", "e4": "1"},  # même position partout
        {"e1": "1", "e2": "2"},  # saisie incomplète
    ],
)
def test_incomplete_or_duplicate_ordering_is_never_a_false_success(authenticated_client, db_session, positions):
    session, question = _ordering_session(db_session)
    data = {"position": "1", "direction": "next", **{f"position__{k}": v for k, v in positions.items()}}
    response = authenticated_client.post(f"/sessions/{session.id}/answer", data=data, follow_redirects=False)
    assert response.status_code == 303
    answer = db_session.query(SessionAnswer).one()
    assert answer.answer_json["order"] == []
    assert _score(question, answer.answer_json) == 0
    page = authenticated_client.get(f"/sessions/{session.id}?q=1").text
    assert "Choisir une position" in page
    if positions == {"e1": "1", "e2": "2"}:
        # Les choix partiels sont conservés à la reprise.
        assert answer.answer_json["positions"] == {"e1": 1, "e2": 2}
        assert '<option value="2" selected>2</option>' in page


def test_complete_ordering_is_saved_by_explicit_positions(authenticated_client, db_session):
    session, question = _ordering_session(db_session)
    data = {"position": "1", "direction": "next",
            "position__e4": "1", "position__e3": "2", "position__e2": "3", "position__e1": "4"}
    authenticated_client.post(f"/sessions/{session.id}/answer", data=data, follow_redirects=False)
    answer = db_session.query(SessionAnswer).one()
    assert answer.answer_json == {"order": ["e4", "e3", "e2", "e1"]}
    assert _score(question, answer.answer_json) == 0
    data.update({"position__e1": "1", "position__e2": "2", "position__e3": "3", "position__e4": "4"})
    authenticated_client.post(f"/sessions/{session.id}/answer", data=data, follow_redirects=False)
    db_session.refresh(answer)
    assert _score(question, answer.answer_json) == 1

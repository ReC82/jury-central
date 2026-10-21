"""Ticket #153 — remise en ordre par cartes (glisser-déposer, tactile, clavier).

Garanties vérifiées côté serveur (le comportement JavaScript est vérifié à la main, voir
le rapport) :
- la page d'entraînement/examen rend des cartes dans l'ordre mélangé de la session, état
  « sans réponse » au chargement (positions à 0), sans jamais exposer l'ordre correct ;
- l'autosave JSON enregistre l'ordre par identifiants stables, refuse tout ordre invalide
  sans toucher la réponse existante, et la reprise réaffiche l'ordre enregistré ;
- double sauvegarde (autosave puis navigation) : une seule réponse, même score ;
- quiz : cartes sans autosave, validation volontaire inchangée ;
- les anciennes réponses (positions partielles des listes déroulantes) restent lisibles.
"""

import re

import pytest

from app.ai.local_correction import correct_locally
from app.v1.ai_bridge import answer_json_to_submitted, content_to_questionnaire_question
from app.v1.display_order import SNAPSHOT_KEY
from app.v1.models import (
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    create_question,
)
from tests.test_ticket137_quiz import _choose, _content, _csrf, _session_id, _start, _user

ITEMS = [
    {"id": "e1", "label": "Identifier le problème public"},
    {"id": "e2", "label": "Rechercher les acteurs concernés"},
    {"id": "e3", "label": "Comparer les solutions possibles"},
    {"id": "e4", "label": "Évaluer la décision prise"},
]
CORRECT = ["e1", "e2", "e3", "e4"]
SHOWN = ["e3", "e1", "e4", "e2"]


def _ordering_question(db, module, uaa):
    return create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type="ordering",
        generation_source="manual",
        content_json={
            "prompt": "Remets dans l'ordre les étapes d'analyse d'une décision publique (ticket 153).",
            "items": ITEMS,
            "correct_order": CORRECT,
            "explanation": "On part du problème, puis les acteurs, les solutions et l'évaluation.",
        },
    )


@pytest.fixture()
def exam(authenticated_client, db_session):
    content = _content(db_session, per_uaa=0)
    module, (uaa,) = content["FSE"]
    question = _ordering_question(db_session, module, uaa)
    db_session.flush()
    session = QuestionnaireSession(
        user_id=_user(db_session).id, mode=SessionMode.EXAM, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    sq = SessionQuestion(
        session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
        content_snapshot_json={SNAPSHOT_KEY: {"items": SHOWN}},
    )
    db_session.add(sq)
    db_session.commit()
    return authenticated_client, session, sq


def _card_ids(html: str) -> list[str]:
    return re.findall(r'<li class="jc-order-card" data-id="([^"]+)"', html)


def _score(sq: SessionQuestion, answer_json: dict) -> float:
    content = sq.question_version.content_json
    item = content_to_questionnaire_question(
        question_id="q", question_type="ordering", content=content, points_max=1.0,
    )
    return correct_locally(item, answer_json_to_submitted("ordering", content, answer_json)).points_awarded


def _autosave(client, session, sq, answer_json):
    return client.post(f"/api/v1/sessions/{session.id}/answers/{sq.id}", json={"answer_json": answer_json})


def test_cards_start_unanswered_in_session_order_without_solution(exam):
    client, session, sq = exam
    page = client.get(f"/sessions/{session.id}?q=1").text
    assert _card_ids(page) == SHOWN
    assert 'data-answered="false"' in page
    assert f'data-autosave-url="/api/v1/sessions/{session.id}/answers/{sq.id}"' in page
    assert "Fais glisser les étapes pour les mettre dans l'ordre" in page
    assert "Conserver cet ordre" in page and "Monter" in page and "Descendre" in page
    assert "vendor/sortablejs/Sortable.min.js" in page and "js/ordering_cards.js" in page
    # Repli sans JavaScript : positions vides, aucune réponse pré-remplie.
    assert page.count('<option value="0" selected>Choisir une position</option>') == 4
    assert "correct_order" not in page


def test_autosave_saves_by_ids_and_resume_shows_saved_order(exam, db_session):
    client, session, sq = exam
    response = _autosave(client, session, sq, {"order": ["e2", "e1", "e3", "e4"]})
    assert response.status_code == 200
    assert response.json() == {"saved": True}  # jamais de verdict ni de solution
    answer = db_session.query(SessionAnswer).one()
    assert answer.answer_json == {"order": ["e2", "e1", "e3", "e4"]}

    page = client.get(f"/sessions/{session.id}?q=1").text
    assert _card_ids(page) == ["e2", "e1", "e3", "e4"]
    assert 'data-answered="true"' in page
    assert '<option value="1" selected>1</option>' in page  # champs repris tels quels


@pytest.mark.parametrize(
    "answer_json",
    [
        {"order": ["e1", "e1", "e2", "e3"]},  # doublon
        {"order": ["e1", "e2", "e3"]},  # élément manquant
        {"order": ["e1", "e2", "e3", "e9"]},  # élément inconnu
        {"order": [1, 2, 3, 4]},  # pas des identifiants
        {"order": "e1,e2,e3,e4"},
        {"positions": {"e1": 1}},
    ],
)
def test_autosave_rejects_invalid_order_and_keeps_previous_answer(exam, db_session, answer_json):
    client, session, sq = exam
    assert _autosave(client, session, sq, {"order": SHOWN}).status_code == 200
    assert _autosave(client, session, sq, answer_json).status_code == 422
    db_session.expire_all()
    assert db_session.query(SessionAnswer).one().answer_json == {"order": SHOWN}


def test_empty_order_clears_to_unanswered(exam, db_session):
    client, session, sq = exam
    _autosave(client, session, sq, {"order": CORRECT})
    assert _autosave(client, session, sq, {"order": []}).status_code == 200
    db_session.expire_all()
    answer = db_session.query(SessionAnswer).one()
    assert answer.answer_json == {"order": []}
    assert _score(sq, answer.answer_json) == 0


def test_double_save_autosave_then_navigation_keeps_one_answer_and_score(exam, db_session):
    client, session, sq = exam
    _autosave(client, session, sq, {"order": CORRECT})
    data = {"position": "1", "direction": "next",
            **{f"position__{item_id}": str(i) for i, item_id in enumerate(CORRECT, start=1)}}
    assert client.post(f"/sessions/{session.id}/answer", data=data, follow_redirects=False).status_code == 303
    db_session.expire_all()
    (answer,) = db_session.query(SessionAnswer).all()
    assert answer.answer_json == {"order": CORRECT}
    assert _score(sq, answer.answer_json) == 1


def test_navigation_without_interaction_stays_unanswered(exam, db_session):
    client, session, sq = exam
    data = {"position": "1", "direction": "next", **{f"position__{i}": "0" for i in CORRECT}}
    client.post(f"/sessions/{session.id}/answer", data=data, follow_redirects=False)
    answer = db_session.query(SessionAnswer).one()
    assert answer.answer_json["order"] == []
    assert _score(sq, answer.answer_json) == 0


def test_legacy_partial_positions_stay_readable(exam, db_session):
    client, session, sq = exam
    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"order": [], "positions": {"e1": 2}}))
    db_session.commit()
    page = client.get(f"/sessions/{session.id}?q=1").text
    assert 'data-answered="false"' in page
    assert _card_ids(page) == SHOWN
    assert '<option value="2" selected>2</option>' in page  # valeur partielle gardée


def test_autosave_refused_once_session_is_finished(exam, db_session):
    client, session, sq = exam
    session.status = SessionStatus.CORRECTING
    db_session.commit()
    assert _autosave(client, session, sq, {"order": CORRECT}).status_code == 409


# --- Quiz ---------------------------------------------------------------------------------


@pytest.fixture()
def quiz(authenticated_client, db_session):
    content = _content(db_session, per_uaa=0)
    module, (uaa,) = content["FSE"]
    _ordering_question(db_session, module, uaa)
    db_session.commit()
    _choose(authenticated_client)
    session_id = _session_id(_start(authenticated_client, uaa="t137-fse01"))
    return authenticated_client, session_id


def test_quiz_cards_have_no_autosave_and_validation_stays_voluntary(quiz, db_session):
    client, session_id = quiz
    page = client.get(f"/quiz/parties/{session_id}").text
    assert len(_card_ids(page)) == 4
    assert "data-autosave-url" not in page
    assert "Valider ma réponse" in page and "correct_order" not in page

    # Validation sans position : refusée, aucune note.
    client.post(f"/quiz/parties/{session_id}/valider",
                data={"csrf_token": _csrf(page), "position": "1"}, follow_redirects=False)
    db_session.expire_all()
    assert db_session.query(SessionAnswer).filter(SessionAnswer.points_awarded.isnot(None)).count() == 0

    # Ordre explicite (comme « Conserver cet ordre » ou après déplacement) : corrigé.
    data = {"csrf_token": _csrf(page), "position": "1",
            **{f"position__{item_id}": str(i) for i, item_id in enumerate(CORRECT, start=1)}}
    client.post(f"/quiz/parties/{session_id}/valider", data=data, follow_redirects=False)
    db_session.expire_all()
    (answer,) = db_session.query(SessionAnswer).all()
    assert answer.answer_json == {"order": CORRECT}
    assert answer.points_awarded == 1.0

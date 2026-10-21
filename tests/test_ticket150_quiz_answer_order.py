"""Ticket #150 — quiz : choisir systématiquement la première réponse ne doit plus réussir.

Cause constatée : les QCM des banques rédigées à la main stockent souvent la bonne réponse
en premier et l'écran suivait l'ordre de la banque. Correctif : permutation propre à
chaque question servie, persistée, correction inchangée (par identifiant). Permutations
contrôlées (graines fixes ou permutation posée explicitement) : aucun test aléatoire."""

import random
import re

import pytest

from app.v1 import display_order
from app.v1.display_order import SNAPSHOT_KEY, apply_display_order, build_display_order
from app.v1.models import (
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    create_question,
)
from app.v1.parcours import resolve_keys
from app.v1.quiz_service import build_catalog, resolve_scope, start_quiz, validate_quiz_answer
from app.v1.session_service import _finalize_session, build_question_display
from tests.test_ticket137_quiz import _choose, _content, _csrf, _session_id, _start, _text, _user

OPTIONS = [
    {"option_id": "a", "label": "Bonne réponse"},
    {"option_id": "b", "label": "Leurre un"},
    {"option_id": "c", "label": "Leurre deux"},
    {"option_id": "d", "label": "Leurre trois"},
]


def _bank_mc(db, module, uaa, *, prompt="Quelle est la bonne réponse (ticket 150) ?", **extra):
    content = {"prompt": prompt, "options": OPTIONS, "correct_option_ids": ["a"], **extra}
    return create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type="multiple_choice",
        generation_source="manual", content_json=content,
    )


@pytest.fixture()
def player(authenticated_client, db_session):
    """Un seul cours (FSE01) avec un QCM dont la bonne réponse est PREMIÈRE dans la banque."""
    content = _content(db_session, per_uaa=0)
    module, (uaa,) = content["FSE"]
    question = _bank_mc(db_session, module, uaa)
    db_session.commit()
    _choose(authenticated_client)
    return authenticated_client, question


def _force_order(db, session_id, order):
    session = db.get(QuestionnaireSession, session_id)
    (sq,) = session.session_questions
    sq.content_snapshot_json = {SNAPSHOT_KEY: {"options": order}}
    db.commit()
    return sq


def _displayed_option_ids(html: str) -> list[str]:
    return re.findall(r'name="option_id"\s+id="option-\d+" value="([^"]+)"', html)


# --- Permutation ------------------------------------------------------------------------------


def test_permutation_keeps_ids_and_varies_the_first_position_with_fixed_seeds():
    content = {"options": OPTIONS, "correct_option_ids": ["a"]}
    firsts = []
    for seed in range(40):
        order = build_display_order("multiple_choice", content, random.Random(seed))["options"]
        assert sorted(order) == ["a", "b", "c", "d"]
        firsts.append(order[0])
    # Le premier choix n'est plus mécaniquement la bonne réponse, sans imposer une
    # distribution uniforme ni « jamais en premier » (qui serait un autre indice).
    assert set(firsts) == {"a", "b", "c", "d"}
    assert 0 < firsts.count("a") < len(firsts) // 2


def test_position_dependent_options_and_author_choice_are_respected():
    options = [*OPTIONS[:3], {"option_id": "z", "label": "Toutes les réponses ci-dessus"}]
    for seed in range(10):
        order = build_display_order("multiple_choice", {"options": options}, random.Random(seed))["options"]
        assert order[-1] == "z"
    assert build_display_order("multiple_choice", {"options": OPTIONS, "shuffle": False}) is None
    assert build_display_order("classification", {"categories": ["x", "y"]}) is None


def test_ordering_is_never_displayed_already_solved():
    items = [{"id": "i1", "label": "1"}, {"id": "i2", "label": "2"}]
    for seed in range(10):
        order = build_display_order("ordering", {"items": items, "correct_order": ["i1", "i2"]}, random.Random(seed))
        assert order == {"items": ["i2", "i1"]}


def test_legacy_session_without_permutation_keeps_bank_order():
    payload = {"options": OPTIONS}
    assert apply_display_order("multiple_choice", payload, None) is payload
    reordered = apply_display_order("multiple_choice", payload, {SNAPSHOT_KEY: {"options": ["c", "a", "d", "b"]}})
    assert [o["option_id"] for o in reordered["options"]] == ["c", "a", "d", "b"]
    assert [o["option_id"] for o in payload["options"]] == ["a", "b", "c", "d"]  # copie


# --- Quiz : affichage, correction, stabilité --------------------------------------------------


def test_first_displayed_wrong_answer_is_wrong_and_permutation_is_stable(player, db_session):
    client, question = player
    session_id = _session_id(_start(client, uaa="t137-fse01"))
    session = db_session.get(QuestionnaireSession, session_id)
    (sq,) = session.session_questions
    stored = sq.content_snapshot_json[SNAPSHOT_KEY]["options"]
    assert sorted(stored) == ["a", "b", "c", "d"]  # permutation persistée à la création
    assert question.current_version.content_json["options"] == OPTIONS  # banque intacte

    _force_order(db_session, session_id, ["c", "a", "d", "b"])
    page = client.get(f"/quiz/parties/{session_id}").text
    assert _displayed_option_ids(page) == ["c", "a", "d", "b"]
    assert _displayed_option_ids(client.get(f"/quiz/parties/{session_id}").text) == ["c", "a", "d", "b"]
    assert "correct_option_ids" not in page and "Bonne réponse" in page

    # L'élève coche la PREMIÈRE réponse affichée (fausse) : faux, aucun point.
    response = client.post(
        f"/quiz/parties/{session_id}/valider",
        data={"csrf_token": _csrf(page), "position": "1", "option_id": "c"},
        follow_redirects=False,
    )
    feedback_html = client.get(response.headers["location"]).text
    feedback = _text(feedback_html)
    assert "Pas tout à fait" in feedback
    # La correction affichée suit l'ordre vu : c (ton choix), a (bonne réponse), d, b.
    labels = re.findall(r'<span class="flex-grow-1">([^<]+)</span>', feedback_html)
    assert labels == ["Leurre deux", "Bonne réponse", "Leurre trois", "Leurre un"]

    # Double validation (même avec la bonne réponse) : aucune recorrection.
    client.post(
        f"/quiz/parties/{session_id}/valider",
        data={"csrf_token": _csrf(page), "position": "1", "option_id": "a"},
    )
    db_session.expire_all()
    (answer,) = db_session.query(SessionAnswer).all()
    assert answer.points_awarded == 0.0
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.score == 0.0
    assert "0 / 1 point" in _text(client.get(f"/quiz/parties/{session_id}").text)


@pytest.mark.parametrize("order", [["a", "b", "c", "d"], ["b", "a", "c", "d"], ["b", "c", "d", "a"]])
def test_correct_answer_recognised_wherever_it_is_displayed(player, db_session, order):
    client, _ = player
    session_id = _session_id(_start(client, uaa="t137-fse01"))
    _force_order(db_session, session_id, order)
    page = client.get(f"/quiz/parties/{session_id}").text
    assert _displayed_option_ids(page) == order
    response = client.post(
        f"/quiz/parties/{session_id}/valider",
        data={"csrf_token": _csrf(page), "position": "1", "option_id": "a"},
        follow_redirects=False,
    )
    assert "Bonne réponse" in _text(client.get(response.headers["location"]).text)
    db_session.expire_all()
    assert db_session.get(QuestionnaireSession, session_id).score == 1.0


def test_each_option_in_isolated_games_only_one_is_credited(player, db_session):
    _client, _ = player
    user = _user(db_session)
    pathway = resolve_keys("cess", "p", "ampcr")
    scope = resolve_scope(build_catalog(db_session, pathway, user), uaa_slugs=["t137-fse01"])
    credited = {}
    for index, option_id in enumerate("abcd"):
        session = start_quiz(
            db_session, user=user, pathway=pathway, scope=scope, count=5,
            difficulty=SessionDifficultyRequest.MEDIUM, retry_of=1000 + index,
        )
        (sq,) = session.session_questions
        answer = validate_quiz_answer(
            db_session, session=session, session_question=sq,
            answer_json={"selected_option_ids": [option_id]},
        )
        credited[option_id] = answer.points_awarded
    assert credited == {"a": 1.0, "b": 0.0, "c": 0.0, "d": 0.0}


def test_multiple_answers_wrong_subset_or_everything_never_gets_the_maximum(player, db_session):
    client, question = player
    user = _user(db_session)
    multi = create_question(
        db_session, module_id=question.module_id, uaa_id=question.uaa_id, question_type="multiple_choice",
        generation_source="manual",
        content_json={
            "prompt": "Quelles sont les deux bonnes réponses (ticket 150) ?", "options": OPTIONS,
            "min_selections": 2, "max_selections": 2, "correct_option_ids": ["a", "c"],
        },
    )
    session = _finalize_session(
        db_session, user=user, module_id=question.module_id, mode=SessionMode.QUIZ,
        difficulty=SessionDifficultyRequest.MEDIUM, selected=[multi],
    )
    (sq,) = session.session_questions
    from app.v1.quiz_service import _correct

    assert _correct(sq, {"selected_option_ids": ["a", "b"]})["points_awarded"] == 0.0
    assert _correct(sq, {"selected_option_ids": ["a"]})["points_awarded"] == 0.0
    assert _correct(sq, {"selected_option_ids": ["a", "b", "c", "d"]})["points_awarded"] == 0.0
    assert _correct(sq, {"selected_option_ids": ["c", "a"]})["points_awarded"] == 1.0

    # Côté écran : cocher « tout » est refusé (réponse incomplète, rien n'est compté).
    _force_order(db_session, session.id, ["b", "d", "a", "c"])
    page = client.get(f"/quiz/parties/{session.id}").text
    refused = client.post(
        f"/quiz/parties/{session.id}/valider",
        data={"csrf_token": _csrf(page), "position": "1", "option_id": ["a", "b", "c", "d"]},
    )
    assert refused.status_code == 422 and "exactement 2" in refused.text


# --- Entraînement / examen : même permutation, correction inchangée ---------------------------


@pytest.mark.parametrize("mode", [SessionMode.PRACTICE, SessionMode.EXAM])
def test_practice_and_exam_sessions_also_get_a_persisted_permutation(player, db_session, monkeypatch, mode):
    _, question = player
    monkeypatch.setattr(display_order.random, "SystemRandom", lambda: random.Random(3))
    expected = build_display_order("multiple_choice", question.current_version.content_json, random.Random(3))
    session = _finalize_session(
        db_session, user=_user(db_session), module_id=question.module_id, mode=mode,
        difficulty=SessionDifficultyRequest.MEDIUM, selected=[question],
    )
    (sq,) = session.session_questions
    assert sq.content_snapshot_json == {SNAPSHOT_KEY: expected}
    shown = [o["option_id"] for o in build_question_display(db_session, sq).public_payload["options"]]
    assert shown == expected["options"]
    assert question.current_version.content_json["options"] == OPTIONS

"""Tests du contrat générique « questionnaire » (ticket #23) : validation de
`QuestionnaireQuestion`/`Questionnaire`/`QuestionnaireRequest`, sérialisation tolérante,
absence de fuite de solution."""

import pytest

from app.ai.context import get_context
from app.ai.schemas import (
    QUESTION_TYPES,
    Questionnaire,
    QuestionnaireQuestion,
    QuestionnaireRequest,
    QuestionnaireValidationError,
)

CONTEXT = get_context("ampcr-mc01")


def _single_choice(**overrides):
    defaults = {
        "question_id": "q1",
        "type": "single_choice",
        "prompt": "La RAM est-elle volatile ?",
        "points_max": 2,
        "choices": ["Oui", "Non"],
        "correct_indexes": [0],
    }
    defaults.update(overrides)
    return QuestionnaireQuestion(**defaults)


# --- Validation par type ---------------------------------------------------------------


def test_question_requires_id_type_prompt_points():
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(question_id="")
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(type="not-a-type")
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(prompt="   ")
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(points_max=0)


def test_single_choice_and_true_false_require_exactly_one_correct_index():
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(correct_indexes=[])
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(correct_indexes=[0, 1])
    with pytest.raises(QuestionnaireValidationError):
        _single_choice(correct_indexes=[5])


def test_multiple_choice_requires_at_least_one_valid_index():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q2", type="multiple_choice", prompt="Lesquels ?", points_max=2,
            choices=["A", "B"], correct_indexes=[],
        )
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q2", type="multiple_choice", prompt="Lesquels ?", points_max=2,
            choices=["A", "B"], correct_indexes=[9],
        )


def test_ordering_requires_valid_permutation():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q3", type="ordering", prompt="Ordonne.", points_max=2,
            order_items=["A", "B"], correct_order=[0, 0],
        )


def test_classification_requires_matching_lengths_and_valid_indexes():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q4", type="classification", prompt="Classe.", points_max=2,
            categories=["C1", "C2"], elements=["E1", "E2"], correct_categories=[0],
        )
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q4", type="classification", prompt="Classe.", points_max=2,
            categories=["C1", "C2"], elements=["E1", "E2"], correct_categories=[0, 9],
        )


def test_matching_requires_matching_lengths_and_valid_indexes():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q5", type="matching", prompt="Associe.", points_max=2,
            pairs_left=["G1", "G2"], pairs_right=["D1", "D2"], correct_pairs=[0],
        )


def test_numeric_requires_answer_and_non_negative_tolerance():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q6", type="numeric", prompt="2+2 ?", points_max=1,
        )
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q6", type="numeric", prompt="2+2 ?", points_max=1,
            numeric_answer=4, numeric_tolerance=-1,
        )


def test_fill_blank_requires_accepted_answers():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireQuestion(
            question_id="q7", type="fill_blank", prompt="Complète.", points_max=1,
        )


def test_semantic_types_require_a_rubric():
    for question_type in ("long_answer", "diagnostic", "procedure"):
        with pytest.raises(QuestionnaireValidationError):
            QuestionnaireQuestion(
                question_id="q8", type=question_type, prompt="Explique.", points_max=3,
            )
        # Avec rubric, construction valide.
        QuestionnaireQuestion(
            question_id="q8", type=question_type, prompt="Explique.", points_max=3,
            rubric="doit mentionner X",
        )


def test_short_answer_and_vocabulary_do_not_require_a_rubric():
    """Contrairement à long_answer/diagnostic/procedure : peuvent être locaux
    (accepted_answers) ou sémantiques (rubric) — voir requires_ai_correction."""
    QuestionnaireQuestion(
        question_id="q9", type="short_answer", prompt="Sigle ?", points_max=1,
        accepted_answers=["RAM"],
    )
    QuestionnaireQuestion(
        question_id="q9", type="vocabulary", prompt="Traduis.", points_max=1,
        rubric="accepter les synonymes usuels",
    )


# --- requires_ai_correction ---------------------------------------------------------------


@pytest.mark.parametrize(
    "question_type",
    [
        "single_choice", "multiple_choice", "true_false", "fill_blank",
        "matching", "classification", "ordering", "numeric",
    ],
)
def test_deterministic_types_never_require_ai_correction(question_type):
    question = _minimal_valid_question(question_type)
    assert question.requires_ai_correction() is False


@pytest.mark.parametrize("question_type", ["long_answer", "diagnostic", "procedure"])
def test_always_semantic_types_always_require_ai_correction(question_type):
    question = QuestionnaireQuestion(
        question_id="qx", type=question_type, prompt="Explique.", points_max=3,
        rubric="grille de test",
    )
    assert question.requires_ai_correction() is True


@pytest.mark.parametrize("question_type", ["short_answer", "vocabulary"])
def test_conditionally_local_types_depend_on_accepted_answers(question_type):
    with_accepted = QuestionnaireQuestion(
        question_id="qy", type=question_type, prompt="Réponds.", points_max=1,
        accepted_answers=["ok"],
    )
    assert with_accepted.requires_ai_correction() is False

    without_accepted = QuestionnaireQuestion(
        question_id="qy", type=question_type, prompt="Réponds.", points_max=1,
        rubric="évaluer le fond",
    )
    assert without_accepted.requires_ai_correction() is True


def _minimal_valid_question(question_type: str) -> QuestionnaireQuestion:
    common = {"question_id": "qz", "type": question_type, "prompt": "Question de test", "points_max": 1}
    if question_type in ("single_choice", "true_false"):
        return QuestionnaireQuestion(**common, choices=["A", "B"], correct_indexes=[0])
    if question_type == "multiple_choice":
        return QuestionnaireQuestion(**common, choices=["A", "B"], correct_indexes=[0, 1])
    if question_type == "ordering":
        return QuestionnaireQuestion(**common, order_items=["A", "B"], correct_order=[1, 0])
    if question_type == "classification":
        return QuestionnaireQuestion(
            **common, categories=["C1", "C2"], elements=["E1", "E2"], correct_categories=[0, 1]
        )
    if question_type == "matching":
        return QuestionnaireQuestion(
            **common, pairs_left=["G1", "G2"], pairs_right=["D1", "D2"], correct_pairs=[0, 1]
        )
    if question_type == "numeric":
        return QuestionnaireQuestion(**common, numeric_answer=4, numeric_tolerance=0)
    if question_type == "fill_blank":
        return QuestionnaireQuestion(**common, accepted_answers=["ok"])
    raise AssertionError(f"type non géré par ce helper : {question_type}")


# --- Représentation publique : jamais la solution -----------------------------------------


@pytest.mark.parametrize("question_type", list(QUESTION_TYPES))
def test_public_dict_never_leaks_solution_fields(question_type):
    if question_type in ("long_answer", "diagnostic", "procedure"):
        question = QuestionnaireQuestion(
            question_id="qp", type=question_type, prompt="Test", points_max=1, rubric="grille",
        )
    elif question_type in ("short_answer", "vocabulary", "fill_blank"):
        question = QuestionnaireQuestion(
            question_id="qp", type=question_type, prompt="Test", points_max=1,
            accepted_answers=["secret"],
        )
    else:
        question = _minimal_valid_question(question_type)

    public = question.to_public_dict()
    forbidden_keys = {
        "correct_indexes", "correct_order", "correct_categories", "correct_pairs",
        "numeric_answer", "accepted_answers", "rubric", "explanation",
    }
    assert forbidden_keys.isdisjoint(public.keys())
    assert "secret" not in str(public)


# --- Questionnaire : unicité, sérialisation tolérante --------------------------------------


def test_questionnaire_rejects_duplicate_question_ids():
    with pytest.raises(QuestionnaireValidationError):
        Questionnaire(mode="practice", questions=[_single_choice(), _single_choice()])


def test_questionnaire_rejects_unknown_mode():
    with pytest.raises(QuestionnaireValidationError):
        Questionnaire(mode="not-a-mode", questions=[_single_choice()])


def test_questionnaire_to_json_from_json_roundtrip():
    questionnaire = Questionnaire(mode="exam", questions=[_single_choice()])
    restored = Questionnaire.from_json(questionnaire.to_json())
    assert restored.mode == "exam"
    assert restored.get_question("q1").correct_indexes == [0]
    assert restored.total_points_max == 2


def test_questionnaire_from_json_tolerates_malformed_input():
    assert Questionnaire.from_json("").questions == []
    assert Questionnaire.from_json("not json").questions == []
    assert Questionnaire.from_json("{}").mode == "practice"


def test_questionnaire_from_json_skips_invalid_questions_without_raising():
    raw = (
        '{"mode": "practice", "questions": ['
        '{"question_id": "valid", "type": "single_choice", "prompt": "x", "points_max": 1, '
        '"choices": ["A", "B"], "correct_indexes": [0]}, '
        '{"question_id": "invalid", "type": "unknown_type", "prompt": "y", "points_max": 1}'
        "]}"
    )
    questionnaire = Questionnaire.from_json(raw)
    assert [q.question_id for q in questionnaire.questions] == ["valid"]


def test_questionnaire_total_points_max_is_sum_of_questions():
    questionnaire = Questionnaire(
        mode="practice",
        questions=[_single_choice(points_max=3), _single_choice(question_id="q2", points_max=7)],
    )
    assert questionnaire.total_points_max == 10


# --- QuestionnaireRequest -----------------------------------------------------------------


def test_questionnaire_request_requires_at_least_one_context():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(), mode="practice", difficulty="facile", question_count=5,
            allowed_types=("single_choice",),
        )


def test_questionnaire_request_rejects_unknown_mode_or_difficulty():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="not-a-mode", difficulty="facile", question_count=5,
            allowed_types=("single_choice",),
        )
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="practice", difficulty="extreme", question_count=5,
            allowed_types=("single_choice",),
        )


def test_questionnaire_request_rejects_non_positive_question_count():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="practice", difficulty="facile", question_count=0,
            allowed_types=("single_choice",),
        )


def test_questionnaire_request_rejects_empty_or_unknown_allowed_types():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="practice", difficulty="facile", question_count=5,
            allowed_types=(),
        )
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="practice", difficulty="facile", question_count=5,
            allowed_types=("not-a-type",),
        )


def test_questionnaire_request_rejects_non_positive_total_points():
    with pytest.raises(QuestionnaireValidationError):
        QuestionnaireRequest(
            contexts=(CONTEXT,), mode="exam", difficulty="facile", question_count=5,
            allowed_types=("single_choice",), total_points=0,
        )


def test_questionnaire_request_accepts_multiple_contexts():
    other = get_context("ampcr-mc02")
    request = QuestionnaireRequest(
        contexts=(CONTEXT, other), mode="exam", difficulty="moyen", question_count=10,
        allowed_types=("single_choice", "long_answer"), total_points=20,
    )
    assert len(request.contexts) == 2

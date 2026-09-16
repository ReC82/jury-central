"""Tests de la correction locale et déterministe (ticket #23) : chaque type déterministe
doit être corrigé sans aucun appel IA, gérer correct/incorrect/malformé sans exception."""

import pytest

from app.ai.local_correction import correct_locally, requires_ai_correction
from app.ai.schemas import QuestionnaireQuestion


def test_single_choice_correct_and_incorrect():
    question = QuestionnaireQuestion(
        question_id="q1", type="single_choice", prompt="?", points_max=2,
        choices=["Oui", "Non"], correct_indexes=[0],
    )
    assert correct_locally(question, "0").correct is True
    assert correct_locally(question, "0").points_awarded == 2
    assert correct_locally(question, "1").correct is False
    assert correct_locally(question, "1").points_awarded == 0
    assert correct_locally(question, "not-a-number").correct is False


def test_true_false():
    question = QuestionnaireQuestion(
        question_id="q2", type="true_false", prompt="?", points_max=1,
        choices=["Vrai", "Faux"], correct_indexes=[1],
    )
    assert correct_locally(question, 1).correct is True
    assert correct_locally(question, 0).correct is False


def test_multiple_choice_exact_set_match_required():
    question = QuestionnaireQuestion(
        question_id="q3", type="multiple_choice", prompt="?", points_max=3,
        choices=["A", "B", "C"], correct_indexes=[0, 2],
    )
    assert correct_locally(question, [0, 2]).correct is True
    assert correct_locally(question, [2, 0]).correct is True  # ordre indifférent
    assert correct_locally(question, [0]).correct is False  # incomplet
    assert correct_locally(question, [0, 1, 2]).correct is False  # en trop
    assert correct_locally(question, "not-a-list").correct is False
    assert correct_locally(question, ["a", "b"]).correct is False


def test_ordering_correct_incorrect_and_malformed():
    question = QuestionnaireQuestion(
        question_id="q4", type="ordering", prompt="?", points_max=2,
        order_items=["A", "B", "C"], correct_order=[2, 0, 1],
    )
    assert correct_locally(question, [2, 0, 1]).correct is True
    assert correct_locally(question, [0, 1, 2]).correct is False
    assert correct_locally(question, [0, 0, 1]).correct is False  # doublon, pas permutation
    assert correct_locally(question, [0, 1]).correct is False  # longueur incorrecte
    assert correct_locally(question, "not-a-list").correct is False


def test_classification_correct_incomplete_and_wrong_type():
    question = QuestionnaireQuestion(
        question_id="q5", type="classification", prompt="?", points_max=2,
        categories=["Matériel", "Logiciel"], elements=["CPU", "Navigateur"],
        correct_categories=[0, 1],
    )
    assert correct_locally(question, [0, 1]).correct is True
    assert correct_locally(question, [1, 1]).correct is False
    assert correct_locally(question, [0]).correct is False
    assert correct_locally(question, None).correct is False


def test_matching_correct_and_incorrect():
    question = QuestionnaireQuestion(
        question_id="q6", type="matching", prompt="?", points_max=2,
        pairs_left=["Gauche A", "Gauche B"], pairs_right=["Droite A", "Droite B"],
        correct_pairs=[0, 1],
    )
    assert correct_locally(question, [0, 1]).correct is True
    assert correct_locally(question, [1, 0]).correct is False


def test_numeric_within_and_outside_tolerance():
    question = QuestionnaireQuestion(
        question_id="q7", type="numeric", prompt="2+2 ?", points_max=1,
        numeric_answer=4, numeric_tolerance=0.5,
    )
    assert correct_locally(question, "4").correct is True
    assert correct_locally(question, "4.4").correct is True
    assert correct_locally(question, 4).correct is True
    assert correct_locally(question, "4,4").correct is True  # virgule décimale acceptée
    assert correct_locally(question, "4.6").correct is False
    assert correct_locally(question, "pas un nombre").correct is False
    assert correct_locally(question, None).correct is False


def test_numeric_exact_tolerance_zero():
    question = QuestionnaireQuestion(
        question_id="q8", type="numeric", prompt="1/3 ?", points_max=1,
        numeric_answer=0.3333333333333333, numeric_tolerance=0,
    )
    # Tolérance nulle : seule l'égalité fraction-exacte compte (pas d'approximation).
    assert correct_locally(question, "1/3").correct is False  # 1/3 exact != flottant tronqué


def test_fill_blank_normalized_match():
    question = QuestionnaireQuestion(
        question_id="q9", type="fill_blank", prompt="La ___ vive.", points_max=1,
        accepted_answers=["mémoire", "RAM"],
    )
    assert correct_locally(question, "Mémoire").correct is True
    assert correct_locally(question, "  ram  ").correct is True
    assert correct_locally(question, "disque").correct is False
    assert correct_locally(question, "").correct is False


def test_short_answer_and_vocabulary_local_when_accepted_answers_present():
    for question_type in ("short_answer", "vocabulary"):
        question = QuestionnaireQuestion(
            question_id="q10", type=question_type, prompt="?", points_max=1,
            accepted_answers=["RAM"],
        )
        assert requires_ai_correction(question) is False
        assert correct_locally(question, "ram").correct is True
        assert correct_locally(question, "autre chose").correct is False


def test_correct_locally_raises_for_semantic_question():
    question = QuestionnaireQuestion(
        question_id="q11", type="long_answer", prompt="Explique.", points_max=5,
        rubric="grille",
    )
    with pytest.raises(ValueError):
        correct_locally(question, "une réponse")


def test_expected_answer_display_never_empty_for_deterministic_types():
    """Sert de garde-fou : la réponse attendue affichée après correction ne doit jamais
    être vide pour un type déterministe correctement configuré."""
    questions = [
        QuestionnaireQuestion(
            question_id="a", type="single_choice", prompt="?", points_max=1,
            choices=["X", "Y"], correct_indexes=[1],
        ),
        QuestionnaireQuestion(
            question_id="b", type="ordering", prompt="?", points_max=1,
            order_items=["X", "Y"], correct_order=[1, 0],
        ),
        QuestionnaireQuestion(
            question_id="c", type="numeric", prompt="?", points_max=1,
            numeric_answer=42, numeric_tolerance=0,
        ),
    ]
    for question in questions:
        correction = correct_locally(question, None)
        assert correction.expected_answer

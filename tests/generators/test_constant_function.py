from fractions import Fraction

from generators.exercise_types import InteractiveExercise
from generators.maths.constant_function import generate


def test_generate_returns_a_value_table_exercise():
    exercise = generate(difficulty=1, seed=1)
    assert isinstance(exercise, InteractiveExercise)
    assert exercise.type == "value_table"
    assert exercise.question
    assert exercise.hint


def test_generate_table_shape():
    exercise = generate(difficulty=1, seed=1)
    assert len(exercise.data["columns"]) == 3
    assert len(exercise.data["rows"]) == 1
    row = exercise.data["rows"][0]
    assert row["label"] == "f(x)"
    assert row["editable"] == [True, True, True]


def test_generate_answer_is_same_value_for_every_column():
    """La signature d'une fonction constante : la même valeur p pour tout x."""
    exercise = generate(difficulty=1, seed=1)
    cells = exercise.answer["cells"]
    assert len(cells) == 3
    assert len(set(cells)) == 1


def test_generate_is_deterministic_with_seed():
    first = generate(difficulty=2, seed=123)
    second = generate(difficulty=2, seed=123)
    assert first.question == second.question
    assert first.data == second.data
    assert first.answer == second.answer


def test_generate_without_seed_varies():
    questions = {generate(difficulty=1).question for _ in range(30)}
    assert len(questions) > 1


def test_difficulty_1_uses_small_positive_integers():
    for seed in range(100):
        exercise = generate(difficulty=1, seed=seed)
        p = Fraction(exercise.answer["cells"][0])
        assert p.denominator == 1
        assert 1 <= p.numerator <= 10


def test_difficulty_3_can_produce_fractions():
    denominators = set()
    for seed in range(100):
        exercise = generate(difficulty=3, seed=seed)
        p = Fraction(exercise.answer["cells"][0])
        denominators.add(p.denominator)
    assert denominators - {1}, "au moins un dénominateur non trivial attendu au niveau 3"


def test_difficulty_is_clamped_to_valid_range():
    assert generate(difficulty=0, seed=1).difficulty == 1
    assert generate(difficulty=99, seed=1).difficulty == 3


def test_public_dict_never_contains_answer():
    exercise = generate(difficulty=1, seed=1)
    assert "answer" not in exercise.to_public_dict()
    assert "answer" not in exercise.to_public_json()

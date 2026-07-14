from fractions import Fraction

import pytest

from generators.maths.constant_function import generate


def test_generate_returns_valid_exercise():
    exercise = generate(difficulty=1, seed=1)
    assert exercise.statement
    assert isinstance(exercise.answer, Fraction)
    assert exercise.hint


def test_generate_is_deterministic_with_seed():
    first = generate(difficulty=2, seed=123)
    second = generate(difficulty=2, seed=123)
    assert first.statement == second.statement
    assert first.answer == second.answer


def test_generate_without_seed_varies():
    statements = {generate(difficulty=1).statement for _ in range(30)}
    assert len(statements) > 1


@pytest.mark.parametrize("difficulty", [1, 2, 3])
def test_all_task_types_eventually_appear(difficulty):
    task_types = {generate(difficulty=difficulty, seed=s).metadata["task_type"] for s in range(50)}
    assert task_types == {"image", "table", "find_p", "match"}


def test_difficulty_1_uses_small_positive_integers():
    for seed in range(100):
        exercise = generate(difficulty=1, seed=seed)
        assert exercise.answer.denominator == 1
        assert 1 <= exercise.answer.numerator <= 10


def test_difficulty_3_can_produce_fractions():
    denominators = {generate(difficulty=3, seed=s).answer.denominator for s in range(100)}
    assert denominators - {1}, "au moins un dénominateur non trivial attendu au niveau 3"


def test_answer_matches_p_in_metadata():
    for seed in range(100):
        for difficulty in (1, 2, 3):
            exercise = generate(difficulty=difficulty, seed=seed)
            assert exercise.answer == exercise.metadata["p"]


def test_difficulty_is_clamped_to_valid_range():
    assert generate(difficulty=0, seed=1).difficulty == 1
    assert generate(difficulty=99, seed=1).difficulty == 3

from fractions import Fraction

import pytest

from generators.maths.equations import generate


def test_generate_returns_valid_exercise():
    exercise = generate(difficulty=1, seed=42)
    assert exercise.statement
    assert isinstance(exercise.answer, Fraction)
    assert exercise.difficulty == 1
    assert exercise.seed == 42
    assert len(exercise.solution_steps) == 3


def test_generate_is_deterministic_with_seed():
    first = generate(difficulty=2, seed=123)
    second = generate(difficulty=2, seed=123)
    assert first.statement == second.statement
    assert first.answer == second.answer


def test_generate_without_seed_varies():
    statements = {generate(difficulty=1).statement for _ in range(20)}
    assert len(statements) > 1


@pytest.mark.parametrize("difficulty", [1, 2])
def test_low_difficulty_always_has_integer_answer(difficulty):
    for seed in range(100):
        exercise = generate(difficulty=difficulty, seed=seed)
        assert exercise.answer.denominator == 1


def test_coefficient_a_is_never_zero():
    for seed in range(200):
        for difficulty in (1, 2, 3):
            exercise = generate(difficulty=difficulty, seed=seed)
            assert exercise.metadata["a"] != 0


def test_answer_actually_solves_the_equation():
    for seed in range(200):
        for difficulty in (1, 2, 3):
            exercise = generate(difficulty=difficulty, seed=seed)
            a, b, c = exercise.metadata["a"], exercise.metadata["b"], exercise.metadata["c"]
            assert a * exercise.answer + b == c


def test_difficulty_is_clamped_to_valid_range():
    assert generate(difficulty=0, seed=1).difficulty == 1
    assert generate(difficulty=99, seed=1).difficulty == 3

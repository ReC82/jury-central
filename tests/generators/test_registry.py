import pytest

from generators.registry import available_generators, get_generator


def test_linear_equation_is_registered():
    assert "maths.equations.linear_equation" in available_generators()


def test_get_generator_returns_callable():
    generator = get_generator("maths.equations.linear_equation")
    exercise = generator(difficulty=1, seed=1)
    assert exercise.statement


def test_get_generator_raises_on_unknown_id():
    with pytest.raises(KeyError):
        get_generator("unknown.generator")

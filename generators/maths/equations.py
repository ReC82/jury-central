import random
from fractions import Fraction

import sympy as sp

from generators.base import GeneratedExercise

_X = sp.symbols("x")


def _format_term(a: int) -> str:
    if a == 1:
        return "x"
    if a == -1:
        return "-x"
    return f"{a}x"


def _format_equation(a: int, b: int, c: int) -> str:
    left = _format_term(a)
    if b > 0:
        left += f" + {b}"
    elif b < 0:
        left += f" - {abs(b)}"
    return f"{left} = {c}"


def _random_nonzero(rng: random.Random, low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = rng.randint(low, high)
    return value


def generate(difficulty: int, seed: int | None = None) -> GeneratedExercise:
    """Génère une équation du premier degré ax + b = c avec une solution unique.

    a est toujours différent de 0 : l'équation admet donc toujours exactement
    une solution (jamais impossible, jamais une identité).
    """
    difficulty = max(1, min(int(difficulty), 3))
    rng_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
    rng = random.Random(rng_seed)

    require_integer = difficulty < 3

    if require_integer:
        b_bound = 10 if difficulty == 1 else 20
        x_bound = 10 if difficulty == 1 else 20

        a = rng.randint(1, 9) if difficulty == 1 else _random_nonzero(rng, -9, 9)
        b = rng.randint(-b_bound, b_bound)
        x_value = rng.randint(-x_bound, x_bound)
        c = a * x_value + b
    else:
        a = _random_nonzero(rng, -12, 12)
        b = rng.randint(-20, 20)
        c = rng.randint(-20, 20)

    equation = sp.Eq(a * _X + b, c)
    solution = sp.solve(equation, _X)[0]
    answer = Fraction(int(solution.p), int(solution.q))

    if require_integer and answer.denominator != 1:
        # Filet de sécurité : ne devrait jamais se produire vu la construction ci-dessus.
        return generate(difficulty, rng.randint(0, 2**31 - 1))

    statement = f"Résous l'équation suivante : {_format_equation(a, b, c)}"
    solution_steps = [
        _format_equation(a, b, c),
        f"{_format_term(a)} = {c - b}",
        f"x = {answer}",
    ]

    return GeneratedExercise(
        statement=statement,
        answer=answer,
        difficulty=difficulty,
        seed=rng_seed,
        solution_steps=solution_steps,
        metadata={"a": a, "b": b, "c": c},
    )

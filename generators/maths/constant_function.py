import random
from fractions import Fraction

from generators.exercise_types import InteractiveExercise
from generators.value_table import ValueTableRow, build_value_table_exercise

_HINT = "Une fonction constante renvoie toujours la même valeur, peu importe x."
_COLUMN_COUNT = 3


def _random_p(rng: random.Random, difficulty: int) -> Fraction:
    if difficulty <= 1:
        return Fraction(rng.randint(1, 10))
    if difficulty == 2:
        return Fraction(rng.randint(-15, 15))
    denominator = rng.choice([1, 2, 4, 5])
    numerator = rng.randint(-20, 20)
    return Fraction(numerator, denominator)


def generate(difficulty: int, seed: int | None = None) -> InteractiveExercise:
    """Génère un exercice « tableau de valeurs » sur la fonction constante f(x) = p.

    Retourne un exercice interactif `value_table` (voir docs/EXERCISE_TYPES.md) : une ligne
    f(x), une colonne par valeur de x, toutes les cellules à compléter avec la même valeur
    p — illustre directement ce qui définit une fonction constante (le résultat ne dépend
    jamais de x). Aucun cas ambigu à éviter : une fonction constante est toujours bien
    définie pour n'importe quelle valeur de p.
    """
    difficulty = max(1, min(int(difficulty), 3))
    rng_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
    rng = random.Random(rng_seed)

    p = _random_p(rng, difficulty)
    columns = sorted(rng.sample(range(-10, 11), _COLUMN_COUNT))

    return build_value_table_exercise(
        question=f"Complète le tableau de valeurs de la fonction constante f(x) = {p}.",
        columns=columns,
        rows=[ValueTableRow(label="f(x)", editable=[True] * _COLUMN_COUNT)],
        answer_cells=[str(p)] * _COLUMN_COUNT,
        hint=_HINT,
        explanation=f"Quel que soit x, f(x) = {p} : c'est la définition d'une fonction constante.",
        difficulty=difficulty,
        seed=rng_seed,
    )

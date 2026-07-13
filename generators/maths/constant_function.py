import random
from fractions import Fraction

from generators.base import GeneratedExercise

_TASK_TYPES = ["image", "table", "find_p", "match"]
_HINT = "Une fonction constante renvoie toujours la même valeur, peu importe x."


def _random_p(rng: random.Random, difficulty: int) -> Fraction:
    if difficulty <= 1:
        return Fraction(rng.randint(1, 10))
    if difficulty == 2:
        return Fraction(rng.randint(-15, 15))
    denominator = rng.choice([1, 2, 4, 5])
    numerator = rng.randint(-20, 20)
    return Fraction(numerator, denominator)


def generate(difficulty: int, seed: int | None = None) -> GeneratedExercise:
    """Génère un exercice sur la fonction constante f(x) = p.

    Aucun cas ambigu à éviter ici : une fonction constante est toujours bien
    définie pour n'importe quelle valeur de p (contrairement à ax + b = c).
    """
    difficulty = max(1, min(int(difficulty), 3))
    rng_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
    rng = random.Random(rng_seed)

    task_type = rng.choice(_TASK_TYPES)
    p = _random_p(rng, difficulty)

    if task_type == "image":
        x = rng.randint(-10, 10)
        statement = f"Soit la fonction constante f(x) = {p}. Calcule f({x})."
        solution_steps = [
            f"f(x) = {p} pour tout x (c'est une fonction constante).",
            f"f({x}) = {p}",
        ]
    elif task_type == "table":
        x_values = rng.sample(range(-10, 11), 3)
        x_list = ", ".join(str(x) for x in x_values)
        statement = (
            f"Complète le tableau de valeurs de f(x) = {p} pour x = {x_list}, "
            "puis donne la valeur commune de f(x)."
        )
        solution_steps = [
            f"Quel que soit x, f(x) = {p}.",
            f"f({x_values[0]}) = f({x_values[1]}) = f({x_values[2]}) = {p}",
        ]
    elif task_type == "find_p":
        x0 = rng.randint(-10, 10)
        statement = (
            f"Le graphique d'une fonction constante passe par le point ({x0}, {p}). "
            "Quelle est la valeur de p dans f(x) = p ?"
        )
        solution_steps = [
            "Pour une fonction constante, f(x) = p pour tout x.",
            f"Le point ({x0}, {p}) donne directement p = {p}.",
        ]
    else:
        statement = (
            f"Un graphique représente une droite horizontale d'équation y = {p}. "
            "Écris la valeur de p telle que ce graphique corresponde à f(x) = p."
        )
        solution_steps = [f"Une droite horizontale y = {p} correspond à f(x) = p avec p = {p}."]

    return GeneratedExercise(
        statement=statement,
        answer=p,
        difficulty=difficulty,
        seed=rng_seed,
        solution_steps=solution_steps,
        metadata={"p": p, "task_type": task_type},
        hint=_HINT,
    )

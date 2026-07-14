from generators.base import ExerciseGenerator
from generators.maths import constant_function, equations

REGISTRY: dict[str, ExerciseGenerator] = {
    "maths.equations.linear_equation": equations.generate,
    "maths.functions.constant_function": constant_function.generate,
}


def get_generator(generator_id: str) -> ExerciseGenerator:
    try:
        return REGISTRY[generator_id]
    except KeyError as exc:
        raise KeyError(f"Générateur inconnu : {generator_id}") from exc


def available_generators() -> list[str]:
    return sorted(REGISTRY)

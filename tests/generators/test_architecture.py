"""Tests de contrat : valident que TOUT générateur enregistré dans le registre
respecte l'interface commune, sans avoir besoin d'un test dédié par générateur.
Un futur générateur ajouté à generators/registry.py est automatiquement couvert.

Un générateur retourne soit un `GeneratedExercise` (ancien moteur), soit un
`InteractiveExercise` (nouveau moteur, voir docs/EXERCISE_TYPES.md) : ces tests vérifient
les deux formes plutôt que d'en imposer une seule.
"""

import pytest

from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise
from generators.registry import available_generators, get_generator


def test_registry_is_not_empty():
    assert available_generators()


@pytest.mark.parametrize("generator_id", available_generators())
def test_generator_returns_a_known_exercise_type(generator_id):
    generator = get_generator(generator_id)
    exercise = generator(difficulty=1, seed=1)
    assert isinstance(exercise, (GeneratedExercise, InteractiveExercise))
    assert exercise.difficulty == 1
    assert exercise.seed == 1

    if isinstance(exercise, GeneratedExercise):
        assert exercise.statement
        assert exercise.answer is not None
    else:
        assert exercise.question
        assert exercise.data
        assert exercise.answer
        assert "answer" not in exercise.to_public_dict()


@pytest.mark.parametrize("generator_id", available_generators())
def test_generator_is_deterministic_given_a_seed(generator_id):
    generator = get_generator(generator_id)
    first = generator(difficulty=1, seed=42)
    second = generator(difficulty=1, seed=42)
    if isinstance(first, GeneratedExercise):
        assert first.statement == second.statement
        assert first.answer == second.answer
    else:
        assert first.question == second.question
        assert first.data == second.data
        assert first.answer == second.answer


@pytest.mark.parametrize("generator_id", available_generators())
def test_generator_id_follows_domain_module_name_convention(generator_id):
    parts = generator_id.split(".")
    assert len(parts) == 3, "attendu : domaine.module.nom (ex. maths.equations.linear_equation)"

import pytest

from app.exercise_blocks import (
    ExerciseBlockConfig,
    exercise_to_dict,
    exercise_to_public_dict,
    generate_exercises,
)
from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise
from generators.registry import get_generator


def test_config_round_trips_through_json():
    config = ExerciseBlockConfig(
        generator="maths.equations.linear_equation",
        difficulty=2,
        count=3,
        tags=["algèbre", "premier degré"],
    )
    restored = ExerciseBlockConfig.from_json(config.to_json())
    assert restored == config


def test_config_from_empty_content_uses_defaults():
    config = ExerciseBlockConfig.from_json("")
    assert config.generator == ""
    assert config.difficulty == 1
    assert config.count == 1
    assert config.tags == []


def test_config_from_invalid_json_uses_defaults():
    config = ExerciseBlockConfig.from_json("not json")
    assert config.generator == ""
    assert config.count == 1


def test_generate_exercises_returns_requested_count():
    config = ExerciseBlockConfig(generator="maths.equations.linear_equation", difficulty=1, count=3)
    exercises = generate_exercises(config)
    assert len(exercises) == 3
    for exercise in exercises:
        assert isinstance(exercise, GeneratedExercise)
        assert exercise.statement
        assert exercise.seed is not None


def test_generate_exercises_returns_raw_objects_not_dicts():
    """generate_exercises() ne convertit plus en dict : c'est à l'appelant (rendu de
    leçon) de choisir la représentation selon le type retourné (GeneratedExercise vs
    InteractiveExercise) — voir docs/EXERCISE_TYPES.md."""
    config = ExerciseBlockConfig(generator="maths.functions.constant_function", difficulty=1, count=2)
    exercises = generate_exercises(config)
    assert len(exercises) == 2
    for exercise in exercises:
        assert isinstance(exercise, InteractiveExercise)
        assert exercise.type == "value_table"


def test_generate_exercises_never_exposes_the_answer():
    config = ExerciseBlockConfig(generator="maths.equations.linear_equation", difficulty=1, count=1)
    exercise = generate_exercises(config)[0]
    public = exercise_to_public_dict(exercise)
    assert "answer_value" not in public
    assert "answer_display" not in public
    assert "solution_steps" not in public


def test_generate_exercises_raises_for_unknown_generator():
    config = ExerciseBlockConfig(generator="unknown.generator")
    with pytest.raises(KeyError):
        generate_exercises(config)


def test_exercise_to_dict_includes_full_answer_for_admin_debug():
    generator = get_generator("maths.equations.linear_equation")
    exercise = generator(difficulty=1, seed=1)
    data = exercise_to_dict(exercise)
    assert "answer_value" in data
    assert "answer_display" in data
    assert "solution_steps" in data

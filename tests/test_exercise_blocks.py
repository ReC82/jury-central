import pytest

from app.exercise_blocks import ExerciseBlockConfig, generate_exercises


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
        assert exercise["statement"]
        assert "answer_value" in exercise
        assert "answer_display" in exercise


def test_generate_exercises_raises_for_unknown_generator():
    config = ExerciseBlockConfig(generator="unknown.generator")
    with pytest.raises(KeyError):
        generate_exercises(config)

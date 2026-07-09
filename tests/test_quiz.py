from app.quiz import QuizConfig


def test_config_round_trips_through_json():
    config = QuizConfig(
        question="Combien font 2 + 2 ?",
        choices=["3", "4", "5"],
        correct_index=1,
        explanation="2 + 2 = 4",
    )
    restored = QuizConfig.from_json(config.to_json())
    assert restored == config


def test_config_from_empty_content_uses_defaults():
    config = QuizConfig.from_json("")
    assert config.question == ""
    assert config.choices == []
    assert config.correct_index == 0
    assert config.explanation == ""


def test_config_from_invalid_json_uses_defaults():
    config = QuizConfig.from_json("not json")
    assert config.question == ""
    assert config.choices == []

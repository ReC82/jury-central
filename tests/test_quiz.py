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


def test_config_defaults_are_backward_compatible():
    config = QuizConfig.from_json("")
    assert config.answer_type == "choice"
    assert config.correct_value == ""
    assert config.group == ""
    assert config.order_in_group == 0


def test_round_trip_preserves_grouping_and_numeric_fields():
    config = QuizConfig(
        question="Combien font 2 + 2 ?",
        answer_type="numeric",
        correct_value="4",
        explanation="2 + 2 = 4",
        group="chiffres",
        order_in_group=3,
    )
    restored = QuizConfig.from_json(config.to_json())
    assert restored == config


def test_check_choice_mode_correct_and_incorrect():
    config = QuizConfig(question="Q", choices=["a", "b", "c"], correct_index=1)
    assert config.check("1") is True
    assert config.check("0") is False
    assert config.check("abc") is False


def test_check_numeric_mode_accepts_normalized_formats():
    config = QuizConfig(question="Q", answer_type="numeric", correct_value="1.75")
    assert config.check("1,75") is True
    assert config.check("7/4") is True
    assert config.check("2") is False


def test_to_public_dict_never_exposes_the_answer():
    config = QuizConfig(
        question="Q", choices=["a", "b"], correct_index=1, correct_value="secret"
    )
    public = config.to_public_dict(block_id=42)
    assert public == {
        "block_id": 42,
        "question": "Q",
        "question_html": "<p>Q</p>",
        "choices": ["a", "b"],
        "answer_type": "choice",
    }
    assert "correct_index" not in public
    assert "correct_value" not in public
    assert "secret" not in str(public)


def test_to_public_dict_renders_question_as_markdown():
    """Une question de quiz peut contenir un vrai tableau Markdown plutôt qu'une phrase qui
    le décrit — voir docs/UI_GUIDELINES.md (renderer de contenu riche, VS003.1)."""
    config = QuizConfig(
        question="| $x$ | -1 | 0 | 1 |\n|---|---|---|---|\n| $f(x)$ | 4 | 4 | 4 |",
        choices=["a", "b"],
        correct_index=0,
    )
    public = config.to_public_dict(block_id=1)
    assert "<table>" in public["question_html"]
    assert "<th>" in public["question_html"] or "<td>" in public["question_html"]

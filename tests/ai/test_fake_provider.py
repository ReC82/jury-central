from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider

CONTEXT = get_context("ampcr-mc01")


def test_fake_provider_generate_is_deterministic_and_traced():
    provider = FakeAIProvider()
    exercise = provider.generate_exercise(CONTEXT, "difficile")

    assert exercise.difficulty == "difficile"
    assert exercise.statement
    assert provider.generate_calls == [(CONTEXT, "difficile")]


def test_fake_provider_correct_returns_structured_result():
    provider = FakeAIProvider()
    result = provider.correct_answer(
        CONTEXT,
        exercise_statement="Explique le rôle du CPU.",
        exercise_type="réponse rédigée",
        difficulty="moyen",
        candidate_answer="Le CPU exécute les instructions.",
    )

    assert result.appreciation
    assert result.correct_points
    assert result.errors == []
    assert result.expected_answer_explained
    assert provider.correct_calls[0][0] == CONTEXT.course_key

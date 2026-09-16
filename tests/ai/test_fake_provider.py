from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import QUESTION_TYPES, QuestionnaireRequest

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


def test_fake_provider_generate_questionnaire_produces_requested_count_and_types():
    provider = FakeAIProvider()
    request = QuestionnaireRequest(
        contexts=(CONTEXT,), mode="exam", difficulty="moyen", question_count=len(QUESTION_TYPES),
        allowed_types=tuple(QUESTION_TYPES), total_points=20,
    )
    questionnaire = provider.generate_questionnaire(request)

    assert len(questionnaire.questions) == len(QUESTION_TYPES)
    assert {q.type for q in questionnaire.questions} == set(QUESTION_TYPES)
    assert provider.questionnaire_calls == [request]


def test_fake_provider_correct_semantic_batch_is_traced_and_deterministic():
    provider = FakeAIProvider()
    request = QuestionnaireRequest(
        contexts=(CONTEXT,), mode="practice", difficulty="facile", question_count=1,
        allowed_types=("long_answer",),
    )
    questionnaire = provider.generate_questionnaire(request)
    question = questionnaire.questions[0]

    results = provider.correct_semantic_batch(
        [question], {question.question_id: "une réponse de test"}, "standard", [CONTEXT]
    )

    assert question.question_id in results
    assert provider.semantic_calls == [((question.question_id,), "standard")]

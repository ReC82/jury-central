"""Tests unitaires du pont éditorial <-> IA (ticket #29, `app/editorial_ai_correction.py`)
— aucun appel réseau réel, `FakeAIProvider` uniquement."""

from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import QuestionCorrection
from app.editorial_ai_correction import (
    correct_editorial_item_with_ai,
    editorial_item_to_question,
)
from app.editorial_exercise import EditorialExerciseItem

CONTEXT = get_context("ampcr-mc01")


def _long_answer_item(**overrides):
    defaults = {
        "exercise_id": "mc01-ex3",
        "type": "long_answer",
        "prompt": "Explique pourquoi.",
        "points": 2.0,
        "explanation": "Doit mentionner la compatibilité socket/chipset.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


def test_editorial_item_to_question_maps_fields_correctly():
    item = _long_answer_item()
    question = editorial_item_to_question(item)

    assert question.question_id == item.exercise_id
    assert question.type == item.type
    assert question.prompt == item.prompt
    assert question.points_max == item.points
    # explanation sert de rubric — jamais dupliqué sous un nouveau champ d'auteurisation.
    assert question.rubric == item.explanation


def test_correct_editorial_item_with_ai_calls_provider_once():
    provider = FakeAIProvider()
    item = _long_answer_item()

    correction = correct_editorial_item_with_ai(provider, item, "une réponse", CONTEXT)

    assert correction.exercise_id == "mc01-ex3"
    assert provider.semantic_calls == [(("mc01-ex3",), "standard")]
    assert correction.points_max == 2.0
    assert 0 <= correction.points_awarded <= 2.0


def test_correct_editorial_item_with_ai_respects_severity_parameter():
    provider = FakeAIProvider()
    item = _long_answer_item(points=10.0)

    lenient = correct_editorial_item_with_ai(provider, item, "x", CONTEXT, severity="lenient")
    strict = correct_editorial_item_with_ai(provider, item, "x", CONTEXT, severity="strict")

    assert lenient.points_awarded > strict.points_awarded
    assert provider.semantic_calls[-2][1] == "lenient"
    assert provider.semantic_calls[-1][1] == "strict"


def test_correct_editorial_item_with_ai_never_leaks_points_max_from_provider():
    class _OverclaimingProvider(FakeAIProvider):
        def correct_semantic_batch(self, questions, answers, severity, contexts):
            return {
                q.question_id: QuestionCorrection(
                    question_id=q.question_id, points_awarded=999, points_max=999,
                    correct=True,
                )
                for q in questions
            }

    item = _long_answer_item(points=3.0)
    correction = correct_editorial_item_with_ai(
        _OverclaimingProvider(), item, "x", CONTEXT
    )
    assert correction.points_max == 3.0
    assert correction.points_awarded == 3.0  # borné à points_max, jamais 999


def test_correct_editorial_item_with_ai_handles_missing_result_without_crashing():
    class _SilentProvider(FakeAIProvider):
        def correct_semantic_batch(self, questions, answers, severity, contexts):
            return {}

    item = _long_answer_item(points=5.0)
    correction = correct_editorial_item_with_ai(_SilentProvider(), item, "x", CONTEXT)
    assert correction.points_awarded == 0.0
    assert correction.points_max == 5.0
    assert correction.correct is False

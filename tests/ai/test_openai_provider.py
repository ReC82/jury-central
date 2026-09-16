"""Tests du fournisseur IA réel — aucun appel réseau : httpx.post est intercepté (voir
complément IA du ticket #10, « prévoir tests avec provider mock/fake, sans consommation
réelle d'API dans pytest »)."""

import json

import httpx
import pytest

from app.ai.context import get_context
from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AINotConfiguredError, AIResponseError, AITimeoutError
from app.ai.schemas import QuestionnaireQuestion, QuestionnaireRequest

CONTEXT = get_context("ampcr-mc01")


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def _openai_envelope(content: dict) -> dict:
    return {"choices": [{"message": {"content": json.dumps(content, ensure_ascii=False)}}]}


def test_missing_api_key_raises_not_configured():
    with pytest.raises(AINotConfiguredError):
        OpenAIProvider(api_key="", model="gpt-4o-mini", timeout_seconds=5)


def test_generate_exercise_success(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = json
        captured["timeout"] = timeout
        return _FakeResponse(
            200, _openai_envelope({"exercise_type": "calcul", "statement": "Calcule 2+2."})
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    exercise = provider.generate_exercise(CONTEXT, "facile")

    assert exercise.exercise_type == "calcul"
    assert exercise.statement == "Calcule 2+2."
    assert exercise.difficulty == "facile"

    # La clé API est bien transmise en en-tête HTTP, jamais ailleurs.
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["payload"]["response_format"]["type"] == "json_schema"
    assert captured["payload"]["response_format"]["json_schema"]["strict"] is True
    assert captured["timeout"] == 5


def test_generate_exercise_never_leaks_api_key_in_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(500, {})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-super-secret", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")

    assert "sk-super-secret" not in str(excinfo.value)


def test_timeout_raises_ai_timeout_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.TimeoutException("boom")

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AITimeoutError):
        provider.generate_exercise(CONTEXT, "facile")


def test_malformed_json_content_raises_response_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(200, {"choices": [{"message": {"content": "not json"}}]})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.generate_exercise(CONTEXT, "facile")


def test_correct_answer_success(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "appreciation": "Bonne réponse dans l'ensemble.",
                    "correct_points": ["Rôle du CPU bien identifié."],
                    "errors": ["Le lien avec la RAM n'est pas mentionné."],
                    "expected_answer_explained": "Le CPU exécute les instructions...",
                    "score": 1.5,
                    "max_score": 2,
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    result = provider.correct_answer(
        CONTEXT,
        exercise_statement="Explique le rôle du CPU.",
        exercise_type="réponse rédigée",
        difficulty="moyen",
        candidate_answer="Le CPU calcule des trucs.",
    )

    assert result.score == 1.5
    assert result.max_score == 2
    assert result.correct_points == ["Rôle du CPU bien identifié."]
    assert result.errors == ["Le lien avec la RAM n'est pas mentionné."]


# --- Contrat générique « questionnaire » (ticket #23) --------------------------------------


def _questionnaire_request(**overrides) -> QuestionnaireRequest:
    defaults = {
        "contexts": (CONTEXT,),
        "mode": "practice",
        "difficulty": "moyen",
        "question_count": 2,
        "allowed_types": ("single_choice", "long_answer"),
    }
    defaults.update(overrides)
    return QuestionnaireRequest(**defaults)


def test_generate_questionnaire_success(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "questions": [
                        {
                            "question_id": "q1",
                            "type": "single_choice",
                            "prompt": "La RAM est-elle volatile ?",
                            "points_max": 2,
                            "choices": ["Oui", "Non"],
                            "correct_indexes": [0],
                            "order_items": None,
                            "correct_order": None,
                            "categories": None,
                            "elements": None,
                            "correct_categories": None,
                            "pairs_left": None,
                            "pairs_right": None,
                            "correct_pairs": None,
                            "numeric_answer": None,
                            "numeric_tolerance": None,
                            "accepted_answers": None,
                            "rubric": None,
                            "explanation": "La RAM perd son contenu hors tension.",
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    questionnaire = provider.generate_questionnaire(_questionnaire_request())

    assert len(questionnaire.questions) == 1
    assert questionnaire.questions[0].type == "single_choice"
    assert questionnaire.questions[0].correct_indexes == [0]


def test_generate_questionnaire_empty_response_raises_response_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(200, _openai_envelope({"questions": []}))

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.generate_questionnaire(_questionnaire_request())


def test_generate_questionnaire_unknown_type_is_dropped_not_crashed(monkeypatch):
    """Défense en profondeur : si un type hors contrat passait malgré l'enum strict du
    schéma JSON, il est simplement ignoré (chargement tolérant), jamais une exception qui
    ferait tout échouer."""

    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "questions": [
                        {
                            "question_id": "bad",
                            "type": "not_a_real_type",
                            "prompt": "x",
                            "points_max": 1,
                            "choices": None,
                            "correct_indexes": None,
                            "order_items": None,
                            "correct_order": None,
                            "categories": None,
                            "elements": None,
                            "correct_categories": None,
                            "pairs_left": None,
                            "pairs_right": None,
                            "correct_pairs": None,
                            "numeric_answer": None,
                            "numeric_tolerance": None,
                            "accepted_answers": None,
                            "rubric": None,
                            "explanation": None,
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        # Aucune question exploitable après filtrage tolérant -> réponse invalide signalée.
        provider.generate_questionnaire(_questionnaire_request())


def test_generate_questionnaire_timeout_raises_ai_timeout_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.TimeoutException("boom")

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AITimeoutError):
        provider.generate_questionnaire(_questionnaire_request())


def _semantic_question(question_id="s1", points_max=10) -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id=question_id, type="long_answer", prompt="Explique le rôle du CPU.",
        points_max=points_max, rubric="doit mentionner l'exécution d'instructions",
    )


def test_correct_semantic_batch_success(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "corrections": [
                        {
                            "question_id": "s1",
                            "points_awarded": 7,
                            "correct": True,
                            "strengths": ["Rôle du CPU bien identifié."],
                            "errors": [],
                            "missing": ["Lien avec la RAM"],
                            "feedback": "Bonne réponse globalement.",
                            "expected_answer": "Le CPU exécute les instructions...",
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    results = provider.correct_semantic_batch(
        [_semantic_question()], {"s1": "Le CPU calcule."}, "standard", [CONTEXT]
    )

    assert results["s1"].points_awarded == 7
    assert results["s1"].points_max == 10  # vient de la question envoyée, pas de la réponse


def test_correct_semantic_batch_ignores_points_max_claimed_by_model(monkeypatch):
    """Même si la réponse contenait un `points_max` (elle ne le devrait jamais, absent du
    schéma), il ne serait de toute façon jamais lu : seul `points_max` de la question
    d'origine fait foi."""

    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "corrections": [
                        {
                            "question_id": "s1",
                            "points_awarded": 999,
                            "points_max": 999,
                            "correct": True,
                            "strengths": [],
                            "errors": [],
                            "missing": [],
                            "feedback": "",
                            "expected_answer": "",
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    results = provider.correct_semantic_batch(
        [_semantic_question(points_max=10)], {"s1": "x"}, "standard", [CONTEXT]
    )
    assert results["s1"].points_max == 10


def test_correct_semantic_batch_unknown_question_id_is_ignored(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200,
            _openai_envelope(
                {
                    "corrections": [
                        {
                            "question_id": "does-not-exist",
                            "points_awarded": 5,
                            "correct": True,
                            "strengths": [],
                            "errors": [],
                            "missing": [],
                            "feedback": "",
                            "expected_answer": "",
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    results = provider.correct_semantic_batch(
        [_semantic_question()], {"s1": "x"}, "standard", [CONTEXT]
    )
    assert results == {}


def test_correct_semantic_batch_provider_error_raises_ai_response_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(500, {})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.correct_semantic_batch([_semantic_question()], {"s1": "x"}, "standard", [CONTEXT])

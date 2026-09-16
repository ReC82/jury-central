"""Tests du fournisseur IA réel — aucun appel réseau : httpx.post est intercepté (voir
complément IA du ticket #10, « prévoir tests avec provider mock/fake, sans consommation
réelle d'API dans pytest »)."""

import json

import httpx
import pytest

from app.ai.context import get_context
from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AINotConfiguredError, AIResponseError, AITimeoutError

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

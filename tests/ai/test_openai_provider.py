"""Tests du fournisseur IA réel — aucun appel réseau : httpx.post est intercepté (voir
complément IA du ticket #10, « prévoir tests avec provider mock/fake, sans consommation
réelle d'API dans pytest »).

Ticket #31 : le fournisseur appelle désormais `/v1/responses` (Responses API), plus
`/v1/chat/completions` — `_openai_envelope` construit l'enveloppe `output[]` correspondante
(avec un item `reasoning` intercalé avant le `message`, comme observé avec les modèles de
raisonnement réels, pour vérifier que l'extraction ne dépend jamais d'un index fixe)."""

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
    """Enveloppe Responses API réaliste : un item `reasoning` (sans texte exploitable)
    précède le `message` — l'extraction doit chercher le bon item, jamais supposer que
    `output[0]` est le message."""
    return {
        "id": "resp_test",
        "object": "response",
        "model": "gpt-5.6-luna",
        "output": [
            {"id": "rs_1", "type": "reasoning", "content": [], "summary": []},
            {
                "id": "msg_1",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {"type": "output_text", "text": json.dumps(content, ensure_ascii=False)}
                ],
            },
        ],
    }


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
    # Ticket #31 : Responses API — /v1/responses, text.format (pas response_format).
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["payload"]["text"]["format"]["type"] == "json_schema"
    assert captured["payload"]["text"]["format"]["strict"] is True
    assert "response_format" not in captured["payload"]
    assert "messages" not in captured["payload"]
    # Jamais de `temperature` : rejetée (HTTP 400) par les modèles GPT-5 de raisonnement,
    # dont gpt-5.6-luna — voir le rapport de ticket #31.
    assert "temperature" not in captured["payload"]
    # instructions (système) et input (utilisateur) bien séparés au niveau racine.
    assert "générateur d'exercices" in captured["payload"]["instructions"]
    assert "carte mère" in captured["payload"]["input"]
    assert captured["timeout"] == 5


def test_generate_exercise_uses_configured_model_gpt_5_6_luna(monkeypatch):
    """Reproduit exactement le scénario du ticket #31 : OPENAI_MODEL=gpt-5.6-luna."""
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["payload"] = json
        return _FakeResponse(
            200, _openai_envelope({"exercise_type": "calcul", "statement": "Calcule 2+2."})
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-5.6-luna", timeout_seconds=5)
    exercise = provider.generate_exercise(CONTEXT, "moyen")

    assert exercise.statement == "Calcule 2+2."
    assert captured["payload"]["model"] == "gpt-5.6-luna"


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
        return _FakeResponse(
            200,
            {
                "output": [
                    {
                        "id": "msg_1",
                        "type": "message",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "not json"}],
                    }
                ]
            },
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.generate_exercise(CONTEXT, "facile")


def test_empty_output_array_raises_response_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(200, {"output": []})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.generate_exercise(CONTEXT, "facile")


def test_output_with_only_reasoning_item_raises_response_error(monkeypatch):
    """Aucun item `message` du tout (ex. le modèle n'a produit que du raisonnement, sans
    réponse finale) : ne doit jamais planter avec un IndexError/KeyError brut."""

    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            200, {"output": [{"id": "rs_1", "type": "reasoning", "content": [], "summary": []}]}
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError):
        provider.generate_exercise(CONTEXT, "facile")


def test_http_400_includes_openai_error_details_without_leaking_secrets(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            400,
            {
                "error": {
                    "type": "invalid_request_error",
                    "code": "unsupported_parameter",
                    "message": "Unsupported parameter: 'response_format'.",
                }
            },
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-super-secret", model="gpt-5.6-luna", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")

    message = str(excinfo.value)
    assert "400" in message
    assert "invalid_request_error" in message
    assert "unsupported_parameter" in message
    assert "response_format" in message  # message OpenAI repris, tronqué si besoin
    assert "sk-super-secret" not in message


def test_http_400_error_message_is_truncated_to_a_reasonable_length(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            400,
            {"error": {"type": "invalid_request_error", "message": "x" * 5000}},
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")

    assert len(str(excinfo.value)) < 500


def test_http_401_raises_clean_response_error_without_body(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(401, {})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-invalid", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")
    assert "401" in str(excinfo.value)
    assert "sk-invalid" not in str(excinfo.value)


def test_http_429_rate_limit_raises_clean_response_error(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            429, {"error": {"type": "rate_limit_error", "message": "Rate limit reached."}}
        )

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")
    assert "429" in str(excinfo.value)
    assert "rate_limit_error" in str(excinfo.value)


def test_error_response_with_unparseable_body_still_raises_clean_response_error(monkeypatch):
    class _BrokenBodyResponse(_FakeResponse):
        def json(self):
            raise ValueError("no body")

    def fake_post(url, headers=None, json=None, timeout=None):
        return _BrokenBodyResponse(500, {})

    monkeypatch.setattr("app.ai.openai_provider.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini", timeout_seconds=5)
    with pytest.raises(AIResponseError) as excinfo:
        provider.generate_exercise(CONTEXT, "facile")
    assert "500" in str(excinfo.value)


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

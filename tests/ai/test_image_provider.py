"""Tests du fournisseur de génération d'images — aucun appel réseau : `httpx.post` est
intercepté (même convention que `tests/ai/test_openai_provider.py`, ticket #108)."""

import base64
import json

import httpx
import pytest

from app.ai.image_provider import ImageProvider
from app.ai.provider import AINotConfiguredError, AIResponseError, AITimeoutError


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_missing_api_key_raises_not_configured():
    with pytest.raises(AINotConfiguredError):
        ImageProvider(api_key="", model="gpt-image-2.5-flare", timeout_seconds=30)


def test_generate_image_success(monkeypatch):
    captured = {}
    raw_bytes = b"\x89PNG\r\n\x1a\nfake-image-bytes"
    b64 = base64.b64encode(raw_bytes).decode("ascii")

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = json
        captured["timeout"] = timeout
        return _FakeResponse(200, {"data": [{"b64_json": b64}]})

    monkeypatch.setattr(httpx, "post", fake_post)

    provider = ImageProvider(api_key="sk-test", model="gpt-image-2.5-flare", timeout_seconds=30)
    result = provider.generate_image(prompt="a red circle", size="1024x1024", quality="low")

    assert result == raw_bytes
    assert captured["url"] == "https://api.openai.com/v1/images/generations"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert "sk-test" not in str(captured["payload"])  # la clé ne doit jamais fuiter dans le corps
    assert captured["payload"]["model"] == "gpt-image-2.5-flare"
    assert captured["payload"]["prompt"] == "a red circle"
    assert captured["payload"]["size"] == "1024x1024"
    assert captured["payload"]["quality"] == "low"
    assert captured["payload"]["n"] == 1


def test_generate_image_error_response_never_leaks_key(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            403,
            {
                "error": {
                    "type": "invalid_request_error",
                    "code": "organization_verification_required",
                    "message": "Your organization must be verified to use this model.",
                }
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = ImageProvider(api_key="sk-test", model="gpt-image-2.5-flare", timeout_seconds=30)

    with pytest.raises(AIResponseError) as exc_info:
        provider.generate_image(prompt="a red circle")

    message = str(exc_info.value)
    assert "sk-test" not in message
    assert "organization_verification_required" in message


def test_generate_image_timeout(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = ImageProvider(api_key="sk-test", model="gpt-image-2.5-flare", timeout_seconds=30)

    with pytest.raises(AITimeoutError):
        provider.generate_image(prompt="a red circle")


def test_generate_image_malformed_response(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(200, {"data": [{}]})  # pas de b64_json

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = ImageProvider(api_key="sk-test", model="gpt-image-2.5-flare", timeout_seconds=30)

    with pytest.raises(AIResponseError):
        provider.generate_image(prompt="a red circle")


def test_generate_image_invalid_base64(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(200, {"data": [{"b64_json": "not-valid-base64!!!"}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = ImageProvider(api_key="sk-test", model="gpt-image-2.5-flare", timeout_seconds=30)

    with pytest.raises(AIResponseError):
        provider.generate_image(prompt="a red circle")

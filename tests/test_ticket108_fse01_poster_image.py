"""Ticket #108 § 4 — génération maîtrisée de l'illustration de l'affiche FSE01 : au maximum
deux tentatives, aucune écriture de fichier partiel en cas d'échec, pas de régénération
silencieuse si l'image existe déjà. Aucun appel réseau réel (voir `AIProviderError` factice
ci-dessous, même esprit que `tests/ai/test_image_provider.py`)."""

import json

import pytest

import app.v1.fse01_image as fse01_image
from app.ai.provider import AIResponseError


class _FakeProvider:
    def __init__(self, outcomes):
        self._outcomes = list(outcomes)
        self.calls = 0

    def generate_image(self, prompt, size, quality):
        self.calls += 1
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture()
def isolated_image_paths(tmp_path, monkeypatch):
    img_dir = tmp_path / "img"
    image_path = img_dir / "fse01_affiche_securite_routiere.png"
    metadata_path = img_dir / "fse01_affiche_securite_routiere.json"
    monkeypatch.setattr(fse01_image, "IMG_DIR", img_dir)
    monkeypatch.setattr(fse01_image, "IMAGE_PATH", image_path)
    monkeypatch.setattr(fse01_image, "METADATA_PATH", metadata_path)
    return image_path, metadata_path


def test_skips_generation_if_image_already_exists(isolated_image_paths, monkeypatch):
    image_path, _ = isolated_image_paths
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"already-here")

    def fail_if_called():
        raise AssertionError("ne doit jamais appeler le fournisseur si l'image existe déjà")

    monkeypatch.setattr(fse01_image, "get_image_provider", fail_if_called)

    result = fse01_image.generate_and_save_poster_image(force=False)
    assert result == image_path
    assert image_path.read_bytes() == b"already-here"


def test_succeeds_on_first_attempt(isolated_image_paths, monkeypatch):
    image_path, metadata_path = isolated_image_paths
    provider = _FakeProvider([b"real-image-bytes"])
    monkeypatch.setattr(fse01_image, "get_image_provider", lambda: provider)

    result = fse01_image.generate_and_save_poster_image(force=False)

    assert result == image_path
    assert provider.calls == 1
    assert image_path.read_bytes() == b"real-image-bytes"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["prompt"] == fse01_image.FSE01_POSTER_PROMPT
    assert "generated_at" in metadata


def test_retries_once_after_technical_failure_then_succeeds(isolated_image_paths, monkeypatch):
    image_path, _ = isolated_image_paths
    provider = _FakeProvider([AIResponseError("panne temporaire"), b"real-image-bytes"])
    monkeypatch.setattr(fse01_image, "get_image_provider", lambda: provider)

    result = fse01_image.generate_and_save_poster_image(force=False)

    assert result == image_path
    assert provider.calls == 2
    assert image_path.read_bytes() == b"real-image-bytes"


def test_never_more_than_two_attempts_and_no_partial_file_on_failure(
    isolated_image_paths, monkeypatch
):
    image_path, metadata_path = isolated_image_paths
    provider = _FakeProvider(
        [AIResponseError("échec 1"), AIResponseError("échec 2"), b"ne-doit-jamais-etre-utilise"]
    )
    monkeypatch.setattr(fse01_image, "get_image_provider", lambda: provider)

    result = fse01_image.generate_and_save_poster_image(force=False)

    assert result is None
    assert provider.calls == 2  # jamais une 3e tentative
    assert not image_path.exists()
    assert not metadata_path.exists()


def test_force_regenerates_even_if_image_exists(isolated_image_paths, monkeypatch):
    image_path, _ = isolated_image_paths
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"old-image")
    provider = _FakeProvider([b"new-image"])
    monkeypatch.setattr(fse01_image, "get_image_provider", lambda: provider)

    result = fse01_image.generate_and_save_poster_image(force=True)

    assert result == image_path
    assert image_path.read_bytes() == b"new-image"

"""Ticket #118 — génération maîtrisée des deux illustrations de Sophie Lambert (FSE03) :
au maximum deux tentatives par image, aucune écriture de fichier partiel en cas d'échec,
la scène d'anniversaire réutilise le portrait comme image de référence (cohérence du
personnage). Aucun appel réseau réel (même esprit que `tests/ai/test_image_provider.py`
et `tests/test_ticket108_fse01_poster_image.py`)."""

import json

import pytest

import app.v1.fse03_image as fse03_image
from app.ai.provider import AIResponseError


class _FakeProvider:
    def __init__(self, generate_outcomes=None, edit_outcomes=None):
        self._generate_outcomes = list(generate_outcomes or [])
        self._edit_outcomes = list(edit_outcomes or [])
        self.generate_calls = 0
        self.edit_calls = []

    def generate_image(self, prompt, size, quality):
        self.generate_calls += 1
        outcome = self._generate_outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def edit_image(self, prompt, reference_images, size, quality, input_fidelity=None):
        self.edit_calls.append(reference_images)
        outcome = self._edit_outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture()
def isolated_paths(tmp_path, monkeypatch):
    img_dir = tmp_path / "img"
    portrait_path = img_dir / "fse03_sophie_portrait.png"
    portrait_meta = img_dir / "fse03_sophie_portrait.json"
    birthday_path = img_dir / "fse03_sophie_birthday.png"
    birthday_meta = img_dir / "fse03_sophie_birthday.json"
    monkeypatch.setattr(fse03_image, "IMG_DIR", img_dir)
    monkeypatch.setattr(fse03_image, "PORTRAIT_IMAGE_PATH", portrait_path)
    monkeypatch.setattr(fse03_image, "PORTRAIT_METADATA_PATH", portrait_meta)
    monkeypatch.setattr(fse03_image, "BIRTHDAY_IMAGE_PATH", birthday_path)
    monkeypatch.setattr(fse03_image, "BIRTHDAY_METADATA_PATH", birthday_meta)
    return portrait_path, portrait_meta, birthday_path, birthday_meta


def test_generates_portrait_then_uses_it_as_reference_for_birthday(isolated_paths, monkeypatch):
    portrait_path, portrait_meta, birthday_path, birthday_meta = isolated_paths
    provider = _FakeProvider(
        generate_outcomes=[b"portrait-bytes"],
        edit_outcomes=[b"birthday-bytes"],
    )
    monkeypatch.setattr(fse03_image, "get_image_provider", lambda: provider)

    result_portrait, result_birthday = fse03_image.generate_and_save_sophie_images()

    assert result_portrait == portrait_path
    assert result_birthday == birthday_path
    assert portrait_path.read_bytes() == b"portrait-bytes"
    assert birthday_path.read_bytes() == b"birthday-bytes"
    # La scène d'anniversaire doit avoir reçu le portrait fraîchement généré comme référence.
    assert provider.edit_calls == [[b"portrait-bytes"]]
    metadata = json.loads(birthday_meta.read_text(encoding="utf-8"))
    assert metadata["reference_image"] == "fse03_sophie_portrait.png"


def test_skips_generation_if_both_images_already_exist(isolated_paths, monkeypatch):
    portrait_path, _, birthday_path, _ = isolated_paths
    portrait_path.parent.mkdir(parents=True)
    portrait_path.write_bytes(b"already-portrait")
    birthday_path.write_bytes(b"already-birthday")

    def fail_if_called():
        raise AssertionError("ne doit jamais appeler le fournisseur si les images existent déjà")

    monkeypatch.setattr(fse03_image, "get_image_provider", fail_if_called)

    result_portrait, result_birthday = fse03_image.generate_and_save_sophie_images(force=False)
    assert result_portrait == portrait_path
    assert result_birthday == birthday_path


def test_portrait_failure_prevents_birthday_attempt(isolated_paths, monkeypatch):
    portrait_path, _, birthday_path, _ = isolated_paths
    provider = _FakeProvider(
        generate_outcomes=[AIResponseError("échec 1"), AIResponseError("échec 2")],
    )
    monkeypatch.setattr(fse03_image, "get_image_provider", lambda: provider)

    result_portrait, result_birthday = fse03_image.generate_and_save_sophie_images()

    assert result_portrait is None
    assert result_birthday is None
    assert not portrait_path.exists()
    assert not birthday_path.exists()
    assert provider.edit_calls == []  # jamais tenté sans portrait


def test_birthday_retries_once_after_technical_failure(isolated_paths, monkeypatch):
    _, _, birthday_path, _ = isolated_paths
    provider = _FakeProvider(
        generate_outcomes=[b"portrait-bytes"],
        edit_outcomes=[AIResponseError("échec technique"), b"birthday-bytes"],
    )
    monkeypatch.setattr(fse03_image, "get_image_provider", lambda: provider)

    _, result_birthday = fse03_image.generate_and_save_sophie_images()

    assert result_birthday == birthday_path
    assert len(provider.edit_calls) == 2


def test_never_more_than_two_attempts_per_image(isolated_paths, monkeypatch):
    portrait_path, _, birthday_path, _ = isolated_paths
    provider = _FakeProvider(
        generate_outcomes=[b"portrait-bytes"],
        edit_outcomes=[AIResponseError("échec 1"), AIResponseError("échec 2")],
    )
    monkeypatch.setattr(fse03_image, "get_image_provider", lambda: provider)

    result_portrait, result_birthday = fse03_image.generate_and_save_sophie_images()

    assert result_portrait == portrait_path
    assert result_birthday is None
    assert len(provider.edit_calls) == 2  # jamais une 3e tentative
    assert not birthday_path.exists()


def test_force_regenerates_both_images(isolated_paths, monkeypatch):
    portrait_path, _, birthday_path, _ = isolated_paths
    portrait_path.parent.mkdir(parents=True)
    portrait_path.write_bytes(b"old-portrait")
    birthday_path.write_bytes(b"old-birthday")
    provider = _FakeProvider(
        generate_outcomes=[b"new-portrait"],
        edit_outcomes=[b"new-birthday"],
    )
    monkeypatch.setattr(fse03_image, "get_image_provider", lambda: provider)

    result_portrait, result_birthday = fse03_image.generate_and_save_sophie_images(force=True)

    assert portrait_path.read_bytes() == b"new-portrait"
    assert birthday_path.read_bytes() == b"new-birthday"

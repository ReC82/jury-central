"""Ticket #35 — empêcher le fallback involontaire sur la vraie OPENAI_API_KEY.

Reproduit et vérifie la correction du risque identifié pendant le ticket #29 : un
process manuel/local, lancé sans `OPENAI_API_KEY` déjà positionnée dans son
environnement, sur une machine où `.env` contient une vraie clé (staging), hérite
silencieusement de cette clé via le fallback `env_file` de pydantic-settings.

Aucun test ici ne lit ni n'affiche la vraie clé (`/srv/jury-central/.env`) : tous les
`.env` utilisés sont des fichiers temporaires contenant une valeur factice explicitement
non réelle (`sk-fake-test-...`), et aucun appel réseau n'est effectué (voir
`tests/ai/test_openai_provider.py` pour la même discipline sur les tests du fournisseur
lui-même).
"""

import os
from pathlib import Path

import pytest

from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AINotConfiguredError
from app.config import Settings
from app.safe_local_server import force_safe_local_environment

_FAKE_ENV_FILE_KEY = "sk-fake-test-key-never-real-do-not-use"
_FAKE_PROCESS_ENV_KEY = "sk-fake-process-env-key-never-real"


def _write_fake_env_file(tmp_path: Path, key: str = _FAKE_ENV_FILE_KEY) -> Path:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "ADMIN_USERNAME=test-admin\n"
        "ADMIN_PASSWORD=test-password\n"
        "SECRET_KEY=test-secret\n"
        f"OPENAI_API_KEY={key}\n",
        encoding="utf-8",
    )
    return env_path


def test_pytest_never_loads_a_real_key_from_env(monkeypatch):
    """Garde déjà en place dans tests/conftest.py, vérifiée explicitement ici : sous
    pytest, OPENAI_API_KEY vaut toujours "" dans le process, quel que soit .env."""
    assert os.environ.get("OPENAI_API_KEY") == ""


def test_root_cause_reproduced_without_the_guard(tmp_path, monkeypatch):
    """Reproduit le scénario du ticket #29 : sans la garde, un process dont
    OPENAI_API_KEY est absente de l'environnement retombe silencieusement sur .env."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = _write_fake_env_file(tmp_path)

    settings = Settings(_env_file=env_file)

    assert settings.openai_api_key == _FAKE_ENV_FILE_KEY


def test_safe_local_guard_prevents_fallback_to_env_file(tmp_path, monkeypatch):
    """Le mode local sûr (app.safe_local_server) empêche ce fallback : une fois la garde
    appliquée, .env n'est plus jamais consulté pour ce champ, même si le fichier existe
    et contient une clé."""
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_ENV_FILE_KEY)  # état avant la garde
    env_file = _write_fake_env_file(tmp_path)

    force_safe_local_environment()

    assert os.environ["OPENAI_API_KEY"] == ""
    settings = Settings(_env_file=env_file)
    assert settings.openai_api_key == ""


def test_staging_style_explicit_env_var_still_loads_correctly(tmp_path, monkeypatch):
    """Le service staging réel (systemd, EnvironmentFile=.env) positionne
    OPENAI_API_KEY comme une vraie variable de process avant le démarrage d'uvicorn —
    ce cas doit continuer à fonctionner normalement, sans être affecté par la garde."""
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_PROCESS_ENV_KEY)
    env_file = _write_fake_env_file(tmp_path, key="sk-different-value-in-env-file")

    settings = Settings(_env_file=env_file)

    # La variable de process (équivalent EnvironmentFile) l'emporte toujours sur .env.
    assert settings.openai_api_key == _FAKE_PROCESS_ENV_KEY


def test_safe_local_server_module_import_has_no_side_effect_beyond_the_guard():
    """Importer app.safe_local_server ne doit jamais démarrer de serveur ni importer
    app.main au niveau module (uvicorn.run n'est appelé que dans main())."""
    import sys

    assert "app.safe_local_server" in sys.modules
    # app.main n'est référencé que par la chaîne "app.main:app" passée à uvicorn.run
    # dans main() — jamais importé directement par ce module.
    import inspect

    import app.safe_local_server as mod

    source = inspect.getsource(mod)
    assert "import app.main" not in source
    assert "from app.main" not in source


def test_no_real_network_call_possible_with_empty_key():
    """Avec la garde appliquée, toute tentative de correction/génération IA lève
    AINotConfiguredError avant toute I/O réseau — jamais un appel réel."""
    force_safe_local_environment()
    with pytest.raises(AINotConfiguredError):
        OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o-mini", timeout_seconds=5)


def test_not_configured_error_never_contains_a_secret():
    force_safe_local_environment()
    with pytest.raises(AINotConfiguredError) as excinfo:
        OpenAIProvider(api_key="", model="gpt-4o-mini", timeout_seconds=5)
    message = str(excinfo.value)
    assert _FAKE_ENV_FILE_KEY not in message
    assert _FAKE_PROCESS_ENV_KEY not in message
    assert "sk-" not in message


def test_safe_local_server_cli_entry_point_is_registered():
    """La commande `safe-local-server` (voir pyproject.toml [project.scripts]) est bien
    exposée, au même titre que seed-db/reset-db."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    assert 'safe-local-server = "app.safe_local_server:main"' in content

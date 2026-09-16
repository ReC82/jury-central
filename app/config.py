from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    admin_username: str
    admin_password: str
    secret_key: str = "changeme"

    # Génération/correction d'exercices par IA (ticket #10, complément IA) — jamais commité,
    # jamais transmis au navigateur, jamais journalisé (voir app/ai/openai_provider.py).
    # Chaîne vide = fonctionnalité non configurée (voir app/ai/provider.py::AINotConfiguredError).
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_request_timeout_seconds: float = 20.0

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


settings = Settings()

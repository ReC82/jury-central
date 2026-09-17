from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    admin_username: str
    admin_password: str
    secret_key: str = "changeme"

    # Environnement d'exécution (ticket #39) : "local" par défaut, comme déjà documenté
    # dans .env.example depuis l'origine du projet (jusqu'ici jamais lu par le code).
    # Seul usage actuel : app.main.py active le drapeau `Secure` du cookie de session
    # (voir SessionMiddleware) uniquement pour "staging"/"prod" — jamais par défaut, pour
    # ne changer aucun comportement existant tant que .env ne le déclare pas
    # explicitement. Voir docs/auth_v1.md, § Session.
    app_env: str = "local"

    # Génération/correction d'exercices par IA (ticket #10, complément IA) — jamais commité,
    # jamais transmis au navigateur, jamais journalisé (voir app/ai/openai_provider.py).
    # Chaîne vide = fonctionnalité non configurée (voir app/ai/provider.py::AINotConfiguredError).
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_request_timeout_seconds: float = 20.0

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


settings = Settings()

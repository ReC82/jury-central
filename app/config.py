from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    admin_username: str
    admin_password: str
    secret_key: str = "changeme"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


settings = Settings()

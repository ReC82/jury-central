"""Point d'entrée unique pour obtenir le fournisseur IA réellement utilisé.

Le reste de l'application (routes `app/practice.py`) appelle toujours `get_ai_provider()`
plutôt que d'instancier `OpenAIProvider` directement, pour garder un seul endroit de
configuration et permettre aux tests de substituer un fournisseur factice
(`monkeypatch.setattr("app.practice.get_ai_provider", ...)`, voir `tests/ai/`).
"""

from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AIProvider
from app.config import settings


def get_ai_provider() -> AIProvider:
    """Lève `AINotConfiguredError` (voir `app.ai.provider`) si aucune clé n'est configurée —
    à catch par l'appelant pour renvoyer une erreur claire côté UI, jamais une panne 500."""
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.ai_request_timeout_seconds,
    )

"""Interface générique d'un fournisseur IA.

Le reste de l'application (routes `app/practice.py`) ne dépend jamais directement d'un SDK
ou d'une API tierce — uniquement de ce protocole. Permet de substituer un fournisseur
factice dans les tests (`app/ai/fake_provider.py`), sans appel réseau réel, conformément au
complément IA du ticket #10.
"""

from typing import Protocol

from app.ai.schemas import AICorrectionResult, GeneratedAIExercise, PedagogicalContext


class AIProviderError(Exception):
    """Erreur générique du fournisseur IA — jamais une exception brute de SDK/HTTP."""


class AINotConfiguredError(AIProviderError):
    """Aucune clé API configurée : fonctionnalité indisponible, pas une panne serveur."""


class AITimeoutError(AIProviderError):
    """Le fournisseur IA n'a pas répondu dans le délai imparti."""


class AIResponseError(AIProviderError):
    """Réponse reçue mais invalide ou non conforme au format attendu."""


class AIProvider(Protocol):
    def generate_exercise(
        self, context: PedagogicalContext, difficulty: str
    ) -> GeneratedAIExercise: ...

    def correct_answer(
        self,
        context: PedagogicalContext,
        exercise_statement: str,
        exercise_type: str,
        difficulty: str,
        candidate_answer: str,
    ) -> AICorrectionResult: ...

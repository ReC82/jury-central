"""Interface générique d'un fournisseur IA.

Le reste de l'application (routes `app/practice.py`) ne dépend jamais directement d'un SDK
ou d'une API tierce — uniquement de ce protocole. Permet de substituer un fournisseur
factice dans les tests (`app/ai/fake_provider.py`), sans appel réseau réel, conformément au
complément IA du ticket #10.

Ticket #23 : ajoute `generate_questionnaire`/`correct_semantic_batch` au même protocole —
même fournisseur, même mécanisme de substitution en test, pas un second moteur. La
correction déterministe (QCM, vrai/faux, matching, classification, ordering, numeric,
fill_blank) ne passe jamais par le fournisseur : voir `app/ai/local_correction.py` et
l'orchestrateur `app/ai/questionnaire.py::correct_questionnaire`, qui n'appelle
`correct_semantic_batch` que pour le sous-ensemble de questions qui en ont réellement
besoin (long_answer/diagnostic/procedure, et short_answer/vocabulary sans
`accepted_answers`).
"""

from typing import Any, Protocol

from app.ai.schemas import (
    AICorrectionResult,
    GeneratedAIExercise,
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireQuestion,
    QuestionnaireRequest,
)


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

    def generate_questionnaire(self, request: QuestionnaireRequest) -> Questionnaire: ...

    def correct_semantic_batch(
        self,
        questions: list[QuestionnaireQuestion],
        answers: dict[str, Any],
        severity: str,
        contexts: list[PedagogicalContext],
    ) -> dict[str, QuestionCorrection]: ...

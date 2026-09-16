"""Structures de données du moteur IA.

Toute donnée échangée avec un fournisseur IA passe par ces dataclasses : le reste de
l'application ne manipule jamais du texte libre non structuré renvoyé par un modèle de
langage (voir le complément IA du ticket #10 : « ne pas se contenter de texte libre si une
réponse JSON structurée peut rendre le système plus robuste »).
"""

from dataclasses import dataclass, field
from typing import Any

DIFFICULTIES = ("facile", "moyen", "difficile")

EXERCISE_TYPES = (
    "réponse rédigée",
    "diagnostic",
    "classement",
    "calcul",
    "procédure",
    "mise en situation",
)


@dataclass(frozen=True)
class PedagogicalContext:
    """Contexte pédagogique borné transmis à l'IA — jamais l'ensemble de la base.

    Rédigé à la main pour chaque cours (voir `app/ai/context.py`) à partir du contenu
    réellement enseigné, jamais extrait automatiquement d'un bloc de contenu libre : ce sont
    les notions explicitement validées par ChatGPT (chef de projet, autorité pédagogique).
    """

    course_key: str
    course_title: str
    level: str
    allowed_notions: list[str]
    competencies: list[str]
    vocabulary: list[str]
    constraints: str = ""


@dataclass
class GeneratedAIExercise:
    exercise_type: str
    difficulty: str
    statement: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "exercise_type": self.exercise_type,
            "difficulty": self.difficulty,
            "statement": self.statement,
        }


@dataclass
class AICorrectionResult:
    appreciation: str
    correct_points: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    expected_answer_explained: str = ""
    score: float | None = None
    max_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "appreciation": self.appreciation,
            "correct_points": self.correct_points,
            "errors": self.errors,
            "expected_answer_explained": self.expected_answer_explained,
            "score": self.score,
            "max_score": self.max_score,
        }

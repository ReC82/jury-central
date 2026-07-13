import json
from dataclasses import dataclass, field
from typing import Any

from generators.base import GeneratedExercise
from generators.registry import get_generator


@dataclass
class ExerciseBlockConfig:
    generator: str
    difficulty: int = 1
    count: int = 1
    tags: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(
            {
                "generator": self.generator,
                "difficulty": self.difficulty,
                "count": self.count,
                "tags": self.tags,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, raw: str) -> "ExerciseBlockConfig":
        try:
            data = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        return cls(
            generator=data.get("generator", ""),
            difficulty=int(data.get("difficulty", 1)),
            count=max(1, int(data.get("count", 1))),
            tags=list(data.get("tags", [])),
        )


def exercise_to_dict(exercise: GeneratedExercise) -> dict[str, Any]:
    """Représentation complète, y compris la réponse. Réservé à l'admin (debug)."""
    return {
        "statement": exercise.statement,
        "solution_steps": exercise.solution_steps,
        "answer_value": float(exercise.answer),
        "answer_display": str(exercise.answer),
        "hint": exercise.hint,
    }


def exercise_to_public_dict(exercise: GeneratedExercise) -> dict[str, Any]:
    """Représentation publique : jamais la réponse ni la correction.

    La vérification et la correction se font via un second appel serveur
    (`/practice/api/verify` et `/practice/api/reveal`) en fournissant le seed.
    """
    return {"statement": exercise.statement, "seed": exercise.seed, "hint": exercise.hint}


def generate_exercises(config: ExerciseBlockConfig) -> list[dict[str, Any]]:
    """Génère `count` exercices publics (sans réponse) pour l'affichage d'un bloc."""
    generator = get_generator(config.generator)
    return [
        exercise_to_public_dict(generator(difficulty=config.difficulty))
        for _ in range(config.count)
    ]

import json
from dataclasses import dataclass, field
from typing import Any

from app.content import render_markdown
from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise
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
        "statement_html": render_markdown(exercise.statement),
        "solution_steps": exercise.solution_steps,
        "solution_steps_html": [render_markdown(step) for step in exercise.solution_steps],
        "answer_value": float(exercise.answer),
        "answer_display": str(exercise.answer),
        "hint": exercise.hint,
        "hint_html": render_markdown(exercise.hint) if exercise.hint else "",
    }


def exercise_to_public_dict(exercise: GeneratedExercise) -> dict[str, Any]:
    """Représentation publique : jamais la réponse ni la correction.

    La vérification et la correction se font via un second appel serveur
    (`/practice/api/verify` et `/practice/api/reveal`) en fournissant le seed.

    `statement_html`/`hint_html` sont le rendu du même Design System que le cours (voir
    `app/content.py::render_markdown`) : tableaux, listes et formules MathJax dans un énoncé
    généré s'affichent correctement, au lieu d'une phrase brute.
    """
    return {
        "statement": exercise.statement,
        "statement_html": render_markdown(exercise.statement),
        "seed": exercise.seed,
        "hint": exercise.hint,
        "hint_html": render_markdown(exercise.hint) if exercise.hint else "",
    }


def generate_exercises(
    config: ExerciseBlockConfig,
) -> list[GeneratedExercise | InteractiveExercise]:
    """Génère `count` exercices bruts pour un bloc `generated_exercise`.

    Retourne les objets tels que produits par le générateur (jamais convertis en dict ici) :
    un générateur donné renvoie toujours la même forme (`GeneratedExercise` ou
    `InteractiveExercise`), mais l'appelant (rendu de leçon) doit détecter laquelle avant de
    choisir le composant d'affichage — voir docs/EXERCISE_TYPES.md.
    """
    generator = get_generator(config.generator)
    return [generator(difficulty=config.difficulty) for _ in range(config.count)]

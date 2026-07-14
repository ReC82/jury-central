from dataclasses import dataclass, field
from typing import Any, Protocol

from generators.exercise_types import InteractiveExercise


@dataclass
class GeneratedExercise:
    statement: str
    answer: Any
    difficulty: int
    seed: int
    solution_steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    hint: str = ""


class ExerciseGenerator(Protocol):
    """Interface commune que chaque générateur doit exposer.

    Un générateur retourne soit un `GeneratedExercise` (ancien moteur : énoncé texte, une
    seule réponse), soit un `InteractiveExercise` (nouveau moteur, voir
    docs/EXERCISE_TYPES.md — ex. `value_table`). Les deux formes coexistent : chaque appelant
    (rendu de leçon, routes /practice/api, outils de debug admin) doit détecter le type
    retourné plutôt que de supposer une forme fixe.
    """

    def __call__(
        self, difficulty: int, seed: int | None = None
    ) -> GeneratedExercise | InteractiveExercise: ...

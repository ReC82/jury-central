from dataclasses import dataclass, field
from typing import Any, Protocol


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
    """Interface commune que chaque générateur doit exposer."""

    def __call__(self, difficulty: int, seed: int | None = None) -> GeneratedExercise: ...

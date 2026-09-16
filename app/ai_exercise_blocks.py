"""Configuration JSON du bloc de leçon `ai_exercise` (génération + correction IA à la
demande) — voir `docs/ai_exercise_engine.md` et le complément IA du ticket #10.

Suit exactement la même convention que `app/exercise_blocks.py::ExerciseBlockConfig` (JSON
stocké dans `LessonBlock.content`), pour un générateur Python déterministe. Ici, la clé
`context_key` pointe vers un contexte pédagogique borné du registre
`app/ai/context.py::PEDAGOGICAL_CONTEXTS` — jamais de contenu pédagogique libre stocké dans
le bloc lui-même.
"""

import json
from dataclasses import dataclass


@dataclass
class AIExerciseBlockConfig:
    context_key: str
    intro: str = ""

    def to_json(self) -> str:
        return json.dumps(
            {"context_key": self.context_key, "intro": self.intro}, ensure_ascii=False
        )

    @classmethod
    def from_json(cls, raw: str) -> "AIExerciseBlockConfig":
        try:
            data = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        return cls(
            context_key=data.get("context_key", ""),
            intro=data.get("intro", ""),
        )

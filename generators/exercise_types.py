"""Enveloppe générique des exercices interactifs (voir docs/EXERCISE_TYPES.md).

Format commun à tous les types d'exercices interactifs de Jury Central (numeric, text,
multiple_choice, true_false, value_table, equation, matching, drag_drop, geometry, graph).
Un générateur ne produit jamais de HTML, de CSS ni de JavaScript : uniquement cette
structure de données. Le rendu est entièrement construit côté frontend par le composant
correspondant au champ `type`.
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InteractiveExercise:
    type: str
    question: str
    data: dict[str, Any]
    answer: dict[str, Any]
    hint: str = ""
    explanation: str = ""
    difficulty: int = 1
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        """Représentation envoyée au navigateur avant validation : jamais `answer`."""
        return {
            "type": self.type,
            "question": self.question,
            "data": self.data,
            "hint": self.hint,
            "difficulty": self.difficulty,
            "seed": self.seed,
        }

    def to_public_json(self) -> str:
        return json.dumps(self.to_public_dict(), ensure_ascii=False)

    def to_full_dict(self) -> dict[str, Any]:
        """Représentation complète, réponse incluse.

        Réservée au serveur (vérification) et aux outils de debug admin — ne jamais
        transmettre cette représentation à un étudiant avant qu'il ait répondu.
        """
        return {
            "type": self.type,
            "question": self.question,
            "data": self.data,
            "answer": self.answer,
            "hint": self.hint,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "seed": self.seed,
            "metadata": self.metadata,
        }

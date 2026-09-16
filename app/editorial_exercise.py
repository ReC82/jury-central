"""Socle générique des exercices éditoriaux structurés (ticket #17).

Un bloc de leçon `editorial_exercise` regroupe plusieurs items structurés (voir
`docs/claude-reports/2026-09-16_audit_interactivite.md`, section D, et
`docs/editorial_exercise_engine.md`). Première tranche de types (ticket #17) :
`single_choice`, `true_false`, `short_answer` — uniquement lorsqu'une correction locale
déterministe est fiable (comparaison exacte après normalisation, voir
`app/answer_checking.py::text_answer_matches`). Les types nécessitant une correction IA
(`long_answer`) ou une correction locale plus complexe (`classification`, `ordering`,
`matching`) seront ajoutés par des tickets séparés — voir
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` pour la liste précise des
exercices MC01 concernés.

Même principe de sécurité que `value_table`/`quiz`/`ai_exercise` : le serveur recharge
toujours la configuration complète depuis `LessonBlock.content` pour corriger ; aucune
réponse correcte, aucune liste de réponses acceptées, aucune explication n'est jamais
transmise au navigateur avant l'appel de correction. Aucun `eval()`.
"""

import json
from dataclasses import dataclass, field
from typing import Any

from app.answer_checking import text_answer_matches
from app.content import render_markdown

EDITORIAL_EXERCISE_TYPES = ("single_choice", "true_false", "short_answer")
EDITORIAL_EXERCISE_MODES = ("practice", "exam")


class EditorialExerciseValidationError(ValueError):
    """Configuration d'exercice éditorial structurellement invalide.

    Levée à la construction directe (`EditorialExerciseItem(...)`, utilisée par
    `app/seed.py` et les tests) pour échouer tôt sur une erreur d'auteur. `from_json`
    (chargement depuis la base, y compris un contenu admin mal formé) ne la laisse en
    revanche jamais remonter : un item invalide est silencieusement ignoré plutôt que de
    faire échouer le rendu de la page publique — voir `EditorialExerciseBlockConfig.from_json`.
    """


@dataclass
class EditorialExerciseItem:
    exercise_id: str
    type: str
    prompt: str
    points: float = 1.0
    # single_choice / true_false — jamais dans to_public_dict avant correction :
    choices: list[str] = field(default_factory=list)
    correct_index: int | None = None
    # short_answer — jamais dans to_public_dict avant correction :
    accepted_answers: list[str] = field(default_factory=list)
    # commun — jamais dans to_public_dict avant correction :
    explanation: str = ""

    def __post_init__(self) -> None:
        if not self.exercise_id:
            raise EditorialExerciseValidationError("exercise_id est obligatoire.")
        if self.type not in EDITORIAL_EXERCISE_TYPES:
            raise EditorialExerciseValidationError(
                f"{self.exercise_id} : type d'exercice éditorial inconnu : {self.type!r}."
            )
        if not self.prompt.strip():
            raise EditorialExerciseValidationError(f"{self.exercise_id} : prompt vide.")
        if self.points <= 0:
            raise EditorialExerciseValidationError(f"{self.exercise_id} : points doit être > 0.")

        if self.type in ("single_choice", "true_false"):
            if len(self.choices) < 2:
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : au moins deux choix sont requis."
                )
            if self.correct_index is None or not (0 <= self.correct_index < len(self.choices)):
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : correct_index invalide."
                )
        elif self.type == "short_answer" and not self.accepted_answers:
            raise EditorialExerciseValidationError(
                f"{self.exercise_id} : accepted_answers est requis pour short_answer."
            )

    def to_public_dict(self) -> dict[str, Any]:
        """Représentation envoyée au navigateur avant correction : jamais `correct_index`,
        `accepted_answers` ni `explanation`."""
        data: dict[str, Any] = {
            "exercise_id": self.exercise_id,
            "type": self.type,
            "prompt": self.prompt,
            "prompt_html": render_markdown(self.prompt),
            "points": self.points,
        }
        if self.type in ("single_choice", "true_false"):
            data["choices"] = self.choices
        return data

    def check(self, submitted: str) -> bool:
        """Vérifie une réponse soumise. Ne révèle jamais la bonne réponse."""
        if self.type in ("single_choice", "true_false"):
            try:
                return int(submitted) == self.correct_index
            except (TypeError, ValueError):
                return False
        if self.type == "short_answer":
            return text_answer_matches(self.accepted_answers, submitted)
        return False

    def correct_answer_display(self) -> str:
        if self.type in ("single_choice", "true_false") and self.correct_index is not None:
            return self.choices[self.correct_index]
        if self.type == "short_answer" and self.accepted_answers:
            return self.accepted_answers[0]
        return ""


@dataclass
class EditorialExerciseBlockConfig:
    mode: str = "practice"
    items: list[EditorialExerciseItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.mode not in EDITORIAL_EXERCISE_MODES:
            raise EditorialExerciseValidationError(f"mode inconnu : {self.mode!r}.")
        ids = [item.exercise_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise EditorialExerciseValidationError(
                "exercise_id doit être unique au sein d'un même bloc."
            )

    def get_item(self, exercise_id: str) -> EditorialExerciseItem | None:
        return next((item for item in self.items if item.exercise_id == exercise_id), None)

    def to_json(self) -> str:
        return json.dumps(
            {
                "mode": self.mode,
                "items": [
                    {
                        "exercise_id": item.exercise_id,
                        "type": item.type,
                        "prompt": item.prompt,
                        "points": item.points,
                        "choices": item.choices,
                        "correct_index": item.correct_index,
                        "accepted_answers": item.accepted_answers,
                        "explanation": item.explanation,
                    }
                    for item in self.items
                ],
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, raw: str) -> "EditorialExerciseBlockConfig":
        """Chargement tolérant depuis la base : un item structurellement invalide (contenu
        admin mal formé) est silencieusement ignoré plutôt que de faire échouer le rendu de
        la page publique. La validation stricte a lieu à l'auteurisation du contenu
        (construction directe d'`EditorialExerciseItem`, voir `app/seed.py` et les tests)."""
        try:
            data = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}

        items: list[EditorialExerciseItem] = []
        for raw_item in data.get("items", []):
            try:
                items.append(
                    EditorialExerciseItem(
                        exercise_id=raw_item.get("exercise_id", ""),
                        type=raw_item.get("type", ""),
                        prompt=raw_item.get("prompt", ""),
                        points=float(raw_item.get("points", 1.0)),
                        choices=list(raw_item.get("choices", [])),
                        correct_index=raw_item.get("correct_index"),
                        accepted_answers=list(raw_item.get("accepted_answers", [])),
                        explanation=raw_item.get("explanation", ""),
                    )
                )
            except (EditorialExerciseValidationError, TypeError, ValueError):
                continue

        mode = data.get("mode", "practice")
        if mode not in EDITORIAL_EXERCISE_MODES:
            mode = "practice"
        try:
            return cls(mode=mode, items=items)
        except EditorialExerciseValidationError:
            # exercise_id dupliqués après filtrage : configuration incohérente, on ne
            # publie aucun exercice plutôt que d'en publier un sous-ensemble ambigu.
            return cls(mode=mode, items=[])

    def to_public_dict(self) -> dict[str, Any]:
        return {"mode": self.mode, "items": [item.to_public_dict() for item in self.items]}


@dataclass
class EditorialExerciseCorrection:
    exercise_id: str
    correct: bool
    correct_answer: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "exercise_id": self.exercise_id,
            "correct": self.correct,
            "correct_answer": self.correct_answer,
            "correct_answer_html": render_markdown(self.correct_answer)
            if self.correct_answer
            else "",
            "explanation": self.explanation,
            "explanation_html": render_markdown(self.explanation) if self.explanation else "",
        }


def check_editorial_answer(
    config: EditorialExerciseBlockConfig, exercise_id: str, submitted: str
) -> EditorialExerciseCorrection | None:
    """Vérifie une réponse soumise pour un item du bloc. Retourne `None` si `exercise_id`
    est introuvable dans cette configuration (à l'appelant de renvoyer 404) — jamais
    d'exception pour ce cas, qui n'indique pas une erreur de programmation."""
    item = config.get_item(exercise_id)
    if item is None:
        return None
    return EditorialExerciseCorrection(
        exercise_id=item.exercise_id,
        correct=item.check(submitted),
        correct_answer=item.correct_answer_display(),
        explanation=item.explanation,
    )

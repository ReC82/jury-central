"""Socle générique des exercices éditoriaux structurés (ticket #17, étendu au #21).

Un bloc de leçon `editorial_exercise` regroupe plusieurs items structurés (voir
`docs/claude-reports/2026-09-16_audit_interactivite.md`, section D, et
`docs/editorial_exercise_engine.md`). Types pris en charge :
`single_choice`, `true_false`, `short_answer` (ticket #17), `classification`, `ordering`
(ticket #21) — uniquement lorsqu'une correction locale déterministe est fiable. Les types
nécessitant une correction IA (`long_answer`) ou un appariement (`matching`) seront ajoutés
par des tickets séparés — voir `docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md`
et `docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md` pour la liste
précise des exercices MC01 concernés.

Même principe de sécurité que `value_table`/`quiz`/`ai_exercise` : le serveur recharge
toujours la configuration complète depuis `LessonBlock.content` pour corriger ; aucune
réponse correcte, aucune liste de réponses acceptées, aucune explication n'est jamais
transmise au navigateur avant l'appel de correction. Aucun `eval()`.

Pour `classification`/`ordering`, la réponse soumise n'est plus une simple chaîne mais une
liste d'entiers (voir `EditorialExerciseItem.check`) — `check_editorial_answer` accepte donc
`submitted: Any` depuis le ticket #21, tout en restant rétrocompatible avec les réponses
`str` des types existants.
"""

import json
from dataclasses import dataclass, field
from typing import Any

from app.answer_checking import text_answer_matches
from app.content import render_markdown

EDITORIAL_EXERCISE_TYPES = (
    "single_choice",
    "true_false",
    "short_answer",
    "classification",
    "ordering",
)
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
    # classification — categories/elements publics, correct_categories jamais avant correction :
    categories: list[str] = field(default_factory=list)
    elements: list[str] = field(default_factory=list)
    correct_categories: list[int] = field(default_factory=list)
    # ordering — order_items public (ordre de présentation), correct_order jamais avant
    # correction :
    order_items: list[str] = field(default_factory=list)
    correct_order: list[int] = field(default_factory=list)
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
        elif self.type == "classification":
            if len(self.categories) < 2:
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : au moins deux catégories sont requises."
                )
            if len(self.elements) < 2:
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : au moins deux éléments à classer sont requis."
                )
            if len(self.correct_categories) != len(self.elements):
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : correct_categories doit avoir la même longueur "
                    "que elements."
                )
            if any(not (0 <= c < len(self.categories)) for c in self.correct_categories):
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : correct_categories contient un index de "
                    "catégorie invalide."
                )
        elif self.type == "ordering":
            if len(self.order_items) < 2:
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : au moins deux éléments à ordonner sont requis."
                )
            if sorted(self.correct_order) != list(range(len(self.order_items))):
                raise EditorialExerciseValidationError(
                    f"{self.exercise_id} : correct_order doit être une permutation valide "
                    "des index de order_items."
                )

    def to_public_dict(self) -> dict[str, Any]:
        """Représentation envoyée au navigateur avant correction : jamais `correct_index`,
        `accepted_answers`, `correct_categories`, `correct_order` ni `explanation`."""
        data: dict[str, Any] = {
            "exercise_id": self.exercise_id,
            "type": self.type,
            "prompt": self.prompt,
            "prompt_html": render_markdown(self.prompt),
            "points": self.points,
        }
        if self.type in ("single_choice", "true_false"):
            data["choices"] = self.choices
        elif self.type == "classification":
            data["categories"] = self.categories
            data["elements"] = self.elements
        elif self.type == "ordering":
            data["order_items"] = self.order_items
        return data

    def check(self, submitted: Any) -> bool:
        """Vérifie une réponse soumise. Ne révèle jamais la bonne réponse.

        `submitted` est une `str` pour single_choice/true_false/short_answer (inchangé
        depuis le ticket #17), et une `list[int]` pour classification/ordering (ticket
        #21) : classification attend un index de catégorie par élément, dans l'ordre de
        `elements` ; ordering attend une permutation des index de `order_items` dans
        l'ordre proposé par l'apprenant. Toute forme inattendue (mauvais type, mauvaise
        longueur, valeurs non entières, permutation invalide) est traitée comme une réponse
        incorrecte, jamais comme une erreur serveur.
        """
        if self.type in ("single_choice", "true_false"):
            try:
                return int(submitted) == self.correct_index
            except (TypeError, ValueError):
                return False
        if self.type == "short_answer":
            if not isinstance(submitted, str):
                return False
            return text_answer_matches(self.accepted_answers, submitted)
        if self.type == "classification":
            return self._check_classification(submitted)
        if self.type == "ordering":
            return self._check_ordering(submitted)
        return False

    def _check_classification(self, submitted: Any) -> bool:
        if not isinstance(submitted, list) or len(submitted) != len(self.elements):
            return False
        try:
            submitted_indexes = [int(value) for value in submitted]
        except (TypeError, ValueError):
            return False
        return submitted_indexes == self.correct_categories

    def _check_ordering(self, submitted: Any) -> bool:
        if not isinstance(submitted, list) or len(submitted) != len(self.order_items):
            return False
        try:
            submitted_indexes = [int(value) for value in submitted]
        except (TypeError, ValueError):
            return False
        if sorted(submitted_indexes) != list(range(len(self.order_items))):
            return False
        return submitted_indexes == self.correct_order

    def correct_answer_display(self) -> str:
        if self.type in ("single_choice", "true_false") and self.correct_index is not None:
            return self.choices[self.correct_index]
        if self.type == "short_answer" and self.accepted_answers:
            return self.accepted_answers[0]
        if self.type == "classification" and self.correct_categories:
            pairs = zip(self.elements, self.correct_categories, strict=True)
            return "\n".join(
                f"- {element} → {self.categories[category_index]}"
                for element, category_index in pairs
            )
        if self.type == "ordering" and self.correct_order:
            return "\n".join(
                f"{position + 1}. {self.order_items[item_index]}"
                for position, item_index in enumerate(self.correct_order)
            )
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
                        "categories": item.categories,
                        "elements": item.elements,
                        "correct_categories": item.correct_categories,
                        "order_items": item.order_items,
                        "correct_order": item.correct_order,
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
                        categories=list(raw_item.get("categories", [])),
                        elements=list(raw_item.get("elements", [])),
                        correct_categories=list(raw_item.get("correct_categories", [])),
                        order_items=list(raw_item.get("order_items", [])),
                        correct_order=list(raw_item.get("correct_order", [])),
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
    config: EditorialExerciseBlockConfig, exercise_id: str, submitted: Any
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

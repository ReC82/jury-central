"""Vérification serveur des exercices `value_table` (voir docs/EXERCISE_TYPES.md).

Compare une soumission cellule par cellule à la réponse de l'exercice. Réutilise
`app.answer_checking` (comparaison exacte via `Fraction`, aucun `eval()`), comme les quiz et
les exercices générés. La réponse n'est jamais transmise au navigateur avant cet appel.
"""

from dataclasses import dataclass
from typing import Any

from app.answer_checking import answers_match, parse_answer
from generators.exercise_types import InteractiveExercise
from generators.value_table import ValueTableData


@dataclass
class CellResult:
    row: int
    col: int
    correct: bool
    correct_value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "row": self.row,
            "col": self.col,
            "correct": self.correct,
            "correct_value": self.correct_value,
        }


@dataclass
class ValueTableCorrection:
    all_correct: bool
    cells: list[CellResult]
    explanation: str
    hint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "all_correct": self.all_correct,
            "cells": [cell.to_dict() for cell in self.cells],
            "explanation": self.explanation,
            "hint": self.hint,
        }


def check_value_table_answers(
    exercise: InteractiveExercise, submitted: list[str]
) -> ValueTableCorrection:
    """Vérifie une soumission cellule par cellule pour un exercice `value_table`.

    `submitted` doit contenir une réponse par cellule éditable, dans l'ordre de
    `ValueTableData.editable_positions()` (lignes puis colonnes). Lève `ValueError` si
    `exercise.type` n'est pas `"value_table"` ou si le nombre de réponses ne correspond pas
    au nombre de cellules éditables — ces deux cas indiquent un appelant incohérent, jamais
    une réponse étudiante invalide (une case vide est gérée comme une réponse incorrecte,
    pas comme une erreur).
    """
    if exercise.type != "value_table":
        raise ValueError(f"Type d'exercice inattendu pour value_table : {exercise.type!r}")

    table = ValueTableData.from_dict(exercise.data)
    positions = table.editable_positions()
    correct_values = exercise.answer.get("cells", [])

    if len(submitted) != len(positions):
        raise ValueError(
            f"{len(positions)} réponse(s) attendue(s), {len(submitted)} soumise(s)."
        )
    if len(correct_values) != len(positions):
        raise ValueError(
            "La réponse de l'exercice ne correspond pas au nombre de cellules éditables."
        )

    cells: list[CellResult] = []
    all_correct = True
    for (row_index, col_index), correct_raw, submitted_raw in zip(
        positions, correct_values, submitted, strict=True
    ):
        expected = parse_answer(str(correct_raw))
        is_correct = expected is not None and answers_match(expected, submitted_raw)
        if not is_correct:
            all_correct = False
        cells.append(
            CellResult(row=row_index, col=col_index, correct=is_correct, correct_value=correct_raw)
        )

    return ValueTableCorrection(
        all_correct=all_correct,
        cells=cells,
        explanation=exercise.explanation,
        hint=exercise.hint,
    )

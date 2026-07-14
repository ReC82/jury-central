"""Type d'exercice interactif "value_table" (voir docs/EXERCISE_TYPES.md, section 5).

Un générateur construit un `ValueTableData` (colonnes + lignes, chaque cellule marquée
éditable ou non) et fournit une réponse par cellule éditable via `build_value_table_exercise`.
Aucun HTML n'est produit ici : le composant frontend (app/static/js/value_table.js) dessine
entièrement le tableau à partir de la structure de données retournée.
"""

from dataclasses import dataclass, field
from typing import Any

from generators.exercise_types import InteractiveExercise


@dataclass
class ValueTableRow:
    """Une ligne du tableau.

    `values[i]` est la valeur affichée pour la colonne i (donnée de départ déjà connue de
    l'étudiant) ; elle est ignorée à l'affichage si `editable[i]` vaut `True` (la cellule est
    alors vide, à compléter). `values` peut être omis si toutes les cellules sont éditables.
    """

    label: str
    editable: list[bool]
    values: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.values:
            self.values = [None] * len(self.editable)
        if len(self.values) != len(self.editable):
            raise ValueError(
                f"La ligne « {self.label} » : `values` ({len(self.values)}) et `editable` "
                f"({len(self.editable)}) doivent avoir la même longueur."
            )

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "values": self.values, "editable": self.editable}


@dataclass
class ValueTableData:
    columns: list[Any]
    rows: list[ValueTableRow]

    def __post_init__(self) -> None:
        if not self.columns:
            raise ValueError("Un tableau doit avoir au moins une colonne.")
        if not self.rows:
            raise ValueError("Un tableau doit avoir au moins une ligne.")
        for row in self.rows:
            if len(row.editable) != len(self.columns):
                raise ValueError(
                    f"La ligne « {row.label} » a {len(row.editable)} cellule(s), "
                    f"attendu {len(self.columns)} (une par colonne)."
                )

    def to_dict(self) -> dict[str, Any]:
        return {"columns": self.columns, "rows": [row.to_dict() for row in self.rows]}

    def editable_positions(self) -> list[tuple[int, int]]:
        """Positions (row_index, col_index) des cellules éditables, dans l'ordre — lignes
        puis colonnes — attendu par `answer["cells"]` et par les réponses soumises."""
        return [
            (row_index, col_index)
            for row_index, row in enumerate(self.rows)
            for col_index, editable in enumerate(row.editable)
            if editable
        ]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValueTableData":
        rows = [
            ValueTableRow(
                label=raw_row["label"],
                editable=list(raw_row["editable"]),
                values=list(raw_row.get("values") or []),
            )
            for raw_row in data["rows"]
        ]
        return cls(columns=list(data["columns"]), rows=rows)


def build_value_table_exercise(
    *,
    question: str,
    columns: list[Any],
    rows: list[ValueTableRow],
    answer_cells: list[Any],
    hint: str = "",
    explanation: str = "",
    difficulty: int = 1,
    seed: int | None = None,
) -> InteractiveExercise:
    """Assemble un exercice `value_table` conforme à docs/EXERCISE_TYPES.md.

    `answer_cells` fournit une réponse pour chaque cellule éditable, dans l'ordre de
    `ValueTableData.editable_positions()` (lignes puis colonnes) — c'est ce qui permet à
    l'exemple officiel du document (une seule ligne) de rester une simple liste à plat.
    """
    table = ValueTableData(columns=columns, rows=rows)
    expected = len(table.editable_positions())
    if len(answer_cells) != expected:
        raise ValueError(
            f"{expected} réponse(s) attendue(s) (une par cellule éditable), "
            f"{len(answer_cells)} fournie(s)."
        )
    return InteractiveExercise(
        type="value_table",
        question=question,
        data=table.to_dict(),
        answer={"cells": list(answer_cells)},
        hint=hint,
        explanation=explanation,
        difficulty=difficulty,
        seed=seed,
    )

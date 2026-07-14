import pytest

from app.value_table import check_value_table_answers
from generators.exercise_types import InteractiveExercise
from generators.value_table import ValueTableData, ValueTableRow, build_value_table_exercise


def _official_example() -> InteractiveExercise:
    """Reproduit l'exemple officiel de docs/EXERCISE_TYPES.md (section "Exemple Value Table")."""
    return build_value_table_exercise(
        question="Complète le tableau.",
        columns=[-3, -5, -10],
        rows=[ValueTableRow(label="f(x)", editable=[True, True, True])],
        answer_cells=[2, 2, 2],
    )


# --- ValueTableRow / ValueTableData ---------------------------------------------------


def test_row_without_values_defaults_to_none() -> None:
    row = ValueTableRow(label="f(x)", editable=[True, False, True])
    assert row.values == [None, None, None]


def test_row_rejects_mismatched_values_length() -> None:
    with pytest.raises(ValueError):
        ValueTableRow(label="f(x)", editable=[True, True], values=[1])


def test_table_rejects_empty_columns() -> None:
    with pytest.raises(ValueError):
        ValueTableData(columns=[], rows=[ValueTableRow(label="f(x)", editable=[])])


def test_table_rejects_empty_rows() -> None:
    with pytest.raises(ValueError):
        ValueTableData(columns=[1, 2], rows=[])


def test_table_rejects_row_with_wrong_cell_count() -> None:
    with pytest.raises(ValueError):
        ValueTableData(columns=[1, 2, 3], rows=[ValueTableRow(label="f(x)", editable=[True, True])])


def test_editable_positions_row_major_order_across_multiple_rows() -> None:
    table = ValueTableData(
        columns=[-2, 0, 3],
        rows=[
            ValueTableRow(label="2x", values=[-4, 0, 6], editable=[False, False, False]),
            ValueTableRow(label="f(x)", editable=[True, True, True]),
        ],
    )
    assert table.editable_positions() == [(1, 0), (1, 1), (1, 2)]


def test_editable_positions_mixed_row() -> None:
    table = ValueTableData(
        columns=["a", "b", "c"],
        rows=[ValueTableRow(label="f(x)", values=[1, None, 3], editable=[False, True, False])],
    )
    assert table.editable_positions() == [(0, 1)]


def test_table_to_dict_matches_official_example_shape() -> None:
    table = ValueTableData(columns=[-3, -5, -10], rows=[ValueTableRow(label="f(x)", editable=[True, True, True])])
    assert table.to_dict() == {
        "columns": [-3, -5, -10],
        "rows": [{"label": "f(x)", "values": [None, None, None], "editable": [True, True, True]}],
    }


def test_table_from_dict_round_trip() -> None:
    original = ValueTableData(
        columns=[-2, 0, 3],
        rows=[
            ValueTableRow(label="2x", values=[-4, 0, 6], editable=[False, False, False]),
            ValueTableRow(label="f(x)", editable=[True, True, True]),
        ],
    )
    rebuilt = ValueTableData.from_dict(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()


# --- build_value_table_exercise -------------------------------------------------------


def test_build_matches_official_example() -> None:
    exercise = _official_example()
    assert exercise.type == "value_table"
    assert exercise.data == {
        "columns": [-3, -5, -10],
        "rows": [{"label": "f(x)", "values": [None, None, None], "editable": [True, True, True]}],
    }
    assert exercise.answer == {"cells": [2, 2, 2]}


def test_build_rejects_wrong_number_of_answers() -> None:
    with pytest.raises(ValueError):
        build_value_table_exercise(
            question="Complète le tableau.",
            columns=[-3, -5, -10],
            rows=[ValueTableRow(label="f(x)", editable=[True, True, True])],
            answer_cells=[2, 2],
        )


# --- InteractiveExercise : jamais la réponse avant validation -------------------------


def test_public_dict_never_contains_answer() -> None:
    exercise = _official_example()
    public = exercise.to_public_dict()
    assert "answer" not in public
    assert "answer" not in exercise.to_public_json()


def test_public_dict_contains_data_and_question() -> None:
    exercise = _official_example()
    public = exercise.to_public_dict()
    assert public["type"] == "value_table"
    assert public["question"] == "Complète le tableau."
    assert public["data"]["columns"] == [-3, -5, -10]


def test_full_dict_contains_answer() -> None:
    exercise = _official_example()
    full = exercise.to_full_dict()
    assert full["answer"] == {"cells": [2, 2, 2]}


# --- check_value_table_answers ---------------------------------------------------------


def test_check_all_correct() -> None:
    exercise = _official_example()
    correction = check_value_table_answers(exercise, ["2", "2", "2"])
    assert correction.all_correct is True
    assert all(cell.correct for cell in correction.cells)
    assert [cell.correct_value for cell in correction.cells] == [2, 2, 2]


def test_check_some_incorrect() -> None:
    exercise = _official_example()
    correction = check_value_table_answers(exercise, ["2", "3", "2"])
    assert correction.all_correct is False
    assert [cell.correct for cell in correction.cells] == [True, False, True]


def test_check_accepts_comma_decimal() -> None:
    exercise = build_value_table_exercise(
        question="q",
        columns=[1],
        rows=[ValueTableRow(label="f(x)", editable=[True])],
        answer_cells=["1.5"],
    )
    correction = check_value_table_answers(exercise, ["1,5"])
    assert correction.all_correct is True


def test_check_empty_submission_is_incorrect_not_an_error() -> None:
    exercise = _official_example()
    correction = check_value_table_answers(exercise, ["", "2", "2"])
    assert correction.all_correct is False
    assert correction.cells[0].correct is False


def test_check_cell_positions_only_cover_editable_cells() -> None:
    exercise = build_value_table_exercise(
        question="q",
        columns=[-2, 0, 3],
        rows=[
            ValueTableRow(label="2x", values=[-4, 0, 6], editable=[False, False, False]),
            ValueTableRow(label="f(x)", editable=[True, True, True]),
        ],
        answer_cells=[-3, 1, 7],
    )
    correction = check_value_table_answers(exercise, ["-3", "1", "7"])
    assert correction.all_correct is True
    assert [(cell.row, cell.col) for cell in correction.cells] == [(1, 0), (1, 1), (1, 2)]


def test_check_rejects_wrong_type() -> None:
    exercise = InteractiveExercise(type="numeric", question="q", data={}, answer={})
    with pytest.raises(ValueError):
        check_value_table_answers(exercise, [])


def test_check_rejects_wrong_submission_length() -> None:
    exercise = _official_example()
    with pytest.raises(ValueError):
        check_value_table_answers(exercise, ["2", "2"])


def test_check_returns_explanation_and_hint() -> None:
    exercise = build_value_table_exercise(
        question="q",
        columns=[1],
        rows=[ValueTableRow(label="f(x)", editable=[True])],
        answer_cells=[1],
        hint="Indice utile",
        explanation="Explication détaillée",
    )
    correction = check_value_table_answers(exercise, ["1"])
    assert correction.hint == "Indice utile"
    assert correction.explanation == "Explication détaillée"


# --- Route de démo admin (TestClient) --------------------------------------------------


def test_demo_page_requires_admin(client) -> None:
    response = client.get("/admin/value-table-demo", follow_redirects=False)
    assert response.status_code == 303


def test_demo_page_renders_without_answer_in_html(admin_client) -> None:
    response = admin_client.get("/admin/value-table-demo")
    assert response.status_code == 200
    assert "data-exercise=" in response.text
    assert "&#34;answer&#34;" not in response.text
    assert "cells&quot;:[-3,1,7]" not in response.text.replace(" ", "")


def test_demo_verify_requires_admin(client) -> None:
    response = client.post(
        "/admin/value-table-demo/verify",
        json={"answers": ["-3", "1", "7"]},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_demo_verify_all_correct(admin_client) -> None:
    response = admin_client.post(
        "/admin/value-table-demo/verify", json={"answers": ["-3", "1", "7"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["all_correct"] is True
    assert len(body["cells"]) == 3


def test_demo_verify_partial_wrong(admin_client) -> None:
    response = admin_client.post(
        "/admin/value-table-demo/verify", json={"answers": ["-3", "0", "7"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["all_correct"] is False
    assert body["cells"][1]["correct"] is False
    assert body["cells"][1]["correct_value"] == 1


def test_demo_verify_wrong_answer_count(admin_client) -> None:
    response = admin_client.post("/admin/value-table-demo/verify", json={"answers": ["-3"]})
    assert response.status_code == 422

"""Tests unitaires du socle `editorial_exercise` (ticket #17) : sérialisation, validation
de configuration, représentation publique, absence de fuite de réponse, correction."""

import pytest

from app.editorial_exercise import (
    EditorialExerciseBlockConfig,
    EditorialExerciseItem,
    EditorialExerciseValidationError,
    check_editorial_answer,
)


def _single_choice_item(**overrides):
    defaults = {
        "exercise_id": "q1",
        "type": "single_choice",
        "prompt": "La RAM est-elle volatile ?",
        "choices": ["Oui", "Non", "Cela dépend"],
        "correct_index": 0,
        "explanation": "La RAM perd son contenu à l'extinction du PC.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


def _true_false_item(**overrides):
    defaults = {
        "exercise_id": "q2",
        "type": "true_false",
        "prompt": "Un SSD a des pièces mécaniques.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 1,
        "explanation": "Un SSD utilise de la mémoire flash NAND, sans pièce mécanique.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


def _short_answer_item(**overrides):
    defaults = {
        "exercise_id": "q3",
        "type": "short_answer",
        "prompt": "Sigle anglais de la mémoire vive ?",
        "accepted_answers": ["RAM", "Random Access Memory"],
        "explanation": "RAM = Random Access Memory.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


def _classification_item(**overrides):
    defaults = {
        "exercise_id": "q4",
        "type": "classification",
        "prompt": "Classe chaque composant.",
        "categories": ["Matériel", "Logiciel"],
        "elements": ["Carte graphique", "Navigateur", "RAM"],
        "correct_categories": [0, 1, 0],
        "explanation": "Le matériel est physique, le logiciel est un programme.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


def _ordering_item(**overrides):
    defaults = {
        "exercise_id": "q5",
        "type": "ordering",
        "prompt": "Remets les étapes dans l'ordre.",
        "order_items": ["Affichage", "Lecture SSD", "Exécution CPU", "Chargement RAM"],
        "correct_order": [1, 3, 2, 0],
        "explanation": "Lecture, chargement, exécution, affichage.",
    }
    defaults.update(overrides)
    return EditorialExerciseItem(**defaults)


# --- Validation de configuration ---------------------------------------------------------


def test_item_requires_exercise_id():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(exercise_id="")


def test_item_rejects_unknown_type():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(type="essay")


def test_item_rejects_empty_prompt():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(prompt="   ")


def test_item_rejects_non_positive_points():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(points=0)


def test_choice_item_requires_at_least_two_choices():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(choices=["Seule option"])


def test_choice_item_requires_valid_correct_index():
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(correct_index=5)
    with pytest.raises(EditorialExerciseValidationError):
        _single_choice_item(correct_index=None)


def test_short_answer_requires_accepted_answers():
    with pytest.raises(EditorialExerciseValidationError):
        _short_answer_item(accepted_answers=[])


def test_classification_requires_at_least_two_categories():
    with pytest.raises(EditorialExerciseValidationError):
        _classification_item(categories=["Matériel"])


def test_classification_requires_at_least_two_elements():
    with pytest.raises(EditorialExerciseValidationError):
        _classification_item(elements=["Seul élément"], correct_categories=[0])


def test_classification_requires_correct_categories_matching_elements_length():
    with pytest.raises(EditorialExerciseValidationError):
        _classification_item(correct_categories=[0, 1])  # 3 éléments, 2 réponses


def test_classification_rejects_out_of_range_category_index():
    with pytest.raises(EditorialExerciseValidationError):
        _classification_item(correct_categories=[0, 5, 0])


def test_ordering_requires_at_least_two_items():
    with pytest.raises(EditorialExerciseValidationError):
        _ordering_item(order_items=["Seul élément"], correct_order=[0])


def test_ordering_rejects_non_permutation_correct_order():
    with pytest.raises(EditorialExerciseValidationError):
        _ordering_item(correct_order=[0, 1, 2, 2])  # doublon, 3 absent
    with pytest.raises(EditorialExerciseValidationError):
        _ordering_item(correct_order=[0, 1, 2])  # longueur incorrecte


def test_block_rejects_duplicate_exercise_ids():
    with pytest.raises(EditorialExerciseValidationError):
        EditorialExerciseBlockConfig(
            items=[_single_choice_item(exercise_id="dup"), _true_false_item(exercise_id="dup")]
        )


def test_block_rejects_unknown_mode():
    with pytest.raises(EditorialExerciseValidationError):
        EditorialExerciseBlockConfig(mode="quiz", items=[_single_choice_item()])


# --- Sérialisation / désérialisation ------------------------------------------------------


def test_to_json_from_json_roundtrip():
    config = EditorialExerciseBlockConfig(
        mode="practice",
        items=[
            _single_choice_item(),
            _true_false_item(),
            _short_answer_item(),
            _classification_item(),
            _ordering_item(),
        ],
    )
    restored = EditorialExerciseBlockConfig.from_json(config.to_json())

    assert restored.mode == "practice"
    assert [item.exercise_id for item in restored.items] == ["q1", "q2", "q3", "q4", "q5"]
    assert restored.get_item("q1").correct_index == 0
    assert restored.get_item("q3").accepted_answers == ["RAM", "Random Access Memory"]
    assert restored.get_item("q4").correct_categories == [0, 1, 0]
    assert restored.get_item("q5").correct_order == [1, 3, 2, 0]


def test_from_json_empty_or_malformed_returns_empty_config():
    assert EditorialExerciseBlockConfig.from_json("").items == []
    assert EditorialExerciseBlockConfig.from_json("not json").items == []
    assert EditorialExerciseBlockConfig.from_json("{}").mode == "practice"


def test_from_json_skips_invalid_items_without_raising():
    """Un contenu admin mal formé (JSON valide mais item structurellement invalide) ne
    doit jamais faire planter le chargement — l'item invalide est simplement ignoré."""
    raw = (
        '{"mode": "practice", "items": ['
        '{"exercise_id": "valid", "type": "true_false", "prompt": "x", '
        '"choices": ["Vrai", "Faux"], "correct_index": 0}, '
        '{"exercise_id": "invalid", "type": "unknown_type", "prompt": "y"}'
        "]}"
    )
    config = EditorialExerciseBlockConfig.from_json(raw)
    assert [item.exercise_id for item in config.items] == ["valid"]


def test_from_json_falls_back_to_practice_for_invalid_mode():
    raw = '{"mode": "not-a-mode", "items": []}'
    assert EditorialExerciseBlockConfig.from_json(raw).mode == "practice"


# --- Représentation publique : jamais la solution ------------------------------------------


def test_item_public_dict_never_leaks_solution():
    for item in (
        _single_choice_item(),
        _true_false_item(),
        _short_answer_item(),
        _classification_item(),
        _ordering_item(),
    ):
        public = item.to_public_dict()
        assert "correct_index" not in public
        assert "accepted_answers" not in public
        assert "correct_categories" not in public
        assert "correct_order" not in public
        assert "explanation" not in public


def test_classification_public_dict_includes_categories_and_elements_but_not_answer():
    public = _classification_item().to_public_dict()
    assert public["categories"] == ["Matériel", "Logiciel"]
    assert public["elements"] == ["Carte graphique", "Navigateur", "RAM"]
    assert "correct_categories" not in public


def test_ordering_public_dict_includes_order_items_but_not_correct_order():
    public = _ordering_item().to_public_dict()
    assert public["order_items"] == ["Affichage", "Lecture SSD", "Exécution CPU", "Chargement RAM"]
    assert "correct_order" not in public


def test_block_public_dict_never_leaks_solution():
    config = EditorialExerciseBlockConfig(
        items=[
            _single_choice_item(),
            _true_false_item(),
            _short_answer_item(),
            _classification_item(),
            _ordering_item(),
        ]
    )
    public = config.to_public_dict()
    serialized = str(public)
    assert "correct_index" not in serialized
    assert "accepted_answers" not in serialized
    assert "correct_categories" not in serialized
    assert "correct_order" not in serialized
    assert "explanation" not in serialized
    # "RAM" apparaît légitimement dans l'énoncé (prompt) de q1/q3 — on vérifie plutôt que
    # la valeur de la réponse acceptée de q3 (le champ lui-même déjà vérifié ci-dessus)
    # n'apparaît pas hors de ce contexte : "Random Access Memory" n'est présent nulle part.
    assert "Random Access Memory" not in serialized


def test_choice_public_dict_includes_choices_but_not_answer():
    public = _single_choice_item().to_public_dict()
    assert public["choices"] == ["Oui", "Non", "Cela dépend"]


def test_short_answer_public_dict_has_no_choices_key():
    public = _short_answer_item().to_public_dict()
    assert "choices" not in public


# --- Correction : bonne réponse / mauvaise réponse / id invalide --------------------------


def test_check_editorial_answer_correct_choice():
    config = EditorialExerciseBlockConfig(items=[_single_choice_item()])
    correction = check_editorial_answer(config, "q1", "0")
    assert correction.correct is True
    assert correction.correct_answer == "Oui"
    assert correction.explanation


def test_check_editorial_answer_incorrect_choice():
    config = EditorialExerciseBlockConfig(items=[_single_choice_item()])
    correction = check_editorial_answer(config, "q1", "1")
    assert correction.correct is False
    assert correction.correct_answer == "Oui"


def test_check_editorial_answer_true_false():
    config = EditorialExerciseBlockConfig(items=[_true_false_item()])
    assert check_editorial_answer(config, "q2", "1").correct is True
    assert check_editorial_answer(config, "q2", "0").correct is False


def test_check_editorial_answer_short_answer_normalized_match():
    config = EditorialExerciseBlockConfig(items=[_short_answer_item()])
    assert check_editorial_answer(config, "q3", "ram").correct is True
    assert check_editorial_answer(config, "q3", "  Ram  ").correct is True
    assert check_editorial_answer(config, "q3", "random access memory").correct is True
    assert check_editorial_answer(config, "q3", "mémoire vive").correct is False
    assert check_editorial_answer(config, "q3", "").correct is False


def test_check_editorial_answer_malformed_choice_answer_is_incorrect_not_an_error():
    config = EditorialExerciseBlockConfig(items=[_single_choice_item()])
    correction = check_editorial_answer(config, "q1", "not-a-number")
    assert correction.correct is False


def test_check_editorial_answer_unknown_exercise_id_returns_none():
    config = EditorialExerciseBlockConfig(items=[_single_choice_item()])
    assert check_editorial_answer(config, "does-not-exist", "0") is None


# --- Correction : classification -----------------------------------------------------------


def test_check_editorial_answer_classification_correct():
    config = EditorialExerciseBlockConfig(items=[_classification_item()])
    correction = check_editorial_answer(config, "q4", [0, 1, 0])
    assert correction.correct is True
    assert "Carte graphique" in correction.correct_answer
    assert "Matériel" in correction.correct_answer


def test_check_editorial_answer_classification_incorrect():
    config = EditorialExerciseBlockConfig(items=[_classification_item()])
    assert check_editorial_answer(config, "q4", [1, 1, 0]).correct is False


def test_check_editorial_answer_classification_incomplete_is_incorrect_not_an_error():
    config = EditorialExerciseBlockConfig(items=[_classification_item()])
    assert check_editorial_answer(config, "q4", [0, 1]).correct is False
    assert check_editorial_answer(config, "q4", []).correct is False


def test_check_editorial_answer_classification_wrong_type_is_incorrect_not_an_error():
    config = EditorialExerciseBlockConfig(items=[_classification_item()])
    assert check_editorial_answer(config, "q4", "not-a-list").correct is False
    assert check_editorial_answer(config, "q4", None).correct is False
    assert check_editorial_answer(config, "q4", ["a", "b", "c"]).correct is False


# --- Correction : ordering ------------------------------------------------------------------


def test_check_editorial_answer_ordering_correct():
    config = EditorialExerciseBlockConfig(items=[_ordering_item()])
    correction = check_editorial_answer(config, "q5", [1, 3, 2, 0])
    assert correction.correct is True
    assert correction.correct_answer.startswith("1. Lecture SSD")


def test_check_editorial_answer_ordering_incorrect_valid_permutation():
    config = EditorialExerciseBlockConfig(items=[_ordering_item()])
    assert check_editorial_answer(config, "q5", [0, 1, 2, 3]).correct is False


def test_check_editorial_answer_ordering_incomplete_is_incorrect_not_an_error():
    config = EditorialExerciseBlockConfig(items=[_ordering_item()])
    assert check_editorial_answer(config, "q5", [1, 3, 2]).correct is False
    assert check_editorial_answer(config, "q5", []).correct is False


def test_check_editorial_answer_ordering_malformed_not_a_permutation_is_incorrect():
    """Doublon/valeur hors bornes : une réponse structurellement invalide, pas une
    permutation valide de order_items — traitée comme une réponse incorrecte, pas une
    erreur serveur."""
    config = EditorialExerciseBlockConfig(items=[_ordering_item()])
    assert check_editorial_answer(config, "q5", [1, 1, 2, 0]).correct is False
    assert check_editorial_answer(config, "q5", [1, 3, 2, 9]).correct is False
    assert check_editorial_answer(config, "q5", "not-a-list").correct is False


def test_correction_to_dict_shape():
    config = EditorialExerciseBlockConfig(items=[_short_answer_item()])
    correction = check_editorial_answer(config, "q3", "RAM")
    data = correction.to_dict()
    for key in [
        "exercise_id",
        "correct",
        "correct_answer",
        "correct_answer_html",
        "explanation",
        "explanation_html",
    ]:
        assert key in data

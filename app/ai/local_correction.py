"""Correction locale et déterministe des types de question qui n'en ont pas besoin par
IA (ticket #23) : `single_choice`, `multiple_choice`, `true_false`, `matching`,
`classification`, `ordering`, `numeric`, `fill_blank`, et `short_answer`/`vocabulary`
lorsque leur rubric fournit `accepted_answers`.

Même principe de sécurité que le reste du projet (`app/answer_checking.py`,
`app/editorial_exercise.py`) : comparaison exacte après normalisation, aucun `eval()`,
aucune réponse malformée ne remonte d'exception — traitée comme incorrecte. Aucun de ces
types ne déclenche jamais d'appel réseau vers un fournisseur IA (voir
`app/ai/questionnaire.py::correct_questionnaire`, qui n'invoque le fournisseur que pour le
sous-ensemble de questions qui en ont réellement besoin).
"""

from fractions import Fraction
from typing import Any

from app.ai.schemas import (
    CONDITIONALLY_LOCAL_QUESTION_TYPES,
    DETERMINISTIC_QUESTION_TYPES,
    QuestionCorrection,
    QuestionnaireQuestion,
)
from app.answer_checking import parse_answer, text_answer_matches


def requires_ai_correction(question: QuestionnaireQuestion) -> bool:
    """Vrai si cette question doit être corrigée par le fournisseur IA plutôt que
    localement — voir `QuestionnaireQuestion.requires_ai_correction` (méthode équivalente,
    dupliquée ici comme fonction libre pour rester utilisable sans instance dans
    `app/ai/questionnaire.py`)."""
    return question.requires_ai_correction()


def _as_int_list(value: Any) -> list[int] | None:
    if not isinstance(value, list):
        return None
    try:
        return [int(item) for item in value]
    except (TypeError, ValueError):
        return None


def _check_single_or_true_false(question: QuestionnaireQuestion, submitted: Any) -> bool:
    try:
        return int(submitted) == question.correct_indexes[0]
    except (TypeError, ValueError):
        return False


def _check_multiple_choice(question: QuestionnaireQuestion, submitted: Any) -> bool:
    indexes = _as_int_list(submitted)
    if indexes is None:
        return False
    return sorted(set(indexes)) == sorted(set(question.correct_indexes))


def _check_ordering(question: QuestionnaireQuestion, submitted: Any) -> bool:
    indexes = _as_int_list(submitted)
    if indexes is None or len(indexes) != len(question.order_items):
        return False
    if sorted(indexes) != list(range(len(question.order_items))):
        return False
    return indexes == question.correct_order


# --- Crédit partiel (ticket #70, § B) — classification/matching uniquement -------------------
#
# Remplace les anciens vérificateurs booléens all-or-nothing (`indexes ==
# question.correct_categories`/`correct_pairs`) — `correct` (booléen, 100% exact) reste
# dérivé de la même comparaison exacte, seul `points_awarded` change désormais.
#
# `ordering` en est délibérément EXCLU (§ AUDIT du ticket : « auditer avant d'appliquer un
# crédit partiel naïf ») : un crédit partiel position-par-position serait TROMPEUR pour un
# ordonnancement — ex. attendu [A, B, C, D], soumis [B, A, C, D] (une seule inversion
# adjacente, intuitivement « presque juste ») ne score que 2/4 en comparaison position par
# position, alors qu'un décalage global comme [D, A, B, C] (chaque élément à la bonne
# position RELATIVE, juste décalé d'un cran) scorerait 0/4 — sous-évaluant fortement une
# réponse presque correcte. Une métrique honnête (paires adjacentes correctement
# ordonnées, ou plus proche sous-séquence commune) est une vraie décision pédagogique,
# hors du périmètre minimal de ce ticket — documentée ici, non implémentée.


def _partial_credit_classification(question: QuestionnaireQuestion, submitted: Any) -> Fraction:
    """Fraction d'éléments correctement classés (ex. 2 corrects sur 4 → 1/2) — jamais
    all-or-nothing. Position par position, chaque élément a une seule bonne catégorie
    (contrairement à `ordering`, une classification n'a pas d'effet de cascade entre
    éléments : reclasser l'élément 1 ne change jamais la bonne réponse de l'élément 2)."""
    indexes = _as_int_list(submitted)
    total = len(question.elements)
    if indexes is None or len(indexes) != total or total == 0:
        return Fraction(0)
    correct = sum(
        1 for given, expected in zip(indexes, question.correct_categories, strict=True) if given == expected
    )
    return Fraction(correct, total)


def _partial_credit_matching(question: QuestionnaireQuestion, submitted: Any) -> Fraction:
    """Même principe que `_partial_credit_classification`, pour `matching` — chaque paire
    gauche/droite est indépendante des autres."""
    indexes = _as_int_list(submitted)
    total = len(question.pairs_left)
    if indexes is None or len(indexes) != total or total == 0:
        return Fraction(0)
    correct = sum(
        1 for given, expected in zip(indexes, question.correct_pairs, strict=True) if given == expected
    )
    return Fraction(correct, total)


_PARTIAL_CREDIT_CHECKERS = {
    "classification": _partial_credit_classification,
    "matching": _partial_credit_matching,
}


def _check_numeric(question: QuestionnaireQuestion, submitted: Any) -> bool:
    if question.numeric_answer is None:
        return False
    if isinstance(submitted, (int, float)) and not isinstance(submitted, bool):
        value: Fraction | None = Fraction(str(submitted))
    elif isinstance(submitted, str):
        value = parse_answer(submitted)
    else:
        value = None
    if value is None:
        return False
    # str(...) plutôt que Fraction(float) directement : évite les artefacts de précision
    # binaire (ex. Fraction(0.1) != Fraction("0.1")) — même précaution que le reste du
    # module pour toute conversion float -> Fraction.
    expected = Fraction(str(question.numeric_answer))
    tolerance = Fraction(str(question.numeric_tolerance))
    return abs(value - expected) <= tolerance


def _check_text(question: QuestionnaireQuestion, submitted: Any) -> bool:
    if not isinstance(submitted, str):
        return False
    return text_answer_matches(question.accepted_answers, submitted)


_CHECKERS = {
    "single_choice": _check_single_or_true_false,
    "true_false": _check_single_or_true_false,
    "multiple_choice": _check_multiple_choice,
    "ordering": _check_ordering,
    "numeric": _check_numeric,
    "fill_blank": _check_text,
    "short_answer": _check_text,
    "vocabulary": _check_text,
}


def _expected_answer_display(question: QuestionnaireQuestion) -> str:
    if question.type in ("single_choice", "true_false") and question.correct_indexes:
        return question.choices[question.correct_indexes[0]]
    if question.type == "multiple_choice" and question.correct_indexes:
        return ", ".join(question.choices[i] for i in sorted(question.correct_indexes))
    if question.type == "ordering" and question.correct_order:
        return "\n".join(
            f"{position + 1}. {question.order_items[item_index]}"
            for position, item_index in enumerate(question.correct_order)
        )
    if question.type == "classification" and question.correct_categories:
        pairs = zip(question.elements, question.correct_categories, strict=True)
        return "\n".join(
            f"- {element} → {question.categories[category_index]}"
            for element, category_index in pairs
        )
    if question.type == "matching" and question.correct_pairs:
        pairs = zip(question.pairs_left, question.correct_pairs, strict=True)
        return "\n".join(
            f"- {left} → {question.pairs_right[right_index]}" for left, right_index in pairs
        )
    if question.type == "numeric" and question.numeric_answer is not None:
        return str(question.numeric_answer)
    if question.type in ("fill_blank", "short_answer", "vocabulary") and question.accepted_answers:
        return question.accepted_answers[0]
    return ""


def correct_locally(question: QuestionnaireQuestion, submitted: Any) -> QuestionCorrection:
    """Corrige localement une question déterministe. Ne doit être appelée que si
    `requires_ai_correction(question)` est faux — sinon lève `ValueError` (erreur de
    programmation de l'appelant, jamais un cas d'usage normal)."""
    if requires_ai_correction(question):
        raise ValueError(
            f"{question.question_id} : type {question.type!r} nécessite une correction IA, "
            "pas locale."
        )

    partial_checker = _PARTIAL_CREDIT_CHECKERS.get(question.type)
    if partial_checker is not None:
        fraction = partial_checker(question, submitted)
        # `fraction.denominator` n'est PAS le nombre d'éléments (ex. 2/4 se réduit à 1/2)
        # — recalculé séparément pour un message lisible (« 2/4 »).
        total_items = len(question.elements) if question.type == "classification" else len(question.pairs_left)
        correct_items = round(float(fraction) * total_items) if total_items else 0
        correct = fraction == 1
        points_awarded = round(float(question.points_max) * float(fraction), 4)
        return QuestionCorrection(
            question_id=question.question_id,
            points_awarded=points_awarded,
            points_max=question.points_max,
            correct=correct,
            strengths=(
                [f"{correct_items}/{total_items} élément(s) correctement associé(s)."]
                if correct_items > 0 else []
            ),
            errors=(
                [] if correct
                else [f"{total_items - correct_items}/{total_items} élément(s) mal associé(s)."]
            ),
            missing=[],
            feedback=(
                "Correction automatique déterministe avec crédit partiel "
                f"({correct_items}/{total_items} corrects) — pas d'appel IA nécessaire."
            ),
            expected_answer=_expected_answer_display(question),
        )

    checker = _CHECKERS.get(question.type)
    if checker is None:
        # Défense en profondeur : ne devrait jamais arriver (couvert par
        # DETERMINISTIC_QUESTION_TYPES ∪ CONDITIONALLY_LOCAL_QUESTION_TYPES ∪
        # ALWAYS_SEMANTIC_QUESTION_TYPES == QUESTION_TYPES, vérifié par test).
        raise ValueError(f"{question.question_id} : aucun correcteur local pour {question.type!r}.")

    correct = checker(question, submitted)
    return QuestionCorrection(
        question_id=question.question_id,
        points_awarded=question.points_max if correct else 0.0,
        points_max=question.points_max,
        correct=correct,
        strengths=[] if not correct else ["Réponse correcte."],
        errors=[] if correct else ["Réponse incorrecte."],
        missing=[],
        feedback="Correction automatique déterministe (pas d'appel IA nécessaire).",
        expected_answer=_expected_answer_display(question),
    )


# Garde-fou à l'import : `_CHECKERS` (all-or-nothing) ∪ `_PARTIAL_CREDIT_CHECKERS`
# (crédit partiel, ticket #70 § B) doit couvrir exactement les types corrigeables
# localement (déterministes + conditionnellement locaux) — ni plus, ni moins, sans
# chevauchement entre les deux (classification/matching sont dans l'un OU l'autre,
# jamais les deux à la fois).
assert not (set(_CHECKERS) & set(_PARTIAL_CREDIT_CHECKERS))
assert (
    set(_CHECKERS) | set(_PARTIAL_CREDIT_CHECKERS)
) == DETERMINISTIC_QUESTION_TYPES | CONDITIONALLY_LOCAL_QUESTION_TYPES

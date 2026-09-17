"""Pont entre la banque V1 (registre #40, `app/v1/question_engine.py`/`question_types.py`)
et le moteur de génération/correction par lots déjà construit et validé en conditions
réelles (ticket #23, `app.ai.questionnaire`/`app.ai.schemas`) — ticket #55 (MVP urgent).

Pourquoi un pont plutôt qu'un nouveau moteur IA : le ticket #55 condense volontairement
#41/#42/#43/#44 pour livrer un parcours réellement utilisable avant les épreuves. Le
moteur `app.ai.questionnaire.generate_questionnaire`/`correct_questionnaire` est déjà
écrit, testé et validé avec un vrai fournisseur en staging (ticket #31) — l'utiliser tel
quel pour la génération/correction, plutôt que de réécrire cette logique pour le format
`content_json` du registre #40, réduit le risque avant une échéance fixe. Le registre #40
reste l'autorité pour le STOCKAGE en banque (validation, `public_payload()` anti-fuite) ;
ce module ne fait que convertir entre les deux représentations pour les 7 types utilisés
par la composition MVP (voir `BRIDGE_TYPES`).

Aucun second mécanisme de correction n'est créé : `correct_questionnaire` reste le seul
point d'appel réseau, appelé au plus une fois par soumission de session (voir
`app/v1/session_service.py`)."""

from typing import Any

from app.ai.schemas import QuestionnaireQuestion

# Types de composition du MVP (#55, § COMPOSITION) — les seuls que ce pont sait
# convertir. Les types visuels/#48 ne sont ni générés ni corrigés par ce chemin.
BRIDGE_TYPES = frozenset(
    {"multiple_choice", "classification", "ordering", "short_answer", "vocabulary", "diagnostic", "long_answer"}
)

_SEMANTIC_RUBRIC_TYPES = frozenset({"diagnostic", "long_answer"})


class BridgeError(ValueError):
    """Type non pris en charge par le pont, ou contenu structurellement incompatible."""


def content_to_questionnaire_question(
    *, question_id: str, question_type: str, content: dict[str, Any], points_max: float
) -> QuestionnaireQuestion:
    """Convertit un `content_json` (forme du registre #40) en `QuestionnaireQuestion`
    (forme du contrat #23) — utilisé pour construire le `Questionnaire` soumis à
    `correct_questionnaire` lors de la soumission d'une session."""
    if question_type == "multiple_choice":
        options = content["options"]
        option_ids = [o["option_id"] for o in options]
        correct_indexes = [option_ids.index(oid) for oid in content["correct_option_ids"]]
        return QuestionnaireQuestion(
            question_id=question_id,
            type="multiple_choice",
            prompt=content["prompt"],
            points_max=points_max,
            choices=[o["label"] for o in options],
            correct_indexes=correct_indexes,
        )
    if question_type == "classification":
        return QuestionnaireQuestion(
            question_id=question_id,
            type="classification",
            prompt=content["prompt"],
            points_max=points_max,
            categories=list(content["categories"]),
            elements=list(content["elements"]),
            correct_categories=list(content["correct_categories"]),
        )
    if question_type == "ordering":
        items = content["items"]
        item_ids = [i["id"] for i in items]
        correct_order = [item_ids.index(iid) for iid in content["correct_order"]]
        return QuestionnaireQuestion(
            question_id=question_id,
            type="ordering",
            prompt=content["prompt"],
            points_max=points_max,
            order_items=[i["label"] for i in items],
            correct_order=correct_order,
        )
    if question_type in ("short_answer", "vocabulary"):
        return QuestionnaireQuestion(
            question_id=question_id,
            type=question_type,
            prompt=content["prompt"],
            points_max=points_max,
            accepted_answers=list(content.get("accepted_answers", [])),
            rubric=content.get("rubric", ""),
        )
    if question_type in _SEMANTIC_RUBRIC_TYPES:
        rubric = content.get("rubric", "").strip()
        extra_points = content.get("expected_points") or content.get("critical_points") or []
        if extra_points:
            rubric = f"{rubric}\nPoints attendus : {'; '.join(extra_points)}".strip()
        return QuestionnaireQuestion(
            question_id=question_id,
            type=question_type,
            prompt=content["prompt"],
            points_max=points_max,
            rubric=rubric or "Grille de correction non renseignée.",
        )
    raise BridgeError(f"Type non pris en charge par le pont IA : {question_type!r}.")


def questionnaire_question_to_content(question: QuestionnaireQuestion) -> dict[str, Any]:
    """Convertit une `QuestionnaireQuestion` générée par l'IA en `content_json` conforme
    au registre #40 — toujours revalidé par `app.v1.question_engine.validate_content`
    avant persistance (voir `app/v1/bank.py`), jamais stocké sans repasser par le
    registre."""
    if question.type == "multiple_choice":
        options = [
            {"option_id": str(index), "label": choice}
            for index, choice in enumerate(question.choices)
        ]
        correct_option_ids = [str(index) for index in question.correct_indexes]
        selection_count = len(correct_option_ids) or 1
        return {
            "prompt": question.prompt,
            "options": options,
            "min_selections": selection_count,
            "max_selections": selection_count,
            "correct_option_ids": correct_option_ids,
        }
    if question.type == "classification":
        return {
            "prompt": question.prompt,
            "categories": list(question.categories),
            "elements": list(question.elements),
            "correct_categories": list(question.correct_categories),
        }
    if question.type == "ordering":
        items = [{"id": f"item{index}", "label": label} for index, label in enumerate(question.order_items)]
        correct_order = [items[index]["id"] for index in question.correct_order]
        return {"prompt": question.prompt, "items": items, "correct_order": correct_order}
    if question.type in ("short_answer", "vocabulary"):
        return {
            "prompt": question.prompt,
            "accepted_answers": list(question.accepted_answers),
            "rubric": question.rubric,
        }
    if question.type in _SEMANTIC_RUBRIC_TYPES:
        return {
            "prompt": question.prompt,
            "rubric": question.rubric or "Grille de correction générée automatiquement.",
        }
    raise BridgeError(f"Type non pris en charge par le pont IA : {question.type!r}.")


def answer_json_to_submitted(question_type: str, content: dict[str, Any], answer_json: dict[str, Any]) -> Any:
    """Convertit un `answer_json` (forme du registre #40) en la valeur `submitted` que
    `app.ai.local_correction`/`correct_questionnaire` attendent pour ce type."""
    if question_type == "multiple_choice":
        option_ids = [o["option_id"] for o in content["options"]]
        selected = answer_json.get("selected_option_ids", []) or []
        return [option_ids.index(oid) for oid in selected if oid in option_ids]
    if question_type == "classification":
        return list(answer_json.get("assignments", []) or [])
    if question_type == "ordering":
        item_ids = [i["id"] for i in content["items"]]
        order = answer_json.get("order", []) or []
        return [item_ids.index(iid) for iid in order if iid in item_ids]
    if question_type in ("short_answer", "vocabulary", "diagnostic", "long_answer"):
        return answer_json.get("text", "") or ""
    raise BridgeError(f"Type non pris en charge par le pont IA : {question_type!r}.")


def describe_submitted_answer(question_type: str, content: dict[str, Any], answer_json: dict[str, Any]) -> str:
    """Représentation humainement lisible de LA RÉPONSE DE L'UTILISATEUR (pas la
    solution) — utilisée uniquement dans l'écran de résultats, APRÈS correction (§ 55 :
    « pour classification/ordering/QCM, la réponse donnée par l'utilisateur doit rester
    clairement visible après correction »). Ne lève jamais d'exception sur une réponse
    absente/malformée : affiche « (sans réponse) » plutôt que de faire échouer l'écran de
    résultats."""
    try:
        if question_type == "multiple_choice":
            labels = {o["option_id"]: o["label"] for o in content["options"]}
            selected = answer_json.get("selected_option_ids", []) or []
            chosen = [labels[oid] for oid in selected if oid in labels]
            return ", ".join(chosen) if chosen else "(sans réponse)"
        if question_type == "classification":
            elements = content["elements"]
            categories = content["categories"]
            assignments = answer_json.get("assignments", []) or []
            if len(assignments) != len(elements):
                return "(sans réponse)"
            return " ; ".join(
                f"{element} → {categories[category_index]}"
                for element, category_index in zip(elements, assignments, strict=True)
                if 0 <= category_index < len(categories)
            ) or "(sans réponse)"
        if question_type == "ordering":
            labels = {i["id"]: i["label"] for i in content["items"]}
            order = answer_json.get("order", []) or []
            chosen = [labels[iid] for iid in order if iid in labels]
            return " → ".join(chosen) if chosen else "(sans réponse)"
        if question_type in ("short_answer", "vocabulary", "diagnostic", "long_answer"):
            text = (answer_json.get("text") or "").strip()
            return text if text else "(sans réponse)"
    except (KeyError, IndexError, TypeError):
        return "(sans réponse)"
    return "(sans réponse)"

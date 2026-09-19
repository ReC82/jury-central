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

import random
from typing import Any

from app.ai.schemas import QuestionnaireQuestion
from app.v1.short_answer_limits import compute_short_answer_max_length

# Types de composition du MVP (#55, § COMPOSITION) — les seuls que ce pont sait
# convertir ET que la génération IA peut produire (`allowed_types`, voir
# `app/v1/session_service.py`). Les types visuels/#48 ne sont ni générés ni corrigés par
# ce chemin.
BRIDGE_TYPES = frozenset(
    {"multiple_choice", "classification", "ordering", "short_answer", "vocabulary", "diagnostic", "long_answer"}
)

# document_analysis / source_comparison (ticket #47, Français) : CORRECTION uniquement,
# jamais génération — le contrat #23 (`QuestionnaireQuestion.type`) n'a pas de notion de
# document, et une génération sans document réel existant n'aurait aucun sens (à quel
# document rattacher la question ?). Ces types sont donc exclus de `BRIDGE_TYPES` (jamais
# demandés à `generate_questionnaire`) mais gérés explicitement par
# `content_to_questionnaire_question`/`answer_json_to_submitted`/
# `describe_submitted_answer` pour que la CORRECTION (toujours nécessaire, banque
# hand-authored ou non) et l'affichage des résultats fonctionnent. Le texte du document
# n'est JAMAIS dupliqué ici : il est injecté une seule fois dans le contexte pédagogique
# de correction (voir `app/v1/session_service.py::submit_session`), pas répété par
# question — la question elle-même ne porte que `source_document_version_id(s)`
# (référence, jamais le texte).
DOCUMENT_TYPES = frozenset({"document_analysis", "source_comparison"})

# Types que ce pont sait décrire pour l'écran de résultats et parser depuis un formulaire
# de réponse — plus large que `BRIDGE_TYPES` (qui ne couvre que ce qui peut être généré).
CORRECTABLE_TYPES = BRIDGE_TYPES | DOCUMENT_TYPES

_SEMANTIC_RUBRIC_TYPES = frozenset({"diagnostic", "long_answer"})
_FREE_TEXT_ANSWER_TYPES = frozenset({"short_answer", "vocabulary", "diagnostic", "long_answer"}) | DOCUMENT_TYPES


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
    if question_type in DOCUMENT_TYPES:
        # Le contrat #23 n'a pas de type document_analysis/source_comparison propre :
        # mappé sur "long_answer" (réponse longue notée sur rubric) — le seul champ perdu
        # est `source_document_version_id(s)`, qui ne sert qu'à la référence/l'affichage,
        # jamais à la correction elle-même (le TEXTE du document est fourni une seule
        # fois via le contexte pédagogique, voir `submit_session`, jamais ici).
        rubric = content.get("rubric", "").strip()
        extra_points = content.get("expected_points") or []
        if extra_points:
            rubric = f"{rubric}\nPoints attendus : {'; '.join(extra_points)}".strip()
        return QuestionnaireQuestion(
            question_id=question_id,
            type="long_answer",
            prompt=content["prompt"],
            points_max=points_max,
            rubric=rubric or "Grille de correction non renseignée.",
        )
    raise BridgeError(f"Type non pris en charge par le pont IA : {question_type!r}.")


def shuffle_ordering_items(items: list[dict[str, Any]], correct_order: list[str]) -> list[dict[str, Any]]:
    """Mélange l'ordre d'AFFICHAGE de `items` (ticket #69 § 2 — bug réel constaté : les
    éléments d'une question `ordering` générée étaient parfois affichés directement dans
    le bon ordre, rendant l'exercice trivial : « il suffit de choisir 1, 2, 3, 4, 5, 6 »).

    Ne modifie JAMAIS `correct_order` (source de vérité privée, une liste d'`id` — pas de
    positions dans `items` — voir `OrderingContent`, `app.v1.question_types`) : seule la
    séquence PHYSIQUE de la liste `items` change, ce qui ne change ni les id/label de
    chaque élément ni la définition de la bonne réponse. Garantit que la séquence affichée
    ne correspond JAMAIS exactement à `correct_order`, sauf impossibilité mathématique
    (un seul élément) — reshuffle si le tirage aléatoire retombe sur l'ordre exact
    attendu (§ 2 : « si le shuffle retombe sur l'ordre exact attendu, reshuffle »), avec un
    filet de sécurité déterministe (rotation d'un cran) si le tirage aléatoire échoue à
    plusieurs reprises (espace de permutations minuscule, ex. 2 éléments)."""
    if len(items) < 2:
        return items
    shuffled = list(items)
    attempts = 0
    while [item["id"] for item in shuffled] == correct_order and attempts < 20:
        random.shuffle(shuffled)
        attempts += 1
    if [item["id"] for item in shuffled] == correct_order:
        shuffled = shuffled[1:] + shuffled[:1]
    return shuffled


def shuffle_multiple_choice_options(options: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mélange l'ordre d'AFFICHAGE de `options` (ticket #80, problème 1 — bug réel
    constaté : la bonne réponse apparaissait trop souvent en première position). Avant ce
    correctif, `options` était persisté dans exactement l'ordre fourni par le générateur/
    l'auteur — quel que soit `MultipleChoiceContent.shuffle` (champ exposé au client mais
    jamais réellement appliqué), et une IA ou un·e auteur·ice place très souvent la bonne
    réponse en premier par habitude, rendant sa position statistiquement prévisible.

    Ne modifie JAMAIS `option_id` (source de vérité de `correct_option_ids` — voir
    `MultipleChoiceContent`, `app.v1.question_types`) : chaque dict `{option_id, label}`
    reste intact, seule la séquence PHYSIQUE de la liste change. Contrairement à
    `shuffle_ordering_items`, aucune garantie « jamais dans l'ordre d'origine » n'est
    nécessaire ici : contrairement à un `ordering` qui devient trivial si affiché déjà
    trié, un QCM dont le tirage aléatoire laisse par hasard la bonne réponse en première
    position n'est pas un problème — seule la RÉPÉTITION SYSTÉMATIQUE en première
    position, sur l'ensemble des questions, est le bug à corriger."""
    if len(options) < 2:
        return options
    shuffled = list(options)
    random.shuffle(shuffled)
    return shuffled


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
        # Ticket #80 : mélange physique de l'ordre d'affichage — `option_id` reste
        # attaché à son `label`, donc `correct_option_ids` (déjà basé sur l'id, jamais la
        # position) reste valide sans changement.
        options = shuffle_multiple_choice_options(options)
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
        items = shuffle_ordering_items(items, correct_order)
        return {"prompt": question.prompt, "items": items, "correct_order": correct_order}
    if question.type in ("short_answer", "vocabulary"):
        # Ticket #85 : `max_length` n'était jamais fourni ici, donc retombait toujours
        # sur le défaut Pydantic fixe (200) quelle que soit la question — trop court pour
        # une réponse développée (ex. comparaison HDD/SSD SATA/SSD NVMe), inutilement
        # large pour un simple rappel factuel. Calculé à partir de la formulation exacte
        # de l'énoncé, jamais une valeur unique pour tous les `short_answer`.
        return {
            "prompt": question.prompt,
            "accepted_answers": list(question.accepted_answers),
            "rubric": question.rubric,
            "max_length": compute_short_answer_max_length(question.prompt),
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
    if question_type in _FREE_TEXT_ANSWER_TYPES:
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
        if question_type in _FREE_TEXT_ANSWER_TYPES:
            text = (answer_json.get("text") or "").strip()
            return text if text else "(sans réponse)"
    except (KeyError, IndexError, TypeError):
        return "(sans réponse)"
    return "(sans réponse)"

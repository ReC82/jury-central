"""Ticket #80 — position des bonnes réponses / fuite de réponse.

PROBLÈME 1 (multiple_choice) : la bonne réponse apparaissait trop souvent en première
position. Cause racine : `MultipleChoiceContent.shuffle` (champ exposé au client) n'était
JAMAIS réellement appliqué — `options` était persisté dans exactement l'ordre fourni par
le générateur/l'auteur, quel que soit ce champ. Corrigé par
`app.v1.ai_bridge.shuffle_multiple_choice_options`, appliqué au moment de la persistance
(mêmes deux points d'entrée que `shuffle_ordering_items`, #69) : conversion IA
(`questionnaire_question_to_content`) et import éditorial legacy MC01 (`app.v1.bank`).
`correct_option_ids` référence déjà `option_id`, jamais une position — donc rien à changer
côté vérité, seul l'ordre d'AFFICHAGE change.

PROBLÈME 2 (classification) : un élément pouvait contenir littéralement le mot qui
identifie sa propre catégorie parmi celles proposées (ex. « ... identifié comme NVMe... »
pour une catégorie « SSD NVMe » parmi HDD/SSD SATA/SSD NVMe) — aucun raisonnement requis.
Corrigé par `app.v1.quality_validation._check_classification_reveals_answer_label` : compare
les mots DISTINCTIFS de la bonne catégorie (mots qui n'apparaissent dans AUCUNE autre
catégorie proposée — jamais un mot générique partagé comme « SSD ») aux mots de l'élément.

Aucun appel OpenAI réel : `FakeAIProvider` partout, seeds déterministes pour les
vérifications statistiques."""

import random

from app.ai.schemas import QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.ai_bridge import (
    questionnaire_question_to_content,
    shuffle_multiple_choice_options,
)
from app.v1.bank import persist_generated_questions
from app.v1.quality_validation import validate_question_quality
from app.v1.question_engine import public_payload
from app.v1.question_types import MultipleChoiceContent

# =============================================================================================
# 1. shuffle_multiple_choice_options — unité, seeds déterministes
# =============================================================================================


def test_shuffle_preserves_option_id_label_pairing():
    random.seed(1)
    options = [
        {"option_id": "0", "label": "Alpha"}, {"option_id": "1", "label": "Beta"},
        {"option_id": "2", "label": "Gamma"}, {"option_id": "3", "label": "Delta"},
    ]
    shuffled = shuffle_multiple_choice_options(options)
    by_id = {o["option_id"]: o["label"] for o in shuffled}
    assert by_id == {"0": "Alpha", "1": "Beta", "2": "Gamma", "3": "Delta"}
    assert {o["option_id"] for o in shuffled} == {"0", "1", "2", "3"}


def test_shuffle_actually_changes_order_with_fixed_seed():
    """Seed déterministe (§ ticket) : avec cette graine précise, l'ordre change bien —
    non-régression explicite si `shuffle_multiple_choice_options` redevenait un no-op."""
    random.seed(7)
    options = [{"option_id": str(i), "label": f"Option {i}"} for i in range(6)]
    shuffled = shuffle_multiple_choice_options(list(options))
    assert [o["option_id"] for o in shuffled] != [o["option_id"] for o in options]


def test_shuffle_noop_below_two_options():
    assert shuffle_multiple_choice_options([]) == []
    single = [{"option_id": "0", "label": "Seule option"}]
    assert shuffle_multiple_choice_options(single) == single


def test_correct_answer_position_is_not_systematically_first():
    """§ ticket #80 : « bonne réponse possible en position 1, 2, 3, 4 » — vérifié
    statistiquement sur un grand nombre de tirages, seed fixée pour la reproductibilité."""
    random.seed(2024)
    position_counts = [0, 0, 0, 0]
    trials = 400
    for _ in range(trials):
        options = [
            {"option_id": "0", "label": "Bonne réponse"},
            {"option_id": "1", "label": "Distracteur B"},
            {"option_id": "2", "label": "Distracteur C"},
            {"option_id": "3", "label": "Distracteur D"},
        ]
        shuffled = shuffle_multiple_choice_options(options)
        position = next(i for i, o in enumerate(shuffled) if o["option_id"] == "0")
        position_counts[position] += 1

    # Distribution grossièrement uniforme (25% chacune) — jamais 100% en position 0 comme
    # avant le correctif. Marge large (chaque position doit apparaître au moins 10% du
    # temps) pour ne jamais rendre ce test flaky.
    for count in position_counts:
        assert count >= trials * 0.10, position_counts
    assert position_counts[0] < trials, "la bonne réponse ne doit plus JAMAIS être systématiquement en position 0"


# =============================================================================================
# 2. Truth liée à option_id, jamais à la position — vérifié après mélange
# =============================================================================================


def test_correctness_check_still_works_after_shuffle():
    random.seed(3)
    options = [{"option_id": str(i), "label": f"Option {i}"} for i in range(5)]
    shuffled = shuffle_multiple_choice_options(options)
    content = MultipleChoiceContent(
        prompt="Question test.", options=shuffled, correct_option_ids=["2"], min_selections=1, max_selections=1,
    )
    payload = public_payload("multiple_choice", 1, content.model_dump())
    # correct_option_ids n'est jamais exposé publiquement — seule la structure options/
    # option_id l'est, jamais une position.
    assert "correct_option_ids" not in payload
    option_ids_displayed = [o["option_id"] for o in payload["options"]]
    assert "2" in option_ids_displayed  # l'id correct est bien présent, peu importe où


def test_generated_multiple_choice_content_has_shuffled_options_baked_in():
    """`questionnaire_question_to_content` (conversion IA) applique bien le mélange —
    `correct_option_ids` reste cohérent avec `options` après conversion."""
    random.seed(9)
    question = QuestionnaireQuestion(
        question_id="q1", type="multiple_choice", points_max=1.0,
        prompt="Quelle est la bonne réponse ?",
        choices=["Bonne réponse", "Distracteur 1", "Distracteur 2", "Distracteur 3"],
        correct_indexes=[0],
    )
    content = questionnaire_question_to_content(question)
    option_ids = [o["option_id"] for o in content["options"]]
    assert content["correct_option_ids"] == ["0"]
    assert "0" in option_ids
    labels_by_id = {o["option_id"]: o["label"] for o in content["options"]}
    assert labels_by_id["0"] == "Bonne réponse"


def test_editorial_legacy_single_choice_conversion_shuffles_options():
    """Chemin d'import éditorial (§ ticket #80, contenu hand-authored — ex. MC01) : le
    mélange s'applique aussi à `_editorial_item_to_v1_content`, pas seulement à la
    génération IA. MC01 lui-même ne contient aucun exercice `single_choice` dans son
    contenu actuel (vérifié : long_answer/classification/diagnostic/ordering/vocabulary
    uniquement) — ce test construit donc directement un item éditorial synthétique pour
    exercer ce chemin de conversion précis, sans dépendre du contenu MC01 réel."""
    from app.editorial_exercise import EditorialExerciseItem
    from app.v1.bank import _editorial_item_to_v1_content

    random.seed(11)
    item = EditorialExerciseItem(
        exercise_id="synthetic-1", type="single_choice", prompt="Question factice à choix.",
        choices=["Bonne réponse", "Distracteur 1", "Distracteur 2", "Distracteur 3"],
        correct_index=0,
    )
    first_position_count = 0
    trials = 30
    for _ in range(trials):
        _, content = _editorial_item_to_v1_content(item)
        correct_ids = set(content["correct_option_ids"])
        labels_by_id = {o["option_id"]: o["label"] for o in content["options"]}
        assert labels_by_id[content["correct_option_ids"][0]] == "Bonne réponse"
        if content["options"][0]["option_id"] in correct_ids:
            first_position_count += 1
    # Sur 30 tirages, il serait extrêmement improbable (< 1/2^29) que la bonne réponse
    # reste TOUJOURS en position 0 si le mélange fonctionne réellement.
    assert first_position_count < trials, "la bonne réponse ne doit pas toujours rester en position 0"


# =============================================================================================
# 3. Fuite de réponse dans une classification — rejet à la validation qualité
# =============================================================================================


def test_classification_leaking_category_word_is_rejected():
    """Cas exact signalé dans le ticket."""
    content = {
        "prompt": "Classe chaque support de stockage selon sa technologie.",
        "categories": ["HDD mécanique", "SSD SATA", "SSD NVMe"],
        "elements": ["Le support flash est identifié comme NVMe sur un emplacement M.2 compatible."],
        "correct_categories": [2],
    }
    errors = validate_question_quality(None, None, "classification", content)
    assert errors
    assert "NVMe" in errors[0] or "nvme" in errors[0].lower()


def test_classification_without_leak_is_accepted():
    """Reformulations suggérées par le ticket — aucune fuite lexicale directe."""
    content = {
        "prompt": "Classe chaque support de stockage selon sa technologie.",
        "categories": ["HDD mécanique", "SSD SATA", "SSD NVMe"],
        "elements": [
            "Support flash au format 2,5 pouces relié par câble de données.",
            "Support flash installé directement sur carte mère via M.2/PCIe.",
            "Plateaux magnétiques et tête de lecture mécanique.",
        ],
        "correct_categories": [1, 2, 0],
    }
    assert validate_question_quality(None, None, "classification", content) == []


def test_classification_shared_word_between_categories_does_not_false_positive():
    """« SSD » seul, partagé par 2 catégories, ne doit JAMAIS suffire à déclencher un
    rejet — seul un mot qui identifie une SEULE catégorie parmi celles proposées compte."""
    content = {
        "prompt": "Classe chaque support selon sa technologie.",
        "categories": ["HDD mécanique", "SSD SATA", "SSD NVMe"],
        "elements": ["Ce support est un SSD, avec de bonnes performances générales."],
        "correct_categories": [1],
    }
    assert validate_question_quality(None, None, "classification", content) == []


def test_classification_leak_check_ignores_other_question_types():
    content = {
        "prompt": "Quel support est un SSD NVMe ?",
        "options": [{"option_id": "0", "label": "Support identifié NVMe sur M.2"}],
        "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
    }
    # multiple_choice n'est pas concerné par cette règle spécifique (seulement
    # classification) — aucune erreur levée par CE contrôle précis, même si le libellé
    # contient un terme technique (autres règles, ex. formulation molle, restent actives
    # séparément et sont testées ailleurs, #69).
    from app.v1.quality_validation import _check_classification_reveals_answer_label

    assert _check_classification_reveals_answer_label("multiple_choice", content) == []


# =============================================================================================
# 4. Bout en bout : persist_generated_questions rejette une classification qui fuite
# =============================================================================================


def test_persist_generated_questions_rejects_leaking_classification(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()

    leaking_question = QuestionnaireQuestion(
        question_id="leak-1", type="classification", points_max=1.0,
        prompt="Classe chaque support de stockage selon sa technologie.",
        categories=["HDD mécanique", "SSD SATA", "SSD NVMe"],
        elements=[
            "Le support flash est identifié comme NVMe sur un emplacement M.2 compatible.",
            "Plateaux magnétiques et tête de lecture mécanique.",
        ],
        correct_categories=[2, 0],
    )
    domain_rejections: list[str] = []
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[leaking_question],
        domain_rejections=domain_rejections,
    )
    assert persisted == []
    assert domain_rejections == ["classification"]

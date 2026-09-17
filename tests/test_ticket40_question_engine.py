"""Ticket #40 — Question Engine V1 : registre extensible des types de questions.

Aucun appel OpenAI réel (ce ticket ne construit ni génération ni correction IA — voir
`app.v1.question_engine.check_answer`, qui retourne `None` pour signaler qu'une
correction sémantique est nécessaire, sans jamais l'exécuter lui-même)."""

import json

import pytest

from app.v1 import question_types  # noqa: F401 — enregistre les 26 types
from app.v1.models import create_source_document
from app.v1.question_engine import (
    ContentValidationError,
    QuestionEngineError,
    check_answer,
    get_question_type,
    list_question_types,
    public_payload,
    validate_answer,
    validate_content,
)

EXPECTED_TYPE_IDS = {
    "multiple_choice",
    "true_false",
    "short_answer",
    "long_answer",
    "fill_blank",
    "matching",
    "classification",
    "ordering",
    "numeric",
    "diagnostic",
    "procedure",
    "vocabulary",
    "calculation",
    "formula",
    "graph_reading",
    "graph_interaction",
    "diagram_labeling",
    "image_identification",
    "hotspot",
    "table_completion",
    "document_analysis",
    "source_comparison",
    "timeline",
    "code_reading",
    "code_completion",
    "troubleshooting",
}

# Contenu minimal valide par type, avec un "canari" injecté dans chaque champ privé
# (rubric/explanation/correct_*) pour la vérification systématique anti-fuite (§ ci-dessous).
CANARY = "CANARY_SECRET_DO_NOT_LEAK"

MINIMAL_VALID_CONTENT: dict[str, dict] = {
    "multiple_choice": {
        "prompt": "Choisis les périphériques de sortie.",
        "options": [{"option_id": "a", "label": "Écran"}, {"option_id": "b", "label": "Clavier"}],
        "correct_option_ids": ["a"],
        "explanation": CANARY,
    },
    "true_false": {"prompt": "La RAM est volatile.", "correct_value": True, "explanation": CANARY},
    "short_answer": {"prompt": "Sigle de mémoire vive ?", "accepted_answers": [CANARY]},
    "long_answer": {"prompt": "Explique.", "rubric": CANARY, "expected_points": [CANARY]},
    "fill_blank": {
        "text_with_blanks": "La {{a}} est volatile.",
        "blanks": [{"blank_id": "a", "accepted_answers": [CANARY]}],
    },
    "matching": {
        "prompt": "Associe.",
        "left_items": [{"id": "l1", "label": "CPU"}, {"id": "l2", "label": "RAM"}],
        "right_items": [{"id": "r1", "label": "Calcul"}, {"id": "r2", "label": "Mémoire"}],
        "correct_pairs": {"l1": "r1", "l2": "r2"},
        "explanation": CANARY,
    },
    "classification": {
        "prompt": "Classe.",
        "categories": ["Matériel", "Logiciel"],
        "elements": ["Carte graphique", "Navigateur"],
        "correct_categories": [0, 1],
        "explanation": CANARY,
    },
    "ordering": {
        "prompt": "Ordonne.",
        "items": [{"id": "i1", "label": "Lecture"}, {"id": "i2", "label": "Exécution"}],
        "correct_order": ["i1", "i2"],
        "explanation": CANARY,
    },
    "numeric": {"prompt": "Combien ?", "expected_value": 42.0, "explanation": CANARY},
    "diagnostic": {"prompt": "Diagnostique.", "rubric": CANARY, "critical_points": [CANARY]},
    "procedure": {"prompt": "Décris la procédure.", "rubric": CANARY, "expected_steps": [CANARY]},
    "vocabulary": {"prompt": "Traduis RAM.", "accepted_answers": [CANARY]},
    "calculation": {"prompt": "Calcule.", "expected_value": 3.14, "rubric": CANARY},
    "formula": {"prompt": "Donne la formule.", "accepted_representations": [CANARY]},
    "graph_reading": {
        "prompt": "Lis le graphique.",
        "response_mode": "numeric",
        "expected_value": 10.0,
    },
    "graph_interaction": {
        "prompt": "Place le point.",
        "expected_points": [{"x": 0.5, "y": 0.5}],
    },
    "diagram_labeling": {
        "prompt": "Étiquette.",
        "zones": [{"zone_id": "z1", "marker": "A"}],
        "label_options": [{"id": "l1", "label": "CPU"}],
        "correct_mapping": {"z1": "l1"},
    },
    "image_identification": {
        "prompt": "Identifie.",
        "response_mode": "choice",
        "options": [{"option_id": "a", "label": "CPU"}, {"option_id": "b", "label": "GPU"}],
        "correct_option_ids": ["a"],
    },
    "hotspot": {
        "prompt": "Clique sur le CPU.",
        "zones": [{"zone_id": "z1", "x_min": 0.1, "y_min": 0.1, "x_max": 0.3, "y_max": 0.3}],
        "correct_zone_ids": ["z1"],
    },
    "table_completion": {
        "prompt": "Complète.",
        "headers": ["Composant", "Rôle"],
        "rows": [[{"cell_id": "c1", "value": "CPU"}, {"cell_id": "c2", "editable": True}]],
        "accepted_answers": {"c2": [CANARY]},
    },
    "document_analysis": {
        "prompt": "Analyse ce texte.",
        "source_document_version_id": 1,
        "rubric": CANARY,
        "expected_points": [CANARY],
    },
    "source_comparison": {
        "prompt": "Compare ces deux textes.",
        "source_document_version_ids": [1, 2],
        "rubric": CANARY,
        "expected_points": [CANARY],
    },
    "timeline": {
        "prompt": "Ordonne chronologiquement.",
        "events": [{"id": "e1", "label": "Boot"}, {"id": "e2", "label": "Login"}],
        "correct_order": ["e1", "e2"],
        "explanation": CANARY,
    },
    "code_reading": {
        "prompt": "Que fait ce code ?",
        "code": "print('hello')",
        "response_mode": "choice",
        "options": [{"option_id": "a", "label": "Affiche hello"}, {"option_id": "b", "label": "Rien"}],
        "correct_option_ids": ["a"],
    },
    "code_completion": {
        "prompt": "Complète le code.",
        "code_stimulus": "print(___)",
        "accepted_answers": [CANARY],
    },
    "troubleshooting": {
        "prompt": "Dépanne.",
        "rubric": CANARY,
        "critical_points": [CANARY],
        "forbidden_claims": [CANARY],
    },
}


# --- 1. Registre contient tous les types V1 attendus -----------------------------------------


def test_registry_contains_all_expected_v1_types():
    registered_ids = {spec.type_id for spec in list_question_types()}
    assert registered_ids == EXPECTED_TYPE_IDS


def test_minimal_content_fixture_covers_every_registered_type():
    """Garde-fou du fichier de test lui-même : toute évolution du registre doit venir
    avec un contenu minimal correspondant ci-dessus."""
    assert set(MINIMAL_VALID_CONTENT.keys()) == EXPECTED_TYPE_IDS


# --- 2. Type IDs uniques -----------------------------------------------------------------------


def test_type_ids_are_unique_and_registering_a_duplicate_fails():
    from app.v1.question_engine import QuestionTypeRegistry

    registry = QuestionTypeRegistry()
    spec = get_question_type("multiple_choice")
    registry.register(spec)
    with pytest.raises(QuestionEngineError):
        registry.register(spec)


# --- 3./5. Schema versions supportées / version inconnue refusée ------------------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_schema_version_1_is_supported_for_every_type(type_id):
    spec = get_question_type(type_id)
    assert 1 in spec.schema_versions


def test_unknown_schema_version_rejected():
    with pytest.raises(QuestionEngineError):
        validate_content("multiple_choice", 999, MINIMAL_VALID_CONTENT["multiple_choice"])


# --- 4. Type inconnu refusé ---------------------------------------------------------------------


def test_unknown_type_rejected():
    with pytest.raises(QuestionEngineError):
        get_question_type("does_not_exist")
    with pytest.raises(QuestionEngineError):
        validate_content("does_not_exist", 1, {})


# --- 6./7. Content valide accepté / invalide refusé (tous les types) --------------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_minimal_content_is_accepted_for_every_type(type_id):
    validate_content(type_id, 1, MINIMAL_VALID_CONTENT[type_id])


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_empty_content_is_rejected_for_every_type(type_id):
    with pytest.raises(ContentValidationError):
        validate_content(type_id, 1, {})


# --- 30. PUBLIC PAYLOAD ne contient jamais correct answers/rubric/solution ---------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_public_payload_never_leaks_the_canary_secret(type_id):
    content = MINIMAL_VALID_CONTENT[type_id]
    payload = public_payload(type_id, 1, content)
    serialized = json.dumps(payload, ensure_ascii=False)
    assert CANARY not in serialized, f"{type_id} fuit un champ privé dans public_payload()"


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_public_payload_always_reports_type_and_requires_ai_flag(type_id):
    payload = public_payload(type_id, 1, MINIMAL_VALID_CONTENT[type_id])
    assert payload["type"] == type_id
    assert isinstance(payload["requires_ai"], bool)


KNOWN_PRIVATE_FIELD_NAMES = {
    "correct_option_ids", "correct_value", "correct_categories", "correct_order",
    "correct_pairs", "correct_mapping", "correct_zone_ids", "accepted_answers",
    "accepted_representations", "rubric", "expected_points", "critical_points",
    "forbidden_claims", "expected_parameters", "expected_steps", "expected_value",
    "tolerance_abs", "tolerance_rel", "max_score",
}


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_public_payload_never_contains_known_private_field_names(type_id):
    payload = public_payload(type_id, 1, MINIMAL_VALID_CONTENT[type_id])
    leaked = KNOWN_PRIVATE_FIELD_NAMES & set(payload.keys())
    assert not leaked, f"{type_id} expose des clés privées : {leaked}"


# --- 9./10./11. multiple_choice : nombre variable d'options, réponse unique, multi -------------


def test_multiple_choice_supports_variable_number_of_options():
    content = {
        "prompt": "Choisis.",
        "options": [{"option_id": str(i), "label": f"Option {i}"} for i in range(6)],
        "correct_option_ids": ["0"],
    }
    validate_content("multiple_choice", 1, content)  # 2 options minimum déjà couvert ailleurs


def test_multiple_choice_single_answer_min_max_one():
    content = {
        "prompt": "Une seule bonne réponse.",
        "options": [{"option_id": "a", "label": "A"}, {"option_id": "b", "label": "B"}],
        "min_selections": 1,
        "max_selections": 1,
        "correct_option_ids": ["a"],
    }
    validate_content("multiple_choice", 1, content)
    assert check_answer("multiple_choice", 1, content, {"selected_option_ids": ["a"]}) is True
    assert check_answer("multiple_choice", 1, content, {"selected_option_ids": ["b"]}) is False


def test_multiple_choice_multi_answer_min_two_max_three():
    content = {
        "prompt": "2 ou 3 bonnes réponses.",
        "options": [{"option_id": str(i), "label": f"Option {i}"} for i in range(5)],
        "min_selections": 2,
        "max_selections": 3,
        "correct_option_ids": ["0", "1", "2"],
    }
    validate_content("multiple_choice", 1, content)
    assert check_answer("multiple_choice", 1, content, {"selected_option_ids": ["0", "1", "2"]}) is True
    assert check_answer("multiple_choice", 1, content, {"selected_option_ids": ["0"]}) is False


def test_multiple_choice_rejects_correct_ids_violating_min_max():
    content = {
        "prompt": "Incohérent.",
        "options": [{"option_id": "a", "label": "A"}, {"option_id": "b", "label": "B"}],
        "min_selections": 2,
        "max_selections": 2,
        "correct_option_ids": ["a"],
    }
    with pytest.raises(ContentValidationError):
        validate_content("multiple_choice", 1, content)


# --- 12. classification : catégories variables --------------------------------------------------


def test_classification_supports_variable_number_of_categories():
    content = {
        "prompt": "Classe.",
        "categories": ["A", "B", "C", "D", "E"],
        "elements": ["x", "y", "z"],
        "correct_categories": [0, 2, 4],
    }
    validate_content("classification", 1, content)
    assert check_answer("classification", 1, content, {"assignments": [0, 2, 4]}) is True
    assert check_answer("classification", 1, content, {"assignments": [0, 0, 0]}) is False


# --- 13. ordering ---------------------------------------------------------------------------------


def test_ordering_check_answer():
    content = MINIMAL_VALID_CONTENT["ordering"]
    assert check_answer("ordering", 1, content, {"order": ["i1", "i2"]}) is True
    assert check_answer("ordering", 1, content, {"order": ["i2", "i1"]}) is False


def test_ordering_rejects_non_permutation_correct_order():
    content = {
        "prompt": "x",
        "items": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
        "correct_order": ["a", "c"],
    }
    with pytest.raises(ContentValidationError):
        validate_content("ordering", 1, content)


# --- 14. matching ---------------------------------------------------------------------------------


def test_matching_check_answer():
    content = MINIMAL_VALID_CONTENT["matching"]
    assert check_answer("matching", 1, content, {"pairs": {"l1": "r1", "l2": "r2"}}) is True
    assert check_answer("matching", 1, content, {"pairs": {"l1": "r2", "l2": "r1"}}) is False


# --- 15. numeric : tolérance -----------------------------------------------------------------


def test_numeric_tolerance_absolute():
    content = {"prompt": "Combien ?", "expected_value": 10.0, "tolerance_abs": 0.5}
    assert check_answer("numeric", 1, content, {"raw_input": "10.4"}) is True
    assert check_answer("numeric", 1, content, {"raw_input": "10.6"}) is False


def test_numeric_tolerance_relative():
    content = {"prompt": "Combien ?", "expected_value": 100.0, "tolerance_rel": 0.05}
    assert check_answer("numeric", 1, content, {"raw_input": "104"}) is True
    assert check_answer("numeric", 1, content, {"raw_input": "106"}) is False


def test_numeric_unit_required():
    content = {
        "prompt": "Combien de watts ?",
        "expected_value": 750,
        "unit": "W",
        "unit_required": True,
    }
    assert check_answer("numeric", 1, content, {"raw_input": "750", "unit": "W"}) is True
    assert check_answer("numeric", 1, content, {"raw_input": "750", "unit": ""}) is False


def test_numeric_never_uses_eval():
    content = {"prompt": "x", "expected_value": 4.0}
    # Une entrée qui serait dangereuse si évaluée n'est jamais interprétée comme code.
    assert check_answer("numeric", 1, content, {"raw_input": "__import__('os')"}) is False


# --- 16. short_answer (local + bascule sémantique) -----------------------------------------------


def test_short_answer_local_correction_with_accepted_answers():
    content = {"prompt": "Sigle ?", "accepted_answers": ["RAM"]}
    assert check_answer("short_answer", 1, content, {"text": "ram"}) is True
    assert check_answer("short_answer", 1, content, {"text": "rom"}) is False


def test_short_answer_without_accepted_answers_requires_semantic_correction():
    content = {"prompt": "Explique brièvement.", "rubric": "Doit mentionner la volatilité."}
    assert check_answer("short_answer", 1, content, {"text": "n'importe quoi"}) is None
    payload = public_payload("short_answer", 1, content)
    assert payload["requires_ai"] is True


# --- 17./18./19. long_answer / diagnostic / procedure (toujours sémantiques) --------------------


@pytest.mark.parametrize("type_id", ["long_answer", "diagnostic", "procedure", "troubleshooting"])
def test_always_semantic_types_never_correct_locally(type_id):
    content = MINIMAL_VALID_CONTENT[type_id]
    assert check_answer(type_id, 1, content, {"text": "réponse quelconque"}) is None
    spec = get_question_type(type_id)
    assert spec.requires_semantic_correction(validate_content(type_id, 1, content)) is True


# --- 20. vocabulary ---------------------------------------------------------------------------


def test_vocabulary_local_and_semantic():
    local_content = {"prompt": "Traduis RAM.", "accepted_answers": ["mémoire vive"]}
    assert check_answer("vocabulary", 1, local_content, {"text": "Mémoire Vive"}) is True

    semantic_content = {"prompt": "Explique ce terme.", "rubric": "..."}
    assert check_answer("vocabulary", 1, semantic_content, {"text": "peu importe"}) is None


# --- 21. document_analysis avec SourceDocument --------------------------------------------------


def test_document_analysis_references_a_real_source_document_version(db_session):
    document = create_source_document(db_session, title="Texte", content_text="Il était une fois...")
    db_session.commit()

    content = {
        "prompt": "Résume ce texte.",
        "source_document_version_id": document.current_version_id,
        "rubric": CANARY,
    }
    validated = validate_content("document_analysis", 1, content)
    assert validated.source_document_version_id == document.current_version_id

    payload = public_payload("document_analysis", 1, content)
    assert payload["source_document_version_id"] == document.current_version_id
    assert CANARY not in json.dumps(payload)

    spec = get_question_type("document_analysis")
    assert spec.source_document_requirement.value == "required"


def test_document_analysis_requires_a_positive_document_id():
    with pytest.raises(ContentValidationError):
        validate_content(
            "document_analysis", 1, {"prompt": "x", "source_document_version_id": 0, "rubric": "y"}
        )


# --- 22. source_comparison multi-documents -------------------------------------------------------


def test_source_comparison_requires_at_least_two_documents():
    with pytest.raises(ContentValidationError):
        validate_content(
            "source_comparison",
            1,
            {"prompt": "x", "source_document_version_ids": [1], "rubric": "y"},
        )
    validate_content(
        "source_comparison",
        1,
        {"prompt": "x", "source_document_version_ids": [1, 2, 3], "rubric": "y"},
    )
    spec = get_question_type("source_comparison")
    assert spec.source_document_requirement.value == "multiple"


# --- 23. image_identification : asset requis -----------------------------------------------------


def test_image_identification_requires_an_asset():
    spec = get_question_type("image_identification")
    assert spec.asset_contract.requires_asset is True
    assert spec.asset_contract.min_assets == 1


def test_long_answer_requires_no_asset():
    spec = get_question_type("long_answer")
    assert spec.asset_contract.requires_asset is False


# --- 24. hotspot : zones normalisées ---------------------------------------------------------------


def test_hotspot_coordinates_must_be_normalized_between_0_and_1():
    content = dict(MINIMAL_VALID_CONTENT["hotspot"])
    bad = {**content, "zones": [{"zone_id": "z1", "x_min": -0.1, "y_min": 0, "x_max": 0.5, "y_max": 0.5}]}
    with pytest.raises(ContentValidationError):
        validate_content("hotspot", 1, bad)


def test_hotspot_resolves_zone_from_normalized_point():
    content = MINIMAL_VALID_CONTENT["hotspot"]
    assert check_answer("hotspot", 1, content, {"normalized_points": [[0.2, 0.2]]}) is True
    assert check_answer("hotspot", 1, content, {"normalized_points": [[0.9, 0.9]]}) is False


def test_hotspot_prefers_explicit_zone_ids_over_points():
    content = MINIMAL_VALID_CONTENT["hotspot"]
    assert check_answer("hotspot", 1, content, {"selected_zone_ids": ["z1"]}) is True


# --- 25. diagram_labeling ---------------------------------------------------------------------


def test_diagram_labeling_check_answer():
    content = MINIMAL_VALID_CONTENT["diagram_labeling"]
    assert check_answer("diagram_labeling", 1, content, {"mapping": {"z1": "l1"}}) is True
    assert check_answer("diagram_labeling", 1, content, {"mapping": {"z1": "l2"}}) is False


# --- 26. table_completion ------------------------------------------------------------------------


def test_table_completion_local_correction():
    content = {
        "prompt": "Complète.",
        "headers": ["A"],
        "rows": [[{"cell_id": "c1", "editable": True}]],
        "accepted_answers": {"c1": ["ram"]},
    }
    assert check_answer("table_completion", 1, content, {"values": {"c1": "RAM"}}) is True
    assert check_answer("table_completion", 1, content, {"values": {"c1": "rom"}}) is False


def test_table_completion_missing_accepted_answer_requires_semantic():
    content = {
        "prompt": "Complète.",
        "headers": ["A"],
        "rows": [[{"cell_id": "c1", "editable": True}]],
        "rubric": "grille",
    }
    assert check_answer("table_completion", 1, content, {"values": {"c1": "anything"}}) is None


# --- 27. graph schemas ------------------------------------------------------------------------


def test_graph_reading_numeric_mode():
    content = {"prompt": "Lis la valeur.", "response_mode": "numeric", "expected_value": 25.0}
    assert check_answer("graph_reading", 1, content, {"raw_input": "25"}) is True
    assert check_answer("graph_reading", 1, content, {"raw_input": "30"}) is False


def test_graph_reading_multiple_choice_mode():
    content = {
        "prompt": "Choisis la bonne tendance.",
        "response_mode": "multiple_choice",
        "options": [{"option_id": "up", "label": "Hausse"}, {"option_id": "down", "label": "Baisse"}],
        "correct_option_ids": ["up"],
    }
    assert check_answer("graph_reading", 1, content, {"selected_option_ids": ["up"]}) is True


def test_graph_reading_text_mode_without_accepted_answers_is_semantic():
    content = {"prompt": "Explique la courbe.", "response_mode": "text", "rubric": "..."}
    assert check_answer("graph_reading", 1, content, {"text": "n'importe quoi"}) is None


def test_graph_interaction_point_placement_with_tolerance():
    content = {
        "prompt": "Place le point au sommet.",
        "expected_points": [{"x": 1.0, "y": 2.0}],
        "point_tolerance": 0.2,
    }
    assert check_answer("graph_interaction", 1, content, {"points": [{"x": 1.1, "y": 1.9}]}) is True
    assert check_answer("graph_interaction", 1, content, {"points": [{"x": 5.0, "y": 5.0}]}) is False


def test_graph_interaction_parameter_set():
    content = {
        "prompt": "Ajuste les paramètres.",
        "interaction_kind": "parameter_set",
        "expected_parameters": {"a": 1.0, "b": 2.0},
        "parameter_tolerance": 0.1,
    }
    assert check_answer("graph_interaction", 1, content, {"parameters": {"a": 1.05, "b": 1.95}}) is True
    assert check_answer("graph_interaction", 1, content, {"parameters": {"a": 5.0, "b": 5.0}}) is False


# --- 28. code schemas : aucune exécution ---------------------------------------------------------


def test_code_reading_never_executes_code():
    content = {
        "prompt": "Que fait ce code ?",
        "code": "__import__('os').system('touch /tmp/should-not-exist-ticket40')",
        "response_mode": "choice",
        "options": [{"option_id": "a", "label": "Rien de spécial"}, {"option_id": "b", "label": "Autre"}],
        "correct_option_ids": ["a"],
    }
    import os

    marker = "/tmp/should-not-exist-ticket40"
    if os.path.exists(marker):
        os.remove(marker)
    validate_content("code_reading", 1, content)
    check_answer("code_reading", 1, content, {"selected_option_ids": ["a"]})
    assert not os.path.exists(marker), "le code stimulus a été exécuté — ne doit jamais arriver"


def test_code_completion_local_text_match_never_executes():
    content = {"prompt": "Complète.", "code_stimulus": "print(___)", "accepted_answers": ['"hello"']}
    assert check_answer("code_completion", 1, content, {"text": '"hello"'}) is True
    assert check_answer("code_completion", 1, content, {"text": "os.system('id')"}) is False


def test_no_eval_or_exec_in_engine_source():
    """Analyse statique (AST) plutôt qu'une recherche de sous-chaîne : les docstrings de
    ce module mentionnent volontairement `eval()`/`exec()` en prose (« jamais de
    eval() ») — seul un appel RÉEL à `eval`/`exec` doit faire échouer ce test."""
    import ast
    import inspect

    from app.v1 import question_engine
    from app.v1 import question_types as question_types_module

    for module in (question_engine, question_types_module):
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in ("eval", "exec"), (
                    f"appel réel à {node.func.id}() trouvé dans {module.__name__}"
                )


# --- 31. Compatibilité QuestionVersion (#38) ------------------------------------------------------


def test_content_json_round_trips_through_question_version(db_session):
    from app.models import Module, Subject
    from app.v1.models import GenerationSource, create_question

    subject = Subject(name="Informatique", slug="informatique-t40")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="AMPCR", slug="ampcr-t40", subject=subject)
    db_session.add(module)
    db_session.flush()

    content = MINIMAL_VALID_CONTENT["multiple_choice"]
    question = create_question(
        db_session,
        module_id=module.id,
        question_type="multiple_choice",
        content_json=content,
        generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()
    db_session.expire_all()

    from app.v1.models import Question

    reloaded = db_session.get(Question, question.id)
    validated = validate_content(
        reloaded.current_version.question_type, 1, reloaded.current_version.content_json
    )
    assert validated.prompt == content["prompt"]


# --- 32. Types/capabilities sérialisables ----------------------------------------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_capabilities_are_json_serializable(type_id):
    spec = get_question_type(type_id)
    serialized = json.dumps(
        {
            "type_id": spec.type_id,
            "correction_mode": spec.correction_mode.value,
            "capabilities": sorted(c.value for c in spec.capabilities),
            "source_document_requirement": spec.source_document_requirement.value,
            "asset_kinds": sorted(k.value for k in spec.asset_contract.allowed_kinds),
        }
    )
    assert json.loads(serialized)["type_id"] == type_id


# --- 33. Aucun comportement spécialisé selon subject/module --------------------------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS))
def test_content_model_never_references_subject_or_module(type_id):
    spec = get_question_type(type_id)
    field_names = set(spec.content_model.model_fields.keys())
    assert "subject" not in field_names
    assert "module" not in field_names
    assert "module_id" not in field_names


def test_same_classification_schema_used_for_informatique_and_français_content():
    """Scénario Informatique et scénario Français avec exactement le même type/schéma —
    aucune branche spécialisée par matière (voir docstring du module)."""
    informatique = {
        "prompt": "Classe : matériel ou logiciel ?",
        "categories": ["Matériel", "Logiciel"],
        "elements": ["Carte graphique", "Navigateur"],
        "correct_categories": [0, 1],
    }
    francais = {
        "prompt": "Classe : registre soutenu ou familier ?",
        "categories": ["Soutenu", "Familier"],
        "elements": ["Nonobstant", "Un truc de ouf"],
        "correct_categories": [0, 1],
    }
    validate_content("classification", 1, informatique)
    validate_content("classification", 1, francais)


def test_document_analysis_scenario_français(db_session):
    document = create_source_document(
        db_session, title="Extrait littéraire", content_text="Il pleure dans mon cœur..."
    )
    db_session.commit()
    content = {
        "prompt": "Quel est le sentiment dominant de cet extrait ?",
        "source_document_version_id": document.current_version_id,
        "rubric": "Doit identifier la mélancolie.",
    }
    validate_content("document_analysis", 1, content)


def test_source_comparison_scenario_français(db_session):
    doc_a = create_source_document(db_session, title="Texte A", content_text="...")
    doc_b = create_source_document(db_session, title="Texte B", content_text="...")
    db_session.commit()
    content = {
        "prompt": "Compare le point de vue des deux auteurs.",
        "source_document_version_ids": [doc_a.current_version_id, doc_b.current_version_id],
        "rubric": "Doit mentionner les deux points de vue.",
    }
    validate_content("source_comparison", 1, content)


# --- answer valide/invalide générique ---------------------------------------------------------


@pytest.mark.parametrize("type_id", sorted(EXPECTED_TYPE_IDS - {"true_false"}))
def test_answer_model_accepts_its_own_empty_default_shape(type_id):
    """Chaque answer_model doit accepter une réponse « vide » sans lever d'exception
    (état initial avant que l'élève ait répondu, ex. autosave vide). Exception :
    `true_false` exige un booléen explicite — un booléen n'a pas d'état « vide »
    sensé, et `app.v1.models.SessionAnswer` n'est de toute façon créé qu'au premier
    envoi réel (voir ticket #38) : l'absence de réponse se traduit par l'absence de
    ligne, jamais par un answer_json ambigu."""
    spec = get_question_type(type_id)
    spec.answer_model.model_validate({})


def test_true_false_answer_requires_an_explicit_boolean():
    with pytest.raises(ContentValidationError):
        validate_answer("true_false", 1, {})


def test_matching_answer_rejects_non_dict_pairs_gracefully():
    with pytest.raises(ContentValidationError):
        validate_answer("matching", 1, {"pairs": "not-a-dict"})

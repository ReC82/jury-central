"""Ticket #69 — Qualité questions AMPCR : éliminer les diagnostics/classifications/
ordering/QCM trop faciles ou ambigus.

Ne touche pas au modèle de données, aux sessions, au scoring (#70), aux limites de
réponse longue (#73), au Français ni à l'UX navigation (#67) — uniquement la QUALITÉ et
la CLARTÉ des questions générées.

Couvre :
1. `app.v1.ai_bridge.shuffle_ordering_items` — correctif mécanique principal (§ 2, Q4).
2. `app.v1.quality_validation` — filet de sécurité + règles mécaniques bornées
   (Q6/Q10/UTP-STP + garde ordering).
3. `app.v1.bank.persist_generated_questions` — intégration bout en bout (rejet qualité
   avant persistance, journalisation, non-visibilité en banque).
4. `app.ai.prompts` — instructions de génération (Q3/Q11/Q17, non mécaniquement
   vérifiables côté serveur sans NLP — couvertes par le prompt, § 9 du ticket).
5. Non-régression #64/#68 et garantie structurelle #40 (« aucun double choix correct
   involontaire »).

Aucun appel OpenAI réel."""

import random

import pytest
from pydantic import ValidationError

from app.ai.prompts import GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
from app.ai.schemas import QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.ai_bridge import questionnaire_question_to_content, shuffle_ordering_items
from app.v1.bank import persist_generated_questions
from app.v1.quality_validation import validate_question_quality
from app.v1.question_types import MultipleChoiceContent


class _FakeUAA:
    def __init__(self, code: str):
        self.code = code


MC17 = _FakeUAA("MC17")


# =============================================================================================
# 1. app.v1.ai_bridge.shuffle_ordering_items — correctif mécanique (§ 2, Q4)
# =============================================================================================


def test_shuffle_never_matches_correct_order_two_items():
    """Cas le plus difficile (2 permutations possibles seulement) : jamais l'ordre
    attendu, sur de nombreux essais."""
    correct_order = ["item0", "item1"]
    random.seed(42)
    for _ in range(300):
        items = [{"id": "item0", "label": "A"}, {"id": "item1", "label": "B"}]
        result = shuffle_ordering_items(items, correct_order)
        assert [i["id"] for i in result] != correct_order


def test_shuffle_never_matches_correct_order_six_items():
    correct_order = [f"item{i}" for i in range(6)]
    random.seed(7)
    for _ in range(100):
        items = [{"id": f"item{i}", "label": chr(65 + i)} for i in range(6)]
        result = shuffle_ordering_items(items, correct_order)
        assert [i["id"] for i in result] != correct_order


def test_shuffle_preserves_id_label_pairs():
    items = [{"id": "item0", "label": "Monter"}, {"id": "item1", "label": "Installer OS"}, {"id": "item2", "label": "RJ45"}]
    correct_order = ["item0", "item1", "item2"]
    result = shuffle_ordering_items(items, correct_order)
    by_id = {i["id"]: i["label"] for i in result}
    assert by_id == {"item0": "Monter", "item1": "Installer OS", "item2": "RJ45"}


def test_shuffle_never_modifies_correct_order_itself():
    items = [{"id": "item0", "label": "A"}, {"id": "item1", "label": "B"}, {"id": "item2", "label": "C"}]
    correct_order = ["item2", "item0", "item1"]
    result = shuffle_ordering_items(items, correct_order)
    assert correct_order == ["item2", "item0", "item1"]  # jamais modifié
    assert {i["id"] for i in result} == {"item0", "item1", "item2"}  # même ensemble


def test_shuffle_single_item_returns_as_is():
    items = [{"id": "item0", "label": "Seul"}]
    assert shuffle_ordering_items(items, ["item0"]) == items


def test_questionnaire_question_to_content_ordering_never_pre_sorted():
    """Cas réel Q4 (§ 2) : `order_items` fournis par l'IA dans l'ordre correct, avec
    `correct_order` identité — le pont IA doit tout de même livrer un `content_json` dont
    l'affichage diffère de l'ordre attendu."""
    question = QuestionnaireQuestion(
        question_id="q4", type="ordering", prompt="Ordonne les étapes.", points_max=1.0,
        order_items=["Montage PC", "Installer OS", "RJ45", "IP", "Test second PC", "Partage"],
        correct_order=[0, 1, 2, 3, 4, 5],
    )
    random.seed(123)
    for _ in range(50):
        content = questionnaire_question_to_content(question)
        displayed_ids = [item["id"] for item in content["items"]]
        assert displayed_ids != content["correct_order"]
        # Le libellé associé à chaque id reste exact malgré le mélange.
        labels_by_id = {item["id"]: item["label"] for item in content["items"]}
        assert labels_by_id["item0"] == "Montage PC"
        assert labels_by_id["item5"] == "Partage"


# =============================================================================================
# 2. app.v1.quality_validation — filet de sécurité + règles mécaniques bornées
# =============================================================================================


def test_ordering_exact_match_rejected_as_safety_net():
    content = {
        "items": [{"id": "item0", "label": "A"}, {"id": "item1", "label": "B"}, {"id": "item2", "label": "C"}],
        "correct_order": ["item0", "item1", "item2"],
    }
    errors = validate_question_quality(None, MC17, "ordering", content)
    assert errors and "ordre attendu" in errors[0]


def test_ordering_shuffled_accepted():
    content = {
        "items": [{"id": "item2", "label": "C"}, {"id": "item0", "label": "A"}, {"id": "item1", "label": "B"}],
        "correct_order": ["item0", "item1", "item2"],
    }
    assert validate_question_quality(None, MC17, "ordering", content) == []


# --- Q10 : CIDR trop guidé --------------------------------------------------------------------


def test_cidr_overguided_ordering_rejected():
    """Cas réel Q10 (§ 3) : l'énoncé donne déjà les bornes du classement."""
    content = {
        "prompt": (
            "Classe les préfixes ... en partant du plus petit nombre d'hôtes utilisables "
            "(/30) jusqu'au plus grand (/24)."
        ),
        "items": [
            {"id": "item0", "label": "/24"}, {"id": "item1", "label": "/26"}, {"id": "item2", "label": "/30"},
        ],
        "correct_order": ["item2", "item1", "item0"],
    }
    errors = validate_question_quality(None, MC17, "ordering", content)
    assert errors and "révèle directement" in errors[0]


def test_cidr_not_overguided_ordering_accepted():
    content = {
        "prompt": "Classe ces préfixes du plus petit nombre d'hôtes utilisables au plus grand.",
        "items": [
            {"id": "item0", "label": "/24"}, {"id": "item1", "label": "/26"}, {"id": "item2", "label": "/30"},
        ],
        "correct_order": ["item2", "item1", "item0"],
    }
    assert validate_question_quality(None, MC17, "ordering", content) == []


def test_cidr_overguided_classification_rejected():
    content = {
        "prompt": "Classe chaque préfixe : /30 est le plus petit, /24 le plus grand en nombre d'hôtes.",
        "categories": ["Petit nombre d'hôtes", "Grand nombre d'hôtes"],
        "elements": ["/30", "/24"],
        "correct_categories": [0, 1],
    }
    errors = validate_question_quality(None, MC17, "classification", content)
    assert errors and "révèle directement" in errors[0]


# --- Q6 : diagnostic autosuffisant --------------------------------------------------------------


def test_q6_vague_diagnostic_rejected():
    """Cas réel Q6 (§ 7) : l'énoncé annonce déjà le symptôme et l'étape attendue est
    redondante/vague, sans donnée concrète exploitable."""
    content = {
        "prompt": "Le poste est correctement raccordé physiquement mais ne possède pas d'adresse IP exploitable.",
    }
    errors = validate_question_quality(None, MC17, "diagnostic", content)
    assert errors and "contexte concret" in errors[0]


def test_q6_apipa_dhcp_diagnostic_accepted():
    content = {
        "prompt": (
            "`ipconfig` affiche 169.254.23.8 sur un poste configuré en DHCP. Quelle "
            "vérification fais-tu ensuite et quelle commande peut aider ?"
        ),
    }
    assert validate_question_quality(None, MC17, "diagnostic", content) == []


def test_generic_diagnostic_autosuffisance_example_rejected():
    """§ 6, exemple générique du ticket (à éviter)."""
    content = {"prompt": "Après avoir vérifié l'adresse IP, que vérifier ensuite ?"}
    assert validate_question_quality(None, MC17, "diagnostic", content) != []


def test_generic_diagnostic_autosuffisance_example_accepted():
    """§ 6, exemple préférable du ticket."""
    content = {
        "prompt": (
            "Le lien Ethernet est actif. Le poste possède 192.168.1.25/24. Le ping vers "
            "192.168.1.1 échoue. Quelle vérification effectues-tu ensuite ?"
        ),
    }
    assert validate_question_quality(None, MC17, "diagnostic", content) == []


# --- UTP/STP : critères objectifs -----------------------------------------------------------


def test_utp_stp_soft_phrasing_rejected():
    """Cas réel (§ 8) : « souvent choisi » ne peut pas déterminer seul une classification."""
    content = {
        "prompt": "Câble souvent choisi pour une installation informatique courante...",
        "options": [{"option_id": "0", "label": "UTP"}, {"option_id": "1", "label": "STP"}],
    }
    errors = validate_question_quality(None, MC17, "multiple_choice", content)
    assert errors and "trop faible" in errors[0]


@pytest.mark.parametrize(
    "prompt",
    [
        "Quel câble n'a pas de blindage métallique ?",
        "Quel câble comporte un blindage contre les perturbations électromagnétiques ?",
        "Quel câble nécessite un raccordement correct du blindage pour rester efficace ?",
    ],
)
def test_utp_stp_objective_criteria_accepted(prompt):
    content = {
        "prompt": prompt,
        "options": [{"option_id": "0", "label": "UTP"}, {"option_id": "1", "label": "STP"}],
    }
    assert validate_question_quality(None, MC17, "multiple_choice", content) == []


def test_generalement_utilise_also_flagged():
    content = {
        "prompt": "Norme généralement utilisée pour le câblage domestique.",
        "options": [{"option_id": "0", "label": "T568A"}, {"option_id": "1", "label": "T568B"}],
    }
    assert validate_question_quality(None, MC17, "multiple_choice", content) != []


# --- Périmètre : ne touche pas ce qui n'a rien à voir ----------------------------------------


def test_unrelated_question_never_flagged():
    content = {
        "prompt": "Quel composant stocke les données de façon volatile ?",
        "options": [{"option_id": "0", "label": "RAM"}, {"option_id": "1", "label": "SSD"}],
    }
    assert validate_question_quality(None, MC17, "multiple_choice", content) == []


def test_long_answer_type_never_checked_by_diagnostic_rule():
    """La règle d'autosuffisance ne s'applique qu'au type `diagnostic` (§ 6), pas à
    `long_answer`, pour rester bornée et ne pas sur-bloquer des types non visés."""
    content = {"prompt": "Explique.", "rubric": "grille"}
    assert validate_question_quality(None, MC17, "long_answer", content) == []


# =============================================================================================
# 3. app.v1.bank.persist_generated_questions — intégration bout en bout
# =============================================================================================


def test_quality_rejected_question_not_persisted(db_session, caplog):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    bad_diagnostic = QuestionnaireQuestion(
        question_id="q1", type="diagnostic", prompt="Après avoir vérifié l'adresse IP, que vérifier ensuite ?",
        points_max=1.0, rubric="grille",
    )
    with caplog.at_level("WARNING"):
        persisted = persist_generated_questions(
            db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[bad_diagnostic],
        )
    assert persisted == []
    assert "QUALITY_VALIDATION_REJECTED" in caplog.text


def test_quality_rejected_question_not_visible_in_bank(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    bad = QuestionnaireQuestion(
        question_id="q1", type="multiple_choice",
        prompt="Câble souvent choisi pour une installation informatique courante...",
        points_max=1.0, choices=["UTP", "STP"], correct_indexes=[0],
    )
    persist_generated_questions(db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[bad])
    db_session.commit()
    from app.v1.models import ContentStatus, Question

    prompts = [
        q.current_version.content_json.get("prompt")
        for q in db_session.query(Question).filter_by(module_id=ampcr.id, uaa_id=mc17.id, status=ContentStatus.ACTIVE)
    ]
    assert not any("souvent choisi" in (p or "") for p in prompts)


def test_valid_question_persisted_normally(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    good = QuestionnaireQuestion(
        question_id="q1", type="diagnostic",
        prompt="`ipconfig` affiche 169.254.23.8 sur un poste configuré en DHCP. Que vérifies-tu ensuite ?",
        points_max=1.0, rubric="grille",
    )
    persisted = persist_generated_questions(db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[good])
    assert len(persisted) == 1


def test_mixed_batch_only_quality_invalid_rejected(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    bad = QuestionnaireQuestion(
        question_id="bad", type="diagnostic", prompt="Après avoir vérifié l'adresse IP, que vérifier ensuite ?",
        points_max=1.0, rubric="grille",
    )
    good = QuestionnaireQuestion(
        question_id="good", type="diagnostic",
        prompt="`ping` vers 192.168.1.1 échoue alors que l'IP locale est correcte. Que vérifies-tu ensuite ?",
        points_max=1.0, rubric="grille",
    )
    rejections: list[str] = []
    persisted = persist_generated_questions(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[bad, good], domain_rejections=rejections,
    )
    assert len(persisted) == 1
    assert "192.168.1.1" in persisted[0].current_version.content_json["prompt"]
    assert rejections == ["diagnostic"]


# =============================================================================================
# 4. app.ai.prompts — instructions de génération (Q3/Q11/Q17, prompt-only par design § 9)
# =============================================================================================


def test_prompt_instructs_plausible_distractors_not_grotesque():
    assert "grotesques" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT or "jamais grotesques" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_wifi_bad_and_good_distractor_examples_present():
    """Q11 — exemples exacts du ticket."""
    assert "désactiver le SSID" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "remplacer le BSSID par une adresse" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "2,4 GHz" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_security_bad_and_good_distractor_examples_present():
    """Q17 — exemples exacts du ticket."""
    assert "pulvériser un liquide" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "câble secteur branché" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "radiateur" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "précaution ESD" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_instructs_ordering_display_order_never_sorted():
    assert "jamais déjà triés" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_instructs_classification_distractor_categories_and_objective_criteria():
    assert "catégories" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "propriété technique" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT
    assert "souvent choisi" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_instructs_cidr_never_leak_bounds_in_statement():
    assert "ne révèle jamais une partie de la réponse" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


def test_prompt_instructs_diagnostic_exactly_one_reasonable_next_step():
    assert "EXACTEMENT une démarche" in GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT


# =============================================================================================
# 5. Non-régression #64/#68 + garantie structurelle #40
# =============================================================================================


def test_no_unintentional_double_correct_answer_structurally_impossible():
    """§ 11 : « aucun double choix correct involontaire » — déjà garanti structurellement
    par le registre #40 (ticket #38/#40) pour un QCM à réponse unique : `correct_option_
    ids` DOIT avoir exactement `max_selections` éléments. Non-régression documentée, pas
    une nouvelle règle."""
    with pytest.raises(ValidationError):
        MultipleChoiceContent(
            prompt="Question ?",
            options=[{"option_id": "0", "label": "A"}, {"option_id": "1", "label": "B"}, {"option_id": "2", "label": "C"}],
            min_selections=1, max_selections=1,
            correct_option_ids=["0", "1"],  # deux réponses correctes pour un choix unique
        )


def test_domain_validation_still_wired_alongside_quality_validation(db_session):
    """Non-régression #68 : la validation métier IPv4 continue de fonctionner, dans le
    même pipeline que la nouvelle validation qualité."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    bad_ipv4 = QuestionnaireQuestion(
        question_id="q1", type="multiple_choice",
        prompt="Un poste possède l'adresse 192.168.1.10/28. Quelle adresse est valide pour un autre poste ?",
        points_max=1.0, choices=["192.168.1.0", "192.168.1.5"], correct_indexes=[0],
    )
    persisted = persist_generated_questions(db_session, module_id=ampcr.id, uaa_id=mc17.id, questions=[bad_ipv4])
    assert persisted == []


def test_no_real_openai_provider_imported_by_quality_validation():
    import app.v1.quality_validation as module

    assert "openai_provider" not in module.__dict__
    with open(module.__file__) as f:
        source = f.read()
    assert "openai" not in source.lower()

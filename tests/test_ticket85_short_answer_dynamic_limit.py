"""Ticket #85 — limite de longueur des `short_answer` trop basse (200 caractères fixes
quelle que soit la question).

Cas réel : une question de comparaison HDD / SSD SATA / SSD NVMe coupait la réponse de
l'utilisateur à 200/200 caractères alors qu'il voulait la compléter.
"""

from app.ai.schemas import QuestionnaireQuestion
from app.editorial_exercise import EditorialExerciseItem
from app.v1.ai_bridge import questionnaire_question_to_content
from app.v1.bank import _editorial_item_to_v1_content, migrate_short_answer_max_length
from app.v1.models import create_question
from app.v1.quality_validation import check_short_answer_length_coherence, validate_question_quality
from app.v1.short_answer_limits import (
    DEVELOPED_DEFAULT_MAX_LENGTH,
    FACTUAL_DEFAULT_MAX_LENGTH,
    compute_short_answer_max_length,
    is_max_length_incoherent,
)

# --- § 85.A : calcul de la limite dynamique --------------------------------------------------


def test_factual_question_gets_factual_range():
    prompt = "Que signifie l'acronyme SMART ?"
    limit = compute_short_answer_max_length(prompt)
    assert 100 <= limit <= 300
    assert limit == FACTUAL_DEFAULT_MAX_LENGTH


def test_increment_question_is_factual():
    limit = compute_short_answer_max_length("Quel est l'incrément d'un réseau en /26 ?")
    assert limit == FACTUAL_DEFAULT_MAX_LENGTH


def test_command_question_is_factual():
    limit = compute_short_answer_max_length("Quelle commande affiche la configuration IP sous Windows ?")
    assert limit == FACTUAL_DEFAULT_MAX_LENGTH


def test_real_case_hdd_ssd_comparison_gets_developed_range():
    prompt = "Compare le HDD, le SSD SATA et le SSD NVMe en termes de vitesse et de fiabilité."
    limit = compute_short_answer_max_length(prompt)
    assert 800 <= limit <= 1500
    assert limit == DEVELOPED_DEFAULT_MAX_LENGTH


def test_explique_trigger_gets_developed_range():
    assert compute_short_answer_max_length("Explique pourquoi un SSD est plus rapide qu'un HDD.") == DEVELOPED_DEFAULT_MAX_LENGTH


def test_justifie_trigger_gets_developed_range():
    assert compute_short_answer_max_length("Justifie ton choix de masque pour ce sous-réseau.") == DEVELOPED_DEFAULT_MAX_LENGTH


def test_decris_trigger_gets_developed_range():
    assert compute_short_answer_max_length("Décris la démarche de diagnostic à suivre.") == DEVELOPED_DEFAULT_MAX_LENGTH


def test_pourquoi_trigger_gets_developed_range():
    assert compute_short_answer_max_length("Pourquoi ne faut-il jamais défragmenter un SSD ?") == DEVELOPED_DEFAULT_MAX_LENGTH


def test_multi_part_trigger_gets_developed_range():
    limit = compute_short_answer_max_length("Donne trois raisons pour lesquelles un PC ne démarre pas.")
    assert limit == DEVELOPED_DEFAULT_MAX_LENGTH


def test_accent_insensitive_trigger_detection():
    # "décris"/"démarche" avec ou sans accents, casse variable.
    assert compute_short_answer_max_length("DECRIS la demarche complete.") == DEVELOPED_DEFAULT_MAX_LENGTH


# --- § 85.B : garde d'incohérence -------------------------------------------------------------


def test_incoherent_when_developed_prompt_has_factual_limit():
    assert is_max_length_incoherent("Explique pourquoi WPA2 est moins sûr que WPA3.", 200) is True


def test_coherent_when_developed_prompt_has_developed_limit():
    assert is_max_length_incoherent("Explique pourquoi WPA2 est moins sûr que WPA3.", 1500) is False


def test_coherent_when_factual_prompt_has_factual_limit():
    assert is_max_length_incoherent("Que signifie SMART ?", 200) is False


def test_check_short_answer_length_coherence_rejects_incoherent_content():
    content = {"prompt": "Compare le HDD et le SSD en détail.", "max_length": 200}
    errors = check_short_answer_length_coherence(None, None, "short_answer", content)
    assert len(errors) == 1
    assert "85.B" in errors[0] or "Incohérence" in errors[0]


def test_check_short_answer_length_coherence_accepts_coherent_content():
    content = {"prompt": "Compare le HDD et le SSD en détail.", "max_length": 1500}
    assert check_short_answer_length_coherence(None, None, "short_answer", content) == []


def test_check_short_answer_length_coherence_ignores_other_types():
    content = {"prompt": "Explique en détail.", "max_length": 200}
    assert check_short_answer_length_coherence(None, None, "multiple_choice", content) == []


def test_check_short_answer_length_coherence_wired_into_full_validator():
    content = {"prompt": "Justifie en détail ton raisonnement.", "max_length": 200}
    errors = validate_question_quality(None, None, "short_answer", content)
    assert any("85.B" in e or "Incohérence" in e for e in errors)


# --- Câblage dans la génération IA (Informatique) ---------------------------------------------


def test_ai_bridge_sets_dynamic_max_length_for_factual_question():
    question = QuestionnaireQuestion(
        question_id="q1", type="short_answer", prompt="Que signifie l'acronyme SMART ?",
        points_max=1.0, accepted_answers=["surveillance de l'état du disque"],
    )
    content = questionnaire_question_to_content(question)
    assert content["max_length"] == FACTUAL_DEFAULT_MAX_LENGTH


def test_ai_bridge_sets_dynamic_max_length_for_developed_question():
    question = QuestionnaireQuestion(
        question_id="q1", type="short_answer",
        prompt="Explique pourquoi un SSD NVMe est plus rapide qu'un SSD SATA.",
        points_max=1.0, rubric="Doit mentionner le bus PCIe et le protocole NVMe.",
    )
    content = questionnaire_question_to_content(question)
    assert content["max_length"] == DEVELOPED_DEFAULT_MAX_LENGTH


def test_ai_bridge_vocabulary_type_also_gets_dynamic_max_length():
    question = QuestionnaireQuestion(
        question_id="q1", type="vocabulary", prompt="Que signifie DHCP ?",
        points_max=1.0, accepted_answers=["Dynamic Host Configuration Protocol"],
    )
    content = questionnaire_question_to_content(question)
    assert content["max_length"] == FACTUAL_DEFAULT_MAX_LENGTH


# --- Câblage dans l'import éditorial legacy (MC01 Informatique) -------------------------------


def test_editorial_short_answer_gets_dynamic_max_length():
    item = EditorialExerciseItem(
        exercise_id="t85-ex1",
        type="short_answer",
        prompt="Compare le rôle du CPU et de la RAM dans le traitement d'une instruction.",
        accepted_answers=["reponse de reference"],
        explanation="",
    )
    v1_type, content = _editorial_item_to_v1_content(item)
    assert v1_type == "short_answer"
    assert content["max_length"] == DEVELOPED_DEFAULT_MAX_LENGTH


# --- § 85.C : migration des questions déjà persistées ------------------------------------------


def test_migration_increases_max_length_for_developed_question_stuck_at_200(db_session):
    from app.models import Module, Subject

    subject = Subject(name="Informatique", slug="informatique-t85")
    db_session.add(subject)
    db_session.flush()
    module = Module(subject_id=subject.id, code="AMPCR-T85", slug="ampcr-t85")
    db_session.add(module)
    db_session.flush()

    question = create_question(
        db_session, module_id=module.id, question_type="short_answer",
        content_json={
            "prompt": "Compare le HDD, le SSD SATA et le SSD NVMe.",
            "accepted_answers": [],
            "rubric": "Doit couvrir vitesse, fiabilité et prix.",
            "max_length": 200,
        },
        generation_source="manual",
    )
    db_session.commit()
    original_version_id = question.current_version_id

    report = migrate_short_answer_max_length(db_session)
    db_session.commit()

    assert report["reviewed"] >= 1
    assert report["increased"] >= 1

    db_session.refresh(question)
    assert question.current_version_id != original_version_id
    assert question.current_version.content_json["max_length"] == DEVELOPED_DEFAULT_MAX_LENGTH
    # Rien d'autre n'a changé.
    assert question.current_version.content_json["rubric"] == "Doit couvrir vitesse, fiabilité et prix."


def test_migration_never_decreases_or_touches_genuinely_factual_questions(db_session):
    from app.models import Module, Subject

    subject = Subject(name="Informatique", slug="informatique-t85b")
    db_session.add(subject)
    db_session.flush()
    module = Module(subject_id=subject.id, code="AMPCR-T85B", slug="ampcr-t85b")
    db_session.add(module)
    db_session.flush()

    question = create_question(
        db_session, module_id=module.id, question_type="short_answer",
        content_json={
            "prompt": "Que signifie l'acronyme SMART ?",
            "accepted_answers": ["surveillance de l'etat du disque"],
            "rubric": "",
            "max_length": 200,
        },
        generation_source="manual",
    )
    db_session.commit()
    original_version_id = question.current_version_id

    migrate_short_answer_max_length(db_session)
    db_session.commit()

    db_session.refresh(question)
    assert question.current_version_id == original_version_id
    assert question.current_version.content_json["max_length"] == 200


def test_migration_is_idempotent(db_session):
    from app.models import Module, Subject

    subject = Subject(name="Informatique", slug="informatique-t85c")
    db_session.add(subject)
    db_session.flush()
    module = Module(subject_id=subject.id, code="AMPCR-T85C", slug="ampcr-t85c")
    db_session.add(module)
    db_session.flush()

    create_question(
        db_session, module_id=module.id, question_type="short_answer",
        content_json={
            "prompt": "Justifie le choix d'un masque /28 pour ce sous-réseau.",
            "accepted_answers": [],
            "rubric": "Doit calculer le nombre d'hôtes utilisables.",
            "max_length": 200,
        },
        generation_source="manual",
    )
    db_session.commit()

    first = migrate_short_answer_max_length(db_session)
    db_session.commit()
    second = migrate_short_answer_max_length(db_session)
    db_session.commit()

    assert first["increased"] >= 1
    assert second["increased"] == 0

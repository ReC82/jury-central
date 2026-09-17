"""Tests d'intégration du ticket #10 : Informatique AMPCR, mini-cours 01.

Vérifie que la matière est réellement navigable, que le cours affiche la matière
obligatoire sans casser Mathématiques, et surtout que le corrigé de l'examen final n'est
jamais servi sur la route publique (is_published=False, voir app/main.py::uaa_detail).
"""

from app.seed import MC01_BLOCKS, seed


def test_informatique_subject_is_navigable(client, db_session):
    seed()

    response = client.get("/subjects")
    assert response.status_code == 200
    assert "Informatique" in response.text


def test_mc01_is_accessible_from_normal_navigation(client, db_session):
    seed()

    subjects_response = client.get("/subjects")
    assert "/subjects/informatique" in subjects_response.text

    subject_response = client.get("/subjects/informatique")
    assert subject_response.status_code == 200
    assert "/modules/ampcr" in subject_response.text

    module_response = client.get("/modules/ampcr")
    assert module_response.status_code == 200
    assert "/uaa/ampcr-mc01" in module_response.text

    uaa_response = client.get("/uaa/ampcr-mc01")
    assert uaa_response.status_code == 200
    assert "Architecture générale d'un PC" in uaa_response.text


def test_mc01_covers_the_mandatory_content(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc01")
    assert response.status_code == 200
    text = response.text

    # Les 9 notions obligatoires du ticket #10.
    for expected in [
        "Matériel (hardware) et logiciel (software)",
        "Rôle de la carte mère",
        "Rôle du processeur",
        "Rôle de la RAM",
        "Rôle du stockage",
        "Rôle du GPU",
        "Rôle de l'alimentation",
        "Qu'est-ce qu'un périphérique",
        "Scénario : tu lances un programme installé sur un SSD",
    ]:
        assert expected in text, f"section manquante : {expected}"

    # Vocabulaire FR/EN et vocabulaire ancien du référentiel.
    assert "Motherboard" in text
    assert "Graveur optique" in text
    assert "Lecteur de disquettes" in text


def test_mc01_has_twelve_exercises_with_hidden_corrections(authenticated_client, db_session):
    """Depuis le ticket #55, `/uaa/ampcr-mc01/practice` affiche le nouveau parcours de
    session V1 (choix de difficulté, puis questionnaire de 10 questions) plutôt que les
    12 exercices `editorial_exercise` empilés du ticket #29 — voir
    `docs/claude-reports/2026-09-17_ticket-55_urgent-ampcr-full.md`. Le contenu
    pédagogique des 12 exercices reste inchangé en base (`app.seed.MC01_BLOCKS`) et sert
    désormais de banque V1 initiale (`app.v1.bank.import_mc01_legacy_to_bank`) — voir
    `tests/test_ticket55_urgent_ampcr_full.py` pour la non-régression détaillée du
    contenu."""
    seed()

    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    text = response.text

    assert response.status_code == 200
    assert "Commencer l'entraînement" in text

    # Aucune correction ni contenu d'exercice visible avant qu'une session ne soit créée.
    assert "Correction :" not in text
    for n in range(1, 13):
        assert f"Exercice {n} —" not in text

    # Aucune fuite de solution, pour aucun type.
    assert "correct_categories" not in text
    assert "correct_order" not in text
    assert '"correct_index"' not in text
    assert '"accepted_answers"' not in text
    assert '"explanation"' not in text
    assert '"rubric"' not in text


def test_exam_is_published_without_visible_correction(authenticated_client, db_session):
    """Depuis le ticket #55, `/uaa/ampcr-mc01/exam` affiche le nouveau parcours de
    session V1 — plus l'ancien examen Markdown statique."""
    seed()

    response = authenticated_client.get("/uaa/ampcr-mc01/exam")
    text = response.text

    assert response.status_code == 200
    assert "Commencer l'évaluation" in text

    # Le corrigé (bloc non publié) ni l'ancien examen statique ne doivent jamais
    # apparaître sur la nouvelle page publique.
    assert "Corrigé" not in text
    assert "0,5 pt par rôle correct" not in text
    assert "notation qualitative" not in text


def test_course_page_no_longer_contains_practice_or_exam_content(client, db_session):
    """Acceptation explicite du ticket #22 : la page Cours ne mélange plus théorie,
    exercices et examen dans le même flux."""
    seed()

    response = client.get("/uaa/ampcr-mc01")
    text = response.text

    assert response.status_code == 200
    # Théorie toujours présente.
    assert "Rôle de la carte mère" in text
    # Plus aucun exercice ni examen dans le flux Cours.
    for n in range(1, 13):
        assert f"Exercice {n} —" not in text
    assert "Examen final" not in text
    assert "Génère ton propre exercice" not in text
    # La navigation vers les deux autres espaces reste accessible depuis Cours.
    assert "/uaa/ampcr-mc01/practice" in text
    assert "/uaa/ampcr-mc01/exam" in text


def test_exam_correction_block_exists_but_is_unpublished(db_session):
    seed()

    from app.models import UAA, LessonBlock

    uaa = db_session.query(UAA).filter_by(code="MC01").first()
    assert uaa is not None

    correction_block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, title="Examen final — Corrigé (réservé formateur, non publié)")
        .first()
    )
    assert correction_block is not None
    assert correction_block.is_published is False
    assert len(uaa.lesson_blocks) == len(MC01_BLOCKS)


def test_seed_does_not_break_existing_mathematiques_content(client, db_session):
    seed()

    response = client.get("/uaa/mb32-uaa1")
    assert response.status_code == 200
    assert "Fonction constante" in response.text

    subjects_response = client.get("/subjects")
    assert "Mathématiques" in subjects_response.text

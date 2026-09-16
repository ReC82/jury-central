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


def test_mc01_has_twelve_exercises_with_hidden_corrections(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc01")
    text = response.text

    # Les 12 énoncés sont présents (rendu Markdown -> <h2>Exercice N — ...</h2>).
    for n in range(1, 13):
        assert f"Exercice {n} —" in text, f"exercice {n} manquant"

    # Chaque exercice contient bien un paragraphe de correction : le Markdown est rendu
    # côté serveur tel quel (comme pour Solides/Patrons en Géométrie), le masquage jusqu'à
    # la demande explicite est appliqué ensuite côté client par
    # app/static/js/design_system.js::splitExerciseCorrections() — pas testable via
    # TestClient (pas de JS), donc on vérifie ici que le texte est bien présent et sera
    # capturé par ce mécanisme générique (déjà couvert par la convention existante).
    assert text.count("Correction :") >= 12


def test_exam_is_published_without_visible_correction(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc01")
    text = response.text

    assert "Examen final" in text
    assert "Question 10 (2 pts)" in text

    # Le corrigé (bloc non publié) ne doit jamais apparaître sur la page publique.
    assert "Corrigé" not in text
    assert "0,5 pt par rôle correct" not in text
    assert "notation qualitative" not in text


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

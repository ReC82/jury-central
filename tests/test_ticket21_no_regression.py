"""Non-régression du ticket #21 (classification/ordering + migration MC01) :

- exercices 1, 2, 9, 11 migrés vers des blocs `editorial_exercise`, sans doublon avec
  l'ancien texte Markdown ;
- exercices 3, 4, 5, 6, 7, 8, 10, 12 strictement inchangés ;
- MC02, MC03 et Mathématiques non affectés ;
- le seed reste additif et idempotent (deux appels successifs ne créent rien de plus) ;
- scénario explicite de migration d'un staging déjà seedé AVANT le ticket #21 (base
  contenant encore l'ancien texte Markdown des exercices 1/2/9/11) : un second seed doit
  retirer l'ancien contenu et ajouter les nouveaux blocs, sans jamais passer par un
  reset-db — voir docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md,
  section « Migration du contenu déjà seedé (staging) »."""

from app.models import UAA, BlockType, LessonBlock, Module, Subject
from app.seed import (
    INFORMATIQUE_SUBJECT_NAME,
    MC01_BLOCKS,
    MC01_OBSOLETE_TITLES,
    MC02_BLOCKS,
    MC03_BLOCKS,
    seed,
)


def _mc01_uaa(db_session):
    return db_session.query(UAA).filter_by(code="MC01").first()


def test_exactly_four_mc01_exercises_are_editorial_exercise_blocks(client, db_session):
    seed()
    uaa = _mc01_uaa(db_session)
    assert uaa is not None

    editorial_blocks = [
        block for block in uaa.lesson_blocks if block.type == BlockType.EDITORIAL_EXERCISE
    ]
    assert len(editorial_blocks) == 4
    titles = {block.title for block in editorial_blocks}
    assert titles == {
        "Exercice 1 — Matériel ou logiciel (classification)",
        "Exercice 2 — Unité centrale ou périphérique (classification)",
        "Exercice 9 — Lancement d'un programme (ordering)",
        "Exercice 11 — Entrée, sortie ou mixte (classification)",
    }


def test_migrated_exercises_no_longer_appear_in_markdown_form(client, db_session):
    """Les exercices 1, 2, 9, 11 ne doivent plus exister sous leur ancien texte Markdown —
    aucun doublon entre le bloc structuré et un reliquat statique."""
    seed()
    uaa = _mc01_uaa(db_session)
    markdown_text = "\n".join(
        block.content for block in uaa.lesson_blocks if block.type == BlockType.MARKDOWN
    )

    # Titres/énoncés Markdown propres aux exercices migrés — absents du texte restant.
    assert "## Exercice 1 — classer" not in markdown_text
    assert "## Exercice 2 — classer" not in markdown_text
    assert "## Exercice 9 — reconstruire" not in markdown_text
    assert "## Exercice 11 — classer" not in markdown_text

    # Ticket #22 : les exercices sont désormais sur l'espace S'entraîner, pas Cours.
    response = client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    assert response.text.count("Exercice 1 —") == 1
    assert response.text.count("Exercice 2 —") == 1
    assert response.text.count("Exercice 9 —") == 1
    assert response.text.count("Exercice 11 —") == 1


def test_untouched_exercises_keep_their_exact_original_markdown_text(client, db_session):
    """Les exercices 3, 4, 5, 6, 7, 8, 10, 12 ne sont pas modifiés par ce ticket."""
    seed()
    uaa = _mc01_uaa(db_session)
    markdown_text = "\n".join(
        block.content for block in uaa.lesson_blocks if block.type == BlockType.MARKDOWN
    )

    for heading, correction_excerpt in [
        (
            "## Exercice 3 — expliquer",
            "Le processeur doit être compatible avec le socket de la carte mère",
        ),
        ("## Exercice 4 — diagnostiquer", "la carte graphique (ou la connexion GPU/écran)"),
        ("## Exercice 5 — expliquer", "La RAM est une mémoire de travail temporaire"),
        ("## Exercice 6 — expliquer une ambiguïté", "32 Go » peut désigner la RAM"),
        ("## Exercice 7 — expliquer", "Un GPU intégré est directement intégré au CPU"),
        ("## Exercice 8 — expliquer", "750 W est la puissance **maximale**"),
        ("## Exercice 10 — diagnostiquer", "La RAM est la piste la plus probable"),
        ("## Exercice 12 — vocabulaire", "Mémoire vive → RAM"),
    ]:
        assert heading in markdown_text
        assert correction_excerpt in markdown_text


def test_mc01_block_count_matches_mc01_blocks_constant(client, db_session):
    seed()
    uaa = _mc01_uaa(db_session)
    assert len(uaa.lesson_blocks) == len(MC01_BLOCKS) == 23


def test_seed_is_idempotent_after_migration(client, db_session):
    """Un second appel à seed() après la migration ne crée ni ne supprime plus rien."""
    seed()
    uaa = _mc01_uaa(db_session)
    block_count_after_first = len(uaa.lesson_blocks)

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    assert len(uaa.lesson_blocks) == block_count_after_first


def test_staging_already_seeded_before_ticket_21_is_migrated_without_reset(client, db_session):
    """Reproduit un staging seedé AVANT le ticket #21 : les deux blocs Markdown portent
    encore leur ANCIEN titre (aujourd'hui dans MC01_OBSOLETE_TITLES) avec l'ancien texte
    complet (Ex1+Ex2, puis Ex9+Ex10+Ex11+Ex12). Un seed() unique doit retirer ces deux
    blocs obsolètes et ajouter les 7 blocs de remplacement (4 structurés + 2 Markdown
    réduits + le bloc IA déjà présent), sans jamais appeler reset()."""
    informatique = Subject(name=INFORMATIQUE_SUBJECT_NAME, slug="informatique")
    db_session.add(informatique)
    db_session.flush()
    ampcr = Module(code="AMPCR", slug="ampcr", subject=informatique)
    db_session.add(ampcr)
    db_session.flush()
    uaa = UAA(
        code="MC01",
        title="Architecture générale d'un PC",
        slug="ampcr-mc01",
        position=1,
        is_published=True,
        module=ampcr,
    )
    db_session.add(uaa)
    db_session.flush()

    old_titles = sorted(MC01_OBSOLETE_TITLES)
    assert len(old_titles) == 2
    db_session.add(
        LessonBlock(
            uaa=uaa,
            title=old_titles[0],
            type=BlockType.MARKDOWN,
            content="## Exercice 1 — classer\n\nAncien contenu pré-#21.",
            position=13,
            is_published=True,
        )
    )
    db_session.add(
        LessonBlock(
            uaa=uaa,
            title=old_titles[1],
            type=BlockType.MARKDOWN,
            content="## Exercice 9 — reconstruire\n\nAncien contenu pré-#21.",
            position=15,
            is_published=True,
        )
    )
    db_session.commit()

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    remaining_titles = {block.title for block in uaa.lesson_blocks}
    assert old_titles[0] not in remaining_titles
    assert old_titles[1] not in remaining_titles

    editorial_blocks = [
        block for block in uaa.lesson_blocks if block.type == BlockType.EDITORIAL_EXERCISE
    ]
    assert len(editorial_blocks) == 4

    # Ticket #22 : le contenu migré vit désormais sur l'espace S'entraîner, pas Cours —
    # on vérifie l'absence de l'ancien contenu sur les deux pages.
    course_response = client.get("/uaa/ampcr-mc01")
    assert course_response.status_code == 200
    assert "Ancien contenu pré-#21" not in course_response.text

    practice_response = client.get("/uaa/ampcr-mc01/practice")
    assert practice_response.status_code == 200
    assert "Ancien contenu pré-#21" not in practice_response.text


def test_mc02_and_mc03_unaffected(client, db_session):
    seed()

    mc02 = db_session.query(UAA).filter_by(code="MC02").first()
    mc03 = db_session.query(UAA).filter_by(code="MC03").first()
    assert len(mc02.lesson_blocks) == len(MC02_BLOCKS)
    assert len(mc03.lesson_blocks) == len(MC03_BLOCKS)

    assert client.get("/uaa/ampcr-mc02").status_code == 200
    assert client.get("/uaa/ampcr-mc03").status_code == 200


def test_mathematiques_unaffected(client, db_session):
    seed()

    response = client.get("/uaa/mb32-uaa1")
    assert response.status_code == 200
    assert "Fonction constante" in response.text

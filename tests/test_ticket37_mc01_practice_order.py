"""Ticket #37 — MC01 Practice : corriger l'ordre d'affichage des exercices 9 et 11.

Cause (voir docs/claude-reports/2026-09-17_ticket-37_mc01-practice-order.md) : `_seed_uaa`
ne met jamais à jour `position` pour un bloc déjà existant (matché par titre) — par
conception, puisque `position` est modifiable depuis l'admin (voir `app/admin.py`) et ne
doit donc jamais être silencieusement écrasée pour un bloc quelconque. Or 6 blocs MC01
existaient déjà AVANT le ticket #29 (créés au #21 ou avant : AI_EXERCISE, fiche mémo,
examen, corrigé, Exercice 9, Exercice 11) et ont gardé leur position de l'époque, tandis
que les 8 nouveaux blocs d'exercices insérés par #29 ont reçu la position actuellement
déclarée dans `MC01_BLOCKS` — d'où des positions dupliquées et un ordre d'affichage
incorrect.

Le correctif (`MC01_PRACTICE_REPOSITION_TITLES` + `_seed_uaa(reposition_titles=...,
repositioned=...)`) resynchronise, de façon scopée et explicite, uniquement ces 6 titres
sur la position déjà déclarée dans `MC01_BLOCKS` — jamais un mécanisme générique appliqué
à tous les blocs."""

from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.seed import (
    INFORMATIQUE_SUBJECT_NAME,
    MC01_BLOCKS,
    MC01_PRACTICE_REPOSITION_TITLES,
    seed,
)

EXPECTED_EXERCISE_TITLES_IN_ORDER = [
    "Exercice 1 — Matériel ou logiciel (classification)",
    "Exercice 2 — Unité centrale ou périphérique (classification)",
    "Exercice 3 — Compatibilité CPU/carte mère (réponse rédigée)",
    "Exercice 4 — Diagnostic : rien ne s'affiche (diagnostic)",
    "Exercice 5 — RAM et stockage (réponse rédigée)",
    "Exercice 6 — Ambiguïté des Go (réponse rédigée)",
    "Exercice 7 — GPU intégré ou dédié (réponse rédigée)",
    "Exercice 8 — Puissance de l'alimentation (réponse rédigée)",
    "Exercice 9 — Lancement d'un programme (ordering)",
    "Exercice 10 — Diagnostic : le PC ralentit (diagnostic)",
    "Exercice 11 — Entrée, sortie ou mixte (classification)",
    "Exercice 12 — Vocabulaire FR/EN (vocabulaire)",
]

# Positions historiques réellement observées sur staging avant ce ticket (voir le rapport
# de validation staging du #29) : les 6 blocs créés avant #29 ont gardé leur ancienne
# position, en collision avec celle des blocs insérés par #29.
_LEGACY_POSITIONS = {
    "Architecture d'un PC — Génère ton propre exercice (IA)": 16,
    "Fiche mémo — Architecture générale d'un PC": 17,
    "Exercice 9 — Lancement d'un programme (ordering)": 17,
    "Examen final — Architecture générale d'un PC (10 questions, 20 points)": 18,
    "Exercice 11 — Entrée, sortie ou mixte (classification)": 18,
    "Examen final — Corrigé (réservé formateur, non publié)": 19,
}


def _mc01_uaa(db_session):
    return db_session.query(UAA).filter_by(code="MC01").first()


_NEW_TICKET_29_EXERCISE_TITLES = {
    "Exercice 3 — Compatibilité CPU/carte mère (réponse rédigée)",
    "Exercice 4 — Diagnostic : rien ne s'affiche (diagnostic)",
    "Exercice 5 — RAM et stockage (réponse rédigée)",
    "Exercice 6 — Ambiguïté des Go (réponse rédigée)",
    "Exercice 7 — GPU intégré ou dédié (réponse rédigée)",
    "Exercice 8 — Puissance de l'alimentation (réponse rédigée)",
    "Exercice 10 — Diagnostic : le PC ralentit (diagnostic)",
    "Exercice 12 — Vocabulaire FR/EN (vocabulaire)",
}


def _build_drifted_staging_state(db_session) -> UAA:
    """Reconstruit fidèlement l'état réel de staging avant ce ticket : les 28 blocs de
    MC01_BLOCKS existent déjà, avec les 6 titres de `_LEGACY_POSITIONS` ayant gardé leur
    position d'avant #29. L'ordre d'INSERTION reproduit aussi l'historique réel — les
    blocs antérieurs à #29 (dont Ex9/Ex11, créés au #21) sont insérés avant les 8 blocs
    d'exercices ajoutés par #29 (dont Ex5) — car SQLite départage les positions égales par
    l'ordre d'insertion (rowid), exactement comme observé sur le staging réel où Ex9/Ex11
    (id plus petit, créés avant) s'affichaient avant Ex5/Ex6 (id plus grand, créés après)
    malgré une position numériquement plus grande."""
    informatique = Subject(name=INFORMATIQUE_SUBJECT_NAME, slug="informatique")
    db_session.add(informatique)
    db_session.flush()
    ampcr = Module(code="AMPCR", slug="ampcr", subject=informatique)
    db_session.add(ampcr)
    db_session.flush()
    uaa = UAA(
        code="MC01", title="Architecture générale d'un PC", slug="ampcr-mc01",
        position=1, is_published=True, module=ampcr,
    )
    db_session.add(uaa)
    db_session.flush()

    def _add(block_data: dict) -> None:
        position = _LEGACY_POSITIONS.get(block_data["title"], block_data["position"])
        db_session.add(LessonBlock(
            uaa=uaa, title=block_data["title"], type=block_data["type"],
            content=block_data["content"], position=position,
            is_published=block_data["is_published"], space=block_data["space"],
        ))

    legacy_blocks = [
        b for b in MC01_BLOCKS if b["title"] not in _NEW_TICKET_29_EXERCISE_TITLES
    ]
    new_ticket_29_blocks = [
        b for b in MC01_BLOCKS if b["title"] in _NEW_TICKET_29_EXERCISE_TITLES
    ]
    for block_data in legacy_blocks:
        _add(block_data)
    for block_data in new_ticket_29_blocks:
        _add(block_data)

    db_session.commit()
    return uaa


def _practice_exercise_titles_in_order(client) -> list[str]:
    response = client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    import re

    return re.findall(r"Exercice \d+ — [^<]*", response.text)


# --- Reproduction du problème -----------------------------------------------------------


def test_drifted_state_reproduces_the_reported_wrong_order(client, db_session):
    """Confirme que l'état reconstruit reproduit bien l'ordre erroné observé en staging
    (1, 2, 3, 4, 9, 5, 11, 6, 7, 8, 10, 12) — avant toute correction."""
    _build_drifted_staging_state(db_session)

    titles = _practice_exercise_titles_in_order(client)
    numbers = [int(t.split()[1]) for t in titles]
    assert numbers == [1, 2, 3, 4, 9, 5, 11, 6, 7, 8, 10, 12]


def test_drifted_state_has_position_collisions(db_session):
    _build_drifted_staging_state(db_session)
    uaa = _mc01_uaa(db_session)
    positions = [b.position for b in uaa.lesson_blocks]
    assert len(positions) != len(set(positions))


# --- Correction par migration additive/idempotente ---------------------------------------


def test_seed_fixes_the_order_on_a_drifted_staging_state(client, db_session):
    _build_drifted_staging_state(db_session)

    seed()
    db_session.expire_all()

    titles = _practice_exercise_titles_in_order(client)
    numbers = [int(t.split()[1]) for t in titles]
    assert numbers == list(range(1, 13))


def test_seed_removes_all_position_collisions(db_session):
    _build_drifted_staging_state(db_session)

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    positions = [b.position for b in uaa.lesson_blocks]
    assert len(positions) == len(set(positions)), f"positions dupliquées : {positions}"


def test_fresh_seed_already_has_the_correct_order(client, db_session):
    """Une base jamais seedée (ou déjà à jour) doit directement afficher le bon ordre —
    la migration ne doit pas être requise pour un nouveau déploiement."""
    seed()

    titles = _practice_exercise_titles_in_order(client)
    numbers = [int(t.split()[1]) for t in titles]
    assert numbers == list(range(1, 13))


def test_seed_second_pass_is_idempotent_no_further_change(db_session):
    """Un second seed après correction ne modifie plus rien (aucun nouveau
    repositionnement, aucune position modifiée)."""
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    positions_after_first_fix = {b.title: b.position for b in uaa.lesson_blocks}

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    positions_after_second_pass = {b.title: b.position for b in uaa.lesson_blocks}

    assert positions_after_second_pass == positions_after_first_fix


def test_seed_second_pass_creates_no_duplicate_blocks(db_session):
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    count_after_first = len(uaa.lesson_blocks)

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    assert len(uaa.lesson_blocks) == count_after_first

    titles = [b.title for b in uaa.lesson_blocks]
    assert len(titles) == len(set(titles))


# --- Non-régression : contenu, espace, IA, correction locale -----------------------------


def test_repositioning_never_changes_pedagogical_content(db_session):
    """Le repositionnement ne touche que `position` — jamais `content`/`title`/
    `is_published`/`space` d'un bloc déjà existant."""
    _build_drifted_staging_state(db_session)
    uaa = _mc01_uaa(db_session)
    content_before = {b.title: (b.content, b.is_published, b.space) for b in uaa.lesson_blocks}

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    content_after = {b.title: (b.content, b.is_published, b.space) for b in uaa.lesson_blocks}

    assert content_after == content_before


def test_twelve_exercises_still_present_and_structured_after_fix(db_session):
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    editorial_blocks = [b for b in uaa.lesson_blocks if b.type == BlockType.EDITORIAL_EXERCISE]
    assert len(editorial_blocks) == 12
    assert all(b.space == BlockSpace.PRACTICE for b in editorial_blocks)

    markdown_exercise_titles = [
        b.title for b in uaa.lesson_blocks
        if b.type == BlockType.MARKDOWN and "exercice" in b.title.lower()
    ]
    assert markdown_exercise_titles == []


def test_course_blocks_unaffected_by_repositioning(db_session):
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    course_blocks = [b for b in uaa.lesson_blocks if b.space == BlockSpace.COURSE]
    assert len(course_blocks) == 13  # 12 chapitres + fiche mémo


def test_exam_blocks_unaffected_by_repositioning(db_session):
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    exam_blocks = [b for b in uaa.lesson_blocks if b.space == BlockSpace.EXAM]
    assert len(exam_blocks) == 2
    exam_titles = {b.title for b in exam_blocks}
    assert exam_titles == {
        "Examen final — Architecture générale d'un PC (10 questions, 20 points)",
        "Examen final — Corrigé (réservé formateur, non publié)",
    }


def test_local_correction_still_works_after_fix(client, db_session):
    """Classification (Exercice 1) toujours corrigeable localement après repositionnement."""
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    ex1 = next(b for b in uaa.lesson_blocks if b.title.startswith("Exercice 1"))

    response = client.post(
        f"/practice/api/editorial/{ex1.id}/verify",
        json={"exercise_id": "mc01-ex1", "answer": [0, 1, 0, 1, 0]},
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_ai_exercise_block_still_present_and_unaffected(db_session):
    _build_drifted_staging_state(db_session)
    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    ai_blocks = [b for b in uaa.lesson_blocks if b.type == BlockType.AI_EXERCISE]
    assert len(ai_blocks) == 1
    assert ai_blocks[0].title == "Architecture d'un PC — Génère ton propre exercice (IA)"
    assert ai_blocks[0].space == BlockSpace.PRACTICE


def test_reposition_titles_scoped_to_exactly_the_drifted_blocks():
    """La liste des titres repositionnables est bornée et explicite (pas de mécanisme
    générique) : exactement les 6 blocs connus pour avoir dérivé."""
    assert MC01_PRACTICE_REPOSITION_TITLES == frozenset(_LEGACY_POSITIONS)


def test_declared_mc01_blocks_positions_are_already_sequential_and_unique():
    """La source de vérité (MC01_BLOCKS) elle-même ne doit plus jamais contenir de
    collision : condition nécessaire pour que la migration produise un ordre correct."""
    positions = [block["position"] for block in MC01_BLOCKS]
    assert len(positions) == len(set(positions))
    assert sorted(positions) == list(range(1, len(MC01_BLOCKS) + 1))


def test_exercise_positions_in_mc01_blocks_match_exercise_numbering():
    """Les positions 13 à 24 de MC01_BLOCKS doivent correspondre exactement, dans
    l'ordre, aux exercices 1 à 12 — condition pédagogique du ticket."""
    exercise_blocks = [
        block for block in MC01_BLOCKS if block["title"].startswith("Exercice ")
    ]
    exercise_blocks_sorted_by_position = sorted(exercise_blocks, key=lambda b: b["position"])
    titles_by_position = [b["title"] for b in exercise_blocks_sorted_by_position]
    assert titles_by_position == EXPECTED_EXERCISE_TITLES_IN_ORDER

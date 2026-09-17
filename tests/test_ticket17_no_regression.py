"""Non-régression du ticket #17 (socle editorial_exercise) : `app/seed.py` n'était pas
modifié par ce ticket — aucun des 12 exercices existants de MC01 ne pouvait être migré sans
le dénaturer avec la première tranche de types (voir
docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md). MC02, MC03 et
Mathématiques restent strictement inchangés, et le seed reste additif et idempotent.

Mise à jour ticket #21 : 4 des 12 exercices de MC01 (1, 2, 9, 11) sont désormais migrés
vers des blocs `editorial_exercise` (classification/ordering) — voir
docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md et
tests/test_ticket21_no_regression.py pour la non-régression spécifique à ce ticket. Le
test ci-dessous est ajusté en conséquence (4 blocs editorial_exercise attendus, et non 0)
mais conserve son rôle : vérifier que les 12 exercices restent tous accessibles, quel que
soit leur type de bloc.

Mise à jour ticket #22 : les 12 exercices ne sont plus servis sur `/uaa/{slug}` (page
Cours, théorie uniquement) mais sur `/uaa/{slug}/practice` (espace S'entraîner) — voir
docs/claude-reports/2026-09-16_ticket-22_separation-cours-practice-exam.md et
tests/test_ticket22_no_regression.py.

Mise à jour ticket #29 : les 8 exercices restants (3, 4, 5, 6, 7, 8, 10, 12) sont à leur
tour migrés en blocs `editorial_exercise` (long_answer/diagnostic/vocabulary) — MC01 ne
contient plus AUCUN bloc Markdown d'exercice. Voir
docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md et
tests/test_ticket29_no_regression.py."""

from app.models import UAA, BlockType, LessonBlock
from app.seed import MC01_BLOCKS, MC02_BLOCKS, MC03_BLOCKS, seed


def test_mc01_content_is_untouched_by_ticket_17(authenticated_client, db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="MC01").first()
    assert uaa is not None
    assert len(uaa.lesson_blocks) == len(MC01_BLOCKS)

    editorial_blocks = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.EDITORIAL_EXERCISE)
        .count()
    )
    # Les 12 exercices MC01 sont désormais tous des blocs editorial_exercise (4 depuis
    # #21, 8 de plus depuis #29) — voir docstring du module.
    assert editorial_blocks == 12

    # Ticket #22 : les 12 exercices sont désormais sur l'espace S'entraîner, pas Cours.
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    for n in range(1, 13):
        assert f"Exercice {n} —" in response.text


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

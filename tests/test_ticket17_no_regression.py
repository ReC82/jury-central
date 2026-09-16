"""Non-régression du ticket #17 (socle editorial_exercise) : `app/seed.py` n'est pas
modifié par ce ticket — aucun des 12 exercices existants de MC01 ne peut être migré sans
le dénaturer avec la première tranche de types (voir
docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md). Ces tests confirment que
MC01, MC02, MC03 et Mathématiques restent strictement inchangés, et que le seed reste
additif et idempotent."""

from app.models import UAA, BlockType, LessonBlock
from app.seed import MC01_BLOCKS, MC02_BLOCKS, MC03_BLOCKS, seed


def test_mc01_content_is_untouched_by_ticket_17(client, db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="MC01").first()
    assert uaa is not None
    assert len(uaa.lesson_blocks) == len(MC01_BLOCKS)

    editorial_blocks = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.EDITORIAL_EXERCISE)
        .count()
    )
    assert editorial_blocks == 0  # aucun exercice MC01 migré dans ce ticket

    response = client.get("/uaa/ampcr-mc01")
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

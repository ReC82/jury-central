"""Tests d'intégration du ticket #14 : Informatique AMPCR, mini-cours 03.

Vérifie que la matière est navigable après MC02, que le cours affiche la matière
obligatoire sans casser MC01/MC02/Mathématiques, que le corrigé de l'examen n'est jamais
servi publiquement, et que le moteur IA existant (aucun second moteur) génère/corrige bien
dans le contexte pédagogique borné propre à MC03.
"""

from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, BlockType, LessonBlock
from app.seed import MC03_BLOCKS, seed


def test_informatique_mc03_is_accessible_after_mc02(client, db_session):
    seed()

    module_response = client.get("/modules/ampcr")
    assert module_response.status_code == 200
    assert "/uaa/ampcr-mc01" in module_response.text
    assert "/uaa/ampcr-mc02" in module_response.text
    assert "/uaa/ampcr-mc03" in module_response.text

    uaa_response = client.get("/uaa/ampcr-mc03")
    assert uaa_response.status_code == 200
    assert "CPU et mémoire RAM" in uaa_response.text


def test_mc03_covers_the_mandatory_content(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc03")
    assert response.status_code == 200
    text = response.text

    for expected in [
        "Rôle du CPU et cycle d'exécution",
        "Cœurs, threads et fréquence",
        "IPC et hiérarchie de cache (L1/L2/L3)",
        "Architecture 32/64 bits",
        "Socket, génération et compatibilité",
        "TDP, refroidissement et throttling",
        "CPU avec ou sans graphique intégré",
        "Rôle et capacité de la RAM",
        "DDR3, DDR4, DDR5",
        "DIMM, SO-DIMM et canaux mémoire",
        "Capacité maximale et compatibilité",
        "XMP/EXPO et ECC",
        "RAM, VRAM et stockage",
        "Goulot d'étranglement et symptômes",
        "Diagnostic RAM et CPU/thermique",
        "Unités et pièges d'examen",
        "Vocabulaire FR/EN",
    ]:
        assert expected in text, f"section manquante : {expected}"

    # Nuances explicitement exigées par le ticket #14 : ne jamais transformer TDP en
    # "consommation", GHz en mesure absolue, ni 64 bits en "deux fois plus rapide".
    assert "pas une mesure exacte de consommation" in text or "pas une mesure exacte de" in text
    assert "deux fois plus" in text
    assert "DDR4 en plus rapide" in text


def test_mc03_has_at_least_ten_exercises_with_hidden_corrections(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc03")
    text = response.text

    for n in range(1, 13):
        assert f"Exercice {n} —" in text, f"exercice {n} manquant"
    assert text.count("Correction :") >= 12


def test_mc03_exam_is_published_without_visible_correction(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc03")
    text = response.text

    assert "Examen final" in text
    assert "Question 10 (2 pts)" in text
    assert "Corrigé" not in text
    assert "notation qualitative" not in text


def test_mc03_exam_correction_block_exists_but_is_unpublished(db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="MC03").first()
    assert uaa is not None

    correction_block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, title="Examen final — Corrigé (réservé formateur, non publié)")
        .first()
    )
    assert correction_block is not None
    assert correction_block.is_published is False
    assert len(uaa.lesson_blocks) == len(MC03_BLOCKS)


def test_mc03_has_registered_pedagogical_context():
    context = get_context("ampcr-mc03")
    assert context is not None
    assert "CPU" in context.course_title
    assert "ram" in " ".join(context.allowed_notions).lower()
    assert "2.3.2" in " ".join(context.competencies)
    assert "TDP" in context.constraints


def _get_ai_block_id(db_session, uaa_code: str) -> int:
    uaa = db_session.query(UAA).filter_by(code=uaa_code).first()
    block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.AI_EXERCISE)
        .first()
    )
    assert block is not None
    return block.id


def test_mc03_ai_generation_uses_the_shared_engine_with_mc03_context(
    client, db_session, monkeypatch
):
    """Le même moteur générique (#10) est réutilisé, avec le contexte MC03 — pas de
    second moteur IA."""
    seed()
    block_id = _get_ai_block_id(db_session, "MC03")

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "facile"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statement_token"]

    called_context, difficulty = fake.generate_calls[0]
    assert called_context.course_key == "ampcr-mc03"
    assert difficulty == "facile"

    correct_response = client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": block_id,
            "exercise_statement": data["statement"],
            "exercise_type": data["exercise_type"],
            "difficulty": data["difficulty"],
            "statement_token": data["statement_token"],
            "answer": "La RAM est volatile, le stockage est persistant.",
        },
    )
    assert correct_response.status_code == 200
    assert fake.correct_calls[0][0] == "ampcr-mc03"


def test_mc01_mc02_and_mathematiques_unaffected_by_mc03(client, db_session):
    seed()

    mc01_response = client.get("/uaa/ampcr-mc01")
    assert mc01_response.status_code == 200
    assert "Architecture générale d'un PC" in mc01_response.text

    mc02_response = client.get("/uaa/ampcr-mc02")
    assert mc02_response.status_code == 200
    assert "Carte mère, formats et connectiques" in mc02_response.text

    math_response = client.get("/uaa/mb32-uaa1")
    assert math_response.status_code == 200
    assert "Fonction constante" in math_response.text

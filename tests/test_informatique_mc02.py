"""Tests d'intégration du ticket #12 : Informatique AMPCR, mini-cours 02.

Vérifie que la matière est navigable après MC01, que le cours affiche la matière
obligatoire sans casser MC01/Mathématiques, que le corrigé de l'examen n'est jamais servi
publiquement, et que le moteur IA existant (aucun second moteur) génère/corrige bien dans
le contexte pédagogique borné propre à MC02.
"""

from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, BlockType, LessonBlock
from app.seed import MC02_BLOCKS, seed


def test_informatique_mc02_is_accessible_after_mc01(client, db_session):
    seed()

    module_response = client.get("/modules/ampcr")
    assert module_response.status_code == 200
    assert "/uaa/ampcr-mc01" in module_response.text
    assert "/uaa/ampcr-mc02" in module_response.text

    uaa_response = client.get("/uaa/ampcr-mc02")
    assert uaa_response.status_code == 200
    assert "Carte mère, formats et connectiques" in uaa_response.text


def test_mc02_covers_the_mandatory_content(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc02")
    assert response.status_code == 200
    text = response.text

    for expected in [
        "Rôle détaillé de la carte mère",
        "Formats ATX, micro-ATX, Mini-ITX",
        "Socket CPU et compatibilité",
        "Chipset",
        "Slots RAM (DIMM)",
        "PCI Express (PCIe)",
        "Stockage sur la carte mère (SATA, M.2)",
        "Alimentation interne (ATX 24 broches, EPS)",
        "Connecteurs internes",
        "Connectique arrière (E/S)",
        "F_PANEL",
        "BIOS/UEFI et POST",
        "Méthode de compatibilité",
        "Diagnostic professionnel",
        "Sécurité et décharge électrostatique (ESD)",
        "Vocabulaire FR/EN",
    ]:
        assert expected in text, f"section manquante : {expected}"

    assert "Motherboard" in text
    assert "M.2" in text


def test_mc02_has_at_least_ten_exercises_with_hidden_corrections(client, db_session):
    """Depuis le ticket #22, les exercices sont sur la page S'entraîner."""
    seed()

    response = client.get("/uaa/ampcr-mc02/practice")
    text = response.text

    for n in range(1, 13):
        assert f"Exercice {n} —" in text, f"exercice {n} manquant"
    assert text.count("Correction :") >= 12


def test_mc02_exam_is_published_without_visible_correction(client, db_session):
    """Depuis le ticket #22, l'examen est sur la page S'évaluer."""
    seed()

    response = client.get("/uaa/ampcr-mc02/exam")
    text = response.text

    assert "Examen final" in text
    assert "Question 10 (2 pts)" in text
    assert "Corrigé" not in text
    assert "notation qualitative" not in text


def test_mc02_course_page_no_longer_contains_practice_or_exam_content(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc02")
    text = response.text

    assert response.status_code == 200
    for n in range(1, 13):
        assert f"Exercice {n} —" not in text
    assert "Examen final" not in text


def test_mc02_exam_correction_block_exists_but_is_unpublished(db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="MC02").first()
    assert uaa is not None

    correction_block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, title="Examen final — Corrigé (réservé formateur, non publié)")
        .first()
    )
    assert correction_block is not None
    assert correction_block.is_published is False
    assert len(uaa.lesson_blocks) == len(MC02_BLOCKS)


def test_mc02_has_registered_pedagogical_context():
    context = get_context("ampcr-mc02")
    assert context is not None
    assert "Carte mère" in context.course_title
    assert "socket" in " ".join(context.allowed_notions).lower()
    assert "1.2.3" in " ".join(context.competencies)
    assert "mini-cours 03" in context.constraints


def _get_ai_block_id(db_session, uaa_code: str) -> int:
    uaa = db_session.query(UAA).filter_by(code=uaa_code).first()
    block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.AI_EXERCISE)
        .first()
    )
    assert block is not None
    return block.id


def test_mc02_ai_generation_uses_the_shared_engine_with_mc02_context(
    client, db_session, monkeypatch
):
    """Le même moteur générique (#10) est réutilisé, avec le contexte MC02 — pas de
    second moteur IA."""
    seed()
    block_id = _get_ai_block_id(db_session, "MC02")

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "difficile"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statement_token"]

    # Le fournisseur a bien reçu le contexte pédagogique de MC02, pas celui de MC01.
    called_context, difficulty = fake.generate_calls[0]
    assert called_context.course_key == "ampcr-mc02"
    assert difficulty == "difficile"

    correct_response = client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": block_id,
            "exercise_statement": data["statement"],
            "exercise_type": data["exercise_type"],
            "difficulty": data["difficulty"],
            "statement_token": data["statement_token"],
            "answer": "Le socket doit correspondre et le BIOS doit être à jour.",
        },
    )
    assert correct_response.status_code == 200
    assert fake.correct_calls[0][0] == "ampcr-mc02"


def test_mc01_and_mathematiques_unaffected_by_mc02(client, db_session):
    seed()

    mc01_response = client.get("/uaa/ampcr-mc01")
    assert mc01_response.status_code == 200
    assert "Architecture générale d'un PC" in mc01_response.text

    math_response = client.get("/uaa/mb32-uaa1")
    assert math_response.status_code == 200
    assert "Fonction constante" in math_response.text

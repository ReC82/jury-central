"""Tests d'intégration du ticket #16 : Informatique AMPCR, mini-cours 04.

Vérifie que la matière est navigable après MC03, que le cours affiche la matière
obligatoire sans casser MC01/MC02/MC03/Mathématiques, que le corrigé de l'examen n'est
jamais servi publiquement, que le moteur IA existant (aucun second moteur) génère/corrige
bien dans le contexte pédagogique borné propre à MC04, et que les pièges pédagogiques
explicitement exigés par le ticket sont bien présents dans le contenu (M.2 ≠ NVMe, SMART
ne garantit rien, TBW n'est pas une date de panne, synchronisation ≠ sauvegarde, jamais
formater en premier réflexe, jamais défragmenter un SSD).
"""

from app.ai.context import get_context
from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, BlockType, LessonBlock
from app.seed import MC04_BLOCKS, seed


def test_informatique_mc04_is_accessible_after_mc03(client, db_session):
    seed()

    module_response = client.get("/modules/ampcr")
    assert module_response.status_code == 200
    assert "/uaa/ampcr-mc01" in module_response.text
    assert "/uaa/ampcr-mc02" in module_response.text
    assert "/uaa/ampcr-mc03" in module_response.text
    assert "/uaa/ampcr-mc04" in module_response.text

    uaa_response = client.get("/uaa/ampcr-mc04")
    assert uaa_response.status_code == 200
    assert "Stockage : HDD, SSD SATA et NVMe" in uaa_response.text


def test_mc04_covers_the_mandatory_content(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc04")
    assert response.status_code == 200
    text = response.text

    for expected in [
        "Stockage persistant : rôle et unités",
        "Disque dur (HDD)",
        "SSD : NAND et contrôleur",
        "SSD SATA",
        "M.2 et NVMe",
        "Endurance et fiabilité (TBW, wear leveling, TRIM)",
        "SMART et diagnostic de santé",
        "Sauvegarde : notions et règle 3-2-1",
        "Ransomware et synchronisation",
        "Choisir la bonne technologie",
        "Diagnostic stockage",
        "Sécurité et bonnes pratiques",
        "Vocabulaire FR/EN",
        "Ancien vocabulaire du référentiel",
    ]:
        assert expected in text, f"section manquante : {expected}"

    assert "IDE / PATA" in text or "IDE/PATA" in text


def test_mc04_respects_the_mandatory_pedagogical_nuances(client, db_session):
    """Les pièges explicitement exigés par le ticket #16 doivent être présents.

    Les assertions portent sur des segments de texte non coupés par le rendu Markdown
    (une expression entièrement en gras, ou entièrement hors gras) pour rester fiables
    quel que soit le HTML généré autour (<strong>...</strong>).
    """
    seed()

    response = client.get("/uaa/ampcr-mc04")
    text = response.text

    assert "peut être" in text and "SATA" in text and "NVMe" in text  # M.2 ≠ NVMe
    assert "ne garantit absolument pas" in text  # SMART
    assert "date de mort certaine" in text  # TBW
    assert "n'est donc pas, à elle seule, une protection" in text  # sync != backup
    assert "première étape d'un diagnostic" in text  # jamais formater en premier
    assert "Ne jamais recommander de défragmenter un SSD" in text


def test_mc04_has_at_least_ten_exercises_with_hidden_corrections(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc04")
    text = response.text

    for n in range(1, 13):
        assert f"Exercice {n} —" in text, f"exercice {n} manquant"
    assert text.count("Correction :") >= 12


def test_mc04_exam_is_published_without_visible_correction(client, db_session):
    seed()

    response = client.get("/uaa/ampcr-mc04")
    text = response.text

    assert "Examen final" in text
    assert "Question 10 (2 pts)" in text
    assert "Corrigé" not in text
    assert "notation qualitative" not in text


def test_mc04_exam_correction_block_exists_but_is_unpublished(db_session):
    seed()

    uaa = db_session.query(UAA).filter_by(code="MC04").first()
    assert uaa is not None

    correction_block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, title="Examen final — Corrigé (réservé formateur, non publié)")
        .first()
    )
    assert correction_block is not None
    assert correction_block.is_published is False
    assert len(uaa.lesson_blocks) == len(MC04_BLOCKS)


def test_mc04_has_registered_pedagogical_context():
    context = get_context("ampcr-mc04")
    assert context is not None
    assert "Stockage" in context.course_title
    assert "nvme" in " ".join(context.allowed_notions).lower()
    assert "2.3.2" in " ".join(context.competencies)
    assert "défragmentation" in context.constraints.lower() or "formater" in context.constraints.lower()


def _get_ai_block_id(db_session, uaa_code: str) -> int:
    uaa = db_session.query(UAA).filter_by(code=uaa_code).first()
    block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.AI_EXERCISE)
        .first()
    )
    assert block is not None
    return block.id


def test_mc04_ai_generation_uses_the_shared_engine_with_mc04_context(
    client, db_session, monkeypatch
):
    """Le même moteur générique (#10) est réutilisé, avec le contexte MC04 — pas de
    second moteur IA."""
    seed()
    block_id = _get_ai_block_id(db_session, "MC04")

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "difficile"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statement_token"]

    called_context, difficulty = fake.generate_calls[0]
    assert called_context.course_key == "ampcr-mc04"
    assert difficulty == "difficile"

    correct_response = client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": block_id,
            "exercise_statement": data["statement"],
            "exercise_type": data["exercise_type"],
            "difficulty": data["difficulty"],
            "statement_token": data["statement_token"],
            "answer": "Un SSD NVMe utilise le protocole PCIe, contrairement à un SSD SATA.",
        },
    )
    assert correct_response.status_code == 200
    assert fake.correct_calls[0][0] == "ampcr-mc04"


def test_mc01_mc02_mc03_and_mathematiques_unaffected_by_mc04(client, db_session):
    seed()

    mc01_response = client.get("/uaa/ampcr-mc01")
    assert mc01_response.status_code == 200
    assert "Architecture générale d'un PC" in mc01_response.text

    mc02_response = client.get("/uaa/ampcr-mc02")
    assert mc02_response.status_code == 200
    assert "Carte mère, formats et connectiques" in mc02_response.text

    mc03_response = client.get("/uaa/ampcr-mc03")
    assert mc03_response.status_code == 200
    assert "CPU et mémoire RAM" in mc03_response.text

    math_response = client.get("/uaa/mb32-uaa1")
    assert math_response.status_code == 200
    assert "Fonction constante" in math_response.text

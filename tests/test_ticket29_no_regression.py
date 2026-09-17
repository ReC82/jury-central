"""Tests du ticket #29 (« Entraînement — rendre toutes les questions répondables et
masquer les corrections ») :

- les 12 exercices MC01 sont tous des blocs `editorial_exercise` en espace PRACTICE ;
- les 12 sont répondables (contrôle de réponse adapté à leur type) ;
- aucune correction n'est jamais visible dans le HTML initial, pour aucun des 12 ;
- classification/ordering (#21) restent fonctionnels, non cassés par #29 ;
- correction déterministe inchangée (locale) ;
- correction sémantique IA utilise le contrat existant (#23), jamais un second moteur ;
- feedback uniquement après validation (jamais avant, quel que soit le type) ;
- aucun doublon avec les anciens blocs Markdown ;
- scénario de migration d'un staging déjà seedé avant #29 (forme post-#22, 23 blocs MC01,
  8 exercices encore en 3 blocs Markdown) vers la forme post-#29 (28 blocs, 12 exercices
  structurés), sans reset-db ;
- routes existantes (MC02/MC03/Mathématiques) non régressées."""

from pathlib import Path

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AIProviderError
from app.editorial_exercise import EditorialExerciseBlockConfig
from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.seed import (
    INFORMATIQUE_SUBJECT_NAME,
    MC01_BLOCKS,
    MC01_OBSOLETE_TITLES,
    MC02_BLOCKS,
    MC03_BLOCKS,
    seed,
)

ALL_EXERCISE_IDS = [f"mc01-ex{n}" for n in range(1, 13)]


def _mc01_uaa(db_session):
    return db_session.query(UAA).filter_by(code="MC01").first()


def _mc01_editorial_blocks(db_session):
    uaa = _mc01_uaa(db_session)
    return [b for b in uaa.lesson_blocks if b.type == BlockType.EDITORIAL_EXERCISE]


def _mc01_editorial_items(db_session):
    items = {}
    for block in _mc01_editorial_blocks(db_session):
        config = EditorialExerciseBlockConfig.from_json(block.content)
        for item in config.items:
            items[item.exercise_id] = item
    return items


# --- 12/12 présents, structurés, en PRACTICE -------------------------------------------


def test_all_twelve_mc01_exercises_are_editorial_exercise_blocks_in_practice(
    client, db_session
):
    seed()
    items = _mc01_editorial_items(db_session)
    assert set(items.keys()) == set(ALL_EXERCISE_IDS)

    for block in _mc01_editorial_blocks(db_session):
        assert block.space == BlockSpace.PRACTICE
        assert block.is_published is True


def test_no_mc01_exercise_remains_as_plain_markdown(client, db_session):
    """Plus aucun doublon : aucun bloc Markdown de MC01 ne contient de texte d'exercice
    (« ## Exercice N — »)."""
    seed()
    uaa = _mc01_uaa(db_session)
    markdown_blocks = [b for b in uaa.lesson_blocks if b.type == BlockType.MARKDOWN]
    for block in markdown_blocks:
        for n in range(1, 13):
            assert f"## Exercice {n} —" not in block.content, (block.title, n)


def test_mc01_block_count_is_28_after_ticket_29(client, db_session):
    seed()
    uaa = _mc01_uaa(db_session)
    assert len(uaa.lesson_blocks) == len(MC01_BLOCKS) == 28


# --- 12/12 répondables : chaque type expose le bon contrôle public ---------------------


def test_all_twelve_exercises_have_a_type_and_public_representation(client, db_session):
    """« Répondable » = le JSON public expose un `type` reconnu par le widget JS et jamais
    la solution — vérifié précisément type par type ci-dessous."""
    items = None

    def _load():
        nonlocal items
        items = _mc01_editorial_items(db_session)

    seed()
    _load()

    expected_types = {
        "mc01-ex1": "classification",
        "mc01-ex2": "classification",
        "mc01-ex3": "long_answer",
        "mc01-ex4": "diagnostic",
        "mc01-ex5": "long_answer",
        "mc01-ex6": "long_answer",
        "mc01-ex7": "long_answer",
        "mc01-ex8": "long_answer",
        "mc01-ex9": "ordering",
        "mc01-ex10": "diagnostic",
        "mc01-ex11": "classification",
        "mc01-ex12": "vocabulary",
    }
    for exercise_id, expected_type in expected_types.items():
        assert items[exercise_id].type == expected_type, exercise_id

    for exercise_id, item in items.items():
        public = item.to_public_dict()
        assert public["type"] in (
            "classification",
            "ordering",
            "long_answer",
            "diagnostic",
            "vocabulary",
        )
        # Un contrôle de réponse est toujours possible : soit des choix structurés
        # (classification/ordering), soit une zone de texte libre (les autres types, pas
        # de champ supplémentaire nécessaire au-delà du prompt).
        if public["type"] == "classification":
            assert len(public["categories"]) >= 2
            assert len(public["elements"]) >= 2
        elif public["type"] == "ordering":
            assert len(public["order_items"]) >= 2


def test_free_text_types_are_flagged_for_ai_widget_selection(client, db_session):
    """`requires_ai` (jamais un secret) permet au widget JS de choisir textarea + bouton
    « Corriger » plutôt qu'un champ court + « Vérifier »."""
    seed()
    items = _mc01_editorial_items(db_session)
    for exercise_id in ("mc01-ex3", "mc01-ex4", "mc01-ex5", "mc01-ex6", "mc01-ex7", "mc01-ex8",
                        "mc01-ex10", "mc01-ex12"):
        assert items[exercise_id].to_public_dict()["requires_ai"] is True
    for exercise_id in ("mc01-ex1", "mc01-ex2", "mc01-ex9", "mc01-ex11"):
        assert items[exercise_id].to_public_dict()["requires_ai"] is False


def test_javascript_widget_handles_all_twelve_types():
    """Garde-fou statique : le widget JS doit savoir construire un contrôle pour chacun des
    types réellement utilisés par MC01 (pas de dépendance sur un navigateur pour ce test)."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "app" / "static" / "js" / "editorial_exercise.js"
    )
    js = js_path.read_text(encoding="utf-8")
    for type_check in (
        'item.type === "classification"',
        'item.type === "ordering"',
        'item.type === "long_answer"',
        'item.type === "diagnostic"',
        'item.type === "vocabulary"',
    ):
        assert type_check in js


# --- Aucune correction visible au chargement --------------------------------------------


def test_no_correction_visible_in_initial_html_for_any_exercise(authenticated_client, db_session):
    seed()
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    text = response.text

    assert "Correction :" not in text
    for forbidden in (
        '"correct_index"',
        '"accepted_answers"',
        '"correct_categories"',
        '"correct_order"',
        '"explanation"',
        '"rubric"',
    ):
        assert forbidden not in text
    # Les explications réelles (grilles de correction) ne doivent apparaître nulle part.
    assert "Le processeur doit être compatible avec le socket" not in text
    assert "La RAM est la piste la plus probable" not in text


# --- Classification / ordering (#21) toujours fonctionnels -----------------------------


def test_classification_still_corrects_deterministically(authenticated_client, db_session):
    seed()
    block = next(
        b
        for b in _mc01_editorial_blocks(db_session)
        if "mc01-ex1" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex1", "answer": [0, 1, 0, 1, 0]},
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_ordering_still_corrects_deterministically(authenticated_client, db_session):
    seed()
    block = next(
        b
        for b in _mc01_editorial_blocks(db_session)
        if "mc01-ex9" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex9", "answer": [1, 3, 2, 0]},
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


# --- Correction sémantique IA : utilise le contrat existant (#23) ----------------------


def test_long_answer_correction_uses_fake_provider_via_existing_contract(
    authenticated_client, db_session, monkeypatch
):
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex3" in b.content
    )
    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex3", "answer": "Une réponse de test suffisamment longue."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "points_awarded" in data and "points_max" in data
    assert data["points_max"] == 1.0
    # Un seul appel au fournisseur, pour cette seule question (pas de second moteur IA).
    assert fake.semantic_calls == [(("mc01-ex3",), "standard")]


def test_diagnostic_correction_uses_fake_provider(authenticated_client, db_session, monkeypatch):
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex4" in b.content
    )
    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex4", "answer": "La carte graphique et l'écran."},
    )
    assert response.status_code == 200
    assert fake.semantic_calls == [(("mc01-ex4",), "standard")]


def test_vocabulary_correction_uses_fake_provider(authenticated_client, db_session, monkeypatch):
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex12" in b.content
    )
    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex12", "answer": "RAM, HDD, motherboard, PSU."},
    )
    assert response.status_code == 200
    assert fake.semantic_calls == [(("mc01-ex12",), "standard")]


def test_ai_correction_without_key_returns_clean_503_answer_not_lost(authenticated_client, db_session):
    """Sans clé configurée (comportement par défaut de l'environnement de test) : 503
    propre, jamais un 500, jamais la solution."""
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex3" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex3", "answer": "Une réponse de test."},
    )
    assert response.status_code == 503
    assert "configurée" in response.json()["detail"].lower()
    body_text = response.text
    assert "Le processeur doit être compatible avec le socket" not in body_text


def test_ai_provider_error_returns_clean_502(authenticated_client, db_session, monkeypatch):
    class _FailingProvider(FakeAIProvider):
        def correct_semantic_batch(self, questions, answers, severity, contexts):
            raise AIProviderError("panne simulée du fournisseur")

    monkeypatch.setattr("app.practice.get_ai_provider", lambda: _FailingProvider())
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex3" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex3", "answer": "Une réponse de test."},
    )
    assert response.status_code == 502


def test_non_string_answer_rejected_for_semantic_types(authenticated_client, db_session, monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex3" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex3", "answer": [1, 2, 3]},
    )
    assert response.status_code == 422
    assert fake.semantic_calls == []  # jamais appelé avec une réponse mal formée


# --- Points bornés, jamais confiance aveugle dans l'IA ----------------------------------


def test_semantic_correction_points_are_bounded_server_side(authenticated_client, db_session, monkeypatch):
    class _OverclaimingProvider(FakeAIProvider):
        def correct_semantic_batch(self, questions, answers, severity, contexts):
            from app.ai.schemas import QuestionCorrection

            return {
                q.question_id: QuestionCorrection(
                    question_id=q.question_id, points_awarded=999, points_max=999,
                    correct=True,
                )
                for q in questions
            }

    monkeypatch.setattr("app.practice.get_ai_provider", lambda: _OverclaimingProvider())
    seed()
    block = next(
        b for b in _mc01_editorial_blocks(db_session) if "mc01-ex3" in b.content
    )
    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "mc01-ex3", "answer": "x"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["points_max"] == 1.0
    assert data["points_awarded"] == 1.0


# --- Migration d'un staging déjà seedé avant #29 (forme post-#22) ----------------------


def test_staging_seeded_before_ticket_29_is_migrated_without_reset(authenticated_client, db_session):
    """Reproduit un staging seedé après #21/#22 mais AVANT #29 : Ex1/Ex2/Ex9/Ex11 déjà
    structurés, Ex3/4/5/6/7/8/10/12 encore répartis dans 3 blocs Markdown sous leurs
    anciens titres (aujourd'hui dans MC01_OBSOLETE_TITLES). Un seul seed() doit retirer
    ces 3 blocs Markdown et ajouter les 8 nouveaux blocs structurés, sans reset-db."""
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

    # Les 4 blocs déjà structurés (#21), état post-#22 (space=PRACTICE).
    for block_data in MC01_BLOCKS:
        if block_data["title"] in (
            "Exercice 1 — Matériel ou logiciel (classification)",
            "Exercice 2 — Unité centrale ou périphérique (classification)",
            "Exercice 9 — Lancement d'un programme (ordering)",
            "Exercice 11 — Entrée, sortie ou mixte (classification)",
        ):
            db_session.add(LessonBlock(
                uaa=uaa, title=block_data["title"], type=block_data["type"],
                content=block_data["content"], position=block_data["position"],
                is_published=True, space=BlockSpace.PRACTICE,
            ))

    # Les 3 blocs Markdown pré-#29, sous leurs anciens titres (contenu factice mais
    # identifiable), en PRACTICE (état post-#22).
    old_markdown_titles = [
        "Architecture d'un PC — Exercices (composants et rôles : suite)",
        "Architecture d'un PC — Exercices (2/3 : RAM, stockage, GPU, PSU)",
        "Architecture d'un PC — Exercices (diagnostic et vocabulaire : suite)",
    ]
    assert set(old_markdown_titles).issubset(MC01_OBSOLETE_TITLES)
    for position, title in enumerate(old_markdown_titles, start=15):
        db_session.add(LessonBlock(
            uaa=uaa, title=title, type=BlockType.MARKDOWN,
            content="## Exercice X — ancien contenu pré-#29.",
            position=position, is_published=True, space=BlockSpace.PRACTICE,
        ))
    db_session.commit()

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)

    remaining_titles = {block.title for block in uaa.lesson_blocks}
    for old_title in old_markdown_titles:
        assert old_title not in remaining_titles

    editorial_blocks = [
        block for block in uaa.lesson_blocks if block.type == BlockType.EDITORIAL_EXERCISE
    ]
    assert len(editorial_blocks) == 12

    # Ticket #55 : /uaa/ampcr-mc01/practice affiche désormais le nouveau parcours de
    # session V1 — la migration des 12 exercices elle-même reste vérifiée ci-dessus au
    # niveau des données (aucun ancien titre Markdown, 12 blocs editorial_exercise).
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    assert "ancien contenu pré-#29" not in response.text


def test_seed_is_idempotent_after_ticket_29_migration(client, db_session):
    seed()
    uaa = _mc01_uaa(db_session)
    block_count_after_first = len(uaa.lesson_blocks)

    seed()
    db_session.expire_all()
    uaa = _mc01_uaa(db_session)
    assert len(uaa.lesson_blocks) == block_count_after_first


# --- Non-régression MC02/MC03/Mathématiques ---------------------------------------------


def test_mc02_and_mc03_unaffected_by_ticket_29(authenticated_client, db_session):
    seed()
    mc02 = db_session.query(UAA).filter_by(code="MC02").first()
    mc03 = db_session.query(UAA).filter_by(code="MC03").first()
    assert len(mc02.lesson_blocks) == len(MC02_BLOCKS)
    assert len(mc03.lesson_blocks) == len(MC03_BLOCKS)
    assert authenticated_client.get("/uaa/ampcr-mc02/practice").status_code == 200
    assert authenticated_client.get("/uaa/ampcr-mc03/practice").status_code == 200


def test_mathematiques_unaffected_by_ticket_29(client, db_session):
    seed()
    response = client.get("/uaa/mb32-uaa1")
    assert response.status_code == 200
    assert "Fonction constante" in response.text

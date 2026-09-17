"""Tests d'intégration des routes de génération/correction IA (complément IA du ticket
#10). Le fournisseur réel n'est jamais appelé : soit non configuré (comportement par
défaut de cet environnement de test, sans OPENAI_API_KEY), soit remplacé par
FakeAIProvider via monkeypatch — jamais de consommation d'API réelle."""

from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import DIFFICULTIES
from app.models import UAA, BlockType, LessonBlock
from app.seed import seed


def _get_ai_block_id(db_session) -> int:
    uaa = db_session.query(UAA).filter_by(code="MC01").first()
    block = (
        db_session.query(LessonBlock)
        .filter_by(uaa_id=uaa.id, type=BlockType.AI_EXERCISE)
        .first()
    )
    assert block is not None
    return block.id


def test_generate_without_configuration_returns_clear_503(authenticated_client, db_session):
    seed()
    block_id = _get_ai_block_id(db_session)

    response = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "facile"}
    )

    assert response.status_code == 503
    assert "configurée" in response.json()["detail"].lower()


def test_generate_unknown_block_returns_404(authenticated_client, db_session):
    seed()
    response = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": 999999, "difficulty": "facile"}
    )
    assert response.status_code == 404


def test_generate_rejects_invalid_difficulty(authenticated_client, db_session):
    seed()
    block_id = _get_ai_block_id(db_session)

    response = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "impossible"}
    )
    assert response.status_code == 422


def test_generate_with_fake_provider_returns_signed_exercise(authenticated_client, db_session, monkeypatch):
    seed()
    block_id = _get_ai_block_id(db_session)

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    response = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "moyen"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["difficulty"] == "moyen"
    assert data["difficulty"] in DIFFICULTIES
    assert data["statement"]
    assert data["statement_html"]
    assert data["statement_token"]
    # Aucune clé/secret ne doit apparaître dans la réponse envoyée au navigateur.
    assert "secret" not in str(data).lower()
    assert "api_key" not in str(data).lower()


def test_correct_with_fake_provider_returns_structured_result(authenticated_client, db_session, monkeypatch):
    seed()
    block_id = _get_ai_block_id(db_session)

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    generate_response = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "difficile"}
    )
    generated = generate_response.json()

    correct_response = authenticated_client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": block_id,
            "exercise_statement": generated["statement"],
            "exercise_type": generated["exercise_type"],
            "difficulty": generated["difficulty"],
            "statement_token": generated["statement_token"],
            "answer": "Le CPU exécute les instructions du programme.",
        },
    )

    assert correct_response.status_code == 200
    result = correct_response.json()
    for key in [
        "appreciation",
        "appreciation_html",
        "correct_points",
        "errors",
        "expected_answer_explained",
        "expected_answer_explained_html",
        "score",
        "max_score",
    ]:
        assert key in result

    # La réponse du candidat a bien été transmise au fournisseur comme donnée à évaluer.
    assert fake.correct_calls[0][4] == "Le CPU exécute les instructions du programme."


def test_correct_rejects_tampered_statement(authenticated_client, db_session, monkeypatch):
    seed()
    block_id = _get_ai_block_id(db_session)

    fake = FakeAIProvider()
    monkeypatch.setattr("app.practice.get_ai_provider", lambda: fake)

    generated = authenticated_client.post(
        "/practice/api/ai/generate", json={"block_id": block_id, "difficulty": "facile"}
    ).json()

    tampered_response = authenticated_client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": block_id,
            "exercise_statement": "Un énoncé totalement différent, jamais généré par le serveur.",
            "exercise_type": generated["exercise_type"],
            "difficulty": generated["difficulty"],
            "statement_token": generated["statement_token"],
            "answer": "Peu importe.",
        },
    )

    assert tampered_response.status_code == 400
    assert len(fake.correct_calls) == 0  # le fournisseur n'est jamais appelé


def test_correct_unknown_block_returns_404(authenticated_client, db_session):
    seed()
    response = authenticated_client.post(
        "/practice/api/ai/correct",
        json={
            "block_id": 999999,
            "exercise_statement": "x",
            "exercise_type": "calcul",
            "difficulty": "facile",
            "statement_token": "invalid",
            "answer": "x",
        },
    )
    assert response.status_code == 404

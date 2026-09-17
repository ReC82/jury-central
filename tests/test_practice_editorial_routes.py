"""Tests d'intégration de la route générique `/practice/api/editorial/{block_id}/verify`
(ticket #17), et de la route de démonstration admin associée."""

from app.editorial_exercise import EditorialExerciseBlockConfig, EditorialExerciseItem
from app.models import UAA, BlockType, LessonBlock, Module, Subject


def _create_editorial_block(db_session, *, is_published: bool = True) -> LessonBlock:
    subject = Subject(name="Matière test", slug="matiere-test")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MOD", slug="mod", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="U1", title="UAA test", slug="uaa-test", is_published=True, module=module)
    db_session.add(uaa)
    db_session.flush()

    config = EditorialExerciseBlockConfig(
        mode="practice",
        items=[
            EditorialExerciseItem(
                exercise_id="q1",
                type="single_choice",
                prompt="La RAM est-elle volatile ?",
                choices=["Oui", "Non"],
                correct_index=0,
                explanation="La RAM perd son contenu à l'extinction du PC.",
            ),
            EditorialExerciseItem(
                exercise_id="q2",
                type="short_answer",
                prompt="Sigle anglais de la mémoire vive ?",
                accepted_answers=["RAM"],
                explanation="RAM = Random Access Memory.",
            ),
            EditorialExerciseItem(
                exercise_id="q3",
                type="classification",
                prompt="Classe chaque composant.",
                categories=["Matériel", "Logiciel"],
                elements=["Carte graphique", "Navigateur"],
                correct_categories=[0, 1],
                explanation="Le matériel est physique, le logiciel est un programme.",
            ),
            EditorialExerciseItem(
                exercise_id="q4",
                type="ordering",
                prompt="Remets les étapes dans l'ordre.",
                order_items=["Lecture SSD", "Exécution CPU"],
                correct_order=[0, 1],
                explanation="On lit avant d'exécuter.",
            ),
        ],
    )
    block = LessonBlock(
        uaa=uaa,
        title="Exercices — Test",
        type=BlockType.EDITORIAL_EXERCISE,
        content=config.to_json(),
        position=1,
        is_published=is_published,
    )
    db_session.add(block)
    db_session.commit()
    return block


def test_verify_correct_single_choice_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q1", "answer": "0"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["correct_answer"] == "Oui"
    assert data["explanation"]


def test_verify_incorrect_single_choice_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q1", "answer": "1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["correct_answer"] == "Oui"


def test_verify_short_answer_correct_and_normalized(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q2", "answer": "  ram  "},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_verify_correct_classification_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q3", "answer": [0, 1]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert "Carte graphique" in data["correct_answer"]


def test_verify_incorrect_classification_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q3", "answer": [1, 1]},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is False


def test_verify_correct_ordering_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q4", "answer": [0, 1]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert "Lecture SSD" in data["correct_answer"]


def test_verify_incorrect_ordering_answer(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q4", "answer": [1, 0]},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is False


def test_verify_unknown_exercise_id_returns_404(authenticated_client, db_session):
    block = _create_editorial_block(db_session)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "does-not-exist", "answer": "0"},
    )

    assert response.status_code == 404


def test_verify_unknown_block_id_returns_404(authenticated_client, db_session):
    _create_editorial_block(db_session)

    response = authenticated_client.post(
        "/practice/api/editorial/999999/verify",
        json={"exercise_id": "q1", "answer": "0"},
    )

    assert response.status_code == 404


def test_verify_unpublished_block_returns_404(authenticated_client, db_session):
    block = _create_editorial_block(db_session, is_published=False)

    response = authenticated_client.post(
        f"/practice/api/editorial/{block.id}/verify",
        json={"exercise_id": "q1", "answer": "0"},
    )

    assert response.status_code == 404


def test_verify_wrong_block_type_returns_404(authenticated_client, db_session):
    subject = Subject(name="Matière test 2", slug="matiere-test-2")
    db_session.add(subject)
    db_session.flush()
    module = Module(code="MOD2", slug="mod2", subject=subject)
    db_session.add(module)
    db_session.flush()
    uaa = UAA(code="U2", title="UAA", slug="uaa-test-2", is_published=True, module=module)
    db_session.add(uaa)
    db_session.flush()
    markdown_block = LessonBlock(
        uaa=uaa, title="Cours", type=BlockType.MARKDOWN, content="x", position=1, is_published=True
    )
    db_session.add(markdown_block)
    db_session.commit()

    response = authenticated_client.post(
        f"/practice/api/editorial/{markdown_block.id}/verify",
        json={"exercise_id": "q1", "answer": "0"},
    )

    assert response.status_code == 404


def test_public_uaa_page_never_leaks_solution_before_correction(client, db_session):
    _create_editorial_block(db_session)

    response = client.get("/uaa/uaa-test")

    assert response.status_code == 200
    text = response.text
    assert "editorial-exercise-block" in text
    assert "RAM = Random Access Memory" not in text  # explanation
    assert '"correct_index"' not in text
    assert '"accepted_answers"' not in text
    assert '"correct_categories"' not in text
    assert '"correct_order"' not in text


def test_admin_editorial_exercise_demo_page_renders(admin_client):
    response = admin_client.get("/admin/editorial-exercise-demo")
    assert response.status_code == 200
    assert "editorial-exercise-block" in response.text
    assert "demo-single-choice" in response.text
    # Jamais la solution avant correction, même sur la page de démo admin.
    assert "Random Access Memory" not in response.text


def test_admin_editorial_exercise_demo_verify_correct(admin_client):
    response = admin_client.post(
        "/admin/editorial-exercise-demo/verify",
        json={"exercise_id": "demo-true-false", "answer": "1"},
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_admin_editorial_exercise_demo_verify_requires_login(client):
    response = client.post(
        "/admin/editorial-exercise-demo/verify",
        json={"exercise_id": "demo-true-false", "answer": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"

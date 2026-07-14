"""Tests d'intégration bout en bout : générateur value_table -> page publique d'une UAA
-> vérification serveur, et non-régression du moteur "generated_exercise" existant
(équations) pour les deux mêmes points d'entrée.
"""

from app.seed import seed


def test_uaa1_public_page_renders_value_table_widget_for_constant_function(client):
    seed()

    response = client.get("/uaa/mb32-uaa1")
    assert response.status_code == 200

    html = response.text
    assert 'class="border rounded p-3 value-table-exercise"' in html
    assert 'data-generator="maths.functions.constant_function"' in html
    assert 'data-verify-url="/practice/api/value-table/verify"' in html
    # Aucune trace de la réponse dans le HTML envoyé au navigateur.
    assert "&#34;answer&#34;" not in html
    assert '"answer"' not in html


def test_uaa1_public_page_no_longer_uses_old_exercise_widget_for_constant_function(client):
    """L'ancien rendu texte (exercise-widget) ne doit plus apparaître pour la fonction
    constante : le bloc ne produit plus que des value_table."""
    seed()
    response = client.get("/uaa/mb32-uaa1")
    assert "exercise-widget" not in response.text


def test_legacy_generate_rejects_value_table_generator(client):
    """/api/generate est réservé à l'ancien moteur (GeneratedExercise) : un générateur
    value_table doit y être refusé proprement plutôt que de provoquer une erreur serveur."""
    response = client.get(
        "/practice/api/generate",
        params={"generator": "maths.functions.constant_function", "difficulty": 1},
    )
    assert response.status_code == 400


def test_value_table_verify_endpoint_end_to_end(client):
    from generators.maths.constant_function import generate

    exercise = generate(difficulty=1, seed=7)
    p = exercise.answer["cells"][0]

    response = client.post(
        "/practice/api/value-table/verify",
        json={
            "generator": "maths.functions.constant_function",
            "difficulty": 1,
            "seed": 7,
            "answers": [str(p), str(p), str(p)],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["all_correct"] is True
    assert len(body["cells"]) == 3
    assert body["explanation"]


def test_value_table_verify_endpoint_detects_wrong_answer(client):
    from generators.maths.constant_function import generate

    exercise = generate(difficulty=1, seed=7)
    p = exercise.answer["cells"][0]
    wrong = str(float(p) + 1)

    response = client.post(
        "/practice/api/value-table/verify",
        json={
            "generator": "maths.functions.constant_function",
            "difficulty": 1,
            "seed": 7,
            "answers": [wrong, str(p), str(p)],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["all_correct"] is False
    assert body["cells"][0]["correct"] is False


def test_value_table_verify_rejects_generated_exercise_generator(client):
    response = client.post(
        "/practice/api/value-table/verify",
        json={
            "generator": "maths.equations.linear_equation",
            "difficulty": 1,
            "seed": 1,
            "answers": ["1"],
        },
    )
    assert response.status_code == 400


def test_legacy_verify_rejects_value_table_generator(client):
    response = client.post(
        "/practice/api/verify",
        json={
            "generator": "maths.functions.constant_function",
            "difficulty": 1,
            "seed": 1,
            "answer": "1",
        },
    )
    assert response.status_code == 400


def test_legacy_reveal_rejects_value_table_generator(client):
    response = client.post(
        "/practice/api/reveal",
        json={"generator": "maths.functions.constant_function", "difficulty": 1, "seed": 1},
    )
    assert response.status_code == 400


# --- Non-régression : l'ancien moteur (équations) reste inchangé --------------------------


def test_equations_generator_still_uses_legacy_pipeline(client):
    response = client.get(
        "/practice/api/generate",
        params={"generator": "maths.equations.linear_equation", "difficulty": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert "statement" in body
    assert "seed" in body


def test_equations_verify_still_works(client):
    generate_response = client.get(
        "/practice/api/generate",
        params={"generator": "maths.equations.linear_equation", "difficulty": 1, "seed": 5},
    )
    seed_used = generate_response.json()["seed"]

    from generators.maths.equations import generate as equations_generate

    exercise = equations_generate(difficulty=1, seed=seed_used)

    verify_response = client.post(
        "/practice/api/verify",
        json={
            "generator": "maths.equations.linear_equation",
            "difficulty": 1,
            "seed": seed_used,
            "answer": str(exercise.answer),
        },
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["correct"] is True


# --- Outil de debug /admin/generators : gère les deux types --------------------------------


def test_admin_generators_renders_value_table_widget_for_constant_function(admin_client):
    response = admin_client.get(
        "/admin/generators",
        params={"generator": "maths.functions.constant_function", "difficulty": 1, "seed": 1},
    )
    assert response.status_code == 200
    assert 'class="value-table-exercise"' in response.text
    assert 'data-generator="maths.functions.constant_function"' in response.text
    assert "&#34;answer&#34;" not in response.text


def test_admin_generators_still_renders_legacy_view_for_equations(admin_client):
    response = admin_client.get(
        "/admin/generators",
        params={"generator": "maths.equations.linear_equation", "difficulty": 1, "seed": 1},
    )
    assert response.status_code == 200
    assert "value-table-exercise" not in response.text
    assert "Étapes de correction" in response.text or "Résultat" in response.text


def test_admin_value_table_demo_still_works(admin_client):
    """Le démonstrateur fixe (non relié à un générateur) doit continuer de fonctionner."""
    response = admin_client.get("/admin/value-table-demo")
    assert response.status_code == 200
    assert 'class="value-table-exercise"' in response.text

    verify_response = admin_client.post(
        "/admin/value-table-demo/verify", json={"answers": ["-3", "1", "7"]}
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["all_correct"] is True

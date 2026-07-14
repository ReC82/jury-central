"""Tests du renderer de contenu riche unique (VS003.1) : cours, quiz, exercices générés et
value_table doivent tous produire du HTML rendu (tableaux, listes, MathJax) via
`app/content.py::render_markdown`, jamais du texte brut affiché tel quel.
"""

from app.exercise_blocks import exercise_to_dict, exercise_to_public_dict
from app.quiz import QuizConfig
from app.seed import seed
from app.value_table import CellResult, ValueTableCorrection, value_table_public_dict
from generators.exercise_types import InteractiveExercise
from generators.maths.constant_function import generate as generate_constant_function
from generators.maths.equations import generate as generate_equation


# --- Quiz -----------------------------------------------------------------------------


def test_quiz_question_html_renders_markdown_table():
    config = QuizConfig(
        question="| $x$ | -1 | 0 | 1 |\n|---|---|---|---|\n| $f(x)$ | 4 | 4 | 4 |",
        choices=["f(x) = x + 4", "f(x) = 4"],
        correct_index=1,
    )
    public = config.to_public_dict(block_id=1)
    assert "<table>" in public["question_html"]
    assert "<td>4</td>" in public["question_html"]


def test_quiz_question_html_renders_plain_text_as_paragraph():
    config = QuizConfig(question="Une simple phrase.", choices=["a", "b"], correct_index=0)
    public = config.to_public_dict(block_id=1)
    assert public["question_html"] == "<p>Une simple phrase.</p>"


def test_quiz_question_html_preserves_list():
    config = QuizConfig(
        question="Choisis :\n\n- un\n- deux",
        choices=["a", "b"],
        correct_index=0,
    )
    public = config.to_public_dict(block_id=1)
    assert "<ul>" in public["question_html"]
    assert "<li>un</li>" in public["question_html"]


# --- Exercices générés (ancien moteur) -------------------------------------------------


def test_exercise_public_dict_includes_rendered_statement_and_hint():
    exercise = generate_equation(difficulty=1, seed=1)
    public = exercise_to_public_dict(exercise)
    assert public["statement_html"] == f"<p>{exercise.statement}</p>"
    # équations n'a pas de hint dans ce générateur
    assert public["hint_html"] == ""


def test_exercise_public_dict_renders_hint_when_present():
    exercise = generate_equation(difficulty=1, seed=1)
    exercise.hint = "Isole x d'un côté."
    public = exercise_to_public_dict(exercise)
    assert public["hint_html"] == "<p>Isole x d'un côté.</p>"


def test_exercise_to_dict_includes_rendered_solution_steps():
    exercise = generate_equation(difficulty=1, seed=1)
    full = exercise_to_dict(exercise)
    assert len(full["solution_steps_html"]) == len(exercise.solution_steps)
    for rendered, raw in zip(full["solution_steps_html"], exercise.solution_steps, strict=True):
        assert rendered == f"<p>{raw}</p>"


# --- value_table -------------------------------------------------------------------


def test_value_table_public_dict_renders_question_and_hint():
    exercise = generate_constant_function(difficulty=1, seed=1)
    public = value_table_public_dict(exercise)
    assert "answer" not in public
    assert public["question_html"] == f"<p>{exercise.question}</p>"
    assert public["hint_html"] == f"<p>{exercise.hint}</p>"


def test_value_table_public_dict_handles_missing_hint():
    exercise = InteractiveExercise(
        type="value_table", question="Q", data={"columns": [], "rows": []}, answer={}, hint=""
    )
    public = value_table_public_dict(exercise)
    assert public["hint_html"] == ""


def test_value_table_correction_renders_explanation():
    correction = ValueTableCorrection(
        all_correct=True,
        cells=[CellResult(row=0, col=0, correct=True, correct_value="4")],
        explanation="Quel que soit x, f(x) = 4.",
        hint="Indice",
    )
    data = correction.to_dict()
    assert data["explanation_html"] == "<p>Quel que soit x, f(x) = 4.</p>"


def test_value_table_correction_handles_missing_explanation():
    correction = ValueTableCorrection(all_correct=True, cells=[], explanation="", hint="")
    data = correction.to_dict()
    assert data["explanation_html"] == ""


# --- /practice/api : les routes exposent aussi le HTML rendu, jamais du texte brut ------


def test_reveal_endpoint_returns_rendered_solution_steps(client):
    exercise = generate_equation(difficulty=1, seed=1)
    response = client.post(
        "/practice/api/reveal",
        json={"generator": "maths.equations.linear_equation", "difficulty": 1, "seed": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["solution_steps_html"]) == len(exercise.solution_steps)
    assert body["solution_steps_html"][0].startswith("<p>")


def test_quiz_verify_endpoint_returns_rendered_explanation(client, db_session):
    from app.models import UAA, BlockType, LessonBlock, Module, Subject

    subject = Subject(name="Test", slug="test")
    module = Module(code="M1", slug="m1", subject=subject)
    uaa = UAA(code="U1", title="U1", slug="u1", position=1, is_published=True, module=module)
    block = LessonBlock(
        uaa=uaa,
        title="Quiz",
        type=BlockType.QUIZ,
        content=QuizConfig(
            question="Q",
            choices=["a", "b"],
            correct_index=0,
            explanation="**Parce que.**",
        ).to_json(),
        position=1,
        is_published=True,
    )
    db_session.add_all([subject, module, uaa, block])
    db_session.commit()

    response = client.post(f"/practice/api/quiz/{block.id}/verify", json={"answer": "0"})
    assert response.status_code == 200
    body = response.json()
    assert body["explanation_html"] == "<p><strong>Parce que.</strong></p>"


# --- Page publique : la question "tableau en prose" devient un vrai tableau -------------


def test_uaa1_quiz_question_renders_as_real_table_not_a_sentence(client):
    """Cas concret demandé pour VS003.1 : "Le tableau x : -1,0,1 -> f(x): 4,4,4" doit
    s'afficher comme un <table>, pas comme une phrase brute.

    Cette question fait partie d'un parcours de quiz groupé : son contenu est transmis au
    navigateur comme JSON (`data-questions`, consommé par quiz.js) plutôt qu'en HTML brut
    sur la page — on vérifie donc le HTML rendu à l'intérieur de ce JSON.
    """
    import html as html_lib
    import json
    import re

    seed()
    response = client.get("/uaa/mb32-uaa1")
    assert response.status_code == 200
    page_html = response.text

    assert "Le tableau x : -1, 0, 1" not in page_html

    match = re.search(r'data-questions="([^"]*)"', page_html)
    assert match, "bloc quiz-run introuvable sur la page"
    questions = json.loads(html_lib.unescape(match.group(1)))

    target = next(
        (q for q in questions if "correspond à quelle fonction" in q["question_html"]), None
    )
    assert target is not None, "question introuvable dans le parcours de quiz"
    assert "<table>" in target["question_html"]
    assert "<td>4</td>" in target["question_html"]

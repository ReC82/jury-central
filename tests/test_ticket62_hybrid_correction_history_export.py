"""Ticket #62 — correction pédagogique hybride, sévérité 1-5, historique, impression et
export (URGENT avant Français).

Deux niveaux de test :
1. Unitaire, sans DB ni HTTP (`app.v1.hybrid_correction`) — rapide, couvre le
   verrouillage du score déterministe et le contenu exact du batch IA.
2. HTTP de bout en bout (`TestClient`) — couvre sévérité/historique/impression/export/
   isolation utilisateur/non-régression.

Aucun appel OpenAI réel : `FakeAIProvider` partout où une correction IA est exercée."""

import re

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import (
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireQuestion,
)
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.hybrid_correction import correct_session_hybrid
from app.v1.models import QuestionnaireSession

CONTEXT = PedagogicalContext(
    course_key="k", course_title="t", level="l", allowed_notions=[], competencies=[], vocabulary=[]
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _register(client, email: str):
    token = _csrf(client.get("/register").text)
    response = client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "Aa1!aaaaaaaa",
            "password_confirm": "Aa1!aaaaaaaa", "display_name": "t",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text


def _seed_mc01_bank(db_session):
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()


def _answer_payload_for(html: str) -> dict:
    if 'name="option_id"' in html:
        match = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', html)
        return {"option_id": match.group(1)}
    category_names = re.findall(r'name="(category__\d+)"', html)
    if category_names:
        data = {}
        for name in category_names:
            block = re.search(rf'name="{name}".*?</select>', html, re.DOTALL)
            values = re.findall(r'<option value="(\d+)"', block.group(0))
            data[name] = values[0]
        return data
    item_names = re.findall(r'name="(position__item\d+)"', html)
    if item_names:
        return {name: str(idx) for idx, name in enumerate(item_names, start=1)}
    return {"text": "Réponse de test couvrant plusieurs phrases pour valider la correction."}


def _start_session(client, uaa_slug: str, mode: str = "practice") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


def _answer_all(client, session_url: str, total: int) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303, response.text


def _submit(client, session_url: str, severity: int = 3) -> None:
    response = client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": str(severity)},
        follow_redirects=False,
    )
    assert response.status_code == 303


# =============================================================================================
# 1. Unitaire — verrouillage du score déterministe, batch unique, explications
# =============================================================================================


def _ordering_question() -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id="q1", type="ordering", prompt="Ordonne.", points_max=1.0,
        order_items=["SSD", "RAM", "CPU", "écran"], correct_order=[0, 1, 2, 3],
    )


def _classification_question() -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        question_id="q2", type="classification", prompt="Classe.", points_max=1.0,
        categories=["Matériel", "Logiciel"], elements=["RAM", "Navigateur"],
        correct_categories=[0, 1],
    )


def test_deterministic_score_identical_with_and_without_ai():
    """Le score déterministe local est identique, que le lot IA contienne cette question
    ou non — l'IA ne fait qu'expliquer, jamais recalculer."""
    from app.ai.local_correction import correct_locally

    question = _ordering_question()
    wrong_answer = [0, 1, 3, 2]
    local_only = correct_locally(question, wrong_answer)

    questionnaire = Questionnaire(mode="practice", questions=[question])
    hybrid = correct_session_hybrid(
        FakeAIProvider(), questionnaire, {"q1": wrong_answer}, {"q1": "SSD → RAM → écran → CPU"},
        "standard", (CONTEXT,),
    )
    assert hybrid.questions[0].points_awarded == local_only.points_awarded == 0.0
    assert hybrid.questions[0].correct == local_only.correct is False


def test_ai_cannot_modify_deterministic_score():
    """Même si le fournisseur IA renvoie un score falsifié, le serveur l'ignore
    intégralement pour une question déterministe (§ 3 du ticket : SERVER_SCORE_LOCKED)."""

    class MaliciousProvider:
        def correct_semantic_batch(self, questions, answers, severity, contexts):
            return {
                q.question_id: QuestionCorrection(
                    question_id=q.question_id, points_awarded=999.0, points_max=999.0,
                    correct=True, feedback="score falsifié",
                )
                for q in questions
            }

    question = _ordering_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    result = correct_session_hybrid(
        MaliciousProvider(), questionnaire, {"q1": [0, 1, 3, 2]}, {"q1": "SSD → RAM → écran → CPU"},
        "standard", (CONTEXT,),
    )
    correction = result.questions[0]
    assert correction.points_awarded == 0.0
    assert correction.points_max == 1.0
    assert correction.correct is False


def test_ordering_wrong_receives_pedagogical_ai_explanation():
    question = _ordering_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire, {"q1": [0, 1, 3, 2]}, {"q1": "SSD → RAM → écran → CPU"},
        "standard", (CONTEXT,),
    )
    assert "Correction automatique déterministe" not in result.questions[0].feedback
    assert fake.semantic_calls  # le lot IA a bien été appelé


def test_classification_wrong_receives_pedagogical_ai_explanation():
    question = _classification_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire, {"q2": [1, 0]}, {"q2": "RAM → Logiciel ; Navigateur → Matériel"},
        "standard", (CONTEXT,),
    )
    assert result.questions[0].correct is False
    assert "Correction automatique déterministe" not in result.questions[0].feedback


def test_correct_deterministic_answer_is_not_sent_to_ai():
    """§ 3 du ticket : pas besoin d'appel d'explication pour une réponse déterministe
    correcte."""
    question = _ordering_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    fake = FakeAIProvider()
    result = correct_session_hybrid(
        fake, questionnaire, {"q1": [0, 1, 2, 3]}, {"q1": "SSD → RAM → CPU → écran"},
        "standard", (CONTEXT,),
    )
    assert result.questions[0].correct is True
    assert not fake.semantic_calls  # aucun appel : la seule question était correcte


def test_single_batch_call_mixes_semantic_and_explain_only_questions():
    ordering = _ordering_question()
    long_answer = QuestionnaireQuestion(
        question_id="q3", type="long_answer", prompt="Explique.", points_max=2.0, rubric="grille",
    )
    questionnaire = Questionnaire(mode="practice", questions=[ordering, long_answer])
    fake = FakeAIProvider()
    correct_session_hybrid(
        fake, questionnaire,
        {"q1": [0, 1, 3, 2], "q3": "une réponse"},
        {"q1": "SSD → RAM → écran → CPU"},
        "standard", (CONTEXT,),
    )
    assert len(fake.semantic_calls) == 1
    question_ids_sent = fake.semantic_calls[0][0]
    assert set(question_ids_sent) == {"q1", "q3"}


@pytest.mark.parametrize("severity", ["very_lenient", "lenient", "standard", "strict", "very_strict"])
def test_all_five_internal_severity_levels_accepted(severity):
    question = QuestionnaireQuestion(
        question_id="q3", type="long_answer", prompt="Explique.", points_max=2.0, rubric="grille",
    )
    questionnaire = Questionnaire(mode="practice", questions=[question])
    result = correct_session_hybrid(
        FakeAIProvider(), questionnaire, {"q3": "réponse"}, {}, severity, (CONTEXT,)
    )
    assert result.questions[0].points_max == 2.0


def test_severity_does_not_change_deterministic_outcome():
    question = _ordering_question()
    questionnaire = Questionnaire(mode="practice", questions=[question])
    wrong_answer = [0, 1, 3, 2]
    for severity in ("very_lenient", "very_strict"):
        result = correct_session_hybrid(
            FakeAIProvider(), questionnaire, {"q1": wrong_answer},
            {"q1": "SSD → RAM → écran → CPU"}, severity, (CONTEXT,),
        )
        assert result.questions[0].points_awarded == 0.0
        assert result.questions[0].correct is False


def test_severity_changes_semantic_points_awarded():
    question = QuestionnaireQuestion(
        question_id="q3", type="long_answer", prompt="Explique.", points_max=4.0, rubric="grille",
    )
    questionnaire = Questionnaire(mode="practice", questions=[question])
    lenient = correct_session_hybrid(
        FakeAIProvider(), questionnaire, {"q3": "réponse"}, {}, "lenient", (CONTEXT,)
    )
    strict = correct_session_hybrid(
        FakeAIProvider(), questionnaire, {"q3": "réponse"}, {}, "very_strict", (CONTEXT,)
    )
    assert lenient.questions[0].points_awarded > strict.questions[0].points_awarded


# =============================================================================================
# 2. HTTP de bout en bout — sévérité, historique, impression, export, isolation
# =============================================================================================


def test_severity_selector_default_is_three(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    assert 'id="severity-3"' in response.text
    checked_block = re.search(r'id="severity-3"[^>]*', response.text).group(0)
    assert "checked" in checked_block


def test_severity_persisted_on_completed_session(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    session_id = int(session_url.rsplit("/", 1)[-1])
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url, severity=5)

    session = db_session.get(QuestionnaireSession, session_id)
    assert session.parameters_json["severity"] == 5
    assert session.status.value == "completed"


def test_no_solution_leak_before_submission(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        for field in ("correct_option_ids", "correct_categories", "correct_order", "rubric", "expected_points"):
            assert field not in response.text


def test_history_shows_completed_and_in_progress_sessions(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)

    completed_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, completed_url, 10)
    _submit(authenticated_client, completed_url, severity=2)

    _start_session(authenticated_client, "ampcr-mc01")

    response = authenticated_client.get("/mes-sessions")
    assert response.status_code == 200
    assert "Terminé" in response.text
    assert "En cours" in response.text
    assert "Voir les résultats" in response.text
    assert "Reprendre" in response.text
    assert "Bienveillante" in response.text  # libellé sévérité 2


def test_reconnection_completed_session_reachable_from_history(client, db_session, monkeypatch):
    """§ 9 du ticket : terminer un entraînement, logout, login, retrouver exactement la
    session terminée dans l'historique, ouvrir ses résultats."""
    seed()
    _seed_mc01_bank(db_session)
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)

    _register(client, "reco@example.invalid")
    session_url = _start_session(client, "ampcr-mc01")
    session_id = session_url.rsplit("/", 1)[-1]
    _answer_all(client, session_url, 10)
    _submit(client, session_url, severity=3)

    token = _csrf(client.get("/account").text)
    response = client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303

    token = _csrf(client.get("/login").text)
    response = client.post(
        "/login", data={"csrf_token": token, "email": "reco@example.invalid", "password": "Aa1!aaaaaaaa"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    history = client.get("/mes-sessions")
    assert session_id in history.text

    results = client.get(session_url)
    assert results.status_code == 200
    assert "Score" in results.text


def test_reconnection_in_progress_session_resumable(client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)

    _register(client, "reco2@example.invalid")
    session_url = _start_session(client, "ampcr-mc01")
    token = _csrf(client.get(f"{session_url}?q=1").text)
    client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "next", "text": "réponse partielle"},
        follow_redirects=False,
    )

    token = _csrf(client.get("/account").text)
    client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    token = _csrf(client.get("/login").text)
    client.post(
        "/login", data={"csrf_token": token, "email": "reco2@example.invalid", "password": "Aa1!aaaaaaaa"},
        follow_redirects=False,
    )

    landing = client.get("/uaa/ampcr-mc01/practice")
    assert "Reprendre" in landing.text
    resumed = client.get(session_url)
    assert resumed.status_code == 200


def test_multiple_result_panels_can_be_expanded_simultaneously(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url)

    response = authenticated_client.get(session_url)
    assert 'data-bs-parent="#results-accordion"' not in response.text
    assert response.text.count('class="accordion-collapse collapse') >= 10


def test_expand_all_and_collapse_all_buttons_present(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url)

    response = authenticated_client.get(session_url)
    assert 'id="expand-all"' in response.text
    assert 'id="collapse-all"' in response.text
    assert "setAll(true)" in response.text
    assert "setAll(false)" in response.text


def test_print_button_and_css_force_all_panels_visible(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url)

    response = authenticated_client.get(session_url)
    assert "window.print()" in response.text
    assert "@media print" in response.text
    assert "display: block !important" in response.text
    # Toutes les questions (et leurs corrections) doivent être présentes dans le HTML,
    # y compris celles repliées par défaut — jamais générées dynamiquement côté client.
    for position in range(1, 11):
        assert f"Question {position} —" in response.text


def test_export_contains_all_questions_answers_and_feedback(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url)

    response = authenticated_client.get(f"{session_url}/export.md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "attachment" in response.headers["content-disposition"]
    assert "# Métadonnées" in response.text
    for position in range(1, 11):
        assert f"## Question {position}" in response.text
    assert "### Ma réponse" in response.text
    assert "### Attendu / critères" in response.text
    assert "### Points" in response.text
    assert "### Explication" in response.text


def test_export_forbidden_for_other_user(client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)

    _register(client, "owner@example.invalid")
    session_url = _start_session(client, "ampcr-mc01")
    _answer_all(client, session_url, 10)
    _submit(client, session_url)

    token = _csrf(client.get("/account").text)
    client.post("/logout", data={"csrf_token": token}, follow_redirects=False)

    _register(client, "intruder@example.invalid")
    response = client.get(f"{session_url}/export.md")
    assert response.status_code == 404


def test_export_forbidden_before_completion(authenticated_client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    response = authenticated_client.get(f"{session_url}/export.md")
    assert response.status_code == 409


def test_history_strictly_isolated_between_users(client, db_session, monkeypatch):
    seed()
    _seed_mc01_bank(db_session)
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)

    _register(client, "userA@example.invalid")
    session_a_url = _start_session(client, "ampcr-mc01")

    token = _csrf(client.get("/account").text)
    client.post("/logout", data={"csrf_token": token}, follow_redirects=False)

    _register(client, "userB@example.invalid")
    history_b = client.get("/mes-sessions")
    # userB n'a créé aucune session : son historique doit être explicitement vide, et ne
    # jamais contenir de lien vers la session de userA (vérifié par l'URL complète, pas
    # par un simple identifiant numérique qui apparaît trivialement ailleurs dans la page).
    assert "Aucune session pour l'instant" in history_b.text
    assert f'href="{session_a_url}"' not in history_b.text


def test_no_openai_key_configured_never_crashes_submission(authenticated_client, db_session):
    """Aucun monkeypatch de provider ici : `OPENAI_API_KEY=""` (garanti par
    tests/conftest.py) déclenche le chemin `_UnconfiguredProvider`/repli local — la
    soumission ne doit jamais échouer (§ 16 du ticket)."""
    seed()
    _seed_mc01_bank(db_session)
    session_url = _start_session(authenticated_client, "ampcr-mc01")
    _answer_all(authenticated_client, session_url, 10)
    _submit(authenticated_client, session_url)
    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "Score" in response.text


# =============================================================================================
# 3. Non-régression MC01 / MC17 / MC31 / MC38 (practice + résultats)
# =============================================================================================


@pytest.mark.parametrize("uaa_slug", ["ampcr-mc01", "ampcr-mc17", "ampcr-mc31", "ampcr-mc38"])
def test_practice_and_results_still_work_for_key_mc(authenticated_client, db_session, monkeypatch, uaa_slug):
    seed()
    _seed_mc01_bank(db_session)
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get(f"/uaa/{uaa_slug}/practice")
    assert response.status_code == 200

    session_url = _start_session(authenticated_client, uaa_slug)
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all(authenticated_client, session_url, session.question_count)
    _submit(authenticated_client, session_url)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "Score" in response.text

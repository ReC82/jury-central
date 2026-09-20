"""Ticket #74 — lien vers le cours à relire.

Après correction, pour chaque question incorrecte ou partielle : « Cours concerné : MCxx
— <titre> » + bouton « Relire le cours » (`/uaa/{slug}`, la page Cours déjà publique).
Synthèse globale « Cours à relire en priorité », limitée à 5, triée par nombre d'erreurs
décroissant. Inclus dans les résultats, l'export Markdown et l'impression (référence
textuelle visible à l'impression, boutons interactifs masqués — même principe que #77).

Architecture générique (§ ticket) : `_build_results_rows`/`_courses_to_review`
(`app/v1/routes_sessions.py`) ne dépendent d'aucune notion spécifique à l'Informatique —
réutilisable tel quel pour le Français dès qu'une session mélange plusieurs UAA.

Limite assumée, documentée (pas de nouvelle architecture/contenu inventé) : le ticket
mentionne aussi « À revoir : <micro-notion> », plus granulaire que le cours entier — aucune
donnée structurée de ce niveau n'existe dans le modèle actuel (une Question n'est
rattachée qu'à une UAA, jamais à une micro-notion distincte) ; l'implémenter demanderait un
nouveau champ/contenu édité par ChatGPT, hors du périmètre de cette passe. Seul le
rattachement au COURS (déjà existant, #79 § 13) est utilisé.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import QuestionnaireSession
from app.v1.routes_sessions import _courses_to_review, _is_incorrect_or_partial

# =============================================================================================
# Helpers
# =============================================================================================


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _seed_mc01(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    return ampcr, mc01


def _answer_payload_for(html: str, *, force_wrong: bool = False) -> dict:
    if 'name="option_id"' in html:
        # Choisit délibérément une option DIFFÉRENTE de la première pour maximiser les
        # chances de tomber sur une réponse fausse (utile pour peupler "à revoir").
        matches = re.findall(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', html)
        if force_wrong and len(matches) > 1:
            return {"option_id": matches[-1]}
        return {"option_id": matches[0]}
    category_names = re.findall(r'name="(category__\d+)"', html)
    if category_names:
        data = {}
        for name in category_names:
            block = re.search(rf'name="{name}".*?</select>', html, re.DOTALL)
            values = re.findall(r'<option value="(\d+)"', block.group(0))
            # Choisit systématiquement une mauvaise catégorie si possible.
            data[name] = values[-1] if force_wrong and len(values) > 1 else values[0]
        return data
    return {"text": "azerty"}  # réponse rédigée clairement hors sujet -> incorrecte


def _answer_all_wrong_and_submit(client, session_url: str, total: int, db_session, provider) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == total else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text, force_wrong=True))
        client.post(f"{session_url}/answer", data=data, follow_redirects=False)
    response = client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)
    # Ticket #88 : le POST ne corrige plus de façon synchrone — fait tourner le worker
    # explicitement (appel direct, pas de processus séparé) avant que l'appelant ne lise
    # un résultat.
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=provider)


# =============================================================================================
# 1. _is_incorrect_or_partial / _courses_to_review — unité
# =============================================================================================


def test_is_incorrect_or_partial_true_when_not_correct():
    assert _is_incorrect_or_partial({"feedback": {"correct": False}}) is True
    assert _is_incorrect_or_partial({"feedback": {}}) is True  # jamais corrigée -> à revoir
    assert _is_incorrect_or_partial({"feedback": {"correct": True}}) is False


def test_courses_to_review_ranks_by_error_count_and_limits_to_five():
    results = []
    for i in range(3):
        results.append({"feedback": {"correct": False}, "course_slug": "ampcr-mc17", "course_title": "Subnetting", "course_code": "MC17"})
    for i in range(1):
        results.append({"feedback": {"correct": False}, "course_slug": "ampcr-mc15", "course_title": "RJ45", "course_code": "MC15"})
    for i in range(2):
        results.append({"feedback": {"correct": True}, "course_slug": "ampcr-mc17", "course_title": "Subnetting", "course_code": "MC17"})

    ranked = _courses_to_review(results)
    assert ranked[0]["course_slug"] == "ampcr-mc17"
    assert ranked[0]["error_count"] == 3
    assert ranked[1]["course_slug"] == "ampcr-mc15"
    assert ranked[1]["error_count"] == 1


def test_courses_to_review_limited_to_five_courses():
    results = [
        {"feedback": {"correct": False}, "course_slug": f"ampcr-mc{i:02d}", "course_title": f"Cours {i}", "course_code": f"MC{i:02d}"}
        for i in range(1, 9)
    ]
    ranked = _courses_to_review(results)
    assert len(ranked) == 5


def test_courses_to_review_ignores_rows_without_a_known_course():
    results = [{"feedback": {"correct": False}, "course_slug": None, "course_title": None, "course_code": None}]
    assert _courses_to_review(results) == []


def test_courses_to_review_ignores_correct_answers():
    results = [{"feedback": {"correct": True}, "course_slug": "ampcr-mc17", "course_title": "Subnetting", "course_code": "MC17"}]
    assert _courses_to_review(results) == []


# =============================================================================================
# 2. Résultats HTML — lien par question + synthèse globale
# =============================================================================================


def test_results_page_shows_course_link_for_incorrect_questions(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
    )
    session_url = f"/sessions/{int(response.headers['location'].rsplit('/', 1)[-1])}"
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    _answer_all_wrong_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    # Au moins une question s'est révélée fausse (réponses délibérément erronées) —
    # doit afficher le lien vers son cours.
    assert "Cours concerné" in response.text
    assert "Relire le cours" in response.text
    assert 'href="/uaa/ampcr-mc01"' in response.text


def test_results_page_shows_courses_to_review_summary(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
    )
    session_url = f"/sessions/{int(response.headers['location'].rsplit('/', 1)[-1])}"
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    _answer_all_wrong_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    assert "Cours à relire en priorité" in response.text
    assert "MC01" in response.text
    assert re.search(r"\d+ erreurs?", response.text)


def test_no_course_review_data_when_everything_is_correct(db_session):
    """Non-régression, au niveau service (pas besoin d'un aller-retour HTTP complet ici,
    déjà couvert par les tests ci-dessus pour le cas « incorrect ») : si toutes les
    réponses d'une session sont correctes, ni `_build_results_rows` ni
    `_courses_to_review` ne doivent produire le moindre « à revoir » (jamais un faux
    positif)."""
    from app.v1.models import (
        SessionAnswer,
        SessionDifficultyRequest,
        SessionMode,
        SessionQuestion,
        SessionStatus,
        User,
        create_question,
    )
    from app.v1.routes_sessions import _build_results_rows
    from app.v1.session_service import submit_session

    ampcr, mc01 = _seed_mc01(db_session)
    fake = FakeAIProvider()
    user = User(email="ticket74@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="multiple_choice",
        content_json={
            "prompt": "Q ?", "options": [{"option_id": "0", "label": "A"}, {"option_id": "1", "label": "B"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source="manual",
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=ampcr.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    sq = SessionQuestion(session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0)
    db_session.add(sq)
    db_session.flush()
    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"selected_option_ids": ["0"]}))
    db_session.commit()

    submit_session(db_session, session=session, provider=fake, severity_ui=3)
    db_session.refresh(session)

    results = _build_results_rows(db_session, sorted(session.session_questions, key=lambda sq: sq.position))
    assert all(row["feedback"].get("correct") for row in results)
    assert _courses_to_review(results) == []


# =============================================================================================
# 3. Export Markdown
# =============================================================================================


def test_export_markdown_includes_courses_to_review_and_per_question_reference(
    authenticated_client, db_session, monkeypatch
):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
    )
    session_url = f"/sessions/{int(response.headers['location'].rsplit('/', 1)[-1])}"
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    _answer_all_wrong_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(f"{session_url}/export.md")
    assert response.status_code == 200
    assert "# Cours à relire en priorité" in response.text
    assert "*Cours concerné :" in response.text


# =============================================================================================
# 4. Impression : référence texte visible, bouton interactif masqué (même principe que #77)
# =============================================================================================


def test_print_shows_course_reference_text_but_hides_interactive_button(
    authenticated_client, db_session, monkeypatch
):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
    )
    session_url = f"/sessions/{int(response.headers['location'].rsplit('/', 1)[-1])}"
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_wrong_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    # "Cours concerné" (référence textuelle) reste visible à l'impression ; seul le
    # bouton "Relire le cours" (interactif) est masqué (`d-print-none`).
    assert "Cours concerné" in response.text
    match = re.search(r'<a href="/uaa/[^"]+" class="([^"]*)">\s*Relire le cours', response.text)
    assert match, "lien « Relire le cours » introuvable"
    assert "d-print-none" in match.group(1)
    assert "window.print()" in response.text
    assert "@media print" in response.text

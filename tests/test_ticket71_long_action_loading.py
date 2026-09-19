"""Ticket #71 — UX actions longues / double-clic.

PROBLÈMES RÉELS : création practice/exam et correction IA peuvent prendre plusieurs
secondes ; l'utilisateur peut recliquer pendant l'attente ; un 504 Gateway Timeout a déjà
été observé sur création exam.

Ce fichier couvre :
1. UI : bouton désactivé + spinner + message d'attente présents dans le HTML rendu, pour
   START PRACTICE, START EXAM et SUBMIT/CORRECTION (`app/templates/v1_session_start.html`,
   `app/templates/v1_session_submit_confirm.html`) — protection CLIENTE, meilleur effort,
   contournable (JS désactivé, requête rejouée directement) donc jamais la seule ligne de
   défense.
2. Protection SERVEUR (la vraie garantie, jamais contournable) :
   - `app.v1.routes_sessions._is_unstarted` : un double POST sur « Commencer » ne crée
     JAMAIS 2 sessions practice (exam était déjà protégé, § 12 du ticket #55) — vérifié
     par un double POST HTTP réel, avec le même jeton CSRF (reproduit exactement un
     double-clic avant que la page ne recharge).
   - `app.v1.session_service.submit_session` : réclamation atomique — un double POST sur
     « Terminer et corriger » ne déclenche jamais 2 corrections IA (vérifié via
     `FakeAIProvider.semantic_calls`), jamais 2 sessions marquées différemment.
   - Non-régression explicite : une VRAIE deuxième tentative (après avoir répondu à au
     moins une question) crée bien une session practice distincte — la politique
     « plusieurs sessions practice simultanées autorisées » (ticket #55 § 12) reste
     intacte, ce ticket ne bloque QUE le doublon accidentel immédiat.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import QuestionnaireSession, SessionStatus

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
    return {"text": "Réponse de test couvrant plusieurs phrases pour valider la correction."}


# =============================================================================================
# 1. UI — bouton désactivé, spinner, messages d'attente
# =============================================================================================


def test_practice_start_page_has_loading_state_markup(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    assert 'id="start-session-button"' in response.text
    assert "spinner-border" in response.text
    assert "Préparation de l'entraînement" in response.text
    assert "Génération des questions en cours" in response.text


def test_exam_start_page_has_loading_state_markup(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/exam")
    assert response.status_code == 200
    assert 'id="start-session-button"' in response.text
    assert "Préparation de l'évaluation" in response.text


def test_submit_confirm_page_has_loading_state_markup(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"/sessions/{session_id}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = authenticated_client.post(f"/sessions/{session_id}/answer", data=data, follow_redirects=False)

    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    assert response.status_code == 200
    assert 'id="submit-correction-button"' in response.text
    assert "spinner-border" in response.text
    assert "Correction en cours" in response.text
    assert len(fake.semantic_calls) == 0  # rien tant que le formulaire n'a pas été soumis


# =============================================================================================
# 2. Protection SERVEUR — double POST « Commencer »
# =============================================================================================


def test_double_post_practice_start_creates_only_one_session(authenticated_client, db_session, monkeypatch):
    """§ ticket #71 : « Double POST : pas 2 sessions ». Practice n'était PAS protégé
    avant #71 (exam l'était déjà, § 12 du ticket #55) — reproduit un double-clic exact :
    même jeton CSRF, deux POST consécutifs."""
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    data = {"csrf_token": token, "difficulty": "medium"}

    first = authenticated_client.post("/uaa/ampcr-mc01/practice/start", data=data, follow_redirects=False)
    second = authenticated_client.post("/uaa/ampcr-mc01/practice/start", data=data, follow_redirects=False)
    assert first.status_code == 303
    assert second.status_code == 303

    first_id = int(first.headers["location"].rsplit("/", 1)[-1])
    second_id = int(second.headers["location"].rsplit("/", 1)[-1])
    assert first_id == second_id, "les deux POST doivent aboutir à la MÊME session, jamais 2"

    created_session = db_session.get(QuestionnaireSession, first_id)
    sessions = db_session.query(QuestionnaireSession).filter_by(user_id=created_session.user_id).all()
    practice_sessions = [s for s in sessions if s.mode.value == "practice"]
    assert len(practice_sessions) == 1


def test_double_post_exam_start_creates_only_one_session(authenticated_client, db_session, monkeypatch):
    """Non-régression explicite : exam déjà protégé (§ 12 du ticket #55) — reconfirmé ici
    dans le cadre du ticket #71."""
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/exam")
    token = _csrf(response.text)
    data = {"csrf_token": token, "difficulty": "medium"}

    first = authenticated_client.post("/uaa/ampcr-mc01/exam/start", data=data, follow_redirects=False)
    second = authenticated_client.post("/uaa/ampcr-mc01/exam/start", data=data, follow_redirects=False)
    first_id = int(first.headers["location"].rsplit("/", 1)[-1])
    second_id = int(second.headers["location"].rsplit("/", 1)[-1])
    assert first_id == second_id


def test_double_post_global_ampcr_practice_start_creates_only_one_session(
    authenticated_client, db_session, monkeypatch
):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/modules/ampcr/practice")
    token = _csrf(response.text)
    data = {"csrf_token": token, "difficulty": "medium"}

    first = authenticated_client.post("/modules/ampcr/practice/start", data=data, follow_redirects=False)
    second = authenticated_client.post("/modules/ampcr/practice/start", data=data, follow_redirects=False)
    first_id = int(first.headers["location"].rsplit("/", 1)[-1])
    second_id = int(second.headers["location"].rsplit("/", 1)[-1])
    assert first_id == second_id


def test_genuine_second_practice_attempt_after_answering_creates_a_new_session(
    authenticated_client, db_session, monkeypatch
):
    """Non-régression : la politique « plusieurs sessions practice simultanées
    autorisées » (§ 12 du ticket #55) reste intacte — seul le doublon accidentel
    IMMÉDIAT (aucune réponse entre les deux) est bloqué par #71."""
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    first = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    first_id = int(first.headers["location"].rsplit("/", 1)[-1])

    # Répond à la première question de la première session — elle n'est plus "vierge".
    response = authenticated_client.get(f"/sessions/{first_id}?q=1")
    token = _csrf(response.text)
    data = {"csrf_token": token, "position": 1, "direction": "next"}
    data.update(_answer_payload_for(response.text))
    authenticated_client.post(f"/sessions/{first_id}/answer", data=data, follow_redirects=False)

    # Nouvelle tentative délibérée : doit créer une VRAIE deuxième session.
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    second = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    second_id = int(second.headers["location"].rsplit("/", 1)[-1])
    assert second_id != first_id


# =============================================================================================
# 3. Protection SERVEUR — double POST « Terminer et corriger » (aucune 2e correction IA)
# =============================================================================================


def test_double_post_submit_triggers_only_one_ai_correction(authenticated_client, db_session, monkeypatch):
    """§ ticket #71 : « Double POST : pas 2 corrections ; pas 2 appels IA. » Réclamation
    atomique (`session_service.submit_session`) vérifiée par un double POST HTTP réel,
    même jeton CSRF."""
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"/sessions/{session_id}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        authenticated_client.post(f"/sessions/{session_id}/answer", data=data, follow_redirects=False)

    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = _csrf(response.text)
    submit_data = {"csrf_token": token, "severity": "3"}

    first = authenticated_client.post(f"/sessions/{session_id}/submit", data=submit_data, follow_redirects=False)
    second = authenticated_client.post(f"/sessions/{session_id}/submit", data=submit_data, follow_redirects=False)
    assert first.status_code == 303
    assert second.status_code == 303

    assert len(fake.semantic_calls) == 1, "un seul appel de correction IA, jamais deux, malgré le double POST"

    db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED
    score_after_both_posts = session.score
    assert score_after_both_posts is not None


def test_submit_session_atomic_claim_prevents_concurrent_correction_at_service_level(db_session, monkeypatch):
    """Vérifie directement au niveau service (pas HTTP) que `submit_session` refuse une
    deuxième exécution une fois la session réclamée — reproduit la course la plus
    serrée possible (deux appels Python consécutifs, sans round-trip HTTP)."""
    from app.v1.models import (
        SessionDifficultyRequest,
        SessionMode,
        SessionQuestion,
        User,
        create_question,
    )
    from app.v1.session_service import submit_session

    ampcr, mc01 = _seed_mc01(db_session)
    user = User(email="ticket71@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="short_answer",
        content_json={"prompt": "Question de test.", "rubric": "Grille."},
        generation_source="manual",
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=ampcr.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0)
    )
    db_session.commit()

    fake = FakeAIProvider()
    result_1 = submit_session(db_session, session=session, provider=fake, severity_ui=3)
    result_2 = submit_session(db_session, session=session, provider=fake, severity_ui=3)

    assert len(fake.semantic_calls) == 1
    assert result_1.status == SessionStatus.COMPLETED
    assert result_2.status == SessionStatus.COMPLETED
    assert result_1.score == result_2.score

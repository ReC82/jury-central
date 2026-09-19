"""Ticket #73 — URGENT réponses longues : supprimer la limite silencieuse et éviter
toute troncature.

Audit (voir docs/claude-reports/2026-09-19_ticket-73_long-answer-capacity.md) : le seul
vrai plafond bloquant, avant ce ticket, était `maxlength="2000"` côté navigateur
(`app/templates/v1_session_question.html`) — soit la valeur par défaut de
`LongAnswerContent.max_length` (2000), soit un repli codé en dur à 2000 pour les 5 autres
types texte libre (`diagnostic`/`procedure`/`document_analysis`/`source_comparison`/
`troubleshooting`), qui n'exposaient encore aucun `max_length` du tout. Tout le reste de
la chaîne (parsing du formulaire, DB `JSON`, prompt IA, export Markdown, impression) était
déjà non borné.

Ce fichier couvre :
1. Les modèles Pydantic exposent désormais tous un `max_length` explicite (20000).
2. Bout en bout HTTP réel (pas de mock du côté formulaire) : un texte de 10 000+
   caractères survit à l'autosave, au rechargement, à la soumission, à la correction, à
   l'affichage des résultats et à l'export Markdown — sans aucune troncature, pour
   `long_answer` ET `diagnostic` (représentatif des 5 autres types texte libre, qui
   partagent exactement le même chemin de code générique — voir `_parse_answer_form`,
   `app/v1/routes_sessions.py`).
3. Le compteur de caractères visible est bien rendu et alimenté par le bon plafond.
4. short_answer garde une limite courte (hors périmètre de ce ticket, non touché).
5. Non-régression : aucun appel OpenAI réel, Ruff/tests globaux inchangés ailleurs.
"""

import re

from app.ai.fake_provider import FakeAIProvider
from app.models import Module
from app.seed import seed
from app.v1.models import (
    GenerationSource,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.question_types import (
    DiagnosticContent,
    DocumentAnalysisContent,
    LongAnswerContent,
    ProcedureContent,
    ShortAnswerContent,
    SourceComparisonContent,
    TroubleshootingContent,
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _build_single_question_session(db_session, *, question_type: str, content: dict, mode=SessionMode.PRACTICE):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    assert user is not None, "authenticated_client doit avoir déjà créé ce compte"

    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=None, question_type=question_type,
        content_json=content, generation_source=GenerationSource.MANUAL,
    )
    db_session.flush()

    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=ampcr.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(
            session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
        )
    )
    db_session.commit()
    return session.id


# Pas d'espace/retour à la ligne final : `describe_submitted_answer` applique `.strip()`
# (comportement voulu, sans perte de contenu réel) — un texte de test se terminant par un
# espace donnerait un faux positif de troncature lors de la comparaison exacte ci-dessous.
LONG_TEXT_10K = ("Ceci est une phrase de test pour la capacité de réponse longue. " * 162).strip()
assert len(LONG_TEXT_10K) >= 10_000, len(LONG_TEXT_10K)


# =============================================================================================
# 1. Modèles Pydantic — max_length désormais explicite partout
# =============================================================================================


def test_long_answer_default_max_length_is_20000():
    content = LongAnswerContent(prompt="?", rubric="grille")
    assert content.max_length == 20_000


def test_diagnostic_procedure_document_analysis_source_comparison_troubleshooting_expose_max_length():
    assert DiagnosticContent(prompt="?", rubric="grille").max_length == 20_000
    assert ProcedureContent(prompt="?", rubric="grille").max_length == 20_000
    assert DocumentAnalysisContent(prompt="?", source_document_version_id=1, rubric="grille").max_length == 20_000
    assert (
        SourceComparisonContent(prompt="?", source_document_version_ids=[1, 2], rubric="grille").max_length
        == 20_000
    )
    assert TroubleshootingContent(prompt="?", rubric="grille").max_length == 20_000


def test_long_answer_accepts_explicit_higher_max_length():
    """L'architecture permet de dépasser 20000 si un contenu précis le demande — jamais
    figé en dur ailleurs que cette valeur par défaut."""
    content = LongAnswerContent(prompt="?", rubric="grille", max_length=50_000)
    assert content.max_length == 50_000


def test_short_answer_keeps_its_short_default_untouched():
    """Hors périmètre du ticket (§ 7 : « les short_answer peuvent garder une limite
    raisonnable ») — non-régression explicite : toujours 200 par défaut."""
    content = ShortAnswerContent(prompt="?", accepted_answers=["x"])
    assert content.max_length == 200


# =============================================================================================
# 2. Bout en bout HTTP réel — long_answer, aucune troncature
# =============================================================================================


def test_10k_long_answer_survives_autosave_reload_submit_results_export(
    authenticated_client, db_session, monkeypatch
):
    session_id = _build_single_question_session(
        db_session, question_type="long_answer",
        content={"prompt": "Rédige une réponse argumentée.", "rubric": "grille"},
    )
    fake = _patch_fake_provider(monkeypatch)

    # UI -> autosave (POST)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert f'maxlength="{20_000}"' in response.text
    assert 'id="answer-char-counter"' in response.text
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": LONG_TEXT_10K},
        follow_redirects=False,
    )
    assert response.status_code == 303

    # Reload -> le texte complet doit réapparaître dans le textarea, jamais tronqué.
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert LONG_TEXT_10K in response.text

    # Submit -> correction (un seul appel IA batch, FakeAIProvider).
    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    # Ticket #88 : le POST ne corrige plus de façon synchrone — fait tourner le worker
    # explicitement (appel direct, pas de processus séparé) avant de lire un résultat.
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)
    assert len(fake.semantic_calls) == 1

    # Résultats -> le texte complet de LA RÉPONSE DE L'UTILISATEUR doit être affiché en entier.
    response = authenticated_client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert LONG_TEXT_10K in response.text

    # Export Markdown -> même exigence, aucune troncature.
    response = authenticated_client.get(f"/sessions/{session_id}/export.md")
    assert response.status_code == 200
    assert LONG_TEXT_10K in response.text


def test_10k_diagnostic_answer_survives_full_round_trip(authenticated_client, db_session, monkeypatch):
    """Représentatif des 5 autres types texte libre (procedure/document_analysis/
    source_comparison/troubleshooting partagent exactement le même chemin de code
    générique `_parse_answer_form`/textarea, voir docstring du module)."""
    session_id = _build_single_question_session(
        db_session, question_type="diagnostic",
        content={"prompt": "Diagnostique la panne décrite.", "rubric": "grille"},
    )
    fake = _patch_fake_provider(monkeypatch)

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": LONG_TEXT_10K},
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert LONG_TEXT_10K in response.text

    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    # Ticket #88 : le POST ne corrige plus de façon synchrone — fait tourner le worker
    # explicitement (appel direct, pas de processus séparé) avant de lire un résultat.
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)

    response = authenticated_client.get(f"/sessions/{session_id}")
    assert LONG_TEXT_10K in response.text

    response = authenticated_client.get(f"/sessions/{session_id}/export.md")
    assert LONG_TEXT_10K in response.text


def test_20k_long_answer_not_truncated_by_form_parsing_or_db(authenticated_client, db_session, monkeypatch):
    """Vérifie explicitement la marge haute (20000, § 2 du ticket : « acceptable si
    l'architecture le permet proprement sans risque » — confirmé par l'audit : DB JSON et
    parsing de formulaire non bornés)."""
    text_20k = ("Argument détaillé et développé. " * 628).strip()  # ~20 095 caractères
    assert len(text_20k) >= 20_000
    session_id = _build_single_question_session(
        db_session, question_type="long_answer",
        content={"prompt": "Rédige une réponse très développée.", "rubric": "grille", "max_length": 25_000},
    )
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": text_20k},
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert text_20k in response.text


# =============================================================================================
# 3. Compteur de caractères visible
# =============================================================================================


def test_character_counter_present_with_max_length_data_attribute(authenticated_client, db_session, monkeypatch):
    session_id = _build_single_question_session(
        db_session, question_type="long_answer",
        content={"prompt": "Rédige une réponse.", "rubric": "grille"},
    )
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert 'data-max-length="20000"' in response.text
    assert "answer-textarea" in response.text
    # Le script de mise à jour du compteur est bien présent (comportement, pas seulement le marqueur).
    assert "answer-char-counter" in response.text
    assert "toLocaleString" in response.text


def test_choice_and_structured_question_types_never_render_the_free_text_counter(
    authenticated_client, db_session, monkeypatch
):
    """Le compteur ne doit apparaître QUE pour les types texte libre — jamais pour un
    QCM/classification/ordering (non-régression de l'affichage existant)."""
    session_id = _build_single_question_session(
        db_session, question_type="multiple_choice",
        content={
            "prompt": "Choix ?", "options": [{"option_id": "0", "label": "A"}, {"option_id": "1", "label": "B"}],
            "correct_option_ids": ["0"], "min_selections": 1, "max_selections": 1,
        },
    )
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    assert response.status_code == 200
    assert "answer-char-counter" not in response.text

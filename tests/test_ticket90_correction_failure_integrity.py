"""Ticket #90 — AUCUN FAUX 0 SI CORRECTION IA INDISPONIBLE.

Bug réel observé sur la session 43 (staging) : quand l'IA était indisponible pendant la
correction asynchrone (#88), les questions sémantiques (`long_answer`/`diagnostic`/
`short_answer` développé) recevaient un 0/1 fabriqué ET la session passait `COMPLETED`
comme si la correction était réellement terminée. Ce fichier prouve que ce n'est plus le
cas : une question qui a réellement besoin de l'IA reste `PENDING_CORRECTION`/
`CORRECTION_FAILED` (jamais 0), la session devient `CORRECTION_INCOMPLETE` (jamais
`COMPLETED`) tant que toutes les questions score-gating n'ont pas une correction réelle,
et un retry cible UNIQUEMENT ce qui manque.

Couvre aussi les deux bugs de correction déterministe réels du ticket :
- § 8 : masque /29, réponse « 256 - 248 = 8, donc 8 est l'incrément » devait scorer 1/1,
  pas 0/1 (`app.answer_checking.extract_last_number`).
- § 9 : une short_answer sémantique (« Cite deux contrôles… », « Explique… ») ne doit
  jamais être notée par égalité textuelle stricte, même avec `accepted_answers`
  (`app.answer_checking.is_semantic_short_answer_prompt`).

Aucun appel OpenAI réel : `FakeAIProvider` partout (et un provider délibérément en panne
pour simuler `AIProviderError`).
"""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.local_correction import _check_numeric
from app.ai.provider import AIProviderError
from app.ai.schemas import QuestionnaireQuestion
from app.answer_checking import extract_last_number, is_semantic_short_answer_prompt
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import (
    CorrectionJob,
    CorrectionJobStatus,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.session_service import (
    CorrectionJobNotRetryableError,
    claim_next_pending_correction_job,
    enqueue_correction,
    get_correction_job,
    retry_correction_job,
    run_correction_job,
    save_answer,
    submit_session,
)

# =============================================================================================
# Helpers
# =============================================================================================


class _FailingProvider(FakeAIProvider):
    """Simule un fournisseur IA totalement indisponible — jamais un vrai appel OpenAI."""

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        raise AIProviderError("panne simulée")


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch, fake=None):
    fake = fake if fake is not None else FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _seed_mc01(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    return ampcr, mc01


def _build_session(db_session, ampcr, mc01, questions: list[tuple[str, dict]]) -> QuestionnaireSession:
    """Construit une session avec des questions arbitraires (type, content_json) déjà
    répondues — jamais via l'IA (`generation_source="manual"`), pour cibler exactement le
    mélange déterministe/sémantique voulu par chaque test."""
    user = User(email=f"ticket90-{id(questions)}@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=ampcr.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=len(questions),
    )
    db_session.add(session)
    db_session.flush()

    for position, (question_type, content) in enumerate(questions, start=1):
        question = create_question(
            db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type=question_type,
            content_json=content, generation_source="manual",
        )
        db_session.add(
            SessionQuestion(
                session_id=session.id, question_version_id=question.current_version_id,
                position=position, points_max=1.0,
            )
        )
    db_session.commit()
    return session


def _answer_all(db_session, session: QuestionnaireSession, answer_jsons: list[dict]) -> None:
    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    for sq, answer_json in zip(session_questions, answer_jsons, strict=True):
        save_answer(db_session, session_question=sq, answer_json=answer_json)


def _run_job(db_session, session: QuestionnaireSession, provider, severity_ui: int = 3) -> CorrectionJob:
    job = enqueue_correction(db_session, session=session, severity_ui=severity_ui)
    claimed = claim_next_pending_correction_job(db_session)
    return run_correction_job(db_session, job=claimed or job, provider=provider)


_MC_QUESTION = ("multiple_choice", {
    "prompt": "Quel protocole est orienté connexion ?",
    "options": [{"option_id": "a", "label": "TCP"}, {"option_id": "b", "label": "UDP"}],
    "min_selections": 1, "max_selections": 1, "correct_option_ids": ["a"],
})
_LONG_ANSWER_QUESTION = ("long_answer", {"prompt": "Explique la démarche de diagnostic.", "rubric": "grille"})
_DIAGNOSTIC_QUESTION = ("diagnostic", {"prompt": "Diagnostique la panne décrite ci-dessus.", "rubric": "grille"})


# =============================================================================================
# 1. Aucun faux 0 quand l'IA est indisponible pour une question sémantique
# =============================================================================================


def test_ai_provider_error_on_one_semantic_question_never_produces_a_zero(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION, _LONG_ANSWER_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}, {"text": "Ma réponse développée."}])

    job = _run_job(db_session, session, _FailingProvider())

    db_session.refresh(session)
    assert job.status == CorrectionJobStatus.INCOMPLETE
    assert session.status == SessionStatus.CORRECTION_INCOMPLETE
    assert session.score is None

    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    semantic_answer = sqs[1].answer
    assert semantic_answer.points_awarded is None, "jamais un 0 fabriqué"
    assert semantic_answer.correction_status.value == "failed"


def test_ai_provider_error_on_four_semantic_questions_keeps_session_not_completed(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    questions = [_MC_QUESTION] + [_LONG_ANSWER_QUESTION] * 4
    session = _build_session(db_session, ampcr, mc01, questions)
    _answer_all(
        db_session, session,
        [{"selected_option_ids": ["a"]}] + [{"text": "Réponse développée."}] * 4,
    )

    job = _run_job(db_session, session, _FailingProvider())

    db_session.refresh(session)
    assert job.status == CorrectionJobStatus.INCOMPLETE
    assert session.status != SessionStatus.COMPLETED
    assert session.status == SessionStatus.CORRECTION_INCOMPLETE

    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    for sq in sqs[1:]:
        assert sq.answer.points_awarded is None
        assert sq.answer.correction_status.value == "failed"


def test_deterministic_questions_remain_correctly_scored_despite_ai_failure(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION, _LONG_ANSWER_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}, {"text": "Réponse."}])

    _run_job(db_session, session, _FailingProvider())

    db_session.refresh(session)
    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    deterministic_answer = sqs[0].answer
    assert deterministic_answer.correction_status.value == "corrected"
    assert deterministic_answer.points_awarded == 1.0


def test_deterministic_only_session_still_completes_even_with_failing_provider(db_session):
    """Une session 100% déterministe (jamais besoin de l'IA pour le score) doit terminer
    normalement même si le fournisseur configuré est en panne — non-régression directe du
    comportement §55/§62 (le paramètre `_UnconfiguredProvider` ne doit jamais bloquer une
    session qui n'a jamais besoin de lui pour son SCORE)."""
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["b"]}])  # réponse fausse -> explain_only

    job = _run_job(db_session, session, _FailingProvider())

    db_session.refresh(session)
    assert job.status == CorrectionJobStatus.COMPLETED
    assert session.status == SessionStatus.COMPLETED
    assert session.score == 0.0


# =============================================================================================
# 2. Retry ciblé
# =============================================================================================


def test_retry_targets_only_unresolved_questions_and_completes(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION, _LONG_ANSWER_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}, {"text": "Réponse développée."}])

    _run_job(db_session, session, _FailingProvider())
    db_session.refresh(session)
    assert session.status == SessionStatus.CORRECTION_INCOMPLETE

    working = FakeAIProvider()
    job = get_correction_job(db_session, session_id=session.id)
    retry_correction_job(db_session, job=job, session=session)
    db_session.refresh(session)
    assert session.status == SessionStatus.CORRECTING

    result_job = _run_job(db_session, session, working)

    db_session.refresh(session)
    assert result_job.status == CorrectionJobStatus.COMPLETED
    assert session.status == SessionStatus.COMPLETED
    assert session.score is not None
    # Une seule question avait besoin de l'IA -> un seul appel batch, jamais un second pour
    # la question déterministe déjà acquise.
    assert len(working.semantic_calls) == 1


def test_retry_never_modifies_already_corrected_answers(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION, _LONG_ANSWER_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}, {"text": "Réponse développée."}])

    _run_job(db_session, session, _FailingProvider())
    db_session.refresh(session)
    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    deterministic_points_before = sqs[0].answer.points_awarded
    deterministic_answer_json_before = dict(sqs[0].answer.answer_json)

    job = get_correction_job(db_session, session_id=session.id)
    retry_correction_job(db_session, job=job, session=session)
    _run_job(db_session, session, FakeAIProvider())

    db_session.refresh(session)
    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    assert sqs[0].answer.points_awarded == deterministic_points_before
    assert sqs[0].answer.answer_json == deterministic_answer_json_before


def test_retry_raises_when_job_is_neither_failed_nor_incomplete(db_session):
    import pytest

    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}])
    _run_job(db_session, session, FakeAIProvider())
    db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED

    job = get_correction_job(db_session, session_id=session.id)
    with pytest.raises(CorrectionJobNotRetryableError):
        retry_correction_job(db_session, job=job, session=session)


# =============================================================================================
# 3. /29 — masque 255.255.255.248, réponse noyée dans une explication
# =============================================================================================


def test_increment_248_answer_with_explanatory_prose_scores_1_of_1():
    q = QuestionnaireQuestion(
        question_id="q1", type="numeric", prompt="Masque 255.255.255.248, quel est l'incrément ?",
        points_max=1.0, numeric_answer=8, numeric_tolerance=0,
    )
    assert _check_numeric(q, "256 - 248 = 8, donc 8 est l'incrément.") is True


def test_extract_last_number_handles_accents_punctuation_and_word_order():
    assert extract_last_number("256 - 248 = 8, donc 8 est l'incrément.") == 8
    assert extract_last_number("8") == 8
    assert extract_last_number("le résultat, après calcul, donne 8") == 8
    assert extract_last_number("aucun nombre ici") is None


def test_extract_last_number_rejects_a_wrong_final_conclusion():
    """Ne généralise pas en fuzzy matching dangereux : une réponse qui mentionne la bonne
    valeur en passant mais conclut sur une autre reste fausse."""
    assert extract_last_number("je pensais que c'était 8 mais en fait c'est 16") == 16


def test_bare_numeric_answer_still_works_as_before():
    q = QuestionnaireQuestion(
        question_id="q1", type="numeric", prompt="Incrément ?", points_max=1.0,
        numeric_answer=8, numeric_tolerance=0,
    )
    assert _check_numeric(q, "8") is True
    assert _check_numeric(q, "16") is False


def test_increment_248_end_to_end_via_correct_locally(db_session):
    from app.ai.local_correction import correct_locally

    q = QuestionnaireQuestion(
        question_id="q1", type="numeric", prompt="Masque 255.255.255.248, incrément ?",
        points_max=1.0, numeric_answer=8, numeric_tolerance=0,
    )
    result = correct_locally(q, "256 - 248 = 8, donc 8 est l'incrément.")
    assert result.points_awarded == 1.0
    assert result.correct is True


# =============================================================================================
# 4. DETERMINISTIC_SHORT vs SEMANTIC_SHORT
# =============================================================================================


def test_semantic_short_answer_prompts_detected():
    assert is_semantic_short_answer_prompt("Quelle démarche suivre et pourquoi ?") is True
    assert is_semantic_short_answer_prompt("Cite deux contrôles à effectuer avant de conclure.") is True
    assert is_semantic_short_answer_prompt("Explique pourquoi ce test est nécessaire.") is True
    assert is_semantic_short_answer_prompt("Compare le HDD et le SSD.") is True


def test_deterministic_short_answer_prompts_not_flagged_as_semantic():
    assert is_semantic_short_answer_prompt("Que signifie l'acronyme ESD ?") is False
    assert is_semantic_short_answer_prompt("Quelle commande affiche la configuration IP ?") is False
    assert is_semantic_short_answer_prompt("Quel masque pour un /27 ?") is False


def test_semantic_short_answer_requires_ai_even_with_accepted_answers():
    q = QuestionnaireQuestion(
        question_id="q1", type="short_answer", prompt="Explique pourquoi ce contrôle est nécessaire.",
        points_max=1.0, accepted_answers=["une réponse type"],
    )
    assert q.requires_ai_correction() is True


def test_deterministic_short_answer_stays_local_with_accepted_answers():
    q = QuestionnaireQuestion(
        question_id="q1", type="short_answer", prompt="Que signifie ESD ?",
        points_max=1.0, accepted_answers=["décharge électrostatique"],
    )
    assert q.requires_ai_correction() is False


def test_semantic_short_answer_never_scored_by_strict_text_equality_end_to_end(db_session):
    """Reproduit § 90.9 : une short_answer sémantique avec accepted_answers ne doit jamais
    recevoir 0 juste parce que le texte diffère littéralement — elle part directement à
    l'IA (jamais une comparaison stricte), qui peut la noter correctement."""
    ampcr, mc01 = _seed_mc01(db_session)
    semantic_short = ("short_answer", {
        "prompt": "Explique pourquoi il faut couper l'alimentation avant d'intervenir.",
        "accepted_answers": ["pour éviter tout risque électrique"],
        "rubric": "Doit mentionner un risque électrique ou de choc.",
    })
    session = _build_session(db_session, ampcr, mc01, [semantic_short])
    _answer_all(db_session, session, [{"text": "Pour ne pas prendre de risque de choc électrique pendant l'intervention."}])

    job = _run_job(db_session, session, FakeAIProvider())

    db_session.refresh(session)
    assert job.status == CorrectionJobStatus.COMPLETED
    assert session.status == SessionStatus.COMPLETED


# =============================================================================================
# 5. Non-régression #70 (crédit partiel) et #88 (worker/submit non bloquant)
# =============================================================================================


def test_classification_partial_credit_not_regressed_by_ticket_90(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    classification_question = ("classification", {
        "prompt": "Classe ces éléments.",
        "categories": ["HDD", "SSD"],
        "elements": ["Plateaux magnétiques", "Mémoire flash NAND"],
        "correct_categories": [0, 1],
    })
    session = _build_session(db_session, ampcr, mc01, [classification_question])
    _answer_all(db_session, session, [{"assignments": [0, 0]}])  # 1 correct sur 2

    job = _run_job(db_session, session, FakeAIProvider())

    db_session.refresh(session)
    assert job.status == CorrectionJobStatus.COMPLETED
    sqs = sorted(session.session_questions, key=lambda sq: sq.position)
    assert sqs[0].answer.points_awarded == 0.5


def test_submit_session_function_still_unchanged_and_directly_usable(db_session, monkeypatch):
    """#70/#71/#74 continuent d'utiliser `submit_session` (synchrone) directement — ce
    ticket ne le modifie pas."""
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session(db_session, ampcr, mc01, [_MC_QUESTION])
    _answer_all(db_session, session, [{"selected_option_ids": ["a"]}])

    fake = FakeAIProvider()
    result = submit_session(db_session, session=session, provider=fake, severity_ui=3)
    assert result.status == SessionStatus.COMPLETED
    assert result.score is not None


# =============================================================================================
# 6. HTTP : historique, export/print incomplete, submit non bloquant, double submit
# =============================================================================================


def _register_and_login(client, email="ticket90-http@example.test"):
    r = client.get("/register")
    token = _csrf(r.text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": email, "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "T90",
        },
    )


def test_results_page_shows_incomplete_banner_and_retry_button(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _register_and_login(client)
    _patch_fake_provider(monkeypatch, _FailingProvider())

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    session_url = r.headers["location"]
    session_id = int(session_url.rstrip("/").split("/")[-1])

    session = db_session.get(QuestionnaireSession, session_id)
    position = 1
    while True:
        r = client.get(f"{session_url}?q={position}")
        if r.status_code != 200:
            break
        token = _csrf(r.text)
        direction = "submit" if "Terminer" in r.text else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if 'name="option_id"' in r.text:
            m = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', r.text)
            if m:
                data["option_id"] = m.group(1)
        elif 'name="text"' in r.text:
            data["text"] = "Réponse développée expliquant la démarche suivie."
        r = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        if direction == "submit":
            break
        position += 1

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=_FailingProvider())

    results = client.get(session_url)
    db_session.refresh(session)
    if session.status.value == "correction_incomplete":
        assert results.status_code == 200
        assert "CORRECTION INCOMPLÈTE" in results.text
        assert "Réessayer la correction" in results.text
        assert "retry-correction" in results.text


def test_history_distinguishes_correcting_incomplete_and_completed(client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _register_and_login(client)
    fake = _patch_fake_provider(monkeypatch, FakeAIProvider())

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    session_url = r.headers["location"]

    position = 1
    while True:
        r = client.get(f"{session_url}?q={position}")
        if r.status_code != 200:
            break
        token = _csrf(r.text)
        direction = "submit" if "Terminer" in r.text else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if 'name="option_id"' in r.text:
            m = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', r.text)
            if m:
                data["option_id"] = m.group(1)
        elif 'name="text"' in r.text:
            data["text"] = "Réponse."
        r = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        if direction == "submit":
            break
        position += 1

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)
    client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)

    history_before_worker = client.get("/mes-sessions")
    assert "Correction en cours" in history_before_worker.text

    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)

    history_after = client.get("/mes-sessions")
    assert "Terminé" in history_after.text


def test_submit_still_nonblocking_and_double_submit_still_single_job(client, db_session, monkeypatch):
    """Non-régression #88 directe."""
    _seed_mc01(db_session)
    _register_and_login(client)
    _patch_fake_provider(monkeypatch, FakeAIProvider())

    r = client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(r.text)
    r = client.post("/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False)
    session_url = r.headers["location"]
    session_id = int(session_url.rstrip("/").split("/")[-1])

    position = 1
    while True:
        r = client.get(f"{session_url}?q={position}")
        if r.status_code != 200:
            break
        token = _csrf(r.text)
        direction = "submit" if "Terminer" in r.text else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if 'name="option_id"' in r.text:
            m = re.search(r'name="option_id"\s+id="[^"]*"\s+value="(\d+)"', r.text)
            if m:
                data["option_id"] = m.group(1)
        elif 'name="text"' in r.text:
            data["text"] = "Réponse."
        r = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        if direction == "submit":
            break
        position += 1

    r = client.get(f"{session_url}/submit-confirm")
    token = _csrf(r.text)

    import time

    t0 = time.monotonic()
    first = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    second = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    elapsed = time.monotonic() - t0

    assert first.status_code == 303
    assert second.status_code == 303
    assert elapsed < 1.0
    assert db_session.query(CorrectionJob).filter_by(session_id=session_id).count() == 1

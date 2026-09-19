"""Ticket #70 — recotation + points partiels + feedback pédagogique.

A. RE-COTATION NON DESTRUCTIVE : « Comparer une autre sévérité » sur une session
terminée — ne modifie JAMAIS le résultat original (réponses/correction/score
immuables), simule une correction séparée à une autre sévérité
(`app.v1.session_service.simulate_severity_comparison`). Seules les questions
sémantiques peuvent varier — les questions déterministes gardent toujours le score
verrouillé de `correct_locally`, indépendant de la sévérité.

B. POINTS PARTIELS : `classification`/`matching` notent désormais au prorata du nombre
d'éléments correctement associés (ex. 2 corrects sur 4 → 0.5/1.0), plus jamais
all-or-nothing. `ordering` reste délibérément EXCLU (§ AUDIT du ticket — voir
`app/ai/local_correction.py`, un crédit partiel position par position y serait trompeur).

C. FEEDBACK IA PLUS PÉDAGOGIQUE : le prompt système de correction sémantique impose
désormais une structure en 6 points pour toute réponse incorrecte/partielle
(`app.ai.prompts.CORRECT_SEMANTIC_SYSTEM_PROMPT`). Deux mini-cours AMPCR reçoivent en
plus des FAITS DE RÉFÉRENCE concrets transmis verbatim par le ticket (jamais inventés) :
MC17 (subnetting : masques/incréments) et MC15 (câblage RJ45 : ordre T568B, règle
testeur).

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.local_correction import correct_locally
from app.ai.prompts import CORRECT_SEMANTIC_SYSTEM_PROMPT
from app.ai.provider import AIProviderError
from app.ai.schemas import QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.ampcr_plan import AMPCR_CONTEXTS
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import (
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.session_service import (
    SessionNotCompletedError,
    simulate_severity_comparison,
    submit_session,
)

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


def _build_session_with_question(db_session, *, module_id: int, uaa_id: int, question_type: str, content: dict, mode=SessionMode.PRACTICE):
    user = User(email="ticket70@example.invalid", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    question = create_question(
        db_session, module_id=module_id, uaa_id=uaa_id, question_type=question_type,
        content_json=content, generation_source="manual",
    )
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0)
    )
    db_session.commit()
    return session


# =============================================================================================
# A. Re-cotation non destructive
# =============================================================================================


def test_compare_severity_requires_a_completed_session(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session_with_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="short_answer",
        content={"prompt": "Question.", "rubric": "Grille."},
    )
    fake = FakeAIProvider()
    try:
        simulate_severity_comparison(db_session, session=session, provider=fake, severity_ui=5)
        raise AssertionError("devrait lever SessionNotCompletedError sur une session IN_PROGRESS")
    except SessionNotCompletedError:
        pass


def test_compare_severity_never_modifies_the_original_result(db_session):
    """§ ticket #70 : « ne jamais modifier le résultat original » — vérifié directement :
    score, réponses et feedback_json restent identiques après la simulation."""
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session_with_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="short_answer",
        content={"prompt": "Explique un concept.", "rubric": "Grille de correction."},
    )
    sq = session.session_questions[0]
    from app.v1.models import SessionAnswer

    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"text": "Ma réponse de test."}))
    db_session.commit()

    fake = FakeAIProvider()
    submit_session(db_session, session=session, provider=fake, severity_ui=3)
    db_session.refresh(session)
    original_score = session.score
    original_feedback = dict(session.session_questions[0].answer.feedback_json)
    original_points = session.session_questions[0].answer.points_awarded

    comparison = simulate_severity_comparison(db_session, session=session, provider=fake, severity_ui=5)

    db_session.refresh(session)
    assert session.score == original_score
    assert session.session_questions[0].answer.points_awarded == original_points
    assert session.session_questions[0].answer.feedback_json == original_feedback
    assert session.status == SessionStatus.COMPLETED
    assert comparison.original_score == original_score
    assert comparison.severity_ui == 5


def test_compare_severity_deterministic_score_never_varies(db_session):
    """Une question déterministe (multiple_choice) garde EXACTEMENT le même score entre
    l'original et n'importe quelle comparaison — seule une question sémantique peut
    varier."""
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session_with_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="multiple_choice",
        content={
            "prompt": "Quel protocole ?", "options": [{"option_id": "0", "label": "A"}, {"option_id": "1", "label": "B"}],
            "min_selections": 1, "max_selections": 1, "correct_option_ids": ["0"], "explanation": "x",
        },
    )
    sq = session.session_questions[0]
    from app.v1.models import SessionAnswer

    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"selected_option_ids": ["0"]}))
    db_session.commit()

    fake = FakeAIProvider()
    submit_session(db_session, session=session, provider=fake, severity_ui=1)
    db_session.refresh(session)

    for severity in (2, 3, 4, 5):
        comparison = simulate_severity_comparison(db_session, session=session, provider=fake, severity_ui=severity)
        assert comparison.comparative_score == session.score  # QCM correct : score inchangé quelle que soit la sévérité


def test_compare_severity_http_round_trip_shows_both_scores(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
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
    authenticated_client.post(f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)

    response = authenticated_client.get(f"/sessions/{session_id}")
    original_score_text = re.search(r"Score : ([\d.]+)", response.text).group(1)

    response = authenticated_client.get(f"/sessions/{session_id}")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/compare-severity", data={"csrf_token": token, "severity": "5"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Comparaison de sévérité" in response.text
    assert f"Score original : <strong>{original_score_text}</strong>" in response.text
    assert "Score sévérité 5" in response.text

    # Le résultat original en base n'a pas bougé.
    db_session.refresh(session)
    assert str(session.score) == original_score_text


def test_compare_severity_handles_ai_provider_error_gracefully(authenticated_client, db_session, monkeypatch):
    _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"}, follow_redirects=False,
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
    authenticated_client.post(f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)

    fake.correct_semantic_batch = lambda *a, **k: (_ for _ in ()).throw(AIProviderError("panne simulée"))

    response = authenticated_client.get(f"/sessions/{session_id}")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/compare-severity", data={"csrf_token": token, "severity": "5"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "indisponible" in response.text.lower() or "réessaie" in response.text.lower()


# =============================================================================================
# B. Points partiels — classification/matching, jamais ordering
# =============================================================================================


def test_classification_partial_credit_exact_ticket_example():
    """4 items, 2 corrects => 0.5/1.0 (exemple exact du ticket)."""
    question = QuestionnaireQuestion(
        question_id="q1", type="classification", points_max=1.0, prompt="Classe.",
        categories=["A", "B"], elements=["e1", "e2", "e3", "e4"], correct_categories=[0, 1, 0, 1],
    )
    result = correct_locally(question, [0, 0, 1, 1])
    assert result.points_awarded == 0.5
    assert result.correct is False


def test_classification_partial_credit_all_correct_is_full_score():
    question = QuestionnaireQuestion(
        question_id="q1", type="classification", points_max=2.0, prompt="Classe.",
        categories=["A", "B"], elements=["e1", "e2"], correct_categories=[0, 1],
    )
    result = correct_locally(question, [0, 1])
    assert result.points_awarded == 2.0
    assert result.correct is True


def test_matching_partial_credit():
    question = QuestionnaireQuestion(
        question_id="q1", type="matching", points_max=2.0, prompt="Associe.",
        pairs_left=["g1", "g2"], pairs_right=["d1", "d2"], correct_pairs=[0, 1],
    )
    result = correct_locally(question, [1, 1])  # 1 correct sur 2
    assert result.points_awarded == 1.0
    assert result.correct is False


def test_classification_malformed_submission_gets_zero_credit_not_a_crash():
    question = QuestionnaireQuestion(
        question_id="q1", type="classification", points_max=1.0, prompt="Classe.",
        categories=["A", "B"], elements=["e1", "e2"], correct_categories=[0, 1],
    )
    result = correct_locally(question, "pas une liste")
    assert result.points_awarded == 0.0
    assert result.correct is False


def test_ordering_remains_all_or_nothing_not_touched_by_this_ticket():
    """§ AUDIT du ticket : ordering explicitement EXCLU du crédit partiel — non-régression
    explicite, une inversion partielle reste notée 0."""
    question = QuestionnaireQuestion(
        question_id="q1", type="ordering", points_max=1.0, prompt="Ordonne.",
        order_items=["a", "b", "c", "d"], correct_order=[0, 1, 2, 3],
    )
    result = correct_locally(question, [1, 0, 2, 3])  # une seule inversion adjacente
    assert result.points_awarded == 0.0
    assert result.correct is False


def test_classification_partial_credit_end_to_end_via_submit_session(db_session):
    ampcr, mc01 = _seed_mc01(db_session)
    session = _build_session_with_question(
        db_session, module_id=ampcr.id, uaa_id=mc01.id, question_type="classification",
        content={
            "prompt": "Classe ces 4 éléments.", "categories": ["Cat A", "Cat B"],
            "elements": ["e1", "e2", "e3", "e4"], "correct_categories": [0, 1, 0, 1], "explanation": "x",
        },
    )
    sq = session.session_questions[0]
    from app.v1.models import SessionAnswer

    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"assignments": [0, 0, 1, 1]}))
    db_session.commit()

    fake = FakeAIProvider()
    submit_session(db_session, session=session, provider=fake, severity_ui=3)
    db_session.refresh(session)
    assert session.score == 0.5


# =============================================================================================
# C. Feedback IA plus pédagogique
# =============================================================================================


def test_system_prompt_requires_the_six_point_pedagogical_structure():
    for marker in (
        "où se situe précisément l'erreur",
        "quelle est la bonne réponse",
        "le raisonnement",
        "règle/",
        "mnémotechnique",
        "notion/quel cours revoir",
    ):
        assert marker in CORRECT_SEMANTIC_SYSTEM_PROMPT


def test_system_prompt_forbids_penalizing_a_verification_already_done():
    assert "ne la lui reproche jamais comme manquante" in CORRECT_SEMANTIC_SYSTEM_PROMPT


def test_mc17_context_has_subnetting_reference_facts():
    context = AMPCR_CONTEXTS["ampcr-mc17"]
    for fact in ("255.255.255.128", "255.255.255.240", "incrément 16", "non contigus"):
        assert fact in context.constraints


def test_mc15_context_has_t568b_order_and_tester_rule():
    context = AMPCR_CONTEXTS["ampcr-mc15"]
    for fact in (
        "1 blanc-orange", "2 orange", "8 brun", "testeur RJ45 sert précisément",
    ):
        assert fact in context.constraints


def test_unrelated_mc_context_has_no_leaked_reference_facts():
    """Les faits MC17/MC15 ne doivent JAMAIS apparaître dans un autre mini-cours."""
    context = AMPCR_CONTEXTS["ampcr-mc20"]
    assert "255.255.255.240" not in context.constraints
    assert "blanc-orange" not in context.constraints

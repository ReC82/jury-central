"""Ticket #45 — Rating adaptatif V1 : difficulté empirique des questions et niveau par
module (`app.v1.rating`). Aucun appel IA réel : `FakeAIProvider` uniquement."""

import random

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module, Subject
from app.v1.models import (
    DEFAULT_MODULE_RATING,
    AnswerCorrectionStatus,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    UserModuleRating,
    create_question,
)
from app.v1.rating import (
    ADAPTIVE_BAND,
    RATING_MAX,
    RATING_MIN,
    apply_session_rating,
    expected_success,
    generation_difficulty_fr,
    k_question,
    k_user,
    order_by_proximity,
    question_rating,
)
from app.v1.session_service import (
    claim_next_pending_correction_job,
    compose_selection,
    enqueue_correction,
    run_correction_job,
)

# =============================================================================================
# Helpers
# =============================================================================================


def _module(db, code="M45"):
    subject = Subject(name=f"Matière {code}", slug=f"matiere-{code.lower()}")
    db.add(subject)
    db.flush()
    module = Module(code=code, slug=f"module-{code.lower()}", subject_id=subject.id)
    db.add(module)
    db.flush()
    uaa = UAA(code=f"{code}-U1", title="UAA test", slug=f"uaa-{code.lower()}", module_id=module.id)
    db.add(uaa)
    db.commit()
    return module, uaa


def _user(db, email="t45@example.invalid"):
    user = User(email=email, password_hash="x", display_name="t45")
    db.add(user)
    db.commit()
    return user


def _question(db, module, uaa, n, difficulty=None):
    return create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type="short_answer",
        content_json={"prompt": f"Question #45 numéro {n} ?", "rubric": "Grille."},
        generation_source="manual", difficulty_declared=difficulty,
    )


def _completed_session(db, user, module, questions, scores, *, blank=()):
    """Session COMPLETED avec réponses déjà corrigées (`scores[i]` = points sur 1)."""
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.COMPLETED,
        question_count=len(questions), parameters_json={"severity": 3},
    )
    db.add(session)
    db.flush()
    for position, (question, score) in enumerate(zip(questions, scores, strict=True), start=1):
        sq = SessionQuestion(
            session_id=session.id, question_version_id=question.current_version_id,
            position=position, points_max=1.0,
        )
        db.add(sq)
        db.flush()
        db.add(SessionAnswer(
            session_question_id=sq.id,
            answer_json={} if position - 1 in blank else {"text": "réponse"},
            correction_status=AnswerCorrectionStatus.CORRECTED,
            points_awarded=score,
            feedback_json={"correct": score >= 1.0, "points_max": 1.0},
        ))
    session.score = sum(scores)
    db.commit()
    db.refresh(session)
    return session


# =============================================================================================
# 1. Formules et bornes
# =============================================================================================


def test_expected_success_is_symmetric_and_monotonic():
    assert expected_success(1000, 1000) == pytest.approx(0.5)
    assert expected_success(1200, 1000) > 0.5 > expected_success(800, 1000)
    assert expected_success(1400, 1000) == pytest.approx(10 / 11)


def test_k_factors_decrease_with_experience_and_stay_bounded():
    assert k_user(0) == 64.0
    assert k_user(5) < k_user(0)
    assert k_user(10_000) == 16.0
    assert k_question(0) == 40.0
    assert k_question(10_000) == 8.0


def test_initial_question_rating_follows_declared_difficulty(db_session):
    module, uaa = _module(db_session)
    easy = _question(db_session, module, uaa, 1, QuestionDifficulty.EASY)
    hard = _question(db_session, module, uaa, 2, QuestionDifficulty.HARD)
    none = _question(db_session, module, uaa, 3)
    assert question_rating(easy) == 900.0
    assert question_rating(hard) == 1100.0
    assert question_rating(none) == DEFAULT_MODULE_RATING
    assert easy.difficulty_rating is None  # jamais écrit tant qu'aucune réponse notée


def test_generation_difficulty_mapping():
    assert generation_difficulty_fr(800) == "facile"
    assert generation_difficulty_fr(1000) == "moyen"
    assert generation_difficulty_fr(1200) == "difficile"


# =============================================================================================
# 2. Progression / régression après un questionnaire terminé
# =============================================================================================


def test_success_raises_user_and_lowers_question_ratings(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    questions = [_question(db_session, module, uaa, n) for n in range(4)]
    session = _completed_session(db_session, user, module, questions, [1.0] * 4)

    detail = apply_session_rating(db_session, session)
    db_session.commit()

    row = db_session.query(UserModuleRating).filter_by(user_id=user.id, module_id=module.id).one()
    # Utilisateur neuf (K=64), 4 réussites attendues à 50 % : +64 × 0.5 = +32.
    assert row.rating == pytest.approx(1032.0)
    assert row.sessions_count == 1
    assert detail["user_before"] == 1000.0 and detail["user_after"] == 1032.0
    for question in questions:
        db_session.refresh(question)
        # Question neuve (K=40) réussie à 50 % attendu : 1000 − 40 × 0.5 = 980.
        assert question.difficulty_rating == pytest.approx(980.0)
        assert question.rating_sample_size == 1
        assert question.times_served == 1 and question.times_correct == 1
        assert question.difficulty_declared is None  # métadonnée jamais modifiée


def test_failure_lowers_user_and_raises_question_ratings(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    questions = [_question(db_session, module, uaa, n, QuestionDifficulty.MEDIUM) for n in range(3)]
    session = _completed_session(db_session, user, module, questions, [0.0] * 3)
    apply_session_rating(db_session, session)
    db_session.commit()

    row = db_session.query(UserModuleRating).filter_by(user_id=user.id).one()
    assert row.rating == pytest.approx(968.0)
    for question in questions:
        assert question.difficulty_rating == pytest.approx(1020.0)
        assert question.times_correct == 0
        assert question.difficulty_declared == QuestionDifficulty.MEDIUM


def test_partial_credit_counts_proportionally(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, 1)
    session = _completed_session(db_session, user, module, [question], [0.5])
    apply_session_rating(db_session, session)
    # Score 0.5 = attendu 0.5 : aucun mouvement, mais tentative comptée, pas réussie.
    assert question.difficulty_rating == pytest.approx(1000.0)
    assert question.rating_sample_size == 1
    assert question.times_correct == 0


def test_blank_answer_penalises_user_but_not_question_difficulty(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    answered, skipped = _question(db_session, module, uaa, 1), _question(db_session, module, uaa, 2)
    session = _completed_session(db_session, user, module, [answered, skipped], [1.0, 0.0], blank=(1,))
    detail = apply_session_rating(db_session, session)

    assert detail["user_delta"] == pytest.approx(0.0)  # (+0.5 − 0.5) / 2
    assert skipped.difficulty_rating is None
    assert skipped.rating_sample_size == 0
    assert skipped.times_served == 1
    assert answered.rating_sample_size == 1


def test_ratings_are_clamped_to_bounds(db_session):
    module, uaa = _module(db_session)
    strong, weak = _user(db_session, "strong@example.invalid"), _user(db_session, "weak@example.invalid")
    db_session.add(UserModuleRating(user_id=strong.id, module_id=module.id, rating=RATING_MAX - 1, sessions_count=0))
    db_session.add(UserModuleRating(user_id=weak.id, module_id=module.id, rating=RATING_MIN + 1, sessions_count=0))
    very_hard = _question(db_session, module, uaa, 1)
    very_hard.difficulty_rating = RATING_MAX - 1
    very_easy = _question(db_session, module, uaa, 2)
    very_easy.difficulty_rating = RATING_MIN + 1
    db_session.commit()

    # Réussite à attendu 50 % : l'utilisateur fort monterait de +32, la question difficile
    # descendrait de 20 ; échec symétrique pour l'utilisateur faible.
    apply_session_rating(db_session, _completed_session(db_session, strong, module, [very_hard], [1.0]))
    apply_session_rating(db_session, _completed_session(db_session, weak, module, [very_easy], [0.0]))
    ratings = {r.user_id: r.rating for r in db_session.query(UserModuleRating).all()}
    assert ratings[strong.id] == RATING_MAX
    assert ratings[weak.id] == RATING_MIN
    assert very_hard.difficulty_rating == pytest.approx(RATING_MAX - 21)
    assert very_easy.difficulty_rating == pytest.approx(RATING_MIN + 21)

    # Bornes atteintes : jamais dépassées, même après des sessions répétées.
    for _ in range(10):
        apply_session_rating(db_session, _completed_session(db_session, strong, module, [very_hard], [1.0]))
        apply_session_rating(db_session, _completed_session(db_session, weak, module, [very_easy], [0.0]))
    for row in db_session.query(UserModuleRating).all():
        assert RATING_MIN <= row.rating <= RATING_MAX
    assert RATING_MIN <= very_hard.difficulty_rating <= RATING_MAX
    assert RATING_MIN <= very_easy.difficulty_rating <= RATING_MAX


def test_progressive_adjustment_converges(db_session):
    """Une question échouée par tout le monde devient progressivement plus difficile, de
    moins en moins vite (K décroissant)."""
    module, uaa = _module(db_session)
    question = _question(db_session, module, uaa, 1)
    deltas = []
    for n in range(6):
        user = _user(db_session, email=f"t45-{n}@example.invalid")
        before = question_rating(question)
        session = _completed_session(db_session, user, module, [question], [0.0])
        apply_session_rating(db_session, session)
        deltas.append(question.difficulty_rating - before)
    assert all(d > 0 for d in deltas)
    assert question.difficulty_rating > 1000.0
    assert deltas == sorted(deltas, reverse=True)


def test_algorithm_is_deterministic(db_session):
    module, uaa = _module(db_session)
    results = []
    for run in range(2):
        user = _user(db_session, email=f"det-{run}@example.invalid")
        questions = [_question(db_session, module, uaa, f"{run}-{n}") for n in range(3)]
        session = _completed_session(db_session, user, module, questions, [1.0, 0.5, 0.0])
        detail = apply_session_rating(db_session, session)
        results.append((detail["user_after"], [q["rating_after"] for q in detail["questions"]]))
    assert results[0] == results[1]


# =============================================================================================
# 3. Une seule fois par questionnaire, par module, jamais rétroactif
# =============================================================================================


def test_rating_is_applied_once_per_session(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, 1)
    session = _completed_session(db_session, user, module, [question], [1.0])
    assert apply_session_rating(db_session, session) is not None
    first = question.difficulty_rating
    assert apply_session_rating(db_session, session) is None
    assert question.difficulty_rating == first
    assert question.rating_sample_size == 1
    assert db_session.query(UserModuleRating).one().sessions_count == 1


def test_non_completed_session_is_not_rated(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, 1)
    session = _completed_session(db_session, user, module, [question], [1.0])
    session.status = SessionStatus.CORRECTION_INCOMPLETE
    assert apply_session_rating(db_session, session) is None
    assert db_session.query(UserModuleRating).count() == 0


def test_rating_is_per_module(db_session):
    module_a, uaa_a = _module(db_session, "MA")
    module_b, _ = _module(db_session, "MB")
    user = _user(db_session)
    session = _completed_session(db_session, user, module_a, [_question(db_session, module_a, uaa_a, 1)], [1.0])
    apply_session_rating(db_session, session)
    db_session.commit()
    rows = db_session.query(UserModuleRating).filter_by(user_id=user.id).all()
    assert [r.module_id for r in rows] == [module_a.id]
    assert module_b.id not in {r.module_id for r in rows}


def test_session_score_is_never_modified(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    session = _completed_session(db_session, user, module, [_question(db_session, module, uaa, 1)], [1.0])
    apply_session_rating(db_session, session)
    assert session.score == 1.0
    assert session.parameters_json["severity"] == 3  # clé existante conservée
    assert session.parameters_json["rating"]["algorithm"] == "elo-v1"


def test_async_correction_applies_rating_on_completion(db_session, monkeypatch):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, 1)
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.ADAPTIVE, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    sq = SessionQuestion(session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0)
    db_session.add(sq)
    db_session.flush()
    db_session.add(SessionAnswer(session_question_id=sq.id, answer_json={"text": "Une réponse."}))
    db_session.commit()

    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=FakeAIProvider())
    db_session.refresh(session)

    assert session.status == SessionStatus.COMPLETED
    assert "rating" in session.parameters_json
    row = db_session.query(UserModuleRating).filter_by(user_id=user.id, module_id=module.id).one()
    assert row.sessions_count == 1
    assert question.rating_sample_size == 1


# =============================================================================================
# 4. Sélection adaptative
# =============================================================================================


def test_order_by_proximity_never_excludes_and_prefers_close_ratings(db_session):
    module, uaa = _module(db_session)
    questions = []
    for n, rating in enumerate([600, 1300, 1010, 900, 1500]):
        q = _question(db_session, module, uaa, n)
        q.difficulty_rating = float(rating)
        questions.append(q)
    ordered = order_by_proximity(questions, 1000.0)
    assert sorted(q.id for q in ordered) == sorted(q.id for q in questions)
    assert [q.difficulty_rating for q in ordered][:2] == [1010.0, 900.0]
    assert ordered[-1].difficulty_rating in (600.0, 1500.0)


def test_compose_selection_adaptive_prefers_band_then_completes(db_session):
    module, uaa = _module(db_session)
    near, far = [], []
    for n in range(6):
        q = _question(db_session, module, uaa, f"near-{n}")
        q.difficulty_rating = 1200.0 + n
        near.append(q)
        q = _question(db_session, module, uaa, f"far-{n}")
        q.difficulty_rating = 700.0
        far.append(q)
    random.seed(45)
    pool = far + near
    selected = compose_selection(pool, 4, difficulty=SessionDifficultyRequest.ADAPTIVE, target_rating=1200.0)
    assert all(abs(q.difficulty_rating - 1200.0) <= ADAPTIVE_BAND for q in selected)
    # Jamais de session raccourcie : complète avec le reste si la bande ne suffit pas.
    selected = compose_selection(pool, 10, difficulty=SessionDifficultyRequest.ADAPTIVE, target_rating=1200.0)
    assert len(selected) == 10
    # Sans niveau connu : comportement inchangé (aucune préférence).
    random.seed(1)
    a = compose_selection(list(pool), 5, difficulty=SessionDifficultyRequest.ADAPTIVE)
    random.seed(1)
    b = compose_selection(list(pool), 5, difficulty=None)
    assert [q.id for q in a] == [q.id for q in b]


def test_start_session_adaptive_uses_module_rating(db_session):
    from app.v1.session_service import start_session

    module, uaa = _module(db_session)
    user = _user(db_session)
    db_session.add(UserModuleRating(user_id=user.id, module_id=module.id, rating=1300.0, sessions_count=4))
    hard_ids = set()
    for n in range(12):
        q = _question(db_session, module, uaa, f"easy-{n}", QuestionDifficulty.EASY)
        q = _question(db_session, module, uaa, f"hard-{n}", QuestionDifficulty.HARD)
        q.difficulty_rating = 1280.0
        hard_ids.add(q.id)
    db_session.commit()

    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code=None,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.ADAPTIVE,
        provider=FakeAIProvider(), question_count=10,
    )
    served = {sq.question_version.question_id for sq in session.session_questions}
    assert len(served) == 10
    assert served <= hard_ids
    assert session.difficulty_requested == SessionDifficultyRequest.ADAPTIVE


# =============================================================================================
# 5. Parcours HTTP : option « Adaptatif » réelle, niveau affiché, évolution au résultat
# =============================================================================================


def test_http_adaptive_flow_shows_level_and_rating_change(client, db_session, monkeypatch):
    from tests.test_ticket88_async_correction_jobs import (
        _csrf,
        _patch_fake_provider,
        _register_and_login,
        _resolve_build_job_url,
        _seed_mc01,
    )

    ampcr, _ = _seed_mc01(db_session)
    fake = _patch_fake_provider(monkeypatch)
    _register_and_login(client, email="ticket45-http@example.test")

    r = client.get("/uaa/ampcr-mc01/practice")
    assert r.status_code == 200
    assert 'value="adaptive"' in r.text
    assert "bientôt disponible" not in r.text
    assert 'id="module-rating"' in r.text and "<strong>1000</strong>" in r.text

    token = _csrf(r.text)
    r = client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "adaptive"},
        follow_redirects=False,
    )
    session_url = _resolve_build_job_url(db_session, r.headers["location"])
    session_id = int(session_url.rstrip("/").split("/")[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.ADAPTIVE

    r = client.get(session_url)
    token = _csrf(r.text)
    r = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": 3}, follow_redirects=False)
    assert r.status_code == 303
    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=fake)

    r = client.get(session_url)
    assert r.status_code == 200
    assert 'id="module-rating-change"' in r.text
    user_id = db_session.get(QuestionnaireSession, session_id).user_id
    row = db_session.query(UserModuleRating).filter_by(user_id=user_id, module_id=ampcr.id).one()
    assert row.sessions_count == 1
    rated = db_session.get(QuestionnaireSession, session_id).parameters_json["rating"]["questions"]
    assert len(rated) == 10  # y compris les questions laissées vides (créées à la correction)

    r = client.get("/uaa/ampcr-mc01/practice")
    assert "1 questionnaire terminé" in r.text

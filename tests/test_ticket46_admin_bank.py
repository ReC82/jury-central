"""Ticket #46 — Admin V1 : banque de questions, génération, signalements et usage IA.
Aucun appel IA réel : `FakeAIProvider` uniquement."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.models import UAA, Module, Subject
from app.v1.ai_usage import KIND_CORRECTION, UsageTrackingProvider, estimate_cost, record_ai_usage
from app.v1.bank import select_bank_questions
from app.v1.bank_admin import (
    BankAdminError,
    QuestionFilters,
    edit_question_content,
    module_bank_stats,
    search_questions,
    set_question_status,
)
from app.v1.feedback import create_question_feedback
from app.v1.generation_control import is_generation_paused, set_generation_status
from app.v1.models import (
    AIUsage,
    AIUsageEvent,
    AnswerCorrectionStatus,
    ContentStatus,
    FeedbackType,
    GenerationSource,
    ModuleGenerationStatus,
    Question,
    QuestionFeedback,
    QuestionnaireSession,
    QuestionVersion,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.session_service import (
    claim_next_pending_correction_job,
    enqueue_correction,
    run_correction_job,
    start_session,
)

# =============================================================================================
# Helpers
# =============================================================================================


def _module(db, code="M46"):
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


def _user(db, email="t46@example.invalid"):
    user = User(email=email, password_hash="x", display_name="t46")
    db.add(user)
    db.commit()
    return user


def _question(db, module, uaa, prompt, *, source=GenerationSource.MANUAL, question_type="short_answer"):
    question = create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type=question_type,
        content_json={"prompt": prompt, "rubric": "Grille."}, generation_source=source,
    )
    db.commit()
    return question


def _session_with(db, user, module, questions, *, status=SessionStatus.COMPLETED):
    session = QuestionnaireSession(
        user_id=user.id, mode=SessionMode.PRACTICE, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=status,
        question_count=len(questions),
    )
    db.add(session)
    db.flush()
    for position, question in enumerate(questions, start=1):
        sq = SessionQuestion(
            session_id=session.id, question_version_id=question.current_version_id,
            position=position, points_max=1.0,
        )
        db.add(sq)
        db.flush()
        db.add(SessionAnswer(
            session_question_id=sq.id, answer_json={"text": "réponse"},
            correction_status=AnswerCorrectionStatus.CORRECTED if status == SessionStatus.COMPLETED
            else AnswerCorrectionStatus.PENDING,
            points_awarded=1.0 if status == SessionStatus.COMPLETED else None,
        ))
    db.commit()
    db.refresh(session)
    return session


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


class _TokenFakeProvider(FakeAIProvider):
    """Fournisseur factice qui déclare des jetons consommés, comme OpenAIProvider."""

    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self):
        super().__init__()
        self._pending = {"input_tokens": 0, "output_tokens": 0}

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        self._pending["input_tokens"] += 1000
        self._pending["output_tokens"] += 200
        return super().correct_semantic_batch(questions, answers, severity, contexts)

    def consume_usage(self):
        usage, self._pending = self._pending, {"input_tokens": 0, "output_tokens": 0}
        return usage


# =============================================================================================
# 1. Statistiques par module
# =============================================================================================


def test_module_stats_are_computed_from_the_bank(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    q1 = _question(db_session, module, uaa, "Q1 réseau ?", source=GenerationSource.AI_GENERATED)
    q2 = _question(db_session, module, uaa, "Q2 mémoire ?")
    q3 = _question(db_session, module, uaa, "Q3 disque ?")
    q4 = _question(db_session, module, uaa, "Q4 archivée ?")
    q1.difficulty_rating, q2.difficulty_rating, q3.difficulty_rating = 900.0, 1000.0, 1200.0
    q1.times_served, q1.times_correct = 4, 1
    q2.times_served, q2.times_correct = 4, 3
    q3.status = ContentStatus.REVIEW_NEEDED
    q4.status = ContentStatus.ARCHIVED
    db_session.commit()
    s1 = _session_with(db_session, user, module, [q1, q2])
    _session_with(db_session, user, module, [q1])
    create_question_feedback(
        db_session, user_id=user.id, session_question=s1.session_questions[1],
        feedback_type=FeedbackType.AMBIGUOUS, comment="Pas clair",
    )
    db_session.add(AIUsageEvent(module_id=module.id, kind="generation", calls=2, generated_questions=10,
                                input_tokens=5000, output_tokens=1000, estimated_cost=0.02))
    db_session.commit()

    stats = next(s for s in module_bank_stats(db_session) if s.module.id == module.id)
    assert stats.total == 4
    assert stats.by_status[ContentStatus.ACTIVE] == 2
    assert stats.by_status[ContentStatus.ARCHIVED] == 1
    assert (stats.rating_min, stats.rating_median, stats.rating_max) == (900.0, 1000.0, 1200.0)
    assert stats.attempts == 8 and stats.successes == 4 and stats.success_rate == 50.0
    assert stats.generated == 1 and stats.manual == 3
    assert stats.reused == 1  # q1 servie dans 2 sessions
    assert stats.servings == 3
    assert stats.signaled == 1  # q2, signalement ouvert
    assert stats.to_review == 2  # q2 (signalement) + q3 (à revoir)
    assert stats.generation_status == ModuleGenerationStatus.ACTIVE
    assert stats.usage_total.calls == 2 and stats.usage_total.estimated_cost == 0.02
    assert stats.usage_month.generated_questions == 10


# =============================================================================================
# 2. Recherche et filtres
# =============================================================================================


def test_search_filters_module_type_status_rating_text_and_review(db_session):
    module, uaa = _module(db_session)
    other, other_uaa = _module(db_session, code="X46")
    q1 = _question(db_session, module, uaa, "Quelle est la fréquence d'un processeur ?")
    q2 = _question(db_session, module, uaa, "Ordonne les étapes du démarrage.")
    q3 = _question(db_session, other, other_uaa, "Question d'un autre module.")
    q1.difficulty_rating = 1100.0
    q2.status = ContentStatus.ARCHIVED
    db_session.commit()

    def ids(**kwargs):
        items, total = search_questions(db_session, QuestionFilters(**kwargs))
        assert total == len(items)
        return {item.id for item in items}

    assert ids(module_id=module.id) == {q1.id, q2.id}
    assert ids(status=ContentStatus.ARCHIVED) == {q2.id}
    assert ids(question_type="short_answer", module_id=other.id) == {q3.id}
    assert ids(rating_min=1050) == {q1.id}
    assert ids(rating_max=1000) == set()
    assert ids(text="fréquence") == {q1.id}  # accent : JSON échappé en base
    assert ids(text=str(q3.id)) == {q3.id}
    assert ids(to_review=True) == set()
    set_question_status(db_session, q3, ContentStatus.FLAGGED)
    db_session.commit()
    assert ids(to_review=True) == {q3.id}


# =============================================================================================
# 3. Versionnement et archivage
# =============================================================================================


def test_edit_creates_new_version_and_old_session_keeps_old_version(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, "Ancienne formulation ?")
    old_version_id = question.current_version_id
    session = _session_with(db_session, user, module, [question])

    new_version = edit_question_content(
        db_session, question, '{"prompt": "Nouvelle formulation ?", "rubric": "Grille."}'
    )
    db_session.commit()

    assert new_version.version == 2
    assert question.current_version_id == new_version.id
    assert db_session.get(QuestionVersion, old_version_id).content_json["prompt"] == "Ancienne formulation ?"
    db_session.refresh(session)
    assert session.session_questions[0].question_version_id == old_version_id


def test_edit_rejects_invalid_or_identical_content(db_session):
    module, uaa = _module(db_session)
    question = _question(db_session, module, uaa, "Question ?")
    for raw in ("{pas du json", "[1, 2]", '{"prompt": "Question ?", "rubric": "Grille."}', '{"rubric": "x"}'):
        try:
            edit_question_content(db_session, question, raw)
        except BankAdminError:
            db_session.rollback()
        else:  # pragma: no cover
            raise AssertionError(f"contenu accepté à tort : {raw}")
    assert db_session.query(QuestionVersion).filter_by(question_id=question.id).count() == 1


def test_archived_question_is_never_selected_and_can_be_reactivated(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, "Question archivable ?")
    set_question_status(db_session, question, ContentStatus.ARCHIVED)
    db_session.commit()
    assert select_bank_questions(db_session, user_id=user.id, module_id=module.id, uaa_id=uaa.id, limit=10) == []
    set_question_status(db_session, question, ContentStatus.ACTIVE)
    db_session.commit()
    assert [q.id for q in select_bank_questions(
        db_session, user_id=user.id, module_id=module.id, uaa_id=uaa.id, limit=10
    )] == [question.id]
    assert db_session.get(Question, question.id) is not None


# =============================================================================================
# 4. Génération ACTIVE / PAUSED
# =============================================================================================


def test_paused_generation_never_calls_ai_and_uses_bank(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    _question(db_session, module, uaa, "Seule question de la banque ?")
    set_generation_status(db_session, module.id, ModuleGenerationStatus.PAUSED)
    db_session.commit()
    assert is_generation_paused(db_session, module.id)

    fake = FakeAIProvider()
    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code=uaa.code,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, provider=fake,
        question_count=5,
    )
    assert fake.questionnaire_calls == []
    assert len(session.session_questions) == 1

    set_generation_status(db_session, module.id, ModuleGenerationStatus.ACTIVE)
    db_session.commit()
    start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code=uaa.code,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM, provider=fake,
        question_count=5,
    )
    assert len(fake.questionnaire_calls) >= 1


# =============================================================================================
# 5. Usage IA
# =============================================================================================


def test_openai_provider_accumulates_and_resets_token_usage():
    provider = OpenAIProvider(api_key="sk-test-never-used", model="m", timeout_seconds=1)
    provider._record_usage({"usage": {"input_tokens": 120, "output_tokens": 30}})
    provider._record_usage({"usage": {"input_tokens": 80, "output_tokens": 20}})
    provider._record_usage({"no_usage": True})
    assert provider.consume_usage() == {"input_tokens": 200, "output_tokens": 50}
    assert provider.consume_usage() == {"input_tokens": 0, "output_tokens": 0}


def test_record_ai_usage_writes_event_and_monthly_aggregate(db_session):
    module, _ = _module(db_session)
    user = _user(db_session)
    tracker = UsageTrackingProvider(_TokenFakeProvider())
    assert record_ai_usage(db_session, tracker, kind=KIND_CORRECTION, module_id=module.id, user_id=user.id) is None

    tracker.correct_semantic_batch([], {}, "standard", [])
    event = record_ai_usage(db_session, tracker, kind=KIND_CORRECTION, module_id=module.id, user_id=user.id)
    db_session.commit()
    assert event.calls == 1 and event.input_tokens == 1000 and event.output_tokens == 200
    assert event.estimated_cost == estimate_cost(1000, 200) > 0
    aggregate = db_session.query(AIUsage).filter_by(user_id=user.id).one()
    assert aggregate.input_tokens == 1000 and aggregate.model == "fake-model"


def test_correction_job_records_ai_usage_for_module(db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, "Explique le rôle de la RAM.")
    session = _session_with(db_session, user, module, [question], status=SessionStatus.IN_PROGRESS)

    enqueue_correction(db_session, session=session, severity_ui=3)
    job = claim_next_pending_correction_job(db_session)
    run_correction_job(db_session, job=job, provider=_TokenFakeProvider())

    event = db_session.query(AIUsageEvent).one()
    assert event.module_id == module.id and event.user_id == user.id and event.session_id == session.id
    assert event.kind == KIND_CORRECTION and event.ai_corrections == 1 and event.input_tokens == 1000


# =============================================================================================
# 6. Signalements utilisateur (HTTP)
# =============================================================================================


def _register_and_login(client, email):
    r = client.get("/register")
    client.post("/register", data={
        "csrf_token": _csrf(r.text), "email": email, "password": "test-password-1234",
        "password_confirm": "test-password-1234", "display_name": "T46",
    })
    return client


def test_user_can_report_a_question_from_results(client, db_session):
    module, uaa = _module(db_session)
    question = _question(db_session, module, uaa, "Question à signaler ?")
    _register_and_login(client, "t46-report@example.test")
    user = db_session.query(User).filter_by(email="t46-report@example.test").one()
    session = _session_with(db_session, user, module, [question])

    r = client.get(f"/sessions/{session.id}")
    assert r.status_code == 200
    assert "Signaler un problème sur cette question" in r.text
    assert 'value="answer_disputed"' in r.text
    token = _csrf(r.text)

    r = client.post(f"/sessions/{session.id}/questions/1/feedback",
                    data={"feedback_type": "answer_disputed", "comment": "Ma réponse était juste."},
                    follow_redirects=False)
    assert r.status_code == 400  # pas de CSRF

    for comment in ("Ma réponse était juste.", "Précision ajoutée."):
        r = client.post(f"/sessions/{session.id}/questions/1/feedback",
                        data={"feedback_type": "answer_disputed", "comment": comment, "csrf_token": token},
                        follow_redirects=False)
        assert r.status_code == 303
    feedback = db_session.query(QuestionFeedback).one()  # pas de doublon
    db_session.refresh(feedback)
    assert feedback.comment == "Précision ajoutée."
    assert feedback.question_version_id == question.current_version_id
    assert feedback.session_answer_id == session.session_questions[0].answer.id
    assert db_session.get(Question, question.id).status == ContentStatus.ACTIVE  # jamais automatique

    r = client.get(r.headers["location"])
    assert "ton signalement a été transmis" in r.text


def test_report_rejected_on_in_progress_or_foreign_session(client, db_session):
    module, uaa = _module(db_session)
    question = _question(db_session, module, uaa, "Question ?")
    other = _user(db_session, email="t46-other@example.invalid")
    foreign = _session_with(db_session, other, module, [question])
    _register_and_login(client, "t46-me@example.test")
    me = db_session.query(User).filter_by(email="t46-me@example.test").one()
    running = _session_with(db_session, me, module, [question], status=SessionStatus.IN_PROGRESS)
    token = _csrf(client.get("/").text)

    data = {"feedback_type": "incorrect", "csrf_token": token}
    assert client.post(f"/sessions/{foreign.id}/questions/1/feedback", data=data).status_code == 404
    assert client.post(f"/sessions/{running.id}/questions/1/feedback", data=data).status_code == 409
    assert db_session.query(QuestionFeedback).count() == 0


# =============================================================================================
# 7. Pages admin (HTTP)
# =============================================================================================


def test_admin_bank_pages_require_admin(client):
    for url in ("/admin/bank", "/admin/bank/questions", "/admin/bank/feedback"):
        r = client.get(url, follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"] == "/admin/login"


def test_admin_bank_full_flow(admin_client, db_session):
    module, uaa = _module(db_session)
    user = _user(db_session)
    question = _question(db_session, module, uaa, "Quelle est la capacité du disque ?")
    session = _session_with(db_session, user, module, [question])
    feedback = create_question_feedback(
        db_session, user_id=user.id, session_question=session.session_questions[0],
        feedback_type=FeedbackType.INCORRECT, comment="La correction est fausse.",
    )
    db_session.commit()

    r = admin_client.get("/admin/dashboard")
    assert 'href="/admin/bank"' in r.text
    r = admin_client.get("/admin/bank")
    assert r.status_code == 200 and "M46" in r.text and "Génération ACTIVE" in r.text
    assert "sk-" not in r.text
    token = _csrf(r.text)

    r = admin_client.post(f"/admin/bank/modules/{module.id}/generation",
                          data={"generation_status": "paused", "csrf_token": token}, follow_redirects=False)
    assert r.status_code == 303 and is_generation_paused(db_session, module.id)

    r = admin_client.get(f"/admin/bank/questions?module_id={module.id}&to_review=1")
    assert r.status_code == 200 and f"#{question.id}" in r.text
    r = admin_client.get("/admin/bank/feedback")
    assert "La correction est fausse." in r.text

    r = admin_client.get(f"/admin/bank/questions/{question.id}")
    assert r.status_code == 200 and "Enregistrer une nouvelle version" in r.text

    r = admin_client.post(f"/admin/bank/questions/{question.id}/edit",
                          data={"content_json": "{oups", "csrf_token": token})
    assert r.status_code == 400 and "JSON invalide" in r.text
    r = admin_client.post(
        f"/admin/bank/questions/{question.id}/edit",
        data={"content_json": '{"prompt": "Capacité du disque en Go ?", "rubric": "Grille."}', "csrf_token": token},
        follow_redirects=False,
    )
    assert r.status_code == 303
    db_session.expire_all()
    assert db_session.get(Question, question.id).current_version.version == 2

    r = admin_client.post(f"/admin/bank/questions/{question.id}/status",
                          data={"status": "invalid", "csrf_token": token}, follow_redirects=False)
    assert r.status_code == 303
    db_session.expire_all()
    assert db_session.get(Question, question.id).status == ContentStatus.INVALID

    r = admin_client.post(f"/admin/bank/feedback/{feedback.id}/resolve",
                          data={"resolved": "1", "csrf_token": token}, follow_redirects=False)
    assert r.status_code == 303
    db_session.expire_all()
    assert db_session.get(QuestionFeedback, feedback.id).resolved_at is not None

    r = admin_client.get(f"/admin/bank/questions/{question.id}?done=edited")
    assert "Nouvelle version créée" in r.text and "v2 (courante)" in r.text

    r = admin_client.post(f"/admin/bank/questions/{question.id}/status",
                          data={"status": "active"}, follow_redirects=False)
    assert r.status_code == 400  # CSRF manquant


def test_admin_regenerate_variant_creates_review_needed_question(admin_client, db_session, monkeypatch):
    from tests.test_ticket88_async_correction_jobs import _seed_mc01

    ampcr, mc01 = _seed_mc01(db_session)
    original = (
        db_session.query(Question)
        .join(QuestionVersion, Question.current_version_id == QuestionVersion.id)
        .filter(Question.uaa_id == mc01.id, QuestionVersion.question_type == "classification")
        .first()
    )
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_admin_bank.get_ai_provider", lambda: fake)
    before = db_session.query(Question).filter_by(uaa_id=mc01.id).count()

    r = admin_client.get(f"/admin/bank/questions/{original.id}")
    assert "Générer une variante" in r.text
    r = admin_client.post(f"/admin/bank/questions/{original.id}/variant",
                          data={"csrf_token": _csrf(r.text)}, follow_redirects=False)
    assert r.status_code == 303, r.text
    assert len(fake.questionnaire_calls) == 1
    assert fake.questionnaire_calls[0].allowed_types == ("classification",)

    db_session.expire_all()
    assert db_session.query(Question).filter_by(uaa_id=mc01.id).count() == before + 1
    variant_id = int(r.headers["location"].rsplit("variant=", 1)[1])
    variant = db_session.get(Question, variant_id)
    assert variant.status == ContentStatus.REVIEW_NEEDED
    assert variant.generation_source == GenerationSource.AI_GENERATED
    assert db_session.get(Question, original.id).current_version.version == original.current_version.version
    assert db_session.query(AIUsageEvent).filter_by(kind="admin_variant", module_id=ampcr.id).count() == 1

    set_generation_status(db_session, ampcr.id, ModuleGenerationStatus.PAUSED)
    db_session.commit()
    r = admin_client.get(f"/admin/bank/questions/{original.id}")
    assert "Génération en pause pour ce module." in r.text
    r = admin_client.post(f"/admin/bank/questions/{original.id}/variant", data={"csrf_token": _csrf(r.text)})
    assert r.status_code == 400 and len(fake.questionnaire_calls) == 1


def test_variant_refused_for_hand_authored_fse_bank(admin_client, db_session):
    from app.seed import seed

    seed()
    fse01 = db_session.query(UAA).filter_by(code="FSE01").first()
    if fse01 is None:  # pragma: no cover — dépend du seed
        return
    from app.v1.fse_bank import import_fse01_to_bank

    import_fse01_to_bank(db_session, fse01.module, fse01)
    db_session.commit()
    question = db_session.query(Question).filter_by(uaa_id=fse01.id).first()
    r = admin_client.get(f"/admin/bank/questions/{question.id}")
    assert "banque rédigée à la main" in r.text

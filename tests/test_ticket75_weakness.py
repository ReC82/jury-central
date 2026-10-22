"""Ticket #75 — points faibles : profil, renforcement ciblé à correction immédiate et
examen ciblé. Aucune IA : banques construites en base, correction locale déterministe."""

import re
from datetime import UTC, datetime, timedelta

from app.ai.fake_provider import FakeAIProvider
from app.models import UAA, Module, Subject
from app.v1.models import (
    AnswerCorrectionStatus,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    create_question,
)
from app.v1.parcours import user_uaa_progress
from app.v1.session_service import (
    WEAKNESS_EXAM_SCOPE,
    get_in_progress_session,
    get_owned_session,
    list_user_sessions,
    simulate_severity_comparison,
)
from app.v1.weakness import (
    Observation,
    resolve_targets,
    score_observations,
    start_weakness_exam,
    weakness_profile,
)

EXPLANATION = "Explication-secrete-75"
_WORDS = [
    "Routeur", "Commutateur", "Pare-feu", "Adresse", "Processeur", "Mémoire", "Câble",
    "Serveur", "Connecteur", "Partition", "Clavier", "Imprimante", "Hyperlien", "Registre",
    "Pilote", "Tableau", "Budget", "Slogan", "Synonyme", "Commune", "Parlement", "Région",
]


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def _obs(ratio, *, difficulty="medium", mode=SessionMode.PRACTICE, n=0):
    return Observation(
        session_id=n, session_question_id=n, mode=mode, ratio=ratio, difficulty=difficulty,
        at=datetime(2026, 10, 1, tzinfo=UTC) + timedelta(minutes=n),
    )


# --- 1. Calcul du score (unité) ---------------------------------------------------------


def test_error_creates_weakness_and_repeated_errors_increase_it():
    history = score_observations([_obs(0, n=1), _obs(0, n=2), _obs(0, n=3)])
    assert history[0] > 0
    assert history[0] < history[1] < history[2]


def test_partial_answer_increases_less_than_total_error():
    assert score_observations([_obs(0.5)])[-1] < score_observations([_obs(0)])[-1]
    assert score_observations([_obs(0.5)])[-1] > 0


def test_single_success_does_not_reset_and_repeated_successes_reduce():
    base = [_obs(0, n=1), _obs(0, n=2)]
    after_one = score_observations([*base, _obs(1, n=3)])
    assert 0 < after_one[-1] < after_one[-2]
    assert after_one[-1] > 40  # toujours un point faible après une seule réussite
    after_four = score_observations([*base, *[_obs(1, n=k) for k in range(3, 7)]])
    assert after_four[-1] < 20
    assert after_four[-1] < after_one[-1]


def test_easy_question_error_weighs_more_than_hard_one():
    easy = score_observations([_obs(0, difficulty="easy")])[-1]
    hard = score_observations([_obs(0, difficulty="hard")])[-1]
    assert easy > hard


# --- Données de test ----------------------------------------------------------------------


def _content(db):
    subject = Subject(name="Informatique", slug="informatique")
    db.add(subject)
    db.flush()
    module = Module(code="AMPCR", slug="ampcr", subject_id=subject.id)
    db.add(module)
    db.flush()
    uaas = []
    for position, code in enumerate(("MC15", "MC17", "MC20"), start=1):
        uaa = UAA(code=code, title=f"Cours {code}", slug=f"t75-{code.lower()}", position=position,
                  is_published=True, module_id=module.id)
        db.add(uaa)
        uaas.append(uaa)
    db.flush()
    questions = {}
    for index, uaa in enumerate(uaas):
        questions[uaa.code] = [
            create_question(
                db, module_id=module.id, uaa_id=uaa.id, question_type="multiple_choice",
                generation_source="manual", difficulty_declared=QuestionDifficulty.MEDIUM,
                content_json={
                    "prompt": f"{_WORDS[(n * 5 + index * 7) % len(_WORDS)]} "
                              f"{_WORDS[(n * 3 + index + 11) % len(_WORDS)]} {uaa.code} cas {n} ?",
                    "options": [
                        {"option_id": "a", "label": f"Juste {uaa.code} {n}"},
                        {"option_id": "b", "label": f"Faux {uaa.code} {n}"},
                    ],
                    "correct_option_ids": ["a"],
                    "explanation": EXPLANATION,
                },
            )
            for n in range(1, 9)
        ]
    db.commit()
    return module, uaas, questions


def _make_user(db, email):
    user = User(email=email, password_hash="x", display_name=email)
    db.add(user)
    db.commit()
    return user


def _test_user(db):
    return db.query(User).filter_by(email="eleve-test@example.test").one()


def _completed_session(db, user, module, answers, *, mode=SessionMode.PRACTICE, when=None):
    """`answers` : liste (question, ratio). Session terminée, réponses corrigées."""
    when = when or datetime.now(UTC) - timedelta(hours=1)
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=module.id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.COMPLETED,
        question_count=len(answers), completed_at=when,
    )
    db.add(session)
    db.flush()
    for position, (question, ratio) in enumerate(answers, start=1):
        sq = SessionQuestion(session_id=session.id, question_version_id=question.current_version_id,
                             position=position, points_max=1.0)
        db.add(sq)
        db.flush()
        db.add(SessionAnswer(
            session_question_id=sq.id, answer_json={"selected_option_ids": ["a" if ratio else "b"]},
            answered_at=when + timedelta(seconds=position), correction_status=AnswerCorrectionStatus.CORRECTED,
            points_awarded=ratio, feedback_json={"correct": ratio >= 1},
        ))
    db.commit()
    return session


def _entry(entries, code):
    return next(e for e in entries if e.uaa.code == code)


# --- 2. Profil depuis la base ---------------------------------------------------------------


def test_profile_ranks_courses_and_isolates_users(db_session):
    module, _, qs = _content(db_session)
    alice = _make_user(db_session, "alice@example.test")
    bob = _make_user(db_session, "bob@example.test")
    _completed_session(db_session, alice, module, [
        (qs["MC17"][0], 0), (qs["MC17"][1], 0), (qs["MC15"][0], 0.5), (qs["MC20"][0], 1),
    ])
    _completed_session(db_session, bob, module, [(qs["MC20"][1], 0), (qs["MC20"][2], 0)])

    entries = weakness_profile(db_session, user_id=alice.id)
    assert [e.uaa.code for e in entries] == ["MC17", "MC15", "MC20"]
    assert _entry(entries, "MC17").score > _entry(entries, "MC15").score > _entry(entries, "MC20").score
    assert _entry(entries, "MC20").level_key == "fort"
    assert _entry(entries, "MC17").low_data  # 2 réponses seulement
    # Bob n'influence jamais le profil d'Alice, et inversement.
    bob_entries = weakness_profile(db_session, user_id=bob.id)
    assert [e.uaa.code for e in bob_entries] == ["MC20"]
    assert bob_entries[0].answers == 2


def test_quiz_in_progress_practice_and_failed_answers_are_not_counted(db_session):
    module, _, qs = _content(db_session)
    user = _make_user(db_session, "c@example.test")
    _completed_session(db_session, user, module, [(qs["MC15"][0], 0)], mode=SessionMode.QUIZ)
    unfinished = _completed_session(db_session, user, module, [(qs["MC17"][0], 0)])
    unfinished.status = SessionStatus.IN_PROGRESS
    failed = _completed_session(db_session, user, module, [(qs["MC20"][0], 0)])
    failed.session_questions[0].answer.correction_status = AnswerCorrectionStatus.FAILED
    db_session.commit()
    assert weakness_profile(db_session, user_id=user.id) == []


def test_regrading_comparison_never_double_counts(db_session):
    module, _, qs = _content(db_session)
    user = _make_user(db_session, "d@example.test")
    session = _completed_session(db_session, user, module, [(qs["MC17"][0], 0), (qs["MC17"][1], 1)])
    before = weakness_profile(db_session, user_id=user.id)
    for severity in (1, 5):
        simulate_severity_comparison(db_session, session=session, provider=FakeAIProvider(), severity_ui=severity)
    after = weakness_profile(db_session, user_id=user.id)
    assert [(e.key, e.answers, e.score) for e in after] == [(e.key, e.answers, e.score) for e in before]
    assert after[0].answers == 2


def test_trend_improves_after_later_successes(db_session):
    module, _, qs = _content(db_session)
    user = _make_user(db_session, "e@example.test")
    first = datetime(2026, 10, 1, tzinfo=UTC)
    _completed_session(db_session, user, module, [(qs["MC17"][0], 0), (qs["MC17"][1], 0)], when=first)
    assert weakness_profile(db_session, user_id=user.id)[0].trend == "nouveau"
    _completed_session(db_session, user, module, [(qs["MC17"][2], 1), (qs["MC17"][3], 1)],
                       when=first + timedelta(days=2))
    entry = weakness_profile(db_session, user_id=user.id)[0]
    assert entry.trend == "amelioration"
    assert entry.last_error_at.date() == first.date()


def test_mix_targets_the_strongest_weaknesses(db_session):
    module, _, qs = _content(db_session)
    user = _make_user(db_session, "f@example.test")
    _completed_session(db_session, user, module, [
        (qs["MC17"][0], 0), (qs["MC17"][1], 0), (qs["MC17"][2], 0),
        (qs["MC15"][0], 0), (qs["MC20"][0], 1),
    ])
    kind, targets = resolve_targets(weakness_profile(db_session, user_id=user.id))
    assert kind == "mix"
    assert [t.uaa.code for t in targets] == ["MC17", "MC15"]  # MC20 « Fort » exclu


# --- 3. Renforcement ciblé (HTTP) ------------------------------------------------------------


def _start_reinforcement(client, **fields):
    token = _csrf(client.get("/points-faibles").text)
    response = client.post("/points-faibles/renforcer", data={"csrf_token": token, **fields},
                           follow_redirects=False)
    assert response.status_code == 303, response.text
    match = re.match(r"/renforcement/(\d+)$", response.headers["location"])
    assert match, response.headers["location"]
    return int(match.group(1))


def _validate(client, session_id, position, option_id):
    token = _csrf(client.get(f"/renforcement/{session_id}").text)
    return client.post(f"/renforcement/{session_id}/valider",
                       data={"csrf_token": token, "position": str(position), "option_id": option_id},
                       follow_redirects=False)


def test_weakness_page_requires_login(client):
    response = client.get("/points-faibles", follow_redirects=False)
    assert response.status_code in (302, 303, 401)


def test_weakness_page_lists_levels_and_actions(authenticated_client, db_session):
    module, _, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [(qs["MC17"][0], 0), (qs["MC17"][1], 0), (qs["MC20"][0], 1)])
    html = authenticated_client.get("/points-faibles").text
    assert "Mes points faibles" in html
    assert "MC17 — Cours MC17" in html and "Prioritaire" in html
    assert "MC20 — Cours MC20" in html and "Fort" in html
    assert "peu de données" in html
    assert "Travailler mes points faibles" in html
    assert 'value="u' in html  # action « S'entraîner sur ce point »
    assert "/uaa/t75-mc17" in html  # « Relire le cours »
    assert "Examen ciblé points faibles" in html


def test_reinforcement_immediate_correction_and_variant_after_error(authenticated_client, db_session):
    module, uaas, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [(qs["MC17"][0], 0), (qs["MC17"][1], 0)])
    mc17 = next(u for u in uaas if u.code == "MC17")
    session_id = _start_reinforcement(authenticated_client, cible=f"u{mc17.id}")

    page = authenticated_client.get(f"/renforcement/{session_id}").text
    assert "Valider ma réponse" in page
    assert EXPLANATION not in page  # jamais de solution avant validation
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.mode == SessionMode.REINFORCEMENT
    initial = session.question_count
    assert initial == 6
    first_question_id = session.session_questions[0].question_version.question_id
    assert all(sq.question_version.question.uaa_id == mc17.id for sq in session.session_questions)

    response = _validate(authenticated_client, session_id, 1, "b")
    assert response.status_code == 303
    feedback = authenticated_client.get(response.headers["location"]).text
    assert EXPLANATION in feedback and "Pas tout à fait" in feedback
    assert "Question suivante" in feedback and "Relire le cours" in feedback
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == initial + 1
    added = max(session.session_questions, key=lambda sq: sq.position)
    assert added.position == initial + 1
    assert added.question_version.question_id != first_question_id
    assert added.question_version.question.uaa_id == mc17.id

    # La réponse validée est verrouillée : une seconde validation ne change rien.
    _validate(authenticated_client, session_id, 1, "a")
    db_session.expire_all()
    assert db_session.get(QuestionnaireSession, session_id).session_questions[0].answer.feedback_json["correct"] is False

    # Une réponse de renforcement alimente immédiatement le profil.
    entry = _entry(weakness_profile(db_session, user_id=user.id), "MC17")
    assert entry.answers == 3


def test_reinforcement_completes_with_summary_and_reduces_weakness(authenticated_client, db_session):
    module, uaas, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [(qs["MC17"][0], 0), (qs["MC17"][1], 0)])
    before = _entry(weakness_profile(db_session, user_id=user.id), "MC17").score
    mc17 = next(u for u in uaas if u.code == "MC17")
    session_id = _start_reinforcement(authenticated_client, cible=f"u{mc17.id}")
    for position in range(1, 7):
        _validate(authenticated_client, session_id, position, "a")
    done = re.sub(r"\s+", " ", authenticated_client.get(f"/renforcement/{session_id}").text)
    assert "Renforcement terminé" in done and "6 bonnes réponses sur 6" in done
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED and session.question_count == 6
    after = _entry(weakness_profile(db_session, user_id=user.id), "MC17")
    assert after.score < before and after.trend == "amelioration"


def test_reinforcement_from_results_page_targets_session_courses(authenticated_client, db_session):
    module, _, qs = _content(db_session)
    user = _test_user(db_session)
    session = _completed_session(db_session, user, module, [(qs["MC15"][0], 0), (qs["MC20"][0], 1)])
    html = authenticated_client.get(f"/sessions/{session.id}").text
    assert "Renforcer ces notions" in html
    session_id = _start_reinforcement(authenticated_client, cours="t75-mc15")
    reinforcement = db_session.get(QuestionnaireSession, session_id)
    assert {sq.question_version.question.uaa.code for sq in reinforcement.session_questions} == {"MC15"}


def test_reinforcement_is_isolated_from_practice_exam_routes(authenticated_client, db_session):
    module, uaas, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [(qs["MC17"][0], 0)])
    session_id = _start_reinforcement(authenticated_client)
    assert get_owned_session(db_session, session_id=session_id, user_id=user.id) is None
    assert session_id not in [s.id for s in list_user_sessions(db_session, user_id=user.id)]
    redirect = authenticated_client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert redirect.headers["location"] == f"/renforcement/{session_id}"
    assert authenticated_client.post(f"/sessions/{session_id}/submit", data={}).status_code in (403, 404)
    # Ni entraînement ni examen blanc dans la progression du parcours.
    mc17 = next(u for u in uaas if u.code == "MC17")
    assert user_uaa_progress(db_session, user).get(mc17.id, {}).get("in_progress_session_id") is None


def test_other_user_cannot_open_reinforcement(authenticated_client, db_session):
    module, _, qs = _content(db_session)
    other = _make_user(db_session, "autre@example.test")
    session = _completed_session(db_session, other, module, [(qs["MC17"][0], 0)])
    session.mode = SessionMode.REINFORCEMENT
    db_session.commit()
    assert authenticated_client.get(f"/renforcement/{session.id}").status_code == 404


# --- 4. Examen ciblé ------------------------------------------------------------------------


def test_weakness_exam_has_no_correction_before_submit_and_only_weak_courses(authenticated_client, db_session):
    module, uaas, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [
        (qs["MC17"][0], 0), (qs["MC17"][1], 0), (qs["MC15"][0], 0), (qs["MC20"][0], 1),
    ])
    token = _csrf(authenticated_client.get("/points-faibles").text)
    response = authenticated_client.post("/points-faibles/examen",
                                         data={"csrf_token": token, "matiere": "AMPCR", "questions": "10"},
                                         follow_redirects=False)
    assert response.status_code == 303
    session_id = int(re.match(r"/sessions/(\d+)$", response.headers["location"]).group(1))
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.mode == SessionMode.EXAM
    assert session.parameters_json["scope"] == WEAKNESS_EXAM_SCOPE
    codes = {sq.question_version.question.uaa.code for sq in session.session_questions}
    assert codes == {"MC17", "MC15"}
    assert session.question_count == 10
    page = authenticated_client.get(f"/sessions/{session_id}").text
    assert EXPLANATION not in page
    # Jamais repris comme l'examen d'un cours ni comme l'examen global.
    for uaa in uaas:
        assert get_in_progress_session(db_session, user_id=user.id, module_id=module.id,
                                       mode=SessionMode.EXAM, uaa_id=uaa.id) is None
    assert get_in_progress_session(db_session, user_id=user.id, module_id=module.id,
                                   mode=SessionMode.EXAM, uaa_id=None) is None
    # Un second clic reprend le même examen.
    again = start_weakness_exam(db_session, user=user, module=module, count=10)
    assert again.id == session_id


def test_weakness_exam_refused_without_active_weakness(authenticated_client, db_session):
    module, _, qs = _content(db_session)
    user = _test_user(db_session)
    _completed_session(db_session, user, module, [(qs["MC20"][0], 1)])
    token = _csrf(authenticated_client.get("/points-faibles").text)
    response = authenticated_client.post("/points-faibles/examen",
                                         data={"csrf_token": token, "matiere": "AMPCR", "questions": "20"},
                                         follow_redirects=False)
    assert response.headers["location"] == "/points-faibles?info=examen"

"""Ticket #137 — quiz ludiques par matière et multi-matières du parcours CESS P.
Aucune IA : banques construites directement en base, correction locale déterministe."""

import re

import pytest

from app.models import UAA, Module, Subject
from app.v1.models import (
    AnswerCorrectionStatus,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    User,
    UserModuleRating,
    create_question,
)
from app.v1.parcours import resolve_keys, user_uaa_progress
from app.v1.quiz_service import (
    build_catalog,
    plan_quiz,
    quiz_results,
    resolve_scope,
    start_quiz,
    validate_quiz_answer,
)

EXPLANATION = "Explication-secrete-137"
_WORDS = [
    "Routeur", "Affiche", "Commutateur", "Argument", "Constitution", "Pare-feu", "Métaphore",
    "Parlement", "Adresse", "Narrateur", "Commune", "Processeur", "Synonyme", "Élection",
    "Mémoire", "Paragraphe", "Syndicat", "Câble", "Ponctuation", "Budget", "Pilote",
    "Registre", "Impôt", "Serveur", "Connecteur", "Fédéralisme", "Partition", "Slogan",
    "Tableau", "Région", "Clavier", "Témoignage", "Ministre", "Imprimante", "Hyperlien",
]


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace("&nbsp;", " ")


def _mc(db, module, uaa, n, *, difficulty=None, explanation=EXPLANATION):
    return create_question(
        db, module_id=module.id, uaa_id=uaa.id, question_type="multiple_choice",
        generation_source="manual", difficulty_declared=difficulty,
        content_json={
            "prompt": f"{_WORDS[(n * 7 + len(uaa.code) * 3 + len(module.code)) % len(_WORDS)]} "
                      f"{_WORDS[(n * 11 + 5) % len(_WORDS)]} {uaa.code} n°{n} ?",
            "options": [
                {"option_id": "a", "label": f"Réponse juste {uaa.code} {n}"},
                {"option_id": "b", "label": f"Réponse fausse {uaa.code} {n}"},
            ],
            "correct_option_ids": ["a"],
            "explanation": explanation,
        },
    )


def _content(db, *, per_uaa=3):
    """AMPCR (MC01 avec banque, MC02 sans), Français (FR01), FSE (FSE01, difficulté
    déclarée), MB32 hors parcours. Chaque cours a aussi une question rédigée (exclue)."""
    out = {}
    for name, slug, code, uaa_codes in (
        ("Informatique", "informatique", "AMPCR", ("MC01", "MC02")),
        ("Français", "francais", "FRANCAIS", ("FR01",)),
        ("Formation sociale et économique", "fse", "FSE", ("FSE01",)),
        ("Mathématiques", "mathematiques", "MB32", ("UAA1",)),
    ):
        subject = Subject(name=name, slug=slug)
        db.add(subject)
        db.flush()
        module = Module(code=code, slug=code.lower(), subject_id=subject.id)
        db.add(module)
        db.flush()
        uaas = []
        for position, uaa_code in enumerate(uaa_codes, start=1):
            uaa = UAA(code=uaa_code, title=f"Cours {uaa_code}", slug=f"t137-{uaa_code.lower()}",
                      position=position, is_published=True, module_id=module.id)
            db.add(uaa)
            uaas.append(uaa)
        db.flush()
        out[code] = (module, uaas)
    for code, (module, uaas) in out.items():
        for uaa in uaas:
            if uaa.code == "MC02":
                continue
            for n in range(1, per_uaa + 1):
                difficulty = (
                    (QuestionDifficulty.HARD if n == per_uaa else QuestionDifficulty.EASY)
                    if code == "FSE" else None
                )
                _mc(db, module, uaa, n + 100 * uaas.index(uaa), difficulty=difficulty)
            create_question(
                db, module_id=module.id, uaa_id=uaa.id, question_type="short_answer",
                generation_source="manual",
                content_json={"prompt": f"Explique {uaa.code}.", "accepted_answers": ["x"]},
            )
    db.commit()
    return out


def _choose(client):
    token = _csrf(client.get("/parcours?diplome=cess&forme=p").text)
    client.post("/parcours/choisir",
                data={"csrf_token": token, "diploma": "cess", "form": "p", "option": "ampcr"})


def _user(db):
    return db.query(User).filter_by(email="eleve-test@example.test").one()


def _start(client, **fields):
    token = _csrf(client.get("/quiz").text)
    data = {"csrf_token": token, "questions": "5", "difficulte": "medium", **fields}
    return client.post("/quiz/demarrer", data=data, follow_redirects=False)


def _session_id(response) -> int:
    assert response.status_code == 303, response.text
    match = re.match(r"/quiz/parties/(\d+)$", response.headers["location"])
    assert match, response.headers["location"]
    return int(match.group(1))


def _answer(client, session_id, position, option_id):
    token = _csrf(client.get(f"/quiz/parties/{session_id}").text)
    return client.post(
        f"/quiz/parties/{session_id}/valider",
        data={"csrf_token": token, "position": str(position), "option_id": option_id},
        follow_redirects=False,
    )


@pytest.fixture()
def player(authenticated_client, db_session):
    content = _content(db_session)
    _choose(authenticated_client)
    return authenticated_client, content


# --- Catalogue / périmètre ---------------------------------------------------------------------


def test_catalog_is_bounded_to_pathway_and_objective_types(player, db_session):
    _, content = player
    offers = build_catalog(db_session, resolve_keys("cess", "p", "ampcr"), _user(db_session))
    assert [o.module.code for o in offers] == ["AMPCR", "FRANCAIS", "FSE"]  # jamais MB32
    ampcr = offers[0]
    assert [(c.uaa.code, c.available) for c in ampcr.chapters] == [("MC01", 3), ("MC02", 0)]
    assert offers[2].declares_difficulty and not ampcr.declares_difficulty


def test_home_requires_account_and_lists_subjects_honestly(client, player):
    authenticated_client, _ = player
    page = _text(authenticated_client.get("/quiz").text)
    assert "Tout mon parcours" in page
    assert "Informatique — maintenance PC-réseaux" in page and "Français" in page
    assert "MC02 — Cours MC02 : pas encore de questions de quiz" in page
    assert "Mathématiques" not in page
    assert "QCM, classement, remise en ordre" in page
    authenticated_client.post("/logout", data={"csrf_token": _csrf(authenticated_client.get("/").text)})
    assert authenticated_client.get("/quiz", follow_redirects=False).status_code == 303


def test_recap_announces_distribution_and_limits_before_start(player):
    client, _ = player
    page = _text(client.get("/quiz/apercu?parcours=1&questions=5&difficulte=hard").text)
    assert "Tout mon parcours" in page and "Lancer la partie" in page
    assert "2 questions dans cette partie" in page  # 5 → 2/2/1 entre les 3 matières
    assert "1 question dans cette partie" in page
    assert "tous les cours ne seront pas interrogés" not in page  # 3 cours jouables, 5 questions
    assert "Difficulté non renseignée dans la banque pour : Informatique" in page
    only_missing = _text(client.get("/quiz/apercu?uaa=t137-mc02").text)
    assert "Pas de quiz possible pour ce choix" in only_missing
    assert "MC02" in only_missing


def test_plan_reports_short_quiz_and_insufficient_bank(player, db_session):
    catalog = build_catalog(db_session, resolve_keys("cess", "p", "ampcr"), _user(db_session))
    scope = resolve_scope(catalog, module_codes=["AMPCR"])
    plan = plan_quiz(scope, count=20, difficulty=SessionDifficultyRequest.MEDIUM)
    assert plan.total == 3
    assert any("la partie en comptera 3" in note for note in plan.notes)
    assert scope.label == "Informatique — maintenance PC-réseaux"


# --- Partie ----------------------------------------------------------------------------------


def test_single_chapter_game_feedback_results_and_course_links(player, db_session):
    client, _ = player
    session_id = _session_id(_start(client, uaa="t137-mc01"))
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.mode == SessionMode.QUIZ and session.question_count == 3
    assert {sq.question_version.question_type for sq in session.session_questions} == {"multiple_choice"}

    first = client.get(f"/quiz/parties/{session_id}").text
    assert "Question 1 / 3" in first
    assert EXPLANATION not in first and "correct_option_ids" not in first  # rien avant validation
    assert "Réponse juste" in first

    # Réponse incomplète : refusée, rien d'enregistré, jamais comptée fausse
    token = _csrf(first)
    incomplete = client.post(f"/quiz/parties/{session_id}/valider",
                             data={"csrf_token": token, "position": "1"})
    assert incomplete.status_code == 422 and "Choisis une réponse" in incomplete.text
    assert db_session.query(SessionAnswer).count() == 0

    wrong = _answer(client, session_id, 1, "b")
    assert wrong.headers["location"] == f"/quiz/parties/{session_id}?vu=1"
    feedback = _text(client.get(wrong.headers["location"]).text)
    assert "Pas tout à fait" in feedback and EXPLANATION in feedback
    assert "relis le cours MC01" in feedback and "Question suivante" in feedback

    # Double validation : aucune recorrection, aucune modification
    again = _answer(client, session_id, 1, "a")
    assert again.headers["location"] == f"/quiz/parties/{session_id}?vu=1"
    db_session.expire_all()
    answers = db_session.query(SessionAnswer).all()
    assert len(answers) == 1 and answers[0].points_awarded == 0.0

    # Reprise exacte : la partie reprend à la question 2
    assert "Question 2 / 3" in client.get(f"/quiz/parties/{session_id}").text
    _answer(client, session_id, 2, "a")
    last = _answer(client, session_id, 3, "a")
    assert "Voir mon résultat" in client.get(last.headers["location"]).text

    results = _text(client.get(f"/quiz/parties/{session_id}").text)
    assert "2 / 3 points" in results
    assert 'href="/uaa/t137-mc01"' in client.get(f"/quiz/parties/{session_id}").text
    assert "Reprendre mes erreurs" in results and "Rejouer (5 questions)" in results
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED and session.score == 2.0


def test_quiz_is_distinct_from_practice_exam_history_and_rating(player, db_session):
    client, content = player
    session_id = _session_id(_start(client, uaa="t137-mc01"))
    for position in (1, 2, 3):
        _answer(client, session_id, position, "a")
    user = _user(db_session)
    assert user_uaa_progress(db_session, user) == {}  # ni « entraîné » ni examen blanc
    assert f"/sessions/{session_id}" not in client.get("/mes-sessions").text
    assert db_session.query(UserModuleRating).count() == 0
    redirect = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert redirect.headers["location"] == f"/quiz/parties/{session_id}"
    token = _csrf(client.get("/quiz").text)
    assert client.post(f"/sessions/{session_id}/answer",
                       data={"csrf_token": token, "position": "1"}).status_code == 404
    assert client.get(f"/sessions/{session_id}/export.md").status_code == 404


def test_multi_subject_selection_is_applied_and_balanced(player, db_session):
    client, content = player
    session_id = _session_id(_start(client, matiere=["FRANCAIS", "FSE"], questions="5"))
    session = db_session.get(QuestionnaireSession, session_id)
    codes = [sq.question_version.question.module.code for sq in session.session_questions]
    assert set(codes) == {"FRANCAIS", "FSE"} and len(codes) == 5
    assert sorted([codes.count("FRANCAIS"), codes.count("FSE")]) == [2, 3]
    prompts = [sq.question_version.content_json["prompt"] for sq in session.session_questions]
    assert len(set(prompts)) == len(prompts)  # aucun doublon intra-partie


def test_whole_pathway_mixes_all_available_subjects(player, db_session):
    client, _ = player
    session_id = _session_id(_start(client, parcours="1", questions="10"))
    session = db_session.get(QuestionnaireSession, session_id)
    codes = {sq.question_version.question.module.code for sq in session.session_questions}
    assert codes == {"AMPCR", "FRANCAIS", "FSE"}
    assert session.question_count == 9  # 3 cours jouables × 3 questions : jamais de répétition


def test_unseen_questions_come_first_between_games(player, db_session):
    _, content = player
    module, uaas = content["AMPCR"]
    for n in range(4, 7):
        _mc(db_session, module, uaas[0], n)
    db_session.commit()
    user = _user(db_session)
    pathway = resolve_keys("cess", "p", "ampcr")
    scope = resolve_scope(build_catalog(db_session, pathway, user), uaa_slugs=["t137-mc01"])
    first = start_quiz(db_session, user=user, pathway=pathway, scope=scope, count=5,
                       difficulty=SessionDifficultyRequest.MEDIUM)
    first_ids = {sq.question_version.question_id for sq in first.session_questions}
    first.status = SessionStatus.ABANDONED
    db_session.commit()
    second = start_quiz(db_session, user=user, pathway=pathway, scope=scope, count=5,
                        difficulty=SessionDifficultyRequest.EASY)
    second_ids = [sq.question_version.question_id for sq in second.session_questions]
    assert len(first_ids) == 5
    assert second_ids[0] not in first_ids  # la seule jamais vue passe en premier


def test_requested_difficulty_is_preferred(player, db_session):
    user = _user(db_session)
    pathway = resolve_keys("cess", "p", "ampcr")
    scope = resolve_scope(build_catalog(db_session, pathway, user), uaa_slugs=["t137-fse01"])
    session = start_quiz(db_session, user=user, pathway=pathway, scope=scope, count=5,
                         difficulty=SessionDifficultyRequest.HARD)
    first = session.session_questions[0].question_version.question
    assert first.difficulty_declared == QuestionDifficulty.HARD


def test_retry_errors_uses_new_cases_from_failed_courses(player, db_session):
    client, content = player
    module, uaas = content["AMPCR"]
    for n in range(4, 7):
        _mc(db_session, module, uaas[0], n)
    db_session.commit()
    session_id = _session_id(_start(client, matiere=["AMPCR", "FSE"], questions="5"))
    session = db_session.get(QuestionnaireSession, session_id)
    missed = set()
    for sq in sorted(session.session_questions, key=lambda s: s.position):
        is_ampcr = sq.question_version.question.module.code == "AMPCR"
        if is_ampcr:
            missed.add(sq.question_version.question_id)
        _answer(client, session_id, sq.position, "b" if is_ampcr else "a")
    token = _csrf(client.get(f"/quiz/parties/{session_id}").text)
    retry = client.post(f"/quiz/parties/{session_id}/erreurs", data={"csrf_token": token},
                        follow_redirects=False)
    retry_id = _session_id(retry)
    db_session.expire_all()
    retry_session = db_session.get(QuestionnaireSession, retry_id)
    questions = [sq.question_version.question for sq in retry_session.session_questions]
    assert questions and all(q.uaa.code == "MC01" for q in questions)
    assert not {q.id for q in questions} & missed
    assert "Reprise de mes erreurs" in client.get(f"/quiz/parties/{retry_id}").text


def test_technical_error_is_never_a_wrong_answer(player, db_session, monkeypatch):
    user = _user(db_session)
    pathway = resolve_keys("cess", "p", "ampcr")
    scope = resolve_scope(build_catalog(db_session, pathway, user), uaa_slugs=["t137-fr01"])
    session = start_quiz(db_session, user=user, pathway=pathway, scope=scope, count=5,
                         difficulty=SessionDifficultyRequest.MEDIUM)
    questions = sorted(session.session_questions, key=lambda s: s.position)

    def boom(*_args, **_kwargs):
        raise RuntimeError("panne")

    monkeypatch.setattr("app.v1.quiz_service.correct_locally", boom)
    answer = validate_quiz_answer(db_session, session=session, session_question=questions[0],
                                  answer_json={"selected_option_ids": ["b"]})
    assert answer.correction_status == AnswerCorrectionStatus.FAILED and answer.points_awarded is None
    monkeypatch.undo()
    for sq in questions[1:]:
        validate_quiz_answer(db_session, session=session, session_question=sq,
                             answer_json={"selected_option_ids": ["a"]})
    results = quiz_results(session)
    assert session.status == SessionStatus.COMPLETED
    assert results["counted_total"] == 2 and results["not_counted"] == 1 and results["pct"] == 100


def test_double_start_returns_the_same_untouched_game(player, db_session):
    client, _ = player
    first = _session_id(_start(client, uaa="t137-mc01"))
    second = _session_id(_start(client, uaa="t137-mc01"))
    assert first == second
    assert db_session.query(QuestionnaireSession).filter_by(mode=SessionMode.QUIZ).count() == 1


def test_entry_points_from_dashboard_and_module_page(player):
    client, _ = player
    assert 'href="/quiz"' in client.get("/mon-parcours").text
    module_page = client.get("/modules/ampcr").text
    assert 'href="/quiz/apercu?matiere=AMPCR"' in module_page
    assert 'href="/quiz/apercu?uaa=t137-mc01"' in module_page
    assert 'href="/quiz/apercu?uaa=t137-mc02"' not in module_page  # pas de questions
    assert "Quiz sur toute la matière" not in client.get("/modules/mb32").text

"""Ticket #101 — Formation sociale et économique : FSE17 « Révision générale et méthode
d'examen » et les trois « examens blancs » progressifs (facile/moyen/difficile).

FSE17 n'est PAS une matière propre (comme MC38 pour AMPCR, ticket #58) : son contenu de
cours est une pure synthèse de FSE01-FSE16 (aucune notion nouvelle), et ses sessions
practice/exam tirent exclusivement dans la banque FSE01-FSE16 via
`app.v1.session_service._start_fse_transversal_session` — jamais dans FSE17 lui-même, qui
n'a pas de banque propre (voir `app.v1.routes_sessions._FSE_BANK_IMPORTERS`, où FSE17 est
volontairement absent).

Les « trois examens blancs progressifs » du ticket #101 sont réalisés en réutilisant
intégralement le sélecteur de difficulté déjà existant sur la page de démarrage de
n'importe quel cours FSE (facile=EASY, moyen=MEDIUM, difficile=HARD) : aucune nouvelle
infrastructure, aucune nouvelle UAA, conformément à « réutiliser le moteur de sessions
existant » (ticket #101) et à « pas de refonte du moteur hors périmètre » (ticket #102).

Aucun appel OpenAI réel : `FakeAIProvider`/`_UnconfiguredProvider` partout."""

import re
from collections import Counter

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.models import UAA, Module, Subject
from app.seed import seed
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.fse_plan import (
    FSE17_CODE,
    FSE17_SESSION_SCOPE,
    FSE_MODULE_CODE,
    FSE_PLAN_BY_CODE,
    FSE_SUBJECT_NAME,
    fse01_to_fse16_codes,
)
from app.v1.models import (
    QuestionDifficulty,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    User,
)
from app.v1.session_service import (
    DEFAULT_QUESTION_COUNT,
    GLOBAL_EXAM_QUESTION_COUNT,
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    describe_session_scope,
    get_session_build_job,
    run_correction_job,
    run_session_build_job,
    start_session,
)

FSE17_SLUG = "fse-fse17"


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _user(db_session, email: str) -> User:
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _resolve_build_job_url(db_session, location: str) -> str:
    from app.v1 import routes_sessions

    if not location.startswith("/session-build-jobs/"):
        return location
    job_id = int(location.rstrip("/").rsplit("/", 1)[-1])
    try:
        provider = routes_sessions.get_ai_provider()
    except AINotConfiguredError:
        provider = _UnconfiguredProvider()
    job = claim_next_pending_build_job(db_session)
    if job is None:
        job = get_session_build_job(db_session, job_id=job_id)
    run_session_build_job(db_session, job=job, provider=provider)
    job = get_session_build_job(db_session, job_id=job_id)
    return f"/sessions/{job.created_session_id}"


def _start_session(client, db_session, slug: str, mode: str, difficulty: str) -> str:
    response = client.get(f"/uaa/{slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return _resolve_build_job_url(db_session, response.headers["location"])


def _answer_all_and_submit(client, session_url: str, total: int, db_session, provider, severity: int) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == total else "next"
        response = client.post(
            f"{session_url}/answer",
            data={"csrf_token": token, "position": position, "direction": direction, "text": "une réponse de vérification"},
            follow_redirects=False,
        )
        assert response.status_code == 303
    response = client.get(response.headers["location"])
    token = _csrf(response.text)
    response = client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": severity}, follow_redirects=False
    )
    assert response.status_code == 303
    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=provider)


def _seed_all_fse_banks(db_session, module: Module) -> None:
    """Importe les 16 banques FSE01-FSE16 nécessaires pour que la révision transversale
    FSE17 ait un pool réel à sélectionner (jamais FSE17 lui-même, qui n'en a pas)."""
    from app.v1 import routes_sessions

    for code in fse01_to_fse16_codes():
        plan = FSE_PLAN_BY_CODE[code]
        uaa = db_session.query(UAA).filter_by(slug=plan.slug).first()
        importer = routes_sessions._FSE_BANK_IMPORTERS[plan.slug]
        importer(db_session, module, uaa)
    db_session.commit()


# =============================================================================================
# 1. Plan / registre
# =============================================================================================


def test_fse17_registered_in_plan():
    assert FSE17_CODE in FSE_PLAN_BY_CODE
    plan = FSE_PLAN_BY_CODE[FSE17_CODE]
    assert plan.title == "Révision générale et méthode d'examen"
    assert plan.slug == FSE17_SLUG


def test_fse17_not_in_bank_importers():
    """FSE17 (ticket #101) n'a volontairement pas de banque propre — même principe que
    MC38 (ticket #58, non présent dans les dicts d'import per-cours)."""
    from app.v1.routes_sessions import _FSE_BANK_IMPORTERS

    assert FSE17_SLUG not in _FSE_BANK_IMPORTERS


def test_fse01_to_fse16_codes_excludes_fse17():
    codes = fse01_to_fse16_codes()
    assert len(codes) == 16
    assert FSE17_CODE not in codes


# =============================================================================================
# 2. Matière / module / UAA — FSE17 seedé en dernière position
# =============================================================================================


def test_fse17_seeded_last(db_session):
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaas = db_session.query(UAA).filter_by(module_id=module.id).order_by(UAA.position).all()
    assert len(uaas) == 17
    assert uaas[-1].code == "FSE17"
    assert uaas[-1].is_published is True


# =============================================================================================
# 3. Cours — contenu réel, synthèse sans notion nouvelle
# =============================================================================================


def test_fse17_course_page_is_real_content(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE17_SLUG}")
    assert response.status_code == 200
    text = response.text
    # Ticket #105 : les titres de section exacts ont été reformulés par la refonte
    # pédagogique et visuelle (découpage en plusieurs blocs titrés) — ce test vérifie la
    # substance de chaque section plutôt que le libellé exact de son ancien titre.
    for notion in (
        "Interactions médiatiques", "Le citoyen et l'État", "Ce que je dois savoir faire",
        "Lexique", "Confusions fréquentes",
        "CITER", "IDENTIFIER", "EXPLIQUER", "JUSTIFIER",
        "examens blancs", "simulations pédagogiques du Jury",
    ):
        assert notion in text
    assert "provisoire" not in text.lower()
    # Ticket #101 : FSE17 ne réapprend aucune notion nouvelle.
    assert "aucune notion nouvelle" in text
    # Les 16 cours doivent tous être cités dans le tableau de synthèse.
    for code in fse01_to_fse16_codes():
        assert code in text


def test_fse17_twelve_transversal_exercises_with_separate_corrections(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE17_SLUG}")
    text = response.text
    for i in range(1, 13):
        assert f"Exercice {i}" in text
        assert f"Corrigé {i}" in text


# =============================================================================================
# 4. Mécanisme transversal — tire exclusivement dans FSE01-16, jamais FSE17
# =============================================================================================


def test_transversal_session_never_includes_fse17_questions(db_session):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    user = _user(db_session, email="fse17-practice@example.invalid")

    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=None, uaa_code=FSE17_CODE,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=_UnconfiguredProvider(), question_count=DEFAULT_QUESTION_COUNT,
    )
    covered_codes = {
        sq.question_version.question.uaa.code for sq in session.session_questions
    }
    assert "FSE17" not in covered_codes
    assert covered_codes <= set(fse01_to_fse16_codes())
    assert session.parameters_json["scope"] == FSE17_SESSION_SCOPE


def test_transversal_session_covers_multiple_courses(db_session):
    """Un examen blanc transversal (20 questions) doit, avec 16 cours disponibles,
    couvrir plusieurs mini-cours distincts — jamais un seul (§ balance par UAA,
    `_uaa_balanced_oversample`, même mécanisme que l'examen blanc global AMPCR)."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    user = _user(db_session, email="fse17-exam@example.invalid")

    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=None, uaa_code=FSE17_CODE,
        mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=_UnconfiguredProvider(), question_count=GLOBAL_EXAM_QUESTION_COUNT,
    )
    covered_codes = {
        sq.question_version.question.uaa.code for sq in session.session_questions
    }
    assert len(covered_codes) >= 5
    assert len(session.session_questions) == GLOBAL_EXAM_QUESTION_COUNT


def test_transversal_session_has_no_duplicate_questions(db_session):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    user = _user(db_session, email="fse17-dedup@example.invalid")

    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=None, uaa_code=FSE17_CODE,
        mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest.HARD,
        provider=_UnconfiguredProvider(), question_count=GLOBAL_EXAM_QUESTION_COUNT,
    )
    question_ids = [sq.question_version.question.id for sq in session.session_questions]
    assert len(question_ids) == len(set(question_ids))


def test_describe_session_scope_labels_fse17(db_session):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    user = _user(db_session, email="fse17-scope@example.invalid")

    session = start_session(
        db_session, user=user, module_id=module.id, uaa_id=None, uaa_code=FSE17_CODE,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.EASY,
        provider=_UnconfiguredProvider(), question_count=DEFAULT_QUESTION_COUNT,
    )
    assert describe_session_scope(session) == "FSE17 — Révision transversale (FSE01→FSE16)"


# =============================================================================================
# 5. Les trois examens blancs progressifs (facile/moyen/difficile) — difficulté réellement
#    effective sur le pool transversal complet
# =============================================================================================


def test_three_progressive_mock_exams_via_difficulty_selector(db_session):
    """Facile/moyen/difficile = EASY/MEDIUM/HARD choisis au démarrage de l'examen FSE17 —
    aucune UAA ni mécanisme supplémentaire : la difficulté déjà effective depuis le ticket
    #96 (review) s'applique ici au pool transversal FSE01-16 complet."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)

    def run(difficulty, email):
        user = _user(db_session, email=email)
        session = start_session(
            db_session, user=user, module_id=module.id, uaa_id=None, uaa_code=FSE17_CODE,
            mode=SessionMode.EXAM, difficulty=difficulty,
            provider=_UnconfiguredProvider(), question_count=GLOBAL_EXAM_QUESTION_COUNT,
        )
        return Counter(sq.question_version.question.difficulty_declared for sq in session.session_questions)

    facile = run(SessionDifficultyRequest.EASY, "fse17-facile@example.invalid")
    moyen = run(SessionDifficultyRequest.MEDIUM, "fse17-moyen@example.invalid")
    difficile = run(SessionDifficultyRequest.HARD, "fse17-difficile@example.invalid")

    # 16 cours x 7 EASY = 112 disponibles, aucun type EASY n'est "sémantique long" (§ 14 du
    # ticket #55) : un examen facile de 20 questions est donc intégralement EASY.
    assert facile[QuestionDifficulty.EASY] == 20
    # Idem pour MEDIUM (classification/short_answer/ordering, jamais long_answer/
    # document_analysis dans les banques FSE) : un examen moyen est intégralement MEDIUM.
    assert moyen[QuestionDifficulty.MEDIUM] == 20
    # HARD est, par construction des banques FSE (ticket #96), composé exclusivement de
    # document_analysis/long_answer — tous deux des types "sémantiques longs" plafonnés à
    # MAX_LONG_SEMANTIC_PER_SESSION=3 PAR SESSION (§ 14 du ticket #55, règle transversale à
    # toute la plateforme, jamais contournée pour FSE17). L'examen "difficile" obtient donc
    # le maximum de 3 questions HARD (le plus possible sans violer cette règle) plutôt que
    # 20 : la difficulté progresse par la présence de ces 3 analyses longues/autonomes
    # (jamais présentes dans facile/moyen), pas par un remplacement intégral du contenu —
    # conforme au ticket #101 (« difficulté croissante par autonomie et complexité, pas par
    # ajout de contenu hors programme »).
    assert difficile[QuestionDifficulty.HARD] == 3
    assert facile[QuestionDifficulty.HARD] == 0
    assert moyen[QuestionDifficulty.HARD] == 0
    assert facile != moyen != difficile
    assert facile != difficile


# =============================================================================================
# 6. Parcours complet HTTP (practice + exam, difficulté + sévérité, reprise)
# =============================================================================================


def test_full_exam_flow_fse17(authenticated_client, db_session, monkeypatch):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    fake = _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, db_session, FSE17_SLUG, "exam", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    assert len(session.session_questions) == GLOBAL_EXAM_QUESTION_COUNT
    total = len(session.session_questions)

    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=3)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    assert session.parameters_json["severity"] == 3
    assert len(fake.semantic_calls) <= 1

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    # Chaque question d'une session transversale FSE17 relie vers SA propre UAA réelle
    # (FSE01-16), jamais vers FSE17 lui-même (qui n'a pas de contenu de banque) — comportement
    # correct et plus utile (relire le cours d'origine de chaque question), vérifié ici par
    # la présence d'au moins un lien vers un vrai cours FSE parmi FSE01-16.
    assert any(f"/uaa/fse-{code.lower()}" in results.text for code in fse01_to_fse16_codes())
    assert f"/uaa/{FSE17_SLUG}" not in results.text


def test_settings_persist_across_resume_fse17(authenticated_client, db_session, monkeypatch):
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    _seed_all_fse_banks(db_session, module)
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, db_session, FSE17_SLUG, "practice", "easy")
    session_id = int(session_url.rsplit("/", 1)[-1])

    landing = authenticated_client.get(f"/uaa/{FSE17_SLUG}/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    assert session_url in landing.text

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.EASY
    assert session.status.value == "in_progress"
    assert len(session.session_questions) == DEFAULT_QUESTION_COUNT


# =============================================================================================
# 7. Non-régression — FSE01-16, MC38 (AMPCR) et Français restent inchangés
# =============================================================================================


def test_fse01_and_fse09_still_work_after_fse17_added(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    for slug, title in [
        ("fse-fse01", "Communiquer : le schéma de communication"),
        ("fse-fse09", "Qui décide de quoi ?"),
    ]:
        response = authenticated_client.get(f"/uaa/{slug}")
        assert response.status_code == 200
        assert title in response.text

    session_url = _start_session(authenticated_client, db_session, "fse-fse01", "practice", "medium")
    assert session_url.startswith("/sessions/")


def test_mc38_transversal_unaffected(authenticated_client, db_session, monkeypatch):
    """MC38 (ticket #58) utilise un mécanisme transversal analogue mais distinct — ce test
    garantit que l'ajout de FSE17 n'a pas interféré avec son dispatch dans `start_session`."""
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/ampcr-mc38/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc38/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    url = _resolve_build_job_url(db_session, response.headers["location"])
    assert url.startswith("/sessions/")


def test_ampcr_and_francais_unaffected(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    for slug in ("ampcr-mc01", "francais-c01"):
        response = authenticated_client.get(f"/uaa/{slug}/practice")
        assert response.status_code == 200
        token = _csrf(response.text)
        response = authenticated_client.post(
            f"/uaa/{slug}/practice/start",
            data={"csrf_token": token, "difficulty": "medium"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        url = _resolve_build_job_url(db_session, response.headers["location"])
        assert url.startswith("/sessions/")

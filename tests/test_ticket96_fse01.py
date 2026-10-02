"""Ticket #96 — Formation sociale et économique (FSE) : création de la matière et
livraison complète de FSE01 « Communiquer : le schéma de communication » (cahier des
charges détaillé du ticket #97).

Contexte : aucune matière FSE n'existait dans le dépôt avant ce ticket. Ce test couvre :
la création de la matière/du module/de FSE01 (idempotente, FSE02→FSE17 jamais présentés
comme disponibles), la réutilisation intégrale du moteur V1 existant (banque, sessions,
autosave, reprise, correction hybride asynchrone), et surtout que difficulté ET sévérité
de cotation — deux paramètres distincts — sont réellement transmis, persistés et
appliqués côté serveur, y compris lors d'une reprise de session.

Aucun appel OpenAI réel : `FakeAIProvider` partout (voir `app.ai.fake_provider`)."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.ai.schemas import Questionnaire
from app.models import UAA, Module, Subject
from app.seed import seed
from app.v1.ai_bridge import CORRECTABLE_TYPES, content_to_questionnaire_question
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.fse_bank import import_fse01_to_bank
from app.v1.fse_plan import (
    FSE_MODULE_CODE,
    FSE_PLAN,
    FSE_PLAN_BY_CODE,
    FSE_SUBJECT_NAME,
    get_fse_context,
)
from app.v1.hybrid_correction import correct_session_hybrid
from app.v1.models import (
    Question,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    User,
)
from app.v1.session_service import (
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    compose_selection,
    get_session_build_job,
    run_correction_job,
    run_session_build_job,
    start_session,
)

FSE01_SLUG = "fse-fse01"


def _user(db_session, email="fse96-review@example.invalid") -> User:
    """Utilisateur minimal pour les appels de service directs (sans passer par
    l'inscription HTTP) — même pattern que
    `tests/test_ticket82_no_intrasession_duplicates.py::_user`."""
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _resolve_build_job_url(db_session, location: str) -> str:
    """Ticket #92 : /start crée un SessionBuildJob et redirige vers sa page d'attente —
    fait tourner le job en direct (appel de service, jamais un vrai worker séparé),
    exactement comme `tests/test_ticket94_french_20_courses.py`."""
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


def _start_session(client, db_session, mode: str, difficulty: str) -> str:
    response = client.get(f"/uaa/{FSE01_SLUG}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{FSE01_SLUG}/{mode}/start",
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
            data={"csrf_token": token, "position": position, "direction": direction, "text": "une réponse"},
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


# =============================================================================================
# 1. Plan / registre
# =============================================================================================


def test_fse01_registered_in_fse_plan():
    assert "FSE01" in FSE_PLAN_BY_CODE
    plan = FSE_PLAN_BY_CODE["FSE01"]
    assert plan.title == "Communiquer : le schéma de communication"
    assert plan.slug == FSE01_SLUG


def test_fse01_to_fse17_in_plan():
    """Ticket #96 : FSE01 rédigé. Ticket #97 : FSE02-FSE04 rédigés (voir
    tests/test_ticket97_fse02_04.py). Ticket #98 : FSE05-FSE08 rédigés (voir
    tests/test_ticket98_fse05_08.py). Tickets #99/#100/#101 : FSE09-FSE17 rédigés (voir
    tests/test_ticket99_fse09_12.py, tests/test_ticket100_fse13_16.py,
    tests/test_ticket101_fse17.py). Le programme officiel des 17 mini-cours est désormais
    complet."""
    assert [plan.code for plan in FSE_PLAN] == [
        "FSE01", "FSE02", "FSE03", "FSE04", "FSE05", "FSE06", "FSE07", "FSE08",
        "FSE09", "FSE10", "FSE11", "FSE12", "FSE13", "FSE14", "FSE15", "FSE16", "FSE17",
    ]


# =============================================================================================
# 2. Matière / module / UAA — création idempotente, les 17 mini-cours présents
# =============================================================================================


def test_fse_subject_module_uaa_seeded(db_session):
    """Tickets #97-#101 : FSE02-FSE17 ajoutés après FSE01 — voir les fichiers de test dédiés
    à chaque ticket pour la couverture complète (plan, ordre, idempotence). Ce test reste
    focalisé sur FSE01 lui-même."""
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    assert subject is not None
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    assert module is not None
    uaas = db_session.query(UAA).filter_by(module_id=module.id).all()
    assert len(uaas) == 17
    fse01 = next(u for u in uaas if u.code == "FSE01")
    assert fse01.is_published is True
    assert fse01.slug == FSE01_SLUG


def test_fse_seed_is_idempotent(db_session):
    seed()
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    assert db_session.query(UAA).filter_by(module_id=module.id).count() == 17


def test_fse_visible_in_subjects_navigation(client, db_session):
    seed()
    response = client.get("/subjects")
    assert response.status_code == 200
    assert FSE_SUBJECT_NAME in response.text

    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    response = client.get(f"/subjects/{subject.slug}")
    assert response.status_code == 200
    assert FSE_MODULE_CODE in response.text

    module = subject.modules[0]
    response = client.get(f"/modules/{module.slug}")
    assert response.status_code == 200
    assert "Communiquer : le schéma de communication" in response.text
    assert f"/uaa/{FSE01_SLUG}" in response.text


# =============================================================================================
# 3. Cours — contenu réel, pas un brouillon/stub
# =============================================================================================


def test_fse01_course_page_is_real_content(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE01_SLUG}")
    assert response.status_code == 200
    text = response.text
    for notion in ("émetteur", "récepteur", "canal", "code", "contexte", "rétroaction", "obstacle"):
        assert notion in text
    # Les trois applications explicitement demandées par le ticket #97.
    assert "Karim Haddad" in text  # mail
    assert "sécurité routière" in text  # affiche
    assert "Techno Services" in text  # réseau social
    # Jamais présenté comme un brouillon/validation technique (voir
    # tests/test_ticket94_french_20_courses.py::test_fr01_05_pages_never_show_provisional_status_to_the_user).
    assert "provisoire" not in text.lower()
    assert "stub" not in text.lower()


def test_fse01_hidden_answers_use_details_collapsed_by_default(client, db_session):
    seed()
    response = client.get(f"/uaa/{FSE01_SLUG}")
    # Ticket #112 : les corrigés utilisent <details class="jc-exercise-correction">
    # (toujours l'élément natif <details>, sans l'attribut "open" — fermé par défaut).
    assert "<details" in response.text
    assert "<details open" not in response.text
    assert "Voir le corrigé" in response.text


# =============================================================================================
# 4. Banque — types corrects, documents réellement rattachés, isolation
# =============================================================================================


def test_fse01_bank_import_is_idempotent(db_session):
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    module = uaa.module
    first = import_fse01_to_bank(db_session, module, uaa)
    second = import_fse01_to_bank(db_session, module, uaa)
    assert first == 14
    assert second == 0
    assert db_session.query(Question).filter_by(uaa_id=uaa.id).count() == 14


def test_fse01_bank_uses_only_relevant_question_types(db_session):
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    for question in questions:
        assert question.current_version.question_type in CORRECTABLE_TYPES


def test_no_orphan_document_dependent_questions_in_fse01(db_session):
    """Même règle que le Français (#94 § 8) : toute question qui porte
    `source_document_version_id` référence un SourceDocumentVersion réellement persisté."""
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    from app.v1.models import SourceDocumentVersion

    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    checked = 0
    for question in questions:
        content = question.current_version.content_json
        doc_id = content.get("source_document_version_id")
        if doc_id:
            checked += 1
            assert db_session.get(SourceDocumentVersion, doc_id) is not None
    assert checked >= 6  # au moins les short_answer/document_analysis/long_answer rattachés


def test_fse01_questions_isolated_to_its_own_uaa(db_session):
    """Aucun mélange avec Informatique/Français/Mathématiques : toutes les questions
    importées pour FSE01 appartiennent exclusivement à son propre uaa_id."""
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 14
    assert all(q.module.code == FSE_MODULE_CODE for q in questions)


# =============================================================================================
# 5. Parcours complet — théorie -> entraînement -> examen -> correction -> résultats
# =============================================================================================


def test_fse01_practice_session_offers_difficulty_choice_with_same_labels(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
    assert response.status_code == 200
    for label in ("Facile", "Moyen", "Difficile"):
        assert label in response.text


def test_fse01_exam_offers_difficulty_and_severity_choice(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "hard")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert response.status_code == 200
    token = _csrf(response.text)
    authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "submit", "text": "réponse"},
        follow_redirects=False,
    )
    confirm = authenticated_client.get(f"{session_url}/submit-confirm")
    assert confirm.status_code == 200
    for level in (1, 2, 3, 4, 5):
        assert f'id="severity-{level}"' in confirm.text


def test_fse01_difficulty_and_severity_are_distinct_and_applied_server_side(authenticated_client, db_session, monkeypatch):
    """Coeur du ticket #96 : difficulté (sélection des questions) et sévérité (notation)
    sont deux réglages distincts, transmis au serveur, persistés en base, et appliqués
    réellement (pas un simple sélecteur décoratif)."""
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "easy")
    session_id = int(session_url.rsplit("/", 1)[-1])

    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.EASY

    total = len(session.session_questions)
    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=5)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    # La sévérité choisie à la soumission ne modifie jamais la difficulté choisie au départ.
    assert session.difficulty_requested == SessionDifficultyRequest.EASY
    assert session.parameters_json["severity"] == 5


def test_fse01_settings_persist_across_resume(authenticated_client, db_session, monkeypatch):
    """Une session en cours, rechargée (reprise), conserve exactement la difficulté
    choisie au départ — pas seulement au moment de la création."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "practice", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])

    landing = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    assert session_url in landing.text

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    assert session.status.value == "in_progress"


def test_fse01_full_exam_flow_results_and_back_to_course_link(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    total = len(session.session_questions)

    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=3)

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert f"/uaa/{FSE01_SLUG}" in results.text  # retour au cours

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    assert session.score is not None
    assert len(fake.semantic_calls) <= 1  # jamais un appel IA par question
    for sq in session.session_questions:
        assert sq.answer is not None
        assert sq.answer.correction_status.value == "corrected"


def test_fse01_no_duplicate_questions_within_a_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    version_ids = [sq.question_version_id for sq in session.session_questions]
    assert len(version_ids) == len(set(version_ids))


# =============================================================================================
# 6. Non-régression — Informatique AMPCR et Français restent inchangés
# =============================================================================================


def test_ampcr_and_francais_unaffected_by_fse(authenticated_client, db_session, monkeypatch):
    """Les modifications partagées (app/main.py, routes_sessions.py, session_service.py)
    pour brancher FSE ne changent rien au comportement d'Informatique AMPCR ni de
    Français — vérifié par un aller-retour pratique complet sur chacun."""
    seed()
    _patch_fake_provider(monkeypatch)

    # AMPCR MC01
    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    url = _resolve_build_job_url(db_session, response.headers["location"])
    assert url.startswith("/sessions/")

    # Français C01 (pilote historique #47)
    response = authenticated_client.get("/uaa/francais-c01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/practice/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    url = _resolve_build_job_url(db_session, response.headers["location"])
    assert url.startswith("/sessions/")


# =============================================================================================
# 7. Review de beef790 — difficulté/sévérité : mécanisme réel, pas seulement la
#    persistance (les tests de la section 5 ci-dessus vérifiaient surtout que les valeurs
#    étaient enregistrées ; ceux-ci prouvent, avec FakeAIProvider, qu'elles sont bien
#    TRANSMISES aux bons appels, et documentent explicitement la limite réelle du moteur
#    pour la banque hand-authored de FSE01).
# =============================================================================================


def test_fse01_bank_questions_now_declare_a_difficulty_and_it_is_honored_by_selection(db_session):
    """Remplace l'ancienne limite assumée du commit `65f0712` (« les 14 questions FSE01
    n'ont aucune difficulté déclarée, le moteur ne peut donc pas filtrer parmi elles ») —
    corrigée par ce complément de review : `app.v1.bank.select_bank_questions` et
    `app.v1.session_service.compose_selection` prennent désormais un paramètre
    `difficulty`, honoré par un round-robin en deux passes (voir section 8 ci-dessous pour
    la preuve par la sélection réelle, pas seulement la signature)."""
    import inspect

    from app.v1.bank import select_bank_questions

    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 14
    assert any(q.difficulty_declared is not None for q in questions), (
        "les questions FSE01 doivent désormais porter une difficulté déclarée"
    )
    assert "difficulty" in inspect.signature(select_bank_questions).parameters
    assert "difficulty" in inspect.signature(compose_selection).parameters


def _start_fse01_with_generation_shortfall(db_session, *, email: str, difficulty: SessionDifficultyRequest):
    """Fraîchement seedée à chaque appel (fixture `db_session` function-scoped — base
    vidée/recréée entre tests, voir `tests/conftest.py::_clean_database`) : indispensable
    ici, car `start_session` PERSISTE dans la banque les questions générées pour combler
    le manque (`persist_generated_questions`) — un deuxième appel dans la MÊME base, même
    avec un autre utilisateur, retrouverait une banque déjà enrichie à 20 par le premier
    appel et ne déclencherait plus aucune génération. Chaque difficulté est donc vérifiée
    dans un test séparé, chacun avec sa propre base vierge."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, module, uaa)
    fake = FakeAIProvider()
    user = _user(db_session, email=email)
    start_session(
        db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="FSE01",
        mode=SessionMode.PRACTICE, difficulty=difficulty,
        provider=fake, question_count=20,  # > 14 : force la génération de complément
    )
    assert fake.questionnaire_calls, "banque (14) < question_count (20) doit déclencher une génération"
    return fake.questionnaire_calls[-1]


def test_fse01_easy_difficulty_is_transmitted_to_ai_generation_when_bank_is_insufficient(db_session):
    """Avec `question_count` > taille de la banque (14), `start_session`
    (app.v1.session_service) déclenche une génération IA de complément — un SECOND canal,
    distinct de la sélection dans la banque hand-authored (voir section 8 ci-dessous), par
    lequel la difficulté choisie a aussi un effet. Vérifie, avec `FakeAIProvider`, que la
    difficulté « facile » transmise dans la
    `QuestionnaireRequest` correspond exactement à celle demandée (traduction
    `_DIFFICULTY_TO_FRENCH`), et que le contexte pédagogique transmis est spécifiquement
    celui de FSE01 (`course_key == "fse-fse01"`), jamais un contexte générique (ex. le
    contexte AMPCR global)."""
    request = _start_fse01_with_generation_shortfall(
        db_session, email="fse96-review-easy@example.invalid", difficulty=SessionDifficultyRequest.EASY,
    )
    assert request.difficulty == "facile"
    assert any(c.course_key == "fse-fse01" for c in request.contexts), (
        "le contexte pédagogique transmis à la génération doit être celui de FSE01"
    )


def test_fse01_hard_difficulty_is_transmitted_to_ai_generation_when_bank_is_insufficient(db_session):
    """Même vérification que le test précédent, pour la difficulté « difficile » — dans
    une base séparée (voir `_start_fse01_with_generation_shortfall`), afin que les deux
    valeurs de difficulté transmises puissent être comparées sans que la banque enrichie
    par le premier appel ne fausse le second."""
    request = _start_fse01_with_generation_shortfall(
        db_session, email="fse96-review-hard@example.invalid", difficulty=SessionDifficultyRequest.HARD,
    )
    assert request.difficulty == "difficile"
    assert any(c.course_key == "fse-fse01" for c in request.contexts), (
        "le contexte pédagogique transmis à la génération doit être celui de FSE01"
    )


def test_fse01_severity_is_transmitted_to_correction_and_changes_points_awarded(db_session):
    """Réutilise le vrai barème FSE01 (rubric du `long_answer` sur le mail de Karim,
    banque réelle, contexte pédagogique réel `get_fse_context`) pour prouver, avec
    `FakeAIProvider`, que (1) la sévérité choisie est bien celle reçue par
    `correct_semantic_batch` (tracée dans `fake.semantic_calls`), et (2) qu'elle change
    réellement les points attribués pour une même réponse — jamais un simple sélecteur
    décoratif, pour FSE01 comme pour les autres matières (comportement générique déjà
    couvert par `tests/test_ticket62_hybrid_correction_history_export.py`, reproduit ici
    spécifiquement avec le contenu FSE01)."""
    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    long_answer_question = next(
        q for q in questions if q.current_version.question_type == "long_answer"
    )
    content = long_answer_question.current_version.content_json
    qq = content_to_questionnaire_question(
        question_id="q1", question_type="long_answer", content=content, points_max=1.0,
    )
    questionnaire = Questionnaire(mode="exam", questions=[qq])
    context = get_fse_context("fse-fse01")
    assert context is not None
    fake = FakeAIProvider()
    answer = {"q1": "Une réponse de test suffisamment longue pour être prise en compte."}

    lenient = correct_session_hybrid(fake, questionnaire, answer, {}, "very_lenient", (context,))
    strict = correct_session_hybrid(fake, questionnaire, answer, {}, "very_strict", (context,))

    assert fake.semantic_calls[-2][1] == "very_lenient"
    assert fake.semantic_calls[-1][1] == "very_strict"
    assert lenient.questions[0].points_awarded > strict.questions[0].points_awarded, (
        "la sévérité doit réellement changer les points attribués pour une réponse identique"
    )


def test_fse01_severity_ui_choice_reaches_the_correction_call_with_correct_mapping(
    authenticated_client, db_session, monkeypatch
):
    """Bout en bout HTTP (pas seulement au niveau service) : la valeur 1-5 choisie dans le
    formulaire `/sessions/{id}/submit` est bien celle reçue par `correct_semantic_batch`,
    via le mapping documenté dans `app.v1.session_service._SEVERITY_UI_TO_INTERNAL`
    (1 -> very_lenient, ..., 5 -> very_strict)."""
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id = int(session_url.rsplit("/", 1)[-1])
    total = len(db_session.get(QuestionnaireSession, session_id).session_questions)
    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=1)
    assert fake.semantic_calls, "au moins une question FSE01 nécessite une notation sémantique"
    assert fake.semantic_calls[-1][1] == "very_lenient"

    fake2 = _patch_fake_provider(monkeypatch)
    session_url_2 = _start_session(authenticated_client, db_session, "exam", "medium")
    session_id_2 = int(session_url_2.rsplit("/", 1)[-1])
    total2 = len(db_session.get(QuestionnaireSession, session_id_2).session_questions)
    _answer_all_and_submit(authenticated_client, session_url_2, total2, db_session, fake2, severity=5)
    assert fake2.semantic_calls[-1][1] == "very_strict"


def test_fse01_difficulty_persists_across_multiple_reloads_and_partial_answers(
    authenticated_client, db_session, monkeypatch
):
    """Renforce `test_fse01_settings_persist_across_resume` : la difficulté reste HARD à
    travers PLUSIEURS rechargements successifs de la page de reprise, et après qu'une
    réponse a été partiellement enregistrée — pas seulement juste après la création."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "practice", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])

    for _ in range(3):
        landing = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
        assert "Reprendre l'entraînement en cours" in landing.text
        db_session.expire_all()
        session = db_session.get(QuestionnaireSession, session_id)
        assert session.difficulty_requested == SessionDifficultyRequest.HARD

    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text)
    authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": 1, "direction": "next", "text": "réponse partielle"},
        follow_redirects=False,
    )

    landing = authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    assert session.status.value == "in_progress"


# =============================================================================================
# 8. Review de 65f0712 — la difficulté influence RÉELLEMENT les questions servies, pas
#    seulement une valeur enregistrée/transmise à une génération forcée. Couvre le parcours
#    NORMAL de FSE01 (banque déjà remplie, 14 questions, sessions de 10, practice ET exam,
#    sessions successives, reprise) — sans fournisseur IA configuré (`_UnconfiguredProvider`,
#    reflet exact de la production réelle de FSE01 aujourd'hui, OPENAI_API_KEY vide).
#
#    Mécanisme (app/v1/bank.py, app/v1/session_service.py — générique, adapté, pas un
#    second moteur) :
#    1. `app.v1.bank._prioritize_by_difficulty` place en tête, dans le pool brut lu en
#       base, les questions dont `difficulty_declared` correspond à la difficulté demandée.
#    2. `app.v1.session_service.compose_selection` exécute D'ABORD le round-robin
#       type-diverse habituel UNIQUEMENT sur ces questions (`matching`), et ne complète
#       avec le reste (`other`) que si cette première passe ne suffit pas à atteindre le
#       nombre de questions demandé — sans jamais réinitialiser le plafond de types
#       sémantiques longs entre les deux passes.
#    Un simple tri avant le groupage par type ne suffisait pas : `compose_selection`
#    regroupe par type puis mélange chaque groupe, ce qui aurait noyé toute préférence
#    d'ordre avec une banque aussi petite que celle de FSE01 (14 questions pour 10
#    demandées) — vérifié expérimentalement pendant le développement de ce correctif avant
#    la réécriture en deux passes.
# =============================================================================================


def test_fse01_difficulty_declared_distribution_is_6_5_3(db_session):
    """Précondition des tests ci-dessous, vérifiée explicitement plutôt que supposée : 6
    questions EASY, 5 MEDIUM, 3 HARD — assez de chaque pour que le choix de difficulté ait
    un effet substantiel et mesurable dans une session de 10 questions."""
    from collections import Counter

    seed()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    counts = Counter(q.difficulty_declared for q in questions)
    assert counts == {
        QuestionDifficulty.EASY: 6,
        QuestionDifficulty.MEDIUM: 5,
        QuestionDifficulty.HARD: 3,
    }


def _declared_difficulty_counts(session: QuestionnaireSession) -> dict:
    from collections import Counter

    return Counter(
        sq.question_version.question.difficulty_declared for sq in session.session_questions
    )


def test_fse01_difficulty_filters_served_questions_in_normal_practice_session(db_session):
    """Cœur de la demande de review : dans le parcours NORMAL (banque déjà remplie, 10
    questions, AUCUN fournisseur IA configuré — `_UnconfiguredProvider`, comme en
    production réelle pour FSE01 aujourd'hui), choisir EASY/MEDIUM/HARD produit des
    sessions dont la composition par difficulté diffère RÉELLEMENT, et contient TOUJOURS
    l'intégralité des questions disponibles à la difficulté demandée (6/5/3) — jamais
    seulement une valeur enregistrée sans effet sur la sélection."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, module, uaa)

    def run(difficulty: SessionDifficultyRequest, email: str) -> QuestionnaireSession:
        user = _user(db_session, email=email)
        return start_session(
            db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="FSE01",
            mode=SessionMode.PRACTICE, difficulty=difficulty,
            provider=_UnconfiguredProvider(), question_count=10,
        )

    easy_counts = _declared_difficulty_counts(run(SessionDifficultyRequest.EASY, "diff-easy@example.invalid"))
    medium_counts = _declared_difficulty_counts(run(SessionDifficultyRequest.MEDIUM, "diff-medium@example.invalid"))
    hard_counts = _declared_difficulty_counts(run(SessionDifficultyRequest.HARD, "diff-hard@example.invalid"))

    # Chaque difficulté demandée est intégralement représentée (toutes les questions
    # disponibles à cette difficulté sont servies) — jamais une préférence noyée/ignorée.
    assert easy_counts[QuestionDifficulty.EASY] == 6
    assert medium_counts[QuestionDifficulty.MEDIUM] == 5
    assert hard_counts[QuestionDifficulty.HARD] == 3

    # Les trois compositions sont réellement différentes les unes des autres (pas le même
    # ensemble de questions recyclé quel que soit le réglage).
    assert easy_counts != medium_counts
    assert medium_counts != hard_counts
    assert easy_counts != hard_counts

    # Chaque session reste bien composée de 10 questions (parcours normal, pas raccourci).
    for counts in (easy_counts, medium_counts, hard_counts):
        assert sum(counts.values()) == 10


def test_fse01_difficulty_filters_served_questions_in_normal_exam_session(db_session):
    """Même preuve que le test précédent, en examen (`SessionMode.EXAM`) — la demande
    explicite couvre « entraînement ET examen de 10 questions » : même mécanisme
    générique, aucune différence de traitement entre les deux modes."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, module, uaa)

    def run(difficulty: SessionDifficultyRequest, email: str) -> QuestionnaireSession:
        user = _user(db_session, email=email)
        return start_session(
            db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="FSE01",
            mode=SessionMode.EXAM, difficulty=difficulty,
            provider=_UnconfiguredProvider(), question_count=10,
        )

    easy_counts = _declared_difficulty_counts(run(SessionDifficultyRequest.EASY, "exam-diff-easy@example.invalid"))
    hard_counts = _declared_difficulty_counts(run(SessionDifficultyRequest.HARD, "exam-diff-hard@example.invalid"))

    assert easy_counts[QuestionDifficulty.EASY] == 6
    assert hard_counts[QuestionDifficulty.HARD] == 3
    assert easy_counts != hard_counts


def test_fse01_difficulty_preference_holds_across_successive_sessions_without_ai(db_session):
    """« Sessions successives » (demande explicite) : un même utilisateur qui enchaîne
    plusieurs sessions HARD doit continuer à recevoir les 3 questions HARD à chaque fois,
    même une fois qu'elles sont toutes déjà vues — preuve que le repli « dernier recours »
    (`select_bank_questions` sur les questions déjà vues, `app.v1.session_service.
    start_session`) reste lui aussi sensible à la difficulté demandée, pas seulement la
    toute première sélection sur des questions inédites. Sans fournisseur IA configuré
    (reflet de la production réelle) : la génération de complément échoue systématiquement
    et le repli sur les questions déjà vues est donc réellement exercé, pas contourné."""
    seed()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=FSE01_SLUG).first()
    import_fse01_to_bank(db_session, module, uaa)
    user = _user(db_session, email="successive-hard@example.invalid")

    for attempt in range(1, 4):
        session = start_session(
            db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code="FSE01",
            mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.HARD,
            provider=_UnconfiguredProvider(), question_count=10,
        )
        counts = _declared_difficulty_counts(session)
        assert counts[QuestionDifficulty.HARD] == 3, (
            f"session {attempt} : les 3 questions HARD doivent rester présentes même une "
            "fois déjà vues, via le repli difficulté-aware sur les questions vues"
        )


def test_fse01_difficulty_composition_persists_through_resume(authenticated_client, db_session, monkeypatch):
    """« Reprise » (demande explicite) : la composition par difficulté d'une session HARD
    ne change pas entre sa création et sa relecture (page rechargée plusieurs fois) — les
    `SessionQuestion` sont figées à la création, jamais recalculées à l'affichage."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, "practice", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])

    db_session.expire_all()
    original_counts = _declared_difficulty_counts(db_session.get(QuestionnaireSession, session_id))
    assert original_counts[QuestionDifficulty.HARD] == 3

    for _ in range(2):
        authenticated_client.get(f"/uaa/{FSE01_SLUG}/practice")
        authenticated_client.get(session_url)
        db_session.expire_all()
        reloaded_counts = _declared_difficulty_counts(db_session.get(QuestionnaireSession, session_id))
        assert reloaded_counts == original_counts


def test_other_subjects_selection_is_byte_for_byte_unaffected_by_difficulty_priority(db_session):
    """« Préserve les autres matières » (demande explicite) : l'adaptation générique du
    moteur (`app.v1.bank._prioritize_by_difficulty`, `app.v1.session_service.
    compose_selection`) ne doit RIEN changer pour une matière qui ne déclare encore aucune
    difficulté — vérifié directement (résultat byte-for-byte identique, même graine
    aléatoire), pas seulement supposé parce que la précondition `difficulty_declared is
    None` est vraie aujourd'hui."""
    import random as random_module

    from app.v1.bank import (
        _prioritize_by_difficulty,
        import_mc01_legacy_to_bank,
        select_bank_questions,
    )

    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    questions = db_session.query(Question).filter_by(uaa_id=mc01.id).all()
    assert questions, "précondition : MC01 doit avoir des questions importées"
    assert all(q.difficulty_declared is None for q in questions), (
        "précondition : Informatique AMPCR ne déclare encore aucune difficulté"
    )

    # `_prioritize_by_difficulty` : no-op strict, quelle que soit la difficulté demandée.
    assert _prioritize_by_difficulty(questions, None) == questions
    assert _prioritize_by_difficulty(questions, SessionDifficultyRequest.HARD) == questions

    # `compose_selection` : résultat identique avec la même graine aléatoire, avec ou sans
    # difficulté transmise.
    random_module.seed(1234)
    without_difficulty = compose_selection(list(questions), 10)
    random_module.seed(1234)
    with_difficulty = compose_selection(list(questions), 10, difficulty=SessionDifficultyRequest.HARD)
    assert [q.id for q in without_difficulty] == [q.id for q in with_difficulty]

    # `select_bank_questions` : même garantie, bout en bout (requête + priorisation).
    # Comparaison par ENSEMBLE, pas par ordre : l'ordre lui-même dépend de `ORDER BY
    # RANDOM()` côté SQLite (pas du module `random` de Python — `random.seed()` n'a donc
    # aucune prise dessus, déjà le cas avant ce ticket), jamais une garantie de ce module ;
    # la garantie réelle de non-régression est que l'ENSEMBLE renvoyé ne change pas.
    user = _user(db_session, email="ampcr-no-regression@example.invalid")
    pool_without = select_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc01.id, limit=30
    )
    pool_with = select_bank_questions(
        db_session, user_id=user.id, module_id=ampcr.id, uaa_id=mc01.id, limit=30,
        difficulty=SessionDifficultyRequest.HARD,
    )
    assert {q.id for q in pool_without} == {q.id for q in pool_with}

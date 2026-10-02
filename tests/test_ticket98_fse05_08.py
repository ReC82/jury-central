"""Ticket #98 — Formation sociale et économique : FSE05 « Image, vie privée et données
personnelles », FSE06 « Droits et comportements illicites en ligne », FSE07 « Analyser un
dossier médiatique », FSE08 « La Belgique : État et niveaux de pouvoir ».

Même moteur, mêmes conventions que FSE01-FSE04 (tickets #96/#97, voir
`tests/test_ticket96_fse01.py`/`tests/test_ticket97_fse02_04.py` pour la preuve exhaustive
du mécanisme générique partagé — pas répétée ici en entier) : théorie/entraînement/examen
réutilisant le moteur V1, difficulté réellement effective, sévérité distincte, reprise,
résultats.

Nouveauté ticket #98 : FSE05, FSE06 et FSE08 mobilisent des affirmations juridiques et
institutionnelles réelles (droit à l'image, comportements en ligne, organisation de l'État
belge), vérifiées auprès de sources belges officielles et référencées dans
`app.v1.fse05_course`/`fse06_course`/`fse08_course` (§ Sources officielles vérifiées) et dans
le rapport docs/claude-reports — vérifié ici par la présence de ces sections dans le contenu
publié, pas par une revérification des faits eux-mêmes (hors périmètre d'un test automatisé).
FSE08 est le premier cours du thème « Le citoyen et l'État » (les cours précédents relevaient
tous du thème « Interactions médiatiques »).

Aucun appel OpenAI réel : `FakeAIProvider`/`_UnconfiguredProvider` partout."""

import re
from collections import Counter

import pytest

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.models import UAA, Module, Subject
from app.seed import seed
from app.v1.ai_bridge import CORRECTABLE_TYPES
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.fse_bank import (
    import_fse05_to_bank,
    import_fse06_to_bank,
    import_fse07_to_bank,
    import_fse08_to_bank,
)
from app.v1.fse_plan import FSE_MODULE_CODE, FSE_PLAN_BY_CODE, FSE_SUBJECT_NAME
from app.v1.models import (
    Question,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    SourceDocumentVersion,
    User,
)
from app.v1.session_service import (
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    get_session_build_job,
    run_correction_job,
    run_session_build_job,
    start_session,
)

COURSES = {
    "FSE05": {"slug": "fse-fse05", "title": "Image, vie privée et données personnelles", "importer": import_fse05_to_bank},
    "FSE06": {"slug": "fse-fse06", "title": "Droits et comportements illicites en ligne", "importer": import_fse06_to_bank},
    "FSE07": {"slug": "fse-fse07", "title": "Analyser un dossier médiatique", "importer": import_fse07_to_bank},
    "FSE08": {"slug": "fse-fse08", "title": "La Belgique : État et niveaux de pouvoir", "importer": import_fse08_to_bank},
}


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


# =============================================================================================
# 1. Plan / registre
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_course_registered_in_fse_plan(code):
    assert code in FSE_PLAN_BY_CODE
    plan = FSE_PLAN_BY_CODE[code]
    assert plan.title == COURSES[code]["title"]
    assert plan.slug == COURSES[code]["slug"]


def test_fse08_is_first_citoyen_theme_course():
    """FSE01-FSE07 relèvent tous du thème « Interactions médiatiques » ; FSE08 est le
    premier cours du thème « Le citoyen et l'État » (ticket #98)."""
    for code in ("FSE01", "FSE02", "FSE03", "FSE04", "FSE05", "FSE06", "FSE07"):
        assert "Médias" in FSE_PLAN_BY_CODE[code].theme
    assert "Citoyen" in FSE_PLAN_BY_CODE["FSE08"].theme


# =============================================================================================
# 2. Matière / module / UAA — FSE01-08 seedés dans l'ordre, idempotent
# =============================================================================================


def test_fse01_to_fse08_seeded_in_order(db_session):
    """Tickets #99-#101 ont ajouté FSE09-FSE17 après FSE08 (voir
    tests/test_ticket99_fse09_12.py et suivants) : ce test reste focalisé sur la
    non-régression de l'ordre FSE01->FSE08 (ticket #98)."""
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaas = db_session.query(UAA).filter_by(module_id=module.id).order_by(UAA.position).all()
    assert [u.code for u in uaas[:8]] == [
        "FSE01", "FSE02", "FSE03", "FSE04", "FSE05", "FSE06", "FSE07", "FSE08",
    ]
    assert all(u.is_published for u in uaas[:8])


def test_fse_seed_is_idempotent_with_eight_courses(db_session):
    """Tickets #99-#101 ont ajouté FSE09-FSE17 (17 UAA au total, voir les fichiers de test
    dédiés) : ce test vérifie seulement que FSE01-FSE08 restent présents et idempotents."""
    seed()
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaa_codes = {u.code for u in db_session.query(UAA).filter_by(module_id=module.id).all()}
    assert {"FSE01", "FSE02", "FSE03", "FSE04", "FSE05", "FSE06", "FSE07", "FSE08"} <= uaa_codes


def test_module_listing_shows_all_eight_courses_in_order(client, db_session):
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = subject.modules[0]
    response = client.get(f"/modules/{module.slug}")
    assert response.status_code == 200
    text = response.text
    titles = [
        "Communiquer : le schéma de communication",
        "Les médias et leurs financements",
        "Identités, traces numériques et appartenance",
        "Normes, valeurs et influence sociale",
        "Image, vie privée et données personnelles",
        "Droits et comportements illicites en ligne",
        "Analyser un dossier médiatique",
        "La Belgique : État et niveaux de pouvoir",
    ]
    positions = [text.find(title) for title in titles]
    assert all(p != -1 for p in positions), "les 8 cours doivent être listés"
    assert positions == sorted(positions), "les 8 cours doivent être listés dans l'ordre FSE01->FSE08"


# =============================================================================================
# 3. Cours — contenu réel par cours, sources officielles vérifiées référencées
# =============================================================================================


def test_fse05_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse05")
    assert response.status_code == 200
    text = response.text
    for notion in ("droit à l'image", "prise de vue", "diffusion", "sujet principal", "personne accessoire", "donnée personnelle", "finalité"):
        assert notion in text
    assert "provisoire" not in text.lower()
    assert "stub" not in text.lower()
    # Ticket #98 : affirmations juridiques vérifiées et référencées (§ Sources).
    assert "Sources officielles vérifiées" in text
    assert "autoriteprotectiondonnees.be" in text
    assert "consulté le 2026-10-01" in text


def test_fse06_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse06")
    assert response.status_code == 200
    text = response.text
    for notion in ("cyberharcèlement", "injure", "calomnie", "menace", "discrimination", "usurpation d'identité", "intrusion informatique", "liberté d'expression"):
        assert notion in text
    assert "provisoire" not in text.lower()
    # Ticket #98 : jamais de qualification pénale ni de peine figée (pas de numéro
    # d'article ni de durée de peine citée, même si le mot « article » apparaît pour
    # rappeler explicitement de ne jamais en citer).
    assert not re.search(r"article\s+\d", text, re.IGNORECASE)
    assert not re.search(r"\bart\.?\s*\d", text, re.IGNORECASE)
    assert "Sources officielles vérifiées" in text
    assert "safeonweb.be" in text


def test_fse07_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse07")
    assert response.status_code == 200
    text = response.text
    for notion in ("fait", "interprétation", "opinion", "fiabilité", "enjeu juridique", "enjeu sociologique", "conclusion argumentée"):
        assert notion in text
    assert "Athénée du Parc" in text
    assert "provisoire" not in text.lower()


def test_fse08_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse08")
    assert response.status_code == 200
    text = response.text
    for notion in ("monarchie constitutionnelle", "démocratie parlementaire", "séparation des pouvoirs", "Région", "Communauté", "commune", "décret", "ordonnance"):
        assert notion in text
    assert "provisoire" not in text.lower()
    assert "Sources officielles vérifiées" in text
    assert "lachambre.be" in text


@pytest.mark.parametrize("slug", ["fse-fse05", "fse-fse06", "fse-fse07", "fse-fse08"])
def test_hidden_answers_use_details_collapsed_by_default(client, db_session, slug):
    seed()
    response = client.get(f"/uaa/{slug}")
    assert "<details>" in response.text
    assert "Voir la correction expliquée" in response.text


# =============================================================================================
# 4. Banque — par cours : idempotente, types corrects, pas de document orphelin, isolée
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_bank_import_is_idempotent_and_uses_only_relevant_types(db_session, code):
    seed()
    info = COURSES[code]
    uaa = db_session.query(UAA).filter_by(slug=info["slug"]).first()
    first = info["importer"](db_session, uaa.module, uaa)
    second = info["importer"](db_session, uaa.module, uaa)
    assert first == 14
    assert second == 0
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    assert len(questions) == 14
    for question in questions:
        assert question.current_version.question_type in CORRECTABLE_TYPES
    assert all(q.module.code == FSE_MODULE_CODE for q in questions), "isolation : jamais mélangé avec une autre matière"


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_no_orphan_document_dependent_questions(db_session, code):
    seed()
    info = COURSES[code]
    uaa = db_session.query(UAA).filter_by(slug=info["slug"]).first()
    info["importer"](db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    checked = 0
    for question in questions:
        doc_id = question.current_version.content_json.get("source_document_version_id")
        if doc_id:
            checked += 1
            assert db_session.get(SourceDocumentVersion, doc_id) is not None
    assert checked >= 4


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_difficulty_distribution_is_7_4_3(db_session, code):
    seed()
    info = COURSES[code]
    uaa = db_session.query(UAA).filter_by(slug=info["slug"]).first()
    info["importer"](db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    counts = Counter(q.difficulty_declared for q in questions)
    assert counts == {
        QuestionDifficulty.EASY: 7,
        QuestionDifficulty.MEDIUM: 4,
        QuestionDifficulty.HARD: 3,
    }


# =============================================================================================
# 5. Difficulté réellement effective (héritée du correctif ticket #96 review) — vérifiée
#    explicitement pour chaque nouveau cours, pas seulement supposée parce que le moteur
#    est partagé.
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_difficulty_filters_served_questions_in_normal_practice_session(db_session, code):
    seed()
    info = COURSES[code]
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE).first()
    uaa = db_session.query(UAA).filter_by(slug=info["slug"]).first()
    info["importer"](db_session, module, uaa)

    def run(difficulty, email):
        user = _user(db_session, email=email)
        session = start_session(
            db_session, user=user, module_id=module.id, uaa_id=uaa.id, uaa_code=code,
            mode=SessionMode.PRACTICE, difficulty=difficulty,
            provider=_UnconfiguredProvider(), question_count=10,
        )
        return Counter(sq.question_version.question.difficulty_declared for sq in session.session_questions)

    easy_counts = run(SessionDifficultyRequest.EASY, f"{code}-easy@example.invalid")
    hard_counts = run(SessionDifficultyRequest.HARD, f"{code}-hard@example.invalid")

    assert easy_counts[QuestionDifficulty.EASY] == 7
    assert hard_counts[QuestionDifficulty.HARD] == 3
    assert easy_counts != hard_counts


# =============================================================================================
# 6. Parcours complet — un aller-retour HTTP réel par cours (théorie déjà couverte § 3)
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_full_exam_flow_with_difficulty_and_severity(authenticated_client, db_session, monkeypatch, code):
    seed()
    info = COURSES[code]
    fake = _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, db_session, info["slug"], "exam", "hard")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    total = len(session.session_questions)

    _answer_all_and_submit(authenticated_client, session_url, total, db_session, fake, severity=2)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status == SessionStatus.COMPLETED
    assert session.difficulty_requested == SessionDifficultyRequest.HARD
    assert session.parameters_json["severity"] == 2
    assert len(fake.semantic_calls) <= 1

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert f"/uaa/{info['slug']}" in results.text


@pytest.mark.parametrize("code", ["FSE05", "FSE06", "FSE07", "FSE08"])
def test_settings_persist_across_resume(authenticated_client, db_session, monkeypatch, code):
    seed()
    info = COURSES[code]
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, db_session, info["slug"], "practice", "easy")
    session_id = int(session_url.rsplit("/", 1)[-1])

    landing = authenticated_client.get(f"/uaa/{info['slug']}/practice")
    assert "Reprendre l'entraînement en cours" in landing.text
    assert session_url in landing.text

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.difficulty_requested == SessionDifficultyRequest.EASY
    assert session.status.value == "in_progress"


# =============================================================================================
# 7. Non-régression — FSE01-04 et les autres matières restent inchangés
# =============================================================================================


def test_fse01_to_fse04_still_work_after_fse05_08_added(authenticated_client, db_session, monkeypatch):
    # Ticket #82 (connexions concurrentes SQLite) : jamais appeler un importeur de banque
    # directement via la fixture `db_session` ici — la route HTTP ci-dessous déclenche déjà
    # `_ensure_bank_seeded` sur sa PROPRE connexion (`get_db`), une seconde connexion
    # concurrente sur le même fichier SQLite produirait "database is locked".
    seed()
    _patch_fake_provider(monkeypatch)
    for slug, title in [
        ("fse-fse01", "Communiquer : le schéma de communication"),
        ("fse-fse02", "Les médias et leurs financements"),
        ("fse-fse03", "Identités, traces numériques et appartenance"),
        ("fse-fse04", "Normes, valeurs et influence sociale"),
    ]:
        response = authenticated_client.get(f"/uaa/{slug}")
        assert response.status_code == 200
        assert title in response.text

    session_url = _start_session(authenticated_client, db_session, "fse-fse01", "practice", "medium")
    assert session_url.startswith("/sessions/")


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

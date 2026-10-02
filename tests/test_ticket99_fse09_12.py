"""Ticket #99 — Formation sociale et économique : FSE09 « Qui décide de quoi ? », FSE10
« Élections et participation citoyenne », FSE11 « Partis politiques et choix argumenté »,
FSE12 « Le budget de l'État ».

Même moteur, mêmes conventions que FSE01-FSE08 (tickets #96-#98, voir
`tests/test_ticket96_fse01.py`/`tests/test_ticket98_fse05_08.py` pour la preuve exhaustive
du mécanisme générique partagé — pas répétée ici en entier) : théorie/entraînement/examen
réutilisant le moteur V1, difficulté réellement effective, sévérité distincte, reprise,
résultats.

Nouveauté ticket #99 : FSE09 (compétences), FSE10 (élections) et FSE11 (partis) mobilisent
des affirmations juridiques/institutionnelles réelles, vérifiées auprès de sources belges
officielles et référencées dans `app.v1.fse09_course`/`fse10_course`/`fse11_course`
(§ Sources officielles vérifiées) et dans le rapport docs/claude-reports. FSE12 reste
purement conceptuel (budget), sans vérification externe nécessaire au-delà de l'exclusion
stricte de l'IPP (jamais calculée ni déclarée).

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
    import_fse09_to_bank,
    import_fse10_to_bank,
    import_fse11_to_bank,
    import_fse12_to_bank,
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
    "FSE09": {"slug": "fse-fse09", "title": "Qui décide de quoi ?", "importer": import_fse09_to_bank},
    "FSE10": {"slug": "fse-fse10", "title": "Élections et participation citoyenne", "importer": import_fse10_to_bank},
    "FSE11": {"slug": "fse-fse11", "title": "Partis politiques et choix argumenté", "importer": import_fse11_to_bank},
    "FSE12": {"slug": "fse-fse12", "title": "Le budget de l'État", "importer": import_fse12_to_bank},
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


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
def test_course_registered_in_fse_plan(code):
    assert code in FSE_PLAN_BY_CODE
    plan = FSE_PLAN_BY_CODE[code]
    assert plan.title == COURSES[code]["title"]
    assert plan.slug == COURSES[code]["slug"]


# =============================================================================================
# 2. Matière / module / UAA — FSE09-12 seedés dans l'ordre, idempotent
# =============================================================================================


def test_fse09_to_fse12_seeded_in_order(db_session):
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaas = db_session.query(UAA).filter_by(module_id=module.id).order_by(UAA.position).all()
    codes = [u.code for u in uaas]
    assert codes[8:12] == ["FSE09", "FSE10", "FSE11", "FSE12"]
    assert all(u.is_published for u in uaas[8:12])


def test_fse_seed_is_idempotent_with_fse09_12(db_session):
    seed()
    seed()
    subject = db_session.query(Subject).filter_by(name=FSE_SUBJECT_NAME).first()
    module = db_session.query(Module).filter_by(code=FSE_MODULE_CODE, subject_id=subject.id).first()
    uaa_codes = {u.code for u in db_session.query(UAA).filter_by(module_id=module.id).all()}
    assert {"FSE09", "FSE10", "FSE11", "FSE12"} <= uaa_codes


# =============================================================================================
# 3. Cours — contenu réel par cours, sources officielles vérifiées référencées
# =============================================================================================


def test_fse09_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse09")
    assert response.status_code == 200
    text = response.text
    for notion in ("compétence", "niveau fédéral", "Région", "Communauté", "matières personnalisables"):
        assert notion in text
    assert "provisoire" not in text.lower()
    assert "Sources officielles vérifiées" in text
    assert "lachambre.be" in text


def test_fse10_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse10")
    assert response.status_code == 200
    text = response.text
    for notion in ("scrutin proportionnel", "procuration", "vote blanc", "vote nul", "témoin du dépouillement", "pétition", "consultation populaire"):
        assert notion in text
    assert "provisoire" not in text.lower()
    assert "Sources officielles vérifiées" in text
    assert "2026-10-01" in text
    # Ticket #99 : vote obligatoire non uniforme — ne jamais généraliser sans préciser.
    assert "Flandre" in text


def test_fse11_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse11")
    assert response.status_code == 200
    text = response.text
    for notion in ("famille politique", "socialiste", "libérale", "écologiste", "axe gauche-centre-droite"):
        assert notion in text
    for party in ("PS", "MR", "Ecolo", "Les Engagés", "PTB", "Vlaams Belang"):
        assert party in text
    assert "provisoire" not in text.lower()
    assert "Sources officielles vérifiées" in text
    assert "brusselstimes.com" in text
    # Ticket #99 : jamais d'opinion personnelle demandée à l'élève.
    assert "opinion personnelle" in text


def test_fse12_course_page_is_real_content(client, db_session):
    seed()
    response = client.get("/uaa/fse-fse12")
    assert response.status_code == 200
    text = response.text
    for notion in ("recette fiscale", "recette parafiscale", "dépense de fonctionnement", "solde budgétaire", "déficit", "dette"):
        assert notion in text
    assert "provisoire" not in text.lower()
    # Ticket #96/#99 : l'IPP n'est jamais calculée ni déclarée.
    assert "IPP" in text
    assert not re.search(r"calcul(e|er|é)?\s+(l'|ton |son )?IPP", text, re.IGNORECASE)


@pytest.mark.parametrize("slug", ["fse-fse09", "fse-fse10", "fse-fse11", "fse-fse12"])
def test_hidden_answers_use_details_collapsed_by_default(client, db_session, slug):
    seed()
    response = client.get(f"/uaa/{slug}")
    # Ticket #115 : les corrigés utilisent <details class="jc-exercise-correction">
    # (toujours l'élément natif <details>, sans l'attribut "open" — fermé par défaut).
    assert "<details" in response.text
    assert "<details open" not in response.text
    assert "Voir le corrigé" in response.text


# =============================================================================================
# 4. Banque — par cours : idempotente, types corrects, pas de document orphelin, isolée
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
def test_bank_has_no_near_duplicate_questions(db_session, code):
    """Ticket #102 (contrôle de couverture) : l'audit a révélé des paires de questions
    quasi-identiques dans des banques FSE déjà livrées (prompts réutilisés mot pour mot
    pour deux ensembles différents, voir `app.v1.dedup.is_near_duplicate`) — corrigées dans
    ce ticket. Garde de non-régression explicite."""
    from app.v1.dedup import is_near_duplicate, question_signature

    seed()
    info = COURSES[code]
    uaa = db_session.query(UAA).filter_by(slug=info["slug"]).first()
    info["importer"](db_session, uaa.module, uaa)
    questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
    sigs = [question_signature(q.current_version.question_type, q.current_version.content_json) for q in questions]
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            assert not is_near_duplicate(sigs[i], sigs[j]), f"questions {i} et {j} de {code} sont quasi-identiques"


# =============================================================================================
# 5. Difficulté réellement effective
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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
# 6. Parcours complet
# =============================================================================================


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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


@pytest.mark.parametrize("code", ["FSE09", "FSE10", "FSE11", "FSE12"])
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
# 7. Non-régression — FSE01-08 et les autres matières restent inchangés
# =============================================================================================


def test_fse01_still_works_after_fse09_12_added(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/uaa/fse-fse01")
    assert response.status_code == 200
    assert "Communiquer : le schéma de communication" in response.text

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

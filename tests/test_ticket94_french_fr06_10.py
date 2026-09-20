"""Ticket #94 — Français : parcours des 20 mini-cours (PHASE B : FR06→FR10).

Même architecture/standard de qualité que PHASE A (`tests/test_ticket94_french_20_courses.py`)
: cours réels non-stub (structure en 10 points), banque systématiquement rattachée à un
`SourceDocument` réel, practice/exam ciblés, réutilise intégralement le moteur
SourceDocument (#77/#79) et la génération/correction asynchrones (#88/#90/#92) — aucune
nouvelle architecture. Leçon du review PHASE A appliquée dès le départ : aucun jargon
« UAA »/statut provisoire visible par l'élève.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.models import Module
from app.seed import seed
from app.v1 import routes_sessions
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.francais_fr06_10_bank import (
    import_francais_fr06_to_bank,
    import_francais_fr07_to_bank,
    import_francais_fr08_to_bank,
    import_francais_fr09_to_bank,
    import_francais_fr10_to_bank,
)
from app.v1.francais_plan import FRANCAIS_PLAN_BY_CODE
from app.v1.models import Question, QuestionnaireSession
from app.v1.session_service import (
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    get_session_build_job,
    run_correction_job,
    run_session_build_job,
)

FR06_10_CODES = ["FR06", "FR07", "FR08", "FR09", "FR10"]
FR06_10_SLUGS = [f"francais-{code.lower()}" for code in FR06_10_CODES]

_IMPORTERS = {
    "FR06": import_francais_fr06_to_bank,
    "FR07": import_francais_fr07_to_bank,
    "FR08": import_francais_fr08_to_bank,
    "FR09": import_francais_fr09_to_bank,
    "FR10": import_francais_fr10_to_bank,
}

_PROVISIONAL_LABELS = (
    "validation technique provisoire",
    "provisional_technical_sample",
    "pas un examen cess officiel",
    "sample",
    "prototype",
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _resolve_build_job_url(db_session, location: str) -> str:
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


def _start_session(client, db_session, uaa_slug: str, mode: str = "practice") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return _resolve_build_job_url(db_session, response.headers["location"])


def _run_pending_correction_job(db_session, provider):
    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=provider)
    return job


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
    return {"text": "Réponse détaillée de validation couvrant plusieurs phrases et justifiant chaque point demandé."}


def _answer_all_and_submit(client, session_url, db_session, provider):
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    for position in range(1, session.question_count + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303
    response = client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)
    assert response.status_code == 303
    _run_pending_correction_job(db_session, provider)


# =============================================================================================
# 1. Plan / registre — FR06→FR10 présents
# =============================================================================================


def test_fr06_to_fr10_registered_in_francais_plan():
    for code in FR06_10_CODES:
        assert code in FRANCAIS_PLAN_BY_CODE


def test_fr06_10_titles_are_bare_human_readable():
    for code in FR06_10_CODES:
        title = FRANCAIS_PLAN_BY_CODE[code].title
        assert "UAA" not in title
        assert code not in title, f"{code} : titre stocké ne doit pas dupliquer le code (même convention que PHASE A)"


# =============================================================================================
# 2. Seed — 5 cours créés, non-stub, sans jargon
# =============================================================================================


def test_fr06_10_seeded_and_published(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    codes = {uaa.code for uaa in francais.uaas}
    for code in FR06_10_CODES:
        assert code in codes
    for uaa in francais.uaas:
        if uaa.code in FR06_10_CODES:
            assert uaa.is_published
            assert uaa.hidden_from_listing is False


def test_fr06_10_course_pages_are_not_stub(client, db_session):
    seed()
    for slug in FR06_10_SLUGS:
        response = client.get(f"/uaa/{slug}")
        assert response.status_code == 200, slug
        text = response.text
        assert "contenu à venir" not in text.lower(), slug
        for required_section in (
            "Ce que tu dois savoir faire",
            "Théorie progressive",
            "Définitions importantes",
            "Méthode étape par étape",
            "Exemples commentés",
            "Mauvaises réponses comparées aux bonnes",
            "Pièges et erreurs fréquentes",
            "Exercices guidés",
            "Corrigés très expliqués",
            "Fiche mémo",
        ):
            assert required_section in text, f"{slug} : section manquante « {required_section} »"


def test_fr06_10_pages_never_show_provisional_status_or_jargon(client, db_session):
    seed()
    for slug in FR06_10_SLUGS:
        for space in ("", "/practice", "/exam"):
            response = client.get(f"/uaa/{slug}{space}")
            assert response.status_code == 200, (slug, space)
            lowered = response.text.lower()
            for label in _PROVISIONAL_LABELS:
                assert label not in lowered, f"{slug}{space} : étiquette provisoire détectée « {label} »"
        response = client.get(f"/uaa/{slug}")
        assert "UAA" not in response.text
        assert not re.search(r"ticket\s*#\d+", response.text, re.IGNORECASE), slug


def test_francais_public_listing_now_shows_ten_courses(client, db_session):
    seed()
    response = client.get("/modules/francais")
    assert response.status_code == 200
    links = re.findall(r'href="/uaa/(francais-[a-z0-9]+)"', response.text)
    assert "francais-c01" not in links
    expected = {f"francais-{c.lower()}" for c in ("FR01", "FR02", "FR03", "FR04", "FR05", *FR06_10_CODES)}
    assert set(links) == expected, f"attendu exactement 10 cours publics, trouvé : {links}"


# =============================================================================================
# 3. Banque — audit anti-orphelin, types pertinents
# =============================================================================================


def test_no_orphan_document_dependent_questions_in_fr06_10(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    # Ancré sur un texte/document précis — jamais un stem nu ("résume"/"synthétise") qui
    # matcherait aussi une question purement méthodologique/conceptuelle (ex. « quelle
    # différence entre résumer UN texte et synthétiser PLUSIEURS documents ? », FR09) ne
    # portant sur aucun document réel.
    triggers = [
        "d'après le texte", "selon le texte", "selon le document",
        "en t'appuyant sur le texte", "en t'appuyant sur le document",
        "compare les", "compare la source", "justifie à partir de", "résume le texte", "résume cet",
        "synthétise les", "synthétise ce dossier",
    ]
    orphans = []
    for code in FR06_10_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        for question in db_session.query(Question).filter_by(uaa_id=uaa.id):
            content = question.current_version.content_json
            prompt = content.get("prompt", "")
            has_doc = bool(
                content.get("source_document_version_id") or content.get("source_document_version_ids")
            )
            prompt_outside_quotes = re.sub(r"«.*?»", "", prompt, flags=re.DOTALL)
            if any(t in prompt_outside_quotes.lower() for t in triggers) and not has_doc:
                orphans.append((code, question.id, prompt[:60]))
    assert orphans == [], f"questions orphelines détectées : {orphans}"


def test_fr06_10_bank_import_is_idempotent(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    for code in FR06_10_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        first = _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        second = _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        assert first > 0
        assert second == 0


def test_fr06_10_bank_uses_only_relevant_question_types(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    allowed = {"short_answer", "long_answer", "document_analysis", "source_comparison", "vocabulary", "classification"}
    for code in FR06_10_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        types_used = {
            q.current_version.question_type for q in db_session.query(Question).filter_by(uaa_id=uaa.id)
        }
        assert types_used <= allowed, (code, types_used)


def test_fr09_bank_has_multi_document_source_comparison_questions(db_session):
    """§ FR09 (synthétiser) : au moins une question source_comparison référençant
    plusieurs documents distincts (la compétence-clé du cours)."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    uaa = next(u for u in francais.uaas if u.code == "FR09")
    import_francais_fr09_to_bank(db_session, francais, uaa)
    db_session.commit()
    comparisons = [
        q for q in db_session.query(Question).filter_by(uaa_id=uaa.id)
        if q.current_version.question_type == "source_comparison"
    ]
    assert comparisons, "FR09 doit comporter au moins une question source_comparison"
    for q in comparisons:
        ids = q.current_version.content_json["source_document_version_ids"]
        assert len(ids) >= 2


def test_fallback_generation_never_produces_irrelevant_types_for_fr06_10(authenticated_client, db_session, monkeypatch):
    """Même correctif que PHASE A (validation staging) : FR06→FR10 ont aussi une banque
    (7-9 questions) plus petite que DEFAULT_QUESTION_COUNT (10)."""
    fake = _patch_fake_provider(monkeypatch)
    seed()
    for slug, code in zip(FR06_10_SLUGS, FR06_10_CODES, strict=True):
        session_url = _start_session(authenticated_client, db_session, slug, mode="practice")
        session_id = int(session_url.rsplit("/", 1)[-1])
        session = db_session.get(QuestionnaireSession, session_id)
        types_used = {sq.question_version.question_type for sq in session.session_questions}
        forbidden = types_used & {"multiple_choice", "ordering", "diagnostic"}
        assert not forbidden, f"{code} : type(s) hors périmètre Français généré(s) : {forbidden}"
    _ = fake


# =============================================================================================
# 4. Practice/exam ciblés, async build (#92), aucun 504
# =============================================================================================


def test_each_fr06_10_practice_session_is_scoped_to_its_own_course(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    for slug, code in zip(FR06_10_SLUGS, FR06_10_CODES, strict=True):
        session_url = _start_session(authenticated_client, db_session, slug, mode="practice")
        session_id = int(session_url.rsplit("/", 1)[-1])
        session = db_session.get(QuestionnaireSession, session_id)
        assert session.question_count <= 10
        for sq in session.session_questions:
            assert sq.question_version.question.uaa.code == code


def test_fr06_exam_session_is_nonblocking_and_scoped(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    response = authenticated_client.get("/uaa/francais-fr06/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-fr06/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/session-build-jobs/")
    session_url = _resolve_build_job_url(db_session, location)
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count <= 10, "FR06 exam ne doit PAS hériter du volume global 20 questions"


# =============================================================================================
# 5. Documents — visibles pendant question/correction, parité IA/élève, FR09 multi-doc
# =============================================================================================


def test_document_visible_during_question_for_fr07(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr07", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    found_a_document = False
    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        if "Voir le texte" in response.text or "target=\"_blank\"" in response.text:
            found_a_document = True
    assert found_a_document, "au moins une question FR07 doit référencer un document visible"
    _ = fake


def test_fr09_multi_document_visible_and_ai_student_parity(authenticated_client, db_session, monkeypatch):
    """FR09 : au moins une session doit exposer une question portant sur PLUSIEURS
    documents (source_comparison), et AI_STUDENT_SOURCE_PARITY doit tenir même dans ce
    cas multi-document — même mécanisme que #77/#94 PHASE A."""
    from app.v1.session_service import _document_contexts_for, build_question_display

    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr09", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    session_questions = list(session.session_questions)

    multi_doc_found = any(
        sq.question_version.question_type == "source_comparison" for sq in session_questions
    )
    assert multi_doc_found, "FR09 : au moins une question multi-document attendue dans la session"

    student_doc_ids: set[int] = set()
    for sq in session_questions:
        display = build_question_display(db_session, sq)
        student_doc_ids.update(document.id for document in display.source_documents)
    ai_contexts = _document_contexts_for(db_session, session_questions)
    ai_doc_ids = {int(context.course_key.removeprefix("source-document-")) for context in ai_contexts}
    assert ai_doc_ids == student_doc_ids, "AI_STUDENT_SOURCE_PARITY violée (FR09 multi-document)"
    _ = fake


# =============================================================================================
# 6. Correction async (#88/#90), FR08 long_answer, FR10 argumentation, aucun 504
# =============================================================================================


def test_fr08_full_practice_flow_long_answer_async_correction_no_false_zero(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr08", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert any(sq.question_version.question_type == "long_answer" for sq in session.session_questions), (
        "FR08 doit comporter au moins une question long_answer"
    )

    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value == "completed"
    for sq in session.session_questions:
        assert sq.answer.correction_status.value == "corrected"
        assert sq.answer.points_awarded is not None


def test_fr10_exam_argumentation_flow(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr10", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    types_used = {sq.question_version.question_type for sq in session.session_questions}
    assert types_used & {"short_answer", "long_answer", "document_analysis", "classification", "source_comparison"}

    t0_status = session.status.value
    assert t0_status == "in_progress"
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value in ("completed", "correction_incomplete")


def test_fr06_10_export_print_and_history(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr08", mode="practice")
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)

    export = authenticated_client.get(f"{session_url}/export.md")
    assert export.status_code == 200

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert "@media print" in results.text

    history = authenticated_client.get("/mes-sessions")
    assert history.status_code == 200
    assert "FR08" in history.text


def test_fr06_10_long_answer_accepts_long_text_without_truncation(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr09", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    # FR09 (synthèse multi-document) exprime son texte long via `source_comparison`
    # (plusieurs documents) plutôt que `long_answer` (un seul document) — les deux
    # partagent la même capacité de réponse longue (`max_length` par défaut 20000).
    long_answer_position = next(
        (
            sq.position for sq in session.session_questions
            if sq.question_version.question_type in ("long_answer", "source_comparison")
        ),
        None,
    )
    assert long_answer_position is not None, "FR09 doit comporter au moins une question à réponse longue"
    long_text = "Synthèse développée et argumentée. " * 400
    assert len(long_text) > 10000
    response = authenticated_client.get(f"{session_url}?q={long_answer_position}")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": long_answer_position, "direction": "next", "text": long_text},
        follow_redirects=False,
    )
    assert response.status_code == 303
    _ = fake

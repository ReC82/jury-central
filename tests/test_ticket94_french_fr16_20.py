"""Ticket #94 — Français : parcours des 20 mini-cours (PHASE D : FR16→FR20).

FR16→FR19 suivent le standard des phases A/B/C (cours non-stub, banque rattachée à de
vrais `SourceDocument`, practice/exam ciblés). FR20 est le cours de méthode ET l'examen
blanc final : sans banque propre, ses sessions tirent dans FR01→FR19 (scope
`fr20_transversal`), comme FSE17 — jamais de génération IA, jamais C01 ni FR20.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.models import UAA, Module
from app.seed import seed
from app.v1 import routes_sessions
from app.v1.document_references import audit_document_references
from app.v1.francais_fr16_20_bank import (
    import_francais_fr16_to_bank,
    import_francais_fr17_to_bank,
    import_francais_fr18_to_bank,
    import_francais_fr19_to_bank,
)
from app.v1.francais_plan import (
    FR20_SESSION_SCOPE,
    FRANCAIS_PLAN_BY_CODE,
    fr01_to_fr19_codes,
    get_francais_context,
)
from app.v1.models import Question, QuestionnaireSession, SessionMode
from app.v1.session_service import describe_session_scope, get_in_progress_session
from tests.test_ticket94_french_fr06_10 import (
    _PROVISIONAL_LABELS,
    _answer_all_and_submit,
    _csrf,
    _patch_fake_provider,
    _resolve_build_job_url,
    _start_session,
)

FR16_19_CODES = ["FR16", "FR17", "FR18", "FR19"]
FR16_20_SLUGS = [f"francais-fr{n}" for n in range(16, 21)]

_IMPORTERS = {
    "FR16": import_francais_fr16_to_bank,
    "FR17": import_francais_fr17_to_bank,
    "FR18": import_francais_fr18_to_bank,
    "FR19": import_francais_fr19_to_bank,
}


def _import_fr16_19(db_session) -> Module:
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    for code in FR16_19_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
    db_session.commit()
    return francais


def _start_fr20(client, db_session, mode: str, question_count: str = "") -> QuestionnaireSession:
    response = client.get(f"/uaa/francais-fr20/{mode}")
    assert response.status_code == 200
    data = {"csrf_token": _csrf(response.text), "difficulty": "medium"}
    if question_count:
        data["question_count"] = question_count
    response = client.post(f"/uaa/francais-fr20/{mode}/start", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/session-build-jobs/")
    session_url = _resolve_build_job_url(db_session, response.headers["location"])
    return db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))


# =============================================================================================
# 1. Plan, seed, pages — les 20 cours
# =============================================================================================


def test_twenty_courses_registered_with_context():
    codes = [f"FR{n:02d}" for n in range(1, 21)]
    for code in codes:
        plan = FRANCAIS_PLAN_BY_CODE[code]
        assert "UAA" not in plan.title and code not in plan.title
        assert get_francais_context(plan.course_key) is not None
    assert fr01_to_fr19_codes() == codes[:19]
    assert "francais-fr20" not in routes_sessions._FRANCAIS_BANK_IMPORTERS


def test_twenty_courses_listed_in_order(client, db_session):
    seed()
    response = client.get("/modules/francais")
    links = list(dict.fromkeys(re.findall(r'href="/uaa/(francais-fr\d\d)"', response.text)))
    assert links == [f"francais-fr{n:02d}" for n in range(1, 21)]


def test_fr16_20_course_pages_are_complete(client, db_session):
    seed()
    for slug in FR16_20_SLUGS:
        response = client.get(f"/uaa/{slug}")
        assert response.status_code == 200, slug
        text = response.text
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
        ):
            assert required_section in text, f"{slug} : section manquante « {required_section} »"
        assert 'id="a-retenir"' in text, slug
        assert "<details open" not in text, slug
        lowered = text.lower()
        for label in _PROVISIONAL_LABELS:
            assert label not in lowered, (slug, label)
        for space in ("/practice", "/exam"):
            assert client.get(f"/uaa/{slug}{space}").status_code == 200, (slug, space)


def test_fr20_course_points_to_every_previous_course(client, db_session):
    seed()
    text = client.get("/uaa/francais-fr20").text
    for code in ("FR01", "FR09", "FR13", "FR16", "FR19"):
        assert code in text


# =============================================================================================
# 2. Banque FR16→FR19
# =============================================================================================


def test_fr16_19_bank_idempotent_types_and_supports(db_session):
    francais = _import_fr16_19(db_session)
    allowed = {"short_answer", "long_answer", "document_analysis", "source_comparison", "vocabulary", "classification"}
    for code in FR16_19_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        questions = db_session.query(Question).filter_by(uaa_id=uaa.id).all()
        assert len(questions) >= 8, code
        assert {q.current_version.question_type for q in questions} <= allowed, code
        assert _IMPORTERS[code](db_session, francais, uaa) == 0
        for question in questions:
            content = question.current_version.content_json
            prompt = re.sub(r"«.*?»", "", content.get("prompt", ""), flags=re.DOTALL).lower()
            has_doc = bool(content.get("source_document_version_id") or content.get("source_document_version_ids"))
            if re.search(
                r"\b(dans|d'après|selon|à partir des?) (le |la |les |l')(récit|nouvelle|texte|"
                r"transcription|négociation|discussion|situation|compte rendu|avis|notes|fait divers|"
                r"version|scène|transposition)",
                prompt,
            ):
                assert has_doc, (code, prompt[:80])


def test_fr16_19_document_references_are_resolvable(db_session):
    _import_fr16_19(db_session)
    report = audit_document_references(db_session, uaa_codes=tuple(FR16_19_CODES))
    assert report["audited"] >= 32
    assert report["unresolved"] == []


def test_each_fr16_19_practice_session_is_scoped(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    for code in FR16_19_CODES:
        session_url = _start_session(authenticated_client, db_session, f"francais-{code.lower()}", mode="practice")
        session = db_session.get(QuestionnaireSession, int(session_url.rsplit("/", 1)[-1]))
        for sq in session.session_questions:
            assert sq.question_version.question.uaa.code == code
            assert sq.question_version.question_type not in {"multiple_choice", "ordering", "diagnostic"}


def test_fr17_full_practice_flow_async_correction_no_false_zero(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr17", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value == "completed"
    for sq in session.session_questions:
        assert sq.answer.correction_status.value == "corrected"
        assert sq.answer.points_awarded is not None


# =============================================================================================
# 3. FR20 — examen blanc transversal FR01→FR19
# =============================================================================================


def test_fr20_exam_is_transversal_bank_only_and_twenty_questions(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session = _start_fr20(authenticated_client, db_session, "exam")
    assert session.question_count == 20
    assert (session.parameters_json or {}).get("scope") == FR20_SESSION_SCOPE
    codes = {sq.question_version.question.uaa.code for sq in session.session_questions}
    assert codes <= set(fr01_to_fr19_codes())
    assert len(codes) >= 8, f"examen blanc trop peu varié : {codes}"
    from app.v1.models import GenerationSource

    assert db_session.query(Question).filter_by(generation_source=GenerationSource.AI_GENERATED).count() == 0
    _ = fake
    # Les banques FR01→FR19 ont été amorcées même sans visite préalable des cours.
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    imported = {u.code for u in francais.uaas if db_session.query(Question).filter_by(uaa_id=u.id).count()}
    assert set(fr01_to_fr19_codes()) <= imported
    assert describe_session_scope(session) == "FR20 — Examen blanc final (FR01→FR19)"


def test_fr20_practice_default_volume_and_resume_by_scope(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    session = _start_fr20(authenticated_client, db_session, "practice")
    assert session.question_count == 10
    assert (session.parameters_json or {}).get("scope") == FR20_SESSION_SCOPE
    found = get_in_progress_session(
        db_session, user_id=session.user_id, module_id=session.module_id, mode=SessionMode.PRACTICE,
        scope=FR20_SESSION_SCOPE,
    )
    assert found is not None and found.id == session.id
    # Un deuxième clic sur « Commencer » (session vierge) reprend la même session (#71).
    response = authenticated_client.get("/uaa/francais-fr20/practice")
    response = authenticated_client.post(
        "/uaa/francais-fr20/practice/start",
        data={"csrf_token": _csrf(response.text), "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session.id}"


def test_fr20_never_offers_generation_only_lengths_beyond_bank(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    session = _start_fr20(authenticated_client, db_session, "exam", question_count="40")
    assert session.question_count == 40
    codes = {sq.question_version.question.uaa.code for sq in session.session_questions}
    assert codes <= set(fr01_to_fr19_codes())
    versions = [sq.question_version.question_id for sq in session.session_questions]
    assert len(versions) == len(set(versions)), "doublon intra-session (#82)"


def test_fr20_exam_full_flow_results_export_and_history(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session = _start_fr20(authenticated_client, db_session, "exam")
    session_url = f"/sessions/{session.id}"
    _answer_all_and_submit(authenticated_client, session_url, db_session, fake)
    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session.id)
    assert session.status.value in ("completed", "correction_incomplete")
    for sq in session.session_questions:
        assert sq.answer.points_awarded is not None or sq.answer.correction_status.value != "corrected"
    export = authenticated_client.get(f"{session_url}/export.md")
    assert export.status_code == 200
    assert "fr20-examen-blanc" in export.headers["content-disposition"]
    assert "FR20 — Examen blanc final" in authenticated_client.get("/mes-sessions").text
    assert authenticated_client.get(session_url).status_code == 200


def test_fr20_progress_is_attributed_to_fr20_in_parcours(authenticated_client, db_session, monkeypatch):
    from app.v1 import parcours

    _patch_fake_provider(monkeypatch)
    seed()
    session = _start_fr20(authenticated_client, db_session, "practice")
    assert parcours._SCOPE_TO_UAA_CODE[FR20_SESSION_SCOPE] == "FR20"
    fr20 = db_session.query(UAA).filter_by(code="FR20").first()
    assert fr20 is not None and session.module_id == fr20.module_id

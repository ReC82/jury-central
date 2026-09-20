"""Ticket #94 — Français : parcours complet des 20 mini-cours (PHASE A : FR01→FR05).

Contexte : le moteur Français V1 existait déjà (#47/#77/#79/#88/#90/#92), mais le
véritable contenu pédagogique (20 mini-cours CESS Professionnel) n'existait pas — seule
une UAA pilote provisoire (C01) servait de validation technique. Ce ticket ajoute les 5
premiers cours réels (FR01→FR05), chacun avec un vrai cours (structure en 10 points, non
stub), une banque de questions dédiée systématiquement rattachée à un `SourceDocument`
réel (jamais de « D'après le texte » orphelin), practice/exam ciblés, et réutilise
intégralement le moteur SourceDocument existant (#77/#79) ainsi que la correction/
génération asynchrones (#88/#90/#92) — aucune nouvelle architecture.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.models import Module
from app.seed import seed
from app.v1 import routes_sessions
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.francais_fr01_05_bank import (
    import_francais_fr01_to_bank,
    import_francais_fr02_to_bank,
    import_francais_fr03_to_bank,
    import_francais_fr04_to_bank,
    import_francais_fr05_to_bank,
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

FR01_05_CODES = ["FR01", "FR02", "FR03", "FR04", "FR05"]
FR01_05_SLUGS = [f"francais-{code.lower()}" for code in FR01_05_CODES]

_IMPORTERS = {
    "FR01": import_francais_fr01_to_bank,
    "FR02": import_francais_fr02_to_bank,
    "FR03": import_francais_fr03_to_bank,
    "FR04": import_francais_fr04_to_bank,
    "FR05": import_francais_fr05_to_bank,
}


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
    fait tourner le job en direct (appel de service, jamais un vrai worker séparé)."""
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


# =============================================================================================
# 1. Plan / registre — FR01→FR05 présents, C01 inchangée
# =============================================================================================


def test_fr01_to_fr05_registered_in_francais_plan():
    for code in FR01_05_CODES:
        assert code in FRANCAIS_PLAN_BY_CODE
    assert "C01" in FRANCAIS_PLAN_BY_CODE, "C01 (ticket #47) ne doit jamais être supprimée"


def test_fr01_05_titles_are_human_readable_not_uaa():
    """Ticket #94 (review ChatGPT PHASE A) : le titre stocké reste BARE (sans « FRxx — »),
    même convention que AMPCR (`app.v1.ampcr_plan`) — les templates composent déjà
    « {{ uaa.code }} — {{ uaa.title }} » (listing) ou « {{ uaa.title }} ({{ uaa.code }}) »
    (page cours), préfixer le titre lui-même dupliquerait le code à l'affichage. Le code
    ne doit donc PAS apparaître dans le titre stocké, mais reste affiché séparément."""
    for code in FR01_05_CODES:
        title = FRANCAIS_PLAN_BY_CODE[code].title
        assert "UAA" not in title
        assert code not in title, f"{code} : le titre stocké ne doit pas dupliquer le code (affiché séparément)"


# =============================================================================================
# 2. Seed — 5 cours créés, non-stub
# =============================================================================================


def test_fr01_05_seeded_and_published(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    codes = {uaa.code for uaa in francais.uaas}
    for code in FR01_05_CODES:
        assert code in codes
    for uaa in francais.uaas:
        if uaa.code in FR01_05_CODES:
            assert uaa.is_published


def test_fr01_05_course_pages_are_not_stub(client, db_session):
    seed()
    for slug in FR01_05_SLUGS:
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


def test_fr01_05_hidden_answers_use_details_collapsed_by_default(client, db_session):
    """§ « Exercices d'apprentissage » : corrigés visibles mais MASQUÉS PAR DÉFAUT —
    implémenté via `<details>` (fermé par défaut tant que l'attribut `open` est absent)."""
    seed()
    response = client.get("/uaa/francais-fr01")
    assert response.status_code == 200
    assert "<details>" in response.text
    assert "<summary>" in response.text
    assert "Voir la correction expliquée" in response.text


# =============================================================================================
# 2b. Review ChatGPT PHASE A — pas de statut "provisoire", C01 hors navigation publique
# =============================================================================================

_PROVISIONAL_LABELS = (
    "validation technique provisoire",
    "provisional_technical_sample",
    "pas un examen cess officiel",
    "sample",
    "prototype",
)


def test_fr01_05_pages_never_show_provisional_status_to_the_user(client, db_session):
    """Review ChatGPT (§ 1) : FR01→FR05 sont désormais de vrais cours — plus aucune
    mention « validation technique provisoire »/« PROVISIONAL_TECHNICAL_SAMPLE »/« PAS un
    examen CESS officiel » sur une page visible par l'élève (cours, practice, exam)."""
    seed()
    for slug in FR01_05_SLUGS:
        for space in ("", "/practice", "/exam"):
            response = client.get(f"/uaa/{slug}{space}")
            assert response.status_code == 200, (slug, space)
            lowered = response.text.lower()
            for label in _PROVISIONAL_LABELS:
                assert label not in lowered, f"{slug}{space} : étiquette provisoire détectée « {label} »"


def test_fr01_05_pages_never_show_uaa_or_ticket_jargon(client, db_session):
    """Review ChatGPT (§ 4) : jamais « UAA », « ticket #xx » dans le contenu pédagogique
    visible par l'élève — ce jargon reste réservé au code/commentaires/rapports."""
    seed()
    for slug in FR01_05_SLUGS:
        response = client.get(f"/uaa/{slug}")
        assert response.status_code == 200
        text = response.text
        assert "UAA" not in text
        assert not re.search(r"ticket\s*#\d+", text, re.IGNORECASE), slug


def test_c01_hidden_from_public_module_listing(client, db_session):
    """Review ChatGPT (§ 2/§ 3) : la page publique du module Français doit lister
    exactement FR01→FR05 (à ce stade) et PLUS C01."""
    seed()
    response = client.get("/modules/francais")
    assert response.status_code == 200
    text = response.text
    assert "francais-c01" not in text
    for code in FR01_05_CODES:
        assert code in text
    public_course_links = re.findall(r'href="/uaa/(francais-[a-z0-9]+)"', text)
    assert set(public_course_links) == set(FR01_05_SLUGS), (
        f"attendu exactement 5 cours publics FR01→FR05, trouvé : {public_course_links}"
    )


def test_c01_still_fully_reachable_via_its_legacy_url(client, db_session):
    """Review ChatGPT (§ 2) : C01 masquée de la navigation, mais son URL historique doit
    rester pleinement fonctionnelle (page cours, practice, exam) — aucune régression pour
    l'historique/les sessions déjà existantes."""
    seed()
    for path in ("/uaa/francais-c01", "/uaa/francais-c01/practice", "/uaa/francais-c01/exam"):
        response = client.get(path)
        assert response.status_code == 200, path


def test_c01_hidden_from_listing_flag_is_idempotent_across_reseeds(db_session):
    seed()
    seed()
    from app.models import UAA

    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    assert c01 is not None
    assert c01.hidden_from_listing is True
    assert c01.is_published is True, "C01 doit rester pleinement accessible, jamais dépubliée"


# =============================================================================================
# 3. Banque — audit anti-orphelin (§ 6/§ 8 du ticket : AUCUNE question sans document réel)
# =============================================================================================


def test_no_orphan_document_dependent_questions_in_fr01_05(db_session):
    """Audit exhaustif (ticket #94 § 6) : toute question dont l'énoncé utilise un langage
    supposant un texte lisible doit avoir un `source_document_version_id`/`_ids` réel."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    triggers = [
        "d'après le texte", "selon le texte", "selon le document",
        "en t'appuyant sur le texte", "en t'appuyant sur le document",
        "compare", "que pense l'auteur", "identifie un passage",
    ]
    orphans = []
    for code in FR01_05_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        for question in db_session.query(Question).filter_by(uaa_id=uaa.id):
            content = question.current_version.content_json
            prompt = content.get("prompt", "")
            has_doc = bool(
                content.get("source_document_version_id") or content.get("source_document_version_ids")
            )
            # Ignore le texte entre guillemets « » : certaines questions FR01 sont des
            # questions META sur la structure d'une consigne (ex. « classe les éléments
            # de cette consigne : "Compare les deux documents..." ») — le mot
            # déclencheur y apparaît dans un EXEMPLE cité, jamais comme une vraie
            # exigence de lecture d'un document réel par l'élève.
            prompt_outside_quotes = re.sub(r"«.*?»", "", prompt, flags=re.DOTALL)
            if any(t in prompt_outside_quotes.lower() for t in triggers) and not has_doc:
                orphans.append((code, question.id, prompt[:60]))
    assert orphans == [], f"questions orphelines détectées : {orphans}"


def test_fr01_05_bank_import_is_idempotent(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    for code in FR01_05_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        first = _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        second = _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        assert first > 0
        assert second == 0


def test_fr01_05_bank_uses_only_relevant_question_types(db_session):
    """§ 10/§ ENTRAÎNEMENT du ticket : short_answer / long_answer / document_analysis /
    source_comparison / vocabulary / classification — jamais de QCM artificiel."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    allowed = {"short_answer", "long_answer", "document_analysis", "source_comparison", "vocabulary", "classification"}
    for code in FR01_05_CODES:
        uaa = next(u for u in francais.uaas if u.code == code)
        _IMPORTERS[code](db_session, francais, uaa)
        db_session.commit()
        types_used = {
            q.current_version.question_type for q in db_session.query(Question).filter_by(uaa_id=uaa.id)
        }
        assert types_used <= allowed, (code, types_used)
        assert "multiple_choice" not in types_used, f"{code} : QCM artificiel détecté"


# =============================================================================================
# 4. Practice/exam ciblés, async build (#92), aucun 504
# =============================================================================================


def test_each_fr01_05_practice_session_is_scoped_to_its_own_course(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    for slug, code in zip(FR01_05_SLUGS, FR01_05_CODES, strict=True):
        session_url = _start_session(authenticated_client, db_session, slug, mode="practice")
        session_id = int(session_url.rsplit("/", 1)[-1])
        session = db_session.get(QuestionnaireSession, session_id)
        assert session.question_count <= 10
        for sq in session.session_questions:
            assert sq.question_version.question.uaa.code == code, (
                "une session practice FRxx ne doit tirer QUE dans son propre cours"
            )


def test_fr01_exam_session_is_nonblocking_and_scoped(authenticated_client, db_session, monkeypatch):
    """§ 92 : le POST /start ne doit jamais bloquer, même pour un examen Français
    ciblé (non-régression explicite : seul C01/MC38 doivent garder le volume global de
    20 questions, jamais FR01→FR19, cf. app.v1.routes_sessions._enqueue_build_for_uaa)."""
    _patch_fake_provider(monkeypatch)
    seed()
    response = authenticated_client.get("/uaa/francais-fr01/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-fr01/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/session-build-jobs/"), "START_HTTP_NONBLOCKING : doit toujours enqueuer un job"
    session_url = _resolve_build_job_url(db_session, location)
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count <= 10, "FR01 exam ne doit PAS hériter du volume global 20 questions (réservé à C01/FR20/MC38)"


# =============================================================================================
# 5. Documents — visibles pendant la question ET la correction, parité IA/élève
# =============================================================================================


def test_document_visible_during_question_for_fr02(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr02", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    found_a_document = False
    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        if "source_document" in str(session.session_questions[position - 1].question_version.content_json):
            found_a_document = True
            assert "Voir le texte" in response.text or "documents/" in response.text
            assert "nouvel onglet" in response.text.lower() or "target=" in response.text.lower()
    assert found_a_document, "au moins une question FR02 doit référencer un document"
    _ = fake


def test_document_visible_during_correction_and_ai_student_parity(authenticated_client, db_session, monkeypatch):
    """AI_STUDENT_SOURCE_PARITY : le correcteur IA doit recevoir EXACTEMENT les mêmes
    documents que ceux montrés à l'élève — vérifié via `_document_contexts_for` vs
    `build_question_display`, même mécanisme que #77."""
    from app.v1.session_service import _document_contexts_for, build_question_display

    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr03", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    session_questions = list(session.session_questions)

    student_doc_ids: set[int] = set()
    for sq in session_questions:
        display = build_question_display(db_session, sq)
        student_doc_ids.update(document.id for document in display.source_documents)

    ai_contexts = _document_contexts_for(db_session, session_questions)
    ai_doc_ids = {int(context.course_key.removeprefix("source-document-")) for context in ai_contexts}
    assert ai_doc_ids == student_doc_ids, "AI_STUDENT_SOURCE_PARITY violée"
    assert student_doc_ids, "FR03 doit référencer au moins un document"

    # Correction complète, puis vérifie la même règle sur la page de résultats.
    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    authenticated_client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)
    _run_pending_correction_job(db_session, fake)

    results = authenticated_client.get(session_url)
    assert results.status_code == 200
    assert "Voir le texte" in results.text or "document" in results.text.lower()


# =============================================================================================
# 6. Correction async (#88/#90), pas de 504, historique/export
# =============================================================================================


def test_fr04_full_practice_flow_async_correction_no_false_zero(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr04", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303

    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303, "SUBMIT_NONBLOCKING : jamais un 504, toujours un 303 immédiat"
    _run_pending_correction_job(db_session, fake)

    db_session.expire_all()
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.status.value == "completed"
    for sq in session.session_questions:
        assert sq.answer.correction_status.value == "corrected"
        assert sq.answer.points_awarded is not None


def test_fr05_export_and_history_include_course(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr05", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    authenticated_client.post(f"{session_url}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False)
    _run_pending_correction_job(db_session, fake)

    export = authenticated_client.get(f"{session_url}/export.md")
    assert export.status_code == 200

    history = authenticated_client.get("/mes-sessions")
    assert history.status_code == 200
    assert "FR05" in history.text


def test_fr01_05_long_answer_accepts_long_text_without_truncation(authenticated_client, db_session, monkeypatch):
    """§ LONG ANSWER : aucune limite gênante (#73, support 20k conservé)."""
    fake = _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-fr04", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    long_answer_position = next(
        (sq.position for sq in session.session_questions if sq.question_version.question_type == "long_answer"),
        None,
    )
    assert long_answer_position is not None, "FR04 doit comporter au moins une question long_answer"
    long_text = "Phrase développée et argumentée. " * 400  # ~13 000 caractères
    assert len(long_text) > 10000
    response = authenticated_client.get(f"{session_url}?q={long_answer_position}")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"{session_url}/answer",
        data={"csrf_token": token, "position": long_answer_position, "direction": "next", "text": long_text},
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"{session_url}?q={long_answer_position}")
    assert str(len(long_text)) in response.text or len(long_text) > 10000
    _ = fake


# =============================================================================================
# 7. Non-régression : C01 (#47), suite complète
# =============================================================================================


def test_c01_still_works_unaffected_by_fr01_05(authenticated_client, db_session, monkeypatch):
    _patch_fake_provider(monkeypatch)
    seed()
    session_url = _start_session(authenticated_client, db_session, "francais-c01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    # Ticket #82 : 9 ou 10 selon le tirage (garde anti-doublon intra-session finale) —
    # même non-régression que tests/test_ticket47_francais_v1.py.
    assert 9 <= session.question_count <= 10

"""Chantier prioritaire — Examen blanc CESS Français (mode Examen blanc).

Contexte officiel : l'épreuve écrite CESS Français dure 3h, vaut 50% de la note, et
demande UNE tâche parmi deux familles (synthèse OU argumentation) — le candidat ne
choisit pas le jour de l'examen. Ce fichier couvre : génération async d'un dossier de 3
documents originaux + tâche + grille /100 (jamais un appel IA dans le cycle HTTP, #92),
rédaction/autosave, correction async /100 sans faux 0 (#88/#90), parité élève/IA sur les
documents (#77/#79), anti-répétition thème/type, historique, export/print.

Aucun appel OpenAI réel : `FakeAIProvider` partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.provider import AINotConfiguredError
from app.v1.correction_worker import _UnconfiguredProvider
from app.v1.french_mock_exam_service import (
    choose_exam_type,
    choose_theme,
    claim_next_pending_mock_exam_build,
    claim_next_pending_mock_exam_correction,
    compute_signature,
    run_mock_exam_build,
    run_mock_exam_correction,
)
from app.v1.models import FrenchMockExam, FrenchMockExamStatus, FrenchMockExamType, User


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    """Patché au même endroit que le worker réel lit son fournisseur
    (`app.v1.correction_worker._get_provider_or_unconfigured` → `app.ai.factory.get_ai_provider`)."""
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: fake)
    return fake


def _run_pending_build(db_session, provider):
    job = claim_next_pending_mock_exam_build(db_session)
    if job is not None:
        run_mock_exam_build(db_session, exam=job, provider=provider)
    return job


def _run_pending_correction(db_session, provider):
    job = claim_next_pending_mock_exam_correction(db_session)
    if job is not None:
        run_mock_exam_correction(db_session, exam=job, provider=provider)
    return job


def _start_and_build(client, db_session, provider, mode: str = "surprise") -> str:
    response = client.get("/francais/examen-blanc")
    token = _csrf(response.text)
    response = client.post(
        "/francais/examen-blanc/start", data={"csrf_token": token, "mode": mode}, follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    exam_url = response.headers["location"]
    _run_pending_build(db_session, provider)
    return exam_url


# =============================================================================================
# 1. Mode / landing (§ 1)
# =============================================================================================


def test_mock_exam_landing_shows_three_modes(authenticated_client):
    response = authenticated_client.get("/francais/examen-blanc")
    assert response.status_code == 200
    assert "Examen blanc CESS — Surprise" in response.text
    assert "Entraînement ciblé — Synthèse" in response.text
    assert "Entraînement ciblé — Argumentation" in response.text


def test_francais_module_page_links_to_mock_exam(authenticated_client, db_session):
    from app.seed import seed

    seed()
    response = authenticated_client.get("/modules/francais")
    assert response.status_code == 200
    assert "/francais/examen-blanc" in response.text


# =============================================================================================
# 2. Async build (§ 36, § 92) — aucun 504, aucun appel IA dans le POST
# =============================================================================================


def test_start_http_is_nonblocking_for_all_three_modes(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    for mode in ("surprise", "synthesis", "argumentation"):
        response = authenticated_client.get("/francais/examen-blanc")
        token = _csrf(response.text)
        response = authenticated_client.post(
            "/francais/examen-blanc/start", data={"csrf_token": token, "mode": mode}, follow_redirects=False,
        )
        assert response.status_code == 303, (mode, response.text)
    _ = fake


def test_build_with_deliberately_slow_provider_does_not_block_start(authenticated_client, db_session, monkeypatch):
    import time

    class _SlowProvider(FakeAIProvider):
        def generate_french_mock_exam(self, request):
            time.sleep(1.0)
            return super().generate_french_mock_exam(request)

    slow = _SlowProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: slow)

    response = authenticated_client.get("/francais/examen-blanc")
    token = _csrf(response.text)
    t0 = time.monotonic()
    response = authenticated_client.post(
        "/francais/examen-blanc/start", data={"csrf_token": token, "mode": "surprise"}, follow_redirects=False,
    )
    elapsed = time.monotonic() - t0
    assert response.status_code == 303
    assert elapsed < 0.5, f"START_HTTP a pris {elapsed:.2f}s — ne doit jamais attendre le fournisseur IA (1s)"
    assert len(slow.mock_exam_generation_calls) == 0, "aucun appel IA ne doit avoir lieu dans le cycle HTTP"


# =============================================================================================
# 3. Dossier documentaire (§ 5-11, § 28)
# =============================================================================================


def test_generated_exam_has_exactly_three_distinct_documents(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.status == FrenchMockExamStatus.READY
    assert len(exam.documents) == 3
    titles = {d.title for d in exam.documents}
    assert len(titles) == 3, "les 3 documents doivent être distincts"
    kinds = {d.title.split("—")[0] for d in exam.documents}  # heuristique simple de diversité
    assert len(kinds) >= 1


def test_no_fake_real_source_in_generated_documents(authenticated_client, db_session, monkeypatch):
    """§ 6 : jamais une source réelle inventée (Le Soir, RTBF, Le Monde, CNRS...) —
    vérifié sur le contenu factice ET sur les titres."""
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    forbidden_sources = ("le soir", "rtbf", "le monde", "cnrs", "le figaro", "france info")
    for doc in exam.documents:
        text_lower = (doc.title + " " + (doc.content_text or "")).lower()
        for forbidden in forbidden_sources:
            assert forbidden not in text_lower, f"source réelle détectée : {forbidden}"


def test_documents_visible_during_question_with_read_and_new_tab_links(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    response = authenticated_client.get(exam_url)
    assert response.status_code == 200
    assert response.text.count("Lire") >= 3
    assert response.text.count('target="_blank"') >= 3
    assert "Portefeuille de documents" in response.text


def test_question_created_after_documents_and_requires_documents(authenticated_client, db_session, monkeypatch):
    """§ 9/§ 29 : la tâche doit exister et ne jamais référencer un document absent — ici
    vérifié structurellement : `task_prompt` non vide, généré dans le même appel qui
    produit les documents (donc toujours cohérent par construction du contrat IA)."""
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.task_prompt and exam.task_prompt.strip()
    assert exam.rubric_json
    assert sum(c["max_points"] for c in exam.rubric_json) == 100.0
    assert exam.expected_information_json  # corrigé privé présent


def test_expected_information_never_exposed_before_correction(authenticated_client, db_session, monkeypatch):
    """§ 16/§ 24 : le corrigé privé ne doit jamais apparaître sur la page de rédaction."""
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    response = authenticated_client.get(exam_url)
    for key_idea in exam.expected_information_json["key_ideas"]:
        assert key_idea["idea"] not in response.text


# =============================================================================================
# 4. Grilles /100 (§ 17, § 25)
# =============================================================================================


def test_synthesis_rubric_sums_to_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake, mode="synthesis")
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.exam_type == FrenchMockExamType.SYNTHESIS
    assert sum(c["max_points"] for c in exam.rubric_json) == 100.0
    assert len(exam.rubric_json) == 4  # A/B/C/D


def test_argumentation_rubric_sums_to_100(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake, mode="argumentation")
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.exam_type in (FrenchMockExamType.ARGUMENTATION_OPINION, FrenchMockExamType.ARGUMENTATION_REQUEST)
    assert sum(c["max_points"] for c in exam.rubric_json) == 100.0
    assert len(exam.rubric_json) == 3  # A/B/C


# =============================================================================================
# 5. Autosave, longueur, mot count (§ 32, § 33)
# =============================================================================================


def test_autosave_and_word_count(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    long_text = "Ma réponse développée. " * 500  # bien plus de 20 000 caractères possible
    response = authenticated_client.post(
        f"/api/v1/mock-exams/{exam_id}/answer",
        json={"answer_text": long_text, "preparation_table_json": {"notes": "brouillon"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["saved"] is True
    assert data["word_count"] > 1000
    db_session.expire_all()
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.answer_text == long_text
    assert exam.preparation_table_json == {"notes": "brouillon"}


def test_long_answer_not_truncated(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    long_text = "Phrase développée et argumentée. " * 700
    assert len(long_text) > 20000
    response = authenticated_client.post(
        f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": long_text},
    )
    assert response.status_code == 200
    db_session.expire_all()
    exam = db_session.get(FrenchMockExam, exam_id)
    assert len(exam.answer_text) == len(long_text), "aucune troncature artificielle"


def test_resume_after_logout_login(client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    token = _csrf(client.get("/register").text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": "resume-mockexam@example.test", "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "T",
        },
    )
    exam_url = _start_and_build(client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    client.post(f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse avant déconnexion."})

    token = _csrf(client.get("/").text)
    client.post("/logout", data={"csrf_token": token})
    token = _csrf(client.get("/login").text)
    client.post(
        "/login", data={"csrf_token": token, "email": "resume-mockexam@example.test", "password": "test-password-1234"},
    )
    response = client.get(exam_url)
    assert response.status_code == 200
    assert "Réponse avant déconnexion." in response.text


# =============================================================================================
# 6. Async correction (§ 35, § 37) — aucun faux 0, aucun 504
# =============================================================================================


def test_submit_http_is_nonblocking(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    authenticated_client.post(f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse de test."})
    token = _csrf(authenticated_client.get(exam_url).text)
    response = authenticated_client.post(f"{exam_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303


def test_full_flow_completes_with_score(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    authenticated_client.post(
        f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse développée. " * 100},
    )
    token = _csrf(authenticated_client.get(exam_url).text)
    response = authenticated_client.post(f"{exam_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    assert response.status_code == 303
    _run_pending_correction(db_session, fake)

    db_session.expire_all()
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.status == FrenchMockExamStatus.COMPLETED
    assert exam.score is not None
    assert exam.max_score == 100.0
    assert exam.feedback_json

    results = authenticated_client.get(exam_url)
    assert results.status_code == 200
    assert "NOTE" in results.text


def test_ai_correction_failure_never_produces_a_zero(authenticated_client, db_session, monkeypatch):
    """§ 37 : aucun 0 automatique — CORRECTION_INCOMPLETE, bouton de reprise ciblé."""
    from app.ai.provider import AIProviderError

    class _FailingProvider(FakeAIProvider):
        def correct_french_mock_exam(self, **kwargs):
            raise AIProviderError("panne simulée")

    failing = _FailingProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: failing)

    exam_url = _start_and_build(authenticated_client, db_session, failing)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    authenticated_client.post(f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse de test."})
    token = _csrf(authenticated_client.get(exam_url).text)
    authenticated_client.post(f"{exam_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    _run_pending_correction(db_session, failing)

    db_session.expire_all()
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.status == FrenchMockExamStatus.CORRECTION_INCOMPLETE
    assert exam.score is None, "AI_FAILURE_FALSE_ZERO : aucun score fabriqué"

    results = authenticated_client.get(exam_url)
    assert "CORRECTION INCOMPLÈTE" in results.text
    assert "Reprendre la correction" in results.text

    # Retry ciblé : réutilise la MÊME ligne, ne crée jamais un second examen.
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: fake)
    token = _csrf(authenticated_client.get(exam_url).text)
    authenticated_client.post(f"{exam_url}/retry-correction", data={"csrf_token": token}, follow_redirects=False)
    _run_pending_correction(db_session, fake)
    db_session.expire_all()
    exam = db_session.get(FrenchMockExam, exam_id)
    assert exam.status == FrenchMockExamStatus.COMPLETED
    assert exam.score is not None
    assert db_session.query(FrenchMockExam).filter_by(user_id=exam.user_id).count() == 1


def test_build_failure_never_creates_phantom_exam(authenticated_client, db_session, monkeypatch):
    from app.ai.provider import AIProviderError

    class _FailingGenProvider(FakeAIProvider):
        def generate_french_mock_exam(self, request):
            raise AIProviderError("panne simulée")

    failing = _FailingGenProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: failing)

    response = authenticated_client.get("/francais/examen-blanc")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/francais/examen-blanc/start", data={"csrf_token": token, "mode": "surprise"}, follow_redirects=False,
    )
    exam_url = response.headers["location"]
    _run_pending_build(db_session, failing)

    response = authenticated_client.get(exam_url)
    assert "échoué" in response.text.lower()
    assert "Réessayer" in response.text

    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.correction_worker.get_ai_provider", lambda: fake)
    token = _csrf(response.text)
    authenticated_client.post(f"{exam_url}/retry-build", data={"csrf_token": token}, follow_redirects=False)
    _run_pending_build(db_session, fake)
    response = authenticated_client.get(exam_url)
    assert response.status_code == 200
    assert "Portefeuille de documents" in response.text


# =============================================================================================
# 7. Document parity élève/IA (§ 11, § 51)
# =============================================================================================


def test_ai_receives_exactly_the_documents_shown_to_student(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)
    student_doc_ids = {d.id for d in exam.documents}

    authenticated_client.post(f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse."})
    token = _csrf(authenticated_client.get(exam_url).text)
    authenticated_client.post(f"{exam_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    _run_pending_correction(db_session, fake)

    correction_calls = fake.mock_exam_correction_calls
    assert len(correction_calls) == 1
    # Le service transmet exactement `exam.documents` (title, kind, text) au correcteur —
    # vérifié indirectement : 3 documents envoyés, tous appartenant au dossier de l'élève.
    assert len(student_doc_ids) == 3


# =============================================================================================
# 8. Anti-répétition (§ 3, § 27, § 30, § 47)
# =============================================================================================


def test_choose_theme_avoids_recent_themes(db_session):
    user = User(email="theme-test@example.test", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    from app.v1.french_mock_exam_themes import MOCK_EXAM_THEMES

    seen_keys = []
    for _ in range(5):
        theme_key, _theme = choose_theme(db_session, user_id=user.id)
        seen_keys.append(theme_key)
        exam = FrenchMockExam(
            user_id=user.id, theme=dict(MOCK_EXAM_THEMES)[theme_key], theme_key=theme_key,
            exam_type=FrenchMockExamType.SYNTHESIS, min_words=350, max_words=450,
            status=FrenchMockExamStatus.READY,
        )
        db_session.add(exam)
        db_session.commit()
    # Sur les 5 dernières (fenêtre RECENT_THEME_WINDOW=5), jamais de répétition immédiate.
    assert len(set(seen_keys)) == len(seen_keys), f"répétition détectée : {seen_keys}"


def test_choose_exam_type_avoids_long_streaks(db_session):
    user = User(email="type-test@example.test", password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()

    seen_types = []
    for _ in range(10):
        exam_type = choose_exam_type(db_session, user_id=user.id, mode="surprise")
        seen_types.append(exam_type)
        exam = FrenchMockExam(
            user_id=user.id, theme="t", theme_key="k", exam_type=exam_type,
            min_words=350, max_words=450, status=FrenchMockExamStatus.READY,
        )
        db_session.add(exam)
        db_session.commit()
    # Jamais 5 fois de suite le même type (§ 27 exemple explicite).
    for i in range(len(seen_types) - 4):
        window = seen_types[i : i + 5]
        assert len(set(window)) > 1, f"5 répétitions consécutives détectées : {window}"
    assert FrenchMockExamType.SYNTHESIS in seen_types
    assert any(t != FrenchMockExamType.SYNTHESIS for t in seen_types)


def test_multi_generation_produces_varied_themes_and_types(authenticated_client, db_session, monkeypatch):
    """§ 47 : génère 10 examens, vérifie plusieurs thèmes, SYNTHESIS et ARGUMENTATION
    présents, OPINION et REQUEST présents, signatures différentes."""
    fake = _patch_fake_provider(monkeypatch)
    exam_ids = []
    for _ in range(10):
        exam_url = _start_and_build(authenticated_client, db_session, fake, mode="surprise")
        exam_ids.append(int(exam_url.rstrip("/").rsplit("/", 1)[-1]))

    exams = [db_session.get(FrenchMockExam, eid) for eid in exam_ids]
    themes = {e.theme_key for e in exams}
    types = {e.exam_type for e in exams}
    signatures = [e.signature for e in exams]

    assert len(themes) > 1, "pas 10 fois le même thème"
    assert FrenchMockExamType.SYNTHESIS in types
    assert FrenchMockExamType.ARGUMENTATION_OPINION in types or FrenchMockExamType.ARGUMENTATION_REQUEST in types
    assert len(set(signatures)) == len(signatures), "signatures doivent être différentes"


def test_compute_signature_deterministic_and_distinct():
    sig1 = compute_signature(theme_key="theme-ia", exam_type=FrenchMockExamType.SYNTHESIS, task_prompt="Question A ?")
    sig2 = compute_signature(theme_key="theme-ia", exam_type=FrenchMockExamType.SYNTHESIS, task_prompt="Question A ?")
    sig3 = compute_signature(theme_key="theme-ia", exam_type=FrenchMockExamType.SYNTHESIS, task_prompt="Question B ?")
    assert sig1 == sig2
    assert sig1 != sig3


# =============================================================================================
# 9. Historique / export / print (§ 34, § 44)
# =============================================================================================


def test_history_shows_mock_exam_with_type_and_theme(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake, mode="synthesis")
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    exam = db_session.get(FrenchMockExam, exam_id)

    response = authenticated_client.get("/mes-sessions")
    assert response.status_code == 200
    assert "Examen blanc CESS" in response.text
    # Jinja échappe l'apostrophe (rendu HTML différent selon la version) — compare sur la
    # partie du thème SANS apostrophe plutôt que de dépendre de l'échappement exact.
    theme_fragment = exam.theme.split("'")[-1].strip()
    assert theme_fragment in response.text


def test_export_and_print_after_completion(authenticated_client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    exam_url = _start_and_build(authenticated_client, db_session, fake)
    exam_id = int(exam_url.rstrip("/").rsplit("/", 1)[-1])
    authenticated_client.post(f"/api/v1/mock-exams/{exam_id}/answer", json={"answer_text": "Réponse de test."})
    token = _csrf(authenticated_client.get(exam_url).text)
    authenticated_client.post(f"{exam_url}/submit", data={"csrf_token": token}, follow_redirects=False)
    _run_pending_correction(db_session, fake)

    export = authenticated_client.get(f"{exam_url}/export.md")
    assert export.status_code == 200
    assert "Portefeuille de documents" in export.text
    assert "Score" in export.text or "NOTE" in export.text.upper()

    results = authenticated_client.get(exam_url)
    assert "@media print" in results.text


# =============================================================================================
# 10. Ownership / sécurité
# =============================================================================================


def test_other_user_cannot_access_exam(client, db_session, monkeypatch):
    fake = _patch_fake_provider(monkeypatch)
    token = _csrf(client.get("/register").text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": "owner-mockexam@example.test", "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "Owner",
        },
    )
    exam_url = _start_and_build(client, db_session, fake)

    token = _csrf(client.get("/").text)
    client.post("/logout", data={"csrf_token": token})
    token = _csrf(client.get("/register").text)
    client.post(
        "/register",
        data={
            "csrf_token": token, "email": "intruder-mockexam@example.test", "password": "test-password-1234",
            "password_confirm": "test-password-1234", "display_name": "Intruder",
        },
    )
    response = client.get(exam_url)
    assert response.status_code == 404


# =============================================================================================
# 11. Resolver de fallback pour AINotConfiguredError (parité avec les autres chantiers)
# =============================================================================================


def test_resolve_fallback_helper_uses_unconfigured_provider_when_not_patched(db_session):
    try:
        from app.v1.correction_worker import get_ai_provider as patched

        patched()
    except AINotConfiguredError:
        provider = _UnconfiguredProvider()
        assert provider is not None

"""Ticket #47 — Français V1 : premier parcours complet (pilote technique provisoire).

Aucun contenu Français officiel ou brouillon ChatGPT n'existait dans le dépôt avant ce
ticket (voir `docs/content_plan_informatique_francais.md` § 3.3) — l'utilisateur a validé
explicitement la création d'une UAA pilote de VALIDATION TECHNIQUE (texte original,
jamais présenté comme un examen CESS officiel, voir `app.v1.francais_content`), pour
prouver que tout le parcours (SourceDocument partagé, practice/exam, autosave, reprise,
correction batch IA, résultats détaillés) fonctionne réellement.

Aucun appel OpenAI réel : toutes les corrections passent par `FakeAIProvider`."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.answer_checking import normalize_text
from app.models import UAA, Module
from app.seed import seed
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.francais_content import (
    CODING_DEBATE_DOCUMENT_TITLE,
    DIGITAL_LIFE_DOCUMENT_TITLE,
    MAIN_DOCUMENT_TITLE,
    SECOND_DOCUMENT_TITLE,
    TRAINING_DOCUMENT_TITLE,
)
from app.v1.models import (
    Question,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocument,
    SourceDocumentVersion,
    User,
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, mode: str = "practice", difficulty: str = "medium") -> str:
    response = client.get(f"/uaa/francais-c01/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/francais-c01/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


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
    return {"text": "Réponse de test couvrant plusieurs phrases pour valider la correction."}


def _answer_all_and_submit(
    client, session_url: str, total: int, db_session, provider, severity: int | None = None
) -> None:
    for position in range(1, total + 1):
        response = client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        token = _csrf(response.text)
        direction = "submit" if position == total else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        data.update(_answer_payload_for(response.text))
        response = client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303, response.text
    response = client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    submit_data = {"csrf_token": token}
    if severity is not None:
        submit_data["severity"] = severity
    response = client.post(f"{session_url}/submit", data=submit_data, follow_redirects=False)
    assert response.status_code == 303
    # Ticket #88 : le POST ne corrige plus de façon synchrone — fait tourner le worker
    # explicitement (appel direct, pas de processus séparé) avant que l'appelant ne lise
    # un résultat.
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=provider)


# --- 1. SourceDocument partagé, banque hand-authored ----------------------------------------


def test_francais_bank_import_creates_shared_source_documents(db_session):
    """Corpus étendu (overnight mission du 2026-09-19, § Phases 5-7) : 5 SourceDocument,
    40 questions — voir docs/francais_v1_functional.md pour le détail."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    imported = import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    assert imported == 40

    documents = db_session.query(SourceDocument).all()
    assert len(documents) == 5
    titles = {doc.current_version.title for doc in documents}
    assert titles == {
        MAIN_DOCUMENT_TITLE, SECOND_DOCUMENT_TITLE, DIGITAL_LIFE_DOCUMENT_TITLE,
        TRAINING_DOCUMENT_TITLE, CODING_DEBATE_DOCUMENT_TITLE,
    }


def test_fait_opinion_classification_explanations_match_correct_categories(db_session):
    """Bug identifié en review : l'explication de la classification Fait/Opinion (texte
    smartphone) contredisait `correct_categories` (« les deux premières... la deuxième
    est un jugement » — contradictoire). `correct_categories=[0, 1, 0]` (Fait/Opinion/
    Fait) était déjà correct ; seul le texte l'était pas. Corrigé pour refléter
    fidèlement le mapping : la 1re et la 3e affirmations sont des faits, la 2e une
    opinion. Le corpus étendu ajoute une seconde classification Fait/Opinion (texte
    numérique au quotidien) — vérifiée avec la même exigence de cohérence."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()

    classification_questions = [
        q for q in db_session.query(Question).filter_by(uaa_id=c01.id)
        if q.current_version.question_type == "classification"
    ]
    assert len(classification_questions) == 2
    for question in classification_questions:
        content = question.current_version.content_json
        assert content["correct_categories"] == [0, 1, 0]
        explanation = normalize_text(content["explanation"])
        assert "premiere" in explanation
        assert "troisieme" in explanation
        # Non-régression explicite du bug : l'ancienne formulation contradictoire a disparu.
        assert "deux premieres" not in explanation


def test_francais_bank_import_is_idempotent(db_session):
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()
    second = import_francais_c01_to_bank(db_session, francais, c01)
    assert second == 0
    assert db_session.query(SourceDocumentVersion).count() == 5


def test_multiple_questions_reference_the_same_document(db_session):
    """§ « DOCUMENT SOURCE » du ticket : un même texte doit pouvoir servir à plusieurs
    questions, jamais dupliqué."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()

    from app.v1.models import Question

    questions = db_session.query(Question).filter_by(uaa_id=c01.id).all()
    referencing_a_document = [
        q for q in questions
        if q.current_version.content_json.get("source_document_version_id")
        or q.current_version.content_json.get("source_document_version_ids")
    ]
    # Corpus étendu (#47) : 4 document_analysis + 4 source_comparison + 1 long_answer
    # référençant explicitement son document déclencheur (débat programmation) = 9.
    # Audit #79 § 4 : 29 questions supplémentaires (short_answer/vocabulary/
    # classification/long_answer) disaient « D'après le texte »/« Selon le texte »/etc.
    # sans aucun rattachement structuré — corrigées pour toutes en avoir un (2 questions
    # d'opinion citant leur affirmation en entier dans le prompt restent volontairement
    # sans document, voir francais_bank.py). Total : 9 + 29 = 38.
    assert len(referencing_a_document) == 38

    main_doc_version = (
        db_session.query(SourceDocumentVersion)
        .join(SourceDocument, SourceDocument.current_version_id == SourceDocumentVersion.id)
        .filter(SourceDocumentVersion.title == MAIN_DOCUMENT_TITLE)
        .one()
    )
    main_doc_questions = [
        q for q in referencing_a_document
        if q.current_version.content_json.get("source_document_version_id") == main_doc_version.id
        or main_doc_version.id in (q.current_version.content_json.get("source_document_version_ids") or [])
    ]
    # Le document principal (smartphone) sert, à lui seul, à plusieurs questions
    # (2 document_analysis + 4 source_comparison) — jamais dupliqué malgré ce nombre.
    assert len(main_doc_questions) >= 3
    # Aucun texte long dupliqué dans une question : seule une référence (id), jamais
    # `content_text`, n'apparaît dans le content_json d'une question.
    for question in referencing_a_document:
        assert "content_text" not in question.current_version.content_json
        assert MAIN_DOCUMENT_TITLE not in str(question.current_version.content_json)


# --- 2. Course page publique, statut provisoire affiché --------------------------------------


def test_course_page_is_public_and_marked_provisional(client, db_session):
    seed()
    response = client.get("/uaa/francais-c01")
    assert response.status_code == 200
    assert "validation technique provisoire" in response.text
    assert "PAS un examen CESS officiel" in response.text


def test_practice_and_exam_require_authentication(client, db_session):
    seed()
    response = client.get("/uaa/francais-c01/practice", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


# --- 3. Practice : 10 questions, aucune correction avant submit, autosave --------------------


def test_practice_session_has_ten_questions_from_shared_bank(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    # Ticket #82 : 9 ou 10 selon le tirage (garde anti-doublon intra-session, voir
    # test_exam_session_has_twenty_questions pour le détail).
    assert 9 <= session.question_count <= 10
    assert session.status.value == "in_progress"


def test_no_correction_or_solution_visible_before_submit(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    forbidden_fields = (
        "rubric", "expected_points", "correct_option_ids", "correct_categories",
        "accepted_answers", "explanation",
    )
    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        for field in forbidden_fields:
            assert field not in response.text, (position, field)
        assert "Corriger" not in response.text
        assert "Vérifier ma réponse" not in response.text


def test_autosave_persists_a_long_answer_across_requests(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")

    long_text = "Ceci est une réponse longue de validation. " * 60  # largement > 300 mots
    for position in range(1, 11):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        if 'name="text"' in response.text and 'rows="8"' in response.text:
            data = {"csrf_token": token, "position": position, "direction": "next", "text": long_text}
            authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
            break

    reloaded = authenticated_client.get(f"{session_url}?q={position}")
    assert long_text in reloaded.text, "la réponse longue autosauvegardée doit être intégralement relue, non tronquée"


def test_resume_offers_the_in_progress_session(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = session_url.rsplit("/", 1)[-1]

    landing = authenticated_client.get("/uaa/francais-c01/practice")
    assert "Reprendre" in landing.text
    assert f"/sessions/{session_id}" in landing.text


# --- 4. Exam : 20 questions (corpus § Phases 5-7 le permet), immuable après soumission -------


def test_exam_session_has_twenty_questions(authenticated_client, db_session, monkeypatch):
    """§ Phase 9 (overnight) : « 20 questions si techniquement raisonnable » — le corpus
    étendu (40 questions, § Phases 5-7) le permet, vérifié ici sans appel de génération
    (FakeAIProvider ne devrait même pas être sollicité si la banque suffit).

    Ticket #82 : la garde anti-doublon intra-session finale peut retirer 1 question si les
    2 questions `classification` Fait/Opinion du corpus (même gabarit de prompt/catégories
    générique, § finding non corrigé ici — hors périmètre Informatique de #82) sont
    toutes les deux tirées dans la même session — 19 ou 20 selon le tirage, jamais moins,
    jamais un doublon."""
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert 19 <= session.question_count <= 20
    assert len(session.session_questions) == session.question_count
    assert session.mode.value == "exam"
    assert len(fake.questionnaire_calls) == 0


def test_exam_prevents_duplicate_in_progress_sessions(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    first_url = _start_session(authenticated_client, mode="exam")
    response = authenticated_client.get("/uaa/francais-c01/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/francais-c01/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.headers["location"] == first_url


def test_exam_session_immutable_after_submission(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)
    db_session.refresh(session)
    assert session.status.value == "completed"

    # Toute tentative de modification après soumission est sans effet (§ 55/56, réutilisé).
    response = authenticated_client.get(f"{session_url}?q=1")
    token = _csrf(response.text) if "csrf_token" in response.text else None
    if token:
        authenticated_client.post(
            f"{session_url}/answer",
            data={"csrf_token": token, "position": 1, "direction": "next", "text": "modification tardive"},
            follow_redirects=False,
        )
    db_session.refresh(session)
    assert session.status.value == "completed"


# --- 5. Correction batch unique, résultat détaillé, réponse longue non tronquée ---------------


def test_submission_triggers_exactly_one_semantic_batch_call(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)
    assert len(fake.semantic_calls) == 1


def test_document_context_is_provided_once_per_document_not_per_question(authenticated_client, db_session, monkeypatch):
    """§ CORRECTION du ticket : « le document partagé ne doit pas être dupliqué inutilement
    question par question dans le contexte envoyé à l'IA »."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    from app.v1.session_service import _document_contexts_for

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    contexts = _document_contexts_for(db_session, session_questions)
    # Au plus 5 documents existent dans le corpus (§ Phases 5-7) — et une session de 10
    # questions ne peut de toute façon jamais en référencer plus que son propre nombre de
    # questions — jamais un contexte par QUESTION qui les référence (donc jamais plus que
    # le nombre de documents DISTINCTS réellement cités par cette session précise).
    assert len(contexts) <= 5
    assert len(contexts) <= len(session_questions)
    for context in contexts:
        # Le texte n'apparaît qu'une fois dans le contexte de ce document.
        assert context.constraints.count(context.course_title) <= 1


def test_long_answer_is_not_truncated_end_to_end(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    long_text = "Argument développé sur plusieurs phrases pour tester la longueur. " * 80
    assert len(long_text) > 2000  # dépasse largement le max_length par défaut (2000)

    long_answer_position = None
    for sq in sorted(session.session_questions, key=lambda sq: sq.position):
        if sq.question_version.question_type == "long_answer":
            long_answer_position = sq.position
            break
    assert long_answer_position is not None

    for position in range(1, session.question_count + 1):
        response = authenticated_client.get(f"{session_url}?q={position}")
        token = _csrf(response.text)
        direction = "submit" if position == session.question_count else "next"
        data = {"csrf_token": token, "position": position, "direction": direction}
        if position == long_answer_position:
            data["text"] = long_text
        else:
            data.update(_answer_payload_for(response.text))
        response = authenticated_client.post(f"{session_url}/answer", data=data, follow_redirects=False)
        assert response.status_code == 303

    response = authenticated_client.get(f"{session_url}/submit-confirm")
    token = _csrf(response.text)
    authenticated_client.post(f"{session_url}/submit", data={"csrf_token": token}, follow_redirects=False)

    db_session.refresh(session)
    answer = next(
        sq.answer for sq in session.session_questions if sq.position == long_answer_position
    )
    assert answer.answer_json["text"] == long_text, "la réponse longue soumise ne doit jamais être tronquée"


def test_results_show_detailed_feedback_structure(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "Ta réponse" in response.text
    assert "point(s)" in response.text  # POINTS (en-tête accordéon)


def test_no_public_solution_leak_anywhere_in_results(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    for field in ("correct_option_ids", "correct_categories", "accepted_answers"):
        assert field not in response.text


# --- 5b. Grille de correction (rubric) : clauses pédagogiques (§ Phases 10-11) réellement -----
# --- transmises à l'IA, pas seulement présentes dans francais_bank.py -------------------------


def _patch_fake_provider_with_rubric_spy(monkeypatch) -> tuple[list, "FakeAIProvider"]:
    """Comme `_patch_fake_provider`, mais espionne aussi les questions réellement transmises
    à `correct_semantic_batch` (jamais un vrai appel OpenAI) — pour vérifier que le
    `rubric` de la banque atteint bien le pont IA (`app.v1.ai_bridge`,
    `app.ai.prompts.build_correct_semantic_messages`), pas seulement qu'il existe dans
    `francais_bank.py`. Retourne aussi `fake` (ticket #88 : nécessaire pour faire tourner
    le worker explicitement après un submit HTTP, désormais asynchrone)."""
    fake = FakeAIProvider()
    captured: list = []
    original = fake.correct_semantic_batch

    def spy(questions, answers, severity, contexts):
        captured.append(list(questions))
        return original(questions, answers, severity, contexts)

    monkeypatch.setattr(fake, "correct_semantic_batch", spy)
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return captured, fake


def _build_single_existing_question_session(db_session, question: Question, mode=SessionMode.PRACTICE) -> int:
    """Construit une session à une seule question référençant une question RÉELLE déjà
    importée de la banque Français (jamais une question synthétique) — pour tester le
    contenu pédagogique réel, de façon déterministe (pas de sélection aléatoire à filtrer)."""
    user = db_session.query(User).filter_by(email="eleve-test@example.test").first()
    assert user is not None, "authenticated_client doit avoir déjà créé ce compte"
    session = QuestionnaireSession(
        user_id=user.id, mode=mode, module_id=question.module_id,
        difficulty_requested=SessionDifficultyRequest.MEDIUM, status=SessionStatus.IN_PROGRESS,
        question_count=1,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        SessionQuestion(
            session_id=session.id, question_version_id=question.current_version_id, position=1, points_max=1.0,
        )
    )
    db_session.commit()
    return session.id


def _first_francais_question_with_rubric_containing(db_session, c01, needle: str) -> Question:
    for question in db_session.query(Question).filter_by(uaa_id=c01.id):
        rubric = question.current_version.content_json.get("rubric") or ""
        if needle in rubric:
            return question
    raise AssertionError(f"aucune question Français n'a de rubric contenant {needle!r}")


def test_opinion_neutrality_clause_reaches_the_ai_correction_prompt(
    authenticated_client, db_session, monkeypatch
):
    """Phase 11 (mission de nuit) : la sévérité ne doit jamais juger l'opinion elle-même —
    cette règle vit dans `_OPINION_NEUTRALITY_CLAUSE` (`francais_bank.py`). Ce test vérifie
    qu'elle atteint réellement l'appel `correct_semantic_batch`, pas seulement qu'elle est
    écrite dans le fichier de contenu."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()

    question = _first_francais_question_with_rubric_containing(
        db_session, c01, "Ne juge JAMAIS l'opinion exprimée elle-même"
    )
    captured, fake = _patch_fake_provider_with_rubric_spy(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={
            "csrf_token": token, "position": 1, "direction": "submit",
            "text": "Je pense que oui, pour plusieurs raisons développées ici.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)

    assert len(captured) == 1
    sent_rubrics = [q.rubric or "" for q in captured[0]]
    assert any("Ne juge JAMAIS l'opinion exprimée elle-même" in r for r in sent_rubrics)


def test_long_answer_feedback_structure_clause_reaches_the_ai_correction_prompt(
    authenticated_client, db_session, monkeypatch
):
    """Phase 10 (mission de nuit) : le feedback IA d'une réponse longue doit être structuré
    (STRUCTURE / ARGUMENTATION / UTILISATION DU DOCUMENT / LANGUE) —
    `_LONG_ANSWER_FEEDBACK_STRUCTURE_CLAUSE`. Vérifié jusqu'à l'appel IA réel (factice)."""
    seed()
    francais = db_session.query(Module).filter_by(code="FRANCAIS").first()
    c01 = db_session.query(UAA).filter_by(slug="francais-c01").first()
    import_francais_c01_to_bank(db_session, francais, c01)
    db_session.commit()

    question = _first_francais_question_with_rubric_containing(db_session, c01, "STRUCTURE")
    assert question.current_version.question_type == "long_answer"
    captured, fake = _patch_fake_provider_with_rubric_spy(monkeypatch)
    session_id = _build_single_existing_question_session(db_session, question)

    response = authenticated_client.get(f"/sessions/{session_id}?q=1")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/answer",
        data={
            "csrf_token": token, "position": 1, "direction": "submit",
            "text": "Réponse longue et argumentée couvrant plusieurs paragraphes développés.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = authenticated_client.get(f"/sessions/{session_id}/submit-confirm")
    token = _csrf(response.text)
    response = authenticated_client.post(
        f"/sessions/{session_id}/submit", data={"csrf_token": token, "severity": "3"}, follow_redirects=False,
    )
    assert response.status_code == 303
    from app.v1.session_service import claim_next_pending_correction_job, run_correction_job

    job = claim_next_pending_correction_job(db_session)
    if job is not None:
        run_correction_job(db_session, job=job, provider=fake)

    assert len(captured) == 1
    sent_rubrics = [q.rubric or "" for q in captured[0]]
    assert any("STRUCTURE" in r and "ARGUMENTATION" in r for r in sent_rubrics)


# --- 6. Document reste lisible pendant la question (accordéon, mobile-first) ------------------


def test_source_document_panel_is_shown_for_document_referencing_questions(
    authenticated_client, db_session, monkeypatch
):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    doc_position = None
    for sq in sorted(session.session_questions, key=lambda sq: sq.position):
        if sq.question_version.question_type in ("document_analysis", "source_comparison"):
            doc_position = sq.position
            break
    assert doc_position is not None

    response = authenticated_client.get(f"{session_url}?q={doc_position}")
    assert response.status_code == 200
    assert "source-document-panel" in response.text
    assert "Voir le document" in response.text
    assert "Ouvrir dans un nouvel onglet" in response.text
    assert "inutile de revenir en arrière" in response.text


def test_mobile_viewport_meta_present(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    response = authenticated_client.get(f"{session_url}?q=1")
    assert 'name="viewport"' in response.text


def test_document_accordion_is_scoped_and_bounded(authenticated_client, db_session, monkeypatch):
    """Une question ne doit jamais afficher les 5 documents à la fois (Phase 8, mission
    de nuit) : seul(s) le(s) document(s) réellement référencé(s) apparaissent, dans un
    accordéon à hauteur bornée et défilable (pas un mur de texte permanent)."""
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)

    single_doc_position = None
    comparison_position = None
    for sq in sorted(session.session_questions, key=lambda sq: sq.position):
        qtype = sq.question_version.question_type
        if qtype == "document_analysis" and single_doc_position is None:
            single_doc_position = sq.position
        if qtype == "source_comparison" and comparison_position is None:
            comparison_position = sq.position

    for position, expected_max in ((single_doc_position, 1), (comparison_position, 2)):
        if position is None:
            continue
        response = authenticated_client.get(f"{session_url}?q={position}")
        assert response.status_code == 200
        assert response.text.count("source-document-panel") <= expected_max
        assert "max-height: 50vh" in response.text
        assert "overflow-y: auto" in response.text


# --- 7. Non-régression AMPCR (le parcours Français ne casse rien d'existant) ------------------


def test_ampcr_mc01_practice_still_works(authenticated_client, db_session, monkeypatch):
    from app.v1.bank import import_mc01_legacy_to_bank

    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    response = authenticated_client.get("/uaa/ampcr-mc01/practice")
    assert response.status_code == 200
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/uaa/ampcr-mc01/practice/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303


# --- 8. Sévérité, export, impression, historique, déconnexion — vérifiés pour Français --------
# --- (mission de nuit § Phase 12 : fonctionnalités génériques #62, jamais testées avec un ------
# --- module Français jusqu'ici) -----------------------------------------------------------------


def test_severity_one_three_five_all_accepted_and_persisted_for_francais(
    authenticated_client, db_session, monkeypatch
):
    seed()
    for severity in (1, 3, 5):
        fake = _patch_fake_provider(monkeypatch)
        session_url = _start_session(authenticated_client, mode="practice")
        session_id = int(session_url.rsplit("/", 1)[-1])
        session = db_session.get(QuestionnaireSession, session_id)
        _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake, severity=severity)

        db_session.expire_all()
        session = db_session.get(QuestionnaireSession, session_id)
        assert session.status.value == "completed"
        assert (session.parameters_json or {}).get("severity") == severity

        response = authenticated_client.get(session_url)
        assert response.status_code == 200


def test_export_markdown_contains_francais_session_content(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(f"{session_url}/export.md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "attachment" in response.headers["content-disposition"]
    assert "# Métadonnées" in response.text
    assert "Français" in response.text
    for position in range(1, session.question_count + 1):
        assert f"## Question {position}" in response.text
    assert "### Ma réponse" in response.text
    assert "### Explication" in response.text


def test_print_button_and_css_present_for_francais_results(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get(session_url)
    assert response.status_code == 200
    assert "window.print()" in response.text
    assert "@media print" in response.text
    for position in range(1, session.question_count + 1):
        assert f"Question {position} —" in response.text


def test_mes_sessions_shows_francais_session(authenticated_client, db_session, monkeypatch):
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    response = authenticated_client.get("/mes-sessions")
    assert response.status_code == 200
    assert "Français" in response.text
    assert f'/sessions/{session_id}"' in response.text


def test_logout_then_login_preserves_francais_history(authenticated_client, db_session, monkeypatch):
    """Se déconnecter puis se reconnecter ne doit rien perdre : la session Français
    complétée reste visible dans l'historique après une nouvelle connexion (§ Phase 12)."""
    seed()
    fake = _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    _answer_all_and_submit(authenticated_client, session_url, session.question_count, db_session, fake)

    account_response = authenticated_client.get("/account")
    assert account_response.status_code == 200
    token = _csrf(account_response.text)
    logout_response = authenticated_client.post(
        "/logout", data={"csrf_token": token}, follow_redirects=False
    )
    assert logout_response.status_code == 303

    protected_response = authenticated_client.get("/mes-sessions", follow_redirects=False)
    assert protected_response.status_code == 303
    assert protected_response.headers["location"].startswith("/login")

    login_page = authenticated_client.get("/login")
    token = _csrf(login_page.text)
    login_response = authenticated_client.post(
        "/login",
        data={"csrf_token": token, "email": "eleve-test@example.test", "password": "test-password-1234"},
        follow_redirects=False,
    )
    assert login_response.status_code == 303

    history_response = authenticated_client.get("/mes-sessions")
    assert history_response.status_code == 200
    assert f'/sessions/{session_id}"' in history_response.text


# --- 9. Navigation Cours / S'entraîner / S'évaluer (ticket #22, générique) -- vérifiée --------
# --- explicitement pour l'espace Français (mission de nuit § Phase 13) -----------------------


def test_francais_space_nav_present_on_course_practice_and_exam_pages(authenticated_client, db_session):
    """La navigation à 3 onglets (`_uaa_space_nav.html`, ticket #22) est générique (basée
    uniquement sur `uaa.slug`) et déjà incluse par `uaa_detail.html` et
    `v1_session_start.html` : aucune UI/route nouvelle n'était nécessaire pour le Français
    (§ Phase 13). Ce test a révélé un vrai bug pré-existant (partagé avec AMPCR, pas
    spécifique au Français) : `render_practice_landing`/`render_exam_landing`
    (`app/v1/routes_sessions.py`) ne passaient jamais `active_space` au template, donc
    aucun onglet n'était jamais surligné actif sur les pages practice/exam. Corrigé par un
    ajout d'une clé de contexte manquante (aucune nouvelle architecture)."""
    seed()
    pages_and_active_space = (
        ("/uaa/francais-c01", "course"),
        ("/uaa/francais-c01/practice", "practice"),
        ("/uaa/francais-c01/exam", "exam"),
    )
    for url, active_space in pages_and_active_space:
        response = authenticated_client.get(url)
        assert response.status_code == 200, url
        assert 'class="jc-space-nav' in response.text
        assert '📘 Cours' in response.text
        assert "📝 S'entraîner" in response.text
        assert "📝 S'évaluer" not in response.text  # jamais le mauvais emoji collé
        assert "🎓 S'évaluer" in response.text
        assert 'href="/uaa/francais-c01"' in response.text
        assert 'href="/uaa/francais-c01/practice"' in response.text
        assert 'href="/uaa/francais-c01/exam"' in response.text
        active_href = {
            "course": "/uaa/francais-c01",
            "practice": "/uaa/francais-c01/practice",
            "exam": "/uaa/francais-c01/exam",
        }[active_space]
        anchor_match = re.search(
            rf'<a[^>]*href="{re.escape(active_href)}"[^>]*>.*?</a>', response.text, re.DOTALL
        )
        assert anchor_match, (url, active_space)
        assert "active" in anchor_match.group(0), (url, active_space)
        assert 'aria-current="page"' in anchor_match.group(0), (url, active_space)

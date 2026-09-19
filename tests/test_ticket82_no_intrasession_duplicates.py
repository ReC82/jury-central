"""Ticket #82 — BUG RÉEL : doublons intra-session (question 1 == question 10 dans une
même évaluation).

Cause racine trouvée dans `app.v1.session_service` : le « dernier repli » de
`start_session`/`_start_mc38_transversal_session`, quand la banque + génération ne
suffisent pas à atteindre `question_count`, complétait via
`pool[len(selected) % len(pool)]` — une pure répétition CYCLIQUE dès que `pool` est plus
petit que le manque à combler. C'est exactement le bug rapporté : avec une banque
insuffisante, la question déjà en position 1 (ou toute autre) réapparaît mécaniquement à
une position ultérieure.

Fix (voir `app.v1.session_service`) :
- `deduplicate_intra_session(selected)` : garde finale, appliquée par
  `_finalize_session` JUSTE AVANT l'insertion des `SessionQuestion` — élimine même
  `question_id`, même `current_version_id`, même énoncé EXACT (normalisé) avec un
  `question_id` différent, et tout quasi-doublon manifeste (mécanisme #64 réutilisé tel
  quel : `question_signature`/`is_near_duplicate`).
- `_extend_selection_without_duplicates(selected, fallback_pool, question_count)`
  remplace le cyclage : concatène puis déduplique, tronque à `question_count` — NE
  CYCLE JAMAIS. Une session plus courte que demandé est acceptable ; un doublon ne l'est
  jamais.
- `app.ai.fake_provider._fake_question` (garde-fou de test) génère désormais un contenu
  réellement distinct par question générée (avant : contenu 100% fixe par type, ce qui
  masquait ce bug précis dans TOUS les tests utilisant ce stub — deux appels du même
  type dans un même lot produisaient déjà, avant #82, deux questions identiques que rien
  ne rejetait).

Aucun appel OpenAI réel : `FakeAIProvider` (et des doublures dédiées ci-dessous) partout."""

import re

from app.ai.fake_provider import FakeAIProvider
from app.ai.schemas import Questionnaire, QuestionnaireQuestion
from app.models import UAA, Module
from app.seed import seed
from app.v1.bank import import_mc01_legacy_to_bank
from app.v1.models import (
    GenerationSource,
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    User,
    create_question,
)
from app.v1.session_service import (
    deduplicate_intra_session,
    start_session,
)


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "jeton CSRF introuvable"
    return match.group(1)


def _patch_fake_provider(monkeypatch):
    fake = FakeAIProvider()
    monkeypatch.setattr("app.v1.routes_sessions.get_ai_provider", lambda: fake)
    return fake


def _start_session(client, uaa_slug: str, mode: str = "practice", difficulty: str = "medium") -> str:
    response = client.get(f"/uaa/{uaa_slug}/{mode}")
    token = _csrf(response.text)
    response = client.post(
        f"/uaa/{uaa_slug}/{mode}/start",
        data={"csrf_token": token, "difficulty": difficulty},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    return response.headers["location"]


def _user(db_session, email="ticket82@example.invalid") -> User:
    user = User(email=email, password_hash="x", display_name="t")
    db_session.add(user)
    db_session.commit()
    return user


def _assert_no_intra_session_duplicates(session: QuestionnaireSession) -> None:
    """Assertion centrale du ticket : ni même `question_id`, ni même `version_id`, ni
    même énoncé exact, deux fois dans la même session."""
    session_questions = session.session_questions
    version_ids = [sq.question_version_id for sq in session_questions]
    assert len(version_ids) == len(set(version_ids)), "même question_version_id répété"

    question_ids = [
        sq.question_version.question_id for sq in session_questions if sq.question_version.question_id
    ]
    assert len(question_ids) == len(set(question_ids)), "même question_id répété"

    prompts = [sq.question_version.content_json.get("prompt", "") for sq in session_questions]
    assert len(prompts) == len(set(prompts)), "même énoncé exact répété (ids différents)"


# =============================================================================================
# 1. deduplicate_intra_session — unité
# =============================================================================================


def test_deduplicate_keeps_first_occurrence_of_same_question_id(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json={"prompt": "Unique.", "rubric": "Grille."}, generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()

    result = deduplicate_intra_session([question, question, question])
    assert len(result) == 1
    assert result[0].id == question.id


def test_deduplicate_rejects_exact_same_text_with_different_question_id(db_session):
    """§ ticket #82 : « doublon exact texte avec ID différent : rejet » — deux Question
    DIFFÉRENTES en base, contenu identique."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    content = {"prompt": "Exactement le même énoncé.", "rubric": "Grille."}
    q1 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json=dict(content), generation_source=GenerationSource.MANUAL,
    )
    q2 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json=dict(content), generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()
    assert q1.id != q2.id

    result = deduplicate_intra_session([q1, q2])
    assert len(result) == 1
    assert result[0].id == q1.id


def test_deduplicate_rejects_near_duplicate_via_ticket64_mechanism(db_session):
    """§ ticket #82 : « quasi-doublon manifeste : rejet via mécanisme #64 » — même
    structure (options triées identiques) et énoncés très proches, ids différents."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    base_options = [
        {"option_id": "0", "label": "Option A"}, {"option_id": "1", "label": "Option B"},
    ]
    q1 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quelle est la bonne réponse à cette question technique précise ?",
            "options": base_options, "min_selections": 1, "max_selections": 1,
            "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source=GenerationSource.MANUAL,
    )
    q2 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="multiple_choice",
        content_json={
            "prompt": "Quelle est la bonne réponse à cette question technique précise, exactement ?",
            "options": base_options, "min_selections": 1, "max_selections": 1,
            "correct_option_ids": ["0"], "explanation": "x",
        },
        generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()

    result = deduplicate_intra_session([q1, q2])
    assert len(result) == 1


def test_deduplicate_keeps_genuinely_different_questions(db_session):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    q1 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json={"prompt": "Première question, totalement différente de la suivante.", "rubric": "x"},
        generation_source=GenerationSource.MANUAL,
    )
    q2 = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json={"prompt": "Seconde question, sujet et vocabulaire sans rapport avec l'autre.", "rubric": "y"},
        generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()

    result = deduplicate_intra_session([q1, q2])
    assert len(result) == 2


# =============================================================================================
# 2. Reproduction directe du bug rapporté : générateur qui produit un contenu IDENTIQUE
# =============================================================================================


class _AlwaysIdenticalProvider:
    """Simule un générateur défaillant qui renvoie TOUJOURS la même question — exactement
    le scénario qui provoquait le bug rapporté (question 1 == question 10) avant #82."""

    def __init__(self):
        self.questionnaire_calls = []

    def generate_questionnaire(self, request):
        self.questionnaire_calls.append(request)
        questions = [
            QuestionnaireQuestion(
                question_id=f"identical-{len(self.questionnaire_calls)}-{i}",
                type="short_answer",
                points_max=1.0,
                prompt="Toujours exactement la même question factice, jamais variée.",
                accepted_answers=["même réponse"],
            )
            for i in range(request.question_count)
        ]
        return Questionnaire(mode=request.mode, questions=questions)

    def correct_semantic_batch(self, *args, **kwargs):
        raise NotImplementedError


def test_identical_generated_content_never_duplicated_in_session(db_session):
    """Reproduction directe du bug #82 : banque vide, générateur qui renvoie toujours la
    MÊME question. Avant le fix, `pool[len(selected) % len(pool)]` aurait rempli la
    session en répétant cette unique question générée jusqu'à `question_count`. Après le
    fix : au plus 1 exemplaire retenu, session plus courte, jamais de doublon."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    user = _user(db_session)
    provider = _AlwaysIdenticalProvider()

    session = start_session(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc17.id, uaa_code="MC17",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=provider, question_count=10,
    )
    _assert_no_intra_session_duplicates(session)
    assert session.question_count == 1, "un seul exemplaire d'une question toujours identique, jamais 10"


# =============================================================================================
# 3. Banque presque épuisée — session plus courte plutôt qu'un doublon
# =============================================================================================


class _AlwaysInvalidProvider:
    """Génération qui échoue TOUJOURS la validation structurelle (type inconnu) — simule
    une génération indisponible/inutilisable, forçant le repli banque pur."""

    def __init__(self):
        self.questionnaire_calls = []

    def generate_questionnaire(self, request):
        self.questionnaire_calls.append(request)
        return Questionnaire(mode=request.mode, questions=[])

    def correct_semantic_batch(self, *args, **kwargs):
        raise NotImplementedError


def test_bank_nearly_exhausted_yields_shorter_session_not_duplicates(db_session):
    """§ ticket #82 : « Si la banque est insuffisante : ... 3. session éventuellement
    plus courte ; 4. jamais de doublon intra-session. » Seulement 3 questions RÉELLEMENT
    distinctes en banque, `question_count=10` demandé, génération indisponible."""
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    # Trois énoncés VOLONTAIREMENT sans vocabulaire partagé significatif (sinon #64 les
    # traiterait lui-même comme quasi-doublons — ce n'est pas ce que ce test veut vérifier
    # ici, seulement le comportement du repli quand la banque est petite).
    distinct_prompts = [
        "Quel protocole chiffre les échanges HTTP par défaut sur le port 443 ?",
        "Quelle commande affiche la table de routage locale sous Linux ?",
        "Quelle unité mesure la fréquence d'horloge d'un processeur moderne ?",
    ]
    for prompt in distinct_prompts:
        create_question(
            db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
            content_json={"prompt": prompt, "rubric": "x"},
            generation_source=GenerationSource.MANUAL,
        )
    db_session.commit()
    user = _user(db_session)
    provider = _AlwaysInvalidProvider()

    session = start_session(
        db_session, user=user, module_id=ampcr.id, uaa_id=mc17.id, uaa_code="MC17",
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest.MEDIUM,
        provider=provider, question_count=10,
    )
    _assert_no_intra_session_duplicates(session)
    assert session.question_count == 3, "au plus les 3 questions réellement distinctes disponibles"


# =============================================================================================
# 4. Non-régression : practice 10Q / exam 10Q / exam 20Q / MC38 transversal — bases
# suffisamment fournies, aucune répétition intra-session
# =============================================================================================


def test_practice_ten_questions_no_duplicates(authenticated_client, db_session, monkeypatch):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10
    _assert_no_intra_session_duplicates(session)


def test_exam_ten_questions_no_duplicates(authenticated_client, db_session, monkeypatch):
    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc01 = db_session.query(UAA).filter_by(slug="ampcr-mc01").first()
    import_mc01_legacy_to_bank(db_session, ampcr, mc01)
    db_session.commit()
    _patch_fake_provider(monkeypatch)

    session_url = _start_session(authenticated_client, "ampcr-mc01", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10
    _assert_no_intra_session_duplicates(session)


def test_exam_twenty_questions_no_duplicates(authenticated_client, db_session, monkeypatch):
    """Examen blanc global AMPCR (§ 8 du ticket #64) — 20 questions, puisées dans
    plusieurs mini-cours, générées entièrement via FakeAIProvider (aucun contenu
    hand-authored pour MC04+) : le scénario le plus à risque de répétition avant #82."""
    seed()
    _patch_fake_provider(monkeypatch)
    response = authenticated_client.get("/modules/ampcr/exam")
    token = _csrf(response.text)
    response = authenticated_client.post(
        "/modules/ampcr/exam/start", data={"csrf_token": token, "difficulty": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 303, response.text
    session_id = int(response.headers["location"].rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 20
    _assert_no_intra_session_duplicates(session)


def test_mc38_transversal_twenty_questions_no_duplicates(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="exam")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 20
    _assert_no_intra_session_duplicates(session)


def test_mc38_transversal_practice_no_duplicates(authenticated_client, db_session, monkeypatch):
    seed()
    _patch_fake_provider(monkeypatch)
    session_url = _start_session(authenticated_client, "ampcr-mc38", mode="practice")
    session_id = int(session_url.rsplit("/", 1)[-1])
    session = db_session.get(QuestionnaireSession, session_id)
    assert session.question_count == 10
    _assert_no_intra_session_duplicates(session)


# =============================================================================================
# 5. Garde finale toujours appliquée, même si un appelant oublie de dédupliquer en amont
# =============================================================================================


def test_finalize_session_deduplicates_even_if_caller_passes_raw_duplicates(db_session):
    """§ ticket #82 : « Ajouter une garde finale AVANT insertion des SessionQuestion » —
    vérifiée directement : `_finalize_session` ne fait pas confiance à `selected`, même
    si celui-ci contient déjà un doublon manifeste construit à la main."""
    from app.v1.session_service import _finalize_session

    seed()
    ampcr = db_session.query(Module).filter_by(code="AMPCR").first()
    mc17 = db_session.query(UAA).filter_by(slug="ampcr-mc17").first()
    question = create_question(
        db_session, module_id=ampcr.id, uaa_id=mc17.id, question_type="short_answer",
        content_json={"prompt": "Une seule vraie question.", "rubric": "x"},
        generation_source=GenerationSource.MANUAL,
    )
    db_session.commit()
    user = _user(db_session)

    session = _finalize_session(
        db_session, user=user, module_id=ampcr.id, mode=SessionMode.PRACTICE,
        difficulty=SessionDifficultyRequest.MEDIUM,
        selected=[question, question, question, question],
    )
    assert session.question_count == 1
    _assert_no_intra_session_duplicates(session)

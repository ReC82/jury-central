"""Service de session V1 — moteur minimal condensant #41 (sélection banque)/#42
(sessions)/#43 (génération batch)/#44 (correction globale) pour la livraison urgente
MC01→MC38 (ticket #55).

Principe transversal : AUCUNE correction n'est jamais calculée avant
`submit_session()` — ni à la création de session, ni à l'autosave (`save_answer`). Un seul
appel IA au maximum par session, à la création (génération du complément manquant) et un
seul autre au maximum à la soumission (correction sémantique groupée) — jamais un appel
par question (voir `app.ai.questionnaire`, réutilisé tel quel, ticket #23)."""

import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session as DBSession

from app.ai.local_correction import correct_locally, requires_ai_correction
from app.ai.provider import AIProvider, AIProviderError
from app.ai.questionnaire import generate_questionnaire
from app.ai.schemas import (
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireRequest,
)
from app.v1.ai_bridge import (
    BRIDGE_TYPES,
    answer_json_to_submitted,
    content_to_questionnaire_question,
    describe_submitted_answer,
)
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.bank import (
    persist_generated_questions,
    recent_seen_prompts,
    select_bank_questions,
    select_transversal_bank_questions,
)
from app.v1.dedup import is_near_duplicate, question_signature
from app.v1.hybrid_correction import correct_session_hybrid
from app.v1.mc38_transversal import (
    MC38_CODE,
    MC38_SESSION_SCOPE,
    is_meta_revision_question,
    pick_transversal_contexts,
    question_full_text_from_questionnaire_question,
)
from app.v1.models import (
    AnswerCorrectionStatus,
    Question,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    record_question_seen,
)

DEFAULT_QUESTION_COUNT = 10
GLOBAL_EXAM_QUESTION_COUNT = 20
LONG_SEMANTIC_TYPES = frozenset({"long_answer", "diagnostic", "procedure", "troubleshooting"})
MAX_LONG_SEMANTIC_PER_SESSION = 3

_DIFFICULTY_TO_FRENCH = {
    SessionDifficultyRequest.EASY: "facile",
    SessionDifficultyRequest.MEDIUM: "moyen",
    SessionDifficultyRequest.HARD: "difficile",
    SessionDifficultyRequest.ADAPTIVE: "moyen",
}

# Sévérité de correction (ticket #62, § 5/6/7) : sélecteur UI 1-5, mappé sur les 5 niveaux
# internes du contrat #23 (`app.ai.schemas.SEVERITY_LEVELS`). N'influence QUE la notation/
# le feedback sémantique (voir `app.v1.hybrid_correction`) — jamais la correction
# déterministe, calculée indépendamment par `correct_locally`.
SEVERITY_UI_LEVELS = (1, 2, 3, 4, 5)
SEVERITY_UI_DEFAULT = 3
SEVERITY_UI_LABELS = {
    1: "Très bienveillante",
    2: "Bienveillante",
    3: "Standard",
    4: "Stricte",
    5: "Très stricte / niveau examen",
}
_SEVERITY_UI_TO_INTERNAL = {
    1: "very_lenient",
    2: "lenient",
    3: "standard",
    4: "strict",
    5: "very_strict",
}


class SessionCreationError(Exception):
    """La banque est vide et la génération a échoué : aucune question disponible du
    tout — cas limite documenté, ne devrait normalement jamais se produire une fois la
    banque amorcée (voir `app/v1/bank.py::import_mc01_legacy_to_bank`)."""


@dataclass
class QuestionDisplay:
    """Vue assemblée d'une `SessionQuestion` pour le template — jamais construite à
    partir d'un accès direct au contenu privé côté vue (voir `public_payload`)."""

    session_question: SessionQuestion
    position: int
    question_type: str
    public_payload: dict
    answer_json: dict


def compose_selection(pool: list[Question], count: int) -> list[Question]:
    """Répartit la sélection entre types disponibles (round-robin, diversité maximale) en
    plafonnant STRICTEMENT les types sémantiques longs à `MAX_LONG_SEMANTIC_PER_SESSION`
    (§ 14 du ticket #55 : « maximum 3 réponses longues/sémantiques » — règle stricte, pas
    seulement une préférence). Peut retourner MOINS de `count` questions si la banque
    disponible ne fournit pas assez de types non-sémantiques : à l'appelant
    (`start_session`) de compléter par génération ciblée plutôt que de violer le
    plafond en repêchant des types déjà plafonnés."""
    by_type: dict[str, list[Question]] = defaultdict(list)
    for question in pool:
        by_type[question.current_version.question_type].append(question)
    for bucket in by_type.values():
        random.shuffle(bucket)

    type_cycle = list(by_type.keys())
    random.shuffle(type_cycle)

    selected: list[Question] = []
    long_count = 0
    progressed = True
    while len(selected) < count and progressed:
        progressed = False
        for question_type in type_cycle:
            if len(selected) >= count:
                break
            bucket = by_type[question_type]
            if not bucket:
                continue
            is_long = question_type in LONG_SEMANTIC_TYPES
            if is_long and long_count >= MAX_LONG_SEMANTIC_PER_SESSION:
                continue
            selected.append(bucket.pop())
            long_count += is_long
            progressed = True

    return selected


def _diversity_capped_oversample(pool: list[Question], target_count: int, key_fn) -> list[Question]:
    """Plafonne la représentation d'une seule valeur de `key_fn` (catégorie AMPCR pour
    MC38 — ticket #58 § 6 ; mini-cours/UAA pour l'examen blanc global — ticket #64 § 8)
    dans le pool transmis à `compose_selection`. `key_fn(question) -> str | None` ; une
    valeur `None` place la question hors regroupement (jamais plafonnée, ajoutée en
    excédent si besoin — ex. question sans UAA connue).

    IMPORTANT : `compose_selection` regroupe son entrée par TYPE de question sans jamais
    tenir compte de l'ORDRE — réordonner `pool` sans réellement en exclure une partie
    n'aurait donc AUCUN effet sur la diversité obtenue en sortie. Cette fonction retire
    donc réellement l'excédent d'une valeur dominante (au-delà de la moitié de
    `target_count`) plutôt que de se contenter de le réordonner, sauf si cela laisserait
    trop peu de questions au total (repli explicite, comme pour MC38 : pas besoin de
    respecter exactement ces nombres si la banque disponible ne le permet pas)."""
    by_key: dict[str, list[Question]] = defaultdict(list)
    for question in pool:
        key = key_fn(question)
        if key is None:
            continue
        by_key[key].append(question)
    for bucket in by_key.values():
        random.shuffle(bucket)

    if len(by_key) <= 1:
        return pool

    max_per_key = max(1, -(-target_count // 2))  # ceil(target_count / 2)
    capped = [question for bucket in by_key.values() for question in bucket[:max_per_key]]
    random.shuffle(capped)

    if len(capped) < target_count:
        kept_ids = {id(question) for question in capped}
        leftovers = [question for question in pool if id(question) not in kept_ids]
        random.shuffle(leftovers)
        capped.extend(leftovers[: target_count * 3 - len(capped)])
    return capped


def _ampcr_category_key(question: Question) -> str | None:
    code = question.uaa.code if question.uaa else None
    plan = AMPCR_PLAN_BY_CODE.get(code) if code else None
    return plan.category if plan else None


def _category_balanced_oversample(pool: list[Question], target_count: int) -> list[Question]:
    """MC38 (§ 6 du ticket #58 : « plusieurs catégories obligatoires », pas nécessairement
    toutes ni des proportions exactes) — voir `_diversity_capped_oversample`."""
    return _diversity_capped_oversample(pool, target_count, _ampcr_category_key)


def _uaa_key(question: Question) -> str | None:
    return question.uaa.code if question.uaa else None


def _uaa_balanced_oversample(pool: list[Question], target_count: int) -> list[Question]:
    """Examen blanc global AMPCR (§ 8 du ticket #64 : « plusieurs mini-cours » obligatoires
    parmi les 20 questions) — voir `_diversity_capped_oversample`."""
    return _diversity_capped_oversample(pool, target_count, _uaa_key)


def _limit_near_duplicate_clusters(pool: list[Question], *, max_per_cluster: int = 2) -> list[Question]:
    """Plafonne à `max_per_cluster` le nombre de questions quasi-identiques (même
    signature structurelle, voir `app.v1.dedup`) au sein d'un même pool — évite qu'une
    session (en particulier l'examen blanc 20Q) présente 3 variantes ou plus très proches
    de la même micro-notion (§ 8 du ticket #64 : « pas plus de 2 questions très proches sur
    la même micro-notion »). Conserve l'ordre reçu (le pool est déjà mélangé en amont par
    `select_bank_questions`, tiré aléatoirement en base)."""
    kept: list[Question] = []
    kept_signatures: list = []
    cluster_counts: list[int] = []
    for question in pool:
        version = question.current_version
        if version is None:
            kept.append(question)
            continue
        signature = question_signature(version.question_type, version.content_json)
        cluster_index = next(
            (i for i, existing in enumerate(kept_signatures) if is_near_duplicate(signature, existing)),
            None,
        )
        if cluster_index is None:
            kept.append(question)
            kept_signatures.append(signature)
            cluster_counts.append(1)
        elif cluster_counts[cluster_index] < max_per_cluster:
            kept.append(question)
            cluster_counts[cluster_index] += 1
        # sinon : cluster déjà à `max_per_cluster`, question écartée du pool.
    return kept


def get_in_progress_session(
    db: DBSession,
    *,
    user_id: int,
    module_id: int,
    mode: SessionMode,
    uaa_id: int | None = None,
    scope: str | None = None,
) -> QuestionnaireSession | None:
    """`scope` (ticket #58) repère une session par marqueur explicite
    (`parameters_json["scope"]`, ex. MC38_SESSION_SCOPE) plutôt que par `uaa_id` — requis
    pour MC38, dont les questions appartiennent à MC01→MC37, jamais à MC38 lui-même."""
    query = db.query(QuestionnaireSession).filter_by(
        user_id=user_id, module_id=module_id, mode=mode, status=SessionStatus.IN_PROGRESS
    )
    sessions = query.order_by(QuestionnaireSession.created_at.desc()).all()

    if scope is not None:
        for candidate in sessions:
            if (candidate.parameters_json or {}).get("scope") == scope:
                return candidate
        return None

    if uaa_id is None:
        # Parcours global (§ 16/17 du ticket #55) : `uaa_id=None` doit repérer une session
        # GLOBALE déjà en cours, jamais une session per-MC — sinon un examen MC01 en cours
        # empêcherait à tort de démarrer l'examen blanc global AMPCR en redirigeant vers ce
        # mauvais examen (bug constaté en validation staging du ticket #55). Une session
        # est considérée globale si ses questions couvrent plus d'un mini-cours distinct.
        # Exclut explicitement les sessions MC38 (§58) : elles partagent la même
        # caractéristique « plusieurs mini-cours » sans être une vraie session globale
        # /modules/ampcr/... — même classe de bug que ci-dessus, à ne pas réintroduire.
        for candidate in sessions:
            if (candidate.parameters_json or {}).get("scope") == MC38_SESSION_SCOPE:
                continue
            uaa_ids = {
                sq.question_version.question.uaa_id
                for sq in candidate.session_questions
                if sq.question_version.question.uaa_id is not None
            }
            if len(uaa_ids) != 1:
                return candidate
        return None
    for candidate in sessions:
        first_question = candidate.session_questions[0] if candidate.session_questions else None
        if first_question and first_question.question_version.question.uaa_id == uaa_id:
            return candidate
    return None


def _pedagogical_context_for(uaa_code: str | None) -> PedagogicalContext:
    if uaa_code and uaa_code in AMPCR_PLAN_BY_CODE:
        from app.v1.ampcr_plan import AMPCR_CONTEXTS

        plan = AMPCR_PLAN_BY_CODE[uaa_code]
        return AMPCR_CONTEXTS[plan.course_key]
    # Parcours global : contexte générique couvrant l'ensemble du programme AMPCR.
    return PedagogicalContext(
        course_key="ampcr-global",
        course_title="Informatique — Assistant/Assistante de maintenance PC-réseaux (AMPCR), programme complet",
        level="CESS Professionnel, filière AMPCR, tous mini-cours confondus",
        allowed_notions=[plan.title for plan in AMPCR_PLAN_BY_CODE.values()],
        competencies=[],
        vocabulary=[],
        constraints="Reste dans le périmètre des mini-cours AMPCR listés, niveau débutant à intermédiaire.",
    )


def _finalize_session(
    db: DBSession,
    *,
    user: User,
    module_id: int,
    mode: SessionMode,
    difficulty: SessionDifficultyRequest,
    selected: list[Question],
    parameters_json: dict | None = None,
) -> QuestionnaireSession:
    """Construit la `QuestionnaireSession`/`SessionQuestion` à partir d'une sélection déjà
    prête — factorisé entre le parcours per-MC/global (`start_session`) et le parcours
    transversal MC38 (`_start_mc38_transversal_session`, ticket #58). `parameters_json`
    porte le marqueur `scope` (ticket #58, voir `get_in_progress_session`)."""
    session = QuestionnaireSession(
        user_id=user.id,
        mode=mode,
        module_id=module_id,
        difficulty_requested=difficulty,
        status=SessionStatus.IN_PROGRESS,
        question_count=len(selected),
        parameters_json=parameters_json,
    )
    db.add(session)
    db.flush()

    for position, question in enumerate(selected, start=1):
        session_question = SessionQuestion(
            session_id=session.id,
            question_version_id=question.current_version_id,
            position=position,
            points_max=1.0,
        )
        db.add(session_question)
        record_question_seen(
            db, user_id=user.id, question_version=question.current_version, session_id=session.id
        )
    db.commit()
    return session


def _start_mc38_transversal_session(
    db: DBSession,
    *,
    user: User,
    module_id: int,
    mc38_uaa_id: int | None,
    mode: SessionMode,
    difficulty: SessionDifficultyRequest,
    provider: AIProvider,
    question_count: int,
) -> QuestionnaireSession:
    """MC38 (ticket #58) : jamais le contexte MC38 lui-même (« comment réviser ») —
    sélectionne et génère exclusivement à partir des mini-cours réels MC01→MC37, avec une
    diversité de catégories best-effort (§ 6 du ticket), et filtre toute question générée
    qui ressemblerait à une question MÉTA sur le processus de révision avant de la
    persister (voir `app.v1.mc38_transversal.is_meta_revision_question`). Les questions
    générées sont tout de même stockées sous `uaa_id=mc38_uaa_id` (MC38 a bien sa propre
    ligne UAA) plutôt que sans attribution : la banque grandit organiquement d'une session
    à l'autre, comme pour tous les autres mini-cours — `select_transversal_bank_questions`
    inclut explicitement ce bucket dans son périmètre de lecture, jamais dans les contextes
    de génération (voir `app.v1.bank`).

    Anti-répétition (ticket #64 § 1) : la sélection banque initiale n'interroge QUE des
    questions jamais vues (`only_unseen=True`) — une question déjà vue n'est reprise qu'en
    tout dernier recours, ci-dessous, après tentative de génération."""
    oversample = select_transversal_bank_questions(
        db, user_id=user.id, module_id=module_id, limit=question_count * 3, only_unseen=True
    )
    oversample = _category_balanced_oversample(oversample, question_count)
    oversample = _limit_near_duplicate_clusters(oversample)
    selected = compose_selection(oversample, question_count)

    if len(selected) < question_count:
        missing = question_count - len(selected)
        long_count = sum(
            1 for q in selected if q.current_version.question_type in LONG_SEMANTIC_TYPES
        )
        allowed_types = tuple(
            BRIDGE_TYPES - LONG_SEMANTIC_TYPES
            if long_count >= MAX_LONG_SEMANTIC_PER_SESSION
            else BRIDGE_TYPES
        )
        contexts = pick_transversal_contexts()
        difficulty_fr = _DIFFICULTY_TO_FRENCH[difficulty]
        avoid_prompts = tuple(recent_seen_prompts(db, user_id=user.id, module_id=module_id))
        request = QuestionnaireRequest(
            contexts=contexts,
            mode=mode.value,
            difficulty=difficulty_fr,
            question_count=missing,
            allowed_types=allowed_types,
            avoid_prompts=avoid_prompts,
        )
        try:
            questionnaire = generate_questionnaire(provider, request)
            non_meta_questions = [
                q for q in questionnaire.questions
                if not is_meta_revision_question(question_full_text_from_questionnaire_question(q))
            ]
            new_questions = persist_generated_questions(
                db, module_id=module_id, uaa_id=mc38_uaa_id, questions=non_meta_questions
            )
            selected.extend(new_questions[:missing])
        except AIProviderError:
            pass  # repli ci-dessous : jamais d'échec de session pour ce seul motif.

    if len(selected) < question_count:
        # Dernier recours (§ 1 du ticket #64 : « réutiliser une ancienne question
        # uniquement en dernier recours ») : `only_unseen=False` (par défaut) autorise de
        # nouveau les questions déjà vues, seulement maintenant que banque-jamais-vue et
        # génération ont toutes deux été tentées.
        fallback_pool = select_transversal_bank_questions(
            db, user_id=user.id, module_id=module_id, limit=question_count * 5
        )
        if not fallback_pool and not selected:
            raise SessionCreationError(
                "Aucune question disponible pour la révision transversale MC38 (banque "
                "MC01-37 vide et génération indisponible)."
            )
        pool = selected or fallback_pool
        while len(selected) < question_count and pool:
            selected.append(pool[len(selected) % len(pool)])

    return _finalize_session(
        db, user=user, module_id=module_id, mode=mode, difficulty=difficulty, selected=selected,
        parameters_json={"scope": MC38_SESSION_SCOPE},
    )


def start_session(
    db: DBSession,
    *,
    user: User,
    module_id: int,
    uaa_id: int | None,
    uaa_code: str | None,
    mode: SessionMode,
    difficulty: SessionDifficultyRequest,
    provider: AIProvider,
    question_count: int = DEFAULT_QUESTION_COUNT,
) -> QuestionnaireSession:
    """Crée une nouvelle session : sélectionne dans la banque, complète par génération
    batch (UN appel) si nécessaire, et se rabat sur les questions déjà vues plutôt que
    d'échouer si la génération échoue (voir docstring du module).

    MC38 (ticket #58) est délégué à `_start_mc38_transversal_session` : ce mini-cours
    n'est pas une matière propre, ses sessions tirent exclusivement dans MC01→MC37 (jamais
    dans son propre contexte « révision/mémorisation », source du bug de questions méta
    constaté en validation staging)."""
    if uaa_code == MC38_CODE:
        return _start_mc38_transversal_session(
            db, user=user, module_id=module_id, mc38_uaa_id=uaa_id, mode=mode, difficulty=difficulty,
            provider=provider, question_count=question_count,
        )

    # Anti-répétition (ticket #64 § 1) : la sélection banque initiale n'interroge QUE des
    # questions jamais vues — une question déjà vue n'est reprise qu'en tout dernier
    # recours, plus bas, après tentative de génération.
    oversample = select_bank_questions(
        db, user_id=user.id, module_id=module_id, uaa_id=uaa_id, limit=question_count * 3,
        only_unseen=True,
    )
    if uaa_id is None:
        # Parcours global/examen blanc AMPCR (§ 8 du ticket #64) : plusieurs mini-cours
        # obligatoires — jamais pertinent pour une session scopée à un seul UAA.
        oversample = _uaa_balanced_oversample(oversample, question_count)
    oversample = _limit_near_duplicate_clusters(oversample)
    selected = compose_selection(oversample, question_count)

    if len(selected) < question_count:
        missing = question_count - len(selected)
        long_count = sum(
            1 for q in selected if q.current_version.question_type in LONG_SEMANTIC_TYPES
        )
        # Le plafond § 14 est déjà respecté par `compose_selection` : si atteint, on
        # demande explicitement des types NON sémantiques longs pour le complément,
        # plutôt que de laisser la génération choisir librement et risquer de le dépasser.
        allowed_types = tuple(
            BRIDGE_TYPES - LONG_SEMANTIC_TYPES
            if long_count >= MAX_LONG_SEMANTIC_PER_SESSION
            else BRIDGE_TYPES
        )
        context = _pedagogical_context_for(uaa_code)
        difficulty_fr = _DIFFICULTY_TO_FRENCH[difficulty]
        avoid_prompts = tuple(
            recent_seen_prompts(db, user_id=user.id, module_id=module_id, uaa_id=uaa_id)
        )
        request = QuestionnaireRequest(
            contexts=(context,),
            mode=mode.value,
            difficulty=difficulty_fr,
            question_count=missing,
            allowed_types=allowed_types,
            avoid_prompts=avoid_prompts,
        )
        try:
            questionnaire = generate_questionnaire(provider, request)
            new_questions = persist_generated_questions(
                db, module_id=module_id, uaa_id=uaa_id, questions=questionnaire.questions
            )
            selected.extend(new_questions[:missing])
        except AIProviderError:
            pass  # repli ci-dessous : jamais d'échec de session pour ce seul motif.

    if len(selected) < question_count:
        # Dernier repli explicite (§ GÉNÉRATION du ticket #55, § 1 du ticket #64 :
        # « réutiliser une ancienne question uniquement en dernier recours ») : réutilise
        # ce qui existe déjà (`only_unseen=False`, par défaut), y compris en répétant et en
        # dépassant exceptionnellement le plafond sémantique, plutôt que de refuser de
        # créer la session.
        fallback_pool = select_bank_questions(
            db, user_id=user.id, module_id=module_id, uaa_id=uaa_id, limit=question_count * 5
        )
        if not fallback_pool and not selected:
            raise SessionCreationError(
                "Aucune question disponible pour ce mini-cours (banque vide et génération "
                "indisponible)."
            )
        pool = selected or fallback_pool
        while len(selected) < question_count and pool:
            selected.append(pool[len(selected) % len(pool)])

    return _finalize_session(
        db, user=user, module_id=module_id, mode=mode, difficulty=difficulty, selected=selected
    )


def get_owned_session(db: DBSession, *, session_id: int, user_id: int) -> QuestionnaireSession | None:
    session = db.get(QuestionnaireSession, session_id)
    if session is None or session.user_id != user_id:
        return None
    return session


def describe_session_scope(session: QuestionnaireSession) -> str:
    """Libellé humain « module / mini-cours » d'une session, pour l'historique (ticket
    #62 § 8) — dérivé sans nouvelle colonne : marqueur `parameters_json["scope"]` (#58)
    en priorité, sinon la/les UAA réellement couvertes par les questions de la session
    (une seule UAA pour une session per-MC, plusieurs pour un parcours global)."""
    if (session.parameters_json or {}).get("scope") == MC38_SESSION_SCOPE:
        return "MC38 — Révision transversale (MC01→MC37)"

    uaa_titles: list[str] = []
    seen_ids: set[int] = set()
    for session_question in session.session_questions:
        question = session_question.question_version.question
        uaa = question.uaa if question else None
        if uaa is not None and uaa.id not in seen_ids:
            seen_ids.add(uaa.id)
            uaa_titles.append(f"{uaa.code} — {uaa.title}")

    if len(uaa_titles) == 1:
        return uaa_titles[0]
    if len(uaa_titles) > 1:
        return f"Parcours global ({len(uaa_titles)} mini-cours)"
    return session.module.code if session.module else "—"


def list_user_sessions(db: DBSession, *, user_id: int) -> list[QuestionnaireSession]:
    """Sessions de l'utilisateur, les plus récentes d'abord (ticket #62 § 8) — isolation
    stricte par `user_id`, jamais une autre session que la sienne."""
    return (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user_id)
        .order_by(QuestionnaireSession.created_at.desc())
        .all()
    )


def build_question_display(session_question: SessionQuestion) -> QuestionDisplay:
    from app.v1.question_engine import public_payload

    version = session_question.question_version
    payload = public_payload(version.question_type, version.schema_version, version.content_json)
    answer = session_question.answer
    return QuestionDisplay(
        session_question=session_question,
        position=session_question.position,
        question_type=version.question_type,
        public_payload=payload,
        answer_json=(answer.answer_json if answer else {}) or {},
    )


def save_answer(db: DBSession, *, session_question: SessionQuestion, answer_json: dict) -> SessionAnswer:
    """Autosave pur : jamais de calcul de correction ici (voir docstring du module)."""
    existing = session_question.answer
    if existing is None:
        existing = SessionAnswer(session_question_id=session_question.id, answer_json=answer_json)
        db.add(existing)
    else:
        existing.answer_json = answer_json
        existing.answered_at = datetime.now(UTC)
    db.commit()
    return existing


def submit_session(
    db: DBSession,
    *,
    session: QuestionnaireSession,
    provider: AIProvider,
    severity_ui: int = SEVERITY_UI_DEFAULT,
) -> QuestionnaireSession:
    """Correction globale hybride (ticket #62, étend § 15 du ticket #55) : construit un
    `Questionnaire` (#23) à partir des `SessionQuestion` de la session, appelle
    `correct_session_hybrid` — UN SEUL appel IA groupé qui note les questions sémantiques
    ET explique pédagogiquement les questions déterministes incorrectes (score verrouillé,
    jamais modifié par l'IA — voir `app.v1.hybrid_correction`) — puis marque la session
    `COMPLETED` (immuable — voir `QuestionnaireSession.is_locked`).

    `severity_ui` (1-5, § 5/6/7 du ticket #62) : n'influence QUE la notation/le feedback
    sémantique (via `_SEVERITY_UI_TO_INTERNAL`) — jamais la correction déterministe, qui
    reste calculée par `correct_locally` indépendamment de la sévérité choisie."""
    if session.is_locked():
        return session

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    questionnaire_questions = []
    answers: dict[str, object] = {}
    human_readable_answers: dict[str, str] = {}
    for session_question in session_questions:
        version = session_question.question_version
        question_id = f"sq{session_question.id}"
        qq = content_to_questionnaire_question(
            question_id=question_id,
            question_type=version.question_type,
            content=version.content_json,
            points_max=session_question.points_max,
        )
        questionnaire_questions.append(qq)
        raw_answer = session_question.answer.answer_json if session_question.answer else {}
        answers[question_id] = answer_json_to_submitted(version.question_type, version.content_json, raw_answer or {})
        human_readable_answers[question_id] = describe_submitted_answer(
            version.question_type, version.content_json, raw_answer or {}
        )

    questionnaire = Questionnaire(mode=session.mode.value, questions=questionnaire_questions)
    uaa_code = None
    first_question = session_questions[0].question_version.question if session_questions else None
    if first_question and first_question.uaa_id:
        uaa = first_question.uaa
        uaa_code = uaa.code if uaa else None
    context = _pedagogical_context_for(uaa_code)
    severity_internal = _SEVERITY_UI_TO_INTERNAL.get(severity_ui, "standard")

    try:
        correction = correct_session_hybrid(
            provider, questionnaire, answers, human_readable_answers, severity_internal, (context,)
        )
        corrections_by_id = {c.question_id: c for c in correction.questions}
        score = correction.score
    except AIProviderError:
        # Repli explicite (§ 13/§ CORRECTION du ticket #55, § 16 du ticket #62) : la
        # correction IA groupée a échoué (service indisponible) — corrige localement ce
        # qui peut l'être plutôt que de faire échouer toute la soumission ; les questions
        # sémantiques restent honnêtement signalées comme non corrigées (jamais un score
        # inventé) ; les questions déterministes gardent leur score local ET leur
        # explication locale minimale existante (message générique, faute d'IA
        # disponible) — jamais de perte de soumission.
        corrections_by_id = {}
        for qq in questionnaire_questions:
            if requires_ai_correction(qq):
                corrections_by_id[qq.question_id] = QuestionCorrection(
                    question_id=qq.question_id,
                    points_awarded=0.0,
                    points_max=qq.points_max,
                    correct=False,
                    errors=["Correction automatique indisponible pour le moment."],
                    feedback=(
                        "La correction automatique de cette question n'a pas pu être "
                        "effectuée (service de correction indisponible). Contacte ton "
                        "formateur si besoin."
                    ),
                )
            else:
                corrections_by_id[qq.question_id] = correct_locally(
                    qq, answers.get(qq.question_id)
                )
        score = sum(c.points_awarded for c in corrections_by_id.values())

    for session_question in session_questions:
        question_id = f"sq{session_question.id}"
        result = corrections_by_id.get(question_id)
        if result is None:
            continue
        answer_row = session_question.answer
        if answer_row is None:
            answer_row = SessionAnswer(session_question_id=session_question.id, answer_json={})
            db.add(answer_row)
        answer_row.points_awarded = result.points_awarded
        answer_row.correction_status = AnswerCorrectionStatus.CORRECTED
        answer_row.feedback_json = {
            "correct": result.correct,
            "points_max": result.points_max,
            "strengths": result.strengths,
            "errors": result.errors,
            "missing": result.missing,
            "feedback": result.feedback,
            "expected_answer": result.expected_answer,
        }

    session.score = round(score, 2)
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(UTC)
    # Persistance de la sévérité (§ 7 du ticket #62) : fusionnée dans parameters_json sans
    # écraser d'éventuelles autres clés déjà présentes (ex. {"scope": "mc38"}, ticket #58).
    updated_parameters = dict(session.parameters_json or {})
    updated_parameters["severity"] = severity_ui
    session.parameters_json = updated_parameters
    db.commit()
    return session

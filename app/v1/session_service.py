"""Service de session V1 — moteur minimal condensant #41 (sélection banque)/#42
(sessions)/#43 (génération batch)/#44 (correction globale) pour la livraison urgente
MC01→MC38 (ticket #55).

Principe transversal : AUCUNE correction n'est jamais calculée avant
`submit_session()` — ni à la création de session, ni à l'autosave (`save_answer`). Un seul
appel IA au maximum par session, à la création (génération du complément manquant) et un
seul autre au maximum à la soumission (correction sémantique groupée) — jamais un appel
par question (voir `app.ai.questionnaire`, réutilisé tel quel, ticket #23)."""

import random
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import update
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
from app.answer_checking import normalize_text
from app.v1.ai_bridge import (
    BRIDGE_TYPES,
    DOCUMENT_TYPES,
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
from app.v1.francais_plan import FRANCAIS_PLAN_BY_CODE, get_francais_context
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
    CorrectionJob,
    CorrectionJobStatus,
    Question,
    QuestionnaireSession,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    SourceDocumentVersion,
    User,
    record_question_seen,
)

DEFAULT_QUESTION_COUNT = 10
GLOBAL_EXAM_QUESTION_COUNT = 20
LONG_SEMANTIC_TYPES = frozenset({"long_answer", "diagnostic", "procedure", "troubleshooting"}) | DOCUMENT_TYPES
MAX_LONG_SEMANTIC_PER_SESSION = 3

# Ticket #68 § 15 : « priorité qualité > économie de tokens » — si la validation métier
# (`app.v1.domain_validation`) rejette une partie d'un lot généré (ex. une question IPv4
# techniquement fausse), on retente un appel CIBLÉ pour combler le manque plutôt que de se
# rabattre immédiatement sur la banque. Borné pour ne jamais boucler indéfiniment si le
# fournisseur produit systématiquement du contenu invalide ; au-delà, le repli banque
# existant (§ GÉNÉRATION du ticket #55) prend le relais côté appelant.
MAX_DOMAIN_REGENERATION_ATTEMPTS = 2

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
    source_documents: list[SourceDocumentVersion]
    source_document_labels: list[str]


def _generate_with_domain_retry(
    provider: AIProvider,
    *,
    missing: int,
    build_request: Callable[[int], QuestionnaireRequest],
    persist_batch: Callable[[Questionnaire], tuple[list[Question], int]],
) -> list[Question]:
    """Génère puis persiste jusqu'à `missing` questions. `persist_batch` renvoie
    `(questions_persistées, nombre_rejeté_par_validation_métier)` — un second appel n'est
    déclenché QUE si le manque restant est réellement imputable à la validation métier
    (`app.v1.domain_validation`, ticket #68 § 15 : « priorité qualité > économie de
    tokens »), jamais pour un manque dû au dédoublonnage (#64) ou à un contenu
    structurellement invalide, qui ne justifient PAS un second appel et doivent laisser
    l'invariant « un seul appel IA par session » du ticket #55 intact.

    Jamais pour compenser un échec réseau/fournisseur non plus : `AIProviderError` n'est
    jamais rattrapée ici, elle remonte telle quelle à l'appelant, qui gère son repli
    habituel (banque déjà vue en dernier recours). Borné à
    `MAX_DOMAIN_REGENERATION_ATTEMPTS` tentatives de complément — jamais de boucle
    infinie si le fournisseur produit systématiquement du contenu techniquement invalide ;
    le manque éventuel après cette limite reste à la charge de l'appelant, jamais une
    question invalide servie pour compléter artificiellement une session."""
    request = build_request(missing)
    questionnaire = generate_questionnaire(provider, request)
    persisted, domain_rejected = persist_batch(questionnaire)
    collected: list[Question] = list(persisted)
    remaining = missing - len(collected)

    attempts = 0
    while remaining > 0 and domain_rejected > 0 and attempts < MAX_DOMAIN_REGENERATION_ATTEMPTS:
        request = build_request(remaining)
        questionnaire = generate_questionnaire(provider, request)
        persisted, domain_rejected = persist_batch(questionnaire)
        collected.extend(persisted)
        remaining = missing - len(collected)
        attempts += 1
    return collected


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


def deduplicate_intra_session(selected: list[Question]) -> list[Question]:
    """Garde finale anti-doublon intra-session (ticket #82) — appliquée juste avant
    l'insertion des `SessionQuestion` (`_finalize_session`), et réutilisée par les
    fallbacks « dernier recours » de `start_session`/`_start_mc38_transversal_session` pour
    ne jamais proposer une question déjà retenue comme complément.

    Élimine, dans l'ordre de `selected` (garde la PREMIÈRE occurrence de chaque groupe) :
    - même `Question.id` plus d'une fois ;
    - même `current_version_id` plus d'une fois ;
    - même énoncé EXACT (normalisé) avec un `question_id` différent (ex. une question
      dupliquée en banque sous deux id distincts) ;
    - quasi-doublon manifeste (même mécanisme que #64 : `question_signature`/
      `is_near_duplicate` — structure triée identique, ou énoncés très proches).

    Ne complète JAMAIS le manque en répétant une question déjà retenue — c'est aux
    appelants de proposer une session plus courte plutôt que de violer cette garde (§
    ticket #82 : « le fallback ne doit jamais cycler sur la même question »)."""
    kept: list[Question] = []
    seen_question_ids: set[int] = set()
    seen_version_ids: set[int] = set()
    seen_prompts: set[str] = set()
    seen_signatures: list = []

    for question in selected:
        if question.id in seen_question_ids or question.current_version_id in seen_version_ids:
            continue
        version = question.current_version
        content = version.content_json or {}
        prompt_key = normalize_text(str(content.get("prompt", "")))
        if prompt_key and prompt_key in seen_prompts:
            continue
        signature = question_signature(version.question_type, content)
        if any(is_near_duplicate(signature, existing) for existing in seen_signatures):
            continue

        kept.append(question)
        seen_question_ids.add(question.id)
        seen_version_ids.add(question.current_version_id)
        if prompt_key:
            seen_prompts.add(prompt_key)
        seen_signatures.append(signature)

    return kept


def _extend_selection_without_duplicates(
    selected: list[Question], fallback_pool: list[Question], question_count: int
) -> list[Question]:
    """Complète `selected` avec des questions de `fallback_pool` jusqu'à `question_count`,
    SANS JAMAIS introduire de doublon intra-session (ticket #82) — ni en répétant une
    question déjà retenue, ni en « cyclant » sur le pool une fois épuisé (bug corrigé :
    l'ancien code faisait `pool[len(selected) % len(pool)]`, qui répète mécaniquement les
    mêmes questions dès que le pool est plus petit que le manque à combler — exactement le
    bug observé, question 1 == question 10 dans une même évaluation).

    S'arrête dès que le pool ne fournit plus rien d'unique : une session plus courte que
    demandé est acceptable (§ ticket #82, hiérarchie de repli), un doublon ne l'est
    jamais."""
    return deduplicate_intra_session([*selected, *fallback_pool])[:question_count]


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
    if uaa_code and uaa_code in FRANCAIS_PLAN_BY_CODE:
        plan = FRANCAIS_PLAN_BY_CODE[uaa_code]
        context = get_francais_context(plan.course_key)
        if context is not None:
            return context
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
    porte le marqueur `scope` (ticket #58, voir `get_in_progress_session`).

    Ticket #82 (garde finale) : `selected` repasse ici par
    `deduplicate_intra_session` juste AVANT l'insertion des `SessionQuestion` — le
    dernier point de passage commun à TOUS les parcours de création de session, quel que
    soit ce qui a pu se produire en amont. `question_count` reflète le nombre RÉEL de
    questions retenues après cette garde (jamais le nombre demandé si la garde en a
    retiré) — une session plus courte que prévu est acceptable, un doublon ne l'est
    jamais."""
    selected = deduplicate_intra_session(selected)
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
        # Snapshot optionnel (§ H du modèle #38) : uniquement pour document_analysis
        # (UN document) — jamais requis pour la relecture (résolue à l'affichage depuis
        # content_json, voir `build_question_display`), simple dénormalisation utile.
        # source_comparison référence plusieurs documents, non représentable par ce
        # champ FK unique : laissé à None, sans conséquence fonctionnelle.
        content = question.current_version.content_json or {}
        source_document_version_id = content.get("source_document_version_id")
        session_question = SessionQuestion(
            session_id=session.id,
            question_version_id=question.current_version_id,
            position=position,
            points_max=1.0,
            source_document_version_id=source_document_version_id,
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

        def _persist_non_meta(questionnaire: Questionnaire) -> tuple[list[Question], int]:
            non_meta_questions = [
                q for q in questionnaire.questions
                if not is_meta_revision_question(question_full_text_from_questionnaire_question(q))
            ]
            domain_rejections: list[str] = []
            persisted = persist_generated_questions(
                db, module_id=module_id, uaa_id=mc38_uaa_id, questions=non_meta_questions,
                domain_rejections=domain_rejections,
            )
            return persisted, len(domain_rejections)

        try:
            new_questions = _generate_with_domain_retry(
                provider,
                missing=missing,
                build_request=lambda count: QuestionnaireRequest(
                    contexts=contexts, mode=mode.value, difficulty=difficulty_fr,
                    question_count=count, allowed_types=allowed_types, avoid_prompts=avoid_prompts,
                ),
                persist_batch=_persist_non_meta,
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
        selected = _extend_selection_without_duplicates(selected, fallback_pool, question_count)

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

        def _persist(questionnaire: Questionnaire) -> tuple[list[Question], int]:
            domain_rejections: list[str] = []
            persisted = persist_generated_questions(
                db, module_id=module_id, uaa_id=uaa_id, questions=questionnaire.questions,
                domain_rejections=domain_rejections,
            )
            return persisted, len(domain_rejections)

        try:
            new_questions = _generate_with_domain_retry(
                provider,
                missing=missing,
                build_request=lambda count: QuestionnaireRequest(
                    contexts=(context,), mode=mode.value, difficulty=difficulty_fr,
                    question_count=count, allowed_types=allowed_types, avoid_prompts=avoid_prompts,
                ),
                persist_batch=_persist,
            )
            selected.extend(new_questions[:missing])
        except AIProviderError:
            pass  # repli ci-dessous : jamais d'échec de session pour ce seul motif.

    if len(selected) < question_count:
        # Dernier repli explicite (§ GÉNÉRATION du ticket #55, § 1 du ticket #64 :
        # « réutiliser une ancienne question uniquement en dernier recours ») : réutilise
        # ce qui existe déjà (`only_unseen=False`, par défaut), en dépassant
        # exceptionnellement le plafond sémantique si besoin — mais JAMAIS en répétant une
        # question déjà retenue (ticket #82 : une session plus courte que demandé est
        # acceptable, un doublon intra-session ne l'est jamais).
        fallback_pool = select_bank_questions(
            db, user_id=user.id, module_id=module_id, uaa_id=uaa_id, limit=question_count * 5
        )
        if not fallback_pool and not selected:
            raise SessionCreationError(
                "Aucune question disponible pour ce mini-cours (banque vide et génération "
                "indisponible)."
            )
        selected = _extend_selection_without_duplicates(selected, fallback_pool, question_count)

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


def _referenced_document_ids(payload: dict) -> list[int]:
    """Seule source de vérité pour « quel(s) document(s) cette question référence »,
    dérivée du PAYLOAD PUBLIC (`public_payload`) — jamais du `content_json` brut.

    Ticket #77 (bug) : la question `long_answer` id=170 référençait un document dans son
    `content_json`, mais le type `long_answer` ne déclarait pas ce champ — Pydantic le
    supprimait silencieusement du payload public, donc `build_question_display` (élève)
    ne le voyait jamais, alors que `_document_contexts_for` (correction IA), qui lisait
    alors le `content_json` brut directement, le voyait quand même : l'élève était corrigé
    sur un document qu'il n'avait jamais pu lire.

    Fix structurel : les DEUX appelants passent désormais par cette même fonction, qui ne
    lit QUE le payload public (donc filtré par le modèle Pydantic du type). Un document
    absent du modèle d'un type ne peut plus jamais atteindre le correcteur IA sans être
    aussi montré à l'élève — plus une question de discipline au cas par cas."""
    doc_ids: list[int] = []
    single_id = payload.get("source_document_version_id")
    if single_id:
        doc_ids = [single_id]
    multiple_ids = payload.get("source_document_version_ids")
    if multiple_ids:
        doc_ids = list(multiple_ids)
    return doc_ids


def document_label(question_type: str, index: int) -> str:
    """Étiquette d'un document référencé par position (ticket #79, § 9) : « Document A »/
    « Document B » pour `source_comparison` (jamais mélangés — voir
    `resolve_documents_in_order` pour l'ordre), « Document de référence » sinon (au plus 1
    document pour les autres types actuellement, voir `SourceDocumentRequirement`). Seule
    définition de cet étiquetage — utilisée à la fois pour l'écran de question
    (`build_question_display`) et pour les résultats/export (`routes_sessions.py`)."""
    if question_type == "source_comparison":
        return f"Document {chr(ord('A') + index)}"
    return "Document de référence"


def resolve_documents_in_order(db: DBSession, doc_ids: list[int]) -> list[SourceDocumentVersion]:
    """Résout des identifiants de `SourceDocumentVersion` en respectant l'ORDRE fourni
    (ticket #79, § 9 « Document A / Document B ») — jamais un tri par id. Une question
    `source_comparison` référence ses documents dans l'ordre où son `prompt`/`rubric` les
    nomme (ex. « texte principal » puis « second texte ») ; trier par id casserait cet
    étiquetage si un document cité en premier a été créé après l'autre."""
    if not doc_ids:
        return []
    fetched = db.query(SourceDocumentVersion).filter(SourceDocumentVersion.id.in_(doc_ids)).all()
    by_id = {document.id: document for document in fetched}
    return [by_id[doc_id] for doc_id in doc_ids if doc_id in by_id]


def build_question_display(db: DBSession, session_question: SessionQuestion) -> QuestionDisplay:
    from app.v1.question_engine import public_payload

    version = session_question.question_version
    payload = public_payload(version.question_type, version.schema_version, version.content_json)
    answer = session_question.answer

    # Français (ticket #47) : une question document_analysis/source_comparison/
    # long_answer (#77) référence un ou plusieurs SourceDocumentVersion par identifiant
    # (jamais le texte dupliqué dans content_json, voir #40) — résolus ici pour le
    # panneau/accordéon de lecture du template, une seule requête, jamais par question
    # dans une boucle ailleurs.
    doc_ids = _referenced_document_ids(payload)
    source_documents = resolve_documents_in_order(db, doc_ids)
    source_document_labels = [document_label(version.question_type, index) for index in range(len(source_documents))]

    return QuestionDisplay(
        session_question=session_question,
        position=session_question.position,
        question_type=version.question_type,
        public_payload=payload,
        answer_json=(answer.answer_json if answer else {}) or {},
        source_documents=source_documents,
        source_document_labels=source_document_labels,
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


def _document_contexts_for(db: DBSession, session_questions: list[SessionQuestion]) -> tuple[PedagogicalContext, ...]:
    """Construit un contexte pédagogique par document référencé par au moins une question
    de la session (ticket #47, § CORRECTION : « le document partagé doit être fourni une
    seule fois dans le contexte logique du batch ») — jamais un contexte par QUESTION, un
    seul par DOCUMENT distinct, quel que soit le nombre de questions qui le référencent.
    Le texte complet n'apparaît donc qu'une fois dans le prompt de correction
    (`app/ai/prompts.py::_questionnaire_context_block`, inchangé, itère sur les contextes
    une seule fois avant la boucle sur les questions).

    Ticket #77 : les identifiants de document viennent du PAYLOAD PUBLIC
    (`_referenced_document_ids`), exactement comme pour l'élève (`build_question_display`)
    — jamais du `content_json` brut. Garantit que l'IA ne peut jamais recevoir un document
    que l'élève n'a pas pu voir (voir docstring de `_referenced_document_ids`)."""
    from app.v1.question_engine import public_payload

    doc_ids: set[int] = set()
    for session_question in session_questions:
        version = session_question.question_version
        payload = public_payload(version.question_type, version.schema_version, version.content_json)
        doc_ids.update(_referenced_document_ids(payload))
    if not doc_ids:
        return ()

    documents = (
        db.query(SourceDocumentVersion)
        .filter(SourceDocumentVersion.id.in_(doc_ids))
        .order_by(SourceDocumentVersion.id)
        .all()
    )
    return tuple(
        PedagogicalContext(
            course_key=f"source-document-{document.id}",
            course_title=document.title or "Document source",
            level="Texte de référence pour les questions de cette session qui le citent",
            allowed_notions=[],
            competencies=[],
            vocabulary=[],
            constraints=(
                "Texte source de référence (fourni une seule fois pour toute la session, "
                "valable pour toute question qui s'y réfère) :\n\"\"\"\n"
                f"{document.content_text or ''}\n\"\"\""
            ),
        )
        for document in documents
    )


def _build_questionnaire_inputs(
    session_questions: list[SessionQuestion],
) -> tuple[list, dict[str, object], dict[str, str]]:
    """Construit `(questionnaire_questions, answers, human_readable_answers)` à partir de
    `session_questions` — factorisé (ticket #70 § A) entre `submit_session` (correction
    réelle, persistée) et `simulate_severity_comparison` (simulation en LECTURE SEULE,
    jamais persistée) : les deux doivent construire EXACTEMENT le même
    `Questionnaire`/mêmes réponses à partir des réponses déjà enregistrées, sans jamais
    diverger entre les deux usages."""
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
    return questionnaire_questions, answers, human_readable_answers


def _contexts_for_session(db: DBSession, session_questions: list[SessionQuestion]) -> tuple[PedagogicalContext, ...]:
    """Contexte pédagogique + contexte(s) documentaire(s) pour la correction d'une
    session — factorisé (ticket #70 § A) entre `submit_session` et
    `simulate_severity_comparison`, jamais deux implémentations."""
    uaa_code = None
    first_question = session_questions[0].question_version.question if session_questions else None
    if first_question and first_question.uaa_id:
        uaa = first_question.uaa
        uaa_code = uaa.code if uaa else None
    context = _pedagogical_context_for(uaa_code)
    return (context, *_document_contexts_for(db, session_questions))


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
    reste calculée par `correct_locally` indépendamment de la sévérité choisie.

    Documents partagés (ticket #47) : `_document_contexts_for` ajoute un contexte par
    document réellement référencé par au moins une question de la session, en plus du
    contexte de matière/UAA — le texte source n'apparaît donc qu'une fois dans le lot,
    quel que soit le nombre de questions qui le citent.

    Ticket #71 : réclamation ATOMIQUE de la session AVANT l'appel IA (potentiellement
    long, plusieurs secondes — l'origine du bug rapporté : bouton recliqué ou requête
    réémise pendant l'attente déclenchait une SECONDE correction IA complète, avant même
    que la première n'ait eu le temps de marquer la session `COMPLETED`). L'ancien code ne
    fixait `status = COMPLETED` qu'à la toute fin — cette fenêtre de plusieurs secondes
    était exactement la fenêtre de la course. Un `UPDATE ... WHERE status = IN_PROGRESS`
    est atomique au niveau de la ligne : si `rowcount == 0`, une autre requête a déjà
    réclamé cette session entre notre lecture et maintenant — on s'arrête immédiatement,
    sans jamais appeler l'IA une seconde fois. Le corps de la fonction est protégé par un
    filet de sécurité : toute exception inattendue (hors `AIProviderError`, déjà gérée
    plus bas avec un repli local) remet `status = IN_PROGRESS` avant de se propager,
    jamais une session bloquée `COMPLETED` sans résultat réel."""
    if session.is_locked():
        return session

    claim = db.execute(
        update(QuestionnaireSession)
        .where(QuestionnaireSession.id == session.id, QuestionnaireSession.status == SessionStatus.IN_PROGRESS)
        .values(status=SessionStatus.COMPLETED)
    )
    db.commit()
    if claim.rowcount == 0:
        db.refresh(session)
        return session
    session.status = SessionStatus.COMPLETED

    try:
        return _correct_and_finalize_claimed_session(
            db, session=session, provider=provider, severity_ui=severity_ui
        )
    except Exception:
        session.status = SessionStatus.IN_PROGRESS
        db.commit()
        raise


def _correct_and_finalize_claimed_session(
    db: DBSession, *, session: QuestionnaireSession, provider: AIProvider, severity_ui: int
) -> QuestionnaireSession:
    """Corps de `submit_session` (ticket #71 : extrait pour envelopper d'un filet de
    sécurité qui annule la réclamation atomique en cas d'exception inattendue — voir
    docstring de `submit_session`). `session.status` est déjà `COMPLETED` en entrée."""
    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    questionnaire_questions, answers, human_readable_answers = _build_questionnaire_inputs(session_questions)
    questionnaire = Questionnaire(mode=session.mode.value, questions=questionnaire_questions)
    contexts = _contexts_for_session(db, session_questions)
    severity_internal = _SEVERITY_UI_TO_INTERNAL.get(severity_ui, "standard")

    try:
        correction = correct_session_hybrid(
            provider, questionnaire, answers, human_readable_answers, severity_internal, contexts
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


# =============================================================================================
# Correction asynchrone (ticket #88) : casse la dépendance entre la durée de l'appel IA
# groupé et la requête HTTP `POST /sessions/{id}/submit`, seule cause du 504 Gateway
# Time-out réellement observé en staging. `submit_session`/`_correct_and_finalize_
# claimed_session` ci-dessus restent INCHANGÉS (toujours directement utilisables/testés,
# ex. tickets #70/#71/#74) — réutilisés tels quels par `run_correction_job` ci-dessous
# comme le corps réel du travail de correction, exécuté par un worker séparé, jamais
# dans le cycle requête/réponse HTTP.
# =============================================================================================

_ENQUEUE_RACE_RETRY_ATTEMPTS = 10
_ENQUEUE_RACE_RETRY_DELAY_SECONDS = 0.05


def get_correction_job(db: DBSession, *, session_id: int) -> CorrectionJob | None:
    return db.query(CorrectionJob).filter_by(session_id=session_id).first()


def enqueue_correction(db: DBSession, *, session: QuestionnaireSession, severity_ui: int) -> CorrectionJob:
    """Point d'entrée non bloquant de `POST /sessions/{id}/submit` (ticket #88) : verrouille
    la session (`IN_PROGRESS` → `CORRECTING`, réclamation atomique — même mécanisme que
    l'ancienne réclamation `IN_PROGRESS` → `COMPLETED` de `submit_session`, voir sa
    docstring) et crée (ou retrouve) un `CorrectionJob` `PENDING`. NE FAIT JAMAIS d'appel
    IA — retourne dès que le job existe, en quelques millisecondes, quelle que soit la
    durée que prendra la correction elle-même.

    Idempotent par construction (ticket #88 § 4) : `CorrectionJob.session_id` est UNIQUE
    en base — un double clic, un refresh, un retour arrière/avant, un retry HTTP ou deux
    onglets simultanés retombent tous sur CE MÊME job (recherché en premier, avant toute
    tentative de réclamation), jamais une seconde ligne ni un second appel IA."""
    existing = get_correction_job(db, session_id=session.id)
    if existing is not None:
        return existing

    claim = db.execute(
        update(QuestionnaireSession)
        .where(QuestionnaireSession.id == session.id, QuestionnaireSession.status == SessionStatus.IN_PROGRESS)
        .values(status=SessionStatus.CORRECTING)
    )
    db.commit()

    if claim.rowcount == 0:
        # Une autre requête a déjà réclamé cette session (course gagnée ailleurs) — son
        # job existe déjà ou est sur le point d'être committé ; on le retrouve, avec un
        # court repli borné pour l'extrême cas où notre lecture précède de quelques
        # millisecondes le commit du gagnant (fenêtre de course, jamais observée en
        # pratique avec SQLite — écritures sérialisées — mais couverte explicitement).
        for _ in range(_ENQUEUE_RACE_RETRY_ATTEMPTS):
            existing = get_correction_job(db, session_id=session.id)
            if existing is not None:
                return existing
            time.sleep(_ENQUEUE_RACE_RETRY_DELAY_SECONDS)
        db.refresh(session)
        raise RuntimeError(
            f"Session {session.id} réclamée (status={session.status.value}) mais aucun "
            "CorrectionJob retrouvé après un court délai — incohérence inattendue."
        )

    job = CorrectionJob(session_id=session.id, status=CorrectionJobStatus.PENDING, severity_ui=severity_ui)
    db.add(job)
    db.commit()
    return job


def claim_next_pending_correction_job(db: DBSession, *, max_attempts: int = 3) -> CorrectionJob | None:
    """Réclamation ATOMIQUE du prochain job `PENDING` par un worker (ticket #88 § 8) —
    `UPDATE ... WHERE status = PENDING` : si un autre worker l'a réclamé entre notre
    lecture et cette mise à jour, `rowcount == 0` et on renvoie `None` sans jamais
    exécuter deux fois la même correction. Les jobs ayant déjà atteint `max_attempts`
    sont ignorés (laissés `PENDING`... non — voir `recover_stale_correction_jobs`, qui
    les fait passer `FAILED` : ce filtre est un filet de sécurité supplémentaire, jamais
    la seule protection)."""
    job = (
        db.query(CorrectionJob)
        .filter(CorrectionJob.status == CorrectionJobStatus.PENDING, CorrectionJob.attempt_count < max_attempts)
        .order_by(CorrectionJob.created_at)
        .first()
    )
    if job is None:
        return None

    claim = db.execute(
        update(CorrectionJob)
        .where(CorrectionJob.id == job.id, CorrectionJob.status == CorrectionJobStatus.PENDING)
        .values(
            status=CorrectionJobStatus.RUNNING,
            started_at=datetime.now(UTC),
            attempt_count=CorrectionJob.attempt_count + 1,
        )
    )
    db.commit()
    if claim.rowcount == 0:
        return None
    db.refresh(job)
    return job


def run_correction_job(db: DBSession, *, job: CorrectionJob, provider: AIProvider) -> CorrectionJob:
    """Corps réel du travail de correction (ticket #88), exécuté par un worker — jamais
    dans une requête HTTP. Réutilise `_correct_and_finalize_claimed_session` telle quelle
    (déjà responsable de faire passer `session.status` à `COMPLETED`) : `AIProviderError`
    y est DÉJÀ gérée avec un repli local gracieux (§ 13/§ CORRECTION du ticket #55, § 16
    du ticket #62, comportement INCHANGÉ par ce ticket) — cette fonction ne voit donc
    jamais cette exception, seulement une erreur réellement inattendue (bug, base
    indisponible...), qu'elle transforme en `CorrectionJobStatus.FAILED` avec un message
    d'erreur, jamais en session bloquée sans explication."""
    session = db.get(QuestionnaireSession, job.session_id)
    if session is None:
        job.status = CorrectionJobStatus.FAILED
        job.error_message = f"Session {job.session_id} introuvable."
        db.commit()
        return job

    try:
        _correct_and_finalize_claimed_session(db, session=session, provider=provider, severity_ui=job.severity_ui)
    except Exception as exc:  # noqa: BLE001 — job de fond, jamais de propagation vers un client HTTP
        db.rollback()
        job.status = CorrectionJobStatus.FAILED
        job.error_message = str(exc)[:2000]
        db.commit()
        return job

    job.status = CorrectionJobStatus.COMPLETED
    job.completed_at = datetime.now(UTC)
    db.commit()
    return job


def recover_stale_correction_jobs(
    db: DBSession, *, stale_after_seconds: int = 300, max_attempts: int = 3
) -> dict[str, int]:
    """Récupération des jobs bloqués (ticket #88 § 9) : un worker qui plante APRÈS avoir
    réclamé un job (`RUNNING`) mais AVANT de le conclure le laisserait sinon bloqué
    indéfiniment. Tout job `RUNNING` depuis plus de `stale_after_seconds` est soit remis
    `PENDING` (requeue, s'il lui reste des tentatives), soit basculé `FAILED` (au-delà de
    `max_attempts` — jamais de boucle infinie de reprises)."""
    threshold = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
    stale_jobs = (
        db.query(CorrectionJob)
        .filter(CorrectionJob.status == CorrectionJobStatus.RUNNING, CorrectionJob.started_at < threshold)
        .all()
    )
    requeued = 0
    failed = 0
    for job in stale_jobs:
        if job.attempt_count >= max_attempts:
            job.status = CorrectionJobStatus.FAILED
            job.error_message = (
                "Job resté bloqué (RUNNING) trop longtemps — nombre maximal de tentatives "
                f"atteint ({max_attempts})."
            )
            failed += 1
        else:
            job.status = CorrectionJobStatus.PENDING
            job.started_at = None
            requeued += 1
    db.commit()
    return {"requeued": requeued, "failed": failed}


class CorrectionJobNotFailedError(ValueError):
    """Un retry n'a de sens que sur un job réellement `FAILED` (ticket #88 § 10)."""


def retry_failed_correction_job(db: DBSession, *, job: CorrectionJob) -> CorrectionJob:
    """Réessaie une correction en échec (ticket #88 § 10) : réutilise le MÊME job (jamais
    une seconde ligne, jamais un second `CorrectionJob` pour la session), remis `PENDING`
    avec un compteur de tentatives repartant de zéro (action humaine explicite et
    délibérée, distincte d'une reprise automatique après incident — voir
    `recover_stale_correction_jobs`). Ne modifie jamais les réponses déjà enregistrées ni
    `QuestionnaireSession.status` (reste `CORRECTING`, verrouillée)."""
    if job.status != CorrectionJobStatus.FAILED:
        raise CorrectionJobNotFailedError(f"Job {job.id} n'est pas FAILED (status={job.status.value}).")
    job.status = CorrectionJobStatus.PENDING
    job.error_message = None
    job.started_at = None
    job.attempt_count = 0
    db.commit()
    return job


class SessionNotCompletedError(ValueError):
    """La comparaison de sévérité (§ A du ticket #70) n'a de sens que sur une session déjà
    terminée — jamais sur une session `IN_PROGRESS` (pas encore de correction de
    référence à comparer)."""


@dataclass(frozen=True)
class SeverityComparison:
    """Résultat d'une simulation de re-cotation (ticket #70 § A) — jamais persisté, jamais
    utilisé pour modifier `session.score`/les `SessionAnswer` existants. Purement informatif,
    recalculé à chaque demande."""

    severity_ui: int
    severity_label: str
    original_score: float
    comparative_score: float
    question_count: int


def simulate_severity_comparison(
    db: DBSession, *, session: QuestionnaireSession, provider: AIProvider, severity_ui: int
) -> SeverityComparison:
    """« Comparer une autre sévérité » (ticket #70 § A) — simule une correction à une
    AUTRE sévérité SANS JAMAIS modifier le résultat original : ni les réponses, ni la
    correction déjà enregistrée (`SessionAnswer.points_awarded`/`feedback_json`), ni
    `session.score`. Cette fonction ne fait AUCUNE écriture en base (aucun `db.add`, aucun
    `db.commit`) — une simulation comparative séparée, recalculée à la demande, jamais une
    seconde vérité stockée.

    Seules les questions SÉMANTIQUES (notées par IA) peuvent réellement varier d'une
    sévérité à l'autre : `correct_session_hybrid` reste le même moteur que
    `submit_session`, qui verrouille TOUJOURS le score des questions déterministes sur
    `correct_locally` (indépendant de la sévérité, voir `_lock_score_keep_ai_explanation`
    dans `app.v1.hybrid_correction`) — la différence entre `original_score` et
    `comparative_score` ne peut donc jamais provenir d'une question à réponse fermée
    (QCM/classification/ordering/...), uniquement des réponses rédigées notées par IA.

    Déclenche UN appel IA supplémentaire, explicitement demandé par l'utilisateur — hors
    de l'invariant « un seul appel IA par session » du ticket #55, qui ne régit que la
    création et la soumission initiales, jamais une comparaison a posteriori demandée
    volontairement. Peut lever `AIProviderError`, jamais rattrapée ici (à l'appelant, la
    route, de l'afficher proprement)."""
    if session.status != SessionStatus.COMPLETED:
        raise SessionNotCompletedError(
            "La comparaison de sévérité n'est possible que sur une session terminée."
        )

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    questionnaire_questions, answers, human_readable_answers = _build_questionnaire_inputs(session_questions)
    questionnaire = Questionnaire(mode=session.mode.value, questions=questionnaire_questions)
    contexts = _contexts_for_session(db, session_questions)
    severity_internal = _SEVERITY_UI_TO_INTERNAL.get(severity_ui, "standard")

    correction = correct_session_hybrid(
        provider, questionnaire, answers, human_readable_answers, severity_internal, contexts
    )
    return SeverityComparison(
        severity_ui=severity_ui,
        severity_label=SEVERITY_UI_LABELS.get(severity_ui, str(severity_ui)),
        original_score=session.score,
        comparative_score=round(correction.score, 2),
        question_count=session.question_count,
    )

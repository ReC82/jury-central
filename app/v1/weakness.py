"""Points faibles V1 (ticket #75) : profil de fragilité par utilisateur et par notion,
renforcement ciblé à correction immédiate et examen ciblé.

Profil — jamais une seconde vérité stockée : il est recalculé à la demande depuis les
réponses déjà persistées (`SessionAnswer` → `SessionQuestion` → `QuestionVersion` →
`Question.uaa` / `Question.concepts`). Une réponse = une observation, quelle que soit la
manière dont elle a été relue : la « comparaison d'une autre sévérité » (#70) ne modifie
jamais la correction enregistrée, elle ne peut donc jamais être comptée deux fois.

Sources (§ G) : entraînements et examens blancs terminés (`COMPLETED`), et chaque réponse
corrigée d'un renforcement ciblé (corrigée dès sa validation). Les parties de quiz restent
une activité ludique distincte (#137) et ne comptent pas. Une réponse en erreur technique
(`FAILED`) ou en attente de correction n'est jamais une observation.

Granularité (§ B) : une question étiquetée par des notions (`Question.concepts`, table
`v1_concepts` déjà prévue par #38) alimente chaque notion du cours ; sinon, repli sur le
mini-cours (UAA). La banque actuelle n'a encore aucune notion étiquetée : le profil est
donc aujourd'hui par cours, et deviendra plus fin sans changement de code dès qu'un
étiquetage existera.

Score de fragilité (0-100, § A) — mise à jour séquentielle, de la plus ancienne réponse à
la plus récente (la récence pèse donc naturellement plus) :

    réussite partielle r = points obtenus / points max (0 = faux, 1 = juste)
    cible = 100 × (1 − r)
    score ← score + α × (cible − score)

- erreur (r < 0,5) : α = 0,5, × 1,2 si la question est facile, × 0,8 si elle est
  difficile — rater une question facile révèle davantage une fragilité ;
- réussite (r ≥ 0,5) : α = 0,35, × 0,8 si facile, × 1,2 si difficile, et × 1,15 en
  examen (réussite sans aide), × 0,9 en renforcement (la correction vient d'être lue).

Conséquences voulues : deux erreurs d'affilée pèsent plus qu'une (50 → 75 → 87,5) ; une
réponse partielle augmente moins qu'une erreur totale ; une seule réussite ne remet
jamais à zéro (87,5 → 57) ; plusieurs réussites font chuter le score (→ 37 → 24 → 16).

Affichage (§ F) : jamais le nombre brut, seulement un niveau — Prioritaire / Fragile /
À consolider / Fort — avec « peu de données » tant que moins de 3 réponses existent, la
date de la dernière erreur et une tendance (comparaison avec le score d'avant la
dernière session ayant porté sur la notion).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm.attributes import flag_modified

from app import models
from app.v1.ai_bridge import CORRECTABLE_TYPES
from app.v1.bank import _exclude_unusable_assets, _seen_signatures, _split_unseen_and_seen
from app.v1.dedup import find_near_duplicate, question_signature
from app.v1.models import (
    AnswerCorrectionStatus,
    Concept,
    ContentStatus,
    Question,
    QuestionDifficulty,
    QuestionnaireSession,
    QuestionVersion,
    SessionAnswer,
    SessionDifficultyRequest,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    UserQuestionHistory,
)
from app.v1.quiz_service import (
    QUIZ_QUESTION_TYPES,
    current_position,
    is_validated,
    ordered_questions,
    validate_quiz_answer,
)
from app.v1.session_service import (
    LONG_SEMANTIC_TYPES,
    MAX_LONG_SEMANTIC_PER_SESSION,
    WEAKNESS_EXAM_SCOPE,
    _finalize_session,
    add_session_question,
    deduplicate_intra_session,
)

EVIDENCE_MODES = (SessionMode.PRACTICE, SessionMode.EXAM, SessionMode.REINFORCEMENT)

ALPHA_ERROR = 0.5
ALPHA_SUCCESS = 0.35
ERROR_THRESHOLD = 0.5  # r < 0,5 : observation comptée comme une erreur
ERROR_DIFFICULTY_FACTOR = {"easy": 1.2, "medium": 1.0, "hard": 0.8}
SUCCESS_DIFFICULTY_FACTOR = {"easy": 0.8, "medium": 1.0, "hard": 1.2}
SUCCESS_MODE_FACTOR = {
    SessionMode.EXAM: 1.15,
    SessionMode.PRACTICE: 1.0,
    SessionMode.REINFORCEMENT: 0.9,
}

# (seuil, clé, libellé) du plus fragile au plus solide.
LEVELS = (
    (65.0, "prioritaire", "Prioritaire"),
    (40.0, "fragile", "Fragile"),
    (20.0, "a_consolider", "À consolider"),
    (0.0, "fort", "Fort"),
)
ACTIVE_THRESHOLD = 20.0  # « À consolider » et au-delà : point faible actif
LOW_DATA_ANSWERS = 3
TREND_DELTA = 8.0

MIX_TARGETS = 3
REINFORCEMENT_INITIAL_QUESTIONS = 6
REINFORCEMENT_MAX_QUESTIONS = 10
REINFORCEMENT_KEY = "reinforcement"

WEAKNESS_EXAM_LENGTHS = (10, 20)
WEAKNESS_EXAM_TARGETS = 5
WEAKNESS_EXAM_MIN_QUESTIONS = 3


class WeaknessError(Exception):
    """Renforcement ou examen ciblé impossible (aucun point faible, aucune question…)."""


# --- Profil ------------------------------------------------------------------------------


@dataclass
class Observation:
    session_id: int
    session_question_id: int
    mode: SessionMode
    ratio: float
    difficulty: str
    at: datetime


@dataclass
class WeaknessEntry:
    key: str
    uaa: models.UAA
    concept: Concept | None
    score: float
    answers: int
    errors: int
    partials: int
    successes: int
    last_error_at: datetime | None
    last_answer_at: datetime | None
    trend: str  # nouveau | amelioration | stable | degradation
    history: list[float] = field(default_factory=list)

    @property
    def label(self) -> str:
        course = f"{self.uaa.code} — {self.uaa.title}"
        return f"{course} / {self.concept.label}" if self.concept else course

    @property
    def level(self) -> tuple[str, str]:
        return level_for(self.score)

    @property
    def level_key(self) -> str:
        return self.level[0]

    @property
    def level_label(self) -> str:
        return self.level[1]

    @property
    def active(self) -> bool:
        return self.score >= ACTIVE_THRESHOLD

    @property
    def low_data(self) -> bool:
        return self.answers < LOW_DATA_ANSWERS

    @property
    def module(self) -> models.Module:
        return self.uaa.module


def level_for(score: float) -> tuple[str, str]:
    for threshold, key, label in LEVELS:
        if score >= threshold:
            return key, label
    return LEVELS[-1][1], LEVELS[-1][2]


def entry_key(uaa_id: int, concept_id: int | None = None) -> str:
    return f"u{uaa_id}c{concept_id}" if concept_id else f"u{uaa_id}"


def _difficulty_band(question: Question) -> str:
    if question.difficulty_declared is not None:
        return question.difficulty_declared.value
    rating = question.difficulty_rating
    if rating is None:
        return QuestionDifficulty.MEDIUM.value
    if rating < 950:
        return QuestionDifficulty.EASY.value
    if rating > 1050:
        return QuestionDifficulty.HARD.value
    return QuestionDifficulty.MEDIUM.value


def update_score(score: float, observation: Observation) -> float:
    """Une étape de la mise à jour séquentielle (voir docstring du module)."""
    error = 1.0 - observation.ratio
    if observation.ratio < ERROR_THRESHOLD:
        alpha = ALPHA_ERROR * ERROR_DIFFICULTY_FACTOR.get(observation.difficulty, 1.0)
    else:
        alpha = (
            ALPHA_SUCCESS
            * SUCCESS_DIFFICULTY_FACTOR.get(observation.difficulty, 1.0)
            * SUCCESS_MODE_FACTOR.get(observation.mode, 1.0)
        )
    alpha = min(alpha, 1.0)
    return score + alpha * (100.0 * error - score)


def score_observations(observations: list[Observation]) -> list[float]:
    """Scores successifs après chaque observation (ordre chronologique)."""
    score = 0.0
    history = []
    for observation in observations:
        score = update_score(score, observation)
        history.append(score)
    return history


def _observations_by_key(
    db: DBSession, *, user_id: int, module_id: int | None = None
) -> tuple[dict[str, list[Observation]], dict[str, tuple[models.UAA, Concept | None]]]:
    query = (
        db.query(SessionAnswer, SessionQuestion, QuestionnaireSession, Question)
        .join(SessionQuestion, SessionQuestion.id == SessionAnswer.session_question_id)
        .join(QuestionnaireSession, QuestionnaireSession.id == SessionQuestion.session_id)
        .join(QuestionVersion, QuestionVersion.id == SessionQuestion.question_version_id)
        .join(Question, Question.id == QuestionVersion.question_id)
        .filter(
            QuestionnaireSession.user_id == user_id,
            QuestionnaireSession.mode.in_(EVIDENCE_MODES),
            or_(
                QuestionnaireSession.status == SessionStatus.COMPLETED,
                QuestionnaireSession.mode == SessionMode.REINFORCEMENT,
            ),
            SessionAnswer.correction_status == AnswerCorrectionStatus.CORRECTED,
            SessionAnswer.points_awarded.is_not(None),
            Question.uaa_id.is_not(None),
        )
    )
    if module_id is not None:
        query = query.filter(Question.module_id == module_id)

    by_key: dict[str, list[Observation]] = {}
    targets: dict[str, tuple[models.UAA, Concept | None]] = {}
    for answer, session_question, session, question in query.all():
        points_max = session_question.points_max or 1.0
        ratio = max(0.0, min(1.0, (answer.points_awarded or 0.0) / points_max))
        at = answer.answered_at or session.completed_at or session.created_at
        if at is not None and at.tzinfo is None:
            at = at.replace(tzinfo=UTC)
        observation = Observation(
            session_id=session.id,
            session_question_id=session_question.id,
            mode=session.mode,
            ratio=ratio,
            difficulty=_difficulty_band(question),
            at=at,
        )
        concepts = list(question.concepts) or [None]
        for concept in concepts:
            key = entry_key(question.uaa_id, concept.id if concept else None)
            by_key.setdefault(key, []).append(observation)
            targets.setdefault(key, (question.uaa, concept))
    for observations in by_key.values():
        observations.sort(key=lambda o: (o.at, o.session_question_id))
    return by_key, targets


def _trend(observations: list[Observation], history: list[float]) -> str:
    last_session = observations[-1].session_id
    first_of_last = next(i for i, o in enumerate(observations) if o.session_id == last_session)
    if first_of_last == 0:
        return "nouveau"
    delta = history[-1] - history[first_of_last - 1]
    if delta <= -TREND_DELTA:
        return "amelioration"
    if delta >= TREND_DELTA:
        return "degradation"
    return "stable"


def weakness_profile(
    db: DBSession, *, user_id: int, module_id: int | None = None
) -> list[WeaknessEntry]:
    """Toutes les notions/cours ayant au moins une réponse corrigée de l'utilisateur, du
    plus fragile au plus solide. Isolation stricte : seules ses propres sessions."""
    by_key, targets = _observations_by_key(db, user_id=user_id, module_id=module_id)
    entries = []
    for key, observations in by_key.items():
        history = score_observations(observations)
        uaa, concept = targets[key]
        errors = [o for o in observations if o.ratio < ERROR_THRESHOLD]
        entries.append(
            WeaknessEntry(
                key=key,
                uaa=uaa,
                concept=concept,
                score=round(history[-1], 1),
                answers=len(observations),
                errors=len(errors),
                partials=sum(1 for o in observations if 0 < o.ratio < 1),
                successes=sum(1 for o in observations if o.ratio >= 1),
                last_error_at=errors[-1].at if errors else None,
                last_answer_at=observations[-1].at,
                trend=_trend(observations, history),
                history=history,
            )
        )
    entries.sort(key=lambda e: (-e.score, e.uaa.code, e.key))
    return entries


def active_weaknesses(entries: list[WeaknessEntry]) -> list[WeaknessEntry]:
    return [e for e in entries if e.active]


# --- Banque disponible pour une cible -----------------------------------------------------


def _target_query(db: DBSession, entry: WeaknessEntry, question_types) -> list[Question]:
    query = (
        db.query(Question)
        .join(QuestionVersion, QuestionVersion.id == Question.current_version_id)
        .filter(
            Question.status == ContentStatus.ACTIVE,
            Question.uaa_id == entry.uaa.id,
            QuestionVersion.question_type.in_(tuple(question_types)),
        )
    )
    if entry.concept is not None:
        query = query.filter(Question.concepts.any(Concept.id == entry.concept.id))
    return _exclude_unusable_assets(db, query).all()


def available_reinforcement_counts(db: DBSession, entries: list[WeaknessEntry]) -> dict[str, int]:
    """Questions à correction immédiate disponibles par cible (bouton désactivé à 0)."""
    return {entry.key: len(_target_query(db, entry, QUIZ_QUESTION_TYPES)) for entry in entries}


def _ordered_pool(
    db: DBSession, *, user: User, entry: WeaknessEntry, question_types, exclude_ids: set[int]
) -> list[Question]:
    """Jamais vues d'abord (ni par identité ni par quasi-doublon), puis déjà vues, les
    moins récemment vues en premier — de vrais nouveaux cas avant toute répétition."""
    candidates = [q for q in _target_query(db, entry, question_types) if q.id not in exclude_ids]
    random.shuffle(candidates)
    last_seen = {
        question_id: seen_at
        for question_id, seen_at in db.query(
            UserQuestionHistory.question_id, UserQuestionHistory.last_seen_at
        ).filter_by(user_id=user.id)
    }
    unseen, seen = _split_unseen_and_seen(
        candidates,
        seen_question_ids=set(last_seen),
        seen_signatures=_seen_signatures(db, user_id=user.id),
    )
    epoch = datetime.min.replace(tzinfo=UTC)

    def seen_at(question: Question) -> datetime:
        value = last_seen.get(question.id)
        if value is None:
            return epoch
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    seen.sort(key=seen_at)
    return unseen + seen


def _pick_round_robin(
    pools: list[list[Question]], count: int, *, max_long: int | None = None
) -> list[Question]:
    """Une question par cible à tour de rôle (cibles déjà triées de la plus fragile à la
    moins fragile), sans doublon intra-session ; `max_long` borne les réponses longues."""
    selected: list[Question] = []
    long_count = 0
    progressed = True
    while len(selected) < count and progressed:
        progressed = False
        for pool in pools:
            if len(selected) >= count:
                break
            while pool:
                candidate = pool.pop(0)
                is_long = candidate.current_version.question_type in LONG_SEMANTIC_TYPES
                if is_long and max_long is not None and long_count >= max_long:
                    continue
                if len(deduplicate_intra_session([*selected, candidate])) != len(selected) + 1:
                    continue
                selected.append(candidate)
                long_count += int(is_long)
                progressed = True
                break
    return selected


def _target_payload(entry: WeaknessEntry) -> dict:
    return {
        "key": entry.key,
        "uaa_id": entry.uaa.id,
        "concept_id": entry.concept.id if entry.concept else None,
        "label": entry.label,
        "score_before": entry.score,
        "level_before": entry.level_label,
    }


# --- Renforcement ciblé (§ C/D/H) ----------------------------------------------------------


def reinforcement_params(session: QuestionnaireSession) -> dict:
    return (session.parameters_json or {}).get(REINFORCEMENT_KEY) or {}


def get_owned_reinforcement(
    db: DBSession, *, session_id: int, user: User
) -> QuestionnaireSession | None:
    session = db.get(QuestionnaireSession, session_id)
    if session is None or session.user_id != user.id or session.mode != SessionMode.REINFORCEMENT:
        return None
    return session


def in_progress_reinforcements(db: DBSession, user: User) -> list[QuestionnaireSession]:
    return (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id, mode=SessionMode.REINFORCEMENT, status=SessionStatus.IN_PROGRESS)
        .order_by(QuestionnaireSession.created_at.desc())
        .all()
    )


def recent_reinforcements(db: DBSession, user: User, *, limit: int = 5) -> list[QuestionnaireSession]:
    return (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id, mode=SessionMode.REINFORCEMENT, status=SessionStatus.COMPLETED)
        .order_by(QuestionnaireSession.completed_at.desc())
        .limit(limit)
        .all()
    )


def resolve_targets(
    entries: list[WeaknessEntry],
    *,
    keys: list[str] | tuple[str, ...] = (),
    uaa_slugs: list[str] | tuple[str, ...] = (),
    module_id: int | None = None,
) -> tuple[str, list[WeaknessEntry]]:
    """`keys` : « Renforcer ce point faible » ; `uaa_slugs` : les cours ratés d'une session
    (page résultats) ; sinon « Travailler mes points faibles » : mix des principaux points
    faibles actifs (d'un module si `module_id`). Une clé étrangère au profil est ignorée."""
    if keys:
        wanted = set(keys)
        return "cible", [e for e in entries if e.key in wanted]
    if uaa_slugs:
        wanted_uaas = set(uaa_slugs)
        chosen = [e for e in entries if e.uaa.slug in wanted_uaas and e.concept is None]
        return "session", chosen[:MIX_TARGETS]
    pool = [e for e in active_weaknesses(entries) if module_id is None or e.uaa.module_id == module_id]
    return "mix", pool[:MIX_TARGETS]


def _reinforcement_label(kind: str, targets: list[WeaknessEntry]) -> str:
    if len(targets) == 1:
        return targets[0].label
    if kind == "session":
        return "Notions ratées de ma session"
    return "Mes principaux points faibles"


def start_reinforcement(
    db: DBSession, *, user: User, kind: str, targets: list[WeaknessEntry]
) -> QuestionnaireSession:
    if not targets:
        raise WeaknessError("Aucun point faible à renforcer pour l'instant.")
    signature = sorted(e.key for e in targets)
    for session in in_progress_reinforcements(db, user):
        if reinforcement_params(session).get("signature") == signature:
            return session  # reprise exacte, jamais une seconde session identique

    pools = [
        _ordered_pool(db, user=user, entry=e, question_types=QUIZ_QUESTION_TYPES, exclude_ids=set())
        for e in targets
    ]
    usable = [(e, pool) for e, pool in zip(targets, pools, strict=True) if pool]
    if not usable:
        raise WeaknessError(
            "Pas encore de question à correction immédiate (QCM, classement, remise en ordre) "
            "pour ce point faible."
        )
    selected = _pick_round_robin([pool for _, pool in usable], REINFORCEMENT_INITIAL_QUESTIONS)
    used = [e for e, _ in usable]
    parameters = {
        "activity": REINFORCEMENT_KEY,
        REINFORCEMENT_KEY: {
            "label": _reinforcement_label(kind, used),
            "kind": kind,
            "targets": [_target_payload(e) for e in used],
            "skipped": [e.label for e in targets if e not in used],
            "max_questions": REINFORCEMENT_MAX_QUESTIONS,
            "added_variants": 0,
            "signature": signature,
        },
    }
    return _finalize_session(
        db, user=user, module_id=selected[0].module_id, mode=SessionMode.REINFORCEMENT,
        difficulty=SessionDifficultyRequest.ADAPTIVE, selected=selected, parameters_json=parameters,
    )


def _target_for(session: QuestionnaireSession, question: Question) -> dict | None:
    concept_ids = {c.id for c in question.concepts}
    for target in reinforcement_params(session).get("targets") or []:
        if target["uaa_id"] != question.uaa_id:
            continue
        if target.get("concept_id") and target["concept_id"] not in concept_ids:
            continue
        return target
    return None


def _add_variant_after_error(
    db: DBSession, *, session: QuestionnaireSession, session_question: SessionQuestion, user: User
) -> SessionQuestion | None:
    """Après une erreur (ou une réponse partielle) : une AUTRE question sur la même notion,
    servie plus loin dans la session — jamais la même ni un quasi-doublon de celle ratée,
    dans la limite de `max_questions`."""
    params = reinforcement_params(session)
    questions = ordered_questions(session)
    if len(questions) >= int(params.get("max_questions") or REINFORCEMENT_MAX_QUESTIONS):
        return None
    failed = session_question.question_version.question
    target = _target_for(session, failed)
    if target is None:
        return None
    entry = WeaknessEntry(
        key=target["key"], uaa=failed.uaa,
        concept=db.get(Concept, target["concept_id"]) if target.get("concept_id") else None,
        score=0.0, answers=0, errors=0, partials=0, successes=0,
        last_error_at=None, last_answer_at=None, trend="nouveau",
    )
    in_session = [sq.question_version.question for sq in questions]
    failed_signature = question_signature(
        session_question.question_version.question_type, session_question.question_version.content_json
    )
    pool = _ordered_pool(
        db, user=user, entry=entry, question_types=QUIZ_QUESTION_TYPES,
        exclude_ids={q.id for q in in_session},
    )
    for candidate in pool:
        version = candidate.current_version
        if find_near_duplicate(question_signature(version.question_type, version.content_json), [failed_signature]):
            continue
        if len(deduplicate_intra_session([*in_session, candidate])) != len(in_session) + 1:
            continue
        added = add_session_question(
            db, session=session, question=candidate, position=questions[-1].position + 1, user_id=user.id
        )
        session.question_count = len(questions) + 1
        params["added_variants"] = int(params.get("added_variants") or 0) + 1
        flag_modified(session, "parameters_json")
        db.flush()
        return added
    return None


def validate_reinforcement_answer(
    db: DBSession,
    *,
    session: QuestionnaireSession,
    session_question: SessionQuestion,
    answer_json: dict,
    user: User,
) -> SessionAnswer:
    """Correction immédiate (moteur du quiz, local et déterministe), puis, après une
    erreur, ajout d'une variante sur la même notion."""

    def after(answer: SessionAnswer) -> None:
        if answer.correction_status != AnswerCorrectionStatus.CORRECTED:
            return
        if (answer.feedback_json or {}).get("correct"):
            return
        _add_variant_after_error(db, session=session, session_question=session_question, user=user)

    return validate_quiz_answer(
        db, session=session, session_question=session_question, answer_json=answer_json,
        on_validated=after,
    )


def reinforcement_summary(db: DBSession, session: QuestionnaireSession) -> dict:
    """Bilan de fin : réussite par cible et niveau avant → maintenant."""
    params = reinforcement_params(session)
    profile = {e.key: e for e in weakness_profile(db, user_id=session.user_id)}
    rows = []
    per_target: dict[str, dict] = {}
    for target in params.get("targets") or []:
        now = profile.get(target["key"])
        per_target[target["key"]] = {
            **target,
            "asked": 0,
            "correct": 0,
            "entry": now,
            "level_now": now.level_label if now else target.get("level_before"),
            "level_now_key": now.level_key if now else None,
        }
    for sq in ordered_questions(session):
        answer = sq.answer
        counted = answer is not None and answer.correction_status == AnswerCorrectionStatus.CORRECTED
        correct = counted and bool((answer.feedback_json or {}).get("correct"))
        question = sq.question_version.question
        target = _target_for(session, question)
        rows.append({"session_question": sq, "uaa": question.uaa, "counted": counted, "correct": correct})
        if target is not None and counted:
            per_target[target["key"]]["asked"] += 1
            per_target[target["key"]]["correct"] += int(correct)
    counted_total = sum(1 for r in rows if r["counted"])
    correct_total = sum(1 for r in rows if r["correct"])
    return {
        "rows": rows,
        "targets": list(per_target.values()),
        "counted_total": counted_total,
        "correct_total": correct_total,
        "added_variants": int(params.get("added_variants") or 0),
    }


def reinforcement_state(session: QuestionnaireSession) -> dict:
    questions = ordered_questions(session)
    return {
        "total": len(questions),
        "done": sum(1 for sq in questions if is_validated(sq)),
        "position": current_position(session),
    }


# --- Examen ciblé points faibles (§ E) -----------------------------------------------------


def in_progress_weakness_exam(
    db: DBSession, *, user: User, module_id: int
) -> QuestionnaireSession | None:
    sessions = (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id, module_id=module_id, mode=SessionMode.EXAM, status=SessionStatus.IN_PROGRESS)
        .order_by(QuestionnaireSession.created_at.desc())
        .all()
    )
    return next(
        (s for s in sessions if (s.parameters_json or {}).get("scope") == WEAKNESS_EXAM_SCOPE), None
    )


def start_weakness_exam(
    db: DBSession, *, user: User, module: models.Module, count: int
) -> QuestionnaireSession:
    """Vrai test de progression : un examen blanc ordinaire (aucune correction avant la
    soumission, correction et sévérité habituelles) composé uniquement de questions des
    notions faibles actives du module — les plus fragiles servies en premier."""
    if count not in WEAKNESS_EXAM_LENGTHS:
        count = WEAKNESS_EXAM_LENGTHS[0]
    existing = in_progress_weakness_exam(db, user=user, module_id=module.id)
    if existing is not None:
        return existing
    targets = active_weaknesses(weakness_profile(db, user_id=user.id, module_id=module.id))
    targets = targets[:WEAKNESS_EXAM_TARGETS]
    if not targets:
        raise WeaknessError("Aucun point faible actif dans cette matière pour l'instant.")
    pools = [
        _ordered_pool(db, user=user, entry=e, question_types=CORRECTABLE_TYPES, exclude_ids=set())
        for e in targets
    ]
    selected = _pick_round_robin(pools, count, max_long=MAX_LONG_SEMANTIC_PER_SESSION)
    if len(selected) < WEAKNESS_EXAM_MIN_QUESTIONS:
        raise WeaknessError("Pas assez de questions disponibles sur ces points faibles.")
    parameters = {
        "scope": WEAKNESS_EXAM_SCOPE,
        "weakness": {
            "requested_count": count,
            "targets": [_target_payload(e) for e in targets],
        },
    }
    return _finalize_session(
        db, user=user, module_id=module.id, mode=SessionMode.EXAM,
        difficulty=SessionDifficultyRequest.ADAPTIVE, selected=selected, parameters_json=parameters,
    )

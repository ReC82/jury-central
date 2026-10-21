"""Administration de la banque de questions V1 (ticket #46).

Lecture : statistiques par module, recherche filtrée, détail d'une question (versions,
signalements, utilisation). Écriture, toujours sans suppression physique :
- modifier le contenu → nouvelle `QuestionVersion` (`add_question_version`), validée par
  le registre #40 ; les sessions passées gardent la version qu'elles ont servie ;
- changer le statut (actif, archivé, signalé, invalide, obsolète, à revoir) — seules les
  questions ACTIVE sont servies (`app.v1.bank`) ;
- régénérer une variante par IA (nouvelle Question, statut « à revoir » : jamais servie
  avant validation par l'admin) ;
- interrupteur de génération par module (`app.v1.generation_control`) ;
- marquer un signalement traité (`app.v1.feedback`)."""

import json
import statistics
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.ai.provider import AIProviderError
from app.ai.questionnaire import generate_questionnaire
from app.ai.schemas import QuestionnaireRequest
from app.models import UAA, Module
from app.v1.ai_bridge import BRIDGE_TYPES
from app.v1.ai_usage import KIND_ADMIN_VARIANT, UsageTrackingProvider, record_ai_usage
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.bank import persist_generated_questions
from app.v1.francais_plan import FRANCAIS_PLAN_BY_CODE
from app.v1.generation_control import get_generation_status, is_generation_paused
from app.v1.mc38_transversal import MC38_CODE
from app.v1.models import (
    AIUsageEvent,
    ContentStatus,
    GenerationSource,
    ModuleGenerationStatus,
    Question,
    QuestionFeedback,
    QuestionVersion,
    SessionQuestion,
    add_question_version,
)
from app.v1.question_engine import ContentValidationError, QuestionEngineError, validate_content

STATUS_LABELS: dict[ContentStatus, str] = {
    ContentStatus.ACTIVE: "Active",
    ContentStatus.ARCHIVED: "Archivée",
    ContentStatus.FLAGGED: "Signalée",
    ContentStatus.INVALID: "Invalide",
    ContentStatus.OBSOLETE: "Obsolète",
    ContentStatus.REVIEW_NEEDED: "À revoir",
}

SOURCE_LABELS: dict[GenerationSource, str] = {
    GenerationSource.AI_GENERATED: "Générée (IA)",
    GenerationSource.IMPORTED: "Importée",
    GenerationSource.MANUAL: "Manuelle",
}

REVIEW_STATUSES = (ContentStatus.FLAGGED, ContentStatus.REVIEW_NEEDED)
DEFAULT_PAGE_SIZE = 50


class BankAdminError(ValueError):
    """Action admin refusée — message affichable tel quel."""


def _month_start() -> datetime:
    now = datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _unresolved_feedback_counts(db: Session) -> dict[int, int]:
    rows = (
        db.query(QuestionFeedback.question_id, func.count(QuestionFeedback.id))
        .filter(QuestionFeedback.resolved_at.is_(None))
        .group_by(QuestionFeedback.question_id)
    )
    return {question_id: count for question_id, count in rows}


def _session_counts_by_question(db: Session) -> dict[int, int]:
    """Nombre de sessions distinctes dans lesquelles chaque question a été servie (toutes
    versions confondues)."""
    rows = (
        db.query(QuestionVersion.question_id, func.count(func.distinct(SessionQuestion.session_id)))
        .join(SessionQuestion, SessionQuestion.question_version_id == QuestionVersion.id)
        .group_by(QuestionVersion.question_id)
    )
    return {question_id: count for question_id, count in rows}


@dataclass
class UsageTotals:
    calls: int = 0
    generated_questions: int = 0
    ai_corrections: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0


def _usage_by_module(db: Session, *, since: datetime | None = None) -> dict[int | None, UsageTotals]:
    query = db.query(
        AIUsageEvent.module_id,
        func.sum(AIUsageEvent.calls),
        func.sum(AIUsageEvent.generated_questions),
        func.sum(AIUsageEvent.ai_corrections),
        func.sum(AIUsageEvent.input_tokens),
        func.sum(AIUsageEvent.output_tokens),
        func.sum(AIUsageEvent.estimated_cost),
    )
    if since is not None:
        query = query.filter(AIUsageEvent.created_at >= since)
    result: dict[int | None, UsageTotals] = {}
    for module_id, calls, generated, corrections, tokens_in, tokens_out, cost in query.group_by(AIUsageEvent.module_id):
        result[module_id] = UsageTotals(
            calls=int(calls or 0),
            generated_questions=int(generated or 0),
            ai_corrections=int(corrections or 0),
            input_tokens=int(tokens_in or 0),
            output_tokens=int(tokens_out or 0),
            estimated_cost=round(float(cost or 0.0), 4),
        )
    return result


@dataclass
class ModuleBankStats:
    module: Module
    total: int = 0
    by_status: dict[ContentStatus, int] = field(default_factory=dict)
    signaled: int = 0
    to_review: int = 0
    rating_min: float | None = None
    rating_median: float | None = None
    rating_max: float | None = None
    rated: int = 0
    attempts: int = 0
    successes: int = 0
    generated: int = 0
    imported: int = 0
    manual: int = 0
    reused: int = 0
    servings: int = 0
    generation_status: ModuleGenerationStatus = ModuleGenerationStatus.ACTIVE
    usage_total: UsageTotals = field(default_factory=UsageTotals)
    usage_month: UsageTotals = field(default_factory=UsageTotals)

    @property
    def success_rate(self) -> float | None:
        return round(100 * self.successes / self.attempts, 1) if self.attempts else None


def module_bank_stats(db: Session) -> list[ModuleBankStats]:
    """Statistiques par module, calculées sur la base (jamais estimées). Seuls les modules
    qui ont au moins une question en banque ou un usage IA sont listés."""
    feedback_counts = _unresolved_feedback_counts(db)
    session_counts = _session_counts_by_question(db)
    usage_total = _usage_by_module(db)
    usage_month = _usage_by_module(db, since=_month_start())

    stats: dict[int, ModuleBankStats] = {}
    ratings: dict[int, list[float]] = {}
    for question in db.query(Question).all():
        entry = stats.get(question.module_id)
        if entry is None:
            entry = stats[question.module_id] = ModuleBankStats(module=question.module)
            ratings[question.module_id] = []
        entry.total += 1
        entry.by_status[question.status] = entry.by_status.get(question.status, 0) + 1
        has_feedback = question.id in feedback_counts
        entry.signaled += has_feedback or question.status == ContentStatus.FLAGGED
        entry.to_review += has_feedback or question.status in REVIEW_STATUSES
        if question.difficulty_rating is not None:
            ratings[question.module_id].append(question.difficulty_rating)
        entry.attempts += question.times_served or 0
        entry.successes += question.times_correct or 0
        if question.generation_source == GenerationSource.AI_GENERATED:
            entry.generated += 1
        elif question.generation_source == GenerationSource.IMPORTED:
            entry.imported += 1
        else:
            entry.manual += 1
        served_in = session_counts.get(question.id, 0)
        entry.servings += served_in
        entry.reused += served_in >= 2

    for module_id in usage_total:
        if module_id is not None and module_id not in stats:
            module = db.get(Module, module_id)
            if module is not None:
                stats[module_id] = ModuleBankStats(module=module)
                ratings[module_id] = []

    for module_id, entry in stats.items():
        values = ratings[module_id]
        if values:
            entry.rated = len(values)
            entry.rating_min = round(min(values), 1)
            entry.rating_median = round(statistics.median(values), 1)
            entry.rating_max = round(max(values), 1)
        entry.generation_status = get_generation_status(db, module_id)
        entry.usage_total = usage_total.get(module_id, UsageTotals())
        entry.usage_month = usage_month.get(module_id, UsageTotals())

    return sorted(stats.values(), key=lambda s: (s.module.subject.name if s.module.subject else "", s.module.code))


def usage_without_module(db: Session) -> UsageTotals:
    return _usage_by_module(db).get(None, UsageTotals())


@dataclass
class QuestionFilters:
    module_id: int | None = None
    uaa_id: int | None = None
    question_type: str | None = None
    status: ContentStatus | None = None
    rating_min: float | None = None
    rating_max: float | None = None
    text: str | None = None
    to_review: bool = False
    page: int = 1
    per_page: int = DEFAULT_PAGE_SIZE


def search_questions(db: Session, filters: QuestionFilters) -> tuple[list[Question], int]:
    query = db.query(Question).join(QuestionVersion, Question.current_version_id == QuestionVersion.id)
    if filters.module_id is not None:
        query = query.filter(Question.module_id == filters.module_id)
    if filters.uaa_id is not None:
        query = query.filter(Question.uaa_id == filters.uaa_id)
    if filters.question_type:
        query = query.filter(QuestionVersion.question_type == filters.question_type)
    if filters.status is not None:
        query = query.filter(Question.status == filters.status)
    if filters.rating_min is not None:
        query = query.filter(Question.difficulty_rating >= filters.rating_min)
    if filters.rating_max is not None:
        query = query.filter(Question.difficulty_rating <= filters.rating_max)
    if filters.text:
        needle = filters.text.strip()
        if needle.isdigit():
            query = query.filter(or_(Question.id == int(needle), cast(QuestionVersion.content_json, String).ilike(f"%{needle}%")))
        else:
            # Le JSON stocke les accents échappés (é) : on cherche les deux formes.
            escaped = json.dumps(needle)[1:-1]
            query = query.filter(
                or_(
                    cast(QuestionVersion.content_json, String).ilike(f"%{needle}%"),
                    cast(QuestionVersion.content_json, String).ilike(f"%{escaped}%"),
                )
            )
    if filters.to_review:
        unresolved = db.query(QuestionFeedback.question_id).filter(QuestionFeedback.resolved_at.is_(None))
        query = query.filter(or_(Question.status.in_(REVIEW_STATUSES), Question.id.in_(unresolved)))
    total = query.count()
    page = max(1, filters.page)
    items = (
        query.order_by(Question.id.desc())
        .offset((page - 1) * filters.per_page)
        .limit(filters.per_page)
        .all()
    )
    return items, total


def distinct_question_types(db: Session) -> list[str]:
    return [row[0] for row in db.query(QuestionVersion.question_type).distinct().order_by(QuestionVersion.question_type)]


def unresolved_feedback_counts(db: Session, question_ids: list[int]) -> dict[int, int]:
    if not question_ids:
        return {}
    rows = (
        db.query(QuestionFeedback.question_id, func.count(QuestionFeedback.id))
        .filter(QuestionFeedback.resolved_at.is_(None), QuestionFeedback.question_id.in_(question_ids))
        .group_by(QuestionFeedback.question_id)
    )
    return {question_id: count for question_id, count in rows}


def version_usage_counts(db: Session, question: Question) -> dict[int, int]:
    """Nombre de passages en session par version de la question."""
    rows = (
        db.query(SessionQuestion.question_version_id, func.count(SessionQuestion.id))
        .join(QuestionVersion, SessionQuestion.question_version_id == QuestionVersion.id)
        .filter(QuestionVersion.question_id == question.id)
        .group_by(SessionQuestion.question_version_id)
    )
    return {version_id: count for version_id, count in rows}


def question_versions(db: Session, question: Question) -> list[QuestionVersion]:
    return (
        db.query(QuestionVersion)
        .filter_by(question_id=question.id)
        .order_by(QuestionVersion.version.desc())
        .all()
    )


def question_feedback(db: Session, question: Question) -> list[QuestionFeedback]:
    return (
        db.query(QuestionFeedback)
        .filter_by(question_id=question.id)
        .order_by(QuestionFeedback.resolved_at.isnot(None), QuestionFeedback.created_at.desc())
        .all()
    )


def edit_question_content(db: Session, question: Question, raw_content: str) -> QuestionVersion:
    """Modifier = créer une nouvelle version (jamais de modification en place). Le type
    de question ne change pas ; le contenu doit être un JSON valide pour ce type."""
    current = question.current_version
    if current is None:
        raise BankAdminError("Question sans version courante.")
    try:
        content: Any = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise BankAdminError(f"JSON invalide : {exc.msg} (ligne {exc.lineno}).") from exc
    if not isinstance(content, dict):
        raise BankAdminError("Le contenu doit être un objet JSON.")
    if content == current.content_json:
        raise BankAdminError("Aucune modification : le contenu est identique à la version courante.")
    try:
        validate_content(current.question_type, current.schema_version, content)
    except ContentValidationError as exc:
        details = "; ".join(getattr(exc, "errors", []) or [str(exc)])
        raise BankAdminError(f"Contenu refusé pour le type {current.question_type} : {details}") from exc
    except QuestionEngineError as exc:
        raise BankAdminError(str(exc)) from exc
    version = add_question_version(
        db,
        question,
        question_type=current.question_type,
        content_json=content,
        generator_model=current.generator_model,
        prompt_version=current.prompt_version,
        source_program_version=current.source_program_version,
        source_document_version_id=current.source_document_version_id,
    )
    question.updated_at = datetime.now(UTC)
    db.flush()
    return version


def set_question_status(db: Session, question: Question, status: ContentStatus) -> None:
    question.status = status
    question.updated_at = datetime.now(UTC)
    db.flush()


def _variant_context(question: Question):
    """Contexte pédagogique pour régénérer une variante, ou raison du refus."""
    from app.v1.session_service import _pedagogical_context_for

    uaa: UAA | None = question.uaa
    if uaa is None or uaa.code is None:
        return None, "Question sans mini-cours rattaché : variante impossible."
    if uaa.code not in AMPCR_PLAN_BY_CODE and uaa.code not in FRANCAIS_PLAN_BY_CODE:
        # FSE : banque rédigée à la main uniquement, jamais de génération IA (#96).
        return None, "Ce module n'utilise pas la génération IA (banque rédigée à la main)."
    if uaa.code == MC38_CODE:
        # MC38 : révision transversale, son propre contexte produirait des questions méta (#58).
        return None, "MC38 (révision transversale) : régénère la variante depuis le mini-cours d'origine."
    context = _pedagogical_context_for(uaa.code)
    if context.course_key == "ampcr-global":
        return None, "Contexte pédagogique du mini-cours introuvable : variante impossible."
    return context, None


def variant_unavailable_reason(db: Session, question: Question) -> str | None:
    current = question.current_version
    if current is None:
        return "Question sans version courante."
    _, reason = _variant_context(question)
    if reason is not None:
        return reason
    if current.question_type not in BRIDGE_TYPES:
        return f"Le type {current.question_type} ne peut pas être généré par l'IA."
    if current.source_document_version_id is not None:
        return "Question liée à un document source : variante impossible."
    if is_generation_paused(db, question.module_id):
        return "Génération en pause pour ce module."
    return None


def regenerate_variant(db: Session, question: Question, provider) -> Question:
    """Une variante = une NOUVELLE question du même type et du même mini-cours, produite
    par un appel IA unique, passée par les mêmes validations que toute génération
    (structure, domaine, qualité, anti-doublon) et créée au statut « à revoir » — jamais
    servie avant validation par l'admin. La question d'origine n'est pas modifiée."""
    reason = variant_unavailable_reason(db, question)
    if reason is not None:
        raise BankAdminError(reason)
    context, _ = _variant_context(question)
    current = question.current_version
    request = QuestionnaireRequest(
        contexts=(context,),
        mode="practice",
        difficulty={"easy": "facile", "hard": "difficile"}.get(
            question.difficulty_declared.value if question.difficulty_declared else "", "moyen"
        ),
        question_count=1,
        allowed_types=(current.question_type,),
        avoid_prompts=(str(current.content_json.get("prompt", "")),),
    )
    tracker = UsageTrackingProvider(provider)
    try:
        questionnaire = generate_questionnaire(tracker, request)
        persisted = persist_generated_questions(
            db, module_id=question.module_id, uaa_id=question.uaa_id, questions=questionnaire.questions
        )
    except AIProviderError as exc:
        record_ai_usage(db, tracker, kind=KIND_ADMIN_VARIANT, module_id=question.module_id, failed=True)
        raise BankAdminError(f"Génération IA indisponible : {exc}") from exc
    record_ai_usage(db, tracker, kind=KIND_ADMIN_VARIANT, module_id=question.module_id, failed=not persisted)
    if not persisted:
        raise BankAdminError(
            "L'IA n'a produit aucune variante valide (rejetée par la validation ou trop proche "
            "d'une question existante). Réessaie."
        )
    variant = persisted[0]
    variant.status = ContentStatus.REVIEW_NEEDED
    variant.difficulty_declared = question.difficulty_declared
    db.flush()
    return variant

"""Service — Examen blanc CESS Français (chantier prioritaire, mode Examen blanc).

Même discipline async que #88/#90/#92 (jamais un appel IA dans le cycle requête/réponse
HTTP), mais SANS job séparé : `FrenchMockExam.status` EST son propre job — le worker
réclame atomiquement les lignes `PENDING` (build) / `SUBMITTED` (correction) via la même
primitive UPDATE-claim que `claim_next_pending_correction_job`/`claim_next_pending_build_job`
(voir `app.v1.session_service`), appliquée directement à cette table plutôt qu'à une table
de job dédiée (§ 46 du chantier : « créer uniquement le nécessaire »)."""

import hashlib
import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session as DBSession

from app.ai.french_mock_exam_schemas import MockExamGenerationRequest
from app.ai.provider import AIProvider, AIProviderError
from app.v1.french_mock_exam_themes import MOCK_EXAM_THEMES
from app.v1.models import (
    FrenchMockExam,
    FrenchMockExamStatus,
    FrenchMockExamType,
    User,
    create_source_document,
)

DEFAULT_SYNTHESIS_MIN_WORDS = 350
DEFAULT_SYNTHESIS_MAX_WORDS = 450
DEFAULT_ARGUMENTATION_MIN_WORDS = 400
DEFAULT_ARGUMENTATION_MAX_WORDS = 550

# § 3/§ 30 : combien de sessions récentes consulter pour l'anti-répétition — pas un
# algorithme complexe, une simple fenêtre glissante.
RECENT_THEME_WINDOW = 5
RECENT_TYPE_WINDOW = 3

MockExamMode = str  # "surprise" | "synthesis" | "argumentation"


class MockExamNotReadyError(ValueError):
    pass


class MockExamNotSubmittableError(ValueError):
    pass


class MockExamNotRetryableError(ValueError):
    pass


# =============================================================================================
# Sélection thème / type (§ 3, § 4, § 27, § 30 — anti-répétition simple, jamais un
# algorithme complexe ni une base vectorielle)
# =============================================================================================


def _recent_exams(db: DBSession, *, user_id: int, limit: int) -> list[FrenchMockExam]:
    return (
        db.query(FrenchMockExam)
        .filter(FrenchMockExam.user_id == user_id)
        .order_by(FrenchMockExam.created_at.desc())
        .limit(limit)
        .all()
    )


def choose_theme(db: DBSession, *, user_id: int) -> tuple[str, str]:
    """Évite les `theme_key` des `RECENT_THEME_WINDOW` dernières sessions de cet
    utilisateur — si tous les thèmes du catalogue ont été récemment utilisés (peu
    probable avec 20 thèmes et une fenêtre de 5), retombe sur le catalogue complet plutôt
    que d'échouer."""
    recent = _recent_exams(db, user_id=user_id, limit=RECENT_THEME_WINDOW)
    recent_keys = {exam.theme_key for exam in recent}
    candidates = [t for t in MOCK_EXAM_THEMES if t[0] not in recent_keys]
    if not candidates:
        candidates = list(MOCK_EXAM_THEMES)
    # Déterministe mais varié : dérivé du nombre de sessions déjà créées par
    # l'utilisateur plutôt qu'un `random` non testable de façon fiable.
    index = db.query(FrenchMockExam).filter(FrenchMockExam.user_id == user_id).count() % len(candidates)
    return candidates[index]


def choose_exam_type(db: DBSession, *, user_id: int, mode: MockExamMode) -> FrenchMockExamType:
    """§ 2/§ 27 : mode Surprise — équilibre SYNTHESIS vs ARGUMENTATION (si les 2 derniers
    types sont de la même famille, force l'autre famille) et, au sein d'ARGUMENTATION,
    alterne OPINION/REQUEST. Modes ciblés (§ 1) : type fixé, seule l'alternance
    OPINION/REQUEST reste appliquée pour le mode « argumentation »."""
    recent = _recent_exams(db, user_id=user_id, limit=RECENT_TYPE_WINDOW)
    recent_types = [exam.exam_type for exam in recent]

    if mode == "synthesis":
        return FrenchMockExamType.SYNTHESIS
    if mode == "argumentation":
        return _choose_argumentation_subtype(recent_types)

    # Mode surprise (§ 2/§ 27).
    if recent_types and all(t == recent_types[0] for t in recent_types[: min(2, len(recent_types))]):
        last_family_is_synthesis = recent_types[0] == FrenchMockExamType.SYNTHESIS
        if last_family_is_synthesis:
            return _choose_argumentation_subtype(recent_types)
        return FrenchMockExamType.SYNTHESIS

    # Pas de répétition détectée : alterne simplement selon la parité du nombre de
    # sessions déjà créées (déterministe, testable, « pas besoin d'algorithme complexe »).
    total = db.query(FrenchMockExam).filter(FrenchMockExam.user_id == user_id).count()
    if total % 2 == 0:
        return FrenchMockExamType.SYNTHESIS
    return _choose_argumentation_subtype(recent_types)


def _choose_argumentation_subtype(recent_types: list[FrenchMockExamType]) -> FrenchMockExamType:
    last_argumentation = next(
        (t for t in recent_types if t != FrenchMockExamType.SYNTHESIS), None
    )
    if last_argumentation == FrenchMockExamType.ARGUMENTATION_OPINION:
        return FrenchMockExamType.ARGUMENTATION_REQUEST
    return FrenchMockExamType.ARGUMENTATION_OPINION


def _word_bounds_for(exam_type: FrenchMockExamType) -> tuple[int, int]:
    if exam_type == FrenchMockExamType.SYNTHESIS:
        return DEFAULT_SYNTHESIS_MIN_WORDS, DEFAULT_SYNTHESIS_MAX_WORDS
    return DEFAULT_ARGUMENTATION_MIN_WORDS, DEFAULT_ARGUMENTATION_MAX_WORDS


def compute_signature(*, theme_key: str, exam_type: FrenchMockExamType, task_prompt: str) -> str:
    """§ 3 : signature courte, jamais une base vectorielle — theme_key + exam_type +
    empreinte courte de la tâche générée, suffisant pour détecter une répétition quasi
    identique sans comparaison sémantique lourde."""
    digest = hashlib.sha256(task_prompt.encode("utf-8")).hexdigest()[:16]
    return f"{theme_key}:{exam_type.value}:{digest}"


# =============================================================================================
# Démarrage (§ 1, § 2, § 31) — création immédiate, PENDING, jamais d'appel IA ici
# =============================================================================================


def start_mock_exam(db: DBSession, *, user: User, mode: MockExamMode) -> FrenchMockExam:
    theme_key, theme = choose_theme(db, user_id=user.id)
    exam_type = choose_exam_type(db, user_id=user.id, mode=mode)
    min_words, max_words = _word_bounds_for(exam_type)
    exam = FrenchMockExam(
        user_id=user.id,
        theme=theme,
        theme_key=theme_key,
        exam_type=exam_type,
        surprise_mode=(mode == "surprise"),
        min_words=min_words,
        max_words=max_words,
        status=FrenchMockExamStatus.PENDING,
        answer_text="",
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_mock_exam(db: DBSession, *, exam_id: int) -> FrenchMockExam | None:
    return db.get(FrenchMockExam, exam_id)


# =============================================================================================
# Build asynchrone (réutilise le PATTERN #92, pas la table SessionBuildJob)
# =============================================================================================


def claim_next_pending_mock_exam_build(db: DBSession, *, max_attempts: int = 3) -> FrenchMockExam | None:
    exam = (
        db.query(FrenchMockExam)
        .filter(FrenchMockExam.status == FrenchMockExamStatus.PENDING, FrenchMockExam.attempt_count < max_attempts)
        .order_by(FrenchMockExam.created_at)
        .first()
    )
    if exam is None:
        return None
    claim = db.execute(
        update(FrenchMockExam)
        .where(FrenchMockExam.id == exam.id, FrenchMockExam.status == FrenchMockExamStatus.PENDING)
        .values(
            status=FrenchMockExamStatus.BUILDING,
            started_at=datetime.now(UTC),
            attempt_count=FrenchMockExam.attempt_count + 1,
        )
    )
    db.commit()
    if claim.rowcount == 0:
        return None
    db.refresh(exam)
    return exam


def run_mock_exam_build(db: DBSession, *, exam: FrenchMockExam, provider: AIProvider) -> FrenchMockExam:
    """Ordre strict § 9 : thème/type déjà choisis (à la création, § « Sélection »), donc
    ici seulement génération des documents + tâche + grille + corrigé privé, PUIS
    validation (§ 28/§ 29) avant persistance. Jamais de faux succès : un dossier qui ne
    passe pas la validation est traité comme un échec de génération (`BUILD_FAILED`),
    jamais silencieusement accepté."""
    recent = _recent_exams(db, user_id=exam.user_id, limit=RECENT_TYPE_WINDOW)
    avoid_task_signatures = tuple(e.task_prompt[:80] for e in recent if e.task_prompt)
    request = MockExamGenerationRequest(
        exam_type=exam.exam_type.value,
        theme=exam.theme,
        min_words=exam.min_words,
        max_words=exam.max_words,
        avoid_task_signatures=avoid_task_signatures,
    )
    try:
        generation = provider.generate_french_mock_exam(request)
        _validate_generation(generation)
    except (AIProviderError, MockExamValidationError) as exc:
        db.rollback()
        exam.status = FrenchMockExamStatus.BUILD_FAILED
        exam.error_message = str(exc)[:2000]
        db.commit()
        return exam

    doc1 = create_source_document(db, title=generation.documents[0].title, content_text=generation.documents[0].text)
    doc2 = create_source_document(db, title=generation.documents[1].title, content_text=generation.documents[1].text)
    doc3 = create_source_document(db, title=generation.documents[2].title, content_text=generation.documents[2].text)
    db.flush()

    exam.document_1_id = doc1.current_version_id
    exam.document_2_id = doc2.current_version_id
    exam.document_3_id = doc3.current_version_id
    exam.task_prompt = generation.task_prompt
    exam.required_genre = generation.required_genre or None
    exam.recipient = generation.recipient or None
    exam.rubric_json = [
        {"name": c.name, "max_points": c.max_points, "criteria": c.criteria}
        for c in generation.rubric_categories
    ]
    exam.expected_information_json = {
        "key_ideas": [
            {"idea": k.idea, "source_document_indexes": k.source_document_indexes, "axis": k.axis}
            for k in generation.key_ideas
        ],
        "contradictions": generation.contradictions,
        "complements": generation.complements,
        "target_opinion": generation.target_opinion,
    }
    exam.signature = compute_signature(
        theme_key=exam.theme_key, exam_type=exam.exam_type, task_prompt=generation.task_prompt
    )
    exam.status = FrenchMockExamStatus.READY
    exam.completed_at = None
    db.commit()
    db.refresh(exam)
    return exam


class MockExamValidationError(ValueError):
    pass


_MIN_DOCUMENT_WORDS = 300  # § 8 : cible 500-900, plancher de validation tolérant (contenu réel IA)


def _validate_generation(generation) -> None:
    """§ 28/§ 29 : jamais persister un dossier qui ne peut pas servir. Volontairement
    tolérant sur la longueur exacte (« cible raisonnable », pas une règle dure) mais
    strict sur les invariants structurels (3 documents, angles distincts, tâche non
    vide, grille sommant à 100)."""
    if len(generation.documents) != 3:
        raise MockExamValidationError("Le dossier généré ne comporte pas exactement 3 documents.")
    for doc in generation.documents:
        word_count = len(doc.text.split())
        if word_count < _MIN_DOCUMENT_WORDS:
            raise MockExamValidationError(f"Document « {doc.title} » trop court ({word_count} mots).")
    kinds = {doc.doc_kind for doc in generation.documents}
    if len(kinds) < 2:
        raise MockExamValidationError("Les documents générés n'ont pas d'angles suffisamment différents.")
    if not generation.task_prompt.strip():
        raise MockExamValidationError("Tâche générée vide.")
    if not generation.rubric_categories:
        raise MockExamValidationError("Grille de correction vide.")
    total_points = sum(c.max_points for c in generation.rubric_categories)
    if not (95.0 <= total_points <= 105.0):
        raise MockExamValidationError(f"Grille de correction ne totalise pas 100 points ({total_points}).")


def recover_stale_mock_exam_builds(
    db: DBSession, *, stale_after_seconds: int = 300, max_attempts: int = 3
) -> dict[str, int]:
    threshold = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
    stale = (
        db.query(FrenchMockExam)
        .filter(FrenchMockExam.status == FrenchMockExamStatus.BUILDING, FrenchMockExam.started_at < threshold)
        .all()
    )
    requeued = failed = 0
    for exam in stale:
        if exam.attempt_count >= max_attempts:
            exam.status = FrenchMockExamStatus.BUILD_FAILED
            exam.error_message = "Génération restée bloquée trop longtemps — nombre maximal de tentatives atteint."
            failed += 1
        else:
            exam.status = FrenchMockExamStatus.PENDING
            exam.started_at = None
            requeued += 1
    db.commit()
    return {"requeued": requeued, "failed": failed}


def retry_mock_exam_build(db: DBSession, *, exam: FrenchMockExam) -> FrenchMockExam:
    if exam.status != FrenchMockExamStatus.BUILD_FAILED:
        raise MockExamNotRetryableError("Ce dossier n'est pas en échec — rien à relancer.")
    exam.status = FrenchMockExamStatus.PENDING
    exam.error_message = None
    exam.started_at = None
    db.commit()
    return exam


# =============================================================================================
# Rédaction / autosave (§ 32, § 33)
# =============================================================================================


def save_mock_exam_answer(
    db: DBSession, *, exam: FrenchMockExam, answer_text: str | None = None,
    preparation_table_json: dict | list | None = None,
) -> FrenchMockExam:
    if exam.status != FrenchMockExamStatus.READY:
        raise MockExamNotReadyError("Ce dossier n'est plus modifiable (déjà soumis ou pas encore prêt).")
    if answer_text is not None:
        exam.answer_text = answer_text
    if preparation_table_json is not None:
        exam.preparation_table_json = preparation_table_json
    db.commit()
    return exam


# =============================================================================================
# Soumission / correction asynchrone (réutilise le PATTERN #88/#90)
# =============================================================================================


def submit_mock_exam(db: DBSession, *, exam: FrenchMockExam) -> FrenchMockExam:
    """Réclamation atomique READY→SUBMITTED — un double POST retombe toujours sur la
    même ligne déjà SUBMITTED (ou au-delà), jamais une seconde soumission acceptée."""
    if exam.status != FrenchMockExamStatus.READY:
        return exam  # déjà soumis/en correction/terminé : idempotent, pas une erreur
    db.execute(
        update(FrenchMockExam)
        .where(FrenchMockExam.id == exam.id, FrenchMockExam.status == FrenchMockExamStatus.READY)
        .values(status=FrenchMockExamStatus.SUBMITTED, submitted_at=datetime.now(UTC))
    )
    db.commit()
    db.refresh(exam)
    return exam


def claim_next_pending_mock_exam_correction(db: DBSession, *, max_attempts: int = 3) -> FrenchMockExam | None:
    exam = (
        db.query(FrenchMockExam)
        .filter(FrenchMockExam.status == FrenchMockExamStatus.SUBMITTED, FrenchMockExam.attempt_count < max_attempts)
        .order_by(FrenchMockExam.submitted_at)
        .first()
    )
    if exam is None:
        return None
    claim = db.execute(
        update(FrenchMockExam)
        .where(FrenchMockExam.id == exam.id, FrenchMockExam.status == FrenchMockExamStatus.SUBMITTED)
        .values(
            status=FrenchMockExamStatus.CORRECTING,
            attempt_count=FrenchMockExam.attempt_count + 1,
        )
    )
    db.commit()
    if claim.rowcount == 0:
        return None
    db.refresh(exam)
    return exam


_WORD_RE = re.compile(r"[a-zàâäéèêëïîôöùûüçœæ]{4,}", re.IGNORECASE)


def _similarity_ratio(answer_text: str, documents_text: list[str]) -> float:
    """§ 42 : heuristique LÉGÈRE (jamais une détection NLP lourde), transmise à l'IA
    correctrice comme simple INDICATION — jamais un rejet automatique. Ratio de mots
    « significatifs » (4+ lettres) de la réponse également présents dans les documents
    source, sur l'ensemble des mots significatifs de la réponse."""
    answer_words = {w.lower() for w in _WORD_RE.findall(answer_text)}
    if not answer_words:
        return 0.0
    source_words: set[str] = set()
    for text in documents_text:
        source_words.update(w.lower() for w in _WORD_RE.findall(text))
    overlap = answer_words & source_words
    return round(len(overlap) / len(answer_words), 3)


def run_mock_exam_correction(db: DBSession, *, exam: FrenchMockExam, provider: AIProvider) -> FrenchMockExam:
    """§ 37 : jamais de 0 automatique si l'IA échoue — `CORRECTION_INCOMPLETE`, réponse
    de l'élève intacte, bouton de reprise cible la MÊME ligne (jamais une nouvelle
    session)."""
    documents = exam.documents
    doc_texts = [d.content_text or "" for d in documents]
    doc_tuples = [
        (d.title or "", "", d.content_text or "") for d in documents
    ]
    rubric = exam.rubric_json or []
    rubric_tuples = [(c["name"], c["max_points"], c.get("criteria") or []) for c in rubric]
    expected = exam.expected_information_json or {}
    key_ideas_tuples = [
        (k["idea"], k.get("source_document_indexes") or [], k.get("axis", ""))
        for k in expected.get("key_ideas") or []
    ]
    similarity_ratio = _similarity_ratio(exam.answer_text, doc_texts)

    try:
        correction = provider.correct_french_mock_exam(
            exam_type=exam.exam_type.value,
            task_prompt=exam.task_prompt or "",
            documents=doc_tuples,
            rubric_categories=rubric_tuples,
            key_ideas=key_ideas_tuples,
            contradictions=expected.get("contradictions") or [],
            complements=expected.get("complements") or [],
            answer_text=exam.answer_text,
            min_words=exam.min_words,
            max_words=exam.max_words,
            similarity_ratio=similarity_ratio,
        )
    except AIProviderError as exc:
        db.rollback()
        exam.status = FrenchMockExamStatus.CORRECTION_INCOMPLETE
        exam.error_message = str(exc)[:2000]
        db.commit()
        return exam

    exam.score = correction.score
    exam.max_score = correction.max_score
    exam.feedback_json = {
        "category_scores": [
            {"name": c.name, "points": c.points, "max_points": c.max_points, "comment": c.comment}
            for c in correction.category_scores
        ],
        "strengths": correction.strengths,
        "improvements": correction.improvements,
        "structure_feedback": correction.structure_feedback,
        "document_comprehension_feedback": correction.document_comprehension_feedback,
        "source_usage_feedback": correction.source_usage_feedback,
        "task_specific_feedback": correction.task_specific_feedback,
        "language_feedback": correction.language_feedback,
        "length_feedback": correction.length_feedback,
        "similarity_ratio": similarity_ratio,
    }
    exam.status = FrenchMockExamStatus.COMPLETED
    exam.completed_at = datetime.now(UTC)
    exam.error_message = None
    db.commit()
    db.refresh(exam)
    return exam


def recover_stale_mock_exam_corrections(
    db: DBSession, *, stale_after_seconds: int = 300, max_attempts: int = 3
) -> dict[str, int]:
    threshold = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
    stale = (
        db.query(FrenchMockExam)
        .filter(FrenchMockExam.status == FrenchMockExamStatus.CORRECTING, FrenchMockExam.submitted_at < threshold)
        .all()
    )
    requeued = failed = 0
    for exam in stale:
        if exam.attempt_count >= max_attempts:
            exam.status = FrenchMockExamStatus.CORRECTION_INCOMPLETE
            exam.error_message = "Correction restée bloquée trop longtemps — nombre maximal de tentatives atteint."
            failed += 1
        else:
            exam.status = FrenchMockExamStatus.SUBMITTED
            requeued += 1
    db.commit()
    return {"requeued": requeued, "failed": failed}


def retry_mock_exam_correction(db: DBSession, *, exam: FrenchMockExam) -> FrenchMockExam:
    if exam.status != FrenchMockExamStatus.CORRECTION_INCOMPLETE:
        raise MockExamNotRetryableError("Cette correction n'est pas en échec — rien à relancer.")
    exam.status = FrenchMockExamStatus.SUBMITTED
    exam.error_message = None
    db.commit()
    return exam


__all__ = [
    "DEFAULT_ARGUMENTATION_MAX_WORDS",
    "DEFAULT_ARGUMENTATION_MIN_WORDS",
    "DEFAULT_SYNTHESIS_MAX_WORDS",
    "DEFAULT_SYNTHESIS_MIN_WORDS",
    "MockExamNotReadyError",
    "MockExamNotRetryableError",
    "MockExamNotSubmittableError",
    "MockExamValidationError",
    "choose_exam_type",
    "choose_theme",
    "claim_next_pending_mock_exam_build",
    "claim_next_pending_mock_exam_correction",
    "compute_signature",
    "get_mock_exam",
    "recover_stale_mock_exam_builds",
    "recover_stale_mock_exam_corrections",
    "retry_mock_exam_build",
    "retry_mock_exam_correction",
    "run_mock_exam_build",
    "run_mock_exam_correction",
    "save_mock_exam_answer",
    "start_mock_exam",
    "submit_mock_exam",
]

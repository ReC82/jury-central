"""Signalements utilisateur sur une question (ticket #46, `QuestionFeedback`).

Un signalement vise la version exactement servie dans la session (jamais seulement la
question) et la réponse de l'utilisateur. Il ne change jamais le statut de la question :
la question apparaît dans « À contrôler » de l'admin, qui décide (archiver, marquer
invalide, modifier → nouvelle version…). Jamais supprimé : l'admin le marque traité
(`resolved_at`)."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.v1.models import FeedbackType, QuestionFeedback, SessionQuestion

FEEDBACK_LABELS: dict[FeedbackType, str] = {
    FeedbackType.TOO_EASY: "Trop facile",
    FeedbackType.TOO_HARD: "Trop difficile",
    FeedbackType.AMBIGUOUS: "Question ambiguë",
    FeedbackType.INCORRECT: "Question ou correction incorrecte",
    FeedbackType.IMAGE_INCORRECT: "Image incorrecte",
    FeedbackType.ANSWER_DISPUTED: "Réponse contestable",
    FeedbackType.OTHER: "Autre",
}

MAX_FEEDBACK_COMMENT_LENGTH = 1000


def parse_feedback_type(raw: str | None) -> FeedbackType | None:
    try:
        return FeedbackType(raw or "")
    except ValueError:
        return None


def create_question_feedback(
    db: Session,
    *,
    user_id: int,
    session_question: SessionQuestion,
    feedback_type: FeedbackType,
    comment: str | None,
) -> QuestionFeedback:
    """Un même utilisateur qui renvoie le même type de signalement pour la même question
    de la même session met à jour son commentaire (pas de doublon) ; le signalement
    redevient « à traiter »."""
    version = session_question.question_version
    answer = session_question.answer
    cleaned = (comment or "").strip()[:MAX_FEEDBACK_COMMENT_LENGTH] or None

    query = db.query(QuestionFeedback).filter_by(
        user_id=user_id, question_version_id=version.id, feedback_type=feedback_type
    )
    query = (
        query.filter_by(session_answer_id=answer.id)
        if answer is not None
        else query.filter(QuestionFeedback.session_answer_id.is_(None))
    )
    feedback = query.first()
    if feedback is None:
        feedback = QuestionFeedback(
            user_id=user_id,
            question_id=version.question_id,
            question_version_id=version.id,
            session_answer_id=answer.id if answer is not None else None,
            feedback_type=feedback_type,
        )
        db.add(feedback)
    feedback.comment = cleaned
    feedback.resolved_at = None
    db.flush()
    return feedback


def resolve_feedback(db: Session, feedback: QuestionFeedback, *, resolved: bool = True) -> None:
    feedback.resolved_at = datetime.now(UTC) if resolved else None
    db.flush()

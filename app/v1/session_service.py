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
from app.ai.questionnaire import correct_questionnaire, generate_questionnaire
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
)
from app.v1.ampcr_plan import AMPCR_PLAN_BY_CODE
from app.v1.bank import persist_generated_questions, select_bank_questions
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
CORRECTION_SEVERITY = "standard"

_DIFFICULTY_TO_FRENCH = {
    SessionDifficultyRequest.EASY: "facile",
    SessionDifficultyRequest.MEDIUM: "moyen",
    SessionDifficultyRequest.HARD: "difficile",
    SessionDifficultyRequest.ADAPTIVE: "moyen",
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


def get_in_progress_session(
    db: DBSession, *, user_id: int, module_id: int, mode: SessionMode, uaa_id: int | None = None
) -> QuestionnaireSession | None:
    query = db.query(QuestionnaireSession).filter_by(
        user_id=user_id, module_id=module_id, mode=mode, status=SessionStatus.IN_PROGRESS
    )
    sessions = query.order_by(QuestionnaireSession.created_at.desc()).all()
    if uaa_id is None:
        return sessions[0] if sessions else None
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
    d'échouer si la génération échoue (voir docstring du module)."""
    oversample = select_bank_questions(
        db, user_id=user.id, module_id=module_id, uaa_id=uaa_id, limit=question_count * 3
    )
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
        request = QuestionnaireRequest(
            contexts=(context,),
            mode=mode.value,
            difficulty=difficulty_fr,
            question_count=missing,
            allowed_types=allowed_types,
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
        # Dernier repli explicite (§ GÉNÉRATION du ticket #55) : réutilise ce qui existe
        # déjà, y compris en répétant et en dépassant exceptionnellement le plafond
        # sémantique, plutôt que de refuser de créer la session.
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

    session = QuestionnaireSession(
        user_id=user.id,
        mode=mode,
        module_id=module_id,
        difficulty_requested=difficulty,
        status=SessionStatus.IN_PROGRESS,
        question_count=len(selected),
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


def get_owned_session(db: DBSession, *, session_id: int, user_id: int) -> QuestionnaireSession | None:
    session = db.get(QuestionnaireSession, session_id)
    if session is None or session.user_id != user_id:
        return None
    return session


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


def submit_session(db: DBSession, *, session: QuestionnaireSession, provider: AIProvider) -> QuestionnaireSession:
    """Correction globale unique (§ 15 du ticket #55) : construit un `Questionnaire`
    (#23) à partir des `SessionQuestion` de la session, appelle `correct_questionnaire`
    (correction locale immédiate + UN SEUL appel IA groupé pour le reste), puis marque la
    session `COMPLETED` (immuable — voir `QuestionnaireSession.is_locked`)."""
    if session.is_locked():
        return session

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    questionnaire_questions = []
    answers: dict[str, object] = {}
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

    questionnaire = Questionnaire(mode=session.mode.value, questions=questionnaire_questions)
    uaa_code = None
    first_question = session_questions[0].question_version.question if session_questions else None
    if first_question and first_question.uaa_id:
        uaa = first_question.uaa
        uaa_code = uaa.code if uaa else None
    context = _pedagogical_context_for(uaa_code)

    try:
        correction = correct_questionnaire(provider, questionnaire, answers, CORRECTION_SEVERITY, [context])
        corrections_by_id = {c.question_id: c for c in correction.questions}
        score = correction.score
    except AIProviderError:
        # Repli explicite (§ 13/§ CORRECTION du ticket #55) : la correction IA groupée a
        # échoué (service indisponible) — corrige localement ce qui peut l'être plutôt que
        # de faire échouer toute la soumission ; les questions sémantiques restent
        # honnêtement signalées comme non corrigées (jamais un score inventé).
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
    db.commit()
    return session

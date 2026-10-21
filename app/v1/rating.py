"""Rating adaptatif V1 (ticket #45) — difficulté empirique des questions et niveau de
l'utilisateur PAR MODULE.

Algorithme (« elo-v1 », déterministe, documenté dans `docs/rating_adaptatif_v1.md`) :

- Échelle commune utilisateur/question centrée sur `DEFAULT_MODULE_RATING` (1000),
  bornée à [`RATING_MIN`, `RATING_MAX`].
- Rating initial d'une question jamais notée : dérivé de sa difficulté DÉCLARÉE
  (`INITIAL_QUESTION_RATING`), qui reste une simple métadonnée jamais modifiée.
- Probabilité de réussite attendue (logistique Elo, échelle 400) :
  `p = 1 / (1 + 10 ** ((R_question - R_user) / 400))`.
- Score observé par question : `points_awarded / points_max`, borné à [0, 1] (les
  points partiels comptent proportionnellement).
- Mise à jour UNE FOIS par questionnaire terminé (`SessionStatus.COMPLETED`), jamais
  après chaque question : tous les attendus sont calculés avec les ratings d'AVANT le
  questionnaire, puis appliqués ensemble.
  - utilisateur : `ΔU = K_user × moyenne(score − p)` sur toutes les questions corrigées
    (une question laissée vide compte comme un échec de l'utilisateur) ;
  - question : `ΔQ = K_question × (p − score)`, uniquement si l'utilisateur a réellement
    répondu (une réponse vide ne dit rien de la difficulté de la question).
- Pas d'ajustement progressif : `K` décroît avec l'expérience
  (`K = max(K_MIN, K_MAX / (1 + n / DEMI_VIE))`), donc les premiers résultats bougent
  vite puis le rating se stabilise.
- Idempotent : le détail appliqué est figé dans `parameters_json["rating"]` de la
  session ; une session qui le porte déjà n'est jamais recomptée. Les sessions terminées
  avant ce ticket ne sont jamais rejouées (aucun impact rétroactif), et le score d'une
  session n'est jamais modifié par le rating.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session as DBSession

from app.v1.models import (
    DEFAULT_MODULE_RATING,
    AnswerCorrectionStatus,
    Question,
    QuestionDifficulty,
    QuestionnaireSession,
    SessionAnswer,
    SessionStatus,
    UserModuleRating,
)

logger = logging.getLogger(__name__)

ALGORITHM_VERSION = "elo-v1"
RATING_MIN = 400.0
RATING_MAX = 1600.0
ELO_SCALE = 400.0

INITIAL_QUESTION_RATING = {
    QuestionDifficulty.EASY: 900.0,
    QuestionDifficulty.MEDIUM: 1000.0,
    QuestionDifficulty.HARD: 1100.0,
}

K_USER_MAX = 64.0
K_USER_MIN = 16.0
K_USER_HALF_LIFE = 5.0  # questionnaires terminés dans le module

K_QUESTION_MAX = 40.0
K_QUESTION_MIN = 8.0
K_QUESTION_HALF_LIFE = 10.0  # réponses notées

# Sélection adaptative : questions dont le rating est à ±ADAPTIVE_BAND du niveau de
# l'utilisateur servies en priorité ; ordre par tranches de ADAPTIVE_BUCKET_WIDTH pour
# garder l'aléatoire de la banque à l'intérieur d'une même tranche.
ADAPTIVE_BAND = 150.0
ADAPTIVE_BUCKET_WIDTH = 50.0

# Niveau à demander à la génération IA quand la banque ne suffit pas en mode adaptatif.
ADAPTIVE_EASY_BELOW = 950.0
ADAPTIVE_HARD_ABOVE = 1050.0

PARAMETERS_KEY = "rating"


def clamp_rating(value: float) -> float:
    return max(RATING_MIN, min(RATING_MAX, value))


def expected_success(user_rating: float, question_rating: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((question_rating - user_rating) / ELO_SCALE))


def k_user(sessions_count: int) -> float:
    return max(K_USER_MIN, K_USER_MAX / (1.0 + sessions_count / K_USER_HALF_LIFE))


def k_question(sample_size: int) -> float:
    return max(K_QUESTION_MIN, K_QUESTION_MAX / (1.0 + sample_size / K_QUESTION_HALF_LIFE))


def question_rating(question: Question) -> float:
    """Rating effectif d'une question : empirique s'il existe, sinon initial déduit de la
    difficulté déclarée (moyen si aucune)."""
    if question.difficulty_rating is not None:
        return question.difficulty_rating
    return INITIAL_QUESTION_RATING.get(question.difficulty_declared, DEFAULT_MODULE_RATING)


def get_user_module_rating(db: DBSession, *, user_id: int, module_id: int) -> UserModuleRating | None:
    return db.query(UserModuleRating).filter_by(user_id=user_id, module_id=module_id).first()


def user_rating_value(db: DBSession, *, user_id: int, module_id: int) -> float:
    row = get_user_module_rating(db, user_id=user_id, module_id=module_id)
    return row.rating if row is not None else DEFAULT_MODULE_RATING


def generation_difficulty_fr(user_rating: float) -> str:
    if user_rating < ADAPTIVE_EASY_BELOW:
        return "facile"
    if user_rating > ADAPTIVE_HARD_ABOVE:
        return "difficile"
    return "moyen"


def order_by_proximity(questions: list[Question], target: float) -> list[Question]:
    """Tri STABLE par tranche de distance au niveau visé : jamais d'exclusion, et
    l'ordre (aléatoire) d'origine est conservé à l'intérieur d'une même tranche."""
    return sorted(
        questions, key=lambda q: int(abs(question_rating(q) - target) // ADAPTIVE_BUCKET_WIDTH)
    )


def in_adaptive_band(question: Question, target: float) -> bool:
    return abs(question_rating(question) - target) <= ADAPTIVE_BAND


def _is_blank_answer(answer_json) -> bool:
    if answer_json in (None, "", [], {}):
        return True
    if isinstance(answer_json, dict):
        return all(_is_blank_answer(value) for value in answer_json.values())
    if isinstance(answer_json, str):
        return not answer_json.strip()
    return False


@dataclass(frozen=True)
class _Observation:
    question: Question
    score: float
    answered: bool
    correct: bool


def _observations(db: DBSession, session: QuestionnaireSession) -> list[_Observation]:
    # Réponses relues en base (après flush) plutôt que via `SessionQuestion.answer` : la
    # correction crée en cours de route les réponses des questions laissées vides, que la
    # relation déjà chargée (à None) ne refléterait pas.
    db.flush()
    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    answers = {
        answer.session_question_id: answer
        for answer in db.query(SessionAnswer).filter(
            SessionAnswer.session_question_id.in_([sq.id for sq in session_questions])
        )
    }
    observations: list[_Observation] = []
    seen_question_ids: set[int] = set()
    for session_question in session_questions:
        answer = answers.get(session_question.id)
        if (
            answer is None
            or answer.correction_status != AnswerCorrectionStatus.CORRECTED
            or answer.points_awarded is None
        ):
            continue
        question = session_question.question_version.question
        if question.id in seen_question_ids:
            continue
        points_max = (answer.feedback_json or {}).get("points_max") or session_question.points_max
        if not points_max or points_max <= 0:
            continue
        seen_question_ids.add(question.id)
        score = max(0.0, min(1.0, answer.points_awarded / points_max))
        observations.append(
            _Observation(
                question=question,
                score=score,
                answered=not _is_blank_answer(answer.answer_json),
                correct=score >= 1.0 - 1e-9,
            )
        )
    return observations


def apply_session_rating(db: DBSession, session: QuestionnaireSession) -> dict | None:
    """Applique UNE fois le rating d'un questionnaire terminé (voir docstring du module).
    Ne commit pas : appelé juste avant le commit de finalisation de la correction.
    Retourne le détail figé dans `parameters_json["rating"]`, ou `None` si rien à faire
    (session non terminée, déjà comptée, ou aucune réponse corrigée)."""
    if session.status != SessionStatus.COMPLETED:
        return None
    if PARAMETERS_KEY in (session.parameters_json or {}):
        return None
    observations = _observations(db, session)
    if not observations:
        return None

    user_row = get_user_module_rating(db, user_id=session.user_id, module_id=session.module_id)
    if user_row is None:
        user_row = UserModuleRating(
            user_id=session.user_id, module_id=session.module_id,
            rating=DEFAULT_MODULE_RATING, sessions_count=0,
        )
        db.add(user_row)
    user_before = user_row.rating if user_row.rating is not None else DEFAULT_MODULE_RATING
    sessions_before = user_row.sessions_count or 0
    k_u = k_user(sessions_before)

    # Tous les attendus sont calculés AVANT toute mise à jour (ordre sans effet).
    expectations = [
        (obs, question_rating(obs.question), expected_success(user_before, question_rating(obs.question)))
        for obs in observations
    ]
    user_delta = k_u * sum(obs.score - p for obs, _, p in expectations) / len(expectations)
    user_after = round(clamp_rating(user_before + user_delta), 2)

    question_details = []
    for obs, q_before, p in expectations:
        question = obs.question
        question.times_served = (question.times_served or 0) + 1
        question.times_correct = (question.times_correct or 0) + int(obs.correct)
        q_after = q_before
        if obs.answered:
            sample = question.rating_sample_size or 0
            q_after = round(clamp_rating(q_before + k_question(sample) * (p - obs.score)), 2)
            question.difficulty_rating = q_after
            question.rating_sample_size = sample + 1
        question_details.append({
            "question_id": question.id,
            "score": round(obs.score, 4),
            "expected": round(p, 4),
            "answered": obs.answered,
            "rating_before": round(q_before, 2),
            "rating_after": q_after,
        })

    user_row.rating = user_after
    user_row.sessions_count = sessions_before + 1

    detail = {
        "algorithm": ALGORITHM_VERSION,
        "module_id": session.module_id,
        "user_before": round(user_before, 2),
        "user_after": user_after,
        "user_delta": round(user_after - user_before, 2),
        "k_user": round(k_u, 2),
        "sessions_count_after": user_row.sessions_count,
        "questions": question_details,
        "applied_at": datetime.now(UTC).isoformat(),
    }
    parameters = dict(session.parameters_json or {})
    parameters[PARAMETERS_KEY] = detail
    session.parameters_json = parameters
    # Rend la ligne de rating visible des requêtes suivantes même sans autoflush.
    db.flush()
    return detail


def apply_session_rating_safely(db: DBSession, session: QuestionnaireSession) -> dict | None:
    """Enveloppe de `apply_session_rating` pour les chemins de correction : un échec du
    rating ne doit JAMAIS empêcher la finalisation d'une correction (savepoint annulé,
    erreur journalisée, session laissée sans rating)."""
    try:
        with db.begin_nested():
            return apply_session_rating(db, session)
    except Exception:  # le rating est secondaire par rapport à la correction
        logger.exception("Rating adaptatif non appliqué pour la session %s", session.id)
        return None

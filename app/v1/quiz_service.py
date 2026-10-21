"""Quiz ludiques par matière et multi-matières du parcours (ticket #137).

Une partie de quiz est une `QuestionnaireSession` ordinaire en `SessionMode.QUIZ` : mêmes
banques (`v1_questions`, versions immuables), même historique `UserQuestionHistory`, même
garde anti-doublon intra-session (`deduplicate_intra_session`) et même création
(`_finalize_session`) que les entraînements et examens blancs — seul le cycle change :

- **une question à la fois, validée explicitement** : `validate_quiz_answer` corrige la
  réponse côté serveur dès sa validation (correction locale déterministe déjà utilisée par
  le moteur, `app.ai.local_correction.correct_locally`), la verrouille, puis révèle la
  solution et l'explication de CETTE question uniquement. Aucune solution n'est jamais
  envoyée au navigateur avant cette validation (le formulaire ne reçoit que
  `public_payload`) ;
- **formats objectifs seulement** (`QUIZ_QUESTION_TYPES`) : QCM, classement, remise en
  ordre. Les réponses rédigées (courtes ou longues), l'analyse de documents et l'oral
  restent dans les entraînements/examens blancs : une comparaison textuelle stricte
  produirait de faux négatifs immédiats et un QCM ne mesure pas une production longue ;
- **aucune IA** : pas de génération ni de correction payante pendant une partie ; le
  quiz pioche dans les banques déjà constituées (manuelles ou générées puis persistées) ;
- **une erreur technique n'est jamais une mauvaise réponse** : si la correction d'une
  question échoue, la réponse est conservée, marquée `FAILED` et exclue du score (ni
  juste ni fausse) — la partie continue ;
- **activité distincte** : ni entraînement, ni examen blanc (`app.v1.parcours`), absente
  de « Mes entraînements », aucun effet sur le rating de module (`app.v1.rating`).

Périmètre : uniquement les cours publiés des matières du parcours choisi
(`app.v1.parcours`), jamais un autre programme. Le mélange multi-matières est équilibré
par tourniquet matière → cours (`_pick_balanced`) ; les questions jamais vues passent
avant les déjà vues, puis la difficulté demandée avant les autres (même priorité que
`app.v1.bank.select_bank_questions`)."""

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from app import models
from app.ai.local_correction import correct_locally
from app.v1.ai_bridge import (
    answer_json_to_submitted,
    content_to_questionnaire_question,
    describe_submitted_answer,
)
from app.v1.bank import _seen_signatures, _split_unseen_and_seen
from app.v1.dedup import find_near_duplicate, question_signature
from app.v1.display_order import apply_display_order
from app.v1.models import (
    AnswerCorrectionStatus,
    ContentStatus,
    Question,
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
from app.v1.parcours import ResolvedPathway, listed_uaas
from app.v1.rating import user_rating_value
from app.v1.session_service import (
    _difficulty_predicate,
    _finalize_session,
    deduplicate_intra_session,
)

QUIZ_QUESTION_TYPES = ("multiple_choice", "classification", "ordering")
QUIZ_LENGTHS = (5, 10, 20)
DEFAULT_QUIZ_LENGTH = 10
QUIZ_DIFFICULTY_LABELS = {
    SessionDifficultyRequest.EASY: "Facile",
    SessionDifficultyRequest.MEDIUM: "Moyen",
    SessionDifficultyRequest.HARD: "Difficile",
    SessionDifficultyRequest.ADAPTIVE: "Adaptée à mon niveau",
}
DEFAULT_QUIZ_DIFFICULTY = SessionDifficultyRequest.MEDIUM
TYPE_LABELS = {
    "multiple_choice": "QCM",
    "classification": "Classement",
    "ordering": "Remise en ordre",
}
PARAMETERS_KEY = "quiz"
# Une nouvelle partie identique demandée dans ce délai (double clic, retour arrière) et
# toujours sans aucune réponse retombe sur la partie déjà créée.
DUPLICATE_START_WINDOW_SECONDS = 30


class QuizError(Exception):
    """Demande de partie impossible (périmètre vide, aucune question disponible…)."""


# --- Catalogue : ce que le parcours propose réellement ---------------------------------------


@dataclass
class ChapterOffer:
    uaa: models.UAA
    available: int
    unseen: int


@dataclass
class SubjectOffer:
    track: object  # app.v1.parcours.SubjectTrack
    module: models.Module
    chapters: list[ChapterOffer]
    declares_difficulty: bool

    @property
    def available(self) -> int:
        return sum(c.available for c in self.chapters)

    @property
    def unseen(self) -> int:
        return sum(c.unseen for c in self.chapters)

    @property
    def playable_chapters(self) -> list[ChapterOffer]:
        return [c for c in self.chapters if c.available]


def _quiz_questions_query(db: DBSession, uaa_ids: list[int]):
    return (
        db.query(Question)
        .join(QuestionVersion, QuestionVersion.id == Question.current_version_id)
        .filter(
            Question.status == ContentStatus.ACTIVE,
            Question.uaa_id.in_(uaa_ids),
            QuestionVersion.question_type.in_(QUIZ_QUESTION_TYPES),
        )
    )


def _seen_question_ids(db: DBSession, user: User | None) -> set[int]:
    if user is None:
        return set()
    return {
        row[0]
        for row in db.query(UserQuestionHistory.question_id).filter_by(user_id=user.id).distinct()
    }


def quiz_question_counts(db: DBSession, uaa_ids: list[int]) -> dict[int, int]:
    """Nombre de questions de quiz disponibles par UAA (une seule requête groupée)."""
    if not uaa_ids:
        return {}
    counts: dict[int, int] = {}
    for (uaa_id,) in _quiz_questions_query(db, uaa_ids).with_entities(Question.uaa_id):
        counts[uaa_id] = counts.get(uaa_id, 0) + 1
    return counts


def build_catalog(db: DBSession, pathway: ResolvedPathway, user: User | None) -> list[SubjectOffer]:
    """Matières du parcours présentes en base, avec leurs cours publiés et le nombre de
    questions de quiz réellement disponibles par cours (0 = signalé, jamais caché)."""
    seen_ids = _seen_question_ids(db, user)
    offers: list[SubjectOffer] = []
    for track in pathway.option.tracks:
        module = db.query(models.Module).filter_by(code=track.module_code).first()
        if module is None:
            continue
        uaas = listed_uaas(module)
        questions = _quiz_questions_query(db, [u.id for u in uaas]).all() if uaas else []
        by_uaa: dict[int, list[Question]] = {}
        for question in questions:
            by_uaa.setdefault(question.uaa_id, []).append(question)
        chapters = [
            ChapterOffer(
                uaa=uaa,
                available=len(by_uaa.get(uaa.id, [])),
                unseen=sum(1 for q in by_uaa.get(uaa.id, []) if q.id not in seen_ids),
            )
            for uaa in uaas
        ]
        offers.append(
            SubjectOffer(
                track=track,
                module=module,
                chapters=chapters,
                declares_difficulty=any(q.difficulty_declared is not None for q in questions),
            )
        )
    return offers


# --- Périmètre demandé -------------------------------------------------------------------------


@dataclass
class QuizScope:
    """Cours retenus, groupés par matière (ordre du parcours). `kind` : parcours |
    matiere | chapitre | selection | erreurs."""

    kind: str
    label: str
    subjects: list[tuple[SubjectOffer, list[ChapterOffer]]]
    ignored: list[str] = field(default_factory=list)  # libellés écartés faute de questions

    @property
    def uaa_ids(self) -> list[int]:
        return [c.uaa.id for _, chapters in self.subjects for c in chapters]

    @property
    def available(self) -> int:
        return sum(c.available for _, chapters in self.subjects for c in chapters)

    @property
    def unseen(self) -> int:
        return sum(c.unseen for _, chapters in self.subjects for c in chapters)


def resolve_scope(
    catalog: list[SubjectOffer],
    *,
    whole_pathway: bool = False,
    module_codes: list[str] | tuple[str, ...] = (),
    uaa_slugs: list[str] | tuple[str, ...] = (),
    uaa_ids: list[int] | tuple[int, ...] = (),
    kind: str | None = None,
) -> QuizScope:
    """Traduit une sélection (formulaire ou paramètres persistés) en cours du parcours.
    Une matière cochée vaut tous ses cours ; sinon seuls ses cours cochés. Tout code ou
    slug étranger au parcours est ignoré — jamais un cours d'un autre programme."""
    wanted_modules = set(module_codes)
    wanted_slugs = set(uaa_slugs)
    wanted_ids = set(uaa_ids)
    subjects: list[tuple[SubjectOffer, list[ChapterOffer]]] = []
    ignored: list[str] = []
    for offer in catalog:
        if whole_pathway or offer.module.code in wanted_modules:
            chosen = list(offer.chapters)
            whole = True
        else:
            chosen = [
                c for c in offer.chapters if c.uaa.slug in wanted_slugs or c.uaa.id in wanted_ids
            ]
            whole = False
        if not chosen:
            continue
        playable = [c for c in chosen if c.available]
        if whole and not playable:
            ignored.append(offer.track.title)
        elif not whole:
            ignored.extend(f"{c.uaa.code} — {c.uaa.title}" for c in chosen if not c.available)
        if playable:
            subjects.append((offer, playable))

    if kind is None:
        chapter_count = sum(len(chapters) for _, chapters in subjects)
        if whole_pathway:
            kind = "parcours"
        elif len(subjects) == 1 and chapter_count == 1 and not wanted_modules:
            kind = "chapitre"
        elif len(subjects) == 1 and wanted_modules:
            kind = "matiere"
        else:
            kind = "selection"
    return QuizScope(kind=kind, label=_scope_label(kind, subjects), subjects=subjects, ignored=ignored)


def _scope_label(kind: str, subjects) -> str:
    if kind == "parcours":
        return "Tout mon parcours"
    if kind == "erreurs":
        return "Reprise de mes erreurs"
    if len(subjects) == 1:
        offer, chapters = subjects[0]
        if kind == "matiere":
            return offer.track.title
        if len(chapters) == 1:
            return f"{chapters[0].uaa.code} — {chapters[0].uaa.title}"
        if len(chapters) == len(offer.playable_chapters):
            return offer.track.title
        return f"{offer.track.title} ({len(chapters)} cours)"
    return " + ".join(offer.track.title for offer, _ in subjects)


# --- Sélection équilibrée ----------------------------------------------------------------------


@dataclass
class QuizPlan:
    """Aperçu honnête d'une partie : nombre par matière, limites annoncées avant le départ."""

    requested: int
    total: int
    per_subject: list[dict]
    notes: list[str]


def _allocate(count: int, capacities: list[int]) -> list[int]:
    """Répartition par tourniquet (une question à la fois par matière ayant encore du
    stock) — même règle que `_pick_balanced`, utilisée pour l'aperçu."""
    allocation = [0] * len(capacities)
    progressed = True
    while sum(allocation) < count and progressed:
        progressed = False
        for index, capacity in enumerate(capacities):
            if sum(allocation) >= count:
                break
            if allocation[index] < capacity:
                allocation[index] += 1
                progressed = True
    return allocation


def plan_quiz(
    scope: QuizScope, *, count: int, difficulty: SessionDifficultyRequest
) -> QuizPlan:
    capacities = [sum(c.available for c in chapters) for _, chapters in scope.subjects]
    allocation = _allocate(count, capacities)
    per_subject = [
        {
            "title": offer.track.title,
            "theme": offer.track.theme,
            "icon": offer.track.icon,
            "chapters": len(chapters),
            "available": capacity,
            "unseen": sum(c.unseen for c in chapters),
            "planned": planned,
            "declares_difficulty": offer.declares_difficulty,
        }
        for (offer, chapters), capacity, planned in zip(
            scope.subjects, capacities, allocation, strict=True
        )
    ]
    total = sum(allocation)
    notes: list[str] = []
    if scope.ignored:
        notes.append(
            "Pas encore de questions de quiz pour : " + ", ".join(scope.ignored)
            + ". Ce contenu n'est donc pas dans la partie."
        )
    if total < count:
        notes.append(
            f"Seulement {total} question{'s' if total > 1 else ''} disponible"
            f"{'s' if total > 1 else ''} pour ce choix : la partie en comptera {total}."
        )
    chapter_total = sum(len(chapters) for _, chapters in scope.subjects)
    if total and chapter_total > total:
        notes.append(
            f"Partie courte : {total} questions pour {chapter_total} cours — tous les cours ne "
            "seront pas interrogés cette fois. Rejoue pour couvrir les autres."
        )
    if any(p["planned"] == 0 for p in per_subject):
        missing = [p["title"] for p in per_subject if p["planned"] == 0]
        notes.append("Pas de question cette fois pour : " + ", ".join(missing) + ".")
    if scope.unseen < total:
        notes.append(
            "Tu as déjà vu une partie de ces questions : les nouvelles passent en premier, "
            "certaines déjà vues peuvent revenir."
        )
    if difficulty in (SessionDifficultyRequest.EASY, SessionDifficultyRequest.MEDIUM, SessionDifficultyRequest.HARD):
        undeclared = [p["title"] for p in per_subject if not p["declares_difficulty"]]
        if undeclared:
            notes.append(
                "Difficulté non renseignée dans la banque pour : " + ", ".join(undeclared)
                + " — ces questions sont de niveaux variés."
            )
    return QuizPlan(requested=count, total=total, per_subject=per_subject, notes=notes)


def _ordered_candidates(
    db: DBSession,
    *,
    user: User,
    uaa_ids: list[int],
    difficulty: SessionDifficultyRequest,
    module_id: int,
    exclude_question_ids: set[int],
) -> dict[int, list[Question]]:
    """Par cours : jamais vues d'abord, puis déjà vues ; à l'intérieur de chaque groupe,
    la difficulté demandée d'abord (`_difficulty_predicate`, partagé avec le moteur).
    `exclude_question_ids` (reprise des erreurs) : ces questions ET leurs quasi-doublons
    sont exclus — de vrais nouveaux cas, jamais la même question reformulée."""
    candidates = _quiz_questions_query(db, uaa_ids).all()
    random.shuffle(candidates)
    excluded_signatures = []
    if exclude_question_ids:
        for question in db.query(Question).filter(Question.id.in_(exclude_question_ids)).all():
            version = question.current_version
            excluded_signatures.append(question_signature(version.question_type, version.content_json))
        candidates = [
            q for q in candidates
            if q.id not in exclude_question_ids
            and find_near_duplicate(
                question_signature(q.current_version.question_type, q.current_version.content_json),
                excluded_signatures,
            ) is None
        ]
    unseen, seen = _split_unseen_and_seen(
        candidates,
        seen_question_ids=_seen_question_ids(db, user),
        seen_signatures=_seen_signatures(db, user_id=user.id),
    )
    target = (
        user_rating_value(db, user_id=user.id, module_id=module_id)
        if difficulty == SessionDifficultyRequest.ADAPTIVE
        else None
    )
    matches = _difficulty_predicate(difficulty, target)

    def prioritized(group: list[Question]) -> list[Question]:
        if matches is None:
            return group
        return [q for q in group if matches(q)] + [q for q in group if not matches(q)]

    ordered = prioritized(unseen) + prioritized(seen)
    by_uaa: dict[int, list[Question]] = {uaa_id: [] for uaa_id in uaa_ids}
    for question in ordered:
        by_uaa[question.uaa_id].append(question)
    return by_uaa


def _pick_balanced(queues: list[list[list[Question]]], count: int) -> list[Question]:
    """Tourniquet matière → cours : à chaque tour, chaque matière fournit une question,
    prise dans son cours suivant. Un candidat qui ferait doublon avec la sélection
    (`deduplicate_intra_session`) est écarté ; jamais de répétition pour combler."""
    selected: list[Question] = []
    pointers = [0] * len(queues)
    progressed = True
    while len(selected) < count and progressed:
        progressed = False
        for module_index, uaa_queues in enumerate(queues):
            if len(selected) >= count or not uaa_queues:
                continue
            for step in range(len(uaa_queues)):
                queue_index = (pointers[module_index] + step) % len(uaa_queues)
                queue = uaa_queues[queue_index]
                picked = None
                while queue:
                    candidate = queue.pop(0)
                    if len(deduplicate_intra_session([*selected, candidate])) == len(selected) + 1:
                        picked = candidate
                        break
                if picked is not None:
                    selected.append(picked)
                    pointers[module_index] = (queue_index + 1) % len(uaa_queues)
                    progressed = True
                    break
    return selected


def find_recent_duplicate_start(
    db: DBSession, *, user: User, signature: dict
) -> QuestionnaireSession | None:
    now = datetime.now(UTC)
    recent = (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id, mode=SessionMode.QUIZ, status=SessionStatus.IN_PROGRESS)
        .order_by(QuestionnaireSession.created_at.desc())
        .limit(3)
        .all()
    )
    for session in recent:
        created = session.created_at if session.created_at.tzinfo else session.created_at.replace(tzinfo=UTC)
        if (now - created).total_seconds() > DUPLICATE_START_WINDOW_SECONDS:
            continue
        params = (session.parameters_json or {}).get(PARAMETERS_KEY) or {}
        if params.get("signature") == signature and all(
            sq.answer is None for sq in session.session_questions
        ):
            return session
    return None


def start_quiz(
    db: DBSession,
    *,
    user: User,
    pathway: ResolvedPathway,
    scope: QuizScope,
    count: int,
    difficulty: SessionDifficultyRequest,
    exclude_question_ids: set[int] | None = None,
    retry_of: int | None = None,
) -> QuestionnaireSession:
    if count not in QUIZ_LENGTHS:
        count = DEFAULT_QUIZ_LENGTH
    if not scope.subjects:
        raise QuizError("Aucune question de quiz n'est disponible pour ce choix.")
    signature = {
        "uaa_ids": sorted(scope.uaa_ids),
        "count": count,
        "difficulty": difficulty.value,
        "kind": scope.kind,
        "retry_of": retry_of,
    }
    existing = find_recent_duplicate_start(db, user=user, signature=signature)
    if existing is not None:
        return existing

    exclude = set(exclude_question_ids or ())
    queues = []
    for offer, chapters in scope.subjects:
        by_uaa = _ordered_candidates(
            db, user=user, uaa_ids=[c.uaa.id for c in chapters], difficulty=difficulty,
            module_id=offer.module.id, exclude_question_ids=exclude,
        )
        uaa_queues = [by_uaa[c.uaa.id] for c in chapters if by_uaa[c.uaa.id]]
        random.shuffle(uaa_queues)  # parties courtes : d'autres cours la fois suivante
        queues.append(uaa_queues)
    # Matière de départ tirée au sort : une partie courte ne favorise pas toujours l'option.
    offset = random.randrange(len(queues))
    order = list(range(offset, len(queues))) + list(range(offset))
    selected = _pick_balanced([queues[i] for i in order], count)
    if not selected:
        raise QuizError("Aucune nouvelle question n'est disponible pour ce choix.")

    plan = plan_quiz(scope, count=count, difficulty=difficulty)
    parameters = {
        "activity": "quiz",
        PARAMETERS_KEY: {
            "label": scope.label,
            "kind": scope.kind,
            "pathway": "/".join(pathway.keys),
            "uaa_ids": scope.uaa_ids,
            "module_codes": [offer.module.code for offer, _ in scope.subjects],
            "requested_count": count,
            "retry_of": retry_of,
            "excluded_question_ids": sorted(exclude),
            "notes": plan.notes,
            "signature": signature,
        },
    }
    first_module_id = selected[0].module_id
    return _finalize_session(
        db, user=user, module_id=first_module_id, mode=SessionMode.QUIZ,
        difficulty=difficulty, selected=selected, parameters_json=parameters,
    )


# --- Déroulé d'une partie ----------------------------------------------------------------------


def get_owned_quiz(db: DBSession, *, session_id: int, user: User) -> QuestionnaireSession | None:
    session = db.get(QuestionnaireSession, session_id)
    if session is None or session.user_id != user.id or session.mode != SessionMode.QUIZ:
        return None
    return session


def quiz_params(session: QuestionnaireSession) -> dict:
    return (session.parameters_json or {}).get(PARAMETERS_KEY) or {}


def ordered_questions(session: QuestionnaireSession) -> list[SessionQuestion]:
    return sorted(session.session_questions, key=lambda sq: sq.position)


def is_validated(session_question: SessionQuestion) -> bool:
    answer = session_question.answer
    return answer is not None and answer.correction_status != AnswerCorrectionStatus.PENDING


def current_position(session: QuestionnaireSession) -> int | None:
    """Reprise exacte : première question non encore validée (`None` = partie finie)."""
    for session_question in ordered_questions(session):
        if not is_validated(session_question):
            return session_question.position
    return None


class IncompleteAnswerError(ValueError):
    """Réponse incomplète : rien n'est enregistré, la question reste à valider."""


def parse_quiz_answer(question_type: str, content: dict, form) -> dict:
    """Lit et contrôle la réponse côté serveur. Une réponse incomplète n'est jamais
    corrigée (ni comptée fausse) : l'élève complète puis valide."""
    if question_type == "multiple_choice":
        known = {o["option_id"] for o in content["options"]}
        selected = [oid for oid in dict.fromkeys(form.getlist("option_id")) if oid in known]
        minimum = int(content.get("min_selections") or 1)
        maximum = int(content.get("max_selections") or 1)
        if not selected:
            raise IncompleteAnswerError("Choisis une réponse avant de valider.")
        if len(selected) < minimum or len(selected) > maximum:
            if minimum == maximum:
                raise IncompleteAnswerError(f"Choisis exactement {minimum} réponses.")
            raise IncompleteAnswerError(f"Choisis entre {minimum} et {maximum} réponses.")
        return {"selected_option_ids": selected}
    if question_type == "classification":
        assignments = []
        for index in range(len(content["elements"])):
            raw = str(form.get(f"category__{index}", ""))
            value = int(raw) if raw.isdigit() else -1
            if not 0 <= value < len(content["categories"]):
                raise IncompleteAnswerError("Range chaque élément dans une catégorie avant de valider.")
            assignments.append(value)
        return {"assignments": assignments}
    if question_type == "ordering":
        items = content["items"]
        positions = []
        for item in items:
            raw = str(form.get(f"position__{item['id']}", "0"))
            positions.append((int(raw) if raw.isdigit() else 0, item["id"]))
        if sorted(p for p, _ in positions) != list(range(1, len(items) + 1)):
            raise IncompleteAnswerError(
                "Donne une position différente (de 1 à "
                f"{len(items)}) à chaque élément avant de valider."
            )
        return {"order": [item_id for _, item_id in sorted(positions)]}
    raise IncompleteAnswerError("Format de question non pris en charge par le quiz.")


def _correct(session_question: SessionQuestion, answer_json: dict) -> dict:
    version = session_question.question_version
    content = version.content_json
    question = content_to_questionnaire_question(
        question_id=f"sq{session_question.id}",
        question_type=version.question_type,
        content=content,
        points_max=session_question.points_max,
    )
    submitted = answer_json_to_submitted(version.question_type, content, answer_json)
    result = correct_locally(question, submitted)
    partial = 0 < result.points_awarded < result.points_max
    return {
        "points_awarded": result.points_awarded,
        "feedback": {
            "correct": result.correct,
            "partial": partial,
            "points_max": result.points_max,
            "strengths": result.strengths,
            "errors": result.errors,
            "expected_answer": result.expected_answer,
            "explanation": (content.get("explanation") or "").strip(),
        },
    }


def validate_quiz_answer(
    db: DBSession, *, session: QuestionnaireSession, session_question: SessionQuestion, answer_json: dict
) -> SessionAnswer:
    """Valide UNE réponse : correction immédiate côté serveur, réponse verrouillée.
    Idempotent (double clic, deux onglets) : une question déjà validée n'est jamais
    recorrigée ni modifiée. Si la correction échoue techniquement, la réponse est gardée
    en `FAILED` — exclue du score, jamais une mauvaise réponse."""
    if is_validated(session_question):
        return session_question.answer
    try:
        corrected = _correct(session_question, answer_json)
        status = AnswerCorrectionStatus.CORRECTED
        points = corrected["points_awarded"]
        feedback = corrected["feedback"]
    except Exception:  # noqa: BLE001 — contenu inattendu : jamais une mauvaise réponse
        status = AnswerCorrectionStatus.FAILED
        points = None
        feedback = {"technical_error": True}

    answer = session_question.answer
    if answer is None:
        answer = SessionAnswer(session_question=session_question, answer_json=answer_json)
        db.add(answer)
    answer.answer_json = answer_json
    answer.answered_at = datetime.now(UTC)
    answer.correction_status = status
    answer.points_awarded = points
    answer.feedback_json = feedback
    try:
        db.flush()
    except IntegrityError:  # validation concurrente : la première gagne
        db.rollback()
        db.refresh(session_question)
        return session_question.answer

    if current_position(session) is None:
        _complete(session)
    db.commit()
    return answer


def _complete(session: QuestionnaireSession) -> None:
    corrected = [
        sq.answer for sq in session.session_questions
        if sq.answer is not None and sq.answer.correction_status == AnswerCorrectionStatus.CORRECTED
    ]
    session.score = round(sum(a.points_awarded or 0.0 for a in corrected), 2)
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(UTC)


def feedback_view(session_question: SessionQuestion) -> dict:
    """Ce qui est montré APRÈS validation : la réponse donnée, la solution et
    l'explication — construit seulement pour une question validée."""
    version = session_question.question_version
    # Ticket #150 : la correction affichée suit l'ordre vu par l'élève pendant la question.
    content = apply_display_order(version.question_type, version.content_json, session_question.content_snapshot_json)
    answer = session_question.answer
    answer_json = (answer.answer_json if answer else {}) or {}
    feedback = (answer.feedback_json if answer else {}) or {}
    view = {
        "technical_error": bool(feedback.get("technical_error")),
        "correct": bool(feedback.get("correct")),
        "partial": bool(feedback.get("partial")),
        "points_awarded": answer.points_awarded if answer else None,
        "explanation": feedback.get("explanation") or "",
        "expected_answer": feedback.get("expected_answer") or "",
        "errors": feedback.get("errors") or [],
        "user_answer": describe_submitted_answer(version.question_type, content, answer_json),
        "options": [],
        "rows": [],
        "order": [],
    }
    try:
        if version.question_type == "multiple_choice":
            chosen = set(answer_json.get("selected_option_ids") or [])
            correct_ids = set(content.get("correct_option_ids") or [])
            view["options"] = [
                {"label": o["label"], "chosen": o["option_id"] in chosen, "correct": o["option_id"] in correct_ids}
                for o in content["options"]
            ]
        elif version.question_type == "classification":
            categories = content["categories"]
            given = answer_json.get("assignments") or []
            view["rows"] = [
                {
                    "element": element,
                    "given": categories[given[i]] if i < len(given) and 0 <= given[i] < len(categories) else "—",
                    "expected": categories[expected],
                    "ok": i < len(given) and given[i] == expected,
                }
                for i, (element, expected) in enumerate(
                    zip(content["elements"], content["correct_categories"], strict=True)
                )
            ]
        elif version.question_type == "ordering":
            labels = {i["id"]: i["label"] for i in content["items"]}
            given = answer_json.get("order") or []
            view["order"] = [
                {
                    "label": labels[item_id],
                    "given": labels.get(given[i]) if i < len(given) else "—",
                    "ok": i < len(given) and given[i] == item_id,
                }
                for i, item_id in enumerate(content["correct_order"])
            ]
    except (KeyError, IndexError, TypeError):
        pass
    return view


# --- Résultat --------------------------------------------------------------------------------


def quiz_results(session: QuestionnaireSession) -> dict:
    """Score sur les questions réellement corrigées, points forts / cours à revoir par
    cours (UAA) et répartition par matière."""
    rows = []
    by_uaa: dict[int, dict] = {}
    by_subject: dict[str, dict] = {}
    for sq in ordered_questions(session):
        question = sq.question_version.question
        uaa = question.uaa
        answer = sq.answer
        status = answer.correction_status if answer else AnswerCorrectionStatus.PENDING
        counted = status == AnswerCorrectionStatus.CORRECTED
        correct = counted and bool((answer.feedback_json or {}).get("correct"))
        rows.append({"session_question": sq, "uaa": uaa, "counted": counted, "correct": correct,
                     "feedback": feedback_view(sq) if answer else None})
        if uaa is None or not counted:
            continue
        entry = by_uaa.setdefault(uaa.id, {"uaa": uaa, "asked": 0, "correct": 0, "points": 0.0})
        entry["asked"] += 1
        entry["correct"] += int(correct)
        entry["points"] += answer.points_awarded or 0.0
        subject_name = uaa.module.subject.name if uaa.module and uaa.module.subject else uaa.module.code
        subject = by_subject.setdefault(subject_name, {"name": subject_name, "asked": 0, "points": 0.0})
        subject["asked"] += 1
        subject["points"] += answer.points_awarded or 0.0
    counted_total = sum(1 for r in rows if r["counted"])
    score = session.score if session.score is not None else sum(
        (r["session_question"].answer.points_awarded or 0.0) for r in rows if r["counted"]
    )
    ratio = (score / counted_total) if counted_total else None
    strengths = sorted(
        (e for e in by_uaa.values() if e["correct"] == e["asked"]), key=lambda e: e["uaa"].code
    )
    to_review = sorted(
        (e for e in by_uaa.values() if e["correct"] < e["asked"]),
        key=lambda e: (e["correct"] - e["asked"], e["uaa"].code),
    )
    return {
        "rows": rows,
        "score": round(score, 2),
        "counted_total": counted_total,
        "not_counted": len(rows) - counted_total,
        "ratio": ratio,
        "pct": None if ratio is None else round(ratio * 100),
        "strengths": strengths,
        "to_review": to_review,
        "subjects": [
            {**s, "pct": round(100 * s["points"] / s["asked"]) if s["asked"] else None}
            for s in by_subject.values()
        ],
        "missed_question_ids": sorted(
            {r["session_question"].question_version.question_id for r in rows if r["counted"] and not r["correct"]}
        ),
    }


def result_message(pct: int | None) -> tuple[str, str]:
    """Retour positif mesuré, jamais présenté comme une note officielle."""
    if pct is None:
        return ("Partie terminée", "Aucune réponse n'a pu être comptée cette fois.")
    if pct >= 80:
        return ("Très bonne partie !", "Tu maîtrises bien ces notions. Rejoue pour voir de nouveaux cas.")
    if pct >= 50:
        return ("Bonne partie", "Les bases sont là. Relis les cours indiqués ci-dessous, puis reprends tes erreurs.")
    return ("Continue, ça vient", "Relis d'abord les cours indiqués ci-dessous, puis reprends tes erreurs : c'est en recommençant qu'on progresse.")


# --- Vue d'ensemble du compte ----------------------------------------------------------------


def user_quizzes(db: DBSession, user: User, *, limit: int = 12) -> list[QuestionnaireSession]:
    return (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id, mode=SessionMode.QUIZ)
        .order_by(QuestionnaireSession.created_at.desc())
        .limit(limit)
        .all()
    )


def subject_quiz_stats(db: DBSession, user: User) -> dict[str, dict]:
    """Par code de module : questions de quiz corrigées et réussies (toutes parties)."""
    rows = (
        db.query(models.Module.code, SessionAnswer.points_awarded, SessionAnswer.feedback_json)
        .join(SessionQuestion, SessionQuestion.id == SessionAnswer.session_question_id)
        .join(QuestionnaireSession, QuestionnaireSession.id == SessionQuestion.session_id)
        .join(QuestionVersion, QuestionVersion.id == SessionQuestion.question_version_id)
        .join(Question, Question.id == QuestionVersion.question_id)
        .join(models.Module, models.Module.id == Question.module_id)
        .filter(
            QuestionnaireSession.user_id == user.id,
            QuestionnaireSession.mode == SessionMode.QUIZ,
            SessionAnswer.correction_status == AnswerCorrectionStatus.CORRECTED,
        )
        .all()
    )
    stats: dict[str, dict] = {}
    for code, _points, feedback in rows:
        entry = stats.setdefault(code, {"answered": 0, "correct": 0})
        entry["answered"] += 1
        entry["correct"] += int(bool((feedback or {}).get("correct")))
    for entry in stats.values():
        entry["pct"] = round(100 * entry["correct"] / entry["answered"]) if entry["answered"] else None
    return stats

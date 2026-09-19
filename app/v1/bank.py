"""Banque de questions V1 — service minimal (ticket #55, condensation de #41/#43).

Ne construit pas l'admin #46. Fournit uniquement :
- import du contenu MC01 déjà rédigé (`app.editorial_exercise`) vers la banque V1, via le
  registre #40 (aucune solution privée stockée hors du contrat validé) ;
- sélection de questions ACTIVE pour un module, en évitant les questions déjà vues par
  l'utilisateur quand c'est possible (repli sur les questions déjà vues sinon, jamais un
  échec de session pour ce motif — voir § BANQUE MVP du ticket) ;
- persistance de questions générées par lot (voir `app/v1/ai_bridge.py`), toujours
  revalidées par `app.v1.question_engine.validate_content` (registre #40, structurel) PUIS
  `app.v1.domain_validation.validate_domain_question` (ticket #68, vérité technique —
  ex. IPv4/subnetting) PUIS `app.v1.quality_validation.validate_question_quality`
  (ticket #69, clarté/qualité pédagogique) avant stockage.

Aucun contenu legacy n'est supprimé : `app.editorial_exercise`/MC01_BLOCKS restent
strictement inchangés (voir `app/main.py` pour le nouveau routage qui ne les rend plus
pour les UAA migrées, sans jamais les retirer de la base)."""

import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.schemas import QuestionnaireQuestion
from app.editorial_exercise import EditorialExerciseBlockConfig, EditorialExerciseItem
from app.models import UAA, BlockType, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.ai_bridge import (
    questionnaire_question_to_content,
    shuffle_multiple_choice_options,
    shuffle_ordering_items,
)
from app.v1.dedup import find_near_duplicate, question_signature
from app.v1.domain_validation import validate_domain_question
from app.v1.models import (
    ContentStatus,
    GenerationSource,
    Question,
    UserQuestionHistory,
    create_question,
)
from app.v1.quality_validation import validate_question_quality
from app.v1.question_engine import ContentValidationError, QuestionEngineError, validate_content

logger = logging.getLogger(__name__)

_EDITORIAL_TO_V1_TYPE = {
    "single_choice": "multiple_choice",
    "classification": "classification",
    "ordering": "ordering",
    "short_answer": "short_answer",
    "long_answer": "long_answer",
    "diagnostic": "diagnostic",
    "vocabulary": "vocabulary",
}


class BankImportError(ValueError):
    pass


def _editorial_item_to_v1_content(item: EditorialExerciseItem) -> tuple[str, dict[str, Any]]:
    v1_type = _EDITORIAL_TO_V1_TYPE.get(item.type)
    if v1_type is None:
        raise BankImportError(f"{item.exercise_id} : type éditorial {item.type!r} non importable en V1.")

    if v1_type == "multiple_choice":
        options = [{"option_id": str(i), "label": choice} for i, choice in enumerate(item.choices)]
        correct_id = str(item.correct_index) if item.correct_index is not None else "0"
        # Ticket #80 : contenu éditorial legacy (MC01) place systématiquement la bonne
        # réponse au même index qu'à l'origine — mélange physique, `option_id` intact.
        options = shuffle_multiple_choice_options(options)
        return v1_type, {
            "prompt": item.prompt,
            "options": options,
            "min_selections": 1,
            "max_selections": 1,
            "correct_option_ids": [correct_id],
            "explanation": item.explanation,
        }
    if v1_type == "classification":
        return v1_type, {
            "prompt": item.prompt,
            "categories": list(item.categories),
            "elements": list(item.elements),
            "correct_categories": list(item.correct_categories),
            "explanation": item.explanation,
        }
    if v1_type == "ordering":
        items = [{"id": f"item{i}", "label": label} for i, label in enumerate(item.order_items)]
        correct_order = [items[i]["id"] for i in item.correct_order]
        items = shuffle_ordering_items(items, correct_order)
        return v1_type, {"prompt": item.prompt, "items": items, "correct_order": correct_order, "explanation": item.explanation}
    if v1_type in ("short_answer", "vocabulary"):
        return v1_type, {
            "prompt": item.prompt,
            "accepted_answers": list(item.accepted_answers),
            "rubric": item.explanation if not item.accepted_answers else "",
        }
    # long_answer / diagnostic : l'explanation éditoriale sert déjà de grille de correction.
    return v1_type, {"prompt": item.prompt, "rubric": item.explanation}


def import_mc01_legacy_to_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe les 12 exercices MC01 déjà rédigés (`app.seed.MC01_BLOCKS`,
    `editorial_exercise`) dans la banque V1, scopés à `uaa` (MC01 précisément — voir
    `Question.uaa_id`, ticket #55). Idempotent au niveau processus : si des Question
    existent déjà pour cette UAA avec `generation_source=IMPORTED`, ne réimporte rien —
    jamais de doublon à chaque `seed-db`/démarrage."""
    from app.seed import MC01_BLOCKS  # import différé : évite un cycle app.seed <-> app.v1

    already_imported = (
        db.query(Question)
        .filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED)
        .count()
    )
    if already_imported:
        return 0

    imported = 0
    for block_data in MC01_BLOCKS:
        if block_data["type"] != BlockType.EDITORIAL_EXERCISE:
            continue
        config = EditorialExerciseBlockConfig.from_json(block_data["content"])
        for item in config.items:
            try:
                v1_type, content = _editorial_item_to_v1_content(item)
                validate_content(v1_type, 1, content)
            except (BankImportError, ContentValidationError, QuestionEngineError):
                continue
            create_question(
                db,
                module_id=module.id,
                uaa_id=uaa.id,
                question_type=v1_type,
                content_json=content,
                generation_source=GenerationSource.IMPORTED,
            )
            imported += 1
    db.flush()
    return imported


def get_module_by_uaa_slug(db: Session, uaa_slug: str) -> Module | None:
    uaa = db.query(UAA).filter_by(slug=uaa_slug).first()
    return uaa.module if uaa is not None else None


def get_uaa_by_slug(db: Session, uaa_slug: str) -> UAA | None:
    return db.query(UAA).filter_by(slug=uaa_slug).first()


def _seen_signatures(db: Session, *, user_id: int) -> list:
    """Signatures structurelles (voir `app.v1.dedup`) des questions déjà vues par
    l'utilisateur, tous mini-cours confondus — sert à détecter un quasi-doublon d'une
    question déjà vue même sous une autre `Question.id` (ex. options réordonnées par une
    génération IA ultérieure, § 2 du ticket #64 : « réordonner les options ne doit pas
    suffire à rendre une question nouvelle »). Ignoré si l'utilisateur n'a encore rien vu
    (repli rapide, requête évitée)."""
    seen_question_ids = {
        row[0]
        for row in db.query(UserQuestionHistory.question_id).filter_by(user_id=user_id).distinct()
    }
    if not seen_question_ids:
        return []
    seen_questions = db.query(Question).filter(Question.id.in_(seen_question_ids)).all()
    return [
        question_signature(q.current_version.question_type, q.current_version.content_json)
        for q in seen_questions
        if q.current_version is not None
    ]


def _split_unseen_and_seen(
    all_active: list[Question], *, seen_question_ids: set[int], seen_signatures: list
) -> tuple[list[Question], list[Question]]:
    """Répartit `all_active` en (jamais-vues, déjà-vues-ou-quasi-doublons-d'une-vue) — voir
    `_seen_signatures`. Un ancien quasi-doublon d'une question vue tombe côté « déjà vue »
    même si son `Question.id` propre n'a jamais été servi à cet utilisateur."""
    unseen: list[Question] = []
    seen: list[Question] = []
    for candidate in all_active:
        if candidate.id in seen_question_ids:
            seen.append(candidate)
            continue
        version = candidate.current_version
        if version is not None and seen_signatures:
            candidate_signature = question_signature(version.question_type, version.content_json)
            if find_near_duplicate(candidate_signature, seen_signatures) is not None:
                seen.append(candidate)
                continue
        unseen.append(candidate)
    return unseen, seen


def select_bank_questions(
    db: Session,
    *,
    user_id: int,
    module_id: int,
    uaa_id: int | None,
    limit: int,
    only_unseen: bool = False,
) -> list[Question]:
    """Sélectionne jusqu'à `limit` questions ACTIVE, en excluant celles déjà vues par
    l'utilisateur — par identité exacte ET par quasi-doublon structurel (voir
    `_split_unseen_and_seen`) — quand c'est possible. `uaa_id` scope à un mini-cours
    précis ; `None` interroge tout le module (parcours global AMPCR, § 16 du ticket #55).

    `only_unseen=True` (ticket #64 § 1, priorité anti-répétition) : ne renvoie QUE des
    questions jamais vues (ni par id, ni par quasi-doublon), quitte à retourner moins que
    `limit` — c'est à l'appelant (`app.v1.session_service.start_session`) d'enchaîner sur
    une génération ciblée puis, en tout dernier recours seulement, un repli explicite sur
    une question déjà vue (nouvel appel avec `only_unseen=False`) — jamais ce module qui
    mélange silencieusement les deux, pour que « générer avant de recycler » reste une
    vraie séquence observable plutôt qu'un mélange aléatoire.

    `only_unseen=False` (par défaut, comportement historique) : repli explicite intégré —
    si le nombre de questions jamais vues est insuffisant, complète avec des questions déjà
    vues plutôt que d'échouer."""
    seen_question_ids = {
        row[0]
        for row in db.query(UserQuestionHistory.question_id).filter_by(user_id=user_id).distinct()
    }
    seen_signatures = _seen_signatures(db, user_id=user_id)

    query = db.query(Question).filter_by(module_id=module_id, status=ContentStatus.ACTIVE)
    query = query.filter_by(uaa_id=uaa_id) if uaa_id is not None else query.filter(Question.uaa_id.is_not(None))
    all_active = query.order_by(func.random()).all()
    unseen, seen = _split_unseen_and_seen(
        all_active, seen_question_ids=seen_question_ids, seen_signatures=seen_signatures
    )

    if only_unseen:
        return unseen[:limit]

    selected = unseen[:limit]
    if len(selected) < limit:
        selected += seen[: limit - len(selected)]
    return selected


def recent_seen_prompts(
    db: Session, *, user_id: int, module_id: int, uaa_id: int | None = None, limit: int = 25
) -> list[str]:
    """Énoncés des questions les plus récemment vues par l'utilisateur (practice ET exam —
    `UserQuestionHistory` ne distingue pas le mode, alimentée par `record_question_seen`
    dans les deux cas, voir `app.v1.session_service._finalize_session`), scopés au module/
    mini-cours concerné — transmis à la génération IA (`avoid_prompts`,
    `app.ai.schemas.QuestionnaireRequest`) pour qu'elle produise de VRAIES variantes plutôt
    que de resservir une notion déjà couverte sous une autre forme (ticket #64 § 3)."""
    history_rows = (
        db.query(UserQuestionHistory, Question)
        .join(Question, Question.id == UserQuestionHistory.question_id)
        .filter(UserQuestionHistory.user_id == user_id, Question.module_id == module_id)
    )
    if uaa_id is not None:
        history_rows = history_rows.filter(Question.uaa_id == uaa_id)
    history_rows = history_rows.order_by(UserQuestionHistory.last_seen_at.desc()).limit(limit).all()
    prompts: list[str] = []
    for _history, question in history_rows:
        version = question.current_version
        prompt = (version.content_json or {}).get("prompt") if version else None
        if isinstance(prompt, str) and prompt.strip():
            prompts.append(prompt.strip())
    return prompts


def _question_full_text(question: Question) -> str:
    """Texte complet (énoncé + catégories/options/éléments) pour la garde anti-méta MC38 —
    le seul `prompt` ne suffit pas, voir `app.v1.mc38_transversal.
    question_full_text_from_content_json`."""
    from app.v1.mc38_transversal import question_full_text_from_content_json

    content = question.current_version.content_json if question.current_version else {}
    return question_full_text_from_content_json(content) if isinstance(content, dict) else ""


def select_transversal_bank_questions(
    db: Session, *, user_id: int, module_id: int, limit: int, only_unseen: bool = False
) -> list[Question]:
    """Sélection dédiée à MC38 (ticket #58, révision transversale). Puise dans les
    mini-cours MC01→MC37 réels ET dans le bucket propre de MC38 (où sont stockées les
    questions déjà générées par une session MC38 précédente, voir
    `app.v1.session_service._start_mc38_transversal_session`) — jamais dans le CONTEXTE
    pédagogique MC38 pour la GÉNÉRATION (voir `app.v1.mc38_transversal.
    pick_transversal_contexts`, qui ignore toujours MC38). Exclut par sécurité toute
    question déjà en banque qui ressemblerait à une question MÉTA sur le processus de
    révision (garde défensive contre d'éventuelles questions déjà générées avant ce
    ticket — voir le rapport de ticket).

    `only_unseen` : voir `select_bank_questions`, même contrat (ticket #64 § 1)."""
    from app.models import UAA
    from app.v1.mc38_transversal import MC38_CODE, is_meta_revision_question, mc01_to_mc37_codes

    uaa_ids = [
        row[0]
        for row in db.query(UAA.id).filter(
            UAA.module_id == module_id, UAA.code.in_([*mc01_to_mc37_codes(), MC38_CODE])
        )
    ]
    if not uaa_ids:
        return []

    seen_question_ids = {
        row[0]
        for row in db.query(UserQuestionHistory.question_id).filter_by(user_id=user_id).distinct()
    }
    seen_signatures = _seen_signatures(db, user_id=user_id)

    query = db.query(Question).filter(
        Question.module_id == module_id,
        Question.status == ContentStatus.ACTIVE,
        Question.uaa_id.in_(uaa_ids),
    )
    all_active = [q for q in query.order_by(func.random()).all() if not is_meta_revision_question(_question_full_text(q))]
    unseen, seen = _split_unseen_and_seen(
        all_active, seen_question_ids=seen_question_ids, seen_signatures=seen_signatures
    )

    if only_unseen:
        return unseen[:limit]

    selected = unseen[:limit]
    if len(selected) < limit:
        selected += seen[: limit - len(selected)]
    return selected


def persist_generated_questions(
    db: Session,
    *,
    module_id: int,
    uaa_id: int | None,
    questions: list[QuestionnaireQuestion],
    domain_rejections: list[str] | None = None,
) -> list[Question]:
    """Valide, dans l'ordre, (1) registre #40 structurel, (2) `app.v1.domain_validation`
    (ticket #68, vérité technique — ex. IPv4/subnetting), (3) `app.v1.quality_validation`
    (ticket #69, clarté/qualité pédagogique — ex. ordering déjà trié, énoncé qui révèle sa
    propre réponse) avant de persister des questions générées par lot — voir
    `app/v1/ai_bridge.py::questionnaire_question_to_content`. Une question dont la
    conversion/validation structurelle échoue est ignorée plutôt que de faire échouer tout
    le lot ; une question structurellement valide mais techniquement fausse OU de mauvaise
    qualité pédagogique est rejetée de la même façon — jamais persistée, jamais servie —
    et journalisée (`DOMAIN_VALIDATION_REJECTED`/`QUALITY_VALIDATION_REJECTED`).

    `domain_rejections` (optionnel) : si fourni, le type de chaque question rejetée par la
    validation MÉTIER **ou** QUALITÉ (jamais structurelle ni dédoublonnage) y est ajouté —
    permet à l'appelant (`app.v1.session_service._generate_with_domain_retry`, ticket #68
    § 15) de savoir si un manque après persistance vient réellement d'un rejet
    métier/qualité (auquel cas un appel de complément ciblé est justifié) ou d'une autre
    cause (dédoublonnage #64, contenu structurellement invalide) qui ne doit JAMAIS
    déclencher un second appel IA — préserve l'invariant « un seul appel par session » du
    ticket #55 hors de ce cas précis.

    Déduplication (ticket #64 § 2) : une question dont la signature structurelle (voir
    `app.v1.dedup`) est un quasi-doublon d'une question ACTIVE déjà en banque pour ce
    même module/mini-cours est ignorée plutôt que persistée — un réordonnancement des
    options ou une reformulation superficielle par le générateur ne doit jamais suffire à
    faire grossir la banque d'une variante qui n'en est pas une. Comparée aussi aux
    questions déjà acceptées DANS CE MÊME lot (un lot généré en un appel peut lui-même
    contenir des quasi-doublons entre elles)."""
    module = db.get(Module, module_id)
    uaa = db.get(UAA, uaa_id) if uaa_id is not None else None

    existing_query = db.query(Question).filter_by(module_id=module_id, status=ContentStatus.ACTIVE)
    existing_query = (
        existing_query.filter_by(uaa_id=uaa_id) if uaa_id is not None else existing_query.filter(Question.uaa_id.is_(None))
    )
    existing_signatures = [
        question_signature(q.current_version.question_type, q.current_version.content_json)
        for q in existing_query.all()
        if q.current_version is not None
    ]

    persisted: list[Question] = []
    accepted_signatures: list = []
    for question in questions:
        try:
            content = questionnaire_question_to_content(question)
            validate_content(question.type, 1, content)
        except (ContentValidationError, QuestionEngineError, KeyError, ValueError):
            continue

        domain_errors = validate_domain_question(module, uaa, question.type, content)
        if domain_errors:
            logger.warning(
                "DOMAIN_VALIDATION_REJECTED uaa=%s question_type=%s reasons=%s",
                uaa.code if uaa is not None else None,
                question.type,
                domain_errors,
            )
            if domain_rejections is not None:
                domain_rejections.append(question.type)
            continue

        quality_errors = validate_question_quality(module, uaa, question.type, content)
        if quality_errors:
            logger.warning(
                "QUALITY_VALIDATION_REJECTED uaa=%s question_type=%s reasons=%s",
                uaa.code if uaa is not None else None,
                question.type,
                quality_errors,
            )
            if domain_rejections is not None:
                domain_rejections.append(question.type)
            continue

        candidate_signature = question_signature(question.type, content)
        if find_near_duplicate(candidate_signature, existing_signatures) is not None:
            continue
        if find_near_duplicate(candidate_signature, accepted_signatures) is not None:
            continue
        stored = create_question(
            db,
            module_id=module_id,
            uaa_id=uaa_id,
            question_type=question.type,
            content_json=content,
            generation_source=GenerationSource.AI_GENERATED,
        )
        persisted.append(stored)
        accepted_signatures.append(candidate_signature)
    db.flush()
    return persisted

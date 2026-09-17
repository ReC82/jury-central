"""Banque de questions V1 — service minimal (ticket #55, condensation de #41/#43).

Ne construit pas l'admin #46. Fournit uniquement :
- import du contenu MC01 déjà rédigé (`app.editorial_exercise`) vers la banque V1, via le
  registre #40 (aucune solution privée stockée hors du contrat validé) ;
- sélection de questions ACTIVE pour un module, en évitant les questions déjà vues par
  l'utilisateur quand c'est possible (repli sur les questions déjà vues sinon, jamais un
  échec de session pour ce motif — voir § BANQUE MVP du ticket) ;
- persistance de questions générées par lot (voir `app/v1/ai_bridge.py`), toujours
  revalidées par `app.v1.question_engine.validate_content` avant stockage.

Aucun contenu legacy n'est supprimé : `app.editorial_exercise`/MC01_BLOCKS restent
strictement inchangés (voir `app/main.py` pour le nouveau routage qui ne les rend plus
pour les UAA migrées, sans jamais les retirer de la base)."""

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.schemas import QuestionnaireQuestion
from app.editorial_exercise import EditorialExerciseBlockConfig, EditorialExerciseItem
from app.models import UAA, BlockType, Module
from app.v1 import question_types  # noqa: F401 — enregistre les 26 types (#40) au chargement
from app.v1.ai_bridge import questionnaire_question_to_content
from app.v1.models import (
    ContentStatus,
    GenerationSource,
    Question,
    UserQuestionHistory,
    create_question,
)
from app.v1.question_engine import ContentValidationError, QuestionEngineError, validate_content

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


def select_bank_questions(
    db: Session, *, user_id: int, module_id: int, uaa_id: int | None, limit: int
) -> list[Question]:
    """Sélectionne jusqu'à `limit` questions ACTIVE, en excluant celles déjà vues par
    l'utilisateur quand c'est possible. `uaa_id` scope à un mini-cours précis ; `None`
    interroge tout le module (parcours global AMPCR, § 16 du ticket #55). Repli explicite :
    si le nombre de questions JAMAIS vues est insuffisant, complète avec des questions déjà
    vues plutôt que d'échouer — jamais moins de questions que ce que la banque peut
    réellement fournir."""
    seen_question_ids = {
        row[0]
        for row in db.query(UserQuestionHistory.question_id).filter_by(user_id=user_id).distinct()
    }

    query = db.query(Question).filter_by(module_id=module_id, status=ContentStatus.ACTIVE)
    query = query.filter_by(uaa_id=uaa_id) if uaa_id is not None else query.filter(Question.uaa_id.is_not(None))
    all_active = query.order_by(func.random()).all()
    unseen = [q for q in all_active if q.id not in seen_question_ids]
    seen = [q for q in all_active if q.id in seen_question_ids]

    selected = unseen[:limit]
    if len(selected) < limit:
        selected += seen[: limit - len(selected)]
    return selected


def persist_generated_questions(
    db: Session, *, module_id: int, uaa_id: int | None, questions: list[QuestionnaireQuestion]
) -> list[Question]:
    """Valide (registre #40) puis persiste des questions générées par lot — voir
    `app/v1/ai_bridge.py::questionnaire_question_to_content`. Une question dont la
    conversion/validation échoue est ignorée plutôt que de faire échouer tout le lot."""
    persisted: list[Question] = []
    for question in questions:
        try:
            content = questionnaire_question_to_content(question)
            validate_content(question.type, 1, content)
        except (ContentValidationError, QuestionEngineError, KeyError, ValueError):
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
    db.flush()
    return persisted

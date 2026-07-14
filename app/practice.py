from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.answer_checking import answers_match
from app.database import get_db
from app.exercise_blocks import exercise_to_public_dict
from app.quiz import QuizConfig
from app.templating import templates
from app.value_table import check_value_table_answers
from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise
from generators.maths.equations import generate
from generators.registry import get_generator

router = APIRouter(prefix="/practice", tags=["practice"])


class VerifyExerciseRequest(BaseModel):
    generator: str
    difficulty: int
    seed: int
    answer: str


class RevealExerciseRequest(BaseModel):
    generator: str
    difficulty: int
    seed: int


class VerifyQuizRequest(BaseModel):
    answer: str


class VerifyValueTableRequest(BaseModel):
    generator: str
    difficulty: int
    seed: int
    answers: list[str]


@router.get("/equations", response_class=HTMLResponse)
async def practice_equations(request: Request, difficulty: int = 1) -> HTMLResponse:
    difficulty = max(1, min(difficulty, 3))
    exercise = generate(difficulty=difficulty)
    return templates.TemplateResponse(
        request=request,
        name="practice_equations.html",
        context={"exercise": exercise, "difficulty": difficulty},
    )


def _get_generator_or_404(generator_id: str):
    try:
        return get_generator(generator_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Générateur inconnu")


def _require_generated_exercise(exercise) -> GeneratedExercise:
    """Garde-fou : ces routes ne savent traiter que l'ancien format `GeneratedExercise`
    (énoncé texte, une seule réponse). Un générateur `value_table` doit passer par
    `/api/value-table/verify` — voir docs/EXERCISE_TYPES.md."""
    if not isinstance(exercise, GeneratedExercise):
        raise HTTPException(
            status_code=400,
            detail="Ce générateur ne produit pas d'exercice de ce type (utiliser "
            "/practice/api/value-table/verify pour un exercice value_table).",
        )
    return exercise


@router.get("/api/generate")
async def api_generate_exercise(generator: str, difficulty: int = 1) -> JSONResponse:
    generator_fn = _get_generator_or_404(generator)
    exercise = _require_generated_exercise(generator_fn(difficulty=difficulty))
    return JSONResponse(exercise_to_public_dict(exercise))


@router.post("/api/verify")
async def api_verify_exercise(payload: VerifyExerciseRequest) -> JSONResponse:
    """Régénère l'exercice à partir du seed et compare, sans jamais avoir stocké
    la réponse côté client."""
    generator_fn = _get_generator_or_404(payload.generator)
    exercise = _require_generated_exercise(
        generator_fn(difficulty=payload.difficulty, seed=payload.seed)
    )
    correct = answers_match(exercise.answer, payload.answer)
    return JSONResponse({"correct": correct})


@router.post("/api/reveal")
async def api_reveal_exercise(payload: RevealExerciseRequest) -> JSONResponse:
    """Révèle la correction détaillée, uniquement appelé après action explicite."""
    generator_fn = _get_generator_or_404(payload.generator)
    exercise = _require_generated_exercise(
        generator_fn(difficulty=payload.difficulty, seed=payload.seed)
    )
    return JSONResponse(
        {"solution_steps": exercise.solution_steps, "answer_display": str(exercise.answer)}
    )


@router.post("/api/value-table/verify")
async def api_verify_value_table(payload: VerifyValueTableRequest) -> JSONResponse:
    """Régénère l'exercice value_table à partir du seed et vérifie cellule par cellule,
    sans jamais avoir stocké la réponse côté client (voir docs/EXERCISE_TYPES.md)."""
    generator_fn = _get_generator_or_404(payload.generator)
    exercise = generator_fn(difficulty=payload.difficulty, seed=payload.seed)
    if not isinstance(exercise, InteractiveExercise) or exercise.type != "value_table":
        raise HTTPException(
            status_code=400, detail="Ce générateur ne produit pas d'exercice value_table."
        )
    try:
        correction = check_value_table_answers(exercise, payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return JSONResponse(correction.to_dict())


@router.post("/api/quiz/{block_id}/verify")
async def api_verify_quiz(
    block_id: int, payload: VerifyQuizRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    block = db.get(models.LessonBlock, block_id)
    if block is None or block.type != models.BlockType.QUIZ or not block.is_published:
        raise HTTPException(status_code=404, detail="Question introuvable")

    config = QuizConfig.from_json(block.content)
    correct = config.check(payload.answer)
    return JSONResponse(
        {
            "correct": correct,
            "explanation": config.explanation,
            "correct_index": config.correct_index if config.answer_type == "choice" else None,
        }
    )

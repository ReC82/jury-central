from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.ai import context as ai_context
from app.ai.factory import get_ai_provider
from app.ai.integrity import sign_exercise, verify_exercise_signature
from app.ai.provider import AINotConfiguredError, AIProviderError
from app.ai_exercise_blocks import AIExerciseBlockConfig
from app.answer_checking import answers_match
from app.content import render_markdown
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

Difficulty = Literal["facile", "moyen", "difficile"]


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


class GenerateAIExerciseRequest(BaseModel):
    block_id: int
    difficulty: Difficulty


class CorrectAIExerciseRequest(BaseModel):
    block_id: int
    exercise_statement: str
    exercise_type: str
    difficulty: Difficulty
    statement_token: str
    answer: str


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
        {
            "solution_steps": exercise.solution_steps,
            "solution_steps_html": [render_markdown(step) for step in exercise.solution_steps],
            "answer_display": str(exercise.answer),
        }
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
            "explanation_html": render_markdown(config.explanation) if config.explanation else "",
            "correct_index": config.correct_index if config.answer_type == "choice" else None,
        }
    )


def _load_ai_exercise_config(block_id: int, db: Session) -> AIExerciseBlockConfig:
    block = db.get(models.LessonBlock, block_id)
    if block is None or block.type != models.BlockType.AI_EXERCISE or not block.is_published:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    return AIExerciseBlockConfig.from_json(block.content)


def _resolve_pedagogical_context(config: AIExerciseBlockConfig):
    pedagogical_context = ai_context.get_context(config.context_key)
    if pedagogical_context is None:
        raise HTTPException(
            status_code=500, detail="Contexte pédagogique introuvable pour cet exercice."
        )
    return pedagogical_context


@router.post("/api/ai/generate")
async def api_generate_ai_exercise(
    payload: GenerateAIExerciseRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    """Génère un exercice à la demande, borné au contexte pédagogique du cours (voir
    app/ai/context.py). Ne stocke jamais l'exercice : l'énoncé est signé (HMAC) et renvoyé
    tel quel au client, qui devra le re-présenter intact pour la correction (voir
    app/ai/integrity.py)."""
    config = _load_ai_exercise_config(payload.block_id, db)
    pedagogical_context = _resolve_pedagogical_context(config)

    try:
        exercise = get_ai_provider().generate_exercise(pedagogical_context, payload.difficulty)
    except AINotConfiguredError as exc:
        raise HTTPException(
            status_code=503, detail="Génération IA non configurée sur ce serveur."
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    token = sign_exercise(
        payload.block_id, exercise.difficulty, exercise.exercise_type, exercise.statement
    )
    return JSONResponse(
        {
            "exercise_type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "statement": exercise.statement,
            "statement_html": render_markdown(exercise.statement),
            "statement_token": token,
        }
    )


@router.post("/api/ai/correct")
async def api_correct_ai_exercise(
    payload: CorrectAIExerciseRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    """Corrige une réponse via l'IA. La réponse du candidat est transmise au fournisseur
    comme une donnée à évaluer, jamais comme une instruction (voir app/ai/prompts.py) ;
    aucune correction IA ne modifie jamais le contenu du bloc en base."""
    config = _load_ai_exercise_config(payload.block_id, db)
    pedagogical_context = _resolve_pedagogical_context(config)

    if not verify_exercise_signature(
        payload.block_id,
        payload.difficulty,
        payload.exercise_type,
        payload.exercise_statement,
        payload.statement_token,
    ):
        raise HTTPException(
            status_code=400,
            detail="Exercice invalide ou modifié : génère un nouvel exercice avant de le "
            "corriger.",
        )

    try:
        correction = get_ai_provider().correct_answer(
            pedagogical_context,
            exercise_statement=payload.exercise_statement,
            exercise_type=payload.exercise_type,
            difficulty=payload.difficulty,
            candidate_answer=payload.answer,
        )
    except AINotConfiguredError as exc:
        raise HTTPException(
            status_code=503, detail="Correction IA non configurée sur ce serveur."
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    result = correction.to_dict()
    result["appreciation_html"] = render_markdown(result["appreciation"])
    result["expected_answer_explained_html"] = (
        render_markdown(result["expected_answer_explained"])
        if result["expected_answer_explained"]
        else ""
    )
    return JSONResponse(result)

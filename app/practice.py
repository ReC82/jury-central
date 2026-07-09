from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.exercise_blocks import exercise_to_dict
from app.templating import templates
from generators.maths.equations import generate
from generators.registry import get_generator

router = APIRouter(prefix="/practice", tags=["practice"])


@router.get("/equations", response_class=HTMLResponse)
async def practice_equations(request: Request, difficulty: int = 1) -> HTMLResponse:
    difficulty = max(1, min(difficulty, 3))
    exercise = generate(difficulty=difficulty)
    return templates.TemplateResponse(
        request=request,
        name="practice_equations.html",
        context={"exercise": exercise, "difficulty": difficulty},
    )


@router.get("/api/generate")
async def api_generate_exercise(generator: str, difficulty: int = 1) -> JSONResponse:
    try:
        generator_fn = get_generator(generator)
    except KeyError:
        raise HTTPException(status_code=404, detail="Générateur inconnu")
    exercise = generator_fn(difficulty=difficulty)
    return JSONResponse(exercise_to_dict(exercise))

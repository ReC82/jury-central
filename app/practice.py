from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templating import templates
from generators.maths.equations import generate

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

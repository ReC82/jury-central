"""Routes du parcours « AMPCR — Pratique écrite » (ticket #192) : accueil, matrice de
couverture officielle et format d'exercice. Lecture seule, publiques comme le reste des
cours ; la progression n'apparaît qu'une fois connecté. Voir `app.v1.ampcr_pratique_plan`."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.database import get_db
from app.templating import templates
from app.v1 import ampcr_pratique_plan as plan
from app.v1.ampcr_pratique_format import EXAMPLE_EXERCISE, build_rubric
from app.v1.auth import get_current_user
from app.v1.parcours import uaa_state, user_uaa_progress

router = APIRouter()


def _common_context(db) -> dict:
    published = plan.published_uaas(db)
    rows = plan.coverage_rows(frozenset(published))
    return {
        "plan": plan,
        "published": published,
        "theory": plan.theory_uaas(db),
        "rows": rows,
        "summary": plan.coverage_summary(rows),
    }


@router.get(plan.PRACTICAL_PATH_URL, response_class=HTMLResponse)
async def practical_home(request: Request, db=Depends(get_db)):  # noqa: B008
    context = _common_context(db)
    user = get_current_user(request, db)
    progress = user_uaa_progress(db, user)
    published = context["published"]
    states = {code: uaa_state(progress.get(uaa.id)) for code, uaa in published.items()}
    modules = []
    for module in plan.MODULES:
        courses = [plan.COURSE_SLOTS_BY_CODE[code] for code in module.course_codes]
        exercise = plan.EXERCISE_SLOTS_BY_CODE[module.exercise_code]
        requirement_ids = sorted({r for c in courses for r in c.requirement_ids})
        theory_codes = sorted(
            {t for r in requirement_ids for t in plan.REQUIREMENTS_BY_ID[r].theory_codes}
        )
        modules.append(
            {
                "module": module,
                "courses": courses,
                "exercise": exercise,
                "requirement_ids": requirement_ids,
                "theory_codes": theory_codes,
                "published_count": sum(1 for c in courses if c.code in published),
            }
        )
    context.update(
        {
            "modules": modules,
            "states": states,
            "published_course_count": sum(1 for c in plan.COURSE_SLOTS if c.code in published),
            "published_exercise_count": sum(1 for e in plan.EXERCISE_SLOTS if e.code in published),
        }
    )
    return templates.TemplateResponse(request=request, name="ampcr_pratique_home.html", context=context)


@router.get(f"{plan.PRACTICAL_PATH_URL}/matrice", response_class=HTMLResponse)
async def practical_matrix(request: Request, db=Depends(get_db)):  # noqa: B008
    return templates.TemplateResponse(
        request=request, name="ampcr_pratique_matrix.html", context=_common_context(db)
    )


@router.get(f"{plan.PRACTICAL_PATH_URL}/format-exercice", response_class=HTMLResponse)
async def practical_exercise_format(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="ampcr_pratique_format.html",
        context={
            "plan": plan,
            "exercise": EXAMPLE_EXERCISE,
            "rubric": build_rubric(EXAMPLE_EXERCISE),
        },
    )

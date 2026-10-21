"""Routes du parcours (ticket #136) : assistant Diplôme → Forme → Option et tableau de bord
« Mon parcours ». Public : un visiteur peut choisir et consulter son parcours (mémorisé en
session) ; la progression réelle n'apparaît qu'une fois connecté. Voir `app.v1.parcours`."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.database import get_db
from app.templating import templates
from app.v1.auth import get_current_user, validate_csrf_token
from app.v1.parcours import (
    REGISTRY,
    build_dashboard,
    get_diploma,
    get_form,
    get_saved_pathway,
    has_stored_pathway,
    resolve_keys,
    save_pathway,
)

router = APIRouter()


@router.get("/parcours", response_class=HTMLResponse)
async def choose_pathway(
    request: Request,
    diplome: str | None = None,
    forme: str | None = None,
    db=Depends(get_db),  # noqa: B008
) -> HTMLResponse:
    user = get_current_user(request, db)
    diploma = get_diploma(diplome)
    form = get_form(diploma, forme) if diploma else None
    if form is not None and not form.available:
        form = None
    step = 3 if form else (2 if diploma else 1)
    return templates.TemplateResponse(
        request=request,
        name="parcours_choose.html",
        context={
            "step": step,
            "registry": REGISTRY,
            "diploma": diploma,
            "form": form,
            "saved": get_saved_pathway(request, db, user),
        },
    )


@router.post("/parcours/choisir")
async def save_pathway_choice(
    request: Request,
    diploma: str = Form(...),
    form: str = Form(...),
    option: str = Form(...),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    pathway = resolve_keys(diploma, form, option)
    if pathway is None or not validate_csrf_token(request, csrf_token):
        return RedirectResponse(url="/parcours", status_code=303)
    save_pathway(request, db, get_current_user(request, db), pathway)
    return RedirectResponse(url="/mon-parcours", status_code=303)


@router.get("/mon-parcours", response_class=HTMLResponse)
async def my_pathway(request: Request, db=Depends(get_db)):  # noqa: B008
    user = get_current_user(request, db)
    pathway = get_saved_pathway(request, db, user)
    if pathway is None:
        return RedirectResponse(url="/parcours", status_code=303)
    if user is not None and not has_stored_pathway(db, user):
        # Choix fait avant connexion : rattaché au compte à la première visite connectée.
        save_pathway(request, db, user, pathway)
    return templates.TemplateResponse(
        request=request,
        name="parcours_dashboard.html",
        context=build_dashboard(db, pathway, user),
    )

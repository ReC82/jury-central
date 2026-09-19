"""Route du lexique AMPCR (ticket #84) — ressource pédagogique transverse, accessible
depuis Informatique → AMPCR → Lexique / Acronymes FR-EN. Lecture seule, aucune donnée de
session, mêmes règles d'accès qu'une page de cours (connexion requise, jamais publique —
voir `app.main` § UAA détail)."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.templating import templates
from app.v1.auth import require_user
from app.v1.lexicon import LEXICON_THEMES
from app.v1.models import User

router = APIRouter()


@router.get("/modules/ampcr/lexicon", response_class=HTMLResponse)
async def ampcr_lexicon(
    request: Request,
    user: User = Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="v1_lexicon.html",
        context={"themes": LEXICON_THEMES},
    )

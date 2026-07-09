from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin, verify_credentials
from app.database import get_db
from app.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request) -> HTMLResponse:
    if request.session.get("is_admin"):
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": None},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request, username: str = Form(...), password: str = Form(...)
) -> HTMLResponse:
    if verify_credentials(username, password):
        request.session["is_admin"] = True
        request.session["username"] = username
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": "Identifiants invalides"},
        status_code=401,
    )


@router.get("/logout", dependencies=[Depends(require_admin)])
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    dependencies=[Depends(require_admin)],
)
async def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    context = {
        "username": request.session.get("username"),
        "subject_count": db.query(models.Subject).count(),
        "module_count": db.query(models.Module).count(),
        "uaa_count": db.query(models.UAA).count(),
    }
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context=context,
    )

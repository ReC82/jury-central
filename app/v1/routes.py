"""Routes web d'authentification V1 (ticket #39) : /register, /login, /logout, /account.

Voir `docs/auth_v1.md` pour l'architecture (session, CSRF, protection open-redirect) et
`app/v1/auth.py` pour l'implémentation réutilisée ici. Ce routeur ne connaît aucun détail
de hachage/session lui-même — il orchestre uniquement la requête HTTP autour des helpers
de `app.v1.auth`."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.templating import templates
from app.v1.auth import (
    RegistrationError,
    authenticate_user,
    get_current_user,
    get_or_create_csrf_token,
    login_user,
    logout_user,
    record_login,
    register_user,
    require_user,
    safe_next_path,
    validate_csrf_token,
)
from app.v1.models import User

router = APIRouter(tags=["v1-auth"])


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:  # noqa: B008
    if get_current_user(request, db) is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="v1_register.html",
        context={"error": None, "csrf_token": get_or_create_csrf_token(request)},
    )


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    csrf_token: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    display_name: str = Form(""),
) -> HTMLResponse:
    if not validate_csrf_token(request, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="v1_register.html",
            context={
                "error": "Session expirée, réessaie.",
                "csrf_token": get_or_create_csrf_token(request),
            },
            status_code=400,
        )

    try:
        user = register_user(
            db,
            email=email,
            password=password,
            password_confirm=password_confirm,
            display_name=display_name,
        )
    except RegistrationError as exc:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="v1_register.html",
            context={"error": str(exc), "csrf_token": get_or_create_csrf_token(request)},
            status_code=400,
        )

    db.commit()
    login_user(request, user)
    return RedirectResponse(url="/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_form(
    request: Request, db: Session = Depends(get_db), next: str = "/"  # noqa: B008
) -> HTMLResponse:
    if get_current_user(request, db) is not None:
        return RedirectResponse(url=safe_next_path(next), status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="v1_login.html",
        context={
            "error": None,
            "csrf_token": get_or_create_csrf_token(request),
            "next": safe_next_path(next),
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    csrf_token: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
) -> HTMLResponse:
    safe_target = safe_next_path(next)
    if not validate_csrf_token(request, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="v1_login.html",
            context={
                "error": "Session expirée, réessaie.",
                "csrf_token": get_or_create_csrf_token(request),
                "next": safe_target,
            },
            status_code=400,
        )

    user = authenticate_user(db, email=email, password=password)
    if user is None:
        # Message générique volontaire : ne révèle jamais si l'email existe (voir
        # app.v1.auth.authenticate_user, docstring).
        return templates.TemplateResponse(
            request=request,
            name="v1_login.html",
            context={
                "error": "Email ou mot de passe incorrect.",
                "csrf_token": get_or_create_csrf_token(request),
                "next": safe_target,
            },
            status_code=401,
        )

    login_user(request, user)
    record_login(user)
    db.commit()
    return RedirectResponse(url=safe_target, status_code=303)


@router.post("/logout")
async def logout_submit(request: Request, csrf_token: str = Form(...)) -> RedirectResponse:
    if validate_csrf_token(request, csrf_token):
        logout_user(request)
    return RedirectResponse(url="/", status_code=303)


@router.get("/account", response_class=HTMLResponse)
async def account_page(
    request: Request, user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="v1_account.html",
        context={"account_user": user, "csrf_token": get_or_create_csrf_token(request)},
    )

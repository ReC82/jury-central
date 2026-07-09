from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin, verify_credentials
from app.database import get_db
from app.templating import templates

public_router = APIRouter(prefix="/admin", tags=["admin"])
protected_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@public_router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request) -> HTMLResponse:
    if request.session.get("is_admin"):
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": None},
    )


@public_router.post("/login", response_class=HTMLResponse)
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


@protected_router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)


@protected_router.get("/dashboard", response_class=HTMLResponse)
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


@protected_router.get("/subjects", response_class=HTMLResponse)
async def admin_list_subjects(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    subjects = db.query(models.Subject).order_by(models.Subject.name).all()
    return templates.TemplateResponse(
        request=request,
        name="admin_subjects.html",
        context={"subjects": subjects},
    )


@protected_router.get("/subjects/{subject_id}", response_class=HTMLResponse)
async def admin_subject_modules(
    subject_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_modules.html",
        context={"subject": subject},
    )


@protected_router.get("/modules/{module_id}", response_class=HTMLResponse)
async def admin_module_uaas(
    module_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_uaa_list.html",
        context={"module": module},
    )


@protected_router.get("/uaa/{uaa_id}", response_class=HTMLResponse)
async def admin_uaa_blocks(
    uaa_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_uaa_blocks.html",
        context={"uaa": uaa},
    )


@protected_router.get("/uaa/{uaa_id}/blocks/new", response_class=HTMLResponse)
async def admin_new_block_form(
    uaa_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    next_position = max((block.position for block in uaa.lesson_blocks), default=0) + 1
    return templates.TemplateResponse(
        request=request,
        name="admin_block_form.html",
        context={
            "uaa": uaa,
            "block": None,
            "block_types": list(models.BlockType),
            "next_position": next_position,
        },
    )


@protected_router.post("/uaa/{uaa_id}/blocks/new")
async def admin_create_block(
    uaa_id: int,
    title: str = Form(...),
    block_type: str = Form(alias="type"),
    content: str = Form(""),
    position: int = Form(0),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    try:
        parsed_type = models.BlockType(block_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de bloc invalide")

    db.add(
        models.LessonBlock(
            uaa=uaa,
            title=title,
            type=parsed_type,
            content=content,
            position=position,
            is_published=is_published,
        )
    )
    db.commit()
    return RedirectResponse(url=f"/admin/uaa/{uaa_id}", status_code=303)


@protected_router.get("/blocks/{block_id}/edit", response_class=HTMLResponse)
async def admin_edit_block_form(
    block_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    block = db.get(models.LessonBlock, block_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Bloc introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_block_form.html",
        context={
            "uaa": block.uaa,
            "block": block,
            "block_types": list(models.BlockType),
            "next_position": block.position,
        },
    )


@protected_router.post("/blocks/{block_id}/edit")
async def admin_update_block(
    block_id: int,
    title: str = Form(...),
    block_type: str = Form(alias="type"),
    content: str = Form(""),
    position: int = Form(0),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    block = db.get(models.LessonBlock, block_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Bloc introuvable")
    try:
        parsed_type = models.BlockType(block_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de bloc invalide")

    block.title = title
    block.type = parsed_type
    block.content = content
    block.position = position
    block.is_published = is_published
    db.commit()
    return RedirectResponse(url=f"/admin/uaa/{block.uaa_id}", status_code=303)


@protected_router.post("/blocks/{block_id}/delete")
async def admin_delete_block(block_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    block = db.get(models.LessonBlock, block_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Bloc introuvable")
    uaa_id = block.uaa_id
    db.delete(block)
    db.commit()
    return RedirectResponse(url=f"/admin/uaa/{uaa_id}", status_code=303)


router = APIRouter()
router.include_router(public_router)
router.include_router(protected_router)

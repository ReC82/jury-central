from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.admin import router as admin_router
from app.config import settings
from app.content import extract_youtube_id, render_markdown
from app.database import Base, engine, get_db
from app.templating import templates

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jury Central")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(admin_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


@app.get("/subjects", response_class=HTMLResponse)
async def list_subjects(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    subjects = db.query(models.Subject).order_by(models.Subject.name).all()
    return templates.TemplateResponse(
        request=request,
        name="subjects.html",
        context={"subjects": subjects},
    )


@app.get("/subjects/{subject_slug}", response_class=HTMLResponse)
async def subject_detail(
    subject_slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    subject = db.query(models.Subject).filter_by(slug=subject_slug).first()
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return templates.TemplateResponse(
        request=request,
        name="subject_detail.html",
        context={"subject": subject},
    )


@app.get("/modules/{module_slug}", response_class=HTMLResponse)
async def module_detail(
    module_slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.query(models.Module).filter_by(slug=module_slug).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    return templates.TemplateResponse(
        request=request,
        name="module_detail.html",
        context={"module": module},
    )


@app.get("/uaa/{uaa_slug}", response_class=HTMLResponse)
async def uaa_detail(
    uaa_slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    uaa = db.query(models.UAA).filter_by(slug=uaa_slug).first()
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")

    rendered_blocks = []
    for block in uaa.lesson_blocks:
        if not block.is_published:
            continue
        html = render_markdown(block.content) if block.type == models.BlockType.MARKDOWN else None
        youtube_id = (
            extract_youtube_id(block.content) if block.type == models.BlockType.YOUTUBE else None
        )
        rendered_blocks.append({"block": block, "html": html, "youtube_id": youtube_id})

    return templates.TemplateResponse(
        request=request,
        name="uaa_detail.html",
        context={"uaa": uaa, "rendered_blocks": rendered_blocks},
    )

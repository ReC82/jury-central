import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.admin import router as admin_router
from app.card_kind import card_meta, classify_block_title
from app.config import settings
from app.content import extract_youtube_id, render_markdown
from app.database import Base, engine, get_db
from app.exercise_blocks import ExerciseBlockConfig, exercise_to_public_dict, generate_exercises
from app.practice import router as practice_router
from app.quiz import QuizConfig
from app.templating import templates
from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jury Central")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(admin_router)
app.include_router(practice_router)


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
    if uaa is None or not uaa.is_published:
        raise HTTPException(status_code=404, detail="UAA introuvable")

    def empty_item(block: models.LessonBlock) -> dict:
        return {
            "block": block,
            "html": None,
            "youtube_id": None,
            "config": None,
            "exercises": None,
            "value_table_exercises": None,
            "quiz": None,
            "quiz_run": None,
            "card": card_meta(classify_block_title(block.title)),
        }

    rendered_blocks: list[dict] = []
    pending_group_name: str | None = None
    pending_group_entries: list[tuple[int, models.LessonBlock, QuizConfig]] = []

    def flush_group() -> None:
        nonlocal pending_group_name, pending_group_entries
        if pending_group_entries:
            pending_group_entries.sort(key=lambda entry: entry[0])
            questions = [
                config.to_public_dict(block.id) for _, block, config in pending_group_entries
            ]
            item = empty_item(pending_group_entries[0][1])
            item["quiz_run"] = {
                "questions_json": json.dumps(questions, ensure_ascii=False),
                "count": len(pending_group_entries),
            }
            item["card"] = card_meta("quiz")
            rendered_blocks.append(item)
        pending_group_name = None
        pending_group_entries = []

    for block in uaa.lesson_blocks:
        if not block.is_published:
            continue

        if block.type == models.BlockType.QUIZ:
            config = QuizConfig.from_json(block.content)
            if config.group:
                if pending_group_name is not None and pending_group_name != config.group:
                    flush_group()
                pending_group_name = config.group
                pending_group_entries.append((config.order_in_group, block, config))
                continue
            flush_group()
            item = empty_item(block)
            item["quiz"] = config
            item["card"] = card_meta("quiz")
            rendered_blocks.append(item)
            continue

        flush_group()
        item = empty_item(block)

        if block.type == models.BlockType.MARKDOWN:
            item["html"] = render_markdown(block.content)
        elif block.type == models.BlockType.YOUTUBE:
            item["youtube_id"] = extract_youtube_id(block.content)
        elif block.type == models.BlockType.GENERATED_EXERCISE:
            config = ExerciseBlockConfig.from_json(block.content)
            item["config"] = config
            item["card"] = card_meta("exercise")
            try:
                raw_exercises = generate_exercises(config)
            except KeyError:
                raw_exercises = []

            item["exercises"] = [
                exercise_to_public_dict(exercise)
                for exercise in raw_exercises
                if isinstance(exercise, GeneratedExercise)
            ]
            item["value_table_exercises"] = [
                {
                    "exercise_json": exercise.to_public_json(),
                    "generator": config.generator,
                    "difficulty": exercise.difficulty,
                    "seed": exercise.seed,
                }
                for exercise in raw_exercises
                if isinstance(exercise, InteractiveExercise) and exercise.type == "value_table"
            ]

        rendered_blocks.append(item)

    flush_group()

    needs_plotly = any(
        item["html"] and "jc-graph-constant" in item["html"] for item in rendered_blocks
    )

    return templates.TemplateResponse(
        request=request,
        name="uaa_detail.html",
        context={"uaa": uaa, "rendered_blocks": rendered_blocks, "needs_plotly": needs_plotly},
    )

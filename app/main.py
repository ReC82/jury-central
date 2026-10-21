import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.admin import router as admin_router
from app.ai import context as ai_context
from app.ai_exercise_blocks import AIExerciseBlockConfig
from app.card_kind import card_meta, classify_block_title
from app.config import settings
from app.content import extract_youtube_id, render_markdown
from app.database import Base, engine, ensure_schema_migrations, get_db
from app.editorial_exercise import EditorialExerciseBlockConfig
from app.exercise_blocks import ExerciseBlockConfig, exercise_to_public_dict, generate_exercises
from app.practice import router as practice_router
from app.quiz import QuizConfig
from app.templating import templates
from app.v1 import models as v1_models  # noqa: F401 — enregistre les tables V1 (#38)
from app.v1 import question_types as v1_question_types  # noqa: F401 — enregistre les 26 types (#40)
from app.v1.ampcr_plan import get_plan_by_slug
from app.v1.auth import get_current_user, require_user
from app.v1.course_memo import apply_course_memo
from app.v1.francais_plan import get_francais_plan_by_slug
from app.v1.fse_plan import get_fse_plan_by_slug
from app.v1.parcours import (
    build_dashboard,
    get_saved_pathway,
    has_v1_sessions,
    listed_uaas,
    track_for_module,
    uaa_state,
    user_uaa_progress,
)
from app.v1.quiz_service import quiz_question_counts
from app.v1.routes import router as v1_auth_router
from app.v1.routes_admin_bank import router as v1_admin_bank_router
from app.v1.routes_lexicon import router as v1_lexicon_router
from app.v1.routes_parcours import router as v1_parcours_router
from app.v1.routes_quiz import router as v1_quiz_router
from app.v1.routes_sessions import render_exam_landing, render_practice_landing
from app.v1.routes_sessions import router as v1_sessions_router
from app.value_table import value_table_public_dict
from generators.base import GeneratedExercise
from generators.exercise_types import InteractiveExercise

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)
ensure_schema_migrations()

app = FastAPI(title="Jury Central")
# `https_only` : voir app/config.py::Settings.app_env — False tant que .env ne déclare
# pas explicitement APP_ENV=staging/prod (comportement inchangé par défaut, voir
# docs/auth_v1.md, § Session).
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    https_only=settings.app_env in ("staging", "prod"),
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(admin_router)
app.include_router(v1_admin_bank_router)
app.include_router(practice_router)
app.include_router(v1_auth_router)
app.include_router(v1_sessions_router)
app.include_router(v1_lexicon_router)
app.include_router(v1_parcours_router)
app.include_router(v1_quiz_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:  # noqa: B008
    # Ticket #136 : accueil = point d'entrée du parcours. Parcours déjà mémorisé →
    # « Continuer » + aperçu réel (prochaine étape) ; sinon « Choisir mon parcours ».
    user = get_current_user(request, db)
    pathway = get_saved_pathway(request, db, user)
    dashboard = build_dashboard(db, pathway, user) if pathway else None
    subjects = db.query(models.Subject).order_by(models.Subject.name).all()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"pathway": pathway, "dashboard": dashboard, "subjects": subjects},
    )


def _subject_tile(subject: models.Subject) -> dict:
    """Tuile de matière (ticket #136) : habillage repris du registre de parcours quand la
    matière y figure, repli neutre sinon (ex. Mathématiques) — jamais de contenu inventé."""
    modules = [m for m in subject.modules if listed_uaas(m)]
    track = next((t for t in (track_for_module(m.code) for m in subject.modules) if t), None)
    return {
        "subject": subject,
        "modules": modules,
        "track": track,
        "course_count": sum(len(listed_uaas(m)) for m in modules),
    }


@app.get("/subjects", response_class=HTMLResponse)
async def list_subjects(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    subjects = db.query(models.Subject).order_by(models.Subject.name).all()
    return templates.TemplateResponse(
        request=request,
        name="subjects.html",
        context={"subjects": subjects, "tiles": [_subject_tile(s) for s in subjects]},
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
        context={"subject": subject, "tile": _subject_tile(subject)},
    )


@app.get("/modules/{module_slug}", response_class=HTMLResponse)
async def module_detail(
    module_slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.query(models.Module).filter_by(slug=module_slug).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    # Ticket #136 : chemin de cours (missions) — chaque cours garde son accès direct ;
    # Entraînement/Examen blanc proposés seulement s'ils existent réellement pour ce cours.
    user = get_current_user(request, db)
    progress = user_uaa_progress(db, user)
    uaas = listed_uaas(module)
    # Ticket #137 : quiz proposé seulement pour les cours qui ont des questions de quiz.
    quiz_counts = quiz_question_counts(db, [u.id for u in uaas])
    courses = []
    for uaa in uaas:
        spaces = {block.space for block in uaa.lesson_blocks}
        v1 = has_v1_sessions(uaa)
        courses.append(
            {
                "uaa": uaa,
                "state": uaa_state(progress.get(uaa.id)),
                "has_practice": v1 or models.BlockSpace.PRACTICE in spaces,
                "has_exam": v1 or models.BlockSpace.EXAM in spaces,
                "quiz_count": quiz_counts.get(uaa.id, 0),
            }
        )
    return templates.TemplateResponse(
        request=request,
        name="module_detail.html",
        context={
            "module": module,
            "courses": courses,
            "track": track_for_module(module.code),
            "quiz_total": sum(quiz_counts.values()),
        },
    )


def _render_lesson_blocks(blocks: list[models.LessonBlock]) -> tuple[list[dict], bool]:
    """Rend une liste de blocs de leçon déjà publiés en `rendered_blocks` pour un template.

    Générique : ne sait rien de l'UAA, du gabarit ni de l'espace pédagogique (COURSE/
    PRACTICE/EXAM, ticket #22) qui l'appelle — le tri par espace a lieu AVANT l'appel (voir
    les trois routes `/uaa/{slug}`, `/uaa/{slug}/practice`, `/uaa/{slug}/exam` ci-dessous),
    ce qui garde cette fonction, et le template qu'elle alimente, strictement identiques aux
    trois espaces.
    """

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
            "ai_exercise": None,
            "editorial_exercise": None,
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

    for block in blocks:
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
            item["quiz"] = config.to_public_dict(block.id)
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
                    "exercise_json": json.dumps(
                        value_table_public_dict(exercise), ensure_ascii=False
                    ),
                    "generator": config.generator,
                    "difficulty": exercise.difficulty,
                    "seed": exercise.seed,
                }
                for exercise in raw_exercises
                if isinstance(exercise, InteractiveExercise) and exercise.type == "value_table"
            ]
        elif block.type == models.BlockType.AI_EXERCISE:
            ai_config = AIExerciseBlockConfig.from_json(block.content)
            item["card"] = card_meta("exercise")
            pedagogical_context = ai_context.get_context(ai_config.context_key)
            if pedagogical_context is not None:
                item["ai_exercise"] = {
                    "block_id": block.id,
                    "intro_html": render_markdown(ai_config.intro) if ai_config.intro else "",
                }
        elif block.type == models.BlockType.EDITORIAL_EXERCISE:
            editorial_config = EditorialExerciseBlockConfig.from_json(block.content)
            item["card"] = card_meta("exercise")
            item["editorial_exercise"] = {
                "verify_url": f"/practice/api/editorial/{block.id}/verify",
                "items_json": json.dumps(
                    editorial_config.to_public_dict()["items"], ensure_ascii=False
                ),
            }

        rendered_blocks.append(item)

    flush_group()

    needs_plotly = any(
        item["html"] and "jc-graph-constant" in item["html"] for item in rendered_blocks
    )
    return rendered_blocks, needs_plotly


def _get_published_uaa(uaa_slug: str, db: Session) -> models.UAA:
    uaa = db.query(models.UAA).filter_by(slug=uaa_slug).first()
    if uaa is None or not uaa.is_published:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    return uaa


def _space_blocks(uaa: models.UAA, space: models.BlockSpace) -> list[models.LessonBlock]:
    return [block for block in uaa.lesson_blocks if block.space == space]


@app.get("/uaa/{uaa_slug}", response_class=HTMLResponse)
async def uaa_detail(
    uaa_slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    uaa = _get_published_uaa(uaa_slug, db)
    course_blocks = _space_blocks(uaa, models.BlockSpace.COURSE)
    rendered_blocks, needs_plotly = _render_lesson_blocks(course_blocks)
    # Ticket #136 (21/10) : séquence finale « À retenir » (synthèse, savoir-faire,
    # vocabulaire) qui reprend les sections mémo existantes au lieu de les dupliquer.
    apply_course_memo(
        uaa.module.code, uaa.code, uaa.slug, uaa.title, course_blocks, rendered_blocks
    )

    # Ticket #136 : cours précédent/suivant du même module (navigation libre, jamais un
    # verrou) et habillage de la matière.
    siblings = listed_uaas(uaa.module)
    index = next((i for i, u in enumerate(siblings) if u.id == uaa.id), None)
    prev_uaa = siblings[index - 1] if index else None
    next_uaa = siblings[index + 1] if index is not None and index + 1 < len(siblings) else None
    return templates.TemplateResponse(
        request=request,
        name="uaa_detail.html",
        context={
            "uaa": uaa,
            "rendered_blocks": rendered_blocks,
            "needs_plotly": needs_plotly,
            "active_space": "course",
            "track": track_for_module(uaa.module.code),
            "prev_uaa": prev_uaa,
            "next_uaa": next_uaa,
        },
    )


@app.get("/uaa/{uaa_slug}/practice", response_class=HTMLResponse)
async def uaa_practice(
    uaa_slug: str,
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    user=Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    uaa = _get_published_uaa(uaa_slug, db)

    # Ticket #55 : les UAA du programme AMPCR (MC01..MC38) utilisent désormais le
    # parcours de session V1 générique (banque + génération/correction par lot) plutôt
    # que le rendu legacy empilé — voir `app/v1/routes_sessions.py`. Le code legacy
    # (`_render_lesson_blocks`, `uaa_practice.html`) reste inchangé et continue de servir
    # toute UAA non migrée (Mathématiques, futur Français...), sans régression.
    if (
        get_plan_by_slug(uaa.slug) is not None
        or get_francais_plan_by_slug(uaa.slug) is not None
        or get_fse_plan_by_slug(uaa.slug) is not None
    ):
        return render_practice_landing(request, db, uaa, user)

    rendered_blocks, needs_plotly = _render_lesson_blocks(
        _space_blocks(uaa, models.BlockSpace.PRACTICE)
    )

    return templates.TemplateResponse(
        request=request,
        name="uaa_practice.html",
        context={
            "uaa": uaa,
            "rendered_blocks": rendered_blocks,
            "needs_plotly": needs_plotly,
            "active_space": "practice",
        },
    )


@app.get("/uaa/{uaa_slug}/exam", response_class=HTMLResponse)
async def uaa_exam(
    uaa_slug: str,
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    user=Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    uaa = _get_published_uaa(uaa_slug, db)

    if (
        get_plan_by_slug(uaa.slug) is not None
        or get_francais_plan_by_slug(uaa.slug) is not None
        or get_fse_plan_by_slug(uaa.slug) is not None
    ):
        return render_exam_landing(request, db, uaa, user)

    rendered_blocks, needs_plotly = _render_lesson_blocks(
        _space_blocks(uaa, models.BlockSpace.EXAM)
    )

    return templates.TemplateResponse(
        request=request,
        name="uaa_exam.html",
        context={
            "uaa": uaa,
            "rendered_blocks": rendered_blocks,
            "needs_plotly": needs_plotly,
            "active_space": "exam",
        },
    )

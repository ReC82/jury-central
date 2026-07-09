from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin, verify_credentials
from app.database import get_db
from app.exercise_blocks import ExerciseBlockConfig
from app.quiz import QuizConfig, build_quiz_config
from app.quiz_import import ImportResult, ImportRowError, import_quiz_csv
from app.templating import templates
from generators.registry import available_generators, get_generator

QUIZ_TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "templates" / "quiz_template.csv"
)

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


def _build_quiz_content(
    question: str,
    choice_1: str,
    choice_2: str,
    choice_3: str,
    choice_4: str,
    correct_choice: str,
    explanation: str,
) -> str:
    try:
        selected_raw_index = int(correct_choice)
    except ValueError:
        raise HTTPException(status_code=400, detail="Réponse correcte invalide.")

    config, error = build_quiz_config(
        question=question,
        choices=[choice_1, choice_2, choice_3, choice_4],
        correct_raw_index=selected_raw_index,
        explanation=explanation,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return config.to_json()


def _build_content(
    parsed_type: models.BlockType,
    content: str,
    generator: str,
    difficulty: int,
    count: int,
    tags: str,
    question: str,
    choice_1: str,
    choice_2: str,
    choice_3: str,
    choice_4: str,
    correct_choice: str,
    explanation: str,
) -> str:
    if parsed_type == models.BlockType.GENERATED_EXERCISE:
        if generator not in available_generators():
            raise HTTPException(status_code=400, detail="Générateur inconnu")
        config = ExerciseBlockConfig(
            generator=generator,
            difficulty=difficulty,
            count=max(1, count),
            tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
        )
        return config.to_json()

    if parsed_type == models.BlockType.QUIZ:
        return _build_quiz_content(
            question, choice_1, choice_2, choice_3, choice_4, correct_choice, explanation
        )

    return content


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
            "generators": available_generators(),
            "exercise_config": ExerciseBlockConfig(generator=""),
            "quiz_config": QuizConfig(question=""),
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
    generator: str = Form(""),
    difficulty: int = Form(1),
    count: int = Form(1),
    tags: str = Form(""),
    question: str = Form(""),
    choice_1: str = Form(""),
    choice_2: str = Form(""),
    choice_3: str = Form(""),
    choice_4: str = Form(""),
    correct_choice: str = Form("0"),
    explanation: str = Form(""),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    try:
        parsed_type = models.BlockType(block_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de bloc invalide")

    stored_content = _build_content(
        parsed_type,
        content,
        generator,
        difficulty,
        count,
        tags,
        question,
        choice_1,
        choice_2,
        choice_3,
        choice_4,
        correct_choice,
        explanation,
    )

    db.add(
        models.LessonBlock(
            uaa=uaa,
            title=title,
            type=parsed_type,
            content=stored_content,
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
    exercise_config = (
        ExerciseBlockConfig.from_json(block.content)
        if block.type == models.BlockType.GENERATED_EXERCISE
        else ExerciseBlockConfig(generator="")
    )
    quiz_config = (
        QuizConfig.from_json(block.content)
        if block.type == models.BlockType.QUIZ
        else QuizConfig(question="")
    )
    return templates.TemplateResponse(
        request=request,
        name="admin_block_form.html",
        context={
            "uaa": block.uaa,
            "block": block,
            "block_types": list(models.BlockType),
            "next_position": block.position,
            "generators": available_generators(),
            "exercise_config": exercise_config,
            "quiz_config": quiz_config,
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
    generator: str = Form(""),
    difficulty: int = Form(1),
    count: int = Form(1),
    tags: str = Form(""),
    question: str = Form(""),
    choice_1: str = Form(""),
    choice_2: str = Form(""),
    choice_3: str = Form(""),
    choice_4: str = Form(""),
    correct_choice: str = Form("0"),
    explanation: str = Form(""),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    block = db.get(models.LessonBlock, block_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Bloc introuvable")
    try:
        parsed_type = models.BlockType(block_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Type de bloc invalide")

    stored_content = _build_content(
        parsed_type,
        content,
        generator,
        difficulty,
        count,
        tags,
        question,
        choice_1,
        choice_2,
        choice_3,
        choice_4,
        correct_choice,
        explanation,
    )

    block.title = title
    block.type = parsed_type
    block.content = stored_content
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


@protected_router.get("/quiz", response_class=HTMLResponse)
async def admin_quiz_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin_quiz.html",
        context={"result": None},
    )


@protected_router.get("/quiz/template.csv")
async def admin_quiz_template() -> Response:
    content = QUIZ_TEMPLATE_PATH.read_text(encoding="utf-8")
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=quiz_template.csv"},
    )


@protected_router.post("/quiz/import", response_class=HTMLResponse)
async def admin_quiz_import(
    request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> HTMLResponse:
    raw_bytes = await file.read()
    try:
        csv_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        result = ImportResult(errors=[ImportRowError(0, "Le fichier doit être encodé en UTF-8.")])
    else:
        result = import_quiz_csv(csv_text, db)
    return templates.TemplateResponse(
        request=request,
        name="admin_quiz.html",
        context={"result": result},
    )


@protected_router.get("/generators", response_class=HTMLResponse)
async def admin_generators(
    request: Request,
    generator: str = "",
    difficulty: int = 1,
    seed: int | None = None,
) -> HTMLResponse:
    exercise = None
    error = None

    if generator:
        try:
            generator_fn = get_generator(generator)
        except KeyError:
            error = f"Générateur « {generator} » introuvable."
        else:
            exercise = generator_fn(difficulty=difficulty, seed=seed)

    return templates.TemplateResponse(
        request=request,
        name="admin_generators.html",
        context={
            "generators": available_generators(),
            "selected_generator": generator,
            "difficulty": difficulty,
            "seed": seed,
            "exercise": exercise,
            "error": error,
        },
    )


router = APIRouter()
router.include_router(public_router)
router.include_router(protected_router)

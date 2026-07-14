import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.answer_checking import parse_answer
from app.auth import require_admin, verify_credentials
from app.database import get_db
from app.exercise_blocks import ExerciseBlockConfig
from app.quiz import QuizConfig, build_quiz_config
from app.quiz_import import ImportResult, ImportRowError, import_quiz_csv
from app.slugify import slugify
from app.templating import templates
from app.value_table import check_value_table_answers, value_table_public_dict
from generators.exercise_types import InteractiveExercise
from generators.registry import available_generators, get_generator
from generators.value_table import ValueTableRow, build_value_table_exercise

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


def _clean_required_text(raw: str, *, field_label: str, max_length: int) -> str:
    value = raw.strip()
    if not value:
        raise HTTPException(status_code=400, detail=f"Le champ « {field_label} » est obligatoire.")
    if len(value) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Le champ « {field_label} » dépasse {max_length} caractères.",
        )
    return value


def _clean_slug(raw: str, fallback_source: str) -> str:
    value = (raw or "").strip() or slugify(fallback_source)
    if not value:
        raise HTTPException(status_code=400, detail="Impossible de générer un slug non vide.")
    if len(value) > 120:
        raise HTTPException(status_code=400, detail="Le slug dépasse 120 caractères.")
    return value


def _ensure_unique(
    db: Session,
    model: type,
    field,
    value: str,
    *,
    field_label: str,
    exclude_id: int | None = None,
) -> None:
    query = db.query(model).filter(field == value)
    if exclude_id is not None:
        query = query.filter(model.id != exclude_id)
    if query.first() is not None:
        raise HTTPException(status_code=400, detail=f"{field_label} « {value} » est déjà utilisé(e).")


@protected_router.get("/subjects", response_class=HTMLResponse)
async def admin_list_subjects(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    subjects = db.query(models.Subject).order_by(models.Subject.name).all()
    summaries = [
        {
            "subject": subject,
            "module_count": len(subject.modules),
            "uaa_count": sum(len(module.uaas) for module in subject.modules),
            "block_count": sum(
                len(uaa.lesson_blocks) for module in subject.modules for uaa in module.uaas
            ),
        }
        for subject in subjects
    ]
    return templates.TemplateResponse(
        request=request,
        name="admin_subjects.html",
        context={"summaries": summaries},
    )


@protected_router.get("/subjects/new", response_class=HTMLResponse)
async def admin_new_subject_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin_subject_form.html",
        context={"subject": None},
    )


@protected_router.post("/subjects/new")
async def admin_create_subject(
    name: str = Form(...), slug: str = Form(""), db: Session = Depends(get_db)
) -> RedirectResponse:
    clean_name = _clean_required_text(name, field_label="Nom", max_length=100)
    clean_slug = _clean_slug(slug, clean_name)
    _ensure_unique(db, models.Subject, models.Subject.name, clean_name, field_label="Ce nom")
    _ensure_unique(db, models.Subject, models.Subject.slug, clean_slug, field_label="Ce slug")

    subject = models.Subject(name=clean_name, slug=clean_slug)
    db.add(subject)
    db.commit()
    return RedirectResponse(url="/admin/subjects", status_code=303)


@protected_router.get("/subjects/{subject_id}", response_class=HTMLResponse)
async def admin_subject_modules(
    subject_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    summaries = [
        {
            "module": module,
            "uaa_count": len(module.uaas),
            "block_count": sum(len(uaa.lesson_blocks) for uaa in module.uaas),
        }
        for module in subject.modules
    ]
    return templates.TemplateResponse(
        request=request,
        name="admin_modules.html",
        context={"subject": subject, "summaries": summaries},
    )


@protected_router.get("/subjects/{subject_id}/edit", response_class=HTMLResponse)
async def admin_edit_subject_form(
    subject_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_subject_form.html",
        context={"subject": subject},
    )


@protected_router.post("/subjects/{subject_id}/edit")
async def admin_update_subject(
    subject_id: int, name: str = Form(...), slug: str = Form(""), db: Session = Depends(get_db)
) -> RedirectResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")

    clean_name = _clean_required_text(name, field_label="Nom", max_length=100)
    clean_slug = _clean_slug(slug, clean_name)
    _ensure_unique(
        db, models.Subject, models.Subject.name, clean_name,
        field_label="Ce nom", exclude_id=subject_id,
    )
    _ensure_unique(
        db, models.Subject, models.Subject.slug, clean_slug,
        field_label="Ce slug", exclude_id=subject_id,
    )

    subject.name = clean_name
    subject.slug = clean_slug
    db.commit()
    return RedirectResponse(url=f"/admin/subjects/{subject_id}", status_code=303)


@protected_router.post("/subjects/{subject_id}/delete")
async def admin_delete_subject(subject_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    db.delete(subject)
    db.commit()
    return RedirectResponse(url="/admin/subjects", status_code=303)


@protected_router.get("/subjects/{subject_id}/modules/new", response_class=HTMLResponse)
async def admin_new_module_form(
    subject_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_module_form.html",
        context={"subject": subject, "module": None},
    )


@protected_router.post("/subjects/{subject_id}/modules/new")
async def admin_create_module(
    subject_id: int, code: str = Form(...), slug: str = Form(""), db: Session = Depends(get_db)
) -> RedirectResponse:
    subject = db.get(models.Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")

    clean_code = _clean_required_text(code, field_label="Code", max_length=20)
    clean_slug = _clean_slug(slug, clean_code)
    _ensure_unique(db, models.Module, models.Module.slug, clean_slug, field_label="Ce slug")

    module = models.Module(code=clean_code, slug=clean_slug, subject=subject)
    db.add(module)
    db.commit()
    return RedirectResponse(url=f"/admin/subjects/{subject_id}", status_code=303)


@protected_router.get("/modules/{module_id}", response_class=HTMLResponse)
async def admin_module_uaas(
    module_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    summaries = [{"uaa": uaa, "block_count": len(uaa.lesson_blocks)} for uaa in module.uaas]
    return templates.TemplateResponse(
        request=request,
        name="admin_uaa_list.html",
        context={"module": module, "summaries": summaries},
    )


@protected_router.get("/modules/{module_id}/edit", response_class=HTMLResponse)
async def admin_edit_module_form(
    module_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_module_form.html",
        context={"subject": module.subject, "module": module},
    )


@protected_router.post("/modules/{module_id}/edit")
async def admin_update_module(
    module_id: int, code: str = Form(...), slug: str = Form(""), db: Session = Depends(get_db)
) -> RedirectResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")

    clean_code = _clean_required_text(code, field_label="Code", max_length=20)
    clean_slug = _clean_slug(slug, clean_code)
    _ensure_unique(
        db, models.Module, models.Module.slug, clean_slug,
        field_label="Ce slug", exclude_id=module_id,
    )

    module.code = clean_code
    module.slug = clean_slug
    db.commit()
    return RedirectResponse(url=f"/admin/modules/{module_id}", status_code=303)


@protected_router.post("/modules/{module_id}/delete")
async def admin_delete_module(module_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    subject_id = module.subject_id
    db.delete(module)
    db.commit()
    return RedirectResponse(url=f"/admin/subjects/{subject_id}", status_code=303)


@protected_router.get("/modules/{module_id}/uaa/new", response_class=HTMLResponse)
async def admin_new_uaa_form(
    module_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    next_position = max((uaa.position for uaa in module.uaas), default=0) + 1
    return templates.TemplateResponse(
        request=request,
        name="admin_uaa_form.html",
        context={"module": module, "uaa": None, "next_position": next_position},
    )


@protected_router.post("/modules/{module_id}/uaa/new")
async def admin_create_uaa(
    module_id: int,
    code: str = Form(...),
    title: str = Form(...),
    slug: str = Form(""),
    position: int = Form(0),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    module = db.get(models.Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable")

    clean_code = _clean_required_text(code, field_label="Code", max_length=20)
    clean_title = _clean_required_text(title, field_label="Titre", max_length=150)
    clean_slug = _clean_slug(slug, f"{module.code}-{clean_code}")
    _ensure_unique(db, models.UAA, models.UAA.slug, clean_slug, field_label="Ce slug")

    uaa = models.UAA(
        code=clean_code,
        title=clean_title,
        slug=clean_slug,
        position=position,
        is_published=is_published,
        module=module,
    )
    db.add(uaa)
    db.commit()
    return RedirectResponse(url=f"/admin/modules/{module_id}", status_code=303)


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


@protected_router.get("/uaa/{uaa_id}/edit", response_class=HTMLResponse)
async def admin_edit_uaa_form(
    uaa_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    return templates.TemplateResponse(
        request=request,
        name="admin_uaa_form.html",
        context={"module": uaa.module, "uaa": uaa, "next_position": uaa.position},
    )


@protected_router.post("/uaa/{uaa_id}/edit")
async def admin_update_uaa(
    uaa_id: int,
    code: str = Form(...),
    title: str = Form(...),
    slug: str = Form(""),
    position: int = Form(0),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")

    clean_code = _clean_required_text(code, field_label="Code", max_length=20)
    clean_title = _clean_required_text(title, field_label="Titre", max_length=150)
    clean_slug = _clean_slug(slug, f"{uaa.module.code}-{clean_code}")
    _ensure_unique(
        db, models.UAA, models.UAA.slug, clean_slug,
        field_label="Ce slug", exclude_id=uaa_id,
    )

    uaa.code = clean_code
    uaa.title = clean_title
    uaa.slug = clean_slug
    uaa.position = position
    uaa.is_published = is_published
    db.commit()
    return RedirectResponse(url=f"/admin/uaa/{uaa_id}", status_code=303)


@protected_router.post("/uaa/{uaa_id}/delete")
async def admin_delete_uaa(uaa_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    uaa = db.get(models.UAA, uaa_id)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")
    module_id = uaa.module_id
    db.delete(uaa)
    db.commit()
    return RedirectResponse(url=f"/admin/modules/{module_id}", status_code=303)


def _build_quiz_content(
    question: str,
    choice_1: str,
    choice_2: str,
    choice_3: str,
    choice_4: str,
    correct_choice: str,
    explanation: str,
    answer_type: str,
    correct_value: str,
    group: str,
    order_in_group: int,
) -> str:
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La question est obligatoire.")

    if answer_type == "numeric":
        if parse_answer(correct_value) is None:
            raise HTTPException(
                status_code=400, detail="La réponse numérique correcte est invalide."
            )
        config = QuizConfig(
            question=question,
            answer_type="numeric",
            correct_value=correct_value.strip(),
            explanation=explanation.strip(),
            group=group.strip(),
            order_in_group=order_in_group,
        )
        return config.to_json()

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
    config.group = group.strip()
    config.order_in_group = order_in_group
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
    answer_type: str,
    correct_value: str,
    group: str,
    order_in_group: int,
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
            question,
            choice_1,
            choice_2,
            choice_3,
            choice_4,
            correct_choice,
            explanation,
            answer_type,
            correct_value,
            group,
            order_in_group,
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
    answer_type: str = Form("choice"),
    correct_value: str = Form(""),
    quiz_group: str = Form(""),
    order_in_group: int = Form(0),
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
        answer_type,
        correct_value,
        quiz_group,
        order_in_group,
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
    answer_type: str = Form("choice"),
    correct_value: str = Form(""),
    quiz_group: str = Form(""),
    order_in_group: int = Form(0),
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
        answer_type,
        correct_value,
        quiz_group,
        order_in_group,
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
    exercise_json = None
    error = None

    if generator:
        try:
            generator_fn = get_generator(generator)
        except KeyError:
            error = f"Générateur « {generator} » introuvable."
        else:
            exercise = generator_fn(difficulty=difficulty, seed=seed)
            if isinstance(exercise, InteractiveExercise) and exercise.type == "value_table":
                exercise_json = json.dumps(value_table_public_dict(exercise), ensure_ascii=False)

    return templates.TemplateResponse(
        request=request,
        name="admin_generators.html",
        context={
            "generators": available_generators(),
            "selected_generator": generator,
            "difficulty": difficulty,
            "seed": seed,
            "exercise": exercise,
            "exercise_json": exercise_json,
            "error": error,
        },
    )


def _value_table_demo_exercise():
    """Exercice fixe de démonstration pour le composant `value_table` (docs/EXERCISE_TYPES.md).

    Aucun générateur réel n'y est associé pour le moment (voir docs/ROADMAP.md, VS003) :
    cette fonction sert uniquement à tester l'architecture du composant (rendu, saisie,
    vérification cellule par cellule, correction) de bout en bout, sans modifier les
    générateurs existants.
    """
    return build_value_table_exercise(
        question="Complète le tableau de valeurs de f(x) = 2x + 1.",
        columns=[-2, 0, 3],
        rows=[
            ValueTableRow(label="2x", values=[-4, 0, 6], editable=[False, False, False]),
            ValueTableRow(label="f(x) = 2x + 1", editable=[True, True, True]),
        ],
        answer_cells=[-3, 1, 7],
        hint="Ajoute 1 à la valeur de la ligne « 2x ».",
        explanation="f(x) = 2x + 1 : on multiplie x par 2 (ligne « 2x »), puis on ajoute 1.",
    )


class ValueTableVerifyRequest(BaseModel):
    answers: list[str]


@protected_router.get("/value-table-demo", response_class=HTMLResponse)
async def admin_value_table_demo(request: Request) -> HTMLResponse:
    exercise = _value_table_demo_exercise()
    return templates.TemplateResponse(
        request=request,
        name="admin_value_table_demo.html",
        context={"exercise_json": json.dumps(value_table_public_dict(exercise), ensure_ascii=False)},
    )


@protected_router.post("/value-table-demo/verify")
async def admin_value_table_demo_verify(payload: ValueTableVerifyRequest) -> JSONResponse:
    exercise = _value_table_demo_exercise()
    try:
        correction = check_value_table_answers(exercise, payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return JSONResponse(correction.to_dict())


router = APIRouter()
router.include_router(public_router)
router.include_router(protected_router)

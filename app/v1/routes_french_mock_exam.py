"""Routes — Examen blanc CESS Français (chantier prioritaire, mode Examen blanc).

Même discipline async que #88/#90/#92 : `POST .../start` et `POST .../submit` ne font
JAMAIS d'appel IA dans le cycle requête/réponse — ils créent/font avancer la ligne
`FrenchMockExam` (PENDING/SUBMITTED) et redirigent immédiatement vers une page d'attente
qui interroge le worker en polling (voir `app.v1.correction_worker`,
`app.v1.french_mock_exam_service`)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

from app.database import get_db
from app.templating import templates
from app.v1.auth import require_user, require_user_api
from app.v1.francais_plan import FRANCAIS_PLAN_BY_CODE
from app.v1.french_mock_exam_service import (
    MockExamNotReadyError,
    MockExamNotRetryableError,
    get_mock_exam,
    retry_mock_exam_build,
    retry_mock_exam_correction,
    save_mock_exam_answer,
    start_mock_exam,
    submit_mock_exam,
)
from app.v1.models import FrenchMockExam, FrenchMockExamStatus, User

router = APIRouter(tags=["v1-french-mock-exam"])

_MODE_LABELS = {
    "surprise": "Examen blanc CESS — Surprise",
    "synthesis": "Entraînement ciblé — Synthèse",
    "argumentation": "Entraînement ciblé — Argumentation",
}

_EXAM_TYPE_LABELS = {
    "synthesis": "Synthèse",
    "argumentation_opinion": "Argumentation — réaction à une opinion",
    "argumentation_request": "Argumentation — réclamation/demande",
}

# § 43 du chantier : mapping cours à relire, uniquement les cours PUBLIQUEMENT livrés
# (FR08/FR09/FR10 — ticket #94 PHASE B) sont liés ; FR11-14 préparés mais jamais liés
# tant qu'ils ne sont pas livrés (pas de lien mort).
_RELATED_COURSES_BY_EXAM_TYPE = {
    "synthesis": ["FR08", "FR09"],
    "argumentation_opinion": ["FR10"],
    "argumentation_request": ["FR10"],
}


def _owned_exam(db, *, exam_id: int, user_id: int) -> FrenchMockExam | None:
    exam = get_mock_exam(db, exam_id=exam_id)
    if exam is None or exam.user_id != user_id:
        return None
    return exam


# =============================================================================================
# Landing + démarrage (§ 1, § 2, § 31)
# =============================================================================================


@router.get("/francais/examen-blanc", response_class=HTMLResponse)
async def mock_exam_landing(
    request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="v1_mock_exam_landing.html", context={},
    )


@router.post("/francais/examen-blanc/start")
async def mock_exam_start(
    request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> RedirectResponse:
    form = await request.form()
    mode = str(form.get("mode", "surprise"))
    if mode not in _MODE_LABELS:
        raise HTTPException(status_code=422, detail="Mode d'examen blanc inconnu.")
    exam = start_mock_exam(db, user=user, mode=mode)
    return RedirectResponse(url=f"/francais/examen-blanc/{exam.id}", status_code=303)


# =============================================================================================
# Dossier / rédaction / attente (§ 31, § 32, § 33)
# =============================================================================================


@router.get("/francais/examen-blanc/{exam_id}", response_class=HTMLResponse)
async def mock_exam_view(
    exam_id: int, request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")

    if exam.status in (FrenchMockExamStatus.PENDING, FrenchMockExamStatus.BUILDING, FrenchMockExamStatus.BUILD_FAILED):
        return templates.TemplateResponse(
            request=request,
            name="v1_mock_exam_build_waiting.html",
            context={"exam": exam, "mode_label": _MODE_LABELS.get("surprise" if exam.surprise_mode else "synthesis")},
        )

    if exam.status == FrenchMockExamStatus.READY:
        word_count = len((exam.answer_text or "").split())
        return templates.TemplateResponse(
            request=request,
            name="v1_mock_exam_write.html",
            context={
                "exam": exam,
                "exam_type_label": _EXAM_TYPE_LABELS[exam.exam_type.value],
                "word_count": word_count,
            },
        )

    if exam.status in (FrenchMockExamStatus.SUBMITTED, FrenchMockExamStatus.CORRECTING):
        return templates.TemplateResponse(
            request=request, name="v1_mock_exam_correcting.html", context={"exam": exam},
        )

    # COMPLETED / CORRECTION_INCOMPLETE.
    related_codes = _RELATED_COURSES_BY_EXAM_TYPE.get(exam.exam_type.value, [])
    related_courses = [
        {"code": code, "title": FRANCAIS_PLAN_BY_CODE[code].title, "slug": FRANCAIS_PLAN_BY_CODE[code].slug}
        for code in related_codes
        if code in FRANCAIS_PLAN_BY_CODE
    ]
    return templates.TemplateResponse(
        request=request,
        name="v1_mock_exam_results.html",
        context={
            "exam": exam,
            "exam_type_label": _EXAM_TYPE_LABELS[exam.exam_type.value],
            "related_courses": related_courses,
            "word_count": len((exam.answer_text or "").split()),
        },
    )


@router.get("/francais/examen-blanc/{exam_id}/status")
async def mock_exam_build_status(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user_api)  # noqa: B008
) -> dict:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    status_map = {
        FrenchMockExamStatus.PENDING: "pending",
        FrenchMockExamStatus.BUILDING: "pending",
        FrenchMockExamStatus.BUILD_FAILED: "failed",
        FrenchMockExamStatus.READY: "ready",
    }
    return {
        "status": status_map.get(exam.status, "pending"),
        "error_message": exam.error_message,
        "exam_url": f"/francais/examen-blanc/{exam.id}",
    }


@router.post("/francais/examen-blanc/{exam_id}/retry-build")
async def mock_exam_retry_build(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> RedirectResponse:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    try:
        retry_mock_exam_build(db, exam=exam)
    except MockExamNotRetryableError:
        pass
    return RedirectResponse(url=f"/francais/examen-blanc/{exam.id}", status_code=303)


# =============================================================================================
# Autosave (§ 33) — même contrat que l'API d'autosave existante (#42/#62)
# =============================================================================================


@router.post("/api/v1/mock-exams/{exam_id}/answer")
async def mock_exam_autosave(
    exam_id: int, request: Request, db=Depends(get_db), user: User = Depends(require_user_api)  # noqa: B008
):
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    payload = await request.json()
    answer_text = payload.get("answer_text")
    preparation_table_json = payload.get("preparation_table_json")
    try:
        save_mock_exam_answer(
            db, exam=exam, answer_text=answer_text, preparation_table_json=preparation_table_json,
        )
    except MockExamNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"saved": True, "word_count": len((exam.answer_text or "").split())}


# =============================================================================================
# Soumission / correction asynchrone (§ 35, § 37)
# =============================================================================================


@router.post("/francais/examen-blanc/{exam_id}/submit")
async def mock_exam_submit(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> RedirectResponse:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    submit_mock_exam(db, exam=exam)
    return RedirectResponse(url=f"/francais/examen-blanc/{exam.id}", status_code=303)


@router.get("/francais/examen-blanc/{exam_id}/correction-status")
async def mock_exam_correction_status(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user_api)  # noqa: B008
) -> dict:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    status_map = {
        FrenchMockExamStatus.SUBMITTED: "pending",
        FrenchMockExamStatus.CORRECTING: "pending",
        FrenchMockExamStatus.COMPLETED: "completed",
        FrenchMockExamStatus.CORRECTION_INCOMPLETE: "incomplete",
    }
    return {"status": status_map.get(exam.status, "pending"), "error_message": exam.error_message}


@router.post("/francais/examen-blanc/{exam_id}/retry-correction")
async def mock_exam_retry_correction(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> RedirectResponse:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    try:
        retry_mock_exam_correction(db, exam=exam)
    except MockExamNotRetryableError:
        pass
    return RedirectResponse(url=f"/francais/examen-blanc/{exam.id}", status_code=303)


# =============================================================================================
# Export / print (§ 44)
# =============================================================================================


def _build_mock_exam_export_markdown(exam: FrenchMockExam) -> str:
    lines = [
        "# Examen blanc CESS Français — export",
        "",
        f"**Type :** {_EXAM_TYPE_LABELS.get(exam.exam_type.value, exam.exam_type.value)}",
        f"**Thème :** {exam.theme}",
        f"**Statut :** {exam.status.value}",
        "",
    ]
    if exam.status == FrenchMockExamStatus.CORRECTION_INCOMPLETE:
        lines += ["**CORRECTION INCOMPLÈTE** — la correction IA n'a pas pu aboutir, score non définitif.", ""]

    lines.append("## Portefeuille de documents")
    for i, doc in enumerate(exam.documents, start=1):
        lines += [f"### Document {i} — {doc.title}", "", doc.content_text or "", ""]

    lines += ["## Consigne", "", exam.task_prompt or "", ""]
    lines += ["## Production", "", exam.answer_text or "", ""]

    if exam.status == FrenchMockExamStatus.COMPLETED and exam.score is not None:
        lines += [f"## Score : {exam.score:.0f} / {exam.max_score:.0f}", ""]
        feedback = exam.feedback_json or {}
        for category in feedback.get("category_scores") or []:
            lines.append(f"- {category['name']} : {category['points']}/{category['max_points']} — {category.get('comment', '')}")
        lines.append("")
        for key, label in (
            ("strengths", "Points forts"), ("improvements", "À améliorer"),
            ("structure_feedback", "Structure"), ("document_comprehension_feedback", "Compréhension des documents"),
            ("source_usage_feedback", "Utilisation des sources"), ("task_specific_feedback", "Retour spécifique"),
            ("language_feedback", "Langue"), ("length_feedback", "Longueur"),
        ):
            value = feedback.get(key)
            if isinstance(value, list):
                if value:
                    lines.append(f"## {label}")
                    lines += [f"- {item}" for item in value]
                    lines.append("")
            elif value:
                lines += [f"## {label}", "", str(value), ""]

    return "\n".join(lines)


@router.get("/francais/examen-blanc/{exam_id}/export.md")
async def mock_exam_export_markdown(
    exam_id: int, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> PlainTextResponse:
    exam = _owned_exam(db, exam_id=exam_id, user_id=user.id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Examen blanc introuvable")
    if exam.status not in (FrenchMockExamStatus.COMPLETED, FrenchMockExamStatus.CORRECTION_INCOMPLETE):
        raise HTTPException(status_code=409, detail="Export disponible uniquement après soumission.")
    content = _build_mock_exam_export_markdown(exam)
    return PlainTextResponse(content, media_type="text/markdown")

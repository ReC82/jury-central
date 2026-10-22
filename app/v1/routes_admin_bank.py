"""Routes de l'administration de la banque de questions V1 (ticket #46) — `/admin/bank…`,
protégées comme tout `/admin/*` (`app.auth.require_admin`). Logique dans
`app.v1.bank_admin` ; aucune route de suppression."""

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.ai.factory import get_ai_provider
from app.ai.provider import AINotConfiguredError
from app.auth import require_admin
from app.database import get_db
from app.models import UAA, Module
from app.templating import templates
from app.v1.assets import (
    VISUAL_TYPE_LABELS,
    asset_display,
    asset_metadata,
    asset_visual_type,
    assets_for_version,
    can_regenerate,
    mark_asset_incorrect,
    questions_using_asset,
    reactivate_asset,
    version_usage_count,
)
from app.v1.auth import validate_csrf_token
from app.v1.bank_admin import (
    SOURCE_LABELS,
    STATUS_LABELS,
    BankAdminError,
    QuestionFilters,
    distinct_question_types,
    edit_question_content,
    module_bank_stats,
    question_feedback,
    question_versions,
    regenerate_variant,
    search_questions,
    set_question_status,
    unresolved_feedback_counts,
    usage_without_module,
    variant_unavailable_reason,
    version_usage_counts,
)
from app.v1.feedback import FEEDBACK_LABELS, resolve_feedback
from app.v1.generation_control import get_generation_status, set_generation_status
from app.v1.models import Asset, ContentStatus, ModuleGenerationStatus, Question, QuestionFeedback

router = APIRouter(prefix="/admin/bank", tags=["admin-bank"], dependencies=[Depends(require_admin)])

_DONE_MESSAGES = {
    "edited": "Nouvelle version créée : elle est désormais la version courante.",
    "status": "Statut mis à jour.",
    "variant": "Variante créée au statut « À revoir » : vérifie-la puis active-la.",
    "feedback": "Signalement mis à jour.",
    "asset_flagged": "Visuel marqué incorrect : les questions qui l'utilisent ne sont plus proposées.",
    "asset_reactivated": "Visuel réactivé : les questions qui l'utilisent sont de nouveau proposées.",
}


def _check_csrf(request: Request, token: str) -> None:
    if not validate_csrf_token(request, token):
        raise HTTPException(status_code=400, detail="Session expirée, recharge la page.")


def _optional_int(raw: str | None) -> int | None:
    return int(raw) if raw and raw.strip().lstrip("-").isdigit() else None


def _optional_float(raw: str | None) -> float | None:
    try:
        return float(raw) if raw not in (None, "") else None
    except ValueError:
        return None


@router.get("", response_class=HTMLResponse)
async def bank_overview(request: Request, db=Depends(get_db)) -> HTMLResponse:  # noqa: B008
    return templates.TemplateResponse(
        request=request,
        name="admin_bank.html",
        context={
            "stats": module_bank_stats(db),
            "usage_without_module": usage_without_module(db),
            "status_labels": STATUS_LABELS,
            "statuses": list(ContentStatus),
        },
    )


@router.post("/modules/{module_id}/generation")
async def bank_set_generation(
    module_id: int,
    request: Request,
    generation_status: str = Form(...),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    _check_csrf(request, csrf_token)
    if db.get(Module, module_id) is None:
        raise HTTPException(status_code=404, detail="Module introuvable")
    try:
        status = ModuleGenerationStatus(generation_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Statut de génération inconnu") from exc
    set_generation_status(db, module_id, status)
    db.commit()
    return RedirectResponse(url="/admin/bank", status_code=303)


@router.get("/questions", response_class=HTMLResponse)
async def bank_questions(
    request: Request,
    module_id: str | None = None,
    uaa_id: str | None = None,
    question_type: str | None = None,
    status: str | None = None,
    rating_min: str | None = None,
    rating_max: str | None = None,
    q: str | None = None,
    to_review: str | None = None,
    page: int = 1,
    db=Depends(get_db),  # noqa: B008
) -> HTMLResponse:
    try:
        parsed_status = ContentStatus(status) if status else None
    except ValueError:
        parsed_status = None
    filters = QuestionFilters(
        module_id=_optional_int(module_id),
        uaa_id=_optional_int(uaa_id),
        question_type=question_type or None,
        status=parsed_status,
        rating_min=_optional_float(rating_min),
        rating_max=_optional_float(rating_max),
        text=(q or "").strip() or None,
        to_review=bool(to_review),
        page=max(1, page),
    )
    items, total = search_questions(db, filters)
    modules = db.query(Module).order_by(Module.code).all()
    uaas = (
        db.query(UAA).filter_by(module_id=filters.module_id).order_by(UAA.code).all()
        if filters.module_id is not None
        else []
    )
    query_params = {
        key: value
        for key, value in {
            "module_id": module_id, "uaa_id": uaa_id, "question_type": question_type, "status": status,
            "rating_min": rating_min, "rating_max": rating_max, "q": q, "to_review": to_review,
        }.items()
        if value
    }
    page_count = max(1, (total + filters.per_page - 1) // filters.per_page)
    return templates.TemplateResponse(
        request=request,
        name="admin_bank_questions.html",
        context={
            "items": items,
            "total": total,
            "filters": filters,
            "modules": modules,
            "uaas": uaas,
            "question_types": distinct_question_types(db),
            "status_labels": STATUS_LABELS,
            "statuses": list(ContentStatus),
            "feedback_counts": unresolved_feedback_counts(db, [item.id for item in items]),
            "query_params": query_params,
            "page_count": page_count,
        },
    )


def _render_question(request: Request, db, question: Question, *, error: str | None = None,
                     draft: str | None = None, status_code: int = 200) -> HTMLResponse:
    current = question.current_version
    done = request.query_params.get("done")
    return templates.TemplateResponse(
        request=request,
        name="admin_bank_question.html",
        context={
            "question": question,
            "versions": question_versions(db, question),
            "version_usage": version_usage_counts(db, question),
            "feedback": question_feedback(db, question),
            "feedback_labels": FEEDBACK_LABELS,
            "status_labels": STATUS_LABELS,
            "source_labels": SOURCE_LABELS,
            "statuses": list(ContentStatus),
            "generation_status": get_generation_status(db, question.module_id),
            "variant_unavailable": variant_unavailable_reason(db, question),
            "content_draft": draft
            if draft is not None
            else json.dumps(current.content_json if current else {}, ensure_ascii=False, indent=2),
            "error": error,
            "message": _DONE_MESSAGES.get(done) if done else None,
            "variant_id": _optional_int(request.query_params.get("variant")),
            "assets": [_asset_row(db, asset) for asset in assets_for_version(db, current.id)] if current else [],
        },
        status_code=status_code,
    )


def _asset_row(db, asset: Asset) -> dict:
    """Ticket #48 : vue admin d'un visuel (statut, provenance, réutilisation)."""
    metadata = asset_metadata(asset)
    return {
        "asset": asset,
        "display": asset_display(asset),
        "metadata": metadata,
        "visual_type_label": VISUAL_TYPE_LABELS.get(asset_visual_type(asset), "—"),
        "version_count": version_usage_count(db, asset),
        "questions": questions_using_asset(db, asset),
        "can_regenerate": can_regenerate(asset),
    }


def _get_question(db, question_id: int) -> Question:
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question introuvable")
    return question


@router.get("/questions/{question_id}", response_class=HTMLResponse)
async def bank_question_detail(question_id: int, request: Request, db=Depends(get_db)) -> HTMLResponse:  # noqa: B008
    return _render_question(request, db, _get_question(db, question_id))


@router.post("/questions/{question_id}/edit", response_class=HTMLResponse)
async def bank_question_edit(
    question_id: int,
    request: Request,
    content_json: str = Form(...),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
):
    _check_csrf(request, csrf_token)
    question = _get_question(db, question_id)
    try:
        edit_question_content(db, question, content_json)
    except BankAdminError as exc:
        db.rollback()
        return _render_question(request, db, question, error=str(exc), draft=content_json, status_code=400)
    db.commit()
    return RedirectResponse(url=f"/admin/bank/questions/{question_id}?done=edited", status_code=303)


@router.post("/questions/{question_id}/status")
async def bank_question_status(
    question_id: int,
    request: Request,
    status: str = Form(...),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    _check_csrf(request, csrf_token)
    question = _get_question(db, question_id)
    try:
        parsed = ContentStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Statut inconnu") from exc
    set_question_status(db, question, parsed)
    db.commit()
    return RedirectResponse(url=f"/admin/bank/questions/{question_id}?done=status", status_code=303)


@router.post("/questions/{question_id}/variant", response_class=HTMLResponse)
async def bank_question_variant(
    question_id: int,
    request: Request,
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
):
    _check_csrf(request, csrf_token)
    question = _get_question(db, question_id)
    try:
        provider = get_ai_provider()
    except AINotConfiguredError:
        return _render_question(request, db, question, error="Génération IA non configurée sur ce serveur.",
                                status_code=503)
    try:
        variant = regenerate_variant(db, question, provider)
    except BankAdminError as exc:
        # L'usage IA éventuellement consommé reste enregistré.
        db.commit()
        return _render_question(request, db, question, error=str(exc), status_code=400)
    db.commit()
    return RedirectResponse(
        url=f"/admin/bank/questions/{question_id}?done=variant&variant={variant.id}", status_code=303
    )


@router.get("/feedback", response_class=HTMLResponse)
async def bank_feedback(request: Request, show: str = "open", db=Depends(get_db)) -> HTMLResponse:  # noqa: B008
    query = db.query(QuestionFeedback)
    if show != "all":
        query = query.filter(QuestionFeedback.resolved_at.is_(None))
    items = query.order_by(QuestionFeedback.created_at.desc()).limit(200).all()
    questions = {
        q.id: q for q in db.query(Question).filter(Question.id.in_({f.question_id for f in items})).all()
    } if items else {}
    return templates.TemplateResponse(
        request=request,
        name="admin_bank_feedback.html",
        context={
            "items": items,
            "questions": questions,
            "show": show,
            "feedback_labels": FEEDBACK_LABELS,
            "status_labels": STATUS_LABELS,
        },
    )


@router.post("/feedback/{feedback_id}/resolve")
async def bank_feedback_resolve(
    feedback_id: int,
    request: Request,
    resolved: str = Form("1"),
    next: str = Form(""),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    _check_csrf(request, csrf_token)
    feedback = db.get(QuestionFeedback, feedback_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Signalement introuvable")
    resolve_feedback(db, feedback, resolved=resolved == "1")
    db.commit()
    target = (
        f"/admin/bank/questions/{feedback.question_id}?done=feedback"
        if next == "question"
        else "/admin/bank/feedback"
    )
    return RedirectResponse(url=target, status_code=303)


# --- Visuels (ticket #48) -------------------------------------------------------------------------


@router.get("/assets", response_class=HTMLResponse)
async def bank_assets(request: Request, db=Depends(get_db)) -> HTMLResponse:  # noqa: B008
    assets = db.query(Asset).order_by(Asset.id).all()
    done = request.query_params.get("done")
    return templates.TemplateResponse(
        request=request,
        name="admin_bank_assets.html",
        context={
            "rows": [_asset_row(db, asset) for asset in assets],
            "status_labels": STATUS_LABELS,
            "message": _DONE_MESSAGES.get(done) if done else None,
        },
    )


def _get_asset(db, asset_id: int) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Visuel introuvable")
    return asset


def _asset_redirect(next_question: str, done: str) -> RedirectResponse:
    question_id = _optional_int(next_question)
    target = f"/admin/bank/questions/{question_id}" if question_id else "/admin/bank/assets"
    return RedirectResponse(url=f"{target}?done={done}", status_code=303)


@router.post("/assets/{asset_id}/flag")
async def bank_asset_flag(
    asset_id: int,
    request: Request,
    reason: str = Form(""),
    request_regeneration: str = Form(""),
    next_question: str = Form(""),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    _check_csrf(request, csrf_token)
    asset = _get_asset(db, asset_id)
    mark_asset_incorrect(db, asset, reason=reason, request_regeneration=request_regeneration == "1")
    db.commit()
    return _asset_redirect(next_question, "asset_flagged")


@router.post("/assets/{asset_id}/reactivate")
async def bank_asset_reactivate(
    asset_id: int,
    request: Request,
    next_question: str = Form(""),
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
) -> RedirectResponse:
    _check_csrf(request, csrf_token)
    asset = _get_asset(db, asset_id)
    reactivate_asset(db, asset)
    db.commit()
    return _asset_redirect(next_question, "asset_reactivated")

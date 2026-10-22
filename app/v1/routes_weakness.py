"""Routes « Mes points faibles » (ticket #75) : profil, renforcement ciblé question par
question avec correction immédiate, et examen ciblé. Toute la logique est dans
`app.v1.weakness` ; la saisie et la correction d'une réponse réutilisent celles du quiz
(`app.v1.quiz_service`). Un compte est requis."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import models
from app.database import get_db
from app.templating import templates
from app.v1.auth import require_user, validate_csrf_token
from app.v1.models import SessionStatus, User
from app.v1.quiz_service import (
    TYPE_LABELS,
    IncompleteAnswerError,
    current_position,
    feedback_view,
    incomplete_answer_echo,
    is_validated,
    ordered_questions,
    parse_quiz_answer,
)
from app.v1.session_service import build_question_display
from app.v1.weakness import (
    LEVELS,
    WEAKNESS_EXAM_LENGTHS,
    WeaknessError,
    active_weaknesses,
    available_reinforcement_counts,
    get_owned_reinforcement,
    in_progress_reinforcements,
    in_progress_weakness_exam,
    recent_reinforcements,
    reinforcement_params,
    reinforcement_summary,
    resolve_targets,
    start_reinforcement,
    start_weakness_exam,
    validate_reinforcement_answer,
    weakness_profile,
)

router = APIRouter(tags=["v1-weakness"])

TREND_LABELS = {
    "nouveau": ("bi-dot", "Première série"),
    "amelioration": ("bi-arrow-down-right", "S'améliore"),
    "stable": ("bi-arrow-right", "Stable"),
    "degradation": ("bi-arrow-up-right", "Se dégrade"),
}
LEVEL_PILLS = {
    "prioritaire": ("jc-pill-danger", "bi-exclamation-octagon-fill"),
    "fragile": ("jc-pill-warn", "bi-exclamation-triangle-fill"),
    "a_consolider": ("jc-pill-primary", "bi-hourglass-split"),
    "fort": ("jc-pill-success", "bi-check-circle-fill"),
}


@router.get("/points-faibles", response_class=HTMLResponse)
async def weakness_home(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    entries = weakness_profile(db, user_id=user.id)
    groups: dict[int, dict] = {}
    for entry in entries:
        module = entry.module
        group = groups.setdefault(
            module.id,
            {"module": module, "subject": module.subject.name if module.subject else module.code,
             "entries": [], "active": 0, "exam_in_progress": None},
        )
        group["entries"].append(entry)
        group["active"] += int(entry.active)
    for group in groups.values():
        group["exam_in_progress"] = in_progress_weakness_exam(db, user=user, module_id=group["module"].id)
    return templates.TemplateResponse(
        request=request,
        name="weakness_home.html",
        context={
            "groups": list(groups.values()),
            "active_total": len(active_weaknesses(entries)),
            "available": available_reinforcement_counts(db, entries),
            "in_progress": in_progress_reinforcements(db, user),
            "recent": recent_reinforcements(db, user),
            "reinforcement_params": reinforcement_params,
            "trend_labels": TREND_LABELS,
            "level_pills": LEVEL_PILLS,
            "levels": LEVELS,
            "exam_lengths": WEAKNESS_EXAM_LENGTHS,
            "notice": request.query_params.get("info"),
        },
    )


@router.post("/points-faibles/renforcer")
async def weakness_reinforce(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    form = await request.form()
    if not validate_csrf_token(request, form.get("csrf_token")):
        return RedirectResponse(url="/points-faibles", status_code=303)
    module_code = form.get("matiere")
    module = db.query(models.Module).filter_by(code=module_code).first() if module_code else None
    kind, targets = resolve_targets(
        weakness_profile(db, user_id=user.id),
        keys=form.getlist("cible"),
        uaa_slugs=form.getlist("cours"),
        module_id=module.id if module else None,
    )
    try:
        session = start_reinforcement(db, user=user, kind=kind, targets=targets)
    except WeaknessError:
        return RedirectResponse(url="/points-faibles?info=vide", status_code=303)
    return RedirectResponse(url=f"/renforcement/{session.id}", status_code=303)


@router.post("/points-faibles/examen")
async def weakness_exam(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    form = await request.form()
    if not validate_csrf_token(request, form.get("csrf_token")):
        return RedirectResponse(url="/points-faibles", status_code=303)
    module = db.query(models.Module).filter_by(code=form.get("matiere") or "").first()
    if module is None:
        return RedirectResponse(url="/points-faibles", status_code=303)
    try:
        count = int(form.get("questions") or WEAKNESS_EXAM_LENGTHS[0])
    except ValueError:
        count = WEAKNESS_EXAM_LENGTHS[0]
    try:
        session = start_weakness_exam(db, user=user, module=module, count=count)
    except WeaknessError:
        return RedirectResponse(url="/points-faibles?info=examen", status_code=303)
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)


def _reinforcement_or_404(db, session_id: int, user: User):
    session = get_owned_reinforcement(db, session_id=session_id, user=user)
    if session is None:
        raise HTTPException(status_code=404, detail="Renforcement introuvable")
    return session


def _render_question(request, db, session, session_question, *, error=None, answer_json=None, status_code=200):
    display = build_question_display(db, session_question)
    if answer_json is not None:
        display.answer_json = answer_json
    validated = is_validated(session_question)
    questions = ordered_questions(session)
    uaa = session_question.question_version.question.uaa
    feedback = feedback_view(session_question) if validated else None
    variant_note = None
    if feedback and not feedback["correct"] and not feedback["technical_error"]:
        later = [sq for sq in questions if sq.position > session_question.position]
        if any(sq.question_version.question.uaa_id == (uaa.id if uaa else None) for sq in later):
            variant_note = "Une autre question sur cette notion t'attend plus loin : c'est en recommençant qu'on la fixe."
    return templates.TemplateResponse(
        request=request,
        name="quiz_question.html",
        status_code=status_code,
        context={
            "session": session,
            "params": reinforcement_params(session),
            "display": display,
            "position": session_question.position,
            "total": len(questions),
            "done": sum(1 for sq in questions if is_validated(sq)),
            "validated": validated,
            "feedback": feedback,
            "is_last": current_position(session) is None,
            "error": error,
            "uaa": uaa,
            "type_label": TYPE_LABELS.get(display.question_type, ""),
            "play_url": f"/renforcement/{session.id}",
            "pause_url": "/points-faibles",
            "pause_note": "ton renforcement est enregistré",
            "activity_title": "Renforcement ciblé",
            "activity_icon": "bullseye",
            "intro_note": "Renforcement ciblé : la correction s'affiche dès que tu valides ta réponse.",
            "reread_button": True,
            "last_label": "Voir mon bilan",
            "variant_note": variant_note,
        },
    )


@router.get("/renforcement/{session_id}", response_class=HTMLResponse)
async def reinforcement_play(
    session_id: int,
    request: Request,
    vu: int | None = None,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _reinforcement_or_404(db, session_id, user)
    questions = ordered_questions(session)
    if vu is not None:
        reviewed = next((sq for sq in questions if sq.position == vu), None)
        if reviewed is not None and is_validated(reviewed):
            return _render_question(request, db, session, reviewed)
    position = current_position(session)
    if position is None:
        return templates.TemplateResponse(
            request=request,
            name="weakness_reinforcement_done.html",
            context={
                "session": session,
                "params": reinforcement_params(session),
                "summary": reinforcement_summary(db, session),
                "level_pills": LEVEL_PILLS,
            },
        )
    current = next(sq for sq in questions if sq.position == position)
    return _render_question(request, db, session, current)


@router.post("/renforcement/{session_id}/valider")
async def reinforcement_validate(
    session_id: int,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _reinforcement_or_404(db, session_id, user)
    form = await request.form()
    base = f"/renforcement/{session.id}"
    if not validate_csrf_token(request, form.get("csrf_token")):
        return RedirectResponse(url=base, status_code=303)
    try:
        position = int(form.get("position", ""))
    except ValueError:
        return RedirectResponse(url=base, status_code=303)
    target = next((sq for sq in session.session_questions if sq.position == position), None)
    if target is None or session.status != SessionStatus.IN_PROGRESS or is_validated(target):
        suffix = f"?vu={position}" if target is not None and is_validated(target) else ""
        return RedirectResponse(url=f"{base}{suffix}", status_code=303)
    if position != current_position(session):
        return RedirectResponse(url=base, status_code=303)
    version = target.question_version
    try:
        answer_json = parse_quiz_answer(version.question_type, version.content_json, form)
    except IncompleteAnswerError as exc:
        partial = incomplete_answer_echo(version.content_json, form)
        return _render_question(request, db, session, target, error=str(exc), answer_json=partial, status_code=422)
    validate_reinforcement_answer(db, session=session, session_question=target, answer_json=answer_json, user=user)
    return RedirectResponse(url=f"{base}?vu={position}", status_code=303)

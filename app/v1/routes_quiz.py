"""Routes de l'espace Quiz (ticket #137) : choix du périmètre dans le parcours,
récapitulatif avant départ, partie question par question avec validation serveur, résultat
et reprise des erreurs. Toute la logique est dans `app.v1.quiz_service` ; un compte est
requis (score et reprise persistés)."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.database import get_db
from app.templating import templates
from app.v1.auth import require_user, validate_csrf_token
from app.v1.models import SessionDifficultyRequest, SessionStatus, User
from app.v1.parcours import get_saved_pathway
from app.v1.quiz_service import (
    DEFAULT_QUIZ_DIFFICULTY,
    DEFAULT_QUIZ_LENGTH,
    QUIZ_DIFFICULTY_LABELS,
    QUIZ_LENGTHS,
    TYPE_LABELS,
    IncompleteAnswerError,
    QuizError,
    build_catalog,
    current_position,
    feedback_view,
    get_owned_quiz,
    incomplete_answer_echo,
    is_validated,
    ordered_questions,
    parse_quiz_answer,
    plan_quiz,
    quiz_params,
    quiz_results,
    resolve_scope,
    result_message,
    start_quiz,
    subject_quiz_stats,
    user_quizzes,
    validate_quiz_answer,
)
from app.v1.session_service import build_question_display

router = APIRouter(tags=["v1-quiz"])


def _difficulty(raw: str | None) -> SessionDifficultyRequest:
    try:
        return SessionDifficultyRequest(raw)
    except ValueError:
        return DEFAULT_QUIZ_DIFFICULTY


def _count(raw: str | int | None) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_QUIZ_LENGTH
    return value if value in QUIZ_LENGTHS else DEFAULT_QUIZ_LENGTH


def _selection_from(source) -> dict:
    """Lit la sélection depuis les paramètres d'URL ou un formulaire (mêmes noms)."""
    return {
        "whole_pathway": source.get("parcours") == "1",
        "module_codes": source.getlist("matiere"),
        "uaa_slugs": source.getlist("uaa"),
    }


def _pathway_or_redirect(request: Request, db, user: User):
    pathway = get_saved_pathway(request, db, user)
    if pathway is None:
        return None, RedirectResponse(url="/parcours", status_code=303)
    return pathway, None


@router.get("/quiz", response_class=HTMLResponse)
async def quiz_home(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    pathway, redirect = _pathway_or_redirect(request, db, user)
    if redirect:
        return redirect
    catalog = build_catalog(db, pathway, user)
    selection = _selection_from(request.query_params)
    quizzes = user_quizzes(db, user)
    return templates.TemplateResponse(
        request=request,
        name="quiz_home.html",
        context={
            "pathway": pathway,
            "catalog": catalog,
            "preselected_modules": set(selection["module_codes"]),
            "preselected_uaas": set(selection["uaa_slugs"]),
            "open_modules": {
                offer.module.code
                for offer in catalog
                if any(c.uaa.slug in selection["uaa_slugs"] for c in offer.chapters)
            },
            "lengths": QUIZ_LENGTHS,
            "default_length": DEFAULT_QUIZ_LENGTH,
            "difficulties": list(QUIZ_DIFFICULTY_LABELS.items()),
            "default_difficulty": DEFAULT_QUIZ_DIFFICULTY,
            "in_progress": [q for q in quizzes if q.status == SessionStatus.IN_PROGRESS],
            "finished": [q for q in quizzes if q.status == SessionStatus.COMPLETED],
            "stats": subject_quiz_stats(db, user),
            "quiz_params": quiz_params,
        },
    )


@router.get("/quiz/apercu", response_class=HTMLResponse)
async def quiz_preview(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    pathway, redirect = _pathway_or_redirect(request, db, user)
    if redirect:
        return redirect
    params = request.query_params
    selection = _selection_from(params)
    count = _count(params.get("questions"))
    difficulty = _difficulty(params.get("difficulte"))
    scope = resolve_scope(build_catalog(db, pathway, user), **selection)
    plan = plan_quiz(scope, count=count, difficulty=difficulty)
    return templates.TemplateResponse(
        request=request,
        name="quiz_recap.html",
        context={
            "pathway": pathway,
            "scope": scope,
            "plan": plan,
            "selection": selection,
            "count": count,
            "difficulty": difficulty,
            "difficulty_label": QUIZ_DIFFICULTY_LABELS[difficulty],
            "nothing_selected": not any(selection.values()),
        },
    )


@router.post("/quiz/demarrer")
async def quiz_start(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    form = await request.form()
    if not validate_csrf_token(request, form.get("csrf_token")):
        return RedirectResponse(url="/quiz", status_code=303)
    pathway, redirect = _pathway_or_redirect(request, db, user)
    if redirect:
        return redirect
    scope = resolve_scope(build_catalog(db, pathway, user), **_selection_from(form))
    try:
        session = start_quiz(
            db, user=user, pathway=pathway, scope=scope,
            count=_count(form.get("questions")), difficulty=_difficulty(form.get("difficulte")),
        )
    except QuizError:
        return RedirectResponse(url="/quiz?vide=1", status_code=303)
    return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)


def _quiz_or_404(db, session_id: int, user: User):
    session = get_owned_quiz(db, session_id=session_id, user=user)
    if session is None:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    return session


def _render_question(request, db, session, session_question, *, error=None, answer_json=None, status_code=200):
    display = build_question_display(db, session_question)
    if answer_json is not None:
        display.answer_json = answer_json
    validated = is_validated(session_question)
    questions = ordered_questions(session)
    uaa = session_question.question_version.question.uaa
    return templates.TemplateResponse(
        request=request,
        name="quiz_question.html",
        status_code=status_code,
        context={
            "session": session,
            "params": quiz_params(session),
            "display": display,
            "position": session_question.position,
            "total": len(questions),
            "done": sum(1 for sq in questions if is_validated(sq)),
            "validated": validated,
            "feedback": feedback_view(session_question) if validated else None,
            "is_last": current_position(session) is None,
            "error": error,
            "uaa": uaa,
            "type_label": TYPE_LABELS.get(display.question_type, ""),
        },
    )


@router.get("/quiz/parties/{session_id}", response_class=HTMLResponse)
async def quiz_play(
    session_id: int,
    request: Request,
    vu: int | None = None,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _quiz_or_404(db, session_id, user)
    questions = ordered_questions(session)
    if vu is not None:
        reviewed = next((sq for sq in questions if sq.position == vu), None)
        if reviewed is not None and is_validated(reviewed):
            return _render_question(request, db, session, reviewed)
    position = current_position(session)
    if position is None:
        results = quiz_results(session)
        title, message = result_message(results["pct"])
        return templates.TemplateResponse(
            request=request,
            name="quiz_results.html",
            context={
                "session": session,
                "params": quiz_params(session),
                "results": results,
                "title": title,
                "message": message,
                "difficulty_label": QUIZ_DIFFICULTY_LABELS.get(session.difficulty_requested, ""),
            },
        )
    current = next(sq for sq in questions if sq.position == position)
    return _render_question(request, db, session, current)


@router.post("/quiz/parties/{session_id}/valider")
async def quiz_validate(
    session_id: int,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _quiz_or_404(db, session_id, user)
    form = await request.form()
    if not validate_csrf_token(request, form.get("csrf_token")):
        return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
    try:
        position = int(form.get("position", ""))
    except ValueError:
        return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
    target = next((sq for sq in session.session_questions if sq.position == position), None)
    if target is None or session.status != SessionStatus.IN_PROGRESS or is_validated(target):
        # Double clic / onglet en retard : on montre ce qui est déjà validé, sans recorriger.
        suffix = f"?vu={position}" if target is not None and is_validated(target) else ""
        return RedirectResponse(url=f"/quiz/parties/{session.id}{suffix}", status_code=303)
    if position != current_position(session):
        return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
    version = target.question_version
    try:
        answer_json = parse_quiz_answer(version.question_type, version.content_json, form)
    except IncompleteAnswerError as exc:
        partial = incomplete_answer_echo(version.content_json, form)
        return _render_question(request, db, session, target, error=str(exc), answer_json=partial, status_code=422)
    validate_quiz_answer(db, session=session, session_question=target, answer_json=answer_json)
    return RedirectResponse(url=f"/quiz/parties/{session.id}?vu={position}", status_code=303)


def _replay(request, db, user, session, *, errors_only: bool):
    pathway = get_saved_pathway(request, db, user)
    if pathway is None:
        return RedirectResponse(url="/parcours", status_code=303)
    params = quiz_params(session)
    catalog = build_catalog(db, pathway, user)
    exclude = set()
    if errors_only:
        results = quiz_results(session)
        exclude = set(results["missed_question_ids"])
        uaa_ids = [entry["uaa"].id for entry in results["to_review"]]
        if not uaa_ids:
            return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
        count = next((n for n in QUIZ_LENGTHS if n >= len(exclude)), QUIZ_LENGTHS[-1])
        scope = resolve_scope(catalog, uaa_ids=uaa_ids, kind="erreurs")
    else:
        count = _count(params.get("requested_count"))
        scope = resolve_scope(catalog, uaa_ids=params.get("uaa_ids") or [], kind=params.get("kind"))
    try:
        new_session = start_quiz(
            db, user=user, pathway=pathway, scope=scope, count=count,
            difficulty=session.difficulty_requested, exclude_question_ids=exclude, retry_of=session.id,
        )
    except QuizError:
        return RedirectResponse(url=f"/quiz/parties/{session.id}?epuise=1", status_code=303)
    return RedirectResponse(url=f"/quiz/parties/{new_session.id}", status_code=303)


@router.post("/quiz/parties/{session_id}/rejouer")
async def quiz_replay(
    session_id: int,
    request: Request,
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _quiz_or_404(db, session_id, user)
    if not validate_csrf_token(request, csrf_token):
        return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
    return _replay(request, db, user, session, errors_only=False)


@router.post("/quiz/parties/{session_id}/erreurs")
async def quiz_retry_errors(
    session_id: int,
    request: Request,
    csrf_token: str = Form(""),
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = _quiz_or_404(db, session_id, user)
    if not validate_csrf_token(request, csrf_token) or session.status != SessionStatus.COMPLETED:
        return RedirectResponse(url=f"/quiz/parties/{session.id}", status_code=303)
    return _replay(request, db, user, session, errors_only=True)

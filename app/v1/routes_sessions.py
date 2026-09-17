"""Routes du parcours de session V1 (ticket #55, MVP urgent MC01→MC38 + parcours global
AMPCR). Condense #41 (sélection)/#42 (sessions/autosave)/#43 (génération)/#44
(correction)/#24/#25 (UX) en un parcours réellement utilisable avant les épreuves.

Toutes les routes exigent un compte (`require_user`/`require_user_api`, ticket #39) — les
cours restent publics, S'entraîner/S'évaluer non.

UX : une question à la fois (formulaire HTML classique, Post/Redirect/Get) plutôt qu'une
autosave JS pilotée par `fetch()` pour la navigation — choix délibéré de simplicité/
fiabilité pour l'échéance (voir `docs/claude-reports/2026-09-17_ticket-55_urgent-ampcr-full.md`,
§ décisions) : chaque clic Suivant/Précédent enregistre la réponse courante côté serveur
avant de rediriger, aucun JavaScript requis pour que le parcours fonctionne. L'API JSON
`POST /api/v1/sessions/{id}/answers/{session_question_id}` (exigée explicitement par le
ticket) reste disponible en parallèle, pour un usage programmatique futur — les deux
chemins appellent la même fonction `save_answer()`, jamais deux mécanismes distincts."""

from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.ai.factory import get_ai_provider
from app.ai.provider import AINotConfiguredError
from app.database import get_db
from app.models import UAA, Module
from app.templating import templates
from app.v1.ampcr_plan import AMPCR_MODULE_CODE, get_plan_by_slug
from app.v1.auth import require_user, require_user_api
from app.v1.bank import get_uaa_by_slug, import_mc01_legacy_to_bank
from app.v1.models import (
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    User,
)
from app.v1.session_service import (
    GLOBAL_EXAM_QUESTION_COUNT,
    SessionCreationError,
    build_question_display,
    get_in_progress_session,
    get_owned_session,
    save_answer,
    start_session,
    submit_session,
)

router = APIRouter(tags=["v1-sessions"])


class _UnconfiguredProvider:
    """Substitut paresseux quand `get_ai_provider()` échouerait dès la construction
    (`AINotConfiguredError`, voir `app.ai.openai_provider.OpenAIProvider.__init__`) :
    laisse `start_session`/`submit_session` suivre leur chemin de repli existant
    (`except AIProviderError`) au lieu de faire échouer la route avant même d'essayer la
    banque locale."""

    def generate_questionnaire(self, request):
        raise AINotConfiguredError("Génération IA non configurée sur ce serveur.")

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        raise AINotConfiguredError("Correction IA non configurée sur ce serveur.")


def _get_provider_or_unconfigured():
    try:
        return get_ai_provider()
    except AINotConfiguredError:
        return _UnconfiguredProvider()


_DIFFICULTY_LABELS = {
    SessionDifficultyRequest.EASY: "Facile",
    SessionDifficultyRequest.MEDIUM: "Moyen",
    SessionDifficultyRequest.HARD: "Difficile",
}


def _ampcr_module(db) -> Module:
    module = db.query(Module).filter_by(code=AMPCR_MODULE_CODE).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Module AMPCR introuvable")
    return module


def _ensure_mc01_bank_seeded(db, module: Module, uaa: UAA) -> None:
    if uaa.slug == "ampcr-mc01":
        import_mc01_legacy_to_bank(db, module, uaa)
        db.commit()


# --- Landing pages (appelées depuis app/main.py pour les UAA AMPCR) ---------------------------


def render_practice_landing(request: Request, db, uaa: UAA, user: User) -> HTMLResponse:
    module = uaa.module
    _ensure_mc01_bank_seeded(db, module, uaa)
    resumable = get_in_progress_session(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.PRACTICE, uaa_id=uaa.id
    )
    return templates.TemplateResponse(
        request=request,
        name="v1_session_start.html",
        context={
            "uaa": uaa,
            "mode": "practice",
            "mode_label": "S'entraîner",
            "start_url": f"/uaa/{uaa.slug}/practice/start",
            "resumable": resumable,
            "difficulties": list(_DIFFICULTY_LABELS.items()),
            "allow_new_while_in_progress": True,
        },
    )


def render_exam_landing(request: Request, db, uaa: UAA, user: User) -> HTMLResponse:
    module = uaa.module
    _ensure_mc01_bank_seeded(db, module, uaa)
    resumable = get_in_progress_session(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.EXAM, uaa_id=uaa.id
    )
    return templates.TemplateResponse(
        request=request,
        name="v1_session_start.html",
        context={
            "uaa": uaa,
            "mode": "exam",
            "mode_label": "S'évaluer",
            "start_url": f"/uaa/{uaa.slug}/exam/start",
            "resumable": resumable,
            "difficulties": list(_DIFFICULTY_LABELS.items()),
            # Évite plusieurs examens IN_PROGRESS identiques (choix documenté, ticket #55
            # § 12/§ RESUME) : si un examen est déjà en cours, seule la reprise est proposée.
            "allow_new_while_in_progress": False,
        },
    )


def _start_session_for_uaa(
    db, *, uaa: UAA, user: User, mode: SessionMode, difficulty: SessionDifficultyRequest
) -> QuestionnaireSession:
    module = uaa.module
    _ensure_mc01_bank_seeded(db, module, uaa)
    plan = get_plan_by_slug(uaa.slug)
    return start_session(
        db,
        user=user,
        module_id=module.id,
        uaa_id=uaa.id,
        uaa_code=plan.code if plan else None,
        mode=mode,
        difficulty=difficulty,
        provider=_get_provider_or_unconfigured(),
    )


@router.post("/uaa/{uaa_slug}/practice/start")
async def start_practice_session(
    uaa_slug: str,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
    difficulty: str = Form("medium"),
    resume: str = Form(""),
):
    uaa = get_uaa_by_slug(db, uaa_slug)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")

    if resume:
        existing = get_in_progress_session(
            db, user_id=user.id, module_id=uaa.module_id, mode=SessionMode.PRACTICE, uaa_id=uaa.id
        )
        if existing is not None:
            return RedirectResponse(url=f"/sessions/{existing.id}", status_code=303)

    try:
        session = _start_session_for_uaa(
            db, uaa=uaa, user=user, mode=SessionMode.PRACTICE,
            difficulty=SessionDifficultyRequest(difficulty),
        )
    except (SessionCreationError, ValueError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="v1_session_start.html",
            context={
                "uaa": uaa, "mode": "practice", "mode_label": "S'entraîner",
                "start_url": f"/uaa/{uaa.slug}/practice/start", "resumable": None,
                "difficulties": list(_DIFFICULTY_LABELS.items()),
                "allow_new_while_in_progress": True, "error": str(exc),
            },
            status_code=503,
        )
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)


@router.post("/uaa/{uaa_slug}/exam/start")
async def start_exam_session(
    uaa_slug: str,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
    difficulty: str = Form("medium"),
    resume: str = Form(""),
):
    uaa = get_uaa_by_slug(db, uaa_slug)
    if uaa is None:
        raise HTTPException(status_code=404, detail="UAA introuvable")

    # Un examen déjà IN_PROGRESS est toujours repris, jamais dupliqué (§ 12 du ticket #55 :
    # « éviter plusieurs examens IN_PROGRESS identiques ») — `resume` n'a donc pas besoin
    # d'être testé explicitement ici, contrairement à practice où plusieurs sessions
    # simultanées restent autorisées.
    existing = get_in_progress_session(
        db, user_id=user.id, module_id=uaa.module_id, mode=SessionMode.EXAM, uaa_id=uaa.id
    )
    if existing is not None:
        return RedirectResponse(url=f"/sessions/{existing.id}", status_code=303)

    try:
        session = _start_session_for_uaa(
            db, uaa=uaa, user=user, mode=SessionMode.EXAM,
            difficulty=SessionDifficultyRequest(difficulty),
        )
    except (SessionCreationError, ValueError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="v1_session_start.html",
            context={
                "uaa": uaa, "mode": "exam", "mode_label": "S'évaluer",
                "start_url": f"/uaa/{uaa.slug}/exam/start", "resumable": None,
                "difficulties": list(_DIFFICULTY_LABELS.items()),
                "allow_new_while_in_progress": False, "error": str(exc),
            },
            status_code=503,
        )
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)


# --- Parcours global AMPCR (§ 16/17 du ticket #55) ---------------------------------------------


@router.get("/modules/ampcr/practice", response_class=HTMLResponse)
async def ampcr_global_practice_landing(
    request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    module = _ampcr_module(db)
    resumable = get_in_progress_session(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.PRACTICE, uaa_id=None
    )
    return templates.TemplateResponse(
        request=request,
        name="v1_session_start.html",
        context={
            "uaa": None,
            "global_title": "Informatique AMPCR — programme complet",
            "mode": "practice",
            "mode_label": "S'entraîner (AMPCR global)",
            "start_url": "/modules/ampcr/practice/start",
            "resumable": resumable,
            "difficulties": list(_DIFFICULTY_LABELS.items()),
            "allow_new_while_in_progress": True,
        },
    )


@router.get("/modules/ampcr/exam", response_class=HTMLResponse)
async def ampcr_global_exam_landing(
    request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    module = _ampcr_module(db)
    resumable = get_in_progress_session(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.EXAM, uaa_id=None
    )
    return templates.TemplateResponse(
        request=request,
        name="v1_session_start.html",
        context={
            "uaa": None,
            "global_title": "Informatique AMPCR — examen blanc complet",
            "mode": "exam",
            "mode_label": "S'évaluer (examen blanc AMPCR, 20 questions)",
            "start_url": "/modules/ampcr/exam/start",
            "resumable": resumable,
            "difficulties": list(_DIFFICULTY_LABELS.items()),
            "allow_new_while_in_progress": False,
        },
    )


@router.post("/modules/ampcr/practice/start")
async def start_ampcr_global_practice(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
    difficulty: str = Form("medium"),
    resume: str = Form(""),
):
    module = _ampcr_module(db)
    if resume:
        existing = get_in_progress_session(
            db, user_id=user.id, module_id=module.id, mode=SessionMode.PRACTICE, uaa_id=None
        )
        if existing is not None:
            return RedirectResponse(url=f"/sessions/{existing.id}", status_code=303)
    session = start_session(
        db, user=user, module_id=module.id, uaa_id=None, uaa_code=None,
        mode=SessionMode.PRACTICE, difficulty=SessionDifficultyRequest(difficulty),
        provider=_get_provider_or_unconfigured(),
    )
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)


@router.post("/modules/ampcr/exam/start")
async def start_ampcr_global_exam(
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
    difficulty: str = Form("medium"),
    resume: str = Form(""),
):
    module = _ampcr_module(db)
    existing = get_in_progress_session(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.EXAM, uaa_id=None
    )
    if existing is not None:
        return RedirectResponse(url=f"/sessions/{existing.id}", status_code=303)
    session = start_session(
        db, user=user, module_id=module.id, uaa_id=None, uaa_code=None,
        mode=SessionMode.EXAM, difficulty=SessionDifficultyRequest(difficulty),
        provider=_get_provider_or_unconfigured(), question_count=GLOBAL_EXAM_QUESTION_COUNT,
    )
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)


# --- Vue de session (question par question puis résultats) -------------------------------------


def _parse_answer_form(question_type: str, content: dict[str, Any], form) -> dict[str, Any]:
    if question_type == "multiple_choice":
        return {"selected_option_ids": form.getlist("option_id")}
    if question_type == "classification":
        assignments = []
        for index in range(len(content["elements"])):
            raw = form.get(f"category__{index}", "")
            assignments.append(int(raw) if raw.isdigit() else -1)
        return {"assignments": assignments}
    if question_type == "ordering":
        items = content["items"]
        positions = []
        for item in items:
            raw = form.get(f"position__{item['id']}", "0")
            positions.append((int(raw) if raw.isdigit() else 0, item["id"]))
        ordered = [item_id for _, item_id in sorted(positions)]
        return {"order": ordered}
    # short_answer / vocabulary / diagnostic / long_answer
    return {"text": form.get("text", "")}


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
async def view_session(
    session_id: int,
    request: Request,
    q: int = 1,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)

    if session.status != SessionStatus.IN_PROGRESS:
        results = [
            {
                "position": sq.position,
                "question_type": sq.question_version.question_type,
                "prompt": sq.question_version.content_json.get("prompt", ""),
                "user_answer": _describe_answer(sq),
                "feedback": (sq.answer.feedback_json if sq.answer else {}) or {},
                "points_awarded": sq.answer.points_awarded if sq.answer else 0.0,
            }
            for sq in session_questions
        ]
        return templates.TemplateResponse(
            request=request,
            name="v1_session_results.html",
            context={"session": session, "results": results},
        )

    position = max(1, min(q, len(session_questions)))
    current = session_questions[position - 1]
    display = build_question_display(current)

    return templates.TemplateResponse(
        request=request,
        name="v1_session_question.html",
        context={
            "session": session,
            "display": display,
            "position": position,
            "total": len(session_questions),
            "has_previous": position > 1,
            "has_next": position < len(session_questions),
            "is_last": position == len(session_questions),
        },
    )


def _describe_answer(session_question) -> str:
    from app.v1.ai_bridge import BRIDGE_TYPES, describe_submitted_answer

    version = session_question.question_version
    answer_json = (session_question.answer.answer_json if session_question.answer else {}) or {}
    if version.question_type not in BRIDGE_TYPES:
        return "(sans réponse)"
    return describe_submitted_answer(version.question_type, version.content_json, answer_json)


@router.post("/sessions/{session_id}/answer")
async def answer_and_navigate(
    session_id: int,
    request: Request,
    position: int = Form(...),
    direction: str = Form("next"),
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status != SessionStatus.IN_PROGRESS:
        return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    current = next((sq for sq in session_questions if sq.position == position), None)
    if current is not None:
        form = await request.form()
        content = current.question_version.content_json
        answer_json = _parse_answer_form(current.question_version.question_type, content, form)
        save_answer(db, session_question=current, answer_json=answer_json)

    if direction == "previous":
        next_position = max(1, position - 1)
    elif direction == "submit":
        return RedirectResponse(url=f"/sessions/{session_id}/submit-confirm", status_code=303)
    else:
        next_position = min(len(session_questions), position + 1)
    return RedirectResponse(url=f"/sessions/{session_id}?q={next_position}", status_code=303)


@router.get("/sessions/{session_id}/submit-confirm", response_class=HTMLResponse)
async def submit_confirm(
    session_id: int,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status != SessionStatus.IN_PROGRESS:
        return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)
    return templates.TemplateResponse(
        request=request, name="v1_session_submit_confirm.html", context={"session": session}
    )


@router.post("/sessions/{session_id}/submit")
async def submit_session_route(
    session_id: int,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
):
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status == SessionStatus.IN_PROGRESS:
        submit_session(db, session=session, provider=_get_provider_or_unconfigured())
    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)


# --- API autosave JSON (ticket #55 § AUTOSAVE) --------------------------------------------------


@router.post("/api/v1/sessions/{session_id}/answers/{session_question_id}")
async def api_autosave_answer(
    session_id: int,
    session_question_id: int,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user_api),  # noqa: B008
):
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status != SessionStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Session déjà terminée : réponse non modifiable.")

    session_question = next(
        (sq for sq in session.session_questions if sq.id == session_question_id), None
    )
    if session_question is None:
        raise HTTPException(status_code=404, detail="Question de session introuvable")

    payload = await request.json()
    answer_json = payload.get("answer_json")
    if not isinstance(answer_json, dict):
        raise HTTPException(status_code=422, detail="answer_json (objet) est requis.")

    # Jamais de correct/incorrect/solution/score ici (voir docstring du module) : l'API
    # ne retourne QUE la confirmation d'enregistrement.
    save_answer(db, session_question=session_question, answer_json=answer_json)
    return {"saved": True}

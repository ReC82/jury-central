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
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.ai.factory import get_ai_provider
from app.ai.provider import AINotConfiguredError
from app.database import get_db
from app.models import UAA, Module
from app.templating import templates
from app.v1.ampcr_plan import AMPCR_MODULE_CODE, get_plan_by_slug
from app.v1.auth import require_user, require_user_api
from app.v1.bank import get_uaa_by_slug, import_mc01_legacy_to_bank
from app.v1.francais_bank import import_francais_c01_to_bank
from app.v1.francais_plan import get_francais_plan_by_slug
from app.v1.mc38_transversal import MC38_CODE, MC38_SESSION_SCOPE
from app.v1.models import (
    QuestionnaireSession,
    SessionDifficultyRequest,
    SessionMode,
    SessionStatus,
    SourceDocumentVersion,
    User,
)
from app.v1.session_service import (
    DEFAULT_QUESTION_COUNT,
    GLOBAL_EXAM_QUESTION_COUNT,
    SEVERITY_UI_DEFAULT,
    SEVERITY_UI_LABELS,
    SEVERITY_UI_LEVELS,
    SessionCreationError,
    # Ticket #77 : seule source de vérité pour « quel(s) document(s) une question
    # référence », dérivée du payload public — jamais du `content_json` brut. Importé ici
    # malgré le préfixe privé pour que les résultats/export (§ 6 du ticket) utilisent
    # EXACTEMENT la même résolution que l'élève pendant la session
    # (`build_question_display`) et que le correcteur IA (`_document_contexts_for`),
    # plutôt que d'en réimplémenter une troisième copie qui pourrait diverger.
    _referenced_document_ids,
    build_question_display,
    describe_session_scope,
    get_in_progress_session,
    get_owned_session,
    list_user_sessions,
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


def _ensure_bank_seeded(db, module: Module, uaa: UAA) -> None:
    """Amorce paresseuse de la banque hand-authored au premier accès practice/exam de
    l'UAA concernée — MC01 (ticket #55) et Français C01 (ticket #47), même principe
    (idempotent, jamais de doublon)."""
    if uaa.slug == "ampcr-mc01":
        import_mc01_legacy_to_bank(db, module, uaa)
        db.commit()
    elif uaa.slug == "francais-c01":
        import_francais_c01_to_bank(db, module, uaa)
        db.commit()


# --- Landing pages (appelées depuis app/main.py pour les UAA AMPCR) ---------------------------


def _resumable_session_for_uaa(db, *, user_id: int, module_id: int, mode: SessionMode, uaa: UAA):
    """Repère une session per-MC déjà en cours pour `uaa`. MC38 (ticket #58) est un cas
    particulier : ses questions appartiennent à MC01→MC37, jamais à MC38 lui-même, donc
    `uaa_id=uaa.id` ne matcherait jamais — on utilise le marqueur `scope` à la place (voir
    `get_in_progress_session`)."""
    plan = get_plan_by_slug(uaa.slug)
    if plan is not None and plan.code == MC38_CODE:
        return get_in_progress_session(
            db, user_id=user_id, module_id=module_id, mode=mode, scope=MC38_SESSION_SCOPE
        )
    return get_in_progress_session(db, user_id=user_id, module_id=module_id, mode=mode, uaa_id=uaa.id)


def render_practice_landing(request: Request, db, uaa: UAA, user: User) -> HTMLResponse:
    module = uaa.module
    _ensure_bank_seeded(db, module, uaa)
    resumable = _resumable_session_for_uaa(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.PRACTICE, uaa=uaa
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
            "active_space": "practice",
        },
    )


def render_exam_landing(request: Request, db, uaa: UAA, user: User) -> HTMLResponse:
    module = uaa.module
    _ensure_bank_seeded(db, module, uaa)
    resumable = _resumable_session_for_uaa(
        db, user_id=user.id, module_id=module.id, mode=SessionMode.EXAM, uaa=uaa
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
            "active_space": "exam",
        },
    )


def _start_session_for_uaa(
    db, *, uaa: UAA, user: User, mode: SessionMode, difficulty: SessionDifficultyRequest
) -> QuestionnaireSession:
    module = uaa.module
    _ensure_bank_seeded(db, module, uaa)
    plan = get_plan_by_slug(uaa.slug)
    francais_plan = None
    if plan is not None:
        uaa_code = plan.code
    else:
        francais_plan = get_francais_plan_by_slug(uaa.slug)
        uaa_code = francais_plan.code if francais_plan else None
    # MC38 examen (ticket #58 § 6) : « utiliser 20 questions si le moteur le permet déjà »
    # — même volume que l'examen blanc global, cohérent avec sa nature transversale
    # MC01→MC37 (voir app.v1.session_service._start_mc38_transversal_session). Français
    # (overnight mission du 2026-09-19, § Phase 9) : même volume — le corpus (40
    # questions, § Phases 5-7) le permet techniquement (vérifié : un examen de 20
    # questions se compose entièrement depuis la banque, sans appel de génération).
    question_count = (
        GLOBAL_EXAM_QUESTION_COUNT
        if mode == SessionMode.EXAM and (uaa_code == "MC38" or francais_plan is not None)
        else DEFAULT_QUESTION_COUNT
    )
    return start_session(
        db,
        user=user,
        module_id=module.id,
        uaa_id=uaa.id,
        uaa_code=uaa_code,
        mode=mode,
        difficulty=difficulty,
        provider=_get_provider_or_unconfigured(),
        question_count=question_count,
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
        existing = _resumable_session_for_uaa(
            db, user_id=user.id, module_id=uaa.module_id, mode=SessionMode.PRACTICE, uaa=uaa
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
    existing = _resumable_session_for_uaa(
        db, user_id=user.id, module_id=uaa.module_id, mode=SessionMode.EXAM, uaa=uaa
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


@router.get("/documents/{version_id}", response_class=HTMLResponse)
async def view_source_document(
    version_id: int,
    request: Request,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
) -> HTMLResponse:
    """Route de lecture seule stable (ticket #79 § 7) — pensée pour s'ouvrir dans un
    nouvel onglet (`target="_blank"`) depuis une question ou un résultat, sans perdre la
    page d'origine. Titre + texte complet uniquement : aucun feedback, aucune solution,
    aucune information sur quelle(s) question(s) le référencent — un `SourceDocumentVersion`
    est un document de référence partagé, jamais un contenu propre à une session ou un
    utilisateur, donc pas de vérification de propriété au-delà de « être connecté »
    (mêmes règles d'accès que la page Cours, déjà publique pour le contenu pédagogique)."""
    document = db.get(SourceDocumentVersion, version_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document introuvable")
    return templates.TemplateResponse(
        request=request,
        name="v1_document_view.html",
        context={"document": document},
    )


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
        results = _build_results_rows(db, session_questions)
        severity_ui = (session.parameters_json or {}).get("severity")
        return templates.TemplateResponse(
            request=request,
            name="v1_session_results.html",
            context={
                "session": session,
                "results": results,
                "scope_label": describe_session_scope(session),
                "subject_name": session.module.subject.name if session.module else "—",
                "severity_label": SEVERITY_UI_LABELS.get(severity_ui),
                "courses_to_review": _courses_to_review(results),
            },
        )

    position = max(1, min(q, len(session_questions)))
    current = session_questions[position - 1]
    display = build_question_display(db, current)

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
    from app.v1.ai_bridge import CORRECTABLE_TYPES, describe_submitted_answer

    version = session_question.question_version
    answer_json = (session_question.answer.answer_json if session_question.answer else {}) or {}
    if version.question_type not in CORRECTABLE_TYPES:
        return "(sans réponse)"
    return describe_submitted_answer(version.question_type, version.content_json, answer_json)


def _build_results_rows(db, session_questions: list) -> list[dict]:
    """Ligne de résultat par question — factorisé (ticket #62) entre l'écran HTML
    (`v1_session_results.html`) et l'export Markdown, jamais deux implémentations.

    `source_documents` (ticket #77 § 6, #79 § 8-9) : le(s) document(s) référencé(s) par
    cette question — {id, label, title, content_text} — résolus via le même payload
    public que l'élève a vu pendant la session (`_referenced_document_ids` +
    `resolve_documents_in_order`, jamais un tri par id qui casserait l'étiquetage A/B).
    Le texte complet est inclus (relecture possible depuis les résultats, § 8 du ticket
    #79) mais jamais dupliqué plusieurs fois : une seule résolution par document distinct.

    `course_title`/`course_slug` (ticket #79 § 13) : rattachement de la question à son
    UAA/cours, exposé pour qu'un futur ticket (#74) puisse ajouter un bouton « Relire le
    cours » sans nouvelle architecture — aucun bouton ajouté ici."""
    from app.v1.question_engine import public_payload
    from app.v1.session_service import document_label, resolve_documents_in_order

    payloads = {
        sq.position: public_payload(
            sq.question_version.question_type, sq.question_version.schema_version, sq.question_version.content_json
        )
        for sq in session_questions
    }
    all_doc_ids: set[int] = set()
    for payload in payloads.values():
        all_doc_ids.update(_referenced_document_ids(payload))
    documents_by_id = {
        document.id: document for document in resolve_documents_in_order(db, sorted(all_doc_ids))
    }

    rows = []
    for sq in session_questions:
        question_type = sq.question_version.question_type
        doc_ids = _referenced_document_ids(payloads[sq.position])
        source_documents = [
            {
                "id": doc_id,
                "label": document_label(question_type, index),
                "title": documents_by_id[doc_id].title or "Document source",
                "content_text": documents_by_id[doc_id].content_text or "",
            }
            for index, doc_id in enumerate(doc_ids)
            if doc_id in documents_by_id
        ]
        uaa = sq.question_version.question.uaa if sq.question_version.question else None
        rows.append(
            {
                "position": sq.position,
                "question_type": question_type,
                "prompt": sq.question_version.content_json.get("prompt", ""),
                "user_answer": _describe_answer(sq),
                "feedback": (sq.answer.feedback_json if sq.answer else {}) or {},
                "points_awarded": sq.answer.points_awarded if sq.answer else 0.0,
                "source_documents": source_documents,
                "course_title": uaa.title if uaa else None,
                "course_slug": uaa.slug if uaa else None,
                "course_code": uaa.code if uaa else None,
            }
        )
    return rows


def _is_incorrect_or_partial(row: dict) -> bool:
    """Ticket #74 : une question dont la correction n'est pas marquée `correct=True` —
    couvre à la fois « faux » (déterministe ou sémantique) et « partiel » (crédit partiel
    #70 § B, ou correction sémantique avec `correct=False` malgré des points partiels).
    `feedback` vide (jamais corrigée) est traité comme « à revoir », jamais ignoré."""
    return not (row.get("feedback") or {}).get("correct", False)


def _courses_to_review(results: list[dict], *, limit: int = 5) -> list[dict]:
    """« Cours à relire en priorité » (ticket #74) : agrège les questions incorrectes/
    partielles par cours (UAA), triées par nombre d'erreurs décroissant, limité à `limit`
    (3-5 demandé par le ticket — 5 par défaut, jamais plus). Questions sans UAA connue
    (parcours global/transversal sans mini-cours identifiable) ignorées : rien de concret
    à « relire »."""
    counts: dict[str, dict] = {}
    for row in results:
        if not _is_incorrect_or_partial(row):
            continue
        slug = row.get("course_slug")
        if not slug:
            continue
        entry = counts.setdefault(
            slug,
            {"course_slug": slug, "course_title": row.get("course_title"), "course_code": row.get("course_code"), "error_count": 0},
        )
        entry["error_count"] += 1
    ranked = sorted(counts.values(), key=lambda entry: entry["error_count"], reverse=True)
    return ranked[:limit]


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
        request=request,
        name="v1_session_submit_confirm.html",
        context={
            "session": session,
            "severity_levels": SEVERITY_UI_LEVELS,
            "severity_labels": SEVERITY_UI_LABELS,
            "severity_default": SEVERITY_UI_DEFAULT,
        },
    )


@router.post("/sessions/{session_id}/submit")
async def submit_session_route(
    session_id: int,
    db=Depends(get_db),  # noqa: B008
    user: User = Depends(require_user),  # noqa: B008
    severity: int = Form(SEVERITY_UI_DEFAULT),
):
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status == SessionStatus.IN_PROGRESS:
        severity_ui = severity if severity in SEVERITY_UI_LEVELS else SEVERITY_UI_DEFAULT
        submit_session(
            db, session=session, provider=_get_provider_or_unconfigured(), severity_ui=severity_ui
        )
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


# --- Historique utilisateur (ticket #62 § 8) -----------------------------------------------


@router.get("/mes-sessions", response_class=HTMLResponse)
async def my_sessions(
    request: Request, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> HTMLResponse:
    sessions = list_user_sessions(db, user_id=user.id)
    rows = [
        {
            "session": session,
            "scope_label": describe_session_scope(session),
            "subject_name": session.module.subject.name if session.module else "—",
            "severity_label": SEVERITY_UI_LABELS.get((session.parameters_json or {}).get("severity")),
        }
        for session in sessions
    ]
    return templates.TemplateResponse(
        request=request, name="v1_history.html", context={"rows": rows}
    )


# --- Export Markdown (ticket #62 § 13) -------------------------------------------------------


def _export_slug(session: QuestionnaireSession) -> str:
    """Identifiant court pour le nom de fichier d'export — le code de la première UAA
    référencée si une seule est en jeu (cas per-MC courant), sinon un repli générique
    dérivé du module/scope (jamais un slug vide)."""
    uaa_codes = {
        sq.question_version.question.uaa.code
        for sq in session.session_questions
        if sq.question_version.question and sq.question_version.question.uaa
    }
    if len(uaa_codes) == 1:
        return next(iter(uaa_codes)).lower()
    if (session.parameters_json or {}).get("scope") == MC38_SESSION_SCOPE:
        return "mc38-transversal"
    if len(uaa_codes) > 1:
        return "global"
    return session.module.code.lower() if session.module else "session"


def _build_session_export_markdown(session: QuestionnaireSession, results: list[dict]) -> str:
    """Contenu Markdown de l'export (ticket #62 § 13) — structure imposée : métadonnées
    puis une section par question (énoncé, ma réponse, attendu/critères, points, points
    forts, erreurs, éléments manquants, explication). Aucune donnée d'un autre
    utilisateur : construit exclusivement à partir de `session`/`results`, déjà scopés à
    l'appelant (voir `get_owned_session`)."""
    severity_ui = (session.parameters_json or {}).get("severity")
    lines = [
        "# Métadonnées",
        "",
        f"- Matière : {session.module.subject.name if session.module else '—'}",
        f"- Module / mini-cours : {describe_session_scope(session)}",
        f"- Mode : {'Évaluation' if session.mode.value == 'exam' else 'Entraînement'}",
        f"- Date : {session.completed_at.strftime('%d/%m/%Y à %H:%M') if session.completed_at else ''}",
        f"- Score : {session.score} / {session.question_count}",
        f"- Sévérité : {SEVERITY_UI_LABELS.get(severity_ui, '—')}",
        "",
    ]
    courses_to_review = _courses_to_review(results)
    if courses_to_review:
        lines += ["# Cours à relire en priorité", ""]
        for rank, entry in enumerate(courses_to_review, start=1):
            code_prefix = f"{entry['course_code']} — " if entry.get("course_code") else ""
            lines.append(
                f"{rank}. {code_prefix}{entry['course_title']} — "
                f"{entry['error_count']} erreur{'s' if entry['error_count'] > 1 else ''}"
            )
        lines.append("")
    for row in results:
        feedback = row["feedback"]
        strengths_lines = [f"- {s}" for s in feedback.get("strengths") or []] or ["—"]
        errors_lines = [f"- {e}" for e in feedback.get("errors") or []] or ["—"]
        missing_lines = [f"- {m}" for m in feedback.get("missing") or []] or ["—"]
        source_documents = row.get("source_documents") or []
        document_ref_lines = [f"- {doc['label']} : {doc['title']}" for doc in source_documents]
        lines += [
            f"## Question {row['position']}",
            "",
            row["prompt"],
            "",
            *(["Document(s) de référence :", "", *document_ref_lines, ""] if source_documents else []),
            "### Ma réponse",
            "",
            row["user_answer"] or "(sans réponse)",
            "",
            "### Attendu / critères",
            "",
            feedback.get("expected_answer") or "—",
            "",
            "### Points",
            "",
            f"{row['points_awarded']} / {feedback.get('points_max', 1)}",
            "",
            "### Points forts",
            "",
            *strengths_lines,
            "",
            "### Erreurs",
            "",
            *errors_lines,
            "",
            "### Éléments manquants",
            "",
            *missing_lines,
            "",
            "### Explication",
            "",
            feedback.get("feedback") or "—",
            "",
        ]
        if not feedback.get("correct") and row.get("course_slug"):
            code_prefix = f"{row['course_code']} — " if row.get("course_code") else ""
            lines += [f"*Cours concerné : {code_prefix}{row['course_title']}*", ""]
    return "\n".join(lines)


@router.get("/sessions/{session_id}/export.md")
async def export_session_markdown(
    session_id: int, db=Depends(get_db), user: User = Depends(require_user)  # noqa: B008
) -> Response:
    session = get_owned_session(db, session_id=session_id, user_id=user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Session pas encore terminée : rien à exporter.")

    session_questions = sorted(session.session_questions, key=lambda sq: sq.position)
    results = _build_results_rows(db, session_questions)
    content = _build_session_export_markdown(session, results)

    mode_slug = "exam" if session.mode.value == "exam" else "practice"
    date_slug = session.completed_at.strftime("%Y-%m-%d") if session.completed_at else "session"
    filename = f"jury-central_{_export_slug(session)}_{mode_slug}_{date_slug}.md"

    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

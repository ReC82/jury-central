"""Parcours Diplôme → Forme → Option (ticket #136, reprend la navigation demandée par #67).

Distinction imposée par le ticket, reflétée telle quelle dans ce registre :
- **diplôme** (CESS) → **forme** (CESS P, professionnel) → **option** officielle (OBG) ;
- une option rassemble des **matières** (`SubjectTrack`) : l'option elle-même (Informatique
  AMPCR) et les matières de la formation commune ;
- une matière contient des **cours/chapitres** (les UAA publiées en base — jamais déclarés ici).

Ce module ne crée aucun contenu : il relie le registre aux Subject/Module/UAA existants par
le **code de module** (stable) et calcule une progression à partir des seules actions
réellement enregistrées (sessions V1 corrigées). Un cours non publié n'existe pas pour
l'interface ; `planned_count` sert uniquement à afficher honnêtement « x disponibles sur y
prévus » — jamais un faux cours.

Persistance du choix : table `v1_user_pathways` pour un compte connecté, session signée
(`request.session`) pour un visiteur. Changer de parcours ne touche à aucune progression.
"""

from dataclasses import dataclass, field

from fastapi import Request
from sqlalchemy.orm import Session as DBSession

from app import models
from app.v1.francais_plan import FR20_SESSION_SCOPE
from app.v1.fse_plan import FSE17_SESSION_SCOPE
from app.v1.mc38_transversal import MC38_SESSION_SCOPE
from app.v1.models import (
    Question,
    QuestionnaireSession,
    QuestionVersion,
    SessionMode,
    SessionQuestion,
    SessionStatus,
    User,
    UserPathway,
)

SESSION_KEY = "jc_pathway"

# Seuil de réussite affiché pour un examen blanc : 50 % (seuil des épreuves CESS P documenté
# dans docs/content_plan_fse.md § 2). Indicatif — jamais présenté comme une note officielle.
EXAM_PASS_RATIO = 0.5

# Sessions transversales dont les questions couvrent plusieurs UAA : attribuées à l'UAA de
# révision qui les porte (MC38, FSE17, FR20), pas éclatées sur les cours couverts.
_SCOPE_TO_UAA_CODE = {
    MC38_SESSION_SCOPE: "MC38", FSE17_SESSION_SCOPE: "FSE17", FR20_SESSION_SCOPE: "FR20",
}


@dataclass(frozen=True)
class SubjectTrack:
    module_code: str
    role: str  # "option" | "commune"
    title: str
    tagline: str
    icon: str  # nom Bootstrap Icons (sans préfixe « bi- »)
    illustration: str  # chemin relatif à app/static
    theme: str  # clé de palette CSS (.jc-theme-<theme>)
    planned_count: int
    planned_note: str


@dataclass(frozen=True)
class OptionDef:
    key: str
    label: str
    short: str
    description: str
    tracks: tuple[SubjectTrack, ...]


@dataclass(frozen=True)
class FormDef:
    key: str
    label: str
    long_label: str
    description: str
    options: tuple[OptionDef, ...] = field(default_factory=tuple)

    @property
    def available(self) -> bool:
        return bool(self.options)


@dataclass(frozen=True)
class DiplomaDef:
    key: str
    label: str
    long_label: str
    description: str
    forms: tuple[FormDef, ...]

    @property
    def available(self) -> bool:
        return any(form.available for form in self.forms)


AMPCR_TRACK = SubjectTrack(
    module_code="AMPCR",
    role="option",
    title="Informatique — maintenance PC-réseaux",
    tagline="Matériel, systèmes, réseaux et dépannage : le cœur de l'option.",
    icon="pc-display",
    illustration="img/parcours/informatique.webp",
    theme="info",
    planned_count=38,
    planned_note="38 mini-cours prévus (MC01→MC38)",
)
FRANCAIS_TRACK = SubjectTrack(
    module_code="FRANCAIS",
    role="commune",
    title="Français",
    tagline="Lire, comprendre, justifier et écrire comme à l'examen.",
    icon="book",
    illustration="img/parcours/francais.webp",
    theme="fr",
    planned_count=20,
    planned_note="20 mini-cours prévus (FR01→FR20)",
)
FSE_TRACK = SubjectTrack(
    module_code="FSE",
    role="commune",
    title="Formation sociale et économique",
    tagline="Médias, citoyenneté et État : comprendre la société.",
    icon="people",
    illustration="img/parcours/fse.webp",
    theme="fse",
    planned_count=17,
    planned_note="17 mini-cours prévus (FSE01→FSE17)",
)

AMPCR_OPTION = OptionDef(
    key="ampcr",
    label="Assistant/Assistante de maintenance PC-réseaux",
    short="AMPCR",
    description=(
        "Option de base groupée du CESS professionnel. Ton parcours rassemble l'option "
        "et les matières de la formation commune déjà présentes sur Jury Central."
    ),
    tracks=(AMPCR_TRACK, FRANCAIS_TRACK, FSE_TRACK),
)

REGISTRY: tuple[DiplomaDef, ...] = (
    DiplomaDef(
        key="cess",
        label="CESS",
        long_label="Certificat d'enseignement secondaire supérieur",
        description="Le diplôme de fin de secondaire, présenté devant le Jury de la FWB.",
        forms=(
            FormDef(
                key="p",
                label="CESS P",
                long_label="Enseignement professionnel",
                description="Formation commune + une option qualifiante.",
                options=(AMPCR_OPTION,),
            ),
            FormDef(
                key="g",
                label="CESS G",
                long_label="Enseignement général",
                description="Pas encore de contenu sur Jury Central.",
            ),
            FormDef(
                key="tq",
                label="CESS TQ",
                long_label="Technique de qualification",
                description="Pas encore de contenu sur Jury Central.",
            ),
        ),
    ),
)

# Modules présents en base mais pas (encore) rattachés à une option du registre : affichés
# honnêtement comme « autres contenus », jamais insérés dans un parcours sans confirmation.
OTHER_MODULE_CODES = ("MB32",)


def get_diploma(key: str | None) -> DiplomaDef | None:
    return next((d for d in REGISTRY if d.key == key), None)


def get_form(diploma: DiplomaDef | None, key: str | None) -> FormDef | None:
    if diploma is None:
        return None
    return next((f for f in diploma.forms if f.key == key), None)


def get_option(form: FormDef | None, key: str | None) -> OptionDef | None:
    if form is None:
        return None
    return next((o for o in form.options if o.key == key), None)


@dataclass(frozen=True)
class ResolvedPathway:
    diploma: DiplomaDef
    form: FormDef
    option: OptionDef

    @property
    def keys(self) -> tuple[str, str, str]:
        return (self.diploma.key, self.form.key, self.option.key)


def resolve_keys(diploma_key: str | None, form_key: str | None, option_key: str | None):
    """`ResolvedPathway` si les trois clés désignent une option réellement disponible du
    registre, sinon `None` (clé inconnue, forme sans contenu, cookie altéré…)."""
    diploma = get_diploma(diploma_key)
    form = get_form(diploma, form_key)
    option = get_option(form, option_key)
    if option is None:
        return None
    return ResolvedPathway(diploma=diploma, form=form, option=option)


def get_saved_pathway(request: Request, db: DBSession, user: User | None):
    """Compte connecté : la table fait foi ; à défaut (ou visiteur) : la session signée."""
    if user is not None:
        row = db.query(UserPathway).filter_by(user_id=user.id).first()
        if row is not None:
            resolved = resolve_keys(row.diploma_key, row.form_key, row.option_key)
            if resolved is not None:
                return resolved
    stored = request.session.get(SESSION_KEY) or {}
    return resolve_keys(stored.get("diploma"), stored.get("form"), stored.get("option"))


def has_stored_pathway(db: DBSession, user: User) -> bool:
    return db.query(UserPathway.id).filter_by(user_id=user.id).first() is not None


def save_pathway(request: Request, db: DBSession, user: User | None, pathway: ResolvedPathway):
    diploma_key, form_key, option_key = pathway.keys
    request.session[SESSION_KEY] = {
        "diploma": diploma_key,
        "form": form_key,
        "option": option_key,
    }
    if user is None:
        return
    row = db.query(UserPathway).filter_by(user_id=user.id).first()
    if row is None:
        row = UserPathway(user_id=user.id)
        db.add(row)
    row.diploma_key, row.form_key, row.option_key = diploma_key, form_key, option_key
    db.commit()


# --- Progression réelle -----------------------------------------------------------------


def listed_uaas(module: models.Module) -> list[models.UAA]:
    """Cours réellement proposés d'un module — même filtre que `module_detail.html`."""
    return sorted(
        (u for u in module.uaas if u.is_published and not u.hidden_from_listing),
        key=lambda u: (u.position, u.id),
    )


def _session_uaa_ids(db: DBSession, sessions: list[QuestionnaireSession]) -> dict[int, set[int]]:
    if not sessions:
        return {}
    rows = (
        db.query(SessionQuestion.session_id, Question.uaa_id)
        .join(QuestionVersion, QuestionVersion.id == SessionQuestion.question_version_id)
        .join(Question, Question.id == QuestionVersion.question_id)
        .filter(SessionQuestion.session_id.in_([s.id for s in sessions]))
        .distinct()
        .all()
    )
    mapping: dict[int, set[int]] = {}
    for session_id, uaa_id in rows:
        if uaa_id is not None:
            mapping.setdefault(session_id, set()).add(uaa_id)
    return mapping


def user_uaa_progress(db: DBSession, user: User | None) -> dict[int, dict]:
    """Par UAA : entraînements corrigés, meilleur examen blanc (ratio), session en cours.

    Seules des actions enregistrées comptent (« consulté » reste côté navigateur, voir
    `progress.js`) : un entraînement compte s'il a été corrigé (COMPLETED), un examen blanc
    est « réussi » si son meilleur score atteint `EXAM_PASS_RATIO` — une correction
    incomplète ne compte jamais comme réussite."""
    if user is None:
        return {}
    sessions = (
        db.query(QuestionnaireSession)
        .filter_by(user_id=user.id)
        # Ticket #137 : une partie de quiz n'est ni un entraînement ni un examen blanc.
        # Ticket #75 : un renforcement ciblé non plus.
        .filter(QuestionnaireSession.mode.notin_((SessionMode.QUIZ, SessionMode.REINFORCEMENT)))
        .order_by(QuestionnaireSession.created_at.desc())
        .all()
    )
    uaa_by_code = {}
    scoped = [s for s in sessions if (s.parameters_json or {}).get("scope") in _SCOPE_TO_UAA_CODE]
    if scoped:
        codes = set(_SCOPE_TO_UAA_CODE.values())
        uaa_by_code = {
            u.code: u.id for u in db.query(models.UAA).filter(models.UAA.code.in_(codes)).all()
        }
    session_uaas = _session_uaa_ids(db, [s for s in sessions if s not in scoped])

    progress: dict[int, dict] = {}
    for session in sessions:
        scope = (session.parameters_json or {}).get("scope")
        if scope in _SCOPE_TO_UAA_CODE:
            uaa_id = uaa_by_code.get(_SCOPE_TO_UAA_CODE[scope])
            uaa_ids = {uaa_id} if uaa_id else set()
        else:
            uaa_ids = session_uaas.get(session.id, set())
        if len(uaa_ids) != 1:
            continue  # parcours global multi-cours : pas attribué à un cours précis
        entry = progress.setdefault(
            next(iter(uaa_ids)),
            {"practice_done": 0, "exam_best": None, "in_progress_session_id": None},
        )
        if session.status == SessionStatus.IN_PROGRESS:
            if entry["in_progress_session_id"] is None:  # la plus récente (tri desc)
                entry["in_progress_session_id"] = session.id
            continue
        if session.status != SessionStatus.COMPLETED or session.score is None:
            continue
        if session.mode == SessionMode.PRACTICE:
            entry["practice_done"] += 1
        elif session.question_count:
            ratio = session.score / session.question_count
            if entry["exam_best"] is None or ratio > entry["exam_best"]:
                entry["exam_best"] = ratio
    return progress


def uaa_state(entry: dict | None) -> dict:
    """Libellés distincts, jamais confondus : entraîné ≠ examen blanc réussi."""
    entry = entry or {}
    exam_best = entry.get("exam_best")
    return {
        "practice_done": entry.get("practice_done", 0),
        "exam_best_pct": None if exam_best is None else round(exam_best * 100),
        "exam_passed": exam_best is not None and exam_best >= EXAM_PASS_RATIO,
        "in_progress_session_id": entry.get("in_progress_session_id"),
    }


def build_track_view(db: DBSession, track: SubjectTrack, progress: dict[int, dict]) -> dict | None:
    module = db.query(models.Module).filter_by(code=track.module_code).first()
    if module is None:
        return None
    uaas = listed_uaas(module)
    courses = [{"uaa": uaa, "state": uaa_state(progress.get(uaa.id))} for uaa in uaas]
    practiced = sum(1 for c in courses if c["state"]["practice_done"])
    passed = sum(1 for c in courses if c["state"]["exam_passed"])
    next_course = next((c for c in courses if not c["state"]["practice_done"]), None)
    return {
        "track": track,
        "module": module,
        "subject": module.subject,
        "courses": courses,
        "available_count": len(uaas),
        "planned_count": max(track.planned_count, len(uaas)),
        "practiced_count": practiced,
        "passed_count": passed,
        "practiced_pct": round(100 * practiced / len(uaas)) if uaas else 0,
        "next_course": next_course,
    }


def build_dashboard(db: DBSession, pathway: ResolvedPathway, user: User | None) -> dict:
    progress = user_uaa_progress(db, user)
    tracks = [
        view
        for view in (build_track_view(db, t, progress) for t in pathway.option.tracks)
        if view is not None
    ]
    resume = None
    for view in tracks:
        for course in view["courses"]:
            session_id = course["state"]["in_progress_session_id"]
            if session_id is not None:
                resume = {"course": course, "view": view, "session_id": session_id}
                break
        if resume:
            break
    next_step = None
    if resume is None and tracks:
        view = next((v for v in tracks if v["next_course"]), tracks[0])
        course = view["next_course"] or (view["courses"][0] if view["courses"] else None)
        if course is not None:
            next_step = {"course": course, "view": view}
    others = [
        m
        for m in db.query(models.Module).filter(models.Module.code.in_(OTHER_MODULE_CODES)).all()
        if listed_uaas(m)
    ]
    return {
        "pathway": pathway,
        "tracks": tracks,
        "resume": resume,
        "next_step": next_step,
        "other_modules": others,
        "has_activity": bool(progress),
    }


def track_for_module(module_code: str) -> SubjectTrack | None:
    for diploma in REGISTRY:
        for form in diploma.forms:
            for option in form.options:
                for track in option.tracks:
                    if track.module_code == module_code:
                        return track
    return None


def has_v1_sessions(uaa: models.UAA) -> bool:
    """Entraînement/examen blanc V1 réellement branchés (mêmes gardes que `app.main`)."""
    from app.v1.ampcr_plan import get_plan_by_slug
    from app.v1.francais_plan import get_francais_plan_by_slug
    from app.v1.fse_plan import get_fse_plan_by_slug

    return (
        get_plan_by_slug(uaa.slug) is not None
        or get_francais_plan_by_slug(uaa.slug) is not None
        or get_fse_plan_by_slug(uaa.slug) is not None
    )

"""Plan Français V1 — première UAA pilote (ticket #47).

Contrairement à AMPCR (38 mini-cours déjà cadrés par ChatGPT dans les tickets #55/#56),
**aucun contenu Français n'existait dans le dépôt** au moment de ce ticket : aucune
Subject « Français », aucun `SourceDocument`, aucun cours (confirmé par
`docs/content_plan_informatique_francais.md` § 3.3 et par une recherche exhaustive du
dépôt). Face à ce constat, l'utilisateur a validé explicitement (ticket #47, recadrage) la
création d'**une première UAA pilote, marquée comme contenu de validation technique
provisoire** (`app.v1.francais_content`, texte original rédigé pour ce ticket, jamais
présenté comme un examen CESS officiel), pour prouver que tout le parcours fonctionne
avant qu'un vrai corpus pédagogique ne soit fourni.

Ce module suit EXACTEMENT le même schéma que `app.v1.ampcr_plan` (même pattern déjà
utilisé et validé, pas une nouvelle structure) : un petit registre code→titre→contexte,
consulté par `app.v1.session_service`/`app.v1.routes_sessions`/`app.main` de la même
façon que le registre AMPCR."""

from dataclasses import dataclass

from app.ai.schemas import PedagogicalContext

FRANCAIS_SUBJECT_NAME = "Français"
# Code court en majuscules, comme AMPCR_MODULE_CODE ("AMPCR") — donne, via le même
# mécanisme `slugify(f"{module.code}-{uaa.code}")` que `_seed_uaa` (app/seed.py) et le
# reste du projet (ticket #10), le slug attendu "francais-c01" pour la première UAA.
FRANCAIS_MODULE_CODE = "FRANCAIS"
FRANCAIS_MODULE_TITLE = "Français — CESS Professionnel"


@dataclass(frozen=True)
class FrancaisUAAPlan:
    code: str
    title: str

    @property
    def slug(self) -> str:
        return f"francais-{self.code.lower()}"

    @property
    def course_key(self) -> str:
        return f"francais-{self.code.lower()}"


# Une seule UAA pilote pour ce ticket (voir docstring du module : contenu de validation
# technique provisoire, pas un découpage CESS officiel).
FRANCAIS_PLAN: tuple[FrancaisUAAPlan, ...] = (
    FrancaisUAAPlan(
        code="C01",
        title="Lecture et compréhension — texte d'exemple (validation technique, provisoire)",
    ),
)

FRANCAIS_PLAN_BY_CODE: dict[str, FrancaisUAAPlan] = {plan.code: plan for plan in FRANCAIS_PLAN}
FRANCAIS_PLAN_BY_SLUG: dict[str, FrancaisUAAPlan] = {plan.slug: plan for plan in FRANCAIS_PLAN}


def get_francais_plan_by_slug(uaa_slug: str) -> FrancaisUAAPlan | None:
    return FRANCAIS_PLAN_BY_SLUG.get(uaa_slug)


def _build_context(plan: FrancaisUAAPlan) -> PedagogicalContext:
    return PedagogicalContext(
        course_key=plan.course_key,
        course_title=plan.title,
        level="CESS Professionnel — niveau de lecture/compréhension standard",
        allowed_notions=[
            "compréhension à la lecture (explicite et implicite)",
            "justification à l'aide d'éléments du texte",
            "reformulation",
            "identification de l'idée principale et synthèse courte",
            "distinction entre fait et opinion",
            "vocabulaire en contexte",
            "opinion argumentée",
            "analyse documentaire (citer et interpréter un passage)",
            "comparaison entre deux documents",
        ],
        competencies=[
            "Lire et comprendre un texte informatif de niveau CESS",
            "Justifier une réponse à l'aide d'éléments précis du texte",
            "Rédiger une réponse argumentée structurée",
        ],
        vocabulary=[],
        constraints=(
            "IMPORTANT — contenu de validation technique provisoire (ticket #47), PAS un "
            "examen CESS officiel : le texte support est original, rédigé spécifiquement "
            "pour tester le parcours. Reste strictement dans le contenu du ou des "
            "documents fournis dans le contexte de correction — n'invente jamais de fait "
            "absent du texte, ne récompense jamais une réponse hors sujet même si elle "
            "est bien écrite. Niveau adapté à un·e élève de CESS Professionnel."
        ),
    )


FRANCAIS_CONTEXTS: dict[str, PedagogicalContext] = {
    plan.course_key: _build_context(plan) for plan in FRANCAIS_PLAN
}


def get_francais_context(course_key: str) -> PedagogicalContext | None:
    return FRANCAIS_CONTEXTS.get(course_key)

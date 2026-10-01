"""Plan Formation sociale et économique (FSE) — CESS Professionnel (ticket #96).

Contexte : aucune matière « Formation sociale et économique » n'existait dans le dépôt
avant ce ticket (confirmé par une recherche exhaustive du dépôt — aucune `Subject`, aucun
`Module`, aucune UAA). Le périmètre complet (17 mini-cours FSE01→FSE17, voir le ticket
#96 § Plan) est fixé par ChatGPT (chef de projet) ; seul FSE01 est livré avec un contenu
réellement rédigé par ce ticket (cahier des charges détaillé du ticket #97) — les
FSE02→FSE17 restent documentés (titre, thème, pages du programme) pour les tickets
suivants, mais ne sont PAS seedés en base tant qu'ils n'ont pas de contenu réel : même
principe que `app.v1.francais_plan` (ticket #94 PHASE A, FR01→FR05 seuls dans
`FRANCAIS_PLAN` au moment de leur rédaction, FR06→FR20 ajoutés phase par phase) — jamais
un cours vide présenté comme disponible (`docs/PROJECT_RULES.md` § 5/§ 10).

Ce module suit EXACTEMENT le même schéma que `app.v1.francais_plan`/`app.v1.ampcr_plan`
(registre code→titre→contexte pédagogique borné), consulté par
`app.v1.session_service`/`app.v1.routes_sessions`/`app.main` de la même façon."""

from dataclasses import dataclass

from app.ai.schemas import PedagogicalContext

FSE_SUBJECT_NAME = "Formation sociale et économique"
FSE_MODULE_CODE = "FSE"


@dataclass(frozen=True)
class FSEUAAPlan:
    code: str
    title: str
    # Regroupement thématique du programme officiel (ticket #96 § Plan) — métadonnée
    # d'information uniquement (pas une hiérarchie DB supplémentaire, voir
    # `docs/content_workflow.md` : Subject → Module → UAA reste la seule hiérarchie
    # persistée) : "Médias" (Interactions médiatiques, programme p. 41-47) ou "Citoyen"
    # (Le citoyen et l'État, programme p. 56-64).
    theme: str
    program_pages: str
    allowed_notions: tuple[str, ...]
    competencies: tuple[str, ...]

    @property
    def slug(self) -> str:
        return f"fse-{self.code.lower()}"

    @property
    def course_key(self) -> str:
        return f"fse-{self.code.lower()}"


# Ticket #96/#97 : seul FSE01 est rédigé par ce ticket. Le reste du plan officiel
# (FSE02→FSE17, § Plan du ticket #96) est documenté dans `docs/content_plan_fse.md` —
# jamais ajouté ici tant qu'il n'a pas de contenu réel associé (voir docstring du module).
FSE_PLAN: tuple[FSEUAAPlan, ...] = (
    FSEUAAPlan(
        code="FSE01",
        title="Communiquer : le schéma de communication",
        theme="Interactions médiatiques (Médias)",
        program_pages="programme 474/2016/240, p. 43-45",
        allowed_notions=(
            "émetteur et récepteur d'un message",
            "message, code et canal (support/contact)",
            "contexte (référent) d'une communication",
            "distinction entre canal (support de transmission) et code (système de signes utilisé)",
            "schéma de la communication appliqué à un mail, une affiche et une publication sur réseau social",
            "obstacle/bruit qui perturbe la transmission d'un message",
            "rétroaction (réponse du récepteur à l'émetteur) et ses limites selon le canal",
        ),
        competencies=(
            "Identifier émetteur, récepteur, message, code, canal et contexte dans une situation de communication réelle",
            "Distinguer canal et code dans un mail, une affiche ou une publication sur réseau social",
            "Expliquer comment un obstacle (bruit) perturbe une communication et quelles conséquences il entraîne",
            "Reconnaître la rétroaction disponible (ou son absence) selon le canal utilisé",
        ),
    ),
)

FSE_PLAN_BY_CODE: dict[str, FSEUAAPlan] = {plan.code: plan for plan in FSE_PLAN}
FSE_PLAN_BY_SLUG: dict[str, FSEUAAPlan] = {plan.slug: plan for plan in FSE_PLAN}


def get_fse_plan_by_slug(uaa_slug: str) -> FSEUAAPlan | None:
    return FSE_PLAN_BY_SLUG.get(uaa_slug)


def _build_context(plan: FSEUAAPlan) -> PedagogicalContext:
    return PedagogicalContext(
        course_key=plan.course_key,
        course_title=plan.title,
        level="CESS Professionnel — Formation sociale et économique, niveau standard",
        allowed_notions=list(plan.allowed_notions),
        competencies=list(plan.competencies),
        vocabulary=[],
        constraints=(
            "PÉRIMÈTRE STRICT (consignes CESS P 2026-2027/1, ticket #96) : reste "
            "exclusivement dans les notions listées ci-dessus — n'évalue et ne valorise "
            "jamais une connaissance de budget familial, crédits, emprunts, TAEG, IPP, "
            "fiscalité immobilière, ou toute autre notion hors de ce mini-cours. Les "
            "exemples (mail, affiche, publication sur réseau social) sont originaux, "
            "rédigés pour ce cours : ne jamais inventer de fait, d'organisme ou de règle "
            "juridique absent du support fourni. Niveau adapté à un·e élève de CESS "
            "Professionnel qui reprend ses études."
        ),
    )


FSE_CONTEXTS: dict[str, PedagogicalContext] = {plan.course_key: _build_context(plan) for plan in FSE_PLAN}


def get_fse_context(course_key: str) -> PedagogicalContext | None:
    return FSE_CONTEXTS.get(course_key)

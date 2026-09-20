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


_DEFAULT_NOTIONS = [
    "compréhension à la lecture (explicite et implicite)",
    "justification à l'aide d'éléments du texte",
    "reformulation",
    "identification de l'idée principale et synthèse courte",
    "distinction entre fait et opinion",
    "vocabulaire en contexte",
    "opinion argumentée",
    "analyse documentaire (citer et interpréter un passage)",
    "comparaison entre deux documents",
]
_DEFAULT_COMPETENCIES = [
    "Lire et comprendre un texte informatif de niveau CESS",
    "Justifier une réponse à l'aide d'éléments précis du texte",
    "Rédiger une réponse argumentée structurée",
]


@dataclass(frozen=True)
class FrancaisUAAPlan:
    code: str
    title: str
    # Ticket #94 : chaque FRxx cible des notions précises (§ objectifs donnés par
    # l'utilisateur/ChatGPT) — `None` = reprend les notions génériques historiques de C01
    # (ticket #47), pour ne rien changer à son comportement existant.
    allowed_notions: tuple[str, ...] | None = None
    competencies: tuple[str, ...] | None = None

    @property
    def slug(self) -> str:
        return f"francais-{self.code.lower()}"

    @property
    def course_key(self) -> str:
        return f"francais-{self.code.lower()}"


# Ticket #94 (PHASE A) : parcours des 20 mini-cours Français CESS Professionnel — les
# titres FR01→FR05 ci-dessous reprennent EXACTEMENT les intitulés fournis par
# l'utilisateur/ChatGPT (ticket #94 § 2, non réinventés). C01 (ticket #47) reste
# INCHANGÉE — contenu de validation technique provisoire distinct, jamais renommé ni
# supprimé, pour ne casser aucun test/usage existant. FR06→FR20 seront ajoutés par les
# phases B/C/D suivantes (voir docs/claude-reports/2026-09-20_ticket-94_french-20-course-path.md).
FRANCAIS_PLAN: tuple[FrancaisUAAPlan, ...] = (
    FrancaisUAAPlan(
        code="C01",
        title="Lecture et compréhension — texte d'exemple (validation technique, provisoire)",
    ),
    FrancaisUAAPlan(
        code="FR01", title="Comprendre une consigne d'examen",
        allowed_notions=(
            ("verbe opérateur d'une consigne (relever, citer, reformuler, expliquer, "
            "justifier, expliciter, comparer, analyser, résumer, synthétiser, "
            "argumenter, apprécier)"),
            ("décomposition d'une consigne en checklist (objet, contraintes, nombre "
            "d'éléments, documents à utiliser, destinataire, genre, longueur)"),
            "détection du hors-sujet et de la réponse partielle",
        ),
        competencies=(
            "Décoder précisément ce qu'une consigne demande avant d'y répondre",
            "Répondre à CHAQUE exigence d'une consigne à plusieurs parties, sans en oublier",
            "Comparer deux documents sur un point précis demandé par la consigne",
        ),
    ),
    FrancaisUAAPlan(
        code="FR02", title="Lire et comprendre un document",
        allowed_notions=(
            ("situation de communication (auteur/énonciateur, destinataire, intention, "
            "contexte, support, genre)"),
            "stratégies de lecture (survol, repérage, lecture sélective/intégrale)",
            "idée principale et idées secondaires",
            "sens explicite et vocabulaire en contexte",
        ),
        competencies=(
            "Identifier la situation de communication d'un document",
            "Dégager l'idée principale et les idées secondaires d'un texte",
            "Expliquer le sens d'un mot ou d'une expression à partir du contexte",
        ),
    ),
    FrancaisUAAPlan(
        code="FR03", title="Implicite, inférences et justification",
        allowed_notions=(
            "distinction explicite / implicite",
            "méthode INDICE → RAISONNEMENT → CONCLUSION",
            "méthode PREUVE → EXPLICATION → CONCLUSION",
            "inférence appuyée sur le texte, jamais une invention",
        ),
        competencies=(
            "Distinguer ce qui est écrit explicitement de ce qui doit être déduit",
            "Justifier une inférence à l'aide d'un indice précis du texte",
            "Refuser toute conclusion qui n'est pas appuyée par un indice réel du texte",
        ),
    ),
    FrancaisUAAPlan(
        code="FR04", title="Écrire correctement et organiser ses idées",
        allowed_notions=(
            "situation de communication d'un texte à produire (destinataire, intention, genre, registre)",
            "planification et ordre logique des idées",
            "paragraphes, progression et connecteurs logiques",
            "introduction et conclusion",
        ),
        competencies=(
            "Organiser des idées en vrac en un texte structuré",
            "Réordonner des paragraphes désorganisés selon une logique claire",
            "Rédiger un texte adapté à une situation de communication donnée",
        ),
    ),
    FrancaisUAAPlan(
        code="FR05", title="Corriger et améliorer un texte",
        allowed_notions=(
            "révision méthodique (repérer, corriger, remplacer, supprimer, ajouter, déplacer)",
            "cohérence, répétitions et connecteurs",
            "accords, homophones et ponctuation",
            "registre et lexique adaptés à la situation",
        ),
        competencies=(
            "Repérer des erreurs réelles dans un texte (accords, homophones, ponctuation)",
            "Corriger un texte sans en changer le sens ni ajouter d'information absente",
            "Adapter le registre d'un texte à une situation professionnelle",
        ),
    ),
    # Ticket #94 PHASE B : FR06→FR10.
    FrancaisUAAPlan(
        code="FR06", title="Rechercher et sélectionner l'information",
        allowed_notions=(
            "sommaire, index, dictionnaire, encyclopédie, article, site, ressource multimédia/hypermédia",
            "survol, repérage, lecture sélective",
            "pertinence d'une source par rapport à une question de recherche",
            "fiche-source et trace de recherche",
        ),
        competencies=(
            "Transformer un sujet en questions de recherche et mots-clés",
            "Choisir une source adaptée et juger sa pertinence par survol",
            "Repérer une information précise et la noter dans une fiche-source",
        ),
    ),
    FrancaisUAAPlan(
        code="FR07", title="Évaluer une source et sa fiabilité",
        allowed_notions=(
            "auteur/organisme, expertise, éditeur/site, date, méthode/références, objectif déclaré vs réel",
            "fait, opinion, témoignage, publicité, argument",
            "biais et recoupement",
            "différence entre pertinence et fiabilité",
        ),
        competencies=(
            "Évaluer la fiabilité d'une source à partir de critères précis",
            "Distinguer fait, opinion, témoignage et publicité dans un même texte",
            "Recouper une information avec une autre source indépendante",
        ),
    ),
    FrancaisUAAPlan(
        code="FR08", title="Réduire et résumer un texte",
        allowed_notions=(
            "réduction, résumé, paraphrase, commentaire",
            "idée principale, idées secondaires, hiérarchisation",
            "condensation, reformulation, fidélité, neutralité",
            "longueur imposée",
        ),
        competencies=(
            "Hiérarchiser l'idée principale et les idées secondaires d'un texte",
            "Résumer un texte par reformulation, jamais par copie",
            "Respecter une longueur imposée en restant fidèle et neutre",
        ),
    ),
    FrancaisUAAPlan(
        code="FR09", title="Synthétiser plusieurs documents",
        allowed_notions=(
            "différence entre résumé et synthèse",
            "points communs, compléments, divergences, nuances entre documents",
            "plan thématique personnel (jamais un plan par document)",
            "patchwork à éviter",
        ),
        competencies=(
            "Confronter plusieurs documents pour en dégager des relations (commun/complément/divergence/nuance)",
            "Organiser une synthèse selon un plan thématique personnel",
            "Éviter le plan par document (D1/D2/D3) et le patchwork",
        ),
    ),
    FrancaisUAAPlan(
        code="FR10", title="Comprendre thèse, arguments et preuves",
        allowed_notions=(
            "thème, thèse explicite/implicite, argument, exemple, preuve/donnée, contre-argument, conclusion",
            "solidité d'un argument (donnée précise vs impression)",
            "généralisation hâtive, arguments répétitifs, attaque personnelle simple",
            "argument vs exemple",
        ),
        competencies=(
            "Identifier la thèse (explicite ou implicite) d'un texte argumentatif",
            "Distinguer argument, exemple et preuve",
            "Évaluer la solidité d'un argument et repérer ses faiblesses",
        ),
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
        allowed_notions=list(plan.allowed_notions) if plan.allowed_notions is not None else list(_DEFAULT_NOTIONS),
        competencies=list(plan.competencies) if plan.competencies is not None else list(_DEFAULT_COMPETENCIES),
        vocabulary=[],
        constraints=(
            "IMPORTANT — contenu de validation technique provisoire (tickets #47/#94), "
            "PAS un examen CESS officiel : les textes support sont originaux, rédigés "
            "spécifiquement pour ce parcours. Reste strictement dans le contenu du ou des "
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

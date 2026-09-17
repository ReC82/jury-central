"""Plan complet AMPCR (MC01→MC38) et contextes pédagogiques V1 associés (ticket #55,
recadrage « INFORMATIQUE AMPCR COMPLET »).

**Autorité pédagogique** : les 38 codes/titres/catégories ci-dessous sont ceux fournis
directement par ChatGPT (chef de projet) dans le corps du ticket #55 — même modalité de
traçabilité déjà appliquée à MC01/MC02/MC03 (cahier des charges dans le ticket GitHub,
voir `docs/content_plan_informatique_francais.md`, § 0). Ce module ne redéfinit jamais ce
qui doit être enseigné : il STRUCTURE la liste fournie.

**Limite assumée et documentée (voir aussi le rapport de ticket)** : MC01/MC02/MC03
disposent d'un contenu pédagogique réellement rédigé (`app/ai/context.py::
PEDAGOGICAL_CONTEXTS`, cahiers des charges des tickets #10/#12/#14) — leurs contextes sont
repris ici tels quels. MC04 à MC38 n'ont, à ce jour, aucun contenu pédagogique rédigé dans
ce dépôt (confirmé par `docs/content_plan_informatique_francais.md`, § 3.2 : « aucune
source officielle, aucun brouillon ChatGPT déposé ») — leurs contextes ci-dessous ne
contiennent que le TITRE déjà fourni par ChatGPT, sans notions détaillées inventées : `Claude
ne redéfinit jamais le contenu pédagogique` (règle du projet) s'applique aussi à ce
ticket. Ces contextes bornent volontairement l'IA au sujet du titre pour empêcher toute
dérive hors programme, mais restent MINIMAUX et attendent une revue/un enrichissement par
ChatGPT avant tout usage à grande échelle — voir
`docs/ampcr_v1_functional.md`, colonne `bank_seed`."""

from dataclasses import dataclass

from app.ai.context import PEDAGOGICAL_CONTEXTS
from app.ai.schemas import PedagogicalContext

AMPCR_MODULE_CODE = "AMPCR"

# Types recommandés par catégorie (§ 7 du ticket #55 : « ne fais pas 38 questionnaires
# composés uniquement de long_answer ») — utilisé par la sélection/génération de session
# (voir `app/v1/session_service.py::compose_question_types`) comme préférence, jamais une
# contrainte stricte.
_RECOMMENDED_TYPES_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "hardware": ("multiple_choice", "classification", "vocabulary", "diagnostic", "true_false"),
    "systems": ("multiple_choice", "ordering", "short_answer", "true_false", "diagnostic"),
    "networks": ("numeric", "calculation", "multiple_choice", "short_answer", "classification"),
    "wifi": ("multiple_choice", "true_false", "vocabulary", "short_answer"),
    "security": ("multiple_choice", "true_false", "diagnostic", "short_answer"),
    "troubleshooting": ("diagnostic", "troubleshooting", "ordering", "multiple_choice"),
    "professional": ("short_answer", "multiple_choice", "true_false", "classification"),
    "final": ("multiple_choice", "classification", "ordering", "short_answer", "diagnostic", "numeric"),
}


@dataclass(frozen=True)
class AMPCRModulePlan:
    code: str  # "MC01".."MC38"
    title: str
    category: str  # hardware/systems/networks/wifi/security/troubleshooting/professional/final
    has_authored_content: bool  # True seulement pour MC01/MC02/MC03 (contenu réellement rédigé)

    @property
    def course_key(self) -> str:
        return f"ampcr-{self.code.lower()}"

    @property
    def recommended_types(self) -> tuple[str, ...]:
        return _RECOMMENDED_TYPES_BY_CATEGORY[self.category]


# Titres et catégories fournis verbatim par ChatGPT (ticket #55) — ne jamais reformuler.
_PLAN_ROWS: tuple[tuple[str, str, str], ...] = (
    ("MC01", "Architecture générale d'un PC", "hardware"),
    ("MC02", "Carte mère, formats, bus et connectiques", "hardware"),
    ("MC03", "Processeur et mémoire RAM", "hardware"),
    ("MC04", "Stockage : HDD, SSD SATA et NVMe", "hardware"),
    ("MC05", "Alimentation, refroidissement, ESD et sécurité électrique", "hardware"),
    ("MC06", "Montage, démontage et reconditionnement d'un PC", "hardware"),
    ("MC07", "BIOS, UEFI, POST et démarrage", "systems"),
    ("MC08", "Partitionnement, GPT/MBR et formatage", "systems"),
    ("MC09", "Installer Windows proprement", "systems"),
    ("MC10", "Windows : administration et commandes essentielles", "systems"),
    ("MC11", "Linux : bases utiles au technicien PC-réseaux", "systems"),
    ("MC12", "Pilotes, périphériques et logiciels", "systems"),
    ("MC13", "Fondamentaux réseau : LAN, WAN, OSI et TCP/IP", "networks"),
    ("MC14", "Équipements réseau : switch, routeur, point d'accès, modem", "networks"),
    ("MC15", "Câblage Ethernet et RJ45 : T568A/T568B", "networks"),
    ("MC16", "IPv4 : adresses, masque, passerelle et plages privées", "networks"),
    ("MC17", "Subnetting 1 : masques et CIDR", "networks"),
    ("MC18", "Subnetting 2 : réseau, broadcast et exercices avancés", "networks"),
    ("MC19", "DHCP : attribution automatique des paramètres IP", "networks"),
    ("MC20", "DNS, ARP et ICMP", "networks"),
    ("MC21", "TCP, UDP et ports réseau", "networks"),
    ("MC22", "Internet, NAT/PAT et routage de base", "networks"),
    ("MC23", "Switching, topologies et segmentation", "networks"),
    ("MC24", "VLAN, trunk et réseau invité", "networks"),
    ("MC25", "Wi-Fi : normes, bandes, canaux et couverture", "wifi"),
    ("MC26", "Sécurité Wi-Fi : WPA2, WPA3, PSK, Enterprise", "wifi"),
    ("MC27", "Sécurité réseau traditionnelle", "security"),
    ("MC28", "Menaces informatiques et protection des postes", "security"),
    ("MC29", "Dépannage matériel : méthode et pannes courantes", "troubleshooting"),
    ("MC30", "Dépannage Windows et Linux", "troubleshooting"),
    ("MC31", "Dépannage réseau méthodique", "troubleshooting"),
    ("MC32", "Maintenance préventive et entretien", "troubleshooting"),
    ("MC33", "Partage de ressources, comptes, droits et permissions", "professional"),
    ("MC34", "Inventaire matériel et gestion simple des ressources", "professional"),
    ("MC35", "Ergonomie, sécurité, environnement et confidentialité", "professional"),
    ("MC36", "Communication client et rapport technique", "professional"),
    ("MC37", "Laboratoire intégrateur PC + réseau", "final"),
    ("MC38", "Révision finale et examen blanc AMPCR", "final"),
)

_AUTHORED_CODES = frozenset({"MC01", "MC02", "MC03"})

AMPCR_PLAN: tuple[AMPCRModulePlan, ...] = tuple(
    AMPCRModulePlan(code=code, title=title, category=category, has_authored_content=code in _AUTHORED_CODES)
    for code, title, category in _PLAN_ROWS
)

AMPCR_PLAN_BY_CODE: dict[str, AMPCRModulePlan] = {plan.code: plan for plan in AMPCR_PLAN}


def _minimal_context(plan: AMPCRModulePlan) -> PedagogicalContext:
    """Contexte minimal pour un MC sans contenu pédagogique rédigé (voir docstring du
    module) : ne contient QUE le titre déjà fourni par ChatGPT — jamais de notions
    détaillées inventées par ce ticket."""
    return PedagogicalContext(
        course_key=plan.course_key,
        course_title=plan.title,
        level="CESS Professionnel, filière Assistant/Assistante de maintenance PC-réseaux (AMPCR), niveau débutant",
        allowed_notions=[plan.title],
        competencies=[],
        vocabulary=[],
        constraints=(
            "Contexte minimal (ticket #55) : reste strictement dans le sujet exact du titre "
            f"« {plan.title} », niveau débutant. N'invente aucune notion technique au-delà de "
            "ce que ce titre couvre explicitement — ce contexte n'a pas encore été enrichi "
            "par un cahier des charges pédagogique détaillé."
        ),
    )


def _build_contexts() -> dict[str, PedagogicalContext]:
    contexts: dict[str, PedagogicalContext] = {}
    for plan in AMPCR_PLAN:
        if plan.has_authored_content and plan.course_key in PEDAGOGICAL_CONTEXTS:
            contexts[plan.course_key] = PEDAGOGICAL_CONTEXTS[plan.course_key]
        else:
            contexts[plan.course_key] = _minimal_context(plan)
    return contexts


AMPCR_CONTEXTS: dict[str, PedagogicalContext] = _build_contexts()


def get_ampcr_context(course_key: str) -> PedagogicalContext | None:
    return AMPCR_CONTEXTS.get(course_key)


def get_plan_by_slug(uaa_slug: str) -> AMPCRModulePlan | None:
    """`uaa_slug` attendu au format `ampcr-mc01`..`ampcr-mc38` (voir `app.slugify`,
    convention déjà utilisée par #10 : `slugify(f"{module.code}-{uaa.code}")`)."""
    prefix = "ampcr-"
    if not uaa_slug.startswith(prefix):
        return None
    return AMPCR_PLAN_BY_CODE.get(uaa_slug[len(prefix):].upper())

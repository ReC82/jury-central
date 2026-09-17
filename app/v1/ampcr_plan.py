"""Plan complet AMPCR (MC01→MC38) et contextes pédagogiques V1 associés (ticket #55,
recadrage « INFORMATIQUE AMPCR COMPLET », puis correctif de revue PR #56).

**Autorité pédagogique** : les 38 codes/titres/catégories ci-dessous sont ceux fournis
directement par ChatGPT (chef de projet) dans le corps du ticket #55 — même modalité de
traçabilité déjà appliquée à MC01/MC02/MC03 (cahier des charges dans le ticket GitHub,
voir `docs/content_plan_informatique_francais.md`, § 0). Ce module ne redéfinit jamais ce
qui doit être enseigné : il STRUCTURE la liste fournie.

**MC01/MC02/MC03** disposent d'un contenu pédagogique réellement rédigé (`app/ai/
context.py::PEDAGOGICAL_CONTEXTS`, cahiers des charges des tickets #10/#12/#14) — leurs
contextes sont repris ici tels quels, inchangés.

**MC04 à MC38** : la revue de la PR #56 a signalé que ces contextes se limitaient au seul
titre, insuffisant pour borner fiablement la génération avant l'examen. ChatGPT a alors
transmis l'objectif pédagogique EXACT de chaque mini-cours, tel que défini dans le plan
AMPCR validé (`_OBJECTIVES_BY_CODE` ci-dessous, reproduit verbatim, jamais reformulé ni
complété par une notion technique inventée par Claude). Chaque contexte MC04-38 combine
désormais : le titre, cet objectif exact, et les types de question déjà recommandés pour
sa catégorie (`_RECOMMENDED_TYPES_BY_CATEGORY`, inchangé depuis la livraison initiale du
ticket #55). Ces contextes restent volontairement plus sommaires que MC01-03 (pas de
cahier des charges complet, pas de vocabulaire FR/EN, pas de contraintes pédagogiques
détaillées) et attendent un enrichissement éditorial ultérieur — voir
`docs/ampcr_v1_functional.md`."""

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

# Objectifs pédagogiques EXACTS du plan AMPCR validé, transmis verbatim par ChatGPT
# (revue de la PR #56) pour les 38 mini-cours. Reproduits tels quels, jamais reformulés ni
# complétés par une notion technique inventée par Claude. MC01-03 sont listés ici pour
# traçabilité complète du plan mais conservent leur contexte riche existant
# (`PEDAGOGICAL_CONTEXTS`), plus détaillé que ce seul objectif.
_OBJECTIVES_BY_CODE: dict[str, str] = {
    "MC01": (
        "Comprendre l'architecture d'un ordinateur, le rôle CPU/RAM/stockage/carte "
        "mère/GPU/alimentation et leurs interactions."
    ),
    "MC02": "Sockets, chipsets, ATX/mATX/ITX, PCIe, SATA, M.2, USB, headers et alimentations ATX/EPS.",
    "MC03": "CPU, cœurs/threads/fréquence/cache, DDR3/4/5, dual channel, compatibilités et pannes courantes.",
    "MC04": "Technologies de stockage, interfaces, SMART, performances, fiabilité et sauvegarde.",
    "MC05": "PSU, puissance, connecteurs, pâte thermique, flux d'air, ESD et risques électriques.",
    "MC06": "Procédure complète, outils, contrôle, upgrade, réutilisation de composants et validation.",
    "MC07": "Firmware, POST, ordre de boot, Secure Boot, paramètres essentiels et dépannage de démarrage.",
    "MC08": "Partitions, volumes, EFI, NTFS/FAT32/exFAT/ext4, formatage et précautions.",
    "MC09": "Préparation, clé bootable, installation, pilotes, mises à jour, comptes et tests.",
    "MC10": "Arborescence, utilisateurs, permissions, services, périphériques, CMD et PowerShell.",
    "MC11": "Arborescence, utilisateurs, sudo, permissions, services, apt et commandes de diagnostic.",
    "MC12": "Drivers, périphériques inconnus, installation/désinstallation, compatibilité et conflits.",
    "MC13": "Types de réseaux, couches OSI/TCP-IP, encapsulation, trames, paquets et équipements.",
    "MC14": "Rôles, différences, table MAC, routage de base et réseau domestique/pro.",
    "MC15": "UTP/STP, catégories, paires torsadées, brochage, sertissage, droit/croisé et testeur.",
    "MC16": "IPv4, binaire utile, réseau/hôte, RFC1918, loopback, APIPA et passerelle.",
    "MC17": "/24 à /30, masques décimaux, incréments, nombre d'hôtes et méthode mentale.",
    "MC18": "Réseau/broadcast/plage, même sous-réseau, choix de masque et exercices contextualisés.",
    "MC19": "Bail DHCP, DORA, APIPA, réservations, dépannage et renouvellement.",
    "MC20": "Résolution de noms, cache DNS, ARP IPv4-MAC, ping/ICMP et diagnostic.",
    "MC21": "TCP/UDP, ports, sockets, HTTP(S), DNS, DHCP, SSH, RDP et services courants.",
    "MC22": "Passerelle, route par défaut, NAT/PAT, IP publique/privée et chemin vers Internet.",
    "MC23": "Étoile, broadcast, table MAC, domaines de collision/broadcast et segmentation.",
    "MC24": "VLAN, access, trunk 802.1Q, segmentation et cas simple d'entreprise.",
    "MC25": "802.11, 2,4/5/6 GHz, canaux, largeur, SSID/BSSID, interférences et roaming.",
    "MC26": "WEP/WPA/WPA2/WPA3, PSK, 802.1X/RADIUS, invité, isolation client et WPS.",
    "MC27": "Pare-feu, ACL, segmentation, 802.1X, port security, VPN, DMZ et moindre privilège.",
    "MC28": "Malware, ransomware, phishing, MITM, Evil Twin, MFA, sauvegardes et mises à jour.",
    "MC29": "PC mort, pas d'image, RAM, PSU, GPU, stockage, surchauffe et configuration minimale.",
    "MC30": "Logs, services, pilotes, lenteurs, SFC/DISM, journalctl/systemctl, stockage et mémoire.",
    "MC31": "Physique → IP → passerelle → Internet → DNS → application, avec commandes de test.",
    "MC32": "Nettoyage, températures, mises à jour, stockage, sauvegardes, inventaire et suivi.",
    "MC33": "Partage de dossiers/imprimantes, comptes, groupes, droits NTFS/partage et bonnes pratiques.",
    "MC34": (
        "Inventorier postes/composants, numéros de série, état, stock et notions simples "
        "de base de données."
    ),
    "MC35": (
        "Risques électriques/incendie, ergonomie, pictogrammes, tri DEEE, confidentialité "
        "et données clients."
    ),
    "MC36": "Questionner, expliquer simplement, vocabulaire FR/EN, fiche d'intervention et rapport.",
    "MC37": "Montage, OS, RJ45, IP, partage, Wi-Fi, sécurité et pannes volontaires dans un scénario complet.",
    "MC38": "Synthèse, fiches mémo, pièges, exercices transversaux et examen type qualification.",
}


def _detailed_context(plan: AMPCRModulePlan) -> PedagogicalContext:
    """Contexte pour un MC sans cahier des charges complet (MC04-38, voir docstring du
    module) : titre + objectif EXACT du plan AMPCR validé (`_OBJECTIVES_BY_CODE`) + types
    de question déjà recommandés pour sa catégorie — jamais de notion technique inventée
    au-delà de cet objectif transmis par ChatGPT."""
    objective = _OBJECTIVES_BY_CODE[plan.code]
    return PedagogicalContext(
        course_key=plan.course_key,
        course_title=plan.title,
        level="CESS Professionnel, filière Assistant/Assistante de maintenance PC-réseaux (AMPCR), niveau débutant",
        allowed_notions=[plan.title, objective],
        competencies=[
            f"Objectif du plan AMPCR pour {plan.code} : {objective}",
            f"Types de question adaptés à ce mini-cours : {', '.join(plan.recommended_types)}",
        ],
        vocabulary=[],
        constraints=(
            f"Reste strictement dans l'objectif pédagogique défini pour « {plan.title} » : "
            f"{objective} N'invente aucune notion technique au-delà de cet objectif et du "
            "titre — ce contexte n'a pas encore été enrichi par un cahier des charges "
            "pédagogique complet comme MC01 à MC03."
        ),
    )


def _build_contexts() -> dict[str, PedagogicalContext]:
    contexts: dict[str, PedagogicalContext] = {}
    for plan in AMPCR_PLAN:
        if plan.has_authored_content and plan.course_key in PEDAGOGICAL_CONTEXTS:
            contexts[plan.course_key] = PEDAGOGICAL_CONTEXTS[plan.course_key]
        else:
            contexts[plan.course_key] = _detailed_context(plan)
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

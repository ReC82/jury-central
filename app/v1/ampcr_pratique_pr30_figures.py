"""PR30 « Grand laboratoire écrit — installation et dépannage d'un réseau complet » — dossier
de la PME fictive, valeurs calculées et schémas (ticket #229).

PR30 est le **dossier intégrateur** du parcours : il ne réinvente aucune règle. Chaque valeur
du dossier est calculée par les fonctions déjà vérifiées des cours précédents, appliquées aux
données d'une seule PME fictive (« Géomètres Lambert & Associés ») :

- plan des locaux, longueurs de liens, switch, panneau, baie, câble et PoE : PR18
  (`plan_runs`, `choose_switch`, `panels_needed`, `choose_rack`, `boxes_needed`,
  `poe_verdict`, `patch_rows`, `link_verdict`, `validation_diagnosis`) ;
- code des couleurs T568B : socle #192 / PR15 (`T568B`, `pinout_svg`) ;
- plan IPv4 et DHCP : PR20 (`Host`, `AddressPlan`, `plan_errors`) ;
- groupe de travail ou domaine : PR22 (`recommend_model`) ;
- partages et droits effectifs (partage + NTFS) : PR23 (`effective_access`) ;
- compatibilité Windows 11 : PR07 (`win11_check`) ;
- Wi-Fi : PR25 (`audit_config`, `passphrase_issues`, `best_channel_24`, `received_dbm`) ;
- recette, verdict, décision et rapport : PR29 (`Criterion`, `Measure`, `Report`) ;
- arbres de décision : PR27 (`Tree`, `walk`).

Ce module ajoute seulement : les données de la PME, la nomenclature **sans prix** (budget
indicatif par postes de dépense, prix à obtenir par devis), la correspondance des huit études
de cas avec les exigences officielles AP-xx et les compléments, les procédures du
laboratoire, l'arbre de recette d'un poste et des schémas SVG construits depuis ces données
(aucune image générée). Les personnes, l'entreprise, les adresses MAC et les relevés sont
fictifs ; l'adresse publique vient de la plage de documentation RFC 5737.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_plan import REQUIREMENTS_BY_ID
from app.v1.ampcr_pratique_pr07_figures import (
    W11_NO,
    W11_OK,
    W11_SETTINGS,
    PcSpec,
    win11_check,
)
from app.v1.ampcr_pratique_pr15_figures import pinout_svg
from app.v1.ampcr_pratique_pr18_figures import (
    BOX_M,
    D_IP,
    D_OK,
    D_PHYS,
    D_SHARE,
    PERMANENT_LINK_MAX_M,
    POE_OK,
    T_OK,
    T_WIRING,
    FloorPlan,
    LinkTest,
    Point,
    RackItem,
    Room,
    boxes_needed,
    choose_rack,
    choose_switch,
    floor_plan_svg,
    link_verdict,
    panels_needed,
    patch_rows,
    plan_runs,
    poe_budget_w,
    poe_verdict,
    rack_svg,
    rack_units,
    switch_ports_needed,
    validation_diagnosis,
)
from app.v1.ampcr_pratique_pr20_figures import AddressPlan, Host, lan_svg, plan_errors, subnet_facts
from app.v1.ampcr_pratique_pr22_figures import MODEL_DOMAIN, MODEL_WG, Organisation, recommend_model
from app.v1.ampcr_pratique_pr23_figures import (
    AUTH_USERS,
    LEVEL_MODIFY,
    LEVEL_NONE,
    LEVEL_READ,
    LOCAL_ADMINS,
    Account,
    Ace,
    Folder,
    Share,
    effective_access,
    unc,
)
from app.v1.ampcr_pratique_pr25_figures import (
    BAND_5,
    BAND_24,
    OBSTACLE_LABELS,
    TARGET_DBM,
    WPA2_PSK,
    WPA2_WPA3,
    ApConfig,
    Neighbor,
    audit_config,
    best_channel_24,
    passphrase_issues,
    received_dbm,
    signal_verdict,
)
from app.v1.ampcr_pratique_pr27_figures import Tree
from app.v1.ampcr_pratique_pr28_figures import _blank_tree, checklist_svg
from app.v1.ampcr_pratique_pr29_figures import (
    K_NET,
    Criterion,
    JournalEntry,
    Measure,
    Report,
)
from app.v1.ampcr_pratique_visuals import (
    T568B,
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    pin_table,
    step_flow_svg,
)

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
_STROKE = "#33415c"
_SOFT = "#f4f6fb"

COMPANY = "Géomètres Lambert & Associés"
COMPANY_SHORT = "Lambert"

# =============================================================================================
# 1. Le dossier : locaux, personnes, postes
# =============================================================================================

PLAN = FloorPlan(
    name="Géomètres Lambert & Associés, plateau de bureaux (24 m × 10 m)",
    width_m=24,
    depth_m=10,
    rooms=(
        Room("Salle A — accueil et administration", 0, 0, 11, 10),
        Room("Local technique", 11, 0, 2, 4, "LT"),
        Room("Couloir", 11, 4, 2, 6, "C"),
        Room("Salle B — bureau d'études", 13, 0, 11, 10),
    ),
    rack=Point("BAIE", "Baie murale du local technique", 12, 2),
    box=Point("BOX", "Arrivée fibre de l'opérateur et box", 11.6, 3.4),
    outlets=(
        Point("P01", "Salle A, poste ACCUEIL", 1, 8),
        Point("P02", "Salle A, poste DIRECTION", 1, 2),
        Point("P03", "Salle A, poste COMPTA", 6, 9.5),
        Point("P04", "Salle A, imprimante multifonction IMP-01", 10.5, 9.5),
        Point("P05", "Salle A, prise de réserve", 6, 0.5),
        Point("P06", "Salle B, poste ETUDES1", 23, 2),
        Point("P07", "Salle B, poste ETUDES2", 23, 8),
        Point("P08", "Salle B, poste LINUX1", 17, 9.5),
        Point("P09", "Plafond du couloir, point d'accès Wi-Fi AP-01", 12, 7, poe_class=4),
        Point("P10", "Salle B, prise de réserve", 14, 0.5),
    ),
)
RUNS = plan_runs(PLAN)  # (repère, parcours horizontal, longueur à prévoir)
RUN_LENGTHS = tuple(length for _k, _h, length in RUNS)
TOTAL_CABLE_M = sum(RUN_LENGTHS)
LONGEST_RUN = max(RUNS, key=lambda r: r[2])

# Personnes (fictives) : (identifiant, nom affiché, fonction, poste, groupes)
PEOPLE: tuple[tuple[str, str, str, str], ...] = (
    ("amartin", "Alice Martin", "accueil et secrétariat", "ACCUEIL"),
    ("cdubois", "Claire Dubois", "directrice", "DIRECTION"),
    ("flemaire", "François Lemaire", "comptable", "COMPTA"),
    ("jroux", "Julien Roux", "géomètre", "ETUDES1"),
    ("nperrin", "Nadia Perrin", "dessinatrice", "ETUDES2"),
    ("tvidal", "Thomas Vidal", "cartographe (logiciels libres)", "LINUX1"),
)

# Contraintes du client, telles qu'écrites dans la demande (support fictif).
CONSTRAINTS: tuple[str, ...] = (
    "Six personnes, deux salles séparées par le local technique ; la fibre de l'opérateur arrive dans le local technique.",
    "Internet pour tous ; un dossier commun et des dossiers par service, avec des droits différents.",
    "Une imprimante multifonction pour tous, utilisable même quand les autres PC sont éteints.",
    "Wi-Fi pour les portables du personnel dans les deux salles ; Wi-Fi séparé pour les clients en rendez-vous, sans accès aux fichiers.",
    "Quatre postes de plus dans deux ans ; le serveur doit s'arrêter proprement en cas de coupure de courant.",
    "Budget à présenter par postes de dépense : le client compare lui-même les devis des fournisseurs.",
    "Installation pendant un week-end ; les données de la comptabilité ne quittent jamais le bureau.",
)

# Parc existant ou acheté (relevé du technicien, fictif) et compatibilité Windows 11 (PR07).
PCS: tuple[tuple[str, str, PcSpec], ...] = (
    ("ACCUEIL", "PC neuf, Windows 11 Pro préinstallé",
     PcSpec("Intel Core i5-14400", True, True, 10, 2.5, 16, 512, True, "UEFI", True, 2.0, True, "GPT")),
    ("DIRECTION", "portable de 2023, Windows 11 Pro",
     PcSpec("Intel Core Ultra 5 125U", True, True, 12, 1.3, 16, 512, True, "UEFI", True, 2.0, True, "GPT")),
    ("COMPTA", "PC de 2021 sous Windows 10 Pro",
     PcSpec("Intel Core i5-11400", True, True, 6, 2.6, 16, 512, True, "UEFI", False, 2.0, False, "GPT")),
    ("ETUDES1", "station de dessin de 2024, Windows 11 Pro",
     PcSpec("AMD Ryzen 7 7700", True, True, 8, 3.8, 32, 1000, True, "UEFI", True, 2.0, True, "GPT")),
    ("ETUDES2", "station neuve livrée sans système",
     PcSpec("AMD Ryzen 7 7700", True, True, 8, 3.8, 32, 1000, True, "UEFI", True, 2.0, True, "GPT")),
    ("LINUX1", "PC de 2014 récupéré, 8 Go, SSD de 240 Go",
     PcSpec("Intel Core i5-4590", True, False, 4, 3.3, 8, 240, True, "Hérité", False, 0, False, "MBR")),
)
PC_CHECKS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {name: win11_check(spec) for name, _d, spec in PCS}

OS_WIN11 = "Windows 11 Pro"
OS_UBUNTU = "Ubuntu 24.04 LTS (bureau)"
SERVER_OS = "Windows Server, édition Standard"


def os_choice(name: str) -> str:
    """Système retenu : Windows 11 Pro si le PC est compatible (tel quel ou après réglages du
    firmware) ; sinon un système libre maintenu (Ubuntu LTS), plutôt que Windows 10, qui
    n'est plus pris en charge depuis le 14 octobre 2025."""
    verdict = PC_CHECKS[name][0]
    return OS_WIN11 if verdict in (W11_OK, W11_SETTINGS) else OS_UBUNTU


OS_PLAN: dict[str, str] = {name: os_choice(name) for name, _d, _s in PCS}

# =============================================================================================
# 2. Dimensionnement, nomenclature et budget indicatif (sans prix)
# =============================================================================================

LINKS = len(PLAN.outlets)  # liens à brasser (prises, y compris celle du point d'accès)
UPLINKS = 2  # cordons directs dans la baie : box et serveur SRV-01
FUTURE_POSTES = 4
PORTS_NOW = switch_ports_needed(LINKS, UPLINKS)
PORTS_LATER = switch_ports_needed(LINKS + FUTURE_POSTES, UPLINKS)  # le switch est choisi pour l'extension prévue
SWITCH_PORTS = choose_switch(LINKS + FUTURE_POSTES, UPLINKS)
PANELS = panels_needed(LINKS)
CABLE_BOXES = boxes_needed(RUN_LENGTHS)
SWITCH_POE_BUDGET_W = 120.0  # budget PoE du switch retenu (fiche du modèle)
POE_CLASSES = tuple(o.poe_class for o in PLAN.outlets if o.poe_class is not None)
POE_NEED_W = poe_budget_w(POE_CLASSES)
POE_RESULT = poe_verdict(POE_CLASSES, SWITCH_POE_BUDGET_W)

RACK_LAYOUT: tuple[RackItem, ...] = (  # du haut vers le bas
    RackItem("Panneau de brassage 24 ports Cat6", 1),
    RackItem("Passe-câbles", 1),
    RackItem(f"Switch administrable {SWITCH_PORTS} ports PoE+", 1),
    RackItem("Étagère : box de l'opérateur", 2),
    RackItem("Étagère : serveur SRV-01 (mini-tour)", 4),
    RackItem("Onduleur", 2),
    RackItem("Bandeau de prises électriques", 1),
)
RACK_USED_U = rack_units(RACK_LAYOUT)
RACK_U = choose_rack(RACK_USED_U)

COST_ACTIVE = "Matériel actif"
COST_PASSIVE = "Câblage et matériel passif"
COST_SOFTWARE = "Logiciels et licences"
COST_LABOUR = "Main-d'œuvre"
COST_GROUPS = (COST_ACTIVE, COST_PASSIVE, COST_SOFTWARE, COST_LABOUR)


@dataclass(frozen=True)
class BomLine:
    item: str
    quantity: str
    group: str
    why: str


BOM: tuple[BomLine, ...] = (
    BomLine(f"Switch administrable gigabit {SWITCH_PORTS} ports, PoE+ ({SWITCH_POE_BUDGET_W:g} W), VLAN", "1", COST_ACTIVE,
            f"aujourd'hui {PORTS_NOW} ports, {PORTS_LATER} avec les {FUTURE_POSTES} postes prévus (20 % de réserve compris) ; VLAN ; PoE du point d'accès"),
    BomLine("Point d'accès Wi-Fi 6 bibande, plafonnier, PoE, deux SSID", "1", COST_ACTIVE,
            "personnel et invités séparés ; alimenté par le câble"),
    BomLine("Onduleur (UPS) avec port USB ou réseau pour l'arrêt du serveur", "1", COST_ACTIVE,
            "box, switch et serveur tiennent une micro-coupure ; arrêt propre du serveur"),
    BomLine("Serveur de fichiers SRV-01 (mini-tour, 2 disques en miroir)", "1", COST_ACTIVE,
            "partages centralisés, sauvegarde ; le miroir protège d'une panne de disque, pas d'un effacement"),
    BomLine("Disques de sauvegarde externes, en rotation", "2", COST_ACTIVE,
            "une copie hors du bureau chaque semaine (la sauvegarde n'est pas le miroir)"),
    BomLine("Câble Cat6 U/UTP monobrin, gaine LSZH, boîte de 305 m", str(CABLE_BOXES), COST_PASSIVE,
            f"{TOTAL_CABLE_M} m à poser, plus long lien {LONGEST_RUN[2]} m ≤ {PERMANENT_LINK_MAX_M} m"),
    BomLine(f"Baie murale {RACK_U} U, porte à clé, ventilée", "1", COST_PASSIVE,
            f"{RACK_USED_U} U occupés + 25 % de réserve"),
    BomLine("Panneau de brassage 24 ports Cat6", str(PANELS), COST_PASSIVE,
            f"{LINKS} ports utilisés, {24 * PANELS - LINKS} libres pour les {FUTURE_POSTES} postes prévus"),
    BomLine("Prises murales RJ45 Cat6 (keystone + boîtier)", str(LINKS), COST_PASSIVE, "une par repère P01 à P10"),
    BomLine("Cordons de brassage Cat6 de 0,5 m (baie)", str(LINKS + UPLINKS), COST_PASSIVE, "panneau → switch, box et serveur"),
    BomLine("Cordons de poste Cat6 de 3 m", str(LINKS - 1), COST_PASSIVE, "prise → poste, imprimante ; le point d'accès est raccordé au plafond"),
    BomLine("Goulottes, chemins de câbles, colliers à velcro", "selon métré", COST_PASSIVE,
            "séparation du courant fort, rayon de courbure"),
    BomLine(SERVER_OS, "1", COST_SOFTWARE, "système du serveur de fichiers"),
    BomLine("Licences d'accès client (CAL) Windows Server, par utilisateur", str(len(PEOPLE)), COST_SOFTWARE,
            "chaque personne qui utilise le serveur en a besoin"),
    BomLine("Mise à niveau Windows 11 Pro de COMPTA", "0 (gratuite depuis Windows 10 Pro)", COST_SOFTWARE,
            "même édition Pro, licence numérique conservée"),
    BomLine(OS_UBUNTU, "1", COST_SOFTWARE, "logiciel libre : aucune licence à acheter"),
    BomLine("Pose et raccordement du câblage, tests au testeur", "heures à estimer", COST_LABOUR, "deux techniciens, un week-end"),
    BomLine("Installation et configuration : baie, réseau, serveur, postes, Wi-Fi", "heures à estimer", COST_LABOUR, "dossier de configuration remis"),
    BomLine("Recette, rapport, formation courte des utilisateurs", "heures à estimer", COST_LABOUR, "PV signé, procédures remises"),
)
BOM_BY_GROUP: dict[str, tuple[BomLine, ...]] = {g: tuple(b for b in BOM if b.group == g) for g in COST_GROUPS}
PRICE_NOTE = (
    "Aucun prix n'est inventé : le budget indicatif présente les quantités par poste de dépense ; "
    "les montants viennent des devis d'au moins deux fournisseurs, à la date de la commande."
)

# =============================================================================================
# 3. Câblage, brassage et recette des liens
# =============================================================================================

STANDARD = "T568B"
PINS = pin_table(T568B)  # (broche, couleur) de 1 à 8
PATCH = patch_rows(PLAN)  # (repère, destination, port du switch, prise)

# Rapport du testeur après la pose (fictif) : un seul lien en défaut (fil 6 ouvert à la prise P08).
LINK_TESTS: tuple[LinkTest, ...] = tuple(
    LinkTest(key, wiremap_ok=(key != "P08"), length_m=float(length - 4), certification="PASS")
    for key, _h, length in RUNS
)
LINK_RESULTS: dict[str, str] = {t.label: link_verdict(t) for t in LINK_TESTS}
FAILED_LINKS = tuple(k for k, v in LINK_RESULTS.items() if v != T_OK)
WIREMAP_P08 = "1-1 2-2 3-3 4-4 5-5 6-ouvert 7-7 8-8"
P08_LENGTH_M = next(t.length_m for t in LINK_TESTS if t.label == "P08")

# =============================================================================================
# 4. Plan IPv4, DHCP et DNS
# =============================================================================================

NETWORK = "192.168.50.0/24"
PREFIX = 24
ROUTER_IP = "192.168.50.1"  # box : passerelle, NAT, pare-feu, DHCP et relais DNS du LAN
SWITCH_IP = "192.168.50.2"
AP_IP = "192.168.50.3"
SERVER_IP = "192.168.50.10"
PRINTER_IP = "192.168.50.20"
POOL = ("192.168.50.100", "192.168.50.199")
WAN_IP = "203.0.113.77"  # adresse publique de la box (RFC 5737, fictive)
GUEST_VLAN = 60
GUEST_NETWORK = "192.168.60.0/24"
GUEST_GATEWAY = "192.168.60.1"
LEASE_HOURS = 24


def _dhcp(name: str, role: str, last: int, mac: str) -> Host:
    return Host(name, role, f"192.168.50.{last}", PREFIX, ROUTER_IP, (ROUTER_IP,), mac, dhcp=True)


HOSTS: tuple[Host, ...] = (
    Host("BOX", "box : passerelle, DHCP, DNS", ROUTER_IP, PREFIX, None, (), "00-1E-80-5A-10-01"),
    Host("SW-01", "switch (adresse de gestion)", SWITCH_IP, PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-02"),
    Host("AP-01", "point d'accès Wi-Fi", AP_IP, PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-03"),
    Host("SRV-01", "serveur de fichiers", SERVER_IP, PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-0A"),
    Host("IMP-01", "imprimante multifonction", PRINTER_IP, PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-14"),
    _dhcp("ACCUEIL", "poste, DHCP", 101, "3C-52-82-50-01-01"),
    _dhcp("DIRECTION", "portable, DHCP", 102, "3C-52-82-50-01-02"),
    _dhcp("COMPTA", "poste, DHCP", 103, "3C-52-82-50-01-03"),
    _dhcp("ETUDES1", "station, DHCP", 104, "3C-52-82-50-01-04"),
    _dhcp("ETUDES2", "station, DHCP", 105, "3C-52-82-50-01-05"),
    _dhcp("LINUX1", "poste Linux, DHCP", 106, "3C-52-82-50-01-06"),
)
HOSTS_BY_NAME = {h.name: h for h in HOSTS}
ADDRESS_PLAN = AddressPlan(NETWORK, HOSTS, ROUTER_IP, ROUTER_IP, POOL)
PLAN_ERRORS = plan_errors(ADDRESS_PLAN)  # doit rester vide (contrôlé par les tests)
FACTS = subnet_facts(ROUTER_IP, PREFIX)
POOL_SIZE = int(POOL[1].rsplit(".", 1)[1]) - int(POOL[0].rsplit(".", 1)[1]) + 1
FIXED_HOSTS = tuple(h for h in HOSTS if not h.dhcp)

# Brouillon d'un collègue (exercices) : trois erreurs que `plan_errors` doit trouver.
DRAFT_HOSTS: tuple[Host, ...] = (
    HOSTS[0],
    Host("SRV-01", "serveur de fichiers", SERVER_IP, PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-0A"),
    Host("IMP-01", "imprimante multifonction", "192.168.50.150", PREFIX, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-14"),
    Host("AP-01", "point d'accès Wi-Fi", AP_IP, 16, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-03"),
    Host("SW-01", "switch (adresse de gestion)", SWITCH_IP, PREFIX, "192.168.1.1", (ROUTER_IP,), "00-1E-80-5A-10-02"),
)
DRAFT_PLAN = AddressPlan(NETWORK, DRAFT_HOSTS, ROUTER_IP, ROUTER_IP, POOL)
DRAFT_ERRORS = plan_errors(DRAFT_PLAN)

# =============================================================================================
# 5. Groupe de travail ou domaine, comptes, partages et droits (serveur SRV-01)
# =============================================================================================

ORG = Organisation(COMPANY, postes=len(PCS))
ORG_LATER = Organisation(f"{COMPANY} avec stagiaires", postes=len(PCS) + FUTURE_POSTES, rotation=True)
MODEL = recommend_model(ORG)
MODEL_LATER = recommend_model(ORG_LATER)

LOCAL_USERS = "Utilisateurs"  # groupe local de SRV-01 qui contient chaque compte créé
G_ADMIN, G_DIRECTION, G_COMPTA, G_ETUDES = "G_Administration", "G_Direction", "G_Compta", "G_Etudes"
GROUPS_OF: dict[str, tuple[str, ...]] = {
    "amartin": (G_ADMIN,),
    "cdubois": (G_ADMIN, G_DIRECTION),
    "flemaire": (G_ADMIN, G_COMPTA),
    "jroux": (G_ETUDES,),
    "nperrin": (G_ETUDES,),
    "tvidal": (G_ETUDES,),
}
ACCOUNTS: tuple[Account, ...] = tuple(
    Account(login, name, (LOCAL_USERS, *GROUPS_OF[login])) for login, name, _f, _p in PEOPLE
)
ACCOUNTS_BY_LOGIN = {a.login: a for a in ACCOUNTS}

SERVER = "SRV-01"
ROOT = "D:\\Partages"
FOLDERS = ("Commun", "Administration", "Etudes", "Compta")
TREE: dict[str, Folder] = {
    f.path: f
    for f in (
        Folder(ROOT, (Ace(LOCAL_ADMINS, "Contrôle total"),), inherit=False),
        Folder(f"{ROOT}\\Commun", (Ace(LOCAL_USERS, "Modification"),)),
        Folder(f"{ROOT}\\Administration", (Ace(G_ADMIN, "Modification"),)),
        Folder(f"{ROOT}\\Etudes", (Ace(G_ETUDES, "Modification"), Ace(G_DIRECTION, "Lecture et exécution"))),
        Folder(f"{ROOT}\\Compta", (Ace(G_COMPTA, "Modification"), Ace(G_DIRECTION, "Lecture et exécution"))),
    )
}
SHARES: dict[str, Share] = {
    name: Share(name, f"{ROOT}\\{name}", (Ace(AUTH_USERS, "Modifier"),)) for name in FOLDERS
}


def access(login: str, folder: str) -> str:
    """Droit effectif par le réseau (le plus restrictif du partage et de NTFS, PR23)."""
    return effective_access(ACCOUNTS_BY_LOGIN[login], f"{ROOT}\\{folder}", tree=TREE, shares=SHARES)


MATRIX: dict[str, dict[str, str]] = {a.login: {f: access(a.login, f) for f in FOLDERS} for a in ACCOUNTS}

# Besoins exprimés par le client (ce que la matrice doit donner).
NEEDS: tuple[tuple[str, str], ...] = (
    ("Commun", "tout le personnel lit et modifie"),
    ("Administration", "accueil, direction et comptabilité lisent et modifient ; le bureau d'études n'y accède pas"),
    ("Etudes", "le bureau d'études lit et modifie ; la directrice lit seulement"),
    ("Compta", "le comptable lit et modifie ; la directrice lit seulement ; personne d'autre"),
)

# =============================================================================================
# 6. Wi-Fi du personnel et des invités
# =============================================================================================

SSID_PRO = "LAMBERT-PRO"
SSID_GUEST = "LAMBERT-INVITES"
PASSPHRASE_PRO = "Borne-Theodolite-Cadastre-2026"  # ASCII imprimable (802.11) ; fictive, jamais dans un rapport
NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Pharmacie-Centre", 1, -61, "b0:4e:26:11:00:01"),
    Neighbor("Proximus-A2C4", 6, -66, "f4:ca:e5:11:00:02"),
    Neighbor("Notaire-Wifi", 11, -84, "00:1d:7e:11:00:03"),
    Neighbor("Telenet-77B1", 9, -86, "c8:cd:72:11:00:04"),
)
CHANNEL_24 = best_channel_24(NEIGHBORS)
CHANNEL_5 = 36  # sans DFS
WIFI_NAMES = (COMPANY_SHORT, "Géomètres")
AP_CONFIG = ApConfig(SSID_PRO, WPA2_WPA3, PASSPHRASE_PRO, channel_24=CHANNEL_24, guest_isolated=True, names=WIFI_NAMES)
AP_AUDIT = audit_config(AP_CONFIG)  # doit rester vide
DRAFT_AP = ApConfig(SSID_PRO, WPA2_PSK, "lambert2026", wps=True, admin_default=True, channel_24=3, width_24=40,
                    ssid_hidden=True, guest_isolated=False, names=WIFI_NAMES)
DRAFT_AP_AUDIT = audit_config(DRAFT_AP)

# Relevé de couverture prévu (estimation du cours PR25 : point d'accès au plafond du couloir).
SURVEY: tuple[tuple[str, float, tuple[str, ...]], ...] = (
    ("Couloir, sous le point d'accès", 2.5, ()),
    ("Salle A, bureau ACCUEIL", 11.0, ("cloison",)),
    ("Salle A, angle de la DIRECTION", 13.2, ("cloison",)),
    ("Salle B, poste ETUDES1", 12.1, ("cloison",)),
    ("Salle B, angle le plus éloigné", 13.2, ("cloison",)),
)


def survey_rows() -> tuple[tuple[str, str, int, int, str], ...]:
    """(lieu, obstacles, dBm 2,4 GHz, dBm 5 GHz, verdict 5 GHz) — le 5 GHz, plus atténué,
    décide."""
    rows = []
    for place, distance, obstacles in SURVEY:
        d24, d5 = received_dbm(distance, BAND_24, obstacles), received_dbm(distance, BAND_5, obstacles)
        label = ", ".join(OBSTACLE_LABELS[o] for o in obstacles) or "aucun"
        rows.append((f"{place} ({distance:g} m)".replace(".", ","), label, d24, d5, signal_verdict(d5)))
    return tuple(rows)


SURVEY_ROWS = survey_rows()
WORST_5 = min(r[3] for r in SURVEY_ROWS)
ONE_AP_ENOUGH = WORST_5 >= TARGET_DBM

# =============================================================================================
# 7. Sécurité de l'installation
# =============================================================================================

SEC_GOOD = "Mesure de sécurité efficace"
SEC_FAKE = "Fausse sécurité ou pratique à proscrire"
SEC_KINDS = (SEC_GOOD, SEC_FAKE)
SECURITY_ITEMS: tuple[tuple[str, str], ...] = (
    ("Changer les mots de passe d'administration par défaut de la box, du switch et du point d'accès", SEC_GOOD),
    ("Masquer le nom du réseau Wi-Fi du personnel", SEC_FAKE),
    ("WPA2/WPA3-Personnel avec une clé longue, WPS désactivé", SEC_GOOD),
    ("Wi-Fi invités sur un VLAN isolé du réseau interne", SEC_GOOD),
    ("Donner à chacun le compte administrateur du serveur « pour éviter les appels »", SEC_FAKE),
    ("Un compte nominatif par personne, droits limités à son service", SEC_GOOD),
    ("Considérer le miroir des deux disques du serveur comme la sauvegarde", SEC_FAKE),
    ("Sauvegarde hebdomadaire sur disque externe gardé hors du bureau, restauration testée", SEC_GOOD),
    ("Laisser la baie ouverte pour que le personnel puisse redémarrer la box", SEC_FAKE),
    ("Onduleur qui commande l'arrêt propre du serveur", SEC_GOOD),
    ("Mettre à jour Windows, Ubuntu et les micrologiciels avant la recette", SEC_GOOD),
    ("Noter la clé Wi-Fi et les mots de passe dans le rapport remis au client", SEC_FAKE),
)
SECURITY_CHECKLIST: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Équipements", (
        "Mots de passe par défaut changés (box, switch, point d'accès, onduleur)",
        "Micrologiciels à jour ; administration à distance coupée",
        "Baie fermée à clé ; clé remise à la directrice",
    )),
    ("Comptes et données", (
        "Un compte par personne ; administrateur réservé au technicien",
        "Droits vérifiés avec la matrice ; aucun « Tout le monde : contrôle total »",
        "Sauvegarde externe planifiée et restauration d'essai réussie",
    )),
    ("Postes et Wi-Fi", (
        "Systèmes à jour, antivirus et pare-feu actifs, profil réseau « Privé »",
        "Wi-Fi WPA2/WPA3, WPS coupé ; invités isolés du réseau interne",
        "Identifiants remis sous pli au client, jamais dans le rapport",
    )),
)

# =============================================================================================
# 8. Procédures, recette d'un poste, pannes de mise en service
# =============================================================================================

LAB_STEPS: tuple[tuple[str, str], ...] = (
    ("Analyser la demande", "Besoins, contraintes, plan des locaux, parc existant ; questions au client."),
    ("Concevoir", "Topologie en étoile, emplacements, plan IPv4, comptes et droits, Wi-Fi."),
    ("Chiffrer et commander", "Nomenclature, budget par postes, devis des fournisseurs, accord écrit."),
    ("Câbler et tester", "Pose, raccordement T568B, repérage, chaque lien au testeur."),
    ("Équiper la baie", "Panneau, switch, box, serveur, onduleur ; brassage selon le plan."),
    ("Installer et configurer", "Serveur, partages, systèmes des postes, imprimante, Wi-Fi."),
    ("Sécuriser", "Mots de passe, mises à jour, sauvegarde, baie fermée, invités isolés."),
    ("Recetter et rendre compte", "Fiche de recette avec le client, rapport, PV signé, dossier remis."),
)
RECETTE_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer la fiche", "Critères d'acceptation écrits avec le client avant la recette."),
    ("Liens", "Rapport du testeur : les dix liens conformes, longueurs relevées."),
    ("Chaque poste", "Lien, adresse, passerelle, autre poste, Internet, partage, dans cet ordre."),
    ("Imprimante", "Impression depuis chaque poste, ordinateurs voisins éteints."),
    ("Wi-Fi", "Signal mesuré aux points prévus ; invité : Internet oui, serveur non."),
    ("Sécurité", "Liste de sécurité cochée ; coupure de courant simulée si le client l'autorise."),
    ("Verdict et signature", "Avant / après, verdict, réserves ; PV signé, dossier remis."),
)
INSTALL_WIN_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier", "Compatibilité (msinfo32, tpm.msc) ; sauvegarde vérifiée si des données existent."),
    ("Régler le firmware", "Mode UEFI, TPM activé, démarrage sécurisé ; démarrer sur la clé."),
    ("Installer", "Windows 11 Pro, disque entier en GPT ; compte local de l'utilisateur."),
    ("Pilotes et mises à jour", "Windows Update, pilotes du fabricant ; Gestionnaire sans erreur."),
    ("Réseau", "Profil « Privé » ; adresse DHCP du plan ; nom du poste comme l'inventaire."),
    ("Ressources", "Lecteur réseau vers le partage du service ; imprimante IMP-01 par son adresse IP."),
)
INSTALL_LINUX_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier", "Image Ubuntu contrôlée (sha256sum) ; aucune donnée à garder sur le SSD."),
    ("Régler le firmware", "Mode UEFI ; démarrer sur la clé ; ignorer le TPM, inutile ici."),
    ("Installer", "Disque entier : partition EFI et racine ext4 ; compte de l'utilisateur."),
    ("Mettre à jour", "sudo apt update puis sudo apt upgrade ; redémarrer."),
    ("Réseau", "ip -br addr : adresse DHCP du plan ; nom d'hôte linux1."),
    ("Ressources", "Partage smb://192.168.50.10/Etudes avec le compte du serveur ; imprimante par IP."),
)
PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Mener le laboratoire, de la demande à la réception", LAB_STEPS),
    ("Recette de l'installation avec le client", RECETTE_STEPS),
    ("Installer Windows 11 Pro et raccorder le poste", INSTALL_WIN_STEPS),
    ("Installer Ubuntu et raccorder le poste", INSTALL_LINUX_STEPS),
)

RECETTE_TREE = Tree(
    key="recette-poste",
    title="Un poste échoue à la recette",
    start="Un poste de la PME n'atteint pas le partage ou Internet au moment de la recette.",
    questions=(
        ("Le voyant de la carte et du port du switch sont-ils allumés ?",
         "Lien physique : cordon, prise, brassage ou port ; rapport du testeur du lien."),
        ("ipconfig ou ip addr montre-t-il une adresse 192.168.50.x, masque /24, passerelle .1 ?",
         "Adressage : DHCP, port du switch dans le bon VLAN, adresse en double."),
        ("Le ping de la passerelle 192.168.50.1 répond-il ?",
         "Passerelle : box ou son raccordement, pare-feu du poste."),
        ("Le ping du serveur 192.168.50.10 répond-il ?",
         "Poste distant : serveur éteint, pare-feu, autre réseau."),
        ("Un site s'ouvre-t-il par son nom ?",
         "Internet : DNS du poste, box, liaison de l'opérateur."),
        ("Le partage \\\\SRV-01\\<service> s'ouvre-t-il avec le compte de la personne ?",
         "Partage : chemin, compte enregistré, droits du partage ou NTFS."),
    ),
    final="Poste validé : noter les résultats sur la fiche de recette et passer au suivant.",
)

# Résultats de la recette (fictifs) : les contrôles de PR18, dans le même ordre.
_ALL_OK = {"lien": True, "adresse": True, "passerelle": True, "poste": True, "internet": True, "partage": True}
RECETTE_RESULTS: dict[str, dict[str, bool]] = {
    "ACCUEIL": dict(_ALL_OK),
    "DIRECTION": dict(_ALL_OK),
    "COMPTA": {**_ALL_OK, "partage": False},
    "ETUDES1": dict(_ALL_OK),
    "ETUDES2": {**_ALL_OK, "adresse": False, "passerelle": False, "poste": False, "internet": False, "partage": False},
    "LINUX1": {k: False for k in _ALL_OK},
}
RECETTE_DIAG: dict[str, str] = {name: validation_diagnosis(r) for name, r in RECETTE_RESULTS.items()}
RECETTE_EVIDENCE: dict[str, str] = {
    "COMPTA": "« Accès refusé » sur \\\\SRV-01\\Compta ; le Gestionnaire d'identification contient SRV-01\\amartin, "
              "enregistré quand l'accueil a préparé le poste",
    "ETUDES2": "ipconfig : 192.168.60.112, masque 255.255.255.0, passerelle 192.168.60.1 ; port 7 du switch "
               "laissé dans le VLAN 60 (invités) après un essai",
    "LINUX1": "ip -br link : enp3s0 DOWN, NO-CARRIER ; le testeur montrait le fil 6 ouvert sur le lien P08",
}

# Panne logicielle de COMPTA : droit effectif du compte enregistré par erreur.
STORED_LOGIN = "amartin"
STORED_ACCESS = access(STORED_LOGIN, "Compta")
RIGHT_ACCESS = access("flemaire", "Compta")

# Panne matérielle d'ETUDES1 (ajout de mémoire) : piste par piste.
RAM_FAULT_STEPS: tuple[tuple[str, str], ...] = (
    ("Sécuriser", "Arrêter, débrancher le secteur, bracelet antistatique relié au châssis."),
    ("Revenir à l'état connu", "Retirer les deux nouvelles barrettes : le PC démarre-t-il avec les 32 Go d'origine ?"),
    ("Tester une barrette", "Une seule nouvelle barrette, enfoncée jusqu'au clic des deux loquets, dans l'emplacement indiqué par le manuel."),
    ("Comparer", "Référence, type DDR, fréquence et tension : la liste de compatibilité (QVL) de la carte mère."),
    ("Conclure", "Barrette défectueuse ou incompatible : retour au fournisseur ; journal et rapport."),
)

# =============================================================================================
# 9. Les huit études de cas : exigences officielles et compléments
# =============================================================================================


@dataclass(frozen=True)
class CaseSpec:
    number: int
    level: int  # 1 à 4, de la plus guidée à la plus ouverte
    title: str
    official: tuple[str, ...]  # exigences AP-01..AP-38 travaillées
    complements: tuple[str, ...]  # compléments du parcours (AP-C..) et du cours, signalés comme tels


CASES: tuple[CaseSpec, ...] = (
    CaseSpec(1, 1, "Inventaire, contraintes et budget indicatif",
             ("AP-01", "AP-08", "AP-17", "AP-31", "AP-38"),
             ("AP-C01", "budget par postes de dépense (sans prix inventé)", "onduleur et sauvegarde externe")),
    CaseSpec(2, 1, "Câblage T568B, baie, brassage et recette des liens",
             ("AP-18", "AP-19", "AP-20", "AP-23", "AP-34", "AP-36"),
             ("AP-C02", "repérage baie-panneau-port, réserve de 20 % des ports")),
    CaseSpec(3, 2, "Plan IPv4, DHCP et DNS",
             ("AP-29", "AP-30", "AP-31", "AP-38"),
             ("réservations DHCP et adresses fixes hors étendue",)),
    CaseSpec(4, 2, "Groupe de travail ou domaine, comptes, partages et droits",
             ("AP-24", "AP-25", "AP-26", "AP-27"),
             ("licences d'accès client du serveur",)),
    CaseSpec(5, 3, "Installation des systèmes et raccordement des postes",
             ("AP-08", "AP-10", "AP-11", "AP-12", "AP-17", "AP-25"),
             ("AP-C03", "fin de prise en charge de Windows 10")),
    CaseSpec(6, 3, "Panne matérielle et panne logicielle à la mise en service",
             ("AP-02", "AP-09", "AP-13", "AP-14", "AP-15", "AP-27"),
             ("AP-C02", "Gestionnaire d'identification de Windows")),
    CaseSpec(7, 3, "Wi-Fi du personnel et des invités, sécurité de l'installation",
             ("AP-33", "AP-31"),
             ("AP-C03", "VLAN invités", "sauvegarde 3 copies et restauration d'essai")),
    CaseSpec(8, 4, "Recette, dépannage de l'accès au réseau et rapport final",
             ("AP-32", "AP-36", "AP-37", "AP-38", "AP-16"),
             ("AP-C01", "procès-verbal de recette, réserve et suivi")),
)
CASES_BY_NUMBER = {c.number: c for c in CASES}
COVERED_OFFICIAL = tuple(sorted({r for c in CASES for r in c.official}))
NOT_COVERED_OFFICIAL = tuple(
    r for r in REQUIREMENTS_BY_ID if r.startswith("AP-") and not r.startswith("AP-C") and r not in COVERED_OFFICIAL
)

# Tâches du dossier : exigence officielle ou complément (exercice de classement).
REQ_OFFICIAL = "Exigence officielle (consignes, pp. 5-6)"
REQ_COMPLEMENT = "Complément pédagogique du parcours"
REQ_KINDS = (REQ_OFFICIAL, REQ_COMPLEMENT)
REQ_TASKS: tuple[tuple[str, str, str], ...] = (
    ("Décrire le raccordement d'une prise RJ45 selon un code des couleurs", REQ_OFFICIAL, "AP-34"),
    ("Établir le plan d'adressage IP des postes", REQ_OFFICIAL, "AP-30"),
    ("Choisir entre groupe de travail et domaine", REQ_OFFICIAL, "AP-24"),
    ("Sécuriser le Wi-Fi et choisir le chiffrement", REQ_OFFICIAL, "AP-33"),
    ("Dépanner un poste qui n'accède pas au réseau", REQ_OFFICIAL, "AP-37"),
    ("Présenter un budget par postes de dépense", REQ_COMPLEMENT, "budget"),
    ("Dimensionner l'onduleur et l'arrêt du serveur", REQ_COMPLEMENT, "onduleur"),
    ("Isoler les invités dans un VLAN", REQ_COMPLEMENT, "VLAN"),
    ("Mettre le bracelet antistatique avant d'ouvrir un PC", REQ_COMPLEMENT, "AP-C02"),
    ("Rédiger le rapport et le procès-verbal de recette", REQ_COMPLEMENT, "AP-C01"),
)

# =============================================================================================
# 10. Rapport final du chantier (modèle de PR29)
# =============================================================================================

C_LINKS = Criterion("Liens conformes au testeur (sur 10)", ">=", 10)
C_POSTES = Criterion("Postes validés à la recette (sur 6)", ">=", 6)
C_LOSS = Criterion("Ping de la passerelle depuis chaque poste, pertes", "<=", 0, "%")
C_WIFI = Criterion("Signal Wi-Fi 5 GHz au point le plus éloigné", ">=", TARGET_DBM, "dBm")
C_GUEST = Criterion("Invité : accès au serveur refusé", "=", "oui")
C_UPS = Criterion("Coupure de courant : arrêt propre du serveur", "=", "oui")
FINAL_MEASURES: tuple[Measure, ...] = (
    Measure(C_LINKS, 9, 10),
    Measure(C_POSTES, 3, 6),
    Measure(C_LOSS, None, 0),
    Measure(C_WIFI, None, -55),
    Measure(C_GUEST, None, "oui"),
    Measure(C_UPS, None, None),
)

FINAL_REPORT = Report(
    key="L1",
    theme="réseau complet",
    title="Installation du réseau du bureau : recette avec une réserve",
    kind=K_NET,
    context="Fin du chantier du week-end ; recette le lundi matin avec la directrice.",
    fields={
        "reference": "Chantier 2026-118, 24-26/10/2026, deux techniciens de l'atelier",
        "equipement": f"Réseau du bureau : baie {RACK_U} U du local technique, switch SW-01, AP-01, SRV-01, IMP-01, six postes",
        "demande": "Installer le réseau complet : câblage, serveur de fichiers, Wi-Fi personnel et invités, postes",
        "symptomes": "À la recette : COMPTA « Accès refusé » sur Compta ; ETUDES2 en 192.168.60.112 ; LINUX1 sans lien",
        "hypotheses": "COMPTA : compte enregistré ; ETUDES2 : port dans le VLAN invités ; LINUX1 : défaut de la prise P08",
        "releves": "Testeur : P08 fil 6 ouvert ; ETUDES2 : passerelle 192.168.60.1 ; COMPTA : identifiant SRV-01\\amartin enregistré",
        "tests": "Recette poste par poste (lien, adresse, passerelle, serveur, Internet, partage) ; testeur sur chaque lien",
        "resultats": "Trois causes distinctes confirmées, une par poste",
        "action": "P08 refaite en T568B et retestée ; port 7 remis dans le VLAN 1 ; identifiant enregistré supprimé, reconnexion avec flemaire",
        "pieces": "Keystone Cat6 posé sur P08 (stock atelier) ; aucune autre pièce",
        "risques": "Arrêt du serveur sur coupure non testé (non concluant) ; quatre postes futurs à câbler sur les prises de réserve",
        "recommandation": "Test de coupure le samedi 7/11 avec la directrice ; restauration d'essai mensuelle de la sauvegarde",
        "signature": "Mme Dubois, directrice, 26/10/2026 : réception avec réserve",
    },
    measures=FINAL_MEASURES,
    checks_done=frozenset({"fonctionnel", "stabilite", "reseau", "securite"}),
    rollback_ready=True,
    journal=(
        JournalEntry("08:30", "Recette ACCUEIL, DIRECTION, ETUDES1", "6 contrôles réussis sur chaque poste"),
        JournalEntry("08:55", "Recette COMPTA : ouverture de \\\\SRV-01\\Compta", "« Accès refusé »"),
        JournalEntry("09:05", "Identifiant SRV-01\\amartin supprimé, reconnexion avec flemaire", "Compta : lecture et écriture"),
        JournalEntry("09:20", "ETUDES2 : port 7 du switch remis dans le VLAN 1, ipconfig /renew", "192.168.50.105, passerelle .1"),
        JournalEntry("09:50", "P08 refaite en T568B, lien retesté", f"8 fils conformes, {P08_LENGTH_M:g} m, PASS"),
        JournalEntry("10:10", "Recette LINUX1, COMPTA, ETUDES2 refaite", "6 contrôles réussis sur chaque poste"),
    ),
    client_message=(
        "Le réseau est installé : chacun accède à Internet, à l'imprimante et à ses dossiers, et le Wi-Fi des "
        "visiteurs n'ouvre pas vos fichiers. Trois petits défauts trouvés ce matin sont corrigés et vérifiés devant "
        "vous. Il reste à vérifier, un samedi, que le serveur s'éteint proprement lors d'une coupure de courant : "
        "nous le ferons ensemble le 7 novembre."
    ),
)

# =============================================================================================
# 11. Schémas
# =============================================================================================


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


def tree_alt(tree: Tree, questions: tuple[tuple[str, str], ...] | None = None) -> str:
    qs = questions or tree.questions
    return (f"Arbre de décision « {tree.title} ». Départ : {tree.start} "
            + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(qs, start=1))
            + f" Si toutes les réponses sont oui : {tree.final}")


def matrix_svg(matrix: dict[str, dict[str, str]], *, title: str = "Droits effectifs par le réseau sur SRV-01") -> str:
    """Comptes en lignes, dossiers en colonnes (tient sur 380 px pour six comptes et quatre
    dossiers) ; chaque case porte le niveau écrit en toutes lettres."""
    logins = list(matrix)
    folders = list(next(iter(matrix.values())))
    width, left, col_w, row_h, top = 380, 66, 78, 24, 48
    short = {LEVEL_NONE: "aucun", LEVEL_READ: "lecture", LEVEL_MODIFY: "modification"}
    fills = {LEVEL_NONE: "#fbecec", LEVEL_READ: "#fff3c4", LEVEL_MODIFY: "#e9f5ec"}
    parts = [_text_lines(width // 2, 16, [title], size=12, weight="700", anchor="middle")]
    for j, folder in enumerate(folders):
        x = left + j * col_w
        parts.append(f'<rect x="{x}" y="{top - 24}" width="{col_w - 2}" height="22" fill="#dbe4f3" stroke="{_STROKE}"/>')
        parts.append(_text_lines(x + col_w // 2 - 1, top - 9, [folder], size=9, weight="700", anchor="middle"))
    for i, login in enumerate(logins):
        y = top + i * row_h
        parts.append(f'<rect x="4" y="{y}" width="{left - 6}" height="{row_h - 2}" fill="{_SOFT}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(8, y + 15, [login], size=10.5, weight="700"))
        for j, folder in enumerate(folders):
            x = left + j * col_w
            value = matrix[login][folder]
            parts.append(f'<rect data-cell="{escape(login)}|{escape(folder)}" data-value="{escape(value)}" x="{x}" y="{y}" '
                         f'width="{col_w - 2}" height="{row_h - 2}" fill="{fills[value]}" stroke="{_STROKE}"/>')
            parts.append(_text_lines(x + col_w // 2 - 1, y + 15, [short[value]], size=10.5, anchor="middle"))
    y = top + len(logins) * row_h + 14
    notes = _wrap("Partages : « Utilisateurs authentifiés : Modifier » ; NTFS décide (le plus restrictif "
                  "des deux s'applique par le réseau).", 62)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def _matrix_alt() -> str:
    return "Droits effectifs par le réseau sur SRV-01 : " + " ; ".join(
        f"{login} — " + ", ".join(f"{f} : {v.lower()}" for f, v in row.items()) for login, row in MATRIX.items()
    ) + "."


def link_tests_svg(tests: tuple[LinkTest, ...]) -> str:
    """Rapport du testeur, une ligne par lien : repère, longueur, câblage, verdict calculé."""
    width, row_h, top = 380, 22, 44
    parts = [
        _text_lines(width // 2, 16, ["Recette des liens — rapport du testeur"], size=12, weight="700", anchor="middle"),
        _text_lines(10, 36, ["Lien"], size=10, weight="700"),
        _text_lines(70, 36, ["Longueur"], size=10, weight="700"),
        _text_lines(150, 36, ["Câblage"], size=10, weight="700"),
        _text_lines(236, 36, ["Verdict"], size=10, weight="700"),
    ]
    for i, t in enumerate(tests):
        y = top + i * row_h
        result = link_verdict(t)
        bad = result != T_OK
        parts.append(f'<rect data-link="{escape(t.label)}" data-result="{escape(result)}" x="4" y="{y}" width="372" '
                     f'height="{row_h - 2}" rx="3" fill="{"#fbecec" if bad else _SOFT}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(10, y + 14, [t.label], size=10.5, weight="700"))
        parts.append(_text_lines(70, y + 14, [f"{t.length_m:g} m".replace(".", ",")], size=10.5))
        parts.append(_text_lines(150, y + 14, ["✗ fil 6 ouvert" if not t.wiremap_ok else "✓ 8 fils"], size=10.5))
        parts.append(_text_lines(236, y + 14, ["✗ défaut de câblage" if bad else "✓ conforme"], size=10.5,
                                 weight="700" if bad else "400"))
    y = top + len(tests) * row_h + 12
    notes = _wrap(f"Limite du lien permanent : {PERMANENT_LINK_MAX_M} m. Certification Cat6 : PASS sur les dix liens. "
                  "Rapport fictif, présentation simplifiée.", 62)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def recette_svg(results: dict[str, dict[str, bool]]) -> str:
    """Fiche de recette : postes en lignes, six contrôles en colonnes (✓ / ✗ / –), diagnostic
    calculé à droite (premier contrôle en échec)."""
    keys = ("lien", "adresse", "passerelle", "poste", "internet", "partage")
    heads = ("Lien", "IP", "Pass.", "Serv.", "Web", "Part.")
    width, left, col_w, row_h, top = 380, 84, 34, 24, 50
    parts = [_text_lines(width // 2, 16, ["Fiche de recette des six postes"], size=12, weight="700", anchor="middle")]
    for j, head in enumerate(heads):
        parts.append(_text_lines(left + j * col_w + col_w // 2, top - 8, [head], size=10, weight="700", anchor="middle"))
    parts.append(_text_lines(left + 6 * col_w + 4, top - 8, ["Piste"], size=10, weight="700"))
    short = {D_OK: "validé", D_PHYS: "lien physique", D_IP: "adressage", D_SHARE: "partage"}
    for i, (name, res) in enumerate(results.items()):
        y = top + i * row_h
        diag = validation_diagnosis(res)
        first = next((k for k in keys if not res[k]), None)
        parts.append(f'<rect data-poste="{escape(name)}" data-diag="{escape(diag)}" x="4" y="{y}" width="372" '
                     f'height="{row_h - 2}" rx="3" fill="{_SOFT if diag == D_OK else "#fbecec"}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(8, y + 15, [name], size=10.5, weight="700"))
        for j, k in enumerate(keys):
            after_first = first is not None and keys.index(k) > keys.index(first)
            mark = "–" if after_first else ("✓" if res[k] else "✗")
            parts.append(_text_lines(left + j * col_w + col_w // 2, y + 15, [mark], size=11, weight="700", anchor="middle"))
        parts.append(_text_lines(left + 6 * col_w + 4, y + 15, [short.get(diag, diag)], size=10))
    y = top + len(results) * row_h + 12
    notes = _wrap("✓ réussi ; ✗ échec ; – non significatif : un contrôle qui suit un échec ne prouve rien tant "
                  "que le premier défaut n'est pas corrigé.", 62)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def _recette_alt() -> str:
    return "Fiche de recette : " + " ; ".join(
        f"{name} — " + (", ".join(k for k, v in res.items() if not v) + " en échec" if not all(res.values()) else "tout réussi")
        + f", piste : {RECETTE_DIAG[name]}" for name, res in RECETTE_RESULTS.items()
    ) + "."


def survey_svg(rows: tuple[tuple[str, str, int, int, str], ...]) -> str:
    """Relevé de couverture estimé : lieu, obstacles, signal 2,4 et 5 GHz, verdict."""
    width = 380
    parts = [_text_lines(width // 2, 16, ["Couverture Wi-Fi estimée (point d'accès au couloir)"], size=12, weight="700", anchor="middle")]
    y = 30
    for place, obstacles, d24, d5, verdict in rows:
        lines = _wrap(place, 40)
        h = 10 + 14 * (len(lines) + 2) + 6
        parts.append(f'<rect data-point="{escape(place)}" data-dbm5="{d5}" x="4" y="{y}" width="372" height="{h}" rx="4" '
                     f'fill="{_SOFT}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(10, y + 16, lines, size=10.5, weight="700", step=14))
        parts.append(_text_lines(10, y + 16 + 14 * len(lines), [f"obstacle : {obstacles}",
                                 f"2,4 GHz : {d24} dBm · 5 GHz : {d5} dBm ({verdict})"], size=10.5, step=14))
        y += h + 4
    notes = _wrap(f"Objectif : {TARGET_DBM} dBm ou mieux en 5 GHz. Estimation (modèle du cours PR25) à confirmer "
                  "par une mesure sur place à la recette.", 62)
    parts.append(_text_lines(8, y + 12, notes, size=10.5, step=13))
    return _svg(width, y + 12 + 13 * len(notes), parts)


_FIGURE_HOSTS = tuple(h for h in HOSTS if h.name != "SW-01")
PLAN_FIGURE = Figure(
    key="pr30-plan-locaux",
    title="Plan des locaux de la PME et emplacement des prises",
    alt=(f"Plateau de {PLAN.width_m:g} m sur {PLAN.depth_m:g} m : salle A (accueil et administration) à gauche, local "
         "technique et couloir au centre, salle B (bureau d'études) à droite. Baie et box dans le local technique. "
         + " ; ".join(f"prise {o.key} : {o.label}" for o in PLAN.outlets) + "."),
    caption="Plan fictif à l'échelle ; les câbles suivent les murs et le faux plafond, jamais en diagonale.",
    svg=floor_plan_svg(PLAN),
)
LAN_FIGURE = Figure(
    key="pr30-schema-logique",
    title="Schéma logique et plan d'adressage du réseau",
    alt=(f"Réseau {NETWORK} en étoile : la box {ROUTER_IP} relie Internet (adresse publique {WAN_IP}) au switch, "
         "qui relie chaque équipement par un câble. "
         + " ; ".join(f"{h.name} ({h.role}) : {h.ip}/{h.prefix}" + (" par DHCP" if h.dhcp else " fixe") for h in _FIGURE_HOSTS)
         + f". Adresse de gestion du switch : {SWITCH_IP}. Étendue DHCP de la box : {POOL[0]} à {POOL[1]}."),
    caption=f"Adresses fixes hors de l'étendue DHCP ({POOL[0]} à {POOL[1]}) ; le switch se gère en {SWITCH_IP}.",
    svg=lan_svg(AddressPlan(NETWORK, _FIGURE_HOSTS, ROUTER_IP, ROUTER_IP, POOL), WAN_IP),
)
RACK_FIGURE = Figure(
    key="pr30-baie",
    title=f"Baie murale de {RACK_U} U, face avant",
    alt=(f"Baie de {RACK_U} U, du haut vers le bas : " + " ; ".join(f"{i.name} ({i.units} U)" for i in RACK_LAYOUT)
         + f". Occupé : {RACK_USED_U} U ; libre : {RACK_U - RACK_USED_U} U."),
    caption="Le panneau en haut, le switch juste dessous (cordons courts), les éléments lourds en bas.",
    svg=rack_svg(RACK_LAYOUT, RACK_U, title=f"Baie {RACK_U} U du local technique"),
)
PINOUT_FIGURE = Figure(
    key="pr30-t568b",
    title="Code des couleurs T568B, aux deux extrémités de chaque lien",
    alt="Prise RJ45 en T568B, broches 1 à 8 : " + " ; ".join(f"{pin} {color}" for pin, color in PINS) + ".",
    caption="Une seule norme pour toute l'installation : T568B à la prise et au panneau (lien droit).",
    svg=pinout_svg(T568B, title="T568B — prises et panneau"),
)
LINKS_FIGURE = Figure(
    key="pr30-recette-liens",
    title="Recette des dix liens au testeur",
    alt="Rapport du testeur : " + " ; ".join(
        f"{t.label} {t.length_m:g} m, {'fil 6 ouvert' if not t.wiremap_ok else '8 fils conformes'}, {LINK_RESULTS[t.label].lower()}"
        for t in LINK_TESTS) + ".",
    caption="Un lien en défaut de câblage (P08) : le raccordement est refait et retesté avant la recette des postes.",
    svg=link_tests_svg(LINK_TESTS),
)
MATRIX_FIGURE = Figure(
    key="pr30-matrice-droits",
    title="Matrice des droits effectifs sur le serveur",
    alt=_matrix_alt(),
    caption="Calculée depuis les autorisations du partage et NTFS (règle de PR23) ; elle répond exactement aux besoins du client.",
    svg=matrix_svg(MATRIX),
)
SURVEY_FIGURE = Figure(
    key="pr30-couverture-wifi",
    title="Couverture Wi-Fi estimée",
    alt="Couverture estimée : " + " ; ".join(f"{p}, obstacle {o}, 2,4 GHz {a} dBm, 5 GHz {b} dBm, {v}" for p, o, a, b, v in SURVEY_ROWS) + ".",
    caption="Un point d'accès au plafond du couloir suffit pour les deux salles, à confirmer par la mesure.",
    svg=survey_svg(SURVEY_ROWS),
)
RECETTE_FIGURE = Figure(
    key="pr30-fiche-recette",
    title="Fiche de recette des postes",
    alt=_recette_alt(),
    caption="Le premier contrôle en échec désigne la piste ; les suivants ne prouvent rien tant qu'il n'est pas corrigé.",
    svg=recette_svg(RECETTE_RESULTS),
)
TREE_FIGURE = Figure(
    key="pr30-arbre-recette",
    title=f"Arbre — {RECETTE_TREE.title}",
    alt=tree_alt(RECETTE_TREE),
    caption="On descend tant que la réponse est « oui » ; au premier « non », on traite cette piste seulement.",
    svg=decision_tree_svg(RECETTE_TREE.questions, RECETTE_TREE.final),
)
SECURITY_FIGURE = Figure(
    key="pr30-liste-securite",
    title="Liste de sécurité de l'installation",
    alt="Liste de sécurité en trois parties. " + " ".join(
        f"{title} : " + " ; ".join(items) + "." for title, items in SECURITY_CHECKLIST),
    caption="À cocher avant la recette ; les identifiants sont remis sous pli, jamais écrits dans le rapport.",
    svg=checklist_svg(SECURITY_CHECKLIST),
)
LAB_FIGURE = _proc_figure("pr30-procedure-laboratoire", 1, PROCEDURES[0][0], LAB_STEPS,
                          "Huit phases ; chaque étude de cas du cours correspond à une ou deux phases.")
RECETTE_PROC_FIGURE = _proc_figure("pr30-procedure-recette", 2, PROCEDURES[1][0], RECETTE_STEPS,
                                   "La recette se fait avec le client, sur des critères écrits avant.")
WIN_FIGURE = _proc_figure("pr30-procedure-windows", 3, PROCEDURES[2][0], INSTALL_WIN_STEPS,
                          "Station ETUDES2, livrée sans système ; même trame pour la mise à niveau de COMPTA.")
LINUX_FIGURE = _proc_figure("pr30-procedure-ubuntu", 4, PROCEDURES[3][0], INSTALL_LINUX_STEPS,
                            "PC LINUX1, non compatible Windows 11 : un système libre maintenu.")

PR30_FIGURES: tuple[Figure, ...] = (
    LAB_FIGURE,
    PLAN_FIGURE,
    RACK_FIGURE,
    PINOUT_FIGURE,
    LINKS_FIGURE,
    LAN_FIGURE,
    MATRIX_FIGURE,
    WIN_FIGURE,
    LINUX_FIGURE,
    SURVEY_FIGURE,
    SECURITY_FIGURE,
    RECETTE_PROC_FIGURE,
    TREE_FIGURE,
    RECETTE_FIGURE,
)

# Schémas à compléter (exercices), servis en fichiers statiques comme PR18 à PR29 ------------

MARKS = ("①", "②", "③", "④")
RACK_BLANKS: dict[int, str] = {0: "①", 2: "②", 5: "③", 6: "④"}
RACK_BLANK_ANSWERS = {mark: RACK_LAYOUT[index].name for index, mark in RACK_BLANKS.items()}
RACK_BLANK_FIGURE = Figure(
    key="pr30-baie-a-completer",
    title="Baie du local technique à compléter",
    alt=(f"Baie de {RACK_U} U, du haut vers le bas : "
         + " ; ".join(f"{RACK_BLANKS[i]} ({item.units} U)" if i in RACK_BLANKS else f"{item.name} ({item.units} U)"
                      for i, item in enumerate(RACK_LAYOUT)) + "."),
    caption="Schéma à compléter : nomme les éléments ①, ②, ③ et ④ et justifie leur place.",
    svg=rack_svg(RACK_LAYOUT, RACK_U, blanks=RACK_BLANKS, title=f"Baie {RACK_U} U à compléter"),
)
TREE_BLANK_NUMBERS = (1, 2, 4, 6)
TREE_BLANK_QUESTIONS, TREE_BLANK_ANSWERS = _blank_tree(RECETTE_TREE, TREE_BLANK_NUMBERS)
TREE_BLANK_FIGURE = Figure(
    key="pr30-arbre-recette-a-completer",
    title="Arbre de recette d'un poste à compléter",
    alt=tree_alt(RECETTE_TREE, TREE_BLANK_QUESTIONS),
    caption="Schéma à compléter : piste à suivre en ①, ②, ③ et ④ quand la réponse est « non ».",
    svg=decision_tree_svg(TREE_BLANK_QUESTIONS, RECETTE_TREE.final),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (RACK_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr30-baie-a-completer.svg"),
    (TREE_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr30-arbre-recette-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR29)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


__all__ = [  # réexports utilisés par le cours et la banque
    "BOX_M",
    "MODEL_DOMAIN",
    "MODEL_WG",
    "POE_OK",
    "T_WIRING",
    "W11_NO",
    "passphrase_issues",
    "unc",
]

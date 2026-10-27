"""PR25 « Wi-Fi : configuration, couverture, sécurité et diagnostic » — données de référence,
calculs, relevés de commandes fictifs et schémas SVG (ticket #224).

Tout est construit **depuis des données** de ce module, contrôlées par
`tests/test_ticket224_ampcr_pratique_pr25.py` (qui recalcule indépendamment) :

- architecture (box/routeur, switch, serveur DHCP, points d'accès câblés, répéteur, mesh,
  clients ; SSID et BSSID) ;
- normes IEEE 802.11 utiles (`STANDARDS`) ; canaux 2,4 GHz (fréquence centrale,
  chevauchement, 1/6/11, choix du canal le moins encombré : `center_24`, `overlaps_24`,
  `best_channel_24`) ; canaux 5 GHz et 6 GHz autorisés en Europe et blocs par largeur de
  canal (`blocks_5`, `blocks_6`) ;
- couverture : affaiblissement en espace libre + obstacles (`fspl_db`, `received_dbm`),
  qualité affichée par Windows (`quality_pct`), appréciation du signal (`signal_verdict`),
  débit de liaison et débit utile, y compris derrière un répéteur (`link_rate`,
  `useful_mbps`, `repeater_mbps`) ;
- sécurité : modes classés (`SECURITY_MODES`), contrôle d'une clé (`passphrase_issues`) et
  audit d'une configuration de point d'accès (`audit_config`) ;
- diagnostic dans l'ordre (`WIFI_CHECKS`, `wifi_checks`, `wifi_diagnosis`, `first_failure`) ;
- trois procédures illustrées et quatre schémas à compléter servis aussi en fichiers
  statiques (`STATIC_FIGURES`).

Valeurs de référence : IEEE 802.11 (normes b/a/g/n/ac/ax/be, débits maximaux théoriques),
plan de canaux ETSI / décisions européennes (2,4 GHz : canaux 1 à 13, 2412 à 2472 MHz ; 5 GHz :
36 à 64 et 100 à 140, DFS à partir de 52 ; 6 GHz : 5945 à 6425 MHz, 24 canaux de 20 MHz),
Wi-Fi Alliance (WPA2 : AES-CCMP ; WPA3 : SAE, obligatoire en 6 GHz ; WEP et TKIP interdits
pour un réseau certifié récent ; WPS PIN vulnérable), Microsoft (`netsh wlan`, qualité du
signal 0 % = −100 dBm, 100 % = −50 dBm, interpolation linéaire). Formule d'affaiblissement en
espace libre : FSPL (dB) = 20 log10(d en m) + 20 log10(f en MHz) − 27,55.

**Conventions du cours**, signalées dans le texte : réseau de l'atelier de PR24
(192.168.20.0/24, box .1, serveur DHCP/DNS SRV-01 .5, AP-01 .30) ; puissance rayonnée de
20 dBm ; affaiblissements des obstacles en ordres de grandeur ; seuils de signal −60 / −67 /
−75 dBm ; débit utile = moitié du débit de liaison, partagé entre clients ; répéteur à une
radio = débit divisé par deux. Ce sont des **estimations simplifiées** : la mesure sur place
fait foi. Personnes, postes et entreprises **fictifs**. Chaque schéma porte son information en
texte : la couleur n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une
photographie.
"""

import math
from dataclasses import dataclass, field
from html import escape

from app.v1.ampcr_pratique_pr20_figures import Host, ipconfig_all_lines
from app.v1.ampcr_pratique_pr24_figures import (
    AP_IP,
    DOMAIN,
    GUEST_NETWORK,
    GUEST_SSID,
    GUEST_VLAN,
    LAN_NETWORK,
    LAN_PREFIX,
    NS_OK,
    NS_TIMEOUT,
    ROUTER_IP,
    SERVER_IP,
    SSID,
    WEB_IP,
    WEB_NAME,
    WifiStatus,
    netsh_wlan_lines,
    nslookup_lines,
    win_ping_lines,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56
FICTIVE_LABEL = "capture fictive — présentation simplifiée"
_STROKE = "#33415c"
_FILL = "#dbe4f3"
_SOFT = "#f4f6fb"
_GOOD = "#e9f5ec"
_WARN = "#fff3c4"
_BAD = "#fbecec"


def fr(value: float) -> str:
    """Nombre à la française : virgule décimale, sans « ,0 » inutile."""
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


# =============================================================================================
# 1. Réseau de référence (atelier de PR24) et architecture
# =============================================================================================

AP1_NAME, AP2_NAME = "AP-01", "AP-02"
AP2_IP = "192.168.20.31"
REPEATER_NAME = "REP-01"
BSSID_AP1_24, BSSID_AP1_5 = "9c:53:22:10:20:31", "9c:53:22:10:20:32"
BSSID_AP2_24, BSSID_AP2_5 = "9c:53:22:10:21:31", "9c:53:22:10:21:32"
GUEST_GATEWAY = "10.30.0.1"

# Rôles des équipements (architecture) : (nom, rôle, liaison, détail)
ROLES: tuple[tuple[str, str, str, str], ...] = (
    ("Box", "routeur : passerelle, NAT et pare-feu vers Internet", "câble", f"{ROUTER_IP}"),
    ("SRV-01", "serveur DHCP et DNS (distribue les adresses)", "câble", f"{SERVER_IP}"),
    (AP1_NAME, "point d'accès câblé (PoE), rez-de-chaussée", "câble", f"{AP_IP}"),
    (AP2_NAME, "point d'accès câblé, étage", "câble", f"{AP2_IP}"),
    (REPEATER_NAME, "répéteur : retransmet le signal d'un point d'accès, sans câble", "radio", "annexe"),
    ("Clients", "portables, smartphones : associés à un point d'accès", "radio", "DHCP"),
)

# Comparaison des façons d'étendre la couverture : (solution, liaison vers le réseau, débit, quand)
EXTENSIONS: tuple[tuple[str, str, str, str], ...] = (
    ("Point d'accès câblé supplémentaire", "câble Ethernet (PoE possible)",
     "plein débit, chaque point d'accès sur son canal", "meilleure solution dès qu'un câble est possible"),
    ("Système mesh (maillé)", "radio entre les bornes (ou câble si disponible)",
     "bon si les bornes se reçoivent bien ; une radio dédiée aide", "maison ou petit bureau sans câblage"),
    ("Répéteur", "radio, reprend le signal d'un point d'accès",
     "souvent divisé par deux (une radio) ; dépend du signal reçu", "dépannage ponctuel d'une zone"),
)

# =============================================================================================
# 2. Normes et bandes
# =============================================================================================

# (norme IEEE, nom commercial, bandes, débit maximal théorique en Mb/s)
STANDARDS: tuple[tuple[str, str, str, int], ...] = (
    ("802.11b", "—", "2,4 GHz", 11),
    ("802.11a", "—", "5 GHz", 54),
    ("802.11g", "—", "2,4 GHz", 54),
    ("802.11n", "Wi-Fi 4", "2,4 et 5 GHz", 600),
    ("802.11ac", "Wi-Fi 5", "5 GHz", 6933),
    ("802.11ax", "Wi-Fi 6 / 6E", "2,4 et 5 GHz (+ 6 GHz en 6E)", 9608),
    ("802.11be", "Wi-Fi 7", "2,4, 5 et 6 GHz", 46120),
)

BAND_24, BAND_5, BAND_6 = "2,4 GHz", "5 GHz", "6 GHz"
BANDS = (BAND_24, BAND_5, BAND_6)
BAND_FREQ_MHZ: dict[str, int] = {BAND_24: 2437, BAND_5: 5180, BAND_6: 5975}  # canal 6, 36, 5 (6 GHz)

# 2,4 GHz : canaux 1 à 13 autorisés en Europe ; 5 MHz entre deux numéros, ~22 MHz occupés.
EU_24_CHANNELS: tuple[int, ...] = tuple(range(1, 14))
NON_OVERLAP_24: tuple[int, ...] = (1, 6, 11)
OVERLAP_SPACING_24 = 5  # deux canaux distants de moins de 5 numéros se chevauchent


def center_24(channel: int) -> int:
    """Fréquence centrale (MHz) d'un canal 2,4 GHz : 2407 + 5 × n (le canal 14, japonais, à part)."""
    if channel == 14:
        return 2484
    if not 1 <= channel <= 13:
        raise ValueError(channel)
    return 2407 + 5 * channel


def overlaps_24(a: int, b: int) -> bool:
    """Deux canaux 2,4 GHz se gênent s'ils sont identiques ou distants de moins de 5 numéros
    (centres à moins de 25 MHz pour ~22 MHz occupés chacun)."""
    return abs(a - b) < OVERLAP_SPACING_24


STRONG_NEIGHBOR_DBM = -80  # voisin reçu au-dessus : il gêne (convention du cours)


@dataclass(frozen=True)
class Neighbor:
    ssid: str
    channel: int
    dbm: int
    bssid: str = ""


def interference_24(channel: int, neighbors: tuple[Neighbor, ...]) -> tuple[int, int]:
    """(nombre de voisins forts sur un canal qui chevauche, signal du plus fort, −100 si aucun)."""
    hits = [n.dbm for n in neighbors if n.dbm >= STRONG_NEIGHBOR_DBM and overlaps_24(channel, n.channel)]
    return len(hits), max(hits, default=-100)


def best_channel_24(neighbors: tuple[Neighbor, ...], choices: tuple[int, ...] = NON_OVERLAP_24) -> int:
    """Canal parmi 1, 6, 11 le moins gêné : moins de voisins forts, puis voisin le plus faible."""
    return min(choices, key=lambda ch: (*interference_24(ch, neighbors), ch))


# 5 GHz en Europe : 36 à 64 et 100 à 140 (le 144 et les canaux 149+ ne sont pas utilisés ici).
EU_5_CHANNELS: tuple[int, ...] = (36, 40, 44, 48, 52, 56, 60, 64,
                                  100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140)
DFS_FROM = 52  # à partir du canal 52 : détection radar (DFS) obligatoire
_SEGMENTS_5: tuple[tuple[int, ...], ...] = (
    (36, 40, 44, 48, 52, 56, 60, 64),
    (100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144),
)
WIDTHS: tuple[int, ...] = (20, 40, 80, 160)


def center_5(channel: int) -> int:
    return 5000 + 5 * channel


def blocks_5(width: int, allowed: tuple[int, ...] = EU_5_CHANNELS) -> tuple[tuple[int, ...], ...]:
    """Blocs de canaux utilisables pour une largeur donnée : groupes alignés de width/20 canaux
    consécutifs, chacun entièrement autorisé (un bloc qui aurait besoin du 144 est perdu)."""
    n = width // 20
    out: list[tuple[int, ...]] = []
    for segment in _SEGMENTS_5:
        for i in range(0, len(segment) - n + 1, n):
            block = segment[i:i + n]
            if all(ch in allowed for ch in block):
                out.append(block)
    return tuple(out)


def is_dfs(block: tuple[int, ...]) -> bool:
    return any(ch >= DFS_FROM for ch in block)


# 6 GHz en Europe : 5945–6425 MHz, canaux 1, 5, 9 … 93 (centre 5950 + 5 × n).
EU_6_CHANNELS: tuple[int, ...] = tuple(range(1, 94, 4))
SIX_GHZ_RANGE = (5945, 6425)


def center_6(channel: int) -> int:
    return 5950 + 5 * channel


def blocks_6(width: int) -> tuple[tuple[int, ...], ...]:
    n = width // 20
    return tuple(EU_6_CHANNELS[i:i + n] for i in range(0, len(EU_6_CHANNELS) - n + 1, n))


BAND_FACTS: tuple[tuple[str, str, str, str, str], ...] = (
    (BAND_24, "13 (1, 6, 11 sans chevauchement)", "la plus grande ; traverse mieux les murs",
     "encombrée : voisins, Bluetooth, micro-ondes", "tous les appareils, objets connectés"),
    (BAND_5, f"{len(EU_5_CHANNELS)} de 20 MHz (DFS dès le 52)", "plus courte que 2,4 GHz",
     "moins encombrée ; plus de débit", "portables et smartphones récents"),
    (BAND_6, f"{len(EU_6_CHANNELS)} de 20 MHz", "la plus courte",
     "très peu encombrée ; WPA3 obligatoire", "appareils Wi-Fi 6E ou 7 seulement"),
)

# =============================================================================================
# 3. Couverture, signal et débit
# =============================================================================================

EIRP_DBM = 20  # puissance rayonnée du point d'accès (100 mW, limite européenne en 2,4 GHz)

# Affaiblissement d'un obstacle (dB) en 2,4 GHz et en 5 GHz : ordres de grandeur du cours.
OBSTACLES: dict[str, tuple[int, int]] = {
    "vitre": (2, 3),
    "cloison": (3, 4),
    "brique": (6, 10),
    "béton": (12, 18),
    "dalle": (15, 25),
    "métal": (20, 25),
}
OBSTACLE_LABELS: dict[str, str] = {
    "vitre": "vitre simple",
    "cloison": "cloison en plaques de plâtre",
    "brique": "mur de briques",
    "béton": "mur en béton",
    "dalle": "dalle d'étage en béton",
    "métal": "porte, armoire ou rayonnage métallique",
}

SIGNAL_EXCELLENT, SIGNAL_GOOD, SIGNAL_WEAK, SIGNAL_BAD = "excellent", "bon", "faible", "insuffisant"
SIGNAL_THRESHOLDS: tuple[tuple[int, str], ...] = ((-60, SIGNAL_EXCELLENT), (-67, SIGNAL_GOOD), (-75, SIGNAL_WEAK))
TARGET_DBM = -67  # objectif de couverture : navigation, visioconférence
VISIBLE_DBM = -85  # en dessous, le réseau n'apparaît plus (ou pas de façon utilisable)


def fspl_db(distance_m: float, freq_mhz: float) -> float:
    """Affaiblissement en espace libre : 20 log10(d m) + 20 log10(f MHz) − 27,55."""
    return 20 * math.log10(distance_m) + 20 * math.log10(freq_mhz) - 27.55


def obstacle_loss(obstacles: tuple[str, ...], band: str) -> int:
    index = 0 if band == BAND_24 else 1
    return sum(OBSTACLES[o][index] for o in obstacles)


def received_dbm(distance_m: float, band: str, obstacles: tuple[str, ...] = (), *, eirp: int = EIRP_DBM) -> int:
    """Signal reçu estimé (dBm, arrondi) : puissance rayonnée − espace libre − obstacles."""
    return round(eirp - fspl_db(distance_m, BAND_FREQ_MHZ[band]) - obstacle_loss(obstacles, band))


def signal_verdict(dbm: float) -> str:
    for threshold, verdict in SIGNAL_THRESHOLDS:
        if dbm >= threshold:
            return verdict
    return SIGNAL_BAD


def quality_pct(dbm: float) -> int:
    """Qualité affichée par Windows (`netsh wlan`) : 0 % = −100 dBm, 100 % = −50 dBm, linéaire."""
    return int(max(0, min(100, 2 * (dbm + 100))))


def dbm_from_pct(pct: int) -> int:
    return round(pct / 2 - 100)


# Débit de liaison négocié par un client 802.11n 2×2 en 20 MHz selon le signal (convention).
LINK_RATES: tuple[tuple[int, int], ...] = ((-60, 144), (-67, 104), (-75, 52), (-82, 13))


def link_rate(dbm: float) -> int:
    for threshold, rate in LINK_RATES:
        if dbm >= threshold:
            return rate
    return 0


def useful_mbps(link_mbps: float, clients: int = 1) -> float:
    """Débit utile estimé : moitié du débit de liaison, partagé entre les clients actifs."""
    return link_mbps * 0.5 / clients


def repeater_mbps(uplink_dbm: float, client_dbm: float) -> float:
    """Débit utile derrière un répéteur à une radio : le plus faible des deux liens, puis divisé
    par deux (chaque paquet passe deux fois sur la même radio), puis moitié utile."""
    return useful_mbps(min(link_rate(uplink_dbm), link_rate(client_dbm)) / 2)


@dataclass(frozen=True)
class SurveyPoint:
    key: str
    place: str
    distance_m: float
    obstacles: tuple[str, ...]
    x: int  # position sur le plan (schéma non à l'échelle)
    y: int

    def dbm(self, band: str) -> int:
        return received_dbm(self.distance_m, band, self.obstacles)


SURVEY: tuple[SurveyPoint, ...] = (
    SurveyPoint("P1", "Atelier", 6, (), 92, 128),
    SurveyPoint("P2", "Bureau", 10, ("brique",), 252, 70),
    SurveyPoint("P3", "Salle de réunion", 14, ("brique", "cloison"), 252, 168),
    SurveyPoint("P4", "Stock", 18, ("béton", "métal"), 340, 128),
    SurveyPoint("P5", "Étage (au-dessus de l'atelier)", 8, ("dalle",), 92, 34),
)
SURVEY_BY_KEY = {p.key: p for p in SURVEY}


def survey_table(points: tuple[SurveyPoint, ...] = SURVEY) -> tuple[tuple[str, int, str, int, str], ...]:
    return tuple(
        (p.key, p.dbm(BAND_24), signal_verdict(p.dbm(BAND_24)), p.dbm(BAND_5), signal_verdict(p.dbm(BAND_5)))
        for p in points
    )


# Répéteur : deux emplacements comparés (même atelier, annexe au fond du terrain).
@dataclass(frozen=True)
class RepeaterPlacement:
    label: str
    uplink_m: float
    uplink_obstacles: tuple[str, ...]
    client_m: float
    client_obstacles: tuple[str, ...]

    @property
    def uplink_dbm(self) -> int:
        return received_dbm(self.uplink_m, BAND_24, self.uplink_obstacles)

    @property
    def client_dbm(self) -> int:
        return received_dbm(self.client_m, BAND_24, self.client_obstacles)

    @property
    def mbps(self) -> float:
        return repeater_mbps(self.uplink_dbm, self.client_dbm)


REPEATER_BAD = RepeaterPlacement("Répéteur dans l'annexe, près du portable", 30, ("béton", "béton", "brique"), 3, ())
REPEATER_GOOD = RepeaterPlacement("Répéteur à mi-chemin, dans le couloir", 12, ("béton",), 18, ("béton",))

# =============================================================================================
# 4. Sécurité
# =============================================================================================

SEC_REFUSE, SEC_MIN, SEC_BEST = "À refuser", "Acceptable", "Recommandé"
SEC_VERDICTS = (SEC_REFUSE, SEC_MIN, SEC_BEST)

OPEN, WEP, WPA_TKIP, WPA2_PSK, WPA2_WPA3, WPA3_SAE, ENTERPRISE = (
    "Ouvert", "WEP", "WPA", "WPA2-Personnel", "WPA2/WPA3-Personnel", "WPA3-Personnel", "WPA2/WPA3-Entreprise",
)


@dataclass(frozen=True)
class SecurityMode:
    name: str
    cipher: str
    verdict: str
    why: str


SECURITY_MODES: tuple[SecurityMode, ...] = (
    SecurityMode(OPEN, "aucun", SEC_REFUSE, "trafic radio lisible par tous ; jamais pour le réseau interne"),
    SecurityMode(WEP, "RC4", SEC_REFUSE, "clé retrouvée en quelques minutes ; obsolète"),
    SecurityMode(WPA_TKIP, "TKIP", SEC_REFUSE, "obsolète et retiré ; limite le débit à 54 Mb/s"),
    SecurityMode(WPA2_PSK, "AES-CCMP", SEC_MIN, "clé partagée (PSK) : sûr si la clé est longue et WPS coupé"),
    SecurityMode(WPA2_WPA3, "AES-CCMP", SEC_MIN, "mode de transition : WPA3 pour les appareils qui le gèrent"),
    SecurityMode(WPA3_SAE, "AES-CCMP", SEC_BEST, "échange SAE : résiste aux attaques par dictionnaire"),
    SecurityMode(ENTERPRISE, "AES", SEC_BEST, "802.1X/RADIUS : un identifiant par personne, révocable"),
)
SECURITY_BY_NAME = {m.name: m for m in SECURITY_MODES}

COMMON_KEYS = frozenset({"password", "motdepasse", "azerty123", "123456789", "12345678", "wifi2026", "bienvenue"})


def passphrase_issues(key: str, *, names: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Défauts d'une clé WPA2/WPA3-Personnel (convention du cours : 12 caractères au moins,
    trois types de caractères ou une phrase de 20 caractères et plus, rien de devinable)."""
    issues: list[str] = []
    if not 8 <= len(key) <= 63:
        return ("longueur hors de 8 à 63 caractères : refusée par le point d'accès",)
    if len(key) < 12:
        issues.append("trop courte (moins de 12 caractères)")
    kinds = sum((any(c.islower() for c in key), any(c.isupper() for c in key),
                 any(c.isdigit() for c in key), any(not c.isalnum() for c in key)))
    if len(key) < 20 and kinds < 3:
        issues.append("peu variée (moins de trois types de caractères)")
    lowered = key.lower()
    if any(name.lower() in lowered for name in names if name):
        issues.append("contient le nom du réseau ou de l'entreprise")
    if lowered in COMMON_KEYS:
        issues.append("mot de passe courant, essayé en premier")
    return tuple(issues)


@dataclass(frozen=True)
class ApConfig:
    ssid: str
    security: str
    passphrase: str
    wps: bool = False
    admin_default: bool = False
    firmware_current: bool = True
    channel_24: int = 1
    width_24: int = 20
    ssid_hidden: bool = False
    guest_isolated: bool | None = None  # None : pas de réseau invités
    dhcp_sources: int = 1
    names: tuple[str, ...] = field(default=())


def audit_config(cfg: ApConfig) -> tuple[tuple[str, str], ...]:
    """Défauts d'une fiche de configuration : (paramètre, correction)."""
    out: list[tuple[str, str]] = []
    if SECURITY_BY_NAME[cfg.security].verdict == SEC_REFUSE:
        out.append(("Sécurité", f"{cfg.security} à remplacer par WPA3-Personnel ou WPA2/WPA3-Personnel (AES)"))
    if passphrase_issues(cfg.passphrase, names=(cfg.ssid, *cfg.names)):
        out.append(("Clé", "nouvelle clé longue (12+ caractères variés ou phrase de 20+), sans nom devinable"))
    if cfg.wps:
        out.append(("WPS", "désactiver (code PIN vulnérable)"))
    if cfg.admin_default:
        out.append(("Administration", "changer le mot de passe d'administration par défaut"))
    if not cfg.firmware_current:
        out.append(("Micrologiciel", "installer la dernière version (failles corrigées)"))
    if cfg.channel_24 not in NON_OVERLAP_24:
        out.append(("Canal 2,4 GHz", "1, 6 ou 11, selon les voisins relevés"))
    if cfg.width_24 != 20:
        out.append(("Largeur 2,4 GHz", "20 MHz (40 MHz chevauche presque toute la bande)"))
    if cfg.ssid_hidden:
        out.append(("SSID masqué", "le diffuser : le masquer ne protège pas et gêne les connexions"))
    if cfg.guest_isolated is False:
        out.append(("Invités", "isoler le réseau invités du réseau interne (VLAN, isolation des clients)"))
    if cfg.dhcp_sources != 1:
        out.append(("DHCP", "une seule source DHCP par réseau (répéteur en mode point d'accès ou pont)"))
    return tuple(out)


REFERENCE_CONFIG = ApConfig(SSID, WPA2_WPA3, "Copeaux-Rabot-Établi-2026!", channel_24=6, guest_isolated=True,
                            names=("Durant", "Atelier"))

# =============================================================================================
# 5. Diagnostic d'un poste Wi-Fi, dans l'ordre
# =============================================================================================

W_INVISIBLE = "Réseau invisible : radio coupée, SSID masqué, bande non prise en charge ou hors de portée"
W_KEY = "Authentification : clé incorrecte ou sécurité non prise en charge"
W_IP = "Adressage : pas de bail DHCP (169.254) ou adresse d'un autre réseau"
W_INTERNET = "Connecté sans Internet : passerelle, DNS ou liaison de la box"
W_SIGNAL = "Couverture : signal faible au poste (distance, obstacles, emplacement)"
W_REPEATER = "Répéteur mal placé : il reçoit mal le point d'accès"
W_CHANNEL = "Interférences : canal encombré ou qui chevauche un voisin"
W_OK = "Wi-Fi conforme : signal suffisant, Internet joignable"
WIFI_DIAGNOSES = (W_INVISIBLE, W_KEY, W_IP, W_INTERNET, W_SIGNAL, W_REPEATER, W_CHANNEL)

WIFI_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("visible", "Le SSID attendu est visible à l'endroit du poste", W_INVISIBLE),
    ("auth", "Le poste s'associe et la clé est acceptée", W_KEY),
    ("ip", "Le poste reçoit une adresse du bon réseau", W_IP),
    ("internet", "Passerelle, DNS et Internet répondent", W_INTERNET),
    ("signal", f"Signal au poste d'au moins {TARGET_DBM} dBm", W_SIGNAL),
    ("repeteur", f"Le répéteur reçoit le point d'accès à {TARGET_DBM} dBm ou plus", W_REPEATER),
    ("canal", "Aucun voisin fort sur un canal qui chevauche", W_CHANNEL),
)
WIFI_KEYS = tuple(k for k, _w, _d in WIFI_CHECKS)


@dataclass(frozen=True)
class WifiState:
    radio_on: bool = True  # radio du point d'accès et du poste (mode avion, interrupteur, horaire)
    ssid_broadcast: bool = True
    band_supported: bool = True  # la carte du poste gère la bande (et le canal) émis
    signal_dbm: int = -55
    key_ok: bool = True
    security_supported: bool = True  # la carte gère le mode (ex. WPA3 seul)
    address_ok: bool = True  # bail DHCP du bon réseau
    gateway_ok: bool = True
    dns_ok: bool = True
    wan_ok: bool = True
    repeater_uplink_dbm: int | None = None  # None : pas de répéteur
    strong_overlaps: int = 0


def wifi_checks(state: WifiState) -> dict[str, bool]:
    return {
        "visible": state.radio_on and state.ssid_broadcast and state.band_supported and state.signal_dbm >= VISIBLE_DBM,
        "auth": state.key_ok and state.security_supported,
        "ip": state.address_ok,
        "internet": state.gateway_ok and state.dns_ok and state.wan_ok,
        "signal": state.signal_dbm >= TARGET_DBM,
        "repeteur": state.repeater_uplink_dbm is None or state.repeater_uplink_dbm >= TARGET_DBM,
        "canal": state.strong_overlaps == 0,
    }


def wifi_diagnosis(results: dict[str, bool]) -> str:
    """Le premier contrôle en échec désigne la piste."""
    for key, _what, diagnosis in WIFI_CHECKS:
        if not results[key]:
            return diagnosis
    return W_OK


def first_failure(failed: str, keys: tuple[str, ...] = WIFI_KEYS) -> dict[str, bool]:
    index = keys.index(failed)
    return {k: i < index for i, k in enumerate(keys)}


# =============================================================================================
# 6. Procédures
# =============================================================================================

CONFIG_STEPS: tuple[tuple[str, str], ...] = (
    ("Placer", "Central, en hauteur, hors armoire, loin du métal et du micro-ondes ; câblé au switch."),
    ("Sécuriser l'accès", "Par câble : mot de passe d'administration changé, micrologiciel à jour."),
    ("SSID et bandes", "Nom neutre, sans nom de famille ni modèle ; 2,4 et 5 GHz actives."),
    ("Canaux et largeur", "2,4 GHz : 1, 6 ou 11 en 20 MHz ; 5 GHz : canal libre en 40 ou 80 MHz."),
    ("Sécurité et clé", "WPA3 ou WPA2/WPA3-Personnel, clé longue, WPS désactivé."),
    ("Adressage", "Une seule source DHCP : plage, passerelle et DNS du réseau."),
    ("Invités", f"SSID {GUEST_SSID} isolé du réseau interne, clé distincte."),
    ("Tester et consigner", "Connexion, signal mesuré pièce par pièce, débit ; fiche remise."),
)
COVERAGE_STEPS: tuple[tuple[str, str], ...] = (
    ("Mesurer", f"Signal en dBm pièce par pièce ; repérer les zones sous {TARGET_DBM} dBm."),
    ("Expliquer", "Distance, murs, dalle, métal, canal encombré, bande 5 GHz trop loin."),
    ("Déplacer d'abord", "Point d'accès central, en hauteur, sorti de l'armoire."),
    ("Câbler si possible", "Second point d'accès câblé : même SSID et sécurité, autre canal."),
    ("Sinon mesh ou répéteur", f"À mi-chemin, là où il reçoit {TARGET_DBM} dBm ou mieux."),
    ("Vérifier", "Nouvelle mesure, débit, passage d'un point d'accès à l'autre en marchant."),
    ("Consigner", "Plan avec emplacements, canaux et mesures."),
)
TROUBLE_STEPS: tuple[tuple[str, str], ...] = (
    ("Constater", "Message exact ; un poste ou tous ; quel endroit ; depuis quand."),
    ("Réseau visible ?", "netsh wlan show networks ; radio du poste et du point d'accès, bande."),
    ("Clé et sécurité", "Oublier le réseau, ressaisir la clé ; mode WPA pris en charge."),
    ("Adresse", "ipconfig : bon réseau, pas 169.254, une seule source DHCP."),
    ("Internet", "ping passerelle, ping adresse Internet, nslookup d'un nom."),
    ("Signal et répéteur", f"netsh wlan show interfaces : {TARGET_DBM} dBm ou mieux ; lien du répéteur."),
    ("Canal", "Voisins sur le même canal ou qui chevauchent : 1, 6, 11 ou 5 GHz."),
    ("Corriger et consigner", "Correction minimale, test, compte rendu."),
)
ASSOCIATION_STEPS: tuple[tuple[str, str], ...] = (
    ("Découverte", "Le poste écoute les balises (beacons) ou envoie des sondes : SSID, BSSID, signal."),
    ("Association", "Il choisit un BSSID et s'y associe ; en WPA3, l'échange SAE a lieu ici."),
    ("Clés", "Échange en 4 temps avec la clé ; en Entreprise, 802.1X/RADIUS vérifie d'abord l'identifiant."),
    ("DHCP", "Découverte, offre, demande, accusé : adresse, masque, passerelle, DNS."),
    ("Passerelle et DNS", "Le poste joint la box puis résout les noms : Internet."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Configurer un point d'accès", CONFIG_STEPS),
    ("Étendre la couverture", COVERAGE_STEPS),
    ("Dépanner un poste Wi-Fi", TROUBLE_STEPS),
)

# Arborescence de l'interface d'administration d'un point d'accès (générique, fictive).
MENU_TREE: tuple[tuple[int, str], ...] = (
    (0, f"Administration du point d'accès (http://{AP_IP})"),
    (1, "Sans fil"),
    (2, "Général : SSID, bande, canal, largeur"),
    (2, "Sécurité : mode WPA, clé, WPS"),
    (2, "Réseau invités : SSID, clé, isolation"),
    (1, "Réseau local"),
    (2, "Adresse du point d'accès, VLAN"),
    (2, "Serveur DHCP : activé ou non, plage"),
    (1, "Système"),
    (2, "Micrologiciel : version, mise à jour"),
    (2, "Mot de passe d'administration"),
    (2, "Sauvegarde de la configuration"),
)

# =============================================================================================
# 7. Relevés fictifs (56 caractères par ligne au plus)
# =============================================================================================


def networks_lines(networks: tuple[tuple[str, str, Neighbor], ...]) -> tuple[str, ...]:
    """`netsh wlan show networks mode=bssid` (extrait) : (SSID, authentification, relevé)."""
    lines = ["C:\\> netsh wlan show networks mode=bssid"]
    for index, (ssid, auth, n) in enumerate(networks, start=1):
        band = BAND_24 if n.channel <= 14 else BAND_5
        lines += [
            f"SSID {index} : {ssid}",
            f"    Authentification : {auth}",
            f"    BSSID 1          : {n.bssid}",
            f"         Signal      : {quality_pct(n.dbm)}%",
            f"         Bande       : {band}",
            f"         Canal       : {n.channel}",
        ]
    return tuple(lines)


def drivers_lines(radios: str, bands: str) -> tuple[str, ...]:
    """`netsh wlan show drivers` (extrait simplifié)."""
    return (
        "C:\\> netsh wlan show drivers",
        "    Pilote            : carte Wi-Fi intégrée",
        f"    Radios prises en charge : {radios}",
        f"    Bandes prises en charge : {bands}",
        "    Prise en charge WPA3    : non",
    )


def wifi_ipconfig_lines(host: Host, *, apipa: bool = False) -> tuple[str, ...]:
    lines = list(ipconfig_all_lines(host, dhcp_server=SERVER_IP if host.ip.startswith("192.168.20.") else None,
                                    apipa=apipa, iface="Wi-Fi"))
    lines[0] = "Carte réseau sans fil Wi-Fi :"
    lines[1] = "   Description. . . . : Carte Wi-Fi intégrée"
    return ("C:\\> ipconfig /all", "", *lines)


def nmcli_lines(rows: tuple[tuple[str, int, int, str], ...]) -> tuple[str, ...]:
    """`nmcli -f SSID,CHAN,SIGNAL,SECURITY dev wifi list` (Linux) : (SSID, canal, %, sécurité)."""
    lines = ["$ nmcli -f SSID,CHAN,SIGNAL,SECURITY dev wifi", "SSID              CHAN  SIGNAL  SECURITY"]
    lines += [f"{ssid:<18}{chan:<6}{sig:<8}{sec}" for ssid, chan, sig, sec in rows]
    return tuple(lines)


# Relevé de référence : voisins de l'atelier en 2,4 GHz (bureau d'en face, boulangerie…).
NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Boulangerie-Wifi", 1, -58, "a0:21:b7:01:02:03"),
    Neighbor("Proximus-7F3A", 3, -71, "f4:ca:e5:11:22:33"),
    Neighbor("Cabinet-Lenoir", 11, -88, "00:1d:7e:44:55:66"),
    Neighbor("Livebox-21C0", 13, -79, "c8:cd:72:77:88:99"),
)
NEIGHBORS_BEST = best_channel_24(NEIGHBORS)
NETWORKS_SCAN_LINES = networks_lines(
    ((SSID, "WPA2 - Personnel", Neighbor(SSID, 1, -52, BSSID_AP1_24)),
     *((n.ssid, "WPA2 - Personnel", n) for n in NEIGHBORS[:3])),
)

# =============================================================================================
# 8. Schémas SVG
# =============================================================================================


def _box(x: float, y: float, w: float, lines: list[str], *, key: str = "", dashed: bool = False,
         fill: str = _FILL, h: float | None = None) -> str:
    height = h if h is not None else 12 + 15 * len(lines)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    data = f' data-node="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x}" y="{y}" width="{w}" height="{height}" rx="7" fill="{fill}" stroke="{_STROKE}" '
            f'stroke-width="1.5"{dash}/>'
            + _text_lines(int(x) + 7, int(y) + 17, lines[:1], size=11.5, weight="700")
            + _text_lines(int(x) + 7, int(y) + 31, lines[1:], size=10, step=13))


def _line(x1: float, y1: float, x2: float, y2: float, *, radio: bool = False) -> str:
    dash = ' stroke-dasharray="6 4"' if radio else ""
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{_STROKE}" stroke-width="2"{dash} fill="none"/>'


def _notes(y: int, text: str, parts: list[str], width: int = 380) -> int:
    lines = _wrap(text, 62)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return y + 13 * len(lines)


ARCH_ROWS: tuple[tuple[str, str], ...] = (
    ("box", "Box"),
    ("dhcp", "SRV-01"),
    ("ap", AP2_NAME),
    ("repeteur", REPEATER_NAME),
)
ARCH_VALUES: dict[str, str] = {
    "box": "routeur : passerelle, NAT, pare-feu",
    "dhcp": "serveur DHCP et DNS",
    "ap": "point d'accès câblé, plein débit",
    "repeteur": "répéteur : retransmet par radio",
}


def architecture_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Architecture de l'atelier : Internet → box → switch → SRV-01, AP-01, AP-02 (câbles) ;
    répéteur relié par radio à AP-02 ; clients associés par radio. `blanks` (« box »,
    « dhcp », « ap », « repeteur ») masque le rôle d'un équipement."""
    blanks = blanks or {}

    def role(key: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else ARCH_VALUES[key]

    def kw(key: str) -> dict:
        hidden = key in blanks
        return {"key": "" if hidden else key, "dashed": hidden, "fill": "#ffffff" if hidden else _FILL}

    width = 380
    parts = [_text_lines(width // 2, 16, ["Wi-Fi de l'atelier : qui fait quoi ?"], size=12.5, weight="700",
                         anchor="middle")]
    parts.append(_box(4, 26, 110, ["Internet", "fournisseur d'accès"], fill=_SOFT))
    parts.append(_line(114, 44, 140, 44))
    parts.append(_box(140, 26, 236, [f"Box ({ROUTER_IP})", role("box")], **kw("box")))
    parts.append(_line(258, 68, 258, 90))
    parts.append(_box(140, 90, 236, ["Switch PoE", "relie tous les équipements câblés"], fill=_SOFT))
    parts.append(_line(140, 108, 114, 108))
    parts.append(_box(4, 90, 110, ["SRV-01 (.5)", role("dhcp")], **kw("dhcp"), h=58))
    # deux points d'accès câblés
    parts.append(_line(200, 132, 200, 160))
    parts.append(_line(320, 132, 320, 160))
    parts.append(_box(140, 160, 116, [f"{AP1_NAME} (.30)", "câblé, PoE", "rez-de-chaussée", "canaux 1 et 36"], h=72))
    parts.append(_box(262, 160, 114, [f"{AP2_NAME} (.31)", *_wrap(role("ap"), 17)[:2], "étage : 6 et 44"],
                      **kw("ap"), h=72))
    # répéteur par radio
    parts.append(_line(319, 232, 319, 256, radio=True))
    parts.append(_box(222, 256, 154, [REPEATER_NAME + " (annexe)", *_wrap(role("repeteur"), 24)[:2], "même SSID"],
                      **kw("repeteur"), h=72))
    # clients
    parts.append(_line(198, 232, 198, 256, radio=True))
    parts.append(_box(4, 256, 210, ["Clients (radio)", f"SSID {SSID} : réseau interne", f"SSID {GUEST_SSID} :",
                                    f"VLAN {GUEST_VLAN}, isolé ({GUEST_NETWORK})"], fill=_SOFT, h=72))
    y = 348
    y = _notes(y, "Trait plein = câble ; tirets = radio. Un SSID (nom du réseau) est émis par plusieurs "
               "radios ; chaque radio a son BSSID (adresse MAC). Un seul serveur DHCP par réseau.", parts)
    return _svg(width, y + 6, parts)


def _arch_alt(blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}

    def v(key: str) -> str:
        return f"{blanks[key]} à compléter" if key in blanks else ARCH_VALUES[key]

    return (
        f"Internet relié par câble à la box ({ROUTER_IP}), rôle : {v('box')}. La box est reliée au switch PoE, "
        f"qui relie le serveur SRV-01 ({SERVER_IP}), rôle : {v('dhcp')}, et deux points d'accès câblés : {AP1_NAME} "
        f"({AP_IP}) au rez sur les canaux 1 et 36, et {AP2_NAME} ({AP2_IP}) à l'étage sur les canaux 6 et 44, rôle : "
        f"{v('ap')}. Le répéteur {REPEATER_NAME}, dans l'annexe, est relié par radio à {AP2_NAME}, rôle : "
        f"{v('repeteur')}, même SSID. Les clients s'associent par radio au SSID {SSID} (réseau interne) ou "
        f"{GUEST_SSID} (VLAN {GUEST_VLAN}, réseau {GUEST_NETWORK}, isolé du réseau interne {LAN_NETWORK})."
    )


_CH_LEFT, _CH_STEP = 56, 22  # canal 1 à x = 56, 22 px par numéro de canal (5 MHz)


def _ch_x(channel: float) -> float:
    return _CH_LEFT + (channel - 1) * _CH_STEP


def _arc(channel: int, top: float, base: float, *, dashed: bool = False, bold: bool = False) -> str:
    """Occupation d'un canal : ±11 MHz autour du centre, soit ±2,2 numéros de canal. Un voisin
    (tirets) est marqué `data-neighbor`, un canal sans chevauchement `data-channel`."""
    x1, x2, cx = _ch_x(channel - 2.2), _ch_x(channel + 2.2), _ch_x(channel)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    stroke = "2.5" if bold else "1.5"
    attr = "data-neighbor" if dashed else "data-channel"
    return (f'<path {attr}="{channel}" data-center="{center_24(channel)}" d="M{x1:.1f} {base} '
            f'Q{cx:.1f} {2 * top - base:.1f} {x2:.1f} {base}" fill="none" stroke="{_STROKE}" '
            f'stroke-width="{stroke}"{dash}/>')


def channels_24_svg(neighbors: tuple[Neighbor, ...] = NEIGHBORS, *, blanks: dict[str, str] | None = None) -> str:
    """Canaux 2,4 GHz : les 13 numéros et leur fréquence, les trois canaux sans chevauchement
    (arcs pleins) et les voisins relevés (arcs en tirets, SSID et signal). `blanks` (« c1 »,
    « c2 », « c3 », « choix ») masque un canal sans chevauchement ou le canal conseillé."""
    blanks = blanks or {}
    width, base = 380, 150
    parts = [_text_lines(width // 2, 16, ["Bande 2,4 GHz : canaux et chevauchements"], size=12.5, weight="700",
                         anchor="middle")]
    parts.append(f'<path d="M{_CH_LEFT - 8} {base} H{_ch_x(13) + 8}" stroke="{_STROKE}" stroke-width="1.5"/>')
    for ch in EU_24_CHANNELS:
        x = _ch_x(ch)
        parts.append(f'<path d="M{x:.1f} {base} V{base + 5}" stroke="{_STROKE}" stroke-width="1.2"/>')
        parts.append(_text_lines(int(x), base + 17, [str(ch)], size=10, anchor="middle"))
    scale = f"canal 1 = {center_24(1)} MHz … canal 13 = {center_24(13)} MHz ; 5 MHz entre deux numéros"
    parts.append(_text_lines(width // 2, base + 31, [scale], size=9.5, anchor="middle"))
    for key, ch in zip(("c1", "c2", "c3"), NON_OVERLAP_24, strict=True):
        if key in blanks:
            parts.append(_text_lines(int(_ch_x(ch)), 52, [f"{blanks[key]} ?"], size=12, weight="700", anchor="middle"))
            parts.append(f'<path d="M{_ch_x(ch - 2.2):.1f} {base} Q{_ch_x(ch):.1f} 50 {_ch_x(ch + 2.2):.1f} {base}" '
                         f'fill="none" stroke="{_STROKE}" stroke-width="2.5"/>')
        else:
            parts.append(_arc(ch, 60, base, bold=True))
            parts.append(_text_lines(int(_ch_x(ch)), 52, [f"canal {ch}"], size=11, weight="700", anchor="middle"))
    for i, n in enumerate(neighbors):
        top = 92 + 12 * (i % 3)
        parts.append(_arc(n.channel, top, base, dashed=True))
    y = base + 48
    parts.append(_text_lines(8, y, ["Voisins relevés (tirets) :"], size=10.5, weight="700"))
    y += 14
    for n in neighbors:
        parts.append(_text_lines(14, y, [f"{n.ssid} : canal {n.channel}, {n.dbm} dBm"], size=10.5))
        y += 13
    choice = f"{blanks['choix']} ?" if "choix" in blanks else f"canal {best_channel_24(neighbors)}"
    parts.append(_box(4, y + 4, 372, ["Canal conseillé pour l'atelier", choice],
                      key="" if "choix" in blanks else "choix", dashed="choix" in blanks,
                      fill="#ffffff" if "choix" in blanks else _GOOD))
    y += 50
    y = _notes(y + 14, f"Arcs pleins : 1, 6, 11, les seuls à ne pas se chevaucher. Un voisin gêne s'il est reçu à "
               f"{STRONG_NEIGHBOR_DBM} dBm ou plus sur un canal à moins de 5 numéros.", parts)
    return _svg(width, y + 6, parts)


def _channels_alt(neighbors: tuple[Neighbor, ...] = NEIGHBORS, blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}
    trio = [f"{blanks[k]} à compléter" if k in blanks else str(ch)
            for k, ch in zip(("c1", "c2", "c3"), NON_OVERLAP_24, strict=True)]
    choice = f"{blanks['choix']} à compléter" if "choix" in blanks else f"canal {best_channel_24(neighbors)}"
    return (
        f"Axe des canaux 2,4 GHz de 1 ({center_24(1)} MHz) à 13 ({center_24(13)} MHz), 5 MHz entre deux numéros, "
        f"chaque canal occupe environ 22 MHz. Canaux sans chevauchement : {', '.join(trio)}. Voisins relevés : "
        + "; ".join(f"{n.ssid} canal {n.channel} à {n.dbm} dBm" for n in neighbors)
        + f". Canal conseillé pour l'atelier : {choice}."
    )


def widths_5_svg() -> str:
    """Canaux 5 GHz autorisés en Europe et blocs utilisables selon la largeur (20 à 160 MHz) ;
    les blocs qui demandent la détection radar (DFS) sont en tirets."""
    width = 380
    slots = list(_SEGMENTS_5[0]) + [None] + list(_SEGMENTS_5[1][:-1])  # 144 non autorisé
    left, slot_w = 62, 15.5
    x_of = {ch: left + i * slot_w for i, ch in enumerate(slots) if ch is not None}
    parts = [_text_lines(width // 2, 16, ["Bande 5 GHz (Europe) : canaux selon la largeur"], size=12.5, weight="700",
                         anchor="middle")]
    for i, (ch, x) in enumerate(x_of.items()):
        parts.append(f'<text x="{x + slot_w / 2:.0f}" y="{32 + 9 * (i % 2)}" font-size="8.5" '
                     f'text-anchor="middle">{ch}</text>')
    y = 46
    for w in WIDTHS:
        blocks = blocks_5(w)
        parts.append(_text_lines(6, y + 16, [f"{w} MHz"], size=10.5, weight="700"))
        for block in blocks:
            x1 = x_of[block[0]]
            bw = f"{slot_w * len(block) - 2:.1f}"
            dash = ' stroke-dasharray="4 2"' if is_dfs(block) else ""
            fill = _WARN if is_dfs(block) else _GOOD
            parts.append(f'<rect data-width="{w}" data-block="{block[0]}-{block[-1]}" x="{x1 + 1:.1f}" y="{y + 4}" '
                         f'width="{bw}" height="18" rx="3" fill="{fill}" stroke="{_STROKE}" stroke-width="1"{dash}/>')
        parts.append(_text_lines(6, y + 36, [f"{len(blocks)} canaux de {w} MHz"], size=9.5))
        y += 44
    y = _notes(y + 14, f"Plein : canaux 36 à 48, sans détection radar. Tirets : DFS (52 et au-delà), le point "
               "d'accès change de canal s'il détecte un radar. Plus le canal est large, plus le débit est élevé "
               f"mais moins il y a de canaux. 6 GHz (Wi-Fi 6E/7) : {len(blocks_6(20))} canaux de 20 MHz, "
               f"{len(blocks_6(80))} de 80 MHz.", parts)
    return _svg(width, y + 6, parts)


def _widths_alt() -> str:
    rows = []
    for w in WIDTHS:
        blocks = blocks_5(w)
        rows.append(f"{w} MHz : {len(blocks)} canaux (" + ", ".join(f"{b[0]}-{b[-1]}" if len(b) > 1 else str(b[0])
                                                                 for b in blocks) + ")")
    return ("Canaux 5 GHz autorisés en Europe : 36 à 64 et 100 à 140 ; détection radar (DFS) à partir du 52. "
            + " ; ".join(rows) + f". En 6 GHz : {len(blocks_6(20))} canaux de 20 MHz et {len(blocks_6(80))} de 80 MHz.")


_ROOM_LINES: tuple[tuple[int, int, int, int, str], ...] = (
    # (x1, y1, x2, y2, matériau) : murs intérieurs du plan schématique
    (180, 56, 180, 196, "brique"),
    (180, 126, 300, 126, "cloison"),
    (300, 56, 300, 196, "béton"),
)
AP_POS = (60, 128)


def coverage_svg(points: tuple[SurveyPoint, ...] = SURVEY, *, blanks: dict[str, str] | None = None) -> str:
    """Plan schématique (non à l'échelle) de l'atelier avec AP-01 et les points de mesure ;
    sous le plan, le tableau des signaux estimés 2,4 / 5 GHz et leur appréciation. `blanks`
    (« P3:2,4 », « P4:2,4 », « P5:5 »…) masque une valeur."""
    blanks = blanks or {}
    width = 380
    parts = [_text_lines(width // 2, 16, ["Couverture de AP-01 : mesures estimées"], size=12.5, weight="700",
                         anchor="middle")]
    parts.append(f'<rect x="4" y="56" width="372" height="140" fill="#ffffff" stroke="{_STROKE}" stroke-width="2.5"/>')
    parts.append(f'<rect x="4" y="22" width="176" height="30" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.2" '
                 'stroke-dasharray="4 2"/>')
    parts.append(_text_lines(150, 41, ["étage"], size=9.5, anchor="middle"))
    for x1, y1, x2, y2, mat in _ROOM_LINES:
        parts.append(f'<path data-wall="{mat}" d="M{x1} {y1} L{x2} {y2}" stroke="{_STROKE}" stroke-width="3"/>')
    parts.append(_text_lines(14, 72, ["Atelier"], size=10, weight="700"))
    parts.append(_text_lines(188, 72, ["Bureau"], size=10, weight="700"))
    parts.append(_text_lines(188, 190, ["Réunion"], size=10, weight="700"))
    parts.append(_text_lines(308, 72, ["Stock"], size=10, weight="700"))
    parts.append(_text_lines(308, 86, ["rayonnages"], size=9))
    parts.append(_text_lines(308, 98, ["métalliques"], size=9))
    ax, ay = AP_POS
    parts.append(f'<circle data-ap="{AP1_NAME}" cx="{ax}" cy="{ay}" r="9" fill="{_STROKE}"/>')
    parts.append(_text_lines(ax, ay + 24, [AP1_NAME], size=10, weight="700", anchor="middle"))
    for p in points:
        parts.append(f'<circle cx="{p.x}" cy="{p.y}" r="10" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(_text_lines(p.x, p.y + 4, [p.key], size=9.5, weight="700", anchor="middle"))
    y = 214
    head = ["Point", "Distance, obstacles", BAND_24, BAND_5]
    xs = (6, 44, 236, 310)
    parts.append("".join(_text_lines(x, y, [h], size=10, weight="700") for x, h in zip(xs, head, strict=True)))
    y += 6
    for p in points:
        obstacles = " + ".join(p.obstacles) if p.obstacles else "aucun"
        cells = []
        for band, short in ((BAND_24, "2,4"), (BAND_5, "5")):
            key = f"{p.key}:{short}"
            dbm = p.dbm(band)
            cells.append(f"{blanks[key]} ?" if key in blanks else f"{dbm} dBm")
            cells.append("" if key in blanks else signal_verdict(dbm))
        parts.append(f'<rect data-point="{p.key}" data-24="{p.dbm(BAND_24)}" data-5="{p.dbm(BAND_5)}" x="4" '
                     f'y="{y}" width="372" height="30" rx="4" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="0.8"/>')
        parts.append(_text_lines(xs[0] + 4, y + 13, [p.key], size=10, weight="700"))
        parts.append(_text_lines(xs[1], y + 13, [f"{fr(p.distance_m)} m, {obstacles}"[:34]], size=9.5))
        parts.append(_text_lines(xs[1], y + 25, [p.place[:34]], size=9))
        parts.append(_text_lines(xs[2], y + 13, [cells[0]], size=10, weight="700"))
        parts.append(_text_lines(xs[2], y + 25, [cells[1]], size=9))
        parts.append(_text_lines(xs[3], y + 13, [cells[2]], size=10, weight="700"))
        parts.append(_text_lines(xs[3], y + 25, [cells[3]], size=9))
        y += 34
    y = _notes(y + 12, f"Estimation simplifiée : {EIRP_DBM} dBm rayonnés − affaiblissement en espace libre − "
               f"obstacles. Objectif {TARGET_DBM} dBm ou mieux ; la mesure sur place fait foi.", parts)
    return _svg(width, y + 6, parts)


def _coverage_alt(points: tuple[SurveyPoint, ...] = SURVEY, blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}

    def v(p: SurveyPoint, band: str, short: str) -> str:
        key = f"{p.key}:{short}"
        return f"{blanks[key]} à compléter" if key in blanks else f"{p.dbm(band)} dBm ({signal_verdict(p.dbm(band))})"

    return (
        f"Plan schématique de l'atelier : {AP1_NAME} dans l'atelier ; mur de briques vers le bureau et la salle de "
        "réunion, séparés par une cloison ; mur en béton vers le stock aux rayonnages métalliques ; étage au-dessus de "
        f"l'atelier. Signal estimé ({EIRP_DBM} dBm rayonnés, espace libre et obstacles) : "
        + " ; ".join(
            f"{p.key} {p.place}, {fr(p.distance_m)} m, obstacles {' + '.join(p.obstacles) or 'aucun'} : "
            f"2,4 GHz {v(p, BAND_24, '2,4')}, 5 GHz {v(p, BAND_5, '5')}"
            for p in points)
        + f". Objectif : {TARGET_DBM} dBm ou mieux."
    )


def repeater_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Deux emplacements du répéteur : liens AP → répéteur et répéteur → portable, signal
    estimé de chacun et débit utile obtenu. `blanks` (« mal:lien », « mal:debit », « bien:lien »,
    « bien:debit ») masque une valeur."""
    blanks = blanks or {}
    width = 380
    parts = [_text_lines(width // 2, 16, ["Où placer le répéteur ?"], size=12.5, weight="700", anchor="middle")]
    y = 30
    for tag, rp in (("mal", REPEATER_BAD), ("bien", REPEATER_GOOD)):
        link = f"{blanks[tag + ':lien']} ?" if tag + ":lien" in blanks else f"{rp.uplink_dbm} dBm ({signal_verdict(rp.uplink_dbm)})"
        rate = f"{blanks[tag + ':debit']} ?" if tag + ":debit" in blanks else f"≈ {fr(rp.mbps)} Mb/s utiles"
        parts.append(f'<rect data-placement="{tag}" data-uplink="{rp.uplink_dbm}" data-client="{rp.client_dbm}" '
                     f'x="4" y="{y}" width="372" height="134" rx="8" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.2"/>')
        parts.append(_text_lines(12, y + 18, [rp.label], size=11.5, weight="700"))
        parts.append(_box(12, y + 30, 70, [AP1_NAME, "câblé"], fill=_FILL))
        parts.append(_line(82, y + 50, 158, y + 50, radio=True))
        parts.append(_box(158, y + 30, 76, [REPEATER_NAME, "une radio"], fill=_WARN))
        parts.append(_line(234, y + 50, 300, y + 50, radio=True))
        parts.append(_box(300, y + 30, 70, ["Portable", "client"], fill=_FILL))
        obstacles = " + ".join(rp.uplink_obstacles)
        parts.append(_text_lines(12, y + 84, [f"Lien {AP1_NAME} → {REPEATER_NAME} : {fr(rp.uplink_m)} m, {obstacles}"],
                                 size=9.5))
        parts.append(_text_lines(12, y + 97, [f"signal reçu par le répéteur : {link}"], size=10, weight="700"))
        client_obs = " + ".join(rp.client_obstacles) or "aucun obstacle"
        client_line = f"Lien {REPEATER_NAME} → portable : {fr(rp.client_m)} m, {client_obs}, {rp.client_dbm} dBm"
        parts.append(_text_lines(12, y + 110, [client_line], size=9.5))
        parts.append(_text_lines(12, y + 124, [f"Débit pour le portable : {rate}"], size=10.5, weight="700"))
        y += 142
    y = _notes(y + 8, "Le portable voit un excellent signal… du répéteur. Ce qui compte d'abord, c'est le lien "
               f"entre le point d'accès et le répéteur : {TARGET_DBM} dBm ou mieux. Un répéteur à une radio divise "
               "le débit par deux.", parts)
    return _svg(width, y + 6, parts)


def _repeater_alt(blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}
    out = []
    for tag, rp in (("mal", REPEATER_BAD), ("bien", REPEATER_GOOD)):
        link = (f"{blanks[tag + ':lien']} à compléter" if tag + ":lien" in blanks
                else f"{rp.uplink_dbm} dBm ({signal_verdict(rp.uplink_dbm)})")
        rate = f"{blanks[tag + ':debit']} à compléter" if tag + ":debit" in blanks else f"environ {fr(rp.mbps)} Mb/s"
        out.append(
            f"{rp.label} : lien {AP1_NAME} vers {REPEATER_NAME} sur {fr(rp.uplink_m)} m à travers "
            f"{' + '.join(rp.uplink_obstacles)}, signal {link} ; lien {REPEATER_NAME} vers le portable sur "
            f"{fr(rp.client_m)} m ({' + '.join(rp.client_obstacles) or 'aucun obstacle'}), {rp.client_dbm} dBm ; débit "
            f"utile pour le portable {rate}"
        )
    return "Deux emplacements du répéteur à une radio, en 2,4 GHz. " + ". ".join(out) + "."


def security_svg() -> str:
    """Modes de sécurité classés : à refuser (✗), acceptable (~), recommandé (✓)."""
    width = 380
    parts = [_text_lines(width // 2, 16, ["Sécurité Wi-Fi : que choisir ?"], size=12.5, weight="700", anchor="middle")]
    y = 28
    marks = {SEC_REFUSE: ("✗", _BAD), SEC_MIN: ("~", _WARN), SEC_BEST: ("✓", _GOOD)}
    for verdict in (SEC_BEST, SEC_MIN, SEC_REFUSE):
        mark, fill = marks[verdict]
        modes = [m for m in SECURITY_MODES if m.verdict == verdict]
        h = 22 + 28 * len(modes)
        parts.append(f'<rect data-verdict="{verdict}" x="4" y="{y}" width="372" height="{h}" rx="8" fill="{fill}" '
                     f'stroke="{_STROKE}" stroke-width="1.2"/>')
        parts.append(_text_lines(12, y + 16, [f"{mark} {verdict}"], size=11.5, weight="700"))
        yy = y + 32
        for m in modes:
            parts.append(f'<text data-mode="{escape(m.name)}" x="20" y="{yy}" font-size="10.5" font-weight="700">'
                         f"{escape(m.name)} ({escape(m.cipher)})</text>")
            parts.append(_text_lines(20, yy + 12, [m.why], size=9.5))
            yy += 28
        y += h + 6
    y = _notes(y + 8, "WPS (bouton ou code PIN) : à désactiver, le code PIN se devine. Masquer le SSID ou filtrer "
               "les adresses MAC ne remplace pas le chiffrement.", parts)
    return _svg(width, y + 6, parts)


def menu_tree_svg() -> str:
    """Arborescence (générique, fictive) de l'interface d'administration d'un point d'accès."""
    width, step = 380, 22
    parts = [_text_lines(width // 2, 16, ["Où régler quoi ? Interface d'administration"], size=12.5, weight="700",
                         anchor="middle")]
    y = 36
    last_x: dict[int, tuple[float, float]] = {}
    for depth, label in MENU_TREE:
        x = 10 + depth * 22
        if depth:
            px, py = last_x[depth - 1]
            parts.append(f'<path d="M{px + 6} {py + 4} V{y - 4} H{x - 4}" fill="none" stroke="{_STROKE}" stroke-width="1.2"/>')
        weight = "700" if depth < 2 else "400"
        parts.append(f'<text data-depth="{depth}" x="{x}" y="{y}" font-size="{11.5 if depth < 2 else 10.5}" '
                     f'font-weight="{weight}">{escape(label)}</text>')
        last_x[depth] = (x, y)
        y += step
    y = _notes(y + 2, "Interface générique et fictive : les noms de menus changent selon la marque, la notice du "
               "fabricant fait foi.", parts)
    return _svg(width, y + 6, parts)


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte fictive, ligne par ligne : " + " / ".join(line.strip() for line in lines if line.strip())


def _tree_alt(checks: tuple[tuple[str, str, str], ...], final: str) -> str:
    return "Arbre de diagnostic : " + " ; ".join(
        f"{i}. {what} ? Si non : {diag}." for i, (_k, what, diag) in enumerate(checks, start=1)
    ) + f" Si tout est oui : {final}"


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


ARCH_FIGURE = Figure(
    key="pr25-architecture",
    title="Architecture Wi-Fi : box, serveur DHCP, points d'accès, répéteur, clients",
    alt=_arch_alt(),
    caption="Un SSID, plusieurs radios (BSSID) ; câble jusqu'aux points d'accès dès que possible.",
    svg=architecture_svg(),
)
CHANNELS_FIGURE = Figure(
    key="pr25-canaux-24",
    title="Canaux 2,4 GHz : 1, 6 et 11 ne se chevauchent pas",
    alt=_channels_alt(),
    caption=f"Avec les voisins relevés, le canal le moins gêné est le {NEIGHBORS_BEST}.",
    svg=channels_24_svg(),
)
WIDTHS_FIGURE = Figure(
    key="pr25-canaux-5",
    title="Canaux 5 GHz en Europe selon la largeur",
    alt=_widths_alt(),
    caption="Largeur plus grande = débit plus élevé mais moins de canaux libres ; DFS au-delà du 48.",
    svg=widths_5_svg(),
)
COVERAGE_FIGURE = Figure(
    key="pr25-couverture",
    title="Couverture estimée de AP-01 en 2,4 et 5 GHz",
    alt=_coverage_alt(),
    caption="Le 5 GHz porte moins loin et traverse moins bien : le stock et l'étage demandent une solution.",
    svg=coverage_svg(),
)
REPEATER_FIGURE = Figure(
    key="pr25-repeteur",
    title="Répéteur mal placé, répéteur bien placé",
    alt=_repeater_alt(),
    caption="Un répéteur se place là où il reçoit encore bien le point d'accès, pas à côté du client.",
    svg=repeater_svg(),
)
ASSOC_FIGURE = Figure(
    key="pr25-connexion",
    title="Connexion d'un client Wi-Fi : de la découverte à Internet",
    alt=f"{len(ASSOCIATION_STEPS)} étapes : " + " ; ".join(
        f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(ASSOCIATION_STEPS, start=1)),
    caption="Radio, clé, adresse puis Internet : un échec à une étape désigne la piste.",
    svg=step_flow_svg(ASSOCIATION_STEPS),
)
SECURITY_FIGURE = Figure(
    key="pr25-securite",
    title="Modes de sécurité Wi-Fi classés",
    alt="Modes de sécurité Wi-Fi. " + " ; ".join(f"{m.name} ({m.cipher}) : {m.verdict}, {m.why}" for m in SECURITY_MODES)
        + ". WPS à désactiver ; masquer le SSID ou filtrer les adresses MAC ne remplace pas le chiffrement.",
    caption="WEP et TKIP sont à refuser ; WPA3 (SAE) ou Entreprise (802.1X/RADIUS) sont recommandés.",
    svg=security_svg(),
)
MENU_FIGURE = Figure(
    key="pr25-arborescence",
    title="Arborescence d'une interface d'administration de point d'accès",
    alt="Arborescence : " + " ; ".join(("— " * depth) + label for depth, label in MENU_TREE) + ".",
    caption="Interface générique : chaque réglage du cours a sa rubrique ; la notice du fabricant fait foi.",
    svg=menu_tree_svg(),
)
DIAG_FINAL = "Tous les contrôles réussissent : Wi-Fi conforme ; reprendre le dépannage réseau de PR24 si besoin."
DIAG_FIGURE = Figure(
    key="pr25-arbre-diagnostic",
    title="Arbre de diagnostic d'un poste Wi-Fi",
    alt=_tree_alt(WIFI_CHECKS, DIAG_FINAL),
    caption="On s'arrête au premier contrôle en échec : il désigne la piste.",
    svg=decision_tree_svg(tuple((what, diag) for _k, what, diag in WIFI_CHECKS), DIAG_FINAL),
)
SCAN_FIGURE = Figure(
    key="pr25-releve-reseaux",
    title="Relevé des réseaux voisins depuis l'atelier",
    alt=_screen_alt(NETWORKS_SCAN_LINES),
    caption="netsh wlan show networks mode=bssid : SSID, sécurité, BSSID, signal (%), bande et canal de chaque réseau.",
    svg=screen_svg(NETWORKS_SCAN_LINES, label=FICTIVE_LABEL),
)
CONFIG_PROC_FIGURE = _proc_figure("pr25-procedure-configuration", 1, PROCEDURES[0][0], CONFIG_STEPS,
                                  "Placer, sécuriser l'accès, régler radio et sécurité, puis tester et consigner.")
COVERAGE_PROC_FIGURE = _proc_figure("pr25-procedure-couverture", 2, PROCEDURES[1][0], COVERAGE_STEPS,
                                    "Mesurer avant d'acheter : déplacer, câbler, et seulement ensuite répéter.")
TROUBLE_PROC_FIGURE = _proc_figure("pr25-procedure-depannage", 3, PROCEDURES[2][0], TROUBLE_STEPS,
                                   "De la radio au canal : on s'arrête au premier contrôle en échec.")

PR25_FIGURES: tuple[Figure, ...] = (
    ARCH_FIGURE,
    CHANNELS_FIGURE,
    WIDTHS_FIGURE,
    COVERAGE_FIGURE,
    REPEATER_FIGURE,
    ASSOC_FIGURE,
    SECURITY_FIGURE,
    MENU_FIGURE,
    DIAG_FIGURE,
    SCAN_FIGURE,
    CONFIG_PROC_FIGURE,
    COVERAGE_PROC_FIGURE,
    TROUBLE_PROC_FIGURE,
)

# =============================================================================================
# 9. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

ARCH_BLANKS: dict[str, str] = {"box": "①", "dhcp": "②", "ap": "③", "repeteur": "④"}
ARCH_BLANK_ANSWERS: dict[str, str] = {ARCH_BLANKS[k]: ARCH_VALUES[k] for k in ("box", "dhcp", "ap", "repeteur")}
ARCH_BLANK_FIGURE = Figure(
    key="pr25-architecture-a-completer",
    title="Architecture Wi-Fi à compléter",
    alt=_arch_alt(ARCH_BLANKS),
    caption="Schéma à compléter : rôle de la box ①, de SRV-01 ②, de AP-02 ③ et de REP-01 ④.",
    svg=architecture_svg(blanks=ARCH_BLANKS),
)

CHANNELS_BLANKS: dict[str, str] = {"c1": "①", "c2": "②", "c3": "③", "choix": "④"}
CHANNELS_BLANK_ANSWERS: dict[str, str] = {
    "①": str(NON_OVERLAP_24[0]), "②": str(NON_OVERLAP_24[1]), "③": str(NON_OVERLAP_24[2]),
    "④": f"canal {NEIGHBORS_BEST}",
}
CHANNELS_BLANK_FIGURE = Figure(
    key="pr25-canaux-a-completer",
    title="Canaux 2,4 GHz à compléter",
    alt=_channels_alt(NEIGHBORS, CHANNELS_BLANKS),
    caption="Schéma à compléter : les trois canaux sans chevauchement ①, ②, ③ et le canal conseillé ④.",
    svg=channels_24_svg(blanks=CHANNELS_BLANKS),
)

COVERAGE_BLANKS: dict[str, str] = {"P3:2,4": "①", "P3:5": "②", "P4:2,4": "③", "P5:5": "④"}
COVERAGE_BLANK_ANSWERS: dict[str, str] = {
    "①": f"{SURVEY_BY_KEY['P3'].dbm(BAND_24)} dBm ({signal_verdict(SURVEY_BY_KEY['P3'].dbm(BAND_24))})",
    "②": f"{SURVEY_BY_KEY['P3'].dbm(BAND_5)} dBm ({signal_verdict(SURVEY_BY_KEY['P3'].dbm(BAND_5))})",
    "③": f"{SURVEY_BY_KEY['P4'].dbm(BAND_24)} dBm ({signal_verdict(SURVEY_BY_KEY['P4'].dbm(BAND_24))})",
    "④": f"{SURVEY_BY_KEY['P5'].dbm(BAND_5)} dBm ({signal_verdict(SURVEY_BY_KEY['P5'].dbm(BAND_5))})",
}
COVERAGE_BLANK_FIGURE = Figure(
    key="pr25-couverture-a-completer",
    title="Couverture à compléter",
    alt=_coverage_alt(SURVEY, COVERAGE_BLANKS),
    caption="Schéma à compléter : signal estimé en P3 (2,4 GHz ① et 5 GHz ②), en P4 (2,4 GHz ③), en P5 (5 GHz ④).",
    svg=coverage_svg(blanks=COVERAGE_BLANKS),
)

REPEATER_BLANKS: dict[str, str] = {"mal:lien": "①", "mal:debit": "②", "bien:lien": "③", "bien:debit": "④"}
REPEATER_BLANK_ANSWERS: dict[str, str] = {
    "①": f"{REPEATER_BAD.uplink_dbm} dBm ({signal_verdict(REPEATER_BAD.uplink_dbm)})",
    "②": f"environ {fr(REPEATER_BAD.mbps)} Mb/s",
    "③": f"{REPEATER_GOOD.uplink_dbm} dBm ({signal_verdict(REPEATER_GOOD.uplink_dbm)})",
    "④": f"environ {fr(REPEATER_GOOD.mbps)} Mb/s",
}
REPEATER_BLANK_FIGURE = Figure(
    key="pr25-repeteur-a-completer",
    title="Emplacement du répéteur à compléter",
    alt=_repeater_alt(REPEATER_BLANKS),
    caption="Schéma à compléter : signal du lien vers le répéteur ① et ③, débit pour le portable ② et ④.",
    svg=repeater_svg(blanks=REPEATER_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (ARCH_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr25-architecture-a-completer.svg"),
    (CHANNELS_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr25-canaux-a-completer.svg"),
    (COVERAGE_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr25-couverture-a-completer.svg"),
    (REPEATER_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr25-repeteur-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR23)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


# Relevés réutilisés par le cours et les exercices --------------------------------------------

LAPTOP = Host("LT-07", "portable Wi-Fi", "192.168.20.142", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "A4-C3-F0-55-20-77",
              dhcp=True)
LAPTOP_APIPA = Host("LT-07", "portable Wi-Fi", "169.254.71.12", 16, None, (), "A4-C3-F0-55-20-77", dhcp=True)
WEAK_STATUS = WifiStatus("connecté", SSID, BSSID_AP1_24, "802.11n", "WPA2 - Personnel", "CCMP", BAND_24, 1,
                         link_rate(SURVEY_BY_KEY["P4"].dbm(BAND_24)), quality_pct(SURVEY_BY_KEY["P4"].dbm(BAND_24)))
WEAK_LINES = netsh_wlan_lines(WEAK_STATUS)
INTERNET_PING_OK = win_ping_lines(WEB_IP, (12, 11, 12, 13))
DNS_TIMEOUT_LINES = nslookup_lines(WEB_NAME, "192.168.20.250", NS_TIMEOUT)
DNS_OK_LINES = nslookup_lines(WEB_NAME, SERVER_IP, NS_OK, WEB_IP, server_name=f"srv-01.{DOMAIN}")


def all_capture_lines() -> tuple[str, ...]:
    """Toutes les lignes de captures des figures (contrôle de largeur par les tests)."""
    return (NETWORKS_SCAN_LINES + WEAK_LINES + wifi_ipconfig_lines(LAPTOP) + wifi_ipconfig_lines(LAPTOP_APIPA, apipa=True)
            + drivers_lines("802.11b 802.11g 802.11n", BAND_24) + INTERNET_PING_OK + DNS_TIMEOUT_LINES + DNS_OK_LINES)


"""PR14 « Débits, distances, atténuation et impédance » — données de référence, calculs et
schémas SVG (ticket #217).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket217_ampcr_pratique_pr14.py` :

- unités : bit, octet, préfixes décimaux et binaires (`DECIMAL_PREFIXES`, `BINARY_PREFIXES`,
  `to_bits`), durée d'une copie (`transfer_time_s`, `duration_fr`), débit utile
  (`TCP_EFFICIENCY`, calculé depuis la taille des en-têtes) ;
- Ethernet cuivre et coaxial : normes, câbles, longueurs (`COPPER_STANDARDS`,
  `copper_verdict`, `COAX_STANDARDS`) ;
- décibels et atténuation (`loss_db`, `fraction_after`, `dbm`, `mw`, `cable_loss_db`,
  `CABLE_LOSS_100MHZ`) ; diaphonie (`acr_db`) ;
- impédance et réflexions (`reflection_coefficient` de PR16, `reflected_power_pct`,
  `return_loss_db`) ;
- fibre : affaiblissements, portées selon le module optique, bilan de liaison
  (`FIBRE_ATTENUATION`, `FIBRE_REACH`, `fibre_loss_db`, `FibreLink`, `fibre_errors`) ;
- duplex et auto-négociation (`Port`, `negotiate`) ;
- trois procédures illustrées (`TRANSFER_STEPS`, `LINK_STEPS`, `FIBRE_STEPS`).

Valeurs de référence (normes publiques, recoupées ; la fiche du fabricant fait foi) :
- IEEE 802.3 : 10BASE-T (2 paires, catégorie 3), 100BASE-TX (2 paires, catégorie 5),
  1000BASE-T (4 paires), 10GBASE-T (4 paires, catégorie 6A sur 100 m ; catégorie 6 : 55 m au
  plus, 37 m dans le pire cas de diaphonie entre câbles, TIA TSB-155) ; 10BASE2 (RG-58 50 Ω,
  185 m) et 10BASE5 (coaxial épais 50 Ω, 500 m), segments dont l'affaiblissement ne doit pas
  dépasser 8,5 dB à 10 MHz ; 1000BASE-SX, 1000BASE-LX, 10GBASE-SR, 10GBASE-LR (portées par
  type de fibre) ; trame : préambule + délimiteur 8 octets, en-tête 14, FCS 4, intervalle
  12 ; IPv4 20 octets, TCP 20 octets sans option ;
- TIA-568 : canal ≤ 100 m (lien permanent ≤ 90 m + cordons) ; affaiblissement maximal du
  câble seul à 100 MHz pour 100 m à 20 °C : Cat5e 22,0 dB, Cat6 19,8 dB, Cat6A 19,1 dB ;
  impédance de la paire torsadée 100 Ω ± 15 Ω ; fibre câblée : multimode 3,5 dB/km à 850 nm et
  1,5 dB/km à 1300 nm, connecteur (paire raccordée) 0,75 dB, épissure 0,3 dB au plus ;
- ISO/IEC 11801 : monomode OS2 0,4 dB/km, OS1 1,0 dB/km.

Les règles de choix (cuivre ou fibre à 10 Gb/s) sont des **conventions du cours**, signalées
comme telles. Chaque schéma porte son information en texte (valeurs en toutes lettres) : la
couleur n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr15_figures import CHANNEL_MAX_M
from app.v1.ampcr_pratique_pr16_figures import (
    THICK_SEGMENT_MAX_M,
    THIN_SEGMENT_MAX_M,
    reflection_coefficient,
)
from app.v1.ampcr_pratique_pr16_figures import fr as _fr_pr16
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, _wrap, step_flow_svg

WRITTEN_AT = "octobre 2026"
_STROKE = "#33415c"
_BAD = "#b3261e"
_OK = "#1d6b34"
_FILL = "#dbe4f3"

# =============================================================================================
# 1. Unités : bit, octet, préfixes
# =============================================================================================

BITS_PER_BYTE = 8
DECIMAL_PREFIXES: dict[str, int] = {"k": 10**3, "M": 10**6, "G": 10**9, "T": 10**12}
BINARY_PREFIXES: dict[str, int] = {"Ki": 2**10, "Mi": 2**20, "Gi": 2**30, "Ti": 2**40}


def to_bits(value: float, unit: str) -> float:
    """« 18 Go » → bits. `unit` = préfixe éventuel + « o » (octet) ou « b » (bit) ; les
    préfixes décimaux (k, M, G, T) valent des puissances de 10, les binaires (Ki, Mi, Gi, Ti)
    des puissances de 2."""
    if unit.endswith("o"):
        factor, prefix = BITS_PER_BYTE, unit[:-1]
    elif unit.endswith("b"):
        factor, prefix = 1, unit[:-1]
    else:
        raise ValueError(f"Unité inconnue : {unit!r} (octet « o » ou bit « b »).")
    if prefix and prefix not in DECIMAL_PREFIXES and prefix not in BINARY_PREFIXES:
        raise ValueError(f"Préfixe inconnu : {prefix!r}.")
    multiplier = DECIMAL_PREFIXES.get(prefix) or BINARY_PREFIXES.get(prefix) or 1
    return value * multiplier * factor


def rate_bps(value: float, unit: str) -> float:
    """« 100 Mb/s » → bits par seconde (préfixes décimaux seulement, comme pour tout débit)."""
    prefix = unit.removesuffix("b/s")
    if prefix == unit or (prefix and prefix not in DECIMAL_PREFIXES):
        raise ValueError(f"Débit attendu en b/s, kb/s, Mb/s, Gb/s : {unit!r}.")
    return value * DECIMAL_PREFIXES.get(prefix, 1)


def transfer_time_s(size_bits: float, nominal_bps: float, efficiency: float = 1.0) -> float:
    """Durée d'une copie : taille en bits / débit utile (débit nominal × rendement)."""
    if not 0 < efficiency <= 1:
        raise ValueError("Le rendement est compris entre 0 (exclu) et 1.")
    return size_bits / (nominal_bps * efficiency)


def duration_fr(seconds: float) -> str:
    """425,5 s → « 7 min 6 s » (arrondi à la seconde)."""
    total = round(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    parts = []
    if hours:
        parts.append(f"{hours} h")
    if minutes or hours:
        parts.append(f"{minutes} min")
    parts.append(f"{secs} s")
    return " ".join(parts)


# Débit utile maximal d'une copie TCP sur Ethernet (trame de 1 500 octets de données) : sur la
# ligne, chaque trame occupe aussi le préambule et le délimiteur, l'en-tête, le contrôle (FCS)
# et l'intervalle entre trames ; dans la trame, IPv4 et TCP prennent 40 octets.
ETH_PREAMBLE_SFD = 8
ETH_HEADER = 14
ETH_FCS = 4
ETH_IFG = 12
ETH_MTU = 1500
IPV4_HEADER = 20
TCP_HEADER = 20
ETH_WIRE_BYTES = ETH_PREAMBLE_SFD + ETH_HEADER + ETH_MTU + ETH_FCS + ETH_IFG  # 1 538
TCP_PAYLOAD = ETH_MTU - IPV4_HEADER - TCP_HEADER  # 1 460
TCP_EFFICIENCY = TCP_PAYLOAD / ETH_WIRE_BYTES  # ≈ 0,949


def fr(value: float, digits: int = 1) -> str:
    """Nombre au format français (`fr` de PR16) ; `digits=0` arrondit à l'unité sans
    retirer les zéros des entiers (120 reste « 120 »)."""
    if digits == 0:
        return str(round(value))
    return _fr_pr16(value, digits)


def pct(value: float, digits: int = 1) -> str:
    return f"{fr(100 * value, digits)} %"


UNIT_ROWS: tuple[tuple[str, str, str], ...] = (
    ("b (bit)", "0 ou 1, la plus petite information", "Débits : b/s, kb/s, Mb/s, Gb/s"),
    ("o (octet) — en anglais B (byte)", "8 bits", "Tailles : fichiers, disques, mémoire"),
    ("k, M, G, T (décimaux)", "10³, 10⁶, 10⁹, 10¹²", "Débits toujours ; tailles des disques et des fabricants"),
    ("Ki, Mi, Gi, Ti (binaires)", "2¹⁰ = 1 024 ; 2²⁰ ; 2³⁰ ; 2⁴⁰", "Tailles affichées par certains systèmes (Windows écrit « Go » pour Gio)"),
)

TRANSFER_STEPS: tuple[tuple[str, str], ...] = (
    ("Taille en bits", "Convertir la taille : octets × 8, préfixe décimal ou binaire."),
    ("Débit en b/s", "Convertir le débit nominal : 1 Gb/s = 10⁹ b/s."),
    ("Débit utile", "Appliquer le rendement (protocoles, disques) : nominal × rendement."),
    ("Diviser", "Durée = taille en bits / débit utile en b/s."),
    ("Convertir", "Secondes → minutes et heures, unité écrite."),
    ("Vérifier", "Ordre de grandeur plausible ; comparer à une mesure réelle."),
)

# =============================================================================================
# 2. Ethernet cuivre et coaxial : débits et longueurs
# =============================================================================================

CATEGORY_ORDER: tuple[str, ...] = ("Cat3", "Cat5", "Cat5e", "Cat6", "Cat6A")


@dataclass(frozen=True)
class CopperStandard:
    name: str
    rate: str
    rate_mbps: int
    min_category: str
    pairs: int
    note: str


COPPER_STANDARDS: tuple[CopperStandard, ...] = (
    CopperStandard("10BASE-T", "10 Mb/s", 10, "Cat3", 2, "Paires 1-2 et 3-6 ; historique"),
    CopperStandard("100BASE-TX", "100 Mb/s", 100, "Cat5", 2, "Paires 1-2 et 3-6 seulement ; « Fast Ethernet »"),
    CopperStandard("1000BASE-T", "1 Gb/s", 1000, "Cat5e", 4, "Les 4 paires, dans les deux sens à la fois"),
    CopperStandard("10GBASE-T", "10 Gb/s", 10000, "Cat6A", 4,
                   "Cat6 : 55 m au plus (37 m si beaucoup de câbles voisins), à certifier"),
)
COPPER_BY_NAME = {s.name: s for s in COPPER_STANDARDS}
TEN_G_CAT6_MAX_M = 55
TEN_G_CAT6_WORST_M = 37

V_OK = "Conforme"
V_CATEGORY = "Catégorie insuffisante"
V_LENGTH = "Trop long pour la paire torsadée"
V_CONDITIONAL = "Possible sous conditions (10 Gb/s en Cat6 ≤ 55 m, à certifier)"
COPPER_VERDICTS = (V_OK, V_CATEGORY, V_LENGTH, V_CONDITIONAL)


def copper_verdict(standard: str, category: str, length_m: float) -> str:
    """Canal en paire torsadée : longueur ≤ 100 m d'abord, puis catégorie minimale ; 10 Gb/s
    en Cat6 seulement jusqu'à 55 m, après certification (TIA TSB-155)."""
    spec = COPPER_BY_NAME[standard]
    if length_m > CHANNEL_MAX_M:
        return V_LENGTH
    rank = CATEGORY_ORDER.index(category)
    if spec.name == "10GBASE-T" and category == "Cat6":
        return V_CONDITIONAL if length_m <= TEN_G_CAT6_MAX_M else V_CATEGORY
    return V_OK if rank >= CATEGORY_ORDER.index(spec.min_category) else V_CATEGORY


COAX_STANDARDS: tuple[tuple[str, str, int, str], ...] = (
    ("10BASE5", "Coaxial épais 50 Ω (≈ 10 mm)", THICK_SEGMENT_MAX_M, "10 Mb/s, bus, half-duplex, 100 transceivers au plus"),
    ("10BASE2", "Coaxial fin RG-58 50 Ω", THIN_SEGMENT_MAX_M, "10 Mb/s, bus, half-duplex, 30 stations au plus"),
)
# IEEE 802.3 : l'affaiblissement d'un segment ne dépasse pas 8,5 dB à 10 MHz ; c'est lui qui
# fixe la longueur (coaxial fin plus atténuant → segment plus court).
COAX_SEGMENT_MAX_DB = 8.5

# =============================================================================================
# 3. Décibels, atténuation, bruit, diaphonie
# =============================================================================================


def loss_db(p_in: float, p_out: float) -> float:
    """Affaiblissement en dB entre deux puissances : 10 × log10(Pentrée / Psortie)."""
    return 10 * math.log10(p_in / p_out)


def fraction_after(loss: float) -> float:
    """Part de la puissance qui reste après un affaiblissement de `loss` dB."""
    return 10 ** (-loss / 10)


def dbm(milliwatts: float) -> float:
    """Puissance absolue en dBm : 0 dBm = 1 mW."""
    return 10 * math.log10(milliwatts)


def mw(level_dbm: float) -> float:
    return 10 ** (level_dbm / 10)


def cable_loss_db(length_m: float, db_per_100m: float) -> float:
    """En dB, l'affaiblissement est proportionnel à la longueur (à fréquence donnée)."""
    return db_per_100m * length_m / 100


# Affaiblissement maximal du câble seul, 100 m, 20 °C, à 100 MHz (TIA-568).
CABLE_LOSS_100MHZ: dict[str, float] = {"Cat5e": 22.0, "Cat6": 19.8, "Cat6A": 19.1}

DB_EXAMPLES: tuple[float, ...] = (0, 3, 6, 10, 20, 30)


def acr_db(next_db: float, attenuation_db: float) -> float:
    """Rapport atténuation/diaphonie (ACR-N) : NEXT − affaiblissement, en dB ; plus il est
    grand, mieux le récepteur distingue le signal de la diaphonie."""
    return next_db - attenuation_db


# =============================================================================================
# 4. Impédance et réflexions
# =============================================================================================

TWISTED_PAIR_OHM = 100
TWISTED_PAIR_TOLERANCE_OHM = 15


def reflected_power_pct(gamma: float) -> float:
    """Part de la puissance réfléchie : Γ² (en %)."""
    return 100 * gamma * gamma


def return_loss_db(gamma: float) -> float | None:
    """Affaiblissement de réflexion : −20 × log10 |Γ| ; `None` si Γ = 0 (adaptation parfaite)."""
    if gamma == 0:
        return None
    return -20 * math.log10(abs(gamma))


R_MATCHED = "Adaptée : pas de réflexion"
R_PARTIAL = "Réflexion partielle"
R_OPEN = "Réflexion totale, même signe (extrémité ouverte)"
R_SHORT = "Réflexion totale inversée (court-circuit)"
REFLECTION_KINDS = (R_MATCHED, R_PARTIAL, R_OPEN, R_SHORT)


def reflection_kind(gamma: float) -> str:
    if abs(gamma) < 1e-9:
        return R_MATCHED
    if abs(gamma - 1) < 1e-9:
        return R_OPEN
    if abs(gamma + 1) < 1e-9:
        return R_SHORT
    return R_PARTIAL


# (situation, impédance de la ligne, charge en ohms ou None si ouverte)
REFLECTION_EXAMPLES: tuple[tuple[str, int, float | None], ...] = (
    ("Coaxial 50 Ω terminé par 50 Ω", 50, 50),
    ("Coaxial 75 Ω vers une entrée 50 Ω", 75, 50),
    ("Coaxial 50 Ω vers une caméra 75 Ω", 50, 75),
    ("Coaxial 50 Ω sans terminateur", 50, None),
    ("Coaxial 50 Ω court-circuité", 50, 0),
)

# =============================================================================================
# 5. Fibre optique : affaiblissement, portée selon le module, bilan
# =============================================================================================

MULTIMODE = "multimode"
SINGLEMODE = "monomode"

FIBRE_TYPES: tuple[tuple[str, str, str, str], ...] = (
    ("OM1", MULTIMODE, "62,5 µm", "Ancienne ; portée courte"),
    ("OM2", MULTIMODE, "50 µm", "Ancienne ; 1 Gb/s jusqu'à 550 m"),
    ("OM3", MULTIMODE, "50 µm", "Optimisée laser ; 10 Gb/s jusqu'à 300 m"),
    ("OM4", MULTIMODE, "50 µm", "Optimisée laser ; 10 Gb/s jusqu'à 400 m"),
    ("OS1 / OS2", SINGLEMODE, "≈ 9 µm", "Cœur fin, laser ; kilomètres"),
)

# (fibre, longueur d'onde en nm) → affaiblissement maximal en dB/km
FIBRE_ATTENUATION: dict[tuple[str, int], float] = {
    (MULTIMODE, 850): 3.5,
    (MULTIMODE, 1300): 1.5,
    ("OS1", 1310): 1.0,
    ("OS2", 1310): 0.4,
    ("OS2", 1550): 0.4,
}
CONNECTOR_PAIR_DB = 0.75
SPLICE_DB = 0.3

# (module optique, fibre, longueur d'onde, portée maximale en m) — IEEE 802.3
FIBRE_REACH: tuple[tuple[str, str, int, int], ...] = (
    ("1000BASE-SX", "OM1", 850, 275),
    ("1000BASE-SX", "OM2", 850, 550),
    ("1000BASE-LX", "OS2", 1310, 5000),
    ("10GBASE-SR", "OM1", 850, 33),
    ("10GBASE-SR", "OM2", 850, 82),
    ("10GBASE-SR", "OM3", 850, 300),
    ("10GBASE-SR", "OM4", 850, 400),
    ("10GBASE-LR", "OS2", 1310, 10000),
)
REACH_M = {(module, fibre): reach for module, fibre, _w, reach in FIBRE_REACH}


def attenuation_for(fibre: str, wavelength_nm: int) -> float:
    kind = MULTIMODE if fibre.startswith("OM") else fibre
    return FIBRE_ATTENUATION[(kind, wavelength_nm)]


def fibre_loss_db(length_m: float, db_per_km: float, connectors: int, splices: int) -> float:
    """Perte d'une liaison optique : fibre + paires de connecteurs + épissures."""
    return length_m / 1000 * db_per_km + connectors * CONNECTOR_PAIR_DB + splices * SPLICE_DB


@dataclass(frozen=True)
class FibreLink:
    name: str
    module: str
    fibre: str
    wavelength_nm: int
    length_m: float
    connectors: int
    splices: int
    budget_db: float  # budget de canal du module (fiche technique)

    @property
    def loss_db(self) -> float:
        return round(fibre_loss_db(self.length_m, attenuation_for(self.fibre, self.wavelength_nm),
                                   self.connectors, self.splices), 2)

    @property
    def margin_db(self) -> float:
        return round(self.budget_db - self.loss_db, 2)


F_REACH = "longueur supérieure à la portée du module sur cette fibre"
F_BUDGET = "perte supérieure au budget du module"


def fibre_errors(link: FibreLink) -> list[str]:
    """Une liaison optique doit respecter **les deux** limites : la portée (dispersion, propre
    au module et à la fibre) et le budget de pertes."""
    errors: list[str] = []
    if link.length_m > REACH_M[(link.module, link.fibre)]:
        errors.append(F_REACH)
    if link.loss_db > link.budget_db:
        errors.append(F_BUDGET)
    return errors


M_10G_COPPER = "10GBASE-T sur Cat6A"
M_10G_OM3 = "10GBASE-SR sur OM3"
M_10G_OM4 = "10GBASE-SR sur OM4"
M_10G_LR = "10GBASE-LR sur monomode OS2"
MEDIA_10G = (M_10G_COPPER, M_10G_OM3, M_10G_OM4, M_10G_LR)


def choose_10g(length_m: float, *, between_buildings: bool = False) -> str:
    """Convention du cours pour une liaison à 10 Gb/s : la solution la plus simple qui tient la
    distance ; jamais de cuivre entre deux bâtiments (terres différentes, foudre)."""
    if length_m <= CHANNEL_MAX_M and not between_buildings:
        return M_10G_COPPER
    for medium, fibre in ((M_10G_OM3, "OM3"), (M_10G_OM4, "OM4")):
        if length_m <= REACH_M[("10GBASE-SR", fibre)]:
            return medium
    if length_m <= REACH_M[("10GBASE-LR", "OS2")]:
        return M_10G_LR
    raise ValueError("Au-delà de 10 km : module longue portée (hors du cours).")


FIBRE_STEPS: tuple[tuple[str, str], ...] = (
    ("Relever", "Longueur, type de fibre, longueur d'onde, connecteurs, épissures."),
    ("Valeurs", "dB/km de la fibre, 0,75 dB par connecteur, 0,3 dB par épissure."),
    ("Calculer la perte", "Fibre (km × dB/km) + connecteurs + épissures."),
    ("Portée et budget", "Portée du module sur cette fibre ; budget de sa fiche technique."),
    ("Marge", "Budget − perte ; comparer à la marge exigée par le client."),
    ("Conclure et mesurer", "Verdict justifié, puis mesure au photomètre ou réflectomètre."),
)

# =============================================================================================
# 6. Duplex, auto-négociation, collisions
# =============================================================================================

FULL = "full"
HALF = "half"


@dataclass(frozen=True)
class Port:
    """Réglage d'un port : auto-négociation, ou vitesse et duplex forcés (10 ou 100 Mb/s)."""

    auto: bool = True
    speed: int | None = None
    duplex: str | None = None
    max_speed: int = 1000

    def __post_init__(self) -> None:
        if not self.auto and (self.speed not in (10, 100) or self.duplex not in (FULL, HALF)):
            raise ValueError("Port forcé : vitesse 10 ou 100 Mb/s et duplex full ou half.")


@dataclass(frozen=True)
class Link:
    up: bool
    speed: int | None = None
    duplex_a: str | None = None
    duplex_b: str | None = None

    @property
    def mismatch(self) -> bool:
        return self.up and self.duplex_a != self.duplex_b


def negotiate(a: Port, b: Port, *, four_pairs_ok: bool = True) -> Link:
    """Résultat d'une liaison en paire torsadée entre deux ports.
    - Deux ports en auto : meilleure vitesse commune, full duplex ; 1 Gb/s exige les 4 paires,
      sinon la carte rétrograde à 100 Mb/s (comportement courant, « downshift »).
    - Un port forcé, l'autre en auto : le port auto détecte la vitesse mais ne peut pas
      connaître le duplex : il se met en **half duplex** (détection parallèle, IEEE 802.3).
    - Deux ports forcés : il faut la même vitesse ; chacun garde son duplex."""
    if a.auto and b.auto:
        speed = min(a.max_speed, b.max_speed)
        if speed == 1000 and not four_pairs_ok:
            speed = 100
        return Link(True, speed, FULL, FULL)
    if a.auto != b.auto:
        forced, auto = (a, b) if not a.auto else (b, a)
        if forced.speed > auto.max_speed:
            return Link(False)
        duplex_forced, duplex_auto = forced.duplex, HALF
        if forced is a:
            return Link(True, forced.speed, duplex_forced, duplex_auto)
        return Link(True, forced.speed, duplex_auto, duplex_forced)
    if a.speed != b.speed:
        return Link(False)
    return Link(True, a.speed, a.duplex, b.duplex)


N_GIGA = "1 Gb/s full duplex"
N_FAST = "100 Mb/s full duplex"
N_MISMATCH = "100 Mb/s avec désaccord de duplex"
N_DOWN = "Pas de lien"
NEGOTIATION_RESULTS = (N_GIGA, N_FAST, N_MISMATCH, N_DOWN)


def link_result(link: Link) -> str:
    if not link.up:
        return N_DOWN
    if link.mismatch:
        return N_MISMATCH
    if link.speed == 1000:
        return N_GIGA
    if link.speed == 100 and link.duplex_a == FULL:
        return N_FAST
    raise ValueError("Résultat hors des catégories de l'exercice.")


LINK_STEPS: tuple[tuple[str, str], ...] = (
    ("Relever", "Vitesse et duplex des deux côtés (carte et port du switch), compteurs d'erreurs."),
    ("Configuration", "Auto-négociation des deux côtés ; rien de forcé d'un seul côté."),
    ("Capacités", "Carte, switch, prise murale ou téléphone intermédiaire : tous à 1 Gb/s ?"),
    ("Câble", "Testeur : 8 conducteurs (paires 4-5 et 7-8), longueur, catégorie."),
    ("Isoler", "Changer le cordon, puis le port, pour localiser le maillon fautif."),
    ("Contrôler et consigner", "1 Gb/s full duplex des deux côtés, compteurs stables, rapport."),
)

# =============================================================================================
# 7. Données et figures
# =============================================================================================


def byte_svg() -> str:
    """Un octet = huit cases de bit, puis l'échelle des préfixes décimaux et binaires."""
    width = 380
    parts = [_text_lines(width // 2, 18, ["1 octet (o) = 8 bits (b)"], size=13, weight="700", anchor="middle")]
    cell, left = 40, 30
    for i in range(BITS_PER_BYTE):
        x = left + i * cell
        parts.append(f'<rect data-bit="{i}" x="{x}" y="28" width="{cell - 4}" height="30" rx="4" '
                     f'fill="{_FILL}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(x + (cell - 4) // 2, 48, [str((0b10110010 >> (7 - i)) & 1)], size=13,
                                 weight="700", anchor="middle"))
    parts.append(_text_lines(width // 2, 76, ["Exemple : 1011 0010 (8 bits = 1 octet)"], size=11, anchor="middle"))
    y = 100
    parts.append(_text_lines(8, y, ["Décimal (débits, disques)"], size=12, weight="700"))
    parts.append(_text_lines(200, y, ["Binaire (systèmes)"], size=12, weight="700"))
    rows = (("k = 1 000", "Ki = 1 024"), ("M = 1 000 000", "Mi = 1 048 576"),
            ("G = 10⁹", "Gi = 2³⁰ ≈ 1,074 × 10⁹"), ("T = 10¹²", "Ti = 2⁴⁰ ≈ 1,100 × 10¹²"))
    for i, (dec, binary) in enumerate(rows, start=1):
        parts.append(_text_lines(8, y + 18 * i, [dec], size=11.5))
        parts.append(_text_lines(200, y + 18 * i, [binary], size=11.5))
    note_y = y + 18 * len(rows) + 22
    notes = _wrap("Un débit s'écrit en bits par seconde (b/s), une taille en octets : × 8 ou ÷ 8 "
                  "pour passer de l'un à l'autre.", 58)
    parts.append(_text_lines(8, note_y, notes, size=11, step=14))
    return _svg(width, note_y + 14 * len(notes), parts)


REACH_BARS: tuple[tuple[str, str, int], ...] = (
    ("10BASE-T à 10GBASE-T", "paire torsadée, canal", CHANNEL_MAX_M),
    ("10BASE2", "coaxial fin RG-58", THIN_SEGMENT_MAX_M),
    ("10BASE5", "coaxial épais", THICK_SEGMENT_MAX_M),
    ("10GBASE-SR", "multimode OM3", REACH_M[("10GBASE-SR", "OM3")]),
    ("1000BASE-SX", "multimode OM2", REACH_M[("1000BASE-SX", "OM2")]),
    ("1000BASE-LX", "monomode", REACH_M[("1000BASE-LX", "OS2")]),
    ("10GBASE-LR", "monomode", REACH_M[("10GBASE-LR", "OS2")]),
)


def reach_svg() -> str:
    """Portées maximales, barres sur une échelle logarithmique (10 m → 10 km)."""
    width, left, right = 380, 8, 12
    scale_w = width - left - right
    log_min, log_max = 1, 4  # 10 m à 10 000 m

    def sx(m: float) -> float:
        return left + scale_w * (math.log10(m) - log_min) / (log_max - log_min)

    parts = [_text_lines(width // 2, 18, ["Portée maximale (échelle logarithmique)"], size=12.5,
                         weight="700", anchor="middle")]
    y = 32
    for name, medium, metres in REACH_BARS:
        parts.append(_text_lines(left, y + 12, [f"{name} — {medium}"], size=11, weight="700"))
        bar = sx(metres) - left
        parts.append(f'<rect data-standard="{escape(name)}" data-m="{metres}" x="{left}" y="{y + 17}" '
                     f'width="{bar:.1f}" height="14" rx="3" fill="{_FILL}" stroke="{_STROKE}"/>')
        label = f"{metres} m" if metres < 1000 else f"{fr(metres / 1000)} km"
        lx, anchor = (left + bar + 5, "start") if bar < scale_w - 60 else (left + bar - 5, "end")
        parts.append(_text_lines(int(lx), y + 29, [label], size=11, weight="700", anchor=anchor))
        y += 40
    for metres, label in ((10, "10 m"), (100, "100 m"), (1000, "1 km"), (10000, "10 km")):
        x = sx(metres)
        parts.append(f'<path d="M{x:.1f} {y} V{y + 6}" stroke="{_STROKE}"/>')
        anchor = "start" if metres == 10 else "end" if metres == 10000 else "middle"
        parts.append(_text_lines(int(x), y + 18, [label], size=10.5, anchor=anchor))
    return _svg(width, y + 26, parts)


def db_svg() -> str:
    """Puissance restante après 0, 3, 6, 10, 20, 30 dB : barres en %, valeurs écrites."""
    width, left = 380, 70
    scale = (width - left - 60) / 100
    parts = [_text_lines(width // 2, 18, ["Puissance restante après un affaiblissement"], size=12.5,
                         weight="700", anchor="middle")]
    y = 32
    for loss in DB_EXAMPLES:
        remaining = 100 * fraction_after(loss)
        parts.append(_text_lines(8, y + 14, [f"{fr(loss)} dB"], size=12, weight="700"))
        bar = max(remaining * scale, 2)
        parts.append(f'<rect data-db="{fr(loss)}" data-percent="{fr(remaining, 1)}" x="{left}" y="{y}" '
                     f'width="{bar:.1f}" height="20" rx="3" fill="{_FILL}" stroke="{_STROKE}"/>')
        text = f"{fr(remaining, 1)} %" if remaining >= 1 else f"{fr(remaining, 2)} %"
        parts.append(_text_lines(int(left + bar + 6), y + 14, [text], size=12, weight="700"))
        y += 30
    notes = _wrap("Chaque tranche de 3 dB divise environ la puissance par 2, chaque tranche de "
                  "10 dB par 10. Les dB s'additionnent le long d'une liaison.", 58)
    parts.append(_text_lines(8, y + 12, notes, size=11, step=14))
    return _svg(width, y + 14 * len(notes) + 8, parts)


def crosstalk_svg() -> str:
    """Deux paires d'un même câble : émetteur à gauche sur la paire 1 ; la diaphonie se mesure
    sur la paire 2, du même côté (NEXT) ou à l'autre bout (FEXT)."""
    width = 380
    parts = [_text_lines(width // 2, 18, ["Diaphonie entre deux paires d'un même câble"], size=12.5,
                         weight="700", anchor="middle")]
    x1, x2 = 70, 310
    for y, label in ((52, "Paire 1 : émetteur"), (112, "Paire 2 : voisine")):
        parts.append(f'<path d="M{x1} {y} H{x2}" stroke="{_STROKE}" stroke-width="5"/>')
        parts.append(_text_lines(width // 2, y - 10, [label], size=11.5, weight="700", anchor="middle"))
    parts.append(f'<rect x="8" y="38" width="58" height="28" rx="4" fill="{_FILL}" stroke="{_STROKE}"/>')
    parts.append(_text_lines(37, 56, ["Émet."], size=11, weight="700", anchor="middle"))
    parts.append(f'<rect x="{x2 + 4}" y="38" width="58" height="28" rx="4" fill="#ffffff" stroke="{_STROKE}"/>')
    parts.append(_text_lines(x2 + 33, 56, ["Reçoit"], size=11, weight="700", anchor="middle"))
    for x, key, label in ((x1 + 20, "next", "NEXT"), (x2 - 20, "fext", "FEXT")):
        parts.append(f'<path data-crosstalk="{key}" d="M{x1 + 40} 58 Q{(x1 + 40 + x) // 2} 85 {x} 106" '
                     f'fill="none" stroke="{_BAD}" stroke-width="2" stroke-dasharray="5 3"/>')
    parts.append(f'<rect x="8" y="98" width="58" height="28" rx="4" fill="#fbecec" stroke="{_STROKE}"/>')
    parts.append(_text_lines(37, 116, ["NEXT"], size=11, weight="700", anchor="middle"))
    parts.append(f'<rect x="{x2 + 4}" y="98" width="58" height="28" rx="4" fill="#fbecec" stroke="{_STROKE}"/>')
    parts.append(_text_lines(x2 + 33, 116, ["FEXT"], size=11, weight="700", anchor="middle"))
    notes = (
        "NEXT (paradiaphonie) : mesurée du côté de l'émetteur.",
        "FEXT (télédiaphonie) : mesurée à l'autre extrémité.",
        "Valeur en dB d'affaiblissement du signal parasite :",
        "plus elle est grande, meilleur est le câble.",
    )
    parts.append(_text_lines(8, 150, list(notes), size=11, step=15))
    return _svg(width, 150 + 15 * len(notes), parts)


def reflection_svg(examples: tuple[tuple[str, int, float | None], ...]) -> str:
    """Pour chaque liaison : Γ calculé, part réfléchie en barre et en texte."""
    width, left = 380, 8
    scale = (width - 2 * left) / 100
    parts = [_text_lines(width // 2, 18, ["Réflexion à l'extrémité d'une ligne"], size=12.5, weight="700",
                         anchor="middle")]
    y = 34
    for label, line, load in examples:
        gamma = reflection_coefficient(load, line)
        power = reflected_power_pct(gamma)
        parts.append(_text_lines(left, y + 12, [label], size=11.5, weight="700"))
        bar = max(power * scale, 2)
        parts.append(f'<rect data-gamma="{fr(gamma, 2)}" x="{left}" y="{y + 18}" width="{bar:.1f}" height="14" '
                     f'rx="3" fill="{"#e9f5ec" if gamma == 0 else "#fbecec"}" stroke="{_STROKE}"/>')
        sign = "+" if gamma > 0 else ""
        text = f"Γ = {sign}{fr(gamma, 2)} ; puissance réfléchie : {fr(power, 1)} %"
        parts.append(_text_lines(left, y + 46, [text], size=11))
        y += 58
    notes = _wrap("Γ = (Zcharge − Zligne) / (Zcharge + Zligne). Ouverte : Γ = +1 ; court-circuit : "
                  "Γ = −1 ; adaptée : Γ = 0.", 58)
    parts.append(_text_lines(left, y + 8, notes, size=11, step=14))
    return _svg(width, y + 14 * len(notes) + 6, parts)


def budget_svg(link: FibreLink) -> str:
    """Bilan d'une liaison optique : segments empilés (fibre, connecteurs, épissures, marge)
    à l'échelle, comparés au budget du module."""
    width, left = 380, 10
    scale = (width - 2 * left) / max(link.budget_db, link.loss_db)
    fibre = round(link.length_m / 1000 * attenuation_for(link.fibre, link.wavelength_nm), 2)
    segments = (
        ("fibre", f"Fibre {fr(link.length_m / 1000, 2)} km", fibre),
        ("connecteurs", f"{link.connectors} connecteurs", link.connectors * CONNECTOR_PAIR_DB),
        ("epissures", f"{link.splices} épissures", link.splices * SPLICE_DB),
    )
    parts = [_text_lines(width // 2, 18, [f"Bilan : {link.name}"], size=12.5, weight="700", anchor="middle")]
    x, y = float(left), 34
    fills = ("#c9d6ee", "#e3c9a8", "#d9d9d9")
    for (key, _label, value), fill in zip(segments, fills, strict=True):
        w = value * scale
        parts.append(f'<rect data-part="{key}" data-db="{fr(value, 2)}" x="{x:.1f}" y="{y}" width="{w:.1f}" '
                     f'height="30" fill="{fill}" stroke="{_STROKE}"/>')
        x += w
    if link.margin_db > 0:
        parts.append(f'<rect data-part="marge" data-db="{fr(link.margin_db, 2)}" x="{x:.1f}" y="{y}" '
                     f'width="{link.margin_db * scale:.1f}" height="30" fill="#e9f5ec" stroke="{_OK}" '
                     f'stroke-dasharray="4 3"/>')
    budget_x = left + link.budget_db * scale
    parts.append(f'<path d="M{budget_x:.1f} {y - 6} V{y + 38}" stroke="{_BAD}" stroke-width="2"/>')
    lines = [f"{label} : {fr(value, 2)} dB" for _k, label, value in segments]
    lines += [
        f"Perte totale : {fr(link.loss_db, 2)} dB",
        f"Budget du module ({link.module}) : {fr(link.budget_db, 2)} dB (trait vertical)",
        f"Marge : {fr(link.margin_db, 2)} dB",
    ]
    parts.append(_text_lines(left, y + 58, lines, size=11.5, step=16))
    return _svg(width, y + 58 + 16 * len(lines), parts)


# Liaison du schéma de bilan (et du cas résolu 4) : 10GBASE-SR sur OM3 entre deux baies.
BUDGET_EXAMPLE = FibreLink("baie A → baie B, OM3, 850 nm", "10GBASE-SR", "OM3", 850, 220, 2, 0, 2.6)

BYTE_FIGURE = Figure(
    key="pr14-octet-prefixes",
    title="Bit, octet et préfixes décimaux ou binaires",
    alt=(
        "Huit cases de bit 1 0 1 1 0 0 1 0 forment un octet. Préfixes décimaux : k = 1 000, "
        "M = 1 000 000, G = 10 puissance 9, T = 10 puissance 12. Préfixes binaires : Ki = 1 024, "
        "Mi = 1 048 576, Gi = 2 puissance 30 soit environ 1,074 milliard, Ti = 2 puissance 40. Un "
        "débit s'écrit en bits par seconde, une taille en octets : multiplier ou diviser par 8."
    ),
    caption="b = bit, o = octet (B en anglais) ; les débits utilisent toujours les préfixes décimaux.",
    svg=byte_svg(),
)

REACH_FIGURE = Figure(
    key="pr14-portees",
    title="Portée maximale des liaisons Ethernet selon le support",
    alt=(
        "Barres sur une échelle logarithmique de 10 m à 10 km. "
        + " ".join(f"{name} ({medium}) : {metres} m." for name, medium, metres in REACH_BARS)
        + " La portée de la fibre dépend du module optique et du type de fibre."
    ),
    caption=(
        "Cuivre : 100 m par canal quel que soit le débit ; coaxial historique : 185 ou 500 m ; "
        "fibre : selon le module et la fibre (IEEE 802.3)."
    ),
    svg=reach_svg(),
)

DB_FIGURE = Figure(
    key="pr14-decibels",
    title="Décibels : puissance restante après un affaiblissement",
    alt=(
        "Barres horizontales : "
        + ", ".join(f"{fr(d)} dB → {fr(100 * fraction_after(d), 2)} % de la puissance" for d in DB_EXAMPLES)
        + ". 3 dB divisent environ par 2, 10 dB par 10."
    ),
    caption="Affaiblissement (dB) = 10 × log10(Pentrée / Psortie) ; les dB d'une liaison s'additionnent.",
    svg=db_svg(),
)

CROSSTALK_FIGURE = Figure(
    key="pr14-diaphonie",
    title="Diaphonie : NEXT et FEXT",
    alt=(
        "Deux paires parallèles d'un même câble. La paire 1 porte le signal de l'émetteur, à "
        "gauche. Une partie du signal passe sur la paire 2 : mesurée du côté de l'émetteur, "
        "c'est la paradiaphonie (NEXT) ; mesurée à l'autre extrémité, la télédiaphonie (FEXT). "
        "La valeur en dB est l'affaiblissement du signal parasite : plus elle est grande, mieux "
        "c'est."
    ),
    caption="Le testeur mesure le NEXT aux deux extrémités ; détorsadage et écrasement le dégradent.",
    svg=crosstalk_svg(),
)

REFLECTION_FIGURE = Figure(
    key="pr14-reflexions",
    title="Impédance et réflexions",
    alt=(
        "Cinq liaisons : "
        + " ".join(
            f"{label} : coefficient de réflexion {fr(reflection_coefficient(load, line), 2)}, "
            f"{fr(reflected_power_pct(reflection_coefficient(load, line)), 1)} % de la puissance réfléchie."
            for label, line, load in REFLECTION_EXAMPLES
        )
    ),
    caption="Toute rupture d'impédance réfléchit une partie du signal ; une ligne adaptée n'en réfléchit pas.",
    svg=reflection_svg(REFLECTION_EXAMPLES),
)

BUDGET_FIGURE = Figure(
    key="pr14-bilan-optique",
    title="Bilan d'une liaison en fibre optique",
    alt=(
        f"Barre empilée : fibre OM3 de {BUDGET_EXAMPLE.length_m:g} m à 3,5 dB/km = "
        f"{fr(BUDGET_EXAMPLE.length_m / 1000 * 3.5, 2)} dB, deux connecteurs à 0,75 dB = 1,5 dB, "
        f"aucune épissure ; perte totale {fr(BUDGET_EXAMPLE.loss_db, 2)} dB. Budget du module "
        f"{BUDGET_EXAMPLE.module} : {fr(BUDGET_EXAMPLE.budget_db, 2)} dB ; marge "
        f"{fr(BUDGET_EXAMPLE.margin_db, 2)} dB."
    ),
    caption="Perte = fibre (km × dB/km) + connecteurs + épissures ; elle doit rester sous le budget du module.",
    svg=budget_svg(BUDGET_EXAMPLE),
)

TRANSFER_FIGURE = Figure(
    key="pr14-procedure-duree",
    title="Procédure 1 — Calculer la durée d'une copie",
    alt="Six étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(TRANSFER_STEPS, start=1)),
    caption="Toujours écrire les unités : bits et b/s, puis secondes converties.",
    svg=step_flow_svg(TRANSFER_STEPS),
)

LINK_FIGURE = Figure(
    key="pr14-procedure-liaison",
    title="Procédure 2 — Liaison à 100 Mb/s au lieu de 1 Gb/s",
    alt="Six étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(LINK_STEPS, start=1)),
    caption="Du plus simple (lire l'état) au plus long (tester le câble), en isolant chaque maillon.",
    svg=step_flow_svg(LINK_STEPS),
)

FIBRE_FIGURE = Figure(
    key="pr14-procedure-bilan",
    title="Procédure 3 — Bilan d'une liaison optique",
    alt="Six étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(FIBRE_STEPS, start=1)),
    caption="La portée du module et le budget de pertes se vérifient tous les deux.",
    svg=step_flow_svg(FIBRE_STEPS),
)

PR14_FIGURES: tuple[Figure, ...] = (
    BYTE_FIGURE,
    TRANSFER_FIGURE,
    REACH_FIGURE,
    DB_FIGURE,
    CROSSTALK_FIGURE,
    REFLECTION_FIGURE,
    BUDGET_FIGURE,
    FIBRE_FIGURE,
    LINK_FIGURE,
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Calculer la durée d'une copie", TRANSFER_STEPS),
    ("Diagnostiquer une liaison à 100 Mb/s au lieu de 1 Gb/s", LINK_STEPS),
    ("Faire le bilan d'une liaison optique", FIBRE_STEPS),
)

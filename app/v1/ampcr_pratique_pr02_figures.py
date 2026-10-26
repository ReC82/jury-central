"""PR02 « Alimentation, connectique, compatibilité et sécurité » — données techniques de
référence, calculs et schémas SVG (ticket #203).

Tout est construit **depuis des données** de ce module (tuples), contrôlées par
`tests/test_ticket203_ampcr_pratique_pr02.py` :

- tensions du bloc et tolérances (`RAILS`) : guide de conception des alimentations ATX12V
  (Intel) — ±5 % sur +12 V, +5 V, +3,3 V et +5 VSB, ±10 % sur −12 V ; plages **calculées** ;
- brochages ATX 24 et EPS 8 : repris du cours PR06 (`ATX24_PINOUT`, `EPS8_PINOUT`) ;
  alimentation SATA 15 broches (spécification Serial ATA) et Molex 4 broches ;
- puissances des connecteurs PCIe (`POWER_CONNECTORS`) : spécification PCI Express CEM
  (75 W par l'emplacement x16, 75 W par un 6 broches, 150 W par un 8 broches, 600 W au plus
  par un 12V-2x6) ;
- rendement (`EFFICIENCY_LEVELS`) : seuils de la certification 80 PLUS (secteur 115 V,
  usage interne) ; puissance absorbée et pertes **calculées** ;
- budget de puissance (`power_budget`, `recommended_psu`) : somme des puissances maximales
  des fiches + marge, arrondie à la gamme supérieure ;
- compatibilité d'une configuration (`check_configuration`) : règles du cours appliquées par
  programme aux fiches fictives des cas et exercices ;
- vidéo et USB (`VIDEO_STANDARDS`, `USB_POWER`) : HDMI Licensing / VESA, USB-IF.

Les fiches produits, configurations et relevés sont des **supports fictifs** (mention
affichée) : ils ne reproduisent aucun produit réel. Aucun schéma ne vient d'une image générée.
"""

import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr01_figures import Link, Node, block_diagram_svg, fr_number
from app.v1.ampcr_pratique_pr06_figures import ATX24_PINOUT, EPS8_PINOUT
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    pin_columns_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01)

# =============================================================================================
# 1. Données de référence
# =============================================================================================

MAINS_VOLTAGE = 230  # tension du secteur en Belgique (V, alternatif, 50 Hz)
MAINS_FREQUENCY = 50


@dataclass(frozen=True)
class Rail:
    name: str  # « +12 V »
    nominal: float  # volts (signé)
    tolerance_pct: int
    color: str  # couleur de fil ATX
    uses: str


RAILS: tuple[Rail, ...] = (
    Rail("+12 V", 12.0, 5, "jaune", "processeur (par l'EPS et le VRM), carte graphique, ventilateurs, moteurs des disques"),
    Rail("+5 V", 5.0, 5, "rouge", "électronique des disques, ports USB, logique de la carte mère"),
    Rail("+3,3 V", 3.3, 5, "orange", "logique de la carte mère, emplacements PCIe et M.2"),
    Rail("+5 VSB", 5.0, 5, "violet", "veille : présente dès que le bloc est branché, même PC éteint"),
    Rail("−12 V", -12.0, 10, "bleu", "ancien port série ; très faible courant"),
)
RAILS_BY_NAME = {r.name: r for r in RAILS}


def tolerance_range(rail: Rail) -> tuple[float, float]:
    """Plage admise (V) : nominal ± tolérance ; pour −12 V, de −13,2 V à −10,8 V."""
    delta = abs(rail.nominal) * rail.tolerance_pct / 100
    return round(rail.nominal - delta, 3), round(rail.nominal + delta, 3)


def within_tolerance(rail: Rail, measured: float) -> bool:
    low, high = tolerance_range(rail)
    return low <= measured <= high


def volts(value: float, decimals: int = 2) -> str:
    sign = "−" if value < 0 else ""
    return f"{sign}{fr_number(abs(value), decimals)} V"


# Connecteurs du bloc : (nom, broches, tensions, puissance de référence, destination).
POWER_CONNECTORS: tuple[tuple[str, int, str, str, str], ...] = (
    ("ATX 24 broches (20+4)", 24, "+3,3 V, +5 V, +12 V, −12 V, +5 VSB", "—", "carte mère (alimentation principale)"),
    ("EPS 8 broches (4+4), « CPU »", 8, "+12 V (4 fils jaunes, 4 masses)", "fixée par le bloc", "processeur, par le VRM"),
    ("PCIe 6 broches", 6, "+12 V", "75 W", "carte graphique"),
    ("PCIe 8 broches (6+2), « PCIe » ou « VGA »", 8, "+12 V (3 fils jaunes, 5 masses)", "150 W", "carte graphique"),
    ("12V-2x6 (16 broches : 12 + 4 de détection)", 16, "+12 V", "600 W au plus", "carte graphique récente"),
    ("Alimentation SATA 15 broches", 15, "+3,3 V, +5 V, +12 V", "—", "disques et lecteurs SATA"),
    ("Molex 4 broches", 4, "+5 V, +12 V", "—", "anciens disques, accessoires"),
)
PCIE_SLOT_WATTS = 75  # puissance fournie par l'emplacement PCIe x16 d'une carte graphique
PCIE6_WATTS = 75
PCIE8_WATTS = 150
HPWR_MAX_WATTS = 600


def gpu_power_capacity(pcie6: int = 0, pcie8: int = 0) -> int:
    """Puissance maximale qu'une carte graphique peut tirer selon la norme : emplacement x16
    + connecteurs PCIe d'alimentation."""
    return PCIE_SLOT_WATTS + PCIE6_WATTS * pcie6 + PCIE8_WATTS * pcie8


# Alimentation SATA 15 broches : trois broches par tension ; la 11 sert aussi au démarrage
# échelonné ou au voyant d'activité selon le disque.
SATA_POWER_PINOUT: tuple[tuple[int, str, str], ...] = (
    (1, "+3,3 V", "orange"), (2, "+3,3 V", "orange"), (3, "+3,3 V", "orange"),
    (4, "Masse", "noir"), (5, "Masse", "noir"), (6, "Masse", "noir"),
    (7, "+5 V", "rouge"), (8, "+5 V", "rouge"), (9, "+5 V", "rouge"),
    (10, "Masse", "noir"), (11, "Masse / démarrage", "noir"), (12, "Masse", "noir"),
    (13, "+12 V", "jaune"), (14, "+12 V", "jaune"), (15, "+12 V", "jaune"),
)
MOLEX_PINOUT: tuple[tuple[int, str, str], ...] = (
    (1, "+12 V", "jaune"), (2, "Masse", "noir"), (3, "Masse", "noir"), (4, "+5 V", "rouge"),
)

# Formats de bloc : (nom, largeur × hauteur × profondeur en mm, usage).
PSU_FORMS: tuple[tuple[str, str, str], ...] = (
    ("ATX", "150 × 86 × 140 mm (profondeur souvent plus grande)", "tours et mini-tours"),
    ("SFX", "125 × 63,5 × 100 mm", "petits boîtiers Mini-ITX"),
)

# 80 PLUS, secteur 115 V, usage interne : (niveau, rendement minimal à 20 %, 50 %, 100 % de
# charge). Titanium exige aussi 90 % à 10 % de charge.
EFFICIENCY_LEVELS: tuple[tuple[str, int, int, int], ...] = (
    ("80 PLUS", 80, 80, 80),
    ("Bronze", 82, 85, 82),
    ("Silver", 85, 88, 85),
    ("Gold", 87, 90, 87),
    ("Platinum", 90, 92, 89),
    ("Titanium", 92, 94, 90),
)
EFFICIENCY_BY_NAME = {name: (a, b, c) for name, a, b, c in EFFICIENCY_LEVELS}


def wall_power(output_w: float, efficiency_pct: float) -> float:
    """Puissance absorbée au secteur (W) pour une puissance fournie et un rendement donnés."""
    return output_w * 100 / efficiency_pct


def losses(output_w: float, efficiency_pct: float) -> float:
    """Pertes (W) dissipées en chaleur dans le bloc."""
    return wall_power(output_w, efficiency_pct) - output_w


# Vidéo : (norme, débit maximal du lien en Gbit/s, exemple de définition sans compression).
VIDEO_STANDARDS: tuple[tuple[str, float, str], ...] = (
    ("HDMI 1.4", 10.2, "4K (3840 × 2160) à 30 Hz"),
    ("HDMI 2.0", 18, "4K à 60 Hz"),
    ("HDMI 2.1", 48, "4K à 120 Hz ; 8K à 60 Hz avec compression DSC"),
    ("DisplayPort 1.2", 21.6, "4K à 60 Hz"),
    ("DisplayPort 1.4", 32.4, "4K à 120 Hz ; 8K à 60 Hz avec compression DSC"),
    ("DisplayPort 2.1", 80, "jusqu'à 80 Gbit/s (UHBR20) : 4K et 8K à haute fréquence"),
)

# Puissance fournie par un port USB : (cas, tension, courant, puissance en W).
USB_POWER: tuple[tuple[str, str, str, float], ...] = (
    ("Port USB 2.0", "5 V", "0,5 A", 2.5),
    ("Port USB 3.x", "5 V", "0,9 A", 4.5),
    ("USB-C sans négociation (USB Type-C Current)", "5 V", "3 A", 15),
    ("USB Power Delivery (câble 5 A)", "20 V", "5 A", 100),
    ("USB Power Delivery 3.1 (EPR)", "48 V", "5 A", 240),
)

# Clés M.2 : (clé du module, ce qu'elle indique, où elle entre).
M2_KEYS: tuple[tuple[str, str, str], ...] = (
    ("M", "SSD NVMe (PCIe x4) ; parfois SATA", "emplacement à clé M uniquement"),
    ("B+M", "en général SSD M.2 SATA (deux encoches)", "emplacements à clé M ou B — même si l'interface ne suit pas"),
    ("A+E", "carte Wi-Fi / Bluetooth", "emplacement à clé E"),
)

# =============================================================================================
# 2. Budget de puissance et compatibilité (calculés)
# =============================================================================================


@dataclass(frozen=True)
class Load:
    name: str
    watts: int  # puissance maximale de la fiche (fictive)
    on_12v: bool  # alimenté essentiellement par le +12 V


def power_budget(loads: tuple[Load, ...]) -> int:
    return sum(load.watts for load in loads)


PSU_RANGE_STEP = 50  # les blocs se vendent par paliers (450, 500, 550… W)
DEFAULT_MARGIN = 0.30  # marge de 30 % : pics, vieillissement, rendement près de 50-60 % de charge


def recommended_psu(total_w: int, margin: float = DEFAULT_MARGIN, gpu_recommendation: int = 0) -> int:
    """Puissance de bloc conseillée : total + marge, arrondi au palier supérieur, jamais en
    dessous de la recommandation du fabricant de la carte graphique."""
    with_margin = math.ceil(total_w * (1 + margin) / PSU_RANGE_STEP) * PSU_RANGE_STEP
    return max(with_margin, gpu_recommendation)


def current_12v(loads: tuple[Load, ...]) -> float:
    return sum(load.watts for load in loads if load.on_12v) / 12


# Configuration du cas 2 (fiches fictives) — budget calculé dans le cours.
CASE2_LOADS: tuple[Load, ...] = (
    Load("Processeur (fiche)", 125, True),
    Load("Carte graphique (fiche)", 220, True),
    Load("Carte mère et chipset", 40, False),
    Load("2 barrettes DDR5", 10, False),
    Load("SSD NVMe", 7, False),
    Load("Disque dur 3,5\"", 8, True),
    Load("4 ventilateurs", 12, True),
)
CASE2_GPU_RECOMMENDATION = 650  # alimentation recommandée par la fiche de la carte graphique
CASE2_TOTAL = power_budget(CASE2_LOADS)
CASE2_RECOMMENDED = recommended_psu(CASE2_TOTAL, gpu_recommendation=CASE2_GPU_RECOMMENDATION)
CASE2_MARGIN_ONLY = recommended_psu(CASE2_TOTAL)


@dataclass(frozen=True)
class Configuration:
    """Fiches fictives d'un devis : chaque champ vient d'une fiche produit."""

    cpu_socket: str
    board_socket: str
    board_form: str
    board_memory: str  # « DDR5 DIMM »
    board_m2: str  # « NVMe » | « NVMe ou SATA »
    ram: str  # « DDR4 DIMM »
    ssd_m2: str  # « NVMe » | « SATA »
    case_forms: tuple[str, ...]
    case_gpu_max_mm: int
    case_cooler_max_mm: int
    gpu_length_mm: int
    gpu_pcie8_needed: int
    gpu_psu_recommendation_w: int
    cooler_height_mm: int
    cooler_sockets: tuple[str, ...]
    psu_watts: int
    psu_pcie8: int
    psu_form: str
    case_psu_forms: tuple[str, ...]


def check_configuration(cfg: Configuration) -> list[tuple[str, bool, str]]:
    """Grille de compatibilité du cours (chapitre 9) : (critère, conforme ?, justification)."""
    checks = [
        ("Processeur ↔ socket", cfg.cpu_socket == cfg.board_socket,
         f"processeur {cfg.cpu_socket}, carte {cfg.board_socket}"),
        ("Mémoire ↔ carte", cfg.ram == cfg.board_memory, f"barrettes {cfg.ram}, carte {cfg.board_memory}"),
        ("Carte mère ↔ boîtier", cfg.board_form in cfg.case_forms,
         f"carte {cfg.board_form}, boîtier {' / '.join(cfg.case_forms)}"),
        ("SSD M.2 ↔ emplacement", cfg.ssd_m2 in cfg.board_m2, f"SSD M.2 {cfg.ssd_m2}, emplacement {cfg.board_m2}"),
        ("Carte graphique ↔ boîtier", cfg.gpu_length_mm <= cfg.case_gpu_max_mm,
         f"{cfg.gpu_length_mm} mm pour {cfg.case_gpu_max_mm} mm au plus"),
        ("Ventirad ↔ boîtier et socket",
         cfg.cooler_height_mm <= cfg.case_cooler_max_mm and cfg.board_socket in cfg.cooler_sockets,
         f"{cfg.cooler_height_mm} mm pour {cfg.case_cooler_max_mm} mm au plus ; sockets {', '.join(cfg.cooler_sockets)}"),
        ("Bloc : puissance", cfg.psu_watts >= cfg.gpu_psu_recommendation_w,
         f"{cfg.psu_watts} W pour {cfg.gpu_psu_recommendation_w} W recommandés"),
        ("Bloc : connecteurs PCIe", cfg.psu_pcie8 >= cfg.gpu_pcie8_needed,
         f"{cfg.psu_pcie8} × PCIe 8 broches pour {cfg.gpu_pcie8_needed} nécessaires"),
        ("Bloc ↔ boîtier", cfg.psu_form in cfg.case_psu_forms, f"bloc {cfg.psu_form}, boîtier {' / '.join(cfg.case_psu_forms)}"),
    ]
    return checks


def failed_checks(cfg: Configuration) -> list[str]:
    return [label for label, ok, _why in check_configuration(cfg) if not ok]


# Cas 1 du cours : devis à contrôler (fiches fictives).
CASE1_CONFIG = Configuration(
    cpu_socket="AM5", board_socket="AM5", board_form="microATX", board_memory="DDR5 DIMM",
    board_m2="NVMe", ram="DDR4 DIMM", ssd_m2="SATA",
    case_forms=("microATX", "Mini-ITX"), case_gpu_max_mm=300, case_cooler_max_mm=160,
    gpu_length_mm=285, gpu_pcie8_needed=2, gpu_psu_recommendation_w=650,
    cooler_height_mm=155, cooler_sockets=("AM4", "AM5", "LGA1700"),
    psu_watts=550, psu_pcie8=1, psu_form="ATX", case_psu_forms=("ATX",),
)
# Exercice E08 : autre devis (fiches fictives).
E08_CONFIG = Configuration(
    cpu_socket="LGA1700", board_socket="LGA1700", board_form="ATX", board_memory="DDR5 DIMM",
    board_m2="NVMe ou SATA", ram="DDR5 DIMM", ssd_m2="NVMe",
    case_forms=("microATX", "Mini-ITX"), case_gpu_max_mm=330, case_cooler_max_mm=150,
    gpu_length_mm=310, gpu_pcie8_needed=2, gpu_psu_recommendation_w=700,
    cooler_height_mm=158, cooler_sockets=("AM4", "AM5", "LGA1700"),
    psu_watts=750, psu_pcie8=2, psu_form="ATX", case_psu_forms=("ATX", "SFX"),
)

# Relevé du cas 4 et de l'exercice E07 : mesures d'un testeur, à vide et en charge.
CASE4_MEASURES: tuple[tuple[str, float, float], ...] = (
    ("+12 V", 12.08, 11.21),
    ("+5 V", 5.04, 4.98),
    ("+3,3 V", 3.33, 3.30),
    ("+5 VSB", 5.02, 5.01),
)
E07_MEASURES: tuple[tuple[str, float], ...] = (
    ("+12 V", 11.62),
    ("+5 V", 5.31),
    ("+3,3 V", 3.18),
    ("+5 VSB", 4.71),
    ("−12 V", -11.2),
)


def measure_lines(measures: tuple[tuple[str, float, float], ...]) -> tuple[str, ...]:
    """Relevé d'un testeur sous forme de capture (deux colonnes : à vide, en charge)."""
    lines = [
        "Relevé du testeur — bloc ATX (fictif)",
        f"{'Rail':<8}{'À vide':>10}{'En charge':>12}",
    ]
    lines += [f"{name:<8}{fr_number(idle, 2):>8} V{fr_number(load, 2):>10} V" for name, idle, load in measures]
    return tuple(lines)


# =============================================================================================
# 3. Schémas
# =============================================================================================

# --- 3.1 Chaîne d'alimentation -------------------------------------------------------------

CHAIN_NODES: tuple[Node, ...] = (
    Node("mains", ("Prise secteur", "230 V alternatif, 50 Hz"), 100, 8, 180, 46),
    Node("psu", ("Bloc d'alimentation", "redresse, découpe, régule"), 100, 100, 180, 50),
    Node("r12", ("+12 V", "CPU (EPS → VRM)", "GPU, ventilateurs"), 4, 214, 120, 64),
    Node("r5", ("+5 V, +3,3 V", "SSD, ports USB", "logique carte"), 130, 214, 120, 64),
    Node("vsb", ("+5 VSB", "veille, présente", "dès le branchement"), 256, 214, 120, 64),
)
CHAIN_LINKS: tuple[Link, ...] = (
    Link("mains", "psu", "AC", "v"),
    Link("psu", "r12", "DC", "v"),
    Link("psu", "r5", "DC", "v"),
    Link("psu", "vsb", "DC", "v"),
)
CHAIN_FIGURE = Figure(
    key="pr02-chaine-alimentation",
    title="Du secteur aux composants : la chaîne d'alimentation",
    alt=(
        "Schéma-bloc. La prise secteur fournit du 230 volts alternatif à 50 hertz au bloc "
        "d'alimentation, qui le redresse, le découpe et le régule. Le bloc fournit trois groupes "
        "de tensions continues : le +12 volts pour le processeur (par le connecteur EPS et le "
        "VRM), la carte graphique, les ventilateurs et les moteurs des disques ; le +5 volts et "
        "le +3,3 volts pour les SSD, les ports USB et la logique de la carte mère ; le +5 volts "
        "de veille, présent dès que le bloc est branché, même PC éteint."
    ),
    caption=(
        "Le bloc transforme le courant alternatif (AC) du secteur en tensions continues (DC). "
        "Le +12 V porte l'essentiel de la puissance d'un PC moderne ; le +5 VSB reste présent "
        "tant que le câble secteur est branché."
    ),
    svg=block_diagram_svg(CHAIN_NODES, CHAIN_LINKS, width=380, height=306,
                          footer="Support simplifié — le −12 V (très faible courant) n'est pas représenté."),
)

# --- 3.2 Brochages ---------------------------------------------------------------------------

ATX24_FIGURE = Figure(
    key="pr02-atx24",
    title="Connecteur principal ATX 24 broches",
    alt=(
        "Tableau des 24 broches du connecteur ATX, rangée 1 à 12 puis rangée 13 à 24 : "
        + " ; ".join(f"broche {n} {s} fil {c}" for n, s, c in ATX24_PINOUT)
        + "."
    ),
    caption=(
        "ATX 24 broches : colonne de gauche = broches 1 à 12, colonne de droite = 13 à 24 (la 13 "
        "en face de la 1). Fils : jaune +12 V, rouge +5 V, orange +3,3 V, violet +5 VSB, vert "
        "PS_ON# (mise en marche), gris PWR_OK (tensions stables), noir masse. Les broches 11, 12, "
        "23 et 24 forment la partie « +4 » détachable."
    ),
    svg=pin_columns_svg(ATX24_PINOUT, title="ATX 24 broches — carte mère", rows=12),
)

EPS8_FIGURE = Figure(
    key="pr02-eps8",
    title="Connecteur processeur EPS 8 broches",
    alt=(
        "Tableau des 8 broches du connecteur EPS du processeur : broches 1 à 4 masse, fil noir ; "
        "broches 5 à 8 +12 volts, fil jaune ; la broche 5 est en face de la broche 1."
    ),
    caption=(
        "EPS 8 broches (« CPU ») : 4 masses et 4 × +12 V. Le PCIe 8 broches de la carte graphique "
        "place ses +12 V autrement et a un détrompage différent : les deux ne s'échangent jamais."
    ),
    svg=pin_columns_svg(EPS8_PINOUT, title="EPS 8 broches — processeur", rows=4),
)

_PALETTE = {"orange": "#e8740c", "rouge": "#c62828", "noir": "#1b1b1b", "jaune": "#e3c100"}


def pin_row_svg(rows: tuple[tuple[str, tuple[tuple[int, str, str], ...]], ...]) -> str:
    """Connecteurs à une seule rangée (SATA, Molex) : une case par broche, numéro, tension en
    texte et couleur de fil en texte ; la pastille n'est qu'un repère."""
    width, pin_w, gap, left = 380, 23, 1.5, 6
    parts: list[str] = []
    y = 6
    for title, pins in rows:
        parts.append(f'<text x="{left}" y="{y + 12}" font-size="13" font-weight="700">{escape(title)}</text>')
        y += 20
        for index, (number, signal, color) in enumerate(pins):
            x = left + index * (pin_w + gap)
            parts.append(
                f'<rect data-row="{escape(title)}" data-pin="{number}" data-signal="{escape(signal)}" '
                f'data-color="{escape(color)}" x="{x:.1f}" y="{y}" width="{pin_w}" height="78" rx="3" '
                f'fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1"/>'
                f'<rect x="{x + 5:.1f}" y="{y + 4}" width="{pin_w - 10}" height="12" rx="2" '
                f'fill="{_PALETTE.get(color, "#ffffff")}" stroke="{_STROKE}" stroke-width="0.8"/>'
                f'<text x="{x + pin_w / 2:.1f}" y="{y + 30}" font-size="10.5" font-weight="700" '
                f'text-anchor="middle">{number}</text>'
            )
            label = {"+3,3 V": "3,3", "+5 V": "5", "+12 V": "12"}.get(signal, "M")
            parts.append(
                f'<text x="{x + pin_w / 2:.1f}" y="{y + 50}" font-size="10" text-anchor="middle">{label}</text>'
            )
        y += 96
    parts.append(_text_lines(left, y + 4, ["Chiffre = tension en volts ; M = masse (fil noir)."], size=11))
    return _svg(width, y + 14, parts)


SATA_MOLEX_FIGURE = Figure(
    key="pr02-sata-molex",
    title="Alimentation SATA 15 broches et Molex 4 broches",
    alt=(
        "Deux connecteurs à une rangée. Alimentation SATA, 15 broches : "
        + " ; ".join(f"broche {n} {s}" for n, s, _c in SATA_POWER_PINOUT)
        + ". Molex, 4 broches : "
        + " ; ".join(f"broche {n} {s} fil {c}" for n, s, c in MOLEX_PINOUT)
        + "."
    ),
    caption=(
        "SATA 15 broches : trois broches par tension (+3,3 V, +5 V, +12 V) et des masses ; "
        "beaucoup de blocs ne câblent pas le +3,3 V. Molex : +12 V (jaune), deux masses, +5 V "
        "(rouge). Le câble de données SATA, lui, n'a que 7 contacts et ne transporte aucune "
        "alimentation."
    ),
    svg=pin_row_svg(
        (("Alimentation SATA — 15 broches", SATA_POWER_PINOUT), ("Molex — 4 broches", MOLEX_PINOUT))
    ),
)

# --- 3.3 Budget de puissance -----------------------------------------------------------------


def budget_svg(loads: tuple[Load, ...], *, margin: float, recommended: int, gpu_reco: int) -> str:
    """Barres horizontales (une par composant), puis total, total avec marge et bloc retenu ;
    chaque barre porte sa valeur en texte (lecture sans couleur)."""
    width, left, label_w, bar_h, gap = 380, 6, 140, 18, 6
    total = power_budget(loads)
    scale = (width - left - label_w - 50) / max(recommended, gpu_reco)
    parts: list[str] = []
    y = 8
    rows: list[tuple[str, int, str]] = [(load.name, load.watts, "#cfd8ea") for load in loads]
    rows += [
        ("Total", total, "#8aa1c9"),
        (f"Total + marge {int(margin * 100)} %", round(total * (1 + margin)), "#5d7bb0"),
        ("Bloc retenu", recommended, "#2e6b3a"),
    ]
    for index, (name, watts, fill) in enumerate(rows):
        if index == len(loads):
            parts.append(f'<path d="M{left} {y - 3} H{width - 6}" stroke="{_STROKE}" stroke-width="1"/>')
            y += 4
        lines = _wrap(name, 30)
        parts.append(_text_lines(left, y + 13, lines[:1], size=10.5, weight="700" if index >= len(loads) else "400"))
        w = watts * scale
        parts.append(
            f'<rect data-load="{escape(name)}" data-watts="{watts}" x="{left + label_w}" y="{y}" '
            f'width="{w:.1f}" height="{bar_h}" rx="3" fill="{fill}" stroke="{_STROKE}" stroke-width="0.8"/>'
            f'<text x="{left + label_w + w + 4:.1f}" y="{y + 13}" font-size="10.5">{watts} W</text>'
        )
        y += bar_h + gap
    return _svg(width, y + 6, parts)


BUDGET_FIGURE = Figure(
    key="pr02-budget-puissance",
    title="Budget de puissance du cas 2",
    alt=(
        "Barres horizontales des puissances maximales : "
        + " ; ".join(f"{load.name} {load.watts} watts" for load in CASE2_LOADS)
        + f". Total {CASE2_TOTAL} watts ; total avec 30 % de marge "
        f"{round(CASE2_TOTAL * 1.3)} watts, soit le palier de {CASE2_MARGIN_ONLY} watts ; la carte "
        f"graphique recommande {CASE2_GPU_RECOMMENDATION} watts : bloc retenu {CASE2_RECOMMENDED} watts."
    ),
    caption=(
        "On additionne les puissances maximales des fiches, on ajoute une marge (ici 30 %), on "
        "arrondit au palier commercial supérieur et on ne descend jamais sous la recommandation "
        "du fabricant de la carte graphique. Configuration fictive."
    ),
    svg=budget_svg(CASE2_LOADS, margin=DEFAULT_MARGIN, recommended=CASE2_RECOMMENDED,
                   gpu_reco=CASE2_GPU_RECOMMENDATION),
)

# --- 3.4 Flux d'air ---------------------------------------------------------------------------

# (clé, entrée ou sortie, x1, y1, x2, y2, libellé, x du libellé, y du libellé)
AIRFLOW: tuple[tuple[str, str, int, int, int, int, str, int, int], ...] = (
    ("front-1", "in", 374, 90, 300, 90, "entrée façade", 330, 80),
    ("front-2", "in", 374, 170, 300, 170, "entrée façade", 330, 160),
    ("rear", "out", 70, 90, 6, 90, "sortie arrière", 36, 80),
    ("top", "out", 150, 62, 150, 10, "sortie haute", 210, 30),
    ("psu", "in", 140, 300, 140, 262, "entrée du bloc (filtre)", 230, 292),
    ("psu-out", "out", 70, 236, 6, 236, "sortie bloc", 36, 226),
)


def airflow_svg() -> str:
    width = 380
    parts = [
        f'<rect x="70" y="62" width="230" height="200" rx="6" fill="#ffffff" stroke="{_STROKE}" stroke-width="2"/>',
        '<text x="185" y="80" font-size="10.5" text-anchor="middle" font-weight="700">Tour vue de côté</text>',
        '<text x="185" y="94" font-size="10" text-anchor="middle">arrière à gauche, façade à droite</text>',
        f'<rect x="110" y="106" width="70" height="38" rx="4" fill="#f4f6fb" stroke="{_STROKE}"/>',
        '<text x="145" y="129" font-size="10.5" text-anchor="middle">ventirad</text>',
        f'<rect x="90" y="166" width="150" height="16" rx="3" fill="#f4f6fb" stroke="{_STROKE}"/>',
        '<text x="165" y="178" font-size="10" text-anchor="middle">carte graphique</text>',
        f'<rect x="74" y="214" width="140" height="44" rx="4" fill="#eef3ee" stroke="{_STROKE}"/>',
        '<text x="144" y="240" font-size="10.5" text-anchor="middle">bloc d’alimentation</text>',
    ]
    for key, kind, x1, y1, x2, y2, label, lx, ly in AIRFLOW:
        dash = "" if kind == "in" else ' stroke-dasharray="6 3"'
        parts.append(
            f'<path data-flow="{kind}" data-key="{key}" d="M{x1} {y1} L{x2} {y2}" stroke="#1f5fbf" '
            f'stroke-width="3"{dash}/>'
        )
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        p1 = (x2 - 9 * ux + 5 * px, y2 - 9 * uy + 5 * py)
        p2 = (x2 - 9 * ux - 5 * px, y2 - 9 * uy - 5 * py)
        parts.append(
            f'<path d="M{p1[0]:.1f} {p1[1]:.1f} L{x2} {y2} L{p2[0]:.1f} {p2[1]:.1f}" fill="none" '
            f'stroke="#1f5fbf" stroke-width="2.5"/>'
        )
        parts.append(f'<text x="{lx}" y="{ly}" font-size="10" text-anchor="middle">{escape(label)}</text>')
    parts.append(_text_lines(6, 322, ["Trait plein = entrée d'air frais ;", "pointillé = sortie d'air chaud."], size=10.5, step=14))
    return _svg(width, 346, parts)


AIRFLOW_FIGURE = Figure(
    key="pr02-flux-air",
    title="Flux d'air dans une tour",
    alt=(
        "Tour vue de côté, façade à droite. Deux ventilateurs de façade font entrer l'air frais "
        "vers le ventirad et la carte graphique ; l'air chaud sort par un ventilateur arrière et "
        "par le haut. Le bloc d'alimentation, en bas, aspire l'air par un filtre sous le boîtier "
        "et le rejette à l'arrière, dans son propre circuit."
    ),
    caption=(
        "Flux classique avant → arrière et bas → haut (l'air chaud monte). Un filtre bouché, un "
        "ventilateur monté à l'envers ou des câbles devant la façade font monter les températures."
    ),
    svg=airflow_svg(),
)

# --- 3.5 Symptômes d'alimentation -----------------------------------------------------------

SYMPTOM_TREE: tuple[tuple[str, str], ...] = (
    ("Un voyant ou un ventilateur réagit-il à l'appui sur le bouton ?",
     "Prise, câble secteur, multiprise, interrupteur du bloc sur I ; puis bouton de façade et testeur d'alimentation."),
    ("Le PC reste-t-il allumé plus de quelques secondes ?",
     "Arrêt de protection : ATX 24 ou EPS mal branché, court-circuit, bloc défaillant → configuration minimale, testeur."),
    ("Reste-t-il stable sous forte charge (jeu, calcul) ?",
     "Bloc sous-dimensionné ou fatigué, câbles PCIe manquants → mesurer en charge, essayer un bloc connu bon."),
    ("Les tensions mesurées sont-elles dans les tolérances (±5 %) ?",
     "Bloc hors tolérance : le remplacer, jamais l'ouvrir ni le réparer."),
)
SYMPTOM_FINAL = "Alimentation probablement hors de cause : poursuivre le diagnostic (PR06) — mémoire, températures, pilotes."
SYMPTOM_FIGURE = Figure(
    key="pr02-symptomes-alimentation",
    title="Évaluer des symptômes d'alimentation",
    alt=(
        "Arbre de décision en quatre questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(SYMPTOM_TREE, start=1))
        + f" Si toutes les réponses sont oui : {SYMPTOM_FINAL}"
    ),
    caption=(
        "Chaque « non » oriente vers une piste et des tests ; « c'est l'alimentation » reste une "
        "hypothèse tant qu'une mesure ou un bloc connu bon ne l'a pas confirmée."
    ),
    svg=decision_tree_svg(SYMPTOM_TREE, SYMPTOM_FINAL),
)

# --- 3.6 Procédure sûre -----------------------------------------------------------------------

SAFE_STEPS: tuple[tuple[str, str], ...] = (
    ("Couper", "Arrêter le système, interrupteur du bloc sur 0, débrancher le câble secteur."),
    ("Décharger", "Appuyer quelques secondes sur le bouton de démarrage ; vérifier que la LED de veille est éteinte."),
    ("Se protéger", "Bracelet antistatique relié au châssis, tapis, aucun bijou ; pièces dans leur sachet."),
    ("Repérer", "Photographier et noter chaque câble (ATX 24, EPS, PCIe, SATA) avant de débrancher."),
    ("Remplacer", "Bloc de même format, assez puissant, avec ses propres câbles ; ventilateur vers le filtre."),
    ("Contrôler", "Tous les connecteurs clipsés, aucun câble dans un ventilateur ; tensions, test en charge, compte rendu."),
)
SAFE_FIGURE = Figure(
    key="pr02-procedure-sure",
    title="Remplacer un bloc d'alimentation en sécurité",
    alt=(
        "Six étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(SAFE_STEPS, start=1))
        + "."
    ),
    caption=(
        "Procédure écrite attendue : chaque étape est nommée et justifiée. Un bloc défectueux se "
        "remplace : on ne l'ouvre jamais."
    ),
    svg=step_flow_svg(SAFE_STEPS),
)

PR02_FIGURES: tuple[Figure, ...] = (
    CHAIN_FIGURE,
    ATX24_FIGURE,
    EPS8_FIGURE,
    SATA_MOLEX_FIGURE,
    BUDGET_FIGURE,
    AIRFLOW_FIGURE,
    SYMPTOM_FIGURE,
    SAFE_FIGURE,
)

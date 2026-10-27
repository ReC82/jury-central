"""PR18 « Installation physique d'un mini-réseau » — données de référence, calculs et schémas
SVG (ticket #219).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket219_ampcr_pratique_pr18.py` :

- plan des locaux d'exemple (pièces, baie, prises, point d'accès, arrivée de l'opérateur) et
  longueur estimée de chaque lien (`PLAN`, `horizontal_m`, `run_length_m`) ; contrôle des
  longueurs (`channel_errors` de PR13, lien permanent ≤ 90 m) ;
- topologie en étoile logique tirée du même plan (`star_svg`) ;
- dimensionnement : ports du switch (`switch_ports_needed`, `choose_switch`), panneaux de
  brassage (`panels_needed`), hauteur de baie (`RackItem`, `rack_units`, `choose_rack`),
  boîtes de câble de 305 m (`boxes_needed`) ;
- alimentation PoE : puissance réservée par classe (`POE_CLASS_W`, `poe_budget_w`) ;
- repérage identique aux deux extrémités (`label_for` de PR13) et plan de brassage
  (`patch_rows`) ;
- devis et nomenclature : totaux HT, TVA 21 %, TTC (`QuoteLine`, `quote_totals`) ;
- recette du câblage (`LinkTest`, `link_verdict`) et validation du réseau dans l'ordre
  (`VALIDATION_CHECKS`, `validation_diagnosis`) ;
- trois procédures illustrées (`INSTALL_STEPS`, `TEST_STEPS`, `CHECK_STEPS`) ;
- cinq schémas à compléter servis aussi en fichiers statiques (`STATIC_FIGURES`).

Valeurs de référence (normes publiques ; la fiche du fabricant fait foi) :
- TIA-568 / ISO/IEC 11801 : lien permanent ≤ 90 m, canal ≤ 100 m (données de PR15, contrôle de
  PR13) ; distance aux câbles d'énergie selon EN 50174-2 (données de PR13) ;
- IEEE 802.3af/at/bt : puissance fournie par le switch (PSE) selon la classe de l'appareil :
  classe 0 15,4 W, 1 4 W, 2 7 W, 3 15,4 W, 4 30 W, 5 45 W, 6 60 W, 7 75 W, 8 90 W ;
- câble en boîte de 305 m (1 000 pieds), conditionnement courant ; hauteur d'équipement en
  unités de baie (1 U = 44,45 mm) ;
- TVA belge au taux normal : 21 %.

**Conventions du cours**, signalées dans le texte : longueur d'un lien = parcours horizontal
le long des murs (somme des écarts en x et en y) + 3 m de montée et de descente + 2 m de
réserve, arrondie au mètre supérieur ; 20 % de ports de réserve sur le switch ; 25 % d'unités
libres dans la baie ; deux prises par poste de travail ; repère « B1-P1-07 ». Les plans, prix,
appareils et relevés sont **fictifs**. Chaque schéma porte son information en texte : la
couleur n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr13_figures import (
    SEPARATION_MM,
    channel_errors,
    label_for,
    min_separation_mm,
)
from app.v1.ampcr_pratique_pr14_figures import fr
from app.v1.ampcr_pratique_pr15_figures import CHANNEL_MAX_M, CORDS_MAX_M, PERMANENT_LINK_MAX_M
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, _wrap, step_flow_svg

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
_STROKE = "#33415c"
_FILL = "#dbe4f3"
_ROOM = "#f7f8fb"
_BAD = "#b3261e"
_OK = "#1d6b34"

__all__ = [  # réexports utilisés par le cours et la banque
    "CHANNEL_MAX_M",
    "CORDS_MAX_M",
    "PERMANENT_LINK_MAX_M",
    "SEPARATION_MM",
    "channel_errors",
    "fr",
    "label_for",
    "min_separation_mm",
]

# =============================================================================================
# 1. Plan des locaux d'exemple et longueurs des liens
# =============================================================================================

VERTICAL_M = 3  # montée depuis la baie + descente vers la prise (convention du cours)
SLACK_M = 2  # réserve (love) aux deux extrémités (convention du cours)


@dataclass(frozen=True)
class Room:
    name: str
    x: float
    y: float
    w: float
    h: float
    short: str = ""  # libellé affiché dans une petite pièce (expliqué dans la légende)


@dataclass(frozen=True)
class Point:
    key: str  # P01…, AP, BOX, BAIE
    label: str
    x: float
    y: float
    poe_class: int | None = None  # classe PoE de l'appareil branché (None : pas de PoE)


@dataclass(frozen=True)
class FloorPlan:
    name: str
    width_m: float
    depth_m: float
    rooms: tuple[Room, ...]
    rack: Point
    box: Point
    outlets: tuple[Point, ...]  # prises reliées à la baie (y compris celle du point d'accès)


def horizontal_m(a: Point, b: Point) -> float:
    """Parcours horizontal le long des murs et des chemins de câbles : écart en x + écart en y
    (jamais en diagonale à travers les pièces)."""
    return round(abs(a.x - b.x) + abs(a.y - b.y), 2)


def run_length_m(horizontal: float) -> int:
    """Longueur de câble à prévoir pour un lien (convention du cours) : parcours horizontal +
    montée et descente + réserve, arrondie au mètre supérieur."""
    return math.ceil(horizontal + VERTICAL_M + SLACK_M - 1e-9)


PLAN = FloorPlan(
    name="Cabinet d'expertise comptable, rez-de-chaussée (24 m × 14 m)",
    width_m=24,
    depth_m=14,
    rooms=(
        Room("Accueil", 0, 0, 8, 7),
        Room("Bureau 1", 8, 0, 8, 7),
        Room("Bureau 2", 16, 0, 8, 7),
        Room("Réunion", 0, 7, 10, 7),
        Room("Local technique", 10, 7, 3, 3, "LT"),
        Room("Sanitaires", 10, 10, 3, 4, "WC"),
        Room("Plateau", 13, 7, 11, 7),
    ),
    rack=Point("BAIE", "Baie murale (panneau + switch)", 11.5, 8.5),
    box=Point("BOX", "Box de l'opérateur (arrivée de la ligne)", 10.5, 9.5),
    outlets=(
        Point("P01", "Accueil, poste", 2, 6.5),
        Point("P02", "Accueil, poste (2e prise)", 3, 6.5),
        Point("P03", "Accueil, imprimante multifonction", 7.5, 1),
        Point("P04", "Bureau 1, poste", 12, 0.5),
        Point("P05", "Bureau 1, poste (2e prise)", 13, 0.5),
        Point("P06", "Bureau 2, poste", 20, 0.5),
        Point("P07", "Bureau 2, poste (2e prise)", 21, 0.5),
        Point("P08", "Réunion, écran de présentation", 5, 13.5),
        Point("P09", "Plateau, poste 1", 17, 13.5),
        Point("P10", "Plateau, poste 1 (2e prise)", 18, 13.5),
        Point("P11", "Plateau, poste 2", 23.5, 10),
        Point("P12", "Plateau, poste 2 (2e prise)", 23.5, 11.5),
        Point("P13", "Plafond du plateau, point d'accès Wi-Fi", 20.5, 9.5, poe_class=4),
    ),
)


def plan_runs(plan: FloorPlan) -> tuple[tuple[str, float, int], ...]:
    """(repère, parcours horizontal, longueur à prévoir) pour chaque prise du plan."""
    return tuple(
        (o.key, horizontal_m(plan.rack, o), run_length_m(horizontal_m(plan.rack, o))) for o in plan.outlets
    )


PLAN_RUNS = plan_runs(PLAN)
PLAN_TOTAL_M = sum(length for _k, _h, length in PLAN_RUNS)

# =============================================================================================
# 2. Dimensionnement : switch, panneaux, baie, câble
# =============================================================================================

SWITCH_SIZES: tuple[int, ...] = (8, 16, 24, 48)
PORT_RESERVE = 0.2  # convention du cours
PANEL_PORTS = 24  # panneau de brassage 1 U courant
BOX_M = 305  # boîte de câble (1 000 pieds)
RACK_SIZES_U: tuple[int, ...] = (6, 9, 12, 15, 18, 22, 27, 42)
RACK_RESERVE = 0.25  # convention du cours
U_MM = 44.45


def switch_ports_needed(links: int, uplinks: int = 1) -> int:
    """Ports à prévoir : liens à brasser + 20 % de réserve (arrondi au-dessus) + liens montants
    (box, autre switch)."""
    return math.ceil(links * (1 + PORT_RESERVE) - 1e-9) + uplinks


def choose_switch(links: int, uplinks: int = 1) -> int:
    needed = switch_ports_needed(links, uplinks)
    for size in SWITCH_SIZES:
        if size >= needed:
            return size
    raise ValueError("Plus de 48 ports : prévoir plusieurs switchs.")


def panels_needed(links: int) -> int:
    return math.ceil(links / PANEL_PORTS)


@dataclass(frozen=True)
class RackItem:
    name: str
    units: int


def rack_units(items: tuple[RackItem, ...]) -> int:
    return sum(i.units for i in items)


def choose_rack(used_u: int) -> int:
    """Plus petite baie standard qui garde au moins 25 % d'unités libres (convention)."""
    needed = math.ceil(used_u * (1 + RACK_RESERVE) - 1e-9)
    for size in RACK_SIZES_U:
        if size >= needed:
            return size
    raise ValueError("Plus de 42 U : prévoir plusieurs baies.")


def boxes_needed(lengths: tuple[int, ...] | list[int]) -> int:
    """Boîtes de 305 m : un lien ne se raboute jamais, chaque longueur doit tenir dans le reste
    d'une boîte (rangement des plus longues d'abord)."""
    remaining: list[float] = []
    for length in sorted(lengths, reverse=True):
        if length > BOX_M:
            raise ValueError("Lien plus long qu'une boîte : impossible en paire torsadée.")
        for i, left in enumerate(remaining):
            if left >= length:
                remaining[i] = left - length
                break
        else:
            remaining.append(BOX_M - length)
    return len(remaining)


RACK_LAYOUT: tuple[RackItem, ...] = (  # du haut vers le bas (exemple du cours)
    RackItem("Panneau de brassage 24 ports", 1),
    RackItem("Passe-câbles (guide-cordons)", 1),
    RackItem("Switch 24 ports PoE", 1),
    RackItem("Étagère : box de l'opérateur", 2),
    RackItem("Bandeau de prises électriques", 1),
)
RACK_USED_U = rack_units(RACK_LAYOUT)

# =============================================================================================
# 3. Alimentation PoE
# =============================================================================================

# Puissance réservée au port du switch (PSE) selon la classe annoncée par l'appareil
# (IEEE 802.3af/at/bt).
POE_CLASS_W: dict[int, float] = {0: 15.4, 1: 4.0, 2: 7.0, 3: 15.4, 4: 30.0, 5: 45.0, 6: 60.0, 7: 75.0, 8: 90.0}
POE_STANDARDS: tuple[tuple[str, str, str], ...] = (
    ("IEEE 802.3af (PoE)", "classes 0 à 3", "15,4 W par port"),
    ("IEEE 802.3at (PoE+)", "classe 4", "30 W par port"),
    ("IEEE 802.3bt (PoE++)", "classes 5 à 8", "45 à 90 W par port"),
)


def poe_budget_w(classes: list[int] | tuple[int, ...]) -> float:
    return round(sum(POE_CLASS_W[c] for c in classes), 1)


POE_OK = "Budget suffisant"
POE_KO = "Budget dépassé"


def poe_verdict(classes: list[int] | tuple[int, ...], switch_budget_w: float) -> str:
    return POE_OK if poe_budget_w(classes) <= switch_budget_w + 1e-9 else POE_KO


# Exemple du cours : 1 point d'accès (classe 4), 4 caméras (classe 3), 6 téléphones (classe 2).
POE_EXAMPLE: tuple[tuple[str, int, int], ...] = (
    ("Point d'accès Wi-Fi", 4, 1),
    ("Caméra IP", 3, 4),
    ("Téléphone IP", 2, 6),
)
POE_EXAMPLE_CLASSES = tuple(c for _n, c, q in POE_EXAMPLE for _ in range(q))
POE_EXAMPLE_TOTAL = poe_budget_w(POE_EXAMPLE_CLASSES)
POE_EXAMPLE_SWITCHES: tuple[tuple[str, float], ...] = (("Switch A", 65.0), ("Switch B", 130.0), ("Switch C", 370.0))

# =============================================================================================
# 4. Repérage et plan de brassage
# =============================================================================================


def patch_rows(plan: FloorPlan, rack: int = 1, panel: int = 1) -> tuple[tuple[str, str, int, str], ...]:
    """(repère, destination, port du switch, prise) : le port n du panneau est brassé sur le
    port n du switch (convention du cours) ; le repère est le même à la prise et au panneau."""
    rows = []
    for port, outlet in enumerate(plan.outlets, start=1):
        rows.append((label_for(rack, panel, port), outlet.label, port, outlet.key))
    return tuple(rows)


PATCH_ROWS = patch_rows(PLAN)

# =============================================================================================
# 5. Devis et nomenclature
# =============================================================================================

VAT_RATE = 0.21


@dataclass(frozen=True)
class QuoteLine:
    ref: str
    label: str
    quantity: int
    unit_price: float  # € HT

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


def quote_totals(lines: tuple[QuoteLine, ...]) -> tuple[float, float, float]:
    """(total HT, TVA 21 %, total TTC), arrondis au centime."""
    ht = round(sum(line.total for line in lines), 2)
    vat = round(ht * VAT_RATE, 2)
    return ht, vat, round(ht + vat, 2)


def euro(value: float) -> str:
    """Montant au format belge : 1 234,50 €."""
    whole, cents = f"{value:.2f}".split(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return f"{' '.join(groups)},{cents} €"


# Nomenclature du plan d'exemple (prix fictifs, € HT).
PLAN_LINKS = len(PLAN.outlets)
PLAN_SWITCH = choose_switch(PLAN_LINKS)
PLAN_BOXES = boxes_needed([length for _k, _h, length in PLAN_RUNS])
PLAN_RACK_U = choose_rack(RACK_USED_U)
PLAN_QUOTE: tuple[QuoteLine, ...] = (
    QuoteLine("C6A", "Câble Cat6A U/FTP monobrin, boîte de 305 m", PLAN_BOXES, 289.00),
    QuoteLine("KS", "Connecteur keystone Cat6A blindé (prise + panneau)", 2 * PLAN_LINKS, 7.50),
    QuoteLine("PP24", "Panneau de brassage 24 ports vide, 1 U", panels_needed(PLAN_LINKS), 39.00),
    QuoteLine("BOI", "Boîtier mural apparent 1 poste", PLAN_LINKS, 6.20),
    QuoteLine("CB1", "Cordon de brassage Cat6A, 1 m", PLAN_LINKS, 4.90),
    QuoteLine("CP3", "Cordon de poste Cat6A, 3 m", PLAN_LINKS, 6.90),
    QuoteLine("SW24", "Switch administrable 24 ports, PoE+ 195 W", 1, 420.00),
    QuoteLine("B9U", f"Baie murale {PLAN_RACK_U} U, porte vitrée à clé", 1, 189.00),
    QuoteLine("PC1U", "Passe-câbles 1 U", 1, 18.00),
    QuoteLine("ET2U", "Étagère 2 U", 1, 24.00),
    QuoteLine("PDU", "Bandeau 6 prises électriques 1 U", 1, 35.00),
)
PLAN_QUOTE_TOTALS = quote_totals(PLAN_QUOTE)

# =============================================================================================
# 6. Recette du câblage et validation du réseau
# =============================================================================================

T_OK = "Conforme"
T_WIRING = "Défaut de câblage (continuité ou paires)"
T_LENGTH = "Lien trop long"
T_PERF = "Performances insuffisantes (certification échouée)"
TEST_VERDICTS = (T_OK, T_WIRING, T_LENGTH, T_PERF)


@dataclass(frozen=True)
class LinkTest:
    label: str
    wiremap_ok: bool  # continuité et appairage des 8 fils
    length_m: float
    certification: str  # « PASS » ou « FAIL » (certificateur, classe visée)


def link_verdict(test: LinkTest) -> str:
    """On lit le rapport dans l'ordre : câblage, longueur, puis performances."""
    if not test.wiremap_ok:
        return T_WIRING
    if test.length_m > PERMANENT_LINK_MAX_M:
        return T_LENGTH
    if test.certification == "FAIL":
        return T_PERF
    if test.certification != "PASS":
        raise ValueError(test.certification)
    return T_OK


D_PHYS = "Lien physique : cordon, prise, brassage ou port"
D_IP = "Adressage : pas d'adresse valide (DHCP)"
D_GW = "Passerelle : box ou son raccordement"
D_PEER = "Poste distant : éteint, pare-feu ou autre réseau"
D_NET = "Accès Internet : opérateur ou résolution des noms"
D_SHARE = "Partage : chemin, droits ou compte"
D_OK = "Réseau validé"
DIAGNOSES = (D_PHYS, D_IP, D_GW, D_PEER, D_NET, D_SHARE)

# (contrôle, ce qu'on regarde, diagnostic si le contrôle échoue), dans l'ordre de la validation
VALIDATION_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("lien", "Voyant de la carte et du port du switch allumés", D_PHYS),
    ("adresse", "ipconfig : adresse du réseau de la box, masque, passerelle, DNS", D_IP),
    ("passerelle", "ping de la box (passerelle)", D_GW),
    ("poste", "ping d'un autre poste du réseau", D_PEER),
    ("internet", "Ouverture d'un site par son nom", D_NET),
    ("partage", "Ouverture du dossier partagé \\\\SERVEUR\\Dossiers", D_SHARE),
)
CHECK_KEYS = tuple(k for k, _w, _d in VALIDATION_CHECKS)


def validation_diagnosis(results: dict[str, bool]) -> str:
    """Le premier contrôle qui échoue désigne la piste ; les suivants ne prouvent rien tant
    qu'il n'est pas réglé."""
    for key, _what, diagnosis in VALIDATION_CHECKS:
        if not results[key]:
            return diagnosis
    return D_OK


def first_failure(failed: str) -> dict[str, bool]:
    """Résultats où tout réussit jusqu'au contrôle `failed`, qui échoue (les suivants aussi)."""
    index = CHECK_KEYS.index(failed)
    return {k: i < index for i, k in enumerate(CHECK_KEYS)}


# =============================================================================================
# 7. Implantation des équipements et procédures
# =============================================================================================

PLACEMENT: tuple[tuple[str, str, str], ...] = (
    ("Baie (panneau + switch)", "Local fermé à clé, ventilé, sec, au centre de l'étoile",
     f"tous les liens ≤ {PERMANENT_LINK_MAX_M} m ; accès réservé ; prise électrique dédiée"),
    ("Box ou routeur", "À l'arrivée de la ligne de l'opérateur, de préférence dans la baie",
     "relié au switch par un cordon ; seul lien vers Internet"),
    ("Point d'accès Wi-Fi", "En hauteur, au centre de la zone à couvrir, loin des masses métalliques",
     "alimenté par le câble (PoE) ; un câble jusqu'au switch"),
    ("Prises murales", "Près de chaque poste, deux prises par poste ; une par imprimante, écran, caméra",
     "repérées comme le port du panneau ; boîtier fixé"),
    ("Chemins de câbles", "Couloirs, faux plafond, goulottes ; à distance des câbles d'énergie",
     "croisement du courant fort à angle droit ; pas de câble au sol dans un passage"),
)

INSTALL_STEPS: tuple[tuple[str, str], ...] = (
    ("Analyser le besoin", "Postes, imprimantes, Wi-Fi, PoE, débit, plan des locaux, évolution."),
    ("Concevoir", "Étoile, emplacement de la baie, prises, supports, longueurs ≤ 90 m."),
    ("Chiffrer", "Nomenclature, devis HT, TVA, TTC ; accord du client."),
    ("Poser", "Chemins, séparation du courant fort, rayons, repères aux deux bouts."),
    ("Raccorder", "Keystones et panneau poinçonnés selon une seule norme ; baie équipée."),
    ("Tester", "Chaque lien au testeur : câblage, longueur, certification ; corriger."),
    ("Configurer et valider", "Box, switch, postes ; lien, IP, passerelle, PC-PC, Internet, partage."),
    ("Documenter et réceptionner", "Plan, tableau de brassage, rapports de test, PV signé."),
)

TEST_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Plan de brassage, liste des repères, testeur chargé et référencé."),
    ("Brancher", "Unité principale au panneau, unité distante à la prise, mêmes repères."),
    ("Lire le câblage", "Continuité des 8 fils, paires, inversions, coupures, courts-circuits."),
    ("Lire la longueur", f"Lien permanent ≤ {PERMANENT_LINK_MAX_M} m."),
    ("Certifier", "Mesures de la catégorie visée : PASS ou FAIL, rapport enregistré."),
    ("Corriger et consigner", "Refaire le raccordement fautif, retester, archiver le rapport."),
)

CHECK_STEPS: tuple[tuple[str, str], ...] = tuple(
    (key.capitalize() if key != "poste" else "Autre poste", what) for key, what, _d in VALIDATION_CHECKS
) + (("Consigner", "Résultats dans le dossier de recette, signés avec le client."),)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Installer un mini-réseau, de l'étude à la réception", INSTALL_STEPS),
    ("Tester et certifier le câblage", TEST_STEPS),
    ("Valider le réseau dans l'ordre", CHECK_STEPS),
)

# =============================================================================================
# 8. Schémas SVG
# =============================================================================================

_SCALE = 15  # px par mètre
_PLAN_X, _PLAN_Y = 10, 28


def _px(x_m: float, y_m: float) -> tuple[float, float]:
    return _PLAN_X + x_m * _SCALE, _PLAN_Y + y_m * _SCALE


def _marker(x: float, y: float, text: str) -> str:
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#ffffff" stroke="{_BAD}" stroke-width="2"/>'
            f'<text x="{x:.1f}" y="{y + 4:.1f}" font-size="11" font-weight="700" text-anchor="middle">{escape(text)}</text>')


def floor_plan_svg(plan: FloorPlan, *, markers: tuple[tuple[str, float, float], ...] = (),
                   show_equipment: bool = True) -> str:
    """Plan à l'échelle (15 px par mètre) : pièces, baie (B), box (R), prises (numéros) et point
    d'accès (AP). `markers` : emplacements numérotés à compléter (schéma d'exercice)."""
    width = int(plan.width_m * _SCALE) + 2 * _PLAN_X
    height_plan = int(plan.depth_m * _SCALE)
    parts = [_text_lines(width // 2, 16, [plan.name.split(",")[0]], size=11.5, weight="700", anchor="middle")]
    for room in plan.rooms:
        x, y = _px(room.x, room.y)
        parts.append(f'<rect data-room="{escape(room.name)}" x="{x:.1f}" y="{y:.1f}" width="{room.w * _SCALE:.1f}" '
                     f'height="{room.h * _SCALE:.1f}" fill="{_ROOM}" stroke="{_STROKE}" stroke-width="1.5"/>')
        cx = x + room.w * _SCALE / 2
        lines = [room.short] if room.short else _wrap(room.name, max(6, int(room.w * 1.7)))
        parts.append(_text_lines(int(cx), int(y + 13 if room.short else y + room.h * _SCALE / 2 + 4), lines, size=10, anchor="middle", step=12))
    if show_equipment:
        rx, ry = _px(plan.rack.x, plan.rack.y)
        parts.append(f'<rect data-point="BAIE" x="{rx - 9:.1f}" y="{ry - 9:.1f}" width="18" height="18" fill="{_STROKE}"/>'
                     f'<text x="{rx:.1f}" y="{ry + 4:.1f}" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">B</text>')
        bx, by = _px(plan.box.x, plan.box.y)
        parts.append(f'<path data-point="BOX" d="M{bx:.1f} {by - 8:.1f} L{bx + 8:.1f} {by + 6:.1f} L{bx - 8:.1f} {by + 6:.1f} Z" '
                     f'fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
                     f'<text x="{bx:.1f}" y="{by + 4:.1f}" font-size="8" font-weight="700" text-anchor="middle">R</text>')
        for outlet in plan.outlets:
            ox, oy = _px(outlet.x, outlet.y)
            if outlet.poe_class is not None:
                parts.append(f'<circle data-point="{outlet.key}" data-poe="{outlet.poe_class}" cx="{ox:.1f}" cy="{oy:.1f}" r="8" '
                             f'fill="#fff3c4" stroke="{_STROKE}" stroke-width="1.5"/>'
                             f'<text x="{ox:.1f}" y="{oy + 3:.1f}" font-size="7.5" font-weight="700" text-anchor="middle">AP</text>')
            else:
                parts.append(f'<rect data-point="{outlet.key}" x="{ox - 3.5:.1f}" y="{oy - 3.5:.1f}" width="7" height="7" '
                             f'fill="{_FILL}" stroke="{_STROKE}"/>')
                number = int(outlet.key[1:])
                dy = -6 if outlet.y > plan.depth_m / 2 else 13
                parts.append(f'<text x="{ox:.1f}" y="{oy + dy:.1f}" font-size="8.5" text-anchor="middle">{number}</text>')
    for text, xm, ym in markers:
        mx, my = _px(xm, ym)
        parts.append(f'<g data-marker="{escape(text)}">{_marker(mx, my, text)}</g>')
    y = _PLAN_Y + height_plan + 18
    legend = [f"Échelle : le trait ci-dessus mesure 1 m ; plan de {fr(plan.width_m, 0)} m × {fr(plan.depth_m, 0)} m."]
    legend += ["; ".join(f"{r.short} : {r.name.lower()}" for r in plan.rooms if r.short) + "."]
    if show_equipment:
        legend += [("B : baie ; R : box de l'opérateur ; carrés numérotés : prises RJ45 (repère P01…) ; "
                    "AP : point d'accès Wi-Fi au plafond, alimenté par PoE.")]
    if markers:
        legend += ["Cercles numérotés : emplacements à compléter."]
    wrapped = [line for text in legend for line in _wrap(text, 62)]
    parts.append(f'<path d="M{_PLAN_X} {y - 8} h{_SCALE}" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_text_lines(_PLAN_X + _SCALE + 6, y - 4, ["1 m"], size=10))
    parts.append(_text_lines(_PLAN_X, y + 12, wrapped, size=10.5, step=13))
    return _svg(width, y + 12 + 13 * len(wrapped), parts)


def _node(x: float, y: float, w: float, lines: list[str], *, key: str = "", dashed: bool = False) -> str:
    h = 14 + 13 * len(lines)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    data = f' data-node="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{_FILL}" '
            f'stroke="{_STROKE}" stroke-width="1.5"{dash}/>'
            + _text_lines(int(x), int(y + 15), lines, size=10.5, weight="700", anchor="middle", step=13))


STAR_LEAVES: tuple[tuple[str, str], ...] = (
    ("postes", "8 postes"),
    ("imprimante", "Imprimante (P03)"),
    ("ecran", "Écran (P08)"),
    ("ap", "Point d'accès Wi-Fi (P13)"),
)


def star_svg(*, blanks: dict[str, str] | None = None, remote: bool = False) -> str:
    """Topologie logique en étoile : Internet → box → switch (centre) → chaque prise par son
    propre câble. `blanks` remplace le libellé d'un nœud par un numéro à compléter ; `remote`
    ajoute un second bâtiment relié par une liaison à compléter."""
    blanks = blanks or {}
    width = 380
    parts: list[str] = []

    def label(key: str, text: str, chars: int = 13) -> list[str]:
        return [f"{blanks[key]} ?"] if key in blanks else _wrap(text, chars)

    parts.append(_node(190, 6, 170, label("internet", "Internet (opérateur)", 24), key="" if "internet" in blanks else "internet", dashed=True))
    parts.append(f'<path d="M190 33 V52" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_node(190, 52, 160, label("box", "Box / routeur", 22), key="" if "box" in blanks else "box"))
    parts.append(f'<path d="M190 79 V100" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_node(190, 100, 200, label("switch", "Switch (centre de l'étoile)", 30), key="" if "switch" in blanks else "switch"))
    leaf_y = 196
    xs = (48, 140, 232, 324)
    for x, (key, text) in zip(xs, STAR_LEAVES, strict=True):
        parts.append(f'<path data-link="{"" if key in blanks else key}" d="M190 127 L{x} {leaf_y}" stroke="{_STROKE}" stroke-width="1.6"/>')
        parts.append(_node(x, leaf_y, 86, label(key, text), key="" if key in blanks else key))
    y = leaf_y + 66
    if remote:
        parts.append(f'<path data-link="{"" if "liaison" in blanks else "liaison"}" d="M290 114 H374 V{y + 24} H370" fill="none" stroke="{_BAD}" stroke-width="2.4" stroke-dasharray="7 4"/>')
        parts.append(_text_lines(368, 160, [blanks.get("liaison", "fibre")], size=11, weight="700", anchor="end"))
        parts.append(_node(296, y + 10, 140, label("switch2", "Switch du bâtiment B", 20), key="switch2"))
        y += 52
    notes = _wrap("Chaque prise a son propre câble jusqu'au panneau, brassé sur un port du switch : "
                  "un câble coupé n'arrête qu'un poste.", 62)
    parts.append(_text_lines(10, y + 10, notes, size=10.5, step=13))
    return _svg(width, y + 10 + 13 * len(notes), parts)


def rack_svg(items: tuple[RackItem, ...], total_u: int, *, blanks: dict[int, str] | None = None,
             title: str = "") -> str:
    """Face avant d'une baie, unité par unité (U1 en bas). `items` sont posés du haut vers le
    bas ; `blanks` (index de l'élément → numéro) remplace un libellé par un emplacement à
    compléter."""
    blanks = blanks or {}
    if rack_units(items) > total_u:
        raise ValueError("Les équipements dépassent la hauteur de la baie.")
    width, u_h, top, left, rack_w = 380, 24, 30, 46, 300
    parts = [_text_lines(width // 2, 18, [title or f"Baie {total_u} U, face avant"], size=12, weight="700", anchor="middle")]
    parts.append(f'<rect x="{left - 6}" y="{top - 6}" width="{rack_w + 12}" height="{total_u * u_h + 12}" rx="4" '
                 f'fill="#e9ebef" stroke="{_STROKE}" stroke-width="2"/>')
    for u in range(total_u):
        y = top + u * u_h
        parts.append(_text_lines(left - 12, y + 16, [f"U{total_u - u}"], size=9.5, anchor="end"))
    u_index = 0
    for index, item in enumerate(items):
        y = top + u_index * u_h
        text = f"{blanks[index]} ?" if index in blanks else item.name
        fill = "#ffffff" if index in blanks else _FILL
        dash = ' stroke-dasharray="5 3"' if index in blanks else ""
        name = "" if index in blanks else escape(item.name)  # un schéma à compléter ne cache pas sa réponse
        parts.append(f'<rect data-item="{name}" data-u="{item.units}" x="{left}" y="{y + 1}" width="{rack_w}" '
                     f'height="{item.units * u_h - 2}" rx="3" fill="{fill}" stroke="{_STROKE}" stroke-width="1.4"{dash}/>')
        parts.append(_text_lines(left + rack_w // 2, int(y + item.units * u_h / 2 + 4), [f"{text} ({item.units} U)"],
                                 size=11, weight="700", anchor="middle"))
        u_index += item.units
    free = total_u - u_index
    y = top + total_u * u_h + 24
    lines = _wrap(f"Occupé : {rack_units(items)} U ; libre : {free} U (réserve). 1 U = {fr(U_MM, 2)} mm.", 62)
    parts.append(_text_lines(10, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def patching_svg(rows: tuple[tuple[str, str, int, str], ...], *, blanks: dict[int, str] | None = None,
                 limit: int = 8) -> str:
    """Plan de brassage : port du panneau → repère (identique à la prise) → port du switch.
    `blanks` (index de ligne → numéro) masque le repère et le port à compléter."""
    blanks = blanks or {}
    width, row_h, top = 380, 24, 44
    shown = rows[:limit]
    parts = [
        _text_lines(width // 2, 16, ["Plan de brassage — baie 1, panneau 1"], size=12, weight="700", anchor="middle"),
        _text_lines(14, 36, ["Port panneau"], size=10, weight="700"),
        _text_lines(104, 36, ["Repère (prise = panneau)"], size=10, weight="700"),
        _text_lines(268, 36, ["Port switch"], size=10, weight="700"),
    ]
    for index, (label, _dest, switch_port, key) in enumerate(shown):
        y = top + index * row_h
        panel_port = int(label.rsplit("-", 1)[1])
        hidden = index in blanks
        parts.append(f'<rect data-row="{panel_port}" data-label="{"" if hidden else label}" x="8" y="{y}" width="364" '
                     f'height="{row_h - 3}" rx="3" fill="{"#ffffff" if hidden else "#f4f6fb"}" stroke="{_STROKE}" stroke-width="1"/>')
        parts.append(_text_lines(40, y + 15, [f"{panel_port:02d}"], size=11, weight="700", anchor="middle"))
        parts.append(_text_lines(104, y + 15, [f"{blanks[index]} ?" if hidden else f"{label} ({key})"], size=11))
        parts.append(_text_lines(300, y + 15, ["?" if hidden else str(switch_port)], size=11, weight="700", anchor="middle"))
        parts.append(f'<path d="M232 {y + 10} H262" stroke="{_STROKE}" stroke-width="1.5"/>')
    y = top + len(shown) * row_h + 14
    notes = _wrap("Convention du cours : le port n du panneau est brassé sur le port n du switch ; "
                  "la prise porte le même repère que le port du panneau (baie, panneau, port).", 62)
    parts.append(_text_lines(10, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


CHAIN_BLANK_ITEMS: tuple[tuple[str, str], ...] = (
    ("switch", "Switch (port 7)"),
    ("cordon_brassage", "Cordon de brassage, 2 m"),
    ("panneau", "Panneau de brassage, port B1-P1-07"),
    ("permanent", "Câble monobrin Cat6A, 84 m"),
    ("prise", "Prise murale (keystone) B1-P1-07"),
    ("cordon_poste", "Cordon de poste, 5 m"),
    ("pc", "PC de la comptable"),
)
CHAIN_BLANKS: dict[str, str] = {"cordon_brassage": "①", "panneau": "②", "prise": "③", "cordon_poste": "④"}
CHAIN_PERMANENT_M, CHAIN_CORDS_M = 84, 7


def chain_blank_svg() -> str:
    """Chaîne d'un lien, du switch au PC, avec quatre éléments à nommer."""
    width, box_h, gap = 380, 30, 12
    parts: list[str] = []
    y = 8
    for index, (key, label) in enumerate(CHAIN_BLANK_ITEMS):
        hidden = key in CHAIN_BLANKS
        text = f"{CHAIN_BLANKS[key]} ? ({label.rsplit(', ', 1)[1]})" if hidden and ", " in label else (
            f"{CHAIN_BLANKS[key]} ?" if hidden else label)
        dash = ' stroke-dasharray="5 3"' if hidden else ""
        parts.append(f'<rect data-element="{"" if hidden else key}" x="70" y="{y}" width="250" height="{box_h}" rx="6" '
                     f'fill="{"#ffffff" if hidden else _FILL}" stroke="{_STROKE}" stroke-width="1.5"{dash}/>')
        parts.append(_text_lines(195, y + 19, [text], size=11, weight="700", anchor="middle"))
        y += box_h
        if index < len(CHAIN_BLANK_ITEMS) - 1:
            parts.append(f'<path d="M195 {y} V{y + gap}" stroke="{_STROKE}" stroke-width="2"/>')
            y += gap
    # accolades : lien permanent (panneau → prise) et canal (switch → PC)
    top_perm = 8 + 2 * (box_h + gap)
    bottom_perm = 8 + 4 * (box_h + gap) + box_h
    parts.append(f'<path d="M330 {top_perm} h10 V{bottom_perm} h-10" fill="none" stroke="{_BAD}" stroke-width="1.6"/>')
    parts.append(_text_lines(346, (top_perm + bottom_perm) // 2, ["⑤ ?"], size=11, weight="700"))
    parts.append(f'<path d="M62 8 h-10 V{y} h10" fill="none" stroke="{_BAD}" stroke-width="1.6"/>')
    parts.append(_text_lines(6, y // 2, ["canal"], size=10.5, weight="700"))
    notes = _wrap("⑤ : nom et longueur maximale de la partie fixe, du panneau à la prise.", 62)
    parts.append(_text_lines(10, y + 22, notes, size=10.5, step=13))
    return _svg(width, y + 22 + 13 * len(notes), parts)


def poe_svg(rows: tuple[tuple[str, int, int], ...], switches: tuple[tuple[str, float], ...]) -> str:
    """Puissance PoE réservée par type d'appareil (barres) comparée au budget des switchs."""
    width, left, bar_max = 380, 150, 210
    total = poe_budget_w(tuple(c for _n, c, q in rows for _ in range(q)))
    scale_max = max(total, *(b for _s, b in switches))
    parts = [_text_lines(width // 2, 16, ["Budget PoE : puissance réservée au switch"], size=12, weight="700", anchor="middle")]
    y = 30
    for name, cls, qty in rows:
        watts = poe_budget_w((cls,) * qty)
        parts.append(_text_lines(8, y + 14, [f"{qty} × {name}"], size=10.5, weight="700"))
        parts.append(_text_lines(8, y + 27, [f"classe {cls} : {qty} × {fr(POE_CLASS_W[cls])} W"], size=9.5))
        parts.append(f'<rect data-device="{escape(name)}" data-w="{fr(watts)}" x="{left}" y="{y + 4}" '
                     f'width="{bar_max * watts / scale_max:.1f}" height="18" fill="{_FILL}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(int(left + bar_max * watts / scale_max + 6), y + 18, [f"{fr(watts)} W"], size=10.5))
        y += 36
    parts.append(f'<rect data-total="{fr(total)}" x="{left}" y="{y + 4}" width="{bar_max * total / scale_max:.1f}" height="20" '
                 f'fill="#fff3c4" stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(8, y + 18, ["Total réservé"], size=10.5, weight="700"))
    parts.append(_text_lines(left + 6, y + 18, [f"{fr(total)} W"], size=10.5, weight="700"))
    y += 40
    for name, budget in switches:
        verdict = POE_OK if total <= budget else POE_KO
        mark = "✓" if verdict == POE_OK else "✗"
        parts.append(f'<g data-switch="{escape(name)}" data-budget="{fr(budget)}" data-verdict="{escape(verdict)}">'
                     + _text_lines(8, y, [f"{mark} {name} : budget {fr(budget, 0)} W → {verdict.lower()}"], size=10.5) + "</g>")
        y += 15
    notes = _wrap("Convention : on additionne la puissance réservée par classe (IEEE 802.3af/at/bt) ; "
                  "fiches des appareils et des switchs fictives.", 62)
    parts.append(_text_lines(8, y + 8, notes, size=10, step=13))
    return _svg(width, y + 8 + 13 * len(notes), parts)


PLAN_FIGURE = Figure(
    key="pr18-plan-locaux",
    title="Plan des locaux et implantation du réseau",
    alt=(
        f"Plan à l'échelle d'un cabinet de {fr(PLAN.width_m, 0)} m sur {fr(PLAN.depth_m, 0)} m : "
        + ", ".join(r.name for r in PLAN.rooms)
        + ". La baie (B) et la box de l'opérateur (R) sont dans le local technique, au centre. "
        + f"{len(PLAN.outlets) - 1} prises RJ45 numérotées : "
        + " ; ".join(f"{int(o.key[1:])} {o.label}" for o in PLAN.outlets if o.poe_class is None)
        + ". Un point d'accès Wi-Fi au plafond du plateau, alimenté en PoE (prise 13)."
    ),
    caption="Baie au centre : tous les liens restent courts ; deux prises par poste ; point d'accès au centre de la zone à couvrir.",
    svg=floor_plan_svg(PLAN),
)

STAR_FIGURE = Figure(
    key="pr18-etoile",
    title="Topologie en étoile du cabinet",
    alt=(
        "Internet arrive sur la box de l'opérateur, reliée au switch, centre de l'étoile. Le switch "
        "est relié par un câble distinct à chaque prise : " + ", ".join(t for _k, t in STAR_LEAVES)
        + ". Un câble coupé n'arrête qu'un poste."
    ),
    caption="Topologie physique en étoile : un câble par prise, tous ramenés au switch.",
    svg=star_svg(),
)

RACK_FIGURE = Figure(
    key="pr18-baie",
    title=f"Équipement d'une baie murale {PLAN_RACK_U} U",
    alt=(
        f"Baie de {PLAN_RACK_U} unités, du haut vers le bas : "
        + ", ".join(f"{i.name} ({i.units} U)" for i in RACK_LAYOUT)
        + f". {RACK_USED_U} U occupées, {PLAN_RACK_U - RACK_USED_U} U libres en réserve."
    ),
    caption="Panneau, passe-câbles et switch côte à côte : cordons de brassage courts et rangés.",
    svg=rack_svg(RACK_LAYOUT, PLAN_RACK_U),
)

PATCH_FIGURE = Figure(
    key="pr18-plan-brassage",
    title="Plan de brassage : repère de la prise, port du panneau, port du switch",
    alt=(
        "Tableau des huit premiers ports : "
        + " ; ".join(f"port {int(lab.rsplit('-', 1)[1]):02d}, repère {lab} ({key}), port {sw} du switch"
                     for lab, _d, sw, key in PATCH_ROWS[:8])
        + ". Le port n du panneau est brassé sur le port n du switch."
    ),
    caption="Un même repère à la prise et au panneau : on retrouve un lien sans ouvrir les goulottes.",
    svg=patching_svg(PATCH_ROWS),
)

POE_FIGURE = Figure(
    key="pr18-budget-poe",
    title="Budget PoE d'un switch",
    alt=(
        "Puissance réservée : "
        + " ; ".join(f"{q} {n} de classe {c}, {fr(poe_budget_w((c,) * q))} W" for n, c, q in POE_EXAMPLE)
        + f". Total {fr(POE_EXAMPLE_TOTAL)} W. "
        + " ; ".join(f"{s} : budget {fr(b, 0)} W, {poe_verdict(POE_EXAMPLE_CLASSES, b).lower()}" for s, b in POE_EXAMPLE_SWITCHES)
        + "."
    ),
    caption="On compare la somme des puissances réservées au budget PoE total du switch, pas au nombre de ports.",
    svg=poe_svg(POE_EXAMPLE, POE_EXAMPLE_SWITCHES),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


INSTALL_FIGURE = _proc_figure("pr18-procedure-installation", 1, PROCEDURES[0][0], INSTALL_STEPS,
                              "Chaque étape produit un document : besoin, plan, devis, rapports de test, procès-verbal.")
TEST_FIGURE = _proc_figure("pr18-procedure-tests", 2, PROCEDURES[1][0], TEST_STEPS,
                           "Un lien n'est livré qu'avec son rapport de test.")
CHECK_FIGURE = _proc_figure("pr18-procedure-validation", 3, PROCEDURES[2][0], CHECK_STEPS,
                            "Du plus simple au plus large : le premier contrôle qui échoue désigne la piste.")

PR18_FIGURES: tuple[Figure, ...] = (
    PLAN_FIGURE,
    STAR_FIGURE,
    RACK_FIGURE,
    PATCH_FIGURE,
    POE_FIGURE,
    INSTALL_FIGURE,
    TEST_FIGURE,
    CHECK_FIGURE,
)

# =============================================================================================
# 9. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

# Emplacements à compléter sur le plan : (numéro, x, y, réponse attendue)
PLAN_BLANKS: tuple[tuple[str, float, float, str], ...] = (
    ("①", 11.5, 8.5, "Baie : panneau de brassage et switch (centre de l'étoile)"),
    ("②", 10.5, 9.6, "Box ou routeur de l'opérateur (arrivée de la ligne)"),
    ("③", 20.5, 9.5, "Point d'accès Wi-Fi au plafond, alimenté en PoE"),
    ("④", 2.2, 6.3, "Deux prises RJ45 pour le poste de l'accueil"),
    ("⑤", 7.5, 1.2, "Prise RJ45 de l'imprimante multifonction"),
)

PLAN_BLANK_FIGURE = Figure(
    key="pr18-plan-a-completer",
    title="Plan des locaux à compléter",
    alt=(
        f"Plan à l'échelle du cabinet de {fr(PLAN.width_m, 0)} m sur {fr(PLAN.depth_m, 0)} m, sans équipement : "
        + ", ".join(r.name for r in PLAN.rooms)
        + ". Cinq emplacements numérotés : ① au milieu du local technique, contre le mur ; ② dans le "
        "local technique, là où arrive la ligne de l'opérateur ; ③ au plafond, au centre du plateau ; "
        "④ contre le mur de l'accueil, près du bureau d'accueil ; ⑤ dans un angle de l'accueil, près "
        "de l'emplacement prévu pour l'imprimante."
    ),
    caption="Schéma à compléter : nommer l'équipement prévu à chaque emplacement numéroté.",
    svg=floor_plan_svg(PLAN, markers=tuple((n, x, y) for n, x, y, _a in PLAN_BLANKS), show_equipment=False),
)

RACK_BLANK_LAYOUT: tuple[RackItem, ...] = (
    RackItem("Panneau de brassage 24 ports", 1),
    RackItem("Passe-câbles (guide-cordons)", 1),
    RackItem("Switch 24 ports PoE", 1),
    RackItem("Passe-câbles (guide-cordons)", 1),
    RackItem("Panneau de brassage 24 ports", 1),
    RackItem("Étagère : box de l'opérateur", 2),
    RackItem("Bandeau de prises électriques", 1),
)
RACK_BLANK_TOTAL_U = 12
RACK_BLANKS: dict[int, str] = {0: "①", 2: "②", 3: "③", 6: "④"}

RACK_BLANK_FIGURE = Figure(
    key="pr18-baie-a-completer",
    title="Baie 12 U à compléter",
    alt=(
        "Baie de 12 unités, du haut vers le bas : ① emplacement vide de 1 U ; passe-câbles 1 U ; ② "
        "emplacement vide de 1 U ; ③ emplacement vide de 1 U ; panneau de brassage 24 ports 1 U ; "
        "étagère de la box 2 U ; ④ emplacement vide de 1 U. Il reste 4 U libres en bas. Équipements "
        "à placer : un panneau de brassage 24 ports, un switch 24 ports PoE, un passe-câbles, un "
        "bandeau de prises électriques."
    ),
    caption="Schéma à compléter : placer panneau, switch, passe-câbles et bandeau électrique.",
    svg=rack_svg(RACK_BLANK_LAYOUT, RACK_BLANK_TOTAL_U, blanks=RACK_BLANKS, title="Baie 12 U à compléter"),
)

CHAIN_BLANK_FIGURE = Figure(
    key="pr18-lien-a-completer",
    title="Chaîne d'un lien à compléter",
    alt=(
        "Du haut vers le bas : switch, port 7 ; ① élément de 2 m ; ② élément portant le repère B1-P1-07 "
        "dans la baie ; câble monobrin Cat6A de 84 m ; ③ élément au mur portant le repère B1-P1-07 ; "
        "④ élément de 5 m ; PC de la comptable. Une accolade ⑤ couvre la partie fixe, de ② à ③ ; une "
        "accolade « canal » couvre l'ensemble, du switch au PC."
    ),
    caption="Schéma à compléter : nommer les éléments ① à ④ et la partie fixe ⑤, avec sa longueur maximale.",
    svg=chain_blank_svg(),
)

STAR_BLANKS: dict[str, str] = {"box": "①", "switch": "②", "ap": "③", "liaison": "④ ?"}

STAR_BLANK_FIGURE = Figure(
    key="pr18-etoile-a-completer",
    title="Topologie en étoile à compléter",
    alt=(
        "Internet (opérateur) en haut, relié à ① ; ① relié à ② ; ② relié par un câble distinct à 8 postes, "
        "à l'imprimante, à l'écran de réunion et à ③, un appareil au plafond du plateau sans prise "
        "électrique. ② est aussi relié au switch du bâtiment B, à 140 m dans un autre bâtiment, par la "
        "liaison ④."
    ),
    caption="Schéma à compléter : nommer ①, ② et ③ et choisir le support de la liaison ④.",
    svg=star_svg(blanks=STAR_BLANKS, remote=True),
)

PATCH_BLANKS: dict[int, str] = {2: "①", 5: "②", 6: "③"}

PATCH_BLANK_FIGURE = Figure(
    key="pr18-brassage-a-completer",
    title="Plan de brassage à compléter",
    alt=(
        "Tableau des ports 01 à 08 du panneau 1 de la baie 1. "
        + " ; ".join(
            (f"port {i + 1:02d} : {PATCH_BLANKS[i]} repère et port du switch à compléter" if i in PATCH_BLANKS
             else f"port {i + 1:02d} : repère {lab} ({key}), port {sw} du switch")
            for i, (lab, _d, sw, key) in enumerate(PATCH_ROWS[:8])
        )
        + ". Le port n du panneau est brassé sur le port n du switch."
    ),
    caption="Schéma à compléter : écrire les repères et les ports du switch manquants.",
    svg=patching_svg(PATCH_ROWS, blanks=PATCH_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (PLAN_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr18-plan-a-completer.svg"),
    (RACK_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr18-baie-a-completer.svg"),
    (CHAIN_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr18-lien-a-completer.svg"),
    (STAR_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr18-etoile-a-completer.svg"),
    (PATCH_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr18-brassage-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle qu'EX01) : le SVG du cours,
    précédé d'un titre et d'une description accessibles (affiché dans une balise `<img>`)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

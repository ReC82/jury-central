"""PR17 « Fibre optique — choix, raccordement et diagnostic » — données de référence, calculs
et schémas SVG (ticket #218).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket218_ampcr_pratique_pr17.py` :

- géométrie de la fibre (cœur, gaine 125 µm, revêtement 250 µm), types OM/OS, couleurs
  habituelles des gaines et des connecteurs (`FIBRE_KINDS`, `fibre_family`) ;
- connecteurs LC/SC/ST et polissage UPC/APC (`CONNECTORS`, `POLISHES`) ;
- modules optiques SFP/SFP+ et compatibilité module ↔ fibre ↔ distance (`MODULES`,
  `module_verdict`), portées reprises de PR14 (`REACH_M`) ;
- polarité d'une liaison duplex (`polarity_ok`) ;
- pertes, puissance reçue et zones de réception (`rx_power_dbm`, `RxSpec`, `rx_status`),
  photométrie (`measured_loss_db`, `photometry_verdict`) ; affaiblissements, connecteurs et
  épissures repris de PR14 (`fibre_loss_db`, `CONNECTOR_PAIR_DB`, `SPLICE_DB`) ;
- réflectométrie (OTDR) : distance depuis le temps aller-retour (`otdr_distance_m`), nature
  d'un événement (`OtdrEvent`, `otdr_event_kind`), position d'une cassure (`break_position_m`) ;
- rayon de courbure minimal (`min_bend_radius_mm`) ;
- comparaison cuivre / coaxial / fibre (`COMPARISON`) ;
- trois procédures illustrées (`CLEAN_STEPS`, `INSTALL_STEPS`, `DIAG_STEPS`).

Valeurs de référence (normes et usages publics, recoupés ; la fiche du fabricant fait foi) :
- gaine optique 125 µm, revêtement primaire 250 µm, protection serrée 900 µm ; cœur 62,5 µm
  (OM1), 50 µm (OM2 à OM4), environ 9 µm en monomode (ISO/IEC 11801, IEC 60793) ;
- longueurs d'onde : 850 et 1 300 nm en multimode, 1 310 et 1 550 nm en monomode, toutes dans
  l'infrarouge, invisibles ;
- couleurs habituelles des gaines (TIA-598) : orange OM1/OM2, aqua OM3/OM4 (OM4 parfois
  violet en Europe), jaune monomode ; connecteurs : beige multimode ancien, aqua OM3/OM4, bleu
  monomode UPC, vert monomode APC — le **marquage imprimé** sur la gaine fait foi ;
- férule LC 1,25 mm, SC et ST 2,5 mm ; APC poli à 8° ;
- portées IEEE 802.3 (1000BASE-SX/LX, 10GBASE-SR/LR) : données de PR14 ;
- indice de groupe d'une fibre monomode courante ≈ 1,468 (réglage « IOR » du réflectomètre) ;
- rayon de courbure : repère d'installation courant de 10 × le diamètre du câble au repos et
  20 × pendant le tirage (**convention du cours**, la fiche du câble fait foi).

Les modules et appareils cités dans les exercices ont des fiches **fictives**, signalées comme
telles. Chaque schéma porte son information en texte (valeurs en toutes lettres) : la couleur
n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr14_figures import (
    CONNECTOR_PAIR_DB,
    MULTIMODE,
    REACH_M,
    SINGLEMODE,
    SPLICE_DB,
    attenuation_for,
    fibre_loss_db,
    fr,
)
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, _wrap, step_flow_svg

WRITTEN_AT = "octobre 2026"
_STROKE = "#33415c"
_BAD = "#b3261e"
_OK = "#1d6b34"
_FILL = "#dbe4f3"

# =============================================================================================
# 1. Géométrie, types de fibre et couleurs
# =============================================================================================

CLADDING_UM = 125
COATING_UM = 250
BUFFER_UM = 900


@dataclass(frozen=True)
class FibreKind:
    code: str
    mode: str  # MULTIMODE ou SINGLEMODE (PR14)
    core_um: float
    jacket: str  # couleur habituelle de la gaine (TIA-598)
    connector: str  # couleur habituelle du corps de connecteur
    wavelengths: tuple[int, ...]
    note: str


FIBRE_KINDS: tuple[FibreKind, ...] = (
    FibreKind("OM1", MULTIMODE, 62.5, "orange", "beige", (850, 1300), "ancienne, portée courte"),
    FibreKind("OM2", MULTIMODE, 50, "orange", "beige", (850, 1300), "ancienne, 1 Gb/s jusqu'à 550 m"),
    FibreKind("OM3", MULTIMODE, 50, "aqua (turquoise)", "aqua", (850, 1300), "optimisée laser, 10 Gb/s jusqu'à 300 m"),
    FibreKind("OM4", MULTIMODE, 50, "aqua, parfois violet", "aqua ou violet", (850, 1300),
              "optimisée laser, 10 Gb/s jusqu'à 400 m"),
    FibreKind("OS2", SINGLEMODE, 9, "jaune", "bleu (UPC) ou vert (APC)", (1310, 1550),
              "monomode, kilomètres (OS1 : version d'intérieur, plus atténuante)"),
)
FIBRE_KINDS_BY_CODE = {k.code: k for k in FIBRE_KINDS}

FAM_OLD_MM = "Multimode ancienne (OM1 ou OM2)"
FAM_LASER_MM = "Multimode optimisée laser (OM3 ou OM4)"
FAM_SM = "Monomode (OS1 ou OS2)"
FAMILIES = (FAM_OLD_MM, FAM_LASER_MM, FAM_SM)


def fibre_mode(code: str) -> str:
    """OM1…OM5 : multimode ; OS1/OS2 : monomode."""
    if code.startswith("OM"):
        return MULTIMODE
    if code in ("OS1", "OS2"):
        return SINGLEMODE
    raise ValueError(f"Fibre inconnue : {code}")


def fibre_family(code: str) -> str:
    if code in ("OM1", "OM2"):
        return FAM_OLD_MM
    if code in ("OM3", "OM4"):
        return FAM_LASER_MM
    if fibre_mode(code) == SINGLEMODE:
        return FAM_SM
    raise ValueError(f"Famille non traitée dans le cours : {code}")


# =============================================================================================
# 2. Connecteurs et polissage
# =============================================================================================

# (nom, diamètre de la férule en mm, verrouillage, usage courant)
CONNECTORS: tuple[tuple[str, float, str, str], ...] = (
    ("LC", 1.25, "loquet à clip (comme un RJ45)", "modules SFP/SFP+, tiroirs à haute densité ; en duplex, deux LC clipsés"),
    ("SC", 2.5, "carré, pousser-tirer", "tiroirs, boîtiers d'opérateur (souvent SC/APC vert)"),
    ("ST", 2.5, "baïonnette (quart de tour)", "anciennes installations multimode (complément)"),
)
CONNECTORS_BY_NAME = {name: (ferrule, lock, use) for name, ferrule, lock, use in CONNECTORS}

# (polissage, angle de la face en degrés, couleur habituelle en monomode, remarque)
POLISHES: tuple[tuple[str, int, str, str], ...] = (
    ("UPC", 0, "bleu", "face droite bombée ; la plus courante"),
    ("APC", 8, "vert", "face inclinée à 8° : très peu de lumière renvoyée ; vidéo, opérateurs, PON"),
)


def polish_compatible(a: str, b: str) -> bool:
    """Deux connecteurs ne se raccordent que s'ils ont le même polissage : un APC face à un
    UPC laisse un vide et un angle (forte perte) et peut abîmer les faces."""
    return a == b


# =============================================================================================
# 3. Modules optiques, compatibilité et polarité
# =============================================================================================


@dataclass(frozen=True)
class Module:
    name: str
    form: str  # SFP (1 Gb/s) ou SFP+ (10 Gb/s)
    rate: str
    wavelength_nm: int
    mode: str


MODULES: tuple[Module, ...] = (
    Module("1000BASE-SX", "SFP", "1 Gb/s", 850, MULTIMODE),
    Module("1000BASE-LX", "SFP", "1 Gb/s", 1310, SINGLEMODE),
    Module("10GBASE-SR", "SFP+", "10 Gb/s", 850, MULTIMODE),
    Module("10GBASE-LR", "SFP+", "10 Gb/s", 1310, SINGLEMODE),
)
MODULES_BY_NAME = {m.name: m for m in MODULES}

C_OK = "Compatible"
C_PAIR = "Modules différents aux deux extrémités"
C_FIBRE = "Module inadapté au type de fibre posé"
C_REACH = "Portée du module dépassée sur cette fibre"
COMPAT_VERDICTS = (C_OK, C_PAIR, C_FIBRE, C_REACH)


def module_errors(module_a: str, module_b: str, fibre: str, length_m: float) -> list[str]:
    """Toutes les raisons pour lesquelles une liaison n'est pas garantie : mêmes modules aux
    deux bouts, module prévu pour la fibre (multimode ou monomode), portée du module sur cette
    fibre (IEEE 802.3, données de PR14)."""
    errors: list[str] = []
    if module_a != module_b:
        errors.append(C_PAIR)
    for name in dict.fromkeys((module_a, module_b)):
        module = MODULES_BY_NAME[name]
        if module.mode != fibre_mode(fibre):
            if C_FIBRE not in errors:
                errors.append(C_FIBRE)
        elif (name, fibre) in REACH_M and length_m > REACH_M[(name, fibre)]:
            if C_REACH not in errors:
                errors.append(C_REACH)
        elif (name, fibre) not in REACH_M:
            raise ValueError(f"Portée de {name} sur {fibre} non tabulée dans le cours.")
    return errors


def module_verdict(module_a: str, module_b: str, fibre: str, length_m: float) -> str:
    """Premier défaut, dans l'ordre où on le cherche : paire de modules, type de fibre, portée."""
    errors = module_errors(module_a, module_b, fibre, length_m)
    return errors[0] if errors else C_OK


def polarity_ok(a_tx_to: str) -> bool:
    """Liaison duplex : la fibre qui part de l'émission (TX) de A doit arriver sur la réception
    (RX) de B ; l'autre fibre relie alors le TX de B au RX de A. `a_tx_to` : « RX » ou « TX »."""
    if a_tx_to not in ("RX", "TX"):
        raise ValueError(a_tx_to)
    return a_tx_to == "RX"


# =============================================================================================
# 4. Pertes, puissance reçue, photométrie
# =============================================================================================


def dbm_fr(value: float) -> str:
    """Niveau en dBm avec un vrai signe moins (−14,4) ; « + » explicite au-dessus de 0."""
    text = fr(value)
    return text.replace("-", "−") if value < 0 else (f"+{text}" if value > 0 else text)


def rx_power_dbm(tx_dbm: float, loss_db: float) -> float:
    """Puissance reçue = puissance émise − perte de la liaison (dBm − dB = dBm)."""
    return round(tx_dbm - loss_db, 2)


NO_LIGHT_DBM = -30.0  # en dessous, les modules affichent « LOS » (souvent −40 dBm)


@dataclass(frozen=True)
class RxSpec:
    """Plage de réception de la fiche d'un module (valeurs d'exemple : fiche fictive)."""

    sensitivity_dbm: float  # puissance minimale reçue
    overload_dbm: float  # puissance maximale reçue (au-delà : saturation)


RX_NONE = "Aucune lumière reçue"
RX_LOW = "Trop faible : sous la sensibilité"
RX_OK = "Dans la plage de la fiche"
RX_HIGH = "Trop forte : saturation du récepteur"
RX_STATUSES = (RX_NONE, RX_LOW, RX_OK, RX_HIGH)


def rx_status(rx_dbm: float | None, spec: RxSpec) -> str:
    if rx_dbm is None or rx_dbm <= NO_LIGHT_DBM:
        return RX_NONE
    if rx_dbm < spec.sensitivity_dbm:
        return RX_LOW
    if rx_dbm > spec.overload_dbm:
        return RX_HIGH
    return RX_OK


# Fiche d'exemple (fictive) d'un module 10GBASE-LR : émission −8,2 à +0,5 dBm.
LR_SPEC = RxSpec(sensitivity_dbm=-14.4, overload_dbm=0.5)
# Fiche d'exemple (fictive) d'un module 10GBASE-SR.
SR_SPEC = RxSpec(sensitivity_dbm=-9.9, overload_dbm=-1.0)


def measured_loss_db(reference_dbm: float, reading_dbm: float) -> float:
    """Photométrie : perte = puissance de référence (source + cordon de référence) − puissance
    lue au bout de la liaison."""
    return round(reference_dbm - reading_dbm, 2)


P_OK = "Conforme"
P_KO = "Non conforme : perte trop élevée"


def photometry_verdict(loss_db: float, max_db: float) -> str:
    return P_OK if loss_db <= max_db + 1e-9 else P_KO


def max_link_loss_db(length_m: float, fibre: str, wavelength_nm: int, connectors: int, splices: int) -> float:
    """Perte maximale admissible d'une liaison (valeurs de PR14), arrondie au centième."""
    return round(fibre_loss_db(length_m, attenuation_for(fibre, wavelength_nm), connectors, splices), 2)


# =============================================================================================
# 5. Réflectométrie (OTDR)
# =============================================================================================

LIGHT_SPEED_M_S = 299_792_458
GROUP_INDEX = 1.468


def otdr_distance_m(round_trip_s: float, group_index: float = GROUP_INDEX) -> float:
    """Distance d'un événement : la lumière fait l'aller-retour, à c / n dans le verre."""
    return LIGHT_SPEED_M_S * round_trip_s / (2 * group_index)


def break_position_m(event_m: float, launch_m: float) -> float:
    """Position d'un défaut **dans la liaison** : position lue moins la bobine amorce."""
    return event_m - launch_m


@dataclass(frozen=True)
class OtdrEvent:
    position_m: float
    reflective: bool  # pic de réflexion visible
    loss_1310: float  # perte de l'événement à 1 310 nm (dB)
    loss_1550: float  # perte de l'événement à 1 550 nm (dB)
    end: bool = False  # la trace retombe dans le bruit juste après
    label: str = ""


O_CONNECTOR = "Connecteur (pic de réflexion, petite perte)"
O_SPLICE = "Épissure par fusion (sans pic, petite perte)"
O_BEND = "Courbure trop serrée (sans pic, perte plus forte à 1 550 nm)"
O_END = "Fin de fibre ou cassure (puis plus que du bruit)"
OTDR_KINDS = (O_CONNECTOR, O_SPLICE, O_BEND, O_END)
BEND_GAP_DB = 0.2  # écart 1550 − 1310 au-delà duquel on suspecte une courbure


def otdr_event_kind(event: OtdrEvent) -> str:
    """Lecture d'un événement au niveau technicien : une courbure perd nettement plus à
    1 550 nm qu'à 1 310 nm ; une épissure perd pareil aux deux longueurs d'onde."""
    if event.end:
        return O_END
    if event.reflective:
        return O_CONNECTOR
    if event.loss_1550 - event.loss_1310 > BEND_GAP_DB:
        return O_BEND
    return O_SPLICE


@dataclass(frozen=True)
class OtdrTrace:
    name: str
    launch_m: float  # bobine amorce
    link_m: float  # longueur prévue de la liaison
    db_per_km: float
    events: tuple[OtdrEvent, ...]

    @property
    def end_m(self) -> float:
        return next(e.position_m for e in self.events if e.end)

    @property
    def broken(self) -> bool:
        """La trace s'arrête avant le bout prévu de la liaison."""
        return break_position_m(self.end_m, self.launch_m) < self.link_m - 1


OTDR_EXAMPLE = OtdrTrace(
    name="Tiroir A → tiroir B, OS2, 1 550 nm",
    launch_m=150,
    link_m=1230,
    db_per_km=attenuation_for("OS2", 1550),
    events=(
        OtdrEvent(150, True, 0.35, 0.35, label="Connecteur du tiroir A"),
        OtdrEvent(610, False, 0.06, 0.07, label="Épissure"),
        OtdrEvent(980, False, 0.12, 0.85, label="Courbure"),
        OtdrEvent(1380, True, 0.0, 0.0, end=True, label="Connecteur du tiroir B (fin)"),
    ),
)


def trace_points(trace: OtdrTrace, *, wavelength: int = 1550) -> list[tuple[float, float]]:
    """Niveau (dB, relatif) le long de la fibre : pente = affaiblissement linéique, marche à
    chaque événement ; un pic marque une réflexion."""
    level, last, points = 0.0, 0.0, [(0.0, 0.0)]
    for event in trace.events:
        level -= (event.position_m - last) / 1000 * trace.db_per_km
        points.append((event.position_m, round(level, 3)))
        if event.reflective:
            points.append((event.position_m, round(level + 1.5, 3)))
            points.append((event.position_m + 15, round(level, 3)))
        level -= event.loss_1550 if wavelength == 1550 else event.loss_1310
        last = event.position_m + (15 if event.reflective else 0)
        if event.end:
            points.append((last, round(level - 4, 3)))
            points.append((last + 120, round(level - 4.2, 3)))
            break
        points.append((last, round(level, 3)))
    return points


# =============================================================================================
# 6. Pose : rayon de courbure
# =============================================================================================

BEND_FACTOR_REST = 10
BEND_FACTOR_PULL = 20


def min_bend_radius_mm(diameter_mm: float, *, pulling: bool) -> float:
    """Convention du cours : 10 × le diamètre au repos, 20 × pendant le tirage (la fiche du
    câble fait foi ; les fibres « insensibles à la courbure » acceptent moins)."""
    return diameter_mm * (BEND_FACTOR_PULL if pulling else BEND_FACTOR_REST)


# =============================================================================================
# 7. Comparaison des supports
# =============================================================================================

COMPARISON: tuple[tuple[str, str, str, str], ...] = (
    ("Ce qui circule", "courant électrique sur 4 paires", "courant électrique (âme et tresse)", "lumière dans du verre"),
    ("Débits courants", "100 Mb/s à 10 Gb/s", "10 Mb/s (réseau historique) ; TV et vidéo", "1 à 100 Gb/s et plus"),
    ("Longueur d'un tronçon", "100 m (canal)", "185 m (10BASE2), 500 m (10BASE5)",
     "centaines de m (multimode) à des km (monomode), selon le module"),
    ("Parasites électromagnétiques", "sensible ; torsade et écran", "moins sensible (tresse)", "insensible"),
    ("Liaison entre deux bâtiments", "à éviter (terres différentes, foudre)", "à éviter", "isolation électrique totale"),
    ("Alimentation PoE", "oui", "non", "non"),
    ("Raccordement", "sertissage ou poinçonnage, outillage simple", "connecteur BNC ou F",
     "connecteurs propres, épissure ou pigtail, outillage coûteux"),
    ("Coût", "faible", "faible", "câble raisonnable ; modules, mesure et outillage plus chers"),
    ("Fragilité", "robuste", "robuste", "courbures, écrasement, connecteurs à nettoyer"),
)


# =============================================================================================
# 8. Procédures
# =============================================================================================

CLEAN_STEPS: tuple[tuple[str, str], ...] = (
    ("Couper la lumière", "Port désactivé ou module retiré ; vérifier au photomètre, jamais à l'œil."),
    ("Inspecter", "Sonde ou microscope d'inspection sur la fiche et sur la traversée."),
    ("Nettoyer à sec", "Nettoyeur à cliquet ou lingette non pelucheuse, un seul passage."),
    ("Réinspecter", "Encore sale : alcool isopropylique, puis à sec ; rayé : remplacer."),
    ("Raccorder", "Brancher aussitôt ; capuchon sur tout connecteur libre."),
    ("Mesurer", "Puissance reçue ou perte au photomètre ; consigner."),
)

INSTALL_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Parcours, longueur, type de fibre, connecteurs, modules, budget calculé."),
    ("Tirer", "Par l'élément de traction (aramide), sans dépasser tension ni rayon de courbure."),
    ("Ranger", "Love de réserve, attaches non serrées, étiquettes aux deux extrémités."),
    ("Raccorder", "Épisser les pigtails dans les cassettes du tiroir optique, protections posées."),
    ("Contrôler", "Nettoyer, inspecter, mesurer chaque fibre au photomètre (OTDR si demandé)."),
    ("Documenter", "Plan de brassage, polarité, mesures comparées au budget, rapport."),
)

DIAG_STEPS: tuple[tuple[str, str], ...] = (
    ("Relever", "État des ports, voyants, modules, puissances émise et reçue des deux côtés."),
    ("Modules", "Même norme aux deux bouts, adaptée à la fibre et à la distance, reconnue."),
    ("Polarité", "L'émission (TX) de chaque côté arrive sur la réception (RX) de l'autre."),
    ("Connecteurs", "Inspecter, nettoyer, réinspecter ; jarretières du bon type."),
    ("Mesurer", "Photomètre fibre par fibre ; réflectomètre pour localiser un défaut."),
    ("Réparer et consigner", "Corriger, remesurer, comparer au budget, consigner."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Inspecter, nettoyer, inspecter un connecteur", CLEAN_STEPS),
    ("Poser et contrôler une liaison optique", INSTALL_STEPS),
    ("Diagnostiquer une liaison optique sans lien", DIAG_STEPS),
)

# =============================================================================================
# 9. Schémas SVG
# =============================================================================================

_SECTION_KINDS = ("OM1", "OM3", "OS2")


def section_svg() -> str:
    """Coupes à l'échelle (cœur dans une gaine de 125 µm, revêtement de 250 µm) et trajet de
    la lumière : réflexions sur la gaine en multimode, trajet presque droit en monomode."""
    width = 380
    scale = 0.36  # px par µm : 250 µm → 90 px
    parts = [_text_lines(width // 2, 18, ["Coupe d'une fibre (à l'échelle)"], size=12.5, weight="700", anchor="middle")]
    for index, code in enumerate(_SECTION_KINDS):
        kind = FIBRE_KINDS_BY_CODE[code]
        cx, cy = 66 + index * 124, 82
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{COATING_UM / 2 * scale:.1f}" fill="#f1f1f1" stroke="{_STROKE}"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{CLADDING_UM / 2 * scale:.1f}" fill="#e9eef7" stroke="{_STROKE}"/>')
        parts.append(f'<circle data-fibre="{code}" data-core-um="{fr(kind.core_um)}" cx="{cx}" cy="{cy}" '
                     f'r="{kind.core_um / 2 * scale:.2f}" fill="#f2b84b" stroke="{_STROKE}" stroke-width="0.8"/>')
        label = [f"{code} : cœur {fr(kind.core_um)} µm", "gaine 125 µm"]
        parts.append(_text_lines(cx, 146, label, size=11, anchor="middle", step=14))
    parts.append(_text_lines(10, 190, ["Revêtement 250 µm (gris clair) autour de la gaine."], size=11))
    # Trajets de la lumière (schéma de principe, pas à l'échelle)
    y0 = 214
    for row, (title, mode) in enumerate((("Multimode : plusieurs trajets, réflexions sur la gaine", MULTIMODE),
                                         ("Monomode : un seul trajet, presque droit", SINGLEMODE))):
        y = y0 + row * 96
        core_h = 28 if mode == MULTIMODE else 8
        parts.append(_text_lines(10, y, [title], size=11.5, weight="700"))
        top = y + 12
        parts.append(f'<rect x="10" y="{top}" width="360" height="{core_h + 24}" fill="#e9eef7" stroke="{_STROKE}"/>')
        parts.append(f'<rect data-mode="{mode}" x="10" y="{top + 12}" width="360" height="{core_h}" fill="#f8d79a" stroke="{_STROKE}" stroke-width="0.8"/>')
        mid = top + 12 + core_h / 2
        if mode == MULTIMODE:
            pts, x, up = [f"10 {mid:.1f}"], 10, True
            while x < 360:
                x = min(x + 40, 370)
                pts.append(f"{x} {top + 13 if up else top + 12 + core_h - 1}")
                up = not up
            parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{_BAD}" stroke-width="1.6"/>')
        else:
            parts.append(f'<path d="M10 {mid:.1f} H370" stroke="{_BAD}" stroke-width="1.6"/>')
        parts.append(_text_lines(14, top + core_h + 40, ["gaine (indice plus faible) autour du cœur"], size=10.5))
    notes = _wrap("Le cœur a un indice de réfraction un peu plus élevé que la gaine : la lumière qui "
                  "touche la limite sous un angle rasant est entièrement renvoyée dans le cœur "
                  "(réflexion totale).", 60)
    parts.append(_text_lines(10, y0 + 190, notes, size=11, step=14))
    return _svg(width, y0 + 190 + 14 * len(notes), parts)


DUPLEX_CASES: tuple[tuple[str, str], ...] = (
    ("Correct : chaque TX arrive sur le RX d'en face", "RX"),
    ("Inversé : TX relié au TX, RX au RX — pas de lien", "TX"),
)


def duplex_svg() -> str:
    """Deux modules SFP+ reliés par une jarretière duplex : polarité correcte, puis inversée."""
    width = 380
    parts: list[str] = []
    y = 8
    for title, a_to in DUPLEX_CASES:
        ok = polarity_ok(a_to)
        parts.append(_text_lines(10, y + 14, [("✓ " if ok else "✗ ") + title], size=12, weight="700"))
        top = y + 24
        for x, side in ((10, "A"), (300, "B")):
            parts.append(f'<rect x="{x}" y="{top}" width="70" height="64" rx="6" fill="{_FILL}" stroke="{_STROKE}"/>')
            parts.append(_text_lines(x + 35, top + 14, [f"Module {side}"], size=11, weight="700", anchor="middle"))
        for label_x in (62, 318):
            parts.append(_text_lines(label_x, top + 34, ["TX"], size=11, weight="700", anchor="middle"))
            parts.append(_text_lines(label_x, top + 56, ["RX"], size=11, weight="700", anchor="middle"))
        y_tx, y_rx = top + 30, top + 52
        colour = _OK if ok else _BAD
        if ok:
            fibres = (("1", "A-TX", "B-RX", f"M80 {y_tx} C190 {y_tx} 190 {y_rx} 300 {y_rx}"),
                      ("2", "B-TX", "A-RX", f"M300 {y_tx} C190 {y_tx} 190 {y_rx} 80 {y_rx}"))
            legend = "Fibre 1 : TX de A → RX de B ; fibre 2 (pointillés) : TX de B → RX de A"
        else:
            fibres = (("1", "A-TX", "B-TX", f"M80 {y_tx} H300"), ("2", "A-RX", "B-RX", f"M80 {y_rx} H300"))
            legend = "Fibre 1 : TX de A ↔ TX de B ; fibre 2 (pointillés) : RX ↔ RX"
        for number, start, end, d in fibres:
            dash = ' stroke-dasharray="7 4"' if number == "2" else ""
            parts.append(f'<path data-fibre="{number}" data-from="{start}" data-to="{end}" d="{d}" '
                         f'fill="none" stroke="{colour}" stroke-width="2.4"{dash}/>')
        legend_lines = _wrap(legend, 62)
        parts.append(_text_lines(10, top + 80, legend_lines, size=10.5, step=13))
        y = top + 80 + 13 * len(legend_lines) + 6
    notes = _wrap("Correction d'une inversion : croiser les deux fibres à UNE seule extrémité "
                  "(ouvrir le clip duplex de la jarretière), puis vérifier la puissance reçue des deux côtés.", 60)
    parts.append(_text_lines(10, y + 8, notes, size=11, step=14))
    return _svg(width, y + 8 + 14 * len(notes), parts)


def connectors_svg() -> str:
    """Férules à l'échelle relative (LC 1,25 mm, SC et ST 2,5 mm) et faces UPC / APC."""
    width = 380
    parts = [_text_lines(width // 2, 18, ["Connecteurs : diamètre de la férule (échelle relative)"],
                         size=12.5, weight="700", anchor="middle")]
    y = 34
    for name, ferrule, lock, _use in CONNECTORS:
        r = ferrule * 10  # 1 mm = 10 px de rayon par mm de diamètre / 2 → échelle relative
        parts.append(f'<circle data-connector="{name}" data-ferrule-mm="{fr(ferrule, 2)}" cx="40" cy="{y + 18}" '
                     f'r="{r / 2 + 6:.1f}" fill="{_FILL}" stroke="{_STROKE}"/>')
        parts.append(f'<circle cx="40" cy="{y + 18}" r="{r / 2:.1f}" fill="#ffffff" stroke="{_STROKE}"/>')
        parts.append(f'<circle cx="40" cy="{y + 18}" r="1.4" fill="{_BAD}"/>')
        parts.append(_text_lines(84, y + 12, [f"{name} — férule {fr(ferrule, 2)} mm"], size=12, weight="700"))
        parts.append(_text_lines(84, y + 28, [f"verrouillage : {lock}"], size=11))
        y += 48
    parts.append(_text_lines(10, y + 10, ["Polissage de la face (vu de côté)"], size=12.5, weight="700"))
    y += 22
    for name, angle, colour, note in POLISHES:
        top, h = y, 34
        slope = math.tan(math.radians(angle)) * h
        parts.append(f'<path data-polish="{name}" data-angle="{angle}" d="M14 {top} H80 L{80 + slope:.1f} {top + h} '
                     f'H14 Z" fill="{_FILL}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(100, top + 13, [f"{name} : face à {angle}° — corps {colour} en monomode"], size=11.5, weight="700"))
        parts.append(_text_lines(100, top + 29, _wrap(note, 44)[:1], size=11))
        y += h + 16
    notes = _wrap("Un APC ne se raccorde jamais sur un UPC. LC et SC se relient par une jarretière "
                  "LC-SC, jamais par un adaptateur forcé.", 60)
    parts.append(_text_lines(10, y + 6, notes, size=11, step=14))
    return _svg(width, y + 6 + 14 * len(notes), parts)


# Chaîne de la liaison du schéma (et du cas résolu 1) : deux bâtiments, 800 m d'OS2.
CHAIN_LENGTH_M = 800
CHAIN_ELEMENTS: tuple[tuple[str, str, float], ...] = (
    ("module", "Module SFP+ 10GBASE-LR du switch A", 0.0),
    ("jarretiere", "Jarretière duplex LC-LC OS2 (vers le tiroir)", 0.0),
    ("connecteur", "Traversée du tiroir A : paire de connecteurs", CONNECTOR_PAIR_DB),
    ("epissure", "Pigtail épissé à la fibre du câble (cassette)", SPLICE_DB),
    ("fibre", f"Câble OS2, {CHAIN_LENGTH_M} m à 1 310 nm", CHAIN_LENGTH_M / 1000 * attenuation_for("OS2", 1310)),
    ("epissure", "Épissure du pigtail dans le tiroir B", SPLICE_DB),
    ("connecteur", "Traversée du tiroir B : paire de connecteurs", CONNECTOR_PAIR_DB),
    ("jarretiere", "Jarretière duplex LC-LC OS2 (vers le switch)", 0.0),
    ("module", "Module SFP+ 10GBASE-LR du switch B", 0.0),
)
CHAIN_TOTAL_DB = round(sum(db for _k, _l, db in CHAIN_ELEMENTS), 2)


def chain_svg() -> str:
    """Éléments d'une liaison entre deux tiroirs optiques, avec la perte de chacun."""
    width, box_h, gap = 380, 30, 10
    parts: list[str] = []
    y = 8
    fills = {"module": "#d9d9d9", "jarretiere": "#fff3c4", "connecteur": "#e3c9a8", "epissure": "#f6d6d6", "fibre": "#c9d6ee"}
    for index, (key, label, db) in enumerate(CHAIN_ELEMENTS):
        parts.append(f'<rect data-element="{key}" data-db="{fr(db, 2)}" x="10" y="{y}" width="360" height="{box_h}" rx="6" '
                     f'fill="{fills[key]}" stroke="{_STROKE}"/>')
        loss = "—" if db == 0 else f"{fr(db, 2)} dB"
        parts.append(_text_lines(18, y + 19, [label], size=11.5))
        parts.append(_text_lines(362, y + 19, [loss], size=11.5, weight="700", anchor="end"))
        y += box_h
        if index < len(CHAIN_ELEMENTS) - 1:
            parts.append(f'<path d="M190 {y} V{y + gap}" stroke="{_STROKE}" stroke-width="2"/>')
            y += gap
    lines = [f"Perte maximale calculée : {fr(CHAIN_TOTAL_DB, 2)} dB",
             "Jarretières : pertes comptées avec les connecteurs qu'elles relient (règle de PR14)."]
    parts.append(_text_lines(10, y + 20, lines[:1], size=12, weight="700"))
    parts.append(_text_lines(10, y + 38, _wrap(lines[1], 60), size=11, step=14))
    return _svg(width, y + 38 + 14 * len(_wrap(lines[1], 60)), parts)


def otdr_svg(trace: OtdrTrace) -> str:
    """Trace de réflectomètre (1 550 nm) : niveau en dB le long de la fibre, événements
    numérotés et décrits en texte sous la courbure."""
    width, height = 380, 210
    left, right, top, bottom = 40, 14, 22, 36
    plot_w, plot_h = width - left - right, height - top - bottom
    points = trace_points(trace)
    x_max = max(x for x, _ in points)
    y_max, y_min = 2.0, min(y for _x, y in points) - 0.5

    def sx(x: float) -> float:
        return left + plot_w * x / x_max

    def sy(y: float) -> float:
        return top + plot_h * (y_max - y) / (y_max - y_min)

    parts = [
        _text_lines(width // 2, 14, [f"Trace : {trace.name}"], size=12, weight="700", anchor="middle"),
        f'<path d="M{left} {top} V{top + plot_h} H{left + plot_w}" fill="none" stroke="{_STROKE}" stroke-width="1.2"/>',
        _text_lines(left + plot_w // 2, height - 6, ["Distance depuis le réflectomètre (m)"], size=11, anchor="middle"),
        f'<text x="12" y="{top + plot_h / 2:.0f}" font-size="11" text-anchor="middle" transform="rotate(-90 12 {top + plot_h / 2:.0f})">Niveau (dB)</text>',
    ]
    for tick in range(0, int(x_max) + 1, 500):
        parts.append(f'<path d="M{sx(tick):.1f} {top + plot_h} v4" stroke="{_STROKE}"/>')
        parts.append(_text_lines(int(sx(tick)), top + plot_h + 15, [str(tick)], size=10, anchor="middle"))
    path = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f} {sy(y):.1f}" for i, (x, y) in enumerate(points))
    parts.append(f'<path data-trace="1" d="{path}" fill="none" stroke="#1f5fbf" stroke-width="2"/>')
    parts.append(f'<rect x="{left}" y="{top}" width="{sx(trace.launch_m) - left:.1f}" height="{plot_h}" fill="#f4f4f4" opacity="0.6"/>')
    parts.append(_text_lines(int(sx(trace.launch_m / 2)), top + plot_h - 6, ["amorce"], size=10, anchor="middle"))
    for number, event in enumerate(trace.events, start=1):
        x = sx(event.position_m)
        parts.append(f'<g data-event="{escape(otdr_event_kind(event))}" data-m="{event.position_m:g}" '
                     f'data-loss="{fr(event.loss_1550, 2)}"><circle cx="{x:.1f}" cy="{top + 8}" r="8" fill="#ffffff" stroke="{_STROKE}"/>'
                     f'<text x="{x:.1f}" y="{top + 12}" font-size="10.5" font-weight="700" text-anchor="middle">{number}</text></g>')
    lines = []
    for number, event in enumerate(trace.events, start=1):
        kind = otdr_event_kind(event).split(" (")[0]
        detail = "" if event.end else f", perte {fr(event.loss_1550, 2)} dB à 1 550 nm"
        if kind.startswith("Courbure"):
            detail += f" ({fr(event.loss_1310, 2)} dB à 1 310 nm)"
        lines += _wrap(f"{number}. {event.position_m:g} m — {kind}{detail}", 62)
    lines += _wrap(f"Pente de la trace : {fr(trace.db_per_km, 1)} dB/km. Bobine amorce de {trace.launch_m:g} m : "
                   "la liaison commence au premier connecteur.", 62)
    parts.append(_text_lines(10, height + 8, lines, size=11, step=14))
    return _svg(width, height + 8 + 14 * len(lines), parts)


RX_SCALE_MIN, RX_SCALE_MAX = -40, 5
RX_EXAMPLES: tuple[tuple[str, float | None], ...] = (
    ("LOS", None),
    ("−17,0", -17.0),
    ("−5,2", -5.2),
    ("+1,4", 1.4),
)


def rx_svg(spec: RxSpec) -> str:
    """Échelle de puissance reçue (dBm) et zones de la fiche : aucune lumière, trop faible,
    correcte, saturation."""
    width, left, right = 380, 14, 14
    scale_w = width - left - right

    def sx(dbm: float) -> float:
        return left + scale_w * (dbm - RX_SCALE_MIN) / (RX_SCALE_MAX - RX_SCALE_MIN)

    parts = [_text_lines(width // 2, 18, ["Puissance reçue (dBm) et fiche du module"], size=12.5, weight="700", anchor="middle")]
    zones = (
        (RX_NONE, RX_SCALE_MIN, NO_LIGHT_DBM, "#eeeeee"),
        (RX_LOW, NO_LIGHT_DBM, spec.sensitivity_dbm, "#fbecec"),
        (RX_OK, spec.sensitivity_dbm, spec.overload_dbm, "#e9f5ec"),
        (RX_HIGH, spec.overload_dbm, RX_SCALE_MAX, "#fbe3c9"),
    )
    y = 34
    for name, lo, hi, fill in zones:
        parts.append(f'<rect data-zone="{escape(name)}" data-from="{fr(lo)}" data-to="{fr(hi)}" x="{sx(lo):.1f}" y="{y}" '
                     f'width="{sx(hi) - sx(lo):.1f}" height="26" fill="{fill}" stroke="{_STROKE}"/>')
    for dbm in (-40, -30, -20, -10, 0):
        parts.append(f'<path d="M{sx(dbm):.1f} {y + 26} v5" stroke="{_STROKE}"/>')
        parts.append(_text_lines(int(sx(dbm)), y + 43, [str(dbm).replace("-", "−")], size=10.5, anchor="middle"))
    for label, value in RX_EXAMPLES:
        x = sx(-40 if value is None else value)
        parts.append(f'<path data-rx="{label}" d="M{x:.1f} {y - 4} V{y + 30}" stroke="{_BAD}" stroke-width="2"/>')
    y += 62
    lines = [
        f"Aucune lumière : ≤ {dbm_fr(NO_LIGHT_DBM)} dBm (le module affiche LOS ou −40 dBm)",
        f"Trop faible : de {dbm_fr(NO_LIGHT_DBM)} à {dbm_fr(spec.sensitivity_dbm)} dBm (sensibilité)",
        f"Correcte : de {dbm_fr(spec.sensitivity_dbm)} à {dbm_fr(spec.overload_dbm)} dBm",
        f"Saturation : au-dessus de {dbm_fr(spec.overload_dbm)} dBm",
    ]
    lines += ["Exemples (traits) : " + " ; ".join(
        f"{label} dBm → {rx_status(value, spec).split(' :')[0].lower()}" if value is not None else "LOS → aucune lumière"
        for label, value in RX_EXAMPLES)]
    wrapped: list[str] = []
    for line in lines:
        wrapped += _wrap(line, 60)
    parts.append(_text_lines(10, y, wrapped, size=11, step=14))
    parts.append(_text_lines(10, y + 14 * len(wrapped) + 6, ["Fiche d'exemple fictive (10GBASE-LR)."], size=10.5))
    return _svg(width, y + 14 * len(wrapped) + 12, parts)


SECTION_FIGURE = Figure(
    key="pr17-coupe-fibre",
    title="Coupe d'une fibre et trajet de la lumière",
    alt=(
        "Trois coupes à l'échelle dans une gaine de 125 micromètres entourée d'un revêtement de "
        "250 micromètres : OM1 cœur de 62,5 micromètres, OM3 cœur de 50 micromètres, OS2 cœur "
        "d'environ 9 micromètres. Dessous, en multimode, la lumière suit plusieurs trajets en se "
        "réfléchissant sur la gaine ; en monomode, un seul trajet presque droit. Le cœur a un "
        "indice de réfraction un peu plus élevé que la gaine : réflexion totale."
    ),
    caption="Le cœur guide la lumière ; la gaine, d'indice plus faible, la renvoie vers le cœur.",
    svg=section_svg(),
)

DUPLEX_FIGURE = Figure(
    key="pr17-polarite-duplex",
    title="Liaison duplex : émission (TX) et réception (RX)",
    alt=(
        "En haut, liaison correcte : la fibre 1 part du TX du module A et arrive au RX du module "
        "B ; la fibre 2 part du TX de B et arrive au RX de A. En bas, liaison inversée : le TX de "
        "A arrive sur le TX de B et le TX de B sur le TX de A ; aucun récepteur ne reçoit de "
        "lumière, pas de lien. Correction : croiser les deux fibres à une seule extrémité."
    ),
    caption="Deux fibres par liaison : chacune va d'un émetteur vers le récepteur d'en face.",
    svg=duplex_svg(),
)

CONNECTORS_FIGURE = Figure(
    key="pr17-connecteurs",
    title="Connecteurs LC, SC, ST et polissage UPC ou APC",
    alt=(
        "Férules à l'échelle relative : LC 1,25 millimètre, verrouillage à clip ; SC 2,5 "
        "millimètres, carré pousser-tirer ; ST 2,5 millimètres, baïonnette. Polissage vu de "
        "côté : UPC face droite, corps bleu en monomode ; APC face inclinée à 8 degrés, corps "
        "vert. Un APC ne se raccorde jamais sur un UPC."
    ),
    caption="LC sur les modules SFP/SFP+ ; SC sur de nombreux tiroirs et boîtiers ; APC vert, UPC bleu.",
    svg=connectors_svg(),
)

CHAIN_FIGURE = Figure(
    key="pr17-chaine-liaison",
    title="Raccordement : de module à module, à travers deux tiroirs optiques",
    alt=(
        "De haut en bas : "
        + " ; ".join(f"{label}{'' if db == 0 else f', {fr(db, 2)} dB'}" for _k, label, db in CHAIN_ELEMENTS)
        + f". Perte maximale calculée : {fr(CHAIN_TOTAL_DB, 2)} décibels."
    ),
    caption="Pigtails épissés dans les tiroirs, jarretières de brassage vers les modules ; chaque élément compte dans le bilan.",
    svg=chain_svg(),
)

OTDR_FIGURE = Figure(
    key="pr17-trace-otdr",
    title="Lire une trace de réflectomètre (OTDR)",
    alt=(
        f"Courbe descendante, pente de {fr(OTDR_EXAMPLE.db_per_km, 1)} dB par kilomètre, après une bobine amorce "
        f"de {OTDR_EXAMPLE.launch_m:g} mètres. "
        + " ".join(
            f"Événement {n} à {e.position_m:g} m : {otdr_event_kind(e)}"
            + ("" if e.end else f", perte {fr(e.loss_1550, 2)} dB à 1 550 nm") + "."
            for n, e in enumerate(OTDR_EXAMPLE.events, start=1)
        )
        + " La courbure perd 0,12 dB à 1 310 nm seulement."
    ),
    caption="Pic = réflexion (connecteur, fin) ; marche sans pic = épissure ou courbure ; chute dans le bruit = fin ou cassure.",
    svg=otdr_svg(OTDR_EXAMPLE),
)

RX_FIGURE = Figure(
    key="pr17-puissance-recue",
    title="Puissance reçue et plage de la fiche du module",
    alt=(
        f"Échelle de −40 à +5 dBm. Aucune lumière jusqu'à {dbm_fr(NO_LIGHT_DBM)} dBm ; trop faible jusqu'à "
        f"{dbm_fr(LR_SPEC.sensitivity_dbm)} dBm, la sensibilité ; plage correcte de {dbm_fr(LR_SPEC.sensitivity_dbm)} à "
        f"{dbm_fr(LR_SPEC.overload_dbm)} dBm ; au-dessus, saturation. Exemples : LOS, aucune lumière ; −17 dBm, trop "
        "faible ; −5,2 dBm, correcte ; +1,4 dBm, saturation."
    ),
    caption="Puissance reçue = puissance émise − perte ; elle doit tomber dans la plage de la fiche (exemple fictif).",
    svg=rx_svg(LR_SPEC),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


CLEAN_FIGURE = _proc_figure("pr17-procedure-nettoyage", 1, PROCEDURES[0][0], CLEAN_STEPS,
                            "Toujours inspecter avant de brancher : un seul grain de poussière suffit à perdre le lien.")
INSTALL_FIGURE = _proc_figure("pr17-procedure-pose", 2, PROCEDURES[1][0], INSTALL_STEPS,
                              "La mesure finale se compare au budget calculé avant la pose.")
DIAG_FIGURE = _proc_figure("pr17-procedure-diagnostic", 3, PROCEDURES[2][0], DIAG_STEPS,
                           "Du relevé le plus simple à la mesure la plus longue.")

PR17_FIGURES: tuple[Figure, ...] = (
    SECTION_FIGURE,
    CONNECTORS_FIGURE,
    DUPLEX_FIGURE,
    RX_FIGURE,
    CHAIN_FIGURE,
    OTDR_FIGURE,
    CLEAN_FIGURE,
    INSTALL_FIGURE,
    DIAG_FIGURE,
)

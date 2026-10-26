"""Schémas du cours PR16 « Câble coaxial et BNC — impédance, fabrication et diagnostic écrit »
(ticket #198).

Règle du ticket : impédances, terminaisons, longueurs et lectures de tests sont **construites
depuis des données vérifiées** et contrôlées par `tests/test_ticket198_ampcr_pratique_pr16.py` ;
aucun schéma n'est tiré d'une image générée. Un bus coaxial est décrit par des données
(`Bus` : extrémités, stations, tronçons) ; le même objet sert à dessiner le schéma, à lister ses
non-conformités (`bus_errors`) et à calculer la lecture d'un ohmmètre (`ohmmeter_reading`) :
le schéma, le corrigé et le barème ne peuvent pas se contredire.

Valeurs de référence (IEEE 802.3, clauses 8 et 10, retirées des nouvelles installations en
2011 ; recoupées sur la documentation publiée) : 10BASE2 = coaxial fin 50 Ω (RG-58 A/U ou
C/U), segment de 185 m au plus, 30 stations au plus, 0,5 m au moins entre deux T,
T BNC branché directement sur la carte, terminateur 50 Ω à chaque extrémité, mise à la terre
en un seul point ; 10BASE5 = coaxial épais 50 Ω (≈ 10 mm), segment de 500 m, 100
transceivers au plus, prises tous les 2,5 m (repères sur la gaine), prise vampire,
transceiver et câble AUI, terminateurs 50 Ω sur connecteurs N.
Chaque schéma porte son information en texte (✓ / ✗, valeurs en toutes lettres) : la couleur
n'est qu'un repère, le schéma reste lisible imprimé en noir et blanc.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    step_flow_svg,
    two_lists_svg,
)

_STROKE = "#33415c"
_BAD = "#b3261e"
_OK = "#1d6b34"

# --- Données de référence -----------------------------------------------------------------

# Impédance caractéristique nominale des câbles cités dans le cours (marquage de la gaine).
CABLE_IMPEDANCE: dict[str, int] = {
    "RG-58": 50,
    "RG-8": 50,
    "RG-59": 75,
    "RG-6": 75,
    "RG-62": 93,
}

# (câble, impédance, diamètre extérieur approximatif, usage typique)
CABLE_TYPES: tuple[tuple[str, int, str, str], ...] = (
    ("RG-58 (A/U, C/U)", 50, "≈ 5 mm", "Ethernet fin 10BASE2, mesure, radio"),
    ("Coaxial épais (type RG-8)", 50, "≈ 10 mm", "Ethernet épais 10BASE5, radio"),
    ("RG-59", 75, "≈ 6 mm", "Vidéo analogique, vidéosurveillance, SDI sur courte distance"),
    ("RG-6", 75, "≈ 7 mm", "Télévision, satellite (fiches F)"),
    ("RG-62", 93, "≈ 6 mm", "Réseaux historiques ARCNET, terminaux IBM 3270"),
)

THIN_IMPEDANCE_OHM = 50
THIN_SEGMENT_MAX_M = 185
THIN_STATIONS_MAX = 30
THIN_MIN_SPACING_M = 0.5
THICK_SEGMENT_MAX_M = 500
THICK_TRANSCEIVERS_MAX = 100
THICK_TAP_SPACING_M = 2.5
AUI_MAX_M = 50
ETHERNET_COAX_RATE = "10 Mb/s"

# Vitesse de la lumière dans le vide, en mètres par nanoseconde.
LIGHT_M_PER_NS = 0.299792458


def fr(value: float, digits: int = 1) -> str:
    """Nombre au format français (virgule décimale, pas de « ,0 » inutile)."""
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def reflection_coefficient(load_ohm: float | None, line_ohm: float) -> float:
    """Coefficient de réflexion Γ = (Zc − Z0) / (Zc + Z0) ; `None` = extrémité ouverte (Γ = +1),
    0 Ω = court-circuit (Γ = −1), charge égale à la ligne = adaptation (Γ = 0)."""
    if load_ohm is None:
        return 1.0
    return (load_ohm - line_ohm) / (load_ohm + line_ohm)


def tdr_distance_m(round_trip_ns: float, velocity_factor: float) -> float:
    """Distance du défaut vue par un réflectomètre (TDR) : l'impulsion fait l'aller-retour,
    d = v × t / 2 avec v = facteur de vélocité × c."""
    return velocity_factor * LIGHT_M_PER_NS * round_trip_ns / 2


def parallel(*resistances: float) -> float:
    return 1 / sum(1 / r for r in resistances)


# --- Modèle d'un bus coaxial -----------------------------------------------------------------

FAULT_OPEN = "câble coupé"
FAULT_SHORT = "court-circuit âme/blindage"
FAULT_CRUSHED = "câble écrasé"
FAULT_BAD_CRIMP = "connecteur mal serti"

ATTACH_T = "T sur la carte"
ATTACH_STUB = "câble entre le T et la carte"


@dataclass(frozen=True)
class BusEnd:
    terminator_ohm: int | None  # None : extrémité libre, sans terminateur
    grounded: bool = False


@dataclass(frozen=True)
class Station:
    name: str
    attachment: str = ATTACH_T


@dataclass(frozen=True)
class Span:
    length_m: float
    cable: str = "RG-58"
    fault: str = ""


@dataclass(frozen=True)
class Bus:
    """Segment de bus : `items` alterne stations et tronçons, commence et finit par une
    station (le terminateur est vissé sur le T de la station d'extrémité)."""

    first: BusEnd
    items: tuple[Station | Span, ...]
    last: BusEnd

    @property
    def stations(self) -> tuple[Station, ...]:
        return tuple(i for i in self.items if isinstance(i, Station))

    @property
    def spans(self) -> tuple[Span, ...]:
        return tuple(i for i in self.items if isinstance(i, Span))

    @property
    def length_m(self) -> float:
        return sum(s.length_m for s in self.spans)


def bus_errors(bus: Bus) -> list[str]:
    """Non-conformités d'un segment 10BASE2, dans l'ordre de lecture du schéma."""
    errors: list[str] = []
    names = bus.stations
    for side, end in ((names[0].name, bus.first), (names[-1].name, bus.last)):
        if end.terminator_ohm is None:
            errors.append(f"Extrémité côté {side} sans terminateur : il faut un terminateur 50 Ω.")
        elif end.terminator_ohm != THIN_IMPEDANCE_OHM:
            errors.append(
                f"Terminateur de {end.terminator_ohm} Ω côté {side} : il faut 50 Ω."
            )
    if bus.first.grounded and bus.last.grounded:
        errors.append("Blindage mis à la terre aux deux extrémités : un seul point de terre.")
    for station in bus.stations:
        if station.attachment != ATTACH_T:
            errors.append(f"{station.name} : câble entre le T et la carte, le T doit être sur la carte.")
    for span in bus.spans:
        impedance = CABLE_IMPEDANCE.get(span.cable)
        if impedance != THIN_IMPEDANCE_OHM:
            errors.append(f"Tronçon en {span.cable} ({impedance} Ω) : il faut du RG-58 50 Ω.")
        if span.length_m < THIN_MIN_SPACING_M:
            errors.append(f"Tronçon de {fr(span.length_m)} m : 0,5 m au moins entre deux T.")
        if span.fault:
            errors.append(f"Tronçon de {fr(span.length_m)} m : {span.fault}.")
    if bus.length_m > THIN_SEGMENT_MAX_M:
        errors.append(f"Segment de {fr(bus.length_m)} m : 185 m au plus.")
    if len(bus.stations) > THIN_STATIONS_MAX:
        errors.append(f"{len(bus.stations)} stations : 30 au plus par segment.")
    return errors


def ohmmeter_reading(bus: Bus, station_index: int = 0) -> float | None:
    """Résistance lue entre âme et blindage au T d'une station, réseau arrêté (les cartes ne
    chargent pas le câble en continu ; résistance du câble négligée). `None` = infini (circuit
    ouvert). Un court-circuit donne 0 ; une coupure isole les terminateurs situés au-delà ; un
    câble écrasé ou un connecteur mal serti ne se voit généralement pas à l'ohmmètre."""
    positions = [i for i, item in enumerate(bus.items) if isinstance(item, Station)]
    here = positions[station_index]
    reachable: list[float] = []
    for direction, end in ((-1, bus.first), (1, bus.last)):
        index, blocked = here, False
        while 0 <= index + direction < len(bus.items):
            index += direction
            item = bus.items[index]
            if isinstance(item, Span) and item.fault == FAULT_SHORT:
                return 0.0
            if isinstance(item, Span) and item.fault == FAULT_OPEN:
                blocked = True
                break
        if not blocked and end.terminator_ohm:
            reachable.append(end.terminator_ohm)
    return parallel(*reachable) if reachable else None


def reading_text(value: float | None) -> str:
    return "infini (circuit ouvert, « OL »)" if value is None else f"{fr(value)} Ω"


# --- Dessins -------------------------------------------------------------------------------


def _verdict(parts: list[str], y: int, errors: list[str], *, ok_text: str) -> int:
    if not errors:
        parts.append(_text_lines(10, y, [f"✓ {ok_text}"], size=12, weight="700"))
        return y + 18
    parts.append(_text_lines(10, y, ["✗ Non-conformités :"], size=12, weight="700"))
    y += 17
    for error in errors:
        lines = _wrap(error, 54)
        parts.append(_text_lines(18, y, lines, size=11, step=14))
        y += 14 * len(lines) + 3
    return y


def bus_svg(bus: Bus, *, title: str, ok_text: str = "Segment conforme.") -> str:
    """Bus vertical (lisible sur téléphone) : extrémité, stations (T à gauche sur le bus, PC à
    droite), tronçons avec câble, longueur et défaut, autre extrémité, puis la liste des
    non-conformités calculée par `bus_errors`."""
    width, bus_x = 380, 92
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">{escape(title)}</text>'
    ]
    y = 32

    def end_box(end: BusEnd, where: str) -> None:
        nonlocal y
        if end.terminator_ohm is None:
            parts.append(
                f'<g data-end="{where}" data-terminator="aucun">'
                f'<circle cx="{bus_x}" cy="{y + 10}" r="9" fill="#ffffff" stroke="{_BAD}" stroke-width="2.5"/>'
                f'<path d="M{bus_x - 5} {y + 5} l10 10 M{bus_x + 5} {y + 5} l-10 10" stroke="{_BAD}" stroke-width="2.5"/></g>'
            )
            parts.append(_text_lines(bus_x + 18, y + 14, ["✗ extrémité libre, sans terminateur"], size=11.5, weight="700"))
        else:
            ok = end.terminator_ohm == THIN_IMPEDANCE_OHM
            parts.append(
                f'<rect data-end="{where}" data-terminator="{end.terminator_ohm}" x="{bus_x - 30}" y="{y}" width="60" height="22" rx="5" '
                f'fill="{"#e9f5ec" if ok else "#fbecec"}" stroke="{_OK if ok else _BAD}" stroke-width="2"/>'
            )
            parts.append(_text_lines(bus_x, y + 15, [f"{end.terminator_ohm} Ω"], size=12, weight="700", anchor="middle"))
            label = "terminateur" + (" ✓" if ok else " ✗ (50 Ω requis)")
            parts.append(_text_lines(bus_x + 38, y + 15, [label], size=11.5))
        if end.grounded:
            gx = 22
            parts.append(
                f'<path data-ground="{where}" d="M{bus_x - 30} {y + 11} H{gx} V{y + 20} M{gx - 9} {y + 20} H{gx + 9} '
                f'M{gx - 6} {y + 24} H{gx + 6} M{gx - 3} {y + 28} H{gx + 3}" fill="none" stroke="{_STROKE}" stroke-width="1.6"/>'
            )
            parts.append(_text_lines(gx - 12, y + 40, ["terre"], size=10))
        y += 22

    end_box(bus.first, "1")
    for item in bus.items:
        if isinstance(item, Span):
            h = 46
            impedance = CABLE_IMPEDANCE.get(item.cable)
            bad_cable = impedance != THIN_IMPEDANCE_OHM
            dash = ' stroke-dasharray="7 5"' if item.fault == FAULT_OPEN else ""
            parts.append(
                f'<path data-span="{escape(item.cable)}|{item.length_m:g}|{escape(item.fault)}" d="M{bus_x} {y} V{y + h}" '
                f'stroke="{_BAD if (bad_cable or item.fault) else _STROKE}" stroke-width="{6 if item.cable in ("RG-8",) else 4}"{dash}/>'
            )
            parts.append(_text_lines(bus_x - 12, y + 20, [item.cable, f"{fr(item.length_m)} m"], size=10.5, step=13, anchor="end"))
            notes = []
            if bad_cable:
                notes.append(f"✗ {impedance} Ω")
            if item.fault:
                notes.append(f"✗ {item.fault}")
            if notes:
                parts.append(_text_lines(bus_x + 14, y + 20, notes, size=11, weight="700", step=14))
            y += h
        else:
            stub = item.attachment != ATTACH_T
            parts.append(
                f'<rect data-station="{escape(item.name)}" data-attachment="{"stub" if stub else "T"}" x="{bus_x - 11}" y="{y}" '
                f'width="22" height="22" rx="3" fill="#ffffff" stroke="{_STROKE}" stroke-width="2"/>'
            )
            parts.append(_text_lines(bus_x, y + 16, ["T"], size=12, weight="700", anchor="middle"))
            pc_x = 250
            if stub:
                parts.append(
                    f'<path d="M{bus_x + 11} {y + 11} H{pc_x}" stroke="{_BAD}" stroke-width="3" stroke-dasharray="6 4"/>'
                )
                parts.append(_text_lines(bus_x + 18, y + 26, ["✗ câble T → carte"], size=10.5, weight="700"))
            else:
                parts.append(f'<path d="M{bus_x + 11} {y + 11} H{pc_x}" stroke="{_STROKE}" stroke-width="2"/>')
                parts.append(_text_lines(bus_x + 18, y + 7, ["T direct sur la carte"], size=9.5))
            parts.append(
                f'<rect x="{pc_x}" y="{y - 2}" width="120" height="26" rx="5" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
            )
            parts.append(_text_lines(pc_x + 60, y + 15, [item.name], size=11.5, weight="700", anchor="middle"))
            y += 22
    end_box(bus.last, "2")
    y += 40 if bus.last.grounded else 18
    stats = (
        f"{len(bus.stations)} stations · {fr(bus.length_m)} m de câble · "
        f"limites : 30 stations, 185 m"
    )
    parts.append(_text_lines(10, y, [stats], size=11))
    y = _verdict(parts, y + 20, bus_errors(bus), ok_text=ok_text)
    return _svg(width, y + 4, parts)


def coax_section_svg() -> str:
    """Coupe d'un coaxial (cercles concentriques) et vue de côté dénudée en gradins, avec les
    quatre couches repérées 1 à 4 dans les deux vues."""
    width, height = 380, 300
    cx, cy = 92, 110
    layers = (
        (74, "#4a4f57", "4"),  # gaine
        (62, "#9aa3ae", "3"),  # blindage (tresse + feuille)
        (55, "#f2f2ee", "2"),  # diélectrique
        (12, "#c77d2e", "1"),  # âme
    )
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">Câble coaxial : coupe et vue dénudée</text>'
    ]
    for radius, fill, number in layers:
        parts.append(
            f'<circle data-layer="{number}" cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
    # Tresse : hachures sur l'anneau du blindage.
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="58.5" fill="none" stroke="#ffffff" stroke-width="5" stroke-dasharray="3 3"/>'
    )
    # Pastilles numérotées posées sur chaque couche (lisibles en noir et blanc).
    badges = (("1", cx, cy), ("2", cx, cy + 33), ("3", cx - 41, cy - 41), ("4", cx + 48, cy + 48))
    for number, x, y in badges:
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="9" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<text x="{x}" y="{y + 4.5}" font-size="12" font-weight="700" text-anchor="middle">{number}</text>'
        )
    legend = (
        ("1", "Âme : conducteur central (cuivre)"),
        ("2", "Diélectrique : isolant qui fixe l'écart âme/blindage"),
        ("3", "Blindage : feuille et/ou tresse, retour du signal"),
        ("4", "Gaine : protection extérieure, marquage"),
    )
    ly = 44
    for number, text in legend:
        lines = _wrap(f"{number}. {text}", 26)
        parts.append(_text_lines(184, ly, lines, size=11.5, step=14))
        ly += 14 * len(lines) + 8
    # Vue de côté dénudée : gaine, blindage, diélectrique, âme (de gauche à droite).
    top = 222
    steps = ((10, 120, "#4a4f57", "4"), (130, 80, "#9aa3ae", "3"), (210, 70, "#f2f2ee", "2"), (280, 80, "#c77d2e", "1"))
    heights = {"4": 40, "3": 32, "2": 26, "1": 8}
    for x, w, fill, number in steps:
        h = heights[number]
        parts.append(
            f'<rect data-step="{number}" x="{x}" y="{top - h // 2}" width="{w}" height="{h}" fill="{fill}" stroke="{_STROKE}" stroke-width="1.2"/>'
        )
        parts.append(_text_lines(x + w // 2, top + 38, [number], size=12, weight="700", anchor="middle"))
    parts.append(
        _text_lines(10, top + 62, ["Vue de côté, câble préparé en gradins (non à l'échelle)"], size=10.5)
    )
    return _svg(width, height, parts)


BNC_PARTS: tuple[tuple[str, str], ...] = (
    ("Manchon (facultatif)", "Protège la sortie du câble ; enfilé en premier"),
    ("Bague à sertir (férule)", "Enfilée sur le câble ; serrera le blindage sur le corps"),
    ("Contact central (broche)", "Serti ou soudé sur l'âme ; mâle ou femelle"),
    ("Corps à baïonnette", "Isolant interne + écrou quart de tour sur les ergots de la prise"),
)


def bnc_parts_svg() -> str:
    """Connecteur BNC mâle à sertir, éclaté dans l'ordre de montage sur le câble."""
    width = 380
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">BNC mâle à sertir : pièces</text>'
    ]
    y = 34
    shapes = (
        f'<path d="M20 {{y}} h70 l14 8 v12 l-14 8 h-70 z" fill="#4a4f57" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="20" y="{{y}}" width="70" height="28" rx="3" fill="#d9dde3" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<path d="M20 {{y_mid}} h46 l18 -4 v8 l-18 -4" fill="#e1b94f" stroke="{_STROKE}" stroke-width="1.5"/>',
        (
            f'<rect x="20" y="{{y}}" width="84" height="28" rx="4" fill="#c9ced6" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<rect x="70" y="{{y_lug}}" width="10" height="6" fill="{_STROKE}"/>'
        ),
    )
    for i, ((name, detail), shape) in enumerate(zip(BNC_PARTS, shapes, strict=True), start=1):
        parts.append(f'<g data-part="{i}">' + shape.format(y=y, y_mid=y + 14, y_lug=y - 4) + "</g>")
        parts.append(_text_lines(118, y + 11, [f"{i}. {name}"], size=12, weight="700"))
        parts.append(_text_lines(118, y + 26, _wrap(detail, 34), size=10.5, step=13))
        y += 52
    parts.append(_text_lines(10, y + 4, ["Ordre de montage : 1 → 4. Formes simplifiées, non à l'échelle."], size=10.5))
    return _svg(width, y + 14, parts)


def strip_profile_svg() -> str:
    """Câble préparé pour une fiche à sertir : trois cotes A, B, C sans valeur (elles viennent
    de la notice du fabricant du connecteur)."""
    width, top = 380, 70
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">Préparation : cotes de la notice</text>',
        f'<rect x="10" y="{top - 20}" width="150" height="40" fill="#4a4f57" stroke="{_STROKE}"/>',
        f'<rect x="160" y="{top - 16}" width="70" height="32" fill="#9aa3ae" stroke="{_STROKE}"/>',
        f'<rect x="230" y="{top - 13}" width="60" height="26" fill="#f2f2ee" stroke="{_STROKE}"/>',
        f'<rect x="290" y="{top - 4}" width="70" height="8" fill="#c77d2e" stroke="{_STROKE}"/>',
    ]
    dims = (("A", 160, 360), ("B", 230, 360), ("C", 290, 360))
    for i, (name, x1, x2) in enumerate(dims):
        y = top + 34 + 20 * i
        parts.append(
            f'<path data-dim="{name}" d="M{x1} {y} H{x2} M{x1} {y - 5} V{y + 5} M{x2} {y - 5} V{y + 5}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x1 - 6, y + 4, [name], size=12, weight="700", anchor="end"))
    legend = (
        "A : longueur de gaine retirée",
        "B : blindage (tresse) laissé apparent",
        "C : âme nue, sans diélectrique",
        "A, B, C : lire la notice du connecteur choisi ;",
        "aucune cote n'est universelle.",
    )
    parts.append(_text_lines(10, top + 112, list(legend), size=11.5, step=16))
    return _svg(width, top + 112 + 16 * len(legend), parts)


def tdr_svg(*, title: str, event: str, round_trip_ns: float, velocity_factor: float,
            span_ns: float = 1000) -> str:
    """Trace de réflectomètre (TDR) fictive : impulsion émise à 0 ns, réflexion à `round_trip_ns`,
    vers le haut pour un circuit ouvert (Γ > 0), vers le bas pour un court-circuit (Γ < 0),
    aucune si le câble est adapté."""
    width, height = 380, 220
    left, right, mid = 34, 12, 100
    plot_w = width - left - right

    def sx(ns: float) -> float:
        return left + plot_w * ns / span_ns

    sign = {"ouvert": -1, "court-circuit": 1, "adapté": 0}[event]  # SVG : y vers le bas
    x = sx(round_trip_ns)
    d = f"M{left} {mid} L{left + 4} {mid - 50} L{left + 12} {mid - 50} L{left + 16} {mid}"
    if sign:
        d += f" L{x - 6:.1f} {mid} L{x:.1f} {mid + sign * 40} L{x + 10:.1f} {mid + sign * 40} L{x + 16:.1f} {mid}"
    d += f" L{left + plot_w} {mid}"
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">{escape(title)}</text>',
        f'<path d="M{left} 34 V170 H{left + plot_w}" fill="none" stroke="{_STROKE}" stroke-width="1.2"/>',
        f'<path d="M{left} {mid} H{left + plot_w}" stroke="#c9ced6" stroke-width="1" stroke-dasharray="4 4"/>',
        f'<path data-event="{event}" data-ns="{round_trip_ns:g}" d="{d}" fill="none" stroke="#1f5fbf" stroke-width="2.5"/>',
        _text_lines(left + 20, 48, ["impulsion émise"], size=10.5),
    ]
    for tick in range(0, int(span_ns) + 1, 200):
        parts.append(_text_lines(int(sx(tick)), 184, [str(tick)], size=10, anchor="middle"))
    parts.append(_text_lines(left + plot_w // 2, 198, ["temps aller-retour (ns)"], size=10.5, anchor="middle"))
    if sign:
        label_y = mid + sign * 40 + (16 if sign > 0 else -8)
        word = "réflexion positive" if event == "ouvert" else "réflexion négative"
        parts.append(_text_lines(int(min(x, width - 120)), label_y, [f"{word} à {round_trip_ns:g} ns"], size=10.5, weight="700"))
        distance = tdr_distance_m(round_trip_ns, velocity_factor)
        summary = f"{'Circuit ouvert' if event == 'ouvert' else 'Court-circuit'} à ≈ {fr(distance)} m (facteur de vélocité {fr(velocity_factor, 2)})"
    else:
        summary = "Pas de réflexion : câble adapté jusqu'au terminateur"
    parts.append(_text_lines(10, 214, [summary], size=11, weight="700"))
    return _svg(width, height + 4, parts)


def readings_svg(rows: tuple[tuple[str, float | None, str], ...]) -> str:
    """Tableau d'affichages d'ohmmètre : situation, valeur lue, conclusion."""
    width, row_h = 380, 46
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">Ohmmètre entre âme et blindage</text>'
    ]
    y = 30
    for situation, value, meaning in rows:
        parts.append(
            f'<rect data-reading="{"OL" if value is None else f"{value:g}"}" x="6" y="{y}" width="{width - 12}" height="{row_h - 6}" rx="6" '
            f'fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.2"/>'
        )
        parts.append(
            f'<rect x="14" y="{y + 7}" width="74" height="26" rx="3" fill="#111827"/>'
            f'<text x="51" y="{y + 25}" font-size="13" text-anchor="middle" fill="#e5e7eb" font-weight="700">'
            f'{"OL" if value is None else fr(value) + " Ω"}</text>'
        )
        parts.append(_text_lines(98, y + 16, _wrap(situation, 44)[:1], size=11, weight="700"))
        parts.append(_text_lines(98, y + 31, _wrap(meaning, 46)[:1], size=10.5))
        y += row_h
    parts.append(_text_lines(10, y + 8, ["Réseau arrêté ; résistance du câble négligée (« OL » = infini)."], size=10.5))
    return _svg(width, y + 16, parts)


def comparison_svg() -> str:
    """Trois liaisons coaxiales côte à côte (empilées) : 10BASE2, 10BASE5, vidéo 75 Ω."""
    width = 380
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">Trois liaisons coaxiales différentes</text>'
    ]
    y = 32
    # 10BASE2
    parts.append(f'<g data-panel="10BASE2"><rect x="4" y="{y}" width="{width - 8}" height="92" rx="8" fill="#f4f6fb" stroke="{_STROKE}"/>')
    parts.append(_text_lines(12, y + 18, ["10BASE2 — Ethernet fin, 50 Ω, bus"], size=12.5, weight="700"))
    by = y + 46
    parts.append(f'<path d="M30 {by} H350" stroke="{_STROKE}" stroke-width="4"/>')
    for x, label in ((22, "50 Ω"), (358, "50 Ω")):
        parts.append(f'<rect x="{x - 14}" y="{by - 9}" width="28" height="18" rx="3" fill="#e9f5ec" stroke="{_OK}"/>')
        parts.append(_text_lines(x, by + 26, [label], size=10, anchor="middle"))
    # T des stations d'extrémité accolés aux terminateurs (vissés sur la sortie libre du T).
    for x in (44, 190, 336):
        parts.append(f'<rect x="{x - 8}" y="{by - 8}" width="16" height="16" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.8"/>')
        parts.append(_text_lines(x, by + 4, ["T"], size=10, weight="700", anchor="middle"))
        parts.append(f'<path d="M{x} {by - 8} V{by - 16}" stroke="{_STROKE}" stroke-width="1.8"/>')
    parts.append(_text_lines(12, y + 84, ["RG-58 · BNC · T sur la carte · 185 m · 30 stations"], size=10.5))
    parts.append("</g>")
    y += 100
    # 10BASE5
    parts.append(f'<g data-panel="10BASE5"><rect x="4" y="{y}" width="{width - 8}" height="108" rx="8" fill="#f4f6fb" stroke="{_STROKE}"/>')
    parts.append(_text_lines(12, y + 18, ["10BASE5 — Ethernet épais, 50 Ω, bus"], size=12.5, weight="700"))
    by = y + 40
    parts.append(f'<path d="M30 {by} H350" stroke="{_STROKE}" stroke-width="8"/>')
    for x in (22, 358):
        parts.append(f'<rect x="{x - 14}" y="{by - 10}" width="28" height="20" rx="3" fill="#e9f5ec" stroke="{_OK}"/>')
    for x in (90, 160):
        parts.append(f'<rect x="{x - 16}" y="{by + 6}" width="32" height="16" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(f'<path d="M{x} {by + 22} V{by + 44}" stroke="{_STROKE}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    parts.append(_text_lines(190, by + 18, ["prise vampire + transceiver", "câble AUI ≤ 50 m → station"], size=10, step=14))
    parts.append(_text_lines(12, y + 100, ["≈ 10 mm · N · 500 m · 100 transceivers · 2,5 m"], size=10.5))
    parts.append("</g>")
    y += 116
    # Vidéo
    parts.append(f'<g data-panel="video-75"><rect x="4" y="{y}" width="{width - 8}" height="92" rx="8" fill="#f4f6fb" stroke="{_STROKE}"/>')
    parts.append(_text_lines(12, y + 18, ["Vidéo — 75 Ω, point à point"], size=12.5, weight="700"))
    by = y + 48
    parts.append(f'<rect x="14" y="{by - 13}" width="78" height="26" rx="4" fill="#ffffff" stroke="{_STROKE}"/>')
    parts.append(_text_lines(53, by + 4, ["Caméra"], size=11, anchor="middle"))
    parts.append(f'<path d="M92 {by} H270" stroke="{_STROKE}" stroke-width="4"/>')
    parts.append(f'<rect x="270" y="{by - 13}" width="96" height="26" rx="4" fill="#ffffff" stroke="{_STROKE}"/>')
    parts.append(_text_lines(318, by + 4, ["Enregistreur"], size=11, anchor="middle"))
    parts.append(_text_lines(181, by - 8, ["RG-59 75 Ω, BNC 75 Ω"], size=10, anchor="middle"))
    parts.append(_text_lines(12, y + 84, ["Pas de T ni de bus ; l'entrée du récepteur fait 75 Ω"], size=10.5))
    parts.append("</g>")
    y += 100
    return _svg(width, y, parts)


# --- Bus de référence et bus fautifs -------------------------------------------------------


def _stations_bus(names: tuple[str, ...], lengths: tuple[float, ...], *, first: BusEnd, last: BusEnd,
                  attachments: dict[str, str] | None = None, cables: dict[int, str] | None = None,
                  faults: dict[int, str] | None = None) -> Bus:
    items: list[Station | Span] = []
    for i, name in enumerate(names):
        items.append(Station(name, (attachments or {}).get(name, ATTACH_T)))
        if i < len(lengths):
            items.append(Span(lengths[i], (cables or {}).get(i, "RG-58"), (faults or {}).get(i, "")))
    return Bus(first=first, items=tuple(items), last=last)


GOOD_TERMINATOR = BusEnd(50)
GROUNDED_TERMINATOR = BusEnd(50, grounded=True)

ATELIER_NAMES = ("PC-1", "PC-2", "PC-3", "Serveur")
ATELIER_LENGTHS = (12, 8, 15)

BUS_OK = _stations_bus(ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR)
BUS_MISSING_TERMINATOR = _stations_bus(ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=BusEnd(None))
BUS_STUB_AND_GROUNDS = _stations_bus(
    ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=BusEnd(50, grounded=True),
    attachments={"PC-2": ATTACH_STUB},
)
BUS_WRONG_IMPEDANCE = _stations_bus(
    ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=BusEnd(75), cables={1: "RG-59"},
)
BUS_CUT = _stations_bus(ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR,
                        faults={1: FAULT_OPEN})

BUS_OK_FIGURE = Figure(
    key="pr16-bus-10base2-conforme",
    title="Bus 10BASE2 conforme : T sur chaque carte, deux terminateurs 50 Ω",
    alt=(
        "Bus vertical de haut en bas : terminateur 50 Ω relié à la terre, T du PC-1, 12 m de RG-58, "
        "T du PC-2, 8 m de RG-58, T du PC-3, 15 m de RG-58, T du Serveur, terminateur 50 Ω. Chaque T "
        "est branché directement sur la carte réseau. 4 stations, 35 m de câble. Segment conforme."
    ),
    caption=(
        "Bus 10BASE2 correct : un seul câble qui passe de T en T, un terminateur 50 Ω à chaque "
        "extrémité (vissé sur le T de la station d'extrémité), un seul point de terre."
    ),
    svg=bus_svg(BUS_OK, title="Bus 10BASE2 conforme"),
)

BUS_FAULT_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr16-bus-sans-terminateur",
        title="Schéma fautif 1 — terminateur absent",
        alt=(
            "Même bus que le schéma conforme, mais l'extrémité côté Serveur n'a pas de terminateur : "
            "le T du Serveur a une sortie libre. Non-conformité : extrémité sans terminateur, il faut "
            "un terminateur 50 Ω."
        ),
        caption="À corriger : une extrémité libre réfléchit tout le signal ; tout le segment tombe en panne.",
        svg=bus_svg(BUS_MISSING_TERMINATOR, title="Schéma fautif 1 : terminateur absent"),
    ),
    Figure(
        key="pr16-bus-derivation-et-deux-terres",
        title="Schéma fautif 2 — câble entre T et carte, deux terres",
        alt=(
            "Bus de quatre stations : le PC-2 est relié à son T par un câble (dérivation) au lieu d'avoir "
            "le T branché sur sa carte, et le blindage est mis à la terre aux deux extrémités. "
            "Non-conformités : T à brancher directement sur la carte, un seul point de terre."
        ),
        caption="À corriger : la dérivation crée une branche non terminée ; deux terres créent une boucle de masse.",
        svg=bus_svg(BUS_STUB_AND_GROUNDS, title="Schéma fautif 2 : dérivation, deux terres"),
    ),
    Figure(
        key="pr16-bus-mauvaise-impedance",
        title="Schéma fautif 3 — tronçon 75 Ω et terminateur 75 Ω",
        alt=(
            "Bus de quatre stations : le tronçon de 8 m entre PC-2 et PC-3 est en RG-59 de 75 Ω, et le "
            "terminateur côté Serveur vaut 75 Ω. Non-conformités : il faut du RG-58 50 Ω et un "
            "terminateur 50 Ω."
        ),
        caption="À corriger : chaque changement d'impédance réfléchit une partie du signal.",
        svg=bus_svg(BUS_WRONG_IMPEDANCE, title="Schéma fautif 3 : mauvaise impédance"),
    ),
    Figure(
        key="pr16-bus-cable-coupe",
        title="Schéma fautif 4 — câble coupé",
        alt=(
            "Bus de quatre stations correctement terminé, mais le tronçon de 8 m entre PC-2 et PC-3 est "
            "coupé. Le bus est séparé en deux morceaux non terminés chacun d'un côté."
        ),
        caption="Une coupure laisse deux demi-bus, chacun avec une extrémité libre : plus aucun poste ne communique de façon fiable.",
        svg=bus_svg(BUS_CUT, title="Schéma fautif 4 : câble coupé"),
    ),
)

COAX_SECTION_FIGURE = Figure(
    key="pr16-coupe-coaxial",
    title="Coupe annotée d'un câble coaxial",
    alt=(
        "Coupe d'un coaxial en cercles concentriques, du centre vers l'extérieur : 1 âme (conducteur "
        "central en cuivre), 2 diélectrique (isolant), 3 blindage (feuille et/ou tresse), 4 gaine. "
        "Dessous, le même câble vu de côté, dénudé en gradins : gaine, blindage, diélectrique, âme."
    ),
    caption="Les quatre couches d'un coaxial. L'âme et le blindage partagent le même axe : c'est l'origine du nom.",
    svg=coax_section_svg(),
)

COMPARISON_FIGURE = Figure(
    key="pr16-comparaison-coaxiaux",
    title="10BASE2, 10BASE5 et liaison vidéo 75 Ω",
    alt=(
        "Trois panneaux. 10BASE2 : bus de RG-58 50 Ω, T sur les stations, terminateur 50 Ω à chaque "
        "extrémité, 185 m, 30 stations. 10BASE5 : coaxial épais 50 Ω d'environ 10 mm, prises vampires "
        "et transceivers, câble AUI de 50 m au plus vers la station, connecteurs N, 500 m, 100 "
        "transceivers, espacement de 2,5 m. Vidéo : liaison point à point caméra vers enregistreur en "
        "RG-59 75 Ω avec BNC 75 Ω, sans T ni bus."
    ),
    caption="Même famille de câble, trois usages : l'impédance, la topologie et le connecteur changent.",
    svg=comparison_svg(),
)

BNC_PARTS_FIGURE = Figure(
    key="pr16-bnc-eclate",
    title="Connecteur BNC mâle à sertir, éclaté",
    alt="Quatre pièces dans l'ordre de montage : " + " ; ".join(
        f"{i}. {n} — {d}" for i, (n, d) in enumerate(BNC_PARTS, start=1)
    ) + ".",
    caption="Pièces d'un BNC à sertir en trois éléments (plus le manchon). Les formes varient selon le fabricant.",
    svg=bnc_parts_svg(),
)

STRIP_FIGURE = Figure(
    key="pr16-cotes-denudage",
    title="Préparer le câble : les cotes A, B et C viennent de la notice",
    alt=(
        "Câble dénudé en gradins : gaine, tresse apparente, diélectrique, âme nue. Trois cotes A "
        "(gaine retirée), B (tresse apparente) et C (âme nue) sont repérées sans valeur : elles "
        "sont données par la notice du connecteur choisi, aucune n'est universelle."
    ),
    caption="On ne retient pas de cotes « par cœur » : chaque modèle de connecteur a les siennes.",
    svg=strip_profile_svg(),
)

CRIMP_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier", "Câble et connecteur de même impédance, connecteur prévu pour ce câble ; notice."),
    ("Enfiler", "Manchon puis bague à sertir sur le câble, avant toute préparation."),
    ("Dénuder", "Dénudeur coaxial réglé : cotes de la notice, sans entailler âme ni tresse."),
    ("Contact", "Âme dans le contact central jusqu'en butée ; sertir (ou souder) le contact."),
    ("Corps", "Pousser le corps : contact enclenché, tresse sur le fût, aucun brin vers l'âme."),
    ("Sertir", "Bague sur la tresse, sertir avec la matrice adaptée ; manchon par-dessus."),
    ("Contrôler", "Visuel, traction, continuité âme et blindage, pas de court-circuit."),
)

CRIMP_FIGURE = Figure(
    key="pr16-etapes-bnc",
    title="Monter un BNC à sertir : les sept étapes",
    alt="Sept étapes reliées par des flèches : "
    + " ; ".join(f"{i}. {name} — {detail}" for i, (name, detail) in enumerate(CRIMP_STEPS, start=1)),
    caption="Procédure générale ; les cotes et l'outil de sertissage sont ceux de la notice du connecteur.",
    svg=step_flow_svg(CRIMP_STEPS, width=340),
)

CRIMP_CHECKS_OK: tuple[str, ...] = (
    "Contact central à la bonne hauteur",
    "Tresse entière sous la bague",
    "Bague sertie, ne tourne pas",
    "Résiste à une traction ferme",
    "Âme et blindage continus",
)
CRIMP_DEFECTS: tuple[str, ...] = (
    "Contact en retrait ou trop sorti",
    "Brin de tresse vers l'âme",
    "Bague mal sertie, câble tourne",
    "Âme entaillée ou cassée",
    "Diélectrique écrasé",
)

CRIMP_CHECK_FIGURE = Figure(
    key="pr16-controle-bnc",
    title="Contrôler un BNC serti",
    alt=(
        "Deux listes. Connecteur correct : " + ", ".join(CRIMP_CHECKS_OK)
        + ". Défauts à rechercher : " + ", ".join(CRIMP_DEFECTS) + "."
    ),
    caption="Contrôle visuel et mécanique avant le test électrique : un défaut ici explique souvent une panne intermittente.",
    svg=two_lists_svg("Connecteur correct", CRIMP_CHECKS_OK, "Défauts à rechercher", CRIMP_DEFECTS),
)

# Lectures d'ohmmètre au T du PC-1 (réseau arrêté), calculées sur les bus du cours.
BUS_SHORT = _stations_bus(ATELIER_NAMES, ATELIER_LENGTHS, first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR,
                          faults={2: FAULT_SHORT})
BUS_NO_TERMINATORS = _stations_bus(ATELIER_NAMES, ATELIER_LENGTHS, first=BusEnd(None), last=BusEnd(None))
READING_CASES: tuple[tuple[str, Bus, str], ...] = (
    ("Deux terminateurs 50 Ω en place", BUS_OK, "Normal : 50 Ω ∥ 50 Ω = 25 Ω"),
    ("Un terminateur manquant", BUS_MISSING_TERMINATOR, "Il ne reste qu'un terminateur"),
    ("Coupure entre PC-2 et PC-3", BUS_CUT, "On ne voit que le terminateur de son côté"),
    ("Court-circuit âme/blindage", BUS_SHORT, "Connecteur ou câble en court-circuit"),
    ("Aucun terminateur", BUS_NO_TERMINATORS, "Bus ouvert aux deux bouts"),
)
READINGS: tuple[tuple[str, float | None, str], ...] = tuple(
    (situation, ohmmeter_reading(bus, 0), meaning) for situation, bus, meaning in READING_CASES
)

READINGS_FIGURE = Figure(
    key="pr16-lectures-ohmmetre",
    title="Lire l'ohmmètre sur un bus 10BASE2",
    alt="Mesures au T du PC-1, réseau arrêté : " + " ; ".join(
        f"{s} : {reading_text(v)}, {m}" for s, v, m in READINGS
    ) + ".",
    caption="Mesure entre âme et blindage au T d'une station, réseau arrêté (affichages fictifs, résistance du câble négligée).",
    svg=readings_svg(READINGS),
)

TDR_VF = 0.66
TDR_OPEN_NS = 400
TDR_SHORT_NS = 250

TDR_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr16-tdr-ouvert",
        title="Réflectomètre — circuit ouvert",
        alt=(
            f"Trace fictive : impulsion émise à 0 ns, réflexion positive (même sens) à {TDR_OPEN_NS} ns. "
            f"Facteur de vélocité {fr(TDR_VF, 2)} : circuit ouvert à environ {fr(tdr_distance_m(TDR_OPEN_NS, TDR_VF))} m."
        ),
        caption="Réflexion de même sens que l'impulsion = impédance plus élevée, jusqu'au circuit ouvert (trace fictive).",
        svg=tdr_svg(title="TDR : circuit ouvert", event="ouvert", round_trip_ns=TDR_OPEN_NS, velocity_factor=TDR_VF),
    ),
    Figure(
        key="pr16-tdr-court-circuit",
        title="Réflectomètre — court-circuit",
        alt=(
            f"Trace fictive : impulsion émise à 0 ns, réflexion négative (sens inverse) à {TDR_SHORT_NS} ns. "
            f"Facteur de vélocité {fr(TDR_VF, 2)} : court-circuit à environ {fr(tdr_distance_m(TDR_SHORT_NS, TDR_VF))} m."
        ),
        caption="Réflexion inversée = impédance plus faible, jusqu'au court-circuit (trace fictive).",
        svg=tdr_svg(title="TDR : court-circuit", event="court-circuit", round_trip_ns=TDR_SHORT_NS, velocity_factor=TDR_VF),
    ),
)

PR16_FIGURES: tuple[Figure, ...] = (
    COAX_SECTION_FIGURE,
    BNC_PARTS_FIGURE,
    BUS_OK_FIGURE,
    *BUS_FAULT_FIGURES,
    COMPARISON_FIGURE,
    STRIP_FIGURE,
    CRIMP_FIGURE,
    CRIMP_CHECK_FIGURE,
    READINGS_FIGURE,
    *TDR_FIGURES,
)

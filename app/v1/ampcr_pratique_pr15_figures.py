"""Schémas du cours PR15 « Câblage RJ45 T568A/B — fabrication, schémas et tests » (ticket #197).

Règle du ticket : brochages, couleurs, numéros de broches et paires sont **construits depuis
des données vérifiées** (`T568A` / `T568B` du socle #192, normes TIA/EIA-568) et contrôlés par
`tests/test_ticket197_ampcr_pratique_pr15.py` ; aucun n'est tiré d'une image générée. Chaque
schéma porte son information en texte (numéro, nom de couleur, paire) : la couleur n'est qu'un
repère, le schéma reste lisible imprimé en noir et blanc. Les affichages de testeur sont des
reconstitutions **fictives** (présentation variable selon le modèle), calculées à partir des
liaisons broche à broche décrites ici.
"""

from html import escape

from app.v1.ampcr_pratique_visuals import (
    T568A,
    T568B,
    WIRE_COLORS,
    Figure,
    _svg,
    _text_lines,
    _wrap,
    step_flow_svg,
)

# --- Données de référence ---------------------------------------------------------------

# Orientation de lecture de TOUS les schémas de fiche de ce cours.
PLUG_ORIENTATION = (
    "Fiche RJ45 (8P8C) vue côté contacts dorés, languette de verrouillage dessous (côté "
    "opposé, non visible), extrémité de la fiche vers le haut et câble vers le bas : "
    "broche 1 à gauche, broche 8 à droite."
)

# Numérotation des paires de la norme TIA-568 : paire 1 bleue, 2 orange, 3 verte, 4 marron.
PAIR_NUMBERS: dict[str, int] = {"bleu": 1, "orange": 2, "vert": 3, "marron": 4}
# Positions des paires dans la fiche (identiques en T568A et T568B).
PAIR_POSITIONS: tuple[tuple[int, int], ...] = ((1, 2), (3, 6), (4, 5), (7, 8))

STANDARDS: dict[str, tuple[str, ...]] = {"T568A": T568A, "T568B": T568B}


def wire_label(wire: str) -> str:
    """« blanc-orange » → « blanc/orange » (graphie du cours)."""
    return wire.replace("-", "/")


def pair_color(wire: str) -> str:
    return wire.removeprefix("blanc-")


def pairs_by_position(wires: tuple[str, ...]) -> dict[tuple[int, int], str]:
    """Couleur de la paire branchée sur chaque position (1-2, 3-6, 4-5, 7-8), en vérifiant
    que les deux broches d'une position portent bien les deux fils d'une même paire."""
    result = {}
    for a, b in PAIR_POSITIONS:
        ca, cb = pair_color(wires[a - 1]), pair_color(wires[b - 1])
        if ca != cb:
            raise ValueError(f"Broches {a}-{b} : fils de deux paires différentes (paire séparée).")
        result[(a, b)] = ca
    return result


def straight_links(wires: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    """Câble droit : même norme aux deux bouts, broche n → broche n."""
    return tuple((pin, pin) for pin in range(1, len(wires) + 1))


def links_between(end_a: tuple[str, ...], end_b: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    """Broche de l'extrémité B où arrive le fil de chaque broche de l'extrémité A (le même
    fil, repéré par sa couleur)."""
    return tuple((pin, end_b.index(wire) + 1) for pin, wire in enumerate(end_a, start=1))


def split_pairs(wires: tuple[str, ...]) -> list[tuple[int, int]]:
    """Positions de paire (1-2, 3-6, 4-5, 7-8) dont les deux broches ne reçoivent pas les
    deux fils d'une même paire torsadée."""
    return [(a, b) for a, b in PAIR_POSITIONS if pair_color(wires[a - 1]) != pair_color(wires[b - 1])]


# Erreur classique : paires rangées côte à côte (1-2, 3-4, 5-6, 7-8). La continuité broche à
# broche est parfaite si les deux bouts sont faits pareil, mais les broches 3-6 et 4-5 ne
# sont plus chacune sur une paire torsadée : paires séparées (split pairs).
SEQUENTIAL_WRONG: tuple[str, ...] = (
    "blanc-orange", "orange", "blanc-vert", "vert", "blanc-bleu", "bleu", "blanc-marron", "marron",
)

# Usage des broches par Ethernet (IEEE 802.3) côté carte réseau (MDI). Un switch (MDI-X)
# inverse émission et réception en 10/100 Mb/s.
ETHERNET_PIN_USE: tuple[tuple[int, str, str], ...] = (
    (1, "TX+ (émission)", "BI_DA+"),
    (2, "TX− (émission)", "BI_DA−"),
    (3, "RX+ (réception)", "BI_DB+"),
    (4, "inutilisée", "BI_DC+"),
    (5, "inutilisée", "BI_DC−"),
    (6, "RX− (réception)", "BI_DB−"),
    (7, "inutilisée", "BI_DD+"),
    (8, "inutilisée", "BI_DD−"),
)

# Catégories : valeurs usuelles (TIA-568 / IEEE 802.3), longueur de canal 100 m.
CATEGORIES: tuple[tuple[str, int, str, str], ...] = (
    ("Cat5e", 100, "1 Gb/s (1000BASE-T) sur 100 m", "Minimum courant ; 10 Gb/s non prévu"),
    ("Cat6", 250, "1 Gb/s sur 100 m ; 10 Gb/s sur une longueur réduite (environ 37 à 55 m selon l'environnement)", "Diaphonie entre câbles voisins limitante à 10 Gb/s"),
    ("Cat6A", 500, "10 Gb/s (10GBASE-T) sur 100 m", "Câble plus épais, connecteurs Cat6A"),
)
CHANNEL_MAX_M = 100
PERMANENT_LINK_MAX_M = 90
CORDS_MAX_M = 10


# --- Dessins -------------------------------------------------------------------------------

_STROKE = "#33415c"


def _wire_strip(x: float, y: float, w: float, h: float, wire: str) -> str:
    """Fil vu de face : plein pour une couleur, blanc rayé pour « blanc-x » (lisible en N&B)."""
    color = WIRE_COLORS[pair_color(wire)]
    if not wire.startswith("blanc-"):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{color}" stroke="{color}" stroke-width="1.5"/>'
    stripes = "".join(
        f'<rect x="{x + 2}" y="{y + 4 + i * 16}" width="{w - 4}" height="7" fill="{color}"/>'
        for i in range(int((h - 6) // 16))
    )
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#ffffff" stroke="{color}" stroke-width="1.5"/>{stripes}'


def pinout_svg(wires: tuple[str, ...], *, title: str, wrong: bool = False) -> str:
    """Fiche 8P8C dans l'orientation `PLUG_ORIENTATION` (broche 1 à gauche), puis la liste
    texte des 8 broches : numéro, couleur, paire et position de paire."""
    if len(wires) != 8:
        raise ValueError("Une fiche 8P8C compte exactement 8 broches.")
    width = 380
    plug_x, plug_w, top = 70, 240, 34
    slot = plug_w / 8
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">{escape(title)}</text>',
        # corps de la fiche (extrémité en haut), contacts, puis fils sortant vers le câble (bas)
        f'<rect x="{plug_x}" y="{top}" width="{plug_w}" height="96" rx="6" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="2"/>',
        f'<text x="{plug_x + plug_w + 6}" y="{top + 14}" font-size="10.5">extrémité</text>',
        f'<text x="{plug_x + plug_w + 6}" y="{top + 27}" font-size="10.5">de la fiche</text>',
    ]
    for index, wire in enumerate(wires):
        pin = index + 1
        x = plug_x + index * slot
        parts.append(
            f'<rect x="{x + 7:.1f}" y="{top + 6}" width="{slot - 14:.1f}" height="16" rx="2" '
            f'fill="#d4a017" stroke="#8a6d0b" stroke-width="1"/>'
            f'<text x="{x + slot / 2:.1f}" y="{top + 38}" text-anchor="middle" font-size="13" font-weight="700">{pin}</text>'
        )
        parts.append(
            f'<g data-pin="{pin}" data-wire="{escape(wire)}">'
            + _wire_strip(round(x + 6, 1), top + 44, round(slot - 12, 1), 100, wire)
            + "</g>"
        )
    parts.append(
        f'<rect x="{plug_x + 20}" y="{top + 132}" width="{plug_w - 40}" height="18" rx="4" fill="#cfd6e4" stroke="{_STROKE}" stroke-width="1.5"/>'
        f'<text x="{width // 2}" y="{top + 145}" text-anchor="middle" font-size="10.5">gaine du câble (vers le bas)</text>'
    )
    y = top + 172
    parts.append(_text_lines(8, y, ["Broche · couleur du fil · paire"], size=11.5, weight="700"))
    positions = {pin: (a, b) for a, b in PAIR_POSITIONS for pin in (a, b)}
    for index, wire in enumerate(wires):
        pin = index + 1
        a, b = positions[pin]
        color = pair_color(wire)
        row_y = y + 18 + index * 18
        parts.append(
            f'<text x="8" y="{row_y}" font-size="12" font-weight="700">{pin}</text>'
            f'<text x="30" y="{row_y}" font-size="12">{escape(wire_label(wire))}</text>'
            f'<text x="150" y="{row_y}" font-size="12">paire {PAIR_NUMBERS[color]} ({escape(color)})</text>'
            f'<text x="{width - 8}" y="{row_y}" font-size="11" text-anchor="end">position {a}-{b}</text>'
        )
    y += 18 + 8 * 18
    if wrong:
        parts.append(
            f'<rect x="4" y="{y - 4}" width="{width - 8}" height="22" rx="4" fill="#fbecec" stroke="#b3261e" stroke-width="1.5"/>'
            f'<text x="{width // 2}" y="{y + 11}" text-anchor="middle" font-size="12" font-weight="700">'
            "✗ ORDRE FAUX — ne pas reproduire</text>"
        )
        y += 24
    return _svg(width, y + 4, parts)


def comparison_svg() -> str:
    """Tableau broche ↔ T568A ↔ T568B : « = » si la broche est identique, « ≠ » sinon."""
    width, top, row_h = 380, 46, 24
    parts = [
        f'<text x="{width // 2}" y="16" text-anchor="middle" font-weight="700" font-size="14">T568A et T568B, broche par broche</text>',
        _text_lines(8, top - 8, ["Broche"], size=11.5, weight="700"),
        _text_lines(70, top - 8, ["T568A"], size=11.5, weight="700"),
        _text_lines(196, top - 8, ["T568B"], size=11.5, weight="700"),
        _text_lines(width - 8, top - 8, ["A / B"], size=11.5, weight="700", anchor="end"),
    ]
    for index, (wa, wb) in enumerate(zip(T568A, T568B, strict=True)):
        pin = index + 1
        y = top + index * row_h
        same = wa == wb
        parts.append(
            f'<rect data-pin="{pin}" data-a="{escape(wa)}" data-b="{escape(wb)}" x="4" y="{y}" width="{width - 8}" '
            f'height="{row_h - 3}" rx="3" fill="{"#f4f6fb" if same else "#fff4e0"}" stroke="{_STROKE}" stroke-width="1"/>'
            f'<text x="20" y="{y + 15}" font-size="12" font-weight="700">{pin}</text>'
            + _wire_strip(52, y + 3, 12, row_h - 9, wa)
            + f'<text x="70" y="{y + 15}" font-size="12">{escape(wire_label(wa))}</text>'
            + _wire_strip(178, y + 3, 12, row_h - 9, wb)
            + f'<text x="196" y="{y + 15}" font-size="12">{escape(wire_label(wb))}</text>'
            f'<text x="{width - 12}" y="{y + 15}" font-size="12" font-weight="700" text-anchor="end">'
            f'{"=" if same else "≠"}</text>'
        )
    y = top + 8 * row_h + 14
    notes = (
        "≠ : broches 1, 2, 3 et 6 — A et B échangent la paire orange et la paire verte.",
        "= : broches 4, 5, 7 et 8 — paires bleue (4-5) et marron (7-8) identiques.",
    )
    for note in notes:
        lines = _wrap(note, 56)
        parts.append(_text_lines(8, y, lines, size=11.5))
        y += 16 * len(lines) + 4
    return _svg(width, y, parts)


def wiremap_svg(
    links: tuple[tuple[int, int | None], ...],
    *,
    title: str,
    verdict: str,
    notes: tuple[str, ...] = (),
    left: str = "Extrémité A",
    right: str = "Extrémité B",
    left_wires: tuple[str, ...] | None = None,
    right_wires: tuple[str, ...] | None = None,
    shorts: tuple[tuple[int, int], ...] = (),
    split: tuple[tuple[int, int], ...] = (),
) -> str:
    """Liaisons broche à broche entre deux extrémités (câble ou affichage de testeur) :
    `links` = (broche A, broche B ou None si circuit ouvert). Chaque broche est écrite en
    texte, avec la couleur de son fil si elle est fournie ; le verdict est écrit en clair."""
    width, top, row_h = 380, 56, 24
    lx, rx = 132, 248  # extrémités des liaisons
    parts = [
        f'<text x="{width // 2}" y="16" text-anchor="middle" font-weight="700" font-size="13.5">{escape(title)}</text>',
        f'<text x="8" y="{top - 14}" font-size="11.5" font-weight="700">{escape(left)}</text>',
        f'<text x="{width - 8}" y="{top - 14}" font-size="11.5" font-weight="700" text-anchor="end">{escape(right)}</text>',
    ]

    def row_y(pin: int) -> int:
        return top + (pin - 1) * row_h

    for pin in range(1, 9):
        y = row_y(pin)
        lw = f" {wire_label(left_wires[pin - 1])}" if left_wires else ""
        rw = f"{wire_label(right_wires[pin - 1])} " if right_wires else ""
        parts.append(
            f'<text x="8" y="{y + 4}" font-size="11.5"><tspan font-weight="700">{pin}</tspan>{escape(lw)}</text>'
            f'<circle cx="{lx}" cy="{y}" r="4" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<circle cx="{rx}" cy="{y}" r="4" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<text x="{width - 8}" y="{y + 4}" font-size="11.5" text-anchor="end">{escape(rw)}<tspan font-weight="700">{pin}</tspan></text>'
        )
    for a, b in links:
        ya = row_y(a)
        if b is None:
            parts.append(
                f'<path data-link="{a}-ouvert" d="M{lx + 4} {ya} H{lx + 40}" stroke="{_STROKE}" stroke-width="2"/>'
                f'<text x="{lx + 46}" y="{ya + 4}" font-size="11" font-weight="700">✗ ouvert</text>'
            )
            continue
        dash = "" if a == b else ' stroke-dasharray="6 3"'
        parts.append(
            f'<path data-link="{a}-{b}" d="M{lx + 4} {ya} L{rx - 4} {row_y(b)}" stroke="{_STROKE}" '
            f'stroke-width="2"{dash}/>'
        )
    for a, b in shorts:
        parts.append(
            f'<path data-short="{a}-{b}" d="M{lx - 10} {row_y(a)} V{row_y(b)}" stroke="#b3261e" stroke-width="3"/>'
            f'<text x="{lx - 14}" y="{(row_y(a) + row_y(b)) // 2 + 4}" font-size="10.5" font-weight="700" text-anchor="end">court-circuit</text>'
        )
    for column, (a, b) in enumerate(split):
        ya, yb, x = row_y(a), row_y(b), lx - 14 - 22 * column
        parts.append(
            f'<path data-split="{a}-{b}" d="M{x} {ya} h-6 V{yb} h6" fill="none" stroke="#b3261e" stroke-width="2"/>'
            f'<text x="{x - 3}" y="{ya - 7}" font-size="10" font-weight="700" text-anchor="middle">{a}-{b}</text>'
        )
    y = row_y(8) + 26
    verdict_lines = _wrap(verdict, 50)
    box_h = 10 + 16 * len(verdict_lines)
    parts.append(
        f'<rect x="4" y="{y - 14}" width="{width - 8}" height="{box_h}" rx="5" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
    )
    parts.append(_text_lines(12, y, verdict_lines, size=12, weight="700"))
    y += box_h + 6
    for note in notes:
        lines = _wrap(note, 58)
        parts.append(_text_lines(8, y, lines, size=11))
        y += 15 * len(lines) + 3
    return _svg(width, y, parts)


def plug_anatomy_svg() -> str:
    """Fiche 8P8C vue de dessus, schématique (non à l'échelle), avec ses repères."""
    width, height = 380, 300
    parts = [
        f'<text x="{width // 2}" y="16" text-anchor="middle" font-weight="700" font-size="14">Fiche 8P8C sertie : les repères à contrôler</text>',
        # corps
        f'<rect x="90" y="32" width="200" height="180" rx="8" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="2"/>',
    ]
    for i in range(8):
        x = 102 + i * 23
        parts.append(f'<rect x="{x}" y="38" width="14" height="22" rx="2" fill="#d4a017" stroke="#8a6d0b"/>')
        parts.append(f'<path d="M{x + 7} 60 V150" stroke="{WIRE_COLORS[pair_color(T568B[i])]}" stroke-width="5"/>')
    parts += [
        # gaine dans la fiche, sous la patte de maintien
        f'<rect x="120" y="150" width="140" height="110" rx="6" fill="#cfd6e4" stroke="{_STROKE}" stroke-width="1.5"/>',
        '<rect x="110" y="170" width="160" height="14" rx="3" fill="none" stroke="#b3261e" stroke-width="2" stroke-dasharray="5 3"/>',
        # repères
        f'<path d="M290 49 H316" stroke="{_STROKE}"/>',
        _text_lines(320, 46, ["1 contacts", "en bout"], size=10.5),
        f'<path d="M290 104 H316" stroke="{_STROKE}"/>',
        _text_lines(320, 100, ["2 fils en", "butée,", "dans l'ordre"], size=10.5),
        f'<path d="M270 177 H316" stroke="{_STROKE}"/>',
        _text_lines(320, 174, ["3 patte de", "maintien"], size=10.5),
        f'<path data-dimension="detorsade" d="M84 62 h-6 V150 h6" fill="none" stroke="{_STROKE}" stroke-width="1.5"/>',
        _text_lines(6, 96, ["4 détorsadé", "≈ 12-13 mm", "au plus"], size=10.5),
        f'<path d="M120 230 H64" stroke="{_STROKE}"/>',
        _text_lines(6, 226, ["5 gaine", "dans la", "fiche"], size=10.5),
        _text_lines(width // 2, 280, ["Vue de dessus, contacts visibles, broche 1 à gauche (schéma,"], size=10.5, anchor="middle"),
        _text_lines(width // 2, 294, ["non à l'échelle ; fils dessinés dans l'ordre T568B)."], size=10.5, anchor="middle"),
    ]
    return _svg(width, height, parts)


def chain_svg(elements: tuple[tuple[str, str], ...], brackets: tuple[tuple[int, int, str], ...]) -> str:
    """Chaîne verticale d'éléments (nom, précision) reliés par des flèches ; `brackets` =
    (premier, dernier élément inclus, libellé) dessinés à droite (lien permanent, canal)."""
    width, box_w, box_h, gap = 380, 206, 44, 16
    parts: list[str] = []
    centers: list[tuple[int, int]] = []
    y = 8
    for index, (name, detail) in enumerate(elements):
        parts.append(
            f'<rect data-element="{index + 1}" x="6" y="{y}" width="{box_w}" height="{box_h}" rx="7" '
            f'fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(14, y + 18, [f"{index + 1}. {name}"], size=12.5, weight="700"))
        parts.append(_text_lines(14, y + 35, _wrap(detail, 34)[:1], size=11))
        centers.append((y, y + box_h))
        if index < len(elements) - 1:
            mid = 6 + box_w // 2
            parts.append(
                f'<path d="M{mid} {y + box_h + 1} V{y + box_h + gap - 3}" stroke="{_STROKE}" stroke-width="2"/>'
                f'<path d="M{mid - 5} {y + box_h + gap - 8} L{mid} {y + box_h + gap - 2} L{mid + 5} {y + box_h + gap - 8}" '
                f'fill="none" stroke="{_STROKE}" stroke-width="2"/>'
            )
        y += box_h + gap
    for column, (first, last, label) in enumerate(brackets):
        x = box_w + 16 + column * 80
        y1, y2 = centers[first - 1][0] + 4, centers[last - 1][1] - 4
        parts.append(
            f'<path data-bracket="{first}-{last}" d="M{x} {y1} h8 V{y2} h-8" fill="none" stroke="#1f5fbf" stroke-width="2"/>'
        )
        lines = _wrap(label, 9)
        cy = (y1 + y2) // 2 - 7 * (len(lines) - 1)
        parts.append(_text_lines(x + 12, cy, lines, size=11, weight="700", step=14))
    return _svg(width, y - gap + 8, parts)


# --- Figures du cours ----------------------------------------------------------------------


def _pin_alt(wires: tuple[str, ...]) -> str:
    return ", ".join(f"broche {i} {wire_label(w)}" for i, w in enumerate(wires, start=1))


T568A_FIGURE = Figure(
    key="pr15-brochage-t568a",
    title="Brochage T568A, broches 1 à 8",
    alt=f"{PLUG_ORIENTATION} T568A : {_pin_alt(T568A)}. Paires : verte sur 1-2, orange sur 3-6, bleue sur 4-5, marron sur 7-8.",
    caption=(
        "T568A. Orientation : contacts dorés face à toi, languette dessous, câble vers le bas — "
        "broche 1 à gauche. Fils blancs rayés de la couleur de leur paire ; la liste texte fait foi."
    ),
    svg=pinout_svg(T568A, title="T568A — fiche vue côté contacts"),
)

T568B_FIGURE = Figure(
    key="pr15-brochage-t568b",
    title="Brochage T568B, broches 1 à 8",
    alt=f"{PLUG_ORIENTATION} T568B : {_pin_alt(T568B)}. Paires : orange sur 1-2, verte sur 3-6, bleue sur 4-5, marron sur 7-8.",
    caption=(
        "T568B. Même orientation que T568A : contacts face à toi, languette dessous, câble vers le "
        "bas — broche 1 à gauche. La liste texte fait foi."
    ),
    svg=pinout_svg(T568B, title="T568B — fiche vue côté contacts"),
)

COMPARISON_FIGURE = Figure(
    key="pr15-comparaison-a-b",
    title="Correspondance broche, paire et couleur : T568A et T568B",
    alt=(
        "Tableau de 8 lignes : "
        + " ; ".join(
            f"broche {i} : T568A {wire_label(a)}, T568B {wire_label(b)}, {'identique' if a == b else 'différent'}"
            for i, (a, b) in enumerate(zip(T568A, T568B, strict=True), start=1)
        )
        + ". Les broches 1, 2, 3 et 6 changent (paires orange et verte échangées), 4, 5, 7 et 8 sont identiques."
    ),
    caption="Comparaison broche par broche : seules les paires orange et verte changent de place (signe ≠).",
    svg=comparison_svg(),
)

SEQUENTIAL_WRONG_FIGURE = Figure(
    key="pr15-ordre-faux-paires-separees",
    title="Erreur classique : paires rangées côte à côte (ordre FAUX)",
    alt=(
        f"{PLUG_ORIENTATION} Ordre faux : {_pin_alt(SEQUENTIAL_WRONG)}. Les broches 3 et 6 "
        "reçoivent blanc/vert et bleu, les broches 4 et 5 vert et blanc/bleu : deux paires séparées."
    ),
    caption=(
        "Ordre FAUX : 1-2, 3-4, 5-6, 7-8 rangés paire par paire. La position 3-6 reçoit un fil "
        "vert et un fil bleu : paire séparée (split pair), même si un testeur simple affiche 1→1 … 8→8."
    ),
    svg=pinout_svg(SEQUENTIAL_WRONG, title="Ordre faux — fiche vue côté contacts", wrong=True),
)

STRAIGHT_LINKS = straight_links(T568B)
STRAIGHT_FIGURE = Figure(
    key="pr15-cable-droit-b-b",
    title="Câble droit T568B ↔ T568B",
    alt=(
        "Deux extrémités câblées en T568B ; chaque broche arrive sur la même broche : "
        + ", ".join(f"{a} vers {b}" for a, b in STRAIGHT_LINKS)
        + "."
    ),
    caption="Câble droit : même norme aux deux bouts (ici B-B), broche n → broche n.",
    svg=wiremap_svg(
        STRAIGHT_LINKS,
        title="Câble droit B-B",
        verdict="Droit : 1→1, 2→2, … 8→8.",
        left="Bout 1 (T568B)",
        right="Bout 2 (T568B)",
        left_wires=T568B,
        right_wires=T568B,
    ),
)

CROSSOVER_LINKS = links_between(T568A, T568B)
CROSSOVER_FIGURE = Figure(
    key="pr15-cable-croise-a-b",
    title="Câble croisé T568A ↔ T568B",
    alt=(
        "Bout 1 en T568A, bout 2 en T568B ; chaque fil arrive sur la broche de même couleur : "
        + ", ".join(f"{a} vers {b}" for a, b in CROSSOVER_LINKS)
        + ". Les paires orange et verte sont croisées, les paires bleue et marron restent droites."
    ),
    caption=(
        "Câble croisé historique : A à un bout, B à l'autre. 1↔3 et 2↔6 (liaisons en pointillés), "
        "4, 5, 7, 8 droites. Il croise l'émission et la réception du 10/100 Mb/s."
    ),
    svg=wiremap_svg(
        CROSSOVER_LINKS,
        title="Câble croisé A-B",
        verdict="Croisé : 1→3, 2→6, 3→1, 6→2 ; 4, 5, 7, 8 droits.",
        left="Bout 1 (T568A)",
        right="Bout 2 (T568B)",
        left_wires=T568A,
        right_wires=T568B,
    ),
)

ANATOMY_FIGURE = Figure(
    key="pr15-anatomie-fiche",
    title="Fiche 8P8C sertie : repères de contrôle",
    alt=(
        "Schéma d'une fiche vue de dessus, contacts visibles, broche 1 à gauche, fils dessinés dans "
        "l'ordre T568B. Repères : 1 les huit contacts dorés en bout ; 2 les huit fils poussés en "
        "butée au fond de la fiche, dans l'ordre ; 3 la patte de maintien qui serre la gaine ; "
        "4 longueur détorsadée d'environ 12 à 13 mm au plus ; 5 la gaine entre dans la fiche."
    ),
    caption=(
        "Ce qu'on contrôle après sertissage : fils en butée et dans l'ordre, gaine serrée par la "
        "patte de maintien, détorsadage minimal. Schéma, non à l'échelle."
    ),
    svg=plug_anatomy_svg(),
)

CRIMP_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Câble et fiches compatibles (catégorie, monobrin ou multibrin) ; manchons enfilés."),
    ("Couper et dénuder", "Coupe franche ; retirer 25 à 30 mm de gaine sans entailler les fils."),
    ("Ranger", "Détorsader le minimum, ranger dans l'ordre T568A ou T568B, aplatir les fils."),
    ("Recouper", "Couper droit à environ 12-13 mm : la gaine doit entrer dans la fiche."),
    ("Insérer", "Contacts vers soi, broche 1 à gauche ; pousser les 8 fils jusqu'en butée."),
    ("Contrôler", "Ordre des couleurs à travers la fiche, fils en bout, gaine sous la patte."),
    ("Sertir", "Pince adaptée, pression complète ; puis l'autre bout selon droit ou croisé."),
    ("Tester", "Testeur de câble (wiremap) avant mise en service ; noter le résultat."),
)

CRIMP_FIGURE = Figure(
    key="pr15-etapes-sertissage",
    title="Fabriquer un cordon RJ45 : les huit étapes",
    alt="Huit étapes reliées par des flèches : "
    + " ; ".join(f"{i}. {name} — {detail}" for i, (name, detail) in enumerate(CRIMP_STEPS, start=1)),
    caption="Procédure de sertissage d'une fiche, de haut en bas. Un câble non testé n'est pas terminé.",
    svg=step_flow_svg(CRIMP_STEPS, width=340),
)

# --- Affichages de testeur (wiremap) fictifs --------------------------------------------------

TESTER_GOOD = tuple((p, p) for p in range(1, 9))
TESTER_OPEN = tuple((p, None if p == 7 else p) for p in range(1, 9))
TESTER_REVERSED = ((1, 2), (2, 1)) + tuple((p, p) for p in range(3, 9))
TESTER_SPLIT = TESTER_GOOD  # continuité parfaite : seul un testeur qui mesure la diaphonie voit le défaut
SPLIT_POSITIONS = tuple(split_pairs(SEQUENTIAL_WRONG))

_TESTER_NOTE = "Affichage de testeur fictif ; présentation variable selon le modèle."

TESTER_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr15-testeur-bon",
        title="Testeur — câble droit conforme",
        alt="Affichage de testeur fictif : liaisons 1 vers 1 jusqu'à 8 vers 8, toutes présentes. Verdict : câblage conforme, câble droit.",
        caption="Câble droit conforme : 8 liaisons broche à broche. Ce test ne mesure ni la catégorie ni le débit (affichage fictif).",
        svg=wiremap_svg(TESTER_GOOD, title="Wiremap : câble conforme", verdict="RÉSULTAT : RÉUSSI — câble droit 1→1 … 8→8.",
                        left="Testeur", right="Bouchon distant", notes=(_TESTER_NOTE,)),
    ),
    Figure(
        key="pr15-testeur-ouvert",
        title="Testeur — circuit ouvert sur la broche 7",
        alt="Affichage de testeur fictif : liaisons 1 à 6 et 8 présentes, broche 7 sans liaison (circuit ouvert). Verdict : échec, ouvert broche 7.",
        caption="Circuit ouvert : le fil de la broche 7 (blanc/marron en T568B) n'arrive pas, souvent un fil pas en butée ou coupé (affichage fictif).",
        svg=wiremap_svg(TESTER_OPEN, title="Wiremap : circuit ouvert", verdict="RÉSULTAT : ÉCHEC — circuit ouvert broche 7.",
                        left="Testeur", right="Bouchon distant",
                        notes=("Fil non en butée, coupé ou non serti : refaire la fiche en cause.", _TESTER_NOTE)),
    ),
    Figure(
        key="pr15-testeur-inverse",
        title="Testeur — fils inversés sur la paire 1-2",
        alt="Affichage de testeur fictif : broche 1 vers 2, broche 2 vers 1, broches 3 à 8 droites. Verdict : échec, paire 1-2 inversée.",
        caption="Fils inversés : les deux fils d'une même paire sont permutés à un bout (1→2, 2→1) (affichage fictif).",
        svg=wiremap_svg(TESTER_REVERSED, title="Wiremap : paire inversée", verdict="RÉSULTAT : ÉCHEC — paire 1-2 inversée.",
                        left="Testeur", right="Bouchon distant",
                        notes=("Blanc/orange et orange permutés à un bout : refaire cette fiche.", _TESTER_NOTE)),
    ),
    Figure(
        key="pr15-testeur-paires-separees",
        title="Testeur de qualification — paires séparées 3-6 / 4-5",
        alt=(
            "Affichage de testeur fictif : liaisons 1 vers 1 jusqu'à 8 vers 8, continuité correcte, "
            "mais crochets sur les positions 3-6 et 4-5. Verdict : échec, paires séparées (split pair) "
            "détectées par la mesure de diaphonie."
        ),
        caption=(
            "Paires séparées : continuité parfaite, mais 3-6 et 4-5 ne sont pas sur une même paire "
            "torsadée. Un testeur de continuité simple afficherait « réussi » (affichage fictif)."
        ),
        svg=wiremap_svg(TESTER_SPLIT, title="Wiremap : paires séparées",
                        verdict="RÉSULTAT : ÉCHEC — paires séparées 3-6 et 4-5 (diaphonie).",
                        left="Testeur", right="Bouchon distant", split=SPLIT_POSITIONS,
                        notes=("Cause typique : fils rangés côte à côte (ordre faux) aux deux bouts.", _TESTER_NOTE)),
    ),
)

# Exemple 3 du cours : à un bout, le fil vert (broche 6 en T568B) et le fil bleu (broche 4)
# ont été permutés. Extrémité B réelle :
EXAMPLE3_END_B: tuple[str, ...] = T568B[:3] + (T568B[5], T568B[4], T568B[3]) + T568B[6:]
EXAMPLE3_LINKS = links_between(T568B, EXAMPLE3_END_B)
EXAMPLE3_FIGURE = Figure(
    key="pr15-exemple-erreur-3-6",
    title="Exemple 3 — fils vert et bleu permutés à un bout",
    alt=(
        "Bout 1 en T568B, bout 2 avec vert en broche 4 et bleu en broche 6 : "
        + ", ".join(f"{a} vers {b}" for a, b in EXAMPLE3_LINKS)
        + ". Verdict : échec, fils croisés 4 et 6."
    ),
    caption="Relevé fictif de l'exemple 3 : 4→6 et 6→4 (pointillés). La paire 3-6 n'est plus la paire verte.",
    svg=wiremap_svg(EXAMPLE3_LINKS, title="Wiremap : erreur sur la broche 6",
                    verdict="RÉSULTAT : ÉCHEC — fils croisés 4↔6.",
                    left="Bout 1 (T568B)", right="Bout 2 (réalisé)",
                    left_wires=T568B, right_wires=EXAMPLE3_END_B, notes=(_TESTER_NOTE,)),
)

CHAIN_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Switch (baie)", "Port de l'équipement actif"),
    ("Cordon de brassage", "Multibrin, fiches serties, court"),
    ("Panneau de brassage", "Port étiqueté, câble poinçonné"),
    ("Câble permanent", "Monobrin, chemins de câbles"),
    ("Prise murale", "Keystone poinçonné, port étiqueté"),
    ("Cordon de poste", "Multibrin, prise murale → PC"),
    ("PC", "Carte réseau du poste"),
)
CHAIN_BRACKETS: tuple[tuple[int, int, str], ...] = (
    (3, 5, f"lien permanent ≤ {PERMANENT_LINK_MAX_M} m"),
    (1, 7, f"canal ≤ {CHANNEL_MAX_M} m"),
)

CHAIN_FIGURE = Figure(
    key="pr15-chaine-baie-pc",
    title="Chaîne de câblage : de la baie au PC",
    alt=(
        "Sept éléments de haut en bas : "
        + " ; ".join(f"{i}. {n} ({d})" for i, (n, d) in enumerate(CHAIN_ELEMENTS, start=1))
        + f". Accolade du panneau à la prise murale : lien permanent de {PERMANENT_LINK_MAX_M} m au plus. "
        f"Accolade du switch au PC : canal de {CHANNEL_MAX_M} m au plus, cordons compris."
    ),
    caption=(
        f"Canal ≤ {CHANNEL_MAX_M} m = lien permanent ≤ {PERMANENT_LINK_MAX_M} m + cordons "
        f"(≈ {CORDS_MAX_M} m au total). On teste et on étiquette les deux bouts du lien permanent."
    ),
    svg=chain_svg(CHAIN_ELEMENTS, CHAIN_BRACKETS),
)

PR15_FIGURES: tuple[Figure, ...] = (
    T568A_FIGURE,
    T568B_FIGURE,
    COMPARISON_FIGURE,
    SEQUENTIAL_WRONG_FIGURE,
    STRAIGHT_FIGURE,
    CROSSOVER_FIGURE,
    ANATOMY_FIGURE,
    CRIMP_FIGURE,
    *TESTER_FIGURES,
    EXAMPLE3_FIGURE,
    CHAIN_FIGURE,
)

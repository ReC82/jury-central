"""Schémas techniques du parcours AMPCR pratique écrite (ticket #192).

Règle des tickets PR/EX : un schéma qui porte une information technique exacte (brochage,
couleurs, ordre d'étapes, valeurs) est construit **à partir de données vérifiées**, en SVG
vectoriel, jamais par une image générée. Ce module fournit le socle commun, sans nouvelle
dépendance (SVG écrit à la main, comme les schémas FSE) :

- `Figure` / `render_figure` : figure accessible (`role="img"`, `<title>`, `<desc>`,
  légende, mention « non officiel »), mise à l'échelle par `viewBox` (mobile) et protégée
  des coupures de page (impression A4) ;
- `step_flow_svg` : démarche en étapes reliées par des flèches (méthode, procédure) ;
- `connector_pins_svg` : rangée de broches numérotées (fiche 8P8C) dont chaque fil est
  dessiné depuis `WIRE_COLORS` ; les fils « blanc-x » sont rayés, pour rester lisibles en
  noir et blanc ; le tableau texte reste la référence (`pin_table`) ;
- `validate_figure` : refuse un schéma sans texte alternatif, sans légende, sans `viewBox`,
  ou contenant du script ou une ressource externe.

Les illustrations d'ambiance (gestes, outils, situations) passent par la génération d'images
existante (`app.ai.factory.get_image_provider`, commande manuelle, fichier statique + JSON du
prompt — voir `app/v1/parcours_images.py`), jamais pour des broches, des textes ou des valeurs.
"""

import re
from dataclasses import dataclass
from html import escape

from markupsafe import Markup

# Couleurs de fil d'un câble à 4 paires torsadées. Les codes T568A/T568B sont ceux des
# normes TIA/EIA-568 (broches 1 → 8) ; ils sont vérifiés par les tests du ticket #192.
WIRE_COLORS: dict[str, str] = {
    "orange": "#e8740c",
    "vert": "#2e8b3a",
    "bleu": "#1f5fbf",
    "marron": "#7a4a21",
}
T568A: tuple[str, ...] = (
    "blanc-vert", "vert", "blanc-orange", "bleu", "blanc-bleu", "orange", "blanc-marron", "marron",
)
T568B: tuple[str, ...] = (
    "blanc-orange", "orange", "blanc-vert", "bleu", "blanc-bleu", "vert", "blanc-marron", "marron",
)
RJ45_ORIENTATION = (
    "Fiche vue côté contacts dorés, languette de verrouillage dessous : broche 1 à gauche."
)

_FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"


@dataclass(frozen=True)
class Figure:
    key: str  # identifiant HTML stable (lettres, chiffres, tirets)
    title: str
    alt: str  # texte alternatif complet : ce que le schéma montre, sans le voir
    caption: str
    svg: str
    official: bool = False  # True seulement pour un schéma recopié d'un document officiel


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def step_flow_svg(steps: tuple[tuple[str, str], ...], *, width: int = 320) -> str:
    """Étapes (titre, détail) empilées verticalement et reliées par des flèches."""
    box_x, box_w, gap = 10, width - 20, 26
    parts: list[str] = []
    y = 10
    for index, (label, detail) in enumerate(steps, start=1):
        detail_lines = _wrap(detail, 40)
        box_h = 30 + 16 * len(detail_lines)
        parts.append(
            f'<rect x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="8" '
            f'fill="#f4f6fb" stroke="#33415c" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{box_x + 12}" y="{y + 20}" font-weight="700" font-size="14">'
            f"{index}. {escape(label)}</text>"
        )
        for line_index, line in enumerate(detail_lines):
            parts.append(
                f'<text x="{box_x + 12}" y="{y + 38 + 16 * line_index}" font-size="12.5">'
                f"{escape(line)}</text>"
            )
        y += box_h
        if index < len(steps):
            mid = width // 2
            parts.append(
                f'<path d="M{mid} {y + 2} V{y + gap - 6}" stroke="#33415c" stroke-width="2"/>'
                f'<path d="M{mid - 6} {y + gap - 10} L{mid} {y + gap - 2} L{mid + 6} {y + gap - 10}" '
                f'fill="none" stroke="#33415c" stroke-width="2"/>'
            )
            y += gap
    height = y + 10
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{_FONT}" fill="#1b2333">' + "".join(parts) + "</svg>"
    )


def _wire_base(wire: str) -> str:
    return wire.removeprefix("blanc-")


def connector_pins_svg(wires: tuple[str, ...], *, label: str) -> str:
    """Rangée de 8 broches numérotées ; chaque fil est coloré depuis `WIRE_COLORS`."""
    if len(wires) != 8:
        raise ValueError("Une fiche 8P8C compte exactement 8 broches.")
    pin_w, pin_gap, left, top = 30, 6, 14, 34
    width = left * 2 + 8 * pin_w + 7 * pin_gap
    parts = [
        (f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" '
        f'font-size="14">{escape(label)}</text>'),
        (f'<rect x="4" y="{top - 8}" width="{width - 8}" height="126" rx="10" fill="none" '
        f'stroke="#33415c" stroke-width="1.5"/>'),
    ]
    for index, wire in enumerate(wires):
        base = _wire_base(wire)
        if base not in WIRE_COLORS:
            raise ValueError(f"Couleur de fil inconnue : {wire}")
        color = WIRE_COLORS[base]
        x = left + index * (pin_w + pin_gap)
        parts.append(
            f'<text x="{x + pin_w // 2}" y="{top + 12}" text-anchor="middle" '
            f'font-size="13" font-weight="700">{index + 1}</text>'
        )
        parts.append(
            f'<rect data-pin="{index + 1}" data-wire="{escape(wire)}" x="{x}" y="{top + 20}" '
            f'width="{pin_w}" height="90" rx="4" '
            f'fill="{"#ffffff" if wire.startswith("blanc-") else color}" '
            f'stroke="{color}" stroke-width="2"/>'
        )
        if wire.startswith("blanc-"):
            for stripe in range(4):
                sy = top + 30 + stripe * 22
                parts.append(
                    f'<rect x="{x + 2}" y="{sy}" width="{pin_w - 4}" height="9" fill="{color}"/>'
                )
    return (
        f'<svg viewBox="0 0 {width} {top + 124}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{_FONT}" fill="#1b2333">' + "".join(parts) + "</svg>"
    )


def pin_table(wires: tuple[str, ...]) -> list[tuple[int, str]]:
    """Référence texte d'une rangée de broches (toujours affichée avec le schéma)."""
    return [(index, wire) for index, wire in enumerate(wires, start=1)]


def validate_figure(figure: Figure) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"[a-z0-9-]+", figure.key):
        errors.append("Identifiant de figure invalide.")
    if len(figure.alt.strip()) < 40:
        errors.append("Texte alternatif absent ou trop court (40 caractères minimum).")
    if not figure.caption.strip():
        errors.append("Légende absente.")
    if "viewBox=" not in figure.svg:
        errors.append("SVG sans viewBox : pas de mise à l'échelle mobile.")
    lowered = figure.svg.lower()
    if "<script" in lowered or re.search(r"\son\w+\s*=", lowered):
        errors.append("SVG contenant du script.")
    if "href=" in lowered or "url(http" in lowered:
        errors.append("SVG appelant une ressource externe.")
    if not figure.official and "officiel" in figure.caption.lower().replace("non officiel", ""):
        errors.append("Légende présentant comme officiel un schéma qui ne l'est pas.")
    return errors


def render_figure(figure: Figure) -> Markup:
    """Figure accessible : le SVG reçoit `role="img"`, un `<title>` et une `<desc>`."""
    errors = validate_figure(figure)
    if errors:
        raise ValueError(f"Figure {figure.key} refusée : {' '.join(errors)}")
    title_id, desc_id = f"fig-{figure.key}-title", f"fig-{figure.key}-desc"
    svg = figure.svg.replace(
        "<svg ",
        f'<svg role="img" aria-labelledby="{title_id} {desc_id}" ',
        1,
    )
    head_end = svg.index(">") + 1
    svg = (
        svg[:head_end]
        + f'<title id="{title_id}">{escape(figure.title)}</title>'
        + f'<desc id="{desc_id}">{escape(figure.alt)}</desc>'
        + svg[head_end:]
    )
    mention = "" if figure.official else " <span class=\"text-muted\">(schéma non officiel)</span>"
    return Markup(
        f'<figure class="jc-tech-figure" id="fig-{figure.key}">{svg}'
        f"<figcaption>{escape(figure.caption)}{mention}</figcaption></figure>"
    )


DIAGNOSTIC_METHOD_FIGURE = Figure(
    key="demarche-intervention",
    title="Démarche d'une intervention écrite",
    alt=(
        "Six étapes reliées par des flèches : 1 observer et relever les symptômes, "
        "2 formuler des hypothèses, 3 tester de la plus simple à la plus invasive, "
        "4 agir avec autorisation, 5 vérifier le résultat, 6 rédiger le compte rendu."
    ),
    caption=(
        "Démarche attendue dans une réponse écrite de technicien : chaque étape est "
        "nommée et justifiée."
    ),
    svg=step_flow_svg(
        (
            ("Observer", "Relever les symptômes exacts, les messages et ce qui a changé."),
            ("Hypothèses", "Lister les causes possibles, de la plus probable à la moins probable."),
            ("Tester", "Du test le plus simple et le moins risqué au plus invasif."),
            ("Agir", "Corriger la cause retenue, avec l'accord du client si l'action est risquée."),
            ("Vérifier", "Contrôler que le problème a disparu et que rien d'autre n'est touché."),
            ("Compte rendu", "Écrire constat, tests, cause, action, résultat et conseil."),
        )
    ),
)


# --- Helpers ajoutés au ticket #193 (PR06) ----------------------------------------------
# Mêmes règles que ci-dessus : chaque figure est dessinée depuis des données (tuples) que
# les tests du ticket contrôlent ; aucune information ne repose sur la seule couleur.

_MONO = "ui-monospace, 'DejaVu Sans Mono', Consolas, monospace"


def _svg(width: int, height: int, parts: list[str], *, font: str = _FONT) -> str:
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{font}" fill="#1b2333">' + "".join(parts) + "</svg>"
    )


def _arrow_down(x: int, y1: int, y2: int) -> str:
    return (
        f'<path d="M{x} {y1} V{y2 - 4}" stroke="#33415c" stroke-width="2"/>'
        f'<path d="M{x - 6} {y2 - 10} L{x} {y2 - 2} L{x + 6} {y2 - 10}" fill="none" '
        f'stroke="#33415c" stroke-width="2"/>'
    )


def _arrow_right(x1: int, x2: int, y: int) -> str:
    return (
        f'<path d="M{x1} {y} H{x2 - 4}" stroke="#33415c" stroke-width="2"/>'
        f'<path d="M{x2 - 10} {y - 6} L{x2 - 2} {y} L{x2 - 10} {y + 6}" fill="none" '
        f'stroke="#33415c" stroke-width="2"/>'
    )


def _text_lines(x: int, y: int, lines: list[str], *, size: float = 12.5, weight: str = "400",
                step: int = 16, anchor: str = "start") -> str:
    return "".join(
        f'<text x="{x}" y="{y + step * i}" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


def decision_tree_svg(
    questions: tuple[tuple[str, str], ...], final: str, *, width: int = 380
) -> str:
    """Arbre décisionnel linéaire : chaque question (colonne de gauche) mène, si la réponse
    est « non », à une piste (colonne de droite) et, si « oui », à la question suivante.
    `final` est la conclusion quand toutes les réponses sont « oui »."""
    left_x, left_w = 6, 178
    right_x = left_x + left_w + 26
    right_w = width - right_x - 6
    parts: list[str] = []
    y = 8
    for index, (question, if_no) in enumerate(questions, start=1):
        q_lines = _wrap(question, 20)
        n_lines = _wrap(if_no, 22)
        box_h = max(22 + 15 * len(q_lines), 18 + 15 * len(n_lines)) + 6
        parts.append(
            f'<rect data-step="{index}" x="{left_x}" y="{y}" width="{left_w}" height="{box_h}" '
            f'rx="8" fill="#f4f6fb" stroke="#33415c" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(left_x + 8, y + 18, [f"{index}. {q_lines[0]}", *q_lines[1:]],
                                 size=12, weight="700", step=15))
        parts.append(
            f'<rect x="{right_x}" y="{y}" width="{right_w}" height="{box_h}" rx="8" '
            f'fill="#ffffff" stroke="#33415c" stroke-width="1.5" stroke-dasharray="5 3"/>'
        )
        parts.append(_text_lines(right_x + 8, y + 18, n_lines, size=11.5, step=15))
        mid = y + box_h // 2
        parts.append(_arrow_right(left_x + left_w, right_x, mid))
        parts.append(
            f'<text x="{left_x + left_w + 13}" y="{mid + 15}" font-size="10.5" font-weight="700" '
            f'text-anchor="middle">NON</text>'
        )
        y += box_h
        cx = left_x + left_w // 2
        parts.append(_arrow_down(cx, y + 2, y + 26))
        parts.append(f'<text x="{cx + 8}" y="{y + 18}" font-size="10.5" font-weight="700">OUI</text>')
        y += 26
    final_lines = _wrap(final, 50)
    final_h = 14 + 16 * len(final_lines)
    parts.append(
        f'<rect x="{left_x}" y="{y}" width="{width - 12}" height="{final_h}" rx="8" '
        f'fill="#e9f5ec" stroke="#2e6b3a" stroke-width="1.5"/>'
    )
    parts.append(_text_lines(left_x + 8, y + 18, final_lines, size=12, weight="700"))
    return _svg(width, y + final_h + 8, parts)


def pin_columns_svg(
    pins: tuple[tuple[int, str, str], ...], *, title: str, rows: int, pin_label: str = "Broche"
) -> str:
    """Connecteur à deux rangées vu comme un tableau : colonne de gauche = broches 1 à
    `rows`, colonne de droite = broches `rows + 1` à `2 × rows` (la broche `rows + 1` est en
    face de la broche 1). Chaque broche porte son numéro, son signal en texte et sa couleur
    de fil en texte ; la pastille de couleur n'est qu'un repère (lecture en noir et blanc)."""
    if len(pins) != 2 * rows:
        raise ValueError("Le connecteur doit compter exactement 2 × rows broches.")
    numbers = [p[0] for p in pins]
    if numbers != list(range(1, 2 * rows + 1)):
        raise ValueError("Les broches doivent être numérotées de 1 à 2 × rows, dans l'ordre.")
    width, col_w, top, row_h = 380, 184, 40, 24
    palette = {
        "orange": "#e8740c", "rouge": "#c62828", "noir": "#1b1b1b", "gris": "#8a8f98",
        "violet": "#6a3fa0", "jaune": "#e3c100", "bleu": "#1f5fbf", "vert": "#2e8b3a",
        "blanc": "#ffffff", "—": "#ffffff",
    }
    parts = [
        (f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="14">'
         f"{escape(title)}</text>"),
        (f'<text x="{width // 2}" y="33" text-anchor="middle" font-size="11">'
         f"{escape(pin_label)} · signal · couleur du fil</text>"),
    ]
    for index, (number, signal, color) in enumerate(pins):
        column, row = divmod(index, rows)
        x = 4 + column * (col_w + 4)
        y = top + row * row_h
        parts.append(
            f'<rect data-pin="{number}" data-signal="{escape(signal)}" data-color="{escape(color)}" '
            f'x="{x}" y="{y}" width="{col_w}" height="{row_h - 3}" rx="4" fill="#f4f6fb" '
            f'stroke="#33415c" stroke-width="1"/>'
        )
        parts.append(
            f'<rect x="{x + 4}" y="{y + 4}" width="13" height="{row_h - 11}" rx="2" '
            f'fill="{palette.get(color, "#ffffff")}" stroke="#33415c" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x + 22}" y="{y + 15}" font-size="11.5" font-weight="700">{number}</text>'
            f'<text x="{x + 44}" y="{y + 15}" font-size="11.5">{escape(signal)}</text>'
            f'<text x="{x + col_w - 5}" y="{y + 15}" font-size="10.5" text-anchor="end">'
            f"{escape(color)}</text>"
        )
    return _svg(width, top + rows * row_h + 6, parts)


def line_chart_svg(
    points: tuple[tuple[int, int], ...], *, threshold: int, x_label: str, y_label: str,
    threshold_label: str, y_max: int,
) -> str:
    """Courbe simple (x croissant) avec une ligne de seuil pointillée ; chaque point porte
    sa valeur en texte, pour une lecture sans couleur ni grille fine."""
    width, height = 380, 230
    left, right, top, bottom = 44, 12, 18, 40
    plot_w, plot_h = width - left - right, height - top - bottom
    x_max = max(x for x, _ in points) or 1

    def sx(x: int) -> float:
        return left + plot_w * x / x_max

    def sy(y: int) -> float:
        return top + plot_h * (1 - y / y_max)

    parts = [
        f'<path d="M{left} {top} V{top + plot_h} H{left + plot_w}" fill="none" stroke="#33415c" stroke-width="1.5"/>',
        f'<path d="M{left} {sy(threshold):.1f} H{left + plot_w}" stroke="#b3261e" stroke-width="1.5" stroke-dasharray="6 4"/>',
        f'<text x="{left + 6}" y="{sy(threshold) - 5:.1f}" font-size="11" font-weight="700">{escape(threshold_label)}</text>',
        f'<text x="{left + plot_w / 2:.0f}" y="{height - 6}" font-size="11.5" text-anchor="middle">{escape(x_label)}</text>',
        f'<text x="12" y="{top + plot_h / 2:.0f}" font-size="11.5" text-anchor="middle" transform="rotate(-90 12 {top + plot_h / 2:.0f})">{escape(y_label)}</text>',
    ]
    for tick in range(0, y_max + 1, 20):
        parts.append(f'<text x="{left - 6}" y="{sy(tick) + 4:.1f}" font-size="10" text-anchor="end">{tick}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f} {sy(y):.1f}" for i, (x, y) in enumerate(points))
    parts.append(f'<path d="{path}" fill="none" stroke="#1f5fbf" stroke-width="2.5"/>')
    for x, y in points:
        parts.append(
            f'<circle data-x="{x}" data-y="{y}" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.5" fill="#1f5fbf"/>'
            f'<text x="{sx(x):.1f}" y="{sy(y) - 8:.1f}" font-size="10" text-anchor="middle">{y}</text>'
            f'<text x="{sx(x):.1f}" y="{top + plot_h + 14}" font-size="10" text-anchor="middle">{x}</text>'
        )
    return _svg(width, height, parts)


def screen_svg(lines: tuple[str, ...], *, label: str) -> str:
    """Écran texte fictif (POST, firmware, console) : texte clair sur fond sombre, police à
    chasse fixe. `label` (ex. « capture fictive ») est toujours affiché sous l'écran."""
    width, line_h, top = 380, 15, 14
    height = top + line_h * len(lines) + 34
    parts = [
        f'<rect x="2" y="2" width="{width - 4}" height="{height - 26}" rx="6" fill="#111827" stroke="#33415c" stroke-width="2"/>',
    ]
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="12" y="{top + 12 + line_h * i}" font-size="10.5" fill="#e5e7eb" '
            f'font-family="{_MONO}" xml:space="preserve">{escape(line)}</text>'
        )
    parts.append(
        f'<text x="{width // 2}" y="{height - 8}" font-size="11" text-anchor="middle" '
        f'font-style="italic">{escape(label)}</text>'
    )
    return _svg(width, height, parts)


def two_lists_svg(left_title: str, left: tuple[str, ...], right_title: str,
                  right: tuple[str, ...]) -> str:
    """Deux listes côte à côte (ex. « on garde » / « on retire »), avec un symbole texte
    (✓ / ✗) devant chaque élément : la distinction ne repose pas sur la couleur."""
    width, col_w, top = 380, 182, 36
    rows = max(len(left), len(right))
    line_h = 34
    height = top + rows * line_h + 10
    parts: list[str] = []
    for column, (title, items, mark, fill) in enumerate(
        ((left_title, left, "✓", "#e9f5ec"), (right_title, right, "✗", "#fbecec"))
    ):
        x = 6 + column * (col_w + 4)
        parts.append(
            f'<rect x="{x}" y="4" width="{col_w}" height="{height - 8}" rx="8" fill="{fill}" '
            f'stroke="#33415c" stroke-width="1.5"/>'
            f'<text x="{x + col_w // 2}" y="24" text-anchor="middle" font-weight="700" font-size="13">'
            f"{escape(title)}</text>"
        )
        for i, item in enumerate(items):
            wrapped = _wrap(item, 24)
            parts.append(
                f'<text x="{x + 8}" y="{top + 14 + line_h * i}" font-size="12" font-weight="700">{mark}</text>'
            )
            parts.append(_text_lines(x + 24, top + 14 + line_h * i, wrapped, size=11.5, step=13))
    return _svg(width, height, parts)


@dataclass(frozen=True)
class BoardPart:
    key: str
    label: str
    x: int
    y: int
    w: int
    h: int
    detail: str = ""


def board_plan_svg(parts_data: tuple[BoardPart, ...], *, width: int = 380, height: int = 400,
                   title: str) -> str:
    """Plan schématique d'une carte (vue de dessus) : chaque zone est un rectangle
    étiqueté, positionné depuis les données ; ce n'est pas un plan à l'échelle."""
    parts = [
        (f'<rect x="2" y="22" width="{width - 4}" height="{height - 24}" rx="6" fill="#eef3ee" '
         f'stroke="#2e6b3a" stroke-width="2"/>'),
        (f'<text x="{width // 2}" y="15" text-anchor="middle" font-size="13" font-weight="700">'
         f"{escape(title)}</text>"),
    ]
    for part in parts_data:
        parts.append(
            f'<rect data-part="{escape(part.key)}" x="{part.x}" y="{part.y}" width="{part.w}" '
            f'height="{part.h}" rx="4" fill="#ffffff" stroke="#33415c" stroke-width="1.5"/>'
        )
        lines = _wrap(part.label, max(6, part.w // 7))
        cy = part.y + part.h / 2 - (len(lines) - 1) * 6.5 + 4
        for i, line in enumerate(lines):
            parts.append(
                f'<text x="{part.x + part.w / 2:.0f}" y="{cy + 13 * i:.0f}" font-size="11" '
                f'font-weight="700" text-anchor="middle">{escape(line)}</text>'
            )
    return _svg(width, height, parts)

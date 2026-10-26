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

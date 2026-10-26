"""PR01 « Structure d'un PC et identification des composants » — données techniques de
référence, relevés d'inventaire fictifs et schémas SVG (ticket #202).

Tout est construit **depuis des données** de ce module (tuples), contrôlées par
`tests/test_ticket202_ampcr_pratique_pr01.py` :

- formats de carte mère (`FORM_FACTORS`) : spécifications ATX 2.x et microATX (Intel),
  Mini-ITX (VIA) — dimensions maximales et nombre d'emplacements d'extension ;
- barrettes mémoire (`MEMORY_MODULES`) : normes JEDEC DDR3, DDR4, DDR5 (nombre de contacts,
  tension nominale) ;
- générations PCI Express (`PCIE_GENERATIONS`) : débit par ligne **calculé** depuis le débit
  de transfert et le codage 128b/130b (PCI-SIG) ;
- USB (`USB_SPEEDS`) : USB-IF (USB 2.0, USB 3.2 Gen 1/Gen 2/Gen 2x2, USB4) ;
- connecteurs d'alimentation : repris du cours PR06 (`OTHER_CONNECTORS`, guide ATX12V et
  spécification PCIe CEM), au niveau de l'identification seulement (le détail est en PR02) ;
- relevés d'inventaire (`lsblk_lines`, `memory_cim_lines`) : tailles en octets converties
  **par calcul** en unités binaires, comme le font les outils réels.

Le plan de carte mère, le boîtier, le panneau arrière, les fiches produits et les relevés sont
des **supports fictifs** (mention affichée) : ils ne reproduisent aucun produit réel. Aucun
schéma ne vient d'une image générée.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr06_figures import OTHER_CONNECTORS
from app.v1.ampcr_pratique_visuals import (
    BoardPart,
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR24)

# =============================================================================================
# 1. Données de référence
# =============================================================================================


@dataclass(frozen=True)
class FormFactor:
    name: str
    width_mm: int  # côté de la plaque d'E/S arrière
    depth_mm: int
    max_slots: int  # emplacements d'extension au plus
    note: str


FORM_FACTORS: tuple[FormFactor, ...] = (
    FormFactor("ATX", 305, 244, 7, "PC de bureau et tours classiques"),
    FormFactor("microATX", 244, 244, 4, "mini-tours, PC de bureau compacts"),
    FormFactor("Mini-ITX", 170, 170, 1, "petits boîtiers, PC de salon"),
)
FORM_FACTORS_BY_NAME = {f.name: f for f in FORM_FACTORS}

# Une carte entre dans un boîtier prévu pour son format ou pour un format PLUS GRAND (mêmes
# points de fixation de référence, plaque d'E/S au même endroit) — jamais l'inverse.
_FORM_ORDER = ("Mini-ITX", "microATX", "ATX")


def board_fits_case(board: str, case: str) -> bool:
    return _FORM_ORDER.index(board) <= _FORM_ORDER.index(case)


@dataclass(frozen=True)
class MemoryModule:
    generation: str
    form: str  # « DIMM » (PC de bureau) | « SO-DIMM » (portable, mini-PC)
    contacts: int
    voltage: str  # tension nominale JEDEC


MEMORY_MODULES: tuple[MemoryModule, ...] = (
    MemoryModule("DDR3", "DIMM", 240, "1,5 V (DDR3L : 1,35 V)"),
    MemoryModule("DDR3", "SO-DIMM", 204, "1,5 V (DDR3L : 1,35 V)"),
    MemoryModule("DDR4", "DIMM", 288, "1,2 V"),
    MemoryModule("DDR4", "SO-DIMM", 260, "1,2 V"),
    MemoryModule("DDR5", "DIMM", 288, "1,1 V"),
    MemoryModule("DDR5", "SO-DIMM", 262, "1,1 V"),
)
DIMM_LENGTH_MM = 133.35  # longueur d'une barrette DIMM DDR3/DDR4/DDR5
SODIMM_LENGTH_MM = 69.6  # longueur d'une barrette SO-DIMM DDR4/DDR5 (DDR3 : 67,6 mm)


def memory_module(generation: str, form: str) -> MemoryModule:
    return next(m for m in MEMORY_MODULES if m.generation == generation and m.form == form)


# Générations PCI Express : (version, débit de transfert en GT/s). Codage 128b/130b à partir
# de la version 3.0 (8b/10b avant) ; débit utile par ligne et par sens calculé ci-dessous.
PCIE_GENERATIONS: tuple[tuple[str, int], ...] = (("3.0", 8), ("4.0", 16), ("5.0", 32))


def pcie_lane_gbytes(transfer_gt: int) -> float:
    """Débit utile d'une ligne PCIe (Go/s, un sens) en codage 128b/130b."""
    return transfer_gt * 128 / 130 / 8


def pcie_link_gbytes(transfer_gt: int, lanes: int) -> float:
    return pcie_lane_gbytes(transfer_gt) * lanes


def fr_number(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


SATA3_GBITS = 6  # SATA révision 3 : 6 Gbit/s sur la liaison
SATA3_USEFUL_MBYTES = 600  # codage 8b/10b : 6000 Mbit/s × 8/10 / 8 = 600 Mo/s utiles

# USB : (nom actuel, ancien nom courant, débit en Gbit/s, connecteurs possibles).
USB_SPEEDS: tuple[tuple[str, str, float, str], ...] = (
    ("USB 2.0", "Hi-Speed", 0.48, "USB-A, USB-C, micro-B"),
    ("USB 3.2 Gen 1", "USB 3.0 / USB 3.1 Gen 1", 5, "USB-A, USB-C"),
    ("USB 3.2 Gen 2", "USB 3.1 Gen 2", 10, "USB-A, USB-C"),
    ("USB 3.2 Gen 2x2", "—", 20, "USB-C uniquement"),
    ("USB4", "—", 40, "USB-C uniquement (20 ou 40 Gbit/s selon le port)"),
)

# Prises audio jack 3,5 mm d'un PC de bureau (code couleur PC 99).
AUDIO_JACKS: tuple[tuple[str, str], ...] = (
    ("vert", "sortie casque ou haut-parleurs"),
    ("rose", "entrée microphone"),
    ("bleu clair", "entrée ligne (source audio externe)"),
)

# Connecteurs d'alimentation à reconnaître (identification ; brochage et puissance : PR02).
POWER_CONNECTORS: tuple[tuple[str, str, str], ...] = (
    ("ATX 24 broches (souvent 20+4)", "carte mère", "Alimentation principale de la carte mère"),
    ("EPS 8 broches (souvent 4+4), marqué « CPU »", "carte mère, près du socket", "Alimente le processeur via le VRM"),
    *((name, "périphérique", use) for name, _pins, _power, use in OTHER_CONNECTORS),
)

# =============================================================================================
# 2. Relevés d'inventaire fictifs (calculés)
# =============================================================================================


def binary_size(size_bytes: int) -> str:
    """Taille affichée par `lsblk` (unités binaires : 1K = 1024 octets, une décimale)."""
    value = float(size_bytes)
    for unit in ("B", "K", "M", "G", "T"):
        if value < 1024 or unit == "T":
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    raise AssertionError  # pragma: no cover


@dataclass(frozen=True)
class BlockDevice:
    name: str
    tran: str  # sata | nvme | usb
    rota: int  # 1 = disque à plateaux, 0 = sans pièce mobile
    size_bytes: int  # capacité annoncée en octets (fabricant : 1 Go = 10⁹ octets)
    model: str


INVENTORY_DISKS: tuple[BlockDevice, ...] = (
    BlockDevice("sda", "sata", 1, 2 * 10**12, "HDD 3,5 2 To (fictif)"),
    BlockDevice("sdb", "sata", 0, 500 * 10**9, "SSD 2,5 500 Go (fictif)"),
    BlockDevice("nvme0n1", "nvme", 0, 1 * 10**12, "SSD M.2 1 To (fictif)"),
    BlockDevice("sdc", "usb", 0, 64 * 10**9, "Clé USB 64 Go (fictive)"),
)


def lsblk_lines(disks: tuple[BlockDevice, ...]) -> tuple[str, ...]:
    """Sortie de `lsblk -d -o NAME,TRAN,ROTA,SIZE,MODEL` (disques seuls)."""
    header = f"{'NAME':<8} {'TRAN':<5}{'ROTA':>4} {'SIZE':>6} MODEL"
    rows = [
        f"{d.name:<8} {d.tran:<5}{d.rota:>4} {binary_size(d.size_bytes):>6} {d.model}" for d in disks
    ]
    return ("$ lsblk -d -o NAME,TRAN,ROTA,SIZE,MODEL", header, *rows)


@dataclass(frozen=True)
class MemorySlot:
    locator: str
    capacity_gib: int  # 0 = emplacement vide ou barrette non détectée
    speed: int  # MT/s


def memory_cim_lines(slots: tuple[MemorySlot, ...]) -> tuple[str, ...]:
    """Sortie PowerShell (simplifiée) de
    `Get-CimInstance Win32_PhysicalMemory | Format-Table DeviceLocator, Capacity, Speed` :
    une ligne par barrette **détectée**, capacité en octets."""
    detected = [s for s in slots if s.capacity_gib]
    lines = [
        "PS> Get-CimInstance Win32_PhysicalMemory |",
        ">>   Format-Table DeviceLocator, Capacity, Speed",
        "",
        f"{'DeviceLocator':<14}{'Capacity':>12}{'Speed':>7}",
        f"{'-------------':<14}{'--------':>12}{'-----':>7}",
    ]
    lines += [f"{s.locator:<14}{s.capacity_gib * 2**30:>12}{s.speed:>7}" for s in detected]
    return tuple(lines)


# Cas 2 : deux barrettes DDR5 de 8 Go installées (A2 et B2), une seule détectée.
CASE2_SLOTS: tuple[MemorySlot, ...] = (
    MemorySlot("DIMM_A1", 0, 0),
    MemorySlot("DIMM_A2", 8, 4800),
    MemorySlot("DIMM_B1", 0, 0),
    MemorySlot("DIMM_B2", 0, 0),
)
CASE2_INSTALLED_GIB = 16

# =============================================================================================
# 3. Schémas
# =============================================================================================


@dataclass(frozen=True)
class Node:
    key: str
    lines: tuple[str, ...]
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class Link:
    a: str
    b: str
    label: str
    side: str  # « v » : bas de a → haut de b ; « h » : côté de a → côté de b


def _anchor(node: Node, other: Node, side: str) -> tuple[float, float]:
    if side == "v":
        y = node.y + node.h if other.y > node.y else node.y
        return node.x + node.w / 2, y
    x = node.x + node.w if other.x > node.x else node.x
    return x, node.y + node.h / 2


def block_diagram_svg(nodes: tuple[Node, ...], links: tuple[Link, ...], *, width: int,
                      height: int, footer: str = "") -> str:
    """Schéma-bloc : chaque nœud est une case titrée ; chaque liaison est un trait plein
    portant son libellé (bus, interface) sur fond blanc, lisible sans couleur."""
    by_key = {n.key: n for n in nodes}
    parts: list[str] = []
    for link in links:
        a, b = by_key[link.a], by_key[link.b]
        x1, y1 = _anchor(a, b, link.side)
        x2, y2 = _anchor(b, a, link.side)
        parts.append(
            f'<path data-link="{escape(link.a)}-{escape(link.b)}" d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" '
            f'stroke="{_STROKE}" stroke-width="3"/>'
        )
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        label_w = 6.4 * len(link.label) + 8
        parts.append(
            f'<rect x="{mx - label_w / 2:.0f}" y="{my - 9:.0f}" width="{label_w:.0f}" height="16" rx="3" '
            f'fill="#ffffff" stroke="{_STROKE}" stroke-width="0.8"/>'
            f'<text x="{mx:.0f}" y="{my + 3:.0f}" font-size="10.5" text-anchor="middle">{escape(link.label)}</text>'
        )
    for node in nodes:
        parts.append(
            f'<rect data-node="{escape(node.key)}" x="{node.x}" y="{node.y}" width="{node.w}" '
            f'height="{node.h}" rx="8" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        top = node.y + node.h / 2 - (len(node.lines) - 1) * 7 + 4
        for i, line in enumerate(node.lines):
            parts.append(
                f'<text x="{node.x + node.w / 2:.0f}" y="{top + 14 * i:.0f}" font-size="{12 if i == 0 else 10.5}" '
                f'font-weight="{700 if i == 0 else 400}" text-anchor="middle">{escape(line)}</text>'
            )
    if footer:
        parts.append(_text_lines(6, height - 8, [footer], size=10.5))
    return _svg(width, height, parts)


# --- 3.1 Cheminement des données -------------------------------------------------------------

DATA_PATH_NODES: tuple[Node, ...] = (
    Node("gpu", ("Carte graphique", "→ écran"), 6, 8, 150, 46),
    Node("nvme", ("SSD NVMe", "emplacement M.2_1"), 224, 8, 150, 46),
    Node("ram", ("Mémoire vive", "barrettes DDR"), 6, 126, 100, 56),
    Node("cpu", ("Processeur", "contrôleur mémoire", "graphique intégré ?"), 150, 116, 150, 76),
    Node("chipset", ("Chipset", "contrôleurs d'E/S"), 150, 262, 150, 52),
    Node("sata", ("Ports SATA", "HDD, SSD 2,5\""), 6, 366, 86, 48),
    Node("usb", ("Ports USB", "clavier, clé…"), 100, 366, 86, 48),
    Node("lan", ("Réseau,", "audio, Wi-Fi"), 194, 366, 86, 48),
    Node("m2b", ("M.2_2,", "PCIe x1/x4"), 288, 366, 86, 48),
)
DATA_PATH_LINKS: tuple[Link, ...] = (
    Link("gpu", "cpu", "PCIe x16", "v"),
    Link("nvme", "cpu", "PCIe x4", "v"),
    Link("ram", "cpu", "DDR", "h"),
    Link("cpu", "chipset", "liaison CPU-chipset", "v"),
    Link("chipset", "sata", "SATA", "v"),
    Link("chipset", "usb", "USB", "v"),
    Link("chipset", "lan", "PCIe", "v"),
    Link("chipset", "m2b", "PCIe", "v"),
)

DATA_PATH_FIGURE = Figure(
    key="pr01-cheminement-donnees",
    title="Cheminement des données dans un PC de bureau récent",
    alt=(
        "Schéma-bloc. Le processeur est au centre. Il est relié directement à la mémoire vive "
        "(canaux DDR), à la carte graphique (PCIe x16, qui alimente l'écran) et au SSD NVMe de "
        "l'emplacement M.2_1 (PCIe x4). Une liaison processeur-chipset le relie au chipset, qui "
        "gère les ports SATA (disques durs, SSD 2,5 pouces), les ports USB, le réseau, l'audio "
        "et le Wi-Fi (PCIe) et un second emplacement M.2 ou des emplacements PCIe x1/x4."
    ),
    caption=(
        "Répartition typique d'une plateforme récente : les liaisons les plus rapides (mémoire, "
        "carte graphique, premier M.2) partent du processeur ; le chipset gère les autres "
        "entrées-sorties et partage sa liaison avec le processeur. Le manuel de la carte indique "
        "quels ports dépendent du processeur ou du chipset. Le bloc d'alimentation alimente "
        "tout mais ne transporte aucune donnée."
    ),
    svg=block_diagram_svg(DATA_PATH_NODES, DATA_PATH_LINKS, width=380, height=440,
                          footer="Support fictif simplifié — non à l'échelle."),
)

# --- 3.2 Formats de carte mère (à l'échelle) ---------------------------------------------------


def form_factor_svg() -> str:
    left, top, scale = 12, 30, 1.0
    width = int(left * 2 + FORM_FACTORS_BY_NAME["ATX"].width_mm * scale)
    height = int(top + FORM_FACTORS_BY_NAME["ATX"].depth_mm * scale + 34)
    dashes = {"ATX": "", "microATX": ' stroke-dasharray="8 4"', "Mini-ITX": ' stroke-dasharray="3 3"'}
    parts = [
        _text_lines(width // 2, 16, ["Formats de carte mère à l'échelle"], size=12,
                    weight="700", anchor="middle"),
        f'<rect x="{left - 8}" y="{top}" width="6" height="60" fill="{_STROKE}"/>',
        _text_lines(left - 2, top + 76, ["E/S"], size=9.5, weight="700"),
    ]
    for form in FORM_FACTORS:  # le plus grand d'abord (dessous)
        w, h = form.width_mm * scale, form.depth_mm * scale
        parts.append(
            f'<rect data-form="{escape(form.name)}" data-width-mm="{form.width_mm}" '
            f'data-depth-mm="{form.depth_mm}" x="{left}" y="{top}" width="{w:.0f}" height="{h:.0f}" '
            f'fill="{"#ffffff" if form.name == "ATX" else "none"}" stroke="{_STROKE}" stroke-width="2"'
            f"{dashes[form.name]}/>"
        )
    itx, matx, atx = (FORM_FACTORS_BY_NAME[n] for n in ("Mini-ITX", "microATX", "ATX"))
    parts.append(_text_lines(left + 10, top + 22, [f"Mini-ITX {itx.width_mm} × {itx.depth_mm} mm",
                                                   f"{itx.max_slots} emplacement"], size=11, weight="700"))
    parts.append(_text_lines(left + 10, top + itx.depth_mm + 22,
                             [f"microATX {matx.width_mm} × {matx.depth_mm} mm",
                              f"jusqu'à {matx.max_slots} emplacements"], size=11, weight="700"))
    parts.append(_text_lines(left + matx.width_mm + 6, top + 22,
                             ["ATX", f"{atx.width_mm} ×", f"{atx.depth_mm} mm", f"jusqu'à {atx.max_slots}",
                              "empl."], size=10.5, weight="700"))
    parts.append(_text_lines(left, height - 8, [
        "Trait plein : ATX · tirets : microATX · pointillés : Mini-ITX"], size=10.5))
    return _svg(width, height, parts)


FORM_FACTOR_FIGURE = Figure(
    key="pr01-formats",
    title="Formats de carte mère ATX, microATX et Mini-ITX à l'échelle",
    alt=(
        "Trois rectangles superposés, dessinés à l'échelle et alignés sur le coin de la plaque "
        "d'entrées-sorties arrière : "
        + " ; ".join(f"{f.name} {f.width_mm} × {f.depth_mm} mm, jusqu'à {f.max_slots} emplacement(s) "
                     "d'extension" for f in FORM_FACTORS)
        + ". Le Mini-ITX tient dans le microATX, qui tient dans l'ATX."
    ),
    caption=(
        "Dimensions maximales des spécifications ATX, microATX et Mini-ITX, dessinées à "
        "l'échelle. Les trois formats partagent la position de la plaque d'E/S et des fixations "
        "de référence : une carte plus petite entre dans un boîtier prévu pour un format plus "
        "grand, jamais l'inverse."
    ),
    svg=form_factor_svg(),
)

# --- 3.3 Plan numéroté de carte mère ATX (support fictif) ----------------------------------------

# (numéro, élément, détail d'identification) — légende du plan et réponses du cas 1.
BOARD_PARTS: tuple[tuple[BoardPart, int], ...] = (
    (BoardPart("io", "Plaque d'E/S arrière", 8, 30, 52, 140, "Ports soudés à la carte, accessibles à l'arrière du boîtier."), 1),
    (BoardPart("eps", "Connecteur EPS 8 broches (CPU)", 70, 30, 100, 22, "Alimentation du processeur, en haut à gauche."), 2),
    (BoardPart("vrm", "VRM (étage d'alimentation du processeur)", 70, 58, 26, 112, "Selfs et transistors sous radiateur, autour du socket."), 3),
    (BoardPart("socket", "Socket du processeur", 102, 62, 92, 92, "Support carré à levier ou cadre de maintien."), 4),
    (BoardPart("cpufan", "Connecteur CPU_FAN (4 broches)", 102, 158, 92, 14, "Ventilateur du processeur, près du socket."), 5),
    (BoardPart("ram", "4 emplacements DIMM (A1 A2 B1 B2)", 204, 30, 76, 142, "Longs slots à clips, parallèles, à droite du socket."), 6),
    (BoardPart("atx24", "Connecteur ATX 24 broches", 290, 40, 26, 110, "Le plus gros connecteur, sur le bord droit."), 7),
    (BoardPart("usb3", "Connecteur interne USB 3.x (19 broches)", 324, 40, 48, 50, "Câble des ports USB de la façade."), 8),
    (BoardPart("pcie16", "PCIe x16 (relié au processeur)", 24, 198, 230, 18, "Long slot, le plus proche du processeur, carte graphique."), 9),
    (BoardPart("m21", "Emplacement M.2_1 (processeur)", 24, 226, 150, 16, "Fente plate avec vis ou loquet de maintien."), 10),
    (BoardPart("pcie1", "PCIe x1", 24, 252, 70, 14, "Court slot : carte réseau, carte son…"), 11),
    (BoardPart("pcie4", "PCIe x16 mécanique, x4 électrique (chipset)", 24, 276, 230, 18, "Long slot, mais seulement 4 lignes câblées."), 12),
    (BoardPart("m22", "Emplacement M.2_2 (chipset)", 24, 304, 150, 16, "Second M.2, relié au chipset."), 13),
    (BoardPart("chipset", "Chipset (sous radiateur)", 264, 236, 62, 50, "Puce sous radiateur plat, en bas à droite."), 14),
    (BoardPart("sata", "Ports SATA (données)", 334, 196, 38, 98, "Petits connecteurs en L, souvent coudés, sur le bord."), 15),
    (BoardPart("bios", "Puce du firmware UEFI (mémoire flash)", 186, 304, 54, 30, "Petite puce à 8 pattes, parfois sur support."), 16),
    (BoardPart("cmos", "Pile CMOS (bouton 3 V)", 250, 302, 42, 42, "Pile bouton ronde."), 17),
    (BoardPart("audio", "Connecteur audio de façade (HD_AUDIO)", 8, 334, 80, 24, "En bas à gauche, près de la puce audio."), 18),
    (BoardPart("usb2", "Connecteur interne USB 2.0 (9 broches)", 98, 334, 70, 24, "Ports USB 2.0 de façade ou lecteur de cartes."), 19),
    (BoardPart("panel", "Connecteur de façade (bouton, reset, LED)", 300, 352, 72, 24, "Broches fines ; brochage dans le manuel."), 20),
)


def numbered_board_svg(width: int = 380, height: int = 386) -> str:
    parts = [
        (f'<rect x="2" y="22" width="{width - 4}" height="{height - 24}" rx="6" fill="#eef3ee" '
         f'stroke="#2e6b3a" stroke-width="2"/>'),
        _text_lines(width // 2, 15, ["Carte mère ATX fictive — plan numéroté"], size=12.5,
                    weight="700", anchor="middle"),
    ]
    for part, number in BOARD_PARTS:
        parts.append(
            f'<rect data-part="{escape(part.key)}" data-number="{number}" x="{part.x}" y="{part.y}" '
            f'width="{part.w}" height="{part.h}" rx="3" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{part.x + part.w / 2:.0f}" y="{part.y + part.h / 2 + 5:.0f}" font-size="'
            f'{13 if part.h >= 18 else 11}" font-weight="700" text-anchor="middle">{number}</text>'
        )
    return _svg(width, height, parts)


BOARD_FIGURE = Figure(
    key="pr01-plan-carte-mere",
    title="Plan numéroté d'une carte mère ATX (support fictif)",
    alt=(
        "Plan simplifié d'une carte mère ATX vue de dessus, plaque d'entrées-sorties à gauche, "
        "avec vingt repères numérotés : "
        + " ; ".join(f"{n} {p.label}" for p, n in BOARD_PARTS)
        + ". Ce n'est pas un plan à l'échelle."
    ),
    caption=(
        "Plan numéroté d'une carte mère ATX fictive (non à l'échelle) ; la légende est dans le "
        "tableau qui suit. L'emplacement exact des éléments change d'un modèle à l'autre : le "
        "manuel de la carte fait foi."
    ),
    svg=numbered_board_svg(),
)

# --- 3.4 Intérieur d'une tour (support fictif) ------------------------------------------------

CASE_PARTS: tuple[tuple[BoardPart, int], ...] = (
    (BoardPart("io", "Plaque d'E/S", 300, 34, 28, 86), 1),
    (BoardPart("rearfan", "Ventilateur arrière (extraction)", 334, 34, 40, 64), 2),
    (BoardPart("board", "Carte mère", 120, 34, 172, 250), 3),
    (BoardPart("cooler", "Ventirad du processeur", 170, 60, 80, 70), 4),
    (BoardPart("ram", "Barrettes de RAM", 254, 52, 30, 78), 5),
    (BoardPart("gpu", "Carte graphique", 110, 170, 210, 40), 6),
    (BoardPart("slots", "Équerres des cartes d'extension", 334, 150, 40, 134), 7),
    (BoardPart("frontfan", "Ventilateurs de façade (entrée d'air)", 6, 34, 34, 250), 8),
    (BoardPart("hdd", "Baie 3,5\" (disque dur)", 46, 196, 58, 52), 9),
    (BoardPart("ssd", "Support 2,5\" (SSD SATA)", 46, 252, 58, 32), 10),
    (BoardPart("panel", "Façade : bouton, USB, audio", 46, 34, 58, 70), 11),
    (BoardPart("psu", "Bloc d'alimentation (en bas, à l'arrière)", 210, 296, 164, 54), 12),
    (BoardPart("cables", "Passe-câbles vers l'arrière du plateau", 110, 296, 92, 54), 13),
)


def numbered_case_svg(width: int = 380, height: int = 362) -> str:
    parts = [
        (f'<rect x="2" y="24" width="{width - 4}" height="{height - 26}" rx="6" fill="#f7f7f7" '
         f'stroke="{_STROKE}" stroke-width="2"/>'),
        _text_lines(width // 2, 15, ["Tour ATX fictive — vue côté gauche, panneau retiré"], size=12.5,
                    weight="700", anchor="middle"),
    ]
    for part, number in CASE_PARTS:
        parts.append(
            f'<rect data-part="{escape(part.key)}" data-number="{number}" x="{part.x}" y="{part.y}" '
            f'width="{part.w}" height="{part.h}" rx="3" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<text x="{part.x + part.w / 2:.0f}" y="{part.y + 18}" font-size="13" font-weight="700" '
            f'text-anchor="middle">{number}</text>'
        )
    parts.append(_text_lines(8, height - 6, ["avant ←", ""], size=10))
    parts.append(_text_lines(width - 8, height - 6, ["→ arrière"], size=10, anchor="end"))
    return _svg(width, height + 8, parts)


CASE_FIGURE = Figure(
    key="pr01-interieur-tour",
    title="Intérieur d'une tour ATX, vue de côté (support fictif)",
    alt=(
        "Vue de côté d'une tour, façade à gauche, arrière à droite, avec treize repères : "
        + " ; ".join(f"{n} {p.label}" for p, n in CASE_PARTS)
        + ". L'air entre par la façade et sort à l'arrière."
    ),
    caption=(
        "Disposition courante d'une tour ATX (fictive, non à l'échelle) : l'air frais entre par "
        "la façade, traverse le boîtier et ressort à l'arrière ; le bloc d'alimentation est en "
        "bas. Légende dans le tableau qui suit."
    ),
    svg=numbered_case_svg(),
)

# --- 3.5 Panneau arrière (support fictif) -----------------------------------------------------

# (numéro, port, ce qu'on y branche, à quoi le reconnaître)
REAR_PORTS: tuple[tuple[int, str, str, str], ...] = (
    (1, "PS/2 combiné", "ancien clavier ou souris", "Prise ronde à 6 broches, mi-violette mi-verte"),
    (2, "USB 2.0 (×2)", "clavier, souris, imprimante", "USB-A, languette souvent noire ; 480 Mbit/s"),
    (3, "USB 3.2 Gen 1 (×4)", "clé, disque externe", "USB-A, languette souvent bleue ; 5 Gbit/s"),
    (4, "USB 3.2 Gen 2 type C", "SSD externe, smartphone", "USB-C réversible ; marqué 10 Gbit/s"),
    (5, "HDMI", "écran ou téléviseur (si le processeur a une partie graphique)", "Trapèze à 19 contacts"),
    (6, "DisplayPort", "écran (si le processeur a une partie graphique)", "Un coin coupé, loquet"),
    (7, "RJ45 (Ethernet)", "câble réseau vers la prise ou le switch", "Prise 8 contacts, voyants"),
    (8, "Connecteurs d'antenne Wi-Fi", "antennes fournies", "Deux petits pas de vis dorés"),
    (9, "Jacks audio 3,5 mm", "casque (vert), micro (rose), entrée ligne (bleu clair)", "Trois prises rondes colorées"),
    (10, "Sorties de la carte graphique", "écran, quand une carte graphique est installée", "Équerre d'une carte d'extension, sous la plaque d'E/S"),
)


_REAR_SHORT = {
    1: "PS/2", 2: "USB 2.0", 3: "USB 3.2 Gen 1", 4: "USB-C 10 Gbit/s", 5: "HDMI", 6: "DisplayPort",
    7: "RJ45", 8: "Antennes Wi-Fi", 9: "Audio", 10: "Sorties de la carte graphique",
}


def rear_panel_svg(width: int = 380, height: int = 262) -> str:
    boxes = (
        (1, 12, 36, 64, 44), (2, 82, 36, 64, 44), (3, 152, 36, 64, 44), (4, 222, 36, 64, 44),
        (5, 12, 88, 64, 40), (6, 82, 88, 64, 40), (7, 152, 88, 64, 40), (8, 222, 88, 64, 40),
        (9, 292, 36, 44, 92), (10, 12, 184, 356, 40),
    )
    parts = [
        _text_lines(width // 2, 15, ["Arrière d'un PC de bureau fictif"], size=12.5, weight="700", anchor="middle"),
        '<rect x="4" y="28" width="340" height="108" rx="4" fill="#eef3ee" stroke="#2e6b3a" stroke-width="2"/>',
        _text_lines(8, 152, ["Plaque d'E/S de la carte mère"], size=10.5, weight="700"),
        f'<rect x="4" y="176" width="372" height="56" rx="4" fill="#eef1f8" stroke="{_STROKE}" stroke-width="2"/>',
        _text_lines(8, 248, ["Emplacements d'extension : carte graphique"], size=10.5, weight="700"),
    ]
    for number, x, y, w, h in boxes:
        parts.append(
            f'<rect data-port="{number}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#ffffff" '
            f'stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 16}" font-size="13" font-weight="700" text-anchor="middle">{number}</text>'
        )
        short = _wrap(_REAR_SHORT[number], 40 if w > 100 else 9)[:2]
        parts.append(_text_lines(int(x + w / 2), y + 29, short, size=9, step=10, anchor="middle"))
    return _svg(width, height, parts)


REAR_PANEL_FIGURE = Figure(
    key="pr01-panneau-arriere",
    title="Panneau arrière d'un PC de bureau (support fictif)",
    alt=(
        "Arrière d'un PC de bureau avec la plaque d'entrées-sorties de la carte mère en haut et, "
        "en dessous, l'équerre d'une carte graphique. Repères : "
        + " ; ".join(f"{n} {port}" for n, port, _u, _l in REAR_PORTS)
        + "."
    ),
    caption=(
        "Panneau arrière fictif. Quand une carte graphique est installée, l'écran se branche sur "
        "ses sorties (repère 10) : les sorties vidéo de la carte mère (5, 6) ne fonctionnent que "
        "si le processeur a une partie graphique intégrée, et elles sont souvent désactivées en "
        "présence d'une carte graphique. Les couleurs de languette USB sont une habitude, pas une "
        "garantie : le marquage et le manuel font foi."
    ),
    svg=rear_panel_svg(),
)

# --- 3.6 Barrettes DIMM et SO-DIMM (longueurs à l'échelle) -------------------------------------


def _contacts_text(form: str) -> str:
    return ", ".join(f"{m.generation} : {m.contacts}" for m in MEMORY_MODULES if m.form == form)


def memory_modules_svg() -> str:
    scale, left = 2.6, 12
    width = int(left * 2 + DIMM_LENGTH_MM * scale)
    width = max(width, 360)
    parts = [_text_lines(width // 2, 16, ["Barrettes mémoire — longueurs à l'échelle"], size=12.5,
                         weight="700", anchor="middle")]
    rows = (
        ("DIMM (PC de bureau)", DIMM_LENGTH_MM, 30, _contacts_text("DIMM")),
        ("SO-DIMM (portable, mini-PC)", SODIMM_LENGTH_MM, 30, _contacts_text("SO-DIMM")),
    )
    y = 34
    for label, length, height_px, contacts in rows:
        w = length * scale
        parts.append(_text_lines(left, y + 12, [f"{label} — {fr_number(length, 2 if length > 100 else 1)} mm"],
                                 size=11.5, weight="700"))
        y += 20
        parts.append(
            f'<rect data-module="{escape(label)}" data-length-mm="{length}" x="{left}" y="{y}" '
            f'width="{w:.0f}" height="{height_px}" rx="3" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        for i in range(6):
            parts.append(
                f'<rect x="{left + 10 + i * (w - 30) / 6:.0f}" y="{y + 5}" width="{(w - 40) / 8:.0f}" height="12" '
                f'fill="#33415c"/>'
            )
        parts.append(
            f'<rect x="{left}" y="{y + height_px - 6}" width="{w:.0f}" height="6" fill="#c9a227"/>'
            f'<path d="M{left + w * 0.55:.0f} {y + height_px + 1} v-9 h5 v9" fill="#ffffff" stroke="{_STROKE}"/>'
        )
        parts.append(_text_lines(left, y + height_px + 16,
                                 [f"puces · contacts dorés ({contacts})",
                                  "encoche-détrompeur : position propre à chaque génération"],
                                 size=10, step=13))
        y += height_px + 46
    return _svg(width, y, parts)


MEMORY_FIGURE = Figure(
    key="pr01-barrettes",
    title="Barrettes DIMM et SO-DIMM, longueurs à l'échelle",
    alt=(
        f"Deux barrettes dessinées à l'échelle : DIMM de {fr_number(DIMM_LENGTH_MM, 2)} mm pour PC "
        f"de bureau et SO-DIMM d'environ {fr_number(SODIMM_LENGTH_MM)} mm pour portable. Chacune porte "
        "des puces mémoire, une rangée de contacts dorés et une encoche-détrompeur dont la position "
        "dépend de la génération (DDR3, DDR4, DDR5)."
    ),
    caption=(
        "Longueurs normalisées (JEDEC) dessinées à l'échelle ; l'encoche est placée de façon "
        "indicative. Deux barrettes de même format mais de générations différentes n'ont pas "
        "l'encoche au même endroit : elles ne s'insèrent pas dans le même slot."
    ),
    svg=memory_modules_svg(),
)

# --- 3.7 Démarche d'identification -------------------------------------------------------------

IDENTIFY_STEPS: tuple[tuple[str, str], ...] = (
    ("Observer", "Forme, taille, nombre de broches, détrompeur, position sur la carte, inscriptions."),
    ("Nommer", "Le nom exact du composant ou du connecteur (pas « un câble », mais « EPS 8 broches »)."),
    ("Rôle", "Ce qu'il fait dans le PC, en une phrase."),
    ("Relier", "À quoi il est connecté et par quelle liaison (DDR, PCIe, SATA, USB)."),
    ("Vérifier", "Inscription, manuel ou fiche du fabricant, outil d'inventaire."),
    ("Noter", "Inventaire écrit : composant, modèle, caractéristique utile, état."),
)

IDENTIFY_FIGURE = Figure(
    key="pr01-demarche-identification",
    title="Démarche écrite d'identification d'un composant",
    alt=(
        "Six étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(IDENTIFY_STEPS, start=1))
    ),
    caption=(
        "Démarche attendue à l'écrit pour identifier un composant sur un schéma, une photo ou "
        "un inventaire : chaque étape apparaît dans la réponse."
    ),
    svg=step_flow_svg(IDENTIFY_STEPS),
)

# --- 3.8 Arbre de compatibilité -------------------------------------------------------------

COMPATIBILITY_QUESTIONS: tuple[tuple[str, str], ...] = (
    ("Le format physique convient-il ?", "Incompatible : format de carte, taille du module, longueur de carte, hauteur du ventirad."),
    ("Le connecteur et le détrompeur sont-ils les bons ?", "Incompatible : socket, génération DDR, clé M.2, DIMM ou SO-DIMM."),
    ("L'interface électrique est-elle prise en charge ?", "Incompatible : M.2 SATA dans un M.2 NVMe seul, lignes PCIe, chipset."),
    ("L'alimentation suffit-elle ?", "Puissance ou connecteurs PCIe/EPS insuffisants : changer le bloc ou la pièce."),
    ("Firmware, pilote et système suivent-ils ?", "Mise à jour du firmware, pilote ou version de système à prévoir avant le montage."),
)
COMPATIBILITY_FINAL = "Compatible : noter les références vérifiées (fiche, manuel, liste de compatibilité) dans le dossier."

COMPATIBILITY_FIGURE = Figure(
    key="pr01-arbre-compatibilite",
    title="Arbre de contrôle de compatibilité d'une pièce",
    alt=(
        "Arbre de décision en cinq questions ; si la réponse est non, on suit la piste de droite, "
        "si oui, la question suivante : "
        + " ; ".join(f"{i} {q} Si non : {n}" for i, (q, n) in enumerate(COMPATIBILITY_QUESTIONS, start=1))
        + f" Conclusion si tout est oui : {COMPATIBILITY_FINAL}"
    ),
    caption=(
        "Contrôle de compatibilité dans l'ordre : physique, connecteur, interface, alimentation, "
        "logiciel. Une pièce qui « rentre » n'est pas forcément compatible."
    ),
    svg=decision_tree_svg(COMPATIBILITY_QUESTIONS, COMPATIBILITY_FINAL),
)

PR01_FIGURES: tuple[Figure, ...] = (
    IDENTIFY_FIGURE,
    DATA_PATH_FIGURE,
    FORM_FACTOR_FIGURE,
    CASE_FIGURE,
    BOARD_FIGURE,
    MEMORY_FIGURE,
    REAR_PANEL_FIGURE,
    COMPATIBILITY_FIGURE,
)

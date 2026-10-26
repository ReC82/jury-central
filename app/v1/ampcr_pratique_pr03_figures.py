"""PR03 « Montage et démontage d'un PC — procédure écrite » — données de référence,
contrôles et schémas SVG (ticket #204).

Tout est construit **depuis des données** de ce module (tuples), contrôlées par
`tests/test_ticket204_ampcr_pratique_pr03.py` :

- cinq procédures illustrées (`PREP_STEPS`, `ASSEMBLY_STEPS`, `CPU_STEPS`,
  `DISASSEMBLY_STEPS`, `FIRST_BOOT_STEPS`) : les mêmes tuples dessinent les schémas et
  alimentent les remises en ordre des exercices ;
- connecteur de façade (`FRONT_PANEL_PINS`) : brochage 2 × 5 du guide Intel « Front Panel
  I/O Connectivity Design Guide », le plus répandu ; la disposition **réelle** est toujours
  celle du manuel de la carte mère (rappel affiché avec le schéma) ;
- entretoises (`standoff_status`) : une entretoise sous chaque trou de la carte, aucune
  ailleurs ; plan de boîtier et cartes **fictifs** ;
- visserie courante (`SCREWS`), contrôle visuel (`VISUAL_CHECKS`), arbre des pannes au
  premier démarrage (`BOOT_TREE`) ;
- inventaire attendu / détecté par le firmware (`inventory_gaps`) et seuil d'alerte de
  température (`temperature_verdict`) appliqués aux relevés **fictifs** des cas.

Aucun schéma ne vient d'une image générée : un schéma de broches ou de vis faux serait pire
que pas de schéma.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01/PR02)

# =============================================================================================
# 1. Les cinq procédures illustrées
# =============================================================================================

# Procédure 1 — préparer le poste et l'intervention.
PREP_STEPS: tuple[tuple[str, str], ...] = (
    ("Autoriser", "Fiche d'intervention signée ; sauvegarde faite ou refus noté ; mot de passe si nécessaire."),
    ("Relever", "État initial, PC encore fermé : photos, numéro de série, défauts visibles, accessoires remis."),
    ("Couper", "Arrêter le système, interrupteur du bloc sur 0, câble secteur débranché, bouton appuyé."),
    ("Installer le poste", "PC débranché posé sur une table dégagée et éclairée, tapis antistatique, bac à vis."),
    ("Se protéger", "Bracelet antistatique relié au châssis ; ni bijou ni pull en laine ; pièces dans leur sachet."),
    ("Documenter", "Photographier l'intérieur et chaque branchement avant de débrancher quoi que ce soit."),
)

# Procédure 2 — montage complet d'un PC de bureau (ordre recommandé).
ASSEMBLY_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Poste, ESD, inventaire des pièces, manuels ouverts ; compatibilité vérifiée."),
    ("Processeur", "Sur la carte mère posée sur son carton : processeur dans le socket, levier fermé."),
    ("Mémoire et M.2", "Barrettes dans les emplacements du manuel, SSD M.2 vissé (entretoise M.2)."),
    ("Refroidissement", "Pâte thermique, ventirad fixé en croix, câble sur CPU_FAN."),
    ("Boîtier", "Entretoises sous chaque trou de la carte, plaque d'E/S si elle n'est pas intégrée."),
    ("Carte mère", "Carte posée sur les entretoises, ports alignés sur la plaque, vis sans forcer."),
    ("Bloc et disques", "Bloc d'alimentation vissé, ventilateur vers le filtre ; disques SATA fixés."),
    ("Carte graphique", "Dans le premier emplacement PCIe x16, clip enclenché, équerre vissée."),
    ("Câbles", "ATX 24, EPS, PCIe, SATA, façade, USB, audio, ventilateurs ; câbles rangés."),
    ("Contrôler", "Contrôle visuel complet, puis premier démarrage et tests avant de fermer."),
)

# Procédure 3 — processeur, pâte thermique et ventirad (socket LGA, cas le plus courant).
CPU_STEPS: tuple[tuple[str, str], ...] = (
    ("Ouvrir le socket", "Lever le levier, ouvrir le cadre ; le capot de protection reste en place."),
    ("Orienter", "Aligner le triangle doré du processeur sur le repère du socket et les encoches."),
    ("Poser", "Déposer le processeur à la verticale, sans le faire glisser ni appuyer."),
    ("Verrouiller", "Fermer le cadre et le levier ; le capot sort seul : le garder pour un retour."),
    ("Pâte thermique", "Une petite noisette au centre (ou selon la notice) ; pas d'excès, pas de bulles."),
    ("Ventirad", "Retirer le film de la semelle, poser bien à plat, serrer en croix et progressivement."),
    ("Brancher", "Câble du ventilateur sur CPU_FAN (ou pompe sur AIO_PUMP), loin des pales."),
)

# Procédure 4 — démontage documenté (ordre inverse du montage).
DISASSEMBLY_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Autorisation et sauvegarde, état initial, mise hors tension, ESD (procédure 1)."),
    ("Photographier", "Chaque câble et chaque emplacement ; repérer les câbles par une étiquette."),
    ("Débrancher", "Appuyer sur chaque loquet ; tirer sur le connecteur, jamais sur les fils."),
    ("Carte graphique", "Dévisser l'équerre, débrancher le PCIe, ouvrir le clip, sortir à la verticale."),
    ("Stockage et mémoire", "Disques, SSD M.2 et barrettes ; vis triées et étiquetées dans le bac."),
    ("Ventirad", "Dévisser en croix, décoller par une légère rotation, jamais en tirant d'un coup."),
    ("Carte mère", "Dévisser la carte, la sortir par les bords, la poser sur son carton ou dans son sachet."),
    ("Ranger", "Chaque pièce dans un sachet antistatique étiqueté ; fiche de démontage complétée."),
)

# Procédure 5 — premier démarrage et tests.
FIRST_BOOT_STEPS: tuple[tuple[str, str], ...] = (
    ("Contrôle visuel", "Grille de contrôle complète (chapitre 8) ; aucune vis libre dans le boîtier."),
    ("Mise sous tension", "Secteur, interrupteur sur I, bouton ; observer ventilateurs, LED et écran."),
    ("Patienter", "Le premier démarrage peut rester noir plusieurs minutes (entraînement mémoire)."),
    ("Lire l'UEFI", "Processeur, mémoire totale, disques, températures, ventilateur CPU, date et heure."),
    ("Tester", "Test mémoire, températures en charge, état SMART des disques, ports et boutons."),
    ("Rendre compte", "Valeurs relevées, anomalies corrigées, conclusion ; puis fermer le boîtier."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Préparer le poste et l'intervention", PREP_STEPS),
    ("Monter un PC complet", ASSEMBLY_STEPS),
    ("Installer le processeur, la pâte thermique et le ventirad", CPU_STEPS),
    ("Démonter un PC en documentant", DISASSEMBLY_STEPS),
    ("Premier démarrage et tests", FIRST_BOOT_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


PREP_FIGURE = Figure(
    key="pr03-preparer-poste",
    title="Procédure 1 — Préparer le poste et l'intervention",
    alt=_procedure_alt("Procédure de préparation d'une intervention sur un PC.", PREP_STEPS),
    caption=(
        "Avant tout geste technique : autorisation et sauvegarde, état initial, mise hors "
        "tension, poste antistatique et photos. Rien ne se démonte avant ces six étapes."
    ),
    svg=step_flow_svg(PREP_STEPS),
)

ASSEMBLY_FIGURE = Figure(
    key="pr03-ordre-montage",
    title="Procédure 2 — Monter un PC complet",
    alt=_procedure_alt("Ordre recommandé de montage d'un PC de bureau.", ASSEMBLY_STEPS),
    caption=(
        "Ordre recommandé : on équipe la carte mère hors du boîtier (accès facile au socket et "
        "aux emplacements), on l'installe, puis le bloc, les disques, la carte graphique et le "
        "câblage. Un gros ventirad ou un boîtier étroit peuvent imposer d'adapter l'ordre : la "
        "notice fait foi."
    ),
    svg=step_flow_svg(ASSEMBLY_STEPS),
)

CPU_FIGURE = Figure(
    key="pr03-processeur-ventirad",
    title="Procédure 3 — Processeur, pâte thermique et ventirad",
    alt=_procedure_alt("Installation d'un processeur sur un socket LGA puis de son ventirad.", CPU_STEPS),
    caption=(
        "Socket LGA (broches sur la carte mère) : rien ne se force, le processeur se pose. Sur un "
        "socket PGA (broches sous le processeur, ex. AM4), on lève le levier, on aligne le "
        "triangle et le processeur tombe seul dans les trous."
    ),
    svg=step_flow_svg(CPU_STEPS),
)

DISASSEMBLY_FIGURE = Figure(
    key="pr03-demontage",
    title="Procédure 4 — Démonter un PC en documentant",
    alt=_procedure_alt("Démontage d'un PC dans l'ordre inverse du montage.", DISASSEMBLY_STEPS),
    caption=(
        "Démontage = ordre inverse du montage, mais documenté : photos, étiquettes, vis triées. "
        "Ce qui n'est pas noté au démontage manquera au remontage."
    ),
    svg=step_flow_svg(DISASSEMBLY_STEPS),
)

FIRST_BOOT_FIGURE = Figure(
    key="pr03-premier-demarrage",
    title="Procédure 5 — Premier démarrage et tests",
    alt=_procedure_alt("Mise en service d'un PC qui vient d'être monté.", FIRST_BOOT_STEPS),
    caption=(
        "Le boîtier reste ouvert jusqu'à la fin des tests : on corrige sans tout redémonter. Le "
        "compte rendu reprend les valeurs lues, pas « tout fonctionne »."
    ),
    svg=step_flow_svg(FIRST_BOOT_STEPS),
)

# =============================================================================================
# 2. Connecteur de façade (F_PANEL)
# =============================================================================================


@dataclass(frozen=True)
class PanelPin:
    number: int
    signal: str
    role: str  # « LED disque », « LED alimentation », « bouton Reset », « bouton Power », …
    polarized: bool  # True : le sens du câble compte (LED) ; False : bouton ou broche inutilisée


# Guide Intel « Front Panel I/O Connectivity Design Guide » : connecteur 2 × 5, broche 10 =
# détrompeur (absente). Rangée des impaires : LED disque et Reset ; rangée des paires : LED
# d'alimentation et bouton Power.
FRONT_PANEL_PINS: tuple[PanelPin, ...] = (
    PanelPin(1, "HDD_LED+", "LED disque", True),
    PanelPin(2, "PLED+", "LED alimentation", True),
    PanelPin(3, "HDD_LED−", "LED disque", True),
    PanelPin(4, "PLED−", "LED alimentation", True),
    PanelPin(5, "RESET (masse)", "bouton Reset", False),
    PanelPin(6, "PWR_SW", "bouton Power", False),
    PanelPin(7, "RESET_SW", "bouton Reset", False),
    PanelPin(8, "PWR_SW (masse)", "bouton Power", False),
    PanelPin(9, "+5 V", "aucun câble du boîtier", False),
    PanelPin(10, "clé", "détrompeur", False),
)
FRONT_PANEL_BY_NUMBER = {p.number: p for p in FRONT_PANEL_PINS}


def panel_pins_for(role: str) -> tuple[int, ...]:
    return tuple(p.number for p in FRONT_PANEL_PINS if p.role == role)


_PANEL_SHORT = {
    "LED disque": "LED disque", "LED alimentation": "LED alim.", "bouton Reset": "Reset",
    "bouton Power": "Power", "aucun câble du boîtier": "non utilisée", "détrompeur": "pas de broche",
}


def front_panel_svg(pins: tuple[PanelPin, ...]) -> str:
    """Connecteur 2 × 5 vu de dessus : rangée du haut = broches paires, rangée du bas =
    broches impaires, broche 1 en bas à gauche (pastille carrée). Chaque case porte le
    numéro, le signal et le rôle en texte ; la broche 10 est dessinée vide (détrompeur)."""
    width, cell_w, cell_h, left, top = 380, 72, 62, 10, 34
    parts = [
        (f'<text x="{width // 2}" y="16" text-anchor="middle" font-size="13.5" font-weight="700">'
         "Connecteur de façade 2 × 5 (disposition Intel)</text>"),
        (f'<text x="{width // 2}" y="30" text-anchor="middle" font-size="11">'
         "Haut : broches paires · bas : broches impaires · ■ = broche 1</text>"),
    ]
    for pin in pins:
        column = (pin.number - 1) // 2
        row = 0 if pin.number % 2 == 0 else 1
        x = left + column * (cell_w + 2)
        y = top + row * (cell_h + 4)
        empty = pin.number == 10
        dash = ' stroke-dasharray="4 3"' if empty else ""
        parts.append(
            f'<rect data-pin="{pin.number}" data-signal="{escape(pin.signal)}" '
            f'data-role="{escape(pin.role)}" data-polarized="{str(pin.polarized).lower()}" '
            f'x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="5" '
            f'fill="{"#ffffff" if empty else "#f4f6fb"}" stroke="{_STROKE}" stroke-width="1.2"{dash}/>'
        )
        if pin.number == 1:
            parts.append(f'<rect x="{x + 4}" y="{y + 4}" width="10" height="10" fill="{_STROKE}"/>')
        elif not empty:
            parts.append(f'<circle cx="{x + 9}" cy="{y + 9}" r="5" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.2"/>')
        parts.append(
            f'<text x="{x + cell_w - 6}" y="{y + 14}" font-size="12" font-weight="700" '
            f'text-anchor="end">{pin.number}</text>'
        )
        parts.append(_text_lines(x + 4, y + 30, _wrap(pin.signal, 11), size=10, weight="700", step=12))
        parts.append(_text_lines(x + 5, y + 55, [_PANEL_SHORT[pin.role]], size=9.5))
    y = top + 2 * (cell_h + 4) + 14
    notes = [
        "LED : polarisées, fil de couleur (ou marqué +) sur la broche +.",
        "Boutons Power et Reset : non polarisés, sens indifférent.",
        "Toujours vérifier le schéma du manuel de la carte mère.",
    ]
    parts.append(_text_lines(left, y, notes, size=11, step=15))
    return _svg(width, y + 15 * len(notes) + 2, parts)


FRONT_PANEL_FIGURE = Figure(
    key="pr03-facade",
    title="Connecteur de façade (F_PANEL)",
    alt=(
        "Connecteur à deux rangées de cinq broches. "
        + " ; ".join(f"broche {p.number} : {p.signal}, {p.role}" for p in FRONT_PANEL_PINS)
        + ". Les LED sont polarisées, les boutons ne le sont pas."
    ),
    caption=(
        "Disposition du guide Intel, reprise par la plupart des cartes ATX ; certaines cartes "
        "ont un autre brochage : le manuel de la carte (ou la sérigraphie) fait foi. Une LED "
        "branchée à l'envers ne s'allume pas mais ne casse rien ; un bouton Power branché sur "
        "les broches Reset ne démarre pas le PC."
    ),
    svg=front_panel_svg(FRONT_PANEL_PINS),
)

# =============================================================================================
# 3. Entretoises : une sous chaque trou de la carte, aucune ailleurs
# =============================================================================================

# Plan fictif des emplacements d'entretoise d'un boîtier ATX (repère, x, y en unités du schéma).
CASE_POSITIONS: tuple[tuple[str, int, int], ...] = (
    ("A", 30, 40), ("B", 155, 40), ("C", 280, 40),
    ("D", 30, 130), ("E", 155, 130), ("F", 280, 130),
    ("G", 30, 220), ("H", 155, 220), ("I", 280, 220),
    ("J", 30, 300), ("K", 155, 300), ("L", 280, 300),
)
CASE_POSITION_KEYS = tuple(key for key, _x, _y in CASE_POSITIONS)

STATUS_OK = "ok"
STATUS_MISSING = "manquante"
STATUS_EXTRA = "en trop"
STATUS_FREE = "libre"
STATUS_LABELS = {
    STATUS_OK: "trou + entretoise : correct",
    STATUS_MISSING: "trou sans entretoise : carte qui fléchit",
    STATUS_EXTRA: "entretoise sans trou : court-circuit possible",
    STATUS_FREE: "ni trou ni entretoise",
}


def standoff_status(board_holes: frozenset[str], standoffs: frozenset[str]) -> dict[str, str]:
    """Verdict de chaque emplacement du boîtier pour une carte et des entretoises posées."""
    unknown = (board_holes | standoffs) - set(CASE_POSITION_KEYS)
    if unknown:
        raise ValueError(f"Emplacements inconnus : {sorted(unknown)}")
    verdicts = {}
    for key in CASE_POSITION_KEYS:
        hole, standoff = key in board_holes, key in standoffs
        if hole and standoff:
            verdicts[key] = STATUS_OK
        elif hole:
            verdicts[key] = STATUS_MISSING
        elif standoff:
            verdicts[key] = STATUS_EXTRA
        else:
            verdicts[key] = STATUS_FREE
    return verdicts


def standoff_problems(board_holes: frozenset[str], standoffs: frozenset[str]) -> tuple[list[str], list[str]]:
    """(entretoises en trop, entretoises manquantes), triées par repère."""
    status = standoff_status(board_holes, standoffs)
    extra = [k for k, v in status.items() if v == STATUS_EXTRA]
    missing = [k for k, v in status.items() if v == STATUS_MISSING]
    return extra, missing


# Exercice E07 : carte microATX fictive (8 trous) dans le boîtier ATX ci-dessus ; le stagiaire a
# laissé les entretoises montées en usine pour une carte ATX.
E07_BOARD_HOLES = frozenset({"A", "C", "D", "E", "F", "G", "H", "I"})
E07_STANDOFFS = frozenset({"A", "B", "C", "D", "F", "G", "H", "I", "J", "K", "L"})

_STATUS_FILL = {STATUS_OK: "#e9f5ec", STATUS_MISSING: "#fff4e5", STATUS_EXTRA: "#fdecea", STATUS_FREE: "#ffffff"}
_STATUS_MARK = {STATUS_OK: "OK", STATUS_MISSING: "?", STATUS_EXTRA: "X", STATUS_FREE: "·"}


def standoff_svg(board_holes: frozenset[str], standoffs: frozenset[str], *, title: str) -> str:
    """Plan du fond de boîtier : chaque emplacement porte son repère, sa marque (OK, X, ?)
    et son verdict en texte ; le cadre pointillé matérialise la carte mère."""
    status = standoff_status(board_holes, standoffs)
    width, height = 380, 420
    hole_ys = [y for key, _x, y in CASE_POSITIONS if key in board_holes]
    parts = [
        f'<text x="{width // 2}" y="16" text-anchor="middle" font-size="13.5" font-weight="700">{escape(title)}</text>',
        f'<rect x="6" y="24" width="{width - 12}" height="318" rx="6" fill="#f7f7f7" stroke="{_STROKE}" stroke-width="1.5"/>',
    ]
    if hole_ys:
        parts.append(
            f'<rect x="16" y="{min(hole_ys) - 4}" width="{width - 32}" height="{max(hole_ys) - min(hole_ys) + 48}" '
            f'rx="6" fill="none" stroke="#2e6b3a" stroke-width="1.5" stroke-dasharray="6 4"/>'
        )
    for key, x, y in CASE_POSITIONS:
        verdict = status[key]
        parts.append(
            f'<g data-position="{key}" data-status="{escape(verdict)}">'
            f'<circle cx="{x + 18}" cy="{y + 18}" r="15" fill="{_STATUS_FILL[verdict]}" stroke="{_STROKE}" stroke-width="1.5"/>'
            f'<text x="{x + 18}" y="{y + 23}" font-size="12.5" font-weight="700" text-anchor="middle">{_STATUS_MARK[verdict]}</text>'
            f'<text x="{x + 40}" y="{y + 16}" font-size="12.5" font-weight="700">{key}</text>'
            f'<text x="{x + 40}" y="{y + 30}" font-size="10">{escape(verdict)}</text></g>'
        )
    legend = [f"{_STATUS_MARK[s]} : {STATUS_LABELS[s]}" for s in (STATUS_OK, STATUS_EXTRA, STATUS_MISSING)]
    legend.append("Cadre pointillé : emplacement de la carte mère.")
    parts.append(_text_lines(10, 362, legend, size=11, step=15))
    return _svg(width, height, parts)


STANDOFF_FIGURE = Figure(
    key="pr03-entretoises",
    title="Entretoises : relevé d'un montage de stagiaire (fictif)",
    alt=(
        "Plan du fond d'un boîtier avec douze emplacements d'entretoise, A à L. "
        + " ; ".join(f"{k} : {v}" for k, v in standoff_status(E07_BOARD_HOLES, E07_STANDOFFS).items())
        + ". Une entretoise sans trou en face touche le circuit de la carte."
    ),
    caption=(
        "Une entretoise sous chaque trou de la carte, aucune ailleurs : une entretoise « en "
        "trop » touche une piste au dos de la carte (court-circuit possible) ; une entretoise "
        "« manquante » laisse la carte fléchir quand on branche un connecteur. Plan fictif."
    ),
    svg=standoff_svg(E07_BOARD_HOLES, E07_STANDOFFS, title="Fond de boîtier ATX, carte microATX posée"),
)

# =============================================================================================
# 4. Visserie, contrôle visuel, pannes au premier démarrage
# =============================================================================================

# (élément fixé, vis la plus courante, remarque). Valeurs les plus fréquentes : les vis livrées
# avec le boîtier et les pièces font foi.
SCREWS: tuple[tuple[str, str, str], ...] = (
    ("Carte mère sur ses entretoises", "6-32 UNC (parfois M3)", "Vis livrées avec le boîtier ; serrer sans forcer."),
    ("Entretoises dans le boîtier", "filetage 6-32 côté boîtier", "Seulement en face d'un trou de la carte."),
    ("Bloc d'alimentation", "6-32 UNC", "Quatre vis à l'arrière."),
    ("Disque 3,5 pouces", "6-32 UNC (grosse tête)", "Ou tiroir sans vis du boîtier."),
    ("SSD ou disque 2,5 pouces", "M3", "Une vis 6-32, plus grosse, abîmerait le filetage du disque."),
    ("SSD M.2", "M2 (très petite)", "Vis ou loquet de la carte ; entretoise M.2 à la bonne longueur (2280)."),
    ("Équerre de carte d'extension", "6-32 UNC le plus souvent", "Ou loquet sans vis selon le boîtier."),
    ("Ventilateurs de boîtier", "vis autotaraudeuses", "Ou picots en caoutchouc."),
)

# (moment, vérification) : la grille du chapitre 8, réutilisée par le cas 1 et les exercices.
VISUAL_CHECKS: tuple[tuple[str, str], ...] = (
    ("Fixations", "Carte mère vissée sur toutes ses entretoises, aucune vis ni entretoise libre dans le boîtier."),
    ("Processeur", "Ventirad à plat, film de la semelle retiré, câble sur CPU_FAN."),
    ("Mémoire", "Barrettes enfoncées jusqu'au clic, clips fermés des deux côtés, emplacements du manuel."),
    ("Carte graphique", "Clip PCIe enclenché, équerre vissée, connecteurs PCIe ou 12V-2x6 enfoncés à fond."),
    ("Alimentation", "ATX 24 et EPS clipsés ; SATA alimentation et données sur chaque disque."),
    ("Façade", "Power, Reset et LED sur les bonnes broches ; USB et audio de façade branchés."),
    ("Câbles", "Aucun câble dans un ventilateur ni sur le ventirad ; flux d'air dégagé."),
    ("Secteur", "Sélecteur de tension éventuel correct, interrupteur du bloc accessible."),
)

BOOT_TREE: tuple[tuple[str, str], ...] = (
    ("Un ventilateur ou une LED réagit-il au bouton ?",
     "Secteur et interrupteur du bloc ; ATX 24 et EPS ; câble Power du boîtier sur les bonnes broches de façade."),
    ("Le PC reste-t-il allumé ?",
     "Arrêt immédiat : EPS absent, vis ou entretoise en court-circuit, câble mal enfoncé → couper et contrôler."),
    ("Une image apparaît-elle (après quelques minutes au 1er démarrage) ?",
     "Écran sur la carte graphique ; barrettes enfoncées ; LED de diagnostic de la carte ; une barrette seule."),
    ("L'UEFI voit-il tout le matériel ?",
     "Mémoire incomplète : barrette mal enfoncée ; disque absent : câbles, M.2 vissé, port SATA partagé."),
    ("Températures normales au repos et en charge ?",
     "Film du ventirad, pâte, serrage, CPU_FAN, sens des ventilateurs ; couper si le processeur chauffe."),
)
BOOT_TREE_FINAL = "Montage validé : tests mémoire, disques et ports, puis compte rendu et fermeture du boîtier."

BOOT_TREE_FIGURE = Figure(
    key="pr03-pannes-premier-demarrage",
    title="Pannes au premier démarrage : par où commencer",
    alt=(
        "Arbre de décision en cinq questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(BOOT_TREE, start=1))
        + f" Si toutes les réponses sont oui : {BOOT_TREE_FINAL}"
    ),
    caption=(
        "Après un montage, la panne vient presque toujours du montage lui-même : on contrôle "
        "les branchements, PC débranché, avant de soupçonner une pièce neuve."
    ),
    svg=decision_tree_svg(BOOT_TREE, BOOT_TREE_FINAL),
)

# =============================================================================================
# 5. Relevés fictifs : inventaire détecté et températures
# =============================================================================================


@dataclass(frozen=True)
class Inventory:
    cpu: str
    memory_gb: int
    memory_modules: int
    drives: tuple[str, ...]
    cpu_fan_rpm: int


def inventory_gaps(expected: Inventory, detected: Inventory) -> list[str]:
    """Écarts entre le bon de montage et ce que le firmware détecte (un écart par critère)."""
    gaps = []
    if detected.cpu != expected.cpu:
        gaps.append("processeur")
    if detected.memory_gb != expected.memory_gb or detected.memory_modules != expected.memory_modules:
        gaps.append("mémoire")
    missing = [d for d in expected.drives if d not in detected.drives]
    if missing:
        gaps.append("stockage")
    if detected.cpu_fan_rpm == 0:
        gaps.append("ventilateur CPU")
    return gaps


def uefi_lines(inv: Inventory, *, slots: tuple[tuple[str, str], ...], temp_c: int) -> tuple[str, ...]:
    """Écran de synthèse fictif du firmware (texte limité à `SCREEN_WIDTH` caractères)."""
    lines = [
        "UEFI — Informations système (capture fictive)",
        f"Processeur      : {inv.cpu}",
        f"Mémoire totale  : {inv.memory_gb * 1024} Mo",
    ]
    lines += [f"  {slot:<14}: {content}" for slot, content in slots]
    for index, drive in enumerate(inv.drives or ("aucun périphérique",), start=1):
        lines.append(f"Stockage {index}      : {drive}")
    lines.append(f"Temp. processeur: {temp_c} °C")
    lines.append(f"CPU_FAN         : {inv.cpu_fan_rpm} tr/min" if inv.cpu_fan_rpm else "CPU_FAN         : N/A")
    return tuple(lines)


# Cas 3 (premier démarrage incomplet) : bon de montage et ce que l'UEFI affiche.
CASE3_EXPECTED = Inventory(
    cpu="Processeur 8 cœurs (fictif)", memory_gb=32, memory_modules=2,
    drives=("SSD NVMe 1 To (M.2_1)", "Disque SATA 2 To (SATA 1)"), cpu_fan_rpm=900,
)
CASE3_DETECTED = Inventory(
    cpu="Processeur 8 cœurs (fictif)", memory_gb=16, memory_modules=1,
    drives=("SSD NVMe 1 To (M.2_1)",), cpu_fan_rpm=0,
)
CASE3_SLOTS: tuple[tuple[str, str], ...] = (("DIMM_A2", "16 Go DDR5-4800"), ("DIMM_B2", "vide"))
CASE3_TEMP = 41
CASE3_SCREEN = uefi_lines(CASE3_DETECTED, slots=CASE3_SLOTS, temp_c=CASE3_TEMP)

UEFI_FIGURE = Figure(
    key="pr03-uefi-premier-demarrage",
    title="Écran du firmware au premier démarrage (fictif)",
    alt="Écran texte du firmware. " + " ; ".join(CASE3_SCREEN) + ".",
    caption=(
        "On compare chaque ligne au bon de montage : 16 Go au lieu de 32, un seul disque sur "
        "deux, ventilateur CPU non détecté. Capture fictive, reconstituée pour l'entraînement."
    ),
    svg=screen_svg(CASE3_SCREEN, label="Capture fictive — pas un écran officiel"),
)

TEMP_ALERT_MARGIN = 10  # °C sous la limite de la fiche : au-delà, on cherche une cause


def temperature_verdict(temp_c: int, limit_c: int) -> str:
    """« normal », « à surveiller » (moins de 10 °C sous la limite) ou « anormal » (limite
    atteinte : le processeur réduit sa fréquence ou s'arrête pour se protéger)."""
    if temp_c >= limit_c:
        return "anormal"
    if temp_c >= limit_c - TEMP_ALERT_MARGIN:
        return "à surveiller"
    return "normal"


# Cas 4 (surchauffe après montage) : relevés avant et après correction, limite de la fiche.
CASE4_LIMIT = 95
CASE4_BEFORE = (("Repos", 58), ("Charge, 2 min", 95))
CASE4_AFTER = (("Repos", 36), ("Charge, 30 min", 74))

PR03_FIGURES: tuple[Figure, ...] = (
    PREP_FIGURE,
    ASSEMBLY_FIGURE,
    CPU_FIGURE,
    STANDOFF_FIGURE,
    FRONT_PANEL_FIGURE,
    FIRST_BOOT_FIGURE,
    UEFI_FIGURE,
    BOOT_TREE_FIGURE,
    DISASSEMBLY_FIGURE,
)

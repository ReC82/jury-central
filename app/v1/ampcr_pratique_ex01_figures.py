"""EX01 « Examen blanc écrit — maintenance et dépannage matériel » — données des dossiers et
schémas (ticket #230).

Une seule source pour le sujet affiché, les documents des questions et le corrigé :
- **plan lettré** d'une carte mère ATX (repères A à L), dessiné sur la géométrie du plan
  numéroté de PR01 (`BOARD_PARTS`) : mêmes éléments, mêmes positions, lettres attribuées ici ;
- **LED de diagnostic** relevées sur le poste du dossier A ;
- **budget d'alimentation** du dossier B, calculé avec la règle de PR02
  (`power_budget`, `recommended_psu` : total des fiches + 30 %, palier de 50 W supérieur,
  jamais sous la recommandation du fabricant de la carte graphique) ;
- **relevé de températures** du dossier B, lu avec la convention de PR03/PR04
  (`temperature_verdict` : « à surveiller » à moins de 10 °C de la limite de la fiche) ;
- **relevé SMART** du dossier C, lu avec la règle de PR04 (`smart_verdict`).

Toutes les situations, références et valeurs sont **fictives** (aucun produit réel). Les deux
schémas utilisés dans les questions sont aussi enregistrés en fichiers statiques
(`app/static/img/ampcr-pratique/`) ; un test vérifie qu'ils sont identiques au SVG produit ici.
"""

from html import escape

from app.v1.ampcr_pratique_pr01_figures import BOARD_PARTS
from app.v1.ampcr_pratique_pr02_figures import Load, power_budget, recommended_psu
from app.v1.ampcr_pratique_pr03_figures import temperature_verdict
from app.v1.ampcr_pratique_pr04_figures import smart_verdict
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, line_chart_svg

_STROKE = "#33415c"
STATIC_DIR_REF = "img/ampcr-pratique"

# =============================================================================================
# Partie 1 — plan lettré de la carte mère (question X01)
# =============================================================================================

# Lettre → clé de `BOARD_PARTS` (PR01). L'ordre des lettres ne suit pas la lecture du plan.
BOARD_LETTERS: tuple[tuple[str, str], ...] = (
    ("A", "ram"),
    ("B", "eps"),
    ("C", "pcie16"),
    ("D", "cmos"),
    ("E", "socket"),
    ("F", "sata"),
    ("G", "atx24"),
    ("H", "m21"),
    ("I", "cpufan"),
    ("J", "panel"),
    ("K", "chipset"),
    ("L", "usb3"),
)

_PARTS_BY_KEY = {part.key: part for part, _number in BOARD_PARTS}

# Ce que le candidat doit nommer (réponse attendue, une ligne par repère).
BOARD_ANSWERS: dict[str, str] = {
    "A": "emplacements DIMM de la mémoire vive (4 slots)",
    "B": "connecteur EPS 8 broches d'alimentation du processeur",
    "C": "emplacement PCIe x16 (carte graphique)",
    "D": "pile CMOS (bouton 3 V)",
    "E": "socket du processeur",
    "F": "ports SATA (données des disques et SSD 2,5 pouces)",
    "G": "connecteur d'alimentation principal ATX 24 broches",
    "H": "emplacement M.2 (SSD NVMe ou SATA selon le manuel)",
    "I": "connecteur CPU_FAN du ventilateur du processeur (4 broches)",
    "J": "connecteur de façade (bouton marche, reset, LED)",
    "K": "chipset (sous radiateur)",
    "L": "connecteur interne USB 3.x de la façade (19 broches)",
}

# Description visuelle de chaque repère, sans le nommer (document de la question, lisible
# sans voir le schéma et transmise au correcteur).
BOARD_DESCRIPTIONS: dict[str, str] = {
    "A": "quatre longs emplacements parallèles munis de clips, juste à droite du repère E",
    "B": "connecteur à 8 broches dans le coin supérieur gauche, au-dessus de petits radiateurs",
    "C": "long emplacement horizontal, le plus proche du repère E, sous celui-ci",
    "D": "petit élément rond et plat d'environ 2 cm, en bas de la carte",
    "E": "grand support carré dans la moitié haute, à gauche du centre, bordé à sa gauche par de petits radiateurs",
    "F": "petits connecteurs en L regroupés sur le bord droit, dans la moitié basse",
    "G": "connecteur haut et étroit à deux rangées de broches, juste à droite du repère A",
    "H": "fente plate couchée sur la carte, juste sous le repère C, où un module se fixe par une vis",
    "I": "petit connecteur à 4 broches juste sous le repère E",
    "J": "rangée de broches fines dans le coin inférieur droit",
    "K": "puce plate sous un radiateur, en bas à droite, à gauche du repère F",
    "L": "connecteur rectangulaire à 19 broches en haut à droite, à côté du repère G",
}

# Questions de branchement (X01, consigne 2) : élément à brancher → repère attendu.
BOARD_CONNECTIONS: tuple[tuple[str, str], ...] = (
    ("le câble 8 broches marqué « CPU » du bloc d'alimentation", "B"),
    ("le câble du ventilateur du ventirad", "I"),
    ("les fils du bouton marche de la façade", "J"),
    ("un SSD NVMe au format M.2 2280", "H"),
)
# Repères reliés directement au processeur sur une plateforme récente (consigne 3).
BOARD_CPU_LINKED: tuple[str, ...] = ("A", "C")


def lettered_board_svg(width: int = 380, height: int = 386) -> str:
    """Même dessin que le plan numéroté de PR01 ; seuls les repères lettrés portent un
    texte, les autres éléments restent des cadres vides (gris)."""
    letters = {key: letter for letter, key in BOARD_LETTERS}
    parts = [
        (f'<rect x="2" y="22" width="{width - 4}" height="{height - 24}" rx="6" fill="#eef3ee" '
         f'stroke="#2e6b3a" stroke-width="2"/>'),
        _text_lines(width // 2, 15, ["Carte mère ATX fictive — repères A à L"], size=12.5,
                    weight="700", anchor="middle"),
    ]
    for part, _number in BOARD_PARTS:
        letter = letters.get(part.key)
        fill = "#ffffff" if letter else "#e3e7e3"
        parts.append(
            f'<rect data-part="{escape(part.key)}" data-letter="{letter or ""}" x="{part.x}" y="{part.y}" '
            f'width="{part.w}" height="{part.h}" rx="3" fill="{fill}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        if letter:
            parts.append(
                f'<text x="{part.x + part.w / 2:.0f}" y="{part.y + part.h / 2 + 5:.0f}" font-size="'
                f'{13 if part.h >= 18 else 11}" font-weight="700" text-anchor="middle">{letter}</text>'
            )
    return _svg(width, height, parts)


BOARD_FIGURE = Figure(
    key="ex01-plan-carte-mere",
    title="Plan lettré d'une carte mère ATX (support fictif)",
    alt=(
        "Plan simplifié d'une carte mère ATX vue de dessus, plaque d'entrées-sorties à gauche, "
        "avec douze repères lettrés : "
        + " ; ".join(f"{letter} {BOARD_DESCRIPTIONS[letter]}" for letter, _key in BOARD_LETTERS)
        + ". Les cadres gris sans lettre ne sont pas à identifier. Ce n'est pas un plan à l'échelle."
    ),
    caption=(
        "Plan lettré d'une carte mère ATX fictive (non à l'échelle). L'emplacement exact des "
        "éléments change d'un modèle à l'autre : le manuel de la carte fait foi."
    ),
    svg=lettered_board_svg(),
)
BOARD_FIGURE_FILE = f"{STATIC_DIR_REF}/ex01-plan-carte-mere.svg"


def board_document_text() -> str:
    lines = [
        (
            "Schéma fictif : carte mère ATX vue de dessus, plaque d'entrées-sorties à gauche, "
            "douze repères lettrés (non à l'échelle)."
        ),
    ]
    lines += [f"Repère {letter} : {BOARD_DESCRIPTIONS[letter]}." for letter, _key in BOARD_LETTERS]
    return "\n".join(lines)


# =============================================================================================
# Dossier A — fiduciaire Mertens : poste qui ne démarre plus après un ajout de mémoire
# =============================================================================================

# (libellé imprimé sur la carte, allumée ?) — relevé du technicien à l'arrivée.
DEBUG_LEDS: tuple[tuple[str, bool], ...] = (
    ("CPU", False),
    ("DRAM", True),
    ("VGA", False),
    ("BOOT", False),
)
LIT_LED = next(name for name, lit in DEBUG_LEDS if lit)

# Mémoire relevée à l'ouverture (emplacement, contenu) — d'après le dossier A.
DOSSIER_A_SLOTS: tuple[tuple[str, str], ...] = (
    ("A1", "16 Go DDR5-6000 (ajoutée), clip de gauche ouvert, barrette inclinée"),
    ("A2", "8 Go DDR5-4800 (d'origine)"),
    ("B1", "16 Go DDR5-6000 (ajoutée)"),
    ("B2", "8 Go DDR5-4800 (d'origine)"),
)
DOSSIER_A_WAIT_SECONDS = 30  # durée d'attente du neveu avant de couper (dossier A)


def debug_leds_svg(width: int = 380, height: int = 150) -> str:
    """Quatre LED de diagnostic côte à côte ; la LED allumée est pleine ET marquée
    « allumée » en texte (jamais la couleur seule)."""
    parts = [
        (f'<rect x="2" y="24" width="{width - 4}" height="{height - 26}" rx="6" fill="#eef3ee" '
         f'stroke="#2e6b3a" stroke-width="2"/>'),
        _text_lines(width // 2, 15, ["LED de diagnostic de la carte mère (relevé fictif)"], size=12.5,
                    weight="700", anchor="middle"),
    ]
    step = (width - 40) / len(DEBUG_LEDS)
    for i, (name, lit) in enumerate(DEBUG_LEDS):
        cx = 20 + step * i + step / 2
        fill = "#f59e0b" if lit else "#ffffff"
        parts.append(
            f'<circle data-led="{name}" data-lit="{str(lit).lower()}" cx="{cx:.0f}" cy="66" r="16" '
            f'fill="{fill}" stroke="{_STROKE}" stroke-width="2"/>'
        )
        parts.append(f'<text x="{cx:.0f}" y="106" font-size="13" font-weight="700" text-anchor="middle">{name}</text>')
        parts.append(
            f'<text x="{cx:.0f}" y="126" font-size="11.5" text-anchor="middle">{"allumée fixe" if lit else "éteinte"}</text>'
        )
    return _svg(width, height, parts)


LEDS_FIGURE = Figure(
    key="ex01-led-diagnostic",
    title="LED de diagnostic relevées sur le poste PC-COMPTA-03 (dossier A, fictif)",
    alt=(
        "Quatre voyants de diagnostic de la carte mère, de gauche à droite : "
        + " ; ".join(f"{name} {'allumée fixe' if lit else 'éteinte'}" for name, lit in DEBUG_LEDS)
        + ". Ventilateurs en rotation, aucune image."
    ),
    caption=(
        f"Seule la LED {LIT_LED} reste allumée : selon le manuel de cette carte (dossier A), le "
        "démarrage est arrêté à l'étape mémoire. La signification des LED dépend du fabricant."
    ),
    svg=debug_leds_svg(),
)
LEDS_FIGURE_FILE = f"{STATIC_DIR_REF}/ex01-led-diagnostic.svg"


def leds_document_text() -> str:
    states = ", ".join(f"{name} {'allumée fixe' if lit else 'éteinte'}" for name, lit in DEBUG_LEDS)
    return (
        "Relevé fictif des quatre LED de diagnostic de la carte mère, PC sous tension : "
        f"{states}. Ventilateurs en rotation, aucune image à l'écran, aucun bip (pas de "
        "haut-parleur branché)."
    )


# =============================================================================================
# Dossier B — studio Lumen : changement de carte graphique, mémoire, refroidissement
# =============================================================================================

GPU_NEW_W = 285
GPU_NEW_PSU_RECOMMENDATION = 700  # recommandation du fabricant de la nouvelle carte
GPU_NEW_LENGTH_MM = 310
CASE_MAX_GPU_LENGTH_MM = 300
GPU_NEW_PCIE_8PIN = 2
PSU_CURRENT_W = 550
PSU_CURRENT_PCIE_8PIN = 1

# Configuration APRÈS la modification demandée (fiches fictives, puissances maximales).
DOSSIER_B_LOADS: tuple[Load, ...] = (
    Load("Processeur (fiche, puissance maximale)", 180, True),
    Load("Nouvelle carte graphique (fiche)", GPU_NEW_W, True),
    Load("Carte mère et chipset", 40, False),
    Load("4 barrettes DDR5", 20, False),
    Load("SSD NVMe", 7, False),
    Load("Disque dur 3,5 pouces", 8, True),
    Load("4 ventilateurs", 12, True),
    Load("Ports USB et périphériques", 15, False),
)
DOSSIER_B_TOTAL_W = power_budget(DOSSIER_B_LOADS)
DOSSIER_B_PSU_W = recommended_psu(DOSSIER_B_TOTAL_W, gpu_recommendation=GPU_NEW_PSU_RECOMMENDATION)

# Mémoire : en place et proposée (dossier B).
DOSSIER_B_RAM_SLOTS = 4
DOSSIER_B_RAM_MAX_GB = 128
DOSSIER_B_RAM_INSTALLED = "2 × 16 Go DDR5-5600 (A2, B2)"
DOSSIER_B_RAM_TOTAL_AFTER_GB = 2 * 16 + 2 * 16

# Températures sous un rendu vidéo (minute, °C processeur, fréquence GHz, ventilateur tr/min).
TEMP_LIMIT_C = 100  # température maximale indiquée sur la fiche du processeur (fictive)
TEMPERATURE_LOG: tuple[tuple[int, int, str, int], ...] = (
    (0, 45, "5,3", 620),
    (2, 86, "5,1", 610),
    (4, 98, "4,2", 615),
    (6, 100, "3,1", 620),
    (8, 100, "2,9", 610),
)
TEMP_AFTER_LIMIT_MINUTE = next(m for m, t, _f, _v in TEMPERATURE_LOG if t >= TEMP_LIMIT_C)
TEMP_FINAL_VERDICT = temperature_verdict(TEMPERATURE_LOG[-1][1], TEMP_LIMIT_C)
# Relevé après l'intervention (minute, °C) : 30 min de rendu.
TEMPERATURE_AFTER: tuple[tuple[int, int], ...] = ((0, 38), (10, 72), (20, 76), (30, 77))
TEMP_AFTER_VERDICT = temperature_verdict(max(t for _m, t in TEMPERATURE_AFTER), TEMP_LIMIT_C)

TEMPERATURE_FIGURE = Figure(
    key="ex01-temperatures-rendu",
    title="Température du processeur pendant un rendu vidéo (dossier B, fictif)",
    alt=(
        "Courbe de la température du processeur en fonction du temps de rendu : "
        + ", ".join(f"minute {m} : {t} °C" for m, t, _f, _v in TEMPERATURE_LOG)
        + f". Ligne pointillée : maximum de la fiche, {TEMP_LIMIT_C} °C. La fréquence passe de "
        f"{TEMPERATURE_LOG[0][2]} à {TEMPERATURE_LOG[-1][2]} GHz et le ventilateur reste vers "
        f"{TEMPERATURE_LOG[-1][3]} tr/min."
    ),
    caption=(
        f"La température atteint le maximum de la fiche ({TEMP_LIMIT_C} °C) à la minute "
        f"{TEMP_AFTER_LIMIT_MINUTE} pendant que la fréquence baisse : le processeur se protège. "
        "Le ventilateur ne change pas de vitesse."
    ),
    svg=line_chart_svg(
        tuple((m, t) for m, t, _f, _v in TEMPERATURE_LOG),
        threshold=TEMP_LIMIT_C,
        x_label="Minutes de rendu",
        y_label="Température CPU (°C)",
        threshold_label=f"max. fiche {TEMP_LIMIT_C} °C",
        y_max=120,
    ),
)

# =============================================================================================
# Dossier C — clinique vétérinaire Les Saules : SSD ajouté non détecté, disque de données
# =============================================================================================

# Écran « Stockage » du firmware UEFI après l'ajout (capture fictive).
UEFI_STORAGE_SCREEN: tuple[str, ...] = (
    "UEFI — Avancé > Configuration du stockage",
    "Mode SATA ............ AHCI",
    "M.2_1 (processeur) ... SSD NVMe 500 Go (système)",
    "M.2_2 (chipset) ...... SSD M.2 SATA 256 Go",
    "SATA_1 ............... Disque dur 2 To (données)",
    "SATA_2 ............... Aucun",
    "SATA_3 ............... Aucun",
    "SATA_4 ............... Aucun",
    "SATA_5 ............... Désactivé (partagé avec M.2_2)",
    "SATA_6 ............... Désactivé (partagé avec M.2_2)",
)
NEW_SSD_PORT = "SATA_5"
FREE_SATA_PORTS: tuple[str, ...] = ("SATA_2", "SATA_3", "SATA_4")
MANUAL_SHARING_RULE = (
    "Si un SSD M.2 SATA est installé dans M.2_2, les ports SATA_5 et SATA_6 sont désactivés. "
    "Un SSD NVMe dans M.2_2 ne désactive aucun port SATA."
)

# Relevé SMART du disque dur de données (valeurs brutes, fictives).
DOSSIER_C_SMART: tuple[tuple[str, int], ...] = (
    ("Reallocated_Sector_Ct", 0),
    ("Current_Pending_Sector", 24),
    ("Offline_Uncorrectable", 24),
    ("UDMA_CRC_Error_Count", 0),
    ("Power_On_Hours", 31250),
)
DOSSIER_C_SMART_VERDICT = smart_verdict(dict(DOSSIER_C_SMART))


def smart_document_lines() -> tuple[str, ...]:
    lines = [
        "Relevé SMART — disque dur 2 To de données (SATA_1), utilitaire du fabricant (fictif)",
        "Résultat global : PASSED",
        "Attribut                      Valeur brute",
    ]
    lines += [f"{name:<30}{value}" for name, value in DOSSIER_C_SMART]
    return tuple(lines)


EX01_FIGURES: tuple[Figure, ...] = (BOARD_FIGURE, LEDS_FIGURE, TEMPERATURE_FIGURE)
# Schémas aussi servis comme documents des questions (fichier statique, même SVG).
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (BOARD_FIGURE, BOARD_FIGURE_FILE),
    (LEDS_FIGURE, LEDS_FIGURE_FILE),
)


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma : le SVG du cours, précédé d'un titre
    et d'une description accessibles (le fichier est affiché dans une balise `<img>`)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

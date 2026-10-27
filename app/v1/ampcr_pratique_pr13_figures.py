"""PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose » — données de référence, règles de
choix et de pose, schémas SVG (ticket #216).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket216_ampcr_pratique_pr13.py` :

- la désignation normalisée du blindage X/YTP (ISO/IEC 11801) : `parse_designation`,
  `structure_of`, coupes dessinées depuis la désignation (`section_svg`) ; les noms historiques
  UTP, FTP, STP (`HISTORICAL`) ;
- les catégories 5e, 6 et 6A (`CATEGORIES` de PR15), les conducteurs rigides ou
  souples (`CONDUCTORS`) et le marquage d'une gaine (`JACKET_FIELDS`) ;
- le câble coaxial (structure et familles reprises de PR16 : `CABLE_TYPES`,
  `coax_section_svg`) ;
- le choix d'un câble selon les contraintes (`Need`, `choose`, `CHOICE_TREE`) ;
- les règles de pose : rayon de courbure (`min_bend_radius_mm`), traction (`PULL_MAX_N`),
  séparation des câbles électriques (`SEPARATION_MM`, `min_separation_mm`), contrôle d'un
  tronçon (`Run`, `run_errors`) ; longueurs (`channel_errors`) ; repérage (`label_for`) ;
- deux procédures illustrées (`CHOICE_STEPS`, `POSE_STEPS`).

Valeurs de référence :
- TIA-568 (ANSI/TIA-568.2-D et 568.0) : rayon de courbure minimal d'un câble 4 paires installé
  = 4 × son diamètre extérieur s'il n'est pas écranté, 8 × s'il l'est ; traction maximale
  110 N (25 lbf) pendant le tirage ; lien permanent ≤ 90 m, canal ≤ 100 m ; détorsadage
  ≤ 13 mm au raccordement ;
- EN 50174-2 : distance minimale entre câbles de données et câbles d'énergie selon la classe
  de séparation du câble de données (a à d, donnée par le fabricant), sans cloison et pour
  trois circuits d'énergie au plus : 300, 100, 50 et 10 mm ; davantage de circuits ou de
  courant multiplie la distance, une cloison métallique la réduit (tableaux de la norme) ;
- coaxial : rayon de courbure donné par le fabricant ; à défaut, le cours retient 10 × le
  diamètre (**convention du cours**).

Les règles de choix (blindage selon les perturbations et la possibilité de mise à la terre) et
le schéma d'étiquetage sont des **conventions du cours**, signalées comme telles. Chaque schéma
porte son information en texte (désignation, ✓ / ✗, valeurs en toutes lettres) : la couleur
n'est qu'un repère, le schéma reste lisible imprimé en noir et blanc. Aucun schéma ne vient
d'une image générée ni d'une photographie.
"""

from dataclasses import dataclass

from app.v1.ampcr_pratique_pr15_figures import (
    CHANNEL_MAX_M,
    CORDS_MAX_M,
    PERMANENT_LINK_MAX_M,
    chain_svg,
)
from app.v1.ampcr_pratique_pr16_figures import (
    THIN_SEGMENT_MAX_M,
    coax_section_svg,
    fr,
)
from app.v1.ampcr_pratique_visuals import (
    WIRE_COLORS,
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    step_flow_svg,
    two_lists_svg,
)

WRITTEN_AT = "octobre 2026"
_STROKE = "#33415c"
_FOIL = "#8a96a6"
_BAD = "#b3261e"
_OK = "#1d6b34"

# =============================================================================================
# 1. Blindage : désignation X/YTP (ISO/IEC 11801)
# =============================================================================================

# Lettres : U = aucun écran, F = écran en feuille (foil), S = tresse (shield/braid).
OVERALL_TEXT: dict[str, str] = {
    "U": "aucun écran global",
    "F": "écran global en feuille",
    "S": "tresse globale",
    "SF": "tresse et feuille globales",
}
PAIR_TEXT: dict[str, str] = {
    "U": "paires non écrantées",
    "F": "chaque paire sous feuille",
    "S": "chaque paire sous tresse",
}

STRUCT_NONE = "Aucun écran"
STRUCT_OVERALL = "Écran global seulement"
STRUCT_PAIR = "Écran par paire seulement"
STRUCT_BOTH = "Écran global et écran par paire"
STRUCTURES = (STRUCT_NONE, STRUCT_OVERALL, STRUCT_PAIR, STRUCT_BOTH)


def parse_designation(designation: str) -> tuple[str, str]:
    """« S/FTP » → ("S", "F") : protection globale (U, F, S ou SF) et protection de chaque
    paire (U, F ou S). Lève `ValueError` pour une désignation qui n'est pas de la forme X/YTP."""
    overall, sep, rest = designation.partition("/")
    if not sep or not rest.endswith("TP") or overall not in OVERALL_TEXT or rest[:-2] not in PAIR_TEXT:
        raise ValueError(f"Désignation X/YTP invalide : {designation!r}")
    return overall, rest[:-2]


def structure_of(designation: str) -> str:
    overall, pair = parse_designation(designation)
    if overall == "U":
        return STRUCT_NONE if pair == "U" else STRUCT_PAIR
    return STRUCT_OVERALL if pair == "U" else STRUCT_BOTH


def is_screened(designation: str) -> bool:
    return structure_of(designation) != STRUCT_NONE


def describe(designation: str) -> str:
    overall, pair = parse_designation(designation)
    return f"{OVERALL_TEXT[overall]}, {PAIR_TEXT[pair]}"


# Les quatre constructions du ticket, avec leur usage typique (convention du cours).
SHIELDINGS: tuple[tuple[str, str], ...] = (
    ("U/UTP", "Bureaux, salles de classe : perturbations faibles ; le plus simple et le moins cher."),
    ("F/UTP", "Perturbations moyennes (néons, ascenseur, photocopieurs) ; système blindé relié à la terre."),
    ("U/FTP", "Fréquent en Cat6A : l'écran de chaque paire réduit aussi la diaphonie entre câbles voisins."),
    ("S/FTP", "Atelier, industrie, local technique chargé : perturbations fortes ; système blindé relié à la terre."),
)

# Noms historiques → désignation normalisée. « FTP » et « STP » sont ambigus selon les
# fabricants : seule la notation X/YTP de la fiche technique fait foi.
HISTORICAL: tuple[tuple[str, str, str], ...] = (
    ("UTP", "U/UTP", "Sans ambiguïté : aucun écran."),
    ("FTP", "F/UTP le plus souvent", "Parfois employé pour U/FTP : lire la fiche technique."),
    ("STP", "S/FTP, S/UTP ou F/FTP selon le fabricant",
     "Ambigu ; à l'origine, câble IBM de type 1 (150 Ω, Token Ring), sans rapport avec l'Ethernet actuel."),
    ("S/STP, PiMF", "S/FTP", "Anciennes appellations du câble à tresse globale et paires sous feuille."),
)

PAIR_COLORS: tuple[str, ...] = ("bleu", "orange", "vert", "marron")  # paires 1 à 4 (TIA-568)


def _cross_section(cx: int, cy: int, designation: str) -> list[str]:
    """Coupe d'un câble 4 paires : gaine, tresse et/ou feuille globales, quatre paires (deux
    conducteurs chacune), feuille ou tresse autour de chaque paire selon la désignation."""
    overall, pair = parse_designation(designation)
    parts = [f'<g data-designation="{designation}" data-overall="{overall}" data-pair="{pair}">']
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="#e4e7ec" stroke="{_STROKE}" stroke-width="2"/>')
    if "S" in overall:
        parts.append(
            f'<circle data-overall-braid="1" cx="{cx}" cy="{cy}" r="56" fill="none" stroke="{_STROKE}" '
            f'stroke-width="4" stroke-dasharray="2 2"/>'
        )
    if "F" in overall:
        radius = 51 if "S" in overall else 55
        parts.append(
            f'<circle data-overall-foil="1" cx="{cx}" cy="{cy}" r="{radius}" fill="#ffffff" stroke="{_FOIL}" stroke-width="3"/>'
        )
    for index, (dx, dy) in enumerate(((-21, -21), (21, -21), (-21, 21), (21, 21))):
        px, py = cx + dx, cy + dy
        color = WIRE_COLORS[PAIR_COLORS[index]]
        if pair != "U":
            dash = ' stroke-dasharray="2 2"' if pair == "S" else ""
            parts.append(
                f'<circle data-pair-screen="{pair}" cx="{px}" cy="{py}" r="17" fill="#ffffff" stroke="{_FOIL}" '
                f'stroke-width="2.5"{dash}/>'
            )
        parts.append(f'<circle cx="{px - 7}" cy="{py}" r="6.5" fill="{color}" stroke="{_STROKE}"/>')
        parts.append(f'<circle cx="{px + 7}" cy="{py}" r="6.5" fill="#ffffff" stroke="{color}" stroke-width="3"/>')
    parts.append("</g>")
    return parts


def section_svg(designations: tuple[str, ...]) -> str:
    """Coupes côte à côte (deux par ligne), chacune légendée en toutes lettres."""
    width, cell_w, cell_h = 380, 190, 218
    rows = (len(designations) + 1) // 2
    parts: list[str] = []
    for index, designation in enumerate(designations):
        x0, y0 = (index % 2) * cell_w, (index // 2) * cell_h
        cx, cy = x0 + cell_w // 2, y0 + 92
        parts.append(_text_lines(cx, y0 + 18, [designation], size=14, weight="700", anchor="middle"))
        parts += _cross_section(cx, cy, designation)
        overall, pair = parse_designation(designation)
        lines = [f"Global : {OVERALL_TEXT[overall]}", f"Paire : {PAIR_TEXT[pair]}"]
        wrapped = [w for line in lines for w in _wrap(line, 30)]
        parts.append(_text_lines(cx, y0 + 172, wrapped, size=10.5, step=13, anchor="middle"))
    return _svg(width, rows * cell_h + 6, parts)


SECTION_DESIGNATIONS = tuple(d for d, _u in SHIELDINGS)

# =============================================================================================
# 2. Catégories, conducteurs, marquage
# =============================================================================================

SOLID = "Monobrin (rigide) : installation fixe, poinçonné"
STRANDED = "Multibrin (souple) : cordon, fiches serties"
CONDUCTOR_KINDS = (SOLID, STRANDED)

CONDUCTORS: tuple[tuple[str, str, str], ...] = (
    ("Monobrin (solid, « /1 » sur la gaine)",
     "Câble permanent : chemins de câbles, goulottes, entre panneau et prise murale",
     "Poinçonnage sur keystone et panneau (contacts autodénudants) ; moins d'atténuation, mais casse s'il est plié souvent"),
    ("Multibrin (stranded, « /7 » sur la gaine)",
     "Cordons de brassage et de poste, souvent manipulés",
     "Fiches à sertir pour multibrin ; plus souple, atténuation un peu plus forte : longueur des cordons limitée"),
)

# Marquage type d'une gaine (fictif mais construit comme un marquage réel) et sa lecture.
JACKET_MARKING = "CAT.6A U/FTP 4x2xAWG23/1 500 MHz LSZH Dca 0127 m"
JACKET_FIELDS: tuple[tuple[str, str], ...] = (
    ("CAT.6A", "Catégorie 6A : performances garanties jusqu'à 500 MHz, 10 Gb/s sur 100 m"),
    ("U/FTP", "Aucun écran global, chaque paire sous feuille : système écranté, mise à la terre"),
    ("4x2xAWG23/1", "4 paires de 2 conducteurs, diamètre AWG 23, monobrin (/1) : câble d'installation"),
    ("500 MHz", "Fréquence jusqu'à laquelle les performances de la catégorie sont garanties"),
    ("LSZH", "Gaine à faible dégagement de fumée et sans halogène"),
    ("Dca", "Classe de réaction au feu (règlement européen des produits de construction)"),
    ("0127 m", "Repère métrique : la différence entre deux repères donne la longueur tirée"),
)

# =============================================================================================
# 3. Choisir un câble selon les contraintes (convention du cours)
# =============================================================================================

EMI_LOW = "faibles"
EMI_MEDIUM = "moyennes"
EMI_HIGH = "fortes"

SERVICE_ETHERNET = "réseau Ethernet"
SERVICE_VIDEO = "vidéo analogique (caméra, enregistreur)"
SERVICE_TV = "télévision, satellite"
SERVICE_10BASE2 = "ancien réseau Ethernet coaxial 10BASE2"

FAMILY_UUTP = "U/UTP"
FAMILY_FUTP = "F/UTP"
FAMILY_SFTP = "S/FTP"
FAMILY_FIBRE = "Fibre optique"
FAMILY_COAX75 = "Coaxial 75 Ω"
FAMILY_COAX50 = "Coaxial 50 Ω"
FAMILIES = (FAMILY_UUTP, FAMILY_FUTP, FAMILY_SFTP, FAMILY_FIBRE, FAMILY_COAX75, FAMILY_COAX50)


@dataclass(frozen=True)
class Need:
    service: str = SERVICE_ETHERNET
    rate_gbps: float = 1
    length_m: float = 50
    emi: str = EMI_LOW
    grounded: bool = True  # système blindé de bout en bout et baie reliée à la terre possibles


@dataclass(frozen=True)
class Choice:
    family: str
    cable: str
    connector: str
    reason: str


def category_for(rate_gbps: float) -> str:
    """Catégorie minimale pour le débit sur un canal de 100 m (TIA-568, IEEE 802.3)."""
    if rate_gbps <= 1:
        return "Cat5e"
    if rate_gbps <= 10:
        return "Cat6A"
    raise ValueError("Au-delà de 10 Gb/s, le cuivre à paires torsadées n'est pas retenu dans ce cours.")


def choose(need: Need) -> Choice:
    """Règle de choix du cours : service → famille ; Ethernet : longueur (≤ 100 m), débit →
    catégorie, perturbations et possibilité de mise à la terre → blindage."""
    if need.service == SERVICE_VIDEO:
        return Choice(FAMILY_COAX75, "Coaxial 75 Ω (RG-59)", "BNC 75 Ω",
                      "Vidéo analogique : impédance 75 Ω de la caméra et de l'enregistreur.")
    if need.service == SERVICE_TV:
        return Choice(FAMILY_COAX75, "Coaxial 75 Ω (RG-6)", "Fiches F",
                      "Télévision et satellite : 75 Ω, fiches F vissées.")
    if need.service == SERVICE_10BASE2:
        if need.length_m > THIN_SEGMENT_MAX_M:
            raise ValueError("Segment 10BASE2 limité à 185 m.")
        return Choice(FAMILY_COAX50, "Coaxial 50 Ω (RG-58)", "BNC 50 Ω, T et terminateurs 50 Ω",
                      "Maintenance d'un bus 10BASE2 existant : 50 Ω partout.")
    if need.length_m > CHANNEL_MAX_M or need.rate_gbps > 10:
        return Choice(FAMILY_FIBRE, "Fibre optique (PR17)", "Selon la fibre",
                      f"Au-delà de {CHANNEL_MAX_M} m (ou de 10 Gb/s), la paire torsadée ne convient plus.")
    category = category_for(need.rate_gbps)
    if need.emi == EMI_LOW:
        return Choice(FAMILY_UUTP, f"{category} U/UTP", "8P8C non blindé",
                      "Perturbations faibles : un câble non écranté suffit.")
    if need.emi == EMI_MEDIUM:
        if need.grounded:
            return Choice(FAMILY_FUTP, f"{category} F/UTP", "8P8C blindé",
                          "Perturbations moyennes et système blindé relié à la terre : écran global.")
        return Choice(FAMILY_UUTP, f"{category} U/UTP", "8P8C non blindé",
                      "Écran impossible à relier à la terre : U/UTP et séparation renforcée.")
    if need.grounded:
        return Choice(FAMILY_SFTP, f"{category} S/FTP", "8P8C blindé",
                      "Perturbations fortes : tresse globale et paires écrantées, mises à la terre.")
    return Choice(FAMILY_FIBRE, "Fibre optique (PR17)", "Selon la fibre",
                  "Perturbations fortes sans mise à la terre possible : la fibre n'y est pas sensible.")


CHOICE_TREE: tuple[tuple[str, str], ...] = (
    ("Faut-il un réseau Ethernet actuel ?", "Vidéo : coaxial 75 Ω (RG-59, BNC 75 Ω) ; TV : RG-6 et fiches F"),
    (f"Longueur ≤ {CHANNEL_MAX_M} m et débit ≤ 10 Gb/s ?", "Fibre optique (PR17)"),
    ("Perturbations moyennes ou fortes ?", "Faibles : U/UTP suffit"),
    ("Écran relié à la terre possible de bout en bout ?",
     "Moyennes : U/UTP et séparation renforcée ; fortes : fibre optique"),
)
CHOICE_FINAL = "Moyennes : F/UTP ; fortes : S/FTP. Catégorie : Cat5e pour 1 Gb/s, Cat6A pour 10 Gb/s."

CHOICE_STEPS: tuple[tuple[str, str], ...] = (
    ("Besoin", "Service (Ethernet, vidéo, TV), débit attendu aujourd'hui et demain, nombre de prises."),
    ("Longueur", "Mesurer le parcours réel : ≤ 90 m de lien permanent, sinon fibre ou équipement actif."),
    ("Environnement", "Perturbations (moteurs, néons, câbles d'énergie), extérieur, feu, humidité."),
    ("Catégorie", "Débit → catégorie minimale ; toute la chaîne de la même catégorie."),
    ("Blindage", "Selon les perturbations, seulement si la terre et la continuité sont assurées."),
    ("Consigner", "Référence exacte (catégorie, X/YTP, AWG, gaine) sur le bon de commande et le plan."),
)

# =============================================================================================
# 4. Règles de pose
# =============================================================================================

BEND_FACTOR_UNSCREENED = 4
BEND_FACTOR_SCREENED = 8
BEND_FACTOR_COAX = 10  # convention du cours quand la fiche du fabricant manque
PULL_MAX_N = 110  # câble 4 paires, pendant le tirage (TIA-568)
UNTWIST_MAX_MM = 13

# EN 50174-2 : distance minimale sans cloison, jusqu'à trois circuits d'énergie, selon la classe
# de séparation du câble de données (donnée par le fabricant).
SEPARATION_MM: dict[str, int] = {"a": 300, "b": 100, "c": 50, "d": 10}
SEPARATION_UNKNOWN_MM = SEPARATION_MM["a"]  # classe inconnue : cas le plus défavorable


def min_bend_radius_mm(diameter_mm: float, designation: str | None) -> float:
    """Rayon de courbure intérieur minimal d'un câble installé. `designation` = X/YTP pour une
    paire torsadée, `None` pour un coaxial."""
    if designation is None:
        factor = BEND_FACTOR_COAX
    else:
        factor = BEND_FACTOR_SCREENED if is_screened(designation) else BEND_FACTOR_UNSCREENED
    return round(factor * diameter_mm, 1)


def min_separation_mm(separation_class: str | None) -> int:
    return SEPARATION_MM.get(separation_class or "", SEPARATION_UNKNOWN_MM)


ERR_BEND = "Rayon de courbure trop petit"
ERR_PULL = "Traction excessive au tirage"
ERR_SEPARATION = "Trop près des câbles électriques"
RUN_OK = "Conforme"
RUN_VERDICTS = (RUN_OK, ERR_BEND, ERR_PULL, ERR_SEPARATION)


@dataclass(frozen=True)
class Run:
    """Un tronçon posé, tel que relevé sur le chantier."""

    name: str
    designation: str | None  # None = coaxial
    diameter_mm: float
    bend_radius_mm: float
    pull_n: float
    power_distance_mm: float | None  # None = aucun câble électrique en parallèle
    separation_class: str | None = None
    metal_divider: bool = False


def run_errors(run: Run) -> list[str]:
    errors: list[str] = []
    if run.bend_radius_mm < min_bend_radius_mm(run.diameter_mm, run.designation):
        errors.append(ERR_BEND)
    if run.designation is not None and run.pull_n > PULL_MAX_N:
        errors.append(ERR_PULL)
    if (run.power_distance_mm is not None and not run.metal_divider
            and run.power_distance_mm < min_separation_mm(run.separation_class)):
        errors.append(ERR_SEPARATION)
    return errors


def channel_errors(permanent_m: float, cords_m: float) -> list[str]:
    errors: list[str] = []
    if permanent_m > PERMANENT_LINK_MAX_M:
        errors.append(f"lien permanent de {fr(permanent_m)} m > {PERMANENT_LINK_MAX_M} m")
    if cords_m > CORDS_MAX_M:
        errors.append(f"cordons de {fr(cords_m)} m au total > {CORDS_MAX_M} m")
    if permanent_m + cords_m > CHANNEL_MAX_M:
        errors.append(f"canal de {fr(permanent_m + cords_m)} m > {CHANNEL_MAX_M} m")
    return errors


def label_for(rack: int, panel: int, port: int) -> str:
    """Repère identique aux deux extrémités (convention du cours) : baie, panneau, port."""
    return f"B{rack}-P{panel}-{port:02d}"


POSE_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer", "Plan de câblage, repères des prises, chemins vérifiés (séparation, longueur)."),
    ("Étiqueter", "Même repère aux deux bouts du câble avant de le tirer."),
    ("Tirer", f"Sans dépasser {PULL_MAX_N} N, sans plier sous le rayon minimal, sans vriller."),
    ("Fixer", "Colliers non serrés ou bandes auto-agrippantes ; jamais d'agrafe ; réserve de câble."),
    ("Raccorder", f"Poinçonner selon T568A ou B, détorsader ≤ {UNTWIST_MAX_MM} mm, écran continu."),
    ("Tester et consigner", "Câblage, longueur, performances ; résultats et repères dans le dossier."),
)

# =============================================================================================
# 5. Données des figures
# =============================================================================================

CHAIN_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Switch (baie)", "Équipement actif, baie à la terre"),
    ("Cordon de brassage", "Multibrin, fiches serties"),
    ("Panneau de brassage", "Port repéré B1-P1-07"),
    ("Câble permanent", "Monobrin, poinçonné aux deux bouts"),
    ("Prise murale", "Keystone, repère B1-P1-07"),
    ("Cordon de poste", "Multibrin, prise murale → PC"),
    ("PC", "Carte réseau du poste"),
)
CHAIN_BRACKETS: tuple[tuple[int, int, str], ...] = (
    (3, 5, f"lien permanent ≤ {PERMANENT_LINK_MAX_M} m"),
    (1, 7, f"canal ≤ {CHANNEL_MAX_M} m"),
)

SCREEN_OK: tuple[str, ...] = (
    "Panneau de brassage blindé relié à la baie",
    "Baie reliée à la barrette de terre",
    "Câble écranté, écran repris à 360°",
    "Keystones blindés aux deux bouts",
    "Cordons blindés jusqu'aux équipements",
)
SCREEN_BROKEN: tuple[str, ...] = (
    "Keystone non blindé : écran interrompu",
    "Écran coupé ras, non raccordé",
    "Baie non reliée à la terre",
    "Cordon non blindé sur un poste",
    "Câble écranté sur panneau non blindé",
)


def bend_svg(examples: tuple[tuple[str, str | None, float], ...]) -> str:
    """Rayon de courbure minimal dessiné à l'échelle (1 mm = 1 px) pour des câbles donnés :
    (nom, désignation ou None pour un coaxial, diamètre en mm)."""
    width = 380
    parts = [_text_lines(width // 2, 18, ["Rayon de courbure minimal (à l'échelle 1:1 à l'écran)"],
                         size=12.5, weight="700", anchor="middle")]
    x = 14
    for name, designation, diameter in examples:
        radius = min_bend_radius_mm(diameter, designation)
        factor = round(radius / diameter)
        cy = 40 + radius
        # Quart de cercle : le câble arrive à la verticale et repart à l'horizontale.
        parts.append(
            f'<path data-radius="{fr(radius)}" d="M{x} 40 A{radius} {radius} 0 0 0 {x + radius} {cy}" '
            f'fill="none" stroke="{_STROKE}" stroke-width="{diameter}" stroke-linecap="butt" opacity="0.8"/>'
        )
        parts.append(f'<path d="M{x + radius} 40 L{x + radius} {cy}" stroke="{_OK}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        parts.append(f'<circle cx="{x + radius}" cy="40" r="2.5" fill="{_OK}"/>')
        lines = [name, f"Ø {fr(diameter)} mm × {factor}", f"R ≥ {fr(radius)} mm"]
        parts.append(_text_lines(x, cy + 24, lines, size=11, step=14))
        x += max(int(radius) + 34, 110)
    height = 40 + max(min_bend_radius_mm(d, des) for _n, des, d in examples) + 70
    return _svg(width, int(height), parts)


BEND_EXAMPLES: tuple[tuple[str, str | None, float], ...] = (
    ("Cat6 U/UTP", "U/UTP", 6.0),
    ("Cat6A S/FTP", "S/FTP", 7.5),
    ("RG-59 (coaxial)", None, 6.1),
)


def separation_svg() -> str:
    """Barres horizontales : distance minimale sans cloison selon la classe EN 50174-2."""
    width, left, scale = 380, 92, 0.85  # 300 mm → 255 px
    parts = [_text_lines(width // 2, 18, ["Distance minimale aux câbles d'énergie (sans cloison)"],
                         size=12.5, weight="700", anchor="middle")]
    y = 36
    for cls, mm in SEPARATION_MM.items():
        bar = max(mm * scale, 3)
        parts.append(_text_lines(8, y + 15, [f"Classe {cls}"], size=12, weight="700"))
        parts.append(
            f'<rect data-class="{cls}" data-mm="{mm}" x="{left}" y="{y}" width="{bar:.1f}" height="20" '
            f'rx="3" fill="#dbe4f3" stroke="{_STROKE}"/>'
        )
        label_x = left + bar + 6
        anchor = "start"
        if label_x > width - 60:
            label_x, anchor = left + bar - 6, "end"
        parts.append(_text_lines(int(label_x), y + 15, [f"{mm} mm"], size=12, weight="700", anchor=anchor))
        y += 32
    notes = _wrap("Classe donnée par le fabricant du câble de données (a = la moins protégée). "
                  "Jusqu'à 3 circuits ; au-delà, distance multipliée. Inconnue : 300 mm.", 58)
    parts.append(_text_lines(8, y + 10, notes, size=11, step=14))
    return _svg(width, y + 14 * len(notes) + 8, parts)


# =============================================================================================
# 6. Figures du cours
# =============================================================================================

SECTIONS_FIGURE = Figure(
    key="pr13-coupes-paires",
    title="Coupes de quatre câbles à paires torsadées : U/UTP, F/UTP, U/FTP, S/FTP",
    alt=(
        "Quatre coupes de câble à 4 paires (8 conducteurs). "
        + " ".join(f"{d} : {describe(d)}." for d in SECTION_DESIGNATIONS)
        + " La première lettre décrit la protection globale, la lettre avant TP celle de chaque paire."
    ),
    caption=(
        "Lire X/YTP : X = protection globale, Y = protection de chaque paire ; U = aucune, "
        "F = feuille, S = tresse. Trait plein gris = feuille, pointillé épais = tresse."
    ),
    svg=section_svg(SECTION_DESIGNATIONS),
)

COAX_FIGURE = Figure(
    key="pr13-coupe-coaxial",
    title="Coupe annotée d'un câble coaxial",
    alt=(
        "Coupe d'un coaxial en cercles concentriques, du centre vers l'extérieur : 1 âme (conducteur "
        "central en cuivre), 2 diélectrique (isolant), 3 blindage (feuille et/ou tresse), 4 gaine. "
        "Dessous, le même câble vu de côté, dénudé en gradins : gaine, blindage, diélectrique, âme."
    ),
    caption=(
        "Âme, diélectrique, blindage, gaine : le rapport des diamètres de l'âme et du blindage et "
        "le diélectrique fixent l'impédance (50 Ω ou 75 Ω), marquée sur la gaine."
    ),
    svg=coax_section_svg(),
)

CHOICE_FIGURE = Figure(
    key="pr13-arbre-choix",
    title="Arbre de choix d'un câble",
    alt=(
        "Quatre questions successives ; une réponse non mène à une piste. "
        + " ".join(f"{i}. {q} Si non : {n}." for i, (q, n) in enumerate(CHOICE_TREE, start=1))
        + f" Si oui à tout : {CHOICE_FINAL}"
    ),
    caption="Règle de choix du cours (convention) : on part du service, puis longueur, mise à la terre et perturbations.",
    svg=decision_tree_svg(CHOICE_TREE, CHOICE_FINAL),
)

CHOICE_STEPS_FIGURE = Figure(
    key="pr13-procedure-choix",
    title="Procédure 1 — Choisir un câble",
    alt="Six étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(CHOICE_STEPS, start=1)),
    caption="Le choix se justifie par écrit : besoin, longueur, environnement, catégorie, blindage, référence.",
    svg=step_flow_svg(CHOICE_STEPS),
)

POSE_FIGURE = Figure(
    key="pr13-procedure-pose",
    title="Procédure 2 — Poser un câble à paires torsadées",
    alt="Six étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(POSE_STEPS, start=1)),
    caption="Pose professionnelle : on prépare et on étiquette avant de tirer, on teste et on consigne après.",
    svg=step_flow_svg(POSE_STEPS),
)

CHAIN_FIGURE = Figure(
    key="pr13-chaine-baie-prise",
    title="De la baie à la prise : éléments et longueurs",
    alt=(
        "Sept éléments de haut en bas : "
        + " ; ".join(f"{i}. {n} ({d})" for i, (n, d) in enumerate(CHAIN_ELEMENTS, start=1))
        + f". Accolade du panneau à la prise murale : lien permanent de {PERMANENT_LINK_MAX_M} m au plus. "
        f"Accolade du switch au PC : canal de {CHANNEL_MAX_M} m au plus, cordons compris."
    ),
    caption=(
        f"Monobrin dans le lien permanent (≤ {PERMANENT_LINK_MAX_M} m), multibrin dans les cordons "
        f"(≤ {CORDS_MAX_M} m au total) ; même repère au panneau et à la prise."
    ),
    svg=chain_svg(CHAIN_ELEMENTS, CHAIN_BRACKETS),
)

SCREEN_FIGURE = Figure(
    key="pr13-continuite-ecran",
    title="Blindage efficace ou interrompu",
    alt=(
        "Deux colonnes. Écran efficace : " + " ; ".join(SCREEN_OK)
        + ". Écran interrompu : " + " ; ".join(SCREEN_BROKEN) + "."
    ),
    caption="Un câble écranté n'apporte rien si un seul maillon interrompt l'écran ou si la terre manque.",
    svg=two_lists_svg("Écran efficace", SCREEN_OK, "Écran interrompu", SCREEN_BROKEN),
)

BEND_FIGURE = Figure(
    key="pr13-rayon-courbure",
    title="Rayon de courbure minimal de trois câbles",
    alt=(
        "Trois quarts de cercle à l'échelle. "
        + " ".join(
            f"{name} : diamètre {fr(d)} mm, rayon minimal {fr(min_bend_radius_mm(d, des))} mm."
            for name, des, d in BEND_EXAMPLES
        )
        + " Facteur 4 pour un câble non écranté, 8 pour un câble écranté, 10 pour le coaxial (convention du cours)."
    ),
    caption=(
        f"Rayon minimal = {BEND_FACTOR_UNSCREENED} × Ø (non écranté), {BEND_FACTOR_SCREENED} × Ø (écranté), "
        f"{BEND_FACTOR_COAX} × Ø pour un coaxial si la fiche du fabricant manque."
    ),
    svg=bend_svg(BEND_EXAMPLES),
)

SEPARATION_FIGURE = Figure(
    key="pr13-separation-energie",
    title="Distance minimale entre câbles de données et câbles d'énergie",
    alt=(
        "Barres horizontales, sans cloison, jusqu'à trois circuits d'énergie : "
        + ", ".join(f"classe {c} {mm} mm" for c, mm in SEPARATION_MM.items())
        + ". Classe inconnue : 300 mm. Une cloison métallique réduit la distance."
    ),
    caption="Valeurs de la norme EN 50174-2 sans cloison ; le croisement d'un câble d'énergie se fait à angle droit.",
    svg=separation_svg(),
)

PR13_FIGURES: tuple[Figure, ...] = (
    SECTIONS_FIGURE,
    SCREEN_FIGURE,
    COAX_FIGURE,
    CHOICE_FIGURE,
    CHOICE_STEPS_FIGURE,
    CHAIN_FIGURE,
    SEPARATION_FIGURE,
    BEND_FIGURE,
    POSE_FIGURE,
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Choisir un câble", CHOICE_STEPS),
    ("Poser un câble à paires torsadées", POSE_STEPS),
)


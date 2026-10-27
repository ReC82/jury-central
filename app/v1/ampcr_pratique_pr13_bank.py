"""PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose » — exercices corrigés et mini-examen
(ticket #216).

Même organisation que PR12 (`app.v1.ampcr_pratique_pr12_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 17 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (pose, choix, chaîne de la baie au poste), classements
  (structure d'après la désignation X/YTP, câble selon les contraintes, conformité d'un tronçon
  posé, monobrin ou multibrin, coaxial 50 Ω ou 75 Ω), documents (marquage de gaine, longueurs,
  continuité de l'écran, rayon de courbure, étiquetage), commande « FTP » ambiguë, comparatif,
  coaxial écrasé, procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations sont **fictives** ; désignations, choix, rayons, distances, longueurs et repères
viennent de `app.v1.ampcr_pratique_pr13_figures` (mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr13_figures import (
    CHAIN_ELEMENTS,
    CHOICE_STEPS,
    CONDUCTOR_KINDS,
    EMI_HIGH,
    EMI_LOW,
    EMI_MEDIUM,
    FAMILIES,
    POSE_STEPS,
    PULL_MAX_N,
    RUN_OK,
    RUN_VERDICTS,
    SERVICE_10BASE2,
    SERVICE_TV,
    SERVICE_VIDEO,
    SOLID,
    STRANDED,
    STRUCTURES,
    Need,
    Run,
    channel_errors,
    choose,
    fr,
    label_for,
    min_bend_radius_mm,
    min_separation_mm,
    run_errors,
    structure_of,
)
from app.v1.ampcr_pratique_pr16_figures import CABLE_IMPEDANCE

PR13_CODE = "PR13"

KIND_ORDER = "ordonnancement"
KIND_STRUCTURE = "lecture d'une désignation"
KIND_CHOICE = "choix selon les contraintes"
KIND_POSE = "règles de pose"
KIND_COAX = "câble coaxial"
KIND_ERROR = "repérage d'erreurs"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-18", "AP-20"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(POSE_STEPS)
E02_STEPS = _labels(CHOICE_STEPS)
E03_STEPS = _labels(CHAIN_ELEMENTS)

E04_DESIGNATIONS = ("F/UTP", "U/UTP", "S/FTP", "U/FTP", "SF/UTP", "F/FTP", "S/UTP")
E04_CORRECT = tuple(STRUCTURES.index(structure_of(d)) for d in E04_DESIGNATIONS)

E05_CASES: tuple[tuple[str, Need], ...] = (
    ("Cabinet d'avocats : 1 Gb/s, plus long parcours 55 m, bureaux calmes",
     Need(rate_gbps=1, length_m=55, emi=EMI_LOW)),
    ("Atelier de soudure : NAS à 10 Gb/s à 40 m, perturbations fortes, baie et système blindés reliés à la terre",
     Need(rate_gbps=10, length_m=40, emi=EMI_HIGH, grounded=True)),
    ("Liaison entre deux bâtiments d'une école : 140 m de parcours",
     Need(rate_gbps=1, length_m=140, emi=EMI_LOW)),
    ("Caméra de surveillance analogique vers l'enregistreur, 45 m",
     Need(service=SERVICE_VIDEO, length_m=45)),
    ("Prises de télévision des chambres d'un hôtel",
     Need(service=SERVICE_TV, length_m=30)),
    ("Remplacer un tronçon abîmé du bus 10BASE2 conservé dans un laboratoire de formation",
     Need(service=SERVICE_10BASE2, length_m=12)),
    ("Bureaux voisins de la salle des machines d'un ascenseur : perturbations moyennes, système blindé relié à la terre prévu",
     Need(rate_gbps=1, length_m=60, emi=EMI_MEDIUM, grounded=True)),
    ("Hall de production provisoire : perturbations fortes, aucune terre utilisable pour un écran",
     Need(rate_gbps=1, length_m=70, emi=EMI_HIGH, grounded=False)),
    ("Entrepôt : perturbations moyennes (néons), coffrets et prises en plastique, aucune terre pour un écran",
     Need(rate_gbps=1, length_m=80, emi=EMI_MEDIUM, grounded=False)),
)
E05_CORRECT = tuple(FAMILIES.index(choose(need).family) for _t, need in E05_CASES)

E06_RUNS: tuple[tuple[str, Run], ...] = (
    ("Cat6 U/UTP Ø 6 mm : courbe de rayon 30 mm, tiré à 80 N, câble électrique à 150 mm (câble de classe b)",
     Run("T1", "U/UTP", 6.0, 30, 80, 150, "b")),
    ("Cat6A S/FTP Ø 7,5 mm : angle de goulotte de rayon 40 mm, tiré à 90 N, aucun câble électrique",
     Run("T2", "S/FTP", 7.5, 40, 90, None)),
    ("Cat6 U/UTP Ø 6 mm : courbe de rayon 50 mm, tiré au treuil à 180 N, aucun câble électrique",
     Run("T3", "U/UTP", 6.0, 50, 180, None)),
    ("Cat6 U/UTP Ø 6 mm : courbe de rayon 50 mm, tiré à 60 N, câble électrique à 40 mm (classe c), sans cloison",
     Run("T4", "U/UTP", 6.0, 50, 60, 40, "c")),
    ("Cat6A F/UTP Ø 7 mm : courbe de rayon 60 mm, tiré à 100 N, câble électrique à 20 mm (classe d)",
     Run("T5", "F/UTP", 7.0, 60, 100, 20, "d")),
    ("Coaxial RG-59 Ø 6,1 mm : coude de rayon 30 mm derrière l'enregistreur, aucun câble électrique",
     Run("T6", None, 6.1, 30, 20, None)),
    ("Cat5e U/UTP Ø 5,5 mm : courbe de rayon 30 mm, tiré à 70 N, câble électrique à 200 mm, classe inconnue",
     Run("T7", "U/UTP", 5.5, 30, 70, 200, None)),
    ("Cat6 U/UTP Ø 6 mm : courbe de rayon 40 mm, tiré à 90 N, câble électrique à 30 mm derrière une cloison métallique",
     Run("T8", "U/UTP", 6.0, 40, 90, 30, None, metal_divider=True)),
)


def _verdict(run: Run) -> str:
    errors = run_errors(run)
    if len(errors) > 1:
        raise ValueError(f"{run.name} : un seul défaut par tronçon dans l'exercice.")
    return errors[0] if errors else RUN_OK


E06_CORRECT = tuple(RUN_VERDICTS.index(_verdict(run)) for _t, run in E06_RUNS)

E07_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Câble entre le panneau de brassage et la prise murale du bureau 12", SOLID),
    ("Cordon de 1 m entre le panneau de brassage et le switch, dans la baie", STRANDED),
    ("Cordon de 3 m entre la prise murale et le PC", STRANDED),
    ("Liaison fixe de 40 m entre deux baies, terminée sur panneaux", SOLID),
    ("Câble posé en goulotte jusqu'au keystone de la salle de réunion", SOLID),
    ("Cordon d'une imprimante qu'on déplace souvent", STRANDED),
)

E08_CATEGORIES = ("50 Ω", "75 Ω")
E08_ELEMENTS: tuple[tuple[str, int], ...] = (
    ("Bus Ethernet fin 10BASE2 en RG-58", CABLE_IMPEDANCE["RG-58"]),
    ("Caméra analogique vers enregistreur en RG-59", CABLE_IMPEDANCE["RG-59"]),
    ("Prise d'antenne de télévision en RG-6, fiche F", CABLE_IMPEDANCE["RG-6"]),
    ("Antenne d'un émetteur-récepteur radio en RG-8", CABLE_IMPEDANCE["RG-8"]),
    ("Parabole satellite vers le décodeur en RG-6", CABLE_IMPEDANCE["RG-6"]),
    ("Terminateur placé au bout d'un bus 10BASE2", 50),
    ("Liaison vidéo numérique SDI d'une caméra vers la régie en RG-59", CABLE_IMPEDANCE["RG-59"]),
)
E08_CORRECT = tuple(E08_CATEGORIES.index(f"{ohm} Ω") for _e, ohm in E08_ELEMENTS)

E10_PORTS: tuple[tuple[str, float, float, float], ...] = (
    ("B1-P1-01", 62, 1, 3),
    ("B1-P1-02", 88, 2, 5),
    ("B1-P1-03", 93, 1, 2),
    ("B1-P1-04", 85, 3, 9),
    ("B1-P1-05", 89, 5, 7),
    ("B1-P1-06", 40, 0.5, 2),
)
E10_VERDICTS = {port: channel_errors(perm, a + b) for port, perm, a, b in E10_PORTS}
E10_BAD = tuple(port for port, errors in E10_VERDICTS.items() if errors)

E12_DIAMETER = 7.8
E12_MIN = min_bend_radius_mm(E12_DIAMETER, "S/FTP")
E12_GOULOTTE_R = 40
E12_WIDE_R = 75

E14_ROWS: tuple[tuple[str, str, str], ...] = (
    ("Accueil", label_for(1, 1, 1), label_for(1, 1, 1)),
    ("Bureau 2, prise gauche", label_for(1, 1, 2), label_for(1, 1, 2)),
    ("Bureau 2, prise droite", label_for(1, 1, 3), label_for(1, 1, 4)),
    ("Bureau 3", "(aucune étiquette)", label_for(1, 1, 5)),
    ("Salle de réunion", label_for(1, 1, 6), label_for(1, 1, 6)),
    ("Imprimante du couloir", label_for(1, 1, 6), label_for(1, 1, 7)),
)
E14_BAD = tuple(place for place, wall, panel in E14_ROWS if wall != panel)

X06_MIN = min_separation_mm(None)
X07_DIAMETER = 7.6
X07_MIN = min_bend_radius_mm(X07_DIAMETER, "S/FTP")
X08_ERRORS = channel_errors(92, 2 + 3)

# =============================================================================================
# 17 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la pose d'un câble",
        question_type="ordering",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_ORDER,
        context=(
            "Tu encadres un stagiaire qui doit câbler deux bureaux d'une agence immobilière : "
            "deux câbles Cat6 U/UTP entre la baie du couloir et deux prises murales. La fiche "
            "« pose d'un câble » de l'atelier, collée dans la camionnette, a ses six étapes "
            "dans le désordre."
        ),
        instructions=("Remets les six étapes de la pose dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Préparer → étiqueter → tirer → fixer → raccorder → tester et consigner (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Préparer : plan de câblage, repère de chaque prise, chemin vérifié (longueur, distance aux câbles électriques). 2. Étiqueter le câble aux deux bouts avec le même repère avant de le tirer : une fois dans le faux plafond, on ne sait plus lequel est lequel. 3. Tirer sans dépasser 110 N, sans plier sous le rayon minimal ni vriller.",
            "4. Fixer avec des colliers non serrés ou des bandes auto-agrippantes, jamais d'agrafe, en laissant une réserve. 5. Raccorder : poinçonner selon T568A ou T568B, détorsader 13 mm au plus. 6. Tester (câblage, longueur, performances) et consigner les résultats avec les repères.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le choix d'un câble",
        question_type="ordering",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_ORDER,
        context=(
            "Une imprimerie te demande un devis pour câbler un nouvel atelier. Avant de "
            "commander, ton responsable veut un choix justifié par écrit. Le modèle de "
            "« justification du choix d'un câble » de l'atelier liste six étapes, recopiées "
            "dans le désordre par un collègue."
        ),
        instructions=("Remets les six étapes du choix dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Besoin → longueur → environnement → catégorie → blindage → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. Besoin : quel service (Ethernet, vidéo, télévision), quel débit aujourd'hui et demain, combien de prises. 2. Longueur : on mesure le parcours réel ; au-delà de 90 m de lien permanent, la paire torsadée ne convient plus (fibre ou équipement actif intermédiaire). 3. Environnement : moteurs, néons, câbles d'énergie, extérieur, contraintes de feu.",
            "4. Catégorie : le débit fixe la catégorie minimale, et toute la chaîne (câble, prises, panneau, cordons) doit l'atteindre. 5. Blindage : selon les perturbations, et seulement si l'écran peut être continu et relié à la terre. 6. Consigner la référence exacte (catégorie, X/YTP, AWG, gaine) sur le bon de commande et le plan.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (2, 4, 0, 5, 1, 3)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="De la baie au PC : remettre la chaîne dans l'ordre",
        question_type="ordering",
        requirement_ids=("AP-18",),
        kind=KIND_ORDER,
        context=(
            "Sur le plan de câblage d'une PME, tu dois dessiner le chemin du signal entre le "
            "switch de la baie et le PC d'un comptable. Les sept éléments de la liaison ont été "
            "notés en vrac par le client, qui ne connaît pas le vocabulaire du câblage."
        ),
        instructions=("Remets les sept éléments dans l'ordre, du switch de la baie jusqu'au PC.",),
        criteria=(
            _c("Ordre", 3.5, "Switch → cordon de brassage → panneau de brassage → câble permanent → prise murale → cordon de poste → PC (0,5 pt par élément)."),
        ),
        correction=(
            "Dans la baie : le switch, un cordon de brassage (souple, multibrin) jusqu'au panneau de brassage, où arrive le câble permanent poinçonné. Le câble permanent (monobrin) court dans les chemins de câbles jusqu'à la prise murale du bureau.",
            "Au bureau : la prise murale (keystone poinçonné), puis le cordon de poste (multibrin) jusqu'au PC. Le lien permanent va du panneau à la prise (90 m au plus) ; le canal complet, cordons compris, ne dépasse pas 100 m.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (4, 1, 6, 0, 3, 5, 2)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Sept désignations : quelle construction ?",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_STRUCTURE,
        context=(
            "Le grossiste de l'atelier a envoyé sept bobines de câble à paires torsadées. Sur "
            "chaque gaine, on lit la désignation normalisée X/YTP. Pour ranger le stock, ton "
            "responsable veut savoir, pour chaque bobine, où se trouve l'écran : autour de "
            "l'ensemble des paires, autour de chaque paire, aux deux endroits, ou nulle part."
        ),
        instructions=("Range chaque désignation selon la construction qu'elle décrit.",),
        criteria=(
            _c("Classement", 3.5, "U/UTP → aucun ; F/UTP, SF/UTP, S/UTP → global seul ; U/FTP → par paire seul ; S/FTP, F/FTP → global et par paire (0,5 pt par élément)."),
        ),
        correction=(
            "La lettre avant la barre décrit la protection globale (autour des quatre paires), celle avant « TP » la protection de chaque paire ; U = aucune, F = feuille, S = tresse, SF = tresse et feuille. U/UTP n'a donc aucun écran.",
            "F/UTP (feuille globale), SF/UTP (tresse et feuille globales) et S/UTP (tresse globale) n'ont qu'un écran global. U/FTP n'a qu'un écran autour de chaque paire. S/FTP (tresse globale) et F/FTP (feuille globale) ont en plus chaque paire sous feuille.",
        ),
        classification=Classification(
            categories=STRUCTURES,
            elements=tuple(f"Câble marqué « {d} »" for d in E04_DESIGNATIONS),
            correct=E04_CORRECT,
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Neuf demandes : quel câble ?",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Neuf demandes de devis sont arrivées cette semaine. Pour chacune, tu dois proposer "
            "la famille de câble en appliquant la règle de choix de l'atelier : le service, puis "
            "la longueur (100 m au plus en paire torsadée), puis les perturbations, et un écran "
            "seulement s'il peut être relié à la terre de bout en bout."
        ),
        instructions=("Range chaque demande dans la famille de câble qui convient.",),
        criteria=(
            _c("Classement", 4.5, "Avocats → U/UTP ; soudure 10 Gb/s blindé → S/FTP ; 140 m → fibre ; caméra et TV → coaxial 75 Ω ; 10BASE2 → coaxial 50 Ω ; ascenseur avec terre → F/UTP ; hall sans terre → fibre ; entrepôt sans terre → U/UTP (0,5 pt par élément)."),
        ),
        correction=(
            "Bureaux calmes : U/UTP suffit. Perturbations moyennes avec un système blindé relié à la terre : F/UTP ; fortes : S/FTP. Sans terre possible, un écran n'apporte rien : U/UTP avec une séparation renforcée si les perturbations sont moyennes, fibre optique si elles sont fortes (elle n'y est pas sensible).",
            "Au-delà de 100 m, la paire torsadée ne convient plus : fibre (ou équipement actif intermédiaire). Vidéo analogique et télévision : coaxial 75 Ω (RG-59 avec BNC 75 Ω, RG-6 avec fiches F). Un ancien bus 10BASE2 se répare en coaxial 50 Ω (RG-58), sans mélanger les impédances.",
        ),
        classification=Classification(
            categories=FAMILIES,
            elements=tuple(t for t, _n in E05_CASES),
            correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Huit tronçons posés : conformes ou non ?",
        question_type="classification",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Tu réceptionnes le chantier d'un sous-traitant. Pour huit tronçons, ton relevé "
            "indique le câble, son diamètre, le plus petit rayon de courbure, l'effort de tirage "
            "noté sur le treuil et la distance aux câbles électriques parallèles. Règles : rayon "
            "≥ 4 × Ø (non écranté), 8 × Ø (écranté), 10 × Ø (coaxial) ; tirage ≤ 110 N ; "
            "EN 50174-2 sans cloison : classe b 100 mm, c 50 mm, d 10 mm, inconnue 300 mm."
        ),
        instructions=("Range chaque tronçon : conforme, ou le défaut qu'il présente (un seul défaut au plus par tronçon).",),
        criteria=(
            _c("Classement", 4, "T1, T5, T8 → conformes ; T2 (40 < 60 mm) et T6 (30 < 61 mm) → rayon ; T3 (180 N) → traction ; T4 (40 < 50 mm) et T7 (200 < 300 mm) → câbles électriques (0,5 pt par élément)."),
        ),
        correction=(
            f"Rayons : U/UTP Ø 6 mm → 24 mm au moins (30, 50 et 40 mm conviennent) ; F/UTP Ø 7 mm → 56 mm (60 mm convient) ; S/FTP Ø 7,5 mm → {fr(min_bend_radius_mm(7.5, 'S/FTP'))} mm : 40 mm est trop serré ; RG-59 Ø 6,1 mm → {fr(min_bend_radius_mm(6.1, None))} mm : 30 mm est trop serré. Tirage : 180 N dépasse les {PULL_MAX_N} N admis ; le câble peut être étiré et ses paires déformées.",
            "Séparation : classe b à 150 mm (≥ 100) et classe d à 20 mm (≥ 10) conviennent ; classe c à 40 mm (< 50) ne convient pas ; une classe inconnue impose le cas le plus défavorable, 300 mm, donc 200 mm ne suffit pas. Derrière une cloison métallique, la distance de 30 mm est admise.",
        ),
        classification=Classification(
            categories=RUN_VERDICTS,
            elements=tuple(t for t, _r in E06_RUNS),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Monobrin ou multibrin ?",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_STRUCTURE,
        context=(
            "Tu prépares la commande de câble pour l'installation d'un cabinet médical. Le "
            "grossiste propose chaque référence en conducteurs rigides (monobrin, « /1 ») ou "
            "souples (multibrin, « /7 »). Pour chacun des six usages du devis, indique la "
            "version à commander et la façon de la raccorder."
        ),
        instructions=("Range chaque usage dans le type de conducteur qui convient.",),
        criteria=(
            _c("Classement", 3, "Panneau → prise, liaison entre baies, goulotte → keystone : monobrin poinçonné ; cordons (brassage, poste, imprimante) : multibrin serti (0,5 pt par élément)."),
        ),
        correction=(
            "Tout ce qui est posé une fois pour toutes (lien permanent entre panneau et prise, liaison fixe entre baies, câble en goulotte) est en monobrin : il se poinçonne bien sur les keystones et panneaux et atténue un peu moins, mais casse s'il est plié souvent.",
            "Tout ce qu'on manipule (cordons de brassage, cordons de poste, cordon d'un appareil déplacé) est en multibrin, souple, avec des fiches à sertir prévues pour multibrin ; sa longueur totale reste limitée (10 m pour l'ensemble des cordons d'un canal).",
        ),
        classification=Classification(
            categories=CONDUCTOR_KINDS,
            elements=tuple(e for e, _k in E07_ELEMENTS),
            correct=tuple(CONDUCTOR_KINDS.index(k) for _e, k in E07_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Coaxial : 50 Ω ou 75 Ω ?",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_COAX,
        context=(
            "Un client te confie un carton de chutes de câble coaxial et de connecteurs récupérés "
            "dans un ancien bâtiment. Avant de les réutiliser, tu dois indiquer pour sept usages "
            "l'impédance caractéristique exigée, puisqu'on ne mélange jamais les deux "
            "impédances sur une même liaison."
        ),
        instructions=("Range chaque usage selon l'impédance du coaxial qu'il exige.",),
        criteria=(
            _c("Classement", 3.5, "10BASE2, terminateur, radio RG-8 → 50 Ω ; caméra RG-59, TV, satellite, SDI → 75 Ω (0,5 pt par élément)."),
        ),
        correction=(
            "50 Ω : l'Ethernet coaxial (RG-58 en 10BASE2, coaxial épais en 10BASE5), ses terminateurs 50 Ω, et la radio (RG-58, RG-8) ; cette valeur est un compromis entre puissance transmissible et pertes.",
            "75 Ω : la vidéo et la télévision (RG-59 et BNC 75 Ω pour une caméra ou une liaison SDI, RG-6 et fiches F pour l'antenne et la parabole) ; 75 Ω donne une très faible atténuation. Un câble ou un connecteur de l'autre impédance provoque des réflexions.",
        ),
        classification=Classification(
            categories=E08_CATEGORIES,
            elements=tuple(e for e, _o in E08_ELEMENTS),
            correct=E08_CORRECT,
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Lire le marquage d'une gaine",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_STRUCTURE,
        context=(
            "Sur un chantier, tu trouves une bobine sans étiquette. Le marquage imprimé sur la "
            "gaine est recopié dans le document 1. Le chef de chantier veut l'utiliser pour deux "
            "usages : le lien permanent d'un open space (10 Gb/s, 85 m, baie reliée à la terre) "
            "et la fabrication de cordons de brassage."
        ),
        documents=(_console("Document 1 — Marquage relevé sur la gaine", "CAT.6A U/FTP 4x2xAWG23/1 500 MHz LSZH Dca 0127 m"),),
        instructions=(
            "Explique ce que dit chaque élément du marquage.",
            "Dis, en justifiant, si ce câble convient pour chacun des deux usages.",
        ),
        criteria=(
            _c("Lecture", 1.5, "Cat6A (500 MHz, 10 Gb/s sur 100 m) ; U/FTP : pas d'écran global, chaque paire sous feuille ; 4 paires AWG 23 monobrin (/1) ; LSZH : sans halogène, peu de fumée ; Dca : classe de réaction au feu ; 0127 m : repère métrique."),
            _c("Lien permanent", 0.75, "Convient : Cat6A pour 10 Gb/s, 85 m ≤ 90 m ; câble écranté : keystones, panneau et cordons blindés, écran continu relié à la terre par la baie."),
            _c("Cordons", 0.75, "Ne convient pas : monobrin, prévu pour le poinçonnage ; casse à la manipulation, fiches inadaptées ; prendre du multibrin (/7) ou des cordons fabriqués."),
        ),
        correction=(
            "CAT.6A : catégorie 6A, performances garanties jusqu'à 500 MHz, 10 Gb/s sur 100 m. U/FTP : aucun écran global, chaque paire sous feuille (câble écranté). 4x2xAWG23/1 : quatre paires de deux conducteurs, diamètre AWG 23, monobrin. LSZH : gaine à faible dégagement de fumée, sans halogène. Dca : classe de réaction au feu européenne. 0127 m : repère métrique, utile pour calculer la longueur tirée.",
            "Lien permanent de l'open space : oui, la catégorie 6A tient 10 Gb/s et 85 m reste sous les 90 m ; comme le câble est écranté, il faut des keystones et un panneau blindés et un écran continu, relié à la terre par la baie. Cordons de brassage : non, le monobrin est fait pour être poinçonné une fois ; plié souvent, il casse, et les fiches à sertir doivent correspondre au multibrin.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Relevé des longueurs d'un panneau de brassage",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Avant de signer la réception d'une installation, tu contrôles les longueurs des six "
            "premières liaisons d'un panneau. Le document 1 donne, pour chaque port, la longueur "
            "du lien permanent mesurée par le testeur et la longueur des deux cordons prévus "
            "(brassage dans la baie et cordon de poste)."
        ),
        documents=(
            _table(
                "Document 1 — Longueurs relevées (m)",
                ("Port", "Lien permanent", "Cordon de brassage", "Cordon de poste"),
                *((port, fr(p), fr(a), fr(b)) for port, p, a, b in E10_PORTS),
            ),
        ),
        instructions=(
            "Pour chaque port, indique s'il respecte les longueurs de la norme et, sinon, la règle dépassée.",
            "Propose une correction pour chaque port non conforme.",
        ),
        criteria=(
            _c("Verdicts", 1.5, f"Conformes : 01, 02, 06 ; non conformes : {', '.join(E10_BAD)} — 03 : lien permanent 93 m > 90 ; 04 : cordons 12 m > 10 (canal 97 m) ; 05 : cordons 12 m et canal 101 m > 100."),
            _c("Corrections", 1.5, "03 : déplacer la prise ou passer par un autre chemin, sinon équipement actif plus proche ; 04 et 05 : cordons plus courts (cordon de poste de 5 m, brassage de 1 m) ; recontrôler."),
        ),
        correction=(
            "Règles : lien permanent ≤ 90 m, cordons ≤ 10 m au total, canal ≤ 100 m. 01 (62 + 4 = 66 m), 02 (88 + 7 = 95 m) et 06 (40 + 2,5 = 42,5 m) sont conformes. 03 : 93 m de lien permanent dépassent 90 m, même si le canal (96 m) reste sous 100 m : non conforme.",
            "04 : 12 m de cordons dépassent 10 m (canal 97 m) ; 05 : 12 m de cordons et un canal de 101 m. Corrections : pour 03, raccourcir le parcours (autre chemin, prise déplacée) ou desservir le bureau depuis un équipement plus proche ; pour 04 et 05, cordons plus courts. On recontrôle et l'on consigne les nouvelles valeurs.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Un système écranté qui ne protège pas",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Dans un atelier de mécanique, des PC perdent la connexion quand le compresseur "
            "démarre. L'installateur affirme : « impossible, j'ai posé du F/UTP ». Tu relèves la "
            "composition réelle de trois liaisons (document 1). La barrette de terre du local "
            "technique est à deux mètres de la baie."
        ),
        documents=(
            _table(
                "Document 1 — Relevé de l'installation",
                ("Élément", "Constat"),
                ("Câble des trois liaisons", "Cat6 F/UTP"),
                ("Panneau de brassage", "Blindé, vissé sur la baie"),
                ("Baie", "Aucun conducteur vers la barrette de terre"),
                ("Prises murales", "Keystones non blindés ; feuille du câble coupée ras"),
                ("Cordons de poste", "U/UTP"),
            ),
        ),
        instructions=(
            "Explique pourquoi le câble écranté ne protège pas ces liaisons.",
            "Rédige les corrections à faire et le contrôle final.",
        ),
        criteria=(
            _c("Analyse", 1.5, "Écran interrompu : keystones non blindés, feuille coupée ras ; cordons non blindés ; baie non reliée à la terre : l'écran n'évacue pas les parasites (il peut même les capter)."),
            _c("Corrections", 1.5, "Keystones blindés, écran repris à 360°, cordons blindés ; baie reliée à la barrette de terre (par l'électricien ou selon l'installation) ; séparation du câble du compresseur ; contrôle : continuité de l'écran au testeur, plus de coupure au démarrage."),
        ),
        correction=(
            "Un écran ne protège que s'il est continu de bout en bout et relié à la terre. Ici, il s'arrête aux prises (keystones non blindés, feuille coupée ras), les cordons sont non blindés et la baie n'est pas reliée à la terre : la feuille n'évacue pas les parasites et peut même les capter comme une antenne.",
            "Corrections : keystones blindés avec reprise de l'écran sur tout le pourtour, cordons blindés jusqu'aux PC, baie reliée à la barrette de terre (liaison réalisée selon l'installation électrique, par l'électricien), et vérification de la distance au câble d'alimentation du compresseur. Contrôle : continuité de l'écran au testeur, puis démarrages du compresseur sans perte de connexion ; rapport.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Rayon de courbure dans une goulotte",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Un bureau d'études veut faire passer douze câbles S/FTP dans une goulotte murale. "
            "La fiche du câble (document 1) donne son diamètre. L'angle intérieur standard de la "
            "goulotte impose aux câbles un rayon de 40 mm ; le fabricant propose aussi un angle "
            "à grand rayon (75 mm)."
        ),
        documents=(
            _table(
                "Document 1 — Extrait de la fiche technique",
                ("Caractéristique", "Valeur"),
                ("Désignation", "Cat6A S/FTP 4x2xAWG23/1"),
                ("Diamètre extérieur", f"{fr(E12_DIAMETER)} mm"),
                ("Rayon de courbure minimal (installé)", "8 × diamètre"),
                ("Effort de tirage maximal", f"{PULL_MAX_N} N"),
            ),
        ),
        instructions=(
            "Calcule le rayon de courbure minimal et dis quel angle de goulotte convient.",
            "Explique ce qui arrive si l'on force le câble dans l'angle standard.",
        ),
        criteria=(
            _c("Calcul", 1, f"8 × {fr(E12_DIAMETER)} = {fr(E12_MIN)} mm ; 40 mm < {fr(E12_MIN)} mm : angle standard refusé ; 75 mm ≥ {fr(E12_MIN)} mm : angle à grand rayon."),
            _c("Conséquences", 1, "Paires déformées, torsade et écart modifiés : diaphonie et pertes de retour, écran abîmé ; échec probable aux tests de performance, défaut parfois invisible à l'œil."),
        ),
        correction=(
            f"Rayon minimal : 8 × {fr(E12_DIAMETER)} mm = {fr(E12_MIN)} mm. L'angle standard (40 mm) est plus serré que ce minimum : il est refusé. L'angle à grand rayon (75 mm) le respecte : c'est lui qu'il faut commander.",
            "Forcé dans un angle trop serré, le câble se déforme : les paires changent de géométrie (torsade et écart entre conducteurs), la diaphonie et les réflexions augmentent, l'écran peut se fendre. Le défaut ne se voit pas forcément, mais le lien risque d'échouer aux tests de performance ou de donner des erreurs.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Un coaxial vidéo fixé à l'agrafeuse",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_COAX,
        context=(
            "Dans une boulangerie, l'image d'une caméra analogique est dégradée (traînées, "
            "contours doublés) depuis la pose. Tu constates que le RG-59 a été fixé le long de la "
            "plinthe avec une agrafeuse murale : plusieurs agrafes écrasent la gaine. Les autres "
            "caméras, posées avec des clips, donnent une image nette."
        ),
        instructions=("Explique le lien entre les agrafes et l'image, puis rédige la correction et le contrôle.",),
        criteria=(
            _c("Explication", 1, "Agrafe qui écrase : diélectrique déformé, distance âme/blindage changée → impédance localement différente de 75 Ω → réflexions qui dégradent l'image (traînées, images doublées)."),
            _c("Correction", 1, "Remplacer le tronçon abîmé (ou tout le câble) ; fixer avec des clips adaptés au diamètre, sans serrer ; rayon de courbure respecté ; contrôle : image nette, comparaison avec une autre caméra ; rapport."),
        ),
        correction=(
            "L'impédance d'un coaxial dépend de la géométrie : diamètre de l'âme, diamètre du blindage et diélectrique entre les deux. Une agrafe qui écrase la gaine déforme le diélectrique et rapproche le blindage de l'âme : à cet endroit, l'impédance n'est plus 75 Ω, une partie du signal est réfléchie et revient en retard, d'où les traînées et les contours doublés.",
            "Correction : remplacer le câble abîmé (au moins le tronçon agrafé, sans multiplier les raccords), le fixer avec des clips adaptés au diamètre, sans serrer, en respectant le rayon de courbure. Contrôle : image nette, comparable aux autres caméras ; rapport mentionnant le remplacement.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Contrôler l'étiquetage d'une installation",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_ERROR,
        context=(
            "Une agence de voyages t'appelle : on ne retrouve plus quel port du panneau dessert "
            "quel bureau. La règle de l'atelier impose le même repère aux deux bouts de chaque "
            "câble (baie, panneau, port). Tu relèves les étiquettes des prises murales et du "
            "panneau de brassage (document 1)."
        ),
        documents=(
            _table(
                "Document 1 — Étiquettes relevées",
                ("Emplacement de la prise", "Étiquette de la prise murale", "Port du panneau relié (testeur)"),
                *E14_ROWS,
            ),
        ),
        instructions=(
            "Relève les anomalies d'étiquetage.",
            "Rédige la correction et ce qu'il faut mettre à jour.",
        ),
        criteria=(
            _c("Anomalies", 1.5, "Bureau 2 droite : prise B1-P1-03 reliée au port 04 ; bureau 3 : prise sans étiquette (port 05) ; imprimante : prise B1-P1-06 en double (reliée au port 07)."),
            _c("Correction", 1.5, "Réétiqueter chaque prise d'après le port réellement relié (repéré au testeur), étiquettes durables et lisibles aux deux bouts ; mettre à jour le plan de câblage et le tableau de brassage ; contrôle final de chaque correspondance."),
        ),
        correction=(
            f"Trois anomalies : {', '.join(E14_BAD)}. Au bureau 2, la prise droite porte B1-P1-03 mais elle est reliée au port 04 ; au bureau 3, la prise n'a pas d'étiquette (elle est reliée au port 05) ; la prise de l'imprimante porte B1-P1-06, déjà utilisé par la salle de réunion, alors qu'elle est reliée au port 07.",
            "On réétiquette chaque prise d'après le port réellement relié, identifié au testeur, avec une étiquette durable aux deux bouts du câble. On met à jour le plan de câblage et le tableau de brassage de la baie, puis l'on contrôle chaque correspondance. Un repère unique et identique aux deux bouts évite de débrancher le mauvais poste.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="U/UTP, F/UTP ou S/FTP pour une école ?",
        question_type="long_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Une école rénove ses salles de classe (perturbations faibles) et son atelier de "
            "mécanique (moteurs, poste à souder : perturbations fortes). La direction veut "
            "comprendre la différence de prix entre les câbles U/UTP, F/UTP et S/FTP proposés "
            "dans le devis. Une baie reliée à la terre est prévue dans chaque bâtiment."
        ),
        instructions=(
            "Compare les trois câbles : construction, protection contre les parasites, mise en œuvre, coût.",
            "Recommande un câble pour les classes et un pour l'atelier, en justifiant.",
        ),
        criteria=(
            _c("Comparaison", 2, "U/UTP : sans écran, le plus fin et souple, rayon 4 × Ø, pas de terre, moins cher ; F/UTP : feuille globale, protection moyenne ; S/FTP : tresse et paires sous feuille, meilleure protection et moins de diaphonie, plus épais et cher, rayon 8 × Ø ; les deux derniers exigent une chaîne blindée continue reliée à la terre."),
            _c("Recommandation", 1, "Classes : U/UTP (perturbations faibles) ; atelier : S/FTP avec chaîne blindée et terre de la baie ; catégorie selon le débit (Cat6A si 10 Gb/s)."),
        ),
        correction=(
            "U/UTP : aucun écran ; la torsade suffit contre les perturbations faibles ; câble fin et souple (rayon de courbure 4 × Ø), connecteurs simples, pas de mise à la terre : le moins cher. F/UTP : une feuille autour des quatre paires ; meilleure protection contre les perturbations moyennes. S/FTP : tresse globale et chaque paire sous feuille ; meilleure protection et moins de diaphonie, mais câble plus épais, plus raide (8 × Ø) et plus cher.",
            "Les deux câbles écrantés n'ont d'intérêt que si toute la chaîne est blindée (keystones, panneau, cordons) et reliée à la terre ; la pose est plus longue. Recommandation : U/UTP dans les classes, où les perturbations sont faibles ; S/FTP dans l'atelier, avec chaîne blindée continue et baie reliée à la terre. Catégorie selon le débit voulu : Cat6A si l'on vise 10 Gb/s.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Une commande de « câble FTP »",
        question_type="short_answer",
        requirement_ids=("AP-18",),
        kind=KIND_STRUCTURE,
        context=(
            "Le cahier des charges d'un client demande « du câble FTP Cat6 ». Chez le grossiste, "
            "deux références répondent à la recherche « FTP » : une Cat6 F/UTP et une Cat6 U/FTP, "
            "à des prix différents. Ton collègue veut prendre la moins chère sans poser de "
            "question."
        ),
        instructions=("Explique le problème et rédige ce que tu fais avant de commander.",),
        criteria=(
            _c("Problème", 1, "« FTP » est un nom historique ambigu : F/UTP (feuille globale) ou U/FTP (feuille par paire) ; constructions différentes, connecteurs et mise en œuvre à adapter."),
            _c("Démarche", 1, "Faire préciser par le client la désignation X/YTP (ou la déduire du besoin : perturbations, diaphonie, système blindé), la noter sur le bon de commande ; prévoir prises et cordons blindés et la terre."),
        ),
        correction=(
            "« FTP » est une appellation historique : selon les fabricants, elle désigne un câble à feuille globale (F/UTP) ou un câble à feuille autour de chaque paire (U/FTP). Ce ne sont pas les mêmes câbles : l'U/FTP réduit aussi la diaphonie entre paires et entre câbles voisins, la préparation de l'écran au raccordement diffère.",
            "Avant de commander, on fait préciser la désignation normalisée X/YTP par le client (ou on la propose d'après le besoin) et on l'écrit sur le bon de commande. Dans les deux cas, le câble est écranté : il faut des prises, un panneau et des cordons blindés, et une baie reliée à la terre.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Corriger la fiche de pose d'un collègue",
        question_type="long_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a rédigé la fiche « pose rapide » de l'atelier. Elle dit : 1) passer le "
            "câble réseau dans la même goulotte que le 230 V, collé contre lui, c'est plus propre ; "
            "2) tirer fort, le câble est solide ; 3) fixer avec l'agrafeuse ; 4) détorsader 5 cm "
            "pour poinçonner plus facilement ; 5) étiqueter plus tard ; 6) pas besoin de tester "
            "si le PC se connecte."
        ),
        instructions=("Relève chaque erreur, explique le risque et rédige la version correcte de chaque point.",),
        criteria=(
            _c("Séparation et tirage", 1.5, "1) parasites induits : chemin séparé, distance selon la classe (300 mm si inconnue) ou cloison métallique, croisement à angle droit ; 2) ≤ 110 N, sinon paires étirées et déformées."),
            _c("Fixation et raccordement", 1.5, "3) agrafe : câble écrasé, paires déformées : colliers non serrés ou bandes auto-agrippantes ; 4) détorsadage ≤ 13 mm, sinon diaphonie au raccordement."),
            _c("Repérage et tests", 1, "5) étiqueter avant de tirer, même repère aux deux bouts ; 6) tester chaque lien (câblage, longueur, performances) et consigner : un PC qui se connecte ne prouve ni le débit ni l'absence d'erreurs."),
        ),
        correction=(
            "1) Collé contre un câble 230 V, le câble de données capte des parasites : on utilise un chemin séparé ou une goulotte à compartiments avec cloison, à la distance exigée par la classe du câble (300 mm si on ne la connaît pas), et l'on croise le 230 V à angle droit. 2) Tiré trop fort (au-delà de 110 N), le câble s'étire et ses paires se déforment. 3) Une agrafe écrase le câble : on fixe avec des colliers non serrés ou des bandes auto-agrippantes.",
            "4) Détorsader 5 cm supprime la protection de la torsade au raccordement : 13 mm au plus. 5) On étiquette avant de tirer, avec le même repère aux deux bouts, sinon on ne sait plus quel câble arrive où. 6) Un PC qui se connecte ne prouve pas que le lien tient son débit : on teste chaque lien (câblage, longueur, performances) et l'on consigne les résultats.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions × 2 points = /20 (réserve « Examen blanc »)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Câbler un cabinet comptable",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Un cabinet comptable fait câbler douze bureaux. Les postes travaillent à 1 Gb/s ; "
            "le plus long parcours entre la baie et une prise mesure 68 m. Les bureaux sont "
            "calmes : pas de machine, pas de câble électrique de forte puissance. Le budget est "
            "serré et aucune baie reliée à la terre n'est prévue."
        ),
        instructions=("Propose le câble (catégorie et blindage) et justifie chaque choix.",),
        criteria=(
            _c("Choix", 1, "Paire torsadée U/UTP, Cat5e au minimum (Cat6 acceptée comme marge) ; prises et cordons de la même catégorie."),
            _c("Justification", 1, "1 Gb/s sur ≤ 100 m : Cat5e suffit ; 68 m < 90 m de lien permanent ; perturbations faibles et pas de terre : un écran n'apporterait rien et coûterait plus cher."),
        ),
        correction=(
            "Câble à paires torsadées U/UTP, catégorie 5e au minimum (une catégorie 6 donne de la marge pour l'avenir), avec prises, panneau et cordons de la même catégorie au moins.",
            "Justification : la Cat5e tient 1 Gb/s sur un canal de 100 m, et 68 m restent sous les 90 m de lien permanent. Les perturbations sont faibles et aucune terre n'est prévue : un câble écranté n'apporterait rien ici, compliquerait la pose et coûterait plus cher.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Relier le NAS d'une menuiserie",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Dans une menuiserie, le NAS doit être relié à 10 Gb/s au switch de la baie, à 35 m, "
            "en passant au-dessus des machines à moteur et de leurs variateurs de vitesse "
            "(perturbations fortes). La baie est reliée à la barrette de terre du bâtiment et "
            "l'installateur peut fournir un système blindé complet."
        ),
        instructions=("Propose le câble et la connectique, et dis ce qu'il faut respecter à la pose pour que le choix soit efficace.",),
        criteria=(
            _c("Choix", 1, "Cat6A (10 Gb/s sur 100 m) S/FTP : tresse globale et paires sous feuille, adaptés aux perturbations fortes ; keystones, panneau et cordons blindés Cat6A."),
            _c("Pose", 1, "Écran continu de bout en bout, repris à 360°, relié à la terre par la baie ; distance aux câbles d'énergie, croisement à angle droit ; rayon ≥ 8 × Ø ; test, dont continuité de l'écran."),
        ),
        correction=(
            "Câble Cat6A, seule catégorie qui garantit 10 Gb/s sur 100 m, en S/FTP : la tresse globale et la feuille autour de chaque paire protègent contre les fortes perturbations des moteurs et variateurs. Toute la connectique est blindée et de catégorie 6A.",
            "Le choix n'est efficace que si l'écran est continu (keystones et panneau blindés, écran repris sur tout le pourtour, cordons blindés) et relié à la terre par la baie. On respecte aussi la distance aux câbles d'énergie (croisement à angle droit) et le rayon de courbure (8 × le diamètre), puis on teste le lien, continuité de l'écran comprise.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Relier deux bâtiments à 160 m",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_CHOICE,
        context=(
            "Une entreprise veut relier le switch de ses bureaux à celui de l'entrepôt, à 160 m "
            "de câble en passant dans une gaine enterrée entre les deux bâtiments. Le gérant "
            "propose « un grand câble Cat6A S/FTP, c'est le meilleur », pour éviter d'acheter "
            "autre chose."
        ),
        instructions=("Dis si la proposition convient et propose la solution, en justifiant.",),
        criteria=(
            _c("Refus justifié", 1, "Paire torsadée limitée à 100 m de canal (90 m de lien permanent), quel que soit le blindage ou la catégorie : 160 m impossible d'un seul tenant."),
            _c("Solution", 1, "Fibre optique entre les deux bâtiments (longue distance, insensible aux parasites, pas de liaison électrique entre deux terres différentes), avec câble prévu pour l'extérieur ; détail en PR17."),
        ),
        correction=(
            "La proposition ne convient pas : une liaison en paire torsadée est limitée à 100 m de canal (dont 90 m de lien permanent), quelle que soit la catégorie ou le blindage. Un Cat6A S/FTP de 160 m ne respecte pas la norme et ne garantit aucun débit.",
            "Solution : une fibre optique entre les deux switchs. Elle couvre largement 160 m, n'est pas sensible aux parasites et ne relie pas électriquement deux bâtiments dont les terres peuvent avoir des potentiels différents ; le câble doit être prévu pour l'extérieur (gaine enterrée). Le choix de la fibre est détaillé dans le cours PR17.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Une bobine pour le lien permanent ?",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_STRUCTURE,
        context=(
            "Un client a acheté lui-même une bobine pour faire câbler ses bureaux : liens "
            "permanents de la baie aux prises murales, 1 Gb/s, perturbations moyennes, baie "
            "reliée à la terre. Le marquage de la gaine est recopié dans le document 1. Il veut "
            "savoir si tu peux l'utiliser."
        ),
        documents=(_console("Document 1 — Marquage relevé sur la gaine", "CAT.5E F/UTP 4x2xAWG26/7 100 MHz PVC 0042 m"),),
        instructions=("Lis le marquage et dis, en justifiant, si ce câble convient pour ces liens permanents.",),
        criteria=(
            _c("Lecture", 1, "Cat5e (100 MHz, 1 Gb/s) ; F/UTP : feuille globale, adaptée aux perturbations moyennes ; AWG26/7 : multibrin (/7) fin, câble de cordon."),
            _c("Conclusion", 1, "Ne convient pas pour le lien permanent : multibrin non prévu pour le poinçonnage des keystones et panneaux, atténuation plus forte ; prendre du Cat5e (ou plus) F/UTP monobrin (/1) ; la bobine peut servir à faire des cordons."),
        ),
        correction=(
            "CAT.5E : catégorie 5e, 100 MHz, suffisante pour 1 Gb/s. F/UTP : feuille autour des quatre paires, adaptée aux perturbations moyennes avec une baie reliée à la terre. 4x2xAWG26/7 : quatre paires de conducteurs AWG 26 multibrins (sept brins) : c'est un câble de cordon.",
            "Il ne convient donc pas aux liens permanents : le multibrin n'est pas fait pour le poinçonnage sur keystones et panneaux (mauvais contact), et ses pertes plus fortes réduisent la longueur admise. Il faut un câble Cat5e ou mieux, F/UTP, monobrin (« /1 ») ; la bobine du client peut servir à fabriquer des cordons.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Caméra branchée avec du RG-58",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_COAX,
        context=(
            "Pour relier une caméra analogique à l'enregistreur, à 80 m, un bricoleur a utilisé "
            "une chute de RG-58 et des fiches BNC 50 Ω récupérées sur un ancien réseau. L'image "
            "est floue sur les contours et présente des traînées. La caméra et l'enregistreur "
            "ont des entrées et sorties vidéo 75 Ω."
        ),
        instructions=("Explique l'origine du défaut et rédige la correction.",),
        criteria=(
            _c("Cause", 1, "RG-58 et BNC 50 Ω sur une liaison vidéo 75 Ω : désadaptation d'impédance → réflexions (traînées, contours doublés), et pertes plus fortes du RG-58 sur 80 m."),
            _c("Correction", 1, "Remplacer par du coaxial 75 Ω (RG-59) avec des BNC 75 Ω sertis, d'une seule longueur, sans T ni terminateur ; contrôle de l'image ; on ne mélange jamais 50 et 75 Ω."),
        ),
        correction=(
            "La caméra et l'enregistreur ont une impédance de 75 Ω. Le RG-58 et les BNC récupérés sont des éléments 50 Ω, prévus pour l'Ethernet 10BASE2 : l'impédance de la ligne ne correspond plus à celle des appareils, une partie du signal se réfléchit (traînées, contours doublés), et le RG-58, plus fin, affaiblit davantage le signal sur 80 m.",
            "Correction : poser un coaxial 75 Ω (RG-59) d'une seule longueur, avec des fiches BNC 75 Ω serties à l'outil adapté, sans T ni terminateur (liaison point à point). Contrôle : image nette ; rapport. On ne mélange jamais les deux impédances sur une même liaison.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Câble réseau contre le 230 V",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Dans un magasin, un câble Cat6 U/UTP a été posé sur 12 m dans la même goulotte que "
            "trois circuits 230 V, à 2 cm d'eux, sans cloison. La fiche du câble n'indique pas "
            "sa classe de séparation. La caisse perd parfois le réseau quand le four voisin "
            "démarre."
        ),
        instructions=("Explique le problème et rédige la correction conforme.",),
        criteria=(
            _c("Problème", 1, f"Couplage avec les câbles d'énergie (parasites au démarrage du four) ; classe inconnue : il faut appliquer la distance la plus grande, {X06_MIN} mm sans cloison, 20 mm ne suffisent pas."),
            _c("Correction", 1, "Chemin séparé à la bonne distance, ou goulotte à compartiments avec cloison métallique ; croiser le 230 V à angle droit ; retester le lien et vérifier la caisse au démarrage du four."),
        ),
        correction=(
            f"Le câble de données suit trois circuits 230 V à 2 cm : au démarrage du four, le courant appelé crée des parasites que le câble capte. Sans classe de séparation connue, on applique le cas le plus défavorable de la norme EN 50174-2 : {X06_MIN} mm sans cloison. 20 mm ne suffisent pas.",
            "Correction : faire passer le câble dans un chemin séparé, à la distance exigée, ou dans une goulotte à compartiments avec cloison métallique ; croiser les câbles d'énergie à angle droit. Contrôle : nouveau test du lien et observation de la caisse au démarrage du four ; rapport.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Câble S/FTP plié derrière une baie",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            f"Derrière une baie, des câbles Cat6A S/FTP de {fr(X07_DIAMETER)} mm de diamètre ont "
            "été pliés à angle vif pour entrer dans le panneau de brassage : le rayon intérieur "
            "mesure environ 25 mm. Deux des liens échouent aux tests de performance alors que le "
            "câblage broche à broche est correct."
        ),
        instructions=("Calcule le rayon minimal, explique les échecs et rédige la correction.",),
        criteria=(
            _c("Calcul et cause", 1, f"Écranté : 8 × {fr(X07_DIAMETER)} = {fr(X07_MIN)} mm ; 25 mm est bien trop serré : paires déformées, écran abîmé → diaphonie et réflexions : échec aux tests de performance malgré un câblage correct."),
            _c("Correction", 1, f"Reprendre le cheminement (anneaux ou guide-câbles, réserve) avec un rayon ≥ {fr(X07_MIN)} mm ; remplacer et reraccorder les câbles abîmés si le test échoue encore ; retester et consigner."),
        ),
        correction=(
            f"Pour un câble écranté, le rayon de courbure minimal est 8 fois son diamètre : 8 × {fr(X07_DIAMETER)} mm = {fr(X07_MIN)} mm. À 25 mm, le câble est plié bien trop serré : les paires changent de géométrie et l'écran peut se fendre. Un testeur de câblage simple voit les huit conducteurs bien reliés, mais la diaphonie et les réflexions font échouer les tests de performance.",
            f"Correction : reprendre le cheminement derrière la baie (guide-câbles, anneaux, réserve de câble) pour garder un rayon d'au moins {fr(X07_MIN)} mm ; si les liens échouent encore, remplacer et reraccorder les câbles abîmés. Retester et consigner les résultats.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Une prise à 92 m du panneau",
        question_type="short_answer",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Le testeur mesure 92 m de lien permanent entre le panneau de brassage et la prise "
            "du bureau le plus éloigné d'un entrepôt. Le poste sera relié avec un cordon de 2 m "
            "dans la baie et un cordon de 3 m au bureau. L'installateur affirme que « tout va "
            "bien, le total fait moins de 100 m »."
        ),
        instructions=("Dis si l'installateur a raison, en justifiant, et propose une solution.",),
        criteria=(
            _c("Analyse", 1, "Canal 97 m ≤ 100 m, mais lien permanent 92 m > 90 m : non conforme ; les deux règles s'appliquent, le lien permanent a sa propre limite."),
            _c("Solution", 1, "Raccourcir le parcours (autre chemin, prise déplacée) ou rapprocher l'équipement actif (switch d'étage relié par fibre ou câble conforme) ; retester ; consigner."),
        ),
        correction=(
            f"L'installateur a tort. Le canal fait 92 + 2 + 3 = 97 m, sous les 100 m, mais le lien permanent de 92 m dépasse la limite de 90 m : {', '.join(X08_ERRORS)}. Les deux règles s'appliquent ; le lien permanent a sa propre limite, et le lien ne peut pas être déclaré conforme.",
            "Solution : raccourcir le parcours (autre chemin de câbles, prise déplacée plus près) ou rapprocher l'équipement actif, par exemple un switch installé dans l'entrepôt et relié à la baie par une fibre ou un câble conforme. On reteste ensuite et l'on consigne la nouvelle mesure.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Écran raccordé d'un seul côté",
        question_type="document_analysis",
        requirement_ids=("AP-20",),
        kind=KIND_POSE,
        context=(
            "Dans un laboratoire, des liaisons F/UTP restent perturbées par un appareil de mesure "
            "voisin. Le relevé de l'installation (document 1) décrit chaque maillon d'une "
            "liaison type. L'installateur dit avoir « fait au mieux avec les pièces du stock »."
        ),
        documents=(
            _table(
                "Document 1 — Relevé d'une liaison type",
                ("Maillon", "Constat"),
                ("Baie", "Reliée à la barrette de terre"),
                ("Panneau de brassage", "Non blindé (plastique)"),
                ("Câble", "Cat6 F/UTP, feuille repliée sur la gaine"),
                ("Prise murale", "Keystone blindé, écran repris à 360°"),
                ("Cordons", "Blindés"),
            ),
        ),
        instructions=("Explique pourquoi l'écran ne joue pas son rôle et rédige la correction.",),
        criteria=(
            _c("Analyse", 1, "Panneau non blindé : l'écran du câble n'est pas raccordé à la baie, donc pas à la terre ; feuille repliée sans contact ; l'écran flotte et peut capter les parasites."),
            _c("Correction", 1, "Panneau blindé relié à la baie, écran du câble repris à 360° dans chaque connecteur ; contrôle de la continuité de l'écran au testeur ; observation avec l'appareil de mesure en marche ; rapport."),
        ),
        correction=(
            "La baie est reliée à la terre, mais le panneau de brassage est en plastique, non blindé : l'écran du câble n'y est raccordé à rien, il n'est donc relié ni à la baie ni à la terre. La feuille simplement repliée sur la gaine n'assure aucun contact. L'écran « flotte » : il n'évacue pas les parasites et peut même les capter.",
            "Correction : remplacer le panneau par un panneau blindé fixé et relié à la baie, et reprendre l'écran du câble sur tout le pourtour dans chaque connecteur. Contrôle : continuité de l'écran mesurée au testeur, puis fonctionnement avec l'appareil de mesure en marche ; rapport.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Repérer et réceptionner trois prises",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_POSE,
        context=(
            "Tu viens de poser trois liens Cat6 U/UTP entre le panneau 1 de la baie 1 (ports 10, "
            "11 et 12) et trois prises du bureau d'un notaire. Avant de partir, tu dois les "
            "repérer selon la règle de l'atelier (baie, panneau, port) et réaliser la réception "
            "de l'installation."
        ),
        instructions=("Rédige les repères des trois liens et la liste des contrôles et documents de réception.",),
        criteria=(
            _c("Repères", 1, f"{label_for(1, 1, 10)}, {label_for(1, 1, 11)}, {label_for(1, 1, 12)} : même repère au port du panneau et sur la prise murale, étiquettes durables ; plan de câblage mis à jour."),
            _c("Réception", 1, "Tests de chaque lien : câblage broche à broche (wiremap), longueur (≤ 90 m), performances de la catégorie ; résultats enregistrés avec les repères dans le dossier remis au client."),
        ),
        correction=(
            f"Repères : {label_for(1, 1, 10)}, {label_for(1, 1, 11)} et {label_for(1, 1, 12)} (baie 1, panneau 1, port), écrits à l'identique sur le port du panneau et sur la prise murale correspondante, avec des étiquettes durables ; le plan de câblage et le tableau de brassage sont mis à jour.",
            "Réception : chaque lien est testé (câblage broche à broche, longueur sous 90 m, performances de la catégorie 6 avec un testeur qui les mesure). Les résultats sont enregistrés avec leurs repères et remis au client avec le plan.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
        ):
            errors.append(f"{item.key} : classification incohérente.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
        if not REQ & set(item.requirement_ids):
            errors.append(f"{item.key} : au moins une exigence du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

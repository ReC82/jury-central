"""PR18 « Installation physique d'un mini-réseau » — exercices corrigés et mini-examen
(ticket #219).

Même organisation que PR17 (`app.v1.ampcr_pratique_pr17_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (installation, tests du câblage, validation),
  classements (implantation, choix du support, rapport de recette, premier contrôle en échec),
  **cinq schémas à compléter** (plan des locaux, baie, chaîne d'un lien, étoile, plan de
  brassage, servis en SVG), **quatre devis et nomenclatures** (nomenclature d'un plan, devis à
  vérifier, choix d'un switch PoE, baie), longueurs, sécurité, analyse du besoin, dossier de
  recette ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, prix et appareils sont **fictifs** ; tous les nombres des énoncés, barèmes et
corrigés viennent des fonctions de `app.v1.ampcr_pratique_pr18_figures` (mêmes données que les
schémas) et des règles de PR13 (choix du câble, séparation).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr13_figures import (
    EMI_HIGH,
    EMI_LOW,
    EMI_MEDIUM,
    FAMILY_COAX75,
    FAMILY_FIBRE,
    FAMILY_FUTP,
    FAMILY_UUTP,
    SERVICE_TV,
    SERVICE_VIDEO,
    Need,
    choose,
)
from app.v1.ampcr_pratique_pr18_figures import (
    CHAIN_CORDS_M,
    CHAIN_PERMANENT_M,
    CHECK_STEPS,
    D_GW,
    D_IP,
    D_NET,
    D_PEER,
    D_PHYS,
    D_SHARE,
    DIAGNOSES,
    INSTALL_STEPS,
    PATCH_BLANKS,
    PATCH_ROWS,
    PERMANENT_LINK_MAX_M,
    PLACEMENT,
    PLAN_BLANKS,
    PLAN_QUOTE,
    PLAN_QUOTE_TOTALS,
    PLAN_RUNS,
    POE_CLASS_W,
    POE_KO,
    POE_OK,
    RACK_BLANK_TOTAL_U,
    STATIC_BY_KEY,
    TEST_STEPS,
    TEST_VERDICTS,
    VAT_RATE,
    LinkTest,
    QuoteLine,
    RackItem,
    boxes_needed,
    channel_errors,
    choose_rack,
    choose_switch,
    euro,
    first_failure,
    fr,
    link_verdict,
    min_separation_mm,
    panels_needed,
    poe_budget_w,
    poe_verdict,
    quote_totals,
    rack_units,
    run_length_m,
    switch_ports_needed,
    validation_diagnosis,
)

PR18_CODE = "PR18"

KIND_ORDER = "ordonnancement"
KIND_PLAN = "implantation et choix du matériel"
KIND_SCHEMA = "schéma à compléter"
KIND_QUOTE = "devis et nomenclature"
KIND_TEST = "tests, validation et recette"
KIND_SAFETY = "sécurité"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-36", "AP-38"})


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(INSTALL_STEPS)
E02_STEPS = _labels(CHECK_STEPS)
E03_STEPS = _labels(TEST_STEPS)

PLACE_NAMES = tuple(name for name, _w, _r in PLACEMENT)
PLACE_RACK, PLACE_BOX, PLACE_AP, PLACE_OUTLET, PLACE_PATH = PLACE_NAMES
E04_CASES: tuple[tuple[str, str], ...] = (
    ("Point d'où partent tous les câbles des prises, au milieu des bureaux", PLACE_RACK),
    ("Là où la ligne de l'opérateur entre dans le bâtiment", PLACE_BOX),
    ("Faux plafond du couloir, à bonne distance des câbles électriques", PLACE_PATH),
    ("Au plafond, au centre de l'open space, loin de l'armoire métallique", PLACE_AP),
    ("Deux à côté de chaque bureau, une près de l'imprimante", PLACE_OUTLET),
    ("Local fermé à clé et ventilé, accès réservé au service informatique", PLACE_RACK),
    ("Goulotte le long des plinthes, qui croise les câbles électriques à angle droit", PLACE_PATH),
    ("Au milieu de la zone à couvrir, en hauteur, alimenté par son câble réseau", PLACE_AP),
)
E04_CORRECT = tuple(PLACE_NAMES.index(p) for _t, p in E04_CASES)

E05_CATEGORIES = (FAMILY_UUTP, FAMILY_FUTP, FAMILY_FIBRE, FAMILY_COAX75)
E05_CASES: tuple[tuple[str, Need], ...] = (
    ("Liaison vers le switch du bâtiment voisin, 140 m, 10 Gb/s", Need(rate_gbps=10, length_m=140)),
    ("Poste de bureau à 35 m de la baie, 1 Gb/s, bureaux calmes", Need(rate_gbps=1, length_m=35)),
    ("Caméra analogique existante vers l'enregistreur vidéo", Need(service=SERVICE_VIDEO, length_m=30)),
    ("Poste d'atelier à 40 m, perturbations moyennes, baie et prises blindées reliées à la terre",
     Need(rate_gbps=1, length_m=40, emi=EMI_MEDIUM, grounded=True)),
    ("Poste près d'une presse, fortes perturbations, aucune mise à la terre possible",
     Need(rate_gbps=1, length_m=30, emi=EMI_HIGH, grounded=False)),
    ("Point d'accès Wi-Fi à 25 m, 1 Gb/s, faux plafond de bureaux", Need(rate_gbps=1, length_m=25, emi=EMI_LOW)),
    ("Antenne de télévision vers l'écran de la salle d'attente", Need(service=SERVICE_TV, length_m=20)),
    ("Poste à 20 m près de néons, perturbations moyennes, terre impossible à assurer",
     Need(rate_gbps=1, length_m=20, emi=EMI_MEDIUM, grounded=False)),
)
E05_CHOICES = tuple(choose(n) for _t, n in E05_CASES)
E05_CORRECT = tuple(E05_CATEGORIES.index(c.family) for c in E05_CHOICES)

E06_TESTS: tuple[LinkTest, ...] = (
    LinkTest("B1-P1-04 : câblage correct, 41 m, FAIL (paradiaphonie)", True, 41, "FAIL"),
    LinkTest("B1-P1-01 : câblage correct, 18 m, PASS", True, 18, "PASS"),
    LinkTest("B1-P1-05 : fil 7 coupé, 22 m, FAIL", False, 22, "FAIL"),
    LinkTest("B1-P1-03 : câblage correct, 94 m, FAIL", True, 94, "FAIL"),
    LinkTest("B1-P1-02 : paire 3-6 inversée, 17 m, FAIL", False, 17, "FAIL"),
    LinkTest("B1-P1-06 : câblage correct, 63 m, PASS", True, 63, "PASS"),
    LinkTest("B1-P1-08 : câblage correct, 27 m, FAIL (perte d'insertion)", True, 27, "FAIL"),
    LinkTest("B1-P1-07 : câblage correct, 92 m, FAIL (longueur)", True, 92, "FAIL"),
)
E06_CORRECT = tuple(TEST_VERDICTS.index(link_verdict(t)) for t in E06_TESTS)

E07_CASES: tuple[tuple[str, str], ...] = (
    ("Box et autres postes répondent ; aucun site ne s'ouvre, ni par son nom ni par son adresse", "internet"),
    ("Voyant du port éteint au switch et sur le PC, cordon de poste changé sans effet", "lien"),
    ("Tout répond, Internet fonctionne ; « Accès refusé » en ouvrant \\\\SERVEUR\\Compta", "partage"),
    ("ipconfig affiche 169.254.12.7, aucune passerelle", "adresse"),
    ("ping de la box réussi ; ping du poste de l'accueil sans réponse, ce poste est éteint", "poste"),
    ("Adresse 192.168.1.23 correcte ; le ping de la box 192.168.1.1 échoue, les autres postes aussi", "passerelle"),
    ("Voyant éteint sur un poste neuf : la prise B1-P1-09 n'est brassée sur aucun port", "lien"),
)
E07_CORRECT = tuple(DIAGNOSES.index(validation_diagnosis(first_failure(k))) for _t, k in E07_CASES)

PLAN_MAX_RUN = max(length for _k, _h, length in PLAN_RUNS)
E10_ERRORS = channel_errors(CHAIN_PERMANENT_M, CHAIN_CORDS_M)

E13_RUNS: tuple[tuple[str, float], ...] = (
    ("Accueil, poste (2 prises)", 9.5),
    ("Bureau, poste (2 prises)", 14.0),
    ("Bureau, imprimante", 6.0),
    ("Salle de pause, point d'accès Wi-Fi", 21.5),
)
E13_PRISES = (2, 2, 1, 1)
E13_LENGTHS = tuple(run_length_m(h) for _t, h in E13_RUNS)
E13_LINKS = sum(E13_PRISES)
E13_TOTAL_M = sum(length * n for length, n in zip(E13_LENGTHS, E13_PRISES, strict=True))
E13_ALL_LENGTHS = tuple(length for length, n in zip(E13_LENGTHS, E13_PRISES, strict=True) for _ in range(n))
E13_BOXES = boxes_needed(E13_ALL_LENGTHS)
E13_SWITCH = choose_switch(E13_LINKS)
E13_PORTS = switch_ports_needed(E13_LINKS)

# Devis à vérifier : trois erreurs volontaires (quantité de keystones, total d'une ligne, taux de TVA).
E14_WRONG_KS_QTY = len(PATCH_ROWS)
E14_WRONG_CP_TOTAL = round(next(line.total for line in PLAN_QUOTE if line.ref == "CP3") - 10, 2)
E14_WRONG_VAT_RATE = 0.06


def _e14_written_total(line: QuoteLine) -> float:
    if line.ref == "KS":
        return round(E14_WRONG_KS_QTY * line.unit_price, 2)
    if line.ref == "CP3":
        return E14_WRONG_CP_TOTAL
    return line.total


E14_WRITTEN_HT = round(sum(_e14_written_total(line) for line in PLAN_QUOTE), 2)
E14_WRITTEN_VAT = round(E14_WRITTEN_HT * E14_WRONG_VAT_RATE, 2)
E14_WRITTEN_TTC = round(E14_WRITTEN_HT + E14_WRITTEN_VAT, 2)
E14_HT, E14_VAT, E14_TTC = PLAN_QUOTE_TOTALS
E14_KS = next(line for line in PLAN_QUOTE if line.ref == "KS")
E14_CP = next(line for line in PLAN_QUOTE if line.ref == "CP3")

# Choix d'un switch : 6 postes à 1 prise utilisée, 1 imprimante, 1 AP (classe 4), 2 caméras
# (classe 3), 4 téléphones IP (classe 2) branchés sur leur propre prise.
E15_DEVICES: tuple[tuple[str, int, int | None], ...] = (
    ("Postes de travail", 6, None),
    ("Imprimante", 1, None),
    ("Point d'accès Wi-Fi (classe 4)", 1, 4),
    ("Caméras IP (classe 3)", 2, 3),
    ("Téléphones IP (classe 2)", 4, 2),
)
E15_LINKS = sum(q for _n, q, _c in E15_DEVICES)
E15_CLASSES = tuple(c for _n, q, c in E15_DEVICES if c is not None for _ in range(q))
E15_POE = poe_budget_w(E15_CLASSES)
E15_PORTS = switch_ports_needed(E15_LINKS)
E15_CATALOGUE: tuple[tuple[str, int, float, float], ...] = (  # (réf., ports, budget PoE W, prix HT)
    ("S1", 24, 65.0, 240.0),
    ("S2", 24, 195.0, 420.0),
    ("S3", 16, 120.0, 260.0),
    ("S4", 48, 370.0, 890.0),
)
E15_OK = tuple(ref for ref, ports, budget, _p in E15_CATALOGUE if ports >= E15_PORTS and poe_verdict(E15_CLASSES, budget) == POE_OK)
E15_CHOICE = min((p, ref) for ref, ports, budget, p in E15_CATALOGUE if ref in E15_OK)[1]

E16_ITEMS: tuple[RackItem, ...] = (
    RackItem("Panneau de brassage 24 ports", 1),
    RackItem("Panneau de brassage 24 ports", 1),
    RackItem("Passe-câbles", 1),
    RackItem("Passe-câbles", 1),
    RackItem("Switch 48 ports", 1),
    RackItem("Étagère pour la box", 2),
    RackItem("Onduleur", 2),
    RackItem("Bandeau de prises électriques", 1),
)
E16_USED = rack_units(E16_ITEMS)
E16_RACK = choose_rack(E16_USED)

E17_RUNS: tuple[tuple[str, float], ...] = (
    ("Atelier, poste 1", 42.0),
    ("Atelier, poste 2", 61.0),
    ("Magasin, caisse", 78.0),
    ("Quai de chargement, scanner", 87.5),
    ("Bureau du chef d'atelier", 33.0),
    ("Vestiaire, badgeuse", 55.0),
)
E17_LENGTHS = tuple(run_length_m(h) for _t, h in E17_RUNS)
E17_TOO_LONG = tuple(t for (t, _h), length in zip(E17_RUNS, E17_LENGTHS, strict=True) if length > PERMANENT_LINK_MAX_M)
E17_TOTAL = sum(E17_LENGTHS)
E17_BOXES = boxes_needed(E17_LENGTHS)

E18_CLASS, E18_DISTANCE = "b", 50
E18_MIN = min_separation_mm(E18_CLASS)
E18_UNKNOWN = min_separation_mm(None)

# --- Mini-examen -------------------------------------------------------------------------------

X01_CANDIDATES: tuple[tuple[str, float], ...] = (("Emplacement A, réserve au bout du couloir", 88.0),
                                                  ("Emplacement B, local au centre du bâtiment", 46.0))
X01_LENGTHS = tuple(run_length_m(h) for _t, h in X01_CANDIDATES)

X03_POSTES = 6
X03_LINKS = X03_POSTES * 2 + 2  # 2 prises par poste + imprimante + point d'accès
X03_PORTS = switch_ports_needed(X03_LINKS)
X03_SWITCH = choose_switch(X03_LINKS)

X04_LINES: tuple[QuoteLine, ...] = (
    QuoteLine("C6", "Câble Cat6 U/UTP, boîte de 305 m", 1, 159.00),
    QuoteLine("KS", "Keystone Cat6", 16, 5.40),
    QuoteLine("PP", "Panneau de brassage 24 ports", 1, 35.00),
    QuoteLine("CO", "Cordon Cat6, 2 m", 16, 3.75),
    QuoteLine("SW", "Switch 16 ports", 1, 129.00),
)
X04_HT, X04_VAT, X04_TTC = quote_totals(X04_LINES)

X05_CLASSES = (4, 4, 3, 3, 3, 3)
X05_BUDGET = 120.0
X05_TOTAL = poe_budget_w(X05_CLASSES)

X06_TESTS: tuple[LinkTest, ...] = (
    LinkTest("B1-P1-04", False, 31, "FAIL"),
    LinkTest("B1-P1-11", True, 94, "FAIL"),
    LinkTest("B1-P1-15", True, 48, "FAIL"),
)
X06_VERDICTS = tuple(link_verdict(t) for t in X06_TESTS)

X08_CLASS, X08_DISTANCE = "c", 30
X08_MIN = min_separation_mm(X08_CLASS)

X10_ITEMS = ("Bandeau de prises électriques (1 U)", "Switch 24 ports (1 U)", "Étagère pour la box (2 U)",
             "Panneau de brassage 24 ports (1 U)", "Passe-câbles (1 U)")

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'installation d'un mini-réseau",
        question_type="ordering",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_ORDER,
        context=(
            "Une agence immobilière emménage dans de nouveaux bureaux et te confie son réseau : six "
            "postes, une imprimante, un point d'accès Wi-Fi et la box de l'opérateur. Ton responsable "
            "a recopié la fiche « installation d'un mini-réseau » de l'entreprise, mais ses huit "
            "étapes sont dans le désordre."
        ),
        instructions=("Remets les huit étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Analyser le besoin → concevoir → chiffrer → poser → raccorder → tester → configurer et valider → documenter et réceptionner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On analyse le besoin (postes, imprimantes, Wi-Fi, PoE, plan des locaux, évolution). 2. On conçoit : étoile, place de la baie, prises, supports, longueurs. 3. On chiffre (nomenclature, devis) et on obtient l'accord du client avant de commander.",
            "4. On pose les chemins et les câbles, repérés aux deux bouts. 5. On raccorde keystones et panneau, on équipe la baie. 6. On teste chaque lien et on corrige. 7. On configure et on valide le réseau (lien, adresse, passerelle, autre poste, Internet, partage). 8. On documente et on fait réceptionner par le client.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 6, 0, 5, 1, 7, 2, 4)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la validation du réseau",
        question_type="ordering",
        requirement_ids=("AP-38",),
        kind=KIND_ORDER,
        context=(
            "Le câblage d'un cabinet de kinésithérapie est terminé et testé. Avant de faire signer le "
            "client, tu dois valider le réseau depuis le poste de l'accueil. La fiche de validation "
            "de l'atelier, en sept contrôles, a été mélangée par un stagiaire."
        ),
        instructions=("Remets les sept contrôles dans l'ordre, du plus simple au plus large.",),
        criteria=(
            _c("Ordre", 3.5, "Lien → adresse → passerelle → autre poste → Internet → partage → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. Lien : voyants de la carte et du port du switch. 2. Adresse : ipconfig montre une adresse du réseau de la box, le masque, la passerelle et le DNS. 3. Passerelle : ping de la box. 4. Autre poste : ping d'un poste du réseau.",
            "5. Internet : un site s'ouvre par son nom. 6. Partage : le dossier partagé s'ouvre. 7. On consigne les résultats dans le dossier de recette. Chaque contrôle suppose que les précédents réussissent : le premier qui échoue désigne la piste.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 6, 0, 3, 5, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le test et la certification du câblage",
        question_type="ordering",
        requirement_ids=("AP-36",),
        kind=KIND_ORDER,
        context=(
            "Un installateur vient de poser 24 liens Cat6A dans une école. Tu dois tester chaque "
            "lien avec le certificateur loué pour la journée. Le mode opératoire en six étapes a été "
            "imprimé dans le désordre."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Préparer → brancher → lire le câblage → lire la longueur → certifier → corriger et consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On prépare le plan de brassage, la liste des repères et le testeur (chargé, référencé). 2. On branche l'unité principale au panneau et l'unité distante à la prise de même repère. 3. On lit le câblage : continuité des 8 fils, paires, inversions, coupures.",
            f"4. On lit la longueur : lien permanent ≤ {PERMANENT_LINK_MAX_M} m. 5. On certifie : mesures de la catégorie visée, résultat PASS ou FAIL, rapport enregistré. 6. On corrige le raccordement fautif, on reteste et on archive le rapport.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 5, 0, 4, 1, 3)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Où installer chaque élément du réseau ?",
        question_type="classification",
        requirement_ids=("AP-36",),
        kind=KIND_PLAN,
        context=(
            "Un bureau d'architectes de huit personnes t'a envoyé ses notes d'implantation, prises "
            "pendant la visite des locaux. Pour chacune, tu dois indiquer de quel élément du réseau "
            "elle parle : baie, box, point d'accès Wi-Fi, prises murales ou chemins de câbles."
        ),
        instructions=("Range chaque note selon l'élément du réseau qu'elle concerne.",),
        criteria=(
            _c("Classement", 4, "Point central et local fermé → baie ; arrivée de la ligne → box ; plafond au centre et alimenté par le câble → point d'accès ; à côté des bureaux → prises ; faux plafond et goulotte qui croise l'électricité à angle droit → chemins de câbles (0,5 pt par élément)."),
        ),
        correction=(
            f"La baie est le centre de l'étoile : tous les câbles des prises y arrivent ; on la place dans un local fermé à clé, ventilé, assez central pour que chaque lien reste sous {PERMANENT_LINK_MAX_M} m. La box se place à l'arrivée de la ligne de l'opérateur, de préférence dans la baie.",
            "Le point d'accès se met en hauteur, au centre de la zone à couvrir, loin des masses métalliques, alimenté par son câble (PoE). Les prises se posent près des postes (deux par poste). Les chemins de câbles passent par le faux plafond ou des goulottes, à distance des câbles électriques, qu'ils croisent à angle droit.",
        ),
        classification=Classification(categories=PLACE_NAMES, elements=tuple(t for t, _p in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Cuivre, fibre ou coaxial pour chaque liaison ?",
        question_type="classification",
        requirement_ids=("AP-36",),
        kind=KIND_PLAN,
        context=(
            "Pour le réseau d'une PME de mécanique (bureaux, atelier, bâtiment voisin), tu dois choisir "
            "le support de huit liaisons. Règle du cours (PR13) : au-delà de 100 m ou entre deux "
            "bâtiments, fibre ; perturbations faibles, U/UTP ; moyennes avec terre assurée, F/UTP ; "
            "fortes sans terre, fibre ; vidéo analogique et télévision, coaxial 75 Ω."
        ),
        instructions=("Range chaque liaison selon le support à poser.",),
        criteria=(
            _c("Classement", 4, "Bureau calme, point d'accès, néons sans terre possible → U/UTP ; atelier avec terre → F/UTP ; bâtiment voisin à 140 m, presse sans terre → fibre ; caméra analogique, antenne TV → coaxial 75 Ω (0,5 pt par élément)."),
        ),
        correction=(
            "On regarde d'abord le service : la caméra analogique et l'antenne de télévision restent en coaxial 75 Ω (BNC ou fiches F). Pour Ethernet, la longueur : 140 m vers un autre bâtiment dépassent les 100 m du canal et relieraient électriquement deux bâtiments → fibre.",
            "Puis les perturbations : faibles (bureaux, faux plafond) → U/UTP ; moyennes avec un système blindé relié à la terre → F/UTP ; moyennes sans terre possible → U/UTP avec une séparation renforcée (un écran non relié à la terre ne sert à rien) ; fortes sans terre → fibre, insensible aux parasites.",
        ),
        classification=Classification(categories=E05_CATEGORIES, elements=tuple(t for t, _n in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Lire un rapport de recette du câblage",
        question_type="classification",
        requirement_ids=("AP-36",),
        kind=KIND_TEST,
        context=(
            "Le certificateur a testé huit liens d'un cabinet d'avocats en Cat6A. Pour chacun, tu as "
            "relevé le câblage (continuité et paires), la longueur et le résultat PASS/FAIL. On lit "
            f"toujours dans l'ordre : câblage, puis longueur (lien permanent ≤ {PERMANENT_LINK_MAX_M} m), "
            "puis performances."
        ),
        instructions=("Range chaque lien selon le défaut principal à corriger, ou « Conforme ».",),
        criteria=(
            _c("Classement", 4, "01 et 06 → conformes ; 02 (paire inversée) et 05 (fil coupé) → défaut de câblage ; 03 (94 m) et 07 (92 m) → trop long ; 04 et 08 (câblage correct, longueur correcte, FAIL) → performances insuffisantes (0,5 pt par élément)."),
        ),
        correction=(
            "Un défaut de câblage (fil coupé, paire inversée) fait échouer toutes les mesures : on le corrige d'abord, en refaisant le raccordement (keystone ou panneau) puis on reteste. Si le câblage est bon mais que le lien dépasse 90 m, il est trop long : on ne peut que changer le parcours, déplacer la baie ou ajouter un switch.",
            "Câblage et longueur corrects mais FAIL : performances insuffisantes (paradiaphonie, perte d'insertion) : détorsadage trop long au raccordement, câble écrasé ou plié, composant d'une catégorie inférieure. Les liens 01 et 06 sont conformes : rapport archivé.",
        ),
        classification=Classification(categories=TEST_VERDICTS, elements=tuple(t.label for t in E06_TESTS), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Validation : quel est le premier contrôle en échec ?",
        question_type="classification",
        requirement_ids=("AP-38",),
        kind=KIND_TEST,
        context=(
            "Pendant la mise en service du réseau d'une agence de voyages (box 192.168.1.1, partage "
            "sur SERVEUR), tes collègues t'envoient sept constats. Ordre de validation : lien, "
            "adresse, passerelle, autre poste, Internet, partage ; le premier contrôle qui échoue "
            "désigne la piste."
        ),
        instructions=("Range chaque constat selon la piste à suivre.",),
        criteria=(
            _c("Classement", 3.5, "Voyant éteint (deux constats) → lien physique ; 169.254 → adressage ; box injoignable → passerelle ; poste éteint → poste distant ; aucun site → accès Internet ; « Accès refusé » → partage (0,5 pt par élément)."),
        ),
        correction=(
            "Voyant éteint : rien ne passe au niveau physique (cordon, prise, brassage, port) ; une prise brassée sur aucun port donne le même symptôme. Une adresse 169.254.x.x signifie que le poste n'a reçu aucune adresse du serveur DHCP (la box) : adressage. Si l'adresse est bonne mais que la box ne répond pas, alors que d'autres postes ne la joignent pas non plus, c'est la passerelle (box ou son raccordement).",
            "Box joignable mais un poste ne répond pas : ce poste est éteint, son pare-feu bloque le ping ou il est sur un autre réseau. Réseau local correct mais aucun site, même par adresse : accès Internet (opérateur, box). Tout répond sauf le dossier : partage (chemin, droits, compte).",
        ),
        classification=Classification(categories=DIAGNOSES, elements=tuple(t for t, _k in E07_CASES), correct=E07_CORRECT),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : implanter le réseau sur le plan",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_SCHEMA,
        context=(
            "Le cabinet d'expertise comptable du document 1 (24 m × 14 m) s'équipe : cinq postes à deux "
            "prises, une imprimante, un écran de réunion, un point d'accès Wi-Fi et la box de "
            "l'opérateur, dont la ligne arrive dans le local technique. Le plan porte cinq "
            "emplacements numérotés à compléter."
        ),
        documents=(_schema("pr18-plan-a-completer", "Document 1 — Plan des locaux à compléter (schéma fictif)"),),
        instructions=(
            "Indique l'équipement à installer à chacun des emplacements ① à ⑤.",
            "Justifie l'emplacement ① par la longueur des liens.",
        ),
        criteria=(
            _c("Emplacements", 2.5, " ; ".join(f"{n} {a}" for n, _x, _y, a in PLAN_BLANKS) + " (0,5 pt chacun)."),
            _c("Justification", 1, f"Baie au centre : le lien le plus long reste court ({PLAN_MAX_RUN} m, bien sous les {PERMANENT_LINK_MAX_M} m) ; local fermé, ventilé, proche de l'arrivée de l'opérateur."),
        ),
        correction=(
            "① Baie (panneau de brassage et switch) dans le local technique, au centre de l'étoile. ② Box de l'opérateur, là où arrive la ligne, reliée au switch par un cordon. ③ Point d'accès Wi-Fi au plafond, au centre du plateau, alimenté par son câble en PoE. ④ Deux prises RJ45 pour le poste de l'accueil. ⑤ Prise RJ45 de l'imprimante.",
            f"Placée au centre, la baie garde tous les liens courts : le plus éloigné (Bureau 2) demande {PLAN_MAX_RUN} m de câble, largement sous les {PERMANENT_LINK_MAX_M} m du lien permanent. Le local technique est fermé à clé, ventilé, et reçoit déjà la ligne de l'opérateur.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : équiper une baie",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_SCHEMA,
        context=(
            f"Dans une maison médicale, la baie de {RACK_BLANK_TOTAL_U} U du document 1 est en partie équipée. "
            "Il te reste à placer quatre éléments : un panneau de brassage 24 ports, un switch 24 ports "
            "PoE, un passe-câbles et un bandeau de prises électriques (1 U chacun). Règle de "
            "l'atelier : chaque switch entre deux panneaux, avec un passe-câbles entre chaque "
            "panneau et le switch ; l'alimentation en bas."
        ),
        documents=(_schema("pr18-baie-a-completer", "Document 1 — Baie à compléter (schéma fictif)"),),
        instructions=(
            "Indique l'élément à placer en ①, ②, ③ et ④.",
            "Explique l'intérêt de cette disposition.",
        ),
        criteria=(
            _c("Emplacements", 2, "① panneau de brassage ; ② switch 24 ports PoE ; ③ passe-câbles ; ④ bandeau de prises électriques (0,5 pt chacun)."),
            _c("Justification", 1, "Cordons de brassage courts et rangés entre panneau et switch ; électricité en bas, loin des cordons ; place libre pour l'évolution."),
        ),
        correction=(
            "① Panneau de brassage 24 ports (le passe-câbles en dessous le sépare du switch). ② Switch 24 ports PoE, entre les deux passe-câbles. ③ Passe-câbles, qui sépare le switch du second panneau. ④ Bandeau de prises électriques, en bas de la baie.",
            "Chaque port du switch est juste à côté du port de panneau qu'il dessert : les cordons de brassage sont courts (0,5 à 1 m) et rangés dans les passe-câbles, on suit un lien d'un coup d'œil. L'alimentation électrique en bas reste à l'écart des cordons de données ; les 4 U libres permettent d'ajouter un panneau ou un onduleur.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : la chaîne d'un lien",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_SCHEMA,
        context=(
            "Pour le dossier technique d'un cabinet comptable, tu dois expliquer au client comment "
            "le PC de la comptable est relié au switch. Le schéma du document 1 montre la chaîne "
            "complète, du switch au PC ; quatre éléments et la partie fixe du câblage sont à nommer."
        ),
        documents=(_schema("pr18-lien-a-completer", "Document 1 — Chaîne d'un lien à compléter (schéma fictif)"),),
        instructions=(
            "Nomme les éléments ① à ④ et la partie ⑤ avec sa longueur maximale.",
            "Vérifie les longueurs de cette installation.",
        ),
        criteria=(
            _c("Éléments", 2, "① cordon de brassage ; ② panneau de brassage (port B1-P1-07) ; ③ prise murale (keystone) B1-P1-07 ; ④ cordon de poste (0,5 pt chacun)."),
            _c("Lien permanent", 0.5, f"⑤ lien permanent, du panneau à la prise : {PERMANENT_LINK_MAX_M} m au plus."),
            _c("Vérification", 1, f"Lien permanent {CHAIN_PERMANENT_M} m ≤ {PERMANENT_LINK_MAX_M} m ; cordons 2 + 5 = {CHAIN_CORDS_M} m ≤ 10 m ; canal {CHAIN_PERMANENT_M + CHAIN_CORDS_M} m ≤ 100 m : conforme."),
        ),
        correction=(
            "① Cordon de brassage (souple, multibrin) entre le port 7 du switch et le panneau. ② Panneau de brassage, port B1-P1-07. ③ Prise murale avec son keystone, portant le même repère B1-P1-07. ④ Cordon de poste entre la prise et le PC. ⑤ Lien permanent : le câble monobrin fixe, poinçonné du panneau à la prise, 90 m au plus.",
            f"Ici : lien permanent {CHAIN_PERMANENT_M} m ≤ 90 m ; cordons {CHAIN_CORDS_M} m ≤ 10 m ; canal complet {CHAIN_PERMANENT_M + CHAIN_CORDS_M} m ≤ 100 m. L'installation est conforme ({'aucune erreur' if not E10_ERRORS else ', '.join(E10_ERRORS)}).",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : la topologie en étoile",
        question_type="document_analysis",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_SCHEMA,
        context=(
            "Le gérant d'une imprimerie veut comprendre le réseau proposé : bureaux, atelier et un "
            "entrepôt dans un second bâtiment à 140 m. Le schéma logique du document 1 a été "
            "préparé pour lui, mais trois équipements et le support de la liaison vers l'entrepôt "
            "sont à compléter."
        ),
        documents=(_schema("pr18-etoile-a-completer", "Document 1 — Topologie à compléter (schéma fictif)"),),
        instructions=(
            "Nomme les équipements ①, ② et ③ et choisis le support de la liaison ④.",
            "Explique au gérant un avantage de la topologie en étoile.",
        ),
        criteria=(
            _c("Équipements", 1.5, "① box ou routeur de l'opérateur ; ② switch, centre de l'étoile ; ③ point d'accès Wi-Fi alimenté en PoE (0,5 pt chacun)."),
            _c("Liaison", 1, "④ fibre optique entre les deux switchs : 140 m > 100 m, et pas de liaison électrique entre deux bâtiments."),
            _c("Avantage", 0.5, "Un câble par appareil : un câble coupé n'arrête qu'un poste ; on ajoute ou isole un poste sans toucher aux autres."),
        ),
        correction=(
            "① Box (ou routeur) de l'opérateur : seul passage vers Internet. ② Switch, centre de l'étoile : chaque prise y revient par son propre câble. ③ Point d'accès Wi-Fi, au plafond, alimenté par son câble (PoE). ④ Fibre optique entre le switch principal et celui de l'entrepôt : 140 m dépassent les 100 m de la paire torsadée et la fibre isole électriquement les deux bâtiments.",
            "Avantage de l'étoile : un câble coupé ou un poste en panne n'arrête que ce poste ; on repère et on teste chaque lien séparément ; on ajoute un poste en brassant un port de plus. Le point faible est le switch central : on le protège (baie, onduleur).",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : le plan de brassage",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_SCHEMA,
        context=(
            "Tu termines le dossier du cabinet comptable. Le plan de brassage du document 1 (baie 1, "
            "panneau 1) a des cases vides. Convention de l'entreprise : repère « B<baie>-P<panneau>-<port "
            "sur deux chiffres> », identique à la prise et au panneau ; le port n du panneau est "
            "brassé sur le port n du switch."
        ),
        documents=(_schema("pr18-brassage-a-completer", "Document 1 — Plan de brassage à compléter (schéma fictif)"),),
        instructions=(
            "Complète les repères et les ports du switch ①, ② et ③.",
            "Explique à quoi sert ce repérage pour un dépannage.",
        ),
        criteria=(
            _c("Repères et ports", 1.5, " ; ".join(f"{PATCH_BLANKS[i]} {PATCH_ROWS[i][0]}, port {PATCH_ROWS[i][2]}" for i in sorted(PATCH_BLANKS)) + " (0,5 pt chacun)."),
            _c("Utilité", 1.5, "Le même repère à la prise et au panneau : on retrouve le port du panneau puis du switch sans ouvrir les goulottes ; on teste et on isole le bon lien ; le plan est remis au client et tenu à jour."),
        ),
        correction=(
            " ; ".join(f"{PATCH_BLANKS[i]} port {i + 1:02d} du panneau : repère {PATCH_ROWS[i][0]}, brassé sur le port {PATCH_ROWS[i][2]} du switch" for i in sorted(PATCH_BLANKS)) + ".",
            "Un utilisateur signale « ma prise ne marche plus » : on lit le repère sur la prise (par exemple B1-P1-06), on trouve le port 06 du panneau 1 de la baie 1, puis le port 6 du switch ; on teste ce lien, on change le cordon ou le port, sans tirer sur les autres câbles. Le plan est remis au client et mis à jour à chaque changement.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Nomenclature : du plan à la liste du matériel",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            "Une petite agence d'assurances (accueil, un bureau, une salle de pause) veut son réseau. "
            "Le document 1 donne, pour chaque emplacement, le nombre de prises et le parcours "
            "horizontal depuis la baie. Convention du cours : longueur = parcours + 3 m (montée et "
            "descente) + 2 m de réserve, arrondie au mètre supérieur ; câble en boîtes de 305 m ; "
            "switch avec 20 % de réserve et un port pour la box."
        ),
        documents=(
            _table(
                "Document 1 — Relevé du plan",
                ("Emplacement", "Prises", "Parcours horizontal depuis la baie"),
                *((t, str(n), f"{fr(h)} m") for (t, h), n in zip(E13_RUNS, E13_PRISES, strict=True)),
            ),
        ),
        instructions=(
            "Calcule la longueur de chaque lien et le métrage total, puis le nombre de boîtes de câble.",
            "Établis la nomenclature : keystones, panneau, cordons, taille du switch.",
        ),
        criteria=(
            _c("Longueurs", 1.5, "Liens de " + ", ".join(f"{length} m" for length in E13_LENGTHS) + f" ; total {E13_TOTAL_M} m (2 liens pour les postes) ; {E13_BOXES} boîte de 305 m."),
            _c("Nomenclature", 2, f"{E13_LINKS} liens → {2 * E13_LINKS} keystones (prise + panneau), 1 panneau 24 ports, {E13_LINKS} cordons de brassage et {E13_LINKS} cordons de poste ; switch : {E13_LINKS} × 1,2 → {E13_PORTS - 1} + 1 = {E13_PORTS} ports → {E13_SWITCH} ports."),
        ),
        correction=(
            "Longueurs : " + " ; ".join(f"{t.split(',')[0]} {fr(h)} + 5 = {fr(h + 5)} → {length} m" for (t, h), length in zip(E13_RUNS, E13_LENGTHS, strict=True))
            + f". Les postes ont deux prises, donc deux câbles : total {E13_TOTAL_M} m, qui tient dans {E13_BOXES} boîte de 305 m (aucun lien ne se raboute).",
            f"Nomenclature : {E13_LINKS} liens, donc {2 * E13_LINKS} keystones (un à la prise, un au panneau), 1 panneau de brassage 24 ports, {E13_LINKS} boîtiers muraux, {E13_LINKS} cordons de brassage et {E13_LINKS} cordons de poste. Switch : {E13_LINKS} liens + 20 % = {E13_PORTS - 1} ports, plus 1 pour la box = {E13_PORTS} → switch de {E13_SWITCH} ports (PoE pour le point d'accès).",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Devis : trouver et corriger les erreurs",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            f"Pour le cabinet comptable du cours ({len(PATCH_ROWS)} liens, panneau 24 ports vide à équiper de "
            "keystones), un collègue a préparé le devis du document 1. Avant de l'envoyer, ton "
            "responsable te demande de le vérifier ligne par ligne. En Belgique, le taux normal de "
            f"TVA est de {fr(VAT_RATE * 100, 0)} %."
        ),
        documents=(
            _table(
                "Document 1 — Devis (prix fictifs, € HT)",
                ("Réf.", "Désignation", "Qté", "PU HT", "Total HT"),
                *((line.ref, line.label, str(E14_WRONG_KS_QTY if line.ref == "KS" else line.quantity), euro(line.unit_price),
                   euro(_e14_written_total(line))) for line in PLAN_QUOTE),
                ("", "Total HT", "", "", euro(E14_WRITTEN_HT)),
                ("", "TVA 6 %", "", "", euro(E14_WRITTEN_VAT)),
                ("", "Total TTC", "", "", euro(E14_WRITTEN_TTC)),
            ),
        ),
        instructions=(
            "Relève les trois erreurs du devis en justifiant.",
            "Calcule le total HT, la TVA et le total TTC corrects.",
        ),
        criteria=(
            _c("Erreurs", 2, f"KS : {E14_WRONG_KS_QTY} au lieu de {E14_KS.quantity} (deux keystones par lien : prise + panneau) ; CP3 : {E14_CP.quantity} × {euro(E14_CP.unit_price)} = {euro(E14_CP.total)}, pas {euro(E14_WRONG_CP_TOTAL)} ; TVA à 21 %, pas 6 %."),
            _c("Totaux", 1.5, f"HT {euro(E14_HT)} ; TVA 21 % {euro(E14_VAT)} ; TTC {euro(E14_TTC)}."),
        ),
        correction=(
            f"1. Keystones : un lien a un keystone à la prise et un au panneau (vide) : {len(PATCH_ROWS)} liens × 2 = {E14_KS.quantity}, pas {E14_WRONG_KS_QTY} ; ligne {E14_KS.quantity} × {euro(E14_KS.unit_price)} = {euro(E14_KS.total)}. 2. Cordons de poste : {E14_CP.quantity} × {euro(E14_CP.unit_price)} = {euro(E14_CP.total)}, pas {euro(E14_WRONG_CP_TOTAL)}. 3. La TVA d'une installation pour une entreprise est au taux normal de 21 %, pas 6 %.",
            f"Total HT corrigé : {euro(E14_HT)} ; TVA 21 % : {euro(E14_VAT)} ; total TTC : {euro(E14_TTC)}. On renvoie le devis corrigé et on garde la nomenclature avec le dossier.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Choisir le switch : ports et budget PoE",
        question_type="document_analysis",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_QUOTE,
        context=(
            "Une agence bancaire installe son réseau : chaque appareil du document 1 a sa propre "
            "prise. Le fournisseur propose les switchs du document 2. Convention du cours : 20 % de "
            "ports de réserve et un port pour la box ; puissance PoE réservée selon la classe : "
            + ", ".join(f"classe {c} {fr(POE_CLASS_W[c])} W" for c in (2, 3, 4)) + "."
        ),
        documents=(
            _table("Document 1 — Appareils à raccorder", ("Appareil", "Quantité", "PoE"),
                   *((n, str(q), "non" if c is None else f"classe {c}") for n, q, c in E15_DEVICES)),
            _table("Document 2 — Switchs proposés (fiches fictives)", ("Réf.", "Ports", "Budget PoE total", "Prix HT"),
                   *((ref, str(p), f"{fr(b, 0)} W", euro(price)) for ref, p, b, price in E15_CATALOGUE)),
        ),
        instructions=(
            "Calcule le nombre de ports et la puissance PoE nécessaires.",
            "Choisis le switch en justifiant le rejet des trois autres.",
        ),
        criteria=(
            _c("Calculs", 1.5, f"{E15_LINKS} liens → {E15_LINKS} × 1,2 = {E15_PORTS - 1} + 1 = {E15_PORTS} ports ; PoE : 30 + 2 × 15,4 + 4 × 7 = {fr(E15_POE)} W."),
            _c("Choix justifié", 2, f"{E15_CHOICE} : 24 ports ≥ {E15_PORTS}, 195 W ≥ {fr(E15_POE)} W ; S1 rejeté (65 W < {fr(E15_POE)} W) ; S3 rejeté (16 ports < {E15_PORTS}) ; S4 convient mais surdimensionné et plus cher."),
        ),
        correction=(
            f"Ports : {E15_LINKS} appareils = {E15_LINKS} liens ; avec 20 % de réserve, {E15_PORTS - 1} ports, plus 1 pour la box : {E15_PORTS} ports. PoE : point d'accès 30 W + 2 caméras × 15,4 W + 4 téléphones × 7 W = {fr(E15_POE)} W réservés.",
            f"S1 a assez de ports mais seulement 65 W de PoE : budget dépassé. S3 a 120 W mais 16 ports seulement. S2 (24 ports, 195 W) et S4 (48 ports, 370 W) conviennent ; on retient {E15_CHOICE}, suffisant et moins cher ; S4 serait surdimensionné.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Nomenclature de la baie : choisir sa hauteur",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            "Une école primaire prévoit 40 prises et un onduleur pour son local informatique. Le "
            "document 1 liste les équipements à monter dans la baie. Les baies existent en 6, 9, 12, "
            "15, 18, 22, 27 et 42 U ; convention du cours : garder au moins 25 % d'unités libres."
        ),
        documents=(
            _table("Document 1 — Équipements de la baie", ("Équipement", "Hauteur"),
                   *((i.name, f"{i.units} U") for i in E16_ITEMS)),
        ),
        instructions=(
            "Calcule la hauteur occupée et choisis la baie.",
            "Justifie le nombre de panneaux et l'intérêt de la réserve.",
        ),
        criteria=(
            _c("Calcul et choix", 2, f"{E16_USED} U occupées ; × 1,25 = {fr(E16_USED * 1.25, 2)} → baie de {E16_RACK} U."),
            _c("Justification", 1, f"40 prises → {panels_needed(40)} panneaux de 24 ports ; la réserve accueille un panneau, un switch ou un équipement ajouté plus tard et laisse l'air circuler."),
        ),
        correction=(
            f"Hauteur occupée : 1 + 1 + 1 + 1 + 1 + 2 + 2 + 1 = {E16_USED} U. Avec 25 % de réserve : {E16_USED} × 1,25 = {fr(E16_USED * 1.25, 2)} U, arrondi à {int(E16_USED * 1.25) + 1} ; la plus petite baie standard qui convient fait {E16_RACK} U.",
            f"40 prises demandent {panels_needed(40)} panneaux de 24 ports (48 ports, 8 libres). La réserve d'unités permet d'ajouter un panneau ou un switch sans changer de baie, et laisse de l'espace pour la ventilation de l'onduleur et du switch.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Longueurs des liens et commande de câble",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            "Une entreprise de logistique fait câbler son atelier et son magasin depuis une baie "
            "placée dans les bureaux, à une extrémité du bâtiment. Le document 1 donne le parcours "
            "horizontal de six liens. Convention : longueur = parcours + 5 m, arrondie au mètre "
            f"supérieur ; lien permanent ≤ {PERMANENT_LINK_MAX_M} m ; câble en boîtes de 305 m, un lien ne se "
            "raboute jamais."
        ),
        documents=(
            _table("Document 1 — Parcours depuis la baie", ("Lien", "Parcours horizontal"),
                   *((t, f"{fr(h)} m") for t, h in E17_RUNS)),
        ),
        instructions=(
            "Calcule chaque longueur et repère le lien non conforme ; propose deux solutions.",
            "Calcule le métrage total et le nombre de boîtes en tenant compte des chutes.",
        ),
        criteria=(
            _c("Longueurs et conformité", 1.5, "Longueurs " + ", ".join(f"{length} m" for length in E17_LENGTHS) + f" ; {E17_TOO_LONG[0].split(',')[0].lower()} à {max(E17_LENGTHS)} m > {PERMANENT_LINK_MAX_M} m : non conforme."),
            _c("Solutions", 1, "Déplacer la baie vers le centre du bâtiment, ou ajouter un switch près du quai relié à la baie (cuivre ≤ 90 m ou fibre)."),
            _c("Câble", 1, f"Total {E17_TOTAL} m ; en rangeant les plus longs d'abord, il faut {E17_BOXES} boîtes de 305 m (pas 305 × 2 par hasard : on vérifie que chaque lien tient dans une boîte)."),
        ),
        correction=(
            "Longueurs : " + " ; ".join(f"{t.split(',')[0]} {fr(h)} + 5 → {length} m" for (t, h), length in zip(E17_RUNS, E17_LENGTHS, strict=True))
            + f". Le lien du quai fait {max(E17_LENGTHS)} m : au-delà des {PERMANENT_LINK_MAX_M} m du lien permanent, il n'est pas conforme (pertes, erreurs, certification impossible).",
            f"Solutions : rapprocher la baie du centre du bâtiment, ou poser un petit switch dans le magasin, relié à la baie par un câble ≤ {PERMANENT_LINK_MAX_M} m (ou une fibre), qui dessert le quai. Câble : {E17_TOTAL} m au total ; une boîte de 305 m contient 93 + 83 + 66 + 60 = 302 m, les deux derniers liens (47 et 38 m) demandent une seconde boîte : {E17_BOXES} boîtes.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Sécurité : câbles réseau et courant fort",
        question_type="short_answer",
        requirement_ids=("AP-36",),
        kind=KIND_SAFETY,
        context=(
            "Dans un garage automobile, l'électricien a posé un chemin de câbles d'énergie (trois "
            f"circuits) dans le faux plafond. Ton collègue veut y coucher les câbles réseau à {E18_DISTANCE} mm, "
            f"sans cloison ; la fiche du câble indique une classe de séparation « {E18_CLASS} ». Il veut aussi "
            "percer le mur du local technique sans vérifier ce qu'il y a derrière."
        ),
        instructions=("Dis si la pose est conforme, ce qu'il faut faire, et les précautions de sécurité du chantier.",),
        criteria=(
            _c("Séparation", 1.5, f"Classe {E18_CLASS} sans cloison : {E18_MIN} mm minimum (EN 50174-2) ; {E18_DISTANCE} mm : non conforme → chemin séparé à ≥ {E18_MIN} mm ou cloison métallique ; croiser à angle droit ; classe inconnue : {E18_UNKNOWN} mm."),
            _c("Sécurité du chantier", 1.5, "Détecteur de câbles et plans avant de percer ; couper le circuit concerné si on travaille près d'une ligne ; escabeau stable, lunettes ; ne pas fixer les câbles réseau sur les câbles électriques ; respecter les coupe-feu."),
        ),
        correction=(
            f"La norme EN 50174-2 demande, pour un câble de classe {E18_CLASS} sans cloison et jusqu'à trois circuits d'énergie, au moins {E18_MIN} mm ; {E18_DISTANCE} mm ne suffisent pas. On pose un chemin séparé à {E18_MIN} mm au moins, ou on sépare par une cloison métallique ; on croise le courant fort à angle droit. Sans classe connue, on applique {E18_UNKNOWN} mm.",
            "Avant de percer : plans du bâtiment et détecteur de câbles et de canalisations ; travailler loin des conducteurs sous tension ou faire couper le circuit ; escabeau stable, lunettes ; ne jamais attacher les câbles réseau aux câbles électriques ; refermer les traversées coupe-feu.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Analyser le besoin avant de dessiner le réseau",
        question_type="long_answer",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_PLAN,
        context=(
            "La gérante d'une librairie-café t'appelle : « Je voudrais un réseau dans ma nouvelle "
            "boutique, il me faut quoi ? » Elle a un étage de 180 m², une caisse, deux postes, une "
            "imprimante, et pense à du Wi-Fi pour les clients. Tu dois préparer la visite des lieux."
        ),
        instructions=("Rédige les informations à recueillir et à relever avant de concevoir le réseau, en expliquant à quoi chacune sert.",),
        criteria=(
            _c("Besoins", 1.5, "Nombre et place des postes, caisse, imprimantes, téléphones, caméras ; Wi-Fi (personnel et clients séparés) ; débit, partage de fichiers, évolution prévue."),
            _c("Locaux", 1.5, "Plan avec cotes ; arrivée de la ligne de l'opérateur ; local possible pour la baie (fermé, ventilé, prise électrique) ; chemins (faux plafond, goulottes) ; câbles électriques ; perturbations."),
            _c("Contraintes", 1, "Budget, délais, horaires de travaux, accord du propriétaire pour percer ; documents à fournir (plan, devis)."),
        ),
        correction=(
            "Besoins : combien d'appareils et où (caisse, deux postes, imprimante, éventuels téléphones ou caméras) ; Wi-Fi pour le personnel et pour les clients, à séparer ; usages (caisse, partage, Internet) et évolution (deux prises par poste, ports en réserve). Ces réponses fixent le nombre de prises, la taille du switch et le besoin en PoE.",
            "Locaux : plan coté, arrivée de la ligne de l'opérateur, un local fermé et ventilé pour la baie, chemins possibles et câbles électriques existants : on en déduit l'emplacement de la baie, les longueurs (≤ 90 m) et la séparation du courant fort. Contraintes : budget, délais, horaires des travaux, accord du propriétaire pour percer. On repart avec un relevé qui permet de dessiner le plan et de chiffrer le devis.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Préparer le dossier de recette",
        question_type="short_answer",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_TEST,
        context=(
            "Le réseau d'une étude de notaire est installé, testé et configuré. Le notaire doit "
            "signer la réception demain et demande « ce qu'il recevra comme papiers ». Ton "
            "responsable te charge de préparer le dossier de recette."
        ),
        instructions=("Liste le contenu du dossier de recette et explique à quoi il sert.",),
        criteria=(
            _c("Contenu", 2, "Plan des locaux avec prises et baie ; plan de brassage (repères, ports) ; rapports de test de chaque lien ; configuration (adresses de la box, du switch, identifiants remis séparément) ; résultats de la validation ; procès-verbal de réception signé, réserves éventuelles."),
            _c("Utilité", 1, "Preuve que l'installation est conforme ; base pour tout dépannage ou extension ; garantie ; tenu à jour à chaque modification."),
        ),
        correction=(
            "Le dossier contient : le plan des locaux avec les prises, la baie et les chemins ; le plan de brassage (repère de chaque prise, port du panneau, port du switch) ; le rapport de test de chaque lien (PASS) ; la configuration de base (box, switch, adresses) — mots de passe remis à part ; les résultats de la validation (lien, adresse, passerelle, autre poste, Internet, partage) ; le procès-verbal de réception signé, avec les réserves éventuelles.",
            "Il prouve que l'installation livrée est conforme, sert de base à tout dépannage ou extension (on retrouve un lien par son repère) et à la garantie. On le remet au client et on le met à jour à chaque modification.",
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
        title="Où placer la baie d'un bâtiment en longueur ?",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_PLAN,
        context=(
            "Un centre de formation occupe un bâtiment de plain-pied de 70 m de long. Deux "
            "emplacements sont possibles pour la baie. Le document 1 donne, pour chacun, le parcours "
            "horizontal jusqu'à la prise la plus éloignée. Convention : longueur = parcours + 5 m, "
            f"arrondie au mètre supérieur ; lien permanent ≤ {PERMANENT_LINK_MAX_M} m."
        ),
        documents=(
            _table("Document 1 — Emplacements possibles", ("Emplacement", "Parcours jusqu'à la prise la plus éloignée"),
                   *((t, f"{fr(h)} m") for t, h in X01_CANDIDATES)),
        ),
        instructions=("Choisis l'emplacement de la baie en justifiant par un calcul, puis cite deux autres conditions que le local doit remplir.",),
        criteria=(
            _c("Calcul et choix", 1, f"A : {fr(X01_CANDIDATES[0][1])} + 5 → {X01_LENGTHS[0]} m > {PERMANENT_LINK_MAX_M} m ; B : {X01_LENGTHS[1]} m ≤ {PERMANENT_LINK_MAX_M} m → emplacement B, au centre."),
            _c("Conditions du local", 1, "Fermé à clé, ventilé, sec, avec une prise électrique dédiée ; proche de l'arrivée de l'opérateur si possible ; loin des sources de chaleur et d'eau."),
        ),
        correction=(
            f"Emplacement A : {fr(X01_CANDIDATES[0][1])} + 5 = {fr(X01_CANDIDATES[0][1] + 5)} → {X01_LENGTHS[0]} m, au-delà des {PERMANENT_LINK_MAX_M} m du lien permanent : la prise la plus éloignée ne serait pas conforme. Emplacement B : {fr(X01_CANDIDATES[1][1])} + 5 = {X01_LENGTHS[1]} m : conforme, avec de la marge. On choisit B, au centre de l'étoile, qui raccourcit aussi tous les autres liens.",
            "Le local doit en outre être fermé à clé, ventilé et sec, disposer d'une prise électrique dédiée, et si possible être proche de l'arrivée de la ligne de l'opérateur.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Relier un second bâtiment",
        question_type="short_answer",
        requirement_ids=("AP-36",),
        kind=KIND_PLAN,
        context=(
            "Une asbl occupe deux bâtiments séparés par une cour : 120 m de parcours entre les deux "
            "locaux techniques. Le bâtiment B a huit postes. Le trésorier propose de tirer un seul "
            "câble Cat6 « bien blindé » depuis le switch du bâtiment A jusqu'au switch du bâtiment B."
        ),
        instructions=("Dis si la proposition convient et propose une solution justifiée pour l'ensemble des deux bâtiments.",),
        criteria=(
            _c("Analyse", 1, "Non : 120 m > 100 m du canal cuivre, quel que soit le blindage ; un câble cuivre relierait électriquement deux bâtiments (terres différentes, foudre)."),
            _c("Solution", 1, "Fibre optique (câble d'extérieur) entre les deux switchs, modules adaptés ; dans chaque bâtiment, câblage cuivre en étoile depuis son switch, liens ≤ 90 m."),
        ),
        correction=(
            "Le Cat6 ne convient pas : un canal cuivre est limité à 100 m (120 m ici), blindé ou non, et il relierait électriquement deux bâtiments dont les terres peuvent être à des potentiels différents (courants, foudre).",
            "Solution : une fibre optique prévue pour l'extérieur entre les switchs des deux bâtiments (modules identiques aux deux bouts, portée et budget vérifiés) ; dans chaque bâtiment, une étoile en cuivre depuis son switch, chaque lien restant sous 90 m.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Nomenclature d'un petit cabinet",
        question_type="short_answer",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            f"Un cabinet de dentistes veut {X03_POSTES} postes à deux prises chacun, une prise pour "
            "l'imprimante et une pour un point d'accès Wi-Fi au plafond. Le panneau de brassage de 24 "
            "ports est vide (à équiper de keystones). Convention : 20 % de ports de réserve sur le "
            "switch et un port pour la box."
        ),
        instructions=("Calcule le nombre de liens, de keystones et de cordons, et la taille du switch.",),
        criteria=(
            _c("Liens et accessoires", 1, f"{X03_POSTES} × 2 + 1 + 1 = {X03_LINKS} liens ; {2 * X03_LINKS} keystones (prise + panneau) ; {X03_LINKS} cordons de brassage et {X03_LINKS} cordons de poste ; 1 panneau 24 ports."),
            _c("Switch", 1, f"{X03_LINKS} × 1,2 → {X03_PORTS - 1} + 1 = {X03_PORTS} ports → switch {X03_SWITCH} ports, PoE pour le point d'accès."),
        ),
        correction=(
            f"Liens : {X03_POSTES} postes × 2 prises + imprimante + point d'accès = {X03_LINKS}. Chaque lien a un keystone à la prise et un au panneau : {2 * X03_LINKS} keystones ; un cordon de brassage et un cordon de poste par lien : {X03_LINKS} + {X03_LINKS}. Un panneau de 24 ports suffit.",
            f"Switch : {X03_LINKS} + 20 % = {X03_PORTS - 1} ports (arrondi au-dessus), plus 1 pour la box = {X03_PORTS} : on prend un {X03_SWITCH} ports, avec PoE pour alimenter le point d'accès.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Calculer un devis",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_QUOTE,
        context=(
            "Tu prépares le devis du câblage d'un petit commerce. Le document 1 donne les quantités et "
            f"les prix unitaires hors TVA (prix fictifs). Le taux de TVA applicable est de {fr(VAT_RATE * 100, 0)} %."
        ),
        documents=(
            _table("Document 1 — Lignes du devis (€ HT)", ("Réf.", "Désignation", "Qté", "PU HT"),
                   *((line.ref, line.label, str(line.quantity), euro(line.unit_price)) for line in X04_LINES)),
        ),
        instructions=("Calcule le total de chaque ligne, le total HT, la TVA et le total TTC.",),
        criteria=(
            _c("Lignes", 1, " ; ".join(f"{line.ref} {euro(line.total)}" for line in X04_LINES) + "."),
            _c("Totaux", 1, f"HT {euro(X04_HT)} ; TVA 21 % {euro(X04_VAT)} ; TTC {euro(X04_TTC)}."),
        ),
        correction=(
            "Total de chaque ligne = quantité × prix unitaire : " + " ; ".join(f"{line.ref} {line.quantity} × {euro(line.unit_price)} = {euro(line.total)}" for line in X04_LINES) + ".",
            f"Total HT : {euro(X04_HT)}. TVA : {euro(X04_HT)} × 21 % = {euro(X04_VAT)}. Total TTC : {euro(X04_TTC)}.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Le switch PoE suffira-t-il ?",
        question_type="short_answer",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_QUOTE,
        context=(
            f"Une crèche veut alimenter par le câble deux points d'accès Wi-Fi de classe 4 et quatre "
            f"caméras IP de classe 3 avec un switch PoE déjà en stock, dont le budget PoE total est de "
            f"{fr(X05_BUDGET, 0)} W. Puissance réservée par port : classe 3 {fr(POE_CLASS_W[3])} W, classe 4 {fr(POE_CLASS_W[4])} W."
        ),
        instructions=("Calcule la puissance nécessaire, conclus et propose une solution.",),
        criteria=(
            _c("Calcul et conclusion", 1, f"2 × 30 + 4 × 15,4 = {fr(X05_TOTAL)} W > {fr(X05_BUDGET, 0)} W → {poe_verdict(X05_CLASSES, X05_BUDGET).lower()} : un appareil risque de ne pas démarrer ou de s'éteindre."),
            _c("Solution", 1, "Switch avec un budget PoE plus élevé (par exemple ≥ 130 W ou PoE+ 195 W) ; ou injecteur PoE pour un appareil ; ne pas compter seulement les ports."),
        ),
        correction=(
            f"Puissance réservée : 2 points d'accès × 30 W + 4 caméras × 15,4 W = 60 + 61,6 = {fr(X05_TOTAL)} W. C'est plus que les {fr(X05_BUDGET, 0)} W du switch : {POE_KO.lower()}. Le switch refusera d'alimenter un des appareils (ou le coupera) alors que les ports sont libres.",
            "Solution : choisir un switch dont le budget PoE total dépasse la somme (par exemple 195 W), ou alimenter un appareil par un injecteur PoE. On vérifie toujours le budget total, pas seulement le nombre de ports PoE.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Rapport de test : que faire de chaque lien ?",
        question_type="document_analysis",
        requirement_ids=("AP-36",),
        kind=KIND_TEST,
        context=(
            "Le certificateur a signalé trois liens en échec dans une école primaire qui vient de "
            "faire câbler ses classes en Cat6A, panneau et keystones blindés. Le "
            f"document 1 résume leurs résultats. Lien permanent ≤ {PERMANENT_LINK_MAX_M} m."
        ),
        documents=(
            _table("Document 1 — Liens en échec (extrait du rapport)", ("Repère", "Câblage", "Longueur", "Résultat"),
                   ("B1-P1-04", "fils 3 et 6 inversés", "31 m", "FAIL"),
                   ("B1-P1-11", "correct", "94 m", "FAIL"),
                   ("B1-P1-15", "correct", "48 m", "FAIL (paradiaphonie au panneau)")),
        ),
        instructions=("Pour chaque lien, donne le défaut et l'action corrective, puis ce que tu fais après la correction.",),
        criteria=(
            _c("Défauts et actions", 1.5, f"04 : {X06_VERDICTS[0].lower()} → refaire le raccordement (keystone ou panneau) selon la même norme ; 11 : {X06_VERDICTS[1].lower()} → nouveau parcours, baie ou switch plus proche ; 15 : {X06_VERDICTS[2].lower()} → refaire le poinçonnage au panneau (détorsadage ≤ 13 mm), vérifier la catégorie des composants."),
            _c("Après", 0.5, "Retester chaque lien corrigé, archiver les rapports PASS dans le dossier de recette."),
        ),
        correction=(
            "B1-P1-04 : deux fils inversés, défaut de câblage : on refait le raccordement fautif (keystone ou panneau) en suivant la même norme T568A ou B aux deux bouts. B1-P1-11 : câblage correct mais 94 m, trop long : on raccourcit le parcours ou on rapproche le point de distribution (switch supplémentaire).",
            "B1-P1-15 : câblage et longueur corrects mais paradiaphonie au panneau : raccordement mal fait (paires trop détorsadées, plus de 13 mm) ; on refait le poinçonnage et on vérifie que tous les composants sont de catégorie 6A. Après correction, on reteste chaque lien et on archive les rapports PASS.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Un poste neuf n'a pas d'adresse",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_TEST,
        context=(
            "Pendant la validation du réseau d'un cabinet de géomètres, le poste du deuxième bureau "
            "affiche le voyant réseau allumé, mais rien ne fonctionne. Les autres postes sont "
            "corrects. Le document 1 montre ce que tu relèves."
        ),
        documents=(
            _console(
                "Document 1 — Relevé sur le poste (capture fictive)",
                "C:\\> ipconfig",
                "Carte Ethernet Ethernet :",
                "   Adresse IPv4 configurée automatiquement : 169.254.88.14",
                "   Masque de sous-réseau. . . . . . . . . : 255.255.0.0",
                "   Passerelle par défaut. . . . . . . . . :",
            ),
        ),
        instructions=("Dis quel contrôle échoue, ce que cela signifie et les vérifications à faire, dans l'ordre.",),
        criteria=(
            _c("Diagnostic", 1, f"Lien correct (voyant) ; adresse 169.254 sans passerelle → {validation_diagnosis(first_failure('adresse')).lower()} : le poste n'a reçu aucune réponse du serveur DHCP (la box)."),
            _c("Vérifications", 1, "Port du switch dans le bon réseau (brassage, switch relié à la box), carte en adresse automatique, renouveler l'adresse (ipconfig /renew) ; puis reprendre la validation : passerelle, autre poste, Internet, partage."),
        ),
        correction=(
            "Le lien physique est bon (voyant allumé). L'adresse 169.254.x.x, sans passerelle, est une adresse que Windows s'attribue quand aucun serveur DHCP ne répond : le contrôle « adresse » échoue. Les contrôles suivants (ping de la box, Internet, partage) échoueront tous tant que ce point n'est pas réglé.",
            "Vérifications : la prise est-elle brassée sur un port du switch relié à la box (et pas sur un autre réseau) ? La carte est-elle en adresse automatique ? On renouvelle l'adresse (ipconfig /renew) ; on doit obtenir une adresse du réseau de la box et sa passerelle ; puis on reprend la validation dans l'ordre et on consigne.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Câbles réseau à côté des câbles électriques",
        question_type="short_answer",
        requirement_ids=("AP-36",),
        kind=KIND_SAFETY,
        context=(
            "Dans une boulangerie, le câble réseau du poste de la caisse a été couché sur le même "
            f"chemin que deux circuits électriques, à {X08_DISTANCE} mm, sans cloison. La fiche du câble "
            f"donne une classe de séparation « {X08_CLASS} » ; la norme EN 50174-2 demande alors {X08_MIN} mm sans "
            "cloison (jusqu'à trois circuits)."
        ),
        instructions=("Dis si la pose est conforme, pourquoi la règle existe, et ce que tu corriges.",),
        criteria=(
            _c("Conformité et raison", 1, f"{X08_DISTANCE} mm < {X08_MIN} mm : non conforme ; les câbles d'énergie induisent des parasites (erreurs, lenteurs) et une séparation protège aussi les câbles de données."),
            _c("Correction", 1, f"Déplacer le câble à ≥ {X08_MIN} mm, ou chemin à cloison métallique ; croiser à angle droit ; retester le lien."),
        ),
        correction=(
            f"Non conforme : {X08_DISTANCE} mm au lieu de {X08_MIN} mm au moins. Les câbles d'énergie, surtout avec des appareils à moteur ou à résistance comme dans une boulangerie, induisent des parasites dans le câble de données (erreurs, lenteurs, coupures).",
            f"On déplace le câble réseau à {X08_MIN} mm au moins, ou dans un compartiment séparé par une cloison métallique ; on croise les câbles électriques à angle droit ; on reteste le lien et on met à jour le plan.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Retrouver un lien grâce à son repère",
        question_type="short_answer",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_TEST,
        context=(
            "Dans une PME, une employée signale que sa prise « B1-P2-05 » ne fonctionne plus. "
            "Convention de l'entreprise : repère B<baie>-P<panneau>-<port>, identique à la prise et "
            "au panneau ; le port n du panneau 1 est brassé sur le port n du switch 1, le port n du "
            "panneau 2 sur le port n du switch 2."
        ),
        instructions=("Dis où se trouve le lien dans la baie et décris ta démarche de dépannage.",),
        criteria=(
            _c("Localisation", 1, "Baie 1, panneau 2, port 05 ; brassé sur le port 5 du switch 2."),
            _c("Démarche", 1, "Voyant du port ; changer le cordon de poste puis le cordon de brassage ; tester le lien au testeur (câblage, longueur) ; essayer un autre port du switch ; corriger, retester, mettre le plan à jour."),
        ),
        correction=(
            "B1-P2-05 : baie 1, panneau 2, port 05 ; d'après la convention, il est brassé sur le port 5 du switch 2. On trouve le lien sans ouvrir les goulottes ni débrancher les voisins.",
            "On regarde le voyant du port 5 du switch 2 ; on change le cordon de poste, puis le cordon de brassage ; on teste le lien permanent au testeur entre la prise et le panneau ; on essaie un autre port du switch. On corrige l'élément fautif, on reteste et on met à jour le plan de brassage si un port a changé.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Équiper une baie de 9 U",
        question_type="short_answer",
        requirement_ids=("AP-36",),
        kind=KIND_PLAN,
        context=(
            "Pour un cabinet de kinésithérapie, tu dois monter dans une baie murale de 9 U : "
            + ", ".join(X10_ITEMS[i].lower() for i in (0, 1, 2, 3, 4))
            + ". Convention de l'atelier : brassage en haut, électricité en bas."
        ),
        instructions=("Propose l'ordre de montage du haut vers le bas, calcule la réserve et justifie.",),
        criteria=(
            _c("Ordre", 1, "Panneau de brassage → passe-câbles → switch → étagère de la box → bandeau électrique (en bas)."),
            _c("Réserve et justification", 1, "6 U occupées, 3 U libres ; cordons courts entre panneau et switch ; électricité à l'écart des cordons ; place pour l'évolution."),
        ),
        correction=(
            "Du haut vers le bas : panneau de brassage (1 U), passe-câbles (1 U), switch (1 U), étagère de la box (2 U), bandeau de prises électriques (1 U). Hauteur : 6 U sur 9 ; il reste 3 U libres.",
            "Le passe-câbles entre panneau et switch garde les cordons de brassage courts et rangés ; la box sous le switch se relie par un cordon court ; l'électricité, en bas, reste à l'écart des cordons de données ; les 3 U libres laissent l'air circuler et permettent d'ajouter un panneau.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, schémas à compléter et devis demandés par le ticket."""
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
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 5:
        errors.append("Ticket #219 : au moins 5 schémas à compléter.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_QUOTE) < 4:
        errors.append("Ticket #219 : au moins 4 devis ou nomenclatures.")
    if len(E17_TOO_LONG) != 1 or E10_ERRORS:
        errors.append("E10/E17 : données de longueur incohérentes.")
    if E15_CHOICE != "S2" or poe_verdict(X05_CLASSES, X05_BUDGET) != POE_KO:
        errors.append("E15/X05 : verdicts PoE inattendus.")
    if {validation_diagnosis(first_failure(k)) for _t, k in E07_CASES} != set(DIAGNOSES):
        errors.append("E07 : toutes les pistes doivent être utilisées.")
    if {D_PHYS, D_IP, D_GW, D_PEER, D_NET, D_SHARE} != set(DIAGNOSES):
        errors.append("Pistes de validation incohérentes.")
    return errors

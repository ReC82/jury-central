"""PR17 « Fibre optique — choix, raccordement et diagnostic » — exercices corrigés et
mini-examen (ticket #218).

Même organisation que PR14 (`app.v1.ampcr_pratique_pr14_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 18 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (nettoyage d'un connecteur, pose et contrôle,
  diagnostic), classements (puissance reçue, événements d'une trace OTDR, compatibilité des
  modules, identification d'une fibre, cause probable d'une panne), documents (rapport de
  photométrie, trace OTDR, relevé des modules, choix d'un module, commande de jarretières,
  rapport de chantier), rédactions (sécurité laser, éclats, comparaison avec le cuivre,
  pigtail et épissure) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et les fiches de modules sont **fictives** ; tous les nombres des énoncés,
barèmes et corrigés viennent des fonctions de `app.v1.ampcr_pratique_pr17_figures` (mêmes
données que les schémas).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr14_figures import REACH_M, choose_10g
from app.v1.ampcr_pratique_pr17_figures import (
    CLEAN_STEPS,
    COMPAT_VERDICTS,
    DIAG_STEPS,
    FAMILIES,
    INSTALL_STEPS,
    LR_SPEC,
    OTDR_KINDS,
    RX_STATUSES,
    SR_SPEC,
    OtdrEvent,
    RxSpec,
    break_position_m,
    dbm_fr,
    fibre_family,
    fr,
    max_link_loss_db,
    measured_loss_db,
    min_bend_radius_mm,
    module_errors,
    module_verdict,
    otdr_event_kind,
    photometry_verdict,
    rx_power_dbm,
    rx_status,
)

PR17_CODE = "PR17"

KIND_ORDER = "ordonnancement"
KIND_CHOICE = "choix de la fibre et des modules"
KIND_CONNECT = "raccordement et pose"
KIND_MEASURE = "mesure et contrôle"
KIND_DIAG = "diagnostic"
KIND_SAFETY = "sécurité"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-21", "AP-22"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(CLEAN_STEPS)
E02_STEPS = _labels(INSTALL_STEPS)
E03_STEPS = _labels(DIAG_STEPS)

# (description, puissance reçue en dBm ou None si LOS) — fiche d'exemple 10GBASE-LR
E04_CASES: tuple[tuple[str, float | None], ...] = (
    ("Liaison de 2 km : −3,8 dBm", -3.8),
    ("Port du bâtiment C : −40,0 dBm, alarme LOS", None),
    ("Liaison de 9 km avec trois épissures refaites : −16,2 dBm", -16.2),
    ("Liaison de 5 m entre deux baies voisines : +1,4 dBm", 1.4),
    ("Liaison de 7 km : −13,9 dBm", -13.9),
    ("Liaison de 4 km : −9,0 dBm", -9.0),
    ("Connecteur visiblement taché : −22,5 dBm", -22.5),
    ("Jarretière débranchée côté tiroir : −31,0 dBm", -31.0),
)
E04_CORRECT = tuple(RX_STATUSES.index(rx_status(rx, LR_SPEC)) for _t, rx in E04_CASES)

E05_EVENTS: tuple[tuple[str, OtdrEvent], ...] = (
    ("À 980 m : sans pic, 0,1 dB à 1 310 nm mais 0,9 dB à 1 550 nm", OtdrEvent(980, False, 0.1, 0.9)),
    ("À 1 200 m : pic de réflexion, perte 0,6 dB, la trace continue", OtdrEvent(1200, True, 0.6, 0.6)),
    ("À 412 m alors que la liaison mesure 640 m : grand pic, puis plus que du bruit", OtdrEvent(412, True, 0, 0, end=True)),
    ("À 620 m : marche de 0,05 dB sans pic, même valeur à 1 310 et à 1 550 nm", OtdrEvent(620, False, 0.05, 0.05)),
    ("Au passage d'un coffret, sans pic : 0,3 dB à 1 310 nm, 1,4 dB à 1 550 nm", OtdrEvent(2100, False, 0.3, 1.4)),
    ("À 150 m : pic de réflexion, perte 0,4 dB, la trace continue", OtdrEvent(150, True, 0.4, 0.4)),
    ("À 1 750 m : marche de 0,15 dB sans pic, identique aux deux longueurs d'onde", OtdrEvent(1750, False, 0.15, 0.15)),
)
E05_CORRECT = tuple(OTDR_KINDS.index(otdr_event_kind(e)) for _t, e in E05_EVENTS)

# (module A, module B, fibre, longueur)
E06_CASES: tuple[tuple[str, str, str, float], ...] = (
    ("10GBASE-SR", "10GBASE-SR", "OM3", 180),
    ("10GBASE-SR", "10GBASE-SR", "OM2", 150),
    ("10GBASE-LR", "10GBASE-LR", "OS2", 3200),
    ("10GBASE-SR", "10GBASE-LR", "OS2", 800),
    ("10GBASE-SR", "10GBASE-SR", "OS2", 40),
    ("1000BASE-SX", "1000BASE-SX", "OM1", 320),
    ("1000BASE-LX", "1000BASE-LX", "OS2", 4000),
    ("10GBASE-LR", "10GBASE-LR", "OM4", 90),
)


def _e06_text(a: str, b: str, fibre: str, m: float) -> str:
    modules = f"{a} aux deux extrémités" if a == b else f"{a} d'un côté, {b} de l'autre"
    length = f"{fr(m / 1000)} km" if m >= 1000 else f"{m:g} m"
    return f"{modules}, fibre {fibre}, {length}"


E06_ELEMENTS = tuple(_e06_text(*case) for case in E06_CASES)
E06_CORRECT = tuple(COMPAT_VERDICTS.index(module_verdict(*case)) for case in E06_CASES)

# (marquage relevé, code de la fibre)
E07_CASES: tuple[tuple[str, str], ...] = (
    ("Gaine orange, marquage « 62.5/125 »", "OM1"),
    ("Gaine jaune, marquage « 9/125 OS2 »", "OS2"),
    ("Gaine aqua (turquoise), marquage « 50/125 OM3 »", "OM3"),
    ("Gaine violette, marquage « 50/125 OM4 »", "OM4"),
    ("Gaine orange, marquage « 50/125 OM2 »", "OM2"),
    ("Jarretière à connecteurs verts SC/APC, gaine jaune", "OS2"),
    ("Câble d'extérieur à gaine noire, marquage « OS2 9/125 »", "OS2"),
    ("Gaine aqua, marquage « 50/125 OM4 »", "OM4"),
)
E07_CORRECT = tuple(FAMILIES.index(fibre_family(code)) for _t, code in E07_CASES)

CAUSE_POLARITY = "Polarité inversée"
CAUSE_DIRTY = "Connecteur sale"
CAUSE_MODULE = "Mauvais module"
CAUSE_REACH = "Distance trop grande pour le module"
CAUSE_BREAK = "Fibre cassée"
CAUSES = (CAUSE_POLARITY, CAUSE_DIRTY, CAUSE_MODULE, CAUSE_REACH, CAUSE_BREAK)
E08_CASES: tuple[tuple[str, str], ...] = (
    ("Après un échange de switch : module 850 nm branché sur une fibre jaune monomode", CAUSE_MODULE),
    ("Après des travaux : aucune lumière au photomètre, la trace OTDR s'arrête à mi-parcours", CAUSE_BREAK),
    ("Lien neuf : LOS des deux côtés ; au photomètre, chaque fibre laisse passer la lumière avec 1,8 dB de perte", CAUSE_POLARITY),
    ("10GBASE-SR sur OM1 de 120 m : perte mesurée 2,0 dB, lien instable et erreurs", CAUSE_REACH),
    ("Erreurs CRC ; puissance reçue 8 dB sous la valeur calculée d'un seul côté ; l'inspection montre une tache", CAUSE_DIRTY),
    ("Module 1000BASE-LX d'un côté, 1000BASE-SX de l'autre, aucun lien", CAUSE_MODULE),
    ("Lien ouvert après un rebrassage : LOS des deux côtés, puissance émise normale, fibres testées bonnes", CAUSE_POLARITY),
)
E08_CORRECT = tuple(CAUSES.index(cause) for _t, cause in E08_CASES)

E09_REF = -10.0
E09_LENGTH, E09_CONNECTORS, E09_SPLICES = 1600, 2, 2
E09_MAX = max_link_loss_db(E09_LENGTH, "OS2", 1310, E09_CONNECTORS, E09_SPLICES)
E09_READINGS: tuple[tuple[str, float], ...] = (("F1", -12.30), ("F2", -12.05), ("F3", -15.80), ("F4", -12.60))
E09_LOSSES = {f: measured_loss_db(E09_REF, r) for f, r in E09_READINGS}
E09_VERDICTS = {f: photometry_verdict(loss, E09_MAX) for f, loss in E09_LOSSES.items()}

E10_LAUNCH, E10_LINK, E10_END = 150, 640, 562
E10_BREAK = break_position_m(E10_END, E10_LAUNCH)
E10_MAX_BEFORE = max_link_loss_db(E10_LINK, "OS2", 1310, 2, 2)
E10_MAX_AFTER = max_link_loss_db(E10_LINK, "OS2", 1310, 2, 4)

E11_LENGTH = 100
E11_MAX = max_link_loss_db(E11_LENGTH, "OM3", 850, 2, 0)
E11_A_TX, E11_A_RX, E11_B_TX, E11_B_RX = -2.5, -2.9, -2.6, -10.8
E11_LOSS_AB = round(E11_A_TX - E11_B_RX, 2)
E11_LOSS_BA = round(E11_B_TX - E11_A_RX, 2)

E12_LENGTH, E12_SPLICES = 1200, 4
E12_LOSS = max_link_loss_db(E12_LENGTH, "OS2", 1310, 2, E12_SPLICES)
E12_BUDGET = 6.2
E12_MARGIN = round(E12_BUDGET - E12_LOSS, 2)

E14_DIAMETER = 8
E14_REST = min_bend_radius_mm(E14_DIAMETER, pulling=False)
E14_PULL = min_bend_radius_mm(E14_DIAMETER, pulling=True)

X01_LENGTH = 600
X01_MAX = max_link_loss_db(X01_LENGTH, "OS2", 1310, 2, 2)

X02_LENGTH, X02_TX, X02_RX = 20, -2.0, -12.6
X02_MAX = max_link_loss_db(X02_LENGTH, "OM4", 850, 2, 0)
X02_EXPECTED_RX = rx_power_dbm(X02_TX, X02_MAX)
X02_LOSS = round(X02_TX - X02_RX, 2)

X03_ERRORS = module_errors("10GBASE-SR", "10GBASE-LR", "OS2", 2000)

X04_LENGTH = 140
X04_LOSS = max_link_loss_db(X04_LENGTH, "OM2", 850, 2, 0)

X05_LAUNCH, X05_LINK, X05_END = 100, 900, 487
X05_BREAK = break_position_m(X05_END, X05_LAUNCH)

X06_REF, X06_READ = -8.0, -10.95
X06_LOSS = measured_loss_db(X06_REF, X06_READ)
X06_MAX = max_link_loss_db(240, "OM3", 850, 2, 1)

X07_DIAMETER = 6
X07_REST = min_bend_radius_mm(X07_DIAMETER, pulling=False)
X07_PULL = min_bend_radius_mm(X07_DIAMETER, pulling=True)

X09_MEDIUM = choose_10g(180, between_buildings=True)

X10_SPEC = RxSpec(sensitivity_dbm=-23.0, overload_dbm=-3.0)  # fiche fictive « longue portée »
X10_TX, X10_LOSS = 1.0, 1.6
X10_RX = rx_power_dbm(X10_TX, X10_LOSS)
X10_MIN_ATT = round(X10_RX - X10_SPEC.overload_dbm, 2)
X10_ATT = 5.0
X10_RX_AFTER = rx_power_dbm(X10_RX, X10_ATT)

# =============================================================================================
# 18 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le nettoyage d'un connecteur",
        question_type="ordering",
        requirement_ids=("AP-21",),
        kind=KIND_ORDER,
        context=(
            "Dans la salle serveur d'une école, un lien optique vers le bâtiment des ateliers "
            "accumule les erreurs. Ton responsable te confie la fiche « nettoyage d'un connecteur "
            "optique » à appliquer sur la jarretière, mais ses six étapes ont été mélangées en "
            "recopiant la fiche."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Couper la lumière → inspecter → nettoyer à sec → réinspecter → raccorder → mesurer (0,5 pt par étape)."),
        ),
        correction=(
            "1. On coupe la lumière (port désactivé ou module retiré) et on le vérifie au photomètre, jamais en regardant. 2. On inspecte la fiche et la traversée avec une sonde d'inspection : on ne nettoie pas à l'aveugle. 3. On nettoie à sec (nettoyeur à cliquet ou lingette non pelucheuse, un seul passage).",
            "4. On réinspecte : si une salissure reste, nettoyage humide à l'alcool isopropylique puis à sec ; une face rayée se remplace. 5. On raccorde aussitôt, capuchons sur les connecteurs libres. 6. On mesure la puissance reçue ou la perte et on consigne.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (2, 5, 0, 3, 1, 4)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la pose et le contrôle d'une liaison",
        question_type="ordering",
        requirement_ids=("AP-21",),
        kind=KIND_ORDER,
        context=(
            "Une PME agrandit son entrepôt et fait poser une fibre entre le local technique et le "
            "nouveau bâtiment. Le sous-traitant a envoyé son mode opératoire en six étapes, mais "
            "dans le désordre ; tu dois le remettre en ordre avant la réunion de chantier."
        ),
        instructions=("Remets les six étapes de la pose dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Préparer → tirer → ranger → raccorder → contrôler → documenter (0,5 pt par étape)."),
        ),
        correction=(
            "1. On prépare : parcours, longueur, type de fibre, connecteurs, modules et budget calculé. 2. On tire le câble par son élément de traction (aramide), sans dépasser la tension ni le rayon de courbure. 3. On range : love de réserve, attaches non serrées, étiquettes aux deux extrémités.",
            "4. On raccorde : pigtails épissés dans les cassettes du tiroir optique, protections d'épissure posées. 5. On contrôle : nettoyage, inspection et mesure de chaque fibre au photomètre (et au réflectomètre si le cahier des charges le demande). 6. On documente : plan de brassage, polarité, mesures comparées au budget, rapport.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 3, 0, 5, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le diagnostic d'une liaison sans lien",
        question_type="ordering",
        requirement_ids=("AP-21",),
        kind=KIND_ORDER,
        context=(
            "Une liaison optique entre deux bâtiments d'une maison de repos ne monte plus depuis "
            "ce matin. La fiche de diagnostic de l'atelier, en six étapes, a été recopiée dans le "
            "désordre par un stagiaire ; tu dois la corriger avant de partir sur place."
        ),
        instructions=("Remets les six étapes dans l'ordre, de la plus simple à la plus longue.",),
        criteria=(
            _c("Ordre", 3, "Relever → modules → polarité → connecteurs → mesurer → réparer et consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On relève l'état des ports, les voyants, les modules et les puissances émise et reçue des deux côtés. 2. On vérifie les modules : même norme aux deux bouts, adaptée à la fibre et à la distance, reconnue par le switch. 3. On vérifie la polarité : le TX de chaque côté doit arriver sur le RX de l'autre.",
            "4. On inspecte et on nettoie les connecteurs, on vérifie les jarretières. 5. On mesure chaque fibre au photomètre, puis au réflectomètre pour localiser un défaut. 6. On répare, on remesure, on compare au budget et on consigne.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Puissance reçue : dans la plage de la fiche ?",
        question_type="classification",
        requirement_ids=("AP-21",),
        kind=KIND_MEASURE,
        context=(
            "Une intercommunale a équipé huit liaisons du même module 10GBASE-LR. Tu relèves la "
            "puissance reçue de chaque port. La fiche (fictive) du module indique : réception "
            f"de {dbm_fr(LR_SPEC.sensitivity_dbm)} dBm (sensibilité) à {dbm_fr(LR_SPEC.overload_dbm)} dBm (maximum) ; "
            "à −30 dBm ou moins, le module ne voit aucune lumière (LOS)."
        ),
        instructions=("Range chaque relevé selon l'état de la réception.",),
        criteria=(
            _c("Classement", 4, "LOS et −31,0 dBm → aucune lumière ; −16,2 et −22,5 dBm → trop faible ; −3,8, −9,0 et −13,9 dBm → dans la plage ; +1,4 dBm → saturation (0,5 pt par élément)."),
        ),
        correction=(
            f"On compare chaque valeur à la fiche : en dessous de {dbm_fr(LR_SPEC.sensitivity_dbm)} dBm, le récepteur ne décode plus correctement (−16,2 et −22,5 dBm : trop faible) ; jusqu'à −30 dBm et en dessous, il ne voit plus de lumière (LOS, −31,0 dBm : jarretière débranchée, fibre coupée ou polarité inversée).",
            f"Entre {dbm_fr(LR_SPEC.sensitivity_dbm)} et {dbm_fr(LR_SPEC.overload_dbm)} dBm, la réception est correcte (−3,8 ; −9,0 ; −13,9 dBm, ce dernier avec très peu de marge). Au-dessus de {dbm_fr(LR_SPEC.overload_dbm)} dBm (+1,4 dBm sur 5 m), le récepteur sature : on ajoute l'atténuateur prévu par la fiche ou on choisit un module adapté à la distance.",
        ),
        classification=Classification(
            categories=RX_STATUSES, elements=tuple(t for t, _r in E04_CASES), correct=E04_CORRECT,
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Événements d'une trace de réflectomètre",
        question_type="classification",
        requirement_ids=("AP-21",),
        kind=KIND_MEASURE,
        context=(
            "Un bureau d'études a mesuré plusieurs liaisons monomodes au réflectomètre (OTDR), à "
            "1 310 et 1 550 nm, avec une bobine amorce. Il te transmet sept événements relevés "
            "sur les traces. Rappel : un pic signale une réflexion ; une courbure perd nettement "
            "plus à 1 550 nm qu'à 1 310 nm."
        ),
        instructions=("Range chaque événement selon sa nature probable.",),
        criteria=(
            _c("Classement", 3.5, "Pics avec perte et trace qui continue (150 m, 1 200 m) → connecteurs ; marches sans pic égales aux deux longueurs d'onde (620 m, 1 750 m) → épissures ; perte bien plus forte à 1 550 nm (980 m, coffret) → courbures ; grand pic puis bruit à 412 m → fin de fibre ou cassure (0,5 pt par élément)."),
        ),
        correction=(
            "Un connecteur renvoie un peu de lumière : pic de réflexion, petite perte, et la trace continue après. Une épissure par fusion ne réfléchit presque rien : simple marche, de même valeur à 1 310 et 1 550 nm.",
            "Une courbure trop serrée ne réfléchit pas non plus, mais elle perd beaucoup plus à 1 550 nm qu'à 1 310 nm : c'est la signature à chercher (0,9 dB contre 0,1 dB ; 1,4 dB contre 0,3 dB). Après un grand pic, une trace qui tombe dans le bruit marque la fin de la fibre : si c'est avant la longueur prévue (412 m sur 640 m), c'est une cassure.",
        ),
        classification=Classification(
            categories=OTDR_KINDS, elements=tuple(t for t, _e in E05_EVENTS), correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Modules et fibres : la liaison est-elle possible ?",
        question_type="classification",
        requirement_ids=("AP-21",),
        kind=KIND_CHOICE,
        context=(
            "Tu relis la commande de modules optiques d'un collègue pour huit liaisons. Portées "
            "(IEEE 802.3) : 10GBASE-SR 82 m sur OM2, 300 m sur OM3, 400 m sur OM4 ; 1000BASE-SX "
            "275 m sur OM1 ; 10GBASE-LR 10 km et 1000BASE-LX 5 km sur monomode OS2. Les modules SR "
            "et SX sont multimodes, LR et LX monomodes."
        ),
        instructions=("Range chaque liaison selon le premier défaut trouvé, ou « Compatible ».",),
        criteria=(
            _c("Classement", 4, "SR/OM3 180 m, LR/OS2 3,2 km, LX/OS2 4 km → compatibles ; SR et LR mélangés → modules différents ; SR sur OS2, LR sur OM4 → module inadapté à la fibre ; SR/OM2 150 m, SX/OM1 320 m → portée dépassée (0,5 pt par élément)."),
        ),
        correction=(
            "On vérifie dans l'ordre : les deux extrémités portent-elles le même type de module ? (SR d'un côté, LR de l'autre : non, longueurs d'onde et fibres différentes). Le module est-il prévu pour la fibre posée ? (SR multimode sur fibre jaune OS2, LR monomode sur OM4 : non).",
            f"La longueur respecte-t-elle la portée du module sur cette fibre ? En multimode, la dispersion limite la portée même si la perte est faible : SR sur OM2 tient {REACH_M[('10GBASE-SR', 'OM2')]} m (150 m : non), SX sur OM1 {REACH_M[('1000BASE-SX', 'OM1')]} m (320 m : non). SR sur OM3 à 180 m, LR à 3,2 km et LX à 4 km sur OS2 sont compatibles ; il reste à vérifier le budget.",
        ),
        classification=Classification(categories=COMPAT_VERDICTS, elements=E06_ELEMENTS, correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Identifier une fibre d'après sa gaine et son marquage",
        question_type="classification",
        requirement_ids=("AP-21",),
        kind=KIND_CHOICE,
        context=(
            "Dans le local technique d'une ancienne usine reconvertie en bureaux, tu fais "
            "l'inventaire des câbles et jarretières optiques avant de commander des modules. Tu "
            "notes la couleur de chaque gaine et ce qui est imprimé dessus ; la documentation "
            "d'origine a disparu."
        ),
        instructions=("Range chaque câble ou jarretière dans la famille de fibre qui convient.",),
        criteria=(
            _c("Classement", 4, "62.5/125 et OM2 orange → multimode ancienne ; OM3 aqua, OM4 violet ou aqua → multimode optimisée laser ; jaune 9/125, SC/APC vert, câble noir marqué OS2 → monomode (0,5 pt par élément)."),
        ),
        correction=(
            "Le marquage imprimé sur la gaine fait foi : 62.5/125 ou 50/125 OM1/OM2 = multimode ancienne (gaine orange en général) ; 50/125 OM3 ou OM4 = multimode optimisée laser (gaine aqua, parfois violette pour l'OM4) ; 9/125 OS1 ou OS2 = monomode (gaine jaune en intérieur).",
            "Un câble d'extérieur est souvent noir quel que soit son type : on lit le marquage (OS2). Un connecteur vert est un APC, utilisé en monomode. Les couleurs sont un usage courant (TIA-598), pas une garantie : en cas de doute, le marquage ou la documentation tranchent.",
        ),
        classification=Classification(
            categories=FAMILIES, elements=tuple(t for t, _c2 in E07_CASES), correct=E07_CORRECT,
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Quelle cause probable pour chaque panne optique ?",
        question_type="classification",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            "Le service informatique d'une province t'envoie le résumé de sept tickets sur des "
            "liaisons optiques. Pour chacun, il a noté les symptômes et les premières mesures. Tu "
            "dois orienter le technicien qui partira sur place vers la cause la plus probable."
        ),
        instructions=("Range chaque ticket selon la cause la plus probable.",),
        criteria=(
            _c("Classement", 3.5, "LOS des deux côtés avec des fibres bonnes au photomètre (lien neuf, rebrassage) → polarité ; perte excessive d'un seul côté avec tache → connecteur sale ; 850 nm sur fibre jaune, LX face à SX → mauvais module ; SR sur OM1 à 120 m → distance ; plus de lumière, trace qui s'arrête → fibre cassée (0,5 pt par élément)."),
        ),
        correction=(
            "LOS des deux côtés alors que chaque fibre, testée seule, transmet la lumière avec une perte normale : la lumière part bien, mais arrive sur un émetteur ; c'est la polarité (TX sur TX). Perte excessive dans un seul sens et salissure à l'inspection : connecteur sale.",
            f"Un module 850 nm (multimode) sur une fibre monomode, ou deux normes différentes aux deux bouts : mauvais module. 10GBASE-SR sur OM1 ne tient que {REACH_M[('10GBASE-SR', 'OM1')]} m : à 120 m, la perte est faible mais la dispersion empêche un lien stable. Plus aucune lumière et une trace OTDR qui s'arrête avant le bout : fibre cassée.",
        ),
        classification=Classification(
            categories=CAUSES, elements=tuple(t for t, _c2 in E08_CASES), correct=E08_CORRECT,
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Rapport de photométrie d'un câble de quatre fibres",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_MEASURE,
        context=(
            "Un câble monomode OS2 de quatre fibres relie le siège d'une mutuelle à son centre "
            f"d'archives. La liaison mesure {fr(E09_LENGTH / 1000)} km, avec {E09_CONNECTORS} paires de connecteurs et "
            f"{E09_SPLICES} épissures. Le document 1 donne la référence prise avec la source et le cordon de "
            "référence, puis la puissance lue au bout de chaque fibre, à 1 310 nm."
        ),
        documents=(
            _table(
                "Document 1 — Mesures au photomètre, 1 310 nm",
                ("Mesure", "Puissance lue"),
                ("Référence (source + cordon)", f"{dbm_fr(E09_REF)} dBm"),
                *((f"Fibre {f[1]}", f"{dbm_fr(r)} dBm") for f, r in E09_READINGS),
            ),
        ),
        instructions=(
            "Calcule la perte maximale admissible de la liaison (0,4 dB/km, 0,75 dB par paire de connecteurs, 0,3 dB par épissure).",
            "Calcule la perte de chaque fibre, conclus pour chacune et dis quoi faire.",
        ),
        criteria=(
            _c("Perte admissible", 1, f"1,6 km × 0,4 = 0,64 dB + 2 × 0,75 + 2 × 0,3 = {fr(E09_MAX, 2)} dB."),
            _c("Pertes mesurées", 1, "Perte = référence − lecture : " + ", ".join(f"{f} {fr(v, 2)} dB" for f, v in E09_LOSSES.items()) + "."),
            _c("Conclusion et action", 1, f"F1, F2, F4 conformes (≤ {fr(E09_MAX, 2)} dB) ; F3 non conforme ({fr(E09_LOSSES['F3'], 2)} dB) : inspecter et nettoyer ses connecteurs aux deux bouts, remesurer, puis réflectomètre si la perte reste élevée."),
        ),
        correction=(
            f"Perte admissible : fibre 1,6 km × 0,4 dB/km = 0,64 dB ; connecteurs 2 × 0,75 = 1,5 dB ; épissures 2 × 0,3 = 0,6 dB ; total {fr(E09_MAX, 2)} dB. La perte d'une fibre est la différence entre la référence et la puissance lue : " + " ; ".join(f"{f} : {fr(v, 2)} dB" for f, v in E09_LOSSES.items()) + ".",
            f"F1, F2 et F4 sont conformes. F3 ({fr(E09_LOSSES['F3'], 2)} dB) dépasse de {fr(E09_LOSSES['F3'] - E09_MAX, 2)} dB : on inspecte et nettoie ses connecteurs aux deux extrémités, on remesure ; si la perte reste trop forte, le réflectomètre localise le défaut (épissure ratée, courbure, connecteur abîmé). On consigne les quatre mesures.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Localiser une cassure sur une trace de réflectomètre",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            "Depuis le terrassement du parking, la liaison monomode entre la mairie et le hall "
            f"des sports ne fonctionne plus. Elle mesure {E10_LINK} m entre les deux tiroirs, avec deux "
            "pigtails épissés. Le photomètre ne voit plus aucune lumière. Le document 1 résume la "
            f"trace prise depuis la mairie, avec une bobine amorce de {E10_LAUNCH} m."
        ),
        documents=(
            _table(
                "Document 1 — Événements de la trace (1 550 nm, depuis la mairie)",
                ("Position", "Événement", "Perte"),
                (f"{E10_LAUNCH} m", "pic de réflexion, la trace continue", "0,35 dB"),
                (f"{E10_LAUNCH + 3} m", "marche sans pic", "0,05 dB"),
                (f"{E10_END} m", "grand pic de réflexion, puis bruit", "fin de trace"),
            ),
        ),
        instructions=(
            "Dis où se trouve la cassure, mesurée depuis le tiroir de la mairie, en justifiant.",
            "Propose la réparation et calcule la perte admissible après réparation (0,4 dB/km, 2 connecteurs à 0,75 dB, 0,3 dB par épissure).",
        ),
        criteria=(
            _c("Lecture", 1, f"150 m : connecteur du tiroir (début de la liaison) ; 153 m : épissure du pigtail ; {E10_END} m : fin de trace avant {E10_LAUNCH + E10_LINK} m → cassure."),
            _c("Position", 1, f"{E10_END} − {E10_LAUNCH} = {E10_BREAK:g} m depuis le tiroir de la mairie, le long du câble (réserves comprises)."),
            _c("Réparation et budget", 1, f"Ouvrir à cet endroit (zone des travaux), deux épissures par fusion dans un boîtier, ou remplacer le tronçon ; perte admissible {fr(E10_MAX_BEFORE, 2)} → {fr(E10_MAX_AFTER, 2)} dB ; remesurer, consigner."),
        ),
        correction=(
            f"Le pic à {E10_LAUNCH} m est le connecteur du tiroir de la mairie : la liaison commence là, après la bobine amorce. La petite marche sans pic juste après est l'épissure du pigtail. À {E10_END} m, un grand pic suivi de bruit marque la fin de la fibre, alors que la liaison devrait finir à {E10_LAUNCH + E10_LINK} m : c'est une cassure.",
            f"Position : {E10_END} − {E10_LAUNCH} = {E10_BREAK:g} m de fibre depuis le tiroir (longueur de câble, réserves comprises, pas forcément la distance au sol). On ouvre à cet endroit, on refait la continuité par deux épissures par fusion dans un boîtier étanche (ou on remplace le tronçon). Perte admissible : {fr(E10_MAX_BEFORE, 2)} dB avant, {fr(E10_MAX_AFTER, 2)} dB avec les deux épissures de plus ; on remesure (photomètre et OTDR) et on met à jour le dossier.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Relevé des modules : un sens de la liaison perd trop",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            "Dans un data center d'hébergement, une liaison 10GBASE-SR en OM3 de "
            f"{E11_LENGTH} m entre deux baies montre des erreurs CRC sur le switch B. Les modules "
            "affichent leurs puissances (document 1). La fiche (fictive) du module donne une "
            f"réception de {dbm_fr(SR_SPEC.sensitivity_dbm)} à {dbm_fr(SR_SPEC.overload_dbm)} dBm."
        ),
        documents=(
            _console(
                "Document 1 — Puissances lues sur les modules (capture fictive)",
                "Switch A  port Te1/0/50  10GBASE-SR",
                f"  Puissance émise   {dbm_fr(E11_A_TX)} dBm",
                f"  Puissance reçue   {dbm_fr(E11_A_RX)} dBm",
                "Switch B  port Te1/0/50  10GBASE-SR",
                f"  Puissance émise   {dbm_fr(E11_B_TX)} dBm",
                f"  Puissance reçue   {dbm_fr(E11_B_RX)} dBm   alarme : puissance reçue basse",
            ),
        ),
        instructions=(
            "Calcule la perte de chaque sens et la perte admissible de la liaison (3,5 dB/km à 850 nm, 2 connecteurs à 0,75 dB).",
            "Dis où chercher la cause, ce que tu fais et comment tu contrôles.",
        ),
        criteria=(
            _c("Calculs", 1.5, f"A → B : {dbm_fr(E11_A_TX)} − ({dbm_fr(E11_B_RX)}) = {fr(E11_LOSS_AB, 1)} dB ; B → A : {fr(E11_LOSS_BA, 1)} dB ; admissible : {fr(E11_LENGTH / 1000, 1)} × 3,5 + 1,5 = {fr(E11_MAX, 2)} dB."),
            _c("Diagnostic et action", 1.5, f"Seul le sens A → B perd trop (réception de B {dbm_fr(E11_B_RX)} dBm, sous {dbm_fr(SR_SPEC.sensitivity_dbm)} dBm) : connecteur sale ou abîmé sur cette fibre ; inspecter, nettoyer, réinspecter aux deux bouts ; contrôle : puissance reçue revenue vers −3 dBm, erreurs stables."),
        ),
        correction=(
            f"Perte d'un sens = puissance émise d'un côté − puissance reçue de l'autre. A → B : {dbm_fr(E11_A_TX)} − ({dbm_fr(E11_B_RX)}) = {fr(E11_LOSS_AB, 1)} dB. B → A : {dbm_fr(E11_B_TX)} − ({dbm_fr(E11_A_RX)}) = {fr(E11_LOSS_BA, 1)} dB. Perte admissible : {fr(E11_LENGTH / 1000, 1)} km × 3,5 dB/km + 2 × 0,75 dB = {fr(E11_MAX, 2)} dB.",
            f"Le sens B → A est normal ; le sens A → B perd beaucoup trop et B reçoit {dbm_fr(E11_B_RX)} dBm, sous la sensibilité de {dbm_fr(SR_SPEC.sensitivity_dbm)} dBm : d'où les erreurs CRC sur B. La fibre qui va du TX de A au RX de B a un connecteur sale ou abîmé. On coupe la lumière, on inspecte, nettoie et réinspecte ses connecteurs (jarretières et traversées, aux deux bouts) ; on contrôle que B reçoit environ −3 dBm et que les erreurs n'augmentent plus.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Choisir le module d'une liaison entre deux bâtiments",
        question_type="document_analysis",
        requirement_ids=("AP-21", "AP-22"),
        kind=KIND_CHOICE,
        context=(
            "Un lycée veut relier à 10 Gb/s deux bâtiments distants de "
            f"{fr(E12_LENGTH / 1000)} km par la fibre monomode OS2 déjà posée : deux paires de connecteurs, "
            f"{E12_SPLICES} épissures. Les switchs ont des ports SFP+. Le fournisseur propose les modules du "
            "document 1."
        ),
        documents=(
            _table(
                "Document 1 — Modules proposés (fiches fictives)",
                ("Module", "Format", "Longueur d'onde", "Fibre", "Portée", "Budget"),
                ("10GBASE-SR", "SFP+", "850 nm", "multimode", "300 m (OM3)", "—"),
                ("10GBASE-LR", "SFP+", "1 310 nm", "monomode", "10 km", f"{fr(E12_BUDGET)} dB"),
                ("1000BASE-LX", "SFP", "1 310 nm", "monomode", "5 km", "—"),
            ),
        ),
        instructions=(
            "Choisis le module en justifiant (débit, format, fibre, portée).",
            "Calcule la perte de la liaison (0,4 dB/km, 0,75 dB par paire de connecteurs, 0,3 dB par épissure) et la marge.",
        ),
        criteria=(
            _c("Choix justifié", 1.5, "10GBASE-LR : 10 Gb/s, format SFP+ des ports, monomode comme la fibre posée, portée 10 km ≥ 1,2 km ; SR exclu (multimode, 300 m), LX exclu (1 Gb/s) ; le même module aux deux extrémités."),
            _c("Bilan", 1.5, f"1,2 × 0,4 = 0,48 + 1,5 + {E12_SPLICES} × 0,3 = {fr(E12_LOSS, 2)} dB ; marge {fr(E12_BUDGET)} − {fr(E12_LOSS, 2)} = {fr(E12_MARGIN, 2)} dB ; à confirmer par une mesure."),
        ),
        correction=(
            "Il faut 10 Gb/s dans un port SFP+ : 10GBASE-SR ou 10GBASE-LR. La fibre posée est monomode : le SR (850 nm, multimode, 300 m sur OM3) est exclu. Le 10GBASE-LR (1 310 nm, monomode, 10 km) convient ; le 1000BASE-LX ne fait que 1 Gb/s. On commande deux modules LR identiques, reconnus par les switchs. La fibre isole aussi électriquement les deux bâtiments, ce qu'un câble cuivre ne ferait pas.",
            f"Perte : 1,2 km × 0,4 dB/km = 0,48 dB ; 2 × 0,75 = 1,5 dB ; {E12_SPLICES} × 0,3 = {fr(E12_SPLICES * 0.3, 1)} dB ; total {fr(E12_LOSS, 2)} dB. Marge : {fr(E12_BUDGET)} − {fr(E12_LOSS, 2)} = {fr(E12_MARGIN, 2)} dB, confortable ; on mesure la liaison au photomètre avant la mise en service.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Commander les bonnes jarretières",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_CONNECT,
        context=(
            "Pour une agence bancaire, tu prépares deux brassages optiques. Le document 1 décrit "
            "les extrémités à relier ; le document 2, les jarretières que le magasin propose. Tu "
            "dois choisir les bonnes références et expliquer pourquoi les autres ne conviennent pas."
        ),
        documents=(
            _table(
                "Document 1 — Extrémités à relier",
                ("Liaison", "Côté équipement", "Côté tiroir"),
                ("1", "Module 10GBASE-SR (LC duplex)", "Tiroir OM4, traversées LC duplex"),
                ("2", "Boîtier de l'opérateur : SC/APC, monomode", "Tiroir OS2, traversées LC/UPC"),
            ),
            _table(
                "Document 2 — Jarretières disponibles",
                ("Réf.", "Description"),
                ("J1", "LC-LC duplex, OM1, gaine orange"),
                ("J2", "LC-LC duplex, OM4, gaine aqua"),
                ("J3", "SC/UPC – LC/UPC, OS2, gaine jaune"),
                ("J4", "SC/APC – LC/UPC, OS2, gaine jaune"),
            ),
        ),
        instructions=("Choisis la jarretière de chaque liaison et justifie le rejet des deux autres.",),
        criteria=(
            _c("Liaison 1", 1.5, "J2 : LC-LC duplex, multimode OM4 comme le tiroir et le module SR ; J1 rejetée : OM1 (62,5 µm), on ne mélange pas les types de fibre."),
            _c("Liaison 2", 1.5, "J4 : SC/APC côté opérateur, LC/UPC côté tiroir, monomode ; J3 rejetée : SC/UPC face à un SC/APC (polissages différents : forte perte, faces abîmées)."),
        ),
        correction=(
            "Liaison 1 : le module SR et le tiroir sont en LC duplex et en OM4 : la jarretière J2 (LC-LC duplex, OM4, gaine aqua) convient. J1 est en OM1 : cœur de 62,5 µm au lieu de 50 µm, on ne mélange pas les types de fibre sur une même liaison (pertes et portée non garanties).",
            "Liaison 2 : le boîtier de l'opérateur est en SC/APC (vert), le tiroir en LC/UPC : il faut J4 (SC/APC – LC/UPC, OS2). J3 a un SC/UPC : un UPC face à un APC laisse un vide et un angle, d'où une forte perte et un risque d'abîmer les faces. On note les références dans le plan de brassage.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Contrôler un chantier de pose : rayons de courbure",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_CONNECT,
        context=(
            "Tu réceptionnes la pose d'un câble optique de "
            f"{E14_DIAMETER} mm de diamètre dans un hôpital de jour. Le chef de chantier a rempli le "
            "rapport du document 1. Règle du cours (la fiche du câble fait foi) : rayon de courbure "
            "minimal de 10 fois le diamètre au repos et de 20 fois pendant le tirage."
        ),
        documents=(
            _table(
                "Document 1 — Rapport de chantier",
                ("Point contrôlé", "Constat"),
                ("Tirage", "par l'élément de traction en aramide"),
                ("Rayon au coin du faux plafond, pendant le tirage", "120 mm"),
                ("Love de réserve dans le local technique (câble au repos)", "rayon 60 mm"),
                ("Attaches du chemin de câbles", "serrées à la pince, gaine marquée"),
                ("Étiquettes", "posées aux deux extrémités"),
            ),
        ),
        instructions=(
            "Calcule les rayons minimaux et dis, pour chaque point, s'il est conforme.",
            "Propose les corrections et le contrôle final.",
        ),
        criteria=(
            _c("Rayons minimaux", 1, f"Repos : 10 × {E14_DIAMETER} = {E14_REST:g} mm ; tirage : 20 × {E14_DIAMETER} = {E14_PULL:g} mm."),
            _c("Conformité", 1, f"Tirage par l'aramide et étiquettes : conformes ; coin à 120 mm < {E14_PULL:g} mm et love à 60 mm < {E14_REST:g} mm : non conformes ; attaches serrées : non conformes (écrasement)."),
            _c("Corrections et contrôle", 1, "Love refait avec un rayon ≥ 80 mm, attaches desserrées (velcro), coin repris ou contrôlé ; mesure au photomètre et au réflectomètre (courbure : perte plus forte à 1 550 nm)."),
        ),
        correction=(
            f"Rayon minimal : au repos 10 × {E14_DIAMETER} mm = {E14_REST:g} mm ; pendant le tirage 20 × {E14_DIAMETER} mm = {E14_PULL:g} mm. Le tirage par l'élément en aramide et les étiquettes aux deux bouts sont conformes. Le coin pris à 120 mm pendant le tirage est sous {E14_PULL:g} mm, la love à 60 mm sous {E14_REST:g} mm : non conformes. Les attaches serrées écrasent le câble : non conforme.",
            f"Corrections : refaire la love avec un rayon d'au moins {E14_REST:g} mm, remplacer les attaches serrées par des attaches souples non serrées. La fibre a pu souffrir au coin : on mesure chaque fibre au photomètre et au réflectomètre, à 1 310 et 1 550 nm (une courbure perd nettement plus à 1 550 nm). On consigne les mesures et les corrections.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Sécurité laser : corriger un geste dangereux",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_SAFETY,
        context=(
            "Dans le local technique d'une école, un collègue débranche une jarretière d'un "
            "switch en service et approche le connecteur de son œil « pour voir s'il y a de la "
            "lumière ». Comme il ne voit rien, il affirme que le port est éteint et qu'il peut "
            "brancher le module de son choix."
        ),
        instructions=("Explique pourquoi son geste et sa conclusion sont faux, et ce qu'il doit faire.",),
        criteria=(
            _c("Danger", 1.5, "Lumière infrarouge (850, 1 310, 1 550 nm) invisible : ne rien voir ne prouve rien ; un laser peut brûler la rétine sans douleur ; ne jamais regarder une fibre ou un connecteur, même supposé éteint."),
            _c("Bonne pratique", 1.5, "Vérifier au photomètre (ou la puissance reçue affichée) ; capuchon sur le connecteur ; inspection seulement fibre déconnectée de toute source, avec une sonde d'inspection ; module choisi selon la fibre et la liaison, pas au hasard."),
        ),
        correction=(
            "Les liaisons réseau utilisent de l'infrarouge (850, 1 310, 1 550 nm) : l'œil ne le voit pas. Ne rien voir ne prouve donc pas que le port est éteint, et un faisceau laser peut léser la rétine sans aucune sensation. On ne regarde jamais l'extrémité d'une fibre ou d'un connecteur, même si on la croit éteinte.",
            "On vérifie la présence de lumière avec un photomètre ou en lisant la puissance affichée par le module ; on pose un capuchon sur tout connecteur débranché ; on n'inspecte une face qu'avec une sonde d'inspection, fibre déconnectée de toute source. Le module se choisit selon la fibre et la liaison, jamais « au choix ».",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Éclats de fibre après un raccordement",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_SAFETY,
        context=(
            "Après une journée d'épissures dans le local technique d'une crèche, un stagiaire a "
            "laissé les chutes de fibre sur la table, à côté de son sandwich, et s'apprête à les "
            "balayer dans la corbeille avec la main. Le local doit être rendu propre le soir même."
        ),
        instructions=("Explique le risque et la bonne façon de travailler et de ranger.",),
        criteria=(
            _c("Risque", 1, "Éclats de verre très fins, presque invisibles : ils pénètrent la peau ou l'œil et s'avalent ; ne jamais manger ni boire au poste."),
            _c("Bonne pratique", 2, "Travailler sur un tapis sombre, lunettes ; chutes déposées aussitôt dans un récipient fermé et étiqueté ; ramasser au ruban adhésif, jamais à la main ni en soufflant ; se laver les mains ; local laissé propre."),
        ),
        correction=(
            "Une chute de fibre est un éclat de verre très fin, presque invisible : il pénètre la peau ou l'œil et peut être avalé avec la nourriture. On ne mange et ne boit jamais au poste d'épissure, et on ne balaie jamais les chutes à la main ni en soufflant.",
            "On travaille sur un tapis sombre (les chutes y sont visibles), avec des lunettes de protection ; chaque chute va aussitôt dans un récipient fermé et étiqueté ; on ramasse ce qui reste avec du ruban adhésif ; on se lave les mains. Le récipient est évacué selon les consignes du site.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Fibre ou cuivre pour un atelier de soudure ?",
        question_type="long_answer",
        requirement_ids=("AP-21", "AP-22"),
        kind=KIND_CHOICE,
        context=(
            "Une entreprise de constructions métalliques veut relier son atelier de soudure à ses "
            "bureaux, à 250 m, dans un autre bâtiment. Le câble passera près des postes à souder "
            "et des armoires de puissance. Le gérant propose un câble Cat6 « blindé et costaud » "
            "qu'il a en stock."
        ),
        instructions=("Compare le cuivre et la fibre pour cette liaison et fais une proposition justifiée.",),
        criteria=(
            _c("Comparaison", 2, "Cuivre : 100 m de canal au plus (250 m impossible), sensible aux parasites, relie électriquement deux bâtiments (terres différentes, foudre) ; fibre : insensible aux parasites, isolation électrique, centaines de m en multimode."),
            _c("Proposition", 1.5, "Fibre : par exemple multimode OM3/OM4 avec modules SR (300/400 m) ou SX à 1 Gb/s, ou monomode ; câble prévu pour l'extérieur ; budget et portée vérifiés."),
            _c("Limites honnêtes", 0.5, "Fibre : modules, outillage et raccordement plus chers, plus fragile (courbures, connecteurs propres), pas de PoE."),
        ),
        correction=(
            "Le Cat6 est exclu d'office : un canal cuivre est limité à 100 m, quelle que soit la catégorie ou le blindage. En plus, il relierait électriquement deux bâtiments aux terres différentes (courants de terre, foudre) et passerait près des postes à souder et des armoires de puissance, très perturbants.",
            "La fibre ne transporte que de la lumière : insensible aux parasites, sans liaison électrique entre les bâtiments, et elle tient la distance (10GBASE-SR : 300 m sur OM3, 400 m sur OM4 ; ou 1 Gb/s en 1000BASE-SX ; ou monomode pour l'avenir). On prévoit un câble d'extérieur, on vérifie portée et budget. En contrepartie : modules et raccordement plus chers, fibre plus fragile (courbures, connecteurs à garder propres), pas d'alimentation PoE.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Pigtail et épissure : expliquer le raccordement au client",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_CONNECT,
        context=(
            "Le gérant d'une imprimerie lit le devis de raccordement de sa nouvelle fibre : "
            "« 2 tiroirs optiques, 8 pigtails LC, 8 épissures par fusion, 8 protections "
            "d'épissure ». Il demande pourquoi on ne pose pas simplement un connecteur au bout de "
            "chaque fibre du câble."
        ),
        instructions=("Explique au client ce qu'est un pigtail, une épissure par fusion, et pourquoi on procède ainsi.",),
        criteria=(
            _c("Définitions", 1.5, "Pigtail : courte fibre avec un connecteur posé et poli en usine ; épissure par fusion : les deux fibres soudées bout à bout à l'arc électrique, protégées par un manchon, rangées dans une cassette du tiroir."),
            _c("Justification", 1.5, f"Connecteur d'usine fiable ; épissure de très faible perte (au plus {fr(0.3, 1)} dB, souvent bien moins), sans réflexion ; le tiroir protège les fibres et permet le brassage par jarretières."),
        ),
        correction=(
            "Un pigtail est une courte fibre munie d'un connecteur posé et poli en usine. Dans le tiroir optique, on soude chaque fibre du câble à un pigtail : c'est l'épissure par fusion (les deux fibres, clivées, sont fondues bout à bout par un arc électrique), protégée par un manchon et rangée dans une cassette.",
            "Ainsi, le connecteur a la qualité de l'usine, et l'épissure ajoute très peu de perte (0,3 dB au plus, souvent bien moins) et pas de réflexion. Le tiroir protège les fibres et les présente sur des traversées : on brasse ensuite avec des jarretières vers les switchs.",
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
        title="Liaison neuve entre deux bâtiments sans lien",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            f"Une liaison 10GBASE-LR de {X01_LENGTH} m en OS2 (2 connecteurs, 2 épissures) vient d'être "
            "installée entre l'école et sa salle de sport. Le lien ne monte pas. Le document 1 donne "
            "les puissances des modules et les mesures au photomètre de chaque fibre."
        ),
        documents=(
            _table(
                "Document 1 — Relevés",
                ("Mesure", "Valeur"),
                ("Module école : émise / reçue", "−1,9 dBm / −40,0 dBm (LOS)"),
                ("Module salle de sport : émise / reçue", "−2,2 dBm / −40,0 dBm (LOS)"),
                ("Fibre 1 au photomètre (1 310 nm)", "1,6 dB de perte"),
                ("Fibre 2 au photomètre (1 310 nm)", "1,7 dB de perte"),
            ),
        ),
        instructions=("Donne la cause la plus probable en la justifiant par les mesures, puis la correction et le contrôle.",),
        criteria=(
            _c("Diagnostic justifié", 1, f"Fibres bonnes (1,6 et 1,7 dB ≤ {fr(X01_MAX, 2)} dB admissibles), modules qui émettent, mais aucun RX ne reçoit : TX relié au TX, polarité inversée."),
            _c("Correction et contrôle", 1, "Croiser les deux fibres à une seule extrémité (clip duplex de la jarretière), puis vérifier la puissance reçue des deux côtés (vers −4 dBm) et le lien ; noter la polarité dans le dossier."),
        ),
        correction=(
            f"Les deux modules émettent normalement et chaque fibre, mesurée seule, perd 1,6 et 1,7 dB, sous la perte admissible de {fr(X01_MAX, 2)} dB (0,24 + 1,5 + 0,6). Pourtant aucun récepteur ne voit de lumière : la lumière de chaque émetteur arrive sur l'émetteur d'en face. C'est une polarité inversée.",
            "Correction : croiser les deux fibres à une seule extrémité (on ouvre le clip duplex de la jarretière et on inverse les deux LC). Contrôle : puissance reçue d'environ −4 dBm des deux côtés, lien monté, et polarité notée dans le plan de brassage.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Erreurs sur une liaison courte entre deux baies",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            f"Entre deux baies d'une salle serveur, une liaison 10GBASE-SR en OM4 de {X02_LENGTH} m "
            f"(2 connecteurs) a des erreurs depuis un rebrassage. Le module A émet {dbm_fr(X02_TX)} dBm ; le "
            f"module B reçoit {dbm_fr(X02_RX)} dBm. Fiche (fictive) : réception de {dbm_fr(SR_SPEC.sensitivity_dbm)} "
            f"à {dbm_fr(SR_SPEC.overload_dbm)} dBm. Affaiblissement : 3,5 dB/km ; 0,75 dB par paire de connecteurs."
        ),
        instructions=("Calcule la perte attendue et la perte réelle, donne la cause probable et l'intervention.",),
        criteria=(
            _c("Calculs", 1, f"Attendue ≤ {fr(X02_MAX, 2)} dB (réception vers {dbm_fr(X02_EXPECTED_RX)} dBm) ; réelle {dbm_fr(X02_TX)} − ({dbm_fr(X02_RX)}) = {fr(X02_LOSS, 1)} dB ; réception sous la sensibilité."),
            _c("Cause et intervention", 1, "Connecteur sale (rebrassage) : couper la lumière, inspecter, nettoyer, réinspecter les deux bouts de la fibre ; remesurer, vérifier que les erreurs cessent."),
        ),
        correction=(
            f"Perte admissible : {fr(X02_LENGTH / 1000, 2)} km × 3,5 + 2 × 0,75 = {fr(X02_MAX, 2)} dB ; B devrait donc recevoir environ {dbm_fr(X02_EXPECTED_RX)} dBm ou plus. Il reçoit {dbm_fr(X02_RX)} dBm : perte réelle {fr(X02_LOSS, 1)} dB, et une puissance sous la sensibilité de {dbm_fr(SR_SPEC.sensitivity_dbm)} dBm, d'où les erreurs.",
            f"Sur {X02_LENGTH} m, une telle perte vient presque toujours d'un connecteur sale ou abîmé, surtout après un rebrassage. On coupe la lumière, on inspecte, nettoie et réinspecte les connecteurs de cette fibre aux deux bouts (jarretière et traversées), puis on vérifie la puissance reçue et l'arrêt des erreurs.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Lien coupé après un échange de switch",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_CHOICE,
        context=(
            "Un technicien a remplacé le switch du siège d'une association et y a mis un module "
            "10GBASE-SR trouvé dans le stock. Le port est relié par une fibre jaune OS2 de 2 km au "
            "site distant, équipé d'un module 10GBASE-LR. Depuis, le lien ne monte plus."
        ),
        instructions=("Explique pourquoi la liaison ne peut pas fonctionner et ce qu'il faut faire.",),
        criteria=(
            _c("Explication", 1, "Deux erreurs : modules différents aux deux bouts (SR 850 nm / LR 1 310 nm) et SR multimode sur une fibre monomode OS2."),
            _c("Correction", 1, "Module 10GBASE-LR (SFP+, monomode, 10 km) aux deux extrémités, reconnu par le nouveau switch ; nettoyer, brancher, vérifier la puissance reçue et le lien."),
        ),
        correction=(
            f"La liaison cumule deux erreurs : {X03_ERRORS[0].lower()} (SR à 850 nm d'un côté, LR à 1 310 nm de l'autre) et {X03_ERRORS[1].lower()} (le SR est un module multimode, la fibre jaune est monomode OS2). Ce n'est pas un problème de câble.",
            "On remplace le module SR par un 10GBASE-LR (SFP+, 1 310 nm, monomode, 10 km), identique à celui du site distant et reconnu par le nouveau switch. On nettoie et inspecte les connecteurs, on branche, puis on vérifie la puissance reçue des deux côtés et le lien.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="10 Gb/s sur une ancienne fibre OM2",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_CHOICE,
        context=(
            "Une entreprise de logistique veut passer à 10 Gb/s la liaison entre son entrepôt et "
            f"ses bureaux : {X04_LENGTH} m de fibre multimode OM2 existante, deux connecteurs. Un "
            "collègue a calculé une perte faible et a commandé deux modules 10GBASE-SR. Après "
            "installation, le lien est instable et compte de nombreuses erreurs."
        ),
        instructions=("Explique le problème et propose deux solutions.",),
        criteria=(
            _c("Explication", 1, f"Perte faible ({fr(X04_LOSS, 2)} dB) mais portée de 10GBASE-SR sur OM2 limitée à {REACH_M[('10GBASE-SR', 'OM2')]} m (dispersion modale) : {X04_LENGTH} m dépassent la portée."),
            _c("Solutions", 1, f"Fibre OM3 ({REACH_M[('10GBASE-SR', 'OM3')]} m) ou OM4 ({REACH_M[('10GBASE-SR', 'OM4')]} m) avec les modules SR, ou monomode OS2 avec 10GBASE-LR ; ou rester à 1 Gb/s (1000BASE-SX, 550 m sur OM2)."),
        ),
        correction=(
            f"La perte est faible ({X04_LENGTH / 1000:g} km × 3,5 + 1,5 = {fr(X04_LOSS, 2)} dB), mais un bilan de pertes ne suffit pas : en multimode, la dispersion modale limite la portée. 10GBASE-SR ne tient que {REACH_M[('10GBASE-SR', 'OM2')]} m sur OM2 ; à {X04_LENGTH} m, le lien est instable.",
            f"Solutions : tirer une fibre OM3 (portée {REACH_M[('10GBASE-SR', 'OM3')]} m) ou OM4 ({REACH_M[('10GBASE-SR', 'OM4')]} m) et garder les modules SR ; ou tirer une monomode OS2 avec des modules 10GBASE-LR ; ou rester à 1 Gb/s sur l'OM2 avec 1000BASE-SX (550 m).",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Localiser une cassure",
        question_type="document_analysis",
        requirement_ids=("AP-21",),
        kind=KIND_DIAG,
        context=(
            "Après un élagage, la liaison optique entre la ferme d'un domaine et sa boutique ne "
            f"fonctionne plus. Elle mesure {X05_LINK} m entre les deux tiroirs. Le document 1 résume la "
            f"trace OTDR prise depuis la ferme, avec une bobine amorce de {X05_LAUNCH} m."
        ),
        documents=(
            _table(
                "Document 1 — Trace OTDR depuis la ferme (1 550 nm)",
                ("Position", "Événement"),
                (f"{X05_LAUNCH} m", "pic de réflexion, perte 0,3 dB, la trace continue"),
                (f"{X05_END} m", "grand pic de réflexion, puis plus que du bruit"),
            ),
        ),
        instructions=("Dis où se trouve le défaut depuis le tiroir de la ferme, en justifiant, puis ce que tu fais.",),
        criteria=(
            _c("Position justifiée", 1, f"Pic à {X05_LAUNCH} m = connecteur du tiroir (début de la liaison) ; fin à {X05_END} m avant {X05_LAUNCH + X05_LINK} m → cassure à {X05_END} − {X05_LAUNCH} = {X05_BREAK:g} m de fibre depuis le tiroir."),
            _c("Intervention", 1, "Chercher sur le parcours (zone d'élagage), réparer par deux épissures par fusion en boîtier ou remplacer le tronçon ; remesurer, mettre à jour budget et dossier."),
        ),
        correction=(
            f"Le pic à {X05_LAUNCH} m est le connecteur du tiroir de la ferme, après la bobine amorce : c'est le début de la liaison. À {X05_END} m, la trace tombe dans le bruit, alors que la liaison devrait finir à {X05_LAUNCH + X05_LINK} m : c'est une cassure, à {X05_END} − {X05_LAUNCH} = {X05_BREAK:g} m de fibre du tiroir.",
            "On cherche le défaut sur le parcours à cette longueur (réserves comprises), sans doute dans la zone de l'élagage ; on répare par deux épissures par fusion dans un boîtier étanche, ou on remplace le tronçon. On remesure au photomètre et au réflectomètre, et on met à jour le budget et le dossier.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Recette d'une liaison multimode au photomètre",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_MEASURE,
        context=(
            "Tu réceptionnes une liaison OM3 de 240 m (2 paires de connecteurs, 1 épissure) dans un "
            "centre culturel. Avec la source à 850 nm et le cordon de référence, le photomètre lit "
            f"{dbm_fr(X06_REF)} dBm ; au bout de la liaison, il lit {dbm_fr(X06_READ)} dBm. Valeurs : 3,5 dB/km, "
            "0,75 dB par paire de connecteurs, 0,3 dB par épissure."
        ),
        instructions=("Calcule la perte mesurée et la perte admissible, conclus et dis quoi faire.",),
        criteria=(
            _c("Calculs", 1, f"Mesurée : {dbm_fr(X06_REF)} − ({dbm_fr(X06_READ)}) = {fr(X06_LOSS, 2)} dB ; admissible : 0,24 × 3,5 + 1,5 + 0,3 = {fr(X06_MAX, 2)} dB."),
            _c("Conclusion et action", 1, f"Non conforme ({fr(X06_LOSS - X06_MAX, 2)} dB de trop) : inspecter et nettoyer les connecteurs, remesurer ; si la perte reste, réflectomètre pour localiser (épissure, courbure) ; ne pas réceptionner avant."),
        ),
        correction=(
            f"Perte mesurée = référence − lecture = {dbm_fr(X06_REF)} − ({dbm_fr(X06_READ)}) = {fr(X06_LOSS, 2)} dB. Perte admissible : 0,24 km × 3,5 dB/km = 0,84 dB ; 2 × 0,75 = 1,5 dB ; 1 × 0,3 dB ; total {fr(X06_MAX, 2)} dB.",
            f"La liaison dépasse de {fr(X06_LOSS - X06_MAX, 2)} dB : non conforme. On inspecte et nettoie les connecteurs, on remesure ; si la perte reste trop forte, le réflectomètre localise l'élément fautif (épissure ratée, courbure, connecteur abîmé). On ne réceptionne pas avant une mesure conforme.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Rangement d'un câble dans le local technique",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_CONNECT,
        context=(
            f"Dans le local technique d'une pharmacie, un câble optique de {X07_DIAMETER} mm a été tiré "
            "avec un rayon de 150 mm au passage le plus serré. Au repos, sa réserve a été enroulée "
            "en petites boucles de 40 mm de rayon, serrées par des colliers. Règle du cours : 10 × "
            "le diamètre au repos, 20 × pendant le tirage ; la fiche du câble fait foi."
        ),
        instructions=("Vérifie les deux rayons, dis ce qui ne va pas et ce que tu fais.",),
        criteria=(
            _c("Vérification", 1, f"Tirage : 20 × {X07_DIAMETER} = {X07_PULL:g} mm ≤ 150 mm → conforme ; repos : 10 × {X07_DIAMETER} = {X07_REST:g} mm > 40 mm → non conforme ; colliers serrés : écrasement."),
            _c("Action", 1, f"Refaire la réserve (rayon ≥ {X07_REST:g} mm), attaches souples non serrées, puis mesurer (photomètre, OTDR à 1 550 nm où une courbure perd plus) et consigner."),
        ),
        correction=(
            f"Pendant le tirage, le rayon minimal est 20 × {X07_DIAMETER} = {X07_PULL:g} mm : 150 mm conviennent. Au repos, il faut 10 × {X07_DIAMETER} = {X07_REST:g} mm : les boucles de 40 mm sont trop serrées et les colliers écrasent le câble ; la fibre perd de la lumière et peut se fissurer avec le temps.",
            f"On refait la réserve en grandes boucles (rayon d'au moins {X07_REST:g} mm), maintenues par des attaches souples non serrées, puis on mesure chaque fibre (photomètre ; au réflectomètre, une courbure perd nettement plus à 1 550 nm qu'à 1 310 nm) et on consigne.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Règles de sécurité pour une intervention sur fibre",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_SAFETY,
        context=(
            "Tu encadres un stagiaire pour une journée de raccordements optiques dans un immeuble "
            "de bureaux occupé : débranchement de jarretières sur des switchs en service, puis "
            "préparation et soudure de fibres dans les tiroirs. Le responsable veut une consigne "
            "écrite avant de commencer."
        ),
        instructions=("Rédige les règles de sécurité essentielles : lumière laser et éclats de fibre.",),
        criteria=(
            _c("Laser", 1, "Ne jamais regarder une fibre ou un connecteur (infrarouge invisible) ; vérifier l'absence de lumière au photomètre ; capuchons ; sonde d'inspection seulement fibre déconnectée."),
            _c("Éclats", 1, "Tapis sombre, lunettes ; chutes dans un récipient fermé et étiqueté ; ruban adhésif, jamais la main ; ni manger ni boire ; se laver les mains."),
        ),
        correction=(
            "Laser : la lumière des liaisons (850, 1 310, 1 550 nm) est invisible ; on ne regarde jamais l'extrémité d'une fibre ou d'un connecteur, même supposée éteinte ; on vérifie au photomètre, on met un capuchon sur tout connecteur libre, on n'inspecte une face qu'avec une sonde d'inspection, fibre déconnectée.",
            "Éclats : on travaille sur un tapis sombre, avec des lunettes ; chaque chute va aussitôt dans un récipient fermé et étiqueté ; on ramasse au ruban adhésif, jamais à la main ; on ne mange et ne boit pas au poste ; on se lave les mains en fin de travail.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Relier le service d'imagerie d'un hôpital",
        question_type="long_answer",
        requirement_ids=("AP-21", "AP-22"),
        kind=KIND_CHOICE,
        context=(
            "Un hôpital veut relier à 10 Gb/s le service d'imagerie (IRM, scanner) au bâtiment "
            "principal, à 180 m. Le service technique propose un câble cuivre Cat6A blindé « pour "
            "économiser les modules optiques ». Le câble passerait dans une gaine enterrée entre "
            "les deux bâtiments."
        ),
        instructions=("Compare cuivre et fibre pour cette liaison et propose un support et des modules, en justifiant.",),
        criteria=(
            _c("Comparaison", 1, "Cuivre : canal ≤ 100 m (180 m impossible), relie électriquement deux bâtiments, sensible aux fortes perturbations ; fibre : distance, isolation électrique, insensible aux parasites ; plus chère et plus fragile."),
            _c("Proposition", 1, f"Fibre, par exemple {X09_MEDIUM} (portée 300 m), ou OM4 / monomode OS2 avec 10GBASE-LR ; câble d'extérieur ; mêmes modules aux deux bouts, budget vérifié et mesuré."),
        ),
        correction=(
            "Le Cat6A est exclu : un canal cuivre ne dépasse pas 100 m, il relierait électriquement deux bâtiments (terres différentes, foudre) et passerait près d'équipements très perturbants. La fibre tient la distance, isole électriquement et ignore les parasites ; elle coûte plus cher en modules et en raccordement et demande des connecteurs propres.",
            f"Proposition : {X09_MEDIUM} (portée 300 m sur OM3, 180 m conviennent), ou OM4, ou monomode OS2 avec 10GBASE-LR si l'on veut de la réserve ; câble prévu pour l'extérieur ; mêmes modules aux deux bouts ; budget calculé puis mesuré à la recette.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Un module longue portée sur une liaison courte",
        question_type="short_answer",
        requirement_ids=("AP-21",),
        kind=KIND_MEASURE,
        context=(
            "Pour un essai en atelier, un technicien relie deux switchs par une jarretière de 3 m "
            "avec des modules longue portée trouvés en stock. Fiche (fictive) : émission "
            f"{dbm_fr(X10_TX)} dBm, réception de {dbm_fr(X10_SPEC.sensitivity_dbm)} à {dbm_fr(X10_SPEC.overload_dbm)} dBm. "
            f"La perte totale de la jarretière et des connecteurs est de {fr(X10_LOSS)} dB."
        ),
        instructions=("Calcule la puissance reçue, conclus et propose une solution chiffrée.",),
        criteria=(
            _c("Calcul et conclusion", 1, f"{dbm_fr(X10_TX)} − {fr(X10_LOSS)} = {dbm_fr(X10_RX)} dBm > {dbm_fr(X10_SPEC.overload_dbm)} dBm : saturation du récepteur (erreurs, risque d'abîmer le récepteur)."),
            _c("Solution", 1, f"Atténuateur d'au moins {fr(X10_MIN_ATT)} dB, par exemple {fr(X10_ATT, 0)} dB → {dbm_fr(X10_RX_AFTER)} dBm, dans la plage ; ou modules adaptés à la courte distance (SR/LR selon la fibre)."),
        ),
        correction=(
            f"Puissance reçue = émise − perte = {dbm_fr(X10_TX)} − {fr(X10_LOSS)} = {dbm_fr(X10_RX)} dBm. C'est au-dessus du maximum de {dbm_fr(X10_SPEC.overload_dbm)} dBm : le récepteur sature (erreurs, et risque de l'abîmer).",
            f"Il faut au moins {fr(X10_MIN_ATT)} dB d'atténuation : un atténuateur de {fr(X10_ATT, 0)} dB donne {dbm_fr(X10_RX_AFTER)} dBm, dans la plage de la fiche. Mieux : utiliser des modules prévus pour une courte distance, adaptés à la fibre.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, cohérence des données chiffrées des corrigés."""
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
    if [v for v in E09_VERDICTS.values()].count("Conforme") != 3:
        errors.append("E09 : trois fibres conformes et une non conforme attendues.")
    if rx_status(E11_B_RX, SR_SPEC) == rx_status(E11_A_RX, SR_SPEC):
        errors.append("E11 : un seul sens doit être hors plage.")
    if rx_status(X10_RX, X10_SPEC) != "Trop forte : saturation du récepteur" or rx_status(X10_RX_AFTER, X10_SPEC) != "Dans la plage de la fiche":
        errors.append("X10 : saturation puis plage correcte attendues.")
    return errors

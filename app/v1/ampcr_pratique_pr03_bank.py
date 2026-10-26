"""PR03 « Montage et démontage d'un PC — procédure écrite » — exercices corrigés et
mini-examen (ticket #204).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — ordonnancement (remises en ordre), repérage d'erreurs, justification
  de l'ordre et des précautions, premier démarrage et procédures écrites ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, fiches et relevés sont **fictifs** ; les procédures, le brochage de façade, les
entretoises et les relevés viennent de `app.v1.ampcr_pratique_pr03_figures` (mêmes données que
les schémas). Aucune manipulation sous tension ni ouverture de bloc d'alimentation n'est
demandée.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr03_figures import (
    CASE3_EXPECTED,
    CPU_STEPS,
    E07_BOARD_HOLES,
    E07_STANDOFFS,
    FRONT_PANEL_BY_NUMBER,
    PREP_STEPS,
    Inventory,
    inventory_gaps,
    panel_pins_for,
    standoff_problems,
    temperature_verdict,
    uefi_lines,
)
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)

PR03_CODE = "PR03"

KIND_ORDER = "ordonnancement"
KIND_ERROR = "repérage d'erreurs"
KIND_JUSTIFY = "justification"
KIND_BOOT = "premier démarrage"
KIND_PROCEDURE = "procédure écrite"

# Exigence officielle du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-14"})


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _shuffled_ordering(steps: tuple[str, ...], shown: tuple[int, ...]) -> Ordering:
    """`shown` = ordre d'affichage (indices dans `steps`, la bonne suite) ; renvoie l'ordre
    attendu exprimé en positions d'affichage, comme le type « ordering » le demande."""
    displayed = tuple(steps[i] for i in shown)
    correct = tuple(shown.index(i) for i in range(len(steps)))
    return Ordering(steps=displayed, correct=correct)


def _labels(steps: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    return tuple(f"{label} — {detail}" for label, detail in steps)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(PREP_STEPS)
E02_STEPS = (
    "Installer le processeur dans le socket, carte mère posée sur son carton.",
    "Insérer les barrettes de mémoire et visser le SSD M.2.",
    "Appliquer la pâte thermique et fixer le ventirad, câble sur CPU_FAN.",
    "Préparer le boîtier (entretoises en face des trous, plaque d'E/S), y poser et visser la carte mère.",
    "Installer le bloc d'alimentation et les disques SATA.",
    "Insérer la carte graphique dans le premier emplacement PCIe x16 et visser l'équerre.",
    "Brancher les câbles d'alimentation, de façade et de données, puis les ranger.",
)
E03_STEPS = _labels(CPU_STEPS)
E04_STEPS = (
    "Faire signer l'autorisation et vérifier la sauvegarde, relever l'état initial.",
    "Arrêter le PC, interrupteur du bloc sur 0, débrancher le secteur, appuyer sur le bouton.",
    "Mettre le bracelet antistatique relié au châssis et photographier les branchements.",
    "Débrancher le câble PCIe en appuyant sur son loquet.",
    "Dévisser l'équerre, ouvrir le clip de l'emplacement et sortir la carte à la verticale.",
    "Installer la nouvelle carte, clip enclenché, équerre vissée, câble PCIe branché à fond.",
    "Rebrancher le secteur, démarrer et vérifier l'image, le pilote et les températures en charge.",
)

E07_EXTRA, E07_MISSING = standoff_problems(E07_BOARD_HOLES, E07_STANDOFFS)

POWER_PINS = panel_pins_for("bouton Power")  # (6, 8)
RESET_PINS = panel_pins_for("bouton Reset")  # (5, 7)
PLED_PINS = panel_pins_for("LED alimentation")  # (2, 4)
HDD_PINS = panel_pins_for("LED disque")  # (1, 3)

E11_DETECTED = Inventory(
    cpu=CASE3_EXPECTED.cpu, memory_gb=16, memory_modules=1, drives=("Disque SATA 2 To (SATA 1)",),
    cpu_fan_rpm=1150,
)
E11_SCREEN = uefi_lines(E11_DETECTED, slots=(("DIMM_A2", "vide"), ("DIMM_B2", "16 Go DDR5-4800")), temp_c=38)
E11_GAPS = inventory_gaps(CASE3_EXPECTED, E11_DETECTED)  # mémoire, stockage

E13_LIMIT = 100
E13_TEMPS = (("Repos", 61), ("Charge, 1 min", 89), ("Charge, 3 min", 100))
E13_VERDICTS = tuple(temperature_verdict(t, E13_LIMIT) for _m, t in E13_TEMPS)

E05_CATEGORIES = ("Bonne pratique", "Erreur à corriger")
E06_CATEGORIES = (
    "Contrôle visuel, PC débranché",
    "Lecture dans l'UEFI au premier démarrage",
    "Test sous le système installé",
)


def _pins(pins: tuple[int, ...]) -> str:
    return " et ".join(str(p) for p in pins)


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la préparation d'une intervention",
        question_type="ordering",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Une cliente dépose son PC de bureau à l'atelier pour l'ajout d'un second disque. Tu "
            "rédiges la préparation de l'intervention pour un stagiaire, avant qu'il n'ouvre le "
            "boîtier. Ses notes contiennent les bonnes étapes, mais dans le désordre."
        ),
        instructions=("Remets les six étapes de préparation dans l'ordre d'une intervention professionnelle.",),
        criteria=(
            _c("Ordre", 3, "Autoriser (fiche, sauvegarde) → relever l'état initial → couper et débrancher → installer le poste → se protéger (bracelet) → photographier l'intérieur."),
        ),
        correction=(
            "1. Autoriser : la fiche d'intervention est signée et la sauvegarde faite (ou le refus noté) avant tout geste. 2. Relever l'état initial : photos de l'extérieur, numéro de série, défauts visibles — on prouve l'état dans lequel le PC est arrivé.",
            "3. Couper : arrêt du système, interrupteur sur 0, câble secteur débranché, appui sur le bouton pour décharger. 4. Installer le poste (table dégagée, tapis antistatique, bac à vis). 5. Se protéger : bracelet relié au châssis. 6. Documenter : photographier l'intérieur et chaque branchement avant de débrancher.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (4, 2, 0, 5, 3, 1)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le montage complet d'un PC",
        question_type="ordering",
        requirement_ids=("AP-14",),
        kind=KIND_ORDER,
        context=(
            "Tu dois monter un PC de bureau à partir de pièces neuves déjà vérifiées compatibles : "
            "carte mère ATX, processeur, deux barrettes, SSD M.2, disque SATA, carte graphique, "
            "bloc d'alimentation et boîtier ATX. Le poste est prêt, le bracelet en place. Les "
            "étapes de ta fiche de montage ont été mélangées."
        ),
        instructions=("Remets les sept étapes du montage dans l'ordre recommandé par la procédure 2 du cours.",),
        criteria=(
            _c("Ordre", 3, "Processeur → mémoire et M.2 → pâte et ventirad → boîtier préparé et carte mère vissée → bloc et disques → carte graphique → câbles."),
        ),
        correction=(
            "On équipe d'abord la carte mère hors du boîtier, sur son carton : processeur, mémoire et SSD M.2 (accès facile, pas de risque de heurter le socket), puis la pâte et le ventirad. On prépare ensuite le boîtier (entretoises en face des trous, plaque d'E/S) et on y visse la carte.",
            "Viennent le bloc d'alimentation et les disques, puis la carte graphique, installée tard car elle masque les connecteurs et les emplacements voisins. Le câblage termine le montage, suivi du contrôle visuel et du premier démarrage.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (5, 2, 0, 3, 6, 1, 4)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'installation du processeur et du ventirad",
        question_type="ordering",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Un client t'apporte une carte mère à socket LGA (les broches sont sur la carte) et "
            "son processeur neuf, avec un ventirad à vis. La carte est posée sur son carton, tu "
            "portes le bracelet antistatique. Le stagiaire a écrit les étapes sur des cartes "
            "qui sont tombées dans le désordre."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Ouvrir le socket → orienter (triangle) → poser à la verticale → verrouiller → pâte thermique → ventirad (film retiré, serrage en croix) → câble sur CPU_FAN."),
        ),
        correction=(
            "1. Ouvrir le levier et le cadre ; le capot de protection reste en place pour protéger les broches. 2. Orienter : triangle doré du processeur sur le repère du socket, encoches alignées. 3. Poser le processeur à la verticale, sans glisser. 4. Fermer le cadre et le levier : le capot sort seul ; on le garde.",
            "5. Déposer une petite noisette de pâte au centre. 6. Retirer le film de la semelle du ventirad, le poser à plat et serrer en croix, progressivement. 7. Brancher le ventilateur sur CPU_FAN, câble éloigné des pales.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (4, 1, 6, 0, 3, 5, 2)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le remplacement d'une carte graphique",
        question_type="ordering",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Un client t'a confié son PC pour remplacer sa carte graphique par un modèle plus "
            "récent, déjà vérifié compatible (longueur, alimentation, connecteurs du bloc). Tu "
            "rédiges la procédure de démontage et remontage ; les étapes sont mélangées."
        ),
        instructions=("Remets les sept étapes dans l'ordre d'une intervention sûre et documentée.",),
        criteria=(
            _c("Ordre", 3, "Autorisation, sauvegarde et état initial → mise hors tension → bracelet et photos → débrancher le PCIe → dévisser, ouvrir le clip, sortir la carte → installer la nouvelle → démarrer et vérifier."),
        ),
        correction=(
            "On commence par l'autorisation, la sauvegarde et l'état initial, puis la mise hors tension complète (secteur débranché, bouton appuyé) et la protection antistatique, avec des photos des branchements. On débranche le câble PCIe en appuyant sur son loquet, on dévisse l'équerre et on ouvre le clip de l'emplacement avant de sortir la carte à la verticale.",
            "La nouvelle carte est clipsée, vissée et alimentée à fond. Le test final vérifie l'image, le pilote et les températures en charge, puis le compte rendu est rédigé.",
        ),
        ordering=_shuffled_ordering(E04_STEPS, (3, 6, 1, 5, 0, 4, 2)),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Bonnes pratiques ou erreurs pendant un montage",
        question_type="classification",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ERROR,
        context=(
            "Tu relis le journal de montage d'un stagiaire qui vient d'assembler un PC de bureau "
            "pour un client. Avant la mise en service, tu veux savoir quels gestes étaient "
            "corrects et lesquels doivent être corrigés ou ne plus jamais être faits."
        ),
        instructions=("Classe chacun des huit gestes relevés : bonne pratique ou erreur à corriger.",),
        criteria=(
            _c("Classement", 4, "Bonnes pratiques : carte posée sur son carton, film du ventirad retiré, serrage en croix, appui sur le loquet avant de débrancher. Erreurs : processeur poussé pour qu'il entre, pâte étalée au doigt en grande quantité, entretoises d'usine laissées sans vérifier, bloc d'alimentation ouvert pour voir le ventilateur (0,5 pt par élément)."),
        ),
        correction=(
            "Bonnes pratiques : poser la carte mère sur son carton, retirer le film de protection de la semelle du ventirad, serrer le ventirad en croix et progressivement, appuyer sur le loquet d'un connecteur avant de le tirer.",
            "Erreurs : un processeur ne se pousse jamais (il se pose ; s'il n'entre pas, l'orientation est fausse et les broches risquent d'être tordues) ; trop de pâte déborde et isole moins bien qu'une fine couche, et le doigt la salit ; chaque entretoise doit être en face d'un trou de la carte ; un bloc d'alimentation ne s'ouvre jamais (condensateurs chargés).",
        ),
        classification=Classification(
            categories=E05_CATEGORIES,
            elements=(
                "Carte mère posée sur son carton pour installer le processeur",
                "Processeur poussé un peu pour qu'il entre dans le socket",
                "Film de protection retiré de la semelle du ventirad",
                "Pâte thermique étalée au doigt sur tout le processeur, en couche épaisse",
                "Vis du ventirad serrées en croix, progressivement",
                "Entretoises montées en usine laissées sans comparer aux trous de la carte",
                "Loquet de l'ATX 24 enfoncé avant de tirer sur le connecteur",
                "Bloc d'alimentation ouvert pour vérifier son ventilateur",
            ),
            correct=(0, 1, 0, 1, 0, 1, 0, 1),
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Classer les vérifications d'après le moment où on les fait",
        question_type="classification",
        requirement_ids=("AP-14",),
        kind=KIND_BOOT,
        context=(
            "Tu prépares la fiche de contrôle d'un atelier qui monte des PC de bureau. Chaque "
            "vérification doit être faite au bon moment : certaines PC débranché, avant la "
            "première mise sous tension ; d'autres dans l'UEFI au premier démarrage ; d'autres "
            "une fois le système installé."
        ),
        instructions=("Range chacune des sept vérifications dans le moment où on la fait.",),
        criteria=(
            _c("Classement", 3.5, "PC débranché : aucune vis libre, câble loin des pales, clips des barrettes. UEFI : mémoire totale détectée, température et ventilateur CPU, disques reconnus. Système : test mémoire de plusieurs passes et état SMART (0,5 pt par élément)."),
        ),
        correction=(
            "Avant la première mise sous tension, PC débranché : on cherche ce qui se voit — vis ou entretoise libre, câble près d'un ventilateur, barrettes mal clipsées. Dans l'UEFI : ce que le firmware détecte — mémoire totale, disques, température et vitesse du ventilateur du processeur.",
            "Une fois le système installé (ou depuis une clé de test) : les tests longs, comme un test mémoire en plusieurs passes et la lecture de l'état SMART des disques avec un utilitaire.",
        ),
        classification=Classification(
            categories=E06_CATEGORIES,
            elements=(
                "Aucune vis ni entretoise libre dans le boîtier",
                "Mémoire totale égale à la somme des barrettes",
                "Aucun câble ne touche les pales d'un ventilateur",
                "Disques reconnus dans la liste de stockage",
                "Test mémoire en plusieurs passes sans erreur",
                "État SMART des disques lu avec un utilitaire",
                "Température du processeur et vitesse de CPU_FAN",
            ),
            correct=(0, 1, 0, 1, 2, 2, 1),
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Repérer les entretoises mal placées",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_ERROR,
        context=(
            "Un stagiaire installe une carte mère microATX dans un boîtier ATX. Le boîtier avait "
            "des entretoises montées en usine ; il en a ajouté ou retiré certaines. Avant qu'il "
            "ne visse la carte, tu compares les trous de la carte et les entretoises présentes "
            "(document 1, emplacements A à L du fond du boîtier)."
        ),
        documents=(
            _table(
                "Document 1 — Relevé des emplacements (plan fictif)",
                ("Emplacement", "Trou dans la carte en face ?", "Entretoise vissée ?"),
                *(
                    (key, "oui" if key in E07_BOARD_HOLES else "non", "oui" if key in E07_STANDOFFS else "non")
                    for key in "ABCDEFGHIJKL"
                ),
            ),
        ),
        instructions=(
            "Indique les emplacements où il y a une entretoise en trop et ceux où il en manque une.",
            "Explique le risque de chaque erreur.",
            "Indique la correction avant de visser la carte.",
        ),
        criteria=(
            _c("En trop", 1, f"Entretoises sans trou : {', '.join(E07_EXTRA)}."),
            _c("Manquante", 0.5, f"Trou sans entretoise : {', '.join(E07_MISSING)}."),
            _c("Risques", 1.5, "En trop : l'entretoise métallique touche le circuit au dos de la carte → court-circuit, PC qui ne démarre pas ou s'arrête, carte abîmée. Manquante : carte qui fléchit quand on branche un connecteur ou une barrette, contraintes sur les soudures."),
            _c("Correction", 1, "Retirer les entretoises en trop, ajouter celle qui manque, présenter la carte pour vérifier chaque trou, puis visser sans forcer."),
        ),
        correction=(
            f"Entretoises en trop (aucun trou en face) : {', '.join(E07_EXTRA)}. Entretoise manquante (trou sans support) : {', '.join(E07_MISSING)}. Les entretoises J, K et L sont celles d'une carte ATX plus haute : une carte microATX est moins longue.",
            "Une entretoise en trop touche le dos de la carte, où passent des pistes : court-circuit possible, PC qui ne démarre pas ou s'éteint aussitôt. Une entretoise manquante laisse la carte fléchir à l'insertion d'une barrette ou d'un connecteur. Correction : retirer B, J, K et L, ajouter E, présenter la carte et vérifier chaque trou, puis visser sans forcer.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Corriger un câblage de façade",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_ERROR,
        context=(
            "Après un montage, rien ne se passe quand on appuie sur le bouton Power du boîtier, "
            "ni sur Reset ; la LED d'alimentation de la façade reste éteinte. L'ATX 24 et l'EPS "
            "sont branchés et le bloc est sous tension. Le manuel de la carte suit la "
            "disposition Intel du cours (document 1) ; le relevé du stagiaire est en document 2."
        ),
        documents=(
            _table(
                "Document 1 — Connecteur de façade d'après le manuel (disposition Intel)",
                ("Broche", "Signal"),
                *((str(n), FRONT_PANEL_BY_NUMBER[n].signal) for n in range(1, 11)),
            ),
            _table(
                "Document 2 — Relevé du stagiaire",
                ("Câble du boîtier", "Branché sur les broches"),
                ("POWER SW", _pins(RESET_PINS)),
                ("RESET SW", "non branché"),
                ("POWER LED + (fil de couleur)", str(PLED_PINS[1])),
                ("POWER LED − (fil blanc ou noir)", str(PLED_PINS[0])),
                ("HDD LED", f"{_pins(HDD_PINS)}, fil de couleur sur 1"),
            ),
        ),
        instructions=(
            "Explique pourquoi le PC ne démarre pas et pourquoi la LED reste éteinte.",
            "Indique le branchement correct des câbles POWER SW, RESET SW et POWER LED.",
            "Dis si l'erreur a pu endommager quelque chose.",
        ),
        criteria=(
            _c("Démarrage", 1, f"POWER SW est sur les broches Reset ({_pins(RESET_PINS)}) : l'appui ne relie pas PWR_SW à la masse, le PC ne démarre pas."),
            _c("LED", 1, "Câble de LED inversé : + sur la broche −, la LED (polarisée) ne s'allume pas."),
            _c("Correction", 1.5, f"POWER SW sur {_pins(POWER_PINS)} (sens indifférent) ; RESET SW sur {_pins(RESET_PINS)} ; POWER LED + sur {PLED_PINS[0]}, − sur {PLED_PINS[1]} ; HDD LED inchangé (correct)."),
            _c("Dégâts", 0.5, "Aucun : une LED inversée ne conduit pas, un bouton n'est qu'un contact ; on corrige PC débranché."),
        ),
        correction=(
            f"Le câble POWER SW est branché sur les broches {_pins(RESET_PINS)}, celles du Reset : l'appui sur Power ne fait rien, et Reset n'est pas branché. La LED d'alimentation est polarisée : son fil + est sur la broche {PLED_PINS[1]} (PLED−), elle ne peut pas s'allumer.",
            f"Correction, PC débranché : POWER SW sur {_pins(POWER_PINS)}, RESET SW sur {_pins(RESET_PINS)} (boutons non polarisés, sens indifférent), POWER LED + sur {PLED_PINS[0]} et − sur {PLED_PINS[1]}. Le HDD LED est correct. Rien n'est endommagé : une LED inversée ne conduit pas et un bouton n'est qu'un contact. Toujours vérifier le schéma du manuel de la carte, qui fait foi.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Rédiger la fiche avant un démontage chez un client",
        question_type="long_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_PROCEDURE,
        context=(
            "Une petite entreprise te demande de remplacer le ventirad bruyant du PC de sa "
            "comptable. Le PC contient la comptabilité de l'année ; la comptable n'est pas "
            "certaine que la dernière sauvegarde soit récente. Tu interviens sur place, sur un "
            "bureau encombré, et tu dois rédiger ce que tu fais avant d'ouvrir le boîtier."
        ),
        instructions=(
            "Rédige les actions à mener avant de démonter, dans l'ordre, en justifiant chacune.",
            "Indique ce que tu notes sur la fiche d'intervention.",
        ),
        criteria=(
            _c("Données et accord", 1.5, "Vérifier ou faire faire une sauvegarde (copie contrôlée) ; obtenir l'accord écrit du responsable ; noter un éventuel refus."),
            _c("État initial", 1, "Photos de l'extérieur, numéro de série, défauts existants, ce qui fonctionne avant l'intervention."),
            _c("Sécurité", 1, "Arrêt, interrupteur sur 0, secteur débranché, bouton appuyé ; bracelet antistatique ; poste dégagé et tapis."),
            _c("Fiche", 0.5, "Date, client, matériel, demande, autorisation, état initial, actions prévues."),
        ),
        correction=(
            "1. Données : vérifier que la sauvegarde existe et se relit, sinon la faire avant toute intervention — un démontage peut toujours mal se passer. 2. Accord : faire signer la demande et l'autorisation d'ouvrir le PC par le responsable ; noter tout refus de sauvegarde. 3. État initial : photos, numéro de série, défauts visibles, ce qui fonctionne avant (pour prouver qu'on n'a rien dégradé).",
            "4. Mise hors tension : arrêt du système, interrupteur sur 0, câble secteur débranché, bouton appuyé. 5. Poste : surface dégagée et éclairée, tapis antistatique, bac à vis ; bracelet relié au châssis ; photos de l'intérieur. La fiche porte date, client, matériel et numéro de série, demande, autorisation, sauvegarde, état initial et actions prévues.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Contrôle visuel : trouver ce qui empêche la mise sous tension",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_ERROR,
        context=(
            "Un PC vient d'être monté. Avant de le brancher au secteur, tu fais le contrôle "
            "visuel de l'atelier. Le document 1 reprend tes observations, boîtier ouvert, PC "
            "débranché. Le bon de montage prévoit une carte graphique avec deux connecteurs "
            "PCIe 8 broches."
        ),
        documents=(
            _table(
                "Document 1 — Observations du contrôle visuel",
                ("Élément", "Observation"),
                ("Carte mère", "Vissée ; une vis libre roule au fond du boîtier"),
                ("Ventirad", "Posé à plat ; film plastique transparent visible sous la semelle"),
                ("Mémoire", "Deux barrettes, clips fermés"),
                ("Carte graphique", "Clip enclenché ; un seul des deux PCIe 8 broches branché"),
                ("Alimentation", "ATX 24 clipsé ; EPS 8 broches non branché"),
                ("Câbles", "Câble du ventilateur arrière passé contre les pales du ventirad"),
            ),
        ),
        instructions=(
            "Relève chaque anomalie et la conséquence prévisible si l'on démarrait ainsi.",
            "Indique la correction de chacune.",
        ),
        criteria=(
            _c("Anomalies", 2.5, "Vis libre (court-circuit) ; film du ventirad (surchauffe) ; second PCIe manquant (carte qui refuse de démarrer ou instable) ; EPS absent (pas de démarrage ou arrêt immédiat) ; câble dans les pales (blocage, bruit, câble coupé) — 0,5 pt chacune."),
            _c("Corrections", 1.5, "Retirer la vis ; retirer le film ; brancher le second PCIe 8 broches du bloc (pas d'adaptateur) ; brancher l'EPS 8 broches « CPU » ; attacher le câble à l'écart ; refaire le contrôle avant de brancher."),
        ),
        correction=(
            "Cinq anomalies : une vis libre peut toucher la carte (court-circuit) ; le film plastique sous le ventirad empêche le contact thermique (surchauffe en quelques minutes) ; la carte graphique n'a qu'un câble sur deux (beaucoup de cartes refusent alors de démarrer, sinon instabilité) ; l'EPS n'est pas branché (le processeur n'est pas alimenté : pas de démarrage ou arrêt immédiat) ; un câble touche les pales (blocage, bruit, isolant arraché).",
            "Corrections, PC toujours débranché : retirer la vis, retirer le film, brancher le second câble PCIe du bloc (jamais un adaptateur), brancher l'EPS « CPU » jusqu'au clic, attacher le câble avec un collier à l'écart des pales, puis refaire tout le contrôle avant la mise sous tension.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Comparer l'UEFI au bon de montage",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-15"),
        kind=KIND_BOOT,
        context=(
            "Premier démarrage d'un PC que tu viens de monter. Le bon de montage prévoit "
            f"{CASE3_EXPECTED.memory_modules} barrettes pour {CASE3_EXPECTED.memory_gb} Go, un "
            "SSD NVMe de 1 To dans l'emplacement M.2_1 et un disque SATA de 2 To. L'écran de "
            "synthèse du firmware est reproduit en document 1."
        ),
        documents=(_console("Document 1 — Écran de synthèse du firmware (fictif)", *E11_SCREEN),),
        instructions=(
            "Compare chaque ligne au bon de montage et relève les écarts.",
            "Pour chaque écart, donne la cause la plus probable après un montage et la vérification à faire, PC débranché.",
        ),
        criteria=(
            _c("Écarts", 1.5, "16 Go au lieu de 32 (DIMM_A2 vide) ; SSD NVMe absent ; processeur, disque SATA et ventilateur conformes."),
            _c("Mémoire", 1, "Barrette de DIMM_A2 mal enfoncée (clip non fermé) : la renfoncer jusqu'au double clic ; sinon tester la barrette seule."),
            _c("SSD", 1, "SSD M.2 mal inséré ou non vissé (il remonte), entretoise M.2 à la mauvaise longueur : le réinsérer à 30° et le visser ; sinon vérifier dans le manuel l'emplacement et le type pris en charge."),
            _c("Démarche", 0.5, "Un seul changement à la fois, PC débranché, puis relire l'UEFI."),
        ),
        correction=(
            "Écarts : mémoire totale 16 384 Mo (16 Go) au lieu de 32 Go, avec DIMM_A2 vide ; le SSD NVMe n'apparaît pas. Le processeur, le disque SATA et le ventilateur CPU sont conformes.",
            "Après un montage, la cause la plus probable est un geste de montage : barrette de DIMM_A2 pas enfoncée jusqu'au clic → PC débranché, la renfoncer bien droite, les deux clips fermés ; SSD M.2 inséré de travers ou non vissé, ou entretoise M.2 mal placée → le réinsérer et le visser. On change une chose à la fois, puis on relit l'UEFI. Si l'écart persiste, on teste la pièce seule ou dans un autre emplacement (manuel).",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Écran noir au premier démarrage : attendre ou couper ?",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_BOOT,
        context=(
            "Un stagiaire démarre pour la première fois un PC qu'il vient de monter, avec deux "
            "barrettes DDR5 neuves. Les ventilateurs tournent, la LED « DRAM » de la carte mère "
            "est allumée et l'écran reste noir depuis quarante secondes. Il veut couper et tout "
            "redémonter."
        ),
        instructions=(
            "Dis ce que tu lui conseilles et justifie.",
            "Indique quand il faudra réellement chercher une panne et par quoi commencer.",
        ),
        criteria=(
            _c("Conseil", 1, "Attendre quelques minutes : au premier démarrage, la carte entraîne la mémoire (surtout en DDR5), écran noir et LED DRAM allumée sont normaux ; couper interrompt l'opération."),
            _c("Panne", 1, "Si rien après plusieurs minutes : couper, débrancher, renfoncer les barrettes dans les emplacements du manuel, essayer une barrette seule ; vérifier l'écran sur la carte graphique."),
        ),
        correction=(
            "Attendre : au premier démarrage (et après un changement de mémoire), la carte mère entraîne la mémoire, ce qui peut prendre plusieurs minutes avec de la DDR5 ; pendant ce temps, l'écran reste noir et la LED DRAM est allumée. Couper relance l'opération depuis le début.",
            "Si rien ne change après plusieurs minutes : arrêter, débrancher, vérifier que les barrettes sont enfoncées dans les emplacements recommandés par le manuel, essayer une seule barrette, et contrôler que l'écran est branché sur la carte graphique.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Températures anormales après un montage",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-15"),
        kind=KIND_BOOT,
        context=(
            "Un PC monté la veille s'éteint ou ralentit fortement après quelques minutes de "
            "calcul. La fiche du processeur indique une température maximale de "
            f"{E13_LIMIT} °C. Le ventilateur du processeur tourne. Les relevés de l'outil de "
            "surveillance sont en document 1."
        ),
        documents=(
            _table(
                "Document 1 — Relevés de température (fictifs)",
                ("Moment", "Température du processeur"),
                *((moment, f"{temp} °C") for moment, temp in E13_TEMPS),
            ),
        ),
        instructions=(
            "Interprète les relevés au regard de la limite de la fiche.",
            "Donne trois causes de montage possibles et leur vérification, PC débranché.",
        ),
        criteria=(
            _c("Interprétation", 1, f"Déjà élevé au repos (61 °C), la limite de {E13_LIMIT} °C est atteinte en 3 minutes : le processeur réduit sa fréquence puis s'arrête pour se protéger ; refroidissement défaillant."),
            _c("Causes", 2, "Film de la semelle laissé ; pâte absente, en excès ou mal répartie ; ventirad mal serré ou de travers ; ventilateur branché ailleurs ou flux d'air inversé — trois causes avec vérification."),
            _c("Suite", 1, "Démonter le ventirad, nettoyer, nouvelle pâte, remonter en croix ; refaire un test en charge et noter les valeurs."),
        ),
        correction=(
            f"Au repos, 61 °C est déjà élevé pour un PC neuf ; en charge, la limite de {E13_LIMIT} °C est atteinte en trois minutes : le processeur baisse sa fréquence puis s'arrête pour se protéger. Ce n'est pas une pièce défectueuse mais, presque toujours, un défaut de montage du refroidissement.",
            "Causes à vérifier, PC débranché : film plastique laissé sous la semelle ; pâte absente, en excès ou mal répartie (empreinte sur le processeur) ; ventirad pas à plat ou mal serré (serrage en croix) ; ventilateur branché ailleurs qu'en CPU_FAN ou monté à l'envers. Correction : nettoyer à l'alcool isopropylique, nouvelle pâte, remontage, puis test en charge avec relevé des températures.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Justifier l'ordre de montage",
        question_type="long_answer",
        requirement_ids=("AP-14",),
        kind=KIND_JUSTIFY,
        context=(
            "Ton responsable te demande de justifier par écrit la fiche de montage de l'atelier, "
            "qu'un nouveau technicien trouve « trop compliquée ». Il veut monter la carte mère "
            "vide dans le boîtier, puis installer le processeur, la mémoire et le ventirad "
            "dedans, et la carte graphique en premier « pour voir si elle rentre »."
        ),
        instructions=(
            "Justifie l'équipement de la carte mère hors du boîtier.",
            "Justifie la place de la carte graphique et du câblage dans l'ordre.",
            "Indique quand l'ordre peut être adapté.",
        ),
        criteria=(
            _c("Hors boîtier", 1.5, "Accès au socket et aux emplacements sans heurter la carte ; moins de risque de tordre les broches ou de faire fléchir la carte ; on voit les verrous et les repères."),
            _c("Carte graphique", 1, "Installée tard : elle masque emplacements et connecteurs voisins (M.2, SATA, façade), elle est lourde ; sa longueur se vérifie sur la fiche du boîtier, pas en la montant."),
            _c("Câblage", 0.5, "En dernier pour ranger les câbles proprement et contrôler chaque connecteur."),
            _c("Adaptation", 1, "Selon la notice : ventirad à plaque arrière ou AIO, gros ventirad qui masque la mémoire, boîtier étroit ; la notice prime."),
        ),
        correction=(
            "La carte mère s'équipe hors du boîtier, posée sur son carton : on accède au socket, aux emplacements de mémoire et au M.2 sans la faire fléchir ni heurter les broches du socket, et on voit bien les repères et les clips.",
            "La carte graphique vient tard car elle cache les emplacements voisins et les connecteurs de façade, M.2 et SATA ; sa compatibilité se vérifie sur les fiches (longueur), pas en l'essayant. Le câblage termine le montage pour être rangé et contrôlé. L'ordre s'adapte quand la notice l'impose : ventirad à plaque arrière à poser avant d'installer la carte, watercooling (AIO) fixé au boîtier, gros ventirad qui masque la mémoire (mémoire d'abord).",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Un ventirad collé au processeur",
        question_type="short_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_JUSTIFY,
        context=(
            "Tu démontes le ventirad d'un ancien PC à socket AM4 (de type PGA : les broches sont "
            "sous le processeur) pour le nettoyer. Les vis sont retirées, mais le ventirad "
            "reste collé : la pâte a séché. Un collègue propose de tirer fort vers le haut."
        ),
        instructions=(
            "Explique le risque de sa proposition.",
            "Décris la bonne manière de faire et ce qu'il faut faire au remontage.",
        ),
        criteria=(
            _c("Risque", 1, "Le processeur peut sortir du socket collé au ventirad, levier fermé : broches tordues ou arrachées, processeur ou socket détruit."),
            _c("Manière", 1, "Tourner doucement le ventirad d'un côté à l'autre pour décoller la pâte (après quelques minutes de fonctionnement si possible, pâte tiède), puis le soulever ; nettoyer à l'alcool isopropylique ; pâte neuve au remontage."),
        ),
        correction=(
            "Sur un socket PGA, la pâte sèche peut coller le processeur au ventirad : en tirant, on l'arrache du socket alors que le levier est fermé, et les broches se tordent ou cassent.",
            "On tourne doucement le ventirad de quelques degrés d'un côté à l'autre pour casser la pâte (elle cède mieux tiède, après quelques minutes de fonctionnement puis une mise hors tension complète), puis on le soulève. On nettoie les deux surfaces à l'alcool isopropylique et on met une pâte neuve au remontage.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Visserie : choisir la bonne vis au remontage",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_JUSTIFY,
        context=(
            "Au démontage d'un PC, un stagiaire a mis toutes les vis dans le même gobelet. Au "
            "remontage, il en trouve de quatre sortes (document 1). Il doit refixer la carte "
            "mère, le bloc d'alimentation, un SSD SATA 2,5 pouces et un SSD M.2."
        ),
        documents=(
            _table(
                "Document 1 — Vis trouvées (relevé)",
                ("Lot", "Description"),
                ("V1", "Vis à filetage 6-32 UNC, tête cruciforme"),
                ("V2", "Vis M3 courtes, tête plate"),
                ("V3", "Très petite vis M2"),
                ("V4", "Vis autotaraudeuses longues"),
            ),
        ),
        instructions=(
            "Attribue un lot de vis à chaque élément à refixer, en justifiant.",
            "Dis ce qu'il aurait dû faire au démontage.",
        ),
        criteria=(
            _c("Attribution", 2, "Carte mère : 6-32 (V1) le plus souvent, parfois M3 selon le boîtier ; bloc : 6-32 (V1) ; SSD 2,5 pouces : M3 (V2) ; SSD M.2 : M2 (V3) ; V4 : ventilateurs."),
            _c("Précaution", 1, "Ne jamais forcer : une vis qui ne s'engage pas à la main n'est pas la bonne (filetage abîmé)."),
            _c("Démontage", 1, "Trier les vis par élément dans un bac à cases ou des sachets étiquetés, photos, fiche de démontage."),
        ),
        correction=(
            "Carte mère : vis 6-32 du boîtier (V1) dans la plupart des boîtiers, parfois M3 : on essaie à la main, sans forcer. Bloc d'alimentation : 6-32 (V1). SSD 2,5 pouces : M3 (V2), une 6-32 abîmerait son filetage. SSD M.2 : la très petite vis M2 (V3). Les vis autotaraudeuses (V4) servent aux ventilateurs.",
            "Une vis qui ne s'engage pas facilement à la main n'est pas la bonne : forcer abîme le filetage. Au démontage, il fallait trier les vis par élément (bac à cases, sachets étiquetés) et le noter sur la fiche de démontage, avec des photos.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions × 2 points = /20 (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Préparer l'ouverture d'un PC de client",
        question_type="long_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_PROCEDURE,
        context=(
            "Un client te confie son PC de bureau pour ajouter une barrette de mémoire. Le "
            "disque contient ses photos de famille, sans autre copie. Tu travailles à "
            "l'atelier, sur un poste commun où d'autres techniciens interviennent."
        ),
        instructions=("Rédige, dans l'ordre et en les justifiant, tout ce que tu fais avant de toucher la carte mère.",),
        criteria=(
            _c("Données et accord", 0.6, "Sauvegarde proposée et faite (ou refus écrit) ; autorisation signée."),
            _c("État initial", 0.4, "Photos, numéro de série, défauts existants, fonctionnement avant."),
            _c("Mise hors tension", 0.5, "Arrêt, interrupteur sur 0, secteur débranché, bouton appuyé (le +5 VSB reste présent tant que le PC est branché)."),
            _c("ESD et poste", 0.5, "Bracelet relié au châssis, tapis, barrette dans son sachet tenue par les bords ; photos de l'intérieur."),
        ),
        correction=(
            "1. Proposer et faire une sauvegarde des photos (seule copie), ou faire signer le refus. 2. Faire signer l'autorisation d'intervention. 3. Relever l'état initial : photos, numéro de série, défauts, ce qui fonctionne. 4. Arrêter, interrupteur sur 0, débrancher le secteur, appuyer sur le bouton : branché, un PC éteint garde le +5 VSB.",
            "5. Préparer le poste (tapis antistatique, bac à vis) ; mettre le bracelet relié au châssis ; garder la barrette dans son sachet et la tenir par les bords. 6. Photographier l'intérieur avant de toucher quoi que ce soit.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un processeur qui « n'entre pas »",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_JUSTIFY,
        context=(
            "Un stagiaire installe un processeur sur une carte mère à socket LGA. Le processeur "
            "ne se pose pas à plat ; il te demande s'il peut appuyer un peu avant de fermer le "
            "levier, « puisque le levier va de toute façon le plaquer »."
        ),
        instructions=("Réponds-lui en justifiant, et décris la pose correcte.",),
        criteria=(
            _c("Réponse", 1, "Non : s'il ne se pose pas à plat, il est mal orienté ; appuyer ou fermer le levier tord les broches du socket (sur la carte), dégât non réparable simplement."),
            _c("Pose", 1, "Levier et cadre ouverts, capot en place ; triangle sur le repère, encoches alignées ; poser à la verticale sans glisser ; fermer ; garder le capot."),
        ),
        correction=(
            "Non. Un processeur se pose, il ne se force jamais : s'il ne repose pas à plat, il est mal orienté. En appuyant ou en fermant le levier, on tord les broches du socket LGA, qui sont sur la carte mère : la carte devient inutilisable.",
            "Pose correcte : ouvrir le levier et le cadre (capot en place), aligner le triangle doré sur le repère et les encoches sur les ergots, déposer à la verticale sans faire glisser, vérifier qu'il est à plat, fermer le cadre et le levier ; le capot sort seul et se garde.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Remonter un ventirad sans changer la pâte ?",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_JUSTIFY,
        context=(
            "Pour nettoyer un boîtier très poussiéreux, un collègue a retiré le ventirad du "
            "processeur. Il veut le reposer tel quel : « la pâte est encore là, ça ira ». Le PC "
            "sert à du montage vidéo, avec de longues périodes de calcul."
        ),
        instructions=("Dis si c'est acceptable, justifie, et décris le remontage correct.",),
        criteria=(
            _c("Réponse", 1, "Non : la couche a été déformée et a pris de l'air et de la poussière ; contact thermique moins bon, surchauffe et baisse de fréquence en calcul."),
            _c("Remontage", 1, "Nettoyer processeur et semelle à l'alcool isopropylique, chiffon non pelucheux ; petite quantité de pâte neuve ; ventirad à plat, serrage en croix ; test de température en charge."),
        ),
        correction=(
            "Non : quand on soulève un ventirad, la couche de pâte se déchire et emprisonne de l'air et des poussières ; le contact thermique devient moins bon, d'où des températures plus élevées et des baisses de fréquence pendant les longs calculs.",
            "On nettoie les deux surfaces à l'alcool isopropylique avec un chiffon non pelucheux, on remet une petite quantité de pâte neuve, on repose le ventirad à plat et on serre en croix, puis on vérifie la température en charge.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Une entretoise de trop",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_ERROR,
        context=(
            "Un PC tout juste monté s'allume une fraction de seconde puis s'éteint, à chaque "
            "appui. En démontant, tu constates qu'une entretoise vissée dans le boîtier se "
            "trouve sous la carte mère microATX, à un endroit où la carte n'a pas de trou."
        ),
        instructions=("Explique le lien avec le symptôme et la correction.",),
        criteria=(
            _c("Lien", 1, "L'entretoise métallique touche le circuit au dos de la carte : court-circuit, la protection du bloc coupe aussitôt."),
            _c("Correction", 1, "PC débranché, sortir la carte, retirer l'entretoise, vérifier qu'aucune vis ne traîne et que chaque entretoise est en face d'un trou, contrôler la carte puis redémarrer."),
        ),
        correction=(
            "L'entretoise sans trou en face touche le dos de la carte, où passent des pistes : elle crée un court-circuit, et la protection du bloc d'alimentation coupe aussitôt — d'où l'allumage d'une fraction de seconde.",
            "PC débranché, sortir la carte, retirer l'entretoise, vérifier que chaque entretoise correspond à un trou et qu'aucune vis ne traîne, puis remonter et tester. Si la carte ne démarre toujours pas, elle a pu être endommagée : la tester à part.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="La LED d'alimentation reste éteinte",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_ERROR,
        context=(
            "Un PC que tu viens de monter démarre et fonctionne normalement, mais la LED "
            "d'alimentation de la façade reste éteinte. Le câble POWER LED du boîtier a deux "
            "fils, un de couleur et un blanc ; le manuel indique PLED+ et PLED− sur le "
            "connecteur de façade."
        ),
        instructions=("Donne la cause la plus probable et la correction ; dis si le matériel est en danger.",),
        criteria=(
            _c("Cause", 1, "Câble de LED branché à l'envers : la LED est polarisée et ne s'allume que dans un sens."),
            _c("Correction", 1, "PC débranché, retourner le connecteur : fil de couleur (+) sur PLED+ ; aucun danger, une LED inversée ne conduit pas."),
        ),
        correction=(
            "Les boutons ne sont pas polarisés, mais les LED le sont : la LED d'alimentation branchée à l'envers ne s'allume pas. PC débranché, on retourne le connecteur pour mettre le fil de couleur (+) sur PLED+, d'après le manuel. Aucun danger : une LED à l'envers ne laisse simplement pas passer le courant.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Ventilateurs qui tournent, pas d'image",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-15"),
        kind=KIND_BOOT,
        context=(
            "Un PC monté par un stagiaire démarre : les ventilateurs tournent, mais aucune image "
            "n'apparaît, même après cinq minutes. Le document 1 reprend les observations. Le "
            "processeur n'a pas de partie graphique intégrée (fiche)."
        ),
        documents=(
            _table(
                "Document 1 — Observations",
                ("Élément", "Observation"),
                ("LED de diagnostic", "« DRAM » allumée en continu"),
                ("Mémoire", "Deux barrettes ; un clip de la seconde est resté ouvert"),
                ("Écran", "Câble HDMI sur la sortie de la carte mère"),
                ("Carte graphique", "Clip enclenché, deux PCIe 8 broches branchés"),
            ),
        ),
        instructions=("Relève les deux erreurs, leur conséquence et la correction, dans l'ordre où tu les traites.",),
        criteria=(
            _c("Mémoire", 1, "Barrette mal enfoncée (clip ouvert), confirmée par la LED DRAM : PC débranché, la renfoncer jusqu'au clic des deux côtés."),
            _c("Écran", 1, "Sortie de la carte mère inactive sans partie graphique intégrée : brancher l'écran sur la carte graphique."),
        ),
        correction=(
            "1. La LED DRAM et le clip ouvert désignent la mémoire : la seconde barrette n'est pas enfoncée. PC débranché, la renfoncer bien droite jusqu'au clic des deux côtés. 2. Même avec la mémoire corrigée, l'écran resterait noir : la sortie HDMI de la carte mère ne fonctionne qu'avec un processeur à partie graphique intégrée. Brancher l'écran sur une sortie de la carte graphique.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="SSD M.2 absent de l'UEFI après montage",
        question_type="short_answer",
        requirement_ids=("AP-14",),
        kind=KIND_BOOT,
        context=(
            "Après le montage d'un PC, l'UEFI voit le disque SATA mais pas le SSD M.2 NVMe que "
            "tu as installé dans l'emplacement M.2_1, pourtant compatible d'après le manuel. Au "
            "montage, tu n'as pas trouvé la petite vis du M.2 et tu as laissé le SSD « posé »."
        ),
        instructions=("Explique le lien entre ton montage et le symptôme, puis la correction.",),
        criteria=(
            _c("Lien", 1, "Non vissé, le SSD remonte en biais (il est inséré à environ 30°) : contacts mal engagés, non détecté."),
            _c("Correction", 1, "PC débranché, réinsérer le SSD à fond, le rabattre sur l'entretoise M.2 placée à la bonne longueur (2280) et le fixer avec la vis M2 ou le loquet ; relire l'UEFI."),
        ),
        correction=(
            "Un SSD M.2 s'insère en biais (environ 30°) puis se rabat et se fixe ; sans vis, il remonte et ses contacts ne sont plus correctement engagés : l'UEFI ne le voit pas. PC débranché, on le réinsère à fond, on vérifie l'entretoise M.2 à la position de sa longueur (2280), on le fixe avec la vis M2 (ou le loquet de la carte), puis on relit l'UEFI.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Changer une barrette cachée par un gros ventirad",
        question_type="long_answer",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_ORDER,
        context=(
            "Un client demande de remplacer une barrette de mémoire défectueuse (identifiée par "
            "un test mémoire). Son PC a un gros ventirad dont le ventilateur recouvre le premier "
            "emplacement de mémoire. Le PC est arrêté, à l'atelier, autorisation et sauvegarde "
            "déjà en ordre."
        ),
        instructions=("Rédige la procédure de démontage et de remontage, dans l'ordre, avec les précautions.",),
        criteria=(
            _c("Sécurité", 0.5, "Secteur débranché, bouton appuyé, bracelet ; photos."),
            _c("Démontage", 0.7, "Retirer le ventilateur du ventirad (clips) ou le ventirad s'il le faut ; ouvrir les clips de l'emplacement, sortir la barrette droite."),
            _c("Remontage", 0.5, "Barrette de même type (DDR, capacité, fréquence) enfoncée jusqu'au clic ; ventilateur reposé, rebranché sur CPU_FAN ; pâte neuve si le ventirad a été retiré."),
            _c("Contrôle", 0.3, "Mémoire totale dans l'UEFI, test mémoire, température du processeur."),
        ),
        correction=(
            "1. Secteur débranché, bouton appuyé, bracelet relié au châssis ; photos de l'intérieur. 2. Débrancher le ventilateur du ventirad et le déclipser pour dégager l'emplacement (si le ventirad entier doit sortir : rotation douce, puis pâte neuve au remontage). 3. Ouvrir les clips, sortir la barrette bien droite, la ranger dans un sachet antistatique.",
            "4. Insérer la barrette de remplacement (même génération, capacité et fréquence) en alignant l'encoche, jusqu'au clic des deux côtés. 5. Reposer le ventilateur, câble sur CPU_FAN. 6. Contrôler la mémoire totale dans l'UEFI, lancer un test mémoire et vérifier la température du processeur ; compte rendu.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Améliorer le câblage et le flux d'air",
        question_type="document_analysis",
        requirement_ids=("AP-14",),
        kind=KIND_JUSTIFY,
        context=(
            "Un PC monté par un stagiaire fonctionne, mais il est bruyant et chauffe. Ton "
            "relevé, boîtier ouvert et PC débranché, est en document 1. Le boîtier possède un "
            "passage de câbles derrière le plateau de la carte mère."
        ),
        documents=(
            _table(
                "Document 1 — Relevé du câblage et des ventilateurs",
                ("Élément", "Observation"),
                ("Câbles du bloc", "Tous passés devant la carte mère, en paquet devant la façade"),
                ("Ventilateurs de façade", "Les deux soufflent vers l'extérieur (flèche du cadre)"),
                ("Ventilateur arrière", "Souffle vers l'extérieur"),
                ("Câble SATA", "Pendant au-dessus de la carte graphique, touche son ventilateur"),
            ),
        ),
        instructions=("Relève les défauts et propose les corrections en les justifiant.",),
        criteria=(
            _c("Flux", 1, "Trois ventilateurs en extraction, aucune entrée d'air frais : retourner ceux de la façade (entrée), arrière en sortie ; la flèche du cadre indique le sens."),
            _c("Câbles", 1, "Câbles devant la façade bloquent l'air : les passer derrière le plateau, attacher ; câble SATA écarté du ventilateur de la carte graphique."),
        ),
        correction=(
            "Les trois ventilateurs extraient l'air : rien n'apporte d'air frais. On retourne les ventilateurs de façade pour qu'ils aspirent (flèche du cadre vers l'intérieur), l'arrière reste en extraction : entrée à l'avant, sortie à l'arrière et en haut. Les câbles en paquet devant la façade freinent l'air : on les passe derrière le plateau et on les attache. Le câble SATA est écarté du ventilateur de la carte graphique (bruit, risque de blocage).",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Valider un montage avant la remise au client",
        question_type="long_answer",
        requirement_ids=("AP-14",),
        kind=KIND_PROCEDURE,
        context=(
            "Tu viens de monter un PC de bureau pour un client : il démarre et l'UEFI détecte "
            "tout le matériel du bon de montage. Ton responsable demande une validation écrite "
            "avant la remise, « pas juste : ça marche »."
        ),
        instructions=("Rédige les tests à mener et le contenu du compte rendu.",),
        criteria=(
            _c("Tests", 1.2, "Test mémoire en plusieurs passes ; températures au repos et en charge comparées à la fiche ; état SMART des disques ; ports USB, audio et boutons de façade ; stabilité en charge."),
            _c("Compte rendu", 0.8, "Matériel installé et numéros de série, valeurs relevées (mémoire, températures, état des disques), anomalies corrigées, conclusion et date, signature."),
        ),
        correction=(
            "Tests : un test mémoire en plusieurs passes sans erreur ; les températures du processeur au repos et après un test en charge, comparées à la limite de la fiche ; l'état SMART des disques ; chaque port USB, l'audio et les boutons et LED de la façade ; quelques dizaines de minutes de charge sans arrêt.",
            "Compte rendu : configuration et numéros de série, valeurs mesurées (mémoire détectée, températures, état SMART), anomalies rencontrées et corrections, conclusion « conforme » datée et signée. Le boîtier est fermé après les tests.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence officielle du cours citée."""
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
            errors.append(f"{item.key} : au moins une exigence officielle du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

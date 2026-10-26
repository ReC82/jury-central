"""Schémas du cours PR06 « Diagnostic des pannes matérielles » (ticket #193).

Chaque figure est construite depuis les données de ce module (tuples), elles-mêmes
contrôlées par `tests/test_ticket193_ampcr_pratique_pr06.py`. Sources des données
techniques (citées dans le cours et le rapport) :

- brochage ATX 24 broches et EPS 8 broches : guide de conception des alimentations
  ATX12V/EPS12V (Intel, ATX12V Power Supply Design Guide ; SSI EPS12V) — couleurs de fil
  usuelles de ces guides ;
- puissance des connecteurs PCIe (emplacement x16 : 75 W ; 6 broches : 75 W ; 8 broches :
  150 W) : spécification PCI Express CEM (PCI-SIG) ;
- connecteurs SATA (alimentation 15 broches +3,3 V / +5 V / +12 V ; données 7 broches) :
  spécification Serial ATA.

Les écrans, relevés et plans de carte mère sont des **supports fictifs** construits pour
les cas du cours (mention affichée sur chaque figure) : ils ne reproduisent aucun produit
réel et ne sont jamais présentés comme officiels.
"""

from app.v1.ampcr_pratique_visuals import (
    BoardPart,
    Figure,
    board_plan_svg,
    decision_tree_svg,
    line_chart_svg,
    pin_columns_svg,
    screen_svg,
    step_flow_svg,
    two_lists_svg,
)

# --- Chaîne de démarrage --------------------------------------------------------------------

# (étape, ce qui s'y passe / ce que l'on observe quand elle échoue), dans l'ordre réel.
BOOT_CHAIN: tuple[tuple[str, str], ...] = (
    ("Secteur", "Prise, multiprise, câble, interrupteur du bloc. Échec : PC totalement inerte."),
    ("Bloc d'alimentation", "Fournit +12 V, +5 V, +3,3 V et la veille +5 VSB, puis le signal PWR_OK."),
    ("Carte mère", "Le bouton agit sur la carte, qui allume le bloc (PS_ON#) et alimente CPU, RAM, cartes."),
    ("POST", "Autotest du firmware : CPU, RAM, vidéo. Échec : ventilateurs mais ni image ni démarrage, bips ou LED."),
    ("Firmware BIOS/UEFI", "Logo, réglages, ordre de démarrage. Une image ici prouve que l'affichage fonctionne."),
    ("Détection du stockage", "Disques SATA, M.2, NVMe reconnus. Échec : « No boot device », disque absent."),
    ("Chargeur d'amorçage", "Windows Boot Manager (partition EFI) ou GRUB. Échec : erreur avant le logo du système."),
    ("Système d'exploitation", "Noyau, pilotes, services. Échec : écran bleu, plantage, redémarrage."),
)

BOOT_CHAIN_FIGURE = Figure(
    key="pr06-chaine-demarrage",
    title="Chaîne de démarrage d'un PC",
    alt=(
        "Huit étapes reliées par des flèches, de haut en bas : "
        + " ; ".join(f"{i}. {name} — {detail}" for i, (name, detail) in enumerate(BOOT_CHAIN, start=1))
    ),
    caption=(
        "Chaîne de démarrage : chaque étape suppose que la précédente a réussi. Repérer la "
        "dernière étape réussie localise la panne. Lecture de haut en bas."
    ),
    svg=step_flow_svg(BOOT_CHAIN, width=340),
)

# --- Arbre décisionnel « PC ne démarre pas » ------------------------------------------------

# (question fermée, piste si la réponse est « non »). Ordre : du plus simple et sans risque
# au plus invasif, en suivant la chaîne de démarrage.
NO_BOOT_TREE: tuple[tuple[str, str], ...] = (
    (
        "Le secteur arrive-t-il ? (prise testée avec un autre appareil, câble, interrupteur sur I)",
        "Corriger le secteur : autre prise, autre câble, interrupteur du bloc sur I.",
    ),
    (
        "Un signe de vie à l'appui sur le bouton ? (ventilateur, LED, bip)",
        "PC inerte : bouton de façade, ATX 24 et EPS bien clipsés, test du bloc (testeur ou bloc connu bon), recherche d'un court-circuit.",
    ),
    (
        "Le PC reste-t-il allumé plus de quelques secondes ?",
        "Arrêt immédiat : EPS absent, court-circuit, protection du bloc. Passer en configuration minimale.",
    ),
    (
        "Une image apparaît-elle ? (logo ou écran du firmware)",
        "Pas d'image : écran, entrée, câble, bonne sortie vidéo ; puis LED, bips ou code POST lus dans le manuel ; RAM une barrette ; configuration minimale.",
    ),
    (
        "Le firmware voit-il le disque de démarrage ?",
        "Stockage : câbles SATA, type M.2, ordre et mode de démarrage. Ne pas formater ; protéger les données.",
    ),
    (
        "Le système démarre-t-il jusqu'au bureau sans planter ?",
        "Échec du chargeur ou plantage : messages, journaux, RAM, températures, pilotes (voir PR11).",
    ),
)
NO_BOOT_TREE_FINAL = (
    "Toutes les réponses sont « oui » : le démarrage est complet. Reprendre le symptôme décrit "
    "par le client (périphérique, application, réseau)."
)

NO_BOOT_TREE_FIGURE = Figure(
    key="pr06-arbre-pc-ne-demarre-pas",
    title="Arbre décisionnel « Le PC ne démarre pas »",
    alt=(
        "Six questions en colonne, chacune avec une piste si la réponse est non : "
        + " ; ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(NO_BOOT_TREE, start=1))
        + f" Si toutes les réponses sont oui : {NO_BOOT_TREE_FINAL}"
    ),
    caption=(
        "Arbre décisionnel : on descend tant que la réponse est « oui » ; au premier « non », "
        "on suit la piste de droite. Chaque piste se teste du plus simple au plus invasif."
    ),
    svg=decision_tree_svg(NO_BOOT_TREE, NO_BOOT_TREE_FINAL),
)

# --- Connecteurs d'alimentation ---------------------------------------------------------------

# Connecteur principal ATX 24 broches (ATX12V 2.x) : (broche, signal, couleur du fil).
# Broches 1-12 sur une rangée, 13-24 sur l'autre (13 en face de 1). La broche 20 n'est plus
# utilisée (ancien −5 V, retiré des normes récentes).
ATX24_PINOUT: tuple[tuple[int, str, str], ...] = (
    (1, "+3,3 V", "orange"),
    (2, "+3,3 V", "orange"),
    (3, "Masse", "noir"),
    (4, "+5 V", "rouge"),
    (5, "Masse", "noir"),
    (6, "+5 V", "rouge"),
    (7, "Masse", "noir"),
    (8, "PWR_OK", "gris"),
    (9, "+5 VSB (veille)", "violet"),
    (10, "+12 V", "jaune"),
    (11, "+12 V", "jaune"),
    (12, "+3,3 V", "orange"),
    (13, "+3,3 V", "orange"),
    (14, "−12 V", "bleu"),
    (15, "Masse", "noir"),
    (16, "PS_ON#", "vert"),
    (17, "Masse", "noir"),
    (18, "Masse", "noir"),
    (19, "Masse", "noir"),
    (20, "non utilisée", "—"),
    (21, "+5 V", "rouge"),
    (22, "+5 V", "rouge"),
    (23, "+5 V", "rouge"),
    (24, "Masse", "noir"),
)

# Connecteur processeur EPS12V 8 broches : 1-4 masse, 5-8 +12 V (5 en face de 1).
EPS8_PINOUT: tuple[tuple[int, str, str], ...] = (
    (1, "Masse", "noir"),
    (2, "Masse", "noir"),
    (3, "Masse", "noir"),
    (4, "Masse", "noir"),
    (5, "+12 V", "jaune"),
    (6, "+12 V", "jaune"),
    (7, "+12 V", "jaune"),
    (8, "+12 V", "jaune"),
)

ATX24_FIGURE = Figure(
    key="pr06-atx24",
    title="Connecteur principal ATX 24 broches",
    alt=(
        "Tableau des 24 broches du connecteur ATX, rangée 1 à 12 puis rangée 13 à 24 : "
        + " ; ".join(f"broche {n} {s} fil {c}" for n, s, c in ATX24_PINOUT)
        + "."
    ),
    caption=(
        "ATX 24 broches (normes ATX12V récentes) : colonne de gauche = broches 1 à 12, "
        "colonne de droite = 13 à 24, la 13 étant en face de la 1. Numérotation seulement : "
        "pour l'orientation du clip, voir le connecteur ou le manuel. PS_ON# (vert) allume le "
        "bloc, PWR_OK (gris) signale des tensions stables, +5 VSB (violet) reste présent PC "
        "éteint mais branché."
    ),
    svg=pin_columns_svg(ATX24_PINOUT, title="ATX 24 broches — carte mère", rows=12),
)

EPS8_FIGURE = Figure(
    key="pr06-eps8",
    title="Connecteur processeur EPS 8 broches",
    alt=(
        "Tableau des 8 broches du connecteur EPS du processeur : broches 1 à 4 masse, fil noir ; "
        "broches 5 à 8 +12 volts, fil jaune ; la broche 5 est en face de la broche 1."
    ),
    caption=(
        "EPS 8 broches (alimentation du processeur, souvent marqué « CPU » sur le câble) : "
        "4 masses et 4 × +12 V. À ne pas confondre avec le PCIe 8 broches de la carte graphique, "
        "dont le détrompage est différent : ne jamais forcer."
    ),
    svg=pin_columns_svg(EPS8_PINOUT, title="EPS 8 broches — processeur", rows=4),
)

# Autres connecteurs : (connecteur, broches, tensions ou puissance, usage). Texte du tableau
# du cours ; aucune valeur n'est tirée d'une image.
OTHER_CONNECTORS: tuple[tuple[str, str, str, str], ...] = (
    ("PCIe 6 broches", "6", "+12 V, jusqu'à 75 W", "Carte graphique (en plus des 75 W de l'emplacement x16)"),
    ("PCIe 8 broches (6+2)", "8", "+12 V, jusqu'à 150 W", "Carte graphique plus puissante"),
    ("Alimentation SATA", "15", "+3,3 V, +5 V et +12 V", "Disques SATA 2,5\" et 3,5\", lecteurs"),
    ("Données SATA", "7", "aucune alimentation", "Liaison entre le disque et la carte mère"),
    ("Molex 4 broches", "4", "+12 V (jaune) et +5 V (rouge)", "Anciens disques, ventilateurs, accessoires"),
)

# --- Plan schématique de carte mère (support fictif) ---------------------------------------

BOARD_PARTS: tuple[BoardPart, ...] = (
    BoardPart("io", "E/S arrière (vidéo de la carte, USB, réseau)", 10, 32, 56, 150),
    BoardPart("eps", "EPS 8 br. (CPU)", 76, 32, 96, 26),
    BoardPart("socket", "Socket CPU + refroidisseur", 80, 68, 112, 104),
    BoardPart("ram", "RAM : A1 A2 B1 B2", 204, 32, 84, 140),
    BoardPart("atx24", "ATX 24 broches", 298, 40, 72, 84),
    BoardPart("leds", "LED CPU DRAM VGA BOOT", 298, 132, 72, 50),
    BoardPart("pcie16", "PCIe x16 (carte graphique)", 30, 196, 240, 26),
    BoardPart("m2", "Emplacement M.2", 30, 232, 170, 26),
    BoardPart("pcie1", "PCIe x1", 30, 268, 110, 24),
    BoardPart("sata", "4 ports SATA", 298, 196, 72, 84),
    BoardPart("chipset", "Chipset", 214, 236, 70, 44),
    BoardPart("cmos", "Pile CMOS", 160, 300, 72, 44),
    BoardPart("front", "Façade : bouton, LED, USB", 244, 330, 126, 44),
)

BOARD_FIGURE = Figure(
    key="pr06-plan-carte-mere",
    title="Plan schématique d'une carte mère ATX (support fictif)",
    alt=(
        "Plan simplifié d'une carte mère vue de dessus, avec ces zones étiquetées : "
        + ", ".join(part.label for part in BOARD_PARTS)
        + ". Ce n'est pas un plan à l'échelle."
    ),
    caption=(
        "Plan schématique d'une carte mère ATX fictive, vue de dessus (non à l'échelle). "
        "L'emplacement exact des éléments change d'un modèle à l'autre : le manuel de la carte "
        "fait foi (slot RAM à utiliser avec une seule barrette, ports partagés, LED)."
    ),
    svg=board_plan_svg(BOARD_PARTS, title="Carte mère ATX — vue de dessus (fictive)"),
)

# --- Cas 3 : écran du firmware (capture fictive) ---------------------------------------------

FIRMWARE_SCREEN: tuple[str, ...] = (
    "UEFI — Informations système",
    "Processeur ........ détecté",
    "Mémoire ........... 16384 Mo",
    "Stockage :",
    "  SATA3_0 ......... non détecté",
    "  SATA3_1 ......... DVD-RW",
    "  M.2_1 ........... non détecté",
    "Mode de démarrage . UEFI (CSM désactivé)",
    "Ordre : 1. Windows Boot Manager (absent)",
    "",
    "Reboot and Select proper Boot device",
    "or Insert Boot Media in selected",
    "Boot device and press a key_",
)

FIRMWARE_SCREEN_FIGURE = Figure(
    key="pr06-ecran-firmware",
    title="Écran du firmware au démarrage (capture fictive)",
    alt="Écran texte : " + " / ".join(line for line in FIRMWARE_SCREEN if line) + ".",
    caption=(
        "Capture fictive reconstituée pour le cas 3 : la mémoire et le processeur sont vus, "
        "aucun disque de démarrage n'est détecté. Le message de la dernière ligne est celui "
        "qu'affichent de nombreux firmwares quand aucun périphérique de démarrage n'est trouvé."
    ),
    svg=screen_svg(FIRMWARE_SCREEN, label="Capture fictive — cas 3"),
)

# --- Cas 4 : relevé de températures sous charge -------------------------------------------

# (minute, température CPU °C, fréquence CPU GHz, vitesse du ventilateur CPU tr/min)
TEMPERATURE_LOG: tuple[tuple[int, int, str, int], ...] = (
    (0, 41, "4,4", 640),
    (2, 72, "4,4", 650),
    (4, 85, "4,4", 640),
    (6, 93, "4,2", 650),
    (8, 99, "2,6", 640),
    (10, 100, "1,8", 650),
)
TEMPERATURE_LIMIT = 100  # température maximale indiquée sur la fiche du processeur (cas 4)

TEMPERATURE_FIGURE = Figure(
    key="pr06-courbe-temperature",
    title="Température du processeur pendant le test de charge (cas 4)",
    alt=(
        "Courbe de la température du processeur en fonction du temps : "
        + ", ".join(f"minute {m} : {t} °C" for m, t, _f, _v in TEMPERATURE_LOG)
        + f". Ligne pointillée : maximum indiqué par le fabricant, {TEMPERATURE_LIMIT} °C. "
        "Le PC s'éteint juste après la minute 10."
    ),
    caption=(
        "Relevé fictif du cas 4 (mêmes valeurs que le tableau) : la température monte jusqu'au "
        "maximum indiqué par le fabricant, puis le PC s'éteint."
    ),
    svg=line_chart_svg(
        tuple((m, t) for m, t, _f, _v in TEMPERATURE_LOG),
        threshold=TEMPERATURE_LIMIT,
        x_label="Temps de charge (minutes)",
        y_label="Température CPU (°C)",
        threshold_label=f"maximum fabricant {TEMPERATURE_LIMIT} °C",
        y_max=120,
    ),
)

# --- Configuration minimale ------------------------------------------------------------------

MINIMAL_KEEP: tuple[str, ...] = (
    "Bloc d'alimentation (si possible connu bon)",
    "Carte mère",
    "Processeur + refroidisseur",
    "1 barrette RAM (slot du manuel)",
    "1 sortie vidéo : iGPU ou 1 carte graphique",
    "Écran + clavier",
)
MINIMAL_REMOVE: tuple[str, ...] = (
    "Disques, SSD, lecteurs",
    "Barrettes RAM supplémentaires",
    "Cartes d'extension inutiles au test",
    "Périphériques USB (sauf clavier)",
    "Câbles réseau, imprimante, hub",
    "Carte graphique si l'iGPU suffit",
)

MINIMAL_CONFIG_FIGURE = Figure(
    key="pr06-configuration-minimale",
    title="Plan de configuration minimale",
    alt=(
        "Deux listes. On garde : " + ", ".join(MINIMAL_KEEP) + ". On retire : "
        + ", ".join(MINIMAL_REMOVE) + "."
    ),
    caption=(
        "Configuration minimale : seulement ce qui est indispensable pour atteindre le POST et "
        "une image. Toujours hors tension, prise retirée, avec protection ESD. On rajoute "
        "ensuite un élément à la fois et on teste après chaque ajout."
    ),
    svg=two_lists_svg("On garde (✓)", MINIMAL_KEEP, "On retire (✗)", MINIMAL_REMOVE),
)

PR06_FIGURES: tuple[Figure, ...] = (
    BOOT_CHAIN_FIGURE,
    NO_BOOT_TREE_FIGURE,
    ATX24_FIGURE,
    EPS8_FIGURE,
    BOARD_FIGURE,
    FIRMWARE_SCREEN_FIGURE,
    TEMPERATURE_FIGURE,
    MINIMAL_CONFIG_FIGURE,
)

"""PR01 « Structure d'un PC et identification des composants » — exercices corrigés et
mini-examen (ticket #202).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — identifications sur schéma ou description, analyses d'inventaire,
  choix de pièces compatibles, scénarios et procédures écrites ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les fiches produits sont **fictives** (aucune spécification de produit réel inventée) mais
cohérentes avec les normes du cours (`app.v1.ampcr_pratique_pr01_figures`) ; les relevés
d'inventaire sont produits par le code (tailles converties par calcul).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr01_figures import (
    CASE2_SLOTS,
    FORM_FACTORS_BY_NAME,
    INVENTORY_DISKS,
    SATA3_USEFUL_MBYTES,
    binary_size,
    board_fits_case,
    fr_number,
    lsblk_lines,
    memory_cim_lines,
    pcie_link_gbytes,
)
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)

PR01_CODE = "PR01"

KIND_ID = "identification"
KIND_INVENTORY = "analyse d'inventaire"
KIND_CHOICE = "choix d'une pièce compatible"
KIND_SCENARIO = "scénario"
KIND_PROCEDURE = "procédure écrite"

# Exigences officielles du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-01", "AP-02", "AP-05", "AP-07", "AP-17"})


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E04_LINES = lsblk_lines(INVENTORY_DISKS)
E04_SSD_SHOWN = binary_size(500 * 10**9)  # « 465.7G » pour un SSD vendu 500 Go
E06_NVME4 = fr_number(pcie_link_gbytes(16, 4))  # PCIe 4.0 x4 ≈ 7,9 Go/s
E06_NVME3 = fr_number(pcie_link_gbytes(8, 4))  # PCIe 3.0 x4 ≈ 3,9 Go/s
E08_ATX_IN_MATX = board_fits_case("ATX", "microATX")  # False
E08_MATX_SLOTS = FORM_FACTORS_BY_NAME["microATX"].max_slots
CASE_MEMORY_LINES = memory_cim_lines(CASE2_SLOTS)

E02_CATEGORIES = (
    "Mémoire volatile (contenu perdu à l'extinction)",
    "Mémoire non volatile du firmware (ROM, flash)",
    "Stockage de masse non volatile",
)
E11_CATEGORIES = ("Périphérique d'entrée", "Périphérique de sortie", "Périphérique d'entrée et de sortie")


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Identifier huit éléments d'une carte mère d'après leur description",
        question_type="document_analysis",
        requirement_ids=("AP-07", "AP-02", "AP-01"),
        kind=KIND_ID,
        context=(
            "Un stagiaire de l'atelier a photographié une carte mère ATX posée sur le tapis "
            "antistatique, mais la photo est floue. Il a donc décrit par écrit huit éléments "
            "repérés A à H (document 1), sans les nommer. Tu dois compléter sa fiche d'inventaire."
        ),
        documents=(
            _table(
                "Document 1 — Description des repères (carte mère ATX, vue de dessus)",
                ("Repère", "Description relevée"),
                ("A", "Support carré d'environ 4 cm à levier métallique, dans la moitié haute, entouré de petits radiateurs"),
                ("B", "Quatre longs emplacements parallèles, munis de clips, juste à droite du repère A"),
                ("C", "Connecteur à 24 broches sur deux rangées, sur le bord droit"),
                ("D", "Connecteur à 8 broches marqué « CPU », dans le coin en haut à gauche"),
                ("E", "Long emplacement parallèle au bord inférieur, le plus proche du repère A"),
                ("F", "Fente plate couchée sur la carte, avec un pas de vis à 80 mm de la fente"),
                ("G", "Pile ronde et plate d'environ 2 cm"),
                ("H", "Petits connecteurs en forme de L à 7 contacts, regroupés sur le bord droit"),
            ),
        ),
        instructions=(
            "Nomme chacun des huit éléments A à H.",
            "Donne en une phrase le rôle de chacun.",
            ("Indique lesquels de B, E, F et H sont en général reliés directement au processeur et "
             "lesquels passent par le chipset, en précisant où se vérifie cette information."),
        ),
        criteria=(
            _c("Identification", 2, "A socket du processeur (entouré du VRM) ; B emplacements DIMM de mémoire vive ; C connecteur d'alimentation ATX 24 broches ; D connecteur EPS 8 broches du processeur ; E emplacement PCIe x16 ; F emplacement M.2 ; G pile CMOS ; H ports SATA de données (0,25 pt par repère)."),
            _c("Rôles", 1.5, "Socket : reçoit le processeur ; DIMM : barrettes de RAM ; ATX 24 : alimentation principale de la carte ; EPS : alimentation du processeur via le VRM ; PCIe x16 : carte graphique ; M.2 : SSD (NVMe ou SATA selon l'emplacement) ; pile : horloge (et réglages sur certaines cartes) ; SATA : liaison de données des disques."),
            _c("Liaisons", 0.5, "B (mémoire) et E (PCIe x16) sont reliés au processeur, F souvent aussi pour le premier M.2 ; H (SATA) dépend en général du chipset ; vérification dans le manuel ou le schéma-bloc de la carte."),
        ),
        correction=(
            "A est le socket du processeur ; les petits radiateurs autour couvrent le VRM, qui fabrique la tension du processeur. B : les quatre emplacements DIMM reçoivent les barrettes de mémoire vive. C : le connecteur ATX 24 broches apporte l'alimentation principale de la carte. D : le connecteur EPS 8 broches, marqué CPU, alimente le processeur à travers le VRM.",
            "E : l'emplacement PCIe x16 le plus proche du processeur, destiné à la carte graphique. F : un emplacement M.2 ; le pas de vis à 80 mm correspond à un module 2280 ; il reçoit un SSD NVMe ou SATA selon ce que le manuel indique. G : la pile CMOS maintient l'horloge de la carte (et, sur certaines cartes, les réglages). H : les ports SATA relient les disques durs et SSD 2,5 pouces à la carte (données seulement).",
            "Sur une plateforme récente, la mémoire (B) et le PCIe x16 principal (E) sont reliés au processeur, comme souvent le premier M.2 (F) ; les ports SATA (H) passent en général par le chipset. Cela se vérifie dans le manuel de la carte (schéma-bloc ou tableau des emplacements), jamais au jugé.",
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Ranger les mémoires d'un PC : volatile, firmware ou stockage",
        question_type="classification",
        requirement_ids=("AP-02", "AP-01"),
        kind=KIND_ID,
        context=(
            "Un client lit sur une fiche technique les mots « RAM », « ROM », « cache » et « SSD » "
            "et pense que ce sont quatre noms pour la même chose. Pour lui expliquer, tu ranges "
            "chaque mémoire de son PC selon ce qu'elle conserve et à quoi elle sert."
        ),
        instructions=(
            ("Classe chacun des sept éléments dans la catégorie qui lui correspond : mémoire "
             "volatile, mémoire non volatile du firmware, ou stockage de masse non volatile."),
        ),
        criteria=(
            _c("Classement", 3.5, "Barrette DDR5, cache L3 et mémoire GDDR de la carte graphique : volatiles ; puce flash du firmware UEFI : firmware ; SSD NVMe, disque dur et clé USB : stockage de masse (0,5 pt par élément)."),
        ),
        correction=(
            "Volatiles (contenu perdu à l'extinction) : la barrette DDR5 (mémoire vive de travail), le cache L3 (petite mémoire très rapide dans le processeur) et la mémoire GDDR de la carte graphique (mémoire vive de la carte graphique).",
            "Firmware : la puce flash de la carte mère contient le firmware UEFI (le « BIOS ») ; on l'appelle encore ROM car elle n'est pas modifiée en usage normal, mais elle est réinscriptible lors d'une mise à jour. Elle ne contient ni le système ni les fichiers de l'utilisateur.",
            "Stockage de masse (non volatile, grande capacité, contient système et fichiers) : le SSD NVMe, le disque dur et la clé USB. Un SSD utilise aussi de la mémoire flash, mais c'est un périphérique de stockage, pas la ROM de la carte.",
        ),
        classification=Classification(
            categories=E02_CATEGORIES,
            elements=(
                "Barrette DDR5 de 16 Go",
                "Puce flash de la carte mère qui contient le firmware UEFI",
                "SSD NVMe de 1 To",
                "Cache L3 intégré au processeur",
                "Disque dur 3,5 pouces de 2 To",
                "Mémoire GDDR soudée sur la carte graphique",
                "Clé USB de 64 Go",
            ),
            correct=(0, 1, 2, 0, 2, 0, 2),
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le trajet d'une photo jusqu'à l'écran",
        question_type="ordering",
        requirement_ids=("AP-01", "AP-07"),
        kind=KIND_ID,
        context=(
            "Pour expliquer le rôle de chaque composant à un client, tu décris le trajet des "
            "données quand il ouvre une photo enregistrée sur le SSD NVMe de son PC de bureau. "
            "L'écran est branché par DisplayPort sur la carte graphique, installée dans le slot "
            "PCIe x16. Les étapes ci-dessous sont mélangées."
        ),
        instructions=("Remets les six étapes dans l'ordre réel du trajet des données.",),
        criteria=(
            _c("Ordre", 3, "Lecture sur le SSD → liaison PCIe vers le processeur → copie en mémoire vive → décodage par le processeur → envoi à la carte graphique par le PCIe x16 → signal vers l'écran par DisplayPort."),
        ),
        correction=(
            "1. Les données de la photo sont lues sur le SSD NVMe. 2. Elles passent par la liaison PCIe de l'emplacement M.2 jusqu'au processeur. 3. Elles sont copiées en mémoire vive (le contrôleur mémoire est dans le processeur).",
            "4. Le processeur lit ces données en mémoire vive et décode l'image. 5. L'image est transmise à la carte graphique par le slot PCIe x16. 6. La carte graphique envoie le signal vidéo à l'écran par le câble DisplayPort. Le chipset n'intervient pas ici : le SSD, la mémoire et la carte graphique sont reliés directement au processeur.",
        ),
        ordering=Ordering(
            steps=(
                "L'image est transmise à la carte graphique par le slot PCIe x16.",
                "Les données de la photo sont lues sur le SSD NVMe.",
                "Le processeur lit les données en mémoire vive et décode l'image.",
                "La carte graphique envoie le signal vidéo à l'écran par le câble DisplayPort.",
                "Les données passent par la liaison PCIe de l'emplacement M.2 jusqu'au processeur.",
                "Les données sont copiées en mémoire vive.",
            ),
            correct=(1, 4, 5, 2, 0, 3),
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Lire l'inventaire des disques d'un poste Linux",
        question_type="document_analysis",
        requirement_ids=("AP-01", "AP-02"),
        kind=KIND_INVENTORY,
        context=(
            "Un poste de l'atelier tourne sous Linux. Avant de proposer une mise à niveau, tu "
            "relèves la liste de ses unités de stockage avec la commande lsblk (document 1). La "
            "colonne TRAN indique l'interface, ROTA vaut 1 pour un disque à plateaux et 0 pour "
            "une unité sans pièce mobile, SIZE est affichée en unités binaires (1G = 1024³ "
            "octets). Le client s'étonne que son SSD « de 500 Go » n'affiche pas 500."
        ),
        documents=(_console("Document 1 — Inventaire des unités de stockage (capture fictive)", *E04_LINES),),
        instructions=(
            "Pour chaque ligne, indique le type d'unité et son interface.",
            f"Explique au client pourquoi son SSD de 500 Go affiche {E04_SSD_SHOWN}.",
            "Indique sur quelle unité installer le système pour obtenir le démarrage le plus rapide, et pourquoi.",
        ),
        criteria=(
            _c("Types et interfaces", 2, "sda : disque dur à plateaux SATA ; sdb : SSD SATA 2,5 pouces ; nvme0n1 : SSD NVMe sur M.2 (PCIe) ; sdc : clé USB, stockage amovible."),
            _c("Unités", 1, f"Le fabricant compte en unités décimales (500 Go = 500 × 10⁹ octets) ; lsblk affiche en unités binaires (1G = 1024³ octets) : 500 × 10⁹ / 1024³ ≈ {E04_SSD_SHOWN.replace('G', '')} ; rien ne manque, ce n'est pas une panne."),
            _c("Choix du système", 1, f"nvme0n1 : liaison PCIe nettement plus rapide que le SATA (limité à {SATA3_USEFUL_MBYTES} Mo/s utiles) et sans pièce mobile."),
        ),
        correction=(
            "sda (TRAN sata, ROTA 1) : disque dur à plateaux en SATA, ici de 2 To. sdb (sata, ROTA 0) : SSD SATA 2,5 pouces. nvme0n1 (nvme) : SSD NVMe sur un emplacement M.2, relié en PCIe. sdc (usb) : clé USB, stockage amovible.",
            f"Le fabricant annonce la capacité en unités décimales : 500 Go = 500 000 000 000 octets. lsblk compte en unités binaires (1G = 1 073 741 824 octets) : 500 × 10⁹ / 1024³ ≈ 465,7, d'où « {E04_SSD_SHOWN} ». Il ne manque rien.",
            f"Le système va sur nvme0n1 : le NVMe passe par le PCIe, bien plus rapide que la liaison SATA (au plus {SATA3_USEFUL_MBYTES} Mo/s utiles) ; le disque dur à plateaux est le plus lent et sert plutôt aux archives.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Choisir une barrette de mémoire pour un portable",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Une cliente veut passer son ordinateur portable de 8 à 16 Go de mémoire vive sans "
            "retirer la barrette déjà installée. Tu as relevé la fiche du portable (document 1) "
            "et le fournisseur propose quatre barrettes (document 2). Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Fiche du portable (fictive)",
                ("Élément", "Valeur"),
                ("Emplacements mémoire", "2 × SO-DIMM DDR4 ; 1 occupé, 1 libre"),
                ("Barrette installée", "8 Go SO-DIMM DDR4-3200"),
                ("Capacité maximale", "32 Go (2 × 16 Go)"),
            ),
            _table(
                "Document 2 — Barrettes proposées (fictives)",
                ("Offre", "Barrette"),
                ("A", "8 Go DIMM DDR4-3200"),
                ("B", "8 Go SO-DIMM DDR5-4800"),
                ("C", "8 Go SO-DIMM DDR4-3200"),
                ("D", "32 Go SO-DIMM DDR4-3200"),
            ),
        ),
        instructions=(
            "Choisis la barrette à commander.",
            "Justifie le rejet de chacune des trois autres offres.",
            "Cite deux précautions à prendre lors de l'installation.",
        ),
        criteria=(
            _c("Choix", 1, "Offre C : SO-DIMM DDR4-3200 de 8 Go, identique à la barrette en place ; total 16 Go."),
            _c("Rejets justifiés", 2, "A : format DIMM de PC de bureau, trop long pour un portable ; B : DDR5, encoche et tension différentes, ne s'insère pas dans un slot DDR4 ; D : 32 Go dépasse les 16 Go maximum par emplacement de la fiche."),
            _c("Précautions", 1, "Portable éteint, débranché, batterie déconnectée si le manuel le prévoit ; protection ESD ; barrette tenue par les bords, insérée à environ 45° puis rabattue jusqu'aux clips ; vérification de la capacité détectée ensuite."),
        ),
        correction=(
            "Offre C. Elle a le bon format (SO-DIMM), la bonne génération (DDR4) et la même fréquence que la barrette en place : le portable aura 16 Go.",
            "A est une DIMM, le format long des PC de bureau : elle n'entre pas dans un portable. B est une DDR5 : l'encoche-détrompeur et la tension diffèrent, elle ne s'insère pas dans un slot DDR4. D a le bon format mais 32 Go par barrette, au-delà des 16 Go par emplacement indiqués par la fiche (32 Go au total sur deux emplacements).",
            "Précautions : portable éteint et débranché, batterie déconnectée si le manuel le demande, bracelet ou tapis antistatique, barrette tenue par les bords, insertion inclinée puis rabattue jusqu'au verrouillage des clips. On vérifie ensuite que 16 Go sont détectés.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Choisir un SSD M.2 compatible avec la carte mère",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-07", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Un client veut le SSD le plus rapide possible pour le système, dans l'emplacement "
            "M.2_1 de sa carte mère, et plus tard un second SSD bon marché. Le document 1 reprend "
            "le manuel de la carte, le document 2 les offres du fournisseur. Fiches fictives. Les "
            "ports SATA_1 et SATA_2 sont déjà utilisés par un disque dur et un graveur."
        ),
        documents=(
            _table(
                "Document 1 — Extrait du manuel de la carte mère (fictif)",
                ("Emplacement", "Caractéristiques"),
                ("M.2_1", "clé M ; PCIe 4.0 x4, NVMe uniquement ; modules 2242, 2260, 2280"),
                ("M.2_2", "clé M ; PCIe 3.0 x4 NVMe ou SATA ; modules 2280 ; en mode SATA, le port SATA_2 est désactivé"),
                ("SATA_1 à SATA_4", "SATA 6 Gbit/s"),
            ),
            _table(
                "Document 2 — SSD proposés (fictifs)",
                ("Offre", "SSD"),
                ("A", "M.2 SATA, format 2280, clé B+M"),
                ("B", "M.2 NVMe PCIe 4.0 x4, format 22110"),
                ("C", "M.2 NVMe PCIe 4.0 x4, format 2280"),
                ("D", "SSD SATA 2,5 pouces"),
            ),
        ),
        instructions=(
            "Indique le SSD à installer dans M.2_1 et justifie.",
            "Pour chaque autre offre, dis si elle est utilisable, où, et avec quelle conséquence.",
            "Compare le débit théorique de l'interface du SSD retenu à celui du SATA.",
        ),
        criteria=(
            _c("SSD du système", 1, "C : NVMe PCIe 4.0 x4 au format 2280, accepté par M.2_1 (NVMe uniquement, 2280 prévu)."),
            _c("Autres offres", 2, "A : un M.2 SATA ne fonctionne pas dans M.2_1 (NVMe uniquement), même s'il s'y enfiche ; possible dans M.2_2 mais il désactive SATA_2, donc le graveur ; B : 22110 = 110 mm, trop long pour les deux emplacements ; D : utilisable sur SATA_3 ou SATA_4 avec un câble de données et une alimentation SATA."),
            _c("Débits", 1, f"PCIe 4.0 x4 ≈ {E06_NVME4} Go/s théoriques contre {SATA3_USEFUL_MBYTES} Mo/s utiles pour le SATA 6 Gbit/s (le SSD réel peut être plus lent que son interface)."),
        ),
        correction=(
            "Dans M.2_1, on installe C : un SSD NVMe PCIe 4.0 x4 au format 2280 (22 mm de large, 80 mm de long), exactement ce que l'emplacement accepte.",
            "A (M.2 SATA, clé B+M) s'enfiche physiquement dans une clé M, mais M.2_1 n'accepte que le NVMe : il ne serait pas détecté. Il fonctionnerait dans M.2_2, mais le port SATA_2 serait alors désactivé et le graveur perdu. B est au format 22110 (110 mm) : aucun emplacement de la carte ne le reçoit. D (SATA 2,5 pouces) convient comme second SSD sur SATA_3 ou SATA_4, avec un câble de données SATA et un connecteur d'alimentation SATA du bloc.",
            f"Débit théorique de l'interface : PCIe 4.0 x4 ≈ {E06_NVME4} Go/s (PCIe 3.0 x4 de M.2_2 : ≈ {E06_NVME3} Go/s), SATA 6 Gbit/s : {SATA3_USEFUL_MBYTES} Mo/s utiles. La fiche du SSD indique son débit réel, souvent inférieur.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Choisir un processeur de remplacement compatible",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-02", "AP-07"),
        kind=KIND_CHOICE,
        context=(
            "Un client veut un processeur plus puissant pour son PC de bureau, sans changer de "
            "carte mère ni de mémoire. Tu as relevé la carte mère (document 1) et le fournisseur "
            "propose trois processeurs (document 2). Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Carte mère du client (fictive)",
                ("Élément", "Valeur"),
                ("Socket", "AM4"),
                ("Mémoire", "DDR4, 2 × 8 Go installés"),
                ("Firmware installé", "version 1.20"),
                ("Liste des processeurs pris en charge (site du fabricant)", "processeur P2 : à partir du firmware 1.40"),
            ),
            _table(
                "Document 2 — Processeurs proposés (fictifs)",
                ("Offre", "Processeur"),
                ("P1", "socket AM5, mémoire DDR5 uniquement"),
                ("P2", "socket AM4, mémoire DDR4"),
                ("P3", "socket LGA1700"),
            ),
        ),
        instructions=(
            "Indique le processeur compatible et rejette les deux autres en justifiant.",
            "Indique ce qu'il faut faire AVANT de remplacer le processeur, et dans quel ordre.",
            "Cite les vérifications liées au refroidissement.",
        ),
        criteria=(
            _c("Choix et rejets", 1.5, "P2 seul : même socket AM4 et DDR4 ; P1 : socket AM5 (et DDR5), ne rentre pas ; P3 : socket Intel LGA1700, autre plateforme."),
            _c("Firmware d'abord", 1.5, "La carte est en 1.20 et P2 exige 1.40 : mettre à jour le firmware avec l'ancien processeur en place, sans coupure, puis seulement remplacer le processeur ; sinon pas d'image malgré le même socket."),
            _c("Refroidissement", 1, "Ventirad compatible avec le socket et suffisant pour la puissance thermique du nouveau processeur ; nettoyage et pâte thermique neuve ; ventilateur sur CPU_FAN."),
        ),
        correction=(
            "P2 est le seul compatible : socket AM4 et mémoire DDR4, comme la carte du client. P1 est en socket AM5 et n'accepte que la DDR5 : ni la carte ni la mémoire ne conviennent. P3 est un processeur Intel en socket LGA1700 : autre plateforme.",
            "Même socket ne suffit pas : la liste du fabricant exige le firmware 1.40 et la carte est en 1.20. Ordre : sauvegarder les réglages utiles, mettre à jour le firmware avec l'ancien processeur en place (alimentation stable, sans interruption), vérifier la version, puis seulement couper, débrancher et remplacer le processeur avec les précautions ESD.",
            "Refroidissement : vérifier que le ventirad est prévu pour le socket et pour la puissance thermique du nouveau processeur, nettoyer l'ancienne pâte, appliquer une pâte neuve, rebrancher le ventilateur sur CPU_FAN, puis contrôler la température au premier démarrage.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Une carte mère ATX pour un boîtier mini-tour",
        question_type="short_answer",
        requirement_ids=("AP-17", "AP-07"),
        kind=KIND_SCENARIO,
        context=(
            "Un client a acheté une carte mère au format ATX pour remplacer la sienne. Son boîtier "
            "est une mini-tour dont la fiche indique « cartes mères compatibles : microATX, "
            "Mini-ITX ». Il veut garder ce boîtier et installer plus tard trois cartes "
            "d'extension (carte graphique, carte réseau, carte d'acquisition)."
        ),
        instructions=(
            "Explique, dimensions à l'appui, si la carte ATX peut être montée dans ce boîtier.",
            "Propose une solution qui respecte le souhait du client et justifie-la.",
        ),
        criteria=(
            _c("Diagnostic", 1.5, "Non : l'ATX mesure 305 × 244 mm, le boîtier n'accepte que le microATX (244 × 244 mm au plus) ; les fixations et la place manquent sur 61 mm."),
            _c("Solution", 1.5, f"Carte microATX : elle entre dans le boîtier et offre jusqu'à {E08_MATX_SLOTS} emplacements d'extension, assez pour trois cartes (vérifier leur nombre exact et l'épaisseur de la carte graphique) ; sinon un boîtier ATX ; le Mini-ITX n'a qu'un emplacement."),
        ),
        correction=(
            "La carte ATX mesure jusqu'à 305 × 244 mm ; le boîtier accepte au plus le microATX, soit 244 × 244 mm. Il manque environ 61 mm et les fixations de la partie droite de la carte n'existent pas : elle ne peut pas être montée.",
            f"Solution : échanger la carte contre un modèle microATX de même plateforme ; ce format offre jusqu'à {E08_MATX_SLOTS} emplacements d'extension, ce qui permet trois cartes (en vérifiant le nombre réel d'emplacements et qu'une carte graphique épaisse n'en masque pas un). Autre possibilité : garder la carte ATX et changer de boîtier. Le Mini-ITX ne convient pas : un seul emplacement d'extension.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Vérifier qu'une carte graphique peut être installée",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-01"),
        kind=KIND_CHOICE,
        context=(
            "Un client a repéré une carte graphique et te demande si elle peut être montée dans "
            "son PC avant de la commander. Le document 1 rassemble ce que tu as relevé. Fiches "
            "fictives."
        ),
        documents=(
            _table(
                "Document 1 — Relevé de compatibilité (fictif)",
                ("Élément", "Carte graphique envisagée", "PC du client"),
                ("Emplacement", "PCIe 4.0 x16", "carte mère : PCIe 3.0 x16 libre"),
                ("Longueur", "320 mm", "boîtier : 300 mm au plus"),
                ("Épaisseur", "2 emplacements", "2 emplacements libres sous le slot"),
                ("Alimentation", "2 connecteurs PCIe 8 broches ; bloc recommandé 650 W", "bloc 550 W, un seul câble PCIe 6+2"),
                ("Sorties", "3 DisplayPort, 1 HDMI", "écran : entrée HDMI"),
            ),
        ),
        instructions=(
            "Examine chaque ligne et dis si elle est compatible ou non, en justifiant.",
            "Donne ta conclusion au client et deux solutions possibles.",
        ),
        criteria=(
            _c("Emplacement", 1, "Compatible : le PCIe est rétrocompatible, la carte 4.0 fonctionne dans un slot 3.0 x16, au débit du 3.0."),
            _c("Encombrement", 1, "Longueur incompatible (320 mm pour 300 mm) ; épaisseur compatible (2 emplacements libres)."),
            _c("Alimentation", 1.5, "Incompatible : 550 W au lieu des 650 W recommandés et un seul câble PCIe pour deux connecteurs 8 broches ; pas d'adaptateur de fortune."),
            _c("Sorties et conclusion", 1.5, "Sortie HDMI disponible pour l'écran ; conclusion : pas montable en l'état ; solutions : carte plus courte et moins gourmande adaptée au bloc, ou nouveau boîtier et nouveau bloc adapté."),
        ),
        correction=(
            "Emplacement : compatible. Le PCIe est rétrocompatible : une carte PCIe 4.0 fonctionne dans un slot PCIe 3.0 x16, avec le débit du 3.0. Épaisseur : compatible, deux emplacements sont libres. Sorties : compatible, l'écran se branche sur la sortie HDMI de la carte.",
            "Longueur : incompatible, 320 mm pour 300 mm au plus dans le boîtier. Alimentation : incompatible, le bloc fait 550 W pour 650 W recommandés et n'a qu'un câble PCIe pour deux connecteurs 8 broches ; on n'utilise pas d'adaptateur Molex ou SATA pour compenser.",
            "Conclusion : la carte ne peut pas être montée en l'état. Solutions : choisir une carte plus courte (300 mm au plus) dont l'alimentation recommandée et les connecteurs conviennent au bloc, ou changer le boîtier et le bloc pour des modèles adaptés (devis à valider par le client).",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Brancher un poste de travail sur les bons ports",
        question_type="document_analysis",
        requirement_ids=("AP-05", "AP-01", "AP-06"),
        kind=KIND_ID,
        context=(
            "Tu installes un PC de bureau neuf équipé d'une carte graphique dédiée. Tu dois "
            "brancher : un écran DisplayPort, une imprimante USB 2.0, un SSD externe USB "
            "10 Gbit/s à connecteur USB-C, un casque-micro à deux jacks (vert et rose) et le câble "
            "réseau. Le document 1 décrit les ports de l'arrière du PC."
        ),
        documents=(
            _table(
                "Document 1 — Arrière du PC (relevé, fictif)",
                ("Repère", "Description"),
                ("1", "Deux prises USB-A à languette noire, marquées USB 2.0"),
                ("2", "Quatre prises USB-A à languette bleue, marquées 5 Gbit/s"),
                ("3", "Une prise USB-C marquée 10 Gbit/s"),
                ("4", "HDMI et DisplayPort sur la plaque de la carte mère"),
                ("5", "Prise rectangulaire à 8 contacts avec deux voyants"),
                ("6", "Trois prises rondes 3,5 mm : bleu clair, vert, rose"),
                ("7", "Trois DisplayPort et un HDMI sur l'équerre d'une carte d'extension, sous la plaque"),
            ),
        ),
        instructions=(
            "Pour chaque appareil, indique le repère à utiliser et justifie.",
            "Explique pourquoi l'écran ne doit pas être branché sur le repère 4.",
        ),
        criteria=(
            _c("Branchements", 2.5, "Écran : DisplayPort de la carte graphique (7) ; imprimante : USB 2.0 (1) ou un autre USB ; SSD externe : USB-C 10 Gbit/s (3) ; casque : vert = sortie casque, rose = micro (6) ; réseau : RJ45 (5)."),
            _c("Sorties vidéo", 1.5, "Le repère 4 dépend de la partie graphique du processeur : elle peut être absente ou désactivée quand une carte graphique est installée ; la carte graphique, plus performante, doit piloter l'écran."),
        ),
        correction=(
            "Écran : un DisplayPort de la carte graphique (repère 7). Imprimante : une prise USB 2.0 (repère 1) suffit, une imprimante n'a pas besoin d'un port rapide. SSD externe : la prise USB-C 10 Gbit/s (repère 3), seule à offrir son débit. Casque-micro : jack vert sur la sortie casque, jack rose sur l'entrée micro (repère 6). Réseau : la prise RJ45 à voyants (repère 5).",
            "Les sorties de la plaque de la carte mère (repère 4) ne fonctionnent que si le processeur a une partie graphique intégrée, et elles sont souvent désactivées quand une carte graphique est présente : l'écran resterait noir ou utiliserait la partie graphique la moins performante.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Classer les périphériques d'un bureau",
        question_type="classification",
        requirement_ids=("AP-05", "AP-01"),
        kind=KIND_ID,
        context=(
            "Pour l'inventaire du matériel d'une petite agence, tu dois indiquer pour chaque "
            "périphérique s'il envoie des informations vers l'ordinateur, en reçoit de lui, ou "
            "fait les deux. Chaque appareil est branché sur un PC de bureau."
        ),
        instructions=(
            ("Classe chacun des huit périphériques : périphérique d'entrée, de sortie, ou "
             "d'entrée et de sortie."),
        ),
        criteria=(
            _c("Classement", 4, "Entrée : scanner, webcam, lecteur de codes-barres ; sortie : vidéoprojecteur, haut-parleurs ; entrée et sortie : écran tactile, imprimante multifonction, casque-micro (0,5 pt par périphérique)."),
        ),
        correction=(
            "Entrée (envoient des données au PC) : le scanner, la webcam et le lecteur de codes-barres.",
            "Sortie (reçoivent des données du PC) : le vidéoprojecteur et les haut-parleurs.",
            "Entrée et sortie : l'écran tactile (affiche et capte le toucher), l'imprimante multifonction (imprime et numérise) et le casque-micro (écoute et micro). Tous ont besoin d'un pilote, générique ou fourni par le fabricant.",
        ),
        classification=Classification(
            categories=E11_CATEGORIES,
            elements=(
                "Scanner à plat",
                "Vidéoprojecteur",
                "Écran tactile",
                "Webcam",
                "Imprimante multifonction avec scanner",
                "Haut-parleurs",
                "Lecteur de codes-barres",
                "Casque-micro",
            ),
            correct=(0, 1, 2, 0, 2, 1, 0, 2),
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Une imprimante USB reconnue comme « périphérique inconnu »",
        question_type="long_answer",
        requirement_ids=("AP-05",),
        kind=KIND_SCENARIO,
        context=(
            "Dans un cabinet médical, une imprimante USB neuve est branchée sur un PC sous "
            "Windows 11 64 bits. Elle n'imprime pas ; le Gestionnaire de périphériques affiche "
            "« Périphérique inconnu » avec un triangle jaune. La secrétaire a déjà téléchargé un "
            "pilote sur un site de téléchargement, prévu « pour Windows 32 bits », qui refuse de "
            "s'installer."
        ),
        instructions=(
            "Explique le rôle d'un pilote de périphérique.",
            "Explique pourquoi le pilote téléchargé ne convient pas et le risque de la source utilisée.",
            "Rédige la procédure pour faire fonctionner l'imprimante et la vérification finale.",
        ),
        criteria=(
            _c("Rôle du pilote", 1, "Logiciel qui permet au système d'exploitation de dialoguer avec un matériel précis : il traduit les demandes du système en commandes du périphérique ; sans lui, le matériel est vu mais inutilisable."),
            _c("Pilote inadapté", 1.5, "Un pilote est propre au système et à son architecture : un pilote 32 bits ne s'installe pas sur Windows 64 bits ; un site de téléchargement tiers peut fournir un logiciel modifié ou malveillant."),
            _c("Procédure", 2, "Relever le modèle exact ; pilote du site du fabricant ou de Windows Update pour Windows 11 64 bits ; installer, éventuellement supprimer le périphérique inconnu et le redétecter ; droits administrateur."),
            _c("Vérification", 0.5, "Périphérique reconnu sans triangle dans le Gestionnaire, page de test imprimée."),
        ),
        correction=(
            "Un pilote est le logiciel qui permet au système d'exploitation de dialoguer avec un matériel précis : il traduit les demandes du système (imprimer cette page) en commandes que l'imprimante comprend. Sans pilote, Windows voit qu'un appareil est branché mais ne sait pas l'utiliser : d'où « Périphérique inconnu ».",
            "Le pilote téléchargé est prévu pour Windows 32 bits ; le PC est en 64 bits : un pilote doit correspondre au système et à son architecture. De plus, un site de téléchargement tiers peut fournir une version modifiée ou contenant un logiciel malveillant : on prend le pilote chez le fabricant ou via Windows Update.",
            "Procédure : relever le modèle exact sur l'étiquette ; chercher le pilote sur le site du fabricant pour Windows 11 64 bits (ou laisser Windows Update le proposer) ; l'installer avec un compte administrateur ; si nécessaire, supprimer le « Périphérique inconnu » dans le Gestionnaire puis rebrancher l'imprimante. Vérification : l'imprimante apparaît sous son nom, sans triangle, et une page de test sort correctement.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Répondre à trois questions de client sur le firmware",
        question_type="long_answer",
        requirement_ids=("AP-02", "AP-07"),
        kind=KIND_SCENARIO,
        context=(
            "Au comptoir, un client pose trois questions. 1) « Si je mets à jour le BIOS, est-ce "
            "que je perds mes photos ? » 2) « Mon PC affiche le 1er janvier 2020 à chaque "
            "démarrage, même après l'avoir réglé. » 3) « J'ai remplacé mon disque par un disque "
            "neuf et vide, et l'écran de configuration du PC s'affiche quand même : où est-il "
            "enregistré ? »"
        ),
        instructions=("Réponds à chacune des trois questions en expliquant le rôle du composant concerné.",),
        criteria=(
            _c("Mise à jour du firmware", 1.5, "Le firmware est dans une puce flash de la carte mère, distincte du disque : la mise à jour ne touche pas les photos ; risque réel : une coupure pendant la mise à jour peut rendre la carte inutilisable ; réglages souvent remis par défaut ; sauvegarde des données de toute façon conseillée."),
            _c("Pile CMOS", 1.5, "La pile bouton de la carte maintient l'horloge (et, sur certaines cartes, les réglages) PC débranché ; usée, la date se réinitialise : la remplacer par le même modèle, PC débranché, puis régler date et heure."),
            _c("Firmware hors disque", 1, "L'écran de configuration fait partie du firmware UEFI enregistré dans la puce flash (la « ROM ») de la carte mère : il fonctionne sans disque ; le disque ne contient que le système et les fichiers."),
        ),
        correction=(
            "1) Non. Le firmware (le « BIOS », aujourd'hui UEFI) est enregistré dans une puce de mémoire flash de la carte mère, pas sur le disque : la mise à jour ne touche pas vos photos. Le vrai risque est une coupure de courant pendant l'opération, qui peut rendre la carte inutilisable ; les réglages du firmware peuvent aussi revenir aux valeurs par défaut. Une sauvegarde de vos données reste conseillée avant toute intervention.",
            "2) La pile bouton de la carte mère alimente l'horloge (et, sur certaines cartes, la mémoire des réglages) quand le PC est débranché. Usée, elle ne garde plus la date. On la remplace par le même modèle, PC débranché, avec les précautions antistatiques, puis on règle la date et l'heure.",
            "3) L'écran de configuration fait partie du firmware, enregistré dans la puce flash de la carte mère (on l'appelle encore ROM : mémoire non volatile qui n'est pas modifiée en usage normal). Il s'exécute avant tout disque, avec le POST. Le disque, lui, contient le système et les fichiers : un disque vide ne permet simplement pas de démarrer un système.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Choisir un ventirad pour un processeur",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Tu montes un PC de bureau. Le processeur est en socket AM5, avec une puissance "
            "thermique indiquée de 105 W ; le boîtier accepte un ventirad de 160 mm de haut au "
            "plus. Le fournisseur propose trois ventirads (document 1). Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Ventirads proposés (fictifs)",
                ("Offre", "Sockets pris en charge", "Puissance dissipée annoncée", "Hauteur"),
                ("V1", "AM4, AM5", "150 W", "158 mm"),
                ("V2", "LGA1700", "180 W", "150 mm"),
                ("V3", "AM4, AM5", "65 W", "60 mm"),
            ),
        ),
        instructions=(
            "Choisis le ventirad et justifie le rejet des deux autres.",
            "Cite trois points à respecter lors de son installation.",
        ),
        criteria=(
            _c("Choix", 1, "V1 : prend en charge l'AM5, dissipe 150 W ≥ 105 W, 158 mm ≤ 160 mm."),
            _c("Rejets", 1.5, "V2 : fixation prévue pour LGA1700 seulement, ne se monte pas sur AM5 ; V3 : 65 W, insuffisant pour 105 W (surchauffe, baisse de fréquence)."),
            _c("Installation", 1.5, "Pâte thermique (souvent pré-appliquée ou fine couche), fixation et serrage croisé selon la notice, ventilateur branché sur CPU_FAN, sens du flux d'air vers l'arrière, contrôle de la température au démarrage."),
        ),
        correction=(
            "V1 : il prend en charge le socket AM5, dissipe 150 W, plus que les 105 W du processeur, et mesure 158 mm pour 160 mm au plus dans le boîtier. V2 a un système de fixation prévu pour le socket Intel LGA1700 : il ne se monte pas sur AM5. V3 est compatible AM5 mais ne dissipe que 65 W : le processeur chaufferait et baisserait sa fréquence.",
            "Installation : appliquer la pâte thermique (ou garder celle pré-appliquée), serrer la fixation de manière progressive et croisée selon la notice, brancher le ventilateur sur le connecteur CPU_FAN, orienter le flux d'air vers le ventilateur arrière, puis contrôler la température au premier démarrage.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Rédiger la procédure d'ajout d'une barrette de mémoire",
        question_type="long_answer",
        requirement_ids=("AP-02", "AP-07", "AP-C02"),
        kind=KIND_PROCEDURE,
        context=(
            "Ton responsable te demande de rédiger, pour les stagiaires de l'atelier, la procédure "
            "d'ajout d'une seconde barrette DIMM DDR4 dans un PC de bureau. La carte mère a quatre "
            "emplacements A1, A2, B1, B2 ; une barrette est déjà en A2 ; le manuel indique A2 et "
            "B2 pour deux barrettes."
        ),
        instructions=(
            "Rédige la procédure complète, étape par étape, de la préparation à la vérification.",
            "Justifie chaque précaution liée à l'électricité statique et à la sécurité électrique.",
        ),
        criteria=(
            _c("Préparation et sécurité", 1.5, "Vérifier la compatibilité (DDR4, DIMM, capacité, manuel) ; arrêter le système, débrancher le secteur, appuyer sur le bouton de démarrage pour vider la charge résiduelle."),
            _c("Précautions ESD justifiées", 1.5, "Bracelet relié au châssis ou au tapis antistatique, barrette laissée dans son sachet jusqu'au montage, tenue par les bords sans toucher les contacts : une décharge peut endommager les puces sans trace visible."),
            _c("Insertion", 1, "Slot B2 selon le manuel ; clips ouverts ; encoche alignée sur le détrompeur ; pression verticale des deux côtés jusqu'au verrouillage des clips, sans forcer."),
            _c("Vérification", 1, "Remonter, rebrancher, démarrer : capacité totale détectée dans le firmware et le système (gestionnaire des tâches ou outil d'inventaire), test mémoire si doute ; noter l'intervention."),
        ),
        correction=(
            "1. Préparer : vérifier que la barrette est une DIMM DDR4 compatible avec la carte (manuel, capacité maximale). 2. Arrêter le système, débrancher le cordon secteur, puis appuyer quelques secondes sur le bouton de démarrage pour décharger les condensateurs : on ne travaille jamais sous tension.",
            "3. Se relier à la masse : bracelet antistatique pincé sur le châssis ou relié au tapis antistatique ; laisser la barrette dans son sachet jusqu'au dernier moment et la tenir par les bords, sans toucher les contacts ni les puces. Une décharge électrostatique, même imperceptible, peut endommager les puces sans trace visible.",
            "4. Ouvrir le boîtier, repérer B2 (indiqué par le manuel pour deux barrettes), ouvrir les clips, aligner l'encoche sur le détrompeur, enfoncer verticalement des deux côtés jusqu'à ce que les clips se referment, sans forcer. 5. Refermer, rebrancher, démarrer : vérifier que la capacité totale est détectée dans le firmware puis dans le système ; en cas de doute, lancer un test mémoire. Noter l'intervention dans la fiche du poste.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Contrôler un devis de montage complet",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-07", "AP-02", "AP-01"),
        kind=KIND_CHOICE,
        context=(
            "Un client a composé lui-même la configuration de son futur PC (document 1) et te "
            "demande de la vérifier avant de passer commande. Toutes les fiches sont fictives ; "
            "les valeurs indiquées sont celles des fiches."
        ),
        documents=(
            _table(
                "Document 1 — Configuration proposée par le client (fictive)",
                ("Pièce", "Caractéristiques"),
                ("Processeur", "socket AM5 ; puissance thermique 105 W"),
                ("Carte mère", "socket AM5 ; format ATX ; 4 × DIMM DDR5 ; M.2_1 : NVMe PCIe 4.0 x4 uniquement, 2280 ; 4 × SATA"),
                ("Mémoire", "2 × 16 Go DIMM DDR4-3200"),
                ("SSD", "M.2 SATA, format 2280"),
                ("Carte graphique", "PCIe 4.0 x16 ; 300 mm ; 2 × PCIe 8 broches ; bloc recommandé 650 W"),
                ("Bloc d'alimentation", "750 W ; ATX 24 broches, EPS 8 broches, 2 câbles PCIe 6+2, 4 SATA"),
                ("Boîtier", "mini-tour microATX ; carte graphique 330 mm au plus ; ventirad 165 mm au plus"),
                ("Ventirad", "AM4/AM5 ; 150 W ; 160 mm"),
            ),
        ),
        instructions=(
            "Relève chaque incompatibilité, explique-la et propose la correction.",
            "Liste les pièces que tu as vérifiées et trouvées compatibles, avec le critère contrôlé.",
        ),
        criteria=(
            _c("Mémoire", 1, "DDR4 incompatible avec une carte DDR5 (encoche et tension différentes) : prendre 2 × 16 Go DIMM DDR5."),
            _c("SSD", 1, "M.2 SATA dans un M.2 NVMe uniquement : non détecté ; prendre un SSD NVMe 2280 (ou garder ce SSD si un autre emplacement accepte le SATA)."),
            _c("Boîtier", 1, "Carte ATX (305 × 244 mm) dans un boîtier microATX : impossible ; boîtier ATX ou carte microATX."),
            _c("Pièces compatibles", 2, "Processeur et carte : même socket AM5 ; carte graphique : PCIe x16, 300 mm ≤ 330 mm, 750 W ≥ 650 W et 2 câbles PCIe pour 2 connecteurs ; ventirad : AM5, 150 W ≥ 105 W, 160 mm ≤ 165 mm ; bloc : ATX 24 et EPS présents."),
        ),
        correction=(
            "Trois incompatibilités. Mémoire : la carte accepte la DDR5 ; une barrette DDR4 n'a ni la même encoche ni la même tension et ne s'insère pas : commander 2 × 16 Go DIMM DDR5. SSD : M.2_1 n'accepte que le NVMe ; un M.2 SATA s'y enficherait mais ne serait pas détecté : prendre un SSD NVMe 2280. Boîtier : la carte est ATX (305 × 244 mm) et le boîtier n'accepte que le microATX : choisir un boîtier ATX (ou une carte microATX équivalente).",
            "Compatibles : le processeur et la carte mère ont le même socket AM5 ; la carte graphique (PCIe 4.0 x16) se monte dans le slot x16, mesure 300 mm pour 330 mm au plus, et le bloc de 750 W dépasse les 650 W recommandés avec deux câbles PCIe pour ses deux connecteurs 8 broches ; le ventirad prend en charge l'AM5, dissipe 150 W pour 105 W et mesure 160 mm pour 165 mm au plus ; le bloc fournit l'ATX 24 broches et l'EPS 8 broches. Ces contrôles de boîtier sont à refaire si le client change de boîtier.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions notées sur 2 points (onglet « Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Nommer quatre éléments d'après leur description",
        question_type="document_analysis",
        requirement_ids=("AP-07", "AP-02"),
        kind=KIND_ID,
        context=(
            "Un collègue te transmet la description de quatre éléments d'une carte mère de PC de "
            "bureau (document 1), relevés lors d'un inventaire, et te demande de compléter la fiche."
        ),
        documents=(
            _table(
                "Document 1 — Description des repères (fictive)",
                ("Repère", "Description"),
                ("1", "Connecteur à 8 broches marqué « CPU », près du bord supérieur"),
                ("2", "Fente plate couchée sur la carte, vis de maintien à 80 mm"),
                ("3", "Petite puce à 8 pattes, à côté de la pile bouton"),
                ("4", "Connecteur à 19 broches sur deux rangées, sur le bord, relié à un câble venant de la façade"),
            ),
        ),
        instructions=("Nomme chaque élément et donne son rôle en une phrase.",),
        criteria=(
            _c("Repère 1", 0.5, "Connecteur EPS 8 broches : alimentation du processeur (via le VRM)."),
            _c("Repère 2", 0.5, "Emplacement M.2 (module 2280) : SSD NVMe ou SATA selon le manuel."),
            _c("Repère 3", 0.5, "Puce flash du firmware UEFI (BIOS) : contient le programme de démarrage et de configuration."),
            _c("Repère 4", 0.5, "Connecteur interne USB 3.x : relie les ports USB 3 de la façade à la carte."),
        ),
        correction=(
            "1 : connecteur EPS 8 broches, qui alimente le processeur à travers le VRM. 2 : emplacement M.2 pour un module 2280, qui reçoit un SSD (NVMe ou SATA selon le manuel). 3 : la puce de mémoire flash qui contient le firmware UEFI. 4 : le connecteur interne USB 3.x (19 broches), qui relie les ports USB 3 de la façade à la carte mère.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un PC sans disque affiche son écran de configuration",
        question_type="short_answer",
        requirement_ids=("AP-02", "AP-01"),
        kind=KIND_SCENARIO,
        context=(
            "Un PC de bureau dont le disque a été retiré pour être remplacé affiche quand même "
            "l'écran de configuration UEFI à l'allumage, avec la quantité de mémoire vive "
            "installée. Le client ne comprend pas « où est enregistré ce programme » puisqu'il n'y "
            "a plus de disque."
        ),
        instructions=(
            ("Explique au client, en distinguant la mémoire vive, la mémoire du firmware et le "
             "stockage, pourquoi cet écran s'affiche et ce qui manque pour démarrer un système."),
        ),
        criteria=(
            _c("Firmware", 0.8, "Le programme de configuration est le firmware UEFI, stocké dans une puce flash (ROM) non volatile de la carte mère, exécuté au POST sans disque."),
            _c("Mémoire vive", 0.6, "La RAM est volatile : mémoire de travail détectée et testée au POST, elle ne garde rien à l'extinction."),
            _c("Stockage", 0.6, "Le disque (stockage de masse) contient le système et les fichiers ; sans lui, le firmware ne trouve rien à démarrer."),
        ),
        correction=(
            "L'écran vient du firmware UEFI, enregistré dans une puce de mémoire flash de la carte mère (la « ROM »), non volatile : il s'exécute dès l'allumage, avec le POST, sans aucun disque. La mémoire vive, elle, est volatile : c'est la mémoire de travail, détectée et comptée au POST, vide à chaque démarrage. Le disque est le stockage de masse : il contient le système et les fichiers ; sans lui, le firmware n'a aucun système à démarrer.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Passer un PC de bureau à 32 Go",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Un graphiste veut passer son PC de bureau de 16 à 32 Go de mémoire vive en gardant "
            "les barrettes en place. Le document 1 décrit sa carte et les offres du fournisseur. "
            "Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Carte mère et offres (fictives)",
                ("Élément", "Valeur"),
                ("Carte mère", "4 × DIMM DDR5 ; 128 Go au plus ; A2 et B2 occupés par 2 × 8 Go DDR5-5600"),
                ("Offre A", "kit 2 × 8 Go DIMM DDR5-5600"),
                ("Offre B", "kit 2 × 16 Go DIMM DDR4-3200"),
                ("Offre C", "kit 2 × 8 Go SO-DIMM DDR5-5600"),
            ),
        ),
        instructions=("Choisis l'offre, justifie le rejet des deux autres et indique les emplacements à utiliser.",),
        criteria=(
            _c("Choix", 0.6, "Offre A : DIMM DDR5 de même fréquence ; 4 × 8 Go = 32 Go, sous les 128 Go maximum."),
            _c("Rejets", 0.8, "B : DDR4, ne s'insère pas dans un slot DDR5 ; C : SO-DIMM, format portable, trop court pour un slot DIMM."),
            _c("Emplacements", 0.6, "A1 et B1, libres ; vérifier la liste de compatibilité ou le manuel (la fréquence peut baisser avec quatre barrettes) ; contrôle de la capacité détectée."),
        ),
        correction=(
            "Offre A : deux DIMM DDR5-5600 de 8 Go, identiques aux barrettes en place ; avec les quatre emplacements occupés, on obtient 32 Go, bien sous le maximum de 128 Go. B est en DDR4 : l'encoche et la tension diffèrent, elle ne s'insère pas. C est au format SO-DIMM des portables : trop courte pour un emplacement DIMM. On installe le kit en A1 et B1, en vérifiant le manuel (avec quatre barrettes, la fréquence peut être abaissée), puis on contrôle que 32 Go sont détectés.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Copier des fichiers d'un disque USB vers le disque interne",
        question_type="document_analysis",
        requirement_ids=("AP-01", "AP-07"),
        kind=KIND_INVENTORY,
        context=(
            "Un client copie 200 Go de photos d'un disque externe USB vers le disque dur interne "
            "SATA de son PC de bureau et trouve la copie lente. Le document 1 reprend les "
            "caractéristiques relevées. Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Relevé (fictif)",
                ("Élément", "Caractéristique"),
                ("Disque externe", "SSD USB 3.2 Gen 1, branché sur un port USB 5 Gbit/s"),
                ("Port USB utilisé", "géré par le chipset"),
                ("Disque interne", "disque dur à plateaux SATA 6 Gbit/s ; débit séquentiel annoncé : 200 Mo/s"),
            ),
        ),
        instructions=(
            "Décris le trajet des données entre les deux disques, composant par composant.",
            "Indique l'élément qui limite la vitesse de copie et justifie.",
        ),
        criteria=(
            _c("Trajet", 1.2, "Disque externe → port USB → chipset → liaison chipset-processeur → processeur et mémoire vive → chipset → port SATA → disque dur."),
            _c("Élément limitant", 0.8, "Le disque dur (200 Mo/s), plus lent que l'USB 5 Gbit/s (environ 500 Mo/s utiles) et que le SATA 6 Gbit/s : c'est le maillon le plus lent qui fixe la vitesse."),
        ),
        correction=(
            "Trajet : les données sortent du disque externe par le port USB, géré par le chipset ; elles remontent par la liaison chipset-processeur jusqu'au processeur, qui les place en mémoire vive ; elles repartent vers le chipset, puis par le port SATA jusqu'au disque dur.",
            "Le maillon le plus lent fixe la vitesse : le disque dur écrit à 200 Mo/s environ, alors que l'USB 5 Gbit/s permet environ 500 Mo/s utiles et le SATA 6 Gbit/s 600 Mo/s. Ce n'est pas une panne : c'est la limite du disque dur.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Choisir un format de carte mère pour un petit boîtier",
        question_type="short_answer",
        requirement_ids=("AP-17", "AP-07"),
        kind=KIND_SCENARIO,
        context=(
            "Une association veut un PC compact pour sa salle de montage vidéo. Il doit recevoir "
            "une carte graphique et une carte d'acquisition vidéo, deux cartes d'extension PCIe. "
            "Le vendeur propose un boîtier Mini-ITX très compact ou un boîtier microATX un peu "
            "plus grand."
        ),
        instructions=("Indique le format de carte mère et le boîtier à choisir, en justifiant avec les caractéristiques des formats.",),
        criteria=(
            _c("Mini-ITX écarté", 1, "Mini-ITX (170 × 170 mm) : un seul emplacement d'extension, pas de place pour deux cartes."),
            _c("Choix justifié", 1, "microATX (244 × 244 mm au plus, jusqu'à 4 emplacements) dans le boîtier microATX ; vérifier le nombre réel d'emplacements et l'épaisseur de la carte graphique."),
        ),
        correction=(
            "Le Mini-ITX (170 × 170 mm) n'a qu'un emplacement d'extension : impossible d'y mettre deux cartes. On choisit une carte microATX (244 × 244 mm au plus, jusqu'à quatre emplacements) dans le boîtier microATX, en vérifiant sur la fiche que la carte choisie a bien deux emplacements utilisables, même avec une carte graphique épaisse.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Écran noir après l'installation d'une carte graphique",
        question_type="short_answer",
        requirement_ids=("AP-01", "AP-05"),
        kind=KIND_SCENARIO,
        context=(
            "Un client vient d'installer une carte graphique dans son PC de bureau. Il a laissé le "
            "câble HDMI de l'écran branché sur la prise HDMI de la plaque arrière de la carte mère, "
            "comme avant. Les ventilateurs tournent mais l'écran affiche « Aucun signal »."
        ),
        instructions=("Explique la cause probable et la correction, puis ce qu'il reste à installer côté logiciel.",),
        criteria=(
            _c("Cause", 0.8, "Les sorties de la carte mère dépendent de la partie graphique du processeur, désactivée (ou absente) quand une carte graphique est installée : la vidéo sort par la carte graphique."),
            _c("Correction", 0.7, "Brancher l'écran sur une sortie de la carte graphique (équerre sous la plaque d'E/S), vérifier son alimentation PCIe si elle en a."),
            _c("Logiciel", 0.5, "Installer le pilote de la carte graphique (fabricant), vérifier la résolution."),
        ),
        correction=(
            "Les sorties vidéo de la carte mère sont pilotées par la partie graphique du processeur ; quand une carte graphique est installée, le firmware l'utilise en priorité et ces sorties sont souvent désactivées (ou le processeur n'en a pas). Il faut brancher l'écran sur une sortie de la carte graphique, sur l'équerre sous la plaque d'E/S, et vérifier que ses connecteurs d'alimentation PCIe sont branchés. Ensuite, installer le pilote de la carte graphique du fabricant et vérifier la résolution.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Brancher un SSD externe 10 Gbit/s",
        question_type="document_analysis",
        requirement_ids=("AP-05", "AP-01", "AP-06"),
        kind=KIND_ID,
        context=(
            "Un photographe achète un SSD externe USB 3.2 Gen 2 (10 Gbit/s) avec un câble USB-C. "
            "Il le branche sur la prise USB-C de la façade de son PC et trouve les copies plus "
            "lentes qu'annoncé. Le document 1 reprend le manuel du PC (fictif)."
        ),
        documents=(
            _table(
                "Document 1 — Ports USB du PC (extrait du manuel, fictif)",
                ("Emplacement", "Port", "Norme"),
                ("Façade", "1 × USB-C", "USB 3.2 Gen 1 (5 Gbit/s)"),
                ("Façade", "2 × USB-A", "USB 2.0"),
                ("Arrière", "1 × USB-C", "USB 3.2 Gen 2 (10 Gbit/s)"),
                ("Arrière", "4 × USB-A bleus", "USB 3.2 Gen 1 (5 Gbit/s)"),
            ),
        ),
        instructions=("Explique la lenteur et indique le port à utiliser.",),
        criteria=(
            _c("Explication", 1.2, "USB-C désigne la forme du connecteur, pas le débit : la prise USB-C de façade est en 5 Gbit/s, elle bride le SSD à 10 Gbit/s."),
            _c("Port", 0.8, "La prise USB-C arrière, USB 3.2 Gen 2 à 10 Gbit/s, avec un câble qui supporte ce débit."),
        ),
        correction=(
            "USB-C est seulement la forme du connecteur : le débit dépend de la norme du port. La prise USB-C de façade est en USB 3.2 Gen 1, à 5 Gbit/s : elle divise par deux le débit possible du SSD. Il faut utiliser la prise USB-C arrière, en USB 3.2 Gen 2 à 10 Gbit/s, avec le câble fourni (prévu pour ce débit).",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Webcam sans pilote après une réinstallation",
        question_type="short_answer",
        requirement_ids=("AP-05",),
        kind=KIND_SCENARIO,
        context=(
            "Après la réinstallation de Windows sur un PC de bureau, la webcam USB d'une employée ne "
            "fonctionne plus. Le Gestionnaire de périphériques l'affiche sous « Autres "
            "périphériques » avec un triangle jaune. Le câble et le port fonctionnent avec un autre "
            "appareil."
        ),
        instructions=("Explique le rôle d'un pilote et rédige la démarche pour remettre la webcam en service, avec la vérification.",),
        criteria=(
            _c("Rôle du pilote", 0.6, "Logiciel qui permet au système de dialoguer avec ce matériel ; la réinstallation a supprimé celui de la webcam."),
            _c("Démarche", 1, "Identifier le modèle ; pilote du fabricant pour la bonne version et architecture du système, ou Windows Update ; installation avec droits administrateur ; mettre à jour ou réinstaller depuis le Gestionnaire."),
            _c("Vérification", 0.4, "Webcam reconnue sans triangle, image dans l'application Caméra ou de visioconférence, autorisation d'accès à la caméra activée."),
        ),
        correction=(
            "Un pilote est le logiciel qui permet au système d'exploitation de dialoguer avec un matériel précis ; la réinstallation l'a supprimé, d'où le triangle jaune. Démarche : relever le modèle de la webcam, récupérer le pilote sur le site du fabricant pour la bonne version et l'architecture de Windows (ou via Windows Update), l'installer avec un compte administrateur, puis actualiser le périphérique dans le Gestionnaire. Vérification : la webcam apparaît sous son nom, sans triangle, et donne une image dans l'application Caméra, l'accès à la caméra étant autorisé dans les paramètres de confidentialité.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Choisir un processeur pour un PC sans carte graphique",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Une école monte des PC de bureautique sans carte graphique : l'écran sera branché sur "
            "la sortie HDMI de la carte mère. La carte mère est en socket LGA1700. Le fournisseur "
            "propose trois processeurs (document 1). Fiches fictives."
        ),
        documents=(
            _table(
                "Document 1 — Processeurs proposés (fictifs)",
                ("Offre", "Caractéristiques"),
                ("Q1", "socket LGA1700 ; sans partie graphique intégrée"),
                ("Q2", "socket LGA1700 ; partie graphique intégrée"),
                ("Q3", "socket LGA1851 ; partie graphique intégrée"),
            ),
        ),
        instructions=("Choisis le processeur et justifie le rejet des deux autres ; indique ce qu'il faut encore vérifier.",),
        criteria=(
            _c("Choix", 0.6, "Q2 : bon socket et partie graphique intégrée, indispensable sans carte graphique."),
            _c("Rejets", 0.9, "Q1 : sans partie graphique, la sortie HDMI de la carte mère ne donnerait aucune image ; Q3 : socket LGA1851, ne rentre pas dans un LGA1700."),
            _c("Vérification", 0.5, "Liste des processeurs pris en charge par la carte et version minimale du firmware ; ventirad adapté."),
        ),
        correction=(
            "Q2 : il est au bon socket (LGA1700) et possède une partie graphique intégrée, indispensable puisque l'écran se branche sur la carte mère. Q1 n'a pas de partie graphique : la sortie HDMI de la carte mère resterait noire sans carte graphique. Q3 est en socket LGA1851 : il ne s'installe pas dans un socket LGA1700. Il reste à vérifier la liste des processeurs pris en charge par la carte (et la version de firmware minimale) et le ventirad.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Justifier les précautions avant d'installer une carte d'extension",
        question_type="short_answer",
        requirement_ids=("AP-07", "AP-C02"),
        kind=KIND_PROCEDURE,
        context=(
            "Tu dois installer une carte réseau PCIe x1 dans un PC de bureau, dans une salle à "
            "moquette, par temps sec. Ton stagiaire veut l'installer PC allumé « pour voir tout de "
            "suite si elle marche » et sort la carte de son sachet pour la poser sur le bureau."
        ),
        instructions=("Cite quatre précautions à prendre et justifie chacune.",),
        criteria=(
            _c("Hors tension", 0.6, "PC arrêté et débranché, bouton maintenu pour décharger : l'insertion sous tension peut détruire la carte ou la carte mère et expose au risque électrique."),
            _c("Masse et ESD", 0.6, "Bracelet relié au châssis ou au tapis antistatique : la moquette et l'air sec favorisent les décharges qui abîment les composants sans trace visible."),
            _c("Manipulation", 0.4, "Carte gardée dans son sachet jusqu'au montage, tenue par les bords et l'équerre, sans toucher les contacts dorés."),
            _c("Montage et contrôle", 0.4, "Slot PCIe x1 (ou plus long) libre, équerre retirée, carte enfoncée droite et vissée ; puis pilote et test du réseau."),
        ),
        correction=(
            "1. Hors tension : arrêter, débrancher le secteur, appuyer sur le bouton pour décharger ; l'insertion sous tension peut détruire la carte ou la carte mère. 2. Antistatique : bracelet relié au châssis ou au tapis ; moquette et air sec favorisent les décharges électrostatiques, qui abîment les composants sans trace visible. 3. Manipulation : laisser la carte dans son sachet antistatique jusqu'au montage et la tenir par les bords et l'équerre, jamais par les contacts. 4. Montage : slot PCIe x1 (ou plus long) libre, équerre de fermeture retirée, carte enfoncée droite et vissée ; puis pilote et test de la connexion réseau.",
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

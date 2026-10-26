"""PR05 « Stockage, partitions, formatage et défragmentation » — exercices corrigés et
mini-examen (ticket #206).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item, et `app.v1.ampcr_pratique_pr04_bank`, dont il réutilise les
petits constructeurs) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre, choix du système de fichiers, de la table de
  partitions et de l'entretien adapté au support, plans de partitions chiffrés, calculs Go/Gio,
  lecture de captures et de relevés SMART, symptômes, procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, captures et relevés sont **fictifs** ; procédures, choix, capacités et
verdicts viennent de `app.v1.ampcr_pratique_pr05_figures` (mêmes données que les schémas).
Aucune opération destructive n'est demandée sans sauvegarde vérifiée préalable.
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr05_figures import (
    FRAGMENTATION_ALERT,
    FS_EXFAT,
    FS_EXT4,
    FS_FAT32,
    FS_NTFS,
    GB,
    GIB,
    LINUX_NEW_DISK_STEPS,
    MBR_LIMIT_BYTES,
    MEDIA_HDD,
    MEDIA_SATA_SSD,
    SAFE_STEPS,
    TABLE_GPT,
    TABLE_MBR,
    TB,
    USE_ESP,
    USE_LEGACY_DEVICE,
    USE_LINUX,
    USE_SHARED_REMOVABLE,
    USE_WINDOWS_DATA,
    USE_WINDOWS_SYSTEM,
    WIN_NEW_DISK_STEPS,
    boot_mode_consistent,
    filesystem_for,
    fr_number,
    gb_to_gib,
    needs_defrag,
    partition_table_choice,
    plan_fits,
    smart_lines,
    smart_reading,
)
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)

PR05_CODE = "PR05"

KIND_ORDER = "ordonnancement"
KIND_CHOICE = "choix et plan de partitions"
KIND_CALC = "capacités et unités"
KIND_DIAG = "diagnostic et relevés"
KIND_ERROR = "repérage d'erreurs"

# Exigence officielle du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-03"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(SAFE_STEPS)
E02_STEPS = _labels(WIN_NEW_DISK_STEPS)
E03_STEPS = _labels(LINUX_NEW_DISK_STEPS)

E04_CATEGORIES = (FS_NTFS, FS_FAT32, FS_EXFAT, FS_EXT4)
# (support et usage, usage du cours, plus gros fichier en octets)
E04_ELEMENTS: tuple[tuple[str, str, int], ...] = (
    ("Partition C: d'un PC neuf sous Windows 11", USE_WINDOWS_SYSTEM, 0),
    ("Partition racine / d'un serveur Debian", USE_LINUX, 0),
    ("Partition EFI (ESP) d'un PC qui démarre en UEFI", USE_ESP, 0),
    ("Clé USB de 128 Go pour échanger des vidéos de 6 Go entre un PC Windows et un Mac", USE_SHARED_REMOVABLE, 6 * GB),
    ("Clé USB de 16 Go pour mettre à jour le firmware d'une carte mère dont l'outil ne lit que FAT32 (fichier de 32 Mo)",
     USE_LEGACY_DEVICE, 32 * 2**20),
    ("Disque externe de 2 To réservé aux sauvegardes d'un PC Windows, avec droits d'accès sur les dossiers",
     USE_WINDOWS_DATA, 0),
    ("Carte SD de 64 Go d'un appareil photo, lue sous Windows, macOS et Linux", USE_SHARED_REMOVABLE, 0),
    ("Partition /home séparée d'un portable Ubuntu", USE_LINUX, 0),
)
E04_CORRECT = tuple(
    E04_CATEGORIES.index(filesystem_for(use, largest_file_bytes=size)) for _l, use, size in E04_ELEMENTS
)

E05_HDD = "Disque dur seulement"
E05_SSD = "SSD seulement"
E05_BOTH = "Les deux"
E05_CATEGORIES = (E05_HDD, E05_SSD, E05_BOTH)
E05_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Une défragmentation régulière améliore les performances", E05_HDD),
    ("Le système envoie la commande TRIM pour signaler les blocs libérés", E05_SSD),
    ("Le contrôleur répartit les écritures sur toutes les cellules (répartition de l'usure)", E05_SSD),
    ("Un choc pendant le fonctionnement peut abîmer les têtes de lecture", E05_HDD),
    ("L'état SMART se lit attribut par attribut avant toute intervention", E05_BOTH),
    ("Les données se sauvegardent et la copie se vérifie avant de repartitionner", E05_BOTH),
    ("Le temps d'accès de plusieurs millisecondes vient de la rotation des plateaux", E05_HDD),
    ("L'endurance est donnée en téraoctets écrits (TBW)", E05_SSD),
)

E06_CATEGORIES = (TABLE_GPT, TABLE_MBR)
# (situation, taille du disque, disque de démarrage, PC UEFI)
E06_CASES: tuple[tuple[str, int, bool, bool], ...] = (
    ("Disque de données de 4 To ajouté à un PC de bureau récent (UEFI)", 4 * TB, False, True),
    ("Disque système d'un PC neuf livré avec Windows 11 (UEFI)", 1 * TB, True, True),
    ("Disque système de 500 Go d'un ancien PC sans UEFI (BIOS uniquement), pour Windows 10", 500 * GB, True, False),
    ("Disque de 1 To d'un PC UEFI sur lequel l'utilisateur veut six partitions", 1 * TB, False, True),
    ("Disque de données de 3 To ajouté à un ancien PC sans UEFI ; Windows 10 reste sur l'autre disque",
     3 * TB, False, False),
    ("Disque système de 250 Go d'un PC de 2008 sans UEFI, pour installer Linux", 250 * GB, True, False),
)
E06_CORRECT = tuple(
    E06_CATEGORIES.index(partition_table_choice(disk_bytes=size, boots_os=boot, firmware_uefi=uefi))
    for _s, size, boot, uefi in E06_CASES
)

# E07 : capacités annoncées et affichées.
E07_HDD_GIB = gb_to_gib(1000)  # 931,32
E07_SSD_GIB = gb_to_gib(500)  # 465,66

# E08 : SSD NVMe de 1 To, Windows en UEFI + partition D: de 300 Gio sur le même SSD.
E08_D_MIB = 300 * 1024
E08_C_GIB = plan_fits(gb_to_gib(1000), (100, 16, 750, E08_D_MIB))

# E09 : SSD de 256 Go, Ubuntu en UEFI avec /home séparé.
E09_FIXED_MIB = (512, 50 * 1024, 4 * 1024)
E09_HOME_GIB = plan_fits(gb_to_gib(256), E09_FIXED_MIB)

# E12 : « Optimiser les lecteurs » d'un poste de comptabilité.
E12_ROWS: tuple[tuple[str, str, int | None], ...] = (
    ("C:", MEDIA_SATA_SSD, None),
    ("D:", MEDIA_HDD, 4),
    ("E:", MEDIA_HDD, 34),
)
E12_DEFRAG = tuple(d for d, media, frag in E12_ROWS if frag is not None and needs_defrag(media, frag))

# E13 : relevé SMART d'un disque à repartitionner.
E13_SMART: tuple[tuple[str, int], ...] = (
    ("Power_On_Hours", 29870),
    ("Reallocated_Sector_Ct", 56),
    ("Current_Pending_Sector", 12),
    ("Offline_Uncorrectable", 12),
    ("UDMA_CRC_Error_Count", 0),
)
E13_VERDICT, E13_CABLE = smart_reading(dict(E13_SMART))

# E15 : disque GPT, firmware passé en mode hérité (CSM).
E15_OK_BEFORE = boot_mode_consistent(TABLE_GPT, "UEFI")
E15_OK_AFTER = boot_mode_consistent(TABLE_GPT, "BIOS")

# Examen : X02, X04, X06, X09.
X02_GIB = gb_to_gib(2000)
X04_DISK = 3 * TB
X04_DISK_GIB = round(X04_DISK / GIB, 2)  # 2793,97
X04_MBR_GIB = round(MBR_LIMIT_BYTES / GIB, 2)  # 2048
X04_LOST_GIB = round((X04_DISK - MBR_LIMIT_BYTES) / GIB, 2)
X06_SMART: tuple[tuple[str, int], ...] = (
    ("Reallocated_Sector_Ct", 0),
    ("Current_Pending_Sector", 0),
    ("Offline_Uncorrectable", 0),
    ("UDMA_CRC_Error_Count", 214),
)
X06_VERDICT, X06_CABLE = smart_reading(dict(X06_SMART))
X09_SMART: tuple[tuple[str, int], ...] = (
    ("Power_On_Hours", 17420),
    ("Reallocated_Sector_Ct", 12),
    ("Current_Pending_Sector", 0),
    ("Offline_Uncorrectable", 0),
    ("UDMA_CRC_Error_Count", 0),
)
X09_VERDICT, X09_CABLE = smart_reading(dict(X09_SMART))


def _gib(value: float, digits: int = 2) -> str:
    return fr_number(value, digits)


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre les précautions avant d'agir sur un disque",
        question_type="ordering",
        requirement_ids=("AP-03", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Un client demande d'agrandir la partition C: de son PC de bureau en prenant de "
            "la place sur la partition D:, qui contient ses photos de famille. Avant de "
            "toucher aux partitions, ton responsable veut la liste des précautions dans "
            "l'ordre. Le stagiaire les a notées, mais mélangées."
        ),
        instructions=("Remets les sept étapes dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Identifier le disque → lire l'état SMART → sauvegarder → vérifier la copie → noter l'état actuel → agir → contrôler."),
        ),
        correction=(
            "1. Identifier le disque (modèle, capacité, numéro dans Gestion des disques) : une opération lancée sur le mauvais disque est la première cause de perte. 2. Lire l'état SMART : un disque qui faiblit se copie d'abord, on ne le sollicite pas avec un redimensionnement. 3. Sauvegarder, avec l'accord écrit du client, et 4. vérifier la copie en ouvrant des fichiers.",
            "5. Noter l'état actuel (capture des partitions) pour pouvoir comparer. 6. Agir, une opération à la fois, en relisant la sélection. 7. Contrôler : tailles, lettres, espace libre, photos toujours présentes.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 6, 1, 4, 0, 5, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'ajout d'un disque de données sous Windows",
        question_type="ordering",
        requirement_ids=("AP-03",),
        kind=KIND_ORDER,
        context=(
            "Une graphiste manque de place : tu ajoutes un disque dur neuf de 4 To dans sa "
            "tour Windows 11 (PC UEFI) pour y ranger ses archives. Tu rédiges pour le dossier "
            "d'intervention la procédure complète, de l'installation physique au contrôle "
            "final ; les étapes ont été mélangées."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Installer → vérifier l'UEFI → ouvrir Gestion des disques → initialiser en GPT → nouveau volume simple → formater → contrôler."),
        ),
        correction=(
            "1. Installer hors tension (fixation, câble de données SATA, alimentation). 2. Vérifier que l'UEFI voit le disque : sinon le problème est matériel et Windows n'y pourra rien. 3. Gestion des disques affiche le disque « Non initialisé ». 4. L'initialiser en GPT (PC UEFI, et 4 To dépasse la limite de 2 Tio du MBR).",
            "5. Créer un nouveau volume simple dans l'espace non alloué, avec une lettre (D:). 6. Le formater en NTFS (disque Windows), nom « Archives », formatage rapide suffisant pour un disque neuf. 7. Contrôler : lecteur visible, capacité d'environ 3 725 Go affichée, fichier test écrit et relu.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 6, 0, 3, 5, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la préparation d'un disque sous Linux",
        question_type="ordering",
        requirement_ids=("AP-03", "AP-11"),
        kind=KIND_ORDER,
        context=(
            "Sur le serveur Linux d'une petite association, tu ajoutes un disque neuf qui "
            "doit être monté automatiquement sur /srv/donnees à chaque démarrage. Le disque "
            "système est un SSD NVMe. Ta fiche de commandes a été mélangée ; remets-la en "
            "ordre avant de l'exécuter."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Repérer le disque (lsblk) → créer la table GPT → créer la partition → formater en ext4 → monter → rendre permanent (fstab, UUID) → contrôler."),
        ),
        correction=(
            "1. lsblk -f d'abord : on repère le nouveau disque (sans partition, bonne taille) et on vérifie qu'il ne s'agit pas du disque système nvme0n1. 2. parted mklabel gpt crée la table (sur un disque vide uniquement). 3. mkpart crée la partition sur tout le disque. 4. mkfs.ext4 la formate.",
            "5. On crée le dossier et on monte la partition pour tester. 6. On lit l'UUID avec blkid et on ajoute la ligne dans /etc/fstab, puis sudo mount -a : une erreur de syntaxe se voit tout de suite, pas au redémarrage. 7. df -h confirme la taille ; un redémarrage confirme le montage automatique.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 5, 0, 6, 3, 1, 4)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Choisir le système de fichiers selon l'usage",
        question_type="classification",
        requirement_ids=("AP-03",),
        kind=KIND_CHOICE,
        context=(
            "L'atelier prépare plusieurs supports pour des clients différents. Pour chacun, "
            "le système de fichiers dépend du système qui l'utilise, des appareils qui doivent "
            "le lire et de la taille des plus gros fichiers. Rappel du cours : FAT32 refuse "
            "tout fichier de plus de 4 Gio."
        ),
        instructions=("Range chacun des huit supports dans le système de fichiers à utiliser.",),
        criteria=(
            _c("Classement", 4, "NTFS : C: Windows 11, disque de sauvegarde Windows. FAT32 : partition EFI, clé de mise à jour du firmware. exFAT : clé vidéo Windows/Mac, carte SD. ext4 : racine Debian, /home Ubuntu (0,5 pt par élément)."),
        ),
        correction=(
            "NTFS pour Windows : journalisation, droits d'accès, fichiers de grande taille — partition C: et disque de sauvegarde qui a besoin de droits sur les dossiers. ext4 pour les partitions Linux (racine, /home).",
            "FAT32 quand le lecteur ne connaît que lui : la partition EFI (exigée par l'UEFI) et la clé de mise à jour du firmware (fichier de 32 Mo, bien sous la limite de 4 Gio). exFAT pour les supports échangés entre Windows, macOS et Linux avec de gros fichiers : la vidéo de 6 Go ne passe pas en FAT32 ; la carte SD de 64 Go est aussi en exFAT.",
        ),
        classification=Classification(
            categories=E04_CATEGORIES,
            elements=tuple(label for label, _u, _s in E04_ELEMENTS),
            correct=E04_CORRECT,
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Disque dur, SSD ou les deux ?",
        question_type="classification",
        requirement_ids=("AP-03",),
        kind=KIND_CHOICE,
        context=(
            "Pour la fiche d'entretien de l'atelier, un collègue a noté des affirmations sur "
            "les supports de stockage, sans préciser à quel type de support elles "
            "s'appliquent. Certaines ne valent que pour le disque dur (plateaux, têtes), "
            "d'autres que pour le SSD (mémoire flash), d'autres pour les deux."
        ),
        instructions=("Range chacune des huit affirmations : disque dur seulement, SSD seulement, ou les deux.",),
        criteria=(
            _c("Classement", 4, "Disque dur : défragmentation, chocs et têtes, temps d'accès dû à la rotation. SSD : TRIM, répartition de l'usure, endurance en TBW. Les deux : lecture SMART, sauvegarde vérifiée avant de repartitionner (0,5 pt par élément)."),
        ),
        correction=(
            "Disque dur : les fichiers fragmentés obligent les têtes à se déplacer, d'où l'intérêt de la défragmentation ; les têtes volent au-dessus des plateaux, un choc en marche peut les abîmer ; la rotation impose plusieurs millisecondes d'accès.",
            "SSD : TRIM signale les blocs libérés pour que le contrôleur les efface à l'avance ; la répartition de l'usure et l'endurance en téraoctets écrits viennent des cycles d'écriture limités de la mémoire flash. Les deux : l'état SMART et la sauvegarde vérifiée avant toute opération sur les partitions.",
        ),
        classification=Classification(
            categories=E05_CATEGORIES,
            elements=tuple(e for e, _c2 in E05_ELEMENTS),
            correct=tuple(E05_CATEGORIES.index(c) for _e, c in E05_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Table de partitions : GPT ou MBR ?",
        question_type="classification",
        requirement_ids=("AP-03", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Avant de préparer six disques vides (données sauvegardées), tu dois choisir leur "
            "table de partitions. Rappels du cours : MBR gère au plus 2 Tio et 4 partitions "
            "principales ; un PC sans UEFI ne démarre que d'un disque MBR ; Windows sait lire "
            "un disque de données GPT même sur un ancien PC."
        ),
        instructions=("Range chaque disque dans la table de partitions à créer.",),
        criteria=(
            _c("Classement", 3, "GPT : 4 To de données, Windows 11, six partitions, 3 To de données sur ancien PC. MBR : disque système Windows 10 sur PC BIOS, disque système Linux sur PC de 2008 (0,5 pt par élément)."),
        ),
        correction=(
            "GPT dès que le PC démarre en UEFI (Windows 11 l'impose pour son disque système), dès que le disque dépasse 2 Tio (4 To, 3 To) ou qu'il faut plus de 4 partitions principales. Le disque de 3 To de l'ancien PC ne sert pas au démarrage : GPT est lisible par Windows 10 et permet d'utiliser toute la capacité.",
            "MBR seulement pour le disque de démarrage d'un PC sans UEFI (BIOS uniquement) : Windows 10 sur le PC BIOS et Linux sur le PC de 2008 ; leurs disques (500 Go et 250 Go) restent sous la limite de 2 Tio.",
        ),
        classification=Classification(
            categories=E06_CATEGORIES,
            elements=tuple(s for s, *_rest in E06_CASES),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="« Il manque 69 Go sur mon disque ! »",
        question_type="short_answer",
        requirement_ids=("AP-03",),
        kind=KIND_CALC,
        context=(
            "Un client a acheté un disque dur vendu « 1 To » et un SSD vendu « 500 Go ». "
            f"Windows affiche {_gib(E07_HDD_GIB)} Go pour le premier et {_gib(E07_SSD_GIB)} Go "
            "pour le second. Il pense avoir été trompé et demande une explication écrite "
            "chiffrée avant de rapporter les disques au magasin."
        ),
        instructions=(
            "Explique l'écart et montre le calcul pour le disque de 1 To.",
            "Calcule la valeur que Windows affichera pour le SSD et dis si le client doit rapporter ses disques.",
        ),
        criteria=(
            _c("Explication", 1, "Le fabricant compte en Go décimaux (1 Go = 10^9 octets) ; Windows compte en Gio (1 Gio = 2^30 = 1 073 741 824 octets) mais affiche « Go »."),
            _c("Calculs", 1, f"10^12 ÷ 2^30 ≈ {_gib(E07_HDD_GIB)} ; 500 × 10^9 ÷ 2^30 ≈ {_gib(E07_SSD_GIB)}."),
            _c("Conclusion", 1, "Aucune capacité manquante : même nombre d'octets, deux unités ; rien à rapporter."),
        ),
        correction=(
            "Le fabricant compte en unités décimales : 1 To = 1 000 000 000 000 octets, 1 Go = 1 000 000 000 octets. Windows divise par 1 073 741 824 (2^30, un gibioctet ou Gio) mais écrit « Go ».",
            f"Disque dur : 1 000 000 000 000 ÷ 1 073 741 824 ≈ {_gib(E07_HDD_GIB)} Gio. SSD : 500 000 000 000 ÷ 1 073 741 824 ≈ {_gib(E07_SSD_GIB)} Gio. Il ne manque aucun octet : c'est la même capacité exprimée dans deux unités. Il n'y a rien à rapporter.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Plan de partitions d'un SSD Windows avec une partition de données",
        question_type="long_answer",
        requirement_ids=("AP-03", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Un indépendant reçoit un PC UEFI avec un SSD NVMe vide vendu « 1 To ». Il veut "
            "Windows 11 et une partition D: de 300 Gio séparée pour ses dossiers clients, "
            "afin de pouvoir réinstaller Windows sans toucher à ses données. L'installation "
            "utilisera la disposition standard de Windows (EFI 100 Mo, MSR 16 Mo, récupération "
            "d'environ 750 Mo)."
        ),
        instructions=(
            "Donne la table de partitions et la liste ordonnée des partitions avec leur système de fichiers et leur taille.",
            "Calcule la taille de C: et indique la valeur à saisir en Mo dans Gestion des disques pour D:.",
        ),
        criteria=(
            _c("Table", 0.5, "GPT : PC UEFI, Windows 11."),
            _c("Partitions", 1.5, "EFI (ESP) FAT32 100 Mo ; MSR 16 Mo sans système de fichiers ; C: NTFS ; récupération NTFS ≈ 750 Mo ; D: NTFS 300 Gio."),
            _c("Calculs", 1, f"Capacité ≈ {_gib(gb_to_gib(1000))} Gio ; D: = 300 × 1024 = {E08_D_MIB} Mo saisis ; C: ≈ {_gib(E08_C_GIB)} Gio."),
        ),
        correction=(
            "Table GPT (PC UEFI, Windows 11). Disposition : 1) EFI (ESP), FAT32, 100 Mo ; 2) MSR, réservée, 16 Mo ; 3) C: Windows, NTFS ; 4) Récupération, NTFS, environ 750 Mo ; 5) D: Données, NTFS, 300 Gio. La partition de données se crée après l'installation, dans l'espace laissé libre (ou en réduisant C:).",
            f"Capacité : 10^12 ÷ 2^30 ≈ {_gib(gb_to_gib(1000))} Gio. Gestion des disques demande la taille en Mo (en réalité des Mio) : 300 × 1024 = {E08_D_MIB} Mo. C: ≈ {_gib(gb_to_gib(1000))} − 0,10 − 0,02 − 0,73 − 300 ≈ {_gib(E08_C_GIB)} Gio.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Plan de partitions d'un portable Ubuntu avec /home séparé",
        question_type="long_answer",
        requirement_ids=("AP-03", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Une enseignante veut Ubuntu sur un portable UEFI équipé d'un SSD vide vendu "
            "« 256 Go » et 8 Go de mémoire, sans mise en veille prolongée. Elle souhaite un "
            "/home séparé pour garder ses documents lors d'une réinstallation. Le cahier des "
            "charges impose : partition EFI de 512 Mo, racine de 50 Gio, swap de 4 Gio, /home "
            "sur le reste."
        ),
        instructions=(
            "Donne la table et la liste des partitions avec système de fichiers et point de montage.",
            "Calcule la taille de /home.",
        ),
        criteria=(
            _c("Table et ESP", 0.5, "GPT (UEFI) ; ESP FAT32 512 Mo montée sur /boot/efi."),
            _c("Partitions", 1.5, "/ ext4 50 Gio ; swap 4 Gio (espace d'échange, pas de système de fichiers) ; /home ext4 sur le reste."),
            _c("Calcul", 1, f"256 × 10^9 ÷ 2^30 ≈ {_gib(gb_to_gib(256))} Gio ; /home ≈ {_gib(gb_to_gib(256))} − 0,5 − 50 − 4 ≈ {_gib(E09_HOME_GIB)} Gio."),
        ),
        correction=(
            "Table GPT (PC UEFI). 1) EFI (ESP), FAT32, 512 Mo, montée sur /boot/efi (chargeur GRUB). 2) / (racine), ext4, 50 Gio : système et programmes. 3) swap, 4 Gio : espace d'échange (sans hibernation, quelques Gio suffisent). 4) /home, ext4, reste du disque : documents et réglages des utilisateurs, conservés si l'on réinstalle sans reformater /home.",
            f"Capacité : 256 000 000 000 ÷ 1 073 741 824 ≈ {_gib(gb_to_gib(256))} Gio. /home ≈ {_gib(gb_to_gib(256))} − 0,5 − 50 − 4 ≈ {_gib(E09_HOME_GIB)} Gio.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Un disque de photos « Non initialisé »",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-C03", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Un client apporte le disque dur de 1 To de son ancien PC, qui contient dix ans "
            "de photos ; il n'en a pas d'autre copie. Branché dans un boîtier USB sur le PC de "
            "l'atelier, le disque n'apparaît pas dans l'Explorateur. Gestion des disques "
            "affiche le document 1 et propose une fenêtre « Initialiser le disque »."
        ),
        documents=(
            _console(
                "Document 1 — Gestion des disques (capture fictive)",
                "Disque 2   Inconnu   931,51 Go   Non initialisé",
                "  931,51 Go  Non alloué",
                "Fenêtre : « Vous devez initialiser un disque avant",
                "que le Gestionnaire de disques logiques puisse",
                "y accéder. » [MBR] [GPT] [OK]",
            ),
        ),
        instructions=(
            "Dis si tu cliques sur « OK » et justifie.",
            "Rédige les étapes suivantes, sans risque pour les photos.",
        ),
        criteria=(
            _c("Décision", 1, "Annuler : ne pas initialiser — ce disque contenait des données ; l'initialisation écrit une nouvelle table de partitions vide."),
            _c("Démarche", 1.5, "Lire l'état SMART ; essayer un autre câble ou boîtier (adaptateur USB en cause) ; si le disque faiblit, image disque ; récupération (outil de récupération de partitions ou de fichiers) vers un autre disque, avec l'accord écrit du client."),
            _c("Trace", 0.5, "Rapport : état SMART, actions, fichiers récupérés ; aucune écriture sur le disque d'origine."),
        ),
        correction=(
            "Non : on annule. Un disque qui contenait dix ans de photos et apparaît « Non initialisé » a perdu sa table de partitions (ou l'adaptateur USB le présente mal) ; l'initialiser écrirait une table vide par-dessus et compliquerait la récupération.",
            "On lit l'état SMART, on essaie un autre boîtier ou un raccordement SATA direct (certains adaptateurs présentent mal un disque). Si le disque faiblit, on en fait d'abord une image. Avec l'accord écrit du client, on récupère la partition ou les fichiers vers un autre disque, sans jamais écrire sur l'original, puis on rédige le rapport.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Un disque externe devenu « RAW »",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-13", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Une étudiante a débranché son disque externe pendant une copie. Depuis, Windows "
            "affiche le message du document 1 à chaque branchement et Gestion des disques "
            "indique « E: RAW ». Le disque contient son travail de fin d'études ; la dernière "
            "copie date d'un mois. Elle a déjà la souris sur « Formater le disque »."
        ),
        documents=(
            _console(
                "Document 1 — Message et Gestion des disques (fictif)",
                "« Vous devez formater le disque dans le lecteur E:",
                "avant de pouvoir l'utiliser. Voulez-vous le",
                "formater ? » [Formater le disque] [Annuler]",
                "Disque 1   De base   931,48 Go   En ligne",
                "  E: 931,48 Go RAW   Sain (Partition principale)",
            ),
        ),
        instructions=(
            "Dis ce que l'étudiante doit répondre au message et pourquoi.",
            "Explique l'état « RAW » affiché par Gestion des disques et rédige la démarche de récupération.",
        ),
        criteria=(
            _c("Réponse", 0.5, "Annuler : formater crée un système de fichiers vide et rend la récupération plus difficile."),
            _c("RAW", 0.5, "Windows ne reconnaît plus de système de fichiers lisible sur la partition (structures endommagées par l'arrachage), mais les données sont en général toujours sur le disque."),
            _c("Démarche", 1, "État SMART ; ne rien écrire sur le disque ; copie ou image si le disque faiblit ; outil de récupération vers un autre support ; vérifier les fichiers ; ensuite seulement reformater et restaurer ; conseil : éjection sûre et sauvegardes."),
        ),
        correction=(
            "Annuler. « RAW » signifie que Windows ne trouve plus de système de fichiers lisible sur la partition : l'arrachage pendant l'écriture a endommagé ses structures. Les fichiers sont en général toujours présents ; un formatage en créerait de nouvelles structures vides et compliquerait la récupération.",
            "Démarche : lire l'état SMART ; n'écrire aucun fichier sur ce disque ; faire une image si le disque montre des signes de faiblesse ; récupérer les fichiers avec un outil de récupération vers un autre disque, puis les vérifier avec elle. Seulement ensuite : reformater, recopier, et conseiller l'éjection sûre et une sauvegarde régulière.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="« Défragmentez tous mes disques »",
        question_type="document_analysis",
        requirement_ids=("AP-03",),
        kind=KIND_DIAG,
        context=(
            "Le comptable d'une PME trouve son PC lent et demande de « défragmenter tous les "
            "disques ». Le PC a trois lecteurs ; l'outil « Optimiser les lecteurs » de Windows "
            "affiche le document 1. L'état SMART des trois supports est bon et chaque lecteur "
            f"a plus de 20 % d'espace libre. Convention du cours : un disque dur se défragmente "
            f"au-delà de {FRAGMENTATION_ALERT} % de fragmentation."
        ),
        documents=(
            _table(
                "Document 1 — Optimiser les lecteurs (capture fictive)",
                ("Lecteur", "Type de média", "État actuel"),
                ("C:", "Disque SSD", "OK (12 jours depuis le dernier découpage)"),
                ("D:", "Disque dur", "OK (4 % fragmenté)"),
                ("E:", "Disque dur", "Optimisation nécessaire (34 % fragmenté)"),
            ),
        ),
        instructions=("Pour chaque lecteur, dis ce que tu fais et pourquoi, puis réponds au comptable en une phrase.",),
        criteria=(
            _c("C:", 1, "SSD : pas de défragmentation (aucun gain, écritures inutiles) ; Windows l'optimise par TRIM (« découpage »), déjà fait."),
            _c("D: et E:", 1.5, f"D: 4 % : rien à faire ; E: 34 % : défragmenter (au-delà de {FRAGMENTATION_ALERT} %), SMART bon et espace libre suffisant."),
            _c("Réponse", 0.5, "Seul E: est défragmenté ; la lenteur peut aussi avoir d'autres causes (démarrage, espace, logiciels)."),
        ),
        correction=(
            "C: est un SSD : on ne le défragmente pas. Il n'y a pas de têtes à déplacer, une défragmentation n'apporte rien et consomme des écritures. Windows l'optimise par TRIM (« découpage »), fait il y a 12 jours. D: n'est fragmenté qu'à 4 % : rien à faire.",
            f"E: est fragmenté à 34 %, au-delà du seuil de {FRAGMENTATION_ALERT} % : avec un état SMART bon et de l'espace libre, on lance l'optimisation de E:. Réponse au comptable : « Seul E: avait besoin d'une défragmentation ; le SSD s'entretient autrement. Si la lenteur persiste, je chercherai une autre cause. » Résultat (% fragmenté après) dans le rapport.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Repartitionner un disque qui faiblit ?",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-C03", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Un client veut que tu agrandisses la partition C: de son PC de bureau (disque dur "
            "de 1 To) en réduisant D:, qui contient ses factures. Avant d'intervenir, tu "
            "relèves l'état SMART du disque (document 1). Règle du cours : secteurs en attente "
            "ou illisibles au-dessus de 0 → à remplacer ; secteurs réalloués seuls → à surveiller."
        ),
        documents=(_console("Document 1", *smart_lines("Relevé SMART — disque dur 1 To (fictif)", "PASSED", E13_SMART)),),
        instructions=(
            "Interprète le relevé (ne te limite pas au résultat global).",
            "Dis si tu redimensionnes les partitions et rédige ce que tu fais à la place.",
        ),
        criteria=(
            _c("Lecture", 1, "PASSED ne suffit pas : 12 secteurs en attente, 12 illisibles, 56 réalloués → disque à remplacer ; pas d'erreur de câble (CRC à 0)."),
            _c("Décision", 1, "Pas de redimensionnement (il déplace des données sur un disque qui perd des secteurs) : sauvegarde immédiate et vérifiée de D: et des documents, accord du client, remplacement du disque (SSD), réinstallation ou clonage, partitions refaites sur le nouveau disque."),
            _c("Trace", 1, "Rapport : valeurs SMART, risque expliqué au client, accord, sauvegarde vérifiée."),
        ),
        correction=(
            "Le résumé « PASSED » ne suffit pas : 12 secteurs en attente et 12 illisibles signifient que le disque n'arrive plus à lire certaines zones ; 56 secteurs ont déjà été remplacés. Verdict du cours : à remplacer. L'erreur ne vient pas du câble (UDMA_CRC_Error_Count à 0).",
            "On ne redimensionne pas : l'opération déplace des données et sollicite tout le disque, au risque de perdre les factures. On explique le risque au client, on sauvegarde immédiatement ses données et on vérifie la copie, puis, avec son accord, on remplace le disque (par exemple un SSD) et on recrée les partitions voulues sur le disque neuf. Valeurs SMART et accord dans le rapport.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Disque C: plein : libérer de l'espace sans rien casser",
        question_type="short_answer",
        requirement_ids=("AP-03", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Le portable Windows 11 d'une assistante sociale affiche une barre rouge sur C: "
            "(SSD de 256 Go, 3 Go libres) ; les mises à jour échouent faute d'espace. Elle "
            "propose de « supprimer ce qui est gros dans C:\\Windows ». Le dossier "
            "Téléchargements contient 40 Go de vidéos et la corbeille 12 Go."
        ),
        instructions=("Rédige une démarche non destructive pour libérer de l'espace et dis ce que tu réponds à sa proposition.",),
        criteria=(
            _c("Mesure", 0.5, "Paramètres > Système > Stockage : voir ce qui occupe l'espace avant d'agir."),
            _c("Actions", 1.5, "Corbeille vidée (avec son accord) ; Nettoyage de disque (fichiers temporaires, anciennes mises à jour) ; vidéos déplacées vers un support externe ou un disque de données, avec son accord ; programmes inutiles désinstallés proprement ; Assistant Stockage activé."),
            _c("Refus", 1, "Ne jamais supprimer à la main dans C:\\Windows ou Program Files : Windows peut ne plus démarrer ; on passe par les outils prévus."),
        ),
        correction=(
            "On mesure d'abord (Paramètres > Système > Stockage). Puis, avec l'accord de l'utilisatrice : vider la corbeille (12 Go), lancer le Nettoyage de disque (fichiers temporaires, fichiers d'anciennes mises à jour), déplacer les vidéos des Téléchargements (40 Go) vers un disque externe ou un partage, désinstaller les programmes inutiles par les Paramètres, activer l'Assistant Stockage.",
            "Réponse : non, on ne supprime rien à la main dans C:\\Windows ni dans les dossiers de programmes ; ce sont des fichiers du système, et Windows pourrait ne plus démarrer. Contrôle final : espace libre suffisant, mises à jour installées.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="« No bootable device » après un réglage du firmware",
        question_type="short_answer",
        requirement_ids=("AP-03", "AP-09", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Pour démarrer une vieille clé de diagnostic, un collègue a activé le mode de "
            "compatibilité (CSM, démarrage « Legacy ») dans le firmware d'un PC Windows 11. "
            "Depuis, le PC affiche « No bootable device ». Le disque système est un SSD NVMe "
            "en table GPT, toujours listé dans le firmware avec sa bonne capacité."
        ),
        instructions=("Explique la cause et rédige la correction, sans réinstaller.",),
        criteria=(
            _c("Cause", 1, "Windows installé sur un disque GPT démarre en mode UEFI : en mode hérité (Legacy/CSM), le firmware cherche un secteur de démarrage MBR et ne trouve rien."),
            _c("Correction", 1, "Revenir au démarrage UEFI (désactiver CSM/Legacy), remettre Windows Boot Manager en tête de l'ordre de démarrage, enregistrer, redémarrer ; réactiver le démarrage sécurisé s'il a été coupé ; noter le réglage dans le rapport."),
        ),
        correction=(
            "Le disque est en GPT : Windows y démarre en mode UEFI, par le chargeur placé dans la partition EFI. En mode hérité (CSM), le firmware cherche un code de démarrage MBR : il ne trouve rien et affiche « No bootable device ». Le disque et Windows sont intacts.",
            "Correction : dans le firmware, revenir au démarrage UEFI (CSM/Legacy désactivé), remettre « Windows Boot Manager » en premier, réactiver le démarrage sécurisé s'il a été désactivé, enregistrer et redémarrer. Aucune réinstallation ni réparation n'est nécessaire. On note le réglage dans le rapport.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Corriger la procédure d'un collègue",
        question_type="long_answer",
        requirement_ids=("AP-03", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a rédigé la procédure suivante pour préparer le PC d'un client "
            "(SSD système de 512 Go, disque dur de données de 2 To contenant les dossiers du "
            "client) avant de lui remettre une clé USB d'échange avec son Mac : « 1. Ouvrir "
            "diskpart, select disk 1, clean pour repartir propre. 2. Défragmenter le SSD et le "
            "disque dur chaque semaine. 3. Formater la clé en FAT32 pour qu'elle marche "
            "partout, y compris pour ses vidéos de 6 Go. 4. Formatage rapide du disque de "
            "données pour effacer ses anciens fichiers avant de le donner à son fils. »"
        ),
        instructions=("Relève les erreurs de chaque point et réécris la procédure correcte.",),
        criteria=(
            _c("Point 1", 0.75, "clean efface toute la table du disque sélectionné : jamais sans identification du disque (list disk, detail disk), sauvegarde vérifiée et accord ; le disque 1 porte peut-être les dossiers du client."),
            _c("Point 2", 0.75, "Pas de défragmentation du SSD (TRIM automatique) ; disque dur : optimisation planifiée, défragmentation seulement si fragmenté au-delà du seuil."),
            _c("Point 3", 0.75, "FAT32 refuse les fichiers de plus de 4 Gio : exFAT, lu et écrit par Windows et macOS."),
            _c("Point 4", 0.75, "Un formatage rapide n'efface pas : accord écrit du propriétaire, sauvegarde, puis effacement sécurisé adapté au support (PR04)."),
        ),
        correction=(
            "1. « clean » efface la table de partitions de tout le disque sélectionné : le disque 1 est peut-être celui des dossiers du client. On identifie d'abord (list disk, detail disk), on sauvegarde et on vérifie la copie, on obtient l'accord écrit — et on n'utilise clean que sur un disque à vider volontairement. 2. On ne défragmente pas un SSD : Windows l'entretient par TRIM ; le disque dur est optimisé par la tâche planifiée, défragmenté seulement au-delà du seuil.",
            "3. FAT32 refuse les fichiers de plus de 4 Gio : les vidéos de 6 Go ne passeraient pas. On formate la clé en exFAT, lu et écrit par Windows et macOS. 4. Un formatage rapide n'efface pas les fichiers : avec l'accord écrit du client et après sauvegarde vérifiée, effacement sécurisé adapté au disque dur (écrasement complet, PR04), avec un certificat.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Quel support pour un portable de chantier ?",
        question_type="short_answer",
        requirement_ids=("AP-03", "AP-17"),
        kind=KIND_CHOICE,
        context=(
            "Un conducteur de travaux utilise son portable sur les chantiers, souvent en "
            "voiture ; le disque dur d'origine (2,5 pouces, SATA) a déjà lâché une fois après "
            "une chute. La notice indique un emplacement M.2 2280 « SATA uniquement » et une "
            "baie 2,5 pouces SATA. Il a acheté un SSD M.2 NVMe en promotion."
        ),
        instructions=("Conseille le type de support et dis si le SSD acheté convient, en justifiant.",),
        criteria=(
            _c("Choix", 1, "SSD : aucune pièce mobile, résiste mieux aux chocs que le disque dur (têtes et plateaux), plus rapide."),
            _c("Compatibilité", 1, "Le SSD NVMe ne fonctionnera pas dans un M.2 « SATA uniquement » : il faut un SSD M.2 SATA ou un SSD 2,5 pouces SATA."),
        ),
        correction=(
            "Un SSD : sans pièce mobile, il supporte bien mieux les chocs et les vibrations qu'un disque dur, dont les têtes peuvent toucher les plateaux ; il est aussi plus rapide.",
            "Le SSD NVMe acheté ne convient pas : l'emplacement M.2 de ce portable est « SATA uniquement », un SSD NVMe n'y serait pas reconnu. Il faut un SSD M.2 SATA (format 2280) ou un SSD 2,5 pouces SATA dans la baie.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un disque de 2 To affiché à 1862 Go",
        question_type="short_answer",
        requirement_ids=("AP-03",),
        kind=KIND_CALC,
        context=(
            "Une cliente installe un disque dur vendu « 2 To ». Gestion des disques affiche "
            f"{_gib(X02_GIB)} Go. Elle demande au technicien si le disque est défectueux ou "
            "si une partie est réservée par Windows, et veut une réponse chiffrée."
        ),
        instructions=("Explique l'écart à la cliente avec le calcul.",),
        criteria=(
            _c("Explication", 1, "Fabricant : 1 To = 10^12 octets (décimal) ; Windows : divise par 2^30 (Gio) mais écrit « Go » ; disque ni défectueux ni amputé."),
            _c("Calcul", 1, f"2 × 10^12 ÷ 1 073 741 824 ≈ {_gib(X02_GIB)} Gio (environ 1,82 Tio)."),
        ),
        correction=(
            "Le disque n'est pas défectueux et Windows ne réserve pas cette différence : le fabricant compte en unités décimales (2 To = 2 000 000 000 000 octets), Windows en unités binaires (1 Gio = 1 073 741 824 octets) tout en écrivant « Go ».",
            f"2 000 000 000 000 ÷ 1 073 741 824 ≈ {_gib(X02_GIB)} Gio, soit environ 1,82 Tio : c'est la même capacité.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="La clé refuse un fichier de 8 Go",
        question_type="short_answer",
        requirement_ids=("AP-03",),
        kind=KIND_CHOICE,
        context=(
            "Un vidéaste copie un film de 8 Go sur sa clé USB de 64 Go, à moitié pleine, pour "
            "le monter sur le Mac d'un collègue. Windows répond : « Le fichier est trop "
            "volumineux pour le système de fichiers de destination ». Les propriétés de la clé "
            "indiquent : système de fichiers FAT32."
        ),
        instructions=("Explique le message et rédige la solution, données comprises.",),
        criteria=(
            _c("Cause", 0.75, "FAT32 limite un fichier à 4 Gio (moins 1 octet) : 8 Go dépasse, quel que soit l'espace libre."),
            _c("Solution", 1.25, "Copier d'abord le contenu de la clé ailleurs et vérifier ; reformater la clé en exFAT (lu et écrit par Windows et macOS) ; recopier les fichiers puis le film ; tester sur le Mac."),
        ),
        correction=(
            "FAT32 n'accepte pas de fichier de plus de 4 Gio (4 294 967 295 octets) : le film de 8 Go est refusé même s'il reste 32 Go de libres.",
            "Comme le formatage efface la clé : copier son contenu sur le PC et vérifier la copie, reformater la clé en exFAT (lu et écrit nativement par Windows et macOS), recopier les fichiers puis le film, et vérifier qu'il s'ouvre sur le Mac.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Un disque de 3 To dont 1 To est inutilisable",
        question_type="document_analysis",
        requirement_ids=("AP-03",),
        kind=KIND_CALC,
        context=(
            "Sur un PC UEFI, un collègue a initialisé un disque dur neuf de 3 To en MBR et y a "
            "créé une partition. Le document 1 montre Gestion des disques. Le disque ne "
            "contient encore aucune donnée."
        ),
        documents=(
            _console(
                "Document 1 — Gestion des disques (capture fictive)",
                f"Disque 1   De base   {fr_number(X04_DISK_GIB)} Go   En ligne",
                f"  D: {fr_number(X04_MBR_GIB)} Go NTFS | {fr_number(X04_LOST_GIB)} Go Non alloué",
                "  (clic droit sur l'espace non alloué : aucune",
                "  option « Nouveau volume simple » disponible)",
            ),
        ),
        instructions=("Explique pourquoi une partie du disque est inutilisable et rédige la correction.",),
        criteria=(
            _c("Cause", 1, f"MBR (secteurs de 512 octets) n'adresse que 2 Tio = {fr_number(X04_MBR_GIB)} Gio ; le reste ({fr_number(X04_LOST_GIB)} Gio) est hors de portée."),
            _c("Correction", 1, "Disque vide : supprimer la partition, convertir en GPT (Gestion des disques ou diskpart convert gpt), créer un volume NTFS sur tout le disque ; s'il contenait des données : sauvegarde vérifiée d'abord."),
        ),
        correction=(
            f"La table MBR compte les secteurs sur 32 bits : avec des secteurs de 512 octets, elle n'adresse que 2^32 × 512 octets = 2 Tio ({fr_number(X04_MBR_GIB)} Gio). Les {fr_number(X04_LOST_GIB)} Gio restants (3 To = {fr_number(X04_DISK_GIB)} Gio) ne peuvent pas recevoir de partition.",
            "Le disque est vide : on supprime la partition, on convertit le disque en GPT (clic droit « Convertir en disque GPT », ou diskpart : select disk 1, convert gpt — après avoir vérifié le numéro du disque), puis on crée un volume NTFS sur toute la capacité. S'il avait contenu des données, on aurait sauvegardé et vérifié la copie avant.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Plan de partitions d'un ancien PC sans UEFI",
        question_type="long_answer",
        requirement_ids=("AP-03", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Une association veut réinstaller Windows 10 sur un PC de bureau ancien dont la "
            "carte mère n'a qu'un BIOS (pas d'UEFI). Le disque est un SSD SATA neuf de "
            "240 Go. L'installateur de Windows crée lui-même la disposition standard pour ce "
            "type de PC."
        ),
        instructions=(
            "Donne la table de partitions et la disposition obtenue (nom, système de fichiers, rôle).",
            "Explique pourquoi GPT ne convient pas ici.",
        ),
        criteria=(
            _c("Table", 0.5, "MBR."),
            _c("Disposition", 1, "Partition « Réservé au système » (NTFS, environ 500 Mo, active : fichiers de démarrage) puis C: NTFS sur le reste (une partition de récupération peut s'ajouter)."),
            _c("Justification", 0.5, "Un PC BIOS sans UEFI ne démarre Windows que depuis un disque MBR ; 240 Go est sous la limite de 2 Tio."),
        ),
        correction=(
            "Table MBR. Disposition : 1) « Réservé au système », NTFS, environ 500 Mo, partition active qui contient les fichiers de démarrage ; 2) C:, NTFS, le reste du disque (selon la version, une petite partition de récupération peut s'y ajouter).",
            "GPT ne convient pas : Windows ne démarre d'un disque GPT qu'en mode UEFI, et ce PC n'a qu'un BIOS. Avec 240 Go, la limite de 2 Tio du MBR n'est pas un problème.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Un disque qui disparaît par moments",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Le disque de données SATA d'un PC de bureau disparaît de l'Explorateur plusieurs "
            "fois par jour puis revient ; des copies échouent. Le document 1 donne son relevé "
            "SMART. Le câble SATA passe tendu contre la carte graphique."
        ),
        documents=(_console("Document 1", *smart_lines("Relevé SMART — disque dur 2 To (fictif)", "PASSED", X06_SMART)),),
        instructions=("Interprète le relevé et rédige l'intervention.",),
        criteria=(
            _c("Lecture", 1, "Aucun secteur réalloué, en attente ni illisible ; 214 erreurs CRC : erreurs de transfert sur la liaison (câble ou connecteur SATA), pas sur les plateaux."),
            _c("Intervention", 1, "Sauvegarde des données ; PC hors tension, remplacer le câble SATA (bien enfiché, sans tension mécanique), essayer un autre port ; vérifier que le compteur CRC n'augmente plus ; rapport."),
        ),
        correction=(
            "Les attributs de surface sont à 0 : le disque lit correctement ses plateaux. En revanche, 214 erreurs CRC signalent des données abîmées pendant le transfert entre le disque et la carte mère : la liaison (câble SATA tendu, connecteur mal enfiché, port) est en cause.",
            "Intervention : sauvegarder les données par précaution ; PC hors tension, remplacer le câble SATA en le faisant passer sans tension, essayer un autre port ; puis vérifier pendant quelques jours que le compteur CRC n'augmente plus (il ne redescend jamais à 0) et que le disque ne disparaît plus. Rapport avec les valeurs.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Formatage rapide ou complet ?",
        question_type="short_answer",
        requirement_ids=("AP-03", "AP-C03"),
        kind=KIND_CHOICE,
        context=(
            "Un stagiaire prépare deux disques durs : un disque neuf destiné aux sauvegardes "
            "d'un client, et un disque d'occasion récupéré dont on ignore l'état, qui servira "
            "de disque de test à l'atelier. Il demande quand choisir le formatage rapide ou le "
            "formatage complet de Windows, et si l'un des deux « efface » un disque."
        ),
        instructions=("Explique la différence, le choix pour chaque disque, et réponds sur l'effacement.",),
        criteria=(
            _c("Différence", 0.75, "Rapide : écrit seulement un nouveau système de fichiers vide. Complet : en plus, parcourt tout le volume (écriture de zéros sous Windows récents) et recherche les secteurs défectueux — beaucoup plus long."),
            _c("Choix", 0.75, "Disque neuf : rapide suffit. Disque d'occasion d'état inconnu : complet (ou test de surface), après lecture SMART."),
            _c("Effacement", 0.5, "Le rapide n'efface pas les données ; un effacement de données se fait avec une technique d'effacement sécurisé adaptée et l'accord du propriétaire (PR04)."),
        ),
        correction=(
            "Le formatage rapide écrit seulement un système de fichiers vide (tables, répertoire racine). Le formatage complet fait la même chose puis parcourt tout le volume : sous les Windows récents, il écrit des zéros et repère les secteurs défectueux ; il prend des heures sur un grand disque.",
            "Disque neuf : formatage rapide. Disque d'occasion : lecture SMART, puis formatage complet (ou test de surface) pour repérer les zones défectueuses. Un formatage rapide n'efface pas les anciens fichiers ; pour rendre des données illisibles, on applique un effacement sécurisé adapté au support avec l'accord du propriétaire (PR04).",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Défragmenter un SSD chaque semaine ?",
        question_type="short_answer",
        requirement_ids=("AP-03",),
        kind=KIND_CHOICE,
        context=(
            "Un client a lu sur un forum qu'il faut défragmenter un ordinateur chaque semaine. "
            "Son portable récent n'a qu'un SSD NVMe ; il veut installer un logiciel de "
            "défragmentation gratuit et programmer une défragmentation complète chaque "
            "dimanche. Il te demande ton avis écrit."
        ),
        instructions=("Réponds au client et explique comment ce SSD est entretenu.",),
        criteria=(
            _c("Avis", 1, "Non : un SSD n'a pas de têtes à déplacer, la fragmentation ne le ralentit pas ; une défragmentation n'apporte rien et consomme des écritures (endurance limitée)."),
            _c("Entretien", 1, "Windows optimise le SSD par TRIM (« découpage ») via « Optimiser les lecteurs », planifié automatiquement ; on vérifie que la planification est active ; aucun logiciel tiers."),
        ),
        correction=(
            "Déconseillé : sur un SSD, l'accès à un bloc prend le même temps où qu'il soit, la fragmentation ne ralentit donc pas la lecture ; défragmenter réécrit inutilement des gigaoctets, alors que la mémoire flash supporte un nombre d'écritures limité.",
            "Windows reconnaît le SSD et l'entretient par la commande TRIM (« découpage ») dans « Optimiser les lecteurs », planifiée automatiquement. On vérifie simplement que l'optimisation planifiée est active ; aucun logiciel de défragmentation n'est nécessaire.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Un relevé SMART à interpréter avec prudence",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-15"),
        kind=KIND_DIAG,
        context=(
            "Lors d'un entretien, tu relèves l'état SMART du disque dur du PC d'un médecin "
            "(document 1). Le PC fonctionne normalement. Règle du cours : secteurs en attente "
            "ou illisibles au-dessus de 0 → à remplacer ; secteurs réalloués seuls → à surveiller."
        ),
        documents=(_console("Document 1", *smart_lines("Relevé SMART — disque dur 1 To (fictif)", "PASSED", X09_SMART)),),
        instructions=("Donne ton verdict et rédige ce que tu écris au client.",),
        criteria=(
            _c("Verdict", 1, "À surveiller : 12 secteurs réalloués (le disque a déjà remplacé des zones défectueuses), aucun en attente ni illisible, pas d'erreur CRC ; « PASSED » seul ne suffit pas."),
            _c("Conseil", 1, "Sauvegarde régulière et vérifiée dès maintenant ; nouveau relevé à intervalle (ex. un mois) : si le nombre augmente ou si des secteurs passent en attente, remplacement ; SMART ne garantit pas l'absence de panne soudaine."),
        ),
        correction=(
            "Verdict : à surveiller. Le résumé « PASSED » ne suffit pas : 12 secteurs ont déjà été réalloués, signe d'usure de la surface ; il n'y a toutefois aucun secteur en attente ni illisible, et aucune erreur de transfert.",
            "Message au client : « Votre disque montre un début d'usure. Faites dès maintenant une sauvegarde régulière et vérifiée de vos données. Je referai un relevé dans un mois ; si le nombre augmente ou si des secteurs deviennent illisibles, il faudra le remplacer. Un bon relevé SMART ne garantit pas qu'un disque ne tombera pas en panne : la sauvegarde reste indispensable. »",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Monter un disque d'archives sous Linux",
        question_type="long_answer",
        requirement_ids=("AP-03", "AP-11"),
        kind=KIND_ORDER,
        context=(
            "Sur un serveur Debian, tu ajoutes un disque dur neuf de 4 To pour des archives. "
            "Après démarrage, lsblk montre le disque système nvme0n1 (trois partitions montées) "
            "et un disque sdb de 3,6T sans partition. Les archives doivent être accessibles "
            "dans /srv/archives, y compris après chaque redémarrage."
        ),
        instructions=("Rédige les commandes dans l'ordre, avec la précaution à prendre avant la première commande qui écrit sur le disque.",),
        criteria=(
            _c("Précaution", 0.5, "Vérifier avec lsblk que sdb est bien le disque neuf (taille, aucune partition), jamais nvme0n1."),
            _c("Préparation", 0.75, "parted /dev/sdb mklabel gpt (4 To > 2 Tio) ; mkpart sur tout le disque ; mkfs.ext4 /dev/sdb1."),
            _c("Montage permanent", 0.75, "mkdir /srv/archives ; mount ; UUID par blkid ; ligne fstab « UUID=… /srv/archives ext4 defaults 0 2 » ; mount -a ; df -h."),
        ),
        correction=(
            "Précaution : lsblk -f pour confirmer que sdb est le disque neuf (3,6T, sans partition), et non le disque système nvme0n1. Puis : sudo parted /dev/sdb mklabel gpt (GPT obligatoire au-delà de 2 Tio) ; sudo parted -a optimal /dev/sdb mkpart archives ext4 0% 100% ; sudo mkfs.ext4 -L archives /dev/sdb1.",
            "sudo mkdir -p /srv/archives ; sudo mount /dev/sdb1 /srv/archives ; sudo blkid /dev/sdb1 pour lire l'UUID ; ajouter dans /etc/fstab : UUID=<uuid> /srv/archives ext4 defaults 0 2 ; sudo mount -a pour tester la ligne ; df -h /srv/archives (environ 3,6 Tio).",
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

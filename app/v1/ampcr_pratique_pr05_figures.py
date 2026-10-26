"""PR05 « Stockage, partitions, formatage et défragmentation » — données de référence, règles
de décision et schémas SVG (ticket #206).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket206_ampcr_pratique_pr05.py` :

- trois supports comparés (`MEDIA_ROWS`) : disque dur, SSD SATA, SSD NVMe ;
- conversions d'unités (`gb_to_gib`, `tb_to_tib`) : un disque vendu « 1 To » (10^12 octets)
  est affiché « 931 Go » par Windows, qui compte en Gio (2^30 octets) ;
- tables de partitions (`MBR_LIMIT_BYTES`, `partition_table_choice`) : MBR limité à 2 Tio
  avec des secteurs de 512 octets et à 4 partitions principales ; GPT obligatoire pour
  démarrer Windows en UEFI ;
- systèmes de fichiers (`FILESYSTEMS`, `filesystem_for`, `fits_on_fat32`) : NTFS, FAT32,
  exFAT, ext4 selon l'usage ;
- trois plans de partitions exacts (`WINDOWS_UEFI_PLAN`, `WINDOWS_BIOS_PLAN`,
  `LINUX_UEFI_PLAN`) et le plan du cas 4 (`CASE4_*`), dessinés et contrôlés depuis les mêmes
  tuples ;
- l'entretien adapté au support (`optimisation_for`) : défragmentation pour un disque dur,
  TRIM pour un SSD ; la lecture prudente d'un relevé SMART (règle de PR04, réutilisée) ;
- les symptômes de stockage et la première action non destructive (`SYMPTOMS`) ;
- cinq procédures illustrées (`SAFE_STEPS`, `WIN_NEW_DISK_STEPS`, `LINUX_NEW_DISK_STEPS`,
  `OPTIMISE_STEPS`, `NOT_DETECTED_STEPS`) : les mêmes tuples dessinent les schémas et
  alimentent les remises en ordre des exercices.

Les captures (Gestion des disques, lsblk, « Optimiser les lecteurs ») sont **fictives** ;
aucun schéma ne vient d'une image générée ni d'une photographie.
"""

from dataclasses import dataclass

from app.v1.ampcr_pratique_pr04_figures import (  # noqa: F401 — règle SMART de PR04 réutilisée
    SMART_OK,
    SMART_REPLACE,
    SMART_WATCH,
    smart_lines,
    smart_verdict,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    PartitionSegment,
    decision_tree_svg,
    partition_map_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR04)

# =============================================================================================
# 1. Supports de stockage
# =============================================================================================


@dataclass(frozen=True)
class MediaRow:
    name: str
    principle: str
    interface: str
    order_of_speed: str  # ordre de grandeur en lecture séquentielle (pas une valeur garantie)
    strengths: str
    limits: str
    optimisation: str


MEDIA_HDD = "Disque dur (HDD)"
MEDIA_SATA_SSD = "SSD SATA"
MEDIA_NVME_SSD = "SSD NVMe"
MEDIA = (MEDIA_HDD, MEDIA_SATA_SSD, MEDIA_NVME_SSD)

MEDIA_ROWS: tuple[MediaRow, ...] = (
    MediaRow(
        MEDIA_HDD,
        "Plateaux magnétiques en rotation (5 400 ou 7 200 tr/min), têtes de lecture mobiles.",
        "SATA (câble de données 7 broches + alimentation SATA 15 broches), 3,5 ou 2,5 pouces.",
        "100 à 250 Mo/s ; temps d'accès de plusieurs millisecondes (rotation et déplacement des têtes).",
        "Grande capacité à bas prix par To : archives, sauvegardes, données volumineuses.",
        "Lent pour le système, bruyant, sensible aux chocs surtout en fonctionnement.",
        "Défragmentation (optimisation) utile.",
    ),
    MediaRow(
        MEDIA_SATA_SSD,
        "Mémoire flash NAND, aucune pièce mobile, contrôleur qui gère l'usure.",
        "SATA, comme un disque dur : boîtier 2,5 pouces ou carte M.2 « SATA ».",
        "Jusqu'à environ 550 Mo/s : la limite vient de l'interface SATA 6 Gbit/s.",
        "Démarrage et programmes rapides, silencieux, résistant aux chocs ; compatible avec tout PC à port SATA.",
        "Prix par To plus élevé ; nombre d'écritures limité (endurance indiquée en To écrits).",
        "TRIM, jamais de défragmentation classique.",
    ),
    MediaRow(
        MEDIA_NVME_SSD,
        "Mémoire flash NAND, comme le SSD SATA, mais dialogue direct avec le processeur.",
        "PCI Express (souvent 4 lignes) par un emplacement M.2 compatible NVMe (format courant 2280).",
        "Environ 3 500 Mo/s en PCIe 3.0 et 7 000 Mo/s en PCIe 4.0 (4 lignes).",
        "Le plus rapide ; aucun câble ; idéal pour le système et les applications.",
        "Exige un emplacement M.2 NVMe (vérifier la notice : certains M.2 ne sont que SATA) ; chauffe sous forte charge.",
        "TRIM, jamais de défragmentation classique.",
    ),
)
MEDIA_BY_NAME = {row.name: row for row in MEDIA_ROWS}

# =============================================================================================
# 2. Unités : Go (10^9) et Gio (2^30)
# =============================================================================================

GB = 10**9
GIB = 2**30
TB = 10**12
TIB = 2**40


def gb_to_gib(gb: float) -> float:
    """Capacité annoncée en Go (10^9 octets) → Gio (2^30), arrondie au centième.

    C'est le nombre que Windows affiche… avec l'étiquette « Go »."""
    return round(gb * GB / GIB, 2)


def fr_number(value: float, digits: int = 2) -> str:
    """Nombre à la virgule décimale, sans séparateur de milliers (comme Windows) :
    1862.65 → « 1862,65 »."""
    return f"{value:.{digits}f}".replace(".", ",")


def tb_to_tib(tb: float) -> float:
    return round(tb * TB / TIB, 2)


# (capacité annoncée, octets, affichage Windows en Gio) — recalculé par les tests.
UNIT_ROWS: tuple[tuple[str, int], ...] = (
    ("256 Go", 256 * GB),
    ("500 Go", 500 * GB),
    ("1 To", 1 * TB),
    ("2 To", 2 * TB),
    ("4 To", 4 * TB),
)

# =============================================================================================
# 3. Secteurs, clusters, pages : ordres de grandeur
# =============================================================================================

SECTOR_LEGACY = 512
SECTOR_ADVANCED = 4096
NTFS_DEFAULT_CLUSTER = 4096
FAT32_MAX_FILE = 2**32 - 1  # 4 Gio moins 1 octet


def clusters_used(file_bytes: int, cluster: int = NTFS_DEFAULT_CLUSTER) -> int:
    """Nombre de clusters (unités d'allocation) occupés par un fichier : un fichier, même
    d'un octet, occupe au moins un cluster entier."""
    if file_bytes <= 0:
        return 0
    return -(-file_bytes // cluster)


def fits_on_fat32(file_bytes: int) -> bool:
    return file_bytes <= FAT32_MAX_FILE


# =============================================================================================
# 4. Tables de partitions : MBR ou GPT
# =============================================================================================

MBR_MAX_PRIMARY = 4
MBR_LIMIT_BYTES = 2**32 * SECTOR_LEGACY  # 2 Tio adressables avec des secteurs de 512 octets
GPT_WINDOWS_MAX_PARTITIONS = 128

TABLE_GPT = "GPT"
TABLE_MBR = "MBR"

MBR_GPT_ROWS: tuple[tuple[str, str, str], ...] = (
    ("Taille de disque gérée", "2 Tio au plus (secteurs de 512 octets) ; au-delà, l'espace est inutilisable",
     "Pratiquement illimitée pour un PC (bien au-delà des disques actuels)"),
    ("Nombre de partitions", "4 principales, ou 3 principales + 1 étendue contenant des lecteurs logiques",
     "128 partitions sous Windows, sans partition étendue"),
    ("Démarrage", "BIOS hérité (ou mode de compatibilité CSM de l'UEFI)",
     "UEFI ; Windows 64 bits ne démarre d'un disque GPT qu'en mode UEFI"),
    ("Robustesse", "Une seule table au début du disque",
     "Table principale au début et copie de secours à la fin, avec somme de contrôle"),
    ("Usage aujourd'hui", "Anciens PC sans UEFI, supports de compatibilité",
     "Tout PC récent ; Windows 11 l'impose pour le disque système (UEFI)"),
)


def partition_table_choice(*, disk_bytes: int, boots_os: bool, firmware_uefi: bool,
                           partitions_needed: int = 1) -> str:
    """Table de partitions à choisir pour un disque **vide** (après sauvegarde).

    - disque système d'un PC qui démarre en BIOS hérité (sans UEFI) : MBR (limite 2 Tio) ;
    - sinon GPT : PC UEFI, disque de plus de 2 Tio, plus de 4 partitions ou disque de
      données d'un PC récent."""
    if boots_os and not firmware_uefi:
        if disk_bytes > MBR_LIMIT_BYTES:
            raise ValueError("Un PC sans UEFI ne peut pas démarrer d'un disque de plus de 2 Tio : "
                             "disque plus petit ou PC compatible UEFI.")
        return TABLE_MBR
    del partitions_needed  # toujours GPT hors démarrage BIOS : plus de limite à 4 partitions
    return TABLE_GPT


def mbr_usable_bytes(disk_bytes: int) -> int:
    """Espace qu'une table MBR (secteurs de 512 octets) peut adresser sur ce disque."""
    return min(disk_bytes, MBR_LIMIT_BYTES)


# =============================================================================================
# 5. Systèmes de fichiers et choix selon l'usage
# =============================================================================================


@dataclass(frozen=True)
class Filesystem:
    name: str
    max_file: str
    windows: str
    macos: str
    linux: str
    journal: bool
    permissions: bool
    typical_use: str


FS_NTFS = "NTFS"
FS_FAT32 = "FAT32"
FS_EXFAT = "exFAT"
FS_EXT4 = "ext4"

FILESYSTEMS: tuple[Filesystem, ...] = (
    Filesystem(FS_NTFS, "très grande (plusieurs To)", "lecture et écriture", "lecture seule",
               "lecture et écriture (pilote ntfs3 ou ntfs-3g)", True, True,
               "Partition système de Windows, disques internes et externes utilisés sous Windows."),
    Filesystem(FS_FAT32, "4 Gio moins 1 octet", "lecture et écriture", "lecture et écriture",
               "lecture et écriture", False, False,
               "Partition EFI (ESP), petites clés pour des appareils anciens (autoradio, TV, mise à jour du firmware)."),
    Filesystem(FS_EXFAT, "très grande (plusieurs To)", "lecture et écriture", "lecture et écriture",
               "lecture et écriture (noyau 5.4 et suivants)", False, False,
               "Clés USB, cartes mémoire et disques externes échangés entre Windows, macOS et Linux."),
    Filesystem(FS_EXT4, "16 Tio (blocs de 4 Kio)", "non lu sans outil supplémentaire", "non lu sans outil supplémentaire",
               "lecture et écriture (système de fichiers courant)", True, True,
               "Partition système et partitions de données de Linux."),
)
FILESYSTEMS_BY_NAME = {fs.name: fs for fs in FILESYSTEMS}

USE_WINDOWS_SYSTEM = "partition système Windows"
USE_LINUX = "partition Linux"
USE_ESP = "partition EFI (ESP)"
USE_SHARED_REMOVABLE = "support amovible partagé Windows / macOS / Linux"
USE_LEGACY_DEVICE = "support amovible pour un appareil ancien"
USE_WINDOWS_DATA = "disque de données utilisé seulement sous Windows"
USES = (USE_WINDOWS_SYSTEM, USE_LINUX, USE_ESP, USE_SHARED_REMOVABLE, USE_LEGACY_DEVICE, USE_WINDOWS_DATA)


def filesystem_for(use: str, *, largest_file_bytes: int = 0) -> str:
    """Système de fichiers recommandé par le cours pour un usage.

    Un appareil ancien qui ne lit que FAT32 ne peut pas recevoir de fichier de plus de
    4 Gio : la fonction refuse ce cas (il faut découper le fichier ou changer d'appareil)."""
    if use == USE_WINDOWS_SYSTEM or use == USE_WINDOWS_DATA:
        return FS_NTFS
    if use == USE_LINUX:
        return FS_EXT4
    if use == USE_ESP:
        return FS_FAT32
    if use == USE_SHARED_REMOVABLE:
        return FS_EXFAT
    if use == USE_LEGACY_DEVICE:
        if not fits_on_fat32(largest_file_bytes):
            raise ValueError("Fichier de plus de 4 Gio : impossible en FAT32.")
        return FS_FAT32
    raise ValueError(f"Usage inconnu : {use}")


# =============================================================================================
# 6. Plans de partitions exacts (schémas)
# =============================================================================================


@dataclass(frozen=True)
class PlannedPartition:
    key: str
    name: str
    filesystem: str
    size_label: str
    size_mib: int | None  # None = « reste du disque »
    role: str
    short: str = ""  # libellé court dans le schéma, si le nom est trop long pour sa case


# Windows 10/11 installé en UEFI : disposition de l'installation de Windows (documentation
# Microsoft « partitions de disque dur UEFI/GPT »). Tailles d'un exemple ; la partition de
# récupération varie d'une version à l'autre.
WINDOWS_UEFI_PLAN: tuple[PlannedPartition, ...] = (
    PlannedPartition("esp", "EFI (ESP)", FS_FAT32, "100 Mo", 100, "chargeur de démarrage UEFI (Windows Boot Manager)"),
    PlannedPartition("msr", "MSR", "aucun", "16 Mo", 16, "réservée par Windows, sans lettre ni système de fichiers"),
    PlannedPartition("c", "C: Windows", FS_NTFS, "reste", None, "système, programmes et profils"),
    PlannedPartition("winre", "Récupération", FS_NTFS, "≈ 750 Mo", 750, "environnement de récupération WinRE",
                     "Récup."),
)
# Windows installé en BIOS hérité : table MBR, partition « Réservé au système » active.
WINDOWS_BIOS_PLAN: tuple[PlannedPartition, ...] = (
    PlannedPartition("sysres", "Réservé au système", FS_NTFS, "≈ 500 Mo", 500, "partition active : fichiers de démarrage",
                     "Réservé"),
    PlannedPartition("c", "C: Windows", FS_NTFS, "reste", None, "système, programmes et profils"),
)
# Linux (Debian/Ubuntu) installé en UEFI : exemple d'un poste de travail.
LINUX_UEFI_PLAN: tuple[PlannedPartition, ...] = (
    PlannedPartition("esp", "EFI (ESP)", FS_FAT32, "512 Mo", 512, "chargeur GRUB, monté sur /boot/efi"),
    PlannedPartition("root", "/ (racine)", FS_EXT4, "reste", None, "système, programmes et dossiers personnels"),
    PlannedPartition("swap", "swap", "échange", "4 Go", 4096, "espace d'échange (ou fichier d'échange à la place)"),
)

PLANS: tuple[tuple[str, str, str, tuple[PlannedPartition, ...]], ...] = (
    ("Windows, PC UEFI", TABLE_GPT, "UEFI", WINDOWS_UEFI_PLAN),
    ("Windows, PC BIOS hérité", TABLE_MBR, "BIOS", WINDOWS_BIOS_PLAN),
    ("Linux, PC UEFI", TABLE_GPT, "UEFI", LINUX_UEFI_PLAN),
)


def _segments(plan: tuple[PlannedPartition, ...]) -> tuple[PartitionSegment, ...]:
    weights = {None: 170}
    return tuple(
        PartitionSegment(p.key, (p.short or p.name, p.filesystem, p.size_label),
                         weights.get(p.size_mib, 80))
        for p in plan
    )


def _plan_alt(title: str, plan: tuple[PlannedPartition, ...]) -> str:
    return f"{title} : " + ", ".join(
        f"{p.name} ({p.filesystem}, {p.size_label}, {p.role})" for p in plan
    )


PLANS_FIGURE = Figure(
    key="pr05-plans-partitions",
    title="Trois plans de partitions à connaître (disques système)",
    alt=(
        "Trois barres, du début à la fin du disque. "
        + ". ".join(_plan_alt(f"{title}, table {table}", plan) for title, table, _fw, plan in PLANS)
        + ". Largeurs non proportionnelles aux tailles."
    ),
    caption=(
        "Dispositions créées par les installateurs (tailles d'exemple ; la partition de "
        "récupération de Windows varie). En UEFI, le chargeur est un fichier de la partition "
        "EFI (FAT32) ; en BIOS hérité, c'est la partition active qui démarre. Cases non "
        "proportionnelles."
    ),
    svg=partition_map_svg(tuple(
        (f"{title} — table {table}", _segments(plan)) for title, table, _fw, plan in PLANS
    )),
)

# Cas 4 : poste d'atelier UEFI, SSD NVMe 500 Go (système) + disque dur 2 To (données).
CASE4_SSD_GB = 500
CASE4_HDD_TB = 2
CASE4_HDD_PLAN: tuple[PlannedPartition, ...] = (
    PlannedPartition("d", "D: Données", FS_NTFS, f"{fr_number(gb_to_gib(CASE4_HDD_TB * 1000), 1)} Go (tout le disque)",
                     None, "documents et sauvegardes locales"),
)


def plan_fits(capacity_gib: float, fixed_mib: tuple[int, ...]) -> float:
    """Espace restant (Gio) pour la partition « reste » une fois les partitions de taille fixe
    retirées ; ValueError si elles ne tiennent pas sur le disque."""
    remaining = capacity_gib - sum(fixed_mib) / 1024
    if remaining <= 0:
        raise ValueError("Les partitions fixes dépassent la capacité du disque.")
    return round(remaining, 2)


CASE4_C_GIB = plan_fits(gb_to_gib(CASE4_SSD_GB), tuple(p.size_mib for p in WINDOWS_UEFI_PLAN if p.size_mib))
CASE4_D_GIB = gb_to_gib(CASE4_HDD_TB * 1000)
# Même disposition que `WINDOWS_UEFI_PLAN`, avec la taille calculée de C: (Gio, affichés « Go »).
CASE4_SSD_PLAN: tuple[PlannedPartition, ...] = tuple(
    PlannedPartition(p.key, p.name, p.filesystem, f"≈ {fr_number(CASE4_C_GIB, 1)} Go", p.size_mib, p.role, p.short)
    if p.size_mib is None else p
    for p in WINDOWS_UEFI_PLAN
)

CASE4_FIGURE = Figure(
    key="pr05-plan-poste-atelier",
    title="Cas 4 — Plan de partitions d'un poste UEFI : SSD système et disque de données",
    alt=(
        f"Deux barres. Disque 0, SSD NVMe {CASE4_SSD_GB} Go, table GPT : "
        + ", ".join(f"{p.name} {p.filesystem} {p.size_label}" for p in CASE4_SSD_PLAN)
        + f" (C: environ {CASE4_C_GIB:.0f} Gio). Disque 1, disque dur {CASE4_HDD_TB} To, table GPT : "
        + ", ".join(f"{p.name} {p.filesystem} {p.size_label}" for p in CASE4_HDD_PLAN)
        + f" ({CASE4_D_GIB:.0f} Gio). Largeurs non proportionnelles."
    ),
    caption=(
        "Le système et les programmes sur le SSD rapide, les données sur le disque dur de "
        "grande capacité : une réinstallation de Windows ne touche pas D:. Les deux disques "
        "en GPT (PC UEFI)."
    ),
    svg=partition_map_svg((
        (f"Disque 0 — SSD NVMe {CASE4_SSD_GB} Go, GPT", _segments(CASE4_SSD_PLAN)),
        (f"Disque 1 — disque dur {CASE4_HDD_TB} To, GPT", _segments(CASE4_HDD_PLAN)),
    )),
)

# =============================================================================================
# 7. Entretien : défragmentation, TRIM, SMART
# =============================================================================================

OPT_DEFRAG = "Défragmenter (optimisation du disque dur)"
OPT_TRIM = "TRIM (optimisation du SSD), jamais de défragmentation"
FRAGMENTATION_ALERT = 10  # % fragmenté au-delà duquel on optimise un disque dur (convention du cours)


def optimisation_for(media: str) -> str:
    if media == MEDIA_HDD:
        return OPT_DEFRAG
    if media in (MEDIA_SATA_SSD, MEDIA_NVME_SSD):
        return OPT_TRIM
    raise ValueError(f"Support inconnu : {media}")


def needs_defrag(media: str, fragmented_percent: int) -> bool:
    """Défragmentation manuelle utile ? Seulement sur un disque dur, au-delà du seuil du cours."""
    return media == MEDIA_HDD and fragmented_percent > FRAGMENTATION_ALERT


# Capture fictive de « Optimiser les lecteurs » (Windows), cas 3 et exercice E12.
OPTIMISE_ROWS: tuple[tuple[str, str, str, int | None], ...] = (
    ("C:", MEDIA_NVME_SSD, "OK (3 jours depuis le dernier découpage)", None),
    ("D:", MEDIA_HDD, "Optimisation nécessaire (27 % fragmenté)", 27),
)
OPTIMISE_SCREEN: tuple[str, ...] = (
    "Optimiser les lecteurs (capture fictive)",
    "Lecteur  Type de média        État actuel",
    "C:       Disque SSD           OK (3 jours depuis le",
    "                              dernier découpage)",
    "D:       Disque dur           Optimisation nécessaire",
    "                              (27 % fragmenté)",
    "Optimisation planifiée : activée (hebdomadaire)",
)

SMART_CRC_ATTRIBUTE = "UDMA_CRC_Error_Count"


def smart_reading(attributes: dict[str, int]) -> tuple[str, bool]:
    """(verdict SMART du cours, câble à contrôler ?).

    Le verdict est celui de PR04 (`smart_verdict`). Des erreurs de transfert
    (`UDMA_CRC_Error_Count` > 0) désignent d'abord la **liaison** (câble ou connecteur SATA),
    pas les plateaux : on change le câble avant de condamner le disque."""
    return smart_verdict(attributes), attributes.get(SMART_CRC_ATTRIBUTE, 0) > 0


# =============================================================================================
# 8. Symptômes de stockage : première action non destructive
# =============================================================================================


@dataclass(frozen=True)
class Symptom:
    key: str
    seen: str
    likely: str
    first_action: str
    never: str


SYMPTOMS: tuple[Symptom, ...] = (
    Symptom("absent-uefi", "Disque absent de l'UEFI (firmware)",
            "Câble de données ou d'alimentation, port désactivé, emplacement M.2 non compatible, disque mort.",
            "PC hors tension : reconnecter ou changer câble et port ; vérifier la notice (M.2 SATA ou NVMe, ports partagés).",
            "Accuser le système d'exploitation : s'il n'est pas vu par l'UEFI, le problème est matériel."),
    Symptom("non-initialise", "Disque vu dans l'UEFI, « Non initialisé » dans Gestion des disques",
            "Disque neuf jamais préparé, ou table de partitions détruite sur un disque qui contenait des données.",
            "Disque neuf : initialiser (GPT) puis créer un volume. Disque qui contenait des données : ne rien initialiser, récupérer d'abord.",
            "Initialiser ou formater un disque qui contenait des données avant de les avoir récupérées."),
    Symptom("sans-lettre", "Partition saine visible dans Gestion des disques, absente de l'Explorateur",
            "Pas de lettre de lecteur attribuée.",
            "« Modifier la lettre de lecteur et les chemins d'accès » : attribuer une lettre libre.",
            "Formater une partition saine pour la faire apparaître."),
    Symptom("raw", "Volume « RAW », Windows propose de formater",
            "Système de fichiers endommagé (arrachage, coupure) ou disque qui se dégrade.",
            "Refuser le formatage, lire l'état SMART, copier les données (image si le disque faiblit), puis réparer.",
            "Accepter le formatage proposé : les données deviennent beaucoup plus difficiles à récupérer."),
    Symptom("plein", "C: plein (barre rouge), mises à jour impossibles, lenteurs",
            "Fichiers temporaires, anciennes mises à jour, téléchargements, corbeille, gros dossiers personnels.",
            "Mesurer ce qui occupe l'espace (Stockage), Nettoyage de disque, déplacer les données personnelles vers D:.",
            "Supprimer des fichiers à la main dans C:\\Windows ou des dossiers de programmes."),
    Symptom("boot", "« No bootable device » ou « Operating system not found » au démarrage",
            "Disque non détecté, ordre de démarrage, mode UEFI / BIOS hérité incohérent avec la table (GPT/MBR), partition EFI abîmée.",
            "UEFI : disque détecté ? Gestionnaire de démarrage en premier ? Mode UEFI pour un disque GPT ? Puis réparation du démarrage (PR11).",
            "Réinstaller Windows d'emblée, ce qui écrase le disque."),
)
SYMPTOMS_BY_KEY = {s.key: s for s in SYMPTOMS}


def boot_mode_consistent(table: str, firmware_mode: str) -> bool:
    """Windows démarre d'un disque GPT en mode UEFI et d'un disque MBR en BIOS hérité (CSM)."""
    return (table, firmware_mode) in ((TABLE_GPT, "UEFI"), (TABLE_MBR, "BIOS"))


# =============================================================================================
# 9. Les cinq procédures illustrées
# =============================================================================================

# Procédure 1 — avant toute opération sur un disque (règle non destructive).
SAFE_STEPS: tuple[tuple[str, str], ...] = (
    ("Identifier le disque", "Modèle, capacité, numéro de disque (Disque 1, /dev/sdb) : on agit sur le bon."),
    ("Lire l'état SMART", "Un disque qui faiblit se copie d'abord, il ne se repartitionne pas."),
    ("Sauvegarder", "Copie des données sur un autre support, accord écrit du propriétaire."),
    ("Vérifier la copie", "Ouvrir quelques fichiers sur la copie : une sauvegarde non relue n'existe pas."),
    ("Noter l'état actuel", "Capture ou relevé des partitions avant modification."),
    ("Agir", "Une opération à la fois, en relisant le disque et la partition sélectionnés."),
    ("Contrôler", "Partitions, lettres, espace libre, données présentes : comparer au relevé."),
)

# Procédure 2 — ajouter un disque de données neuf sous Windows (Gestion des disques).
WIN_NEW_DISK_STEPS: tuple[tuple[str, str], ...] = (
    ("Installer", "PC hors tension : disque fixé, câbles SATA de données et d'alimentation (ou M.2)."),
    ("Vérifier l'UEFI", "Le disque apparaît avec sa capacité dans le firmware."),
    ("Ouvrir Gestion des disques", "diskmgmt.msc : le disque est « Non initialisé »."),
    ("Initialiser en GPT", "Table GPT sur un PC UEFI ou pour un disque de plus de 2 Tio."),
    ("Nouveau volume simple", "Clic droit sur l'espace « Non alloué » : taille, lettre D:."),
    ("Formater", "NTFS, taille d'unité d'allocation par défaut, nom « Données », formatage rapide."),
    ("Contrôler", "D: visible dans l'Explorateur, capacité attendue, fichier test écrit puis relu."),
)

# Procédure 3 — partitionner, formater et monter un disque sous Linux.
LINUX_NEW_DISK_STEPS: tuple[tuple[str, str], ...] = (
    ("Repérer le disque", "lsblk -f : nouveau disque sans partition (ex. /dev/sdb), taille vérifiée."),
    ("Créer la table", "sudo parted /dev/sdb mklabel gpt (disque vide uniquement)."),
    ("Créer la partition", "sudo parted -a optimal /dev/sdb mkpart donnees ext4 0% 100%."),
    ("Formater", "sudo mkfs.ext4 -L donnees /dev/sdb1."),
    ("Monter", "sudo mkdir -p /srv/donnees puis sudo mount /dev/sdb1 /srv/donnees."),
    ("Rendre permanent", "UUID lu avec blkid, ligne ajoutée dans /etc/fstab, test sudo mount -a."),
    ("Contrôler", "df -h /srv/donnees : taille attendue ; redémarrage : montage automatique."),
)

# Procédure 4 — optimiser un lecteur selon son type.
OPTIMISE_STEPS: tuple[tuple[str, str], ...] = (
    ("Identifier le support", "Type de média dans « Optimiser les lecteurs » : disque dur ou SSD."),
    ("Lire l'état SMART", "Disque dur qui faiblit : sauvegarder, ne pas défragmenter."),
    ("Libérer de l'espace", "Nettoyage de disque : la défragmentation a besoin d'espace libre."),
    ("Optimiser", "Disque dur : défragmentation. SSD : TRIM (« découpage »), jamais de défragmentation."),
    ("Planifier", "Optimisation automatique hebdomadaire activée (fstrim.timer sous Linux)."),
    ("Contrôler", "État « OK », pourcentage fragmenté, date de la dernière optimisation."),
)

# Procédure 5 — disque non détecté (diagnostic du plus simple au plus lourd).
NOT_DETECTED_STEPS: tuple[tuple[str, str], ...] = (
    ("Observer", "Absent de l'UEFI, ou présent dans l'UEFI mais pas dans le système ?"),
    ("Contrôler les câbles", "PC hors tension : données et alimentation reconnectés, autre câble, autre port."),
    ("Lire la notice", "Emplacement M.2 SATA ou NVMe, ports SATA désactivés quand un M.2 est occupé."),
    ("Vérifier l'UEFI", "Port activé, mode SATA (AHCI) inchangé, disque listé."),
    ("Vérifier le système", "Gestion des disques ou lsblk : non initialisé, sans lettre, non monté ?"),
    ("Tester ailleurs", "Disque sur un autre PC ou dans un boîtier USB : il est vu ou non."),
    ("Conclure", "Câble, port, réglage ou disque à remplacer ; valeurs et actions dans le rapport."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Avant toute opération sur un disque", SAFE_STEPS),
    ("Ajouter un disque de données sous Windows", WIN_NEW_DISK_STEPS),
    ("Partitionner, formater et monter un disque sous Linux", LINUX_NEW_DISK_STEPS),
    ("Optimiser un lecteur selon son type", OPTIMISE_STEPS),
    ("Retrouver un disque non détecté", NOT_DETECTED_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


SAFE_FIGURE = Figure(
    key="pr05-avant-operation",
    title="Procédure 1 — Avant toute opération sur un disque",
    alt=_procedure_alt("Règle non destructive avant de partitionner, formater ou optimiser.", SAFE_STEPS),
    caption=(
        "Partitionner ou formater détruit l'accès aux données : on identifie le bon disque, "
        "on lit son état, on sauvegarde et on vérifie la copie avant d'agir."
    ),
    svg=step_flow_svg(SAFE_STEPS),
)

WIN_NEW_DISK_FIGURE = Figure(
    key="pr05-disque-windows",
    title="Procédure 2 — Ajouter un disque de données sous Windows",
    alt=_procedure_alt("Installation et préparation d'un disque neuf avec Gestion des disques.", WIN_NEW_DISK_STEPS),
    caption=(
        "Initialiser un disque neuf ne fait perdre aucune donnée ; initialiser un disque qui "
        "contenait des fichiers les rend inaccessibles."
    ),
    svg=step_flow_svg(WIN_NEW_DISK_STEPS),
)

LINUX_NEW_DISK_FIGURE = Figure(
    key="pr05-disque-linux",
    title="Procédure 3 — Partitionner, formater et monter un disque sous Linux",
    alt=_procedure_alt("Préparation d'un disque de données neuf sous Linux.", LINUX_NEW_DISK_STEPS),
    caption=(
        "Le nom /dev/sdb est un exemple : il se vérifie avec lsblk à chaque fois. Dans "
        "/etc/fstab, on désigne la partition par son UUID, qui ne change pas si l'ordre des "
        "disques change."
    ),
    svg=step_flow_svg(LINUX_NEW_DISK_STEPS),
)

OPTIMISE_FIGURE = Figure(
    key="pr05-optimiser",
    title="Procédure 4 — Optimiser un lecteur selon son type",
    alt=_procedure_alt("Optimisation d'un disque dur ou d'un SSD.", OPTIMISE_STEPS),
    caption=(
        "Windows choisit lui-même : défragmentation pour un disque dur, TRIM (« découpage ») "
        "pour un SSD. Défragmenter un SSD n'apporte rien et consomme des écritures."
    ),
    svg=step_flow_svg(OPTIMISE_STEPS),
)

NOT_DETECTED_FIGURE = Figure(
    key="pr05-disque-non-detecte",
    title="Procédure 5 — Retrouver un disque non détecté",
    alt=_procedure_alt("Diagnostic d'un disque qui n'apparaît pas.", NOT_DETECTED_STEPS),
    caption=(
        "Du plus simple au plus lourd, sans rien effacer : un disque absent de l'UEFI est un "
        "problème matériel ; présent dans l'UEFI mais invisible dans le système, il est "
        "souvent non initialisé, sans lettre ou non monté."
    ),
    svg=step_flow_svg(NOT_DETECTED_STEPS),
)

# Arbre : le disque « disparu » de l'Explorateur.
MISSING_TREE: tuple[tuple[str, str], ...] = (
    ("Le disque apparaît-il dans l'UEFI ?",
     "Problème matériel : câbles, port, emplacement M.2, réglage ; sinon disque à remplacer."),
    ("Apparaît-il dans Gestion des disques ?",
     "Pilote du contrôleur (RAID/VMD) ou mode SATA modifié : voir la notice et PR08."),
    ("Est-il initialisé, avec une partition ?",
     "Disque neuf : initialiser en GPT. Disque qui avait des données : ne rien faire, récupérer."),
    ("La partition a-t-elle un système de fichiers lisible ?",
     "RAW : refuser le formatage, SMART, copier les données, puis réparer."),
)
MISSING_TREE_FINAL = "Partition saine sans lettre : attribuer une lettre de lecteur (aucune donnée touchée)."

MISSING_TREE_FIGURE = Figure(
    key="pr05-disque-invisible",
    title="Arbre de décision — un disque n'apparaît pas dans l'Explorateur",
    alt=(
        "Arbre de décision en quatre questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(MISSING_TREE, start=1))
        + f" Si toutes les réponses sont oui : {MISSING_TREE_FINAL}"
    ),
    caption=(
        "Chaque branche commence par une action qui ne modifie pas le disque. Formater ou "
        "initialiser n'est jamais la première réponse quand des données sont en jeu."
    ),
    svg=decision_tree_svg(MISSING_TREE, MISSING_TREE_FINAL),
)

# =============================================================================================
# 10. Captures fictives
# =============================================================================================

# Cas 1 : nouveau disque dur de 2 To à côté d'un SSD système de 512 Go (Gestion des disques).
CASE1_GIB = gb_to_gib(2000)
CASE1_SSD_GIB = gb_to_gib(512)
CASE1_C_GIB = plan_fits(CASE1_SSD_GIB, tuple(p.size_mib for p in WINDOWS_UEFI_PLAN if p.size_mib))
CASE1_SCREEN: tuple[str, ...] = (
    "Gestion des disques (capture fictive)",
    f"Disque 0   De base   {fr_number(CASE1_SSD_GIB)} Go   En ligne",
    f"  EFI 100 Mo | C: {fr_number(CASE1_C_GIB)} Go NTFS | Récup. 750 Mo",
    f"Disque 1   Inconnu   {fr_number(CASE1_GIB)} Go   Non initialisé",
    f"  {fr_number(CASE1_GIB)} Go  Non alloué",
)

# Procédure 3 illustrée : lsblk avant / après (Linux).
LSBLK_SCREEN: tuple[str, ...] = (
    "$ lsblk -f",
    "NAME        FSTYPE LABEL   MOUNTPOINTS",
    "nvme0n1",
    "├─nvme0n1p1 vfat           /boot/efi",
    "├─nvme0n1p2 ext4           /",
    "└─nvme0n1p3 swap           [SWAP]",
    "sdb",
    "$ sudo parted /dev/sdb mklabel gpt",
    "$ sudo parted -a optimal /dev/sdb mkpart donnees \\",
    "    ext4 0% 100%",
    "$ sudo mkfs.ext4 -L donnees /dev/sdb1",
    "$ lsblk -f /dev/sdb",
    "NAME   FSTYPE LABEL   MOUNTPOINTS",
    "sdb",
    "└─sdb1 ext4   donnees",
)

FSTAB_LINE = "UUID=3f6c…a9e2  /srv/donnees  ext4  defaults  0  2"

DISKMGMT_FIGURE = Figure(
    key="pr05-gestion-disques",
    title="Cas 1 — Un disque neuf « Non initialisé » dans Gestion des disques (fictif)",
    alt="Capture texte de Gestion des disques. " + " ; ".join(CASE1_SCREEN) + ".",
    caption=(
        f"Le disque dur vendu « 2 To » apparaît avec {fr_number(CASE1_GIB)} Go (en réalité des "
        "Gio). « Non initialisé » et « Non alloué » : disque neuf, jamais préparé. Capture fictive."
    ),
    svg=screen_svg(CASE1_SCREEN, label="Capture fictive — pas un écran officiel"),
)

LSBLK_FIGURE = Figure(
    key="pr05-lsblk",
    title="Procédure 3 en console : lsblk, parted et mkfs.ext4 (fictif)",
    alt="Terminal Linux : " + " / ".join(line.strip() for line in LSBLK_SCREEN) + ".",
    caption=(
        "Avant : sdb n'a aucune partition. Après : sdb1 en ext4, nommée « donnees ». Le disque "
        "système (nvme0n1) n'est jamais désigné dans les commandes. Capture fictive."
    ),
    svg=screen_svg(LSBLK_SCREEN, label="Capture fictive — terminal Linux"),
)

OPTIMISE_SCREEN_FIGURE = Figure(
    key="pr05-optimiser-lecteurs",
    title="« Optimiser les lecteurs » : un SSD et un disque dur (fictif)",
    alt="Capture texte de l'outil Optimiser les lecteurs. " + " ; ".join(OPTIMISE_SCREEN) + ".",
    caption=(
        "Pour le SSD, Windows indique le dernier « découpage » (TRIM) ; pour le disque dur, le "
        "pourcentage fragmenté. Seul D: a besoin d'une défragmentation. Capture fictive."
    ),
    svg=screen_svg(OPTIMISE_SCREEN, label="Capture fictive — pas un écran officiel"),
)

PR05_FIGURES: tuple[Figure, ...] = (
    PLANS_FIGURE,
    SAFE_FIGURE,
    WIN_NEW_DISK_FIGURE,
    DISKMGMT_FIGURE,
    LINUX_NEW_DISK_FIGURE,
    LSBLK_FIGURE,
    OPTIMISE_FIGURE,
    OPTIMISE_SCREEN_FIGURE,
    NOT_DETECTED_FIGURE,
    MISSING_TREE_FIGURE,
    CASE4_FIGURE,
)

"""PR09 « Installation complète de Linux — préparation et dépannage » — données de référence,
règles de décision et schémas SVG (ticket #209).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket209_ampcr_pratique_pr09.py` :

- l'inventaire du poste (`INVENTORY_FIELDS`) ;
- les distributions courantes et leurs outils (`DISTRIBUTIONS`, `PACKAGE_COMMANDS`) et le choix
  selon l'usage (`USAGE_CHOICES`, convention du cours) ;
- le contrôle d'intégrité de l'image (`checksum_verdict`) ;
- les partitions d'une installation de Linux (`LINUX_ONLY_LAYOUT`, `DUAL_BOOT_LAYOUT`), les
  points de montage (`MOUNT_POINTS`), le repère de taille du swap (`swap_advice`) et la règle
  de prudence du double démarrage (`dual_boot_action`) ;
- le dépannage par six familles (`TROUBLESHOOTING`) : disque non vu, chargeur de démarrage,
  fstab/UUID, réseau absent, permissions et sudo, espace disque ;
- trois procédures illustrées (`PREP_STEPS`, `SETUP_STEPS`, `FINAL_STEPS`) : les mêmes tuples
  dessinent les schémas et alimentent les remises en ordre des exercices ;
- la liste de contrôle finale (`CHECKLIST`) et le plan du rapport (`REPORT_SECTIONS`).

Les installateurs cités (Ubuntu, Linux Mint, Debian, Fedora) sont décrits **au moment de la
rédaction (octobre 2026)** ; leurs libellés changent selon la version : la documentation de la
distribution fait foi. Les sorties de terminal sont montrées **en anglais** (système configuré en
anglais, ou commande précédée de `LANG=C`) : en français, une partie des messages est traduite.
Les captures sont **fictives** et parfois abrégées ; aucun schéma ne vient d'une image générée ni
d'une photographie.
"""

from dataclasses import dataclass

from app.v1.ampcr_pratique_visuals import (
    Figure,
    PartitionSegment,
    decision_tree_svg,
    partition_map_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR08)
WRITTEN_AT = "octobre 2026"
FICTIVE_LABEL = "Capture fictive — sortie abrégée"

# =============================================================================================
# 1. Inventaire du poste avant l'intervention
# =============================================================================================

# (rubrique de la fiche, ce qu'on relève, pourquoi)
INVENTORY_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("Identification", "Marque, modèle, numéro de série, propriétaire",
     "Tracer l'intervention et retrouver la documentation du modèle."),
    ("Processeur et mémoire", "Modèle, 64 bits, quantité de mémoire",
     "Choisir la distribution et le bureau ; prévoir le swap."),
    ("Stockage", "Disques (type, capacité, MBR ou GPT), partitions, données présentes",
     "Choisir le disque cible et repérer ce qu'il faut sauvegarder."),
    ("Firmware", "Mode UEFI ou hérité, démarrage sécurisé, mode du contrôleur (AHCI, RAID, Intel RST/VMD)",
     "Démarrer la clé dans le bon mode ; anticiper un disque non vu."),
    ("Réseau et graphique", "Puces Ethernet, Wi-Fi et carte graphique (lspci -nn)",
     "Prévoir un pilote non libre (Wi-Fi Broadcom, NVIDIA) et un câble réseau."),
    ("Système en place", "Windows à garder ? BitLocker, clé de récupération, démarrage rapide",
     "Double démarrage : préparer Windows avant de toucher au disque."),
    ("Usage et comptes", "Utilisateurs, logiciels nécessaires, imprimante, partages",
     "Choisir la distribution et créer les bons comptes."),
)

# =============================================================================================
# 2. Distributions et gestionnaires de paquets
# =============================================================================================


@dataclass(frozen=True)
class Distribution:
    name: str
    family: str
    package_manager: str
    bootloader: str
    default_fs: str
    support: str


APT = "apt"
DNF = "dnf"

# Valeurs par défaut des installateurs graphiques (octobre 2026, la documentation fait foi).
DISTRIBUTIONS: tuple[Distribution, ...] = (
    Distribution("Ubuntu LTS", "Debian", APT, "GRUB", "ext4", "5 ans de mises à jour standard"),
    Distribution("Linux Mint", "Debian (base Ubuntu LTS)", APT, "GRUB", "ext4", "celui de l'Ubuntu LTS de base"),
    Distribution("Debian stable", "Debian", APT, "GRUB", "ext4", "environ 3 ans, puis suivi à long terme (LTS)"),
    Distribution("Fedora Workstation", "Red Hat", DNF, "GRUB", "Btrfs", "environ 13 mois par version"),
    Distribution("Pop!_OS", "Debian (base Ubuntu)", APT, "systemd-boot", "ext4", "celui de l'Ubuntu de base"),
)
DISTRIBUTIONS_BY_NAME = {d.name: d for d in DISTRIBUTIONS}

# (action, commande apt, commande dnf) — commandes exactes, à lancer avec sudo si elles modifient.
PACKAGE_COMMANDS: tuple[tuple[str, str, str], ...] = (
    ("Rafraîchir la liste des paquets", "sudo apt update", "(dnf rafraîchit lui-même ses métadonnées)"),
    ("Installer les mises à jour", "sudo apt upgrade", "sudo dnf upgrade"),
    ("Installer un logiciel", "sudo apt install vlc", "sudo dnf install vlc"),
    ("Retirer un logiciel", "sudo apt remove vlc", "sudo dnf remove vlc"),
    ("Rechercher un paquet", "apt search vlc", "dnf search vlc"),
    ("Supprimer les paquets devenus inutiles", "sudo apt autoremove", "sudo dnf autoremove"),
    ("Vider le cache des paquets téléchargés", "sudo apt clean", "sudo dnf clean all"),
)


def package_manager_of(distribution: str) -> str:
    """Gestionnaire de paquets d'une distribution du tableau (KeyError sinon)."""
    return DISTRIBUTIONS_BY_NAME[distribution].package_manager


# (usage du client, choix conseillé, raison) — convention du cours, pas une norme.
USAGE_CHOICES: tuple[tuple[str, str, str], ...] = (
    ("Débutant, bureautique et Internet, PC récent", "Ubuntu LTS ou Linux Mint",
     "Installation guidée, support long, documentation en français abondante."),
    ("PC ancien (4 Go de mémoire), usage léger", "Linux Mint Xfce (ou un autre bureau léger)",
     "Bureau sobre en mémoire, base Ubuntu LTS."),
    ("Serveur de fichiers d'une petite structure", "Debian stable (ou Ubuntu Server LTS)",
     "Stabilité, longue durée de support, peu de changements."),
    ("Développeur qui veut des logiciels récents", "Fedora Workstation",
     "Versions récentes, cycle court (mise à niveau environ chaque année)."),
)

# =============================================================================================
# 3. Image ISO et contrôle d'intégrité
# =============================================================================================

ISO_OK = "Image intègre : on peut écrire la clé"
ISO_BAD = "Image corrompue ou modifiée : la supprimer et la retélécharger"
ISO_UNKNOWN = "Rien de vérifié : la somme de l'image n'est pas dans le fichier"
ISO_VERDICTS = (ISO_OK, ISO_BAD, ISO_UNKNOWN)


def checksum_verdict(sha256sum_line: str) -> str:
    """Verdict d'après la ligne affichée par `sha256sum -c` pour l'image (« fichier: OK » ou
    « fichier: FAILED ») ; une autre sortie ne prouve rien."""
    status = sha256sum_line.rsplit(":", 1)[-1].strip()
    if status == "OK":
        return ISO_OK
    if status.startswith("FAILED"):
        return ISO_BAD
    return ISO_UNKNOWN


ISO_NAME = "ubuntu-24.04.3-desktop-amd64.iso"

ISO_CHECK_SCREEN: tuple[str, ...] = (
    "$ ls ~/Téléchargements",
    f"SHA256SUMS  {ISO_NAME}",
    "$ cd ~/Téléchargements",
    "$ sha256sum -c SHA256SUMS --ignore-missing",
    f"{ISO_NAME}: OK",
    "$ lsblk -d -o NAME,SIZE,TRAN,MODEL",
    "NAME      SIZE TRAN MODEL",
    "sda     931.5G sata ST1000DM010",
    "sdb      14.6G usb  DataTraveler 3.0",
    "nvme0n1 476.9G nvme Samsung SSD 970",
)

# =============================================================================================
# 4. Partitions, points de montage, swap
# =============================================================================================


@dataclass(frozen=True)
class LinuxPartition:
    key: str
    name: str
    filesystem: str
    mount_point: str
    size_label: str
    role: str


ESP = LinuxPartition("esp", "Partition système EFI (ESP)", "FAT32 (vfat)", "/boot/efi", "≈ 300 Mo à 1 Go",
                     "Chargeur de démarrage lu par le firmware UEFI (shim, GRUB).")
ROOT = LinuxPartition("root", "Racine", "ext4", "/", "25 Go au moins (40 à 60 Go confortable)",
                      "Système et logiciels ; /etc, /var, /usr.")
HOME = LinuxPartition("home", "Dossiers personnels (facultative)", "ext4", "/home", "le reste",
                      "Données des utilisateurs, conservées si l'on réinstalle le système.")
SWAP = LinuxPartition("swap", "Swap (partition ou fichier)", "swap", "[SWAP]", "selon la mémoire et l'hibernation",
                      "Prolonge la mémoire ; indispensable pour l'hibernation.")

LINUX_ONLY_LAYOUT: tuple[LinuxPartition, ...] = (ESP, ROOT, SWAP, HOME)

MOUNT_POINTS: tuple[str, ...] = (ESP.mount_point, ROOT.mount_point, HOME.mount_point, SWAP.mount_point)


def swap_advice(ram_gb: float, *, hibernation: bool) -> float | None:
    """Taille indicative du swap en Go (tableau de recommandations de la documentation Red Hat,
    repris comme repère du cours) ; None : hibernation déconseillée au-delà de 64 Go."""
    if ram_gb <= 0:
        raise ValueError(ram_gb)
    if ram_gb <= 2:
        return ram_gb * (3 if hibernation else 2)
    if ram_gb <= 8:
        return ram_gb * (2 if hibernation else 1)
    if ram_gb <= 64:
        return ram_gb * 1.5 if hibernation else 4
    return None if hibernation else 4


# --- Double démarrage avec un Windows à garder -----------------------------------------------

PK_ESP = "esp"
PK_MSR = "msr"
PK_WINDOWS = "windows"
PK_RECOVERY = "recovery"
PK_DATA = "data"
PK_FREE = "free"

DB_REUSE = "Réutiliser sans formater (/boot/efi)"
DB_KEEP = "Ne pas toucher"
DB_CREATE = "Créer les partitions de Linux"
DB_STOP = "Arrêter : sauvegarde et accord d'abord"
DUAL_BOOT_ACTIONS = (DB_REUSE, DB_KEEP, DB_CREATE, DB_STOP)


def dual_boot_action(kind: str, *, backup_verified: bool, written_consent: bool) -> str:
    """Ce que le technicien fait de chaque zone du disque dans le partitionnement manuel d'un
    double démarrage : rien n'est créé ni modifié sans sauvegarde vérifiée ET accord écrit ;
    l'ESP de Windows est réutilisée **sans formatage** ; les partitions de Windows et les données
    ne sont jamais touchées ; Linux s'installe dans l'espace libre préparé depuis Windows."""
    if kind not in (PK_ESP, PK_MSR, PK_WINDOWS, PK_RECOVERY, PK_DATA, PK_FREE):
        raise ValueError(kind)
    if not (backup_verified and written_consent):
        return DB_STOP
    if kind == PK_ESP:
        return DB_REUSE
    if kind == PK_FREE:
        return DB_CREATE
    return DB_KEEP


# (zone, nature, largeur relative) — disque de 512 Go après réduction de Windows depuis Windows.
DUAL_BOOT_LAYOUT: tuple[tuple[str, str, tuple[str, ...], int], ...] = (
    ("esp", PK_ESP, ("ESP", "FAT32", "100 Mo"), 3),
    ("msr", PK_MSR, ("MSR", "16 Mo"), 2),
    ("windows", PK_WINDOWS, ("Windows C:", "NTFS", "réduite"), 4),
    ("recovery", PK_RECOVERY, ("Récup.", "NTFS"), 3),
    ("linux-root", PK_FREE, ("Linux /", "ext4", "ex-espace libre"), 5),
)

_LINUX_ONLY_SEGMENTS = (
    PartitionSegment("esp", ("ESP", "FAT32", "/boot/efi"), 3),
    PartitionSegment("root", ("/", "ext4", "60 Go"), 4),
    PartitionSegment("swap", ("swap", "8 Go"), 2),
    PartitionSegment("home", ("/home", "ext4", "le reste"), 5),
)

LAYOUT_FIGURE = Figure(
    key="pr09-partitions",
    title="Deux plans de partitionnement en GPT : Linux seul, et double démarrage avec Windows",
    alt=(
        "Deux disques GPT, du début à la fin. Disque 1, Linux seul : "
        + " ; ".join(f"{p.name}, {p.filesystem}, monté sur {p.mount_point}, {p.size_label}"
                     for p in LINUX_ONLY_LAYOUT)
        + ". Disque 2, double démarrage : partition système EFI de Windows (FAT32, 100 Mo) "
        "réutilisée sans formatage par Linux, partition réservée Microsoft, Windows C: réduite "
        "depuis Windows, partition de récupération, puis la racine de Linux en ext4 dans l'espace "
        "libéré. Les largeurs ne sont pas à l'échelle."
    ),
    caption=(
        "Linux seul : ESP, racine, swap et /home facultative. Double démarrage : on réutilise "
        "l'ESP de Windows sans la formater et on n'installe Linux que dans l'espace libéré depuis "
        "Windows. Largeurs non à l'échelle."
    ),
    svg=partition_map_svg((
        ("Disque A — SSD 512 Go, Linux seul", _LINUX_ONLY_SEGMENTS),
        ("Disque B — SSD 512 Go, Windows + Linux",
         tuple(PartitionSegment(key, lines, weight) for key, _kind, lines, weight in DUAL_BOOT_LAYOUT)),
    )),
)

# =============================================================================================
# 5. Chargeur de démarrage
# =============================================================================================

EFIBOOT_SCREEN: tuple[str, ...] = (
    "$ efibootmgr",
    "BootCurrent: 0000",
    "Timeout: 0 seconds",
    "BootOrder: 0000,0001,0002",
    "Boot0000* Windows Boot Manager",
    "Boot0001* ubuntu",
    "Boot0002* UEFI: USB DataTraveler 3.0",
    "$ sudo efibootmgr -o 0001,0000,0002",
    "BootOrder: 0001,0000,0002",
)


def first_boot_entry(efibootmgr_lines: tuple[str, ...]) -> str:
    """Nom de l'entrée démarrée en premier d'après la sortie de `efibootmgr` (dernier
    « BootOrder » affiché)."""
    order = [line for line in efibootmgr_lines if line.startswith("BootOrder:")][-1]
    first = order.split(":", 1)[1].strip().split(",")[0]
    entry = next(line for line in efibootmgr_lines if line.startswith(f"Boot{first}"))
    return entry.split(" ", 1)[1].strip()


# =============================================================================================
# 6. Dépannage
# =============================================================================================

TR_DISK = "Disque non vu"
TR_BOOT = "Chargeur de démarrage"
TR_FSTAB = "fstab et UUID"
TR_NET = "Réseau absent"
TR_PERM = "Permissions et sudo"
TR_SPACE = "Espace disque"
TR_CATEGORIES = (TR_DISK, TR_BOOT, TR_FSTAB, TR_NET, TR_PERM, TR_SPACE)


@dataclass(frozen=True)
class Trouble:
    category: str
    symptom: str
    check: str
    action: str
    never: str


TROUBLESHOOTING: tuple[Trouble, ...] = (
    Trouble(
        TR_DISK,
        "L'installateur ne propose aucun disque, ou signale Intel RST, alors que le firmware voit le SSD",
        "Firmware : contrôleur en RAID / Intel RST / VMD ; session live : lsblk ne liste pas le SSD.",
        "Disque sans Windows à garder : mode AHCI si la notice le permet. Windows à garder : passer en "
        "AHCI depuis Windows selon la procédure de Microsoft, d'abord.",
        "Changer le mode du contrôleur sous un Windows installé sans préparation (il ne démarre plus).",
    ),
    Trouble(
        TR_DISK,
        "Le firmware lui-même ne voit pas le disque",
        "Branchement, câble SATA, port M.2 compatible (NVMe ou SATA), disque testé ailleurs.",
        "Diagnostic matériel (PR05, PR06) avant toute installation.",
        "Conclure à un problème de Linux et recommencer l'installation.",
    ),
    Trouble(
        TR_BOOT,
        "Après l'installation, le PC démarre directement sous Windows, sans menu GRUB",
        "efibootmgr : l'entrée « Windows Boot Manager » passe avant « ubuntu ».",
        "Mettre l'entrée de Linux en premier : sudo efibootmgr -o … ou ordre de démarrage du firmware.",
        "Réinstaller Linux, ou formater l'ESP.",
    ),
    Trouble(
        TR_BOOT,
        "« grub rescue> » ou « Secure Boot violation » au démarrage",
        "Partition de GRUB supprimée ou déplacée (lsblk en session live) ; image non signée.",
        "Session live, sauvegarde, réinstallation de GRUB selon la documentation de la distribution "
        "(PR11) ; distribution compatible avec le démarrage sécurisé.",
        "Désactiver le démarrage sécurisé « pour voir », ou formater une partition.",
    ),
    Trouble(
        TR_FSTAB,
        "« You are in emergency mode » après le remplacement ou le reformatage d'un disque",
        "journalctl -xb ; comparer les UUID de /etc/fstab à ceux de lsblk -f (ou blkid).",
        "Copie de fstab, ligne corrigée (bon UUID, ou option nofail pour un disque secondaire), "
        "findmnt --verify puis mount -a, redémarrage.",
        "Désigner un disque par /dev/sdb1 (le nom peut changer) ou supprimer la ligne sans comprendre.",
    ),
    Trouble(
        TR_NET,
        "Pas de Wi-Fi : aucun réseau proposé",
        "lspci -nnk : pas de ligne « Kernel driver in use » sous la carte réseau ; identifiant [14e4:…].",
        "Câble Ethernet, puis pilote de la distribution (« Pilotes additionnels », paquet du dépôt).",
        "Installer un pilote d'un site inconnu, ou compiler un module trouvé sur un forum.",
    ),
    Trouble(
        TR_NET,
        "Câble branché mais pas de réseau",
        "ip a : NO-CARRIER (lien absent) ; adresse IPv4 ? ip route : passerelle ? ping de la passerelle "
        "puis d'un nom.",
        "Couche par couche : câble et prise, DHCP (NetworkManager), passerelle, DNS (PR24).",
        "Réinstaller le système pour un câble débranché.",
    ),
    Trouble(
        TR_PERM,
        "« Permission denied » sur un fichier de l'utilisateur, ou « is not in the sudoers file »",
        "ls -l : propriétaire et droits ; groups : membre du groupe sudo (wheel sous Fedora) ?",
        "Rendre ses fichiers à l'utilisateur (sudo chown) ; ajouter au groupe sudo seulement un "
        "administrateur prévu (sudo usermod -aG sudo nom).",
        "chmod -R 777, travailler en root, ou donner sudo à tous les comptes.",
    ),
    Trouble(
        TR_SPACE,
        "« No space left on device », mises à jour impossibles",
        "df -h (Use% 100 %) et df -i ; du -sh sur /var/log, /var/cache/apt, /home.",
        "sudo apt clean, sudo apt autoremove, journalctl --vacuum-size ; données déplacées ; partition "
        "agrandie après sauvegarde.",
        "Supprimer au hasard des fichiers de /usr, /var/lib ou /boot.",
    ),
)

TROUBLES_BY_CATEGORY: dict[str, tuple[Trouble, ...]] = {
    c: tuple(t for t in TROUBLESHOOTING if t.category == c) for c in TR_CATEGORIES
}

BOOT_TREE: tuple[tuple[str, str], ...] = (
    ("Le firmware voit-il le disque ?",
     "Matériel : branchement, port M.2, disque (PR05, PR06)."),
    ("L'entrée de Linux est-elle en tête ?",
     "efibootmgr -o ou ordre de démarrage du firmware."),
    ("GRUB s'affiche-t-il (pas grub rescue) ?",
     "Session live, lsblk, sauvegarde, réinstaller GRUB (PR11)."),
    ("Le bureau s'ouvre-t-il (pas de mode d'urgence) ?",
     "fstab et UUID : comparer à lsblk -f, corriger une copie."),
)
BOOT_FINAL = (
    "Démarrage correct : vérifier aussi l'entrée de Windows en double démarrage, puis le noter "
    "dans le rapport."
)

BOOT_TREE_FIGURE = Figure(
    key="pr09-demarrage",
    title="Arbre de décision — Linux ne démarre pas après l'installation",
    alt=(
        "Arbre de décision en quatre questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(BOOT_TREE, start=1))
        + f" Si toutes les réponses sont oui : {BOOT_FINAL}"
    ),
    caption=(
        "On suit le démarrage dans l'ordre : matériel, firmware, chargeur, puis montages du "
        "système. Aucun formatage, aucune réinstallation à l'aveugle."
    ),
    svg=decision_tree_svg(BOOT_TREE, BOOT_FINAL),
)

# =============================================================================================
# 7. Procédures illustrées
# =============================================================================================

PREP_STEPS: tuple[tuple[str, str], ...] = (
    ("Recueillir la demande", "Usage, données à garder, Windows à conserver ? Accord écrit du client."),
    ("Inventorier le poste", "Mémoire, disques, firmware, puces réseau et graphique, BitLocker."),
    ("Choisir la distribution", "Selon l'usage et le matériel ; version à support long."),
    ("Sauvegarder", "Données de tous les comptes sur un autre support ; copie vérifiée."),
    ("Télécharger et contrôler l'ISO", "Site officiel ; sha256sum -c sur le fichier SHA256SUMS : OK."),
    ("Créer la clé USB", "Clé de 8 Go au moins, cible vérifiée avec lsblk ; Etcher, Rufus ou dd."),
)

SETUP_STEPS: tuple[tuple[str, str], ...] = (
    ("Régler le firmware", "UEFI, démarrage sécurisé laissé actif, mode du stockage noté."),
    ("Démarrer sur la clé", "Menu de démarrage (F12, F11, F8, Échap) : entrée « UEFI: »."),
    ("Langue, clavier, réseau", "Français, clavier belge, Wi-Fi ou câble pour les mises à jour."),
    ("Tester en session live", "Wi-Fi, écran, son, pavé tactile ; disques vus par lsblk."),
    ("Type d'installation", "Effacer, à côté de Windows ou manuel ; logiciels tiers si besoin."),
    ("Partitions", "ESP sur /boot/efi, / en ext4, /home facultative, swap selon besoin."),
    ("Compte et fuseau horaire", "Nom de la machine, utilisateur administrateur (sudo), Europe/Brussels."),
    ("Copie et redémarrage", "Retirer la clé quand l'installateur le demande."),
)

FINAL_STEPS: tuple[tuple[str, str], ...] = (
    ("Mettre à jour", "sudo apt update puis sudo apt upgrade (dnf upgrade sous Fedora)."),
    ("Pilotes", "« Pilotes additionnels » ; clé MOK enrôlée si le démarrage sécurisé est actif."),
    ("Réseau et services", "ip a, ping ; systemctl --failed : aucun service en échec."),
    ("Comptes", "Administrateur dans sudo ; compte standard pour l'usage quotidien."),
    ("Démarrage", "Chaque système prévu démarre ; ordre des entrées contrôlé (efibootmgr)."),
    ("Contrôler et documenter", "Liste de contrôle avec le client ; rapport d'intervention signé."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Préparer l'installation", PREP_STEPS),
    ("Installer Linux, de la clé au bureau", SETUP_STEPS),
    ("Finaliser et valider", FINAL_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


PREP_FIGURE = Figure(
    key="pr09-preparer",
    title="Procédure 1 — Préparer l'installation de Linux",
    alt=_procedure_alt("Préparation d'une installation de Linux.", PREP_STEPS),
    caption=(
        "Rien n'est effacé avant l'accord écrit et la sauvegarde vérifiée. Une image dont la somme "
        "de contrôle n'est pas « OK » n'est jamais écrite sur la clé."
    ),
    svg=step_flow_svg(PREP_STEPS),
)

SETUP_FIGURE = Figure(
    key="pr09-installer",
    title="Procédure 2 — Installer Linux, de la clé au bureau",
    alt=_procedure_alt("Déroulement de l'installation de Linux.", SETUP_STEPS),
    caption=(
        "Libellés d'Ubuntu et de Linux Mint ; d'autres installateurs posent les mêmes questions "
        "dans un autre ordre. La session live sert à tester le matériel avant de toucher au disque."
    ),
    svg=step_flow_svg(SETUP_STEPS),
)

FINAL_FIGURE = Figure(
    key="pr09-finaliser",
    title="Procédure 3 — Finaliser et valider l'installation",
    alt=_procedure_alt("Finalisation d'une installation de Linux.", FINAL_STEPS),
    caption=(
        "Un PC n'est rendu qu'à jour, avec ses pilotes, son réseau, des comptes adaptés et un "
        "démarrage contrôlé, devant le client."
    ),
    svg=step_flow_svg(FINAL_STEPS),
)

# =============================================================================================
# 8. Liste de contrôle et rapport d'intervention
# =============================================================================================

# (point contrôlé, commande ou outil, résultat attendu)
CHECKLIST: tuple[tuple[str, str, str], ...] = (
    ("Système", "cat /etc/os-release", "Distribution et version prévues"),
    ("Démarrage", "efibootmgr ; redémarrages", "Entrée de Linux en premier ; Windows proposé si double démarrage"),
    ("Démarrage sécurisé", "mokutil --sb-state", "« SecureBoot enabled »"),
    ("Partitions", "lsblk -f ; findmnt --verify", "ESP, / et /home montées ; aucune erreur"),
    ("Espace", "df -h", "Espace libre suffisant sur / et /home"),
    ("Mises à jour", "sudo apt update && sudo apt upgrade", "« 0 upgraded » : rien en attente"),
    ("Pilotes", "lspci -k ; « Pilotes additionnels »", "« Kernel driver in use » pour réseau et graphique"),
    ("Réseau", "ip a ; ping -c 3 debian.org", "Adresse obtenue, nom résolu, réponses reçues"),
    ("Services", "systemctl --failed", "« 0 loaded units listed »"),
    ("Comptes et données", "groups ; avec le client", "sudo pour l'administrateur seulement ; fichiers vérifiés"),
)

REPORT_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Demande", "Client, date, besoin exprimé, accord écrit (date, ce qui peut être effacé)."),
    ("Poste", "Marque, modèle, numéro de série ; état initial constaté."),
    ("Sauvegarde", "Support utilisé, contenu, vérification de la copie."),
    ("Actions", "Distribution et version, image contrôlée, partitions, chargeur, comptes, pilotes."),
    ("Contrôles", "Liste de contrôle et résultats (démarrage, mises à jour, réseau, services)."),
    ("Remise", "Données vérifiées avec le client ; explication des comptes et des mises à jour."),
    ("Recommandations", "Sauvegarde régulière, mises à jour, matériel à surveiller ; signatures."),
)

# =============================================================================================
# 9. Captures fictives (écrans SVG, lignes courtes)
# =============================================================================================

DUAL_BOOT_SCREEN: tuple[str, ...] = (
    "$ lsblk -o NAME,SIZE,FSTYPE,LABEL",
    "NAME          SIZE FSTYPE  LABEL",
    "sda          14.6G iso9660 Ubuntu 24.04.3 LTS amd64",
    "nvme0n1     476.9G",
    "├─nvme0n1p1   100M vfat",
    "├─nvme0n1p2    16M",
    "├─nvme0n1p3 375.4G ntfs    Windows",
    "└─nvme0n1p4   752M ntfs    WinRE",
    "",
    "Espace non alloué (réduit depuis Windows) : 100 Go",
)

DF_FULL_SCREEN: tuple[str, ...] = (
    "$ sudo apt upgrade",
    "E: You don't have enough free space in",
    "   /var/cache/apt/archives/.",
    "$ df -h /",
    "Filesystem      Size  Used Avail Use% Mounted on",
    "/dev/nvme0n1p2   20G   19G     0 100% /",
    "$ sudo du -sh /var/log /var/cache/apt /home",
    "4.2G    /var/log",
    "1.6G    /var/cache/apt",
    "9.8G    /home",
)

ISO_CHECK_FIGURE = Figure(
    key="pr09-controle-iso",
    title="Contrôle de l'image ISO et choix de la clé cible (fictif)",
    alt="Capture texte d'un terminal. " + " ; ".join(line.strip() for line in ISO_CHECK_SCREEN) + ".",
    caption=(
        "sha256sum -c compare l'image à la somme publiée : « OK ». lsblk -d identifie la clé par "
        "sa taille et son transport (usb) : ici sdb, jamais sda ni nvme0n1. Capture fictive."
    ),
    svg=screen_svg(ISO_CHECK_SCREEN, label=FICTIVE_LABEL),
)

DUAL_BOOT_FIGURE = Figure(
    key="pr09-double-demarrage",
    title="Session live avant un double démarrage : disques et partitions (fictif)",
    alt="Capture texte d'un terminal. " + " ; ".join(line.strip() for line in DUAL_BOOT_SCREEN if line.strip()) + ".",
    caption=(
        "nvme0n1p1 (100 Mo, vfat) est l'ESP de Windows, à réutiliser sans formatage ; l'espace "
        "libéré depuis Windows n'est pas une partition et n'apparaît pas dans lsblk. Capture fictive."
    ),
    svg=screen_svg(DUAL_BOOT_SCREEN, label=FICTIVE_LABEL),
)

EFIBOOT_FIGURE = Figure(
    key="pr09-efibootmgr",
    title="Cas 3 — Le PC démarre sous Windows : ordre des entrées UEFI (fictif)",
    alt="Capture texte d'un terminal. " + " ; ".join(line.strip() for line in EFIBOOT_SCREEN) + ".",
    caption=(
        "« Windows Boot Manager » (0000) était en premier : le menu GRUB n'apparaissait jamais. "
        "Après efibootmgr -o, l'entrée « ubuntu » (0001) passe en tête. Capture fictive."
    ),
    svg=screen_svg(EFIBOOT_SCREEN, label=FICTIVE_LABEL),
)

DF_FULL_FIGURE = Figure(
    key="pr09-disque-plein",
    title="Racine pleine : mise à jour impossible (fictif)",
    alt="Capture texte d'un terminal. " + " ; ".join(line.strip() for line in DF_FULL_SCREEN) + ".",
    caption=(
        "Racine de 20 Go pleine (« Avail 0 » : ext4 réserve aussi environ 5 % à root). du -sh "
        "montre où va la place avant de nettoyer. Capture fictive."
    ),
    svg=screen_svg(DF_FULL_SCREEN, label=FICTIVE_LABEL),
)

PR09_FIGURES: tuple[Figure, ...] = (
    PREP_FIGURE,
    SETUP_FIGURE,
    LAYOUT_FIGURE,
    FINAL_FIGURE,
    BOOT_TREE_FIGURE,
    ISO_CHECK_FIGURE,
    DUAL_BOOT_FIGURE,
    EFIBOOT_FIGURE,
    DF_FULL_FIGURE,
)

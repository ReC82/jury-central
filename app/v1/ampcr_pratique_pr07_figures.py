"""PR07 « Systèmes d'exploitation, GUI/CLI et prérequis d'installation » — données de
référence, règles de décision et schémas SVG (ticket #207).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket207_ampcr_pratique_pr07.py` :

- les fonctions d'un système d'exploitation (`OS_FUNCTIONS`) et leur place en couches
  (`LAYERS_FIGURE`) : noyau, pilotes, système de fichiers, comptes, services, interface ;
- les systèmes du marché (`OS_FAMILIES`) et les éditions de Windows (`EDITION_FEATURES`,
  `edition_needed`) ;
- les outils graphiques et en ligne de commande (`TOOLS`) ;
- l'architecture 32/64 bits (`max_addressable_gib`) ;
- les prérequis de Windows 11 (`WIN11_REQUIREMENTS`, `win11_check`) : blocages matériels,
  réglages du firmware à faire (mode UEFI, TPM activé) et recommandations ;
- les licences (`LICENCE_ROWS`) ;
- le choix installation propre / mise à niveau (`install_type`, `INSTALL_TREE`) ;
- la virtualisation (`vm_plan`) ;
- trois procédures illustrées (`CHECK_STEPS`, `MEDIA_STEPS`, `INSTALL_PLAN_STEPS`) : les
  mêmes tuples dessinent les schémas et alimentent les remises en ordre des exercices.

Les prérequis cités sont ceux publiés par les éditeurs **au moment de la rédaction
(octobre 2026)** ; ils changent avec les versions : la page officielle de l'éditeur fait foi.
Les captures (Informations système, menu de démarrage, terminal) sont **fictives** ; aucun
schéma ne vient d'une image générée ni d'une photographie.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR05)
WRITTEN_AT = "octobre 2026"

# =============================================================================================
# 1. Fonctions d'un système d'exploitation
# =============================================================================================


@dataclass(frozen=True)
class OsFunction:
    key: str
    name: str
    role: str
    windows: str
    linux: str


FN_KERNEL = "Noyau"
FN_DRIVER = "Pilote"
FN_FS = "Système de fichiers"
FN_ACCOUNTS = "Comptes et droits"
FN_SERVICE = "Service"
FN_INTERFACE = "Interface (GUI ou CLI)"

OS_FUNCTIONS: tuple[OsFunction, ...] = (
    OsFunction(
        "noyau", FN_KERNEL,
        "Cœur du système : partage le temps du processeur entre les programmes, attribue et "
        "protège la mémoire vive de chacun, donne accès au matériel par les pilotes.",
        "noyau Windows NT",
        "noyau Linux (version affichée par uname -r)",
    ),
    OsFunction(
        "pilote", FN_DRIVER,
        "Programme qui traduit les ordres du système pour un matériel précis (carte réseau, "
        "carte graphique, contrôleur de stockage, imprimante).",
        "Gestionnaire de périphériques ; pilotes de Windows Update ou du fabricant",
        "modules du noyau (lsmod), paquets de firmware, quelques pilotes propriétaires (NVIDIA)",
    ),
    OsFunction(
        "fs", FN_FS,
        "Range les fichiers et les dossiers sur le support et enregistre qui peut les lire ou "
        "les modifier.",
        "NTFS (FAT32 pour la partition EFI, exFAT pour l'échange)",
        "ext4 (Btrfs ou XFS selon la distribution)",
    ),
    OsFunction(
        "comptes", FN_ACCOUNTS,
        "Identifie chaque utilisateur, sépare ses fichiers et limite ce qu'il peut modifier "
        "dans le système.",
        "compte administrateur ou standard, Contrôle de compte d'utilisateur (UAC)",
        "utilisateurs et groupes, compte root, commande sudo",
    ),
    OsFunction(
        "services", FN_SERVICE,
        "Programme d'arrière-plan lancé avec le système, sans fenêtre (impression, mises à "
        "jour, réseau, heure).",
        "services.msc, Get-Service",
        "services gérés par systemd : systemctl status",
    ),
    OsFunction(
        "interface", FN_INTERFACE,
        "Ce que l'utilisateur manipule : interface graphique (fenêtres, souris, GUI) ou "
        "interface en ligne de commande (texte, commandes, CLI).",
        "Explorateur, Paramètres ; Invite de commandes, PowerShell, Terminal Windows",
        "environnement de bureau (GNOME, KDE Plasma, Xfce) ; terminal et shell bash",
    ),
)
OS_FUNCTIONS_BY_NAME = {f.name: f for f in OS_FUNCTIONS}

# Pile simplifiée (du haut vers le bas) : mêmes couches pour les deux familles.
LAYER_NAMES: tuple[str, ...] = ("Applications", "Interface", "Services", "Noyau et pilotes", "Firmware", "Matériel")
WINDOWS_STACK: tuple[str, ...] = (
    "Applications : Office, navigateur",
    "Interface : Explorateur ; PowerShell",
    "Services Windows (services.msc)",
    "Noyau NT + pilotes (.sys)",
    "Firmware UEFI",
    "Matériel : processeur, RAM, disques",
)
LINUX_STACK: tuple[str, ...] = (
    "Applications : LibreOffice, navigateur",
    "Interface : GNOME ou Xfce ; bash",
    "Services systemd (systemctl)",
    "Noyau Linux + modules",
    "Firmware UEFI",
    "Matériel : processeur, RAM, disques",
)


def stacks_svg(stacks: tuple[tuple[str, tuple[str, ...]], ...], *, width: int = 380) -> str:
    """Piles de couches côte à côte (une colonne par pile, la première couche en haut).
    Ce n'est pas un schéma à l'échelle : chaque couche est une case étiquetée."""
    gap = 8
    col_w = (width - gap * (len(stacks) + 1)) // len(stacks)
    wrap_at = max(12, col_w // 7)
    depth = max(len(layers) for _t, layers in stacks)
    # Hauteur de chaque rang = la plus haute case de ce rang, pour aligner les colonnes.
    heights = [max((len(_wrap(layers[i], wrap_at)) for _t, layers in stacks if i < len(layers)), default=1)
               for i in range(depth)]
    parts: list[str] = []
    bottom = 0
    for column, (title, layers) in enumerate(stacks):
        x = gap + column * (col_w + gap)
        parts.append(_text_lines(x + col_w // 2, 18, [title], size=13, weight="700", anchor="middle"))
        y = 30
        for i, layer in enumerate(layers):
            box_h = 14 + 15 * heights[i]
            fill = "#e9f5ec" if i == len(layers) - 1 else "#f4f6fb"
            parts.append(
                f'<rect data-layer="{escape(layer)}" x="{x}" y="{y}" width="{col_w}" height="{box_h}" '
                f'rx="6" fill="{fill}" stroke="#33415c" stroke-width="1.5"/>'
            )
            parts.append(_text_lines(x + col_w // 2, y + 18, _wrap(layer, wrap_at), size=11.5,
                                     weight="700" if i == 0 else "400", step=15, anchor="middle"))
            y += box_h + 4
        bottom = max(bottom, y)
    return _svg(width, bottom + 6, parts)


def _stack_alt(intro: str, stacks: tuple[tuple[str, tuple[str, ...]], ...]) -> str:
    return intro + " " + " ".join(
        f"{title}, de haut en bas : " + " ; ".join(layers) + "." for title, layers in stacks
    )


_OS_STACKS = (("Windows", WINDOWS_STACK), ("Linux (Ubuntu)", LINUX_STACK))

LAYERS_FIGURE = Figure(
    key="pr07-couches",
    title="Les couches d'un système d'exploitation — Windows et Linux",
    alt=_stack_alt("Deux piles de six couches côte à côte.", _OS_STACKS),
    caption=(
        "Vue simplifiée : l'application demande, le noyau décide et passe par le pilote, le "
        "pilote commande le matériel. Le firmware UEFI démarre le PC avant le système."
    ),
    svg=stacks_svg(_OS_STACKS),
)

# =============================================================================================
# 2. Systèmes sur le marché et éditions de Windows
# =============================================================================================


@dataclass(frozen=True)
class OsFamily:
    name: str
    publisher_licence: str
    hardware: str
    typical_use: str
    lifecycle: str


OS_FAMILIES: tuple[OsFamily, ...] = (
    OsFamily(
        "Windows (Microsoft)",
        "Propriétaire, payant ; souvent préinstallé avec le PC (licence OEM).",
        "PC de toutes marques, processeurs x64 et ARM64.",
        "Bureautique, jeux, logiciels métiers Windows, réseaux d'entreprise (domaine).",
        "Mises à jour mensuelles ; chaque version a une date de fin de support publiée "
        "(Windows 10 : 14 octobre 2025, sauf programme payant de mises à jour étendues).",
    ),
    OsFamily(
        "Distributions Linux (Ubuntu, Debian, Linux Mint, Fedora…)",
        "Logiciels libres, gratuits (licence GPL et autres) ; support payant facultatif.",
        "Presque tous les PC, y compris anciens ; serveurs.",
        "Serveurs, postes bureautiques, PC reconditionnés, développement.",
        "Versions à support long (LTS, plusieurs années) ou versions courtes ; date de fin "
        "publiée par chaque distribution.",
    ),
    OsFamily(
        "macOS (Apple)",
        "Propriétaire, fourni avec le Mac.",
        "Uniquement les ordinateurs Apple (licence).",
        "Graphisme, vidéo, utilisateurs de l'écosystème Apple.",
        "Mise à jour gratuite tant que le modèle de Mac est pris en charge.",
    ),
    OsFamily(
        "ChromeOS et ChromeOS Flex (Google)",
        "Propriétaire ; Flex gratuit pour installer sur un PC existant.",
        "Chromebooks ; Flex : PC de la liste des modèles certifiés.",
        "Navigation et applications web, écoles, prolonger un PC ancien.",
        "Mises à jour automatiques jusqu'à une date fixée par modèle.",
    ),
)

WINDOWS_CURRENT = "Windows 11"
EDITION_HOME = "Windows 11 Famille"
EDITION_PRO = "Windows 11 Professionnel"

# (besoin, disponible en Famille)
EDITION_FEATURES: tuple[tuple[str, bool], ...] = (
    ("Navigateur, bureautique, courrier, jeux", True),
    ("Microsoft Defender, pare-feu et Windows Update", True),
    ("Se connecter à un autre PC avec le client Bureau à distance", True),
    ("Joindre le PC au domaine Active Directory de l'entreprise", False),
    ("Chiffrer un disque avec BitLocker et sa console de gestion", False),
    ("Être pris en main à distance comme hôte Bureau à distance", False),
    ("Créer des machines virtuelles avec Hyper-V", False),
    ("Régler le poste avec l'Éditeur de stratégie de groupe locale (gpedit.msc)", False),
)
EDITION_FEATURES_BY_NEED = dict(EDITION_FEATURES)


def edition_needed(needs: tuple[str, ...]) -> str:
    """Édition de Windows 11 la moins chère qui couvre tous les besoins listés."""
    unknown = [n for n in needs if n not in EDITION_FEATURES_BY_NEED]
    if unknown:
        raise ValueError(f"Besoin inconnu : {unknown}")
    return EDITION_HOME if all(EDITION_FEATURES_BY_NEED[n] for n in needs) else EDITION_PRO


# =============================================================================================
# 3. Interface graphique (GUI) et ligne de commande (CLI)
# =============================================================================================


@dataclass(frozen=True)
class ToolRow:
    task: str
    windows_gui: str
    windows_cli: str
    linux_gui: str
    linux_cli: str


TOOLS: tuple[ToolRow, ...] = (
    ToolRow("Version du système", "Paramètres > Système > Informations système ; winver",
            "systeminfo ; PowerShell : Get-ComputerInfo",
            "Paramètres > À propos", "cat /etc/os-release ; uname -r"),
    ToolRow("Processeur et mémoire", "Gestionnaire des tâches > Performance ; msinfo32",
            "systeminfo", "Paramètres > À propos", "lscpu ; nproc ; free -h"),
    ToolRow("Disques et partitions", "Gestion des disques (diskmgmt.msc)",
            "diskpart (list disk) ; PowerShell : Get-Disk", "Disques (GNOME), GParted", "lsblk -f ; df -h"),
    ToolRow("Pilotes et périphériques", "Gestionnaire de périphériques (devmgmt.msc)",
            "pnputil /enum-drivers ; PowerShell : Get-PnpDevice",
            "Logiciels et mises à jour > Pilotes additionnels (Ubuntu)", "lspci -k ; lsusb ; lsmod"),
    ToolRow("Services", "Services (services.msc)", "PowerShell : Get-Service ; sc query",
            "selon l'environnement (souvent aucun outil standard)", "systemctl status <service>"),
    ToolRow("Réseau", "Paramètres > Réseau et Internet", "ipconfig /all",
            "Paramètres > Réseau", "ip a ; ip route"),
    ToolRow("Firmware et sécurité", "msinfo32 (Mode BIOS, démarrage sécurisé) ; tpm.msc",
            "PowerShell administrateur : Confirm-SecureBootUEFI ; Get-Tpm",
            "aucun outil standard", "ls /sys/firmware/efi ; mokutil --sb-state"),
    ToolRow("Mises à jour", "Paramètres > Windows Update", "surtout par l'interface graphique",
            "Gestionnaire de mises à jour", "sudo apt update puis sudo apt upgrade (Debian, Ubuntu, Mint)"),
)
TOOLS_BY_TASK = {t.task: t for t in TOOLS}

# =============================================================================================
# 4. Architecture 32/64 bits
# =============================================================================================

ADDRESS_32BIT_GIB = 4  # 2^32 octets adressables = 4 Gio


def max_addressable_gib(os_bits: int) -> int | None:
    """Mémoire adressable par un système 32 bits (4 Gio, dont une partie réservée aux
    périphériques) ; None pour 64 bits : la limite dépasse ce que le PC accepte."""
    if os_bits == 32:
        return ADDRESS_32BIT_GIB
    if os_bits == 64:
        return None
    raise ValueError("32 ou 64 bits")


def usable_ram_gib(installed_gib: float, os_bits: int) -> float:
    """Borne haute de la mémoire utilisable : jamais plus que l'installé ni, en 32 bits, que
    4 Gio (en pratique environ 3,2 à 3,5 Gio, le reste servant aux périphériques)."""
    limit = max_addressable_gib(os_bits)
    return installed_gib if limit is None else min(installed_gib, limit)


# =============================================================================================
# 5. Prérequis de Windows 11 (publiés par Microsoft, relevés en octobre 2026)
# =============================================================================================


@dataclass(frozen=True)
class Requirement:
    key: str
    item: str
    minimum: str
    how_to_check: str


WIN11_REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement("cpu", "Processeur", "64 bits, 1 GHz, 2 cœurs au moins, modèle présent dans la liste "
                "des processeurs compatibles de Microsoft", "msinfo32 (Processeur) ; application Contrôle d'intégrité du PC"),
    Requirement("ram", "Mémoire vive", "4 Go", "msinfo32 ; Gestionnaire des tâches > Performance"),
    Requirement("storage", "Stockage", "64 Go", "Gestion des disques"),
    Requirement("firmware", "Firmware", "UEFI, compatible démarrage sécurisé (Secure Boot)",
                "msinfo32 : « Mode BIOS » et « État du démarrage sécurisé »"),
    Requirement("tpm", "Puce de sécurité TPM", "version 2.0 (puce ou TPM intégré au processeur : "
                "Intel PTT, AMD fTPM)", "tpm.msc : « Version de la spécification »"),
    Requirement("gpu", "Carte graphique", "compatible DirectX 12, pilote WDDM 2.0", "dxdiag"),
    Requirement("display", "Écran", "plus de 9 pouces, définition 720p", "fiche du PC"),
    Requirement("online", "Mise en route", "connexion Internet et compte Microsoft pour l'édition Famille",
                "prévoir le réseau et les identifiants du client"),
)

W11_OK = "Compatible tel quel"
W11_SETTINGS = "Compatible après réglages du firmware"
W11_NO = "Non compatible (matériel)"
W11_VERDICTS = (W11_OK, W11_SETTINGS, W11_NO)


@dataclass(frozen=True)
class PcSpec:
    cpu: str
    cpu_64bit: bool
    cpu_listed: bool
    cores: int
    ghz: float
    ram_gb: int
    storage_gb: int
    uefi_capable: bool  # le firmware sait démarrer en UEFI
    firmware_mode: str  # « UEFI » ou « Hérité » (CSM) actuellement
    secure_boot_on: bool
    tpm_version: float  # 0 = absent, 1.2, 2.0
    tpm_enabled: bool
    disk_table: str  # « GPT » ou « MBR » (disque système actuel)
    dx12: bool = True


def win11_check(pc: PcSpec) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """(verdict, blocages matériels, réglages à faire) pour installer ou mettre à niveau
    vers Windows 11. Le démarrage sécurisé doit être **pris en charge** (firmware UEFI) ; s'il
    est seulement désactivé, on recommande de l'activer (sécurité), ce n'est pas un blocage."""
    blockers: list[str] = []
    if not pc.cpu_64bit:
        blockers.append("processeur 32 bits")
    elif not pc.cpu_listed:
        blockers.append("processeur absent de la liste de compatibilité")
    if pc.cores < 2 or pc.ghz < 1:
        blockers.append("processeur trop faible (moins de 2 cœurs ou de 1 GHz)")
    if pc.ram_gb < 4:
        blockers.append("moins de 4 Go de mémoire vive")
    if pc.storage_gb < 64:
        blockers.append("moins de 64 Go de stockage")
    if not pc.uefi_capable:
        blockers.append("firmware sans UEFI ni démarrage sécurisé")
    if pc.tpm_version < 2:
        blockers.append("pas de TPM 2.0")
    if not pc.dx12:
        blockers.append("carte graphique non compatible DirectX 12")
    if blockers:
        return W11_NO, tuple(blockers), ()
    settings: list[str] = []
    if pc.firmware_mode != "UEFI":
        if pc.disk_table == "MBR":
            settings.append("convertir le disque système en GPT (mbr2gpt, après sauvegarde)")
        settings.append("passer le firmware en mode UEFI (CSM désactivé)")
    if not pc.tpm_enabled:
        settings.append("activer le TPM dans le firmware (Intel PTT ou AMD fTPM)")
    if not pc.secure_boot_on:
        settings.append("activer le démarrage sécurisé (recommandé)")
    hard_settings = [s for s in settings if "recommandé" not in s]
    return (W11_SETTINGS if hard_settings else W11_OK), (), tuple(settings)


# Configuration recommandée publiée par Ubuntu pour sa version Desktop (octobre 2026).
UBUNTU_DESKTOP_RECOMMENDED: tuple[str, ...] = (
    "processeur 64 bits double cœur de 2 GHz",
    "4 Go de mémoire vive",
    "25 Go d'espace disque",
)

# =============================================================================================
# 6. Licences
# =============================================================================================

LICENCE_ROWS: tuple[tuple[str, str, str], ...] = (
    ("OEM (préinstallée par le fabricant)",
     "Liée au premier PC qui l'a reçue : non transférable à un autre PC.",
     ("Réinstallation de la même édition sur le même PC : activation automatique (licence "
      "numérique, clé inscrite dans le firmware).")),
    ("Commerciale (boîte ou achat en ligne)",
     "Transférable sur un autre PC si on la retire du premier.",
     "Clé à conserver, ou licence numérique liée au compte Microsoft."),
    ("En volume (entreprise, école)",
     "Contrat de l'organisation, géré par son service informatique.",
     "Activation par le serveur de l'organisation : ne jamais saisir une clé « trouvée »."),
    ("Logiciel libre (Linux)",
     "Gratuit, installable sur autant de PC qu'on veut.",
     ("Aucune clé ; certaines distributions d'entreprise (Red Hat Enterprise Linux) sont "
      "vendues par abonnement de support.")),
)

# =============================================================================================
# 7. Installation propre ou mise à niveau
# =============================================================================================

INSTALL_UPGRADE = "Mise à niveau sur place"
INSTALL_CLEAN = "Installation propre"
INSTALL_NONE = "Ni l'une ni l'autre : changer de système ou de matériel"
INSTALL_BACKUP_FIRST = "Sauvegarder d'abord"
INSTALL_CHOICES = (INSTALL_UPGRADE, INSTALL_CLEAN, INSTALL_NONE)


def install_type(*, backup_ok: bool, requirements_ok: bool, same_family_and_arch: bool,
                 system_healthy: bool, keep_programs: bool) -> str:
    """Démarche du cours, dans l'ordre de l'arbre `INSTALL_TREE`."""
    if not backup_ok:
        return INSTALL_BACKUP_FIRST
    if not requirements_ok:
        return INSTALL_NONE
    if not same_family_and_arch or not system_healthy or not keep_programs:
        return INSTALL_CLEAN
    return INSTALL_UPGRADE


INSTALL_TREE: tuple[tuple[str, str], ...] = (
    ("Les données sont-elles sauvegardées, copie vérifiée ?",
     "Sauvegarder d'abord : aucune installation sans copie vérifiée et accord écrit."),
    ("Le PC respecte-t-il les prérequis du système visé ?",
     "Ni l'une ni l'autre : autre système (Linux, ChromeOS Flex) ou matériel à changer."),
    ("Même famille et même architecture (Windows 64 bits → Windows 64 bits) ?",
     "Installation propre : pas de mise à niveau de 32 à 64 bits ni de Windows vers Linux."),
    ("Le système actuel est-il sain (sans infection ni erreurs répétées) ?",
     "Installation propre : une mise à niveau garderait les problèmes."),
    ("Le client veut-il garder ses programmes et ses réglages ?",
     "Installation propre : système neuf, programmes réinstallés."),
)
INSTALL_TREE_FINAL = (
    "Mise à niveau sur place possible, lancée depuis le système en marche ; l'installation "
    "propre reste possible si l'on préfère repartir de zéro."
)

INSTALL_TREE_FIGURE = Figure(
    key="pr07-propre-ou-mise-a-niveau",
    title="Arbre de décision — installation propre ou mise à niveau ?",
    alt=(
        "Arbre de décision en cinq questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(INSTALL_TREE, start=1))
        + f" Si toutes les réponses sont oui : {INSTALL_TREE_FINAL}"
    ),
    caption=(
        "La sauvegarde vient avant tout le reste : même une mise à niveau peut échouer. Une "
        "installation propre efface la partition du système."
    ),
    svg=decision_tree_svg(INSTALL_TREE, INSTALL_TREE_FINAL),
)

# =============================================================================================
# 8. Virtualisation
# =============================================================================================

HOST_RESERVE_GIB = 4  # mémoire laissée au système hôte (convention du cours)


def vm_plan(host_ram_gib: float, guests_ram_gib: tuple[float, ...],
            reserve_gib: float = HOST_RESERVE_GIB) -> tuple[float, bool]:
    """(mémoire restant à l'hôte quand toutes les machines virtuelles tournent, plan
    acceptable selon la réserve du cours)."""
    left = host_ram_gib - sum(guests_ram_gib)
    return left, left >= reserve_gib


TYPE2_STACK: tuple[str, ...] = (
    "Machines virtuelles (systèmes invités)",
    "Logiciel : VirtualBox, VMware Workstation",
    "Système hôte : Windows ou Linux",
    "Matériel (VT-x ou AMD-V activé)",
)
TYPE1_STACK: tuple[str, ...] = (
    "Machines virtuelles (systèmes invités)",
    "Hyperviseur : Hyper-V, Proxmox VE (KVM), VMware ESXi",
    "Matériel (VT-x ou AMD-V activé)",
)
_VM_STACKS = (("Type 2 (hébergé)", TYPE2_STACK), ("Type 1 (natif)", TYPE1_STACK))

VM_FIGURE = Figure(
    key="pr07-virtualisation",
    title="Virtualisation : hyperviseur hébergé (type 2) et natif (type 1)",
    alt=_stack_alt("Deux piles côte à côte.", _VM_STACKS),
    caption=(
        "Le type 2 s'installe comme un programme sur un système existant (poste de test) ; le "
        "type 1 s'installe directement sur le matériel (serveur). Les deux exigent les "
        "extensions de virtualisation du processeur, activées dans le firmware."
    ),
    svg=stacks_svg(_VM_STACKS),
)

# =============================================================================================
# 9. Procédures illustrées
# =============================================================================================

# Procédure 1 — vérifier les prérequis avant de choisir.
CHECK_STEPS: tuple[tuple[str, str], ...] = (
    ("Relever le besoin", "Usages, logiciels indispensables, périphériques, contraintes de l'entreprise (domaine)."),
    ("Relever le matériel", "Processeur 64 bits, cœurs, mémoire, stockage : msinfo32, ou lscpu et free -h."),
    ("Relever le firmware", "Mode UEFI ou hérité, démarrage sécurisé, TPM 2.0 : msinfo32, tpm.msc."),
    ("Comparer aux prérequis", "Page officielle de l'éditeur pour la version et l'édition visées."),
    ("Vérifier les pilotes", "Réseau, stockage, graphique : disponibles chez le fabricant pour ce système ?"),
    ("Conclure par écrit", "Compatible, compatible après réglages ou non compatible ; alternative proposée."),
)

# Procédure 2 — préparer le média d'installation.
MEDIA_STEPS: tuple[tuple[str, str], ...] = (
    ("Télécharger l'image", "Image ISO ou outil de création, sur le site officiel de l'éditeur."),
    ("Contrôler l'image", "Somme SHA-256 du fichier comparée à celle publiée par l'éditeur."),
    ("Préparer la clé", "Clé USB de 8 Go au moins, vide ou sauvegardée : elle sera effacée."),
    ("Écrire la clé", "Outil de création officiel, Rufus, balenaEtcher ou dd ; schéma GPT pour un PC UEFI."),
    ("Tester le démarrage", "Menu de démarrage du PC : l'entrée « UEFI: » de la clé lance l'installateur."),
)

# Procédure 3 — plan d'installation complet.
INSTALL_PLAN_STEPS: tuple[tuple[str, str], ...] = (
    ("Sauvegarder", "Données, favoris, courrier ; copie vérifiée, accord écrit du client."),
    ("Relever licences et pilotes", "Édition, clé ou licence numérique ; pilotes réseau et stockage sur clé."),
    ("Préparer le média", "Image officielle contrôlée, clé USB démarrable."),
    ("Régler le firmware", "Mode UEFI, démarrage sécurisé, TPM ; menu ou ordre de démarrage."),
    ("Installer", "Disque cible identifié ; partitions GPT et ESP créées par l'installateur."),
    ("Installer les pilotes", "Chipset, réseau, graphique ; aucun périphérique inconnu."),
    ("Sécuriser", "Compte administrateur et compte standard, mises à jour, antivirus, pare-feu, chiffrement."),
    ("Contrôler et documenter", "Activation, réseau, données restaurées ; rapport d'intervention."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Vérifier les prérequis avant de choisir", CHECK_STEPS),
    ("Préparer le média d'installation", MEDIA_STEPS),
    ("Plan d'installation complet", INSTALL_PLAN_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


CHECK_FIGURE = Figure(
    key="pr07-prerequis",
    title="Procédure 1 — Vérifier les prérequis avant de choisir",
    alt=_procedure_alt("Démarche de vérification des prérequis d'un système.", CHECK_STEPS),
    caption=(
        "On part du besoin du client, puis on relève le matériel et le firmware avant de "
        "comparer aux prérequis publiés : on ne choisit pas un système « au jugé »."
    ),
    svg=step_flow_svg(CHECK_STEPS),
)

MEDIA_FIGURE = Figure(
    key="pr07-media",
    title="Procédure 2 — Préparer le média d'installation",
    alt=_procedure_alt("Préparation d'une clé USB d'installation.", MEDIA_STEPS),
    caption=(
        "Une image téléchargée ailleurs que chez l'éditeur, ou dont la somme de contrôle ne "
        "correspond pas, ne s'utilise pas : elle peut être corrompue ou piégée."
    ),
    svg=step_flow_svg(MEDIA_STEPS),
)

INSTALL_PLAN_FIGURE = Figure(
    key="pr07-plan-installation",
    title="Procédure 3 — Plan d'installation complet",
    alt=_procedure_alt("Plan d'installation d'un système, de la sauvegarde au rapport.", INSTALL_PLAN_STEPS),
    caption=(
        "Le détail de l'installation de Windows et de Linux est traité en PR08 et PR09 ; ici, on "
        "apprend à préparer et à ordonner le plan."
    ),
    svg=step_flow_svg(INSTALL_PLAN_STEPS),
)

# =============================================================================================
# 10. Captures fictives
# =============================================================================================

# Cas 2 : PC de bureau sous Windows 10, démarré en mode hérité (CSM) sur un disque MBR.
CASE2_PC = PcSpec(
    cpu="Intel Core i5-8500", cpu_64bit=True, cpu_listed=True, cores=6, ghz=3.0, ram_gb=8,
    storage_gb=256, uefi_capable=True, firmware_mode="Hérité", secure_boot_on=False,
    tpm_version=2.0, tpm_enabled=True, disk_table="MBR",
)
CASE2_VERDICT, CASE2_BLOCKERS, CASE2_SETTINGS = win11_check(CASE2_PC)
MSINFO_SCREEN: tuple[str, ...] = (
    "Informations système — Résumé (capture fictive)",
    "Système d'exploitation   Windows 10 Professionnel",
    "Type du système          PC à base de x64",
    f"Processeur               {CASE2_PC.cpu}, {CASE2_PC.cores} cœurs",
    f"Mémoire physique (RAM)   {CASE2_PC.ram_gb},00 Go",
    "Mode BIOS                Hérité",
    "État du démarrage sécurisé   Non pris en charge",
    "tpm.msc : Le module TPM est prêt à être utilisé.",
    "          Version de la spécification : 2.0",
    "Gestion des disques : Disque 0 — style MBR",
)

# Cas 4 : menu de démarrage ponctuel d'un PC UEFI, clé Ubuntu branchée.
BOOT_MENU_SCREEN: tuple[str, ...] = (
    "Menu de démarrage (touche F12) — capture fictive",
    "",
    "  Windows Boot Manager (SSD NVMe 500 Go)",
    "  UEFI: Clé USB SanDisk 32 Go, Partition 1",
    "  Clé USB SanDisk 32 Go",
    "  UEFI: Réseau IPv4 (PXE)",
    "",
    "  ↑↓ choisir   Entrée démarrer   Échap quitter",
)
BOOT_UEFI_ENTRY = BOOT_MENU_SCREEN[3].strip()
BOOT_LEGACY_ENTRY = BOOT_MENU_SCREEN[4].strip()

# Exercice E09 : relevé d'un ancien PC sous Linux (session live).
LIVE_CHECK_SCREEN: tuple[str, ...] = (
    "$ uname -m",
    "x86_64",
    "$ nproc",
    "2",
    "$ free -h",
    "       total   utilisé   libre   disponible",
    "Mem:   3,8Gi   1,1Gi     1,9Gi   2,4Gi",
    "$ lsblk -d -o NAME,SIZE,ROTA",
    "NAME   SIZE   ROTA",
    "sda    465,8G    1",
    "$ ls /sys/firmware/efi",
    "ls: impossible d'accéder à '/sys/firmware/efi':",
    "Aucun fichier ou dossier de ce type",
)

MSINFO_FIGURE = Figure(
    key="pr07-msinfo",
    title="Cas 2 — Informations système, TPM et disque d'un PC sous Windows 10 (fictif)",
    alt="Capture texte. " + " ; ".join(line.strip() for line in MSINFO_SCREEN) + ".",
    caption=(
        "« Mode BIOS : Hérité » : le PC démarre en mode de compatibilité (CSM) ; le démarrage "
        "sécurisé n'existe pas dans ce mode. Le TPM 2.0 est prêt. Capture fictive."
    ),
    svg=screen_svg(MSINFO_SCREEN, label="Capture fictive — pas un écran officiel"),
)

BOOT_MENU_FIGURE = Figure(
    key="pr07-menu-demarrage",
    title="Cas 4 — Menu de démarrage ponctuel avec une clé d'installation (fictif)",
    alt="Capture texte d'un menu de démarrage. " + " ; ".join(line.strip() for line in BOOT_MENU_SCREEN if line.strip()) + ".",
    caption=(
        "La même clé apparaît deux fois : l'entrée « UEFI: » démarre en mode UEFI (installation "
        "en GPT), l'autre en mode hérité. La touche du menu varie selon le fabricant (souvent "
        "F12, F11, F8 ou Échap). Capture fictive."
    ),
    svg=screen_svg(BOOT_MENU_SCREEN, label="Capture fictive — pas un écran officiel"),
)

PR07_FIGURES: tuple[Figure, ...] = (
    LAYERS_FIGURE,
    CHECK_FIGURE,
    INSTALL_TREE_FIGURE,
    MEDIA_FIGURE,
    INSTALL_PLAN_FIGURE,
    VM_FIGURE,
    MSINFO_FIGURE,
    BOOT_MENU_FIGURE,
)

"""EX02 « Examen blanc écrit — installation et dépannage des systèmes » — données des dossiers
et schémas (ticket #231).

Une seule source pour le sujet affiché, les documents des questions et le corrigé ; chaque
verdict est calculé avec la règle **du cours** qui l'enseigne :
- **prérequis de Windows 11** des trois postes de la partie 1 (`win11_check`, PR07) et
  édition nécessaire (`edition_needed`, PR07) ;
- **service** d'impression Linux (`service_fix`, PR10) ;
- **dossier A** (Windows) : écran de choix du disque de l'installateur, activation
  (`activation_result`, PR08), partitions créées (`STANDARD_LAYOUT`, PR08), sort des autres
  partitions (`partition_action`, PR08), pilotes manquants (`vendor_name`, `device_action`,
  PR10), comptes à créer (`account_for`, PR10) ;
- **dossier B** (Linux) : plan de partitions d'un double démarrage (`dual_boot_action`,
  `swap_advice`, PR09), mode d'urgence dû à un nom de disque dans fstab (PR09), droits d'un
  dossier partagé (`can_access`, `mode_octal`, PR10) ;
- **dossier C** (Windows) : écran d'arrêt après une mise à jour de pilote, options de WinRE
  (`WINRE_OPTIONS`, PR11), échelle des interventions (`LADDER`, `precaution_for`, PR12) et
  vérification des copies par empreinte SHA-256 (`sha256_hex`, `copy_check`, PR12).

Toutes les situations, références, noms de pilotes, UUID et valeurs sont **fictifs**. Les trois
schémas utilisés dans les questions sont aussi enregistrés en fichiers statiques
(`app/static/img/ampcr-pratique/`) ; un test vérifie qu'ils sont identiques au SVG produit ici.
Libellés de Windows 11 et des distributions Linux relevés en octobre 2026 : ils changent selon
les versions ; la documentation de l'éditeur fait foi.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr07_figures import (
    EDITION_FEATURES,
    PcSpec,
    edition_needed,
    win11_check,
)
from app.v1.ampcr_pratique_pr08_figures import (
    LIC_DIGITAL,
    STANDARD_LAYOUT,
    activation_result,
    partition_action,
)
from app.v1.ampcr_pratique_pr09_figures import (
    PK_ESP,
    PK_FREE,
    PK_MSR,
    PK_RECOVERY,
    PK_WINDOWS,
    dual_boot_action,
    swap_advice,
)
from app.v1.ampcr_pratique_pr10_figures import (
    NEED_ADMIN,
    NEED_DAILY,
    NEED_SHARED,
    account_for,
    can_access,
    device_action,
    mode_octal,
    service_fix,
    vendor_name,
)
from app.v1.ampcr_pratique_pr11_figures import WINRE_OPTIONS
from app.v1.ampcr_pratique_pr12_figures import (
    LADDER_BY_NAME,
    BackupFile,
    copy_check,
    effect_of,
    precaution_for,
    sha256_hex,
)
from app.v1.ampcr_pratique_visuals import Figure, PartitionSegment, partition_map_svg, screen_svg

STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme les cours)

# =============================================================================================
# Partie 1 — trois postes à équiper (question X01)
# =============================================================================================


@dataclass(frozen=True)
class Station:
    name: str
    usage: str
    needs: tuple[str, ...]  # besoins de `EDITION_FEATURES` (PR07) si Windows est retenu
    spec: PcSpec
    cpu_label: str  # ce que montre le relevé (fictif)


_NEED_OFFICE = EDITION_FEATURES[0][0]  # navigateur, bureautique, courrier, jeux
_NEED_BITLOCKER = EDITION_FEATURES[4][0]
_NEED_RDP_HOST = EDITION_FEATURES[5][0]

STATIONS: tuple[Station, ...] = (
    Station(
        "Poste 1 — accueil",
        "Agenda en ligne, courrier, traitement de texte ; Windows 10 installé, à passer sous Windows 11.",
        (_NEED_OFFICE,),
        PcSpec(cpu="i5 fictif", cpu_64bit=True, cpu_listed=True, cores=6, ghz=3.0, ram_gb=8, storage_gb=256,
               uefi_capable=True, firmware_mode="Hérité", secure_boot_on=False, tpm_version=2.0,
               tpm_enabled=False, disk_table="MBR"),
        "64 bits, 6 cœurs, 3,0 GHz, présent dans la liste de compatibilité",
    ),
    Station(
        "Poste 2 — atelier",
        "Navigateur, lecture de PDF et courrier dans le navigateur ; aucun logiciel propre à Windows.",
        (_NEED_OFFICE,),
        PcSpec(cpu="ancien fictif", cpu_64bit=True, cpu_listed=False, cores=4, ghz=2.5, ram_gb=8, storage_gb=240,
               uefi_capable=True, firmware_mode="UEFI", secure_boot_on=True, tpm_version=1.2,
               tpm_enabled=True, disk_table="GPT"),
        "64 bits, 4 cœurs, 2,5 GHz, absent de la liste de compatibilité",
    ),
    Station(
        "Poste 3 — portable du gérant",
        ("Logiciel comptable pour Windows ; le disque doit être chiffré (vol possible) et le prestataire "
         "doit pouvoir s'y connecter avec le Bureau à distance."),
        (_NEED_OFFICE, _NEED_BITLOCKER, _NEED_RDP_HOST),
        PcSpec(cpu="i7 fictif", cpu_64bit=True, cpu_listed=True, cores=8, ghz=2.8, ram_gb=16, storage_gb=512,
               uefi_capable=True, firmware_mode="UEFI", secure_boot_on=True, tpm_version=2.0,
               tpm_enabled=True, disk_table="GPT"),
        "64 bits, 8 cœurs, 2,8 GHz, présent dans la liste de compatibilité",
    ),
)
STATION_CHECKS = {s.name: win11_check(s.spec) for s in STATIONS}
STATION_EDITIONS = {s.name: edition_needed(s.needs) for s in STATIONS}


def _tpm_label(spec: PcSpec) -> str:
    if spec.tpm_version == 0:
        return "absent"
    state = "activé" if spec.tpm_enabled else "désactivé dans le firmware"
    return f"version {spec.tpm_version:g}, {state}".replace(".", ",")


def station_rows() -> tuple[tuple[str, ...], ...]:
    """Relevé des trois postes (msinfo32, tpm.msc, Gestion des disques) : une ligne par poste."""
    rows = []
    for s in STATIONS:
        p = s.spec
        mode = "UEFI" if p.firmware_mode == "UEFI" else "Hérité (CSM activé ; le firmware sait aussi démarrer en UEFI)"
        rows.append((
            s.name,
            s.cpu_label,
            f"{p.ram_gb} Go",
            f"SSD {p.storage_gb} Go, table {p.disk_table}",
            mode,
            "activé" if p.secure_boot_on else "désactivé",
            _tpm_label(p),
            s.usage,
        ))
    return tuple(rows)


# =============================================================================================
# Partie 1 — service d'impression sous Linux (question X02)
# =============================================================================================

CUPS_ENABLED = False
CUPS_RUNNING = False
CUPS_FIX = service_fix(enabled=CUPS_ENABLED, running=CUPS_RUNNING)
CUPS_SCREEN: tuple[str, ...] = (
    "$ systemctl status cups",
    "○ cups.service - CUPS Scheduler",
    "  Loaded: loaded (/usr/lib/systemd/system/cups.service;",
    "          disabled; preset: enabled)",
    "  Active: inactive (dead)",
    "TriggeredBy: ○ cups.socket",
    "            ○ cups.path",
    "    Docs: man:cupsd(8)",
)

# =============================================================================================
# Dossier A — bureau d'architectes : installation propre de Windows 11 (questions X03 à X05)
# =============================================================================================

# Écran « Sélectionner l'emplacement d'installation de Windows 11 » (capture fictive).
# (disque, partition, nom, taille, type, sur le disque cible ?)
INSTALLER_ROWS: tuple[tuple[str, str, str, bool], ...] = (
    ("Disque 0 Partition 1 : SYSTEM", "100 Mo", "Système", False),
    ("Disque 0 Partition 2", "16 Mo", "MSR (réservé)", False),
    ("Disque 0 Partition 3 : Windows", "237,3 Go", "Principal", False),
    ("Disque 0 Partition 4", "750 Mo", "Récupération", False),
    ("Disque 1 Partition 1", "16 Mo", "MSR (réservé)", False),
    ("Disque 1 Partition 2 : PROJETS", "1863,0 Go", "Principal", False),
    ("Disque 2 Espace non alloué", "931,5 Go", "", True),
)
TARGET_DISK = "Disque 2"
INSTALLER_SCREEN: tuple[str, ...] = (
    "Sélectionner l'emplacement d'installation",
    "",
    "Nom                              Taille    Type",
    *(f"{name:<33}{size:<10}{kind}".rstrip() for name, size, kind, _t in INSTALLER_ROWS),
    "",
    "Supprimer  Formater  Nouveau  Charger un pilote",
)
# Rien n'est sauvegardé ni accordé pour les disques 0 et 1 : on n'y touche pas. Le disque 2 est
# neuf (espace non alloué) : on y installe, sans rien supprimer.
INSTALL_HERE = "Sélectionner pour installer (rien à supprimer)"
INSTALLER_ACTIONS = {
    name: INSTALL_HERE if on_target
    else partition_action(on_target_disk=False, backup_verified=True, written_consent=True)
    for name, _size, _kind, on_target in INSTALLER_ROWS
}
# Un SSD vendu « 1 To » (environ 1,0002 × 10^12 octets) apparaît comme 931,5 Go (en fait des Gio) ;
# un disque « 2 To », 1863,0 Go.
NEW_DISK_LABEL = "931,5 Go"

LICENCE = LIC_DIGITAL
LICENCE_EDITION = "Windows 11 Professionnel"
ACTIVATION = activation_result(LICENCE, LICENCE_EDITION, LICENCE_EDITION, same_pc=True)
CREATED_PARTITIONS = tuple((p.name, p.filesystem, p.size_label) for p in STANDARD_LAYOUT)

INSTALLER_FIGURE = Figure(
    key="ex02-installateur-disques",
    title="Installateur de Windows 11 : choix de l'emplacement (capture fictive)",
    alt=(
        "Écran de l'installateur de Windows 11, « Sélectionner l'emplacement d'installation ». "
        + " ; ".join(f"{name}, {size}" + (f", {kind}" if kind else "") for name, size, kind, _t in INSTALLER_ROWS)
        + ". Boutons : Supprimer, Formater, Nouveau, Charger un pilote."
    ),
    caption=(
        "Capture fictive, libellés approximatifs (ils changent selon la version de l'installateur). "
        "Les tailles sont celles qu'affiche Windows (en Gio, notées « Go »)."
    ),
    svg=screen_svg(INSTALLER_SCREEN, label="Capture fictive — installateur de Windows 11"),
)
INSTALLER_FIGURE_FILE = f"{STATIC_DIR_REF}/ex02-installateur-disques.svg"

# Gestionnaire de périphériques après l'installation (capture fictive, identifiants réels des
# fabricants, modèles fictifs). (rubrique, nom affiché, message, ID du matériel)
DEVICES: tuple[tuple[str, str, str, str], ...] = (
    ("Autres périphériques", "Contrôleur Ethernet",
     "Les pilotes de ce périphérique ne sont pas installés. (Code 28)",
     "PCI\\VEN_10EC&DEV_8125&SUBSYS_7C861462"),
    ("Autres périphériques", "Périphérique inconnu",
     "Les pilotes de ce périphérique ne sont pas installés. (Code 28)",
     "USB\\VID_04F9&PID_04B3&MI_00"),
    ("Cartes graphiques", "Carte graphique de base Microsoft",
     "Ce périphérique fonctionne correctement.",
     "PCI\\VEN_10DE&DEV_2882&SUBSYS_51801458"),
)
DEVICE_VENDORS = {name: vendor_name(hw) for _cat, name, _msg, hw in DEVICES}
DEVICE_FIRST_ACTION = {
    name: device_action(int(msg.rsplit("Code ", 1)[1].rstrip(")")))
    for _cat, name, msg, _hw in DEVICES if "Code " in msg
}

# Personnes du bureau (aucun serveur ni contrôleur de domaine : un NAS pour les fichiers).
# (personne, rôle, besoin au sens de PR10)
STAFF: tuple[tuple[str, str, str], ...] = (
    ("Anne Verhaegen", "gérante, valide les achats ; ne fait pas d'administration", NEED_DAILY),
    ("Karim", "architecte", NEED_DAILY),
    ("Sofia", "architecte", NEED_DAILY),
    ("Léo", "stagiaire jusqu'au 31 janvier", NEED_DAILY),
    ("Thomas", "technicien de ton atelier (contrat de maintenance) : logiciels, pilotes, comptes", NEED_ADMIN),
)
STAFF_ACCOUNTS = {person: account_for(need) for person, _role, need in STAFF}
SHARED_ACCOUNT_DECISION = account_for(NEED_SHARED)

# =============================================================================================
# Dossier B — Repair Café « La Clé » : Linux (questions X06 à X08)
# =============================================================================================

DUAL_BOOT_RAM_GB = 8
DUAL_BOOT_SWAP_GB = swap_advice(DUAL_BOOT_RAM_GB, hibernation=False)
DUAL_BOOT_SWAP_HIBERNATION_GB = swap_advice(DUAL_BOOT_RAM_GB, hibernation=True)

# Disque de 512 Go du portable, après réduction de C: depuis Windows (exemple fictif).
# (clé, nature PR09, libellés, largeur)
DUAL_BOOT_ZONES: tuple[tuple[str, str, tuple[str, ...], int], ...] = (
    ("esp", PK_ESP, ("1 ESP", "FAT32", "100 Mo"), 3),
    ("msr", PK_MSR, ("2 MSR", "16 Mo"), 2),
    ("windows", PK_WINDOWS, ("3 Windows", "NTFS", "300 Go"), 5),
    ("recovery", PK_RECOVERY, ("4 Récup.", "NTFS", "750 Mo"), 3),
    ("free", PK_FREE, ("5 Libre", "175 Go"), 4),
)
DUAL_BOOT_ACTIONS = {
    key: dual_boot_action(kind, backup_verified=True, written_consent=True)
    for key, kind, _lines, _w in DUAL_BOOT_ZONES
}
DUAL_BOOT_ACTIONS_WITHOUT_BACKUP = {
    key: dual_boot_action(kind, backup_verified=False, written_consent=True)
    for key, kind, _lines, _w in DUAL_BOOT_ZONES
}

PARTITIONS_FIGURE = Figure(
    key="ex02-partitions-double-demarrage",
    title="Disque du portable avant l'installation de Linux (schéma fictif)",
    alt=(
        "Barre d'un disque SSD de 512 Go, table GPT, du début à la fin du disque : "
        + " ; ".join(" ".join(lines) for _k, _kind, lines, _w in DUAL_BOOT_ZONES)
        + ". Largeurs non proportionnelles aux tailles."
    ),
    caption=(
        "Schéma fictif (cases non proportionnelles) : disque de 512 Go après réduction de C: depuis "
        "Windows ; zone 5 = espace non alloué."
    ),
    svg=partition_map_svg(
        (("SSD 512 Go — table GPT, démarrage UEFI",
          tuple(PartitionSegment(key, lines, w) for key, _kind, lines, w in DUAL_BOOT_ZONES)),)
    ),
)
PARTITIONS_FIGURE_FILE = f"{STATIC_DIR_REF}/ex02-partitions-double-demarrage.svg"

# Serveur de fichiers Debian du Repair Café : un disque neuf (vide) branché, les noms ont changé.
DATA_UUID = "3f6c2a9e-8b41-4d7a-9c5e-2b7d14a0e6f3"
FSTAB_BAD_LINE = "/dev/sdb1  /srv/partage  ext4  defaults  0  2"
FSTAB_FIXED_LINE = f"UUID={DATA_UUID}  /srv/partage  ext4  defaults,nofail  0  2"
OLD_DATA_NAME = "sdb1"
NEW_DATA_NAME = "sdc1"

EMERGENCY_SCREEN: tuple[str, ...] = (
    "[ TIME ] Timed out waiting for device dev-sdb1.device",
    "         - /dev/sdb1.",
    "[DEPEND] Dependency failed for srv-partage.mount",
    "         - /srv/partage.",
    "[DEPEND] Dependency failed for local-fs.target",
    "         - Local File Systems.",
    "You are in emergency mode. After logging in, type",
    "\"journalctl -xb\" to view system logs, \"systemctl",
    "reboot\" to reboot, \"systemctl default\" or \"exit\"",
    "to boot into default mode.",
    "Give root password for maintenance",
    "(or press Control-D to continue):",
)
LSBLK_SCREEN: tuple[str, ...] = (
    "# lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS",
    "NAME     SIZE FSTYPE LABEL   MOUNTPOINTS",
    "sda    238.5G",
    "├─sda1   512M vfat           /boot/efi",
    "├─sda2 229.9G ext4           /",
    "└─sda3   8.1G swap           [SWAP]",
    "sdb    931.5G",
    "sdc      1.8T",
    "└─sdc1   1.8T ext4   PARTAGE",
    "# blkid /dev/sdc1",
    "/dev/sdc1: LABEL=\"PARTAGE\"",
    f"  UUID=\"{DATA_UUID}\"",
    "  TYPE=\"ext4\"",
    "# grep partage /etc/fstab",
    FSTAB_BAD_LINE,
)

# Dossier partagé du Repair Café : droits relevés (ls -l) et comptes (id).
SHARE_DIR = ("drwxrwx---", "jean", "benevoles", "/srv/partage/fiches")
SHARE_FILE = ("-rw-r-----", "jean", "benevoles", "inventaire.ods")
USERS: dict[str, tuple[str, ...]] = {
    "jean": ("jean", "sudo", "benevoles"),
    "lucie": ("lucie",),
    "marc": ("marc", "benevoles"),
}
SHARE_DIR_OCTAL = mode_octal(SHARE_DIR[0])
SHARE_FILE_OCTAL = mode_octal(SHARE_FILE[0])
SHARE_FILE_FIXED_OCTAL = "660"


def access(user: str, target: tuple[str, str, str, str], right: str) -> bool:
    mode, owner, group, _name = target
    return can_access(user, USERS[user], owner, group, mode, right)


PERMISSIONS_SCREEN: tuple[str, ...] = (
    "lucie@clef-srv:~$ ls -ld /srv/partage/fiches",
    f"{SHARE_DIR[0]} 2 {SHARE_DIR[1]} {SHARE_DIR[2]} 4096 Oct 20 10:12",
    f"  {SHARE_DIR[3]}",
    "lucie@clef-srv:~$ cd /srv/partage/fiches",
    "-bash: cd: /srv/partage/fiches: Permission denied",
    "lucie@clef-srv:~$ sudo usermod -aG benevoles lucie",
    "[sudo] password for lucie:",
    "lucie is not in the sudoers file.",
    "lucie@clef-srv:~$ id",
    "uid=1002(lucie) gid=1002(lucie) groups=1002(lucie)",
    "",
    "marc@clef-srv:/srv/partage/fiches$ ls -l",
    f"{SHARE_FILE[0]} 1 {SHARE_FILE[1]} {SHARE_FILE[2]} 18342 Oct 21 16:05",
    f"  {SHARE_FILE[3]}",
    "marc@clef-srv:/srv/partage/fiches$ id",
    "uid=1003(marc) gid=1003(marc)",
    "  groups=1003(marc),1001(benevoles)",
)

# =============================================================================================
# Dossier C — agence immobilière : Windows ne démarre plus, puis restauration (X09, X10)
# =============================================================================================

FAILED_DRIVER = "gfxdrv64.sys"  # nom inventé
STOP_CODE = "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED"
STOP_SCREEN: tuple[str, ...] = (
    ":(",
    "",
    "Votre PC a rencontré un problème et doit",
    "redémarrer. Nous collectons simplement des",
    "informations relatives aux erreurs, puis nous",
    "allons redémarrer à votre place.",
    "",
    "100 % effectué",
    "",
    f"Code d'arrêt : {STOP_CODE}",
    f"Ce qui a échoué : {FAILED_DRIVER}",
)
STOP_FIGURE = Figure(
    key="ex02-ecran-arret",
    title="Écran d'arrêt de Windows au démarrage (capture fictive)",
    alt="Écran d'arrêt Windows : " + " / ".join(line for line in STOP_SCREEN if line) + ".",
    caption=(
        "Capture fictive : texte et code d'arrêt au format de Windows ; nom du pilote inventé. "
        "Selon la version, le fond est bleu ou noir et la mise en page change."
    ),
    svg=screen_svg(STOP_SCREEN, label="Capture fictive — écran d'arrêt (nom de pilote inventé)"),
)
STOP_FIGURE_FILE = f"{STATIC_DIR_REF}/ex02-ecran-arret.svg"

WINRE_SCREEN: tuple[str, ...] = (
    "Réparation automatique",
    "La réparation automatique n'a pas pu réparer",
    "votre PC.",
    "[ Arrêter ]   [ Options avancées ]",
    "",
    "Dépannage > Options avancées",
    *(line for label, role in WINRE_OPTIONS for line in (f"> {label}", f"    {role}")),
)

# Points de restauration proposés par rstrui (fictifs). (date, description, type)
RESTORE_POINTS: tuple[tuple[str, str, str], ...] = (
    ("26/10/2026 18:41", "Installation du pilote graphique 31.0.4 (utilitaire du fabricant)", "Installation"),
    ("22/10/2026 03:05", "Windows Update", "Critique"),
)
RESTORE_POINT_TO_USE = RESTORE_POINTS[0]

LEAST_INVASIVE = LADDER_BY_NAME["Annuler le dernier changement"]
SYSTEM_RESTORE = LADDER_BY_NAME["Restauration du système"]
RESET_KEEP = LADDER_BY_NAME["Réinitialiser en conservant les fichiers"]
FULL_REINSTALL = LADDER_BY_NAME["Réinstallation complète"]
REPAIR_FILES = LADDER_BY_NAME["Réparer les fichiers système"]

# Second poste de l'agence : système endommagé, réinitialisation prévue après sauvegarde.
BACKUP_SET: tuple[BackupFile, ...] = (
    BackupFile("mandats-2026.xlsx", b"Mandats 2026 - classeur fictif Jury Central EX02\n" * 50,
               b"Mandats 2026 - classeur fictif Jury Central EX02\n" * 50),
    BackupFile("photos-biens.zip", b"PK-archive-fictive-photos-biens-EX02-" * 80,
               (b"PK-archive-fictive-photos-biens-EX02-" * 80)[:2048]),
    BackupFile("compromis-0918.pdf", b"%PDF-1.7 compromis fictif 0918 EX02\n" * 40,
               b"%PDF-1.7 compromis fictif 0918 EX02\n" * 40),
)
BACKUP_HASHES: tuple[tuple[str, str, str], ...] = tuple(
    (f.name, sha256_hex(f.original), sha256_hex(f.copy)) for f in BACKUP_SET
)
BACKUP_VERDICTS = {f.name: copy_check(f) for f in BACKUP_SET}
BAD_COPIES = tuple(name for name, verdict in BACKUP_VERDICTS.items() if "différente" in verdict)
RESET_EFFECT = effect_of(RESET_KEEP)
RESET_PRECAUTION = precaution_for(RESET_KEEP)
REINSTALL_EFFECT = effect_of(FULL_REINSTALL)

# =============================================================================================
# Fichiers statiques
# =============================================================================================

EX02_FIGURES: tuple[Figure, ...] = (INSTALLER_FIGURE, PARTITIONS_FIGURE, STOP_FIGURE)
# Schémas aussi servis comme documents des questions (fichier statique, même SVG).
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (INSTALLER_FIGURE, INSTALLER_FIGURE_FILE),
    (PARTITIONS_FIGURE, PARTITIONS_FIGURE_FILE),
    (STOP_FIGURE, STOP_FIGURE_FILE),
)
SCREENS: dict[str, tuple[str, ...]] = {
    "installer": INSTALLER_SCREEN,
    "cups": CUPS_SCREEN,
    "emergency": EMERGENCY_SCREEN,
    "lsblk": LSBLK_SCREEN,
    "permissions": PERMISSIONS_SCREEN,
    "stop": STOP_SCREEN,
    "winre": WINRE_SCREEN,
}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que EX01)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


def figure_document_text(figure: Figure) -> str:
    """Description écrite complète d'un schéma, affichée sous l'image dans la question."""
    return figure.alt

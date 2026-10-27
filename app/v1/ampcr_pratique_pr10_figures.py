"""PR10 « Comptes, pilotes, paramètres et commandes » — données de référence, règles de décision
et schémas SVG (ticket #214).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket214_ampcr_pratique_pr10.py` :

- les types de comptes (`ACCOUNT_TYPES`), les groupes utiles (`WINDOWS_GROUPS`, `LINUX_GROUPS`),
  le compte adapté à un besoin selon le moindre privilège (`account_for`) et l'élévation
  demandée par l'UAC ou sudo (`elevation`) ;
- les permissions Linux (`mode_string`, `mode_octal`, `can_access`) et leur schéma ;
- les pilotes : états du Gestionnaire de périphériques (`DEVICE_STATES`, `device_action`),
  identifiants matériels PCI et USB (`parse_hardware_id`, `vendor_name`) et sources fiables ;
- les paramètres, services et démarrage (`SETTINGS_TOOLS`, `WIN_START_TYPES`,
  `service_fix`) ;
- les commandes de base Windows et Linux (`COMMANDS`) : syntaxe, rôle, sortie attendue,
  droits nécessaires et risques — la même table alimente le cours, les classements et les
  corrigés ;
- quatre procédures illustrées (`ACCOUNT_STEPS`, `DRIVER_STEPS`, `SERVICE_STEPS`,
  `NETWORK_STEPS`) et un arbre de décision (`DEVICE_TREE`) ;
- des relevés fictifs (Windows en français, Linux en anglais) produits par les générateurs
  de PR20 et PR24 (`ipconfig_all_lines`, `win_ping_lines`, `tracert_lines`, `nslookup_lines`).

Les libellés de Windows 11 et des distributions Linux sont ceux **de la rédaction (octobre
2026)** ; ils changent selon les versions : la documentation de l'éditeur fait foi. Les
sorties de Windows sont montrées **en français** (poste belge), celles de Linux **en anglais**
(système réglé en anglais, ou commande précédée de `LANG=C`), comme en PR09 et PR24. Les
captures sont **fictives** et abrégées ; aucun schéma ne vient d'une image générée ni d'une
photographie. Les adresses publiques viennent des plages de documentation de la RFC 5737.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr08_figures import VENDOR_IDS
from app.v1.ampcr_pratique_pr20_figures import Host, ipconfig_all_lines
from app.v1.ampcr_pratique_pr24_figures import (
    NS_OK,
    nslookup_lines,
    win_ping_lines,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR09)
WRITTEN_AT = "octobre 2026"
FICTIVE_LABEL = "Capture fictive — sortie abrégée"

WINDOWS = "Windows"
LINUX = "Linux"

# =============================================================================================
# 1. Comptes, groupes et moindre privilège
# =============================================================================================


@dataclass(frozen=True)
class AccountType:
    key: str
    name: str
    windows: str
    linux: str
    rights: str
    usage: str


ACC_STANDARD = AccountType(
    "standard", "Compte standard (utilisateur)",
    "Membre du groupe Utilisateurs", "Utilisateur hors du groupe sudo (wheel sous Fedora)",
    "Utilise le poste, modifie ses propres fichiers et réglages ; rien pour tout le système.",
    "Usage quotidien de chaque personne, administrateurs compris.",
)
ACC_ADMIN = AccountType(
    "admin", "Compte administrateur nominatif",
    "Membre du groupe Administrateurs ; l'UAC demande une confirmation",
    "Membre du groupe sudo (wheel sous Fedora) ; sudo demande son mot de passe",
    "Installe des logiciels et des pilotes, gère les comptes, les services et les paramètres "
    "du système, après élévation.",
    "La personne chargée d'administrer, et seulement pour les tâches d'administration.",
)
ACC_BUILTIN = AccountType(
    "builtin", "Compte intégré (Administrateur, root)",
    "« Administrateur » intégré, désactivé par défaut",
    "root, verrouillé par défaut sous Ubuntu (on passe par sudo)",
    "Tous les droits, sans confirmation.",
    "Dépannage exceptionnel seulement ; jamais pour travailler.",
)
ACC_DOMAIN = AccountType(
    "domain", "Compte de domaine",
    "DOMAINE\\nom, créé sur le contrôleur de domaine (Active Directory)",
    "Compte de l'annuaire de l'entreprise (poste Linux joint au domaine)",
    "Droits donnés par les groupes du domaine ; même compte sur tous les postes du domaine.",
    "Entreprise ou école avec un serveur : comptes et mots de passe gérés au même endroit.",
)
ACCOUNT_TYPES: tuple[AccountType, ...] = (ACC_STANDARD, ACC_ADMIN, ACC_BUILTIN, ACC_DOMAIN)

# (groupe local, rôle) — noms de Windows 11 en français, groupes courants d'Ubuntu/Debian.
WINDOWS_GROUPS: tuple[tuple[str, str], ...] = (
    ("Administrateurs", "Contrôle total du poste, après confirmation de l'UAC."),
    ("Utilisateurs", "Comptes standard : usage du poste sans modifier le système."),
    ("Utilisateurs du Bureau à distance", "Connexion à distance (Bureau à distance) autorisée."),
    ("Invités", "Accès très limité ; compte Invité désactivé par défaut."),
)
LINUX_GROUPS: tuple[tuple[str, str], ...] = (
    ("sudo (wheel sous Fedora)", "Peut lancer des commandes d'administration avec sudo."),
    ("adm", "Lit les journaux du système (/var/log, journalctl complet)."),
    ("lpadmin", "Gère les imprimantes (CUPS)."),
    ("dialout", "Utilise les ports série (adaptateur USB-série, matériel de laboratoire)."),
    ("Groupe de projet (ex. compta)", "Partage un dossier entre plusieurs comptes (chmod, chown)."),
)

NEED_DAILY = "Usage quotidien d'une personne"
NEED_ADMIN = "Administration du poste"
NEED_CENTRAL = "Réseau d'entreprise avec serveur"
NEED_SHARED = "Plusieurs personnes sur un même compte"
NEEDS = (NEED_DAILY, NEED_ADMIN, NEED_CENTRAL, NEED_SHARED)

ACCOUNT_REFUSE = "Refuser : un compte par personne"
ACCOUNT_CHOICES = (ACC_STANDARD.name, ACC_ADMIN.name, ACC_DOMAIN.name, ACCOUNT_REFUSE)


def account_for(need: str) -> str:
    """Compte à créer selon le principe du moindre privilège (convention du cours)."""
    return {
        NEED_DAILY: ACC_STANDARD.name,
        NEED_ADMIN: ACC_ADMIN.name,
        NEED_CENTRAL: ACC_DOMAIN.name,
        NEED_SHARED: ACCOUNT_REFUSE,
    }[need]


ELEV_NONE = "Aucune élévation : la commande s'exécute"
ELEV_CONSENT = "UAC : invite de consentement (Oui / Non)"
ELEV_CREDENTIALS = "UAC : nom et mot de passe d'un administrateur"
ELEV_SUDO = "sudo : mot de passe de l'utilisateur lui-même"
ELEV_REFUSED = "sudo refusé : « is not in the sudoers file »"


def elevation(os_name: str, *, is_admin: bool, needs_admin: bool) -> str:
    """Ce qui se passe quand un compte lance une action (réglages par défaut de l'UAC sous
    Windows ; sudo sous Linux, l'administrateur étant membre du groupe sudo)."""
    if not needs_admin:
        return ELEV_NONE
    if os_name == WINDOWS:
        return ELEV_CONSENT if is_admin else ELEV_CREDENTIALS
    if os_name == LINUX:
        return ELEV_SUDO if is_admin else ELEV_REFUSED
    raise ValueError(os_name)


ACCOUNT_STEPS: tuple[tuple[str, str], ...] = (
    ("Recueillir le besoin", "Qui utilise le poste, pour quoi faire ; qui administre ?"),
    ("Choisir le type de compte", "Standard par défaut ; administrateur nominatif si nécessaire."),
    ("Créer le compte", "Paramètres → Comptes, net user nom * /add ou sudo adduser nom."),
    ("Mot de passe", "Personnel, saisi par l'utilisateur ; changement à la 1re connexion."),
    ("Groupes", "Administrateurs ou sudo seulement pour l'administrateur ; groupe de projet."),
    ("Contrôler", "net user nom ou groups nom ; connexion d'essai avec l'utilisateur."),
)

# =============================================================================================
# 2. Permissions Linux
# =============================================================================================

_TRIPLET = ("r", "w", "x")


def mode_string(octal: str) -> str:
    """« 750 » → « rwxr-x--- » (trois chiffres : propriétaire, groupe, autres)."""
    if len(octal) != 3 or any(c not in "01234567" for c in octal):
        raise ValueError(octal)
    return "".join(
        letter if int(digit) & bit else "-"
        for digit in octal
        for letter, bit in zip(_TRIPLET, (4, 2, 1), strict=True)
    )


def mode_octal(mode: str) -> str:
    """« rwxr-x--- » (ou « -rwxr-x--- » / « drwxr-x--- » de ls -l) → « 750 »."""
    bits = mode[-9:]
    if len(bits) != 9:
        raise ValueError(mode)
    digits = []
    for i in range(0, 9, 3):
        value = 0
        for letter, bit, char in zip(_TRIPLET, (4, 2, 1), bits[i:i + 3], strict=True):
            if char == letter:
                value += bit
            elif char != "-":
                raise ValueError(mode)
        digits.append(str(value))
    return "".join(digits)


CLASS_OWNER, CLASS_GROUP, CLASS_OTHER = "propriétaire", "groupe", "autres"


def permission_class(user: str, user_groups: tuple[str, ...], owner: str, group: str) -> str:
    """Classe appliquée : la **première** qui correspond (propriétaire, puis groupe, puis
    autres) ; un propriétaire sans droit ne « retombe » pas sur ceux du groupe."""
    if user == owner:
        return CLASS_OWNER
    if group in user_groups:
        return CLASS_GROUP
    return CLASS_OTHER


def can_access(user: str, user_groups: tuple[str, ...], owner: str, group: str, mode: str,
               right: str) -> bool:
    """Droit `r`, `w` ou `x` d'un utilisateur ordinaire (pas root) sur un fichier ou dossier."""
    if right not in _TRIPLET:
        raise ValueError(right)
    bits = mode[-9:]
    offset = (CLASS_OWNER, CLASS_GROUP, CLASS_OTHER).index(permission_class(user, user_groups, owner, group)) * 3
    return bits[offset + _TRIPLET.index(right)] == right


# (droit, sur un fichier, sur un dossier)
RIGHTS_MEANING: tuple[tuple[str, str, str], ...] = (
    ("r (4)", "Lire le contenu", "Lister les noms des fichiers"),
    ("w (2)", "Modifier le contenu", "Créer, renommer, supprimer des fichiers (avec x)"),
    ("x (1)", "Exécuter (script, programme)", "Entrer dans le dossier (cd), atteindre ses fichiers"),
)

PERM_EXAMPLE_MODE = "-rw-r-----"
PERM_EXAMPLE_OWNER = "anne"
PERM_EXAMPLE_GROUP = "compta"
PERM_EXAMPLE_FILE = "budget.ods"


def permission_bits_svg(mode: str, owner: str, group: str, *, width: int = 380) -> str:
    """Les dix caractères de `ls -l` découpés en type + trois triplets, avec la classe de
    chaque triplet et sa valeur octale (lettres et chiffres : rien ne repose sur la couleur)."""
    if len(mode) != 10:
        raise ValueError(mode)
    octal = mode_octal(mode)
    cell_w, top = 30, 34
    left = (width - cell_w * 10 - 3 * 8) // 2
    heading = escape(f"{mode} {owner} {group} {PERM_EXAMPLE_FILE}")
    parts = [f'<text x="{width // 2}" y="20" text-anchor="middle" font-size="13" font-weight="700">{heading}</text>']
    labels = (("type", "fichier" if mode[0] == "-" else "dossier", ""),
              ("propriétaire", owner, octal[0]), ("groupe", group, octal[1]), ("autres", "les autres", octal[2]))
    x = left
    for index, (cls, who, digit) in enumerate(labels):
        chars = mode[0:1] if index == 0 else mode[1 + 3 * (index - 1): 4 + 3 * (index - 1)]
        box_w = cell_w * len(chars)
        parts.append(
            f'<g data-class="{escape(cls)}" data-chars="{escape(chars)}">'
            f'<rect x="{x}" y="{top}" width="{box_w}" height="36" rx="4" fill="#eef2f8" '
            'stroke="#33415c" stroke-width="1.5"/>'
        )
        for j, char in enumerate(chars):
            parts.append(
                f'<text x="{x + cell_w * j + cell_w // 2}" y="{top + 24}" text-anchor="middle" '
                f'font-size="17" font-family="ui-monospace, monospace" font-weight="700">{escape(char)}</text>'
            )
        center = x + box_w // 2
        parts.append(
            f'<text x="{center}" y="{top + 56}" text-anchor="middle" font-size="11.5" font-weight="700">'
            f"{escape(cls)}</text>"
            f'<text x="{center}" y="{top + 72}" text-anchor="middle" font-size="11">{escape(who)}</text>'
        )
        if digit:
            parts.append(
                f'<text x="{center}" y="{top + 90}" text-anchor="middle" font-size="11.5">= {digit}</text>'
            )
        parts.append("</g>")
        x += box_w + 8
    parts.append(
        f'<text x="{width // 2}" y="{top + 116}" text-anchor="middle" font-size="12">'
        f"{escape(f'r = 4 · w = 2 · x = 1 · - = 0 → chmod {octal}')}</text>"
    )
    return _svg(width, top + 128, parts)


PERM_FIGURE = Figure(
    key="pr10-permissions",
    title="Lire les permissions d'un fichier sous Linux (ls -l)",
    alt=(
        f"La ligne « {PERM_EXAMPLE_MODE} {PERM_EXAMPLE_OWNER} {PERM_EXAMPLE_GROUP} {PERM_EXAMPLE_FILE} » "
        "est découpée en quatre cases : le premier caractère « - » indique un fichier ordinaire "
        "(« d » pour un dossier) ; « rw- » est le triplet du propriétaire anne, valeur 6 ; "
        "« r-- » celui du groupe compta, valeur 4 ; « --- » celui des autres, valeur 0. "
        f"Légende : r vaut 4, w vaut 2, x vaut 1, tiret 0, d'où chmod {mode_octal(PERM_EXAMPLE_MODE)}."
    ),
    caption=(
        "anne lit et modifie le fichier, les membres de compta le lisent seulement, les autres "
        "n'y ont pas accès. On additionne les droits de chaque triplet pour obtenir le chiffre "
        "de chmod."
    ),
    svg=permission_bits_svg(PERM_EXAMPLE_MODE, PERM_EXAMPLE_OWNER, PERM_EXAMPLE_GROUP),
)

# =============================================================================================
# 3. Pilotes et périphériques
# =============================================================================================

DEV_INSTALL = "Installer le bon pilote"
DEV_ENABLE = "Réactiver le périphérique"
DEV_ROLLBACK = "Restaurer le pilote précédent"
DEV_HARDWARE = "Contrôler le matériel et la connexion"
DEVICE_ACTIONS = (DEV_INSTALL, DEV_ENABLE, DEV_ROLLBACK, DEV_HARDWARE)


@dataclass(frozen=True)
class DeviceState:
    shown: str  # ce qu'affiche le Gestionnaire de périphériques
    message: str  # « État du périphérique » (onglet Général des propriétés)
    meaning: str
    action: str


# Codes d'erreur du Gestionnaire de périphériques (documentation Microsoft).
DEVICE_STATES: tuple[DeviceState, ...] = (
    DeviceState("Point d'exclamation jaune, rubrique « Autres périphériques »",
                "Les pilotes de ce périphérique ne sont pas installés. (Code 28)",
                "Windows ne trouve aucun pilote : périphérique inconnu.", DEV_INSTALL),
    DeviceState("Flèche vers le bas sur l'icône",
                "Ce périphérique est désactivé. (Code 22)",
                "Quelqu'un a désactivé le périphérique.", DEV_ENABLE),
    DeviceState("Point d'exclamation jaune après une mise à jour du pilote",
                "Ce périphérique ne peut pas démarrer. (Code 10)",
                "Le pilote installé ne convient pas ou est défectueux.", DEV_ROLLBACK),
    DeviceState("Point d'exclamation jaune sur un périphérique USB",
                "Windows a arrêté ce périphérique car il a signalé des problèmes. (Code 43)",
                "Le périphérique ou sa connexion répond mal (port, câble, alimentation).", DEV_HARDWARE),
)
DEVICE_STATES_BY_CODE = {int(s.message.rsplit("Code ", 1)[1].rstrip(")")): s for s in DEVICE_STATES}


def device_action(code: int, *, after_driver_update: bool = False) -> str:
    """Première action selon le code d'erreur ; un Code 10 apparu juste après une mise à jour
    du pilote se traite par la restauration, sinon par l'installation du bon pilote."""
    if code == 10:
        return DEV_ROLLBACK if after_driver_update else DEV_INSTALL
    return DEVICE_STATES_BY_CODE[code].action


# Identifiants de fabricants USB (USB-IF, liste publique des Vendor ID) ; PCI : table de PR08.
USB_VENDOR_IDS: dict[str, str] = {
    "046D": "Logitech",
    "04F9": "Brother",
    "03F0": "HP",
    "04A9": "Canon",
    "0BDA": "Realtek",
}


@dataclass(frozen=True)
class HardwareId:
    bus: str
    vendor_id: str
    device_id: str


def parse_hardware_id(text: str) -> HardwareId:
    """« PCI\\VEN_14E4&DEV_43A0&SUBSYS… » ou « USB\\VID_04F9&PID_0062… » → bus, fabricant, modèle."""
    bus, _sep, rest = text.strip().partition("\\")
    fields = dict(part.split("_", 1) for part in rest.split("&") if "_" in part)
    if bus == "PCI":
        return HardwareId(bus, fields["VEN"][:4].upper(), fields["DEV"][:4].upper())
    if bus == "USB":
        return HardwareId(bus, fields["VID"][:4].upper(), fields["PID"][:4].upper())
    raise ValueError(text)


def vendor_name(text: str) -> str | None:
    """Fabricant d'un identifiant matériel (None si absent des tables du cours)."""
    hw = parse_hardware_id(text)
    return (VENDOR_IDS if hw.bus == "PCI" else USB_VENDOR_IDS).get(hw.vendor_id)


# Sources de pilotes, de la plus sûre à la moins adaptée ; dernière ligne : à refuser.
DRIVER_SOURCES: tuple[tuple[str, str], ...] = (
    ("Windows Update (mises à jour facultatives → pilotes)", "Pilotes signés et testés pour ce Windows."),
    ("Site du fabricant du PC (portable, PC de marque)", "Pilotes adaptés au modèle exact (numéro sur l'étiquette)."),
    ("Site du fabricant du composant (Intel, NVIDIA, Realtek, Brother…)", "Version récente ; vérifier le modèle, la version de Windows et l'architecture."),
    ("Site « tous pilotes gratuits », logiciel « driver booster »", "À refuser : pilotes non vérifiés, logiciels indésirables."),
)

DRIVER_STEPS: tuple[tuple[str, str], ...] = (
    ("Identifier le périphérique", "Gestionnaire de périphériques → Propriétés → Détails → ID du matériel."),
    ("Noter l'état", "Message et code (28, 22, 10, 43) ; changement récent ?"),
    ("Choisir la source", "Windows Update, site du fabricant ; modèle, version de Windows, 64 bits."),
    ("Créer un point de restauration", "Avant toute installation ou mise à jour de pilote."),
    ("Installer ou restaurer", "Installer, mettre à jour, ou « Restaurer le pilote » après une mauvaise mise à jour."),
    ("Contrôler", "« Ce périphérique fonctionne correctement » ; essai réel du périphérique."),
)

DEVICE_TREE: tuple[tuple[str, str], ...] = (
    ("Le périphérique apparaît-il dans le Gestionnaire ?",
     "Matériel : autre port, autre câble, alimentation, autre PC (lsusb sous Linux)."),
    ("Est-il activé (pas de flèche vers le bas) ?",
     "Code 22 : clic droit → Activer le périphérique."),
    ("Un pilote est-il installé (pas de Code 28) ?",
     "ID du matériel → pilote du fabricant ou Windows Update."),
    ("Fonctionnait-il avant la dernière mise à jour ?",
     "Propriétés → Pilote → Restaurer le pilote."),
)
DEVICE_FINAL = (
    "Pilote récent et adapté, pas de code d'erreur : tester le périphérique, puis noter la "
    "version du pilote dans le rapport."
)

# =============================================================================================
# 4. Paramètres, services et démarrage
# =============================================================================================

# (tâche, Windows, Linux)
SETTINGS_TOOLS: tuple[tuple[str, str, str], ...] = (
    ("Réglages courants (affichage, réseau, comptes)", "Paramètres (Win + I)", "Paramètres du bureau (GNOME, KDE…)"),
    ("Périphériques et pilotes", "Gestionnaire de périphériques (devmgmt.msc)", "lspci -k, lsusb, lsblk"),
    ("Services", "Services (services.msc)", "systemctl"),
    ("Programmes lancés au démarrage", "Gestionnaire des tâches → Applications de démarrage", "systemctl list-unit-files --state=enabled ; applications au démarrage du bureau"),
    ("Journaux d'événements", "Observateur d'événements (eventvwr.msc)", "journalctl"),
    ("Comptes et groupes", "Paramètres → Comptes ; lusrmgr.msc (éditions Pro)", "Paramètres → Utilisateurs ; adduser, usermod, groups"),
    ("Disques", "Gestion des disques (diskmgmt.msc)", "lsblk, df -h"),
)

# Types de démarrage d'un service Windows (console Services).
WIN_START_TYPES: tuple[tuple[str, str], ...] = (
    ("Automatique", "Démarre avec Windows."),
    ("Automatique (début différé)", "Démarre peu après l'ouverture de Windows."),
    ("Manuel", "Démarre à la demande d'un programme ou d'un administrateur."),
    ("Désactivé", "Ne peut pas démarrer, même à la demande."),
)

SVC_OK = "Rien à faire : service actif et lancé au démarrage"
SVC_ENABLE_START = "Activer au démarrage et démarrer"
SVC_ENABLE = "Activer au démarrage (il tourne, mais pas après un redémarrage)"
SVC_DIAGNOSE = "Lire le journal, corriger la cause, puis redémarrer le service"
SVC_ACTIONS = (SVC_OK, SVC_ENABLE_START, SVC_ENABLE, SVC_DIAGNOSE)


def service_fix(*, enabled: bool, running: bool, failed: bool = False) -> str:
    """Action pour un service **nécessaire** au client (systemd : enabled/disabled et
    active/inactive/failed ; Windows : Automatique/Désactivé et En cours d'exécution/Arrêté)."""
    if failed:
        return SVC_DIAGNOSE
    if enabled and running:
        return SVC_OK
    if not running:
        return SVC_ENABLE_START if not enabled else SVC_DIAGNOSE
    return SVC_ENABLE


SERVICE_STEPS: tuple[tuple[str, str], ...] = (
    ("Constater le symptôme", "Ex. impression impossible ; message exact noté."),
    ("Identifier le service", "Spouleur d'impression (Windows), cups (Linux)."),
    ("Lire son état", "services.msc : État, Type de démarrage ; systemctl status cups."),
    ("Chercher la cause", "Observateur d'événements ou journalctl -u cups -b."),
    ("Corriger et démarrer", "Type Automatique + Démarrer ; sudo systemctl enable --now cups."),
    ("Contrôler", "Service en cours d'exécution ; page de test imprimée ; après redémarrage aussi."),
)

# =============================================================================================
# 5. Commandes de base : syntaxe, rôle, sortie, droits, risques
# =============================================================================================

RIGHT_STANDARD = "Compte standard"
RIGHT_ADMIN = "Administrateur (UAC ou sudo)"
RIGHT_CATEGORIES = (RIGHT_STANDARD, RIGHT_ADMIN)


@dataclass(frozen=True)
class Command:
    name: str
    os_name: str
    syntax: str
    role: str
    output: str
    rights: str
    risk: str


COMMANDS: tuple[Command, ...] = (
    Command("ipconfig", WINDOWS, "ipconfig /all",
            "Configuration IP de chaque carte : IPv4, masque, passerelle, DNS, MAC, DHCP.",
            "Une rubrique par carte ; « IPv4 d'autoconfiguration » 169.254.x.x = pas de DHCP.",
            "Standard pour lire ; /release, /renew et /flushdns : invite administrateur.",
            "/release coupe le réseau du poste (perte de la prise en main à distance)."),
    Command("ping", WINDOWS, "ping 192.168.1.1",
            "Teste qu'une adresse répond (4 échos par défaut sous Windows).",
            "« Réponse de … temps=… TTL=… » ou « Délai d'attente de la demande dépassé » ; statistiques.",
            RIGHT_STANDARD,
            "Aucun pour le poste ; un pare-feu peut bloquer l'écho : pas de réponse ≠ panne certaine."),
    Command("tracert", WINDOWS, "tracert -d 203.0.113.10",
            "Liste les routeurs (sauts) traversés jusqu'à la destination.",
            "Une ligne par saut ; « * Délai dépassé » là où un routeur ne répond pas.",
            RIGHT_STANDARD,
            "Long ; un saut silencieux n'est pas toujours une coupure."),
    Command("nslookup", WINDOWS, "nslookup www.exemple.be",
            "Interroge le serveur DNS : nom → adresse.",
            "Serveur interrogé, puis adresse ; « Non-existent domain » ou délai expiré.",
            RIGHT_STANDARD, "Aucun (lecture seule)."),
    Command("sfc", WINDOWS, "sfc /scannow",
            "Vérifie les fichiers système protégés et remplace ceux qui sont endommagés.",
            "« … n'a trouvé aucune violation d'intégrité » ou fichiers réparés ; détails dans CBS.log.",
            "Invite de commandes en administrateur.",
            "Long (ne pas interrompre) ; si SFC ne répare pas, DISM d'abord."),
    Command("DISM", WINDOWS, "DISM /Online /Cleanup-Image /RestoreHealth",
            "Répare le magasin de composants de Windows, la référence utilisée par SFC.",
            "Barre de progression puis « L'opération de restauration s'est terminée correctement. »",
            "Invite de commandes en administrateur.",
            "Long ; a besoin de Windows Update (Internet) ou d'une source ; puis relancer sfc."),
    Command("tasklist", WINDOWS, "tasklist /fi \"imagename eq spoolsv.exe\"",
            "Liste les processus en cours : nom de l'image, PID, mémoire utilisée.",
            "Une ligne par processus ; « aucune tâche en service ne correspond » si absent.",
            RIGHT_STANDARD,
            "Aucun pour lire ; arrêter un processus (taskkill) fait perdre le travail non enregistré."),
    Command("net user", WINDOWS, "net user marie",
            "Liste les comptes locaux ou affiche un compte (actif, groupes locaux).",
            "« Compte : actif Oui », « Appartient aux groupes locaux *Utilisateurs ».",
            "Standard pour lire ; /add, /delete, /active : invite administrateur.",
            "Mot de passe tapé en clair dans la commande : utiliser * pour qu'il soit demandé."),
    Command("ip", LINUX, "ip a ; ip route",
            "Interfaces, adresses et routes (passerelle par défaut).",
            "« inet 192.168.1.20/24 », « state UP » ; « default via 192.168.1.1 ».",
            "Standard pour lire ; sudo pour modifier.",
            "Une modification avec ip est perdue au redémarrage ; peut couper une session à distance."),
    Command("systemctl", LINUX, "systemctl status cups",
            "État d'un service ; démarrer, arrêter, activer au démarrage.",
            "« Active: active (running) », « inactive (dead) » ou « failed » ; « enabled » / « disabled ».",
            "Standard pour status ; sudo pour start, stop, restart, enable, disable.",
            "Arrêter ssh ou le réseau d'une machine distante : on perd l'accès."),
    Command("journalctl", LINUX, "journalctl -u cups -b",
            "Lit le journal du système (d'un service, depuis le démarrage, par priorité).",
            "Messages horodatés ; -p err pour les erreurs seulement.",
            "Groupe adm ou sudo pour tout le journal ; sinon ses propres messages.",
            "Aucun pour lire ; --vacuum-size supprime d'anciens journaux."),
    Command("lsblk", LINUX, "lsblk -f",
            "Disques et partitions : taille, système de fichiers, UUID, point de montage.",
            "Arbre sda → sda1 ; colonne MOUNTPOINTS vide = partition non montée.",
            RIGHT_STANDARD,
            "Aucun (lecture) ; sert à identifier la cible avant toute écriture sur un disque."),
    Command("df", LINUX, "df -h",
            "Espace utilisé et libre de chaque système de fichiers monté.",
            "Colonnes Size, Used, Avail, Use%, Mounted on ; 100 % = plein.",
            RIGHT_STANDARD, "Aucun (lecture seule)."),
    Command("chmod", LINUX, "chmod 640 budget.ods",
            "Change les permissions (propriétaire, groupe, autres).",
            "Rien si tout va bien ; « Operation not permitted » si l'on n'est pas propriétaire.",
            "Propriétaire du fichier, ou sudo.",
            "chmod -R 777 ouvre tout à tous ; récursif sur des fichiers système : système cassé."),
    Command("chown", LINUX, "sudo chown anne:compta budget.ods",
            "Change le propriétaire et le groupe d'un fichier ou d'un dossier.",
            "Rien si tout va bien ; visible ensuite avec ls -l.",
            "sudo pour changer le propriétaire.",
            "-R sur le mauvais dossier : des fichiers système changent de propriétaire."),
    Command("apt / dnf", LINUX, "sudo apt update ; sudo apt install vlc",
            "Installe, met à jour et retire des logiciels depuis les dépôts.",
            "Liste des paquets, « Do you want to continue? [Y/n] », puis installation.",
            "sudo (sauf apt search, dnf search).",
            "Retirer un paquet peut retirer ses dépendances ; dépôt ou paquet d'un site inconnu."),
)
COMMANDS_BY_NAME = {c.name: c for c in COMMANDS}


def needs_admin(command: str) -> bool:
    """Vrai si la commande telle qu'écrite modifie le système (convention du cours, d'après
    les droits de la table) ; les formes de lecture restent accessibles à un compte standard."""
    text = command.strip()
    if text.startswith("sudo "):
        return True
    lowered = text.lower()
    if lowered.startswith(("sfc ", "dism ")):
        return True
    if lowered.startswith("ipconfig"):
        return any(opt in lowered for opt in ("/release", "/renew", "/flushdns"))
    if lowered.startswith(("net user", "net localgroup")):
        return any(opt in lowered for opt in ("/add", "/delete", "/active"))
    if lowered.startswith("systemctl "):
        verb = lowered.split()[1]
        return verb in ("start", "stop", "restart", "enable", "disable")
    if lowered.startswith(("apt ", "dnf ")):
        return lowered.split()[1] not in ("search", "list", "show", "info")
    return lowered.startswith("chown ")


# =============================================================================================
# 6. Relevés fictifs (Windows en français, Linux en anglais)
# =============================================================================================

NET_USER_SCREEN: tuple[str, ...] = (
    "C:\\> net user marie",
    "Nom d'utilisateur              marie",
    "Nom complet                    Marie Dubois",
    "Compte : actif                 Oui",
    "Dernier accès                  14/10/2026 08:41",
    "Appartient aux groupes locaux  *Administrateurs",
    "                               *Utilisateurs",
    "Appartient aux groupes globaux *Aucun",
    "La commande s'est terminée correctement.",
)

SFC_DENIED_SCREEN: tuple[str, ...] = (
    "C:\\Users\\paul> sfc /scannow",
    "Vous devez être un administrateur exécutant une",
    "session de console pour pouvoir utiliser",
    "l'utilitaire SFC.",
)

SFC_UNREPAIRED_SCREEN: tuple[str, ...] = (
    "C:\\WINDOWS\\system32> sfc /scannow",
    "Vérification 100% effectuée.",
    "La protection des ressources Windows a trouvé des",
    "fichiers corrompus mais n'a pas pu tous les réparer.",
    "Des détails sont disponibles dans le fichier CBS.Log",
    "windir\\Logs\\CBS\\CBS.log.",
)

SYSTEMCTL_CUPS_SCREEN: tuple[str, ...] = (
    "$ systemctl status cups",
    "○ cups.service - CUPS Scheduler",
    "     Loaded: loaded (/usr/lib/systemd/system/",
    "             cups.service; disabled; preset: enabled)",
    "     Active: inactive (dead)",
    "$ lpstat -p",
    "lpstat: Scheduler is not running.",
)

LS_COMPTA_SCREEN: tuple[str, ...] = (
    "$ id julie",
    "uid=1002(julie) gid=1002(julie) groups=1002(julie),",
    "1005(compta)",
    "$ ls -ld /srv/compta",
    "drwxr-x--- 2 root compta 4096 Oct 12 10:03 /srv/compta",
    "$ touch /srv/compta/note.txt",
    "touch: cannot touch '/srv/compta/note.txt':",
    "Permission denied",
)
COMPTA_DIR_MODE = "drwxr-x---"

DEVICE_ID_SCREEN: tuple[str, ...] = (
    "Gestionnaire de périphériques",
    "v Autres périphériques",
    "    (!) Contrôleur de réseau",
    "",
    "Propriétés → Général → État du périphérique :",
    "  Les pilotes de ce périphérique ne sont pas",
    "  installés. (Code 28)",
    "Propriétés → Détails → ID du matériel :",
    "  PCI\\VEN_14E4&DEV_43A0&SUBSYS_0619106B",
)

# Cas 5 : poste configuré à la main avec une mauvaise passerelle (la box est 192.168.1.1).
CASE5_HOST = Host("ACCUEIL-01", "poste de l'accueil", "192.168.1.30", 24, "192.168.1.254", ("192.168.1.1",),
                  "3C-7C-3F-1A-2B-4D")
CASE5_GATEWAY_OK = "192.168.1.1"
CASE5_IPCONFIG = ("C:\\> ipconfig /all", *ipconfig_all_lines(CASE5_HOST))
CASE5_PING_PRINTER = win_ping_lines("192.168.1.40", (1, 1, 1, 1))
CASE5_PING_GW = win_ping_lines("192.168.1.254", (None, None, None, None))
CASE5_PING_NET = win_ping_lines("203.0.113.10", (14, 13, 14, 15), ttl=56)
CASE5_NSLOOKUP_OK = nslookup_lines("www.exemple.be", "192.168.1.1", NS_OK, "203.0.113.10")

IPCONFIG_FIGURE_SCREEN: tuple[str, ...] = (*CASE5_IPCONFIG, "", *CASE5_PING_GW)

# =============================================================================================
# 7. Procédures illustrées et figures
# =============================================================================================

NETWORK_STEPS: tuple[tuple[str, str], ...] = (
    ("Lire la configuration", "ipconfig /all ou ip a et ip route : adresse, masque, passerelle, DNS."),
    ("Tester la passerelle", "ping de la passerelle : le réseau local fonctionne-t-il ?"),
    ("Tester une adresse Internet", "ping d'une adresse ; tracert pour situer l'arrêt."),
    ("Tester le nom", "nslookup du nom : le serveur DNS répond-il ?"),
    ("Corriger la configuration", "Paramètres → Réseau (DHCP ou valeurs justes) ; jamais au hasard."),
    ("Contrôler", "Nouveau ipconfig /all, ping d'un nom, site ouvert dans le navigateur."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Créer un compte selon le moindre privilège", ACCOUNT_STEPS),
    ("Installer, mettre à jour ou restaurer un pilote", DRIVER_STEPS),
    ("Remettre en route un service arrêté", SERVICE_STEPS),
    ("Contrôler et corriger la configuration réseau", NETWORK_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


ACCOUNT_FIGURE = Figure(
    key="pr10-comptes",
    title="Procédure 1 — Créer un compte selon le moindre privilège",
    alt=_procedure_alt("Création d'un compte utilisateur.", ACCOUNT_STEPS),
    caption=(
        "Chaque personne a son compte, standard par défaut. Les droits d'administration sont "
        "donnés à une personne nommée, pour une raison écrite."
    ),
    svg=step_flow_svg(ACCOUNT_STEPS),
)

DRIVER_FIGURE = Figure(
    key="pr10-pilote",
    title="Procédure 2 — Installer, mettre à jour ou restaurer un pilote",
    alt=_procedure_alt("Intervention sur un pilote Windows.", DRIVER_STEPS),
    caption=(
        "On identifie le périphérique par son ID du matériel avant de chercher un pilote ; le "
        "point de restauration permet de revenir en arrière."
    ),
    svg=step_flow_svg(DRIVER_STEPS),
)

SERVICE_FIGURE = Figure(
    key="pr10-service",
    title="Procédure 3 — Remettre en route un service arrêté",
    alt=_procedure_alt("Remise en route d'un service.", SERVICE_STEPS),
    caption=(
        "Démarrer le service ne suffit pas : on cherche pourquoi il était arrêté et on vérifie "
        "qu'il redémarre avec le système."
    ),
    svg=step_flow_svg(SERVICE_STEPS),
)

NETWORK_FIGURE = Figure(
    key="pr10-reseau",
    title="Procédure 4 — Contrôler et corriger la configuration réseau",
    alt=_procedure_alt("Contrôle de la configuration réseau d'un poste.", NETWORK_STEPS),
    caption=(
        "On teste du plus proche au plus lointain : configuration, passerelle, Internet, puis "
        "nom. Le dépannage réseau complet est traité en PR24."
    ),
    svg=step_flow_svg(NETWORK_STEPS),
)

DEVICE_TREE_FIGURE = Figure(
    key="pr10-peripherique",
    title="Arbre de décision — un périphérique ne fonctionne pas",
    alt=(
        "Arbre de décision en quatre questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(DEVICE_TREE, start=1))
        + f" Si toutes les réponses sont oui : {DEVICE_FINAL}"
    ),
    caption=(
        "On part du matériel (le périphérique est-il vu ?) avant le pilote. Aucun pilote d'un "
        "site inconnu ; un point de restauration avant chaque changement."
    ),
    svg=decision_tree_svg(DEVICE_TREE, DEVICE_FINAL),
)


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte. " + " ; ".join(line.strip() for line in lines if line.strip()) + "."


NET_USER_FIGURE = Figure(
    key="pr10-net-user",
    title="Contrôler un compte avec net user (fictif)",
    alt=_screen_alt(NET_USER_SCREEN),
    caption=(
        "marie est membre des groupes locaux Administrateurs et Utilisateurs : elle peut "
        "administrer le poste après confirmation de l'UAC. Capture fictive."
    ),
    svg=screen_svg(NET_USER_SCREEN, label=FICTIVE_LABEL),
)

DEVICE_ID_FIGURE = Figure(
    key="pr10-id-materiel",
    title="Cas 1 — Périphérique inconnu : état et ID du matériel (fictif)",
    alt=_screen_alt(DEVICE_ID_SCREEN),
    caption=(
        "Code 28 : aucun pilote installé. VEN_14E4 désigne Broadcom, DEV_43A0 le modèle de la "
        "puce (BCM4360) : on cherche le pilote de ce modèle. Capture fictive."
    ),
    svg=screen_svg(DEVICE_ID_SCREEN, label=FICTIVE_LABEL),
)

CUPS_FIGURE = Figure(
    key="pr10-systemctl",
    title="Service d'impression arrêté sous Linux (fictif)",
    alt=_screen_alt(SYSTEMCTL_CUPS_SCREEN),
    caption=(
        "cups est « disabled » (pas lancé au démarrage) et « inactive (dead) » (arrêté) : "
        "sudo systemctl enable --now cups le corrige. Capture fictive."
    ),
    svg=screen_svg(SYSTEMCTL_CUPS_SCREEN, label=FICTIVE_LABEL),
)

IPCONFIG_FIGURE = Figure(
    key="pr10-ipconfig",
    title="Cas 5 — Configuration réseau : ipconfig /all et nslookup (fictif)",
    alt=_screen_alt(IPCONFIG_FIGURE_SCREEN),
    caption=(
        "Configuration manuelle : la passerelle saisie (192.168.1.254) ne répond pas ; la box du "
        "client est 192.168.1.1. Capture fictive."
    ),
    svg=screen_svg(IPCONFIG_FIGURE_SCREEN, label=FICTIVE_LABEL),
)

PR10_FIGURES: tuple[Figure, ...] = (
    ACCOUNT_FIGURE,
    NET_USER_FIGURE,
    PERM_FIGURE,
    DRIVER_FIGURE,
    DEVICE_TREE_FIGURE,
    DEVICE_ID_FIGURE,
    SERVICE_FIGURE,
    CUPS_FIGURE,
    NETWORK_FIGURE,
    IPCONFIG_FIGURE,
)

# =============================================================================================
# 8. Liste de contrôle et rapport
# =============================================================================================

# (point contrôlé, commande ou outil, résultat attendu)
CHECKLIST: tuple[tuple[str, str, str], ...] = (
    ("Comptes", "net user nom ; groups nom", "Un compte par personne ; administrateurs nommés et justifiés"),
    ("Élévation", "Essai d'une installation avec le compte standard", "L'UAC demande un administrateur ; sudo refusé"),
    ("Pilotes", "Gestionnaire de périphériques ; lspci -k", "Aucun point d'exclamation ; « Kernel driver in use »"),
    ("Services", "services.msc ; systemctl --failed", "Services nécessaires en cours d'exécution ; aucun en échec"),
    ("Réseau", "ipconfig /all ; ping d'un nom", "Configuration attendue ; nom résolu, réponses reçues"),
    ("Système", "sfc /scannow ; df -h", "Aucune violation d'intégrité ; espace libre suffisant"),
)

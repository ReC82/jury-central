"""PR23 « Partage de dossiers, imprimantes et permissions » — données de référence, calculs,
relevés de commandes fictifs et schémas SVG (ticket #223).

Tout est construit **depuis des données** de ce module, contrôlées par
`tests/test_ticket223_ampcr_pratique_pr23.py` (qui recalcule indépendamment) :

- chemins UNC (`unc_parts`) ;
- permissions de **partage** et **NTFS**, droit le plus fort des groupes d'un compte dans
  chaque couche, refus (`layer_level`), **héritage** dans l'arborescence (`ntfs_acl`) et
  **combinaison effective** : par le réseau, la plus restrictive des deux couches ; en session
  sur le serveur, NTFS seul (`effective_access`, `limiting_layer`) ; matrice des droits
  effectifs d'un serveur de fichiers de référence (`access_matrix`) ;
- Linux : droits Unix rwx (`mode_string`, `unix_access`), ACL de groupe, partage Samba
  (`samba_level`) et combinaison (`linux_effective`) ;
- imprimantes partagées : modes de partage comparés, dépannage dans l'ordre
  (`PRINT_CHECKS`, `print_checks`, `print_diagnosis`) ;
- dépannage de l'accès à un partage dans l'ordre (`SHARE_CHECKS`, `share_checks`,
  `share_diagnosis`, `first_failure`) et trois procédures illustrées ;
- quatre schémas à compléter servis aussi en fichiers statiques (`STATIC_FIGURES`).

Valeurs de référence : documentation Microsoft (autorisations de partage Lecture, Modifier,
Contrôle total ; autorisations NTFS de base ; un refus explicite l'emporte sur une
autorisation ; une autorisation explicite l'emporte sur un refus hérité ; à travers le réseau,
l'accès effectif est le plus restrictif des deux ensembles ; SMB sur TCP 445 ; règles de pare-feu
« Partage de fichiers et d'imprimantes » ; codes d'erreur `net use` 5, 53, 67, 86, 1219 ;
installation de pilotes d'imprimante réservée aux administrateurs par défaut depuis la mise à
jour d'août 2021, KB5005652), pages de manuel Linux (`chmod`, `ls`, `getfacl`, `smb.conf` :
`valid users`, `read only`, `write list`). Le domaine `ad.dupont.example` (RFC 2606) est celui de
PR22. Messages Windows en français : **captures fictives simplifiées** au format réel, 56
caractères par ligne au plus (lisibles sur mobile).

**Conventions du cours**, signalées dans le texte : réseau 192.168.20.0/24, serveur de fichiers
en .20, serveur Linux en .40, imprimante réseau en .50, box en .254 ; groupes métier préfixés
`G_` ; échelle simplifiée Aucun accès < Lecture < Modification < Contrôle total. Personnes,
postes et entreprises **fictifs**. Chaque schéma porte son information en texte : la couleur
n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr22_figures import (
    DNS_DOMAIN,
    NETBIOS_DOMAIN,
    USERS_DOMAIN,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56
FICTIVE_LABEL = "capture fictive — présentation simplifiée"
_STROKE = "#33415c"
_FILL = "#dbe4f3"
_SOFT = "#f4f6fb"

# =============================================================================================
# 1. Réseau de référence et chemins UNC
# =============================================================================================

NETWORK = "192.168.20.0/24"
SERVER_NAME = "SRV-FICH"
SERVER_IP = "192.168.20.20"
SERVER_FQDN = f"{SERVER_NAME.lower()}.{DNS_DOMAIN}"
LINUX_NAME = "NAS-LIN"
LINUX_IP = "192.168.20.40"
SMB_PORT = 445
SHARE_ROOT = "D:\\Partages"

AUTH_USERS = "Utilisateurs authentifiés"
EVERYONE = "Tout le monde"
LOCAL_ADMINS = "Administrateurs"


def unc(server: str, share: str, *path: str) -> str:
    """Chemin UNC : \\\\serveur\\partage\\chemin (le serveur peut être un nom ou une adresse IP)."""
    return "\\\\" + "\\".join((server, share, *path))


def unc_parts(path: str) -> dict[str, str]:
    """Découpe un chemin UNC en serveur, partage et chemin dans le partage."""
    if not path.startswith("\\\\"):
        raise ValueError(f"Chemin UNC attendu : {path}")
    pieces = path[2:].split("\\")
    if len(pieces) < 2 or not all(pieces[:2]):
        raise ValueError(f"Serveur et partage requis : {path}")
    return {"serveur": pieces[0], "partage": pieces[1], "chemin": "\\".join(pieces[2:])}


UNC_EXAMPLE = unc(SERVER_NAME, "Compta", "2026", "factures.xlsx")
UNC_EXAMPLE_IP = unc(SERVER_IP, "Compta", "2026", "factures.xlsx")
DRIVE_LETTER = "Z:"

# =============================================================================================
# 2. Permissions : partage, NTFS, héritage, combinaison
# =============================================================================================

LEVEL_NONE = "Aucun accès"
LEVEL_READ = "Lecture"
LEVEL_MODIFY = "Modification"
LEVEL_FULL = "Contrôle total"
LEVELS = (LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY, LEVEL_FULL)
ACCESS_LEVELS = (LEVEL_NONE, LEVEL_READ, LEVEL_MODIFY)  # catégories des matrices d'exercices

# Ce que permet chaque niveau (chacun contient le précédent).
LEVEL_ABILITIES: tuple[tuple[str, str], ...] = (
    (LEVEL_READ, "ouvrir et copier les fichiers, lister le dossier, lancer un programme"),
    (LEVEL_MODIFY, "en plus : créer, enregistrer, renommer et supprimer fichiers et sous-dossiers"),
    (LEVEL_FULL, "en plus : changer les autorisations et prendre possession"),
)

# Noms des autorisations dans les fenêtres Windows (français) → niveau de l'échelle du cours.
SHARE_RIGHTS: dict[str, str] = {"Lecture": LEVEL_READ, "Modifier": LEVEL_MODIFY, "Contrôle total": LEVEL_FULL}
NTFS_RIGHTS: dict[str, str] = {
    "Lecture": LEVEL_READ,
    "Lecture et exécution": LEVEL_READ,
    "Modification": LEVEL_MODIFY,
    "Contrôle total": LEVEL_FULL,
}
# Abréviations de icacls : RX (lecture et exécution), M (modification), F (contrôle total).
ICACLS_CODES: dict[str, str] = {"Lecture et exécution": "RX", "Lecture": "R", "Modification": "M",
                                "Contrôle total": "F"}


def _rank(level: str) -> int:
    return LEVELS.index(level)


def weakest(*levels: str) -> str:
    return min(levels, key=_rank)


@dataclass(frozen=True)
class Ace:
    """Entrée d'une liste d'autorisations : un compte ou groupe, un droit, autoriser ou refuser
    (un refus est ici toujours « Refuser : Contrôle total »), hérité ou posé sur l'objet."""
    principal: str
    right: str
    deny: bool = False
    inherited: bool = False


def layer_level(entries: tuple[Ace, ...], groups: tuple[str, ...], *, rights: dict[str, str] = NTFS_RIGHTS) -> str:
    """Droit obtenu dans une couche (partage ou NTFS) par un compte membre de `groups` :
    les autorisations de ses groupes se cumulent (la plus forte compte) ; un refus explicite
    l'emporte sur toute autorisation ; un refus hérité ne bat pas une autorisation explicite."""
    mine = [e for e in entries if e.principal in groups]
    if any(e.deny and not e.inherited for e in mine):
        return LEVEL_NONE
    explicit = [rights[e.right] for e in mine if not e.deny and not e.inherited]
    if any(e.deny and e.inherited for e in mine):
        return max(explicit, key=_rank, default=LEVEL_NONE)
    allowed = [rights[e.right] for e in mine if not e.deny]
    return max(allowed, key=_rank, default=LEVEL_NONE)


@dataclass(frozen=True)
class Folder:
    path: str
    entries: tuple[Ace, ...]
    inherit: bool = True  # False : héritage désactivé (entrées copiées puis modifiées)

    @property
    def parent(self) -> str | None:
        return self.path.rsplit("\\", 1)[0] if self.path.count("\\") > 1 else None

    @property
    def name(self) -> str:
        return self.path.rsplit("\\", 1)[-1]


@dataclass(frozen=True)
class Share:
    name: str
    path: str
    entries: tuple[Ace, ...]


@dataclass(frozen=True)
class Account:
    login: str
    person: str
    groups: tuple[str, ...] = (USERS_DOMAIN,)

    def all_groups(self) -> tuple[str, ...]:
        """Groupes du compte plus les identités que Windows ajoute à toute session ouverte
        avec un compte et un mot de passe."""
        return (self.login, *self.groups, AUTH_USERS, EVERYONE)


def _a(principal: str, right: str, **kw) -> Ace:
    return Ace(principal, right, **kw)


# Serveur de fichiers de référence (SRV-FICH, domaine de PR22).
NTFS_TREE: dict[str, Folder] = {
    f.path: f
    for f in (
        Folder(SHARE_ROOT, (_a(LOCAL_ADMINS, "Contrôle total"),), inherit=False),
        Folder(f"{SHARE_ROOT}\\Commun", (_a(USERS_DOMAIN, "Modification"),)),
        Folder(f"{SHARE_ROOT}\\Compta", (_a("G_Compta", "Modification"), _a("G_Direction", "Lecture et exécution"))),
        Folder(f"{SHARE_ROOT}\\Compta\\Factures", ()),
        Folder(f"{SHARE_ROOT}\\Compta\\Paie", (_a(LOCAL_ADMINS, "Contrôle total"), _a("G_Direction", "Modification")),
               inherit=False),
        Folder(f"{SHARE_ROOT}\\Direction", (_a("G_Direction", "Modification"),)),
        Folder(f"{SHARE_ROOT}\\Archives", (_a(USERS_DOMAIN, "Lecture et exécution"), _a("G_Compta", "Modification"))),
    )
}

SHARES: dict[str, Share] = {
    s.name: s
    for s in (
        Share("Commun", f"{SHARE_ROOT}\\Commun", (_a(AUTH_USERS, "Modifier"),)),
        Share("Compta", f"{SHARE_ROOT}\\Compta", (_a(AUTH_USERS, "Modifier"),)),
        Share("Direction", f"{SHARE_ROOT}\\Direction", (_a("G_Direction", "Modifier"),)),
        Share("Archives", f"{SHARE_ROOT}\\Archives", (_a(AUTH_USERS, "Lecture"),)),
    )
}


def ntfs_acl(path: str, tree: dict[str, Folder] = NTFS_TREE) -> tuple[Ace, ...]:
    """Entrées NTFS d'un dossier : les siennes, puis celles héritées du parent (marquées
    « hérité »), sauf si l'héritage est désactivé."""
    folder = tree[path]
    own = tuple(Ace(e.principal, e.right, e.deny, inherited=False) for e in folder.entries)
    if not folder.inherit or folder.parent is None or folder.parent not in tree:
        return own
    inherited = tuple(Ace(e.principal, e.right, e.deny, inherited=True) for e in ntfs_acl(folder.parent, tree))
    return own + inherited


def share_for(path: str, shares: dict[str, Share] = SHARES) -> Share:
    """Partage par lequel on atteint `path` (le dossier partagé ou un de ses sous-dossiers)."""
    for share in shares.values():
        if path == share.path or path.startswith(share.path + "\\"):
            return share
    raise KeyError(path)


def share_level(account: Account, path: str, shares: dict[str, Share] = SHARES) -> str:
    return layer_level(share_for(path, shares).entries, account.all_groups(), rights=SHARE_RIGHTS)


def ntfs_level(account: Account, path: str, tree: dict[str, Folder] = NTFS_TREE) -> str:
    return layer_level(ntfs_acl(path, tree), account.all_groups())


def effective_access(account: Account, path: str, *, remote: bool = True, tree: dict[str, Folder] = NTFS_TREE,
                     shares: dict[str, Share] = SHARES) -> str:
    """Accès effectif : par le réseau, le plus restrictif du partage et de NTFS ; en session
    ouverte sur le serveur lui-même, NTFS seul (le partage n'intervient pas)."""
    ntfs = ntfs_level(account, path, tree)
    if not remote:
        return ntfs
    return weakest(share_level(account, path, shares), ntfs)


LIMIT_SHARE = "le partage"
LIMIT_NTFS = "NTFS"
LIMIT_BOTH = "les deux (égaux)"


def limiting_layer(account: Account, path: str, *, tree: dict[str, Folder] = NTFS_TREE,
                   shares: dict[str, Share] = SHARES) -> str:
    share, ntfs = share_level(account, path, shares), ntfs_level(account, path, tree)
    if _rank(share) < _rank(ntfs):
        return LIMIT_SHARE
    if _rank(ntfs) < _rank(share):
        return LIMIT_NTFS
    return LIMIT_BOTH


JULIE = Account("jmartin", "Julie Martin (comptable)", (USERS_DOMAIN, "G_Compta"))
CLAIRE = Account("cdupont", "Claire Dupont (directrice)", (USERS_DOMAIN, "G_Direction"))
SAM = Account("sroux", "Sam Roux (secrétariat)", (USERS_DOMAIN, "G_Secretariat"))
MATRIX_ACCOUNTS = (JULIE, CLAIRE, SAM)
MATRIX_PATHS: tuple[str, ...] = (
    f"{SHARE_ROOT}\\Commun",
    f"{SHARE_ROOT}\\Compta",
    f"{SHARE_ROOT}\\Compta\\Factures",
    f"{SHARE_ROOT}\\Compta\\Paie",
    f"{SHARE_ROOT}\\Direction",
    f"{SHARE_ROOT}\\Archives",
)


def short_path(path: str) -> str:
    return path[len(SHARE_ROOT) + 1:]


def access_matrix(accounts: tuple[Account, ...] = MATRIX_ACCOUNTS, paths: tuple[str, ...] = MATRIX_PATHS, *,
                  remote: bool = True) -> dict[str, dict[str, str]]:
    return {a.login: {short_path(p): effective_access(a, p, remote=remote) for p in paths} for a in accounts}


ACCESS_MATRIX = access_matrix()

COMPARISON: tuple[tuple[str, str, str], ...] = (
    ("Où on les règle", "Propriétés → Partage → Partage avancé → Autorisations",
     "Propriétés → onglet Sécurité"),
    ("S'appliquent", "Seulement à l'accès par le réseau", "À l'accès local et par le réseau"),
    ("Portée", "Le partage entier (tous ses sous-dossiers)", "Chaque dossier et chaque fichier, avec héritage"),
    ("Niveaux", "Lecture, Modifier, Contrôle total",
     "Lecture, Lecture et exécution, Écriture, Modification, Contrôle total (+ spéciales)"),
    ("Système de fichiers", "Tous (même FAT32 ou clé USB)", "NTFS seulement"),
)

# =============================================================================================
# 3. Linux : droits Unix, ACL, Samba
# =============================================================================================


def mode_string(mode: int, *, directory: bool = True, acl: bool = False) -> str:
    """Affichage de `ls -l` : type, puis rwx du propriétaire, du groupe et des autres ;
    le bit setgid (2000) s'affiche « s » à la place du x du groupe (« S » sans x)."""
    out = "d" if directory else "-"
    for shift in (6, 3, 0):
        bits = (mode >> shift) & 7
        out += ("r" if bits & 4 else "-") + ("w" if bits & 2 else "-") + ("x" if bits & 1 else "-")
    if mode & 0o2000:
        out = out[:6] + ("s" if out[6] == "x" else "S") + out[7:]
    return out + ("+" if acl else "")


def _bits(mode: int, shift: int) -> str:
    bits = (mode >> shift) & 7
    return ("r" if bits & 4 else "-") + ("w" if bits & 2 else "-") + ("x" if bits & 1 else "-")


def _union(*perms: str) -> str:
    return "".join(c if any(p[i] == c for p in perms) else "-" for i, c in enumerate("rwx"))


def unix_access(mode: int, owner: str, group: str, user: str, user_groups: tuple[str, ...],
                acl_groups: dict[str, str] | None = None) -> str:
    """Droits Unix d'un utilisateur sur un fichier ou dossier : propriétaire, sinon classe
    groupe (groupe propriétaire et groupes nommés de l'ACL, masque supposé rwx), sinon autres.
    Les classes ne se cumulent pas : le propriétaire n'a que les droits du propriétaire."""
    acl_groups = acl_groups or {}
    if user == owner:
        return _bits(mode, 6)
    matching = [_bits(mode, 3)] if group in user_groups else []
    matching += [perm for g, perm in acl_groups.items() if g in user_groups]
    if matching:
        return _union(*matching)
    return _bits(mode, 0)


def dir_level(perms: str) -> str:
    """Accès à un dossier partagé : r et x pour lister et ouvrir ; w et x en plus pour créer,
    modifier et supprimer (w sans x ne sert à rien)."""
    if "r" in perms and "x" in perms:
        return LEVEL_MODIFY if "w" in perms else LEVEL_READ
    return LEVEL_NONE


@dataclass(frozen=True)
class SambaShare:
    name: str
    path: str
    valid_users: tuple[str, ...]  # groupes autorisés (@groupe dans smb.conf)
    read_only: bool = True
    write_list: tuple[str, ...] = ()


def samba_level(share: SambaShare, user_groups: tuple[str, ...]) -> str:
    if share.valid_users and not set(share.valid_users) & set(user_groups):
        return LEVEL_NONE
    if not share.read_only or set(share.write_list) & set(user_groups):
        return LEVEL_MODIFY
    return LEVEL_READ


@dataclass(frozen=True)
class LinuxUser:
    login: str
    groups: tuple[str, ...]


LX_DIR = "/srv/partages/compta"
LX_MODE = 0o2770
LX_OWNER, LX_GROUP = "root", "compta"
LX_ACL: dict[str, str] = {"direction": "r-x"}
LX_SHARE = SambaShare("compta", LX_DIR, ("compta", "direction"), read_only=True, write_list=("compta",))
LX_USERS: tuple[LinuxUser, ...] = (
    LinuxUser("marie", ("compta",)),
    LinuxUser("paul", ("direction",)),
    LinuxUser("sam", ("secretariat",)),
)


def linux_effective(user: LinuxUser, *, mode: int = LX_MODE, owner: str = LX_OWNER, group: str = LX_GROUP,
                    acl: dict[str, str] | None = None, share: SambaShare = LX_SHARE) -> str:
    """Accès par Samba : le plus restrictif de la règle du partage et des droits Unix."""
    perms = unix_access(mode, owner, group, user.login, user.groups, LX_ACL if acl is None else acl)
    return weakest(samba_level(share, user.groups), dir_level(perms))


SMB_CONF_LINES: tuple[str, ...] = (
    f"[{LX_SHARE.name}]",
    f"   path = {LX_SHARE.path}",
    "   valid users = " + " ".join(f"@{g}" for g in LX_SHARE.valid_users),
    "   read only = " + ("yes" if LX_SHARE.read_only else "no"),
    "   write list = " + " ".join(f"@{g}" for g in LX_SHARE.write_list),
)


def ls_lines(mode: int = LX_MODE, *, owner: str = LX_OWNER, group: str = LX_GROUP, acl: bool = True,
             name: str = "compta") -> tuple[str, ...]:
    return (
        "admin@nas-lin:/srv/partages$ ls -ld " + name,
        f"{mode_string(mode, acl=acl)} 2 {owner} {group} 4096 oct. 27 09:12 {name}",
    )


def getfacl_lines(mode: int = LX_MODE, acl: dict[str, str] | None = None) -> tuple[str, ...]:
    acl = LX_ACL if acl is None else acl
    return (
        "admin@nas-lin:/srv/partages$ getfacl compta",
        "# file: compta",
        f"# owner: {LX_OWNER}",
        f"# group: {LX_GROUP}",
        *(("# flags: -s-",) if mode & 0o2000 else ()),
        f"user::{_bits(mode, 6)}",
        f"group::{_bits(mode, 3)}",
        *(f"group:{g}:{p}" for g, p in acl.items()),
        "mask::rwx",
        f"other::{_bits(mode, 0)}",
    )


# =============================================================================================
# 4. Imprimantes partagées
# =============================================================================================

PRINT_HOST = "PC-ACCUEIL"
PRINT_HOST_IP = "192.168.20.31"
USB_PRINTER = "Laser-Accueil"
NET_PRINTER = "IMP-COMPTA"
NET_PRINTER_IP = "192.168.20.50"
RAW_PORT, IPP_PORT = 9100, 631

PRINT_MODES: tuple[tuple[str, str, str, str], ...] = (
    ("Imprimante USB partagée par un poste", unc(PRINT_HOST, USB_PRINTER),
     "Le poste hôte doit rester allumé ; il gère la file d'attente.",
     "Petit bureau, une imprimante de plus sans réseau."),
    ("Imprimante réseau partagée par un serveur d'impression", unc(SERVER_NAME, NET_PRINTER),
     "Une seule file d'attente et un seul pilote à gérer ; droits par groupes.",
     "Plusieurs postes, gestion centralisée (domaine)."),
    ("Imprimante réseau ajoutée par son adresse IP sur chaque poste", f"{NET_PRINTER_IP} (port {RAW_PORT} ou IPP {IPP_PORT})",
     "Pas d'hôte intermédiaire ; une file et un pilote sur chaque poste.",
     "Quelques postes, imprimante à adresse fixe."),
)

P_HOST = "Hôte : le poste ou serveur qui partage est éteint ou injoignable"
P_DEVICE = "Imprimante : éteinte, en erreur ou adresse IP changée"
P_QUEUE = "File d'attente : document bloqué ou spouleur arrêté"
P_DRIVER = "Pilote : absent, inadapté ou installation refusée"
P_RIGHT = "Droit : le compte n'a pas l'autorisation Imprimer"
P_OK = "Impression réussie"
PRINT_DIAGNOSES = (P_HOST, P_DEVICE, P_QUEUE, P_DRIVER, P_RIGHT)

PRINT_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("hote", "Le poste ou serveur qui partage est allumé et répond", P_HOST),
    ("imprimante", "L'imprimante est prête, à l'adresse configurée sur le port", P_DEVICE),
    ("file", "File d'attente vide de document bloqué, spouleur démarré", P_QUEUE),
    ("pilote", "Pilote du bon modèle installé sur le poste", P_DRIVER),
    ("droit", "Le compte a l'autorisation Imprimer", P_RIGHT),
)
PRINT_KEYS = tuple(k for k, _w, _d in PRINT_CHECKS)


@dataclass(frozen=True)
class PrintState:
    host_up: bool = True  # poste ou serveur d'impression (sans objet en impression directe)
    device_ready: bool = True  # allumée, papier, pas d'erreur
    device_ip: str = NET_PRINTER_IP  # adresse réelle de l'imprimante
    port_ip: str = NET_PRINTER_IP  # adresse configurée sur le port d'impression
    queue_stuck: bool = False
    spooler_running: bool = True
    driver_ok: bool = True
    print_right: bool = True


def print_checks(state: PrintState) -> dict[str, bool]:
    return {
        "hote": state.host_up,
        "imprimante": state.device_ready and state.device_ip == state.port_ip,
        "file": state.spooler_running and not state.queue_stuck,
        "pilote": state.driver_ok,
        "droit": state.print_right,
    }


def print_diagnosis(results: dict[str, bool]) -> str:
    for key, _what, diagnosis in PRINT_CHECKS:
        if not results[key]:
            return diagnosis
    return P_OK


# =============================================================================================
# 5. Accès à un partage : diagnostic dans l'ordre
# =============================================================================================

S_NET = "Réseau : le serveur ne répond pas sur son adresse IP"
S_NAME = "Nom : le nom du serveur n'est pas résolu"
S_SMB = "Partage de fichiers bloqué : pare-feu, profil Public ou service arrêté"
S_SHARE = "Partage : nom de partage inexistant ou mal écrit"
S_AUTH = "Identification : compte ou mot de passe refusé"
S_RIGHTS = "Permissions : partage ou NTFS insuffisantes"
S_OK = "Accès conforme à la matrice des droits"
SHARE_DIAGNOSES = (S_NET, S_NAME, S_SMB, S_SHARE, S_AUTH, S_RIGHTS)

SHARE_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("ip", f"Le serveur répond par son adresse IP ({SERVER_IP})", S_NET),
    ("nom", f"Le nom {SERVER_NAME} donne la bonne adresse", S_NAME),
    ("smb", f"Le port TCP {SMB_PORT} (partage de fichiers) répond", S_SMB),
    ("partage", f"net view \\\\{SERVER_NAME} liste le partage demandé", S_SHARE),
    ("compte", "Le compte et le mot de passe sont acceptés", S_AUTH),
    ("droits", "L'accès effectif (partage + NTFS) suffit", S_RIGHTS),
)
SHARE_KEYS = tuple(k for k, _w, _d in SHARE_CHECKS)


@dataclass(frozen=True)
class AccessState:
    server_up: bool = True
    name_ok: bool = True
    smb_open: bool = True  # pare-feu, profil réseau, service « Serveur »
    share_exists: bool = True
    credentials_ok: bool = True
    effective: str = LEVEL_MODIFY
    needed: str = LEVEL_READ


def share_checks(state: AccessState) -> dict[str, bool]:
    return {
        "ip": state.server_up,
        "nom": state.name_ok,
        "smb": state.smb_open,
        "partage": state.share_exists,
        "compte": state.credentials_ok,
        "droits": _rank(state.effective) >= _rank(state.needed),
    }


def share_diagnosis(results: dict[str, bool]) -> str:
    """Le premier contrôle en échec désigne la piste."""
    for key, _what, diagnosis in SHARE_CHECKS:
        if not results[key]:
            return diagnosis
    return S_OK


def first_failure(failed: str, keys: tuple[str, ...] = SHARE_KEYS) -> dict[str, bool]:
    index = keys.index(failed)
    return {k: i < index for i, k in enumerate(keys)}


# Messages de `net use` / de l'Explorateur (français) et piste.
SHARE_MESSAGES: tuple[tuple[str, str], ...] = (
    ("Erreur système 53. Le chemin réseau n'a pas été trouvé. (0x80070035 dans l'Explorateur)",
     "Nom, réseau ou pare-feu : essayer par l'adresse IP, puis le port 445"),
    ("Erreur système 67. Le nom réseau est introuvable.", "Nom du partage mal écrit ou partage supprimé"),
    ("Erreur système 86. Le mot de passe réseau spécifié est incorrect.", "Identification : compte du serveur et mot de passe"),
    ("Erreur système 1219. Les connexions multiples à un serveur … par le même utilisateur, en utilisant plus d'un nom d'utilisateur, ne sont pas autorisées.",
     "Identification : une connexion existe déjà avec un autre compte (net use, cmdkey)"),
    ("Erreur système 5. Accès refusé.", "Permissions : le serveur a répondu et refuse ; à la connexion (net use), le partage ; à l'ouverture du dossier, NTFS"),
)

# =============================================================================================
# 6. Procédures
# =============================================================================================

SHARE_STEPS: tuple[tuple[str, str], ...] = (
    ("Préparer le dossier", f"Sur un volume NTFS du serveur, ex. {SHARE_ROOT}\\Compta, hors du dossier système."),
    ("Créer les groupes", "Un groupe par besoin (G_Compta…), les comptes dedans."),
    ("Régler NTFS", "Onglet Sécurité : droits aux groupes, héritage vérifié, retirer Tout le monde."),
    ("Partager", "Partage avancé : nom du partage, autorisations du partage aux groupes ou utilisateurs authentifiés."),
    ("Ouvrir le pare-feu", f"Profil réseau Privé ou Domaine, « Partage de fichiers et d'imprimantes » (TCP {SMB_PORT})."),
    ("Tester depuis un poste", f"\\\\{SERVER_NAME}\\Compta avec un compte de chaque groupe : accès et refus attendus."),
    ("Consigner", "Matrice des droits, chemin UNC et lecteur réseau remis au client."),
)

PRINTER_STEPS: tuple[tuple[str, str], ...] = (
    ("Installer l'imprimante sur l'hôte", "Pilote du fabricant, page de test locale réussie."),
    ("Fixer son adresse", f"Imprimante réseau : adresse fixe ou réservation DHCP ({NET_PRINTER_IP})."),
    ("Partager", "Propriétés de l'imprimante → Partage : « Partager cette imprimante », nom court sans espace."),
    ("Régler les droits", "Onglet Sécurité : Imprimer pour les groupes concernés ; gestion pour l'administrateur."),
    ("Ouvrir le pare-feu", "« Partage de fichiers et d'imprimantes » sur le profil Privé ou Domaine."),
    ("Connecter les postes", f"\\\\{SERVER_NAME}\\{NET_PRINTER} ; pilote installé par un administrateur si demandé."),
    ("Tester et consigner", "Page de test depuis chaque poste ; chemin, adresse et pilote notés."),
)

TROUBLE_STEPS: tuple[tuple[str, str], ...] = (
    ("Lire le message exact", "Noter le code (5, 53, 67, 86…) ; un ou plusieurs postes, un ou plusieurs comptes ?"),
    ("Adresse IP", f"ping {SERVER_IP} ; essayer \\\\{SERVER_IP}\\partage."),
    ("Nom", f"ping {SERVER_NAME}, nslookup {SERVER_NAME} : bonne adresse ?"),
    ("Partage de fichiers", f"Test-NetConnection {SERVER_NAME} -Port {SMB_PORT} ; pare-feu, profil réseau."),
    ("Nom du partage", f"net view \\\\{SERVER_NAME} : le partage existe-t-il ?"),
    ("Compte", "Compte avec mot de passe, connexion existante (net use, cmdkey /list)."),
    ("Permissions", "Partage + NTFS : la plus restrictive ; groupes de la session (whoami /groups)."),
    ("Consigner", "Cause, correction, test de lecture et d'écriture réussi."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Partager un dossier sur un serveur Windows", SHARE_STEPS),
    ("Partager une imprimante", PRINTER_STEPS),
    ("Dépanner l'accès à un partage", TROUBLE_STEPS),
)

# =============================================================================================
# 7. Relevés fictifs (56 caractères par ligne au plus)
# =============================================================================================

NET_USE_ERRORS: dict[int, str] = {
    5: "Accès refusé.",
    53: "Le chemin réseau n'a pas été trouvé.",
    67: "Le nom réseau est introuvable.",
    86: "Le mot de passe réseau spécifié est incorrect.",
}


def net_use_lines(path: str, *, error: int | None = None, drive: str = DRIVE_LETTER) -> tuple[str, ...]:
    head = (f"C:\\> net use {drive} {path}",)
    if error is None:
        return (*head, "La commande s'est terminée correctement.")
    return (*head, f"Erreur système {error}.", "", NET_USE_ERRORS[error])


def dir_lines(path: str, *, denied: bool) -> tuple[str, ...]:
    """Ouverture d'un dossier partagé : la connexion au partage ne vérifie que les autorisations
    du partage ; NTFS refuse à l'ouverture du dossier (« Accès refusé. »)."""
    head = f"C:\\> dir {path}"
    if denied:
        return (head, "Accès refusé.")
    return (head, f" Répertoire de {path}", "27/10/2026  09:12    <DIR>          2026")


def ping_lines(target: str, *, ip: str | None, replies: bool = True) -> tuple[str, ...]:
    head = f"C:\\> ping -n 2 {target}"
    if ip is None:
        return (head, "La requête Ping n'a pas pu trouver l'hôte", f"{target}. Vérifiez le nom et réessayez.")
    if not replies:
        return (head, f"Envoi d'une requête 'Ping' {ip}", "Délai d'attente de la demande dépassé.",
                "Délai d'attente de la demande dépassé.")
    return (head, *(f"Réponse de {ip} : octets=32 temps<1ms TTL=128" for _ in range(2)))


def port_test_lines(target: str, ip: str, *, open_: bool, port: int = SMB_PORT) -> tuple[str, ...]:
    return (
        f"PS> Test-NetConnection {target} -Port {port}",
        f"ComputerName     : {target}",
        f"RemoteAddress    : {ip}",
        f"RemotePort       : {port}",
        f"TcpTestSucceeded : {open_}",
    )


def net_view_lines(server: str, shares: tuple[str, ...]) -> tuple[str, ...]:
    return (
        f"C:\\> net view \\\\{server}",
        f"Ressources partagées de \\\\{server}",
        "",
        "Nom du partage  Type",
        "-" * 30,
        *(f"{name:<16}Disque" for name in shares),
        "La commande s'est terminée correctement.",
    )


def icacls_lines(path: str, tree: dict[str, Folder] = NTFS_TREE) -> tuple[str, ...]:
    """`icacls` simplifié : (I) = hérité ; (OI)(CI) = s'applique aux fichiers et sous-dossiers ;
    F, M, RX = contrôle total, modification, lecture et exécution."""

    def who(principal: str) -> str:
        if principal == LOCAL_ADMINS:
            return f"BUILTIN\\{principal}"
        if principal in (AUTH_USERS, EVERYONE):
            return principal
        return f"{NETBIOS_DOMAIN}\\{principal}"

    lines = [f"C:\\> icacls {path}", path]
    for ace in ntfs_acl(path, tree):
        if ace.deny:
            raise ValueError("Les refus sont présentés dans un tableau de l'onglet Sécurité, pas en icacls.")
        flags = ("(I)" if ace.inherited else "") + "(OI)(CI)"
        lines.append(f"  {who(ace.principal)}:{flags}({ICACLS_CODES[ace.right]})")
    lines.append("1 fichiers correctement traités")
    return tuple(lines)


def net_share_lines(share: Share) -> tuple[str, ...]:
    perms = {"Lecture": "READ", "Modifier": "CHANGE", "Contrôle total": "FULL"}

    def who(principal: str) -> str:
        if principal == AUTH_USERS:
            return f"AUTORITE NT\\{principal}"
        return principal if principal == EVERYONE else f"{NETBIOS_DOMAIN}\\{principal}"

    return (
        f"C:\\> net share {share.name}",
        f"Nom du partage        {share.name}",
        f"Chemin                {share.path}",
        "Autorisation",
        *(f"  {who(e.principal)}, {perms[e.right]}" for e in share.entries),
        "La commande s'est terminée correctement.",
    )


def get_printer_lines(status: str, *, port_ip: str = NET_PRINTER_IP) -> tuple[str, ...]:
    return (
        f"PS> Get-Printer {NET_PRINTER} | fl Name,PortName,",
        ">>   PrinterStatus",
        f"Name          : {NET_PRINTER}",
        f"PortName      : IP_{port_ip}",
        f"PrinterStatus : {status}",
    )


SPOOLER_LINES: tuple[str, ...] = (
    "C:\\> net stop spooler",
    "Le service Spouleur d'impression s'arrête.",
    "Le service Spouleur d'impression a été arrêté.",
    "C:\\> del /q C:\\Windows\\System32\\spool\\PRINTERS\\*",
    "C:\\> net start spooler",
    "Le service Spouleur d'impression a démarré.",
)

# =============================================================================================
# 8. Schémas SVG
# =============================================================================================


def _box(x: float, y: float, w: float, lines: list[str], *, key: str = "", dashed: bool = False,
         fill: str = _FILL) -> str:
    h = 12 + 15 * len(lines)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    data = f' data-node="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{_STROKE}" '
            f'stroke-width="1.5"{dash}/>'
            + _text_lines(int(x) + 8, int(y) + 17, lines[:1], size=12, weight="700")
            + _text_lines(int(x) + 8, int(y) + 32, lines[1:], size=10.5, step=15))


def _notes(y: int, text: str, parts: list[str], width: int = 380) -> int:
    lines = _wrap(text, 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return y + 13 * len(lines)


UNC_ROWS: tuple[tuple[str, str], ...] = (
    ("serveur", "Serveur (nom ou adresse IP)"),
    ("partage", "Nom du partage"),
    ("chemin", "Chemin dans le partage"),
)


def unc_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Anatomie d'un chemin UNC : \\\\ + serveur + partage + chemin, avec la forme par adresse
    IP et la lettre de lecteur. `blanks` (« serveur », « partage », « chemin », « ip »,
    « lecteur ») masque une valeur."""
    blanks = blanks or {}
    parts_of = unc_parts(UNC_EXAMPLE)

    def val(key: str, text: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else text

    width = 380
    parts = [_text_lines(width // 2, 16, ["Lire un chemin UNC"], size=12.5, weight="700", anchor="middle")]
    full = "\\\\" + "\\".join(val(k, parts_of[k]) for k, _l in UNC_ROWS)
    parts.append(f'<rect x="4" y="26" width="372" height="28" rx="5" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(12, 45, [full], size=12.5, weight="700"))
    y = 66
    parts.append(_box(4, y, 372, ["\\\\ (deux barres obliques inverses)", "début d'un chemin réseau Windows"], fill=_SOFT))
    y += 48
    for key, label in UNC_ROWS:
        hidden = key in blanks
        parts.append(_box(4, y, 372, [label, val(key, parts_of[key])], key="" if hidden else key, dashed=hidden,
                          fill="#ffffff" if hidden else _FILL))
        y += 48
    y += 4
    parts.append(_box(4, y, 372, ["Même ressource par l'adresse IP", val("ip", UNC_EXAMPLE_IP)],
                      key="" if "ip" in blanks else "ip", dashed="ip" in blanks, fill="#fff3c4"))
    y += 48
    parts.append(_box(4, y, 372, ["Lecteur réseau (net use)", f"{val('lecteur', DRIVE_LETTER)} = {unc(SERVER_NAME, 'Compta')}"],
                      key="" if "lecteur" in blanks else "lecteur", dashed="lecteur" in blanks, fill="#e9f5ec"))
    y += 62
    y = _notes(y, "Si le chemin par l'adresse IP fonctionne et pas celui par le nom, la panne est la "
               "résolution du nom (DNS), pas le partage ni les droits.", parts)
    return _svg(width, y, parts)


def layers_svg(account: Account, path: str, *, blanks: dict[str, str] | None = None) -> str:
    """Les deux barrières : autorisations du partage puis NTFS ; accès effectif par le réseau
    (la plus restrictive) et accès local (NTFS seul). `blanks` (« partage », « ntfs »,
    « reseau », « local ») masque une valeur."""
    blanks = blanks or {}
    share = share_for(path)
    values = {
        "partage": share_level(account, path),
        "ntfs": ntfs_level(account, path),
        "reseau": effective_access(account, path),
        "local": effective_access(account, path, remote=False),
    }

    def val(key: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else values[key]

    width = 380
    parts = [_text_lines(width // 2, 16, [f"Deux barrières : {account.login} → {short_path(path)}"], size=12.5,
                         weight="700", anchor="middle")]
    groups = ", ".join(g for g in account.groups)
    parts.append(_box(4, 28, 372, [f"Compte {NETBIOS_DOMAIN}\\{account.login}", f"groupes : {groups}"], fill=_SOFT))
    share_rule = "; ".join(f"{e.principal} : {e.right}" for e in share.entries)
    ntfs_rule = "; ".join(f"{e.principal} : {e.right}" + (" (hérité)" if e.inherited else "")
                          for e in ntfs_acl(path) if e.principal != LOCAL_ADMINS)
    y = 82
    parts.append(f'<path d="M190 {y - 6} V{y}" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_box(4, y, 372, [f"1. Partage \\\\{SERVER_NAME}\\{share.name}", *_wrap(share_rule, 56),
                                  f"→ droit du compte : {val('partage')}"],
                      key="" if "partage" in blanks else "partage", dashed="partage" in blanks))
    y += 12 + 15 * (2 + len(_wrap(share_rule, 56))) + 12
    parts.append(f'<path d="M190 {y - 12} V{y}" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_box(4, y, 372, [f"2. NTFS (onglet Sécurité) de {short_path(path)}", *_wrap(ntfs_rule, 56),
                                  f"→ droit du compte : {val('ntfs')}"],
                      key="" if "ntfs" in blanks else "ntfs", dashed="ntfs" in blanks))
    y += 12 + 15 * (2 + len(_wrap(ntfs_rule, 56))) + 12
    parts.append(_box(4, y, 182, ["Par le réseau", "la plus restrictive :", val("reseau")],
                      key="" if "reseau" in blanks else "reseau", dashed="reseau" in blanks, fill="#e9f5ec"))
    parts.append(_box(194, y, 182, ["Session sur le serveur", "NTFS seul :", val("local")],
                      key="" if "local" in blanks else "local", dashed="local" in blanks, fill="#fff3c4"))
    y += 12 + 15 * 3 + 20
    y = _notes(y, "Dans chaque barrière, les droits des groupes du compte se cumulent (le plus fort compte) ; "
               "un refus explicite l'emporte. Entre les deux barrières, c'est le plus faible qui gagne.", parts)
    return _svg(width, y, parts)


def matrix_svg(matrix: dict[str, dict[str, str]], *, blanks: dict[tuple[str, str], str] | None = None,
               title: str = "Matrice des droits effectifs (par le réseau)") -> str:
    """Tableau comptes × dossiers ; chaque case porte le niveau écrit en toutes lettres (la
    couleur n'est qu'un repère). `blanks` ((compte, dossier) → numéro) masque une case."""
    blanks = blanks or {}
    logins = list(matrix)
    folders = list(next(iter(matrix.values())))
    width, left, col_w, row_h, top = 380, 116, 88, 26, 50
    fills = {LEVEL_NONE: "#fbecec", LEVEL_READ: "#fff3c4", LEVEL_MODIFY: "#e9f5ec", LEVEL_FULL: "#dbe4f3"}
    parts = [_text_lines(width // 2, 16, [title], size=12.5, weight="700", anchor="middle")]
    for j, login in enumerate(logins):
        x = left + j * col_w
        parts.append(f'<rect x="{x}" y="{top - 24}" width="{col_w - 2}" height="22" fill="{_FILL}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(x + col_w // 2 - 1, top - 9, [login], size=11, weight="700", anchor="middle"))
    for i, folder in enumerate(folders):
        y = top + i * row_h
        parts.append(f'<rect x="4" y="{y}" width="{left - 6}" height="{row_h - 2}" fill="{_SOFT}" stroke="{_STROKE}"/>')
        parts.append(_text_lines(8, y + 16, [folder], size=10.5, weight="700"))
        for j, login in enumerate(logins):
            x = left + j * col_w
            hidden = (login, folder) in blanks
            value = matrix[login][folder]
            parts.append(f'<rect data-cell="{escape(login)}|{escape(folder)}" data-value="{"" if hidden else escape(value)}" '
                         f'x="{x}" y="{y}" width="{col_w - 2}" height="{row_h - 2}" '
                         f'fill="{"#ffffff" if hidden else fills[value]}" stroke="{_STROKE}"'
                         f'{" stroke-dasharray=\"4 3\"" if hidden else ""}/>')
            parts.append(_text_lines(x + col_w // 2 - 1, y + 16, [f"{blanks[(login, folder)]} ?" if hidden else value],
                                     size=10.5, anchor="middle"))
    y = top + len(folders) * row_h + 16
    y = _notes(y, "Chaque case = droit effectif par le réseau : le plus restrictif des autorisations du partage "
               "et des autorisations NTFS du dossier.", parts)
    return _svg(width, y, parts)


def tree_svg(paths: tuple[str, ...] = (f"{SHARE_ROOT}\\Compta", f"{SHARE_ROOT}\\Compta\\Factures",
                                       f"{SHARE_ROOT}\\Compta\\Paie"), tree: dict[str, Folder] = NTFS_TREE) -> str:
    """Arborescence et héritage NTFS : chaque dossier liste ses entrées, « (hérité) » ou
    « (posé ici) » ; héritage désactivé signalé."""
    width = 380
    parts = [_text_lines(width // 2, 16, ["Héritage des autorisations NTFS"], size=12.5, weight="700", anchor="middle")]
    y = 28
    for path in paths:
        folder = tree[path]
        depth = path.count("\\") - SHARE_ROOT.count("\\") - 1
        x = 4 + 22 * depth
        lines = [path + ("  — héritage désactivé" if not folder.inherit else "")]
        for ace in ntfs_acl(path, tree):
            lines.append(f"{ace.principal} : {ace.right} " + ("(hérité)" if ace.inherited else "(posé ici)"))
        parts.append(_box(x, y, 376 - x, lines, key=folder.name, dashed=not folder.inherit,
                          fill="#fff3c4" if not folder.inherit else (_FILL if depth == 0 else _SOFT)))
        if depth:
            parts.append(f'<path d="M{x - 12} {y - 8} V{y + 16} H{x}" fill="none" stroke="{_STROKE}" stroke-width="1.5"/>')
        y += 12 + 15 * len(lines) + 12
    y += 6
    y = _notes(y, "Un sous-dossier reçoit les autorisations de son parent (hérité). Pour un dossier "
               "confidentiel, on désactive l'héritage, puis on ne garde que les groupes autorisés.", parts)
    return _svg(width, y, parts)


def printer_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Deux façons de partager une imprimante : USB sur un poste hôte, ou imprimante réseau à
    adresse fixe gérée par un serveur d'impression ; les postes clients s'y connectent par un
    chemin UNC. `blanks` (« usb_unc », « hote », « ip », « net_unc ») masque une valeur."""
    blanks = blanks or {}

    def val(key: str, text: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else text

    width = 380
    parts = [_text_lines(width // 2, 16, ["Imprimantes partagées"], size=12.5, weight="700", anchor="middle")]
    parts.append(_box(4, 28, 182, [PRINT_HOST, f"IP {PRINT_HOST_IP}", f"USB → {USB_PRINTER}",
                                   val("hote", "doit rester allumé")],
                      key="" if "hote" in blanks else "hote", dashed="hote" in blanks))
    parts.append(_box(194, 28, 182, [SERVER_NAME, "serveur d'impression", f"IP {SERVER_IP}", "file et pilote uniques"],
                      key="serveur"))
    parts.append(_box(194, 110, 160, [NET_PRINTER, "imprimante réseau", f"IP fixe {val('ip', NET_PRINTER_IP)}"],
                      key="" if "ip" in blanks else "imprimante", dashed="ip" in blanks, fill="#fff3c4"))
    parts.append(f'<rect data-node="switch" x="4" y="178" width="372" height="22" rx="5" fill="#e7ecf7" '
                 f'stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(190, 193, ["Switch — réseau 192.168.20.0/24"], size=11, weight="700", anchor="middle"))
    parts.append(f'<path d="M95 100 V178" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(f'<path d="M274 167 V178" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(f'<path d="M368 100 V178" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_box(4, 214, 372, ["Postes clients (PC-01, PC-02…)", f"USB partagée : {val('usb_unc', unc(PRINT_HOST, USB_PRINTER))}",
                                    f"réseau : {val('net_unc', unc(SERVER_NAME, NET_PRINTER))}"],
                      key="" if {"usb_unc", "net_unc"} & set(blanks) else "clients", dashed=bool({"usb_unc", "net_unc"} & set(blanks)),
                      fill=_SOFT))
    parts.append(f'<path d="M190 200 V214" stroke="{_STROKE}" stroke-width="2"/>')
    y = _notes(290, "Une imprimante USB partagée n'imprime que si son poste hôte est allumé. Une imprimante "
               "réseau garde une adresse fixe (ou réservée en DHCP) : sinon elle passe « hors connexion ».", parts)
    return _svg(width, y, parts)


LX_ROWS: tuple[tuple[str, str], ...] = (
    ("type", "d = dossier"),
    ("proprietaire", f"rwx — propriétaire {LX_OWNER}"),
    ("groupe", f"rws — groupe {LX_GROUP} (s : les nouveaux fichiers gardent le groupe)"),
    ("autres", "--- — tous les autres : aucun droit"),
    ("acl", "+ — une ACL ajoute group:direction:r-x"),
)


def unix_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Lecture d'une ligne `ls -ld` (mode 2770 + ACL) et accès Samba qui en résulte pour trois
    utilisateurs. `blanks` (clé d'une ligne de LX_ROWS, ou « u:<login> ») masque une valeur."""
    blanks = blanks or {}
    width = 380
    parts = [_text_lines(width // 2, 16, [f"Droits Unix de {LX_DIR}"], size=12.5, weight="700", anchor="middle")]
    parts.append(f'<rect x="4" y="26" width="372" height="26" rx="5" fill="#111827" stroke="{_STROKE}"/>')
    parts.append(f'<text x="12" y="44" font-size="11" fill="#e5e7eb" font-family="ui-monospace, Menlo, Consolas, monospace" '
                 f'xml:space="preserve">{escape(ls_lines()[1])}</text>')
    y = 62
    for key, text in LX_ROWS:
        hidden = key in blanks
        label = {"type": "Caractère 1", "proprietaire": "Caractères 2 à 4", "groupe": "Caractères 5 à 7",
                 "autres": "Caractères 8 à 10", "acl": "Caractère 11"}[key]
        lines = [label, *_wrap(f"{blanks[key]} ?" if hidden else text, 58)]
        parts.append(_box(4, y, 372, lines, key="" if hidden else key, dashed=hidden, fill="#ffffff" if hidden else _SOFT))
        y += 12 + 15 * len(lines) + 6
    y += 6
    parts.append(_text_lines(8, y, [f"Accès par Samba à [{LX_SHARE.name}] (write list = @compta) :"],
                             size=11, weight="700"))
    y += 10
    for user in LX_USERS:
        key = f"u:{user.login}"
        hidden = key in blanks
        text = f"{blanks[key]} ?" if hidden else linux_effective(user)
        parts.append(_box(4, y, 372, [f"{user.login} (groupe {', '.join(user.groups)}) → {text}"],
                          key="" if hidden else user.login, dashed=hidden, fill="#ffffff" if hidden else "#e9f5ec"))
        y += 33
    y = _notes(y + 12, "Le propriétaire, puis le groupe, puis les autres : la première classe qui correspond "
               "s'applique. Par Samba, le plus restrictif du partage et des droits Unix.", parts)
    return _svg(width, y, parts)


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte fictive, ligne par ligne : " + " / ".join(line.strip() for line in lines if line.strip())


def _unc_alt(blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}
    p = unc_parts(UNC_EXAMPLE)

    def v(key: str, text: str) -> str:
        return f"{blanks[key]} à compléter" if key in blanks else text

    return (
        f"Chemin UNC décomposé : deux barres obliques inverses, puis le serveur ({v('serveur', p['serveur'])}), "
        f"le nom du partage ({v('partage', p['partage'])}) et le chemin dans le partage ({v('chemin', p['chemin'])}). "
        f"Même ressource par l'adresse IP : {v('ip', UNC_EXAMPLE_IP)}. Lecteur réseau : "
        f"{v('lecteur', DRIVE_LETTER)} associé à {unc(SERVER_NAME, 'Compta')}."
    )


UNC_FIGURE = Figure(
    key="pr23-chemin-unc",
    title="Chemin UNC : serveur, partage, chemin",
    alt=_unc_alt(),
    caption=f"{UNC_EXAMPLE} : le serveur peut être désigné par son nom ou par son adresse IP.",
    svg=unc_svg(),
)

LAYERS_PATH = f"{SHARE_ROOT}\\Archives"


def _layers_alt(account: Account, path: str, blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}
    share = share_for(path)
    values = {"partage": share_level(account, path), "ntfs": ntfs_level(account, path),
              "reseau": effective_access(account, path), "local": effective_access(account, path, remote=False)}

    def v(key: str) -> str:
        return f"{blanks[key]} à compléter" if key in blanks else values[key]

    return (
        f"Compte {account.login} (groupes {', '.join(account.groups)}) qui ouvre {short_path(path)}. Barrière 1, "
        f"partage {share.name} : " + "; ".join(f"{e.principal} {e.right}" for e in share.entries)
        + f" ; droit du compte {v('partage')}. Barrière 2, NTFS : "
        + "; ".join(f"{e.principal} {e.right}" for e in ntfs_acl(path) if e.principal != LOCAL_ADMINS)
        + f" ; droit du compte {v('ntfs')}. Accès par le réseau (la plus restrictive) : {v('reseau')}. "
        f"Accès en session sur le serveur (NTFS seul) : {v('local')}."
    )


LAYERS_FIGURE = Figure(
    key="pr23-deux-barrieres",
    title="Partage puis NTFS : la plus restrictive l'emporte par le réseau",
    alt=_layers_alt(JULIE, LAYERS_PATH),
    caption="Julie modifie Archives en session sur le serveur, mais ne fait que lire par le réseau : le partage limite.",
    svg=layers_svg(JULIE, LAYERS_PATH),
)


def _matrix_alt(matrix: dict[str, dict[str, str]], blanks: dict[tuple[str, str], str] | None = None) -> str:
    blanks = blanks or {}
    return "Matrice des droits effectifs par le réseau. " + " ; ".join(
        f"{login} : " + ", ".join(f"{folder} " + (f"{blanks[(login, folder)]} à compléter" if (login, folder) in blanks
                                                   else value) for folder, value in row.items())
        for login, row in matrix.items()
    ) + "."


MATRIX_FIGURE = Figure(
    key="pr23-matrice-droits",
    title=f"Matrice des droits de {SERVER_NAME}",
    alt=_matrix_alt(ACCESS_MATRIX),
    caption="Calculée depuis les autorisations de partage et NTFS du serveur de référence (tableaux du chapitre 3).",
    svg=matrix_svg(ACCESS_MATRIX),
)

TREE_FIGURE = Figure(
    key="pr23-heritage",
    title="Héritage : Factures hérite de Compta, Paie ne l'hérite pas",
    alt="Arborescence : " + " ; ".join(
        f"{p}{' (héritage désactivé)' if not NTFS_TREE[p].inherit else ''} : "
        + ", ".join(f"{a.principal} {a.right} {'hérité' if a.inherited else 'posé ici'}" for a in ntfs_acl(p))
        for p in (f"{SHARE_ROOT}\\Compta", f"{SHARE_ROOT}\\Compta\\Factures", f"{SHARE_ROOT}\\Compta\\Paie")
    ) + ".",
    caption="Paie : héritage désactivé, seuls les administrateurs et G_Direction y entrent ; G_Compta n'y a plus accès.",
    svg=tree_svg(),
)

PRINTER_FIGURE = Figure(
    key="pr23-imprimantes",
    title="Imprimante USB partagée et imprimante réseau",
    alt=(
        f"{PRINT_HOST} ({PRINT_HOST_IP}) a l'imprimante {USB_PRINTER} en USB et la partage : il doit rester allumé. "
        f"Le serveur d'impression {SERVER_NAME} ({SERVER_IP}) gère l'imprimante réseau {NET_PRINTER} à l'adresse fixe "
        f"{NET_PRINTER_IP}. Tous sont reliés au switch du réseau 192.168.20.0/24. Les postes clients se connectent à "
        f"{unc(PRINT_HOST, USB_PRINTER)} et à {unc(SERVER_NAME, NET_PRINTER)}."
    ),
    caption="Le chemin UNC d'une imprimante partagée a la même forme que celui d'un dossier partagé.",
    svg=printer_svg(),
)

UNIX_FIGURE = Figure(
    key="pr23-droits-unix",
    title="Linux : lire drwxrws---+ et l'accès Samba",
    alt=(
        f"Ligne ls -ld : {ls_lines()[1]}. " + " ; ".join(text for _k, text in LX_ROWS)
        + ". Accès par Samba : " + " ; ".join(f"{u.login} (groupe {', '.join(u.groups)}) {linux_effective(u)}"
                                              for u in LX_USERS) + "."
    ),
    caption="marie (compta) modifie, paul (direction, par l'ACL) lit, sam n'entre pas.",
    svg=unix_svg(),
)

SHARE_TREE_QUESTIONS: tuple[tuple[str, str], ...] = tuple((what, diag) for _k, what, diag in SHARE_CHECKS)
SHARE_TREE_FINAL = "Tous les contrôles réussissent : accès conforme à la matrice des droits ; tester l'écriture."

SHARE_TREE_FIGURE = Figure(
    key="pr23-arbre-acces",
    title="Accès à un partage : contrôle par contrôle",
    alt=(
        "Arbre de décision : "
        + " ; ".join(f"{i}. {q} ? Si non : {d}" for i, (q, d) in enumerate(SHARE_TREE_QUESTIONS, start=1))
        + f". Si tout est oui : {SHARE_TREE_FINAL}"
    ),
    caption="« Le ping marche mais accès refusé » : réseau et nom sont bons, on continue vers le port 445, le compte, les droits.",
    svg=decision_tree_svg(SHARE_TREE_QUESTIONS, SHARE_TREE_FINAL),
)

PRINT_TREE_QUESTIONS: tuple[tuple[str, str], ...] = tuple((what, diag) for _k, what, diag in PRINT_CHECKS)
PRINT_TREE_FINAL = "Tous les contrôles réussissent : page de test imprimée depuis le poste."

PRINT_TREE_FIGURE = Figure(
    key="pr23-arbre-impression",
    title="Imprimante « hors connexion » ou qui n'imprime pas",
    alt=(
        "Arbre de décision : "
        + " ; ".join(f"{i}. {q} ? Si non : {d}" for i, (q, d) in enumerate(PRINT_TREE_QUESTIONS, start=1))
        + f". Si tout est oui : {PRINT_TREE_FINAL}"
    ),
    caption="De l'hôte au droit d'imprimer : on s'arrête au premier contrôle en échec.",
    svg=decision_tree_svg(PRINT_TREE_QUESTIONS, PRINT_TREE_FINAL),
)

ICACLS_LINES = icacls_lines(f"{SHARE_ROOT}\\Compta\\Factures")
ICACLS_FIGURE = Figure(
    key="pr23-icacls",
    title="Lire les autorisations NTFS avec icacls",
    alt=_screen_alt(ICACLS_LINES),
    caption="(I) = hérité ; (OI)(CI) = s'applique aux fichiers et sous-dossiers ; M = modification, RX = lecture et exécution, F = contrôle total.",
    svg=screen_svg(ICACLS_LINES, label=FICTIVE_LABEL),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


SHARE_PROC_FIGURE = _proc_figure("pr23-procedure-partage", 1, PROCEDURES[0][0], SHARE_STEPS,
                                 "NTFS d'abord, partage ensuite, test avec un compte de chaque groupe.")
PRINTER_PROC_FIGURE = _proc_figure("pr23-procedure-imprimante", 2, PROCEDURES[1][0], PRINTER_STEPS,
                                   "Adresse fixe, partage, droits, pare-feu, puis page de test depuis les postes.")
TROUBLE_PROC_FIGURE = _proc_figure("pr23-procedure-depannage", 3, PROCEDURES[2][0], TROUBLE_STEPS,
                                   "De l'adresse IP aux permissions : on s'arrête au premier contrôle en échec.")

PR23_FIGURES: tuple[Figure, ...] = (
    UNC_FIGURE,
    LAYERS_FIGURE,
    MATRIX_FIGURE,
    TREE_FIGURE,
    ICACLS_FIGURE,
    UNIX_FIGURE,
    PRINTER_FIGURE,
    SHARE_TREE_FIGURE,
    PRINT_TREE_FIGURE,
    SHARE_PROC_FIGURE,
    PRINTER_PROC_FIGURE,
    TROUBLE_PROC_FIGURE,
)

# =============================================================================================
# 9. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

UNC_BLANKS: dict[str, str] = {"serveur": "①", "partage": "②", "ip": "③", "lecteur": "④"}
UNC_BLANK_ANSWERS: dict[str, str] = {
    "①": SERVER_NAME,
    "②": "Compta",
    "③": UNC_EXAMPLE_IP,
    "④": DRIVE_LETTER,
}

UNC_BLANK_FIGURE = Figure(
    key="pr23-unc-a-completer",
    title="Chemin UNC à compléter",
    alt=_unc_alt(UNC_BLANKS),
    caption="Schéma à compléter : serveur ①, partage ②, forme par adresse IP ③, lettre de lecteur ④.",
    svg=unc_svg(blanks=UNC_BLANKS),
)

LAYERS_BLANK_ACCOUNT = CLAIRE
LAYERS_BLANK_PATH = f"{SHARE_ROOT}\\Compta"
LAYERS_BLANKS: dict[str, str] = {"partage": "①", "ntfs": "②", "reseau": "③", "local": "④"}
LAYERS_BLANK_ANSWERS: dict[str, str] = {
    "①": share_level(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH),
    "②": ntfs_level(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH),
    "③": effective_access(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH),
    "④": effective_access(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH, remote=False),
}

LAYERS_BLANK_FIGURE = Figure(
    key="pr23-barrieres-a-completer",
    title="Deux barrières à compléter",
    alt=_layers_alt(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH, LAYERS_BLANKS),
    caption="Schéma à compléter : droit de Claire dans le partage ①, dans NTFS ②, par le réseau ③, en local ④.",
    svg=layers_svg(LAYERS_BLANK_ACCOUNT, LAYERS_BLANK_PATH, blanks=LAYERS_BLANKS),
)

PRINTER_BLANKS: dict[str, str] = {"hote": "①", "ip": "②", "usb_unc": "③", "net_unc": "④"}
PRINTER_BLANK_ANSWERS: dict[str, str] = {
    "①": f"{PRINT_HOST} doit rester allumé (il partage l'imprimante USB)",
    "②": f"Adresse fixe ou réservation DHCP, ici {NET_PRINTER_IP}",
    "③": unc(PRINT_HOST, USB_PRINTER),
    "④": unc(SERVER_NAME, NET_PRINTER),
}

PRINTER_BLANK_FIGURE = Figure(
    key="pr23-imprimantes-a-completer",
    title="Imprimantes partagées à compléter",
    alt=(
        f"{PRINT_HOST} ({PRINT_HOST_IP}) a l'imprimante {USB_PRINTER} en USB et la partage ; condition ① à compléter. "
        f"Le serveur d'impression {SERVER_NAME} ({SERVER_IP}) gère l'imprimante réseau {NET_PRINTER}, adresse ② à "
        "compléter. Tous sont reliés au switch du réseau 192.168.20.0/24. Les postes clients se connectent à "
        "l'imprimante USB par le chemin ③ et à l'imprimante réseau par le chemin ④, à compléter."
    ),
    caption="Schéma à compléter : condition de l'hôte ①, adresse de l'imprimante réseau ②, chemins ③ et ④.",
    svg=printer_svg(blanks=PRINTER_BLANKS),
)

UNIX_BLANKS: dict[str, str] = {"groupe": "①", "autres": "②", "u:paul": "③", "u:sam": "④"}
UNIX_BLANK_ANSWERS: dict[str, str] = {
    "①": f"rws : le groupe {LX_GROUP} lit, écrit et entre ; s = les nouveaux fichiers gardent le groupe {LX_GROUP}",
    "②": "--- : les autres n'ont aucun droit",
    "③": linux_effective(LX_USERS[1]),
    "④": linux_effective(LX_USERS[2]),
}

UNIX_BLANK_FIGURE = Figure(
    key="pr23-unix-a-completer",
    title="Droits Unix à compléter",
    alt=(
        f"Ligne ls -ld : {ls_lines()[1]}. Caractère 1 : d = dossier ; caractères 2 à 4 : rwx, propriétaire "
        f"{LX_OWNER} ; caractères 5 à 7 : sens ① à compléter ; caractères 8 à 10 : sens ② à compléter ; "
        "caractère 11 : + = une ACL ajoute group:direction:r-x. Accès par Samba au partage compta (write list = "
        f"@compta) : marie (groupe compta) {linux_effective(LX_USERS[0])} ; paul (groupe direction) ③ à compléter ; "
        "sam (groupe secretariat) ④ à compléter."
    ),
    caption="Schéma à compléter : sens des caractères 5 à 7 ① et 8 à 10 ②, accès de paul ③ et de sam ④.",
    svg=unix_svg(blanks=UNIX_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (UNC_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr23-unc-a-completer.svg"),
    (LAYERS_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr23-barrieres-a-completer.svg"),
    (PRINTER_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr23-imprimantes-a-completer.svg"),
    (UNIX_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr23-unix-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18/PR21/PR22)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


def all_capture_lines() -> tuple[str, ...]:
    """Toutes les lignes de captures des figures (contrôle de largeur par les tests)."""
    return ICACLS_LINES + ls_lines() + getfacl_lines() + SMB_CONF_LINES + SPOOLER_LINES


"""PR22 « Domaine, groupe de travail, comptes et groupes » — données de référence, calculs,
relevés de commandes fictifs et schémas SVG (ticket #222).

Tout est construit **depuis des données** de ce module, contrôlées par
`tests/test_ticket222_ampcr_pratique_pr22.py` (qui recalcule indépendamment) :

- groupe de travail : base de comptes **propre à chaque poste** ; comptes locaux à créer pour
  que chaque personne ouvre ses postes et les partages (`workgroup_accounts`), comparés au
  domaine (un compte par personne, `ACCOUNT_COUNTS`) ;
- domaine Active Directory de référence : contrôleur `DC01` (adresse fixe, service DNS),
  domaine DNS `ad.dupont.example`, nom NetBIOS `DUPONT`, box passerelle ; formes des noms de
  connexion (`logon_forms`, `account_scope`) ;
- prérequis de la jonction d'un poste (`join_blockers`) ;
- groupes : groupes de domaine imbriqués dans les groupes locaux après la jonction
  (`LOCAL_NESTING`), droits donnés aux groupes (`access_of`) ;
- audit d'une fiche de comptes (`account_errors`) et choix groupe de travail / domaine pour
  une organisation de 3 à 20 postes (`recommend_model`) ;
- dépannage de l'ouverture de session dans l'ordre (`LOGON_CHECKS`, `logon_checks`,
  `logon_diagnosis`, `first_failure`) et trois procédures illustrées ;
- quatre schémas à compléter servis aussi en fichiers statiques (`STATIC_FIGURES`).

Valeurs de référence : documentation Microsoft (Active Directory Domain Services, jonction
d'un ordinateur à un domaine, stratégie Kerberos « tolérance maximale pour la synchronisation
de l'horloge » = 5 minutes par défaut, groupes par défaut « Admins du domaine » et
« Utilisateurs du domaine » ajoutés aux groupes locaux « Administrateurs » et « Utilisateurs »
à la jonction ; Windows Famille ne peut pas rejoindre un domaine ; nom d'ordinateur NetBIOS de
15 caractères au plus). RFC 2606 / RFC 6761 : le domaine `.example` est réservé à la
documentation, d'où `ad.dupont.example` (fictif). Messages Windows en français : **captures
fictives simplifiées** au format réel, 56 caractères par ligne au plus (lisibles sur mobile).

**Conventions du cours**, signalées dans le texte : réseau 192.168.20.0/24, contrôleur en .10,
box en .254 ; groupes métier préfixés `G_` ; compte d'administration séparé préfixé `adm-` ;
repère « groupe de travail jusqu'à une dizaine de postes sans besoin de gestion centralisée ».
Personnes, postes et entreprises **fictifs**. Chaque schéma porte son information en texte :
la couleur n'est qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

import ipaddress
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

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56
FICTIVE_LABEL = "capture fictive — présentation simplifiée"
_STROKE = "#33415c"
_FILL = "#dbe4f3"
_SOFT = "#f4f6fb"

# =============================================================================================
# 1. Domaine de référence
# =============================================================================================

NETWORK = "192.168.20.0/24"
DNS_DOMAIN = "ad.dupont.example"  # domaine DNS du domaine Active Directory (fictif, RFC 2606)
NETBIOS_DOMAIN = "DUPONT"  # nom NetBIOS (court) du même domaine
DC_NAME = "DC01"
DC_IP = "192.168.20.10"
DC_FQDN = f"{DC_NAME.lower()}.{DNS_DOMAIN}"
BOX_IP = "192.168.20.254"
MAX_CLOCK_SKEW_MIN = 5  # stratégie Kerberos par défaut
MAX_COMPUTER_NAME = 15  # nom NetBIOS d'un ordinateur
WORKGROUP_DEFAULT = "WORKGROUP"

ADMINS_DOMAIN = "Admins du domaine"
USERS_DOMAIN = "Utilisateurs du domaine"
COMPUTERS_DOMAIN = "Ordinateurs du domaine"
LOCAL_ADMINS = "Administrateurs"
LOCAL_USERS = "Utilisateurs"

# Imbrication ajoutée automatiquement à la jonction : groupe du domaine → groupe local du poste.
LOCAL_NESTING: tuple[tuple[str, str], ...] = (
    (ADMINS_DOMAIN, LOCAL_ADMINS),
    (USERS_DOMAIN, LOCAL_USERS),
)


def local_groups_of(domain_groups: tuple[str, ...]) -> tuple[str, ...]:
    """Groupes locaux d'un poste du domaine dont un compte de domaine est membre (par
    l'imbrication par défaut)."""
    return tuple(local for dom, local in LOCAL_NESTING if dom in domain_groups)


@dataclass(frozen=True)
class Workstation:
    name: str
    ip: str
    dns: tuple[str, ...]
    gateway: str | None = BOX_IP
    edition: str = "Windows 11 Professionnel"
    clock_offset_min: float = 0.0  # avance (+) ou retard (−) sur le contrôleur
    secure_channel: bool = True  # relation d'approbation poste ↔ domaine valide
    link: bool = True


@dataclass(frozen=True)
class Account:
    login: str
    person: str
    groups: tuple[str, ...] = (USERS_DOMAIN,)
    enabled: bool = True
    locked: bool = False
    password_expired: bool = False
    token_groups: tuple[str, ...] | None = None  # groupes de la session ouverte (None = à jour)

    def session_groups(self) -> tuple[str, ...]:
        return self.groups if self.token_groups is None else self.token_groups


PC_OK = Workstation("PC-03", "192.168.20.13", (DC_IP,))
USER_OK = Account("jmartin", "Julie Martin", (USERS_DOMAIN, "G_Compta"))
TECH_DAILY = Account("tleroy", "Tom Leroy (technicien)", (USERS_DOMAIN, "G_Informatique"))
TECH_ADMIN = Account("adm-tleroy", "Tom Leroy (administration)", (USERS_DOMAIN, ADMINS_DOMAIN))


def logon_forms(login: str, *, computer: str) -> dict[str, str]:
    """Les façons d'écrire un même nom de connexion : local (deux formes), domaine (NetBIOS
    et UPN)."""
    return {
        "local (ce poste)": f".\\{login}",
        "local (poste nommé)": f"{computer}\\{login}",
        "domaine (NetBIOS)": f"{NETBIOS_DOMAIN}\\{login}",
        "domaine (UPN)": f"{login}@{DNS_DOMAIN}",
    }


SCOPE_LOCAL = "Compte local du poste"
SCOPE_DOMAIN = "Compte du domaine"
SCOPES = (SCOPE_LOCAL, SCOPE_DOMAIN)


def account_scope(logon_name: str, *, domain_names: tuple[str, ...] = (NETBIOS_DOMAIN, DNS_DOMAIN)) -> str:
    """Le nom de connexion désigne-t-il un compte local ou un compte du domaine ?
    `.\\nom` et `POSTE\\nom` : local ; `DOMAINE\\nom` et `nom@domaine.dns` : domaine."""
    if "@" in logon_name:
        return SCOPE_DOMAIN if logon_name.split("@", 1)[1].lower() in (d.lower() for d in domain_names) else SCOPE_LOCAL
    if "\\" in logon_name:
        prefix = logon_name.split("\\", 1)[0]
        return SCOPE_DOMAIN if prefix.upper() in (d.upper() for d in domain_names) else SCOPE_LOCAL
    raise ValueError(f"Nom sans préfixe : {logon_name}")


# =============================================================================================
# 2. Groupe de travail : comptes locaux à créer
# =============================================================================================

# Organisation de référence (cabinet de 4 postes) : postes utilisés par chaque personne, et
# poste qui partage le dossier commun.
WG_USERS: dict[str, tuple[str, ...]] = {
    "anne": ("PC-1",),
    "paul": ("PC-2",),
    "sara": ("PC-3",),
    "marc": ("PC-4", "PC-2"),
}
WG_PCS = ("PC-1", "PC-2", "PC-3", "PC-4")
WG_SHARE_PC = "PC-1"  # PC-1 partage le dossier « Commun »
WG_SHARE_USERS = ("anne", "paul", "sara", "marc")


def workgroup_accounts(users: dict[str, tuple[str, ...]], share_pc: str | None,
                       share_users: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Comptes locaux nécessaires sur chaque poste d'un groupe de travail : un compte pour
    chaque personne qui ouvre une session sur ce poste, plus, sur le poste qui partage, un
    compte pour chaque personne qui ouvre le partage par le réseau."""
    pcs = sorted({pc for used in users.values() for pc in used} | ({share_pc} if share_pc else set()))
    result: dict[str, tuple[str, ...]] = {}
    for pc in pcs:
        names = {u for u, used in users.items() if pc in used}
        if pc == share_pc:
            names |= set(share_users)
        result[pc] = tuple(sorted(names))
    return result


def count_accounts(accounts: dict[str, tuple[str, ...]]) -> int:
    return sum(len(v) for v in accounts.values())


WG_ACCOUNTS = workgroup_accounts(WG_USERS, WG_SHARE_PC, WG_SHARE_USERS)


def office_accounts(people: int) -> tuple[int, int]:
    """Organisation type de `people` personnes : chacune a son poste ; tout le monde ouvre le
    dossier commun partagé par le premier poste ; une personne sur quatre (arrondi inférieur)
    travaille aussi sur un deuxième poste. Renvoie (comptes locaux du groupe de travail,
    comptes du domaine)."""
    users = {f"u{i:02d}": (f"P{i:02d}",) for i in range(1, people + 1)}
    for i in range(1, people // 4 + 1):
        users[f"u{i:02d}"] = (f"P{i:02d}", f"P{(i % people) + 1:02d}")
    wg = workgroup_accounts(users, "P01", tuple(users))
    return count_accounts(wg), len(users)


ACCOUNT_SIZES = (3, 5, 10, 20)
ACCOUNT_COUNTS: tuple[tuple[int, int, int], ...] = tuple((n, *office_accounts(n)) for n in ACCOUNT_SIZES)

# =============================================================================================
# 3. Choisir : groupe de travail ou domaine (repère du cours)
# =============================================================================================

MODEL_WG = "Groupe de travail"
MODEL_DOMAIN = "Domaine Active Directory"
MODELS = (MODEL_WG, MODEL_DOMAIN)
WG_MAX_POSTES = 10  # repère du cours


@dataclass(frozen=True)
class Organisation:
    label: str
    postes: int
    rotation: bool = False  # arrivées et départs fréquents, postes partagés par plusieurs personnes
    policies: bool = False  # règles imposées à tous les postes (mots de passe, verrouillage…)
    roaming: bool = False  # les personnes changent de poste et doivent retrouver leur compte


def recommend_model(org: Organisation) -> str:
    """Repère du cours : au-delà d'une dizaine de postes, ou dès qu'il faut gérer les comptes
    et les règles depuis un point central (rotation, stratégies, itinérance), un domaine ; sinon
    un groupe de travail suffit."""
    if org.postes > WG_MAX_POSTES or org.rotation or org.policies or org.roaming:
        return MODEL_DOMAIN
    return MODEL_WG


COMPARISON: tuple[tuple[str, str, str], ...] = (
    ("Où sont les comptes", "Sur chaque poste (base locale)", "Sur le contrôleur de domaine, pour tous les postes"),
    ("Ouvrir une session sur un autre poste", "Il faut un compte local sur ce poste", "Le même compte ouvre tous les postes du domaine"),
    ("Changer un mot de passe", "Sur chaque poste où le compte existe", "Une fois, sur le contrôleur"),
    ("Règles de sécurité communes", "Poste par poste", "Stratégies de groupe (GPO) appliquées à tous"),
    ("Matériel nécessaire", "Aucun serveur", "Au moins un serveur contrôleur de domaine (deux conseillés)"),
    ("Édition de Windows des postes", "Toutes (même Famille)", "Professionnel, Entreprise ou Éducation"),
    ("Adapté à", "Quelques postes, peu de changements", "Au-delà d'une dizaine de postes ou gestion centralisée"),
)

# =============================================================================================
# 4. Jonction d'un poste au domaine
# =============================================================================================

JOIN_PREREQUISITES: tuple[tuple[str, str], ...] = (
    ("Édition", "Windows Professionnel, Entreprise ou Éducation (Famille ne rejoint pas un domaine)."),
    ("Nom du poste", f"Unique dans le domaine, {MAX_COMPUTER_NAME} caractères au plus."),
    ("Réseau", "Le poste joint le contrôleur (lien, adresse du même réseau ou routage)."),
    ("DNS", f"Le serveur DNS du poste est le contrôleur ({DC_IP}), pas la box."),
    ("Heure", f"Écart avec le contrôleur de {MAX_CLOCK_SKEW_MIN} minutes au plus."),
    ("Compte autorisé", "Un compte du domaine autorisé à joindre des postes (administrateur du domaine)."),
)


def join_blockers(ws: Workstation, *, existing_names: tuple[str, ...] = ()) -> list[str]:
    """Prérequis manquants pour joindre `ws` au domaine de référence, dans l'ordre du tableau."""
    blockers: list[str] = []
    if "Famille" in ws.edition:
        blockers.append("Édition")
    if len(ws.name) > MAX_COMPUTER_NAME or ws.name.upper() in (n.upper() for n in existing_names):
        blockers.append("Nom du poste")
    if not reaches_dc(ws):
        blockers.append("Réseau")
    if not dns_ok(ws):
        blockers.append("DNS")
    if abs(ws.clock_offset_min) > MAX_CLOCK_SKEW_MIN:
        blockers.append("Heure")
    return blockers


def reaches_dc(ws: Workstation) -> bool:
    return ws.link and ipaddress.ip_address(DC_IP) in ipaddress.ip_network(f"{ws.ip}/24", strict=False)


def dns_ok(ws: Workstation) -> bool:
    """Un poste du domaine n'interroge que le DNS du domaine (le contrôleur), qui relaie
    lui-même vers Internet : un DNS de box ou public ne connaît pas le domaine."""
    return bool(ws.dns) and all(d == DC_IP for d in ws.dns)


JOIN_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier les prérequis", "Édition Professionnel, nom unique, réseau, heure à l'heure."),
    ("Régler le DNS du poste", f"DNS = contrôleur {DC_IP} (adresse fixe ou option DHCP)."),
    ("Tester le contrôleur", f"ping {DC_IP} ; nslookup {DNS_DOMAIN} renvoie {DC_IP}."),
    ("Joindre le domaine", f"Système → Domaine : {DNS_DOMAIN}, compte autorisé (adm-…)."),
    ("Redémarrer", "Message « Bienvenue dans le domaine », puis redémarrage obligatoire."),
    ("Ouvrir une session du domaine", f"{NETBIOS_DOMAIN}\\jmartin ; whoami ; gpresult /r."),
    ("Consigner", "Poste, date, unité d'organisation, résultats des tests dans la fiche."),
)

# =============================================================================================
# 5. Comptes, groupes, droits
# =============================================================================================

RIGHT_NONE = "Aucun accès"
RIGHT_READ = "Lecture"
RIGHT_CHANGE = "Modification"
RIGHTS = (RIGHT_NONE, RIGHT_READ, RIGHT_CHANGE)

# Dossiers du serveur et droits donnés aux groupes (jamais aux personnes).
FOLDER_ACL: dict[str, dict[str, str]] = {
    "Compta": {"G_Compta": RIGHT_CHANGE, "G_Direction": RIGHT_READ},
    "Commun": {USERS_DOMAIN: RIGHT_CHANGE},
    "Direction": {"G_Direction": RIGHT_CHANGE},
}


def access_of(account: Account, folder: str, *, acl: dict[str, dict[str, str]] = FOLDER_ACL) -> str:
    """Droit effectif d'un compte sur un dossier : le plus fort des droits de ses groupes **de
    la session ouverte** (un ajout à un groupe ne compte qu'après reconnexion)."""
    best = 0
    for group, right in acl[folder].items():
        if group in account.session_groups():
            best = max(best, RIGHTS.index(right))
    return RIGHTS[best]


GROUP_SHEET: tuple[tuple[str, str, str], ...] = (
    ("G_Compta", "Comptabilité : jmartin, lbernard", "Compta : Modification"),
    ("G_Direction", "Direction : cdupont", "Direction : Modification ; Compta : Lecture"),
    (USERS_DOMAIN, "Tous les comptes du domaine", "Commun : Modification"),
    (ADMINS_DOMAIN, "adm-tleroy uniquement", "Administration de tous les postes et du domaine"),
)

LIFECYCLE_STEPS: tuple[tuple[str, str], ...] = (
    ("Recevoir la demande", "Écrite et validée : nom, fonction, date d'arrivée, accès nécessaires."),
    ("Créer le compte", "Un compte nominatif par personne, dans la bonne unité d'organisation."),
    ("Mot de passe initial", "Temporaire, remis à part ; « changer à la prochaine ouverture de session »."),
    ("Groupes", "Groupes métier seulement (G_…) ; jamais Admins du domaine pour un utilisateur."),
    ("Tester", "Connexion d'essai, accès aux dossiers prévus et refus des autres."),
    ("Départ : désactiver", "Le jour du départ : compte désactivé, retiré des groupes, sessions fermées."),
    ("Supprimer plus tard", "Après sauvegarde des données et délai prévu par l'entreprise."),
)

ACCOUNT_ACTION_DISABLE = "Désactiver le compte"
ACCOUNT_ACTION_RESET = "Réinitialiser le mot de passe"
ACCOUNT_ACTION_UNLOCK = "Déverrouiller le compte"
ACCOUNT_ACTION_GROUP = "Ajouter à un groupe métier"
ACCOUNT_ACTIONS = (ACCOUNT_ACTION_DISABLE, ACCOUNT_ACTION_RESET, ACCOUNT_ACTION_UNLOCK, ACCOUNT_ACTION_GROUP)


@dataclass(frozen=True)
class AccountRow:
    """Ligne d'une fiche de comptes à auditer."""
    login: str
    person: str
    groups: tuple[str, ...]
    enabled: bool = True
    left: bool = False  # la personne a quitté l'entreprise
    shared: bool = False  # compte utilisé par plusieurs personnes


ERR_SHARED = "compte commun à plusieurs personnes : un compte nominatif par personne"
ERR_LEFT = "personne partie, compte encore actif : à désactiver"
ERR_ADMIN = "droits d'administration pour un compte de travail quotidien : moindre privilège"
ERR_GUEST = "compte Invité activé : à désactiver"


def account_errors(rows: tuple[AccountRow, ...]) -> list[str]:
    """Erreurs d'une fiche de comptes (une ligne peut en cumuler plusieurs)."""
    errors: list[str] = []
    for row in rows:
        if row.shared:
            errors.append(f"{row.login} : {ERR_SHARED}")
        if row.left and row.enabled:
            errors.append(f"{row.login} : {ERR_LEFT}")
        if ADMINS_DOMAIN in row.groups and not row.login.startswith("adm-") and row.enabled:
            errors.append(f"{row.login} : {ERR_ADMIN}")
        if row.login.lower() == "invité" and row.enabled:
            errors.append(f"{row.login} : {ERR_GUEST}")
    return errors


# =============================================================================================
# 6. Ouverture de session : diagnostic dans l'ordre
# =============================================================================================

D_NET = "Réseau : le poste ne joint pas le contrôleur"
D_DNS = "DNS : le poste n'interroge pas le contrôleur"
D_TIME = "Heure : écart de plus de 5 minutes avec le contrôleur"
D_TRUST = "Poste : relation d'approbation avec le domaine rompue"
D_ACCOUNT = "Compte : désactivé, verrouillé ou mot de passe expiré"
D_RIGHTS = "Droits : groupe manquant ou session pas rouverte"
D_OK = "Session et accès validés"
DIAGNOSES = (D_NET, D_DNS, D_TIME, D_TRUST, D_ACCOUNT, D_RIGHTS)

LOGON_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("reseau", f"Le poste joint le contrôleur (lien, adresse, ping {DC_IP})", D_NET),
    ("dns", f"DNS du poste = contrôleur ; nslookup {DNS_DOMAIN} répond", D_DNS),
    ("heure", f"Écart d'heure avec le contrôleur ≤ {MAX_CLOCK_SKEW_MIN} minutes", D_TIME),
    ("approbation", "La relation d'approbation du poste est valide", D_TRUST),
    ("compte", "Compte actif, non verrouillé, mot de passe valide", D_ACCOUNT),
    ("droits", "Le compte a le groupe voulu dans sa session (whoami /groups)", D_RIGHTS),
)
CHECK_KEYS = tuple(k for k, _w, _d in LOGON_CHECKS)


def logon_checks(ws: Workstation, account: Account, *, needed_group: str | None = None) -> dict[str, bool]:
    """Résultats des contrôles, calculés depuis la configuration du poste et l'état du compte."""
    return {
        "reseau": reaches_dc(ws),
        "dns": dns_ok(ws),
        "heure": abs(ws.clock_offset_min) <= MAX_CLOCK_SKEW_MIN,
        "approbation": ws.secure_channel,
        "compte": account.enabled and not account.locked and not account.password_expired,
        "droits": needed_group is None or needed_group in account.session_groups(),
    }


def logon_diagnosis(results: dict[str, bool]) -> str:
    """Le premier contrôle en échec désigne la piste ; les suivants ne prouvent rien tant qu'il
    n'est pas réglé."""
    for key, _what, diagnosis in LOGON_CHECKS:
        if not results[key]:
            return diagnosis
    return D_OK


def first_failure(failed: str) -> dict[str, bool]:
    index = CHECK_KEYS.index(failed)
    return {k: i < index for i, k in enumerate(CHECK_KEYS)}


# Messages Windows (français) et piste correspondante.
LOGON_MESSAGES: tuple[tuple[str, str], ...] = (
    ("Il n'existe actuellement aucun serveur d'ouverture de session disponible…", D_NET),
    ("Un contrôleur de domaine Active Directory pour le domaine … n'a pas pu être contacté.", D_DNS),
    ("Différence d'heure ou de date entre cet ordinateur et le serveur (Kerberos).", D_TIME),
    ("La relation d'approbation entre cette station de travail et le domaine principal a échoué.", D_TRUST),
    ("Votre compte a été désactivé. Contactez votre administrateur système.", D_ACCOUNT),
    ("Le compte référencé est actuellement verrouillé…", D_ACCOUNT),
    ("Accès refusé (dossier partagé, session ouverte normalement).", D_RIGHTS),
)

TROUBLE_STEPS: tuple[tuple[str, str], ...] = (
    ("Lire le message exact", "Le noter mot pour mot ; un ou plusieurs postes, un ou plusieurs comptes ?"),
    ("Réseau", f"Lien, ipconfig, ping {DC_IP}."),
    ("DNS", f"ipconfig /all : DNS = {DC_IP} ; nslookup {DNS_DOMAIN}."),
    ("Heure", "Comparer avec le contrôleur ; w32tm /resync."),
    ("Poste", f"nltest /sc_query:{DNS_DOMAIN} ; réparer le canal ou rejoindre."),
    ("Compte", "net user jmartin /domain : actif, verrouillé, mot de passe."),
    ("Droits", "whoami /groups ; groupe ajouté → fermer puis rouvrir la session."),
    ("Consigner", "Cause, correction, test de connexion réussi."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Joindre un poste Windows au domaine", JOIN_STEPS),
    ("Gérer un compte, de l'arrivée au départ", LIFECYCLE_STEPS),
    ("Dépanner une ouverture de session ou un accès refusé", TROUBLE_STEPS),
)

# =============================================================================================
# 7. Relevés fictifs (56 caractères par ligne au plus)
# =============================================================================================


def ipconfig_dns_lines(ws: Workstation) -> tuple[str, ...]:
    return (
        "C:\\> ipconfig /all",
        "",
        "Configuration IP de Windows",
        f"   Nom de l'hôte . . . : {ws.name}",
        "",
        "Carte Ethernet Ethernet :",
        f"   Adresse IPv4. . . . : {ws.ip}",
        "   Masque de s.-réseau : 255.255.255.0",
        f"   Passerelle défaut . : {ws.gateway or ''}".rstrip(),
        *(f"   Serveurs DNS. . . . : {d}" if i == 0 else f"                         {d}" for i, d in enumerate(ws.dns)),
    )


def nslookup_lines(server_ip: str, *, knows_domain: bool) -> tuple[str, ...]:
    head = ["C:\\> nslookup " + DNS_DOMAIN]
    if server_ip == DC_IP:
        head += [f"Serveur :   {DC_FQDN}", f"Address:  {DC_IP}", ""]
    else:
        head += ["Serveur :   box.home", f"Address:  {server_ip}", ""]
    if knows_domain:
        return (*head, f"Nom :    {DNS_DOMAIN}", f"Address:  {DC_IP}")
    return (*head, "*** box.home ne parvient pas à trouver", f"    {DNS_DOMAIN} : Non-existent domain")


def net_user_lines(account: Account) -> tuple[str, ...]:
    """`net user <login> /domain` simplifié (comme Windows, « Compte : actif » vaut Oui, Non ou
    Verrouillé)."""
    active = "Verrouillé" if account.locked else ("Oui" if account.enabled else "Non")
    return (
        f"C:\\> net user {account.login} /domain",
        f"Nom d'utilisateur              {account.login}",
        f"Nom complet                    {account.person}"[:SCREEN_WIDTH],
        f"Compte : actif                 {active}",
        "Le compte expire               Jamais",
        "Appartient aux groupes globaux " + (" ".join(f"*{g}" for g in account.groups[:1])),
        *("                               " + f"*{g}" for g in account.groups[1:]),
        "La commande s'est terminée correctement.",
    )


def whoami_groups_lines(account: Account) -> tuple[str, ...]:
    """`whoami /groups` simplifié : groupes de la session ouverte."""
    return (
        "C:\\> whoami",
        f"{NETBIOS_DOMAIN.lower()}\\{account.login}",
        "C:\\> whoami /groups   (extrait simplifié)",
        *(f"{NETBIOS_DOMAIN}\\{g}" for g in account.session_groups() if g != USERS_DOMAIN),
        f"{NETBIOS_DOMAIN}\\{USERS_DOMAIN}",
        *(f"BUILTIN\\{g}" for g in local_groups_of(account.session_groups())),
    )


def time_lines(ws: Workstation, *, dc_time: str = "09:12") -> tuple[str, ...]:
    hours, minutes = (int(x) for x in dc_time.split(":"))
    total = hours * 60 + minutes + round(ws.clock_offset_min)
    local = f"{total // 60:02d}:{total % 60:02d}"
    return (
        f"C:\\> net time \\\\{DC_NAME}",
        f"L'heure actuelle de \\\\{DC_NAME} est 27/10/2026 {dc_time}",
        "La commande s'est terminée correctement.",
        "C:\\> time /t",
        local,
    )


def secure_channel_lines(ok: bool) -> tuple[str, ...]:
    lines = [f"C:\\> nltest /sc_query:{DNS_DOMAIN}"]
    if ok:
        lines += [f"Canal sécurisé vers \\\\{DC_FQDN}", "État = 0 0x0 NERR_Success"]
    else:
        lines += ["Échec : la relation d'approbation entre", "cette station et le domaine principal a échoué.",
                  "État = 1789 0x6fd"]
    return tuple(lines)


JOIN_OK_LINES = (
    f"PS> Add-Computer -DomainName {DNS_DOMAIN} `",
    f"      -Credential {NETBIOS_DOMAIN}\\adm-tleroy -Restart",
    "(après redémarrage, session DUPONT\\jmartin)",
    *whoami_groups_lines(USER_OK),
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


def workgroup_svg(accounts: dict[str, tuple[str, ...]], *, share_pc: str,
                  blanks: dict[str, str] | None = None) -> str:
    """Groupe de travail : chaque poste (2 colonnes) affiche **sa propre** liste de comptes
    locaux ; un switch les relie, sans serveur. `blanks` (« PC-x » → numéro) masque la liste
    d'un poste."""
    blanks = blanks or {}
    width, col_w = 380, 180
    parts = [_text_lines(width // 2, 16, ["Groupe de travail WORKGROUP — pas de serveur"], size=12,
                         weight="700", anchor="middle")]
    pcs = list(accounts)
    heights = [12 + 15 * (2 + (1 if pc in blanks else len(accounts[pc]))) for pc in pcs]
    row_h = max(heights) + 10
    top = 30
    for index, pc in enumerate(pcs):
        x = 6 + (index % 2) * (col_w + 8)
        y = top + (index // 2) * (row_h + 34)
        title = f"{pc}" + (" (partage Commun)" if pc == share_pc else "")
        names = [f"{blanks[pc]} ?"] if pc in blanks else [f"• {n}" for n in accounts[pc]]
        parts.append(_box(x, y, col_w, [title, "Comptes locaux :", *names], key="" if pc in blanks else pc,
                          dashed=pc in blanks))
    rows = (len(pcs) + 1) // 2
    sw_y = top + row_h + 4
    if rows > 1:
        parts.append(f'<rect data-node="switch" x="150" y="{sw_y}" width="80" height="22" rx="5" fill="#e7ecf7" '
                     f'stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(_text_lines(190, sw_y + 15, ["Switch"], size=11, weight="700", anchor="middle"))
    y = max(top + (i // 2) * (row_h + 34) + h for i, h in enumerate(heights)) + 22
    notes = _wrap("Chaque poste vérifie lui-même ses comptes : pour ouvrir une session sur un poste ou "
                  "ouvrir son partage, il faut un compte (avec mot de passe) sur CE poste.", 60)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def domain_svg(workstations: tuple[Workstation, ...], *, blanks: dict[str, str] | None = None) -> str:
    """Domaine : box (passerelle) et contrôleur DC01 (AD DS + DNS, adresse fixe) reliés au
    switch, puis les postes joints au domaine, avec leur DNS et leur passerelle. `blanks`
    (« role », « dc_ip », « <poste>:dns », « <poste>:passerelle ») masque une valeur."""
    blanks = blanks or {}
    width = 380

    def val(key: str, text: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else text

    parts: list[str] = []
    parts.append(_box(72, 6, 304, ["Box — passerelle vers Internet", f"LAN : {BOX_IP}/24"], key="box"))
    parts.append(_box(72, 52, 304, [f"{DC_NAME} — {val('role', 'contrôleur de domaine + DNS')}",
                                    f"IP fixe {val('dc_ip', DC_IP)}/24 · domaine {DNS_DOMAIN}",
                                    f"comptes, groupes, stratégies ({NETBIOS_DOMAIN})"],
                      key="" if {"role", "dc_ip"} & set(blanks) else "dc", fill="#fff3c4"))
    top, row_h, gap = 116, 57, 6
    for index, ws in enumerate(workstations):
        y = top + index * (row_h + gap)
        parts.append(_box(72, y, 304, [
            f"{ws.name} — membre du domaine",
            f"IP {ws.ip}/24 · DNS {val(f'{ws.name}:dns', ', '.join(ws.dns))}",
            f"passerelle {val(f'{ws.name}:passerelle', ws.gateway or '(vide)')}",
        ], key="" if any(k.startswith(f"{ws.name}:") for k in blanks) else ws.name))
    bottom = top + len(workstations) * (row_h + gap) - gap
    parts.append(f'<rect data-node="switch" x="4" y="6" width="54" height="{bottom - 6}" rx="8" fill="#e7ecf7" '
                 f'stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(31, 90, ["Switch"], size=11.5, weight="700", anchor="middle"))
    for y in [27, 80] + [top + i * (row_h + gap) + 28 for i in range(len(workstations))]:
        parts.append(f'<path d="M58 {y} H72" stroke="{_STROKE}" stroke-width="2"/>')
    y = bottom + 18
    notes = _wrap("Les postes s'authentifient auprès du contrôleur (Kerberos) et le trouvent par le DNS : "
                  "leur DNS est le contrôleur, qui relaie vers Internet. La box reste la passerelle.", 60)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


NAME_ROWS: tuple[tuple[str, str], ...] = (
    ("Domaine DNS (nom complet)", DNS_DOMAIN),
    ("Nom NetBIOS du domaine", NETBIOS_DOMAIN),
    ("Contrôleur (nom DNS complet)", DC_FQDN),
    ("Poste (nom DNS complet)", f"pc-03.{DNS_DOMAIN}"),
    ("Connexion au domaine (NetBIOS)", f"{NETBIOS_DOMAIN}\\jmartin"),
    ("Connexion au domaine (UPN)", f"jmartin@{DNS_DOMAIN}"),
    ("Compte local du poste", ".\\support  ou  PC-03\\support"),
)


def names_svg(*, blanks: dict[int, str] | None = None) -> str:
    """Fiche d'identité du domaine : une ligne par nom. `blanks` (index → numéro) masque une
    valeur."""
    blanks = blanks or {}
    width, row_h, top = 380, 34, 30
    parts = [_text_lines(width // 2, 18, ["Les noms d'un même domaine"], size=12.5, weight="700", anchor="middle")]
    for index, (label, value) in enumerate(NAME_ROWS):
        y = top + index * row_h
        hidden = index in blanks
        parts.append(f'<rect data-row="{index + 1}" data-value="{"" if hidden else escape(value)}" x="4" y="{y}" '
                     f'width="372" height="{row_h - 4}" rx="4" fill="{"#ffffff" if hidden else _SOFT}" '
                     f'stroke="{_STROKE}" stroke-width="1"{" stroke-dasharray=\"5 3\"" if hidden else ""}/>')
        parts.append(_text_lines(10, y + 13, [label], size=10, weight="700"))
        parts.append(_text_lines(10, y + 26, [f"{blanks[index]} ?" if hidden else value], size=11))
    y = top + len(NAME_ROWS) * row_h + 10
    notes = _wrap("Domaine DNS : nom du domaine dans le DNS (fictif, .example). NetBIOS : nom court, "
                  "15 caractères au plus. Le préfixe avant « \\ » dit qui vérifie le mot de passe.", 60)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def join_dialog_svg(ws: Workstation) -> str:
    """Fenêtre fictive « Modification du nom ou du domaine de l'ordinateur »."""
    width = 380
    parts = [
        f'<rect x="2" y="2" width="{width - 4}" height="206" rx="6" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="2" y="2" width="{width - 4}" height="24" rx="6" fill="{_FILL}" stroke="{_STROKE}" stroke-width="1.5"/>',
        _text_lines(12, 19, ["Modification du nom ou du domaine de l'ordinateur"], size=11.5, weight="700"),
        _text_lines(12, 46, ["Nom de l'ordinateur :"], size=11),
        f'<rect x="12" y="52" width="200" height="20" fill="#ffffff" stroke="{_STROKE}"/>',
        _text_lines(18, 66, [ws.name], size=11),
        _text_lines(12, 90, [f"Nom complet : {ws.name.lower()}.{DNS_DOMAIN}"], size=10.5),
        _text_lines(12, 112, ["Membre d'un"], size=11, weight="700"),
        f'<circle cx="22" cy="128" r="5" fill="#33415c" stroke="{_STROKE}"/>',
        _text_lines(34, 132, ["(•) Domaine :"], size=11),
        f'<rect x="120" y="120" width="200" height="20" fill="#ffffff" stroke="{_STROKE}"/>',
        _text_lines(126, 134, [DNS_DOMAIN], size=11),
        f'<circle cx="22" cy="156" r="5" fill="#ffffff" stroke="{_STROKE}"/>',
        _text_lines(34, 160, ["( ) Groupe de travail :"], size=11),
        _text_lines(180, 160, [WORKGROUP_DEFAULT], size=11),
        f'<rect x="230" y="176" width="64" height="22" rx="4" fill="{_SOFT}" stroke="{_STROKE}"/>',
        _text_lines(262, 191, ["OK"], size=11, weight="700", anchor="middle"),
        f'<rect x="302" y="176" width="68" height="22" rx="4" fill="{_SOFT}" stroke="{_STROKE}"/>',
        _text_lines(336, 191, ["Annuler"], size=11, anchor="middle"),
    ]
    notes = _wrap("OK demande ensuite le nom et le mot de passe d'un compte du domaine autorisé "
                  "(ex. DUPONT\\adm-tleroy), puis affiche « Bienvenue dans le domaine » ; redémarrage.", 60)
    parts.append(_text_lines(8, 226, notes, size=10.5, step=13))
    return _svg(width, 226 + 13 * len(notes), parts)


def groups_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Droits par les groupes : comptes → groupe → dossier et droit (fiche de groupes), puis
    imbrication des groupes du domaine dans les groupes locaux d'un poste joint. `blanks`
    (« g:<groupe> », « r:<groupe> », « l:<groupe du domaine> ») masque une valeur."""
    blanks = blanks or {}
    width = 380
    parts = [_text_lines(width // 2, 16, ["Les droits passent par les groupes"], size=12.5, weight="700", anchor="middle")]
    y = 28
    for group, members, rights in GROUP_SHEET[:3]:
        g = f"{blanks['g:' + group]} ?" if "g:" + group in blanks else group
        r = f"{blanks['r:' + group]} ?" if "r:" + group in blanks else rights
        hidden_g, hidden_r = "g:" + group in blanks, "r:" + group in blanks
        g_lines = _wrap(g, 16)
        parts.append(_box(4, y, 108, ["Comptes", *_wrap(members, 16)], fill=_SOFT))
        parts.append(f'<path d="M112 {y + 22} H124" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(_box(124, y, 120, ["Groupe", *g_lines], key="" if hidden_g else group, dashed=hidden_g))
        parts.append(f'<path d="M244 {y + 22} H256" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(_box(256, y, 120, ["Dossier : droit", *_wrap(r, 18)], fill="#ffffff" if hidden_r else "#e9f5ec",
                          dashed=hidden_r))
        y += 12 + 15 * max(1 + len(_wrap(members, 16)), 1 + len(_wrap(r, 18)), 1 + len(g_lines)) + 10
    y += 8
    parts.append(_text_lines(8, y, ["À la jonction, sur chaque poste du domaine :"], size=11, weight="700"))
    y += 10
    for dom, local in LOCAL_NESTING:
        key = "l:" + dom
        shown = f"{blanks[key]} ?" if key in blanks else local
        parts.append(_box(4, y, 372, [f"{NETBIOS_DOMAIN}\\{dom}", f"→ devient membre du groupe local {shown}"],
                          key="" if key in blanks else local, dashed=key in blanks))
        y += 48
    notes = _wrap("Arrivée ou départ d'une personne : on change ses groupes, jamais les droits des dossiers. "
                  "Un ajout à un groupe compte à la prochaine ouverture de session.", 60)
    parts.append(_text_lines(8, y + 10, notes, size=10.5, step=13))
    return _svg(width, y + 10 + 13 * len(notes), parts)


def accounts_bars_svg(counts: tuple[tuple[int, int, int], ...]) -> str:
    """Barres horizontales : comptes à gérer en groupe de travail et en domaine pour chaque
    taille d'organisation ; la valeur est écrite au bout de chaque barre."""
    width, left, bar_max = 380, 86, 118
    top_value = max(max(wg, dom) for _n, wg, dom in counts)
    parts = [_text_lines(width // 2, 16, ["Comptes à créer et à tenir à jour"], size=12.5, weight="700", anchor="middle")]
    y = 30
    for people, wg, dom in counts:
        parts.append(_text_lines(6, y + 12, [f"{people}", "personnes"], size=10.5, weight="700", step=12))
        for label, value, fill in (("groupe de travail", wg, "#f2c4c0"), ("domaine", dom, "#bfe3c8")):
            w = max(2.0, bar_max * value / top_value)
            parts.append(f'<rect data-bar="{people}-{label}" data-value="{value}" x="{left}" y="{y}" width="{w:.1f}" '
                         f'height="13" fill="{fill}" stroke="{_STROKE}" stroke-width="1"/>')
            parts.append(_text_lines(int(left + w + 4), y + 11, [f"{value} comptes ({label})"], size=10))
            y += 16
        y += 10
    notes = _wrap("Organisation type : chacun a son poste, tout le monde ouvre le dossier commun d'un poste, "
                  "une personne sur quatre utilise un second poste. Domaine : un compte par personne.", 60)
    parts.append(_text_lines(8, y + 6, notes, size=10.5, step=13))
    return _svg(width, y + 6 + 13 * len(notes), parts)


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte fictive, ligne par ligne : " + " / ".join(line.strip() for line in lines if line.strip())


def _wg_alt(accounts: dict[str, tuple[str, ...]], blanks: dict[str, str] | None = None) -> str:
    blanks = blanks or {}
    pieces = [
        f"{pc}{' (partage le dossier Commun)' if pc == WG_SHARE_PC else ''} : "
        + (f"liste {blanks[pc]} à compléter" if pc in blanks else "comptes locaux " + ", ".join(names))
        for pc, names in accounts.items()
    ]
    return ("Groupe de travail WORKGROUP, sans serveur : quatre postes reliés par un switch. Chaque poste a sa "
            "propre liste de comptes locaux. " + " ; ".join(pieces) + ".")


WORKGROUP_FIGURE = Figure(
    key="pr22-groupe-de-travail",
    title="Groupe de travail : chaque poste a ses propres comptes",
    alt=_wg_alt(WG_ACCOUNTS) + " Marc travaille sur PC-4 et PC-2 ; tout le monde ouvre le partage de PC-1.",
    caption=(f"{count_accounts(WG_ACCOUNTS)} comptes locaux pour {len(WG_USERS)} personnes : chacun sur ses postes, "
             "et tout le monde sur PC-1 qui partage le dossier."),
    svg=workgroup_svg(WG_ACCOUNTS, share_pc=WG_SHARE_PC),
)

DOMAIN_HOSTS: tuple[Workstation, ...] = (
    Workstation("PC-01", "192.168.20.11", (DC_IP,)),
    Workstation("PC-02", "192.168.20.12", (DC_IP,)),
    PC_OK,
)


def _domain_alt(hosts: tuple[Workstation, ...], hidden: dict[str, str] | None = None) -> str:
    hidden = hidden or {}

    def v(key: str, text: str) -> str:
        return f"{hidden[key]} à compléter" if key in hidden else text

    return (
        f"Domaine {DNS_DOMAIN} en étoile autour d'un switch : la box {BOX_IP} (passerelle vers Internet) ; le "
        f"serveur {DC_NAME}, rôle {v('role', 'contrôleur de domaine et serveur DNS')}, adresse fixe "
        f"{v('dc_ip', DC_IP)}/24, qui garde comptes, groupes et stratégies ; puis les postes membres du domaine : "
        + " ; ".join(f"{h.name} {h.ip}/24, DNS {v(h.name + ':dns', ', '.join(h.dns))}, passerelle "
                     f"{v(h.name + ':passerelle', h.gateway or 'vide')}" for h in hosts)
        + "."
    )


DOMAIN_FIGURE = Figure(
    key="pr22-domaine",
    title=f"Domaine {DNS_DOMAIN} : contrôleur, DNS et postes membres",
    alt=_domain_alt(DOMAIN_HOSTS),
    caption="Le contrôleur garde les comptes et sert de DNS ; les postes l'interrogent ; la box reste la passerelle.",
    svg=domain_svg(DOMAIN_HOSTS),
)

NAMES_FIGURE = Figure(
    key="pr22-noms-du-domaine",
    title="Domaine DNS, nom NetBIOS et noms de connexion",
    alt="Fiche des noms du domaine : " + " ; ".join(f"{label} : {value}" for label, value in NAME_ROWS) + ".",
    caption="Un seul domaine d'administration, plusieurs noms : DNS (complet), NetBIOS (court), UPN et forme locale.",
    svg=names_svg(),
)

JOIN_DIALOG_FIGURE = Figure(
    key="pr22-fenetre-jonction",
    title=f"Joindre {PC_OK.name} au domaine {DNS_DOMAIN}",
    alt=(
        "Fenêtre fictive « Modification du nom ou du domaine de l'ordinateur » : nom de l'ordinateur "
        f"{PC_OK.name}, nom complet {PC_OK.name.lower()}.{DNS_DOMAIN} ; « Membre d'un » : Domaine coché, "
        f"{DNS_DOMAIN} saisi ; Groupe de travail ({WORKGROUP_DEFAULT}) non coché ; boutons OK et Annuler."
    ),
    caption="Système → Informations système → Domaine ou groupe de travail → Modifier (ou sysdm.cpl). Fenêtre fictive simplifiée.",
    svg=join_dialog_svg(PC_OK),
)

JOIN_CONSOLE_FIGURE = Figure(
    key="pr22-jonction-console",
    title="Jonction en PowerShell puis contrôle de la session",
    alt=_screen_alt(JOIN_OK_LINES),
    caption="Après redémarrage : la session est celle du domaine et contient les groupes de Julie. Capture fictive simplifiée.",
    svg=screen_svg(JOIN_OK_LINES, label=FICTIVE_LABEL),
)

GROUPS_FIGURE = Figure(
    key="pr22-groupes",
    title="Fiche des groupes : des comptes aux droits",
    alt=(
        "Trois chaînes comptes → groupe → dossier et droit : "
        + " ; ".join(f"{members} → groupe {group} → {rights}" for group, members, rights in GROUP_SHEET[:3])
        + ". À la jonction, sur chaque poste : "
        + " ; ".join(f"{NETBIOS_DOMAIN}\\{dom} devient membre du groupe local {local}" for dom, local in LOCAL_NESTING)
        + "."
    ),
    caption="Droits donnés aux groupes, personnes placées dans les groupes ; les administrateurs du domaine administrent chaque poste.",
    svg=groups_svg(),
)

BARS_FIGURE = Figure(
    key="pr22-comptes-a-gerer",
    title="Combien de comptes gérer : groupe de travail ou domaine",
    alt=(
        "Barres comparant le nombre de comptes à créer : "
        + " ; ".join(f"{n} personnes : {wg} comptes locaux en groupe de travail, {dom} comptes en domaine"
                     for n, wg, dom in ACCOUNT_COUNTS)
        + "."
    ),
    caption="En groupe de travail, le nombre de comptes grandit plus vite que le nombre de personnes. Organisation type calculée.",
    svg=accounts_bars_svg(ACCOUNT_COUNTS),
)

LOGON_TREE_QUESTIONS: tuple[tuple[str, str], ...] = tuple((what, diag) for _k, what, diag in LOGON_CHECKS)
LOGON_TREE_FINAL = "Tous les contrôles réussissent : session ouverte, accès conforme à la fiche des groupes."

LOGON_TREE_FIGURE = Figure(
    key="pr22-arbre-session",
    title="Ouverture de session ou accès refusé : contrôle par contrôle",
    alt=(
        "Arbre de décision : "
        + " ; ".join(f"{i}. {q} ? Si non : {d}" for i, (q, d) in enumerate(LOGON_TREE_QUESTIONS, start=1))
        + f". Si tout est oui : {LOGON_TREE_FINAL}"
    ),
    caption="Le premier contrôle en échec désigne la piste : inutile de réinitialiser un mot de passe si le DNS est faux.",
    svg=decision_tree_svg(LOGON_TREE_QUESTIONS, LOGON_TREE_FINAL),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


JOIN_PROC_FIGURE = _proc_figure("pr22-procedure-jonction", 1, PROCEDURES[0][0], JOIN_STEPS,
                                "Le DNS et l'heure se règlent avant la jonction, pas après l'échec.")
LIFECYCLE_PROC_FIGURE = _proc_figure("pr22-procedure-compte", 2, PROCEDURES[1][0], LIFECYCLE_STEPS,
                                     "Un compte par personne, des droits par les groupes, une désactivation le jour du départ.")
TROUBLE_PROC_FIGURE = _proc_figure("pr22-procedure-depannage", 3, PROCEDURES[2][0], TROUBLE_STEPS,
                                   "Du réseau aux droits : on s'arrête au premier contrôle en échec.")

PR22_FIGURES: tuple[Figure, ...] = (
    WORKGROUP_FIGURE,
    BARS_FIGURE,
    DOMAIN_FIGURE,
    NAMES_FIGURE,
    JOIN_DIALOG_FIGURE,
    JOIN_CONSOLE_FIGURE,
    GROUPS_FIGURE,
    LOGON_TREE_FIGURE,
    JOIN_PROC_FIGURE,
    LIFECYCLE_PROC_FIGURE,
    TROUBLE_PROC_FIGURE,
)

# =============================================================================================
# 9. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

DOMAIN_BLANKS: dict[str, str] = {"role": "①", "dc_ip": "②", "PC-03:dns": "③", "PC-03:passerelle": "④"}
DOMAIN_BLANK_ANSWERS: dict[str, str] = {
    "①": "Contrôleur de domaine (Active Directory) et serveur DNS du domaine",
    "②": f"Adresse fixe, par exemple {DC_IP}/24 (jamais en DHCP)",
    "③": f"{DC_IP} : le contrôleur, seul DNS du poste",
    "④": f"{BOX_IP} : la box reste la passerelle",
}

DOMAIN_BLANK_FIGURE = Figure(
    key="pr22-domaine-a-completer",
    title="Domaine à compléter",
    alt=_domain_alt(DOMAIN_HOSTS, DOMAIN_BLANKS),
    caption="Schéma à compléter : rôle ① et adresse ② du serveur, DNS ③ et passerelle ④ de PC-03.",
    svg=domain_svg(DOMAIN_HOSTS, blanks=DOMAIN_BLANKS),
)

NAMES_BLANKS: dict[int, str] = {1: "①", 3: "②", 4: "③", 5: "④"}
NAMES_BLANK_ANSWERS: dict[str, str] = {NAMES_BLANKS[i]: NAME_ROWS[i][1] for i in NAMES_BLANKS}

NAMES_BLANK_FIGURE = Figure(
    key="pr22-noms-a-completer",
    title="Noms du domaine à compléter",
    alt=(
        "Fiche des noms du domaine : "
        + " ; ".join(f"{label} : " + (f"{NAMES_BLANKS[i]} à compléter" if i in NAMES_BLANKS else value)
                     for i, (label, value) in enumerate(NAME_ROWS))
        + "."
    ),
    caption="Schéma à compléter : nom NetBIOS ①, nom complet du poste ②, deux formes de connexion ③ et ④.",
    svg=names_svg(blanks=NAMES_BLANKS),
)

WG_BLANKS: dict[str, str] = {"PC-1": "①", "PC-2": "②"}
WG_BLANK_ANSWERS: dict[str, str] = {WG_BLANKS[pc]: ", ".join(WG_ACCOUNTS[pc]) for pc in WG_BLANKS}

WG_BLANK_FIGURE = Figure(
    key="pr22-groupe-de-travail-a-completer",
    title="Groupe de travail : comptes à compléter",
    alt=_wg_alt(WG_ACCOUNTS, WG_BLANKS)
    + " Marc travaille sur PC-4 et PC-2 ; tout le monde (anne, paul, sara, marc) ouvre le partage de PC-1.",
    caption="Schéma à compléter : comptes locaux à créer sur PC-1 ① et PC-2 ②.",
    svg=workgroup_svg(WG_ACCOUNTS, share_pc=WG_SHARE_PC, blanks=WG_BLANKS),
)

GROUPS_BLANKS: dict[str, str] = {"g:G_Compta": "①", "r:G_Direction": "②", "l:" + ADMINS_DOMAIN: "③",
                                 "l:" + USERS_DOMAIN: "④"}
GROUPS_BLANK_ANSWERS: dict[str, str] = {
    "①": "G_Compta (groupe métier de la comptabilité)",
    "②": "Direction : Modification ; Compta : Lecture",
    "③": LOCAL_ADMINS,
    "④": LOCAL_USERS,
}

GROUPS_BLANK_FIGURE = Figure(
    key="pr22-groupes-a-completer",
    title="Fiche des groupes à compléter",
    alt=(
        "Trois chaînes comptes → groupe → dossier et droit : Comptabilité (jmartin, lbernard) → groupe ① à "
        "compléter → Compta : Modification ; Direction (cdupont) → groupe G_Direction → droits ② à compléter ; "
        f"tous les comptes du domaine → groupe {USERS_DOMAIN} → Commun : Modification. À la jonction : "
        f"{NETBIOS_DOMAIN}\\{ADMINS_DOMAIN} devient membre du groupe local ③ ; {NETBIOS_DOMAIN}\\{USERS_DOMAIN} "
        "devient membre du groupe local ④."
    ),
    caption="Schéma à compléter : groupe ①, droits ②, groupes locaux ③ et ④.",
    svg=groups_svg(blanks=GROUPS_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (DOMAIN_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr22-domaine-a-completer.svg"),
    (NAMES_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr22-noms-a-completer.svg"),
    (WG_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr22-groupe-de-travail-a-completer.svg"),
    (GROUPS_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr22-groupes-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18/PR21)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


def all_capture_lines() -> tuple[str, ...]:
    """Toutes les lignes de captures des figures (contrôle de largeur par les tests)."""
    return JOIN_OK_LINES

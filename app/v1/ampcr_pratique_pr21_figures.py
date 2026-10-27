"""PR21 « Connexion directe de deux PC et mini-réseau » — données de référence, calculs,
relevés de commandes fictifs et schémas SVG (ticket #221).

Tout est construit **depuis des données** de ce module, contrôlées par
`tests/test_ticket221_ampcr_pratique_pr21.py` (qui recalcule indépendamment) :

- type de port (MDI / MDI-X), câble droit ou croisé, Auto MDI-X : `port_kind`,
  `cable_needed`, `link_up` ; le brochage du câble croisé vient de PR15 (`links_between`) ;
- connexion directe de référence : `PC_A` 192.168.10.1/24 et `PC_B` 192.168.10.2/24, sans
  passerelle ni DNS (modèle d'adressage de PR20 : `Host`, `same_subnet`, `host_errors`) ;
- résultat d'un ping selon le lien, l'adressage des deux postes, le poste distant et son
  pare-feu (`ping_outcome`) et relevés fictifs correspondants (`ping_lines`, `arp_lines` de
  PR24, `ipconfig_all_lines` de PR20, `ipconfig_disconnected_lines`,
  `ipconfig_duplicate_lines`) ;
- mini-réseau de 3 à 6 PC : version isolée (switch seul, adresses fixes) et version avec box
  (passerelle, DNS, étendue DHCP), contrôlées par `plan_errors` de PR20 ; carte des adresses
  (`ADDRESS_RANGES`, `range_of`) ;
- diagnostic dans l'ordre (`CHECKS`, `validation_diagnosis`, `first_failure`, arbre de
  décision) et trois procédures illustrées (`DIRECT_STEPS`, `EXTEND_STEPS`, `ACCEPT_STEPS`) ;
- quatre schémas à compléter servis aussi en fichiers statiques (`STATIC_FIGURES`).

Valeurs de référence : IEEE 802.3 (10BASE-T et 100BASE-TX sur les paires 1-2 et 3-6,
1000BASE-T sur les quatre paires ; Auto MDI-X : la carte inverse elle-même émission et
réception, il suffit qu'un des deux ports le fasse) ; RFC 1918 (adresses privées), RFC 3927
(169.254.0.0/16, adresse automatique sans serveur DHCP), RFC 5737 (adresse publique de
documentation). Messages Windows en français, Linux en anglais : **captures fictives
simplifiées** au format réel, 56 caractères par ligne au plus (lisibles sur mobile).

**Conventions du cours**, signalées dans le texte : réseau 192.168.10.0/24 ; la box en
.254 (garde .1 et .2 de la connexion directe) ; adresses fixes des postes de .1 à .19, des
imprimantes et équipements de .20 à .49, étendue DHCP de .100 à .199. Les postes, MAC et
entreprises sont **fictifs**. Chaque schéma porte son information en texte : la couleur n'est
qu'un repère. Aucun schéma ne vient d'une image générée ni d'une photographie.
"""

import ipaddress
from html import escape

from app.v1.ampcr_pratique_pr15_figures import links_between
from app.v1.ampcr_pratique_pr20_figures import (
    KIND_LINK_LOCAL,
    AddressPlan,
    Host,
    address_kind,
    host_errors,
    ipconfig_all_lines,
    ipv4_dialog_svg,
    is_local_for,
    normalize_mac,
    plan_errors,
    same_subnet,
)
from app.v1.ampcr_pratique_pr24_figures import arp_lines, ping_stats
from app.v1.ampcr_pratique_visuals import (
    T568A,
    T568B,
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
_BAD = "#b3261e"

__all__ = [  # réexports utilisés par le cours et la banque
    "AddressPlan",
    "Host",
    "address_kind",
    "arp_lines",
    "host_errors",
    "ipconfig_all_lines",
    "normalize_mac",
    "ping_stats",
    "plan_errors",
    "same_subnet",
]

# =============================================================================================
# 1. Ports MDI / MDI-X, câble droit ou croisé, Auto MDI-X
# =============================================================================================

MDI = "MDI"  # carte réseau : émet sur 1-2, reçoit sur 3-6 (10/100 Mb/s)
MDIX = "MDI-X"  # port de switch ou de hub : émission et réception déjà inversées

# Type de port de chaque appareil (sans Auto MDI-X).
PORT_KINDS: dict[str, str] = {
    "PC": MDI,
    "Portable": MDI,
    "Serveur": MDI,
    "Imprimante réseau": MDI,
    "Routeur (port routé)": MDI,
    "Switch": MDIX,
    "Hub": MDIX,
    "Box (ports LAN du switch intégré)": MDIX,
}

CABLE_STRAIGHT = "Câble droit"
CABLE_CROSS = "Câble croisé"
CABLE_ANY = "Droit ou croisé (Auto MDI-X)"
CABLE_CHOICES = (CABLE_STRAIGHT, CABLE_CROSS, CABLE_ANY)


def port_kind(device: str) -> str:
    return PORT_KINDS[device]


def cable_needed(a: str, b: str, *, auto_a: bool = False, auto_b: bool = False) -> str:
    """Câble à utiliser entre deux appareils. Un seul port Auto MDI-X suffit : il inverse
    lui-même émission et réception. Sinon : deux ports de même type → croisé, de types
    différents → droit."""
    if auto_a or auto_b:
        return CABLE_ANY
    return CABLE_CROSS if port_kind(a) == port_kind(b) else CABLE_STRAIGHT


def link_up(cable: str, a: str, b: str, *, auto_a: bool = False, auto_b: bool = False) -> bool:
    """Le lien s'établit-il avec ce câble (droit ou croisé, en bon état) ?"""
    if cable not in (CABLE_STRAIGHT, CABLE_CROSS):
        raise ValueError(cable)
    needed = cable_needed(a, b, auto_a=auto_a, auto_b=auto_b)
    return needed == CABLE_ANY or needed == cable


# Câble croisé historique : T568A à un bout, T568B à l'autre (brochage de PR15).
CROSSOVER_LINKS = links_between(T568A, T568B)
STRAIGHT_LINKS = tuple((p, p) for p in range(1, 9))

# Paires utilisées : 10BASE-T et 100BASE-TX sur 1-2 et 3-6 ; 1000BASE-T sur les quatre.
PAIRS_USED: dict[str, tuple[tuple[int, int], ...]] = {
    "10/100 Mb/s": ((1, 2), (3, 6)),
    "1 Gb/s": ((1, 2), (3, 6), (4, 5), (7, 8)),
}

# Liaisons du tableau « droit ou croisé » : (appareil A, appareil B)
CABLE_PAIRS: tuple[tuple[str, str], ...] = (
    ("PC", "PC"),
    ("PC", "Switch"),
    ("Switch", "Switch"),
    ("PC", "Routeur (port routé)"),
    ("PC", "Box (ports LAN du switch intégré)"),
    ("Switch", "Hub"),
)

# Voyants de la carte et du port : ce que chaque état prouve.
LED_STATES: tuple[tuple[str, str, str], ...] = (
    ("Voyant de lien éteint", "Aucun lien électrique négocié",
     "câble débranché ou coupé, carte désactivée, PC distant éteint, câble droit entre deux cartes sans Auto MDI-X"),
    ("Voyant de lien allumé fixe", "Lien établi, aucune trame en ce moment",
     "lire la vitesse négociée (ipconfig, Paramètres, ethtool)"),
    ("Voyant d'activité qui clignote", "Des trames passent",
     "ce n'est pas encore la preuve que l'adressage est bon"),
    ("Lien à 100 Mb/s sur deux cartes 1 Gb/s", "Seules deux paires fonctionnent",
     "paire coupée ou câble ancien à deux paires : tester le câble (PR15)"),
)

# =============================================================================================
# 2. Connexion directe de référence (adressage statique, sans passerelle)
# =============================================================================================

DIRECT_NETWORK = "192.168.10.0/24"
PC_A = Host("PC-A", "poste fixe, partage le dossier", "192.168.10.1", 24, None, (), "3C-52-82-4D-10-01")
PC_B = Host("PC-B", "portable du technicien", "192.168.10.2", 24, None, (), "A4-C3-F0-12-34-02")
SHARE_NAME = "Echange"
SHARE_PATH = "C:\\Echange"
SHARE_UNC = f"\\\\{PC_A.ip}\\{SHARE_NAME}"
SHARE_UNC_NAME = f"\\\\{PC_A.name}\\{SHARE_NAME}"
SHARE_PORT = 445  # SMB


def same_network(a: Host, b: Host) -> bool:
    """Les deux postes se voient-ils dans le même réseau, chacun avec son propre masque ?"""
    return is_local_for(a.ip, a.prefix, b.ip) and is_local_for(b.ip, b.prefix, a.ip)


def direct_errors(a: Host, b: Host) -> list[str]:
    """Erreurs d'une connexion directe : erreurs de chaque poste (PR20), doublon, réseau ou
    masque différents. Une passerelle n'est pas une erreur, mais elle est inutile."""
    errors = host_errors(a) + host_errors(b)
    if a.ip == b.ip:
        errors.append(f"{a.name} et {b.name} : même adresse {a.ip} (doublon).")
    elif not same_network(a, b):
        errors.append(
            f"{a.name} ({a.ip}/{a.prefix}) et {b.name} ({b.ip}/{b.prefix}) ne sont pas dans le même réseau."
        )
    return errors


# =============================================================================================
# 3. Résultat d'un ping et relevés fictifs
# =============================================================================================

OUT_REPLY = "Réponse : le poste distant répond"
OUT_TIMEOUT = "Délai dépassé : la demande part, aucune réponse ne revient"
OUT_UNREACHABLE = "Hôte inaccessible : personne ne répond à la requête ARP"
OUT_FAILURE = "Défaillance générale : aucune route pour émettre"
PING_OUTCOMES = (OUT_REPLY, OUT_TIMEOUT, OUT_UNREACHABLE, OUT_FAILURE)


def ping_outcome(src: Host, dst_ip: str, dst: Host | None, *, link: bool = True, dst_on: bool = True,
                 icmp_allowed: bool = True) -> str:
    """Ce qu'affiche `ping dst_ip` lancé depuis `src`, dans un réseau local sans routeur
    (connexion directe ou switch). `dst` est le poste qui possède réellement l'adresse
    visée (None : personne)."""
    if not link:
        return OUT_FAILURE  # carte déconnectée : plus aucune route
    if not is_local_for(src.ip, src.prefix, dst_ip):
        if src.gateway is None:
            return OUT_FAILURE  # destination hors réseau et aucune passerelle
        raise ValueError("Hors modèle : la demande passerait par un routeur.")
    if dst is None or not dst_on or dst.ip != dst_ip:
        return OUT_UNREACHABLE
    if not is_local_for(dst.ip, dst.prefix, src.ip):
        if dst.gateway is None:
            return OUT_TIMEOUT  # le destinataire reçoit mais ne sait pas répondre
        raise ValueError("Hors modèle : la réponse passerait par un routeur.")
    if not icmp_allowed:
        return OUT_TIMEOUT
    return OUT_REPLY


def _ping_head(target: str) -> list[str]:
    return [f"C:\\> ping {target}", f"Envoi d'une requête 'Ping' {target}", "avec 32 octets de données :"]


def _ping_stats(target: str, sent: int, received: int) -> list[str]:
    lost = sent - received
    return [
        f"Statistiques Ping pour {target}:",
        f"  Paquets : envoyés = {sent}, reçus = {received},",
        f"  perdus = {lost} (perte {round(100 * lost / sent)}%),",
    ]


def ping_lines(src: Host, target: str, outcome: str, *, count: int = 4, ttl: int = 128) -> tuple[str, ...]:
    """Sortie Windows de `ping` (4 échos) pour un résultat de `ping_outcome`. Comme le vrai
    Windows, « Impossible de joindre l'hôte de destination » est compté comme reçu : la
    réponse vient du poste lui-même (0 % de perte, mais aucun écho du destinataire)."""
    lines = _ping_head(target)
    if outcome == OUT_REPLY:
        lines += [f"Réponse de {target} : octets=32 temps<1ms TTL={ttl}"] * count
        lines += _ping_stats(target, count, count)
    elif outcome == OUT_TIMEOUT:
        lines += ["Délai d'attente de la demande dépassé."] * count
        lines += _ping_stats(target, count, 0)
    elif outcome == OUT_UNREACHABLE:
        lines += [f"Réponse de {src.ip} : Impossible de joindre", "  l'hôte de destination."] * count
        lines += _ping_stats(target, count, count)
    elif outcome == OUT_FAILURE:
        lines = [lines[0], *["PING : échec de la transmission. Défaillance générale."] * count]
        lines += _ping_stats(target, count, 0)
    else:
        raise ValueError(outcome)
    return tuple(lines)


def ipconfig_disconnected_lines(host: Host) -> tuple[str, ...]:
    """`ipconfig /all` quand la carte n'a aucun lien : plus d'adresse affichée."""
    return (
        "C:\\> ipconfig /all",
        "",
        "Carte Ethernet Ethernet :",
        "   Statut du média. . : Média déconnecté",
        "   Description. . . . : Contrôleur Ethernet",
        f"   Adresse physique . : {normalize_mac(host.mac)}",
        f"   DHCP activé. . . . : {'Oui' if host.dhcp else 'Non'}",
    )


def ipconfig_duplicate_lines(host: Host) -> tuple[str, ...]:
    """`ipconfig /all` d'un poste dont l'adresse fixe est déjà utilisée sur le réseau :
    Windows la marque « (Dupliqué) » et ne s'en sert pas."""
    return (
        "C:\\> ipconfig /all",
        "",
        "Carte Ethernet Ethernet :",
        f"   Adresse physique . : {normalize_mac(host.mac)}",
        "   DHCP activé. . . . : Non",
        f"   Adresse IPv4 . . . : {host.ip}(Dupliqué)",
        f"   Masque de s.-réseau: {host.mask}",
        f"   Passerelle défaut. : {host.gateway or ''}".rstrip(),
    )


def ipconfig_static_lines(host: Host) -> tuple[str, ...]:
    return ("C:\\> ipconfig /all", "", *ipconfig_all_lines(host, dhcp_server=None))


# Relevés de la connexion directe de référence
PING_OK_LINES = ping_lines(PC_A, PC_B.ip, ping_outcome(PC_A, PC_B.ip, PC_B))
ARP_OK_LINES = arp_lines(PC_A.ip, ((PC_B.ip, PC_B.mac),))
PING_FIREWALL_LINES = ping_lines(PC_B, PC_A.ip, ping_outcome(PC_B, PC_A.ip, PC_A, icmp_allowed=False))
ARP_FIREWALL_LINES = arp_lines(PC_B.ip, ((PC_A.ip, PC_A.mac),))

# Pare-feu Windows : réseau sans passerelle = « réseau non identifié », profil Public.
FIREWALL_STEPS: tuple[tuple[str, str], ...] = (
    ("Profil du réseau", ("Paramètres → Réseau et Internet → Ethernet → Type de profil réseau : Privé "
     "(PowerShell administrateur : Set-NetConnectionProfile -InterfaceAlias Ethernet -NetworkCategory Private).")),
    ("Partage et réponse au ping", ("Paramètres de partage avancés, profil Privé : découverte du réseau et "
     "« Partage de fichiers et d'imprimantes » activés ; cela active aussi la règle entrante « Demande d'écho ICMPv4 ».")),
    ("Ne pas couper le pare-feu", "On ouvre la règle nécessaire sur le profil Privé ; on ne désactive pas le pare-feu."),
)

# =============================================================================================
# 4. Mini-réseau de 3 à 6 PC
# =============================================================================================

MINI_NETWORK = DIRECT_NETWORK
BOX_IP = "192.168.10.254"
POOL = ("192.168.10.100", "192.168.10.199")
WAN_IP = "203.0.113.45"  # adresse publique de la box (RFC 5737, fictive)

# Version isolée : switch seul, adresses fixes, pas de passerelle (aucun accès à Internet).
ISOLATED_HOSTS: tuple[Host, ...] = (
    PC_A,
    PC_B,
    Host("PC-C", "poste de l'accueil", "192.168.10.3", 24, None, (), "3C-52-82-4D-10-03"),
    Host("PC-D", "poste de la comptable", "192.168.10.4", 24, None, (), "3C-52-82-4D-10-04"),
    Host("PC-E", "poste du gérant (Linux)", "192.168.10.5", 24, None, (), "52-54-00-6B-21-05"),
)

# Version avec box : passerelle et DNS = box ; DHCP pour les postes mobiles ; fixes hors étendue.
BOX = Host("BOX", "box : passerelle, DNS, DHCP", BOX_IP, 24, None, (), "00-1D-AA-7E-10-FE")
FIXED_A = Host("PC-A", "poste fixe, partage le dossier", "192.168.10.1", 24, BOX_IP, (BOX_IP,), PC_A.mac)
PRINTER = Host("IMP-01", "imprimante réseau", "192.168.10.20", 24, BOX_IP, (BOX_IP,), "00-80-77-31-AB-20")
BOX_HOSTS: tuple[Host, ...] = (
    BOX,
    FIXED_A,
    PRINTER,
    Host("PC-B", "portable du technicien", "192.168.10.100", 24, BOX_IP, (BOX_IP,), PC_B.mac, dhcp=True),
    Host("PC-C", "poste de l'accueil", "192.168.10.101", 24, BOX_IP, (BOX_IP,), "3C-52-82-4D-10-03", dhcp=True),
    Host("PC-D", "poste de la comptable", "192.168.10.102", 24, BOX_IP, (BOX_IP,), "3C-52-82-4D-10-04", dhcp=True),
    Host("PC-E", "poste du gérant (Linux)", "192.168.10.103", 24, BOX_IP, (BOX_IP,), "52-54-00-6B-21-05", dhcp=True),
)
BOX_PLAN = AddressPlan(MINI_NETWORK, BOX_HOSTS, BOX_IP, BOX_IP, POOL)
ISOLATED_PLAN_ERRORS = [
    e for a in ISOLATED_HOSTS for b in ISOLATED_HOSTS if a.name < b.name for e in direct_errors(a, b)
]

# Carte des adresses du réseau 192.168.10.0/24 (convention du cours) : (première, dernière, usage)
ADDRESS_RANGES: tuple[tuple[int, int, str], ...] = (
    (1, 19, "Postes et serveur à adresse fixe"),
    (20, 49, "Imprimantes et équipements à adresse fixe"),
    (50, 99, "Libre (réserve)"),
    (100, 199, "Étendue DHCP de la box"),
    (200, 253, "Libre (réserve)"),
    (254, 254, "Box : passerelle et DNS"),
)


def range_of(address: str) -> str:
    """Usage prévu pour une adresse du réseau 192.168.10.0/24 d'après la carte des adresses."""
    ip = ipaddress.IPv4Address(address)
    if ip not in ipaddress.IPv4Network(MINI_NETWORK) or int(ip) & 0xFF in (0, 255):
        raise ValueError(f"{address} n'est pas une adresse d'hôte de {MINI_NETWORK}.")
    last = int(ip) & 0xFF
    for first, end, label in ADDRESS_RANGES:
        if first <= last <= end:
            return label
    raise AssertionError(address)


DHCP_VS_STATIC: tuple[tuple[str, str, str], ...] = (
    ("Adresse fixe (statique)", "Saisie à la main sur l'appareil : adresse, masque, passerelle, DNS",
     "serveur, NAS, imprimante, box, connexion directe sans serveur DHCP ; hors de l'étendue DHCP"),
    ("DHCP (automatique)", "Reçue du serveur DHCP (la box) au démarrage, avec masque, passerelle et DNS",
     "postes et portables d'un réseau qui a une box ; aucun doublon si personne n'empiète sur l'étendue"),
    ("Réservation DHCP", "Le serveur DHCP donne toujours la même adresse à une MAC donnée",
     "imprimante ou NAS quand on préfère tout gérer depuis la box"),
)

# =============================================================================================
# 5. Diagnostic et recette dans l'ordre
# =============================================================================================

D_LINK = "Liaison : câble, type de câble, carte ou poste distant"
D_DHCP = "DHCP : aucune adresse reçue (169.254.x.x)"
D_DUP = "Adresse IP dupliquée"
D_PLAN = "Plan d'adressage : réseau ou masque différents"
D_PEER = "Poste distant : éteint ou mauvaise adresse visée"
D_FIREWALL = "Pare-feu du poste distant (profil, règle ICMP)"
D_SHARE = "Partage : chemin, compte ou permissions"
D_GW = "Internet : passerelle ou DNS absents ou faux"
D_OK = "Réseau validé"
DIAGNOSES = (D_LINK, D_DHCP, D_DUP, D_PLAN, D_PEER, D_FIREWALL, D_SHARE, D_GW)

# (clé, contrôle, diagnostic si c'est le premier contrôle en échec), dans l'ordre de la recette
CHECKS: tuple[tuple[str, str, str], ...] = (
    ("lien", "Voyant de lien allumé ; pas de « Média déconnecté »", D_LINK),
    ("adresse", "ipconfig : l'adresse n'est pas une 169.254.x.x", D_DHCP),
    ("doublon", "ipconfig : pas de « (Dupliqué) »", D_DUP),
    ("reseau", "Même réseau et même masque que l'autre poste", D_PLAN),
    ("arp", "La MAC de l'autre poste apparaît dans arp -a", D_PEER),
    ("ping", "Le ping reçoit des réponses du poste visé", D_FIREWALL),
    ("partage", "Le dossier partagé s'ouvre avec le bon compte", D_SHARE),
    ("internet", "Un site s'ouvre par son nom (si une box est prévue)", D_GW),
)
CHECK_KEYS = tuple(k for k, _w, _d in CHECKS)


def validation_diagnosis(results: dict[str, bool]) -> str:
    """Le premier contrôle qui échoue désigne la piste ; les suivants ne prouvent rien tant
    qu'il n'est pas réglé."""
    for key, _what, diagnosis in CHECKS:
        if not results[key]:
            return diagnosis
    return D_OK


def first_failure(failed: str) -> dict[str, bool]:
    """Résultats où tout réussit jusqu'au contrôle `failed`, qui échoue (les suivants aussi)."""
    index = CHECK_KEYS.index(failed)
    return {k: i < index for i, k in enumerate(CHECK_KEYS)}


def checks_from(src: Host, peer: Host, *, link: bool = True, duplicate: bool = False, peer_on: bool = True,
                icmp_allowed: bool = True, share_ok: bool = True, internet_ok: bool = True) -> dict[str, bool]:
    """Résultats des contrôles calculés depuis la configuration des deux postes (ARP et ping
    déduits de `ping_outcome`)."""
    outcome = ping_outcome(src, peer.ip, peer, link=link and not duplicate, dst_on=peer_on, icmp_allowed=icmp_allowed)
    return {
        "lien": link,
        "adresse": address_kind(src.ip) != KIND_LINK_LOCAL,
        "doublon": not duplicate,
        "reseau": same_network(src, peer),
        "arp": outcome in (OUT_REPLY, OUT_TIMEOUT),
        "ping": outcome == OUT_REPLY,
        "partage": share_ok,
        "internet": internet_ok,
    }


TREE_QUESTIONS: tuple[tuple[str, str], ...] = tuple((what, diagnosis) for _k, what, diagnosis in CHECKS)
TREE_FINAL = "Tous les contrôles réussissent : réseau validé, résultats consignés au procès-verbal."

# =============================================================================================
# 6. Procédures
# =============================================================================================

DIRECT_STEPS: tuple[tuple[str, str], ...] = (
    ("Vérifier le matériel", "Carte réseau de chaque PC, câble testé ; Auto MDI-X ou câble croisé."),
    ("Brancher et lire les voyants", "Voyant de lien allumé des deux côtés, vitesse négociée."),
    ("Adresser les deux PC", f"{PC_A.ip}/24 et {PC_B.ip}/24, sans passerelle ni DNS."),
    ("Régler le pare-feu", "Profil Privé, partage de fichiers et réponse au ping autorisés."),
    ("Tester", "ipconfig, ping dans les deux sens, arp -a."),
    ("Partager le dossier", f"Partage {SHARE_NAME}, compte et permissions ; accès {SHARE_UNC}."),
    ("Consigner", "Adresses, résultats des tests et réglages dans la fiche d'intervention."),
)

EXTEND_STEPS: tuple[tuple[str, str], ...] = (
    ("Recenser", "Postes, imprimante, partage, besoin d'Internet ; nombre de ports."),
    ("Choisir le switch", "Ports nécessaires + réserve ; un câble droit par appareil."),
    ("Établir le plan d'adressage", "Réseau, masque, adresses fixes, étendue DHCP, passerelle, DNS."),
    ("Raccorder", "Chaque appareil au switch ; la box au switch si Internet est prévu."),
    ("Configurer les postes", "DHCP ou adresse fixe selon le plan ; noms uniques ; même groupe de travail."),
    ("Valider chaque poste", "Lien, adresse, doublon, ping, partage, Internet ; corriger la première piste."),
)

ACCEPT_STEPS: tuple[tuple[str, str], ...] = tuple(
    (key.capitalize() if key not in ("reseau", "arp") else ("Réseau et masque" if key == "reseau" else "Table ARP"),
     what) for key, what, _d in CHECKS
) + (("Consigner et faire signer", "Tableau de recette par poste, réserves, procès-verbal signé."),)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Mettre en service une connexion directe entre deux PC", DIRECT_STEPS),
    ("Étendre la connexion à un mini-réseau de 3 à 6 PC", EXTEND_STEPS),
    ("Recette du mini-réseau, contrôle par contrôle", ACCEPT_STEPS),
)

# =============================================================================================
# 7. Schémas SVG
# =============================================================================================


def _pc_box(x: int, y: int, w: int, lines: list[str], *, key: str = "", dashed: bool = False) -> str:
    h = 12 + 15 * len(lines)
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    data = f' data-host="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{_FILL}" stroke="{_STROKE}" '
            f'stroke-width="1.5"{dash}/>'
            + _text_lines(x + 8, y + 17, lines[:1], size=12, weight="700")
            + _text_lines(x + 8, y + 32, lines[1:], size=10.5, step=15))


def direct_svg(a: Host, b: Host, *, blanks: dict[str, str] | None = None, cable: str = CABLE_ANY) -> str:
    """Deux PC reliés par un seul câble : configuration IPv4 de chacun (adresse, masque,
    passerelle, DNS), voyants de lien et câble. `blanks` remplace une valeur de PC-B
    (« ip », « masque », « passerelle ») ou le câble (« cable ») par un numéro à compléter."""
    blanks = blanks or {}
    width = 380

    def value(key: str, text: str) -> str:
        return f"{blanks[key]} ?" if key in blanks else text

    def lines(host: Host, right: bool) -> list[str]:
        if right:
            return [host.name, f"IP : {value('ip', host.ip)}", f"Masque : {value('masque', host.mask)}",
                    f"Passerelle : {value('passerelle', host.gateway or '(vide)')}", "DNS : (vide)",
                    f"MAC {host.mac}"]
        return [host.name, f"IP : {host.ip}", f"Masque : {host.mask}", f"Passerelle : {host.gateway or '(vide)'}",
                "DNS : (vide)", f"MAC {host.mac}"]

    parts = [
        _pc_box(4, 8, 168, lines(a, False), key=a.name),
        _pc_box(208, 8, 168, lines(b, True), key="" if blanks else b.name, dashed=bool(blanks)),
    ]
    y_cable = 134
    parts.append(f'<path data-cable="{"" if "cable" in blanks else escape(cable)}" d="M88 110 V{y_cable} H292 V110" '
                 f'fill="none" stroke="{_STROKE}" stroke-width="3"/>')
    for x in (88, 292):  # voyants de lien à côté de chaque prise
        parts.append(f'<circle data-led="lien" cx="{x + 14}" cy="118" r="5" fill="#2e8b57" stroke="{_STROKE}"/>')
    parts.append(_text_lines(190, y_cable + 18, [value("cable", cable)], size=11.5, weight="700", anchor="middle"))
    parts.append(_text_lines(190, y_cable + 34, ["un seul câble RJ45, sans switch"], size=10.5, anchor="middle"))
    notes = _wrap("Rond vert : voyant de lien allumé à côté de la prise de chaque carte. "
                  f"Réseau {DIRECT_NETWORK} isolé : aucune passerelle ni DNS n'est nécessaire.", 60)
    parts.append(_text_lines(8, y_cable + 58, notes, size=10.5, step=13))
    return _svg(width, y_cable + 58 + 13 * len(notes), parts)


def cable_table_svg(rows: tuple[tuple[str, str, bool, bool], ...], *, blanks: dict[int, str] | None = None,
                    title: str = "Quel câble entre deux appareils ?") -> str:
    """Une ligne par liaison : appareils, Auto MDI-X de chaque port, câble à utiliser (calculé
    par `cable_needed`). `blanks` (index de ligne → numéro) masque le câble à trouver."""
    blanks = blanks or {}
    width, row_h, top = 380, 40, 46
    parts = [
        _text_lines(width // 2, 16, [title], size=12, weight="700", anchor="middle"),
        _text_lines(10, 36, ["Liaison (Auto MDI-X : oui / non)"], size=10, weight="700"),
        _text_lines(372, 36, ["Câble"], size=10, weight="700", anchor="end"),
    ]
    for index, (a, b, auto_a, auto_b) in enumerate(rows):
        y = top + index * row_h
        hidden = index in blanks
        answer = cable_needed(a, b, auto_a=auto_a, auto_b=auto_b)
        parts.append(f'<rect data-row="{index + 1}" data-cable="{"" if hidden else escape(answer)}" x="4" y="{y}" '
                     f'width="372" height="{row_h - 4}" rx="4" fill="{"#ffffff" if hidden else "#f4f6fb"}" '
                     f'stroke="{_STROKE}" stroke-width="1"{" stroke-dasharray=\"5 3\"" if hidden else ""}/>')
        parts.append(_text_lines(10, y + 15, [f"{a} ({'oui' if auto_a else 'non'})"], size=10.5, weight="700"))
        parts.append(_text_lines(10, y + 29, [f"↔ {b} ({'oui' if auto_b else 'non'})"], size=10.5))
        parts.append(_text_lines(370, y + 22, [f"{blanks[index]} ?" if hidden else answer], size=10.5,
                                 weight="700", anchor="end"))
    y = top + len(rows) * row_h + 12
    notes = _wrap("Sans Auto MDI-X : carte réseau et port routé = MDI ; switch, hub et ports LAN d'une box = "
                  "MDI-X. Même type → croisé ; types différents → droit. Un seul port Auto MDI-X suffit.", 60)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def mini_svg(hosts: tuple[Host, ...], *, box: Host | None, blanks: dict[str, str] | None = None) -> str:
    """Mini-réseau en étoile : box (facultative) → switch → un câble par appareil. Chaque boîte
    affiche nom, adresse/préfixe (fixe ou DHCP), passerelle et DNS. `blanks` (« switch »,
    « box », ou « <nom>:ip|passerelle|dns ») remplace une valeur par un numéro à compléter."""
    blanks = blanks or {}
    width = 380
    parts: list[str] = []
    y = 6
    if box is not None:
        label = f"{blanks['box']} ?" if "box" in blanks else f"{box.name} — passerelle, DNS, DHCP"
        parts.append(_pc_box(72, y, 304, [label, f"LAN : {box.ip}/{box.prefix} · Internet : {WAN_IP}"],
                             key="" if "box" in blanks else box.name))
        parts.append(f'<path d="M58 30 H72" stroke="{_STROKE}" stroke-width="2"/>')
        y = 6
    sw_top = 6
    others = [h for h in hosts if box is None or h is not box]
    row_h, gap, top = 60, 6, 58 if box is not None else 8
    sw_bottom = top + len(others) * (row_h + gap) - gap
    sw_label = f"{blanks['switch']} ?" if "switch" in blanks else "Switch"
    parts.append(f'<rect data-node="{"" if "switch" in blanks else "switch"}" x="4" y="{sw_top}" width="54" '
                 f'height="{sw_bottom - sw_top}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(31, sw_top + 70, [sw_label], size=11.5, weight="700", anchor="middle"))
    for index, host in enumerate(others):
        hy = top + index * (row_h + gap)
        mid = hy + row_h // 2
        parts.append(f'<path data-link="{escape(host.name)}" d="M58 {mid} H72" stroke="{_STROKE}" stroke-width="2"/>')

        def val(field: str, text: str, host: Host = host) -> str:
            key = f"{host.name}:{field}"
            return f"{blanks[key]} ?" if key in blanks else text

        mode = "DHCP" if host.dhcp else "fixe"
        if blanks and host.dhcp:  # schéma à compléter : ne pas souffler la passerelle des postes fixes
            third = "passerelle et DNS reçus de la box (DHCP)"
        elif blanks and f"{host.name}:passerelle" not in blanks and host.gateway:
            third = "passerelle et DNS : à compléter comme PC-A"
        else:
            third = (f"passerelle {val('passerelle', host.gateway or '(vide)')} · "
                     f"DNS {val('dns', host.dns[0] if host.dns else '(vide)')}")
        parts.append(_pc_box(72, hy, 304, [
            f"{host.name} — {host.role}",
            f"IP {val('ip', f'{host.ip}/{host.prefix}')} ({mode})",
            third,
        ], key="" if any(k.startswith(f"{host.name}:") for k in blanks) else host.name))
    y = top + len(others) * (row_h + gap) + 10
    note = ("Réseau isolé : pas de box, pas de passerelle ; adresses fixes." if box is None
            else f"Étendue DHCP de la box : {POOL[0]} à {POOL[1]} ; adresses fixes hors de l'étendue.")
    lines = _wrap(note, 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def address_map_svg(*, blanks: dict[int, str] | None = None) -> str:
    """Carte des adresses de .1 à .254 : une bande par plage (largeur proportionnelle), avec
    ses bornes et son usage écrits en clair. `blanks` (index de plage → numéro) masque un usage."""
    blanks = blanks or {}
    width, left, bar_w, top = 380, 10, 360, 34
    parts = [_text_lines(width // 2, 16, [f"Carte des adresses du réseau {MINI_NETWORK}"], size=12, weight="700", anchor="middle")]
    x = left
    for index, (first, last, label) in enumerate(ADDRESS_RANGES):
        w = max(6.0, bar_w * (last - first + 1) / 254)
        hidden = index in blanks
        fill = "#ffffff" if hidden else ("#fff3c4" if "DHCP" in label else ("#f4f6fb" if "Libre" in label else _FILL))
        parts.append(f'<rect data-range="{first}-{last}" data-use="{"" if hidden else escape(label)}" x="{x:.1f}" y="{top}" '
                     f'width="{w:.1f}" height="26" fill="{fill}" stroke="{_STROKE}" stroke-width="1"/>')
        x += w
    y = top + 44
    for index, (first, last, label) in enumerate(ADDRESS_RANGES):
        span = f".{first}" if first == last else f".{first} à .{last}"
        text = f"{blanks[index]} ?" if index in blanks else label
        parts.append(_text_lines(14, y, [f"{span} : {text}"], size=11, weight="700" if index in blanks else "400"))
        y += 16
    notes = _wrap("Bandes de gauche à droite dans l'ordre des adresses ; largeur proportionnelle au nombre "
                  "d'adresses. .0 = adresse du réseau, .255 = diffusion : jamais attribuées.", 60)
    parts.append(_text_lines(8, y + 6, notes, size=10.5, step=13))
    return _svg(width, y + 6 + 13 * len(notes), parts)


def _screen_alt(lines: tuple[str, ...]) -> str:
    return "Capture texte fictive, ligne par ligne : " + " / ".join(line.strip() for line in lines if line.strip())


DIRECT_FIGURE = Figure(
    key="pr21-connexion-directe",
    title="Connexion directe de deux PC par un câble",
    alt=(
        f"Deux PC reliés par un seul câble RJ45, sans switch. {PC_A.name} : adresse {PC_A.ip}, masque "
        f"{PC_A.mask}, passerelle vide, DNS vide, MAC {PC_A.mac}. {PC_B.name} : adresse {PC_B.ip}, masque "
        f"{PC_B.mask}, passerelle vide, DNS vide, MAC {PC_B.mac}. Le câble est droit, ou croisé, l'une des cartes "
        "au moins faisant l'Auto MDI-X. Le voyant de lien est allumé à côté de la prise de chaque carte."
    ),
    caption="Même réseau, même masque, adresses différentes ; pas de passerelle : rien ne sort de ce réseau isolé.",
    svg=direct_svg(PC_A, PC_B),
)

CABLE_ROWS: tuple[tuple[str, str, bool, bool], ...] = tuple((a, b, False, False) for a, b in CABLE_PAIRS) + (
    ("PC", "PC", True, False),
)

CABLE_FIGURE = Figure(
    key="pr21-droit-ou-croise",
    title="Câble droit ou croisé selon les ports",
    alt=(
        "Tableau des liaisons et du câble à utiliser : "
        + " ; ".join(f"{a} ({'Auto MDI-X' if aa else 'sans Auto MDI-X'}) avec {b} "
                     f"({'Auto MDI-X' if ab else 'sans Auto MDI-X'}) : {cable_needed(a, b, auto_a=aa, auto_b=ab).lower()}"
                     for a, b, aa, ab in CABLE_ROWS)
        + ". Même type de port, croisé ; types différents, droit ; un seul port Auto MDI-X suffit."
    ),
    caption="La règle historique (MDI / MDI-X) et sa disparition avec l'Auto MDI-X des cartes actuelles.",
    svg=cable_table_svg(CABLE_ROWS),
)

DIALOG_FIGURE = Figure(
    key="pr21-fenetre-ipv4-pc-b",
    title=f"Configuration IPv4 fixe de {PC_B.name}, sans passerelle",
    alt=(
        "Fenêtre fictive « Propriétés de : Protocole Internet version 4 » : « Utiliser l'adresse IP "
        f"suivante » coché ; adresse IP {PC_B.ip}, masque {PC_B.mask}, passerelle par défaut vide ; "
        "« Utiliser l'adresse DNS suivante » coché, serveurs DNS préféré et auxiliaire vides."
    ),
    caption="Connexion directe : adresse et masque suffisent ; passerelle et DNS restent vides.",
    svg=ipv4_dialog_svg(PC_B),
)

PING_FIGURE = Figure(
    key="pr21-ping-arp",
    title=f"Ping réussi de {PC_A.name} vers {PC_B.name}, puis table ARP",
    alt=_screen_alt(PING_OK_LINES + ARP_OK_LINES),
    caption="Quatre réponses, 0 % de perte ; arp -a montre la MAC de PC-B apprise pendant le ping. Capture fictive simplifiée.",
    svg=screen_svg((*PING_OK_LINES, "", *ARP_OK_LINES), label=FICTIVE_LABEL),
)

FIREWALL_FIGURE = Figure(
    key="pr21-ping-pare-feu",
    title=f"Ping sans réponse de {PC_B.name} vers {PC_A.name}, MAC pourtant connue",
    alt=_screen_alt(PING_FIREWALL_LINES + ARP_FIREWALL_LINES),
    caption=("Quatre délais dépassés, mais arp -a connaît la MAC de PC-A : le câble et l'adressage sont bons, "
             "le pare-feu de PC-A ne répond pas au ping. Capture fictive simplifiée."),
    svg=screen_svg((*PING_FIREWALL_LINES, "", *ARP_FIREWALL_LINES), label=FICTIVE_LABEL),
)


def _mini_alt(hosts: tuple[Host, ...], box: Host | None) -> str:
    pieces = [
        f"{h.name} ({h.role}) : {h.ip}/{h.prefix} {'DHCP' if h.dhcp else 'fixe'}, passerelle "
        f"{h.gateway or 'vide'}, DNS {h.dns[0] if h.dns else 'vide'}"
        for h in hosts if box is None or h is not box
    ]
    head = ("Mini-réseau isolé en étoile : un switch relie par un câble chacun des postes ; pas de box. "
            if box is None else
            f"Mini-réseau en étoile : la box {box.ip} (passerelle, DNS, DHCP, adresse publique {WAN_IP}) est reliée "
            f"au switch, qui relie par un câble chacun des appareils ; étendue DHCP {POOL[0]} à {POOL[1]}. ")
    return head + " ; ".join(pieces) + "."


MINI_ISOLATED_FIGURE = Figure(
    key="pr21-mini-reseau-isole",
    title="Mini-réseau isolé : cinq PC autour d'un switch",
    alt=_mini_alt(ISOLATED_HOSTS, None),
    caption="On garde les adresses de la connexion directe et on continue la suite : .3, .4, .5 ; toujours sans passerelle.",
    svg=mini_svg(ISOLATED_HOSTS, box=None),
)

MINI_BOX_FIGURE = Figure(
    key="pr21-mini-reseau-box",
    title="Mini-réseau avec box : passerelle, DNS et DHCP",
    alt=_mini_alt(BOX_HOSTS, BOX),
    caption="La box devient passerelle et DNS ; le PC qui partage et l'imprimante gardent une adresse fixe hors de l'étendue DHCP.",
    svg=mini_svg(BOX_HOSTS, box=BOX),
)

MAP_FIGURE = Figure(
    key="pr21-plan-adressage",
    title=f"Carte des adresses du réseau {MINI_NETWORK}",
    alt=(
        "Bande des adresses .1 à .254, de gauche à droite : "
        + " ; ".join(f".{a}" + ("" if a == b else f" à .{b}") + f" {label.lower()}" for a, b, label in ADDRESS_RANGES)
        + "."
    ),
    caption="Une plage par usage : les adresses fixes ne tombent jamais dans l'étendue DHCP. Convention du cours.",
    svg=address_map_svg(),
)

TREE_FIGURE = Figure(
    key="pr21-arbre-diagnostic",
    title="Diagnostiquer une liaison ou un mini-réseau, contrôle par contrôle",
    alt=(
        "Arbre de décision : "
        + " ; ".join(f"{i}. {q} ? Si non : {d}" for i, (q, d) in enumerate(TREE_QUESTIONS, start=1))
        + f". Si tout est oui : {TREE_FINAL}"
    ),
    caption="Le premier contrôle en échec désigne la piste ; inutile de chercher le partage tant que le ping échoue.",
    svg=decision_tree_svg(TREE_QUESTIONS, TREE_FINAL),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


DIRECT_PROC_FIGURE = _proc_figure("pr21-procedure-connexion", 1, PROCEDURES[0][0], DIRECT_STEPS,
                                  "Du matériel au partage : chaque étape se vérifie avant la suivante.")
EXTEND_PROC_FIGURE = _proc_figure("pr21-procedure-extension", 2, PROCEDURES[1][0], EXTEND_STEPS,
                                  "Le plan d'adressage s'écrit avant de toucher aux postes.")
ACCEPT_PROC_FIGURE = _proc_figure("pr21-procedure-recette", 3, PROCEDURES[2][0], ACCEPT_STEPS,
                                  "Une ligne de recette par poste ; le procès-verbal reprend les résultats.")

PR21_FIGURES: tuple[Figure, ...] = (
    DIRECT_FIGURE,
    CABLE_FIGURE,
    DIALOG_FIGURE,
    PING_FIGURE,
    FIREWALL_FIGURE,
    MINI_ISOLATED_FIGURE,
    MINI_BOX_FIGURE,
    MAP_FIGURE,
    TREE_FIGURE,
    DIRECT_PROC_FIGURE,
    EXTEND_PROC_FIGURE,
    ACCEPT_PROC_FIGURE,
)

# =============================================================================================
# 8. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

DIRECT_BLANKS: dict[str, str] = {"ip": "①", "masque": "②", "passerelle": "③", "cable": "④"}
DIRECT_BLANK_ANSWERS: dict[str, str] = {
    "①": f"Une adresse du même réseau, différente de {PC_A.ip} : {PC_B.ip} (de .2 à .254)",
    "②": f"{PC_B.mask} (/24), le même que {PC_A.name}",
    "③": "Vide : réseau isolé, aucun routeur",
    "④": "Câble droit si une carte au moins fait l'Auto MDI-X ; sinon câble croisé",
}

DIRECT_BLANK_FIGURE = Figure(
    key="pr21-connexion-a-completer",
    title="Connexion directe à compléter",
    alt=(
        f"Deux PC reliés par un seul câble, sans switch. {PC_A.name} : adresse {PC_A.ip}, masque {PC_A.mask}, "
        f"passerelle vide, DNS vide. {PC_B.name} : adresse ① à compléter, masque ② à compléter, passerelle ③ à "
        "compléter, DNS vide. Le câble ④ est à choisir. Voyant de lien allumé des deux côtés."
    ),
    caption="Schéma à compléter : adresse, masque et passerelle de PC-B, type de câble.",
    svg=direct_svg(PC_A, PC_B, blanks=DIRECT_BLANKS),
)

CABLE_BLANK_ROWS: tuple[tuple[str, str, bool, bool], ...] = (
    ("PC", "PC", False, False),
    ("PC", "Switch", False, False),
    ("Switch", "Switch", False, False),
    ("Portable", "PC", True, False),
    ("PC", "Routeur (port routé)", False, False),
)
CABLE_BLANKS: dict[int, str] = {0: "①", 1: "②", 2: "③", 3: "④", 4: "⑤"}

CABLE_BLANK_FIGURE = Figure(
    key="pr21-cablage-a-completer",
    title="Câble droit ou croisé : tableau à compléter",
    alt=(
        "Cinq liaisons dont le câble est à trouver : "
        + " ; ".join(f"{CABLE_BLANKS[i]} {a} ({'Auto MDI-X' if aa else 'sans Auto MDI-X'}) avec {b} "
                     f"({'Auto MDI-X' if ab else 'sans Auto MDI-X'})" for i, (a, b, aa, ab) in enumerate(CABLE_BLANK_ROWS))
        + ". Rappel sous le tableau : carte réseau et port routé MDI ; switch, hub et ports LAN d'une box MDI-X."
    ),
    caption="Schéma à compléter : écrire le câble de chaque liaison ①…⑤.",
    svg=cable_table_svg(CABLE_BLANK_ROWS, blanks=CABLE_BLANKS, title="Quel câble ? (à compléter)"),
)

MINI_BLANKS: dict[str, str] = {
    "switch": "①",
    "IMP-01:ip": "②",
    "PC-A:passerelle": "③",
    "PC-A:dns": "④",
}
MINI_BLANK_ANSWERS: dict[str, str] = {
    "①": "Switch : centre de l'étoile, un câble droit par appareil",
    "②": f"Adresse fixe hors de l'étendue DHCP, dans la plage des imprimantes : {PRINTER.ip}/24",
    "③": f"{BOX_IP} (la box), à saisir à la main sur ce poste fixe",
    "④": f"{BOX_IP} (la box relaie les requêtes DNS)",
}

MINI_BLANK_FIGURE = Figure(
    key="pr21-mini-reseau-a-completer",
    title="Mini-réseau avec box à compléter",
    alt=(
        f"La box {BOX_IP} (passerelle, DNS, DHCP, étendue {POOL[0]} à {POOL[1]}) est reliée à l'équipement ① ; "
        "① relie par un câble chacun des appareils. "
        f"PC-A, poste fixe qui partage le dossier : {FIXED_A.ip}/24 fixe, passerelle ③ et DNS ④ à compléter. "
        "IMP-01, imprimante réseau : adresse ② à compléter, fixe ; passerelle et DNS à compléter comme PC-A. "
        "PC-B, PC-C, PC-D, PC-E : adresses DHCP de l'étendue (.100 à .103), passerelle et DNS reçus de la box."
    ),
    caption="Schéma à compléter : nommer ①, donner l'adresse ② de l'imprimante, la passerelle ③ et le DNS ④ de PC-A.",
    svg=mini_svg(BOX_HOSTS, box=BOX, blanks=MINI_BLANKS),
)

MAP_BLANKS: dict[int, str] = {0: "①", 1: "②", 3: "③", 5: "④"}
MAP_BLANK_ANSWERS: dict[str, str] = {MAP_BLANKS[i]: ADDRESS_RANGES[i][2] for i in MAP_BLANKS}

MAP_BLANK_FIGURE = Figure(
    key="pr21-plan-adressage-a-completer",
    title="Carte des adresses à compléter",
    alt=(
        f"Bande des adresses du réseau {MINI_NETWORK}, de gauche à droite : "
        + " ; ".join((f".{a}" + ("" if a == b else f" à .{b}") + " : "
                      + (f"usage {MAP_BLANKS[i]} à compléter" if i in MAP_BLANKS else label.lower()))
                     for i, (a, b, label) in enumerate(ADDRESS_RANGES))
        + "."
    ),
    caption="Schéma à compléter : écrire l'usage des plages ①, ②, ③ et ④.",
    svg=address_map_svg(blanks=MAP_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (DIRECT_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr21-connexion-a-completer.svg"),
    (CABLE_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr21-cablage-a-completer.svg"),
    (MINI_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr21-mini-reseau-a-completer.svg"),
    (MAP_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr21-plan-adressage-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18) : le SVG du cours,
    précédé d'un titre et d'une description accessibles (affiché dans une balise `<img>`)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


def all_capture_lines() -> tuple[str, ...]:
    """Toutes les lignes de captures des figures (contrôle de largeur par les tests)."""
    return PING_OK_LINES + ARP_OK_LINES + PING_FIREWALL_LINES + ARP_FIREWALL_LINES

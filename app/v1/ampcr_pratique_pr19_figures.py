"""PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements » — données de référence, calculs
et schémas SVG (ticket #220).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket220_ampcr_pratique_pr19.py` :

- topologies bus, étoile, anneau, maillage (`TOPOLOGIES`) ; nombre de liaisons
  (`mesh_links`, `star_links`, `ring_links`) ; effet d'une panne calculé sur un petit modèle
  de réseau (`Net`, `isolated_stations`) ;
- modèle OSI à 7 couches et modèle TCP/IP à 4 couches (`OSI_LAYERS`, `TCPIP_LAYERS`,
  `tcpip_layer_for`) ; unité de données de chaque couche ;
- encapsulation : tailles du segment, du paquet et de la trame Ethernet (`encapsulate`) et
  champs de la trame IEEE 802.3 / Ethernet II (`FRAME_FIELDS`) ;
- protocoles applicatifs et ports (`PORTS`) ; distinction protocole / service / équipement ;
- équipements et couche de travail (`DEVICES`) ; domaines de collision et de diffusion
  calculés sur un plan de réseau (`Lan`, `collision_domains`, `broadcast_domains`) ;
- chemin d'un paquet PC → switch → box → Internet : adresses MAC et IP de chaque trame
  (`next_hop`, `path_frames`) ;
- diagnostic couche par couche (`LAYER_CHECKS`, `fault_layer`) ;
- NetBEUI, protocole historique non routable (`NETBEUI_FACTS`, `crosses_router`) ;
- trois procédures illustrées (`CHOICE_STEPS`, `PATH_STEPS`, `DIAG_STEPS`) ;
- six schémas à compléter servis aussi en fichiers statiques (`STATIC_FIGURES`).

Valeurs de référence (normes publiques) :
- modèle OSI : ISO/IEC 7498-1 ; modèle TCP/IP : RFC 1122 (couches application, transport,
  Internet, accès réseau) ;
- Ethernet IEEE 802.3 : en-tête 14 octets (MAC destination 6, MAC source 6, type 2), données
  46 à 1 500 octets (MTU 1 500), FCS 4 octets ; trame de 64 à 1 518 octets, préambule et
  délimiteur (8 octets) non comptés ; types 0x0800 IPv4, 0x0806 ARP, 0x86DD IPv6 ;
- en-têtes minimaux, sans option : IPv4 20 octets (RFC 791), TCP 20 octets (RFC 9293), UDP
  8 octets (RFC 768) ;
- ports bien connus de l'IANA (HTTP 80, HTTPS 443, DNS 53, DHCP 67/68, SMB 445…).

Adresses publiques fictives : blocs de documentation RFC 5737 (203.0.113.0/24,
198.51.100.0/24), jamais attribués sur Internet ; adresses MAC fictives. Chaque schéma porte
son information en texte : la couleur n'est qu'un repère. Aucun schéma ne vient d'une image
générée ni d'une photographie.
"""

import math
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr14_figures import fr
from app.v1.ampcr_pratique_pr20_figures import is_local_for
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, _wrap, step_flow_svg

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
_STROKE = "#33415c"
_FILL = "#dbe4f3"
_SOFT = "#f4f6fb"
_BAD = "#b3261e"
_OK = "#1d6b34"
_ZONE_A = "#eef4ea"
_ZONE_B = "#fbf1e3"

__all__ = ["fr"]


def octets(n: int) -> str:
    """Nombre d'octets au format belge : 1 518."""
    return f"{n:,}".replace(",", " ")


# =============================================================================================
# 1. Topologies
# =============================================================================================

TOPO_BUS = "Bus"
TOPO_STAR = "Étoile"
TOPO_RING = "Anneau"
TOPO_MESH = "Maillage"
TOPOLOGY_NAMES: tuple[str, ...] = (TOPO_BUS, TOPO_STAR, TOPO_RING, TOPO_MESH)


@dataclass(frozen=True)
class TopologyInfo:
    name: str
    principle: str
    example: str
    advantages: str
    drawbacks: str
    failure: str


TOPOLOGIES: tuple[TopologyInfo, ...] = (
    TopologyInfo(
        TOPO_BUS,
        "Un seul câble (le bus) passe devant toutes les stations ; un bouchon ferme chaque extrémité. "
        "Chaque trame circule sur tout le câble.",
        "Ethernet coaxial 10BASE2 des années 1990 (PR16)",
        "peu de câble, pose simple le long d'une rangée de postes",
        "débit partagé, un seul domaine de collision, panne difficile à localiser",
        "câble coupé, T retiré ou bouchon absent : tout le segment s'arrête (réflexions)",
    ),
    TopologyInfo(
        TOPO_STAR,
        "Chaque station est reliée par son propre câble à un équipement central (switch ; "
        "autrefois hub).",
        "Ethernet actuel en paire torsadée (PR15, PR18)",
        "un câble coupé n'arrête qu'un poste ; ajout et dépannage faciles",
        "plus de câble ; l'équipement central est un point unique de panne",
        "câble d'un poste : ce poste seul ; switch central : tout le réseau",
    ),
    TopologyInfo(
        TOPO_RING,
        "Chaque station est reliée à la suivante, la dernière à la première ; les données font le "
        "tour dans un sens (accès par jeton).",
        "Token Ring d'IBM (4 et 16 Mb/s), FDDI (double anneau de fibre) ; anneaux de fibre des opérateurs",
        "accès ordonné par le jeton : pas de collision",
        "ajouter une station ouvre l'anneau ; anneau simple fragile",
        "anneau simple : une liaison ou une station coupée arrête tout ; anneau double : rebouclage, le service continue",
    ),
    TopologyInfo(
        TOPO_MESH,
        "Plusieurs chemins relient les équipements ; maillage complet : chacun est relié à tous les "
        "autres.",
        "routeurs d'Internet et des opérateurs, liaisons entre sites, switchs de cœur doublés",
        "une liaison coupée : le trafic passe par un autre chemin",
        "coûteux (n × (n − 1) ÷ 2 liaisons en maillage complet), configuration plus complexe",
        "une liaison coupée : aucun équipement isolé tant qu'un autre chemin existe",
    ),
)
TOPOLOGY_BY_NAME = {t.name: t for t in TOPOLOGIES}


def mesh_links(n: int) -> int:
    """Liaisons d'un maillage complet de n équipements : chacun relié aux n − 1 autres, chaque
    liaison comptée une fois."""
    return n * (n - 1) // 2


def star_links(stations: int) -> int:
    """Étoile : un câble par station jusqu'à l'équipement central."""
    return stations


def ring_links(stations: int) -> int:
    return stations


@dataclass(frozen=True)
class Net:
    """Petit modèle de réseau : `stations` (postes), `centers` (switchs ou routeurs) et liaisons."""

    kind: str
    stations: tuple[str, ...]
    links: tuple[tuple[str, str], ...]
    centers: tuple[str, ...] = ()
    double_ring: bool = False


def _components(nodes: set[str], links: list[tuple[str, str]]) -> list[set[str]]:
    parent = {n: n for n in nodes}

    def find(n: str) -> str:
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for a, b in links:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    groups: dict[str, set[str]] = {}
    for n in nodes:
        groups.setdefault(find(n), set()).add(n)
    return list(groups.values())


def isolated_stations(net: Net, *, link: tuple[str, str] | None = None, node: str | None = None,
                      terminator: bool = False) -> frozenset[str]:
    """Stations qui ne communiquent plus avec le reste du réseau après la panne d'une liaison
    (`link`), d'un équipement ou d'une station (`node`), ou d'un bouchon de bus (`terminator`).

    - bus : un câble coupé ou un bouchon absent arrête tout le segment ; une station éteinte
      (T en place) ne gêne pas les autres ;
    - anneau simple : une liaison ou une station en panne arrête la circulation ; anneau double :
      rebouclage, seule la station en panne manque ;
    - étoile, étoile étendue, maillage : calcul de connexité ; avec un équipement central
      (`centers[0]`, vers lequel tout converge), les stations qui ne le joignent plus sont
      isolées (toutes s'il tombe) ; sans équipement central (maillage), celles qui sont hors du
      plus grand groupe encore relié."""
    alive = [s for s in net.stations if s != node]
    if net.kind == TOPO_BUS:
        return frozenset(alive) if (link is not None or terminator) else frozenset()
    if net.kind == TOPO_RING and not net.double_ring:
        return frozenset(alive) if (link is not None or node is not None) else frozenset()
    if net.kind == TOPO_RING:
        return frozenset()
    nodes = (set(net.stations) | set(net.centers)) - {node}
    links = [lk for lk in net.links if lk != link and tuple(reversed(lk)) != link]
    groups = _components(nodes, links)
    if net.centers:
        core = net.centers[0]
        if core == node:
            return frozenset(alive)
        reached = next(g for g in groups if core in g)
    else:
        reached = max(groups, key=len)
    return frozenset(set(alive) - reached)


def _star(n: int) -> Net:
    stations = tuple(f"PC{i}" for i in range(1, n + 1))
    return Net(TOPO_STAR, stations, tuple(("SW", s) for s in stations), centers=("SW",))


def _ring(n: int, *, double: bool = False) -> Net:
    stations = tuple(f"PC{i}" for i in range(1, n + 1))
    links = tuple((stations[i], stations[(i + 1) % n]) for i in range(n))
    return Net(TOPO_RING, stations, links, double_ring=double)


def _mesh(n: int) -> Net:
    stations = tuple(f"R{i}" for i in range(1, n + 1))
    links = tuple((a, b) for i, a in enumerate(stations) for b in stations[i + 1:])
    return Net(TOPO_MESH, stations, links)


def _bus(n: int) -> Net:
    stations = tuple(f"PC{i}" for i in range(1, n + 1))
    return Net(TOPO_BUS, stations, tuple((stations[i], stations[i + 1]) for i in range(n - 1)))


STAR_5 = _star(5)
RING_5 = _ring(5)
DOUBLE_RING_5 = _ring(5, double=True)
MESH_4 = _mesh(4)
BUS_4 = _bus(4)
# Étoile étendue : un switch principal relié à deux switchs d'étage, trois postes chacun.
TREE = Net(
    TOPO_STAR,
    ("PC1", "PC2", "PC3", "PC4", "PC5", "PC6"),
    (("SW0", "SW1"), ("SW0", "SW2"), ("SW1", "PC1"), ("SW1", "PC2"), ("SW1", "PC3"),
     ("SW2", "PC4"), ("SW2", "PC5"), ("SW2", "PC6")),
    centers=("SW0", "SW1", "SW2"),
)

# =============================================================================================
# 2. Modèles OSI et TCP/IP
# =============================================================================================


@dataclass(frozen=True)
class Layer:
    number: int
    name: str
    role: str
    pdu: str
    protocols: str
    equipment: str
    checks: str


OSI_LAYERS: tuple[Layer, ...] = (
    Layer(7, "Application", "services réseau offerts aux programmes : web, messagerie, partage, noms",
          "données", "HTTP, HTTPS, DNS, DHCP, SMTP, IMAP, FTP, SSH, SMB", "serveur, passerelle applicative",
          "le service répond-il ? nslookup, message de l'application, identifiants"),
    Layer(6, "Présentation", "format des données : codage des caractères, compression, chiffrement",
          "données", "codages et formats (ASCII, UTF-8, JPEG)", "—",
          "caractères illisibles, format refusé"),
    Layer(5, "Session", "ouverture, maintien et fermeture du dialogue entre deux applications",
          "données", "gestion du dialogue (NetBIOS ; dans TCP/IP, assurée par l'application)", "—",
          "session coupée, reconnexion demandée"),
    Layer(4, "Transport", "transport de bout en bout entre deux programmes repérés par un port ; TCP fiable "
          "(accusés de réception, retransmission), UDP rapide sans garantie",
          "segment (TCP) ou datagramme (UDP)", "TCP, UDP", "pare-feu (filtrage des ports)",
          "port du service bloqué ou fermé : Test-NetConnection -Port, netstat"),
    Layer(3, "Réseau", "adresse logique (IP) et choix du chemin entre réseaux (routage)",
          "paquet", "IPv4, IPv6, ICMP (ping)", "routeur",
          "ipconfig (adresse, masque, passerelle), ping de la passerelle, tracert"),
    Layer(2, "Liaison de données", "trame entre deux appareils du même réseau local : adresses MAC, "
          "contrôle d'erreur (FCS)",
          "trame", "Ethernet (IEEE 802.3), Wi-Fi (IEEE 802.11) ; ARP fait le lien entre IP et MAC",
          "switch, pont, point d'accès", "port du switch actif et dans le bon VLAN, arp -a"),
    Layer(1, "Physique", "bits transmis sur le support : signal électrique, lumineux ou radio, câbles et "
          "connecteurs", "bit", "normes de câble et de signal (10BASE2, 1000BASE-T, 1000BASE-SX)",
          "câble, prise, hub, répéteur, modem", "voyant de lien, câble, prise, testeur"),
)
OSI_BY_NUMBER = {layer.number: layer for layer in OSI_LAYERS}

# (nom, couches OSI couvertes, protocoles)
TCPIP_LAYERS: tuple[tuple[str, tuple[int, ...], str], ...] = (
    ("Application", (7, 6, 5), "HTTP, DNS, DHCP, SMTP, SMB"),
    ("Transport", (4,), "TCP, UDP"),
    ("Internet", (3,), "IP, ICMP"),
    ("Accès réseau", (2, 1), "Ethernet, Wi-Fi"),
)


def tcpip_layer_for(osi: int) -> str:
    for name, covered, _p in TCPIP_LAYERS:
        if osi in covered:
            return name
    raise ValueError(osi)


# Couche OSI des protocoles cités dans le cours (sans ambiguïté).
PROTOCOL_LAYER: dict[str, int] = {
    "HTTP": 7, "HTTPS": 7, "DNS": 7, "DHCP": 7, "SMTP": 7, "IMAP": 7, "FTP": 7, "SSH": 7, "SMB": 7,
    "TCP": 4, "UDP": 4, "IP": 3, "ICMP": 3, "Ethernet": 2, "Wi-Fi": 2,
}

# =============================================================================================
# 3. Encapsulation et trame Ethernet
# =============================================================================================

ETH_HEADER = 14  # MAC destination 6 + MAC source 6 + type 2
ETH_FCS = 4
ETH_MIN_PAYLOAD = 46
ETH_MTU = 1500
ETH_MIN_FRAME = ETH_HEADER + ETH_MIN_PAYLOAD + ETH_FCS  # 64
ETH_MAX_FRAME = ETH_HEADER + ETH_MTU + ETH_FCS  # 1 518
PREAMBLE = 8  # préambule 7 + délimiteur 1, non comptés dans la trame
IPV4_HEADER = 20
TRANSPORT_HEADER: dict[str, int] = {"TCP": 20, "UDP": 8}
TCP_MSS = ETH_MTU - IPV4_HEADER - TRANSPORT_HEADER["TCP"]  # 1 460
ETHERTYPES: tuple[tuple[str, str], ...] = (("0x0800", "IPv4"), ("0x0806", "ARP"), ("0x86DD", "IPv6"))
BROADCAST_MAC = "FF-FF-FF-FF-FF-FF"


@dataclass(frozen=True)
class Encapsulation:
    transport: str
    data: int
    segment: int  # données + en-tête TCP ou UDP
    packet: int  # segment + en-tête IPv4
    padding: int  # bourrage ajouté si le paquet fait moins de 46 octets
    frame: int  # en-tête Ethernet + paquet (+ bourrage) + FCS


def encapsulate(data: int, transport: str = "TCP") -> Encapsulation:
    """Tailles successives (octets) en IPv4 sur Ethernet, en-têtes sans option."""
    segment = data + TRANSPORT_HEADER[transport]
    packet = segment + IPV4_HEADER
    if packet > ETH_MTU:
        raise ValueError("Paquet plus grand que la MTU Ethernet : TCP découpe en segments plus petits.")
    padding = max(0, ETH_MIN_PAYLOAD - packet)
    return Encapsulation(transport, data, segment, packet, padding, ETH_HEADER + packet + padding + ETH_FCS)


FRAME_FIELDS: tuple[tuple[str, str], ...] = (
    ("Adresse MAC de destination", "6"),
    ("Adresse MAC source", "6"),
    ("Type", "2"),
    ("Données (paquet IP)", f"{ETH_MIN_PAYLOAD} à {octets(ETH_MTU)}"),
    ("FCS (contrôle d'erreur)", "4"),
)

ENCAP_EXAMPLE = encapsulate(TCP_MSS, "TCP")  # 1 460 → 1 480 → 1 500 → 1 518

# =============================================================================================
# 4. Protocoles, services, équipements ; ports
# =============================================================================================

KIND_PROTOCOL = "Protocole"
KIND_SERVICE = "Service"
KIND_DEVICE = "Équipement"
PSE_KINDS: tuple[str, ...] = (KIND_PROTOCOL, KIND_SERVICE, KIND_DEVICE)
PSE_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    (KIND_PROTOCOL, "ensemble de règles (format des messages, ordre des échanges) que deux appareils suivent pour se comprendre",
     "TCP, IP, HTTP, DHCP, Ethernet"),
    (KIND_SERVICE, "fonction rendue par un programme serveur, qui utilise un protocole et attend les demandes sur un port",
     "serveur web, serveur DHCP de la box, partage de fichiers, résolution DNS"),
    (KIND_DEVICE, "matériel qui transporte les données ou les produit ; il peut héberger des services",
     "switch, routeur, point d'accès, box, PC"),
)


@dataclass(frozen=True)
class PortInfo:
    name: str
    transport: str
    ports: tuple[int, ...]
    role: str


PORTS: tuple[PortInfo, ...] = (
    PortInfo("HTTP", "TCP", (80,), "pages web non chiffrées"),
    PortInfo("HTTPS", "TCP", (443,), "pages web chiffrées"),
    PortInfo("DNS", "UDP (et TCP)", (53,), "traduire un nom en adresse IP"),
    PortInfo("DHCP", "UDP", (67, 68), "attribuer l'adresse IP automatiquement (67 serveur, 68 client)"),
    PortInfo("SMTP", "TCP", (25, 587), "envoyer le courrier (25 entre serveurs, 587 envoi par le logiciel de messagerie)"),
    PortInfo("IMAP", "TCP", (143, 993), "lire le courrier sur le serveur (993 chiffré)"),
    PortInfo("FTP", "TCP", (20, 21), "transférer des fichiers (21 commandes, 20 données)"),
    PortInfo("SSH", "TCP", (22,), "administrer à distance, de façon chiffrée"),
    PortInfo("SMB", "TCP", (445,), "partage de fichiers et d'imprimantes Windows"),
    PortInfo("RDP", "TCP", (3389,), "Bureau à distance Windows"),
)
PORT_BY_NAME = {p.name: p for p in PORTS}


def service_for_port(port: int) -> str:
    for info in PORTS:
        if port in info.ports:
            return info.name
    raise KeyError(port)


# =============================================================================================
# 5. Équipements, domaines de collision et de diffusion
# =============================================================================================


@dataclass(frozen=True)
class DeviceInfo:
    name: str
    layer: str  # couche OSI de travail
    role: str
    reads: str  # ce que l'équipement lit pour décider
    collisions: str
    broadcasts: str


DEV_REPEATER = "Répéteur"
DEV_HUB = "Hub"
DEV_BRIDGE = "Pont"
DEV_SWITCH = "Switch"
DEV_AP = "Point d'accès"
DEV_ROUTER = "Routeur"
DEV_MODEM = "Modem"
DEV_GATEWAY = "Passerelle"

DEVICES: tuple[DeviceInfo, ...] = (
    DeviceInfo(DEV_REPEATER, "1", "régénère le signal pour prolonger une liaison", "rien (bits)",
               "ne les sépare pas", "ne les sépare pas"),
    DeviceInfo(DEV_HUB, "1", "concentrateur : recopie chaque signal reçu sur tous les autres ports", "rien (bits)",
               "un seul domaine pour tous ses ports", "ne les sépare pas"),
    DeviceInfo(DEV_BRIDGE, "2", "relie deux segments et ne laisse passer une trame que si le destinataire est de l'autre côté",
               "adresse MAC", "sépare les deux segments", "ne les sépare pas"),
    DeviceInfo(DEV_SWITCH, "2", "commutateur : envoie chaque trame seulement vers le port du destinataire (table MAC)",
               "adresse MAC", "un domaine par port", "ne les sépare pas (sauf VLAN)"),
    DeviceInfo(DEV_AP, "2", "relie les appareils sans fil (Wi-Fi) au réseau filaire", "adresse MAC",
               "accès radio partagé", "ne les sépare pas"),
    DeviceInfo(DEV_ROUTER, "3", "relie des réseaux IP différents et choisit le chemin (table de routage)", "adresse IP",
               "un domaine par interface", "un domaine par interface"),
    DeviceInfo(DEV_MODEM, "1", "convertit le signal numérique en signal adapté à la ligne de l'opérateur (VDSL sur cuivre, "
               "DOCSIS sur coaxial) et inversement ; sur fibre, l'ONT joue ce rôle", "rien (signal)", "—", "—"),
    DeviceInfo(DEV_GATEWAY, "3 à 7", "point de sortie d'un réseau : la passerelle par défaut est l'adresse IP du routeur ; "
               "au sens large, appareil qui traduit entre deux protocoles différents", "adresse IP (ou plus haut)",
               "—", "—"),
)
DEVICE_BY_NAME = {d.name: d for d in DEVICES}

# Types de nœuds du modèle de domaines
N_PC, N_HUB, N_REPEATER, N_SWITCH, N_BRIDGE, N_ROUTER = "pc", "hub", "repeteur", "switch", "pont", "routeur"
_SHARED_MEDIUM = frozenset({N_HUB, N_REPEATER})  # couche 1 : recopie les bits, ne coupe rien


@dataclass(frozen=True)
class Lan:
    """Plan d'un réseau : nœuds (nom → type), positions (dessin) et liaisons."""

    nodes: tuple[tuple[str, str, float, float], ...]  # (nom, type, x, y)
    links: tuple[tuple[str, str], ...]

    @property
    def kinds(self) -> dict[str, str]:
        return {n: k for n, k, _x, _y in self.nodes}


def _link_groups(lan: Lan, merge_through: frozenset[str] | None) -> list[int]:
    """Numéro de groupe de chaque liaison : deux liaisons qui touchent un même nœud dont le
    type est dans `merge_through` (ou, si `None`, qui n'est pas un routeur) sont fusionnées."""
    kinds = lan.kinds
    parent = list(range(len(lan.links)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for node, kind in kinds.items():
        merges = kind in merge_through if merge_through is not None else kind != N_ROUTER
        if not merges:
            continue
        touching = [i for i, (a, b) in enumerate(lan.links) if node in (a, b)]
        for i in touching[1:]:
            parent[find(i)] = find(touching[0])
    roots = [find(i) for i in range(len(lan.links))]
    numbering: dict[int, int] = {}
    for root in roots:
        numbering.setdefault(root, len(numbering) + 1)
    return [numbering[r] for r in roots]


def collision_domain_of_links(lan: Lan) -> list[int]:
    """Domaine de collision (numéroté à partir de 1) de chaque liaison : un hub ou un répéteur
    réunit toutes ses liaisons ; un switch, un pont ou un routeur les sépare."""
    return _link_groups(lan, _SHARED_MEDIUM)


def broadcast_domain_of_links(lan: Lan) -> list[int]:
    """Domaine de diffusion de chaque liaison : seul le routeur arrête une diffusion."""
    return _link_groups(lan, None)


def collision_domains(lan: Lan) -> int:
    return len(set(collision_domain_of_links(lan)))


def broadcast_domains(lan: Lan) -> int:
    return len(set(broadcast_domain_of_links(lan)))


DOMAINS_LAN = Lan(
    nodes=(
        ("R1", N_ROUTER, 190, 34),
        ("SW1", N_SWITCH, 95, 104), ("SW2", N_SWITCH, 300, 104),
        ("PC1", N_PC, 30, 178), ("PC2", N_PC, 95, 178), ("HUB", N_HUB, 165, 178),
        ("PC3", N_PC, 130, 250), ("PC4", N_PC, 200, 250),
        ("PC5", N_PC, 260, 178), ("PC6", N_PC, 340, 178),
    ),
    links=(
        ("R1", "SW1"), ("R1", "SW2"), ("SW1", "PC1"), ("SW1", "PC2"), ("SW1", "HUB"),
        ("HUB", "PC3"), ("HUB", "PC4"), ("SW2", "PC5"), ("SW2", "PC6"),
    ),
)
DOMAINS_COLLISIONS = collision_domains(DOMAINS_LAN)
DOMAINS_BROADCASTS = broadcast_domains(DOMAINS_LAN)

# Réseau du schéma à compléter (exercice) : différent de celui du cours.
DOMAINS_BLANK_LAN = Lan(
    nodes=(
        ("R1", N_ROUTER, 190, 34),
        ("SW1", N_SWITCH, 95, 104), ("HUB", N_HUB, 300, 104),
        ("PC1", N_PC, 25, 178), ("PC2", N_PC, 72, 178), ("PC3", N_PC, 119, 178), ("PC4", N_PC, 166, 178),
        ("PC5", N_PC, 250, 178), ("PC6", N_PC, 300, 178), ("PC7", N_PC, 350, 178),
    ),
    links=(
        ("R1", "SW1"), ("R1", "HUB"), ("SW1", "PC1"), ("SW1", "PC2"), ("SW1", "PC3"), ("SW1", "PC4"),
        ("HUB", "PC5"), ("HUB", "PC6"), ("HUB", "PC7"),
    ),
)

# =============================================================================================
# 6. Chemin d'un paquet : PC → switch → box → Internet
# =============================================================================================


@dataclass(frozen=True)
class Iface:
    owner: str
    mac: str
    ip: str


LAN_PREFIX = 24
PC = Iface("PC-COMPTA", "3C-52-82-1A-2B-01", "192.168.1.23")
PC_PEER = Iface("PC-ACCUEIL", "3C-52-82-1A-2B-07", "192.168.1.40")
BOX_LAN = Iface("Box, interface réseau local", "A4-91-B1-07-3C-10", "192.168.1.1")
BOX_WAN = Iface("Box, interface opérateur", "A4-91-B1-07-3C-11", "203.0.113.45")
ISP_ROUTER = Iface("Routeur de l'opérateur", "00-1F-9E-55-20-01", "203.0.113.1")
SERVER_NAME = "www.exemple.be"
SERVER_IP = "198.51.100.20"
GATEWAY = BOX_LAN.ip
ARP_TABLE: dict[str, str] = {BOX_LAN.ip: BOX_LAN.mac, PC_PEER.ip: PC_PEER.mac}


def next_hop(src_ip: str, prefix: int, dst_ip: str, gateway: str) -> str:
    """Adresse IP à joindre sur le réseau local : le destinataire s'il est dans le même réseau,
    sinon la passerelle par défaut. C'est son adresse MAC que le poste demande par ARP."""
    return dst_ip if is_local_for(src_ip, prefix, dst_ip) else gateway


@dataclass(frozen=True)
class FrameView:
    segment: str
    src_mac: str
    dst_mac: str
    src_ip: str
    dst_ip: str


def lan_frame(src: Iface, dst_ip: str, *, prefix: int = LAN_PREFIX, gateway: str = GATEWAY,
              arp: dict[str, str] | None = None) -> FrameView:
    """Trame émise par un poste du réseau local vers `dst_ip`."""
    table = ARP_TABLE if arp is None else arp
    hop = next_hop(src.ip, prefix, dst_ip, gateway)
    return FrameView("réseau local", src.mac, table[hop], src.ip, dst_ip)


def path_frames(dst_ip: str = SERVER_IP) -> tuple[FrameView, FrameView]:
    """Les deux premières trames d'un paquet du PC vers un serveur d'Internet : le switch ne
    change rien ; la box (routeur) retire la trame, remplace l'adresse IP source privée par son
    adresse publique (NAT) et construit une nouvelle trame vers le routeur de l'opérateur. Les
    adresses MAC changent à chaque routeur ; l'adresse IP de destination ne change pas."""
    first = lan_frame(PC, dst_ip)
    second = FrameView("ligne de l'opérateur", BOX_WAN.mac, ISP_ROUTER.mac, BOX_WAN.ip, dst_ip)
    return first, second


PATH_FRAMES = path_frames()

ARP_LINES: tuple[str, ...] = (
    "C:\\> arp -a",
    f"Interface : {PC.ip} --- 0xb",
    "  Adresse Internet      Adresse physique      Type",
    f"  {BOX_LAN.ip:<20}  {BOX_LAN.mac.lower():<20}  dynamique",
    f"  {PC_PEER.ip:<20}  {PC_PEER.mac.lower():<20}  dynamique",
    f"  {'192.168.1.255':<20}  {BROADCAST_MAC.lower():<20}  statique",
)

# =============================================================================================
# 7. Diagnostic par couche
# =============================================================================================

L1, L2, L3, L4, L7 = (
    "Couche 1 — physique",
    "Couche 2 — liaison",
    "Couche 3 — réseau",
    "Couche 4 — transport",
    "Couche 7 — application",
)
FAULT_LAYERS: tuple[str, ...] = (L1, L2, L3, L4, L7)

# (couche, ce qu'on contrôle, outil ou indice)
LAYER_CHECKS: tuple[tuple[str, str, str], ...] = (
    (L1, "câble, prise, cordon, carte, port", "voyant de lien, testeur de câble"),
    (L2, "port du switch actif, bon VLAN, adresse MAC apprise", "voyant d'activité, arp -a, interface du switch"),
    (L3, "adresse IP, masque, passerelle ; joindre la passerelle et au-delà", "ipconfig, ping, tracert"),
    (L4, "port du service ouvert, pare-feu", "Test-NetConnection -Port, netstat"),
    (L7, "nom résolu, service démarré, identifiants, réglages du logiciel", "nslookup, message de l'application"),
)


def fault_layer(*, link_light: bool, right_vlan: bool = True, ip_ok: bool = True, gateway_ping: bool = True,
                port_open: bool = True, app_ok: bool = True) -> str | None:
    """Première couche en défaut, de bas en haut (`None` : rien à signaler). `app_ok` : nom
    résolu (DNS), service démarré, identifiants acceptés."""
    for ok, layer in ((link_light, L1), (right_vlan, L2), (ip_ok and gateway_ping, L3), (port_open, L4),
                      (app_ok, L7)):
        if not ok:
            return layer
    return None


# =============================================================================================
# 8. NetBEUI (historique)
# =============================================================================================

NETBEUI_FACTS: tuple[str, ...] = (
    ("protocole de réseau local conçu par IBM puis adopté par Microsoft (années 1980-1990), "
     "transport de NetBIOS ;"),
    "aucune adresse réseau : chaque poste est désigné par un nom NetBIOS de 15 caractères ;",
    ("**non routable** : sans adresse réseau, il ne traverse pas un routeur et reste limité à un "
     "seul réseau local ;"),
    "repose beaucoup sur la diffusion (broadcast) : bavard sur un grand réseau ;",
    "remplacé par TCP/IP : Windows XP ne l'installe plus, les systèmes actuels ne le proposent pas.",
)

# (suite de protocoles, routable ?, adressage, usage)
PROTOCOL_SUITES: tuple[tuple[str, bool, str, str], ...] = (
    ("TCP/IP", True, "adresse IP (réseau + hôte)", "Internet et tous les réseaux actuels"),
    ("NetBEUI", False, "nom NetBIOS seul", "petits réseaux Windows et OS/2 anciens"),
    ("IPX/SPX", True, "numéro de réseau + adresse MAC", "réseaux Novell NetWare anciens"),
)
ROUTABLE = {name: routable for name, routable, _a, _u in PROTOCOL_SUITES}


def crosses_router(protocol: str) -> bool:
    return ROUTABLE[protocol]


# =============================================================================================
# 9. Procédures
# =============================================================================================

CHOICE_STEPS: tuple[tuple[str, str], ...] = (
    ("Lire le besoin", "Qui doit communiquer avec qui : même réseau local, autre réseau, Internet, sans fil ?"),
    ("Situer la couche", "Signal à prolonger (1), trames d'un réseau local (2), réseaux IP à relier (3)."),
    ("Choisir l'équipement", "Répéteur ; switch ou point d'accès ; routeur ; modem pour la ligne."),
    ("Vérifier les chiffres", "Nombre de ports, débit, PoE, distance, réserve."),
    ("Justifier par écrit", "Couche, rôle, ce que l'équipement sépare ou relie, alternative écartée."),
)

PATH_STEPS: tuple[tuple[str, str], ...] = (
    ("Comparer les réseaux", "Destination dans mon réseau ? Sinon, envoi à la passerelle par défaut."),
    ("Trouver la MAC", "ARP : quelle est l'adresse MAC de la passerelle (ou du destinataire) ?"),
    ("Encapsuler", "Données → segment (ports) → paquet (IP) → trame (MAC) → bits."),
    ("Traverser le switch", "Il lit la MAC de destination et envoie la trame sur le seul bon port."),
    ("Passer le routeur", "La box retire la trame, lit l'IP, traduit l'adresse source (NAT), refait une trame."),
    ("Rejoindre le serveur", "Chaque routeur refait la trame ; l'IP de destination reste la même."),
)

DIAG_STEPS: tuple[tuple[str, str], ...] = (
    ("Physique (1)", "Voyants, câble, prise, cordon ; testeur si besoin."),
    ("Liaison (2)", "Port du switch actif, bon VLAN ; la passerelle apparaît-elle dans arp -a ?"),
    ("Réseau (3)", "ipconfig : adresse, masque, passerelle ; ping de la passerelle puis d'une IP extérieure."),
    ("Transport (4)", "Le port du service est-il joignable ? Pare-feu du poste ou du serveur."),
    ("Application (7)", "Nom résolu (nslookup), service démarré, identifiants, réglages."),
    ("Consigner", "Couche en défaut, preuve relevée, correction, contrôle refait."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Choisir l'équipement adapté", CHOICE_STEPS),
    ("Suivre un paquet du PC à Internet", PATH_STEPS),
    ("Diagnostiquer couche par couche", DIAG_STEPS),
)

# =============================================================================================
# 10. Schémas SVG
# =============================================================================================


def _marker_text(text: str) -> str:
    return f"{text} ?"


def _pc(x: float, y: float, label: str = "PC", *, key: str = "") -> str:
    data = f' data-node="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x - 15:.1f}" y="{y - 10:.1f}" width="30" height="20" rx="3" fill="{_FILL}" '
            f'stroke="{_STROKE}" stroke-width="1.4"/>'
            f'<text x="{x:.1f}" y="{y + 4:.1f}" font-size="9.5" font-weight="700" text-anchor="middle">{escape(label)}</text>')


def _line(x1: float, y1: float, x2: float, y2: float, *, key: str = "", width: float = 1.6, dash: bool = False) -> str:
    data = f' data-link="{escape(key)}"' if key else ""
    dashed = ' stroke-dasharray="5 3"' if dash else ""
    return (f'<path{data} d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{_STROKE}" '
            f'stroke-width="{width}"{dashed}/>')


def _panel_bus(ox: float, oy: float) -> list[str]:
    parts = [_line(ox + 14, oy + 62, ox + 171, oy + 62, width=3, key="bus")]
    parts.append(f'<rect data-terminator="1" x="{ox + 8}" y="{oy + 54}" width="6" height="16" fill="{_STROKE}"/>')
    parts.append(f'<rect data-terminator="1" x="{ox + 171}" y="{oy + 54}" width="6" height="16" fill="{_STROKE}"/>')
    for i, x in enumerate((ox + 40, ox + 75, ox + 110, ox + 145)):
        y = oy + 26 if i % 2 == 0 else oy + 98
        parts.append(_line(x, y + (10 if i % 2 == 0 else -10), x, oy + 62))
        parts.append(_pc(x, y))
    return parts


def _circle_points(cx: float, cy: float, r: float, n: int) -> list[tuple[float, float]]:
    return [(cx + r * math.sin(2 * math.pi * i / n), cy - r * math.cos(2 * math.pi * i / n)) for i in range(n)]


def _panel_star(ox: float, oy: float) -> list[str]:
    cx, cy = ox + 92, oy + 62
    parts = []
    points = _circle_points(cx, cy, 48, 5)
    for i, (x, y) in enumerate(points):
        parts.append(_line(cx, cy, x, y, key=f"star-{i + 1}"))
    parts.append(f'<rect x="{cx - 17}" y="{cy - 11}" width="34" height="22" rx="4" fill="#fff3c4" stroke="{_STROKE}" stroke-width="1.6"/>'
                 f'<text x="{cx}" y="{cy + 4}" font-size="9.5" font-weight="700" text-anchor="middle">SW</text>')
    parts += [_pc(x, y) for x, y in points]
    return parts


def _panel_ring(ox: float, oy: float) -> list[str]:
    points = _circle_points(ox + 92, oy + 62, 48, 5)
    parts = [_line(*points[i], *points[(i + 1) % 5], key=f"ring-{i + 1}") for i in range(5)]
    parts += [_pc(x, y) for x, y in points]
    return parts


def _panel_mesh(ox: float, oy: float) -> list[str]:
    points = [(ox + 40, oy + 22), (ox + 145, oy + 22), (ox + 145, oy + 102), (ox + 40, oy + 102)]
    parts = [_line(*points[i], *points[j], key=f"mesh-{i + 1}{j + 1}") for i in range(4) for j in range(i + 1, 4)]
    parts += [_pc(x, y, f"R{i + 1}") for i, (x, y) in enumerate(points)]
    return parts


_PANELS = {TOPO_BUS: _panel_bus, TOPO_STAR: _panel_star, TOPO_RING: _panel_ring, TOPO_MESH: _panel_mesh}
TOPO_PANEL_ORDER: tuple[str, ...] = (TOPO_BUS, TOPO_STAR, TOPO_RING, TOPO_MESH)


def topologies_svg(order: tuple[str, ...] = TOPO_PANEL_ORDER, *, blanks: tuple[str, ...] = ()) -> str:
    """Quatre topologies en 2 × 2 cases. `blanks` : numéros affichés à la place des noms (schéma
    à compléter, dans l'ordre des cases)."""
    width = 380
    parts: list[str] = []
    for index, name in enumerate(order):
        ox, oy = 4 + (index % 2) * 188, 4 + (index // 2) * 158
        hidden = bool(blanks)
        data = "" if hidden else f' data-topology="{escape(name)}"'
        parts.append(f'<g{data}><rect x="{ox}" y="{oy}" width="184" height="152" rx="6" fill="{_SOFT}" '
                     f'stroke="#c4cad6"/>')
        parts += _PANELS[name](ox, oy)
        if hidden:
            label = _marker_text(blanks[index])
        elif name == TOPO_MESH:
            label = f"Maillage complet ({mesh_links(4)} liaisons)"
        else:
            label = name
        parts.append(_text_lines(int(ox + 92), int(oy + 140), [label], size=11, weight="700", anchor="middle"))
        parts.append("</g>")
    notes = _wrap("PC : station ; SW : switch central ; R : routeur ; barres noires : bouchons de fin de bus.", 62)
    y = 4 + 2 * 158 + 14
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def osi_svg(*, blanks: dict[str, str] | None = None) -> str:
    """Modèle OSI (7 couches, unité de données) face au modèle TCP/IP (4 couches). `blanks` :
    clés « osi-N » (nom de la couche N), « pdu-N » (unité de la couche N) ou « tcpip-Nom »
    remplacées par un numéro à compléter."""
    blanks = blanks or {}
    width, top, row_h = 380, 40, 30
    parts = [
        _text_lines(8, 16, ["Modèle OSI"], size=11.5, weight="700"),
        _text_lines(160, 16, ["Unité"], size=11.5, weight="700"),
        _text_lines(262, 16, ["Modèle TCP/IP"], size=11.5, weight="700"),
        _text_lines(8, 31, ["(n° et nom de la couche)"], size=9.5),
    ]
    for index, layer in enumerate(OSI_LAYERS):
        y = top + index * row_h
        name_key, pdu_key = f"osi-{layer.number}", f"pdu-{layer.number}"
        name = _marker_text(blanks[name_key]) if name_key in blanks else layer.name
        pdu = _marker_text(blanks[pdu_key]) if pdu_key in blanks else layer.pdu.split(" (")[0]
        data_name = "" if name_key in blanks else escape(layer.name)
        parts.append(f'<rect data-layer="{layer.number}" data-name="{data_name}" x="6" y="{y}" width="244" height="{row_h - 3}" '
                     f'rx="4" fill="{"#ffffff" if name_key in blanks else _FILL}" stroke="{_STROKE}" stroke-width="1.2"/>')
        parts.append(_text_lines(16, y + 18, [f"{layer.number}"], size=11.5, weight="700"))
        parts.append(_text_lines(32, y + 18, [name], size=11, weight="700"))
        parts.append(_text_lines(160, y + 18, [pdu], size=10.5))
    for name, covered, protocols in TCPIP_LAYERS:
        first = OSI_LAYERS[[layer.number for layer in OSI_LAYERS].index(max(covered))]
        index = OSI_LAYERS.index(first)
        y = top + index * row_h
        height = len(covered) * row_h - 3
        key = f"tcpip-{name}"
        label = _marker_text(blanks[key]) if key in blanks else name
        data = "" if key in blanks else escape(name)
        parts.append(f'<rect data-tcpip="{data}" x="258" y="{y}" width="116" height="{height}" rx="4" '
                     f'fill="{"#ffffff" if key in blanks else "#fff3c4"}" stroke="{_STROKE}" stroke-width="1.2"/>')
        if len(covered) == 1:
            parts.append(_text_lines(316, y + 12, [label], size=10.5, weight="700", anchor="middle"))
            parts.append(_text_lines(316, y + 24, [protocols], size=9, anchor="middle"))
        else:
            lines = _wrap(protocols, 18)
            start = int(y + height / 2 - 6.5 * len(lines) + 2)
            parts.append(_text_lines(316, start, [label], size=10.5, weight="700", anchor="middle"))
            parts.append(_text_lines(316, start + 14, lines, size=9.5, anchor="middle", step=12))
    y = top + 7 * row_h + 14
    notes = _wrap("L'émetteur descend les couches (7 → 1) en ajoutant un en-tête à chaque niveau ; le "
                  "récepteur les remonte (1 → 7) en les retirant.", 62)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def _box(x: float, y: float, w: float, text: str, *, fill: str = _FILL, key: str = "", dash: bool = False) -> str:
    data = f' data-part="{escape(key)}"' if key else ""
    dashed = ' stroke-dasharray="4 3"' if dash else ""
    return (f'<rect{data} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="28" rx="3" fill="{fill}" stroke="{_STROKE}" '
            f'stroke-width="1.3"{dashed}/>'
            f'<text x="{x + w / 2:.1f}" y="{y + 18:.1f}" font-size="10.5" font-weight="700" text-anchor="middle">{escape(text)}</text>')


def encapsulation_svg(enc: Encapsulation, *, blanks: dict[str, str] | None = None) -> str:
    """Quatre lignes : données, segment, paquet, trame ; chaque niveau ajoute son en-tête
    (et la trame son FCS). `blanks` : « segment », « packet », « frame » (taille) ou
    « h-transport », « h-ip », « h-eth », « fcs » (taille de l'en-tête) masqués."""
    blanks = blanks or {}
    t = enc.transport
    th = TRANSPORT_HEADER[t]

    def size(key: str, value: int) -> str:
        return _marker_text(blanks[key]) if key in blanks else f"{octets(value)} octets"

    def hdr(key: str, label: str, value: int) -> str:
        return f"{label} {_marker_text(blanks[key])}" if key in blanks else f"{label} {value}"

    width = 380
    x_eth, x_ip, x_tr, x_data, x_fcs, x_end = 6, 66, 126, 186, 316, 374
    unit = "Datagramme UDP" if t == "UDP" else "Segment TCP"
    rows = (
        (f"Données de l'application : {octets(enc.data)} octets", [("data", x_data, x_fcs - x_data, f"Données {octets(enc.data)}")]),
        (f"{unit} : {size('segment', enc.segment)}",
         [("h-transport", x_tr, x_data - x_tr, hdr("h-transport", t, th)), ("data", x_data, x_fcs - x_data, "Données")]),
        (f"Paquet IP : {size('packet', enc.packet)}",
         [("h-ip", x_ip, x_tr - x_ip, hdr("h-ip", "IP", IPV4_HEADER)), ("h-transport", x_tr, x_data - x_tr, t),
          ("data", x_data, x_fcs - x_data, "Données")]),
        (f"Trame Ethernet : {size('frame', enc.frame)}",
         [("h-eth", x_eth, x_ip - x_eth, hdr("h-eth", "Eth", ETH_HEADER)), ("h-ip", x_ip, x_tr - x_ip, "IP"),
          ("h-transport", x_tr, x_data - x_tr, t), ("data", x_data, x_fcs - x_data, "Données"),
          ("fcs", x_fcs, x_end - x_fcs, hdr("fcs", "FCS", ETH_FCS))]),
    )
    parts: list[str] = []
    y = 6
    for label, boxes in rows:
        parts.append(_text_lines(8, y + 12, [label], size=11, weight="700"))
        for key, x, w, text in boxes:
            fill = "#ffffff" if text.endswith("?") else (_SOFT if key == "data" else _FILL)
            parts.append(_box(x, y + 18, w, text, fill=fill, key=key))
        y += 58
    if enc.padding:
        parts.append(_text_lines(8, y + 4, [f"Bourrage : {enc.padding} octets ajoutés (données de trame ≥ {ETH_MIN_PAYLOAD})."],
                                 size=10.5, weight="700"))
        y += 16
    transport = "" if "h-transport" in blanks else "TCP 20, UDP 8, "  # un schéma à compléter ne donne pas sa réponse
    notes = _wrap(f"En-têtes sans option : {transport}IPv4 20, Ethernet 14 (MAC destination, MAC "
                  "source, type) + FCS 4 octets. Préambule de 8 octets non compté.", 62)
    parts.append(_text_lines(8, y + 6, notes, size=10.5, step=13))
    return _svg(width, y + 6 + 13 * len(notes), parts)


def frame_svg(*, blanks: dict[int, str] | None = None) -> str:
    """Champs d'une trame Ethernet dans l'ordre d'émission ; `blanks` (index du champ →
    numéro) masque le nom du champ, pas sa taille."""
    blanks = blanks or {}
    widths = (70, 70, 52, 120, 56)
    width, top = 380, 30
    parts = [_text_lines(width // 2, 16, ["Trame Ethernet (IEEE 802.3 / Ethernet II)"], size=12, weight="700", anchor="middle")]
    x = 6
    for index, ((name, size), w) in enumerate(zip(FRAME_FIELDS, widths, strict=True)):
        hidden = index in blanks
        lines = [_marker_text(blanks[index])] if hidden else _wrap(name, max(6, int(w / 6.4)))
        data = "" if hidden else escape(name)
        parts.append(f'<rect data-field="{data}" data-size="{escape(size)}" x="{x}" y="{top}" width="{w - 3}" height="74" rx="4" '
                     f'fill="{"#ffffff" if hidden else (_SOFT if index == 3 else _FILL)}" stroke="{_STROKE}" stroke-width="1.3"/>')
        parts.append(_text_lines(int(x + (w - 3) / 2), top + 16, lines, size=9.5, weight="700", anchor="middle", step=12))
        parts.append(_text_lines(int(x + (w - 3) / 2), top + 66, [f"{size} o"], size=10, anchor="middle"))
        x += w
    y = top + 96
    if blanks:  # un schéma à compléter ne donne pas ses réponses dans la légende
        notes = _wrap(f"Trame de {ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)} octets, préambule de {PREAMBLE} octets non compté.", 62)
        parts.append(_text_lines(8, y, notes, size=10.5, step=13))
        return _svg(width, y + 13 * len(notes), parts)
    notes = _wrap(
        f"Trame de {ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)} octets (en-tête {ETH_HEADER} + données "
        f"{ETH_MIN_PAYLOAD} à {octets(ETH_MTU)} + FCS {ETH_FCS}). Type : "
        + ", ".join(f"{code} = {name}" for code, name in ETHERTYPES)
        + f". Destination {BROADCAST_MAC} : diffusion à tout le réseau local.", 62)
    parts.append(_text_lines(8, y, notes, size=10.5, step=13))
    return _svg(width, y + 13 * len(notes), parts)


def _node(x: float, y: float, w: float, lines: list[str], *, fill: str = _FILL, key: str = "") -> str:
    h = 12 + 13 * len(lines)
    data = f' data-node="{escape(key)}"' if key else ""
    return (f'<rect{data} x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{fill}" '
            f'stroke="{_STROKE}" stroke-width="1.4"/>'
            + _text_lines(int(x), int(y + 15), lines[:1], size=10.5, weight="700", anchor="middle")
            + _text_lines(int(x), int(y + 28), lines[1:], size=10, anchor="middle", step=13))


PATH_FIELDS: tuple[tuple[str, str], ...] = (
    ("src_mac", "MAC source"), ("dst_mac", "MAC destination"), ("src_ip", "IP source"), ("dst_ip", "IP destination"),
)


def path_svg(frames: tuple[FrameView, FrameView] = PATH_FRAMES, *, blanks: dict[tuple[int, str], str] | None = None) -> str:
    """Chaîne PC → switch → box → routeur de l'opérateur → serveur, puis tableau des adresses
    des deux trames. `blanks` : (index de trame, champ) → numéro à compléter."""
    blanks = blanks or {}
    width = 380
    chain = (
        ("pc", [PC.owner, f"{PC.ip} · {PC.mac}"], _FILL),
        ("switch", ["Switch", "lit la MAC, ne modifie rien"], _SOFT),
        ("box", ["Box (routeur + NAT)", f"LAN {BOX_LAN.ip} · {BOX_LAN.mac}", f"WAN {BOX_WAN.ip} · {BOX_WAN.mac}"], "#fff3c4"),
        ("isp", [ISP_ROUTER.owner, f"{ISP_ROUTER.ip} · {ISP_ROUTER.mac}"], _FILL),
        ("internet", ["Internet : autres routeurs"], _SOFT),
        ("server", [f"Serveur {SERVER_NAME}", SERVER_IP], _FILL),
    )
    parts: list[str] = []
    y = 6
    for index, (key, lines, fill) in enumerate(chain):
        parts.append(_node(190, y, 260, lines, fill=fill, key=key))
        y += 12 + 13 * len(lines)
        if index < len(chain) - 1:
            parts.append(f'<path d="M190 {y} V{y + 14}" stroke="{_STROKE}" stroke-width="2"/>')
            if key in ("pc", "box"):
                n = 1 if key == "pc" else 2
                parts.append(_text_lines(326, y + 11, [f"trame {n}"], size=10, weight="700"))
            y += 14
    y += 14
    col = (8, 104, 240)
    parts.append(_text_lines(col[0], y, ["Champ"], size=10.5, weight="700"))
    parts.append(_text_lines(col[1], y, ["Trame 1", "PC → box"], size=10.5, weight="700", step=13))
    parts.append(_text_lines(col[2], y, ["Trame 2", "box → opérateur"], size=10.5, weight="700", step=13))
    y += 21
    for field, label in PATH_FIELDS:
        parts.append(f'<rect x="6" y="{y}" width="368" height="20" rx="3" fill="{_SOFT}" stroke="#c4cad6"/>')
        parts.append(_text_lines(col[0] + 2, y + 14, [label], size=10))
        for n, frame in enumerate(frames):
            value = _marker_text(blanks[(n, field)]) if (n, field) in blanks else getattr(frame, field)
            parts.append(_text_lines(col[1 + n], y + 14, [value], size=10, weight="700"))
        y += 22
    notes = _wrap("Les adresses MAC changent à chaque routeur ; l'adresse IP de destination reste la "
                  "même ; la box remplace l'adresse IP source privée par son adresse publique (NAT).", 62)
    parts.append(_text_lines(8, y + 12, notes, size=10.5, step=13))
    return _svg(width, y + 12 + 13 * len(notes), parts)


_KIND_FILL = {N_ROUTER: "#fff3c4", N_SWITCH: _FILL, N_HUB: "#f6d9d6", N_PC: _SOFT, N_REPEATER: "#f6d9d6", N_BRIDGE: _FILL}


def domains_svg(lan: Lan, *, numbered: bool = True, zones: bool = True) -> str:
    """Plan d'un réseau. `numbered` : numéro du domaine de collision au milieu de chaque
    liaison ; `zones` : fond coloré et nom de chaque domaine de diffusion."""
    width = 380
    pos = {n: (x, y) for n, _k, x, y in lan.nodes}
    kinds = lan.kinds
    collisions = collision_domain_of_links(lan)
    broadcasts = broadcast_domain_of_links(lan)
    parts: list[str] = []
    bottom = max(y for _n, _k, _x, y in lan.nodes) + 36
    if zones:
        for domain in sorted(set(broadcasts)):
            members = {n for (a, b), d in zip(lan.links, broadcasts, strict=True) if d == domain for n in (a, b)
                       if kinds[n] != N_ROUTER}
            xs = [pos[n][0] for n in members]
            ys = [pos[n][1] for n in members]
            x0, x1, y0, y1 = min(xs) - 24, max(xs) + 24, min(ys) - 26, max(ys) + 30
            fill = _ZONE_A if domain % 2 else _ZONE_B
            parts.append(f'<rect data-broadcast="{domain}" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" '
                         f'fill="{fill}" stroke="#9aa4b5" stroke-dasharray="6 4"/>')
            parts.append(_text_lines(int(x0 + 6), int(y1 - 6), [f"Diffusion {domain}"], size=9.5, weight="700"))
    for (a, b), c in zip(lan.links, collisions, strict=True):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        parts.append(f'<path data-link="{a}-{b}" data-collision="{c if numbered else ""}" d="M{x1} {y1} L{x2} {y2}" '
                     f'stroke="{_STROKE}" stroke-width="1.6"/>')
    for name, kind, x, y in lan.nodes:
        w = 44 if kind != N_PC else 36
        parts.append(f'<rect data-device="{name}" data-kind="{kind}" x="{x - w / 2}" y="{y - 11}" width="{w}" height="22" rx="4" '
                     f'fill="{_KIND_FILL[kind]}" stroke="{_STROKE}" stroke-width="1.4"/>')
        parts.append(_text_lines(int(x), int(y + 4), [name], size=9.5, weight="700", anchor="middle"))
    if numbered:
        for (a, b), c in zip(lan.links, collisions, strict=True):
            (x1, y1), (x2, y2) = pos[a], pos[b]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            parts.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="8" fill="#ffffff" stroke="{_BAD}" stroke-width="1.4"/>'
                         f'<text x="{mx:.1f}" y="{my + 3.5:.1f}" font-size="9.5" font-weight="700" text-anchor="middle">{c}</text>')
    legend = ["R : routeur ; SW : switch ; HUB : hub ; PC : poste."]
    if numbered:
        legend.append(f"Cercles : n° du domaine de collision de chaque liaison ({len(set(collisions))} domaines).")
    if zones:
        legend.append(f"Fonds pointillés : domaines de diffusion ({len(set(broadcasts))}).")
    wrapped = [line for text in legend for line in _wrap(text, 62)]
    parts.append(_text_lines(8, bottom + 12, wrapped, size=10.5, step=13))
    return _svg(width, bottom + 12 + 13 * len(wrapped), parts)


LAYER_BANDS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("Couche 3 — réseau (adresse IP)", (DEV_ROUTER,), "sépare les domaines de collision et de diffusion"),
    ("Couche 2 — liaison (adresse MAC)", (DEV_SWITCH, DEV_BRIDGE, DEV_AP), "sépare les domaines de collision"),
    ("Couche 1 — physique (bits)", (DEV_HUB, DEV_REPEATER, DEV_MODEM), "ne sépare rien : recopie ou convertit le signal"),
)


def devices_svg() -> str:
    width, parts, y = 380, [], 6
    for title, names, effect in LAYER_BANDS:
        parts.append(f'<rect data-band="{escape(title)}" x="6" y="{y}" width="368" height="74" rx="6" fill="{_SOFT}" stroke="#c4cad6"/>')
        parts.append(_text_lines(14, y + 17, [title], size=11, weight="700"))
        x = 14
        for name in names:
            w = 112
            parts.append(f'<rect data-device="{escape(name)}" x="{x}" y="{y + 25}" width="{w}" height="24" rx="4" fill="{_FILL}" stroke="{_STROKE}"/>')
            parts.append(_text_lines(int(x + w / 2), y + 41, [name], size=10.5, weight="700", anchor="middle"))
            x += w + 9
        parts.append(_text_lines(14, y + 66, [effect], size=10))
        y += 80
    notes = _wrap("La box d'un particulier réunit plusieurs équipements : modem, routeur avec NAT, petit "
                  "switch, point d'accès Wi-Fi, serveurs DHCP et DNS.", 62)
    parts.append(_text_lines(8, y + 10, notes, size=10.5, step=13))
    return _svg(width, y + 10 + 13 * len(notes), parts)


TOPO_FIGURE = Figure(
    key="pr19-topologies",
    title="Les quatre topologies : bus, étoile, anneau, maillage",
    alt=(
        "Quatre cases. Bus : un câble horizontal fermé par un bouchon à chaque bout, quatre PC branchés dessus. "
        "Étoile : un switch au centre relié par un câble distinct à cinq PC. Anneau : cinq PC reliés chacun au "
        f"suivant, le dernier au premier. Maillage complet : quatre routeurs reliés chacun aux trois autres, {mesh_links(4)} liaisons."
    ),
    caption="Bus et anneau : une coupure peut tout arrêter ; étoile : un câble coupé n'isole qu'un poste ; maillage : chemin de secours.",
    svg=topologies_svg(),
)

OSI_FIGURE = Figure(
    key="pr19-osi-tcpip",
    title="Modèle OSI à 7 couches et modèle TCP/IP à 4 couches",
    alt=(
        "Colonne OSI, de haut en bas : "
        + " ; ".join(f"{layer.number} {layer.name}, unité : {layer.pdu}" for layer in OSI_LAYERS)
        + ". Colonne TCP/IP : "
        + " ; ".join(f"{name} (couches OSI {', '.join(str(c) for c in covered)} : {p})" for name, covered, p in TCPIP_LAYERS)
        + "."
    ),
    caption="Le modèle OSI sert à raisonner et à situer une panne ; TCP/IP est la pile réellement utilisée.",
    svg=osi_svg(),
)

ENCAP_FIGURE = Figure(
    key="pr19-encapsulation",
    title=f"Encapsulation de {octets(ENCAP_EXAMPLE.data)} octets de données en TCP",
    alt=(
        f"Données de l'application : {octets(ENCAP_EXAMPLE.data)} octets. Segment TCP : en-tête TCP de 20 octets + données = "
        f"{octets(ENCAP_EXAMPLE.segment)} octets. Paquet IP : en-tête IP de 20 octets + segment = {octets(ENCAP_EXAMPLE.packet)} "
        f"octets, la MTU Ethernet. Trame Ethernet : en-tête de 14 octets + paquet + FCS de 4 octets = {octets(ENCAP_EXAMPLE.frame)} octets."
    ),
    caption="Chaque couche ajoute son en-tête devant les données de la couche du dessus ; Ethernet ajoute aussi le FCS à la fin.",
    svg=encapsulation_svg(ENCAP_EXAMPLE),
)

FRAME_FIGURE = Figure(
    key="pr19-trame-ethernet",
    title="Champs d'une trame Ethernet",
    alt=(
        "Champs dans l'ordre : "
        + " ; ".join(f"{name}, {size} octets" for name, size in FRAME_FIELDS)
        + f". Trame de {ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)} octets. Types : "
        + ", ".join(f"{c} {n}" for c, n in ETHERTYPES)
        + f". L'adresse {BROADCAST_MAC} désigne tous les appareils du réseau local."
    ),
    caption="Le switch lit l'adresse MAC de destination ; le champ Type dit ce que transportent les données.",
    svg=frame_svg(),
)

PATH_FIGURE = Figure(
    key="pr19-chemin-paquet",
    title="Chemin d'un paquet : PC → switch → box → Internet",
    alt=(
        f"{PC.owner} ({PC.ip}, {PC.mac}) → switch → box (côté réseau local {BOX_LAN.ip}, {BOX_LAN.mac} ; côté opérateur "
        f"{BOX_WAN.ip}, {BOX_WAN.mac}) → {ISP_ROUTER.owner.lower()} ({ISP_ROUTER.ip}, {ISP_ROUTER.mac}) → Internet → serveur "
        f"{SERVER_NAME} ({SERVER_IP}). "
        + " ".join(
            f"Trame {n} : MAC source {f.src_mac}, MAC destination {f.dst_mac}, IP source {f.src_ip}, IP destination {f.dst_ip}."
            for n, f in enumerate(PATH_FRAMES, start=1)
        )
    ),
    caption="Le switch ne change rien ; à chaque routeur, nouvelle trame (nouvelles MAC) ; la box traduit l'IP source (NAT).",
    svg=path_svg(),
)

DOMAINS_FIGURE = Figure(
    key="pr19-domaines",
    title="Domaines de collision et de diffusion",
    alt=(
        "Un routeur R1 relié à deux switchs. SW1 relie PC1, PC2 et un hub ; le hub relie PC3 et PC4. SW2 relie PC5 et "
        f"PC6. {DOMAINS_COLLISIONS} domaines de collision : chaque liaison d'un switch ou du routeur est un domaine ; le hub "
        f"et ses trois liaisons (vers SW1, PC3, PC4) n'en forment qu'un. {DOMAINS_BROADCASTS} domaines de diffusion : un "
        "par interface du routeur."
    ),
    caption="Le switch sépare les collisions, pas les diffusions ; le routeur sépare les deux ; le hub ne sépare rien.",
    svg=domains_svg(DOMAINS_LAN),
)

DEVICES_FIGURE = Figure(
    key="pr19-equipements-couches",
    title="Équipements rangés par couche",
    alt=(
        "Trois bandes. "
        + " ".join(f"{title} : {', '.join(names)} ; {effect}." for title, names, effect in LAYER_BANDS)
        + " La box réunit modem, routeur avec NAT, switch, point d'accès, DHCP et DNS."
    ),
    caption="Plus l'équipement travaille haut dans les couches, plus il lit d'informations pour décider.",
    svg=devices_svg(),
)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


CHOICE_FIGURE = _proc_figure("pr19-procedure-choix", 1, PROCEDURES[0][0], CHOICE_STEPS,
                             "On part du besoin, pas du catalogue : la couche du problème donne la famille d'équipement.")
PATH_STEPS_FIGURE = _proc_figure("pr19-procedure-chemin", 2, PROCEDURES[1][0], PATH_STEPS,
                                 "Même raisonnement pour tout échange : local ou distant, puis ARP, puis encapsulation.")
DIAG_FIGURE = _proc_figure("pr19-procedure-diagnostic", 3, PROCEDURES[2][0], DIAG_STEPS,
                           "De bas en haut : la première couche en défaut est celle qu'on corrige.")

PR19_FIGURES: tuple[Figure, ...] = (
    TOPO_FIGURE,
    OSI_FIGURE,
    ENCAP_FIGURE,
    FRAME_FIGURE,
    PATH_FIGURE,
    DOMAINS_FIGURE,
    DEVICES_FIGURE,
    CHOICE_FIGURE,
    PATH_STEPS_FIGURE,
    DIAG_FIGURE,
)

# =============================================================================================
# 11. Schémas à compléter (exercices) : figures et fichiers statiques
# =============================================================================================

# Ordre des cases différent de celui du cours.
TOPO_BLANK_ORDER: tuple[str, ...] = (TOPO_RING, TOPO_MESH, TOPO_BUS, TOPO_STAR)
TOPO_BLANKS: tuple[str, ...] = ("①", "②", "③", "④")

TOPO_BLANK_FIGURE = Figure(
    key="pr19-topologies-a-completer",
    title="Quatre topologies à nommer",
    alt=(
        "Quatre cases numérotées, sans nom. ① cinq PC reliés chacun au suivant, le dernier au premier. "
        "② quatre routeurs R1 à R4, chacun relié aux trois autres. ③ un câble horizontal fermé par un bouchon "
        "à chaque bout, quatre PC branchés dessus. ④ un switch au centre relié par un câble distinct à cinq PC."
    ),
    caption="Schéma à compléter : nommer chaque topologie et citer l'effet d'une coupure.",
    svg=topologies_svg(TOPO_BLANK_ORDER, blanks=TOPO_BLANKS),
)

OSI_BLANKS: dict[str, str] = {
    "osi-6": "①", "osi-4": "②", "osi-3": "③", "osi-2": "④", "tcpip-Internet": "⑤", "pdu-3": "⑥", "pdu-2": "⑦",
}
OSI_BLANK_ANSWERS: dict[str, str] = {
    "①": OSI_BY_NUMBER[6].name, "②": OSI_BY_NUMBER[4].name, "③": OSI_BY_NUMBER[3].name,
    "④": OSI_BY_NUMBER[2].name, "⑤": tcpip_layer_for(3), "⑥": OSI_BY_NUMBER[3].pdu, "⑦": OSI_BY_NUMBER[2].pdu,
}

OSI_BLANK_FIGURE = Figure(
    key="pr19-osi-a-completer",
    title="Modèles OSI et TCP/IP à compléter",
    alt=(
        "Colonne OSI, de haut en bas : 7 Application (données) ; 6 ① (données) ; 5 Session (données) ; "
        "4 ② (segment) ; 3 ③ (unité ⑥) ; 2 ④ (unité ⑦) ; 1 Physique (bit). Colonne TCP/IP : Application en face "
        "des couches 7, 6 et 5 ; Transport en face de 4 (TCP, UDP) ; ⑤ en face de 3 (IP, ICMP) ; Accès réseau "
        "en face de 2 et 1 (Ethernet, Wi-Fi)."
    ),
    caption="Schéma à compléter : noms de couches, couche TCP/IP et unités de données manquants.",
    svg=osi_svg(blanks=OSI_BLANKS),
)

ENCAP_BLANK = encapsulate(40, "UDP")  # requête DNS : 40 → 48 → 68 → 86
ENCAP_BLANKS: dict[str, str] = {"segment": "①", "packet": "②", "frame": "③", "h-transport": "④"}

ENCAP_BLANK_FIGURE = Figure(
    key="pr19-encapsulation-a-completer",
    title="Encapsulation d'une requête DNS à compléter",
    alt=(
        f"Données de l'application : {ENCAP_BLANK.data} octets (une requête DNS). Datagramme UDP : en-tête UDP de ④ octets + "
        "données = ① octets. Paquet IP : en-tête IP de 20 octets + datagramme = ② octets. Trame Ethernet : en-tête "
        "Ethernet de 14 octets + paquet + FCS de 4 octets = ③ octets."
    ),
    caption="Schéma à compléter : taille de l'en-tête UDP et tailles du datagramme, du paquet et de la trame.",
    svg=encapsulation_svg(ENCAP_BLANK, blanks=ENCAP_BLANKS),
)

PATH_BLANKS: dict[tuple[int, str], str] = {
    (0, "dst_mac"): "①", (1, "src_mac"): "②", (1, "dst_mac"): "③", (1, "src_ip"): "④", (1, "dst_ip"): "⑤",
}

PATH_BLANK_FIGURE = Figure(
    key="pr19-chemin-a-completer",
    title="Adresses des trames à compléter",
    alt=(
        f"{PC.owner} ({PC.ip}, {PC.mac}) → switch → box (côté réseau local {BOX_LAN.ip}, {BOX_LAN.mac} ; côté opérateur "
        f"{BOX_WAN.ip}, {BOX_WAN.mac}) → {ISP_ROUTER.owner.lower()} ({ISP_ROUTER.ip}, {ISP_ROUTER.mac}) → Internet → serveur "
        f"{SERVER_NAME} ({SERVER_IP}). Trame 1 (PC vers box) : MAC source {PC.mac}, MAC destination ①, IP source {PC.ip}, "
        f"IP destination {SERVER_IP}. Trame 2 (box vers opérateur) : MAC source ②, MAC destination ③, IP source ④, IP "
        "destination ⑤."
    ),
    caption="Schéma à compléter : adresses MAC et IP manquantes des deux trames.",
    svg=path_svg(blanks=PATH_BLANKS),
)

DOMAINS_BLANK_FIGURE = Figure(
    key="pr19-domaines-a-completer",
    title="Domaines à compter",
    alt=(
        "Un routeur R1 a deux interfaces. La première est reliée à un switch SW1, qui relie quatre postes PC1 à PC4. "
        "La seconde est reliée à un hub, qui relie trois postes PC5 à PC7."
    ),
    caption="Schéma à compléter : compter les domaines de collision et de diffusion.",
    svg=domains_svg(DOMAINS_BLANK_LAN, numbered=False, zones=False),
)

FRAME_BLANKS: dict[int, str] = {0: "①", 1: "②", 2: "③", 4: "④"}

FRAME_BLANK_FIGURE = Figure(
    key="pr19-trame-a-completer",
    title="Champs d'une trame Ethernet à compléter",
    alt=(
        "Cinq champs dans l'ordre d'émission : ① 6 octets ; ② 6 octets ; ③ 2 octets ; Données (paquet IP) de "
        f"{ETH_MIN_PAYLOAD} à {octets(ETH_MTU)} octets ; ④ 4 octets."
    ),
    caption="Schéma à compléter : nommer les champs ① à ④ et donner leur rôle.",
    svg=frame_svg(blanks=FRAME_BLANKS),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (TOPO_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-topologies-a-completer.svg"),
    (OSI_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-osi-a-completer.svg"),
    (ENCAP_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-encapsulation-a-completer.svg"),
    (PATH_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-chemin-a-completer.svg"),
    (DOMAINS_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-domaines-a-completer.svg"),
    (FRAME_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr19-trame-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle qu'EX01 et PR18)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

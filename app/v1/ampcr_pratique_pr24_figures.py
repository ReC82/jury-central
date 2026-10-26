"""PR24 « Dépannage réseau et Internet — dossiers d'intervention écrits » — réseau de référence,
relevés de commandes fictifs et schémas SVG (ticket #200).

Tout est construit **depuis des données** : le réseau de référence (`LAN_HOSTS`, `SWITCH_PORTS`)
et les fonctions qui produisent les relevés (`win_ping_lines`, `tracert_lines`,
`nslookup_lines`, `dig_lines`, `dnsmasq_lines`, `netsh_wlan_lines`, `arp_lines`,
`route_print_lines`, `ip_link_lines`, `ip_neigh_lines`, `resolvectl_lines`, `netstat_lines`).
Les calculs d'adressage reprennent le modèle de PR20 (`app.v1.ampcr_pratique_pr20_figures`,
module standard `ipaddress`) ; les tests du ticket vérifient la cohérence de chaque relevé
(statistiques de ping, premier saut = passerelle, taille de l'étendue DHCP, adresses MAC…).

Les relevés sont des **captures fictives simplifiées** (Windows en français, Linux en anglais),
au format réel des commandes mais raccourcies pour rester lisibles sur mobile (56 caractères
par ligne au plus). Les adresses publiques viennent des plages de documentation de la
RFC 5737 (198.51.100.0/24, 203.0.113.0/24), jamais attribuées sur Internet. Aucun schéma ne
vient d'une image générée.
"""

import ipaddress
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr20_figures import (
    Host,
    _box,
    ipconfig_all_lines,
    mac_linux,
    normalize_mac,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (écran de 380 px, comme PR20)
FICTIVE_LABEL = "capture fictive — présentation simplifiée"

# =============================================================================================
# 1. Le réseau de référence : PME « Atelier Durant » (fictive)
# =============================================================================================

LAN_NETWORK = "192.168.20.0/24"
LAN_PREFIX = 24
ROUTER_IP = "192.168.20.1"  # box/routeur : passerelle, NAT, pare-feu
SERVER_IP = "192.168.20.5"  # SRV-01 (Linux, dnsmasq) : DHCP et DNS interne, relaie le reste
NAS_IP = "192.168.20.10"
PRINTER_IP = "192.168.20.20"
AP_IP = "192.168.20.30"
POOL = ("192.168.20.100", "192.168.20.199")
DOMAIN = "atelier.lan"  # suffixe DNS interne fictif
WAN_IP = "203.0.113.45"  # adresse publique de la box (RFC 5737)
ISP_DNS = "198.51.100.53"  # DNS du fournisseur d'accès (fictif, RFC 5737)
WEB_NAME = "www.exemple.be"
WEB_IP = "198.51.100.20"  # site Internet de test (fictif, RFC 5737)
SSID = "ATELIER-PRO"
GUEST_SSID = "ATELIER-INVITES"
GUEST_VLAN = 30
GUEST_NETWORK = "10.30.0.0/24"  # réseau invités (VLAN 30), isolé du réseau interne
SRV_FQDN = f"srv-01.{DOMAIN}"
NAS_FQDN = f"nas-01.{DOMAIN}"
SHARE_UNC = "\\\\NAS-01\\Compta"
LEASE_DAYS = 8  # durée des baux de SRV-01 (dhcp-range=…,8d)


def pool_size(pool: tuple[str, str] = POOL) -> int:
    low, high = (int(ipaddress.IPv4Address(a)) for a in pool)
    return high - low + 1


def in_network(address: str, network: str = LAN_NETWORK) -> bool:
    return ipaddress.IPv4Address(address) in ipaddress.IPv4Network(network)


def in_pool(address: str, pool: tuple[str, str] = POOL) -> bool:
    low, high = (ipaddress.IPv4Address(a) for a in pool)
    return low <= ipaddress.IPv4Address(address) <= high


def is_documentation(address: str) -> bool:
    """Adresse des plages de documentation (RFC 5737) : jamais attribuée sur Internet."""
    ip = ipaddress.IPv4Address(address)
    return any(ip in ipaddress.IPv4Network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))


LAN_HOSTS: tuple[Host, ...] = (
    Host("BOX-01", "routeur, NAT, pare-feu", ROUTER_IP, LAN_PREFIX, None, (), "00-1D-AA-4E-20-01"),
    Host("SRV-01", "serveur DHCP et DNS", SERVER_IP, LAN_PREFIX, ROUTER_IP, ("127.0.0.1",), "00-15-5D-0A-20-05"),
    Host("NAS-01", "stockage, partage Compta", NAS_IP, LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "00-11-32-AA-20-10"),
    Host("IMP-01", "imprimante réseau", PRINTER_IP, LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "00-80-77-31-20-20"),
    Host("AP-01", "point d'accès Wi-Fi (PoE)", AP_IP, LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "9C-53-22-10-20-30"),
    Host("PC-01", "poste Windows, DHCP", "192.168.20.101", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-20-01", dhcp=True),
    Host("PC-02", "poste Windows, DHCP", "192.168.20.102", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-20-02", dhcp=True),
    Host("PC-03", "poste Windows, DHCP", "192.168.20.103", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-20-03", dhcp=True),
    Host("PC-04", "poste Linux, DHCP", "192.168.20.104", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "52-54-00-3A-20-04", dhcp=True),
    Host("LT-01", "portable Wi-Fi, DHCP", "192.168.20.150", LAN_PREFIX, ROUTER_IP, (SERVER_IP,), "A4-C3-F0-55-20-50", dhcp=True),
)
LAN_BY_NAME: dict[str, Host] = {h.name: h for h in LAN_HOSTS}


@dataclass(frozen=True)
class SwitchPort:
    number: int
    device: str  # nom de l'équipement raccordé (ou « — »)
    link: bool
    speed: str  # « 1 Gb/s », « 100 Mb/s », « — »
    duplex: str  # « full », « half », « — »
    vlan: int
    crc_errors: int  # compteur d'erreurs du port (CRC, collisions tardives…)
    poe_w: float = 0.0  # puissance PoE délivrée sur le port
    admin_up: bool = True

    @property
    def state(self) -> str:
        if not self.admin_up:
            return "désactivé (admin)"
        return "lien actif" if self.link else "pas de lien"


SWITCH_PORTS: tuple[SwitchPort, ...] = (
    SwitchPort(1, "BOX-01", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(2, "SRV-01", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(3, "NAS-01", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(4, "IMP-01", True, "100 Mb/s", "full", 1, 0),
    SwitchPort(5, "AP-01", True, "1 Gb/s", "full", 1, 0, poe_w=9.8),
    SwitchPort(6, "PC-01", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(7, "PC-02", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(8, "PC-03", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(9, "PC-04", True, "1 Gb/s", "full", 1, 0),
    SwitchPort(10, "—", False, "—", "—", 1, 0),
)

# PoE (IEEE 802.3) : puissance garantie au port du switch / disponible à l'équipement alimenté.
POE_CLASSES: tuple[tuple[str, str, float, float], ...] = (
    ("PoE", "802.3af", 15.4, 12.95),
    ("PoE+", "802.3at", 30.0, 25.5),
)
ETHERNET_MAX_M = 100  # canal cuivre 100 m (90 m de lien permanent + cordons), voir PR15


def fr(value: float) -> str:
    text = f"{value:g}"
    return text.replace(".", ",")


# =============================================================================================
# 2. Relevés de commandes fictifs (Windows en français, Linux en anglais)
# =============================================================================================


def win_ping_lines(target: str, replies: tuple[int | None, ...], *, ttl: int = 64,
                   name: str | None = None) -> tuple[str, ...]:
    """`ping` Windows : une ligne par écho (`None` = délai dépassé), puis statistiques
    **calculées** (envoyés, reçus, perdus, pourcentage)."""
    shown = f"{name} [{target}]" if name else target
    lines = [f"C:\\> ping {name or target}", f"Envoi d'une requête 'Ping' {shown}", "avec 32 octets de données :"]
    for ms in replies:
        if ms is None:
            lines.append("Délai d'attente de la demande dépassé.")
        else:
            delay = "temps<1ms" if ms < 1 else f"temps={ms} ms"
            lines.append(f"Réponse de {target} : octets=32 {delay} TTL={ttl}")
    sent = len(replies)
    received = sum(1 for r in replies if r is not None)
    lost = sent - received
    lines += [
        f"Statistiques Ping pour {target}:",
        f"  Paquets : envoyés = {sent}, reçus = {received},",
        f"  perdus = {lost} (perte {round(100 * lost / sent)}%),",
    ]
    return tuple(lines)


def win_ping_unknown_name(name: str) -> tuple[str, ...]:
    return (
        f"C:\\> ping {name}",
        "La requête Ping n'a pas pu trouver l'hôte",
        f"{name}. Vérifiez le nom et essayez à nouveau.",
    )


def ping_stats(lines: tuple[str, ...]) -> tuple[int, int, int]:
    """Relit (envoyés, reçus, perdus) dans une sortie de `win_ping_lines` (contrôle des tests)."""
    sent = sum(1 for line in lines if line.startswith(("Réponse de", "Délai d'attente")))
    received = sum(1 for line in lines if line.startswith("Réponse de"))
    return sent, received, sent - received


def tracert_lines(target: str, hops: tuple[str | None, ...]) -> tuple[str, ...]:
    """`tracert -d` Windows : un saut par élément (`None` = trois délais dépassés)."""
    lines = [f"C:\\> tracert -d {target}", f"Détermination de l'itinéraire vers {target}",
             "avec un maximum de 30 sauts :", ""]
    for index, hop in enumerate(hops, start=1):
        if hop is None:
            lines.append(f"{index:>3}     *        *        *     Délai dépassé.")
        else:
            lines.append(f"{index:>3}    <1 ms    <1 ms    <1 ms  {hop}" if index == 1
                         else f"{index:>3}    {8 + 2 * index} ms   {9 + 2 * index} ms   {8 + 2 * index} ms  {hop}")
    return tuple(lines)


NS_OK, NS_NXDOMAIN, NS_TIMEOUT = "ok", "nxdomain", "timeout"


def nslookup_lines(name: str, server: str, status: str, answer: str | None = None,
                   *, server_name: str = "UnKnown", authoritative: bool = False) -> tuple[str, ...]:
    """`nslookup nom [serveur]` Windows : serveur interrogé, puis réponse, nom inexistant ou
    délai dépassé."""
    lines = [f"C:\\> nslookup {name}", f"Serveur :   {server_name}", f"Address:  {server}", ""]
    if status == NS_OK:
        assert answer is not None
        if not authoritative:
            lines.append("Réponse ne faisant pas autorité :")
        lines += [f"Nom :    {name}", f"Address:  {answer}"]
    elif status == NS_NXDOMAIN:
        lines += [f"*** {server_name} ne parvient pas à trouver", f"{name} : Non-existent domain"]
    elif status == NS_TIMEOUT:
        lines += ["DNS request timed out.", "    timeout was 2 seconds.",
                  f"*** Le délai de la requête sur {server_name}", "a expiré"]
    else:
        raise ValueError(status)
    return tuple(lines)


def dig_lines(name: str, server: str, status: str, answer: str | None = None) -> tuple[str, ...]:
    """`dig nom` Linux (extrait) : statut NOERROR/NXDOMAIN, réponse et serveur interrogé."""
    lines = [f"$ dig {name} +noall +answer +comments"]
    if status == NS_TIMEOUT:
        return (*lines, ";; communications error to", f";; {server}#53: timed out",
                ";; no servers could be reached")
    code = "NOERROR" if status == NS_OK else "NXDOMAIN"
    lines.append(f";; ->>HEADER<<- opcode: QUERY, status: {code}")
    if status == NS_OK:
        assert answer is not None
        lines += [";; ANSWER SECTION:", f"{name}. 300 IN A {answer}"]
    lines.append(f";; SERVER: {server}#53({server}) (UDP)")
    return tuple(lines)


@dataclass(frozen=True)
class DhcpEvent:
    time: str  # « 08:14:02 »
    message: str  # « DHCPDISCOVER(eth0) 3c:52:… »


def dnsmasq_lines(events: tuple[DhcpEvent, ...], *, host: str = "srv-01", pid: int = 812) -> tuple[str, ...]:
    """Extrait de `journalctl -u dnsmasq` sur SRV-01 : deux lignes par événement (horodatage
    et processus, puis message), pour rester lisible sur mobile."""
    lines = ["$ journalctl -u dnsmasq --since 08:00"]
    for event in events:
        lines.append(f"oct. 26 {event.time} {host} dnsmasq-dhcp[{pid}]:")
        message = f"  {event.message}"
        while len(message) > SCREEN_WIDTH:  # suite du message sur la ligne suivante
            cut = message.rindex(" ", 0, SCREEN_WIDTH)
            lines.append(message[:cut])
            message = "    " + message[cut + 1:]
        lines.append(message)
    return tuple(lines)


def dora_events(mac: str, ip: str, hostname: str, start: str = "08:14:02") -> tuple[DhcpEvent, ...]:
    """Bail obtenu normalement : DISCOVER, OFFER, REQUEST, ACK (DORA)."""
    m = mac_linux(mac)
    return (
        DhcpEvent(start, f"DHCPDISCOVER(eth0) {m}"),
        DhcpEvent(start, f"DHCPOFFER(eth0) {ip} {m}"),
        DhcpEvent(start, f"DHCPREQUEST(eth0) {ip} {m}"),
        DhcpEvent(start, f"DHCPACK(eth0) {ip} {m} {hostname}"),
    )


def no_address_events(mac: str, times: tuple[str, ...]) -> tuple[DhcpEvent, ...]:
    """Étendue épuisée : chaque DISCOVER reste sans offre (« no address available »)."""
    m = mac_linux(mac)
    return tuple(DhcpEvent(t, f"DHCPDISCOVER(eth0) {m} no address available") for t in times)


def ignored_events(mac: str, times: tuple[str, ...]) -> tuple[DhcpEvent, ...]:
    """Serveur réglé pour ne servir que les cartes enregistrées : DISCOVER « ignored »."""
    m = mac_linux(mac)
    return tuple(DhcpEvent(t, f"DHCPDISCOVER(eth0) {m} ignored") for t in times)


@dataclass(frozen=True)
class WifiStatus:
    state: str  # « connecté » | « déconnecté »
    ssid: str
    bssid: str
    radio: str  # « 802.11ac »
    auth: str  # « WPA2 - Personnel »
    cipher: str  # « CCMP »
    band: str  # « 2,4 GHz » | « 5 GHz »
    channel: int
    rx_mbps: float
    signal_pct: int


def netsh_wlan_lines(status: WifiStatus) -> tuple[str, ...]:
    """`netsh wlan show interfaces` (extrait, Windows en français)."""
    lines = ["C:\\> netsh wlan show interfaces", "    Nom              : Wi-Fi", f"    État             : {status.state}"]
    if status.state == "connecté":
        lines += [
            f"    SSID             : {status.ssid}",
            f"    BSSID            : {status.bssid}",
            f"    Type de radio    : {status.radio}",
            f"    Authentification : {status.auth}",
            f"    Chiffrement      : {status.cipher}",
            f"    Bande            : {status.band}",
            f"    Canal            : {status.channel}",
            f"    Réception (Mb/s) : {fr(status.rx_mbps)}",
            f"    Signal           : {status.signal_pct}%",
        ]
    return tuple(lines)


def arp_lines(interface_ip: str, entries: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    """`arp -a` Windows : table IP → MAC apprise sur le réseau local."""
    lines = ["C:\\> arp -a", f"Interface : {interface_ip} --- 0x7", "  Adresse Internet  Adresse physique     Type"]
    for ip, mac in entries:
        lines.append(f"  {ip:<17} {normalize_mac(mac).lower():<20} dynamique")
    return tuple(lines)


def route_print_lines(host: Host) -> tuple[str, ...]:
    """`route print -4` (extrait) : route par défaut et route du réseau local."""
    facts = host.facts
    lines = ["C:\\> route print -4", "Itinéraires actifs :", "Destination     Masque          Passerelle   Interface"]
    if host.gateway:
        lines.append(f"{'0.0.0.0':<15} {'0.0.0.0':<15} {host.gateway:<12} {host.ip}")
    lines.append(f"{facts.network:<15} {facts.mask:<15} {'On-link':<12} {host.ip}")
    return tuple(lines)


def ip_link_lines(iface: str, mac: str, *, carrier: bool) -> tuple[str, ...]:
    """`ip link show` Linux : `NO-CARRIER` et `state DOWN` quand aucun lien n'est détecté."""
    flags = "BROADCAST,MULTICAST,UP,LOWER_UP" if carrier else "NO-CARRIER,BROADCAST,MULTICAST,UP"
    state = "UP" if carrier else "DOWN"
    return (f"$ ip link show {iface}", f"2: {iface}: <{flags}>", f"    mtu 1500 state {state}",
            f"    link/ether {mac_linux(mac)}")


def ip_neigh_lines(iface: str, entries: tuple[tuple[str, str | None], ...]) -> tuple[str, ...]:
    """`ip neigh` Linux : voisin joignable (MAC connue) ou en échec (`FAILED`)."""
    lines = ["$ ip neigh"]
    for ip, mac in entries:
        if mac:  # ligne réelle coupée en deux pour l'écran mobile
            lines += [f"{ip} dev {iface} lladdr {mac_linux(mac)}", "    REACHABLE"]
        else:
            lines.append(f"{ip} dev {iface} FAILED")
    return tuple(lines)


def resolvectl_lines(iface: str, dns: tuple[str, ...], domain: str | None) -> tuple[str, ...]:
    """`resolvectl status <interface>` (systemd-resolved, extrait)."""
    lines = [f"$ resolvectl status {iface}", f"Link 2 ({iface})", f"  Current DNS Server: {dns[0]}",
             f"         DNS Servers: {' '.join(dns)}"]
    if domain:
        lines.append(f"          DNS Domain: {domain}")
    return tuple(lines)


def netstat_lines(entries: tuple[tuple[str, str, str], ...]) -> tuple[str, ...]:
    """`netstat -an -p tcp` (extrait) : adresse locale, distante, état."""
    lines = ["C:\\> netstat -an -p tcp", "  Proto Adresse locale       Adresse distante  État"]
    for local, remote, state in entries:
        lines.append(f"  TCP   {local:<20} {remote:<17} {state}")
    return tuple(lines)


def test_netconnection_lines(target: str, port: int, *, ping_ok: bool, tcp_ok: bool) -> tuple[str, ...]:
    """`Test-NetConnection` PowerShell (extrait) : ping et test d'un port TCP précis."""
    return (
        f"PS> Test-NetConnection {target} -Port {port}",
        f"ComputerName     : {target}",
        f"RemotePort       : {port}",
        f"PingSucceeded    : {ping_ok}",
        f"TcpTestSucceeded : {tcp_ok}",
    )


# =============================================================================================
# 3. Schémas
# =============================================================================================


def lan_svg() -> str:
    """Réseau en étoile : Internet → box → switch (colonne de gauche, un port par
    équipement) ; le point d'accès alimenté en PoE dessert le portable en Wi-Fi."""
    width = 380
    by_port = {p.device: p for p in SWITCH_PORTS}
    box = LAN_BY_NAME["BOX-01"]
    parts = [
        _box(96, 6, 280, 36, ["Internet (fournisseur d'accès)", f"IP publique de la box : {WAN_IP}"], fill="#ffffff"),
        f'<path d="M236 42 V58" stroke="{_STROKE}" stroke-width="2"/>',
        _box(96, 58, 280, 52, [f"{box.name} — {box.role}", f"LAN {box.ip}/{box.prefix} · NAT vers {WAN_IP}",
                               f"DNS du FAI : {ISP_DNS}"]),
    ]
    wired = [h for h in LAN_HOSTS if h.name in by_port and h.name != "BOX-01"]
    top, row_h, gap = 124, 50, 6
    sw_bottom = top + len(wired) * (row_h + gap) - gap
    parts.append(f'<rect x="4" y="70" width="54" height="{sw_bottom - 70}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" stroke-width="1.5"/>')
    parts.append(_text_lines(31, 112, ["SW-01"], size=12, weight="700", anchor="middle"))
    parts.append(_text_lines(31, 128, ["switch"], size=10.5, anchor="middle"))
    parts.append(f'<path d="M58 84 H96" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append('<text x="61" y="78" font-size="10">port 1</text>')
    for index, host in enumerate(wired):
        y = top + index * (row_h + gap)
        mid = y + row_h // 2
        port = by_port[host.name]
        parts.append(f'<path d="M58 {mid} H96" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(f'<text x="61" y="{mid - 4}" font-size="10">port {port.number}</text>')
        mode = "DHCP" if host.dhcp else "fixe"
        extra = f" · PoE {fr(port.poe_w)} W" if port.poe_w else ""
        parts.append(_box(96, y, 280, row_h, [f"{host.name} — {host.role}",
                                              f"{host.ip}/{host.prefix} ({mode}){extra}"]))
    lt = LAN_BY_NAME["LT-01"]
    y = sw_bottom + 18
    parts.append(f'<path d="M236 {y - 18} V{y}" stroke="{_STROKE}" stroke-width="2" stroke-dasharray="4 4"/>')
    parts.append(f'<text x="242" y="{y - 5}" font-size="10">Wi-Fi « {SSID} »</text>')
    parts.append(_box(96, y, 280, 50, [f"{lt.name} — {lt.role}", f"{lt.ip}/{lt.prefix} via AP-01 (WPA2/WPA3)"]))
    return _svg(width, y + 56, parts)


def _lan_alt() -> str:
    by_port = {p.device: p.number for p in SWITCH_PORTS}
    pieces = [
        f"{h.name} ({h.role}) {h.ip}/{h.prefix}" + (f" sur le port {by_port[h.name]}" if h.name in by_port else " en Wi-Fi")
        for h in LAN_HOSTS
    ]
    return (
        f"Réseau local {LAN_NETWORK} en étoile autour du switch SW-01. La box relie Internet (IP "
        f"publique {WAN_IP}) au réseau local et fait passerelle {ROUTER_IP}, NAT et pare-feu. "
        + " ; ".join(pieces)
        + f". Étendue DHCP de SRV-01 : {POOL[0]} à {POOL[1]} ; DNS interne {SERVER_IP} (suffixe {DOMAIN}), "
        f"qui relaie les noms Internet vers le DNS du FAI {ISP_DNS}."
    )


LAN_FIGURE = Figure(
    key="pr24-lan-reference",
    title="Réseau de référence de l'atelier : box, switch, serveur DHCP/DNS, NAS, imprimante, Wi-Fi",
    alt=_lan_alt(),
    caption=(
        f"Réseau {LAN_NETWORK} : passerelle {ROUTER_IP}, DHCP et DNS sur {SERVER_IP}, étendue "
        f"{POOL[0]}–{POOL[1]}, équipements fixes hors étendue, point d'accès alimenté par le "
        "switch (PoE). Adresses vérifiées par calcul ; MAC et adresses publiques fictives."
    ),
    svg=lan_svg(),
)


def ports_svg(ports: tuple[SwitchPort, ...], *, title: str) -> str:
    """Tableau d'état des ports d'un switch : une ligne par port, état écrit en toutes
    lettres (la couleur n'est qu'un repère)."""
    width, row_h, top = 380, 34, 40
    parts = [
        f'<text x="{width // 2}" y="18" text-anchor="middle" font-weight="700" font-size="13">{escape(title)}</text>',
        f'<text x="{width // 2}" y="33" text-anchor="middle" font-size="10.5">port · équipement · état · vitesse/duplex · VLAN · erreurs · PoE</text>',
    ]
    for i, p in enumerate(ports):
        y = top + i * row_h
        ok = p.link and p.admin_up and p.crc_errors == 0 and p.duplex in ("full", "—")
        fill = "#f4f6fb" if ok else "#fdecea"
        parts.append(
            f'<rect data-port="{p.number}" data-state="{escape(p.state)}" x="4" y="{y}" width="{width - 8}" '
            f'height="{row_h - 4}" rx="4" fill="{fill}" stroke="{_STROKE}" stroke-width="1"/>'
        )
        led = "#2e8b3a" if p.link and p.admin_up else "#8a8f98"
        parts.append(f'<circle cx="18" cy="{y + 15}" r="5" fill="{led}" stroke="{_STROKE}"/>')
        parts.append(f'<text x="30" y="{y + 13}" font-size="11.5" font-weight="700">{p.number} · {escape(p.device)}</text>')
        speed = f"{p.speed} {p.duplex}" if p.link else "—"
        detail = f"{p.state} · {speed} · VLAN {p.vlan} · erreurs {p.crc_errors}"
        if p.poe_w:
            detail += f" · PoE {fr(p.poe_w)} W"
        parts.append(f'<text x="30" y="{y + 26}" font-size="10.5">{escape(detail)}</text>')
    return _svg(width, top + len(ports) * row_h + 4, parts)


PORTS_FIGURE = Figure(
    key="pr24-ports-switch",
    title="Relevé fictif de l'état des ports du switch SW-01",
    alt=(
        "Tableau des dix ports du switch SW-01 : "
        + " ; ".join(f"port {p.number} {p.device}, {p.state}, {p.speed} {p.duplex}, VLAN {p.vlan}, "
                     f"{p.crc_errors} erreur" + (f", PoE {fr(p.poe_w)} W" if p.poe_w else "")
                     for p in SWITCH_PORTS)
        + "."
    ),
    caption=(
        "Ce qu'on lit dans l'interface d'un switch administrable : lien, vitesse et duplex "
        "négociés, VLAN du port, compteur d'erreurs (CRC, collisions), puissance PoE. Relevé fictif."
    ),
    svg=ports_svg(SWITCH_PORTS, title="SW-01 — état des ports (relevé fictif)"),
)

LAYER_STEPS: tuple[tuple[str, str], ...] = (
    ("Physique et liaison", "Voyant, câble, port du switch, carte activée, Wi-Fi associé, PoE."),
    ("Adresse IP et masque", "Adresse du réseau (pas 169.254), bon masque, pas de doublon, bail DHCP."),
    ("Passerelle", "ping de la passerelle ou arp -a : le réseau local et la sortie répondent."),
    ("IP distante", "ping d'une adresse Internet, tracert pour situer l'arrêt."),
    ("DNS", "nslookup du nom : bon serveur, réponse correcte."),
    ("Service ou application", "Partage, imprimante, site, compte, droits, pare-feu du service."),
)

LAYERS_FIGURE = Figure(
    key="pr24-couches",
    title="Procédure ordonnée : de la couche physique au service",
    alt="Six étapes reliées par des flèches : " + " ; ".join(
        f"{i} {name} : {detail}" for i, (name, detail) in enumerate(LAYER_STEPS, start=1)
    ),
    caption=(
        "On teste dans cet ordre : la première étape qui échoue indique la couche à examiner. "
        "On ne cherche pas une panne DNS tant que le lien ou la passerelle ne répondent pas."
    ),
    svg=step_flow_svg(LAYER_STEPS, width=380),
)

TREE_MASTER = (
    (
        ("Le symptôme touche-t-il un seul poste ?", "Plusieurs ou tous : chercher l'élément commun (switch, box, serveur DHCP/DNS, lien du FAI) et commencer par lui."),
        ("Le lien est-il présent (voyant, Wi-Fi associé, carte activée) ?", "Physique ou liaison : câble, prise, port, PoE, radio. Ne rien modifier dans l'IP."),
        ("L'adresse est-elle valide dans le réseau (pas 169.254) ?", "DHCP : bail, étendue pleine, serveur arrêté, VLAN du port ; ipconfig /renew."),
        ("La passerelle répond-elle (ping, arp -a) ?", "Masque, passerelle saisie, doublon d'adresse, VLAN, état de la box."),
        ("Une adresse Internet répond-elle (ping, tracert) ?", "Au-delà de la passerelle : liaison WAN de la box, FAI, filtrage ; tracert situe l'arrêt."),
        ("Le nom est-il résolu (nslookup) ?", "DNS : serveur configuré, joignable, interne ou externe, cache."),
    ),
    "Le réseau fonctionne : chercher au niveau du service (partage, imprimante, site, proxy, compte, droits).",
)
TREE_WIFI = (
    (
        ("Le SSID attendu est-il visible ?", "Radio : point d'accès éteint (PoE), Wi-Fi désactivé, hors de portée, 5 GHz trop loin."),
        ("Le poste s'associe-t-il et s'authentifie-t-il ?", "Authentification : clé incorrecte, WPA3 seul non pris en charge, profil enregistré obsolète."),
        ("Le poste reçoit-il une adresse du bon réseau ?", "IP après association : étendue DHCP, VLAN du SSID, serveur DHCP."),
        ("Le signal et le débit sont-ils stables ?", "Couverture et interférences : placement, canal, bande 2,4/5 GHz, répéteur."),
    ),
    "Wi-Fi correct : reprendre l'arbre général à l'étape « passerelle ».",
)
TREE_SHARE = (
    (
        ("Le serveur répond-il par son adresse IP (ping) ?", "Réseau : reprendre l'arbre général (lien, adresse, passerelle)."),
        ("Le nom du serveur est-il résolu ?", "Essayer \\\\adresse-IP\\partage pour confirmer, puis corriger le DNS."),
        ("Le port 445 répond-il (Test-NetConnection -Port 445) ?", "Service de partage (SMB) arrêté ou port filtré par un pare-feu."),
        ("Le chemin UNC est-il exact (\\\\serveur\\partage) ?", "Corriger le nom du serveur ou du partage."),
        ("Le compte est-il accepté (pas « accès refusé ») ?", "Compte, domaine ou groupe de travail, identifiants mémorisés."),
        ("Les droits suffisent-ils (partage et NTFS) ?", "Le plus restrictif des deux s'applique : ajuster avec l'accord du responsable."),
    ),
    "Ressource accessible : tester lecture et écriture avec l'utilisateur, puis documenter.",
)


def _tree_alt(tree: tuple[tuple[tuple[str, str], ...], str]) -> str:
    return ("Arbre de décision : " + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(tree[0], 1))
            + " Si tout est oui : " + tree[1])


TREE_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr24-arbre-general",
        title="Arbre de diagnostic réseau : du périmètre au service",
        alt=_tree_alt(TREE_MASTER),
        caption="Chaque « non » ouvre une branche de diagnostic ; chaque « oui » fait monter d'une couche.",
        svg=decision_tree_svg(*TREE_MASTER),
    ),
    Figure(
        key="pr24-arbre-wifi",
        title="Arbre de diagnostic Wi-Fi : radio, authentification, adresse",
        alt=_tree_alt(TREE_WIFI),
        caption="Trois problèmes différents à ne pas confondre : la radio, l'authentification et l'adresse IP.",
        svg=decision_tree_svg(*TREE_WIFI),
    ),
    Figure(
        key="pr24-arbre-partage",
        title="Arbre de diagnostic : le réseau répond mais le partage est inaccessible",
        alt=_tree_alt(TREE_SHARE),
        caption="Quand le ping répond, on cherche plus haut : nom, port du service, chemin, compte, droits.",
        svg=decision_tree_svg(*TREE_SHARE),
    ),
)

# --- Captures fictives (documents de diagnostic) ---------------------------------------------

APIPA_HOST = Host("LT-02", "portable neuf, DHCP", "169.254.37.112", 16, None, (), "A4-C3-F0-55-20-62", dhcp=True)
APIPA_LINES = ("C:\\> ipconfig /all", "", *ipconfig_all_lines(APIPA_HOST, dhcp_server=None, apipa=True))
PING_LAN_OK_WAN_KO = (
    *win_ping_lines(ROUTER_IP, (0, 0, 0, 0), ttl=64),
    "",
    *win_ping_lines(WEB_IP, (None, None, None, None)),
)
TRACERT_STOPS = tracert_lines(WEB_IP, (ROUTER_IP, None, None, None))
NSLOOKUP_INTERNAL_KO = nslookup_lines(SRV_FQDN, ISP_DNS, NS_NXDOMAIN)
NSLOOKUP_INTERNAL_OK = nslookup_lines(SRV_FQDN, SERVER_IP, NS_OK, SERVER_IP, server_name=SRV_FQDN)
PC01 = LAN_BY_NAME["PC-01"]
DHCP_LOG_LINES = dnsmasq_lines((
    DhcpEvent("08:14:02", f"DHCPREQUEST(eth0) {PC01.ip} {mac_linux(PC01.mac)}"),
    DhcpEvent("08:14:02", f"DHCPACK(eth0) {PC01.ip} {mac_linux(PC01.mac)} pc-01"),
    *ignored_events(APIPA_HOST.mac, ("09:02:11", "09:02:15", "09:02:23")),
))
WIFI_WEAK = WifiStatus("connecté", SSID, "9c:53:22:10:20:31", "802.11n", "WPA2 - Personnel", "CCMP",
                       "2,4 GHz", 6, 6.5, 18)
WIFI_WEAK_LINES = netsh_wlan_lines(WIFI_WEAK)
PC04 = LAN_BY_NAME["PC-04"]
LINUX_NO_CARRIER = (*ip_link_lines("enp3s0", PC04.mac, carrier=False), "", "$ ip route", "(aucune route)")

DOCUMENT_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr24-doc-apipa",
        title="Document A — ipconfig /all d'un portable en APIPA",
        alt=(f"Capture fictive : DHCP activé, adresse IPv4 d'autoconfiguration {APIPA_HOST.ip}, masque "
             f"{APIPA_HOST.mask}, aucune passerelle, aucun serveur DHCP ni DNS."),
        caption="APIPA : DHCP activé mais aucun bail reçu. C'est un indice, pas une preuve de la cause. Capture fictive.",
        svg=screen_svg(APIPA_LINES, label=FICTIVE_LABEL),
    ),
    Figure(
        key="pr24-doc-ping",
        title="Document B — la passerelle répond, l'adresse Internet non",
        alt=(f"Capture fictive : ping {ROUTER_IP} reçoit 4 réponses sur 4 ; ping {WEB_IP} : 4 délais "
             "dépassés, 100 % de perte."),
        caption="Le réseau local et la passerelle fonctionnent ; l'arrêt est au-delà. Capture fictive.",
        svg=screen_svg(PING_LAN_OK_WAN_KO, label=FICTIVE_LABEL),
    ),
    Figure(
        key="pr24-doc-tracert",
        title="Document C — tracert s'arrête après la box",
        alt=(f"Capture fictive : tracert -d {WEB_IP} ; le saut 1 ({ROUTER_IP}) répond en moins d'une "
             "milliseconde, les sauts 2 à 4 n'affichent que des délais dépassés."),
        caption="Le premier saut est la passerelle ; rien ne répond ensuite : liaison WAN ou FAI à vérifier. Capture fictive.",
        svg=screen_svg(TRACERT_STOPS, label=FICTIVE_LABEL),
    ),
    Figure(
        key="pr24-doc-nslookup",
        title="Document D — nom interne : DNS du FAI contre DNS interne",
        alt=(f"Capture fictive : nslookup {SRV_FQDN} interroge {ISP_DNS} et obtient « Non-existent "
             f"domain » ; interrogé, le DNS interne {SERVER_IP} répond {SERVER_IP}."),
        caption="Un DNS public ne connaît pas les noms internes : le poste doit utiliser le DNS interne. Capture fictive.",
        svg=screen_svg((*NSLOOKUP_INTERNAL_KO, "", *NSLOOKUP_INTERNAL_OK), label=FICTIVE_LABEL),
    ),
    Figure(
        key="pr24-doc-dhcp",
        title="Document E — journal DHCP : un renouvellement accepté, une carte ignorée",
        alt=(f"Extrait fictif du journal dnsmasq de SRV-01 : à 08:14, PC-01 renouvelle son bail "
             f"({PC01.ip}, DHCPREQUEST puis DHCPACK) ; à 09:02, trois demandes DHCPDISCOVER de la "
             f"carte {mac_linux(APIPA_HOST.mac)} sont marquées « ignored »."),
        caption=(f"Le serveur fonctionne (il renouvelle le bail de PC-01, baux de {LEASE_DAYS} jours) mais "
                 "ignore une carte qu'il ne connaît pas. Extrait fictif."),
        svg=screen_svg(DHCP_LOG_LINES, label="extrait fictif de journal — présentation simplifiée"),
    ),
    Figure(
        key="pr24-doc-wifi",
        title="Document F — état Wi-Fi d'un portable : associé mais signal faible",
        alt=(f"Capture fictive de netsh wlan show interfaces : connecté au SSID {SSID}, WPA2 - Personnel, "
             f"CCMP, bande {WIFI_WEAK.band}, canal {WIFI_WEAK.channel}, réception {fr(WIFI_WEAK.rx_mbps)} Mb/s, "
             f"signal {WIFI_WEAK.signal_pct} %."),
        caption="Associé et authentifié, mais signal et débit très faibles : problème radio, pas d'adressage. Capture fictive.",
        svg=screen_svg(WIFI_WEAK_LINES, label=FICTIVE_LABEL),
    ),
    Figure(
        key="pr24-doc-linux",
        title="Document G — Linux : interface sans lien (NO-CARRIER)",
        alt=("Capture fictive sur PC-04 : ip link show enp3s0 affiche NO-CARRIER et state DOWN ; ip route "
             "n'affiche aucune route."),
        caption="Sans lien physique, pas de route : chercher le câble ou le port avant toute configuration IP. Capture fictive.",
        svg=screen_svg(LINUX_NO_CARRIER, label=FICTIVE_LABEL),
    ),
)

PR24_FIGURES: tuple[Figure, ...] = (LAN_FIGURE, PORTS_FIGURE, LAYERS_FIGURE, *TREE_FIGURES, *DOCUMENT_FIGURES)


def all_capture_lines() -> tuple[str, ...]:
    """Toutes les lignes des captures des figures (contrôle de largeur dans les tests)."""
    return (*APIPA_LINES, *PING_LAN_OK_WAN_KO, *TRACERT_STOPS, *NSLOOKUP_INTERNAL_KO, *NSLOOKUP_INTERNAL_OK,
            *DHCP_LOG_LINES, *WIFI_WEAK_LINES, *LINUX_NO_CARRIER)


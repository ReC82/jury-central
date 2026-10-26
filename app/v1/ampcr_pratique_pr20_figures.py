"""Modèle d'adressage et schémas du cours PR20 « IPv4, MAC, masques et passerelles —
configuration et diagnostics écrits » (ticket #199).

Règle du ticket : **aucun calcul d'adressage fait à la main seulement**. Toutes les valeurs
(réseau, diffusion, plage d'hôtes, nombre d'adresses, masque ↔ préfixe, même sous-réseau ou
non, type d'adresse, cohérence d'une configuration ou d'un plan) sont calculées ici avec le
module standard `ipaddress` et contrôlées par `tests/test_ticket199_ampcr_pratique_pr20.py`
(qui recalcule indépendamment). Les mêmes fonctions produisent les schémas, les sorties de
commandes fictives (`ipconfig /all`, `ip addr`, `ip route`), les corrigés et les réponses
attendues des exercices auto-corrigés : schéma, corrigé et barème ne peuvent pas se contredire.

Chaque schéma porte son information en texte (valeurs en toutes lettres, ✓ / ✗) : la couleur
n'est qu'un repère, le schéma reste lisible imprimé en noir et blanc. Aucune image générée.
"""

import ipaddress
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    _MONO,
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    screen_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
_NET = "#1f5fbf"
_HOST = "#b35c00"

# =============================================================================================
# 1. Calculs IPv4 (module standard `ipaddress`)
# =============================================================================================

# Plages particulières enseignées (RFC 1918, RFC 3927, RFC 1122).
PRIVATE_RANGES: tuple[str, ...] = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
LINK_LOCAL_RANGE = "169.254.0.0/16"
LOOPBACK_RANGE = "127.0.0.0/8"

KIND_PRIVATE = "Privée (RFC 1918)"
KIND_PUBLIC = "Publique (routable sur Internet)"
KIND_LOOPBACK = "Bouclage (loopback)"
KIND_LINK_LOCAL = "Lien local (APIPA)"
KIND_UNSPECIFIED = "Non spécifiée (0.0.0.0)"
ADDRESS_KINDS: tuple[str, ...] = (KIND_PRIVATE, KIND_PUBLIC, KIND_LOOPBACK, KIND_LINK_LOCAL, KIND_UNSPECIFIED)


def fr(value: float, digits: int = 1) -> str:
    """Nombre au format français (virgule décimale), sans zéro inutile."""
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def address_kind(address: str) -> str:
    """Type d'une adresse IPv4 parmi les cinq catégories du cours."""
    ip = ipaddress.IPv4Address(address)
    if ip.is_unspecified:
        return KIND_UNSPECIFIED
    if ip.is_loopback:
        return KIND_LOOPBACK
    if ip.is_link_local:
        return KIND_LINK_LOCAL
    if any(ip in ipaddress.IPv4Network(r) for r in PRIVATE_RANGES):
        return KIND_PRIVATE
    if ip.is_global:
        return KIND_PUBLIC
    raise ValueError(f"Adresse hors des catégories du cours : {address}")


def prefix_to_mask(prefix: int) -> str:
    return str(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)


def is_contiguous_mask(mask: str) -> bool:
    """Un masque valide : des 1 à gauche, puis uniquement des 0."""
    value = int(ipaddress.IPv4Address(mask))
    inverted = (~value) & 0xFFFFFFFF
    return (inverted & (inverted + 1)) == 0


def mask_to_prefix(mask: str) -> int:
    if not is_contiguous_mask(mask):
        raise ValueError(f"Masque non contigu : {mask}")
    return int(ipaddress.IPv4Address(mask)).bit_count()


@dataclass(frozen=True)
class SubnetFacts:
    address: str
    prefix: int
    mask: str
    network: str
    broadcast: str
    first_host: str | None  # None pour /31 et /32 (cas particuliers, voir cours)
    last_host: str | None
    total: int  # nombre total d'adresses du bloc
    usable: int  # hôtes « usuels » : total − 2 (réseau et diffusion), sauf /31 et /32

    @property
    def cidr(self) -> str:
        return f"{self.network}/{self.prefix}"

    @property
    def host_range(self) -> str:
        return f"{self.first_host} à {self.last_host}" if self.first_host else "—"


def subnet_facts(address: str, prefix: int) -> SubnetFacts:
    iface = ipaddress.IPv4Interface(f"{address}/{prefix}")
    net = iface.network
    total = net.num_addresses
    if prefix <= 30:
        first, last, usable = str(net.network_address + 1), str(net.broadcast_address - 1), total - 2
    else:  # /31 (lien point à point, RFC 3021) et /32 (une seule adresse) : compléments
        first = last = None
        usable = 2 if prefix == 31 else 1
    return SubnetFacts(
        address=address, prefix=prefix, mask=str(net.netmask), network=str(net.network_address),
        broadcast=str(net.broadcast_address), first_host=first, last_host=last, total=total, usable=usable,
    )


def same_subnet(a: str, a_prefix: int, b: str, b_prefix: int) -> bool:
    """Vrai si les deux postes sont dans le même réseau **et** chacun voit l'autre comme
    local (masques cohérents) : communication directe, sans routeur."""
    return is_local_for(a, a_prefix, b) and is_local_for(b, b_prefix, a) and a_prefix == b_prefix


def is_local_for(address: str, prefix: int, other: str) -> bool:
    """Le poste `address/prefix` considère-t-il `other` comme local (envoi direct, ARP) ?
    Sinon il envoie le paquet à sa passerelle par défaut."""
    return ipaddress.IPv4Address(other) in ipaddress.IPv4Interface(f"{address}/{prefix}").network


def smallest_prefix_for(hosts: int) -> int:
    """Plus long préfixe (plus petit bloc) offrant au moins `hosts` adresses d'hôtes usuelles."""
    for prefix in range(30, 0, -1):
        if 2 ** (32 - prefix) - 2 >= hosts:
            return prefix
    raise ValueError("Trop d'hôtes")


def octets_binary(address: str) -> tuple[str, str, str, str]:
    return tuple(f"{int(o):08b}" for o in address.split("."))  # type: ignore[return-value]


def binary_and_last_octet(address: str, mask: str) -> tuple[str, str, str, int]:
    """(octet de l'adresse, octet du masque, résultat du ET) en binaire, et le résultat en
    décimal, pour le dernier octet."""
    a, m = int(address.split(".")[-1]), int(mask.split(".")[-1])
    return f"{a:08b}", f"{m:08b}", f"{a & m:08b}", a & m


# --- Adresses MAC -------------------------------------------------------------------------


def normalize_mac(mac: str) -> str:
    digits = mac.replace("-", "").replace(":", "").replace(".", "").upper()
    if len(digits) != 12 or any(c not in "0123456789ABCDEF" for c in digits):
        raise ValueError(f"Adresse MAC invalide : {mac}")
    return "-".join(digits[i:i + 2] for i in range(0, 12, 2))


def mac_linux(mac: str) -> str:
    return normalize_mac(mac).lower().replace("-", ":")


def mac_first_octet_bits(mac: str) -> str:
    return f"{int(normalize_mac(mac)[:2], 16):08b}"


def mac_is_group(mac: str) -> bool:
    """Bit I/G (bit de poids faible du premier octet) : 1 = adresse de groupe (multicast)."""
    return bool(int(normalize_mac(mac)[:2], 16) & 0b01)


def mac_is_locally_administered(mac: str) -> bool:
    """Bit U/L (deuxième bit de poids faible du premier octet) : 1 = adresse administrée
    localement (MAC aléatoire du Wi-Fi, carte virtuelle), 0 = attribuée par le fabricant."""
    return bool(int(normalize_mac(mac)[:2], 16) & 0b10)


# --- Configurations de postes et plans d'adressage ------------------------------------------


@dataclass(frozen=True)
class Host:
    name: str
    role: str
    ip: str
    prefix: int
    gateway: str | None
    dns: tuple[str, ...]
    mac: str
    dhcp: bool = False

    @property
    def mask(self) -> str:
        return prefix_to_mask(self.prefix)

    @property
    def facts(self) -> SubnetFacts:
        return subnet_facts(self.ip, self.prefix)


def host_errors(host: Host) -> list[str]:
    """Erreurs de configuration d'un poste seul (sans comparer aux autres)."""
    errors: list[str] = []
    facts = host.facts
    kind = address_kind(host.ip)
    if kind == KIND_LINK_LOCAL:
        errors.append(f"{host.name} : adresse APIPA {host.ip} — aucun bail DHCP obtenu.")
    elif kind in (KIND_LOOPBACK, KIND_UNSPECIFIED):
        errors.append(f"{host.name} : {host.ip} ne peut pas être l'adresse d'une interface du réseau.")
    if host.prefix <= 30 and host.ip == facts.network:
        errors.append(f"{host.name} : {host.ip} est l'adresse du réseau {facts.cidr}, pas une adresse d'hôte.")
    if host.prefix <= 30 and host.ip == facts.broadcast:
        errors.append(f"{host.name} : {host.ip} est l'adresse de diffusion de {facts.cidr}.")
    if host.gateway is not None:
        if host.gateway == host.ip:
            errors.append(f"{host.name} : la passerelle ne peut pas être l'adresse du poste lui-même.")
        elif not is_local_for(host.ip, host.prefix, host.gateway):
            errors.append(
                f"{host.name} : passerelle {host.gateway} hors du réseau {facts.cidr} du poste — injoignable."
            )
    return errors


@dataclass(frozen=True)
class AddressPlan:
    network: str  # ex. « 192.168.10.0/24 »
    hosts: tuple[Host, ...]
    router_ip: str
    dns_ip: str
    dhcp_pool: tuple[str, str] | None = None  # (première, dernière adresse de l'étendue)

    def in_pool(self, address: str) -> bool:
        if self.dhcp_pool is None:
            return False
        low, high = (ipaddress.IPv4Address(a) for a in self.dhcp_pool)
        return low <= ipaddress.IPv4Address(address) <= high


def plan_errors(plan: AddressPlan) -> list[str]:
    """Erreurs d'un plan d'adressage : erreurs de chaque poste, puis cohérence de l'ensemble
    (réseau, masque, passerelle, DNS, doublons IP et MAC, adresse fixe dans l'étendue DHCP)."""
    errors: list[str] = []
    net = ipaddress.IPv4Network(plan.network)
    seen_ip: dict[str, str] = {}
    seen_mac: dict[str, str] = {}
    for host in plan.hosts:
        errors += host_errors(host)
        if ipaddress.IPv4Address(host.ip) not in net:
            errors.append(f"{host.name} : {host.ip} n'appartient pas au réseau {plan.network}.")
        if host.prefix != net.prefixlen:
            errors.append(
                f"{host.name} : masque {host.mask} (/{host.prefix}) au lieu de {net.netmask} (/{net.prefixlen})."
            )
        if host.ip != plan.router_ip and host.gateway is not None and host.gateway != plan.router_ip:
            errors.append(f"{host.name} : passerelle {host.gateway} au lieu de {plan.router_ip} (routeur).")
        if host.ip not in (plan.router_ip, plan.dns_ip) and host.dns and host.dns[0] != plan.dns_ip:
            errors.append(f"{host.name} : DNS {host.dns[0]} au lieu de {plan.dns_ip}.")
        if host.ip in seen_ip:
            errors.append(f"{host.name} : adresse {host.ip} déjà attribuée à {seen_ip[host.ip]} (doublon).")
        else:
            seen_ip[host.ip] = host.name
        mac = normalize_mac(host.mac)
        if mac in seen_mac:
            errors.append(f"{host.name} : adresse MAC {mac} identique à celle de {seen_mac[mac]}.")
        else:
            seen_mac[mac] = host.name
        if not host.dhcp and plan.in_pool(host.ip):
            errors.append(
                f"{host.name} : adresse fixe {host.ip} dans l'étendue DHCP "
                f"{plan.dhcp_pool[0]}–{plan.dhcp_pool[1]} : risque de doublon."  # type: ignore[index]
            )
    return errors


# =============================================================================================
# 2. Le petit réseau de référence du cours (schéma, captures, plan d'adressage)
# =============================================================================================

LAN_NETWORK = "192.168.10.0/24"
LAN_ROUTER = "192.168.10.1"
LAN_SERVER = "192.168.10.5"
LAN_POOL = ("192.168.10.100", "192.168.10.199")
# Côté Internet : adresse de la plage de documentation RFC 5737 (jamais attribuée).
WAN_ADDRESS = "203.0.113.45"

LAN_HOSTS: tuple[Host, ...] = (
    Host("Routeur", "passerelle vers Internet", LAN_ROUTER, 24, None, (), "00-1D-AA-4E-10-01"),
    Host("SRV-01", "serveur DHCP et DNS", LAN_SERVER, 24, LAN_ROUTER, ("127.0.0.1",), "00-15-5D-0A-0B-05"),
    Host("PC-01", "poste, DHCP", "192.168.10.101", 24, LAN_ROUTER, (LAN_SERVER,), "3C-52-82-1A-2B-01", dhcp=True),
    Host("PC-02", "poste, DHCP", "192.168.10.102", 24, LAN_ROUTER, (LAN_SERVER,), "3C-52-82-1A-2B-02", dhcp=True),
    Host("PC-03", "poste, DHCP", "192.168.10.103", 24, LAN_ROUTER, (LAN_SERVER,), "3C-52-82-1A-2B-03", dhcp=True),
    Host("PC-04", "poste Linux, DHCP", "192.168.10.104", 24, LAN_ROUTER, (LAN_SERVER,), "52-54-00-3A-7C-11", dhcp=True),
)
LAN_PLAN = AddressPlan(LAN_NETWORK, LAN_HOSTS, LAN_ROUTER, LAN_SERVER, LAN_POOL)
LAN_BY_NAME: dict[str, Host] = {h.name: h for h in LAN_HOSTS}


def _box(x: int, y: int, w: int, h: int, lines: list[str], *, fill: str = "#f4f6fb", bold_first: bool = True) -> str:
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{_STROKE}" stroke-width="1.5"/>']
    for i, line in enumerate(lines):
        weight = "700" if (i == 0 and bold_first) else "400"
        size = 12.5 if i == 0 else 11.5
        parts.append(
            f'<text x="{x + 8}" y="{y + 17 + 15 * i}" font-size="{size}" font-weight="{weight}">{escape(line)}</text>'
        )
    return "".join(parts)


def lan_svg(plan: AddressPlan, wan: str) -> str:
    """Réseau en étoile : Internet → routeur → switch (colonne de gauche) → un câble par
    équipement (colonne de droite). Chaque boîte affiche nom, rôle, IP/préfixe et MAC."""
    width = 380
    parts: list[str] = []
    router = next(h for h in plan.hosts if h.ip == plan.router_ip)
    parts.append(_box(96, 6, 280, 36, ["Internet (fournisseur d'accès)", f"adresse publique de la box : {wan}"], fill="#ffffff"))
    parts.append(f'<path d="M236 42 V58" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append(_box(96, 58, 280, 52, [
        f"{router.name} — {router.role}",
        f"LAN : {router.ip}/{router.prefix}",
        f"MAC {router.mac}",
    ]))
    others = [h for h in plan.hosts if h is not router]
    top, row_h, gap = 132, 70, 8
    sw_top, sw_bottom = 96, top + len(others) * (row_h + gap) - gap
    parts.append(
        f'<rect x="4" y="{sw_top}" width="54" height="{sw_bottom - sw_top}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" stroke-width="1.5"/>'
    )
    parts.append(_text_lines(31, sw_top + 20, ["Switch"], size=12, weight="700", anchor="middle"))
    parts.append(_text_lines(31, sw_top + 36, ["(étoile)"], size=10.5, anchor="middle"))
    parts.append(f'<path d="M58 84 H96" stroke="{_STROKE}" stroke-width="2"/>')
    parts.append('<text x="61" y="78" font-size="10">port 1</text>')
    for index, host in enumerate(others):
        y = top + index * (row_h + gap)
        mid = y + row_h // 2
        parts.append(f'<path d="M58 {mid} H96" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(f'<text x="61" y="{mid - 4}" font-size="10">port {index + 2}</text>')
        mode = "DHCP" if host.dhcp else "fixe"
        parts.append(_box(96, y, 280, row_h, [
            f"{host.name} — {host.role}",
            f"IP {host.ip}/{host.prefix} ({mode})",
            f"passerelle {host.gateway} · DNS {host.dns[0]}",
            f"MAC {host.mac}",
        ]))
    height = top + len(others) * (row_h + gap) + 4
    return _svg(width, height, parts)


def _lan_alt(plan: AddressPlan) -> str:
    pieces = [
        f"{h.name} ({h.role}) : {h.ip}/{h.prefix}, MAC {h.mac}"
        + (f", passerelle {h.gateway}, DNS {h.dns[0]}" if h.gateway else "")
        for h in plan.hosts
    ]
    return (
        f"Réseau local {plan.network} en étoile : la box/routeur relie Internet (adresse publique "
        f"{WAN_ADDRESS}) au réseau local ; un switch relie par un câble chacun des équipements. "
        + " ; ".join(pieces) + f". Étendue DHCP du serveur : {plan.dhcp_pool[0]} à {plan.dhcp_pool[1]}."  # type: ignore[index]
    )


LAN_FIGURE = Figure(
    key="pr20-lan-reference",
    title="Petit réseau local de référence : 4 postes, switch, routeur, serveur DHCP/DNS",
    alt=_lan_alt(LAN_PLAN),
    caption=(
        f"Réseau {LAN_NETWORK} : passerelle {LAN_ROUTER} (routeur), DHCP et DNS sur {LAN_SERVER}, "
        f"étendue DHCP {LAN_POOL[0]} à {LAN_POOL[1]}, adresses fixes hors de l'étendue. "
        "Adresses vérifiées par calcul ; MAC fictives."
    ),
    svg=lan_svg(LAN_PLAN, WAN_ADDRESS),
)


# =============================================================================================
# 3. Décomposition en bits : adresse, masque, ET logique, diffusion
# =============================================================================================


def bits_svg(address: str, prefix: int) -> str:
    """Quatre lignes de 32 bits (adresse, masque, réseau = adresse ET masque, diffusion =
    bits d'hôte à 1), séparées par une ligne pointillée à la frontière réseau/hôte."""
    facts = subnet_facts(address, prefix)
    rows = (
        ("Adresse", address),
        ("Masque", facts.mask),
        ("ET = réseau", facts.network),
        ("Diffusion", facts.broadcast),
    )
    width, left, bit_w, oct_gap, top, row_h = 380, 108, 7.3, 6, 40, 34
    parts: list[str] = []

    def bit_x(i: int) -> float:
        return left + i * bit_w + (i // 8) * oct_gap

    boundary = (bit_x(prefix - 1) + bit_x(prefix)) / 2 + (bit_w / 2) if 0 < prefix < 32 else None
    parts.append(
        f'<text x="{left}" y="16" font-size="11.5" font-weight="700" fill="{_NET}">réseau : {prefix} bits</text>'
    )
    parts.append(
        f'<text x="{width - 6}" y="16" font-size="11.5" font-weight="700" text-anchor="end" fill="{_HOST}">'
        f"hôte : {32 - prefix} bits</text>"
    )
    for r, (label, value) in enumerate(rows):
        y = top + r * row_h
        parts.append(f'<text x="4" y="{y}" font-size="11.5" font-weight="700">{escape(label)}</text>')
        parts.append(f'<text x="4" y="{y + 14}" font-size="10.5">{escape(value)}</text>')
        bits = "".join(octets_binary(value))
        for i, bit in enumerate(bits):
            colour = _NET if i < prefix else _HOST
            weight = "700" if i < prefix else "400"
            parts.append(
                f'<text x="{bit_x(i):.1f}" y="{y + 6}" font-size="12" font-family="{_MONO}" '
                f'font-weight="{weight}" fill="{colour}">{bit}</text>'
            )
    if boundary is not None:
        parts.append(
            f'<path d="M{boundary:.1f} 22 V{top + len(rows) * row_h - 18}" stroke="{_STROKE}" '
            f'stroke-width="1.5" stroke-dasharray="4 3"/>'
        )
    y = top + len(rows) * row_h + 4
    summary = (
        f"/{prefix} = {facts.mask} · {facts.total} adresses · {facts.usable} hôtes usuels",
        f"Hôtes : {facts.host_range}",
    )
    parts.append(_text_lines(4, y, list(summary), size=11.5, weight="700"))
    return _svg(width, y + 26, parts)


BITS_EXAMPLES: tuple[tuple[str, int], ...] = (
    ("192.168.10.77", 24),
    ("192.168.10.77", 26),
    ("192.168.10.77", 27),
)


def _bits_figure(address: str, prefix: int) -> Figure:
    f = subnet_facts(address, prefix)
    return Figure(
        key=f"pr20-bits-{prefix}",
        title=f"Décomposition en bits de {address}/{prefix}",
        alt=(
            f"Adresse {address} et masque {f.mask} (/{prefix}) écrits en 32 bits : les {prefix} "
            f"premiers bits forment la partie réseau, les {32 - prefix} derniers la partie hôte. "
            f"Le ET logique bit à bit donne le réseau {f.network} ; tous les bits d'hôte à 1 "
            f"donnent la diffusion {f.broadcast}. {f.total} adresses, {f.usable} hôtes usuels, "
            f"de {f.first_host} à {f.last_host}."
        ),
        caption=(
            f"{address}/{prefix} : réseau {f.network}, diffusion {f.broadcast}, hôtes "
            f"{f.host_range} ({f.usable}). Bits réseau en gras, à gauche de la ligne pointillée. "
            "Valeurs calculées."
        ),
        svg=bits_svg(address, prefix),
    )


BITS_FIGURES: tuple[Figure, ...] = tuple(_bits_figure(a, p) for a, p in BITS_EXAMPLES)

# Préfixes du ticket (cas ordinaires) et compléments /31, /32.
PREFIX_TABLE: tuple[int, ...] = (24, 25, 26, 27, 28, 30)
COMPLEMENT_PREFIXES: tuple[int, ...] = (31, 32)


# =============================================================================================
# 4. Adresse MAC
# =============================================================================================

MAC_EXAMPLE = "3C-52-82-1A-2B-01"
MAC_RANDOM_EXAMPLE = "DA-7F-3E-91-0C-55"


def mac_svg(mac: str, random_mac: str) -> str:
    width = 380
    octets = normalize_mac(mac).split("-")
    parts: list[str] = []
    cell_w, left, top = 54, 28, 26
    parts.append(f'<text x="{width // 2}" y="16" font-size="12.5" font-weight="700" text-anchor="middle">'
                 f"{escape(normalize_mac(mac))} : 6 octets = 48 bits</text>")
    for i, octet in enumerate(octets):
        x = left + i * cell_w
        parts.append(f'<rect x="{x}" y="{top}" width="{cell_w - 4}" height="30" rx="5" fill="#f4f6fb" stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + (cell_w - 4) // 2}" y="{top + 20}" font-size="14" font-weight="700" '
                     f'text-anchor="middle" font-family="{_MONO}">{octet}</text>')
    parts.append(f'<path d="M{left} {top + 40} H{left + 3 * cell_w - 4}" stroke="{_NET}" stroke-width="2"/>')
    parts.append(f'<path d="M{left + 3 * cell_w} {top + 40} H{left + 6 * cell_w - 4}" stroke="{_HOST}" stroke-width="2"/>')
    parts.append(_text_lines(left + int(1.5 * cell_w), top + 56, ["3 premiers octets : OUI", "(fabricant de la carte)"],
                             size=11, anchor="middle", step=14))
    parts.append(_text_lines(left + int(4.5 * cell_w), top + 56, ["3 derniers octets :", "numéro de la carte"],
                             size=11, anchor="middle", step=14))
    y = top + 100
    first_bits = mac_first_octet_bits(mac)
    parts.append(_text_lines(6, y, [
        f"Premier octet {octets[0]} = {first_bits} (binaire)",
        f"bit de droite (I/G) = {first_bits[-1]} : adresse individuelle",
        f"bit suivant (U/L) = {first_bits[-2]} : attribuée par le fabricant",
    ], size=11.5, step=16))
    y += 58
    rnd = normalize_mac(random_mac)
    rnd_bits = mac_first_octet_bits(random_mac)
    parts.append(_text_lines(6, y, [
        f"MAC aléatoire {rnd} : {rnd[:2]} = {rnd_bits}",
        f"bit U/L = {rnd_bits[-2]} : administrée localement (Wi-Fi",
        "« adresse aléatoire », machine virtuelle) : pas le fabricant.",
        f"Windows : {normalize_mac(mac)} ; Linux : {mac_linux(mac)}",
    ], size=11.5, step=16))
    return _svg(width, y + 66, parts)


MAC_FIGURE = Figure(
    key="pr20-mac",
    title="Structure d'une adresse MAC",
    alt=(
        f"L'adresse MAC {normalize_mac(MAC_EXAMPLE)} compte 6 octets (48 bits, 12 chiffres "
        "hexadécimaux). Les 3 premiers octets forment l'OUI attribué au fabricant, les 3 "
        f"derniers numérotent la carte. Premier octet {normalize_mac(MAC_EXAMPLE)[:2]} = "
        f"{mac_first_octet_bits(MAC_EXAMPLE)} : bit I/G à 0 (adresse individuelle), bit U/L à 0 "
        f"(attribuée par le fabricant). Une MAC aléatoire comme {normalize_mac(MAC_RANDOM_EXAMPLE)} "
        f"a le bit U/L à 1 (premier octet {mac_first_octet_bits(MAC_RANDOM_EXAMPLE)}) : administrée "
        "localement. Windows écrit avec des tirets, Linux avec des deux-points en minuscules."
    ),
    caption=(
        "Adresse MAC : OUI du fabricant + numéro de carte ; les bits I/G et U/L du premier octet "
        "sont calculés. MAC fictives."
    ),
    svg=mac_svg(MAC_EXAMPLE, MAC_RANDOM_EXAMPLE),
)


# =============================================================================================
# 5. DHCP : échange DORA
# =============================================================================================

DORA_STEPS: tuple[tuple[str, str, str], ...] = (
    ("Discover", "→", "le client, sans adresse (0.0.0.0), cherche un serveur DHCP par diffusion"),
    ("Offer", "←", "le serveur propose une adresse, le masque, la passerelle, le DNS et la durée du bail"),
    ("Request", "→", "le client demande l'adresse proposée (diffusion : les autres serveurs savent)"),
    ("Acknowledge", "←", "le serveur confirme : le bail commence, le client configure sa carte"),
)


def dora_svg() -> str:
    width = 380
    parts = [
        _box(6, 6, 120, 36, ["Client DHCP", "PC-03 (carte)"]),
        _box(234, 6, 140, 36, ["Serveur DHCP", f"SRV-01 {LAN_SERVER}"]),
        f'<path d="M66 42 V{60 + 74 * len(DORA_STEPS)}" stroke="{_STROKE}" stroke-width="1.5" stroke-dasharray="4 3"/>',
        f'<path d="M304 42 V{60 + 74 * len(DORA_STEPS)}" stroke="{_STROKE}" stroke-width="1.5" stroke-dasharray="4 3"/>',
    ]
    for i, (name, direction, detail) in enumerate(DORA_STEPS):
        y = 66 + 74 * i
        x1, x2 = (66, 304) if direction == "→" else (304, 66)
        tip = -8 if direction == "→" else 8
        parts.append(f'<path d="M{x1} {y} H{x2 + tip}" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(f'<path d="M{x2 + 2 * tip} {y - 6} L{x2} {y} L{x2 + 2 * tip} {y + 6}" fill="none" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(f'<text x="190" y="{y - 8}" font-size="12.5" font-weight="700" text-anchor="middle">{i + 1}. {name} {direction}</text>')
        parts.append(_text_lines(190, y + 16, _wrap(detail, 40), size=11, anchor="middle", step=14))
    return _svg(width, 66 + 74 * len(DORA_STEPS), parts)


DORA_FIGURE = Figure(
    key="pr20-dhcp-dora",
    title="Obtention d'une adresse par DHCP : Discover, Offer, Request, Acknowledge",
    alt=(
        "Échange entre un client et un serveur DHCP, en quatre messages : 1 Discover, du client "
        "vers le serveur, en diffusion, le client n'ayant pas encore d'adresse ; 2 Offer, du "
        "serveur vers le client : adresse, masque, passerelle, DNS et durée du bail ; 3 Request, "
        "du client : il demande l'adresse proposée ; 4 Acknowledge, du serveur : confirmation, "
        "le bail commence."
    ),
    caption=(
        "DORA : quatre messages pour obtenir un bail. Sans réponse, Windows s'attribue une "
        "adresse 169.254.x.y (APIPA)."
    ),
    svg=dora_svg(),
)


# =============================================================================================
# 6. Sorties de commandes fictives, calculées depuis un `Host`
# =============================================================================================

WIN_LEASE = ("lundi 26 octobre 2026 08:02", "mardi 27 octobre 2026 08:02")


def ipconfig_all_lines(host: Host, *, dhcp_server: str | None = LAN_SERVER, apipa: bool = False,
                       iface: str = "Ethernet") -> tuple[str, ...]:
    """Extrait simplifié de `ipconfig /all` (Windows en français, points de suite raccourcis)."""
    lines = [
        f"Carte Ethernet {iface} :",
        "   Description. . . . : Contrôleur Ethernet",
        f"   Adresse physique . : {normalize_mac(host.mac)}",
        f"   DHCP activé. . . . : {'Oui' if host.dhcp else 'Non'}",
    ]
    if apipa:
        lines.append(f"   IPv4 d'autoconfig. : {host.ip}(préféré)")
    else:
        lines.append(f"   Adresse IPv4 . . . : {host.ip}(préféré)")
    lines.append(f"   Masque de s.-réseau: {host.mask}")
    if host.dhcp and not apipa:
        lines.append(f"   Bail obtenu. . . . : {WIN_LEASE[0]}")
        lines.append(f"   Bail expirant. . . : {WIN_LEASE[1]}")
    lines.append(f"   Passerelle défaut. : {host.gateway or ''}".rstrip())
    if host.dhcp and not apipa and dhcp_server:
        lines.append(f"   Serveur DHCP . . . : {dhcp_server}")
    if host.dns:
        lines.append(f"   Serveurs DNS . . . : {host.dns[0]}")
    return tuple(lines)


def ip_addr_lines(host: Host, iface: str = "enp3s0") -> tuple[str, ...]:
    facts = host.facts
    dyn = " dynamic" if host.dhcp else ""
    return (
        "$ ip addr show " + iface,
        f"2: {iface}: <BROADCAST,MULTICAST,UP,LOWER_UP>",
        "    mtu 1500 state UP",
        f"    link/ether {mac_linux(host.mac)}",
        f"    inet {host.ip}/{host.prefix} brd {facts.broadcast}",
        f"      scope global{dyn} {iface}",
    )


def ip_route_lines(host: Host, iface: str = "enp3s0") -> tuple[str, ...]:
    facts = host.facts
    proto = "dhcp" if host.dhcp else "static"
    lines = ["$ ip route"]
    if host.gateway:
        lines.append(f"default via {host.gateway} dev {iface}")
        lines.append(f"    proto {proto} metric 100")
    lines.append(f"{facts.cidr} dev {iface} proto kernel")
    lines.append(f"    scope link src {host.ip}")
    return tuple(lines)


IPCONFIG_FIGURE = Figure(
    key="pr20-ipconfig-all",
    title="Sortie fictive de ipconfig /all sur PC-01",
    alt=(
        "Capture texte fictive de la commande ipconfig /all sur PC-01 : adresse physique "
        f"{normalize_mac(LAN_BY_NAME['PC-01'].mac)}, DHCP activé, adresse IPv4 "
        f"{LAN_BY_NAME['PC-01'].ip}, masque {LAN_BY_NAME['PC-01'].mask}, bail obtenu et expirant, "
        f"passerelle {LAN_ROUTER}, serveur DHCP {LAN_SERVER}, serveur DNS {LAN_SERVER}."
    ),
    caption="ipconfig /all : ce qu'il faut relever (MAC, DHCP, IPv4, masque, bail, passerelle, DHCP, DNS). Capture fictive simplifiée.",
    svg=screen_svg(("C:\\> ipconfig /all", "", *ipconfig_all_lines(LAN_BY_NAME["PC-01"])),
                   label="capture fictive — présentation simplifiée"),
)

LINUX_FIGURE = Figure(
    key="pr20-ip-addr-route",
    title="Sorties fictives de ip addr et ip route sur PC-04 (Linux)",
    alt=(
        f"Capture texte fictive sur PC-04 : ip addr montre l'interface enp3s0 active (UP), la MAC "
        f"{mac_linux(LAN_BY_NAME['PC-04'].mac)}, l'adresse {LAN_BY_NAME['PC-04'].ip}/24 et la "
        f"diffusion {LAN_BY_NAME['PC-04'].facts.broadcast} ; ip route montre la route par défaut via "
        f"{LAN_ROUTER} et la route locale {LAN_NETWORK}."
    ),
    caption="ip addr (MAC, IP/préfixe, diffusion, état) et ip route (route par défaut = passerelle, route locale). Capture fictive simplifiée.",
    svg=screen_svg((*ip_addr_lines(LAN_BY_NAME["PC-04"]), "", *ip_route_lines(LAN_BY_NAME["PC-04"])),
                   label="capture fictive — présentation simplifiée"),
)


def ipv4_dialog_svg(host: Host) -> str:
    """Capture fictive de la fenêtre Windows « Propriétés de Protocole Internet version 4 »."""
    width = 380
    parts = [
        f'<rect x="2" y="2" width="{width - 4}" height="318" rx="6" fill="#ffffff" stroke="{_STROKE}" stroke-width="2"/>',
        f'<rect x="2" y="2" width="{width - 4}" height="28" rx="6" fill="#e7ecf7" stroke="{_STROKE}" stroke-width="2"/>',
        '<text x="12" y="21" font-size="12" font-weight="700">Propriétés de : Protocole Internet version 4</text>',
    ]

    def radio(y: int, label: str, on: bool) -> str:
        dot = f'<circle cx="20" cy="{y - 4}" r="3.5" fill="#1b2333"/>' if on else ""
        mark = "(●)" if on else "(○)"
        return (f'<circle cx="20" cy="{y - 4}" r="6" fill="#fff" stroke="{_STROKE}" stroke-width="1.5"/>{dot}'
                f'<text x="32" y="{y}" font-size="11.5">{escape(label)} {mark}</text>')

    def field(y: int, label: str, value: str) -> str:
        return (f'<text x="32" y="{y + 14}" font-size="11.5">{escape(label)}</text>'
                f'<rect x="200" y="{y}" width="166" height="20" rx="3" fill="#fff" stroke="{_STROKE}"/>'
                f'<text x="206" y="{y + 14}" font-size="11.5" font-family="{_MONO}">{escape(value)}</text>')

    static = not host.dhcp
    parts.append(radio(52, "Obtenir une adresse IP automatiquement", not static))
    parts.append(radio(74, "Utiliser l'adresse IP suivante :", static))
    parts.append(field(84, "Adresse IP :", host.ip if static else ""))
    parts.append(field(110, "Masque de sous-réseau :", host.mask if static else ""))
    parts.append(field(136, "Passerelle par défaut :", (host.gateway or "") if static else ""))
    parts.append(radio(184, "Obtenir les adresses DNS automatiquement", not static))
    parts.append(radio(206, "Utiliser l'adresse DNS suivante :", static))
    parts.append(field(216, "Serveur DNS préféré :", host.dns[0] if static and host.dns else ""))
    parts.append(field(242, "Serveur DNS auxiliaire :", host.dns[1] if static and len(host.dns) > 1 else ""))
    parts.append('<rect x="200" y="282" width="78" height="26" rx="4" fill="#e7ecf7" stroke="#33415c"/>'
                 '<text x="239" y="299" font-size="12" text-anchor="middle">OK</text>'
                 '<rect x="288" y="282" width="78" height="26" rx="4" fill="#fff" stroke="#33415c"/>'
                 '<text x="327" y="299" font-size="12" text-anchor="middle">Annuler</text>')
    parts.append('<text x="12" y="300" font-size="10.5" font-style="italic">capture fictive</text>')
    return _svg(width, 324, parts)


# Équipement à adresse fixe du même réseau (NAS), configuré à la main hors de l'étendue DHCP.
STATIC_EXAMPLE = Host("NAS-01", "stockage, adresse fixe", "192.168.10.20", 24, LAN_ROUTER, (LAN_SERVER,), "00-11-32-AA-BB-20")

DIALOG_FIGURE = Figure(
    key="pr20-fenetre-ipv4",
    title="Capture fictive : configuration IPv4 manuelle sous Windows",
    alt=(
        "Fenêtre fictive « Propriétés de : Protocole Internet version 4 » : l'option « Utiliser "
        f"l'adresse IP suivante » est cochée ; adresse IP {STATIC_EXAMPLE.ip}, masque "
        f"{STATIC_EXAMPLE.mask}, passerelle par défaut {STATIC_EXAMPLE.gateway} ; « Utiliser "
        f"l'adresse DNS suivante » cochée, serveur DNS préféré {STATIC_EXAMPLE.dns[0]}, auxiliaire vide."
    ),
    caption=(
        f"Adresse fixe {STATIC_EXAMPLE.ip}/24 : dans le réseau, hors de l'étendue DHCP "
        f"{LAN_POOL[0]}–{LAN_POOL[1]}, passerelle et DNS du plan. Capture fictive."
    ),
    svg=ipv4_dialog_svg(STATIC_EXAMPLE),
)


# =============================================================================================
# 7. Démarche et arbres de diagnostic
# =============================================================================================

LADDER_STEPS: tuple[tuple[str, str], ...] = (
    ("État du lien", "Voyant, « câble réseau débranché », Wi-Fi associé, carte activée, bonne interface."),
    ("Relever la configuration", "ipconfig /all ou ip addr + ip route : IP, masque, passerelle, DNS, DHCP."),
    ("ping 127.0.0.1", "La pile TCP/IP du poste répond (bouclage) ; ne teste pas le câble."),
    ("ping de sa propre IP", "L'adresse est bien attribuée à la carte."),
    ("ping d'un voisin ou de la passerelle", "Le réseau local fonctionne (même sous-réseau)."),
    ("ping d'une IP distante", "La passerelle route vers l'extérieur (tracert / traceroute pour situer)."),
    ("ping d'un nom, nslookup", "La résolution DNS fonctionne."),
)

LADDER_FIGURE = Figure(
    key="pr20-demarche-ping",
    title="Démarche de test, du plus proche au plus lointain",
    alt=(
        "Sept étapes reliées par des flèches : 1 vérifier l'état du lien ; 2 relever la "
        "configuration avec ipconfig /all ou ip addr et ip route ; 3 ping 127.0.0.1 ; 4 ping de "
        "sa propre adresse ; 5 ping d'un voisin ou de la passerelle ; 6 ping d'une adresse IP "
        "distante, tracert pour situer ; 7 ping d'un nom et nslookup."
    ),
    caption=(
        "Tester du plus proche au plus lointain : la première étape qui échoue situe la panne. "
        "Un ping sans réponse n'est pas une preuve : l'ICMP peut être filtré par un pare-feu."
    ),
    svg=step_flow_svg(LADDER_STEPS, width=380),
)

TREE_DNS = (
    (
        ("Le serveur DNS relevé est-il celui du plan ?", "Corriger le DNS (DHCP ou fiche statique), vider le cache (ipconfig /flushdns), retester."),
        ("Le serveur DNS est-il joignable (ping de son IP) ?", "Serveur DNS arrêté ou injoignable : prévenir l'administrateur, tester avec un autre serveur autorisé."),
        ("nslookup du nom répond-il ?", "Nom mal écrit ou absent de la zone : vérifier l'orthographe et le suffixe DNS."),
    ),
    "La résolution fonctionne : chercher du côté du service (site, navigateur, proxy). Ce n'est pas une panne d'Internet.",
)
TREE_APIPA = (
    (
        ("Le lien est-il actif (pas de « média déconnecté ») ?", "Couche physique : câble, prise, port du switch, carte désactivée, Wi-Fi non associé."),
        ("Les autres postes obtiennent-ils un bail ?", "Serveur DHCP arrêté, étendue pleine ou box en panne : contrôler le serveur DHCP."),
        ("ipconfig /release puis /renew donne-t-il un bail ?", "Problème entre ce poste et le serveur : port, VLAN, pare-feu ; tester une autre prise."),
    ),
    "Bail obtenu : relever IP, masque, passerelle, DNS, puis ping passerelle et nom. APIPA = indice, pas preuve.",
)
TREE_TWO_HOSTS = (
    (
        ("Les deux liens sont-ils actifs ?", "Physique : câble, port, carte désactivée, mauvaise interface."),
        ("ping 127.0.0.1 et ping de sa propre IP réussissent-ils ?", "Pile IP ou carte : pilote, carte désactivée, aucune adresse attribuée."),
        ("Mêmes réseau et masque sur les deux postes ?", "Corriger IP ou masque ; sinon passer par un routeur avec une passerelle correcte."),
        ("Pas de doublon d'adresse (conflit, arp -a) ?", "Changer l'adresse en doublon et corriger le plan."),
        ("Le ping répond-il ?", "Pare-feu qui filtre l'ICMP : tester le service visé (partage) avant de conclure."),
    ),
    "La communication IP fonctionne : tester le service demandé (partage, imprimante) et documenter.",
)

TREE_FIGURES: tuple[Figure, ...] = (
    Figure(
        key="pr20-arbre-dns",
        title="Arbre de diagnostic : le ping par adresse IP répond, le ping par nom échoue",
        alt="Arbre de décision : " + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(TREE_DNS[0], 1))
        + " Si tout est oui : " + TREE_DNS[1],
        caption="« ping IP OK, nom KO » : l'accès réseau fonctionne, on cherche du côté de la résolution de noms.",
        svg=decision_tree_svg(*TREE_DNS),
    ),
    Figure(
        key="pr20-arbre-apipa",
        title="Arbre de diagnostic : le poste a une adresse 169.254.x.y (APIPA)",
        alt="Arbre de décision : " + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(TREE_APIPA[0], 1))
        + " Si tout est oui : " + TREE_APIPA[1],
        caption="APIPA : le poste n'a reçu aucune réponse DHCP. On remonte du câble vers le serveur DHCP.",
        svg=decision_tree_svg(*TREE_APIPA),
    ),
    Figure(
        key="pr20-arbre-deux-postes",
        title="Arbre de diagnostic : deux machines ne communiquent pas",
        alt="Arbre de décision : " + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(TREE_TWO_HOSTS[0], 1))
        + " Si tout est oui : " + TREE_TWO_HOSTS[1],
        caption="Deux machines ne communiquent pas : physique, pile IP, adressage, doublon, filtrage — dans cet ordre.",
        svg=decision_tree_svg(*TREE_TWO_HOSTS),
    ),
)

PR20_FIGURES: tuple[Figure, ...] = (
    LAN_FIGURE, MAC_FIGURE, *BITS_FIGURES, DORA_FIGURE, IPCONFIG_FIGURE, LINUX_FIGURE, DIALOG_FIGURE,
    LADDER_FIGURE, *TREE_FIGURES,
)

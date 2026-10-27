"""EX04 « Examen blanc écrit — réseau, configuration et dépannage » — données des dossiers et
schémas (ticket #233).

Une seule source pour le sujet affiché, les documents des questions et le corrigé ; chaque
verdict est calculé avec la règle **du cours** qui l'enseigne :
- **partie 1** : plan d'un réseau, domaines de collision et de diffusion (`Lan`,
  `collision_domains`, `broadcast_domains`, PR19), adresse de la trame (`next_hop`, PR19),
  NetBEUI (`crosses_router`, PR19) ; calculs IPv4 et MAC (`subnet_facts`, `mask_to_prefix`,
  `same_subnet`, `smallest_prefix_for`, `address_kind`, `mac_is_group`,
  `mac_is_locally_administered`, PR20) ;
- **dossier A** (cabinet, connexion directe puis mini-réseau) : câble et Auto MDI-X
  (`cable_needed`, PR21), résultat des pings (`ping_outcome`, `ping_lines`, PR21), plan
  d'adressage (`AddressPlan`, `plan_errors`, PR20) ;
- **dossier B** (agence, dépannage) : relevés `ipconfig /all`, `ip addr`, `ip route`
  (PR20), `ping`, `tracert`, `nslookup`, journal DHCP (PR24) ;
- **dossier C** (bureau d'architectes, Wi-Fi et partages) : fiche du point d'accès
  (`audit_config`, `passphrase_issues`), canal (`best_channel_24`, `interference_24`),
  répéteur (`received_dbm`, `link_rate`, `repeater_mbps`, PR25) ; accès effectif partage + NTFS
  (`effective_access`, `limiting_layer`, PR23) ; imprimante et partage (`in_pool`, PR24 ;
  `net_use_lines`, `port_test_lines`, PR23).

Toutes les situations, entreprises, personnes, adresses et mesures sont **fictives** (adresses
publiques des plages de documentation RFC 5737). Les trois schémas utilisés dans les questions
sont aussi enregistrés en fichiers statiques (`app/static/img/ampcr-pratique/`) ; un test vérifie
qu'ils sont identiques au SVG produit ici. Ils ne donnent **aucun verdict** (pas de ✓ / ✗, pas
de numéro de domaine, pas d'appréciation du signal) : c'est au candidat de conclure.
"""

from html import escape

from app.v1.ampcr_pratique_pr19_figures import (
    N_HUB,
    N_PC,
    N_ROUTER,
    N_SWITCH,
    Lan,
    broadcast_domains,
    collision_domain_of_links,
    collision_domains,
    crosses_router,
    domains_svg,
    next_hop,
)
from app.v1.ampcr_pratique_pr20_figures import (
    KIND_LINK_LOCAL,
    KIND_LOOPBACK,
    KIND_PRIVATE,
    KIND_PUBLIC,
    AddressPlan,
    Host,
    address_kind,
    ip_addr_lines,
    ip_route_lines,
    ipconfig_all_lines,
    is_local_for,
    mac_is_group,
    mac_is_locally_administered,
    mask_to_prefix,
    plan_errors,
    same_subnet,
    smallest_prefix_for,
    subnet_facts,
)
from app.v1.ampcr_pratique_pr21_figures import (
    CABLE_ANY,
    OUT_FAILURE,
    OUT_TIMEOUT,
    OUT_UNREACHABLE,
    _pc_box,
    cable_needed,
    ipconfig_static_lines,
    ping_lines,
    ping_outcome,
)
from app.v1.ampcr_pratique_pr23_figures import (
    AUTH_USERS,
    EVERYONE,
    LEVEL_MODIFY,
    LEVEL_READ,
    LOCAL_ADMINS,
    SHARE_ROOT,
    Account,
    Folder,
    Share,
    effective_access,
    limiting_layer,
    net_use_lines,
    port_test_lines,
    short_path,
)
from app.v1.ampcr_pratique_pr23_figures import _a as _ace
from app.v1.ampcr_pratique_pr24_figures import (
    NS_OK,
    NS_TIMEOUT,
    dnsmasq_lines,
    in_pool,
    is_documentation,
    no_address_events,
    nslookup_lines,
    pool_size,
    tracert_lines,
    win_ping_lines,
    win_ping_unknown_name,
)
from app.v1.ampcr_pratique_pr25_figures import (
    BAND_24,
    WPA_TKIP,
    ApConfig,
    Neighbor,
    audit_config,
    best_channel_24,
    interference_24,
    link_rate,
    networks_lines,
    passphrase_issues,
    received_dbm,
    repeater_mbps,
    useful_mbps,
)
from app.v1.ampcr_pratique_visuals import Figure, _svg, _text_lines, _wrap

STATIC_DIR_REF = "img/ampcr-pratique"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme les cours)
_STROKE = "#33415c"

# =============================================================================================
# Partie 1 — plan d'un réseau (question X01)
# =============================================================================================

PLAN_LAN = Lan(
    nodes=(
        ("R1", N_ROUTER, 190, 34),
        ("SW1", N_SWITCH, 95, 104), ("SW2", N_SWITCH, 300, 104),
        ("PC1", N_PC, 25, 178), ("PC2", N_PC, 72, 178), ("HUB", N_HUB, 150, 178),
        ("PC3", N_PC, 105, 250), ("PC4", N_PC, 150, 250), ("PC5", N_PC, 195, 250),
        ("PC6", N_PC, 265, 178), ("PC7", N_PC, 340, 178),
    ),
    links=(
        ("R1", "SW1"), ("R1", "SW2"), ("SW1", "PC1"), ("SW1", "PC2"), ("SW1", "HUB"),
        ("HUB", "PC3"), ("HUB", "PC4"), ("HUB", "PC5"), ("SW2", "PC6"), ("SW2", "PC7"),
    ),
)
PLAN_COLLISIONS = collision_domains(PLAN_LAN)  # 7 : le hub réunit ses 4 liaisons
PLAN_BROADCASTS = broadcast_domains(PLAN_LAN)  # 2 : une par interface du routeur
PLAN_HUB_DOMAIN_LINKS = tuple(
    link for link, domain in zip(PLAN_LAN.links, collision_domain_of_links(PLAN_LAN), strict=True)
    if domain == collision_domain_of_links(PLAN_LAN)[PLAN_LAN.links.index(("SW1", "HUB"))]
)

# Adresses du plan (tableau de la partie 1).
PLAN_PREFIX = 24
R1_LAN_A = ("R1, interface vers SW1", "192.168.1.1", "00-1D-AA-4E-01-01")
R1_LAN_B = ("R1, interface vers SW2", "192.168.2.1", "00-1D-AA-4E-02-01")
PLAN_PC3 = ("PC3", "192.168.1.13", "3C-52-82-1A-01-13")
PLAN_PC4 = ("PC4", "192.168.1.14", "3C-52-82-1A-01-14")
PLAN_PC6 = ("PC6", "192.168.2.16", "3C-52-82-1A-02-16")
PLAN_ADDRESSES = (R1_LAN_A, R1_LAN_B, PLAN_PC3, PLAN_PC4, PLAN_PC6)
# PC3 → PC6 : autre réseau → la trame va à la passerelle (MAC de R1 côté SW1).
PC3_TO_PC6_HOP = next_hop(PLAN_PC3[1], PLAN_PREFIX, PLAN_PC6[1], R1_LAN_A[1])
PC3_TO_PC6_DST_MAC = {R1_LAN_A[1]: R1_LAN_A[2], PLAN_PC6[1]: PLAN_PC6[2]}[PC3_TO_PC6_HOP]
# PC3 → PC4 : même réseau → trame directe vers PC4.
PC3_TO_PC4_HOP = next_hop(PLAN_PC3[1], PLAN_PREFIX, PLAN_PC4[1], R1_LAN_A[1])
NETBEUI_CROSSES = crosses_router("NetBEUI")  # False : non routable

PLAN_FIGURE = Figure(
    key="ex04-plan-reseau",
    title="Document 1 — Plan du réseau de l'entreprise (schéma fictif)",
    alt=(
        "Plan d'un réseau : le routeur R1 est relié à deux switchs, SW1 et SW2. SW1 relie PC1, PC2 et un hub ; "
        "le hub relie PC3, PC4 et PC5. SW2 relie PC6 et PC7. Une ligne représente un câble. Le schéma ne donne "
        "aucun nombre de domaines."
    ),
    caption="Plan fictif : R routeur, SW switch, HUB hub, PC poste. Une ligne = un câble.",
    svg=domains_svg(PLAN_LAN, numbered=False, zones=False),
)
PLAN_FIGURE_FILE = f"{STATIC_DIR_REF}/ex04-plan-reseau.svg"

# =============================================================================================
# Partie 1 — calculs IPv4 et MAC (question X02)
# =============================================================================================

# (repère, adresse, préfixe donné ou masque donné)
CALC_ROWS: tuple[tuple[str, str, str], ...] = (
    ("a", "192.168.40.77", "/26"),
    ("b", "10.12.200.9", "/21"),
    ("c", "172.20.5.130", "255.255.255.192"),
    ("d", "192.168.40.200", "/27"),
)


def _prefix_of(given: str) -> int:
    return int(given[1:]) if given.startswith("/") else mask_to_prefix(given)


CALC_FACTS = {ref: subnet_facts(ip, _prefix_of(given)) for ref, ip, given in CALC_ROWS}
# a et d sont-ils dans le même réseau ? (même /26 ? non : .64 et .192)
CALC_A_D_SAME = same_subnet("192.168.40.77", 26, "192.168.40.200", 26)
CALC_HOSTS_NEEDED = 50
CALC_SMALLEST_PREFIX = smallest_prefix_for(CALC_HOSTS_NEEDED)  # /26 : 62 hôtes

MAC_ROWS: tuple[tuple[str, str], ...] = (
    ("M1", "3C-52-82-1A-2B-01"),  # adresse du fabricant, unicast
    ("M2", "DA-A1-19-5E-77-02"),  # administrée localement (MAC aléatoire du Wi-Fi)
    ("M3", "01-00-5E-00-00-FB"),  # adresse de groupe (multicast)
)
MAC_FACTS = {ref: (mac_is_group(mac), mac_is_locally_administered(mac)) for ref, mac in MAC_ROWS}
# 172.31.4.9 est encore dans 172.16.0.0/12 (privée) ; 172.32.4.9 en sort (publique).
KIND_ROWS: tuple[tuple[str, str], ...] = (
    ("K1", "169.254.12.7"), ("K2", "127.0.0.1"), ("K3", "172.31.4.9"), ("K4", "172.32.4.9"),
)
KIND_FACTS = {ref: address_kind(ip) for ref, ip in KIND_ROWS}
assert KIND_FACTS == {"K1": KIND_LINK_LOCAL, "K2": KIND_LOOPBACK, "K3": KIND_PRIVATE, "K4": KIND_PUBLIC}

# =============================================================================================
# Dossier A — cabinet « Kiné Sambre » : connexion directe (X03), mini-réseau (X04)
# =============================================================================================

DIRECT_A = Host("PC-ACCUEIL", "poste fixe (partage le dossier Agenda)", "192.168.10.1", 24, None, (), "3C-52-82-4D-10-01")
DIRECT_B_BAD = Host("PORT-KINE", "portable du kiné", "192.168.1.2", 24, None, (), "A4-C3-F0-12-34-02")
DIRECT_B_OK = Host("PORT-KINE", "portable du kiné", "192.168.10.2", 24, None, (), "A4-C3-F0-12-34-02")
# PC-ACCUEIL : carte 10/100 sans Auto MDI-X ; PORT-KINE : carte 1 Gb/s avec Auto MDI-X.
DIRECT_CABLE = cable_needed("PC", "Portable", auto_a=False, auto_b=True)
assert DIRECT_CABLE == CABLE_ANY
DIRECT_CABLE_WITHOUT_AUTO = cable_needed("PC", "Portable")  # « Câble croisé »
DIRECT_SHARE_UNC = f"\\\\{DIRECT_A.ip}\\Agenda"

# 1er relevé : depuis PORT-KINE (mauvais réseau, sans passerelle) vers PC-ACCUEIL.
DIRECT_OUT_1 = ping_outcome(DIRECT_B_BAD, DIRECT_A.ip, DIRECT_A)
assert DIRECT_OUT_1 == OUT_FAILURE
DIRECT_PING_1 = ping_lines(DIRECT_B_BAD, DIRECT_A.ip, DIRECT_OUT_1)
# 2e relevé, après correction de l'adresse : le pare-feu de PC-ACCUEIL bloque l'écho ICMP.
DIRECT_OUT_2 = ping_outcome(DIRECT_B_OK, DIRECT_A.ip, DIRECT_A, icmp_allowed=False)
assert DIRECT_OUT_2 == OUT_TIMEOUT
DIRECT_PING_2 = ping_lines(DIRECT_B_OK, DIRECT_A.ip, DIRECT_OUT_2)
DIRECT_IPCONFIG_A = ipconfig_static_lines(DIRECT_A)
DIRECT_IPCONFIG_B = ipconfig_static_lines(DIRECT_B_BAD)

# Mini-réseau : box en .254 (passerelle, DNS, DHCP .100 à .199), adresses fixes des postes
# de .1 à .19, imprimante de .20 à .49 (conventions du cours PR21).
CAB_NETWORK = "192.168.10.0/24"
CAB_BOX_IP = "192.168.10.254"
CAB_POOL = ("192.168.10.100", "192.168.10.199")
CAB_BOX = Host("BOX", "box : passerelle, DNS, DHCP", CAB_BOX_IP, 24, None, (), "00-1D-AA-7E-10-FE")
CAB_HOSTS: tuple[Host, ...] = (
    CAB_BOX,
    Host("PC-ACCUEIL", "accueil, fixe", "192.168.10.1", 24, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-01"),
    Host("PC-KINE1", "cabinet 1, fixe", "192.168.10.11", 24, "192.168.10.1", (CAB_BOX_IP,), "3C-52-82-4D-10-11"),
    Host("PC-KINE2", "cabinet 2, fixe", "192.168.10.12", 16, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-12"),
    Host("PC-KINE3", "cabinet 3, fixe", "192.168.10.150", 24, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-13"),
    Host("PORT-KINE", "portable, DHCP", "192.168.10.101", 24, CAB_BOX_IP, (CAB_BOX_IP,), "A4-C3-F0-12-34-02", dhcp=True),
    Host("IMP-01", "imprimante, fixe", "192.168.10.11", 24, CAB_BOX_IP, (CAB_BOX_IP,), "00-80-77-31-10-20"),
)
CAB_PLAN = AddressPlan(CAB_NETWORK, CAB_HOSTS, CAB_BOX_IP, CAB_BOX_IP, CAB_POOL)
CAB_ERRORS = tuple(plan_errors(CAB_PLAN))
CAB_POSTS = 5  # postes du cabinet (accueil, 3 cabinets, portable) + 1 imprimante
CAB_SWITCH_PORTS_NEEDED = len(CAB_HOSTS)  # 6 équipements + liaison vers la box = 7 ports
CAB_SWITCH_PORTS = 8

# Corrections retenues (postes fixes de .1 à .19, imprimante en .20).
CAB_FIXED: tuple[Host, ...] = (
    CAB_BOX,
    CAB_HOSTS[1],
    Host("PC-KINE1", "cabinet 1, fixe", "192.168.10.11", 24, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-11"),
    Host("PC-KINE2", "cabinet 2, fixe", "192.168.10.12", 24, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-12"),
    Host("PC-KINE3", "cabinet 3, fixe", "192.168.10.13", 24, CAB_BOX_IP, (CAB_BOX_IP,), "3C-52-82-4D-10-13"),
    CAB_HOSTS[5],
    Host("IMP-01", "imprimante, fixe", "192.168.10.20", 24, CAB_BOX_IP, (CAB_BOX_IP,), "00-80-77-31-10-20"),
)
assert plan_errors(AddressPlan(CAB_NETWORK, CAB_FIXED, CAB_BOX_IP, CAB_BOX_IP, CAB_POOL)) == []


def cabinet_svg(hosts: tuple[Host, ...]) -> str:
    """Mini-réseau en étoile : box en haut, switch à gauche, une boîte par équipement avec sa
    configuration relevée (adresse/préfixe, passerelle, DNS). Aucune indication de conformité."""
    width = 380
    box, *others = hosts
    parts = [
        _pc_box(72, 6, 304, [f"{box.name} — passerelle, DNS, DHCP", f"LAN : {box.ip}/{box.prefix} · Internet : 203.0.113.45"]),
        f'<path d="M58 30 H72" stroke="{_STROKE}" stroke-width="2"/>',
    ]
    row_h, gap, top = 60, 6, 58
    bottom = top + len(others) * (row_h + gap) - gap
    parts.append(f'<rect x="4" y="6" width="54" height="{bottom - 6}" rx="8" fill="#e7ecf7" stroke="{_STROKE}" '
                 'stroke-width="1.5"/>')
    parts.append(_text_lines(31, 76, ["Switch"], size=11.5, weight="700", anchor="middle"))
    parts.append(_text_lines(31, 92, [f"{CAB_SWITCH_PORTS} ports"], size=10, anchor="middle"))
    for index, host in enumerate(others):
        y = top + index * (row_h + gap)
        mid = y + row_h // 2
        mode = "DHCP" if host.dhcp else "fixe"
        parts.append(f'<path d="M58 {mid} H72" stroke="{_STROKE}" stroke-width="2"/>')
        parts.append(_pc_box(72, y, 304, [
            f"{host.name} — {host.role.split(',')[0]}",
            f"IP {host.ip} · masque {host.mask} ({mode})",
            f"passerelle {host.gateway or '(vide)'} · DNS {host.dns[0] if host.dns else '(vide)'}",
        ], key=host.name))
    y = bottom + 20
    lines = _wrap(f"Box : étendue DHCP de {CAB_POOL[0]} à {CAB_POOL[1]}. Valeurs relevées sur chaque appareil.", 60)
    parts.append(_text_lines(8, y, lines, size=10.5, step=13))
    return _svg(width, y + 13 * len(lines), parts)


def _cabinet_alt(hosts: tuple[Host, ...]) -> str:
    box, *others = hosts
    return (
        f"Mini-réseau en étoile : la box {box.ip}/{box.prefix} (passerelle, DNS, DHCP, étendue {CAB_POOL[0]} à "
        f"{CAB_POOL[1]}) est reliée à un switch de {CAB_SWITCH_PORTS} ports, qui relie : "
        + " ; ".join(
            f"{h.name} ({h.role}) adresse {h.ip}, masque {h.mask}, passerelle {h.gateway or 'vide'}, "
            f"DNS {h.dns[0] if h.dns else 'vide'}"
            for h in others)
        + ". Le schéma ne donne aucun verdict."
    )


CABINET_FIGURE = Figure(
    key="ex04-cabinet-mini-reseau",
    title="Dossier A, document A4 — Mini-réseau du cabinet, configurations relevées (schéma fictif)",
    alt=_cabinet_alt(CAB_HOSTS),
    caption="Configurations relevées par la stagiaire sur chaque appareil (fictives). Le schéma ne dit pas ce qui est faux.",
    svg=cabinet_svg(CAB_HOSTS),
)
CABINET_FIGURE_FILE = f"{STATIC_DIR_REF}/ex04-cabinet-mini-reseau.svg"

# =============================================================================================
# Dossier B — agence « Immo Meuse » : DNS (X05), route et DHCP (X06), panne Internet (X07)
# =============================================================================================

AG_NETWORK = "192.168.50.0/24"
AG_BOX_IP = "192.168.50.1"
AG_SRV_IP = "192.168.50.5"  # SRV-01 (Linux, dnsmasq) : DHCP et DNS interne
AG_OLD_DNS = "192.168.50.53"  # ancien serveur DNS, retiré le mois dernier
AG_NAS_IP = "192.168.50.10"
AG_POOL = ("192.168.50.100", "192.168.50.119")
AG_POOL_SIZE = pool_size(AG_POOL)  # 20 adresses
AG_LEASES = 20  # baux actifs relevés sur SRV-01 : tous attribués
WEB_NAME = "www.exemple.be"
WEB_IP = "198.51.100.20"
assert is_documentation(WEB_IP)

# X05 — poste dont le DNS a été saisi à la main (ancien serveur) : IP et Internet OK, noms KO.
AG_ACCUEIL = Host("PC-ACCUEIL", "poste Windows", "192.168.50.21", 24, AG_BOX_IP, (AG_OLD_DNS,), "3C-52-82-1A-50-21")
DNS_IPCONFIG = ("C:\\> ipconfig /all", "", *ipconfig_all_lines(AG_ACCUEIL, dhcp_server=None))
DNS_PING_GW = win_ping_lines(AG_BOX_IP, (1, 1, 1, 1))
DNS_PING_IP = win_ping_lines(WEB_IP, (14, 13, 15, 14), ttl=56)
DNS_PING_NAME = win_ping_unknown_name(WEB_NAME)
DNS_NSLOOKUP_OLD = nslookup_lines(WEB_NAME, AG_OLD_DNS, NS_TIMEOUT)
DNS_NSLOOKUP_SRV = (f"C:\\> nslookup {WEB_NAME} {AG_SRV_IP}",
                    *nslookup_lines(WEB_NAME, AG_SRV_IP, NS_OK, WEB_IP, server_name="srv-01.immo.lan")[1:])
DNS_GATEWAY_LOCAL = is_local_for(AG_ACCUEIL.ip, AG_ACCUEIL.prefix, AG_ACCUEIL.gateway or "")

# X06 (a) — poste Linux à adresse fixe sans passerelle.
AG_LINUX = Host("PC-COMPTA", "poste Linux, fixe", "192.168.50.40", 24, None, (AG_SRV_IP,), "52-54-00-3A-50-40")
LINUX_ADDR = ip_addr_lines(AG_LINUX)
LINUX_ROUTE = ip_route_lines(AG_LINUX)
LINUX_PINGS: tuple[str, ...] = (
    f"$ ping -c 2 {AG_NAS_IP}",
    f"64 bytes from {AG_NAS_IP}: icmp_seq=1 ttl=64",
    f"64 bytes from {AG_NAS_IP}: icmp_seq=2 ttl=64",
    "2 packets transmitted, 2 received, 0% packet loss",
    f"$ ping -c 2 {WEB_IP}",
    "ping: connect: Network is unreachable",
)
LINUX_HAS_DEFAULT = any(line.startswith("default") for line in LINUX_ROUTE)
LINUX_ROUTE_FIXED = ip_route_lines(Host(AG_LINUX.name, AG_LINUX.role, AG_LINUX.ip, 24, AG_BOX_IP, AG_LINUX.dns,
                                        AG_LINUX.mac))

# X06 (b) — portable d'une nouvelle agente : APIPA, étendue DHCP épuisée.
AG_NEW_LAPTOP = Host("PORT-07", "portable Windows, DHCP", "169.254.83.17", 16, None, (), "A4-C3-F0-55-50-07", dhcp=True)
APIPA_IPCONFIG = ("C:\\> ipconfig /all", "", *ipconfig_all_lines(AG_NEW_LAPTOP, apipa=True))
DHCP_LOG = dnsmasq_lines(no_address_events(AG_NEW_LAPTOP.mac, ("08:41:12", "08:41:16", "08:41:24")))
APIPA_KIND = address_kind(AG_NEW_LAPTOP.ip)
# Agrandir l'étendue : .100 à .199 → 100 adresses, toujours hors des adresses fixes.
AG_POOL_NEW = ("192.168.50.100", "192.168.50.199")
AG_POOL_NEW_SIZE = pool_size(AG_POOL_NEW)
assert not any(in_pool(ip, AG_POOL_NEW) for ip in (AG_BOX_IP, AG_SRV_IP, AG_NAS_IP, AG_ACCUEIL.ip, AG_LINUX.ip))

# X07 — panne Internet de toute l'agence : le réseau local répond, rien au-delà de la box.
OUTAGE_PING_GW = win_ping_lines(AG_BOX_IP, (1, 1, 1, 1))
OUTAGE_PING_WEB = win_ping_lines(WEB_IP, (None, None, None, None))
OUTAGE_TRACERT = tracert_lines(WEB_IP, (AG_BOX_IP, None, None))
OUTAGE_NAS = net_use_lines(f"\\\\{AG_NAS_IP}\\Dossiers", drive="S:")
BOX_STATUS: tuple[tuple[str, str], ...] = (
    ("Voyant « Internet »", "rouge fixe depuis 9 h 05"),
    ("Synchronisation (VDSL)", "non synchronisée — aucune porteuse"),
    ("Adresse IP publique", "0.0.0.0"),
    ("Réseau local", "4 ports actifs, Wi-Fi actif, DHCP actif"),
    ("Journal de la box", "09:05 perte de synchronisation de la ligne"),
)

# =============================================================================================
# Dossier C — bureau d'architectes « Atelier Linéa » : Wi-Fi (X08), droits (X09), accès (X10)
# =============================================================================================

LIN_SSID = "Linea"
LIN_NETWORK = "192.168.30.0/24"
LIN_BOX_IP = "192.168.30.254"
LIN_SRV_NAME = "SRV-FICH"
LIN_SRV_IP = "192.168.30.10"
LIN_POOL = ("192.168.30.100", "192.168.30.199")

LIN_AP = ApConfig(
    ssid=LIN_SSID,
    security=WPA_TKIP,
    passphrase="Linea2026",
    wps=True,
    admin_default=True,
    firmware_current=False,
    channel_24=3,
    width_24=40,
    ssid_hidden=True,
    guest_isolated=False,
    names=("Linéa", "Linea", "Atelier"),
)
LIN_AP_DEFECTS = audit_config(LIN_AP)
LIN_KEY_ISSUES = passphrase_issues(LIN_AP.passphrase, names=(LIN_AP.ssid, *LIN_AP.names))

LIN_NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Pharmacie-Gilles", 6, -61, "a0:21:b7:31:02:03"),
    Neighbor("Proximus-55B1", 4, -74, "f4:ca:e5:31:22:33"),
    Neighbor("Telenet-WiFi", 11, -86, "00:1d:7e:31:55:66"),
    Neighbor("Agence-Dumont", 1, -69, "c8:cd:72:31:88:99"),
)
LIN_SCAN = networks_lines(tuple((n.ssid, "WPA2 - Personnel", n) for n in LIN_NEIGHBORS))
LIN_BEST_CHANNEL = best_channel_24(LIN_NEIGHBORS)  # 11
LIN_INTERFERENCE = {ch: interference_24(ch, LIN_NEIGHBORS) for ch in (1, 6, 11)}

# Répéteur : placé aujourd'hui dans la salle de dessin du fond, puis à mi-chemin (couloir).
REP_NOW_M = 32  # point d'accès → R1, dans le local d'archives au fond de la salle de dessin
REP_NOW_UPLINK = received_dbm(REP_NOW_M, BAND_24, ("brique", "béton", "cloison"))
REP_NOW_CLIENT = received_dbm(4, BAND_24, ("cloison",))
REP_NOW_MBPS = repeater_mbps(REP_NOW_UPLINK, REP_NOW_CLIENT)
REP_MID_M, REP_MID_CLIENT_M = 12, 14
REP_MID_UPLINK = received_dbm(REP_MID_M, BAND_24, ("brique",))
REP_MID_CLIENT = received_dbm(REP_MID_CLIENT_M, BAND_24, ("béton",))
REP_MID_MBPS = repeater_mbps(REP_MID_UPLINK, REP_MID_CLIENT)
AP_DIRECT_M = 30
AP_DIRECT_DBM = received_dbm(AP_DIRECT_M, BAND_24, ("brique", "béton"))  # portable du fond, sans répéteur
AP_DIRECT_MBPS = useful_mbps(link_rate(AP_DIRECT_DBM))
REP_MEASURES: tuple[tuple[str, int], ...] = (
    ("Point d'accès → R1 (emplacement actuel, local d'archives)", REP_NOW_UPLINK),
    ("R1 → portable de la salle de dessin", REP_NOW_CLIENT),
    ("Point d'accès → portable, répéteur débranché", AP_DIRECT_DBM),
    ("Point d'accès → couloir (emplacement envisagé)", REP_MID_UPLINK),
    ("Couloir → portable de la salle de dessin", REP_MID_CLIENT),
)
# Débits de liaison 802.11n 2×2, 20 MHz, selon le signal (convention du cours PR25).
LINK_RATE_ROWS: tuple[tuple[str, int], ...] = (
    ("−60 dBm ou mieux", 144), ("−67 à −61 dBm", 104), ("−75 à −68 dBm", 52), ("−82 à −76 dBm", 13),
)


_DISTANCES = (f"Distances : point d'accès → R1 {REP_NOW_M} m ; point d'accès → R2 {REP_MID_M} m ; R2 → portable "
              f"{REP_MID_CLIENT_M} m ; point d'accès → portable {AP_DIRECT_M} m.")


def wifi_plan_svg() -> str:
    """Plan schématique (non à l'échelle) : bureau d'accueil avec le point d'accès, couloir,
    salle de dessin du fond ; positions du répéteur (actuelle, envisagée) et signaux mesurés.
    Aucune appréciation (bon, faible…)."""
    width = 380
    parts = [_text_lines(width // 2, 16, ["Atelier Linéa : plan simplifié du rez-de-chaussée"], size=12.5,
                         weight="700", anchor="middle")]
    parts.append(f'<rect x="4" y="28" width="372" height="150" fill="#ffffff" stroke="{_STROKE}" stroke-width="2.5"/>')
    # cloisons : brique entre accueil et couloir, béton entre couloir et salle du fond
    parts.append(f'<path data-wall="brique" d="M124 28 V178" stroke="{_STROKE}" stroke-width="4"/>')
    parts.append(f'<path data-wall="béton" d="M250 28 V178" stroke="{_STROKE}" stroke-width="7"/>')
    parts.append(_text_lines(14, 46, ["Accueil"], size=10, weight="700"))
    parts.append(_text_lines(134, 46, ["Couloir"], size=10, weight="700"))
    parts.append(_text_lines(256, 140, ["Salle de"], size=10, weight="700"))
    parts.append(_text_lines(256, 153, ["dessin"], size=10, weight="700"))
    parts.append(_text_lines(126, 172, ["brique"], size=9))
    parts.append(_text_lines(254, 172, ["béton"], size=9))
    parts.append(f'<path data-wall="cloison" d="M286 28 V96 H376" stroke="{_STROKE}" stroke-width="2" fill="none"/>')
    parts.append(_text_lines(292, 46, ["Archives"], size=9.5, weight="700"))
    parts.append(_text_lines(300, 110, ["cloison"], size=9))
    parts.append(f'<circle data-ap="AP" cx="40" cy="104" r="9" fill="{_STROKE}"/>')
    parts.append(_text_lines(40, 128, ["Point d'accès"], size=9.5, weight="700", anchor="middle"))
    parts.append(f'<rect data-rep="milieu" x="176" y="94" width="20" height="20" rx="3" fill="#ffffff" '
                 f'stroke="{_STROKE}" stroke-width="1.6" stroke-dasharray="4 2"/>')
    parts.append(_text_lines(186, 128, ["R2 (envisagé)"], size=9.5, anchor="middle"))
    parts.append(f'<rect data-rep="fond" x="330" y="56" width="20" height="20" rx="3" fill="{_STROKE}"/>')
    parts.append(_text_lines(340, 90, ["R1 (actuel)"], size=9.5, anchor="middle"))
    parts.append(f'<rect data-client="portable" x="320" y="132" width="26" height="16" rx="2" fill="#dbe4f3" '
                 f'stroke="{_STROKE}" stroke-width="1.2"/>')
    parts.append(_text_lines(333, 162, ["portable"], size=9.5, anchor="middle"))
    y = 198
    parts.append(_text_lines(8, y, ["Signaux mesurés (2,4 GHz)"], size=10.5, weight="700"))
    y += 8
    for label, dbm in REP_MEASURES:
        lines = _wrap(label, 48)
        h = 8 + 13 * len(lines)
        parts.append(f'<rect x="4" y="{y}" width="372" height="{h}" rx="4" fill="#f4f6fb" stroke="{_STROKE}" '
                     'stroke-width="0.8"/>')
        parts.append(_text_lines(10, y + 14, lines, size=10, step=13))
        parts.append(_text_lines(370, y + 14, [f"{dbm} dBm"], size=10.5, weight="700", anchor="end"))
        y += h + 4
    notes = ["Distances :", f"point d'accès → R1 {REP_NOW_M} m ; point d'accès → R2 {REP_MID_M} m ;",
             f"R2 → portable {REP_MID_CLIENT_M} m ; point d'accès → portable {AP_DIRECT_M} m."]
    parts.append(_text_lines(8, y + 12, notes, size=10, step=13))
    return _svg(width, y + 12 + 13 * len(notes), parts)


WIFI_FIGURE = Figure(
    key="ex04-wifi-repeteur",
    title="Dossier C, document C3 — Plan du rez-de-chaussée et mesures du répéteur (schéma fictif)",
    alt=(
        "Plan simplifié, non à l'échelle : accueil avec le point d'accès, mur de briques, couloir, mur en béton, "
        "salle de dessin du fond avec le portable ; au fond de la salle, derrière une cloison, le local d'archives "
        "où se trouve le répéteur actuel R1 ; position envisagée R2 dans le couloir. "
        "Signaux mesurés en 2,4 GHz : "
        + " ; ".join(f"{label} {dbm} dBm" for label, dbm in REP_MEASURES)
        + ". " + _DISTANCES + " Le schéma ne donne aucune appréciation du signal."
    ),
    caption="Plan fictif, non à l'échelle ; mesures relevées avec un analyseur Wi-Fi.",
    svg=wifi_plan_svg(),
)
WIFI_FIGURE_FILE = f"{STATIC_DIR_REF}/ex04-wifi-repeteur.svg"

# --- X09 : partages et NTFS de SRV-FICH --------------------------------------------------

LIN_TREE: dict[str, Folder] = {
    f.path: f
    for f in (
        Folder(SHARE_ROOT, (_ace(LOCAL_ADMINS, "Contrôle total"),), inherit=False),
        Folder(f"{SHARE_ROOT}\\Projets", (_ace("G_Architectes", "Modification"),
                                          _ace("G_Secretariat", "Lecture et exécution"))),
        Folder(f"{SHARE_ROOT}\\Projets\\Concours", (_ace(LOCAL_ADMINS, "Contrôle total"),
                                                    _ace("G_Associes", "Modification")), inherit=False),
        Folder(f"{SHARE_ROOT}\\Compta", (_ace("G_Compta", "Modification"),
                                         _ace("G_Associes", "Lecture et exécution"))),
    )
}
LIN_SHARES: dict[str, Share] = {
    s.name: s
    for s in (
        Share("Projets", f"{SHARE_ROOT}\\Projets", (_ace(AUTH_USERS, "Modifier"),)),
        Share("Compta", f"{SHARE_ROOT}\\Compta", (_ace(EVERYONE, "Lecture"),)),
    )
}
LIN_SHARES_FIXED: dict[str, Share] = {
    **LIN_SHARES,
    "Compta": Share("Compta", f"{SHARE_ROOT}\\Compta", (_ace(AUTH_USERS, "Modifier"),)),
}
LIN_USERS_GROUP = "Utilisateurs du domaine"
ARCHI = Account("tlambert", "Tom Lambert (architecte)", (LIN_USERS_GROUP, "G_Architectes"))
SECR = Account("nhaddad", "Nora Haddad (secrétariat et comptabilité)", (LIN_USERS_GROUP, "G_Secretariat", "G_Compta"))
ASSOC = Account("evermeer", "Eva Vermeer (associée)", (LIN_USERS_GROUP, "G_Architectes", "G_Associes"))
LIN_ACCOUNTS = (ARCHI, SECR, ASSOC)
LIN_PATHS = (f"{SHARE_ROOT}\\Projets", f"{SHARE_ROOT}\\Projets\\Concours", f"{SHARE_ROOT}\\Compta")


def lin_matrix(shares: dict[str, Share] = LIN_SHARES) -> dict[str, dict[str, str]]:
    return {a.login: {short_path(p): effective_access(a, p, tree=LIN_TREE, shares=shares) for p in LIN_PATHS}
            for a in LIN_ACCOUNTS}


LIN_MATRIX = lin_matrix()
LIN_MATRIX_FIXED = lin_matrix(LIN_SHARES_FIXED)
SECR_COMPTA = LIN_MATRIX["nhaddad"]["Compta"]
SECR_COMPTA_LIMIT = limiting_layer(SECR, f"{SHARE_ROOT}\\Compta", tree=LIN_TREE, shares=LIN_SHARES)
SECR_COMPTA_LOCAL = effective_access(SECR, f"{SHARE_ROOT}\\Compta", remote=False, tree=LIN_TREE, shares=LIN_SHARES)
assert SECR_COMPTA == LEVEL_READ and LIN_MATRIX_FIXED["nhaddad"]["Compta"] == LEVEL_MODIFY


def share_rows() -> tuple[tuple[str, str, str], ...]:
    return tuple((s.name, s.path, ", ".join(f"{e.principal} : {e.right}" for e in s.entries))
                 for s in LIN_SHARES.values())


def ntfs_rows() -> tuple[tuple[str, str, str], ...]:
    rows = []
    for path in LIN_PATHS:
        folder = LIN_TREE[path]
        rows.append((short_path(path), ", ".join(f"{e.principal} : {e.right}" for e in folder.entries),
                     "oui (hérite de D:\\Partages)" if folder.inherit else "non (héritage désactivé)"))
    return tuple(rows)


# --- X10 : imprimante et accès au partage --------------------------------------------------

PRINTER_PORT_IP = "192.168.30.120"  # port TCP/IP créé sur les postes à l'installation
PRINTER_NEW_IP = "192.168.30.131"  # adresse obtenue par DHCP après le remplacement de la box
PRINTER_IN_POOL = in_pool(PRINTER_PORT_IP, LIN_POOL) and in_pool(PRINTER_NEW_IP, LIN_POOL)
PRINTER_FIXED_IP = "192.168.30.20"
assert not in_pool(PRINTER_FIXED_IP, LIN_POOL)
LIN_SECR_PC = Host("PC-SECR", "poste du secrétariat", "192.168.30.104", 24, LIN_BOX_IP, (LIN_BOX_IP,),
                   "3C-52-82-1A-30-04", dhcp=True)
PRINTER_PING = ping_lines(LIN_SECR_PC, PRINTER_PORT_IP, ping_outcome(LIN_SECR_PC, PRINTER_PORT_IP, None))
assert ping_outcome(LIN_SECR_PC, PRINTER_PORT_IP, None) == OUT_UNREACHABLE
PRINTER_QUEUE: tuple[str, ...] = (
    "Imprimante « Traceur-A1 » sur PC-SECR :",
    f"  Port : IP_{PRINTER_PORT_IP} (TCP/IP standard)",
    "  État : hors connexion — 3 documents en attente",
    "Page de configuration imprimée par le traceur :",
    f"  Adresse IP : {PRINTER_NEW_IP} (DHCP)",
    "  Masque : 255.255.255.0  Passerelle : 192.168.30.254",
)
SHARE_UNC = f"\\\\{LIN_SRV_NAME}\\Projets"
SHARE_NET_USE = net_use_lines(SHARE_UNC, error=53, drive="P:")
SHARE_PING: tuple[str, ...] = (
    f"C:\\> ping -n 2 {LIN_SRV_NAME}",
    f"Envoi d'une requête 'Ping' {LIN_SRV_NAME} [{LIN_SRV_IP}]",
    f"Réponse de {LIN_SRV_IP} : octets=32 temps<1ms TTL=128",
    f"Réponse de {LIN_SRV_IP} : octets=32 temps<1ms TTL=128",
)
SHARE_PORT = port_test_lines(LIN_SRV_NAME, LIN_SRV_IP, open_=False)

# =============================================================================================
# Fichiers statiques
# =============================================================================================

EX04_FIGURES: tuple[Figure, ...] = (PLAN_FIGURE, CABINET_FIGURE, WIFI_FIGURE)
STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (PLAN_FIGURE, PLAN_FIGURE_FILE),
    (CABINET_FIGURE, CABINET_FIGURE_FILE),
    (WIFI_FIGURE, WIFI_FIGURE_FILE),
)
SCREENS: dict[str, tuple[str, ...]] = {
    "direct_ipconfig_a": DIRECT_IPCONFIG_A,
    "direct_ipconfig_b": DIRECT_IPCONFIG_B,
    "direct_ping_1": DIRECT_PING_1,
    "direct_ping_2": DIRECT_PING_2,
    "dns_ipconfig": DNS_IPCONFIG,
    "dns_pings": DNS_PING_GW + DNS_PING_IP + DNS_PING_NAME,
    "dns_nslookup": DNS_NSLOOKUP_OLD + DNS_NSLOOKUP_SRV,
    "linux": LINUX_ADDR + LINUX_ROUTE + LINUX_PINGS,
    "apipa": APIPA_IPCONFIG,
    "dhcp_log": DHCP_LOG,
    "outage": OUTAGE_PING_GW + OUTAGE_PING_WEB + OUTAGE_TRACERT + OUTAGE_NAS,
    "scan": LIN_SCAN,
    "printer": PRINTER_QUEUE + PRINTER_PING,
    "share": SHARE_NET_USE + SHARE_PING + SHARE_PORT,
}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que EX01 à EX03)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


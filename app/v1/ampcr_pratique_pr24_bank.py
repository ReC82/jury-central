"""PR24 « Dépannage réseau et Internet — dossiers d'intervention écrits » — exercices corrigés et
mini-examen (ticket #200).

Même organisation que PR06, PR11, PR15, PR16 et PR20 (`app.v1.ampcr_pratique_pr06_bank`, dont ce
module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — 8 analyses de relevés, 5 arbres de décision ou procédures, 4 dossiers
  multi-postes et 3 rapports d'intervention ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les relevés (ping, tracert, nslookup, dig, journaux DHCP, état Wi-Fi, ports du switch, arp,
routes) sont **produits par le code** (`app.v1.ampcr_pratique_pr24_figures`) depuis le réseau
de référence ; les calculs d'adressage et les erreurs de plan viennent du modèle de PR20
(`ipaddress`). Situations, relevés, adresses MAC et adresses publiques (RFC 5737) : fictifs.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)
from app.v1.ampcr_pratique_pr20_figures import (
    AddressPlan,
    Host,
    ipconfig_all_lines,
    is_local_for,
    mac_linux,
    normalize_mac,
    plan_errors,
    subnet_facts,
)
from app.v1.ampcr_pratique_pr24_figures import (
    AP_IP,
    DOMAIN,
    GUEST_NETWORK,
    GUEST_VLAN,
    ISP_DNS,
    LAN_BY_NAME,
    LAN_NETWORK,
    LAYER_STEPS,
    LEASE_DAYS,
    NAS_IP,
    NS_NXDOMAIN,
    NS_OK,
    NS_TIMEOUT,
    POOL,
    PRINTER_IP,
    ROUTER_IP,
    SERVER_IP,
    SHARE_UNC,
    SRV_FQDN,
    SSID,
    SWITCH_PORTS,
    WEB_IP,
    WEB_NAME,
    SwitchPort,
    WifiStatus,
    arp_lines,
    dnsmasq_lines,
    in_network,
    ip_link_lines,
    ip_neigh_lines,
    netsh_wlan_lines,
    no_address_events,
    nslookup_lines,
    pool_size,
    resolvectl_lines,
    test_netconnection_lines,
    tracert_lines,
    win_ping_lines,
)

PR24_CODE = "PR24"

KIND_LOGS = "analyse de relevés"
KIND_TREE = "arbre de décision ou procédure"
KIND_MULTI = "dossier multi-postes"
KIND_REPORT = "rapport d'intervention"
KIND_SCENARIO = "scénario"

REQ = ("AP-32", "AP-37")  # panne Internet, accès au réseau : exigences officielles du cours


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _ports_table(title: str, ports: tuple[SwitchPort, ...]) -> ExerciseDocument:
    return _table(
        title, ("Port", "Équipement", "État", "Vitesse / duplex", "VLAN", "Erreurs"),
        *((str(p.number), p.device, p.state, f"{p.speed} {p.duplex}", str(p.vlan), str(p.crc_errors)) for p in ports),
    )


def _ipconfig(host: Host, **kwargs) -> tuple[str, ...]:
    return ("C:\\> ipconfig /all", *ipconfig_all_lines(host, **kwargs))


PLAN_HEADER = ("Poste", "Adresse IP", "Masque", "Passerelle", "DNS", "Mode")


def _plan_rows(hosts: tuple[Host, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (h.name, h.ip, h.mask, h.gateway or "—", h.dns[0] if h.dns else "—", "DHCP" if h.dhcp else "fixe")
        for h in hosts
    )


def _port(number: int, **changes) -> SwitchPort:
    base = next(p for p in SWITCH_PORTS if p.number == number)
    return SwitchPort(**{**base.__dict__, **changes})


# =============================================================================================
# Données calculées des exercices
# =============================================================================================

# E01 : poste de bureau dans le VLAN invités.
E01_HOST = Host("PC-03", "poste Windows, DHCP", "10.30.0.57", 24, "10.30.0.1", ("10.30.0.1",), "3C-52-82-1A-20-03", dhcp=True)
E01_PORTS = tuple(_port(n, vlan=GUEST_VLAN) if n == 8 else _port(n) for n in (6, 7, 8, 9))
E01_IN_GUEST = in_network(E01_HOST.ip, GUEST_NETWORK)
E01_IN_LAN = in_network(E01_HOST.ip, LAN_NETWORK)

# E02 : tracert complet malgré des sauts muets.
E02_HOPS = (ROUTER_IP, "198.51.100.1", None, "198.51.100.9", WEB_IP)
E02_TRACERT = tracert_lines(WEB_IP, E02_HOPS)

# E03 : DNS fonctionnel, nom mal saisi.
E03_TYPO = "wwww.exemple.be"
E03_LINES = (
    *nslookup_lines(WEB_NAME, SERVER_IP, NS_OK, WEB_IP, server_name=SRV_FQDN),
    "",
    *nslookup_lines(E03_TYPO, SERVER_IP, NS_NXDOMAIN, server_name=SRV_FQDN),
)

# E04 : étendue DHCP épuisée.
E04_MAC = "F2-91-6C-3D-20-88"
E04_POOL_SIZE = pool_size()
E04_LEASES = E04_POOL_SIZE
E04_LINES = (
    *dnsmasq_lines(no_address_events(E04_MAC, ("10:41:02", "10:41:06", "10:41:14"))),
    "",
    "$ wc -l /var/lib/misc/dnsmasq.leases",
    f"{E04_LEASES} /var/lib/misc/dnsmasq.leases",
)

# E05 : Wi-Fi faible.
E05_STATUS = WifiStatus("connecté", SSID, "9c:53:22:10:20:31", "802.11n", "WPA2 - Personnel", "CCMP", "2,4 GHz", 6, 6.5, 18)
E05_LINES = netsh_wlan_lines(E05_STATUS)

# E06 : Linux sans lien.
E06_HOST = LAN_BY_NAME["PC-04"]
E06_LINES = (*ip_link_lines("enp3s0", E06_HOST.mac, carrier=False), "", "$ ip route", "(aucune route)")

# E07 : duplex et erreurs CRC.
E07_PORTS = (_port(6), _port(7, speed="100 Mb/s", duplex="half", crc_errors=1843), _port(8))

# E08 : doublon de l'adresse de l'imprimante.
E08_PRINTER = LAN_BY_NAME["IMP-01"]
E08_INTRUDER_MAC = "00-0C-43-9A-71-B2"
E08_LINES = (
    *win_ping_lines(PRINTER_IP, (1, None, 1, None)),
    "",
    *arp_lines("192.168.20.101", ((ROUTER_IP, LAN_BY_NAME["BOX-01"].mac), (PRINTER_IP, E08_INTRUDER_MAC))),
)

# E09 : procédure ordonnée (étapes affichées dans le désordre).
E09_SHOWN: tuple[int, ...] = (3, 5, 1, 4, 0, 2)

# E10 : à quelle couche s'arrête le diagnostic ?
L_PHY = "Physique ou liaison"
L_IP = "Adressage IP ou DHCP"
L_GW = "Passerelle, routage ou accès Internet"
L_DNS = "Résolution de noms (DNS)"
L_SVC = "Service ou application"
E10_CATEGORIES: tuple[str, ...] = (L_PHY, L_IP, L_GW, L_DNS, L_SVC)
E10_OBSERVATIONS: tuple[tuple[str, str], ...] = (
    (f"ping {WEB_IP} répond ; ping {WEB_NAME} : « hôte introuvable »", L_DNS),
    ("ipconfig : « Média déconnecté » sur la carte Ethernet", L_PHY),
    (f"ping {NAS_IP} répond ; Test-NetConnection NAS-01 -Port 445 : TcpTestSucceeded False", L_SVC),
    ("Adresse 169.254.20.7, masque 255.255.0.0, aucune passerelle", L_IP),
    (f"ping {ROUTER_IP} répond ; ping {WEB_IP} : 100 % de perte ; tracert s'arrête après {ROUTER_IP}", L_GW),
    ("Port du switch : 100 Mb/s au lieu de 1 Gb/s, erreurs CRC en hausse (2 315)", L_PHY),
    ("Windows signale un conflit d'adresse IP avec un autre système du réseau", L_IP),
    ("Le site s'ouvre, l'imprimante répond au ping ; « Le service Spouleur d'impression local n'est pas exécuté »", L_SVC),
)
E10_CORRECT: tuple[int, ...] = tuple(E10_CATEGORIES.index(layer) for _o, layer in E10_OBSERVATIONS)

# E14 : plan de quatre postes (+ le portable déjà en DHCP) à contrôler.
E14_HOSTS: tuple[Host, ...] = (
    Host("PC-A", "poste", "192.168.20.111", 24, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-21-11", dhcp=True),
    Host("PC-B", "poste", "192.168.20.42", 24, "192.168.20.254", (SERVER_IP,), "3C-52-82-1A-21-42"),
    Host("PC-C", "poste", "192.168.20.43", 24, ROUTER_IP, (ISP_DNS,), "3C-52-82-1A-21-43"),
    Host("PC-D", "poste", "192.168.20.150", 24, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-21-50"),
    LAN_BY_NAME["LT-01"],
)
E14_PLAN = AddressPlan(LAN_NETWORK, E14_HOSTS, ROUTER_IP, SERVER_IP, POOL)
E14_ERRORS = plan_errors(E14_PLAN)

# E15 : trois utilisateurs, trois erreurs de partage.
E15_ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("Mme Lenoir (PC-01)", "\\\\NAS01\\Compta", "« Windows ne peut pas accéder à \\\\NAS01\\Compta » — 0x80070035, chemin réseau introuvable", "membre du groupe Compta"),
    ("M. Bah (PC-02)", SHARE_UNC, "« Vous n'avez pas l'autorisation d'accéder à \\\\NAS-01\\Compta »", "groupe Atelier seulement"),
    ("Mme Roux (PC-03)", SHARE_UNC, "ouvre et lit les fichiers ; « Accès refusé » à l'enregistrement", "membre du groupe Compta"),
)

# E16 : deux pannes combinées sur le même poste.
E16_HOST = Host("PC-03", "poste Windows, fixe", "192.168.20.43", 24, ROUTER_IP, ("192.168.20.6",), "3C-52-82-1A-20-03")
E16_PORTS = (_port(7), _port(8, speed="100 Mb/s", duplex="full", crc_errors=2410), _port(9))
E16_LINES = (
    *win_ping_lines(ROUTER_IP, (2, None, 3, 1), ttl=64),
    "",
    *nslookup_lines(WEB_NAME, "192.168.20.6", NS_TIMEOUT),
)

# E17 : un second serveur DHCP sur le réseau.
E17_ROGUE_MAC = "C8-3A-35-0B-11-01"
E17_HOSTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("PC-01", "192.168.20.101/24", ROUTER_IP, SERVER_IP, SERVER_IP),
    ("PC-02", "192.168.1.34/24", "192.168.1.1", "192.168.1.1", "192.168.1.1"),
    ("PC-03", "192.168.1.35/24", "192.168.1.1", "192.168.1.1", "192.168.1.1"),
    ("PC-04", "192.168.20.104/24", ROUTER_IP, SERVER_IP, SERVER_IP),
)
E17_PORT10 = SwitchPort(10, "inconnu (MAC " + normalize_mac(E17_ROGUE_MAC) + ")", True, "100 Mb/s", "full", 1, 0)
E17_AFFECTED = tuple(name for name, ip, *_r in E17_HOSTS if not in_network(ip.split("/")[0]))

# Mini-examen.
X01_HOST = Host("PC-07", "poste Windows, DHCP", "169.254.81.20", 16, None, (), "3C-52-82-1A-20-07", dhcp=True)
X01_PORTS = (_port(9), _port(10, device="PC-07", link=True, speed="1 Gb/s", duplex="full", vlan=99))
X02_TRACERT = tracert_lines(WEB_IP, (ROUTER_IP, None, None, None))
X03_LINES = (
    *win_ping_lines(WEB_IP, (12, 11, 12, 12), ttl=56),
    "",
    *nslookup_lines(WEB_NAME, "192.168.20.6", NS_TIMEOUT),
)
X04_HOST = Host("PC-ACCUEIL", "poste fixe", "192.168.20.45", 28, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-20-45")
X04_FACTS = subnet_facts(X04_HOST.ip, X04_HOST.prefix)
X04_REACHABLE = {name: is_local_for(X04_HOST.ip, X04_HOST.prefix, ip)
                 for name, ip in (("passerelle", ROUTER_IP), ("SRV-01", SERVER_IP), ("NAS-01", NAS_IP),
                                  ("IMP-01", PRINTER_IP), ("AP-01", AP_IP))}
X07_HOST = LAN_BY_NAME["PC-04"]
X07_LINES = (
    "$ ip -brief addr show enp3s0",
    f"enp3s0  UP  {X07_HOST.ip}/{X07_HOST.prefix}",
    "",
    "$ ip route",
    f"{subnet_facts(X07_HOST.ip, X07_HOST.prefix).cidr} dev enp3s0 proto kernel",
    f"    scope link src {X07_HOST.ip}",
    "",
    *ip_neigh_lines("enp3s0", ((ROUTER_IP, LAN_BY_NAME["BOX-01"].mac),)),
    "",
    *resolvectl_lines("enp3s0", (SERVER_IP,), DOMAIN),
)
X08_LINES = (
    *test_netconnection_lines("NAS-01", 445, ping_ok=True, tcp_ok=False),
    "",
    *test_netconnection_lines("SRV-01", 445, ping_ok=True, tcp_ok=True),
)


# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    # --- 8 analyses de relevés ---------------------------------------------------------------
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Une adresse 10.30.0.x sur un poste de bureau",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_LOGS,
        context=(
            f"Dans l'atelier (réseau {LAN_NETWORK}, DHCP sur SRV-01), PC-03 navigue sur Internet "
            f"mais n'ouvre plus le partage {SHARE_UNC} ni l'imprimante, depuis que le prestataire a "
            "réorganisé le switch hier soir. Les autres postes fonctionnent. Tu as relevé la "
            "configuration de PC-03 (document 1) et l'état de quelques ports du switch (document 2). "
            f"Le VLAN {GUEST_VLAN} est celui du réseau invités {GUEST_NETWORK}, servi par la box."
        ),
        instructions=(
            "Interprète l'adresse obtenue par PC-03 : de quel réseau vient-elle ?",
            "Désigne la cause probable en citant le document qui la prouve.",
            "Propose la correction, avec l'autorisation nécessaire, et les tests de validation.",
        ),
        documents=(
            _console("Document 1 — ipconfig /all sur PC-03 (fictif)", *_ipconfig(E01_HOST, dhcp_server="10.30.0.1")),
            _ports_table("Document 2 — ports 6 à 9 du switch SW-01 (relevé fictif)", E01_PORTS),
        ),
        criteria=(
            _c("Interprétation de l'adresse", 1, f"{E01_HOST.ip}/24, passerelle et DHCP 10.30.0.1 : adresse du réseau invités {GUEST_NETWORK}, pas du réseau interne {LAN_NETWORK} ; ce n'est pas une APIPA, un serveur DHCP a bien répondu."),
            _c("Cause prouvée", 1, f"Document 2 : le port 8 (PC-03) est dans le VLAN {GUEST_VLAN} alors que les autres postes sont dans le VLAN 1 ; erreur de la réorganisation d'hier."),
            _c("Correction et validation", 1, "Demander au responsable (ou au prestataire) de remettre le port 8 dans le VLAN 1, consigner l'avant/après ; ipconfig /renew ; adresse 192.168.20.x, ping de la passerelle et de NAS-01, ouverture du partage et impression."),
        ),
        correction=(
            f"PC-03 a reçu {E01_HOST.ip}/24 avec la passerelle 10.30.0.1 et un serveur DHCP 10.30.0.1 : un serveur DHCP a répondu, mais c'est celui du réseau invités ({GUEST_NETWORK}). Internet fonctionne donc (la box route le réseau invités), mais le réseau interne est volontairement isolé : NAS et imprimante sont injoignables.",
            f"Le document 2 donne l'indice décisif : le port 8, celui de PC-03, est dans le VLAN {GUEST_VLAN}, les ports 6, 7 et 9 dans le VLAN 1. On ne suppose pas une erreur de VLAN sans indice : ici, le relevé et la chronologie (réorganisation d'hier) la prouvent.",
            "Correction : faire remettre le port 8 dans le VLAN 1 par la personne autorisée (on ne modifie pas la configuration du switch de production sans accord), noter la configuration avant et après ; puis ipconfig /renew, vérifier une adresse 192.168.20.x, ping de 192.168.20.1 et de NAS-01, ouverture du partage et impression d'une page de test.",
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Des étoiles dans un tracert : panne ou pas ?",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_LOGS,
        context=(
            "Une employée se plaint que « Internet est en panne » car un collègue lui a montré des "
            "étoiles dans le résultat d'un tracert vers le site de test de l'entreprise. Tu "
            "récupères la capture complète (document 1), réalisée depuis PC-01 sur le réseau de "
            f"l'atelier, dont la passerelle est {ROUTER_IP}."
        ),
        instructions=(
            "Explique ce que montre chaque partie du tracert (sauts 1, 2, 3 et 4-5).",
            "Conclus : Internet est-il en panne ? Que faut-il demander à l'employée ?",
        ),
        documents=(_console("Document 1 — tracert depuis PC-01 (fictif)", *E02_TRACERT),),
        criteria=(
            _c("Lecture des sauts", 1, f"Saut 1 = passerelle {ROUTER_IP} (box) ; saut 2 = premier routeur du fournisseur ; saut 3 sans réponse : routeur qui ne répond pas aux sondes (filtrage ICMP), le trafic continue ; sauts 4-5 : la destination {WEB_IP} est atteinte."),
            _c("Conclusion et suite", 1, "Le chemin vers Internet fonctionne : pas de panne ; une ligne d'étoiles au milieu n'est pas un arrêt. Demander le symptôme exact (site, message, heure, lenteur ?) et tester le service visé (navigateur, nom)."),
        ),
        correction=(
            f"Le saut 1 est la passerelle {ROUTER_IP} (la box), le saut 2 le premier routeur du fournisseur. Le saut 3 ne répond pas : certains routeurs ne renvoient pas de message aux sondes de tracert (filtrage ou priorité basse), sans bloquer le trafic qui les traverse.",
            f"Les sauts 4 et 5 répondent, et le dernier est la destination {WEB_IP} : le chemin complet fonctionne. Une ligne d'étoiles n'est une panne que si plus rien ne répond après elle (voir le cas où tout s'arrête après la box).",
            "Il faut donc revenir au symptôme réel : quel site, quel message, depuis quand, lenteur ou erreur ? Puis tester le service lui-même (ouverture du site, résolution du nom).",
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="nslookup répond… sauf pour un nom",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_LOGS,
        context=(
            f"Un comptable écrit que « le DNS est en panne » : son raccourci vers le site du "
            f"fournisseur ({E03_TYPO}, saisi à la main dans ses favoris) affiche une erreur. Les "
            f"autres sites fonctionnent. Tu interroges le DNS interne {SERVER_IP} avec nslookup pour "
            "le nom correct puis pour le nom du raccourci (document 1)."
        ),
        instructions=(
            "Le serveur DNS fonctionne-t-il ? Justifie avec le document.",
            "Donne la cause et la correction, puis la validation.",
        ),
        documents=(_console("Document 1 — deux requêtes nslookup (fictif)", *E03_LINES),),
        criteria=(
            _c("Serveur DNS", 1, f"Oui : {SERVER_IP} répond et résout {WEB_NAME} en {WEB_IP} ; pas de délai dépassé."),
            _c("Cause, correction, validation", 1, f"Le nom {E03_TYPO} (quatre « w ») n'existe pas : « Non-existent domain » est une réponse du serveur. Corriger le favori en {WEB_NAME}, puis ouvrir le site."),
        ),
        correction=(
            f"Le serveur {SERVER_IP} répond : il résout {WEB_NAME} en {WEB_IP}. Un DNS en panne donnerait un délai dépassé pour toutes les requêtes, pas une réponse.",
            f"Pour {E03_TYPO}, la réponse est « Non-existent domain » : le serveur a bien cherché et répond que ce nom n'existe pas. Le favori contient une faute de frappe (quatre « w »). On corrige le favori en {WEB_NAME} et on vérifie l'ouverture du site.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Le journal DHCP du serveur",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_LOGS,
        context=(
            f"Depuis le début de la semaine de formation, des visiteurs se connectent au Wi-Fi "
            f"« {SSID} » avec leur téléphone. Ce matin, un nouveau portable reste en 169.254.x.y. "
            f"Le serveur SRV-01 distribue l'étendue {POOL[0]} à {POOL[1]} avec des baux de "
            f"{LEASE_DAYS} jours. Tu relèves le journal DHCP et le nombre de baux en cours (document 1)."
        ),
        instructions=(
            "Interprète les lignes du journal et le nombre de baux (calcule la taille de l'étendue).",
            "Propose deux corrections possibles, dont une qui évite la récidive, et la validation.",
        ),
        documents=(_console("Document 1 — journal dnsmasq et baux de SRV-01 (fictif)", *E04_LINES),),
        criteria=(
            _c("Interprétation", 1, f"Les DHCPDISCOVER de {mac_linux(E04_MAC)} restent sans offre : « no address available ». L'étendue compte {E04_POOL_SIZE} adresses et {E04_LEASES} baux sont actifs : étendue épuisée (le serveur fonctionne)."),
            _c("Corrections et validation", 1, f"Avec l'accord du responsable : libérer les baux des visiteurs ou agrandir l'étendue (hors adresses fixes) ; éviter la récidive : réseau Wi-Fi invités séparé (VLAN {GUEST_VLAN}) et/ou baux plus courts pour les invités. Valider : bail obtenu par le portable (DHCPACK), ping passerelle et nom."),
        ),
        correction=(
            f"Chaque DHCPDISCOVER du portable ({mac_linux(E04_MAC)}) reçoit la mention « no address available » : le serveur reçoit bien la demande (lien et serveur OK), mais n'a plus d'adresse à proposer. De {POOL[0]} à {POOL[1]}, l'étendue compte {E04_POOL_SIZE} adresses ; {E04_LEASES} baux sont en cours : elle est épuisée par les téléphones des visiteurs, gardés {LEASE_DAYS} jours.",
            "Corrections possibles, avec l'accord du responsable et en notant la configuration initiale : supprimer les baux des appareils visiteurs, ou agrandir l'étendue sans empiéter sur les adresses fixes. Pour éviter la récidive : faire passer les visiteurs sur le Wi-Fi invités (réseau séparé) et/ou raccourcir les baux de ce réseau.",
            "Validation : le journal montre DHCPOFFER puis DHCPACK pour le portable, qui obtient une adresse 192.168.20.x ; ping de la passerelle et ouverture d'un site.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Wi-Fi lent et coupures dans la salle du fond",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-33"),
        kind=KIND_LOGS,
        context=(
            "Dans la salle de réunion du fond, un portable perd régulièrement la connexion et les "
            "téléchargements sont très lents ; près du bureau d'accueil, tout est normal. Le point "
            "d'accès AP-01 émet le même SSID en 2,4 GHz et en 5 GHz. Tu relèves l'état de la carte "
            "Wi-Fi dans la salle (document 1)."
        ),
        instructions=(
            "Relève les valeurs utiles et situe le problème : radio, authentification ou adressage ?",
            "Propose des actions dans l'ordre, de la plus simple à la plus coûteuse, et la validation.",
        ),
        documents=(_console("Document 1 — netsh wlan show interfaces (fictif)", *E05_LINES),),
        criteria=(
            _c("Relevé et diagnostic", 1, f"Connecté et authentifié (WPA2 - Personnel, CCMP) : l'authentification fonctionne ; signal {E05_STATUS.signal_pct} %, {E05_STATUS.band} canal {E05_STATUS.channel}, réception {E05_STATUS.rx_mbps:g} Mb/s : couverture radio insuffisante (distance, murs, interférences), pas un problème d'adresse."),
            _c("Actions et validation", 1, "Vérifier l'emplacement et les obstacles, tester près de l'AP ; choisir un canal moins encombré ; déplacer l'AP ou ajouter un point d'accès (ou répéteur, en sachant qu'il réduit souvent le débit) ; valider en mesurant signal et débit dans la salle et l'absence de coupure."),
        ),
        correction=(
            f"Le portable est connecté au SSID {SSID} et authentifié en WPA2 - Personnel : ni la clé ni le chiffrement ne sont en cause. Le signal n'est que de {E05_STATUS.signal_pct} % et le débit de réception de {E05_STATUS.rx_mbps:g} Mb/s, en {E05_STATUS.band} : le portable est en limite de couverture. C'est un problème radio.",
            "Actions dans l'ordre : comparer près de l'AP (le problème disparaît-il ?), repérer obstacles et sources d'interférences, essayer un autre canal ; si la salle reste mal couverte, déplacer l'AP ou ajouter un point d'accès raccordé au réseau ; un répéteur dépanne mais divise souvent le débit disponible. Le 5 GHz offre plus de débit mais porte moins loin : il n'améliore pas une salle trop éloignée.",
            "Validation : nouveau relevé dans la salle (signal, débit), test de téléchargement et observation sans coupure pendant une réunion.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Un poste Linux sans réseau après « reconfiguration »",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_LOGS,
        context=(
            "PC-04 (Linux) n'a plus de réseau depuis le déménagement de son bureau. Un collègue a "
            "déjà « essayé de remettre l'adresse IP à la main » sans succès, puis a annulé ses "
            "changements. Tu relèves l'état de l'interface et des routes (document 1). Le câble est "
            "branché à une prise murale neuve."
        ),
        instructions=(
            "Que montrent ip link et ip route ? Quelle couche est en cause ?",
            "Pourquoi la reconfiguration IP ne pouvait-elle pas réussir ? Donne les tests suivants dans l'ordre.",
        ),
        documents=(_console("Document 1 — ip link et ip route sur PC-04 (fictif)", *E06_LINES),),
        criteria=(
            _c("Lecture", 1, "NO-CARRIER et state DOWN : la carte est activée mais ne détecte aucun lien ; sans lien, pas d'adresse ni de route : couche physique."),
            _c("Explication et tests", 1, "Modifier l'IP ne crée pas de lien ; tests : câble et fiches, autre cordon, prise murale brassée au switch ? voyant du port, autre prise ou port connu fonctionnel ; puis bail DHCP et ping de la passerelle."),
        ),
        correction=(
            "ip link affiche NO-CARRIER et state DOWN : l'interface enp3s0 est activée (UP dans les options) mais ne voit aucun signal sur le câble. Sans lien, NetworkManager n'obtient pas de bail et ip route est vide. La panne est physique.",
            "Changer l'adresse IP ne pouvait donc rien résoudre : on ne diagnostique pas l'IP tant que le lien est absent. Tests : état et sertissage du cordon, essai avec un cordon connu bon, vérifier que la prise murale neuve est bien brassée sur un port du switch (voyant du port), essayer une autre prise. Une fois le lien présent (LOWER_UP), vérifier le bail et pinger la passerelle.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Un poste lent : la page des ports du switch",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-19"),
        kind=KIND_LOGS,
        context=(
            "Depuis qu'un technicien a « forcé » la carte réseau de PC-02 « pour stabiliser la "
            "connexion », l'utilisatrice trouve les copies vers le NAS très lentes et observe des "
            "micro-coupures. Le switch est en négociation automatique sur tous les ports. Tu "
            "relèves les ports 6 à 8 du switch (document 1)."
        ),
        instructions=(
            "Compare le port 7 aux autres et formule l'hypothèse la plus probable.",
            "Indique le test qui la confirme, la correction et le contrôle après correction.",
        ),
        documents=(_ports_table("Document 1 — ports 6 à 8 du switch SW-01 (relevé fictif)", E07_PORTS),),
        criteria=(
            _c("Hypothèse", 1, "Port 7 (PC-02) en 100 Mb/s half duplex avec 1 843 erreurs, les autres en 1 Gb/s full sans erreur : désaccord de duplex (carte forcée, switch en automatique qui se replie en half duplex) ; autre cause possible : cordon défectueux."),
            _c("Test, correction, contrôle", 1, "Vérifier le réglage vitesse/duplex de la carte (forcé ?) ; remettre la négociation automatique des deux côtés (sinon changer le cordon) ; contrôler 1 Gb/s full, compteur d'erreurs qui n'augmente plus, copie vers le NAS à vitesse normale."),
        ),
        correction=(
            "Le port 7 est le seul en 100 Mb/s half duplex, avec un compteur d'erreurs élevé. Quand un côté est forcé et l'autre en négociation automatique, celui-ci ne peut pas connaître le duplex et se replie en half duplex : les deux côtés ne parlent plus de la même façon, d'où collisions tardives côté half duplex, erreurs CRC côté full duplex, retransmissions et lenteur. La chronologie (carte « forcée ») soutient cette hypothèse ; un cordon défectueux peut aussi produire des erreurs.",
            "Test : lire le réglage « vitesse et duplex » de la carte de PC-02. Correction : remettre la négociation automatique (ou forcer les deux côtés à l'identique, si la politique du réseau l'impose) ; si les erreurs persistent, changer le cordon. Contrôle : port à 1 Gb/s full, compteur d'erreurs stable après plusieurs minutes, copie vers le NAS normale.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="L'imprimante répond une fois sur deux",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_LOGS,
        context=(
            f"L'imprimante IMP-01 ({PRINTER_IP}, adresse fixe ; MAC {normalize_mac(E08_PRINTER.mac)} "
            "sur son étiquette) imprime par intermittence depuis l'installation d'une caméra IP la "
            "semaine dernière. Depuis PC-01, tu lances un ping puis tu affiches la table ARP "
            "(document 1)."
        ),
        instructions=(
            "Interprète le ping et la table ARP.",
            "Donne la cause, la correction et la vérification, et la mesure qui évite la récidive.",
        ),
        documents=(_console("Document 1 — ping et arp -a sur PC-01 (fictif)", *E08_LINES),),
        criteria=(
            _c("Interprétation", 1, f"Ping : 2 réponses sur 4 (50 % de perte) ; arp -a associe {PRINTER_IP} à {normalize_mac(E08_INTRUDER_MAC).lower()}, qui n'est pas la MAC de l'imprimante : un autre appareil (la caméra) utilise la même adresse."),
            _c("Correction et prévention", 1, "Donner à la caméra une adresse libre, fixe hors étendue (ou réservation), avec l'accord du client ; vider le cache ARP (arp -d) ; vérifier que arp -a montre la MAC de l'imprimante et que l'impression est stable ; tenir le plan d'adressage à jour."),
        ),
        correction=(
            f"La moitié des échos se perd et la table ARP associe {PRINTER_IP} à une MAC qui n'est pas celle de l'étiquette de l'imprimante. Deux appareils répondent à la même adresse : selon le moment, les postes envoient leurs données à l'imprimante ou à l'intrus. La chronologie désigne la caméra installée la semaine dernière.",
            "Correction : identifier l'appareil (MAC, interface de la caméra), lui attribuer une adresse fixe libre hors de l'étendue DHCP ou une réservation, avec l'accord du client ; vider le cache ARP des postes (arp -d, droits administrateur) ; contrôler que arp -a montre la MAC de l'imprimante, ping sans perte et impression stable. Prévention : mettre à jour le plan d'adressage et y vérifier chaque nouvelle adresse fixe.",
        ),
    ),
    # --- 5 arbres de décision ou procédures --------------------------------------------------
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Remettre la procédure de diagnostic dans l'ordre",
        question_type="ordering",
        requirement_ids=(*REQ, "AP-C01"),
        kind=KIND_TREE,
        context=(
            "Un stagiaire a noté sur une fiche les six étapes du diagnostic d'un poste qui « n'a "
            "plus Internet », mais dans le désordre. Avant de l'afficher dans l'atelier, tu dois "
            "les remettre dans l'ordre qui permet de situer la panne du plus proche au plus lointain."
        ),
        instructions=("Remets les étapes dans l'ordre de la procédure.",),
        criteria=(
            _c("Ordre", 6, "Physique et liaison → adresse IP et masque → passerelle → IP distante → DNS → service ou application (1 point par étape bien placée)."),
        ),
        correction=(
            "On teste du plus proche au plus lointain : sans lien, aucune adresse ; sans adresse valide, pas de passerelle ; sans passerelle, pas d'Internet ; sans Internet par IP, inutile d'accuser le DNS ; et c'est seulement quand le nom est résolu qu'on examine le service (site, partage, imprimante).",
            "La première étape qui échoue indique la couche à corriger ; les étapes suivantes ne sont pas encore significatives.",
        ),
        ordering=Ordering(
            steps=tuple(f"{LAYER_STEPS[i][0]} : {LAYER_STEPS[i][1]}" for i in E09_SHOWN),
            correct=tuple(E09_SHOWN.index(i) for i in range(len(LAYER_STEPS))),
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="À quelle couche s'arrête le diagnostic ?",
        question_type="classification",
        requirement_ids=REQ,
        kind=KIND_TREE,
        context=(
            "Tu prépares une fiche d'aide pour le support de premier niveau. Pour huit observations "
            "relevées dans d'anciens dossiers de l'atelier, le support doit savoir à quelle couche "
            "chercher en premier. Chaque observation contient déjà le résultat des tests faits."
        ),
        instructions=("Classe chaque observation selon la couche à examiner en premier.",),
        criteria=(
            _c("Classement", 8, "1 DNS ; 2 physique ; 3 service ; 4 adressage/DHCP ; 5 passerelle/accès Internet ; 6 physique ; 7 adressage ; 8 service (1 point par observation)."),
        ),
        correction=(
            "Ping par IP OK et par nom KO : résolution de noms. « Média déconnecté » ou lien dégradé (100 Mb/s au lieu de 1 Gb/s, erreurs CRC) : physique ou liaison. Adresse 169.254 sans passerelle ou conflit d'adresse : adressage ou DHCP.",
            "Passerelle OK mais Internet KO, tracert arrêté après la box : au-delà de la passerelle (liaison WAN, FAI). Serveur qui répond au ping mais port 445 fermé, ou spouleur arrêté : le réseau fonctionne, c'est le service.",
        ),
        classification=Classification(
            categories=E10_CATEGORIES, elements=tuple(o for o, _l in E10_OBSERVATIONS), correct=E10_CORRECT
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Écrire l'arbre de diagnostic d'un portable qui ne se connecte pas au Wi-Fi",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-33", "AP-C01"),
        kind=KIND_TREE,
        context=(
            f"Le responsable de l'atelier veut une procédure écrite pour le cas « un portable ne se "
            f"connecte pas au Wi-Fi {SSID} » (WPA2/WPA3 - Personnel, même SSID en 2,4 et 5 GHz, "
            "adresses distribuées par SRV-01). Elle doit permettre à un collègue de distinguer un "
            "problème radio, un problème d'authentification et un problème d'adresse IP."
        ),
        instructions=(
            "Rédige l'arbre sous forme de questions oui/non, dans l'ordre, avec pour chaque « non » la piste à suivre.",
            "Pour chaque question, indique comment l'observer (outil, écran, commande).",
        ),
        criteria=(
            _c("Ordre radio → authentification → IP", 2, "1 SSID visible ? 2 association et authentification réussies ? 3 adresse du bon réseau reçue ? 4 signal et débit suffisants ? puis reprise de la procédure générale (passerelle, DNS)."),
            _c("Pistes de chaque branche", 2, "SSID invisible : AP éteint ou non alimenté (PoE), Wi-Fi du portable désactivé, hors portée, 5 GHz trop loin ; authentification : clé, profil obsolète, WPA3 non pris en charge ; IP : APIPA, étendue pleine, VLAN du SSID ; signal : placement, interférences, canal, répéteur."),
            _c("Moyens d'observation", 1, "Liste des réseaux, netsh wlan show interfaces / nmcli device wifi, message d'erreur de connexion, ipconfig /all, journal du DHCP, interface de l'AP."),
            _c("Clarté de la procédure", 1, "Questions fermées, une piste par « non », pas de modification de configuration de l'AP sans autorisation."),
        ),
        correction=(
            "1. Le SSID est-il visible dans la liste des réseaux ? Non → radio : AP-01 allumé et alimenté (PoE du port 5), Wi-Fi du portable activé (touche, mode avion), distance, bande 5 GHz hors de portée. Observation : liste des réseaux, nmcli device wifi list, voyants de l'AP.",
            "2. L'association et l'authentification réussissent-elles ? Non → message « impossible de se connecter » : clé incorrecte, profil enregistré avec une ancienne clé (l'oublier et recommencer), carte qui ne gère pas le mode de sécurité (WPA3 seul). Observation : message de Windows, netsh wlan show interfaces (état, authentification).",
            "3. Le portable reçoit-il une adresse du réseau attendu ? Non → APIPA ou mauvais réseau : étendue DHCP pleine, VLAN du SSID, serveur DHCP. Observation : ipconfig /all, journal DHCP.",
            "4. Le signal et le débit sont-ils suffisants et stables ? Non → couverture et interférences : placement, canal, ajout d'un point d'accès ou d'un répéteur. Observation : signal en %, débit de réception.",
            "Si tout est oui, le Wi-Fi n'est pas en cause : reprendre la procédure générale à l'étape passerelle, puis DNS et service.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Changer une option DHCP sur un réseau en production",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C01", "AP-C03"),
        kind=KIND_TREE,
        context=(
            f"Tu as établi que le serveur SRV-01 distribue un DNS périmé (192.168.20.6) à tous les "
            f"postes en DHCP ; le bon DNS est {SERVER_IP}. Il est 10 h, quinze personnes travaillent, "
            "et la modification se fait dans la configuration du service DHCP du serveur, que tu "
            "n'as jamais administré."
        ),
        instructions=(
            "Rédige la procédure d'intervention, de l'autorisation à la clôture.",
            "Explique ce que tu fais pour pouvoir revenir en arrière et pour limiter la gêne.",
        ),
        criteria=(
            _c("Autorisation et préparation", 2, "Accord du responsable du réseau avant toute modification ; consigner l'état initial (copie de la configuration, valeurs relevées) ; prévenir les utilisateurs si une coupure est possible ; choisir le moment."),
            _c("Retour arrière", 1, "Sauvegarde du fichier de configuration et procédure pour le restaurer (et redémarrer le service) si un problème apparaît."),
            _c("Modification et validation", 2, "Une seule modification (option DNS) ; recharger le service ; sur un poste : ipconfig /renew, DNS reçu = 192.168.20.5, nslookup interne et externe ; les autres postes recevront l'option au renouvellement de leur bail (ou ipconfig /renew)."),
            _c("Clôture", 1, "Journal de l'intervention : heure, ancienne et nouvelle valeur, tests, personnes prévenues ; mise à jour de la documentation."),
        ),
        correction=(
            "Avant : obtenir l'accord écrit (ou tracé) du responsable du réseau ; relever et copier la configuration actuelle du DHCP (fichier et valeurs) ; vérifier la nouvelle valeur ; prévenir les utilisateurs si le service doit redémarrer (quelques secondes sans nouveau bail, les postes déjà configurés continuent de travailler).",
            "Retour arrière : garder la copie de la configuration et savoir la restaurer puis relancer le service ; décider à l'avance du critère d'abandon (le service ne redémarre pas, les postes ne reçoivent plus d'adresse).",
            "Pendant : ne changer que l'option DNS, recharger le service, vérifier son état et le journal. Sur un poste de test : ipconfig /renew, DNS reçu 192.168.20.5, nslookup d'un nom interne et d'un nom Internet. Les autres postes prennent la nouvelle option à leur prochain renouvellement de bail ; pour accélérer, ipconfig /renew poste par poste, en prévenant l'utilisateur.",
            "Clôture : noter heure, ancienne et nouvelle valeur, tests et résultats, personnes prévenues ; mettre à jour la documentation du réseau.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Le NAS répond au ping, le partage reste inaccessible",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-25", "AP-27"),
        kind=KIND_TREE,
        context=(
            f"Sur PC-02, l'ouverture de {SHARE_UNC} échoue ce matin alors que « ping {NAS_IP} » "
            "répond normalement. Hier, tout fonctionnait. Tu dois écrire, pour le dossier, le "
            "tableau de diagnostic que tu vas suivre avant d'intervenir sur le NAS, sans encore "
            "connaître le message d'erreur exact."
        ),
        instructions=(
            "Pour au moins quatre causes possibles, donne le test qui les départage, le résultat attendu et l'action.",
            "Indique l'ordre dans lequel tu fais ces tests et pourquoi.",
        ),
        criteria=(
            _c("Causes plausibles", 2, "Nom non résolu (ping par IP seulement), service SMB arrêté ou port 445 filtré, chemin UNC erroné, compte/identifiants refusés (domaine ou groupe de travail, identifiants mémorisés), droits partage/NTFS insuffisants."),
            _c("Tests discriminants", 2, "\\\\192.168.20.10\\Compta (nom vs service) ; Test-NetConnection NAS-01 -Port 445 ; message exact (chemin introuvable / accès refusé) ; essai avec un autre compte autorisé ou depuis un autre poste ; lecture des droits sur le NAS."),
            _c("Ordre justifié et actions", 2, "Du réseau vers les droits : port et nom d'abord (ils concernent tous les utilisateurs), puis chemin, compte et droits ; actions : corriger DNS, relancer le service ou ouvrir le port avec autorisation, corriger le chemin, les identifiants ou les droits avec l'accord du responsable."),
        ),
        correction=(
            "Le ping prouve seulement que le NAS répond au niveau IP. Ordre : 1) nom : ouvrir \\\\192.168.20.10\\Compta — si cela marche, c'est la résolution de NAS-01 (DNS) ; 2) service : Test-NetConnection NAS-01 -Port 445 — TcpTestSucceeded False indique un service SMB arrêté ou un port filtré (pare-feu) ; 3) chemin : orthographe du serveur et du partage (0x80070035 = chemin introuvable) ; 4) compte : « accès refusé » ou demande d'identifiants — compte, domaine ou groupe de travail, identifiants mémorisés dans le Gestionnaire d'identification ; 5) droits : lecture possible mais écriture refusée — combinaison des droits de partage et NTFS, le plus restrictif s'applique.",
            "On va du plus général au plus particulier : un problème de port ou de nom touche tout le monde, un problème de droits un seul compte. Un test depuis un autre poste ou avec un autre compte autorisé départage poste et compte. Les corrections sur le NAS (service, pare-feu, droits) se font avec l'accord du responsable, en notant l'état initial.",
        ),
    ),
    # --- 4 dossiers multi-postes -------------------------------------------------------------
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Contrôler la configuration de quatre postes",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_MULTI,
        context=(
            f"Le réseau de l'atelier est {LAN_NETWORK} : passerelle {ROUTER_IP}, DNS interne "
            f"{SERVER_IP}, étendue DHCP {POOL[0]} à {POOL[1]}, adresses fixes hors étendue. Quatre "
            "postes posent des problèmes différents depuis une intervention d'un ancien prestataire ; "
            "le portable LT-01 fonctionne. Tu as relevé leur configuration (document 1)."
        ),
        instructions=(
            "Pour chaque poste, dis si la configuration est correcte ; sinon, nomme l'erreur et le symptôme qu'elle provoque.",
            "Propose la correction de chaque erreur.",
        ),
        documents=(_table("Document 1 — configurations relevées (fictives)", PLAN_HEADER, *_plan_rows(E14_HOSTS)),),
        criteria=(
            _c("PC-A", 0.5, "Correct (DHCP, adresse de l'étendue, passerelle et DNS du plan)."),
            _c("PC-B", 1, "Passerelle 192.168.20.254 au lieu de 192.168.20.1 : réseau local OK, rien au-delà ; corriger la passerelle."),
            _c("PC-C", 1, f"DNS {ISP_DNS} (DNS du fournisseur) au lieu de {SERVER_IP} : Internet OK mais noms internes ({DOMAIN}) non résolus ; mettre le DNS interne."),
            _c("PC-D", 1.5, "Adresse fixe 192.168.20.150 dans l'étendue DHCP et déjà utilisée par LT-01 : conflit d'adresse, coupures sur les deux machines ; choisir une adresse fixe libre hors étendue (ou passer en DHCP) et corriger le plan."),
        ),
        correction=(
            "PC-A est en DHCP : adresse de l'étendue, passerelle et DNS corrects.",
            *(f"Contrôle : {e}" for e in E14_ERRORS),
            "PC-B sort par une passerelle qui n'existe pas : le réseau local fonctionne, Internet non. PC-C interroge le DNS du fournisseur, qui ne connaît pas les noms internes : Internet fonctionne, srv-01.atelier.lan non. PC-D a une adresse fixe dans l'étendue, déjà attribuée à LT-01 : conflit d'adresse IP, coupures sur les deux machines.",
            "Corrections : passerelle 192.168.20.1 sur PC-B ; DNS 192.168.20.5 sur PC-C ; sur PC-D, une adresse fixe libre hors étendue (par exemple 192.168.20.44, après vérification) ou le DHCP ; puis ping passerelle, nom interne et nom Internet sur chaque poste, et plan d'adressage mis à jour.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Trois utilisateurs, trois refus d'accès au partage",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-25", "AP-27"),
        kind=KIND_MULTI,
        context=(
            f"Le partage {SHARE_UNC} est configuré ainsi sur le NAS : droits de partage « Tous : "
            "Lecture » ; droits du dossier (ACL de type NTFS) « Compta : Modification ». Les trois postes "
            "naviguent sur Internet et répondent au ping du NAS. Les trois utilisateurs signalent "
            "un problème différent (document 1)."
        ),
        instructions=(
            "Pour chaque utilisateur, identifie la cause en t'appuyant sur le message et sur la configuration.",
            "Propose la correction de chacune, en précisant qui doit l'autoriser.",
        ),
        documents=(_table("Document 1 — accès au partage (relevés fictifs)", ("Utilisateur", "Chemin saisi", "Résultat", "Appartenance"), *E15_ROWS),),
        criteria=(
            _c("Mme Lenoir", 0.5, "Chemin erroné (NAS01 sans tiret) : chemin réseau introuvable ; corriger en \\\\NAS-01\\Compta."),
            _c("M. Bah", 0.5, "Pas membre du groupe Compta : refus normal des droits NTFS ; ne rien changer sans décision du responsable (ajout au groupe si justifié)."),
            _c("Mme Roux", 1.5, "Lecture seule : le droit de partage « Lecture » limite l'accès même si NTFS donne « Modification » ; le plus restrictif s'applique ; avec l'accord du responsable, donner au partage un droit suffisant (par exemple Modification pour Compta) et laisser NTFS gérer le détail."),
            _c("Validation", 0.5, "Ouverture, lecture et enregistrement d'un fichier de test par chaque utilisateur concerné."),
        ),
        correction=(
            "Le réseau fonctionne pour les trois (Internet, ping du NAS) : on cherche au niveau du chemin, du compte et des droits.",
            "Mme Lenoir a saisi \\\\NAS01\\Compta : ce serveur n'existe pas (le nom est NAS-01), d'où l'erreur 0x80070035 « chemin réseau introuvable ». Correction : chemin exact, raccourci ou lecteur réseau corrigé.",
            "M. Bah n'est pas membre du groupe Compta : le dossier ne lui donne aucun droit NTFS, le refus est normal. On ne l'ajoute au groupe qu'avec la décision du responsable.",
            "Mme Roux est membre de Compta (NTFS : Modification), mais le partage n'accorde que la Lecture : quand on passe par le réseau, c'est la combinaison la plus restrictive qui s'applique, donc lecture seule. Correction, avec l'accord du responsable : droit de partage suffisant (par exemple Modification ou Contrôle total pour Compta) et droits fins en NTFS. Validation : chaque utilisateur concerné ouvre, lit et enregistre un fichier de test.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Lenteur et noms introuvables : deux pannes à la fois",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-19"),
        kind=KIND_MULTI,
        context=(
            "PC-03 (adresse fixe) cumule deux plaintes : « tout est lent et ça coupe » et « les sites "
            "ne s'ouvrent pas ». Son cordon réseau a été écrasé par une chaise il y a quelques jours ; "
            "le DNS a été saisi à la main il y a longtemps. Tu relèves un ping de la passerelle, un "
            "nslookup (document 1) et les ports du switch (document 2)."
        ),
        instructions=(
            "Identifie les deux pannes et la preuve de chacune.",
            "Explique pourquoi corriger une seule ne suffit pas, puis donne les corrections et la validation.",
        ),
        documents=(
            _console("Document 1 — ping et nslookup sur PC-03 (fictif)", *E16_LINES),
            _ports_table("Document 2 — ports 7 à 9 du switch SW-01 (relevé fictif)", E16_PORTS),
        ),
        criteria=(
            _c("Panne physique", 1, "Port 8 en 100 Mb/s au lieu de 1 Gb/s avec 2 410 erreurs CRC, ping de la passerelle avec 25 % de perte : liaison dégradée (cordon écrasé, paire abîmée)."),
            _c("Panne DNS", 1, f"nslookup interroge 192.168.20.6 et expire : DNS configuré inexistant ; le bon est {SERVER_IP}."),
            _c("Corrections et validation", 1, f"Remplacer le cordon (et contrôler la prise) ; mettre le DNS {SERVER_IP} ; valider : 1 Gb/s full, erreurs stables, ping sans perte, nslookup et ouverture d'un site ; chaque correction seule laisse l'autre symptôme."),
        ),
        correction=(
            "Panne 1 : le port 8 de PC-03 ne se négocie plus qu'en 100 Mb/s (le gigabit a besoin des quatre paires) et accumule les erreurs CRC ; le ping de la passerelle perd un écho sur quatre. Avec le cordon écrasé, la liaison physique est dégradée : c'est la lenteur et les coupures.",
            f"Panne 2 : nslookup interroge 192.168.20.6, qui ne répond pas (délai dépassé) : la résolution de noms échoue, d'où les sites qui ne s'ouvrent pas. Le DNS de l'atelier est {SERVER_IP}.",
            f"Les deux pannes sont indépendantes : un cordon neuf rendra la liaison rapide mais les noms ne seront toujours pas résolus ; corriger le DNS seul laissera la lenteur. Corrections : remplacer le cordon (et vérifier la prise), mettre le DNS {SERVER_IP} (ou repasser en DHCP). Validation : port à 1 Gb/s full, compteur d'erreurs stable, ping sans perte, nslookup {WEB_NAME} OK, site ouvert.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Des adresses 192.168.1.x apparaissent dans l'atelier",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_MULTI,
        context=(
            f"Depuis lundi, certains postes perdent l'accès au NAS et à Internet après un "
            f"redémarrage, d'autres non ; le problème « change de poste » d'un jour à l'autre. Le "
            f"seul serveur DHCP prévu est SRV-01 ({SERVER_IP}). Le port 10 du switch, inutilisé "
            "jusqu'ici, est désormais actif. Tu relèves la configuration des quatre postes "
            "(document 1) et l'état du port 10 (document 2)."
        ),
        instructions=(
            "Explique ce qui se passe et pourquoi la panne semble intermittente.",
            "Donne la correction, les postes à traiter, et une mesure de prévention.",
        ),
        documents=(
            _table("Document 1 — configurations relevées (fictives)", ("Poste", "Adresse", "Passerelle", "DNS", "Serveur DHCP"), *E17_HOSTS),
            _ports_table("Document 2 — port 10 du switch SW-01 (relevé fictif)", (E17_PORT10,)),
        ),
        criteria=(
            _c("Diagnostic", 1.5, "Un second serveur DHCP (192.168.1.1, probablement une box ou un routeur personnel branché sur le port 10) répond aux demandes : les postes qui renouvellent leur bail obtiennent au hasard l'une ou l'autre offre, d'où l'intermittence."),
            _c("Correction", 1, f"Retirer l'appareil du port 10 avec l'accord du responsable (et identifier son propriétaire) ; ipconfig /release puis /renew sur {', '.join(E17_AFFECTED)} ; vérifier serveur DHCP {SERVER_IP} et accès NAS/Internet."),
            _c("Prévention", 0.5, "Désactiver les ports inutilisés, règle d'usage du réseau ; en complément, protection DHCP du switch (DHCP snooping) si le matériel le permet."),
        ),
        correction=(
            f"PC-02 et PC-03 ont une adresse 192.168.1.x donnée par un serveur DHCP 192.168.1.1, qui n'est pas SRV-01. Un second serveur DHCP est donc présent : très probablement un routeur ou une box personnelle branchée sur le port 10, actif depuis peu et dont la MAC ({normalize_mac(E17_ROGUE_MAC)}) n'appartient à aucun équipement de l'atelier.",
            "Le premier serveur qui répond à un DHCPDISCOVER l'emporte : selon le moment du redémarrage, un poste reçoit l'adresse de SRV-01 (tout fonctionne) ou celle de l'intrus (ni NAS ni Internet de l'atelier). C'est pourquoi la panne semble changer de poste.",
            f"Correction : avec l'accord du responsable, débrancher l'appareil du port 10 et en identifier le propriétaire ; sur les postes touchés ({', '.join(E17_AFFECTED)}), ipconfig /release puis /renew ; vérifier serveur DHCP {SERVER_IP}, ping de la passerelle et du NAS. Prévention : désactiver les ports inutilisés, rappeler la règle ; si le switch le permet, protection DHCP (complément).",
        ),
    ),
    # --- 3 rapports d'intervention -----------------------------------------------------------
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Rédiger le rapport d'une intervention réussie",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Notes prises pendant l'intervention, le 26/10 de 9 h 10 à 9 h 55, chez le client « "
            "Atelier Durant » : plainte de M. Bah « pas d'Internet sur PC-02 » ; autres postes OK ; "
            "voyant allumé ; ipconfig : 192.168.20.42/24, passerelle 192.168.20.254, DNS 192.168.20.5 "
            "(fixe) ; ping 192.168.20.5 OK ; ping 192.168.20.254 échoue ; ping 192.168.20.1 OK ; "
            "accord de M. Durant ; passerelle corrigée en 192.168.20.1 ; ping 198.51.100.20 OK ; "
            "site ouvert ; M. Bah a vérifié sa messagerie."
        ),
        instructions=(
            "Rédige le rapport d'intervention professionnel à partir de ces notes.",
            "Ajoute une recommandation de prévention.",
        ),
        criteria=(
            _c("Contexte et symptôme", 1, "Client, date et horaire, demandeur, poste, symptôme exact, périmètre (un seul poste, autres OK)."),
            _c("Tests et résultats", 2, "Relevé de configuration, ping serveur OK, ping de la passerelle configurée KO, ping du routeur réel OK : chaque test avec son résultat."),
            _c("Cause et correction", 1, "Passerelle erronée 192.168.20.254 ; remplacée par 192.168.20.1 avec l'accord du responsable ; ancienne valeur notée."),
            _c("Validation et prévention", 2, "Ping Internet, site, messagerie vérifiée par l'utilisateur ; recommandation : passer le poste en DHCP ou mettre à jour le plan d'adressage, vérifier les autres postes en adresse fixe."),
        ),
        correction=(
            "Exemple de rapport : « Client : Atelier Durant. Date : 26/10, 9 h 10 – 9 h 55. Demandeur : M. Bah. Poste : PC-02 (adresse fixe). Symptôme : pas d'accès à Internet ; les autres postes fonctionnent.",
            "Constats et tests : lien présent (voyant allumé). Configuration : 192.168.20.42/24, passerelle 192.168.20.254, DNS 192.168.20.5. ping 192.168.20.5 (serveur) : OK → réseau local fonctionnel. ping 192.168.20.254 (passerelle configurée) : échec. ping 192.168.20.1 (routeur de l'atelier) : OK.",
            "Cause : passerelle erronée (192.168.20.254, adresse sans équipement). Correction, avec l'accord de M. Durant : passerelle 192.168.20.1 (ancienne valeur notée ci-dessus).",
            "Validation : ping 198.51.100.20 OK, ouverture d'un site, messagerie vérifiée par M. Bah. Recommandation : passer PC-02 en DHCP ou mettre à jour le plan d'adressage, et contrôler la passerelle des autres postes en adresse fixe. »",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Rapport d'une panne intermittente non reproduite",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Mme Roux signale des coupures Wi-Fi « deux ou trois fois par jour » sur son portable. "
            "Pendant ton passage (1 h), aucune coupure ; signal 64 %, 5 GHz, canal 36, bail DHCP "
            "valide, ping de la passerelle sans perte sur 200 échos ; le journal Windows montre deux "
            "déconnexions hier à 11 h 02 et 15 h 47 ; le pilote Wi-Fi date de 2021 ; un four à "
            "micro-ondes se trouve dans la pièce voisine."
        ),
        instructions=(
            "Rédige le rapport en distinguant ce qui est établi, ce qui est supposé et ce qui reste à faire.",
            "Propose un plan de suivi permettant de confirmer la cause.",
        ),
        criteria=(
            _c("Faits établis", 1.5, "Pas de coupure pendant l'intervention ; valeurs relevées (signal, bande, canal, bail, ping) ; deux déconnexions datées dans le journal."),
            _c("Hypothèses non confirmées", 1.5, "Pilote ancien ; interférences (micro-ondes sur 2,4 GHz, moins probable en 5 GHz) ; itinérance ou mise en veille de la carte ; présentées comme hypothèses, cause non déterminée."),
            _c("Plan de suivi", 2, "Noter l'heure exacte des coupures ; comparer avec le journal et l'usage du micro-ondes ; mettre à jour le pilote (avec accord, point de restauration) ; vérifier la gestion d'énergie de la carte ; nouveau contrôle à date fixée."),
            _c("Honnêteté de la conclusion", 1, "Le rapport ne prétend pas avoir réparé : intervention en cours, cause à confirmer, client informé."),
        ),
        correction=(
            "Faits établis : aucune coupure pendant une heure d'observation ; signal 64 %, 5 GHz, canal 36, bail DHCP valide, 200 échos vers la passerelle sans perte ; journal : déconnexions hier à 11 h 02 et 15 h 47.",
            "Hypothèses, non confirmées : pilote Wi-Fi ancien (2021) ; mise en veille de la carte par la gestion d'énergie ; interférences du micro-ondes (surtout en 2,4 GHz : à vérifier si le portable bascule de bande) ; changement de point d'accès.",
            "Conclusion honnête : cause non déterminée, aucune réparation affirmée. Plan de suivi : Mme Roux note l'heure de chaque coupure et ce qu'elle faisait ; comparaison avec le journal et l'usage du micro-ondes ; avec son accord, mise à jour du pilote après un point de restauration ; contrôle de la gestion d'énergie de la carte ; nouveau passage à une date convenue.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Corriger un rapport bâclé",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Voici le rapport laissé par un collègue après une panne générale : « Internet marchait "
            "pas. J'ai redémarré la box et le switch et j'ai remis les postes en DHCP. Ça remarche. "
            "Le problème venait sûrement de la box. » Le responsable de l'atelier te demande ce qui "
            "manque et une version réécrite."
        ),
        instructions=(
            "Relève au moins cinq défauts de ce rapport.",
            "Réécris-le en indiquant entre crochets les informations à recueillir auprès du collègue.",
        ),
        criteria=(
            _c("Défauts relevés", 3, "Pas de date, client, demandeur ni périmètre ; aucun test ni valeur avant l'action ; plusieurs changements en même temps (cause impossible à établir) ; pas d'autorisation ni d'état initial (postes en adresse fixe passés en DHCP) ; cause affirmée sans preuve ; pas de validation détaillée ni de recommandation."),
            _c("Réécriture structurée", 3, "Contexte, symptômes et périmètre, constats et tests avec résultats, actions avec accord, cause (non confirmée) ; validation ; impacts (adresses fixes modifiées à vérifier : NAS, imprimante) ; recommandations ; informations manquantes signalées entre crochets."),
        ),
        correction=(
            "Défauts : ni date, ni client, ni demandeur, ni périmètre (tous les postes ? Wi-Fi ?) ; aucun relevé avant d'agir (ping passerelle, IP distante, état WAN de la box) ; trois changements faits en même temps, donc impossible de savoir lequel a réglé le problème ; passage des postes en DHCP sans autorisation ni relevé de leur configuration initiale (risque pour les équipements en adresse fixe) ; cause affirmée (« sûrement la box ») sans preuve ; validation réduite à « ça remarche » ; aucune recommandation.",
            "Réécriture : « Date [ ], client [ ], demandeur [ ]. Symptôme : plus d'accès Internet sur [tous les postes / lesquels ?] depuis [heure]. Constats avant intervention : [ping passerelle, ping IP distante, état WAN de la box] — non relevés. Actions : redémarrage de la box et du switch [heure, accord de ?] ; passage en DHCP des postes [lesquels, configuration initiale ?]. Cause : non déterminée (plusieurs actions simultanées ; panne de la box possible mais non prouvée). Validation : [tests réalisés]. Impacts à vérifier : équipements en adresse fixe (NAS, imprimante, AP). Recommandations : en cas de récidive, relever l'état WAN de la box avant tout redémarrage ; une action à la fois ; documenter les adresses fixes. »",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Un poste raccordé sur le dernier port libre",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_SCENARIO,
        context=(
            "Un nouveau poste, PC-07, a été raccordé ce matin sur le seul port libre du switch (port "
            "10). Il reste en adresse 169.254.x.y alors que les autres postes de l'atelier "
            "fonctionnent. Par mesure de sécurité, le prestataire place les ports inutilisés dans "
            "un VLAN « parking » (VLAN 99) sans serveur DHCP. Documents : configuration de PC-07 "
            "(document 1), ports 9 et 10 du switch (document 2)."
        ),
        instructions=(
            "Interprète la configuration de PC-07 et la cause, preuve à l'appui.",
            "Donne la correction (avec l'autorisation nécessaire) et sa validation.",
        ),
        documents=(
            _console("Document 1 — ipconfig /all sur PC-07 (fictif)", *_ipconfig(X01_HOST, dhcp_server=None, apipa=True)),
            _ports_table("Document 2 — ports 9 et 10 du switch SW-01 (relevé fictif)", X01_PORTS),
        ),
        criteria=(
            _c("Interprétation et cause", 1, f"{X01_HOST.ip}/16, aucune passerelle : APIPA, aucun bail reçu alors que le lien est actif ; le port 10 est dans le VLAN 99 (parking, sans DHCP), le port 9 dans le VLAN 1 ; le serveur DHCP n'est pas en cause."),
            _c("Correction et validation", 1, "Faire placer le port 10 dans le VLAN 1 par la personne autorisée (ou utiliser un port prévu), état initial noté ; ipconfig /renew ; adresse 192.168.20.x, ping de la passerelle, nom résolu."),
        ),
        correction=(
            f"PC-07 a l'adresse {X01_HOST.ip} et le masque {X01_HOST.mask}, sans passerelle : c'est une adresse APIPA, le poste n'a reçu aucune réponse DHCP. Le lien est pourtant actif (port 10 en 1 Gb/s full). Le port 10 est dans le VLAN 99, réservé aux ports inutilisés et sans DHCP, tandis que les postes sont dans le VLAN 1 : le poste est isolé du serveur DHCP.",
            "Correction : faire placer le port 10 dans le VLAN 1 par la personne autorisée (ou brancher le poste sur un port prévu pour les postes), en notant l'état initial ; puis ipconfig /renew. Validation : adresse 192.168.20.x, passerelle 192.168.20.1, ping de la passerelle et nslookup d'un nom.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Plus d'Internet pour personne",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_SCENARIO,
        context=(
            "À 8 h 30, aucun poste de l'atelier n'accède à Internet ; le partage du NAS et "
            "l'imprimante fonctionnent. La box a été réinitialisée hier soir par un collègue après "
            "une coupure de courant. Tu as relevé un tracert depuis PC-01 (document 1) et la page "
            "d'état de la box (document 2)."
        ),
        instructions=(
            "Situe la panne en t'appuyant sur les deux documents.",
            "Propose l'action à mener et sa validation.",
        ),
        documents=(
            _console("Document 1 — tracert depuis PC-01 (fictif)", *X02_TRACERT),
            _table("Document 2 — page d'état de la box (fictive)", ("Élément", "État"),
                   ("Réseau local", "actif, 192.168.20.1/24"), ("Synchronisation de la ligne", "établie"),
                   ("Connexion Internet (PPP)", "échec d'authentification"), ("Adresse publique", "—")),
        ),
        criteria=(
            _c("Localisation", 1, "Le saut 1 (box) répond, plus rien ensuite ; réseau local OK ; la ligne est synchronisée mais la connexion PPP échoue à l'authentification : identifiants de connexion du fournisseur perdus par la réinitialisation."),
            _c("Action et validation", 1, "Avec l'accord du client, ressaisir les identifiants fournis par le FAI (document du contrat) ou contacter le FAI ; valider : adresse publique attribuée, tracert jusqu'à la destination, site ouvert sur deux postes."),
        ),
        correction=(
            f"Le tracert atteint la box ({ROUTER_IP}) puis plus rien : le réseau local et la passerelle fonctionnent (NAS et imprimante aussi), l'arrêt est après la box. La page d'état précise : la ligne est synchronisée (le support physique fonctionne) mais la connexion PPP échoue à l'authentification et aucune adresse publique n'est attribuée.",
            "La réinitialisation d'hier a effacé les identifiants de connexion du fournisseur. Action, avec l'accord du client : ressaisir l'identifiant et le mot de passe figurant dans les documents du contrat, sinon appeler le FAI. Validation : adresse publique affichée, tracert qui atteint la destination, site ouvert depuis deux postes.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Le ping par adresse passe, les sites ne s'ouvrent pas",
        question_type="document_analysis",
        requirement_ids=REQ,
        kind=KIND_SCENARIO,
        context=(
            "Sur PC-05 (adresse fixe), le navigateur affiche « Impossible de trouver l'adresse du "
            "serveur » pour tous les sites ; les postes en DHCP fonctionnent. Le DNS de l'atelier "
            f"est {SERVER_IP}. Tu relèves un ping vers une adresse Internet et un nslookup "
            "(document 1)."
        ),
        instructions=(
            "Interprète les deux relevés et donne la cause.",
            "Donne la correction et la validation.",
        ),
        documents=(_console("Document 1 — ping et nslookup sur PC-05 (fictif)", *X03_LINES),),
        criteria=(
            _c("Interprétation", 1, f"ping {WEB_IP} : 4 réponses, Internet accessible par adresse ; nslookup interroge 192.168.20.6 et expire : DNS configuré injoignable ou inexistant ; ce n'est pas une panne d'Internet."),
            _c("Correction et validation", 1, f"DNS {SERVER_IP} (ou DHCP), ipconfig /flushdns ; nslookup {WEB_NAME} répond, site ouvert."),
        ),
        correction=(
            f"Le ping de {WEB_IP} reçoit 4 réponses : la carte, la passerelle et l'accès à Internet fonctionnent. nslookup interroge le serveur 192.168.20.6 et n'obtient aucune réponse : le DNS configuré à la main n'existe pas ou plus. Seule la résolution de noms échoue.",
            f"Correction : DNS préféré {SERVER_IP} (ou retour au DHCP), puis ipconfig /flushdns. Validation : nslookup {WEB_NAME} répond par {SERVER_IP}, le site s'ouvre.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Le poste d'accueil ne voit plus rien",
        question_type="short_answer",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_SCENARIO,
        context=(
            f"Le poste d'accueil a été configuré à la main : adresse {X04_HOST.ip}, masque "
            f"{X04_HOST.mask}, passerelle {X04_HOST.gateway}, DNS {SERVER_IP}. Windows a affiché un "
            "avertissement à l'enregistrement, que l'utilisateur a ignoré. Depuis, ni Internet, ni "
            f"le NAS ({NAS_IP}), ni l'imprimante ({PRINTER_IP}) ne répondent. Le réseau de l'atelier "
            f"est {LAN_NETWORK}."
        ),
        instructions=(
            "Calcule le réseau du poste avec ce masque et dis quels équipements lui paraissent locaux.",
            "Explique l'avertissement de Windows et donne la correction.",
        ),
        criteria=(
            _c("Calcul", 1, f"/{X04_FACTS.prefix} : réseau {X04_FACTS.network}, diffusion {X04_FACTS.broadcast}, hôtes {X04_FACTS.host_range} ; passerelle, SRV-01, NAS, imprimante et AP hors de ce réseau."),
            _c("Explication et correction", 1, "Avertissement : la passerelle n'est pas dans le sous-réseau défini par l'adresse et le masque ; elle est donc injoignable ; mettre le masque 255.255.255.0 (/24) puis tester passerelle, NAS, imprimante et un site."),
        ),
        correction=(
            f"Masque {X04_HOST.mask} = /{X04_FACTS.prefix} : blocs de 16 dans le dernier octet ; 45 est entre 32 et 47 : réseau {X04_FACTS.network}, diffusion {X04_FACTS.broadcast}, hôtes {X04_FACTS.host_range}. La passerelle ({ROUTER_IP}), SRV-01, le NAS, l'imprimante et l'AP sont tous hors de ce réseau : le poste croit devoir passer par la passerelle pour les joindre, mais la passerelle elle-même n'est pas joignable directement.",
            "C'est l'objet de l'avertissement de Windows (passerelle hors du sous-réseau défini par l'adresse et le masque). Correction : masque 255.255.255.0, comme le reste du réseau. Validation : ping de la passerelle, du NAS, impression et ouverture d'un site.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Un ancien portable refuse le nouveau Wi-Fi",
        question_type="short_answer",
        requirement_ids=(*REQ, "AP-33"),
        kind=KIND_SCENARIO,
        context=(
            f"Après le remplacement du point d'accès, le SSID {SSID} est configuré en « WPA3 - "
            "Personnel uniquement ». Les téléphones et portables récents se connectent ; un "
            "portable de 2015, dont la carte et son pilote ne prennent en charge que WPA2, voit "
            "le réseau mais échoue à chaque connexion, même avec la bonne clé vérifiée deux fois."
        ),
        instructions=(
            "Situe le problème (radio, authentification ou adressage) et justifie.",
            "Propose deux solutions, avec leurs avantages et inconvénients.",
        ),
        criteria=(
            _c("Diagnostic", 1, "Le SSID est visible (radio OK) ; échec à la connexion avec la bonne clé : authentification ; la carte ne gère pas WPA3 (SAE) ; ce n'est pas un problème d'adresse IP."),
            _c("Solutions", 1, "Mode de transition WPA2/WPA3 sur l'AP (compatibilité, mais sécurité réduite pour les clients WPA2) ; ou carte/adaptateur Wi-Fi compatible WPA3, ou pilote récent s'il ajoute WPA3 (coût, mais sécurité maintenue) ; décision du responsable."),
        ),
        correction=(
            "Le portable voit le SSID : la radio fonctionne. Il échoue à la connexion alors que la clé est bonne : c'est l'étape d'authentification. En « WPA3 uniquement », l'AP impose l'échange SAE, que la carte (WPA2 seulement) ne sait pas faire. L'adressage n'est pas atteint.",
            "Solution 1 : mode de transition WPA2/WPA3 sur l'AP — tous les appareils se connectent, mais les clients WPA2 restent sur la sécurité WPA2. Solution 2 : pilote plus récent s'il ajoute WPA3, sinon adaptateur Wi-Fi compatible WPA3 — petit coût, sécurité maintenue. Le choix revient au responsable.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="L'imprimante répond, mais n'imprime plus",
        question_type="short_answer",
        requirement_ids=(*REQ, "AP-25"),
        kind=KIND_SCENARIO,
        context=(
            f"Hier, l'imprimante IMP-01 a été passée en adresse fixe {PRINTER_IP} (elle avait "
            "auparavant 192.168.20.21, donnée par le DHCP). Depuis, PC-02 n'imprime plus : les "
            "documents restent « en erreur » dans la file. ping 192.168.20.20 répond ; ping "
            "192.168.20.21 : délai dépassé. Dans les propriétés de l'imprimante sur PC-02, le port "
            "utilisé est « IP_192.168.20.21 »."
        ),
        instructions=(
            "Explique pourquoi le ping réussi ne suffit pas à conclure que l'impression doit fonctionner.",
            "Donne la cause, la correction sur PC-02 et la vérification sur les autres postes.",
        ),
        criteria=(
            _c("Raisonnement", 1, "Le ping teste l'adresse 192.168.20.20 ; la file de PC-02 envoie les travaux vers 192.168.20.21 (port de l'imprimante), qui ne répond plus : c'est la configuration de l'impression, pas le réseau."),
            _c("Correction et vérification", 1, "Modifier le port TCP/IP de l'imprimante sur PC-02 vers 192.168.20.20 (ou réinstaller la file), relancer les travaux en erreur, page de test ; vérifier les autres postes installés avant le changement d'adresse."),
        ),
        correction=(
            f"Le ping prouve que l'imprimante répond à {PRINTER_IP}. Mais la file d'impression de PC-02 envoie ses travaux au port IP_192.168.20.21, l'ancienne adresse DHCP, qui ne répond plus : le réseau fonctionne, c'est la configuration de l'impression qui est périmée.",
            "Correction : dans les propriétés de l'imprimante sur PC-02, port TCP/IP standard vers 192.168.20.20 (ou suppression et réinstallation de la file), relancer ou supprimer les travaux en erreur avec l'accord de l'utilisateur, imprimer une page de test. Vérifier tous les postes dont la file a été créée avant le changement d'adresse.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Un poste Linux qui ne sort pas du réseau local",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-30"),
        kind=KIND_SCENARIO,
        context=(
            "Sur PC-04 (Linux, NetworkManager), le NAS et l'imprimante fonctionnent mais aucun "
            "site ne s'ouvre et « ping 198.51.100.20 » répond « Network is unreachable ». Un "
            "stagiaire a modifié la connexion réseau la veille pour « tester une adresse fixe ». "
            "Tu relèves l'adresse, les routes, les voisins et le DNS (document 1)."
        ),
        instructions=(
            "Interprète chaque partie du relevé et donne la cause.",
            "Propose un test immédiat puis la correction persistante, et la validation.",
        ),
        documents=(_console("Document 1 — ip addr, ip route, ip neigh, resolvectl sur PC-04 (fictif)", *X07_LINES),),
        criteria=(
            _c("Interprétation", 1, f"Adresse {X07_HOST.ip}/24 correcte, la box répond (ip neigh REACHABLE), DNS {SERVER_IP} correct ; ip route n'a que la route locale, pas de route par défaut : « Network is unreachable » ; passerelle absente de la connexion."),
            _c("Test et correction", 1, f"Test temporaire : sudo ip route add default via {ROUTER_IP} ; correction persistante dans la connexion NetworkManager (nmcli connection modify … ipv4.gateway {ROUTER_IP}, ou retour en DHCP), selon la distribution ; validation : ping {WEB_IP}, nom, site."),
        ),
        correction=(
            f"ip addr : {X07_HOST.ip}/24, interface active. ip neigh : la box {ROUTER_IP} est joignable. resolvectl : DNS {SERVER_IP}, suffixe {DOMAIN}, corrects. ip route : seulement la route du réseau local, aucune ligne « default via » : le système ne sait pas où envoyer ce qui sort du réseau, d'où « Network is unreachable ». La connexion modifiée hier n'a plus de passerelle.",
            f"Test immédiat (temporaire, perdu au redémarrage) : sudo ip route add default via {ROUTER_IP}, puis ping {WEB_IP}. Correction persistante dans la configuration de NetworkManager — par exemple nmcli connection modify <connexion> ipv4.gateway {ROUTER_IP} puis nmcli connection up <connexion>, ou retour en DHCP — l'outil dépend de la distribution. Validation : route par défaut présente, ping d'une adresse Internet, nom résolu, site ouvert.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Le NAS répond, mais pas son partage",
        question_type="document_analysis",
        requirement_ids=(*REQ, "AP-25"),
        kind=KIND_SCENARIO,
        context=(
            f"Depuis la mise à jour du NAS hier soir, plus personne n'ouvre {SHARE_UNC} : "
            "« Windows ne peut pas accéder à \\\\NAS-01\\Compta ». Les partages de SRV-01 "
            "fonctionnent. Tu lances Test-NetConnection vers les deux serveurs depuis PC-01 "
            "(document 1)."
        ),
        instructions=(
            "Interprète les deux tests et situe la panne.",
            "Donne les vérifications à faire sur le NAS et la validation.",
        ),
        documents=(_console("Document 1 — Test-NetConnection depuis PC-01 (fictif)", *X08_LINES),),
        criteria=(
            _c("Interprétation", 1, "NAS-01 : ping OK mais port 445 (SMB) fermé ; SRV-01 : port 445 ouvert ; le poste et le réseau fonctionnent ; le service de partage du NAS est arrêté ou filtré depuis la mise à jour (tous les utilisateurs touchés)."),
            _c("Vérifications et validation", 1, "Interface du NAS, avec l'accord du responsable : service SMB/partage Windows activé, pare-feu du NAS, version SMB autorisée après mise à jour ; validation : TcpTestSucceeded True, ouverture du partage par un utilisateur."),
        ),
        correction=(
            "Vers NAS-01, le ping réussit (PingSucceeded True) mais la connexion au port TCP 445, celui du partage de fichiers Windows (SMB), échoue. Vers SRV-01, le même test réussit : le poste et le réseau fonctionnent. Le problème est le service de partage du NAS, arrêté ou filtré depuis la mise à jour — ce qui explique que tous les utilisateurs soient touchés.",
            "Vérifications dans l'interface du NAS, avec l'accord du responsable : service de partage Windows (SMB) activé, pare-feu du NAS, versions de SMB autorisées après la mise à jour, journal du NAS. Validation : Test-NetConnection NAS-01 -Port 445 renvoie TcpTestSucceeded True et un utilisateur ouvre le partage.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Les propositions d'un collègue pressé",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C03"),
        kind=KIND_SCENARIO,
        context=(
            "Chez un client où Internet est coupé depuis une heure, un collègue propose : « On "
            "remet la box en configuration d'usine, on lance un scan de tous les ports de toutes "
            "les machines pour voir ce qui cloche, et je copie les journaux du serveur sur ma clé "
            "USB perso pour les analyser chez moi. » Le responsable du client est joignable par "
            "téléphone."
        ),
        instructions=(
            "Explique pour chaque proposition le risque qu'elle fait courir.",
            "Décris comment intervenir de façon sûre à la place.",
        ),
        criteria=(
            _c("Risques", 1, "Réinitialisation : perte de la configuration (identifiants FAI, redirections, Wi-Fi), coupure plus longue, sans retour arrière ; scan non autorisé : intrusif, peut perturber des équipements, interdit sans accord ; journaux sur clé personnelle : données confidentielles hors du client."),
            _c("Intervention sûre", 1, "Appeler le responsable et obtenir l'accord avant toute action ; relever l'état initial (état WAN de la box, sauvegarde de sa configuration) ; tests non destructifs (ping, tracert, page d'état) ; une action à la fois avec retour arrière ; journaux consultés sur place ou transmis par un moyen autorisé."),
        ),
        correction=(
            "Remettre la box en configuration d'usine efface toute sa configuration (identifiants du fournisseur, Wi-Fi, redirections, adresses réservées) : la panne peut s'aggraver et il n'y a plus de retour arrière. Un scan de ports de tout le réseau est une action intrusive : sans autorisation explicite, elle n'est pas permise et peut perturber des équipements. Copier les journaux sur une clé personnelle fait sortir des données confidentielles du client.",
            "À la place : téléphoner au responsable, exposer le diagnostic et obtenir son accord avant toute modification ; relever l'état initial (page d'état WAN de la box, sauvegarde de sa configuration) ; commencer par des tests non destructifs (ping de la passerelle, d'une IP distante, tracert, état de la ligne) ; agir une chose à la fois, avec un retour arrière prévu ; consulter les journaux sur place ou les transmettre par un moyen autorisé par le client.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Le compte rendu d'une étendue DHCP épuisée",
        question_type="long_answer",
        requirement_ids=(*REQ, "AP-C01"),
        kind=KIND_SCENARIO,
        context=(
            f"Le 27/10 à 9 h, trois portables de stagiaires restaient en 169.254.x.y. Le journal de "
            f"SRV-01 montrait « no address available » ; {pool_size()} baux étaient actifs pour une "
            f"étendue de {pool_size()} adresses, dont 41 au nom de téléphones de visiteurs. Avec "
            "l'accord de M. Durant, tu as supprimé les baux des visiteurs et activé le Wi-Fi invités "
            f"(VLAN {GUEST_VLAN}) pour eux ; les trois portables ont obtenu une adresse et ouvert un site."
        ),
        instructions=("Rédige le compte rendu de cette intervention, avec une recommandation.",),
        criteria=(
            _c("Contexte, symptômes, preuves", 1, f"Date, demandeur, postes touchés, adresses APIPA ; journal « no address available », {pool_size()} baux actifs pour {pool_size()} adresses (étendue épuisée), dont 41 visiteurs."),
            _c("Actions, validation, recommandation", 1, "Accord de M. Durant ; baux visiteurs supprimés, Wi-Fi invités activé ; validation : adresses 192.168.20.x, site ouvert ; recommandation : visiteurs toujours sur le réseau invités, surveiller l'occupation de l'étendue, baux plus courts pour les invités."),
        ),
        correction=(
            f"« 27/10, 9 h. Demande : trois portables de stagiaires sans réseau (adresses 169.254.x.y). Constat : journal DHCP de SRV-01 « no address available » ; {pool_size()} baux actifs pour une étendue de {pool_size()} adresses — étendue épuisée, dont 41 baux de téléphones de visiteurs.",
            f"Actions, avec l'accord de M. Durant : suppression des baux des visiteurs ; activation du Wi-Fi invités (VLAN {GUEST_VLAN}) pour les visiteurs. Validation : les trois portables ont obtenu une adresse 192.168.20.x et ouvert un site. Recommandation : ne jamais donner la clé du Wi-Fi interne aux visiteurs, surveiller l'occupation de l'étendue, prévoir des baux courts sur le réseau invités. »",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
        ):
            errors.append(f"{item.key} : classification incohérente.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
        if not set(REQ) <= set(item.requirement_ids):
            errors.append(f"{item.key} : AP-32 et AP-37 doivent être cités.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors


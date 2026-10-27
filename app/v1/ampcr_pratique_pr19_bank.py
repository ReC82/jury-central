"""PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements » — exercices corrigés et
mini-examen (ticket #220).

Même organisation que PR18 (`app.v1.ampcr_pratique_pr18_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (chemin d'un paquet, diagnostic par couche,
  encapsulation), classements (topologies, protocole / service / équipement, couche des
  protocoles, rôle des équipements, couche d'une panne), **six schémas à compléter**
  (topologies, OSI/TCP-IP, encapsulation, adresses des trames, domaines, trame Ethernet, servis
  en SVG), **choix d'équipement et de topologie** (besoins d'une PME, hub à remplacer, deux
  réseaux IP, liaisons entre agences), NetBEUI, ports et pare-feu ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, adresses et appareils sont **fictifs** ; tous les nombres des énoncés, barèmes
et corrigés viennent des fonctions de `app.v1.ampcr_pratique_pr19_figures` (mêmes données que
les schémas).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr19_figures import (
    ARP_LINES,
    BOX_LAN,
    BOX_WAN,
    BROADCAST_MAC,
    DEV_AP,
    DEV_HUB,
    DEV_MODEM,
    DEV_REPEATER,
    DEV_ROUTER,
    DEV_SWITCH,
    DIAG_STEPS,
    DOMAINS_BLANK_LAN,
    ENCAP_BLANK,
    ETH_FCS,
    ETH_HEADER,
    ETH_MIN_FRAME,
    ETH_MIN_PAYLOAD,
    FAULT_LAYERS,
    IPV4_HEADER,
    ISP_ROUTER,
    KIND_DEVICE,
    KIND_PROTOCOL,
    KIND_SERVICE,
    L2,
    L3,
    L4,
    L7,
    N_HUB,
    N_PC,
    N_ROUTER,
    N_SWITCH,
    OSI_BLANK_ANSWERS,
    PATH_FRAMES,
    PATH_STEPS,
    PC,
    PC_PEER,
    PORT_BY_NAME,
    PSE_KINDS,
    SERVER_IP,
    SERVER_NAME,
    STATIC_BY_KEY,
    TOPO_BLANK_ORDER,
    TOPO_BLANKS,
    TOPO_BUS,
    TOPO_MESH,
    TOPO_RING,
    TOPO_STAR,
    TOPOLOGY_BY_NAME,
    TOPOLOGY_NAMES,
    TRANSPORT_HEADER,
    Lan,
    broadcast_domains,
    collision_domains,
    crosses_router,
    encapsulate,
    fault_layer,
    lan_frame,
    mesh_links,
    service_for_port,
)
from app.v1.ampcr_pratique_pr20_figures import is_local_for

PR19_CODE = "PR19"

KIND_ORDER = "ordonnancement"
KIND_TOPO = "topologies"
KIND_LAYERS = "couches et protocoles"
KIND_EQUIPMENT = "choix d'équipement"
KIND_SCHEMA = "schéma à compléter"
KIND_DIAG = "diagnostic par couche"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-23", "AP-29", "AP-31"})


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

ENCAP_STEPS: tuple[tuple[str, str], ...] = (
    ("Application", "Le navigateur prépare la requête pour le site (données)."),
    ("Transport", "TCP ajoute son en-tête : port source et port de destination 443 (segment)."),
    ("Réseau", "IP ajoute son en-tête : adresse IP source et adresse IP de destination (paquet)."),
    ("Liaison", "Ethernet ajoute l'en-tête (adresses MAC, type) et le FCS (trame)."),
    ("Physique", "La carte réseau émet la trame bit par bit sur le câble."),
)

E01_STEPS = _labels(PATH_STEPS)
E02_STEPS = _labels(DIAG_STEPS)
E03_STEPS = _labels(ENCAP_STEPS)

E04_CASES: tuple[tuple[str, str], ...] = (
    ("Un jeton circule de station en station ; seule la station qui le détient peut émettre", TOPO_RING),
    ("Un T BNC à l'arrière de chaque PC, le câble coaxial continue vers le PC suivant", TOPO_BUS),
    ("Quatre agences reliées chacune aux trois autres par une liaison louée", TOPO_MESH),
    ("Chaque PC a son propre câble jusqu'au switch de la baie", TOPO_STAR),
    ("Câble coaxial de poste en poste, un bouchon de 50 Ω à chaque extrémité", TOPO_BUS),
    ("Double boucle de fibre : en cas de coupure, les deux boucles se referment en une seule", TOPO_RING),
    ("Switch central en panne : plus aucun poste ne communique ; un câble coupé n'isole qu'un poste", TOPO_STAR),
    ("Routeurs d'un opérateur : une liaison coupée, le trafic passe par un autre chemin", TOPO_MESH),
)
E04_CORRECT = tuple(TOPOLOGY_NAMES.index(t) for _d, t in E04_CASES)

E05_CASES: tuple[tuple[str, str], ...] = (
    ("Le serveur DHCP intégré à la box, qui distribue les adresses aux postes", KIND_SERVICE),
    ("TCP : règles d'un transport fiable avec accusés de réception", KIND_PROTOCOL),
    ("Le switch 24 ports de la baie", KIND_DEVICE),
    ("Le partage de fichiers \\\\SRV-01\\Compta proposé par le serveur", KIND_SERVICE),
    ("HTTP : format des requêtes et réponses entre navigateur et site web", KIND_PROTOCOL),
    ("Le routeur qui relie le réseau de l'agence à Internet", KIND_DEVICE),
    ("La résolution des noms assurée par le serveur DNS de la société", KIND_SERVICE),
    ("IP : adressage des paquets et acheminement d'un réseau à l'autre", KIND_PROTOCOL),
    ("Le point d'accès Wi-Fi fixé au plafond", KIND_DEVICE),
)
E05_CORRECT = tuple(PSE_KINDS.index(k) for _d, k in E05_CASES)

E06_CATEGORIES = (L2, L3, L4, L7)
E06_CASES: tuple[tuple[str, str], ...] = (
    ("IP : adresse de chaque paquet et routage d'un réseau à l'autre", L3),
    ("TCP : connexion fiable, accusés de réception, numéros de port", L4),
    ("Ethernet : trames entre cartes réseau d'un même réseau local, adresses MAC", L2),
    ("DNS : traduction de www.exemple.be en adresse IP", L7),
    ("ICMP : messages utilisés par ping et tracert", L3),
    ("UDP : envoi rapide sans accusé de réception, numéros de port", L4),
    ("Wi-Fi (IEEE 802.11) : trames radio entre le portable et le point d'accès", L2),
    ("DHCP : demande automatique d'une adresse au démarrage du poste", L7),
)
E06_CORRECT = tuple(E06_CATEGORIES.index(layer) for _d, layer in E06_CASES)

E07_CATEGORIES = (DEV_HUB, DEV_SWITCH, DEV_ROUTER, DEV_MODEM, DEV_AP, DEV_REPEATER)
E07_CASES: tuple[tuple[str, str], ...] = (
    ("Relie le réseau 192.168.1.0/24 du rez au réseau 192.168.2.0/24 de l'étage", DEV_ROUTER),
    ("Recopie chaque signal reçu sur tous ses autres ports, sans lire d'adresse", DEV_HUB),
    ("Apprend la MAC des postes branchés sur chaque port et n'envoie la trame qu'au bon port", DEV_SWITCH),
    ("Transforme les données en signal VDSL sur la paire téléphonique de l'opérateur", DEV_MODEM),
    ("Permet aux portables et aux smartphones de rejoindre le réseau filaire par radio", DEV_AP),
    ("Régénère le signal pour prolonger une liaison trop longue, sans rien filtrer", DEV_REPEATER),
    ("Choisit la route vers un autre réseau grâce à sa table de routage", DEV_ROUTER),
    ("Tous ses ports forment un seul domaine de collision : à remplacer en priorité", DEV_HUB),
)
E07_CORRECT = tuple(E07_CATEGORIES.index(d) for _t, d in E07_CASES)

# Symptômes (relevés) → première couche en défaut, calculée par `fault_layer`.
E08_CASES: tuple[tuple[str, dict[str, bool]], ...] = (
    ("ping de 198.51.100.20 réussi ; « www.exemple.be » introuvable, nslookup échoue", {"app_ok": False}),
    ("Voyant éteint sur la carte et sur le port du switch ; câble écrasé sous un bureau", {"link_light": False}),
    ("Voyant allumé, mais le port du switch est configuré dans le VLAN des invités", {"right_vlan": False}),
    ("ipconfig : passerelle par défaut vide ; les postes du même réseau répondent", {"ip_ok": False}),
    ("ping du serveur réussi ; Test-NetConnection SRV-01 -Port 3389 échoue (pare-feu du serveur)", {"port_open": False}),
    ("Testeur de câble : fil 6 coupé dans la prise murale", {"link_light": False}),
    ("Adresse 192.168.1.23 correcte ; ping de la passerelle 192.168.1.1 sans réponse", {"gateway_ping": False}),
    ("Le logiciel de comptabilité refuse l'identifiant de l'utilisateur ; le réseau répond", {"app_ok": False}),
)
E08_CORRECT = tuple(FAULT_LAYERS.index(fault_layer(**({"link_light": True} | flags))) for _t, flags in E08_CASES)

E09_ANSWERS = dict(zip(TOPO_BLANKS, TOPO_BLANK_ORDER, strict=True))

E11 = ENCAP_BLANK

E12_FIRST, E12_SECOND = PATH_FRAMES

E13_COLLISIONS = collision_domains(DOMAINS_BLANK_LAN)
E13_BROADCASTS = broadcast_domains(DOMAINS_BLANK_LAN)
E13_SWITCHED = Lan(
    DOMAINS_BLANK_LAN.nodes[:2] + (("HUB", N_SWITCH, 300, 104),) + DOMAINS_BLANK_LAN.nodes[3:],
    DOMAINS_BLANK_LAN.links,
)
E13_AFTER = collision_domains(E13_SWITCHED)

E15_NEEDS: tuple[tuple[str, str], ...] = (
    ("Raccorder la ligne VDSL de l'opérateur", DEV_MODEM),
    ("Relier entre eux les 14 postes et 2 imprimantes du bureau (même réseau)", DEV_SWITCH),
    ("Séparer le réseau des bureaux (192.168.10.0/24) de celui de l'atelier (192.168.20.0/24) et les relier", DEV_ROUTER),
    ("Donner accès au réseau aux portables des commerciaux en salle de réunion", DEV_AP),
)


def _hub_lan(pcs: int, kind: str) -> Lan:
    names = tuple(f"PC{i}" for i in range(1, pcs + 1))
    nodes = (("BOX", N_ROUTER, 0, 0), ("C", kind, 0, 0)) + tuple((n, N_PC, 0, 0) for n in names)
    return Lan(nodes, (("BOX", "C"),) + tuple(("C", n) for n in names))


E16_PCS = 8
E16_BEFORE = collision_domains(_hub_lan(E16_PCS, N_HUB))
E16_AFTER = collision_domains(_hub_lan(E16_PCS, N_SWITCH))

E17_A, E17_B, E17_PREFIX = "192.168.1.20", "192.168.2.30", 24
E17_LOCAL = is_local_for(E17_A, E17_PREFIX, E17_B)

E19_RULES: tuple[tuple[str, int, str], ...] = (  # (transport, port, décision), vers Internet
    ("TCP", 80, "autorisé"),
    ("TCP", 443, "autorisé"),
    ("UDP", 53, "autorisé"),
    ("TCP", 587, "bloqué"),
    ("TCP", 445, "bloqué"),
    ("TCP", 3389, "bloqué"),
)
E19_BLOCKED_SERVICE = service_for_port(587)

E20_SITES = 5
E20_MESH = mesh_links(E20_SITES)
E20_STAR = E20_SITES - 1  # chaque agence reliée au siège

# --- Mini-examen -------------------------------------------------------------------------------

X03 = encapsulate(0, "TCP")  # accusé de réception TCP sans données : bourrage → 64 octets

X04_LOCAL = lan_frame(PC, PC_PEER.ip)
X04_REMOTE = lan_frame(PC, SERVER_IP)

X05_PCS_SWITCH, X05_PCS_HUB = 12, 4
X05_LAN = Lan(
    (("BOX", N_ROUTER, 0, 0), ("SW", N_SWITCH, 0, 0), ("HUB", N_HUB, 0, 0))
    + tuple((f"P{i}", N_PC, 0, 0) for i in range(1, X05_PCS_SWITCH + X05_PCS_HUB + 1)),
    (("BOX", "SW"), ("SW", "HUB"))
    + tuple(("SW", f"P{i}") for i in range(1, X05_PCS_SWITCH + 1))
    + tuple(("HUB", f"P{i}") for i in range(X05_PCS_SWITCH + 1, X05_PCS_SWITCH + X05_PCS_HUB + 1)),
)
X05_COLLISIONS = collision_domains(X05_LAN)
X05_BROADCASTS = broadcast_domains(X05_LAN)

X10_SITES = 6
X10_MESH = mesh_links(X10_SITES)

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

_TOPO_EFFECT = {name: TOPOLOGY_BY_NAME[name].failure for name in TOPOLOGY_NAMES}

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le trajet d'un paquet vers Internet",
        question_type="ordering",
        requirement_ids=("AP-29", "AP-31"),
        kind=KIND_ORDER,
        context=(
            "Dans un cabinet d'architectes, tu expliques à un stagiaire ce qui se passe quand le poste "
            f"{PC.ip} ouvre le site {SERVER_NAME}, hébergé sur Internet. Tu as noté les six étapes sur des "
            "fiches, mais le stagiaire les a mélangées en les photocopiant."
        ),
        instructions=("Remets les six étapes dans l'ordre, du poste jusqu'au serveur.",),
        criteria=(
            _c("Ordre", 3, "Comparer les réseaux → trouver la MAC (ARP) → encapsuler → traverser le switch → passer le routeur (NAT) → rejoindre le serveur (0,5 pt par étape)."),
        ),
        correction=(
            "1. Le poste compare l'adresse du serveur à son propre réseau : elle n'en fait pas partie, il enverra donc le paquet à sa passerelle par défaut (la box). 2. Il cherche par ARP l'adresse MAC de la passerelle. 3. Il encapsule : données, segment TCP (ports), paquet IP (adresses IP), trame Ethernet (adresses MAC).",
            "4. Le switch lit l'adresse MAC de destination et envoie la trame sur le seul port de la box. 5. La box retire la trame, lit l'IP, remplace l'adresse source privée par son adresse publique (NAT) et refait une trame vers l'opérateur. 6. Chaque routeur d'Internet refait la trame jusqu'au serveur ; l'adresse IP de destination ne change pas.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre un diagnostic couche par couche",
        question_type="ordering",
        requirement_ids=("AP-29",),
        kind=KIND_ORDER,
        context=(
            "Le service informatique d'une école affiche au mur une fiche « diagnostic réseau en six "
            "étapes », du bas vers le haut du modèle OSI. Un élève l'a décrochée et recollée dans le "
            "désordre. Tu dois la reconstituer avant l'arrivée des techniciens."
        ),
        instructions=("Remets les six étapes dans l'ordre, de la couche la plus basse à la consignation.",),
        criteria=(
            _c("Ordre", 3, "Physique (1) → liaison (2) → réseau (3) → transport (4) → application (7) → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. Physique : voyants, câble, prise, cordon. 2. Liaison : port du switch actif, bon VLAN, passerelle visible dans arp -a. 3. Réseau : ipconfig (adresse, masque, passerelle), ping de la passerelle puis d'une adresse extérieure.",
            "4. Transport : le port du service est-il joignable (pare-feu) ? 5. Application : nom résolu, service démarré, identifiants. 6. On consigne la couche en défaut, la preuve, la correction et le contrôle refait. On monte d'une couche seulement quand la précédente est prouvée correcte.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (2, 5, 0, 4, 1, 3)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'encapsulation à l'émission",
        question_type="ordering",
        requirement_ids=("AP-29",),
        kind=KIND_ORDER,
        context=(
            "Pour préparer une présentation aux nouveaux employés d'une société de logistique, tu dois "
            "montrer comment une requête vers le site sécurisé de la société descend les couches du "
            "poste avant de partir sur le câble. Les cinq cartes de la présentation sont mélangées."
        ),
        instructions=("Remets les cinq étapes de l'encapsulation dans l'ordre, de l'application jusqu'au câble.",),
        criteria=(
            _c("Ordre", 2.5, "Application → transport (segment) → réseau (paquet) → liaison (trame) → physique (bits) (0,5 pt par étape)."),
        ),
        correction=(
            "À l'émission, on descend les couches : l'application produit les données ; TCP y ajoute son en-tête avec les ports (segment) ; IP ajoute les adresses IP (paquet) ; Ethernet ajoute les adresses MAC, le type et le FCS (trame) ; la carte émet les bits.",
            "À la réception, le chemin est inverse (décapsulation) : chaque couche lit et retire son en-tête, puis passe le reste à la couche du dessus.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 4, 0, 3, 1)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Reconnaître la topologie décrite",
        question_type="classification",
        requirement_ids=("AP-23",),
        kind=KIND_TOPO,
        context=(
            "Tu fais l'inventaire des réseaux, anciens et actuels, d'un groupe de PME. Le dossier contient "
            "huit notes de techniciens qui décrivent chacune une installation sans la nommer. Tu dois "
            "indiquer, pour chaque note, la topologie : bus, étoile, anneau ou maillage."
        ),
        instructions=("Range chaque note selon la topologie qu'elle décrit.",),
        criteria=(
            _c("Classement", 4, "T BNC et bouchons → bus ; un câble par PC jusqu'au switch, switch central en panne → étoile ; jeton, double boucle de fibre → anneau ; agences reliées chacune aux autres, routeurs à chemins multiples → maillage (0,5 pt par élément)."),
        ),
        correction=(
            "Bus : un seul câble coaxial passe de poste en poste (T BNC) et se termine par un bouchon à chaque bout. Étoile : chaque poste a son propre câble jusqu'à l'équipement central ; si cet équipement tombe, tout s'arrête, mais un câble coupé n'isole qu'un poste.",
            "Anneau : chaque station transmet à la suivante ; l'accès par jeton évite les collisions ; un double anneau (FDDI) se reboucle en cas de coupure. Maillage : plusieurs chemins existent entre les équipements, une liaison coupée ne coupe pas le service.",
        ),
        classification=Classification(categories=TOPOLOGY_NAMES, elements=tuple(d for d, _t in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Protocole, service ou équipement ?",
        question_type="classification",
        requirement_ids=("AP-29", "AP-31"),
        kind=KIND_LAYERS,
        context=(
            "Dans le rapport d'intervention d'un collègue, les mots « protocole », « service » et "
            "« équipement » sont employés au hasard. Avant de l'envoyer au client, tu relèves neuf "
            "éléments cités et tu dois dire, pour chacun, s'il s'agit d'un protocole (des règles), d'un "
            "service (une fonction rendue par un programme serveur) ou d'un équipement (du matériel)."
        ),
        instructions=("Range chaque élément dans la bonne catégorie.",),
        criteria=(
            _c("Classement", 4.5, "TCP, HTTP, IP → protocoles ; serveur DHCP de la box, partage \\\\SRV-01\\Compta, résolution DNS → services ; switch, routeur, point d'accès → équipements (0,5 pt par élément)."),
        ),
        correction=(
            "Un protocole est un ensemble de règles d'échange (TCP, HTTP, IP) : il ne « tourne » nulle part, il est suivi par les deux côtés. Un service est une fonction rendue par un programme serveur qui utilise un protocole et attend sur un port : le serveur DHCP de la box, le partage de fichiers, la résolution DNS.",
            "Un équipement est du matériel : switch, routeur, point d'accès. Un équipement peut héberger des services (la box fait tourner un serveur DHCP) : on écrit « le service DHCP de la box », pas « l'équipement DHCP ».",
        ),
        classification=Classification(categories=PSE_KINDS, elements=tuple(d for d, _k in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="À quelle couche travaille chaque protocole ?",
        question_type="classification",
        requirement_ids=("AP-29",),
        kind=KIND_LAYERS,
        context=(
            "Pour préparer un tableau de diagnostic destiné au service d'assistance d'une mutuelle, tu "
            "dois placer huit protocoles, décrits par leur rôle, dans le modèle OSI. Le tableau servira "
            "à savoir quel outil utiliser quand l'un d'eux pose problème."
        ),
        instructions=("Range chaque protocole selon la couche OSI où il travaille.",),
        criteria=(
            _c("Classement", 4, "Ethernet, Wi-Fi → couche 2 ; IP, ICMP → couche 3 ; TCP, UDP → couche 4 ; DNS, DHCP → couche 7 (0,5 pt par élément)."),
        ),
        correction=(
            "Couche 2 (liaison) : Ethernet et Wi-Fi transportent des trames entre appareils d'un même réseau local, avec des adresses MAC. Couche 3 (réseau) : IP adresse les paquets et permet le routage ; ICMP (ping, tracert) sert au contrôle de cette couche.",
            "Couche 4 (transport) : TCP et UDP relient deux programmes grâce aux ports, TCP avec accusés de réception, UDP sans. Couche 7 (application) : DNS et DHCP sont des protocoles applicatifs, même s'ils servent à configurer le réseau ; ils utilisent UDP.",
        ),
        classification=Classification(categories=E06_CATEGORIES, elements=tuple(d for d, _l in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Quel équipement correspond à chaque rôle ?",
        question_type="classification",
        requirement_ids=("AP-31",),
        kind=KIND_EQUIPMENT,
        context=(
            "Un fournisseur a envoyé à une PME un catalogue sans les noms des appareils : seule la "
            "description du rôle de chacun apparaît. Le gérant te demande de retrouver de quel "
            "équipement il s'agit avant de passer commande : hub, switch, routeur, modem, point d'accès "
            "ou répéteur."
        ),
        instructions=("Range chaque description selon l'équipement qu'elle désigne.",),
        criteria=(
            _c("Classement", 4, "Recopie sur tous les ports, un seul domaine de collision → hub ; table MAC → switch ; relie 192.168.1.0/24 et 192.168.2.0/24, table de routage → routeur ; signal VDSL → modem ; accès radio → point d'accès ; régénère le signal → répéteur (0,5 pt par élément)."),
        ),
        correction=(
            "Le hub (couche 1) recopie les bits sur tous ses ports : tous les postes partagent un seul domaine de collision, on le remplace par un switch. Le répéteur (couche 1) régénère le signal pour allonger une liaison. Le switch (couche 2) apprend les adresses MAC et n'envoie la trame qu'au port du destinataire.",
            "Le routeur (couche 3) relie des réseaux IP différents et choisit la route avec sa table de routage. Le modem convertit le signal pour la ligne de l'opérateur (VDSL sur la paire téléphonique). Le point d'accès relie les appareils Wi-Fi au réseau filaire.",
        ),
        classification=Classification(categories=E07_CATEGORIES, elements=tuple(t for t, _d in E07_CASES), correct=E07_CORRECT),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Diagnostic : quelle couche est en défaut ?",
        question_type="classification",
        requirement_ids=("AP-29",),
        kind=KIND_DIAG,
        context=(
            "Le service d'assistance d'un centre hospitalier a reçu huit appels dans la matinée. Pour "
            "chacun, le technicien a noté ce qu'il a relevé sur place. Tu dois indiquer la première "
            "couche du modèle OSI en défaut, pour orienter la bonne équipe."
        ),
        instructions=("Range chaque relevé selon la couche en défaut.",),
        criteria=(
            _c("Classement", 4, "Voyant éteint, fil coupé → couche 1 ; mauvais VLAN → couche 2 ; passerelle vide, passerelle sans réponse → couche 3 ; port 3389 bloqué → couche 4 ; nom introuvable, identifiant refusé → couche 7 (0,5 pt par élément)."),
        ),
        correction=(
            "Couche 1 : sans voyant de lien ou avec un fil coupé, rien ne peut passer. Couche 2 : un port placé dans le mauvais VLAN relie le poste à un autre réseau local. Couche 3 : sans passerelle ou si la passerelle ne répond pas, on ne sort pas du réseau. Couche 4 : le serveur répond au ping, mais le pare-feu bloque le port du service (3389, Bureau à distance).",
            "Couche 7 : si une adresse IP répond mais pas le nom, c'est la résolution DNS (application) ; un identifiant refusé alors que le réseau répond est un problème d'application. On note toujours la preuve : la couche du dessous fonctionne.",
        ),
        classification=Classification(categories=FAULT_LAYERS, elements=tuple(t for t, _f in E08_CASES), correct=E08_CORRECT),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : nommer quatre topologies",
        question_type="document_analysis",
        requirement_ids=("AP-23",),
        kind=KIND_SCHEMA,
        context=(
            "Pour un audit des réseaux d'un groupe scolaire, tu as dessiné quatre réseaux rencontrés dans "
            "les différents bâtiments (document 1), sans leur nom. Le rapport doit préciser la topologie "
            "de chacun et ce qui se passe si une liaison est coupée."
        ),
        documents=(_schema("pr19-topologies-a-completer", "Document 1 — Quatre topologies à nommer (schéma fictif)"),),
        instructions=(
            "Nomme la topologie ①, ②, ③ et ④.",
            "Pour chacune, indique l'effet de la coupure d'une liaison.",
        ),
        criteria=(
            _c("Noms", 2, "① " + E09_ANSWERS["①"] + " ; ② maillage complet ; ③ " + E09_ANSWERS["③"].lower() + " ; ④ " + E09_ANSWERS["④"].lower() + " (0,5 pt chacun)."),
            _c("Effet d'une coupure", 2, "Anneau simple : tout s'arrête ; maillage : autre chemin, personne n'est isolé ; bus : tout le segment s'arrête ; étoile : seul le poste du câble coupé est isolé (0,5 pt chacun)."),
        ),
        correction=(
            "① Anneau : chaque PC est relié au suivant et le dernier au premier. ② Maillage complet : chacun des quatre routeurs est relié aux trois autres (6 liaisons). ③ Bus : un câble unique fermé par un bouchon à chaque bout. ④ Étoile : un switch central et un câble par poste.",
            f"Coupure d'une liaison : ① {_TOPO_EFFECT[TOPO_RING]} ; ② {_TOPO_EFFECT[TOPO_MESH]} ; ③ {_TOPO_EFFECT[TOPO_BUS]} ; ④ {_TOPO_EFFECT[TOPO_STAR]}.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : modèles OSI et TCP/IP",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_SCHEMA,
        context=(
            "Un formateur prépare un aide-mémoire pour les techniciens d'un service d'assistance. Sur le "
            "tableau du document 1, il a effacé plusieurs noms de couches, une couche du modèle TCP/IP "
            "et deux unités de données. Il te demande de compléter le tableau."
        ),
        documents=(_schema("pr19-osi-a-completer", "Document 1 — Modèles OSI et TCP/IP à compléter (schéma fictif)"),),
        instructions=(
            "Complète ① à ④ (noms de couches OSI) et ⑤ (couche TCP/IP).",
            "Complète ⑥ et ⑦ (unités de données) et cite un équipement qui travaille à la couche ③.",
        ),
        criteria=(
            _c("Couches OSI", 2, "① présentation ; ② transport ; ③ réseau ; ④ liaison de données (0,5 pt chacune)."),
            _c("Couche TCP/IP", 0.5, "⑤ Internet."),
            _c("Unités et équipement", 1.5, "⑥ paquet ; ⑦ trame ; routeur à la couche réseau (0,5 pt chacun)."),
        ),
        correction=(
            f"① {OSI_BLANK_ANSWERS['①']} (couche 6) ; ② {OSI_BLANK_ANSWERS['②']} (4) ; ③ {OSI_BLANK_ANSWERS['③']} (3) ; ④ {OSI_BLANK_ANSWERS['④']} (2). ⑤ La couche OSI 3 correspond à la couche {OSI_BLANK_ANSWERS['⑤']} du modèle TCP/IP (IP, ICMP).",
            f"⑥ À la couche réseau, l'unité est le {OSI_BLANK_ANSWERS['⑥']} ; ⑦ à la couche liaison, la {OSI_BLANK_ANSWERS['⑦']}. Le routeur travaille à la couche réseau : il lit l'adresse IP pour choisir le chemin.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : tailles d'une requête DNS encapsulée",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_SCHEMA,
        context=(
            f"Un poste d'une agence bancaire envoie une requête DNS de {E11.data} octets de données à son serveur "
            "DNS. Le document 1 montre l'encapsulation, sans les tailles. Rappel : en-têtes sans option, "
            f"IPv4 {IPV4_HEADER} octets, Ethernet {ETH_HEADER} octets plus un FCS de {ETH_FCS} octets ; les "
            f"données d'une trame font au moins {ETH_MIN_PAYLOAD} octets."
        ),
        documents=(_schema("pr19-encapsulation-a-completer", "Document 1 — Encapsulation à compléter (schéma fictif)"),),
        instructions=(
            "Donne la taille de l'en-tête UDP ④, puis calcule ①, ② et ③.",
            "Dis si un bourrage est nécessaire, en justifiant.",
        ),
        criteria=(
            _c("En-tête UDP", 0.5, f"④ {TRANSPORT_HEADER['UDP']} octets."),
            _c("Calculs", 1.5, f"① {E11.data} + {TRANSPORT_HEADER['UDP']} = {E11.segment} ; ② {E11.segment} + {IPV4_HEADER} = {E11.packet} ; ③ {ETH_HEADER} + {E11.packet} + {ETH_FCS} = {E11.frame} octets (0,5 pt chacun)."),
            _c("Bourrage", 1, f"Paquet de {E11.packet} octets ≥ {ETH_MIN_PAYLOAD} : pas de bourrage ; trame de {E11.frame} ≥ {ETH_MIN_FRAME} octets."),
        ),
        correction=(
            f"DNS utilise ici UDP, dont l'en-tête fait {TRANSPORT_HEADER['UDP']} octets (④). Datagramme UDP : {E11.data} + {TRANSPORT_HEADER['UDP']} = {E11.segment} octets (①). Paquet IP : {E11.segment} + {IPV4_HEADER} = {E11.packet} octets (②). Trame : {ETH_HEADER} + {E11.packet} + {ETH_FCS} = {E11.frame} octets (③).",
            f"Le paquet fait {E11.packet} octets, plus que le minimum de {ETH_MIN_PAYLOAD} octets de données d'une trame : aucun bourrage n'est ajouté, la trame dépasse les {ETH_MIN_FRAME} octets minimaux.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : adresses MAC et IP de deux trames",
        question_type="document_analysis",
        requirement_ids=("AP-29", "AP-31"),
        kind=KIND_SCHEMA,
        context=(
            f"Dans une fiduciaire, le poste {PC.owner} ouvre le site {SERVER_NAME}. Le document 1 montre le "
            "chemin et les adresses de chaque équipement ; dans le tableau, plusieurs adresses des deux "
            "premières trames ont été effacées. La box fait la traduction d'adresses (NAT)."
        ),
        documents=(_schema("pr19-chemin-a-completer", "Document 1 — Chemin et adresses à compléter (schéma fictif)"),),
        instructions=(
            "Complète ① à ⑤.",
            "Explique pourquoi les adresses MAC changent entre les deux trames et pourquoi l'adresse IP source change aussi.",
        ),
        criteria=(
            _c("Adresses", 2.5, f"① {E12_FIRST.dst_mac} (box côté réseau local) ; ② {E12_SECOND.src_mac} ; ③ {E12_SECOND.dst_mac} ; ④ {E12_SECOND.src_ip} ; ⑤ {E12_SECOND.dst_ip} (0,5 pt chacune)."),
            _c("Explication", 1.5, "MAC : valable sur un seul réseau local, chaque routeur refait la trame ; IP source : la box remplace l'adresse privée par son adresse publique (NAT) ; IP de destination inchangée."),
        ),
        correction=(
            f"① Le serveur n'est pas dans le réseau {PC.ip}/24 : le PC envoie la trame à sa passerelle, la box, côté réseau local ({BOX_LAN.mac}). ② et ③ : la box émet une nouvelle trame de son interface opérateur ({BOX_WAN.mac}) vers le routeur de l'opérateur ({ISP_ROUTER.mac}). ④ IP source {BOX_WAN.ip} ; ⑤ IP de destination {SERVER_IP}, inchangée.",
            "Une adresse MAC ne sert qu'à l'intérieur d'un réseau local : chaque routeur retire la trame et en construit une nouvelle pour le réseau suivant. L'adresse IP source change ici uniquement parce que la box fait du NAT : l'adresse privée 192.168.x.x n'est pas routable sur Internet.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : compter les domaines de collision et de diffusion",
        question_type="document_analysis",
        requirement_ids=("AP-31", "AP-23"),
        kind=KIND_SCHEMA,
        context=(
            "Une petite imprimerie se plaint de lenteurs dans l'atelier. Le document 1 montre son réseau : "
            "un routeur à deux interfaces, un switch pour les bureaux et un vieux hub pour l'atelier. "
            "Avant de proposer un changement, tu dois compter les domaines de collision et de diffusion."
        ),
        documents=(_schema("pr19-domaines-a-completer", "Document 1 — Réseau de l'imprimerie (schéma fictif)"),),
        instructions=(
            "Compte les domaines de collision et les domaines de diffusion, en justifiant.",
            "Propose un changement pour l'atelier et donne le nouveau nombre de domaines de collision.",
        ),
        criteria=(
            _c("Collisions", 1.5, f"{E13_COLLISIONS} : 5 liaisons du switch (4 postes + routeur), chacune un domaine ; le hub et ses 4 liaisons = 1 domaine."),
            _c("Diffusions", 1, f"{E13_BROADCASTS} : une par interface du routeur ; switch et hub ne les séparent pas."),
            _c("Proposition", 1, f"Remplacer le hub par un switch : {E13_AFTER} domaines de collision, toujours {E13_BROADCASTS} domaines de diffusion."),
        ),
        correction=(
            f"Côté bureaux, chaque port du switch est un domaine de collision : 4 postes + la liaison vers le routeur = 5. Côté atelier, le hub recopie les bits sur tous ses ports : ses 4 liaisons (routeur et 3 postes) forment un seul domaine. Total : {E13_COLLISIONS}. Le routeur arrête les diffusions : {E13_BROADCASTS} domaines de diffusion, un par interface.",
            f"Les lenteurs de l'atelier viennent des collisions et du débit partagé du hub (semi-duplex). On le remplace par un switch : chaque liaison devient un domaine, {E13_AFTER} au total, en duplex intégral ; le nombre de domaines de diffusion ne change pas ({E13_BROADCASTS}).",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : champs d'une trame Ethernet",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_SCHEMA,
        context=(
            "Pendant une analyse de trafic dans une entreprise de transport, un collègue te montre une "
            "trame capturée, découpée en champs (document 1). Les noms de quatre champs ont été effacés ; "
            "seules les tailles en octets restent."
        ),
        documents=(_schema("pr19-trame-a-completer", "Document 1 — Trame Ethernet à compléter (schéma fictif)"),),
        instructions=(
            "Nomme les champs ①, ②, ③ et ④ et donne le rôle de chacun.",
            f"Dis à qui est destinée une trame dont le champ ① vaut {BROADCAST_MAC}.",
        ),
        criteria=(
            _c("Champs", 2, "① adresse MAC de destination ; ② adresse MAC source ; ③ type (protocole transporté : IPv4, ARP, IPv6) ; ④ FCS, contrôle d'erreur (0,5 pt chacun)."),
            _c("Diffusion", 1, "Trame adressée à tous les appareils du réseau local (diffusion, par exemple une requête ARP) ; elle traverse les switchs, pas les routeurs."),
        ),
        correction=(
            "① Adresse MAC de destination (6 octets) : c'est elle que le switch lit pour choisir le port. ② Adresse MAC source (6 octets) : le switch l'apprend dans sa table MAC. ③ Type (2 octets) : ce que contiennent les données (0x0800 IPv4, 0x0806 ARP, 0x86DD IPv6). ④ FCS (4 octets) : contrôle d'erreur ; une trame abîmée est jetée.",
            f"{BROADCAST_MAC} est l'adresse de diffusion : tous les appareils du réseau local reçoivent la trame, par exemple la question ARP « qui a l'adresse 192.168.1.1 ? ». Les switchs la recopient sur tous leurs ports ; un routeur l'arrête.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Choisir les équipements d'une PME",
        question_type="document_analysis",
        requirement_ids=("AP-31",),
        kind=KIND_EQUIPMENT,
        context=(
            "Une société de menuiserie s'installe dans de nouveaux locaux : bureaux et atelier. Le "
            "gérant a listé ses besoins (document 1) et te demande quel type d'équipement répond à "
            "chacun, avec une justification courte. Il veut aussi savoir si sa box peut en remplacer "
            "certains."
        ),
        documents=(
            _table("Document 1 — Besoins du client", ("N°", "Besoin"), *((str(i), need) for i, (need, _d) in enumerate(E15_NEEDS, start=1))),
        ),
        instructions=(
            "Pour chaque besoin, nomme l'équipement et justifie par son rôle ou sa couche.",
            "Indique quels rôles une box d'opérateur peut assurer.",
        ),
        criteria=(
            _c("Équipements", 2, "1 modem (signal de la ligne) ; 2 switch (même réseau local, table MAC) ; 3 routeur (deux réseaux IP différents) ; 4 point d'accès Wi-Fi (0,5 pt chacun)."),
            _c("Justifications", 1, "Couche ou rôle correct pour chaque choix (switch couche 2, routeur couche 3, modem signal, point d'accès radio vers filaire)."),
            _c("Box", 1, "Modem, routeur avec NAT, petit switch, point d'accès, DHCP ; switch et point d'accès dédiés si plus de ports ou de couverture."),
        ),
        correction=(
            "1. La ligne VDSL demande un modem, qui convertit le signal de la paire téléphonique. 2. Pour relier 16 appareils du même réseau, un switch (couche 2) : il envoie chaque trame au seul port du destinataire. 3. Deux réseaux IP différents (192.168.10.0/24 et 192.168.20.0/24) se relient par un routeur (couche 3), qui sépare aussi les diffusions et peut filtrer. 4. Les portables sans fil rejoignent le réseau par un point d'accès Wi-Fi.",
            "La box de l'opérateur réunit modem, routeur avec NAT, petit switch (souvent 4 ports), point d'accès et serveur DHCP. Pour 16 appareils, on ajoute un switch de 24 ports ; un point d'accès dédié couvre mieux la salle de réunion ; le routage entre bureaux et atelier demande un routeur qui gère deux réseaux internes.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Remplacer un vieux hub : justifier le choix",
        question_type="document_analysis",
        requirement_ids=("AP-31", "AP-23"),
        kind=KIND_EQUIPMENT,
        context=(
            f"Dans un garage, {E16_PCS} postes sont branchés sur un hub 10 Mb/s, lui-même relié à la box. Les "
            "mécaniciens se plaignent de lenteurs aux heures de pointe. Le document 1 reprend ce que tu "
            "as relevé sur place. Le patron demande s'il faut acheter un autre hub, un switch ou un "
            "routeur."
        ),
        documents=(
            _table(
                "Document 1 — Relevé dans le garage (fictif)",
                ("Point", "Constat"),
                ("Équipement central", "Hub 16 ports, 10 Mb/s, voyant « COL » souvent allumé"),
                ("Cartes des postes", "1 Gb/s, négociées en 10 Mb/s semi-duplex"),
                ("Adressage", "Tous les postes dans 192.168.1.0/24, passerelle 192.168.1.1 (box)"),
            ),
        ),
        instructions=(
            "Choisis l'équipement de remplacement et justifie (couche, collisions, duplex).",
            "Donne le nombre de domaines de collision avant et après, et dis pourquoi un routeur n'est pas utile ici.",
        ),
        criteria=(
            _c("Choix justifié", 1.5, "Switch (couche 2) : envoie chaque trame au seul port du destinataire, duplex intégral, débit non partagé (1 Gb/s par port)."),
            _c("Domaines", 1, f"Avant : {E16_BEFORE} domaine de collision ; après : {E16_AFTER} (un par liaison, box comprise)."),
            _c("Pas de routeur", 0.5, "Un seul réseau IP (192.168.1.0/24) : rien à router ; la box fait déjà le routage vers Internet."),
        ),
        correction=(
            f"Le hub recopie chaque trame sur tous ses ports : les {E16_PCS} postes et la box partagent {E16_BEFORE} seul domaine de collision et 10 Mb/s en semi-duplex ; le voyant de collision le confirme. Un switch apprend les adresses MAC et n'envoie la trame qu'au bon port : chaque liaison devient un domaine de collision ({E16_AFTER} au total), en duplex intégral et à 1 Gb/s.",
            "Un routeur relie des réseaux IP différents : tous les postes sont dans 192.168.1.0/24, il n'y a rien à router à l'intérieur. La box assure déjà le routage vers Internet. Un autre hub ne changerait rien.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Deux réseaux IP reliés par un switch : pourquoi ça ne marche pas ?",
        question_type="document_analysis",
        requirement_ids=("AP-31", "AP-29"),
        kind=KIND_EQUIPMENT,
        context=(
            "Une association a deux salles : la salle A en 192.168.1.0/24, la salle B en 192.168.2.0/24. Un "
            "bénévole a relié les switchs des deux salles par un câble et un switch supplémentaire, mais "
            "les postes ne se joignent pas d'une salle à l'autre. Le document 1 montre son essai."
        ),
        documents=(
            _console(
                "Document 1 — Essai depuis un poste de la salle A (capture fictive)",
                "C:\\> ipconfig",
                f"   Adresse IPv4. . . . . . . . . . . . . .: {E17_A}",
                "   Masque de sous-réseau. . . . . . . . . : 255.255.255.0",
                "   Passerelle par défaut. . . . . . . . . : 192.168.1.1",
                f"C:\\> ping {E17_B}",
                "Délai d'attente de la demande dépassé.",
            ),
        ),
        instructions=(
            "Explique pourquoi le ping échoue alors que les câbles sont branchés.",
            "Indique l'équipement à installer et les réglages à prévoir sur les postes.",
        ),
        criteria=(
            _c("Analyse", 1.5, f"{E17_B} n'est pas dans le réseau {E17_A}/24 : le poste envoie le paquet à sa passerelle ; un switch ne lit pas les adresses IP et ne route pas."),
            _c("Solution", 1.5, "Un routeur avec une interface dans chaque réseau (par exemple 192.168.1.1 et 192.168.2.1) ; passerelle par défaut de chaque salle = adresse du routeur dans sa salle."),
        ),
        correction=(
            f"Le poste {E17_A}/24 compare l'adresse {E17_B} à son réseau : elle n'en fait pas partie, il confie donc le paquet à sa passerelle 192.168.1.1. Le switch supplémentaire travaille à la couche 2 : il relie des câbles, mais ne lit pas les adresses IP et ne fait pas passer un paquet d'un réseau IP à l'autre.",
            "Il faut un routeur (couche 3) avec une interface dans chaque réseau, par exemple 192.168.1.1 dans la salle A et 192.168.2.1 dans la salle B ; la passerelle par défaut des postes de chaque salle est l'adresse du routeur dans leur salle. On vérifie ensuite par ping de la passerelle, puis d'un poste de l'autre salle.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Un vieux logiciel en NetBEUI entre deux sites",
        question_type="long_answer",
        requirement_ids=("AP-29",),
        kind=KIND_LAYERS,
        context=(
            "Une coopérative agricole utilise encore un logiciel de gestion des années 1990 qui ne "
            "communique qu'en NetBEUI. Les deux postes du siège se voient. La coopérative ouvre un "
            "dépôt dans un autre village, relié au siège par deux routeurs et une liaison de "
            "l'opérateur : le poste du dépôt ne trouve jamais le siège."
        ),
        instructions=(
            "Explique pourquoi le poste du dépôt ne trouve pas le siège.",
            "Propose une solution durable et cite une précaution.",
        ),
        criteria=(
            _c("Explication", 1.5, "NetBEUI n'a pas d'adresse réseau (seulement un nom NetBIOS) : non routable, il ne traverse pas les routeurs ; il repose sur la diffusion, arrêtée par le routeur."),
            _c("Solution", 1, "Passer à TCP/IP (version du logiciel ou logiciel de remplacement), qui est routable ; NetBEUI n'est plus disponible sur les systèmes actuels."),
            _c("Précaution", 0.5, "Sauvegarder les données et tester la migration avant de couper l'ancien système (ou tout autre précaution justifiée)."),
        ),
        correction=(
            "NetBEUI désigne les postes par un nom NetBIOS, sans adresse de réseau : un routeur ne peut pas savoir vers quel réseau envoyer le paquet. Il est donc non routable et repose sur des diffusions, que le routeur arrête. Au siège, les deux postes sont dans le même réseau local : ils se voient.",
            "Solution durable : passer le logiciel en TCP/IP (mise à jour, ou logiciel de remplacement), routable et seul protocole des systèmes actuels ; Windows XP n'installait déjà plus NetBEUI. Précaution : sauvegarder les données et tester sur un poste avant de basculer.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Ports et pare-feu : quel service est bloqué ?",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_DIAG,
        context=(
            "Dans un cabinet de notaires, les employés naviguent sur Internet sans problème, mais leur "
            "logiciel de messagerie ne parvient plus à envoyer le courrier depuis le changement de "
            "pare-feu. La réception fonctionne. Le document 1 reprend les règles du pare-feu vers "
            "Internet."
        ),
        documents=(
            _table(
                "Document 1 — Règles du pare-feu, trafic vers Internet (fictif)",
                ("Transport", "Port de destination", "Décision"),
                *((t, str(p), d) for t, p, d in E19_RULES),
            ),
        ),
        instructions=(
            "Identifie la règle qui bloque l'envoi du courrier et justifie.",
            "Le collègue propose d'ouvrir aussi les ports 445 et 3389 vers Internet : donne ton avis.",
        ),
        criteria=(
            _c("Règle en cause", 1.5, f"TCP {PORT_BY_NAME['SMTP'].ports[1]} bloqué : port d'envoi du courrier ({E19_BLOCKED_SERVICE}) ; à autoriser vers le serveur de messagerie du cabinet."),
            _c("Avis", 1.5, "Refuser : 445 (partage Windows SMB) et 3389 (Bureau à distance) ne doivent pas être ouverts vers Internet sans besoin ; ils exposeraient le cabinet. On n'ouvre que ce qui est nécessaire."),
        ),
        correction=(
            f"Le web passe par TCP 80 et 443, autorisés, et la résolution des noms par UDP 53, autorisé : la navigation fonctionne. L'envoi de courrier par le logiciel de messagerie utilise {E19_BLOCKED_SERVICE} sur TCP 587, bloqué : c'est la couche transport (port) qui est en défaut, pas le câble ni l'adresse IP. On autorise TCP 587 vers le serveur de messagerie, puis on teste un envoi.",
            "Les ports 445 (partage de fichiers SMB) et 3389 (Bureau à distance) n'ont rien à faire vers Internet pour ce besoin ; les ouvrir exposerait les postes. Règle : n'ouvrir que le port nécessaire, vers la seule destination nécessaire.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Relier cinq agences : étoile ou maillage ?",
        question_type="document_analysis",
        requirement_ids=("AP-23", "AP-31"),
        kind=KIND_EQUIPMENT,
        context=(
            f"Un réseau d'agences immobilières compte {E20_SITES} sites, dont le siège. Toutes les "
            "agences consultent le serveur du siège ; une coupure d'une demi-journée coûte cher. "
            "L'opérateur propose deux architectures de liaisons entre routeurs (document 1) et facture "
            "chaque liaison au mois."
        ),
        documents=(
            _table(
                "Document 1 — Propositions de l'opérateur (fictif)",
                ("Proposition", "Description"),
                ("A — étoile", "Chaque agence reliée au seul siège"),
                ("B — maillage complet", "Chaque site relié à tous les autres"),
            ),
        ),
        instructions=(
            "Calcule le nombre de liaisons de chaque proposition.",
            "Compare l'effet d'une liaison coupée et propose une solution intermédiaire justifiée.",
        ),
        criteria=(
            _c("Calculs", 1.5, f"A : {E20_STAR} liaisons ({E20_SITES} − 1) ; B : {E20_SITES} × {E20_SITES - 1} ÷ 2 = {E20_MESH} liaisons."),
            _c("Pannes", 1, "A : une liaison coupée isole l'agence concernée ; B : le trafic passe par un autre site, personne n'est isolé."),
            _c("Proposition", 1, "Maillage partiel : étoile vers le siège + une liaison de secours (ou une seconde liaison du siège) pour les agences critiques ; moins cher que le maillage complet."),
        ),
        correction=(
            f"Proposition A (étoile) : une liaison par agence vers le siège, soit {E20_STAR}. Proposition B (maillage complet) : chaque site est relié aux {E20_SITES - 1} autres, chaque liaison comptée une fois : {E20_SITES} × {E20_SITES - 1} ÷ 2 = {E20_MESH} liaisons, plus du double.",
            "En étoile, une liaison coupée isole l'agence concernée (et la panne du siège isole tout le monde). En maillage, un autre chemin existe. Compromis : maillage partiel, l'étoile plus une liaison de secours (par exemple une connexion Internet avec VPN) pour chaque agence critique.",
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
        title="Tout un atelier coupé d'un coup",
        question_type="short_answer",
        requirement_ids=("AP-23",),
        kind=KIND_TOPO,
        context=(
            "Un atelier de découpe utilise encore six PC reliés par un câble coaxial qui passe de poste en "
            "poste, avec un T BNC à l'arrière de chaque PC et un bouchon à chaque bout. Ce matin, un "
            "ouvrier a déplacé le dernier PC et a laissé tomber le bouchon : plus aucun PC ne communique."
        ),
        instructions=("Nomme la topologie, explique la panne et propose une installation actuelle.",),
        criteria=(
            _c("Topologie et panne", 1, "Bus : sans bouchon, le signal se réfléchit au bout du câble et brouille tout le segment ; tous les postes sont coupés."),
            _c("Proposition", 1, "Remettre le bouchon pour dépanner ; puis passer en étoile : switch et un câble à paires torsadées par poste (une coupure n'isole qu'un poste)."),
        ),
        correction=(
            f"C'est une topologie en bus (Ethernet coaxial). {TOPOLOGY_BY_NAME[TOPO_BUS].failure.capitalize()} : le bouchon absent fait réfléchir le signal, tout le segment s'arrête.",
            "Dépannage immédiat : remettre un bouchon au bout du câble. Solution durable : étoile, avec un switch et un câble à paires torsadées par poste ; une coupure n'isole alors qu'un seul poste.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Le site ne s'ouvre pas : quelle couche ?",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_DIAG,
        context=(
            "Dans une pharmacie, le poste de la caisse n'ouvre plus le site du grossiste, alors que le "
            "voyant réseau est allumé. Tu fais les relevés du document 1, dans l'ordre des couches."
        ),
        documents=(
            _console(
                "Document 1 — Relevés sur le poste de la caisse (capture fictive)",
                "C:\\> ipconfig",
                "   Adresse IPv4. . . . . . . . . . . . . .: 192.168.1.23",
                "   Passerelle par défaut. . . . . . . . . : 192.168.1.1",
                "C:\\> ping 192.168.1.1",
                "Réponse de 192.168.1.1 : octets=32 temps<1ms TTL=64",
                "C:\\> ping 198.51.100.20",
                "Réponse de 198.51.100.20 : octets=32 temps=14 ms TTL=55",
                "C:\\> nslookup www.exemple.be",
                "*** UnKnown ne parvient pas à trouver www.exemple.be : Server failed",
            ),
        ),
        instructions=("Indique la couche en défaut, prouve que les couches inférieures fonctionnent et propose les vérifications suivantes.",),
        criteria=(
            _c("Couche et preuves", 1, "Couches 1 à 3 correctes (voyant, adresse et passerelle, ping de la passerelle et d'une IP d'Internet) ; c'est la résolution des noms (DNS, couche 7) qui échoue."),
            _c("Vérifications", 1, "Serveur DNS configuré sur le poste (ipconfig /all), DNS de la box ou de l'opérateur, essai d'un autre serveur DNS ; puis rouvrir le site par son nom."),
        ),
        correction=(
            "Le voyant est allumé (couche 1) ; l'adresse et la passerelle sont cohérentes et la passerelle répond (couches 2 et 3) ; une adresse IP d'Internet répond aussi : le chemin réseau fonctionne. Seule la traduction du nom échoue : c'est le DNS, un service de la couche application.",
            "On vérifie le serveur DNS du poste (ipconfig /all), celui de la box, on essaie un autre serveur DNS, puis on rouvre le site par son nom et on consigne.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Taille d'un accusé de réception TCP",
        question_type="short_answer",
        requirement_ids=("AP-29",),
        kind=KIND_LAYERS,
        context=(
            "En analysant le trafic d'un serveur de fichiers, tu observes des segments TCP qui ne "
            "contiennent aucune donnée (simples accusés de réception). En-têtes sans option : TCP "
            f"{TRANSPORT_HEADER['TCP']} octets, IPv4 {IPV4_HEADER} octets, Ethernet {ETH_HEADER} octets plus un FCS de "
            f"{ETH_FCS} octets ; une trame transporte au moins {ETH_MIN_PAYLOAD} octets de données."
        ),
        instructions=("Calcule la taille du segment, du paquet et de la trame, en tenant compte du minimum Ethernet.",),
        criteria=(
            _c("Segment et paquet", 1, f"Segment {X03.segment} octets ; paquet {X03.segment} + {IPV4_HEADER} = {X03.packet} octets."),
            _c("Trame", 1, f"{X03.packet} < {ETH_MIN_PAYLOAD} : bourrage de {X03.padding} octets ; trame {ETH_HEADER} + {ETH_MIN_PAYLOAD} + {ETH_FCS} = {X03.frame} octets."),
        ),
        correction=(
            f"Sans donnée, le segment ne contient que l'en-tête TCP : {X03.segment} octets. Le paquet IP : {X03.segment} + {IPV4_HEADER} = {X03.packet} octets.",
            f"Une trame doit transporter au moins {ETH_MIN_PAYLOAD} octets : on ajoute {X03.padding} octets de bourrage. Trame : {ETH_HEADER} + {ETH_MIN_PAYLOAD} + {ETH_FCS} = {X03.frame} octets, la taille minimale d'une trame Ethernet.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Quelle adresse MAC de destination ?",
        question_type="document_analysis",
        requirement_ids=("AP-29", "AP-31"),
        kind=KIND_LAYERS,
        context=(
            f"Le poste {PC.owner} ({PC.ip}/24, passerelle {BOX_LAN.ip}) envoie d'abord un fichier au poste "
            f"{PC_PEER.owner} ({PC_PEER.ip}), puis ouvre le site {SERVER_NAME} ({SERVER_IP}). Le document 1 "
            "montre sa table ARP."
        ),
        documents=(_console("Document 1 — Table ARP du poste (capture fictive)", *ARP_LINES),),
        instructions=("Pour chaque envoi, donne l'adresse MAC de destination de la trame émise par le poste et justifie.",),
        criteria=(
            _c("Envoi local", 1, f"{X04_LOCAL.dst_mac} : {PC_PEER.ip} est dans le même réseau, la trame va directement à {PC_PEER.owner}."),
            _c("Envoi vers Internet", 1, f"{X04_REMOTE.dst_mac} : {SERVER_IP} est hors du réseau, la trame va à la passerelle (box) ; l'IP de destination reste {SERVER_IP}."),
        ),
        correction=(
            f"{PC_PEER.ip} appartient au réseau {PC.ip}/24 : le poste envoie la trame directement à {PC_PEER.owner}, dont l'adresse MAC est dans la table ARP ({X04_LOCAL.dst_mac.lower()}).",
            f"{SERVER_IP} n'est pas dans le réseau local : le poste envoie la trame à sa passerelle {BOX_LAN.ip}, MAC {X04_REMOTE.dst_mac.lower()} ; dans le paquet, l'adresse IP de destination reste celle du serveur. La box fera suivre.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Compter les domaines d'un bureau",
        question_type="short_answer",
        requirement_ids=("AP-31", "AP-23"),
        kind=KIND_EQUIPMENT,
        context=(
            f"Dans un bureau d'études, un switch relie {X05_PCS_SWITCH} postes et la box (routeur). Sur un "
            f"port du switch, un ancien hub relie encore {X05_PCS_HUB} postes de la salle de dessin. Tous "
            "les postes sont dans le même réseau IP ; aucun VLAN n'est configuré."
        ),
        instructions=("Compte les domaines de collision et les domaines de diffusion du réseau local, en justifiant.",),
        criteria=(
            _c("Collisions", 1, f"{X05_COLLISIONS} : {X05_PCS_SWITCH} postes + la box + la liaison vers le hub (qui forme un seul domaine avec ses {X05_PCS_HUB} postes)."),
            _c("Diffusions", 1, f"{X05_BROADCASTS} : un switch et un hub ne séparent pas les diffusions ; seule la box (routeur) les arrête."),
        ),
        correction=(
            f"Chaque port utilisé du switch est un domaine de collision : {X05_PCS_SWITCH} postes, la box et le hub, soit {X05_PCS_SWITCH + 2} ports. Le hub recopie les bits sur tous ses ports : lui, ses {X05_PCS_HUB} postes et sa liaison vers le switch ne forment qu'un domaine. Total : {X05_COLLISIONS}.",
            f"Le switch et le hub laissent passer les diffusions : tout le réseau local forme {X05_BROADCASTS} domaine de diffusion, arrêté par la box.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Switch ou routeur pour le nouvel étage ?",
        question_type="short_answer",
        requirement_ids=("AP-31",),
        kind=KIND_EQUIPMENT,
        context=(
            "Une agence occupe le rez-de-chaussée (réseau 192.168.1.0/24, box 192.168.1.1). Elle reprend "
            "l'étage, déjà câblé par le locataire précédent en 192.168.2.0/24. Le gérant veut garder les "
            "deux réseaux séparés tout en partageant l'imprimante du rez. Il hésite entre un switch et un "
            "routeur."
        ),
        instructions=("Choisis l'équipement et justifie, puis indique la passerelle par défaut des postes de l'étage.",),
        criteria=(
            _c("Choix", 1, "Routeur (couche 3) : relie deux réseaux IP différents, garde les diffusions séparées, peut filtrer ; un switch ne route pas."),
            _c("Passerelle", 1, "Les postes de l'étage prennent pour passerelle l'adresse du routeur dans leur réseau (par exemple 192.168.2.1)."),
        ),
        correction=(
            "Deux réseaux IP différents ne se joignent que par un routeur : il lit l'adresse IP et fait passer les paquets d'un réseau à l'autre, tout en gardant deux domaines de diffusion séparés. Un switch relierait les câbles mais pas les réseaux IP.",
            "Le routeur a une interface dans chaque réseau ; la passerelle par défaut des postes de l'étage est l'adresse du routeur côté étage (par exemple 192.168.2.1) ; une règle peut n'autoriser que l'imprimante du rez.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="NetBEUI et routeur",
        question_type="short_answer",
        requirement_ids=("AP-29",),
        kind=KIND_LAYERS,
        context=(
            "Un musée possède deux vieux PC d'inventaire sous Windows 98 qui partagent un fichier en "
            "NetBEUI. On veut déplacer l'un d'eux dans le bâtiment voisin, dont le réseau est relié au "
            "premier par un routeur. Le conservateur demande si cela fonctionnera tel quel."
        ),
        instructions=("Réponds au conservateur en justifiant, et propose une solution.",),
        criteria=(
            _c("Réponse justifiée", 1, "Non : NetBEUI n'a pas d'adresse réseau, il n'est pas routable et repose sur la diffusion, que le routeur arrête."),
            _c("Solution", 1, "Utiliser TCP/IP (routable) sur les deux postes ou migrer l'inventaire vers un système actuel ; à défaut, garder les deux PC dans le même réseau local."),
        ),
        correction=(
            "Cela ne fonctionnera pas : NetBEUI désigne les postes par un nom NetBIOS, sans adresse de réseau ; il est non routable : un routeur ne peut pas l'acheminer et il arrête les diffusions dont NetBEUI dépend.",
            "Solution : configurer TCP/IP sur les deux postes (Windows 98 le permet) ou, mieux, migrer l'inventaire vers un système actuel ; à défaut, laisser les deux PC dans le même réseau local.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Le ping répond mais pas le site",
        question_type="document_analysis",
        requirement_ids=("AP-29",),
        kind=KIND_DIAG,
        context=(
            "Dans une mutuelle, l'intranet https://intranet.mutuelle.lan ne s'ouvre plus depuis le service "
            "comptable. Le technicien a fait les relevés du document 1 depuis un poste de ce service."
        ),
        documents=(
            _console(
                "Document 1 — Relevés (capture fictive)",
                "PS C:\\> Resolve-DnsName intranet.mutuelle.lan",
                "intranet.mutuelle.lan   A   192.168.30.12",
                "PS C:\\> Test-NetConnection 192.168.30.12",
                "PingSucceeded    : True",
                "PS C:\\> Test-NetConnection 192.168.30.12 -Port 443",
                "TcpTestSucceeded : False",
            ),
        ),
        instructions=("Indique la couche en défaut, justifie par les relevés et propose la correction.",),
        criteria=(
            _c("Diagnostic", 1, "Nom résolu (DNS correct) et ping réussi (couche 3) ; le port 443 (HTTPS) ne répond pas : couche 4, pare-feu ou service web arrêté."),
            _c("Correction", 1, "Vérifier que le service web écoute sur 443 et la règle du pare-feu (serveur ou routeur) pour le réseau comptable ; retester le port puis le site."),
        ),
        correction=(
            "Le nom est traduit en 192.168.30.12 et le serveur répond au ping : le DNS et le réseau IP fonctionnent. Le test du port 443, celui de HTTPS, échoue : le problème est à la couche transport, un pare-feu bloque le port ou le service web n'écoute plus.",
            "On vérifie sur le serveur que le service web est démarré et écoute sur 443, puis la règle du pare-feu (serveur ou routeur) pour le réseau comptable ; on reteste le port puis l'ouverture du site et on consigne.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Corriger un rapport qui confond tout",
        question_type="long_answer",
        requirement_ids=("AP-29", "AP-31"),
        kind=KIND_LAYERS,
        context=(
            "Un stagiaire a écrit dans son rapport : « Le protocole switch ne donnait plus d'adresses, j'ai "
            "redémarré l'équipement DHCP. Le service routeur bloquait le protocole 443. » Le client ne "
            "comprend rien. En réalité, la box (routeur avec serveur DHCP) ne distribuait plus d'adresses "
            "et son pare-feu bloquait le port TCP 443."
        ),
        instructions=("Réécris ces trois phrases correctement en employant protocole, service, équipement et port à bon escient.",),
        criteria=(
            _c("Termes corrigés", 1.5, "Switch et box = équipements ; DHCP = service (serveur DHCP de la box) qui suit le protocole DHCP ; 443 = port TCP du protocole HTTPS, pas un protocole (0,5 pt par phrase)."),
            _c("Clarté pour le client", 0.5, "Phrases compréhensibles : quel équipement, quel service, quelle action, quel port."),
        ),
        correction=(
            "Proposition : « Le service DHCP de la box ne distribuait plus d'adresses aux postes ; j'ai redémarré la box (l'équipement), ce qui a relancé le service. Le pare-feu de la box bloquait le port TCP 443, utilisé par le protocole HTTPS ; j'ai rétabli la règle. »",
            "Un switch est un équipement, il ne distribue pas d'adresses. DHCP est un protocole ; le serveur DHCP de la box est un service. 443 est un numéro de port, pas un protocole.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Anneau ou maillage entre six sites",
        question_type="short_answer",
        requirement_ids=("AP-23",),
        kind=KIND_TOPO,
        context=(
            f"Une intercommunale veut relier les routeurs de {X10_SITES} bâtiments. Le bureau d'études compare un "
            "anneau simple (chaque bâtiment relié au suivant, le dernier au premier) et un maillage "
            "complet. Chaque liaison est une fibre à poser."
        ),
        instructions=("Calcule le nombre de liaisons de chaque solution et compare leur comportement en cas de coupure.",),
        criteria=(
            _c("Calculs", 1, f"Anneau : {X10_SITES} liaisons ; maillage complet : {X10_SITES} × {X10_SITES - 1} ÷ 2 = {X10_MESH} liaisons."),
            _c("Comparaison", 1, "Anneau simple : une coupure interrompt la circulation (ou laisse un seul chemin si les routeurs savent reboucler) ; maillage : plusieurs chemins, coupure sans effet, mais coût beaucoup plus élevé."),
        ),
        correction=(
            f"Anneau : une liaison par bâtiment, soit {X10_SITES}. Maillage complet : {X10_SITES} × {X10_SITES - 1} ÷ 2 = {X10_MESH} liaisons, deux fois et demie plus de fibre.",
            "Un anneau simple est fragile : une coupure interrompt la circulation ; avec des routeurs qui savent repartir dans l'autre sens, il reste un seul chemin. Le maillage complet garde plusieurs chemins mais coûte bien plus ; un anneau double ou un maillage partiel est un compromis.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, schémas à compléter et choix d'équipement demandés par le ticket."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
            or len(set(item.classification.correct)) != len(item.classification.categories)
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
        if not REQ & set(item.requirement_ids):
            errors.append(f"{item.key} : au moins une exigence du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 6:
        errors.append("Ticket #220 : six schémas à compléter attendus.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_EQUIPMENT) < 5:
        errors.append("Ticket #220 : au moins 5 choix d'équipement ou de topologie.")
    if E17_LOCAL or crosses_router("NetBEUI") or not crosses_router("TCP/IP"):
        errors.append("E17/E18 : données d'adressage ou de routage incohérentes.")
    return errors

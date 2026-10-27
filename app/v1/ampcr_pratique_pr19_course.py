"""Cours PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements » — parcours AMPCR pratique
écrite (ticket #220).

Matière : intégralement celle du ticket #220 (topologies bus, étoile, anneau, maillage, avantages,
défauts et pannes ; 7 couches OSI, encapsulation et couches TCP/IP ; Ethernet 802.3,
MAC/ARP/IP/TCP/UDP, adresses et ports ; NetBEUI historique non routable ; hub L1, bridge/switch L2,
routeur L3, passerelle, modem, point d'accès et répéteur ; collisions et diffusion, VLAN en
complément ; chemin d'un paquet PC → switch → routeur → Internet ; diagnostic par couche ; ne pas
confondre protocole, service et équipement ; cinq cas résolus), découpée en blocs titrés (le
titre pilote le type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient
« examen », « source », « ressource », « exemple », « exercice », « méthode », « piège »,
« attention », « transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr19_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr19_bank`.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr19_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr19_figures import (
    ARP_LINES,
    BOX_LAN,
    BOX_WAN,
    BROADCAST_MAC,
    BUS_4,
    CHOICE_FIGURE,
    DEVICES,
    DEVICES_FIGURE,
    DIAG_FIGURE,
    DOMAINS_BROADCASTS,
    DOMAINS_COLLISIONS,
    DOMAINS_FIGURE,
    DOUBLE_RING_5,
    ENCAP_EXAMPLE,
    ENCAP_FIGURE,
    ETH_FCS,
    ETH_HEADER,
    ETH_MAX_FRAME,
    ETH_MIN_FRAME,
    ETH_MIN_PAYLOAD,
    ETH_MTU,
    ETHERTYPES,
    FRAME_FIGURE,
    IPV4_HEADER,
    ISP_ROUTER,
    LAYER_CHECKS,
    MESH_4,
    NETBEUI_FACTS,
    OSI_FIGURE,
    OSI_LAYERS,
    PATH_FIGURE,
    PATH_FRAMES,
    PATH_STEPS_FIGURE,
    PC,
    PC_PEER,
    PORTS,
    PREAMBLE,
    PROCEDURES,
    PROTOCOL_SUITES,
    PSE_DEFINITIONS,
    RING_5,
    SERVER_IP,
    SERVER_NAME,
    STAR_5,
    STATIC_FIGURES,
    TCP_MSS,
    TCPIP_LAYERS,
    TOPO_FIGURE,
    TOPOLOGIES,
    TRANSPORT_HEADER,
    TREE,
    WRITTEN_AT,
    encapsulate,
    isolated_stations,
    lan_frame,
    mesh_links,
    octets,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR19_TITLE = "Topologies, OSI, TCP/IP, NetBEUI et équipements"
PR19_SLUG = "ampcr-pratique-pr19"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr19")
    for document in item.documents:
        if document.image:
            text = f'<p class="jc-pr-doc-text">{escape(document.content_text)}</p>'
            figure = str(render_figure(_SCHEMAS_BY_PATH[document.image]))
            html = html.replace(text, figure + text, 1)
    return html


def _exercises_html() -> str:
    return "\n\n".join(_card(i, item) for i, item in enumerate(PRACTICE_ITEMS, start=1))


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _topologies_table() -> str:
    rows = "\n".join(
        f"| **{t.name}** | {t.principle} | {t.advantages} | {t.drawbacks} | {t.failure} |" for t in TOPOLOGIES
    )
    return "| Topologie | Principe | Avantages | Défauts | Effet d'une panne |\n|---|---|---|---|---|\n" + rows


def _osi_table() -> str:
    rows = "\n".join(
        f"| **{layer.number}** | **{layer.name}** | {layer.role} | {layer.pdu} | {layer.protocols} | {layer.equipment} |"
        for layer in OSI_LAYERS
    )
    return "| N° | Couche | Rôle | Unité | Exemples | Équipement |\n|---|---|---|---|---|---|\n" + rows


def _tcpip_table() -> str:
    rows = "\n".join(
        f"| **{name}** | {', '.join(str(c) for c in covered)} | {protocols} |" for name, covered, protocols in TCPIP_LAYERS
    )
    return "| Couche TCP/IP | Couches OSI correspondantes | Protocoles |\n|---|---|---|\n" + rows


def _encap_table() -> str:
    lines = [encapsulate(TCP_MSS, "TCP"), encapsulate(40, "UDP"), encapsulate(0, "TCP")]
    rows = "\n".join(
        f"| {e.transport}, {octets(e.data)} o de données | {octets(e.segment)} | {octets(e.packet)} | "
        f"{e.padding or '—'} | **{octets(e.frame)}** |"
        for e in lines
    )
    return "| Cas | Segment (o) | Paquet (o) | Bourrage (o) | Trame (o) |\n|---|---|---|---|---|\n" + rows


def _ports_table() -> str:
    rows = "\n".join(
        f"| **{p.name}** | {p.transport} | {', '.join(str(n) for n in p.ports)} | {p.role} |" for p in PORTS
    )
    return "| Protocole | Transport | Port(s) | Usage |\n|---|---|---|---|\n" + rows


def _pse_table() -> str:
    rows = "\n".join(f"| **{kind}** | {definition} | {examples} |" for kind, definition, examples in PSE_DEFINITIONS)
    return "| Notion | Définition | Exemples |\n|---|---|---|\n" + rows


def _devices_table() -> str:
    rows = "\n".join(
        f"| **{d.name}** | {d.layer} | {d.role} | {d.reads} | {d.collisions} | {d.broadcasts} |" for d in DEVICES
    )
    return (
        "| Équipement | Couche | Rôle | Lit pour décider | Domaines de collision | Domaines de diffusion |\n"
        "|---|---|---|---|---|---|\n" + rows
    )


def _suites_table() -> str:
    rows = "\n".join(
        f"| **{name}** | {'oui' if routable else '**non**'} | {addressing} | {usage} |"
        for name, routable, addressing, usage in PROTOCOL_SUITES
    )
    return "| Suite de protocoles | Routable | Adressage | Usage |\n|---|---|---|---|\n" + rows


def _checks_table() -> str:
    rows = "\n".join(f"| **{layer}** | {what} | {tool} |" for layer, what, tool in LAYER_CHECKS)
    return "| Couche | Ce qu'on contrôle | Outil ou indice |\n|---|---|---|\n" + rows


def _frames_table() -> str:
    first, second = PATH_FRAMES
    labels = (("MAC source", "src_mac"), ("MAC destination", "dst_mac"), ("IP source", "src_ip"), ("IP destination", "dst_ip"))
    rows = "\n".join(f"| {label} | {getattr(first, f)} | {getattr(second, f)} |" for label, f in labels)
    return "| Champ | Trame 1 : PC → box | Trame 2 : box → opérateur |\n|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1))


def _console_block(lines: tuple[str, ...]) -> str:
    return '<pre class="jc-pr-console" tabindex="0">' + escape("\n".join(lines)) + "</pre>"


# --- Pannes calculées sur les modèles de topologie ---------------------------------------------

STAR_CABLE = len(isolated_stations(STAR_5, link=("SW", "PC3")))
STAR_CENTER = len(isolated_stations(STAR_5, node="SW"))
BUS_CUT = len(isolated_stations(BUS_4, link=("PC2", "PC3")))
RING_CUT = len(isolated_stations(RING_5, link=("PC1", "PC2")))
DOUBLE_RING_CUT = len(isolated_stations(DOUBLE_RING_5, link=("PC1", "PC2")))
MESH_CUT = len(isolated_stations(MESH_4, link=("R1", "R2")))
TREE_FLOOR = sorted(isolated_stations(TREE, node="SW2"))

# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C3_FIRST, C3_SECOND = PATH_FRAMES
C3_LOCAL = lan_frame(PC, PC_PEER.ip)

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Atelier en bus coaxial et logiciel NetBEUI",
        (
            "Une imprimerie relie encore cinq PC par un câble coaxial (T BNC, bouchons) ; son logiciel de "
            "planning échange en NetBEUI. Chaque fois qu'un PC est déplacé, tout l'atelier perd le réseau. "
            "Le patron veut aussi consulter le planning depuis le bureau, dans un autre réseau IP relié "
            "par un routeur."
        ),
        (
            f"**Topologie** : bus ; {TOPOLOGIES[0].failure} — un câble coupé arrête ici {BUS_CUT} postes sur {len(BUS_4.stations)}.",
            "**Protocole** : NetBEUI n'a pas d'adresse réseau, il est non routable : il ne passera jamais le routeur vers le bureau.",
            f"**Proposition** : étoile (switch, un câble à paires torsadées par poste : une coupure n'isole que {STAR_CABLE} poste) et logiciel en TCP/IP.",
        ),
        "Passer en étoile avec un switch et faire migrer le logiciel vers TCP/IP : coupure limitée à un poste et planning accessible depuis le bureau à travers le routeur.",
    ),
    (
        "Cas 2 — Équiper une PME de A à Z",
        (
            "Une fiduciaire de 12 personnes reçoit une ligne VDSL. Il faut relier 12 postes, 2 imprimantes, "
            "un serveur de fichiers, donner le Wi-Fi au personnel et aux visiteurs, et isoler le réseau "
            "des visiteurs."
        ),
        (
            "**Ligne** : modem VDSL (dans la box) ; **routeur avec NAT** (box) vers Internet ; le serveur DHCP de la box est un **service**.",
            "**Réseau local** : switch 24 ports (couche 2) pour 15 appareils câblés + réserve ; point d'accès Wi-Fi (couche 2) au plafond.",
            "**Visiteurs** : réseau Wi-Fi invités séparé (VLAN ou fonction invités de la box) : un autre domaine de diffusion, sans accès au serveur.",
        ),
        "Box (modem + routeur NAT + DHCP), switch 24 ports, point d'accès avec un réseau invités séparé ; chaque choix justifié par la couche et le rôle.",
    ),
    (
        "Cas 3 — Suivre un paquet jusqu'au site web",
        (
            f"Le poste {PC.owner} ({PC.ip}/24, passerelle {BOX_LAN.ip}) ouvre {SERVER_NAME} ({SERVER_IP}). Le "
            "client veut comprendre ce que voient le switch, la box et l'opérateur."
        ),
        (
            f"**Local ou distant ?** {SERVER_IP} n'est pas dans {PC.ip}/24 → trame vers la passerelle : ARP donne {BOX_LAN.mac}.",
            f"**Trame 1** : MAC {C3_FIRST.src_mac} → {C3_FIRST.dst_mac} ; IP {C3_FIRST.src_ip} → {C3_FIRST.dst_ip}. Le switch lit la MAC et n'envoie que vers la box.",
            f"**Trame 2** : MAC {C3_SECOND.src_mac} → {C3_SECOND.dst_mac} ; IP {C3_SECOND.src_ip} (NAT) → {C3_SECOND.dst_ip}.",
        ),
        f"Les adresses MAC changent à chaque routeur, l'IP de destination {SERVER_IP} reste la même ; la box remplace l'IP source privée par {BOX_WAN.ip}. Vers {PC_PEER.owner}, la trame irait directement à {C3_LOCAL.dst_mac}.",
    ),
    (
        "Cas 4 — Un hub qui ralentit tout",
        (
            "Dans un bureau d'études, un vieux hub relie encore quatre postes de dessin derrière le switch. "
            "Les transferts de plans sont lents et le voyant de collision du hub clignote sans arrêt."
        ),
        (
            f"**Domaines** (schéma « Domaines de collision et de diffusion ») : le hub et ses liaisons forment un seul domaine de collision ; le réseau compte {DOMAINS_COLLISIONS} domaines de collision et {DOMAINS_BROADCASTS} de diffusion.",
            "**Cause** : le hub recopie tout sur tous ses ports, en semi-duplex, débit partagé : collisions.",
            "**Correction** : switch à la place du hub : une liaison = un domaine, duplex intégral ; les diffusions restent dans le même domaine (VLAN ou routeur pour les séparer).",
        ),
        "Remplacer le hub par un switch : les collisions disparaissent, chaque poste dispose du débit complet ; le domaine de diffusion est inchangé.",
    ),
    (
        "Cas 5 — L'intranet ne s'ouvre pas : diagnostic par couche",
        (
            "Dans une mutuelle, un poste n'ouvre plus l'intranet. Le technicien a relevé : voyant allumé ; "
            "adresse, masque et passerelle corrects ; ping de la passerelle et du serveur réussis ; nom "
            "résolu ; test du port 443 en échec."
        ),
        (
            "**Couches 1 à 3** : voyant, adresse, ping de la passerelle et du serveur → correctes.",
            "**Couche 4** : le port 443 (HTTPS) ne répond pas → pare-feu ou service web arrêté.",
            "**Action** : vérifier le service web et la règle du pare-feu, retester le port puis le site, consigner.",
        ),
        "Défaut à la couche transport : port 443 bloqué par le pare-feu du serveur ; règle corrigée, port et site retestés, intervention consignée.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant un schéma de réseau, un relevé ou une demande de client, on attend que tu
**raisonnes avec les couches** : reconnaître une topologie et ses faiblesses, situer un
protocole, une panne ou un équipement dans le modèle OSI, choisir le bon équipement et
**justifier** ton choix. Tu dois savoir :

1. reconnaître les **topologies** bus, étoile, anneau et maillage, leurs avantages, leurs défauts
   et l'effet d'une panne ;
2. expliquer les **7 couches OSI**, les **4 couches TCP/IP** et l'**encapsulation** ;
3. lire une **trame Ethernet** et suivre les adresses **MAC**, **IP** et les **ports** **TCP/UDP** ;
4. distinguer **protocole**, **service** et **équipement** ;
5. situer **NetBEUI**, protocole historique **non routable** ;
6. choisir entre **hub, répéteur, pont, switch, routeur, passerelle, modem et point d'accès** ;
7. compter les **domaines de collision et de diffusion** (VLAN en complément) ;
8. suivre le **chemin d'un paquet** PC → switch → routeur → Internet ;
9. mener un **diagnostic couche par couche**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-23")}
{_req("AP-29")}
{_req("AP-31")}

Ce sont trois exigences **officielles** (consignes, p. 6). Le bus coaxial est détaillé en
[PR16](/uaa/ampcr-pratique-pr16), l'installation en étoile en [PR18](/uaa/ampcr-pratique-pr18),
les adresses IP, masques et passerelles en [PR20](/uaa/ampcr-pratique-pr20) et le dépannage
réseau complet en [PR24](/uaa/ampcr-pratique-pr24). La connexion directe de deux PC (PR21), les
partages (PR23) et le Wi-Fi (PR25) seront approfondis dans leurs cours, publiés ensuite dans
l'ordre du parcours.

## Lien avec la théorie

Les mêmes notions sont présentées dans la théorie AMPCR :
[MC13 Fondamentaux réseau](/uaa/ampcr-mc13), [MC14 Équipements réseau](/uaa/ampcr-mc14),
[MC21 TCP, UDP et ports](/uaa/ampcr-mc21) et [MC23 Switching et topologies](/uaa/ampcr-mc23).
Ce cours-ci est **pratique** : schémas à compléter, relevés à analyser, équipements à choisir,
comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont six **schémas à compléter**
et cinq **choix d'équipement ou de topologie**), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les réseaux, adresses, relevés et captures de ce cours sont des **supports
> fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). Les adresses publiques
> viennent des blocs réservés à la documentation (RFC 5737) ; les tailles d'en-têtes et les
> ports viennent des normes nommées dans les sources. Aucun exercice n'est une question
> officielle ni une question déjà posée par le Jury.
"""


def _topologies() -> str:
    return f"""**Objectifs** : reconnaître une topologie sur un schéma, citer ses avantages et ses défauts,
prévoir l'effet d'une panne.

## 1.1 Les quatre topologies

La **topologie** décrit la façon dont les équipements sont reliés.

{_fig(TOPO_FIGURE)}

{_topologies_table()}

## 1.2 Effet d'une panne, calculé sur les schémas

- **étoile** de 5 postes : un câble coupé isole **{STAR_CABLE}** poste ; le switch central en panne
  isole les **{STAR_CENTER}** ;
- **étoile étendue** (switch principal + deux switchs d'étage) : la panne d'un switch d'étage
  isole ses postes ({", ".join(TREE_FLOOR)}), pas ceux de l'autre étage ;
- **bus** de 4 postes : un câble coupé arrête les **{BUS_CUT}** postes (réflexions, PR16) ;
- **anneau simple** de 5 postes : une liaison coupée arrête les **{RING_CUT}** ; **anneau double** :
  rebouclage, **{DOUBLE_RING_CUT}** poste isolé ;
- **maillage complet** de 4 routeurs ({mesh_links(4)} liaisons) : une liaison coupée isole
  **{MESH_CUT}** routeur, le trafic prend un autre chemin.

Nombre de liaisons : étoile = une par station ; anneau = une par station ; maillage complet de
n équipements = **n × (n − 1) ÷ 2** (5 sites : {mesh_links(5)} ; 6 sites : {mesh_links(6)}).

## 1.3 Topologie physique et topologie logique

La **topologie physique** est le câblage ; la **topologie logique** est la façon dont les
données circulent. Un **hub** Ethernet est câblé en étoile, mais tout poste reçoit tout : bus
logique. Token Ring était câblé en étoile autour d'un concentrateur, avec un anneau logique.
Aujourd'hui : étoile physique (ou étoile étendue) dans les bâtiments, maillage entre routeurs
et sites.

**Procédure professionnelle (à rédiger)** : repérer sur le schéma l'équipement central ou le
câble commun → nommer la topologie → dire ce qu'une coupure arrête → proposer une amélioration
(étoile, chemin de secours).

**Erreur fréquente** : confondre « tout passe par un point central » (étoile) et « tout passe
par un câble commun » (bus) ; oublier que l'étoile a un point unique de panne.

**À l'écrit** : « bus : bouchon absent → tout le segment s'arrête ; étoile : seul le poste du
câble coupé est isolé ».

**Repère rapide** : **bus = un câble commun · étoile = un câble par poste · anneau = de
station en station · maillage = plusieurs chemins**. Exercices liés : {_ex("E04", "E09", "E20")}.
"""


def _models() -> str:
    return f"""**Objectifs** : situer un protocole, un équipement ou une panne dans le modèle OSI et dans le
modèle TCP/IP.

## 2.1 Le modèle OSI à 7 couches

Le modèle **OSI** (norme ISO) découpe la communication en **sept couches**. Chaque couche rend un
service à celle du dessus et utilise celle du dessous. C'est un **outil de raisonnement** : on
s'en sert pour situer une panne et pour choisir un équipement.

{_osi_table()}

Pour retenir l'ordre de 1 à 7 : **P**hysique, **L**iaison, **R**éseau, **T**ransport,
**S**ession, **P**résentation, **A**pplication.

## 2.2 Le modèle TCP/IP à 4 couches

La pile réellement utilisée sur les réseaux est **TCP/IP** ; son modèle compte **quatre
couches** :

{_tcpip_table()}

{_fig(OSI_FIGURE)}

**Procédure professionnelle (à rédiger)** : pour un élément (protocole, équipement, panne), se
demander ce qu'il manipule (bits, trames et MAC, paquets et IP, ports, données du service) → en
déduire la couche OSI → donner la couche TCP/IP correspondante.

**Erreur fréquente** : réciter les sept noms sans savoir ce que fait chaque couche ; placer DNS
ou DHCP à la couche réseau (ce sont des protocoles d'application, transportés par UDP).

**À l'écrit** : « le routeur lit l'adresse IP : couche 3, réseau (Internet en TCP/IP) ».

**Repère rapide** : **1 bits · 2 trames et MAC · 3 paquets et IP · 4 ports (TCP/UDP) · 7
services**. Exercices liés : {_ex("E06", "E10")}.
"""


def _encapsulation() -> str:
    e = ENCAP_EXAMPLE
    return f"""**Objectifs** : décrire l'encapsulation, lire une trame Ethernet et calculer la taille d'une
trame.

## 3.1 Encapsuler et décapsuler

À l'émission, chaque couche **ajoute son en-tête** devant les données de la couche du dessus :
données → **segment** (TCP) ou **datagramme** (UDP) → **paquet** (IP) → **trame** (Ethernet, avec
un **FCS** à la fin) → **bits**. À la réception, chaque couche lit et retire son en-tête
(**décapsulation**).

{_fig(ENCAP_FIGURE)}

Avec les en-têtes sans option (TCP {TRANSPORT_HEADER["TCP"]}, UDP {TRANSPORT_HEADER["UDP"]}, IPv4 {IPV4_HEADER},
Ethernet {ETH_HEADER} + FCS {ETH_FCS} octets) : {octets(e.data)} octets de données → segment {octets(e.segment)} →
paquet {octets(e.packet)} (la **MTU** Ethernet, taille maximale du paquet) → trame {octets(e.frame)} octets. Une
trame transporte au moins {ETH_MIN_PAYLOAD} octets : en dessous, on ajoute un **bourrage**.

{_encap_table()}

## 3.2 La trame Ethernet (IEEE 802.3)

{_fig(FRAME_FIGURE)}

- **adresse MAC de destination** (6 octets) : lue par le switch pour choisir le port ;
  {BROADCAST_MAC} = **diffusion** à tout le réseau local ;
- **adresse MAC source** (6 octets) : apprise par le switch dans sa table MAC ;
- **type** (2 octets) : ce que transportent les données ({", ".join(f"{c} {n}" for c, n in ETHERTYPES)}) ;
- **données** : {ETH_MIN_PAYLOAD} à {octets(ETH_MTU)} octets ;
- **FCS** (4 octets) : contrôle d'erreur ; une trame abîmée est jetée.

Trame de **{ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)} octets** ; le préambule ({PREAMBLE} octets) qui la précède n'est pas
compté. Le détail des adresses MAC (format, constructeur) est en [PR20](/uaa/ampcr-pratique-pr20).

**Procédure professionnelle (à rédiger)** : partir des données → ajouter l'en-tête de transport →
l'en-tête IP → l'en-tête Ethernet et le FCS → vérifier le minimum ({ETH_MIN_PAYLOAD} octets de données) et le
maximum ({octets(ETH_MTU)}).

**Erreur fréquente** : oublier le FCS ; oublier le bourrage d'une petite trame ; compter le
préambule.

**À l'écrit** : « 40 + 8 = 48 ; 48 + 20 = 68 ; 14 + 68 + 4 = 86 octets, pas de bourrage ».

**Repère rapide** : **TCP 20 · UDP 8 · IP 20 · Ethernet 14 + 4 · trame {ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)}**.
Exercices liés : {_ex("E03", "E11", "E14")}.
"""


def _addresses() -> str:
    return f"""**Objectifs** : utiliser les adresses MAC et IP, le rôle d'ARP, les ports TCP/UDP ; ne pas
confondre protocole, service et équipement.

## 4.1 Trois niveaux d'adresses

- **adresse MAC** (couche 2) : gravée dans la carte réseau, 6 octets ; elle ne sert **qu'à
  l'intérieur d'un réseau local** ;
- **adresse IP** (couche 3) : logique, choisie ou attribuée (DHCP) ; elle désigne le poste
  **de bout en bout**, d'un réseau à l'autre ;
- **port** (couche 4) : numéro qui désigne le **programme** dans le poste (443 pour un serveur
  web chiffré).

**ARP** fait le lien entre IP et MAC : pour envoyer une trame à {BOX_LAN.ip}, le poste diffuse
« qui a l'adresse {BOX_LAN.ip} ? » ; la box répond avec sa MAC, gardée dans la **table ARP** :

{_console_block(ARP_LINES)}

*Capture fictive (présentation simplifiée) : `arp -a` sous Windows.*

## 4.2 TCP ou UDP

**TCP** établit une connexion, numérote les données, attend des **accusés de réception** et
renvoie ce qui est perdu : fiable (web, courrier, fichiers). **UDP** envoie sans connexion ni
accusé : plus léger (DNS, DHCP, voix, vidéo en direct). Ports courants :

{_ports_table()}

## 4.3 Protocole, service, équipement

{_pse_table()}

On écrit « le **service** DHCP de la **box** (équipement) suit le **protocole** DHCP sur le
**port** UDP 67 » — jamais « l'équipement DHCP » ni « le protocole switch ».

**Procédure professionnelle (à rédiger)** : pour chaque mot d'un rapport, se demander : est-ce
une règle (protocole), une fonction rendue par un programme (service) ou un matériel
(équipement) ? → réécrire la phrase avec le bon mot.

**Erreur fréquente** : croire que le switch lit les adresses IP ; appeler « protocole » un numéro
de port ; ouvrir un port vers Internet « pour voir ».

**À l'écrit** : « l'envoi de courrier échoue : TCP 587 bloqué par le pare-feu (couche 4) ».

**Repère rapide** : **MAC = dans le réseau local · IP = de bout en bout · port = le programme ·
ARP = IP → MAC**. Exercices liés : {_ex("E05", "E12", "E19")}.
"""


def _netbeui() -> str:
    facts = "\n".join(f"- {fact}" for fact in NETBEUI_FACTS)
    return f"""**Objectifs** : situer NetBEUI dans l'histoire des réseaux et expliquer pourquoi il ne traverse
pas un routeur.

## 5.1 Ce qu'il faut savoir

{facts}

## 5.2 Comparaison avec TCP/IP

{_suites_table()}

Un **routeur** choisit le chemin d'après l'**adresse de réseau** du destinataire. NetBEUI n'en a
pas : il est **non routable**, et ses diffusions sont arrêtées par le routeur. Deux postes
NetBEUI ne communiquent donc que dans le **même réseau local**. Dans un dossier d'examen, on le
rencontre sur une installation ancienne à moderniser ; la réponse attendue est **TCP/IP**.

**Procédure professionnelle (à rédiger)** : repérer le protocole utilisé par l'application
ancienne → vérifier si un routeur sépare les postes → expliquer le blocage (non routable) →
proposer TCP/IP (mise à jour ou remplacement), avec sauvegarde et essai.

**Erreur fréquente** : chercher une panne de câble ou de routeur alors que le protocole lui-même
ne peut pas traverser ; confondre NetBEUI (protocole) et NetBIOS (interface de noms, encore
utilisée par-dessus TCP/IP).

**À l'écrit** : « NetBEUI : pas d'adresse réseau, non routable → bloqué par le routeur → passer
le logiciel en TCP/IP ».

**Repère rapide** : **NetBEUI = noms NetBIOS · diffusion · non routable · remplacé par TCP/IP**.
Exercices liés : {_ex("E18")}.
"""


def _devices() -> str:
    return f"""**Objectifs** : décrire le rôle et la couche de chaque équipement, choisir le bon équipement
pour un besoin.

## 6.1 Les équipements

{_devices_table()}

{_fig(DEVICES_FIGURE)}

**Passerelle** : dans la configuration IP d'un poste, la **passerelle par défaut** est l'adresse
du **routeur** de son réseau (souvent la box) ; au sens large, une passerelle traduit entre deux
protocoles différents. La **box** réunit modem, routeur avec NAT, petit switch, point d'accès,
serveurs DHCP et DNS.

## 6.2 Choisir l'équipement

{_fig(CHOICE_FIGURE)}

**Procédure professionnelle (à rédiger)** : les cinq étapes ci-dessus — besoin, couche,
équipement, chiffres, justification.

**Erreur fréquente** : acheter un switch pour relier deux réseaux IP ; garder un hub ; placer un
répéteur Wi-Fi là où un point d'accès câblé est possible (un répéteur Wi-Fi divise souvent le débit).

**À l'écrit** : « deux réseaux IP → routeur (couche 3) ; passerelle des postes = adresse du
routeur dans leur réseau ».

**Repère rapide** : **répéteur, hub : 1 · pont, switch, point d'accès : 2 · routeur : 3 · modem :
signal de la ligne**. Exercices liés : {_ex("E07", "E15", "E16", "E17")}.
"""


def _domains() -> str:
    return f"""**Objectifs** : compter les domaines de collision et de diffusion d'un schéma et dire ce que
change chaque équipement.

## 7.1 Collision et diffusion

- un **domaine de collision** est la partie du réseau où deux émissions simultanées se
  brouillent (support partagé, semi-duplex) : un **hub** ou un **répéteur** ne sépare rien ; un
  **switch**, un **pont** ou un **routeur** sépare chaque port ; en duplex intégral sur un port de
  switch, il n'y a plus de collision ;
- un **domaine de diffusion** est la partie du réseau atteinte par une trame de diffusion
  ({BROADCAST_MAC}, par exemple une question ARP ou DHCP) : seul le **routeur** l'arrête.

{_fig(DOMAINS_FIGURE)}

Comptage : chaque liaison d'un switch ou d'un routeur = un domaine de collision ; un hub et
toutes ses liaisons = un seul domaine ; domaines de diffusion = interfaces du routeur (ici
**{DOMAINS_COLLISIONS}** et **{DOMAINS_BROADCASTS}**).

## 7.2 Complément : les VLAN

Un **switch administrable** peut découper ses ports en **VLAN** (réseaux locaux virtuels) :
chaque VLAN est un **domaine de diffusion séparé**, comme un switch à part (par exemple un VLAN
pour le personnel, un VLAN pour les invités). Pour passer d'un VLAN à l'autre, il faut un
**routeur** (ou un switch de couche 3). C'est un **complément**, utile pour isoler un réseau
d'invités ; le Wi-Fi invités est détaillé en PR25.

**Procédure professionnelle (à rédiger)** : numéroter chaque liaison → regrouper celles qui
passent par un même hub → compter ; puis compter les interfaces du routeur (et les VLAN).

**Erreur fréquente** : croire qu'un switch sépare les diffusions ; compter un domaine par poste
derrière un hub.

**À l'écrit** : « hub + 3 postes = 1 domaine de collision ; 2 interfaces de routeur = 2 domaines
de diffusion ».

**Repère rapide** : **hub : 1 domaine pour tout · switch : 1 par port · routeur : 1 diffusion
par interface · VLAN : 1 diffusion par VLAN**. Exercices liés : {_ex("E13", "E16")}.
"""


def _path() -> str:
    return f"""**Objectifs** : suivre un paquet du poste jusqu'à Internet et dire quelles adresses changent.

## 8.1 Local ou distant ?

Le poste compare l'adresse de destination à **son réseau** (adresse et masque, PR20) :
- destination **dans le réseau** : trame envoyée **directement** au destinataire (ARP de sa MAC) ;
- destination **hors du réseau** : trame envoyée à la **passerelle par défaut** (ARP de la MAC
  de la box) ; l'adresse IP de destination reste celle du serveur.

## 8.2 Le chemin

{_fig(PATH_FIGURE)}

{_frames_table()}

- le **switch** lit la MAC de destination et envoie la trame au seul port de la box : il ne
  change rien ;
- la **box** (routeur) retire la trame, lit l'IP, remplace l'IP source privée {PC.ip} par son
  adresse publique {BOX_WAN.ip} (**NAT**), puis construit une **nouvelle trame** vers
  {ISP_ROUTER.owner.lower()} ;
- chaque routeur d'Internet refait la trame ; l'**IP de destination** {SERVER_IP} ne change pas.

{_fig(PATH_STEPS_FIGURE)}

**Procédure professionnelle (à rédiger)** : local ou distant → ARP de la bonne MAC →
encapsulation → switch → routeur (NAT) → routeurs suivants ; écrire les adresses de chaque trame.

**Erreur fréquente** : mettre la MAC du serveur d'Internet dans la première trame ; croire que le
switch change les adresses ; oublier le NAT.

**À l'écrit** : « trame 1 : MAC de destination = box ({BOX_LAN.mac}), IP de destination = serveur
({SERVER_IP}) ».

**Repère rapide** : **MAC : change à chaque routeur · IP de destination : ne change pas · IP
source : changée par le NAT de la box**. Exercices liés : {_ex("E01", "E12")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : mener un diagnostic réseau couche par couche et le rédiger avec des preuves.

## 9.1 De bas en haut

On part de la couche **1** et on monte : une couche n'est examinée que si celle du dessous est
**prouvée** correcte.

{_checks_table()}

{_fig(DIAG_FIGURE)}

## 9.2 Lire les relevés

- voyant éteint → **1** ; voyant allumé mais port dans un mauvais VLAN → **2** ;
- adresse 169.254.x.x, passerelle vide ou sans réponse → **3** (adressage détaillé en PR20) ;
- ping du serveur réussi mais port du service fermé (Test-NetConnection -Port) → **4** ;
- adresse IP du serveur joignable mais nom introuvable (nslookup) → **7** (DNS) ;
- tout répond mais l'application refuse l'identifiant → **7**.

Le dépannage complet (DHCP, DNS, box, opérateur) est en [PR24](/uaa/ampcr-pratique-pr24).

**Procédure professionnelle (à rédiger)** : les six étapes ci-dessus ; à chaque couche, noter
la preuve (« ping de la passerelle : réponse en 1 ms ») avant de monter.

**Erreur fréquente** : commencer par réinstaller l'application ; conclure « panne Internet »
alors que le nom seul n'est pas résolu ; sauter une couche.

**À l'écrit** : « couches 1 à 3 correctes (preuves) ; port 443 fermé → couche 4, règle du pare-feu ».

**Repère rapide** : **1 voyant · 2 port et VLAN · 3 IP et passerelle · 4 port du service · 7 nom
et application**. Exercices liés : {_ex("E02", "E08", "E19")}.
"""


def _examples() -> str:
    blocks: list[str] = []
    for title, situation, steps, conclusion in CASES:
        lines = "\n".join(f"{i}. {line}" for i, line in enumerate(steps, start=1))
        blocks.append(
            f"""## {title}

**Situation.** {situation}

**Résolution.**

{lines}

**Conclusion rédigée.** « {conclusion} »
"""
        )
    return (
        "Cinq situations résolues pas à pas avec les règles du cours : topologie et NetBEUI, choix des "
        "équipements, chemin d'un paquet, domaines, diagnostic par couche. Chaque conclusion est justifiée.\n\n"
        + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **Confondre bus et étoile** : un câble commun (bus) contre un câble par poste (étoile).

> **Oublier le point unique de panne** de l'étoile : le switch central.

> **Réciter les couches** sans dire ce que fait chacune ; placer DNS ou DHCP à la couche 3.

> **Oublier le FCS ou le bourrage** dans une taille de trame ({ETH_MIN_FRAME} octets au minimum).

> **Croire que le switch lit l'adresse IP** ou qu'il sépare les diffusions.

> **Relier deux réseaux IP avec un switch** : il faut un routeur.

> **Mettre la MAC du serveur d'Internet** dans la trame émise par le poste : c'est la MAC de la passerelle.

> **Appeler « protocole » un port** ou « équipement » un service.

> **Chercher une panne de câble** pour un logiciel NetBEUI qui doit traverser un routeur.

> **Ouvrir des ports vers Internet** (445, 3389) sans besoin.

> **Sauter des couches** dans un diagnostic, sans preuve.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (chemin d'un paquet, diagnostic par couche,
encapsulation), classements (topologies, protocole / service / équipement, couche des
protocoles, rôle des équipements, couche d'une panne), **six schémas à compléter** (topologies,
OSI/TCP-IP, encapsulation, adresses des trames, domaines, trame Ethernet), **choix d'équipement
et de topologie** (besoins d'une PME, hub à remplacer, deux réseaux IP, liaisons entre agences),
NetBEUI, ports et pare-feu. Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR19_SLUG}/practice), avec correction après envoi.

{_exercises_html()}
"""


_ANSWER_TYPES = {
    "short_answer": "réponse courte",
    "long_answer": "réponse développée",
    "document_analysis": "analyse de document",
}


def _mini_exam() -> str:
    rows = "\n".join(
        f"| {i} | {item.title} | {_ANSWER_TYPES[item.question_type]} | {item.total_points:g} |"
        for i, item in enumerate(EXAM_ITEMS, start=1)
    )
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR19_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (relevés et tables fictifs). **Aucune correction n'est
visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **diagnostic justifié** par les relevés, le **choix argumenté**
(couche, rôle), le **calcul juste** (tailles, liaisons, domaines) — pas la récitation de sigles.
Une autre formulation techniquement juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Topologies** : bus (câble commun, bouchons ; une coupure arrête tout) ; étoile (un câble par
  poste ; switch = point unique de panne) ; anneau (de station en station, jeton ; simple
  fragile, double se reboucle) ; maillage (plusieurs chemins ; complet = n × (n − 1) ÷ 2).
- **OSI** : 1 physique (bits) · 2 liaison (trames, MAC) · 3 réseau (paquets, IP) · 4 transport
  (segments, ports) · 5 session · 6 présentation · 7 application.
- **TCP/IP** : accès réseau (1-2) · Internet (3) · transport (4) · application (5-7).
- **Encapsulation** : TCP {TRANSPORT_HEADER["TCP"]}, UDP {TRANSPORT_HEADER["UDP"]}, IPv4 {IPV4_HEADER}, Ethernet {ETH_HEADER} + FCS {ETH_FCS} ; trame
  {ETH_MIN_FRAME} à {octets(ETH_MAX_FRAME)} octets ; MTU {octets(ETH_MTU)}.
- **Adresses** : MAC dans le réseau local ; IP de bout en bout ; port = programme ; ARP : IP → MAC.
- **Ports** : HTTP 80, HTTPS 443, DNS 53, DHCP 67/68, SMTP 25/587, SSH 22, SMB 445, RDP 3389.
- **Protocole** = règles ; **service** = programme serveur ; **équipement** = matériel.
- **NetBEUI** : noms NetBIOS, diffusion, **non routable**, remplacé par TCP/IP.
- **Équipements** : répéteur, hub (1) ; pont, switch, point d'accès (2) ; routeur (3) ; modem
  (signal) ; passerelle par défaut = routeur.
- **Domaines** : hub = 1 collision pour tout ; switch = 1 par port ; routeur = 1 diffusion par
  interface ; VLAN = 1 diffusion par VLAN.
- **Chemin** : MAC changent à chaque routeur ; IP de destination fixe ; NAT change l'IP source.
- **Diagnostic** : 1 → 2 → 3 → 4 → 7, avec une preuve à chaque couche.

## Glossaire des termes employés

- **ARP** : protocole qui trouve l'adresse MAC correspondant à une adresse IP du réseau local.
- **Domaine de collision** : partie du réseau où deux émissions simultanées se brouillent.
- **Domaine de diffusion** : partie du réseau atteinte par une diffusion ; limitée par un routeur.
- **Encapsulation** : ajout d'un en-tête par chaque couche, à l'émission.
- **FCS** : champ de contrôle d'erreur à la fin de la trame.
- **MTU** : taille maximale d'un paquet sur un support ({octets(ETH_MTU)} octets en Ethernet).
- **NAT** : traduction de l'adresse IP privée en adresse publique par la box.
- **Passerelle par défaut** : adresse du routeur à qui le poste confie tout paquet destiné à un
  autre réseau.
- **Port** : numéro qui désigne un programme dans un poste (TCP ou UDP).
- **Topologie** : façon dont les équipements sont reliés (physique) ou dont les données circulent
  (logique).
- **VLAN** : réseau local virtuel, découpé dans un switch ; un domaine de diffusion par VLAN.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Topologies de réseaux » (AP-23), « Notions de base sur
  les protocoles (TCP/IP, OSI, NETBEUI…) » (AP-29) et « Hub, switch, passerelle, routeur, modem »
  (AP-31). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **ISO/IEC 7498-1** : modèle de référence OSI. **RFC 1122** : couches de la pile TCP/IP.
- **IEEE 802.3** : Ethernet (trame, adresses MAC, FCS, taille minimale et maximale) ; **IEEE
  802.11** : Wi-Fi.
- **RFC 791** (IPv4), **RFC 9293** (TCP), **RFC 768** (UDP), **RFC 826** (ARP), **RFC 1035** (DNS),
  **RFC 2131** (DHCP) ; registre des ports de l'**IANA**.
- **RFC 1001 et 1002** : NetBIOS ; documentation historique Microsoft sur NetBEUI.
- **RFC 5737** : blocs d'adresses réservés à la documentation (adresses publiques des exemples).

Les valeurs sont celles de {WRITTEN_AT} ; les en-têtes sont comptés **sans option**. Les
topologies, tableaux des couches, encapsulations, trames, chemins de paquet, domaines et
procédures du cours sont **produits par programme** depuis des données **vérifiées par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite les topologies, les protocoles (TCP/IP, OSI, NetBEUI) et les équipements. Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les **VLAN** et le comptage des domaines de collision et de diffusion ;
- le **pont**, le **répéteur** et le **point d'accès** (en plus des équipements cités) ;
- les **ports** TCP/UDP, le **NAT** et le chemin détaillé d'un paquet ;
- IPX/SPX, cité pour comparaison avec NetBEUI.

## Supports fictifs

Les entreprises, réseaux, adresses, relevés, captures et tables de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune n'est une question
officielle ou déjà posée par le Jury. Pour une intervention réelle, on relève la configuration
sur place avec les outils du système.
"""


def pr19_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR19 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR19 — 1. Topologies : bus, étoile, anneau, maillage", _topologies()),
        ("PR19 — 2. Les modèles OSI et TCP/IP", _models()),
        ("PR19 — 3. Encapsulation et trame Ethernet", _encapsulation()),
        ("PR19 — 4. Adresses MAC et IP, ARP, ports TCP et UDP", _addresses()),
        ("PR19 — 5. NetBEUI, protocole historique non routable", _netbeui()),
        ("PR19 — 6. Équipements : hub, switch, routeur, passerelle, modem", _devices()),
        ("PR19 — 7. Domaines de collision et de diffusion, VLAN", _domains()),
        ("PR19 — 8. Chemin d'un paquet du PC à Internet", _path()),
        ("PR19 — 9. Diagnostic couche par couche", _diagnosis()),
        ("PR19 — Exemples : cinq situations résolues", _examples()),
        ("PR19 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR19 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR19 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR19 — Fiche mémo et glossaire", _memo()),
        ("PR19 — Sources et compléments pédagogiques", _sources()),
    ]

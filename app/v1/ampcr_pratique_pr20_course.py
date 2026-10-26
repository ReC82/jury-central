"""Cours PR20 « IPv4, MAC, masques et passerelles — configuration et diagnostics écrits » —
parcours AMPCR pratique écrite (ticket #199).

Matière : intégralement celle du ticket #199 (1. modèle d'un réseau local, 2. adresse MAC,
3. IPv4, 4. masque, 5. CIDR, 6. passerelle, 7. DNS, 8. DHCP, 9. configuration Windows,
10. configuration Linux, 11. plan d'adressage, 12. connexion directe de deux PC, 13. méthode de
diagnostic, 14. cas d'erreur, 15. compte rendu), découpée en blocs titrés (le titre pilote le
type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen »,
« source », « exemple », « exercice », « méthode », « piège » ni « attention »). Toutes les
valeurs d'adressage sont **calculées** (`app.v1.ampcr_pratique_pr20_figures`, module standard
`ipaddress`) ; exercices et mini-examen : `app.v1.ampcr_pratique_pr20_bank`. Mise en forme
partagée avec PR06/PR11/PR15/PR16.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr20_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr20_figures import (
    BITS_EXAMPLES,
    BITS_FIGURES,
    COMPLEMENT_PREFIXES,
    DIALOG_FIGURE,
    DORA_FIGURE,
    IPCONFIG_FIGURE,
    LADDER_FIGURE,
    LAN_BY_NAME,
    LAN_FIGURE,
    LAN_HOSTS,
    LAN_NETWORK,
    LAN_POOL,
    LAN_ROUTER,
    LAN_SERVER,
    LINUX_FIGURE,
    MAC_EXAMPLE,
    MAC_FIGURE,
    MAC_RANDOM_EXAMPLE,
    PREFIX_TABLE,
    STATIC_EXAMPLE,
    TREE_FIGURES,
    Host,
    address_kind,
    binary_and_last_octet,
    is_local_for,
    mac_linux,
    normalize_mac,
    prefix_to_mask,
    subnet_facts,
)

PR20_TITLE = "IPv4, MAC, masques et passerelles — configuration et diagnostics écrits"
PR20_SLUG = "ampcr-pratique-pr20"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr20") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _f(address: str, prefix: int):
    return subnet_facts(address, prefix)


# --- Données des cinq cas résolus (calculées) ------------------------------------------------

CASE1_A = Host("COMPTA", "poste", "192.168.10.40", 24, LAN_ROUTER, (LAN_SERVER,), "3C-52-82-1A-2B-40")
CASE1_B = Host("ATELIER", "poste", "192.168.11.40", 24, "192.168.11.1", ("192.168.11.1",), "3C-52-82-1A-2B-41")
CASE4_HOST = Host("RH-2", "poste", "192.168.10.70", 26, LAN_ROUTER, (LAN_SERVER,), "3C-52-82-1A-2B-70")


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : tu ne configureras pas de carte réseau devant le jury, mais tu dois savoir **lire,
calculer, configurer sur papier et justifier**. À partir d'un plan, de relevés de commandes et
de symptômes, tu sais :

1. **lire un plan de réseau** et y repérer cartes, switch, routeur, passerelle, DHCP et DNS ;
2. **relever et interpréter** une adresse MAC, une adresse IPv4, un masque, une passerelle et
   un DNS (`ipconfig /all`, `ip addr`, `ip route`) ;
3. **calculer** réseau, diffusion, plage d'hôtes et nombre d'hôtes ; **convertir** masque ↔
   préfixe ; dire si deux postes sont **dans le même sous-réseau** ;
4. **configurer** un poste (Windows, Linux) et **rédiger un plan d'adressage** cohérent ;
5. **diagnostiquer** un défaut d'adressage (APIPA, DNS, masque, passerelle, doublon…) en
   justifiant chaque test ;
6. **rédiger** le compte rendu de l'intervention.

## Exigence officielle travaillée dans ce cours

{_req("AP-30")}

C'est le cœur du cours. Il prépare aussi, sans les traiter entièrement : la passerelle et le
routeur (AP-31, PR19), la connexion de deux machines en direct (AP-28, approfondie en PR21), le
mini-réseau (AP-38, PR21/PR18) et le dépannage d'accès au réseau et à Internet (AP-37 et AP-32,
PR24).

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C01")}

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC16 IPv4](/uaa/ampcr-mc16), [MC17 Masques et CIDR](/uaa/ampcr-mc17),
[MC18 Réseau et broadcast](/uaa/ampcr-mc18), [MC19 DHCP](/uaa/ampcr-mc19) et
[MC20 DNS, ARP et ICMP](/uaa/ampcr-mc20). Ce cours-ci est **pratique** : relevés, plans,
calculs écrits, configuration et diagnostic, comme dans un dossier d'intervention.

## Comment travailler ce cours

Lis les sections dans l'ordre, refais les calculs des figures **à la main**, puis étudie les
**cinq cas résolus**. Fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans
« S'entraîner », correction après envoi), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les réseaux, relevés, captures et adresses MAC de ce cours sont des **supports
> fictifs** construits pour s'entraîner ; la présentation réelle des commandes varie selon la
> version du système. Toutes les valeurs d'adressage ont été **calculées et vérifiées par
> programme**. Aucun exercice n'est une question officielle ni une question déjà posée par le
> Jury.
"""


def _lan_model() -> str:
    pc = LAN_BY_NAME["PC-01"]
    return f"""## 1.1 Les pièces d'un réseau local

{_fig(LAN_FIGURE)}

- **Carte réseau (interface)** : la « prise » réseau du poste (Ethernet ou Wi-Fi). Chaque carte
  a **une adresse MAC** et reçoit **une configuration IP**. Un portable a souvent deux cartes
  (Ethernet et Wi-Fi) : il faut relever **la bonne interface**.
- **Liaison** : câble Ethernet (paire torsadée, PR15) ou liaison Wi-Fi (PR25) jusqu'au switch
  ou au point d'accès.
- **Switch** : relie les équipements **du même réseau local** ; il transmet les trames d'après
  les adresses **MAC**. Il ne change rien à l'adressage IP.
- **Routeur** : relie **des réseaux différents** (le réseau local et Internet, ou deux
  sous-réseaux). Son adresse côté réseau local est la **passerelle par défaut** des postes. À
  la maison ou en PME, la « box » est à la fois routeur, switch, point d'accès Wi-Fi, serveur
  DHCP et relais DNS.
- **Serveur DHCP** : distribue automatiquement adresse, masque, passerelle et DNS.
- **Serveur DNS** : traduit un **nom** (www.exemple.be) en **adresse IP**.

Dans le réseau de référence : réseau **{LAN_NETWORK}**, passerelle **{LAN_ROUTER}**, serveur
DHCP et DNS **{LAN_SERVER}**, étendue DHCP **{LAN_POOL[0]} à {LAN_POOL[1]}**. PC-01 a reçu
**{pc.ip}/{pc.prefix}** de ce serveur.

## 1.2 Connectivité physique et connectivité logique

Deux niveaux à **toujours séparer** dans un diagnostic :

- **physique** : le lien existe-t-il ? (câble branché, voyant allumé, port du switch actif,
  Wi-Fi associé, carte activée) ;
- **logique** : l'adressage permet-il d'échanger ? (bonne adresse, bon masque, bonne passerelle,
  bon DNS, pas de doublon).

Un câble parfait ne corrige pas un mauvais masque ; une adresse parfaite ne sert à rien si le
câble est débranché. On vérifie **d'abord** le physique, **puis** le logique.
"""


def _mac() -> str:
    mac = normalize_mac(MAC_EXAMPLE)
    return f"""## 2.1 À quoi sert une adresse MAC

{_fig(MAC_FIGURE)}

L'adresse **MAC** (adresse physique) identifie **une carte réseau** sur le **réseau local**.
Le switch s'en sert pour transmettre les trames au bon port. Elle compte **48 bits**, écrits en
**12 chiffres hexadécimaux** (0-9, A-F), groupés par 2 : {mac} sous Windows,
{mac_linux(MAC_EXAMPLE)} sous Linux — c'est **la même adresse**.

- Les **3 premiers octets** (OUI) identifient en principe le **fabricant** ; les 3 derniers
  numérotent la carte. L'adresse gravée par le fabricant est en principe **unique** (unicité
  administrative).
- Mais une MAC **peut être modifiée** par logiciel, et de nombreux appareils utilisent des
  **MAC aléatoires** (« adresse privée » du Wi-Fi des téléphones et de Windows) ou
  **virtuelles** (machines virtuelles). On les reconnaît au **bit U/L à 1** dans le premier
  octet : deuxième chiffre hexadécimal 2, 6, A ou E (ex. {normalize_mac(MAC_RANDOM_EXAMPLE)}).

## 2.2 Relever une adresse MAC

- **Windows** : `ipconfig /all`, ligne « Adresse physique » (de la **bonne carte**) ; aussi
  `getmac`.
- **Linux** : `ip link` ou `ip addr`, ligne `link/ether`.
- **Imprimante, box** : page de configuration, étiquette, interface web.
- **À distance, dans le même réseau** : `ping` de l'adresse IP, puis `arp -a` (Windows) ou
  `ip neigh` (Linux) qui associe IP et MAC. **Limite** : l'ARP ne voit que le réseau local ;
  derrière un routeur, on ne lit que la MAC… du routeur.

> **À retenir —** **MAC ≠ IP** : la MAC identifie une carte sur le lien local, l'adresse IP
> situe un poste dans un réseau et permet de le joindre au-delà du routeur. **MAC ≠ identité** :
> une MAC se lit et se modifie ; elle n'identifie ni une personne ni un appareil de façon
> fiable, et le « filtrage MAC » n'est pas une protection sérieuse.
"""


def _ipv4() -> str:
    examples = [
        ("10.45.2.1", "réseau d'entreprise"),
        ("172.20.0.9", "réseau d'entreprise"),
        ("192.168.0.254", "box domestique"),
        ("172.32.0.9", "juste hors de 172.16/12"),
        ("192.169.1.1", "juste hors de 192.168/16"),
        ("169.254.12.7", "poste sans bail DHCP"),
        ("127.0.0.1", "le poste lui-même"),
        ("0.0.0.0", "pas encore d'adresse"),
    ]
    rows = "\n".join(f"- `{a}` → **{address_kind(a)}** ({why})." for a, why in examples)
    return f"""## 3.1 Une adresse sur 32 bits

Une adresse **IPv4** compte **32 bits**, écrits en **quatre octets** de **0 à 255** séparés par
des points (notation **décimale pointée**) : `192.168.10.101`. Une valeur comme `192.168.10.256`
ou `192.168.10` n'est **pas** une adresse IPv4 valide.

Elle comporte deux parties :

- une **partie réseau** (commune à tous les postes du même réseau) ;
- une **partie hôte** (propre à chaque poste).

C'est le **masque** (section 4) qui dit où passe la frontière.

## 3.2 Adresses particulières d'un réseau

- **Unicast** : l'adresse d'un seul poste (cas normal).
- **Adresse de réseau** : partie hôte entièrement à 0 (`192.168.10.0` en /24). Elle désigne
  le réseau, **jamais** un poste.
- **Adresse de diffusion (broadcast)** : partie hôte entièrement à 1 (`192.168.10.255` en /24).
  Un paquet envoyé à cette adresse est reçu par **tous** les postes du réseau ; **jamais** un
  poste.

## 3.3 Plages à reconnaître immédiatement

- **Privées (RFC 1918)** : **10.0.0.0/8**, **172.16.0.0/12** (de 172.16.0.0 à
  172.31.255.255) et **192.168.0.0/16**. Utilisables librement dans un réseau local, **non
  routées sur Internet** (la box les traduit par NAT, vu en PR24).
- **Bouclage (loopback)** : **127.0.0.1** (en fait tout 127.0.0.0/8) : le poste lui-même ; un
  `ping 127.0.0.1` teste la pile TCP/IP, **pas** la carte ni le câble.
- **Lien local / APIPA** : **169.254.0.0/16**. Windows s'attribue une telle adresse quand
  **aucun serveur DHCP ne répond** : le poste ne joint alors que d'autres postes en 169.254.
- **0.0.0.0** : **adresse non spécifiée** ; selon le contexte, « pas encore d'adresse » (client
  DHCP au démarrage) ou « toutes les adresses / route par défaut » (`0.0.0.0/0`). Jamais
  l'adresse d'un poste.
- **Publiques** : toutes les autres adresses ordinaires, routées sur Internet.

Classement **calculé** de quelques adresses :

{rows}

> **Piège fréquent —** 172.32.0.9 et 192.169.1.1 **ne sont pas** privées : la plage 172.16/12
> s'arrête à 172.31.255.255, la plage 192.168/16 à 192.168.255.255.
"""


def _mask_cidr() -> str:
    prefix_rows = "\n".join(
        f"- **/{p}** = `{prefix_to_mask(p)}` → bloc de **{_f('10.0.0.0', p).total}** adresses, "
        f"**{_f('10.0.0.0', p).usable}** hôtes usuels."
        for p in PREFIX_TABLE
    )
    a, m, r, value = binary_and_last_octet("192.168.10.77", prefix_to_mask(27))
    f27 = _f("192.168.10.77", 27)
    figures = "".join(_fig(fig) for fig in BITS_FIGURES)
    compare = [
        ("192.168.10.70", "192.168.10.100", 24),
        ("192.168.10.70", "192.168.10.100", 26),
    ]
    compare_rows = "\n".join(
        f"- `{x}/{p}` et `{y}/{p}` : réseaux `{_f(x, p).network}` et `{_f(y, p).network}` → "
        + ("**même sous-réseau**, communication directe." if _f(x, p).network == _f(y, p).network
           else "**sous-réseaux différents**, il faut un routeur.")
        for x, y, p in compare
    )
    return f"""## 4.1 Le masque : des 1 pour le réseau, des 0 pour l'hôte

Le **masque** a lui aussi 32 bits : des **1** sur toute la partie réseau, puis des **0** sur la
partie hôte. `255.255.255.0` = 24 bits à 1 puis 8 bits à 0 : on l'écrit aussi **/24**
(notation **CIDR**, « préfixe »). Un masque valide est **contigu** : tous les 1 à gauche, puis
uniquement des 0. `255.255.255.160` (`10100000`) ou `255.255.0.255` ne sont **pas** des masques
valides.

Valeurs possibles d'un octet de masque : 0, 128, 192, 224, 240, 248, 252, 254, 255
(0 à 8 bits à 1).

## 4.2 Réseau et diffusion par le ET logique

- **Adresse de réseau** = adresse **ET** masque, bit à bit (1 ET 1 = 1, sinon 0).
- **Diffusion** = adresse de réseau avec **tous les bits d'hôte à 1**.
- **Plage d'hôtes** = de réseau + 1 à diffusion − 1.
- **Nombre d'adresses** = 2^(bits d'hôte) ; **hôtes usuels** = ce nombre − 2.

Exemple calculé, 192.168.10.77/27 : dernier octet `{a}` ET `{m}` = `{r}` = **{value}**. Réseau
**{f27.network}**, diffusion **{f27.broadcast}**, hôtes **{f27.host_range}** ({f27.usable}).

{figures}

> **Méthode examen —** sans binaire, pour un préfixe entre /25 et /30 : **taille du bloc =
> 256 − dernier octet du masque** (/26 : 256 − 192 = 64). Le réseau est le **multiple du bloc**
> juste en dessous de l'octet de l'adresse ; la diffusion = réseau + bloc − 1. Écris toujours ce
> raisonnement : le correcteur note la démarche.

## 4.3 Les préfixes à connaître

{prefix_rows}

**Compléments (hors cas ordinaires)** : /{COMPLEMENT_PREFIXES[0]} = `{prefix_to_mask(COMPLEMENT_PREFIXES[0])}`,
2 adresses, utilisé **seulement** pour des liaisons point à point entre routeurs (les deux
adresses servent d'hôtes) ; /{COMPLEMENT_PREFIXES[1]} = `{prefix_to_mask(COMPLEMENT_PREFIXES[1])}`,
une seule adresse (une machine précise, dans une route ou une règle de pare-feu). Ne les propose
pas pour un réseau de postes.

> **Piège fréquent —** ne confonds pas **nombre total d'adresses** (64 en /26) et **hôtes
> usuels** (62) : l'adresse de réseau et la diffusion ne s'attribuent pas.

## 5. CIDR : convertir et comparer

- **Masque → préfixe** : compter les bits à 1 (255 = 8, 192 = 2…) ; 255.255.255.224 = 24 + 3 =
  **/27**.
- **Préfixe → masque** : /26 = 24 + 2 → dernier octet 11000000 = **192** → 255.255.255.192.
- **Deux postes communiquent sans routeur** seulement s'ils sont dans **le même réseau**, avec
  **le même masque**. On calcule le réseau de chacun :

{compare_rows}

Si les masques diffèrent, chaque poste raisonne avec **son** masque : l'un peut voir l'autre
comme local et l'autre le voir comme distant (exercice E05) ; on corrige toujours pour que tout
le réseau ait le même masque.
"""


def _gateway_dns_dhcp() -> str:
    pc = LAN_BY_NAME["PC-01"]
    return f"""## 6. La passerelle par défaut

Quand un poste envoie un paquet, il compare l'adresse de destination à **son propre réseau** :

- destination **dans** son réseau (route **locale**) → envoi **direct** (ARP pour trouver la
  MAC, puis le switch) ;
- destination **hors** de son réseau → envoi à la **passerelle par défaut** (route **par
  défaut**, `0.0.0.0/0`), c'est-à-dire au routeur, qui fait suivre.

Règles de cohérence :

- la passerelle doit être **dans le même sous-réseau** que le poste (sinon elle est
  injoignable) ;
- c'est l'adresse **réelle** du routeur sur ce réseau ({LAN_ROUTER} ici) ;
- deux postes du même réseau communiquent **même sans passerelle** ; la passerelle ne sert qu'à
  **sortir** du réseau.

> **À retenir —** passerelle ≠ DNS. La passerelle **achemine** les paquets vers les autres
> réseaux ; le DNS **traduit** les noms en adresses. Sur une box, c'est souvent la même
> adresse, mais ce sont **deux rôles** différents.

## 7. Le DNS

Le DNS traduit `www.exemple.be` en une adresse IP. Le poste interroge le serveur DNS noté dans
sa configuration ({LAN_SERVER} pour PC-01).

- Test **par adresse IP** (`ping 9.9.9.9`) : vérifie l'acheminement.
- Test **par nom** (`ping www.exemple.be`, `nslookup www.exemple.be`) : vérifie **en plus** la
  résolution.

Si le ping par IP répond et le ping par nom échoue, **Internet fonctionne** : c'est la
résolution de noms qui est en panne (DNS erroné, serveur DNS arrêté, nom mal écrit). Dire
« Internet est en panne » serait faux.

## 8. Le DHCP

{_fig(DORA_FIGURE)}

- **DORA** : Discover (le client cherche un serveur par diffusion), Offer (proposition),
  Request (le client demande l'offre), Acknowledge (confirmation).
- **Bail** : l'adresse est prêtée pour une durée ; le client la **renouvelle** avant
  l'expiration (`ipconfig /all` montre « Bail obtenu » et « Bail expirant »).
- **Options** : le serveur fournit aussi **masque**, **passerelle** et **DNS**. Une erreur dans
  ces options touche **tous** les postes en DHCP.
- **Dynamique ou statique** : postes en DHCP (simple, sans doublon) ; serveurs, imprimantes,
  NAS, routeur en **adresse fixe hors de l'étendue** ou en **réservation DHCP** (le serveur
  donne toujours la même adresse à une MAC donnée).
- **Sans réponse DHCP**, Windows passe en **APIPA** (169.254.x.y/16, sans passerelle) : c'est un
  **symptôme** (pas de bail), pas une cause. Câble débranché, port, VLAN, serveur arrêté ou
  étendue pleine sont autant de causes possibles : il faut **tester**.

Dans le réseau de référence, PC-01 a reçu {pc.ip}, masque {pc.mask}, passerelle {pc.gateway} et
DNS {pc.dns[0]} du serveur {LAN_SERVER}.
"""


def _commands() -> str:
    pc4 = LAN_BY_NAME["PC-04"]
    return f"""## 9. Windows : relever, renouveler, tester

{_fig(IPCONFIG_FIGURE)}

**Commandes de lecture** (ne modifient rien) :

- `ipconfig` : adresse, masque, passerelle de chaque carte ;
- `ipconfig /all` : en plus **MAC**, DHCP activé ou non, **bail**, serveur DHCP, **DNS** ;
- `ping <adresse ou nom>` : l'hôte répond-il ? (4 essais) ;
- `tracert <adresse ou nom>` : par quels routeurs passe le paquet, et **où il s'arrête** ;
- `nslookup <nom>` : quel serveur DNS répond et quelle adresse il donne ;
- `arp -a` : correspondances IP ↔ MAC connues sur le réseau local ;
- `route print` : table de routage (route par défaut = `0.0.0.0` masque `0.0.0.0`).

**Commandes qui modifient l'état** (à annoncer à l'utilisateur, coupure brève possible) :

- `ipconfig /release` : rend le bail DHCP (le poste perd son adresse) ;
- `ipconfig /renew` : redemande un bail ;
- `ipconfig /flushdns` : vide le cache DNS du poste.

**Configuration** : Paramètres réseau → options de la carte → Propriétés → « Protocole Internet
version 4 (TCP/IPv4) » : « Obtenir une adresse IP automatiquement » (DHCP) ou « Utiliser
l'adresse IP suivante » (fixe).

{_fig(DIALOG_FIGURE)}

## 10. Linux : relever et configurer

{_fig(LINUX_FIGURE)}

- `ip addr` (ou `ip a`) : interfaces, état **UP/DOWN**, MAC (`link/ether`), adresse/préfixe
  (`inet {pc4.ip}/{pc4.prefix}`), diffusion (`brd {pc4.facts.broadcast}`) ;
- `ip route` : route **par défaut** (`default via {pc4.gateway}`) et route **locale**
  (`{pc4.facts.cidr}`) ;
- `ping -c 4 <cible>` (sous Linux, `ping` continue sans fin si on n'indique pas `-c`) ;
- `ip neigh` : voisins connus (équivalent de `arp -a`) ;
- `resolvectl status` ou `resolvectl dns` **si le système utilise systemd-resolved** ; sinon le
  fichier `/etc/resolv.conf` indique les DNS.

**Temporaire ou persistant** : `sudo ip addr add …` ou `sudo ip route add default via …`
modifient la configuration **jusqu'au redémarrage** seulement (utile pour un test). La
configuration **persistante** se fait avec l'outil de la distribution : **NetworkManager**
(interface graphique ou `nmcli`) sur la plupart des postes de travail, **Netplan** sur Ubuntu
serveur, d'autres fichiers ailleurs. **Il n'y a pas de commande universelle** : on indique
l'outil utilisé.

> **Méthode examen —** dans une réponse écrite, recopie **la valeur relevée** puis
> **l'interprétation** : « ipconfig /all : IPv4 169.254.37.112, masque 255.255.0.0, pas de
> passerelle → adresse APIPA, aucun bail DHCP ». Une commande citée sans interprétation ne
> rapporte presque rien.
"""


def _plan_direct() -> str:
    rows = "\n".join(
        f"- **{h.name}** ({h.role}) : `{h.ip}/{h.prefix}`, "
        + (f"passerelle `{h.gateway}`, DNS `{h.dns[0]}`, " if h.gateway else "")
        + ("DHCP." if h.dhcp else "adresse fixe.")
        for h in (*LAN_HOSTS, STATIC_EXAMPLE)
    )
    a, b = "192.168.1.10", "192.168.1.20"
    return f"""## 11. Construire un plan d'adressage

Un **plan d'adressage** est le tableau de référence du réseau : pour chaque équipement, son
nom, son adresse, son masque, sa passerelle, son DNS, son mode (DHCP, fixe, réservation) et
souvent sa MAC. Démarche :

1. **Choisir le réseau** : une plage privée, de taille suffisante (postes + imprimantes +
   équipements + passerelle + marge) ; /24 pour un petit réseau.
2. **Réserver des zones** : par exemple .1 pour le routeur, .2 à .49 pour les adresses fixes
   (serveurs, imprimantes, NAS, points d'accès), .100 à .199 pour l'**étendue DHCP**.
3. **Paramètres communs** : même masque, même passerelle, même DNS pour tous.
4. **Contrôler** : pas de **doublon**, pas d'adresse de **réseau** ni de **diffusion**, aucune
   adresse fixe **dans l'étendue DHCP**, passerelle **dans** le réseau.
5. **Documenter** le plan et le tenir à jour.

Plan du réseau de référence (contrôlé par programme : aucune erreur) :

{rows}

## 12. Relier deux PC directement

Pour relier deux PC sans switch ni box (copie de données, test) :

- **Câble** : les cartes actuelles gèrent presque toujours l'**Auto MDI-X** : un câble droit
  suffit (un câble croisé fonctionne aussi). Les **voyants de lien** confirment le physique.
- **Adressage** : les deux postes dans **le même réseau**, même masque, adresses différentes —
  par exemple `{a}/24` et `{b}/24`. **Aucune passerelle** n'est nécessaire (il n'y a pas de
  routeur) ; aucun DNS : on utilise les adresses IP.
- Sans DHCP, deux postes Windows **en automatique** finissent chacun en APIPA (169.254.x.y/16)
  et peuvent communiquer entre eux, mais une configuration fixe est plus claire.
- **Pare-feu** : il peut bloquer le ping (ICMP) et le partage ; autoriser ces flux sur le profil
  réseau plutôt que tout désactiver.
- **Tests** : lien, `ipconfig`, ping dans les deux sens, accès au partage.

> **Piège fréquent —** accuser le câble quand les voyants sont allumés et que les adresses sont
> dans deux réseaux différents. Le câble et l'adressage sont **deux couches distinctes**.
"""


def _diagnosis() -> str:
    trees = "".join(_fig(fig) for fig in TREE_FIGURES)
    return f"""## 13.1 Démarche : du plus proche au plus lointain

{_fig(LADDER_FIGURE)}

1. **Lien** : voyant, message « câble réseau débranché », Wi-Fi associé, carte **activée**,
   **bonne interface** (Ethernet ou Wi-Fi ?).
2. **Relevé** : `ipconfig /all` ou `ip addr` + `ip route` : IP, masque, passerelle, DNS, DHCP.
3. `ping 127.0.0.1` : pile TCP/IP.
4. `ping` de **sa propre adresse** : adresse bien attribuée.
5. `ping` d'un **voisin** ou de la **passerelle** : réseau local.
6. `ping` d'une **IP distante**, `tracert` pour situer l'arrêt : routage.
7. `ping` d'un **nom**, `nslookup` : DNS.

Compléments : `arp -a` / `ip neigh` (la passerelle a-t-elle une MAC ?), `route print` /
`ip route` (route par défaut présente ?), état du **DHCP** (bail, serveur).

**Interpréter avec prudence** : un ping sans réponse ne prouve pas que la machine est éteinte :
le **pare-feu peut filtrer l'ICMP** (Windows le bloque souvent par défaut). On confirme par un
autre test (accès au partage, autre machine, `arp -a`).

**Séparer, à l'écrit** : **constat** (ce qu'on voit) → **hypothèse** (cause possible) → **test**
(ce qu'on fait pour vérifier) → **résultat** (valeur obtenue) → **action** (correction).

## 13.2 Trois arbres de diagnostic

{trees}

## 14. Cas d'erreur à reconnaître

- **IP dupliquée** : message de conflit, coupures aléatoires ; `arp -a` montre une MAC
  inattendue. Souvent une adresse fixe placée **dans l'étendue DHCP**.
- **Mauvais masque** : le poste croit locales des adresses distantes (masque trop court, /16)
  ou distantes des adresses locales (masque trop long, /27 au lieu de /24).
- **Mauvaise passerelle** : réseau local OK, rien au-delà ; la passerelle ne répond pas ou est
  hors du réseau.
- **DNS erroné** : ping par IP OK, par nom KO.
- **DHCP absent** : APIPA 169.254.x.y sur les postes en automatique.
- **APIPA** : symptôme de l'absence de bail (voir l'arbre) — jamais une preuve unique.
- **Sous-réseaux incompatibles** : deux postes dans deux réseaux sans routeur.
- **Câble débranché** : « média déconnecté », aucune adresse ou APIPA.
- **Carte désactivée** : l'interface n'apparaît pas ou est « désactivée » ; `ip addr` montre
  `DOWN`.
- **Mauvaise interface** : on relève le Wi-Fi alors que le poste utilise l'Ethernet (ou
  l'inverse), ou une carte virtuelle.
- **Pare-feu ICMP** : le ping échoue alors que le service fonctionne.
"""


def _report() -> str:
    return """## 15. Le compte rendu d'intervention

Une intervention d'adressage se termine par un écrit, compréhensible par le client et utile au
prochain technicien :

1. **Contexte** : demande, poste ou équipement, symptôme, date.
2. **Plan avant / après** : adresse, masque, passerelle, DNS, mode (relevés exacts).
3. **Commandes et observations** : chaque commande avec **le résultat obtenu**.
4. **Hypothèses** envisagées et écartées, avec le test qui les a écartées.
5. **Cause** retenue et **corrections** effectuées.
6. **Tests de validation** : ping passerelle, IP distante, nom, service demandé (partage,
   impression), en présence de l'utilisateur si possible.
7. **Risques et recommandations** : mise à jour du plan, adresses fixes hors étendue,
   réservations, documentation des changements.

> **Méthode examen —** un compte rendu se juge sur l'**exactitude des valeurs**, la **logique**
> constat → test → cause → action → validation, et la **clarté** : pas de jargon inutile pour le
> client, mais toutes les valeurs pour le technicien.
"""


def _examples() -> str:
    a, b = CASE1_A, CASE1_B
    apipa = "169.254.88.14"
    f26 = _f(CASE4_HOST.ip, CASE4_HOST.prefix)
    server_local = is_local_for(CASE4_HOST.ip, CASE4_HOST.prefix, LAN_SERVER)
    return f"""Chaque cas suit la même démarche : **constat**, **relevés**, **raisonnement**, **correction**,
**validation** et **compte rendu**. Supports fictifs ; toutes les valeurs sont calculées.

<h3 class="jc-example-title">Cas 1 — Deux PC dans des sous-réseaux différents</h3>

**Constat.** Le poste COMPTA ne voit pas le dossier partagé du poste ATELIER, branché sur le
même switch.

**Relevés.** COMPTA : `{a.ip}/{a.prefix}`, passerelle `{a.gateway}`. ATELIER :
`{b.ip}/{b.prefix}`, passerelle `{b.gateway}`.

**Raisonnement.** Réseau de COMPTA : **{_f(a.ip, a.prefix).cidr}** ; réseau d'ATELIER :
**{_f(b.ip, b.prefix).cidr}**. Deux réseaux différents : ils ne peuvent communiquer que par un
routeur. Or la passerelle d'ATELIER, `{b.gateway}`, n'existe pas sur ce switch (le seul routeur
est `{LAN_ROUTER}`). ATELIER a été configuré avec un ancien plan.

**Correction.** ATELIER : adresse fixe libre du réseau **{LAN_NETWORK}**, hors étendue DHCP
(par exemple `192.168.10.41/24`), passerelle `{LAN_ROUTER}`, DNS `{LAN_SERVER}` — ou retour en
DHCP.

**Validation.** `ping 192.168.10.40` depuis ATELIER, puis accès au dossier partagé.

**Compte rendu.** « ATELIER était configuré dans le réseau 192.168.11.0/24, différent de celui
de COMPTA (192.168.10.0/24), sans routeur entre eux. Adresse corrigée en 192.168.10.41/24,
passerelle et DNS du plan ; partage accessible. Plan mis à jour. »

<h3 class="jc-example-title">Cas 2 — Un poste en APIPA</h3>

**Constat.** Un portable en Ethernet n'a plus accès à rien ; les autres postes fonctionnent.

**Relevés.** `ipconfig /all` : DHCP activé : Oui ; IPv4 d'autoconfiguration **{apipa}**
(plage 169.254.0.0/16 : {address_kind(apipa)}), masque 255.255.0.0, pas de passerelle.

**Raisonnement.** Aucun bail DHCP reçu. Les autres postes ont un bail : le serveur DHCP
répond. Cause locale probable : lien, prise, port.

**Tests.** Voyant de la carte éteint ; le câble est enfiché dans une prise murale non brassée.
Sur une autre prise : voyant allumé, `ipconfig /renew` → `192.168.10.115/24`, passerelle
`{LAN_ROUTER}`, DNS `{LAN_SERVER}`.

**Validation.** `ping {LAN_ROUTER}`, `ping www.exemple.be`, navigation.

**Compte rendu.** « Portable en APIPA (169.254.88.14) : aucun bail DHCP. Prise murale non
raccordée au switch. Branché sur une prise active, bail obtenu (192.168.10.115/24) ; tests de
passerelle et de nom réussis. Prise signalée pour brassage. »

<h3 class="jc-example-title">Cas 3 — Un DNS erroné</h3>

**Constat.** « Internet ne marche plus » sur un poste en adresse fixe.

**Relevés.** DNS préféré : `192.168.10.50`. `ping {LAN_ROUTER}` OK ; `ping 9.9.9.9` OK ;
`nslookup www.exemple.be` : délai dépassé.

**Raisonnement.** Réseau local et Internet fonctionnent (ping par IP). Seule la résolution
échoue : le DNS configuré n'existe pas ; le bon serveur est `{LAN_SERVER}`.

**Correction.** DNS préféré `{LAN_SERVER}` ; `ipconfig /flushdns`.

**Validation.** `nslookup www.exemple.be` répond via {LAN_SERVER} ; navigation rétablie.

**Compte rendu.** « Panne de résolution de noms, pas d'Internet : DNS 192.168.10.50 erroné.
Remplacé par 192.168.10.5 ; résolution et navigation vérifiées. »

<h3 class="jc-example-title">Cas 4 — Un masque incorrect</h3>

**Constat.** Depuis une « optimisation » faite par un collègue, le poste RH-2 n'ouvre plus le
dossier partagé du serveur {LAN_SERVER} et n'accède plus à Internet ; les autres postes
fonctionnent.

**Relevés.** `{CASE4_HOST.ip}`, masque **{CASE4_HOST.mask}** (/{CASE4_HOST.prefix}), passerelle
`{CASE4_HOST.gateway}`, DNS `{LAN_SERVER}`. Le reste du réseau est en /24.

**Raisonnement.** Avec /{CASE4_HOST.prefix}, le réseau de RH-2 est **{f26.cidr}** (hôtes
{f26.host_range}). Le serveur {LAN_SERVER} lui paraît {"local" if server_local else "**distant**"} ;
pour le joindre, il faudrait passer par la passerelle {CASE4_HOST.gateway}… qui est **elle aussi
hors** de ce réseau calculé. Ni le serveur ni la passerelle ne sont joignables normalement :
configuration incohérente, causée par le seul masque.

**Correction.** Masque 255.255.255.0, comme tout le réseau.

**Validation.** `ping {LAN_SERVER}`, accès au partage, `ping www.exemple.be`.

**Compte rendu.** « Masque 255.255.255.192 saisi par erreur : le poste se croyait dans
{f26.cidr} ; serveur et passerelle lui paraissaient hors de son réseau. Masque 255.255.255.0
rétabli, comme le reste du réseau ; partage et Internet vérifiés. »

<h3 class="jc-example-title">Cas 5 — Un doublon d'adresse IP</h3>

**Constat.** PC-02 affiche « conflit d'adresses IP » par intermittence.

**Relevés.** PC-02 (DHCP) : `192.168.10.102`. Une caméra IP récemment installée a été
configurée à la main en `192.168.10.102`, **dans l'étendue** {LAN_POOL[0]}–{LAN_POOL[1]}.
Depuis PC-01, `arp -a` montre pour 192.168.10.102 la MAC de la caméra.

**Raisonnement.** Deux machines répondent à la même adresse : les paquets vont tantôt à l'une,
tantôt à l'autre.

**Correction.** Caméra en adresse fixe **hors étendue et libre** (par exemple `192.168.10.22`)
ou réservation DHCP ; `ipconfig /release` puis `/renew` sur PC-02.

**Validation.** Plus de message de conflit ; `ping 192.168.10.22` et image de la caméra ;
`arp -a` cohérent.

**Compte rendu.** « Doublon 192.168.10.102 entre PC-02 (DHCP) et la caméra IP (fixe dans
l'étendue). Caméra déplacée en 192.168.10.22, hors étendue ; PC-02 renouvelé ; plus de conflit.
Plan mis à jour : adresses fixes toujours hors de l'étendue. »
"""


def _pitfalls() -> str:
    return """> **Confondre MAC et IP.** La MAC identifie une carte sur le lien local ; l'IP situe le poste
> dans un réseau.

> **Prendre la MAC pour une identité fiable** ou le filtrage MAC pour une sécurité.

> **Croire privées 172.32.x.x ou 192.169.x.x.** Les plages privées sont 10/8, 172.16/12 et
> 192.168/16.

> **Attribuer l'adresse de réseau ou de diffusion** à un poste.

> **Confondre nombre d'adresses et hôtes usuels** (64 et 62 en /26).

> **Écrire un masque non contigu** (255.255.255.160) ou mal convertir (/27 = 255.255.255.224).

> **Placer la passerelle hors du réseau du poste**, ou y mettre l'adresse du DNS par habitude.

> **Dire « Internet est en panne »** quand seul le ping par nom échoue : c'est le DNS.

> **Conclure sur la seule APIPA** sans tester lien, prise, port et serveur DHCP.

> **Mettre une adresse fixe dans l'étendue DHCP** : doublon assuré tôt ou tard.

> **Conclure « machine éteinte »** parce qu'un ping ne répond pas : le pare-feu peut filtrer
> l'ICMP.

> **Annoncer une commande Linux « universelle »** pour une configuration persistante : elle
> dépend de la distribution (NetworkManager, Netplan…).

> **Accuser le câble** d'une connexion directe alors que les adresses sont dans deux réseaux
> différents.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : sept calculs d'adressage et CIDR, cinq diagnostics sur
relevés, quatre configurations de mini-réseaux et quatre comptes rendus ou procédures écrites
(dont une remise en ordre). Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR20_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR20_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Toutes les informations nécessaires sont dans chaque question et ses
documents (relevés de commandes, plans, notes fictives). **Aucune correction n'est visible
pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après l'envoi,
chaque réponse est corrigée selon le **barème analytique** de la question (critères et points),
puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** L'**exactitude des calculs** (réseau, diffusion, plage, masque),
la **lecture des relevés**, le **raisonnement** (constat → test → cause), la **correction**
proposée et sa **validation** — pas la récitation de sigles. Une réponse juste formulée
autrement, ou une autre adresse libre et cohérente, est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé. Un calcul faux (réseau,
diffusion, masque) ou une passerelle hors du réseau sont toujours pénalisés, même bien rédigés.
"""


def _memo() -> str:
    lines = "\n".join(
        f"  - {a}/{p} : réseau {_f(a, p).network}, diffusion {_f(a, p).broadcast}, "
        f"hôtes {_f(a, p).host_range} ({_f(a, p).usable})."
        for a, p in BITS_EXAMPLES
    )
    return f"""## Mémo

- **MAC** : 48 bits, 12 chiffres hexadécimaux ; OUI (fabricant) + carte ; lien local ; bit U/L
  à 1 = MAC aléatoire ou virtuelle. **MAC ≠ IP, MAC ≠ identité.**
- **IPv4** : 32 bits, 4 octets 0-255 ; partie réseau + partie hôte.
- **Privées** : 10/8, 172.16/12, 192.168/16. **127.0.0.1** bouclage. **169.254/16** APIPA.
  **0.0.0.0** non spécifiée.
- **Masque** : 1 contigus puis 0 ; /24 = 255.255.255.0, /25 = .128, /26 = .192, /27 = .224,
  /28 = .240, /30 = .252.
- **Réseau** = IP ET masque ; **diffusion** = bits d'hôte à 1 ; **hôtes** = 2^(32−n) − 2.
- Exemples calculés :
{lines}
- **Même réseau + même masque** = communication directe ; sinon **routeur**.
- **Passerelle** : dans le réseau du poste, adresse du routeur ; sert à **sortir** du réseau.
- **DNS** : nom → IP ; ping IP OK + nom KO = **DNS**, pas Internet.
- **DHCP** : DORA, bail, options masque/passerelle/DNS ; fixes **hors étendue** ou
  **réservation** ; pas de bail → **APIPA**.
- **Windows** : `ipconfig /all`, `/release`, `/renew`, `/flushdns`, `ping`, `tracert`,
  `nslookup`, `arp -a`, `route print`.
- **Linux** : `ip addr`, `ip route`, `ip neigh`, `ping -c`, `resolvectl` si présent ;
  `ip … add` = temporaire ; persistant = outil de la distribution.
- **Démarche** : lien → relevé → 127.0.0.1 → propre IP → passerelle → IP distante → nom.
  Constat / hypothèse / test / résultat / action. ICMP parfois filtré.
- **Compte rendu** : contexte, avant/après, commandes et résultats, hypothèses, cause,
  correction, validation, recommandations.

## Glossaire des termes employés

- **APIPA** : adresse 169.254.x.y que Windows s'attribue sans réponse DHCP.
- **ARP** : mécanisme qui trouve la MAC correspondant à une IP du réseau local.
- **Bail** : durée pendant laquelle une adresse DHCP est prêtée.
- **CIDR** : écriture du masque par un préfixe (/24).
- **Diffusion (broadcast)** : adresse qui atteint tous les postes du réseau.
- **Étendue DHCP** : plage d'adresses que le serveur DHCP distribue.
- **ICMP** : protocole utilisé par `ping` et `tracert`.
- **Interface** : carte réseau (physique ou virtuelle) qui porte une configuration IP.
- **OUI** : 3 premiers octets d'une MAC, attribués au fabricant.
- **Passerelle par défaut** : routeur auquel le poste envoie tout ce qui sort de son réseau.
- **Réservation DHCP** : adresse toujours attribuée à la même MAC.
- **Route par défaut** : `0.0.0.0/0`, utilisée pour toute destination non locale.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 6 : épreuve uniquement écrite, exigence AP-30
  (« L'adressage IP, les adresses MAC, l'identification d'une adresse MAC et d'une adresse
  IP »). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **IPv4, masques, CIDR** : RFC 791 (IPv4), RFC 4632 (CIDR) ; **adresses privées** : RFC 1918 ;
  **lien local / APIPA** : RFC 3927 ; **bouclage et 0.0.0.0** : RFC 1122 ; **/31** : RFC 3021 ;
  **adresses de documentation** (203.0.113.0/24, utilisée pour l'adresse publique fictive) :
  RFC 5737 ; **DHCP** (DORA, bail, options) : RFC 2131 ; **adresses MAC** (48 bits, OUI, bits
  I/G et U/L) : IEEE 802.
- **Commandes** : documentation Microsoft (`ipconfig`, `ping`, `tracert`, `nslookup`, `arp`,
  `route`) et pages de manuel Linux (`ip-address`, `ip-route`, `ip-neighbour`, `resolvectl`,
  `nmcli`) ; présentation simplifiée dans les captures fictives.

Toutes les valeurs d'adressage du cours, des exercices et du mini-examen (réseau, diffusion,
plage, nombre d'hôtes, masque ↔ préfixe, même sous-réseau, type d'adresse, erreurs des plans)
sont **calculées avec le module `ipaddress` de Python et vérifiées par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande l'adressage IP et l'identification des adresses MAC et IP (AP-30).
Sont des **compléments**, signalés comme tels :

- la rédaction de la procédure et du compte rendu (AP-C01, approfondie en PR29) ;
- le DHCP (DORA, bail, réservation), le DNS et les commandes de diagnostic, utiles pour
  identifier et corriger un adressage ; ils préparent le dépannage (AP-37, AP-32 : PR24) ;
- les préfixes /31 et /32, les bits I/G et U/L de la MAC ;
- la connexion directe de deux PC (AP-28, développée en PR21) et le plan d'adressage d'un
  mini-réseau (AP-38, PR21).

## Supports fictifs

Les réseaux, relevés de commandes, captures, plans et adresses MAC de ce cours sont **fictifs**
et reconstitués pour l'entraînement ; la présentation réelle varie selon les systèmes et leur
langue. Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr20_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR20 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR20 — 1. Le réseau local : cartes, switch, routeur, DHCP et DNS", _lan_model()),
        ("PR20 — 2. Adresse MAC : 48 bits, rôle local et limites", _mac()),
        ("PR20 — 3. Adresse IPv4 : 32 bits, réseau, hôte et plages particulières", _ipv4()),
        ("PR20 — 4-5. Masque, préfixe CIDR, réseau, diffusion et plage d'hôtes", _mask_cidr()),
        ("PR20 — 6-8. Passerelle par défaut, DNS et DHCP", _gateway_dns_dhcp()),
        ("PR20 — 9-10. Relever et configurer : commandes Windows et Linux", _commands()),
        ("PR20 — 11-12. Plan d'adressage et connexion directe de deux PC", _plan_direct()),
        ("PR20 — 13-14. Diagnostic d'adressage : démarche, arbres et cas d'erreur", _diagnosis()),
        ("PR20 — 15. Compte rendu d'intervention", _report()),
        ("PR20 — Exemples : cinq cas intégralement résolus", _examples()),
        ("PR20 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR20 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR20 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR20 — Fiche mémo et glossaire", _memo()),
        ("PR20 — Sources et compléments pédagogiques", _sources()),
    ]

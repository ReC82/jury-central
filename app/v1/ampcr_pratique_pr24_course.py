"""Cours PR24 « Dépannage réseau et Internet — dossiers d'intervention écrits » — parcours AMPCR
pratique écrite (ticket #200).

Matière : intégralement celle du ticket #200 (1. méthode en couches, 2. physique et liaison,
3. configuration IP, 4. DHCP, 5. DNS, 6. passerelle et routage, 7. switch et VLAN, 8. Wi-Fi,
9. partages et imprimantes, 10. outils Windows, 11. outils Linux, 12. procédure ordonnée,
13. pannes combinées, 14. sécurité des interventions, 15. rapport professionnel), découpée en
blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de bloc théorique
ne contient « examen », « source », « exemple », « exercice », « méthode », « piège »,
« attention » ni « mémo »). Le réseau de référence, les relevés et les schémas viennent de
`app.v1.ampcr_pratique_pr24_figures` (construits depuis des données, calculs `ipaddress`) ;
exercices et mini-examen : `app.v1.ampcr_pratique_pr24_bank`. Mise en forme partagée avec
PR06/PR11/PR15/PR16/PR20.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr20_figures import Host, ipconfig_all_lines, is_local_for, subnet_facts
from app.v1.ampcr_pratique_pr24_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr24_figures import (
    APIPA_HOST,
    DOCUMENT_FIGURES,
    DOMAIN,
    ETHERNET_MAX_M,
    GUEST_NETWORK,
    GUEST_SSID,
    GUEST_VLAN,
    ISP_DNS,
    LAN_BY_NAME,
    LAN_FIGURE,
    LAN_NETWORK,
    LAYERS_FIGURE,
    LEASE_DAYS,
    NAS_IP,
    NS_NXDOMAIN,
    POE_CLASSES,
    POOL,
    PORTS_FIGURE,
    PRINTER_IP,
    ROUTER_IP,
    SERVER_IP,
    SHARE_UNC,
    SRV_FQDN,
    SSID,
    TREE_FIGURES,
    WAN_IP,
    WEB_IP,
    WEB_NAME,
    WifiStatus,
    fr,
    netsh_wlan_lines,
    nslookup_lines,
    pool_size,
    win_ping_lines,
    win_ping_unknown_name,
)

PR24_TITLE = "Dépannage réseau et Internet — dossiers d'intervention écrits"
PR24_SLUG = "ampcr-pratique-pr24"

_DOCS = {f.key: f for f in DOCUMENT_FIGURES}


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr24") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


# --- Données des six cas résolus (calculées) -------------------------------------------------

CASE2_HOST = Host("PC-02", "poste Windows, fixe", "192.168.20.42", 24, ROUTER_IP, (ISP_DNS,), "3C-52-82-1A-20-02")
CASE3_HOST = Host("PC-ACCUEIL", "poste fixe", "192.168.20.70", 26, ROUTER_IP, (SERVER_IP,), "3C-52-82-1A-20-70")
CASE4_HOST = Host("LT-03", "portable Wi-Fi", "192.168.1.50", 24, "192.168.1.1", ("192.168.1.1",), "A4-C3-F0-55-20-63")
CASE4_WIFI = WifiStatus("connecté", SSID, "9c:53:22:10:20:32", "802.11ac", "WPA2 - Personnel", "CCMP", "5 GHz", 36, 351, 78)


def _case4_ipconfig() -> tuple[str, ...]:
    lines = list(ipconfig_all_lines(CASE4_HOST, iface="Wi-Fi"))
    lines[0] = "Carte réseau sans fil Wi-Fi :"
    return ("C:\\> ipconfig /all", *lines)


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3) : on te remet un **dossier** — plan du réseau, symptômes, relevés de commandes, état des
équipements — et tu dois, sur papier :

1. **localiser méthodiquement** la panne (un poste ou tous, filaire ou Wi-Fi, local ou
   Internet) ;
2. **formuler des hypothèses** et choisir des **tests sûrs**, non destructifs ;
3. **interpréter** les résultats (ping, tracert, nslookup, ipconfig, journaux, état des ports) ;
4. **proposer une correction** autorisée, avec un retour arrière ;
5. **confirmer le rétablissement** par des tests ;
6. **rédiger le compte rendu** de l'intervention.

## Exigences officielles travaillées dans ce cours

{_req("AP-32")}
{_req("AP-37")}

Ce cours mobilise aussi, sans les traiter entièrement : l'adressage IP et MAC (AP-30, cours
[PR20](/uaa/ampcr-pratique-pr20)), les équipements (AP-31, PR19), le Wi-Fi (AP-33, PR25), les
partages et permissions (AP-25 à AP-27, PR23) et les câbles (AP-19, cours
[PR15](/uaa/ampcr-pratique-pr15)).

Compléments pédagogiques (hors liste officielle des pp. 5-6, signalés comme tels) :

{_req("AP-C01")}
{_req("AP-C03")}

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC13 Fondamentaux réseau](/uaa/ampcr-mc13), [MC14 Équipements](/uaa/ampcr-mc14),
[MC19 DHCP](/uaa/ampcr-mc19), [MC20 DNS, ARP et ICMP](/uaa/ampcr-mc20),
[MC22 Internet, NAT et routage](/uaa/ampcr-mc22), [MC24 VLAN](/uaa/ampcr-mc24),
[MC25 Wi-Fi](/uaa/ampcr-mc25), [MC26 Sécurité Wi-Fi](/uaa/ampcr-mc26),
[MC31 Dépannage réseau méthodique](/uaa/ampcr-mc31) et
[MC33 Partage de ressources](/uaa/ampcr-mc33). Ce cours-ci est **pratique** : dossiers,
relevés, procédures et comptes rendus, comme dans une intervention réelle.

## Le réseau de référence

{_fig(LAN_FIGURE)}

La plupart des situations du cours se passent dans ce réseau fictif de PME, « l'atelier » :
réseau **{LAN_NETWORK}**, box **{ROUTER_IP}** (passerelle, NAT, pare-feu, adresse publique
{WAN_IP}), serveur **SRV-01 {SERVER_IP}** (Linux, logiciel dnsmasq : DHCP avec des baux de
{LEASE_DAYS} jours sur l'étendue **{POOL[0]} à {POOL[1]}**, soit {pool_size()} adresses, et DNS
interne du suffixe **{DOMAIN}**, qui relaie les noms Internet vers le DNS du fournisseur
{ISP_DNS}), NAS **{NAS_IP}** (partage `{SHARE_UNC}`), imprimante **{PRINTER_IP}**, point
d'accès alimenté par le switch (Wi-Fi « {SSID} »), et un Wi-Fi invités « {GUEST_SSID} »
(VLAN {GUEST_VLAN}, réseau {GUEST_NETWORK}) isolé du réseau interne.

## Comment travailler ce cours

Lis les sections dans l'ordre, puis étudie les **six cas résolus**. Fais les
**{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction après
envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** le réseau, les relevés, les captures, les adresses MAC et les adresses
> publiques (plages de documentation RFC 5737) de ce cours sont des **supports fictifs**
> construits pour s'entraîner ; la présentation réelle des commandes varie selon la version et
> la langue du système. Les relevés sont **produits et vérifiés par programme** à partir du
> réseau de référence. Aucun exercice n'est une question officielle ni une question déjà posée
> par le Jury.
"""


def _layers() -> str:
    return f"""## 1.1 Avant tout test : cerner le problème

Une plainte comme « Internet ne marche plus » ne dit presque rien. Avant de toucher à quoi que
ce soit, le technicien établit :

- le **symptôme exact** : message affiché, ce qui fonctionne encore, ce qui ne fonctionne plus
  (un site, tous les sites, le partage, l'imprimante) ;
- le **périmètre** : **un poste ou tous** ? **filaire ou Wi-Fi** ? **local ou Internet** (le
  NAS répond-il ? et un site ?) ;
- la **chronologie** : depuis quand, en continu ou par intermittence, à quelle heure ;
- les **changements récents** : mise à jour, déménagement, nouveau matériel, réinitialisation
  de la box, intervention d'un prestataire ;
- la **topologie** : plan du réseau, équipements traversés, adresses prévues.

Le périmètre oriente tout le reste : **un seul poste** touché → on cherche sur ce poste, son
câble, son port, sa configuration ; **tous les postes** → on cherche l'**élément commun**
(switch, box, serveur DHCP ou DNS, liaison du fournisseur).

## 1.2 Raisonner par couches

{_fig(LAYERS_FIGURE)}

On teste dans l'ordre des couches : **physique et liaison**, **adresse IP et masque**,
**passerelle**, **IP distante**, **DNS**, **service ou application**. La première couche qui
échoue est celle qu'on examine ; les tests des couches supérieures ne sont pas encore
significatifs (un DNS ne peut pas répondre à un poste sans lien).

## 1.3 Hypothèse, test, preuve

1. **Hypothèses** : les causes possibles, de la plus probable à la moins probable.
2. **Tests non destructifs** d'abord : on observe et on lit (voyants, `ipconfig /all`, `ping`)
   avant de modifier quoi que ce soit.
3. **Conclusion** : on retient la cause **prouvée** par un test, pas celle qui « tombe en même
   temps ».

**Différencier corrélation et preuve** : « la panne a commencé après la mise à jour » est une
**corrélation**, une piste. La **preuve**, c'est un test qui la confirme : le service s'est
arrêté à l'heure de la mise à jour (journal), et la panne disparaît quand il redémarre.

> **À retenir —** à l'écrit, chaque étape se présente ainsi : **constat** (ce qu'on voit) →
> **hypothèse** → **test** → **résultat** (valeur relevée) → **conclusion** ou nouvelle
> hypothèse. Une conclusion sans test est une supposition.
"""


def _physical() -> str:
    poe = "\n".join(
        f"- **{name}** ({std}) : {fr(port)} W garantis au port du switch, {fr(device)} W disponibles "
        "pour l'équipement alimenté."
        for name, std, port, device in POE_CLASSES
    )
    return f"""## 2.1 Le lien existe-t-il ?

C'est la première question, et elle se règle **avant** toute configuration IP :

- **câble cuivre** : fiches RJ45 bien serties et enclenchées, câble ni écrasé ni plié, longueur
  du canal **{ETHERNET_MAX_M} m au plus** (cours [PR15](/uaa/ampcr-pratique-pr15)) ;
  **fibre** : connecteurs propres, bon type, émission/réception non inversées ;
- **voyants de lien** sur la carte et sur le port du switch (éteint = pas de lien) ;
- **port du switch** : actif ou **désactivé** par l'administrateur, prise murale bien
  **brassée** sur un port ;
- **carte réseau** activée dans le système, bon pilote ; Windows affiche « Média déconnecté »,
  Linux `NO-CARRIER` quand aucun lien n'est détecté ;
- **alimentation** du switch et du point d'accès ; un point d'accès alimenté par le câble
  (**PoE**) s'éteint si le port ou le budget PoE du switch ne suffit pas.

Repères PoE (IEEE 802.3) :

{poe}

> **À retenir —** **pas de lien = pas de diagnostic IP**. Tant que le voyant est éteint ou que
> le système affiche « Média déconnecté », on ne modifie ni l'adresse, ni le masque, ni le DNS.

## 2.2 Vitesse, duplex et erreurs

{_fig(PORTS_FIGURE)}

- **Négociation** : la carte et le port s'accordent automatiquement sur la **vitesse** (100 Mb/s,
  1 Gb/s…) et le **duplex** (full : émission et réception simultanées ; half : l'un ou l'autre).
- **Désaccord de duplex** : si un côté est **forcé** et l'autre en automatique, le côté
  automatique ne peut pas connaître le duplex et se replie en **half duplex** ; le lien
  fonctionne, mais **lentement**, avec des erreurs (collisions tardives côté half duplex,
  erreurs CRC côté full duplex).
- **Erreurs CRC** : trames reçues abîmées (contrôle d'intégrité faux) ; causes : câble ou fiche
  défectueux, paire endommagée, longueur excessive, **parasites** (câble non blindé près d'une
  source de perturbations, blindage mal raccordé), désaccord de duplex. Un compteur qui
  **augmente** est un indice fort.
- **Lien à 100 Mb/s** au lieu de 1 Gb/s sur une carte gigabit : souvent une paire défectueuse
  (le gigabit utilise les quatre paires).
- **Auto MDI-X** : les cartes et switchs actuels adaptent émission et réception ; un câble droit
  convient presque toujours, y compris entre deux PC.

## 2.3 Le Wi-Fi, couche radio

En Wi-Fi, la « couche physique » est la **radio** : SSID visible, **signal** suffisant, débit,
**interférences** (autres réseaux sur le même canal, micro-ondes en 2,4 GHz, murs épais). Le
détail est en section 8.

> **Piège fréquent —** conclure à une panne IP ou DNS alors que le lien est absent ou dégradé.
> Une adresse 169.254.x.y ou un DNS qui ne répond pas sont **des conséquences** possibles d'un
> lien défaillant.
"""


def _ip_dhcp() -> str:
    apipa = _DOCS["pr24-doc-apipa"]
    dhcp = _DOCS["pr24-doc-dhcp"]
    return f"""## 3. Contrôler la configuration IP

Une fois le lien présent, on relève la configuration (`ipconfig /all`, `ip addr`, `ip route`) et
on la compare au **plan d'adressage** (cours [PR20](/uaa/ampcr-pratique-pr20)) :

- **adresse IPv4** dans le réseau prévu (ici {LAN_NETWORK}), ni adresse de réseau ni de
  diffusion ;
- **masque / CIDR** identique à celui du réseau : un masque faux fait croire au poste que des
  adresses locales sont distantes (ou l'inverse) ;
- **passerelle** dans le réseau du poste, égale à l'adresse du routeur ; la **table de
  routage** (`route print`, `ip route`) doit contenir une **route par défaut** vers elle ;
- **adresse MAC** de la bonne carte (Ethernet ou Wi-Fi ?) ;
- **même sous-réseau ou non** : deux postes ne communiquent directement que s'ils sont dans le
  même réseau avec le même masque ;
- **doublon d'adresse IP** : message de conflit, coupures par intermittence, `arp -a` qui
  montre une MAC inattendue ; cause fréquente : une adresse fixe placée **dans l'étendue
  DHCP** ;
- **APIPA 169.254.0.0/16** : le poste est en DHCP mais n'a reçu **aucune réponse** ; Windows
  s'attribue une adresse 169.254.x.y/16, sans passerelle, et réessaie régulièrement ;
- **DHCP, statique ou réservation** : un poste en DHCP reçoit tout du serveur ; une adresse
  **statique** est saisie à la main (hors étendue) ; une **réservation** attribue toujours la
  même adresse à une MAC, depuis le serveur.

{_fig(apipa)}

> **À retenir —** l'APIPA dit **« aucun bail reçu »**, pas **pourquoi**. Les causes possibles
> sont nombreuses : lien, port, VLAN, serveur arrêté, étendue pleine, serveur qui ignore la
> carte. C'est un **indice**, pas une preuve.

## 4. Diagnostiquer le DHCP

**Séquence DORA** (détaillée en [PR20](/uaa/ampcr-pratique-pr20)) : le client diffuse
**Discover**, le serveur répond **Offer**, le client confirme **Request**, le serveur valide
**Acknowledge**. Le client renouvelle ensuite son **bail** avant l'expiration (Request/Ack
seulement). Les **options** transmises comprennent le masque, la **passerelle** (option 3) et
le **DNS** (option 6).

Pannes typiques :

- **absence de bail** : APIPA ; on vérifie lien, port, VLAN, puis le serveur ;
- **étendue épuisée** : toutes les adresses sont prêtées (visiteurs, baux trop longs) ; le
  journal du serveur indique qu'aucune adresse n'est disponible ;
- **mauvais pool** : étendue d'un autre réseau, ou qui empiète sur des adresses fixes ;
- **serveur inaccessible ou arrêté** : aucun Offer ; les postes **déjà configurés continuent
  de fonctionner** jusqu'à la fin de leur bail ({LEASE_DAYS} jours ici) — « les autres postes
  marchent » ne prouve donc pas que le DHCP fonctionne ;
- **relais DHCP** : le Discover est une **diffusion**, qui ne traverse pas un routeur ; si le
  serveur est dans un autre sous-réseau, un **agent relais** est nécessaire ;
- **second serveur DHCP** (box personnelle branchée par erreur) : des postes reçoivent un autre
  réseau, au hasard des renouvellements ;
- **mauvaise option** : passerelle ou DNS faux distribués à **tous** les postes.

{_fig(dhcp)}

**Tests** : `ipconfig /all` (DHCP activé ? serveur DHCP ? bail obtenu et expirant ?),
`ipconfig /renew` (redemande un bail), journal du serveur.

> **Important —** `ipconfig /release` **coupe** la connexion du poste jusqu'au `/renew` : on ne
> le lance jamais à distance (on perd la main sur le poste) ni sur un poste de production sans
> prévenir l'utilisateur. `ipconfig /renew` seul suffit souvent.
"""


def _dns() -> str:
    nslookup = _DOCS["pr24-doc-nslookup"]
    return f"""## 5.1 Connectivité par IP ou résolution de nom ?

Le DNS traduit un **nom** ({WEB_NAME}) en **adresse** ({WEB_IP}). Deux tests suffisent à
séparer les problèmes :

- `ping {WEB_IP}` (par **adresse**) répond → la connectivité vers Internet fonctionne ;
- `ping {WEB_NAME}` (par **nom**) échoue avec « hôte introuvable » → la **résolution de noms**
  est en cause, pas Internet.

> **À retenir —** « ping par IP OK, par nom KO » = **problème DNS**, pas panne d'Internet. Ne
> pas confondre **absence de résolution** et **absence d'Internet**.

## 5.2 Interroger le DNS

- **Windows** : `nslookup nom` (serveur configuré) ou `nslookup nom serveur` (serveur choisi).
- **Linux** : `dig nom`, `dig @serveur nom` (paquet dnsutils ou bind-utils, pas toujours
  installé), `resolvectl query nom` avec systemd-resolved.

Lire la réponse :

- **réponse avec une adresse** : le DNS fonctionne pour ce nom ;
- **« Non-existent domain » / NXDOMAIN** : le serveur répond que **le nom n'existe pas** (faute
  de frappe, nom interne demandé à un DNS public) ;
- **délai dépassé (timed out)** : **aucun serveur** n'a répondu (DNS configuré faux, arrêté ou
  injoignable).

## 5.3 DNS interne et DNS externe

{_fig(nslookup)}

Un **DNS interne** (ici SRV-01, {SERVER_IP}) connaît les noms du réseau de l'entreprise
({SRV_FQDN}) et relaie les autres questions vers Internet. Un **DNS public** ou celui du
fournisseur ({ISP_DNS}) ne connaît **pas** les noms internes. Un poste configuré avec un DNS
public **navigue normalement** mais ne trouve plus les serveurs internes.

## 5.4 Le cache

Le poste garde en **cache** les réponses récentes : après une correction, une ancienne réponse
peut persister. **Windows** : `ipconfig /displaydns` (afficher), `ipconfig /flushdns` (vider).
**Linux** avec systemd-resolved : `resolvectl flush-caches`. `nslookup` interroge directement
le serveur sans passer par le cache ni par le fichier hosts : un nslookup correct et un ping par
nom faux orientent vers le cache ou le fichier hosts du poste.
"""


def _routing_switching() -> str:
    tracert = _DOCS["pr24-doc-tracert"]
    ping = _DOCS["pr24-doc-ping"]
    return f"""## 6.1 Du plus proche au plus lointain

On teste dans l'ordre : un **hôte local** (serveur, voisin), la **passerelle**, puis une
**destination distante** par adresse.

{_fig(ping)}

- local OK, passerelle KO : masque, passerelle saisie, doublon d'adresse, VLAN, box arrêtée ;
- passerelle OK, distant KO : **au-delà** de la passerelle : liaison Internet de la box
  (synchronisation, connexion au fournisseur), fournisseur, filtrage ;
- `tracert` (Windows) ou `traceroute` / `tracepath` (Linux) montre **jusqu'où** les paquets
  vont : le premier saut est la passerelle.

{_fig(tracert)}

Une ligne `*  *  *` au **milieu** d'un tracert n'est pas une panne si les sauts suivants
répondent : certains routeurs ne répondent pas aux sondes. C'est une panne quand **plus rien**
ne répond après un saut.

## 6.2 Route par défaut, masque et routage

- **Route par défaut** (`0.0.0.0/0`) : tout ce qui n'est pas local part vers la passerelle.
  Sans elle (Linux : aucune ligne `default via`), le poste répond « Network is unreachable »
  pour toute adresse extérieure.
- **Mauvais masque** : la passerelle peut se retrouver **hors** du réseau calculé ; Windows
  avertit alors que la passerelle n'est pas dans le même sous-réseau, et le poste ne sort plus.
- **Routage inter-sous-réseaux** : deux réseaux ne communiquent que par un **routeur** qui
  connaît les deux (et des passerelles correctes de chaque côté).
- **NAT** (notion fonctionnelle) : la box remplace l'adresse privée des postes par **son**
  adresse publique ({WAN_IP}) pour sortir sur Internet, et fait le chemin inverse pour les
  réponses. Les adresses privées ne sont jamais routées sur Internet.
- **Pare-feu, ACL et filtrage ICMP** : un pare-feu (du poste, de la box, du serveur) ou une
  liste de contrôle d'accès (ACL) peut bloquer un service ou **seulement le ping** : un ping
  sans réponse **n'est pas une preuve** que la machine est éteinte ; on confirme par un autre
  test (port du service, `arp -a`, autre machine).

## 7. Switch et VLAN

- **Commutation** : le switch apprend sur quel port se trouve chaque **adresse MAC** (table
  MAC) et y envoie les trames. Une MAC absente de la table : l'équipement n'a pas émis, ou il
  n'est pas sur ce switch.
- **Ports désactivés** : par l'administrateur, ou automatiquement par une protection du port ;
  le voyant reste éteint.
- **VLAN** : un switch administrable peut séparer ses ports en **réseaux virtuels** isolés. Un
  port placé dans le **mauvais VLAN** met le poste dans un autre réseau : il reçoit l'adresse
  d'un autre DHCP (ou aucune → APIPA) et ne voit plus les serveurs.
- *Complément* : un port **access** appartient à un seul VLAN (postes) ; un lien **trunk**
  transporte plusieurs VLAN entre équipements (switch, point d'accès, routeur).

> **Piège fréquent —** supposer une erreur de VLAN **sans indice**. On ne l'envisage que si le
> réseau en utilise (plan, switch administrable) et qu'un relevé le montre : adresse d'un autre
> réseau, état du port, réorganisation récente.
"""


def _wifi() -> str:
    tree = TREE_FIGURES[1]
    weak = _DOCS["pr24-doc-wifi"]
    return f"""## 8.1 Trois problèmes différents

Un poste Wi-Fi « qui ne marche pas » peut avoir trois problèmes **distincts**, dans cet ordre :

1. **radio** : le **SSID** (nom du réseau) est-il visible ? le **signal** suffit-il ? Un même
   SSID peut être émis par plusieurs points d'accès, chacun avec son **BSSID** (adresse MAC de
   la radio) ;
2. **association et authentification** : le poste s'associe au point d'accès puis prouve qu'il
   connaît la clé : **WPA2-Personnel** (clé partagée, chiffrement AES-CCMP) ou
   **WPA3-Personnel** (échange SAE, plus robuste) ; clé incorrecte, profil enregistré avec une
   ancienne clé, carte qui ne gère pas WPA3 ;
3. **adressage** : **après** l'association, le poste demande un bail **DHCP** comme en
   filaire ; APIPA ou adresse d'un autre réseau (SSID invités, VLAN) = problème IP.

{_fig(tree)}

## 8.2 Portée, bandes et répéteurs

- **2,4 GHz** : porte plus loin, traverse mieux les murs, mais peu de canaux sans
  chevauchement (1, 6, 11 en pratique) et beaucoup d'interférences (voisins, micro-ondes,
  Bluetooth).
- **5 GHz** : plus de débit et de canaux, mais **portée plus courte**.
- **Répéteur** : prolonge la couverture en retransmettant le signal ; il doit lui-même recevoir
  un bon signal, et un répéteur à une seule radio **divise souvent le débit** disponible. Un
  point d'accès supplémentaire raccordé par câble est préférable quand c'est possible.

{_fig(weak)}

Ce relevé montre un poste **associé et authentifié** (WPA2 - Personnel) mais avec un signal de
18 % et 6,5 Mb/s en réception : problème **radio** (couverture), pas d'adressage.

> **À retenir —** distinguer **problème radio** (SSID invisible, signal faible, coupures),
> **problème d'authentification** (connexion refusée malgré un SSID visible) et **problème IP**
> (associé, mais APIPA ou mauvais réseau). La correction n'est pas la même.
"""


def _shares() -> str:
    tree = TREE_FIGURES[2]
    return f"""## 9.1 Le réseau répond, la ressource non

Quand le ping du serveur répond, le problème est **plus haut** : service, nom, chemin, compte ou
droits. On suit l'arbre ci-dessous.

{_fig(tree)}

- **Découverte du réseau** : l'onglet Réseau de l'explorateur peut ne pas afficher le serveur
  (profil réseau « Public », découverte désactivée) sans que l'accès par chemin soit bloqué.
- **Chemin UNC** : `\\\\serveur\\partage` (ici `{SHARE_UNC}`) ; une faute dans le nom donne
  « chemin réseau introuvable » (0x80070035) ; `\\\\{NAS_IP}\\Compta` contourne le DNS pour
  tester.
- **Permissions** : les droits de **partage** et les droits **NTFS** (du dossier) se
  **combinent** : depuis le réseau, c'est **le plus restrictif** qui s'applique (partage en
  Lecture + NTFS en Modification = lecture seule).
- **Compte** : en **domaine**, le compte du domaine ; en **groupe de travail**, un compte local
  du serveur ou du NAS ; des **identifiants mémorisés** périmés (Gestionnaire d'identification)
  peuvent être refusés sans nouvelle demande.
- **Service et pare-feu** : le partage de fichiers Windows (SMB) utilise le **port TCP 445** ;
  service arrêté ou port filtré = échec malgré le ping. Test :
  `Test-NetConnection NAS-01 -Port 445` (PowerShell).

## 9.2 Imprimante réseau

L'imprimante répond au ping mais n'imprime pas : on vérifie **la file d'impression** (travaux
bloqués, « en erreur »), le **port** utilisé par la file (adresse de l'imprimante à jour ?), le
**service Spouleur d'impression** du poste, puis l'imprimante elle-même (papier, erreurs).
Si un seul poste est touché, le problème est sur ce poste ; si tous le sont, sur l'imprimante ou
le serveur d'impression.
"""


def _tools() -> str:
    return """## 10. Outils Windows

Commandes de **lecture** (sans effet sur la configuration) :

- `ipconfig /all` : adresse, masque, passerelle, DNS, DHCP, bail, MAC ;
- `ping` : réponse d'une adresse ou d'un nom (ICMP) ;
- `tracert -d` : chemin jusqu'à une destination ;
- `nslookup` : réponse d'un serveur DNS ;
- `arp -a` : correspondances IP ↔ MAC du réseau local ;
- `route print` : table de routage, route par défaut ;
- `netstat -an` ou `Get-NetTCPConnection` (PowerShell) : connexions et ports ouverts ;
- `Test-NetConnection hôte -Port n` (PowerShell) : ping et test d'un port TCP précis ;
- `netsh wlan show interfaces` : état de la connexion Wi-Fi.

Commandes de **modification** (à annoncer à l'utilisateur) :

- `ipconfig /renew` et `ipconfig /release` : redemander ou libérer le bail DHCP ;
- `ipconfig /flushdns` : vider le cache DNS (sans risque).

Lecture ou modification : on commence **toujours** par lire.

**Limites de ping** : il teste l'ICMP, pas le service (un site, un partage) ; il peut être
**filtré** ; un ping réussi vers une adresse ne dit rien du nom ni des droits.

## 11. Outils Linux

- `ip addr`, `ip link` : adresses, état de l'interface (`UP`, `NO-CARRIER`) ;
- `ip route` : routes, route par défaut (`default via`) ;
- `ip neigh` : voisins IP ↔ MAC (`REACHABLE`, `FAILED`) ;
- `ping -c 4` : réponse ICMP (4 échos) ;
- `traceroute` ou `tracepath` : chemin jusqu'à la destination ;
- `dig` ou `nslookup` : réponse DNS ;
- `ss -tunap` : connexions et ports en écoute ;
- `journalctl -u NetworkManager -b` : journal du service réseau depuis le démarrage ;
- `nmcli device status`, `nmcli device wifi list` : état des interfaces, réseaux Wi-Fi visibles ;
- `resolvectl status` : serveurs DNS utilisés (systemd-resolved).

**Ne pas présumer** que tous ces outils sont présents : selon la distribution, `dig`,
`traceroute` ou `nmcli` peuvent manquer, et la configuration persistante passe par
NetworkManager, Netplan ou un autre outil. Une commande comme `ip route add` est
**temporaire** (perdue au redémarrage).

> **Méthode examen —** à l'écrit, cite la commande, **la valeur relevée** et **ton
> interprétation** : « ping 192.168.20.1 : 4 reçus sur 4 → la passerelle répond ; ping
> 198.51.100.20 : 100 % de perte → l'arrêt est au-delà de la box ». Une commande citée seule ne
> rapporte presque rien.
"""


def _procedure() -> str:
    master = TREE_FIGURES[0]
    linux = _DOCS["pr24-doc-linux"]
    return f"""## 12.1 La procédure ordonnée

1. **État physique** : voyants, câble, port, carte activée, Wi-Fi associé.
2. **IP et masque** : `ipconfig /all` / `ip addr` — adresse du bon réseau, pas d'APIPA, bon
   masque.
3. **Passerelle** : `ping {ROUTER_IP}` ou `arp -a` (la passerelle a-t-elle une MAC ?).
4. **IP distante** : `ping {WEB_IP}`, `tracert` pour situer l'arrêt.
5. **DNS** : `nslookup {WEB_NAME}` — bon serveur, réponse correcte.
6. **Application ou service** : le site, le partage, l'imprimante, le compte, les droits.

À chaque étape : **résultat attendu** si tout va bien, **interprétation** sinon, et
**branche** suivante. Exemple : à l'étape 2, une adresse 169.254 envoie vers la branche DHCP ;
une adresse d'un autre réseau vers la branche VLAN ou second serveur DHCP.

## 12.2 Arbre de diagnostic général

{_fig(master)}

{_fig(linux)}

Ce relevé Linux arrête la procédure dès l'étape 1 : `NO-CARRIER`, aucune route. On cherche le
câble ou le port, pas l'adresse.
"""


SYMPTOM_TABLE: tuple[tuple[str, tuple[str, ...], str, str, str], ...] = (
    (
        "Un seul poste : adresse 169.254.x.y",
        ("câble ou port", "port dans un VLAN sans DHCP", "serveur DHCP qui ignore la carte", "étendue pleine"),
        "voyant et état du port ; journal du serveur DHCP ; un autre appareil neuf obtient-il un bail ?",
        "port actif et journal « ignored » → la carte n'est pas enregistrée ; « no address available » → étendue pleine",
        "enregistrer la carte (réservation) ou libérer/agrandir l'étendue, avec l'accord du responsable",
    ),
    (
        "Tous les postes : plus d'Internet, le NAS fonctionne",
        ("liaison de la box (ligne, fibre, modem)", "identifiants de connexion du fournisseur", "panne du fournisseur", "DNS distribué faux"),
        "ping de la passerelle, ping d'une IP distante, tracert, page d'état de la box",
        "IP distante KO et tracert arrêté après la box → liaison ou fournisseur ; IP distante OK mais noms KO → DNS",
        "contrôler la ligne et la page d'état ; contacter le fournisseur ; ou corriger le DNS distribué",
    ),
    (
        "Un poste : sites inaccessibles, ping par IP OK",
        ("DNS configuré faux", "DNS public au lieu du DNS interne", "cache ou fichier hosts", "nom mal saisi"),
        "nslookup du nom, puis nslookup nom serveur-interne",
        "délai dépassé → serveur faux ou injoignable ; NXDOMAIN → nom inexistant pour ce serveur",
        "corriger le DNS (ou repasser en DHCP), vider le cache, corriger le nom",
    ),
    (
        "Partage inaccessible, ping du NAS OK",
        ("service SMB arrêté ou port 445 filtré", "nom non résolu", "chemin UNC faux", "compte ou droits"),
        "\\\\IP\\partage, Test-NetConnection -Port 445, message exact, autre compte",
        "port fermé → service ; IP OK mais nom KO → DNS ; « accès refusé » → compte ou droits",
        "relancer le service, corriger DNS, chemin ou droits, avec l'accord du responsable",
    ),
    (
        "Wi-Fi associé, mais pas d'accès",
        ("pas de bail (APIPA)", "configuration IP manuelle sur la carte Wi-Fi", "SSID invités isolé", "portail ou filtrage"),
        "ipconfig /all de la carte Wi-Fi, SSID affiché",
        "DHCP activé : Non avec une adresse d'un autre réseau → configuration manuelle ; APIPA → DHCP ; réseau invités → mauvais SSID",
        "remettre la carte en automatique, traiter le DHCP ou se connecter au bon SSID",
    ),
    (
        "Lenteur intermittente sur un poste filaire",
        ("désaccord de duplex", "câble ou fiche défectueux", "parasites", "saturation d'un lien"),
        "page des ports du switch (vitesse, duplex, CRC), ping prolongé, autre cordon",
        "half duplex ou CRC qui augmentent → liaison ; ports sains → chercher la charge ou l'application",
        "rétablir la négociation, remplacer le cordon, éloigner des parasites, puis mesurer à nouveau",
    ),
)


def _symptoms() -> str:
    cards = "\n".join(
        f"""<div class="jc-pr-doc">
<p class="jc-pr-doc-title">{escape(symptom)}</p>
<ul>
<li><strong>Causes possibles :</strong> {escape(" ; ".join(causes))}.</li>
<li><strong>Test discriminant :</strong> {escape(test)}.</li>
<li><strong>Résultat :</strong> {escape(result)}.</li>
<li><strong>Action :</strong> {escape(action)}.</li>
</ul>
</div>"""
        for symptom, causes, test, result, action in SYMPTOM_TABLE
    )
    return f"""## 13.1 Symptôme → causes possibles → test discriminant → résultat → action

Un **test discriminant** est celui qui **départage** deux hypothèses : son résultat est
différent selon la cause. On le choisit avant de réparer.

{cards}

## 13.2 Pannes combinées

Une intervention réelle cumule parfois **deux** causes ; corriger la première ne fait pas
disparaître tous les symptômes. On revérifie **toute la procédure** après chaque correction.

- **Câble défectueux + DNS faux** : la liaison est lente et les noms ne sont pas résolus ; un
  cordon neuf rend la vitesse, pas les noms.
- **Mauvais masque + mauvaise passerelle** : corriger le masque ne suffit pas si la passerelle
  saisie n'est pas celle du routeur.
- **DHCP intermittent** : deux serveurs DHCP, ou étendue presque pleine ; la panne « change de
  poste » selon les renouvellements de bail.
- **Réseau local OK mais Internet KO** : passerelle, liaison de la box, fournisseur.
- **Internet OK mais partage KO** : DNS interne, service, chemin, compte ou droits.
- **Wi-Fi associé sans IP** : DHCP, VLAN du SSID, étendue pleine.
- **Lenteur intermittente** : duplex, CRC, signal Wi-Fi, saturation ; on mesure **au moment**
  du symptôme (heure notée par l'utilisateur).
"""


def _safety_report() -> str:
    return """## 14. Sécurité des interventions

- **Autorisation** : on ne modifie pas la configuration d'un **réseau de production** (box,
  switch, serveur DHCP ou DNS, NAS) sans l'accord du responsable.
- **État initial** : on relève et on sauvegarde la configuration **avant** de la changer
  (copie du fichier, capture des valeurs).
- **Retour arrière** : on sait comment revenir à l'état initial si la modification aggrave la
  situation ; **une modification à la fois**.
- **Impact** : prévenir les utilisateurs d'une coupure (redémarrage de la box, `ipconfig
  /release`, relance d'un service).
- **Pas de scan intrusif** non autorisé : un balayage de ports ou d'adresses sur le réseau d'un
  client est interdit sans accord explicite et peut perturber des équipements.
- **Confidentialité des journaux** : journaux, captures et configurations contiennent des
  noms, des adresses et parfois des mots de passe ; ils restent chez le client ou sont
  transmis par un moyen autorisé, jamais sur un support personnel.

## 15. Le rapport professionnel

1. **Contexte** : client, date, demandeur, demande.
2. **Symptômes** exacts et **périmètre** (un poste ou tous, filaire ou Wi-Fi, local ou
   Internet).
3. **Schéma** ou référence au plan du réseau concerné.
4. **Hypothèses** envisagées.
5. **Tests et sorties** : chaque commande avec **la valeur relevée**.
6. **Cause confirmée** — ou **incertaine**, dite comme telle, avec ce qui reste à vérifier.
7. **Correction** effectuée, avec l'**autorisation** et l'**état initial** noté.
8. **Tests finaux** : passerelle, IP distante, nom, service demandé, idéalement avec
   l'utilisateur.
9. **Prévention** : recommandation pour éviter la récidive.
10. **Restitution** : explication claire au client, sans jargon inutile.

> **Méthode examen —** un rapport se juge sur l'**exactitude des valeurs**, la logique
> constat → test → cause → action → validation, et l'**honnêteté** : « cause non déterminée »
> vaut mieux qu'une cause inventée.
"""


def _examples() -> str:
    c3 = subnet_facts(CASE3_HOST.ip, CASE3_HOST.prefix)
    pc01 = LAN_BY_NAME["PC-01"]
    c3_local = {name: is_local_for(CASE3_HOST.ip, CASE3_HOST.prefix, ip)
                for name, ip in (("la passerelle", ROUTER_IP), ("SRV-01", SERVER_IP), ("le NAS", NAS_IP),
                                 ("l'imprimante", PRINTER_IP), ("PC-01", pc01.ip))}
    far = ", ".join(n for n, local in c3_local.items() if not local)
    near = ", ".join(n for n, local in c3_local.items() if local)
    case2_lines = (
        *win_ping_lines(SERVER_IP, (0, 0, 0, 0), ttl=64), "", *win_ping_unknown_name(SRV_FQDN),
        "", *nslookup_lines(SRV_FQDN, ISP_DNS, NS_NXDOMAIN),
    )
    return f"""Chaque cas suit la même démarche : **constat**, **relevés**, **raisonnement**, **correction**,
**validation** et **compte rendu**. Réseau de référence ; supports fictifs, valeurs calculées.

<h3 class="jc-example-title">Cas 1 — Un portable neuf en APIPA</h3>

**Constat.** Le portable LT-02, livré ce matin et branché au bureau 3, n'a « pas de réseau » ;
les autres postes fonctionnent.

**Relevés.** `ipconfig /all` : DHCP activé, IPv4 d'autoconfiguration **{APIPA_HOST.ip}**,
masque {APIPA_HOST.mask}, aucune passerelle (document A). Voyant allumé, port actif. Journal de
SRV-01 (document E) : le bail de PC-01 est renouvelé à 08:14, mais les demandes de la carte du
portable sont marquées **ignored**.

**Raisonnement.** APIPA : aucun bail reçu. Le lien est présent et le serveur fonctionne (il
renouvelle PC-01) ; il **reçoit** les demandes du portable mais les **ignore**. La configuration
de l'atelier ne sert que les cartes enregistrées (réservations) : la carte neuve ne l'est pas.
Les autres postes fonctionnent parce qu'ils sont enregistrés — et qu'ils ont un bail en cours.

**Correction.** Avec l'accord du responsable : enregistrer la MAC du portable (réservation hors
des adresses déjà attribuées), recharger le service, `ipconfig /renew`.

**Validation.** Le journal montre DHCPOFFER puis DHCPACK ; adresse 192.168.20.x, ping de
{ROUTER_IP}, ouverture d'un site et du partage.

**Compte rendu.** « LT-02 en APIPA (169.254.37.112) : demandes DHCP ignorées par SRV-01, qui ne
sert que les cartes enregistrées. MAC enregistrée avec l'accord de M. Durant ; bail obtenu,
tests réussis. Rappel : le filtrage par MAC organise les baux, il ne protège pas le réseau. »

<h3 class="jc-example-title">Cas 2 — Ping par adresse OK, nom interne KO</h3>

**Constat.** Sur PC-02, Internet fonctionne, mais l'application de gestion, qui se connecte à
`{SRV_FQDN}`, affiche « serveur introuvable ».

**Relevés.**

{_console(*case2_lines)}

Configuration : adresse fixe {CASE2_HOST.ip}/24, passerelle {CASE2_HOST.gateway}, DNS
**{CASE2_HOST.dns[0]}**.

**Raisonnement.** Le serveur répond par adresse : réseau et serveur fonctionnent. Le nom ne
l'est pas : PC-02 interroge le DNS du fournisseur ({ISP_DNS}), qui répond que `{SRV_FQDN}`
n'existe pas — il ne connaît pas les noms internes. Les sites Internet, eux, sont résolus : d'où
l'impression que « tout marche sauf l'application ».

**Correction.** DNS préféré **{SERVER_IP}** (ou retour en DHCP), `ipconfig /flushdns`.

**Validation.** `nslookup {SRV_FQDN}` répond {SERVER_IP} (document D) ; `nslookup {WEB_NAME}`
répond aussi ; l'application se connecte.

**Compte rendu.** « PC-02 utilisait le DNS du fournisseur (198.51.100.53), qui ne connaît pas
les noms internes ({DOMAIN}). DNS interne 192.168.20.5 rétabli ; noms internes et Internet
résolus ; application fonctionnelle. »

<h3 class="jc-example-title">Cas 3 — Un masque incorrect</h3>

**Constat.** Le poste d'accueil n'accède plus ni à Internet, ni au NAS, ni à l'imprimante ; il
répond pourtant au ping de PC-01.

**Relevés.** Adresse fixe `{CASE3_HOST.ip}`, masque **{CASE3_HOST.mask}** (/{CASE3_HOST.prefix}),
passerelle `{CASE3_HOST.gateway}`. À l'enregistrement, Windows avait averti que la passerelle
n'était pas dans le même sous-réseau.

**Raisonnement.** Avec /{CASE3_HOST.prefix}, le réseau du poste est **{c3.cidr}** (hôtes
{c3.host_range}). Hors de ce réseau : {far}. Dans ce réseau : {near}. Le poste ne joint donc
directement que les adresses {c3.host_range} ; pour le reste, il devrait passer par une passerelle
qui est **elle-même** hors de son réseau. PC-01 ({pc01.ip}/24) voit l'accueil comme local et
lui répond directement : ce ping réussi ne contredit pas le diagnostic.

**Correction.** Masque **255.255.255.0**, comme tout le réseau.

**Validation.** `ping {ROUTER_IP}`, `ping {NAS_IP}`, impression d'une page de test, ouverture
d'un site.

**Compte rendu.** « Masque 255.255.255.192 au lieu de 255.255.255.0 : le poste se croyait dans
{c3.cidr}, passerelle et serveurs hors de son réseau. Masque corrigé ; Internet, NAS et
imprimante vérifiés. »

<h3 class="jc-example-title">Cas 4 — Wi-Fi connecté, sans Internet</h3>

**Constat.** Le portable LT-03, revenu d'une mission chez un autre client, affiche « Aucun accès
Internet » sur le Wi-Fi de l'atelier.

**Relevés.**

{_console(*netsh_wlan_lines(CASE4_WIFI), "", *_case4_ipconfig())}

**Raisonnement.** Radio et authentification sont correctes (SSID {SSID}, signal
{CASE4_WIFI.signal_pct} %, WPA2 - Personnel). Le problème est l'**adressage** : la carte Wi-Fi
est en **adresse fixe** (DHCP activé : Non) dans le réseau 192.168.1.0/24 du client précédent,
avec sa passerelle 192.168.1.1, absente ici.

**Correction.** Propriétés IPv4 de la carte Wi-Fi : « Obtenir une adresse IP automatiquement »
et « Obtenir les adresses des serveurs DNS automatiquement », avec l'accord de l'utilisateur
(noter l'ancienne configuration s'il en a besoin chez ce client).

**Validation.** `ipconfig /all` : bail de SRV-01, adresse 192.168.20.x, passerelle {ROUTER_IP} ;
ping de la passerelle et ouverture d'un site.

**Compte rendu.** « LT-03 associé au Wi-Fi mais configuré en adresse fixe (192.168.1.50/24,
passerelle 192.168.1.1) d'un autre réseau. Carte remise en automatique ; bail obtenu ; accès
vérifié. Ancienne configuration notée pour l'utilisateur. »

<h3 class="jc-example-title">Cas 5 — Réseau local OK, Internet KO</h3>

**Constat.** À 8 h, plus aucun poste n'accède à Internet ; le NAS et l'imprimante fonctionnent.

**Relevés.** `ping {ROUTER_IP}` : 4 réponses ; `ping {WEB_IP}` : 100 % de perte (document B).
`tracert -d {WEB_IP}` : seul le saut 1, la box, répond (document C). Page d'état de la box :
« Synchronisation de la ligne : non établie » ; le voyant de la ligne clignote.

**Raisonnement.** Tous les postes sont touchés et le réseau local fonctionne : l'élément commun
est la box et sa liaison vers le fournisseur. La passerelle répond, rien au-delà : la ligne
n'est pas synchronisée. Le DNS n'est pas en cause (même les adresses IP ne répondent pas).

**Correction.** Contrôler d'abord le raccordement, sans réinitialiser la box : le câble entre
la box et la prise du fournisseur a été débranché lors du ménage de la veille ; on le rebranche.
Si la ligne ne s'était pas synchronisée, on aurait redémarré la box une seule fois avec l'accord
du client, puis contacté le fournisseur avec les relevés.

**Validation.** Ligne synchronisée, adresse publique affichée, `tracert` jusqu'à la
destination, site ouvert depuis deux postes.

**Compte rendu.** « Panne générale d'Internet, réseau local fonctionnel. Box joignable, ligne
non synchronisée. Câble de ligne débranché lors du ménage : rebranché ; synchronisation
rétablie, tests réussis. »

<h3 class="jc-example-title">Cas 6 — Imprimante réseau inaccessible malgré le ping</h3>

**Constat.** Depuis ce matin, PC-01 n'imprime plus sur IMP-01 ; PC-02 et PC-03 impriment.

**Relevés.** `ping {PRINTER_IP}` : 4 réponses. À l'impression : « Le service Spouleur
d'impression local n'est pas exécuté ». La file d'attente ne s'ouvre pas.

**Raisonnement.** L'imprimante répond et imprime pour les autres : ni le réseau ni
l'imprimante ne sont en cause. Seul PC-01 est touché, et son **service d'impression** est
arrêté : c'est la couche service.

**Correction.** Services : démarrer le **Spouleur d'impression** (type de démarrage :
automatique) ; s'il s'arrête de nouveau, supprimer, avec l'accord de l'utilisateur, le travail
bloqué qui le fait planter, puis relancer.

**Validation.** Service en cours d'exécution, file d'attente vide, page de test imprimée,
document de l'utilisateur imprimé.

**Compte rendu.** « PC-01 : service Spouleur arrêté (travail bloqué). Travail supprimé avec
l'accord de l'utilisatrice, service redémarré ; impression vérifiée. Réseau et imprimante non
en cause (ping OK, autres postes OK). »
"""


def _pitfalls() -> str:
    return """> **Toucher à l'IP sans lien.** « Média déconnecté » ou `NO-CARRIER` : on cherche le câble et le
> port, pas l'adresse.

> **Conclure sur la seule APIPA** que « le serveur DHCP est en panne » : lien, port, VLAN,
> étendue et filtrage sont aussi possibles.

> **Croire que « les autres postes marchent » prouve que le DHCP fonctionne** : ils peuvent
> vivre sur un bail en cours.

> **Dire « Internet est en panne »** quand seul le nom ne répond pas : c'est le DNS.

> **Utiliser un DNS public sur un réseau d'entreprise** : les noms internes ne sont plus
> résolus.

> **Prendre une ligne d'étoiles au milieu d'un tracert pour une panne** alors que la
> destination est atteinte.

> **Conclure « machine éteinte »** parce qu'un ping ne répond pas : l'ICMP peut être filtré.

> **Conclure « réseau OK, donc le partage aussi »** : le ping ne teste ni le port 445, ni le
> compte, ni les droits.

> **Supposer une erreur de VLAN sans indice** dans les relevés.

> **Lancer `ipconfig /release` à distance** ou sur un poste en production sans prévenir.

> **Changer plusieurs réglages à la fois** : on ne sait plus lequel a corrigé (ou aggravé) la
> situation.

> **Réinitialiser la box « pour voir »** : identifiants du fournisseur et configuration perdus.

> **Confondre corrélation et preuve** : « c'est arrivé après la mise à jour » n'est qu'une
> piste.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : huit analyses de relevés, cinq arbres de décision ou
procédures (dont une remise en ordre et un classement), quatre dossiers multi-postes et trois
rapports d'intervention. Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR24_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR24_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est un scénario complet : toutes les informations
nécessaires sont dans l'énoncé et ses documents (relevés, pages d'état, tableaux fictifs).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** La **lecture exacte des relevés**, la **localisation** de la
panne (couche, périmètre), le **raisonnement** (test discriminant, preuve), une **correction**
autorisée et sa **validation** — pas la récitation de sigles. Une autre démarche valide et
justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé. Une action dangereuse ou non
autorisée (réinitialisation de la box, scan, modification de production sans accord) est
toujours pénalisée.
"""


def _memo() -> str:
    return f"""## Mémo

- **Cerner** : symptôme exact, périmètre (un poste/tous, filaire/Wi-Fi, local/Internet),
  chronologie, changements récents, topologie.
- **Ordre** : physique → IP/masque → passerelle → IP distante → DNS → service.
- **Pas de lien = pas de diagnostic IP.** Duplex, CRC, PoE, longueur ({ETHERNET_MAX_M} m), radio.
- **APIPA** 169.254.0.0/16 = aucun bail ; **indice, pas preuve**. Autres postes OK ≠ DHCP OK.
- **DHCP** : DORA, bail, étendue, options passerelle et DNS ; relais si serveur dans un autre
  réseau ; second serveur = adresses d'un autre réseau.
- **DNS** : ping IP OK + nom KO = DNS ; NXDOMAIN = nom inexistant ; délai dépassé = serveur
  injoignable ; DNS public ≠ noms internes ; `ipconfig /flushdns`.
- **Passerelle** : local → passerelle → distant ; tracert situe l'arrêt ; route par défaut ;
  masque faux = passerelle hors réseau ; NAT de la box ; **ICMP parfois filtré**.
- **Switch/VLAN** : table MAC, port désactivé, mauvais VLAN = autre réseau ; trunk/access en
  complément ; pas de VLAN supposé sans indice.
- **Wi-Fi** : radio (SSID, BSSID, signal, bande, canal) → authentification (WPA2/WPA3, clé) →
  IP (DHCP après association).
- **Partage** : port 445, nom, chemin UNC, compte, droits partage + NTFS (le plus restrictif).
  **Imprimante** : file, port, spouleur.
- **Sécurité** : autorisation, état initial, retour arrière, une modification à la fois, pas de
  scan non autorisé, journaux confidentiels.
- **Rapport** : contexte, symptômes, périmètre, schéma, hypothèses, tests et sorties, cause
  (confirmée ou incertaine), correction, tests finaux, prévention, restitution.

## Glossaire des termes employés

- **APIPA** : adresse 169.254.x.y qu'un poste s'attribue sans réponse DHCP.
- **BSSID** : adresse MAC de la radio d'un point d'accès pour un SSID.
- **CRC** : contrôle d'intégrité d'une trame ; une erreur CRC = trame abîmée.
- **Duplex** : full (émission et réception simultanées) ou half (l'une ou l'autre).
- **Étendue DHCP** : plage d'adresses distribuées par le serveur.
- **NAT** : traduction des adresses privées en adresse publique par la box.
- **NXDOMAIN** : réponse DNS « ce nom n'existe pas ».
- **PoE** : alimentation d'un équipement par le câble réseau.
- **Relais DHCP** : équipement qui transmet les demandes DHCP vers un serveur d'un autre réseau.
- **SSID** : nom d'un réseau Wi-Fi.
- **Test discriminant** : test dont le résultat départage deux hypothèses.
- **UNC** : chemin réseau `\\\\serveur\\partage`.
- **VLAN** : réseau virtuel isolé sur un switch administrable.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 6 : épreuve uniquement écrite, exigences AP-32
  (« Connexions et interventions en cas de panne internet ») et AP-37 (« Dépannage de problèmes
  simples d'accès au réseau »). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **DHCP** : RFC 2131 (DORA, bail, renouvellement), RFC 2132 (options 3 « routeur » et 6
  « DNS ») ; **relais DHCP** : RFC 1542 ; **APIPA / lien local** : RFC 3927 ; **adresses de
  documentation** utilisées pour les adresses publiques fictives : RFC 5737 ; **NAT** :
  RFC 3022 ; **adresses privées** : RFC 1918.
- **Ethernet et PoE** : IEEE 802.3 (négociation, duplex, 802.3af et 802.3at) ; **Wi-Fi** :
  IEEE 802.11, Wi-Fi Alliance (WPA2, WPA3, SAE) ; **VLAN** : IEEE 802.1Q.
- **Commandes** : documentation Microsoft (`ipconfig`, `ping`, `tracert`, `nslookup`, `arp`,
  `route`, `netstat`, `netsh wlan`, `Test-NetConnection`) et pages de manuel Linux (`ip-link`,
  `ip-route`, `ip-neighbour`, `dig`, `ss`, `journalctl`, `nmcli`, `resolvectl`), dnsmasq ;
  présentation simplifiée dans les captures fictives.

Les relevés du cours, des exercices et du mini-examen (statistiques de ping, sauts de tracert,
réponses DNS, journaux DHCP, état Wi-Fi, ports du switch, tables ARP et routes) sont
**produits par programme** depuis le réseau de référence, et les calculs d'adressage sont faits
avec le module `ipaddress` de Python, **vérifiés par des tests automatiques** ; aucun schéma
n'est tiré d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande les interventions en cas de panne Internet (AP-32) et le
dépannage de problèmes simples d'accès au réseau (AP-37). Sont des **compléments**, signalés
comme tels :

- la rédaction de la procédure et du rapport d'intervention (AP-C01, approfondie en PR29) et
  la protection des données du client (AP-C03 : journaux confidentiels, état initial) ;
- les VLAN, ports trunk/access, le relais DHCP, le PoE et la protection DHCP des switchs ;
- les outils PowerShell (`Test-NetConnection`, `Get-NetTCPConnection`) et Linux
  (`resolvectl`, `nmcli`, `ss`).

## Supports fictifs

Le réseau de l'atelier, les relevés, les captures, les journaux, les pages d'état et les
adresses MAC de ce cours sont **fictifs** et reconstitués pour l'entraînement ; la
présentation réelle varie selon les systèmes, leurs versions et leur langue. Aucun n'est une
question officielle ou déjà posée par le Jury.
"""


def pr24_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR24 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR24 — 1. Démarche en couches : périmètre, chronologie, hypothèses et preuves", _layers()),
        ("PR24 — 2. Physique et liaison : câbles, voyants, ports, duplex, PoE et radio", _physical()),
        ("PR24 — 3-4. Configuration IP et DHCP : APIPA, doublons, bail, étendue et relais", _ip_dhcp()),
        ("PR24 — 5. DNS : résolution de noms, serveurs interne et externe, cache", _dns()),
        ("PR24 — 6-7. Passerelle, routage, NAT, filtrage, switch et VLAN", _routing_switching()),
        ("PR24 — 8. Wi-Fi : radio, authentification puis adressage", _wifi()),
        ("PR24 — 9. Partages et imprimantes : réseau joignable, partage inaccessible", _shares()),
        ("PR24 — 10-11. Outils Windows et Linux : lire avant de modifier", _tools()),
        ("PR24 — 12. Procédure ordonnée et arbre de diagnostic", _procedure()),
        ("PR24 — 13. Tableaux symptôme → test discriminant → action et pannes combinées", _symptoms()),
        ("PR24 — 14-15. Sécurité de l'intervention et rapport professionnel", _safety_report()),
        ("PR24 — Exemples : six cas intégralement résolus", _examples()),
        ("PR24 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR24 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR24 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR24 — Fiche mémo et glossaire", _memo()),
        ("PR24 — Sources et compléments pédagogiques", _sources()),
    ]

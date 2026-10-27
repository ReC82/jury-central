"""Cours PR21 « Connexion directe de deux PC et mini-réseau » — parcours AMPCR pratique écrite
(ticket #221).

Matière : intégralement celle du ticket #221 (carte réseau, câble droit ou croisé historique et
Auto MDI-X, voyants de lien ; adresses statiques 192.168.10.1/24 et .2/24, masque, absence de
passerelle en réseau isolé ; tests ping, ARP et pare-feu ; permissions et partage de fichiers ;
extension à 3–6 PC via un switch ; DHCP ou statique ; routeur, passerelle et DNS ; plan
d'adressage ; erreurs IP dupliquée, masque, DHCP et liaison ; procédure de mise en service et
recette ; cinq cas résolus), découpée en blocs titrés (le titre pilote le type de carte,
`app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert »
ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr21_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr21_bank`. L'adressage IPv4 détaillé vient de PR20, le brochage du câble
croisé de PR15, l'installation physique de PR18, le dépannage complet de PR24 (publiés, liens).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr21_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr21_figures import (
    ACCEPT_PROC_FIGURE,
    ADDRESS_RANGES,
    BOX_HOSTS,
    BOX_IP,
    CABLE_FIGURE,
    CHECKS,
    CROSSOVER_LINKS,
    DHCP_VS_STATIC,
    DIALOG_FIGURE,
    DIRECT_FIGURE,
    DIRECT_PROC_FIGURE,
    EXTEND_PROC_FIGURE,
    FIREWALL_FIGURE,
    FIREWALL_STEPS,
    ISOLATED_HOSTS,
    LED_STATES,
    MAP_FIGURE,
    MINI_BOX_FIGURE,
    MINI_ISOLATED_FIGURE,
    OUT_FAILURE,
    OUT_REPLY,
    OUT_TIMEOUT,
    OUT_UNREACHABLE,
    PAIRS_USED,
    PC_A,
    PC_B,
    PING_FIGURE,
    POOL,
    PRINTER,
    PROCEDURES,
    SHARE_NAME,
    SHARE_UNC,
    SHARE_UNC_NAME,
    STATIC_FIGURES,
    TREE_FIGURE,
    WRITTEN_AT,
    AddressPlan,
    Host,
    cable_needed,
    direct_errors,
    ipconfig_disconnected_lines,
    ipconfig_duplicate_lines,
    link_up,
    ping_lines,
    ping_outcome,
    plan_errors,
    same_network,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR21_TITLE = "Connexion directe de deux PC et mini-réseau"
PR21_SLUG = "ampcr-pratique-pr21"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr21")
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


def _console(lines: tuple[str, ...]) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _led_table() -> str:
    rows = "\n".join(f"| **{state}** | {meaning} | {then} |" for state, meaning, then in LED_STATES)
    return "| Ce que tu vois | Ce que cela prouve | Pistes et suite |\n|---|---|---|\n" + rows


def _crossover_table() -> str:
    rows = "\n".join(f"| {a} | {b} |" for a, b in CROSSOVER_LINKS)
    return "| Broche, bout T568A | Arrive sur la broche, bout T568B |\n|---|---|\n" + rows


def _ping_table() -> str:
    meaning = {
        OUT_REPLY: "Lien, adressage et pare-feu corrects dans les deux sens.",
        OUT_TIMEOUT: "La demande arrive ; le pare-feu la refuse, ou le destinataire ne sait pas répondre (masque).",
        OUT_UNREACHABLE: "Message du poste lui-même : personne n'a cette adresse (éteint, adresse fausse, câble côté distant). Compté comme « reçu » !",
        OUT_FAILURE: "Rien n'est émis : carte sans lien, ou destination hors réseau sans passerelle.",
    }
    message = {
        OUT_REPLY: "Réponse de 192.168.10.2 : octets=32 temps<1ms TTL=128",
        OUT_TIMEOUT: "Délai d'attente de la demande dépassé.",
        OUT_UNREACHABLE: "Réponse de 192.168.10.1 : Impossible de joindre l'hôte de destination.",
        OUT_FAILURE: "PING : échec de la transmission. Défaillance générale.",
    }
    rows = "\n".join(f"| `{message[o]}` | **{o.split(' :')[0]}** | {meaning[o]} |" for o in meaning)
    return "| Message affiché (Windows) | Résultat | Ce que cela prouve |\n|---|---|---|\n" + rows


def _dhcp_table() -> str:
    rows = "\n".join(f"| **{mode}** | {how} | {when} |" for mode, how, when in DHCP_VS_STATIC)
    return "| Mode | Comment | Pour quoi |\n|---|---|---|\n" + rows


def _ranges_table() -> str:
    rows = "\n".join(
        f"| .{a}" + ("" if a == b else f" à .{b}") + f" | {b - a + 1} | {label} |" for a, b, label in ADDRESS_RANGES
    )
    return "| Adresses (192.168.10.…) | Nombre | Usage |\n|---|---|---|\n" + rows


def _plan_table(hosts: tuple[Host, ...]) -> str:
    rows = "\n".join(
        f"| {h.name} | {h.role} | {h.ip} | {h.mask} | {h.gateway or '—'} | {h.dns[0] if h.dns else '—'} | {'DHCP' if h.dhcp else 'fixe'} |"
        for h in hosts
    )
    return "| Appareil | Rôle | Adresse | Masque | Passerelle | DNS | Mode |\n|---|---|---|---|---|---|---|\n" + rows


def _checks_table() -> str:
    rows = "\n".join(f"| {i} | {what} | {diag} |" for i, (_k, what, diag) in enumerate(CHECKS, start=1))
    return "| N° | Contrôle | Piste si c'est le premier échec |\n|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1))


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C2_OLD_STRAIGHT = link_up("Câble droit", "PC", "PC")
C2_OLD_CROSS = link_up("Câble croisé", "PC", "PC")
C3_OUTCOME = ping_outcome(PC_B, PC_A.ip, PC_A, icmp_allowed=False)
C5_B = Host("PC-D", "poste de la comptable", "192.168.10.4", 16, None, (), "3C-52-82-4D-10-04")
C5_NEW = Host("PC-F", "nouveau poste", "192.168.10.3", 24, None, (), "3C-52-82-4D-10-06")
C5_DUP = [e for e in plan_errors(AddressPlan(
    "192.168.10.0/24", (*ISOLATED_HOSTS, C5_NEW), "192.168.10.254", "192.168.10.254")) if "doublon" in e]

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Copier les dossiers d'un PC vers un portable",
        (
            "Un traducteur indépendant veut copier chaque semaine ses dossiers de son PC de bureau vers "
            "son portable, sans box ni clé USB. Les deux cartes sont récentes (1 Gb/s, Auto MDI-X), sous Windows."
        ),
        (
            f"**Liaison** : cartes Auto MDI-X → {cable_needed('PC', 'PC', auto_a=True, auto_b=True).lower()} ; on prend un câble droit ; voyants de lien allumés des deux côtés, 1 Gb/s.",
            f"**Adresses** : PC-A {PC_A.ip}/24, PC-B {PC_B.ip}/24, passerelle et DNS vides ; contrôle : {'même réseau' if same_network(PC_A, PC_B) else 'réseaux différents'}, {len(direct_errors(PC_A, PC_B))} erreur relevée.",
            f"**Pare-feu et partage** : profil Privé ; partage {SHARE_NAME} pour le compte tech (Modifier) ; ping dans les deux sens puis ouverture de {SHARE_UNC}.",
        ),
        f"Liaison directe 1 Gb/s par câble droit, PC-A {PC_A.ip}/24 et PC-B {PC_B.ip}/24 sans passerelle, partage {SHARE_NAME} réservé au compte tech, testé en lecture et écriture.",
    ),
    (
        "Cas 2 — Deux vieux PC qui ne s'allument pas en réseau",
        (
            "Un musée relie deux PC de 2005 (cartes 100 Mb/s sans Auto MDI-X) qui pilotent une exposition. "
            "Avec le câble droit fourni, aucun voyant ne s'allume ; les deux cartes fonctionnent sur un switch."
        ),
        (
            f"**Constat** : deux cartes MDI ; avec un câble droit, l'émission de l'une arrive sur l'émission de l'autre → lien {'possible' if C2_OLD_STRAIGHT else 'impossible'}.",
            f"**Solution** : câble croisé T568A ↔ T568B (1→3, 2→6, 3→1, 6→2) → lien {'établi' if C2_OLD_CROSS else 'impossible'} ; ou petit switch entre les deux avec deux câbles droits.",
            "**Contrôle** : voyants allumés, vitesse 100 Mb/s affichée, puis adresses et ping comme au cas 1.",
        ),
        "Câble croisé fabriqué et étiqueté « croisé » (ou switch intercalé), voyants allumés à 100 Mb/s, liaison validée par ping.",
    ),
    (
        "Cas 3 — Le ping ne répond pas, mais tout semble juste",
        (
            f"Après une connexion directe, le ping de PC-B vers PC-A ({PC_A.ip}) donne quatre délais "
            "dépassés. Les voyants sont allumés, les adresses et masques sont justes. Windows affiche « Réseau non identifié »."
        ),
        (
            f"**Relevé** : ping → {C3_OUTCOME.split(' :')[0].lower()} ; arp -a sur PC-B contient la MAC de PC-A ({PC_A.mac.lower()}) : PC-A a répondu à l'ARP.",
            "**Cause** : sans passerelle, réseau non identifié → profil Public : le pare-feu de PC-A refuse l'écho ICMP (et le partage).",
            "**Correction** : profil Privé, partage de fichiers et d'imprimantes activé (règle d'écho ICMPv4) ; pare-feu laissé actif ; ping : 4 réponses.",
        ),
        "Pare-feu de PC-A en cause (profil Public) : profil Privé et règle d'écho activée, pare-feu actif, ping et partage validés.",
    ),
    (
        "Cas 4 — De deux à six appareils, puis Internet",
        (
            "Le traducteur s'associe : trois postes de plus, une imprimante réseau, puis la box de l'opérateur "
            "pour Internet. On garde PC-A et son partage tels quels."
        ),
        (
            f"**Réseau isolé** : switch 8 ports, câbles droits ; adresses fixes {ISOLATED_HOSTS[0].ip} à {ISOLATED_HOSTS[-1].ip}/24, sans passerelle ; contrôle du plan : {len(plan_errors(AddressPlan('192.168.10.0/24', ISOLATED_HOSTS, '192.168.10.254', '192.168.10.254')))} erreur.",
            f"**Avec la box** : box en {BOX_IP} (passerelle, DNS, DHCP {POOL[0]}–{POOL[1]}) ; PC-A en .1 fixe et imprimante en {PRINTER.ip} fixe, avec passerelle et DNS {BOX_IP} ; les autres en DHCP.",
            "**Validation** : sur chaque poste, lien, adresse, doublon, ping de la box et de PC-A, partage, impression, site par son nom.",
        ),
        f"Mini-réseau en étoile autour d'un switch, box en {BOX_IP}, adresses fixes hors de l'étendue DHCP, plan d'adressage remis au client.",
    ),
    (
        "Cas 5 — Après l'extension, deux erreurs à la fois",
        (
            "Dans le réseau isolé du cas 4, un stagiaire ajoute PC-F en 192.168.10.3 et règle le masque de PC-D "
            "en 255.255.0.0. L'accueil (PC-C) perd le réseau par moments ; PC-D joint encore tout le monde."
        ),
        (
            f"**Doublon** : {C5_DUP[0] if C5_DUP else ''} PC-F affiche « (Dupliqué) » → nouvelle adresse libre (.6).",
            f"**Masque** : PC-D en /16 voit encore les postes du /24 ({'même réseau' if same_network(C5_B, PC_A) else 'réseaux différents'} avec PC-A) : la panne ne se voit pas, mais le plan est faux → 255.255.255.0.",
            "**Recette** : refaire les contrôles de PC-C, PC-D et PC-F, mettre le plan d'adressage à jour.",
        ),
        "Doublon de .3 corrigé (PC-F en .6), masque de PC-D remis en 255.255.255.0, contrôles refaits et plan mis à jour.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant une demande de client, des relevés de commandes ou le schéma d'un petit réseau, on
attend de toi une **mise en service raisonnée** : quel câble, quelles adresses, quels tests,
comment lire leurs résultats et comment prouver que tout fonctionne. Tu dois savoir :

1. **relier deux PC directement** : carte réseau, **câble droit ou croisé**, **Auto MDI-X**,
   **voyants de lien** ;
2. **configurer des adresses statiques** ({PC_A.ip}/24 et {PC_B.ip}/24), le **masque**, et
   expliquer pourquoi **aucune passerelle** n'est nécessaire dans un réseau isolé ;
3. **tester** avec **ping** et la **table ARP**, et régler le **pare-feu** ;
4. **partager un dossier** avec les bons **comptes et permissions** ;
5. **étendre** la liaison à **3 à 6 PC** avec un **switch** ;
6. choisir entre **DHCP et adresses statiques**, placer **routeur, passerelle et DNS**, écrire un
   **plan d'adressage** ;
7. reconnaître les **erreurs** : **IP dupliquée**, **masque**, **DHCP**, **liaison** ;
8. suivre une **procédure de mise en service** et faire la **recette**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-28")}
{_req("AP-38")}

Ce sont deux exigences **officielles** (consignes, p. 6). Le brochage du câble croisé est détaillé
en [PR15](/uaa/ampcr-pratique-pr15), l'installation physique (prises, baie, recette du câblage) en
[PR18](/uaa/ampcr-pratique-pr18), les équipements et modèles en [PR19](/uaa/ampcr-pratique-pr19),
l'adressage IPv4 (masques, calculs, DHCP) en [PR20](/uaa/ampcr-pratique-pr20) et le dépannage
complet en [PR24](/uaa/ampcr-pratique-pr24). Les comptes et groupes (PR22) et les partages et
permissions (PR23) seront approfondis dans leurs cours, publiés ensuite dans l'ordre du parcours.

## Lien avec la théorie

La théorie AMPCR présente le câblage et le réseau local :
[MC15 Câblage Ethernet et RJ45 : T568A/T568B](/uaa/ampcr-mc15) et [MC16 IPv4 : adresses, masque, passerelle et plages privées](/uaa/ampcr-mc16).
Ce cours-ci est **pratique** : schémas, relevés de commandes et fiches de recette à analyser et
à rédiger, comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont quatre **schémas à
compléter** et de nombreux **relevés de commandes**), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les postes, adresses MAC, relevés de commandes et entreprises de ce cours sont
> des **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}) ; les messages
> reprennent le format réel de Windows (en français) et de Linux, en version simplifiée. Les
> menus de Windows changent d'une version à l'autre : **la documentation de l'éditeur fait foi**.
> Aucun exercice n'est une question officielle ni une question déjà posée par le Jury.
"""


def _hardware() -> str:
    return f"""**Objectifs** : choisir le matériel et le câble d'une connexion directe entre deux PC.

## 1.1 La carte réseau

Chaque PC a une **carte réseau** Ethernet (intégrée à la carte mère ou ajoutée), avec une prise
RJ45 et une **adresse MAC** unique. Les cartes actuelles fonctionnent à 1 Gb/s ; un PC ancien peut
n'aller qu'à 100 Mb/s : le lien prend la vitesse de la **plus lente** des deux.

## 1.2 Câble droit ou croisé : la règle historique

En 10 et 100 Mb/s, une carte réseau **émet** sur les broches 1-2 et **reçoit** sur 3-6 (port
**MDI**) ; un port de switch ou de hub fait l'inverse (port **MDI-X**). Entre un PC et un switch,
un **câble droit** (même norme aux deux bouts) relie l'émission de l'un à la réception de l'autre.
Entre **deux appareils de même type** (deux PC, deux switchs, un PC et le port routé d'un ancien
routeur), il faut **croiser** : c'est le **câble croisé**, T568A à un bout et T568B à l'autre
(brochage détaillé en [PR15](/uaa/ampcr-pratique-pr15)) :

{_crossover_table()}

## 1.3 L'Auto MDI-X : la règle qui disparaît

Une carte **Auto MDI-X** détecte le câble et **inverse elle-même** émission et réception : il suffit
qu'**un seul** des deux ports le fasse pour que n'importe quel câble en bon état fonctionne. Presque
toutes les cartes 1 Gb/s actuelles le font : on utilise alors un **câble droit**, le seul qu'on
stocke encore. Le câble croisé reste utile pour du **matériel ancien** des deux côtés. En 1 Gb/s,
les **quatre paires** transportent des données ({", ".join(f"{a}-{b}" for a, b in PAIRS_USED["1 Gb/s"])}), contre deux
en 10/100 Mb/s ({", ".join(f"{a}-{b}" for a, b in PAIRS_USED["10/100 Mb/s"])}).

{_fig(CABLE_FIGURE)}

**Procédure professionnelle (à rédiger)** : identifier les deux cartes (vitesse, Auto MDI-X dans
la fiche) → choisir le câble (droit si un port fait l'Auto MDI-X, sinon croisé) → tester le câble
au testeur → étiqueter un câble croisé « croisé ».

**Erreur fréquente** : chercher une panne de configuration alors qu'un câble droit relie deux
vieux PC sans Auto MDI-X ; ranger un câble croisé avec les câbles droits sans étiquette.

**À l'écrit** : « carte du portable Auto MDI-X : câble droit suffisant ; liaison à 100 Mb/s,
vitesse de la carte la plus lente ».

**Repère rapide** : **même type → croisé · types différents → droit · un port Auto MDI-X → tout
câble**. Exercices liés : {_ex("E04", "E10")}.
"""


def _leds() -> str:
    return f"""**Objectifs** : prouver que le lien physique est établi avant de toucher à la configuration.

## 2.1 Lire les voyants

À côté de la prise RJ45 de la carte (et de chaque port d'un switch), un **voyant de lien** s'allume
quand les deux cartes se sont **négociées** ; un voyant d'**activité** clignote quand des trames
passent. Les couleurs (vitesse) **dépendent du fabricant** : on lit la notice.

{_led_table()}

## 2.2 Ce que montre le système

Sous Windows, une carte sans lien affiche **« Média déconnecté »** dans `ipconfig /all` et n'a
plus d'adresse ; la vitesse négociée se lit dans Paramètres → Réseau et Internet → Ethernet. Sous
Linux, `ip link` affiche **NO-CARRIER** et `state DOWN` ; `ethtool enp3s0` donne la vitesse.

{_console(ipconfig_disconnected_lines(PC_B))}

**Procédure professionnelle (à rédiger)** : brancher → regarder le voyant des deux côtés →
lire l'état et la vitesse dans le système → sans lien : câble, type de câble, carte activée, PC
distant allumé.

**Erreur fréquente** : modifier l'adresse IP alors que le voyant est éteint ; conclure « le réseau
fonctionne » parce que le voyant clignote (l'adressage peut encore être faux).

**À l'écrit** : « voyant éteint et Média déconnecté : panne de liaison ; câble droit entre deux
cartes sans Auto MDI-X remplacé par un câble croisé ».

**Repère rapide** : **pas de voyant = pas de lien = rien d'autre à tester**. Exercices liés :
{_ex("E06")}.
"""


def _addressing() -> str:
    return f"""**Objectifs** : donner aux deux PC une configuration IPv4 fixe et juste, sans passerelle.

## 3.1 Pourquoi des adresses fixes

Deux PC reliés en direct n'ont **aucun serveur DHCP** : en adresse automatique, chacun se donne une
adresse **169.254.x.x** (adresse automatique privée). On saisit donc des **adresses fixes** du
**même réseau privé**, **différentes**, avec le **même masque** :

| Poste | Adresse IPv4 | Masque | Passerelle | DNS |
|---|---|---|---|---|
| {PC_A.name} | {PC_A.ip} | {PC_A.mask} (/24) | (vide) | (vide) |
| {PC_B.name} | {PC_B.ip} | {PC_B.mask} (/24) | (vide) | (vide) |

Avec le masque 255.255.255.0, les trois premiers octets désignent le **réseau** (192.168.10.0/24)
et le dernier le **poste** (de 1 à 254 ; .0 et .255 sont réservés). Le calcul détaillé des
masques est l'objet de [PR20](/uaa/ampcr-pratique-pr20).

## 3.2 Pas de passerelle, pas de DNS

La **passerelle** est l'adresse du **routeur** à qui un poste confie ce qui sort de son réseau.
Ici, les deux PC sont dans le **même réseau** et il n'existe **aucun routeur** : la passerelle reste
**vide**. Le **DNS** traduit des noms de sites en adresses : sans Internet, il reste vide aussi.

{_fig(DIRECT_FIGURE)}

{_fig(DIALOG_FIGURE)}

Sous Windows : Paramètres → Réseau et Internet → Ethernet → Attribution d'adresse IP → Manuel, ou
la fenêtre « Protocole Internet version 4 » ci-dessus. En commande (administrateur) :
`netsh interface ipv4 set address name="Ethernet" static {PC_B.ip} {PC_B.mask}`. Sous Linux
(NetworkManager) : `nmcli con mod "Connexion filaire 1" ipv4.method manual ipv4.addresses
{PC_B.ip}/24` puis `nmcli con up "Connexion filaire 1"`.

**Procédure professionnelle (à rédiger)** : choisir un réseau privé → attribuer .1 et .2 → même
masque → passerelle et DNS vides → vérifier avec `ipconfig /all` (ou `ip addr`).

**Erreur fréquente** : laisser un PC en automatique (169.254) ; saisir un masque différent ; mettre
l'adresse de l'autre PC en passerelle.

**À l'écrit** : « PC-A 192.168.10.1/24, PC-B 192.168.10.2/24 : même réseau ; passerelle vide car
aucun routeur ».

**Repère rapide** : **même réseau · adresses différentes · même masque · passerelle vide**.
Exercices liés : {_ex("E09", "E13")}.
"""


def _tests() -> str:
    return f"""**Objectifs** : prouver la liaison par des commandes et lire leurs messages sans se tromper.

## 4.1 Le ping et la table ARP

`ping 192.168.10.2` envoie quatre **demandes d'écho** (ICMP) et attend les réponses. Avant la
première, le PC demande à tout le réseau « qui a 192.168.10.2 ? » (**requête ARP**) ; la réponse
donne la **MAC** du destinataire, rangée dans la **table ARP** (`arp -a` sous Windows,
`ip neigh` sous Linux). Une MAC présente dans la table prouve que le poste distant **existe et a
répondu**, même si le ping échoue ensuite.

{_fig(PING_FIGURE)}

## 4.2 Lire les quatre messages possibles

{_ping_table()}

Piège classique : « Impossible de joindre l'hôte de destination » est compté comme **reçu**, d'où
un **0 % de perte trompeur** :

{_console(ping_lines(PC_A, "192.168.10.9", OUT_UNREACHABLE)[:5])}

## 4.3 Le pare-feu

Une connexion sans passerelle est un **réseau non identifié** : Windows lui donne le profil
**Public**, où le pare-feu refuse l'écho ICMP et le partage de fichiers. On ne coupe pas le
pare-feu : on règle le profil et la règle nécessaire.

{_fig(FIREWALL_FIGURE)}

""" + "\n".join(f"- **{label}** : {detail}" for label, detail in FIREWALL_STEPS) + f"""

**Procédure professionnelle (à rédiger)** : `ipconfig /all` sur les deux PC → ping dans **les deux
sens** → `arp -a` → si délai dépassé avec MAC connue : pare-feu → noter les résultats.

**Erreur fréquente** : désactiver le pare-feu « pour voir » et l'oublier ; lire « 0 % de perte »
sans regarder **qui** répond.

**À l'écrit** : « ping sans réponse mais MAC de PC-A dans arp -a : réseau correct, pare-feu de PC-A
(profil Public) ; profil Privé, règle d'écho activée ».

**Repère rapide** : **ping dans les deux sens + arp -a · lire qui répond · pare-feu réglé, pas
coupé**. Exercices liés : {_ex("E08", "E14")}.
"""


def _sharing() -> str:
    return f"""**Objectifs** : partager un dossier entre les deux PC avec les bons comptes et permissions.

## 5.1 Partager sous Windows

Sur PC-A (administrateur) : clic droit sur le dossier `C:\\{SHARE_NAME}` → Propriétés → **Partage**
→ **Partage avancé** → « Partager ce dossier », nom **{SHARE_NAME}** → **Autorisations** : retirer
« Tout le monde », donner **Modifier** (ou **Lecture**) au compte autorisé. Onglet **Sécurité**
(permissions NTFS du dossier) : même compte, **Modification** ou **Lecture et exécution**. En
commande : `net share {SHARE_NAME}=C:\\{SHARE_NAME} /GRANT:tech,CHANGE`. Le profil réseau doit être
**Privé**, avec le partage de fichiers activé (le pare-feu ouvre alors le port TCP 445).

## 5.2 Comptes et permissions

Celui qui ouvre le partage depuis PC-B doit s'identifier avec un **compte de PC-A** (par exemple
`PC-A\\tech`) **qui a un mot de passe** : par défaut, Windows refuse à travers le réseau un compte
sans mot de passe. Par le réseau, la permission effective est **la plus restrictive** des deux :
partage « Lecture » + dossier « Modification » = **lecture seule**. Les groupes et permissions
détaillés sont l'objet des cours PR22 et PR23.

## 5.3 Accéder au partage

Depuis PC-B : `{SHARE_UNC}` dans l'Explorateur (ou `{SHARE_UNC_NAME}` si le nom est résolu ; l'adresse
IP marche toujours), ou `net use Z: {SHARE_UNC} /user:PC-A\\tech`. Sous Linux :
`smbclient //{PC_A.ip}/{SHARE_NAME} -U tech`. **Test** : créer, modifier puis supprimer un fichier.

**Procédure professionnelle (à rédiger)** : créer le dossier → partager avec un nom → donner les
permissions au seul compte autorisé (partage + dossier) → profil Privé → ouvrir depuis l'autre PC
→ tester lecture et écriture → noter.

**Erreur fréquente** : laisser « Tout le monde : Contrôle total » ; régler le partage en Modifier
mais oublier l'onglet Sécurité (ou l'inverse) ; compte sans mot de passe.

**À l'écrit** : « partage Echange : tech en Modifier, NTFS tech en Modification ; accès
\\\\192.168.10.1\\Echange testé en écriture ».

**Repère rapide** : **un compte avec mot de passe · partage ET dossier · la plus restrictive
gagne**. Exercices liés : {_ex("E17", "E07")}.
"""


def _switch() -> str:
    return f"""**Objectifs** : passer de deux PC à un mini-réseau de 3 à 6 appareils avec un switch.

## 6.1 Le switch, centre de l'étoile

Au-delà de deux PC, on ajoute un **switch** : chaque appareil y est relié par **son propre câble
droit** (topologie en **étoile**, voir [PR19](/uaa/ampcr-pratique-pr19)). Un switch de 8 ports
suffit pour 6 appareils, avec de la réserve ; un switch non administrable fonctionne dès qu'il est
alimenté. Il **ne donne pas d'adresses** : il relie seulement les appareils du **même réseau**.

## 6.2 On garde le réseau de la connexion directe

On continue la suite : PC-C en .3, PC-D en .4, PC-E en .5, **même masque**, toujours **sans
passerelle** tant qu'il n'y a pas de box. Les deux premiers PC ne changent rien.

{_fig(MINI_ISOLATED_FIGURE)}

{_plan_table(ISOLATED_HOSTS)}

**Procédure professionnelle (à rédiger)** : compter les appareils → switch avec réserve →
un câble droit par appareil → adresses suivantes du plan → même masque → valider poste par poste.

**Erreur fréquente** : réutiliser une adresse déjà prise ; penser qu'un switch fournit les
adresses (c'est le rôle d'un serveur DHCP) ; mélanger un câble croisé non étiqueté avec les
câbles droits.

**À l'écrit** : « switch 8 ports, 5 câbles droits ; PC-C .3, PC-D .4, PC-E .5 /24 sans passerelle ».

**Repère rapide** : **un câble droit par appareil · même réseau · une adresse par appareil**.
Exercices liés : {_ex("E02", "E15")}.
"""


def _dhcp_router() -> str:
    return f"""**Objectifs** : choisir DHCP ou adresses fixes, placer la box, la passerelle et le DNS, et
écrire le plan d'adressage.

## 7.1 DHCP ou adresses statiques

{_dhcp_table()}

Une adresse fixe se choisit **hors de l'étendue DHCP**, sinon le serveur peut la donner aussi à un
autre appareil.

## 7.2 Routeur, passerelle et DNS

Pour aller sur Internet, on relie la **box** (routeur de l'opérateur) au switch. Elle devient :
la **passerelle** (adresse à laquelle les postes confient tout ce qui sort du réseau), le **DNS**
(elle relaie les requêtes de noms) et le **serveur DHCP** (adresse, masque, passerelle et DNS
donnés automatiquement). **Convention du cours** : la box en **{BOX_IP}**, pour garder .1 et .2.

{_fig(MINI_BOX_FIGURE)}

## 7.3 Le plan d'adressage

On l'écrit **avant** de configurer, et on le remet au client :

{_fig(MAP_FIGURE)}

{_ranges_table()}

{_plan_table(BOX_HOSTS)}

Contrôle du plan ci-dessus (même méthode qu'en PR20) : **{len(plan_errors(AddressPlan("192.168.10.0/24", BOX_HOSTS, BOX_IP, BOX_IP, POOL)))} erreur**.

**Procédure professionnelle (à rédiger)** : réseau et masque → plages (fixes, imprimantes, étendue
DHCP, box) → une ligne par appareil (adresse, masque, passerelle, DNS, mode) → configuration →
contrôle.

**Erreur fréquente** : adresse fixe dans l'étendue DHCP ; passerelle vers un PC au lieu de la box ;
oublier le DNS sur un poste à adresse fixe (Internet par adresse IP, mais aucun nom de site).

**À l'écrit** : « box {BOX_IP} : passerelle, DNS, DHCP {POOL[0]}–{POOL[1]} ; imprimante {PRINTER.ip} fixe hors étendue ».

**Repère rapide** : **fixe hors étendue · passerelle = box · DNS = box · plan écrit d'abord**.
Exercices liés : {_ex("E05", "E11", "E12", "E18", "E19")}.
"""


def _errors() -> str:
    dup_host = Host("PC-F", "nouveau poste", "192.168.10.3", 24, None, (), "3C-52-82-4D-10-06")
    return f"""**Objectifs** : reconnaître les quatre erreurs classiques et leur preuve dans les relevés.

## 8.1 Liaison

Voyant éteint, « Média déconnecté », NO-CARRIER : câble débranché ou coupé, câble droit entre deux
cartes sans Auto MDI-X, carte désactivée, PC distant éteint. Le ping affiche **Défaillance
générale** : rien ne peut partir.

## 8.2 DHCP

Adresse **169.254.x.x**, masque 255.255.0.0, pas de passerelle : le poste est en automatique et
**aucun serveur DHCP** n'a répondu (pas de box, box débranchée, poste sur un switch isolé). On
fixe une adresse, ou on rétablit le serveur DHCP, puis `ipconfig /renew`.

## 8.3 Adresse IP dupliquée

Deux appareils avec la **même adresse** : Windows signale un conflit et marque l'adresse
« **(Dupliqué)** » ; l'un des deux perd le réseau, parfois par intermittence.

{_console(ipconfig_duplicate_lines(dup_host))}

## 8.4 Masque ou réseau différents

Un masque différent ou un autre réseau : les deux postes n'ont pas la même idée du réseau. Selon le
sens, on lit **Défaillance générale** (destination hors réseau, pas de passerelle) ou **Délai
dépassé** (la demande arrive, la réponse ne sait pas repartir). Un masque trop large (/16) peut
même **fonctionner** dans un petit réseau : l'erreur se voit au plan, pas au ping.

{_fig(TREE_FIGURE)}

**Procédure professionnelle (à rédiger)** : suivre l'arbre, du lien au partage → s'arrêter au
premier contrôle en échec → corriger → reprendre au début → consigner.

**Erreur fréquente** : changer plusieurs réglages à la fois ; corriger l'adresse d'un poste sans
mettre le plan à jour.

**À l'écrit** : « 192.168.10.3(Dupliqué) : adresse déjà prise par PC-C ; PC-F mis en .6, plan
mis à jour ».

**Repère rapide** : **liaison → DHCP → doublon → masque → ARP → pare-feu → partage → Internet**.
Exercices liés : {_ex("E06", "E07", "E15", "E16")}.
"""


def _acceptance() -> str:
    return f"""**Objectifs** : mettre en service dans l'ordre et prouver le résultat par une recette écrite.

## 9.1 Mise en service

{_fig(DIRECT_PROC_FIGURE)}

{_fig(EXTEND_PROC_FIGURE)}

## 9.2 La recette

On contrôle **chaque poste** dans l'ordre ; le **premier contrôle en échec** désigne la piste :

{_checks_table()}

{_fig(ACCEPT_PROC_FIGURE)}

On remet au client : le **plan d'adressage**, le **schéma** du réseau, le **tableau de recette**
(poste, contrôle, preuve, OK/KO) et un **procès-verbal** daté et signé, avec les réserves ; les mots
de passe sont remis **à part**.

**Procédure professionnelle (à rédiger)** : préparer le tableau → contrôler chaque poste dans
l'ordre → corriger et refaire → consigner les preuves → faire signer.

**Erreur fréquente** : livrer sans tableau ; tester seulement Internet ; ne tester le ping que
dans un sens.

**À l'écrit** : « PC-03 : lien OK, 192.168.10.102 OK, pas de doublon, ping box et PC-A OK, partage
OK, site OK ».

**Repère rapide** : **un poste = une ligne · une preuve par contrôle · PV signé**. Exercices liés :
{_ex("E01", "E03", "E20")}.
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
        "Cinq situations résolues pas à pas avec les règles du cours : câble, adresses, tests, pare-feu, "
        "partage, extension et erreurs. Chaque conclusion s'appuie sur une preuve.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return """> **Câble droit entre deux vieux PC sans Auto MDI-X** : voyants éteints ; il faut un câble croisé.

> **Laisser les PC en adresse automatique** sans serveur DHCP : 169.254.x.x.

> **Masques différents** sur deux PC : selon le sens, défaillance générale ou délai dépassé.

> **Mettre l'autre PC en passerelle** dans une connexion directe : inutile et faux.

> **Lire « 0 % de perte »** sans voir que la réponse vient du poste lui-même.

> **Couper le pare-feu** au lieu de passer le profil en Privé et d'ouvrir la règle d'écho.

> **« Tout le monde : Contrôle total »** sur un partage ; compte sans mot de passe.

> **Adresse fixe dans l'étendue DHCP** de la box : doublon assuré tôt ou tard.

> **Croire que le switch donne les adresses** : c'est le rôle d'un serveur DHCP (la box).

> **Oublier passerelle et DNS** sur un poste à adresse fixe quand Internet est demandé.

> **Livrer sans recette écrite** ni plan d'adressage à jour.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (mise en service, extension, recette),
classements (câble droit ou croisé, adresse fixe ou DHCP, première piste en échec, lecture du
ping), **quatre schémas à compléter** (connexion directe, câbles, mini-réseau, carte des adresses),
**relevés de commandes** à analyser (ipconfig, ping, arp -a), plan d'adressage à vérifier, partage
d'un dossier, accès à Internet et tableau de recette. Rédige ta réponse sur papier **avant**
d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont
proposés dans [S'entraîner](/uaa/{PR21_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR21_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (configurations et relevés fictifs). **Aucune correction
n'est visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **diagnostic prouvé** par les relevés, le **choix justifié**
(câble, adresses, mode d'adressage), la **procédure** et la **recette** — pas la récitation de
sigles. Une autre solution technique juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Câble** : même type de port → croisé ; types différents → droit ; un port Auto MDI-X → tout câble.
- **Voyant** : éteint = pas de lien (« Média déconnecté ») ; rien d'autre à tester avant.
- **Connexion directe** : {PC_A.ip}/24 et {PC_B.ip}/24, même masque, passerelle et DNS vides.
- **Sans serveur DHCP** : adresse 169.254.x.x → fixer les adresses.
- **Ping** : réponse ; délai dépassé (pare-feu ou masque) ; hôte injoignable (personne n'a
  l'adresse, compté « reçu ») ; défaillance générale (pas de lien ou pas de route).
- **arp -a** : MAC présente = le poste distant existe et a répondu.
- **Pare-feu** : réseau non identifié = Public ; passer en Privé, ouvrir la règle d'écho ; ne
  pas couper.
- **Partage** : compte avec mot de passe ; partage ET dossier ; la plus restrictive gagne ;
  {SHARE_UNC}.
- **Mini-réseau** : switch, un câble droit par appareil, adresses suivantes du plan.
- **Box** : passerelle + DNS + DHCP ({BOX_IP}, étendue {POOL[0]}–{POOL[1]}) ; fixes hors étendue.
- **Erreurs** : liaison, DHCP, doublon « (Dupliqué) », masque.
- **Recette** : lien → adresse → doublon → réseau → ARP → ping → partage → Internet → PV.

## Glossaire des termes employés

- **Auto MDI-X** : fonction d'une carte ou d'un port qui inverse seul émission et réception.
- **Câble croisé** : T568A à un bout, T568B à l'autre ; relie deux ports de même type.
- **Câble droit** : même norme aux deux bouts ; relie une carte à un switch.
- **DHCP** : service qui donne automatiquement adresse, masque, passerelle et DNS.
- **Étendue DHCP** : plage d'adresses que le serveur DHCP peut distribuer.
- **Masque** : indique quelle partie de l'adresse désigne le réseau.
- **Passerelle** : adresse du routeur qui fait sortir les paquets du réseau.
- **Plan d'adressage** : tableau des adresses prévues pour chaque appareil.
- **Procès-verbal (PV) de recette** : document signé par lequel le client accepte l'installation.
- **Table ARP** : correspondances adresse IP → adresse MAC apprises par un poste.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Connexion de deux machines en direct » (AP-28) et
  « Création d'un mini réseau entre plusieurs machines » (AP-38). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **IEEE 802.3** : 10BASE-T, 100BASE-TX (paires 1-2 et 3-6), 1000BASE-T (quatre paires), MDI,
  MDI-X et Auto MDI-X ; **TIA-568** : brochages T568A et T568B.
- **RFC 1918** (adresses privées), **RFC 3927** (169.254.0.0/16), **RFC 2131** (DHCP),
  **RFC 826** (ARP), **RFC 792** (ICMP, écho du ping), **RFC 5737** (adresses de documentation,
  utilisées pour les exemples d'Internet).
- **Documentation Microsoft** : profils réseau et pare-feu Windows Defender, partage de fichiers
  (SMB, port 445), `ipconfig`, `ping`, `arp`, `netsh`, `net share`, `net use`.

Les valeurs et menus sont ceux de {WRITTEN_AT} ; ils évoluent selon les versions : **la
documentation de l'éditeur et du fabricant fait foi**. Les schémas, plans, relevés et procédures
du cours sont **produits par programme** depuis des données **vérifiées par des tests
automatiques** (résultat d'un ping selon la configuration, erreurs d'un plan, câble selon les
ports) ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite la connexion directe et le mini-réseau. Sont des **compléments**, signalés comme
tels, utiles pour traiter un dossier écrit :

- les **conventions du cours** : réseau 192.168.10.0/24, box en .254, plages .1–.19, .20–.49,
  .100–.199 ;
- la lecture fine des messages du ping et de la table ARP ; le réglage du profil réseau ;
- le tableau de recette et le procès-verbal.

## Supports fictifs

Les postes, adresses MAC, entreprises et relevés de commandes de ce cours sont **fictifs** et
reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune n'est une question
officielle ou déjà posée par le Jury.
"""


def pr21_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR21 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR21 — 1. Carte réseau, câble droit ou croisé et Auto MDI-X", _hardware()),
        ("PR21 — 2. Voyants de lien et vérification physique", _leds()),
        ("PR21 — 3. Adresses statiques de deux PC, masque et absence de passerelle", _addressing()),
        ("PR21 — 4. Tester : ping, table ARP et pare-feu", _tests()),
        ("PR21 — 5. Partage de fichiers et permissions", _sharing()),
        ("PR21 — 6. Étendre à 3 à 6 PC avec un switch", _switch()),
        ("PR21 — 7. DHCP ou statique, routeur, passerelle, DNS et plan d'adressage", _dhcp_router()),
        ("PR21 — 8. IP dupliquée, masque, DHCP et liaison : reconnaître l'erreur", _errors()),
        ("PR21 — 9. Mise en service et recette", _acceptance()),
        ("PR21 — Exemples : cinq situations résolues", _examples()),
        ("PR21 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR21 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR21 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR21 — Fiche mémo et glossaire", _memo()),
        ("PR21 — Sources et compléments pédagogiques", _sources()),
    ]


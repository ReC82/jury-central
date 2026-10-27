"""Cours PR25 « Wi-Fi : configuration, couverture, sécurité et diagnostic » — parcours AMPCR
pratique écrite (ticket #224).

Matière : intégralement celle du ticket #224 (architecture point d'accès / client / routeur /
répéteur / mesh, SSID et BSSID ; bandes 2,4 / 5 / 6 GHz selon les équipements et la
réglementation, canaux, largeur de canal, interférences, portée, obstacles, roaming, débit réel ;
association, authentification, DHCP et DNS ; normes IEEE 802.11 à niveau utile ; WEP et
WPA-TKIP obsolètes, WPA2 AES-CCMP, WPA3 SAE, Personnel / Entreprise 802.1X / RADIUS, WPS et ses
risques, mot de passe fort, réseau invités et isolation ; configuration d'un point d'accès
(SSID, bande et canal, sécurité, clé, DHCP, micrologiciel, placement) ; diagnostics « réseau
invisible », « connecté sans Internet », mauvaise clé, interférence, mauvaise adresse IP,
répéteur mal placé ; cinq cas résolus), découpée en blocs titrés (le titre pilote le type de
carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert » ni
« mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr25_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr25_bank`. Le réseau de l'atelier vient de PR24 (dépannage réseau),
les équipements de PR19, l'adressage IPv4 de PR20, l'isolation des partages de PR23 (publiés,
liens).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr24_figures import WifiStatus, netsh_wlan_lines, win_ping_lines
from app.v1.ampcr_pratique_pr25_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr25_figures import (
    AP1_NAME,
    AP2_NAME,
    AP_IP,
    ARCH_FIGURE,
    ASSOC_FIGURE,
    BAND_5,
    BAND_24,
    BAND_FACTS,
    CHANNELS_FIGURE,
    CONFIG_PROC_FIGURE,
    COVERAGE_FIGURE,
    COVERAGE_PROC_FIGURE,
    DFS_FROM,
    DIAG_FIGURE,
    EIRP_DBM,
    ENTERPRISE,
    EU_5_CHANNELS,
    EU_6_CHANNELS,
    EXTENSIONS,
    GUEST_GATEWAY,
    GUEST_NETWORK,
    GUEST_SSID,
    GUEST_VLAN,
    LAN_NETWORK,
    MENU_FIGURE,
    NEIGHBORS_BEST,
    NON_OVERLAP_24,
    OBSTACLE_LABELS,
    OBSTACLES,
    PROCEDURES,
    REPEATER_BAD,
    REPEATER_FIGURE,
    REPEATER_GOOD,
    ROUTER_IP,
    SCAN_FIGURE,
    SECURITY_FIGURE,
    SECURITY_MODES,
    SERVER_IP,
    SIX_GHZ_RANGE,
    SSID,
    STANDARDS,
    STATIC_FIGURES,
    STRONG_NEIGHBOR_DBM,
    SURVEY,
    TARGET_DBM,
    TROUBLE_PROC_FIGURE,
    VISIBLE_DBM,
    WEB_IP,
    WIDTHS,
    WIDTHS_FIGURE,
    WIFI_CHECKS,
    WPA2_PSK,
    WPA2_WPA3,
    WPA3_SAE,
    WRITTEN_AT,
    ApConfig,
    Neighbor,
    WifiState,
    audit_config,
    best_channel_24,
    blocks_5,
    blocks_6,
    center_5,
    center_24,
    fr,
    interference_24,
    link_rate,
    passphrase_issues,
    quality_pct,
    signal_verdict,
    useful_mbps,
    wifi_checks,
    wifi_diagnosis,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR25_TITLE = "Wi-Fi : configuration, couverture, sécurité et diagnostic"
PR25_SLUG = "ampcr-pratique-pr25"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr25")
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


def _short(diagnosis: str) -> str:
    return diagnosis.split(" :")[0].lower()


def _rate(mbps: int) -> str:
    return f"{mbps / 1000:.1f} Gb/s".replace(".", ",") if mbps >= 1000 else f"{mbps} Mb/s"


def _standards_table() -> str:
    rows = "\n".join(f"| {std} | {name} | {bands} | {_rate(rate)} |" for std, name, bands, rate in STANDARDS)
    return f"| Norme IEEE | Nom commercial | Bandes | Débit maximal théorique |\n|---|---|---|---|\n{rows}"


def _bands_table() -> str:
    rows = "\n".join(f"| {b} | {ch} | {reach} | {crowd} | {who} |" for b, ch, reach, crowd, who in BAND_FACTS)
    return f"| Bande | Canaux (Europe) | Portée | Encombrement, débit | Appareils |\n|---|---|---|---|---|\n{rows}"


def _widths_table() -> str:
    rows = "\n".join(f"| {w} MHz | {len(blocks_5(w))} | {len(blocks_6(w))} |" for w in WIDTHS)
    return f"| Largeur | Canaux en 5 GHz (Europe) | Canaux en 6 GHz (Europe) |\n|---|---|---|\n{rows}"


def _obstacles_table() -> str:
    rows = "\n".join(f"| {OBSTACLE_LABELS[k]} | {a} dB | {b} dB |" for k, (a, b) in OBSTACLES.items())
    return f"| Obstacle | 2,4 GHz | 5 GHz |\n|---|---|---|\n{rows}"


def _survey_table() -> str:
    rows = "\n".join(
        f"| {p.key} {p.place} | {fr(p.distance_m)} m, {' + '.join(p.obstacles) or 'aucun'} | "
        f"{p.dbm(BAND_24)} dBm ({signal_verdict(p.dbm(BAND_24))}) | {p.dbm(BAND_5)} dBm ({signal_verdict(p.dbm(BAND_5))}) |"
        for p in SURVEY
    )
    return f"| Point | Distance, obstacles | 2,4 GHz | 5 GHz |\n|---|---|---|---|\n{rows}"


def _extensions_table() -> str:
    rows = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in EXTENSIONS)
    return f"| Solution | Liaison vers le réseau | Débit | Quand |\n|---|---|---|---|\n{rows}"


def _security_table() -> str:
    rows = "\n".join(f"| {m.name} | {m.cipher} | {m.verdict} | {m.why} |" for m in SECURITY_MODES)
    return f"| Mode | Chiffrement | Verdict | Pourquoi |\n|---|---|---|---|\n{rows}"


def _checks_table() -> str:
    rows = "\n".join(f"| {i} | {what} | {diag} |" for i, (_k, what, diag) in enumerate(WIFI_CHECKS, start=1))
    return f"| Ordre | Contrôle | Si non : piste |\n|---|---|---|\n{rows}"


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# =============================================================================================
# Cinq cas résolus (données calculées par le module de figures)
# =============================================================================================

C1_NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Pharmacie-Wifi", 6, -61),
    Neighbor("Proximus-55AA", 9, -73),
    Neighbor("Telenet-0C1D", 1, -86),
)
C1_CHANNEL = best_channel_24(C1_NEIGHBORS)
C1_CONFIG = ApConfig("KINE-PRO", WPA2_WPA3, "Genou-Epaule-Cheville-Dos-26", channel_24=C1_CHANNEL, guest_isolated=True,
                     names=("Kine", "Moreau"))
C1_AUDIT = audit_config(C1_CONFIG)
C1_KEY_OK = passphrase_issues(C1_CONFIG.passphrase, names=("KINE-PRO", "Kine", "Moreau")) == ()

C2_STOCK = next(p for p in SURVEY if p.key == "P4")
C2_UP = next(p for p in SURVEY if p.key == "P5")

C3_DIAG = wifi_diagnosis(wifi_checks(WifiState(wan_ok=False)))
C3_GATEWAY = win_ping_lines(ROUTER_IP, (1, 1, 1, 1))
C3_INTERNET = win_ping_lines(WEB_IP, (None, None, None, None))

C4_NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Resto-Wifi", 1, -60),
    Neighbor("Voo-1234", 11, -62),
    Neighbor("Ecole-Invites", 8, -77),
)
C4_SCORES = {ch: interference_24(ch, C4_NEIGHBORS) for ch in NON_OVERLAP_24}
C4_CHANNEL = best_channel_24(C4_NEIGHBORS)

C5_DIAG = wifi_diagnosis(wifi_checks(WifiState(security_supported=False)))
C5_STATUS = netsh_wlan_lines(WifiStatus("déconnecté", SSID, "", "", "", "", "", 0, 0, 0))

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Mettre en service le Wi-Fi d'un cabinet de kinésithérapie",
        (
            "Un cabinet de trois kinésithérapeutes reçoit un point d'accès double bande. Il faut un réseau pour les "
            "praticiens (dossiers patients en ligne) et un Wi-Fi pour les patients en salle d'attente. Le relevé des "
            "voisins donne : " + ", ".join(f"{n.ssid} canal {n.channel} à {n.dbm} dBm" for n in C1_NEIGHBORS) + "."
        ),
        (
            (
                "**Placement et administration** : point d'accès au plafond du couloir central, câblé au switch ; "
                "par câble, mot de passe d'administration changé, micrologiciel mis à jour."
            ),
            (
                f"**Radio** : SSID « {C1_CONFIG.ssid} », 2,4 et 5 GHz. Canal 2,4 GHz : le 6 est occupé par la pharmacie "
                f"(−61), le 1 n'a que Telenet à −86 (sous le seuil de {STRONG_NEIGHBOR_DBM} dBm), le 11 est gêné par "
                f"Proximus du canal 9 (−73) → **canal {C1_CHANNEL}** en 20 MHz ; 5 GHz : canal 36 en 80 MHz."
            ),
            (
                f"**Sécurité** : {C1_CONFIG.security}, clé de type « Genou-Epaule-Cheville-Dos-26 » "
                f"({'conforme' if C1_KEY_OK else 'à revoir'} à la règle du cours), WPS désactivé ; réseau invités isolé "
                "avec sa propre clé, affichée en salle d'attente."
            ),
        ),
        (
            f"Point d'accès en service : SSID {C1_CONFIG.ssid}, {C1_CONFIG.security}, canal {C1_CHANNEL} (2,4 GHz) et 36 "
            f"(5 GHz), invités isolés ; audit de la configuration : {len(C1_AUDIT) or 'aucun'} défaut ; signal mesuré dans "
            "les quatre salles, fiche remise."
        ),
    ),
    (
        "Cas 2 — Le stock et l'étage sont mal couverts",
        (
            f"À l'atelier Durant, seul {AP1_NAME} dessert le bâtiment. Le magasinier se plaint au fond du stock et les "
            "employés de l'étage perdent la visioconférence en 5 GHz. Tu estimes la couverture aux cinq points de "
            "mesure, puis tu vérifies sur place."
        ),
        (
            (
                f"**Mesures** : stock ({C2_STOCK.key}) {C2_STOCK.dbm(BAND_24)} dBm en 2,4 GHz "
                f"({signal_verdict(C2_STOCK.dbm(BAND_24))}) ; étage ({C2_UP.key}) {C2_UP.dbm(BAND_5)} dBm en 5 GHz "
                f"({signal_verdict(C2_UP.dbm(BAND_5))}) ; objectif {TARGET_DBM} dBm."
            ),
            (
                "**Causes** : mur en béton et rayonnages métalliques pour le stock ; dalle d'étage, qui coûte "
                "25 dB en 5 GHz, pour l'étage."
            ),
            (
                f"**Solution** : {AP2_NAME} câblé à l'étage (canaux 6 et 44) et un point d'accès câblé dans le stock "
                "(canaux 11 et 52), même SSID, même sécurité ; aucun répéteur derrière le béton."
            ),
        ),
        (
            "Deux points d'accès câblés ajoutés, canaux distincts ; mesure après travaux : stock et étage au-dessus de "
            f"{TARGET_DBM} dBm dans les deux bandes ; passage de l'un à l'autre testé en marchant."
        ),
    ),
    (
        "Cas 3 — « Connecté, pas d'Internet » après un orage",
        (
            "Le lendemain d'un orage, tous les postes de l'atelier, en Wi-Fi comme en câble, affichent « Pas "
            "d'Internet ». Le Wi-Fi est visible et les postes ont leur adresse habituelle en 192.168.20.x."
        ),
        (
            (
                f"**Relevés** : ping de la passerelle {ROUTER_IP} : réponses ; ping de {WEB_IP} : délai dépassé ; "
                "le voyant « Internet » de la box est rouge."
            ),
            (
                f"**Piste** : {_short(C3_DIAG)} — tous les postes, câble et Wi-Fi, sont touchés : ni la radio, ni la clé, "
                "ni le DHCP ; la panne est au-delà de la passerelle (liaison de la box)."
            ),
            (
                "**Action** : redémarrage de la box avec l'accord du gérant ; voyant toujours rouge → appel au "
                "fournisseur d'accès avec le numéro de ligne ; on ne touche pas aux réglages Wi-Fi."
            ),
        ),
        (
            "Panne de la liaison Internet de la box (orage) signalée au fournisseur ; Wi-Fi et réseau local hors de "
            f"cause ; rétablissement vérifié par un ping de {WEB_IP} et l'ouverture d'un site."
        ),
    ),
    (
        "Cas 4 — Lenteurs à l'heure du midi : le canal",
        (
            "Une agence de voyages réglée en 2,4 GHz sur le canal 4 subit des lenteurs à midi, quand le restaurant et "
            "l'école voisins sont pleins. Signal correct (−58 dBm), Internet correct. Relevé : "
            + ", ".join(f"{n.ssid} canal {n.channel} à {n.dbm} dBm" for n in C4_NEIGHBORS) + "."
        ),
        (
            (
                "**Constat** : le canal 4 n'est pas un canal sans chevauchement ; il est gêné par Resto-Wifi (canal 1) "
                "et par Ecole-Invites (canal 8)."
            ),
            (
                "**Calcul** : "
                + " ; ".join(f"canal {ch} : {n} voisin(s) fort(s)" + (f", le plus fort à {m} dBm" if n else "")
                             for ch, (n, m) in C4_SCORES.items())
                + f" → **canal {C4_CHANNEL}**, en 20 MHz."
            ),
            "**Compléments** : 5 GHz activé pour les portables, canal 36 en 40 MHz ; mesure du débit à midi le lendemain.",
        ),
        f"Canal 2,4 GHz passé de 4 à {C4_CHANNEL} (20 MHz), 5 GHz activé ; lenteurs disparues au contrôle du lendemain midi.",
    ),
    (
        "Cas 5 — WPA3 seul, un portable reste dehors",
        (
            f"Pour renforcer la sécurité, un collègue a réglé « {SSID} » en {WPA3_SAE} seul. Depuis, un portable de "
            "2016 affiche « Impossible de se connecter à ce réseau » ; les autres appareils fonctionnent."
        ),
        (
            (
                "**Relevé** : le réseau est visible ; netsh wlan show drivers indique que la carte ne prend pas en charge "
                "WPA3 ; la clé saisie est la bonne (vérifiée sur un smartphone)."
            ),
            f"**Piste** : {_short(C5_DIAG)} — le mode de sécurité n'est pas pris en charge par la carte, la clé n'est pas en cause.",
            (
                "**Choix** : mise à jour du pilote (parfois suffisante) ; sinon mode de transition "
                f"{WPA2_WPA3} (WPA3 pour les appareils récents, WPA2 AES pour l'ancien) ou clé USB Wi-Fi récente ; "
                "jamais un retour à WEP ou TKIP."
            ),
        ),
        f"Mode {WPA2_WPA3} appliqué en attendant le remplacement du portable ; tous les postes connectés ; remplacement de la carte proposé au client.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant un plan, un relevé Wi-Fi ou une fiche de configuration, on attend de toi un
**choix de configuration justifié** et un **diagnostic prouvé**, pas une liste de sigles. Tu
dois savoir :

1. décrire l'**architecture** : point d'accès, client, routeur, répéteur, mesh, **SSID** et
   **BSSID** ;
2. situer les **normes IEEE 802.11** utiles et choisir une **bande** (2,4, 5 ou 6 GHz), un
   **canal** et une **largeur de canal** ;
3. estimer la **portée**, l'effet des **obstacles** et des **interférences**, le **débit réel**,
   et organiser le **roaming** entre points d'accès ;
4. expliquer la connexion d'un client : **association**, **authentification**, **DHCP**,
   **DNS** ;
5. choisir la **sécurité** : WEP et WPA-TKIP **obsolètes**, **WPA2 AES-CCMP**, **WPA3 SAE**,
   **Personnel** ou **Entreprise** (802.1X/RADIUS), **WPS** et ses risques, **mot de passe
   fort**, **réseau invités** et **isolation** ;
6. **configurer un point d'accès** : SSID, bande et canal, sécurité, clé, DHCP, micrologiciel,
   placement ;
7. **diagnostiquer** : réseau invisible, mauvaise clé, mauvaise adresse IP, connecté sans
   Internet, interférence, répéteur mal placé.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigence travaillée dans ce cours

{_req("AP-33")}

C'est une exigence **officielle** (consignes, p. 6). Le réseau de référence est celui de
l'atelier de [PR24](/uaa/ampcr-pratique-pr24) (dépannage réseau et Internet) ; les équipements
(routeur, switch, point d'accès) sont vus en [PR19](/uaa/ampcr-pratique-pr19), l'adressage IPv4
en [PR20](/uaa/ampcr-pratique-pr20) et la protection des partages en
[PR23](/uaa/ampcr-pratique-pr23).

## Lien avec la théorie

La théorie AMPCR présente le Wi-Fi : [MC25 Wi-Fi : normes, bandes, canaux et
couverture](/uaa/ampcr-mc25) et [MC26 Sécurité Wi-Fi : WPA2, WPA3, PSK,
Enterprise](/uaa/ampcr-mc26). Ce cours-ci est **pratique** : schémas, relevés `netsh wlan`,
fiches de configuration et calculs de couverture à analyser et à rédiger, comme dans un dossier
d'examen ; il ajoute le **répéteur**, cité par l'exigence officielle et absent de la théorie.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont quatre **schémas à
compléter**, des **choix de configuration** et des **relevés** à analyser), puis passe le
**mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, entreprises, réseaux et relevés de ce cours sont des **supports
> fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). Les relevés reprennent le
> format réel de Windows (en français), en version simplifiée. Les signaux et débits calculés
> sont des **estimations simplifiées** : sur le terrain, **la mesure fait foi**, et la
> documentation du fabricant fait foi pour les menus. Aucun exercice n'est une question
> officielle ni une question déjà posée par le Jury.
"""


def _architecture() -> str:
    return f"""**Objectifs** : nommer chaque élément d'un réseau sans fil et son rôle.

## 1.1 Qui fait quoi ?

{_fig(ARCH_FIGURE)}

- Le **client** (portable, smartphone, imprimante) a une **carte Wi-Fi** ; il s'**associe** à
  un point d'accès.
- Le **point d'accès** (AP, *access point*) relie les clients radio au réseau câblé. Il ne
  donne pas forcément les adresses : dans l'atelier, c'est **SRV-01** ({SERVER_IP}) qui fait
  **DHCP** et DNS.
- Le **routeur** (la **box**, {ROUTER_IP}) relie le réseau local à Internet : **passerelle**,
  traduction d'adresses (NAT), pare-feu. Une box grand public réunit souvent routeur, switch,
  point d'accès et serveur DHCP dans un seul boîtier.
- Le **répéteur** reçoit le signal d'un point d'accès et le **retransmet par radio**, sans
  câble ; le **mesh** (système maillé) est un ensemble de bornes qui se relaient entre elles et
  se gèrent comme un seul réseau.

## 1.2 SSID et BSSID

Le **SSID** est le **nom du réseau** affiché ({SSID}). Un même SSID peut être émis par plusieurs
radios : chaque radio a son **BSSID**, l'adresse MAC de cette radio. Dans l'atelier,
{AP1_NAME} et {AP2_NAME} émettent tous deux {SSID}, en 2,4 et en 5 GHz : quatre BSSID pour un
seul SSID. `netsh wlan show interfaces` donne le BSSID, donc **le point d'accès auquel le poste
est associé**.

## 1.3 Étendre la couverture

{_extensions_table()}

**Procédure professionnelle (à rédiger)** : faire le plan (box, switch, points d'accès,
répéteur, clients), écrire pour chaque élément son rôle, sa liaison (câble ou radio) et son
adresse ; noter quel appareil fait le DHCP.

**Erreur fréquente** : croire que « le Wi-Fi » donne l'adresse IP ; brancher un second
appareil qui distribue aussi des adresses (deux serveurs DHCP).

**À l'écrit** : « {AP2_NAME} : point d'accès câblé au switch, SSID {SSID}, BSSID propre ; DHCP
assuré par SRV-01 ».

**Repère rapide** : **SSID = nom ; BSSID = une radio ; point d'accès ≠ routeur ; câble d'abord,
mesh ensuite, répéteur en dernier**. Exercices liés : {_ex("E07", "E19")}.
"""


def _bands() -> str:
    return f"""**Objectifs** : choisir la bande selon les appareils, la distance et l'encombrement.

## 2.1 Les normes utiles

{_standards_table()}

Les débits sont des **maximums théoriques** de la norme (toutes antennes, canal le plus large) :
un portable courant n'en obtient qu'une petite partie (chapitre 4). Les noms commerciaux
(Wi-Fi 4 à 7) sont ceux de la Wi-Fi Alliance. Un point d'accès récent reste **compatible** avec
les anciennes normes de sa bande, mais un vieil appareil **n'utilise que ce qu'il connaît** :
une carte 802.11g ne voit **jamais** un réseau émis en 5 GHz.

## 2.2 Trois bandes

{_bands_table()}

- **2,4 GHz** : porte plus loin, traverse mieux les murs, mais n'a que trois canaux sans
  chevauchement et beaucoup de voisins (réseaux voisins, Bluetooth, four à micro-ondes).
- **5 GHz** : plus de canaux et plus de débit, portée plus courte ; en Europe, canaux 36 à 64
  et 100 à 140 ; à partir du canal {DFS_FROM}, le point d'accès doit **détecter les radars**
  (DFS) et changer de canal s'il en entend un.
- **6 GHz** (Wi-Fi 6E et 7) : {SIX_GHZ_RANGE[0]} à {SIX_GHZ_RANGE[1]} MHz en Europe,
  {len(EU_6_CHANNELS)} canaux de 20 MHz, très peu encombrés ; portée la plus courte ; **WPA3
  obligatoire** ; seuls les appareils Wi-Fi 6E ou 7 le voient.

La liste exacte des canaux dépend du **pays réglé** dans le point d'accès (Belgique) : la
réglementation fait foi.

**Procédure professionnelle (à rédiger)** : relever les normes des appareils (fiche technique,
`netsh wlan show drivers`) ; activer les bandes qu'ils utilisent ; garder le 2,4 GHz pour les
objets connectés et les anciens appareils ; donner le même SSID aux bandes, sauf besoin précis.

**Erreur fréquente** : couper le 2,4 GHz « parce que le 5 GHz est plus rapide » et rendre le
réseau invisible pour une imprimante ou un vieux portable.

**À l'écrit** : « la carte ne gère que 802.11b/g/n en 2,4 GHz : le SSID émis en 5 GHz seul lui
est invisible ».

**Repère rapide** : **2,4 = portée ; 5 = débit et canaux ; 6 = Wi-Fi 6E/7, WPA3, courte
portée**. Exercices liés : {_ex("E06", "E16")}.
"""


def _channels() -> str:
    return f"""**Objectifs** : choisir un canal et une largeur qui limitent les interférences.

## 3.1 Le chevauchement en 2,4 GHz

En 2,4 GHz, le canal *n* est centré sur 2407 + 5 × *n* MHz (canal 1 = {center_24(1)} MHz, canal
13 = {center_24(13)} MHz) : **5 MHz** séparent deux numéros, mais un canal occupe environ
**22 MHz**. Deux canaux distants de moins de 5 numéros **se chevauchent** et se gênent. Les seuls
canaux sans chevauchement sont **{", ".join(map(str, NON_OVERLAP_24))}**.

{_fig(CHANNELS_FIGURE)}

{_fig(SCAN_FIGURE)}

**Choisir le canal** : on relève les voisins (`netsh wlan show networks mode=bssid`) ; Windows
affiche le signal en % : **0 % ≈ −100 dBm, 100 % ≈ −50 dBm**, entre les deux on interpole (52 %
≈ −74 dBm). Convention du cours : un voisin **gêne** s'il est reçu à {STRONG_NEIGHBOR_DBM} dBm ou
plus sur un canal qui chevauche. Parmi 1, 6 et 11, on garde celui qui a le moins de voisins
gênants, puis le voisin le plus faible : ici, le **canal {NEIGHBORS_BEST}**.

## 3.2 Largeur de canal

Un canal plus **large** (40, 80, 160 MHz) donne plus de **débit** mais laisse **moins de canaux
libres** et capte plus d'interférences.

{_fig(WIDTHS_FIGURE)}

{_widths_table()}

- **2,4 GHz : toujours 20 MHz** ; 40 MHz y occuperait presque toute la bande.
- **5 GHz : 40 ou 80 MHz** selon l'encombrement ; 160 MHz seulement si la zone est libre.
- Fréquence centrale en 5 GHz : 5000 + 5 × *n* MHz (canal 36 = {center_5(36)} MHz) ;
  {len(EU_5_CHANNELS)} canaux de 20 MHz autorisés en Europe.

## 3.3 Les autres interférences

Four à **micro-ondes** (vers 2,45 GHz quand il fonctionne), appareils **Bluetooth**, caméras
sans fil, babyphones : ils gênent le 2,4 GHz. Le 5 GHz y échappe. Deux points d'accès d'un même
bâtiment doivent être sur des **canaux différents**.

**Procédure professionnelle (à rédiger)** : relever les voisins à l'endroit d'utilisation ;
convertir les % en dBm ; évaluer 1, 6, 11 ; régler 20 MHz en 2,4 GHz, 40 ou 80 MHz en 5 GHz ;
contrôler le débit aux heures chargées.

**Erreur fréquente** : choisir le canal 3 ou 4 « parce qu'il est libre » : il chevauche le 1
et le 6 ; oublier qu'un voisin sur le canal 7 gêne aussi le 11.

**À l'écrit** : « canal 1 : 2 voisins forts ; 6 : 1 voisin à −71 ; 11 : 1 voisin à −79 → canal 11 en
20 MHz ».

**Repère rapide** : **1, 6, 11 · 20 MHz en 2,4 GHz · moins de 5 numéros = chevauchement · 5 GHz
pour le débit**. Exercices liés : {_ex("E08", "E11")}.
"""


def _coverage() -> str:
    good = REPEATER_GOOD
    return f"""**Objectifs** : estimer la couverture, l'effet des obstacles et le débit réel.

## 4.1 Le signal en dBm

Le signal reçu s'exprime en **dBm** (négatif) : plus il est proche de 0, plus il est fort.
**3 dB de moins = moitié de la puissance.** Repères du cours :

| Signal reçu | Appréciation | Usage |
|---|---|---|
| −60 dBm ou mieux | excellent | tout usage |
| −60 à {TARGET_DBM} dBm | bon | visioconférence, téléphonie |
| {TARGET_DBM} à −75 dBm | faible | navigation lente, coupures |
| sous −75 dBm | insuffisant | inutilisable ; sous {VISIBLE_DBM} dBm, le réseau n'apparaît plus |

## 4.2 Distance et obstacles

Estimation simplifiée du cours : **signal reçu = puissance rayonnée ({EIRP_DBM} dBm) −
affaiblissement en espace libre − obstacles**, avec l'affaiblissement en espace libre
**20 log₁₀(distance en m) + 20 log₁₀(fréquence en MHz) − 27,55**. À distance égale, le 5 GHz
perd environ **6,5 dB de plus** que le 2,4 GHz, et davantage dans les murs.

{_obstacles_table()}

{_fig(COVERAGE_FIGURE)}

{_survey_table()}

Ces valeurs sont des **ordres de grandeur** : une **mesure sur place** (application d'analyse
Wi-Fi, `netsh wlan show interfaces`) fait foi.

## 4.3 Placement et débit réel

- Point d'accès **central**, **en hauteur**, hors armoire métallique, loin du four à
  micro-ondes, de l'aquarium et des miroirs.
- Le **débit réel** est bien inférieur au maximum de la norme : la liaison négociée baisse avec
  le signal (convention du cours, 802.11n 2×2 en 20 MHz : {link_rate(-55)} Mb/s à −55 dBm,
  {link_rate(-70)} Mb/s à −70 dBm, {link_rate(-80)} Mb/s à −80 dBm), le débit **utile** en vaut
  environ la **moitié**, et il est **partagé** entre les clients actifs ({fr(useful_mbps(link_rate(-55), 4))} Mb/s chacun
  pour quatre portables à −55 dBm).

## 4.4 Répéteur et roaming

{_fig(REPEATER_FIGURE)}

Un répéteur à **une radio** reçoit puis réémet chaque paquet sur la même radio : le débit est
**divisé par deux**, et il ne peut pas dépasser ce que lui permet **son propre lien avec le point
d'accès**. Mal placé (près du client, {REPEATER_BAD.uplink_dbm} dBm reçus), il ne donne
qu'environ {fr(REPEATER_BAD.mbps)} Mb/s ; à mi-chemin ({good.uplink_dbm} dBm reçus), environ
{fr(good.mbps)} Mb/s.

Le **roaming** est le passage d'un point d'accès à l'autre en se déplaçant. C'est le **client**
qui décide de changer : il faut le **même SSID**, la **même sécurité** et la **même clé** sur
tous les points d'accès, des **canaux différents** et des zones qui se recouvrent un peu. Les
options 802.11k, v et r, si le matériel les propose, accélèrent ce passage.

{_fig(COVERAGE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : mesurer pièce par pièce ; expliquer chaque zone
faible (distance, matériau) ; déplacer avant d'acheter ; câbler un second point d'accès ; mesh
ou répéteur à mi-chemin en dernier ; mesurer de nouveau.

**Erreur fréquente** : poser le répéteur à côté du client ; ajouter un répéteur derrière un mur
en béton ; promettre le débit « Wi-Fi 6 » de la boîte.

**À l'écrit** : « stock : −77 dBm en 2,4 GHz, insuffisant (béton + métal) → point d'accès câblé
dans le stock, canal 11 ».

**Repère rapide** : **objectif {TARGET_DBM} dBm · 5 GHz = −6,5 dB en espace libre · dalle =
−15 à −25 dB · répéteur à mi-chemin, débit ÷ 2 · même SSID, autres canaux**. Exercices liés :
{_ex("E09", "E10", "E12", "E19")}.
"""


def _connection() -> str:
    return f"""**Objectifs** : décrire les étapes de la connexion pour situer une panne.

## 5.1 De la découverte à Internet

{_fig(ASSOC_FIGURE)}

1. **Découverte** : les points d'accès émettent des **balises** (*beacons*) plusieurs fois par
   seconde ; le client écoute ou envoie des sondes et dresse la liste SSID, BSSID, signal,
   sécurité.
2. **Association et authentification** : le client choisit un BSSID et s'y associe. En **WPA3**,
   l'échange **SAE** a lieu à ce moment.
3. **Clés** : client et point d'accès prouvent qu'ils connaissent la clé par l'**échange en
   4 temps** (*4-way handshake*) et en tirent les clés de chiffrement ; en **Entreprise**,
   le serveur **RADIUS** vérifie d'abord l'identifiant de la personne (**802.1X**).
4. **DHCP** : comme en filaire, découverte, offre, demande, accusé : adresse, masque, passerelle,
   DNS. Sans réponse : adresse **169.254.x.x** (APIPA, [PR20](/uaa/ampcr-pratique-pr20)).
5. **Passerelle et DNS** : le client joint la box, puis résout les noms.

## 5.2 Lire l'état de la carte

{_console(netsh_wlan_lines(WifiStatus("connecté", SSID, "9c:53:22:10:20:32", "802.11ac", "WPA2 - Personnel",
                                     "CCMP", BAND_5, 36, 433, quality_pct(-58))))}

Ce relevé dit : **associé** à {SSID}, **authentifié** en WPA2 avec chiffrement CCMP (AES), sur le
BSSID de {AP1_NAME} en 5 GHz, canal 36, signal {quality_pct(-58)} % ≈ −58 dBm, liaison à 433 Mb/s.
Il ne dit **rien** de l'adresse IP ni d'Internet : `ipconfig`, `ping` et `nslookup` le disent.

**Procédure professionnelle (à rédiger)** : pour chaque étape, citer la preuve : liste des
réseaux (1), état « connecté » (2-3), adresse du bon réseau (4), ping de la passerelle et
`nslookup` (5).

**Erreur fréquente** : conclure « le Wi-Fi marche » parce que l'icône est connectée, alors que
le DHCP ou le DNS échoue.

**À l'écrit** : « associé et authentifié (connecté, WPA2 CCMP), mais 169.254 : l'échec est au
DHCP ».

**Repère rapide** : **radio → association → clés → DHCP → DNS ; connecté ≠ Internet**.
Exercices liés : {_ex("E02", "E13")}.
"""


def _security() -> str:
    return f"""**Objectifs** : choisir et justifier la sécurité d'un réseau sans fil.

## 6.1 Les modes

{_fig(SECURITY_FIGURE)}

{_security_table()}

- **WEP** et **WPA avec TKIP** sont **obsolètes** : WEP se casse en quelques minutes, TKIP est
  retiré des appareils récents (et limite 802.11n à 54 Mb/s). On les **refuse**, même pour un
  vieil appareil : on le remplace ou on l'isole.
- **WPA2** chiffre avec **AES-CCMP** ; en mode **Personnel (PSK)**, tous partagent une clé :
  elle doit être **longue**, car un attaquant qui capture l'échange en 4 temps peut l'essayer
  hors ligne.
- **WPA3-Personnel** remplace la clé partagée par l'échange **SAE**, qui résiste aux attaques
  par dictionnaire hors ligne ; il est **obligatoire en 6 GHz**. Le mode de **transition**
  {WPA2_WPA3} accepte les deux, le temps de remplacer les anciens appareils.
- **{ENTERPRISE}** (802.1X) : chaque personne a **son identifiant**, vérifié par un serveur
  **RADIUS** relié à l'annuaire ; on le désactive au départ d'un employé, sans changer la clé de
  tous.

## 6.2 WPS, clé, invités

- **WPS** (bouton ou code PIN à 8 chiffres) : le code PIN se devine par essais ; on **désactive
  WPS**.
- **Mot de passe fort** : de 8 à 63 caractères en WPA2 ; règle du cours : **12 caractères au
  moins, de trois types**, ou une **phrase de 20 caractères et plus** ; rien de devinable (nom
  du réseau, de l'entreprise, mot de passe courant). On change aussi le **mot de passe
  d'administration** d'usine.
- **Réseau invités** : SSID séparé ({GUEST_SSID}), **réseau séparé** (VLAN {GUEST_VLAN},
  {GUEST_NETWORK}, passerelle {GUEST_GATEWAY}) sans accès au réseau interne {LAN_NETWORK},
  **isolation des clients** (les invités ne se voient pas entre eux), clé distincte.
- **Fausses protections** : masquer le SSID (le nom circule quand même et la connexion devient
  plus difficile) ou filtrer les adresses MAC (elles se recopient) **ne remplacent pas** le
  chiffrement.

**Procédure professionnelle (à rédiger)** : inventaire des appareils et de ce qu'ils gèrent ;
{WPA3_SAE} si tous le gèrent, sinon {WPA2_WPA3} ; Entreprise au-delà d'une vingtaine de
personnes ou avec beaucoup de passages ; WPS coupé ; clé notée sur la fiche, pas sur une
étiquette visible ; invités isolés.

**Erreur fréquente** : garder WEP « pour une imprimante » ; laisser WPS activé ; donner la clé du
personnel aux visiteurs.

**À l'écrit** : « {WPA2_PSK} AES avec clé de 26 caractères : acceptable ; passage en {WPA2_WPA3}
recommandé ; WPS désactivé ».

**Repère rapide** : **WEP/TKIP non · WPA2 AES minimum · WPA3 SAE ou Entreprise · WPS coupé ·
invités isolés · SSID masqué ≠ sécurité**. Exercices liés : {_ex("E04", "E18", "E20")}.
"""


def _configuration() -> str:
    return f"""**Objectifs** : configurer un point d'accès de bout en bout et le documenter.

## 7.1 Où régler quoi ?

{_fig(MENU_FIGURE)}

L'interface d'administration s'ouvre dans un navigateur à l'adresse du point d'accès (ici
`http://{AP_IP}`), de préférence **par câble** : une erreur de réglage radio ne coupe alors pas
la session.

## 7.2 La configuration pas à pas

{_fig(CONFIG_PROC_FIGURE)}

- **Placement** : central, en hauteur, câblé (chapitre 4).
- **Administration et micrologiciel** : mot de passe d'usine changé ; **micrologiciel** mis à
  jour (failles corrigées) ; **sauvegarde de la configuration** une fois terminée.
- **SSID** : nom neutre, sans nom de famille, adresse ou modèle du matériel.
- **Bande, canal, largeur** : chapitres 2 et 3.
- **Sécurité et clé** : chapitre 6.
- **DHCP** : **une seule source** d'adresses par réseau ; si la box ou un serveur la fournit
  déjà, le point d'accès (ou le répéteur) a son DHCP **désactivé** (mode point d'accès ou pont).
- **Invités** : SSID, VLAN, isolation.
- **Test et fiche** : connexion depuis chaque zone, signal et débit, fiche remise au client
  (SSID, sécurité, canaux, emplacement, version du micrologiciel, où est rangée la clé).

**Procédure professionnelle (à rédiger)** : rédiger la fiche de configuration ligne par ligne,
avec pour chaque paramètre la valeur choisie et sa justification.

**Erreur fréquente** : laisser le DHCP du répéteur ou du second routeur actif (deux sources
d'adresses) ; oublier la sauvegarde de configuration avant une mise à jour.

**À l'écrit** : « SSID {SSID} diffusé ; {WPA2_WPA3} ; canal {NEIGHBORS_BEST} en 20 MHz et 36 en
80 MHz ; WPS désactivé ; DHCP : SRV-01 seul ; invités en VLAN {GUEST_VLAN} isolé ;
micrologiciel à jour et sauvegardé ».

**Repère rapide** : **placer · administrer · SSID · canal · sécurité · un seul DHCP · invités
· tester · fiche**. Exercices liés : {_ex("E01", "E17")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : trouver, preuves à l'appui, pourquoi un poste ne se connecte pas ou
n'a pas Internet.

## 8.1 L'ordre des contrôles

{_fig(DIAG_FIGURE)}

{_checks_table()}

Le **premier contrôle en échec** désigne la piste : inutile de changer de canal si la clé est
refusée.

## 8.2 Les quatre pannes de connexion

- **Réseau invisible** : radio coupée (point d'accès éteint, programmation horaire, interrupteur
  ou mode avion du portable), **SSID masqué**, **bande non prise en charge** par la carte (5 GHz
  ou 6 GHz), **hors de portée**. Preuve : `netsh wlan show networks` (le poste voit-il d'autres
  réseaux ?) et `netsh wlan show drivers`.
- **Mauvaise clé** : « Impossible de se connecter à ce réseau » ; clé changée et **profil
  enregistré** avec l'ancienne (« Oublier » le réseau puis ressaisir), majuscules, ou mode de
  sécurité non géré par la carte (WPA3 seul).
- **Mauvaise adresse IP** : connecté mais **169.254.x.x** (pas de réponse DHCP : point d'accès
  qui n'est plus relié au switch, serveur DHCP arrêté, plage pleine), ou adresse d'**un autre
  réseau** (un répéteur ou une seconde box qui distribue ses propres adresses).
- **Connecté sans Internet** (« Pas d'Internet ») : on teste dans l'ordre la **passerelle**
  (`ping {ROUTER_IP}`), une **adresse Internet** (`ping {WEB_IP}`), un **nom** (`nslookup`) ;
  DNS mal saisi, liaison de la box coupée. Le dépannage complet est en
  [PR24](/uaa/ampcr-pratique-pr24).

{_fig(TROUBLE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : relever le message exact et l'étendue ; suivre
l'ordre ; noter chaque preuve (commande et résultat) ; appliquer la correction minimale ;
tester ; consigner.

**Erreur fréquente** : « réinitialiser la box » au premier symptôme, ce qui efface la
configuration de tous ; désactiver la sécurité pour « tester ».

**À l'écrit** : « réseau visible, connecté, mais 169.254 sur les postes associés à
{AP2_NAME} seulement → pas de bail DHCP : liaison de {AP2_NAME} au switch à vérifier ».

**Repère rapide** : **visible → clé → adresse → Internet ; un poste ou tous ? ; profil oublié
puis ressaisi ; un seul DHCP**. Exercices liés : {_ex("E03", "E05", "E13", "E14", "E15", "E16")}.
"""


def _trouble_radio() -> str:
    weak = 46
    return f"""**Objectifs** : diagnostiquer les pannes de qualité : signal faible, interférence,
répéteur mal placé.

## 9.1 Signal faible

Connecté, mais lent ou coupé par moments : on lit le **signal** (`netsh wlan show interfaces`) et
on le convertit : {weak} % ≈ {weak // 2 - 100} dBm, **{signal_verdict(weak // 2 - 100)}**. La
cause est la **distance** ou les **obstacles** (béton, dalle, métal). Correction durable : point
d'accès déplacé ou ajouté (câblé) ; pas un répéteur dans la zone déjà mal couverte.

## 9.2 Interférence

Signal correct, Internet correct, mais lenteurs à **certaines heures** ou **près d'un appareil** :
on relève les voisins et leurs canaux, on repère les **chevauchements** (canal 3 ou 4, voisin sur
7 qui gêne 11), on cherche un micro-ondes ou un appareil Bluetooth. Correction : canal 1, 6 ou 11
le moins gêné, 20 MHz, passage des appareils compatibles en 5 GHz.

## 9.3 Répéteur mal placé

Le client affiche un **excellent signal**, mais Internet est lent : il est associé au
**répéteur**, qui lui-même reçoit mal le point d'accès. On lit la page d'état du répéteur
(signal reçu du point d'accès) : sous {TARGET_DBM} dBm, on le rapproche du point d'accès, à
mi-chemin, ou on le remplace par un point d'accès câblé.

**Procédure professionnelle (à rédiger)** : mesurer le signal au poste ; s'il est bon, mesurer
le lien du répéteur ; s'il est bon aussi, relever les canaux voisins ; corriger, mesurer de
nouveau, noter avant/après.

**Erreur fréquente** : augmenter la puissance du point d'accès (le client, lui, n'émet pas plus
fort) ; passer en 40 MHz en 2,4 GHz « pour aller plus vite ».

**À l'écrit** : « signal du portable −45 dBm (près du répéteur) mais lien répéteur → point
d'accès −79 dBm : répéteur mal placé, débit utile ≈ 3 Mb/s ; à rapprocher à mi-chemin ».

**Repère rapide** : **% → dBm · lent partout = couverture · lent à heure fixe = interférence ·
beau signal mais lent = répéteur**. Exercices liés : {_ex("E05", "E10", "E11", "E12")}.
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
        "Cinq situations résolues pas à pas avec les règles du cours : mise en service complète, couverture, "
        "connexion sans Internet, interférences et sécurité incompatible. Chaque conclusion s'appuie sur une "
        "preuve.\n\n" + "\n".join(blocks)
        + "\n\nRelevés du cas 3 (captures fictives) :\n\n" + _console(C3_GATEWAY) + "\n\n" + _console(C3_INTERNET)
        + "\n\nRelevé du cas 5 (capture fictive) :\n\n" + _console(C5_STATUS) + "\n"
    )


def _pitfalls() -> str:
    return """> **Garder WEP ou WPA-TKIP** « pour un vieil appareil » : tout le réseau devient lisible.

> **Laisser WPS activé** ou le mot de passe d'administration d'usine.

> **Croire que masquer le SSID ou filtrer les adresses MAC protège** le réseau.

> **Choisir le canal 3 ou 4** en 2,4 GHz, ou régler **40 MHz** en 2,4 GHz.

> **Poser le répéteur à côté du client** au lieu de l'endroit où il reçoit bien le point d'accès.

> **Deux serveurs DHCP** sur le même réseau (répéteur ou seconde box en mode routeur).

> **Couper le 2,4 GHz** et rendre le réseau invisible pour les anciens appareils.

> **Conclure « le Wi-Fi marche »** parce que l'icône est connectée, sans tester adresse, passerelle et DNS.

> **Mettre les invités sur le réseau du personnel** ou leur donner la clé du personnel.

> **Réinitialiser la box** au premier problème, sans sauvegarde de la configuration.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (configurer un point d'accès, connexion
d'un client, dépanner un poste), classements (mode de sécurité, piste d'une panne, bande, clés),
**quatre schémas à compléter** (architecture, canaux 2,4 GHz, couverture, répéteur), **choix de
configuration** (canal, audit d'une fiche, roaming) et **relevés** à analyser (`netsh wlan`,
`ipconfig`, `ping`, `nslookup`). Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ;
toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR25_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR25_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (réglages et relevés fictifs). **Aucune correction n'est
visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **choix de configuration justifié**, le **diagnostic prouvé**
par les relevés, la **correction minimale** qui ne dégrade pas la sécurité — pas la récitation
de sigles. Une autre solution technique juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Architecture** : client → point d'accès → switch → box (routeur, passerelle) ; DHCP : un
  seul serveur ; SSID = nom, BSSID = une radio ; câble, puis mesh, puis répéteur.
- **Bandes** : 2,4 GHz portée, canaux 1, 6, 11, 20 MHz ; 5 GHz débit, 36 à 64 et 100 à 140
  (DFS dès {DFS_FROM}), 40 ou 80 MHz ; 6 GHz Wi-Fi 6E/7, WPA3 obligatoire.
- **Normes** : 802.11n = Wi-Fi 4, ac = Wi-Fi 5, ax = Wi-Fi 6/6E, be = Wi-Fi 7.
- **Signal** : 0 % ≈ −100 dBm, 100 % ≈ −50 dBm ; objectif {TARGET_DBM} dBm ; 5 GHz ≈ −6,5 dB de
  plus en espace libre ; dalle −15 à −25 dB.
- **Débit réel** : environ la moitié de la liaison, partagé ; répéteur à une radio ÷ 2.
- **Roaming** : même SSID, même sécurité, même clé, canaux différents.
- **Connexion** : découverte → association → clés (4 temps, SAE, 802.1X) → DHCP → DNS.
- **Sécurité** : WEP/TKIP non ; WPA2 AES minimum ; WPA3 SAE ou Entreprise RADIUS ; WPS coupé ;
  clé 12+ caractères variés ou phrase 20+ ; invités isolés.
- **Diagnostic** : visible → clé → adresse → Internet → signal → répéteur → canal.

## Glossaire des termes employés

- **BSSID** : adresse MAC d'une radio d'un point d'accès.
- **Canal** : portion de la bande utilisée par un réseau ; en 2,4 GHz, 1, 6 et 11 ne se chevauchent pas.
- **dBm** : unité de puissance du signal ; −50 dBm est fort, −80 dBm est faible.
- **DFS** : détection des radars, obligatoire sur une partie des canaux 5 GHz.
- **Mesh (maillé)** : ensemble de bornes qui se relaient et forment un seul réseau.
- **Point d'accès** : appareil qui relie les clients sans fil au réseau câblé.
- **RADIUS** : serveur qui vérifie l'identifiant de chaque personne en mode Entreprise (802.1X).
- **Répéteur** : appareil qui reçoit le signal d'un point d'accès et le retransmet par radio.
- **Roaming** : passage d'un point d'accès à l'autre sans coupure.
- **SAE** : échange de clés de WPA3-Personnel, résistant aux attaques par dictionnaire.
- **SSID** : nom du réseau sans fil.
- **WPS** : connexion simplifiée par bouton ou code PIN, à désactiver.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « WIFI : principe, sécurisation, cryptage, répéteur »
  (AP-33). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **IEEE 802.11** (b, a, g, n, ac, ax, be) et noms commerciaux de la **Wi-Fi Alliance** (Wi-Fi 4
  à 7) ; débits maximaux théoriques des normes.
- **Plans de fréquences européens** (ETSI, décisions de la Commission européenne) : 2,4 GHz,
  canaux 1 à 13 ; 5 GHz, canaux 36 à 64 et 100 à 140, DFS à partir du canal 52 ; 6 GHz,
  {SIX_GHZ_RANGE[0]} à {SIX_GHZ_RANGE[1]} MHz. Le pays réglé dans le point d'accès et la
  réglementation font foi.
- **Wi-Fi Alliance** : WPA2 (AES-CCMP), WPA3 (SAE, mode de transition, WPA3 obligatoire en
  6 GHz), WPA2/WPA3-Entreprise (802.1X) ; WEP et TKIP obsolètes ; faiblesse du code PIN WPS.
- **Documentation Microsoft** : `netsh wlan show interfaces`, `show networks mode=bssid`,
  `show drivers`, `show profiles`, `delete profile` ; qualité du signal de 0 à 100 % entre
  −100 et −50 dBm ; « Impossible de se connecter à ce réseau », « Pas d'Internet, sécurisé ».
- **Affaiblissement en espace libre** : formule classique de propagation radio
  (20 log₁₀ d + 20 log₁₀ f − 27,55, d en m, f en MHz).

Les valeurs et menus sont ceux de {WRITTEN_AT} ; ils évoluent selon les versions : **la
documentation du fabricant fait foi**. Les schémas, relevés, calculs et procédures du cours sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** (canaux et
chevauchements, canaux par largeur, signal estimé, débit derrière un répéteur, audit de
configuration, contrôle des clés, ordre du diagnostic) ; aucun schéma n'est tiré d'une image
générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite le principe du Wi-Fi, sa sécurisation, le chiffrement et le répéteur. Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- le mesh, le roaming et les options 802.11k/v/r ; la bande 6 GHz (Wi-Fi 6E et 7) ;
- les **conventions du cours** : {EIRP_DBM} dBm rayonnés, affaiblissements des obstacles en
  ordres de grandeur, seuils de signal (−60, {TARGET_DBM}, −75 dBm), seuil de gêne d'un voisin
  ({STRONG_NEIGHBOR_DBM} dBm), débit utile = moitié de la liaison, règle des clés ;
- l'ordre de diagnostic d'un poste Wi-Fi et la fiche de configuration remise au client.

## Supports fictifs

Les personnes, entreprises, réseaux et relevés de ce cours sont **fictifs** et reconstitués pour
l'entraînement ; ils ne décrivent aucun client réel. Aucune n'est une question officielle ou
déjà posée par le Jury.
"""


def pr25_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR25 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR25 — 1. Architecture : point d'accès, client, routeur, répéteur, mesh ; SSID et BSSID", _architecture()),
        ("PR25 — 2. Normes IEEE 802.11 et bandes 2,4 / 5 / 6 GHz", _bands()),
        ("PR25 — 3. Canaux, largeur de canal et interférences", _channels()),
        ("PR25 — 4. Portée, obstacles, débit réel, répéteur et roaming", _coverage()),
        ("PR25 — 5. Connexion d'un client : association, authentification, DHCP, DNS", _connection()),
        ("PR25 — 6. Sécurité : WEP, WPA2, WPA3, Personnel ou Entreprise, WPS, invités", _security()),
        ("PR25 — 7. Configurer un point d'accès : SSID, bande, canal, sécurité, DHCP, micrologiciel", _configuration()),
        ("PR25 — 8. Diagnostiquer : réseau invisible, mauvaise clé, mauvaise IP, sans Internet", _diagnosis()),
        ("PR25 — 9. Diagnostiquer la qualité : signal faible, interférence, répéteur mal placé", _trouble_radio()),
        ("PR25 — Exemples : cinq situations résolues", _examples()),
        ("PR25 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR25 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR25 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR25 — Fiche mémo et glossaire", _memo()),
        ("PR25 — Sources et compléments pédagogiques", _sources()),
    ]

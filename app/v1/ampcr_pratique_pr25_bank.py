"""PR25 « Wi-Fi : configuration, couverture, sécurité et diagnostic » — exercices corrigés et
mini-examen (ticket #224).

Même organisation que PR23 (`app.v1.ampcr_pratique_pr23_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (configurer un point d'accès, connexion d'un client,
  dépanner un poste), classements (mode de sécurité, piste d'une panne, bande, clés), **quatre
  schémas à compléter** (architecture, canaux 2,4 GHz, couverture, répéteur, servis en SVG),
  **choix de configuration** (canal, audit d'une fiche, roaming, réseau invités) et
  **diagnostics sur relevés** (netsh wlan, ipconfig, ping, nslookup) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, postes et réseaux sont **fictifs** ; les canaux conseillés, les
signaux estimés, les débits, les défauts de configuration et les pistes de diagnostic des
énoncés et des corrigés viennent des fonctions de `app.v1.ampcr_pratique_pr25_figures`
(mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr20_figures import Host
from app.v1.ampcr_pratique_pr24_figures import NAS_IP, WifiStatus, netsh_wlan_lines, win_ping_lines
from app.v1.ampcr_pratique_pr25_figures import (
    AP2_NAME,
    ARCH_BLANK_ANSWERS,
    ASSOCIATION_STEPS,
    BAND_5,
    BAND_6,
    BAND_24,
    BAND_FREQ_MHZ,
    BANDS,
    BSSID_AP1_5,
    BSSID_AP1_24,
    BSSID_AP2_24,
    CHANNELS_BLANK_ANSWERS,
    CONFIG_STEPS,
    COVERAGE_BLANK_ANSWERS,
    DNS_TIMEOUT_LINES,
    ENTERPRISE,
    GUEST_GATEWAY,
    GUEST_NETWORK,
    GUEST_SSID,
    GUEST_VLAN,
    INTERNET_PING_OK,
    LAPTOP_APIPA,
    NEIGHBORS_BEST,
    NON_OVERLAP_24,
    OPEN,
    REPEATER_BAD,
    REPEATER_BLANK_ANSWERS,
    REPEATER_GOOD,
    ROUTER_IP,
    SEC_BEST,
    SEC_MIN,
    SEC_REFUSE,
    SEC_VERDICTS,
    SECURITY_BY_NAME,
    SERVER_IP,
    SSID,
    STATIC_BY_KEY,
    SURVEY_BY_KEY,
    TARGET_DBM,
    TROUBLE_STEPS,
    W_CHANNEL,
    W_INTERNET,
    W_INVISIBLE,
    W_IP,
    W_KEY,
    W_REPEATER,
    W_SIGNAL,
    WEAK_LINES,
    WEAK_STATUS,
    WEB_IP,
    WEP,
    WIFI_DIAGNOSES,
    WPA2_PSK,
    WPA2_WPA3,
    WPA3_SAE,
    WPA_TKIP,
    ApConfig,
    Neighbor,
    WifiState,
    audit_config,
    best_channel_24,
    dbm_from_pct,
    drivers_lines,
    first_failure,
    fr,
    fspl_db,
    interference_24,
    link_rate,
    networks_lines,
    nmcli_lines,
    obstacle_loss,
    passphrase_issues,
    quality_pct,
    received_dbm,
    repeater_mbps,
    signal_verdict,
    wifi_checks,
    wifi_diagnosis,
    wifi_ipconfig_lines,
)

PR25_CODE = "PR25"

KIND_ORDER = "ordonnancement"
KIND_CONFIG = "choix de configuration"
KIND_SCHEMA = "schéma à compléter"
KIND_DIAG = "diagnostic sur relevés de commandes"

# Exigence officielle du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-33"})
R_WIFI = ("AP-33",)
R_ACCESS = ("AP-33", "AP-37")  # dépannage de problèmes simples d'accès au réseau
R_INTERNET = ("AP-33", "AP-32")  # interventions en cas de panne Internet


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _diag(state: WifiState) -> str:
    return wifi_diagnosis(wifi_checks(state))


def _short(diagnosis: str) -> str:
    return diagnosis.split(" :")[0].lower()


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(CONFIG_STEPS)
E02_STEPS = _labels(ASSOCIATION_STEPS)
E03_STEPS = _labels(TROUBLE_STEPS)

E04_CASES: tuple[tuple[str, str], ...] = (
    ("WEP avec une clé de 13 caractères, « pour la vieille imprimante »", WEP),
    ("WPA (TKIP), présenté comme « compatible avec tout »", WPA_TKIP),
    ("Réseau du personnel ouvert, sans clé, « pour aller plus vite »", OPEN),
    ("WPA2-Personnel (AES-CCMP) avec une clé de 22 caractères variés", WPA2_PSK),
    ("WPA2/WPA3-Personnel (transition) pour garder deux portables anciens", WPA2_WPA3),
    ("WPA3-Personnel (SAE) dans un bureau dont tous les appareils sont récents", WPA3_SAE),
    ("WPA2/WPA3-Entreprise avec serveur RADIUS pour 60 employés", ENTERPRISE),
)
E04_CORRECT = tuple(SEC_VERDICTS.index(SECURITY_BY_NAME[mode].verdict) for _t, mode in E04_CASES)

E05_CASES: tuple[tuple[str, str], ...] = (
    ("Le portable ne voit pas ATELIER-PRO ; le point d'accès est éteint depuis une coupure de courant", "visible"),
    ("« Impossible de se connecter à ce réseau » juste après le changement de la clé sur la box", "auth"),
    ("Associé à ATELIER-PRO, mais ipconfig affiche 169.254.71.12", "ip"),
    ("Associé, adresse correcte, la passerelle répond, mais aucun nom de site n'est résolu", "internet"),
    ("netsh wlan show interfaces : signal 30 % au fond du stock", "signal"),
    ("Le portable affiche 100 % près du répéteur, mais le répéteur reçoit la box à −81 dBm", "repeteur"),
    ("Point d'accès sur le canal 6, signal −55 dBm, Internet correct, lenteurs : voisins forts sur 4 et 5", "canal"),
    ("Un vieux portable 802.11g ne voit pas le SSID émis seulement en 5 GHz", "visible"),
)
E05_CORRECT = tuple(WIFI_DIAGNOSES.index(wifi_diagnosis(first_failure(k))) for _t, k in E05_CASES)

E06_CASES: tuple[tuple[str, str], ...] = (
    ("Thermostat connecté qui ne gère que le 2,4 GHz", BAND_24),
    ("Caméra au fond du jardin, à 25 m et deux murs du point d'accès", BAND_24),
    ("Visioconférence sur des portables récents, à 6 m du point d'accès, dans la même pièce", BAND_5),
    ("Open space où l'on relève quinze réseaux voisins en 2,4 GHz", BAND_5),
    ("Station de montage vidéo Wi-Fi 7 à 3 m d'un point d'accès Wi-Fi 7, sans mur", BAND_6),
    ("Vieux portable 802.11g utilisé à l'accueil", BAND_24),
    ("Casque de réalité virtuelle Wi-Fi 6E dans la pièce du point d'accès", BAND_6),
)
E06_CORRECT = tuple(BANDS.index(b) for _t, b in E06_CASES)

E07_ANSWERS = ARCH_BLANK_ANSWERS
E08_ANSWERS = CHANNELS_BLANK_ANSWERS
E09_ANSWERS = COVERAGE_BLANK_ANSWERS
E10_ANSWERS = REPEATER_BLANK_ANSWERS

# E11 : choisir le canal 2,4 GHz d'un cabinet à partir du relevé des voisins
E11_SSID = "CABINET-MERCIER"
E11_NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Telenet-5521", 6, -55, "5c:35:3b:01:aa:10"),
    Neighbor("WiFi-Voisin", 7, -68, "e4:8d:8c:22:bb:20"),
    Neighbor("Proximus-A1B2", 11, -83, "f4:ca:e5:33:cc:30"),
    Neighbor("Cafe-Gratuit", 1, -78, "00:1d:7e:44:dd:40"),
)
E11_BEST = best_channel_24(E11_NEIGHBORS)
E11_SCORES = {ch: interference_24(ch, E11_NEIGHBORS) for ch in NON_OVERLAP_24}
E11_LINES = networks_lines(tuple((n.ssid, "WPA2 - Personnel", n) for n in E11_NEIGHBORS))

# E12 : signal faible au fond du stock
E12_DBM = dbm_from_pct(WEAK_STATUS.signal_pct)
E12_DIAG = _diag(WifiState(signal_dbm=E12_DBM))
E12_P4 = SURVEY_BY_KEY["P4"]
E12_NEW_AP = received_dbm(5, BAND_24, ("métal",))

# E13 : associé à AP-02, mais 169.254 (câble de l'injecteur PoE débranché)
E13_STATUS = WifiStatus("connecté", SSID, BSSID_AP2_24, "802.11n", "WPA2 - Personnel", "CCMP", BAND_24, 6, 144, 88)
E13_DIAG = _diag(WifiState(address_ok=False))

# E14 : « Pas d'Internet » : DNS saisi à la main
E14_HOST = Host("LT-07", "portable Wi-Fi", "192.168.20.142", 24, ROUTER_IP, ("192.168.20.250",), "A4-C3-F0-55-20-77",
                dhcp=True)
E14_DIAG = _diag(WifiState(dns_ok=False))

# E15 : mauvaise clé (profil enregistré avec l'ancienne clé)
E15_LINES = (
    *netsh_wlan_lines(WifiStatus("déconnecté", SSID, "", "", "", "", "", 0, 0, 0)),
    "",
    "C:\\> netsh wlan show profiles",
    "Profils utilisateurs",
    "    Profil Tous les utilisateurs : ATELIER-PRO",
    "    Profil Tous les utilisateurs : Gare-Wifi",
)
E15_DIAG = _diag(WifiState(key_ok=False))

# E16 : réseau invisible : SSID émis seulement en 5 GHz, carte 2,4 GHz seulement
E16_SSID = "SALLE-CONSEIL"
E16_LINES = (
    *networks_lines((("Atelier-Voisin", "WPA2 - Personnel", Neighbor("", 3, -70, "f4:ca:e5:10:20:30")),
                     ("Gare-Wifi", "Ouvert", Neighbor("", 11, -82, "00:1d:7e:50:60:70")))),
    "",
    *drivers_lines("802.11b 802.11g 802.11n", BAND_24),
)
E16_DIAG = _diag(WifiState(band_supported=False))

# E17 : audit d'une fiche de configuration de box
E17_CONFIG = ApConfig("GARAGE-HENRI", WPA_TKIP, "Garage2026", wps=True, admin_default=True, firmware_current=False,
                      channel_24=3, width_24=40, ssid_hidden=True, guest_isolated=False, names=("Henri", "Garage"))
E17_ISSUES = audit_config(E17_CONFIG)
E17_FIXED = ApConfig("GARAGE-HENRI", WPA2_WPA3, "Pneus-Cric-Vidange-Atelier-26", channel_24=6, guest_isolated=True,
                     names=("Henri", "Garage"))

# E18 : clés proposées pour une boulangerie
E18_SSID, E18_NAMES = "LENOIR-WIFI", ("Lenoir", "Boulangerie")
E18_KEYS: tuple[str, ...] = (
    "lenoir2026",
    "Azerty123",
    "P@in-Croissant-Four-Levain",
    "Kx7#qT2m",
    "baguette brioche eclair tartelette",
    "Boulangerie-Lenoir-2026!",
)
E18_CATEGORIES = ("Clé acceptable", "Clé à refuser")
E18_ISSUES = {k: passphrase_issues(k, names=(E18_SSID, *E18_NAMES)) for k in E18_KEYS}
E18_CORRECT = tuple(1 if E18_ISSUES[k] else 0 for k in E18_KEYS)

# E19 : deux points d'accès mal assortis (roaming)
E19_ROWS: tuple[tuple[str, str, str], ...] = (
    ("SSID", SSID, "ATELIER-PRO-ETAGE"),
    ("Sécurité", WPA2_WPA3, WPA2_PSK),
    ("Canal 2,4 GHz", "6", "6"),
    ("Canal 5 GHz", "36", "36"),
    ("Largeur 5 GHz", "80 MHz", "80 MHz"),
)

# E20 : invités sur le réseau interne
E20_GUEST_HOST = Host("PC-VISITEUR", "portable d'un visiteur", "192.168.20.161", 24, ROUTER_IP, (SERVER_IP,),
                      "3C-A9-F4-12-34-56", dhcp=True)
E20_STATUS = WifiStatus("connecté", GUEST_SSID, "9c:53:22:10:20:35", "802.11ac", "WPA2 - Personnel", "CCMP", BAND_5,
                        36, 433, 92)

# --- Mini-examen -------------------------------------------------------------------------------

X01_NEIGHBORS: tuple[Neighbor, ...] = (
    Neighbor("Voisin-A", 1, -62, "a0:21:b7:11:11:11"),
    Neighbor("Voisin-B", 6, -60, "a0:21:b7:22:22:22"),
    Neighbor("Voisin-C", 9, -74, "a0:21:b7:33:33:33"),
    Neighbor("Voisin-D", 11, -85, "a0:21:b7:44:44:44"),
)
X01_BEST = best_channel_24(X01_NEIGHBORS)
X01_LINES = networks_lines(tuple((n.ssid, "WPA2 - Personnel", n) for n in X01_NEIGHBORS))
X03_DIAG = _diag(WifiState(radio_on=False))
X04_HOST = Host("LT-12", "portable Wi-Fi", "192.168.0.23", 24, "192.168.0.1", ("192.168.0.1",), "A4-C3-F0-55-20-12",
                dhcp=True)
X04_DIAG = _diag(WifiState(address_ok=False))
X05_DIST, X05_OBST = 15, ("brique", "brique")
X05_FSPL = {b: fspl_db(X05_DIST, BAND_FREQ_MHZ[b]) for b in (BAND_24, BAND_5)}
X05_LOSS = {b: obstacle_loss(X05_OBST, b) for b in (BAND_24, BAND_5)}
X05_24 = received_dbm(X05_DIST, BAND_24, X05_OBST)
X05_5 = received_dbm(X05_DIST, BAND_5, X05_OBST)
X06_UPLINK, X06_CLIENT = -79, -45
X06_MBPS = repeater_mbps(X06_UPLINK, X06_CLIENT)
X06_DIAG = _diag(WifiState(signal_dbm=X06_CLIENT, repeater_uplink_dbm=X06_UPLINK))
X09_ROWS: tuple[tuple[str, int, int, str], ...] = (
    ("RESTO-CUISINE", 3, 64, "WPA2"),
    ("Hotel-Clients", 1, 70, "WPA2"),
    ("Bureau-Etage", 6, 58, "WPA2 WPA3"),
    ("Taxi-Wifi", 13, 18, "WPA2"),
)
X09_NEIGHBORS = tuple(Neighbor(s, ch, dbm_from_pct(sig)) for s, ch, sig, _sec in X09_ROWS[1:])
X09_BEST = best_channel_24(X09_NEIGHBORS)
X09_LINES = nmcli_lines(X09_ROWS)

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la configuration d'un point d'accès",
        question_type="ordering",
        requirement_ids=R_WIFI,
        kind=KIND_ORDER,
        context=(
            "Une agence immobilière de huit personnes remplace sa vieille box par un point d'accès Wi-Fi récent, "
            "câblé à son switch. Ta collègue a noté les huit étapes de la mise en service sur un brouillon, dans le "
            "désordre ; tu dois rendre la fiche propre au gérant."
        ),
        instructions=("Remets les huit étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Placer → sécuriser l'accès d'administration → SSID et bandes → canaux et largeur → sécurité et clé → adressage → invités → tester et consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On choisit l'emplacement (central, en hauteur, hors armoire) et on câble le point d'accès. 2. Par câble, on change le mot de passe d'administration et on met à jour le micrologiciel : un appareil neuf peut avoir des failles déjà corrigées. 3. On nomme le réseau (SSID neutre) et on active les deux bandes. 4. On règle les canaux (1, 6 ou 11 en 20 MHz ; un canal libre en 5 GHz).",
            f"5. On choisit WPA3 ou WPA2/WPA3-Personnel avec une clé longue et on désactive WPS. 6. On vérifie qu'une seule source DHCP distribue adresse, passerelle et DNS. 7. On crée le réseau invités ({GUEST_SSID}) isolé du réseau interne. 8. On teste depuis un portable dans chaque pièce et on remet la fiche. Sécuriser l'administration avant d'émettre évite d'exposer un point d'accès aux réglages d'usine.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (4, 1, 7, 0, 5, 2, 6, 3)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la connexion d'un portable au Wi-Fi",
        question_type="ordering",
        requirement_ids=R_WIFI,
        kind=KIND_ORDER,
        context=(
            "Pour expliquer à un stagiaire pourquoi « connecté » ne veut pas toujours dire « Internet », tu décris "
            "ce qui se passe entre le moment où un portable allumé cherche les réseaux et le moment où il ouvre un "
            "site. Les cinq étapes ont été mélangées."
        ),
        instructions=("Remets les cinq étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 2.5, "Découverte → association → clés → DHCP → passerelle et DNS (0,5 pt par étape)."),
        ),
        correction=(
            "1. Le portable découvre les réseaux (balises des points d'accès ou sondes) : il connaît SSID, BSSID, signal et sécurité. 2. Il s'associe à un BSSID (en WPA3, l'échange SAE a lieu à ce moment). 3. Il prouve qu'il connaît la clé par l'échange en 4 temps ; en Entreprise, le serveur RADIUS vérifie d'abord l'identifiant (802.1X).",
            "4. Il demande une adresse par DHCP : adresse, masque, passerelle, DNS. 5. Il joint la passerelle et résout les noms : Internet. Chaque étape a sa panne typique : invisible (1), clé (2-3), 169.254 (4), « pas d'Internet » (5).",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (3, 0, 4, 2, 1)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le dépannage d'un poste Wi-Fi",
        question_type="ordering",
        requirement_ids=R_ACCESS,
        kind=KIND_ORDER,
        context=(
            "Le service d'assistance d'une PME reçoit chaque semaine « le Wi-Fi ne marche pas ». Tu rédiges la fiche "
            "de dépannage en huit étapes, de la plus générale (le réseau est-il visible ?) à la plus fine (le canal), "
            "pour que chacun suive le même ordre ; le brouillon est dans le désordre."
        ),
        instructions=("Remets les huit étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Constater → réseau visible → clé et sécurité → adresse → Internet → signal et répéteur → canal → corriger et consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On note le message exact et l'étendue (un poste ou tous, quel endroit). 2. Le réseau est-il visible ? 3. La clé et le mode de sécurité sont-ils acceptés ? 4. L'adresse est-elle du bon réseau (pas 169.254) ?",
            f"5. Passerelle, adresse Internet et nom répondent-ils ? 6. Le signal atteint-il {TARGET_DBM} dBm, et le répéteur reçoit-il bien le point d'accès ? 7. Un voisin fort occupe-t-il un canal qui chevauche ? 8. On corrige au plus juste, on teste, on consigne. Le premier contrôle en échec désigne la piste : inutile de changer de canal si la clé est refusée.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (6, 2, 0, 7, 4, 1, 5, 3)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Quel mode de sécurité accepter ?",
        question_type="classification",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Tu audites le Wi-Fi de sept petites entreprises clientes. Pour chacune, tu notes le mode de sécurité "
            "trouvé ou demandé. Range chaque situation : à refuser (à changer immédiatement), acceptable (minimum "
            "admis) ou recommandé."
        ),
        instructions=("Range chaque situation selon le mode de sécurité.",),
        criteria=(
            _c("Classement", 3.5, "WEP, WPA (TKIP), ouvert → à refuser ; WPA2-Personnel AES, transition WPA2/WPA3 → acceptable ; WPA3-Personnel, Entreprise 802.1X/RADIUS → recommandé (0,5 pt par élément)."),
        ),
        correction=(
            "WEP (RC4) se casse en quelques minutes ; WPA avec TKIP est obsolète, retiré des appareils récents et limite le débit à 54 Mb/s ; un réseau du personnel ouvert laisse lire tout le trafic radio. Les trois sont à refuser, même « pour une vieille imprimante » : on remplace l'appareil ou on l'isole.",
            "WPA2-Personnel avec AES-CCMP reste acceptable avec une clé longue et WPS coupé ; le mode de transition WPA2/WPA3 garde les anciens appareils en WPA2 tout en offrant WPA3 aux autres. WPA3-Personnel (SAE) résiste aux attaques par dictionnaire ; l'Entreprise (802.1X/RADIUS) donne un identifiant par personne, révocable au départ d'un employé : tous deux sont recommandés.",
        ),
        classification=Classification(categories=SEC_VERDICTS, elements=tuple(t for t, _m in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Quelle piste pour chaque panne Wi-Fi ?",
        question_type="classification",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            f"L'atelier Durant a deux points d'accès et un répéteur. En un mois, l'assistance a noté huit signalements. "
            "Ordre des contrôles : réseau visible, clé acceptée, adresse du bon réseau, Internet, signal au poste, "
            f"lien du répéteur, canal ; le premier en échec désigne la piste. Seuil de signal : {TARGET_DBM} dBm."
        ),
        instructions=("Range chaque signalement selon la piste à suivre.",),
        criteria=(
            _c("Classement", 4, "Point d'accès éteint et SSID en 5 GHz seul pour une carte 802.11g → réseau invisible ; clé changée → authentification ; 169.254 → adressage ; noms non résolus → sans Internet ; 30 % → couverture ; répéteur à −81 dBm → répéteur mal placé ; voisins sur 4 et 5 → interférences (0,5 pt par élément)."),
        ),
        correction=(
            "Un point d'accès éteint ou une bande que la carte ne gère pas (802.11g = 2,4 GHz seulement) : le réseau n'apparaît pas, c'est la première piste. « Impossible de se connecter » juste après un changement de clé : authentification. Associé mais 169.254 : le DHCP n'a pas répondu, c'est l'adressage. Associé, adresse et passerelle bonnes mais aucun nom résolu : « connecté sans Internet » (DNS).",
            f"30 % correspond à environ {dbm_from_pct(30)} dBm : couverture insuffisante. 100 % près du répéteur ne dit rien du lien répéteur → point d'accès : à −81 dBm, le répéteur est mal placé. Signal bon et Internet correct mais lenteurs avec des voisins forts sur les canaux 4 et 5, qui chevauchent le canal 6 du point d'accès : interférences.",
        ),
        classification=Classification(categories=WIFI_DIAGNOSES, elements=tuple(t for t, _k in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Quelle bande pour chaque appareil ?",
        question_type="classification",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Un studio graphique installe un point d'accès Wi-Fi 7 qui émet en 2,4, 5 et 6 GHz. Tu dois indiquer, pour "
            "sept appareils, la bande la plus adaptée : 2,4 GHz porte plus loin mais est encombrée ; 5 GHz offre plus "
            "de débit et de canaux ; 6 GHz est la plus rapide et la plus libre, mais la plus courte et réservée aux "
            "appareils Wi-Fi 6E ou 7."
        ),
        instructions=("Range chaque appareil selon la bande à lui faire utiliser.",),
        criteria=(
            _c("Classement", 3.5, "Thermostat 2,4 GHz seul, caméra lointaine, portable 802.11g → 2,4 GHz ; visioconférence proche, open space encombré → 5 GHz ; station Wi-Fi 7 proche, casque Wi-Fi 6E → 6 GHz (0,5 pt par élément)."),
        ),
        correction=(
            "Un appareil qui ne gère que le 2,4 GHz (thermostat, 802.11g) n'a pas le choix. La caméra à 25 m derrière deux murs profite de la meilleure portée du 2,4 GHz. Les portables récents proches, ou un open space où le 2,4 GHz est saturé, gagnent à passer en 5 GHz : plus de canaux, plus de débit.",
            "Les appareils Wi-Fi 6E ou 7, proches du point d'accès et sans mur, utilisent le 6 GHz : canaux larges et libres, WPA3 obligatoire. Le 6 GHz traverse mal les murs : il ne remplace pas le 5 GHz pour une pièce éloignée.",
        ),
        classification=Classification(categories=BANDS, elements=tuple(t for t, _b in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : qui fait quoi dans le Wi-Fi ?",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_SCHEMA,
        context=(
            "Le gérant de l'atelier Durant confond « la box », « le Wi-Fi » et « le répéteur ». Tu lui remets le "
            "schéma de son installation avec le rôle de chaque équipement : box, serveur SRV-01, deux points d'accès "
            "câblés et un répéteur dans l'annexe. Le document 1 est le schéma à terminer."
        ),
        documents=(_schema("pr25-architecture-a-completer", "Document 1 — Architecture Wi-Fi à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique la différence entre SSID et BSSID avec l'exemple de l'atelier.",
        ),
        criteria=(
            _c("Rôles", 2, " ; ".join(f"{k} {v}" for k, v in E07_ANSWERS.items()) + " (0,5 pt chacun)."),
            _c("SSID et BSSID", 1, f"SSID = nom du réseau ({SSID}), le même sur AP-01, AP-02 et le répéteur ; BSSID = adresse MAC de chaque radio, différente pour chaque point d'accès et chaque bande."),
        ),
        correction=(
            f"① La box est le routeur : passerelle vers Internet, traduction d'adresses (NAT) et pare-feu. ② SRV-01 est le serveur DHCP et DNS : c'est lui qui donne les adresses aux clients Wi-Fi, pas le point d'accès. ③ {AP2_NAME} est un point d'accès câblé : relié au switch, il offre tout le débit. ④ Le répéteur reçoit le signal d'un point d'accès et le retransmet par radio, sans câble.",
            f"Le SSID est le nom affiché ({SSID}) : il est identique sur toutes les radios pour que le portable passe de l'une à l'autre. Le BSSID est l'adresse MAC d'une radio : {BSSID_AP1_24} pour AP-01 en 2,4 GHz, {BSSID_AP1_5} pour AP-01 en 5 GHz, {BSSID_AP2_24} pour AP-02. netsh wlan show interfaces affiche le BSSID et dit donc à quel point d'accès on est associé.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : canaux 2,4 GHz",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_SCHEMA,
        context=(
            "Les employés de l'atelier se plaignent de lenteurs. Tu as relevé les réseaux voisins en 2,4 GHz depuis "
            "le bureau (boulangerie, cabinet, box des voisins) et tu prépares le schéma qui justifiera ton choix de "
            "canal auprès du gérant. Le document 1 est le schéma à terminer."
        ),
        documents=(_schema("pr25-canaux-a-completer", "Document 1 — Canaux 2,4 GHz à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ (canaux sans chevauchement) et ④ (canal conseillé).",
            "Justifie ④ voisin par voisin et indique la largeur de canal à régler en 2,4 GHz.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in E08_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, f"Canal 1 : Boulangerie (−58) et Proximus canal 3 (−71) ; canal 6 : Proximus canal 3 (−71) ; canal 11 : seulement Livebox canal 13 (−79), Cabinet à −88 trop faible pour gêner → canal {NEIGHBORS_BEST} ; 20 MHz en 2,4 GHz."),
        ),
        correction=(
            "① 1, ② 6 et ③ 11 : les canaux sont espacés de 5 MHz mais chacun occupe environ 22 MHz ; seuls trois canaux distants de 5 numéros ne se chevauchent pas. On n'utilise donc que 1, 6 ou 11.",
            f"④ Canal {NEIGHBORS_BEST}. Sur le 1, la boulangerie est très forte (−58 dBm) et le canal 3 de Proximus chevauche (−71). Sur le 6, Proximus canal 3 chevauche aussi (−71). Sur le 11, le cabinet (−88 dBm) est sous le seuil de −80, et seule la Livebox du canal 13 gêne, plus faiblement (−79). En 2,4 GHz, on garde 20 MHz : un canal de 40 MHz y occuperait presque toute la bande.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : couverture d'un point d'accès",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_SCHEMA,
        context=(
            "Avant de proposer du matériel à l'atelier Durant, tu estimes la couverture de AP-01 (20 dBm rayonnés) "
            "aux cinq endroits importants, en 2,4 et en 5 GHz : espace libre, puis affaiblissement des murs, de la "
            f"dalle et des rayonnages métalliques. Objectif : {TARGET_DBM} dBm ou mieux. Le document 1 est ton plan à terminer."
        ),
        documents=(_schema("pr25-couverture-a-completer", "Document 1 — Couverture à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④ (valeur en dBm et appréciation).",
            "Conclus : quelles zones posent problème et que proposes-tu ?",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in E09_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Conclusion", 1, "Stock insuffisant même en 2,4 GHz (béton + métal) → point d'accès câblé dans le stock ; étage faible en 5 GHz → AP-02 câblé à l'étage ; le 5 GHz porte moins loin et traverse moins bien."),
        ),
        correction=(
            f"Avec la formule du cours (20 dBm − espace libre − obstacles) : ① P3 en 2,4 GHz {E09_ANSWERS['①']} ; ② P3 en 5 GHz {E09_ANSWERS['②']} : à distance égale, le 5 GHz perd environ 6,5 dB de plus en espace libre et davantage dans les murs. ③ P4, le stock, en 2,4 GHz : {E09_ANSWERS['③']}, à cause du béton et du métal. ④ P5, l'étage, en 5 GHz : {E09_ANSWERS['④']}, la dalle coûte 25 dB.",
            "Conclusion : le stock n'est pas couvert, même en 2,4 GHz : on y place un point d'accès câblé (un répéteur derrière du béton recevrait lui-même mal). L'étage est correct en 2,4 GHz mais faible en 5 GHz : AP-02, câblé, y est justifié. Ce sont des estimations : on confirme par une mesure sur place.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : placer un répéteur",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_SCHEMA,
        context=(
            "Le gérant a branché un répéteur dans l'annexe, juste à côté du portable de l'apprenti : « il affiche cinq "
            "barres, mais Internet rame ». Tu compares deux emplacements, avec un répéteur à une seule radio en "
            "2,4 GHz. Le document 1 est le schéma à terminer."
        ),
        documents=(_schema("pr25-repeteur-a-completer", "Document 1 — Emplacement du répéteur à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique pourquoi le portable affiche « cinq barres » alors qu'Internet est lent, et donne la règle de placement.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in E10_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Explication", 1, f"Les barres mesurent le lien portable → répéteur ; le goulot est le lien répéteur → point d'accès ; le répéteur se place là où il reçoit {TARGET_DBM} dBm ou mieux, à mi-chemin ; une radio = débit divisé par deux ; un point d'accès câblé reste préférable."),
        ),
        correction=(
            f"① Dans l'annexe, le répéteur reçoit AP-01 à {REPEATER_BAD.uplink_dbm} dBm ({signal_verdict(REPEATER_BAD.uplink_dbm)}) : liaison à {link_rate(REPEATER_BAD.uplink_dbm)} Mb/s. ② Le portable n'obtient qu'{E10_ANSWERS['②']} : le plus faible des deux liens, divisé par deux (une radio) puis moitié utile. ③ À mi-chemin, le répéteur reçoit {E10_ANSWERS['③']}. ④ Le portable obtient alors {E10_ANSWERS['④']}, bien que lui-même reçoive moins fort ({REPEATER_GOOD.client_dbm} dBm).",
            f"Les barres du portable ne mesurent que son lien avec le répéteur, tout proche. Tout le trafic passe ensuite par le lien répéteur → point d'accès, très faible. Règle : le répéteur se place là où il reçoit encore {TARGET_DBM} dBm ou mieux, à peu près à mi-chemin ; si un câble est possible, un point d'accès câblé fait mieux.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Choisir le canal d'un cabinet à partir du relevé des voisins",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            f"Un cabinet d'avocats installe son point d'accès « {E11_SSID} » au premier étage d'un immeuble de "
            "bureaux. Avant de régler le canal 2,4 GHz, tu relèves les réseaux voisins depuis le bureau principal "
            "(document 1). Seuil de gêne retenu : un voisin reçu à −80 dBm ou plus, sur un canal à moins de 5 "
            "numéros. Rappel : sur Windows, 0 % ≈ −100 dBm et 100 % ≈ −50 dBm."
        ),
        documents=(_console("Document 1 — réseaux voisins (capture fictive)", *E11_LINES),),
        instructions=(
            "Convertis chaque signal en dBm et évalue les canaux 1, 6 et 11.",
            "Donne le canal 2,4 GHz retenu et ton conseil pour les portables récents.",
        ),
        criteria=(
            _c("Évaluation", 2, "Telenet canal 6 −55 et WiFi-Voisin canal 7 −68 gênent le 6 ; WiFi-Voisin canal 7 gêne aussi le 11 (4 numéros) ; Proximus canal 11 à −83 ne gêne pas ; Cafe-Gratuit canal 1 à −78 gêne le 1."),
            _c("Choix", 1, f"Canal {E11_BEST} (un seul voisin, le plus faible à −78) en 20 MHz ; portables récents en 5 GHz."),
        ),
        correction=(
            f"Conversion : {', '.join(f'{n.ssid} {quality_pct(n.dbm)} % ≈ {n.dbm} dBm' for n in E11_NEIGHBORS)}. Canal 1 : Cafe-Gratuit (−78) gêne. Canal 6 : Telenet (−55) et WiFi-Voisin du canal 7 (−68). Canal 11 : Proximus à −83 est sous le seuil, mais WiFi-Voisin du canal 7 chevauche le 11 (4 numéros d'écart) à −68.",
            f"Le canal {E11_BEST} n'a qu'un voisin gênant, le plus faible : on le retient, en 20 MHz. Piège : le canal 11, qui « porte le moins de voisins », est gêné par le canal 7. On active aussi le 5 GHz, beaucoup moins encombré, pour les portables récents.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Connecté, mais très lent au fond du stock",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            "Le magasinier de l'atelier Durant scanne les livraisons avec un portable au fond du stock (rayonnages "
            "métalliques, mur en béton entre le stock et l'atelier où se trouve AP-01). Les pages mettent une minute à "
            "s'ouvrir, la connexion tombe parfois ; dans l'atelier, tout est rapide. Le document 1 est relevé au fond du stock."
        ),
        documents=(_console("Document 1 — état de la carte Wi-Fi (capture fictive)", *WEAK_LINES),),
        instructions=(
            "Lis le relevé : association, sécurité, bande, signal (en dBm) et débit.",
            "Donne la piste et une solution durable.",
        ),
        criteria=(
            _c("Lecture", 1.5, f"Connecté à {SSID} (WPA2, CCMP) sur AP-01 en 2,4 GHz ; signal {WEAK_STATUS.signal_pct} % ≈ {E12_DBM} dBm ({signal_verdict(E12_DBM)}) ; réception {WEAK_STATUS.rx_mbps} Mb/s ; association et clé correctes."),
            _c("Piste et solution", 1.5, f"{_short(E12_DIAG)} : béton + métal ; point d'accès câblé dans le stock (≈ {E12_NEW_AP} dBm), sur un autre canal ; pas un répéteur derrière le béton ; mesure après."),
        ),
        correction=(
            f"Le portable est associé à {SSID} et authentifié (WPA2, CCMP) : la clé n'est pas en cause. Le BSSID est celui de AP-01, de l'autre côté du mur en béton. Le signal de {WEAK_STATUS.signal_pct} % correspond à environ {E12_DBM} dBm, {signal_verdict(E12_DBM)} : la liaison descend à {WEAK_STATUS.rx_mbps} Mb/s.",
            f"Piste : {_short(E12_DIAG)}. Solution durable : un point d'accès câblé dans le stock (même SSID, même sécurité, autre canal 2,4 GHz que AP-01) ; à 5 m derrière un rayonnage, on estime {E12_NEW_AP} dBm. Un répéteur placé dans le stock recevrait lui-même AP-01 trop faiblement. On mesure de nouveau avant de clôturer.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Associé au point d'accès, mais adresse 169.254",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            f"Depuis ce matin, à l'étage de l'atelier, les portables se connectent au Wi-Fi mais « n'ont plus rien ». "
            f"Au rez-de-chaussée, tout fonctionne. {AP2_NAME} (étage) est alimenté par un injecteur PoE posé au sol, "
            "relié au switch par un câble ; la femme de ménage a déplacé les meubles hier soir. Documents 1 et 2 relevés à l'étage."
        ),
        documents=(
            _console("Document 1 — état de la carte Wi-Fi (capture fictive)", *netsh_wlan_lines(E13_STATUS)),
            _console("Document 2 — configuration IP (capture fictive)", *wifi_ipconfig_lines(LAPTOP_APIPA, apipa=True)),
        ),
        instructions=(
            "Indique ce qui fonctionne et ce qui ne fonctionne pas, preuves à l'appui.",
            "Donne la cause probable, la vérification et la correction.",
        ),
        criteria=(
            _c("Analyse", 1.5, f"Radio, association et clé correctes (connecté, BSSID {BSSID_AP2_24} = AP-02, signal 88 %) ; adresse 169.254 sans passerelle = aucun bail DHCP ; seule l'étage est touchée → {_short(E13_DIAG)} en aval de AP-02."),
            _c("Cause et correction", 1.5, "Le point d'accès émet (alimenté) mais n'est plus relié au switch : câble injecteur → switch débranché ; vérifier voyants et port du switch ; rebrancher, ipconfig /renew, adresse 192.168.20.x et ping de la passerelle."),
        ),
        correction=(
            f"Le document 1 montre un portable connecté à {SSID}, authentifié (WPA2, CCMP), avec un très bon signal, sur le BSSID {BSSID_AP2_24}, celui de {AP2_NAME} : radio et clé vont bien. Le document 2 montre une adresse {LAPTOP_APIPA.ip} sans passerelle : le portable n'a reçu aucune réponse DHCP. Piste : {_short(E13_DIAG)}.",
            f"Comme seul {AP2_NAME} est concerné, le problème est entre ce point d'accès et le réseau : alimenté par son injecteur, il émet encore, mais le câble de données vers le switch a été débranché pendant le ménage. On vérifie les voyants de l'injecteur et du port du switch, on rebranche, puis ipconfig /renew : adresse en 192.168.20.x, passerelle {ROUTER_IP}, ping réussi.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="« Pas d'Internet, sécurisé » : connecté sans Internet",
        question_type="document_analysis",
        requirement_ids=R_INTERNET,
        kind=KIND_DIAG,
        context=(
            "Un commercial revient de chez un client où un technicien avait « dépanné » son portable. Au bureau, Windows "
            "affiche « Pas d'Internet, sécurisé » sur ATELIER-PRO ; les collègues n'ont aucun problème. Les "
            "documents 1 à 3 sont tes relevés sur son portable."
        ),
        documents=(
            _console("Document 1 — configuration IP (capture fictive)", *wifi_ipconfig_lines(E14_HOST)),
            _console("Document 2 — ping d'une adresse Internet (capture fictive)", *INTERNET_PING_OK),
            _console("Document 3 — résolution d'un nom (capture fictive)", *DNS_TIMEOUT_LINES),
        ),
        instructions=(
            "Indique quelles étapes de la connexion fonctionnent et laquelle échoue.",
            "Donne la cause, la correction et le test.",
        ),
        criteria=(
            _c("Analyse", 1.5, f"Wi-Fi et adresse corrects (192.168.20.142, passerelle {ROUTER_IP}) ; le ping de {WEB_IP} répond → passerelle et Internet fonctionnent ; nslookup expire sur 192.168.20.250 → DNS ; piste {_short(E14_DIAG)}."),
            _c("Correction", 1.5, f"DNS saisi à la main (192.168.20.250, inexistant) → remettre « obtenir automatiquement » ; ipconfig /flushdns ; nslookup répond via {SERVER_IP} ; ouvrir un site."),
        ),
        correction=(
            f"Le portable a une adresse du bon réseau et la passerelle {ROUTER_IP} : l'association et le DHCP vont bien. Le ping de {WEB_IP} répond : la box et la liaison Internet fonctionnent. En revanche, nslookup interroge 192.168.20.250 et le délai expire : aucun nom n'est résolu, d'où « Pas d'Internet ». Piste : {_short(E14_DIAG)}, côté DNS.",
            f"Le DNS 192.168.20.250 a été saisi à la main chez le client ; il n'existe pas ici (le DNS de l'atelier est SRV-01, {SERVER_IP}). On remet le DNS en « obtenir automatiquement » sur la carte Wi-Fi, ipconfig /flushdns, puis nslookup doit répondre par {SERVER_IP} et un site doit s'ouvrir. On note la configuration d'origine dans le compte rendu.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="La clé a changé, un portable ne se connecte plus",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            "Hier, après le départ d'un employé, tu as changé la clé du Wi-Fi ATELIER-PRO et l'as communiquée par écrit. "
            "Ce matin, une comptable rentrée de congé clique sur ATELIER-PRO : Windows affiche « Impossible de se "
            "connecter à ce réseau ». Les autres postes, ressaisis hier, fonctionnent. Le document 1 est relevé sur son portable."
        ),
        documents=(_console("Document 1 — état de la carte et profils enregistrés (capture fictive)", *E15_LINES),),
        instructions=(
            "Donne la piste et justifie à partir du relevé et du contexte.",
            "Décris la correction pas à pas, sans affaiblir la sécurité.",
        ),
        criteria=(
            _c("Diagnostic", 1.5, f"Réseau visible (elle clique dessus), carte déconnectée, profil ATELIER-PRO enregistré avec l'ancienne clé → {_short(E15_DIAG)} ; les autres postes avec la nouvelle clé fonctionnent."),
            _c("Correction", 1.5, "Oublier le réseau (Paramètres ou netsh wlan delete profile name=ATELIER-PRO), se reconnecter avec la nouvelle clé ; ne pas remettre l'ancienne clé ni passer en réseau ouvert ; vérifier connecté + ipconfig."),
        ),
        correction=(
            f"Le réseau est visible, la radio fonctionne ; la carte reste déconnectée et Windows garde un profil ATELIER-PRO : il présente encore l'ancienne clé, refusée depuis hier. Piste : {_short(E15_DIAG)}. Les autres postes, dont le profil a été ressaisi, le confirment.",
            "Correction : Paramètres → Wi-Fi → Gérer les réseaux connus → ATELIER-PRO → Oublier (ou netsh wlan delete profile name=ATELIER-PRO), puis reconnexion avec la nouvelle clé lue sur la fiche. Vérification : netsh wlan show interfaces « connecté », adresse en 192.168.20.x. On ne remet pas l'ancienne clé : elle était connue de l'employé parti.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Le réseau de la salle du conseil est invisible",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            f"Une commune a installé dans la salle du conseil un point d'accès qui émet le SSID « {E16_SSID} » "
            "en 5 GHz seulement (canal 44). Les smartphones et les portables récents le voient. Le portable d'un "
            "conseiller, acheté il y a plus de dix ans, ne le voit pas, assis à 4 m du point d'accès. Le document 1 "
            "est relevé sur ce portable."
        ),
        documents=(_console("Document 1 — réseaux visibles et carte Wi-Fi (capture fictive)", *E16_LINES),),
        instructions=(
            "Explique pourquoi le réseau est invisible pour ce portable seulement.",
            "Propose deux solutions et recommande-en une.",
        ),
        criteria=(
            _c("Diagnostic", 1.5, f"Le portable voit des réseaux 2,4 GHz (radio active) mais pas {E16_SSID} ; sa carte ne gère que 802.11b/g/n en 2,4 GHz ; le SSID n'est émis qu'en 5 GHz → {_short(E16_DIAG)} (bande non prise en charge)."),
            _c("Solutions", 1.5, "Activer aussi la bande 2,4 GHz sur le point d'accès (même SSID, canal 1, 6 ou 11, 20 MHz) ou ajouter une clé USB Wi-Fi double bande ; recommandation argumentée ; pas de réseau ouvert."),
        ),
        correction=(
            f"La radio du portable fonctionne : il voit Atelier-Voisin et Gare-Wifi, en 2,4 GHz. netsh wlan show drivers indique 802.11b, g et n en 2,4 GHz seulement : la carte n'écoute jamais la bande 5 GHz. Le SSID {E16_SSID}, émis seulement en 5 GHz, lui est donc invisible, même à 4 m. Piste : {_short(E16_DIAG)}.",
            "Solution 1 : activer la bande 2,4 GHz du point d'accès avec le même SSID et la même sécurité (canal 1, 6 ou 11, 20 MHz) ; tous les anciens appareils en profitent. Solution 2 : une clé USB Wi-Fi double bande pour ce portable. On recommande la première si d'autres anciens appareils existent, la seconde si l'on veut garder le 2,4 GHz éteint. Si la carte ne gère pas WPA3, le mode de transition WPA2/WPA3 est nécessaire.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Auditer la fiche de configuration d'une box",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Le garage Henri (cinq employés, une borne invités pour les clients) te confie son Wi-Fi « qui marche ». "
            "Avant toute modification, tu relèves les réglages dans l'interface de la box (document 1). Le garage "
            "n'a plus d'appareil antérieur à 2015."
        ),
        documents=(_table(
            "Document 1 — Réglages relevés dans la box",
            ("Paramètre", "Valeur relevée"),
            ("SSID", f"{E17_CONFIG.ssid} (masqué)"),
            ("Sécurité", "WPA (TKIP)"),
            ("Clé", E17_CONFIG.passphrase),
            ("WPS", "activé (code PIN)"),
            ("Mot de passe d'administration", "celui de l'étiquette d'usine (admin)"),
            ("Micrologiciel", "version de 2021, mise à jour disponible"),
            ("Canal et largeur 2,4 GHz", f"{E17_CONFIG.channel_24}, {E17_CONFIG.width_24} MHz"),
            ("Réseau invités", "même réseau que les postes, pas d'isolation"),
        ),),
        instructions=(
            "Relève chaque défaut et justifie-le.",
            "Rédige la fiche corrigée.",
        ),
        criteria=(
            _c("Défauts", 3, f"{len(E17_ISSUES)} défauts : " + " ; ".join(p for p, _c2 in E17_ISSUES) + " (environ 0,33 pt chacun)."),
            _c("Fiche corrigée", 1, f"SSID diffusé, {E17_FIXED.security}, clé longue, WPS coupé, mot de passe d'administration changé, micrologiciel à jour, canal 1, 6 ou 11 en 20 MHz, invités isolés (VLAN, isolation)."),
        ),
        correction=(
            "Sécurité : WPA avec TKIP est obsolète (et limite le débit) ; tous les appareils sont récents, on passe en WPA2/WPA3-Personnel (ou WPA3). Clé « Garage2026 » : courte, devinable (contient le nom). WPS en code PIN : vulnérable, on le désactive. Mot de passe d'administration d'usine : n'importe qui sur le réseau peut tout changer. Micrologiciel de 2021 : failles corrigées depuis.",
            f"Canal 3 en 40 MHz : il chevauche presque toute la bande ; on choisit 1, 6 ou 11 en 20 MHz. SSID masqué : n'apporte aucune sécurité (le nom circule quand même) et gêne les connexions ; on le diffuse. Invités sur le réseau des postes : un client pourrait atteindre les PC du garage ; on isole le réseau invités. Fiche corrigée : {E17_CONFIG.ssid} diffusé, WPA2/WPA3, clé de type « Pneus-Cric-Vidange-Atelier-26 », WPS coupé, mot de passe d'administration personnel, micrologiciel à jour, canal 6 en 20 MHz, invités isolés.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Quelle clé Wi-Fi accepter ?",
        question_type="classification",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            f"La boulangerie Lenoir (SSID « {E18_SSID} ») veut une nouvelle clé WPA2/WPA3-Personnel. Règle du cours : "
            "au moins 12 caractères avec trois types (minuscules, majuscules, chiffres, symboles), ou une phrase de "
            "20 caractères et plus ; rien de devinable (nom du réseau, de l'entreprise, mot de passe courant). "
            "La gérante propose six clés."
        ),
        instructions=("Range chaque clé : acceptable ou à refuser.",),
        criteria=(
            _c("Classement", 3, "P@in-Croissant-Four-Levain et la phrase « baguette brioche eclair tartelette » → acceptables ; lenoir2026, Azerty123, Kx7#qT2m et Boulangerie-Lenoir-2026! → à refuser (0,5 pt par clé)."),
        ),
        correction=(
            "« lenoir2026 » : 10 caractères, deux types, contient le nom. « Azerty123 » : mot de passe parmi les plus essayés. « Kx7#qT2m » : varié mais 8 caractères seulement. « Boulangerie-Lenoir-2026! » : longue et variée, mais construite sur le nom de l'entreprise, la première idée d'un attaquant.",
            "« P@in-Croissant-Four-Levain » (26 caractères variés) et « baguette brioche eclair tartelette » (34 caractères) sont acceptables : la longueur fait la force d'une clé WPA. On la note sur la fiche remise à la gérante, pas sur une étiquette collée sous la box visible des clients.",
        ),
        classification=Classification(categories=E18_CATEGORIES, elements=E18_KEYS, correct=E18_CORRECT),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Deux points d'accès mal assortis : le portable décroche",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            f"À l'atelier, un employé en visioconférence monte du rez à l'étage : l'appel coupe, puis il doit choisir "
            f"un autre réseau à la main. AP-01 (rez) et {AP2_NAME} (étage) sont câblés au même switch. Le document 1 "
            "compare leurs réglages."
        ),
        documents=(_table(
            "Document 1 — Réglages des deux points d'accès",
            ("Paramètre", "AP-01 (rez)", f"{AP2_NAME} (étage)"),
            *E19_ROWS,
        ),),
        instructions=(
            "Relève ce qui empêche le passage automatique de l'un à l'autre (roaming) et ce qui provoque des interférences.",
            "Donne les réglages corrigés de AP-02.",
        ),
        criteria=(
            _c("Défauts", 1.5, "SSID différents → le portable ne considère pas AP-02 comme le même réseau ; sécurités différentes (et donc profils différents) ; mêmes canaux 6 et 36 → les deux points d'accès se gênent là où leurs zones se recouvrent."),
            _c("Réglages", 1.5, f"AP-02 : SSID {SSID}, {WPA2_WPA3}, même clé ; canal 2,4 GHz 1 ou 11 (≠ 6) ; canal 5 GHz 52 ou 44 (≠ 36), largeur cohérente ; zones qui se recouvrent un peu ; 802.11k/v/r si disponibles."),
        ),
        correction=(
            "Pour qu'un portable passe d'un point d'accès à l'autre sans intervention, les deux doivent émettre le même SSID avec la même sécurité et la même clé : c'est alors le même réseau, sur deux BSSID. Ici, le SSID et la sécurité diffèrent : le portable reste accroché à AP-01 jusqu'à la coupure, puis demande un autre réseau.",
            f"De plus, les deux points d'accès utilisent les mêmes canaux (6 et 36) : là où leurs zones se recouvrent, ils se gênent. Réglages de AP-02 : SSID {SSID}, {WPA2_WPA3}, même clé ; 2,4 GHz sur 1 ou 11 ; 5 GHz sur un autre bloc (44 en 40 MHz, ou 52 en 80 MHz) ; on active 802.11k/v/r si le matériel le propose. Test : marcher du rez à l'étage pendant un appel, le BSSID change sans coupure.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Un visiteur sur le Wi-Fi invités atteint le NAS",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_DIAG,
        context=(
            f"Lors d'un contrôle, tu connectes un portable de test au Wi-Fi « {GUEST_SSID} », prévu pour les clients : "
            f"il doit être isolé dans le VLAN {GUEST_VLAN} ({GUEST_NETWORK}, passerelle {GUEST_GATEWAY}) et ne voir "
            "qu'Internet. Les documents 1 à 3 sont tes relevés."
        ),
        documents=(
            _console("Document 1 — état de la carte Wi-Fi (capture fictive)", *netsh_wlan_lines(E20_STATUS)),
            _console("Document 2 — configuration IP (capture fictive)", *wifi_ipconfig_lines(E20_GUEST_HOST)),
            _console("Document 3 — ping du NAS de l'atelier (capture fictive)", *win_ping_lines(NAS_IP, (1, 1, 1, 1))),
        ),
        instructions=(
            "Montre, preuves à l'appui, que le réseau invités n'est pas isolé.",
            "Donne la correction et les tests de validation.",
        ),
        criteria=(
            _c("Constat", 1.5, f"Connecté à {GUEST_SSID} mais adresse 192.168.20.161 (réseau interne) au lieu de 10.30.0.x, DHCP de SRV-01 ; le NAS ({NAS_IP}) répond → un visiteur atteint les données de l'atelier."),
            _c("Correction et tests", 1.5, f"Associer le SSID invités au VLAN {GUEST_VLAN} (port du switch en mode trunk vers le point d'accès), isolation des clients, accès au réseau interne bloqué ; tests : adresse 10.30.0.x, ping du NAS refusé, Internet OK."),
        ),
        correction=(
            f"Le document 1 confirme l'association au SSID {GUEST_SSID}. Mais le document 2 montre une adresse 192.168.20.161, donnée par SRV-01 : le portable est sur le réseau interne, pas dans le VLAN {GUEST_VLAN} ({GUEST_NETWORK}). Le document 3 le prouve : le NAS de l'atelier répond. N'importe quel client peut tenter d'ouvrir les partages.",
            f"Correction : dans le point d'accès, associer le SSID invités au VLAN {GUEST_VLAN} et activer l'isolation des clients ; vérifier que le port du switch qui alimente le point d'accès transporte bien ce VLAN et que la box bloque le passage du VLAN {GUEST_VLAN} vers le réseau interne. Tests : adresse en 10.30.0.x et passerelle {GUEST_GATEWAY}, ping du NAS refusé, un site Internet s'ouvre.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions, 2 points chacune, réponses libres
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Bande et canal pour un bureau partagé",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Une agence de traduction s'installe dans un centre d'affaires et reçoit un point d'accès double bande. "
            "Le document 1 est le relevé des voisins depuis son bureau. Seuil de gêne : −80 dBm ou plus sur un canal "
            "à moins de 5 numéros ; 0 % ≈ −100 dBm et 100 % ≈ −50 dBm."
        ),
        documents=(_console("Document 1 — réseaux voisins (capture fictive)", *X01_LINES),),
        instructions=("Choisis le canal 2,4 GHz et sa largeur, justifie voisin par voisin, puis donne ton conseil pour le 5 GHz.",),
        criteria=(
            _c("Canal 2,4 GHz", 1, f"Canal {X01_BEST} en 20 MHz : 1 gêné par Voisin-A (−62) ; 6 par Voisin-B (−60) et Voisin-C canal 9 (−74) ; 11 seulement par Voisin-C (−74), Voisin-D à −85 sous le seuil."),
            _c("5 GHz", 1, "Activer le 5 GHz pour les portables (plus de canaux, peu de voisins), canal libre en 40 ou 80 MHz ; 36 à 48 sans DFS."),
        ),
        correction=(
            f"Conversion : Voisin-A {X01_NEIGHBORS[0].dbm}, Voisin-B {X01_NEIGHBORS[1].dbm}, Voisin-C {X01_NEIGHBORS[2].dbm}, Voisin-D {X01_NEIGHBORS[3].dbm} dBm. Le canal {X01_BEST} n'est gêné que par Voisin-C (canal 9, −74), plus faible que les voisins des canaux 1 et 6 ; Voisin-D (−85) est sous le seuil. On le règle en 20 MHz.",
            "Le 5 GHz, moins encombré, accueille les portables récents : canal libre (36 à 48 sans détection radar, ou au-delà avec DFS) en 40 ou 80 MHz.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Le client veut garder WEP et WPS",
        question_type="long_answer",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Un imprimeur te demande de laisser le Wi-Fi de l'atelier en WEP « parce que la vieille étiqueteuse "
            "ne connaît que ça » et de garder le bouton WPS « pour connecter facilement les tablettes des "
            "intérimaires ». L'atelier contient les fichiers de ses clients."
        ),
        instructions=("Rédige ta réponse au client : risques, solution technique et réglages recommandés.",),
        criteria=(
            _c("Risques", 1, "WEP se casse en quelques minutes → tout le réseau exposé ; WPS (code PIN) devinable, et les intérimaires gardent l'accès après leur départ."),
            _c("Solution", 1, "Réseau principal en WPA2/WPA3 (ou WPA3), WPS désactivé ; étiqueteuse remplacée, ou reliée par câble ou isolée sur un réseau séparé sans accès aux fichiers ; intérimaires sur un réseau invités ou identifiants individuels (Entreprise)."),
        ),
        correction=(
            "WEP est cassé : la clé se retrouve en quelques minutes en écoutant le réseau, ce qui exposerait les fichiers des clients. Le code PIN WPS se devine par essais, et toute personne qui a appuyé une fois sur le bouton garde l'accès.",
            "On passe le réseau principal en WPA2/WPA3 avec une clé longue et WPS désactivé. L'étiqueteuse est remplacée, reliée par câble, ou isolée sur un réseau séparé sans accès aux fichiers. Les intérimaires utilisent un réseau invités isolé, ou un identifiant personnel en WPA2/WPA3-Entreprise si l'atelier dispose d'un serveur RADIUS.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Le Wi-Fi disparaît chaque soir",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            "Dans une salle de sport, l'équipe du soir signale que le réseau STUDIO-PRO « disparaît » vers 19 h : il n'apparaît "
            "plus dans la liste, sur aucun appareil. Le matin, tout fonctionne. Le document 1 reprend une page de "
            "l'interface du point d'accès."
        ),
        documents=(_table(
            "Document 1 — Page « Sans fil » du point d'accès",
            ("Rubrique", "Réglage"),
            ("Radio 2,4 GHz", "activée, canal 6"),
            ("Radio 5 GHz", "activée, canal 44"),
            ("Programmation Wi-Fi", "activée : radio coupée de 19 h 00 à 7 h 00"),
            ("Diffusion du SSID", "oui"),
        ),),
        instructions=("Donne la piste, la cause et la correction, puis le test.",),
        criteria=(
            _c("Piste et cause", 1, f"{_short(X03_DIAG)} : sur tous les appareils, à heure fixe ; la programmation coupe la radio de 19 h à 7 h."),
            _c("Correction et test", 1, "Adapter la plage horaire à l'ouverture (ou la désactiver) avec l'accord du gérant ; test après 19 h : SSID visible, connexion."),
        ),
        correction=(
            f"Le réseau disparaît pour tous les appareils, chaque soir à la même heure : c'est l'émission elle-même qui cesse. Piste : {_short(X03_DIAG)}. La page montre la cause : la programmation coupe la radio de 19 h à 7 h (réglage d'économie d'énergie).",
            "Avec l'accord du gérant, on adapte la plage aux heures d'ouverture (par exemple de 23 h à 6 h) ou on désactive la programmation. Test après 19 h : STUDIO-PRO apparaît et un appareil se connecte.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Un répéteur distribue de mauvaises adresses",
        question_type="document_analysis",
        requirement_ids=R_INTERNET,
        kind=KIND_DIAG,
        context=(
            "Dans un cabinet dont le réseau est 192.168.20.0/24 (passerelle et DHCP : la box, 192.168.20.1), un "
            "employé a branché lui-même un « répéteur » acheté en grande surface. Depuis, certains portables n'ont "
            "plus accès à l'imprimante ni au serveur ; Internet fonctionne parfois. Le document 1 est relevé sur un portable touché."
        ),
        documents=(_console("Document 1 — configuration IP (capture fictive)", *wifi_ipconfig_lines(X04_HOST)),),
        instructions=("Donne la piste, la cause et la correction.",),
        criteria=(
            _c("Diagnostic", 1, f"Adresse 192.168.0.23, passerelle et serveur DHCP 192.168.0.1 : pas le réseau du cabinet → {_short(X04_DIAG)} ; deux serveurs DHCP : le « répéteur » est en mode routeur."),
            _c("Correction", 1, "Passer l'appareil en mode répéteur (ou point d'accès / pont) sans DHCP, même SSID et sécurité, ou le retirer ; ipconfig /release puis /renew ; vérifier 192.168.20.x et l'accès à l'imprimante."),
        ),
        correction=(
            f"Le portable a reçu 192.168.0.23 avec la passerelle et le serveur DHCP 192.168.0.1 : ce n'est pas le réseau du cabinet. Piste : {_short(X04_DIAG)}. L'appareil branché est en mode routeur : il crée son propre réseau et son propre DHCP, et les portables qui s'y associent sont coupés des équipements du cabinet.",
            "On le passe en mode répéteur ou point d'accès (pont), DHCP désactivé, ou on le retire ; une seule source DHCP par réseau. Sur les portables : ipconfig /release puis /renew, adresse en 192.168.20.x, test d'impression.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Estimer la couverture d'un bureau éloigné",
        question_type="short_answer",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            f"Le bureau du comptable d'une PME se trouve à {X05_DIST} m du point d'accès, derrière deux murs de briques. "
            "Formule du cours : signal reçu = 20 dBm − affaiblissement en espace libre − obstacles. Espace libre à "
            f"{X05_DIST} m : environ {fr(X05_FSPL[BAND_24])} dB en 2,4 GHz et {fr(X05_FSPL[BAND_5])} dB en 5 GHz. Un mur "
            f"de briques : 6 dB en 2,4 GHz, 10 dB en 5 GHz. Objectif : {TARGET_DBM} dBm ou mieux."
        ),
        instructions=("Calcule le signal estimé dans les deux bandes et conclus.",),
        criteria=(
            _c("Calculs", 1, f"2,4 GHz : 20 − {fr(X05_FSPL[BAND_24])} − {X05_LOSS[BAND_24]} ≈ {X05_24} dBm ; 5 GHz : 20 − {fr(X05_FSPL[BAND_5])} − {X05_LOSS[BAND_5]} ≈ {X05_5} dBm."),
            _c("Conclusion", 1, f"2,4 GHz {signal_verdict(X05_24)}, 5 GHz {signal_verdict(X05_5)} (objectif {TARGET_DBM} dBm non atteint en 5 GHz) : le bureau utilisera surtout le 2,4 GHz ; mesure sur place pour confirmer ; point d'accès plus proche si le débit du 5 GHz est nécessaire."),
        ),
        correction=(
            f"2,4 GHz : 20 − {fr(X05_FSPL[BAND_24])} − (6 + 6) ≈ {X05_24} dBm, {signal_verdict(X05_24)}. 5 GHz : 20 − {fr(X05_FSPL[BAND_5])} − (10 + 10) ≈ {X05_5} dBm, {signal_verdict(X05_5)}.",
            "Le 5 GHz perd plus en espace libre et dans les murs : il n'atteint pas l'objectif. Le bureau fonctionnera en 2,4 GHz ; si l'on veut le débit du 5 GHz, il faut un point d'accès plus proche. Ce calcul est une estimation : on confirme par une mesure.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Cinq barres mais une connexion lente",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            "Dans une maison médicale, le répéteur (une radio, 2,4 GHz) est branché dans le cabinet du fond, à côté "
            "du PC du kinésithérapeute. Le PC affiche un signal excellent mais les dossiers en ligne mettent "
            "longtemps à s'ouvrir. Le document 1 reprend la page d'état du répéteur."
        ),
        documents=(_table(
            "Document 1 — Page d'état du répéteur",
            ("Information", "Valeur"),
            ("Signal reçu du point d'accès", f"{X06_UPLINK} dBm"),
            ("Clients associés", f"1 (PC-KINE, {X06_CLIENT} dBm)"),
            ("Mode", "répéteur, même SSID"),
        ),),
        instructions=("Explique le problème avec les valeurs, estime le débit utile et propose une correction.",),
        criteria=(
            _c("Explication", 1, f"Le PC reçoit bien le répéteur ({X06_CLIENT} dBm) mais le répéteur reçoit mal le point d'accès ({X06_UPLINK} dBm, {signal_verdict(X06_UPLINK)}) → {_short(X06_DIAG)} ; débit ≈ {fr(X06_MBPS)} Mb/s (liaison {link_rate(X06_UPLINK)} Mb/s, divisée par deux, moitié utile)."),
            _c("Correction", 1, f"Déplacer le répéteur à mi-chemin, là où il reçoit {TARGET_DBM} dBm ou mieux ; mieux : point d'accès câblé ; mesure après."),
        ),
        correction=(
            f"Le signal excellent du PC ({X06_CLIENT} dBm) ne concerne que son lien avec le répéteur. Le répéteur, lui, reçoit le point d'accès à {X06_UPLINK} dBm ({signal_verdict(X06_UPLINK)}) : liaison à environ {link_rate(X06_UPLINK)} Mb/s, divisée par deux (une radio), soit environ {fr(X06_MBPS)} Mb/s utiles. Piste : {_short(X06_DIAG)}.",
            f"On rapproche le répéteur du point d'accès, là où il reçoit encore {TARGET_DBM} dBm ou mieux, à peu près à mi-chemin ; mieux encore, un point d'accès câblé dans le couloir. On mesure de nouveau le signal du répéteur et le débit.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Personnel ou Entreprise pour quarante-cinq employés ?",
        question_type="long_answer",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Une entreprise de nettoyage de 45 employés, avec beaucoup d'arrivées et de départs, utilise une seule clé "
            "WPA2-Personnel connue de tous, écrite sur un tableau. Un ancien employé a été vu connecté depuis le "
            "parking. L'entreprise dispose d'un serveur Windows avec annuaire."
        ),
        instructions=("Compare WPA2/WPA3-Personnel et Entreprise pour ce cas et recommande une solution argumentée.",),
        criteria=(
            _c("Comparaison", 1, "Personnel : une clé partagée, à changer partout à chaque départ ; Entreprise (802.1X/RADIUS) : un identifiant par personne, désactivé au départ, traçable."),
            _c("Recommandation", 1, "WPA2/WPA3-Entreprise avec RADIUS (NPS) lié à l'annuaire ; en attendant, changer la clé immédiatement ; réseau invités séparé ; clé jamais affichée."),
        ),
        correction=(
            "En mode Personnel, tout le monde partage la même clé : à chaque départ, il faudrait la changer et la redonner aux 45 employés ; sinon les anciens restent connectés, comme ici. En mode Entreprise (802.1X), chaque personne se connecte avec son propre identifiant, vérifié par un serveur RADIUS : on désactive le compte au départ, et les connexions sont tracées.",
            "Recommandation : WPA2/WPA3-Entreprise avec un serveur RADIUS (rôle NPS du serveur Windows) relié à l'annuaire. Immédiatement : changer la clé actuelle et l'effacer du tableau. Les visiteurs vont sur un réseau invités séparé.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Configurer le Wi-Fi des clients d'un café",
        question_type="long_answer",
        requirement_ids=R_WIFI,
        kind=KIND_CONFIG,
        context=(
            "Un café-librairie veut offrir le Wi-Fi à ses clients. Sur le même point d'accès, la caisse enregistreuse "
            "et le PC de gestion utilisent déjà le réseau du personnel. Le gérant craint qu'un client « pirate la "
            "caisse » ou que deux clients se voient entre eux."
        ),
        instructions=("Décris les réglages du réseau invités et explique comment chacun répond aux craintes du gérant.",),
        criteria=(
            _c("Réglages", 1, "SSID invités distinct, VLAN ou réseau séparé (autre plage, DHCP propre), isolation des clients, accès au réseau du personnel bloqué, clé distincte changée régulièrement ou portail, limite de débit éventuelle."),
            _c("Justification", 1, "Réseau séparé + blocage → aucun accès à la caisse ; isolation des clients → les clients ne se voient pas ; clé distincte → la clé du personnel n'est jamais donnée."),
        ),
        correction=(
            "On crée un SSID invités distinct, placé dans un réseau séparé (VLAN, plage d'adresses et DHCP propres) dont l'accès au réseau du personnel est bloqué : la caisse et le PC de gestion sont injoignables. On active l'isolation des clients : deux appareils invités ne peuvent pas communiquer entre eux.",
            "La clé invités est distincte de celle du personnel et changée régulièrement (ou un portail d'accueil) ; une limite de débit évite qu'un client sature la connexion. Le réseau du personnel reste en WPA2/WPA3 avec sa propre clé, jamais affichée.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Coupures en cuisine à l'heure du service",
        question_type="document_analysis",
        requirement_ids=R_ACCESS,
        kind=KIND_DIAG,
        context=(
            "Dans un restaurant, les tablettes de commande (2,4 GHz seulement) perdent la connexion au moment du "
            "service, surtout près du four à micro-ondes. Le point d'accès RESTO-CUISINE est réglé sur le canal 3. Le "
            "document 1 est relevé depuis un portable Linux en cuisine (SIGNAL = qualité en %, plus c'est haut plus "
            "c'est fort)."
        ),
        documents=(_console("Document 1 — réseaux visibles depuis la cuisine (capture fictive)", *X09_LINES),),
        instructions=("Identifie les causes d'interférence et propose les réglages corrigés.",),
        criteria=(
            _c("Causes", 1, "Canal 3 chevauche Hotel-Clients (canal 1, 70 %) et Bureau-Etage (canal 6, 58 %) ; le micro-ondes émet aussi vers 2,45 GHz."),
            _c("Réglages", 1, f"Canal {X09_BEST} (Taxi-Wifi canal 13 très faible) en 20 MHz ; point d'accès éloigné du micro-ondes ; tablettes 2,4 GHz seulement, donc pas de passage en 5 GHz pour elles ; mesure pendant le service."),
        ),
        correction=(
            "Le canal 3 n'est pas un des canaux sans chevauchement : il est gêné à la fois par Hotel-Clients (canal 1, fort) et Bureau-Etage (canal 6, fort). Le four à micro-ondes rayonne autour de 2,45 GHz quand il fonctionne : d'où les coupures « au moment du service ».",
            f"On passe RESTO-CUISINE sur le canal {X09_BEST} en 20 MHz : seul Taxi-Wifi (canal 13, 18 %) est proche, trop faible pour gêner. On éloigne le point d'accès du micro-ondes. Les tablettes ne gérant que le 2,4 GHz, le 5 GHz ne les aide pas ; on vérifie pendant un service.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Rapport : le point d'accès est revenu aux réglages d'usine",
        question_type="long_answer",
        requirement_ids=R_WIFI,
        kind=KIND_DIAG,
        context=(
            "Après une mise à jour du micrologiciel lancée par le gérant d'une agence, plus aucun poste ne voit le réseau "
            "AGENCE-PRO. Sur place, tu constates qu'un réseau ouvert « AP-SETUP-4F2A » est apparu : le point d'accès est "
            "revenu aux réglages d'usine. Tu avais sauvegardé sa configuration lors de l'installation."
        ),
        instructions=("Rédige le compte rendu d'intervention : constat, cause, actions, vérifications et conseil.",),
        criteria=(
            _c("Constat et cause", 0.5, "AGENCE-PRO absent, réseau ouvert d'usine visible ; mise à jour → réinitialisation."),
            _c("Actions", 1, "Connexion par câble ; mot de passe d'administration changé ; restauration de la configuration sauvegardée (ou ressaisie : SSID, WPA2/WPA3, clé, canaux, invités) ; réseau ouvert supprimé ; WPS désactivé."),
            _c("Vérification et conseil", 0.5, "Postes reconnectés sans ressaisie, adresse et Internet OK ; conseil : mises à jour par le technicien, sauvegarde de configuration après chaque modification."),
        ),
        correction=(
            "Constat : AGENCE-PRO n'est plus émis ; un réseau ouvert AP-SETUP-4F2A est visible. Cause : la mise à jour a réinitialisé le point d'accès. Danger immédiat : un réseau ouvert, administrable avec le mot de passe d'usine, est accessible à tous.",
            "Actions : connexion par câble, mot de passe d'administration changé, restauration de la configuration sauvegardée (SSID AGENCE-PRO, WPA2/WPA3, clé, canaux, réseau invités), WPS désactivé. Vérifications : les postes se reconnectent seuls (même SSID et clé), adresse correcte, Internet. Conseil : mises à jour faites par le technicien, nouvelle sauvegarde de configuration après chaque changement.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, schémas, relevés, diagnostics et choix de configuration demandés
    par le ticket."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
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
            errors.append(f"{item.key} : l'exigence AP-33 doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue au mini-examen.")
    if len(PRACTICE_ITEMS) < 18 or len(EXAM_ITEMS) != 10:
        errors.append("Ticket #224 : au moins 18 exercices et un mini-examen de 10 questions.")
    if sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) < 5:
        errors.append("Ticket #224 : au moins 5 exercices sur relevés ou captures.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_DIAG) < 5:
        errors.append("Ticket #224 : au moins 5 diagnostics.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_CONFIG) < 4:
        errors.append("Ticket #224 : au moins 4 choix de configuration.")
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 4:
        errors.append("Ticket #224 : au moins 4 schémas à compléter.")
    expected = {"E12": W_SIGNAL, "E13": W_IP, "E14": W_INTERNET, "E15": W_KEY, "E16": W_INVISIBLE,
                "X03": W_INVISIBLE, "X04": W_IP, "X06": W_REPEATER}
    found = {"E12": E12_DIAG, "E13": E13_DIAG, "E14": E14_DIAG, "E15": E15_DIAG, "E16": E16_DIAG,
             "X03": X03_DIAG, "X04": X04_DIAG, "X06": X06_DIAG}
    if found != expected:
        errors.append("Diagnostics des relevés inattendus.")
    if {wifi_diagnosis(first_failure(k)) for _t, k in E05_CASES} != set(WIFI_DIAGNOSES) or W_CHANNEL not in WIFI_DIAGNOSES:
        errors.append("E05 : toutes les pistes doivent être utilisées.")
    if set(E04_CORRECT) != {0, 1, 2} or set(E06_CORRECT) != {0, 1, 2} or set(E18_CORRECT) != {0, 1}:
        errors.append("E04/E06/E18 : catégories inutilisées.")
    if SEC_VERDICTS != (SEC_REFUSE, SEC_MIN, SEC_BEST) or BANDS != (BAND_24, BAND_5, BAND_6):
        errors.append("Catégories de sécurité ou de bande inattendues.")
    if (E11_BEST, X01_BEST, X09_BEST, NEIGHBORS_BEST) != (1, 11, 11, 11):
        errors.append("Canaux conseillés inattendus.")
    if len(E17_ISSUES) != 9 or audit_config(E17_FIXED):
        errors.append("E17 : audit de configuration inattendu.")
    if (signal_verdict(X05_24), signal_verdict(X05_5)) != ("excellent", "faible"):
        errors.append("X05 : estimation de couverture inattendue.")
    if REPEATER_GOOD.mbps <= REPEATER_BAD.mbps or X06_MBPS >= REPEATER_GOOD.mbps:
        errors.append("Débits derrière le répéteur incohérents.")
    return errors

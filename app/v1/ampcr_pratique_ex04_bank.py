"""EX04 « Examen blanc écrit — réseau, configuration et dépannage » — les 10 questions notées
/100 (ticket #233).

Épreuve autonome du module 4 (PR18 → PR25) : 10 questions de 10 points, **réponses libres**,
dans la réserve `exam` uniquement (`ampcr-pratique-ex04:exam`) — pas d'exercices
d'entraînement propres à EX04 : on s'entraîne dans les cours PR18 → PR25. Organisation :

- partie 1 (sans dossier) : plan d'un réseau — topologie, couches, domaines, trame, NetBEUI
  (X01) ; calculs IPv4/CIDR et identification d'adresses MAC et IP (X02) ;
- **dossier A** (cabinet de kinésithérapie « Kiné Sambre ») : connexion directe de deux PC
  (X03), plan d'adressage d'un mini-réseau de 5 postes et d'une imprimante (X04) ;
- **dossier B** (agence immobilière « Immo Meuse ») : panne DNS sur un poste qui a pourtant la
  connectivité IP (X05), route par défaut manquante et étendue DHCP épuisée (X06), panne
  Internet de toute l'agence et rapport d'intervention (X07) ;
- **dossier C** (bureau d'architectes « Atelier Linéa ») : Wi-Fi — fiche du point d'accès,
  canal, répéteur (X08) ; partages et permissions (X09) ; imprimante et accès au partage
  après un changement de box (X10).

Chaque question reprend les documents du dossier dont elle a besoin : elle se résout seule,
dans n'importe quel ordre. Valeurs et verdicts viennent de `app.v1.ampcr_pratique_ex04_figures`
(mêmes règles que les cours). Situations, adresses et mesures **fictives** ; aucune question
n'est présentée comme officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex04_figures import (
    AG_BOX_IP,
    AG_LEASES,
    AG_NAS_IP,
    AG_OLD_DNS,
    AG_POOL,
    AG_POOL_NEW,
    AG_POOL_NEW_SIZE,
    AG_POOL_SIZE,
    AG_SRV_IP,
    AP_DIRECT_DBM,
    AP_DIRECT_MBPS,
    APIPA_IPCONFIG,
    BOX_STATUS,
    CAB_BOX_IP,
    CAB_ERRORS,
    CAB_FIXED,
    CAB_HOSTS,
    CAB_POOL,
    CAB_SWITCH_PORTS,
    CABINET_FIGURE,
    CABINET_FIGURE_FILE,
    CALC_FACTS,
    CALC_HOSTS_NEEDED,
    CALC_ROWS,
    CALC_SMALLEST_PREFIX,
    DHCP_LOG,
    DIRECT_A,
    DIRECT_B_BAD,
    DIRECT_B_OK,
    DIRECT_IPCONFIG_A,
    DIRECT_IPCONFIG_B,
    DIRECT_PING_1,
    DIRECT_PING_2,
    DIRECT_SHARE_UNC,
    DNS_IPCONFIG,
    DNS_NSLOOKUP_OLD,
    DNS_NSLOOKUP_SRV,
    DNS_PING_GW,
    DNS_PING_IP,
    DNS_PING_NAME,
    KIND_FACTS,
    KIND_ROWS,
    LIN_ACCOUNTS,
    LIN_AP,
    LIN_AP_DEFECTS,
    LIN_BEST_CHANNEL,
    LIN_BOX_IP,
    LIN_MATRIX,
    LIN_MATRIX_FIXED,
    LIN_NEIGHBORS,
    LIN_PATHS,
    LIN_POOL,
    LIN_SCAN,
    LIN_SRV_IP,
    LIN_SRV_NAME,
    LINK_RATE_ROWS,
    LINUX_ADDR,
    LINUX_PINGS,
    LINUX_ROUTE,
    LINUX_ROUTE_FIXED,
    MAC_FACTS,
    MAC_ROWS,
    OUTAGE_NAS,
    OUTAGE_PING_GW,
    OUTAGE_PING_WEB,
    OUTAGE_TRACERT,
    PC3_TO_PC4_HOP,
    PC3_TO_PC6_DST_MAC,
    PLAN_ADDRESSES,
    PLAN_BROADCASTS,
    PLAN_COLLISIONS,
    PLAN_FIGURE,
    PLAN_FIGURE_FILE,
    PLAN_PC4,
    PLAN_PC6,
    PRINTER_FIXED_IP,
    PRINTER_NEW_IP,
    PRINTER_PING,
    PRINTER_PORT_IP,
    PRINTER_QUEUE,
    R1_LAN_A,
    REP_MID_CLIENT,
    REP_MID_MBPS,
    REP_MID_UPLINK,
    REP_NOW_CLIENT,
    REP_NOW_MBPS,
    REP_NOW_UPLINK,
    SECR_COMPTA,
    SECR_COMPTA_LOCAL,
    SHARE_NET_USE,
    SHARE_PING,
    SHARE_PORT,
    SHARE_UNC,
    WEB_IP,
    WEB_NAME,
    WIFI_FIGURE,
    WIFI_FIGURE_FILE,
    ntfs_rows,
    share_rows,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item
from app.v1.ampcr_pratique_pr20_figures import subnet_facts
from app.v1.ampcr_pratique_pr25_figures import dbm_from_pct, link_rate, quality_pct

EX04_CODE = "EX04"
EXAM_TOTAL_POINTS = 100
POINTS_PER_QUESTION = 10
KIND_DOC = "analyse de document"

# Partie ou dossier de chaque question (sujet imprimable, barème global).
PART_1 = "Partie 1 — Plan de réseau et adressage"
DOSSIER_A = "Dossier A — Cabinet de kinésithérapie « Kiné Sambre »"
DOSSIER_B = "Dossier B — Agence immobilière « Immo Meuse »"
DOSSIER_C = "Dossier C — Bureau d'architectes « Atelier Linéa »"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


def _fact_text(ref: str) -> str:
    f = CALC_FACTS[ref]
    usable = f"{f.usable:,}".replace(",", " ")
    return (f"{ref}) /{f.prefix}, masque {f.mask} ; réseau {f.network} ; diffusion {f.broadcast} ; "
            f"hôtes {f.first_host} à {f.last_host} ; {usable} hôtes")


def _calc_all() -> str:
    return " ; ".join(_fact_text(ref) for ref, _ip, _g in CALC_ROWS)


# Valeurs du document 4, mélangées (MAC et IPv4) : (repère, valeur, nature attendue).
_IDS: tuple[tuple[str, str], ...] = (
    MAC_ROWS[0], KIND_ROWS[0], MAC_ROWS[1], KIND_ROWS[1], MAC_ROWS[2], KIND_ROWS[2], KIND_ROWS[3],
)
_ID_LABELS = {old: f"V{n}" for n, (old, _v) in enumerate(_IDS, start=1)}
_V = {_ID_LABELS[ref]: value for ref, value in _IDS}


def _mac_text(ref: str) -> str:
    group, local = MAC_FACTS[ref]
    if group:
        return f"{_ID_LABELS[ref]} adresse MAC de groupe (multicast, bit I/G à 1)"
    origin = "administrée localement (bit U/L à 1)" if local else "attribuée par le fabricant (bit U/L à 0)"
    return f"{_ID_LABELS[ref]} adresse MAC unicast (bit I/G à 0), {origin}"


def _kind_text(ref: str) -> str:
    kind = KIND_FACTS[ref]
    return f"{_ID_LABELS[ref]} ({_V[_ID_LABELS[ref]]}) adresse IPv4 {kind[0].lower()}{kind[1:]}"


_D_AS_26 = subnet_facts(CALC_ROWS[3][1], 26)
_PC_SCAN = {n.ssid: quality_pct(n.dbm) for n in LIN_NEIGHBORS}
_CAB_FIX_ROWS = " ; ".join(f"{h.name} {h.ip}/{h.prefix}" + (f", passerelle et DNS {h.gateway}" if h.gateway else "")
                           + (" (DHCP)" if h.dhcp else "") for h in CAB_FIXED[1:])
_CAB_ERR = " ".join(CAB_ERRORS)


def _cell(level: str) -> str:
    return level.lower()


def _matrix_text(matrix: dict[str, dict[str, str]]) -> str:
    return " ; ".join(
        f"{a.person.split(' (')[0]} : " + ", ".join(f"{p.split(chr(92))[-1]} {_cell(v)}" for p, v in matrix[a.login].items())
        for a in LIN_ACCOUNTS
    )


_DEFECTS = " ; ".join(f"{param} → {fix}" for param, fix in LIN_AP_DEFECTS)

# --- Documents ---------------------------------------------------------------------------------

_P1_PLAN = _schema("Document 1 — Plan du réseau de l'entreprise (schéma fictif)", PLAN_FIGURE.alt, PLAN_FIGURE_FILE)
_P1_ADDR = _table(
    "Document 2 — Adresses relevées sur le plan du document 1",
    ("Interface", "Adresse IPv4 / préfixe", "Adresse MAC"),
    *((name, f"{ip}/24", mac) for name, ip, mac in PLAN_ADDRESSES),
)
_P1_CALC = _table(
    "Document 3 — Configurations à analyser",
    ("Repère", "Adresse IPv4", "Préfixe ou masque"),
    *CALC_ROWS,
)
_P1_IDS = _table(
    "Document 4 — Valeurs relevées dans des fiches de postes",
    ("Repère", "Valeur"),
    *((_ID_LABELS[ref], value) for ref, value in _IDS),
)

_A_REQUEST = _table(
    "Dossier A, document A1 — Fiche du cabinet",
    ("Rubrique", "Contenu"),
    ("Client", "Cabinet de kinésithérapie Kiné Sambre (3 kinés et une secrétaire)"),
    ("Étape 1 (cette semaine)", ("Copier le dossier Agenda du poste d'accueil sur le portable du kiné, par un seul câble, "
                                 "sans box ni switch")),
    ("Cartes réseau", ("PC-ACCUEIL : carte 10/100 Mb/s ancienne, sans Auto MDI-X ; PORT-KINE : carte 1 Gb/s avec "
                       "Auto MDI-X")),
    ("Étape 2 (le mois prochain)", (f"Mini-réseau : box du fournisseur, switch {CAB_SWITCH_PORTS} ports 1 Gb/s, 5 postes "
                                    "(accueil, 3 cabinets, portable) et une imprimante réseau")),
    ("Conventions d'adressage", (f"Réseau 192.168.10.0/24 ; box en {CAB_BOX_IP} (passerelle, DNS, DHCP) ; étendue DHCP "
                                 f"{CAB_POOL[0]} à {CAB_POOL[1]} ; adresses fixes : postes de .1 à .19, imprimantes "
                                 "de .20 à .49")),
)
_A_IPCONFIG = _console(
    "Dossier A, document A2 — ipconfig /all des deux postes, étape 1 (relevés fictifs)",
    f"Sur {DIRECT_A.name} :", *DIRECT_IPCONFIG_A, "", f"Sur {DIRECT_B_BAD.name} :", *DIRECT_IPCONFIG_B,
)
_A_PINGS = _console(
    "Dossier A, document A3 — Pings lancés depuis PORT-KINE (relevés fictifs)",
    "Relevé 1, avant toute modification :", *DIRECT_PING_1, "",
    "Relevé 2, après ta correction du portable :", *DIRECT_PING_2,
)
_A_PLAN = _schema(
    "Dossier A, document A4 — Mini-réseau du cabinet, configurations relevées (schéma fictif)",
    CABINET_FIGURE.alt,
    CABINET_FIGURE_FILE,
)

_B_REQUEST = _table(
    "Dossier B, document B1 — Fiche du réseau de l'agence",
    ("Rubrique", "Contenu"),
    ("Client", "Agence immobilière Immo Meuse (9 personnes) ; gérant : M. Collard"),
    ("Réseau", f"192.168.50.0/24 ; box en {AG_BOX_IP} (passerelle, NAT, pare-feu, ligne VDSL)"),
    ("Serveur SRV-01", (f"{AG_SRV_IP}, Linux : serveur DHCP et DNS du réseau (nom de domaine interne immo.lan), "
                        "relaie les autres noms vers le DNS du fournisseur")),
    ("Étendue DHCP de SRV-01", (f"{AG_POOL[0]} à {AG_POOL[1]}, baux de 7 jours ; ce matin : {AG_LEASES} baux actifs "
                                "(portables, smartphones, visiteurs de la semaine)")),
    ("Adresses fixes", f"box .1, SRV-01 .5, NAS .10 ({AG_NAS_IP}), postes fixes de .20 à .49"),
    ("Historique", f"L'ancien serveur DNS ({AG_OLD_DNS}) a été retiré le 1er octobre ; SRV-01 l'a remplacé"),
)
_B_IPCONFIG = _console("Dossier B, document B2 — ipconfig /all sur PC-ACCUEIL (relevé fictif)", *DNS_IPCONFIG)
_B_PINGS = _console(
    "Dossier B, document B3 — Pings sur PC-ACCUEIL (relevés fictifs)",
    *DNS_PING_GW, "", *DNS_PING_IP, "", *DNS_PING_NAME,
)
_B_NSLOOKUP = _console(
    "Dossier B, document B4 — nslookup sur PC-ACCUEIL (relevés fictifs)",
    *DNS_NSLOOKUP_OLD, "", *DNS_NSLOOKUP_SRV,
)
_B_LINUX = _console(
    "Dossier B, document B5 — Poste Linux PC-COMPTA (relevés fictifs)",
    *LINUX_ADDR, *LINUX_ROUTE, *LINUX_PINGS,
)
_B_APIPA = _console("Dossier B, document B6 — ipconfig /all sur le portable PORT-07 (relevé fictif)", *APIPA_IPCONFIG)
_B_DHCP = _console("Dossier B, document B7 — Journal du serveur DHCP SRV-01 (extrait fictif)", *DHCP_LOG)
_B_OUTAGE = _console(
    "Dossier B, document B8 — Relevés sur PC-ACCUEIL le lundi à 9 h 20 (fictifs)",
    *OUTAGE_PING_GW, "", *OUTAGE_PING_WEB, "", *OUTAGE_TRACERT, "", *OUTAGE_NAS,
)
_B_BOX = _table(
    "Dossier B, document B9 — Page d'état de la box, lundi 9 h 25 (fictive)",
    ("Élément", "État affiché"),
    *BOX_STATUS,
)

_C_REQUEST = _table(
    "Dossier C, document C1 — Fiche du bureau",
    ("Rubrique", "Contenu"),
    ("Client", "Atelier Linéa, bureau d'architectes (6 personnes) ; associée : Mme Vermeer"),
    ("Réseau", (f"192.168.30.0/24 ; box en {LIN_BOX_IP} (passerelle, DNS, DHCP {LIN_POOL[0]} à {LIN_POOL[1]}) ; "
                f"serveur de fichiers {LIN_SRV_NAME} en {LIN_SRV_IP} (Windows Server, domaine LINEA) ; imprimantes "
                "de .20 à .49")),
    ("Wi-Fi", "Un point d'accès à l'accueil ; un répéteur R1 ajouté par un employé dans le local d'archives"),
    ("Événement récent", "Jeudi, le fournisseur a remplacé la box (même réseau, mêmes réglages DHCP)"),
)
_C_AP = _table(
    "Dossier C, document C2 — Fiche de configuration actuelle du point d'accès",
    ("Réglage", "Valeur relevée"),
    ("SSID", f"{LIN_AP.ssid} (diffusion du SSID : masqué)"),
    ("Sécurité", "WPA — Personnel, chiffrement TKIP"),
    ("Clé", LIN_AP.passphrase),
    ("WPS", "activé (bouton et code PIN)"),
    ("Mot de passe d'administration", "admin (valeur d'usine)"),
    ("Micrologiciel", "version de 2021 ; 4 mises à jour de sécurité disponibles"),
    ("Bande 2,4 GHz", f"canal {LIN_AP.channel_24}, largeur {LIN_AP.width_24} MHz"),
    ("Réseau invités", "Linea-Invites, même réseau que les postes, isolation désactivée"),
)
_C_SCAN = _console("Dossier C, document C3 — Réseaux voisins relevés à l'accueil (extrait fictif)", *LIN_SCAN)
_C_PLAN = _schema(
    "Dossier C, document C4 — Plan du rez-de-chaussée et mesures du répéteur (schéma fictif)",
    WIFI_FIGURE.alt,
    WIFI_FIGURE_FILE,
)
_C_RATES = _table(
    "Dossier C, document C5 — Débit de liaison du portable selon le signal (fiche du fabricant, 2,4 GHz, 20 MHz)",
    ("Signal reçu", "Débit de liaison négocié"),
    *((label, f"{rate} Mb/s") for label, rate in LINK_RATE_ROWS),
    ("plus faible que −82 dBm", "pas de connexion utilisable"),
)
_C_SHARES = _table(
    f"Dossier C, document C6 — Partages de {LIN_SRV_NAME}",
    ("Partage", "Dossier", "Autorisations du partage"),
    *share_rows(),
)
_C_NTFS = _table(
    f"Dossier C, document C7 — Autorisations NTFS (onglet Sécurité) sur {LIN_SRV_NAME}",
    ("Dossier", "Entrées posées sur le dossier", "Héritage"),
    ("D:\\Partages", "Administrateurs : Contrôle total", "non (racine)"),
    *ntfs_rows(),
)
_C_NEEDS = _table(
    "Dossier C, document C8 — Comptes, groupes et besoins exprimés par l'associée",
    ("Compte", "Groupes", "Besoin"),
    ("Tom Lambert (tlambert), architecte", "Utilisateurs du domaine, G_Architectes",
     "modifier Projets ; aucun accès à Concours ni à Compta"),
    ("Nora Haddad (nhaddad), secrétariat et comptabilité", "Utilisateurs du domaine, G_Secretariat, G_Compta",
     "lire Projets ; aucun accès à Concours ; modifier Compta"),
    ("Eva Vermeer (evermeer), associée", "Utilisateurs du domaine, G_Architectes, G_Associes",
     "modifier Projets et Concours ; lire Compta"),
)
_C_PRINTER = _console(
    "Dossier C, document C9 — Traceur A1 : file d'attente et ping depuis PC-SECR (relevés fictifs)",
    *PRINTER_QUEUE, "", *PRINTER_PING,
)
_C_SHARE = _console(
    "Dossier C, document C10 — Lecteur P: sur le portable de Tom (relevés fictifs)",
    *SHARE_NET_USE, "", *SHARE_PING, "", *SHARE_PORT,
)

# =============================================================================================
# Les 10 questions (10 points chacune)
# =============================================================================================

_ARCH_ROWS = ", ".join(p.split(chr(92))[-1] for p in LIN_PATHS)

EXAM_ITEMS: tuple[PR06Item, ...] = (
    # ------------------------------------------------------------------ Partie 1
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Lire un plan de réseau : topologie, équipements, domaines et trames",
        question_type="document_analysis",
        requirement_ids=("AP-23", "AP-29", "AP-31"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Une PME te remet le plan de son réseau (document 1) et les adresses de quelques interfaces "
            "(document 2). Le responsable veut comprendre « ce que fait chaque boîte » avant d'ajouter des postes, et "
            "il utilise encore un vieux logiciel qui fonctionne en NetBEUI."
        ),
        documents=(_P1_PLAN, _P1_ADDR),
        instructions=(
            ("Nomme la topologie physique de ce réseau et ce qu'ajoute le hub ; dis quels postes perdent quelles "
             "communications si SW1 tombe en panne."),
            ("Pour R1, SW1 et le hub, donne la couche OSI (et la couche TCP/IP correspondante), ce que l'appareil lit "
             "pour décider, puis compte les domaines de collision et de diffusion du plan, en justifiant."),
            ("PC3 envoie un fichier à PC6, puis à PC4 : pour chaque envoi, donne l'adresse MAC de destination de la "
             "trame qui quitte PC3 et l'adresse IP de destination du paquet ; explique."),
            "PC3 peut-il ouvrir un partage NetBEUI de PC6 ? Justifie et indique ce qu'on utilise aujourd'hui.",
        ),
        criteria=(
            _c("Topologie et panne", 2, "Étoile étendue (hiérarchique) : chaque switch en étoile, reliés au routeur ; le hub est une étoile physique mais un support partagé (bus logique : tout signal est recopié sur tous ses ports). Si SW1 tombe : PC1 et PC2 sont totalement isolés ; PC3, PC4 et PC5 ne communiquent plus qu'entre eux (par le hub) ; PC6 et PC7 continuent entre eux mais perdent tout le réseau de SW1."),
            _c("Couches et domaines", 4, f"R1 : couche 3 réseau (Internet en TCP/IP), lit l'adresse IP, table de routage, sépare collisions et diffusions. SW1 : couche 2 liaison (accès réseau), lit l'adresse MAC (table MAC), un domaine de collision par port. Hub : couche 1 physique (accès réseau), recopie les bits sans rien lire, un seul domaine pour tous ses ports. Domaines de collision : {PLAN_COLLISIONS} (R1-SW1, R1-SW2, SW1-PC1, SW1-PC2, SW2-PC6, SW2-PC7, plus un seul domaine pour les 4 liaisons du hub). Domaines de diffusion : {PLAN_BROADCASTS} (un par interface du routeur : seul R1 arrête une diffusion)."),
            _c("Trames", 3, f"PC3 → PC6 : {PLAN_PC6[1]} n'est pas dans 192.168.1.0/24 → PC3 envoie à sa passerelle : MAC de destination {PC3_TO_PC6_DST_MAC} (R1 côté SW1, trouvée par ARP), IP de destination {PLAN_PC6[1]} (elle ne change pas) ; R1 refait une trame vers PC6 avec sa MAC côté SW2. PC3 → PC4 : même réseau → envoi direct : MAC de destination {PLAN_PC4[2]}, IP {PC3_TO_PC4_HOP} ; le hub recopie la trame aussi vers PC5, qui l'ignore."),
            _c("NetBEUI", 1, "Non : NetBEUI n'a pas d'adresse réseau (nom NetBIOS seul), il est non routable et ne traverse pas R1 ; il reste limité à un réseau local. Aujourd'hui : partage de fichiers SMB sur TCP/IP, routable."),
        ),
        correction=(
            "La topologie physique est une étoile étendue : R1 au centre, chaque switch en étoile avec ses postes. Le hub forme lui aussi une petite étoile, mais c'est un support partagé : il recopie chaque signal sur tous ses ports, comme un bus. Si SW1 tombe en panne, PC1 et PC2 sont isolés ; PC3, PC4 et PC5 se parlent encore à travers le hub mais ne joignent plus rien d'autre ; PC6 et PC7 fonctionnent entre eux mais perdent tout le côté SW1.",
            f"R1 travaille à la couche 3 (réseau ; Internet dans TCP/IP) : il lit l'adresse IP et choisit l'interface de sortie ; il sépare les domaines de collision et de diffusion. SW1 travaille à la couche 2 (liaison ; accès réseau) : il lit l'adresse MAC de destination et n'envoie la trame que sur le bon port ; chaque port est un domaine de collision. Le hub travaille à la couche 1 (physique) : il recopie les bits sur tous ses ports ; ses quatre liaisons forment un seul domaine de collision. Total : {PLAN_COLLISIONS} domaines de collision (six liaisons séparées par les switchs et le routeur, plus celui du hub) et {PLAN_BROADCASTS} domaines de diffusion, un par interface de R1.",
            f"Pour PC6 ({PLAN_PC6[1]}), PC3 compare avec son propre réseau 192.168.1.0/24 : la destination est ailleurs, il envoie donc la trame à sa passerelle {R1_LAN_A[1]} : MAC de destination {PC3_TO_PC6_DST_MAC}, IP de destination {PLAN_PC6[1]}. R1 retire la trame, lit l'IP et construit une nouvelle trame vers PC6. Pour PC4, même réseau : la trame part directement vers la MAC de PC4, {PLAN_PC4[2]}, avec l'IP {PLAN_PC4[1]} ; le hub la recopie aussi vers PC5, qui l'ignore.",
            "NetBEUI n'a pas d'adresse réseau : les postes sont désignés par un nom NetBIOS, le protocole n'est pas routable et ne franchit pas R1. PC3 ne verra donc pas un partage NetBEUI de PC6. Aujourd'hui on partage en SMB sur TCP/IP, qui traverse les routeurs.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Calculer des réseaux IPv4 et identifier des adresses MAC et IP",
        question_type="document_analysis",
        requirement_ids=("AP-30",),
        kind=KIND_DOC,
        context=(
            "Partie 1. Tu prépares des fiches de configuration pour plusieurs clients (document 3). Un collègue t'a "
            "aussi transmis des valeurs relevées dans des fiches de postes, sans préciser ce que c'est (document 4). "
            "La calculatrice est autorisée ; toute méthode juste est acceptée (binaire, taille de bloc…)."
        ),
        documents=(_P1_CALC, _P1_IDS),
        instructions=(
            ("Pour chaque ligne a à d du document 3, donne le préfixe et le masque, l'adresse du réseau, l'adresse de "
             "diffusion, la plage des adresses d'hôtes et le nombre d'hôtes ; détaille la méthode pour au moins une ligne."),
            ("Les postes a et d, configurés tous deux en /26, peuvent-ils communiquer directement, sans routeur ? "
             "Justifie par le calcul."),
            f"Un service doit accueillir {CALC_HOSTS_NEEDED} postes : quel est le plus petit bloc qui convient (préfixe, masque, nombre d'hôtes) ?",
            ("Pour chaque valeur du document 4, dis si c'est une adresse MAC ou une adresse IPv4 et comment tu le "
             "reconnais ; pour une MAC, unicast ou groupe, fabricant ou administrée localement (bit utilisé) ; pour "
             "une IPv4, son type."),
        ),
        criteria=(
            _c("Calculs a à d", 5, _calc_all() + ". Méthode : taille du bloc = 256 − octet significatif du masque ; réseau = multiple du bloc juste inférieur ; diffusion = réseau + bloc − 1 ; hôtes = 2^(32 − préfixe) − 2 (ou ET binaire adresse/masque). 1,25 point par ligne."),
            _c("Même réseau ?", 1.5, f"En /26, a est dans 192.168.40.64/26 (64 à 127) et d dans {_D_AS_26.cidr} ({_D_AS_26.network.split('.')[-1]} à {_D_AS_26.broadcast.split('.')[-1]}) : réseaux différents → pas de communication directe, il faut un routeur (passerelle)."),
            _c(f"Bloc pour {CALC_HOSTS_NEEDED} postes", 1, f"/{CALC_SMALLEST_PREFIX}, masque 255.255.255.192, 62 hôtes ; /27 n'offre que 30 hôtes."),
            _c("Identification", 2.5, "MAC : 48 bits, 6 octets en hexadécimal séparés par - ou : ; IPv4 : 4 nombres décimaux de 0 à 255. " + "; ".join(_mac_text(ref) for ref, _m in MAC_ROWS) + " (bit I/G = bit de poids faible du 1er octet ; bit U/L = le suivant : 3C = 00111100, DA = 11011010, 01 = 00000001). " + "; ".join(_kind_text(ref) for ref, _ip in KIND_ROWS) + " (172.16.0.0/12 va jusqu'à 172.31.255.255)."),
        ),
        correction=(
            f"{_calc_all()}. Méthode pour a : /26 → masque 255.255.255.192 ; bloc 256 − 192 = 64 ; 77 est entre 64 et 127 : réseau 192.168.40.64, diffusion 192.168.40.127, hôtes de .65 à .126, soit 2^6 − 2 = 62. Pour c, le masque 255.255.255.192 compte 26 bits à 1 : /26 ; 130 est entre 128 et 191.",
            f"Avec un masque /26, a est dans le réseau 192.168.40.64/26 (de .64 à .127) et d dans {_D_AS_26.cidr} (de .{_D_AS_26.network.split('.')[-1]} à .{_D_AS_26.broadcast.split('.')[-1]}). Ce sont deux réseaux différents : chacun enverra ses paquets à sa passerelle, il faut un routeur entre eux.",
            f"Pour {CALC_HOSTS_NEEDED} postes, un /27 n'offre que 30 hôtes ; le plus petit bloc qui convient est un /{CALC_SMALLEST_PREFIX}, masque 255.255.255.192, 62 hôtes.",
            "Une adresse MAC compte 6 octets en hexadécimal (ex. 3C-52-82-1A-2B-01), une IPv4 4 nombres décimaux. " + "; ".join(_mac_text(ref) for ref, _m in MAC_ROWS) + ". On lit le premier octet en binaire : bit de poids faible = I/G (1 = groupe), bit suivant = U/L (1 = administrée localement, comme une MAC aléatoire de Wi-Fi). " + "; ".join(_kind_text(ref) for ref, _ip in KIND_ROWS) + ".",
        ),
    ),
    # ------------------------------------------------------------------ Dossier A
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Relier deux PC en direct et interpréter les pings",
        question_type="document_analysis",
        requirement_ids=("AP-28", "AP-30"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Au cabinet Kiné Sambre (document A1), le kiné veut copier le dossier Agenda du poste "
            "d'accueil sur son portable cette semaine, sans box ni switch. Tu relies les deux postes, tu relèves leurs "
            "configurations (document A2), puis tu lances un ping depuis le portable (document A3, relevé 1). Tu "
            "corriges, puis tu relances (relevé 2)."
        ),
        documents=(_A_REQUEST, _A_IPCONFIG, _A_PINGS),
        instructions=(
            "Indique le câble à utiliser entre les deux postes et justifie ; dis lequel il aurait fallu si aucune des deux cartes ne faisait l'Auto MDI-X.",
            "Analyse les configurations (A2) et le relevé 1 (A3) : pourquoi le ping échoue-t-il, et qu'indique ce message ?",
            "Donne la configuration IPv4 complète à saisir sur le portable (adresse, masque, passerelle, DNS) et justifie chaque valeur.",
            "Interprète le relevé 2 et termine l'intervention jusqu'à la copie de l'agenda : réglage, chemin d'accès au dossier partagé, contrôles.",
        ),
        criteria=(
            _c("Câble", 2, "PORT-KINE fait l'Auto MDI-X : un cordon droit (ou croisé) fonctionne, il suffit qu'un des deux ports inverse émission et réception ; on prend un droit standard. Sans Auto MDI-X, deux cartes réseau (MDI) se relient par un câble croisé (T568A à un bout, T568B à l'autre : 1→3, 2→6)."),
            _c("Diagnostic du relevé 1", 3, f"PC-ACCUEIL : {DIRECT_A.ip}/24 → réseau 192.168.10.0/24 ; PORT-KINE : {DIRECT_B_BAD.ip}/24 → 192.168.1.0/24 : pas le même réseau. Pour le portable, {DIRECT_A.ip} n'est pas locale et il n'a aucune passerelle : aucune route, le paquet ne part pas → « Défaillance générale ». Le lien n'est pas en cause (adresse affichée, pas « Média déconnecté »)."),
            _c("Configuration du portable", 2, f"Adresse {DIRECT_B_OK.ip} (ou toute adresse libre de 192.168.10.2 à .254), masque 255.255.255.0 (identique à PC-ACCUEIL), passerelle vide (aucun routeur, inutile), DNS vide (aucun serveur ; on accède par l'adresse IP)."),
            _c("Relevé 2 et fin", 3, f"« Délai d'attente dépassé » : même réseau, la demande part, mais PC-ACCUEIL ne répond pas → son pare-feu bloque l'écho ICMP (réseau en profil Public). Passer la connexion en réseau privé ou autoriser la règle d'écho ICMPv4 du partage de fichiers ; reping : réponses. Partager Agenda (droits limités au compte prévu, lecture suffit), ouvrir {DIRECT_SHARE_UNC} avec un compte de PC-ACCUEIL, copier, ouvrir un fichier copié pour vérifier ; arrêter le partage temporaire."),
        ),
        correction=(
            "La carte de PORT-KINE fait l'Auto MDI-X : elle inverse elle-même émission et réception, un cordon droit standard suffit (un croisé marcherait aussi). Si aucune carte ne le faisait, il faudrait un câble croisé, car deux cartes réseau (MDI) émettent toutes deux sur 1-2 : le croisé relie 1→3, 2→6, 3→1, 6→2.",
            f"PC-ACCUEIL est en {DIRECT_A.ip}/24, donc dans 192.168.10.0/24 ; PORT-KINE est en {DIRECT_B_BAD.ip}/24, donc dans 192.168.1.0/24. Pour le portable, l'adresse {DIRECT_A.ip} est dans un autre réseau, et il n'a pas de passerelle : il ne sait pas où envoyer le paquet. « Défaillance générale » signifie que rien n'est émis. Le câble est bon : la carte a une adresse, elle n'affiche pas « Média déconnecté ».",
            f"Sur PORT-KINE : adresse {DIRECT_B_OK.ip}, masque 255.255.255.0, comme PC-ACCUEIL, pour être dans le même réseau ; passerelle vide, car il n'y a pas de routeur ; DNS vide, car il n'y a pas de serveur de noms : on utilise l'adresse IP.",
            f"Relevé 2 : « Délai d'attente de la demande dépassé » ; les deux postes sont maintenant dans le même réseau, la demande part, mais PC-ACCUEIL ne répond pas : son pare-feu bloque le ping, la connexion étant classée « réseau public ». Je passe le réseau en privé (ou j'autorise la règle d'écho ICMPv4) et je reping : réponses. Je partage le dossier Agenda en lecture pour le compte prévu, j'ouvre {DIRECT_SHARE_UNC} depuis le portable avec un compte de PC-ACCUEIL, je copie le dossier, j'ouvre un fichier copié pour vérifier, puis j'arrête le partage temporaire.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Contrôler et corriger le plan d'adressage d'un mini-réseau",
        question_type="document_analysis",
        requirement_ids=("AP-38", "AP-30", "AP-31"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Le mois suivant, le cabinet Kiné Sambre installe son mini-réseau (document A1). Une stagiaire "
            "a configuré les appareils et relevé leurs réglages (document A4). Plusieurs utilisateurs se plaignent : "
            "pas d'Internet au cabinet 1, impressions qui « se perdent », coupures aléatoires."
        ),
        documents=(_A_REQUEST, _A_PLAN),
        instructions=(
            "Explique le rôle de la box et celui du switch dans ce mini-réseau (couche, ce que fait chacun), et vérifie que le switch a assez de ports.",
            "Relève toutes les erreurs de configuration du document A4 ; pour chacune, donne la règle non respectée et la conséquence pour l'utilisateur.",
            "Propose un plan d'adressage corrigé pour tous les appareils, en respectant les conventions du cabinet.",
            "Rédige la procédure de validation du mini-réseau, dans l'ordre, avec les commandes et le résultat attendu.",
        ),
        criteria=(
            _c("Rôles et ports", 2, f"Box : routeur (couche 3) entre le réseau local et Internet (passerelle, NAT vers l'adresse publique, pare-feu), serveur DHCP et relais DNS. Switch : couche 2, apprend les MAC et relie les appareils du même réseau. Ports : {len(CAB_HOSTS) - 1} appareils + 1 liaison vers la box = {len(CAB_HOSTS)} ≤ {CAB_SWITCH_PORTS} ports (une réserve) ; câbles de 100 m au plus."),
            _c("Erreurs", 4, "1 point par erreur avec sa conséquence : " + _CAB_ERR + " Conséquences : cabinet 1 sans Internet (sa « passerelle » est un poste) ; cabinet 2 dans un /16 incohérent (diffusion 192.168.255.255, envoie en direct tout 192.168.x.x au lieu de passer par la box) ; cabinet 3 en conflit dès que la box attribue .150 ; imprimante et cabinet 1 en conflit d'adresse (coupures, impressions perdues)."),
            _c("Plan corrigé", 2, "Par exemple : " + _CAB_FIX_ROWS + ". Toute adresse fixe juste hors de l'étendue et dans les plages du cabinet est acceptée."),
            _c("Validation", 2, f"Voyants de lien sur chaque prise et port ; ipconfig /all sur chaque poste (adresse, masque /24, passerelle et DNS {CAB_BOX_IP}, aucun « Dupliqué ») ; ping {CAB_BOX_IP} ; ping entre postes et vers l'imprimante ; ping d'une adresse IP Internet puis d'un nom (nslookup) ; page de test imprimée depuis chaque poste ; plan d'adressage et étiquettes remis au cabinet."),
        ),
        correction=(
            f"La box est le routeur du cabinet (couche 3) : passerelle vers Internet, traduction des adresses (NAT), pare-feu, et elle distribue les adresses (DHCP) et relaie les noms (DNS). Le switch (couche 2) relie les appareils du réseau local et envoie chaque trame vers le port du destinataire grâce à sa table MAC. Il faut {len(CAB_HOSTS) - 1} ports pour les appareils et 1 vers la box, soit {len(CAB_HOSTS)} sur {CAB_SWITCH_PORTS} : il en reste un.",
            "Erreurs : " + _CAB_ERR + " Le cabinet 1 n'a pas Internet car sa passerelle est le poste d'accueil ; le masque /16 du cabinet 2 le met dans un réseau incohérent avec les autres ; l'adresse fixe du cabinet 3 sera distribuée un jour par la box à un autre appareil ; l'imprimante et le cabinet 1 ont la même adresse : l'un des deux perd le réseau, d'où les impressions perdues et les coupures.",
            "Plan corrigé (par exemple) : " + _CAB_FIX_ROWS + " ; la box reste en " + CAB_BOX_IP + " avec son étendue " + f"{CAB_POOL[0]} à {CAB_POOL[1]}.",
            f"Validation : contrôler les voyants de lien de chaque appareil et du switch ; sur chaque poste, ipconfig /all (adresse attendue, masque 255.255.255.0, passerelle et DNS {CAB_BOX_IP}, pas de « Dupliqué ») ; ping de la box, d'un autre poste et de l'imprimante ; ping d'une adresse IP Internet puis nslookup d'un nom ; imprimer une page de test depuis chaque poste ; remettre le plan d'adressage et étiqueter les câbles.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier B
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Distinguer une panne de connectivité IP d'une panne de résolution DNS",
        question_type="document_analysis",
        requirement_ids=("AP-32", "AP-37"),
        kind=KIND_DOC,
        context=(
            "Dossier B. À l'agence Immo Meuse (document B1), la secrétaire de l'accueil dit qu'« Internet ne marche "
            "plus » sur son poste depuis début octobre, alors que ses collègues naviguent normalement. Tu relèves la "
            "configuration du poste (document B2), puis tu fais des pings (document B3) et des requêtes nslookup "
            "(document B4)."
        ),
        documents=(_B_REQUEST, _B_IPCONFIG, _B_PINGS, _B_NSLOOKUP),
        instructions=(
            "Résume la configuration du poste (B2) et repère la valeur suspecte en la comparant à la fiche du réseau (B1).",
            "Interprète chaque relevé de B3 et de B4 : ce que chacun prouve ou exclut.",
            "Conclus : la connectivité IP est-elle en cause ? Explique la différence entre « pas de connectivité IP » et « pas de résolution de noms », et le test qui les distingue.",
            "Rédige la correction et les vérifications, dans l'ordre.",
        ),
        criteria=(
            _c("Configuration", 2, f"Adresse fixe 192.168.50.21/24 (hors de l'étendue), passerelle {AG_BOX_IP} (dans le réseau, juste), DNS {AG_OLD_DNS} : c'est l'ancien serveur, retiré le 1er octobre (B1) ; le DNS du réseau est SRV-01, {AG_SRV_IP}."),
            _c("Relevés", 3, f"Ping {AG_BOX_IP} : réponses → câble, carte, adresse, réseau local corrects. Ping {WEB_IP} : réponses (TTL 56) → passerelle, box et Internet fonctionnent. Ping {WEB_NAME} : « n'a pas pu trouver l'hôte » → le nom n'est pas traduit, rien n'est envoyé. nslookup (serveur {AG_OLD_DNS}) : délai expiré → le serveur DNS configuré ne répond pas. nslookup vers {AG_SRV_IP} : réponse {WEB_IP} → le DNS du réseau fonctionne (« ne faisant pas autorité » est normal pour un relais)."),
            _c("Conclusion", 2, "Connectivité IP intacte ; la panne est la résolution des noms, sur ce seul poste. Pas de connectivité : même une adresse IP ne répond pas (passerelle, box, ligne) ; pas de résolution : les adresses IP répondent, les noms non. Test : ping d'une adresse IP extérieure puis d'un nom (ou nslookup)."),
            _c("Correction et vérification", 3, f"Remplacer le DNS {AG_OLD_DNS} par {AG_SRV_IP} (ou repasser le poste en DHCP s'il n'a pas besoin d'une adresse fixe) ; ipconfig /flushdns ; contrôler ipconfig /all ; nslookup {WEB_NAME} sans préciser de serveur → réponse de {AG_SRV_IP} ; navigateur ; vérifier les autres postes fixes ; consigner. Ne toucher ni à la passerelle ni à la box."),
        ),
        correction=(
            f"Le poste a une adresse fixe, 192.168.50.21/24, hors de l'étendue DHCP, et sa passerelle {AG_BOX_IP} est la box : c'est juste. Son serveur DNS est {AG_OLD_DNS}, l'ancien serveur retiré le 1er octobre : c'est la valeur suspecte ; le DNS du réseau est maintenant SRV-01, {AG_SRV_IP}.",
            f"Le ping de la box répond : le câble, la carte, l'adresse et le réseau local fonctionnent. Le ping de l'adresse {WEB_IP} répond aussi : la passerelle, la box et Internet fonctionnent. Le ping de {WEB_NAME} échoue avant même d'envoyer : le nom n'est pas traduit en adresse. nslookup vers {AG_OLD_DNS} expire : ce serveur n'existe plus. nslookup vers {AG_SRV_IP} donne {WEB_IP} : le DNS du réseau fonctionne ; « Réponse ne faisant pas autorité » est normal, SRV-01 relaie la question.",
            "La connectivité IP n'est pas en cause : le poste joint Internet par adresse IP. Seule la résolution des noms échoue, à cause d'un mauvais serveur DNS. Quand la connectivité manque, même une adresse IP extérieure ne répond pas ; quand c'est le DNS, les adresses répondent mais pas les noms. Le test qui les distingue : ping d'une adresse IP extérieure, puis ping d'un nom ou nslookup.",
            f"Correction : dans les propriétés IPv4 du poste, remplacer le DNS {AG_OLD_DNS} par {AG_SRV_IP} (ou repasser en DHCP) ; ipconfig /flushdns ; vérifier avec ipconfig /all ; nslookup {WEB_NAME} doit répondre par {AG_SRV_IP} ; ouvrir un site ; vérifier que les autres postes à adresse fixe n'ont pas la même erreur ; noter l'intervention.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Diagnostiquer une route manquante et une étendue DHCP épuisée",
        question_type="document_analysis",
        requirement_ids=("AP-37", "AP-30", "AP-32"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Deux autres appels de l'agence Immo Meuse (document B1) : le comptable, sur son poste Linux "
            "PC-COMPTA installé la veille par un intérimaire, ouvre ses dossiers du NAS mais n'a pas Internet "
            "(document B5) ; une nouvelle agente, arrivée ce matin avec le portable PORT-07, n'a « aucun réseau » "
            "(documents B6 et B7)."
        ),
        documents=(_B_REQUEST, _B_LINUX, _B_APIPA, _B_DHCP),
        instructions=(
            "Poste PC-COMPTA (B5) : interprète ip addr, ip route et les deux pings ; donne la cause et la ligne qui manque dans la table de routage.",
            "Rédige la correction pour ce poste (réglage, commande ou écran) et ses vérifications.",
            "Portable PORT-07 (B6 et B7) : interprète l'adresse obtenue et le journal du serveur ; calcule la taille de l'étendue et explique la cause.",
            "Propose deux solutions durables pour PORT-07 (avec les valeurs), la vérification, et ce qu'il ne faut pas faire.",
        ),
        criteria=(
            _c("PC-COMPTA : diagnostic", 3, f"ip addr : 192.168.50.40/24, lien UP : adressage local correct. ip route : seule la route du réseau local, aucune route par défaut. Ping du NAS ({AG_NAS_IP}, local) : réponses. Ping de {WEB_IP} : « Network is unreachable » = aucune route (rien n'est émis, ce n'est pas un délai dépassé). Cause : passerelle non configurée ; ligne attendue : « default via {AG_BOX_IP} dev enp3s0 »."),
            _c("PC-COMPTA : correction", 2, f"Dans les paramètres réseau (NetworkManager), IPv4 manuel : passerelle {AG_BOX_IP}, DNS {AG_SRV_IP} (ou nmcli con mod … ipv4.gateway {AG_BOX_IP} puis réactiver la connexion) ; « ip route add default via {AG_BOX_IP} » seul est perdu au redémarrage. Vérifier ip route, ping {WEB_IP}, puis un nom."),
            _c("PORT-07 : diagnostic", 3, f"169.254.83.17/16 sans passerelle = adresse APIPA (lien local) : aucun bail DHCP. Le journal montre les DHCPDISCOVER du portable (même MAC) : le câble et le réseau fonctionnent, le serveur reçoit la demande mais répond « no address available ». Étendue {AG_POOL[0]} à {AG_POOL[1]} = {AG_POOL_SIZE} adresses, {AG_LEASES} baux actifs : étendue épuisée."),
            _c("PORT-07 : solutions", 2, f"Agrandir l'étendue (ex. {AG_POOL_NEW[0]} à {AG_POOL_NEW[1]} = {AG_POOL_NEW_SIZE} adresses, sans toucher aux adresses fixes) ; raccourcir les baux (ex. 1 jour) pour libérer les visiteurs ; éventuellement un réseau invités séparé. Vérifier : ipconfig /release puis /renew → adresse 192.168.50.1xx, DHCPACK dans le journal, ping passerelle et Internet. Ne pas donner au portable une adresse fixe prise dans l'étendue."),
        ),
        correction=(
            f"Sur PC-COMPTA, ip addr montre 192.168.50.40/24 et un lien actif : l'adresse est bonne. ip route ne contient que la route du réseau local : il n'y a pas de route par défaut. Le NAS, dans le même réseau, répond ; pour {WEB_IP}, Linux répond « Network is unreachable » : il ne sait pas où envoyer le paquet. L'intérimaire n'a pas saisi la passerelle ; il manque la ligne « default via {AG_BOX_IP} dev enp3s0 ».",
            f"Correction durable : dans les paramètres réseau (ou nmcli), ajouter la passerelle {AG_BOX_IP} et le DNS {AG_SRV_IP} à la configuration IPv4 manuelle, puis réactiver la connexion. ip route doit alors afficher « {LINUX_ROUTE_FIXED[1]} ». Vérifier par un ping de {WEB_IP}, puis d'un nom.",
            f"PORT-07 a pris 169.254.83.17 en masque /16, sans passerelle : c'est une adresse APIPA, que Windows se donne quand aucun serveur DHCP ne lui répond. Le journal de SRV-01 montre ses demandes (DHCPDISCOVER avec sa MAC) : la liaison est bonne, mais le serveur répond « no address available ». L'étendue va de {AG_POOL[0]} à {AG_POOL[1]}, soit {AG_POOL_SIZE} adresses, et {AG_LEASES} baux sont actifs : elle est pleine.",
            f"Solutions : agrandir l'étendue, par exemple de {AG_POOL_NEW[0]} à {AG_POOL_NEW[1]} ({AG_POOL_NEW_SIZE} adresses, sans chevaucher les adresses fixes), et raccourcir la durée des baux pour libérer les adresses des visiteurs (ou leur réserver un réseau invités). Vérifier : ipconfig /release puis ipconfig /renew sur PORT-07, adresse en 192.168.50.1xx, DHCPACK dans le journal, ping de la passerelle et d'Internet. Ne pas lui fixer à la main une adresse de l'étendue : elle serait redistribuée.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Localiser une panne Internet générale et rédiger le rapport d'intervention",
        question_type="document_analysis",
        requirement_ids=("AP-32", "AP-37"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Lundi à 9 h 15, plus aucun poste de l'agence Immo Meuse (document B1) n'accède à Internet ; "
            "le gérant, M. Collard, t'appelle et veut un rapport écrit. Sur place, tu fais des relevés sur PC-ACCUEIL "
            "(document B8) et tu consultes la page d'état de la box (document B9)."
        ),
        documents=(_B_REQUEST, _B_OUTAGE, _B_BOX),
        instructions=(
            "Interprète les relevés B8 et l'état de la box B9 : où se situe la panne ? Dis ce qui fonctionne, ce qui ne fonctionne pas, et pourquoi ce n'est ni le DNS ni les postes.",
            "Rédige les actions dans l'ordre, du plus simple au plus lourd, jusqu'au rétablissement : ce que tu fais toi-même, quand et comment tu contactes le fournisseur, ce qu'il ne faut pas faire.",
            "Rédige le rapport d'intervention remis au gérant (rubriques, constats chiffrés, actions, état final, recommandations).",
        ),
        criteria=(
            _c("Localisation", 4, f"Ping de la box {AG_BOX_IP} : 0 % de perte → réseau local, switch, câbles et postes fonctionnent. Ping de l'adresse {WEB_IP} : 100 % de perte → on teste une adresse IP, ce n'est donc pas le DNS. tracert : seul le saut 1 (la box) répond, rien au-delà. Lecteur S: du NAS connecté : réseau local intact. Box : VDSL non synchronisée, adresse publique 0.0.0.0, voyant Internet rouge depuis 9 h 05 → la liaison vers le fournisseur est coupée (ligne, câble ou filtre de ligne, ou panne du fournisseur). Tous les postes touchés : pas un poste."),
            _c("Actions ordonnées", 3, "Contrôler le câble de ligne (prise murale, filtre éventuel, câble de la box) et les voyants ; redémarrer la box une seule fois et attendre la synchronisation ; essayer un autre câble de ligne ; consulter la page de pannes du fournisseur ; appeler son support avec le numéro client, l'heure de début (9 h 05), l'état « non synchronisée » et les tests faits ; noter le numéro d'incident ; en attendant, partage de connexion 4G pour un poste urgent. Ne pas réinitialiser la box en usine (perte de la configuration), ne pas modifier les postes ni le DNS."),
            _c("Rapport", 3, "Rubriques : client, date et heures, demandeur, symptôme ; constats chiffrés (0 % / 100 % de perte, tracert arrêté au saut 1, VDSL non synchronisée, IP publique 0.0.0.0, NAS accessible) ; diagnostic (coupure de la liaison du fournisseur, réseau local sain) ; actions et résultats horodatés ; état final (rétabli à telle heure, ou en attente du fournisseur, n° d'incident) ; recommandations (connexion de secours 4G, coordonnées du support affichées). Style factuel, phrases complètes."),
        ),
        correction=(
            f"Le ping de la box répond sans perte : le réseau local, le switch, les câbles et les postes fonctionnent, comme le lecteur S: du NAS qui se connecte. Le ping de l'adresse IP {WEB_IP} échoue à 100 % : le DNS n'est pas en cause, puisqu'on n'utilise aucun nom. tracert s'arrête après la box. La box confirme : ligne VDSL non synchronisée depuis 9 h 05, adresse publique 0.0.0.0. La panne est entre la box et le fournisseur : ligne, câble de ligne ou panne chez l'opérateur ; elle touche tous les postes, donc aucun poste n'est en cause.",
            "Actions : contrôler le câble de ligne, la prise murale et un éventuel filtre, puis les voyants ; redémarrer la box une fois et attendre la synchronisation ; essayer un autre câble de ligne ; consulter l'état des pannes du fournisseur ; appeler son support en donnant le numéro client, l'heure de début, l'état « non synchronisée » et les tests faits, et noter le numéro d'incident ; proposer un partage de connexion 4G pour un poste urgent. Je ne réinitialise pas la box en usine et je ne modifie ni les postes ni le DNS.",
            "Rapport : Immo Meuse, lundi, intervention demandée par M. Collard à 9 h 15. Symptôme : plus d'Internet sur tous les postes. Constats : box joignable (0 % de perte), adresse Internet injoignable (100 % de perte), tracert arrêté au premier saut, NAS accessible, box non synchronisée depuis 9 h 05 avec l'adresse publique 0.0.0.0. Diagnostic : coupure de la liaison du fournisseur, réseau local sain. Actions : câbles contrôlés, box redémarrée, support appelé (n° d'incident), partage 4G pour l'accueil. État final : rétabli à telle heure, ou en attente du fournisseur. Recommandations : connexion de secours, coordonnées du support affichées près de la box.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier C
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Sécuriser un point d'accès, choisir le canal et placer le répéteur",
        question_type="document_analysis",
        requirement_ids=("AP-33",),
        kind=KIND_DOC,
        context=(
            "Dossier C. L'Atelier Linéa (document C1) se plaint d'un Wi-Fi lent dans la salle de dessin et "
            "l'associée craint pour la sécurité des plans des clients. Tu relèves la configuration du point d'accès "
            "(document C2), les réseaux voisins vus depuis l'accueil (document C3), les mesures autour du répéteur "
            "(document C4) et la fiche du portable (document C5)."
        ),
        documents=(_C_REQUEST, _C_AP, _C_SCAN, _C_PLAN, _C_RATES),
        instructions=(
            "Contrôle la fiche C2 : pour chaque réglage à changer, donne la nouvelle valeur et la raison (sécurité, chiffrement, clé, administration, radio).",
            "Choisis le canal 2,4 GHz et la largeur de canal à partir du relevé C3 (convertis les pourcentages en dBm) ; justifie.",
            ("Avec C4 et C5, estime le débit utile du portable de la salle de dessin dans trois cas : répéteur en R1, "
             "sans répéteur, répéteur en R2 (débit utile ≈ moitié du débit de liaison ; un répéteur à une radio divise "
             "encore par deux le plus faible de ses deux liens). Conclus et propose la meilleure solution."),
        ),
        criteria=(
            _c("Fiche du point d'accès", 4, f"0,5 point par réglage, au plus 4 : {_DEFECTS}. Raisons : WPA/TKIP (comme WEP) est obsolète et cassable ; WPA2 ou WPA3 chiffre en AES-CCMP ; la clé « {LIN_AP.passphrase} » est courte et contient le nom ; le code PIN WPS se devine ; un mot de passe d'usine est connu de tous ; un SSID masqué ne protège rien."),
            _c("Canal", 2, "dBm ≈ % ÷ 2 − 100 : " + ", ".join(f"{n.ssid} canal {n.channel} {_PC_SCAN[n.ssid]} % ≈ {dbm_from_pct(_PC_SCAN[n.ssid])} dBm" for n in LIN_NEIGHBORS) + f". Voisins forts (−80 dBm ou mieux) qui chevauchent (moins de 5 numéros d'écart) : canal 1 et canal 6 en ont deux chacun, canal 11 aucun (le voisin du 11 est à −86 dBm) → canal {LIN_BEST_CHANNEL}, largeur 20 MHz ; les appareils récents en 5 GHz."),
            _c("Répéteur", 4, f"R1 : point d'accès → R1 {REP_NOW_UPLINK} dBm → {link_rate(REP_NOW_UPLINK)} Mb/s ; R1 → portable {REP_NOW_CLIENT} dBm → {link_rate(REP_NOW_CLIENT)} Mb/s ; le plus faible {link_rate(REP_NOW_UPLINK)} ÷ 2 = {link_rate(REP_NOW_UPLINK) // 2}, utile ≈ {REP_NOW_MBPS:g} Mb/s. Sans répéteur : {AP_DIRECT_DBM} dBm → {link_rate(AP_DIRECT_DBM)} Mb/s, utile ≈ {AP_DIRECT_MBPS:g} Mb/s : R1 fait perdre du débit (il reçoit mal le point d'accès, sous −67 dBm). R2 : {REP_MID_UPLINK} et {REP_MID_CLIENT} dBm → {link_rate(REP_MID_UPLINK)} Mb/s ÷ 2 = {link_rate(REP_MID_UPLINK) // 2}, utile ≈ {REP_MID_MBPS:g} Mb/s : déplacer en R2. Meilleur : un second point d'accès câblé dans la salle (même SSID et sécurité, autre canal sans chevauchement), sans division du débit."),
        ),
        correction=(
            f"Réglages à corriger : {_DEFECTS}. WPA avec TKIP est obsolète et se casse : WPA3 (ou WPA2/WPA3 en transition) chiffre en AES-CCMP. La clé « {LIN_AP.passphrase} » est trop courte et contient le nom du bureau : il faut une longue phrase de passe. WPS se force par son code PIN, le mot de passe « admin » est connu de tous, un micrologiciel ancien garde des failles, un SSID masqué ne cache rien et gêne les connexions, et les invités doivent être isolés des plans des clients.",
            "Conversion : dBm ≈ % ÷ 2 − 100. " + ", ".join(f"{n.ssid} (canal {n.channel}) ≈ {dbm_from_pct(_PC_SCAN[n.ssid])} dBm" for n in LIN_NEIGHBORS) + f". Les canaux 1 et 6 sont gênés chacun par deux voisins forts (le canal 4 chevauche les deux) ; le canal 11 n'a qu'un voisin trop faible pour gêner. Je choisis le canal {LIN_BEST_CHANNEL}, en 20 MHz (40 MHz chevaucherait presque toute la bande) ; les portables récents utiliseront le 5 GHz.",
            f"Avec R1 : le répéteur reçoit le point d'accès à {REP_NOW_UPLINK} dBm, soit {link_rate(REP_NOW_UPLINK)} Mb/s ; le portable le reçoit à {REP_NOW_CLIENT} dBm ({link_rate(REP_NOW_CLIENT)} Mb/s). Le plus faible, {link_rate(REP_NOW_UPLINK)} Mb/s, est divisé par deux par le répéteur, puis la moitié est utile : environ {REP_NOW_MBPS:g} Mb/s. Sans répéteur, le portable reçoit {AP_DIRECT_DBM} dBm ({link_rate(AP_DIRECT_DBM)} Mb/s) : environ {AP_DIRECT_MBPS:g} Mb/s utiles, deux fois plus. En R2, les deux liens sont à {REP_MID_UPLINK} et {REP_MID_CLIENT} dBm ({link_rate(REP_MID_UPLINK)} Mb/s) : {link_rate(REP_MID_UPLINK)} ÷ 2 ÷ 2 ≈ {REP_MID_MBPS:g} Mb/s. Je déplace le répéteur en R2, à mi-chemin, là où il reçoit le point d'accès à −67 dBm ou mieux ; la meilleure solution reste un second point d'accès câblé dans la salle de dessin, même SSID et même sécurité, sur un autre canal sans chevauchement.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Vérifier les droits sur les partages et mettre un dossier à disposition",
        question_type="document_analysis",
        requirement_ids=("AP-25", "AP-26", "AP-27"),
        kind=KIND_DOC,
        context=(
            f"Dossier C. Sur le serveur {LIN_SRV_NAME} de l'Atelier Linéa (document C1), les dossiers des projets et "
            "de la comptabilité sont partagés (documents C6 et C7). L'associée te donne les besoins de chaque compte "
            "(document C8) et te demande aussi de mettre à disposition de tous un nouveau dossier Modèles (gabarits "
            "de plans et installateur du logiciel de rendu)."
        ),
        documents=(_C_REQUEST, _C_SHARES, _C_NTFS, _C_NEEDS),
        instructions=(
            f"Calcule l'accès effectif par le réseau de chacun des trois comptes sur {_ARCH_ROWS} (tableau) ; explique la règle de combinaison.",
            "Compare au besoin (C8) : quel besoin n'est pas satisfait, quelle couche le bloque, et quelle modification fais-tu (et pourquoi pas une autre) ?",
            "Nora affirme qu'en ouvrant sa session directement sur le serveur, elle peut modifier Compta. Explique.",
            "Rédige la mise à disposition du dossier Modèles : dossier, partage, autorisations, connexion des postes, contrôle.",
        ),
        criteria=(
            _c("Accès effectifs", 4, f"Par le réseau : le plus restrictif du partage et de NTFS ; dans chaque couche les autorisations des groupes s'additionnent ; un refus explicite l'emporte ; Concours n'hérite pas de Projets. Résultat : {_matrix_text(LIN_MATRIX)}. Environ 0,4 point par case, la règle compte pour le reste."),
            _c("Besoin non satisfait", 3, f"Nora doit modifier Compta mais n'obtient que « {SECR_COMPTA.lower()} » : NTFS lui donne Modification (G_Compta), le partage « Tout le monde : Lecture » la limite → la couche qui bloque est le partage. Modifier le partage Compta en « Utilisateurs authentifiés : Modifier » et laisser NTFS faire le tri (Tom reste sans accès, Eva en lecture). Après : {_matrix_text(LIN_MATRIX_FIXED)}. Ne pas donner un droit à Nora seule, ni ouvrir NTFS à tout le monde."),
            _c("Session sur le serveur", 1, f"En local, seul NTFS s'applique (le partage ne joue que par le réseau) : Nora a « {SECR_COMPTA_LOCAL.lower()} » sur le serveur, « {SECR_COMPTA.lower()} » par le réseau."),
            _c("Dossier Modèles", 2, f"Créer D:\\Partages\\Modeles ; partage « Modeles » pour Utilisateurs authentifiés (Lecture, ou Modifier en laissant NTFS décider) ; NTFS : Utilisateurs du domaine Lecture et exécution, G_Associes Modification pour tenir les gabarits ; sur les postes, lecteur réseau M: vers \\\\{LIN_SRV_NAME}\\Modeles (Explorateur ou « net use M: \\\\{LIN_SRV_NAME}\\Modeles /persistent:yes », ou stratégie de groupe) ; contrôle : un architecte ouvre un gabarit et lance l'installateur, mais ne peut pas enregistrer dans le dossier."),
        ),
        correction=(
            f"Par le réseau, l'accès effectif est le plus restrictif des deux couches, partage et NTFS ; dans une couche, les autorisations des groupes d'un compte s'additionnent, et un refus explicite l'emporte. Concours n'hérite pas de Projets : seuls les administrateurs et G_Associes y ont des droits. Résultat : {_matrix_text(LIN_MATRIX)}.",
            f"Le besoin de Nora sur Compta n'est pas satisfait : NTFS lui donne Modification par G_Compta, mais le partage n'accorde que Lecture à Tout le monde ; c'est le partage qui la limite (« {SECR_COMPTA.lower()} »). Je règle le partage Compta sur « Utilisateurs authentifiés : Modifier » et je laisse NTFS décider qui fait quoi : Tom reste sans accès (aucune entrée NTFS), Eva en lecture. Je ne donne pas un droit à Nora personnellement et je n'ouvre pas NTFS à tout le monde. Résultat : {_matrix_text(LIN_MATRIX_FIXED)}.",
            "Ouverte sur le serveur lui-même, la session de Nora n'utilise pas le partage : seul NTFS s'applique, et il lui donne Modification. Par le réseau, le partage la limitait à la lecture.",
            f"Dossier Modèles : créer D:\\Partages\\Modeles ; le partager sous le nom « Modeles » pour Utilisateurs authentifiés ; NTFS : Utilisateurs du domaine en Lecture et exécution, G_Associes en Modification pour mettre à jour les gabarits. Sur chaque poste, connecter le lecteur M: à \\\\{LIN_SRV_NAME}\\Modeles et cocher la reconnexion (ou « net use M: \\\\{LIN_SRV_NAME}\\Modeles /persistent:yes », ou une stratégie de groupe). Contrôle : un architecte ouvre un gabarit et lance l'installateur, mais l'enregistrement dans le dossier lui est refusé.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Dépanner l'imprimante réseau et l'accès au partage après un changement de box",
        question_type="document_analysis",
        requirement_ids=("AP-25", "AP-26", "AP-37"),
        kind=KIND_DOC,
        context=(
            "Dossier C. Depuis le remplacement de la box jeudi (document C1), le traceur A1 de l'Atelier Linéa "
            "n'imprime plus depuis aucun poste (document C9), et le portable de Tom ne retrouve plus son lecteur P: "
            "(document C10), alors que les autres postes ouvrent les partages."
        ),
        documents=(_C_REQUEST, _C_PRINTER, _C_SHARE),
        instructions=(
            "Interprète le document C9 : pourquoi le traceur n'imprime-t-il plus, et quel lien avec le changement de box ?",
            "Propose une correction durable pour le traceur (adresse, réglage sur les postes ou partage de l'imprimante) et les vérifications.",
            "Interprète le document C10 couche par couche : qu'est-ce qui fonctionne, qu'est-ce qui bloque, et ce que n'est pas le problème ?",
            "Indique ce que tu vérifies et corriges pour le lecteur P:, et comment tu prouves que c'est réglé.",
        ),
        criteria=(
            _c("Traceur : diagnostic", 2, f"Le port des postes vise {PRINTER_PORT_IP} ; le traceur a reçu {PRINTER_NEW_IP} par DHCP de la nouvelle box (les deux dans l'étendue {LIN_POOL[0]} à {LIN_POOL[1]}) ; le ping de {PRINTER_PORT_IP} répond « Impossible de joindre l'hôte » : plus personne à cette adresse. File « hors connexion » : les postes impriment vers une adresse vide."),
            _c("Traceur : correction", 3, f"Donner au traceur une adresse fixe hors de l'étendue, dans la plage des imprimantes (ex. {PRINTER_FIXED_IP}), sur son panneau, ou une réservation DHCP sur la box ; mettre à jour le port TCP/IP des postes ; mieux : partager le traceur depuis {LIN_SRV_NAME} (une file \\\\{LIN_SRV_NAME}\\Traceur-A1) pour n'avoir qu'un port à tenir à jour ; page de test depuis chaque poste, file vidée ou relancée, plan d'adressage mis à jour."),
            _c("Lecteur P: : diagnostic", 3, f"Ping de {LIN_SRV_NAME} : le nom est résolu ({LIN_SRV_IP}) et le serveur répond : DNS, adresse et réseau corrects. Test-NetConnection port 445 : False → le service de partage (SMB) n'est pas joignable depuis ce portable. Erreur 53 « chemin réseau introuvable » ≠ erreur 5 « accès refusé » : ce n'est pas une question de droits. Les autres postes ouvrent les partages : le serveur partage bien ; le blocage est sur le chemin de ce portable (pare-feu du portable ou profil réseau Public depuis la nouvelle box, ou règle du serveur)."),
            _c("Lecteur P: : correction et preuve", 2, "Vérifier le profil réseau du portable (domaine ou privé, pas public) et ses règles de pare-feu sortantes, la règle « Partage de fichiers et d'imprimantes » et le service Serveur côté serveur ; corriger ; preuve : TcpTestSucceeded True, net use P: réussit, ouverture d'un fichier ; consigner."),
        ),
        correction=(
            f"Les postes impriment vers le port {PRINTER_PORT_IP}, mais la page de configuration du traceur montre {PRINTER_NEW_IP}, obtenue par DHCP. La nouvelle box a redistribué les adresses de son étendue et le traceur a changé d'adresse. Le ping de {PRINTER_PORT_IP} répond « Impossible de joindre l'hôte de destination » : personne n'a plus cette adresse, d'où la file « hors connexion ».",
            f"Correction : donner au traceur une adresse fixe hors de l'étendue, dans la plage des imprimantes, par exemple {PRINTER_FIXED_IP} (ou une réservation DHCP sur la box), puis mettre à jour le port TCP/IP de chaque poste. Mieux encore, installer le traceur sur {LIN_SRV_NAME} et le partager : les postes se connectent à \\\\{LIN_SRV_NAME}\\Traceur-A1 et un seul port est à tenir à jour. Vérifier : page de test depuis chaque poste, documents en attente imprimés ou relancés, plan d'adressage mis à jour.",
            f"Sur le portable de Tom, le ping de {LIN_SRV_NAME} est résolu en {LIN_SRV_IP} et répond : le DNS, l'adresse IP et le réseau fonctionnent. Mais le test du port 445 échoue : le partage de fichiers (SMB) n'est pas joignable depuis ce poste. L'erreur 53 dit « chemin réseau introuvable », pas « accès refusé » (erreur 5) : les droits ne sont pas en cause. Comme les autres postes ouvrent les partages, le serveur fonctionne ; le blocage se trouve sur le chemin de ce portable : pare-feu ou profil réseau passé en « public » avec la nouvelle box.",
            f"Je vérifie le profil réseau du portable (réseau de domaine ou privé), ses règles de pare-feu, et côté serveur la règle « Partage de fichiers et d'imprimantes » et le service Serveur ; je corrige ce qui bloque. Preuve : Test-NetConnection {LIN_SRV_NAME} -Port 445 donne True, « net use P: {SHARE_UNC} » se termine correctement, Tom ouvre un fichier ; je consigne l'intervention.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()

# Partie ou dossier de chaque question, dans l'ordre du sujet.
ITEM_PARTS: dict[str, str] = {
    "X01": PART_1, "X02": PART_1,
    "X03": DOSSIER_A, "X04": DOSSIER_A,
    "X05": DOSSIER_B, "X06": DOSSIER_B, "X07": DOSSIER_B,
    "X08": DOSSIER_C, "X09": DOSSIER_C, "X10": DOSSIER_C,
}
# Cours où revoir la matière de chaque question.
ITEM_COURSES: dict[str, tuple[str, ...]] = {
    "X01": ("PR19",),
    "X02": ("PR20",),
    "X03": ("PR21", "PR20"),
    "X04": ("PR21", "PR18", "PR20"),
    "X05": ("PR24", "PR20"),
    "X06": ("PR24", "PR20"),
    "X07": ("PR24", "PR19"),
    "X08": ("PR25",),
    "X09": ("PR23", "PR22"),
    "X10": ("PR23", "PR24"),
}
DOSSIER_DOCUMENTS: dict[str, tuple[ExerciseDocument, ...]] = {
    DOSSIER_A: (_A_REQUEST, _A_IPCONFIG, _A_PINGS, _A_PLAN),
    DOSSIER_B: (_B_REQUEST, _B_IPCONFIG, _B_PINGS, _B_NSLOOKUP, _B_LINUX, _B_APIPA, _B_DHCP, _B_OUTAGE, _B_BOX),
    DOSSIER_C: (_C_REQUEST, _C_AP, _C_SCAN, _C_PLAN, _C_RATES, _C_SHARES, _C_NTFS, _C_NEEDS, _C_PRINTER, _C_SHARE),
}


def validate_items() -> list[str]:
    errors = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.total_points != POINTS_PER_QUESTION:
            errors.append(f"{item.key} : {item.total_points:g} points au lieu de {POINTS_PER_QUESTION}.")
        if item.question_type not in ("long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue.")
        if (item.question_type == "document_analysis") != bool(item.documents):
            errors.append(f"{item.key} : type et documents incohérents.")
    if sum(i.total_points for i in ALL_ITEMS) != EXAM_TOTAL_POINTS:
        errors.append("Total différent de 100 points.")
    return errors

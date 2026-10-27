"""PR21 « Connexion directe de deux PC et mini-réseau » — exercices corrigés et mini-examen
(ticket #221).

Même organisation que PR18 (`app.v1.ampcr_pratique_pr18_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (mise en service, extension, recette), classements
  (câble droit ou croisé, adresse fixe ou DHCP, premier contrôle en échec, lecture d'un ping),
  **quatre schémas à compléter** (connexion directe, câbles, mini-réseau, carte des adresses,
  servis en SVG), **relevés de commandes** à analyser (ipconfig, ping, arp -a), plan
  d'adressage à vérifier, partage d'un dossier, accès à Internet, recette ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, postes et adresses MAC sont **fictifs** ; les résultats de ping, erreurs
d'adressage et verdicts des énoncés et des corrigés viennent des fonctions de
`app.v1.ampcr_pratique_pr21_figures` (mêmes données que les schémas) et du modèle d'adressage
de PR20.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr21_figures import (
    ACCEPT_STEPS,
    ADDRESS_RANGES,
    ARP_FIREWALL_LINES,
    BOX_IP,
    CABLE_ANY,
    CABLE_BLANK_ROWS,
    CABLE_BLANKS,
    CABLE_CHOICES,
    CABLE_CROSS,
    CABLE_STRAIGHT,
    D_DHCP,
    D_DUP,
    D_FIREWALL,
    D_GW,
    D_LINK,
    D_PEER,
    D_PLAN,
    D_SHARE,
    DIRECT_BLANK_ANSWERS,
    DIRECT_STEPS,
    EXTEND_STEPS,
    ISOLATED_HOSTS,
    MAP_BLANK_ANSWERS,
    MINI_BLANK_ANSWERS,
    OUT_FAILURE,
    OUT_REPLY,
    OUT_TIMEOUT,
    OUT_UNREACHABLE,
    PC_A,
    PC_B,
    PING_FIREWALL_LINES,
    PING_OUTCOMES,
    POOL,
    SHARE_NAME,
    SHARE_UNC,
    STATIC_BY_KEY,
    AddressPlan,
    Host,
    cable_needed,
    direct_errors,
    first_failure,
    ipconfig_all_lines,
    ipconfig_duplicate_lines,
    ipconfig_static_lines,
    ping_lines,
    ping_outcome,
    plan_errors,
    range_of,
    same_network,
    validation_diagnosis,
)

PR21_CODE = "PR21"

KIND_ORDER = "ordonnancement"
KIND_CABLE = "liaison et câble"
KIND_ADDR = "adressage et plan"
KIND_SCHEMA = "schéma à compléter"
KIND_DIAG = "diagnostic sur relevés de commandes"
KIND_SHARE = "partage et pare-feu"
KIND_ACCEPT = "mise en service et recette"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-28", "AP-38"})

WEB_IP = "198.51.100.20"  # site Internet de test (RFC 5737, fictif)


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _host(name: str, ip: str, prefix: int, mac: str, *, gateway: str | None = None,
          dns: tuple[str, ...] = (), dhcp: bool = False, role: str = "poste") -> Host:
    return Host(name, role, ip, prefix, gateway, dns, mac, dhcp=dhcp)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(DIRECT_STEPS)
E02_STEPS = _labels(EXTEND_STEPS)
E03_STEPS = _labels(ACCEPT_STEPS)

# Câble droit ou croisé : (texte, appareil A, appareil B, Auto MDI-X A, Auto MDI-X B)
E04_CASES: tuple[tuple[str, str, str, bool, bool], ...] = (
    ("Deux anciens PC à cartes 100 Mb/s sans Auto MDI-X, reliés directement", "PC", "PC", False, False),
    ("PC récent à carte Auto MDI-X relié directement à un vieux PC sans Auto MDI-X", "PC", "PC", True, False),
    ("Ancien PC sans Auto MDI-X relié à un switch 10/100 sans Auto MDI-X", "PC", "Switch", False, False),
    ("Deux anciens switchs sans Auto MDI-X ni port « uplink », reliés port à port", "Switch", "Switch", False, False),
    ("Deux portables récents à cartes 1 Gb/s Auto MDI-X reliés directement", "Portable", "Portable", True, True),
    ("PC sans Auto MDI-X relié au port Ethernet d'un ancien routeur (port routé)", "PC", "Routeur (port routé)", False, False),
    ("PC sans Auto MDI-X relié à un port LAN de la box", "PC", "Box (ports LAN du switch intégré)", False, False),
)
E04_ANSWERS = tuple(cable_needed(a, b, auto_a=x, auto_b=y) for _t, a, b, x, y in E04_CASES)
E04_CORRECT = tuple(CABLE_CHOICES.index(c) for c in E04_ANSWERS)

E05_FIXED = "Adresse fixe ou réservée, hors de l'étendue DHCP"
E05_DHCP = "Adresse automatique (DHCP de la box)"
E05_CATEGORIES = (E05_FIXED, E05_DHCP)
E05_CASES: tuple[tuple[str, str], ...] = (
    ("Portable du commercial, qui se branche aussi chez les clients", E05_DHCP),
    ("Imprimante réseau utilisée par tous les postes", E05_FIXED),
    ("Poste de l'accueil", E05_DHCP),
    ("Box de l'opérateur, passerelle du réseau", E05_FIXED),
    (f"PC qui partage le dossier commun, ouvert par {SHARE_UNC}", E05_FIXED),
    ("Tablette de la salle de réunion", E05_DHCP),
    ("Deux PC reliés en direct par un câble, sans box ni serveur", E05_FIXED),
)
E05_CORRECT = tuple(E05_CATEGORIES.index(c) for _t, c in E05_CASES)

E06_CATEGORIES = (D_LINK, D_DHCP, D_DUP, D_PLAN)
E06_CASES: tuple[tuple[str, str], ...] = (
    ("ipconfig /all sur PC-B : « Statut du média : Média déconnecté »", "lien"),
    ("ipconfig /all sur PC-C : « Adresse IPv4 : 192.168.10.3(Dupliqué) »", "doublon"),
    ("PC-A 192.168.10.1/24 et PC-B 192.168.1.2/24 ; le ping affiche « Défaillance générale »", "reseau"),
    ("Poste en DHCP branché sur un switch sans box ni serveur : adresse 169.254.40.12", "adresse"),
    ("Voyants éteints des deux côtés : deux vieux PC sans Auto MDI-X reliés par un câble droit", "lien"),
    ("PC-A 192.168.10.1/24 ; PC-B 192.168.10.130 avec le masque 255.255.255.128", "reseau"),
    ("Windows signale un conflit d'adresse IP avec un autre appareil du réseau", "doublon"),
    ("Box débranchée du switch par erreur ; les postes en DHCP redémarrent en 169.254.x.x", "adresse"),
)
E06_CORRECT = tuple(E06_CATEGORIES.index(validation_diagnosis(first_failure(k))) for _t, k in E06_CASES)

E07_CATEGORIES = (D_PEER, D_FIREWALL, D_SHARE, D_GW)
E07_CASES: tuple[tuple[str, str], ...] = (
    ("Ping sans réponse (délai dépassé), mais arp -a montre la MAC du poste visé", "ping"),
    ("Ping « Impossible de joindre l'hôte de destination » : PC-C est éteint", "arp"),
    (f"Ping réussi ; « Accès refusé » en ouvrant {SHARE_UNC}", "partage"),
    ("Réseau local correct, aucun site ne s'ouvre ; ipconfig : passerelle vide", "internet"),
    ("Ping de 192.168.10.12 alors que l'imprimante est en .20 : impossible de joindre l'hôte", "arp"),
    ("Profil réseau « Public » sur PC-A ; ping sans réponse ; sa MAC est dans arp -a", "ping"),
    ("Passerelle correcte, une adresse IP publique répond au ping ; aucun site par son nom, DNS vide", "internet"),
    ("Le dossier partagé s'ouvre en lecture ; l'enregistrement d'un fichier est refusé", "partage"),
)
E07_CORRECT = tuple(E07_CATEGORIES.index(validation_diagnosis(first_failure(k))) for _t, k in E07_CASES)

# Lecture d'un ping : (situation, source, adresse visée, poste qui la possède, options)
B_OTHER_NET = _host("PC-B", "192.168.1.2", 24, PC_B.mac)
B_SLASH25 = _host("PC-B", "192.168.10.130", 25, PC_B.mac)
E08_CASES: tuple[tuple[str, str], ...] = (
    ("PC-A vers PC-B, configuration de référence, pare-feu réglé", ping_outcome(PC_A, PC_B.ip, PC_B)),
    ("PC-A vers 192.168.10.7 : aucun appareil n'a cette adresse", ping_outcome(PC_A, "192.168.10.7", None)),
    ("PC-B en 192.168.1.2/24 vers PC-A 192.168.10.1, sans passerelle", ping_outcome(B_OTHER_NET, PC_A.ip, PC_A)),
    ("PC-B vers PC-A, profil Public sur PC-A (écho ICMP refusé)", ping_outcome(PC_B, PC_A.ip, PC_A, icmp_allowed=False)),
    ("PC-A vers PC-B, câble débranché côté PC-A", ping_outcome(PC_A, PC_B.ip, PC_B, link=False)),
    ("PC-A vers PC-B, PC-B éteint", ping_outcome(PC_A, PC_B.ip, PC_B, dst_on=False)),
    ("PC-A (/24) vers PC-B en 192.168.10.130/25, sans passerelle", ping_outcome(PC_A, B_SLASH25.ip, B_SLASH25)),
    ("PC-B vers PC-A après ouverture de la règle d'écho ICMPv4", ping_outcome(PC_B, PC_A.ip, PC_A)),
)
E08_CORRECT = tuple(PING_OUTCOMES.index(o) for _t, o in E08_CASES)

E10_ANSWERS = tuple(cable_needed(a, b, auto_a=x, auto_b=y) for a, b, x, y in CABLE_BLANK_ROWS)

# E13 : masque erroné sur PC-B
E13_A = _host("PC-A", PC_A.ip, 24, PC_A.mac)
E13_B = B_SLASH25
E13_FROM_B = ping_outcome(E13_B, E13_A.ip, E13_A)
E13_FROM_A = ping_outcome(E13_A, E13_B.ip, E13_B)
E13_ERRORS = direct_errors(E13_A, E13_B)

# E15 : doublon après l'ajout d'un sixième poste
E15_NEW = _host("PC-F", "192.168.10.3", 24, "3C-52-82-4D-10-06", role="nouveau poste du stagiaire")
E15_OWNER = next(h for h in ISOLATED_HOSTS if h.ip == E15_NEW.ip)
E15_FREE = next(f"192.168.10.{n}" for n in range(1, 20) if f"192.168.10.{n}" not in {h.ip for h in ISOLATED_HOSTS})

# E16 : postes en DHCP sur un switch sans serveur DHCP
E16_HOST = _host("PC-C", "169.254.40.12", 16, "3C-52-82-4D-10-03", dhcp=True)

# E18 : plan d'adressage à vérifier (quatre erreurs volontaires)
E18_HOSTS: tuple[Host, ...] = (
    Host("BOX", "box", BOX_IP, 24, None, (), "00-1D-AA-7E-10-FE"),
    Host("PC-A", "partage", "192.168.10.1", 24, BOX_IP, (BOX_IP,), PC_A.mac),
    Host("IMP-01", "imprimante", "192.168.10.150", 24, BOX_IP, (BOX_IP,), "00-80-77-31-AB-20"),
    Host("PC-C", "accueil", "192.168.10.1", 24, BOX_IP, (BOX_IP,), "3C-52-82-4D-10-03"),
    Host("PC-D", "comptable", "192.168.10.4", 16, BOX_IP, (BOX_IP,), "3C-52-82-4D-10-04"),
    Host("PC-E", "gérant", "192.168.10.5", 24, "192.168.10.1", (BOX_IP,), "52-54-00-6B-21-05"),
)
E18_PLAN = AddressPlan("192.168.10.0/24", E18_HOSTS, BOX_IP, BOX_IP, POOL)
E18_ERRORS = plan_errors(E18_PLAN)

# E19 : poste à adresse fixe sans passerelle dans un réseau qui a une box
E19_HOST = _host("PC-D", "192.168.10.4", 24, "3C-52-82-4D-10-04")
E19_BOX = ping_outcome(E19_HOST, BOX_IP, _host("BOX", BOX_IP, 24, "00-1D-AA-7E-10-FE", role="box"))
E19_WEB = ping_outcome(E19_HOST, WEB_IP, None)

# --- Mini-examen -------------------------------------------------------------------------------

X01_NEW_OLD = cable_needed("PC", "PC", auto_a=True, auto_b=False)
X01_OLD_OLD = cable_needed("PC", "PC")
X03_OUTCOME = ping_outcome(PC_A, "192.168.10.2", None)
X03_LINES = ping_lines(PC_A, "192.168.10.2", X03_OUTCOME)
X04_B = B_OTHER_NET
X04_OUTCOME = ping_outcome(PC_A, X04_B.ip, X04_B)
X05_OUTCOME = ping_outcome(PC_A, PC_B.ip, PC_B, icmp_allowed=False)
X07_DEVICES = ("box", "PC qui partage le dossier", "imprimante", "3 postes", "1 portable")
X08_HOST = _host("PC-02", "169.254.12.7", 16, "3C-52-82-4D-20-02", dhcp=True)

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la mise en service d'une connexion directe",
        question_type="ordering",
        requirement_ids=("AP-28",),
        kind=KIND_ORDER,
        context=(
            "Une fleuriste veut copier chaque soir les commandes de son PC de bureau vers le portable "
            "qu'elle emporte, sans box ni switch : tu relies les deux machines par un câble. La fiche "
            "« connexion directe » de l'atelier compte sept étapes, imprimées dans le désordre."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, "Matériel → brancher et lire les voyants → adresser → pare-feu → tester → partager → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On vérifie les cartes réseau et le câble (Auto MDI-X ou câble croisé). 2. On branche et on lit le voyant de lien des deux côtés. 3. On donne à chaque PC une adresse du même réseau avec le même masque (192.168.10.1/24 et 192.168.10.2/24), sans passerelle.",
            "4. On règle le pare-feu (profil Privé, partage de fichiers et écho ICMP autorisés). 5. On teste : ipconfig, ping dans les deux sens, arp -a. 6. On partage le dossier avec un compte et des permissions adaptés. 7. On consigne adresses et résultats. Chaque étape suppose la précédente réussie.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 6, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'extension à un mini-réseau",
        question_type="ordering",
        requirement_ids=("AP-38",),
        kind=KIND_ORDER,
        context=(
            "La fleuriste embauche deux vendeuses et achète deux PC et une imprimante réseau. La "
            "connexion directe ne suffit plus : il faut un mini-réseau avec un switch et, plus tard, "
            "la box pour Internet. Ton collègue a mélangé les six étapes de la fiche « extension »."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Recenser → choisir le switch → plan d'adressage → raccorder → configurer les postes → valider chaque poste (0,5 pt par étape)."),
        ),
        correction=(
            "1. On recense les appareils et les besoins (partage, imprimante, Internet). 2. On choisit un switch avec assez de ports et de la réserve. 3. On écrit le plan d'adressage (réseau, masque, adresses fixes, étendue DHCP, passerelle, DNS) avant de toucher aux postes.",
            "4. On raccorde chaque appareil au switch par un câble droit, la box aussi si Internet est prévu. 5. On configure chaque poste selon le plan (DHCP ou fixe, nom unique, même groupe de travail). 6. On valide chaque poste dans l'ordre et on corrige la première piste en échec.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 5, 0, 3, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre les contrôles de la recette",
        question_type="ordering",
        requirement_ids=("AP-38",),
        kind=KIND_ORDER,
        context=(
            "Tu dois faire la recette d'un mini-réseau de cinq postes et d'une box dans un cabinet de "
            "kinésithérapie, poste par poste, avant de faire signer le client. Les neuf lignes du "
            "tableau de recette ont été recopiées dans le désordre par un stagiaire."
        ),
        instructions=("Remets les neuf contrôles dans l'ordre, du plus simple au plus large.",),
        criteria=(
            _c("Ordre", 4.5, "Lien → adresse → doublon → réseau et masque → table ARP → ping → partage → Internet → consigner et faire signer (0,5 pt par étape)."),
        ),
        correction=(
            "1. Lien : voyant allumé, pas de « Média déconnecté ». 2. Adresse : pas de 169.254.x.x. 3. Doublon : pas de « (Dupliqué) ». 4. Même réseau et même masque que les autres postes. 5. Table ARP : la MAC du poste visé apparaît après un ping.",
            "6. Le ping reçoit des réponses (sinon, avec la MAC connue : pare-feu). 7. Le partage s'ouvre avec le bon compte. 8. Internet : un site s'ouvre par son nom. 9. On consigne les résultats et on fait signer le procès-verbal. Le premier contrôle en échec désigne la piste.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (5, 2, 8, 0, 7, 3, 1, 6, 4)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Câble droit ou croisé pour chaque liaison ?",
        question_type="classification",
        requirement_ids=("AP-28", "AP-38"),
        kind=KIND_CABLE,
        context=(
            "Un atelier de reconditionnement mélange du matériel récent et des PC de plus de quinze ans. "
            "Pour chaque liaison, tu dois dire quel câble utiliser. Règle : carte réseau et port routé = "
            "MDI ; switch, hub et ports LAN d'une box = MDI-X ; un port Auto MDI-X s'adapte à tout câble."
        ),
        instructions=("Range chaque liaison selon le câble à utiliser.",),
        criteria=(
            _c("Classement", 3.5, "Deux anciens PC, deux anciens switchs, PC et port routé → croisé ; ancien PC et switch, PC et box → droit ; dès qu'un port fait l'Auto MDI-X → droit ou croisé (0,5 pt par élément)."),
        ),
        correction=(
            "Sans Auto MDI-X, une carte réseau émet sur les broches 1-2 et reçoit sur 3-6 ; un port de switch fait l'inverse. Entre deux appareils de types différents (PC et switch, PC et box), le câble droit relie l'émission de l'un à la réception de l'autre. Entre deux appareils de même type (deux PC, deux switchs, PC et port routé d'un routeur), il faut croiser : câble croisé, T568A à un bout et T568B à l'autre.",
            "Dès qu'un des deux ports fait l'Auto MDI-X, il inverse lui-même émission et réception : n'importe quel câble en bon état convient. C'est le cas de presque toutes les cartes 1 Gb/s actuelles ; on prend alors un câble droit, le seul qu'on stocke encore.",
        ),
        classification=Classification(categories=CABLE_CHOICES, elements=tuple(t for t, *_r in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Adresse fixe ou DHCP pour chaque appareil ?",
        question_type="classification",
        requirement_ids=("AP-38",),
        kind=KIND_ADDR,
        context=(
            f"Une agence d'intérim s'équipe d'un mini-réseau 192.168.10.0/24 avec une box en {BOX_IP} "
            f"qui distribue les adresses {POOL[0]} à {POOL[1]}. Pour chaque appareil de la liste du "
            "client, tu dois décider s'il reçoit une adresse automatique ou une adresse fixe."
        ),
        instructions=("Range chaque appareil selon le mode d'adressage à prévoir.",),
        criteria=(
            _c("Classement", 3.5, "Imprimante, box, PC qui partage, deux PC en direct → fixe ou réservée ; portable, accueil, tablette → DHCP (0,5 pt par élément)."),
        ),
        correction=(
            f"Reçoivent une adresse fixe (ou une réservation DHCP) les appareils que les autres doivent retrouver à la même adresse : la box (passerelle), l'imprimante, le PC qui partage le dossier ({SHARE_UNC}). Une adresse fixe se choisit hors de l'étendue {POOL[0]}–{POOL[1]}, sinon la box peut la donner à un autre appareil (doublon). Deux PC reliés en direct n'ont aucun serveur DHCP : adresses fixes obligatoires.",
            "Les postes et appareils mobiles (portable du commercial, tablette, poste de l'accueil) reçoivent leur adresse de la box : rien à saisir, pas de doublon, et le portable fonctionne aussi chez les clients.",
        ),
        classification=Classification(categories=E05_CATEGORIES, elements=tuple(t for t, _c2 in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Liaison, DHCP, doublon ou plan d'adressage ?",
        question_type="classification",
        requirement_ids=("AP-28", "AP-38"),
        kind=KIND_DIAG,
        context=(
            "Pendant la mise en service de connexions directes et de petits réseaux chez plusieurs "
            "clients, tes collègues t'envoient huit relevés. Pour chacun, dis quelle est la première "
            "piste à suivre, dans l'ordre de la recette : lien, adresse, doublon, réseau et masque."
        ),
        instructions=("Range chaque relevé selon la piste à suivre.",),
        criteria=(
            _c("Classement", 4, "Média déconnecté, câble droit entre deux vieux PC → liaison ; 169.254 (deux relevés) → DHCP ; (Dupliqué), conflit signalé → doublon ; 192.168.1.2/24, masque /25 → plan d'adressage (0,5 pt par élément)."),
        ),
        correction=(
            "« Média déconnecté » ou voyants éteints : aucun lien électrique ; entre deux vieux PC sans Auto MDI-X, un câble droit relie émission à émission : il faut un câble croisé. Une adresse 169.254.x.x montre que le poste en DHCP n'a reçu aucune réponse d'un serveur DHCP (switch sans box, box débranchée).",
            "« (Dupliqué) » ou un conflit signalé par Windows : un autre appareil a déjà cette adresse ; le poste ne s'en sert pas. 192.168.1.2/24 n'est pas dans le réseau 192.168.10.0/24 ; avec le masque 255.255.255.128, 192.168.10.130 est dans 192.168.10.128/25, qui ne contient pas 192.168.10.1 : plan d'adressage.",
        ),
        classification=Classification(categories=E06_CATEGORIES, elements=tuple(t for t, _k in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Poste distant, pare-feu, partage ou Internet ?",
        question_type="classification",
        requirement_ids=("AP-28", "AP-38"),
        kind=KIND_DIAG,
        context=(
            "Dans un cabinet d'architectes, le lien, l'adresse et le plan d'adressage de chaque poste "
            "sont corrects. Il reste huit constats. Ordre des contrôles suivants : table ARP (poste "
            "distant), ping (pare-feu), partage, Internet ; le premier en échec désigne la piste."
        ),
        instructions=("Range chaque constat selon la piste à suivre.",),
        criteria=(
            _c("Classement", 4, "Hôte injoignable (poste éteint, mauvaise adresse) → poste distant ; délai dépassé avec MAC connue (deux constats) → pare-feu ; accès refusé, écriture refusée → partage ; passerelle vide, DNS vide → Internet (0,5 pt par élément)."),
        ),
        correction=(
            "« Impossible de joindre l'hôte de destination » : personne n'a répondu à la requête ARP ; le poste visé est éteint ou on vise une adresse que personne ne possède (.12 au lieu de .20). Si la MAC du poste visé est dans arp -a mais que le ping n'obtient aucune réponse, le poste existe et le réseau est bon : son pare-feu refuse l'écho ICMP (profil Public).",
            "Ping réussi mais « Accès refusé » ou écriture refusée : compte ou permissions du partage. Réseau local correct mais pas d'Internet : sans passerelle, rien ne sort ; une adresse IP publique qui répond sans qu'aucun site s'ouvre par son nom : DNS absent ou faux.",
        ),
        classification=Classification(categories=E07_CATEGORIES, elements=tuple(t for t, _k in E07_CASES), correct=E07_CORRECT),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Que va afficher le ping ?",
        question_type="classification",
        requirement_ids=("AP-28",),
        kind=KIND_DIAG,
        context=(
            f"Configuration de référence : PC-A {PC_A.ip}/24 et PC-B {PC_B.ip}/24 reliés en direct, "
            "sans passerelle. Pour préparer ta fiche d'aide au diagnostic, tu prévois ce qu'affiche "
            "un ping sous Windows dans huit situations, avant de les vérifier en atelier."
        ),
        instructions=("Range chaque situation selon le résultat affiché par le ping.",),
        criteria=(
            _c("Classement", 4, "Référence et règle rouverte → réponse ; règle d'écho refusée, masque /25 du destinataire → délai dépassé ; adresse inexistante, PC éteint → hôte inaccessible ; autre réseau sans passerelle, câble débranché → défaillance générale (0,5 pt par élément)."),
        ),
        correction=(
            "« Défaillance générale » : le poste ne peut rien émettre, faute de route : câble débranché (carte sans lien) ou destination hors de son réseau sans passerelle. « Impossible de joindre l'hôte de destination » : la destination est dans le réseau, mais personne ne répond à la requête ARP (adresse inexistante, poste éteint) ; le message vient du poste lui-même.",
            "« Délai d'attente dépassé » : la demande arrive mais aucune réponse ne revient : pare-feu qui refuse l'écho, ou destinataire qui ne voit pas l'émetteur dans son réseau (masque /25 : 192.168.10.1 hors de 192.168.10.128/25) et n'a pas de passerelle. Réponse : tout est correct.",
        ),
        classification=Classification(categories=PING_OUTCOMES, elements=tuple(t for t, _o in E08_CASES), correct=E08_CORRECT),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : configurer une connexion directe",
        question_type="document_analysis",
        requirement_ids=("AP-28",),
        kind=KIND_SCHEMA,
        context=(
            f"Un comptable indépendant veut relier son PC (PC-A, déjà configuré en {PC_A.ip}/24) à son "
            "portable pour copier ses dossiers, sans box ni switch. Le document 1 montre la liaison : "
            "il manque la configuration du portable et le type de câble. La carte du portable fait l'Auto MDI-X."
        ),
        documents=(_schema("pr21-connexion-a-completer", "Document 1 — Connexion directe à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ② et ③ pour PC-B, puis ④.",
            "Justifie l'absence de passerelle.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in DIRECT_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, "Les deux PC sont dans le même réseau : ils se parlent directement ; une passerelle ne sert qu'à sortir du réseau, et il n'y a aucun routeur."),
        ),
        correction=(
            f"① {PC_B.ip} : même réseau 192.168.10.0/24 que PC-A, adresse différente (de .2 à .254, ni .0 ni .255). ② {PC_B.mask}, le même masque que PC-A. ③ Vide. ④ Câble droit : la carte du portable fait l'Auto MDI-X, elle inverse elle-même émission et réception (sans Auto MDI-X des deux côtés : câble croisé).",
            "Un poste n'utilise sa passerelle que pour joindre une adresse hors de son réseau. Ici les deux adresses sont dans 192.168.10.0/24 et il n'existe aucun routeur : la passerelle et le DNS restent vides.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : quel câble pour chaque liaison ?",
        question_type="document_analysis",
        requirement_ids=("AP-28", "AP-38"),
        kind=KIND_SCHEMA,
        context=(
            "Une école récupère du matériel de plusieurs générations pour sa salle de technologie. Le "
            "document 1 liste cinq liaisons à faire, en précisant pour chaque port s'il fait l'Auto "
            "MDI-X. Le magasin a des câbles droits et quelques câbles croisés étiquetés."
        ),
        documents=(_schema("pr21-cablage-a-completer", "Document 1 — Câbles à choisir (schéma fictif)"),),
        instructions=(
            "Indique le câble de chaque liaison ① à ⑤.",
            "Explique la règle utilisée et le rôle de l'Auto MDI-X.",
        ),
        criteria=(
            _c("Câbles", 2.5, " ; ".join(f"{CABLE_BLANKS[i]} {c.lower()}" for i, c in enumerate(E10_ANSWERS)) + " (0,5 pt chacun)."),
            _c("Règle", 1, "MDI (carte, port routé) / MDI-X (switch, hub) : même type → croisé ; types différents → droit ; un seul port Auto MDI-X suffit pour que tout câble fonctionne."),
        ),
        correction=(
            f"① Deux PC sans Auto MDI-X : même type (MDI), {E10_ANSWERS[0].lower()}. ② PC et switch : types différents, {E10_ANSWERS[1].lower()}. ③ Deux switchs sans Auto MDI-X : même type (MDI-X), {E10_ANSWERS[2].lower()}. ④ Le portable fait l'Auto MDI-X : {E10_ANSWERS[3].lower()}. ⑤ PC et port routé du routeur, tous deux MDI : {E10_ANSWERS[4].lower()}.",
            "En 10/100 Mb/s, une carte émet sur 1-2 et reçoit sur 3-6 ; le câble croisé (A d'un côté, B de l'autre) relie 1-2 à 3-6. Un port Auto MDI-X détecte le câble et inverse lui-même émission et réception : il suffit qu'un des deux ports le fasse.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : mini-réseau avec box",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_SCHEMA,
        context=(
            f"Le cabinet de PC-A a grandi : cinq postes, une imprimante et la box de l'opérateur en "
            f"{BOX_IP}, qui distribue les adresses {POOL[0]} à {POOL[1]}. Convention de l'atelier : "
            "imprimantes et équipements à adresse fixe de .20 à .49. Le document 1 est le schéma du réseau à terminer."
        ),
        documents=(_schema("pr21-mini-reseau-a-completer", "Document 1 — Mini-réseau à compléter (schéma fictif)"),),
        instructions=(
            "Complète ① ; donne l'adresse ② de l'imprimante, la passerelle ③ et le DNS ④ de PC-A.",
            "Explique pourquoi l'imprimante ne doit pas prendre une adresse entre .100 et .199.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in MINI_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, "Une adresse fixe dans l'étendue DHCP peut être donnée par la box à un autre appareil : doublon, l'un des deux perd le réseau."),
        ),
        correction=(
            f"① Un switch, centre de l'étoile : chaque appareil et la box y sont reliés par un câble droit. ② Une adresse fixe de la plage des imprimantes, par exemple 192.168.10.20/24. ③ et ④ {BOX_IP} : la box est la passerelle (sortie vers Internet) et relaie les requêtes DNS ; PC-A, à adresse fixe, ne reçoit rien du DHCP : on les saisit à la main (un poste en DHCP les reçoit de la box avec son adresse).",
            f"L'étendue {POOL[0]}–{POOL[1]} appartient au serveur DHCP de la box : elle peut y donner n'importe quelle adresse libre à ses yeux. Une adresse fixe saisie dans cette plage finira par être attribuée aussi à un autre appareil (doublon).",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : carte des adresses du réseau",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_SCHEMA,
        context=(
            "Tu rédiges le dossier technique d'une PME de six postes. Pour que chaque technicien "
            "attribue les adresses de la même façon, tu dessines la carte des adresses du réseau "
            "192.168.10.0/24 (document 1). Il reste quatre plages dont l'usage est à écrire."
        ),
        documents=(_schema("pr21-plan-adressage-a-completer", "Document 1 — Carte des adresses à compléter (schéma fictif)"),),
        instructions=(
            "Indique l'usage des plages ① à ④.",
            "Dis dans quelle plage tombent les adresses 192.168.10.7, 192.168.10.33 et 192.168.10.150.",
        ),
        criteria=(
            _c("Usages", 2, " ; ".join(f"{k} {v}" for k, v in MAP_BLANK_ANSWERS.items()) + " (0,5 pt chacun)."),
            _c("Lecture", 1.5, f".7 → {range_of('192.168.10.7').lower()} ; .33 → {range_of('192.168.10.33').lower()} ; .150 → {range_of('192.168.10.150').lower()} (0,5 pt chacune)."),
        ),
        correction=(
            "① .1 à .19 : postes et serveur à adresse fixe (dont PC-A en .1). ② .20 à .49 : imprimantes et équipements à adresse fixe. ③ .100 à .199 : étendue DHCP de la box. ④ .254 : la box, passerelle et DNS. Les plages libres servent de réserve ; .0 et .255 ne s'attribuent jamais.",
            f"192.168.10.7 : {range_of('192.168.10.7').lower()} ; 192.168.10.33 : {range_of('192.168.10.33').lower()} ; 192.168.10.150 : {range_of('192.168.10.150').lower()}, donc à ne jamais saisir à la main.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Deux PC reliés en direct ne se voient pas",
        question_type="document_analysis",
        requirement_ids=("AP-28",),
        kind=KIND_DIAG,
        context=(
            "Chez un photographe, deux PC sont reliés par un câble droit, les voyants sont allumés des "
            "deux côtés, mais aucun transfert ne fonctionne. Le document 1 montre la configuration de "
            "chaque PC, le document 2 le ping lancé dans chaque sens."
        ),
        documents=(
            _console("Document 1 — ipconfig /all sur les deux PC (extraits fictifs)",
                     "PC-A", *ipconfig_static_lines(E13_A), "", "PC-B", *ipconfig_static_lines(E13_B)),
            _console("Document 2 — Ping dans chaque sens (extraits fictifs)",
                     *ping_lines(E13_B, E13_A.ip, E13_FROM_B)[:3], "", *ping_lines(E13_A, E13_B.ip, E13_FROM_A)[:5]),
        ),
        instructions=(
            "Trouve l'erreur de configuration et explique chacun des deux messages du ping.",
            "Propose la correction et le test qui la valide.",
        ),
        criteria=(
            _c("Erreur", 1, f"PC-B : masque {E13_B.mask} (/25) : son réseau est 192.168.10.128/25, qui ne contient pas {E13_A.ip} ; PC-A (/24) voit pourtant PC-B dans son réseau."),
            _c("Messages", 1, "Depuis PC-B : défaillance générale (PC-A hors de son réseau, pas de passerelle) ; depuis PC-A : la demande arrive, PC-B ne sait pas répondre → délai dépassé."),
            _c("Correction", 1, f"PC-B en {PC_B.ip} masque 255.255.255.0 (ou garder .130 avec le masque 255.255.255.0) ; ping dans les deux sens, arp -a."),
        ),
        correction=(
            f"PC-A a le masque 255.255.255.0 : pour lui, 192.168.10.130 est dans son réseau 192.168.10.0/24. PC-B a le masque {E13_B.mask} : son réseau est 192.168.10.128/25 (adresses .129 à .254), qui ne contient pas 192.168.10.1. Les deux postes n'ont pas la même idée du réseau.",
            "Depuis PC-B, 192.168.10.1 est hors réseau et il n'y a pas de passerelle : rien ne peut partir, « Défaillance générale ». Depuis PC-A, la demande part et arrive, mais PC-B ne sait pas renvoyer la réponse vers 192.168.10.1 : « Délai d'attente dépassé ».",
            f"On met le même masque 255.255.255.0 sur les deux PC (PC-B peut garder .130, ou prendre {PC_B.ip}) ; on refait le ping dans les deux sens et on vérifie la MAC dans arp -a.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Le ping échoue, mais la MAC est connue",
        question_type="document_analysis",
        requirement_ids=("AP-28",),
        kind=KIND_SHARE,
        context=(
            f"Dans une petite boutique, tu viens de relier PC-B ({PC_B.ip}/24) à PC-A ({PC_A.ip}/24) "
            "par un câble, sans box. Voyants allumés, adresses vérifiées avec ipconfig. Windows indique "
            "pour PC-A « Réseau non identifié ». Le document 1 montre ce que tu relèves sur PC-B."
        ),
        documents=(_console("Document 1 — Relevé sur PC-B (capture fictive)", *PING_FIREWALL_LINES, "", *ARP_FIREWALL_LINES),),
        instructions=(
            "Interprète le ping et la table ARP : qu'est-ce qui fonctionne, qu'est-ce qui bloque ?",
            "Donne les réglages à faire sur PC-A, sans désactiver le pare-feu.",
        ),
        criteria=(
            _c("Interprétation", 1.5, f"4 délais dépassés, mais la MAC {PC_A.mac.lower()} de PC-A est dans arp -a : câble, cartes et adressage fonctionnent ; PC-A reçoit la demande et ne répond pas → pare-feu."),
            _c("Réglages", 1.5, "Réseau non identifié (pas de passerelle) → profil Public : passer le profil en Privé ; activer le partage de fichiers et d'imprimantes (règle d'écho ICMPv4 entrante) ; refaire le ping."),
        ),
        correction=(
            f"La table ARP de PC-B contient {PC_A.ip} avec la MAC de PC-A : PC-A a répondu à la requête ARP, donc le câble, les cartes et l'adressage sont bons. La demande d'écho arrive, mais aucune réponse ne revient : c'est le pare-feu de PC-A qui la refuse.",
            "Sans passerelle, Windows classe la connexion en « réseau non identifié », profil Public, où l'écho ICMP et le partage sont bloqués. Sur PC-A : profil réseau Privé (Paramètres, Ethernet, ou Set-NetConnectionProfile), partage de fichiers et d'imprimantes activé sur ce profil, ce qui ouvre la règle « Demande d'écho ICMPv4 entrante ». On ne coupe pas le pare-feu ; on refait le ping.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Un sixième poste et une adresse dupliquée",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_DIAG,
        context=(
            "Le mini-réseau isolé d'une association (cinq PC autour d'un switch, adresses fixes "
            "192.168.10.1 à .5, sans box) reçoit un sixième poste pour un stagiaire. Depuis son "
            "installation, PC-C (accueil) perd par moments le réseau. Le document 2 montre le relevé du nouveau poste."
        ),
        documents=(
            _table("Document 1 — Plan d'adressage affiché dans le local", ("Poste", "Adresse", "Masque"),
                   *((h.name, h.ip, h.mask) for h in ISOLATED_HOSTS)),
            _console("Document 2 — ipconfig /all sur le nouveau poste (capture fictive)", *ipconfig_duplicate_lines(E15_NEW)),
        ),
        instructions=("Explique le problème, sa conséquence et la correction, puis ce que tu mets à jour.",),
        criteria=(
            _c("Diagnostic", 1, f"« (Dupliqué) » : {E15_NEW.ip} est déjà l'adresse de {E15_OWNER.name} ; deux appareils ne peuvent pas avoir la même adresse."),
            _c("Correction", 1, f"Adresse libre du plan pour le nouveau poste (par exemple {E15_FREE}), même masque ; ping depuis et vers PC-C."),
            _c("Documentation", 0.5, "Plan d'adressage mis à jour (nouvelle ligne), consigné dans la fiche."),
        ),
        correction=(
            f"Le nouveau poste a reçu {E15_NEW.ip}, déjà utilisée par {E15_OWNER.name} : Windows l'a détecté et marque l'adresse « (Dupliqué) » ; selon l'ordre de démarrage, l'un ou l'autre perd le réseau, d'où les coupures de l'accueil.",
            f"On donne au nouveau poste une adresse libre du plan, par exemple {E15_FREE}/24 (même masque, sans passerelle), on vérifie l'absence de « (Dupliqué) », on teste par ping dans les deux sens avec PC-C, puis on ajoute la ligne dans le plan d'adressage affiché et dans la fiche.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Tous les postes en 169.254 sur un switch neuf",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_DIAG,
        context=(
            "Un club de bridge relie quatre PC portables à un switch neuf pour partager un fichier de "
            "scores ; il n'y a ni box ni serveur dans la salle. Les portables sont réglés en adresse "
            "automatique. Les voyants sont allumés, mais rien ne fonctionne. Le document 1 montre un relevé."
        ),
        documents=(_console("Document 1 — ipconfig /all sur PC-C (capture fictive)",
                            "C:\\> ipconfig /all", "", *ipconfig_all_lines(E16_HOST, dhcp_server=None, apipa=True)),),
        instructions=("Explique l'adresse obtenue et propose deux solutions, avec leur intérêt.",),
        criteria=(
            _c("Explication", 1, "Adresse 169.254.x.x (masque 255.255.0.0, pas de passerelle) : le poste n'a reçu aucune réponse de serveur DHCP ; il n'y en a pas dans la salle."),
            _c("Solutions", 1.5, "Adresses fixes d'un plan (192.168.10.1 à .4 /24, sans passerelle) ; ou ajouter un serveur DHCP (box, routeur) ; justifier (salle isolée → fixe simple)."),
        ),
        correction=(
            f"{E16_HOST.ip} avec le masque {E16_HOST.mask} est une adresse que Windows se donne seul quand aucun serveur DHCP ne répond (plage 169.254.0.0/16). Un switch ne distribue pas d'adresses : sans box ni serveur, les portables restent en 169.254. Ils pourraient parfois se joindre entre eux, mais rien n'est maîtrisé.",
            "Solution 1, la plus simple pour une salle isolée : adresses fixes d'un plan, 192.168.10.1 à 192.168.10.4/24, sans passerelle ni DNS, notées sur chaque portable. Solution 2 : brancher un appareil serveur DHCP (box ou petit routeur) sur le switch, qui donnera adresse, masque et, s'il a Internet, passerelle et DNS. On valide ensuite par ping et accès au partage.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Partager un dossier entre deux PC reliés en direct",
        question_type="long_answer",
        requirement_ids=("AP-28",),
        kind=KIND_SHARE,
        context=(
            f"La connexion directe est validée (ping dans les deux sens). Le client veut que le portable "
            f"(PC-B) puisse lire et modifier les fichiers du dossier {SHARE_NAME} de PC-A, sous Windows. "
            "Sur PC-A, il existe un compte « tech » avec mot de passe ; personne d'autre ne doit y accéder."
        ),
        instructions=(
            "Rédige la procédure de partage sur PC-A, l'accès depuis PC-B et le test final.",
            "Explique comment se combinent les permissions du partage et celles du dossier.",
        ),
        criteria=(
            _c("Partage", 1.5, f"Propriétés → Partage → Partage avancé : nom {SHARE_NAME}, autorisation Modifier pour tech (pas Tout le monde) ; onglet Sécurité : Modification pour tech ; profil Privé et partage de fichiers activés (ou net share {SHARE_NAME}=C:\\{SHARE_NAME} /GRANT:tech,CHANGE)."),
            _c("Accès et test", 1.5, f"{SHARE_UNC} dans l'Explorateur ou net use Z: {SHARE_UNC} /user:PC-A\\tech ; créer, modifier, supprimer un fichier de test ; noter le résultat."),
            _c("Permissions", 1, "Par le réseau, c'est la plus restrictive des deux qui s'applique (Lecture d'un côté → lecture seule) ; un compte sans mot de passe est refusé par défaut à travers le réseau."),
        ),
        correction=(
            f"Sur PC-A : clic droit sur C:\\{SHARE_NAME} → Propriétés → Partage → Partage avancé → « Partager ce dossier », nom {SHARE_NAME} ; Autorisations : retirer « Tout le monde », ajouter tech avec « Modifier ». Onglet Sécurité : tech en « Modification ». Le profil réseau doit être Privé avec le partage de fichiers et d'imprimantes activé (pare-feu, port 445).",
            f"Sur PC-B : {SHARE_UNC} dans l'Explorateur (ou \\\\PC-A\\{SHARE_NAME} si le nom est résolu), identifiants PC-A\\tech et son mot de passe ; ou net use Z: {SHARE_UNC} /user:PC-A\\tech. Test : créer, renommer, supprimer un fichier ; consigner.",
            "À travers le réseau, Windows applique la plus restrictive des deux permissions : partage « Lecture » + dossier « Modification » donne lecture seule. Un compte local sans mot de passe est refusé par défaut à travers le réseau : on utilise un compte avec mot de passe. Les permissions détaillées sont l'objet du cours PR23.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Vérifier un plan d'adressage",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_ADDR,
        context=(
            f"Un collègue a préparé le plan d'adressage d'un mini-réseau avant l'installation : réseau "
            f"192.168.10.0/24, box en {BOX_IP} (passerelle et DNS), étendue DHCP {POOL[0]} à {POOL[1]}. "
            "Tous les appareils du document 1 seraient configurés à la main. Tu relis le plan avant de partir chez le client."
        ),
        documents=(
            _table("Document 1 — Plan d'adressage proposé", ("Appareil", "Adresse", "Masque", "Passerelle", "DNS"),
                   *((h.name, h.ip, h.mask, h.gateway or "—", h.dns[0] if h.dns else "—") for h in E18_HOSTS)),
        ),
        instructions=("Relève chaque erreur, sa conséquence et la valeur correcte.",),
        criteria=(
            _c("Erreurs", 2, "IMP-01 .150 dans l'étendue DHCP ; PC-C .1 = doublon avec PC-A ; PC-D masque 255.255.0.0 ; PC-E passerelle .1 (PC-A) au lieu de la box (0,5 pt chacune)."),
            _c("Corrections", 1, f"IMP-01 en .20 ; PC-C en .3 (ou DHCP) ; PC-D masque 255.255.255.0 ; PC-E passerelle {BOX_IP}."),
        ),
        correction=(
            f"IMP-01 en 192.168.10.150 : adresse fixe dans l'étendue {POOL[0]}–{POOL[1]}, la box pourra la donner à un autre appareil (doublon) → .20. PC-C en 192.168.10.1 : même adresse que PC-A, l'un des deux sera « (Dupliqué) » → .3 ou DHCP.",
            f"PC-D avec 255.255.0.0 : il se croit dans 192.168.0.0/16 ; il joint encore les postes du /24 mais le plan est incohérent et des adresses hors du réseau lui sembleront locales → 255.255.255.0. PC-E a pour passerelle 192.168.10.1, un PC et pas la box : pas d'Internet → {BOX_IP}. Le contrôle automatique du plan relève {len(E18_ERRORS)} erreurs.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Le réseau local fonctionne, Internet non",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_DIAG,
        context=(
            f"Une box ({BOX_IP}) a été ajoutée au mini-réseau d'un cabinet. Les postes en DHCP ont "
            "Internet ; PC-D, configuré à la main lors de la connexion directe du début, partage et "
            "imprime toujours, mais n'ouvre aucun site. Le document 1 montre tes relevés sur PC-D."
        ),
        documents=(_console("Document 1 — Relevés sur PC-D (captures fictives)",
                            *ipconfig_static_lines(E19_HOST),
                            "",
                            *ping_lines(E19_HOST, BOX_IP, E19_BOX)[:4],
                            "",
                            *ping_lines(E19_HOST, WEB_IP, E19_WEB)[:3]),),
        instructions=("Explique les deux résultats et propose deux corrections possibles.",),
        criteria=(
            _c("Explication", 1.5, f"La box ({BOX_IP}) répond : même réseau ; une adresse d'Internet ({WEB_IP}) est hors réseau et PC-D n'a pas de passerelle → défaillance générale ; pas de DNS non plus."),
            _c("Corrections", 1.5, f"Ajouter passerelle {BOX_IP} et DNS {BOX_IP} ; ou passer PC-D en DHCP (s'il ne partage rien) ; valider en ouvrant un site par son nom."),
        ),
        correction=(
            f"PC-D est bien dans 192.168.10.0/24 : il joint la box et les autres postes. Pour {WEB_IP}, hors de son réseau, il lui faut une passerelle ; le champ est vide, il ne peut rien émettre : « Défaillance générale ». Sans DNS, aucun nom de site ne serait traduit non plus.",
            f"Correction 1 : garder l'adresse fixe et ajouter passerelle {BOX_IP} et DNS {BOX_IP}. Correction 2 : si PC-D ne partage rien, le passer en adresse automatique, la box lui donnera tout. Validation : ping de {WEB_IP}, puis ouverture d'un site par son nom.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Rédiger le tableau de recette d'un mini-réseau",
        question_type="long_answer",
        requirement_ids=("AP-28", "AP-38"),
        kind=KIND_ACCEPT,
        context=(
            "Tu termines l'installation d'un mini-réseau de quatre postes, d'une imprimante et d'une box "
            "dans une agence d'assurances. Le responsable veut un tableau de recette qu'il pourra "
            "relire seul, puis signer. Un poste (PC-03) a montré un doublon, corrigé pendant l'intervention."
        ),
        instructions=(
            "Propose les colonnes du tableau, les contrôles par poste et la preuve attendue pour chacun.",
            "Indique comment tu consignes le doublon corrigé et ce qui accompagne la signature.",
        ),
        criteria=(
            _c("Contrôles et preuves", 2, "Par poste : lien (voyant), adresse (ipconfig, pas 169.254), doublon (pas « (Dupliqué) »), réseau et masque, ping et arp -a vers un autre poste et la box, partage, Internet par un nom ; résultat OK / KO."),
            _c("Consignation", 1, "Doublon : constat, cause, correction, nouveau test OK ; plan d'adressage mis à jour ; réserves éventuelles."),
            _c("Signature", 1, "Plan d'adressage, schéma, comptes remis à part, tableau de recette, procès-verbal daté et signé."),
        ),
        correction=(
            "Colonnes : poste, adresse prévue au plan, contrôle, commande ou geste, résultat attendu, résultat obtenu, OK/KO, remarque. Contrôles dans l'ordre pour chaque poste : voyant de lien ; ipconfig (adresse du plan ou de l'étendue, pas de 169.254, pas de « (Dupliqué) », masque 255.255.255.0) ; ping de la box et d'un autre poste, MAC dans arp -a ; ouverture du partage ; impression d'une page ; ouverture d'un site par son nom.",
            "Pour PC-03 : « doublon avec IMP-01 constaté (Dupliqué), adresse fixe déplacée hors de l'étendue, contrôle refait : OK ». Le plan d'adressage est mis à jour. On joint le schéma du réseau et le plan ; les mots de passe sont remis à part ; le responsable signe un procès-verbal daté, avec les réserves éventuelles.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions × 2 points (réponses libres)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Choisir le câble d'une connexion directe",
        question_type="short_answer",
        requirement_ids=("AP-28",),
        kind=KIND_CABLE,
        context=(
            "Un client veut récupérer les photos d'un vieux PC de 2006 (carte 100 Mb/s sans Auto MDI-X) "
            "en le reliant directement à son PC neuf (carte 1 Gb/s avec Auto MDI-X). Il te demande ensuite "
            "s'il pourrait relier de la même façon ce vieux PC à un second PC tout aussi ancien."
        ),
        instructions=("Indique le câble à utiliser dans chaque cas et justifie.",),
        criteria=(
            _c("Vieux PC et PC neuf", 1, f"{X01_NEW_OLD} : la carte neuve fait l'Auto MDI-X, un seul port suffit ; un câble droit convient."),
            _c("Deux vieux PC", 1, f"{X01_OLD_OLD} (T568A d'un côté, T568B de l'autre) : deux cartes MDI sans Auto MDI-X ; un câble droit relierait émission à émission, voyants éteints."),
        ),
        correction=(
            "Vieux PC et PC neuf : la carte neuve fait l'Auto MDI-X, elle inverse elle-même émission et réception ; un câble droit (ou croisé) en bon état fonctionne. Le lien se fera à 100 Mb/s, la vitesse de la carte la plus lente.",
            "Deux vieux PC sans Auto MDI-X : deux ports de même type (MDI). Il faut un câble croisé, T568A à un bout et T568B à l'autre, qui relie les broches 1-2 de l'un aux broches 3-6 de l'autre.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Adresser deux PC reliés en direct",
        question_type="short_answer",
        requirement_ids=("AP-28",),
        kind=KIND_ADDR,
        context=(
            "Dans un cabinet dentaire, tu relies le PC de la radiographie au PC du dentiste par un câble, "
            "pour transférer les images. Aucun des deux ne doit aller sur Internet par cette liaison et il "
            "n'y a ni box ni serveur. Les deux cartes sont en adresse automatique."
        ),
        instructions=("Donne la configuration IPv4 complète des deux PC et justifie chaque champ.",),
        criteria=(
            _c("Configuration", 1, "Adresses fixes du même réseau privé, différentes : 192.168.10.1 et 192.168.10.2 (ou équivalent) ; masque 255.255.255.0 identique."),
            _c("Justification", 1, "Pas de serveur DHCP → sinon 169.254 ; passerelle et DNS vides : réseau isolé, pas de routeur ; même masque pour être dans le même réseau."),
        ),
        correction=(
            "PC de radiographie : 192.168.10.1, masque 255.255.255.0 ; PC du dentiste : 192.168.10.2, masque 255.255.255.0 ; passerelle et DNS vides sur les deux. Toute autre paire d'adresses privées du même réseau, avec le même masque, est acceptée.",
            "En adresse automatique, faute de serveur DHCP, chaque PC prendrait une adresse 169.254.x.x. Les adresses doivent être différentes, dans le même réseau et avec le même masque ; la passerelle ne sert qu'à sortir du réseau et il n'y a pas de routeur ; aucun nom de site à résoudre : pas de DNS.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="« 0 % de perte », et pourtant…",
        question_type="document_analysis",
        requirement_ids=("AP-28",),
        kind=KIND_DIAG,
        context=(
            f"Un stagiaire teste la connexion directe entre PC-A ({PC_A.ip}/24) et le portable PC-B, "
            "qui devrait avoir 192.168.10.2. Il te montre le document 1 et conclut : « 0 % de perte, la "
            "liaison est bonne ». Les voyants de lien sont allumés."
        ),
        documents=(_console("Document 1 — Ping lancé sur PC-A (capture fictive)", *X03_LINES),),
        instructions=("Dis si le stagiaire a raison, explique le message et donne deux vérifications.",),
        criteria=(
            _c("Lecture", 1, f"Non : les réponses viennent de {PC_A.ip}, PC-A lui-même : « Impossible de joindre l'hôte » = aucune réponse ARP ; Windows les compte comme reçues."),
            _c("Vérifications", 1, "ipconfig sur PC-B (adresse réellement 192.168.10.2 ? masque ?) ; PC-B allumé, carte active ; arp -a sur PC-A ; corriger puis refaire le ping."),
        ),
        correction=(
            f"Le stagiaire se trompe. Chaque ligne est « Réponse de {PC_A.ip} : Impossible de joindre l'hôte de destination » : c'est PC-A qui répond à lui-même, faute d'avoir trouvé la MAC de 192.168.10.2 par ARP. Windows compte ces lignes comme reçues, d'où le 0 % trompeur.",
            "Personne n'a l'adresse 192.168.10.2 sur le lien : on vérifie avec ipconfig sur PC-B qu'il a bien 192.168.10.2/24 (il peut être resté en DHCP, donc en 169.254), qu'il est allumé et sa carte active ; arp -a sur PC-A ne doit montrer aucune entrée pour .2. On corrige et on refait le ping.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Défaillance générale entre deux PC",
        question_type="document_analysis",
        requirement_ids=("AP-28",),
        kind=KIND_DIAG,
        context=(
            "Deux PC d'un garage sont reliés par un câble ; les voyants sont allumés. Le document 1 donne "
            "leur configuration. Le ping de PC-A vers PC-B affiche quatre fois « PING : échec de la "
            "transmission. Défaillance générale. »"
        ),
        documents=(
            _table("Document 1 — Configuration relevée", ("Poste", "Adresse IPv4", "Masque", "Passerelle"),
                   (PC_A.name, PC_A.ip, PC_A.mask, "—"), (X04_B.name, X04_B.ip, X04_B.mask, "—")),
        ),
        instructions=("Explique le message et donne la correction.",),
        criteria=(
            _c("Explication", 1, f"{X04_B.ip} n'est pas dans le réseau 192.168.10.0/24 de PC-A ; sans passerelle, PC-A n'a aucune route : il n'émet rien → défaillance générale ({X04_OUTCOME.split(' :')[0].lower()})."),
            _c("Correction", 1, f"Mettre PC-B dans le même réseau : {PC_B.ip}/24 (ou PC-A en 192.168.1.x) ; ne pas ajouter de passerelle ; refaire le ping."),
        ),
        correction=(
            "Avec le masque /24, PC-A est dans 192.168.10.0/24 et PC-B dans 192.168.1.0/24 : le troisième octet diffère. Pour joindre une adresse d'un autre réseau, PC-A devrait passer par une passerelle ; il n'en a pas : il ne peut rien émettre, d'où « Défaillance générale ». Le câble n'est pas en cause (voyants allumés).",
            f"On place les deux PC dans le même réseau : PC-B en {PC_B.ip}, masque 255.255.255.0 (ou PC-A dans 192.168.1.0/24). Ajouter une passerelle ne servirait à rien : il n'y a pas de routeur. On refait le ping dans les deux sens.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Ping bloqué par le pare-feu",
        question_type="short_answer",
        requirement_ids=("AP-28",),
        kind=KIND_SHARE,
        context=(
            f"Après une connexion directe, le ping de PC-B vers PC-A ({PC_A.ip}) affiche quatre « Délai "
            f"d'attente de la demande dépassé. », mais arp -a sur PC-B contient {PC_A.ip} avec la MAC de "
            "PC-A. Dans les paramètres réseau de PC-A, le profil affiché est « Public »."
        ),
        instructions=("Explique la cause et les réglages à faire, puis le test de validation.",),
        criteria=(
            _c("Cause", 1, "La MAC est connue : câble et adressage bons ; PC-A reçoit la demande et ne répond pas ; profil Public (réseau non identifié, sans passerelle) → pare-feu bloque l'écho ICMP."),
            _c("Réglages et test", 1, "Profil Privé ; partage de fichiers et d'imprimantes / règle d'écho ICMPv4 activés sur ce profil ; pare-feu laissé actif ; ping de nouveau : 4 réponses."),
        ),
        correction=(
            "La présence de la MAC de PC-A dans la table ARP prouve que PC-A a répondu à la requête ARP : câble, cartes et adresses fonctionnent. Le ping n'obtient pas de réponse parce que PC-A la refuse : son pare-feu, sur le profil Public attribué à un réseau sans passerelle (« réseau non identifié »), bloque l'écho ICMP.",
            "On passe le profil réseau de PC-A en Privé et on active le partage de fichiers et d'imprimantes sur ce profil, ce qui active la règle « Demande d'écho ICMPv4 entrante » ; on ne désactive pas le pare-feu. On refait le ping : quatre réponses attendues.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Conflit d'adresse après l'ajout d'une imprimante",
        question_type="short_answer",
        requirement_ids=("AP-38",),
        kind=KIND_DIAG,
        context=(
            f"Dans un mini-réseau avec box ({BOX_IP}, étendue DHCP {POOL[0]} à {POOL[1]}), un technicien a "
            "réglé la nouvelle imprimante en adresse fixe 192.168.10.101. Le lendemain, le poste de "
            "l'accueil, en DHCP, affiche un conflit d'adresse IP et perd le réseau par moments."
        ),
        instructions=("Explique l'origine du conflit et la correction durable.",),
        criteria=(
            _c("Origine", 1, f"192.168.10.101 est dans l'étendue DHCP : la box l'a aussi donnée au poste de l'accueil → doublon ({range_of('192.168.10.101').lower()})."),
            _c("Correction", 1, "Imprimante en adresse fixe hors de l'étendue (par exemple .20) ou réservation DHCP ; renouveler l'adresse de l'accueil ; mettre à jour le plan ; tester."),
        ),
        correction=(
            f"La box distribue {POOL[0]} à {POOL[1]} : elle ignore qu'une imprimante s'est donné 192.168.10.101 à la main et l'a attribuée au poste de l'accueil. Deux appareils ont la même adresse : Windows signale le conflit et l'un des deux perd le réseau.",
            "On donne à l'imprimante une adresse fixe hors de l'étendue (plage .20 à .49, par exemple .20) ou une réservation DHCP sur la box ; on renouvelle l'adresse de l'accueil (ipconfig /renew), on reconfigure l'imprimante sur les postes si besoin, on met le plan à jour et on teste impression et ping.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Plan d'adressage d'un mini-réseau de six appareils",
        question_type="long_answer",
        requirement_ids=("AP-38",),
        kind=KIND_ADDR,
        context=(
            "Une asbl équipe son bureau : une box de l'opérateur, un PC qui partage le dossier commun, une "
            "imprimante réseau, trois postes et un portable de passage. Tout sera relié par un switch et "
            "la box doit donner Internet à tous. Tu choisis le réseau 192.168.10.0/24."
        ),
        instructions=("Propose le plan d'adressage complet (adresse, masque, passerelle, DNS, mode) et justifie.",),
        criteria=(
            _c("Plan", 1, f"Box {BOX_IP} ; PC du partage et imprimante en fixe hors étendue (.1, .20) ; postes et portable en DHCP ({POOL[0]}–{POOL[1]}) ; masque 255.255.255.0 partout ; passerelle et DNS = box."),
            _c("Justification", 1, "Adresses fixes pour ce que les autres doivent retrouver ; jamais dans l'étendue ; DHCP pour le reste (pas de saisie, pas de doublon) ; passerelle et DNS nécessaires pour Internet."),
        ),
        correction=(
            f"Box : {BOX_IP}/24, serveur DHCP pour {POOL[0]} à {POOL[1]}. PC du partage : 192.168.10.1/24 fixe, passerelle {BOX_IP}, DNS {BOX_IP}. Imprimante : 192.168.10.20/24 fixe (ou réservation), même passerelle et DNS. Trois postes et portable : DHCP, ils reçoivent une adresse de l'étendue, le masque 255.255.255.0, la passerelle et le DNS de la box.",
            "Le PC du partage et l'imprimante doivent garder la même adresse pour être retrouvés ; on les place hors de l'étendue pour éviter tout doublon. Les autres appareils en DHCP : rien à saisir, le portable fonctionne ailleurs. Toute autre répartition cohérente (box en .1 et fixes ailleurs) est acceptée si elle est justifiée.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Plus de box, plus d'adresses",
        question_type="document_analysis",
        requirement_ids=("AP-38",),
        kind=KIND_DIAG,
        context=(
            "Dans un local associatif, la box a été rendue à l'opérateur. Les quatre PC, en adresse "
            "automatique, restent reliés au switch pour s'échanger des fichiers. Depuis, plus aucun "
            "partage ne s'ouvre. Le document 1 montre l'un des postes."
        ),
        documents=(_console("Document 1 — ipconfig /all sur PC-02 (capture fictive)",
                            "C:\\> ipconfig /all", "", *ipconfig_all_lines(X08_HOST, dhcp_server=None, apipa=True)),),
        instructions=("Explique le relevé et propose la solution adaptée à ce local, avec son test.",),
        criteria=(
            _c("Explication", 1, "169.254.12.7 / 255.255.0.0, pas de passerelle : plus de serveur DHCP (c'était la box) ; le switch n'en est pas un."),
            _c("Solution", 1, "Adresses fixes d'un plan (192.168.10.1 à .4 /24, sans passerelle ni DNS) ; puis ping entre postes et ouverture du partage par l'adresse IP."),
        ),
        correction=(
            "Le poste est en DHCP, mais le serveur DHCP était la box : sans réponse, Windows s'est donné 169.254.12.7/16, sans passerelle. Le switch ne distribue aucune adresse ; les partages, qui utilisaient les anciennes adresses, ne s'ouvrent plus.",
            "Pour un local sans Internet, on fixe un plan simple : 192.168.10.1 à 192.168.10.4, masque 255.255.255.0, passerelle et DNS vides, noté et affiché. On teste par ping entre postes, puis on ouvre le partage par \\\\192.168.10.x\\Partage. (Un petit routeur DHCP serait aussi une solution, à justifier.)",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Le partage s'ouvre mais refuse l'enregistrement",
        question_type="short_answer",
        requirement_ids=("AP-28",),
        kind=KIND_SHARE,
        context=(
            f"Sur une connexion directe validée par ping, la secrétaire ouvre {SHARE_UNC} depuis son "
            "portable avec le compte « tech » de PC-A. Elle voit les fichiers mais ne peut rien enregistrer. "
            "Sur PC-A : partage Echange « Tout le monde : Lecture » ; dossier, onglet Sécurité : tech en Modification."
        ),
        instructions=("Explique la cause et la correction minimale, puis le test.",),
        criteria=(
            _c("Cause", 1, "Par le réseau, la permission effective est la plus restrictive : partage en Lecture + dossier en Modification → lecture seule."),
            _c("Correction et test", 1, "Autorisation du partage : retirer Tout le monde, tech en Modifier (Change) ; garder Modification sur le dossier ; créer et supprimer un fichier de test."),
        ),
        correction=(
            "À travers le réseau, Windows combine les autorisations du partage et celles du dossier (NTFS) et applique la plus restrictive. Le partage n'autorise que la lecture : même avec « Modification » sur le dossier, l'accès par le réseau reste en lecture seule.",
            "Dans Partage avancé → Autorisations, on retire « Tout le monde » et on donne « Modifier » au seul compte tech ; l'onglet Sécurité reste en Modification. Test depuis le portable : créer, modifier puis supprimer un fichier ; noter le résultat.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Prouver qu'un mini-réseau fonctionne",
        question_type="long_answer",
        requirement_ids=("AP-38",),
        kind=KIND_ACCEPT,
        context=(
            "Tu livres un mini-réseau de quatre postes et une imprimante autour d'un switch, avec une box "
            "pour Internet, dans une école de devoirs. La directrice veut une preuve écrite que tout "
            "fonctionne avant de payer la facture et te demande ce que tu vas vérifier, et comment."
        ),
        instructions=("Liste les contrôles dans l'ordre, la preuve de chacun, et ce que tu remets à la fin.",),
        criteria=(
            _c("Contrôles", 1, "Lien → adresse (pas 169.254) → pas de doublon → réseau et masque → arp/ping de la box et d'un autre poste → partage → impression → site par son nom ; sur chaque poste."),
            _c("Preuves et remise", 1, "Relevés (ipconfig, ping, arp -a), résultat OK/KO consigné ; plan d'adressage, schéma, procès-verbal daté et signé, réserves."),
        ),
        correction=(
            "Sur chaque poste, dans l'ordre : voyant de lien ; ipconfig (adresse prévue, pas de 169.254 ni de « (Dupliqué) », masque 255.255.255.0, passerelle et DNS de la box) ; ping de la box et d'un autre poste, MAC dans arp -a ; ouverture du partage ; impression d'une page ; ouverture d'un site par son nom. Le premier contrôle en échec est corrigé avant de continuer.",
            "Chaque résultat est noté OK/KO dans le tableau de recette avec sa preuve (relevé). On remet le plan d'adressage, le schéma du réseau et le tableau ; les mots de passe à part ; la directrice signe un procès-verbal daté, avec les réserves éventuelles.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, schémas à compléter et relevés de commandes demandés par le ticket."""
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
            errors.append(f"{item.key} : au moins une exigence du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 4:
        errors.append("Ticket #221 : au moins 4 schémas à compléter.")
    if sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) < 5:
        errors.append("Ticket #221 : au moins 5 exercices avec des sorties de commandes.")
    if (E13_FROM_A, E13_FROM_B) != (OUT_TIMEOUT, OUT_FAILURE) or not E13_ERRORS or same_network(E13_A, E13_B):
        errors.append("E13 : résultats de ping inattendus.")
    if (E19_BOX, E19_WEB) != (OUT_REPLY, OUT_FAILURE) or X03_OUTCOME != OUT_UNREACHABLE or X05_OUTCOME != OUT_TIMEOUT:
        errors.append("E19/X03/X05 : résultats de ping inattendus.")
    if len(E18_ERRORS) != 4:
        errors.append("E18 : le plan doit contenir exactement 4 erreurs.")
    if {CABLE_STRAIGHT, CABLE_CROSS, CABLE_ANY} != set(E04_ANSWERS) or X01_NEW_OLD != CABLE_ANY or X01_OLD_OLD != CABLE_CROSS:
        errors.append("E04/X01 : choix de câble incohérents.")
    if {validation_diagnosis(first_failure(k)) for _t, k in E06_CASES + E07_CASES} != {
        D_LINK, D_DHCP, D_DUP, D_PLAN, D_PEER, D_FIREWALL, D_SHARE, D_GW
    }:
        errors.append("E06/E07 : toutes les pistes doivent être utilisées.")
    if len(ADDRESS_RANGES) != 6:
        errors.append("Carte des adresses incohérente.")
    return errors

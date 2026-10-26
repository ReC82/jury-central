"""PR20 « IPv4, MAC, masques et passerelles — configuration et diagnostics écrits » — exercices
corrigés et mini-examen (ticket #199).

Même organisation que PR06, PR11, PR15 et PR16 (`app.v1.ampcr_pratique_pr06_bank`, dont ce
module réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — au moins 6 calculs d'adressage/CIDR, 5 diagnostics sur relevés,
  4 configurations de mini-réseaux et 3 comptes rendus ou procédures écrites ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Tous les calculs (réseau, diffusion, plage, nombre d'hôtes, masque ↔ préfixe, même sous-réseau,
type d'adresse, erreurs d'un plan) sont **faits par le code** (`app.v1.ampcr_pratique_pr20_figures`,
module standard `ipaddress`) et interpolés dans les énoncés, corrigés et barèmes ; les tests
du ticket les recalculent indépendamment. Situations, relevés et adresses MAC : fictifs.
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
    ADDRESS_KINDS,
    LADDER_STEPS,
    LAN_BY_NAME,
    LAN_POOL,
    LAN_ROUTER,
    LAN_SERVER,
    AddressPlan,
    Host,
    address_kind,
    binary_and_last_octet,
    host_errors,
    ip_addr_lines,
    ip_route_lines,
    ipconfig_all_lines,
    is_contiguous_mask,
    is_local_for,
    mac_is_locally_administered,
    mask_to_prefix,
    normalize_mac,
    plan_errors,
    same_subnet,
    smallest_prefix_for,
    subnet_facts,
)

PR20_CODE = "PR20"

KIND_CALC = "calcul d'adressage et CIDR"
KIND_DIAGNOSIS = "diagnostic sur relevés"
KIND_CONFIG = "configuration de mini-réseau"
KIND_REPORT = "compte rendu ou procédure écrite"
KIND_SCENARIO = "scénario"


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _facts_sentence(address: str, prefix: int) -> str:
    f = subnet_facts(address, prefix)
    return (
        f"{address}/{prefix} (masque {f.mask}) : réseau {f.network}, diffusion {f.broadcast}, "
        f"hôtes {f.first_host} à {f.last_host}, {f.total} adresses dont {f.usable} hôtes"
    )


def _plan_rows(plan: AddressPlan) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (h.name, h.ip, h.mask, h.gateway or "—", h.dns[0] if h.dns else "—", "DHCP" if h.dhcp else "fixe")
        for h in plan.hosts
    )


PLAN_HEADER = ("Équipement", "Adresse IP", "Masque", "Passerelle", "DNS", "Mode")

# =============================================================================================
# Données calculées des exercices
# =============================================================================================

# E01 : masques → préfixe (ou masque invalide).
E01_PREFIXES: tuple[int, ...] = (24, 25, 26, 27, 28, 30)
E01_CATEGORIES: tuple[str, ...] = (*(f"/{p}" for p in E01_PREFIXES), "Masque invalide (bits non contigus)")
E01_MASKS: tuple[str, ...] = (
    "255.255.255.192", "255.255.255.0", "255.255.255.252", "255.255.255.160",
    "255.255.255.240", "255.255.255.128", "255.255.255.224", "255.255.0.255",
)
E01_CORRECT: tuple[int, ...] = tuple(
    E01_PREFIXES.index(mask_to_prefix(m)) if is_contiguous_mask(m) else len(E01_PREFIXES) for m in E01_MASKS
)

# E02 : réseau, diffusion, plage, nombre d'hôtes.
E02_CASES: tuple[tuple[str, int], ...] = (
    ("172.16.5.200", 26), ("10.0.12.37", 27), ("192.168.1.130", 25), ("192.168.7.19", 28),
)
E02_FACTS = tuple(subnet_facts(a, p) for a, p in E02_CASES)

# E03 : type d'adresse.
E03_ADDRESSES: tuple[str, ...] = (
    "10.45.2.1", "172.20.0.9", "172.32.0.9", "192.168.0.254", "192.169.1.1", "169.254.12.7", "127.0.0.1", "0.0.0.0",
)
E03_CORRECT: tuple[int, ...] = tuple(ADDRESS_KINDS.index(address_kind(a)) for a in E03_ADDRESSES)

# E04 : même sous-réseau ou routeur nécessaire.
E04_CATEGORIES: tuple[str, ...] = ("Même sous-réseau : communication directe", "Sous-réseaux différents : routeur nécessaire")
E04_PAIRS: tuple[tuple[str, str, int], ...] = (
    ("192.168.1.10", "192.168.1.200", 24),
    ("192.168.1.10", "192.168.1.70", 26),
    ("10.0.0.5", "10.200.3.4", 8),
    ("172.16.1.1", "172.16.2.1", 24),
    ("192.168.5.33", "192.168.5.62", 27),
    ("192.168.5.30", "192.168.5.33", 27),
    ("192.168.0.1", "192.168.0.2", 30),
    ("192.168.0.2", "192.168.0.5", 30),
)
E04_LABELS: tuple[str, ...] = tuple(f"{a}/{p} et {b}/{p}" for a, b, p in E04_PAIRS)
E04_CORRECT: tuple[int, ...] = tuple(0 if same_subnet(a, p, b, p) else 1 for a, b, p in E04_PAIRS)

# E05 : masques différents sur le même câble.
E05_A = Host("PC-A", "poste", "192.168.1.10", 24, "192.168.1.1", ("192.168.1.1",), "3C-52-82-77-00-0A")
E05_B = Host("PC-B", "poste", "192.168.1.130", 25, "192.168.1.1", ("192.168.1.1",), "3C-52-82-77-00-0B")
E05_A_SEES_B = is_local_for(E05_A.ip, E05_A.prefix, E05_B.ip)
E05_B_SEES_A = is_local_for(E05_B.ip, E05_B.prefix, E05_A.ip)
E05_B_ERRORS = host_errors(E05_B)

# E06 : plus petit bloc adapté (hôtes = postes + équipements + passerelle).
E06_NEEDS: tuple[tuple[str, int], ...] = (
    ("Atelier : 25 postes, 1 imprimante et la passerelle", 27),
    ("Accueil : 10 postes et la passerelle", 11),
    ("Liaison entre deux routeurs", 2),
    ("Salle de formation : 60 postes et la passerelle", 61),
)
E06_PREFIXES: tuple[int, ...] = tuple(smallest_prefix_for(n) for _l, n in E06_NEEDS)

# E07 : ET logique écrit en binaire.
E07_IP, E07_MASK = "192.168.20.77", "255.255.255.224"
E07_BITS = binary_and_last_octet(E07_IP, E07_MASK)
E07_FACTS = subnet_facts(E07_IP, mask_to_prefix(E07_MASK))

# E08 : APIPA.
E08_HOST = Host("PC-03", "poste", "169.254.37.112", 16, None, (), LAN_BY_NAME["PC-03"].mac, dhcp=True)

# E09 : DNS erroné (adresse fixe).
E09_HOST = Host("PC-07", "poste", "192.168.10.30", 24, LAN_ROUTER, ("192.168.10.50",), "3C-52-82-1A-2B-07")

# E10 : Linux sans route par défaut.
E10_HOST = Host("PC-04", "poste Linux", "192.168.10.104", 24, None, (LAN_SERVER,), LAN_BY_NAME["PC-04"].mac)

# E11 : mauvaise passerelle (dans le réseau, mais aucun routeur à cette adresse).
E11_HOST = Host("PC-08", "poste", "192.168.10.31", 24, "192.168.10.254", (LAN_SERVER,), "3C-52-82-1A-2B-08")

# E12 : doublon (imprimante fixe dans l'étendue DHCP).
E12_PRINTER = Host("IMP-01", "imprimante", "192.168.10.103", 24, LAN_ROUTER, (LAN_SERVER,), "00-80-77-5C-21-9A")
E12_PLAN = AddressPlan(
    "192.168.10.0/24",
    (LAN_BY_NAME["Routeur"], LAN_BY_NAME["SRV-01"], LAN_BY_NAME["PC-03"], E12_PRINTER),
    LAN_ROUTER, LAN_SERVER, LAN_POOL,
)
E12_ERRORS = plan_errors(E12_PLAN)

# E13 : plan de référence proposé pour un cabinet (validé : aucune erreur).
E13_PLAN = AddressPlan(
    "192.168.50.0/24",
    (
        Host("Box", "routeur, DHCP, DNS", "192.168.50.1", 24, None, (), "00-1D-AA-50-00-01"),
        Host("PC-1", "poste", "192.168.50.100", 24, "192.168.50.1", ("192.168.50.1",), "3C-52-82-50-00-11", dhcp=True),
        Host("PC-2", "poste", "192.168.50.101", 24, "192.168.50.1", ("192.168.50.1",), "3C-52-82-50-00-12", dhcp=True),
        Host("PC-3", "poste", "192.168.50.102", 24, "192.168.50.1", ("192.168.50.1",), "3C-52-82-50-00-13", dhcp=True),
        Host("Imprimante", "réseau", "192.168.50.10", 24, "192.168.50.1", ("192.168.50.1",), "00-80-77-50-00-14"),
        Host("NAS", "stockage", "192.168.50.11", 24, "192.168.50.1", ("192.168.50.1",), "00-11-32-50-00-15"),
    ),
    "192.168.50.1", "192.168.50.1", ("192.168.50.100", "192.168.50.199"),
)
E13_ERRORS = plan_errors(E13_PLAN)

# E14 : plan erroné à relire.
E14_PLAN = AddressPlan(
    "192.168.20.0/24",
    (
        Host("Routeur", "passerelle, DNS", "192.168.20.254", 24, None, (), "00-1D-AA-20-00-FE"),
        Host("PC-A", "poste", "192.168.20.10", 24, "192.168.20.254", ("192.168.20.254",), "3C-52-82-20-00-0A"),
        Host("PC-B", "poste", "192.168.20.0", 24, "192.168.20.254", ("192.168.20.254",), "3C-52-82-20-00-0B"),
        Host("PC-C", "poste", "192.168.20.10", 24, "192.168.20.254", ("192.168.20.254",), "3C-52-82-20-00-0C"),
        Host("Imprimante", "réseau", "192.168.20.60", 24, "192.168.20.254", ("192.168.20.254",), "00-80-77-20-00-0D"),
        Host("NAS", "stockage", "192.168.20.30", 16, "192.168.20.254", ("192.168.20.254",), "00-11-32-20-00-0E"),
        Host("PC-D", "poste", "192.168.20.31", 24, "192.168.21.254", ("192.168.20.254",), "3C-52-82-20-00-0F"),
        Host("Portable", "poste", "192.168.20.255", 24, "192.168.20.254", ("192.168.20.254",), "3C-52-82-20-00-10"),
    ),
    "192.168.20.254", "192.168.20.254", ("192.168.20.50", "192.168.20.150"),
)
E14_ERRORS = plan_errors(E14_PLAN)

# E15 : connexion directe de deux PC.
E15_A = ("192.168.1.10", 24)
E15_B = ("192.168.2.20", 24)
E15_B_FIXED = ("192.168.1.20", 24)

# E16 : NAS à configurer en adresse fixe (Windows et Linux).
E16_HOST = Host("SRV-02", "serveur de fichiers", "192.168.10.21", 24, LAN_ROUTER, (LAN_SERVER,), "00-15-5D-0A-0B-21")

# E17 : étapes de la démarche de test, affichées dans le désordre.
E17_SHOWN: tuple[int, ...] = (4, 2, 6, 0, 5, 3, 1)

# E20 : identification MAC.
E20_PHONE_MAC = "F6-3B-9C-12-4E-70"

# Mini-examen.
X01_FACTS = subnet_facts("10.20.30.140", 26)
X02_MASK, X02_BAD_MASK = "255.255.255.240", "255.255.255.208"
X02_PREFIX = mask_to_prefix(X02_MASK)
X02_FACTS = subnet_facts("192.168.0.1", X02_PREFIX)
X03_A, X03_B, X03_P = "192.168.4.100", "192.168.4.140", 25
X06_HOST = Host("POSTE-L2", "poste Linux", "192.168.1.42", 24, "192.168.1.254", ("192.168.1.1",), "52-54-00-6B-11-42")
X07_A, X07_B, X07_P = "172.16.0.1", "172.17.0.2", 16
X08_PLAN = AddressPlan(
    "192.168.30.0/24",
    (
        Host("Box", "routeur, DHCP, DNS", "192.168.30.1", 24, None, (), "00-1D-AA-30-00-01"),
        Host("Poste 1", "poste", "192.168.30.100", 24, "192.168.30.1", ("192.168.30.1",), "3C-52-82-30-00-01", dhcp=True),
        Host("Poste 2", "poste", "192.168.30.101", 24, "192.168.30.1", ("192.168.30.1",), "3C-52-82-30-00-02", dhcp=True),
        Host("Poste 3", "poste", "192.168.30.102", 24, "192.168.30.1", ("192.168.30.1",), "3C-52-82-30-00-03", dhcp=True),
        Host("Poste 4", "poste", "192.168.30.103", 24, "192.168.30.1", ("192.168.30.1",), "3C-52-82-30-00-04", dhcp=True),
        Host("Imprimante", "réseau", "192.168.30.20", 24, "192.168.30.1", ("192.168.30.1",), "00-80-77-30-00-05"),
    ),
    "192.168.30.1", "192.168.30.1", ("192.168.30.100", "192.168.30.150"),
)
X09_PC3 = ("192.168.40.13", 16)
X09_SERVER = "192.168.41.10"
X09_OTHERS = ("192.168.40.11", 24)


# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Masque ou préfixe : quelle écriture ?",
        question_type="classification",
        requirement_ids=("AP-30",),
        kind=KIND_CALC,
        context=(
            "Tu reprends la documentation d'un réseau d'école où les masques ont été notés de "
            "deux façons différentes. Avant de convertir toute la documentation en notation "
            "CIDR (/n), tu vérifies huit masques relevés sur les fiches des postes ; certains "
            "ont pu être mal recopiés."
        ),
        instructions=("Associe chaque masque à son préfixe, ou indique qu'il est invalide.",),
        criteria=(
            _c("Classement", 8, "255.255.255.192 = /26 ; .0 = /24 ; .252 = /30 ; .160 invalide ; .240 = /28 ; .128 = /25 ; .224 = /27 ; 255.255.0.255 invalide (1 point par masque)."),
        ),
        correction=(
            "On compte les bits à 1 de gauche à droite : 255 = 8 bits, 128 = 1, 192 = 2, 224 = 3, 240 = 4, 248 = 5, 252 = 6. Donc 255.255.255.0 = /24, .128 = /25, .192 = /26, .224 = /27, .240 = /28, .252 = /30.",
            "Un masque valide a tous ses 1 à gauche puis uniquement des 0. 160 = 10100000 (un 0 entre deux 1) et 255.255.0.255 (des 1 après des 0) sont donc invalides : erreur de recopie à faire corriger.",
        ),
        classification=Classification(categories=E01_CATEGORIES, elements=E01_MASKS, correct=E01_CORRECT),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Réseau, diffusion et plage de quatre postes",
        question_type="document_analysis",
        requirement_ids=("AP-30",),
        kind=KIND_CALC,
        context=(
            "Un prestataire a découpé le réseau d'une PME en petits sous-réseaux et t'a laissé "
            "la liste des adresses de quatre postes avec leur préfixe (document 1). Pour mettre "
            "à jour le plan d'adressage, tu dois retrouver pour chacun le réseau, la diffusion, "
            "la plage d'hôtes et le nombre d'hôtes utilisables."
        ),
        instructions=(
            "Pour chaque poste, calcule le masque décimal, l'adresse de réseau et l'adresse de diffusion.",
            "Donne la première et la dernière adresse d'hôte et le nombre d'hôtes utilisables, en montrant ton calcul.",
        ),
        documents=(_table("Document 1 — Adresses relevées (fictives)", ("Poste", "Adresse/préfixe"),
                          *((f"Poste {i}", f"{a}/{p}") for i, (a, p) in enumerate(E02_CASES, start=1))),),
        criteria=tuple(
            _c(f"Poste {i}", 1, f"{f.address}/{f.prefix} : masque {f.mask}, réseau {f.network}, diffusion {f.broadcast}, hôtes {f.first_host} à {f.last_host} ({f.usable}).")
            for i, f in enumerate(E02_FACTS, start=1)
        ),
        correction=(
            "Méthode : taille du bloc = 2^(32 − préfixe) dans l'octet où passe la frontière (/25 : 128, /26 : 64, /27 : 32, /28 : 16). Le réseau est le multiple du bloc juste inférieur ou égal à l'octet de l'adresse ; la diffusion = réseau + bloc − 1 ; les hôtes sont entre les deux ; nombre d'hôtes = bloc − 2.",
            *(f"Poste {i} : {_facts_sentence(f.address, f.prefix)}." for i, f in enumerate(E02_FACTS, start=1)),
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Quelle sorte d'adresse ?",
        question_type="classification",
        requirement_ids=("AP-30",),
        kind=KIND_CALC,
        context=(
            "En préparant un dossier de dépannage, tu as relevé huit adresses IPv4 dans des "
            "captures d'écran de clients (configuration de cartes, journaux de box, messages "
            "d'erreur). Pour chacune, tu dois dire de quelle sorte d'adresse il s'agit avant "
            "d'interpréter la situation du poste."
        ),
        instructions=("Classe chaque adresse dans sa catégorie.",),
        criteria=(
            _c("Classement", 8, "10.45.2.1, 172.20.0.9, 192.168.0.254 privées ; 172.32.0.9 et 192.169.1.1 publiques ; 169.254.12.7 lien local (APIPA) ; 127.0.0.1 bouclage ; 0.0.0.0 non spécifiée (1 point par adresse)."),
        ),
        correction=(
            "Plages privées (RFC 1918) : 10.0.0.0/8, 172.16.0.0/12 (de 172.16.0.0 à 172.31.255.255) et 192.168.0.0/16. 172.32.0.9 est juste après la plage 172.16/12 et 192.169.1.1 juste après 192.168/16 : ce sont des adresses publiques — pièges classiques.",
            "169.254.0.0/16 : adresses de lien local, attribuées automatiquement (APIPA) quand aucun serveur DHCP ne répond. 127.0.0.1 : bouclage, le poste lui-même. 0.0.0.0 : adresse non spécifiée (par exemple l'adresse source d'un client DHCP qui n'a pas encore de bail, ou « toutes les adresses » selon le contexte), jamais l'adresse d'un poste.",
        ),
        classification=Classification(categories=ADDRESS_KINDS, elements=E03_ADDRESSES, correct=E03_CORRECT),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Même réseau ou routeur nécessaire ?",
        question_type="classification",
        requirement_ids=("AP-30", "AP-31"),
        kind=KIND_CALC,
        context=(
            "Un client veut savoir quels postes de ses différents sites peuvent se joindre "
            "directement à travers un switch et lesquels ont besoin d'un routeur. Tu as relevé "
            "huit paires d'adresses ; dans chaque paire, les deux postes ont le même préfixe."
        ),
        instructions=("Classe chaque paire : même sous-réseau, ou sous-réseaux différents (routeur nécessaire).",),
        criteria=(
            _c("Classement", 8, "Même sous-réseau : paires 1, 3, 5 et 7 ; sous-réseaux différents : paires 2, 4, 6 et 8 (1 point par paire)."),
        ),
        correction=(
            "On calcule le réseau de chaque adresse avec le préfixe donné ; même réseau = communication directe (ARP sur le switch), réseaux différents = passage par la passerelle.",
            *(
                f"{a}/{p} → {subnet_facts(a, p).network} ; {b}/{p} → {subnet_facts(b, p).network} : "
                + ("même réseau." if same_subnet(a, p, b, p) else "réseaux différents.")
                for a, b, p in E04_PAIRS
            ),
        ),
        classification=Classification(categories=E04_CATEGORIES, elements=E04_LABELS, correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Deux masques différents sur le même switch",
        question_type="short_answer",
        requirement_ids=("AP-30", "AP-37"),
        kind=KIND_CALC,
        context=(
            f"Dans un bureau, deux postes sont branchés sur le même switch. PC-A : {E05_A.ip}, masque "
            f"{E05_A.mask}, passerelle {E05_A.gateway}. PC-B : {E05_B.ip}, masque {E05_B.mask}, "
            f"passerelle {E05_B.gateway}. Les échanges entre eux sont instables et PC-B n'accède "
            "à rien en dehors du bureau."
        ),
        instructions=(
            "Pour chaque poste, indique si l'autre lui paraît local ou distant, avec le calcul.",
            "Explique la conséquence et propose la correction.",
        ),
        criteria=(
            _c("Vue de chaque poste", 1, f"PC-A ({subnet_facts(E05_A.ip, E05_A.prefix).cidr}) voit PC-B local ; PC-B ({subnet_facts(E05_B.ip, E05_B.prefix).cidr}) voit PC-A distant."),
            _c("Conséquence et correction", 1, f"PC-B envoie ses réponses vers sa passerelle, qui est hors de son réseau ({E05_B.gateway}) : configuration incohérente ; donner à PC-B le masque {E05_A.mask} (/24) comme le reste du réseau, puis tester."),
        ),
        correction=(
            f"PC-A : réseau {subnet_facts(E05_A.ip, E05_A.prefix).cidr} ; {E05_B.ip} en fait partie → PC-B est local (envoi direct). PC-B : réseau {subnet_facts(E05_B.ip, E05_B.prefix).cidr} (hôtes {subnet_facts(E05_B.ip, E05_B.prefix).host_range}) ; {E05_A.ip} n'en fait pas partie → PC-A est distant pour PC-B.",
            f"PC-B doit donc passer par sa passerelle pour répondre à PC-A et pour sortir ; or {E05_B.gateway} n'est pas dans son propre réseau : passerelle injoignable, configuration incohérente (comportement imprévisible selon le système). Correction : masque {E05_A.mask} sur PC-B, comme sur tout le réseau ; puis ping de PC-A, de la passerelle et d'une adresse distante.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Choisir la taille des sous-réseaux",
        question_type="short_answer",
        requirement_ids=("AP-30", "AP-38"),
        kind=KIND_CALC,
        context=(
            "Un centre de formation veut découper son adressage privé en sous-réseaux distincts, "
            "chacun le plus petit possible sans manquer d'adresses. Chaque besoin compte déjà la "
            "passerelle quand il y en a une : " + " ; ".join(f"{label}" for label, _n in E06_NEEDS) + "."
        ),
        instructions=(
            "Pour chaque besoin, donne le plus long préfixe possible (plus petit bloc) et le masque correspondant.",
            "Justifie avec le nombre d'hôtes utilisables du bloc choisi.",
        ),
        criteria=tuple(
            _c(label.split(" :")[0], 0.5,
               f"/{p} ({subnet_facts('10.0.0.0', p).mask}) : {subnet_facts('10.0.0.0', p).usable} hôtes pour {n} adresses nécessaires.")
            for (label, n), p in zip(E06_NEEDS, E06_PREFIXES, strict=True)
        ),
        correction=(
            "Nombre d'hôtes utilisables d'un bloc = 2^(bits d'hôte) − 2 (adresse de réseau et de diffusion retirées). On prend le plus petit bloc qui suffit.",
            *(
                f"{label} : {n} adresses → /{p} ({subnet_facts('10.0.0.0', p).mask}), {subnet_facts('10.0.0.0', p).usable} hôtes"
                + (f" ; /{p + 1} n'en offre que {subnet_facts('10.0.0.0', p + 1).usable}." if p < 30 else " : le /30 est le bloc usuel d'une liaison point à point.")
                for (label, n), p in zip(E06_NEEDS, E06_PREFIXES, strict=True)
            ),
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Le ET logique, bit à bit",
        question_type="short_answer",
        requirement_ids=("AP-30",),
        kind=KIND_CALC,
        context=(
            f"Pour vérifier un calcul contesté par un collègue, tu dois montrer par écrit comment "
            f"on obtient l'adresse de réseau du poste {E07_IP} dont le masque est {E07_MASK}. "
            "Les trois premiers octets du masque valent 255 : seul le dernier octet demande un calcul."
        ),
        instructions=(
            "Écris en binaire le dernier octet de l'adresse et du masque, puis le résultat du ET logique.",
            "Déduis-en l'adresse de réseau, la diffusion et la plage d'hôtes.",
        ),
        criteria=(
            _c("ET logique", 1, f"{E07_BITS[0]} ET {E07_BITS[1]} = {E07_BITS[2]} = {E07_BITS[3]}."),
            _c("Réseau, diffusion, plage", 1, f"Réseau {E07_FACTS.network}/{E07_FACTS.prefix}, diffusion {E07_FACTS.broadcast}, hôtes {E07_FACTS.host_range}."),
        ),
        correction=(
            f"77 = {E07_BITS[0]} ; 224 = {E07_BITS[1]}. ET bit à bit (1 seulement si les deux bits valent 1) : {E07_BITS[2]} = {E07_BITS[3]}.",
            f"Réseau {E07_FACTS.network} (/{E07_FACTS.prefix}). Diffusion : bits d'hôte (les 5 derniers) à 1 → {E07_FACTS.broadcast}. Hôtes : {E07_FACTS.host_range}, soit {E07_FACTS.usable}.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Un poste en 169.254",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            f"Dans le réseau de référence du cours ({LAN_ROUTER} passerelle, DHCP et DNS sur "
            f"{LAN_SERVER}), l'utilisatrice de PC-03 n'accède plus ni aux partages ni à Internet "
            "depuis ce matin. Les autres postes fonctionnent. Tu relèves la configuration (document 1)."
        ),
        instructions=(
            "Interprète le relevé.",
            "Propose, dans l'ordre, les hypothèses et les tests à réaliser, puis la correction et la vérification.",
        ),
        documents=(_console("Document 1 — ipconfig /all sur PC-03 (fictif)", "C:\\> ipconfig /all", "",
                            *ipconfig_all_lines(E08_HOST, apipa=True)),),
        criteria=(
            _c("Interprétation", 0.75, "Adresse 169.254.x.y (APIPA), masque 255.255.0.0, aucune passerelle : DHCP activé mais aucun bail reçu."),
            _c("Hypothèses et tests ordonnés", 0.75, "Lien (câble, prise, port, carte), puis échange DHCP (ipconfig /release puis /renew, autre prise), puis serveur (les autres postes ont un bail, donc le serveur répond : cause locale probable)."),
            _c("Correction et vérification", 0.5, "Corriger la cause (câble, port, carte), renouveler, vérifier IP du réseau 192.168.10.0/24, passerelle et DNS, ping passerelle, ping d'un nom."),
        ),
        correction=(
            "La carte est en DHCP (« DHCP activé : Oui ») mais porte une adresse 169.254.37.112 avec un masque 255.255.0.0 et aucune passerelle : c'est une adresse APIPA que Windows s'attribue quand aucun serveur DHCP ne répond. Elle ne permet de joindre que d'autres postes en APIPA : ni le serveur, ni la passerelle, ni Internet.",
            "Les autres postes ont un bail : le serveur DHCP fonctionne. On cherche donc près de PC-03 : 1) lien (voyant, câble bien enfiché, essai sur une autre prise ou un autre port du switch, carte activée) ; 2) ipconfig /release puis ipconfig /renew pour relancer l'échange DHCP ; 3) si l'échec persiste avec un lien correct, pare-feu ou configuration du port (VLAN). L'APIPA est un indice, pas une preuve : il faut tester.",
            "Après correction (par exemple remplacement d'un cordon défectueux), ipconfig /all doit montrer une adresse de l'étendue 192.168.10.100–199, masque 255.255.255.0, passerelle 192.168.10.1, DNS 192.168.10.5 ; ping de la passerelle et d'un nom réussis ; accès aux partages vérifié avec l'utilisatrice.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Internet « en panne » mais le ping par adresse répond",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-32", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Un comptable signale qu'« Internet ne marche plus » sur PC-07, configuré en adresse "
            f"fixe la semaine dernière par un stagiaire. Le serveur DNS du réseau est {LAN_SERVER} ; "
            "aucune machine n'utilise l'adresse 192.168.10.50. Tu relèves la configuration et "
            "réalises trois tests (document 1)."
        ),
        instructions=(
            "Situe la panne en interprétant chaque test.",
            "Nomme la cause, la correction et la vérification.",
        ),
        documents=(_console(
            "Document 1 — Relevé et tests sur PC-07 (fictifs)",
            "C:\\> ipconfig /all", "", *ipconfig_all_lines(E09_HOST), "",
            f"C:\\> ping {LAN_ROUTER}", f"Réponse de {LAN_ROUTER} : octets=32 temps<1ms TTL=64",
            "C:\\> ping 9.9.9.9", "Réponse de 9.9.9.9 : octets=32 temps=14 ms TTL=58",
            "C:\\> nslookup www.exemple.be", "DNS request timed out.",
            "    timeout was 2 seconds.", "Serveur :   UnKnown", "Address:  192.168.10.50",
        ),),
        criteria=(
            _c("Interprétation des tests", 0.75, "Passerelle joignable (réseau local OK), IP distante joignable (routage et Internet OK), résolution de nom en échec."),
            _c("Cause", 0.75, f"Serveur DNS erroné : 192.168.10.50 au lieu de {LAN_SERVER} ; ce n'est pas une panne d'Internet."),
            _c("Correction et vérification", 0.5, f"Mettre {LAN_SERVER} comme DNS (ou repasser en DHCP), vider le cache (ipconfig /flushdns), nslookup et navigation réussis."),
        ),
        correction=(
            "ping de la passerelle : le réseau local fonctionne. ping 9.9.9.9 : le routage vers Internet fonctionne. nslookup échoue en interrogeant 192.168.10.50 : la résolution des noms est en cause, pas Internet.",
            f"Le DNS configuré (192.168.10.50) n'existe pas ; le bon serveur est {LAN_SERVER}. Erreur de saisie lors de la configuration fixe.",
            f"Correction : DNS préféré {LAN_SERVER} (ou retour en DHCP si le poste n'a pas besoin d'une adresse fixe), ipconfig /flushdns. Vérification : nslookup www.exemple.be répond par le serveur {LAN_SERVER}, navigation rétablie ; noter la modification dans la fiche du poste.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Un poste Linux qui ne sort pas du réseau",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Sur PC-04 (Linux), un technicien a modifié la configuration réseau à la main pour un "
            "test. Depuis, le poste joint le serveur de fichiers du réseau local mais plus aucun "
            f"site extérieur. La passerelle du réseau est {LAN_ROUTER}. Tu relèves la configuration "
            "et fais deux tests (document 1)."
        ),
        instructions=(
            "Interprète les relevés et les tests ; nomme ce qui manque.",
            "Donne une correction immédiate et explique comment la rendre durable.",
        ),
        documents=(_console(
            "Document 1 — PC-04 (fictif)",
            *ip_addr_lines(E10_HOST), "", *ip_route_lines(E10_HOST), "",
            f"$ ping -c 1 {LAN_SERVER}", f"64 bytes from {LAN_SERVER}: icmp_seq=1 ttl=64 time=0.4 ms",
            "$ ping -c 1 9.9.9.9", "ping: connect: Network is unreachable",
        ),),
        criteria=(
            _c("Interprétation", 1, "Adresse et route locale correctes ; aucune ligne « default via » : pas de route par défaut (passerelle), d'où « Network is unreachable » pour toute adresse hors de 192.168.10.0/24."),
            _c("Correction immédiate", 0.5, f"sudo ip route add default via {LAN_ROUTER} (temporaire, perdue au redémarrage) ; puis ping 9.9.9.9 et ping d'un nom."),
            _c("Correction durable", 0.5, "Corriger la passerelle dans l'outil de configuration de la distribution (NetworkManager, Netplan…) ou repasser en DHCP ; redémarrer l'interface et re-vérifier ip route."),
        ),
        correction=(
            f"ip addr : l'interface est active (UP) avec {E10_HOST.ip}/24 ; ip route ne contient que la route locale {subnet_facts(E10_HOST.ip, 24).cidr} : aucune route par défaut. Le poste joint donc son réseau local (ping du serveur réussi) mais ne sait pas où envoyer le reste : « Network is unreachable ».",
            f"Correction immédiate : sudo ip route add default via {LAN_ROUTER} dev enp3s0 ; vérifier ip route (ligne « default via {LAN_ROUTER} »), ping 9.9.9.9 puis ping d'un nom. Cette commande est temporaire : elle disparaît au redémarrage.",
            "Correction durable : renseigner la passerelle dans la configuration persistante utilisée par la distribution (NetworkManager — nmcli ou interface graphique —, Netplan sur Ubuntu serveur…) ou repasser en DHCP ; il n'y a pas de commande universelle. Re-vérifier après redémarrage de l'interface.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="La passerelle qui ne répond pas",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-31", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Un poste neuf, PC-08, a été configuré en adresse fixe d'après une ancienne fiche. Il "
            f"accède aux partages du serveur {LAN_SERVER} mais pas à Internet ; les autres postes "
            f"n'ont aucun problème. Le routeur du réseau est {LAN_ROUTER}. Tu relèves la "
            "configuration et réalises des tests (document 1)."
        ),
        instructions=(
            "Interprète les relevés et nomme l'erreur.",
            "Explique pourquoi le réseau local fonctionne quand même, puis corrige et vérifie.",
        ),
        documents=(_console(
            "Document 1 — Relevé et tests sur PC-08 (fictifs)",
            "C:\\> ipconfig /all", "", *ipconfig_all_lines(E11_HOST), "",
            f"C:\\> ping {LAN_SERVER}", f"Réponse de {LAN_SERVER} : octets=32 temps<1ms TTL=128",
            "C:\\> ping 192.168.10.254", "Réponse de 192.168.10.31 : Impossible de joindre",
            "  l'hôte de destination.",
            "C:\\> arp -a", "  Adresse Internet   Adresse physique   Type",
            f"  {LAN_ROUTER}       00-1d-aa-4e-10-01  dynamique",
            f"  {LAN_SERVER}       00-15-5d-0a-0b-05  dynamique",
        ),),
        criteria=(
            _c("Erreur", 0.75, f"Passerelle 192.168.10.254 au lieu de {LAN_ROUTER} : aucune machine ne répond à cette adresse (pas d'entrée ARP, « impossible de joindre l'hôte »)."),
            _c("Pourquoi le local fonctionne", 0.5, "Le serveur est dans le même réseau /24 : envoi direct sans passerelle ; seule la sortie du réseau utilise la passerelle."),
            _c("Correction et vérification", 0.75, f"Passerelle {LAN_ROUTER} (ou DHCP) ; ping {LAN_ROUTER}, ping 9.9.9.9, ping d'un nom ; mise à jour de la fiche."),
        ),
        correction=(
            f"IP et masque sont corrects ({E11_HOST.ip}/24). La passerelle 192.168.10.254 est bien dans le réseau, mais aucune machine n'y répond : le ping renvoie « Impossible de joindre l'hôte de destination » (le poste n'obtient pas d'adresse MAC par ARP) et la table ARP ne la contient pas. Le vrai routeur est {LAN_ROUTER} : passerelle erronée, recopiée d'une ancienne fiche.",
            f"Le serveur {LAN_SERVER} est dans le même réseau 192.168.10.0/24 : le poste lui envoie les paquets directement, sans passerelle. Seuls les paquets destinés à un autre réseau (Internet) passent par la passerelle, d'où la panne partielle.",
            f"Correction : passerelle {LAN_ROUTER} (ou repasser en DHCP). Vérification : ping {LAN_ROUTER}, ping 9.9.9.9, ping d'un nom, navigation ; corriger la fiche pour éviter que l'erreur se reproduise.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Conflit d'adresse IP après l'installation d'une imprimante",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Depuis l'installation d'une nouvelle imprimante réseau, PC-03 affiche par moments "
            "« Windows a détecté un conflit d'adresses IP » et perd le réseau ; l'impression est "
            f"aussi aléatoire. L'étendue DHCP du serveur va de {LAN_POOL[0]} à {LAN_POOL[1]}. Tu "
            "relèves les informations utiles (document 1)."
        ),
        instructions=(
            "Explique le conflit à partir des relevés.",
            "Propose une correction durable et les vérifications.",
        ),
        documents=(
            _table("Document 1 — Relevés (fictifs)", ("Source", "Information"),
                   ("ipconfig /all sur PC-03", f"IPv4 192.168.10.103 (bail DHCP) · MAC {normalize_mac(LAN_BY_NAME['PC-03'].mac)}"),
                   ("Menu de l'imprimante IMP-01", f"IP fixe 192.168.10.103 · masque 255.255.255.0 · MAC {normalize_mac(E12_PRINTER.mac)}"),
                   ("arp -a sur PC-01, après ping 192.168.10.103", f"192.168.10.103 → {normalize_mac(E12_PRINTER.mac).lower()} (dynamique)")),
        ),
        criteria=(
            _c("Explication", 1, "Doublon : l'imprimante a reçu à la main l'adresse 192.168.10.103, qui est dans l'étendue DHCP et que le serveur a attribuée à PC-03 ; deux MAC répondent pour la même IP (arp -a montre celle de l'imprimante)."),
            _c("Correction durable", 0.5, "Adresse fixe de l'imprimante hors de l'étendue (par exemple 192.168.10.25, non utilisée) ou réservation DHCP par sa MAC ; noter dans le plan."),
            _c("Vérifications", 0.5, "ipconfig /release puis /renew sur PC-03, plus de message de conflit, ping et impression vers la nouvelle adresse, arp -a cohérent."),
        ),
        correction=(
            f"Le relevé montre la même adresse 192.168.10.103 sur deux machines de MAC différentes. L'imprimante a été configurée à la main avec une adresse de l'étendue DHCP ({LAN_POOL[0]}–{LAN_POOL[1]}) ; le serveur, qui l'ignorait, l'a aussi attribuée à PC-03. Contrôles calculés : " + " ".join(E12_ERRORS),
            "Selon la machine qui répond la dernière à l'ARP, les paquets vont à l'une ou à l'autre : coupures et impression aléatoire. arp -a sur PC-01 montre ici la MAC de l'imprimante.",
            "Correction durable : donner à l'imprimante une adresse fixe hors de l'étendue et libre (par exemple 192.168.10.25 si le plan la note libre) ou créer une réservation DHCP liée à sa MAC. Puis ipconfig /release et /renew sur PC-03, mise à jour du port d'impression sur les postes, test d'impression, plan d'adressage mis à jour.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Plan d'adressage d'un petit cabinet",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-38"),
        kind=KIND_CONFIG,
        context=(
            "Un cabinet de kinésithérapie installe un petit réseau : une box (routeur, serveur "
            "DHCP et DNS) d'adresse 192.168.50.1/24, trois PC, une imprimante réseau et un NAS. "
            "L'étendue DHCP de la box va de 192.168.50.100 à 192.168.50.199. L'imprimante et le "
            "NAS doivent garder toujours la même adresse."
        ),
        instructions=(
            "Propose un plan d'adressage : pour chaque équipement, mode (DHCP ou fixe), adresse, masque, passerelle et DNS.",
            "Justifie tes choix et cite trois erreurs que ton plan évite.",
        ),
        criteria=(
            _c("Paramètres communs", 1, "Masque 255.255.255.0 partout, passerelle 192.168.50.1, DNS 192.168.50.1 (box)."),
            _c("Postes et équipements fixes", 1.5, "PC en DHCP (adresses de l'étendue) ; imprimante et NAS en adresses fixes dans le réseau mais hors de l'étendue (par exemple 192.168.50.10 et .11), ou réservations DHCP."),
            _c("Erreurs évitées", 1.5, "Pas de doublon, pas d'adresse fixe dans l'étendue, pas d'adresse de réseau (.0) ni de diffusion (.255), passerelle dans le réseau ; plan écrit et tenu à jour."),
        ),
        correction=(
            "Paramètres communs : réseau 192.168.50.0/24, masque 255.255.255.0, passerelle et DNS 192.168.50.1 (la box). Toute autre proposition cohérente est acceptée.",
            "Plan proposé : " + " ; ".join(f"{h.name} {h.ip}/{h.prefix} ({'DHCP' if h.dhcp else 'fixe'})" for h in E13_PLAN.hosts) + ". Les PC reçoivent leurs paramètres de la box (adresses à titre d'exemple, elles peuvent varier).",
            "Imprimante et NAS : adresses fixes 192.168.50.10 et 192.168.50.11, hors de l'étendue 100–199, ou réservations DHCP liées à leur MAC (même résultat, gestion centralisée).",
            "Erreurs évitées : doublon avec un bail DHCP, adresse 192.168.50.0 (réseau) ou 192.168.50.255 (diffusion), passerelle hors du réseau, masques différents. Contrôle du plan par calcul : " + ("aucune erreur." if not E13_ERRORS else " ".join(E13_ERRORS)),
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Relire un plan d'adressage plein d'erreurs",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-38"),
        kind=KIND_CONFIG,
        context=(
            "Avant de reconfigurer un réseau de PME, tu reçois le plan d'adressage préparé par un "
            "collègue (document 1). Le réseau est 192.168.20.0/24, le routeur (passerelle et DNS) "
            "est 192.168.20.254 et l'étendue DHCP va de 192.168.20.50 à 192.168.20.150 ; tous les "
            "équipements du tableau sont configurés à la main."
        ),
        instructions=(
            "Relève chaque erreur du plan en expliquant sa conséquence.",
            "Propose une valeur corrigée pour chaque ligne fautive.",
        ),
        documents=(_table("Document 1 — Plan d'adressage proposé (fictif)", PLAN_HEADER, *_plan_rows(E14_PLAN)),),
        criteria=(
            _c("PC-B et Portable", 1, "PC-B a l'adresse du réseau (.0) et le Portable l'adresse de diffusion (.255) : adresses non attribuables à un hôte."),
            _c("PC-C", 0.75, "Doublon de 192.168.20.10 avec PC-A : conflit, coupures."),
            _c("Imprimante", 0.75, "Adresse fixe 192.168.20.60 dans l'étendue DHCP : doublon possible avec un bail."),
            _c("NAS et PC-D", 1, "NAS en /16 (masque 255.255.0.0) : voit 192.168.x.y comme local ; PC-D : passerelle 192.168.21.254 hors de son réseau, injoignable."),
            _c("Corrections", 0.5, "Adresses libres hors étendue (par exemple .11, .12, .13, .14), masque 255.255.255.0, passerelle 192.168.20.254 pour tous."),
        ),
        correction=(
            "Erreurs calculées : " + " ".join(E14_ERRORS),
            "Conséquences : l'adresse de réseau et celle de diffusion ne désignent pas un poste (PC-B et Portable sans communication) ; le doublon PC-A / PC-C provoque des conflits ; l'imprimante peut entrer en conflit avec un poste en DHCP ; le NAS en /16 croit locales des adresses qui ne le sont pas et ne passe pas par la passerelle pour elles ; PC-D ne peut pas joindre sa passerelle, donc rien hors du réseau.",
            "Corrections possibles (hors étendue 50–150 et non utilisées) : PC-B 192.168.20.11, PC-C 192.168.20.12, Imprimante 192.168.20.13, Portable 192.168.20.14 ; NAS masque 255.255.255.0 ; PC-D passerelle 192.168.20.254. Toute autre adresse libre, hors étendue, est acceptée.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Relier deux PC directement",
        question_type="long_answer",
        requirement_ids=("AP-28", "AP-30"),
        kind=KIND_CONFIG,
        context=(
            "Un photographe veut copier rapidement des fichiers entre son PC fixe et son portable "
            "en les reliant par un câble Ethernet, sans switch ni box. Les deux cartes gèrent "
            f"l'Auto MDI-X. Il a déjà saisi : PC fixe {E15_A[0]}/{E15_A[1]}, portable "
            f"{E15_B[0]}/{E15_B[1]}, sans passerelle. Le ping entre les deux échoue."
        ),
        instructions=(
            "Explique pourquoi le ping échoue et corrige l'adressage.",
            "Indique ce qu'il faut savoir sur le câble, la passerelle et le pare-feu, puis les tests de validation.",
        ),
        criteria=(
            _c("Cause et correction", 1, f"{E15_A[0]}/24 → réseau {subnet_facts(*E15_A).network} ; {E15_B[0]}/24 → réseau {subnet_facts(*E15_B).network} : réseaux différents sans routeur ; donner au portable par exemple {E15_B_FIXED[0]}/24."),
            _c("Câble et passerelle", 1, "Auto MDI-X : câble droit ou croisé indifférent ; pas de passerelle nécessaire (même réseau, pas de routeur) ; le câble n'explique pas un problème d'adressage."),
            _c("Pare-feu et tests", 1, "Le pare-feu peut bloquer le ping (ICMP) et le partage : autoriser sur le profil adapté ; tests : voyants de lien, ipconfig, ping dans les deux sens, accès au dossier partagé."),
        ),
        correction=(
            f"Les deux adresses sont en /24 mais dans des réseaux différents ({subnet_facts(*E15_A).cidr} et {subnet_facts(*E15_B).cidr}) : chaque poste considère l'autre comme distant et chercherait une passerelle, qui n'existe pas. Correction : mettre les deux postes dans le même réseau, par exemple portable {E15_B_FIXED[0]}/24.",
            "Câble : avec l'Auto MDI-X (courant aujourd'hui), un câble droit suffit ; un câble croisé fonctionne aussi. Le câble n'a rien à voir avec un défaut d'adressage : les voyants de lien allumés le confirment. Passerelle : inutile, il n'y a pas de routeur ; DNS : inutile, on utilise les adresses IP.",
            "Pare-feu : il peut bloquer le ping (ICMP) et le partage de fichiers ; autoriser ces flux sur le profil réseau utilisé plutôt que désactiver le pare-feu. Tests : lien actif, ipconfig sur chaque poste, ping dans les deux sens, accès au dossier partagé et copie d'un fichier test.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Configurer une adresse fixe sous Windows et sous Linux",
        question_type="long_answer",
        requirement_ids=("AP-11", "AP-30"),
        kind=KIND_CONFIG,
        context=(
            f"Dans le réseau de référence ({LAN_ROUTER} passerelle, DNS {LAN_SERVER}, étendue DHCP "
            f"{LAN_POOL[0]}–{LAN_POOL[1]}), un nouveau serveur de fichiers SRV-02 doit recevoir "
            f"l'adresse fixe {E16_HOST.ip}. Il existe en deux versions selon le choix du client : "
            "Windows ou Linux avec NetworkManager. Tu rédiges la fiche de configuration."
        ),
        instructions=(
            "Donne les paramètres à saisir et vérifie qu'ils sont cohérents avec le plan.",
            "Décris la saisie sous Windows et sous Linux, en distinguant configuration temporaire et persistante, puis les vérifications.",
        ),
        criteria=(
            _c("Paramètres", 1, f"IP {E16_HOST.ip}, masque {E16_HOST.mask} (/24), passerelle {LAN_ROUTER}, DNS {LAN_SERVER} ; hors de l'étendue et non utilisée."),
            _c("Windows", 1, "Propriétés de la carte → Protocole Internet version 4 → « Utiliser l'adresse IP suivante » et « Utiliser l'adresse de serveur DNS suivante » ; persistant."),
            _c("Linux", 1, "Persistant via l'outil de la distribution (nmcli/interface NetworkManager, ou Netplan selon le système) ; « ip addr add » seul est temporaire ; vérifier avec ip addr, ip route, ping passerelle et nom."),
        ),
        correction=(
            f"Paramètres : {E16_HOST.ip}/24 (masque {E16_HOST.mask}), passerelle {LAN_ROUTER}, DNS {LAN_SERVER}. Contrôles : l'adresse est dans le réseau 192.168.10.0/24, hors de l'étendue {LAN_POOL[0]}–{LAN_POOL[1]}, différente de celles du plan ; " + ("aucune erreur détectée." if not host_errors(E16_HOST) else " ".join(host_errors(E16_HOST))),
            "Windows : Paramètres réseau → modifier les options de la carte → Propriétés → « Protocole Internet version 4 (TCP/IPv4) » → « Utiliser l'adresse IP suivante », saisir IP, masque, passerelle, puis DNS préféré. Réglage persistant. Vérifier par ipconfig /all.",
            f"Linux avec NetworkManager : par exemple nmcli connection modify \"<nom de la connexion>\" ipv4.method manual ipv4.addresses {E16_HOST.ip}/24 ipv4.gateway {LAN_ROUTER} ipv4.dns {LAN_SERVER}, puis réactiver la connexion — ou l'interface graphique équivalente. D'autres distributions utilisent Netplan ou d'autres fichiers : on suit l'outil du système. La commande « sudo ip addr add {E16_HOST.ip}/24 dev <interface> » ne sert qu'à un test : elle est perdue au redémarrage.",
            "Vérifications : ip addr / ipconfig (adresse et masque), ip route / route print (route par défaut via la passerelle), ping de la passerelle, ping d'un nom, accès au partage depuis un poste ; plan d'adressage mis à jour.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Remettre la démarche de test dans l'ordre",
        question_type="ordering",
        requirement_ids=("AP-30", "AP-37", "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Tu rédiges la procédure de diagnostic que les nouveaux techniciens d'un service "
            "informatique devront suivre quand un poste « n'a plus de réseau ». Un collègue a noté "
            "les sept étapes, mais dans le désordre ; elles doivent aller du plus proche au plus "
            "lointain."
        ),
        instructions=("Remets les étapes dans l'ordre de la démarche.",),
        criteria=(
            _c("Ordre", 7, " → ".join(name for name, _d in LADDER_STEPS) + " (1 point par étape bien placée)."),
        ),
        correction=(
            "On part du plus proche : lien physique, configuration relevée, bouclage (pile TCP/IP), sa propre adresse, le réseau local (voisin ou passerelle), une adresse distante (routage), puis un nom (DNS).",
            "La première étape qui échoue situe la panne : inutile de tester le DNS si la passerelle ne répond pas. Un ping sans réponse peut aussi venir d'un pare-feu qui filtre l'ICMP : on confirme par un autre test.",
        ),
        ordering=Ordering(
            steps=tuple(f"{LADDER_STEPS[i][0]} : {LADDER_STEPS[i][1]}" for i in E17_SHOWN),
            correct=tuple(E17_SHOWN.index(i) for i in range(len(LADDER_STEPS))),
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Rédiger le compte rendu d'une erreur de masque",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Tu viens d'intervenir chez un client et tu dois rédiger le compte rendu à partir de "
            "tes notes de chantier (document 1). Le client, non technicien, veut comprendre ce qui "
            "s'est passé ; son prestataire veut les valeurs exactes."
        ),
        instructions=(
            "Rédige le compte rendu complet : contexte, constats, hypothèses, tests, cause, correction, validation, recommandation.",
        ),
        documents=(_table(
            "Document 1 — Notes d'intervention (fictives)", ("Heure", "Note"),
            ("09:05", "Demande : le poste COMPTA-2 n'imprime plus et n'ouvre pas le dossier partagé du serveur 192.168.10.5."),
            ("09:12", "ipconfig /all : 192.168.10.33, masque 255.255.255.224, passerelle 192.168.10.1, DNS 192.168.10.5 (fixe)."),
            ("09:15", "ping 192.168.10.1 OK ; ping 192.168.10.5 : délai dépassé ; ping 192.168.10.33 OK."),
            ("09:20", "Autres postes : masque 255.255.255.0. Modification faite hier par un prestataire."),
            ("09:25", "Masque corrigé en 255.255.255.0 ; ping 192.168.10.5 OK, dossier partagé et impression OK."),
        ),),
        criteria=(
            _c("Contexte et constats", 0.75, "Demande, poste, symptômes, relevé exact (IP, masque /27, passerelle, DNS)."),
            _c("Analyse", 1.25, f"Avec /27, le réseau du poste est {subnet_facts('192.168.10.33', 27).cidr} : le serveur .5 est vu comme distant (dans {subnet_facts('192.168.10.5', 27).cidr}) ; hypothèses, tests (ping), cause : masque erroné."),
            _c("Correction et validation", 1, "Masque 255.255.255.0 comme le reste du réseau ; ping serveur, partage et impression OK."),
            _c("Recommandation et clarté", 1, "Mettre à jour le plan, éviter les modifications non documentées ou passer en DHCP ; texte compréhensible par le client."),
        ),
        correction=(
            "Contexte : 26/10, poste COMPTA-2, plus d'impression ni d'accès au dossier partagé du serveur 192.168.10.5 depuis une intervention d'un prestataire la veille.",
            "Constats : IP fixe 192.168.10.33, masque 255.255.255.224 (/27), passerelle 192.168.10.1, DNS 192.168.10.5 ; ping de sa propre adresse et de la passerelle OK, ping du serveur sans réponse. Les autres postes sont en 255.255.255.0.",
            f"Analyse : avec /27, le poste se croit dans le réseau {subnet_facts('192.168.10.33', 27).cidr} (hôtes {subnet_facts('192.168.10.33', 27).host_range}) ; le serveur 192.168.10.5 lui paraît dans un autre réseau ({subnet_facts('192.168.10.5', 27).cidr}). Il n'envoie donc pas les paquets directement au serveur, et la communication échoue. Cause : masque erroné saisi lors de la modification.",
            "Correction : masque 255.255.255.0, identique au reste du réseau. Validation : ping du serveur OK, dossier partagé ouvert, page de test imprimée, en présence de l'utilisateur.",
            "Recommandation : mettre à jour la fiche du poste et le plan d'adressage, documenter toute modification ; envisager le DHCP pour les postes qui n'ont pas besoin d'une adresse fixe.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Procédure : donner une adresse stable à une imprimante",
        question_type="long_answer",
        requirement_ids=("AP-25", "AP-30", "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Dans une école, l'imprimante réseau de la salle des professeurs est en DHCP : "
            "après chaque coupure de courant longue, elle change parfois d'adresse et les postes "
            f"n'impriment plus. Le serveur DHCP ({LAN_SERVER}) gère l'étendue "
            f"{LAN_POOL[0]}–{LAN_POOL[1]} ; le plan indique que 192.168.10.30 est libre."
        ),
        instructions=(
            "Compare les deux solutions possibles (adresse fixe sur l'imprimante, réservation DHCP).",
            "Rédige la procédure de la solution choisie, avec les précautions et les vérifications.",
        ),
        criteria=(
            _c("Comparaison", 1, "Adresse fixe hors de l'étendue (configurée sur l'imprimante) ou réservation DHCP liée à la MAC (gestion centralisée, même adresse à chaque bail) ; les deux sont acceptables si cohérentes."),
            _c("Procédure", 1.5, "Relever la MAC (page de configuration) ; créer la réservation ou saisir IP/masque/passerelle/DNS hors étendue ; redémarrer ou renouveler ; mettre à jour le port d'impression des postes."),
            _c("Précautions et vérifications", 1.5, "Vérifier que l'adresse est libre (plan, ping, arp -a), pas dans l'étendue si fixe ; tester ping et impression depuis plusieurs postes ; mettre à jour le plan."),
        ),
        correction=(
            "Adresse fixe : configurée dans le menu de l'imprimante, hors de l'étendue (sinon doublon possible). Réservation DHCP : le serveur attribue toujours la même adresse à la MAC de l'imprimante ; tout reste géré au même endroit. Les deux solutions sont valables ; la réservation est souvent préférée dans un réseau géré.",
            f"Procédure (réservation) : 1) imprimer la page de configuration et relever la MAC ; 2) vérifier que l'adresse visée est libre (plan, ping sans réponse, arp -a) ; 3) sur le serveur DHCP, créer une réservation MAC → adresse (dans l'étendue ou à côté selon le serveur) ; 4) redémarrer l'imprimante ou renouveler son bail ; 5) contrôler sur sa page de configuration l'adresse, le masque 255.255.255.0, la passerelle {LAN_ROUTER} et le DNS {LAN_SERVER}.",
            "Variante adresse fixe : saisir 192.168.10.30, masque 255.255.255.0, passerelle et DNS du plan dans le menu de l'imprimante (adresse hors de l'étendue).",
            "Vérifications : ping de l'imprimante depuis deux postes, mise à jour du port d'impression si l'adresse a changé, page de test ; mettre à jour le plan d'adressage.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Identifier des adresses MAC et en connaître les limites",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-C01"),
        kind=KIND_REPORT,
        context=(
            "Le directeur d'une association te demande deux choses : relever l'adresse MAC et "
            "l'adresse IP d'un PC Windows, d'un PC Linux et de l'imprimante pour préparer des "
            f"réservations DHCP, et « bloquer les inconnus par leur MAC » pour sécuriser le Wi-Fi. "
            f"Sur le téléphone d'un bénévole, tu lis l'adresse Wi-Fi {E20_PHONE_MAC}."
        ),
        instructions=(
            "Décris comment relever MAC et IP sur chaque équipement, y compris à distance.",
            "Interprète l'adresse du téléphone et réponds à la demande de sécurité.",
        ),
        criteria=(
            _c("Relevé", 1.5, "Windows : ipconfig /all (« Adresse physique ») ; Linux : ip addr ou ip link (link/ether) ; imprimante : page de configuration ; à distance : ping puis arp -a (même réseau) ou liste des baux DHCP."),
            _c("Téléphone", 1, f"{E20_PHONE_MAC} : deuxième chiffre hexadécimal {normalize_mac(E20_PHONE_MAC)[1]} → bit U/L à 1 : adresse administrée localement (MAC aléatoire / privée), qui peut changer : réservation peu fiable."),
            _c("Sécurité", 1.5, "Le filtrage MAC n'est pas une sécurité : une MAC se lit et se modifie ; protéger le Wi-Fi par WPA2/WPA3 avec un mot de passe solide ; la MAC n'identifie pas une personne."),
        ),
        correction=(
            "Windows : ipconfig /all, ligne « Adresse physique » (écriture 3C-52-82-…). Linux : ip addr ou ip link, ligne « link/ether » (écriture 3c:52:82:…). Imprimante : page de configuration réseau. À distance, dans le même réseau : ping de l'adresse IP puis arp -a (ou ip neigh) pour lire la MAC associée ; ou la liste des baux du serveur DHCP. L'ARP ne donne pas la MAC d'un poste situé derrière un routeur.",
            f"{normalize_mac(E20_PHONE_MAC)} : premier octet {normalize_mac(E20_PHONE_MAC)[:2]} → bit U/L " + ("à 1 : adresse administrée localement (MAC aléatoire ou « privée » du Wi-Fi). " if mac_is_locally_administered(E20_PHONE_MAC) else "à 0. ") + "Elle peut être différente sur un autre réseau ou changer avec le temps : une réservation par MAC n'est pas fiable pour ce téléphone (sauf à désactiver l'adresse privée pour ce réseau).",
            "Sécurité : une adresse MAC circule en clair et se modifie facilement ; le filtrage MAC n'arrête pas un intrus déterminé et pose des problèmes avec les adresses aléatoires. La protection réelle du Wi-Fi est le chiffrement WPA2 ou WPA3 avec un mot de passe solide (vu en PR25). Une MAC identifie une carte, pas une personne.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Calculer le sous-réseau d'un poste",
        question_type="short_answer",
        requirement_ids=("AP-30",),
        kind=KIND_SCENARIO,
        context=(
            f"Dans une entreprise de logistique, le poste du quai de chargement a l'adresse "
            f"{X01_FACTS.address}/{X01_FACTS.prefix}. Tu dois l'inscrire dans le plan d'adressage, "
            "qui demande pour chaque sous-réseau le masque, le réseau, la diffusion, la plage "
            "d'hôtes et le nombre d'hôtes utilisables."
        ),
        instructions=("Donne ces cinq valeurs en montrant le calcul.",),
        criteria=(
            _c("Masque, réseau, diffusion", 1, f"{X01_FACTS.mask} ; réseau {X01_FACTS.network} ; diffusion {X01_FACTS.broadcast}."),
            _c("Plage et nombre", 1, f"{X01_FACTS.host_range} ; {X01_FACTS.usable} hôtes (64 − 2)."),
        ),
        correction=(
            f"/26 → masque {X01_FACTS.mask}, blocs de 64 dans le dernier octet (0, 64, 128, 192). 140 est entre 128 et 191 : réseau {X01_FACTS.network}, diffusion {X01_FACTS.broadcast}.",
            f"Hôtes : {X01_FACTS.host_range}, soit {X01_FACTS.usable} hôtes utilisables.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Deux masques à vérifier",
        question_type="short_answer",
        requirement_ids=("AP-30",),
        kind=KIND_SCENARIO,
        context=(
            f"Sur la fiche d'un réseau de magasin, deux masques sont notés pour deux sous-réseaux : "
            f"{X02_MASK} pour la caisse et {X02_BAD_MASK} pour la réserve. Le gérant demande "
            "combien de postes peuvent être adressés dans chacun et si la fiche est correcte."
        ),
        instructions=("Analyse chaque masque (préfixe, nombre d'hôtes ou validité) et conclus.",),
        criteria=(
            _c("Premier masque", 1, f"{X02_MASK} = /{X02_PREFIX} : {X02_FACTS.total} adresses, {X02_FACTS.usable} hôtes."),
            _c("Second masque", 1, f"{X02_BAD_MASK} invalide : 208 = {int(X02_BAD_MASK.split('.')[-1]):08b}, les 1 ne sont pas contigus ; fiche à corriger."),
        ),
        correction=(
            f"240 = 11110000 : 24 + 4 = /{X02_PREFIX} ; 4 bits d'hôte → {X02_FACTS.total} adresses, {X02_FACTS.usable} hôtes utilisables.",
            f"208 = {int(X02_BAD_MASK.split('.')[-1]):08b} : un 0 entre des 1, ce n'est pas un masque valide. Il faut demander la valeur prévue (par exemple 255.255.255.224 ou .240) et corriger la fiche.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Deux postes du même atelier ne se voient pas",
        question_type="short_answer",
        requirement_ids=("AP-30", "AP-31"),
        kind=KIND_SCENARIO,
        context=(
            f"Dans un atelier de menuiserie, deux postes branchés sur le même switch ont les "
            f"adresses {X03_A}/{X03_P} et {X03_B}/{X03_P}. Ils ne communiquent pas entre eux. "
            "Aucun routeur ne relie les sous-réseaux de l'atelier ; le patron voudrait une "
            "solution simple."
        ),
        instructions=("Explique pourquoi, avec le calcul, et propose deux solutions.",),
        criteria=(
            _c("Calcul", 1, f"{X03_A}/{X03_P} → {subnet_facts(X03_A, X03_P).cidr} ; {X03_B}/{X03_P} → {subnet_facts(X03_B, X03_P).cidr} : réseaux différents."),
            _c("Solutions", 1, f"Placer les deux postes dans le même réseau (par exemple {X03_B} → une adresse libre de {subnet_facts(X03_A, X03_P).host_range}, ou masque /24 pour tous si le plan le prévoit) ; ou ajouter un routeur avec passerelles."),
        ),
        correction=(
            f"Avec /{X03_P}, le dernier octet est coupé en deux blocs : 0–127 et 128–255. {X03_A} est dans {subnet_facts(X03_A, X03_P).cidr}, {X03_B} dans {subnet_facts(X03_B, X03_P).cidr} : sans routeur, ils ne peuvent pas se joindre.",
            "Solution simple : mettre les deux postes dans le même réseau (changer l'adresse de l'un, ou passer tout l'atelier en /24 si c'est cohérent avec le plan). Sinon, un routeur entre les deux réseaux, avec la bonne passerelle sur chaque poste.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Trois postes en 169.254 après un changement de switch",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une bibliothèque, un switch de 8 ports a été remplacé ce matin. Les trois postes "
            "branchés dessus affichent une adresse 169.254.x.y avec le masque 255.255.0.0 ; les "
            "postes branchés sur l'autre switch reçoivent normalement une adresse 192.168.1.x "
            "de la box, qui est le serveur DHCP."
        ),
        instructions=("Interprète la situation et indique les vérifications à faire, dans l'ordre, jusqu'à la validation.",),
        criteria=(
            _c("Interprétation", 1, "APIPA : aucun bail DHCP pour ces trois postes ; le serveur fonctionne (les autres ont un bail) : la cause est commune au nouveau switch."),
            _c("Vérifications et validation", 1, "Lien montant du nouveau switch vers le reste du réseau (câble, port, voyants), alimentation, configuration éventuelle (VLAN) ; puis ipconfig /renew, adresse 192.168.1.x, ping passerelle et nom."),
        ),
        correction=(
            "169.254.x.y/16 = APIPA : les trois postes n'ont reçu aucune réponse DHCP. Les autres postes obtiennent un bail : la box fonctionne. Le point commun des trois postes est le nouveau switch.",
            "Vérifier le câble qui relie le nouveau switch au reste du réseau (branché, bon port, voyant), puis sa configuration s'il est administrable (VLAN). Ensuite ipconfig /release et /renew sur un poste : adresse 192.168.1.x, masque, passerelle et DNS de la box ; ping de la passerelle et d'un nom ; puis les deux autres postes.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Résolution de noms en panne sur un poste Linux",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-32"),
        kind=KIND_SCENARIO,
        context=(
            "Sur le poste Linux d'un laboratoire scolaire (réseau 10.0.0.0/24, passerelle "
            "10.0.0.1), aucun site ne s'ouvre. Le technicien affirme qu'« Internet est coupé ». "
            "Tu fais les relevés et tests du document 1 avant de contacter le fournisseur d'accès."
        ),
        instructions=("Interprète les tests et dis s'il faut appeler le fournisseur d'accès ; propose la suite.",),
        documents=(_console(
            "Document 1 — Tests sur le poste (fictifs)",
            "$ ping -c 1 10.0.0.1", "64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=0.5 ms",
            "$ ping -c 1 9.9.9.9", "64 bytes from 9.9.9.9: icmp_seq=1 ttl=57 time=15 ms",
            "$ ping -c 1 www.exemple.be", "ping: www.exemple.be: Temporary failure in name resolution",
            "$ resolvectl dns", "Link 2 (enp0s3): 10.0.0.53",
            "$ ping -c 1 10.0.0.53", "From 10.0.0.20 icmp_seq=1 Destination Host Unreachable",
        ),),
        criteria=(
            _c("Interprétation", 1, "Passerelle et IP distante joignables : Internet fonctionne ; la résolution de noms échoue ; le serveur DNS configuré 10.0.0.53 ne répond pas."),
            _c("Décision et suite", 1, "Ne pas appeler le fournisseur : vérifier le serveur DNS local (allumé, service), ou configurer un DNS valide autorisé (par exemple celui de la box) ; retester par nom."),
        ),
        correction=(
            "La passerelle et une adresse publique répondent : l'accès à Internet fonctionne. Seule la résolution échoue (« Temporary failure in name resolution »), et le serveur DNS configuré, 10.0.0.53, est injoignable.",
            "Ce n'est pas une panne Internet : inutile d'appeler le fournisseur. Vérifier le serveur DNS local (allumé, service démarré) ou utiliser un autre serveur DNS autorisé dans la configuration du poste ou du DHCP, puis retester ping par nom et navigation.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Le poste Linux et sa passerelle",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-31"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une agence immobilière, la box (routeur et DNS) a l'adresse 192.168.1.1. Un "
            "poste Linux joint l'imprimante 192.168.1.30 mais aucun site extérieur. Tu relèves "
            "la table de routage et la table des voisins (document 1)."
        ),
        instructions=("Nomme l'erreur à partir des relevés, puis la correction et sa vérification.",),
        documents=(_console(
            "Document 1 — POSTE-L2 (fictif)",
            *ip_route_lines(X06_HOST), "",
            "$ ip neigh", "192.168.1.30 dev enp3s0 lladdr 00:80:77:01:00:1e REACHABLE",
            "192.168.1.254 dev enp3s0 FAILED",
        ),),
        criteria=(
            _c("Erreur", 1, "Route par défaut via 192.168.1.254 : aucune machine à cette adresse (voisin FAILED) ; la box est 192.168.1.1."),
            _c("Correction et vérification", 1, "Passerelle 192.168.1.1 dans la configuration persistante (ou DHCP) ; ip route montre « default via 192.168.1.1 » ; ping de la box, d'une IP distante et d'un nom."),
        ),
        correction=(
            "ip route : « default via 192.168.1.254 ». ip neigh : 192.168.1.254 FAILED, donc aucune machine ne répond à cette adresse. L'imprimante est dans le même réseau : elle est jointe directement, sans passerelle.",
            "Correction : passerelle 192.168.1.1 dans la configuration persistante du poste (NetworkManager ou outil de la distribution), ou retour au DHCP. Vérifier ip route (default via 192.168.1.1), ping 192.168.1.1, ping d'une adresse distante et d'un nom.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Connexion directe pour une copie de données",
        question_type="short_answer",
        requirement_ids=("AP-28", "AP-30"),
        kind=KIND_SCENARIO,
        context=(
            "Pour transférer les données d'un ancien PC vers un nouveau, tu les relies par un "
            f"câble Ethernet (cartes Auto MDI-X, voyants allumés). Ancien PC : {X07_A}/{X07_P} ; "
            f"nouveau PC : {X07_B}/{X07_P} ; aucune passerelle. Le partage de fichiers est activé "
            "sur l'ancien PC, mais le nouveau ne le trouve pas."
        ),
        instructions=("Explique le problème avec le calcul et corrige ; indique deux autres points à contrôler.",),
        criteria=(
            _c("Calcul et correction", 1, f"{X07_A}/{X07_P} → {subnet_facts(X07_A, X07_P).network} ; {X07_B}/{X07_P} → {subnet_facts(X07_B, X07_P).network} : réseaux différents ; mettre par exemple 172.16.0.2/{X07_P} sur le nouveau PC."),
            _c("Autres points", 1, "Pare-feu (ICMP, partage) sur le profil réseau ; câble non en cause (voyants, Auto MDI-X) ; pas de passerelle nécessaire ; ping puis accès au partage."),
        ),
        correction=(
            f"Avec /16, seuls les deux premiers octets comptent pour le réseau : {X07_A} est dans {subnet_facts(X07_A, X07_P).cidr}, {X07_B} dans {subnet_facts(X07_B, X07_P).cidr}. Réseaux différents, sans routeur : pas de communication. Correction : nouveau PC en 172.16.0.2/16 (ou toute adresse libre de 172.16.0.0/16).",
            "Les voyants et l'Auto MDI-X écartent le câble. Il faut aussi vérifier le pare-feu (profil réseau, ping et partage autorisés) ; aucune passerelle n'est nécessaire. Tests : ping dans les deux sens, puis accès au partage.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Plan d'adressage d'une agence de voyage",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-38"),
        kind=KIND_SCENARIO,
        context=(
            "Une agence de voyage s'équipe : une box 192.168.30.1/24 (routeur, DHCP, DNS) dont "
            "l'étendue DHCP va de 192.168.30.100 à 192.168.30.150, quatre postes et une "
            "imprimante réseau qui doit toujours garder la même adresse. Tu rédiges le plan "
            "d'adressage à remettre au gérant."
        ),
        instructions=("Propose le plan (mode, adresse, masque, passerelle, DNS) et justifie deux choix.",),
        criteria=(
            _c("Plan", 1, "Postes en DHCP (adresses de l'étendue) ; imprimante fixe hors étendue (par exemple 192.168.30.20) ou réservation ; masque 255.255.255.0, passerelle et DNS 192.168.30.1."),
            _c("Justifications", 1, "Pas d'adresse fixe dans l'étendue (doublon), pas de .0 ni .255, imprimante stable pour les postes ; plan tenu à jour."),
        ),
        correction=(
            "Plan proposé : " + " ; ".join(f"{h.name} {h.ip} ({'DHCP' if h.dhcp else 'fixe'})" for h in X08_PLAN.hosts) + " ; masque 255.255.255.0, passerelle et DNS 192.168.30.1 pour tous. Contrôle du plan : " + ("aucune erreur." if not plan_errors(X08_PLAN) else " ".join(plan_errors(X08_PLAN))),
            "Justifications : l'imprimante a une adresse stable hors de l'étendue (ou une réservation) pour que les postes la retrouvent ; aucune adresse fixe dans l'étendue (risque de doublon) ; ni adresse de réseau ni de diffusion. Toute autre proposition cohérente est acceptée.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Un seul poste n'atteint pas le serveur de l'étage",
        question_type="document_analysis",
        requirement_ids=("AP-30", "AP-31"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une mutuelle, les postes du rez-de-chaussée sont dans le réseau 192.168.40.0/24 "
            f"(passerelle 192.168.40.1) ; le serveur de l'étage, {X09_SERVER}, est dans le réseau "
            "192.168.41.0/24, derrière le routeur. Tous les postes joignent le serveur, sauf PC-3. "
            "Tu relis le plan (document 1)."
        ),
        instructions=("Trouve l'erreur et explique, avec le calcul, pourquoi seul ce poste est touché ; corrige.",),
        documents=(_table(
            "Document 1 — Extrait du plan (fictif)", ("Poste", "Adresse", "Masque", "Passerelle"),
            ("PC-1", X09_OTHERS[0], "255.255.255.0", "192.168.40.1"),
            ("PC-2", "192.168.40.12", "255.255.255.0", "192.168.40.1"),
            ("PC-3", X09_PC3[0], subnet_facts(*X09_PC3).mask, "192.168.40.1"),
        ),),
        criteria=(
            _c("Erreur et calcul", 1, f"PC-3 en /16 : son réseau est {subnet_facts(*X09_PC3).cidr}, qui contient {X09_SERVER} : il croit le serveur local et ne passe pas par la passerelle."),
            _c("Correction", 1, "Masque 255.255.255.0 sur PC-3 ; vérifier ping du serveur, route par défaut ; les autres (/24) voient le serveur distant et passent par le routeur."),
        ),
        correction=(
            f"PC-3 a le masque {subnet_facts(*X09_PC3).mask} (/16) : son réseau est {subnet_facts(*X09_PC3).cidr}, qui inclut {X09_SERVER}. Il considère donc le serveur comme local et le cherche directement (ARP) au lieu de passer par la passerelle : aucune réponse, le serveur est derrière le routeur.",
            f"Les autres postes, en /24 (réseau {subnet_facts(*X09_OTHERS).cidr}), voient le serveur comme distant et passent par 192.168.40.1 : ils le joignent. Correction : masque 255.255.255.0 sur PC-3, puis ping du serveur et accès à ses ressources.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Compte rendu d'un doublon d'adresse",
        question_type="long_answer",
        requirement_ids=("AP-30", "AP-C01"),
        kind=KIND_SCENARIO,
        context=(
            "Chez un notaire, le poste ACCUEIL perdait le réseau plusieurs fois par jour avec un "
            "message de conflit d'adresses IP. Tes notes : ACCUEIL en DHCP a reçu 192.168.5.120 ; "
            "un ancien point d'accès Wi-Fi avait été configuré à la main en 192.168.5.120, dans "
            "l'étendue DHCP 192.168.5.100–192.168.5.200 ; tu lui as donné 192.168.5.20, libre ; "
            "plus de conflit depuis deux heures."
        ),
        instructions=("Rédige le compte rendu de l'intervention destiné au notaire.",),
        criteria=(
            _c("Constat, cause et test", 1, "Symptôme et message ; doublon 192.168.5.120 entre le poste (DHCP) et le point d'accès (fixe dans l'étendue) ; preuve (arp -a, menu du point d'accès)."),
            _c("Action, validation, recommandation", 1, "Point d'accès en 192.168.5.20 hors étendue, poste renouvelé ; plus de conflit ; plan d'adressage à jour, adresses fixes toujours hors étendue."),
        ),
        correction=(
            "Constat : coupures répétées du poste ACCUEIL avec un message de conflit d'adresses IP. Cause : deux appareils utilisaient 192.168.5.120 — le poste, qui l'avait reçue par DHCP, et un ancien point d'accès configuré à la main avec une adresse située dans l'étendue DHCP (100–200).",
            "Action : le point d'accès a reçu l'adresse fixe 192.168.5.20, libre et hors de l'étendue ; le poste a renouvelé son bail. Validation : plus aucun conflit depuis deux heures, réseau stable. Recommandation : tenir un plan d'adressage à jour et toujours placer les adresses fixes hors de l'étendue DHCP.",
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
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors


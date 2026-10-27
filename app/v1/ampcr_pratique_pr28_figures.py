"""PR28 « Outillage, sécurité et protection des données » — règles du cours, cinq interventions
résolues et schémas (ticket #227).

Ce cours rassemble les **précautions de toute intervention** : choisir l'outil, travailler en
sécurité (complément AP-C02) et protéger les données du client (complément AP-C03). Les règles
qu'un dossier d'examen applique et qu'un correcteur vérifie sont écrites ici une seule fois,
sous forme de données et de fonctions testées, et réutilisées par le cours, les exercices, le
mini-examen et les schémas :

- `TOOLS` / `TASKS` / `INTERVENTIONS` / `kit` : inventaire de l'outillage PC et réseau (usage,
  précaution) ; outil propre à chaque tâche ; kit d'une intervention ;
- `RISKS` : ESD, électricité, bloc d'alimentation, batteries endommagées, ventilation, risques
  mécaniques, laser et éclats de fibre, poste de travail (danger, prévention, réaction) ;
- `DISCONNECT_STEPS`, `BATTERY_STEPS`, `AUTH_STEPS`, `INCIDENT_STEPS` : procédures ;
- `check_321` : règle de sauvegarde 3-2-1 (complément) ; `fingerprint` / `compare_copy` :
  intégrité d'une copie par empreinte SHA-256 ;
- `missing_prerequisites` : ce qui manque avant un effacement, un formatage, une réinitialisation
  ou une réinstallation (sauvegarde vérifiée, accord écrit, personne habilitée, clé de
  récupération, licences) ; décision et techniques d'effacement de PR04 réutilisées ;
- `waste_route` : filière de fin de vie (DEEE, piles et batteries, supports de données,
  cartouches) ;
- `INCIDENT_TREE` : arbre de gestion d'un incident (format et parcours `walk` de PR27) ;
- `CASES` : cinq interventions entièrement résolues, dont les kits, les manques et les filières
  sont **calculés et contrôlés**.

Les schémas sont construits en SVG depuis ces données (aucune image générée, aucun geste
dangereux montré), comme PR18 à PR27. Les personnes, entreprises et dossiers sont fictifs.
"""

import hashlib
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr04_figures import (
    DEST_RECYCLING,
    MEDIA_HDD,
    MEDIA_SATA_SSD,
    data_decision,
    erase_method_ok,
)
from app.v1.ampcr_pratique_pr27_figures import Tree
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    step_flow_svg,
)

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
_STROKE = "#33415c"
_SOFT = "#f4f6fb"

# =============================================================================================
# 1. Outillage : inventaire, outil propre à chaque tâche, kit d'une intervention
# =============================================================================================

FAM_PC = "Poste de travail (PC)"
FAM_NET = "Réseau et câblage"


@dataclass(frozen=True)
class Tool:
    key: str
    name: str
    family: str
    use: str
    precaution: str


TOOLS: tuple[Tool, ...] = (
    Tool("tournevis", "Tournevis cruciformes (PH0 à PH2) et Torx", FAM_PC,
         "visser et dévisser le boîtier, les disques, la carte mère, un SSD M.2",
         "embout de la bonne taille, sans forcer (tête de vis abîmée) ; vis rangées dans un bac à compartiments"),
    Tool("pince", "Pince à bec fin et pince brucelles", FAM_PC,
         "récupérer une vis tombée, saisir un petit connecteur ou un cavalier",
         "uniquement hors tension ; jamais pour tirer sur un câble ni faire levier sur un composant"),
    Tool("esd", "Bracelet et tapis antistatiques (ESD)", FAM_PC,
         "mettre le technicien et la pièce au même potentiel pour éviter une décharge électrostatique",
         "selon la procédure de l'atelier : tapis relié au point de masse, bracelet relié au tapis "
         "(ou, sans tapis, à une partie métallique nue du châssis) ; bracelet contrôlé ; PC débranché"),
    Tool("testeur-alim", "Testeur d'alimentation (bloc ATX)", FAM_PC,
         "contrôler les tensions du bloc par ses connecteurs, hors de la carte mère",
         "outil autorisé par l'atelier ; connecteurs branchés avant la mise sous tension ; ne prouve pas la "
         "tenue en charge ; le bloc n'est jamais ouvert"),
    Tool("multimetre", "Multimètre", FAM_PC,
         "mesurer une tension continue basse (pile CMOS, sortie d'un bloc), une continuité, une résistance",
         "mode et calibre choisis avant de toucher ; cordons et pointes en bon état, catégorie adaptée ; "
         "continuité et résistance hors tension ; aucune mesure sur le 230 V ni dans un bloc"),
    Tool("pate", "Pâte thermique et alcool isopropylique", FAM_PC,
         "refaire l'interface entre le processeur et le radiateur après démontage",
         "ancienne pâte retirée à l'alcool isopropylique et chiffon non pelucheux ; petite quantité ; jamais "
         "sur les contacts ni sur la carte mère ; pièce ventilée"),
    Tool("nettoyage", "Air sec, pinceau antistatique et chiffon microfibre", FAM_PC,
         "dépoussiérer ventilateurs, radiateurs et filtres ; nettoyer les surfaces",
         "PC hors tension ; pales du ventilateur bloquées pendant le soufflage ; bombe tenue droite, par "
         "petites pressions ; pas d'aspirateur domestique ; pièce aérée, masque si beaucoup de poussière"),
    Tool("sertisseuse-rj45", "Sertisseuse 8P8C (RJ45)", FAM_NET,
         "sertir une fiche RJ45 sur un câble à paires torsadées",
         "fiche adaptée au câble (monobrin ou multibrin, catégorie) ; ordre T568A ou T568B ; gaine prise sous "
         "le serre-câble"),
    Tool("denudeur", "Dénudeur de câble à paires", FAM_NET,
         "retirer la gaine extérieure sans entailler les conducteurs",
         "profondeur réglée sur une chute de câble ; conducteur entaillé = recommencer"),
    Tool("insertion", "Outil d'insertion (punch-down 110 ou LSA)", FAM_NET,
         "enfoncer les conducteurs dans les contacts autodénudants d'une prise murale ou d'un panneau",
         "lame du bon type (110 ou LSA) ; côté coupant vers la chute du fil ; torsades gardées jusqu'au contact"),
    Tool("wiremap", "Testeur de câble (wiremap)", FAM_NET,
         "vérifier chaque fil : coupure, court-circuit, inversion, croisement",
         "jamais branché sur un port actif (PoE, ligne téléphonique) ; ne remplace pas une certification ; "
         "piles contrôlées"),
    Tool("bnc", "Pince à sertir BNC et dénudeur coaxial", FAM_NET,
         "préparer un câble coaxial en gradins et sertir une fiche BNC",
         "matrice adaptée au câble (RG58 ou RG59) ; cotes de dénudage du fabricant ; aucun brin de tresse sur l'âme"),
    Tool("fibre-nettoyage", "Kit de nettoyage fibre (stylo ou cassette)", FAM_NET,
         "nettoyer une férule ou un connecteur optique avant de l'emboîter",
         "source éteinte ou fibre débranchée ; capuchons remis aussitôt ; jamais de chiffon ni de souffle"),
    Tool("vfl", "Localisateur visuel (stylo laser rouge)", FAM_NET,
         "faire briller une cassure ou repérer une fibre dans un tiroir optique",
         "laser : jamais vers les yeux ni dans une fibre que l'on regarde ; éteint après usage"),
)
TOOLS_BY_KEY = {t.key: t for t in TOOLS}
PC_TOOLS = tuple(t for t in TOOLS if t.family == FAM_PC)
NET_TOOLS = tuple(t for t in TOOLS if t.family == FAM_NET)

# Une tâche précise → l'outil qui lui est propre (un seul bon choix par tâche).
TASKS: tuple[tuple[str, str], ...] = (
    ("Fixer une fiche RJ45 au bout d'un câble de catégorie 6", "sertisseuse-rj45"),
    ("Raccorder un câble sur les contacts d'une prise murale", "insertion"),
    ("Vérifier qu'aucun fil d'un cordon neuf n'est inversé", "wiremap"),
    ("Contrôler le +12 V d'un bloc démonté, hors de la carte mère", "testeur-alim"),
    ("Mesurer la tension de la pile CMOS retirée", "multimetre"),
    ("Remplacer une barrette de mémoire sans risque de décharge électrostatique", "esd"),
    ("Retirer la gaine d'un câble à paires sans entailler les fils", "denudeur"),
    ("Repérer une fibre cassée dans un tiroir optique", "vfl"),
    ("Remonter un radiateur de processeur après l'avoir démonté", "pate"),
)


def tool_for(task: str) -> Tool:
    return TOOLS_BY_KEY[dict(TASKS)[task]]


@dataclass(frozen=True)
class Intervention:
    key: str
    title: str
    tools: tuple[str, ...]
    risks: tuple[str, ...]


def kit(intervention: "Intervention") -> tuple[Tool, ...]:
    """Kit d'une intervention, dans l'ordre de l'inventaire."""
    return tuple(t for t in TOOLS if t.key in intervention.tools)


# =============================================================================================
# 2. Risques : danger, prévention, réaction
# =============================================================================================


@dataclass(frozen=True)
class Risk:
    key: str
    name: str
    danger: str
    prevention: str
    reaction: str


RISKS: tuple[Risk, ...] = (
    Risk("esd", "Décharge électrostatique (ESD)",
         "une décharge invisible, même trop faible pour être sentie, peut détruire ou affaiblir une puce",
         "PC débranché, bracelet et tapis selon la procédure, pièces tenues par les bords et posées sur le tapis "
         "ou dans un sachet antistatique",
         "pièce suspecte : l'étiqueter, la tester sur un poste de test, ne pas la remettre en service sans contrôle"),
    Risk("elec", "Électricité et condensateurs",
         "le secteur 230 V est mortel ; un bloc ou un écran garde une charge dangereuse après débranchement",
         "arrêter, interrupteur sur 0, débrancher, appuyer sur le bouton de démarrage pour vider les "
         "condensateurs de la carte ; jamais de mesure sur le 230 V",
         "couper le courant avant de toucher une victime, appeler le 112, prévenir le responsable"),
    Risk("psu", "Bloc d'alimentation",
         "ses condensateurs internes restent chargés longtemps à des tensions dangereuses",
         "on n'ouvre jamais un bloc, ni pour le nettoyer ni pour le réparer ; on le teste par ses connecteurs ; "
         "en panne, on le remplace",
         "bloc qui fume, sent le brûlé ou claque : couper, débrancher, l'écarter, ne pas le rebrancher"),
    Risk("batt", "Batteries endommagées (lithium-ion)",
         "une batterie gonflée, percée, chaude ou tombée peut s'enflammer violemment et dégager des fumées toxiques",
         "ne pas la charger, ne pas la percer ni la presser, la retirer si le manuel le permet, la poser dans un bac "
         "ininflammable loin de toute matière combustible",
         "fumée ou flamme : s'éloigner, alerter (112), suivre les consignes incendie du site"),
    Risk("vent", "Ventilation : poussières et vapeurs",
         "poussières soufflées, vapeurs d'alcool isopropylique (inflammable), gaz des bombes d'air sec",
         "pièce aérée, souffler vers l'extérieur du boîtier, masque anti-poussière si l'encrassement est fort, "
         "aucune flamme ni appareil chaud à côté",
         "malaise ou irritation : sortir à l'air libre, prévenir, rincer la peau ou les yeux à l'eau"),
    Risk("meca", "Risques mécaniques",
         "tranches coupantes du boîtier, ventilateur en rotation, charge lourde (serveur, écran), outil qui ripe",
         "gants de manutention pour les tôles, PC éteint avant de toucher un ventilateur, port à deux des "
         "charges lourdes, outil adapté tenu dans l'axe",
         "coupure : désinfecter et protéger ; plaie importante : premiers secours et 112"),
    Risk("laser", "Laser et éclats de fibre",
         "la lumière des modules optiques est souvent infrarouge, donc invisible, et peut brûler la rétine ; un "
         "éclat de fibre se plante dans la peau ou l'œil",
         "ne jamais regarder une extrémité de fibre, capuchons en place, lunettes de protection, éclats jetés dans "
         "un récipient fermé, ne pas manger sur le poste",
         "éclat dans l'œil : ne pas frotter, rincer, consulter un médecin ; dans la peau : le retirer à la pince"),
    Risk("poste", "Poste de travail",
         "plan encombré, liquide renversé, câble au sol qui fait trébucher, éclairage insuffisant, vis perdue "
         "dans le boîtier",
         "plan dégagé et éclairé, boissons à l'écart, câbles rangés, vis triées, outils remis en place après usage",
         "liquide renversé sur un appareil : couper et débrancher, ne pas rallumer avant séchage et contrôle"),
)
RISKS_BY_KEY = {r.key: r for r in RISKS}
RISK_NAMES = tuple(r.name for r in RISKS)

INTERVENTIONS: tuple[Intervention, ...] = (
    Intervention("ram", "Ajouter ou remplacer une barrette de mémoire", ("tournevis", "esd"), ("elec", "esd", "poste")),
    Intervention("nettoyage", "Dépoussiérer un PC et refaire la pâte thermique",
                 ("tournevis", "esd", "pate", "nettoyage"), ("elec", "esd", "vent", "meca")),
    Intervention("alim", "Contrôler un bloc d'alimentation suspect", ("tournevis", "esd", "testeur-alim"),
                 ("elec", "psu", "esd")),
    Intervention("cmos", "Contrôler et remplacer la pile CMOS", ("tournevis", "esd", "multimetre", "pince"),
                 ("elec", "esd", "poste")),
    Intervention("prise", "Poser une prise murale et fabriquer son cordon RJ45",
                 ("denudeur", "insertion", "sertisseuse-rj45", "wiremap"), ("meca", "poste")),
    Intervention("bnc", "Monter une fiche BNC sur un câble coaxial", ("bnc",), ("meca", "poste")),
    Intervention("fibre", "Brasser et contrôler une jarretière optique", ("fibre-nettoyage", "vfl"), ("laser", "poste")),
)
INTERVENTIONS_BY_KEY = {i.key: i for i in INTERVENTIONS}

# =============================================================================================
# 3. Procédures : débranchement, batterie endommagée, fibre, nettoyage, multimètre
# =============================================================================================

DISCONNECT_STEPS: tuple[tuple[str, str], ...] = (
    ("Prévenir", "Faire enregistrer le travail ; vérifier que la sauvegarde des données existe."),
    ("Arrêter le système", "Arrêt normal depuis le système, jamais en coupant le courant."),
    ("Couper le bloc", "Interrupteur arrière du bloc sur 0."),
    ("Débrancher", "Câble secteur retiré, puis les périphériques et le réseau ; portable : chargeur retiré."),
    ("Vider les charges", "Appui de quelques secondes sur le bouton de démarrage, câble débranché."),
    ("Se protéger de l'ESD", "Bracelet relié selon la procédure, puis seulement ouvrir le boîtier."),
)
BATTERY_STEPS: tuple[tuple[str, str], ...] = (
    ("Ne plus charger", "Débrancher le chargeur ; ne pas rallumer l'appareil."),
    ("Ne pas déformer", "Ne pas percer, presser ni plier la batterie ; ne pas forcer le capot."),
    ("Isoler", "Poser l'appareil ou la batterie dans un bac ininflammable, loin des matières combustibles."),
    ("Prévenir", "Informer le client et le responsable ; noter l'état (photo, date) sur la fiche."),
    ("Faire remplacer", "Pièce d'origine par le fabricant ou un réparateur habilité, selon la garantie."),
    ("Éliminer", "Pôles isolés au ruban adhésif, filière des piles et batteries ; jamais à la poubelle."),
)
FIBRE_DO: tuple[str, ...] = (
    "Éteindre la source ou débrancher avant d'inspecter",
    "Remettre les capuchons aussitôt",
    "Nettoyer chaque férule avant de brancher",
    "Lunettes de protection pour couper",
    "Éclats dans un récipient fermé",
)
FIBRE_DONT: tuple[str, ...] = (
    "Regarder l'extrémité d'une fibre",
    "Pointer le stylo laser vers un œil",
    "Souffler sur une férule",
    "Ramasser un éclat à la main",
    "Manger ou boire sur le poste",
)
CLEAN_DO: tuple[str, ...] = (
    "Bloquer les pales du ventilateur avant de souffler",
    "Tenir la bombe d'air sec droite, par petites pressions",
    "Retirer l'ancienne pâte thermique à l'alcool isopropylique",
    "Nettoyer les filtres à poussière de la façade",
    "Travailler dans une pièce aérée",
)
CLEAN_DONT: tuple[str, ...] = (
    "Passer l'aspirateur domestique sur la carte mère",
    "Laisser le ventilateur tourner librement sous le jet d'air",
    "Pulvériser un nettoyant liquide sur le PC sous tension",
    "Dévisser le capot du bloc pour en souffler l'intérieur",
    "Étaler une couche épaisse de pâte qui déborde sur la carte",
)
MULTIMETER_RULES: tuple[tuple[str, str], ...] = (
    ("Choisir", "Mode (tension continue, continuité, résistance) et calibre avant de toucher le circuit."),
    ("Contrôler", "Cordons sans gaine abîmée, pointes en bon état, appareil de catégorie adaptée."),
    ("Brancher", "Cordon noir sur COM, rouge sur la borne V/Ω ; jamais la borne A pour une tension."),
    ("Mesurer hors secteur", "Basse tension continue seulement (pile, sortie d'un bloc) ; jamais le 230 V."),
    ("Couper avant la continuité", "Continuité et résistance uniquement circuit hors tension."),
)
CMOS_NOMINAL = 3.0  # pile bouton CR2032 : 3 V nominal

# =============================================================================================
# 4. Protection des données : 3-2-1, intégrité, autorisation
# =============================================================================================

SUP_INTERNAL = "disque interne du PC"
SUP_EXTERNAL = "disque externe USB"
SUP_NAS = "NAS"
SUP_CLOUD = "stockage en ligne (cloud)"
SUP_USB_KEY = "clé USB"
# Type de support (convention du cours, prudente) : disque interne, disque externe et NAS
# sont tous des disques ; seul un autre type (en ligne, mémoire flash) compte pour le « 2 ».
SUPPORT_TYPES = {
    SUP_INTERNAL: "disque", SUP_EXTERNAL: "disque", SUP_NAS: "disque", SUP_CLOUD: "en ligne",
    SUP_USB_KEY: "mémoire flash",
}

MISS_3 = "moins de 3 copies"
MISS_2 = "un seul type de support"
MISS_1 = "aucune copie hors site"
MISSES_321 = (MISS_3, MISS_2, MISS_1)


@dataclass(frozen=True)
class Copy:
    label: str
    support: str
    offsite: bool


def check_321(copies: tuple[Copy, ...]) -> tuple[str, ...]:
    """Règle 3-2-1 (complément) : au moins 3 copies (l'original compris), sur au moins 2 types
    de supports, dont au moins 1 hors site. Renvoie les points manquants (vide = conforme)."""
    missing = []
    if len(copies) < 3:
        missing.append(MISS_3)
    if len({SUPPORT_TYPES[c.support] for c in copies}) < 2:
        missing.append(MISS_2)
    if not any(c.offsite for c in copies):
        missing.append(MISS_1)
    return tuple(missing)


def fingerprint(content: str) -> str:
    """Empreinte SHA-256 (16 premiers caractères hexadécimaux) d'un contenu fictif."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def compare_copy(source: tuple[tuple[str, int, str], ...],
                 copy: tuple[tuple[str, int, str], ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Intégrité d'une copie : (fichiers absents de la copie, fichiers dont la taille ou
    l'empreinte diffère), dans l'ordre de la source. Lignes : (nom, taille en octets,
    empreinte)."""
    copied = {name: (size, fp) for name, size, fp in copy}
    missing = tuple(name for name, _s, _f in source if name not in copied)
    different = tuple(name for name, size, fp in source if name in copied and copied[name] != (size, fp))
    return missing, different


OP_REINSTALL = "Réinstallation du système"
OP_FORMAT = "Formatage d'un disque"
OP_RESET = "Réinitialisation d'usine"
OP_ERASE = "Effacement sécurisé avant don ou recyclage"
OPERATIONS = (OP_REINSTALL, OP_FORMAT, OP_RESET, OP_ERASE)

PRE_BACKUP = "sauvegarde vérifiée des données à garder (copie relue)"
PRE_CONSENT = "accord écrit, daté, qui nomme l'opération et le support"
PRE_AUTHORIZED = "accord signé par une personne habilitée (propriétaire ou responsable)"
PRE_KEY = "clé de récupération du chiffrement en main (disque chiffré)"
PRE_LICENSES = "licences, comptes et réglages notés pour la remise en service"
PREREQUISITES = (PRE_BACKUP, PRE_CONSENT, PRE_AUTHORIZED, PRE_KEY, PRE_LICENSES)


def required_prerequisites(operation: str, *, keep_data: bool, encrypted: bool) -> tuple[str, ...]:
    """Prérequis d'une opération qui efface : accord écrit d'une personne habilitée toujours ;
    sauvegarde vérifiée si des données sont à garder ; clé de récupération si le disque est
    chiffré et que le poste doit resservir ; licences notées si le poste est remis en service."""
    if operation not in OPERATIONS:
        raise ValueError(f"Opération inconnue : {operation}")
    back_in_service = operation != OP_ERASE
    needed = {PRE_CONSENT, PRE_AUTHORIZED}
    if keep_data:
        needed.add(PRE_BACKUP)
    if encrypted and back_in_service:
        needed.add(PRE_KEY)
    if back_in_service:
        needed.add(PRE_LICENSES)
    return tuple(p for p in PREREQUISITES if p in needed)


def missing_prerequisites(operation: str, done: frozenset[str], *, keep_data: bool,
                          encrypted: bool) -> tuple[str, ...]:
    """Prérequis encore manquants (vide = l'opération peut commencer)."""
    return tuple(p for p in required_prerequisites(operation, keep_data=keep_data, encrypted=encrypted)
                 if p not in done)


AUTH_STEPS: tuple[tuple[str, str], ...] = (
    ("Inventorier", "Avec le client : profils, documents, courriels, favoris, licences, données de logiciels."),
    ("Sauvegarder", "Copier les données à garder sur un autre support, chiffré si elles sont sensibles."),
    ("Vérifier", "Relire la copie : nombre de fichiers, tailles, empreintes, quelques fichiers ouverts."),
    ("Récupérer les clés", "Clé de récupération du chiffrement, licences et comptes notés pour la remise en service."),
    ("Faire signer", "Accord écrit, daté, par une personne habilitée : opération, support, sort des données."),
    ("Effacer ou réinstaller", "Seulement alors ; noter l'opération sur la fiche, la copie est effacée après restitution."),
)

# =============================================================================================
# 5. Fin de vie : filières
# =============================================================================================

W_EEE = "DEEE : appareil électrique ou électronique"
W_BATTERY = "pile ou batterie"
W_DATA = "support de données"
W_TONER = "cartouche d'encre ou toner"
WASTE_KINDS = (W_EEE, W_BATTERY, W_DATA, W_TONER)

ROUTE_EEE = "Collecte DEEE (en Belgique : point Recupel, parc à conteneurs ou collecteur agréé)"
ROUTE_BATTERY = "Collecte des piles et batteries (en Belgique : Bebat), pôles isolés"
ROUTE_DATA = "Effacement certifié ou destruction par une filière agréée, puis collecte DEEE"
ROUTE_TONER = "Reprise par le fabricant ou le fournisseur, ou collecte spécifique des cartouches"
ROUTES = (ROUTE_EEE, ROUTE_BATTERY, ROUTE_DATA, ROUTE_TONER)


def waste_route(kind: str) -> str:
    """Filière d'un déchet de l'atelier : jamais la poubelle ordinaire."""
    return dict(zip(WASTE_KINDS, ROUTES, strict=True))[kind]


# (objet à éliminer, nature) — exemples du cours et des exercices.
WASTE_ITEMS: tuple[tuple[str, str], ...] = (
    ("Écran LCD hors d'usage", W_EEE),
    ("Clavier et souris cassés", W_EEE),
    ("Batterie de portable gonflée, pôles isolés", W_BATTERY),
    ("Piles bouton CR2032 usagées", W_BATTERY),
    ("Disque dur d'un PC de comptabilité", W_DATA),
    ("Clé USB d'un ancien employé", W_DATA),
    ("Toner vide d'une imprimante laser", W_TONER),
)

# =============================================================================================
# 6. Gestion d'incident : procédure et arbre
# =============================================================================================

INCIDENT_STEPS: tuple[tuple[str, str], ...] = (
    ("Sécuriser", "Couper le courant si c'est possible sans risque, s'éloigner du danger, isoler l'appareil."),
    ("Alerter", "112 en cas de blessure grave, de fumée ou de feu ; prévenir le responsable."),
    ("Secourir", "Premiers secours dans la limite de sa formation, sans se mettre en danger."),
    ("Protéger les données", "Arrêter toute écriture, ne rien réinstaller ; signaler aussitôt une fuite possible."),
    ("Noter", "Fiche d'incident : heure, faits, personnes, mesures prises, photos."),
    ("Analyser", "Avec le responsable : cause, mesure pour que cela ne se reproduise pas."),
)

INCIDENT_TREE = Tree(
    key="incident",
    title="Incident pendant une intervention",
    start="Choc électrique, fumée, blessure, pièce abîmée, données perdues ou exposées.",
    questions=(
        ("La zone est-elle sûre (ni fumée, ni flamme, ni contact électrique) ?",
         "Couper le courant sans risque, s'éloigner, alerter le 112 ; ne pas toucher une victime encore en contact."),
        ("Tout le monde est-il indemne (aucun blessé) ?",
         "Premiers secours dans la limite de sa formation ; 112 si c'est grave ; prévenir le responsable."),
        ("Les données du client sont-elles intactes et sous contrôle ?",
         "Arrêter toute écriture, ne rien réinstaller ; prévenir aussitôt le responsable, qui décide de la suite."),
        ("Le matériel est-il intact ?",
         "Isoler l'appareil, l'étiqueter « ne pas utiliser », le photographier ; ne pas le remettre en service."),
    ),
    final="Noter l'incident sur la fiche (heure, faits, mesures), informer le client, analyser la cause avec le responsable.",
)

# Fiche sécurité : rubriques du modèle du cours.
SAFETY_SHEET_FIELDS: tuple[str, ...] = (
    "Intervention", "Risques", "Protections et outils", "Avant", "Pendant", "Après", "En cas d'incident",
)

# Liste de contrôle d'une intervention (avant / pendant / après).
CHECKLIST: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Avant", (
        "Demande et accord écrits ; données sauvegardées et copie vérifiée",
        "Outils choisis et contrôlés ; poste dégagé et éclairé",
        "Système arrêté, bloc sur 0, débranché, charges vidées",
        "Bracelet et tapis antistatiques en place",
    )),
    ("Pendant", (
        "Une modification à la fois, notée sur la fiche",
        "Pièces sur le tapis ou en sachet ; vis triées",
        "Aucune consultation des fichiers personnels du client",
    )),
    ("Après", (
        "Contrôle de fonctionnement devant le client",
        "Copie temporaire des données effacée après restitution",
        "Déchets triés vers leur filière ; outils rangés",
    )),
)

# =============================================================================================
# 7. Les cinq interventions entièrement résolues
# =============================================================================================

C1_INTERVENTION = INTERVENTIONS_BY_KEY["nettoyage"]
C2_RISK = RISKS_BY_KEY["batt"]
C2_ROUTE = waste_route(W_BATTERY)

C3_COPIES: tuple[Copy, ...] = (
    Copy("Original : documents du comptable", SUP_INTERNAL, False),
    Copy("Copie du cabinet sur le NAS du bureau", SUP_NAS, False),
)
C3_COPIES_AFTER = C3_COPIES + (Copy("Copie chiffrée chez le prestataire en ligne", SUP_CLOUD, True),)
C3_321_BEFORE = check_321(C3_COPIES)
C3_321_AFTER = check_321(C3_COPIES_AFTER)
C3_DONE = frozenset({PRE_CONSENT, PRE_AUTHORIZED})
C3_MISSING = missing_prerequisites(OP_REINSTALL, C3_DONE, keep_data=True, encrypted=True)

C3_FILES: tuple[tuple[str, str], ...] = (
    ("Clients-2026.xlsx", "liste des clients du cabinet, version d'octobre"),
    ("Déclarations-TVA.pdf", "déclarations du troisième trimestre"),
    ("Factures-sept.zip", "archive des factures de septembre"),
    ("Contrats.docx", "modèle de contrat de mission"),
)
C3_SOURCE: tuple[tuple[str, int, str], ...] = tuple(
    (name, len(text.encode("utf-8")) * 1000, fingerprint(text)) for name, text in C3_FILES
)
# La copie : Factures-sept.zip interrompue (contenu tronqué), Contrats.docx absent.
C3_COPY: tuple[tuple[str, int, str], ...] = (
    C3_SOURCE[0],
    C3_SOURCE[1],
    ("Factures-sept.zip", C3_SOURCE[2][1] // 2, fingerprint(C3_FILES[2][1][:20])),
)
C3_INTEGRITY = compare_copy(C3_SOURCE, C3_COPY)

C4_INTERVENTION = INTERVENTIONS_BY_KEY["prise"]
C4_FIBRE = INTERVENTIONS_BY_KEY["fibre"]

C5_ITEMS: tuple[tuple[str, str], ...] = (
    ("Cinq unités centrales (disques retirés)", W_EEE),
    ("Cinq disques durs des unités centrales", W_DATA),
    ("Deux SSD SATA des portables", W_DATA),
    ("Deux batteries de portables", W_BATTERY),
    ("Quatre toners vides", W_TONER),
)
C5_ROUTES = tuple((item, waste_route(kind)) for item, kind in C5_ITEMS)
C5_DECISION = data_decision(owner_consent=True, wants_data=False, backup_verified=False, destination=DEST_RECYCLING)
C5_HDD_OK = erase_method_ok(MEDIA_HDD, "écrasement complet du disque (une passe suffit sur un disque récent)")
C5_SSD_FORMAT_OK = erase_method_ok(MEDIA_SATA_SSD, "formatage rapide")


@dataclass(frozen=True)
class Case:
    key: str
    theme: str
    title: str
    context: str
    risks: tuple[str, ...]
    tools: tuple[Tool, ...]
    before: tuple[str, ...]
    during: tuple[str, ...]
    after: tuple[str, ...]
    data: str
    incident: str
    conclusion: str


CASES: tuple[Case, ...] = (
    Case(
        key="C1",
        theme="outillage et sécurité du poste",
        title="Dépoussiérer un PC de dessin qui chauffe et refaire la pâte thermique",
        context=(
            "Bureau d'architectes Ligne (fictif). Le PC tour de dessin s'arrête en plein rendu ; le client a "
            "accepté par écrit un dépoussiérage complet et le remplacement de la pâte thermique du processeur. "
            "L'atelier dispose de tout l'outillage du cours."
        ),
        risks=C1_INTERVENTION.risks,
        tools=kit(C1_INTERVENTION),
        before=(
            "Accord écrit sur la fiche ; la sauvegarde du soir existe et sa date est vérifiée.",
            "Arrêt du système, bloc sur 0, câble secteur débranché, appui sur le bouton de démarrage.",
            "PC porté sur le plan de travail aéré, près de la fenêtre ; tapis relié au point de masse, bracelet relié au tapis.",
        ),
        during=(
            "Pales bloquées avec un doigt ou le pinceau, air sec par petites pressions, bombe droite ; jamais l'aspirateur.",
            "Radiateur démonté, ancienne pâte retirée à l'alcool isopropylique, petite quantité de pâte neuve, radiateur revissé en croix.",
            "Le bloc d'alimentation est seulement soufflé de l'extérieur par ses grilles, jamais ouvert.",
        ),
        after=(
            "Contrôle visuel : câbles en place, aucune vis libre dans le boîtier.",
            "Rendu de test de 30 minutes : température du processeur relevée avant et après.",
            "Chiffons et emballages triés ; bombe vide dans la filière des aérosols de l'atelier.",
        ),
        data="Aucune donnée consultée ; aucun réglage modifié.",
        incident="Aucun ; si le ventilateur avait été endommagé : pièce étiquetée, client prévenu.",
        conclusion=(
            "Kit choisi pour l'intervention, PC débranché et vidé de ses charges, protection ESD en place, "
            "ventilateurs bloqués pendant le soufflage, pâte refaite en petite quantité, bloc jamais ouvert ; "
            "rendu de test validé et températures notées sur la fiche."
        ),
    ),
    Case(
        key="C2",
        theme="batterie endommagée",
        title="Un portable dont le pavé tactile se soulève",
        context=(
            "Agence de voyages Escale (fictive). Une employée apporte son portable : le pavé tactile se bombe et le "
            "capot ne ferme plus bien. Le portable est encore sous garantie ; il est branché sur son chargeur "
            "depuis ce matin."
        ),
        risks=("batt", "poste"),
        tools=(),
        before=(
            "Diagnostic : batterie lithium-ion gonflée (le pavé est poussé par en dessous) ; risque d'incendie.",
            "Chargeur débranché aussitôt ; le portable n'est pas rallumé.",
        ),
        during=(
            "Aucune pression sur le pavé, aucun démontage forcé, aucune perforation.",
            "Portable posé dans le bac métallique de l'atelier, loin du papier et des cartons.",
            "Garantie : on n'ouvre pas ; le fabricant remplace la batterie.",
        ),
        after=(
            "Client et responsable informés ; photo et date notées sur la fiche.",
            f"Batterie remplacée rendue au fabricant ou, si l'atelier la reçoit : {C2_ROUTE[0].lower()}{C2_ROUTE[1:]}.",
            "Portable de prêt fourni ; les données restent sur le portable (aucune copie demandée).",
        ),
        data=("Données non touchées : le portable n'est pas rallumé avec cette batterie ; si une copie est urgente, "
              "on demande au fabricant comment la faire sans risque (jamais en rechargeant la batterie)."),
        incident="Si la batterie chauffe ou fume : s'éloigner, alerter (112), consignes incendie du site.",
        conclusion=(
            "Batterie gonflée = risque d'incendie : plus de charge, aucune pression, isolement dans un bac "
            "ininflammable, appareil sous garantie non ouvert, renvoi au fabricant, filière des batteries, client "
            "informé et poste de prêt."
        ),
    ),
    Case(
        key="C3",
        theme="données du client",
        title="Réinstaller le PC d'un comptable",
        context=(
            "Fiduciaire Atrium (fictive). Le PC de Marc, comptable, doit être réinstallé. Le disque est chiffré "
            "avec BitLocker. Marc a signé l'accord, contresigné par la responsable du cabinet ; ses documents "
            "ont été copiés hier soir sur le NAS du bureau. Marc est en congé cette semaine."
        ),
        risks=(),
        tools=(),
        before=(
            "Règle 3-2-1 (complément), original et NAS seulement : " + ", ".join(C3_321_BEFORE) + ".",
            "Contrôle de la copie par empreinte SHA-256 : " + ", ".join(C3_INTEGRITY[0]) + " absent ; "
            + ", ".join(C3_INTEGRITY[1]) + " différent : copie incomplète, à refaire.",
            "Prérequis encore manquants : " + " ; ".join(C3_MISSING) + ".",
        ),
        during=(
            "Copie refaite puis relue : nombre de fichiers, tailles et empreintes identiques.",
            "Clé de récupération BitLocker obtenue auprès de l'administrateur (pas sur un papier collé au PC).",
            "Licences et réglages de messagerie notés ; aucun document personnel ouvert.",
        ),
        after=(
            "Réinstallation, puis restauration ; Marc contrôle ses dossiers à son retour.",
            "Copie temporaire de l'atelier effacée après sa validation, effacement noté sur la fiche.",
            "Troisième copie chiffrée hors site proposée au responsable : la règle 3-2-1 est alors respectée.",
        ),
        data="Données comptables confidentielles : copie chiffrée, aucun fichier ouvert hors contrôle, mot de passe de Marc jamais demandé.",
        incident="Si la copie avait été perdue : arrêter, ne rien réinstaller, prévenir aussitôt le responsable.",
        conclusion=(
            "La réinstallation n'a commencé qu'après une copie complète et vérifiée par empreintes, la clé de "
            "récupération en main, les licences notées et l'accord de Marc ; copie temporaire effacée ensuite ; "
            "troisième copie hors site proposée (3-2-1)."
        ),
    ),
    Case(
        key="C4",
        theme="outillage réseau et fibre",
        title="Nouvelle prise au bureau 7 et jarretière optique dans la baie",
        context=(
            "École des Tilleuls (fictive). Un bureau reçoit une prise RJ45 murale reliée au panneau de brassage ; "
            "dans la baie, la jarretière optique vers le bâtiment B doit être remplacée. Le switch de la baie "
            "fournit le PoE aux téléphones."
        ),
        risks=tuple(dict.fromkeys(C4_INTERVENTION.risks + C4_FIBRE.risks)),
        tools=kit(C4_INTERVENTION) + kit(C4_FIBRE),
        before=(
            "Plan de brassage relu, port du switch repéré ; intervention annoncée (coupure du lien optique).",
            "Lame d'insertion du bon type (110 ou LSA) ; dénudeur réglé sur une chute de câble.",
        ),
        during=(
            "Prise : gaine retirée sans entailler, torsades gardées jusqu'au contact, code couleur de la prise, côté coupant vers la chute.",
            "Cordon : ordre T568B aux deux bouts, gaine sous le serre-câble, sertissage franc.",
            "Fibre : module éteint ou jarretière débranchée, jamais regardée en face ; férules nettoyées, capuchons remis.",
        ),
        after=(
            "Testeur wiremap sur le lien prise ↔ panneau, débranché du switch (jamais sur un port PoE actif).",
            "Lien optique vérifié par les voyants du switch, puis le service du bâtiment B.",
            "Éclats et chutes dans le récipient fermé ; outils rangés ; plan de brassage mis à jour.",
        ),
        data="Aucune donnée touchée.",
        incident="Éclat de fibre dans le doigt : le retirer à la pince, désinfecter ; dans l'œil : ne pas frotter, rincer, médecin.",
        conclusion=(
            "Outils choisis pour chaque geste (dénudeur, outil d'insertion, sertisseuse, testeur, kit fibre, "
            "localisateur), testeur jamais sur un port PoE, sécurité laser et éclats respectées, lien et service "
            "testés, plan mis à jour."
        ),
    ),
    Case(
        key="C5",
        theme="fin de vie et DEEE",
        title="Vider la réserve : cinq PC et deux portables à recycler",
        context=(
            "Cabinet dentaire Sourire (fictif). Le responsable demande d'évacuer le vieux matériel de la réserve : "
            "cinq unités centrales, deux portables et quatre toners. Les disques contiennent des dossiers de "
            "patients. Il signe l'accord de recyclage et d'effacement."
        ),
        risks=("batt", "meca"),
        tools=(TOOLS_BY_KEY["tournevis"],),
        before=(
            f"Décision pour des données sans copie à garder, en fin de vie : {C5_DECISION.lower()}.",
            "Inventaire des supports par numéro de série ; accord écrit du responsable, qui en a le droit.",
        ),
        during=(
            ("Disques durs : écrasement complet du disque (technique adaptée) ou destruction ; "
             "SSD : commande d'effacement du SSD ou destruction — un formatage rapide n'efface rien."),
            "Batteries des portables retirées, pôles isolés ; port à deux des cartons lourds.",
        ),
        after=(
            *(f"{item} : {route}." for item, route in C5_ROUTES),
            "Certificat d'effacement ou de destruction par support, joint à la fiche.",
        ),
        data="Dossiers de patients (données de santé, très sensibles) : jamais de matériel recyclé avec un disque lisible.",
        incident="Un disque introuvable à l'inventaire : prévenir aussitôt le responsable (fuite possible), qui décide de la suite.",
        conclusion=(
            "Accord écrit, inventaire des supports, effacement adapté au support ou destruction avec certificat, "
            "batteries isolées dans leur filière, DEEE et toners dans les leurs : rien à la poubelle, aucune donnée "
            "de patient lisible."
        ),
    ),
)
CASES_BY_KEY = {c.key: c for c in CASES}

# =============================================================================================
# 8. Schémas
# =============================================================================================


def tool_cards_svg(tools: tuple[Tool, ...], title: str) -> str:
    """Fiches d'outils empilées : nom, usage, précaution (texte, aucune image d'outil)."""
    width, x0 = 400, 6
    parts = [_text_lines(width // 2, 18, [title], size=13, weight="700", anchor="middle")]
    y = 28
    for tool in tools:
        name = _wrap(tool.name, 48)
        use = _wrap(f"Usage : {tool.use}", 58)
        prec = _wrap(f"Précaution : {tool.precaution}", 58)
        h = 12 + 15 * len(name) + 13 * (len(use) + len(prec)) + 4
        parts.append(
            f'<rect data-tool="{tool.key}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 16, name, size=12.5, weight="700", step=15))
        yy = y + 16 + 15 * len(name)
        parts.append(_text_lines(x0 + 8, yy, use, size=11, step=13))
        parts.append(_text_lines(x0 + 8, yy + 13 * len(use), prec, size=11, step=13))
        y += h + 5
    return _svg(width, y + 4, parts)


# Poste de travail antistatique : (numéro, élément). Le schéma ne porte que les numéros.
ESD_PARTS: tuple[tuple[int, str], ...] = (
    (1, "Tapis antistatique posé sur le plan de travail"),
    (2, "Cordon du tapis relié au point de masse de l'atelier"),
    (3, "Bracelet antistatique au poignet, relié au tapis"),
    (4, "Câble secteur du PC débranché de la prise"),
    (5, "Sachet antistatique pour la pièce retirée"),
)


def _badge(x: int, y: int, number: int) -> str:
    return (
        f'<circle data-badge="{number}" cx="{x}" cy="{y}" r="10" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>'
        + _text_lines(x, y + 4, [str(number)], size=11.5, weight="700", anchor="middle")
    )


def esd_station_svg(*, legend: bool) -> str:
    """Poste de travail ESD vu de face : plan, tapis, PC ouvert débranché, bracelet, sachet,
    point de masse ; chaque élément porte un numéro ; la légende est écrite sous le dessin
    (absente dans la version à compléter)."""
    width = 400
    parts = [
        # plan de travail et tapis
        f'<rect x="20" y="170" width="300" height="14" fill="#d9dde6" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="30" y="162" width="280" height="8" fill="#9fb7d9" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="30" y="184" width="10" height="56" fill="#d9dde6" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="300" y="184" width="10" height="56" fill="#d9dde6" stroke="{_STROKE}" stroke-width="1.5"/>',
        # PC ouvert
        f'<rect x="170" y="92" width="80" height="70" rx="4" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="180" y="102" width="40" height="30" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1"/>',
        _text_lines(210, 152, ["PC ouvert"], size=10.5, anchor="middle"),
        # câble secteur débranché : du PC vers la prise murale, interrompu
        f'<path d="M250 140 H300 V120 H328" fill="none" stroke="{_STROKE}" stroke-width="2"/>',
        f'<rect x="328" y="113" width="14" height="14" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<rect x="362" y="104" width="26" height="32" rx="3" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.5"/>',
        _text_lines(375, 150, ["prise"], size=10.5, anchor="middle"),
        _text_lines(352, 125, ["✗"], size=14, weight="700", anchor="middle"),
        # bracelet : poignet au-dessus du tapis, cordon vers un bouton du tapis
        f'<ellipse cx="90" cy="70" rx="22" ry="10" fill="#ffffff" stroke="{_STROKE}" stroke-width="2"/>',
        f'<path d="M90 80 C90 120 70 130 70 160" fill="none" stroke="{_STROKE}" stroke-width="1.5" stroke-dasharray="4 2"/>',
        f'<circle cx="70" cy="164" r="3" fill="{_STROKE}"/>',
        _text_lines(90, 52, ["poignet"], size=10.5, anchor="middle"),
        # cordon du tapis vers le point de masse
        f'<path d="M40 166 H10 V250" fill="none" stroke="{_STROKE}" stroke-width="1.5"/>',
        f'<path d="M0 250 H20 M4 256 H16 M8 262 H12" stroke="{_STROKE}" stroke-width="2"/>',
        # sachet antistatique
        f'<rect x="262" y="132" width="34" height="30" rx="3" fill="#e6e0f2" stroke="{_STROKE}" stroke-width="1.5"/>',
        # numéros
        _badge(130, 156, 1),
        _badge(24, 210, 2),
        _badge(122, 70, 3),
        _badge(345, 140, 4),
        _badge(279, 120, 5),
    ]
    height = 274
    if legend:  # repères écrits seulement dans la version complète (ils donneraient la réponse)
        parts.append(_text_lines(30, 262, ["point de masse"], size=10.5))
        parts.append(_text_lines(279, 151, ["sachet"], size=9, anchor="middle"))
        y = height + 6
        for number, label in ESD_PARTS:
            parts.append(_text_lines(10, y + 12, [f"{number}. {label}"], size=11.5))
            y += 16
        height = y + 6
    return _svg(width, height, parts)


def rule_321_svg(copies: tuple[Copy, ...]) -> str:
    """Les copies d'un exemple, une case chacune (support, lieu), et le bilan 3-2-1 calculé."""
    width, x0 = 400, 6
    parts = [_text_lines(width // 2, 18, ["Règle 3-2-1 : un exemple conforme"], size=13, weight="700", anchor="middle")]
    y = 30
    for i, c in enumerate(copies, start=1):
        lines = _wrap(f"{i}. {c.label}", 52)
        detail = f"Support : {c.support} · {'hors site' if c.offsite else 'sur place'}"
        h = 14 + 15 * len(lines) + 14
        parts.append(
            f'<rect data-copy="{i}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 16, lines, size=12, weight="700", step=15))
        parts.append(_text_lines(x0 + 8, y + 16 + 15 * len(lines), [detail], size=11))
        y += h + 5
    missing = check_321(copies)
    supports = len({SUPPORT_TYPES[c.support] for c in copies})
    offsite = sum(c.offsite for c in copies)
    checks = (
        f"{'✓' if MISS_3 not in missing else '✗'} 3 copies au moins : {len(copies)}",
        f"{'✓' if MISS_2 not in missing else '✗'} 2 types de supports au moins : {supports}",
        f"{'✓' if MISS_1 not in missing else '✗'} 1 copie hors site au moins : {offsite}",
    )
    parts.append(_text_lines(x0 + 4, y + 14, list(checks), size=12, weight="700", step=17))
    return _svg(width, y + 14 + 17 * len(checks), parts)


def waste_svg() -> str:
    """Nature du déchet → filière (texte), une ligne par nature."""
    width, x0 = 400, 6
    parts = [_text_lines(width // 2, 18, ["Fin de vie : à chaque déchet sa filière"], size=13, weight="700",
                         anchor="middle")]
    y = 30
    for kind in WASTE_KINDS:
        k_lines = _wrap(kind, 52)
        r_lines = _wrap(f"→ {waste_route(kind)}", 56)
        examples = _wrap("Ex. : " + ", ".join(i[0].lower() + i[1:] for i, k in WASTE_ITEMS if k == kind), 58)
        h = 12 + 15 * len(k_lines) + 13 * (len(r_lines) + len(examples)) + 4
        parts.append(
            f'<rect data-waste="{WASTE_KINDS.index(kind)}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" '
            f'rx="6" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 16, k_lines, size=12, weight="700", step=15))
        yy = y + 16 + 15 * len(k_lines)
        parts.append(_text_lines(x0 + 8, yy, r_lines, size=11, weight="700", step=13))
        parts.append(_text_lines(x0 + 8, yy + 13 * len(r_lines), examples, size=11, step=13))
        y += h + 5
    parts.append(_text_lines(x0, y + 12, ["✗ jamais dans la poubelle ordinaire"], size=11.5, weight="700"))
    return _svg(width, y + 20, parts)


def checklist_svg(sections: tuple[tuple[str, tuple[str, ...]], ...]) -> str:
    """Liste de contrôle : sections empilées, une case ☐ par point."""
    width, x0 = 400, 6
    parts: list[str] = []
    y = 6
    for title, items in sections:
        lines = [_wrap(item, 52) for item in items]
        h = 26 + sum(14 * len(ls) + 4 for ls in lines) + 4
        parts.append(
            f'<rect data-section="{escape(title)}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 18, [title], size=13, weight="700"))
        yy = y + 36
        for ls in lines:
            parts.append(_text_lines(x0 + 10, yy, ["☐"], size=12.5, weight="700"))
            parts.append(_text_lines(x0 + 28, yy, ls, size=11.5, step=14))
            yy += 14 * len(ls) + 4
        y += h + 6
    return _svg(width, y, parts)


def do_dont_svg(do: tuple[str, ...], dont: tuple[str, ...]) -> str:
    """Deux listes empilées (pleine largeur, lisibles sur mobile) : « À faire » (✓) puis
    « Interdit » (✗) ; la distinction est écrite, pas seulement colorée."""
    width, x0 = 400, 6
    parts: list[str] = []
    y = 6
    for title, items, mark, fill in (("À faire", do, "✓", "#e9f5ec"), ("Interdit", dont, "✗", "#fbecec")):
        lines = [_wrap(item, 50) for item in items]
        h = 30 + sum(14 * len(ls) + 5 for ls in lines) + 2
        parts.append(
            f'<rect data-list="{escape(title)}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{fill}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 18, [title], size=13, weight="700"))
        yy = y + 36
        for ls in lines:
            parts.append(_text_lines(x0 + 10, yy, [mark], size=12.5, weight="700"))
            parts.append(_text_lines(x0 + 28, yy, ls, size=11.5, step=14))
            yy += 14 * len(ls) + 5
        y += h + 6
    return _svg(width, y, parts)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


def tree_alt(tree: Tree, questions: tuple[tuple[str, str], ...] | None = None) -> str:
    qs = questions or tree.questions
    return (f"Arbre de décision « {tree.title} ». Départ : {tree.start} "
            + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(qs, start=1))
            + f" Si tout est oui : {tree.final}")


def _tools_alt(tools: tuple[Tool, ...], family: str) -> str:
    return (f"{len(tools)} fiches d'outils, famille « {family} » : "
            + " ; ".join(f"{t.name} — usage : {t.use} — précaution : {t.precaution}" for t in tools) + ".")


PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Débrancher avant d'intervenir", DISCONNECT_STEPS),
    ("Batterie gonflée ou endommagée", BATTERY_STEPS),
    ("Avant d'effacer ou de réinstaller", AUTH_STEPS),
    ("Réagir à un incident", INCIDENT_STEPS),
    ("Utiliser un multimètre sans danger", MULTIMETER_RULES),
)

PC_TOOLS_FIGURE = Figure(
    key="pr28-outils-pc",
    title="Outillage du poste de travail (PC)",
    alt=_tools_alt(PC_TOOLS, FAM_PC),
    caption="Chaque outil a un usage précis et une précaution ; l'outil adapté évite d'abîmer la pièce et de se blesser.",
    svg=tool_cards_svg(PC_TOOLS, "Outillage PC : usage et précaution"),
)
NET_TOOLS_FIGURE = Figure(
    key="pr28-outils-reseau",
    title="Outillage réseau : cuivre, coaxial et fibre",
    alt=_tools_alt(NET_TOOLS, FAM_NET),
    caption="Outils du câblage : le testeur ne se branche jamais sur un port actif ; la fibre ne se regarde jamais en face.",
    svg=tool_cards_svg(NET_TOOLS, "Outillage réseau : usage et précaution"),
)
ESD_FIGURE = Figure(
    key="pr28-poste-esd",
    title="Poste de travail antistatique (ESD)",
    alt="Schéma d'un poste de travail vu de face, éléments numérotés : "
    + " ; ".join(f"{n}. {label}" for n, label in ESD_PARTS)
    + ". Le PC ouvert est posé sur le tapis ; le câble secteur s'arrête avant la prise murale (débranché).",
    caption="Selon la procédure de l'atelier : tapis à la masse, bracelet relié au tapis, PC débranché, pièce en sachet.",
    svg=esd_station_svg(legend=True),
)
DISCONNECT_FIGURE = _proc_figure("pr28-procedure-debranchement", 1, PROCEDURES[0][0], DISCONNECT_STEPS,
                                 "Rien ne s'ouvre avant le débranchement : l'ordre protège la personne, puis la pièce.")
BATTERY_FIGURE = _proc_figure("pr28-procedure-batterie", 2, PROCEDURES[1][0], BATTERY_STEPS,
                              "Une batterie lithium-ion gonflée peut s'enflammer : on ne la charge plus et on ne la presse pas.")
AUTH_FIGURE = _proc_figure("pr28-procedure-avant-effacement", 3, PROCEDURES[2][0], AUTH_STEPS,
                           "Pas de copie vérifiée et d'accord écrit, pas d'effacement ni de réinstallation.")
INCIDENT_FIGURE = _proc_figure("pr28-procedure-incident", 4, PROCEDURES[3][0], INCIDENT_STEPS,
                               "Les personnes d'abord, puis les données, puis le matériel ; tout est noté.")
MULTIMETER_FIGURE = _proc_figure("pr28-procedure-multimetre", 5, PROCEDURES[4][0], MULTIMETER_RULES,
                                 "Le multimètre sert aux basses tensions et aux circuits hors tension, jamais au secteur.")
FIBRE_FIGURE = Figure(
    key="pr28-securite-fibre",
    title="Sécurité laser et éclats de fibre",
    alt="Deux listes. À faire : " + " ; ".join(FIBRE_DO) + ". Interdit : " + " ; ".join(FIBRE_DONT) + ".",
    caption="La lumière d'un module optique est souvent invisible : l'absence de lumière visible ne prouve rien.",
    svg=do_dont_svg(FIBRE_DO, FIBRE_DONT),
)
CLEAN_FIGURE = Figure(
    key="pr28-nettoyage",
    title="Dépoussiérer et refaire la pâte thermique",
    alt="Deux listes. À faire : " + " ; ".join(CLEAN_DO) + ". Interdit : " + " ; ".join(CLEAN_DONT) + ".",
    caption="Un ventilateur entraîné par le jet d'air tourne trop vite et peut s'abîmer : on bloque ses pales.",
    svg=do_dont_svg(CLEAN_DO, CLEAN_DONT),
)
RULE321_FIGURE = Figure(
    key="pr28-regle-321",
    title="Règle de sauvegarde 3-2-1 (complément)",
    alt="Trois copies d'un même dossier : "
    + " ; ".join(f"{i}. {c.label}, {c.support}, {'hors site' if c.offsite else 'sur place'}"
                 for i, c in enumerate(C3_COPIES_AFTER, start=1))
    + ". Bilan : 3 copies, 2 types de supports au moins, 1 copie hors site : conforme.",
    caption="3 copies (l'original compris), 2 types de supports, 1 copie hors site ; une copie se vérifie avant de servir.",
    svg=rule_321_svg(C3_COPIES_AFTER),
)
WASTE_FIGURE = Figure(
    key="pr28-filieres-deee",
    title="Fin de vie : déchets et filières",
    alt="Quatre natures de déchets et leur filière : "
    + " ; ".join(f"{k} → {waste_route(k)}" for k in WASTE_KINDS) + ". Jamais dans la poubelle ordinaire.",
    caption="Un support de données ne part au recyclage qu'effacé de façon certifiée ou détruit.",
    svg=waste_svg(),
)
CHECKLIST_FIGURE = Figure(
    key="pr28-liste-controle",
    title="Liste de contrôle d'une intervention",
    alt="Liste de contrôle en trois parties. "
    + " ".join(f"{title} : " + " ; ".join(items) + "." for title, items in CHECKLIST),
    caption="À cocher sur la fiche d'intervention : avant, pendant et après.",
    svg=checklist_svg(CHECKLIST),
)
INCIDENT_TREE_FIGURE = Figure(
    key="pr28-arbre-incident",
    title=f"Arbre — {INCIDENT_TREE.title}",
    alt=tree_alt(INCIDENT_TREE),
    caption="On descend tant que la réponse est « oui » ; au premier « non », on suit la piste de droite.",
    svg=decision_tree_svg(INCIDENT_TREE.questions, INCIDENT_TREE.final),
)

PR28_FIGURES: tuple[Figure, ...] = (
    PC_TOOLS_FIGURE,
    NET_TOOLS_FIGURE,
    MULTIMETER_FIGURE,
    FIBRE_FIGURE,
    DISCONNECT_FIGURE,
    ESD_FIGURE,
    BATTERY_FIGURE,
    CLEAN_FIGURE,
    RULE321_FIGURE,
    AUTH_FIGURE,
    WASTE_FIGURE,
    CHECKLIST_FIGURE,
    INCIDENT_FIGURE,
    INCIDENT_TREE_FIGURE,
)

# Schémas à compléter (exercices), servis en fichiers statiques comme PR18 à PR27 ------------

MARKS = ("①", "②", "③", "④")

ESD_BLANK_FIGURE = Figure(
    key="pr28-poste-esd-a-completer",
    title="Poste de travail antistatique à compléter",
    alt=(
        "Schéma à compléter d'un poste de travail vu de face, cinq numéros sans légende : 1 sur la bande posée "
        "sur le plan de travail ; 2 sur le cordon qui descend du bord gauche de cette bande vers un symbole de "
        "masse ; 3 sur l'anneau au poignet, dont un cordon pointillé rejoint la bande ; 4 sur le câble qui part "
        "du PC ouvert et s'arrête, marqué d'une croix, avant la prise murale ; 5 sur la petite pochette posée à "
        "côté du PC."
    ),
    caption="Schéma à compléter : nomme les éléments 1 à 5 et donne le rôle de chacun.",
    svg=esd_station_svg(legend=False),
)


def _blank_tree(tree: Tree, blank_numbers: tuple[int, ...]) -> tuple[tuple[tuple[str, str], ...], dict[str, str]]:
    """Remplace la piste « si non » des questions données (numéros 1…) par ①, ②… ; renvoie
    l'arbre à afficher et les réponses attendues."""
    marks = dict(zip(blank_numbers, MARKS, strict=False))
    shown = tuple((q, marks.get(i, n)) for i, (q, n) in enumerate(tree.questions, start=1))
    answers = {marks[i]: tree.questions[i - 1][1] for i in blank_numbers}
    return shown, answers


INCIDENT_BLANK_NUMBERS = (1, 2, 3, 4)
INCIDENT_BLANK_QUESTIONS, INCIDENT_BLANK_ANSWERS = _blank_tree(INCIDENT_TREE, INCIDENT_BLANK_NUMBERS)
INCIDENT_BLANK_FIGURE = Figure(
    key="pr28-arbre-incident-a-completer",
    title="Arbre d'incident à compléter",
    alt=tree_alt(INCIDENT_TREE, INCIDENT_BLANK_QUESTIONS),
    caption="Schéma à compléter : conduite à tenir en ①, ②, ③ et ④ quand la réponse est « non ».",
    svg=decision_tree_svg(INCIDENT_BLANK_QUESTIONS, INCIDENT_TREE.final),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (ESD_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr28-poste-esd-a-completer.svg"),
    (INCIDENT_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr28-arbre-incident-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR27)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


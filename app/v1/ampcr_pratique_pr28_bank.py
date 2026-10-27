"""PR28 « Outillage, sécurité et protection des données » — exercices corrigés et mini-examen
(ticket #227).

Même organisation que PR27 (`app.v1.ampcr_pratique_pr27_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 22 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — **choix d'outil** (outil propre à une tâche, kit d'une intervention,
  multimètre, testeur d'alimentation), **risques et sécurité** (situations, nettoyage, fibre),
  **procédures à ordonner** (débranchement, batterie gonflée, prise murale, incident),
  **protection des données** (3-2-1, intégrité d'une copie, chiffrement, autorisation,
  confidentialité), **fin de vie** (filières DEEE), **deux schémas à compléter** (poste
  antistatique, arbre d'incident), un **parcours d'arbre** et des **rédactions** (fiche sécurité,
  incident de données) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, entreprises et fichiers sont **fictifs** ; outils, tolérances,
manques de la règle 3-2-1, écarts d'empreintes, prérequis manquants, filières et pistes de
l'arbre viennent des fonctions de `app.v1.ampcr_pratique_pr28_figures` (et de PR02 pour les
tolérances du bloc).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr02_figures import RAILS, tolerance_range, volts, within_tolerance
from app.v1.ampcr_pratique_pr04_bank import _c, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr27_figures import walk
from app.v1.ampcr_pratique_pr28_figures import (
    BATTERY_STEPS,
    CLEAN_DO,
    CLEAN_DONT,
    CMOS_NOMINAL,
    DISCONNECT_STEPS,
    ESD_PARTS,
    INCIDENT_BLANK_ANSWERS,
    INCIDENT_STEPS,
    INCIDENT_TREE,
    INTERVENTIONS_BY_KEY,
    MISSES_321,
    OP_REINSTALL,
    OP_RESET,
    PRE_AUTHORIZED,
    PRE_BACKUP,
    PRE_CONSENT,
    PRE_KEY,
    PRE_LICENSES,
    PREREQUISITES,
    RISK_NAMES,
    RISKS_BY_KEY,
    ROUTES,
    SAFETY_SHEET_FIELDS,
    STATIC_BY_KEY,
    SUP_CLOUD,
    SUP_EXTERNAL,
    SUP_INTERNAL,
    SUP_NAS,
    SUP_USB_KEY,
    TASKS,
    TOOLS,
    TOOLS_BY_KEY,
    W_BATTERY,
    W_DATA,
    W_EEE,
    W_TONER,
    WASTE_ITEMS,
    Copy,
    check_321,
    compare_copy,
    fingerprint,
    kit,
    missing_prerequisites,
    waste_route,
)

PR28_CODE = "PR28"

KIND_TOOL = "choix d'outil"
KIND_RISK = "risques et sécurité"
KIND_ORDER = "procédure à ordonner"
KIND_DATA = "protection des données"
KIND_WASTE = "fin de vie et DEEE"
KIND_SCHEMA = "schéma à compléter"
KIND_TREE = "arbre de décision"
KIND_WRITE = "rédaction"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-C02", "AP-C03"})
R_SAFE = ("AP-C02", "AP-C01")  # sécurité de l'intervention, réponse écrite de technicien
R_DATA = ("AP-C03", "AP-C01")  # protection des données du client
R_BOTH = ("AP-C02", "AP-C03", "AP-C01")
R_HW = ("AP-C02", "AP-14", "AP-C01")  # intervention dans le matériel (montage, démontage)
R_NET = ("AP-C02", "AP-20", "AP-C01")  # outillage de câblage (précautions, connecteurs)
R_FIBRE = ("AP-C02", "AP-21", "AP-C01")  # fibre optique (connexion)


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _text_doc(title: str, text: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="texte", content_text=text)


def _letters(n: int) -> tuple[str, ...]:
    return tuple(chr(ord("a") + i) for i in range(n))


def _tool_names(tools) -> str:
    return ", ".join(t.name for t in tools)


def _fr(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def _rail_rows(measured: dict[str, float]) -> tuple[tuple[str, str], ...]:
    return tuple((r.name, volts(measured[r.name])) for r in RAILS)


def _rails_out(measured: dict[str, float]) -> tuple[str, ...]:
    return tuple(r.name for r in RAILS if not within_tolerance(r, measured[r.name]))


def _range(name: str) -> str:
    rail = next(r for r in RAILS if r.name == name)
    low, high = tolerance_range(rail)
    return f"{volts(low)} à {volts(high)}"


def _listing(files: tuple[tuple[str, str], ...]) -> tuple[tuple[str, int, str], ...]:
    return tuple((name, len(text.encode("utf-8")) * 1000, fingerprint(text)) for name, text in files)


def _listing_rows(rows: tuple[tuple[str, int, str], ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple((name, f"{size:,}".replace(",", " "), fp) for name, size, fp in rows)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_TASKS = TASKS
E01_TOOLS = tuple(dict.fromkeys(key for _t, key in E01_TASKS))
E01_CATEGORIES = tuple(TOOLS_BY_KEY[k].name for k in E01_TOOLS)
E01_CORRECT = tuple(E01_TOOLS.index(key) for _t, key in E01_TASKS)

E02_CASES: tuple[tuple[str, str], ...] = (
    ("Un stagiaire touche les contacts d'une barrette neuve sans bracelet, sur la moquette", "esd"),
    ("Un collègue veut mesurer la tension de la prise murale avec le multimètre de l'atelier", "elec"),
    ("Un bloc d'alimentation fait du bruit : le client propose de l'ouvrir pour le nettoyer", "psu"),
    ("Un portable tombé hier sent le brûlé et sa coque est déformée près de la batterie", "batt"),
    ("Dépoussiérage d'un PC très encrassé dans le local d'archives fermé, sans fenêtre", "vent"),
    ("Retrait d'un serveur de 25 kg de la baie par une seule personne", "meca"),
    ("Le technicien regarde l'extrémité d'une jarretière pour voir « si la lumière passe »", "laser"),
    ("Un café posé à côté du PC ouvert, des câbles qui traversent le passage", "poste"),
    ("Une tôle du boîtier, coupante, manipulée à mains nues", "meca"),
    ("Un éclat de fibre coupée tombé sur le plan où l'équipe mange à midi", "laser"),
)
E02_CATEGORIES = RISK_NAMES
E02_CORRECT = tuple(list(RISKS_BY_KEY).index(k) for _t, k in E02_CASES)

E03_STEPS = _labels(DISCONNECT_STEPS)
E04_STEPS = _labels(BATTERY_STEPS)

E05_INTERVENTION = INTERVENTIONS_BY_KEY["cmos"]
E05_KIT = kit(E05_INTERVENTION)

E06_MEASURED = {"+12 V": 11.31, "+5 V": 5.08, "+3,3 V": 3.27, "+5 VSB": 4.93, "−12 V": -11.6}
E06_OUT = _rails_out(E06_MEASURED)

E07_MEASURED = 2.41

E08_ELEMENTS = CLEAN_DO + CLEAN_DONT
E08_SHOWN = (5, 0, 7, 2, 9, 1, 6, 3, 8, 4)  # ordre d'affichage mélangé
E08_DISPLAYED = tuple(E08_ELEMENTS[i] for i in E08_SHOWN)
E08_CORRECT = tuple(0 if i < len(CLEAN_DO) else 1 for i in E08_SHOWN)

E09_STEPS: tuple[str, ...] = (
    "Repérer la prise et le câble d'après le plan de brassage (même étiquette aux deux bouts)",
    "Retirer la gaine avec le dénudeur réglé sur une chute de câble",
    "Placer chaque paire selon le code couleur de la prise, torsades gardées jusqu'au contact",
    "Enfoncer chaque fil avec l'outil d'insertion, côté coupant vers la chute",
    "Refermer la prise et la fixer dans son boîtier",
    "Tester le lien avec le testeur de câble, débranché de tout port actif",
)

E11_PLANS: tuple[tuple[str, tuple[Copy, ...]], ...] = (
    ("Original sur le PC, disque externe USB au bureau, copie en ligne",
     (Copy("PC", SUP_INTERNAL, False), Copy("USB", SUP_EXTERNAL, False), Copy("en ligne", SUP_CLOUD, True))),
    ("Original sur le PC et une copie en ligne, rien d'autre",
     (Copy("PC", SUP_INTERNAL, False), Copy("en ligne", SUP_CLOUD, True))),
    ("Original sur le PC, un disque externe au bureau, un second disque externe chez la gérante",
     (Copy("PC", SUP_INTERNAL, False), Copy("USB 1", SUP_EXTERNAL, False), Copy("USB 2", SUP_EXTERNAL, True))),
    ("Original sur le PC, copie sur le NAS, copie sur une clé USB rangée dans le tiroir du bureau",
     (Copy("PC", SUP_INTERNAL, False), Copy("NAS", SUP_NAS, False), Copy("clé", SUP_USB_KEY, False))),
    ("Original sur le PC, copie sur le NAS, disque externe déposé chaque vendredi dans un coffre à la banque",
     (Copy("PC", SUP_INTERNAL, False), Copy("NAS", SUP_NAS, False), Copy("coffre", SUP_EXTERNAL, True))),
    ("Original sur le PC, clé USB emportée chaque soir par le gérant, disque externe au bureau",
     (Copy("PC", SUP_INTERNAL, False), Copy("clé", SUP_USB_KEY, True), Copy("USB", SUP_EXTERNAL, False))),
)
E11_OK = "Conforme à la règle 3-2-1"
E11_CATEGORIES = (E11_OK, *(f"Non conforme : {m}" for m in MISSES_321))
E11_VERDICTS = tuple(check_321(copies) for _t, copies in E11_PLANS)
E11_CORRECT = tuple(0 if not v else 1 + MISSES_321.index(v[0]) for v in E11_VERDICTS)

E12_FILES: tuple[tuple[str, str], ...] = (
    ("Dossiers-patients.accdb", "base des dossiers du cabinet vétérinaire, octobre"),
    ("Agenda-2026.ics", "rendez-vous de l'année"),
    ("Radios-octobre.zip", "archive des radiographies d'octobre"),
    ("Tarifs.xlsx", "grille des tarifs des soins"),
    ("Factures-T3.pdf", "factures du troisième trimestre"),
)
E12_SOURCE = _listing(E12_FILES)
E12_COPY: tuple[tuple[str, int, str], ...] = (
    E12_SOURCE[0],
    E12_SOURCE[1],
    ("Radios-octobre.zip", E12_SOURCE[2][1], fingerprint("archive des radiographies d'oct")),
    E12_SOURCE[4],
)
E12_MISSING, E12_DIFFERENT = compare_copy(E12_SOURCE, E12_COPY)

E14_DONE = frozenset({PRE_BACKUP, PRE_LICENSES})
E14_MISSING = missing_prerequisites(OP_RESET, E14_DONE, keep_data=True, encrypted=False)

E15_ELEMENTS = tuple(item for item, _k in WASTE_ITEMS)
E15_CORRECT = tuple(ROUTES.index(waste_route(kind)) for _i, kind in WASTE_ITEMS)

E20_STEPS = _labels(INCIDENT_STEPS)

E22_ANSWERS = (True, True, True, False)
E22_RESULT = walk(INCIDENT_TREE, E22_ANSWERS)

# --- Mini-examen -------------------------------------------------------------------------------

X01_INTERVENTION = INTERVENTIONS_BY_KEY["alim"]
X01_KIT = kit(X01_INTERVENTION)
X01_LIST = tuple(t.name for t in TOOLS if t.family == TOOLS_BY_KEY["tournevis"].family)

X02_MEASURED = {"+12 V": 12.18, "+5 V": 4.71, "+3,3 V": 3.31, "+5 VSB": 5.02, "−12 V": -12.3}
X02_OUT = _rails_out(X02_MEASURED)

X04_STEPS: tuple[str, ...] = (
    "Arrêter le PC, interrupteur du bloc sur 0, câble secteur débranché",
    "Bracelet antistatique relié selon la procédure de l'atelier",
    CLEAN_DONT[0],
    CLEAN_DO[1],
    CLEAN_DONT[1],
    "Remonter le capot et faire un test de fonctionnement",
)
X04_ERRORS = tuple(i + 1 for i, step in enumerate(X04_STEPS) if step in CLEAN_DONT)

X05_COPIES: tuple[Copy, ...] = (
    Copy("Original : dossiers du bureau d'études sur le serveur", SUP_INTERNAL, False),
    Copy("Copie nocturne sur le NAS de la salle serveur", SUP_NAS, False),
    Copy("Copie hebdomadaire sur un disque externe rangé dans l'armoire du bureau", SUP_EXTERNAL, False),
)
X05_MISSING = check_321(X05_COPIES)

X06_FILES: tuple[tuple[str, str], ...] = (
    ("Plans-maison-Dupont.dwg", "plans de la maison Dupont, version 4"),
    ("Métrés.xlsx", "métrés et quantités du chantier"),
    ("Photos-chantier.zip", "photos du chantier, semaine 42"),
    ("Devis-signé.pdf", "devis signé par le client"),
)
X06_SOURCE = _listing(X06_FILES)
X06_COPY: tuple[tuple[str, int, str], ...] = (
    X06_SOURCE[0],
    ("Métrés.xlsx", X06_SOURCE[1][1], fingerprint("métrés et quantités du chantier (ancienne)")),
    X06_SOURCE[3],
)
X06_MISSING, X06_DIFFERENT = compare_copy(X06_SOURCE, X06_COPY)

X07_DONE = frozenset({PRE_BACKUP, PRE_CONSENT, PRE_AUTHORIZED})
X07_MISSING = missing_prerequisites(OP_REINSTALL, X07_DONE, keep_data=True, encrypted=True)

X09_ITEMS: tuple[tuple[str, str], ...] = (
    ("Imprimante jet d'encre hors d'usage, sans cartouches", W_EEE),
    ("Batterie d'onduleur usagée", W_BATTERY),
    ("SSD du PC de la direction", W_DATA),
    ("Cartouches d'encre vides", W_TONER),
)
X09_ROUTES = tuple((item, waste_route(kind)) for item, kind in X09_ITEMS)

X10_ANSWERS = (False,)
X10_RESULT = walk(INCIDENT_TREE, X10_ANSWERS)


# =============================================================================================
# 22 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="À chaque tâche son outil",
        question_type="classification",
        requirement_ids=R_SAFE,
        kind=KIND_TOOL,
        context=(
            "Tu prépares la caisse à outils d'un nouveau technicien. Ton responsable a écrit neuf tâches courantes "
            "de l'atelier et de la pose réseau ; pour chacune, un seul outil de l'inventaire est le bon. Il te "
            "demande de les associer avant la première intervention du nouveau."
        ),
        instructions=("Range chaque tâche sous l'outil qui lui est propre.",),
        criteria=(
            _c("Associations", 4.5, " ; ".join(f"{t} → {TOOLS_BY_KEY[k].name}" for t, k in E01_TASKS) + " (0,5 pt par tâche)."),
        ),
        correction=(
            "Câblage : la sertisseuse fixe une fiche RJ45 ; l'outil d'insertion enfonce les fils dans les contacts d'une prise murale ou d'un panneau ; le dénudeur retire la gaine sans entailler ; le testeur de câble vérifie chaque fil ; le localisateur visuel (laser rouge) fait briller une cassure de fibre.",
            "Poste : le testeur d'alimentation contrôle le bloc par ses connecteurs ; le multimètre mesure une basse tension continue (pile CMOS) ; le bracelet et le tapis antistatiques protègent la barrette ; la pâte thermique, après nettoyage à l'alcool isopropylique, refait le contact entre le processeur et le radiateur.",
        ),
        classification=Classification(categories=E01_CATEGORIES, elements=tuple(t for t, _k in E01_TASKS), correct=E01_CORRECT),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Quel risque dans chaque situation ?",
        question_type="classification",
        requirement_ids=R_SAFE,
        kind=KIND_RISK,
        context=(
            "Pendant une semaine, le responsable de l'atelier a noté dix situations dangereuses observées chez les "
            "techniciens et les stagiaires. Pour la réunion sécurité, tu dois nommer le risque principal de chacune "
            "avant de rappeler la prévention."
        ),
        instructions=("Range chaque situation dans son risque principal.",),
        criteria=(
            _c("Classement", 5, " ; ".join(f"{t} → {RISKS_BY_KEY[k].name}" for t, k in E02_CASES) + " (0,5 pt par situation)."),
        ),
        correction=(
            "Barrette touchée sans bracelet : ESD. Mesure sur la prise murale : électricité (le 230 V ne se mesure pas avec le multimètre de l'atelier). Bloc à ouvrir : jamais, ses condensateurs restent chargés. Portable tombé, odeur de brûlé, coque déformée : batterie endommagée, risque d'incendie.",
            "Local fermé et poussière : ventilation. Serveur de 25 kg et tôle coupante : risques mécaniques (port à deux, gants). Regarder une jarretière et éclat sur le plan du repas : laser et éclats de fibre. Café et câbles dans le passage : poste de travail.",
        ),
        classification=Classification(categories=E02_CATEGORIES, elements=tuple(t for t, _k in E02_CASES), correct=E02_CORRECT),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Débrancher un PC avant de l'ouvrir",
        question_type="ordering",
        requirement_ids=R_HW,
        kind=KIND_ORDER,
        context=(
            "Une comptable te confie son PC tour pour ajouter une barrette de mémoire. Elle travaille encore dessus "
            "quand tu arrives. Les six étapes qui précèdent l'ouverture du boîtier ont été mélangées sur l'aide-mémoire "
            "du stagiaire ; tu les remets dans l'ordre."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Prévenir → arrêter le système → couper le bloc → débrancher → vider les charges → se protéger de l'ESD (0,5 pt par position)."),
        ),
        correction=(
            "On prévient d'abord (travail enregistré, sauvegarde existante), puis on arrête le système proprement : couper le courant d'un PC allumé peut abîmer des fichiers. Ensuite l'interrupteur du bloc sur 0 et le câble secteur débranché (avec les périphériques).",
            "Un appui de quelques secondes sur le bouton de démarrage, câble débranché, vide les charges résiduelles de la carte. Le bracelet antistatique vient en dernier, juste avant d'ouvrir : il protège la barrette, le débranchement protège la personne.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (3, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Une batterie gonflée à l'accueil de l'atelier",
        question_type="ordering",
        requirement_ids=R_SAFE,
        kind=KIND_ORDER,
        context=(
            "Un client dépose au comptoir une tablette sous garantie dont l'écran se décolle : la batterie a gonflé. "
            "Elle est encore branchée sur son chargeur. Le stagiaire a noté six gestes sur des cartes, dans le "
            "désordre ; tu les remets dans l'ordre de la procédure du cours."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Ne plus charger → ne pas déformer → isoler → prévenir → faire remplacer → éliminer (0,5 pt par position)."),
        ),
        correction=(
            "Une batterie lithium-ion gonflée peut s'enflammer : on arrête d'abord la charge, on ne presse ni ne perce rien (même pour refermer l'écran), puis on isole l'appareil dans un bac ininflammable, loin du papier et des cartons.",
            "On prévient ensuite le client et le responsable (photo, date sur la fiche). L'appareil est sous garantie : on ne l'ouvre pas, le fabricant remplace la batterie. Une batterie à éliminer part, pôles isolés, dans la filière des piles et batteries ; jamais à la poubelle.",
        ),
        ordering=_shuffled_ordering(E04_STEPS, (2, 5, 0, 3, 1, 4)),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Préparer le kit d'une intervention sur la pile CMOS",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_TOOL,
        context=(
            "Le PC de la réception d'un hôtel perd sa date et son heure à chaque coupure de courant. Ton responsable "
            "t'envoie contrôler puis remplacer la pile CMOS (pile bouton CR2032 de la carte mère). Le document 1 est "
            "l'inventaire de la caisse à outils : tu n'emportes que ce qui sert."
        ),
        documents=(_table("Document 1 — Inventaire de la caisse à outils (support fictif)", ("Repère", "Outil"),
                          *((letter, t.name) for letter, t in zip(_letters(len(TOOLS)), TOOLS, strict=True))),),
        instructions=(
            "Choisis les outils nécessaires dans le document 1.",
            "Pour chacun, donne une précaution d'emploi.",
        ),
        criteria=(
            _c("Kit", 2, _tool_names(E05_KIT) + " (0,5 pt par outil ; aucun outil de câblage)."),
            _c("Précautions", 2, " ; ".join(f"{t.name} : {t.precaution}" for t in E05_KIT) + " (une précaution juste par outil)."),
        ),
        correction=(
            "Kit : " + _tool_names(E05_KIT) + ". Les tournevis ouvrent le boîtier ; le bracelet et le tapis protègent la carte mère ; le multimètre mesure la pile retirée ; la pince à bec fin aide à saisir une pile coincée, hors tension seulement.",
            "Précautions : PC débranché et charges vidées avant d'ouvrir ; multimètre en tension continue, sur un calibre adapté, cordon noir sur COM ; pince jamais utilisée comme levier sur le support de pile ; la pile usagée part dans la filière des piles.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Lire les mesures d'un testeur d'alimentation",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_TOOL,
        context=(
            "Un PC de bureau s'éteint seul dès qu'on lance un logiciel lourd. Tu démontes le bloc d'alimentation et tu "
            "le contrôles avec le testeur d'alimentation de l'atelier. Le document 1 donne les valeurs affichées ; "
            "les tolérances sont celles du cours PR02 (±5 %, ±10 % pour −12 V)."
        ),
        documents=(_table("Document 1 — Écran du testeur d'alimentation (support fictif)", ("Tension", "Valeur affichée"),
                          *_rail_rows(E06_MEASURED)),),
        instructions=(
            "Indique la ou les tensions hors tolérance, avec la plage admise.",
            "Donne ta conclusion et ce que tu fais du bloc.",
        ),
        criteria=(
            _c("Hors tolérance", 2, f"{', '.join(E06_OUT)} : {volts(E06_MEASURED[E06_OUT[0]])} pour une plage de {_range(E06_OUT[0])} ; les autres sont dans leur plage."),
            _c("Conclusion", 2, "Bloc défaillant : le remplacer par un bloc de puissance et de connectique adaptées ; ne jamais l'ouvrir ni le réparer ; un testeur à vide ne prouve pas la tenue en charge, mais une tension déjà hors tolérance à vide suffit à conclure."),
        ),
        correction=(
            f"+12 V : {volts(E06_MEASURED['+12 V'])}, sous le minimum ({_range('+12 V')}) : hors tolérance. Les autres sont dans leur plage (+5 V de {_range('+5 V')}, +3,3 V de {_range('+3,3 V')}, +5 VSB de {_range('+5 VSB')}, −12 V de {_range('−12 V')}).",
            "Le +12 V alimente le processeur et la carte graphique : sous charge, il baisse encore et le PC s'arrête. On remplace le bloc, on ne l'ouvre jamais (condensateurs chargés). Le testeur travaille presque à vide : un bloc « bon » au testeur peut encore lâcher en charge, mais ici la mesure suffit.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Mesurer une pile CMOS avec le multimètre",
        question_type="short_answer",
        requirement_ids=R_HW,
        kind=KIND_TOOL,
        context=(
            "Dans le PC de la réception d'un hôtel qui perd la date à chaque coupure, tu retires la pile bouton CR2032 "
            f"(tension nominale {_fr(CMOS_NOMINAL)} V). Le multimètre de l'atelier est réglé sur la continuité par le "
            f"technicien précédent. Une fois correctement réglé, il affiche {_fr(E07_MEASURED)} V."
        ),
        instructions=(
            "Indique comment régler et brancher le multimètre avant de mesurer.",
            "Interprète la mesure et indique la suite.",
        ),
        criteria=(
            _c("Réglage", 1, "Mode tension continue (DC), calibre adapté (ex. 20 V) ou automatique, cordon noir sur COM et rouge sur V ; mesure de la pile retirée, PC débranché."),
            _c("Interprétation", 1, f"{_fr(E07_MEASURED)} V, nettement sous les {_fr(CMOS_NOMINAL)} V nominaux : pile usée ; la remplacer par une CR2032, puis régler date et heure et vérifier après une coupure."),
        ),
        correction=(
            f"On ne garde jamais le réglage du collègue : on choisit le mode tension continue et un calibre adapté avant de toucher la pile, cordon noir sur COM, rouge sur V. Une pile neuve donne un peu plus de {_fr(CMOS_NOMINAL)} V ; à {_fr(E07_MEASURED)} V, elle est usée : elle ne garde plus l'horloge quand le PC est débranché. On la remplace (même modèle), on règle date et heure, on contrôle après une coupure, et l'ancienne pile part dans la filière des piles.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Dépoussiérage : à faire ou interdit ?",
        question_type="classification",
        requirement_ids=R_HW,
        kind=KIND_RISK,
        context=(
            "Avant la campagne de nettoyage annuelle des 40 PC d'une école, tu prépares une affiche pour les "
            "stagiaires. Dix gestes ont été proposés par l'équipe ; certains sont de bonnes pratiques, d'autres "
            "abîment le matériel ou mettent en danger. Tu les tries."
        ),
        instructions=("Range chaque geste : à faire ou interdit.",),
        criteria=(
            _c("Tri", 5, "À faire : " + " ; ".join(CLEAN_DO) + ". Interdit : " + " ; ".join(CLEAN_DONT) + " (0,5 pt par geste)."),
        ),
        correction=(
            "À faire : bloquer les pales (un ventilateur entraîné par le jet tourne trop vite et s'abîme), bombe droite par petites pressions (sinon le gaz liquide gèle les composants), alcool isopropylique pour l'ancienne pâte, filtres nettoyés, pièce aérée.",
            "Interdit : l'aspirateur domestique (électricité statique, aspiration de petites pièces), le liquide sur un PC sous tension, l'ouverture du bloc (condensateurs chargés), la pâte en excès qui déborde sur la carte.",
        ),
        classification=Classification(categories=("À faire", "Interdit"), elements=E08_DISPLAYED, correct=E08_CORRECT),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Raccorder une prise murale avec l'outil d'insertion",
        question_type="ordering",
        requirement_ids=R_NET,
        kind=KIND_ORDER,
        context=(
            "Dans une PME, tu poses une prise RJ45 murale au bureau 4 ; le câble arrive déjà du panneau de brassage "
            "de la baie, dont un port du switch fournit le PoE aux téléphones. Le stagiaire a noté les six étapes "
            "sur une fiche, mais dans le désordre."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Repérer → dénuder → placer les paires → insérer → refermer → tester (0,5 pt par position)."),
        ),
        correction=(
            "On repère d'abord le bon câble (même étiquette aux deux bouts). Le dénudeur, réglé sur une chute, retire la gaine sans entailler. Chaque paire est placée selon le code couleur de la prise (T568A ou T568B, le même partout), torsades gardées jusqu'au contact.",
            "L'outil d'insertion enfonce chaque fil, côté coupant vers la chute ; on referme et on fixe. Le testeur de câble se branche sur le lien prise ↔ panneau, jamais sur un port actif : le PoE ou une ligne téléphonique peut l'endommager.",
        ),
        ordering=_shuffled_ordering(E09_STEPS, (4, 1, 3, 0, 5, 2)),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Sécurité laser et éclats de fibre",
        question_type="long_answer",
        requirement_ids=R_FIBRE,
        kind=KIND_RISK,
        context=(
            "Dans la baie d'une école, un collègue remplace une jarretière optique. Pour savoir si « la lumière passe », "
            "il regarde l'extrémité du connecteur encore branché au switch : « je ne vois rien, donc pas de laser ». "
            "Il coupe ensuite une fibre sur la table où l'équipe mange à midi."
        ),
        instructions=("Relève les erreurs, explique le danger et indique la bonne pratique pour chacune.",),
        criteria=(
            _c("Laser", 2, "Ne jamais regarder une fibre ni un module : la lumière est souvent infrarouge, invisible ; « je ne vois rien » ne prouve rien ; éteindre ou débrancher, capuchons, utiliser un appareil de mesure ou le localisateur visuel sans regarder dans la fibre."),
            _c("Éclats", 2, "Éclats qui se plantent dans la peau ou l'œil, ou avalés : lunettes, poste dédié, récipient fermé pour les chutes, pas de repas sur le poste, nettoyage du plan ; éclat dans l'œil : ne pas frotter, rincer, médecin."),
        ),
        correction=(
            "Regarder un connecteur branché est dangereux : les modules optiques émettent souvent en infrarouge, invisible, qui peut brûler la rétine sans douleur. « Je ne vois rien » ne prouve donc pas l'absence de laser. On débranche ou on éteint la source, on remet les capuchons, et on contrôle le lien avec les voyants du switch ou un appareil de mesure, jamais avec l'œil.",
            "Les éclats de fibre de verre sont presque invisibles et se plantent dans la peau ou l'œil ; sur une table de repas, ils peuvent être avalés. On coupe sur un poste dédié, avec des lunettes, on jette les chutes dans un récipient fermé et on nettoie le plan. Un éclat dans l'œil : ne pas frotter, rincer, consulter un médecin.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Ces plans de sauvegarde respectent-ils la règle 3-2-1 ?",
        question_type="classification",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Tu fais le tour de six petits clients pour vérifier leurs sauvegardes. La règle 3-2-1 du cours "
            "(complément) demande 3 copies, l'original compris, sur 2 types de supports (un NAS, un disque externe et "
            "le disque du PC sont tous des disques) et 1 copie hors site."
        ),
        instructions=("Range chaque plan : conforme, ou le point de la règle qui manque.",),
        criteria=(
            _c("Verdicts", 3, " ; ".join(f"{t} → {E11_CATEGORIES[c]}" for (t, _p), c in zip(E11_PLANS, E11_CORRECT, strict=True)) + " (0,5 pt par plan)."),
        ),
        correction=(
            "Conformes : PC + disque externe + copie en ligne (3 copies, disque et en ligne, une hors site) ; PC + clé USB emportée + disque externe (3 copies, disque et mémoire flash, la clé est hors site). Deux copies seulement (PC + en ligne) : il manque une copie.",
            "PC + deux disques externes, ou PC + NAS + disque au coffre : tout est sur des disques, un seul type de support. PC + NAS + clé dans le tiroir : tout est au bureau, aucune copie hors site (un incendie ou un vol emporte tout).",
        ),
        classification=Classification(categories=E11_CATEGORIES, elements=tuple(t for t, _p in E11_PLANS), correct=E11_CORRECT),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Contrôler l'intégrité d'une copie par empreinte",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Avant de remplacer le disque d'un cabinet vétérinaire, tu as copié ses données sur un disque externe "
            "de l'atelier. Pour vérifier la copie, tu as calculé l'empreinte SHA-256 de chaque fichier (Get-FileHash "
            "sous Windows) ; les documents 1 et 2 donnent la source et la copie (16 premiers caractères)."
        ),
        documents=(
            _table("Document 1 — Source (disque du cabinet), support fictif", ("Fichier", "Taille (octets)", "Empreinte SHA-256"),
                   *_listing_rows(E12_SOURCE)),
            _table("Document 2 — Copie (disque externe), support fictif", ("Fichier", "Taille (octets)", "Empreinte SHA-256"),
                   *_listing_rows(E12_COPY)),
        ),
        instructions=(
            "Relève les fichiers absents de la copie et ceux dont la copie diffère.",
            "Conclus : peux-tu remplacer le disque ? Que fais-tu ?",
        ),
        criteria=(
            _c("Écarts", 2, f"Absent : {', '.join(E12_MISSING)} ; différent (même taille, empreinte différente) : {', '.join(E12_DIFFERENT)}."),
            _c("Conclusion", 2, "Copie non valide : ne pas toucher au disque ; refaire la copie des fichiers en cause, recalculer les empreintes jusqu'à ce que tout soit identique ; noter le contrôle sur la fiche."),
        ),
        correction=(
            f"{E12_MISSING[0]} n'apparaît pas dans la copie. {E12_DIFFERENT[0]} a la même taille mais une autre empreinte : son contenu diffère (copie corrompue ou interrompue). Les autres fichiers ont même taille et même empreinte : ils sont identiques.",
            "La copie n'est pas valide : on ne remplace pas le disque. On recopie les deux fichiers, on recalcule leurs empreintes (Get-FileHash sous Windows, sha256sum sous Linux) et on ne passe au remplacement que lorsque toutes sont identiques. Une taille identique ne suffit pas : seule l'empreinte prouve que le contenu est le même.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Un disque chiffré avant une mise à jour du firmware",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Dans un bureau d'avocats, les portables sont chiffrés avec BitLocker. Tu dois mettre à jour le firmware "
            "(UEFI) de l'un d'eux, puis remplacer la carte mère d'un autre. L'utilisatrice te dit : « la clé de "
            "récupération ? Je ne sais pas, on ne me l'a jamais donnée »."
        ),
        instructions=(
            "Explique pourquoi la clé de récupération est indispensable ici et où la chercher.",
            "Donne les précautions avant la mise à jour et ce qu'on ne fait jamais avec cette clé.",
        ),
        criteria=(
            _c("Clé indispensable", 2, "Après une mise à jour du firmware ou un changement de carte mère (TPM), BitLocker peut demander la clé de récupération (48 chiffres) ; sans elle, les données sont perdues. La chercher auprès de l'administrateur (annuaire de l'entreprise) ou dans le compte de l'organisation, avant d'intervenir."),
            _c("Précautions", 2, "Sauvegarde vérifiée ; suspendre BitLocker avant la mise à jour du firmware puis le réactiver ; accord ; ne jamais écrire la clé sur le PC ni la garder après l'intervention, ne jamais l'envoyer en clair ; ne pas désactiver le chiffrement « pour simplifier »."),
        ),
        correction=(
            "Le chiffrement rend le disque illisible sans sa clé. Après une mise à jour du firmware ou un changement de carte mère (et donc de puce TPM), BitLocker peut ne plus déverrouiller le disque seul et demande la clé de récupération de 48 chiffres. Sans elle, les données sont perdues. On la récupère avant d'intervenir, auprès de l'administrateur ou dans le compte de l'organisation où elle a été enregistrée.",
            "Avant la mise à jour : sauvegarde vérifiée, accord, BitLocker suspendu (puis réactivé après). La clé donne accès à toutes les données : elle ne s'écrit pas sur un papier collé au PC, ne s'envoie pas en clair et ne se conserve pas après l'intervention. On ne désactive pas le chiffrement pour se simplifier la tâche.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Peut-on lancer la réinitialisation d'usine ?",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Dans une agence immobilière, le PC du hall doit subir une réinitialisation d'usine. Un stagiaire de "
            "l'agence t'a dit oralement « vous pouvez y aller, le patron est d'accord ». Les photos des biens doivent "
            "être gardées. Le document 1 est la fiche de préparation remplie ce matin."
        ),
        documents=(_table("Document 1 — Fiche de préparation (support fictif)", ("Prérequis", "État"),
                          *((p, "fait" if p in E14_DONE else "non") for p in PREREQUISITES if p != PRE_KEY),
                          (PRE_KEY, "sans objet : disque non chiffré")),),
        instructions=(
            "Indique les prérequis qui manquent encore.",
            "Dis si tu peux commencer et ce que tu fais.",
        ),
        criteria=(
            _c("Manques", 2, " ; ".join(E14_MISSING) + "."),
            _c("Décision", 2, "Non : un accord oral d'un stagiaire ne suffit pas ; obtenir l'accord écrit, daté, du gérant (personne habilitée) pour cette opération ; attendre avant toute réinitialisation."),
        ),
        correction=(
            "La sauvegarde est vérifiée et les licences notées, mais il manque l'accord écrit et la signature d'une personne habilitée. Un accord oral, rapporté par un stagiaire, ne prouve rien et ne vient pas de la personne qui a le droit de décider.",
            "On ne commence pas. On demande au gérant un accord écrit et daté qui nomme l'opération (réinitialisation d'usine du PC du hall) et le sort des données ; on réinitialise ensuite, puis on restaure les photos et on fait contrôler.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="À chaque déchet sa filière",
        question_type="classification",
        requirement_ids=R_BOTH,
        kind=KIND_WASTE,
        context=(
            "En fin d'année, l'atelier vide son local de stockage. Sept objets attendent sur le chariot ; ton "
            "responsable te demande de les répartir dans les bonnes filières de fin de vie, sans rien jeter à la "
            "poubelle ordinaire."
        ),
        instructions=("Range chaque objet dans sa filière.",),
        criteria=(
            _c("Filières", 3.5, " ; ".join(f"{i} → {waste_route(k)}" for i, k in WASTE_ITEMS) + " (0,5 pt par objet)."),
        ),
        correction=(
            "Écran, clavier et souris sont des déchets d'équipements électriques et électroniques (DEEE) : collecte DEEE (en Belgique, point Recupel, parc à conteneurs ou collecteur agréé). Piles et batteries, pôles isolés : collecte des piles et batteries (en Belgique, Bebat).",
            "Le disque d'un PC de comptabilité et la clé USB d'un ancien employé contiennent des données : effacement certifié ou destruction par une filière agréée, avant tout recyclage. Le toner vide : reprise par le fabricant ou le fournisseur.",
        ),
        classification=Classification(categories=ROUTES, elements=E15_ELEMENTS, correct=E15_CORRECT),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Compléter le schéma du poste antistatique",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_SCHEMA,
        context=(
            "Pour l'accueil des stagiaires, ton responsable affiche le schéma du poste de travail antistatique de "
            "l'atelier. La légende a été effacée de la version imprimée : seuls les numéros 1 à 5 restent. Le "
            "document 1 est ce schéma."
        ),
        documents=(_schema("pr28-poste-esd-a-completer", "Document 1 — Poste antistatique à compléter (schéma fictif)"),),
        instructions=(
            "Nomme les éléments 1 à 5.",
            "Donne le rôle de chacun en une phrase.",
        ),
        criteria=(
            _c("Noms", 2.5, " ; ".join(f"{n}. {label}" for n, label in ESD_PARTS) + " (0,5 pt chacun)."),
            _c("Rôles", 1.5, "Tapis et cordon : écouler les charges vers la masse ; bracelet : garder le technicien au même potentiel ; câble débranché : sécurité électrique ; sachet : protéger la pièce retirée."),
        ),
        correction=(
            "1. Tapis antistatique : surface de travail qui écoule doucement les charges. 2. Son cordon, relié au point de masse de l'atelier. 3. Bracelet au poignet, relié au tapis : le technicien reste au même potentiel que la pièce (sans tapis, la procédure le relie à une partie métallique nue du châssis).",
            "4. Câble secteur débranché : on ne travaille jamais dans un PC branché, c'est la sécurité de la personne. 5. Sachet antistatique : la pièce retirée y est rangée, tenue par les bords.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Compléter l'arbre de gestion d'un incident",
        question_type="document_analysis",
        requirement_ids=R_BOTH,
        kind=KIND_SCHEMA,
        context=(
            "Le classeur sécurité de l'atelier contient l'arbre « incident pendant une intervention ». Sur la copie "
            "remise aux stagiaires, les quatre conduites à tenir ont été effacées. Le document 1 est l'arbre à "
            "terminer."
        ),
        documents=(_schema("pr28-arbre-incident-a-completer", "Document 1 — Arbre d'incident à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④ (conduite à tenir quand la réponse est « non »).",
            "Explique pourquoi la question sur la zone vient avant celle sur les blessés.",
        ),
        criteria=(
            _c("Conduites", 3, " ; ".join(f"{m} {a}" for m, a in INCIDENT_BLANK_ANSWERS.items()) + " (0,75 pt chacune)."),
            _c("Ordre", 1, "On ne secourt pas dans une zone dangereuse : sinon on devient une victime de plus (contact électrique, fumée)."),
        ),
        correction=(
            "① Zone non sûre : couper le courant sans risque, s'éloigner, 112 ; ne jamais toucher une victime encore en contact. ② Blessé : premiers secours dans la limite de sa formation, 112 si c'est grave, prévenir le responsable.",
            "③ Données touchées : arrêter toute écriture, ne rien réinstaller, prévenir aussitôt le responsable. ④ Matériel abîmé : l'isoler, l'étiqueter, le photographier, ne pas le remettre en service. La zone vient d'abord : un sauveteur électrisé ne sauve personne.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Le mot de passe sur un papier et les photos du client",
        question_type="short_answer",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Un indépendant te confie son portable pour remplacer le disque. Il te tend un papier avec son mot de "
            "passe de session et ajoute : « et jetez un œil à mes photos de vacances pour voir si elles sont bien "
            "là ». Tu travailles seul à l'atelier ; le client revient demain."
        ),
        instructions=("Indique ce que tu fais du mot de passe et comment tu vérifies les données sans les consulter.",),
        criteria=(
            _c("Mot de passe", 1, "Ne pas le prendre ni le noter : le client ouvre lui-même sa session, ou l'intervention se fait avec un compte technique ; s'il a été divulgué, conseiller de le changer."),
            _c("Données", 1, "Contrôle sans ouvrir les fichiers : nombre de fichiers, tailles, empreintes, devant le client qui ouvre lui-même quelques photos à la restitution."),
        ),
        correction=(
            "Le mot de passe est personnel : on ne le prend pas, on ne le note pas. Le client ouvre lui-même la session ou crée un compte temporaire pour l'intervention, supprimé ensuite ; s'il l'a déjà écrit, on lui conseille de le changer. Les photos sont des données personnelles : on ne les regarde pas. On vérifie la copie par le nombre de fichiers, les tailles et les empreintes, et c'est le client qui ouvre quelques photos à la restitution.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Rédiger la fiche sécurité d'un remplacement d'alimentation",
        question_type="long_answer",
        requirement_ids=R_HW,
        kind=KIND_WRITE,
        context=(
            "Ton responsable veut une fiche sécurité pour chaque intervention courante. Tu rédiges celle du "
            "remplacement d'un bloc d'alimentation défaillant dans un PC tour, à l'atelier, avec le modèle du cours : "
            + ", ".join(SAFETY_SHEET_FIELDS).lower() + "."
        ),
        instructions=("Rédige la fiche en reprenant chaque rubrique du modèle.",),
        criteria=(
            _c("Risques et protections", 1.5, "Électricité et condensateurs, ESD, coupures (tôles) ; bracelet et tapis, tournevis adaptés, testeur d'alimentation, gants si tôles coupantes."),
            _c("Avant / pendant", 1.5, "Arrêt, bloc sur 0, débranché, charges vidées, bracelet ; photo des branchements ; bloc neuf de puissance et connectique adaptées ; jamais ouvrir l'ancien bloc ; câbles rangés."),
            _c("Après et incident", 1, "Contrôle des connecteurs, démarrage et test de charge, ancien bloc en filière DEEE ; incident : couper, débrancher, 112 si blessé, prévenir, noter."),
        ),
        correction=(
            "Intervention : remplacement du bloc d'alimentation d'un PC tour. Risques : électricité (secteur, condensateurs), ESD pour la carte mère, coupures sur les tôles. Protections et outils : tournevis adaptés, bracelet et tapis antistatiques, testeur d'alimentation pour le bloc neuf, gants de manutention si nécessaire.",
            "Avant : sauvegarde existante, arrêt du système, interrupteur sur 0, câble débranché, appui sur le bouton, bracelet ; photo des branchements. Pendant : débrancher les connecteurs sans tirer sur les fils, ne jamais ouvrir l'ancien bloc, monter un bloc de puissance et de connectique adaptées, ranger les câbles hors des ventilateurs.",
            "Après : contrôle des connecteurs, démarrage, test sous charge, ancien bloc étiqueté et envoyé dans la filière DEEE. En cas d'incident : couper et débrancher, 112 en cas de blessure, prévenir le responsable, noter sur la fiche.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la réaction à un incident",
        question_type="ordering",
        requirement_ids=R_BOTH,
        kind=KIND_ORDER,
        context=(
            "Pendant un remplacement d'écran chez un client, la multiprise sous le bureau se met à fumer ; une "
            "employée a une légère brûlure à la main et des documents du client étaient en cours de copie. Le "
            "stagiaire a noté six réactions dans le désordre ; tu les remets dans l'ordre du cours."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Sécuriser → alerter → secourir → protéger les données → noter → analyser (0,5 pt par position)."),
        ),
        correction=(
            "Les personnes d'abord : on sécurise (couper le courant si c'est sans risque, s'éloigner), on alerte (112 si c'est grave, le responsable) et on secourt dans la limite de sa formation (brûlure refroidie à l'eau).",
            "Ensuite les données : la copie interrompue n'est pas relancée au hasard, on note où elle en était et on prévient. Puis on note l'incident sur la fiche (heure, faits, mesures, photos) et on analyse la cause avec le responsable (multiprise surchargée ?).",
        ),
        ordering=_shuffled_ordering(E20_STEPS, (4, 1, 5, 0, 3, 2)),
    ),
    PR06Item(
        key="E21",
        usage=USAGE_PRACTICE,
        title="La clé USB de sauvegarde perdue",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Un stagiaire a copié les données d'un cabinet de kinésithérapie sur une clé USB non chiffrée avant de "
            "réinstaller un PC. En rentrant à l'atelier, il s'aperçoit qu'il a perdu la clé, sans doute dans le "
            "train. Les données contiennent des dossiers de patients. Il te demande s'il doit « en parler »."
        ),
        instructions=(
            "Indique ce qu'il faut faire tout de suite et qui décide de la suite.",
            "Propose deux mesures pour que cela ne se reproduise pas.",
        ),
        criteria=(
            _c("Réaction", 2, "Oui, prévenir aussitôt le responsable, sans cacher ; noter les faits (heure, lieu, contenu, chiffrement absent) ; recherche ; ne pas réinstaller tant que la copie n'est pas refaite ; le responsable prévient le client, responsable de ses données, qui décide de la notification à l'autorité (72 h au plus si la fuite présente un risque)."),
            _c("Mesures", 2, "Copies toujours chiffrées ; support de l'atelier inventorié plutôt qu'une clé personnelle ; copie effacée après restitution ; formation des stagiaires."),
        ),
        correction=(
            "Il faut en parler tout de suite : une fuite possible de données de santé ne se cache pas. Le stagiaire prévient le responsable et note les faits (heure, lieu, contenu, clé non chiffrée). La réinstallation attend : la copie doit être refaite à partir du PC. Le responsable prévient sans attendre le client, responsable de ses données ; c'est lui qui décide de notifier la violation à l'Autorité de protection des données, au plus tard 72 heures après en avoir pris connaissance quand elle présente un risque pour les personnes.",
            "Pour l'avenir : copies toujours chiffrées (un support perdu reste illisible), supports de l'atelier numérotés et inventoriés au lieu de clés personnelles, copies effacées après restitution, rappel de la procédure aux stagiaires.",
        ),
    ),
    PR06Item(
        key="E22",
        usage=USAGE_PRACTICE,
        title="Suivre l'arbre d'incident après une chute de radiateur",
        question_type="short_answer",
        requirement_ids=R_HW,
        kind=KIND_TREE,
        context=(
            "En remontant un PC débranché, tu fais tomber le radiateur du processeur sur la carte graphique : un "
            "petit composant est arraché. Personne n'est blessé, rien ne fume, le disque n'a pas été touché et les "
            "données du client sont sauvegardées."
        ),
        instructions=("Indique la question de l'arbre d'incident où tu t'arrêtes, la conduite à tenir et la suite.",),
        criteria=(
            _c("Question et conduite", 1, f"Question {E22_RESULT[0]} (matériel intact ? non) : {E22_RESULT[1]}"),
            _c("Suite", 1, "Prévenir le responsable et le client sans cacher, noter sur la fiche (heure, faits, photo), proposer le remplacement de la carte, analyser (pièce mal tenue)."),
        ),
        correction=(
            f"Zone sûre (oui), tout le monde indemne (oui), données intactes (oui), matériel intact (non) : arrêt à la question {E22_RESULT[0]}. Conduite : {E22_RESULT[1]} Puis on prévient le responsable et le client, on note l'incident sur la fiche et on propose le remplacement de la carte : un incident caché devient une faute.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Le kit pour contrôler un bloc d'alimentation",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_TOOL,
        context=(
            "Un PC de la médiathèque redémarre seul plusieurs fois par jour ; ton responsable soupçonne le bloc "
            "d'alimentation et te demande de le contrôler à l'atelier. Le document 1 liste les outils PC de la "
            "caisse ; tu choisis seulement ceux qui servent."
        ),
        documents=(_table("Document 1 — Outils PC de la caisse (support fictif)", ("Repère", "Outil"),
                          *((letter, name) for letter, name in zip(_letters(len(X01_LIST)), X01_LIST, strict=True))),),
        instructions=("Choisis les outils et donne la précaution principale du testeur d'alimentation.",),
        criteria=(
            _c("Kit", 1, _tool_names(X01_KIT) + "."),
            _c("Précaution du testeur", 1, "Connecteurs branchés avant la mise sous tension ; il ne prouve pas la tenue en charge ; le bloc n'est jamais ouvert."),
        ),
        correction=(
            "Kit : " + _tool_names(X01_KIT) + ". Les tournevis pour sortir le bloc, la protection antistatique pour la carte mère pendant le démontage, le testeur pour les tensions. Testeur : on branche ses connecteurs avant de mettre le bloc sous tension ; un résultat correct à vide ne prouve pas que le bloc tient en charge ; on n'ouvre jamais le bloc.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Mesures d'un bloc qui fait redémarrer le PC",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_TOOL,
        context=(
            "Le bloc d'alimentation d'un PC de médiathèque, démonté, est branché sur le testeur d'alimentation de "
            "l'atelier. Le document 1 donne les valeurs affichées. Les tolérances sont celles du cours PR02 : ±5 % "
            "pour +12 V, +5 V, +3,3 V et +5 VSB, ±10 % pour −12 V."
        ),
        documents=(_table("Document 1 — Écran du testeur (support fictif)", ("Tension", "Valeur affichée"),
                          *_rail_rows(X02_MEASURED)),),
        instructions=("Indique la tension hors tolérance avec sa plage et ta décision.",),
        criteria=(
            _c("Hors tolérance", 1, f"{', '.join(X02_OUT)} : {volts(X02_MEASURED[X02_OUT[0]])}, plage {_range(X02_OUT[0])}."),
            _c("Décision", 1, "Remplacer le bloc (puissance et connectique adaptées), ne jamais l'ouvrir ; ancien bloc en filière DEEE."),
        ),
        correction=(
            f"+5 V : {volts(X02_MEASURED['+5 V'])}, sous le minimum de la plage {_range('+5 V')} : hors tolérance ; les autres tensions sont dans leur plage. Décision : remplacer le bloc par un modèle de puissance et de connectique adaptées ; on ne l'ouvre jamais (condensateurs chargés) ; l'ancien bloc part dans la filière DEEE.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Un smartphone de service qui gonfle",
        question_type="long_answer",
        requirement_ids=R_SAFE,
        kind=KIND_RISK,
        context=(
            "Un livreur rapporte au service informatique son smartphone de service : il chauffe, la coque arrière se "
            "soulève et il le recharge « pour qu'il tienne la tournée ». L'appareil est hors garantie ; l'atelier "
            "n'est pas équipé pour remplacer ce type de batterie."
        ),
        instructions=("Indique les gestes immédiats, ce que tu ne fais pas et la suite pour l'appareil.",),
        criteria=(
            _c("Gestes immédiats", 1, "Débrancher, ne plus charger ni allumer, ne pas presser ni percer, isoler dans un bac ininflammable loin des matières combustibles ; s'il fume : s'éloigner, alerter."),
            _c("Suite", 1, "Prévenir le responsable, noter (photo, date) ; réparateur habilité ou remplacement de l'appareil ; batterie dans la filière des piles et batteries, pôles isolés ; appareil de remplacement pour le livreur."),
        ),
        correction=(
            "Une batterie lithium-ion qui chauffe et gonfle peut s'enflammer : on débranche, on ne recharge plus, on ne presse pas la coque pour la refermer et on ne perce rien. L'appareil va dans un bac ininflammable, loin du papier. S'il fume : on s'éloigne et on alerte.",
            "L'atelier ne remplace pas ce type de batterie : réparateur habilité ou remplacement de l'appareil, avec l'accord du responsable. La batterie usagée part dans la filière des piles et batteries, pôles isolés. Le livreur reçoit un appareil de remplacement.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Deux erreurs dans une procédure de dépoussiérage",
        question_type="document_analysis",
        requirement_ids=R_HW,
        kind=KIND_RISK,
        context=(
            "Un collègue a rédigé la procédure de dépoussiérage des PC d'une école ; ton responsable te demande de la "
            "relire avant de l'afficher. Le document 1 donne les six étapes numérotées."
        ),
        documents=(_text_doc("Document 1 — Procédure du collègue (support fictif)",
                             " ".join(f"{i}. {step}." for i, step in enumerate(X04_STEPS, start=1))),),
        instructions=("Relève les deux étapes fautives, explique le danger et corrige-les.",),
        criteria=(
            _c("Étape " + str(X04_ERRORS[0]), 1, "Aspirateur domestique interdit (électricité statique, petites pièces aspirées) : air sec par petites pressions et pinceau antistatique."),
            _c("Étape " + str(X04_ERRORS[1]), 1, "Ventilateur libre sous le jet : il tourne trop vite et s'abîme ; bloquer ses pales pendant le soufflage."),
        ),
        correction=(
            f"Étape {X04_ERRORS[0]} : l'aspirateur domestique crée de l'électricité statique et peut aspirer de petites pièces ; on souffle à l'air sec, par petites pressions, avec un pinceau antistatique. Étape {X04_ERRORS[1]} : un ventilateur entraîné par le jet d'air tourne bien au-delà de sa vitesse et s'abîme ; on bloque ses pales pendant le soufflage. Les autres étapes sont correctes (débranchement, bracelet, bombe droite, test final).",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Le plan de sauvegarde d'un bureau d'études",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Le gérant d'un bureau d'études affirme que ses sauvegardes « sont parfaites ». Le document 1 décrit ses "
            "copies. Tu les compares à la règle 3-2-1 du cours (complément) : 3 copies l'original compris, 2 types de "
            "supports (NAS, disque externe et disque interne sont tous des disques), 1 copie hors site."
        ),
        documents=(_table("Document 1 — Copies existantes (support fictif)", ("Copie", "Support", "Lieu"),
                          *((c.label, c.support, "hors site" if c.offsite else "dans le bâtiment") for c in X05_COPIES)),),
        instructions=("Indique les points de la règle 3-2-1 qui manquent et propose une correction.",),
        criteria=(
            _c("Manques", 1, " et ".join(X05_MISSING) + " (trois copies, mais toutes sur des disques et dans le bâtiment)."),
            _c("Correction", 1, "Ajouter une copie d'un autre type et hors site : copie en ligne chiffrée, ou rotation de supports emportés hors site ; tester régulièrement une restauration."),
        ),
        correction=(
            f"Trois copies existent, mais elles sont toutes sur des disques (serveur, NAS, disque externe) et toutes dans le bâtiment : {' et '.join(X05_MISSING)}. Un incendie, une inondation ou un rançongiciel peut tout emporter. Correction : une copie en ligne chiffrée (autre type de support, hors site), et un test de restauration régulier.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Une copie à vérifier avant de formater",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Avant de formater le disque d'un architecte, tu as copié ses dossiers et calculé les empreintes SHA-256 "
            "(16 premiers caractères) de la source et de la copie. Les documents 1 et 2 donnent les deux listes."
        ),
        documents=(
            _table("Document 1 — Source (support fictif)", ("Fichier", "Taille (octets)", "Empreinte SHA-256"),
                   *_listing_rows(X06_SOURCE)),
            _table("Document 2 — Copie (support fictif)", ("Fichier", "Taille (octets)", "Empreinte SHA-256"),
                   *_listing_rows(X06_COPY)),
        ),
        instructions=("Relève les écarts et dis si tu peux formater.",),
        criteria=(
            _c("Écarts", 1, f"Absent : {', '.join(X06_MISSING)} ; empreinte différente : {', '.join(X06_DIFFERENT)}."),
            _c("Décision", 1, "Non : copie non valide ; recopier les fichiers en cause et recalculer les empreintes jusqu'à identité complète."),
        ),
        correction=(
            f"{X06_MISSING[0]} manque dans la copie ; {X06_DIFFERENT[0]} a la même taille mais une autre empreinte : son contenu diffère (ancienne version). On ne formate pas : on recopie ces fichiers, on recalcule les empreintes et on attend qu'elles soient toutes identiques. Seule l'empreinte prouve que le contenu est le même.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Réinstaller un portable chiffré",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_DATA,
        context=(
            "Le portable chiffré (BitLocker) d'une responsable des ressources humaines doit être réinstallé ; ses "
            "dossiers doivent être restaurés ensuite. Le document 1 est la fiche de préparation ; elle doit "
            "retrouver ses logiciels et sa messagerie après l'intervention."
        ),
        documents=(_table("Document 1 — Fiche de préparation (support fictif)", ("Prérequis", "État"),
                          *((p, "fait" if p in X07_DONE else "non") for p in PREREQUISITES)),),
        instructions=("Indique ce qui manque avant de réinstaller et pourquoi chaque point compte.",),
        criteria=(
            _c("Manques", 1, " ; ".join(X07_MISSING) + "."),
            _c("Raisons", 1, "Sans clé de récupération, un disque chiffré peut devenir illisible ; sans licences et réglages notés, la remise en service est impossible ou incomplète."),
        ),
        correction=(
            "La sauvegarde est vérifiée et l'accord signé par une personne habilitée, mais il manque " + " et ".join(X07_MISSING) + ". La clé de récupération est indispensable si le système la demande pendant l'intervention ; sans elle, les données chiffrées sont perdues. Les licences, comptes et réglages notés permettent de remettre les logiciels et la messagerie en service. On attend d'avoir les deux.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Nettoyer un connecteur optique en sécurité",
        question_type="long_answer",
        requirement_ids=R_FIBRE,
        kind=KIND_RISK,
        context=(
            "Le lien optique entre deux bâtiments d'une entreprise est instable. Tu dois débrancher la jarretière, "
            "inspecter et nettoyer ses connecteurs, puis la rebrancher. Un stagiaire t'accompagne et n'a jamais "
            "travaillé sur de la fibre."
        ),
        instructions=("Rédige les consignes de sécurité et la procédure de nettoyage pour le stagiaire.",),
        criteria=(
            _c("Sécurité", 1, "Ne jamais regarder un connecteur ni une fibre (laser souvent invisible) ; source éteinte ou débranchée ; stylo laser jamais vers les yeux ; capuchons ; éclats éventuels dans un récipient fermé."),
            _c("Nettoyage", 1, "Intervention annoncée ; débrancher, nettoyer chaque férule avec le kit (stylo ou cassette), jamais de chiffon ni de souffle ; capuchons remis aussitôt ; rebrancher et contrôler le lien (voyants, service)."),
        ),
        correction=(
            "Sécurité : on ne regarde jamais l'extrémité d'une fibre ni d'un module, même éteint en apparence : la lumière est souvent infrarouge, invisible. On débranche ou on éteint la source, on garde les capuchons, le stylo laser rouge n'est jamais pointé vers un œil.",
            "Procédure : intervention annoncée (le lien sera coupé), jarretière débranchée, chaque férule nettoyée avec le stylo ou la cassette de nettoyage (jamais un chiffon ni le souffle), capuchons remis aussitôt, rebranchement et contrôle des voyants et du service.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Évacuer le matériel usagé d'une direction",
        question_type="short_answer",
        requirement_ids=R_BOTH,
        kind=KIND_WASTE,
        context=(
            "La direction d'une PME remplace son matériel. Il reste une imprimante jet d'encre hors d'usage (sans "
            "cartouches), la batterie usagée de l'onduleur, le SSD de l'ancien PC de la directrice et des cartouches "
            "d'encre vides. Rien ne doit partir à la poubelle ordinaire."
        ),
        instructions=("Indique la filière de chaque objet et la précaution pour le SSD.",),
        criteria=(
            _c("Filières", 1, " ; ".join(f"{i} → {r}" for i, r in X09_ROUTES) + "."),
            _c("SSD", 1, "Accord écrit ; commande d'effacement du SSD (ou destruction) avec certificat avant tout recyclage ; un formatage rapide n'efface rien."),
        ),
        correction=(
            "Imprimante : collecte DEEE. Batterie de l'onduleur : collecte des piles et batteries, pôles isolés. Cartouches : reprise par le fabricant ou le fournisseur. SSD : il contient des données de direction ; avec l'accord écrit, effacement par la commande du SSD ou destruction par une filière agréée, certificat à l'appui, puis collecte DEEE. Un formatage rapide ne suffit pas.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="De la fumée pendant un test de bloc",
        question_type="short_answer",
        requirement_ids=R_SAFE,
        kind=KIND_TREE,
        context=(
            "À l'atelier, un collègue contrôle un bloc d'alimentation sur le testeur ; une odeur de brûlé apparaît, "
            "puis de la fumée sort des grilles du bloc. Personne n'a été touché ; le bloc est toujours branché sur "
            "la multiprise du plan de travail."
        ),
        instructions=("Indique où l'arbre d'incident s'arrête, la conduite à tenir et la suite.",),
        criteria=(
            _c("Arrêt et conduite", 1, f"Question {X10_RESULT[0]} (zone sûre ? non) : {X10_RESULT[1]}"),
            _c("Suite", 1, "Couper à l'interrupteur de la multiprise ou au tableau si c'est sans risque, ne pas ouvrir le bloc, l'isoler et l'étiqueter, prévenir le responsable, noter l'incident ; feu : consignes incendie, 112."),
        ),
        correction=(
            f"De la fumée : la zone n'est pas sûre, l'arbre s'arrête à la question {X10_RESULT[0]}. Conduite : {X10_RESULT[1]} Si c'est sans risque, on coupe l'interrupteur de la multiprise ou le tableau ; on n'ouvre pas le bloc. Ensuite : bloc isolé et étiqueté « ne pas utiliser », responsable prévenu, incident noté ; en cas de flamme, consignes incendie du site et 112.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS

EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, classements et remises en ordre cohérents,
    exigence du cours citée, nombre d'exercices demandé par le ticket, valeurs calculées."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
            or set(item.classification.correct) != set(range(len(item.classification.categories)))
        ):
            errors.append(f"{item.key} : classification incohérente ou catégorie inutilisée.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
        if not REQ & set(item.requirement_ids):
            errors.append(f"{item.key} : l'exigence AP-C02 ou AP-C03 doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue au mini-examen.")
    if len(PRACTICE_ITEMS) < 18 or len(EXAM_ITEMS) != 10:
        errors.append("Ticket #227 : au moins 18 exercices et un mini-examen de 10 questions.")
    kinds = [i.kind for i in PRACTICE_ITEMS]
    if kinds.count(KIND_SCHEMA) != 2 or kinds.count(KIND_ORDER) < 4 or kinds.count(KIND_DATA) < 5:
        errors.append("Ticket #227 : schémas à compléter, procédures et protection des données attendus.")
    if any(len(v) > 1 for v in E11_VERDICTS) or len(set(E11_CORRECT)) != len(E11_CATEGORIES):
        errors.append("E11 : chaque plan doit manquer au plus un point, chaque verdict être utilisé.")
    if E06_OUT != ("+12 V",) or X02_OUT != ("+5 V",):
        errors.append("E06/X02 : tensions hors tolérance inattendues.")
    if (E12_MISSING, E12_DIFFERENT) != (("Tarifs.xlsx",), ("Radios-octobre.zip",)):
        errors.append("E12 : écarts d'intégrité inattendus.")
    if (X06_MISSING, X06_DIFFERENT) != (("Photos-chantier.zip",), ("Métrés.xlsx",)):
        errors.append("X06 : écarts d'intégrité inattendus.")
    if E14_MISSING != (PRE_CONSENT, PRE_AUTHORIZED) or X07_MISSING != (PRE_KEY, PRE_LICENSES):
        errors.append("E14/X07 : prérequis manquants inattendus.")
    if X05_MISSING != check_321(X05_COPIES) or len(X05_MISSING) != 2:
        errors.append("X05 : deux points de la règle 3-2-1 doivent manquer.")
    if (E22_RESULT[0], X10_RESULT[0]) != (4, 1) or X04_ERRORS != (3, 5):
        errors.append("E22/X10/X04 : parcours ou erreurs inattendus.")
    return errors

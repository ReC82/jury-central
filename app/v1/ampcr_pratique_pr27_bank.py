"""PR27 « Construire et justifier une procédure de diagnostic » — exercices corrigés et
mini-examen (ticket #226).

Même organisation que PR26 (`app.v1.ampcr_pratique_pr26_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 23 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — **huit procédures à ordonner et justifier** (cycle de diagnostic, tests
  du moins au plus invasif, couches réseau, adresse 169.254, retour arrière, test croisé d'une
  barrette, imprimante réseau, coupure Internet), **choix et interprétation de tests**
  (invasivité, test croisé, faux positifs et faux négatifs, test discriminant, contrôle de
  configuration, journaux, conditions de reproduction), **deux schémas à compléter** (arbres
  réseau et démarrage, servis en SVG), **deux parcours d'arbre** (système, matériel) et des
  **rédactions** (retour arrière, preuves, impact, escalade) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, entreprises et adresses sont **fictives** ; ordres de tests,
hypothèses restantes, conclusions de tests croisés, écarts de configuration, facteurs communs et
pistes des arbres viennent des fonctions de `app.v1.ampcr_pratique_pr27_figures`.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr27_figures import (
    BOOT_BLANK_ANSWERS,
    CROSS_HOST,
    CROSS_KINDS,
    DHCP_STEPS,
    FALSE_KINDS,
    FALSE_RESULTS,
    LEVEL_NAMES,
    METHOD_STEPS,
    NET_BLANK_ANSWERS,
    NET_LAYERS,
    ROLLBACK_STEPS,
    STATIC_BY_KEY,
    TREE_HARDWARE,
    TREE_NETWORK,
    TREE_OS,
    Probe,
    common_factors,
    config_diff,
    cross_test,
    is_discriminant,
    level_label,
    order_probes,
    precautions,
    remaining,
    walk,
)

PR27_CODE = "PR27"

KIND_ORDER = "procédure à ordonner et justifier"
KIND_TEST = "choix et interprétation des tests"
KIND_TREE = "arbre de décision"
KIND_SCHEMA = "schéma à compléter"
KIND_WRITE = "rédaction"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-15", "AP-C01"})
R_DIAG = ("AP-15", "AP-C01")
R_DATA = ("AP-15", "AP-C01", "AP-C03")  # protection des données du client
R_ESD = ("AP-15", "AP-C01", "AP-C02")  # intervention dans le matériel


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _text_doc(title: str, text: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="texte", content_text=text)


def _arrow(items: tuple[str, ...]) -> str:
    return " → ".join(items)


def _step_names(steps: tuple[tuple[str, str], ...]) -> str:
    return _arrow(tuple(label.lower() for label, _d in steps))


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(METHOD_STEPS)

# E02 : PC lent, six tests candidats à ordonner
E02_PROBES: tuple[Probe, ...] = (
    Probe("Réinstaller Windows après sauvegarde et accord écrit", 5, 120),
    Probe("Ouvrir le boîtier pour dépoussiérer le ventilateur du processeur", 4, 30),
    Probe("Lire le Gestionnaire des tâches et l'Observateur d'événements", 1, 10),
    Probe("Demander à l'utilisateur depuis quand et pendant quelle tâche", 0, 5),
    Probe("Redémarrer le poste après lui avoir fait enregistrer son travail", 2, 5),
    Probe("Démarrage minimal : désactiver les programmes tiers lancés au démarrage", 3, 15),
)
E02_ORDER = order_probes(E02_PROBES)
E02_SHOWN = tuple(E02_ORDER.index(p) for p in E02_PROBES)  # affichage = ordre de la liste ci-dessus

# E03 : niveau d'invasivité
E03_CASES: tuple[tuple[str, int], ...] = (
    ("Écouter l'utilisateur décrire ce qu'il faisait au moment du plantage", 0),
    ("Lire la sortie de ipconfig /all", 1),
    ("Consulter le journal Système dans l'Observateur d'événements", 1),
    ("Brancher la souris sur un autre port USB", 2),
    ("Redémarrer le poste", 2),
    ("Désactiver un service au démarrage avec msconfig", 3),
    ("Restaurer la version précédente du pilote graphique", 3),
    ("Remplacer une barrette de mémoire", 4),
    ("Réinitialiser une imprimante aux réglages d'usine", 5),
    ("Formater la partition système", 5),
)
E03_CORRECT = tuple(level for _t, level in E03_CASES)

# E04 : tests croisés
E04_CASES: tuple[tuple[str, bool, bool], ...] = (
    ("Barrette suspecte dans un PC sain : il bippe ; barrette saine dans le PC en panne : il démarre", False, True),
    ("Écran suspect (avec son câble) sur un autre PC : image normale ; écran sain sur le PC en panne : « Aucun signal »", True, False),
    ("Clavier suspect sur un autre PC : il fonctionne ; clavier sain sur le PC d'origine : il fonctionne aussi", True, True),
    ("Cordon réseau suspect sur un poste sain : pas de lien ; cordon neuf sur le poste d'origine : pas de lien", False, False),
    ("Imprimante suspecte sur un portable sain : rien ne sort ; imprimante de prêt sur le PC d'origine : impression correcte", False, True),
    ("Souris suspecte sur un autre PC : elle fonctionne ; souris neuve sur le PC d'origine : le pointeur ne bouge pas", True, False),
)
E04_VERDICTS = tuple(cross_test(a, b) for _t, a, b in E04_CASES)
E04_CORRECT = tuple(CROSS_KINDS.index(v) for v in E04_VERDICTS)

E05_CORRECT = tuple(FALSE_KINDS.index(k) for _t, k, _w in FALSE_RESULTS)

# E06 : matrice hypothèses × tests (écran noir, ventilateurs qui tournent)
E06_HYPS = ("H1 écran en panne", "H2 câble vidéo défectueux", "H3 sortie vidéo du PC en panne")
E06_TESTS: tuple[tuple[str, tuple[str, str, str]], ...] = (
    ("T1 — appuyer sur le bouton de menu de l'écran", ("aucun menu", "menu affiché", "menu affiché")),
    ("T2 — même écran et même câble sur un portable connu bon", ("pas d'image", "pas d'image", "image")),
    ("T3 — un câble neuf entre le PC et l'écran", ("pas d'image", "image", "pas d'image")),
    ("T4 — redémarrer le PC", ("pas d'image", "pas d'image", "pas d'image")),
)
E06_ALL = (0, 1, 2)
E06_NOT_DISCRIMINANT = tuple(name.split(" — ")[0] for name, exp in E06_TESTS if not is_discriminant(exp, E06_ALL))
E06_AFTER_T1 = remaining(E06_TESTS[0][1], "menu affiché", E06_ALL)
E06_AFTER_T3 = remaining(E06_TESTS[2][1], "image", E06_AFTER_T1)

# E07 : contrôle de configuration
E07_REFERENCE: dict[str, str] = {
    "Adresse IPv4": "192.168.20.21", "Masque": "255.255.255.0", "Passerelle": "192.168.20.1",
    "Serveur DNS": "192.168.20.10", "DHCP activé": "Non",
}
E07_OBSERVED: dict[str, str] = {
    "Adresse IPv4": "192.168.20.21", "Masque": "255.255.0.0", "Passerelle": "192.168.2.1",
    "Serveur DNS": "192.168.20.10", "DHCP activé": "Non",
}
E07_DIFF = config_diff(E07_REFERENCE, E07_OBSERVED)

# E08 : journal Système (extrait simplifié)
E08_LINES: tuple[str, ...] = (
    "Date et heure          Niveau        Source                   ID    Message",
    "26/10/2026 16:41:03    Erreur        disk                      7    Le périphérique \\Device\\Harddisk0\\DR0 a un bloc défectueux.",
    "26/10/2026 16:52:40    Erreur        disk                      7    Le périphérique \\Device\\Harddisk0\\DR0 a un bloc défectueux.",
    "26/10/2026 16:57:58    Erreur        disk                      7    Le périphérique \\Device\\Harddisk0\\DR0 a un bloc défectueux.",
    "27/10/2026 08:02:15    Critique      Kernel-Power             41    Le système a redémarré sans s'arrêter correctement au préalable.",
    "27/10/2026 08:02:20    Erreur        EventLog               6008    L'arrêt système précédent à 16:58:12 le 26/10/2026 n'était pas prévu.",
    "27/10/2026 08:03:01    Information   Service Control Manager 7036   Le service Spouleur d'impression est entré dans l'état : en cours d'exécution.",
)

# E09 : conditions de reproduction d'une imprimante « hors ligne »
E09_HEADER = ("Jour", "Heure", "Poste", "Imprimante inactive depuis plus d'une heure", "« Hors ligne »")
E09_ROWS: tuple[tuple[str, ...], ...] = (
    ("Lundi", "8 h 15", "PC-01", "oui", "oui"),
    ("Lundi", "10 h 20", "PC-02", "non", "non"),
    ("Lundi", "13 h 30", "PC-03", "oui", "oui"),
    ("Mardi", "8 h 05", "PC-02", "oui", "oui"),
    ("Mardi", "9 h 40", "PC-01", "non", "non"),
    ("Mardi", "16 h 10", "PC-03", "non", "non"),
)
E09_FACTORS = common_factors(E09_HEADER, E09_ROWS, outcome="« Hors ligne »", failure="oui")

# E12 / E13 : parcours d'arbres
E12_ANSWERS = (True, True, False)
E12_RESULT = walk(TREE_OS, E12_ANSWERS)
E12_PROGRAMS = 8
E12_RESTARTS = (E12_PROGRAMS - 1).bit_length()  # moitié par moitié : 8 → 4 → 2 → 1
E13_ANSWERS = (True, True, True, False)
E13_RESULT = walk(TREE_HARDWARE, E13_ANSWERS)

E14_STEPS = _labels(DHCP_STEPS)
E15_STEPS = _labels(ROLLBACK_STEPS)

# E16 : test croisé d'une barrette (à ordonner et justifier)
E16_STEPS: tuple[str, ...] = (
    "Noter les symptômes et exporter le journal des arrêts sur écran bleu",
    "Mettre hors tension, débrancher, porter le bracelet antistatique",
    "Retirer la barrette A ; laisser la barrette B seule dans le PC",
    "Lancer un test mémoire long (plusieurs passages) et une journée d'utilisation",
    "Monter la barrette A seule dans un PC sain du même modèle et lancer le même test",
    "Conclure avec la grille du test croisé et remplacer l'élément en cause",
)
E16_SHOWN = (3, 0, 5, 2, 1, 4)

# E20 : mesure d'impact avant de redémarrer un switch
E20_PRECAUTIONS = precautions(2)

# E22 : coupure Internet de tout le bureau, quatre tests à ordonner
E22_PROBES: tuple[Probe, ...] = (
    Probe("Redémarrer la box (coupe tout le bureau environ 5 minutes)", 2, 5),
    Probe("Réinitialiser la box aux réglages d'usine", 5, 30),
    Probe("Regarder les voyants de la box sans y toucher", 0, 1),
    Probe("ping de la passerelle depuis deux postes", 1, 3),
)
E22_ORDER = order_probes(E22_PROBES)

E23_STEPS = tuple(f"{name} — {test}" for name, _c, test in NET_LAYERS)

# --- Mini-examen -------------------------------------------------------------------------------

X02_PROBES: tuple[Probe, ...] = (
    Probe("Réinitialiser l'imprimante aux réglages d'usine", 5, 30),
    Probe("Redémarrer l'imprimante", 2, 5),
    Probe("Lire le message affiché sur l'écran de l'imprimante", 1, 1),
    Probe("ping de l'adresse de l'imprimante depuis un poste", 1, 2),
)
X02_ORDER = order_probes(X02_PROBES)
X03_VERDICT = cross_test(True, False)
X05_REFERENCE: dict[str, str] = {
    "Adresse IPv4": "192.168.5.40", "Masque": "255.255.255.0", "Passerelle": "192.168.5.1", "Serveur DNS": "192.168.5.1",
}
X05_OBSERVED: dict[str, str] = {
    "Adresse IPv4": "192.168.5.40", "Masque": "255.255.255.0", "Passerelle": "192.168.5.254", "Serveur DNS": "192.168.5.1",
}
X05_DIFF = config_diff(X05_REFERENCE, X05_OBSERVED)
X07_HEADER = ("Jour", "Heure", "Logiciel ouvert", "Station d'accueil branchée", "Écran figé")
X07_ROWS: tuple[tuple[str, ...], ...] = (
    ("Lundi", "9 h 30", "tableur", "oui", "oui"),
    ("Lundi", "14 h 00", "navigateur", "non", "non"),
    ("Mardi", "10 h 15", "navigateur", "oui", "oui"),
    ("Mardi", "15 h 40", "tableur", "non", "non"),
    ("Jeudi", "11 h 05", "logiciel de paie", "oui", "oui"),
)
X07_FACTORS = common_factors(X07_HEADER, X07_ROWS, outcome="Écran figé", failure="oui")
X09_ANSWERS = (True, True, False)
X09_RESULT = walk(TREE_NETWORK, X09_ANSWERS)


def _probe_line(p: Probe) -> str:
    return f"{p.label} ({level_label(p.level)}, {p.minutes} min)"


# =============================================================================================
# 23 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le cycle de diagnostic",
        question_type="ordering",
        requirement_ids=R_DIAG,
        kind=KIND_ORDER,
        context=(
            "Ton responsable affiche au mur de l'atelier le cycle que chaque technicien doit suivre pour chaque "
            "hypothèse, de la cause supposée jusqu'à la preuve de la réparation. Les six cartes ont été mélangées "
            "pendant le nettoyage de l'atelier ; tu dois les remettre dans l'ordre."
        ),
        instructions=("Remets les six étapes du cycle dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Hypothèse → test discriminant → résultat attendu → interprétation → action → validation (0,5 pt par étape)."),
        ),
        correction=(
            "1. Hypothèse : une cause qui explique tous les symptômes. 2. Test discriminant : celui dont le résultat change selon l'hypothèse vraie. 3. Résultat attendu : écrit avant de lancer le test, pour chaque hypothèse.",
            "4. Interprétation : on compare le résultat obtenu aux résultats attendus et on écarte les hypothèses contredites. 5. Action : on corrige la cause confirmée, avec ses précautions. 6. Validation : on refait le test du symptôme de départ. Écrire le résultat attendu avant le test empêche de « faire dire » au résultat ce que l'on espérait.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Ordonner six tests du moins au plus invasif",
        question_type="ordering",
        requirement_ids=R_DATA,
        kind=KIND_ORDER,
        context=(
            "Un graphiste se plaint d'un PC devenu très lent. Un collègue pressé propose de « tout réinstaller tout "
            "de suite ». Tu lui montres l'ordre dans lequel les six tests possibles doivent être faits, du moins "
            "invasif au plus invasif (convention du cours : à niveau égal, le plus rapide d'abord)."
        ),
        instructions=("Remets les six tests dans l'ordre où tu les fais.",),
        criteria=(
            _c("Ordre", 3, _arrow(tuple(p.label for p in E02_ORDER)) + " (0,5 pt par position)."),
        ),
        correction=(
            "Ordre : " + " ; ".join(f"{i}. {_probe_line(p)}" for i, p in enumerate(E02_ORDER, start=1)) + ".",
            "On commence par ce qui ne touche à rien (questionner, lire), puis ce qui se défait sans trace (redémarrer), puis une modification réversible notée (démarrage minimal). L'ouverture du boîtier demande la mise hors tension et l'accord du client ; la réinstallation détruit l'état du poste : elle vient en dernier, après sauvegarde vérifiée et accord écrit, et seulement si les tests précédents n'ont rien trouvé.",
        ),
        ordering=_shuffled_ordering(tuple(p.label for p in E02_ORDER), E02_SHOWN),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="À quel niveau d'invasivité appartient chaque geste ?",
        question_type="classification",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Avant de rédiger la procédure de diagnostic d'un dossier, tu classes les gestes possibles sur l'échelle "
            "d'invasivité du cours (0 à 5). Ce classement fixe l'ordre des tests et les précautions à prendre avant "
            "chacun d'eux."
        ),
        instructions=("Range chaque geste dans son niveau d'invasivité.",),
        criteria=(
            _c("Classement", 5, "0 : écouter l'utilisateur ; 1 : ipconfig /all, journal Système ; 2 : autre port USB, redémarrer ; 3 : msconfig, restaurer le pilote ; 4 : remplacer une barrette ; 5 : réinitialisation d'usine, formatage (0,5 pt par geste)."),
        ),
        correction=(
            "Niveau 0 : on ne touche à rien. Niveau 1 : on lit sans rien changer (sortie d'une commande, journal). Niveau 2 : on manipule, mais l'état revient tout seul (autre port, redémarrage). Niveau 3 : on modifie un réglage, il faut noter l'état initial pour pouvoir revenir.",
            "Niveau 4 : on intervient dans le matériel, hors tension et avec protection antistatique. Niveau 5 : l'opération efface ou remplace quelque chose de façon irréversible (réglages d'usine, formatage) : sauvegarde vérifiée et accord écrit avant.",
        ),
        classification=Classification(categories=LEVEL_NAMES, elements=tuple(t for t, _l in E03_CASES), correct=E03_CORRECT),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Interpréter des tests croisés",
        question_type="classification",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Dans un atelier de maintenance, chaque test croisé se fait en deux montages : A, l'élément suspect sur "
            "un poste sain ; B, un élément sain (connu bon) sur le poste suspect. Six fiches de la semaine donnent "
            "les deux résultats ; tu dois écrire la conclusion de chacune."
        ),
        instructions=("Range chaque test croisé dans la conclusion qu'il permet.",),
        criteria=(
            _c("Conclusions", 3, "Barrette et imprimante : élément en cause ; écran et souris : poste d'origine en cause ; clavier : panne non reproduite ; cordon : les deux échouent (0,5 pt par fiche)."),
        ),
        correction=(
            "Si la panne suit l'élément (A échoue, B fonctionne), l'élément est en cause : barrette, imprimante. Si la panne reste sur le poste (A fonctionne, B échoue), c'est le poste : sortie vidéo ou câble du PC pour l'écran, port ou pilote pour la souris.",
            "Si tout fonctionne, la panne n'a pas été reproduite : mauvais contact remis en place pendant le démontage, ou panne intermittente — on surveille. Si tout échoue, il y a deux causes, ou l'élément « sain » ne l'est pas : on revérifie le cordon neuf et le port du switch avant de conclure.",
        ),
        classification=Classification(categories=CROSS_KINDS, elements=tuple(t for t, _a, _b in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Faux positif ou faux négatif ?",
        question_type="classification",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Ton responsable a rassemblé huit situations où un test a trompé un technicien. Un faux positif signale "
            "une panne qui n'existe pas ; un faux négatif ne voit pas une panne qui existe. Tu les classes pour la "
            "formation des nouveaux."
        ),
        instructions=("Range chaque situation : faux positif ou faux négatif.",),
        criteria=(
            _c("Classement", 4, "Faux positifs : ping bloqué par le pare-feu ; piles du testeur ; mauvaise entrée HDMI ; cordon de test coupé. Faux négatifs : paires mélangées ; test mémoire d'un seul passage ; Wi-Fi qui ne coupe pas pendant l'intervention ; antivirus muet (0,5 pt par situation)."),
        ),
        correction=(
            "Faux positifs : le test « échoue » pour une autre raison que la panne cherchée — un pare-feu qui bloque le ping, un outil défaillant (piles), un mauvais réglage (entrée HDMI), un élément de test lui-même en panne. Parade : vérifier l'outil et le montage sur un élément connu bon (témoin).",
            "Faux négatifs : le test « réussit » parce qu'il ne mesure pas ce qui est en panne (continuité ≠ paires), qu'il est trop court ou fait hors des conditions de la panne (intermittente), ou que l'outil ne voit pas tout (antivirus). Un test négatif n'innocente que ce qu'il teste vraiment.",
        ),
        classification=Classification(categories=FALSE_KINDS, elements=tuple(t for t, _k, _w in FALSE_RESULTS), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Choisir le test qui départage",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Le PC de bureau d'une secrétaire démarre (ventilateurs, voyant), mais l'écran reste noir. Tu retiens "
            "trois hypothèses et tu prépares quatre tests. Le document 1 donne, pour chaque test, le résultat "
            "attendu selon l'hypothèse vraie."
        ),
        documents=(_table("Document 1 — Résultats attendus (support fictif)", ("Test", *E06_HYPS),
                          *((name, *exp) for name, exp in E06_TESTS)),),
        instructions=(
            "Indique le test qui ne sert à rien et explique pourquoi.",
            "Tu fais T1 : le menu de l'écran s'affiche. Quelles hypothèses restent ?",
            "Tu fais ensuite T3 et l'image apparaît : conclus et indique l'action et la validation.",
        ),
        criteria=(
            _c("Test inutile", 1, f"{', '.join(E06_NOT_DISCRIMINANT)} : même résultat attendu pour les trois hypothèses, il ne départage rien."),
            _c("Après T1", 1, "H1 écartée (l'écran affiche son menu) ; restent " + " et ".join(E06_HYPS[i].split()[0] for i in E06_AFTER_T1) + "."),
            _c("Conclusion", 2, f"Seule {E06_HYPS[E06_AFTER_T3[0]]} explique l'image avec un câble neuf : remplacer le câble ; valider au redémarrage et après une journée."),
        ),
        correction=(
            "T4 (redémarrer) donne « pas d'image » quelle que soit l'hypothèse : il ne départage rien et fait perdre du temps. Un test n'est utile que si ses résultats attendus diffèrent entre les hypothèses encore possibles.",
            "T1 : l'écran affiche son propre menu, il fonctionne : H1 écartée, restent H2 et H3. T3 : avec un câble neuf, l'image revient : seule H2 prévoyait ce résultat. Action : remplacer le câble vidéo (niveau 2). Validation : image au redémarrage, puis une journée d'utilisation sans coupure ; l'ancien câble est étiqueté « HS ».",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Contrôle de configuration d'un poste",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "À l'accueil d'une école, le poste PC-ACC-02 (adresse fixe) ouvre le serveur de fichiers 192.168.20.10 "
            "mais n'accède plus à Internet depuis qu'un stagiaire « a réglé le réseau ». Le document 1 compare la "
            "fiche de configuration du poste et le relevé de ipconfig /all."
        ),
        documents=(_table("Document 1 — Fiche de configuration et relevé (support fictif)", ("Paramètre", "Fiche (référence)", "Relevé ipconfig /all"),
                          *((k, v, E07_OBSERVED[k]) for k, v in E07_REFERENCE.items())),),
        instructions=(
            "Relève les écarts avec la référence.",
            "Explique pourquoi le serveur reste accessible alors qu'Internet ne l'est plus.",
            "Indique la correction, son niveau d'invasivité et la précaution à prendre avant.",
        ),
        criteria=(
            _c("Écarts", 1, " et ".join(E07_DIFF) + " différents de la fiche (masque 255.255.0.0 au lieu de 255.255.255.0 ; passerelle 192.168.2.1 au lieu de 192.168.20.1)."),
            _c("Explication", 2, "Le serveur 192.168.20.10 est dans le même réseau : pas besoin de passerelle. Pour Internet, le poste envoie à la passerelle 192.168.2.1, qui n'existe pas ; le masque /16 fait en plus croire que tout 192.168.x.x est local."),
            _c("Correction", 1, "Ressaisir masque et passerelle de la fiche (niveau 3), après avoir noté la configuration actuelle (ipconfig /all > fichier) ; tester ping de la passerelle puis un site."),
        ),
        correction=(
            f"Écarts : {', '.join(E07_DIFF).lower()}. Adresse et DNS sont conformes. Le contrôle de configuration consiste à comparer, paramètre par paramètre, le relevé à une référence écrite (fiche, plan d'adressage) : il trouve un réglage modifié sans avoir à deviner.",
            "Le serveur 192.168.20.10 est dans le même réseau que le poste : le trafic n'a pas besoin de passerelle. Pour Internet, le poste envoie tout à 192.168.2.1, adresse inexistante. Correction (niveau 3) : noter la configuration actuelle, ressaisir 255.255.255.0 et 192.168.20.1, puis valider : ping 192.168.20.1, un site, le serveur.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Lire un journal Système",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_TEST,
        context=(
            "Un dessinateur raconte : « Hier vers 17 h, l'écran s'est figé ; j'ai dû maintenir le bouton pour "
            "éteindre. Ce matin il a redémarré normalement. » Tu ouvres l'Observateur d'événements de son poste "
            "PC-DAO-02 ; le document 1 est un extrait simplifié du journal Système."
        ),
        documents=(_console("Document 1 — Journal Système, extrait simplifié (support fictif)", *E08_LINES),),
        instructions=(
            "Indique le premier événement anormal et ce qu'il signale.",
            "Explique ce que prouvent les événements 41 et 6008, et ce qu'ils ne prouvent pas.",
            "Donne ton hypothèse et ton premier geste, avec son niveau d'invasivité.",
        ),
        criteria=(
            _c("Premier événement", 1, "26/10 à 16:41:03, source disk, ID 7 : bloc défectueux sur le disque 0, répété trois fois avant le blocage."),
            _c("41 et 6008", 1, "Ils prouvent un arrêt non prévu à 16:58:12 (le bouton maintenu par l'utilisateur) ; ce sont des conséquences, pas la cause. 7036 est un événement normal."),
            _c("Hypothèse et geste", 2, "Disque système défaillant ; d'abord sauvegarder les données (avant tout autre test), puis lire l'état SMART (niveau 1) ; pas de réparation de disque avant la copie."),
        ),
        correction=(
            "On lit un journal dans l'ordre chronologique et on cherche le premier événement anormal avant l'heure du problème : ici, trois erreurs « disk 7 » (bloc défectueux) entre 16:41 et 16:57, juste avant le blocage. Les événements 41 (Kernel-Power) et 6008 (EventLog) du matin disent seulement que le poste s'est arrêté brutalement : c'est l'utilisateur qui a maintenu le bouton. Ce sont des conséquences.",
            "Hypothèse : le disque système commence à lâcher. Premier geste : sauvegarder immédiatement les données du dessinateur (copie relue), puis lire l'état SMART (niveau 1, lecture seule). Aucune vérification ou réparation de disque n'est lancée avant la copie : elle écrirait sur un disque fragile.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Trouver les conditions de reproduction",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Dans une agence de voyages, l'imprimante réseau apparaît « hors ligne » de temps en temps, sur des "
            "postes différents ; un second essai quelques minutes plus tard fonctionne. Tu as demandé aux employés "
            "de noter chaque impression pendant deux jours (document 1)."
        ),
        documents=(_table("Document 1 — Journal des impressions (support fictif)", E09_HEADER, *E09_ROWS),),
        instructions=(
            "Relève la condition présente à chaque panne et absente sinon.",
            "Formule une hypothèse et le test qui reproduit la panne à volonté.",
            "Écris le critère de validation.",
        ),
        criteria=(
            _c("Condition", 1, " ; ".join(f"{n} = {v}" for n, v in E09_FACTORS) + " ; le poste et l'heure varient : ce ne sont pas des facteurs."),
            _c("Hypothèse et test", 2, "L'imprimante passe en veille profonde et ne répond pas assez vite ; test : la laisser inactive plus d'une heure, puis ping et impression depuis un poste."),
            _c("Validation", 1, "Après réglage de la veille (état initial noté), plusieurs impressions après plus d'une heure d'inactivité, puis une semaine sans « hors ligne »."),
        ),
        correction=(
            "On compare les lignes « oui » et « non » : la seule condition commune à toutes les pannes, et jamais vue sans panne, est une imprimante inactive depuis plus d'une heure. Le poste (PC-01, PC-02, PC-03) et l'heure changent : ils ne sont pas en cause.",
            "Hypothèse : la veille profonde de l'imprimante. La panne devient reproductible : on laisse l'imprimante inactive plus d'une heure, puis on la teste. Action (niveau 3) : noter le réglage de veille actuel, puis l'allonger ou activer le réveil réseau. Validation : impressions après une longue inactivité, puis une semaine de journal sans panne.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : l'arbre réseau",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_SCHEMA,
        context=(
            "Pour le classeur du support d'une PME, tu prépares l'arbre de décision « un poste n'accède pas au réseau "
            "ou à Internet ». Quatre pistes « si non » ont été effacées sur la version imprimée. Le document 1 est "
            "l'arbre à terminer."
        ),
        documents=(_schema("pr27-arbre-reseau-a-completer", "Document 1 — Arbre réseau à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④ (piste à suivre quand la réponse est « non »).",
            "Explique pourquoi on teste le lien avant l'adresse IP.",
        ),
        criteria=(
            _c("Pistes", 2, "① physique : câble, prise, port, test croisé ; ② DHCP : renouveler, autre poste sur la même prise, port/VLAN, serveur ; ③ configuration IP : masque, passerelle, conflit, plan d'adressage ; ④ DNS : serveurs DNS, nslookup, flushdns (0,5 pt chacune)."),
            _c("Ordre", 1, "Approche par couches : sans lien physique, aucune adresse ne peut être obtenue ; on valide la couche du dessous avant celle du dessus."),
        ),
        correction=(
            " ".join(f"{k} {v}" for k, v in NET_BLANK_ANSWERS.items()),
            "L'arbre suit les couches de bas en haut : physique, adresse, passerelle, Internet, noms. Une couche ne fonctionne que si celles du dessous fonctionnent : tester le DNS d'un poste sans lien ne prouve rien.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : l'arbre de démarrage",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_SCHEMA,
        context=(
            "Un atelier de réparation affiche l'arbre « le PC ne démarre pas jusqu'au système » au-dessus du plan de "
            "travail. Quatre pistes ont été effacées par une tache. Le document 1 est l'arbre à terminer ; la "
            "deuxième piste est encore lisible."
        ),
        documents=(_schema("pr27-arbre-demarrage-a-completer", "Document 1 — Arbre de démarrage à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Indique la précaution commune aux pistes ② et ④.",
        ),
        criteria=(
            _c("Pistes", 2, "① alimentation : prise, câble, interrupteur, bouton, bloc ; ② disque : câble SATA ou M.2, disque défaillant ; ③ ordre de démarrage : photo de l'ordre initial, menu ponctuel, correction ; ④ chargeur : réparation du démarrage après sauvegarde (0,5 pt chacune)."),
            _c("Précaution", 1, "Protéger les données avant toute action sur le disque ou le système : sauvegarde (ou lecture du disque sur un autre poste) avant réparation."),
        ),
        correction=(
            " ".join(f"{k} {v}" for k, v in BOOT_BLANK_ANSWERS.items()),
            "Les pistes ② et ④ touchent au disque ou au système : avant toute réparation, on met les données à l'abri. La piste ③ modifie un réglage : l'ordre initial est photographié pour pouvoir revenir en arrière.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Parcourir l'arbre « système »",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TREE,
        context=(
            "Le portable de Marc met cinq minutes à devenir utilisable après l'ouverture de session. Tu as noté tes "
            "constats (document 1) et tu suis l'arbre de décision « système » du cours, question par question."
        ),
        documents=(_table("Document 1 — Constats (support fictif)", ("Question de l'arbre", "Constat"),
                          (TREE_OS.questions[0][0], "oui : aucune erreur de disque ou de mémoire"),
                          (TREE_OS.questions[1][0], "oui : même lenteur avec le compte de test"),
                          (TREE_OS.questions[2][0], "non : en démarrage minimal, la session est prête en 40 s")),),
        instructions=(
            "Donne la piste où mène l'arbre et justifie.",
            "Huit programmes tiers se lancent au démarrage et un seul est en cause : combien de redémarrages au plus pour le trouver par moitiés ?",
            "Donne la précaution avant le démarrage minimal.",
        ),
        criteria=(
            _c("Piste", 1, f"Question {E12_RESULT[0]} : {E12_RESULT[1]}"),
            _c("Redémarrages", 2, f"{E12_RESTARTS} : 8 → 4 → 2 → 1 (on réactive la moitié des programmes à chaque essai)."),
            _c("Précaution", 1, "Niveau 3 : noter les programmes et services actifs (état initial) pour pouvoir tout réactiver ; prévenir Marc."),
        ),
        correction=(
            f"Les deux premières réponses sont « oui » : ni disque ni mémoire, et le problème n'est pas lié au profil de Marc. La troisième est « non » : sans les programmes tiers, la lenteur disparaît. Piste : {E12_RESULT[1]}",
            f"Par moitiés : on réactive 4 programmes ; si la lenteur revient, le coupable est parmi eux, sinon parmi les 4 autres ; puis 2, puis 1. Au plus {E12_RESTARTS} redémarrages, au lieu de 8 en les testant un par un. Avant le démarrage minimal (niveau 3), on note l'état initial pour pouvoir revenir.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Parcourir l'arbre « matériel »",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TREE,
        context=(
            "Dans un cabinet comptable, le scanner USB de la réception ne numérise plus. Tu suis l'arbre de décision "
            "« matériel » du cours ; le document 1 donne tes constats dans l'ordre des questions de l'arbre."
        ),
        documents=(_table("Document 1 — Constats (support fictif)", ("Question de l'arbre", "Constat"),
                          (TREE_HARDWARE.questions[0][0], "oui : voyant vert allumé"),
                          (TREE_HARDWARE.questions[1][0], "oui : l'autotest du bouton « Test » se termine sans erreur"),
                          (TREE_HARDWARE.questions[2][0], "oui : listé dans le gestionnaire de périphériques"),
                          (TREE_HARDWARE.questions[3][0], "non : point d'exclamation jaune, « pilote non installé »")),),
        instructions=(
            "Donne la piste où mène l'arbre.",
            "Indique le niveau d'invasivité de l'action et la précaution à prendre avant.",
            "Écris le test de validation.",
        ),
        criteria=(
            _c("Piste", 1, f"Question {E13_RESULT[0]} : {E13_RESULT[1]}"),
            _c("Niveau et précaution", 2, f"{level_label(3)} : noter le pilote et sa version en place, prévenir l'utilisatrice ; pilote du site du fabricant."),
            _c("Validation", 1, "Numériser un document de la réception vers le dossier habituel ; plus de point d'exclamation."),
        ),
        correction=(
            f"Alimentation, autotest et détection sont bons : le scanner et sa liaison USB fonctionnent. Le point d'exclamation désigne le pilote. Piste : {E13_RESULT[1]}",
            "Installer un pilote modifie la configuration (niveau 3) : on note l'état initial (pilote et version, capture du gestionnaire), on prend le pilote du fabricant pour ce modèle et ce système. Validation : une numérisation réelle de l'utilisatrice, dans son dossier habituel.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Ordonner la procédure « adresse 169.254.x.x »",
        question_type="ordering",
        requirement_ids=R_DIAG,
        kind=KIND_ORDER,
        context=(
            "Dans une fiduciaire, un poste déplacé dans un autre bureau affiche une adresse 169.254.x.x. Ta "
            "responsable te demande la procédure écrite à suivre dans ce cas ; ses cinq étapes ont été notées dans le "
            "désordre sur un brouillon."
        ),
        instructions=("Remets les cinq étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 2.5, _step_names(DHCP_STEPS) + " (0,5 pt par étape)."),
        ),
        correction=(
            "1. Lire (niveau 1) : lien présent et adresse 169.254 confirment que le poste n'obtient pas de bail. 2. Renouveler le bail (niveau 2) : la cause peut être passagère. 3. Test croisé : un portable connu bon sur la même prise dit si c'est la prise ou le poste.",
            "4. Autre prise du bon VLAN : confirme le port ou le VLAN de la prise d'origine. 5. Escalader avec les résultats si la correction (switch, serveur DHCP) sort de tes droits. Chaque étape change une seule variable.",
        ),
        ordering=_shuffled_ordering(E14_STEPS, (2, 4, 0, 3, 1)),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Ordonner un plan de retour arrière",
        question_type="ordering",
        requirement_ids=R_DATA,
        kind=KIND_ORDER,
        context=(
            "Tu dois mettre à jour le pilote de la carte réseau d'un serveur d'impression, pendant la pause de midi. "
            "Ton responsable exige un plan de retour arrière écrit ; tu as noté six étapes dans le désordre et tu "
            "dois les remettre dans l'ordre."
        ),
        instructions=("Remets les six étapes du plan dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, _step_names(ROLLBACK_STEPS) + " (0,5 pt par étape)."),
        ),
        correction=(
            "On note d'abord l'état initial et on le sauvegarde : sans cela, impossible de revenir. On écrit le critère d'échec AVANT la modification (par exemple : pas de réseau 5 minutes après le redémarrage), pour décider sans hésiter.",
            "On applique une seule modification, on refait le test de départ et celui des fonctions voisines (impression depuis deux postes). Si le critère d'échec est atteint, on restaure l'ancien pilote et on vérifie qu'on est bien revenu à l'état initial.",
        ),
        ordering=_shuffled_ordering(E15_STEPS, (4, 2, 0, 5, 3, 1)),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Ordonner et justifier le test croisé d'une barrette",
        question_type="document_analysis",
        requirement_ids=R_ESD,
        kind=KIND_ORDER,
        context=(
            "Un PC de bureau à deux barrettes (A et B) s'arrête sur un écran bleu deux fois par semaine. Un test "
            "mémoire a désigné la barrette A une fois. Un PC sain du même modèle est disponible à l'atelier. Le "
            "document 1 liste les étapes de ta procédure dans le désordre."
        ),
        documents=(_table("Document 1 — Étapes à ordonner (support fictif)", ("Repère", "Étape"),
                          *((chr(ord("a") + i), E16_STEPS[j]) for i, j in enumerate(E16_SHOWN))),),
        instructions=(
            "Donne l'ordre des étapes (repères a à f).",
            "Justifie la place de chaque étape en une phrase.",
        ),
        criteria=(
            _c("Ordre", 2, "Symptômes et journal → hors tension et ESD → B seule → test long → A seule dans le PC sain → conclusion."),
            _c("Justifications", 3, "Preuves avant de toucher ; sécurité avant d'ouvrir ; une seule variable (B seule) ; test long car panne intermittente ; second montage du test croisé ; conclusion par la grille (0,5 pt par justification, 0,5 pt pour l'ensemble)."),
        ),
        correction=(
            "Ordre : " + " → ".join(chr(ord("a") + E16_SHOWN.index(j)) for j in range(len(E16_STEPS))) + ". On garde d'abord les preuves (journal), puis on se met en sécurité (hors tension, bracelet) avant d'ouvrir. On ne change qu'une variable : B seule.",
            "La panne est intermittente : un test court ne prouve rien, il faut plusieurs passages et une journée d'utilisation. Le second montage (A seule dans le PC sain) complète le test croisé : si A échoue là-bas et que B seule fonctionne ici, la barrette A est en cause.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Rédiger la procédure pour une imprimante réseau « hors ligne »",
        question_type="long_answer",
        requirement_ids=R_DIAG,
        kind=KIND_ORDER,
        context=(
            "Dans une PME de douze postes, l'imprimante réseau IMP-02 (adresse fixe 192.168.1.40) apparaît « hors "
            "ligne » sur tous les postes depuis ce matin. La veille, des travaux d'électricité ont eu lieu dans le "
            "couloir où elle se trouve. Tu dois rédiger ta procédure de diagnostic avant d'intervenir."
        ),
        instructions=(
            "Rédige au moins cinq tests, ordonnés du moins au plus invasif.",
            "Pour chacun, donne le niveau, le résultat attendu et ce qu'il écarte.",
        ),
        criteria=(
            _c("Ordre", 2, "Lecture d'abord (écran et voyants de l'imprimante, voyant du câble), puis ping 192.168.1.40, puis manipulations réversibles (câble, prise, redémarrage), puis configuration ; réinitialisation en dernier."),
            _c("Résultats attendus", 2, "Pour chaque test, ce qu'on attend si l'hypothèse est vraie : imprimante éteinte, lien absent (prise débranchée par les travaux), adresse changée, file d'attente."),
            _c("Justification", 1, "Tous les postes touchés : l'élément commun (l'imprimante, son câble, sa prise) ; les travaux sont le changement récent ; une variable à la fois."),
        ),
        correction=(
            "Exemple : 1) écran et voyants de l'imprimante (niveau 1) : allumée et « Prête » ? sinon alimentation (prise coupée par les travaux). 2) voyant de lien à l'arrière (niveau 1) : éteint → câble ou prise réseau. 3) ping 192.168.1.40 depuis un poste (niveau 1) : pas de réponse → réseau ou adresse ; réponse → configuration des postes.",
            "4) imprimer la page de configuration (niveau 2) : l'adresse est-elle encore 192.168.1.40 ? 5) changer de cordon ou de prise (niveau 2, une variable à la fois). 6) redémarrer l'imprimante (niveau 2). La réinitialisation d'usine (niveau 5) n'est envisagée qu'en dernier, configuration sauvegardée. Tous les postes étant touchés, on cherche l'élément commun, en partant du changement récent : les travaux.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Plan de retour arrière d'une mise à jour de pilote graphique",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Un bureau d'études demande la mise à jour du pilote graphique d'un poste de dessin assisté (DAO), parce "
            "que le logiciel de dessin plante à l'ouverture des grands plans. Le poste sert toute la journée ; le "
            "dessinateur doit rendre un plan demain."
        ),
        instructions=(
            "Rédige le plan de retour arrière : état initial, sauvegarde, critère d'échec, retour, vérification.",
            "Indique comment revenir en arrière si l'écran reste noir après la mise à jour.",
        ),
        criteria=(
            _c("État initial et sauvegarde", 1, "Version du pilote notée, point de restauration créé, ancien pilote conservé ; plans du dessinateur enregistrés."),
            _c("Critère d'échec", 1, "Écrit avant : écran noir, plantage à l'ouverture d'un grand plan, ou affichage dégradé ; délai maximum (par exemple 30 min)."),
            _c("Retour arrière", 1, "Gestionnaire de périphériques → propriétés de la carte → Pilote → « Restaurer le pilote » ; écran noir : mode sans échec, puis restauration ou point de restauration."),
            _c("Vérification", 1, "Ouvrir un grand plan, affichage normal ; retour à la version notée si retour arrière ; tout noté sur la fiche."),
        ),
        correction=(
            "Avant : noter la version du pilote, créer un point de restauration, garder l'ancien pilote, faire enregistrer les plans. Critère d'échec écrit à l'avance : écran noir, plantage à l'ouverture d'un grand plan, ou affichage dégradé, constaté dans les 30 minutes. Intervention en dehors des heures de travail du dessinateur.",
            "Retour : Gestionnaire de périphériques, propriétés de la carte graphique, onglet Pilote, « Restaurer le pilote ». Si l'écran reste noir, démarrer en mode sans échec (affichage de base) pour restaurer le pilote ou revenir au point de restauration. Vérification : la version notée est revenue et le logiciel s'ouvre comme avant ; on note tout sur la fiche.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Conserver les preuves sur un poste suspect",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Une employée d'un cabinet d'avocats signale qu'une fenêtre « Support Microsoft » lui a demandé "
            "d'appeler un numéro ; au téléphone, elle a laissé une personne prendre la main à distance sur son poste "
            "pendant dix minutes. Tu es technicien de premier niveau."
        ),
        instructions=(
            "Indique, dans l'ordre, ce que tu fais pour conserver les preuves.",
            "Indique ce que tu ne fais pas, et à qui tu escalades.",
        ),
        criteria=(
            _c("Preuves", 2, "Noter l'heure et le récit, photographier l'écran et le numéro affiché, isoler le poste du réseau sans l'éteindre, noter le logiciel de prise de main utilisé, conserver les journaux."),
            _c("Interdits et escalade", 2, "Ne pas désinstaller, nettoyer ni réinstaller soi-même ; ne pas se connecter avec d'autres comptes sur ce poste ; escalader au responsable informatique ou sécurité ; changer les mots de passe depuis un autre poste sain."),
        ),
        correction=(
            "1) Noter l'heure, ce que l'employée a vu et fait, le numéro appelé. 2) Photographier l'écran. 3) Isoler le poste du réseau (câble, Wi-Fi) sans l'éteindre : la personne ne peut plus agir, et l'état reste observable. 4) Noter le logiciel de prise de main à distance, sans le désinstaller. 5) Conserver les journaux.",
            "On ne « nettoie » rien et on ne réinstalle pas : ce serait effacer les traces dont le responsable a besoin pour savoir ce qui a été fait ou volé. On escalade immédiatement au responsable informatique ou sécurité, avec les preuves. Les mots de passe de l'employée sont changés depuis un autre poste, sain.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Mesurer l'impact d'un test avant de le lancer",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_WRITE,
        context=(
            "Plusieurs postes du 1er étage d'une mutuelle perdent le réseau quelques secondes de temps en temps. Un "
            "collègue propose de redémarrer tout de suite le switch SW-1ER, à 10 h. Le document 1 est le plan de "
            "brassage de ce switch."
        ),
        documents=(_table("Document 1 — Plan de brassage du switch SW-1ER (support fictif)", ("Ports", "Appareils", "Service"),
                          ("1 à 6", "6 postes", "Comptabilité"),
                          ("7 et 8", "2 téléphones IP", "Accueil"),
                          ("9", "Imprimante IMP-1ER", "Tout l'étage"),
                          ("10", "Point d'accès Wi-Fi AP-1ER", "Salle de réunion"),
                          ("24", "Liaison vers le switch principal", "—")),),
        instructions=(
            "Indique qui sera coupé, et ce qui peut être perdu.",
            "Donne le niveau d'invasivité du test et les précautions qu'il exige.",
            "Propose un moment et deux tests moins invasifs à faire avant.",
        ),
        criteria=(
            _c("Impact", 1, "10 appareils : 6 postes de la comptabilité, 2 téléphones de l'accueil (appels en cours coupés), l'imprimante, le point d'accès (toute la salle de réunion) ; travail non enregistré."),
            _c("Niveau et précautions", 1, f"{level_label(2)} : " + " ; ".join(E20_PRECAUTIONS) + "."),
            _c("Moment et tests", 2, "Pause de midi ou après 17 h, annoncé ; avant : lire les voyants et le journal du switch, relever quels postes coupent et quand (journal), ping -t vers la passerelle depuis deux postes."),
        ),
        correction=(
            "Redémarrer SW-1ER coupe tout ce qui y est branché : 6 postes, 2 téléphones (appels perdus), l'imprimante et le point d'accès (tous les portables de la salle de réunion). Un travail non enregistré ou une réservation en cours peuvent être perdus. Le test est réversible (niveau 2) mais son impact est large.",
            "Précautions : " + " ; ".join(E20_PRECAUTIONS) + ". On le fait à la pause de midi ou après 17 h, annoncé à l'étage. Avant, des tests sans coupure : voyants et journal du switch, journal des coupures (quels postes, quand), ping -t depuis deux postes. Le redémarrage efface aussi le journal en mémoire du switch : on le relève avant.",
        ),
    ),
    PR06Item(
        key="E21",
        usage=USAGE_PRACTICE,
        title="Proposer une alternative et escalader",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Le portable d'une infirmière coordinatrice n'affiche plus rien sur son écran intégré. Il est sous "
            "garantie du fabricant jusqu'en 2027 ; ta société n'a pas le droit de l'ouvrir. Le document 1 résume les "
            "tests déjà faits ; elle a besoin de son portable pour son travail de demain."
        ),
        documents=(_table("Document 1 — Tests réalisés (support fictif)", ("Test", "Niveau", "Résultat"),
                          ("Voyant d'alimentation et ventilateur", "0", "allumés"),
                          ("Écran externe branché en HDMI", "2", "image normale, bureau Windows"),
                          ("Luminosité au maximum (touches Fn)", "2", "écran intégré toujours noir"),
                          ("Lampe de poche contre l'écran intégré", "2", "le bureau Windows apparaît, très sombre")),),
        instructions=(
            "Interprète les tests : quelle partie est en cause ?",
            "Explique pourquoi tu escalades et rédige la demande au fabricant.",
            "Propose une alternative pour demain.",
        ),
        criteria=(
            _c("Interprétation", 1, "Image produite (écran externe) et affichée sur la dalle (visible à la lampe) : seul le rétroéclairage de l'écran intégré est en cause."),
            _c("Escalade", 2, "Sous garantie : ne pas ouvrir ; demande au fabricant avec n° de série, symptôme, tests et résultats, date d'achat ; sauvegarde des données avant envoi, accord de l'utilisatrice."),
            _c("Alternative", 1, "Écran externe au bureau, ou portable de prêt configuré avec son compte ; noté sur la fiche."),
        ),
        correction=(
            "L'écran externe affiche une image normale : processeur, mémoire, système et sortie vidéo fonctionnent. À la lampe, l'image apparaît sur la dalle : la dalle reçoit l'image, mais l'éclairage arrière ne s'allume plus. Cause : le rétroéclairage (ou son alimentation).",
            "Le portable est sous garantie : l'ouvrir l'annulerait ; c'est une limite d'autorisation, on escalade au fabricant. Demande : modèle et n° de série, date d'achat, symptôme, les quatre tests et leurs résultats, conclusion « rétroéclairage ». Avant l'envoi : sauvegarde de ses données, accord écrit. Alternative : écran externe au bureau ou portable de prêt, noté sur la fiche.",
        ),
    ),
    PR06Item(
        key="E22",
        usage=USAGE_PRACTICE,
        title="Ordonner et justifier les tests d'une coupure Internet",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_ORDER,
        context=(
            "Dans une agence de communication de huit personnes, plus aucun poste n'accède à Internet depuis 14 h ; le "
            "partage de fichiers interne fonctionne. Le document 1 liste quatre tests proposés par l'équipe, dans le "
            "désordre."
        ),
        documents=(_table("Document 1 — Tests proposés (support fictif)", ("Repère", "Test"),
                          *((chr(ord("a") + i), p.label) for i, p in enumerate(E22_PROBES))),),
        instructions=(
            "Donne l'ordre des tests (repères a à d) du moins au plus invasif.",
            "Justifie chaque position et donne les précautions des deux derniers.",
        ),
        criteria=(
            _c("Ordre", 2, " → ".join(chr(ord("a") + E22_PROBES.index(p)) for p in E22_ORDER) + " : " + _arrow(tuple(p.label for p in E22_ORDER)) + "."),
            _c("Justifications", 2, "Regarder sans toucher ; lire par un ping ; redémarrer (niveau 2) : coupe tout le bureau, prévenir et faire enregistrer ; réinitialiser (niveau 5) : efface la configuration de la box, à éviter, sauvegarde de la configuration et identifiants du fournisseur, accord."),
        ),
        correction=(
            "Ordre : " + " ; ".join(f"{i}. {_probe_line(p)}" for i, p in enumerate(E22_ORDER, start=1)) + ".",
            "Les voyants de la box (ligne, Internet) se lisent sans rien toucher. Le ping de la passerelle depuis deux postes dit si le réseau local va jusqu'à la box (le partage interne fonctionne déjà). Le redémarrage coupe tout le bureau : on prévient et on fait enregistrer. La réinitialisation efface la configuration : en dernier recours seulement, configuration sauvegardée, identifiants du fournisseur en main, accord du responsable — souvent, un appel au fournisseur vient avant.",
        ),
    ),
    PR06Item(
        key="E23",
        usage=USAGE_PRACTICE,
        title="Ordonner les couches réseau pour une approche ascendante",
        question_type="ordering",
        requirement_ids=R_DIAG,
        kind=KIND_ORDER,
        context=(
            "Un nouveau technicien doit apprendre à diagnostiquer « plus rien ne passe » sur un poste en partant de "
            "la couche la plus basse. Tu lui donnes les cinq couches avec leur test typique, mais dans le désordre, "
            "pour qu'il les remette en ordre."
        ),
        instructions=("Remets les cinq couches dans l'ordre de l'approche ascendante (de la plus basse à la plus haute).",),
        criteria=(
            _c("Ordre", 2.5, _arrow(tuple(name for name, _c, _t in NET_LAYERS)) + " (0,5 pt par couche)."),
        ),
        correction=(
            "Physique (câble, voyant) → liaison (carte, port, VLAN, association Wi-Fi) → réseau (adresse, passerelle) → transport (port du service) → application (DNS, compte, droits).",
            "Chaque couche s'appuie sur celle du dessous : on la valide avant de monter. Quand un seul service échoue alors que le reste fonctionne, on peut partir du haut (descendante) ; le ping de la passerelle coupe le problème en deux (par division).",
        ),
        ordering=_shuffled_ordering(E23_STEPS, (2, 4, 1, 3, 0)),
    ),
)

# =============================================================================================
# Mini-examen /20 (10 questions de 2 points, réponses libres)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Un test discriminant pour des haut-parleurs muets",
        question_type="long_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Dans une salle de formation, les haut-parleurs USB du PC du formateur ne produisent plus aucun son. Tu "
            "retiens trois hypothèses : haut-parleurs en panne ; pilote audio défaillant ; mauvaise sortie audio "
            "choisie par défaut dans Windows."
        ),
        instructions=("Propose un test qui écarte au moins une hypothèse et donne le résultat attendu pour chacune des trois.",),
        criteria=(
            _c("Test", 1, "Un test discriminant, par exemple : haut-parleurs sur un autre PC (connu bon) ; ou lire la sortie par défaut dans les paramètres de son ; ou un casque sur le PC."),
            _c("Résultats attendus", 1, "Pour chaque hypothèse : ex. haut-parleurs sur un autre PC — en panne : aucun son ; pilote ou sortie : son normal (écarte la panne des haut-parleurs)."),
        ),
        correction=(
            "Exemple : brancher les haut-parleurs sur un autre PC connu bon (niveau 2). Si les haut-parleurs sont en panne : toujours aucun son. Si c'est le pilote ou la sortie par défaut du PC du formateur : le son sort sur l'autre PC. Le test écarte donc soit la première hypothèse, soit les deux autres.",
            "Autre test accepté : lire la sortie audio par défaut (niveau 1) — si ce n'est pas les haut-parleurs USB, l'hypothèse « sortie » est confirmée. L'important : écrire avant le test le résultat attendu pour chaque hypothèse.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Ordonner quatre tests sur une imprimante partagée",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_ORDER,
        context=(
            "Dans une étude de notaire, l'imprimante réseau partagée n'imprime plus pour personne depuis ce matin. "
            "Le document 1 liste les quatre tests que tu envisages ; la convention du cours s'applique (du moins au "
            "plus invasif ; à niveau égal, le plus rapide)."
        ),
        documents=(_table("Document 1 — Tests envisagés (support fictif)", ("Repère", "Test", "Durée"),
                          *((chr(ord("a") + i), p.label, f"{p.minutes} min") for i, p in enumerate(X02_PROBES))),),
        instructions=("Donne l'ordre des tests et justifie la place du dernier.",),
        criteria=(
            _c("Ordre", 1, " → ".join(chr(ord("a") + X02_PROBES.index(p)) for p in X02_ORDER) + " : message, ping, redémarrage, réinitialisation."),
            _c("Justification", 1, "Réinitialisation d'usine (niveau 5) : efface la configuration (adresse, partage) ; en dernier, après sauvegarde de la configuration et accord."),
        ),
        correction=(
            "Ordre : " + " ; ".join(f"{i}. {_probe_line(p)}" for i, p in enumerate(X02_ORDER, start=1)) + ". Lire le message, puis le ping (même niveau, plus long), puis le redémarrage (réversible, prévenir les utilisateurs).",
            "La réinitialisation d'usine vient en dernier : elle efface l'adresse et les réglages de l'imprimante, ce qui couperait tous les postes même après réparation. On l'envisage seulement après les autres tests, configuration sauvegardée et accord du responsable.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Conclure un test croisé sur une clé Wi-Fi",
        question_type="short_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Un PC de bureau sans carte Wi-Fi intégrée utilise une clé Wi-Fi USB ; il ne se connecte plus. Tu fais un "
            "test croisé : la clé suspecte sur un portable sain se connecte normalement ; une clé neuve sur le PC "
            "d'origine ne se connecte pas non plus."
        ),
        instructions=("Donne la conclusion du test croisé et les deux pistes suivantes à tester.",),
        criteria=(
            _c("Conclusion", 1, f"{X03_VERDICT} : la clé n'est pas en cause."),
            _c("Pistes", 1, "Port USB du PC (autre port), pilote ou profil Wi-Fi enregistré, configuration réseau du PC (deux pistes du poste)."),
        ),
        correction=(
            f"A (clé suspecte sur un poste sain) fonctionne, B (clé saine sur le poste suspect) échoue : {X03_VERDICT.lower()}. On cherche sur le PC : un autre port USB, le pilote de la clé, le profil Wi-Fi enregistré (clé de sécurité obsolète) ou la configuration réseau.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Un testeur de câble qui dit « OK »",
        question_type="long_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Un poste fixe a des coupures et un débit très instable. Le câble posé par un électricien passe le test "
            "d'un simple testeur de continuité (huit voyants allumés dans l'ordre). L'électricien en conclut que le "
            "câble est bon."
        ),
        instructions=("Explique pourquoi cette conclusion peut être fausse et quel test fait la preuve.",),
        criteria=(
            _c("Faux négatif", 1, "Le testeur de continuité ne vérifie que la correspondance broche à broche ; des paires mélangées (paires séparées), une diaphonie ou une atténuation passent le test : faux négatif."),
            _c("Bon test", 1, "Test croisé avec un cordon connu bon, ou mesure par un testeur qui contrôle les paires et la qualité (certificateur) ; vérifier le sertissage selon T568A/B."),
        ),
        correction=(
            "Un testeur de continuité allume ses voyants si chaque broche est reliée à la même broche en face. Si deux fils de paires différentes ont été inversés aux deux bouts, la continuité est correcte mais les paires torsadées sont cassées : diaphonie, erreurs, débit instable. Le test « négatif » ne prouve que la continuité : c'est un faux négatif pour cette panne.",
            "Preuve : remplacer temporairement par un cordon connu bon (test croisé) ; ou mesurer avec un testeur qui contrôle les paires (certificateur) ; vérifier les deux sertissages avec la même norme T568A ou T568B.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Contrôle de configuration d'une imprimante",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Une imprimante multifonction d'un cabinet dentaire imprime normalement depuis tous les postes, mais "
            "l'envoi des numérisations par courriel (serveur de messagerie sur Internet) échoue. Le document 1 "
            "compare sa fiche de configuration et son relevé."
        ),
        documents=(_table("Document 1 — Fiche et relevé (support fictif)", ("Paramètre", "Fiche", "Relevé"),
                          *((k, v, X05_OBSERVED[k]) for k, v in X05_REFERENCE.items())),),
        instructions=("Relève l'écart et explique pourquoi l'impression marche alors que l'envoi par courriel échoue.",),
        criteria=(
            _c("Écart", 1, f"{', '.join(X05_DIFF)} : 192.168.5.254 au lieu de 192.168.5.1."),
            _c("Explication", 1, "L'impression vient des postes du même réseau : pas besoin de passerelle ; le serveur de messagerie est sur Internet : il faut la bonne passerelle."),
        ),
        correction=(
            f"Seule la {X05_DIFF[0].lower()} diffère (192.168.5.254 au lieu de 192.168.5.1). Les postes sont dans le même réseau 192.168.5.0/24 que l'imprimante : l'impression ne passe pas par la passerelle. L'envoi vers un serveur de messagerie sur Internet, lui, passe par la passerelle : avec une mauvaise adresse, il échoue. Correction : ressaisir 192.168.5.1 après avoir noté la configuration, puis tester un envoi.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Ce que disent les événements 41 et 6008",
        question_type="long_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Un utilisateur affirme que son PC « redémarre tout seul ». Dans le journal Système, tu trouves à 9 h 12 un "
            "événement Kernel-Power 41 (« Le système a redémarré sans s'arrêter correctement au préalable ») et un "
            "événement EventLog 6008 (« L'arrêt système précédent à 9:08:40 n'était pas prévu »)."
        ),
        instructions=("Explique ce que ces événements prouvent, ce qu'ils ne prouvent pas, et où chercher la cause.",),
        criteria=(
            _c("Ce qu'ils prouvent", 1, "Un arrêt brutal vers 9:08:40 (coupure de courant, blocage, bouton maintenu, arrêt matériel) ; le redémarrage à 9 h 12 est la conséquence."),
            _c("Où chercher", 1, "Événements juste avant 9:08 (erreurs disque, pilote, température), questions à l'utilisateur, alimentation, multiprise, températures : ces deux événements ne donnent pas la cause."),
        ),
        correction=(
            "41 et 6008 prouvent seulement que le système s'est arrêté sans arrêt propre vers 9:08:40 et a redémarré à 9 h 12. Ils ne disent pas pourquoi : coupure de courant, blocage, bouton maintenu ou protection matérielle (surchauffe, alimentation) donnent les mêmes événements.",
            "On cherche la cause avant 9:08 : événements d'erreur précédents (disque, pilote, matériel), récit de l'utilisateur (bouton maintenu ?), alimentation et multiprise, températures. Un événement de conséquence n'est jamais une cause.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Conditions de reproduction d'un écran figé",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TEST,
        context=(
            "Le portable d'une gestionnaire de paie se fige quelques secondes, certains jours. Elle a noté chaque "
            "utilisation pendant une semaine (document 1). Tu dois trouver dans quelles conditions la panne se "
            "produit avant de proposer un test."
        ),
        documents=(_table("Document 1 — Journal de la gestionnaire (support fictif)", X07_HEADER, *X07_ROWS),),
        instructions=("Relève la condition commune aux pannes et propose le test qui reproduit la panne.",),
        criteria=(
            _c("Condition", 1, " ; ".join(f"{n} = {v}" for n, v in X07_FACTORS) + " à chaque blocage, jamais sans ; le logiciel varie."),
            _c("Test", 1, "Travailler sur la station d'accueil puis sans, mêmes logiciels ; ou autre station, autre câble (une variable à la fois) ; pilote ou micrologiciel de la station."),
        ),
        correction=(
            "La station d'accueil est branchée à chaque blocage, jamais quand il n'y en a pas ; le logiciel change (tableur, navigateur, paie) : il n'est pas en cause. Test : reproduire le travail sur la station puis sans elle, puis avec une autre station ou un autre câble, en changeant une seule variable à la fois.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Plan de retour arrière d'une mise à jour de switch",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Le fabricant du switch principal d'une école publie une mise à jour du micrologiciel qui corrige des "
            "coupures. Le switch relie 40 postes, les téléphones et les points d'accès Wi-Fi. Tu prépares "
            "l'intervention."
        ),
        instructions=("Rédige le plan : niveau, impact, moment, état initial, critère d'échec et retour arrière.",),
        criteria=(
            _c("Niveau, impact et moment", 1, "Niveau 5 (mise à jour du firmware) ; tout le bâtiment coupé ; hors des heures de cours, annoncé, accord du responsable."),
            _c("Retour arrière", 1, "Version actuelle notée, configuration exportée et fichier de l'ancienne version conservé ; critère d'échec écrit (switch qui ne redémarre pas, ports ou VLAN absents, coupures) ; réinstaller l'ancienne version et la configuration, vérifier."),
        ),
        correction=(
            "Mise à jour du micrologiciel = niveau 5 : tout le bâtiment est coupé pendant l'opération. On la fait hors des heures de cours (mercredi après-midi, soirée), annoncée, avec l'accord du responsable. État initial : version actuelle notée, configuration exportée, fichier de l'ancienne version téléchargé et gardé.",
            "Critère d'échec écrit avant : switch qui ne redémarre pas, VLAN ou ports manquants, coupures après 15 minutes. Retour : réinstaller l'ancienne version, réimporter la configuration, vérifier postes, téléphones et Wi-Fi.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Suivre l'arbre réseau",
        question_type="short_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TREE,
        context=(
            "Un poste fixe d'un magasin n'a plus accès au réseau. Le voyant de la prise est allumé ; ipconfig donne "
            "192.168.1.23, masque 255.255.255.0 ; le ping de la passerelle 192.168.1.1 échoue (« Impossible de "
            "joindre l'hôte de destination »)."
        ),
        instructions=("Indique la question de l'arbre réseau où tu t'arrêtes, la piste, et deux contrôles à faire.",),
        criteria=(
            _c("Question et piste", 1, f"Question {X09_RESULT[0]} (passerelle) : {X09_RESULT[1]}"),
            _c("Contrôles", 1, "Comparer passerelle et masque saisis au plan d'adressage ; conflit d'adresse (arp -a, journal) ; autre poste vers la passerelle."),
        ),
        correction=(
            f"Lien présent (oui), adresse valide (oui), passerelle muette (non) : arrêt à la question {X09_RESULT[0]}. Piste : {X09_RESULT[1]} Contrôles : ipconfig /all comparé au plan, recherche d'un conflit d'adresse, ping de la passerelle depuis un autre poste (élément commun ou poste).",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Un disque qui claque : preuves et escalade",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Le PC d'une architecte claque à chaque démarrage et Windows n'arrive plus au bureau. Ses projets des "
            "trois derniers mois ne sont pas sauvegardés. Ta société ne fait pas de récupération de données ; un "
            "laboratoire spécialisé travaille avec elle."
        ),
        instructions=("Indique ce que tu arrêtes, ce que tu notes comme preuves, et à qui tu escalades.",),
        criteria=(
            _c("Arrêt et preuves", 1, "Arrêter toute mise sous tension et tout test ou logiciel de réparation ; noter les bruits, les messages, les tentatives déjà faites, l'heure ; aucune écriture sur le disque."),
            _c("Escalade", 1, "Laboratoire de récupération, avec l'accord et le devis de l'architecte ; fiche : symptômes, tests faits, données prioritaires, confidentialité ; contournement : poste de prêt."),
        ),
        correction=(
            "Chaque démarrage peut aggraver un disque mécanique qui claque, et une réparation écrirait dessus : on arrête tout. Preuves : bruits et messages notés, tentatives déjà faites, heure, sans aucune écriture.",
            "Les données ne sont pas sauvegardées et dépassent nos compétences : escalade au laboratoire, avec l'accord écrit et le devis de l'architecte. Fiche : modèle et n° de série, symptômes, tests déjà faits, données prioritaires (projets récents), confidentialité. Contournement : poste de prêt pour continuer à travailler.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS

EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, classements et remises en ordre cohérents,
    exigence du cours citée, nombre d'exercices et de procédures à ordonner demandés par le
    ticket, valeurs calculées."""
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
            errors.append(f"{item.key} : l'exigence AP-15 ou AP-C01 doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue au mini-examen.")
    if len(PRACTICE_ITEMS) < 20 or len(EXAM_ITEMS) != 10:
        errors.append("Ticket #226 : au moins 20 exercices et un mini-examen de 10 questions.")
    kinds = [i.kind for i in PRACTICE_ITEMS]
    if kinds.count(KIND_ORDER) < 8:
        errors.append("Ticket #226 : au moins 8 procédures à ordonner et justifier.")
    if kinds.count(KIND_SCHEMA) != 2 or kinds.count(KIND_TREE) < 2 or kinds.count(KIND_TEST) < 5:
        errors.append("Ticket #226 : schémas à compléter, arbres et tests attendus.")
    if E06_NOT_DISCRIMINANT != ("T4",) or E06_AFTER_T1 != (1, 2) or E06_AFTER_T3 != (1,):
        errors.append("E06 : hypothèses restantes inattendues.")
    if E07_DIFF != ("Masque", "Passerelle") or X05_DIFF != ("Passerelle",):
        errors.append("E07/X05 : écarts de configuration inattendus.")
    if len(E09_FACTORS) != 1 or len(X07_FACTORS) != 1:
        errors.append("E09/X07 : un seul facteur commun attendu.")
    if (E12_RESULT[0], E13_RESULT[0], X09_RESULT[0], E12_RESTARTS) != (3, 4, 3, 3):
        errors.append("E12/E13/X09 : parcours d'arbre inattendu.")
    if X03_VERDICT != CROSS_HOST or len(set(E04_VERDICTS)) != len(CROSS_KINDS):
        errors.append("E04/X03 : conclusions de test croisé inattendues.")
    if [p.level for p in E02_ORDER] != [0, 1, 2, 3, 4, 5] or [p.level for p in E22_ORDER] != [0, 1, 2, 5]:
        errors.append("E02/E22 : ordre d'invasivité inattendu.")
    return errors

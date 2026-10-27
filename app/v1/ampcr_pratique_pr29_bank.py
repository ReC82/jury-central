"""PR29 « Contrôles finaux et rapport professionnel d'intervention » — exercices corrigés et
mini-examen (ticket #228).

Même organisation que PR28 (`app.v1.ampcr_pratique_pr28_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 22 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — **contrôles finaux** (famille de chaque test, contrôles manquants),
  **critères avant / après** (résultat, verdict, critère mesurable), **journal et tests
  reproductibles**, **correction de rapports** (rubriques manquantes, validation abusive,
  données sensibles, évaluation sur la grille), **communication au client**, **retour arrière
  et décision**, **escalade et documentation**, **deux schémas à compléter** (structure du
  rapport, arbre de clôture), un **parcours d'arbre** et des **rédactions** (rapport complet,
  message au client, réserve et limites) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, entreprises et relevés sont **fictifs** ; contrôles exigés, résultats,
verdicts, décisions, défauts de journal, rubriques manquantes, données sensibles, notes de la
grille et pistes de l'arbre viennent des fonctions de `app.v1.ampcr_pratique_pr29_figures`.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr27_figures import walk
from app.v1.ampcr_pratique_pr29_figures import (
    C_BOOT,
    C_DEVERR,
    C_EVENING,
    C_LOSS,
    C_SPEED,
    C_UPDATES,
    C_WIREMAP,
    CHECK_FAMILIES,
    CHECK_NAMES,
    CRITERIA_STATEMENTS,
    D_ESCALATE,
    D_ROLLBACK,
    DECISION_TREE,
    DOC_ITEMS,
    DOC_TARGETS,
    FINAL_STEPS,
    GRID_TOTAL,
    INCONCLUSIVE,
    K_DEVICE,
    K_NET,
    K_OS,
    MEASURABLE,
    MESSAGE_KINDS,
    MESSAGES,
    NOT_MET,
    NOT_TO_WRITE,
    REPORT_BLANK_ANSWERS,
    REPORT_FIELDS,
    REPORT_GRID,
    REPORT_MENTIONS,
    REPORTS_BY_KEY,
    REPRO_FIELDS,
    ROLLBACK_STEPS,
    STATIC_BY_KEY,
    TO_WRITE,
    TREE_BLANK_ANSWERS,
    V_RESERVE,
    VAGUE,
    Criterion,
    JournalEntry,
    Measure,
    decision,
    fmt,
    journal_issues,
    missing_checks,
    missing_report_fields,
    report_score,
    repro_missing,
    required_checks,
    sensitive_lines,
    verdict,
)

PR29_CODE = "PR29"

KIND_CHECK = "contrôles finaux"
KIND_CRIT = "critères avant / après"
KIND_JOURNAL = "journal et tests reproductibles"
KIND_FIX = "correction de rapport"
KIND_COMM = "communication au client"
KIND_ORDER = "procédure à ordonner"
KIND_DECIDE = "décision, retour arrière et escalade"
KIND_SCHEMA = "schéma à compléter"
KIND_TREE = "arbre de décision"
KIND_WRITE = "rédaction"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-16", "AP-C01"})
R_WRITE = ("AP-C01", "AP-16")  # rédiger une réponse de technicien, vocabulaire technique
R_CHECK = ("AP-C01", "AP-15")  # contrôles d'un dépannage
R_DATA = ("AP-C01", "AP-C03")  # confidentialité dans le rapport
R_NET = ("AP-C01", "AP-37")  # contrôles d'un dépannage réseau
R_FULL = ("AP-C01", "AP-16", "AP-15")


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _text_doc(title: str, text: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="texte", content_text=text)


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _names(families) -> str:
    return ", ".join(f.name for f in families)


def _measure_rows(measures: tuple[Measure, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple((m.criterion.text(), fmt(m.before), fmt(m.after)) for m in measures)


def _results_text(measures: tuple[Measure, ...]) -> str:
    return " ; ".join(f"{m.criterion.text()} : {fmt(m.after)} → {m.result}" for m in measures)


def _journal_rows(entries: tuple[JournalEntry, ...]) -> tuple[tuple[str, str, str, str], ...]:
    return tuple((str(n), e.time, e.action, e.result or "—") for n, e in enumerate(entries, start=1))


def _report_rows(fields: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple((f.label, fields[f.key]) for f in REPORT_FIELDS if fields.get(f.key))


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_TESTS: tuple[tuple[str, str], ...] = (
    ("Faire ouvrir à la comptable le fichier qui affichait l'erreur", "fonctionnel"),
    ("Laisser tourner un test de charge de 30 minutes", "stabilite"),
    ("Relever la vitesse de liaison négociée par la carte réseau", "performance"),
    ("ping de la passerelle, puis nslookup d'un nom de site", "reseau"),
    ("Supprimer le compte technique créé pour l'intervention", "securite"),
    ("Gestionnaire de périphériques : aucun point d'exclamation", "pilote"),
    ("Chronométrer le démarrage jusqu'au bureau", "performance"),
    ("Refaire l'impression qui échouait, depuis le logiciel de l'utilisatrice", "fonctionnel"),
    ("Redémarrer trois fois et relire le journal système", "stabilite"),
    ("Vérifier que l'antivirus est actif et à jour", "securite"),
    ("Ouvrir un site web et le dossier partagé du serveur", "reseau"),
    ("Imprimer une page de test et essayer la webcam", "pilote"),
)
_FAMILY_KEYS = tuple(f.key for f in CHECK_FAMILIES)
E01_CORRECT = tuple(_FAMILY_KEYS.index(k) for _t, k in E01_TESTS)

E02_KIND = K_OS
E02_DONE = frozenset({"fonctionnel", "performance", "securite"})
E02_MISSING = missing_checks(E02_KIND, E02_DONE)

E03_MEASURES: tuple[Measure, ...] = (
    Measure(C_BOOT, 150, 75),
    Measure(C_DEVERR, 1, 0),
    Measure(C_UPDATES, 6, 0),
    Measure(Criterion("Espace libre sur le disque système", ">=", 20, "Go"), 3, 41),
)
E03_RESULTS = tuple(m.result for m in E03_MEASURES)
E03_VERDICT = verdict(E03_RESULTS)

E04_CATEGORIES = (MEASURABLE, VAGUE)
E04_CORRECT = tuple(E04_CATEGORIES.index(k) for _t, k in CRITERIA_STATEMENTS)

E05_STEPS = _labels(FINAL_STEPS)

E06_JOURNAL: tuple[JournalEntry, ...] = (
    JournalEntry("14:02", "ipconfig /all sur le poste de l'accueil", "adresse 169.254.3.20, DHCP activé"),
    JournalEntry("14:10", "Cordon remplacé par un cordon testé", "toujours 169.254.3.20"),
    JournalEntry("14:06", "Portable connu bon sur la même prise", "adresse 169.254 aussi"),
    JournalEntry("14:25", "Port 3 du switch redémarré par l'administrateur", "OK"),
    JournalEntry("14:30", "ipconfig /renew", ""),
    JournalEntry("14:35", "ping -n 50 de la passerelle 192.168.1.1", "0 % de pertes"),
)
E06_ISSUES = journal_issues(E06_JOURNAL)

E07_TEST = {"outil": "ping", "obtenu": "ça marche"}
E07_MISSING = repro_missing(E07_TEST)

E08_CATEGORIES = (TO_WRITE, NOT_TO_WRITE)
E08_CORRECT = tuple(E08_CATEGORIES.index(k) for _t, k in REPORT_MENTIONS)

E09_REMOVED = frozenset({"releves", "pieces", "risques", "recommandation"})
E09_FIELDS = {k: v for k, v in REPORTS_BY_KEY["R1"].filled().items() if k not in E09_REMOVED}
E09_MISSING = missing_report_fields(E09_FIELDS)

E10_MEASURES: tuple[Measure, ...] = (
    Measure(C_LOSS, 100, 0),
    Measure(Criterion("Imprimante réseau : page de test", "=", "oui"), "non", "oui"),
    Measure(C_EVENING, None, None),
)
E10_VERDICT = verdict(tuple(m.result for m in E10_MEASURES))

E11_CORRECT = tuple(MESSAGE_KINDS.index(k) for _t, k in MESSAGES)

E13_STEPS = _labels(ROLLBACK_STEPS)

E14_MEASURES: tuple[Measure, ...] = (
    Measure(C_DEVERR, 1, 1),
    Measure(C_BOOT, 48, 45),
    Measure(Criterion("Wi-Fi : connexion au réseau du bureau", "=", "oui"), "oui", "non"),
)
E14_VERDICT = verdict(tuple(m.result for m in E14_MEASURES))
E14_DECISION = decision(E14_VERDICT, rollback_ready=True)
E14_DECISION_NO_POINT = decision(E14_VERDICT, rollback_ready=False)

E17_ANSWERS = (True, True, False)
E17_RESULT = walk(DECISION_TREE, E17_ANSWERS)

E18_KIND = K_DEVICE
E18_CHECKS = required_checks(E18_KIND)
E18_NOTES: tuple[str, ...] = (
    "Demande 2026-1101 du 27/10/2026, secrétariat de l'Institut Saint-Luc (fictif) : « le second écran ne s'allume plus ».",
    "PC INV-0623, bureau du secrétariat ; écran secondaire INV-E-0119, relié en HDMI.",
    "Écran allumé (voyant orange), message « Aucun signal » ; Windows ne détecte qu'un écran.",
    "Post-it collé sur l'écran — mot de passe : Soleil2026",
    "Câble HDMI essayé sur l'écran principal : aucune image ; câble HDMI neuf : image sur l'écran secondaire.",
    "Câble HDMI de 1,5 m remplacé (stock atelier, réf. HDMI-15-02) ; ancien câble jeté au DEEE.",
    "Windows : deux écrans détectés, mode « Étendre », résolution 1920 × 1080 sur les deux.",
    "La secrétaire a déplacé une fenêtre d'un écran à l'autre et ouvert son agenda : OK pour elle.",
    "Le câble passait sous le pied du bureau, écrasé : il risque d'être écrasé à nouveau si le bureau est déplacé.",
)
E18_SENSITIVE = sensitive_lines(E18_NOTES)

E19_REPORT: tuple[tuple[str, str], ...] = (
    ("Équipement", "PC de Mme Renard, mot de passe : Chat-1987 (pour la prochaine fois)"),
    ("Demande", "PC lent"),
    ("Action", "Ajout d'une barrette de 8 Go DDR4 (réf. RAM-8-3200), mémoire totale 16 Go"),
    ("Validation", "C'est beaucoup plus rapide, le client est content."),
    ("Signature", "—"),
)
E19_MARKS: dict[str, float] = {
    "structure": 0.5, "faits": 0, "demarche": 0, "action": 1, "validation": 0, "limites": 0,
    "client": 0.5, "confidentialite": 0,
}
E19_SCORE = report_score(E19_MARKS)
E19_SENSITIVE = sensitive_lines(tuple(text for _l, text in E19_REPORT))

E21_CORRECT = tuple(DOC_TARGETS.index(t) for _i, t in DOC_ITEMS)

# --- Mini-examen -------------------------------------------------------------------------------

X01_KIND = K_NET
X01_DONE = frozenset({"fonctionnel", "reseau"})
X01_MISSING = missing_checks(X01_KIND, X01_DONE)

X02_MEASURES: tuple[Measure, ...] = (
    Measure(C_WIREMAP, "fil 2 coupé", "conforme"),
    Measure(C_SPEED, 100, 1000),
    Measure(C_LOSS, 9, 2),
)
X02_RESULTS = tuple(m.result for m in X02_MEASURES)
X02_VERDICT = verdict(X02_RESULTS)

X03_JOURNAL: tuple[JournalEntry, ...] = (
    JournalEntry("09:00", "Copie des documents sur le disque chiffré n° 4 de l'atelier", "2 310 fichiers, empreintes identiques"),
    JournalEntry("09:40", "Mise à jour du pilote de la carte graphique", "fait"),
    JournalEntry("09:55", "Redémarrage", "écran noir après le logo"),
    JournalEntry("09:50", "Point de restauration créé", "point « avant pilote » créé"),
    JournalEntry("10:05", "Démarrage en mode sans échec, ancien pilote restauré", ""),
)
X03_ISSUES = journal_issues(X03_JOURNAL)

X04_LINES: tuple[str, ...] = (
    "Équipement : portable INV-0302, service RH",
    "Demande : « la messagerie ne s'ouvre plus »",
    "Le mot de passe du client est Rh-2026! (noté pour le retour)",
    "Action : profil de messagerie recréé",
    "J'ai consulté les courriels de l'utilisatrice pour vérifier qu'ils étaient tous là",
    "Validation : messagerie ouverte, courriel test envoyé et reçu",
)
X04_SENSITIVE = sensitive_lines(X04_LINES)
X04_FIELDS = {
    "equipement": X04_LINES[0], "demande": X04_LINES[1], "action": X04_LINES[3], "validation": X04_LINES[5],
}
X04_MISSING = missing_report_fields(X04_FIELDS)

X05_TEST = {"etapes": "imprimer", "obtenu": "OK"}
X05_MISSING = repro_missing(X05_TEST)

X07_MEASURES: tuple[Measure, ...] = (
    Measure(Criterion("Scanner du copieur : envoi vers le dossier Scans", "=", "oui"), "non", "non"),
    Measure(Criterion("Page de test du copieur", "=", "oui"), "oui", "oui"),
)
X07_VERDICT = verdict(tuple(m.result for m in X07_MEASURES))
X07_DECISION = decision(X07_VERDICT, rollback_ready=False)

X08_ANSWERS = (True, False)
X08_RESULT = walk(DECISION_TREE, X08_ANSWERS)

X09_MEASURES: tuple[Measure, ...] = (
    Measure(Criterion("Batterie : autonomie en lecture vidéo", ">=", 4, "h"), 1.5, 5.25),
    Measure(Criterion("Charge jusqu'à 100 %", "<=", 3, "h"), 7, 2.5),
    Measure(Criterion("Arrêts brutaux sur 3 jours d'usage", "<=", 0), 4, None),
)
X09_VERDICT = verdict(tuple(m.result for m in X09_MEASURES))

X10_ITEMS: tuple[tuple[str, str], ...] = (
    ("Référence et n° de série du disque posé", DOC_ITEMS[3][1]),
    ("14:20 — ancien pilote restauré ; impression revenue", DOC_ITEMS[1][1]),
    ("Cause et solution d'une panne qui reviendra sur les dix PC identiques", DOC_ITEMS[2][1]),
    ("Risque résiduel et recommandation datée", DOC_ITEMS[0][1]),
)

_NAMES = ", ".join(CHECK_NAMES)

# =============================================================================================
# 22 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="À quelle famille de contrôle appartient chaque test ?",
        question_type="classification",
        requirement_ids=R_CHECK,
        kind=KIND_CHECK,
        context=(
            "Ton responsable prépare une fiche de contrôles finaux pour les nouveaux techniciens. Il a noté douze "
            "tests faits à la fin d'interventions récentes, dans le désordre. Pour que la fiche soit claire, chaque "
            f"test doit être rangé dans l'une des six familles du cours : {_NAMES}."
        ),
        instructions=("Range chaque test dans sa famille de contrôle.",),
        criteria=(
            _c("Classement", 6, " ; ".join(f"{t} → {CHECK_NAMES[c]}" for (t, _k), c in zip(E01_TESTS, E01_CORRECT, strict=True)) + " (0,5 pt par test)."),
        ),
        correction=(
            "Test fonctionnel : on refait l'action qui échouait, dans les conditions de l'utilisateur (fichier, impression). Stabilité : le résultat tient dans la durée (charge de 30 minutes, redémarrages, journal relu). Performance : une mesure chiffrée comparée à l'avant (démarrage chronométré, vitesse de liaison).",
            "Réseau local et Internet : passerelle, nom, site et ressource partagée. Sécurité : antivirus, compte technique supprimé. Pilote et périphérique : Gestionnaire sans erreur, page de test, webcam essayée.",
        ),
        classification=Classification(categories=CHECK_NAMES, elements=tuple(t for t, _k in E01_TESTS), correct=E01_CORRECT),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Quels contrôles manquent avant de rendre le portable ?",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_CHECK,
        context=(
            "Un stagiaire vient de réinstaller Windows sur le portable d'une agence de voyages (fictive) et veut le "
            "rendre tout de suite à la cliente. Le document 1 est sa fiche de contrôles. Le cours fixe les familles "
            f"exigées pour une « {E02_KIND.lower()} »."
        ),
        documents=(_table("Document 1 — Fiche de contrôles du stagiaire (support fictif)", ("Contrôle fait", "Résultat"),
                          ("Ouverture du logiciel de réservation par la cliente", "réussie"),
                          ("Démarrage chronométré jusqu'au bureau", "38 s (critère : 60 s au plus)"),
                          ("Antivirus actif, mises à jour faites, compte technique supprimé", "oui")),),
        instructions=(
            "Indique les familles de contrôles exigées pour cette intervention.",
            "Nomme celles qui manquent et propose un test concret pour chacune.",
        ),
        criteria=(
            _c("Familles exigées", 1, _names(required_checks(E02_KIND)) + "."),
            _c("Familles manquantes", 2, _names(E02_MISSING) + " (1 pt par famille)."),
            _c("Tests proposés", 1, "Réseau : ping de la passerelle, nslookup, ouverture d'un site et du partage ; pilote : Gestionnaire de périphériques sans erreur, imprimante, webcam ou lecteur de cartes essayés."),
        ),
        correction=(
            f"Après une réinstallation, le cours exige : {_names(required_checks(E02_KIND)).lower()}. Le stagiaire a fait le test fonctionnel, la performance et la sécurité.",
            f"Il manque : {_names(E02_MISSING).lower()}. Une réinstallation remet des pilotes génériques et efface parfois la configuration réseau : on vérifie la passerelle, un nom, un site et un partage, puis le Gestionnaire de périphériques et chaque périphérique utile (imprimante, webcam). Sans ces deux familles, le poste ne peut pas être déclaré prêt.",
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Lire un tableau de critères avant / après",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_CRIT,
        context=(
            "Après le nettoyage d'un PC de bureau très lent chez un notaire (fictif), ta collègue a mesuré les "
            "critères d'acceptation écrits sur la demande, avant et après son intervention. Le document 1 donne "
            "les critères et les valeurs. Elle te demande si elle peut faire signer la réception."
        ),
        documents=(_table("Document 1 — Critères d'acceptation (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(E03_MEASURES)),),
        instructions=(
            "Donne le résultat de chaque critère : atteint, non atteint ou non concluant.",
            "Donne le verdict d'ensemble et dis si elle peut faire signer.",
        ),
        criteria=(
            _c("Résultats", 2, _results_text(E03_MEASURES) + " (0,5 pt par critère)."),
            _c("Verdict", 2, f"{E03_VERDICT} : le démarrage (75 s) dépasse 60 s ; elle ne fait pas signer « réparé », elle poursuit le diagnostic ou revient à l'état initial et en informe le notaire."),
        ),
        correction=(
            "Chaque critère se lit seul : le démarrage passe de 150 s à 75 s, c'est mieux, mais le critère écrit est 60 s au plus : non atteint. Les périphériques en erreur (0), les mises à jour (0) et l'espace libre (41 Go pour 20 Go demandés) sont atteints.",
            "Un seul critère non atteint suffit : le verdict est « non validé ». Une amélioration n'est pas une réparation ; elle ne fait pas signer la réception d'un poste « réparé », elle poursuit le diagnostic (programmes au démarrage, disque) et explique au client où en est la mesure.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Critère mesurable ou critère vague ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_CRIT,
        context=(
            "Avant chaque intervention, l'atelier écrit avec le client les critères qui prouveront la réparation. "
            "Ton responsable a relevé dix critères écrits par l'équipe le mois dernier : certains se vérifient et "
            "s'écrivent dans un rapport, d'autres ne prouvent rien. Tu les tries pour la réunion d'équipe."
        ),
        instructions=("Range chaque critère : mesurable ou vague.",),
        criteria=(
            _c("Tri", 5, " ; ".join(f"{t} → {k}" for t, k in CRITERIA_STATEMENTS) + " (0,5 pt par critère)."),
        ),
        correction=(
            "Un critère mesurable dit quoi mesurer, avec quel outil et quelle valeur attendre : démarrage en 60 s au plus, 0 % de pertes sur 50 paquets, 8 fils conformes au testeur, aucun arrêt en 30 minutes de charge, une tâche précise réussie par la bonne personne.",
            "« Marche mieux », « a l'air rapide », « client content », « devrait fonctionner », « tout est en ordre » ne se vérifient pas : deux personnes peuvent conclure l'inverse. On les remplace par une mesure et une valeur cible.",
        ),
        classification=Classification(categories=E04_CATEGORIES, elements=tuple(t for t, _k in CRITERIA_STATEMENTS), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Les contrôles finaux, dans l'ordre",
        question_type="ordering",
        requirement_ids=R_CHECK,
        kind=KIND_ORDER,
        context=(
            "Tu viens de remplacer le disque d'un PC de bureau dans une mutuelle (fictive) et de restaurer le "
            "système. Le stagiaire qui t'accompagne a noté les six étapes de la clôture sur des cartes, mais elles "
            "sont mélangées. Tu les remets dans l'ordre de la procédure du cours."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Relire les critères → choisir les contrôles → mesurer → comparer → décider → faire constater (0,5 pt par position)."),
        ),
        correction=(
            "On part toujours des critères écrits avant l'intervention, puis on choisit les familles de contrôles exigées pour ce type d'intervention. On mesure ensuite, dans les mêmes conditions que l'avant, et on compare chaque critère.",
            "La décision (valider, revenir en arrière, escalader ou émettre une réserve) vient du verdict. On termine devant le client : il essaie sur sa tâche et signe la réception, ou note sa réserve.",
        ),
        ordering=_shuffled_ordering(E05_STEPS, (3, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Relire un journal des opérations",
        question_type="document_analysis",
        requirement_ids=R_NET,
        kind=KIND_JOURNAL,
        context=(
            "Un collègue a dépanné le poste de l'accueil d'une maison médicale (fictive), qui n'obtenait plus "
            "d'adresse IP. Il te transmet son journal des opérations (document 1) pour que tu rédiges le rapport. "
            "Avant de t'en servir, tu le relis : un journal doit être chronologique et chaque résultat vérifiable."
        ),
        documents=(_table("Document 1 — Journal des opérations (support fictif)", ("Ligne", "Heure", "Opération", "Résultat"),
                          *_journal_rows(E06_JOURNAL)),),
        instructions=(
            "Relève les défauts du journal, ligne par ligne.",
            "Explique pourquoi chacun pose problème pour le rapport et ce qu'il faut demander au collègue.",
        ),
        criteria=(
            _c("Défauts", 3, " ; ".join(E06_ISSUES) + " (1 pt par défaut)."),
            _c("Conséquences", 1, "L'ordre réel des tests est incertain (le test croisé a-t-il eu lieu avant le cordon ?) ; « OK » et un résultat vide ne prouvent rien : demander l'heure exacte, l'effet du redémarrage du port et l'adresse obtenue après le renouvellement."),
        ),
        correction=(
            "Ligne 3 : 14:06 vient après 14:10 : soit l'heure est fausse, soit les lignes sont inversées ; or l'ordre compte (le test croisé du portable montre que la prise ou le port est en cause, pas le cordon).",
            "Ligne 4 : « OK » ne dit pas ce qui a été observé après le redémarrage du port. Ligne 5 : aucun résultat après ipconfig /renew — quelle adresse ? Sans ces faits, le rapport ne peut pas prouver la cause ni la réparation : on demande au collègue les valeurs exactes avant de rédiger.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Rendre un test reproductible",
        question_type="long_answer",
        requirement_ids=R_NET,
        kind=KIND_JOURNAL,
        context=(
            "Dans le rapport d'un dépannage réseau au secrétariat d'une école (fictive), un stagiaire a écrit pour "
            "toute validation : « Test : ping. Résultat : ça marche. » Le poste concerné est le PC INV-0450 ; la "
            "passerelle est 192.168.20.1. Ton responsable veut qu'un collègue puisse refaire ce test à l'identique "
            "la semaine prochaine."
        ),
        instructions=(
            "Indique les rubriques qui manquent pour que le test soit reproductible.",
            "Réécris le test complet, avec un résultat chiffré plausible.",
        ),
        criteria=(
            _c("Rubriques manquantes", 2, ", ".join(E07_MISSING) + " ; et un résultat obtenu chiffré au lieu de « ça marche » (0,5 pt par rubrique)."),
            _c("Test réécrit", 2, "Ex. : PC INV-0450, session de la secrétaire, câblé ; ping -n 50 192.168.20.1 depuis l'invite de commandes ; attendu 0 % de pertes ; obtenu 50 réponses, 0 % de pertes, 2 ms en moyenne ; le 27/10/2026 à 10:15, 1 min."),
        ),
        correction=(
            f"Un test reproductible dit d'où l'on part, avec quoi, comment, ce qu'on attend, ce qu'on obtient et quand. Ici manquent : {', '.join(E07_MISSING).lower()} ; et « ça marche » n'est pas un résultat : il faut la valeur.",
            "Réécriture : « État de départ : PC INV-0450, session de la secrétaire, câble sur la prise S-03. Commande : ping -n 50 192.168.20.1 (passerelle). Attendu : 0 % de pertes. Obtenu : 50 réponses sur 50, 0 % de pertes, 2 ms en moyenne. Le 27/10/2026 à 10:15, durée 1 min. »",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Ce qu'on écrit, ce qu'on n'écrit jamais dans un rapport",
        question_type="classification",
        requirement_ids=R_DATA,
        kind=KIND_FIX,
        context=(
            "Un rapport d'intervention est remis au client, archivé et parfois relu par d'autres personnes. Ton "
            "responsable a relevé dix éléments trouvés dans des rapports de l'équipe ; il te demande de séparer ce "
            "qui doit y figurer de ce qui ne doit jamais y être écrit, pour la confidentialité du client."
        ),
        instructions=("Range chaque élément : à écrire, ou à ne jamais écrire.",),
        criteria=(
            _c("Tri", 5, " ; ".join(f"{t} → {k}" for t, k in REPORT_MENTIONS) + " (0,5 pt par élément)."),
        ),
        correction=(
            "À écrire : l'identité non sensible de l'équipement (n° d'inventaire, modèle), le message exact, les références des pièces posées, les mesures avec leur unité, les risques résiduels.",
            "Jamais : un mot de passe, une clé de récupération, un numéro de carte bancaire, ce qu'on a vu dans les fichiers personnels, un jugement sur l'utilisateur. Un secret écrit dans un rapport archivé est un secret divulgué.",
        ),
        classification=Classification(categories=E08_CATEGORIES, elements=tuple(t for t, _k in REPORT_MENTIONS), correct=E08_CORRECT),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Rubriques manquantes dans un rapport",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_FIX,
        context=(
            "Ton responsable relit le rapport du remplacement d'un bloc d'alimentation dans un bureau d'études "
            "(fictif) avant de l'envoyer au client. Le document 1 en reproduit les rubriques remplies. Il compare "
            "au modèle du cours en quatorze rubriques et te demande de compléter ce qui manque."
        ),
        documents=(_table("Document 1 — Rapport à relire (support fictif)", ("Rubrique", "Contenu"),
                          *_report_rows(E09_FIELDS)),),
        instructions=(
            "Nomme les rubriques absentes du rapport.",
            "Rédige leur contenu à partir des informations du document 1.",
        ),
        criteria=(
            _c("Rubriques absentes", 2, ", ".join(E09_MISSING) + " (0,5 pt par rubrique)."),
            _c("Contenu rédigé", 2, "Relevés : +12 V mesuré au testeur à 11,31 V avant (hors de 11,40 V à 12,60 V), températures en charge ; pièces : bloc 650 W posé (n° de série), ancien bloc vers la filière DEEE ; risques : autres composants d'origine non garantis ; recommandation datée (renouvellement, dépoussiérage)."),
        ),
        correction=(
            f"Il manque : {', '.join(E09_MISSING).lower()}. La validation cite 11,31 V « avant » : c'est un relevé qui doit avoir sa rubrique, avant toute action.",
            "Pièces : référence et n° de série du bloc posé, sort de l'ancien. Risques résiduels : la carte mère et les autres composants ont six ans, rien n'est garanti au-delà du bloc. Recommandation : renouvellement du poste à prévoir, dépoussiérage régulier, avec une échéance. Sans ces rubriques, le client ne sait ni ce qui a été posé ni ce qui reste à surveiller.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="« Validé, panne résolue » : vraiment ?",
        question_type="document_analysis",
        requirement_ids=R_NET,
        kind=KIND_FIX,
        context=(
            "Une imprimante réseau d'un cabinet de kinésithérapie (fictif) se déconnectait « le soir, après 18 h ». "
            "Un collègue est intervenu à 10 h ; il a remis l'imprimante sur une adresse réservée et rédigé la partie "
            "« Résultats et validation » du rapport (document 1). Les mesures sont dans le document 2."
        ),
        documents=(
            _text_doc("Document 1 — Extrait du rapport (support fictif)",
                      "Résultats : l'imprimante perdait son adresse, c'est sûrement la box. Validation : ping de "
                      "l'imprimante sans perte, page de test imprimée. Validé, panne résolue."),
            _table("Document 2 — Mesures (support fictif)", ("Critère", "Avant", "Après"), *_measure_rows(E10_MEASURES)),
        ),
        instructions=(
            "Relève les erreurs de l'extrait (document 1) en t'appuyant sur les mesures (document 2).",
            "Réécris la validation correcte, avec le verdict.",
        ),
        criteria=(
            _c("Erreurs", 2, "« Sûrement la box » est une hypothèse présentée comme un fait ; « panne résolue » alors que la coupure du soir n'a pas été mesurée (non concluant) ; verdict faux."),
            _c("Validation réécrite", 2, f"Ping 0 % de pertes et page de test : atteints ; coupure du soir : non concluant, aucune mesure après 18 h ; verdict : {E10_VERDICT.lower()} ; test complémentaire planifié un soir, client informé."),
        ),
        correction=(
            "Deux fautes de rédaction : une cause supposée (« sûrement la box ») écrite comme un fait, alors qu'elle doit être notée « hypothèse » ; et une conclusion catégorique (« panne résolue ») sans mesure dans les conditions de la panne : le symptôme apparaissait le soir, le test a eu lieu à 10 h.",
            f"Validation correcte : « Ping de l'imprimante : 0 % de pertes ; page de test imprimée. Coupure du soir : non mesurée (intervention à 10 h), résultat non concluant. Verdict : {E10_VERDICT.lower()}. Test de 18 h à 20 h prévu jeudi ; en attendant, noter l'heure de toute coupure. »",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Ce message convient-il au client ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_COMM,
        context=(
            "À la fin de chaque intervention, le technicien explique au client ce qui a été fait. Ton responsable a "
            "relevé neuf phrases dites ou écrites par l'équipe à des clients non informaticiens (secrétariat, "
            "commerce, école) et te demande de les classer avant une formation sur la communication."
        ),
        instructions=("Range chaque phrase : adaptée au client, trop technique, ou inexacte / trompeuse / déplacée.",),
        criteria=(
            _c("Classement", 4.5, " ; ".join(f"{t} → {k}" for t, k in MESSAGES) + " (0,5 pt par phrase)."),
        ),
        correction=(
            "Adaptées : elles disent ce qui n'allait pas, ce qui a été fait et vérifié, en mots simples, et ce qui reste à surveiller (« je repasse jeudi »). Trop techniques : SMART, dd, NVMe, paire 3-6, 100BASE-TX, bail DHCP — exacts, mais inutilisables par le client.",
            "Inexactes ou déplacées : promettre que la panne ne reviendra jamais, dire que le PC est « comme neuf », accuser l'utilisateur. Un technicien ne promet que ce qu'il a mesuré et ne cherche pas de coupable.",
        ),
        classification=Classification(categories=MESSAGE_KINDS, elements=tuple(t for t, _k in MESSAGES), correct=E11_CORRECT),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Traduire une note technique pour le client",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_COMM,
        context=(
            "Tu as remplacé le bloc d'alimentation d'un PC de dessin qui s'éteignait pendant les rendus, au bureau "
            "d'études Trapèze (fictif). Ta note technique dit : « PSU HS : +12 V à 11,31 V hors tolérance ATX, "
            "Kernel-Power 41. Remplacé par un 650 W 80+ ; burn-in 30 min sans shutdown. CM de 6 ans, à renouveler. » "
            "Le gérant, qui n'est pas informaticien, attend ton explication écrite."
        ),
        instructions=("Rédige en quatre à six phrases le message au gérant : ce qui n'allait pas, ce qui a été fait, la preuve, ce qui reste à prévoir.",),
        criteria=(
            _c("Clarté", 2, "Mots simples, sans sigle (alimentation plutôt que PSU, test de 30 minutes plutôt que burn-in) ; ce qui n'allait pas et ce qui a été fait."),
            _c("Exactitude et suite", 2, "Preuve donnée (30 minutes de rendu sans arrêt) ; aucune promesse au-delà de la mesure ; recommandation : PC de six ans, remplacement à prévoir dans l'année."),
        ),
        correction=(
            "Exemple : « Votre ordinateur s'éteignait parce que son alimentation électrique ne fournissait plus assez de courant pendant les gros calculs. Je l'ai remplacée par une alimentation neuve, un peu plus puissante. J'ai ensuite lancé un rendu pendant 30 minutes : aucun arrêt. Le reste de l'ordinateur a six ans : je vous conseille de prévoir son remplacement dans l'année. »",
            "Le message ne contient aucun sigle, dit ce qui a été mesuré (pas « c'est réparé pour toujours ») et donne une recommandation concrète.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Retour arrière après un contrôle en échec",
        question_type="ordering",
        requirement_ids=R_CHECK,
        kind=KIND_ORDER,
        context=(
            "Dans une pharmacie (fictive), tu as mis à jour le pilote de l'imprimante d'étiquettes ; au contrôle "
            "final, les étiquettes sortent décalées et le critère d'échec écrit avant l'intervention est atteint. "
            "Tu avais exporté la configuration et gardé l'ancien pilote. Les six étapes du retour arrière ont été "
            "mélangées sur la fiche du stagiaire."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Constater → prévenir → restaurer → vérifier l'état initial → noter → proposer la suite (0,5 pt par position)."),
        ),
        correction=(
            "On constate d'abord que le critère d'échec est atteint et on arrête de modifier (pas de nouvel essai au hasard). On prévient la pharmacienne (durée annoncée), puis on restaure l'ancien pilote et la configuration exportée.",
            "On vérifie ensuite que l'état initial est bien retrouvé en refaisant les tests du « avant », on note tout au journal, et on propose la suite : autre version du pilote, contact du fabricant. Rien n'est déclaré réparé.",
        ),
        ordering=_shuffled_ordering(E13_STEPS, (2, 4, 0, 5, 1, 3)),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Le nouveau pilote casse le Wi-Fi : que décider ?",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_DECIDE,
        context=(
            "Chez un courtier en assurances (fictif), tu as installé un nouveau pilote de carte Wi-Fi pour corriger "
            "un périphérique en erreur. Tu avais créé un point de restauration « avant pilote ». Le document 1 donne "
            "les mesures avant et après."
        ),
        documents=(_table("Document 1 — Mesures avant / après (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(E14_MEASURES)),),
        instructions=(
            "Donne le résultat de chaque critère et le verdict.",
            "Indique la décision, puis ce qu'elle aurait été sans point de restauration.",
        ),
        criteria=(
            _c("Résultats et verdict", 2, _results_text(E14_MEASURES) + f" ; verdict : {E14_VERDICT.lower()}."),
            _c("Décision", 2, f"{E14_DECISION} (point « avant pilote ») ; sans point de restauration ni ancien pilote : {E14_DECISION_NO_POINT.lower()}."),
        ),
        correction=(
            "Le périphérique reste en erreur (1) et le Wi-Fi, qui marchait, ne se connecte plus : deux critères non atteints ; le démarrage (45 s) est atteint. Verdict : non validé — l'intervention a même créé une régression.",
            f"Le retour arrière a été préparé : on restaure le point « avant pilote », on vérifie que le Wi-Fi revient, on note au journal et on cherche une autre solution. Sans point de restauration ni ancien pilote, on ne bricole pas : {E14_DECISION_NO_POINT.lower()}.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Compléter l'arbre de clôture",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_SCHEMA,
        context=(
            "Pour l'affiche de l'atelier, ton responsable a dessiné l'arbre du cours qui décide si l'on peut clôturer "
            "une intervention. Il a effacé les quatre conduites à tenir quand la réponse est « non » et les a "
            "remplacées par ①, ②, ③ et ④. Le schéma est le document 1."
        ),
        documents=(_schema("pr29-arbre-cloture-a-completer", "Document 1 — Arbre de clôture à compléter"),),
        instructions=("Écris la conduite à tenir en ①, ②, ③ et ④.",),
        criteria=tuple(
            _c(mark, 1, answer) for mark, answer in TREE_BLANK_ANSWERS.items()
        ),
        correction=(
            "① Contrôles exigés non faits : on les fait avant de conclure. ② Critère non atteint : retour arrière s'il a été préparé, sinon escalade avec les relevés ; jamais « réparé ».",
            "③ Mesure manquante : validation avec réserve écrite, test planifié, client informé. ④ Client qui n'a pas constaté ou n'accepte pas : refaire le test devant lui, noter sa réserve. Si tout est « oui » : signature, rapport remis, archivage.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Compléter la structure du rapport",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_SCHEMA,
        context=(
            "Le modèle de rapport du cours compte six parties et quatorze rubriques. Sur le schéma du document 1, "
            "quatre rubriques ont été remplacées par ①, ②, ③ et ④. Le nouveau technicien doit les retrouver avant "
            "de rédiger son premier rapport."
        ),
        documents=(_schema("pr29-structure-rapport-a-completer", "Document 1 — Structure du rapport à compléter"),),
        instructions=("Nomme les rubriques ①, ②, ③ et ④ et dis en une phrase ce qu'on écrit dans chacune.",),
        criteria=tuple(
            _c(mark, 1, f"{label} : " + next(f.content for f in REPORT_FIELDS if f.label == label) + ".")
            for mark, label in REPORT_BLANK_ANSWERS.items()
        ),
        correction=(
            "① Hypothèses (partie Analyse) : les causes possibles, classées, écrites comme des hypothèses. ② Pièces et logiciels (partie Intervention) : la pièce posée avec sa référence et son n° de série, la pièce retirée, la licence.",
            "③ Risques résiduels et limites (partie Validation) : ce qui n'est pas garanti, les résultats non concluants. ④ Signature et accord (partie Suite) : nom, date et signature du client à la réception, ou sa réserve.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Peut-on clôturer ? Suivre l'arbre",
        question_type="short_answer",
        requirement_ids=R_CHECK,
        kind=KIND_TREE,
        context=(
            "Dans une boulangerie (fictive), tu as remplacé le terminal de caisse et son lecteur de codes-barres. "
            "Tous les contrôles exigés sont faits et tous les critères mesurés sont atteints. Mais la clôture de "
            "caisse automatique de 22 h, qui plantait avant, n'a pas pu être testée : tu repars à 16 h."
        ),
        instructions=("Indique où l'arbre de clôture s'arrête et la conduite à tenir.",),
        criteria=(
            _c("Arrêt", 1, f"Question {E17_RESULT[0]} (résultats concluants ? non : la clôture de 22 h n'est pas mesurée)."),
            _c("Conduite", 1, f"{E17_RESULT[1]} Ex. : test de la clôture le soir même par la gérante, ou à distance, résultat noté."),
        ),
        correction=(
            f"Questions 1 et 2 : oui. Question {E17_RESULT[0]} : non, la clôture de 22 h, qui plantait, n'a pas été testée — le résultat est non concluant. Conduite : {E17_RESULT[1].lower()} On écrit la réserve au rapport, on organise le test (la gérante note le résultat de la clôture de ce soir, ou rappel demain matin) et on ne déclare pas la panne résolue avant.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Rédiger le rapport complet à partir des notes",
        question_type="document_analysis",
        requirement_ids=R_FULL + ("AP-C03",),
        kind=KIND_WRITE,
        context=(
            "Tu viens de dépanner l'écran secondaire du secrétariat de l'Institut Saint-Luc (fictif). Tes notes de "
            "terrain sont dans le document 1, dans l'ordre où tu les as prises. Le directeur veut un rapport "
            "d'intervention selon le modèle du cours, qu'il archivera."
        ),
        documents=(_text_doc("Document 1 — Notes de terrain (support fictif)",
                             " / ".join(f"{i}. {line}" for i, line in enumerate(E18_NOTES, start=1))),),
        instructions=(
            "Rédige le rapport rubrique par rubrique, selon le modèle du cours.",
            "Indique la note que tu ne recopies pas et pourquoi.",
        ),
        criteria=(
            _c("Structure et faits", 1.5, "Rubriques dans l'ordre ; équipement par n° d'inventaire (INV-0623, INV-E-0119) ; symptômes exacts (« Aucun signal », un seul écran détecté) ; hypothèses (câble, port, écran, pilote) séparées des résultats."),
            _c("Tests, action, pièces", 1.5, "Test croisé du câble (aucune image sur l'écran principal, image avec un câble neuf) : câble en cause ; câble HDMI 1,5 m remplacé (réf. HDMI-15-02), ancien au DEEE."),
            _c("Validation et suite", 1.5, f"Contrôles d'une « {E18_KIND.lower()} » : {_names(E18_CHECKS).lower()} ; deux écrans détectés en 1920 × 1080, test de la secrétaire sur son agenda ; risque : câble écrasé sous le pied du bureau ; recommandation : passe-câble ou goulotte ; signature."),
            _c("Confidentialité", 0.5, f"Note {E18_SENSITIVE[0][0]} (mot de passe sur un post-it) jamais recopiée ; conseiller oralement de retirer le post-it et de changer le mot de passe."),
        ),
        correction=(
            "Identification : demande 2026-1101 du 27/10/2026 ; PC INV-0623 et écran INV-E-0119, secrétariat. Demande : second écran éteint. Symptômes : écran sous tension, « Aucun signal », un seul écran détecté par Windows. Hypothèses : 1. câble HDMI ; 2. port du PC ; 3. écran ; 4. pilote. Tests : câble suspect sur l'écran principal → aucune image ; câble neuf → image : câble en cause.",
            "Action : câble HDMI 1,5 m remplacé (réf. HDMI-15-02), ancien câble en filière DEEE. Validation : test fonctionnel (deux écrans, mode Étendre, 1920 × 1080), pilote et périphérique (écrans détectés), sécurité (câble rangé hors du passage) ; la secrétaire a utilisé son agenda sur les deux écrans : verdict validé. Risque résiduel : câble écrasé sous le pied du bureau ; recommandation : passe-câble avant tout déplacement du bureau. Signature de la secrétaire ou du directeur.",
            "La note 4 (mot de passe sur un post-it) ne figure jamais dans un rapport : on conseille seulement, de vive voix, de retirer le post-it et de changer le mot de passe.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Noter un rapport avec la grille du cours",
        question_type="document_analysis",
        requirement_ids=R_WRITE + ("AP-C03",),
        kind=KIND_FIX,
        context=(
            "Un stagiaire a ajouté une barrette de mémoire dans un PC lent d'une agence de location (fictive) et a "
            "rédigé le rapport du document 1. Ton responsable te demande de l'évaluer avec la grille du cours sur "
            f"{GRID_TOTAL} (document 2 : critère acquis, partiel ou absent) et de lui dire quoi améliorer."
        ),
        documents=(
            _table("Document 1 — Rapport du stagiaire (support fictif)", ("Rubrique", "Contenu"), *E19_REPORT),
            _table("Document 2 — Grille d'évaluation d'un rapport (cours PR29)", ("Critère", "Points", "Attendu"),
                   *((label, str(points), detail) for _k, label, points, detail in REPORT_GRID)),
        ),
        instructions=(
            "Évalue chaque critère de la grille (acquis, partiel ou absent) et calcule la note sur 20.",
            "Donne les trois corrections les plus urgentes.",
        ),
        criteria=(
            _c("Évaluation", 2, " ; ".join(f"{label} : {'acquis' if E19_MARKS[k] == 1 else 'partiel' if E19_MARKS[k] else 'absent'}" for k, label, _p, _d in REPORT_GRID) + f" ; note {fmt(E19_SCORE)}/20 (à un demi-critère près)."),
            _c("Corrections urgentes", 2, "Retirer le mot de passe (jamais dans un rapport) ; mesurer avant / après (démarrage chronométré, mémoire utilisée) au lieu de « plus rapide » ; compléter les rubriques (symptômes, hypothèses, relevés, tests, risques, recommandation, signature)."),
        ),
        correction=(
            f"Structure partielle (5 rubriques sur 14), faits et démarche absents (« PC lent », aucune mesure ni test), action acquise (barrette, référence, total), validation absente (« beaucoup plus rapide » n'est pas une mesure), limites absentes, communication partielle, confidentialité absente : mot de passe écrit. Note : {fmt(E19_SCORE)}/20.",
            "Urgent : 1. supprimer le mot de passe et prévenir le client de le changer ; 2. mesurer un critère avant / après (démarrage, ouverture du logiciel, mémoire utilisée) ; 3. compléter le modèle, avec la signature du client.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Escalader un contrôle en échec",
        question_type="long_answer",
        requirement_ids=R_NET,
        kind=KIND_DECIDE,
        context=(
            "Au bureau 7 d'une administration communale (fictive), tu as refait la prise murale : le testeur de câble "
            "indique 8 fils conformes, mais le PC reste connecté à 100 Mb/s au lieu de 1 Gb/s, et le port 22 du switch "
            "est réglé par le service informatique central, hors de tes droits. Aucun retour arrière n'est utile (l'ancienne prise "
            "était cassée)."
        ),
        instructions=(
            "Indique le verdict et la décision.",
            "Rédige le message d'escalade au service informatique central.",
        ),
        criteria=(
            _c("Verdict et décision", 1, f"Non validé (vitesse non atteinte) ; pas de retour arrière utile : {D_ESCALATE.lower()}."),
            _c("Message d'escalade", 3, "Demande et poste identifiés (bureau 7, prise, port 22) ; ce qui a été fait (prise refaite) ; relevés : testeur 8 fils conformes, 100 Mb/s mesurés, autre PC sur la même prise ; ce qui est demandé (contrôle du réglage de vitesse du port 22) ; urgence et contact ; client informé."),
        ),
        correction=(
            f"Le critère de vitesse (1000 Mb/s au moins) n'est pas atteint : verdict non validé. Le retour arrière n'a pas de sens (l'ancienne prise était cassée) et le réglage du port est hors de mes droits : {D_ESCALATE.lower()}.",
            "Message : « Bureau 7, prise B7-01, port 22 du switch du 1er étage. Prise refaite ce jour : testeur 8 fils conformes. Le PC INV-0712 et un portable de test se connectent tous deux à 100 Mb/s sur cette prise, 1000 Mb/s sur la prise B7-02 (port 23). Pouvez-vous vérifier le réglage de vitesse du port 22 ? Le poste reste utilisable à 100 Mb/s ; la cheffe de service est informée. Contact : … » Le rapport note la réserve et l'escalade.",
        ),
    ),
    PR06Item(
        key="E21",
        usage=USAGE_PRACTICE,
        title="Où documenter chaque information ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_DECIDE,
        context=(
            "À la fin d'une journée de dépannages dans une PME (fictive), tu dois ranger huit informations au bon "
            "endroit : le rapport remis au client, le journal des opérations de l'atelier, la base de connaissances "
            "de l'équipe ou l'inventaire du parc. Ton responsable vérifiera que chaque information sera retrouvée "
            "par la bonne personne."
        ),
        instructions=("Range chaque information à l'endroit où elle doit être documentée.",),
        criteria=(
            _c("Classement", 4, " ; ".join(f"{t} → {k}" for t, k in DOC_ITEMS) + " (0,5 pt par information)."),
        ),
        correction=(
            "Le rapport sert au client : verdict, risques, recommandation, signature. Le journal sert à l'atelier : chaque opération horodatée avec son résultat, retour arrière compris.",
            "La base de connaissances sert aux collègues : symptôme, cause et solution qui a marché, procédure de contournement. L'inventaire sert au parc : pièce posée avec son n° de série et sa garantie, nouvelle adresse IP, nom du poste.",
        ),
        classification=Classification(categories=DOC_TARGETS, elements=tuple(t for t, _k in DOC_ITEMS), correct=E21_CORRECT),
    ),
    PR06Item(
        key="E22",
        usage=USAGE_PRACTICE,
        title="Écrire une réserve et les limites du résultat",
        question_type="long_answer",
        requirement_ids=R_NET,
        kind=KIND_WRITE,
        context=(
            "Dans la salle de réunion d'une asbl (fictive), le Wi-Fi « coupe pendant les réunions ». Tu as déplacé la "
            "borne et changé de canal : à 14 h, seul dans la salle avec ton portable, le signal est bon et le débit "
            "correct. Les coupures se produisaient avec une vingtaine de personnes connectées, et la prochaine "
            "réunion a lieu lundi."
        ),
        instructions=("Rédige les rubriques « Risques résiduels et limites » et « Recommandation » du rapport.",),
        criteria=(
            _c("Limites", 2, "Ce qui a été mesuré (signal et débit à 14 h, un seul appareil) et ce qui ne l'a pas été (vingt appareils en réunion) : résultat non concluant, validation avec réserve ; ne pas écrire « réparé »."),
            _c("Recommandation", 2, "Test planifié lundi pendant la réunion (nombre d'appareils, coupures, heure) ; consigne en attendant (noter l'heure de toute coupure, appeler) ; escalade si la borne ne supporte pas la charge."),
        ),
        correction=(
            "Limites : « Signal et débit mesurés à 14 h avec un seul portable : corrects. La situation qui provoquait les coupures (une vingtaine d'appareils en réunion) n'a pas pu être reproduite : résultat non concluant, validation avec réserve. »",
            "Recommandation : « Contrôle pendant la réunion de lundi (nombre d'appareils connectés, coupures et heure). En attendant, noter l'heure de toute coupure et me prévenir. Si les coupures persistent, étude de la capacité de la borne et proposition d'une seconde borne. »",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions /20 (« Examen blanc » seulement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Contrôles manquants après un dépannage réseau",
        question_type="document_analysis",
        requirement_ids=R_NET,
        kind=KIND_CHECK,
        context=(
            "Dans une auto-école (fictive), le poste du guichet avait une adresse en 169.254 ; ton collègue a remis "
            "la carte réseau en DHCP et veut partir. Le document 1 donne les contrôles qu'il a faits. Le cours fixe "
            f"les familles exigées pour une « {X01_KIND.lower()} »."
        ),
        documents=(_table("Document 1 — Contrôles faits (support fictif)", ("Contrôle", "Résultat"),
                          ("Le logiciel de planning s'ouvre et affiche les rendez-vous", "oui"),
                          ("ping -n 50 de la passerelle, nslookup d'un nom", "0 % de pertes ; nom résolu")),),
        instructions=("Nomme les familles de contrôles qui manquent et un test concret pour chacune.",),
        criteria=(
            _c("Familles manquantes", 1, _names(X01_MISSING) + "."),
            _c("Tests", 1, "Stabilité : surveillance ou redémarrages, journal relu, bail renouvelé sans coupure ; sécurité : pare-feu actif, réglages d'origine respectés, compte technique supprimé."),
        ),
        correction=(
            f"Exigées pour une configuration réseau : {_names(required_checks(X01_KIND)).lower()}. Il manque {_names(X01_MISSING).lower()} : vérifier que le bail tient (redémarrage, surveillance) et que le poste reste protégé (pare-feu, compte technique supprimé).",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Verdict d'une réparation de câble",
        question_type="document_analysis",
        requirement_ids=R_NET,
        kind=KIND_CRIT,
        context=(
            "Dans un garage (fictif), un stagiaire a refait la fiche RJ45 côté PC du poste de la réception, qui ne "
            "se connectait plus. Il a mesuré les critères d'acceptation de la demande avant et après (document 1) et "
            "veut faire signer la réception."
        ),
        documents=(_table("Document 1 — Critères avant / après (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(X02_MEASURES)),),
        instructions=("Donne le résultat de chaque critère, le verdict et ce que tu réponds au stagiaire.",),
        criteria=(
            _c("Résultats et verdict", 1, _results_text(X02_MEASURES) + f" ; {X02_VERDICT.lower()}."),
            _c("Réponse", 1, "Pas de signature « réparé » : 2 % de pertes restent ; poursuivre le diagnostic (cordon, prise murale, port), le noter au rapport."),
        ),
        correction=(
            f"Testeur conforme et 1000 Mb/s : atteints ; pertes : 2 % pour 0 % exigé : non atteint. {X02_VERDICT}. On ne fait pas signer : il reste un défaut (cordon, prise, port ou carte) à chercher, et le rapport dit où en est la mesure.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Défauts d'un journal des opérations",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_JOURNAL,
        context=(
            "Après la mise à jour du pilote graphique d'un PC de montage vidéo (fictif), ta collègue te transmet son "
            "journal (document 1) pour le rapport. Le PC est reparti avec l'ancien pilote, mais tu dois pouvoir "
            "justifier chaque étape."
        ),
        documents=(_table("Document 1 — Journal des opérations (support fictif)", ("Ligne", "Heure", "Opération", "Résultat"),
                          *_journal_rows(X03_JOURNAL)),),
        instructions=("Relève les défauts du journal et ce qu'ils empêchent de prouver.",),
        criteria=(
            _c("Défauts", 1.5, " ; ".join(X03_ISSUES) + " (0,5 pt par défaut)."),
            _c("Conséquence", 0.5, "Impossible de prouver que le point de restauration existait avant la mise à jour ni que l'état initial a été vérifié après la restauration."),
        ),
        correction=(
            "Ligne 2 : « fait » ne dit pas quelle version a été installée. Ligne 4 : 09:50 avant 09:55 ? Le point de restauration est noté après la mise à jour du pilote (09:40) : a-t-il vraiment été créé avant ? Ligne 5 : aucun résultat après la restauration : l'affichage est-il revenu ? Le rapport ne peut pas affirmer un retour arrière vérifié.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Corriger un rapport : confidentialité et rubriques",
        question_type="document_analysis",
        requirement_ids=R_DATA + ("AP-16",),
        kind=KIND_FIX,
        context=(
            "Dans le service des ressources humaines d'une entreprise (fictive), un collègue a recréé le profil de "
            "messagerie d'une employée. Avant l'envoi du rapport au chef de service, tu le relis (document 1, une "
            "rubrique par ligne)."
        ),
        documents=(_text_doc("Document 1 — Rapport à relire (support fictif)",
                             " / ".join(f"Ligne {i} : {line}" for i, line in enumerate(X04_LINES, start=1))),),
        instructions=(
            "Indique les lignes à supprimer et pourquoi.",
            "Cite quatre rubriques du modèle du cours qui manquent.",
        ),
        criteria=(
            _c("Lignes à supprimer", 1, " ; ".join(f"ligne {n} ({nature})" for n, nature in X04_SENSITIVE) + " : jamais dans un rapport ; la consultation des courriels n'était pas nécessaire."),
            _c("Rubriques manquantes", 1, "Quatre parmi : " + ", ".join(X04_MISSING) + "."),
        ),
        correction=(
            f"À supprimer : ligne {X04_SENSITIVE[0][0]} (mot de passe : un secret ne s'écrit jamais, l'employée doit le changer) et ligne {X04_SENSITIVE[1][0]} (lire les courriels d'autrui est une atteinte à la confidentialité : on vérifie avec l'employée, qui ouvre elle-même sa messagerie).",
            "Manquent notamment : " + ", ".join(X04_MISSING[:6]).lower() + "…",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Réécrire un test pour qu'il soit reproductible",
        question_type="short_answer",
        requirement_ids=R_CHECK,
        kind=KIND_JOURNAL,
        context=(
            "Après avoir réinstallé le pilote de l'imprimante IMP-04 du bureau des ventes d'un grossiste (fictif), un "
            "collègue a écrit dans son rapport : « Étapes : imprimer. Résultat : OK. » L'imprimante est partagée par "
            "le serveur SRV-02 ; les ventes impriment des bons de livraison depuis leur logiciel de gestion."
        ),
        instructions=("Réécris ce test pour qu'un collègue puisse le refaire à l'identique.",),
        criteria=(
            _c("Rubriques", 1, "Présentes : " + ", ".join(REPRO_FIELDS[i][1] for i in (2, 4)) + " (mais vagues) ; à ajouter : " + ", ".join(X05_MISSING) + "."),
            _c("Test réécrit", 1, "Ex. : poste des ventes, session d'un vendeur, IMP-04 via \\\\SRV-02 ; imprimer un bon de livraison depuis le logiciel ; attendu : bon complet, lisible, une page ; obtenu : page imprimée en 8 s ; date et heure."),
        ),
        correction=(
            "Un test reproductible précise l'état de départ, l'outil, les étapes, l'attendu, l'obtenu et le moment. « Imprimer » et « OK » ne suffisent pas. Exemple : « Poste VENTES-02, session d'un vendeur ; imprimante IMP-04 partagée par SRV-02 ; depuis le logiciel de gestion, impression du bon n° test ; attendu : bon d'une page complet et lisible ; obtenu : imprimé en 8 s, conforme ; le 27/10/2026 à 15:20. »",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Expliquer le résultat à une cliente",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_COMM,
        context=(
            "Dans une librairie (fictive), le PC de caisse ne voyait plus Internet. Ta note technique : « Port 4 du "
            "switch en VLAN invités après le passage du prestataire ; port remis en VLAN 10, renew DHCP, ping GW 0 %, "
            "TPE OK. Coupures de 19 h non reproduites. » La libraire n'est pas informaticienne."
        ),
        instructions=("Rédige en quatre à six phrases ton explication à la libraire.",),
        criteria=(
            _c("Clarté et exactitude", 1, "Sans sigle : un réglage de l'armoire réseau avait été modifié, il est corrigé ; Internet et le terminal de paiement fonctionnent (essayés)."),
            _c("Limite et suite", 1, "Les coupures du soir n'ont pas été vues : résultat à confirmer, contrôle prévu ; en attendant, noter l'heure de toute coupure et appeler ; aucune accusation du prestataire."),
        ),
        correction=(
            "Exemple : « Un réglage de votre armoire réseau avait été changé lors d'une intervention précédente : votre caisse se retrouvait sur le réseau des visiteurs. Je l'ai remis en place ; Internet et le terminal de paiement fonctionnent, nous les avons essayés ensemble. Je n'ai pas pu voir les coupures du soir : je repasse jeudi à 19 h pour vérifier. D'ici là, notez l'heure de toute coupure et appelez-moi. »",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Le scanner du copieur ne fonctionne toujours pas",
        question_type="document_analysis",
        requirement_ids=R_CHECK,
        kind=KIND_DECIDE,
        context=(
            "Dans un cabinet d'architectes (fictif), tu as recréé le dossier partagé Scans pour le copieur. Le "
            "copieur est en location : seul le prestataire peut modifier ses réglages. Tu n'avais rien à sauvegarder "
            "côté copieur. Le document 1 donne les mesures."
        ),
        documents=(_table("Document 1 — Critères avant / après (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(X07_MEASURES)),),
        instructions=("Donne le verdict, la décision et ce que tu écris dans le rapport.",),
        criteria=(
            _c("Verdict et décision", 1, f"{X07_VERDICT} ; aucun retour arrière préparé ni utile : {X07_DECISION.lower()}."),
            _c("Rapport", 1, "Dossier Scans recréé et testé depuis un poste ; envoi du copieur toujours en échec ; prestataire contacté (date, n° de ticket) ; client informé ; pas de signature « réparé »."),
        ),
        correction=(
            f"Le critère principal n'est pas atteint : {X07_VERDICT.lower()}. Les réglages du copieur ne sont pas dans tes droits et aucun retour arrière n'a de sens : {X07_DECISION.lower()}. Le rapport dit ce qui a été vérifié de ton côté (partage accessible depuis un poste), ce qui échoue (envoi du copieur) et qui a été contacté.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Clôturer après une mise à jour de firmware",
        question_type="short_answer",
        requirement_ids=R_CHECK,
        kind=KIND_TREE,
        context=(
            "Chez un comptable (fictif), tu as mis à jour le firmware du NAS. Tous les contrôles exigés sont faits ; "
            "mais la sauvegarde nocturne, lancée en test, échoue avec une erreur d'authentification, alors qu'elle "
            "réussissait avant. Tu avais exporté la configuration du NAS."
        ),
        instructions=("Indique où l'arbre de clôture s'arrête, la conduite à tenir et pourquoi.",),
        criteria=(
            _c("Arrêt", 1, f"Question {X08_RESULT[0]} (critères atteints ? non : la sauvegarde échoue)."),
            _c("Conduite", 1, f"{X08_RESULT[1]} Ici, configuration exportée : retour à la configuration, sauvegarde retestée ; firmware non revenable : escalade au fabricant ; client informé."),
        ),
        correction=(
            f"Question 1 : oui. Question {X08_RESULT[0]} : non — un critère (sauvegarde réussie) n'est pas atteint. Conduite : {X08_RESULT[1].lower()} La configuration exportée permet de revenir sur les réglages ; si le firmware lui-même ne peut pas revenir en arrière, on escalade au fabricant avec l'erreur exacte. Un NAS sans sauvegarde fonctionnelle ne se rend pas comme « réparé ».",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Rédiger la validation d'un remplacement de batterie",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Dans une agence de voyages (fictive), tu as remplacé la batterie gonflée d'un portable. Le document 1 "
            "donne les critères mesurés avant et après ; les arrêts brutaux se produisaient « au bout de quelques "
            "jours » et le portable repart aujourd'hui."
        ),
        documents=(_table("Document 1 — Critères avant / après (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(X09_MEASURES)),),
        instructions=("Rédige les rubriques « Validation », « Risques résiduels et limites » et « Recommandation ».",),
        criteria=(
            _c("Validation", 1, _results_text(X09_MEASURES) + f" ; verdict : {X09_VERDICT.lower()}."),
            _c("Limites et recommandation", 1, "Arrêts sur trois jours non observés : réserve écrite ; rappel ou contrôle dans trois jours ; noter tout arrêt ; ancienne batterie dans la filière des piles et batteries."),
        ),
        correction=(
            f"Validation : autonomie 5 h 15 (≥ 4 h) et charge en 2 h 30 (≤ 3 h) : atteints ; arrêts sur trois jours : non mesurés, non concluant. Verdict : {X09_VERDICT.lower()}. Limites : l'absence d'arrêt ne peut pas être prouvée aujourd'hui. Recommandation : contrôle ou appel dans trois jours, noter l'heure de tout arrêt.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Documenter au bon endroit",
        question_type="short_answer",
        requirement_ids=R_WRITE,
        kind=KIND_DECIDE,
        context=(
            "Après une intervention sur l'un des dix PC identiques d'une salle de formation (fictive), tu dois "
            "documenter quatre informations : la référence du disque posé, une ligne horodatée de retour arrière, "
            "la solution d'une panne qui touchera sans doute les neuf autres PC, et le risque résiduel."
        ),
        instructions=("Indique pour chaque information où elle se documente et pourquoi.",),
        criteria=(
            _c("Destinations", 1.5, " ; ".join(f"{t} → {k}" for t, k in X10_ITEMS) + " (environ 0,4 pt par information)."),
            _c("Justification", 0.5, "Chaque document a son lecteur : client (rapport), atelier (journal), collègues (base de connaissances), gestion du parc (inventaire)."),
        ),
        correction=(
            "Référence du disque → inventaire du parc (garantie, suivi de l'équipement). Ligne de retour arrière → journal des opérations (preuve de chaque étape). Solution d'une panne répétitive → base de connaissances (les collègues l'appliqueront aux neuf autres PC). Risque résiduel → rapport remis au client, qui doit le connaître.",
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
            errors.append(f"{item.key} : l'exigence AP-16 ou AP-C01 doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue au mini-examen.")
    if len(PRACTICE_ITEMS) < 18 or len(EXAM_ITEMS) != 10:
        errors.append("Ticket #228 : au moins 18 exercices et un mini-examen de 10 questions.")
    kinds = [i.kind for i in PRACTICE_ITEMS]
    if kinds.count(KIND_SCHEMA) != 2 or kinds.count(KIND_FIX) + kinds.count(KIND_WRITE) + kinds.count(KIND_COMM) < 8:
        errors.append("Ticket #228 : schémas à compléter, corrections de rapports et rédactions attendus.")
    if [f.key for f in E02_MISSING] != ["reseau", "pilote"] or [f.key for f in X01_MISSING] != ["stabilite", "securite"]:
        errors.append("E02/X01 : contrôles manquants inattendus.")
    if E03_RESULTS.count(NOT_MET) != 1 or X02_RESULTS.count(NOT_MET) != 1:
        errors.append("E03/X02 : un seul critère non atteint attendu.")
    if E10_VERDICT != V_RESERVE or X09_VERDICT != V_RESERVE:
        errors.append("E10/X09 : validation avec réserve attendue.")
    if E14_DECISION != D_ROLLBACK or E14_DECISION_NO_POINT != D_ESCALATE or X07_DECISION != D_ESCALATE:
        errors.append("E14/X07 : décisions inattendues.")
    if len(E06_ISSUES) != 3 or len(X03_ISSUES) != 3:
        errors.append("E06/X03 : trois défauts de journal attendus.")
    if [n for n, _k in X04_SENSITIVE] != [3, 5] or [n for n, _k in E18_SENSITIVE] != [4] or not E19_SENSITIVE:
        errors.append("X04/E18/E19 : lignes sensibles inattendues.")
    if (E17_RESULT[0], X08_RESULT[0]) != (3, 2):
        errors.append("E17/X08 : parcours inattendus.")
    if INCONCLUSIVE not in tuple(m.result for m in X09_MEASURES):
        errors.append("X09 : un résultat non concluant attendu.")
    return errors

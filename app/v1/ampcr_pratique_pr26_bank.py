"""PR26 « Analyser une demande d'intervention technique » — exercices corrigés et mini-examen
(ticket #225).

Même organisation que PR25 (`app.v1.ampcr_pratique_pr25_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remise en ordre de la démarche, **qualification** (observation ou
  hypothèse, reproductible ou intermittente, priorité, questions, escalade), **deux schémas à
  compléter** (matrice de priorité, arbre d'escalade, servis en SVG), **analyse de tickets**
  (fiche incomplète, courriel, journal de tickets, inventaire, évaluation d'une fiche avec la
  grille) et **rédaction** (reformulation, questions, critères de réussite, plan et estimation,
  accord du client, fiche d'escalade) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les demandes, personnes, entreprises et numéros sont **fictifs** ; priorités, rubriques
manquantes, décisions d'escalade, estimations et notes de grille des énoncés et des corrigés
viennent des fonctions de `app.v1.ampcr_pratique_pr26_figures`.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr26_figures import (
    ANALYSIS_STEPS,
    AVOID,
    DIRECT,
    E_AUTH,
    E_BUDGET,
    E_DATA,
    E_SECURITY,
    E_SKILL,
    ESCALATE,
    ESCALATION_KINDS,
    EVAL_GRID,
    EVAL_TOTAL,
    FIELDS_BY_KEY,
    HIGH,
    HYPOTHESIS,
    INTERMITTENT,
    LOW,
    MATRIX_BLANK_ANSWERS,
    MEDIUM,
    OBSERVATION,
    OCCURRENCE_KINDS,
    OCCURRENCES,
    PRIORITIES,
    PRIORITY_DELAYS,
    PRIORITY_LABELS,
    QUESTION_KINDS,
    QUESTIONS,
    REPRODUCIBLE,
    STATEMENT_KINDS,
    STATEMENTS,
    STATIC_BY_KEY,
    TREE_BLANK_ANSWERS,
    USEFUL,
    VAGUE_CRITERIA,
    Situation,
    escalation,
    estimate,
    fr,
    grid_score,
    hm,
    missing_fields,
    only,
    priority,
)

PR26_CODE = "PR26"

KIND_ORDER = "ordonnancement"
KIND_QUALIF = "qualification"
KIND_TICKET = "analyse de tickets"
KIND_WRITE = "rédaction"
KIND_SCHEMA = "schéma à compléter"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-16", "AP-C01"})
R_WRITE = ("AP-16", "AP-C01")
R_DATA = ("AP-16", "AP-C01", "AP-C03")  # protection des données du client
R_DIAG = ("AP-16", "AP-C01", "AP-15")  # dépannage des dysfonctionnements courants


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _text_doc(title: str, text: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="texte", content_text=text)


def _label(key: str) -> str:
    return FIELDS_BY_KEY[key].label


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(ANALYSIS_STEPS)

E02_CASES = STATEMENTS[:8]
E02_CORRECT = tuple(STATEMENT_KINDS.index(k) for _t, k in E02_CASES)

E03_CASES = OCCURRENCES
E03_CORRECT = tuple(OCCURRENCE_KINDS.index(k) for _t, k in E03_CASES)

E04_CASES: tuple[tuple[str, int, int], ...] = (
    ("Le serveur de fichiers ne répond plus : toute l'entreprise est arrêtée, 9 h un lundi", HIGH, HIGH),
    ("La caisse principale d'une boulangerie refuse les cartes un samedi à 10 h ; une seconde caisse fonctionne", MEDIUM, HIGH),
    ("Un stagiaire voudrait un second écran « quand vous aurez le temps »", LOW, LOW),
    ("Le copieur partagé du service RH bourre ; un autre copieur est à l'étage, aucune échéance aujourd'hui", MEDIUM, LOW),
    ("Toute la messagerie de l'entreprise est lente, mais les messages partent ; pas d'échéance", HIGH, LOW),
    ("La comptable seule ne peut plus imprimer ; elle doit sortir la paie dans l'heure, aucune autre imprimante", LOW, HIGH),
    ("Les cinq postes de l'accueil perdent Internet ; les clients attendent au guichet", HIGH, HIGH),
)
E04_PRIORITIES = tuple(priority(i, u) for _t, i, u in E04_CASES)
E04_CATEGORIES = tuple(PRIORITY_LABELS[p] for p in PRIORITIES)
E04_CORRECT = tuple(PRIORITIES.index(p) for p in E04_PRIORITIES)

E05_CASES = QUESTIONS
E05_CORRECT = tuple(QUESTION_KINDS.index(k) for _q, k, _w in E05_CASES)

E06_CASES: tuple[tuple[str, Situation], ...] = (
    ("Remplacer le câble réseau débranché d'un poste de l'accueil", Situation()),
    ("Le client te demande le mot de passe de la messagerie de son collègue absent", only(E_AUTH)),
    ("Un antivirus signale un rançongiciel en cours de chiffrement sur le poste", only(E_SECURITY)),
    ("Le disque d'un portable claque et le client n'a aucune copie de ses photos de chantier", only(E_DATA)),
    ("Réinstaller le pilote d'imprimante d'un poste, accord du client noté", Situation()),
    ("Le portable sous garantie a l'écran fissuré ; le fabricant interdit l'ouverture", only(E_SKILL)),
    ("Le nettoyage prévu en 1 h révèle qu'il faut remplacer la carte mère (pièce à 180 €)", only(E_BUDGET)),
)
E06_TARGETS = tuple(escalation(s) for _t, s in E06_CASES)
E06_CORRECT = tuple(ESCALATION_KINDS.index(DIRECT if k is None else ESCALATE) for k in E06_TARGETS)

E07_ANSWERS = MATRIX_BLANK_ANSWERS
E08_ANSWERS = TREE_BLANK_ANSWERS

# E09 : fiche d'incident incomplète
E09_FICHE: dict[str, str] = {
    "numero": "INT-2610-061",
    "date": "Mardi, 8 h 50",
    "demandeur": "L. Martin, logistique",
    "inventaire": "",
    "emplacement": "Entrepôt, bureau du quai",
    "contexte": "Windows 11, logiciel de gestion de stock",
    "symptomes": "Le PC est « bizarre »",
    "apparition": "",
    "changements": "",
    "utilisateurs": "Une personne",
    "impact": "Faible",
    "urgence": "Moyenne",
    "priorite": "P4 basse",
    "sauvegarde": "",
    "confidentialite": "Pas de données personnelles",
    "autorisation": "",
    "reformulation": "",
    "criteres": "Le PC marche",
    "plan": "Voir sur place",
    "escalade": "Non",
}
E09_MISSING = missing_fields(E09_FICHE)

# E12 : ticket du centre de services à qualifier
E12_IMPACT, E12_URGENCY = MEDIUM, HIGH
E12_PRIORITY = priority(E12_IMPACT, E12_URGENCY)

# E14 : plan d'action et estimation
E14_TASKS: tuple[tuple[str, int], ...] = (
    ("Sauvegarder les documents de l'utilisatrice sur le NAS", 30),
    ("Remplacer le disque dur par un SSD", 25),
    ("Installer Windows 11 et les mises à jour", 60),
    ("Installer suite bureautique et logiciel métier", 30),
    ("Restaurer les documents et contrôler avec l'utilisatrice", 20),
)
E14_SUM = sum(m for _t, m in E14_TASKS)
E14_ESTIMATE = estimate(tuple(m for _t, m in E14_TASKS))

# E16 : journal de tickets d'une semaine
E16_ROWS: tuple[tuple[str, ...], ...] = (
    ("T-101", "Lundi 9 h 10", "Accueil", "Souris sans fil qui ne répond plus", "PC-ACC-01"),
    ("T-102", "Lundi 9 h 30", "Comptabilité", "Logiciel de facturation : « licence introuvable »", "PC-COMPTA-01"),
    ("T-103", "Lundi 10 h 05", "Comptabilité", "Facturation : « licence introuvable » au démarrage du logiciel", "PC-COMPTA-02"),
    ("T-104", "Mardi 14 h 00", "Direction", "Demande d'un second écran", "PC-DIR-01"),
    ("T-105", "Mardi 15 h 20", "Ventes", "Facturation : « licence introuvable », impossible de facturer", "PC-VEN-03"),
    ("T-106", "Mercredi 8 h 45", "Accueil", "Imprimante : bourrage papier", "IMP-01"),
)
E16_LINKED = ("T-102", "T-103", "T-105")
E16_IMPACT, E16_URGENCY = HIGH, MEDIUM
E16_PRIORITY = priority(E16_IMPACT, E16_URGENCY)

# E19 : grille d'évaluation appliquée à la fiche d'un collègue
E19_MARKS: dict[str, float] = {
    "identification": 1, "symptomes": 0.5, "contexte": 1, "frequence": 0, "priorite": 0.5,
    "donnees": 0, "criteres": 0.5, "plan": 1, "escalade": 1,
}
E19_SCORE = grid_score(E19_MARKS)

# E20 : journal d'une panne intermittente
E20_ROWS: tuple[tuple[str, ...], ...] = (
    ("Lundi", "11 h 52", "redémarrage sans message", "gravure de 4 Go en cours"),
    ("Mardi", "9 h 15", "aucun incident", "travail de bureau"),
    ("Mercredi", "15 h 30", "redémarrage sans message", "export vidéo en cours"),
    ("Jeudi", "10 h 00", "aucun incident", "travail de bureau"),
    ("Vendredi", "14 h 05", "redémarrage sans message", "export vidéo en cours"),
)

# --- Mini-examen -------------------------------------------------------------------------------

X03_IMPACT, X03_URGENCY = HIGH, MEDIUM
X03_PRIORITY = priority(X03_IMPACT, X03_URGENCY)
X04_FICHE: dict[str, str] = {
    **{k: "renseigné" for k in E09_FICHE},
    "changements": "",
    "utilisateurs": "",
    "sauvegarde": "",
    "criteres": "",
}
X04_MISSING = missing_fields(X04_FICHE)
X05_SITUATION = Situation(securite=False, donnees=False)
X05_TARGET = escalation(X05_SITUATION)
X08_TASKS: tuple[tuple[str, int], ...] = (
    ("Sauvegarder la configuration du switch", 10),
    ("Remplacer le switch et recâbler 12 postes", 50),
    ("Tester chaque poste et l'imprimante", 30),
)
X08_ESTIMATE = estimate(tuple(m for _t, m in X08_TASKS))

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'analyse d'une demande",
        question_type="ordering",
        requirement_ids=R_WRITE,
        kind=KIND_ORDER,
        context=(
            "Tu débutes au service informatique d'une PME de quarante personnes. Ton responsable te remet ses notes "
            "sur la façon de traiter une demande d'intervention, mais les neuf étapes sont mélangées. Tu dois les "
            "remettre dans l'ordre pour en faire la procédure affichée au bureau."
        ),
        instructions=("Remets les neuf étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4.5, "Recueillir → identifier → questionner → qualifier → prioriser → protéger → reformuler → planifier → décider (0,5 pt par étape)."),
        ),
        correction=(
            "1. On note la demande telle qu'elle est dite, avec la date et le contact. 2. On identifie l'appareil (n° d'inventaire, emplacement, système, réseau). 3. On questionne : questions ouvertes puis fermées. 4. On qualifie : observations séparées des hypothèses, panne reproductible ou intermittente.",
            "5. On évalue impact et urgence, et on lit la priorité dans la matrice. 6. On protège : sauvegarde, confidentialité, risques annoncés, accord écrit. 7. On reformule la demande et les critères de réussite, et on les fait valider. 8. On planifie les étapes, la durée et le coût. 9. On décide : intervenir ou escalader. Qualifier avant de prioriser évite de classer une demande sur un simple avis (« c'est la carte mère »).",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (5, 2, 8, 0, 6, 3, 1, 7, 4)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Observation ou hypothèse ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Au téléphone et par courriel, plusieurs utilisateurs décrivent leur problème. Avant de remplir la "
            "rubrique « Symptômes observés » de la fiche d'incident, tu tries leurs phrases : ce qui est un fait "
            "constaté (on peut le vérifier) et ce qui est une cause supposée ou un avis."
        ),
        instructions=("Range chaque phrase : observation ou hypothèse (interprétation).",),
        criteria=(
            _c("Classement", 4, "Observations : aucun voyant ni ventilateur ; « Imprimante hors ligne » depuis lundi ; trois collègues n'ouvrent plus le dossier ; session en 6 min contre 1 min. Hypothèses : l'alimentation a grillé ; le réseau est en panne ; un virus ; le Wi-Fi est trop faible (0,5 pt par phrase)."),
        ),
        correction=(
            "Une observation décrit ce que l'on voit, entend ou mesure : un voyant éteint, un message exact, un nombre de personnes touchées, une durée mesurée. Elle se vérifie sur place et va dans la rubrique « Symptômes ».",
            "« L'alimentation a grillé », « le réseau est en panne », « un virus », « le Wi-Fi est trop faible » sont des causes supposées : on les note comme hypothèses du demandeur, puis on les teste. Recopier un avis comme symptôme oriente tout le diagnostic dans une seule direction, parfois fausse.",
        ),
        classification=Classification(categories=STATEMENT_KINDS, elements=tuple(t for t, _k in E02_CASES), correct=E02_CORRECT),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Panne reproductible ou intermittente ?",
        question_type="classification",
        requirement_ids=R_DIAG,
        kind=KIND_QUALIF,
        context=(
            "La rubrique « Date d'apparition et fréquence » de la fiche demande de préciser si la panne se reproduit "
            "à chaque essai dans les mêmes conditions, ou seulement de temps en temps. Tu relis sept demandes de la "
            "semaine pour compléter cette rubrique."
        ),
        instructions=("Range chaque description : panne reproductible ou panne intermittente.",),
        criteria=(
            _c("Classement", 3.5, "Reproductibles : « No bootable device » à chaque démarrage ; page 2 toujours absente ; accès refusé à Julie à chaque tentative ; écran noir sur le port de gauche. Intermittentes : redémarrages 2-3 fois par semaine ; Wi-Fi qui coupe certains jours ; « bourrage » une fois sur vingt (0,5 pt par élément)."),
        ),
        correction=(
            "Une panne reproductible apparaît à chaque essai dans les mêmes conditions : on peut la montrer, la tester et vérifier sa disparition tout de suite. L'écran noir « toujours à gauche, jamais à droite » est reproductible : la condition (le port) est connue.",
            "Une panne intermittente apparaît de temps en temps : on ne peut pas la provoquer à la demande. On la rend observable avec un journal (date, heure, ce qui était en cours) pour trouver ce qui la déclenche ; le critère de réussite porte alors sur une durée sans incident.",
        ),
        classification=Classification(categories=OCCURRENCE_KINDS, elements=tuple(t for t, _k in E03_CASES), correct=E03_CORRECT),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Quelle priorité pour chaque demande ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Tu tiens seul le centre de services d'un petit groupe d'entreprises. Sept demandes arrivent. Applique "
            "la matrice du cours : impact élevé, moyen ou faible ; urgence élevée, moyenne ou faible ; "
            "1+1 → P1, 1+2 → P2, 1+3 ou 2+2 → P3, au-delà → P4 (1 = élevé)."
        ),
        instructions=("Attribue une priorité à chaque demande.",),
        criteria=(
            _c("Priorités", 3.5, "Serveur arrêté → P1 ; caisse principale → P2 ; second écran → P4 ; copieur RH → P4 ; messagerie lente → P3 ; paie dans l'heure → P3 ; accueil sans Internet → P1 (0,5 pt par demande)."),
        ),
        correction=(
            "Serveur arrêté : impact élevé (toute l'entreprise) × urgence élevée = P1. Accueil sans Internet, clients au guichet : élevé × élevée = P1. Caisse principale : impact moyen (une seconde caisse permet de continuer) × urgence élevée (samedi matin) = P2.",
            "Messagerie lente pour tous mais qui fonctionne : élevé × faible = P3. Paie dans l'heure pour une seule personne : faible × élevée = P3 — l'échéance relève la priorité d'une demande individuelle. Copieur RH avec contournement : moyen × faible = P4 ; second écran : faible × faible = P4.",
        ),
        classification=Classification(categories=E04_CATEGORIES, elements=tuple(t for t, _i, _u in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Question utile ou question à éviter ?",
        question_type="classification",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Un collègue prépare la liste des questions qu'il pose au téléphone quand un utilisateur appelle. Tu "
            "relis sa liste : certaines questions font avancer l'analyse, d'autres bloquent l'échange (accusation, "
            "jargon, réponse imposée)."
        ),
        instructions=("Range chaque question : utile ou à éviter.",),
        criteria=(
            _c("Classement", 4, "Utiles : depuis quand ; message exact ; ce qui a changé ; d'autres collègues ; à chaque fois ou de temps en temps. À éviter : pièce jointe douteuse (accusation) ; serveur DHCP (jargon) ; « c'est le disque dur » (question orientée) (0,5 pt par question)."),
        ),
        correction=(
            "Les questions utiles recueillent des faits : date d'apparition, mots exacts du message, changements récents, étendue (un poste ou plusieurs), fréquence. L'utilisateur peut y répondre sans connaissance technique.",
            "Une question accusatrice ferme l'échange ; une question en jargon (DHCP) n'obtient pas de réponse fiable ; une question orientée (« c'est le disque, n'est-ce pas ? ») fait confirmer ta propre hypothèse. On commence par des questions ouvertes, puis on précise par des questions fermées.",
        ),
        classification=Classification(categories=QUESTION_KINDS, elements=tuple(q for q, _k, _w in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Traiter directement ou escalader ?",
        question_type="classification",
        requirement_ids=R_DATA,
        kind=KIND_QUALIF,
        context=(
            "Tu es technicien de premier niveau dans une société de maintenance. Ton rôle : intervenir sur les "
            "postes avec l'accord du client, sans droits sur les serveurs ni pouvoir d'achat. Sept situations se "
            "présentent dans la journée ; pour chacune, décide si tu la traites ou si tu dois arrêter et escalader."
        ),
        instructions=("Range chaque situation : traiter directement ou arrêter et escalader.",),
        criteria=(
            _c("Décisions", 3.5, "Directement : câble réseau ; pilote d'imprimante avec accord. Escalader : mot de passe d'un collègue (autorisation) ; rançongiciel (sécurité) ; disque qui claque sans copie (données) ; portable sous garantie (fabricant) ; carte mère à 180 € (nouvelle estimation) (0,5 pt par situation)."),
        ),
        correction=(
            "Le câble et le pilote restent dans ton rôle, sans risque pour les données : tu interviens. Le mot de passe d'un autre compte ne se donne jamais : le responsable décide, selon la procédure de l'entreprise. Un rançongiciel actif : on isole le poste (câble débranché, Wi-Fi coupé), on n'efface rien et on prévient le responsable sécurité.",
            "Disque qui claque sans copie : chaque mise sous tension peut aggraver les dégâts ; on arrête et on propose un spécialiste en récupération. Portable sous garantie : l'ouvrir annulerait la garantie ; on passe par le fabricant. Pièce à 180 € hors estimation : on suspend et on présente un nouveau devis au client avant de continuer.",
        ),
        classification=Classification(categories=ESCALATION_KINDS, elements=tuple(t for t, _s in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : la matrice de priorité",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_SCHEMA,
        context=(
            "Le gérant d'une agence de voyages veut afficher la matrice de priorité près du téléphone du support. "
            "Quatre cases ont été effacées sur la version imprimée. Le document 1 est la matrice à terminer : "
            "lignes = impact, colonnes = urgence."
        ),
        documents=(_schema("pr26-matrice-a-completer", "Document 1 — Matrice de priorité à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Donne pour la case ① le délai de prise en charge et un exemple de demande de l'agence.",
        ),
        criteria=(
            _c("Cases", 2, " ; ".join(f"{k} {v}" for k, v in E07_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Délai et exemple", 1, f"① = P2 : {PRIORITY_DELAYS['P2']} ; exemple : la réservation en ligne est lente pour toute l'agence, mais on peut encore réserver par téléphone (impact élevé, urgence moyenne)."),
        ),
        correction=(
            "① impact élevé × urgence moyenne = P2 haute. ② impact moyen × urgence moyenne = P3 normale. ③ impact faible × urgence élevée = P3 normale : une seule personne, mais une échéance immédiate. ④ impact moyen × urgence faible = P4 basse.",
            "La P2 se prend en charge dans les 2 heures. Exemple : tout le système de réservation est lent pour toute l'agence (impact élevé), mais on peut encore réserver par téléphone (urgence moyenne). La matrice est symétrique : une forte urgence compense un faible impact, et inversement.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : l'arbre d'escalade",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_SCHEMA,
        context=(
            "Ta responsable a dessiné l'arbre que chaque technicien doit suivre avant d'agir sur un poste : cinq "
            "contrôles, du plus grave au moins grave. Les actions de quatre cases « si non » ont été effacées. Le "
            "document 1 est l'arbre à terminer."
        ),
        documents=(_schema("pr26-escalade-a-completer", "Document 1 — Arbre d'escalade à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④ (action à mener quand le contrôle échoue).",
            "Explique pourquoi le contrôle de sécurité vient en premier.",
        ),
        criteria=(
            _c("Actions", 2, "① isoler, ne rien effacer, responsable sécurité ; ② responsable (serveur, droits, compte d'autrui, achat) ; ③ arrêter, sauvegarder d'abord ou spécialiste en récupération ; ④ suspendre et présenter une nouvelle estimation (0,5 pt chacune)."),
            _c("Ordre", 1, "Un incident de sécurité s'étend pendant qu'on travaille (chiffrement, fuite, autres postes) : on l'arrête avant toute autre décision, et on garde les traces."),
        ),
        correction=(
            f"① {E08_ANSWERS['①']} ② {E08_ANSWERS['②']} ③ {E08_ANSWERS['③']} ④ {E08_ANSWERS['④']}",
            "La sécurité passe en premier parce qu'un virus ou une intrusion continue d'agir : chaque minute peut toucher d'autres postes ou d'autres données. On isole d'abord, puis on décide. Les autres contrôles protègent l'autorisation, les données, la qualité et le budget de l'intervention.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Analyser une fiche d'incident incomplète",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_TICKET,
        context=(
            "Un collègue part en congé et te transmet la fiche INT-2610-061 qu'il a ouverte pour le poste du bureau "
            "du quai de l'entrepôt. Avant de te déplacer, tu relis la fiche (document 1) pour savoir ce qu'il faut "
            "encore demander à l'utilisateur."
        ),
        documents=(_table("Document 1 — Fiche INT-2610-061 (support fictif)", ("Rubrique", "Contenu"),
                          *((_label(k), v or "—") for k, v in E09_FICHE.items())),),
        instructions=(
            "Relève les rubriques obligatoires vides.",
            "Relève deux rubriques remplies mais inutilisables et réécris-les sous forme de question à poser.",
        ),
        criteria=(
            _c("Rubriques vides", 3, " ; ".join(_label(k) for k in E09_MISSING) + " (0,5 pt chacune)."),
            _c("Rubriques inutilisables", 2, "« Le PC est bizarre » : quel message ou quel comportement exact voyez-vous ? « Le PC marche » : quel test prouvera que c'est réparé ? (ou « Voir sur place » : quelles étapes et quelle durée ?)."),
        ),
        correction=(
            f"Rubriques obligatoires vides ({len(E09_MISSING)}) : " + ", ".join(_label(k).lower() for k in E09_MISSING) + ". Sans numéro d'inventaire, on risque d'intervenir sur le mauvais appareil ; sans sauvegarde ni autorisation, on ne peut rien entreprendre de risqué.",
            "« Bizarre » est un avis, pas une observation : on demande le message exact, depuis quand, à chaque fois ou parfois. « Le PC marche » n'est pas vérifiable : on écrit un test (le logiciel de stock s'ouvre et enregistre une sortie). « Voir sur place » n'est pas un plan : on note les premières étapes et une estimation.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Reformuler une demande confuse",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Le gérant d'une menuiserie te laisse un message vocal un mercredi après-midi. Tu dois le reformuler "
            "en deux ou trois phrases pour la rubrique « Reformulation » de la fiche, puis le rappeler pour la "
            "faire valider. Le document 1 est la transcription du message."
        ),
        documents=(_text_doc(
            "Document 1 — Message vocal (transcription, support fictif)",
            "« Oui bonjour, c'est Delvaux de la menuiserie. Bon, l'ordinateur du bureau, celui où on fait les devis, "
            "depuis lundi il fait n'importe quoi, je crois que c'est Windows qui a encore fait une mise à jour. "
            "Quand j'ouvre le logiciel de devis il se ferme tout seul au bout de deux secondes, à chaque fois. Le "
            "reste ça va, Internet ça va. J'ai trois devis à envoyer avant vendredi. Rappelez-moi au 0470 00 00 00. »",
        ),),
        instructions=(
            "Rédige la reformulation pour la fiche.",
            "Écris la phrase par laquelle tu la fais valider au téléphone.",
            "Indique ce qui est une hypothèse du gérant et où tu la notes.",
        ),
        criteria=(
            _c("Reformulation", 2, "Depuis lundi, sur le PC des devis, le logiciel de devis se ferme seul environ deux secondes après son ouverture, à chaque essai ; le reste fonctionne ; trois devis à envoyer avant vendredi."),
            _c("Validation", 1, "« Si je résume bien : … Est-ce exact ? Ai-je oublié quelque chose ? »"),
            _c("Hypothèse", 1, "« Une mise à jour de Windows » est une hypothèse du demandeur : notée dans les hypothèses (ou la rubrique Changements récents à vérifier), pas dans les symptômes."),
        ),
        correction=(
            "Reformulation : « Depuis lundi, sur le PC des devis du bureau, le logiciel de devis se ferme seul environ deux secondes après son lancement, à chaque essai. Les autres logiciels et Internet fonctionnent. Trois devis doivent partir avant vendredi. »",
            "Au téléphone : « Monsieur Delvaux, si je résume bien : … Est-ce bien cela ? Y a-t-il autre chose ? » La mise à jour de Windows est une piste à vérifier (historique des mises à jour) : on la note comme hypothèse, pas comme symptôme. La reformulation garde les faits : quoi, depuis quand, à quelle fréquence, l'enjeu.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Analyser le courriel d'un client",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TICKET,
        context=(
            "Une cliente, architecte indépendante, envoie un courriel au support de ta société de maintenance. "
            "Tu ouvres la fiche d'incident : il faut remplir les rubriques Symptômes, Changements récents et "
            "Utilisateurs touchés, et lister les hypothèses à tester. Le document 1 est le courriel."
        ),
        documents=(_text_doc(
            "Document 1 — Courriel reçu le jeudi à 8 h 12 (support fictif)",
            "« Bonjour, mon traceur est encore en panne, je pense que le câble est mort ou que c'est le pilote. "
            "Hier soir j'ai lancé un plan A1 : la feuille est sortie à moitié imprimée, et le voyant orange "
            "clignote depuis. Mon stagiaire a déplacé le traceur mardi pour faire de la place. Je suis seule à "
            "l'utiliser. Je dois remettre ces plans au client demain à 10 h. Cordialement, Claire Noël. »",
        ),),
        instructions=(
            "Rédige les rubriques Symptômes, Changements récents et Utilisateurs touchés.",
            "Liste les hypothèses (celles de la cliente et la tienne), de la plus simple à vérifier à la plus lourde.",
            "Donne la priorité avec la matrice du cours.",
        ),
        criteria=(
            _c("Rubriques", 2, "Symptômes : un plan A1 sorti à moitié imprimé hier soir, voyant orange qui clignote depuis. Changements : traceur déplacé mardi. Utilisateurs : une personne."),
            _c("Hypothèses", 1, "Câble déplacé ou mal rebranché (déplacement), rouleau ou papier mal engagé, erreur signalée par le voyant (manuel), pilote — de la vérification la plus simple à la plus lourde."),
            _c("Priorité", 1, f"Impact faible (une personne) × urgence élevée (remise demain 10 h) = {PRIORITY_LABELS[priority(LOW, HIGH)]}."),
        ),
        correction=(
            "Symptômes (faits) : « un plan A1 sorti à moitié imprimé mercredi soir ; voyant orange clignotant depuis ». Changements récents : « traceur déplacé mardi par le stagiaire ». Utilisateurs touchés : « une seule personne ». « Le câble est mort » et « c'est le pilote » sont des hypothèses de la cliente, notées comme telles.",
            f"Hypothèses ordonnées : lire la signification du voyant dans le manuel ; contrôler le papier ou le rouleau ; contrôler les câbles après le déplacement ; enfin le pilote. Priorité : impact faible × urgence élevée = {PRIORITY_LABELS[priority(LOW, HIGH)]} ; l'échéance du lendemain justifie une intervention dans la journée.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Qualifier un ticket du centre de services",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Tu reçois un ticket par le formulaire en ligne d'un cabinet médical (secrétariat de trois personnes). "
            "Le document 1 est le ticket tel que l'utilisatrice l'a rempli. Tu dois le qualifier avant de "
            "l'attribuer."
        ),
        documents=(_table("Document 1 — Ticket T-2207 (support fictif)", ("Champ", "Contenu"),
                          ("Demandeur", "Secrétariat, poste d'accueil"),
                          ("Objet", "URGENT !!! scanner"),
                          ("Description", "Le scanner du poste d'accueil n'est plus reconnu depuis ce matin : « Aucun périphérique détecté ». Les deux autres secrétaires scannent sur leur poste. Les patients attendent pour que l'on scanne leurs documents d'admission."),
                          ("Priorité choisie par l'utilisatrice", "P1 critique")),),
        instructions=(
            "Évalue l'impact et l'urgence en justifiant chacun.",
            "Déduis la priorité et compare-la avec celle choisie par l'utilisatrice.",
        ),
        criteria=(
            _c("Impact", 1, "Moyen : poste indispensable (accueil des patients), mais contournement possible sur les deux autres postes."),
            _c("Urgence", 1, "Élevée : les patients attendent maintenant à l'accueil."),
            _c("Priorité", 1, f"{PRIORITY_LABELS[E12_PRIORITY]} ({PRIORITY_DELAYS[E12_PRIORITY]}) ; pas P1 : le service n'est pas arrêté. On explique poliment la différence et le délai."),
        ),
        correction=(
            "Impact : un seul poste touché, mais c'est le poste de l'accueil, indispensable ; les deux autres postes permettent de continuer à scanner : impact moyen. Urgence : élevée, des patients attendent.",
            f"Matrice : moyen × élevée = {PRIORITY_LABELS[E12_PRIORITY]}, {PRIORITY_DELAYS[E12_PRIORITY]}. L'utilisatrice a choisi P1 : on ne la contredit pas sèchement, on lui indique le délai et le contournement (scanner sur un autre poste en attendant). La priorité se justifie par l'impact et l'urgence, pas par le nombre de points d'exclamation.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Écrire des critères de réussite vérifiables",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Ton responsable relit quatre fiches d'incident et refuse leurs critères de réussite : « le PC marche », "
            "« l'imprimante fonctionne mieux », « le client est content », « c'est plus rapide ». Ils concernent un PC "
            "qui ne démarrait plus, une imprimante qui bourrait, un client mécontent d'une installation et un "
            "portable lent au démarrage."
        ),
        instructions=(
            "Explique ce qui ne va pas dans ces critères.",
            "Réécris chacun sous forme de test vérifiable, chiffré quand c'est possible.",
        ),
        criteria=(
            _c("Défaut", 1, "Critères vagues, non mesurables : personne ne peut prouver qu'ils sont atteints ; ils ne disent ni quel test faire ni quel résultat attendre."),
            _c("Critères réécrits", 4, "PC : démarre jusqu'au bureau et ouvre les logiciels de l'utilisateur ; imprimante : 50 pages sans bourrage ; client : liste des points demandés vérifiés avec lui et fiche signée ; portable : démarrage mesuré sous 1 minute (1 pt chacun)."),
        ),
        correction=(
            "Un critère de réussite doit être un test que l'on peut faire devant le client, avec un résultat attendu : c'est lui qui prouve la fin de l'intervention et évite les discussions. « Mieux », « content », « plus rapide » ne se mesurent pas.",
            "Exemples : « Le PC démarre jusqu'au bureau Windows et ouvre la messagerie et le logiciel de comptabilité » ; « 50 pages imprimées d'affilée sans bourrage » ; « chaque point de la demande est vérifié avec le client, qui signe la fiche » ; « démarrage jusqu'au bureau en moins d'une minute, mesuré trois fois ». Les chiffres sont convenus avec le client lors de la reformulation.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Plan d'action et estimation d'un remplacement de disque",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Une employée d'un bureau d'études se plaint d'un PC très lent ; le disque dur affiche des secteurs "
            "réalloués. Son responsable accepte le remplacement par un SSD avec réinstallation. Tu dois lui "
            "remettre le plan d'action et la durée annoncée (convention du cours : somme des tâches + 25 %, "
            "arrondie au quart d'heure supérieur). Le document 1 liste les tâches."
        ),
        documents=(_table("Document 1 — Tâches et durées (support fictif)", ("Tâche", "Durée (min)"),
                          *((t, str(m)) for t, m in E14_TASKS)),),
        instructions=(
            "Rédige le plan d'action en ordonnant les tâches et en justifiant la première.",
            "Calcule la durée annoncée.",
            "Indique ce que tu fais si la durée est dépassée.",
        ),
        criteria=(
            _c("Plan", 2, "Sauvegarde d'abord (disque défaillant, données de l'utilisatrice), puis SSD, installation, logiciels, restauration et contrôle avec l'utilisatrice."),
            _c("Durée", 2, f"{E14_SUM} min de tâches + 25 % = {fr(E14_SUM * 1.25)} min, arrondi : {E14_ESTIMATE} min soit {hm(E14_ESTIMATE)}."),
            _c("Dépassement", 1, "Prévenir le responsable avant de dépasser, expliquer la cause et faire accepter une nouvelle estimation."),
        ),
        correction=(
            "1. Sauvegarder les documents sur le NAS (le disque est défaillant : c'est la seule action qui protège les données). 2. Remplacer le disque par le SSD. 3. Installer Windows 11 et les mises à jour. 4. Installer la suite bureautique et le logiciel métier. 5. Restaurer les documents et contrôler avec l'utilisatrice (critères de réussite).",
            f"Durée : {E14_SUM} min de tâches ; avec 25 % d'imprévus : {fr(E14_SUM * 1.25)} min ; arrondie au quart d'heure supérieur : {E14_ESTIMATE} min, soit {hm(E14_ESTIMATE)} annoncées. Si l'intervention dépasse, on prévient le responsable avant de continuer et on fait accepter la nouvelle estimation (contrôle « budget » de l'arbre d'escalade).",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Rédiger l'accord du client avant une réinstallation",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Un indépendant (agent d'assurances) dépose son portable : Windows ne démarre plus et une réinstallation "
            "complète est probable. Le portable contient les dossiers de ses clients. Avant de toucher au disque, ta "
            "société exige un accord écrit, signé par le client, sur le bon d'intervention."
        ),
        instructions=(
            "Rédige le texte de l'accord (cinq à huit lignes) à faire signer.",
            "Cite les quatre points qu'il doit obligatoirement couvrir.",
        ),
        criteria=(
            _c("Sauvegarde", 1, "Ce qui est sauvegardé, où, par qui ; ce qui n'est pas garanti ; le client confirme qu'aucune autre donnée n'est à conserver."),
            _c("Risques", 1, "Réinstallation = effacement du disque ; perte possible de logiciels ou réglages ; durée estimée."),
            _c("Confidentialité", 1, "Les données des clients ne sont ni consultées ni copiées au-delà de la sauvegarde ; copie effacée après restitution."),
            _c("Autorisation", 1, "Accord explicite daté et signé du client (nom), opération décrite précisément ; arrêt et nouvel accord si autre chose est nécessaire."),
        ),
        correction=(
            "Exemple : « Je soussigné(e) …, propriétaire du portable n° de série …, autorise la société … à réinstaller Windows, ce qui efface tout le contenu du disque. Les dossiers Documents, Bureau et Messagerie seront copiés sur un disque de l'atelier avant l'opération puis restaurés ; les autres données ne sont pas garanties. Le technicien ne consulte pas le contenu des fichiers ; la copie est effacée après restitution. Durée estimée : … Toute autre opération fera l'objet d'un nouvel accord. Date, nom, signature. »",
            "Les quatre points : sauvegarde (quoi, où), risques (effacement, durée), confidentialité (pas de consultation, effacement de la copie) et autorisation (opération précise, signature datée). Le client est un professionnel qui détient des données personnelles de tiers : l'accord protège ses clients, lui et le technicien.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Lire un journal de tickets et regrouper un incident",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_TICKET,
        context=(
            "En fin de semaine, ton responsable te demande d'analyser le journal des tickets d'une PME de vente de "
            "matériel (document 1). Il soupçonne que plusieurs tickets traités séparément décrivent un même "
            "problème. Le service Ventes ne peut plus facturer depuis mardi."
        ),
        documents=(_table("Document 1 — Journal des tickets (support fictif)", ("N°", "Date", "Service", "Description", "Appareil"),
                          *E16_ROWS),),
        instructions=(
            "Indique les tickets qui décrivent un même incident et justifie.",
            "Qualifie cet incident regroupé : utilisateurs touchés, impact, urgence, priorité.",
            "Donne la première question à poser et à qui.",
        ),
        criteria=(
            _c("Regroupement", 2, f"{', '.join(E16_LINKED)} : même message « licence introuvable », même logiciel de facturation, trois postes de deux services en deux jours."),
            _c("Qualification", 2, f"Utilisateurs : comptabilité et ventes (plusieurs services) ; impact élevé ; urgence moyenne ; {PRIORITY_LABELS[E16_PRIORITY]} (à relever en P1 si une échéance de facturation tombe aujourd'hui)."),
            _c("Question", 1, "Au responsable ou à l'éditeur : qu'est-ce qui a changé lundi sur la licence (renouvellement, serveur de licences, mise à jour) ?"),
        ),
        correction=(
            f"{', '.join(E16_LINKED)} décrivent le même message sur le même logiciel, sur trois postes différents : la cause est commune (licence, serveur de licences), pas propre à chaque poste. Les tickets T-101, T-104 et T-106 sont sans rapport.",
            f"Incident regroupé : deux services touchés, facturation impossible aux Ventes : impact élevé ; urgence moyenne (pas d'échéance citée) : {PRIORITY_LABELS[E16_PRIORITY]}, à relever en P1 si une facturation urgente est annoncée pour le jour même. On rattache les trois tickets à un seul incident, et on demande au responsable ou à l'éditeur ce qui a changé lundi côté licence ; la gestion de la licence relève souvent d'une escalade (autorisation).",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Rédiger une fiche d'escalade",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Chez un photographe indépendant, le disque externe de 4 To qui contient trois ans de photos de mariage "
            "émet des clics et n'apparaît plus dans l'Explorateur. Il n'existe aucune autre copie. Ta société ne fait "
            "pas de récupération de données : un laboratoire partenaire s'en charge. Le client accepte l'envoi au "
            "laboratoire."
        ),
        instructions=(
            "Explique pourquoi tu arrêtes toute manipulation.",
            "Rédige la fiche d'escalade destinée au laboratoire (faits, tests déjà faits, ce qu'il ne faut pas faire, urgence, contact).",
        ),
        criteria=(
            _c("Arrêt", 1, "Contrôle « données » en échec : disque mécanique défaillant sans copie ; chaque mise sous tension peut détruire des données ; ni réparation, ni formatage, ni logiciel de récupération."),
            _c("Faits et tests", 2, "Disque externe 4 To, clics, absent de l'Explorateur ; testé une seule fois sur un autre câble et un autre PC (ou aucun test) ; aucune écriture faite."),
            _c("Consignes et suite", 2, "Données prioritaires (dossiers récents), confidentialité, accord et devis du client, contact et délai souhaité ; numéro de suivi noté sur la fiche."),
        ),
        correction=(
            "On arrête : le disque est mécanique et défaillant (clics), sans aucune autre copie. Chaque nouvelle mise sous tension peut aggraver l'état des plateaux ; un formatage ou un logiciel de récupération écrirait sur le disque. C'est le contrôle « données » de l'arbre : on escalade vers un spécialiste.",
            "Fiche : « Disque externe 4 To (marque, n° de série), propriété de … Symptômes : clics à la mise sous tension, disque non reconnu depuis le … Tests : un seul essai avec un autre câble sur un autre PC, même résultat ; aucune écriture, aucun logiciel lancé. Données à récupérer en priorité : mariages 2026. Données confidentielles (photos de clients). Devis à transmettre au client avant intervention. Contact : … Délai souhaité : … » On note le numéro de suivi du laboratoire et on informe le client.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Inventaire, références et garantie",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_TICKET,
        context=(
            "Un appel signale : « le portable de Julien Dumont (comptabilité) a l'écran fissuré, c'est le "
            "LT-COMPTA-02, il faut le réparer aujourd'hui ». Avant d'ouvrir la fiche, tu consultes l'inventaire de "
            "l'entreprise (document 1), daté du 27 octobre 2026."
        ),
        documents=(_table("Document 1 — Extrait de l'inventaire (support fictif)", ("N° d'inventaire", "Utilisateur", "Modèle", "N° de série", "Fin de garantie"),
                          ("LT-COMPTA-01", "Julien Dumont", "Portable 14 pouces", "5CD2401AB", "15/03/2027"),
                          ("LT-COMPTA-02", "Ana Silva", "Portable 14 pouces", "5CD2401AC", "15/03/2027"),
                          ("LT-COMPTA-03", "(stock, de prêt)", "Portable 14 pouces", "5CD2207XY", "02/06/2026")),),
        instructions=(
            "Relève l'incohérence et la façon de la lever.",
            "Indique ce que la garantie change pour l'intervention.",
            "Propose une solution pour que Julien Dumont travaille aujourd'hui.",
        ),
        criteria=(
            _c("Incohérence", 1, "LT-COMPTA-02 est attribué à Ana Silva ; Julien Dumont a LT-COMPTA-01 : vérifier l'étiquette et le n° de série sur place avant d'ouvrir la fiche."),
            _c("Garantie", 1, "LT-COMPTA-01 est sous garantie jusqu'au 15/03/2027 : ne pas ouvrir, demande au fabricant avec le n° de série (escalade)."),
            _c("Solution", 1, "Prêt de LT-COMPTA-03 (stock, hors garantie mais disponible), avec ses données sur le serveur ; noté sur la fiche."),
        ),
        correction=(
            "L'inventaire attribue LT-COMPTA-02 à Ana Silva et LT-COMPTA-01 à Julien Dumont : le numéro cité au téléphone est probablement faux. On vérifie l'étiquette et le numéro de série sur l'appareil, puis on note la bonne référence ; intervenir sur le mauvais portable ferait perdre du temps et pourrait toucher les données d'une autre personne.",
            "LT-COMPTA-01 est sous garantie jusqu'au 15 mars 2027 : l'ouvrir pourrait l'annuler. On ouvre une demande chez le fabricant avec le numéro de série (escalade). Pour que Julien Dumont travaille aujourd'hui, on lui prête LT-COMPTA-03 du stock, configuré avec son compte ; prêt et retour notés sur la fiche.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Évaluer la fiche d'un collègue avec la grille",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_TICKET,
        context=(
            "Dans le cadre de la formation d'un nouveau collègue, ton responsable te demande d'évaluer sa fiche "
            "d'incident avec la grille sur 20 du service. Tu as relevé, pour chaque critère, s'il est acquis "
            "(1), partiel (0,5) ou absent (0) : c'est le document 1."
        ),
        documents=(_table("Document 1 — Relevé d'évaluation (support fictif)", ("Critère", "Points", "Niveau relevé"),
                          *((label, str(points), fr(E19_MARKS[key])) for key, label, points, _d in EVAL_GRID)),),
        instructions=(
            "Calcule la note sur 20 en détaillant le calcul.",
            "Rédige deux conseils prioritaires pour le collègue.",
        ),
        criteria=(
            _c("Calcul", 2, f"Somme des points × niveau : {fr(E19_SCORE)} / {EVAL_TOTAL}."),
            _c("Conseils", 2, "Priorité aux critères absents : apparition et fréquence (date, reproductible ou intermittente, utilisateurs) ; données et autorisation (sauvegarde, confidentialité, accord écrit)."),
        ),
        correction=(
            "Calcul : " + " ; ".join(
                f"{label.lower()} {points} × {fr(E19_MARKS[key])} = {fr(points * E19_MARKS[key])}"
                for key, label, points, _d in EVAL_GRID
            ) + f". Total : {fr(E19_SCORE)} / {EVAL_TOTAL}.",
            "Conseils : 1) toujours noter la date d'apparition, la fréquence et les personnes touchées ; 2) ne jamais commencer sans avoir écrit la situation de la sauvegarde et obtenu l'accord du client. Ce sont les deux critères absents, et le second protège les données du client.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Rendre observable une panne intermittente",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_QUALIF,
        context=(
            "Le PC de montage vidéo d'une petite agence de communication redémarre « de temps en temps ». Tu as "
            "demandé au monteur de noter chaque jour ce qu'il faisait au moment des incidents. Le document 1 est "
            "son journal d'une semaine."
        ),
        documents=(_table("Document 1 — Journal du monteur (support fictif)", ("Jour", "Heure", "Événement", "Tâche en cours"),
                          *E20_ROWS),),
        instructions=(
            "Qualifie la panne (reproductible ou intermittente) et relève ce que le journal montre.",
            "Formule une hypothèse et le test qui la vérifie.",
            "Écris le critère de réussite adapté.",
        ),
        criteria=(
            _c("Qualification", 1, "Intermittente ; les trois redémarrages ont lieu pendant une tâche lourde (gravure, exports vidéo), jamais en bureautique."),
            _c("Hypothèse et test", 2, "Charge élevée → surchauffe ou alimentation insuffisante ; test : lancer un export ou un test de charge en surveillant températures et journaux (observateur d'événements)."),
            _c("Critère", 1, "Une semaine de travail normal (ou plusieurs exports longs) sans redémarrage, températures dans les limites."),
        ),
        correction=(
            "Panne intermittente : elle ne se produit pas à chaque fois. Le journal la rend observable : les trois redémarrages ont lieu pendant une gravure ou un export vidéo, jamais pendant le travail de bureau. L'heure ne compte pas ; c'est la charge qui déclenche.",
            "Hypothèse : la charge fait chauffer le processeur ou dépasse ce que fournit l'alimentation. Test : lancer un export long en surveillant les températures et consulter l'observateur d'événements (arrêt inattendu). Critère de réussite : plusieurs exports longs puis une semaine sans redémarrage, températures normales. On ne déclare jamais réparée une panne intermittente sur un seul essai réussi.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (10 questions de 2 points, réponses libres)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Reformuler la demande d'une pharmacienne",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Une pharmacienne appelle : « Depuis ce matin, l'ordinateur de la caisse 2 met une éternité à "
            "imprimer les tickets, enfin il les imprime mais il faut attendre trente secondes, à chaque client. "
            "C'est sûrement le câble. La caisse 1 va bien. On a une file de clients. »"
        ),
        instructions=("Rédige la reformulation pour la fiche d'incident, puis la phrase de validation au téléphone.",),
        criteria=(
            _c("Reformulation", 1, "Depuis ce matin, à la caisse 2, chaque ticket sort environ 30 s après la demande ; la caisse 1 fonctionne ; clients en attente. « Câble » noté comme hypothèse, pas dans la reformulation des faits."),
            _c("Validation", 1, "« Si je résume bien : … Est-ce exact ? » ; correction avec la demandeuse jusqu'à accord."),
        ),
        correction=(
            "« Depuis ce matin, à la caisse 2, chaque ticket s'imprime environ trente secondes après la demande, à chaque client ; la caisse 1 fonctionne normalement ; des clients attendent. » La piste du câble est une hypothèse de la demandeuse.",
            "Validation : « Si je résume bien : … Est-ce bien cela ? Y a-t-il autre chose ? »",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Observations et hypothèses d'un message",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Un enseignant envoie un message au support informatique de son école. Tu dois remplir la rubrique "
            "« Symptômes observés » de la fiche avec les seuls faits, et noter à part les hypothèses. Le "
            "document 1 est son message."
        ),
        documents=(_text_doc(
            "Document 1 — Message de l'enseignant (support fictif)",
            "« Le projecteur de la classe 12 est fichu, je pense que la lampe est grillée. Quand je branche mon "
            "portable, l'écran du projecteur affiche « Aucun signal » en bleu. Avec le portable d'un collègue, "
            "c'est pareil. Le câble HDMI a été changé pendant les vacances. Ce n'est pas urgent, j'ai cours dans la "
            "classe 12 lundi. »",
        ),),
        instructions=("Sépare les observations et les hypothèses, puis rédige la rubrique « Symptômes observés ».",),
        criteria=(
            _c("Tri", 1, "Observations : « Aucun signal » en bleu ; même résultat avec deux portables ; câble HDMI changé pendant les vacances (changement). Hypothèses : projecteur fichu, lampe grillée (contredite : l'écran bleu s'affiche, la lampe éclaire)."),
            _c("Rubrique", 1, "« Le projecteur de la classe 12 affiche « Aucun signal » (fond bleu) quand on branche un portable en HDMI, avec deux portables différents. »"),
        ),
        correction=(
            "Faits : message « Aucun signal » sur fond bleu ; même chose avec deux portables ; câble HDMI changé (changement récent). Hypothèses : « projecteur fichu », « lampe grillée » — contredite par l'observation : un écran bleu affiché prouve que la lampe éclaire.",
            "Rubrique : « Projecteur classe 12 : « Aucun signal » sur fond bleu à la connexion HDMI, avec deux portables différents. » Pistes : câble HDMI neuf, entrée sélectionnée sur le projecteur.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Priorité d'une panne de messagerie",
        question_type="short_answer",
        requirement_ids=R_WRITE,
        kind=KIND_QUALIF,
        context=(
            "Dans une entreprise de transport de 60 personnes, plus personne ne reçoit de courriels depuis 8 h. Les "
            "commandes urgentes arrivent par téléphone, ce qui permet de continuer à travailler, plus lentement. "
            "Matrice du cours : 1+1 → P1, 1+2 → P2, 1+3 ou 2+2 → P3, au-delà → P4 (1 = élevé)."
        ),
        instructions=("Donne l'impact, l'urgence et la priorité, en justifiant chacun en une phrase.",),
        criteria=(
            _c("Impact et urgence", 1, "Impact élevé : toute l'entreprise ; urgence moyenne : travail ralenti, contournement par téléphone."),
            _c("Priorité", 1, f"{PRIORITY_LABELS[X03_PRIORITY]}, {PRIORITY_DELAYS[X03_PRIORITY]}."),
        ),
        correction=(
            f"Impact élevé : les 60 personnes sont touchées. Urgence moyenne : le téléphone permet de continuer, plus lentement. Élevé × moyenne = {PRIORITY_LABELS[X03_PRIORITY]}, {PRIORITY_DELAYS[X03_PRIORITY]}.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Rubriques manquantes d'une fiche",
        question_type="document_analysis",
        requirement_ids=R_DATA,
        kind=KIND_TICKET,
        context=(
            "Avant une intervention de remplacement de carte réseau, ton responsable vérifie ta fiche d'incident. "
            "Le document 1 indique, rubrique par rubrique, si elle est remplie. Il refuse de valider l'intervention "
            "tant que la fiche est incomplète."
        ),
        documents=(_table("Document 1 — État de la fiche (support fictif)", ("Rubrique", "État"),
                          *((_label(k), "rempli" if v else "vide") for k, v in X04_FICHE.items())),),
        instructions=("Cite les rubriques obligatoires vides et explique pourquoi l'une d'elles bloque l'intervention.",),
        criteria=(
            _c("Rubriques", 1, ", ".join(_label(k) for k in X04_MISSING) + "."),
            _c("Blocage", 1, "Données et sauvegarde : sans savoir si une copie existe, on ne touche pas au matériel (ou critères de réussite : sans eux, impossible de prouver la fin de l'intervention)."),
        ),
        correction=(
            f"Rubriques vides : {', '.join(_label(k).lower() for k in X04_MISSING)}. La rubrique « Données et sauvegarde » bloque : on n'ouvre pas un PC sans savoir si les données sont protégées. Sans critères de réussite, on ne peut pas non plus prouver que l'intervention est terminée.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Que faire d'abord ? Signes d'intrusion",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_QUALIF,
        context=(
            "Tu interviens pour « un PC lent » chez un notaire. En arrivant, tu vois des fenêtres de commande qui "
            "s'ouvrent seules et des fichiers renommés en « .locked » dans le dossier partagé. La dernière "
            "sauvegarde date de deux mois. Tu es technicien de premier niveau."
        ),
        instructions=("Indique, dans l'ordre, les deux premières actions et à qui tu escalades, en justifiant l'ordre.",),
        criteria=(
            _c("Ordre", 1, "Sécurité d'abord : isoler le poste du réseau (câble, Wi-Fi) sans l'éteindre ni rien effacer ; ensuite seulement la question des données."),
            _c("Escalade", 1, "Responsable informatique ou sécurité (et le notaire) ; signaler la sauvegarde ancienne ; ne pas tenter de « nettoyer » soi-même."),
        ),
        correction=(
            "Premier contrôle en échec : la sécurité, qui passe avant celui des données. 1) Isoler le poste du réseau pour stopper le chiffrement des partages, sans effacer de fichier ni réinstaller (garder les traces). 2) Prévenir immédiatement le notaire et escalader au responsable informatique ou sécurité, en signalant que la dernière sauvegarde date de deux mois.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Qualifier une coupure « de temps en temps »",
        question_type="long_answer",
        requirement_ids=R_DIAG,
        kind=KIND_QUALIF,
        context=(
            "Une secrétaire signale : « Ma connexion au logiciel de rendez-vous coupe de temps en temps, parfois "
            "deux fois par jour, parfois rien pendant trois jours. Quand je reviens, ça marche. » Tu ne peux pas "
            "rester toute la journée sur place."
        ),
        instructions=("Qualifie la panne, puis explique comment tu la rends observable et quel critère de réussite tu fixes.",),
        criteria=(
            _c("Qualification et journal", 1, "Intermittente ; journal demandé à l'utilisatrice : date, heure, message exact, ce qui était en cours, autres collègues touchés."),
            _c("Critère", 1, "Critère sur une durée : par exemple une semaine (ou dix jours ouvrables) sans coupure, journal à l'appui."),
        ),
        correction=(
            "Panne intermittente : on ne peut pas la reproduire à la demande. On la rend observable avec un journal (date, heure, message exact, tâche en cours, autres personnes touchées) et, si possible, les journaux du poste. Critère de réussite : une semaine de travail sans coupure après la correction, pas un seul essai réussi.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Critères de réussite d'une installation de scanner",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Une agence immobilière demande : « Installez le nouveau scanner pour que les trois agents puissent "
            "scanner les compromis en PDF dans le dossier partagé Ventes. » Tu rédiges les critères de réussite "
            "de la fiche avant l'intervention."
        ),
        instructions=("Écris trois critères de réussite vérifiables.",),
        criteria=(
            _c("Critères", 2, "Chaque agent (les trois) scanne un compromis de plusieurs pages ; le PDF arrive dans le dossier Ventes et s'ouvre lisiblement ; un agent d'un autre service n'y a pas accès / l'agent valide (0,5 à 1 pt par critère vérifiable)."),
        ),
        correction=(
            "1) Depuis chacun des trois postes, un compromis de plusieurs pages est scanné en un seul PDF. 2) Le PDF est enregistré dans le dossier partagé Ventes et s'ouvre, lisible, depuis un autre poste. 3) Les trois agents valident l'essai (signature de la fiche). Chaque critère est un test que l'on fait devant le client.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Estimer le remplacement d'un switch",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Un cabinet comptable demande combien de temps durera le remplacement de son switch défectueux. "
            "Convention du cours : somme des tâches + 25 %, arrondie au quart d'heure supérieur. Le document 1 "
            "liste les tâches."
        ),
        documents=(_table("Document 1 — Tâches (support fictif)", ("Tâche", "Durée (min)"),
                          *((t, str(m)) for t, m in X08_TASKS)),),
        instructions=("Calcule la durée annoncée et écris la phrase que tu dis au client.",),
        criteria=(
            _c("Calcul", 1, f"{sum(m for _t, m in X08_TASKS)} min + 25 % = {fr(sum(m for _t, m in X08_TASKS) * 1.25)} min → {X08_ESTIMATE} min ({hm(X08_ESTIMATE)})."),
            _c("Annonce", 1, f"Durée annoncée {hm(X08_ESTIMATE)} avec coupure du réseau ; prévenir avant tout dépassement."),
        ),
        correction=(
            f"Total des tâches : {sum(m for _t, m in X08_TASKS)} min ; avec 25 % d'imprévus : {fr(sum(m for _t, m in X08_TASKS) * 1.25)} min ; arrondi au quart d'heure supérieur : {X08_ESTIMATE} min, soit {hm(X08_ESTIMATE)}. « L'intervention durera environ {hm(X08_ESTIMATE)}, pendant lesquelles le réseau sera coupé ; je vous préviens avant tout dépassement. »",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Données personnelles sur le PC d'un employé",
        question_type="long_answer",
        requirement_ids=R_DATA,
        kind=KIND_WRITE,
        context=(
            "Le directeur d'une PME te demande de récupérer « tous les fichiers » du PC d'une employée en congé "
            "maladie, pour les copier sur le poste de sa remplaçante. Le PC contient aussi ses courriels et des "
            "dossiers personnels. Tu es technicien externe sous contrat de maintenance."
        ),
        instructions=("Indique ce que tu demandes avant d'agir et ce que tu ne fais pas.",),
        criteria=(
            _c("Avant d'agir", 1, "Demande écrite et précise du directeur (quels dossiers professionnels), conforme aux règles de l'entreprise ; consultation du responsable ou de la procédure ; trace sur la fiche."),
            _c("Limites", 1, "Pas d'ouverture ni de copie des courriels et dossiers personnels ; pas de partage de mot de passe ; copie limitée aux dossiers professionnels désignés."),
        ),
        correction=(
            "Avant d'agir : une demande écrite du directeur précisant les dossiers professionnels à copier, conforme aux règles de l'entreprise (charte informatique, protection des données), notée sur la fiche. Contrôle « autorisation » : si la demande dépasse ce cadre, on escalade au responsable.",
            "On ne fait pas : ouvrir ou copier les courriels et dossiers personnels, communiquer le mot de passe de l'employée, copier « tout » sans tri. La confidentialité protège l'employée comme l'entreprise.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Cinq questions pour « Internet ne marche plus »",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Un client particulier appelle la boutique informatique : « Internet ne marche plus. » Il n'a aucune "
            "connaissance technique. Tu dois recueillir les informations utiles par téléphone avant de décider "
            "d'un déplacement."
        ),
        instructions=("Écris cinq questions utiles, dans l'ordre où tu les poses, et pour chacune ce qu'elle t'apprend.",),
        criteria=(
            _c("Questions", 2, "Que voyez-vous exactement (message) ; depuis quand ; sur quels appareils (un ou tous) ; qu'est-ce qui a changé (box, orage, déménagement) ; voyants de la box — questions ouvertes puis fermées, sans jargon (0,4 pt par question utile justifiée)."),
        ),
        correction=(
            "1) « Que se passe-t-il exactement quand vous ouvrez une page ? » (observation, message). 2) « Depuis quand ? » (apparition). 3) « Est-ce sur tous vos appareils, ou un seul ? » (étendue : box ou appareil). 4) « Qu'est-ce qui a changé récemment : orage, déménagement, nouvelle box ? » (changements). 5) « Quels voyants de la box sont allumés, et de quelle couleur ? » (état de la box). Pas de jargon, pas de question accusatrice.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS

EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, classements et remises en ordre cohérents,
    exigence du cours citée, nombre d'exercices de rédaction, d'analyse de tickets et de
    qualification demandés par le ticket, valeurs calculées."""
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
        errors.append("Ticket #225 : au moins 18 exercices et un mini-examen de 10 questions.")
    kinds = [i.kind for i in PRACTICE_ITEMS]
    if kinds.count(KIND_WRITE) < 5 or kinds.count(KIND_TICKET) < 5 or kinds.count(KIND_QUALIF) < 5:
        errors.append("Ticket #225 : au moins 5 exercices de rédaction, 5 analyses de tickets et 5 qualifications.")
    if E06_TARGETS != (None, E_AUTH, E_SECURITY, E_DATA, None, E_SKILL, E_BUDGET):
        errors.append("E06 : décisions d'escalade inattendues.")
    if E04_PRIORITIES != ("P1", "P2", "P4", "P4", "P3", "P3", "P1"):
        errors.append("E04 : priorités inattendues.")
    if len(E09_MISSING) != 6 or len(X04_MISSING) != 4:
        errors.append("E09/X04 : rubriques manquantes inattendues.")
    if (E14_ESTIMATE, X08_ESTIMATE, E19_SCORE) != (210, 120, 11):
        errors.append("E14/X08/E19 : estimations ou note inattendues.")
    if (E12_PRIORITY, E16_PRIORITY, X03_PRIORITY, X05_TARGET) != ("P2", "P2", "P2", E_SECURITY):
        errors.append("E12/E16/X03/X05 : qualification inattendue.")
    if {k for _t, k in E02_CASES} != {OBSERVATION, HYPOTHESIS} or {k for _t, k in E03_CASES} != {REPRODUCIBLE, INTERMITTENT}:
        errors.append("E02/E03 : catégories inutilisées.")
    if {k for _q, k, _w in E05_CASES} != {USEFUL, AVOID} or len(VAGUE_CRITERIA) != 4:
        errors.append("E05/E13 : données inattendues.")
    return errors


"""PR26 « Analyser une demande d'intervention technique » — données de référence, règles du
cours et schémas (ticket #225).

Ce cours est un cours de **méthode écrite** (exigence AP-16 « vocabulaire technique » et
complément AP-C01 « rédiger une réponse écrite de technicien ») : il ne porte pas de valeurs
électriques ou réseau, mais des **règles de qualification** qu'un dossier d'examen applique et
qu'un correcteur vérifie. Elles sont écrites ici une seule fois, sous forme de données et de
fonctions testées, et réutilisées par le cours, les exercices, le mini-examen et les schémas :

- `priority(impact, urgency)` : matrice impact × urgence → priorité P1 à P4 (convention du
  cours, inspirée des pratiques de centre de services de type ITIL ; chaque entreprise fixe la
  sienne) et délai de prise en charge ;
- `escalation(...)` / `ESCALATION_CHECKS` : ordre des contrôles qui imposent d'arrêter et
  d'escalader (sécurité, autorisation, données, compétence, budget) ;
- `INCIDENT_FIELDS` / `missing_fields` : la fiche d'incident et ses rubriques obligatoires ;
- `EVAL_GRID` / `grid_score` : grille d'évaluation d'une fiche d'incident sur 20 ;
- `estimate` : estimation d'une intervention (somme des tâches + marge, au quart d'heure) ;
- `STATEMENTS` (observation / hypothèse), `OCCURRENCES` (reproductible / intermittente) ;
- `DOSSIERS` : les cinq dossiers entièrement corrigés (PC inerte, impression, lenteur, accès
  partagé, Wi-Fi), dont la priorité et la décision d'escalade sont **calculées**.

Les schémas sont construits en SVG depuis ces données (aucune image générée), comme PR18 à
PR25. Les personnes, entreprises et numéros d'inventaire sont fictifs.
"""

import math
from dataclasses import dataclass
from html import escape

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
_P_FILLS = {"P1": "#fbecec", "P2": "#fff3c4", "P3": "#e8f0fb", "P4": "#e9f5ec"}

# =============================================================================================
# 1. Impact, urgence et priorité (convention du cours)
# =============================================================================================

HIGH, MEDIUM, LOW = 1, 2, 3
LEVELS = (HIGH, MEDIUM, LOW)

IMPACT_LABELS: dict[int, str] = {
    HIGH: "Élevé",
    MEDIUM: "Moyen",
    LOW: "Faible",
}
IMPACT_RULES: dict[int, str] = {
    HIGH: "toute l'entreprise, un service entier, un serveur partagé ou des clients externes touchés",
    MEDIUM: "plusieurs personnes ou un poste indispensable (accueil, caisse, comptabilité)",
    LOW: "une seule personne, avec un contournement possible (autre poste, autre imprimante)",
}
URGENCY_LABELS: dict[int, str] = {
    HIGH: "Élevée",
    MEDIUM: "Moyenne",
    LOW: "Faible",
}
URGENCY_RULES: dict[int, str] = {
    HIGH: "activité arrêtée maintenant, ou échéance dans l'heure (paie, examen, livraison)",
    MEDIUM: "travail ralenti ou dégradé, échéance dans la journée",
    LOW: "simple gêne, la demande peut attendre un rendez-vous",
}

PRIORITIES = ("P1", "P2", "P3", "P4")
PRIORITY_LABELS: dict[str, str] = {
    "P1": "P1 critique",
    "P2": "P2 haute",
    "P3": "P3 normale",
    "P4": "P4 basse",
}
PRIORITY_DELAYS: dict[str, str] = {
    "P1": "prise en charge immédiate (30 min au plus)",
    "P2": "prise en charge dans les 2 heures",
    "P3": "prise en charge dans la journée ouvrable",
    "P4": "intervention planifiée (5 jours ouvrables au plus)",
}


def priority(impact: int, urgency: int) -> str:
    """Matrice impact × urgence (1 = élevé, 3 = faible) : 1+1 → P1 ; 1+2 → P2 ; 1+3 ou 2+2
    → P3 ; au-delà → P4. Symétrique : impact et urgence pèsent autant."""
    if impact not in LEVELS or urgency not in LEVELS:
        raise ValueError("Impact et urgence valent 1 (élevé), 2 (moyen) ou 3 (faible).")
    return PRIORITIES[min(impact + urgency - 2, 3)]


def priority_text(impact: int, urgency: int) -> str:
    p = priority(impact, urgency)
    return (f"impact {IMPACT_LABELS[impact].lower()} × urgence {URGENCY_LABELS[urgency].lower()} = "
            f"{PRIORITY_LABELS[p]}, {PRIORITY_DELAYS[p]}")


PRIORITY_MATRIX: tuple[tuple[str, ...], ...] = tuple(
    tuple(priority(i, u) for u in LEVELS) for i in LEVELS
)

# =============================================================================================
# 2. Observation, hypothèse ; reproductible, intermittente
# =============================================================================================

OBSERVATION = "Observation (fait constaté, vérifiable)"
HYPOTHESIS = "Hypothèse ou interprétation (cause supposée)"
STATEMENT_KINDS = (OBSERVATION, HYPOTHESIS)

# Phrases d'une demande réelle (support fictif) : la catégorie est la référence des exercices.
STATEMENTS: tuple[tuple[str, str], ...] = (
    ("Le PC ne s'allume plus : aucun voyant, aucun bruit de ventilateur.", OBSERVATION),
    ("C'est sûrement l'alimentation qui a grillé.", HYPOTHESIS),
    ("Le message « Imprimante hors ligne » s'affiche depuis lundi matin.", OBSERVATION),
    ("Le réseau est en panne.", HYPOTHESIS),
    ("Trois collègues du même bureau n'ouvrent plus le dossier \\\\SRV-01\\Compta.", OBSERVATION),
    ("Windows a dû attraper un virus, il est devenu très lent.", HYPOTHESIS),
    ("L'ouverture d'une session prend 6 minutes contre 1 minute la semaine passée.", OBSERVATION),
    ("Le Wi-Fi de la salle de réunion est trop faible.", HYPOTHESIS),
    ("Le portable affiche « Pas d'Internet, sécurisé » sur le réseau BUREAU.", OBSERVATION),
    ("Le nouveau logiciel de caisse est incompatible avec l'imprimante.", HYPOTHESIS),
)

REPRODUCIBLE = "Panne reproductible"
INTERMITTENT = "Panne intermittente"
OCCURRENCE_KINDS = (REPRODUCIBLE, INTERMITTENT)
OCCURRENCES: tuple[tuple[str, str], ...] = (
    ("À chaque démarrage, l'écran affiche « No bootable device ».", REPRODUCIBLE),
    ("Le document de 3 pages sort toujours sans la page 2, à chaque essai.", REPRODUCIBLE),
    ("Le PC redémarre seul, deux ou trois fois par semaine, sans action particulière.", INTERMITTENT),
    ("Le Wi-Fi coupe quelques secondes, certains jours, vers midi.", INTERMITTENT),
    ("Le dossier partagé refuse l'accès à Julie à chaque tentative, depuis hier.", REPRODUCIBLE),
    ("L'imprimante affiche « bourrage » une fois sur vingt environ, sans papier coincé.", INTERMITTENT),
    ("L'écran reste noir à chaque fois que le câble HDMI est branché sur le port de gauche, jamais à droite.", REPRODUCIBLE),
)

# =============================================================================================
# 3. Questions utiles, reformulation, critères de réussite
# =============================================================================================

USEFUL = "Question utile"
AVOID = "Question à éviter"
QUESTION_KINDS = (USEFUL, AVOID)
QUESTIONS: tuple[tuple[str, str, str], ...] = (
    ("Depuis quand le problème se produit-il, et à quelle occasion l'avez-vous vu la première fois ?", USEFUL,
     "date et circonstances d'apparition"),
    ("Vous avez encore cliqué sur une pièce jointe douteuse ?", AVOID, "accusatrice : le client se ferme"),
    ("Quel message exact s'affiche ? Pouvez-vous me le lire mot pour mot ou le photographier ?", USEFUL,
     "observation exacte au lieu d'un résumé"),
    ("Votre serveur DHCP distribue-t-il encore des baux ?", AVOID, "jargon : l'utilisateur ne peut pas répondre"),
    ("Qu'est-ce qui a changé récemment : mise à jour, nouveau matériel, déplacement, nouveau logiciel ?", USEFUL,
     "changements récents, souvent la cause"),
    ("C'est le disque dur qui lâche, n'est-ce pas ?", AVOID, "question orientée : impose une hypothèse"),
    ("D'autres collègues ont-ils le même problème, sur d'autres postes ?", USEFUL,
     "étendue : un poste ou tout un service"),
    ("Est-ce que cela se produit à chaque fois, ou seulement de temps en temps ?", USEFUL,
     "reproductible ou intermittente"),
)

# Critère de réussite : vérifiable par un test décrit, chiffré si possible, accepté par le client.
VAGUE_CRITERIA: tuple[str, ...] = (
    "le PC marche",
    "l'imprimante fonctionne mieux",
    "le client est content",
    "c'est plus rapide",
)

# =============================================================================================
# 4. Fiche d'incident (formulaire professionnel)
# =============================================================================================


@dataclass(frozen=True)
class FormField:
    key: str
    section: str
    label: str
    why: str
    required: bool = True


S_ID, S_EQUIP, S_SYMPT, S_QUALIF, S_DATA, S_PLAN = (
    "1. Demande", "2. Équipement et contexte", "3. Symptômes", "4. Qualification",
    "5. Données, risques et autorisation", "6. Plan et suite",
)
INCIDENT_FIELDS: tuple[FormField, ...] = (
    FormField("numero", S_ID, "N° de la demande", "retrouver et suivre la demande"),
    FormField("date", S_ID, "Date et heure de la demande", "mesurer le délai, situer l'apparition"),
    FormField("demandeur", S_ID, "Demandeur, service et contact", "rappeler et confirmer"),
    FormField("inventaire", S_EQUIP, "N° d'inventaire et modèle", "intervenir sur le bon appareil"),
    FormField("emplacement", S_EQUIP, "Emplacement", "trouver l'appareil"),
    FormField("contexte", S_EQUIP, "Contexte matériel, logiciel et réseau", "système, logiciel, connexion utilisés"),
    FormField("symptomes", S_SYMPT, "Symptômes observés (mots exacts, message)", "partir de faits, pas d'avis"),
    FormField("apparition", S_SYMPT, "Date d'apparition et fréquence", "reproductible ou intermittente"),
    FormField("changements", S_SYMPT, "Changements récents", "mise à jour, déplacement, nouveau matériel"),
    FormField("utilisateurs", S_SYMPT, "Utilisateurs touchés", "un poste ou tout un service"),
    FormField("impact", S_QUALIF, "Impact", "étendue des conséquences"),
    FormField("urgence", S_QUALIF, "Urgence", "délai avant un dommage réel"),
    FormField("priorite", S_QUALIF, "Priorité", "ordre de traitement (matrice)"),
    FormField("sauvegarde", S_DATA, "Données et sauvegarde", "existe-t-il une copie récente ?"),
    FormField("confidentialite", S_DATA, "Confidentialité et consentement", "accès aux données accepté par écrit"),
    FormField("autorisation", S_DATA, "Risques annoncés et autorisation", "qui accepte quoi, signé"),
    FormField("reformulation", S_PLAN, "Reformulation validée par le demandeur", "même compréhension des deux côtés"),
    FormField("criteres", S_PLAN, "Critères de réussite", "test qui prouvera la réparation"),
    FormField("plan", S_PLAN, "Plan d'action et estimation", "étapes, durée, coût"),
    FormField("escalade", S_PLAN, "Escalade (oui/non, vers qui, pourquoi)", "limite de compétence ou d'autorisation"),
    FormField("observations", S_PLAN, "Remarques", "informations complémentaires", required=False),
)
FIELDS_BY_KEY: dict[str, FormField] = {f.key: f for f in INCIDENT_FIELDS}
REQUIRED_KEYS: tuple[str, ...] = tuple(f.key for f in INCIDENT_FIELDS if f.required)
SECTIONS: tuple[str, ...] = tuple(dict.fromkeys(f.section for f in INCIDENT_FIELDS))


def missing_fields(filled: dict[str, str]) -> tuple[str, ...]:
    """Rubriques obligatoires vides ou absentes d'une fiche, dans l'ordre du formulaire."""
    return tuple(k for k in REQUIRED_KEYS if not (filled.get(k) or "").strip())


# =============================================================================================
# 5. Escalade : contrôles avant d'intervenir
# =============================================================================================

E_SECURITY, E_AUTH, E_DATA, E_SKILL, E_BUDGET = "securite", "autorisation", "donnees", "competence", "budget"
ESCALATION_CHECKS: tuple[tuple[str, str, str], ...] = (
    (E_SECURITY, "Aucun signe d'incident de sécurité (virus, intrusion, fuite de données)",
     "Isoler le poste du réseau, ne rien effacer, escalader au responsable sécurité ou informatique."),
    (E_AUTH, "L'action reste dans mon rôle et mes droits",
     "Escalader au responsable : serveur, droits d'administration, compte d'une autre personne, achat."),
    (E_DATA, "Les données sont sauvegardées ou ne sont pas menacées",
     "Arrêter : sauvegarder d'abord ; disque qui claque sans copie → spécialiste en récupération."),
    (E_SKILL, "J'ai la compétence, les pièces et l'outillage",
     "Escalader au niveau 2, au fabricant (garantie) ou au prestataire (copieur, Internet)."),
    (E_BUDGET, "Durée et coût restent dans l'estimation acceptée",
     "Suspendre et présenter une nouvelle estimation au client avant de continuer."),
)
ESCALATION_FINAL = "Intervenir selon le plan d'action accepté, puis vérifier les critères de réussite."
ESCALATION_KEYS = tuple(k for k, _q, _a in ESCALATION_CHECKS)
DIRECT = "Traiter directement"
ESCALATE = "Arrêter et escalader"
ESCALATION_KINDS = (DIRECT, ESCALATE)


@dataclass(frozen=True)
class Situation:
    """Réponses aux contrôles d'escalade (True = contrôle réussi)."""

    securite: bool = True
    autorisation: bool = True
    donnees: bool = True
    competence: bool = True
    budget: bool = True


def escalation(situation: Situation) -> str | None:
    """Premier contrôle en échec (clé de `ESCALATION_CHECKS`), ou None : on peut intervenir."""
    for key in ESCALATION_KEYS:
        if not getattr(situation, key):
            return key
    return None


def escalation_action(situation: Situation) -> str:
    key = escalation(situation)
    if key is None:
        return ESCALATION_FINAL
    return next(action for k, _q, action in ESCALATION_CHECKS if k == key)


def only(key: str) -> Situation:
    return Situation(**{key: False})


# =============================================================================================
# 6. Estimation d'une intervention
# =============================================================================================

MARGIN = 0.25  # convention du cours : +25 % d'imprévus, arrondi au quart d'heure supérieur


def estimate(task_minutes: tuple[int, ...]) -> int:
    """Durée annoncée (minutes) : somme des tâches + 25 %, arrondie au quart d'heure supérieur."""
    raw = sum(task_minutes) * (1 + MARGIN)
    return int(math.ceil(raw / 15 - 1e-9) * 15)


def hm(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    if not h:
        return f"{m} min"
    return f"{h} h {m:02d}" if m else f"{h} h"


# =============================================================================================
# 7. Grille d'évaluation d'une fiche d'incident (sur 20)
# =============================================================================================

EVAL_GRID: tuple[tuple[str, str, int, str], ...] = (
    ("identification", "Identification", 2, "demande, demandeur, contact, n° d'inventaire et emplacement"),
    ("symptomes", "Symptômes", 3, "faits observés et mots exacts, séparés des hypothèses"),
    ("contexte", "Contexte et changements", 2, "matériel, logiciel, réseau ; changements récents"),
    ("frequence", "Apparition et fréquence", 2, "date, reproductible ou intermittente, utilisateurs touchés"),
    ("priorite", "Priorité", 3, "impact et urgence justifiés, priorité de la matrice"),
    ("donnees", "Données et autorisation", 3, "sauvegarde, confidentialité, risques annoncés, accord écrit"),
    ("criteres", "Critères de réussite", 2, "tests vérifiables, chiffrés si possible"),
    ("plan", "Plan et estimation", 2, "étapes ordonnées, durée et coût annoncés"),
    ("escalade", "Escalade", 1, "décision justifiée (oui/non, vers qui)"),
)
EVAL_TOTAL = sum(points for _k, _l, points, _d in EVAL_GRID)
EVAL_KEYS = tuple(k for k, *_r in EVAL_GRID)


def grid_score(marks: dict[str, float]) -> float:
    """Note sur 20 : chaque critère est acquis (1), partiel (0,5) ou absent (0)."""
    if any(v not in (0, 0.5, 1) for v in marks.values()) or set(marks) - set(EVAL_KEYS):
        raise ValueError("Critère inconnu ou niveau différent de 0, 0,5 ou 1.")
    return sum(points * marks.get(key, 0) for key, _l, points, _d in EVAL_GRID)


def fr(value: float) -> str:
    return f"{value:g}".replace(".", ",")


# =============================================================================================
# 8. Démarche et procédures
# =============================================================================================

ANALYSIS_STEPS: tuple[tuple[str, str], ...] = (
    ("Recueillir", "Noter la demande telle qu'elle est dite, avec date, demandeur et contact."),
    ("Identifier", "Relever n° d'inventaire, modèle, emplacement, système, logiciel et réseau."),
    ("Questionner", "Questions ouvertes puis fermées : symptômes, date, changements, personnes touchées."),
    ("Qualifier", "Séparer observations et hypothèses ; reproductible ou intermittente."),
    ("Prioriser", "Évaluer impact et urgence, lire la priorité dans la matrice."),
    ("Protéger", "Sauvegarde, confidentialité, risques annoncés, accord écrit du client."),
    ("Reformuler", "Résumer la demande et les critères de réussite, les faire valider."),
    ("Planifier", "Plan d'action ordonné, durée et coût estimés."),
    ("Décider", "Intervenir ou escalader, et le noter sur la fiche."),
)
INTERVIEW_STEPS: tuple[tuple[str, str], ...] = (
    ("Accueillir", "Se présenter, noter l'identité et le moyen de rappel."),
    ("Écouter", "Laisser décrire le problème sans interrompre ni conclure."),
    ("Ouvrir", "Questions ouvertes : que voyez-vous ? depuis quand ? qu'est-ce qui a changé ?"),
    ("Préciser", "Questions fermées : message exact, à chaque fois ou parfois, d'autres postes ?"),
    ("Reformuler", "« Si je résume : … » ; corriger avec le demandeur jusqu'à accord."),
    ("Annoncer", "Priorité, délai, prochaine étape et précautions (ne rien supprimer)."),
)
ESCALATION_STEPS: tuple[tuple[str, str], ...] = (
    ("Constater", "Nommer la limite atteinte : sécurité, droits, données, compétence ou budget."),
    ("Sécuriser", "Arrêter l'action risquée ; isoler si besoin ; ne rien effacer."),
    ("Informer", "Prévenir le demandeur : ce qui est fait, ce qui bloque, qui prend le relais."),
    ("Rédiger", "Fiche d'escalade : faits, tests déjà faits, hypothèses, urgence, pièces jointes."),
    ("Transmettre", "Au bon niveau : responsable, niveau 2, fabricant ou prestataire."),
    ("Suivre", "Noter le numéro de transfert, relancer, clôturer avec le demandeur."),
)
PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Analyser une demande d'intervention", ANALYSIS_STEPS),
    ("Conduire l'entretien de recueil", INTERVIEW_STEPS),
    ("Escalader une demande", ESCALATION_STEPS),
)

# =============================================================================================
# 9. Les cinq dossiers entièrement corrigés
# =============================================================================================


@dataclass(frozen=True)
class Dossier:
    key: str
    title: str
    request: str  # demande telle qu'elle est reçue (mots du demandeur)
    questions: tuple[tuple[str, str], ...]  # (question posée, réponse obtenue)
    fiche: tuple[tuple[str, str], ...]  # (clé de INCIDENT_FIELDS, contenu)
    observations: tuple[str, ...]
    hypotheses: tuple[str, ...]
    occurrence: str
    impact: int
    urgency: int
    situation: Situation
    criteria: tuple[str, ...]
    tasks: tuple[tuple[str, int], ...]  # (tâche, minutes)
    conclusion: str

    @property
    def priority(self) -> str:
        return priority(self.impact, self.urgency)

    @property
    def estimate_minutes(self) -> int:
        return estimate(tuple(m for _t, m in self.tasks))

    @property
    def escalation(self) -> str | None:
        return escalation(self.situation)

    def field(self, key: str) -> str:
        return dict(self.fiche).get(key, "")


DOSSIERS: tuple[Dossier, ...] = (
    Dossier(
        key="D1",
        title="PC inerte à la comptabilité",
        request=(
            "« Mon PC est mort, plus rien ne marche, je pense que c'est la carte mère. J'ai la TVA à rentrer "
            "aujourd'hui ! » — Sophie Lambert, comptable, cabinet Dewez (fictif), lundi 9 h 05."
        ),
        questions=(
            ("Que se passe-t-il exactement quand vous appuyez sur le bouton ?", "Rien : aucun voyant, aucun bruit."),
            ("Depuis quand ?", "Ce matin ; vendredi soir il fonctionnait."),
            ("Quelque chose a-t-il changé ce week-end ?", "Le bureau a été nettoyé, les prises ont été déplacées."),
            ("Les autres appareils de votre bureau fonctionnent-ils ?", "L'écran s'allume, la lampe aussi."),
            ("Où sont vos fichiers de TVA ?", "Sur le disque du PC ; la dernière copie sur clé date d'un mois."),
        ),
        fiche=(
            ("numero", "INT-2610-014"),
            ("date", "Lundi, 9 h 05"),
            ("demandeur", "S. Lambert, comptabilité, poste 214"),
            ("inventaire", "PC-COMPTA-02, tour de bureau"),
            ("emplacement", "Bureau 2, sous le bureau"),
            ("contexte", "Windows 11, logiciel de comptabilité, réseau filaire"),
            ("symptomes", "Aucun voyant ni ventilateur à l'appui sur le bouton ; écran et lampe allumés"),
            ("apparition", "Lundi matin, à chaque essai (reproductible)"),
            ("changements", "Nettoyage du week-end, prises déplacées"),
            ("utilisateurs", "Une personne, poste indispensable (TVA du jour)"),
            ("impact", "Moyen : poste indispensable de la comptabilité"),
            ("urgence", "Élevée : déclaration à rentrer aujourd'hui"),
            ("priorite", "P2 haute"),
            ("sauvegarde", "Copie sur clé vieille d'un mois : ne rien formater"),
            ("confidentialite", "Données comptables : accès limité au dossier TVA, accord oral puis écrit"),
            ("autorisation", "Ouverture du boîtier acceptée par le responsable ; risque annoncé : aucun pour les données"),
            ("reformulation", "« Votre PC ne montre aucun signe d'alimentation depuis ce matin ; il vous faut vos fichiers TVA aujourd'hui. »"),
            ("criteres", "Le PC démarre sur Windows ; le dossier TVA s'ouvre ; le logiciel de comptabilité se lance"),
            ("plan", "Contrôler câble, prise et interrupteur arrière ; tester l'alimentation ; sinon prêter un poste et récupérer le disque"),
            ("escalade", "Non : dans mes compétences et autorisations"),
        ),
        observations=(
            "aucun voyant, aucun ventilateur",
            "écran et lampe du même bureau allumés",
            "prises déplacées pendant le nettoyage",
        ),
        hypotheses=("« carte mère » (avis de la demandeuse)", "câble ou interrupteur arrière", "alimentation défaillante"),
        occurrence=REPRODUCIBLE,
        impact=MEDIUM,
        urgency=HIGH,
        situation=Situation(),
        criteria=(
            "Le PC démarre jusqu'au bureau Windows.",
            "Le dossier TVA s'ouvre et le logiciel de comptabilité se lance.",
            "La demandeuse confirme pouvoir travailler.",
        ),
        tasks=(("Contrôler prise, câble, interrupteur arrière", 10), ("Tester l'alimentation au testeur", 20),
               ("Démarrer et contrôler les critères", 15)),
        conclusion=(
            "Demande qualifiée P2 (impact moyen, urgence élevée) : PC sans aucun signe d'alimentation depuis le "
            "déplacement des prises. Les hypothèses vont de la plus simple (câble, interrupteur) à l'alimentation ; "
            "la carte mère n'est qu'un avis. Données à protéger (copie d'un mois). Intervention directe estimée à "
            "1 h, plan B : poste de prêt et lecture du disque."
        ),
    ),
    Dossier(
        key="D2",
        title="Impression impossible à l'accueil",
        request=(
            "« L'imprimante ne veut plus rien savoir depuis la mise à jour de vendredi, c'est la faute du nouveau "
            "logiciel. » — Karim Benali, accueil de l'agence Horizon (fictive), mardi 10 h 40."
        ),
        questions=(
            ("Quel message voyez-vous ?", "« Imprimante hors ligne » dans Windows."),
            ("Les autres postes impriment-ils sur la même imprimante ?", "Oui, la comptabilité imprime."),
            ("Depuis quand exactement ?", "Lundi matin ; vendredi après-midi cela fonctionnait."),
            ("L'imprimante affiche-t-elle quelque chose ?", "Prête, pas d'erreur."),
            ("Est-ce à chaque impression ?", "Oui, aucun document ne sort depuis ce poste."),
        ),
        fiche=(
            ("numero", "INT-2610-021"),
            ("date", "Mardi, 10 h 40"),
            ("demandeur", "K. Benali, accueil, poste 201"),
            ("inventaire", "PC-ACC-01 ; imprimante IMP-01 (laser réseau)"),
            ("emplacement", "Accueil, rez-de-chaussée"),
            ("contexte", "Windows 11 mis à jour vendredi ; imprimante réseau 192.168.1.40"),
            ("symptomes", "« Imprimante hors ligne » sur PC-ACC-01 ; IMP-01 « Prête » ; la comptabilité imprime"),
            ("apparition", "Depuis lundi matin, à chaque essai (reproductible)"),
            ("changements", "Mise à jour Windows vendredi"),
            ("utilisateurs", "Un poste ; contournement : imprimer depuis la comptabilité"),
            ("impact", "Faible : un poste, contournement possible"),
            ("urgence", "Moyenne : devis clients à remettre dans la journée"),
            ("priorite", "P4 basse"),
            ("sauvegarde", "Sans objet : aucune donnée modifiée"),
            ("confidentialite", "Documents clients dans la file d'attente : ne pas les ouvrir"),
            ("autorisation", "Réinstallation du pilote acceptée ; risque : aucun"),
            ("reformulation", "« Votre poste ne voit plus l'imprimante depuis lundi, les autres postes oui. »"),
            ("criteres", "Une page de test sort depuis PC-ACC-01 ; un devis s'imprime ; la file d'attente est vide"),
            ("plan", "Vérifier le port et l'adresse de l'imprimante sur le poste, puis le pilote ; tester"),
            ("escalade", "Non"),
        ),
        observations=("« Imprimante hors ligne » sur un seul poste", "imprimante « Prête »", "la comptabilité imprime"),
        hypotheses=("« le nouveau logiciel » (avis du demandeur)", "port d'imprimante ou adresse changés", "pilote remplacé par la mise à jour"),
        occurrence=REPRODUCIBLE,
        impact=LOW,
        urgency=MEDIUM,
        situation=Situation(),
        criteria=(
            "Une page de test sort depuis PC-ACC-01.",
            "Un devis client s'imprime en entier.",
            "La file d'attente du poste est vide.",
        ),
        tasks=(("Contrôler port et adresse de l'imprimante", 15), ("Réinstaller le pilote si besoin", 20),
               ("Tests d'impression", 10)),
        conclusion=(
            "Demande qualifiée P4 (impact faible grâce au contournement, urgence moyenne) : un seul poste voit "
            "l'imprimante hors ligne depuis la mise à jour, l'imprimante et les autres postes fonctionnent. La "
            "panne est donc côté poste (port, adresse ou pilote), pas côté imprimante. Intervention directe "
            "estimée à 1 h ; en attendant, impression depuis la comptabilité."
        ),
    ),
    Dossier(
        key="D3",
        title="Lenteur du portable d'un commercial",
        request=(
            "« Mon portable rame, il a un virus c'est sûr, il faut tout réinstaller avant jeudi. » — Marc Thiry, "
            "commercial de la société Valtec (fictive), mercredi 14 h."
        ),
        questions=(
            ("Qu'est-ce qui est lent : le démarrage, un logiciel, Internet ?", "Surtout l'ouverture de session et Outlook."),
            ("Depuis quand ?", "Depuis une dizaine de jours."),
            ("Qu'avez-vous installé récemment ?", "Un logiciel de démonstration reçu d'un client."),
            ("Avez-vous vu un message d'alerte ou des fenêtres étranges ?", "Non, aucun message."),
            ("Vos fichiers sont-ils synchronisés quelque part ?", "Mes offres sont sur le portable seulement."),
        ),
        fiche=(
            ("numero", "INT-2610-033"),
            ("date", "Mercredi, 14 h"),
            ("demandeur", "M. Thiry, commercial, GSM professionnel"),
            ("inventaire", "LT-COM-07, portable 15 pouces"),
            ("emplacement", "Itinérant, passe au bureau le mercredi"),
            ("contexte", "Windows 11, Outlook, VPN, Wi-Fi"),
            ("symptomes", "Ouverture de session en 6 min (1 min avant), Outlook lent ; aucun message d'alerte"),
            ("apparition", "Depuis environ 10 jours, à chaque démarrage (reproductible)"),
            ("changements", "Logiciel de démonstration installé il y a 10 jours"),
            ("utilisateurs", "Une personne"),
            ("impact", "Faible : une personne, travail possible"),
            ("urgence", "Moyenne : rendez-vous client jeudi"),
            ("priorite", "P4 basse"),
            ("sauvegarde", "Offres uniquement sur le portable : copie à faire avant toute action"),
            ("confidentialite", "Offres commerciales confidentielles : copie sur support chiffré de l'entreprise"),
            ("autorisation", "Désinstallation du logiciel de démonstration acceptée ; réinstallation complète refusée sans nouvel accord"),
            ("reformulation", "« Depuis l'installation du logiciel de démonstration, votre session et Outlook sont devenus très lents. »"),
            ("criteres", "Ouverture de session en moins de 2 min ; Outlook ouvert en moins de 30 s ; offres intactes"),
            ("plan", "Sauvegarder les offres ; mesurer le démarrage ; examiner programmes au démarrage et analyse antivirus ; retirer le logiciel en cause"),
            ("escalade", "Non, sauf si l'analyse antivirus détecte une menace"),
        ),
        observations=("session en 6 min au lieu de 1 min", "Outlook lent", "aucun message d'alerte", "logiciel installé il y a 10 jours"),
        hypotheses=("« virus » (avis du demandeur)", "logiciel de démonstration lancé au démarrage", "disque presque plein"),
        occurrence=REPRODUCIBLE,
        impact=LOW,
        urgency=MEDIUM,
        situation=Situation(),
        criteria=(
            "Ouverture de session en moins de 2 minutes (mesurée).",
            "Outlook s'ouvre en moins de 30 secondes.",
            "Les offres du demandeur sont présentes et lisibles.",
        ),
        tasks=(("Copier les offres sur support chiffré", 20), ("Mesurer, examiner démarrage et antivirus", 30),
               ("Retirer le logiciel en cause, redémarrer, mesurer", 25)),
        conclusion=(
            "Demande qualifiée P4 (une personne, rendez-vous jeudi) : lenteur reproductible apparue avec un "
            "logiciel installé il y a dix jours, sans alerte. « Virus » et « tout réinstaller » ne sont que des "
            "avis : on sauvegarde d'abord, on mesure, on retire la cause probable. Réinstallation seulement sur "
            "nouvel accord écrit. Estimation 1 h 45."
        ),
    ),
    Dossier(
        key="D4",
        title="Dossier partagé inaccessible pour toute la comptabilité",
        request=(
            "« Plus personne n'arrive à ouvrir le dossier Compta, les salaires doivent partir à midi ! » — "
            "Nadia Rossi, responsable administrative de la PME Belmat (fictive), jeudi 9 h 20."
        ),
        questions=(
            ("Que se passe-t-il quand vous ouvrez le dossier ?", "« Accès refusé » pour les trois comptables."),
            ("Les autres dossiers du serveur s'ouvrent-ils ?", "Oui, le dossier Commercial s'ouvre."),
            ("Quelque chose a-t-il changé ?", "Le prestataire a « réorganisé les droits » hier soir."),
            ("Depuis quand ?", "Ce matin, à chaque tentative."),
            ("Qui gère le serveur ?", "Le prestataire ; nous n'avons pas le mot de passe administrateur."),
        ),
        fiche=(
            ("numero", "INT-2610-040"),
            ("date", "Jeudi, 9 h 20"),
            ("demandeur", "N. Rossi, administration, poste 300"),
            ("inventaire", "Serveur SRV-01, partage \\\\SRV-01\\Compta"),
            ("emplacement", "Local technique, 1er étage"),
            ("contexte", "Windows Server géré par le prestataire ; postes Windows 11 du groupe Compta"),
            ("symptomes", "« Accès refusé » sur \\\\SRV-01\\Compta pour 3 comptables ; dossier Commercial accessible"),
            ("apparition", "Jeudi matin, à chaque tentative (reproductible)"),
            ("changements", "Droits réorganisés par le prestataire mercredi soir"),
            ("utilisateurs", "Tout le service comptabilité (3 personnes)"),
            ("impact", "Élevé : un service entier bloqué"),
            ("urgence", "Élevée : salaires à envoyer à midi"),
            ("priorite", "P1 critique"),
            ("sauvegarde", "Sauvegarde du serveur gérée par le prestataire"),
            ("confidentialite", "Données salariales : ne pas ouvrir les fichiers ; aucun droit élargi « pour tester »"),
            ("autorisation", "Aucun droit d'administration du serveur : modification interdite"),
            ("reformulation", "« Depuis la réorganisation d'hier soir, les trois comptables reçoivent Accès refusé sur Compta ; les salaires partent à midi. »"),
            ("criteres", "Les trois comptables ouvrent et enregistrent dans Compta ; aucun autre service n'y accède"),
            ("plan", "Relever les messages et comptes touchés, vérifier l'appartenance au groupe Compta, transmettre au prestataire"),
            ("escalade", "Oui : prestataire (administration du serveur), appel immédiat + fiche écrite"),
        ),
        observations=("« Accès refusé » pour trois comptables", "dossier Commercial accessible", "droits réorganisés la veille"),
        hypotheses=("groupe Compta retiré des permissions", "comptes retirés du groupe", "refus ajouté par erreur"),
        occurrence=REPRODUCIBLE,
        impact=HIGH,
        urgency=HIGH,
        situation=Situation(autorisation=False),
        criteria=(
            "Les trois comptables ouvrent et enregistrent un fichier dans Compta.",
            "Un compte d'un autre service n'ouvre toujours pas Compta.",
            "La responsable confirme l'envoi des salaires.",
        ),
        tasks=(("Relever messages, comptes et groupe", 15), ("Rédiger la fiche d'escalade et appeler", 15),
               ("Contrôler les accès après correction", 15)),
        conclusion=(
            "Demande qualifiée P1 (service entier bloqué, échéance à midi) : refus d'accès reproductible depuis "
            "la réorganisation des droits. Je n'ai aucun droit d'administration du serveur : j'escalade "
            "immédiatement au prestataire avec les faits relevés, sans élargir les droits « pour tester ». Je "
            "contrôle ensuite les critères avec les comptables."
        ),
    ),
    Dossier(
        key="D5",
        title="Wi-Fi qui coupe dans la salle de réunion",
        request=(
            "« Le Wi-Fi est nul dans la grande salle, les visios coupent tout le temps. » — Thomas Leroy, gérant de "
            "l'agence Atlas (fictive), vendredi 16 h."
        ),
        questions=(
            ("Qu'est-ce qui coupe : la vidéo, le son, toute la connexion ?", "L'image se fige quelques secondes, puis repart."),
            ("Est-ce à chaque réunion ?", "Non, certaines réunions seulement, plutôt vers midi."),
            ("Est-ce le même problème ailleurs dans l'agence ?", "Non, au bureau ça va."),
            ("Combien de personnes sont connectées pendant ces réunions ?", "Une dizaine, avec les invités."),
            ("Quelque chose a-t-il changé ?", "Une cuisine avec un four à micro-ondes a été installée à côté il y a un mois."),
        ),
        fiche=(
            ("numero", "INT-2610-052"),
            ("date", "Vendredi, 16 h"),
            ("demandeur", "T. Leroy, gérant, GSM"),
            ("inventaire", "Point d'accès AP-02, réseau ATLAS-PRO"),
            ("emplacement", "Grande salle de réunion, 1er étage"),
            ("contexte", "Portables Windows 11 et smartphones ; visioconférence ; Wi-Fi 2,4 et 5 GHz"),
            ("symptomes", "Image figée quelques secondes en visio dans la grande salle ; pas ailleurs"),
            ("apparition", "Certaines réunions, plutôt vers midi, depuis environ un mois (intermittente)"),
            ("changements", "Cuisine avec micro-ondes installée à côté de la salle il y a un mois"),
            ("utilisateurs", "Participants des réunions de la grande salle (jusqu'à 10)"),
            ("impact", "Moyen : plusieurs personnes, réunions clients"),
            ("urgence", "Faible : prochaine réunion importante dans deux semaines"),
            ("priorite", "P4 basse"),
            ("sauvegarde", "Sans objet : configuration du point d'accès sauvegardée avant tout réglage"),
            ("confidentialite", "Aucun accès aux portables des participants"),
            ("autorisation", "Réglage de AP-02 accepté par le gérant ; achat éventuel sur devis"),
            ("reformulation", "« Dans la grande salle seulement, certaines visios se figent, plutôt vers midi, depuis l'arrivée de la cuisine. »"),
            ("criteres", "Signal −67 dBm ou mieux dans la salle ; une visio de 30 min vers midi sans coupure"),
            ("plan", "Journal des coupures (date, heure, bande) ; relevé du signal et des canaux à midi ; passer les clients en 5 GHz ; retester"),
            ("escalade", "Non ; devis au gérant si un point d'accès supplémentaire est nécessaire"),
        ),
        observations=("image figée quelques secondes", "dans la grande salle seulement", "plutôt vers midi", "micro-ondes installé à côté"),
        hypotheses=("« Wi-Fi nul » (avis du demandeur)", "interférence du micro-ondes en 2,4 GHz", "trop de clients sur le point d'accès"),
        occurrence=INTERMITTENT,
        impact=MEDIUM,
        urgency=LOW,
        situation=Situation(),
        criteria=(
            "Signal mesuré à −67 dBm ou mieux aux places de la salle.",
            "Une visioconférence de 30 minutes vers midi se déroule sans coupure.",
            "Le gérant valide le résultat.",
        ),
        tasks=(("Mettre en place un journal des coupures", 15), ("Relevé signal et canaux vers midi", 30),
               ("Régler AP-02 (5 GHz, canal) et retester", 30)),
        conclusion=(
            "Demande qualifiée P4 (impact moyen, urgence faible) : panne intermittente, localisée, corrélée à "
            "l'heure de midi et à l'arrivée d'un micro-ondes. On la rend observable (journal des coupures, "
            "relevé à midi) avant de régler le point d'accès ; le renvoi technique vers le cours Wi-Fi (PR25) "
            "sert pour le relevé. Estimation 1 h 45 ; achat seulement sur devis accepté."
        ),
    ),
)
DOSSIERS_BY_KEY = {d.key: d for d in DOSSIERS}


# =============================================================================================
# 10. Schémas
# =============================================================================================


def _cell(x: int, y: int, w: int, h: int, fill: str, lines: list[str], *, size: float = 12,
          weight: str = "400", data: str = "") -> str:
    attr = f' data-cell="{data}"' if data else ""
    top = y + h // 2 - (len(lines) - 1) * 7 + 4
    return (
        f'<rect{attr} x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{_STROKE}" stroke-width="1.5"/>'
        + _text_lines(x + w // 2, top, lines, size=size, weight=weight, step=14, anchor="middle")
    )


def priority_matrix_svg(*, blanks: dict[tuple[int, int], str] | None = None) -> str:
    """Matrice 3 × 3 : lignes = impact (élevé → faible), colonnes = urgence (élevée → faible).
    Chaque case porte la priorité calculée par `priority` (ou un repère ① à compléter)."""
    blanks = blanks or {}
    head_w, cell_w, head_h, cell_h = 112, 92, 46, 48
    width, height = head_w + 3 * cell_w + 12, head_h + 3 * cell_h + 34
    parts = [
        _text_lines(head_w + 3 * cell_w // 2 + 6, 14, ["URGENCE →"], size=11.5, weight="700", anchor="middle"),
        _text_lines(8, head_h + 3 * cell_h + 26, ["↑ IMPACT (lignes)"], size=11.5, weight="700"),
    ]
    x0, y0 = 6, 20
    parts.append(_cell(x0, y0, head_w, head_h - 20, _SOFT, ["Impact \\ urgence"], size=11, weight="700"))
    for j, u in enumerate(LEVELS):
        parts.append(_cell(x0 + head_w + j * cell_w, y0, cell_w, head_h - 20, _SOFT, [URGENCY_LABELS[u]], weight="700"))
    for i, imp in enumerate(LEVELS):
        y = y0 + head_h - 20 + i * cell_h
        parts.append(_cell(x0, y, head_w, cell_h, _SOFT, [IMPACT_LABELS[imp]], weight="700"))
        for j, u in enumerate(LEVELS):
            p = priority(imp, u)
            mark = blanks.get((imp, u))
            if mark:
                parts.append(_cell(x0 + head_w + j * cell_w, y, cell_w, cell_h, "#ffffff", [mark], size=16,
                                   weight="700", data=f"{imp}-{u}"))
            else:
                parts.append(_cell(x0 + head_w + j * cell_w, y, cell_w, cell_h, _P_FILLS[p], PRIORITY_LABELS[p].split(" "),
                                   weight="700", data=f"{imp}-{u}"))
    return _svg(width, height, parts)


def _matrix_alt(blanks: dict[tuple[int, int], str] | None = None) -> str:
    blanks = blanks or {}
    rows = []
    for imp in LEVELS:
        cells = ", ".join(
            f"urgence {URGENCY_LABELS[u].lower()} : {blanks.get((imp, u)) or PRIORITY_LABELS[priority(imp, u)]}"
            for u in LEVELS
        )
        rows.append(f"impact {IMPACT_LABELS[imp].lower()} — {cells}")
    return "Matrice de priorité, lignes = impact, colonnes = urgence. " + " ; ".join(rows) + "."


def two_columns_svg(left_title: str, left: tuple[str, ...], right_title: str, right: tuple[str, ...],
                    marks: tuple[str, str] = ("O", "H")) -> str:
    """Deux colonnes de phrases ; chaque phrase est précédée d'une lettre (O, H) pour que la
    distinction ne repose pas sur la couleur."""
    width, col_w, top = 400, 192, 56
    wrapped_l = [_wrap(t, 26) for t in left]
    wrapped_r = [_wrap(t, 26) for t in right]
    def col_height(items: list[list[str]]) -> int:
        return sum(14 * len(w) + 12 for w in items)
    height = top + max(col_height(wrapped_l), col_height(wrapped_r)) + 10
    parts: list[str] = []
    for c, (title, items, mark, fill) in enumerate(
        ((left_title, wrapped_l, marks[0], "#e9f5ec"), (right_title, wrapped_r, marks[1], "#fff3c4"))
    ):
        x = 6 + c * (col_w + 4)
        parts.append(
            f'<rect x="{x}" y="4" width="{col_w}" height="{height - 8}" rx="8" fill="{fill}" stroke="{_STROKE}" '
            f'stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x + col_w // 2, 20, _wrap(title, 22), size=12, weight="700", step=14, anchor="middle"))
        y = top + 12
        for lines in items:
            parts.append(f'<text x="{x + 8}" y="{y}" font-size="12" font-weight="700">{mark}</text>')
            parts.append(_text_lines(x + 24, y, lines, size=11.5, step=14))
            y += 14 * len(lines) + 12
    return _svg(width, height, parts)


def form_svg() -> str:
    """Fiche d'incident vierge : six sections, une ligne par rubrique (« * » = obligatoire)."""
    width, line_h, sec_h = 400, 22, 24
    parts: list[str] = []
    y = 6
    for section in SECTIONS:
        parts.append(
            f'<rect x="6" y="{y}" width="{width - 12}" height="{sec_h}" fill="#dbe4f3" stroke="{_STROKE}" stroke-width="1.5"/>'
            + _text_lines(14, y + 16, [section], size=12, weight="700")
        )
        y += sec_h
        for f in (f for f in INCIDENT_FIELDS if f.section == section):
            star = " *" if f.required else ""
            parts.append(
                f'<rect x="6" y="{y}" width="{width - 12}" height="{line_h}" fill="#ffffff" stroke="{_STROKE}" stroke-width="1"/>'
                + _text_lines(14, y + 15, [f"{f.label}{star}"], size=11)
                + f'<path d="M230 {y + 16} H{width - 14}" stroke="#9aa5b8" stroke-width="1" stroke-dasharray="3 3"/>'
            )
            y += line_h
        y += 6
    parts.append(_text_lines(8, y + 10, ["* rubrique obligatoire"], size=10.5))
    return _svg(width, y + 16, parts)


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


def _tree_alt(checks: tuple[tuple[str, str, str], ...], final: str) -> str:
    return "Arbre d'escalade : " + " ; ".join(
        f"{i}. {what} ? Si non : {action}" for i, (_k, what, action) in enumerate(checks, start=1)
    ) + f" Si tout est oui : {final}"


ANALYSIS_FIGURE = _proc_figure("pr26-procedure-analyse", 1, PROCEDURES[0][0], ANALYSIS_STEPS,
                               "De la demande brute à la décision : chaque étape laisse une trace sur la fiche.")
INTERVIEW_FIGURE = _proc_figure("pr26-procedure-entretien", 2, PROCEDURES[1][0], INTERVIEW_STEPS,
                                "Écouter d'abord, questions ouvertes puis fermées, reformuler jusqu'à accord.")
ESCALATION_PROC_FIGURE = _proc_figure("pr26-procedure-escalade", 3, PROCEDURES[2][0], ESCALATION_STEPS,
                                      "Escalader n'est pas abandonner : on transmet des faits et on suit la demande.")
MATRIX_FIGURE = Figure(
    key="pr26-matrice-priorite",
    title="Matrice de priorité impact × urgence",
    alt=_matrix_alt(),
    caption="Convention du cours : la priorité se lit au croisement de l'impact (ligne) et de l'urgence (colonne).",
    svg=priority_matrix_svg(),
)
OBS_FIGURE = Figure(
    key="pr26-observation-hypothese",
    title="Observation ou hypothèse",
    alt=(
        "Deux colonnes. Observations (O) : "
        + " ; ".join(t for t, k in STATEMENTS if k == OBSERVATION)
        + ". Hypothèses ou interprétations (H) : "
        + " ; ".join(t for t, k in STATEMENTS if k == HYPOTHESIS)
        + "."
    ),
    caption="Une observation se vérifie (on peut la constater) ; une hypothèse s'explique et se teste ensuite.",
    svg=two_columns_svg(
        OBSERVATION, tuple(t for t, k in STATEMENTS if k == OBSERVATION),
        HYPOTHESIS, tuple(t for t, k in STATEMENTS if k == HYPOTHESIS),
    ),
)
ESCALATION_FIGURE = Figure(
    key="pr26-arbre-escalade",
    title="Arbre d'escalade avant d'intervenir",
    alt=_tree_alt(ESCALATION_CHECKS, ESCALATION_FINAL),
    caption="On s'arrête au premier contrôle en échec : il désigne l'action et le destinataire de l'escalade.",
    svg=decision_tree_svg(tuple((what, action) for _k, what, action in ESCALATION_CHECKS), ESCALATION_FINAL),
)
FORM_FIGURE = Figure(
    key="pr26-fiche-incident",
    title="Fiche d'incident vierge",
    alt=(
        "Fiche d'incident en six sections : "
        + " ; ".join(
            f"{s} : " + ", ".join(f.label + (" (obligatoire)" if f.required else "") for f in INCIDENT_FIELDS if f.section == s)
            for s in SECTIONS
        )
        + "."
    ),
    caption="Formulaire type à recopier sur la copie d'examen : une rubrique vide se voit tout de suite.",
    svg=form_svg(),
)

PR26_FIGURES: tuple[Figure, ...] = (
    ANALYSIS_FIGURE,
    INTERVIEW_FIGURE,
    ESCALATION_PROC_FIGURE,
    MATRIX_FIGURE,
    OBS_FIGURE,
    ESCALATION_FIGURE,
    FORM_FIGURE,
)

# Schémas à compléter (exercices), servis en fichiers statiques comme PR18 à PR25 ------------

MATRIX_BLANKS: dict[tuple[int, int], str] = {(HIGH, MEDIUM): "①", (MEDIUM, MEDIUM): "②", (LOW, HIGH): "③",
                                             (MEDIUM, LOW): "④"}
MATRIX_BLANK_ANSWERS: dict[str, str] = {mark: PRIORITY_LABELS[priority(*cell)] for cell, mark in MATRIX_BLANKS.items()}
MATRIX_BLANK_FIGURE = Figure(
    key="pr26-matrice-a-completer",
    title="Matrice de priorité à compléter",
    alt=_matrix_alt(MATRIX_BLANKS),
    caption="Schéma à compléter : priorités des cases ①, ②, ③ et ④.",
    svg=priority_matrix_svg(blanks=MATRIX_BLANKS),
)

TREE_BLANK_KEYS: tuple[str, ...] = (E_SECURITY, E_AUTH, E_DATA, E_BUDGET)
TREE_BLANKS: dict[str, str] = {k: m for k, m in zip(TREE_BLANK_KEYS, ("①", "②", "③", "④"), strict=True)}
TREE_BLANK_ANSWERS: dict[str, str] = {
    TREE_BLANKS[k]: action for k, _q, action in ESCALATION_CHECKS if k in TREE_BLANKS
}
_TREE_BLANK_CHECKS = tuple((k, q, TREE_BLANKS.get(k, a)) for k, q, a in ESCALATION_CHECKS)
TREE_BLANK_FIGURE = Figure(
    key="pr26-escalade-a-completer",
    title="Arbre d'escalade à compléter",
    alt=_tree_alt(_TREE_BLANK_CHECKS, ESCALATION_FINAL),
    caption="Schéma à compléter : action à mener en ①, ②, ③ et ④ quand le contrôle échoue.",
    svg=decision_tree_svg(tuple((q, a) for _k, q, a in _TREE_BLANK_CHECKS), ESCALATION_FINAL),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (MATRIX_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr26-matrice-a-completer.svg"),
    (TREE_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr26-escalade-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR25)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )

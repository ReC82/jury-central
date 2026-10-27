"""PR29 « Contrôles finaux et rapport professionnel d'intervention » — règles du cours, cinq
rapports modèles, schémas et formulaires imprimables (ticket #228).

Ce cours est un cours de **méthode écrite** (exigence AP-16 « vocabulaire technique » et
complément AP-C01 « rédiger une réponse écrite de technicien ») : il ne porte pas de nouvelles
valeurs techniques, mais les **règles de clôture** d'une intervention qu'un dossier d'examen
applique et qu'un correcteur vérifie. Elles sont écrites ici une seule fois, sous forme de
données et de fonctions testées, et réutilisées par le cours, les exercices, le mini-examen,
les schémas et les formulaires :

- `CHECK_FAMILIES` / `required_checks` / `missing_checks` : les six familles de contrôles
  finaux (fonctionnel, stabilité, performance, réseau local et Internet, sécurité, pilote et
  périphérique) et celles qu'exige chaque type d'intervention ;
- `Criterion` / `assess` / `verdict` : critères d'acceptation mesurés **avant / après**,
  résultat atteint, non atteint ou **non concluant**, verdict d'ensemble ;
- `decision` / `DECISION_TREE` : valider et faire signer, retour arrière, escalade ou réserve ;
- `JournalEntry` / `journal_issues` : journal des opérations (ordre, résultat vérifiable) ;
- `REPRO_FIELDS` / `repro_missing` : test reproductible ;
- `REPORT_FIELDS` / `missing_report_fields` / `sensitive_lines` : compte rendu structuré et
  données à ne jamais y écrire ;
- `REPORT_GRID` / `report_score` : grille d'évaluation d'un rapport sur 20 ;
- `MESSAGES` : communication au client (adaptée, trop technique, trompeuse) ;
- `DOC_TARGETS` : où se documente chaque information ;
- `REPORTS` : cinq rapports modèles complets (PC, système, RJ45, réseau, partage) dont les
  résultats, le verdict et la décision sont **calculés et contrôlés**.

Les schémas sont construits en SVG depuis ces données (aucune image générée), comme PR18 à
PR28. Les personnes, entreprises, numéros d'inventaire et relevés sont fictifs.
"""

import re
from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr27_figures import Tree
from app.v1.ampcr_pratique_pr28_figures import _blank_tree, checklist_svg, do_dont_svg
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
PRINT_DIR_REF = "print/ampcr-pratique"
_STROKE = "#33415c"
_SOFT = "#f4f6fb"

# =============================================================================================
# 1. Les six familles de contrôles finaux
# =============================================================================================


@dataclass(frozen=True)
class CheckFamily:
    key: str
    name: str
    question: str  # ce que la famille prouve
    tests: tuple[str, ...]  # exemples de tests concrets
    evidence: str  # ce qu'on écrit dans le rapport


CHECK_FAMILIES: tuple[CheckFamily, ...] = (
    CheckFamily(
        "fonctionnel", "Test fonctionnel",
        "Le symptôme de départ a-t-il disparu, dans les conditions où il apparaissait ?",
        ("refaire l'action qui provoquait la panne", "faire essayer l'utilisateur sur sa tâche habituelle"),
        "test refait, conditions, résultat observé",
    ),
    CheckFamily(
        "stabilite", "Stabilité",
        "Le résultat tient-il dans la durée, sous charge et après redémarrage ?",
        ("test de charge de 30 minutes", "trois redémarrages successifs", "journal système relu sans nouvelle erreur"),
        "durée du test, nombre de redémarrages, erreurs du journal",
    ),
    CheckFamily(
        "performance", "Performance",
        "La mesure chiffrée atteint-elle le critère, comparée à l'état avant ?",
        ("temps de démarrage jusqu'au bureau", "débit ou vitesse de liaison", "température en charge"),
        "valeur avant, valeur après, critère",
    ),
    CheckFamily(
        "reseau", "Réseau local et Internet",
        "Le poste communique-t-il avec le réseau local, la passerelle et Internet ?",
        ("ping de la passerelle", "résolution d'un nom (nslookup)", "ouverture d'un site et d'une ressource partagée"),
        "commandes, adresses, pertes, résultats",
    ),
    CheckFamily(
        "securite", "Sécurité",
        "Le poste est-il rendu aussi sûr qu'avant, ou plus ?",
        ("antivirus actif et à jour", "pare-feu actif, mises à jour faites", "compte technique temporaire supprimé",
         "capot fermé, câbles rangés hors du passage"),
        "protections vérifiées, comptes, remise en état",
    ),
    CheckFamily(
        "pilote", "Pilote et périphérique",
        "Chaque périphérique utile est-il reconnu, avec le bon pilote ?",
        ("Gestionnaire de périphériques sans erreur", "page de test de l'imprimante", "écran, clavier, souris, webcam essayés"),
        "périphériques essayés, version du pilote",
    ),
)
CHECKS_BY_KEY = {f.key: f for f in CHECK_FAMILIES}
CHECK_NAMES = tuple(f.name for f in CHECK_FAMILIES)

K_HW = "Remplacement d'une pièce matérielle"
K_OS = "Réinstallation ou réparation du système"
K_CABLE = "Pose ou réparation d'un câblage"
K_NET = "Configuration ou dépannage réseau"
K_SHARE = "Partage, comptes et droits"
K_DEVICE = "Installation d'un pilote ou d'un périphérique"
INTERVENTION_KINDS = (K_HW, K_OS, K_CABLE, K_NET, K_SHARE, K_DEVICE)

# Convention du cours : familles exigées par type d'intervention (le test fonctionnel et la
# sécurité sont toujours exigés).
_REQUIRED: dict[str, tuple[str, ...]] = {
    K_HW: ("fonctionnel", "stabilite", "performance", "securite"),
    K_OS: ("fonctionnel", "performance", "reseau", "securite", "pilote"),
    K_CABLE: ("fonctionnel", "performance", "reseau", "securite"),
    K_NET: ("fonctionnel", "stabilite", "reseau", "securite"),
    K_SHARE: ("fonctionnel", "reseau", "securite"),
    K_DEVICE: ("fonctionnel", "securite", "pilote"),
}


def required_checks(kind: str) -> tuple[CheckFamily, ...]:
    """Familles de contrôles exigées pour un type d'intervention, dans l'ordre du cours."""
    if kind not in _REQUIRED:
        raise ValueError(f"Type d'intervention inconnu : {kind}")
    return tuple(f for f in CHECK_FAMILIES if f.key in _REQUIRED[kind])


def missing_checks(kind: str, done: frozenset[str]) -> tuple[CheckFamily, ...]:
    return tuple(f for f in required_checks(kind) if f.key not in done)


# =============================================================================================
# 2. Critères d'acceptation avant / après
# =============================================================================================

MET = "atteint"
NOT_MET = "non atteint"
INCONCLUSIVE = "non concluant"
RESULTS = (MET, NOT_MET, INCONCLUSIVE)


@dataclass(frozen=True)
class Criterion:
    label: str
    op: str  # "<=" | ">=" | "="
    target: float | str
    unit: str = ""

    def text(self) -> str:
        sign = {"<=": "≤", ">=": "≥", "=": "="}[self.op]
        return f"{self.label} {sign} {fmt(self.target)}{(' ' + self.unit) if self.unit else ''}"


def fmt(value: float | str | None) -> str:
    if value is None:
        return "non mesuré"
    if isinstance(value, str):
        return value
    if float(value).is_integer():
        return f"{int(value)}"
    return f"{value:.2f}".rstrip("0").replace(".", ",")


def assess(criterion: Criterion, value: float | str | None) -> str:
    """Résultat d'un critère pour une valeur mesurée ; `None` = mesure absente ou impossible
    → non concluant (on ne conclut pas sans preuve)."""
    if value is None:
        return INCONCLUSIVE
    if criterion.op == "=":
        return MET if value == criterion.target else NOT_MET
    if isinstance(value, str) or isinstance(criterion.target, str):
        raise TypeError("Comparaison ≤ / ≥ sur une valeur non numérique.")
    ok = value <= criterion.target if criterion.op == "<=" else value >= criterion.target
    return MET if ok else NOT_MET


V_VALID = "Validé : tous les critères sont atteints"
V_REJECT = "Non validé : au moins un critère n'est pas atteint"
V_RESERVE = "Validation avec réserve : un résultat n'est pas concluant"
VERDICTS = (V_VALID, V_REJECT, V_RESERVE)


def verdict(results: tuple[str, ...]) -> str:
    """Un critère non atteint l'emporte ; sinon un résultat non concluant impose une réserve."""
    if not results:
        raise ValueError("Aucun critère : on ne valide pas sans critère d'acceptation.")
    if NOT_MET in results:
        return V_REJECT
    if INCONCLUSIVE in results:
        return V_RESERVE
    return V_VALID


D_SIGN = "Faire constater le résultat, faire signer la réception et remettre le rapport"
D_ROLLBACK = "Retour arrière vers l'état initial sauvegardé, puis vérification de cet état"
D_ESCALATE = "Escalader (niveau 2, fabricant ou prestataire) avec les relevés, sans déclarer réparé"
D_FOLLOWUP = "Réserve écrite au rapport, test complémentaire planifié, client informé"
DECISIONS = (D_SIGN, D_ROLLBACK, D_ESCALATE, D_FOLLOWUP)


def decision(result: str, *, rollback_ready: bool) -> str:
    """Suite à donner au verdict : le retour arrière n'est possible que s'il a été préparé
    (état initial noté, sauvegarde ou point de restauration)."""
    if result == V_VALID:
        return D_SIGN
    if result == V_RESERVE:
        return D_FOLLOWUP
    if result == V_REJECT:
        return D_ROLLBACK if rollback_ready else D_ESCALATE
    raise ValueError(f"Verdict inconnu : {result}")


# Critère bien ou mal formulé (exercices) : un critère d'acceptation est mesurable.
MEASURABLE = "Critère mesurable (on peut le vérifier et l'écrire)"
VAGUE = "Critère vague (impossible à prouver)"
CRITERIA_STATEMENTS: tuple[tuple[str, str], ...] = (
    ("Démarrage jusqu'au bureau en 60 s au plus, chronométré", MEASURABLE),
    ("Le PC marche mieux qu'avant", VAGUE),
    ("Ping de la passerelle : 0 % de pertes sur 50 paquets", MEASURABLE),
    ("Internet a l'air rapide", VAGUE),
    ("Testeur de câble : 8 fils conformes, dans l'ordre", MEASURABLE),
    ("Le client est content", VAGUE),
    ("Aucun arrêt pendant 30 minutes de test de charge", MEASURABLE),
    ("L'imprimante devrait fonctionner", VAGUE),
    ("La comptable ouvre et enregistre un fichier du dossier Compta", MEASURABLE),
    ("Tout est en ordre", VAGUE),
)

# =============================================================================================
# 3. Arbre de décision de fin d'intervention
# =============================================================================================

DECISION_TREE = Tree(
    key="cloture",
    title="Clôturer une intervention",
    start="L'action est faite : peut-on rendre le poste et déclarer la demande résolue ?",
    questions=(
        ("Tous les contrôles exigés pour ce type d'intervention ont-ils été faits ?",
         "Faire les contrôles manquants avant toute conclusion ; ne rien déclarer réparé."),
        ("Tous les critères mesurés sont-ils atteints ?",
         "Retour arrière si l'état initial a été sauvegardé, sinon escalade avec les relevés."),
        ("Tous les résultats sont-ils concluants (aucune mesure manquante) ?",
         "Validation avec réserve écrite, test complémentaire planifié, client informé."),
        ("Le client a-t-il constaté le résultat et l'accepte-t-il ?",
         "Refaire le test devant lui ; noter son refus ou sa réserve sur le rapport."),
    ),
    final="Faire signer la réception, remettre le rapport, archiver la fiche et la documentation.",
)

# =============================================================================================
# 4. Journal des opérations et tests reproductibles
# =============================================================================================


@dataclass(frozen=True)
class JournalEntry:
    time: str  # « HH:MM »
    action: str
    result: str


VAGUE_RESULTS = frozenset({"ok", "fait", "ça marche", "bon", "vu", "réglé", "?"})


def _minutes(hhmm: str) -> int:
    if not re.fullmatch(r"\d{2}:\d{2}", hhmm):
        raise ValueError(f"Heure invalide : {hhmm}")
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def journal_issues(entries: tuple[JournalEntry, ...]) -> tuple[str, ...]:
    """Défauts d'un journal : ligne hors de l'ordre chronologique, résultat absent ou vague
    (« OK », « fait ») qui ne prouve rien. Numéros de ligne à partir de 1."""
    issues: list[str] = []
    times = [_minutes(entry.time) for entry in entries]
    for n, entry in enumerate(entries, start=1):
        if n > 1 and times[n - 1] < times[n - 2]:
            issues.append(f"Ligne {n} : heure antérieure à la ligne précédente (ordre chronologique)")
        if not entry.result.strip():
            issues.append(f"Ligne {n} : résultat absent")
        elif entry.result.strip().lower() in VAGUE_RESULTS:
            issues.append(f"Ligne {n} : résultat vague (« {entry.result.strip()} »), non vérifiable")
    return tuple(issues)


REPRO_FIELDS: tuple[tuple[str, str], ...] = (
    ("depart", "État de départ (poste, compte, branchements)"),
    ("outil", "Outil ou commande exacte"),
    ("etapes", "Étapes, dans l'ordre"),
    ("attendu", "Résultat attendu (le critère)"),
    ("obtenu", "Résultat obtenu, avec la valeur"),
    ("quand", "Date, heure et durée du test"),
)
REPRO_KEYS = tuple(k for k, _l in REPRO_FIELDS)
REPRO_LABELS = dict(REPRO_FIELDS)


def repro_missing(test: dict[str, str]) -> tuple[str, ...]:
    """Rubriques absentes d'un test pour qu'un collègue puisse le refaire à l'identique."""
    return tuple(REPRO_LABELS[k] for k in REPRO_KEYS if not (test.get(k) or "").strip())


# =============================================================================================
# 5. Le compte rendu structuré
# =============================================================================================


@dataclass(frozen=True)
class ReportField:
    key: str
    section: str
    label: str
    content: str  # ce qu'on y écrit


S_IDENT, S_REQUEST, S_ANALYSIS, S_WORK, S_VALID, S_NEXT = (
    "1. Identification", "2. Demande et symptômes", "3. Analyse", "4. Intervention",
    "5. Contrôles et validation", "6. Suite et accord",
)
REPORT_FIELDS: tuple[ReportField, ...] = (
    ReportField("reference", S_IDENT, "N° de demande, date, technicien", "retrouver et suivre l'intervention"),
    ReportField("equipement", S_IDENT, "Équipement (identité non sensible)",
                "n° d'inventaire, modèle, emplacement ; jamais de mot de passe ni de donnée personnelle"),
    ReportField("demande", S_REQUEST, "Demande", "ce que le demandeur a demandé, reformulé et validé"),
    ReportField("symptomes", S_REQUEST, "Symptômes", "faits observés, mots exacts du message"),
    ReportField("hypotheses", S_ANALYSIS, "Hypothèses", "causes possibles, de la plus probable à la moins probable"),
    ReportField("releves", S_ANALYSIS, "Relevés", "mesures et constats avant toute action (valeurs, unités)"),
    ReportField("tests", S_ANALYSIS, "Tests", "tests de diagnostic faits, reproductibles"),
    ReportField("resultats", S_ANALYSIS, "Résultats", "ce que chaque test a montré ; cause retenue"),
    ReportField("action", S_WORK, "Action réalisée", "ce qui a été fait, une modification à la fois"),
    ReportField("pieces", S_WORK, "Pièces et logiciels", "pièce posée (référence, n° de série), pièce retirée, licence"),
    ReportField("validation", S_VALID, "Validation", "contrôles finaux, critères avant / après, verdict"),
    ReportField("risques", S_VALID, "Risques résiduels et limites", "ce qui n'est pas garanti, résultat non concluant"),
    ReportField("recommandation", S_NEXT, "Recommandation", "conseil daté au client, suivi prévu"),
    ReportField("signature", S_NEXT, "Signature et accord", "nom, date et signature du client à la réception"),
)
REPORT_KEYS = tuple(f.key for f in REPORT_FIELDS)
REPORT_BY_KEY = {f.key: f for f in REPORT_FIELDS}
REPORT_SECTIONS = tuple(dict.fromkeys(f.section for f in REPORT_FIELDS))


def missing_report_fields(filled: dict[str, str]) -> tuple[str, ...]:
    """Rubriques vides ou absentes d'un rapport, dans l'ordre du modèle (libellés)."""
    return tuple(f.label for f in REPORT_FIELDS if not (filled.get(f.key) or "").strip())


# Ce qui ne s'écrit jamais dans un rapport (données sensibles, secrets).
_SENSITIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("mot de passe", r"mot de passe\s*(?:[:=]|est|du client)"),
    ("code PIN", r"\bcode pin\b|\bpin\s*[:=]"),
    ("clé de récupération", r"clé de récupération\s*[:=]?\s*\d{6}"),
    ("numéro de carte bancaire", r"\b(?:\d{4}[ -]?){3}\d{4}\b"),
    ("contenu des fichiers personnels", r"(?:contenu|lu|consulté)[^.]*\b(?:courriels?|photos?|fichiers personnels)\b"),
)


def sensitive_lines(lines: tuple[str, ...]) -> tuple[tuple[int, str], ...]:
    """(numéro de ligne, nature) de chaque ligne qui expose une donnée sensible."""
    found: list[tuple[int, str]] = []
    for n, line in enumerate(lines, start=1):
        low = line.lower()
        for nature, pattern in _SENSITIVE_PATTERNS:
            if re.search(pattern, low):
                found.append((n, nature))
                break
    return tuple(found)


TO_WRITE = "À écrire dans le rapport"
NOT_TO_WRITE = "À ne jamais écrire dans le rapport"
REPORT_MENTIONS: tuple[tuple[str, str], ...] = (
    ("N° d'inventaire INV-0412 et modèle du PC", TO_WRITE),
    ("Mot de passe de session de l'utilisatrice", NOT_TO_WRITE),
    ("Message d'erreur exact recopié", TO_WRITE),
    ("Clé de récupération BitLocker de 48 chiffres", NOT_TO_WRITE),
    ("Référence et n° de série du SSD posé", TO_WRITE),
    ("Noms des photos de vacances vues dans le dossier Images", NOT_TO_WRITE),
    ("Valeurs mesurées avant et après, avec leur unité", TO_WRITE),
    ("Numéro de carte bancaire affiché dans le navigateur", NOT_TO_WRITE),
    ("Risque résiduel : batterie à 71 % de sa capacité d'origine", TO_WRITE),
    ("Avis personnel sur l'utilisateur (« pas très doué »)", NOT_TO_WRITE),
)

# =============================================================================================
# 6. Grille d'évaluation d'un rapport (sur 20)
# =============================================================================================

REPORT_GRID: tuple[tuple[str, str, int, str], ...] = (
    ("structure", "Structure complète", 3, "toutes les rubriques du modèle, dans l'ordre"),
    ("faits", "Faits et relevés", 3, "symptômes et relevés exacts, chiffrés, séparés des hypothèses"),
    ("demarche", "Démarche justifiée", 3, "hypothèses, tests reproductibles et résultats reliés"),
    ("action", "Action et pièces", 2, "action précise, pièces et références"),
    ("validation", "Validation mesurée", 4, "contrôles exigés, critères avant / après, verdict exact"),
    ("limites", "Limites et risques", 2, "risques résiduels et résultats non concluants dits clairement"),
    ("client", "Communication au client", 2, "message clair, non technique, recommandation datée"),
    ("confidentialite", "Confidentialité", 1, "aucune donnée sensible, identité de l'équipement non sensible"),
)
GRID_TOTAL = sum(points for _k, _l, points, _d in REPORT_GRID)
GRID_KEYS = tuple(k for k, *_r in REPORT_GRID)


def report_score(marks: dict[str, float]) -> float:
    """Note sur 20 : chaque critère est acquis (1), partiel (0,5) ou absent (0)."""
    if any(v not in (0, 0.5, 1) for v in marks.values()) or set(marks) - set(GRID_KEYS):
        raise ValueError("Critère inconnu ou niveau différent de 0, 0,5 ou 1.")
    return sum(points * marks.get(key, 0) for key, _l, points, _d in REPORT_GRID)


# =============================================================================================
# 7. Communication au client, escalade et documentation
# =============================================================================================

MSG_OK = "Adapté au client (clair, exact, utile)"
MSG_TECH = "Trop technique pour le client"
MSG_WRONG = "Inexact, trompeur ou déplacé"
MESSAGE_KINDS = (MSG_OK, MSG_TECH, MSG_WRONG)
MESSAGES: tuple[tuple[str, str], ...] = (
    ("Votre disque montrait des signes d'usure : je l'ai remplacé et vos documents ont été recopiés et vérifiés.", MSG_OK),
    ("Le SMART remontait des secteurs réalloués, j'ai cloné en dd vers un NVMe PCIe 4.0.", MSG_TECH),
    ("C'est réparé définitivement, cela ne se reproduira jamais.", MSG_WRONG),
    ("Le câble de votre bureau était mal raccordé ; il est refait et testé, la connexion est revenue à pleine vitesse.", MSG_OK),
    ("La paire 3-6 était croisée au 110, d'où un lien négocié en 100BASE-TX.", MSG_TECH),
    ("Vous avez sûrement cassé quelque chose en le déplaçant.", MSG_WRONG),
    ("Je n'ai pas pu vérifier la coupure du soir : je repasse jeudi pour un test, en attendant appelez-moi si elle revient.", MSG_OK),
    ("Le bail DHCP expirait à cause d'une étendue saturée sur le serveur.", MSG_TECH),
    ("Tout est parfait, le PC est comme neuf.", MSG_WRONG),
)

HANDOVER_DO: tuple[str, ...] = (
    "Dire ce qui a été fait en mots simples, sans sigle",
    "Montrer le test devant le client, sur sa propre tâche",
    "Dire ce qui n'est pas garanti et ce qui reste à surveiller",
    "Donner une recommandation datée et le moyen de rappeler",
    "Faire signer la réception, remettre une copie du rapport",
)
HANDOVER_DONT: tuple[str, ...] = (
    "Noyer le client sous le jargon pour paraître compétent",
    "Promettre que la panne ne reviendra jamais",
    "Accuser l'utilisateur ou un collègue",
    "Cacher un résultat non concluant ou un incident",
    "Partir sans faire constater le résultat",
)

DOC_REPORT = "Rapport d'intervention remis au client"
DOC_JOURNAL = "Journal des opérations de l'atelier"
DOC_KB = "Base de connaissances (fiche de solution)"
DOC_INVENTORY = "Inventaire du parc (fiche de l'équipement)"
DOC_TARGETS = (DOC_REPORT, DOC_JOURNAL, DOC_KB, DOC_INVENTORY)
DOC_ITEMS: tuple[tuple[str, str], ...] = (
    ("Verdict, risques résiduels et recommandation au client", DOC_REPORT),
    ("09:12 — pilote Wi-Fi 22.150 désinstallé ; carte absente du Gestionnaire", DOC_JOURNAL),
    ("Symptôme « imprimante hors ligne après mise à jour » : cause et solution qui a marché", DOC_KB),
    ("SSD posé : référence, n° de série, date de pose, garantie", DOC_INVENTORY),
    ("Signature de réception du client", DOC_REPORT),
    ("10:40 — retour au pilote 22.140 ; carte reconnue, ping 0 % de pertes", DOC_JOURNAL),
    ("Procédure de contournement d'un écran noir après mise à jour du firmware", DOC_KB),
    ("Nouvelle adresse IP fixe et nom du poste", DOC_INVENTORY),
)

# =============================================================================================
# 8. Procédures
# =============================================================================================

FINAL_STEPS: tuple[tuple[str, str], ...] = (
    ("Relire les critères", "Reprendre les critères d'acceptation écrits avant l'intervention."),
    ("Choisir les contrôles", "Familles exigées pour ce type d'intervention : aucune n'est oubliée."),
    ("Mesurer", "Refaire chaque mesure du « avant » dans les mêmes conditions, noter la valeur."),
    ("Comparer", "Chaque critère : atteint, non atteint ou non concluant ; verdict d'ensemble."),
    ("Décider", "Valider, retour arrière, escalade ou réserve, selon le verdict."),
    ("Faire constater", "Le client essaie sur sa tâche ; il signe la réception ou note sa réserve."),
)
ROLLBACK_STEPS: tuple[tuple[str, str], ...] = (
    ("Constater", "Le critère d'échec écrit à l'avance est atteint : on arrête de modifier."),
    ("Prévenir", "Informer le client ou le responsable : retour arrière, durée annoncée."),
    ("Restaurer", "Point de restauration, ancien pilote, configuration exportée, câblage photographié."),
    ("Vérifier l'état initial", "Refaire les tests du « avant » : le poste est revenu au point de départ."),
    ("Noter", "Journal : heure, ce qui a été restauré, résultat de la vérification."),
    ("Proposer la suite", "Autre solution, escalade ou commande de pièce ; rien n'est déclaré réparé."),
)
REPORT_STEPS: tuple[tuple[str, str], ...] = (
    ("Rassembler", "Fiche de demande, relevés, journal, résultats des contrôles, références des pièces."),
    ("Remplir les rubriques", "Une rubrique après l'autre, dans l'ordre du modèle, sans en sauter."),
    ("Séparer faits et hypothèses", "Valeurs et unités pour les faits, « hypothèse » écrit en toutes lettres."),
    ("Écrire la validation", "Critères avant / après, verdict, limites et risques résiduels."),
    ("Relire", "Aucune donnée sensible ; un collègue pourrait refaire chaque test."),
    ("Faire signer et archiver", "Signature du client, copie remise, documentation mise à jour."),
)
HANDOVER_STEPS: tuple[tuple[str, str], ...] = (
    ("Résumer", "Ce qui n'allait pas et ce qui a été fait, en deux phrases simples."),
    ("Montrer", "Le client refait sa tâche habituelle devant le technicien."),
    ("Prévenir", "Ce qui n'est pas garanti, ce qui reste à surveiller, le suivi prévu."),
    ("Conseiller", "Une recommandation concrète et datée (sauvegarde, remplacement prévu)."),
    ("Faire signer", "Réception signée, ou réserve notée avec les mots du client."),
)
PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Contrôles finaux avant de rendre le poste", FINAL_STEPS),
    ("Retour arrière après un contrôle en échec", ROLLBACK_STEPS),
    ("Rédiger le rapport d'intervention", REPORT_STEPS),
    ("Restituer au client", HANDOVER_STEPS),
)

# =============================================================================================
# 9. Les cinq rapports modèles complets
# =============================================================================================


@dataclass(frozen=True)
class Measure:
    criterion: Criterion
    before: float | str | None
    after: float | str | None

    @property
    def result(self) -> str:
        return assess(self.criterion, self.after)


@dataclass(frozen=True)
class Report:
    key: str
    theme: str
    title: str
    kind: str  # type d'intervention (contrôles exigés)
    context: str  # situation pour le cours
    fields: dict[str, str]  # rubriques du compte rendu (clés de REPORT_FIELDS, sauf « validation »)
    measures: tuple[Measure, ...]
    checks_done: frozenset[str]
    rollback_ready: bool
    journal: tuple[JournalEntry, ...]
    client_message: str

    @property
    def results(self) -> tuple[str, ...]:
        return tuple(m.result for m in self.measures)

    @property
    def verdict(self) -> str:
        return verdict(self.results)

    @property
    def decision(self) -> str:
        return decision(self.verdict, rollback_ready=self.rollback_ready)

    @property
    def missing_checks(self) -> tuple[CheckFamily, ...]:
        return missing_checks(self.kind, self.checks_done)

    def validation_text(self) -> str:
        checks = ", ".join(f.name.lower() for f in required_checks(self.kind))
        lines = "; ".join(
            f"{m.criterion.text()} : avant {fmt(m.before)}, après {fmt(m.after)} → {m.result}" for m in self.measures
        )
        return f"Contrôles faits : {checks}. Critères : {lines}. Verdict : {self.verdict.lower()}."

    def filled(self) -> dict[str, str]:
        return {**self.fields, "validation": self.validation_text()}


C_12V = Criterion("+12 V au testeur", ">=", 11.40, "V")
C_STOPS = Criterion("Arrêts pendant 30 min de charge", "<=", 0)
C_TEMP = Criterion("Température du processeur en charge", "<=", 85, "°C")
C_BOOT = Criterion("Démarrage jusqu'au bureau", "<=", 60, "s")
C_DEVERR = Criterion("Périphériques en erreur (Gestionnaire)", "<=", 0)
C_UPDATES = Criterion("Mises à jour en attente", "<=", 0)
C_FILES = Criterion("Documents restaurés, empreintes identiques", "=", "oui")
C_WIREMAP = Criterion("Testeur de câble", "=", "conforme")
C_SPEED = Criterion("Vitesse de liaison négociée", ">=", 1000, "Mb/s")
C_LOSS = Criterion("Ping de la passerelle, pertes", "<=", 0, "%")
C_DHCP = Criterion("Adresse IPv4 reçue du DHCP", "=", "oui")
C_DNS = Criterion("Résolution de nom (nslookup)", "=", "oui")
C_EVENING = Criterion("Coupures entre 17 h et 19 h, sur une soirée", "<=", 0)
C_RW = Criterion("Comptable : ouvrir et enregistrer dans Compta", "=", "oui")
C_DENY = Criterion("Stagiaire : accès à Compta refusé", "=", "oui")
C_PRINT = Criterion("Page de test sur l'imprimante partagée", "=", "oui")

REPORTS: tuple[Report, ...] = (
    Report(
        key="R1",
        theme="PC (matériel)",
        title="PC de dessin qui s'éteint en charge : bloc d'alimentation remplacé",
        kind=K_HW,
        context=(
            "Bureau d'études Trapèze (fictif). Le PC tour INV-0731 s'éteint sans message dès qu'un rendu 3D "
            "dure plus de quelques minutes. Le client a accepté par écrit le diagnostic et le remplacement "
            "d'une pièce jusqu'à 120 € ; ses données sont sauvegardées chaque nuit sur le serveur."
        ),
        fields={
            "reference": "Demande 2026-1043 du 14/10/2026 ; intervention le 15/10/2026 ; technicien : K. Mertens.",
            "equipement": "PC tour INV-0731, bureau 2, poste de dessin ; bloc d'origine 550 W.",
            "demande": "« Le PC s'éteint pendant les rendus » ; reformulé et validé : arrêt brutal en charge, pas au repos.",
            "symptomes": "Arrêt sans écran bleu après 3 à 6 min de rendu ; redémarrage normal ; journal : « Kernel-Power 41 ».",
            "hypotheses": "1. Bloc d'alimentation faible en charge ; 2. surchauffe du processeur ; 3. carte graphique.",
            "releves": "Températures en charge : processeur 78 °C, carte graphique 71 °C ; testeur d'alimentation : +12 V à 11,31 V.",
            "tests": "Test de charge de 30 min (rendu de référence) : 3 arrêts ; testeur d'alimentation sur le bloc démonté.",
            "resultats": "Températures dans les limites ; +12 V hors tolérance (11,40 V à 12,60 V) : bloc en cause.",
            "action": "Bloc remplacé par un bloc 650 W certifié, connectique identique ; câbles rangés, capot fermé.",
            "pieces": "Posé : bloc 650 W, n° de série PSU-65-88213 ; retiré : bloc 550 W, filière DEEE.",
            "risques": "Carte mère d'origine (6 ans) : pas de garantie sur les autres composants.",
            "recommandation": "Prévoir le renouvellement du poste dans les 12 mois ; dépoussiérage tous les 6 mois.",
            "signature": "Réception constatée et signée par M. Collin, gérant, le 15/10/2026 à 16:20.",
        },
        measures=(
            Measure(C_12V, 11.31, 12.04),
            Measure(C_STOPS, 3, 0),
            Measure(C_TEMP, 78, 76),
        ),
        checks_done=frozenset({"fonctionnel", "stabilite", "performance", "securite"}),
        rollback_ready=True,
        journal=(
            JournalEntry("13:05", "Test de charge 30 min, rendu de référence", "3 arrêts (à 4, 11 et 19 min)"),
            JournalEntry("13:42", "Arrêt, débranchement, bloc démonté et contrôlé au testeur", "+12 V à 11,31 V"),
            JournalEntry("14:10", "Pose du bloc 650 W, câbles rangés", "démarrage normal"),
            JournalEntry("14:20", "Test de charge 30 min, même rendu", "0 arrêt ; processeur 76 °C"),
            JournalEntry("14:55", "Bloc neuf au testeur, trois redémarrages", "+12 V à 12,04 V ; 3 démarrages normaux"),
        ),
        client_message=(
            "Votre ordinateur s'éteignait parce que son alimentation ne tenait plus l'effort des rendus. Je l'ai "
            "remplacée et j'ai fait un rendu de 30 minutes sans aucun arrêt. Le reste du PC a six ans : pensez à "
            "son remplacement dans l'année."
        ),
    ),
    Report(
        key="R2",
        theme="système d'exploitation",
        title="Windows très lent après une mise à niveau : système réinstallé et documents restaurés",
        kind=K_OS,
        context=(
            "Agence immobilière Clé d'Or (fictive). Le portable INV-0215 met plus de trois minutes à démarrer "
            "depuis une mise à niveau ratée ; deux périphériques sont en erreur. La gérante a signé l'accord de "
            "réinstallation après la copie vérifiée des documents ; le disque est chiffré par BitLocker, clé "
            "obtenue auprès de l'administrateur."
        ),
        fields={
            "reference": "Demande 2026-1057 du 16/10/2026 ; intervention le 17/10/2026 ; technicienne : S. Leroy.",
            "equipement": "Portable INV-0215, accueil ; Windows 11, disque chiffré (BitLocker).",
            "demande": "« Le PC est devenu inutilisable » ; reformulé et validé : démarrage trop long, webcam et lecteur de cartes en erreur.",
            "symptomes": "Démarrage jusqu'au bureau en 3 min 30 ; Gestionnaire : 2 périphériques avec point d'exclamation ; 14 mises à jour bloquées.",
            "hypotheses": "1. Mise à niveau incomplète (fichiers système) ; 2. pilotes incompatibles ; 3. disque défaillant.",
            "releves": "Santé du disque correcte ; sfc /scannow : fichiers corrompus non réparables ; point de restauration absent.",
            "tests": "Démarrage chronométré trois fois ; réparation du système tentée (DISM, sfc) : échec.",
            "resultats": "Disque sain ; système endommagé, réparation impossible : réinstallation retenue (accord écrit).",
            "action": "Copie des documents vérifiée par empreintes, BitLocker suspendu, réinstallation propre, pilotes du fabricant, mises à jour, documents restaurés.",
            "pieces": "Aucune pièce ; licence Windows numérique réactivée ; pilotes du site du fabricant (versions notées au journal).",
            "risques": "Logiciel de gestion immobilière à réinstaller par son éditeur (licence non fournie à l'atelier).",
            "recommandation": "Rendez-vous avec l'éditeur avant le 24/10/2026 ; sauvegarde hebdomadaire sur le NAS à vérifier chaque mois.",
            "signature": "Réception constatée et signée par Mme Dubois, gérante, le 17/10/2026 à 17:05.",
        },
        measures=(
            Measure(C_BOOT, 210, 42),
            Measure(C_DEVERR, 2, 0),
            Measure(C_UPDATES, 14, 0),
            Measure(C_FILES, "sans objet", "oui"),
        ),
        checks_done=frozenset({"fonctionnel", "performance", "reseau", "securite", "pilote"}),
        rollback_ready=True,
        journal=(
            JournalEntry("09:00", "Copie des documents sur le disque chiffré n° 2 de l'atelier", "1 284 fichiers, empreintes identiques"),
            JournalEntry("09:35", "BitLocker suspendu, réinstallation propre lancée", "installation terminée à 10:20"),
            JournalEntry("10:30", "Pilote webcam du catalogue de mises à jour installé", "webcam toujours en erreur (code 10)"),
            JournalEntry("10:38", "Retour arrière : pilote désinstallé", "état initial retrouvé, webcam en erreur"),
            JournalEntry("10:45", "Pilote webcam du site du fabricant installé", "webcam reconnue, image affichée"),
            JournalEntry("11:30", "Mises à jour, documents restaurés, BitLocker réactivé", "0 mise à jour en attente ; empreintes identiques"),
            JournalEntry("11:50", "Démarrage chronométré trois fois", "41 s, 42 s, 42 s"),
        ),
        client_message=(
            "La mise à jour de Windows s'était mal terminée et ne pouvait pas être réparée : j'ai réinstallé "
            "Windows proprement et remis tous vos documents, vérifiés un par un. Le portable démarre maintenant en "
            "moins d'une minute. Votre logiciel de gestion doit être remis par son éditeur : prenez rendez-vous "
            "avec lui cette semaine."
        ),
    ),
    Report(
        key="R3",
        theme="câblage RJ45",
        title="Prise murale du bureau 4 refaite : liaison revenue à 1 Gb/s",
        kind=K_CABLE,
        context=(
            "Cabinet d'avocats Thémis (fictif). Depuis le déménagement des meubles, le PC du bureau 4 se connecte "
            "à 100 Mb/s seulement et perd des paquets. Le câble horizontal arrive du panneau de brassage, port 14 ; "
            "la prise murale est câblée en T568B."
        ),
        fields={
            "reference": "Demande 2026-1068 du 20/10/2026 ; intervention le 20/10/2026 ; technicien : A. Benali.",
            "equipement": "Prise murale B4-02 (bureau 4), câble catégorie 6 vers le panneau, port 14 ; PC INV-0388.",
            "demande": "« Le réseau rame au bureau 4 » ; reformulé et validé : liaison lente et pertes sur ce seul poste.",
            "symptomes": "Carte réseau du PC à 100 Mb/s au lieu de 1 Gb/s ; ping de la passerelle : 12 % de pertes.",
            "hypotheses": "1. Prise murale abîmée lors du déménagement ; 2. cordon de brassage ; 3. carte réseau du PC.",
            "releves": "Cordon remplacé par un cordon testé : aucun changement ; prise murale déplacée, gaine tirée hors du serre-câble.",
            "tests": "Testeur de câble sur le lien prise B4-02 ↔ panneau port 14, débranché du switch.",
            "resultats": "Testeur : paires 3-6 croisées et fil 7 coupé côté prise : prise en cause.",
            "action": "Prise refaite en T568B avec l'outil d'insertion, gaine sous le serre-câble, boîtier refixé.",
            "pieces": "Posé : prise RJ45 catégorie 6 (une) ; ancienne prise : filière DEEE.",
            "risques": "Câble horizontal non certifié : seul un test wiremap a été fait, pas une certification.",
            "recommandation": "Fixer la goulotte derrière le meuble pour éviter une nouvelle traction sur la prise.",
            "signature": "Réception constatée et signée par Me Lambert le 20/10/2026 à 11:40.",
        },
        measures=(
            Measure(C_WIREMAP, "paires 3-6 croisées, fil 7 coupé", "conforme"),
            Measure(C_SPEED, 100, 1000),
            Measure(C_LOSS, 12, 0),
        ),
        checks_done=frozenset({"fonctionnel", "performance", "reseau", "securite"}),
        rollback_ready=False,
        journal=(
            JournalEntry("10:02", "Cordon remplacé par un cordon testé", "toujours 100 Mb/s"),
            JournalEntry("10:10", "Testeur sur le lien B4-02 ↔ port 14, switch débranché", "paires 3-6 croisées, fil 7 coupé"),
            JournalEntry("10:35", "Prise refaite en T568B, gaine sous le serre-câble", "testeur : 8 fils conformes"),
            JournalEntry("10:45", "PC rebranché, vitesse lue dans les propriétés de la carte", "1000 Mb/s"),
            JournalEntry("10:50", "ping -n 50 de la passerelle", "0 % de pertes"),
        ),
        client_message=(
            "La prise réseau de votre bureau avait été abîmée pendant le déménagement. Je l'ai refaite et testée : "
            "votre ordinateur est revenu à pleine vitesse. Pour éviter que cela se reproduise, il faudrait fixer la "
            "goulotte derrière le meuble."
        ),
    ),
    Report(
        key="R4",
        theme="réseau",
        title="Poste sans réseau en 169.254.x.x : DHCP rétabli, coupure du soir non vérifiée",
        kind=K_NET,
        context=(
            "École des Tilleuls (fictive). Le PC de la salle des professeurs n'a plus d'accès au réseau ; il "
            "affiche une adresse 169.254.12.7. Une professeure signale aussi des coupures « le soir, vers 18 h ». "
            "L'intervention a lieu un matin et doit se terminer avant midi."
        ),
        fields={
            "reference": "Demande 2026-1072 du 21/10/2026 ; intervention le 22/10/2026 ; technicienne : L. Gérard.",
            "equipement": "PC INV-0907, salle des professeurs ; prise P-12, switch du local technique, port 7.",
            "demande": "« Plus d'Internet en salle des profs » ; reformulé et validé : ce poste seul, depuis lundi ; coupures le soir signalées.",
            "symptomes": "Adresse 169.254.12.7 (aucun bail DHCP) ; voyant de lien allumé ; les autres postes fonctionnent.",
            "hypotheses": "1. Port du switch dans un mauvais VLAN ; 2. carte réseau en adresse fixe ; 3. serveur DHCP.",
            "releves": "ipconfig /all : DHCP activé, pas de bail ; port 7 du switch placé dans le VLAN « invités » depuis lundi.",
            "tests": "Portable connu bon, en DHCP, sur la prise P-12 : adresse 169.254 aussi ; même portable sur la prise P-11 : bail correct.",
            "resultats": "Prise et câblage bons ; port 7 dans le mauvais VLAN : cause retenue.",
            "action": "Port 7 remis dans le VLAN « pédagogique » par l'administrateur réseau (droits) ; ipconfig /renew sur le poste.",
            "pieces": "Aucune pièce ; modification de configuration du switch notée par l'administrateur.",
            "risques": "Coupures du soir non reproduites ce matin : cause inconnue, résultat non concluant.",
            "recommandation": "Test de 17 h à 19 h le 23/10/2026 avec relevé du journal du switch ; noter l'heure exacte de toute coupure.",
            "signature": "Réception avec réserve signée par M. Petit, directeur, le 22/10/2026 à 11:30.",
        },
        measures=(
            Measure(C_DHCP, "non (169.254.12.7)", "oui"),
            Measure(C_LOSS, 100, 0),
            Measure(C_DNS, "non", "oui"),
            Measure(C_EVENING, None, None),
        ),
        checks_done=frozenset({"fonctionnel", "stabilite", "reseau", "securite"}),
        rollback_ready=True,
        journal=(
            JournalEntry("08:40", "ipconfig /all sur le poste", "169.254.12.7, DHCP activé, pas de bail"),
            JournalEntry("08:50", "Portable connu bon sur P-12 puis sur P-11", "P-12 : 169.254 ; P-11 : bail correct"),
            JournalEntry("09:15", "Administrateur : port 7 remis dans le VLAN pédagogique", "configuration enregistrée"),
            JournalEntry("09:20", "ipconfig /renew, ping -n 50 de la passerelle, nslookup", "bail reçu ; 0 % de pertes ; nom résolu"),
            JournalEntry("11:00", "Surveillance du poste pendant 1 h 40", "aucune coupure (coupures signalées le soir)"),
        ),
        client_message=(
            "Le branchement de ce poste avait été mal réglé dans l'armoire réseau ; l'administrateur l'a corrigé et "
            "le poste a de nouveau Internet. Je n'ai pas pu vérifier les coupures du soir : je reviens demain de "
            "17 h à 19 h pour les observer. Si une coupure arrive avant, notez l'heure et appelez-moi."
        ),
    ),
    Report(
        key="R5",
        theme="partage de dossiers",
        title="Dossier Compta : droits corrigés pour la comptable et refusés au stagiaire",
        kind=K_SHARE,
        context=(
            "PME Atelier Vert (fictive). Depuis la création des comptes de la rentrée, la comptable ne peut plus "
            "enregistrer dans le dossier partagé Compta du serveur, alors que le stagiaire peut l'ouvrir. La gérante, "
            "propriétaire des données, a validé par écrit la liste des personnes autorisées."
        ),
        fields={
            "reference": "Demande 2026-1080 du 23/10/2026 ; intervention le 23/10/2026 ; technicien : P. Wauters.",
            "equipement": "Serveur de fichiers SRV-01 (local technique), partage \\\\SRV-01\\Compta ; imprimante IMP-02.",
            "demande": "« La comptable ne peut plus enregistrer » ; reformulé et validé : droits du partage Compta à remettre selon la liste de la gérante.",
            "symptomes": "Comptable : « Accès refusé » à l'enregistrement ; stagiaire : ouverture des fichiers possible.",
            "hypotheses": "1. Comptable retirée du groupe G-Compta ; 2. stagiaire ajouté au mauvais groupe ; 3. droits NTFS modifiés.",
            "releves": "Groupe G-Compta : comptable absente ; stagiaire membre de G-Compta ; partage : G-Compta en modification.",
            "tests": "Connexion avec chaque compte sur un poste de test : ouverture, enregistrement, suppression d'un fichier test.",
            "resultats": "Erreur de groupes à la création des comptes : cause retenue (aucun droit NTFS modifié).",
            "action": "Comptable ajoutée à G-Compta, stagiaire retiré ; sessions fermées et rouvertes pour appliquer les groupes.",
            "pieces": "Aucune pièce ; liste des membres de G-Compta jointe au rapport.",
            "risques": "Le stagiaire a pu lire des fichiers de Compta pendant trois semaines : la gérante est informée.",
            "recommandation": "Faire valider par la gérante chaque nouveau compte avant sa création ; revue des groupes chaque trimestre.",
            "signature": "Réception constatée et signée par Mme Verbeke, gérante, le 23/10/2026 à 15:10.",
        },
        measures=(
            Measure(C_RW, "non (accès refusé)", "oui"),
            Measure(C_DENY, "non (lecture possible)", "oui"),
            Measure(C_PRINT, "oui", "oui"),
        ),
        checks_done=frozenset({"fonctionnel", "reseau", "securite"}),
        rollback_ready=True,
        journal=(
            JournalEntry("13:30", "Lecture des membres de G-Compta et des droits du partage", "comptable absente, stagiaire présent"),
            JournalEntry("13:45", "Comptable ajoutée à G-Compta, stagiaire retiré", "modification enregistrée"),
            JournalEntry("13:50", "Sessions des deux comptes fermées et rouvertes", "groupes appliqués"),
            JournalEntry("14:00", "Test avec le compte de la comptable", "ouverture et enregistrement réussis"),
            JournalEntry("14:05", "Test avec le compte du stagiaire", "« Accès refusé »"),
            JournalEntry("14:10", "Page de test sur IMP-02 depuis le poste de la comptable", "page imprimée"),
        ),
        client_message=(
            "Lors de la création des comptes de la rentrée, la comptable avait été oubliée dans le groupe qui donne "
            "accès au dossier Compta et le stagiaire y avait été mis par erreur. C'est corrigé et vérifié avec les "
            "deux comptes. Le stagiaire a pu lire ces fichiers pendant trois semaines : je vous laisse décider de la "
            "suite."
        ),
    ),
)
REPORTS_BY_KEY = {r.key: r for r in REPORTS}

# =============================================================================================
# 10. Schémas
# =============================================================================================

MARKS = ("①", "②", "③", "④")


def report_structure_svg(blank: frozenset[str] = frozenset()) -> str:
    """Le compte rendu en six parties empilées, rubriques listées ; les rubriques de `blank`
    sont remplacées par ①, ②… (schéma à compléter)."""
    width, x0 = 400, 6
    marks = dict(zip([f.key for f in REPORT_FIELDS if f.key in blank], MARKS, strict=False))
    parts = [_text_lines(width // 2, 18, ["Le rapport d'intervention en 6 parties"], size=13, weight="700",
                         anchor="middle")]
    y = 30
    for section in REPORT_SECTIONS:
        fields = [f for f in REPORT_FIELDS if f.section == section]
        lines = [marks.get(f.key, f.label) for f in fields]
        h = 26 + 15 * len(lines) + 4
        parts.append(
            f'<rect data-section="{escape(section)}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 18, [section], size=12.5, weight="700"))
        parts.append(_text_lines(x0 + 20, y + 36, [f"• {line}" for line in lines], size=11.5, step=15))
        y += h + 5
    return _svg(width, y + 2, parts)


def families_svg() -> str:
    """Les six familles de contrôles : nom, question, exemples de tests."""
    width, x0 = 400, 6
    parts = [_text_lines(width // 2, 18, ["Les six familles de contrôles finaux"], size=13, weight="700",
                         anchor="middle")]
    y = 30
    for n, family in enumerate(CHECK_FAMILIES, start=1):
        q_lines = _wrap(family.question, 58)
        t_lines = _wrap("Ex. : " + " ; ".join(family.tests), 58)
        h = 14 + 15 + 13 * (len(q_lines) + len(t_lines)) + 6
        parts.append(
            f'<rect data-family="{family.key}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 16, [f"{n}. {family.name}"], size=12.5, weight="700"))
        yy = y + 16 + 15
        parts.append(_text_lines(x0 + 8, yy, q_lines, size=11, step=13))
        parts.append(_text_lines(x0 + 8, yy + 13 * len(q_lines), t_lines, size=11, step=13))
        y += h + 5
    return _svg(width, y + 2, parts)


_RESULT_MARK = {MET: "✓", NOT_MET: "✗", INCONCLUSIVE: "?"}


def before_after_svg(report: Report) -> str:
    """Critères d'un rapport : critère, avant, après et résultat (✓ / ✗ / ?) écrits en
    toutes lettres, puis le verdict calculé."""
    width, x0 = 400, 6
    parts = [_text_lines(width // 2, 18, [f"Avant / après — rapport {report.key[1]}"], size=13, weight="700",
                         anchor="middle")]
    y = 30
    for m in report.measures:
        c_lines = _wrap(m.criterion.text(), 54)
        b_lines = _wrap(f"Avant : {fmt(m.before)}", 26)
        a_lines = _wrap(f"Après : {fmt(m.after)}", 26)
        rows = max(len(b_lines), len(a_lines))
        h = 12 + 15 * len(c_lines) + 14 * rows + 18
        parts.append(
            f'<rect data-measure="{escape(m.result)}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 8, y + 16, c_lines, size=12, weight="700", step=15))
        yy = y + 16 + 15 * len(c_lines)
        parts.append(_text_lines(x0 + 8, yy, b_lines, size=11, step=14))
        parts.append(_text_lines(x0 + 190, yy, a_lines, size=11, step=14))
        parts.append(_text_lines(x0 + 8, yy + 14 * rows + 2, [f"{_RESULT_MARK[m.result]} {m.result}"], size=11.5,
                                 weight="700"))
        y += h + 5
    v_lines = _wrap(f"Verdict : {report.verdict}", 56)
    parts.append(_text_lines(x0 + 4, y + 14, v_lines, size=12, weight="700", step=16))
    return _svg(width, y + 14 + 16 * len(v_lines), parts)


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


def _report_alt(blank: frozenset[str] = frozenset()) -> str:
    marks = dict(zip([f.key for f in REPORT_FIELDS if f.key in blank], MARKS, strict=False))
    return "Le rapport d'intervention en six parties : " + " ; ".join(
        f"{section} : " + ", ".join(marks.get(f.key, f.label) for f in REPORT_FIELDS if f.section == section)
        for section in REPORT_SECTIONS
    ) + "."


FINAL_CHECKLIST: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Avant de rendre le poste", (
        "Critères d'acceptation relus, contrôles exigés choisis",
        "Mesures « après » faites dans les conditions du « avant »",
        "Verdict écrit : atteint, non atteint, non concluant",
    )),
    ("Remise en état", (
        "Compte technique supprimé, protections actives",
        "Capot fermé, câbles rangés, poste propre",
        "Copie temporaire des données effacée après restitution",
    )),
    ("Restitution", (
        "Test refait devant le client, sur sa tâche",
        "Limites et suivi annoncés, recommandation datée",
        "Rapport signé, copie remise, documentation à jour",
    )),
)

REPORT_FIGURE = Figure(
    key="pr29-structure-rapport",
    title="Le rapport d'intervention : six parties, quatorze rubriques",
    alt=_report_alt(),
    caption="Chaque rubrique répond à une question du client ou du collègue qui reprendra le dossier.",
    svg=report_structure_svg(),
)
FAMILIES_FIGURE = Figure(
    key="pr29-familles-controles",
    title="Les six familles de contrôles finaux",
    alt="Six familles de contrôles : " + " ; ".join(
        f"{i}. {f.name} — {f.question} Exemples : {', '.join(f.tests)}" for i, f in enumerate(CHECK_FAMILIES, start=1)
    ) + ".",
    caption="Le test fonctionnel et la sécurité sont toujours exigés ; les autres familles dépendent de l'intervention.",
    svg=families_svg(),
)
BEFORE_AFTER_FIGURE = Figure(
    key="pr29-avant-apres",
    title="Critères d'acceptation avant / après (rapport 3, prise RJ45)",
    alt="Critères du rapport 3 : " + " ; ".join(
        f"{m.criterion.text()}, avant {fmt(m.before)}, après {fmt(m.after)}, {m.result}" for m in REPORTS_BY_KEY["R3"].measures
    ) + f". Verdict : {REPORTS_BY_KEY['R3'].verdict}.",
    caption="Même mesure, mêmes conditions, avant et après : la comparaison prouve la réparation.",
    svg=before_after_svg(REPORTS_BY_KEY["R3"]),
)
RESERVE_FIGURE = Figure(
    key="pr29-avant-apres-reserve",
    title="Un résultat non concluant (rapport 4, réseau)",
    alt="Critères du rapport 4 : " + " ; ".join(
        f"{m.criterion.text()}, avant {fmt(m.before)}, après {fmt(m.after)}, {m.result}" for m in REPORTS_BY_KEY["R4"].measures
    ) + f". Verdict : {REPORTS_BY_KEY['R4'].verdict}.",
    caption="Une mesure impossible à faire n'est ni réussie ni ratée : elle est non concluante et s'écrit en réserve.",
    svg=before_after_svg(REPORTS_BY_KEY["R4"]),
)
DECISION_TREE_FIGURE = Figure(
    key="pr29-arbre-cloture",
    title=f"Arbre — {DECISION_TREE.title}",
    alt=tree_alt(DECISION_TREE),
    caption="On descend tant que la réponse est « oui » ; au premier « non », on suit la piste de droite.",
    svg=decision_tree_svg(DECISION_TREE.questions, DECISION_TREE.final),
)
FINAL_FIGURE = _proc_figure("pr29-procedure-controles", 1, PROCEDURES[0][0], FINAL_STEPS,
                            "On compare au « avant » écrit : sans critère ni mesure, pas de validation.")
ROLLBACK_FIGURE = _proc_figure("pr29-procedure-retour-arriere", 2, PROCEDURES[1][0], ROLLBACK_STEPS,
                               "Le retour arrière se prépare avant d'intervenir et se vérifie après.")
WRITE_FIGURE = _proc_figure("pr29-procedure-redaction", 3, PROCEDURES[2][0], REPORT_STEPS,
                            "Un rapport se relit : un collègue doit pouvoir refaire chaque test.")
HANDOVER_FIGURE = _proc_figure("pr29-procedure-restitution", 4, PROCEDURES[3][0], HANDOVER_STEPS,
                               "Le client comprend ce qui a été fait, ce qui n'est pas garanti et ce qu'il doit faire.")
HANDOVER_DO_FIGURE = Figure(
    key="pr29-communication-client",
    title="Parler au client : à faire, interdit",
    alt="Deux listes. À faire : " + " ; ".join(HANDOVER_DO) + ". Interdit : " + " ; ".join(HANDOVER_DONT) + ".",
    caption="Un message clair et honnête vaut mieux qu'une liste de sigles.",
    svg=do_dont_svg(HANDOVER_DO, HANDOVER_DONT),
)
CHECKLIST_FIGURE = Figure(
    key="pr29-liste-cloture",
    title="Liste de contrôle de clôture",
    alt="Liste de contrôle en trois parties. "
    + " ".join(f"{title} : " + " ; ".join(items) + "." for title, items in FINAL_CHECKLIST),
    caption="À cocher avant de partir : rien n'est rendu sans mesure, remise en état ni signature.",
    svg=checklist_svg(FINAL_CHECKLIST),
)

PR29_FIGURES: tuple[Figure, ...] = (
    FAMILIES_FIGURE,
    FINAL_FIGURE,
    BEFORE_AFTER_FIGURE,
    RESERVE_FIGURE,
    DECISION_TREE_FIGURE,
    ROLLBACK_FIGURE,
    REPORT_FIGURE,
    WRITE_FIGURE,
    HANDOVER_FIGURE,
    HANDOVER_DO_FIGURE,
    CHECKLIST_FIGURE,
)

# Schémas à compléter (exercices), servis en fichiers statiques comme PR18 à PR28 ------------

REPORT_BLANK_KEYS = frozenset({"hypotheses", "pieces", "risques", "signature"})
REPORT_BLANK_ANSWERS = {
    mark: REPORT_BY_KEY[key].label
    for mark, key in zip(MARKS, [f.key for f in REPORT_FIELDS if f.key in REPORT_BLANK_KEYS], strict=True)
}
REPORT_BLANK_FIGURE = Figure(
    key="pr29-structure-rapport-a-completer",
    title="Structure du rapport à compléter",
    alt=_report_alt(REPORT_BLANK_KEYS),
    caption="Schéma à compléter : nomme les rubriques ①, ②, ③ et ④ et dis ce qu'on y écrit.",
    svg=report_structure_svg(REPORT_BLANK_KEYS),
)
TREE_BLANK_NUMBERS = (1, 2, 3, 4)
TREE_BLANK_QUESTIONS, TREE_BLANK_ANSWERS = _blank_tree(DECISION_TREE, TREE_BLANK_NUMBERS)
TREE_BLANK_FIGURE = Figure(
    key="pr29-arbre-cloture-a-completer",
    title="Arbre de clôture à compléter",
    alt=tree_alt(DECISION_TREE, TREE_BLANK_QUESTIONS),
    caption="Schéma à compléter : conduite à tenir en ①, ②, ③ et ④ quand la réponse est « non ».",
    svg=decision_tree_svg(TREE_BLANK_QUESTIONS, DECISION_TREE.final),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (REPORT_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr29-structure-rapport-a-completer.svg"),
    (TREE_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr29-arbre-cloture-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR28)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )


# =============================================================================================
# 11. Formulaires imprimables (A4), servis en fichiers statiques
# =============================================================================================


@dataclass(frozen=True)
class PrintableForm:
    key: str
    title: str
    intro: str
    # (titre de partie, lignes) ; une ligne = (libellé, nombre de lignes à remplir)
    parts: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    # tableau à remplir : (titre, en-têtes, nombre de lignes vides, position parmi les parties)
    table: tuple[str, tuple[str, ...], int, int] | None = None


FORM_REPORT = PrintableForm(
    key="pr29-formulaire-rapport",
    title="Rapport d'intervention",
    intro="Modèle du cours PR29 : remplir chaque rubrique ; ne jamais y écrire un mot de passe, une clé ni une donnée personnelle.",
    parts=tuple(
        (section, tuple((f"{f.label} — {f.content}", 3 if f.key not in ("reference", "signature") else 2)
                        for f in REPORT_FIELDS if f.section == section))
        for section in REPORT_SECTIONS
    ),
)
FORM_CHECKS = PrintableForm(
    key="pr29-formulaire-controles",
    title="Fiche de contrôles finaux",
    intro="Cocher les familles exigées pour l'intervention, noter chaque critère avant / après et le résultat.",
    parts=(
        ("Intervention", (("Type d'intervention et n° de demande", 1), ("Équipement (n° d'inventaire, emplacement)", 1))),
        ("Familles de contrôles", tuple((f"☐ {f.name} — {f.question}", 1) for f in CHECK_FAMILIES)),
        ("Verdict et décision", (("☐ Validé  ☐ Non validé  ☐ Validation avec réserve", 1),
                                 ("Décision : signature, retour arrière, escalade ou réserve (et suivi)", 2))),
    ),
    table=("Critères d'acceptation", ("Critère (valeur cible et unité)", "Avant", "Après", "Résultat"), 6, 2),
)
FORM_JOURNAL = PrintableForm(
    key="pr29-formulaire-journal",
    title="Journal des opérations et test reproductible",
    intro="Une ligne par opération, dans l'ordre des heures, avec un résultat vérifiable (jamais « OK »).",
    parts=(
        ("Test reproductible", tuple((label, 1) for _k, label in REPRO_FIELDS)),
        ("Retour arrière", (("État initial noté ou sauvegardé (comment, où)", 1),
                            ("Critère d'échec qui déclenche le retour arrière", 1))),
    ),
    table=("Journal des opérations", ("Heure", "Opération (une modification à la fois)", "Résultat observé"), 12, 0),
)
PRINTABLE_FORMS: tuple[PrintableForm, ...] = (FORM_REPORT, FORM_CHECKS, FORM_JOURNAL)
PRINTABLE_PATHS = {form.key: f"{PRINT_DIR_REF}/{form.key}.html" for form in PRINTABLE_FORMS}

_PRINT_CSS = (
    "@page{size:A4;margin:14mm}"
    "body{font-family:system-ui,'Segoe UI',Roboto,Arial,sans-serif;color:#111;max-width:180mm;margin:0 auto;"
    "padding:8mm 4mm;font-size:10.5pt;line-height:1.35}"
    "h1{font-size:15pt;margin:0 0 2mm}h2{font-size:11.5pt;margin:5mm 0 1.5mm;border-bottom:1.5px solid #33415c}"
    ".intro,.foot{font-size:9pt;color:#333}.field{margin:1.5mm 0;break-inside:avoid}"
    ".label{font-weight:600}.line{border-bottom:1px solid #777;height:7mm}"
    "table{width:100%;border-collapse:collapse;margin-top:2mm}th,td{border:1px solid #777;padding:1.5mm;"
    "text-align:left;vertical-align:top}th{background:#eef1f8}td{height:7mm}"
    "section{break-inside:avoid}@media print{.screen{display:none}}"
)


def printable_form_html(form: PrintableForm) -> str:
    """Formulaire A4 autonome (aucun script, aucune ressource externe)."""
    body: list[str] = [f"<h1>{escape(form.title)}</h1>", f'<p class="intro">{escape(form.intro)}</p>',
                       '<p class="screen intro">Imprimer : Ctrl+P (ou ⌘+P), format A4.</p>']
    sections: list[str] = []
    for title, fields in form.parts:
        html = f"<section><h2>{escape(title)}</h2>"
        for label, lines in fields:
            html += (f'<div class="field"><div class="label">{escape(label)}</div>'
                     + '<div class="line"></div>' * lines + "</div>")
        sections.append(html + "</section>")
    if form.table is not None:
        title, header, rows, position = form.table
        head = "".join(f"<th>{escape(h)}</th>" for h in header)
        empty = "<tr>" + "<td></td>" * len(header) + "</tr>"
        sections.insert(position, f"<section><h2>{escape(title)}</h2><table><thead><tr>{head}</tr></thead>"
                                  f"<tbody>{empty * rows}</tbody></table></section>")
    body += sections
    body.append(f'<p class="foot">Jury Central — AMPCR pratique écrite, cours PR29 (support d\'entraînement non officiel, {WRITTEN_AT}).</p>')
    return (
        '<!DOCTYPE html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(form.title)} — PR29</title><style>{_PRINT_CSS}</style></head><body>"
        + "".join(body) + "</body></html>\n"
    )

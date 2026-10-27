"""PR30 « Grand laboratoire écrit — installation et dépannage d'un réseau complet » — exercices
transversaux corrigés et mini-examen (ticket #229).

Même organisation que PR29 (`app.v1.ampcr_pratique_pr29_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 23 exercices corrigés, affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner ». Chacun reprend une phase du dossier de la PME : inventaire et budget,
  câblage et recette des liens, plan IPv4 et DHCP, comptes et droits, systèmes, pannes de mise
  en service, Wi-Fi et sécurité, recette, rapport, lien avec les exigences officielles ; deux
  schémas à compléter (baie, arbre de recette), deux procédures à ordonner, un parcours d'arbre ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, entreprises et relevés sont **fictifs** ; dimensionnements, erreurs
de plan IPv4, droits effectifs, compatibilités, défauts Wi-Fi, canaux, verdicts de liens,
diagnostics de recette et verdicts d'ensemble viennent des fonctions des cours PR07, PR18,
PR20, PR22, PR23, PR25, PR27 et PR29, appliquées par `app.v1.ampcr_pratique_pr30_figures`.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr07_figures import W11_NO, W11_SETTINGS, PcSpec, win11_check
from app.v1.ampcr_pratique_pr18_figures import (
    T_LENGTH,
    T_OK,
    T_PERF,
    T_WIRING,
    TEST_VERDICTS,
    LinkTest,
    boxes_needed,
    choose_switch,
    link_verdict,
    panels_needed,
    switch_ports_needed,
    validation_diagnosis,
)
from app.v1.ampcr_pratique_pr20_figures import AddressPlan, Host, plan_errors
from app.v1.ampcr_pratique_pr22_figures import MODEL_DOMAIN, MODEL_WG, Organisation, recommend_model
from app.v1.ampcr_pratique_pr23_figures import Account, effective_access
from app.v1.ampcr_pratique_pr25_figures import (
    WPA_TKIP,
    ApConfig,
    audit_config,
    best_channel_24,
)
from app.v1.ampcr_pratique_pr27_figures import walk
from app.v1.ampcr_pratique_pr29_figures import (
    D_FOLLOWUP,
    INCONCLUSIVE,
    V_RESERVE,
    Criterion,
    Measure,
    decision,
    fmt,
    verdict,
)
from app.v1.ampcr_pratique_pr30_figures import (
    ACCOUNTS_BY_LOGIN,
    BOM,
    CHANNEL_5,
    CHANNEL_24,
    COST_GROUPS,
    DRAFT_AP,
    DRAFT_AP_AUDIT,
    DRAFT_ERRORS,
    DRAFT_HOSTS,
    FINAL_REPORT,
    FOLDERS,
    FUTURE_POSTES,
    G_ETUDES,
    GUEST_NETWORK,
    GUEST_VLAN,
    LAB_STEPS,
    LINKS,
    LOCAL_USERS,
    MATRIX,
    NEIGHBORS,
    NETWORK,
    ONE_AP_ENOUGH,
    POOL,
    POOL_SIZE,
    PORTS_LATER,
    PORTS_NOW,
    RACK_BLANK_ANSWERS,
    RECETTE_DIAG,
    RECETTE_EVIDENCE,
    RECETTE_RESULTS,
    RECETTE_STEPS,
    RECETTE_TREE,
    REQ_KINDS,
    REQ_TASKS,
    RIGHT_ACCESS,
    ROOT,
    ROUTER_IP,
    SEC_KINDS,
    SECURITY_ITEMS,
    SERVER_IP,
    SHARES,
    STATIC_BY_KEY,
    STORED_ACCESS,
    SWITCH_PORTS,
    TREE,
    TREE_BLANK_ANSWERS,
    UPLINKS,
    WORST_5,
    access,
)

PR30_CODE = "PR30"

KIND_INV = "inventaire et budget"
KIND_CABLE = "câblage et recette des liens"
KIND_IP = "plan IPv4 et DHCP"
KIND_ACC = "comptes, partages et droits"
KIND_OS = "systèmes d'exploitation"
KIND_FAULT = "panne de mise en service"
KIND_WIFI = "Wi-Fi"
KIND_SEC = "sécurité"
KIND_RECETTE = "recette et dépannage"
KIND_ORDER = "procédure à ordonner"
KIND_SCHEMA = "schéma à compléter"
KIND_TREE = "arbre de décision"
KIND_REQ = "exigences officielles"
KIND_WRITE = "rédaction"

# Exigences du cours (matrice #192, audit #236) : chaque item cite au moins l'une des trois.
REQ = frozenset({"AP-36", "AP-37", "AP-38"})
R_INV = ("AP-38", "AP-31", "AP-C01")
R_CABLE = ("AP-36", "AP-34")
R_IP = ("AP-38", "AP-30")
R_ACC = ("AP-38", "AP-24", "AP-27")
R_OS = ("AP-38", "AP-10", "AP-17")
R_FAULT = ("AP-37", "AP-15")
R_WIFI = ("AP-38", "AP-33")
R_DIAG = ("AP-37", "AP-36", "AP-38")
R_WRITE = ("AP-38", "AP-C01", "AP-16")


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _text_doc(title: str, text: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="texte", content_text=text)


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


def _host_rows(hosts: tuple[Host, ...]) -> tuple[tuple[str, str, str, str], ...]:
    return tuple((h.name, f"{h.ip}/{h.prefix}", h.gateway or "—", h.dns[0] if h.dns else "—") for h in hosts)


def _pc_rows(pcs: tuple[tuple[str, PcSpec], ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (name, f"{s.cpu}{'' if s.cpu_listed else ' (absent de la liste)'}", f"{s.ram_gb} Go", f"{s.storage_gb} Go",
         f"{s.firmware_mode}, démarrage sécurisé {'actif' if s.secure_boot_on else 'inactif'}",
         f"TPM {fmt(s.tpm_version) if s.tpm_version else 'absent'}{'' if s.tpm_enabled or not s.tpm_version else ' désactivé'}",
         s.disk_table)
        for name, s in pcs
    )


def _measure_rows(measures: tuple[Measure, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple((m.criterion.text(), fmt(m.before), fmt(m.after)) for m in measures)


def _results_text(measures: tuple[Measure, ...]) -> str:
    return " ; ".join(f"{m.criterion.text()} : {fmt(m.after)} → {m.result}" for m in measures)


def _recette_rows(results: dict[str, dict[str, bool]]) -> tuple[tuple[str, ...], ...]:
    keys = ("lien", "adresse", "passerelle", "poste", "internet", "partage")
    return tuple((name, *("réussi" if r[k] else "échec" for k in keys)) for name, r in results.items())


_RECETTE_HEAD = ("Poste", "Lien", "Adresse", "Passerelle", "Serveur", "Internet", "Partage")

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_ELEMENTS = tuple(BOM[i].item for i in (0, 1, 2, 4, 5, 6, 7, 8, 12, 13, 16, 18))
_E01_GROUP = {b.item: b.group for b in BOM}
E01_CORRECT = tuple(COST_GROUPS.index(_E01_GROUP[e]) for e in E01_ELEMENTS)

E02_PROPOSED = 16
E02_NOW_OK = PORTS_NOW <= E02_PROPOSED
E02_LATER_OK = PORTS_LATER <= E02_PROPOSED

E03_PCS: tuple[tuple[str, PcSpec], ...] = (
    ("PC-A", PcSpec("Intel Core i5-11400", True, True, 6, 2.6, 16, 512, True, "UEFI", False, 2.0, False, "GPT")),
    ("PC-B", PcSpec("Intel Core i7-7700", True, False, 4, 3.6, 16, 512, True, "UEFI", True, 2.0, True, "GPT")),
    ("PC-C", PcSpec("Intel Core i5-12500", True, True, 6, 3.0, 8, 256, True, "Hérité", False, 2.0, False, "MBR")),
)
E03_CHECKS = {name: win11_check(spec) for name, spec in E03_PCS}

E04_STEPS = _labels(LAB_STEPS)

E05_TESTS: tuple[tuple[str, LinkTest], ...] = (
    ("P06 : 8 fils conformes, 10 m, certification PASS", LinkTest("P06", True, 10, "PASS")),
    ("P08 : fil 6 ouvert, 14 m", LinkTest("P08", False, 14, "PASS")),
    ("Annexe : 8 fils conformes, 96 m, PASS", LinkTest("A01", True, 96, "PASS")),
    ("P03 : 8 fils conformes, 14 m, certification FAIL (diaphonie)", LinkTest("P03", True, 14, "FAIL")),
    ("P09 : 8 fils conformes, 6 m, certification PASS", LinkTest("P09", True, 6, "PASS")),
    ("P01 : paires 3-6 et 1-2 inversées à la prise, 16 m", LinkTest("P01", False, 16, "PASS")),
)
E05_CATEGORIES = TEST_VERDICTS
E05_CORRECT = tuple(E05_CATEGORIES.index(link_verdict(t)) for _l, t in E05_TESTS)

E07_ERRORS = DRAFT_ERRORS

E09_CAT_FIXED = "Adresse fixe, hors de l'étendue DHCP"
E09_CAT_DHCP = f"DHCP du réseau du personnel ({NETWORK})"
E09_CAT_GUEST = f"DHCP du réseau invités (VLAN {GUEST_VLAN}, {GUEST_NETWORK})"
E09_CATEGORIES = (E09_CAT_FIXED, E09_CAT_DHCP, E09_CAT_GUEST)
E09_ITEMS: tuple[tuple[str, str], ...] = (
    ("Box (passerelle)", E09_CAT_FIXED),
    ("Serveur de fichiers SRV-01", E09_CAT_FIXED),
    ("Imprimante multifonction IMP-01", E09_CAT_FIXED),
    ("Poste ACCUEIL", E09_CAT_DHCP),
    ("Portable de la directrice, en Wi-Fi LAMBERT-PRO", E09_CAT_DHCP),
    ("Poste LINUX1", E09_CAT_DHCP),
    ("Smartphone d'un client en rendez-vous", E09_CAT_GUEST),
    ("Point d'accès AP-01 (adresse de gestion)", E09_CAT_FIXED),
    ("Portable d'un fournisseur venu présenter un devis", E09_CAT_GUEST),
)
E09_CORRECT = tuple(E09_CATEGORIES.index(k) for _t, k in E09_ITEMS)

E10_ORGS: tuple[Organisation, ...] = (
    Organisation("Lambert & Associés aujourd'hui : 6 postes, une personne par poste", 6),
    Organisation("Lambert dans deux ans : 10 postes, stagiaires qui changent tous les trois mois", 10, rotation=True),
    Organisation("Agence immobilière voisine : 4 postes, règles de mot de passe imposées à tous", 4, policies=True),
)
E10_MODELS = tuple(recommend_model(o) for o in E10_ORGS)

E11_LOGINS = ("cdubois", "flemaire", "jroux")

E15_BEST = best_channel_24(NEIGHBORS)

E16_CORRECT = tuple(SEC_KINDS.index(k) for _t, k in SECURITY_ITEMS)

E17_POSTES = ("COMPTA", "ETUDES2", "LINUX1")

E18_STEPS = _labels(RECETTE_STEPS)

E21_ANSWERS = (True, True, False)
E21_RESULT = walk(RECETTE_TREE, E21_ANSWERS)

E22_CORRECT = tuple(REQ_KINDS.index(k) for _t, k, _r in REQ_TASKS)

# --- Mini-examen -------------------------------------------------------------------------------

X01_LINKS, X01_UPLINKS = 22, 2
X01_NEEDED = switch_ports_needed(X01_LINKS, X01_UPLINKS)
X01_SWITCH = choose_switch(X01_LINKS, X01_UPLINKS)
X01_PANELS = panels_needed(X01_LINKS)
X01_LENGTHS = (62, 58, 55, 51, 48, 44, 41, 38, 35, 33, 30, 28, 26, 24, 22, 21, 20, 18, 16, 15, 12, 10)
X01_BOXES = boxes_needed(X01_LENGTHS)

X02_TESTS: tuple[tuple[str, LinkTest], ...] = (
    ("B07 : 8 fils conformes, 88 m, PASS", LinkTest("B07", True, 88, "PASS")),
    ("B08 : 8 fils conformes, 93 m, PASS", LinkTest("B08", True, 93, "PASS")),
    ("B09 : fils 1 et 2 croisés, 40 m", LinkTest("B09", False, 40, "PASS")),
)
X02_RESULTS = tuple(link_verdict(t) for _l, t in X02_TESTS)

X03_HOSTS: tuple[Host, ...] = (
    Host("BOX", "box : passerelle, DHCP, DNS", ROUTER_IP, 24, None, (), "00-1E-80-5A-10-01"),
    Host("SRV-01", "serveur de fichiers", SERVER_IP, 24, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-0A"),
    Host("IMP-01", "imprimante multifonction", SERVER_IP, 24, ROUTER_IP, (ROUTER_IP,), "00-1E-80-5A-10-14"),
    Host("ETUDES2", "station, DHCP", "169.254.31.7", 16, None, (), "3C-52-82-50-01-05", dhcp=True),
)
X03_ERRORS = plan_errors(AddressPlan(NETWORK, X03_HOSTS, ROUTER_IP, ROUTER_IP, POOL))

X04_STAGIAIRE = Account("lstagiaire", "Léa (stagiaire du bureau d'études)", (LOCAL_USERS, G_ETUDES))
X04_ACCESS = {f: effective_access(X04_STAGIAIRE, f"{ROOT}\\{f}", tree=TREE, shares=SHARES) for f in FOLDERS}

X05_ORG = Organisation("Bureau de 8 postes, verrouillage d'écran et mots de passe imposés à tous", 8, policies=True)
X05_MODEL = recommend_model(X05_ORG)

X06_PC = PcSpec("Intel Core i5-12500", True, True, 6, 3.0, 8, 256, True, "Hérité", False, 2.0, False, "MBR")
X06_CHECK = win11_check(X06_PC)

X07_AP = ApConfig("LAMBERT-PRO", WPA_TKIP, "Lambert-2026", channel_24=6, guest_isolated=False, names=("Lambert",))
X07_AUDIT = audit_config(X07_AP)

X08_RESULTS: dict[str, dict[str, bool]] = {
    "ACCUEIL": {"lien": True, "adresse": True, "passerelle": True, "poste": True, "internet": False, "partage": False},
    "ETUDES1": {"lien": True, "adresse": True, "passerelle": True, "poste": False, "internet": False, "partage": False},
}
X08_DIAG = {name: validation_diagnosis(r) for name, r in X08_RESULTS.items()}

X09_MEASURES: tuple[Measure, ...] = (
    Measure(Criterion("Liens conformes au testeur (sur 10)", ">=", 10), 10, 10),
    Measure(Criterion("Postes validés à la recette (sur 6)", ">=", 6), 6, 6),
    Measure(Criterion("Invité : accès au serveur refusé", "=", "oui"), None, None),
    Measure(Criterion("Impression depuis LINUX1", "=", "oui"), "non", "oui"),
)
X09_VERDICT = verdict(tuple(m.result for m in X09_MEASURES))
X09_DECISION = decision(X09_VERDICT, rollback_ready=True)

_COST_NAMES = ", ".join(COST_GROUPS)

# =============================================================================================
# 23 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Ranger la nomenclature par poste de dépense",
        question_type="classification",
        requirement_ids=R_INV,
        kind=KIND_INV,
        context=(
            "La directrice de Géomètres Lambert & Associés (fictif) veut comparer les devis de deux fournisseurs "
            "poste par poste. Tu as écrit la nomenclature de l'installation, sans aucun prix. Elle doit maintenant "
            f"être présentée par poste de dépense : {_COST_NAMES}."
        ),
        instructions=("Range chaque ligne de la nomenclature dans son poste de dépense.",),
        criteria=(
            _c("Classement", 6, " ; ".join(f"{e} → {COST_GROUPS[c]}" for e, c in zip(E01_ELEMENTS, E01_CORRECT, strict=True)) + " (0,5 pt par ligne)."),
        ),
        correction=(
            "Matériel actif : ce qui est alimenté et configuré (switch, point d'accès, onduleur, serveur, disques de sauvegarde). Câblage et passif : câble, baie, panneau, prises et cordons, qui ne se configurent pas.",
            "Logiciels et licences : système du serveur et licences d'accès client, système des postes (Ubuntu ne coûte rien, mais la ligne existe). Main-d'œuvre : pose, tests, configuration, recette. Les prix viennent des devis ; on n'en invente aucun.",
        ),
        classification=Classification(categories=COST_GROUPS, elements=E01_ELEMENTS, correct=E01_CORRECT),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Le switch de 16 ports suffit-il ?",
        question_type="document_analysis",
        requirement_ids=R_INV + ("AP-36",),
        kind=KIND_INV,
        context=(
            f"Le neveu de la directrice propose un switch de {E02_PROPOSED} ports, « largement assez pour six PC ». Le "
            f"document 1 rappelle le plan : {LINKS} prises reliées à la baie, la box et le serveur branchés "
            f"directement au switch, et {FUTURE_POSTES} postes de plus prévus dans deux ans. Le cours garde 20 % de "
            "ports libres en réserve."
        ),
        documents=(_table("Document 1 — Liens à raccorder (support fictif)", ("Élément", "Nombre"),
                          ("Prises P01 à P10 (postes, imprimante, point d'accès, réserves)", str(LINKS)),
                          ("Cordons directs dans la baie (box, serveur)", str(UPLINKS)),
                          ("Postes prévus dans deux ans", str(FUTURE_POSTES))),),
        instructions=(
            "Calcule le nombre de ports nécessaires aujourd'hui, puis dans deux ans.",
            "Conclus sur la proposition et donne la taille de switch à acheter.",
        ),
        criteria=(
            _c("Calculs", 2, f"Aujourd'hui : {LINKS} × 1,2 = {LINKS * 1.2:g} → {PORTS_NOW - UPLINKS} + {UPLINKS} = {PORTS_NOW} ports ; dans deux ans : {LINKS + FUTURE_POSTES} × 1,2 → {PORTS_LATER - UPLINKS} + {UPLINKS} = {PORTS_LATER} ports."),
            _c("Conclusion", 2, f"{E02_PROPOSED} ports suffisent aujourd'hui, pas après l'extension : acheter {SWITCH_PORTS} ports dès maintenant (un second switch plus tard coûterait plus et ajouterait une panne possible)."),
        ),
        correction=(
            f"Aujourd'hui : {LINKS} liens + 20 % = {LINKS * 1.2:g}, arrondi à {PORTS_NOW - UPLINKS}, plus {UPLINKS} cordons directs : {PORTS_NOW} ports. Le switch de {E02_PROPOSED} ports conviendrait.",
            f"Dans deux ans : {LINKS + FUTURE_POSTES} liens + 20 % = {(LINKS + FUTURE_POSTES) * 1.2:g}, arrondi à {PORTS_LATER - UPLINKS}, plus {UPLINKS} : {PORTS_LATER} ports, plus que {E02_PROPOSED}. Puisque l'extension est écrite dans la demande, on achète tout de suite un switch de {SWITCH_PORTS} ports (taille standard suivante).",
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Windows 11 ou un autre système ?",
        question_type="document_analysis",
        requirement_ids=R_OS,
        kind=KIND_OS,
        context=(
            "Un autre cabinet (fictif) prépare le même type d'installation et a relevé trois PC qu'il veut garder. "
            "Windows 10 n'est plus pris en charge depuis le 14 octobre 2025 : chaque PC doit passer à Windows 11 Pro "
            "ou recevoir un autre système maintenu. Le document 1 donne les relevés (msinfo32, tpm.msc, Gestion des disques)."
        ),
        documents=(_table("Document 1 — Relevés des trois PC (support fictif)",
                          ("PC", "Processeur", "Mémoire", "Stockage", "Firmware", "TPM", "Disque"), *_pc_rows(E03_PCS)),),
        instructions=(
            "Pour chaque PC, dis s'il est compatible Windows 11 tel quel, après réglages, ou pas du tout.",
            "Donne les réglages ou le système proposé pour chacun.",
        ),
        criteria=(
            _c("Verdicts", 1.5, " ; ".join(f"{n} : {v[0].lower()}" for n, v in E03_CHECKS.items()) + " (0,5 pt par PC)."),
            _c("Réglages et choix", 2.5, f"PC-A : {', '.join(E03_CHECKS['PC-A'][2])} ; PC-B : processeur absent de la liste → Ubuntu LTS (ou remplacement) ; PC-C : {', '.join(E03_CHECKS['PC-C'][2])}."),
        ),
        correction=(
            "PC-A a tout le matériel : il suffit d'activer le TPM (et, c'est recommandé, le démarrage sécurisé) dans le firmware. PC-C aussi, mais il démarre en mode hérité sur un disque MBR : sauvegarde, conversion en GPT (mbr2gpt), mode UEFI, TPM activé.",
            "PC-B a un processeur absent de la liste de compatibilité : aucun réglage n'y change rien. On lui installe un système maintenu, comme Ubuntu LTS, si ses logiciels existent sous Linux ; sinon on prévoit son remplacement. On ne le laisse pas sous Windows 10 sans mises à jour.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Remettre le laboratoire dans l'ordre",
        question_type="ordering",
        requirement_ids=R_WRITE,
        kind=KIND_ORDER,
        context=(
            "Un nouveau technicien de l'atelier doit mener seul une installation complète chez une PME de six personnes. "
            "Son responsable lui donne les huit phases du chantier, mélangées. Dans quel ordre doit-il travailler pour "
            "ne rien refaire et pouvoir prouver le résultat à la fin ?"
        ),
        instructions=("Remets les huit phases dans l'ordre et justifie la place des deux premières et de la dernière.",),
        criteria=(
            _c("Ordre", 4, " → ".join(label for label, _d in LAB_STEPS) + " (0,5 pt par phase bien placée)."),
        ),
        correction=(
            "On analyse avant de concevoir, on conçoit avant de chiffrer, on câble et on teste chaque lien avant de brancher les équipements : un défaut de lien trouvé plus tard coûte bien plus cher à localiser.",
            "La configuration des postes vient après la baie ; la sécurité se fait avant la recette, qui se termine par le rapport et le procès-verbal signé.",
        ),
        ordering=_shuffled_ordering(E04_STEPS, (3, 0, 6, 1, 7, 4, 2, 5)),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Lire le rapport du testeur de câble",
        question_type="classification",
        requirement_ids=R_CABLE,
        kind=KIND_CABLE,
        context=(
            "Après la pose du câblage Cat6 chez Lambert & Associés (fictif), l'installateur a testé chaque lien entre "
            "la prise et le panneau. Le cours lit un rapport dans l'ordre : câblage des 8 fils, longueur du lien "
            "permanent (90 m au plus), puis certification. Classe chaque ligne du rapport."
        ),
        instructions=("Range chaque lien selon le verdict du testeur.",),
        criteria=(
            _c("Classement", 3, " ; ".join(f"{label} → {E05_CATEGORIES[c]}" for (label, _t), c in zip(E05_TESTS, E05_CORRECT, strict=True)) + " (0,5 pt par lien)."),
        ),
        correction=(
            "Un fil ouvert ou une paire inversée est un défaut de câblage, quelle que soit la longueur. Un lien de 96 m dépasse les 90 m du lien permanent : trop long, même s'il passe la certification. Un lien conforme et court peut échouer en certification (diaphonie : trop détorsadé au raccordement).",
            f"Seuls les liens « {T_OK.lower()} » sont recettés ; les autres sont refaits ({T_WIRING.lower()}, {T_PERF.lower()}) ou repensés ({T_LENGTH.lower()} : autre chemin ou switch plus proche), puis retestés.",
        ),
        classification=Classification(categories=E05_CATEGORIES, elements=tuple(label for label, _t in E05_TESTS), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Décrire le raccordement T568B d'une prise",
        question_type="short_answer",
        requirement_ids=R_CABLE,
        kind=KIND_CABLE,
        context=(
            "Le lien P08 du poste LINUX1 a échoué au testeur (fil 6 ouvert). Tu dois refaire la prise murale et expliquer "
            "par écrit au stagiaire qui t'aide comment la raccorder. Toute l'installation de Lambert & Associés (fictif) "
            "est en T568B, à la prise comme au panneau."
        ),
        instructions=(
            "Donne l'ordre des couleurs T568B des broches 1 à 8.",
            "Explique pourquoi la même norme est utilisée aux deux extrémités et cite deux précautions de raccordement.",
        ),
        criteria=(
            _c("Ordre des couleurs", 2, "1 blanc-orange, 2 orange, 3 blanc-vert, 4 bleu, 5 blanc-bleu, 6 vert, 7 blanc-marron, 8 marron."),
            _c("Justification et précautions", 2, "Même norme aux deux bouts = lien droit, chaque broche arrive sur la même broche ; détorsadage minimal (13 mm au plus), gaine maintenue jusqu'au connecteur, outil à poinçonner, test après raccordement."),
        ),
        correction=(
            "T568B : blanc-orange, orange, blanc-vert, bleu, blanc-bleu, vert, blanc-marron, marron. La paire verte occupe les broches 3 et 6, séparées par la paire bleue (4-5).",
            "Avec la même norme à la prise et au panneau, le lien est droit. Mélanger T568A et T568B sur un même lien croise les paires orange et verte. On détorsade le moins possible, on garde la gaine jusqu'au connecteur, on poinçonne avec l'outil, puis on reteste le lien.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Corriger le brouillon du plan d'adressage",
        question_type="document_analysis",
        requirement_ids=R_IP,
        kind=KIND_IP,
        context=(
            f"Un collègue a préparé les adresses fixes du réseau {NETWORK} de Lambert & Associés (fictif). La box "
            f"{ROUTER_IP} est la passerelle, le serveur DNS des postes et le serveur DHCP ; son étendue va de {POOL[0]} "
            f"à {POOL[1]}. Le document 1 est son brouillon."
        ),
        documents=(_table("Document 1 — Brouillon des adresses fixes (support fictif)",
                          ("Équipement", "Adresse / préfixe", "Passerelle", "DNS"), *_host_rows(DRAFT_HOSTS)),),
        instructions=("Relève les erreurs du brouillon et corrige chaque ligne fautive.",),
        criteria=(
            _c("Erreurs", 3, " ; ".join(e.rstrip(".") for e in DRAFT_ERRORS) + " (1 pt par équipement fautif)."),
            _c("Corrections", 1, "IMP-01 : adresse fixe hors étendue (192.168.50.20) ; AP-01 : /24 (255.255.255.0) ; SW-01 : passerelle 192.168.50.1."),
        ),
        correction=(
            "IMP-01 a une adresse fixe dans l'étendue DHCP : la box pourrait la donner à un poste, d'où un conflit. On la sort de l'étendue (192.168.50.20).",
            "AP-01 en /16 croirait joindre directement tout 192.168.x.x : même masque /24 pour tout le réseau. SW-01 a une passerelle d'un autre réseau, injoignable : sa gestion à distance et ses mises à jour échoueraient. Passerelle 192.168.50.1.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Régler le DHCP et le DNS de la box",
        question_type="short_answer",
        requirement_ids=R_IP + ("AP-29",),
        kind=KIND_IP,
        context=(
            f"Tu configures la box de Lambert & Associés (fictif) pour le réseau {NETWORK}. Les équipements fixes sont en "
            f".1 à .20 ; les postes, les portables et les smartphones du personnel reçoivent leur adresse automatiquement. "
            "Le personnel compte six personnes, avec chacune un PC, un smartphone et parfois un portable."
        ),
        instructions=(
            "Donne l'étendue DHCP, sa taille, la passerelle et le DNS distribués, et justifie l'étendue.",
            "Explique pourquoi l'imprimante n'est pas dans l'étendue et donne une autre solution acceptable.",
        ),
        criteria=(
            _c("Paramètres", 2, f"Étendue {POOL[0]} à {POOL[1]} ({POOL_SIZE} adresses, largement plus que les 20 à 30 appareils) ; masque 255.255.255.0 ; passerelle et DNS {ROUTER_IP} ; bail d'un jour."),
            _c("Imprimante", 2, "Adresse fixe hors de l'étendue : elle ne change jamais, les postes l'atteignent par son IP ; autre solution : réservation DHCP liée à son adresse MAC."),
        ),
        correction=(
            f"Étendue {POOL[0]}–{POOL[1]} : {POOL_SIZE} adresses pour une trentaine d'appareils, avec une large marge, sans chevaucher les adresses fixes. La box distribue le masque /24, la passerelle {ROUTER_IP} et le DNS {ROUTER_IP} (elle relaie vers ceux de l'opérateur).",
            "Les postes impriment vers l'adresse IP de l'imprimante : si elle changeait, l'impression tomberait. D'où une adresse fixe hors étendue. Une réservation DHCP (même adresse donnée à la même MAC) est aussi correcte, si elle est notée dans le dossier.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Adresse fixe, DHCP du personnel ou réseau invités ?",
        question_type="classification",
        requirement_ids=R_IP + ("AP-33",),
        kind=KIND_IP,
        context=(
            f"Le plan du cabinet Lambert (fictif) a trois cas : des adresses fixes hors étendue pour l'infrastructure, le "
            f"DHCP du réseau du personnel ({NETWORK}) et un réseau invités isolé sur le VLAN {GUEST_VLAN} ({GUEST_NETWORK}), "
            "réservé aux visiteurs. Tu remplis la colonne « adressage » de l'inventaire."
        ),
        instructions=("Range chaque appareil dans son mode d'adressage.",),
        criteria=(
            _c("Classement", 4.5, " ; ".join(f"{t} → {k}" for t, k in E09_ITEMS) + " (0,5 pt par appareil)."),
        ),
        correction=(
            "L'infrastructure que d'autres appareils doivent toujours trouver (box, serveur, imprimante, point d'accès, switch) a une adresse fixe hors étendue.",
            "Les appareils du personnel, en câble ou en Wi-Fi, reçoivent une adresse du réseau du personnel. Ceux des visiteurs (client, fournisseur) vont sur le réseau invités : Internet seulement, aucun accès au serveur.",
        ),
        classification=Classification(categories=E09_CATEGORIES, elements=tuple(t for t, _k in E09_ITEMS), correct=E09_CORRECT),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Groupe de travail ou domaine : trois situations",
        question_type="document_analysis",
        requirement_ids=R_ACC,
        kind=KIND_ACC,
        context=(
            "Le cours retient un repère : au-delà d'une dizaine de postes, ou dès qu'il faut gérer comptes et règles depuis "
            "un point central (personnes qui changent souvent, règles imposées à tous, personnes qui changent de poste), "
            "un domaine ; sinon un groupe de travail suffit. Le document 1 décrit trois organisations fictives."
        ),
        documents=(_table("Document 1 — Trois organisations (support fictif)", ("Organisation",),
                          *((o.label,) for o in E10_ORGS)),),
        instructions=("Pour chaque organisation, choisis groupe de travail ou domaine et justifie.",),
        criteria=(
            _c("Choix", 3, " ; ".join(f"{o.label.split(' :')[0]} → {m}" for o, m in zip(E10_ORGS, E10_MODELS, strict=True)) + " (1 pt par organisation)."),
            _c("Justification", 1, "Six postes stables : comptes locaux gérables ; rotation des stagiaires ou règles imposées à tous : gestion centrale par un contrôleur de domaine (Windows Pro requis sur les postes)."),
        ),
        correction=(
            f"Lambert aujourd'hui : six postes, une personne par poste, aucune règle centrale : {E10_MODELS[0].lower()}, avec un compte par personne sur le serveur.",
            f"Lambert dans deux ans : les stagiaires changent souvent, il faudrait créer et supprimer leurs comptes partout : {E10_MODELS[1]}. L'agence immobilière n'a que quatre postes, mais veut des règles imposées à tous : {E10_MODELS[2]} (stratégies de groupe). Une autre solution justifiée (gestion des appareils en ligne) peut être acceptée.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Compléter la matrice des droits du serveur",
        question_type="document_analysis",
        requirement_ids=R_ACC + ("AP-25",),
        kind=KIND_ACC,
        context=(
            "Sur le serveur SRV-01 de Lambert & Associés (fictif), chaque partage donne « Utilisateurs authentifiés : "
            "Modifier » et les autorisations NTFS décident. Le document 1 donne les groupes des personnes et les "
            "autorisations NTFS de chaque dossier ; tu dois vérifier ce que trois personnes obtiennent par le réseau."
        ),
        documents=(
            _table("Document 1 — Groupes et autorisations NTFS (support fictif)", ("Élément", "Contenu"),
                   ("cdubois (directrice)", "Utilisateurs, G_Administration, G_Direction"),
                   ("flemaire (comptable)", "Utilisateurs, G_Administration, G_Compta"),
                   ("jroux (géomètre)", "Utilisateurs, G_Etudes"),
                   ("Commun", "Utilisateurs : Modification"),
                   ("Administration", "G_Administration : Modification"),
                   ("Etudes", "G_Etudes : Modification ; G_Direction : Lecture et exécution"),
                   ("Compta", "G_Compta : Modification ; G_Direction : Lecture et exécution")),
        ),
        instructions=("Donne le droit effectif par le réseau de cdubois, flemaire et jroux sur les quatre dossiers.",),
        criteria=(
            _c("Matrice", 3, " ; ".join(f"{login} : " + ", ".join(f"{f} {MATRIX[login][f].lower()}" for f in FOLDERS) for login in E11_LOGINS) + " (0,25 pt par case)."),
            _c("Règle", 1, "Les autorisations des groupes se cumulent ; par le réseau, le plus restrictif du partage et de NTFS s'applique ; sans entrée NTFS, aucun accès."),
        ),
        correction=(
            "La directrice cumule G_Administration (Administration en modification) et G_Direction (Etudes et Compta en lecture). Le comptable modifie Administration et Compta, n'a rien sur Etudes. Le géomètre modifie Etudes, n'a rien sur Administration ni Compta.",
            "Commun est en modification pour tous (groupe Utilisateurs). Le partage « Modifier » ne limite rien ici : c'est NTFS qui décide. La matrice répond exactement aux besoins écrits par le client.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="« Accès refusé » sur le dossier Compta",
        question_type="document_analysis",
        requirement_ids=R_FAULT + ("AP-27",),
        kind=KIND_FAULT,
        context=(
            "À la recette chez Lambert & Associés (fictif), le comptable François Lemaire ouvre \\\\SRV-01\\Compta depuis "
            "le poste COMPTA : « Accès refusé ». Les autres dossiers s'ouvrent. La matrice des droits prévoit pour lui la "
            "modification sur Compta. L'accueil avait préparé ce poste la veille. Le document 1 donne tes relevés."
        ),
        documents=(_console("Document 1 — Relevés sur COMPTA (capture fictive)",
                            "C:\\> whoami",
                            "compta\\flemaire",
                            "C:\\> cmdkey /list",
                            "Cible : Domain:target=SRV-01",
                            "Type : Mot de passe du domaine",
                            "Utilisateur : SRV-01\\amartin",
                            "C:\\> dir \\\\SRV-01\\Compta",
                            "Accès refusé."),),
        instructions=(
            "Explique la cause de l'accès refusé en t'appuyant sur les relevés et la matrice.",
            "Donne la correction et le test qui la prouve, sans toucher aux droits du serveur.",
        ),
        criteria=(
            _c("Cause", 2, f"Le poste se connecte au serveur avec l'identifiant enregistré SRV-01\\amartin (accueil) : droit de ce compte sur Compta = {STORED_ACCESS.lower()} ; flemaire aurait {RIGHT_ACCESS.lower()}."),
            _c("Correction et test", 2, "Supprimer l'identifiant enregistré (Gestionnaire d'identification ou cmdkey /delete:SRV-01), fermer la connexion, se reconnecter avec SRV-01\\flemaire ; test : créer, enregistrer et supprimer un fichier d'essai dans Compta ; droits du serveur inchangés."),
        ),
        correction=(
            "Le compte de session (compta\\flemaire) n'est pas celui que le serveur voit : Windows présente l'identifiant enregistré pour SRV-01, celui de l'accueil. Ce compte n'a aucun accès à Compta (G_Administration seulement), d'où le refus. Commun et Administration s'ouvrent, ce qui brouille la piste.",
            "On supprime l'identifiant enregistré, on se reconnecte avec le compte du comptable, puis on teste en écriture. Élargir les droits de Compta serait une faute : l'accueil pourrait lire la comptabilité.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Plus d'image après l'ajout de mémoire",
        question_type="long_answer",
        requirement_ids=R_FAULT + ("AP-02", "AP-C02"),
        kind=KIND_FAULT,
        context=(
            "Le samedi du chantier, tu ajoutes deux barrettes de 16 Go à la station ETUDES1 de Lambert & Associés (fictif), "
            "qui en avait déjà deux. Au démarrage, les ventilateurs tournent, aucune image n'apparaît et la carte mère émet "
            "des bips longs répétés ; son manuel les associe à un défaut de mémoire. Avant l'ajout, le PC fonctionnait."
        ),
        instructions=("Rédige ta procédure de diagnostic, étape par étape, jusqu'à la conclusion, avec les précautions.",),
        criteria=(
            _c("Sécurité", 1, "Arrêt, secteur débranché, bracelet antistatique relié au châssis, barrettes tenues par les bords."),
            _c("Démarche", 2, "Revenir à l'état connu (retirer les deux nouvelles barrettes) ; puis une nouvelle barrette à la fois, bien enfoncée, dans le bon emplacement ; une seule modification à la fois."),
            _c("Compatibilité et conclusion", 1, "Comparer type DDR, fréquence, tension à la liste de compatibilité (QVL) de la carte mère ; barrette défectueuse ou incompatible → retour au fournisseur ; journal et rapport."),
        ),
        correction=(
            "Le symptôme apparaît juste après l'ajout de mémoire et le manuel associe ces bips à la mémoire : la piste est la mémoire ajoutée. On arrête, on débranche le secteur et on met le bracelet antistatique.",
            "On retire les deux nouvelles barrettes : si le PC redémarre avec ses 32 Go d'origine, la cause est confirmée. On essaie ensuite une seule nouvelle barrette, enfoncée jusqu'au clic des deux loquets, dans l'emplacement du manuel, puis l'autre. On compare leur référence à la liste de compatibilité de la carte mère. Une barrette défectueuse ou incompatible retourne au fournisseur ; tout est noté au journal.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Auditer la fiche Wi-Fi du stagiaire",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_WIFI,
        context=(
            "Le stagiaire a préparé la configuration du point d'accès AP-01 de Lambert & Associés (fictif) pendant que tu "
            "câblais. Le document 1 est sa fiche. Le Wi-Fi du personnel doit être sûr, et les clients en rendez-vous "
            "doivent avoir Internet sans jamais atteindre le serveur."
        ),
        documents=(_table("Document 1 — Fiche de configuration du stagiaire (support fictif)", ("Paramètre", "Valeur"),
                          ("SSID du personnel", f"{DRAFT_AP.ssid}, masqué"),
                          ("Sécurité", DRAFT_AP.security),
                          ("Clé", DRAFT_AP.passphrase),
                          ("WPS", "activé"),
                          ("Mot de passe d'administration", "celui d'usine"),
                          ("Canal 2,4 GHz / largeur", f"{DRAFT_AP.channel_24} / {DRAFT_AP.width_24} MHz"),
                          ("Réseau invités", "sur le réseau du personnel")),),
        instructions=("Relève chaque défaut de la fiche et donne la correction.",),
        criteria=(
            _c("Défauts et corrections", 4, " ; ".join(f"{p} : {c}" for p, c in DRAFT_AP_AUDIT) + " (points répartis entre les défauts)."),
        ),
        correction=(
            "La clé est courte et contient le nom de l'entreprise ; le WPS et le mot de passe d'usine ouvrent la porte ; le canal 3 chevauche les canaux 1 et 6 ; 40 MHz occupe presque toute la bande 2,4 GHz ; masquer le SSID ne protège rien et gêne les connexions.",
            "Le défaut le plus grave est le réseau invités sur le réseau du personnel : un client pourrait atteindre le serveur. On le place sur le VLAN invités isolé. WPA2-Personnel est acceptable, mais le mode WPA2/WPA3 est préférable.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Choisir les canaux et vérifier la couverture",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_WIFI,
        context=(
            "Depuis le couloir de Lambert & Associés (fictif), tu as relevé les réseaux Wi-Fi voisins (document 1). Le point "
            "d'accès émettra en 2,4 et en 5 GHz. L'estimation du cours donne au pire "
            f"{WORST_5} dBm en 5 GHz dans les deux salles ; l'objectif est −67 dBm ou mieux."
        ),
        documents=(_table("Document 1 — Réseaux voisins relevés (support fictif)", ("Réseau", "Canal 2,4 GHz", "Signal"),
                          *((n.ssid, str(n.channel), f"{n.dbm} dBm") for n in NEIGHBORS)),),
        instructions=(
            "Choisis le canal 2,4 GHz parmi 1, 6 et 11 et justifie ; propose un canal 5 GHz.",
            "Dis si un seul point d'accès suffit et ce qu'il faudra vérifier à la recette.",
        ),
        criteria=(
            _c("Canal 2,4 GHz", 2, f"Canal {E15_BEST} : les canaux 1 et 6 sont occupés par des voisins forts (−61 et −66 dBm) ; sur 11, le seul voisin est faible (−84 dBm), le canal 9 (−86 dBm) aussi."),
            _c("5 GHz et couverture", 2, f"Canal {CHANNEL_5} (sans détection radar) ; un seul point d'accès suffit ({WORST_5} dBm ≥ −67) ; mesure réelle aux points prévus à la recette."),
        ),
        correction=(
            f"On reste sur 1, 6 ou 11, les seuls canaux qui ne se chevauchent pas. Les voisins forts (au-dessus de −80 dBm) occupent 1 et 6 ; sur 11, ne restent que des signaux faibles : canal {E15_BEST}.",
            f"En 5 GHz, le canal {CHANNEL_5} évite la détection radar obligatoire à partir du canal 52. L'estimation donne {WORST_5} dBm au pire : un seul point d'accès au plafond du couloir suffit, mais ce n'est qu'un calcul, à confirmer par une mesure sur place.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Vraie mesure de sécurité ou fausse sécurité ?",
        question_type="classification",
        requirement_ids=("AP-38", "AP-33", "AP-C03"),
        kind=KIND_SEC,
        context=(
            "Avant la recette chez Lambert & Associés (fictif), ton responsable relit la liste de sécurité que l'équipe a "
            "écrite pendant le chantier. Certaines lignes protègent vraiment le réseau et les données ; d'autres donnent une "
            "impression de sécurité, ou sont dangereuses. Tu fais le tri."
        ),
        instructions=("Range chaque ligne : mesure efficace, ou fausse sécurité / pratique à proscrire.",),
        criteria=(
            _c("Tri", 6, " ; ".join(f"{t} → {k}" for t, k in SECURITY_ITEMS) + " (0,5 pt par ligne)."),
        ),
        correction=(
            "Protègent vraiment : mots de passe par défaut changés, WPA2/WPA3 avec une clé longue et WPS coupé, invités isolés, un compte par personne, sauvegarde externe testée, onduleur qui arrête le serveur, mises à jour.",
            "Fausses sécurités : masquer le SSID, le miroir pris pour une sauvegarde (il recopie aussi un effacement), la baie ouverte. Pratiques à proscrire : le compte administrateur partagé, les secrets écrits dans le rapport.",
        ),
        classification=Classification(categories=SEC_KINDS, elements=tuple(t for t, _k in SECURITY_ITEMS), correct=E16_CORRECT),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Interpréter la fiche de recette",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_RECETTE,
        context=(
            "Lundi matin, tu fais la recette des six postes de Lambert & Associés (fictif) avec la directrice. Pour chaque "
            "poste, les contrôles se font dans l'ordre : lien, adresse, passerelle, serveur, Internet, partage. Le "
            "document 1 donne les résultats ; le document 2, ce que tu as relevé sur les trois postes en échec."
        ),
        documents=(
            _table("Document 1 — Fiche de recette (support fictif)", _RECETTE_HEAD, *_recette_rows(RECETTE_RESULTS)),
            _text_doc("Document 2 — Relevés sur les postes en échec (support fictif)",
                      " / ".join(f"{name} : {RECETTE_EVIDENCE[name]}" for name in E17_POSTES)),
        ),
        instructions=(
            "Pour COMPTA, ETUDES2 et LINUX1, indique le premier contrôle en échec et la piste.",
            "Donne la correction et le contrôle qui la valide pour chacun.",
        ),
        criteria=(
            _c("Pistes", 2, " ; ".join(f"{p} → {RECETTE_DIAG[p]}" for p in E17_POSTES) + "."),
            _c("Corrections", 2, "COMPTA : supprimer l'identifiant enregistré, reconnexion avec flemaire ; ETUDES2 : port 7 remis dans le VLAN du personnel, ipconfig /renew ; LINUX1 : prise P08 refaite en T568B, lien retesté ; puis recette complète refaite sur chaque poste."),
        ),
        correction=(
            "On ne lit que le premier échec : sur LINUX1, le lien manque, tout le reste en découle ; sur ETUDES2, l'adresse vient du réseau invités (port dans le VLAN 60) ; sur COMPTA, tout fonctionne sauf le partage.",
            "Une seule correction par poste, puis on refait toute la recette du poste : un contrôle qui suivait un échec ne prouvait rien.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Remettre la recette dans l'ordre",
        question_type="ordering",
        requirement_ids=R_DIAG,
        kind=KIND_ORDER,
        context=(
            "Ta collègue prépare la recette de l'installation d'un cabinet (fictif) qu'elle a câblé et configuré. Elle a noté "
            "les sept étapes de la recette sur des post-it, qui se sont mélangés. Elle te demande l'ordre à suivre devant le "
            "client pour que chaque résultat soit probant."
        ),
        instructions=("Remets les sept étapes de la recette dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, " → ".join(label for label, _d in RECETTE_STEPS) + " (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "Les critères s'écrivent avant ; les liens physiques se vérifient avant les postes (un poste ne prouve rien sur un lien défectueux) ; l'imprimante et le Wi-Fi viennent après les postes ; la sécurité est contrôlée avant de conclure ; le verdict et la signature terminent.",
        ),
        ordering=_shuffled_ordering(E18_STEPS, (2, 0, 5, 3, 6, 1, 4)),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Compléter le schéma de la baie",
        question_type="document_analysis",
        requirement_ids=("AP-36", "AP-31"),
        kind=KIND_SCHEMA,
        context=(
            "Le document 1 représente la baie murale du local technique de Lambert & Associés (fictif), vue de face. Quatre "
            "éléments sont remplacés par ①, ②, ③ et ④. Tu prépares la fiche de la baie pour le dossier remis au client et "
            "dois justifier la place de chaque élément."
        ),
        documents=(_schema("pr30-baie-a-completer", "Document 1 — Baie à compléter (schéma du cours)"),),
        instructions=("Nomme les éléments ①, ②, ③ et ④ et justifie la place de chacun.",),
        criteria=(
            _c("Éléments", 2, " ; ".join(f"{m} {name}" for m, name in RACK_BLANK_ANSWERS.items()) + " (0,5 pt par élément)."),
            _c("Justification", 2, "Panneau en haut, switch juste dessous (cordons courts, passe-câbles entre les deux) ; onduleur, lourd, en bas ; bandeau de prises tout en bas, près de l'arrivée électrique."),
        ),
        correction=(
            "① est le panneau de brassage, où arrivent les câbles fixes des prises ; ② le switch, juste sous le passe-câbles pour des cordons de 0,5 m. ③ est l'onduleur : ses batteries sont lourdes, il va en bas. ④ est le bandeau de prises qui alimente la baie.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Compléter l'arbre de recette d'un poste",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_SCHEMA,
        context=(
            "Le document 1 est l'arbre que l'atelier suit quand un poste échoue à la recette. Pour quatre questions, la piste "
            "à suivre en cas de « non » est remplacée par ①, ②, ③ et ④. Tu complètes l'arbre pour l'affiche de l'atelier."
        ),
        documents=(_schema("pr30-arbre-recette-a-completer", "Document 1 — Arbre de recette à compléter (schéma du cours)"),),
        instructions=("Donne la piste de ①, ②, ③ et ④ et explique pourquoi l'ordre des questions compte.",),
        criteria=(
            _c("Pistes", 3, " ; ".join(f"{m} {a}" for m, a in TREE_BLANK_ANSWERS.items()) + " (0,75 pt par piste)."),
            _c("Ordre", 1, "Du physique vers l'application : chaque contrôle suppose les précédents réussis ; on traite seulement le premier échec."),
        ),
        correction=(
            "① lien physique (cordon, prise, brassage, port ; rapport du testeur) ; ② adressage (DHCP, VLAN du port, doublon) ; ③ poste distant (serveur éteint, pare-feu, autre réseau) ; ④ partage (chemin, compte enregistré, droits).",
            "Un ping du serveur ne prouve rien sans adresse valide : on suit l'ordre et on corrige le premier « non ».",
        ),
    ),
    PR06Item(
        key="E21",
        usage=USAGE_PRACTICE,
        title="Parcourir l'arbre de recette",
        question_type="short_answer",
        requirement_ids=R_DIAG,
        kind=KIND_TREE,
        context=(
            "À la recette d'un poste ajouté plus tard chez Lambert & Associés (fictif), les voyants de la carte et du port "
            "sont allumés, ipconfig montre 192.168.50.123, masque 255.255.255.0, passerelle 192.168.50.1. Mais le ping de "
            "192.168.50.1 répond « Délai d'attente de la demande dépassé » quatre fois."
        ),
        instructions=("Indique où l'arbre de recette s'arrête, la piste et deux vérifications à faire.",),
        criteria=(
            _c("Arrêt", 1, f"Question {E21_RESULT[0]} (ping de la passerelle : non)."),
            _c("Piste et vérifications", 2, f"{E21_RESULT[1]} Vérifier : pare-feu ou logiciel de sécurité du poste, ping de la passerelle depuis un autre poste (la box répond-elle ?), câble et port de la box dans la baie."),
        ),
        correction=(
            f"Questions 1 et 2 : oui. Question {E21_RESULT[0]} : non. Piste : {E21_RESULT[1].lower()} Si la box répond aux autres postes, le problème est propre à ce poste (pare-feu, logiciel installé) ; sinon, c'est la box ou son raccordement.",
        ),
    ),
    PR06Item(
        key="E22",
        usage=USAGE_PRACTICE,
        title="Exigence des consignes ou complément du parcours ?",
        question_type="classification",
        requirement_ids=("AP-38", "AP-C01"),
        kind=KIND_REQ,
        context=(
            "Pour préparer l'épreuve, tu relies chaque tâche du laboratoire à la liste des exigences des consignes "
            "officielles (pp. 5-6). Certaines tâches y figurent ; d'autres sont des compléments utiles du parcours, qui ne "
            "sont pas exigés par la liste. Tu classes dix tâches du dossier de Lambert & Associés (fictif)."
        ),
        instructions=("Range chaque tâche : exigence officielle ou complément pédagogique.",),
        criteria=(
            _c("Tri", 5, " ; ".join(f"{t} → {k}" + (f" ({r})" if r.startswith("AP-") else "") for t, k, r in REQ_TASKS) + " (0,5 pt par tâche)."),
        ),
        correction=(
            "Figurent dans la liste officielle : le code des couleurs RJ45 (AP-34), l'adressage IP (AP-30), domaine et groupe de travail (AP-24), la sécurisation du Wi-Fi (AP-33), le dépannage de l'accès au réseau (AP-37).",
            "Sont des compléments : le budget, l'onduleur, le VLAN invités, la protection antistatique (AP-C02) et la rédaction du rapport (AP-C01). Ils aident à répondre en technicien, mais ne sont pas des sujets imposés.",
        ),
        classification=Classification(categories=REQ_KINDS, elements=tuple(t for t, _k, _r in REQ_TASKS), correct=E22_CORRECT),
    ),
    PR06Item(
        key="E23",
        usage=USAGE_PRACTICE,
        title="Rédiger la validation et la réserve du chantier",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Le chantier de Lambert & Associés (fictif) se termine. Le document 1 donne les critères d'acceptation écrits avec "
            "la directrice, mesurés à la première recette puis après les corrections. Le test de coupure de courant n'a pas pu "
            "être fait : il couperait Internet et le serveur pendant les heures de bureau."
        ),
        documents=(_table("Document 1 — Critères d'acceptation (support fictif)", ("Critère", "1re recette", "Après corrections"),
                          *_measure_rows(FINAL_REPORT.measures)),),
        instructions=(
            "Rédige les rubriques « Validation » et « Risques résiduels et limites » du rapport.",
            "Rédige trois phrases pour la directrice, sans jargon, avec la suite prévue.",
        ),
        criteria=(
            _c("Validation", 2, _results_text(FINAL_REPORT.measures) + f" ; verdict : {FINAL_REPORT.verdict.lower()}."),
            _c("Limites et message", 2, "Arrêt du serveur sur coupure non vérifié : réserve écrite, test daté (un samedi, avec accord) ; message clair : installé et vérifié, un point reste à tester, date proposée ; aucune clé ni mot de passe."),
        ),
        correction=(
            f"Validation : liens 10/10 et postes 6/6 après corrections, 0 % de pertes, signal Wi-Fi au-dessus de l'objectif, invité refusé sur le serveur : atteints. Coupure de courant : non mesurée, non concluante. Verdict : {FINAL_REPORT.verdict.lower()} ; décision : {FINAL_REPORT.decision.lower()}.",
            f"Message possible : « {FINAL_REPORT.client_message} »",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (réserve « exam » uniquement, jamais affiché dans le cours)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Dimensionner l'équipement d'une annexe",
        question_type="document_analysis",
        requirement_ids=("AP-36", "AP-38"),
        kind=KIND_INV,
        context=(
            f"Une annexe d'un bureau d'études (fictif) reçoit {X01_LINKS} prises reliées à une baie, plus la box et un NAS "
            "branchés directement au switch. Le document 1 donne la longueur à prévoir de chaque lien. On garde 20 % de "
            "ports libres ; le câble se vend en boîtes de 305 m et un lien ne se raboute jamais."
        ),
        documents=(_text_doc("Document 1 — Longueurs à prévoir, en mètres (support fictif)",
                             ", ".join(str(n) for n in X01_LENGTHS) + f" (total {sum(X01_LENGTHS)} m)"),),
        instructions=("Donne la taille du switch, le nombre de panneaux de 24 ports et le nombre de boîtes de câble, avec les calculs.",),
        criteria=(
            _c("Switch et panneaux", 1, f"{X01_LINKS} × 1,2 → {X01_NEEDED - X01_UPLINKS} + {X01_UPLINKS} = {X01_NEEDED} ports → switch de {X01_SWITCH} ports ; {X01_PANELS} panneau(x) de 24 ports."),
            _c("Câble", 1, f"Total {sum(X01_LENGTHS)} m, mais un lien ne se raboute pas : en rangeant les plus longs d'abord, {X01_BOXES} boîtes de 305 m."),
        ),
        correction=(
            f"Ports : {X01_LINKS} liens + 20 % = {X01_LINKS * 1.2:g}, arrondi à {X01_NEEDED - X01_UPLINKS}, plus box et NAS : {X01_NEEDED}, au-delà de 24 → switch de {X01_SWITCH} ports. Panneaux : {X01_LINKS} ports tiennent dans {X01_PANELS} panneau de 24.",
            f"Câble : {sum(X01_LENGTHS)} m dépassent une boîte ; chaque lien doit tenir dans le reste d'une boîte : {X01_BOXES} boîtes.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Verdicts du testeur sur trois liens",
        question_type="document_analysis",
        requirement_ids=R_CABLE,
        kind=KIND_CABLE,
        context=(
            "Dans un bâtiment voisin de Lambert & Associés (fictif), un installateur a posé trois liens Cat6 et les a "
            "testés (document 1). La limite du lien permanent est de 90 m. Il veut les mettre en service le jour même."
        ),
        documents=(_table("Document 1 — Rapport du testeur (support fictif)", ("Lien",), *((label,) for label, _t in X02_TESTS)),),
        instructions=("Donne le verdict de chaque lien et la suite à donner.",),
        criteria=(
            _c("Verdicts", 1.5, " ; ".join(f"{label.split(' :')[0]} → {r}" for (label, _t), r in zip(X02_TESTS, X02_RESULTS, strict=True)) + " (0,5 pt par lien)."),
            _c("Suite", 0.5, "B08 : autre chemin plus court ou switch plus proche ; B09 : refaire le raccordement (même norme aux deux bouts) et retester ; seul B07 est mis en service."),
        ),
        correction=(
            "B07 (88 m, conforme) est accepté. B08 dépasse 90 m : trop long, même s'il passe le test. B09 a deux fils croisés : défaut de câblage, raccordement à refaire.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Erreurs dans un relevé d'adresses",
        question_type="document_analysis",
        requirement_ids=R_IP + ("AP-37",),
        kind=KIND_IP,
        context=(
            f"Le réseau de Lambert & Associés (fictif) est {NETWORK}, passerelle et DNS {ROUTER_IP}, étendue DHCP "
            f"{POOL[0]}–{POOL[1]}. Après un déménagement de matériel, tu relèves la configuration de quatre appareils "
            "(document 1). L'imprimante et une station ne fonctionnent plus."
        ),
        documents=(_table("Document 1 — Relevé (support fictif)", ("Appareil", "Adresse / préfixe", "Passerelle", "DNS"),
                          *_host_rows(X03_HOSTS)),),
        instructions=("Relève les erreurs et donne la cause probable de chacune.",),
        criteria=(
            _c("Erreurs", 1.5, " ; ".join(e.rstrip(".") for e in X03_ERRORS) + "."),
            _c("Causes", 0.5, "IMP-01 a reçu par erreur l'adresse du serveur (conflit : changer l'adresse fixe de l'imprimante) ; ETUDES2 n'a pas obtenu de bail DHCP (lien, port, VLAN)."),
        ),
        correction=(
            "IMP-01 porte la même adresse que SRV-01 : conflit, l'un des deux devient injoignable ; on remet l'imprimante en 192.168.50.20. ETUDES2 est en 169.254 : pas de bail DHCP, on vérifie le lien, le port et son VLAN, puis ipconfig /renew.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Droits d'une nouvelle stagiaire",
        question_type="short_answer",
        requirement_ids=R_ACC,
        kind=KIND_ACC,
        context=(
            "Une stagiaire arrive au bureau d'études de Lambert & Associés (fictif). On lui crée un compte sur SRV-01 "
            "membre de Utilisateurs et G_Etudes. Les partages donnent « Utilisateurs authentifiés : Modifier » ; NTFS : "
            "Commun → Utilisateurs Modification ; Administration → G_Administration Modification ; Etudes → G_Etudes "
            "Modification, G_Direction Lecture ; Compta → G_Compta Modification, G_Direction Lecture."
        ),
        instructions=("Donne son droit effectif sur les quatre dossiers et dis si cela respecte les besoins du client.",),
        criteria=(
            _c("Droits", 1.5, ", ".join(f"{f} : {v.lower()}" for f, v in X04_ACCESS.items()) + "."),
            _c("Conformité", 0.5, "Oui : comme le bureau d'études, rien sur Administration ni Compta ; compte à désactiver à la fin du stage."),
        ),
        correction=(
            "Par le réseau, le plus restrictif du partage (modifier) et de NTFS s'applique : NTFS décide. Elle modifie Commun et Etudes, n'a aucun accès à Administration ni à Compta. C'est conforme ; on note la date de fin de stage pour désactiver le compte.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Choisir le modèle de gestion des comptes",
        question_type="short_answer",
        requirement_ids=R_ACC,
        kind=KIND_ACC,
        context=(
            "Un bureau (fictif) de huit postes demande que l'écran se verrouille après cinq minutes et que les mots de "
            "passe respectent les mêmes règles sur tous les PC. Les postes ont Windows 11 Pro. Le technicien précédent "
            "propose un groupe de travail « puisqu'il y a moins de dix postes »."
        ),
        instructions=("Donne ton choix (groupe de travail ou domaine) et justifie en deux arguments.",),
        criteria=(
            _c("Choix", 1, f"{X05_MODEL}."),
            _c("Arguments", 1, "Règles imposées à tous = gestion centrale (stratégies de groupe) ; en groupe de travail, il faudrait régler chaque poste à la main, sans garantie ; Windows Pro peut rejoindre un domaine."),
        ),
        correction=(
            f"Le nombre de postes n'est pas le seul repère : des règles imposées à tous demandent une gestion centrale. {X05_MODEL} : les stratégies de groupe s'appliquent à chaque poste et à chaque compte, et les postes Windows 11 Pro peuvent le rejoindre.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Préparer un PC pour Windows 11",
        question_type="document_analysis",
        requirement_ids=R_OS,
        kind=KIND_OS,
        context=(
            "Chez Lambert & Associés (fictif), un ancien poste doit passer à Windows 11 Pro avant la recette. Les données "
            "de l'utilisatrice sont déjà sauvegardées et la copie est vérifiée. Le document 1 donne les relevés de msinfo32, "
            "tpm.msc et de la Gestion des disques."
        ),
        documents=(_table("Document 1 — Relevés du poste (support fictif)",
                          ("PC", "Processeur", "Mémoire", "Stockage", "Firmware", "TPM", "Disque"), *_pc_rows((("POSTE", X06_PC),))),),
        instructions=("Dis si Windows 11 est possible et liste les réglages à faire, dans l'ordre.",),
        criteria=(
            _c("Verdict", 0.5, f"{X06_CHECK[0]}."),
            _c("Réglages", 1.5, " ; ".join(X06_CHECK[2]) + "."),
        ),
        correction=(
            f"{X06_CHECK[0]} : le matériel convient (processeur listé, TPM 2.0 présent). Le disque est en MBR et le PC démarre en mode hérité : après la sauvegarde vérifiée, conversion en GPT (mbr2gpt), passage en UEFI, activation du TPM, puis du démarrage sécurisé.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Corriger une configuration Wi-Fi dangereuse",
        question_type="document_analysis",
        requirement_ids=R_WIFI,
        kind=KIND_WIFI,
        context=(
            "Dans une agence voisine (fictive), le point d'accès a été installé par un ancien prestataire. Le document 1 "
            "donne sa configuration. Les clients en rendez-vous utilisent le même réseau que le personnel."
        ),
        documents=(_table("Document 1 — Configuration relevée (support fictif)", ("Paramètre", "Valeur"),
                          ("SSID", X07_AP.ssid), ("Sécurité", X07_AP.security), ("Clé", X07_AP.passphrase),
                          ("Canal 2,4 GHz / largeur", f"{X07_AP.channel_24} / {X07_AP.width_24} MHz"),
                          ("Invités", "même réseau que le personnel")),),
        instructions=("Relève les défauts et donne les corrections.",),
        criteria=(
            _c("Défauts", 1.5, " ; ".join(f"{p} : {c}" for p, c in X07_AUDIT) + "."),
            _c("Priorité", 0.5, "Isoler les invités et changer la sécurité avant tout ; le canal 6 est correct."),
        ),
        correction=(
            "WPA (TKIP) est obsolète : WPA2/WPA3-Personnel en AES. La clé contient le nom de l'agence : nouvelle clé longue. Les invités sur le réseau du personnel peuvent atteindre les ordinateurs : réseau invités isolé. Le canal 6 en 20 MHz est correct.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Deux postes échouent à la recette",
        question_type="document_analysis",
        requirement_ids=R_DIAG,
        kind=KIND_RECETTE,
        context=(
            "À la recette d'un cabinet (fictif), deux postes échouent. Les contrôles se font dans l'ordre : lien, adresse, "
            "passerelle, serveur, Internet, partage. Le document 1 donne les résultats. Les autres postes passent tous les "
            "contrôles, Internet compris."
        ),
        documents=(_table("Document 1 — Fiche de recette (support fictif)", _RECETTE_HEAD, *_recette_rows(X08_RESULTS)),),
        instructions=("Donne la piste de chaque poste et la première vérification à faire.",),
        criteria=(
            _c("Pistes", 1, " ; ".join(f"{p} → {d}" for p, d in X08_DIAG.items()) + "."),
            _c("Vérifications", 1, "ACCUEIL : DNS du poste (ipconfig /all, nslookup d'un nom), les autres postes ayant Internet ; ETUDES1 : serveur joignable depuis un autre poste ? sinon pare-feu du poste, VLAN."),
        ),
        correction=(
            "ACCUEIL joint la passerelle et le serveur, mais pas Internet par un nom : comme les autres postes ont Internet, on vérifie son DNS (configuration manuelle oubliée). ETUDES1 joint la passerelle, pas le serveur : on vérifie que le serveur répond aux autres, puis le pare-feu du poste.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Conclure la recette d'un petit réseau",
        question_type="document_analysis",
        requirement_ids=R_WRITE,
        kind=KIND_RECETTE,
        context=(
            "Fin de chantier dans un cabinet (fictif). Le document 1 donne les critères d'acceptation mesurés avant et après "
            "la dernière correction. Le test de l'isolement des invités n'a pas été fait : aucun smartphone de test n'était "
            "disponible. Le gérant veut signer « réception sans réserve »."
        ),
        documents=(_table("Document 1 — Critères avant / après (support fictif)", ("Critère", "Avant", "Après"),
                          *_measure_rows(X09_MEASURES)),),
        instructions=("Donne le résultat de chaque critère, le verdict, la décision et ce que tu réponds au gérant.",),
        criteria=(
            _c("Résultats et verdict", 1, _results_text(X09_MEASURES) + f" ; {X09_VERDICT.lower()}."),
            _c("Décision et réponse", 1, f"{X09_DECISION} ; pas de « sans réserve » : test d'isolement daté, à faire avec un appareil invité."),
        ),
        correction=(
            f"Trois critères atteints, l'isolement des invités non mesuré : non concluant. {X09_VERDICT}. On explique au gérant que ce point protège ses fichiers : la réception est signée avec réserve et le test est planifié.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Synthèse de recette pour la directrice",
        question_type="long_answer",
        requirement_ids=R_WRITE,
        kind=KIND_WRITE,
        context=(
            "Tes notes techniques de recette chez Lambert & Associés (fictif) : « P08 fil 6 ouvert, refait T568B, PASS ; "
            "ETUDES2 port 7 en VLAN 60, remis en VLAN 1, renew OK ; COMPTA cmdkey SRV-01\\amartin supprimé ; 6/6 OK ; "
            "test UPS non fait. » La directrice n'est pas informaticienne et veut savoir où en est son installation."
        ),
        instructions=("Rédige en quatre à six phrases ta synthèse pour la directrice.",),
        criteria=(
            _c("Clarté et exactitude", 1, "Sans sigle : trois petits défauts trouvés (une prise, un réglage du switch, un identifiant enregistré), corrigés et vérifiés ; chacun a Internet, l'imprimante et ses dossiers."),
            _c("Limite et suite", 1, "Arrêt automatique du serveur en cas de coupure non encore testé : date proposée, accord demandé ; aucune accusation de l'accueil, aucun mot de passe."),
        ),
        correction=(
            "Exemple : « Votre réseau est installé et vérifié poste par poste. Ce matin, nous avons trouvé trois petits défauts — une prise murale, un réglage de l'armoire réseau et un ancien identifiant mémorisé sur un PC — tous corrigés et contrôlés devant vous. Chacun accède à Internet, à l'imprimante et à ses dossiers. Il reste à vérifier que le serveur s'éteint proprement lors d'une coupure de courant : je vous propose de le faire samedi prochain. »",
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
            errors.append(f"{item.key} : l'exigence AP-36, AP-37 ou AP-38 doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue au mini-examen.")
    if len(PRACTICE_ITEMS) < 20 or len(EXAM_ITEMS) != 10:
        errors.append("Ticket #229 : au moins 20 exercices transversaux et un mini-examen de 10 questions.")
    if [i.kind for i in PRACTICE_ITEMS].count(KIND_SCHEMA) != 2:
        errors.append("Deux schémas à compléter attendus.")
    if E02_NOW_OK is not True or E02_LATER_OK is not False:
        errors.append("E02 : le switch de 16 ports doit suffire aujourd'hui et pas après l'extension.")
    if [v[0] for v in E03_CHECKS.values()] != [W11_SETTINGS, W11_NO, W11_SETTINGS]:
        errors.append("E03 : verdicts Windows 11 inattendus.")
    if len({h.split(" :")[0] for h in DRAFT_ERRORS}) != 3:
        errors.append("E07 : trois équipements fautifs attendus.")
    if E10_MODELS != (MODEL_WG, MODEL_DOMAIN, MODEL_DOMAIN) or X05_MODEL != MODEL_DOMAIN:
        errors.append("E10/X05 : modèles inattendus.")
    if (STORED_ACCESS, RIGHT_ACCESS) != ("Aucun accès", "Modification"):
        errors.append("E12 : droits inattendus.")
    if CHANNEL_24 != E15_BEST or not ONE_AP_ENOUGH:
        errors.append("E15 : canal ou couverture inattendus.")
    if E21_RESULT[0] != 3:
        errors.append("E21 : parcours inattendu.")
    if len(set(X02_RESULTS)) != 3 or len(X03_ERRORS) < 3:
        errors.append("X02/X03 : résultats inattendus.")
    if X09_VERDICT != V_RESERVE or X09_DECISION != D_FOLLOWUP or INCONCLUSIVE not in tuple(m.result for m in X09_MEASURES):
        errors.append("X09 : validation avec réserve attendue.")
    if X04_ACCESS != {f: access("jroux", f) for f in FOLDERS} or ACCOUNTS_BY_LOGIN["jroux"].groups != X04_STAGIAIRE.groups:
        errors.append("X04 : la stagiaire doit avoir les droits du bureau d'études.")
    return errors

"""PR23 « Partage de dossiers, imprimantes et permissions » — exercices corrigés et mini-examen
(ticket #223).

Même organisation que PR22 (`app.v1.ampcr_pratique_pr22_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (partager un dossier, une imprimante, dépanner un
  accès), classements (droit minimal, piste d'un échec d'accès, piste d'une panne d'impression,
  accès Samba), **quatre schémas à compléter** (chemin UNC, deux barrières, imprimantes, droits
  Unix, servis en SVG), **matrices de droits** à remplir ou à corriger et **diagnostics sur
  relevés** (ping, net use, net view, Test-NetConnection, icacls, net share, Get-Printer,
  ls, getfacl, smb.conf) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, postes et serveurs sont **fictifs** ; les droits effectifs, les
accès Linux et les pistes de diagnostic des énoncés et des corrigés viennent des fonctions de
`app.v1.ampcr_pratique_pr23_figures` (mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr22_figures import USERS_DOMAIN
from app.v1.ampcr_pratique_pr23_figures import (
    ACCESS_LEVELS,
    ACCESS_MATRIX,
    AUTH_USERS,
    CLAIRE,
    JULIE,
    LAYERS_BLANK_ANSWERS,
    LEVEL_FULL,
    LEVEL_MODIFY,
    LEVEL_NONE,
    LEVEL_READ,
    LIMIT_NTFS,
    LIMIT_SHARE,
    LOCAL_ADMINS,
    LX_SHARE,
    MATRIX_PATHS,
    NET_PRINTER,
    NET_PRINTER_IP,
    NTFS_TREE,
    P_DEVICE,
    PRINT_DIAGNOSES,
    PRINT_HOST,
    PRINT_KEYS,
    PRINTER_BLANK_ANSWERS,
    PRINTER_STEPS,
    S_AUTH,
    S_NAME,
    S_NET,
    S_RIGHTS,
    S_SHARE,
    S_SMB,
    SAM,
    SERVER_IP,
    SERVER_NAME,
    SHARE_DIAGNOSES,
    SHARE_ROOT,
    SHARE_STEPS,
    SHARES,
    SMB_CONF_LINES,
    SMB_PORT,
    STATIC_BY_KEY,
    TROUBLE_STEPS,
    UNC_BLANK_ANSWERS,
    UNIX_BLANK_ANSWERS,
    USB_PRINTER,
    AccessState,
    Account,
    Ace,
    Folder,
    LinuxUser,
    PrintState,
    SambaShare,
    Share,
    dir_lines,
    effective_access,
    first_failure,
    get_printer_lines,
    getfacl_lines,
    icacls_lines,
    limiting_layer,
    linux_effective,
    ls_lines,
    net_share_lines,
    net_use_lines,
    ntfs_level,
    ping_lines,
    port_test_lines,
    print_checks,
    print_diagnosis,
    samba_level,
    share_checks,
    share_diagnosis,
    share_level,
    short_path,
    unc,
    unix_access,
)

PR23_CODE = "PR23"

KIND_ORDER = "ordonnancement"
KIND_MATRIX = "matrice de droits"
KIND_SCHEMA = "schéma à compléter"
KIND_DIAG = "diagnostic sur relevés de commandes"
KIND_PRINT = "imprimante partagée"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-25", "AP-26", "AP-27"})
R_SHARE = ("AP-25", "AP-26")
R_RIGHTS = ("AP-27",)
R_PRINT = ("AP-25",)


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


def _rule(entries: tuple[Ace, ...]) -> str:
    return "; ".join(f"{e.principal} : {'Refuser ' if e.deny else ''}{e.right}" for e in entries) or "—"


def _tree_with(path: str, folder: Folder) -> dict[str, Folder]:
    return {**NTFS_TREE, path: folder}


COMPTA = f"{SHARE_ROOT}\\Compta"
PAIE = f"{SHARE_ROOT}\\Compta\\Paie"
ARCHIVES = f"{SHARE_ROOT}\\Archives"

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(SHARE_STEPS)
E02_STEPS = _labels(PRINTER_STEPS)
E03_STEPS = _labels(TROUBLE_STEPS)

E04_CATEGORIES = (LEVEL_READ, LEVEL_MODIFY, LEVEL_FULL)
E04_CASES: tuple[tuple[str, str], ...] = (
    ("Enregistrer ses nouveaux devis dans le dossier", LEVEL_MODIFY),
    ("Consulter les factures et les imprimer", LEVEL_READ),
    ("Donner l'accès du dossier à un nouveau groupe (changer les autorisations)", LEVEL_FULL),
    ("Supprimer les brouillons devenus inutiles", LEVEL_MODIFY),
    ("Lancer le logiciel de caisse installé dans le dossier partagé", LEVEL_READ),
    ("Prendre possession d'un dossier dont le propriétaire a quitté l'entreprise", LEVEL_FULL),
    ("Renommer un sous-dossier", LEVEL_MODIFY),
)
E04_CORRECT = tuple(E04_CATEGORIES.index(level) for _t, level in E04_CASES)

E05_CATEGORIES = SHARE_DIAGNOSES
E05_CASES: tuple[tuple[str, str], ...] = (
    ("net use : « Erreur système 86. Le mot de passe réseau spécifié est incorrect. »", "compte"),
    (f"ping {SERVER_IP} : délai d'attente dépassé ; le câble du serveur a été débranché", "ip"),
    (f"net use Z: \\\\{SERVER_NAME}\\Comptas : « Erreur système 67. Le nom réseau est introuvable. »", "partage"),
    (f"\\\\{SERVER_IP}\\Compta s'ouvre, \\\\{SERVER_NAME}\\Compta répond « chemin réseau introuvable »", "nom"),
    ("« Erreur système 5. Accès refusé. » alors que net view liste bien le partage", "droits"),
    (f"Le ping répond ; Test-NetConnection -Port {SMB_PORT} : TcpTestSucceeded False ; réseau du serveur en profil Public", "smb"),
    ("« Erreur système 1219 » : une connexion au serveur existe déjà avec un autre compte", "compte"),
    ("Le partage s'ouvre, mais enregistrer un fichier est refusé : le partage n'accorde que Lecture", "droits"),
)
E05_CORRECT = tuple(E05_CATEGORIES.index(share_diagnosis(first_failure(k))) for _t, k in E05_CASES)

E06_CATEGORIES = PRINT_DIAGNOSES
E06_CASES: tuple[tuple[str, str], ...] = (
    ("Un PDF de 300 pages en erreur bloque tous les documents suivants dans la file", "file"),
    (f"Plus personne n'imprime sur {USB_PRINTER} depuis que {PRINT_HOST} est éteint le soir", "hote"),
    (f"Connexion à \\\\{SERVER_NAME}\\{NET_PRINTER} : l'installation du pilote demande un administrateur", "pilote"),
    (f"{NET_PRINTER} « hors connexion » ; sa page de configuration indique 192.168.20.117 au lieu de .50", "imprimante"),
    ("Un stagiaire reçoit « Accès refusé » en ajoutant l'imprimante de la direction, réservée à G_Direction", "droit"),
    ("L'imprimante réseau affiche « bourrage papier » sur son écran", "imprimante"),
    ("Le service Spouleur d'impression est arrêté sur le serveur d'impression", "file"),
)
E06_CORRECT = tuple(
    E06_CATEGORIES.index(print_diagnosis(first_failure(k, PRINT_KEYS))) for _t, k in E06_CASES
)

# E07 : accès Samba à /srv/partages/projets
E07_MODE, E07_OWNER, E07_GROUP = 0o2770, "root", "projets"
E07_ACL = {"stagiaires": "r-x"}
E07_SHARE = SambaShare("projets", "/srv/partages/projets", ("projets", "stagiaires", "direction"), read_only=False)
E07_USERS: tuple[LinuxUser, ...] = (
    LinuxUser("lea", ("projets",)),
    LinuxUser("tom", ("stagiaires",)),
    LinuxUser("max", ("direction",)),
    LinuxUser("zoe", ("compta",)),
    LinuxUser("ines", ("projets", "stagiaires")),
    LinuxUser("sam", ("stagiaires", "compta")),
)
E07_ANSWERS = tuple(
    linux_effective(u, mode=E07_MODE, owner=E07_OWNER, group=E07_GROUP, acl=E07_ACL, share=E07_SHARE) for u in E07_USERS
)
E07_CORRECT = tuple(ACCESS_LEVELS.index(a) for a in E07_ANSWERS)

E09_ANSWERS = LAYERS_BLANK_ANSWERS

# E12 : matrice des droits à remplir
E12_MATRIX = ACCESS_MATRIX

# E13 : sous-dossier Paie créé sous Compta, héritage actif
E13_TREE_BEFORE = _tree_with(PAIE, Folder(PAIE, ()))
E13_BEFORE = effective_access(JULIE, PAIE, tree=E13_TREE_BEFORE)
E13_AFTER = effective_access(JULIE, PAIE)
E13_CLAIRE_AFTER = effective_access(CLAIRE, PAIE)

# E14 : refus explicite pour les stagiaires
E14_STAGIAIRE = Account("tmoreau", "Théo Moreau (stagiaire)", (USERS_DOMAIN, "G_Compta", "G_Stagiaires"))
E14_TREE = _tree_with(COMPTA, Folder(COMPTA, (*NTFS_TREE[COMPTA].entries, Ace("G_Stagiaires", "Contrôle total", deny=True))))
E14_RESULT = effective_access(E14_STAGIAIRE, COMPTA, tree=E14_TREE)
E14_JULIE = effective_access(JULIE, COMPTA, tree=E14_TREE)
E14_FACTURES = effective_access(E14_STAGIAIRE, f"{COMPTA}\\Factures", tree=E14_TREE)

# E15 : local ou réseau
E15_REMOTE = effective_access(JULIE, ARCHIVES)
E15_LOCAL = effective_access(JULIE, ARCHIVES, remote=False)
E15_LIMIT = limiting_layer(JULIE, ARCHIVES)

# E16 : ping OK mais accès refusé
E16_SHARE = share_level(SAM, COMPTA)
E16_NTFS = ntfs_level(SAM, COMPTA)
E16_DIAG = share_diagnosis(share_checks(AccessState(effective=effective_access(SAM, COMPTA), needed=LEVEL_READ)))
E16_TREE_AFTER = _tree_with(COMPTA, Folder(COMPTA, (*NTFS_TREE[COMPTA].entries, Ace("G_Secretariat", "Lecture et exécution"))))
E16_AFTER = effective_access(SAM, COMPTA, tree=E16_TREE_AFTER)
E16_AFTER_PAIE = effective_access(SAM, PAIE, tree=E16_TREE_AFTER)

# E17 : nom introuvable
E17_DIAG = share_diagnosis(share_checks(AccessState(name_ok=False)))

# E18 : imprimante hors connexion
E18_NEW_IP = "192.168.20.117"
E18_DIAG = print_diagnosis(print_checks(PrintState(device_ip=E18_NEW_IP)))

# E19 : Samba, la direction ne peut pas écrire
E19_PAUL = LinuxUser("paul", ("direction",))
E19_BEFORE = linux_effective(E19_PAUL)
E19_ONLY_SAMBA = linux_effective(E19_PAUL, share=SambaShare("compta", LX_SHARE.path, LX_SHARE.valid_users, True,
                                                            ("compta", "direction")))
E19_ONLY_ACL = linux_effective(E19_PAUL, acl={"direction": "rwx"})
E19_AFTER = linux_effective(E19_PAUL, acl={"direction": "rwx"},
                            share=SambaShare("compta", LX_SHARE.path, LX_SHARE.valid_users, True, ("compta", "direction")))

# --- Mini-examen -------------------------------------------------------------------------------

X01_TREE = {
    "D:\\Partages": NTFS_TREE[SHARE_ROOT],
    "D:\\Partages\\Devis": Folder("D:\\Partages\\Devis", (Ace("G_Commerciaux", "Modification"),)),
}
X01_SHARES = {"Devis": Share("Devis", "D:\\Partages\\Devis", (Ace(AUTH_USERS, "Lecture"),))}
X01_ACCOUNT = Account("nlambert", "Nora Lambert (commerciale)", (USERS_DOMAIN, "G_Commerciaux"))
X01_REMOTE = effective_access(X01_ACCOUNT, "D:\\Partages\\Devis", tree=X01_TREE, shares=X01_SHARES)
X01_LOCAL = effective_access(X01_ACCOUNT, "D:\\Partages\\Devis", remote=False, tree=X01_TREE, shares=X01_SHARES)
X01_LIMIT = limiting_layer(X01_ACCOUNT, "D:\\Partages\\Devis", tree=X01_TREE, shares=X01_SHARES)
X02_DIAG = share_diagnosis(share_checks(AccessState(smb_open=False)))
X07_PERMS = unix_access(0o750, "root", "rh", "lina", ("compta",))
X07_PERMS_FIX = unix_access(0o750, "root", "rh", "lina", ("compta", "rh"))

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le partage d'un dossier sur un serveur",
        question_type="ordering",
        requirement_ids=R_SHARE,
        kind=KIND_ORDER,
        context=(
            f"Une fiduciaire de douze postes en domaine veut partager le dossier Compta de son serveur {SERVER_NAME} "
            "pour la comptabilité seulement. Ta collègue a noté les sept étapes de la procédure sur un brouillon, "
            "dans le désordre."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, "Dossier → groupes → NTFS → partage → pare-feu → test depuis un poste → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On prépare le dossier sur un volume NTFS du serveur. 2. On crée les groupes et on y place les comptes. 3. On règle les autorisations NTFS (onglet Sécurité) pour les groupes et on retire Tout le monde. 4. On partage le dossier (Partage avancé) et on règle les autorisations du partage.",
            f"5. On vérifie le profil réseau (Privé ou Domaine) et la règle « Partage de fichiers et d'imprimantes » (TCP {SMB_PORT}). 6. On teste depuis un poste avec un compte de chaque groupe : l'accès prévu fonctionne, les autres sont refusés. 7. On consigne la matrice des droits et le chemin UNC. Régler NTFS avant de partager évite d'ouvrir un dossier trop largement, même quelques minutes.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 6, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le partage d'une imprimante réseau",
        question_type="ordering",
        requirement_ids=R_PRINT,
        kind=KIND_ORDER,
        context=(
            f"Un bureau d'études achète une imprimante réseau {NET_PRINTER} et veut la rendre disponible à ses dix "
            f"postes par son serveur {SERVER_NAME}, qui servira de serveur d'impression. La fiche d'installation en "
            "sept étapes a été mélangée."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, "Installer sur l'hôte → fixer l'adresse → partager → droits → pare-feu → connecter les postes → tester et consigner (0,5 pt par étape)."),
        ),
        correction=(
            f"1. On installe l'imprimante et son pilote sur le serveur et on imprime une page de test locale. 2. On fixe son adresse ({NET_PRINTER_IP}, adresse fixe ou réservation DHCP). 3. On la partage avec un nom court. 4. On règle les droits : Imprimer pour les groupes concernés.",
            f"5. On vérifie la règle de pare-feu « Partage de fichiers et d'imprimantes ». 6. On connecte chaque poste à \\\\{SERVER_NAME}\\{NET_PRINTER} (un administrateur installe le pilote si Windows le demande). 7. Page de test depuis chaque poste, puis on note le chemin, l'adresse et le pilote. Sans adresse fixe, l'imprimante passera un jour « hors connexion ».",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 6, 0, 5, 3, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le dépannage de l'accès à un partage",
        question_type="ordering",
        requirement_ids=("AP-25", "AP-27"),
        kind=KIND_ORDER,
        context=(
            "Le service d'assistance d'une PME reçoit souvent « je n'arrive pas à ouvrir le dossier partagé ». Tu "
            "rédiges la fiche de dépannage en huit étapes, du plus général (le serveur répond-il ?) au plus "
            "particulier (les permissions) ; le brouillon est dans le désordre."
        ),
        instructions=("Remets les huit étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Message → adresse IP → nom → partage de fichiers (445) → nom du partage → compte → permissions → consigner (0,5 pt par étape)."),
        ),
        correction=(
            f"1. On note le message exact (code d'erreur) et l'étendue (un poste, un compte ?). 2. Le serveur répond-il par son adresse IP ? 3. Son nom donne-t-il la bonne adresse ? 4. Le partage de fichiers répond-il (Test-NetConnection -Port {SMB_PORT}) ?",
            "5. Le partage demandé existe-t-il (net view) ? 6. Le compte et le mot de passe sont-ils acceptés ? 7. Les permissions effectives (partage + NTFS, la plus restrictive) suffisent-elles ? 8. On consigne. Le premier contrôle en échec désigne la piste : inutile de toucher aux droits si le nom n'est pas résolu.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (5, 2, 7, 0, 6, 3, 1, 4)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Quel droit minimal pour chaque besoin ?",
        question_type="classification",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            "Tu prépares les autorisations NTFS du dossier partagé d'un magasin. Le gérant a listé sept besoins de "
            "son personnel. Pour chacun, choisis le droit le plus faible qui suffit (principe du moindre "
            "privilège) parmi Lecture (ou Lecture et exécution), Modification et Contrôle total."
        ),
        instructions=("Range chaque besoin selon le droit minimal nécessaire.",),
        criteria=(
            _c("Classement", 3.5, "Consulter, lancer un programme → Lecture ; enregistrer, supprimer, renommer → Modification ; changer les autorisations, prendre possession → Contrôle total (0,5 pt par élément)."),
        ),
        correction=(
            "Lecture (et exécution) permet d'ouvrir, de copier, d'imprimer et de lancer un programme. Modification ajoute la création, l'enregistrement, le renommage et la suppression des fichiers et sous-dossiers : c'est le droit normal d'une équipe qui travaille dans un dossier.",
            "Contrôle total ajoute la modification des autorisations et la prise de possession : on le réserve aux administrateurs. Donner Contrôle total à une équipe lui permettrait de s'ouvrir ou de fermer elle-même l'accès aux autres.",
        ),
        classification=Classification(categories=E04_CATEGORIES, elements=tuple(t for t, _l in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Quelle piste pour chaque échec d'accès à un partage ?",
        question_type="classification",
        requirement_ids=("AP-25", "AP-27"),
        kind=KIND_DIAG,
        context=(
            f"Le serveur {SERVER_NAME} ({SERVER_IP}) partage le dossier Compta. En une semaine, l'assistance a noté huit "
            "signalements. Ordre des contrôles : adresse IP, nom, partage de fichiers (port 445), nom du partage, "
            "compte, permissions ; le premier en échec désigne la piste."
        ),
        instructions=("Range chaque signalement selon la piste à suivre.",),
        criteria=(
            _c("Classement", 4, "Câble → réseau ; IP oui, nom non → nom ; port 445 fermé → partage de fichiers bloqué ; erreur 67 → nom du partage ; 86 et 1219 → identification ; 5 et partage en Lecture → permissions (0,5 pt par élément)."),
        ),
        correction=(
            "Délai dépassé sur l'adresse IP avec un câble débranché : réseau. Le chemin par l'adresse IP fonctionne mais pas par le nom : résolution du nom. Le ping répond mais le port 445 ne répond pas : le partage de fichiers est bloqué (profil Public, pare-feu ou service). L'erreur 67 signale un nom de partage inexistant (« Comptas » au lieu de « Compta »).",
            "Les erreurs 86 (mot de passe) et 1219 (déjà connecté avec un autre compte) concernent l'identification. L'erreur 5 après un net view réussi, ou un enregistrement refusé sur un partage en Lecture : le serveur est joint et le compte accepté, ce sont les permissions.",
        ),
        classification=Classification(categories=E05_CATEGORIES, elements=tuple(t for t, _k in E05_CASES), correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Quelle piste pour chaque problème d'impression ?",
        question_type="classification",
        requirement_ids=R_PRINT,
        kind=KIND_PRINT,
        context=(
            f"Une agence a deux imprimantes partagées : {USB_PRINTER}, branchée en USB sur {PRINT_HOST}, et "
            f"{NET_PRINTER}, imprimante réseau à l'adresse {NET_PRINTER_IP} gérée par le serveur {SERVER_NAME}. "
            "Ordre des contrôles : hôte, imprimante, file d'attente, pilote, droit d'imprimer."
        ),
        instructions=("Range chaque problème selon la piste à suivre.",),
        criteria=(
            _c("Classement", 3.5, "Poste hôte éteint → hôte ; adresse changée, bourrage → imprimante ; document bloqué, spouleur arrêté → file ; installation du pilote refusée → pilote ; imprimante réservée à un groupe → droit (0,5 pt par élément)."),
        ),
        correction=(
            f"Une imprimante USB partagée dépend de son poste hôte : {PRINT_HOST} éteint, plus personne n'imprime. Une imprimante qui a changé d'adresse (DHCP) ou qui est en bourrage est en cause elle-même. Un document en erreur ou un spouleur arrêté bloquent la file d'attente.",
            "Depuis la mise à jour de sécurité d'août 2021, l'installation d'un pilote depuis un serveur d'impression demande par défaut un administrateur : c'est une piste « pilote ». Un « Accès refusé » sur une imprimante réservée à G_Direction relève du droit Imprimer.",
        ),
        classification=Classification(categories=E06_CATEGORIES, elements=tuple(t for t, _k in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Accès Samba : qui modifie, qui lit, qui n'entre pas ?",
        question_type="classification",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            "Un serveur Linux partage /srv/partages/projets avec Samba. ls -ld affiche « drwxrws---+ root projets » "
            "(mode 2770) et getfacl ajoute « group:stagiaires:r-x ». Dans smb.conf : valid users = @projets "
            "@stagiaires @direction ; read only = no. L'accès réel est le plus restrictif de Samba et des droits Unix."
        ),
        instructions=("Range chaque utilisateur selon son accès au partage.",),
        criteria=(
            _c("Classement", 3, "lea et ines (projets) → Modification ; tom et sam (stagiaires) → Lecture ; max (direction, autorisé par Samba mais « autres » ---) et zoe (refusée par Samba) → Aucun accès (0,5 pt par élément)."),
        ),
        correction=(
            "lea est dans le groupe propriétaire projets (rws) : Modification. ines est dans projets et stagiaires : la classe groupe cumule rwx et r-x, donc Modification. tom et sam ne sont, parmi les groupes qui comptent, que dans stagiaires : l'ACL donne r-x, donc Lecture, même si Samba autorise l'écriture.",
            "max est accepté par Samba (@direction) mais n'est ni propriétaire, ni dans projets, ni dans l'ACL : il tombe dans « autres » (---), Aucun accès. zoe n'est pas dans valid users : Samba la refuse avant même les droits Unix.",
        ),
        classification=Classification(categories=ACCESS_LEVELS, elements=tuple(f"{u.login} (groupes : {', '.join(u.groups)})" for u in E07_USERS),
                                      correct=E07_CORRECT),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : lire un chemin UNC",
        question_type="document_analysis",
        requirement_ids=R_SHARE,
        kind=KIND_SCHEMA,
        context=(
            f"Tu rédiges la fiche « Accéder au dossier de la comptabilité » pour les nouveaux employés d'une "
            f"fiduciaire. Le serveur {SERVER_NAME} a l'adresse {SERVER_IP} ; il partage le dossier Compta ; le "
            "fichier des factures 2026 est dans le sous-dossier 2026. Le document 1 est le schéma à terminer."
        ),
        documents=(_schema("pr23-unc-a-completer", "Document 1 — Chemin UNC à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique ce que prouve un accès qui fonctionne par ③ mais pas par le nom du serveur.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in UNC_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Explication", 1, "Le serveur, le partage et les droits fonctionnent ; seule la résolution du nom (DNS) est en panne."),
        ),
        correction=(
            f"① {SERVER_NAME} est le serveur, ② Compta est le nom du partage, puis vient le chemin dans le partage (2026\\factures.xlsx). ③ La même ressource s'écrit {UNC_BLANK_ANSWERS['③']} par l'adresse IP. ④ La lettre de lecteur {UNC_BLANK_ANSWERS['④']} associée à \\\\{SERVER_NAME}\\Compta (net use Z: \\\\{SERVER_NAME}\\Compta /persistent:yes).",
            "Si le chemin par l'adresse IP fonctionne et pas celui par le nom, le serveur répond, le partage existe et le compte a ses droits : seule la traduction du nom en adresse échoue. On vérifie le DNS du poste (nslookup, PR22 : DNS = contrôleur de domaine).",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : les deux barrières",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_SCHEMA,
        context=(
            f"La directrice Claire Dupont (groupe G_Direction) ouvre le dossier Compta du serveur {SERVER_NAME}, "
            "par le réseau depuis son bureau ou parfois en session ouverte sur le serveur lui-même. Le document 1 "
            "montre les autorisations du partage et du dossier ; il manque les droits obtenus."
        ),
        documents=(_schema("pr23-barrieres-a-completer", "Document 1 — Deux barrières à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Indique quelle barrière limite Claire par le réseau et justifie.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in E09_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, f"Partage {E09_ANSWERS['①']} (Utilisateurs authentifiés), NTFS {E09_ANSWERS['②']} (G_Direction) : par le réseau la plus restrictive, donc {LIMIT_NTFS} limite ; en local, NTFS seul."),
        ),
        correction=(
            f"① Dans le partage, Claire fait partie des utilisateurs authentifiés : {E09_ANSWERS['①']}. ② Dans NTFS, G_Direction a Lecture et exécution sur Compta : {E09_ANSWERS['②']}. ③ Par le réseau, on garde le plus faible des deux : {E09_ANSWERS['③']}.",
            f"④ En session ouverte sur le serveur, le partage n'intervient pas, seul NTFS compte : {E09_ANSWERS['④']}. C'est donc NTFS qui limite Claire ; c'est voulu : la direction consulte la comptabilité sans la modifier.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : deux imprimantes partagées",
        question_type="document_analysis",
        requirement_ids=R_PRINT,
        kind=KIND_SCHEMA,
        context=(
            f"Dans une agence, l'imprimante {USB_PRINTER} est branchée en USB sur le poste {PRINT_HOST}, qui la "
            f"partage ; l'imprimante réseau {NET_PRINTER} est gérée par le serveur d'impression {SERVER_NAME}. Le "
            "document 1 est le schéma remis au gérant, à terminer."
        ),
        documents=(_schema("pr23-imprimantes-a-completer", "Document 1 — Imprimantes partagées à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Donne un avantage et un inconvénient de chaque façon de partager.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in PRINTER_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Comparaison", 1, "USB partagée : aucun matériel en plus, mais dépend du poste hôte allumé ; imprimante réseau sur serveur : une file, un pilote et des droits gérés en un seul endroit, mais demande un serveur et une adresse fixe."),
        ),
        correction=(
            f"① {PRINTER_BLANK_ANSWERS['①']}. ② {PRINTER_BLANK_ANSWERS['②']} : une imprimante réseau doit garder la même adresse, sinon le port d'impression pointe dans le vide. ③ {PRINTER_BLANK_ANSWERS['③']} et ④ {PRINTER_BLANK_ANSWERS['④']} : même forme qu'un dossier partagé, \\\\hôte\\nom du partage.",
            "L'imprimante USB partagée ne coûte rien de plus, mais le poste hôte doit rester allumé et sa session ne doit pas être ralentie par les impressions des autres. Le serveur d'impression centralise la file, le pilote et les droits (par groupes), au prix d'un serveur allumé et d'une imprimante à adresse fixe.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : droits Unix et Samba",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_SCHEMA,
        context=(
            "Un petit serveur Linux NAS-LIN partage le dossier /srv/partages/compta avec Samba pour la comptabilité "
            "(marie) ; la direction (paul) doit pouvoir lire ; le secrétariat (sam) n'a rien à y faire. Le document 1 "
            "décompose la ligne ls -ld du dossier ; il manque deux explications et deux accès."
        ),
        documents=(_schema("pr23-unix-a-completer", "Document 1 — Droits Unix à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique pourquoi paul ne peut pas écrire alors que le groupe compta a rwx.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in UNIX_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, "paul n'est pas dans le groupe compta : il ne reçoit que l'entrée d'ACL group:direction:r-x ; et Samba ne met que @compta dans write list."),
        ),
        correction=(
            f"① {UNIX_BLANK_ANSWERS['①']}. ② {UNIX_BLANK_ANSWERS['②']}. ③ paul (direction) : {UNIX_BLANK_ANSWERS['③']}. ④ sam : {UNIX_BLANK_ANSWERS['④']} (refusé par valid users et « autres » = ---).",
            "Les droits rwx du groupe ne valent que pour les membres du groupe compta. paul est dans direction : il reçoit l'entrée d'ACL r-x (lire et entrer), pas l'écriture ; en plus, smb.conf ne donne l'écriture (write list) qu'à @compta. Le résultat, Lecture, est celui qui était demandé.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Remplir la matrice des droits effectifs d'un serveur",
        question_type="document_analysis",
        requirement_ids=("AP-26", "AP-27"),
        kind=KIND_MATRIX,
        context=(
            f"À ton arrivée dans une fiduciaire, ton responsable te demande la matrice des droits du serveur "
            f"{SERVER_NAME} pour l'audit : ce que chaque employé obtient vraiment par le réseau. Les documents 1 à 3 "
            "donnent les partages, les autorisations NTFS (Administrateurs a Contrôle total partout) et les comptes."
        ),
        documents=(
            _table("Document 1 — Autorisations des partages", ("Partage", "Dossier", "Autorisations du partage"),
                   *((s.name, short_path(s.path), _rule(s.entries)) for s in SHARES.values())),
            _table("Document 2 — Autorisations NTFS posées sur chaque dossier", ("Dossier", "Héritage du parent", "Entrées posées ici"),
                   *((short_path(p), "oui" if NTFS_TREE[p].inherit else "désactivé",
                      _rule(tuple(e for e in NTFS_TREE[p].entries if e.principal != LOCAL_ADMINS)) if NTFS_TREE[p].entries
                      else "aucune (tout est hérité)") for p in MATRIX_PATHS)),
            _table("Document 3 — Comptes", ("Compte", "Personne", "Groupes"),
                   *((a.login, a.person, ", ".join(a.groups)) for a in (JULIE, CLAIRE, SAM))),
        ),
        instructions=(
            "Remplis la matrice : pour chaque compte et chaque dossier, Aucun accès, Lecture ou Modification par le réseau.",
            "Explique deux cases : Archives pour jmartin et Paie pour jmartin.",
        ),
        criteria=(
            _c("Matrice", 3, " ; ".join(f"{login} : " + ", ".join(f"{f} {v}" for f, v in row.items()) for login, row in E12_MATRIX.items())
               + " (1 pt par compte, 0,5 pt retiré par case fausse)."),
            _c("Explications", 1, "Archives : partage Lecture, NTFS Modification → Lecture (le partage limite) ; Paie : héritage désactivé, G_Compta absent → Aucun accès."),
        ),
        correction=(
            "Méthode : pour chaque case, droit du compte dans le partage (le plus fort de ses groupes), droit NTFS du dossier (entrées posées ici + héritées si l'héritage est actif), puis le plus faible des deux. Factures n'a aucune entrée propre : il hérite de Compta. Direction n'est partagé que pour G_Direction.",
            "Résultat : " + " ; ".join(f"{login} — " + ", ".join(f"{f} {v}" for f, v in row.items()) for login, row in E12_MATRIX.items())
            + f". Archives pour jmartin : partage Lecture (Utilisateurs authentifiés), NTFS Modification (G_Compta) → {E12_MATRIX['jmartin']['Archives']}. Paie pour jmartin : héritage désactivé, seuls Administrateurs et G_Direction y sont → {E12_MATRIX['jmartin']['Compta\\Paie']}.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Les comptables voient le dossier Paie",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_DIAG,
        context=(
            f"La directrice a créé hier le sous-dossier Paie dans Compta, sur {SERVER_NAME}, pour les fiches de salaire. "
            "Ce matin, la comptable Julie Martin (G_Compta) les ouvre sans problème. La directrice veut que seuls la "
            "direction et les administrateurs y entrent. Le document 1 est ton relevé."
        ),
        documents=(_console("Document 1 — icacls du dossier Paie (capture fictive)", *icacls_lines(PAIE, E13_TREE_BEFORE)),),
        instructions=(
            "Explique pourquoi Julie a accès, en t'appuyant sur le relevé.",
            "Donne la correction (fenêtre ou commande) et le test.",
        ),
        criteria=(
            _c("Cause", 1, f"Toutes les entrées portent (I) : Paie hérite de Compta, où G_Compta a Modification → accès de Julie : {E13_BEFORE}."),
            _c("Correction et test", 1.5, f"Désactiver l'héritage de Paie en copiant les entrées (Sécurité → Avancé, ou icacls … /inheritance:d), retirer G_Compta, donner Modification à G_Direction, garder Administrateurs ; test : Julie → {E13_AFTER}, Claire → {E13_CLAIRE_AFTER}."),
        ),
        correction=(
            f"Le relevé ne montre que des entrées héritées, marquées (I) : un nouveau dossier reçoit les autorisations de son parent. Dans Compta, G_Compta a Modification (M) : Julie a donc {E13_BEFORE.lower()} sur Paie.",
            f"Sur Paie : Sécurité → Avancé → « Désactiver l'héritage » → « Convertir les autorisations héritées en autorisations explicites » (ou icacls {PAIE} /inheritance:d), puis on retire G_Compta et on donne Modification à G_Direction (icacls {PAIE} /remove \"DUPONT\\G_Compta\" puis /grant \"DUPONT\\G_Direction:(OI)(CI)M\"). Test : Julie → {E13_AFTER.lower()}, Claire → {E13_CLAIRE_AFTER.lower()}. On vérifie aussi le contenu déjà copié.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Un refus qui bloque le stagiaire partout",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            "Pour que le stagiaire Théo ne touche pas aux factures, un collègue l'a laissé dans G_Compta et a ajouté "
            "sur le dossier Compta un refus pour le groupe G_Stagiaires, dont Théo est membre. Théo ne peut plus rien "
            "ouvrir dans Compta, même pour lire les modèles de documents. Le document 1 est l'onglet Sécurité."
        ),
        documents=(_table("Document 1 — Onglet Sécurité de Compta (extrait fictif)", ("Groupe", "Autoriser", "Refuser"),
                          ("G_Compta", "Modification", "—"),
                          ("G_Direction", "Lecture et exécution", "—"),
                          ("G_Stagiaires", "—", "Contrôle total"),
                          (LOCAL_ADMINS, "Contrôle total (hérité)", "—")),),
        instructions=(
            "Calcule l'accès NTFS de Théo sur Compta et sur Factures, et explique la règle.",
            "Propose une organisation plus propre, selon le moindre privilège.",
        ),
        criteria=(
            _c("Calcul et règle", 1.5, f"Théo : Compta {E14_RESULT}, Factures {E14_FACTURES} (le refus est hérité, et Factures n'a aucune autorisation explicite) ; un refus explicite l'emporte sur les autorisations de ses autres groupes ; Julie reste en {E14_JULIE}."),
            _c("Organisation", 1.5, "Retirer le refus ; sortir Théo de G_Compta ; créer un groupe de lecture (ex. G_Compta_Lecture) avec Lecture et exécution sur Compta, ou un dossier Modèles ; éviter les refus, sources d'erreurs."),
        ),
        correction=(
            f"Théo est dans G_Compta (Modification) et G_Stagiaires (Refuser Contrôle total). Un refus posé sur le dossier l'emporte sur les autorisations : accès {E14_RESULT.lower()} sur Compta, et {E14_FACTURES.lower()} sur Factures, qui hérite du refus sans autorisation explicite pour le contrer. Les autres comptables ne sont pas touchés (Julie : {E14_JULIE.lower()}).",
            "Plus propre : on retire le refus, on sort Théo de G_Compta et on crée un groupe G_Compta_Lecture (Lecture et exécution sur Compta), ou un dossier Modèles accessible en lecture. On n'accorde que ce qui est nécessaire, au lieu d'accorder trop puis de refuser : les refus se propagent et finissent par bloquer des personnes par erreur.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Modification sur le serveur, lecture par le réseau",
        question_type="document_analysis",
        requirement_ids=("AP-26", "AP-27"),
        kind=KIND_DIAG,
        context=(
            f"Julie Martin (G_Compta) doit classer des fichiers dans Archives. Quand l'administrateur lui ouvre une "
            f"session directement sur {SERVER_NAME}, elle y arrive ; depuis son poste, par \\\\{SERVER_NAME}\\Archives, "
            "Windows refuse l'enregistrement. Les documents 1 et 2 sont relevés sur le serveur."
        ),
        documents=(
            _console("Document 1 — net share Archives (capture fictive)", *net_share_lines(SHARES["Archives"])),
            _console("Document 2 — icacls Archives (capture fictive)", *icacls_lines(ARCHIVES)),
        ),
        instructions=(
            "Explique la différence entre les deux accès en t'appuyant sur les relevés.",
            "Propose la correction et le test, sans ouvrir Archives en écriture à tout le monde.",
        ),
        criteria=(
            _c("Explication", 1.5, f"Par le réseau : partage READ (Lecture) + NTFS M (G_Compta) → {E15_REMOTE} ({E15_LIMIT} limite) ; en local, NTFS seul → {E15_LOCAL}."),
            _c("Correction", 1, "Partage Archives : Utilisateurs authentifiés en Modifier (NTFS garde la Lecture des autres et la Modification de G_Compta) ; test d'écriture par Julie et refus pour un compte hors G_Compta."),
        ),
        correction=(
            f"Le partage Archives n'accorde que READ (Lecture) aux utilisateurs authentifiés. NTFS donne Modification (M) à G_Compta et Lecture et exécution (RX) aux utilisateurs du domaine. Par le réseau, Windows applique le plus restrictif : {E15_REMOTE.lower()}, c'est {E15_LIMIT} qui limite. En session sur le serveur, le partage n'intervient pas : NTFS seul, {E15_LOCAL.lower()}.",
            f"On passe le partage en Modifier (net share ou Partage avancé → Autorisations ; New-SmbShare/Grant-SmbShareAccess -AccessRight Change) : les autres restent en lecture grâce à NTFS. Test : Julie enregistre un fichier dans \\\\{SERVER_NAME}\\Archives ; Sam (secrétariat) peut lire mais pas enregistrer.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Le ping répond, mais « Accès refusé »",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_DIAG,
        context=(
            f"Sam Roux (secrétariat, G_Secretariat) doit désormais lire les factures du dossier Compta pour les envoyer "
            f"aux clients. Depuis son poste, il connecte le lecteur Z: à \\\\{SERVER_NAME}\\Compta, puis l'ouvre. Les autres "
            "dossiers fonctionnent. Les documents 1 à 3 sont tes relevés."
        ),
        documents=(
            _console("Document 1 — ping du serveur (capture fictive)", *ping_lines(SERVER_IP, ip=SERVER_IP)),
            _console("Document 2 — ouverture du partage sur le poste de Sam (capture fictive)",
                     *net_use_lines(unc(SERVER_NAME, "Compta")), *dir_lines("Z:\\", denied=True)),
            _console("Document 3 — icacls Compta sur le serveur (capture fictive)", *icacls_lines(COMPTA)),
        ),
        instructions=(
            "Indique la piste et la barrière en cause, preuves à l'appui.",
            "Donne la correction minimale et le test, en protégeant Paie.",
        ),
        criteria=(
            _c("Diagnostic", 1.5, f"Réseau bon (ping), connexion au partage acceptée puis « Accès refusé » à l'ouverture = le serveur répond, le compte est reconnu et refuse ; partage {E16_SHARE} pour les utilisateurs authentifiés ; NTFS : G_Secretariat absent → {E16_NTFS} ; piste permissions, barrière NTFS."),
            _c("Correction et test", 1.5, f"Ajouter G_Secretariat en Lecture et exécution sur Compta (onglet Sécurité ou icacls /grant) ; Sam → {E16_AFTER} ; Paie (héritage désactivé) reste {E16_AFTER_PAIE} ; Sam rouvre sa session si on vient de l'ajouter au groupe."),
        ),
        correction=(
            f"Le ping répond : le réseau et le serveur vont bien. La connexion du lecteur réussit (le partage accepte Sam), mais l'ouverture répond « Accès refusé » : le serveur a été joint, le compte reconnu, on est au niveau des permissions ({E16_DIAG.split(' :')[0].lower()}). Le partage Compta donne Modifier à tous les utilisateurs authentifiés ({E16_SHARE.lower()}), mais icacls ne montre aucune entrée pour G_Secretariat : NTFS donne {E16_NTFS.lower()}.",
            f"On ajoute G_Secretariat en Lecture et exécution sur Compta : icacls {COMPTA} /grant \"DUPONT\\G_Secretariat:(OI)(CI)RX\". Sam obtient {E16_AFTER.lower()} (lecture seule, comme demandé), Factures en hérite, et Paie, dont l'héritage est désactivé, reste en {E16_AFTER_PAIE.lower()}. Test : Sam ouvre Z:, lit une facture, l'enregistrement d'un fichier est refusé.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Le nom du serveur est introuvable",
        question_type="document_analysis",
        requirement_ids=R_SHARE,
        kind=KIND_DIAG,
        context=(
            f"Sur un poste réinstallé hier, le lecteur réseau \\\\{SERVER_NAME}\\Commun ne se connecte plus ; l'Explorateur "
            "affiche « Windows ne peut pas accéder à … » et le code 0x80070035. Les autres postes fonctionnent. Le "
            "technicien qui a réinstallé a réglé le réseau à la main. Les documents 1 à 3 sont tes relevés."
        ),
        documents=(
            _console("Document 1 — ping par le nom (capture fictive)", *ping_lines(SERVER_NAME, ip=None)),
            _console("Document 2 — ping par l'adresse (capture fictive)", *ping_lines(SERVER_IP, ip=SERVER_IP)),
            _console("Document 3 — net use par l'adresse (capture fictive)", *net_use_lines(unc(SERVER_IP, "Commun"))),
        ),
        instructions=(
            "Indique la piste en t'appuyant sur les trois relevés.",
            "Donne ce que tu vérifies et corriges, puis le test.",
        ),
        criteria=(
            _c("Diagnostic", 1.5, "Par l'adresse IP tout fonctionne (ping, partage, compte, droits) ; seul le nom échoue : résolution du nom (DNS)."),
            _c("Correction et test", 1.5, "ipconfig /all : DNS du poste (en domaine : le contrôleur, pas la box ni un DNS public) ; corriger, ipconfig /flushdns ; nslookup SRV-FICH → 192.168.20.20 ; reconnecter \\\\SRV-FICH\\Commun."),
        ),
        correction=(
            f"Le ping par le nom échoue (« n'a pas pu trouver l'hôte ») alors que le ping et le partage par l'adresse {SERVER_IP} fonctionnent : le serveur, le partage, le compte et les droits sont bons. La piste est la {E17_DIAG.split(' :')[0].lower()} : le poste ne sait pas traduire {SERVER_NAME} en adresse.",
            f"On lit ipconfig /all : après la réinstallation, le DNS a probablement été réglé sur la box ou un DNS public, qui ne connaissent pas les noms internes. On remet le DNS de l'entreprise (en domaine, le contrôleur, voir PR22), ipconfig /flushdns, puis nslookup {SERVER_NAME} doit renvoyer {SERVER_IP} ; on reconnecte le lecteur par le nom. On n'utilise pas l'adresse IP comme solution définitive : elle masquerait la panne.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="L'imprimante réseau est « hors connexion »",
        question_type="document_analysis",
        requirement_ids=R_PRINT,
        kind=KIND_PRINT,
        context=(
            f"Depuis la coupure de courant de ce week-end, tous les postes affichent {NET_PRINTER} « hors connexion ». "
            "L'imprimante est allumée et imprime sa page de configuration sans problème. Le DHCP est assuré par la box. "
            "Les documents 1 à 3 sont tes relevés."
        ),
        documents=(
            _console("Document 1 — état de l'imprimante sur le serveur (capture fictive)", *get_printer_lines("Offline")),
            _console("Document 2 — ping de l'adresse du port (capture fictive)", *ping_lines(NET_PRINTER_IP, ip=NET_PRINTER_IP, replies=False)),
            _table("Document 3 — Page de configuration imprimée (extrait)", ("Paramètre", "Valeur"),
                   ("Nom d'hôte", NET_PRINTER), ("Configuration IPv4", "DHCP"), ("Adresse IPv4", E18_NEW_IP),
                   ("Passerelle", "192.168.20.254")),
        ),
        instructions=(
            "Explique la cause en t'appuyant sur les trois documents.",
            "Donne la correction durable et le test.",
        ),
        criteria=(
            _c("Cause", 1.5, f"Le port pointe vers {NET_PRINTER_IP}, qui ne répond plus ; l'imprimante, en DHCP, a reçu {E18_NEW_IP} après la coupure : piste imprimante (adresse changée)."),
            _c("Correction et test", 1.5, f"Réservation DHCP sur la box (ou adresse fixe hors plage DHCP) pour revenir à {NET_PRINTER_IP} ; à défaut, mettre à jour le port ; page de test depuis deux postes."),
        ),
        correction=(
            f"Le serveur envoie les impressions au port IP_{NET_PRINTER_IP}, mais cette adresse ne répond plus (délai d'attente dépassé). La page de configuration montre que l'imprimante est en DHCP et a reçu {E18_NEW_IP} au redémarrage. Piste : {E18_DIAG.split(' :')[0].lower()}, adresse changée ; le pilote et les droits ne sont pas en cause.",
            f"Correction durable : réservation DHCP dans la box (adresse MAC de l'imprimante → {NET_PRINTER_IP}) ou adresse fixe hors de la plage DHCP, puis redémarrage de l'imprimante. Si on garde la nouvelle adresse, on modifie le port sur le serveur (une seule fois, grâce au serveur d'impression). Test : Get-Printer indique Normal, page de test depuis deux postes.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Samba : la direction lit mais ne peut pas enregistrer",
        question_type="document_analysis",
        requirement_ids=("AP-25", "AP-27"),
        kind=KIND_DIAG,
        context=(
            "Sur le serveur Linux NAS-LIN, le partage Samba compta accueille la comptabilité. Paul (groupe direction) "
            "ouvre les fichiers mais ne peut rien enregistrer. La direction demande désormais qu'il puisse y écrire. "
            "Les documents 1 à 3 sont les réglages relevés."
        ),
        documents=(
            _console("Document 1 — extrait de /etc/samba/smb.conf", *SMB_CONF_LINES),
            _console("Document 2 — ls -ld (capture fictive)", *ls_lines()),
            _console("Document 3 — getfacl (capture fictive)", *getfacl_lines()),
        ),
        instructions=(
            "Explique l'accès actuel de Paul par les deux couches (Samba et Unix).",
            "Donne les deux modifications nécessaires, les commandes et le test.",
        ),
        criteria=(
            _c("Analyse", 1.5, f"Samba : paul dans valid users (@direction) mais pas dans write list → lecture ; Unix : pas dans compta, ACL group:direction:r-x → lecture ; résultat {E19_BEFORE}."),
            _c("Modifications et test", 1.5, f"write list = @compta @direction (testparm, systemctl reload smbd) ET setfacl -m g:direction:rwx compta (plus -d pour les nouveaux fichiers) ; une seule des deux ne suffit pas ({E19_ONLY_SAMBA} / {E19_ONLY_ACL}) ; ensemble → {E19_AFTER} ; test d'enregistrement par paul."),
        ),
        correction=(
            f"Côté Samba, paul est accepté (valid users contient @direction) mais read only = yes et write list ne contient que @compta : lecture. Côté Unix, paul n'est pas dans le groupe compta ; l'ACL lui donne r-x : lire et entrer. Accès réel, le plus restrictif des deux : {E19_BEFORE.lower()}.",
            f"Il faut les deux : write list = @compta @direction dans smb.conf (vérifié par testparm, puis sudo systemctl reload smbd) et setfacl -m g:direction:rwx compta, avec setfacl -d -m g:direction:rwx compta pour les fichiers créés ensuite. Seule la première laisserait {E19_ONLY_SAMBA.lower()}, seule la seconde {E19_ONLY_ACL.lower()} ; ensemble : {E19_AFTER.lower()}. Test : paul enregistre un fichier depuis \\\\NAS-LIN\\compta.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Rédiger le plan de partage d'un cabinet de 9 postes",
        question_type="long_answer",
        requirement_ids=("AP-25", "AP-26", "AP-27"),
        kind=KIND_MATRIX,
        context=(
            f"Un cabinet d'architectes de 9 postes en domaine installe un serveur {SERVER_NAME}. Besoins : un dossier "
            "Projets (les architectes modifient, la secrétaire lit), un dossier Administration (la gérante et la "
            "secrétaire modifient, personne d'autre), un dossier Commun (tout le monde), et l'imprimante grand format."
        ),
        documents=(_table("Document 1 — Personnel", ("Fonction", "Nombre"), ("Gérante (architecte)", "1"),
                          ("Architectes", "6"), ("Secrétaire", "1"), ("Technicien externe", "1")),),
        instructions=(
            "Propose les groupes, puis pour chaque dossier les autorisations du partage et NTFS.",
            "Donne le partage de l'imprimante et deux mesures de protection des données.",
        ),
        criteria=(
            _c("Groupes", 1, "G_Architectes (gérante + 6), G_Gestion (gérante + secrétaire), G_Secretariat ; comptes nominatifs ; technicien : compte d'administration séparé."),
            _c("Autorisations", 2, f"Partages : {AUTH_USERS} Modifier (ou groupes concernés) ; NTFS Projets : G_Architectes Modification, G_Secretariat Lecture et exécution ; Administration : G_Gestion Modification ; Commun : {USERS_DOMAIN} Modification ; Tout le monde retiré ; Administrateurs Contrôle total."),
            _c("Imprimante et protection", 1, f"\\\\{SERVER_NAME}\\nom, adresse fixe, Imprimer pour les groupes qui en ont besoin ; sauvegarde du serveur, moindre privilège, pas de partage d'un disque entier ni de Contrôle total aux utilisateurs."),
        ),
        correction=(
            f"Groupes : G_Architectes (la gérante et les 6 architectes), G_Gestion (la gérante et la secrétaire), G_Secretariat (la secrétaire). Partages Projets, Administration et Commun : {AUTH_USERS} en Modifier (le détail se fait dans NTFS). NTFS : Projets → G_Architectes Modification, G_Secretariat Lecture et exécution ; Administration → G_Gestion Modification (rien pour les architectes) ; Commun → {USERS_DOMAIN} Modification ; partout Administrateurs Contrôle total et Tout le monde retiré.",
            f"Imprimante : installée sur {SERVER_NAME}, adresse fixe, partagée sous un nom court (\\\\{SERVER_NAME}\\GrandFormat), droit Imprimer pour G_Architectes. Protection des données : sauvegarde quotidienne du serveur testée, moindre privilège (personne d'autre que les administrateurs en Contrôle total, technicien avec un compte séparé), pas de partage du disque entier ; matrice des droits remise à la gérante.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (10 questions × 2 points, réponses libres, « Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Une commerciale ne peut pas enregistrer ses devis",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            f"Nora Lambert (G_Commerciaux) enregistre ses devis sans problème quand elle travaille sur le serveur "
            f"{SERVER_NAME} lui-même. Depuis son portable, par \\\\{SERVER_NAME}\\Devis, l'enregistrement est refusé ; "
            "l'ouverture fonctionne. Le document 1 donne les autorisations."
        ),
        documents=(_table("Document 1 — Autorisations du dossier Devis", ("Couche", "Autorisations"),
                          ("Partage Devis", f"{AUTH_USERS} : Lecture"),
                          ("NTFS D:\\Partages\\Devis", "G_Commerciaux : Modification ; Administrateurs : Contrôle total")),),
        instructions=("Donne l'accès effectif de Nora dans chaque situation, la barrière qui limite, et la correction.",),
        criteria=(
            _c("Accès et barrière", 1, f"Réseau : {X01_REMOTE} (le plus restrictif ; {X01_LIMIT} limite) ; sur le serveur : {X01_LOCAL} (NTFS seul)."),
            _c("Correction", 1, "Partage Devis en Modifier (pour les utilisateurs authentifiés ou G_Commerciaux) ; NTFS inchangé ; test d'enregistrement par le réseau."),
        ),
        correction=(
            f"Par le réseau, Windows retient le plus restrictif du partage (Lecture) et de NTFS (Modification) : {X01_REMOTE.lower()}, c'est {X01_LIMIT} qui limite. Sur le serveur, le partage n'intervient pas : {X01_LOCAL.lower()}.",
            "On passe l'autorisation du partage en Modifier ; NTFS continue de réserver la modification à G_Commerciaux. Test : Nora enregistre un devis par \\\\SRV-FICH\\Devis.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Le serveur répond au ping mais pas le partage",
        question_type="document_analysis",
        requirement_ids=R_SHARE,
        kind=KIND_DIAG,
        context=(
            f"Après le remplacement de la carte réseau du serveur {SERVER_NAME}, plus aucun poste n'ouvre ses partages "
            "(code 0x80070035), alors que le ping répond. Le centre réseau du serveur indique « Réseau 2 — réseau "
            "public ». Le document 1 est relevé depuis un poste."
        ),
        documents=(_console("Document 1 — test du port 445 (capture fictive)", *port_test_lines(SERVER_NAME, SERVER_IP, open_=False)),),
        instructions=("Donne la piste, la cause probable et la correction, puis le test.",),
        criteria=(
            _c("Piste et cause", 1, f"Port {SMB_PORT} fermé alors que le serveur répond : partage de fichiers bloqué ; nouvelle carte classée en profil Public, où la règle « Partage de fichiers et d'imprimantes » n'est pas active."),
            _c("Correction et test", 1, f"Profil Privé (ou Domaine, si la détection du domaine fonctionne), règle de pare-feu active ; Test-NetConnection -Port {SMB_PORT} → True ; ouverture du partage."),
        ),
        correction=(
            f"Le ping prouve que le serveur répond, mais TcpTestSucceeded : False montre que le port {SMB_PORT} du partage de fichiers est fermé ({X02_DIAG.split(' :')[0].lower()}). La nouvelle carte a été classée en réseau public : le pare-feu y bloque le partage de fichiers.",
            f"On remet le réseau en profil Privé (ou on vérifie pourquoi il n'est pas reconnu comme réseau du domaine) et on vérifie que la règle « Partage de fichiers et d'imprimantes » est active. On ne désactive pas le pare-feu. Test : Test-NetConnection {SERVER_NAME} -Port {SMB_PORT} → True, puis ouverture du partage.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Le nom réseau est introuvable",
        question_type="short_answer",
        requirement_ids=R_SHARE,
        kind=KIND_DIAG,
        context=(
            f"Une nouvelle employée tape « net use Y: \\\\{SERVER_NAME}\\Comptabilite » comme noté sur un vieux "
            "post-it et obtient « Erreur système 67. Le nom réseau est introuvable. ». Les autres lecteurs de son "
            f"poste vers {SERVER_NAME} fonctionnent ; le dossier a été renommé l'an dernier."
        ),
        instructions=("Explique ce qu'indique ce message, comment tu le vérifies et la correction.",),
        criteria=(
            _c("Sens", 1, "Le serveur répond (les autres lecteurs fonctionnent) mais il n'a aucun partage de ce nom : nom de partage faux ou supprimé."),
            _c("Vérification et correction", 1, f"net view \\\\{SERVER_NAME} liste les partages ; utiliser le bon nom (ex. Compta) ; corriger la fiche ; pas de droits à modifier."),
        ),
        correction=(
            "L'erreur 67 arrive après que le serveur a répondu : c'est le nom du partage qui n'existe pas (ou plus). Les autres lecteurs prouvent que le réseau, le nom du serveur et le compte fonctionnent.",
            f"net view \\\\{SERVER_NAME} affiche les partages réellement disponibles ; on se connecte avec le bon nom (par exemple \\\\{SERVER_NAME}\\Compta) et on corrige la fiche d'accueil. Les permissions ne sont pas en cause.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="L'imprimante de l'accueil disparaît chaque soir",
        question_type="short_answer",
        requirement_ids=R_PRINT,
        kind=KIND_PRINT,
        context=(
            f"Dans un cabinet de 8 postes, l'imprimante laser est branchée en USB sur {PRINT_HOST} et partagée. Les "
            "comptables qui travaillent tard ne peuvent plus imprimer après 18 h, quand la secrétaire éteint son PC. "
            "L'imprimante possède une prise réseau inutilisée."
        ),
        instructions=("Explique la cause et propose une solution durable, avec ce qu'il faut régler.",),
        criteria=(
            _c("Cause", 1, f"Imprimante USB partagée : {PRINT_HOST} est l'hôte (file d'attente) ; éteint, l'imprimante n'est plus joignable."),
            _c("Solution", 1, "Brancher l'imprimante au réseau avec une adresse fixe ou réservée, l'ajouter par son adresse IP ou via un serveur d'impression, droits Imprimer, test depuis les postes."),
        ),
        correction=(
            f"L'imprimante est partagée par {PRINT_HOST} : c'est lui qui reçoit les impressions et gère la file d'attente. Quand il est éteint, plus personne ne peut imprimer.",
            "Solution : relier l'imprimante au réseau par sa prise, lui donner une adresse fixe (ou une réservation DHCP), puis l'ajouter sur les postes par son adresse IP ou, mieux, par un serveur d'impression ; on règle les droits Imprimer et on imprime une page de test depuis plusieurs postes.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Matrice des droits d'une association",
        question_type="long_answer",
        requirement_ids=("AP-26", "AP-27"),
        kind=KIND_MATRIX,
        context=(
            "Une association installe un petit serveur de fichiers. Dossiers : Trésorerie (la trésorière modifie, le "
            "président lit), Activités (les 4 animateurs et le président modifient), Public (tous les bénévoles lisent, "
            "les animateurs modifient). Il y a 12 bénévoles en tout."
        ),
        instructions=("Propose les groupes et la matrice des autorisations NTFS, en appliquant le moindre privilège.",),
        criteria=(
            _c("Groupes", 0.5, "Groupes par fonction : G_Tresorerie, G_Bureau ou G_President, G_Animateurs, G_Benevoles (tous) ; comptes nominatifs."),
            _c("Matrice", 1.5, "Trésorerie : trésorière Modification, président Lecture, rien pour les autres ; Activités : animateurs et président Modification ; Public : bénévoles Lecture, animateurs Modification ; Contrôle total aux seuls administrateurs ; Tout le monde retiré (0,5 pt par dossier)."),
        ),
        correction=(
            "Groupes : G_Tresorerie (la trésorière), G_President, G_Animateurs (4), G_Benevoles (les 12). Les droits sont donnés aux groupes, jamais aux personnes.",
            "Trésorerie : G_Tresorerie Modification, G_President Lecture et exécution, aucune entrée pour les autres. Activités : G_Animateurs et G_President Modification. Public : G_Benevoles Lecture et exécution, G_Animateurs Modification. Partout : Administrateurs Contrôle total, Tout le monde retiré ; partage en Modifier pour les utilisateurs authentifiés, le détail est dans NTFS.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Un dossier RH créé au mauvais endroit",
        question_type="short_answer",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            f"La gérante a créé un sous-dossier RH dans Commun, sur {SERVER_NAME}, pour les contrats de travail. Dans "
            f"Commun, {USERS_DOMAIN} a Modification. Elle demande que seuls elle (G_Direction) et les administrateurs "
            "accèdent à RH, sans déplacer le dossier."
        ),
        instructions=("Explique qui accède à RH aujourd'hui et pourquoi, puis la correction et le test.",),
        criteria=(
            _c("Situation", 1, f"Héritage : RH reçoit les autorisations de Commun ; tous les {USERS_DOMAIN} y ont Modification."),
            _c("Correction et test", 1, "Désactiver l'héritage de RH (en convertissant les entrées), retirer Utilisateurs du domaine, donner Modification à G_Direction, garder Administrateurs ; test avec un compte ordinaire (refus) et celui de la gérante."),
        ),
        correction=(
            f"Un nouveau dossier hérite des autorisations de son parent : dans Commun, {USERS_DOMAIN} a Modification, donc tous les employés peuvent lire et modifier les contrats.",
            "Sur RH : Sécurité → Avancé → Désactiver l'héritage (convertir), retirer Utilisateurs du domaine, donner Modification à G_Direction et garder Administrateurs en Contrôle total. Test : un compte ordinaire est refusé, la gérante ouvre et enregistre.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Linux : la comptable n'entre pas dans le dossier RH",
        question_type="document_analysis",
        requirement_ids=R_RIGHTS,
        kind=KIND_MATRIX,
        context=(
            "Sur un serveur Linux, la comptable lina (groupe compta) doit consulter les fiches du dossier "
            "/srv/partages/rh, qui appartient au groupe rh. Elle reçoit « Permission non accordée ». Le document 1 "
            "est le relevé du dossier."
        ),
        documents=(_console("Document 1 — ls -ld (capture fictive)", *ls_lines(0o750, owner="root", group="rh", acl=False, name="rh")),),
        instructions=("Explique les droits de lina, puis donne une correction qui respecte le moindre privilège.",),
        criteria=(
            _c("Explication", 1, f"drwxr-x--- : propriétaire root rwx, groupe rh r-x, autres --- ; lina n'est ni root ni dans rh → classe « autres » : {X07_PERMS}."),
            _c("Correction", 1, f"Lecture seule : setfacl -m g:compta:r-x rh (ACL) ou ajouter lina au groupe rh (usermod -aG rh lina, reconnexion) → {X07_PERMS_FIX} ; pas de chmod 777 ni o+rx."),
        ),
        correction=(
            f"drwxr-x--- se lit : propriétaire root rwx, groupe rh r-x (lire, entrer), autres --- (rien). lina n'est pas root et n'est pas dans rh : elle reçoit les droits des autres, {X07_PERMS}, d'où le refus.",
            f"On donne seulement la lecture : setfacl -m g:compta:r-x /srv/partages/rh (toute la comptabilité) ou, si seule lina est concernée, usermod -aG rh lina puis reconnexion ({X07_PERMS_FIX}). On ne fait ni chmod 777 ni o+rx : tous les comptes du serveur liraient les fiches du personnel.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Deux comptes pour le même serveur",
        question_type="short_answer",
        requirement_ids=R_SHARE,
        kind=KIND_DIAG,
        context=(
            f"Un technicien a connecté le lecteur Z: à \\\\{SERVER_NAME}\\Commun avec son compte d'administration sur le "
            f"poste de Julie, pour une intervention. Julie veut ensuite connecter Y: à \\\\{SERVER_NAME}\\Compta avec "
            "son propre compte et obtient l'erreur système 1219."
        ),
        instructions=("Explique l'erreur et la marche à suivre, en tenant compte de la sécurité.",),
        criteria=(
            _c("Explication", 1, "Windows n'accepte qu'un seul compte par serveur pour une même session : une connexion existe déjà vers SRV-FICH avec le compte du technicien."),
            _c("Marche à suivre", 1, "net use pour lister, net use Z: /delete (et identifiants mémorisés supprimés : cmdkey /list, /delete) ; reconnecter avec le compte de Julie ; ne jamais laisser une connexion d'administration ouverte sur le poste d'un utilisateur."),
        ),
        correction=(
            f"L'erreur 1219 signifie qu'une connexion vers {SERVER_NAME} existe déjà avec un autre compte : Windows n'utilise qu'un compte par serveur dans une même session.",
            "On liste les connexions (net use), on supprime celle du technicien (net use Z: /delete) et ses identifiants mémorisés (cmdkey /list puis /delete), puis Julie se connecte avec son compte. La connexion d'administration laissée ouverte était aussi un risque : Julie aurait pu travailler avec les droits du technicien.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="La file d'attente est bloquée",
        question_type="short_answer",
        requirement_ids=R_PRINT,
        kind=KIND_PRINT,
        context=(
            f"Sur le serveur d'impression {SERVER_NAME}, la file de {NET_PRINTER} contient 14 documents ; le premier est "
            "« Erreur - Impression » et ne peut pas être supprimé. L'imprimante est prête et répond au ping ; aucun "
            "document ne sort."
        ),
        instructions=("Donne la procédure de déblocage dans l'ordre, et ce que tu dis aux utilisateurs.",),
        criteria=(
            _c("Procédure", 1.5, "Arrêter le service Spouleur d'impression (net stop spooler), vider C:\\Windows\\System32\\spool\\PRINTERS, redémarrer le spouleur (net start spooler), page de test."),
            _c("Utilisateurs", 0.5, "Les documents en attente sont perdus : prévenir et faire relancer les impressions utiles."),
        ),
        correction=(
            "Un document en erreur bloque toute la file. On arrête le spouleur (net stop spooler), on supprime les fichiers en attente dans C:\\Windows\\System32\\spool\\PRINTERS, puis on redémarre le spouleur (net start spooler) et on imprime une page de test.",
            "Les 14 documents de la file sont effacés : on prévient les utilisateurs pour qu'ils relancent ce dont ils ont besoin. Si le même document bloque à nouveau, on regarde le pilote ou le fichier.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Auditer le partage des dossiers clients",
        question_type="long_answer",
        requirement_ids=("AP-25", "AP-26", "AP-27"),
        kind=KIND_MATRIX,
        context=(
            "Dans une agence immobilière, le dossier Clients (copies de cartes d'identité, revenus) est partagé avec "
            "« Tout le monde : Contrôle total » sur le partage et dans NTFS. Le disque C: entier du poste de la gérante "
            "est aussi partagé « pour dépanner ». Aucune sauvegarde n'est faite."
        ),
        instructions=("Relève les risques et propose les corrections, en appliquant le moindre privilège.",),
        criteria=(
            _c("Risques", 1, "Tout le monde peut lire, modifier, supprimer et changer les droits de données personnelles ; disque C: entier exposé ; aucune sauvegarde (suppression ou rançongiciel = perte)."),
            _c("Corrections", 1, "Groupe des agents en Modification, gérante, administrateurs en Contrôle total ; Tout le monde retiré ; supprimer le partage de C: et partager un dossier dédié ; sauvegarde régulière testée ; matrice des droits écrite."),
        ),
        correction=(
            "Avec Tout le monde en Contrôle total des deux côtés, n'importe quel compte, y compris un logiciel malveillant lancé sur un poste, peut lire, modifier, supprimer ces données personnelles et même changer les autorisations. Le partage du disque C: expose tous les fichiers de la gérante et du système. Sans sauvegarde, une erreur ou un rançongiciel fait tout perdre.",
            "Corrections : un groupe G_Agents en Modification sur Clients, Administrateurs en Contrôle total, Tout le monde retiré ; partage en Modifier pour les utilisateurs authentifiés (le détail dans NTFS) ; suppression du partage de C: au profit d'un dossier dédié ; sauvegarde régulière et testée ; matrice des droits écrite et revue au départ de chaque employé.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigences du cours citées, schémas à compléter, matrices et diagnostics demandés par le
    ticket."""
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
    if len(PRACTICE_ITEMS) < 18:
        errors.append("Ticket #223 : au moins 18 exercices.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind in (KIND_MATRIX, KIND_DIAG, KIND_PRINT, KIND_SCHEMA)) < 18 - 3:
        errors.append("Ticket #223 : exercices de matrices de droits et de diagnostics insuffisants.")
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 4:
        errors.append("Ticket #223 : au moins 4 schémas à compléter.")
    if sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) < 5:
        errors.append("Ticket #223 : au moins 5 exercices avec des relevés de commandes.")
    expected = {"E16": S_RIGHTS, "E17": S_NAME, "E18": P_DEVICE, "X02": S_SMB}
    found = {"E16": E16_DIAG, "E17": E17_DIAG, "E18": E18_DIAG, "X02": X02_DIAG}
    if found != expected:
        errors.append("Diagnostics des relevés inattendus.")
    if {share_diagnosis(first_failure(k)) for _t, k in E05_CASES} != set(SHARE_DIAGNOSES) or S_NET not in SHARE_DIAGNOSES \
            or S_AUTH not in SHARE_DIAGNOSES or S_SHARE not in SHARE_DIAGNOSES:
        errors.append("E05 : toutes les pistes doivent être utilisées.")
    if {print_diagnosis(first_failure(k, PRINT_KEYS)) for _t, k in E06_CASES} != set(PRINT_DIAGNOSES):
        errors.append("E06 : toutes les pistes doivent être utilisées.")
    if set(E07_ANSWERS) != set(ACCESS_LEVELS) or set(E04_CATEGORIES) != {c for _t, c in E04_CASES}:
        errors.append("E04/E07 : catégories inutilisées.")
    if (E13_BEFORE, E13_AFTER) != (LEVEL_MODIFY, LEVEL_NONE) or (E15_REMOTE, E15_LOCAL, E15_LIMIT) != (
            LEVEL_READ, LEVEL_MODIFY, LIMIT_SHARE):
        errors.append("E13/E15 : droits inattendus.")
    if (E14_RESULT, E14_JULIE) != (LEVEL_NONE, LEVEL_MODIFY) or (E16_AFTER, E16_AFTER_PAIE) != (LEVEL_READ, LEVEL_NONE):
        errors.append("E14/E16 : droits inattendus.")
    if (E19_BEFORE, E19_ONLY_SAMBA, E19_ONLY_ACL, E19_AFTER) != (LEVEL_READ, LEVEL_READ, LEVEL_READ, LEVEL_MODIFY):
        errors.append("E19 : accès Samba inattendus.")
    if (X01_REMOTE, X01_LOCAL, X01_LIMIT) != (LEVEL_READ, LEVEL_MODIFY, LIMIT_SHARE) or X07_PERMS != "---":
        errors.append("X01/X07 : droits inattendus.")
    if samba_level(LX_SHARE, ("secretariat",)) != LEVEL_NONE or LEVEL_FULL not in E04_CATEGORIES:
        errors.append("Samba : refus attendu hors valid users.")
    return errors

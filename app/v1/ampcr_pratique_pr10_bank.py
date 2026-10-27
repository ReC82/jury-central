"""PR10 « Comptes, pilotes, paramètres et commandes » — exercices corrigés et mini-examen
(ticket #214).

Même organisation que PR09 (`app.v1.ampcr_pratique_pr09_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 17 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (compte, pilote, service), classements (commande
  Windows, commande Linux, droits nécessaires, compte selon le besoin, état d'un périphérique),
  extraits de console et captures fictives (net user, UAC, ID du matériel, permissions,
  systemctl, lsblk/df, ipconfig/nslookup, sfc/DISM), procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et relevés sont **fictifs** ; procédures, droits, permissions, états des
périphériques, services et commandes viennent de `app.v1.ampcr_pratique_pr10_figures` (mêmes
données que les schémas). Windows en français, Linux en anglais (voir ce module).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr10_figures import (
    ACCOUNT_CHOICES,
    ACCOUNT_STEPS,
    COMPTA_DIR_MODE,
    DEVICE_ACTIONS,
    DRIVER_STEPS,
    LS_COMPTA_SCREEN,
    NEED_ADMIN,
    NEED_CENTRAL,
    NEED_DAILY,
    NEED_SHARED,
    NET_USER_SCREEN,
    RIGHT_ADMIN,
    RIGHT_CATEGORIES,
    RIGHT_STANDARD,
    SERVICE_STEPS,
    SFC_DENIED_SCREEN,
    SFC_UNREPAIRED_SCREEN,
    SYSTEMCTL_CUPS_SCREEN,
    WINDOWS,
    account_for,
    can_access,
    device_action,
    elevation,
    mode_string,
    needs_admin,
    parse_hardware_id,
    service_fix,
    vendor_name,
)
from app.v1.ampcr_pratique_pr20_figures import Host, ipconfig_all_lines
from app.v1.ampcr_pratique_pr24_figures import (
    NS_OK,
    NS_TIMEOUT,
    nslookup_lines,
    tracert_lines,
    win_ping_lines,
)

PR10_CODE = "PR10"

KIND_ORDER = "ordonnancement"
KIND_ACCOUNT = "comptes et droits"
KIND_DRIVER = "pilotes et périphériques"
KIND_SERVICE = "paramètres et services"
KIND_COMMAND = "commandes et relevés"
KIND_ERROR = "repérage d'erreurs"

# Exigences officielles du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-05", "AP-11", "AP-12"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(ACCOUNT_STEPS)
E02_STEPS = _labels(DRIVER_STEPS)
E03_STEPS = _labels(SERVICE_STEPS)

E04_CATEGORIES = ("ipconfig", "ping", "tracert", "nslookup", "sfc", "DISM", "tasklist", "net user")
E04_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Lire l'adresse IPv4, la passerelle et le serveur DNS de la carte Wi-Fi", "ipconfig"),
    ("Vérifier que l'imprimante réseau 192.168.1.40 répond", "ping"),
    ("Savoir après quel routeur les paquets vers un site s'arrêtent", "tracert"),
    ("Vérifier que le serveur DNS traduit www.exemple.be en adresse", "nslookup"),
    ("Contrôler et réparer les fichiers système protégés de Windows", "sfc"),
    ("Réparer le magasin de composants que SFC utilise comme référence", "DISM"),
    ("Savoir si le processus spoolsv.exe tourne et quel est son PID", "tasklist"),
    ("Voir si le compte de Marie est actif et dans quels groupes locaux il est", "net user"),
)

E05_CATEGORIES = ("ip", "systemctl", "journalctl", "lsblk", "df", "chmod", "chown", "apt")
E05_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Afficher l'adresse de enp3s0 et la route par défaut", "ip"),
    ("Redémarrer le service cups et l'activer au démarrage", "systemctl"),
    ("Lire les messages du service ssh depuis le dernier démarrage", "journalctl"),
    ("Trouver la clé USB, ses partitions et leur UUID", "lsblk"),
    ("Savoir combien d'espace reste sur / et /home", "df"),
    ("Rendre un script exécutable par son propriétaire", "chmod"),
    ("Rendre à anne la propriété d'un fichier copié par root", "chown"),
    ("Installer le logiciel vlc depuis les dépôts d'Ubuntu", "apt"),
)

E06_COMMANDS: tuple[str, ...] = (
    "ipconfig /all",
    "ipconfig /release",
    "ping 192.168.1.1",
    "sfc /scannow",
    "net user",
    "net user julie * /add",
    "systemctl status cups",
    "sudo systemctl restart cups",
    "df -h",
    "sudo apt install vlc",
)
E06_CORRECT = tuple(RIGHT_CATEGORIES.index(RIGHT_ADMIN if needs_admin(c) else RIGHT_STANDARD) for c in E06_COMMANDS)

E07_NEEDS: tuple[tuple[str, str], ...] = (
    ("La secrétaire qui rédige des courriers et lit ses courriels", NEED_DAILY),
    ("L'élève qui utilise un PC de la salle informatique d'une petite asbl", NEED_DAILY),
    ("Le gérant qui installe les logiciels et les mises à jour du cabinet", NEED_ADMIN),
    ("Le technicien de l'atelier qui intervient sur le poste du client", NEED_ADMIN),
    ("Les 40 employés d'une entreprise équipée d'un contrôleur de domaine", NEED_CENTRAL),
    ("Trois stagiaires qui demandent un seul compte « stagiaire » commun", NEED_SHARED),
)
E07_CORRECT = tuple(ACCOUNT_CHOICES.index(account_for(n)) for _e, n in E07_NEEDS)

E08_CASES: tuple[tuple[str, int, bool], ...] = (
    ("« Contrôleur de réseau » sous Autres périphériques, Code 28", 28, False),
    ("Webcam avec une flèche vers le bas, Code 22", 22, False),
    ("Carte graphique en Code 10 juste après la mise à jour de son pilote", 10, True),
    ("Lecteur de cartes en Code 10 sur un Windows réinstallé, pilote générique", 10, False),
    ("Clé USB en Code 43, « périphérique USB non reconnu »", 43, False),
    ("Scanner « Périphérique inconnu » après son branchement, Code 28", 28, False),
)
E08_CORRECT = tuple(DEVICE_ACTIONS.index(device_action(code, after_driver_update=u)) for _e, code, u in E08_CASES)

E09_ADMIN_GROUPS = [line.strip(" *") for line in NET_USER_SCREEN if "*" in line]

E10_STANDARD = elevation(WINDOWS, is_admin=False, needs_admin=True)
E10_ADMIN = elevation(WINDOWS, is_admin=True, needs_admin=True)

E11_ID = "PCI\\VEN_8086&DEV_2725&SUBSYS_00248086"
E11_HW = parse_hardware_id(E11_ID)
E11_VENDOR = vendor_name(E11_ID)

E12_JULIE = ("julie", ("julie", "compta"))
E12_CAN_WRITE = can_access(*E12_JULIE, "root", "compta", COMPTA_DIR_MODE, "w")
E12_CAN_READ = can_access(*E12_JULIE, "root", "compta", COMPTA_DIR_MODE, "r")
E12_FIX_MODE = mode_string("770")

E13_FIX = service_fix(enabled=False, running=False)

E15_HOST = Host("COMPTA-02", "poste de la comptable", "192.168.10.24", 24, "192.168.10.1", ("192.168.10.254",),
                "A4-BB-6D-12-9C-01")
E15_IPCONFIG = ("C:\\> ipconfig /all", *ipconfig_all_lines(E15_HOST))
E15_PING_IP = win_ping_lines("203.0.113.10", (15, 14, 14, 16), ttl=56)
E15_NSLOOKUP = nslookup_lines("www.exemple.be", "192.168.10.254", NS_TIMEOUT)

X04_ID = "USB\\VID_04F9&PID_0062&REV_0100"
X04_VENDOR = vendor_name(X04_ID)

X07_SCRIPT_MODE = "-rw-r--r--"
X07_CAN_EXEC = can_access("paul", ("paul",), "paul", "paul", X07_SCRIPT_MODE, "x")

X09_TRACERT = tracert_lines("203.0.113.10", ("192.168.1.1", None, None, None))
X09_NSLOOKUP = nslookup_lines("www.exemple.be", "192.168.1.1", NS_OK, "203.0.113.10")
X09_PING_GW = win_ping_lines("192.168.1.1", (1, 1, 1, 1))

# =============================================================================================
# 17 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la création d'un compte utilisateur",
        question_type="ordering",
        requirement_ids=("AP-11",),
        kind=KIND_ORDER,
        context=(
            "Un cabinet de kinésithérapie accueille une nouvelle assistante qui travaillera sur "
            "le PC de l'accueil (Windows 11 Pro). Le gérant, seul administrateur du poste, te "
            "demande de lui créer un compte. Ton stagiaire a noté les six étapes de la "
            "procédure de l'atelier, mais dans le désordre."
        ),
        instructions=("Remets les six étapes de la création du compte dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Besoin → type de compte → création → mot de passe → groupes → contrôle (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Recueillir le besoin : qui utilise le poste et pour quoi faire, qui l'administre. 2. Choisir le type de compte : standard par défaut, administrateur seulement pour la personne qui administre. 3. Créer le compte (Paramètres → Comptes, ou net user nom * /add dans une invite administrateur).",
            "4. Mot de passe personnel saisi par l'utilisatrice, changement demandé à la première connexion : le technicien ne le connaît pas. 5. Groupes : Utilisateurs pour l'assistante ; Administrateurs uniquement pour le gérant. 6. Contrôler avec net user nom et par une connexion d'essai.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'intervention sur un pilote",
        question_type="ordering",
        requirement_ids=("AP-05",),
        kind=KIND_ORDER,
        context=(
            "Sur le portable d'un comptable (Windows 11, 64 bits), le lecteur d'empreintes ne "
            "fonctionne plus et apparaît avec un point d'exclamation dans le Gestionnaire de "
            "périphériques. La fiche de procédure « pilote » de l'atelier s'est mélangée à "
            "l'impression : il faut remettre ses six étapes dans l'ordre."
        ),
        instructions=("Remets les six étapes de l'intervention dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Identifier → noter l'état → choisir la source → point de restauration → installer ou restaurer → contrôler (0,5 pt par étape)."),
        ),
        correction=(
            "1. Identifier le périphérique : Propriétés → Détails → ID du matériel (fabricant et modèle). 2. Noter l'état et le code d'erreur (28, 22, 10, 43) et ce qui a changé récemment. 3. Choisir la source du pilote : Windows Update ou site du fabricant, pour ce modèle, ce Windows et le 64 bits.",
            "4. Créer un point de restauration avant de modifier un pilote. 5. Installer, mettre à jour ou, si le problème suit une mise à jour, « Restaurer le pilote ». 6. Contrôler : « Ce périphérique fonctionne correctement » et essai réel du lecteur.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (2, 5, 0, 4, 1, 3)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la remise en route d'un service",
        question_type="ordering",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_ORDER,
        context=(
            "Dans une petite école, plus aucun PC de la salle des professeurs n'imprime depuis "
            "lundi. Le directeur te demande d'intervenir et de laisser une procédure aux "
            "enseignants. Tu l'as rédigée en six étapes, mais le fichier a été réorganisé par "
            "erreur et les étapes sont mélangées."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Symptôme → service concerné → état → cause → corriger et démarrer → contrôler (0,5 pt par étape)."),
        ),
        correction=(
            "1. Constater le symptôme et noter le message exact. 2. Identifier le service concerné : le Spouleur d'impression sous Windows, cups sous Linux. 3. Lire son état (services.msc : État et Type de démarrage ; systemctl status cups).",
            "4. Chercher pourquoi il est arrêté (Observateur d'événements, journalctl -u cups -b) : le démarrer sans comprendre ne règle rien durablement. 5. Corriger (type Automatique, ou sudo systemctl enable --now cups) et démarrer. 6. Contrôler : service en cours d'exécution, page de test, et de nouveau après un redémarrage.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (4, 1, 3, 5, 0, 2)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Huit besoins sous Windows : quelle commande ?",
        question_type="classification",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Tu prépares l'aide-mémoire « invite de commandes » de l'atelier pour les nouveaux "
            "techniciens. Ton responsable a listé huit besoins rencontrés sur des postes "
            "Windows 11 de clients ; pour chacun, l'aide-mémoire doit indiquer la commande de "
            "base qui y répond directement."
        ),
        instructions=("Range chaque besoin dans la commande Windows qui y répond.",),
        criteria=(
            _c("Classement", 4, "ipconfig : configuration IP. ping : imprimante qui répond. tracert : routeur où cela s'arrête. nslookup : nom → adresse. sfc : fichiers système. DISM : magasin de composants. tasklist : processus et PID. net user : compte et groupes (0,5 pt par élément)."),
        ),
        correction=(
            "ipconfig (/all) affiche l'adresse, le masque, la passerelle et le DNS de chaque carte ; ping teste qu'une adresse répond ; tracert liste les routeurs traversés et montre où les paquets s'arrêtent ; nslookup interroge le serveur DNS sur un nom.",
            "sfc /scannow vérifie et répare les fichiers système protégés ; DISM /Online /Cleanup-Image /RestoreHealth répare le magasin de composants qui sert de référence à SFC ; tasklist liste les processus avec leur PID ; net user nom affiche l'état d'un compte local et ses groupes.",
        ),
        classification=Classification(
            categories=E04_CATEGORIES,
            elements=tuple(e for e, _c2 in E04_ELEMENTS),
            correct=tuple(E04_CATEGORIES.index(c) for _e, c in E04_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Huit besoins sous Linux : quelle commande ?",
        question_type="classification",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Le même aide-mémoire contient une page « terminal Linux » pour les postes Ubuntu "
            "des clients et le petit serveur Debian d'un client. Huit besoins y sont listés ; "
            "pour chacun, il faut indiquer la commande de base qui y répond directement."
        ),
        instructions=("Range chaque besoin dans la commande Linux qui y répond.",),
        criteria=(
            _c("Classement", 4, "ip : adresse et route. systemctl : service. journalctl : messages d'un service. lsblk : clé et UUID. df : espace libre. chmod : exécutable. chown : propriétaire. apt : installer vlc (0,5 pt par élément)."),
        ),
        correction=(
            "ip a et ip route affichent les adresses et la route par défaut ; sudo systemctl restart cups puis sudo systemctl enable cups gèrent le service (ou enable --now) ; journalctl -u ssh -b lit les messages du service depuis le démarrage ; lsblk -f liste disques, partitions, systèmes de fichiers et UUID.",
            "df -h donne l'espace utilisé et libre par système de fichiers ; chmod u+x script.sh rend le script exécutable par son propriétaire ; sudo chown anne:anne fichier rend la propriété à anne ; sudo apt install vlc installe depuis les dépôts.",
        ),
        classification=Classification(
            categories=E05_CATEGORIES,
            elements=tuple(e for e, _c2 in E05_ELEMENTS),
            correct=tuple(E05_CATEGORIES.index(c) for _e, c in E05_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Compte standard ou administrateur : quels droits pour chaque commande ?",
        question_type="classification",
        requirement_ids=("AP-11",),
        kind=KIND_ACCOUNT,
        context=(
            "Dans une agence immobilière, les employés travaillent avec des comptes standard ; "
            "seule la gérante est administratrice. Le support te demande lesquelles de ces dix "
            "commandes un employé peut lancer seul, et lesquelles demanderont l'élévation "
            "(invite de l'UAC sous Windows, sudo sous Linux)."
        ),
        instructions=("Range chaque commande selon les droits nécessaires pour qu'elle s'exécute.",),
        criteria=(
            _c("Classement", 5, "Standard : ipconfig /all, ping, net user (liste), systemctl status, df -h. Administrateur : ipconfig /release, sfc /scannow, net user … /add, sudo systemctl restart, sudo apt install (0,5 pt par élément)."),
        ),
        correction=(
            "Les commandes qui lisent une information sont accessibles à un compte standard : ipconfig /all, ping, net user (liste des comptes), systemctl status cups, df -h.",
            "Celles qui modifient le système demandent l'élévation : ipconfig /release (change la configuration réseau), sfc /scannow (répare des fichiers système), net user julie * /add (crée un compte), sudo systemctl restart cups et sudo apt install vlc. Un employé standard verra l'UAC lui demander les identifiants d'un administrateur, ou sudo refuser.",
        ),
        classification=Classification(
            categories=RIGHT_CATEGORIES,
            elements=E06_COMMANDS,
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Moindre privilège : quel compte pour chaque besoin ?",
        question_type="classification",
        requirement_ids=("AP-11",),
        kind=KIND_ACCOUNT,
        context=(
            "Tu rédiges, pour le responsable de l'atelier, une note sur les comptes à créer "
            "chez les clients. Six situations réelles du mois sont listées. Pour chacune, il "
            "faut dire quel compte créer en respectant le moindre privilège, ou s'il faut "
            "refuser la demande."
        ),
        instructions=("Range chaque situation dans le compte à créer (ou le refus).",),
        criteria=(
            _c("Classement", 3, "Standard : secrétaire, élève. Administrateur nominatif : gérant, technicien. Domaine : 40 employés avec contrôleur. Refuser : compte commun des stagiaires (0,5 pt par élément)."),
        ),
        correction=(
            "La secrétaire et l'élève n'ont pas à modifier le système : compte standard. Le gérant qui installe les logiciels et le technicien qui intervient reçoivent un compte administrateur à leur nom (et le gérant garde un compte standard pour son travail quotidien).",
            "Avec un contrôleur de domaine, chaque employé reçoit un compte de domaine, géré au même endroit. Un compte « stagiaire » commun se refuse : un compte par personne, pour que chaque action soit attribuable et que l'on puisse fermer un accès sans toucher aux autres.",
        ),
        classification=Classification(
            categories=ACCOUNT_CHOICES,
            elements=tuple(e for e, _n in E07_NEEDS),
            correct=E07_CORRECT,
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Six états de périphériques : quelle première action ?",
        question_type="classification",
        requirement_ids=("AP-05",),
        kind=KIND_DRIVER,
        context=(
            "Ton responsable te confie les fiches de six interventions de la semaine sur des "
            "postes Windows 11. Chaque fiche décrit ce qu'affichait le Gestionnaire de "
            "périphériques (icône, message et code de l'état du périphérique) et la situation. "
            "Il veut savoir quelle première action était la bonne."
        ),
        instructions=("Range chaque situation dans la première action à mener.",),
        criteria=(
            _c("Classement", 3, "Installer : Code 28 (contrôleur réseau, scanner), Code 10 sur pilote générique. Réactiver : Code 22. Restaurer : Code 10 après mise à jour. Matériel : Code 43 USB (0,5 pt par élément)."),
        ),
        correction=(
            "Code 28 : aucun pilote installé (contrôleur de réseau, scanner inconnu) : on identifie le périphérique par son ID du matériel et on installe le bon pilote ; de même pour un Code 10 sur un pilote générique après réinstallation. Code 22 : le périphérique a été désactivé, on le réactive.",
            "Code 10 juste après une mise à jour du pilote : la nouvelle version pose problème, on restaure le pilote précédent. Code 43 sur une clé USB : le périphérique répond mal, on contrôle d'abord le matériel (autre port, autre câble, port direct plutôt qu'un hub, autre PC).",
        ),
        classification=Classification(
            categories=DEVICE_ACTIONS,
            elements=tuple(e for e, *_r in E08_CASES),
            correct=E08_CORRECT,
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Une employée administratrice sans raison",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_ACCOUNT,
        context=(
            "Dans un bureau d'architectes, Marie Dubois, dessinatrice, utilise le PC du bureau 2. "
            "Lors d'un audit demandé par le gérant, tu relèves le document 1 avec le compte "
            "administrateur du gérant. Marie n'installe jamais rien elle-même : le gérant "
            "s'occupe des logiciels."
        ),
        documents=(_console("Document 1 — Invite de commandes (fictif)", *NET_USER_SCREEN),),
        instructions=(
            "Lis le document : quel est l'état et le niveau de droits du compte ?",
            "Rédige la correction, la commande exacte et le contrôle, en justifiant.",
        ),
        criteria=(
            _c("Lecture", 1, "Compte actif ; membre des groupes locaux Administrateurs et Utilisateurs : Marie est administratrice du poste."),
            _c("Correction", 1.5, "Dans une invite administrateur : net localgroup Administrateurs marie /delete (ou Paramètres → Comptes → type « Utilisateur standard ») ; elle reste dans Utilisateurs ; se déconnecter et se reconnecter ; contrôle : net user marie n'affiche plus *Administrateurs."),
            _c("Justification", 0.5, "Moindre privilège : un logiciel malveillant lancé depuis sa session aurait tous les droits ; elle n'en a pas besoin."),
        ),
        correction=(
            "Le compte de Marie est actif (« Compte : actif Oui ») et membre des groupes locaux Administrateurs et Utilisateurs : elle peut tout modifier sur le poste, après une simple confirmation de l'UAC.",
            "Elle n'administre rien : on retire ses droits, avec le compte du gérant, dans une invite de commandes en administrateur : net localgroup Administrateurs marie /delete (ou Paramètres → Comptes → Autres utilisateurs → type « Utilisateur standard »). Elle reste dans Utilisateurs ; elle se reconnecte pour que le changement s'applique. Contrôle : net user marie n'affiche plus que *Utilisateurs. Raison : moindre privilège ; un logiciel malveillant ouvert dans sa session aurait sinon tous les droits.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="L'UAC demande un mot de passe administrateur",
        question_type="document_analysis",
        requirement_ids=("AP-11",),
        kind=KIND_ACCOUNT,
        context=(
            "Un comptable, avec son compte standard, veut installer la mise à jour de son "
            "logiciel de facturation. Une fenêtre du Contrôle de compte d'utilisateur s'ouvre "
            "(document 1). Le gérant, administrateur, voit la même installation lui demander "
            "seulement « Oui / Non ». Le comptable demande qu'on fasse de lui un administrateur, "
            "« ce sera plus simple »."
        ),
        documents=(
            _console(
                "Document 1 — Contrôle de compte d'utilisateur (reconstitution fictive)",
                "Voulez-vous autoriser cette application à apporter",
                "des modifications à votre appareil ?",
                "Éditeur vérifié : Facturo SPRL",
                "Pour continuer, entrez un nom d'utilisateur et un",
                "mot de passe d'administrateur.",
                "[ Nom d'utilisateur ]  [ Mot de passe ]   Oui | Non",
            ),
        ),
        instructions=("Explique les deux comportements de l'UAC et rédige ta réponse au comptable.",),
        criteria=(
            _c("Comportements", 1.5, f"Compte standard + action d'administration : « {E10_STANDARD} » ; administrateur : « {E10_ADMIN} » ; dans les deux cas l'application ne reçoit les droits qu'après cette étape."),
            _c("Réponse", 1.5, "Pas de compte administrateur pour le comptable : le gérant saisit ses identifiants pour cette mise à jour (ou la fait lui-même) ; vérifier l'éditeur ; ne pas désactiver l'UAC ; moindre privilège."),
        ),
        correction=(
            "Le Contrôle de compte d'utilisateur (UAC) protège les modifications du système. Avec un compte standard, une action d'administration ouvre une invite qui demande le nom et le mot de passe d'un administrateur (document 1). Avec un compte administrateur, l'invite demande seulement un consentement « Oui / Non » : les droits ne sont donnés qu'après cette étape.",
            "On ne fait pas du comptable un administrateur : il n'administre pas le poste, et un logiciel malveillant ouvert depuis sa session aurait alors tous les droits. Le gérant saisit ses identifiants pour cette mise à jour (après avoir vérifié l'éditeur affiché, ici « Facturo SPRL »), ou l'installe lui-même. On ne désactive pas l'UAC.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Un périphérique inconnu après la réinstallation",
        question_type="document_analysis",
        requirement_ids=("AP-05",),
        kind=KIND_DRIVER,
        context=(
            "Après la réinstallation de Windows 11 sur le portable d'une infirmière, le Wi-Fi est "
            "absent. Dans le Gestionnaire de périphériques, un « Contrôleur de réseau » apparaît "
            "sous « Autres périphériques ». Un collègue propose de télécharger « un pack de "
            "pilotes gratuit » par le câble réseau. Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — Propriétés du périphérique (reconstitution fictive)",
                "État du périphérique :",
                "  Les pilotes de ce périphérique ne sont pas",
                "  installés. (Code 28)",
                "Détails → ID du matériel :",
                f"  {E11_ID}",
            ),
        ),
        instructions=(
            "Interprète l'état du périphérique et son ID du matériel.",
            "Rédige la marche à suivre jusqu'au contrôle, et ta réponse au collègue.",
        ),
        criteria=(
            _c("Lecture", 1, f"Code 28 : aucun pilote ; bus {E11_HW.bus}, VEN_{E11_HW.vendor_id} = {E11_VENDOR}, DEV_{E11_HW.device_id} = modèle de la puce : une carte Wi-Fi {E11_VENDOR}."),
            _c("Marche à suivre", 1.5, "Câble réseau ; Windows Update (mises à jour facultatives → pilotes) ou site du fabricant du portable (modèle exact, Windows 11, 64 bits), sinon site Intel ; point de restauration ; installation ; contrôle : « fonctionne correctement », réseaux visibles, connexion."),
            _c("Réponse au collègue", 0.5, "Refuser le pack de pilotes : source non vérifiée, logiciels indésirables, pilotes inadaptés."),
        ),
        correction=(
            f"« Code 28 » : Windows n'a installé aucun pilote pour ce périphérique. L'ID du matériel se lit ainsi : bus {E11_HW.bus}, VEN_{E11_HW.vendor_id} = fabricant {E11_VENDOR}, DEV_{E11_HW.device_id} = modèle de la puce. C'est la carte Wi-Fi {E11_VENDOR} du portable.",
            "Par le câble réseau, on passe Windows Update (Paramètres → Windows Update → Options avancées → Mises à jour facultatives → pilotes) ou on télécharge le pilote sur le site du fabricant du portable pour ce modèle exact, Windows 11 et 64 bits (à défaut, sur le site d'Intel). Point de restauration, installation, puis contrôle : « Ce périphérique fonctionne correctement », réseaux Wi-Fi visibles, connexion réussie. Le « pack de pilotes gratuit » se refuse : source non vérifiée, logiciels indésirables, pilotes inadaptés.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Permission refusée dans le dossier partagé de la comptabilité",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_ACCOUNT,
        context=(
            "Sur le petit serveur Ubuntu d'une PME, le dossier /srv/compta est partagé entre les "
            "membres du groupe compta. Julie, nouvelle comptable, a été ajoutée au groupe ; elle "
            "voit les fichiers mais ne peut rien y enregistrer. Un collègue propose « un chmod "
            "777, comme ça tout le monde peut écrire ». Tu relèves le document 1."
        ),
        documents=(_console("Document 1 — Terminal du serveur (fictif)", *LS_COMPTA_SCREEN),),
        instructions=(
            "Lis les droits du dossier et explique ce que Julie peut et ne peut pas faire.",
            "Rédige la correction exacte, son contrôle et ta réponse au collègue.",
        ),
        criteria=(
            _c("Lecture", 1, f"Propriétaire root, groupe compta, droits {COMPTA_DIR_MODE} : julie est dans compta → triplet du groupe r-x : elle liste et ouvre (lecture {'oui' if E12_CAN_READ else 'non'}), mais ne peut pas créer (écriture {'oui' if E12_CAN_WRITE else 'non'})."),
            _c("Correction", 1.5, f"sudo chmod 770 /srv/compta (ou sudo chmod g+w) → {E12_FIX_MODE} ; les autres n'ont toujours aucun accès ; contrôle : ls -ld, touch par julie, fichier créé."),
            _c("Réponse au collègue", 0.5, "777 donne l'écriture à tous les comptes, y compris hors comptabilité : données confidentielles exposées ; on donne seulement le droit manquant au groupe."),
        ),
        correction=(
            f"Le dossier appartient à root, groupe compta, avec les droits {COMPTA_DIR_MODE}. id montre que julie est membre de compta : c'est le triplet du groupe, r-x, qui s'applique. Elle peut lister (r) et entrer dans le dossier et ouvrir les fichiers (x), mais pas créer ni supprimer de fichier : il manque w, d'où « Permission denied ».",
            f"On ajoute seulement l'écriture au groupe : sudo chmod 770 /srv/compta (ou sudo chmod g+w /srv/compta), soit d{E12_FIX_MODE} ; les autres comptes n'ont toujours aucun accès. Contrôle : ls -ld /srv/compta, puis touch /srv/compta/note.txt par julie. chmod 777 se refuse : tous les comptes du serveur pourraient lire, modifier et supprimer les documents comptables.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Plus aucune impression sur un poste Ubuntu",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_SERVICE,
        context=(
            "Dans une bibliothèque, le poste Ubuntu du prêt n'imprime plus les tickets depuis "
            "qu'un bénévole « a fait du ménage dans les services pour accélérer le démarrage ». "
            "L'imprimante fonctionne depuis un autre PC. Tu relèves le document 1 avec le "
            "compte administrateur du poste."
        ),
        documents=(_console("Document 1 — Terminal (fictif)", *SYSTEMCTL_CUPS_SCREEN),),
        instructions=("Interprète le relevé et rédige la correction, avec la commande exacte et le contrôle.",),
        criteria=(
            _c("Lecture", 1, "cups (service d'impression) : « disabled » = non lancé au démarrage ; « inactive (dead) » = arrêté ; lpstat confirme que l'ordonnanceur ne tourne pas."),
            _c("Correction", 1.5, f"{E13_FIX} : sudo systemctl enable --now cups ; contrôle : systemctl status cups « active (running) » et « enabled », lpstat -p, page de test, puis redémarrage."),
            _c("Rapport", 0.5, "Noter la cause (service désactivé par un bénévole) ; ne désactiver que des services identifiés et inutiles, avec l'accord du responsable."),
        ),
        correction=(
            "cups est le service d'impression de Linux. Le relevé montre « disabled » (il n'est plus lancé au démarrage) et « Active: inactive (dead) » (il est arrêté) ; lpstat le confirme : « Scheduler is not running ». Le « ménage » a désactivé un service nécessaire.",
            "On l'active et on le démarre en une commande : sudo systemctl enable --now cups. Contrôle : systemctl status cups affiche « enabled » et « active (running) », lpstat -p liste l'imprimante, une page de test sort, et le service est toujours actif après un redémarrage. Dans le rapport : cause et correction ; à l'avenir, on ne désactive qu'un service identifié et inutile, avec l'accord du responsable.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="« Disque plein » alors qu'un disque de 1 To est installé",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Un photographe a fait ajouter un disque dur de 1 To à son PC Ubuntu pour ses "
            "archives. Une semaine plus tard, il ne peut plus copier ses photos : « le disque est "
            "plein ». Il pense que le nouveau disque est défectueux. Tu relèves le document 1 "
            "avant toute intervention."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif)",
                "$ df -h / /home",
                "Filesystem      Size  Used Avail Use% Mounted on",
                "/dev/nvme0n1p2  234G  233G  1.0G 100% /",
                "$ lsblk -f",
                "NAME        FSTYPE LABEL    MOUNTPOINTS",
                "sda",
                "└─sda1      ext4   Archives",
                "nvme0n1",
                "├─nvme0n1p1 vfat            /boot/efi",
                "└─nvme0n1p2 ext4            /",
            ),
        ),
        instructions=(
            "Explique ce que montrent les deux commandes.",
            "Rédige la correction (sans formater) et son contrôle.",
        ),
        criteria=(
            _c("Lecture", 1.5, "df : / (SSD, qui contient aussi /home) est plein à 100 % ; lsblk : sda1 (ext4, « Archives ») existe mais n'a aucun point de montage : le disque n'est pas utilisé, il n'est pas en panne."),
            _c("Correction", 1.5, "Monter sda1 (gestionnaire de fichiers, ou dossier /mnt/archives) ; montage permanent dans /etc/fstab par UUID (lsblk -f), avec nofail, après copie du fichier (PR09) ; déplacer les archives ; contrôle df -h : espace libéré sur /, sda1 monté."),
        ),
        correction=(
            "df -h montre que la racine / (sur le SSD nvme0n1p2, qui contient aussi /home) est pleine : 100 %, 1 Go libre. lsblk -f montre le disque de 1 To (sda) avec une partition ext4 « Archives », mais sans point de montage : il n'a jamais été monté, il n'est donc pas utilisé. Il n'est pas défectueux.",
            "On ne formate rien : sda1 contient déjà un système de fichiers. On le monte (gestionnaire de fichiers, ou dossier /mnt/archives), puis on le rend permanent dans /etc/fstab, par son UUID relevé avec lsblk -f et avec l'option nofail, après une copie du fichier (voir PR09). On déplace ensuite les archives du SSD vers ce disque. Contrôle : df -h montre sda1 monté et de l'espace libéré sur /.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Internet « en panne » mais l'adresse répond",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Dans une fiduciaire, le poste de la comptable a été configuré à la main la semaine "
            "dernière. Depuis, aucun site ne s'ouvre ; les autres postes, réglés en DHCP par la "
            "box (192.168.10.1, qui sert aussi de DNS), fonctionnent. Tu relèves les documents 1 "
            "à 3 sur ce poste."
        ),
        documents=(
            _console("Document 1 — ipconfig /all (fictif, abrégé)", *E15_IPCONFIG),
            _console("Document 2 — ping d'une adresse Internet (fictif)", *E15_PING_IP),
            _console("Document 3 — nslookup (fictif)", *E15_NSLOOKUP),
        ),
        instructions=(
            "Interprète les trois relevés et localise la panne.",
            "Rédige la correction et son contrôle.",
        ),
        criteria=(
            _c("Lecture", 1.5, "Configuration manuelle (DHCP Non), adresse, masque et passerelle cohérents ; ping de 203.0.113.10 : 4 reçus, Internet joignable ; nslookup : délai expiré sur 192.168.10.254 → le DNS configuré est faux."),
            _c("Correction", 1.5, "Paramètres → Réseau → Modifier l'attribution du serveur DNS : 192.168.10.1 (ou repasser en DHCP comme les autres postes) ; contrôle : ipconfig /all, nslookup réussi, site ouvert."),
        ),
        correction=(
            "Le poste est en adresse fixe (DHCP activé : Non) ; adresse 192.168.10.24, masque 255.255.255.0 et passerelle 192.168.10.1 sont cohérents. Le ping de 203.0.113.10 reçoit 4 réponses sur 4 : Internet est joignable par adresse. Mais nslookup interroge 192.168.10.254 et le délai expire : ce serveur DNS n'existe pas. Les noms ne sont pas traduits, d'où « aucun site ».",
            "On corrige le serveur DNS : Paramètres → Réseau et Internet → Ethernet → Attribution du serveur DNS → 192.168.10.1 (la box, comme pour les autres postes), ou on repasse le poste en DHCP s'il n'a pas besoin d'une adresse fixe. Contrôle : ipconfig /all affiche le bon DNS, nslookup www.exemple.be répond, le site s'ouvre.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="SFC refusé, puis SFC qui ne répare pas tout",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Sur le PC Windows 11 d'un notaire, le menu Démarrer se ferme tout seul. Ton "
            "stagiaire a ouvert l'invite de commandes avec le compte standard de la secrétaire "
            "(document 1), puis tu as relancé la commande dans une invite en administrateur "
            "(document 2). Le PC est relié à Internet ; ses données sont sauvegardées."
        ),
        documents=(
            _console("Document 1 — Invite du compte standard (fictif)", *SFC_DENIED_SCREEN),
            _console("Document 2 — Invite en administrateur (fictif)", *SFC_UNREPAIRED_SCREEN),
        ),
        instructions=(
            "Explique chacun des deux résultats.",
            "Rédige la suite de l'intervention, dans l'ordre, jusqu'au contrôle.",
        ),
        criteria=(
            _c("Document 1", 0.75, "SFC demande une invite de commandes exécutée en tant qu'administrateur : refus dans une session standard, rien n'a été vérifié."),
            _c("Document 2", 0.75, "Fichiers système corrompus, certains non réparés : le magasin de composants (référence de SFC) est lui-même abîmé ; détails dans CBS.log."),
            _c("Suite", 1.5, "En administrateur : DISM /Online /Cleanup-Image /RestoreHealth (Internet pour Windows Update) → redémarrer → sfc /scannow de nouveau → « aucune violation d'intégrité » ; menu Démarrer contrôlé ; sinon restauration (PR12)."),
        ),
        correction=(
            "Document 1 : SFC refuse de s'exécuter dans une session standard : il faut une invite de commandes lancée « en tant qu'administrateur ». Rien n'a été vérifié. Document 2 : en administrateur, SFC a trouvé des fichiers système corrompus mais n'a pas pu tous les réparer : le magasin de composants, dont SFC tire les fichiers sains, est sans doute abîmé (détails dans CBS.log).",
            "Suite, en administrateur : DISM /Online /Cleanup-Image /RestoreHealth répare le magasin de composants (il télécharge les fichiers sains depuis Windows Update : le PC doit être en ligne) ; on redémarre ; on relance sfc /scannow, qui doit afficher qu'il n'a trouvé aucune violation d'intégrité ou qu'il a réparé les fichiers. Contrôle : le menu Démarrer fonctionne. Si le problème persiste, on passe à la restauration du système (PR12).",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Corriger la procédure d'un collègue",
        question_type="long_answer",
        requirement_ids=("AP-05", "AP-11", "AP-12"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a rédigé la fiche « préparer un poste pour un nouvel employé » d'une "
            "PME (Windows 11 Pro et un serveur Ubuntu). Elle contient : 1) mettre l'employé dans "
            "Administrateurs « pour éviter les appels » ; 2) créer le compte avec net user tom "
            "Bienvenue2026 /add ; 3) désactiver l'UAC ; 4) installer les pilotes depuis "
            "pilotes-gratuits.example ; 5) sur le serveur, chmod -R 777 /srv/partage ; "
            "6) désactiver les services inconnus pour accélérer le démarrage."
        ),
        instructions=("Relève chaque erreur, explique le risque et rédige la version correcte de chaque point.",),
        criteria=(
            _c("Comptes et UAC", 2, "1) compte standard, administrateur nominatif seulement si besoin ; 2) net user tom * /add (mot de passe demandé, pas en clair) et changement à la 1re connexion ; 3) UAC laissé actif."),
            _c("Pilotes et partage", 1.5, "4) Windows Update ou site du fabricant, point de restauration ; 5) droits au groupe concerné seulement (chmod 770 ou g+w, chown :groupe), jamais 777."),
            _c("Services", 0.5, "6) ne désactiver qu'un service identifié et inutile, avec accord ; jamais « au hasard »."),
        ),
        correction=(
            "1) Un employé n'a pas à être administrateur : compte standard ; l'administration reste à une personne nommée. 2) net user tom Bienvenue2026 /add écrit le mot de passe en clair (visible, réutilisé) : net user tom * /add le demande sans l'afficher, et l'utilisateur le change à la première connexion. 3) Désactiver l'UAC supprime la protection des modifications du système : on le laisse actif.",
            "4) Un site de « pilotes gratuits » peut fournir des pilotes inadaptés ou des logiciels malveillants : Windows Update ou site du fabricant, après un point de restauration. 5) chmod -R 777 donne lecture et écriture à tous les comptes du serveur : on donne les droits au groupe concerné seulement (sudo chown -R :equipe /srv/partage puis sudo chmod 770 /srv/partage). 6) Désactiver des services inconnus peut couper l'impression, le réseau ou les mises à jour : on n'arrête qu'un service identifié et inutile, avec l'accord du responsable.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions, 2 points chacune (/20)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Les comptes d'un cabinet de trois personnes",
        question_type="long_answer",
        requirement_ids=("AP-11",),
        kind=KIND_ACCOUNT,
        context=(
            "Un cabinet d'avocats (deux avocates et une secrétaire) reçoit trois PC Windows 11 "
            "Pro, sans serveur. L'une des avocates, Me Lambert, gérera les logiciels. Jusqu'ici, "
            "tout le monde travaillait sur un seul compte « cabinet », administrateur, sans mot "
            "de passe. Le cabinet te demande un plan de comptes."
        ),
        instructions=("Rédige le plan de comptes (nom, type, groupes) et justifie-le.",),
        criteria=(
            _c("Plan", 1.25, "Un compte local par personne et par PC (standard pour les trois, y compris Me Lambert au quotidien) ; un compte administrateur nominatif pour Me Lambert ; mots de passe personnels ; ancien compte « cabinet » supprimé ou désactivé après migration des données."),
            _c("Justification", 0.75, "Moindre privilège ; actions attribuables à chacun ; un compte sans mot de passe et administrateur est la pire configuration ; sans serveur, pas de domaine : comptes locaux (ou comptes Microsoft)."),
        ),
        correction=(
            "Sur chaque PC : un compte local standard (groupe Utilisateurs) pour chaque personne, y compris Me Lambert pour son travail quotidien ; un compte administrateur à son nom (ex. « lambert-admin », groupe Administrateurs) qu'elle n'utilise que pour installer ou régler ; mots de passe personnels. Le compte « cabinet » est désactivé puis supprimé après avoir déplacé ses données.",
            "Justification : moindre privilège (un logiciel malveillant ouvert dans une session standard ne modifie pas le système) ; chaque action est attribuable à une personne ; un compte administrateur sans mot de passe est ouvert à quiconque touche le PC. Sans serveur, il n'y a pas de domaine : des comptes locaux (ou des comptes Microsoft) suffisent.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Comptes locaux et compte de domaine",
        question_type="short_answer",
        requirement_ids=("AP-11",),
        kind=KIND_ACCOUNT,
        context=(
            "Dans une entreprise dotée d'un contrôleur de domaine (ENTREPRISE), Julie ouvre le "
            "PC de la réception avec le compte « .\\julie » créé localement par un intérimaire. "
            "Elle n'accède ni au dossier partagé de son service ni à l'imprimante, alors que "
            "ses collègues, connectés avec « ENTREPRISE\\nom », y accèdent sur ce même PC."
        ),
        instructions=("Explique la différence entre les deux comptes et rédige la correction.",),
        criteria=(
            _c("Différence", 1, "« .\\julie » est un compte local, connu de ce seul PC ; « ENTREPRISE\\julie » est un compte de domaine, créé sur le contrôleur, membre des groupes qui donnent les droits sur les partages et imprimantes."),
            _c("Correction", 1, "Se connecter avec ENTREPRISE\\julie (créé par l'administrateur du domaine s'il n'existe pas) ; copier ses fichiers du profil local ; désactiver ou supprimer le compte local inutile ; contrôle : accès au partage et à l'imprimante."),
        ),
        correction=(
            "« .\\julie » est un compte local : il n'existe que sur ce PC et le serveur ne le connaît pas ; il n'est membre d'aucun groupe du domaine, d'où l'accès refusé. « ENTREPRISE\\julie » est un compte de domaine, créé sur le contrôleur de domaine : les droits sur les partages et les imprimantes sont donnés à ses groupes.",
            "Julie se connecte avec son compte de domaine (créé par l'administrateur du domaine s'il n'existe pas encore) ; on copie les fichiers du profil local vers son nouveau profil, puis on désactive ou supprime le compte local inutile. Contrôle : accès au dossier de son service et impression.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="L'écran scintille depuis la mise à jour du pilote",
        question_type="short_answer",
        requirement_ids=("AP-05",),
        kind=KIND_DRIVER,
        context=(
            "Un graphiste a installé hier soir, depuis le site du fabricant, la nouvelle version "
            "du pilote de sa carte graphique sous Windows 11. Depuis, l'écran scintille et la "
            "carte affiche « Ce périphérique ne peut pas démarrer. (Code 10) ». Avant la mise à "
            "jour, tout fonctionnait. Il a besoin du PC demain matin."
        ),
        instructions=("Rédige l'intervention adaptée, dans l'ordre, jusqu'au contrôle.",),
        criteria=(
            _c("Intervention", 1.5, "Gestionnaire de périphériques → carte graphique → Propriétés → Pilote → « Restaurer le pilote » ; si le bouton est grisé : désinstaller l'appareil et réinstaller la version précédente (site du fabricant) ou point de restauration."),
            _c("Contrôle", 0.5, "« Ce périphérique fonctionne correctement », plus de scintillement ; version notée ; suspendre la mise à jour jusqu'à une version corrigée."),
        ),
        correction=(
            "Le problème suit la mise à jour : on revient à la version précédente. Gestionnaire de périphériques → Cartes graphiques → Propriétés → onglet Pilote → « Restaurer le pilote ». Si le bouton est grisé (version précédente non conservée), on désinstalle l'appareil et on installe la version précédente depuis le site du fabricant, ou on utilise le point de restauration d'avant la mise à jour.",
            "Contrôle : état « Ce périphérique fonctionne correctement », plus de scintillement ; on note la version du pilote dans le rapport et on attend une version corrigée avant de remettre à jour.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Une imprimante USB inconnue",
        question_type="document_analysis",
        requirement_ids=("AP-05",),
        kind=KIND_DRIVER,
        context=(
            "Dans une agence de voyages, une imprimante laser USB vient d'être branchée sur un "
            "PC Windows 11 (64 bits). Elle apparaît comme « Périphérique inconnu » ; l'étiquette "
            "du modèle est illisible. Tu relèves le document 1 dans le Gestionnaire de "
            "périphériques."
        ),
        documents=(
            _console(
                "Document 1 — Propriétés (reconstitution fictive)",
                "État : Les pilotes de ce périphérique ne sont pas",
                "installés. (Code 28)",
                "Détails → ID du matériel :",
                f"  {X04_ID}",
            ),
        ),
        instructions=("Lis l'identifiant et rédige la marche à suivre pour installer le bon pilote.",),
        criteria=(
            _c("Lecture", 0.75, f"Bus USB ; VID_04F9 = {X04_VENDOR} (fabricant) ; PID = modèle ; Code 28 : aucun pilote."),
            _c("Marche à suivre", 1.25, f"Windows Update (pilotes facultatifs) ou site de {X04_VENDOR} : modèle (PID, menu de l'imprimante, page de configuration), Windows 11 64 bits ; point de restauration ; installer ; contrôle : état correct, page de test."),
        ),
        correction=(
            f"USB\\VID_04F9&PID_0062 : périphérique USB dont le fabricant (VID, identifiant attribué par l'USB-IF) est 04F9, soit {X04_VENDOR} ; le PID désigne le modèle. Code 28 : aucun pilote n'est installé.",
            f"On cherche d'abord dans Windows Update (mises à jour facultatives → pilotes), sinon sur le site de {X04_VENDOR}, pour le modèle exact (identifié par le PID, ou par la page de configuration imprimée depuis le menu de l'imprimante) et pour Windows 11 64 bits. Point de restauration, installation, puis contrôle : état « fonctionne correctement » et page de test imprimée.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Le spouleur d'impression ne tourne pas",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_SERVICE,
        context=(
            "Sur un PC Windows 11 d'un secrétariat, toute impression échoue : « Le service de "
            "spouleur d'impression local n'est pas en cours d'exécution ». Le PC a été "
            "« optimisé » par un logiciel gratuit la veille. Tu relèves les documents 1 et 2 "
            "avec le compte administrateur."
        ),
        documents=(
            _console(
                "Document 1 — tasklist (fictif)",
                'C:\\> tasklist /fi "imagename eq spoolsv.exe"',
                "INFORMATION : aucune tâche en service ne",
                "correspond aux critères spécifiés.",
            ),
            _console(
                "Document 2 — Services (reconstitution fictive)",
                "Nom : Spouleur d'impression",
                "Type de démarrage : Désactivé",
                "État du service : Arrêté",
            ),
        ),
        instructions=("Interprète les deux documents et rédige la correction et son contrôle.",),
        criteria=(
            _c("Lecture", 0.75, "spoolsv.exe (processus du spouleur) ne tourne pas ; service Désactivé et Arrêté : il ne peut pas démarrer, cause probable : le logiciel d'« optimisation »."),
            _c("Correction", 1.25, "services.msc → Spouleur d'impression → Type de démarrage Automatique → Appliquer → Démarrer ; contrôle : En cours d'exécution, tasklist trouve spoolsv.exe, page de test, encore actif après redémarrage ; désinstaller l'« optimiseur »."),
        ),
        correction=(
            "tasklist ne trouve pas spoolsv.exe, le processus du spouleur d'impression : il ne tourne pas. La console Services montre pourquoi : type de démarrage « Désactivé », état « Arrêté ». Un service désactivé ne peut pas démarrer, même à la demande ; c'est sans doute le logiciel d'« optimisation » qui l'a désactivé.",
            "services.msc → Spouleur d'impression → Propriétés → Type de démarrage « Automatique » → Appliquer → Démarrer. Contrôle : état « En cours d'exécution », tasklist affiche spoolsv.exe, une page de test sort, et le service est toujours actif après un redémarrage. On désinstalle l'« optimiseur » et on l'écrit dans le rapport.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Le service ssh ne démarre plus",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_SERVICE,
        context=(
            "Sur le serveur Debian d'une PME, l'administrateur a modifié /etc/ssh/sshd_config "
            "puis redémarré le service ; depuis, plus personne ne se connecte à distance. Tu "
            "es devant le serveur, connecté avec un compte administrateur, et tu relèves le "
            "document 1."
        ),
        documents=(
            _console(
                "Document 1 — Terminal du serveur (fictif, abrégé)",
                "$ systemctl status ssh",
                "× ssh.service - OpenBSD Secure Shell server",
                "     Active: failed (Result: exit-code)",
                "$ journalctl -u ssh -b -n 3",
                "sshd[1432]: /etc/ssh/sshd_config: line 14:",
                "  Bad configuration option: PermitRootLogn",
                "sshd[1432]: /etc/ssh/sshd_config: terminating,",
                "  1 bad configuration options",
            ),
        ),
        instructions=("Interprète le relevé et rédige la correction, avec son contrôle.",),
        criteria=(
            _c("Lecture", 0.75, "Service ssh en échec (failed) ; journalctl donne la cause : ligne 14 de sshd_config, option mal orthographiée (PermitRootLogn au lieu de PermitRootLogin)."),
            _c("Correction", 1.25, "Copie de sshd_config ; corriger la ligne 14 (sudo nano) ; tester la configuration (sudo sshd -t, aucune sortie) ; sudo systemctl restart ssh ; contrôle : systemctl status « active (running) », connexion à distance réussie."),
        ),
        correction=(
            "systemctl status montre ssh en échec (« failed », le programme s'est arrêté avec une erreur). journalctl donne la cause exacte : à la ligne 14 de /etc/ssh/sshd_config, l'option « PermitRootLogn » n'existe pas (faute de frappe pour PermitRootLogin) ; sshd refuse de démarrer avec une configuration invalide.",
            "On copie d'abord le fichier (sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak), on corrige la ligne 14 avec sudo nano, on teste la configuration (sudo sshd -t ne doit rien afficher), puis sudo systemctl restart ssh. Contrôle : systemctl status ssh affiche « active (running) » et une connexion à distance réussit.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Un script de sauvegarde qui ne se lance pas",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Paul, utilisateur d'un PC Ubuntu, a reçu de son informaticien un script de "
            "sauvegarde à lancer chaque soir. Il obtient le document 1. Un forum lui conseille "
            "« sudo chmod -R 777 /home » pour « régler tous les problèmes de droits »."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif)",
                "$ ./sauvegarde.sh",
                "bash: ./sauvegarde.sh: Permission denied",
                "$ ls -l sauvegarde.sh",
                f"{X07_SCRIPT_MODE} 1 paul paul 812 Oct 20 18:02 sauvegarde.sh",
            ),
        ),
        instructions=("Explique le refus et rédige la correction minimale, avec son contrôle et ta réponse au forum.",),
        criteria=(
            _c("Lecture", 0.75, f"Paul est propriétaire ; triplet du propriétaire rw- : pas de x, le script n'est pas exécutable (exécution {'possible' if X07_CAN_EXEC else 'impossible'})."),
            _c("Correction", 1.25, "chmod u+x sauvegarde.sh (ou chmod 744 / 754), sans sudo puisqu'il est propriétaire ; contrôle : ls -l montre -rwxr--r--, le script se lance ; refuser chmod -R 777 /home (tous les dossiers personnels ouverts à tous)."),
        ),
        correction=(
            f"ls -l montre que Paul est propriétaire de sauvegarde.sh, avec les droits {X07_SCRIPT_MODE} : le triplet du propriétaire est rw-, sans x. Le fichier n'est pas exécutable, d'où « Permission denied » quand on le lance par ./sauvegarde.sh.",
            "Correction minimale, sans sudo puisqu'il est propriétaire : chmod u+x sauvegarde.sh (droits -rwxr--r--, soit 744). Contrôle : ls -l montre le x, et ./sauvegarde.sh se lance. On refuse sudo chmod -R 777 /home : tous les dossiers personnels deviendraient lisibles et modifiables par tous les comptes.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Réseau local, mais pas d'Internet sous Linux",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Un PC Debian d'un atelier de couture a été configuré en adresse fixe par le neveu "
            "de la gérante. Il imprime sur l'imprimante réseau 192.168.1.40, mais n'atteint "
            "aucune adresse Internet. La box est 192.168.1.1. Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif, abrégé)",
                "$ ip a show enp3s0",
                "2: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP>",
                "    inet 192.168.1.50/24 scope global enp3s0",
                "$ ip route",
                "192.168.1.0/24 dev enp3s0 proto kernel scope link",
                "  src 192.168.1.50",
                "$ ping -c 2 203.0.113.10",
                "ping: connect: Network is unreachable",
            ),
        ),
        instructions=("Interprète le relevé et rédige une correction durable, avec son contrôle.",),
        criteria=(
            _c("Lecture", 0.75, "Interface UP, adresse 192.168.1.50/24 correcte pour le réseau local ; ip route : aucune ligne « default via » : pas de passerelle ; d'où « Network is unreachable » hors du réseau local."),
            _c("Correction", 1.25, "Paramètres réseau (NetworkManager) du profil filaire : passerelle 192.168.1.1 (et DNS), ou DHCP ; pas seulement sudo ip route add default via 192.168.1.1 (perdu au redémarrage) ; contrôle : ip route « default via 192.168.1.1 », ping d'une adresse puis d'un nom."),
        ),
        correction=(
            "L'interface enp3s0 est active et a l'adresse 192.168.1.50/24 : le réseau local fonctionne (l'imprimante répond). Mais ip route ne contient que la route du réseau local, aucune ligne « default via » : aucune passerelle n'est configurée. Le poste ne sait pas où envoyer les paquets vers Internet : « Network is unreachable ».",
            "Correction durable dans la configuration de NetworkManager (Paramètres → Réseau → filaire → IPv4) : passerelle 192.168.1.1 et serveur DNS, ou retour en DHCP. sudo ip route add default via 192.168.1.1 dépanne mais est perdu au redémarrage. Contrôle : ip route affiche « default via 192.168.1.1 », ping d'une adresse Internet puis d'un nom.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Un site inaccessible : lire ping, nslookup et tracert",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Dans une boulangerie, le PC de la caisse (Windows 11) n'ouvre plus le site du "
            "fournisseur, ni aucun autre site ; le téléphone de la gérante, en 4G, l'ouvre. Le "
            "PC est en DHCP derrière la box 192.168.1.1. Tu relèves les documents 1 à 3."
        ),
        documents=(
            _console("Document 1 — ping de la box (fictif)", *X09_PING_GW),
            _console("Document 2 — nslookup (fictif)", *X09_NSLOOKUP),
            _console("Document 3 — tracert (fictif)", *X09_TRACERT),
        ),
        instructions=("Interprète les trois relevés, localise la panne et dis ce que tu fais.",),
        criteria=(
            _c("Lecture", 1.25, "Box joignable (4/4) : réseau local et poste corrects ; nslookup répond (nom résolu) ; tracert : saut 1 = box, puis délais dépassés : les paquets ne vont pas au-delà de la box."),
            _c("Action", 0.75, "Panne côté accès Internet (box ou fournisseur) : voyants et page d'état de la box, redémarrage de la box avec accord, sinon appel du fournisseur ; pas de modification du PC."),
        ),
        correction=(
            "Document 1 : la box répond 4 fois sur 4 : le poste et le réseau local fonctionnent. Document 2 : nslookup obtient une réponse : le nom est résolu (la box répond depuis son cache). Document 3 : tracert passe par la box (saut 1), puis plus aucun routeur ne répond : les paquets ne sortent pas de la box vers le fournisseur.",
            "La panne est du côté de l'accès Internet (liaison de la box ou fournisseur), pas du PC : on regarde les voyants et la page d'état de la box, on la redémarre avec l'accord de la gérante, puis on appelle le fournisseur si la liaison reste coupée. On ne modifie pas la configuration du PC (dépannage réseau complet : PR24).",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Droits, risques et commandes à justifier",
        question_type="short_answer",
        requirement_ids=("AP-11", "AP-12"),
        kind=KIND_COMMAND,
        context=(
            "Une stagiaire prépare, pour un poste de bibliothèque partagé, une fiche d'aide à "
            "trois commandes : ipconfig /release pour « réparer le réseau » depuis la prise en "
            "main à distance, sudo systemctl stop ssh « pour économiser des ressources » sur le "
            "serveur distant, et sudo chown -R biblio /etc « pour éviter les erreurs de droits »."
        ),
        instructions=("Pour chacune des trois commandes, indique son rôle, les droits qu'elle demande et son risque dans cette situation.",),
        criteria=(
            _c("ipconfig /release", 0.5, "Rend le bail DHCP : le poste perd son adresse ; invite administrateur ; à distance, on perd la connexion (puis /renew impossible)."),
            _c("systemctl stop ssh", 0.75, "Arrête le service de connexion à distance ; sudo ; sur un serveur distant, on se coupe soi-même l'accès."),
            _c("chown -R /etc", 0.75, "Change le propriétaire de tous les fichiers de configuration ; sudo ; services et sudo lui-même cassés (fichiers qui doivent appartenir à root) : à refuser."),
        ),
        correction=(
            "ipconfig /release rend le bail DHCP : la carte n'a plus d'adresse ; il faut une invite administrateur. Lancé depuis une prise en main à distance, il coupe la connexion et l'on ne peut plus lancer /renew. sudo systemctl stop ssh arrête le service de connexion à distance (droits sudo) : sur un serveur distant, on se coupe soi-même l'accès.",
            "sudo chown -R biblio /etc donne à biblio la propriété de tous les fichiers de configuration du système : de nombreux services, et sudo lui-même, refusent alors de fonctionner, car ces fichiers doivent appartenir à root. La commande se refuse ; on règle un problème de droits sur le seul fichier concerné.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence officielle du cours citée."""
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
            errors.append(f"{item.key} : au moins une exigence officielle du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

"""PR12 « Dépannage logiciel et restauration du système » — exercices corrigés et mini-examen
(ticket #215).

Même organisation que PR10 (`app.v1.ampcr_pratique_pr10_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 17 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (démarche, restauration, sauvegarde), classements
  (famille de cause, effet d'un outil sur les données, précaution, commande Linux, panne réseau
  logicielle ou physique), relevés fictifs (Moniteur de fiabilité, profil temporaire, volumes
  vus dans WinRE, dpkg interrompu, GRUB, espace disque, empreintes SHA-256, fichiers restaurés
  par root), procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et relevés sont **fictifs** ; familles de causes, échelle des interventions,
précautions, empreintes, espace disque et diagnostic réseau viennent de
`app.v1.ampcr_pratique_pr12_figures` (mêmes données que les schémas). Windows en français,
Linux en anglais.
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr10_figures import can_access
from app.v1.ampcr_pratique_pr12_figures import (
    BACKUP_FILES,
    BACKUP_STEPS,
    CAUSE_ACCOUNT,
    CAUSE_APP,
    CAUSE_DRIVER,
    CAUSE_MALWARE,
    CAUSE_NAMES,
    CAUSE_OS,
    CAUSE_SERVICE,
    CAUSE_STORAGE,
    COPY_BAD,
    DPKG_SCREEN,
    EFFECTS,
    GRUB_NEW_KERNEL,
    GRUB_OLD_KERNEL,
    GRUB_SCREEN,
    LADDER_BY_NAME,
    LINUX_FIXES,
    MEDIA_DISCONNECTED_SCREEN,
    METHOD_STEPS,
    NET_LAYERS,
    PRECAUTIONS,
    RESTORE_STEPS,
    RESTORED_MODE,
    RESTORED_SCREEN,
    TEMP_PROFILE_SCREEN,
    copy_check,
    df_use_percent,
    effect_of,
    network_layer,
    precaution_for,
    sha256_hex,
)
from app.v1.ampcr_pratique_pr20_figures import Host, ipconfig_all_lines

PR12_CODE = "PR12"

KIND_ORDER = "ordonnancement"
KIND_CAUSE = "isolement de la cause"
KIND_WINDOWS = "restauration Windows"
KIND_LINUX = "dépannage Linux"
KIND_DATA = "protection des données"
KIND_NETWORK = "réseau logiciel ou physique"
KIND_ERROR = "repérage d'erreurs"

# Exigences du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-15", "AP-C03"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(METHOD_STEPS)
E02_STEPS = _labels(RESTORE_STEPS)
E03_STEPS = _labels(BACKUP_STEPS)

E04_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Seul le logiciel de facturation se ferme au démarrage, dans tous les comptes ; le reste du PC va bien", CAUSE_APP),
    ("Écran noir à chaque démarrage depuis la pose d'un pilote graphique ; tout va bien en mode sans échec", CAUSE_DRIVER),
    ("Bureau vide et « profil temporaire » pour Sophie seulement ; un compte de test fonctionne", CAUSE_ACCOUNT),
    ("Plus aucun poste n'imprime ; le spouleur d'impression du serveur est « Arrêté »", CAUSE_SERVICE),
    ("Fichiers renommés en .locked et note demandant un paiement en cryptomonnaie", CAUSE_MALWARE),
    ("« Espace disque insuffisant » et mises à jour qui échouent ; C: affiche 0,4 Go libre", CAUSE_STORAGE),
    ("Menu Démarrer et Explorateur qui plantent dans tous les comptes, aussi en mode sans échec ; SFC trouve des fichiers corrompus", CAUSE_OS),
    ("Page d'accueil du navigateur changée et fenêtres publicitaires, avec une extension inconnue", CAUSE_MALWARE),
)

E05_TOOLS = (
    "Annuler le dernier changement",
    "Réparer les fichiers système",
    "Restauration du système",
    "Réinstaller via Windows Update",
    "Réinitialiser en conservant les fichiers",
    "Réinstallation complète",
)
E05_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("« Restaurer le pilote » de la carte graphique dans le Gestionnaire de périphériques", "Annuler le dernier changement"),
    ("DISM /Online /Cleanup-Image /RestoreHealth puis sfc /scannow", "Réparer les fichiers système"),
    ("Retour au point de restauration du 12 octobre avec rstrui.exe", "Restauration du système"),
    ("Récupération → « Résoudre les problèmes à l'aide de Windows Update »", "Réinstaller via Windows Update"),
    ("« Réinitialiser ce PC » → « Conserver mes fichiers »", "Réinitialiser en conservant les fichiers"),
    ("« Réinitialiser ce PC » → « Supprimer tout »", "Réinstallation complète"),
    ("Désinstaller la dernière mise à jour qualité depuis WinRE", "Annuler le dernier changement"),
)
E05_CORRECT = tuple(EFFECTS.index(effect_of(LADDER_BY_NAME[tool])) for _e, tool in E05_ELEMENTS)

E06_CORRECT = tuple(PRECAUTIONS.index(precaution_for(LADDER_BY_NAME[tool])) for _e, tool in E05_ELEMENTS)

E07_CATEGORIES = tuple(command for _need, command in LINUX_FIXES)
E07_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Savoir si la partition / est pleine", "df -h"),
    ("La mise à jour a été coupée par une panne de courant ; apt refuse d'avancer", "sudo dpkg --configure -a"),
    ("Après l'ajout d'un noyau à la main, l'entrée n'apparaît pas dans le menu de démarrage", "sudo update-grub"),
    ("Le serveur a redémarré cette nuit ; savoir quels services ne sont pas repartis", "systemctl --failed"),
    ("Le disque externe (sdb1, démonté) signale des erreurs de système de fichiers", "sudo fsck -f /dev/sdb1"),
    ("Le PC a planté avant le redémarrage : lire les erreurs de la session d'avant", "journalctl -b -1 -p err"),
    ("La partition / est pleine : quel dossier de /var prend la place ?", "sudo du -xh -d1 /var | sort -h"),
    ("apt signale « unmet dependencies » et propose « apt --fix-broken install »", "sudo apt --fix-broken install"),
)

E08_CASES: tuple[tuple[str, dict[str, bool]], ...] = (
    ("Tout répond, nslookup aussi ; seul Firefox affiche « Le serveur proxy refuse les connexions »",
     {"link": True, "valid_ip": True, "gateway_ok": True, "internet_ok": True, "dns_ok": True}),
    ("Adresse 169.254.12.40, masque 255.255.0.0, aucune passerelle",
     {"link": True, "valid_ip": False, "gateway_ok": False, "internet_ok": False, "dns_ok": False}),
    ("ping 203.0.113.10 répond ; nslookup www.exemple.be : délai expiré",
     {"link": True, "valid_ip": True, "gateway_ok": True, "internet_ok": True, "dns_ok": False}),
    ("ipconfig : « Média déconnecté » sur la carte Ethernet du PC fixe",
     {"link": False, "valid_ip": False, "gateway_ok": False, "internet_ok": False, "dns_ok": False}),
    ("La box répond ; ping 203.0.113.10 échoue sur tous les postes ; voyant Internet de la box éteint",
     {"link": True, "valid_ip": True, "gateway_ok": True, "internet_ok": False, "dns_ok": False}),
    ("Adresse 192.168.1.30 correcte, mais le ping de la passerelle 192.168.1.1 échoue (passerelle saisie 192.168.1.254)",
     {"link": True, "valid_ip": True, "gateway_ok": False, "internet_ok": False, "dns_ok": False}),
)
E08_CORRECT = tuple(NET_LAYERS.index(network_layer(**obs)) for _e, obs in E08_CASES)

E09_RELIABILITY = (
    ("19/10/2026", "Information", "Installation réussie : Logiciel de caisse 5.2"),
    ("19/10/2026", "Information", "Installation réussie : pilote d'imprimante tickets 3.1"),
    ("20/10/2026", "Erreur critique", "Arrêt inattendu de Windows (écran bleu)"),
    ("21/10/2026", "Erreur critique", "Arrêt inattendu de Windows (écran bleu)"),
    ("21/10/2026", "Erreur", "Caisse.exe a cessé de fonctionner"),
)

E11_VOLUMES = (
    ("C:", "Récupération", "750 Mo", "Dossier Recovery, aucun dossier Windows"),
    ("D:", "(sans nom)", "475 Go", "Windows, Program Files, Users"),
    ("E:", "Données", "931 Go", "Documents de l'entreprise"),
    ("X:", "Boot", "—", "WinRE lui-même (disque virtuel en mémoire)"),
)
E11_WINDOWS_LETTER = next(letter for letter, _n, _s, content in E11_VOLUMES if content.startswith("Windows"))

E14_ROWS = (
    ("Applications et fonctionnalités", "64 Go"),
    ("Fichiers temporaires (dont « Nettoyage de Windows Update »)", "19 Go"),
    ("Téléchargements", "48 Go"),
    ("Documents", "71 Go"),
    ("Système et réservé", "33 Go"),
    ("Libre", "1,2 Go"),
)

E15_ROWS = tuple(
    (f.name, sha256_hex(f.original), sha256_hex(f.copy)) for f in BACKUP_FILES
)
E15_BAD = tuple(f.name for f in BACKUP_FILES if copy_check(f) == COPY_BAD)

E16_CAN_WRITE = can_access("anne", ("anne",), "root", "root", RESTORED_MODE, "w")
E16_CAN_READ = can_access("anne", ("anne",), "root", "root", RESTORED_MODE, "r")

X06_USED, X06_AVAIL = 45.6, 0.0
X06_PCT = df_use_percent(X06_USED, X06_AVAIL)

X10_HOST = Host("ACCUEIL-02", "portable de l'accueil", "169.254.31.7", 16, None, (), "3C-7C-3F-1A-2B-4E", dhcp=True)
_X10_LINES = ipconfig_all_lines(X10_HOST, apipa=True, iface="Wi-Fi")
X10_APIPA = (  # carte sans fil : intitulé et description propres au Wi-Fi
    "C:\\> ipconfig /all",
    "Carte réseau sans fil Wi-Fi :",
    "   Description. . . . : Intel(R) Wi-Fi 6 AX201",
    *_X10_LINES[2:],
)

# =============================================================================================
# 17 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la démarche de dépannage logiciel",
        question_type="ordering",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Un bureau d'architectes appelle l'atelier : « le PC de la secrétaire plante sans "
            "arrêt depuis lundi ». Avant de partir, ton responsable te rappelle la démarche de "
            "l'atelier pour toute panne logicielle. Sur la fiche affichée au mur, les six étapes "
            "ont été recollées dans le désordre."
        ),
        instructions=("Remets les six étapes de la démarche dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Recueillir → reproduire et délimiter → journaux → protéger les données → corriger par étapes → contrôler et rédiger (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Recueillir les faits : symptôme exact, depuis quand, qui est touché, ce qui a changé. 2. Reproduire et délimiter : la panne existe-t-elle dans un compte de test, en mode sans échec, avec un autre programme ? 3. Lire les journaux (Observateur d'événements, Moniteur de fiabilité, journalctl) pour dater et nommer l'erreur.",
            "4. Protéger les données : sauvegarde vérifiée avant la première modification (et tout de suite si le disque montre des signes de faiblesse). 5. Corriger par étapes, du geste le moins invasif au plus invasif, un seul changement à la fois. 6. Contrôler (symptôme disparu, redémarrage, journaux) et rédiger le rapport.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (2, 4, 0, 5, 3, 1)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre une restauration du système",
        question_type="ordering",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Depuis l'installation d'un utilitaire « d'optimisation » mardi, le PC Windows 11 "
            "d'une pharmacie affiche des erreurs à chaque ouverture de session. Un point de "
            "restauration a été créé lundi. La fiche « restauration du système » que tu "
            "laisses au stagiaire a ses six étapes mélangées."
        ),
        instructions=("Remets les six étapes de la restauration dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Sauvegarde et accord → ouvrir → choisir le point → programmes concernés → lancer → contrôler (0,5 pt par étape)."),
        ),
        correction=(
            "1. Vérifier que les données sont sauvegardées et obtenir l'accord du pharmacien : la restauration retire ce qui a été installé après le point. 2. Ouvrir la restauration du système (rstrui.exe, ou WinRE → Dépannage → Options avancées si Windows ne démarre pas). 3. Choisir le dernier point antérieur à la panne : ici celui de lundi.",
            "4. « Rechercher les programmes concernés » : noter ce qui sera retiré (l'utilitaire de mardi, et tout autre logiciel ou pilote installé depuis lundi). 5. Lancer, ne pas éteindre le PC pendant l'opération. 6. Contrôler : plus d'erreur à l'ouverture de session, programmes utiles réinstallés si besoin, rapport.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la sauvegarde avant intervention",
        question_type="ordering",
        requirement_ids=("AP-C03",),
        kind=KIND_ORDER,
        context=(
            "Le portable d'un indépendant doit peut-être être réinitialisé : Windows plante "
            "toutes les dix minutes. Avant tout, tu dois sauvegarder ses données sur un disque "
            "externe de l'atelier. Le mode opératoire « sauvegarde » de l'atelier a été "
            "réimprimé avec ses six étapes dans le désordre."
        ),
        instructions=("Remets les six étapes de la sauvegarde dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Inventorier → préparer le support → copier sans déplacer → vérifier → consigner → accord (0,5 pt par étape)."),
        ),
        correction=(
            "1. Inventorier avec le client ce qui compte : Documents, Bureau, Images, courriels, favoris, données d'un logiciel métier. 2. Préparer un support sain et assez grand, étiqueté à son nom. 3. Copier sans déplacer : l'original reste sur le portable tant que la copie n'est pas vérifiée.",
            "4. Vérifier la copie : nombre et taille des fichiers, empreintes SHA-256 de fichiers importants, ouverture d'essai. 5. Consigner ce qui est sauvegardé, où et quand, et ce qui ne l'est pas. 6. Seulement alors, obtenir l'accord écrit du client pour la réinitialisation.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (4, 2, 0, 5, 1, 3)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Huit pannes : dans quelle famille de cause ?",
        question_type="classification",
        requirement_ids=("AP-15",),
        kind=KIND_CAUSE,
        context=(
            "Le carnet d'interventions de la semaine compte huit pannes logicielles relevées "
            "chez différents clients. Ton responsable veut une statistique par famille de "
            "cause : système d'exploitation, application, pilote ou démarrage, service, compte, "
            "logiciel malveillant ou stockage. Chaque ligne décrit ce qui a été observé."
        ),
        instructions=("Range chaque panne dans la famille de cause que désignent les observations.",),
        criteria=(
            _c("Classement", 4, "Facturation → application ; écran noir, normal en mode sans échec → pilote ; profil temporaire d'un seul compte → compte ; spouleur arrêté → service ; .locked et rançon → malveillant ; 0,4 Go libre → stockage ; plantages partout, SFC → système ; page d'accueil et publicités → malveillant (0,5 pt par élément)."),
        ),
        correction=(
            "Un seul programme touché, dans tous les comptes : application. Un problème qui disparaît en mode sans échec vient d'un pilote, d'un service ou d'un programme lancé au démarrage, ici le pilote graphique posé juste avant. Un seul utilisateur touché alors qu'un compte de test fonctionne : compte ou profil. Une fonction précise arrêtée avec un service à l'état « Arrêté » : service.",
            "Fichiers renommés et note de rançon, ou page d'accueil changée avec publicités et extension inconnue : logiciel malveillant. Espace libre quasi nul : stockage (les mises à jour échouent faute de place). Plantages dans tous les comptes, même en mode sans échec, avec des fichiers corrompus selon SFC : système d'exploitation.",
        ),
        classification=Classification(
            categories=CAUSE_NAMES,
            elements=tuple(e for e, _c2 in E04_ELEMENTS),
            correct=tuple(CAUSE_NAMES.index(c) for _e, c in E04_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Sept gestes de réparation : que deviennent les fichiers et les programmes ?",
        question_type="classification",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_DATA,
        context=(
            "Avant de proposer une intervention à un client, tu dois lui dire clairement ce "
            "qu'il risque de perdre. Pour la fiche d'information remise aux clients de "
            "l'atelier, classe sept gestes de réparation de Windows 11 selon leur effet sur les "
            "fichiers personnels et sur les programmes installés."
        ),
        instructions=("Range chaque geste selon son effet sur les fichiers et les programmes du client.",),
        criteria=(
            _c("Classement", 3.5, "Restaurer le pilote, DISM/SFC, réinstaller via Windows Update, désinstaller la mise à jour → tout conservé ; restauration du système, réinitialiser en conservant → fichiers conservés, programmes retirés ; Supprimer tout → tout effacé (0,5 pt par élément)."),
        ),
        correction=(
            "Restaurer un pilote, désinstaller une mise à jour, DISM puis SFC et « Résoudre les problèmes à l'aide de Windows Update » (réinstallation de la version actuelle) conservent fichiers, programmes et réglages. La restauration du système conserve les documents mais retire les programmes, pilotes et mises à jour installés après le point.",
            "« Réinitialiser ce PC » en conservant les fichiers garde les documents mais retire les applications installées et les réglages ; « Supprimer tout » efface le disque : fichiers et programmes. Plus on avance, plus la sauvegarde et l'accord du client deviennent indispensables.",
        ),
        classification=Classification(
            categories=EFFECTS,
            elements=tuple(e for e, _t in E05_ELEMENTS),
            correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Les mêmes gestes : quelle précaution avant d'agir ?",
        question_type="classification",
        requirement_ids=("AP-C03",),
        kind=KIND_DATA,
        context=(
            "L'atelier a fixé une règle écrite : plus un geste retire de choses chez le client, "
            "plus il faut de garanties avant de le faire. Trois niveaux existent : noter l'état ; "
            "sauvegarde à jour et accord ; sauvegarde vérifiée et accord écrit. Pour chacun des "
            "sept gestes, indique la précaution minimale exigée par cette règle."
        ),
        instructions=("Range chaque geste dans la précaution minimale à prendre avant de le faire.",),
        criteria=(
            _c("Classement", 3.5, "Pilote, mise à jour, DISM/SFC → noter l'état ; restauration du système, réinstallation via Windows Update → sauvegarde à jour et accord ; réinitialisations → sauvegarde vérifiée et accord écrit (0,5 pt par élément)."),
        ),
        correction=(
            "Restaurer un pilote, désinstaller une mise à jour, DISM puis SFC : rien n'est retiré du client, il suffit de noter l'état avant d'agir (et l'on peut revenir en arrière). La restauration du système retire des programmes, et la réinstallation via Windows Update réécrit Windows : sauvegarde à jour et accord du client.",
            "Les deux réinitialisations retirent toutes les applications, et « Supprimer tout » efface les fichiers : sauvegarde vérifiée (empreintes, ouverture d'essai) et accord écrit du client, qui sait ce qu'il perd. Une sauvegarde reste recommandée avant toute intervention ; la règle fixe un minimum.",
        ),
        classification=Classification(
            categories=PRECAUTIONS,
            elements=tuple(e for e, _t in E05_ELEMENTS),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Huit besoins de dépannage Linux : quelle commande ?",
        question_type="classification",
        requirement_ids=("AP-15",),
        kind=KIND_LINUX,
        context=(
            "Tu complètes l'aide-mémoire « dépannage Linux » de l'atelier pour les postes "
            "Ubuntu et le petit serveur Debian d'un client. Huit situations y sont décrites ; "
            "pour chacune, l'aide-mémoire doit donner la commande qui y répond directement, "
            "telle qu'on la tape."
        ),
        instructions=("Range chaque situation dans la commande qui y répond.",),
        criteria=(
            _c("Classement", 4, "Services pas repartis → systemctl --failed ; session d'avant → journalctl -b -1 -p err ; coupure pendant la mise à jour → dpkg --configure -a ; unmet dependencies → apt --fix-broken install ; / pleine ? → df -h ; quel dossier → du ; sdb1 démonté → fsck ; menu → update-grub (0,5 pt par élément)."),
        ),
        correction=(
            "systemctl --failed liste les services en échec ; journalctl -b -1 -p err affiche les erreurs du démarrage précédent (si le journal est conservé sur disque) ; sudo dpkg --configure -a termine la configuration des paquets interrompue ; sudo apt --fix-broken install installe ou retire ce qu'il faut pour réparer les dépendances.",
            "df -h donne l'espace de chaque partition montée ; sudo du -xh -d1 /var | sort -h classe les sous-dossiers par taille sans changer de partition ; sudo fsck -f /dev/sdb1 vérifie le système de fichiers d'une partition démontée (jamais montée) ; sudo update-grub régénère le menu de GRUB.",
        ),
        classification=Classification(
            categories=E07_CATEGORIES,
            elements=tuple(e for e, _c2 in E07_ELEMENTS),
            correct=tuple(E07_CATEGORIES.index(c) for _e, c in E07_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Panne réseau : logicielle ou physique ?",
        question_type="classification",
        requirement_ids=("AP-15",),
        kind=KIND_NETWORK,
        context=(
            "Six appels « pas d'Internet » sont arrivés ce matin, de six clients différents "
            "(réseaux en 192.168.1.0/24, box 192.168.1.1 sauf indication). Pour chacun, le "
            "client t'a lu une observation au téléphone. Avant de te déplacer, tu dois situer "
            "la panne : matériel, adressage, réseau local, accès Internet, DNS ou application."
        ),
        instructions=("Range chaque observation dans l'endroit où se situe la panne.",),
        criteria=(
            _c("Classement", 3, "Média déconnecté → physique ; 169.254 → DHCP ; passerelle qui ne répond pas → configuration IP ; box injoignable vers Internet sur tous les postes → accès Internet ; IP OK, nom non → DNS ; tout OK sauf un navigateur → application ou proxy (0,5 pt par élément)."),
        ),
        correction=(
            "« Média déconnecté » : la carte ne voit aucun lien ; seule cette observation relève du matériel (câble, prise, port du switch, carte). Une adresse 169.254.x.x est une adresse d'autoconfiguration : aucun serveur DHCP n'a répondu. Une passerelle mal saisie (192.168.1.254 au lieu de 192.168.1.1) est une erreur de configuration IP.",
            "Si la box répond mais qu'aucun poste n'atteint Internet, la panne est du côté de la box ou du fournisseur. Si une adresse répond mais que le nom n'est pas résolu, c'est le DNS. Si tout répond et qu'un seul navigateur échoue avec un message de proxy, c'est un réglage logiciel du poste.",
        ),
        classification=Classification(
            categories=NET_LAYERS,
            elements=tuple(e for e, _o in E08_CASES),
            correct=E08_CORRECT,
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Le Moniteur de fiabilité désigne un changement",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_CAUSE,
        context=(
            "Le PC de caisse d'une friterie (Windows 11) fait un écran bleu une à deux fois par "
            "jour depuis le 20 octobre. La gérante dit « on n'a rien changé ». Le Moniteur de "
            "fiabilité (document 1) montre pourtant d'autres événements. Les ventes sont "
            "enregistrées chaque soir sur le serveur du fournisseur."
        ),
        documents=(
            _table("Document 1 — Moniteur de fiabilité, détails (relevé fictif)", ("Date", "Type", "Événement"), *E09_RELIABILITY),
        ),
        instructions=(
            "Interprète le relevé : quelle est la piste la plus probable ?",
            "Rédige les gestes à faire, dans l'ordre, jusqu'au contrôle.",
        ),
        criteria=(
            _c("Lecture", 1, "Deux installations le 19/10 (logiciel de caisse 5.2 et pilote d'imprimante tickets), puis écrans bleus dès le 20/10 : le changement précède la panne ; « rien changé » est contredit par le relevé."),
            _c("Démarche", 1.25, "Annuler un changement à la fois, le moins invasif d'abord : restaurer ou désinstaller le pilote de l'imprimante tickets (piste pilote : écran bleu), observer ; sinon revenir au logiciel 5.1 avec le fournisseur ou point de restauration du 18-19/10."),
            _c("Contrôle", 0.75, "Une journée sans écran bleu, Moniteur de fiabilité sans nouvel arrêt ; noter la version gardée ; signaler au fournisseur ; rapport."),
        ),
        correction=(
            "Le relevé contredit le « rien changé » : le 19 octobre, le logiciel de caisse 5.2 et le pilote de l'imprimante tickets ont été installés, et les arrêts inattendus de Windows commencent le lendemain. Un écran bleu vient le plus souvent d'un pilote : le pilote de l'imprimante tickets est la piste la plus probable, le logiciel de caisse la seconde.",
            "On annule un changement à la fois : d'abord le pilote (Gestionnaire de périphériques → Restaurer le pilote, ou désinstallation et retour à la version précédente), puis on observe ; si les écrans bleus continuent, on revient au logiciel 5.1 avec le fournisseur, ou à un point de restauration antérieur au 19 octobre (les ventes sont sur le serveur). Contrôle : une journée complète sans arrêt, Moniteur de fiabilité propre, version notée dans le rapport et problème signalé au fournisseur.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Profil temporaire : que faire, et surtout que ne pas faire",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_WINDOWS,
        context=(
            "Ce matin, Sophie, comptable d'une agence immobilière, ouvre sa session Windows 11 : "
            "son bureau est vide, ses fichiers ont « disparu », et la notification du document "
            "1 s'affiche. Elle propose de recréer ses dossiers sur ce bureau pour travailler "
            "en attendant. Le PC a subi une coupure de courant hier soir."
        ),
        documents=(_console("Document 1 — Notification et journal (fictif, abrégé)", *TEMP_PROFILE_SCREEN),),
        instructions=(
            "Explique ce qui se passe et réponds à la proposition de Sophie.",
            "Rédige l'intervention, dans l'ordre, jusqu'au contrôle.",
        ),
        criteria=(
            _c("Lecture", 0.75, "Profil local non chargé (événement 1511) : session avec un profil temporaire ; les fichiers sont toujours dans C:\\Users\\sophie, mais tout ce qui est créé maintenant sera supprimé à la déconnexion : refuser."),
            _c("Données", 0.75, "Depuis un compte administrateur : sauvegarde de C:\\Users\\sophie avant toute réparation ; vérifier le disque (espace, SMART) puis DISM et SFC (coupure de courant)."),
            _c("Réparation", 1, "Redémarrer une fois ; sinon créer un nouveau profil (nouveau compte, ou renommer l'ancien dossier) et recopier Documents, Bureau, Images, favoris, pas tout AppData ; contrôle : session normale, fichiers présents, logiciels reconfigurés."),
        ),
        correction=(
            "Windows n'a pas pu charger le profil local de Sophie (événement 1511, souvent après une coupure ou une erreur disque) et a ouvert une session avec un profil temporaire. Ses fichiers ne sont pas perdus : ils sont toujours dans C:\\Users\\sophie. En revanche, tout ce qu'elle créerait maintenant serait supprimé à la déconnexion : on refuse sa proposition.",
            "On ouvre une session avec un compte administrateur et on sauvegarde C:\\Users\\sophie ; on vérifie l'espace libre et l'état SMART du disque, puis DISM et SFC. Un redémarrage suffit parfois. Sinon, on crée un nouveau profil (nouveau compte, ou ancien compte après renommage de son dossier par un technicien) et l'on y recopie Documents, Bureau, Images et favoris, sans recopier tout AppData qui peut contenir la corruption. Contrôle : ouverture de session normale, fichiers présents, messagerie et logiciels reconfigurés.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="SFC hors ligne depuis WinRE : quelle lettre ?",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_WINDOWS,
        context=(
            "Un PC Windows 11 d'une étude de notaire ne démarre plus et la réparation du "
            "démarrage a échoué. Tu veux vérifier les fichiers système depuis l'invite de "
            "commandes de WinRE. Ton stagiaire tape « sfc /scannow » et obtient une erreur. Tu "
            "relèves les volumes visibles dans WinRE (document 1)."
        ),
        documents=(
            _table("Document 1 — Volumes vus dans WinRE (relevé fictif résumé)", ("Lettre", "Nom", "Taille", "Contenu"), *E11_VOLUMES),
        ),
        instructions=(
            "Explique pourquoi la commande du stagiaire échoue.",
            "Écris la commande correcte et dis ce que tu contrôles avant et après.",
        ),
        criteria=(
            _c("Explication", 0.75, "Dans WinRE, Windows n'est pas lancé : sfc /scannow vise le Windows en cours ; il faut l'analyse hors ligne. Les lettres changent dans WinRE : ici Windows est sur D:, X: est WinRE."),
            _c("Commande", 1, f"sfc /scannow /offbootdir={E11_WINDOWS_LETTER}\\ /offwindir={E11_WINDOWS_LETTER}\\Windows (après dir {E11_WINDOWS_LETTER}\\ pour confirmer)."),
            _c("Contrôle", 0.75, "Avant : identifier le volume Windows (dir), ne rien formater ni nettoyer avec diskpart ; données sur E: non touchées. Après : message de SFC, redémarrage, sinon restauration du système."),
        ),
        correction=(
            "Dans WinRE, le Windows du disque n'est pas en cours d'exécution : sfc /scannow ne vise que le système lancé, il faut une analyse hors ligne. De plus, les lettres de lecteur ne sont pas celles de Windows : X: est WinRE lui-même, C: est ici la partition de récupération, et le dossier Windows est sur D:.",
            f"On confirme avec dir {E11_WINDOWS_LETTER}\\ (dossiers Windows, Program Files, Users), puis : sfc /scannow /offbootdir={E11_WINDOWS_LETTER}\\ /offwindir={E11_WINDOWS_LETTER}\\Windows. On ne formate rien et l'on n'utilise pas diskpart ; le volume de données E: n'est pas touché. Après : on lit le résultat de SFC, on redémarre ; si Windows ne démarre toujours pas, on passe à la restauration du système, puis aux étapes suivantes avec sauvegarde.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Mise à jour coupée : apt refuse d'avancer",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_LINUX,
        context=(
            "Sur le PC Ubuntu d'une asbl, une panne de courant a coupé une mise à jour hier. "
            "Ce matin, toute commande apt échoue (document 1). Un bénévole propose de "
            "« réinstaller Ubuntu, ce sera plus propre ». Le PC démarre et la session s'ouvre "
            "normalement ; les dossiers des bénévoles sont dans /home."
        ),
        documents=(_console("Document 1 — Terminal (fictif)", *DPKG_SCREEN),),
        instructions=("Interprète le message, réponds au bénévole et rédige la correction avec son contrôle.",),
        criteria=(
            _c("Lecture", 0.5, "dpkg (installateur des paquets) a été interrompu : des paquets sont dépaquetés mais pas configurés ; apt se bloque tant que ce n'est pas terminé."),
            _c("Réponse", 0.5, "Pas de réinstallation : le système démarre, la correction est simple et sans risque pour /home."),
            _c("Correction", 1.5, "sudo dpkg --configure -a, puis sudo apt --fix-broken install si des dépendances restent cassées, puis sudo apt update et sudo apt upgrade ; contrôle : apt sans erreur, redémarrage, journalctl -b -p err ; onduleur ou prudence pour les mises à jour."),
        ),
        correction=(
            "La mise à jour a été coupée pendant que dpkg installait les paquets : certains sont dépaquetés mais pas configurés. apt refuse de continuer tant que cette étape n'est pas terminée et donne lui-même la commande à lancer. Une réinstallation serait disproportionnée : le système démarre, et la correction ne touche pas aux dossiers de /home.",
            "On lance sudo dpkg --configure -a, qui termine la configuration ; si apt signale encore des dépendances cassées, sudo apt --fix-broken install. Puis sudo apt update et sudo apt upgrade pour finir la mise à jour. Contrôle : apt ne signale plus d'erreur, redémarrage normal, journalctl -b -p err sans nouvelle erreur. Recommandation : ne pas éteindre pendant une mise à jour (onduleur si les coupures sont fréquentes).",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Plus de Wi-Fi depuis le nouveau noyau",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_LINUX,
        context=(
            "Depuis la mise à jour d'hier, le portable Ubuntu d'une graphiste ne trouve plus "
            "aucun réseau Wi-Fi ; tout fonctionnait avant. Tu as maintenu la touche Maj (ou Échap) "
            "au démarrage pour afficher GRUB, ouvert « Advanced options for Ubuntu » et choisi "
            "la troisième entrée : le Wi-Fi refonctionne (document 1)."
        ),
        documents=(_console("Document 1 — Menu GRUB et terminal (fictif)", *GRUB_SCREEN),),
        instructions=(
            "Interprète le relevé : qu'est-ce qui est en cause ?",
            "Rédige la suite de l'intervention et ce qu'il ne faut pas faire.",
        ),
        criteria=(
            _c("Lecture", 0.75, f"Deux noyaux installés : le nouveau {GRUB_NEW_KERNEL} (sans Wi-Fi) et l'ancien {GRUB_OLD_KERNEL} (Wi-Fi OK) : le problème suit le nouveau noyau ou le pilote Wi-Fi compilé pour lui, pas le matériel."),
            _c("Suite", 1.25, "Garder l'ancien noyau en attendant (démarrer dessus via Options avancées) ; vérifier les mises à jour suivantes ou le paquet du pilote Wi-Fi pour le nouveau noyau (apt, Pilotes additionnels) ; ne pas supprimer l'ancien noyau ; contrôle : Wi-Fi sur le nouveau noyau après correctif ; rapport."),
        ),
        correction=(
            f"GRUB propose deux noyaux : le nouveau {GRUB_NEW_KERNEL}, installé hier, et l'ancien {GRUB_OLD_KERNEL}. Sur l'ancien (uname -r le confirme), le Wi-Fi fonctionne : la carte n'est pas en panne. Le problème suit le nouveau noyau, ou le pilote Wi-Fi (parfois un module compilé pour chaque noyau) qui n'a pas été construit pour lui.",
            "En attendant, la graphiste démarre sur l'ancien noyau par « Advanced options for Ubuntu ». On cherche le correctif : mises à jour suivantes, réinstallation du paquet du pilote Wi-Fi pour le nouveau noyau (outil Pilotes additionnels). On ne supprime pas l'ancien noyau qui fonctionne (attention à apt autoremove) et l'on ne réinstalle pas Ubuntu. Contrôle : après correctif, Wi-Fi sur le nouveau noyau ; rapport.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="C: est plein : que libérer, et que ne pas toucher ?",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_WINDOWS,
        context=(
            "Le PC Windows 11 d'un comptable (SSD de 237 Go) affiche « espace disque "
            "insuffisant » et ses mises à jour échouent. Un collègue a proposé de vider "
            "C:\\Windows\\WinSxS « qui prend trop de place ». Tu relèves Paramètres → Système → "
            "Stockage (document 1). Le client garde ses téléchargements « au cas où »."
        ),
        documents=(
            _table("Document 1 — Paramètres → Stockage (relevé fictif)", ("Catégorie", "Taille"), *E14_ROWS),
        ),
        instructions=("Propose, dans l'ordre, ce que tu libères et comment, ce que tu refuses, et le contrôle.",),
        criteria=(
            _c("Libérer", 1.25, "Fichiers temporaires : Paramètres → Stockage → Fichiers temporaires, ou Nettoyage de disque → « Nettoyer les fichiers système » (nettoyage de Windows Update) ; Téléchargements : trier avec le client, déplacer sur un disque externe avec son accord ; corbeille."),
            _c("Refuser", 0.75, "Ne jamais supprimer à la main dans C:\\Windows ni WinSxS (Windows ne démarre plus ou ne se met plus à jour) ; ne pas supprimer les fichiers du client sans accord."),
            _c("Contrôle", 1, "Espace libre suffisant (repère : 15 % au moins), mises à jour installées, Assistant de stockage activé ; rapport ; si le disque reste trop petit, proposer un SSD plus grand."),
        ),
        correction=(
            "Libérer d'abord ce qui est sans risque : les fichiers temporaires (19 Go) par Paramètres → Stockage → Fichiers temporaires, ou par le Nettoyage de disque avec « Nettoyer les fichiers système », qui retire proprement les fichiers de mise à jour devenus inutiles. Les Téléchargements (48 Go) appartiennent au client : on les trie avec lui et on déplace ce qu'il veut garder sur un disque externe, avec son accord.",
            "On refuse la proposition du collègue : supprimer à la main dans C:\\Windows ou dans WinSxS peut empêcher Windows de démarrer ou de se mettre à jour ; seul l'outil de nettoyage le fait correctement. Contrôle : espace libre suffisant (repère du cours : 15 % au moins), mise à jour installée, Assistant de stockage activé ; rapport. Si le disque reste trop juste, on propose un SSD plus grand.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Vérifier une sauvegarde par empreintes SHA-256",
        question_type="document_analysis",
        requirement_ids=("AP-C03",),
        kind=KIND_DATA,
        context=(
            "Avant de réinitialiser le PC d'un entrepreneur, tu as copié ses fichiers importants "
            "sur le disque externe de l'atelier. La copie s'est terminée sans message d'erreur, "
            "mais le câble USB a bougé pendant l'opération. Tu as calculé l'empreinte SHA-256 "
            "de chaque fichier sur le PC et sur le disque (document 1)."
        ),
        documents=(
            _table("Document 1 — Empreintes SHA-256 (original / copie)", ("Fichier", "SHA-256 sur le PC", "SHA-256 sur la sauvegarde"), *E15_ROWS),
        ),
        instructions=(
            "Interprète le relevé, fichier par fichier.",
            "Dis ce que tu fais avant de lancer la réinitialisation.",
        ),
        criteria=(
            _c("Lecture", 1, f"Trois empreintes identiques : copies identiques bit à bit ; {E15_BAD[0]} : empreintes différentes, copie abîmée ou incomplète."),
            _c("Action", 1, f"Recopier {E15_BAD[0]}, recalculer son empreinte jusqu'à égalité (Get-FileHash, certutil -hashfile … SHA256) ; ouvrir l'archive ; ne pas réinitialiser avant ; consigner et obtenir l'accord écrit."),
        ),
        correction=(
            f"Une empreinte SHA-256 change dès qu'un seul octet diffère. Pour trois fichiers, l'empreinte de la copie est identique à celle de l'original : ces copies sont fidèles. Pour {E15_BAD[0]}, les deux empreintes diffèrent : la copie est abîmée ou incomplète, sans doute à cause du câble qui a bougé, même si aucun message n'est apparu.",
            f"On recopie {E15_BAD[0]} (câble fixé), on recalcule son empreinte (Get-FileHash sous PowerShell, certutil -hashfile … SHA256, ou sha256sum sous Linux) jusqu'à obtenir la même valeur, et l'on ouvre l'archive pour vérifier. Tant que toutes les copies ne sont pas vérifiées, on ne réinitialise pas. Ensuite : consigner la sauvegarde et faire signer l'accord du client.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Fichiers restaurés mais impossibles à modifier",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_LINUX,
        context=(
            "Après la réinstallation de son PC Ubuntu, tu as remis les documents d'Anne depuis "
            "la sauvegarde avec « sudo cp -r ». Anne peut les ouvrir mais pas les enregistrer : "
            "LibreOffice dit « lecture seule ». Tu relèves le document 1. Le compte d'Anne "
            "s'appelle anne, son groupe principal anne."
        ),
        documents=(_console("Document 1 — Terminal (fictif)", *RESTORED_SCREEN),),
        instructions=("Interprète le relevé et rédige la correction, sa portée exacte et son contrôle.",),
        criteria=(
            _c("Lecture", 0.75, "Fichiers à root:root, mode rw-r--r-- : Anne relève de « autres » (r--), elle lit mais ne peut pas écrire ; cause : copie faite avec sudo, sans conserver le propriétaire."),
            _c("Correction", 1.25, "sudo chown -R anne:anne /home/anne/Documents (seulement ce dossier) ; contrôle : ls -l montre anne anne, Anne enregistre un document ; la prochaine fois, cp -a ou rsync -a, ou copier en tant qu'anne ; jamais chmod 777."),
        ),
        correction=(
            "Les fichiers appartiennent à root, groupe root, avec les droits rw-r--r-- : pour Anne, qui n'est ni le propriétaire ni dans le groupe root, c'est le triplet « autres » (r--) qui s'applique : elle peut lire, pas écrire. La cause est la restauration faite avec sudo cp -r, qui crée les copies au nom de root.",
            "On rend les fichiers à Anne, sur ce seul dossier : sudo chown -R anne:anne /home/anne/Documents. Contrôle : ls -l affiche anne anne, Anne modifie et enregistre un document. On ne fait pas de chmod 777 (tout le monde pourrait modifier). La prochaine fois, on restaure avec cp -a ou rsync -a, qui conservent propriétaires et droits, ou l'on copie en étant connecté comme anne.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Corriger la procédure d'un collègue",
        question_type="long_answer",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a rédigé la fiche « PC lent ou qui plante » de l'atelier. Elle dit : "
            "1) réinstaller Windows d'emblée, c'est plus rapide ; 2) pas besoin de sauvegarde, "
            "les documents restent ; 3) désactiver l'antivirus pour gagner en vitesse ; "
            "4) sous Linux, lancer fsck sur la partition / montée ; 5) supprimer le contenu de "
            "C:\\Windows\\WinSxS ; 6) changer plusieurs réglages en même temps pour aller vite."
        ),
        instructions=("Relève chaque erreur, explique le risque et rédige la version correcte de chaque point.",),
        criteria=(
            _c("Réinstallation et données", 1.5, "1) diagnostic d'abord, gestes du moins invasif au plus invasif, réinstallation en dernier recours ; 2) sauvegarde vérifiée et accord écrit avant toute réinitialisation : « Supprimer tout » efface les documents, et toute intervention peut mal tourner."),
            _c("Sécurité et système", 1.5, "3) antivirus laissé actif, analyse plutôt que désactivation ; 4) fsck seulement sur une partition démontée (clé live ou mode de récupération) ; 5) jamais de suppression manuelle dans WinSxS, Nettoyage de disque."),
            _c("Démarche", 1, "6) un changement à la fois, contrôle après chacun, sinon on ne sait pas ce qui a réglé ou aggravé la panne ; tout noter dans le rapport."),
        ),
        correction=(
            "1) Réinstaller d'emblée fait perdre programmes, réglages et souvent la cause, qui reviendra : on diagnostique, puis on corrige du geste le moins invasif au plus invasif ; la réinstallation vient en dernier. 2) Une réinitialisation « Supprimer tout » efface les documents, et toute intervention peut mal tourner : sauvegarde vérifiée et accord écrit du client avant. 3) Désactiver l'antivirus expose le poste ; on lance au contraire une analyse (hors ligne si besoin).",
            "4) fsck sur une partition montée peut abîmer le système de fichiers : on vérifie une partition démontée, depuis une clé live ou le mode de récupération, après sauvegarde si le disque est suspect. 5) Supprimer à la main dans WinSxS peut empêcher Windows de démarrer ou de se mettre à jour : Nettoyage de disque → « Nettoyer les fichiers système ». 6) Changer plusieurs réglages à la fois empêche de savoir lequel a agi : un changement, un contrôle, une ligne dans le rapport.",
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
        title="Un premier appel : « mon PC plante »",
        question_type="long_answer",
        requirement_ids=("AP-15",),
        kind=KIND_CAUSE,
        context=(
            "La gérante d'une boutique de vêtements t'appelle : « mon PC plante, venez vite ». "
            "Elle n'en dit pas plus. Le PC sous Windows 11 sert à la caisse et à la "
            "comptabilité. Tu dois préparer ton intervention avant de te déplacer, et ton "
            "responsable te demande d'écrire ce que tu vas recueillir et faire en premier."
        ),
        instructions=("Rédige les faits à recueillir (avec une question précise pour chacun) et tes trois premiers gestes sur place.",),
        criteria=(
            _c("Faits", 1.25, "Symptôme exact et message ; depuis quand ; reproductible ou non (quelle action) ; portée (un programme, un compte, tout le PC) ; changements récents (mise à jour, logiciel, pilote, coupure) ; données importantes et sauvegarde existante."),
            _c("Premiers gestes", 0.75, "Observer et noter le message ; lire Moniteur de fiabilité et Observateur d'événements ; s'assurer d'une sauvegarde des données (caisse, comptabilité) avant toute modification."),
        ),
        correction=(
            "Faits à recueillir : le symptôme exact (« que se passe-t-il ? quel message, quel code ? ») ; depuis quand ; la reproductibilité (« le problème arrive-t-il en faisant quelque chose de précis ? ») ; la portée (un logiciel, une session, tout le PC) ; les changements récents (mise à jour, logiciel ou pilote installé, coupure de courant) ; les données importantes et l'existence d'une sauvegarde.",
            "Sur place : 1) faire reproduire ou observer le plantage et noter le message mot pour mot ; 2) lire le Moniteur de fiabilité et l'Observateur d'événements pour dater les erreurs et les rapprocher d'un changement ; 3) vérifier ou faire une sauvegarde des données de caisse et de comptabilité avant de modifier quoi que ce soit.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Word plante, mais pas pour tout le monde",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind=KIND_CAUSE,
        context=(
            "Dans un cabinet de géomètres, Word se ferme dès l'ouverture d'un document dans la "
            "session de Marc, sur son PC Windows 11. Tu crées un compte de test sur ce PC : Word "
            "y fonctionne parfaitement. Sur le PC voisin, la session de Marc (compte de domaine) "
            "fonctionne aussi. Aucun autre programme ne pose problème."
        ),
        instructions=("Situe la cause, justifie à partir des observations et propose les deux premiers gestes.",),
        criteria=(
            _c("Cause", 1, "Ni le PC, ni Word en général (compte de test OK), ni le compte en lui-même (autre PC OK) : le profil local de Marc sur ce PC (réglages ou modèle de Word, compléments) ; justification par élimination."),
            _c("Gestes", 1, "Démarrer Word en mode sans échec (winword /safe) et désactiver les compléments ; sinon sauvegarder le profil puis réinitialiser les réglages de Word ou recréer le profil local ; contrôle avec Marc."),
        ),
        correction=(
            "Word fonctionne dans un compte de test sur ce PC : ni Windows ni l'installation de Word ne sont en cause. La session de Marc fonctionne sur un autre PC : son compte non plus. Il reste ce qui est propre à Marc sur ce PC : son profil local (réglages, modèle Normal, compléments de Word).",
            "Premiers gestes : lancer Word en mode sans échec (winword /safe) et désactiver les compléments un par un ; si le problème persiste, sauvegarder le profil de Marc, puis réinitialiser les réglages de Word ou recréer son profil local et recopier ses données. Contrôle : Marc ouvre ses documents normalement.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Le scanner ne marche plus depuis la mise à jour",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind=KIND_WINDOWS,
        context=(
            "Depuis jeudi, le scanner d'un cabinet médical n'est plus reconnu par le logiciel "
            "de numérisation. L'historique de Windows Update montre une mise à jour cumulative "
            "installée jeudi matin. Le fabricant du logiciel signale sur son site un problème "
            "connu avec cette mise à jour et un correctif prévu sous deux semaines."
        ),
        instructions=("Rédige l'intervention : quoi faire, dans quel ordre, et comment éviter que le problème revienne avant le correctif.",),
        criteria=(
            _c("Retour arrière", 1.25, "Point de restauration ou état noté ; Paramètres → Windows Update → Historique → Désinstaller des mises à jour (la cumulative de jeudi) ; redémarrage ; contrôle : scanner reconnu, numérisation d'essai."),
            _c("Éviter la réinstallation", 0.75, "Suspendre les mises à jour jusqu'au correctif (Windows Update → Suspendre) ; noter dans le rapport la mise à jour retirée et la date à laquelle la réactiver."),
        ),
        correction=(
            "La coïncidence entre la mise à jour de jeudi et la panne, confirmée par le fabricant, justifie un retour arrière ciblé : on note l'état, puis Paramètres → Windows Update → Historique des mises à jour → Désinstaller des mises à jour, et l'on retire la cumulative de jeudi. Après redémarrage, on contrôle que le scanner est reconnu et l'on fait une numérisation d'essai.",
            "Pour qu'elle ne se réinstalle pas tout de suite, on suspend les mises à jour (Windows Update → Suspendre) jusqu'à la date du correctif annoncé. Le rapport indique la mise à jour retirée, la raison, et la date à laquelle il faudra reprendre les mises à jour : on ne laisse pas le poste sans mises à jour de sécurité indéfiniment.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Boucle de réparation automatique",
        question_type="long_answer",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_WINDOWS,
        context=(
            "Le PC Windows 11 d'une graphiste affiche « La réparation automatique n'a pas pu "
            "réparer votre PC » à chaque démarrage depuis l'installation d'un pilote de "
            "tablette graphique hier. Ses projets des trois derniers jours ne sont sauvegardés "
            "nulle part. Le disque est détecté par le firmware."
        ),
        instructions=("Rédige la suite des gestes depuis cet écran, dans l'ordre, avec la précaution liée à chacun, jusqu'au contrôle.",),
        criteria=(
            _c("Ordre des gestes", 1.25, "Options avancées → Paramètres → mode sans échec (4) : désinstaller ou restaurer le pilote de la tablette ; sinon Restauration du système (point d'avant hier) ; sinon Désinstaller des mises à jour ; réinitialisation seulement en dernier."),
            _c("Données", 0.75, "Projets non sauvegardés : en mode sans échec, copie des projets sur un support externe avant toute restauration ou réinitialisation ; aucune réinitialisation sans sauvegarde vérifiée et accord écrit ; contrôle : deux démarrages normaux."),
        ),
        correction=(
            "Depuis l'écran : Options avancées → Dépannage → Options avancées → Paramètres → Redémarrer, puis 4 pour le mode sans échec. Le pilote de la tablette, posé hier, est la piste : on le désinstalle ou on le restaure dans le Gestionnaire de périphériques. Si le mode sans échec n'est pas accessible ou que cela ne suffit pas : restauration du système vers un point d'avant hier ; puis désinstaller la dernière mise à jour ; la réinitialisation ne vient qu'en dernier.",
            "Les projets ne sont pas sauvegardés : dès que l'on accède au mode sans échec (ou à l'invite de WinRE), on les copie sur un support externe avant toute restauration. Aucune réinitialisation sans sauvegarde vérifiée et accord écrit de la graphiste. Contrôle : deux démarrages normaux, tablette réinstallée avec un pilote correct du fabricant, rapport.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Choisir le bon point de restauration",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_WINDOWS,
        context=(
            "Le PC d'une école de musique affiche des publicités dans le navigateur depuis le 16 "
            "octobre, après le téléchargement d'un « convertisseur audio gratuit » ce jour-là. Le "
            "logiciel de partitions a été mis à jour le 18 octobre. Tu ouvres la restauration du "
            "système (document 1)."
        ),
        documents=(
            _table(
                "Document 1 — Points de restauration (relevé fictif)",
                ("Date et heure", "Description", "Type"),
                ("18/10/2026 14:02", "Installed Partitions Pro 9.4", "Installation"),
                ("16/10/2026 10:47", "Installed Convertisseur Audio Free", "Installation"),
                ("12/10/2026 03:00", "Point de contrôle automatique", "Système"),
            ),
        ),
        instructions=("Choisis le point, justifie, et dis ce qui sera retiré, ce qui restera et ce que tu contrôles ensuite.",),
        criteria=(
            _c("Choix", 0.75, "Le point du 16/10 10:47 est créé juste avant l'installation du convertisseur : il ramène à l'état d'avant ; celui du 18/10 contient déjà le convertisseur ; celui du 12/10 retirerait plus que nécessaire."),
            _c("Effets", 0.75, "Retirés : le convertisseur et la mise à jour de Partitions Pro 9.4 (à réinstaller ensuite) ; documents conservés ; « Rechercher les programmes concernés »."),
            _c("Contrôle", 0.5, "Analyse antivirus (logiciel publicitaire), extensions du navigateur, plus de publicités ; Partitions Pro remis à jour ; rapport."),
        ),
        correction=(
            "Windows crée un point « Installed … » juste avant d'installer un programme : le point du 16/10 à 10:47 représente l'état d'avant le convertisseur. Celui du 18/10 contient déjà le convertisseur, et celui du 12/10 retirerait inutilement d'autres changements.",
            "La restauration retire le convertisseur et la mise à jour de Partitions Pro du 18/10 (à réinstaller) ; les documents ne sont pas touchés. « Rechercher les programmes concernés » le confirme avant de lancer. Ensuite : analyse antivirus complète (logiciel publicitaire), contrôle des extensions et de la page d'accueil du navigateur, mise à jour de Partitions Pro réinstallée, rapport.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="La base de données ne démarre plus sur le serveur",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_LINUX,
        context=(
            "Sur le petit serveur Debian d'une agence de voyages, le logiciel de réservation "
            "affiche « base de données indisponible » depuis ce matin. Tu relèves les documents "
            "1 et 2. Personne n'a modifié la configuration ; la sauvegarde de la base est "
            "copiée chaque nuit dans /var/backups, sur la même partition."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif, abrégé)",
                "$ systemctl status mariadb",
                "× mariadb.service - MariaDB database server",
                "     Active: failed (Result: exit-code)",
                "$ journalctl -u mariadb -b | tail -n 2",
                "mariadbd: Error writing file './ibtmp1'",
                "  (Errcode: 28 \"No space left on device\")",
            ),
            _console(
                "Document 2 — Espace disque (fictif)",
                "$ df -h /",
                "Filesystem       Size  Used Avail Use% Mounted on",
                f"/dev/sda2         48G   46G     0 {X06_PCT}% /",
            ),
        ),
        instructions=("Interprète les deux relevés et rédige l'intervention avec son contrôle.",),
        criteria=(
            _c("Lecture", 0.75, f"Service en échec ; le journal dit « No space left on device » ; df : / à {X06_PCT} %, 0 disponible : la cause est l'espace disque, pas la configuration."),
            _c("Intervention", 1, "du -xh -d1 pour trouver ce qui occupe (ex. /var/backups qui s'accumule, /var/log) ; libérer sans détruire l'unique sauvegarde (copier les anciennes sauvegardes ailleurs, journalctl --vacuum-size, apt clean) ; sudo systemctl restart mariadb."),
            _c("Contrôle", 0.25, "active (running), logiciel de réservation OK, df sous le seuil ; rotation des sauvegardes vers un autre support."),
        ),
        correction=(
            f"Le service est en échec et son journal en donne la cause : « No space left on device ». df confirme : la partition / est à {X06_PCT} %, sans aucun espace disponible. La base ne peut plus écrire ses fichiers temporaires ; la configuration n'est pas en cause.",
            "On cherche ce qui occupe la place (sudo du -xh -d1 /var | sort -h) : souvent les sauvegardes qui s'accumulent dans /var/backups ou des journaux. On libère sans détruire l'unique sauvegarde : on copie les anciennes sauvegardes sur un autre support avant de les retirer, on réduit le journal (journalctl --vacuum-size) et le cache des paquets (apt clean). Puis sudo systemctl restart mariadb. Contrôle : active (running), réservations accessibles, espace libre suffisant ; recommandation : sauvegardes sur un autre disque, avec rotation.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Fichiers chiffrés et demande de rançon",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_CAUSE,
        context=(
            "Dans une PME de cinq postes, la comptable découvre que ses fichiers ont pris "
            "l'extension .locked et qu'un fichier LISEZ-MOI demande un paiement. Le dossier "
            "partagé du serveur commence aussi à changer. La sauvegarde de la PME est faite "
            "chaque semaine sur un disque USB, débranché après chaque sauvegarde."
        ),
        instructions=("Rédige les gestes immédiats, dans l'ordre, et la suite de l'intervention.",),
        criteria=(
            _c("Immédiat", 1, "Isoler le poste du réseau (câble, Wi-Fi) sans l'éteindre si possible ; ne pas brancher le disque de sauvegarde ; prévenir le responsable ; ne pas payer ; noter l'heure et le message."),
            _c("Suite", 1, "Identifier les postes touchés ; nettoyer ou réinstaller le poste compromis, avec accord ; restaurer les fichiers depuis la sauvegarde saine antérieure ; changer les mots de passe depuis un appareil sain ; contrôle et rapport."),
        ),
        correction=(
            "Gestes immédiats : couper le poste du réseau (câble et Wi-Fi) pour arrêter le chiffrement du partage, de préférence sans l'éteindre ; ne surtout pas brancher le disque de sauvegarde, qui serait chiffré à son tour ; prévenir le responsable ; ne pas payer ; noter l'heure et le message.",
            "Ensuite : vérifier les autres postes et le serveur ; le poste compromis est nettoyé ou réinstallé, avec l'accord du responsable ; les fichiers sont restaurés depuis la sauvegarde hebdomadaire saine, antérieure à l'attaque, après contrôle qu'elle n'est pas touchée ; les mots de passe sont changés depuis un appareil sain. Contrôle : fichiers ouverts, plus de chiffrement ; rapport et recommandation de sauvegardes plus fréquentes.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="fsck sur une partition montée",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-C03"),
        kind=KIND_LINUX,
        context=(
            "Sur un PC Ubuntu, le journal signale des erreurs ext4 sur la partition racine "
            "(/dev/nvme0n1p2). Un collègue veut lancer tout de suite « sudo fsck -y "
            "/dev/nvme0n1p2 » depuis la session ouverte. Les photos de famille du client, "
            "qui ne sont sauvegardées nulle part, sont dans /home sur cette partition."
        ),
        instructions=("Explique le risque de la proposition et rédige la bonne procédure, dans l'ordre.",),
        criteria=(
            _c("Risque", 0.75, "fsck sur un système de fichiers monté (et en écriture) peut l'abîmer davantage ; -y accepte toutes les corrections sans les lire ; sans sauvegarde, perte possible des photos."),
            _c("Procédure", 1.25, "Sauvegarder d'abord /home (disque suspect) ; état du disque (SMART, smartctl ou Disques) ; puis fsck sur la partition démontée : démarrage sur une clé live ou mode de récupération ; contrôle : fsck sans erreur, démarrage, journal propre ; disque remplacé si SMART mauvais."),
        ),
        correction=(
            "fsck ne doit jamais réparer un système de fichiers monté : le système y écrit en même temps et la « réparation » peut l'abîmer davantage. L'option -y accepte toutes les corrections sans les lire. Comme les photos ne sont sauvegardées nulle part, on risquerait de les perdre.",
            "Procédure : 1) sauvegarder d'abord /home sur un support externe (des erreurs disque sont un signal d'alerte) ; 2) vérifier l'état du disque (SMART : outil Disques ou smartctl) ; 3) démarrer sur une clé live (ou le mode de récupération) pour que la partition soit démontée, puis sudo fsck -f /dev/nvme0n1p2 ; 4) contrôle : fsck termine sans erreur, démarrage normal, journal sans nouvelle erreur ext4. Si SMART est mauvais, on remplace le disque.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="« Réinstallez tout, ce sera réglé »",
        question_type="long_answer",
        requirement_ids=("AP-C03",),
        kind=KIND_DATA,
        context=(
            "Un client dépose son portable Windows 11 « trop lent » et demande : « réinstallez "
            "tout, ce sera réglé ». Il y a ses documents, ses photos et sa messagerie locale. "
            "Tu constates 98 % d'espace utilisé sur C: et une quarantaine de programmes au "
            "démarrage. Ton atelier exige un accord signé avant toute réinstallation."
        ),
        instructions=("Rédige ta réponse au client : ce que tu proposes d'abord, et ce que contiendrait l'accord écrit si la réinstallation reste nécessaire.",),
        criteria=(
            _c("Proposition", 1, "Gestes moins invasifs d'abord : libérer de l'espace (fichiers temporaires, nettoyage), désactiver les programmes inutiles au démarrage avec lui, analyse antivirus, contrôle du disque ; puis mesurer à nouveau."),
            _c("Accord", 1, "Ce qui sera effacé (programmes, réglages, messagerie locale), ce qui est sauvegardé et vérifié (liste, support), ce qu'il faudra réinstaller (licences, codes), la date, la signature ; rien sans sauvegarde vérifiée."),
        ),
        correction=(
            "Réponse : la lenteur a ici des causes visibles (C: plein à 98 %, une quarantaine de programmes au démarrage) qu'on peut traiter sans rien effacer : libérer de l'espace (fichiers temporaires, nettoyage des fichiers système, tri des fichiers avec lui), désactiver avec lui les programmes inutiles au démarrage, analyse antivirus, contrôle de l'état du disque. On mesure ensuite le résultat.",
            "Si la réinstallation reste nécessaire, l'accord écrit indique : ce qui sera effacé (programmes, réglages, messagerie locale) ; ce qui est sauvegardé, sur quel support, et que la copie a été vérifiée ; ce qu'il faudra réinstaller et ce que le client doit fournir (licences, mots de passe de ses comptes, saisis par lui) ; la date et la signature du client. Aucune réinstallation sans sauvegarde vérifiée.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Pas d'Internet : câble ou configuration ?",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind=KIND_NETWORK,
        context=(
            "À l'accueil d'un hôtel, deux PC n'ont plus Internet. Sur le PC fixe, relié par "
            "câble, tu relèves le document 1. Sur le portable, en Wi-Fi, tu relèves le "
            "document 2. Les autres appareils de l'hôtel fonctionnent ; la box (192.168.1.1) "
            "distribue les adresses par DHCP."
        ),
        documents=(
            _console("Document 1 — PC fixe (fictif)", *MEDIA_DISCONNECTED_SCREEN),
            _console("Document 2 — Portable (fictif, abrégé)", *X10_APIPA),
        ),
        instructions=("Pour chaque PC, dis si la panne est physique ou logicielle, justifie et donne le premier geste.",),
        criteria=(
            _c("PC fixe", 1, "« Média déconnecté » : aucun lien : panne physique (câble débranché ou abîmé, prise, port du switch, carte) ; vérifier le câble et les voyants, essayer un autre câble ou port."),
            _c("Portable", 1, "Adresse 169.254 d'autoconfiguration, sans passerelle : connecté mais sans réponse DHCP : panne logicielle ou de configuration ; oublier puis rejoindre le réseau Wi-Fi, ipconfig /release puis /renew (sur place), vérifier que le Wi-Fi est en DHCP ; contrôle : adresse 192.168.1.x, ping de la box, site ouvert."),
        ),
        correction=(
            "PC fixe : « Média déconnecté » signifie que la carte ne voit aucun lien électrique ; aucune configuration logicielle n'y changera rien. La panne est physique : câble débranché ou abîmé, prise murale, port du switch ou carte. Premier geste : vérifier le câble et les voyants, essayer un autre câble ou un autre port.",
            "Portable : la carte Wi-Fi est connectée mais a pris une adresse d'autoconfiguration 169.254.x.x sans passerelle : aucun serveur DHCP n'a répondu. C'est une panne logicielle ou de configuration (connexion Wi-Fi, réglage IP fixe, bail). Premier geste : oublier puis rejoindre le réseau, vérifier que la carte est en DHCP, ipconfig /release puis /renew sur place. Contrôle : adresse en 192.168.1.x, ping de la box, site ouvert.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée."""
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
    return errors

"""PR11 « Messages d'erreur Windows/Linux » — exercices corrigés et mini-examen (ticket #194).

Même organisation que PR06 (`app.v1.ampcr_pratique_pr06_bank`, dont ce module réutilise le
type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — au moins 5 analyses de captures ou de journaux, 5 procédures
  ordonnées et 3 cas croisés matériel / système / réseau ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les messages, codes et commandes sont ceux des systèmes réels (sources dans le cours) ; les
machines, personnes, dates, noms de pilotes et UUID sont fictifs. Chaque question donne tout
le contexte nécessaire : aucun message isolé, aucun développé d'acronyme.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)

PR11_CODE = "PR11"

KIND_ANALYSIS = "analyse de capture ou de journal"
KIND_PROCEDURE = "procédure ordonnée"
KIND_CROSS = "cas croisé matériel / système / réseau"
KIND_SCENARIO = "scénario"


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _console(title: str, *lines: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="console", content_text="\n".join(lines))


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="À quel stade chaque erreur survient-elle ?",
        question_type="classification",
        requirement_ids=("AP-09", "AP-13"),
        kind=KIND_ANALYSIS,
        context=(
            "Au service informatique d'une commune, tu tries les tickets du matin. Chaque ticket "
            "contient le message exact relevé par l'utilisateur et le moment où il est apparu. "
            "Avant de chercher une cause, tu dois situer le stade où l'erreur se produit."
        ),
        instructions=(
            "Range chaque message dans le stade où il apparaît.",
        ),
        criteria=(
            _c("Classement", 6, "Reboot and Select proper Boot device = firmware / POST (aucun support de démarrage trouvé) ; grub rescue> = chargeur ; écran bleu INACCESSIBLE_BOOT_DEVICE = noyau / système ; profil temporaire = ouverture de session ; Failed to start cups.service = service ; Code 43 = pilote / périphérique (1 point par message)."),
        ),
        correction=(
            "« Reboot and Select proper Boot device » est affiché par le firmware : il n'a trouvé aucun support de démarrage valable. Le système n'a même pas commencé à se charger.",
            "« error: no such partition. grub rescue> » vient du chargeur GRUB : le firmware a passé la main, mais GRUB ne trouve plus sa partition.",
            "« INACCESSIBLE_BOOT_DEVICE » est un écran bleu au démarrage du noyau Windows : le noyau a démarré mais ne peut plus accéder au disque système (pilote de stockage, mode SATA changé).",
            "« Vous êtes connecté avec un profil temporaire » apparaît à l'ouverture de session : le système fonctionne, le profil de l'utilisateur n'a pas pu être chargé.",
            "« Failed to start cups.service » concerne un service (ici l'impression sous Linux) : le système est démarré, ce service précis a échoué.",
            "« Windows a arrêté ce périphérique… (Code 43) » concerne un pilote ou un périphérique : le périphérique a signalé un problème à son pilote.",
        ),
        classification=Classification(
            categories=("Firmware / POST", "Chargeur d'amorçage", "Noyau / système", "Ouverture de session", "Service", "Pilote / périphérique"),
            elements=(
                "Écran bleu au démarrage : « Code d'arrêt : INACCESSIBLE_BOOT_DEVICE ».",
                "« Windows a arrêté ce périphérique car il a signalé des problèmes. (Code 43) » pour une imprimante USB.",
                "Avant tout logo : « Reboot and Select proper Boot device or Insert Boot Media in selected Boot device ».",
                "Bureau vide et message « Vous êtes connecté avec un profil temporaire ».",
                "« error: no such partition. Entering rescue mode... grub rescue> ».",
                "Sur un serveur Linux démarré : « Failed to start cups.service - CUPS Scheduler. »",
            ),
            correct=(2, 5, 0, 3, 1, 4),
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Corrélation ou cause ? Lire l'Observateur d'événements",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Un PC portable de l'accueil d'une PME redémarre brutalement, en moyenne une fois par "
            "jour, depuis lundi. La responsable affirme : « C'est la mise à jour de lundi qui a tout "
            "cassé, il faut réinstaller Windows. » Tu as exporté les événements du journal Système "
            "(document 1)."
        ),
        instructions=(
            "Reconstitue la chronologie et indique ce que chaque événement prouve, et ce qu'il ne prouve pas.",
            "Dis si la conclusion de la responsable est justifiée et propose les deux tests suivants, non destructifs.",
        ),
        documents=(
            _table(
                "Document 1 — Journal Système, extrait filtré (fictif)",
                ("Niveau", "Date et heure", "Source", "ID", "Message (résumé)"),
                ("Information", "lun. 09/03 12:30", "WindowsUpdateClient", "19", "Installation réussie : mise à jour cumulative"),
                ("Information", "lun. 09/03 16:05", "UserPnp", "20003", "Service du pilote ajouté : pilote graphique installé depuis le site du fabricant"),
                ("Critique", "mar. 10/03 10:41", "Kernel-Power", "41", "Le système a redémarré sans arrêt correct préalable"),
                ("Erreur", "mar. 10/03 10:41", "BugCheck", "1001", "Redémarrage après vérification d'erreur 0x00000116"),
                ("Critique", "mer. 11/03 14:02", "Kernel-Power", "41", "Le système a redémarré sans arrêt correct préalable"),
                ("Erreur", "mer. 11/03 14:02", "BugCheck", "1001", "Redémarrage après vérification d'erreur 0x00000116"),
            ),
        ),
        criteria=(
            _c("Chronologie", 1, "Mise à jour Windows lundi 12:30, pilote graphique installé lundi 16:05, puis redémarrages mardi et mercredi avec le même code."),
            _c("Valeur de chaque événement", 1.5, "Kernel-Power 41 = arrêt non propre (indice, pas une cause) ; BugCheck 1001 = écran bleu avec code 0x116 (VIDEO_TDR_FAILURE, lié à l'affichage) ; deux changements le même jour : coïncidence possible, pas une preuve."),
            _c("Conclusion de la responsable", 0.75, "Non justifiée : deux changements candidats, le code oriente plutôt vers le pilote graphique ; réinstaller détruirait la configuration sans rien prouver."),
            _c("Tests non destructifs", 0.75, "Restaurer le pilote graphique précédent (Gestionnaire de périphériques) et observer ; vérifier températures et charge graphique ; si besoin désinstaller la mise à jour ensuite, un seul changement à la fois."),
        ),
        correction=(
            "Chronologie : lundi 12:30 mise à jour cumulative ; lundi 16:05 nouveau pilote graphique ; mardi 10:41 et mercredi 14:02, deux redémarrages brutaux, chaque fois avec le même code d'arrêt.",
            "Kernel-Power 41 dit seulement que Windows ne s'est pas arrêté proprement : c'est une conséquence, pas une cause. BugCheck 1001 indique qu'un écran bleu a eu lieu, avec le code 0x116 (VIDEO_TDR_FAILURE) : le pilote graphique n'a pas répondu à temps. Deux changements ont eu lieu le même jour ; leur proximité avec les pannes est une corrélation, pas une preuve.",
            "La conclusion « c'est la mise à jour, il faut réinstaller » n'est pas justifiée : le code oriente plutôt vers l'affichage, et une réinstallation est lourde et ne démontre rien.",
            "Tests : 1) restaurer le pilote graphique précédent (Gestionnaire de périphériques > Pilote > Restaurer le pilote) puis observer quelques jours ; 2) si les écrans bleus continuent, contrôler températures et stabilité de la carte graphique, puis seulement ensuite désinstaller la mise à jour. Un seul changement à la fois, chaque résultat noté.",
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Trois périphériques, trois codes",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-05", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Sur un PC de bureau fraîchement réinstallé dans un cabinet médical, trois "
            "périphériques posent problème. Tu as relevé, dans le Gestionnaire de périphériques, "
            "le symbole et le texte de l'onglet « État du périphérique » (document 1)."
        ),
        instructions=(
            "Pour chaque périphérique, explique ce que le code indique et l'action à mener en premier.",
            "Dis lequel des trois demande le plus de tests avant de conclure, et pourquoi.",
        ),
        documents=(
            _table(
                "Document 1 — Relevé du Gestionnaire de périphériques (fictif)",
                ("Périphérique", "Symbole", "État du périphérique"),
                ("Contrôleur Ethernet (sous « Autres périphériques »)", "Triangle jaune", "Les pilotes de ce périphérique ne sont pas installés. (Code 28)"),
                ("Lecteur de cartes SD", "Flèche vers le bas", "Ce périphérique est désactivé. (Code 22)"),
                ("Lecteur de cartes d'identité USB", "Triangle jaune", "Windows a arrêté ce périphérique car il a signalé des problèmes. (Code 43)"),
            ),
        ),
        criteria=(
            _c("Code 28", 0.75, "Aucun pilote installé : installer le pilote du fabricant de la carte mère ou du PC (support du modèle), vérifier ensuite l'état."),
            _c("Code 22", 0.75, "Périphérique simplement désactivé : le réactiver (clic droit > Activer), après avoir vérifié qu'il n'a pas été désactivé volontairement."),
            _c("Code 43", 1, "Le périphérique ou son pilote a signalé un défaut : autre port, autre câble, essai sur un autre PC, pilote du fabricant ; peut être matériel ou logiciel."),
            _c("Le plus de tests", 0.5, "Code 43 : code générique, cause matérielle ou logicielle possible ; on ne conclut qu'après des tests croisés."),
        ),
        correction=(
            "Code 28 (contrôleur Ethernet) : aucun pilote n'est installé, ce qui est fréquent juste après une réinstallation. On télécharge le pilote sur le site du fabricant du PC ou de la carte mère (depuis un autre poste, puisque le réseau ne fonctionne pas) et on l'installe ; l'état doit devenir « Ce périphérique fonctionne correctement ».",
            "Code 22 (lecteur SD) : le périphérique est désactivé. On vérifie qu'il ne l'a pas été volontairement (politique du cabinet), puis on le réactive.",
            "Code 43 (lecteur de cartes d'identité) : le périphérique a signalé un problème. Le code ne dit pas si c'est matériel ou logiciel : on essaie un autre port USB (directement sur le PC, sans concentrateur), un autre câble, le lecteur sur un autre PC, puis le pilote du fabricant.",
            "C'est le code 43 qui demande le plus de tests : il est générique, et la cause peut être le lecteur, le câble, le port ou le pilote.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Serveur Linux en mode d'urgence après un remplacement de disque",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-13", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Dans une école, le petit serveur Linux (Debian) de partage de fichiers a reçu hier un "
            "nouveau disque de données, sur lequel un collègue a recopié le contenu de l'ancien. "
            "Ce matin, il ne démarre plus normalement et affiche le document 1. Tu as ensuite "
            "relevé le document 2 depuis le mode d'urgence."
        ),
        instructions=(
            "Explique ce qui se passe, étape par étape, à partir des deux documents.",
            "Décris la correction, sa vérification avant redémarrage, puis la validation.",
        ),
        documents=(
            _console(
                "Document 1 — Écran de démarrage (extrait fictif)",
                "[ TIME ] Timed out waiting for device dev-disk-by\\x2duuid-7d3c…51fe.device.",
                "[DEPEND] Dependency failed for /data.",
                "[DEPEND] Dependency failed for Local File Systems.",
                "You are in emergency mode. After logging in, type \"journalctl -xb\" to view",
                "system logs, \"systemctl reboot\" to reboot, \"systemctl default\" or \"exit\"",
                "to boot into default mode.",
                "Give root password for maintenance",
                "(or press Control-D to continue):",
            ),
            _console(
                "Document 2 — Commandes en mode d'urgence (extrait fictif)",
                "# lsblk -o NAME,FSTYPE,UUID,MOUNTPOINTS",
                "NAME   FSTYPE UUID            MOUNTPOINTS",
                "sda",
                "├─sda1 vfat   4C1E-2A7B       /boot/efi",
                "└─sda2 ext4   9b2f…6c1d       /",
                "sdb",
                "└─sdb1 ext4   e41a…0b93",
                "# grep data /etc/fstab",
                "UUID=7d3c…51fe  /data  ext4  defaults  0  2",
            ),
        ),
        criteria=(
            _c("Lecture", 1.5, "fstab demande de monter /data depuis l'UUID 7d3c…51fe ; ce disque n'existe plus (ancien disque) ; le délai expire, /data et Local File Systems échouent par dépendance, systemd passe en mode d'urgence ; le nouveau disque sdb1 a l'UUID e41a…0b93."),
            _c("Correction", 1, "Sauvegarder /etc/fstab (copie), remplacer l'UUID par celui de sdb1 (lu avec lsblk ou blkid), éventuellement option nofail pour un disque non indispensable au démarrage."),
            _c("Vérification", 1, "Tester avant redémarrage : mount -a (ou findmnt --verify) sans erreur, /data monté avec les fichiers attendus ; puis redémarrage complet sans mode d'urgence, partage accessible."),
            _c("Prudence", 0.5, "Pas de formatage ni de fsck au hasard : le disque est sain, c'est la configuration qui est fausse."),
        ),
        correction=(
            "Au démarrage, systemd lit /etc/fstab et attend le disque d'UUID 7d3c…51fe pour le monter sur /data. Ce disque était l'ancien : il n'existe plus. Le délai d'attente expire (TIME), le montage de /data échoue, puis la cible Local File Systems échoue à son tour (DEPEND) : systemd passe en mode d'urgence.",
            "Le document 2 le confirme : le nouveau disque est sdb1, d'UUID e41a…0b93, non monté. Aucun système de fichiers ne porte l'UUID cherché par fstab.",
            "Correction : copier d'abord /etc/fstab (cp /etc/fstab /etc/fstab.bak), puis remplacer l'UUID de la ligne /data par celui de sdb1, lu avec lsblk ou blkid. Si /data n'est pas indispensable au démarrage, l'option nofail évite à l'avenir le mode d'urgence.",
            "Vérification avant redémarrage : mount -a (ou findmnt --verify) ne renvoie aucune erreur et /data contient bien les fichiers copiés. Validation : redémarrage complet sans mode d'urgence, partage accessible depuis un poste client. Aucun formatage ni fsck : le disque est sain, seule la configuration était fausse.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="« Permission denied » sur un dossier partagé",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-27", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Sur le serveur Linux d'une petite agence, Julie (compte julie) doit déposer les devis "
            "dans /srv/devis, comme les autres membres du groupe commercial. Elle obtient une "
            "erreur. Un collègue propose : « Fais un chmod 777 et on n'en parle plus. » Tu as "
            "relevé le document 1."
        ),
        instructions=(
            "Explique la cause à partir des droits et des groupes affichés.",
            "Refuse la proposition du collègue en justifiant, et propose une correction minimale, puis sa vérification.",
        ),
        documents=(
            _console(
                "Document 1 — Relevé dans le terminal (extrait fictif)",
                "julie@srv:~$ cp devis-0412.pdf /srv/devis/",
                "cp: cannot create regular file '/srv/devis/devis-0412.pdf': Permission denied",
                "julie@srv:~$ ls -ld /srv/devis",
                "drwxrwx--- 2 marc commercial 4096 mars 10 08:30 /srv/devis",
                "julie@srv:~$ id julie",
                "uid=1004(julie) gid=1004(julie) groups=1004(julie)",
            ),
        ),
        criteria=(
            _c("Lecture des droits", 1, "Dossier propriété de marc, groupe commercial, droits rwx pour le propriétaire et le groupe, aucun droit pour les autres ; julie n'est pas membre du groupe commercial, elle tombe dans « autres »."),
            _c("Refus de chmod 777", 1, "777 donne lecture, écriture et exécution à tous les comptes du serveur : fuite et suppression possibles des devis ; cela masque l'erreur au lieu de la corriger."),
            _c("Correction minimale", 1, "Ajouter julie au groupe commercial (usermod -aG commercial julie, par un administrateur, avec accord) ; nouvelle connexion nécessaire pour que le groupe soit pris en compte."),
            _c("Vérification", 1, "id julie montre le groupe commercial ; dépôt d'un fichier réussi ; un compte hors groupe reste refusé."),
        ),
        correction=(
            "ls -ld montre drwxrwx--- : le propriétaire (marc) et le groupe (commercial) ont lecture, écriture et accès ; les autres n'ont aucun droit. id julie montre que julie n'appartient qu'à son groupe personnel : pour ce dossier, elle fait partie des « autres », d'où le refus.",
            "chmod 777 donnerait tous les droits à tous les comptes du serveur : n'importe qui pourrait lire, modifier ou supprimer les devis. C'est une faille de sécurité qui masque la vraie cause ; on ne l'utilise jamais comme dépannage.",
            "Correction minimale : un administrateur ajoute julie au groupe commercial (sudo usermod -aG commercial julie), avec l'accord du responsable. Julie se déconnecte et se reconnecte pour que le nouveau groupe soit pris en compte.",
            "Vérification : id julie affiche commercial ; le dépôt d'un fichier réussit ; un compte qui n'est pas du groupe est toujours refusé.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Disque « plein » à 41 %",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Sur le serveur Linux d'un atelier, l'application qui enregistre les photos des "
            "réparations renvoie « No space left on device ». Le gérant ne comprend pas : « Il "
            "reste plus de la moitié du disque ! » Tu as relevé le document 1."
        ),
        instructions=(
            "Explique la contradiction apparente à partir du document.",
            "Indique comment trouver le dossier en cause et la démarche de correction, sans supprimer de données au hasard.",
        ),
        documents=(
            _console(
                "Document 1 — Relevé (extrait fictif)",
                "$ df -h /srv",
                "Filesystem      Size  Used Avail Use% Mounted on",
                "/dev/sdb1       916G  352G  518G  41% /srv",
                "$ df -i /srv",
                "Filesystem       Inodes   IUsed IFree IUse% Mounted on",
                "/dev/sdb1      61054976 61054976     0  100% /srv",
            ),
        ),
        criteria=(
            _c("Explication", 1.5, "L'espace en octets est libre (41 %), mais tous les inodes sont utilisés (100 %) : chaque fichier consomme un inode, il est impossible d'en créer un nouveau, d'où le même message « No space left on device »."),
            _c("Recherche", 1, "Trouver le dossier qui contient des millions de petits fichiers : compter les fichiers par dossier (par exemple du --inodes -x -d1 /srv, ou find … | wc -l), souvent un cache, des miniatures ou des fichiers temporaires."),
            _c("Correction prudente", 1, "Identifier l'application qui les crée, vérifier avec le responsable ce qui peut être supprimé ou archivé, sauvegarde si doute ; corriger la cause (purge automatique, rotation)."),
            _c("Validation", 0.5, "df -i montre des inodes libres, l'application enregistre de nouveau, surveillance dans les jours suivants."),
        ),
        correction=(
            "df -h montre 41 % d'espace utilisé, mais df -i montre 100 % des inodes utilisés. Sur un système de fichiers ext4, chaque fichier consomme un inode, dont le nombre est fixé à la création. Quand il n'en reste plus, on ne peut plus créer de fichier même s'il reste de la place : le message est le même, « No space left on device ».",
            "Recherche : compter les fichiers par dossier (du --inodes -x -d1 /srv, puis on descend dans le dossier le plus chargé). On trouve en général des millions de petits fichiers : cache, miniatures, fichiers temporaires ou de session.",
            "Correction : identifier l'application qui crée ces fichiers, décider avec le responsable de ce qui peut être supprimé ou archivé (sauvegarde en cas de doute), puis corriger la cause : purge automatique du cache, rotation.",
            "Validation : df -i montre des inodes libres, l'application enregistre de nouveau les photos ; on surveille le compteur les jours suivants.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Ordonner la méthode universelle",
        question_type="ordering",
        requirement_ids=("AP-13", "AP-C03", "AP-C01"),
        kind=KIND_PROCEDURE,
        context=(
            "Un stagiaire doit intervenir seul sur le PC d'une comptable qui affiche des erreurs "
            "de lecture de fichiers depuis ce matin. Tu lui prépares une fiche avec les grandes "
            "étapes de toute intervention sur un message d'erreur, dans le bon ordre."
        ),
        instructions=(
            "Remets les six étapes dans l'ordre où elles doivent être réalisées.",
        ),
        criteria=(
            _c("Ordre", 6, "Protéger les données → collecter les preuves → tests simples → réparation réversible → opération invasive avec autorisation → validation."),
        ),
        correction=(
            "1. Protéger les données (sauvegarde ou copie des fichiers importants) : des erreurs de lecture peuvent annoncer une panne de disque, et chaque manipulation peut aggraver la situation.",
            "2. Collecter les preuves : message exact, code, heure, journaux, captures, avant qu'un redémarrage ou une réparation ne les efface.",
            "3. Tests simples et non destructifs : vérifier le périmètre (un fichier, un dossier, tout le disque), l'état du disque, l'espace.",
            "4. Réparation réversible : par exemple restaurer un pilote, revenir à un point de restauration, corriger un réglage.",
            "5. Opération invasive (réparation du système de fichiers, réinstallation) seulement avec l'autorisation de la cliente, une fois les données à l'abri.",
            "6. Validation : reproduire le scénario, vérifier que l'erreur a disparu, puis le noter dans le compte rendu.",
        ),
        ordering=Ordering(
            steps=(
                "Réparation réversible (restaurer un pilote, un réglage, un point de restauration).",
                "Collecter les preuves : message exact, code, heure, journaux, captures.",
                "Validation : reproduire le scénario et vérifier que l'erreur a disparu.",
                "Protéger les données : sauvegarde ou copie des fichiers importants.",
                "Opération invasive seulement avec l'autorisation de la cliente.",
                "Tests simples et non destructifs : périmètre, état du disque, espace libre.",
            ),
            correct=(3, 1, 5, 0, 4, 2),
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Fichiers système Windows endommagés : DISM puis SFC",
        question_type="ordering",
        requirement_ids=("AP-11", "AP-13", "AP-15"),
        kind=KIND_PROCEDURE,
        context=(
            "Sur un PC Windows 11 d'un secrétariat, le menu Démarrer ne s'ouvre plus et plusieurs "
            "applications intégrées se ferment au lancement. Le disque est en bon état (rapport "
            "SMART correct) et les données sont sauvegardées sur le serveur. Tu décides de "
            "vérifier et réparer les fichiers système avec les outils intégrés."
        ),
        instructions=(
            "Remets les étapes de la procédure dans l'ordre.",
        ),
        criteria=(
            _c("Ordre", 6, "Vérifier la sauvegarde → invite de commandes en administrateur → DISM /Online /Cleanup-Image /RestoreHealth → sfc /scannow → redémarrer → valider (symptômes, nouveau sfc sans erreur)."),
        ),
        correction=(
            "1. Vérifier que les données sont sauvegardées (c'est le cas ici) : même des outils de réparation intégrés modifient le système.",
            "2. Ouvrir une invite de commandes ou un terminal en administrateur : sans élévation, DISM et SFC refusent de s'exécuter.",
            "3. DISM /Online /Cleanup-Image /RestoreHealth : répare le magasin de composants de Windows, qui sert de référence à SFC (il télécharge les fichiers sains depuis Windows Update, donc il faut une connexion Internet, ou une source indiquée).",
            "4. sfc /scannow : vérifie les fichiers système protégés et remplace ceux qui sont endommagés à partir de ce magasin (résultat dans CBS.log).",
            "5. Redémarrer pour que les fichiers remplacés soient utilisés.",
            "6. Valider : le menu Démarrer et les applications fonctionnent ; un nouveau sfc /scannow ne trouve plus de violation d'intégrité.",
        ),
        ordering=Ordering(
            steps=(
                "Lancer sfc /scannow.",
                "Redémarrer le PC.",
                "Ouvrir une invite de commandes en administrateur.",
                "Vérifier que les données sont sauvegardées.",
                "Valider : symptômes disparus, nouveau sfc /scannow sans violation.",
                "Lancer DISM /Online /Cleanup-Image /RestoreHealth.",
            ),
            correct=(3, 2, 5, 0, 1, 4),
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="« No bootable device » après une mise à jour du firmware",
        question_type="long_answer",
        requirement_ids=("AP-09", "AP-13", "AP-15"),
        kind=KIND_PROCEDURE,
        context=(
            "Un indépendant a mis à jour le firmware (BIOS/UEFI) de son PC de bureau. Depuis, "
            "l'écran affiche « No bootable device -- insert boot disk and press any key ». Il "
            "n'a touché à rien d'autre. Son disque NVMe contient Windows 11 et toute sa "
            "comptabilité, sauvegardée la semaine dernière."
        ),
        instructions=(
            "Rédige la procédure de diagnostic dans l'ordre, du plus simple au plus invasif, en justifiant chaque étape.",
            "Indique les actions que tu t'interdis à ce stade.",
        ),
        criteria=(
            _c("Hypothèse liée au changement", 1, "Une mise à jour du firmware remet souvent les réglages par défaut : mode de démarrage (UEFI/CSM), ordre de démarrage, entrée « Windows Boot Manager » à resélectionner, mode du contrôleur de stockage."),
            _c("Vérifications dans le firmware", 1.5, "Le disque NVMe est-il détecté ? Mode UEFI (Windows 11 démarre en UEFI sur disque GPT) ; Windows Boot Manager en tête de l'ordre de démarrage ; mode du contrôleur inchangé ; enregistrer et redémarrer."),
            _c("Étapes suivantes", 1, "Si le disque est vu mais que le démarrage échoue : environnement de récupération (réparation du démarrage) ; si le disque n'est pas vu : PC débranché, contrôle du montage du NVMe (PR06)."),
            _c("Interdits", 0.5, "Ni réinstallation, ni formatage, ni commande modifiant le démarrage avant ces vérifications ; données à protéger (sauvegarde d'une semaine : à compléter si possible)."),
        ),
        correction=(
            "Le seul changement est la mise à jour du firmware : elle remet souvent les réglages par défaut. L'hypothèse la plus probable est donc un réglage de démarrage perdu, pas une panne du disque.",
            "1. Entrer dans le firmware et vérifier que le disque NVMe est détecté : s'il l'est, le matériel répond. 2. Vérifier le mode de démarrage : Windows 11 démarre en UEFI sur un disque GPT ; si le firmware est passé en mode hérité (CSM/Legacy), il ne trouve pas de chargeur. 3. Placer « Windows Boot Manager » en tête de l'ordre de démarrage. 4. Vérifier que le mode du contrôleur de stockage (AHCI, RAID/VMD) n'a pas changé. Enregistrer et redémarrer.",
            "Si le disque est vu et réglé mais que le démarrage échoue encore : environnement de récupération (réparation du démarrage). S'il n'est pas vu : PC débranché, contrôler le montage du disque (voir PR06).",
            "Interdits à ce stade : réinstaller, formater, lancer des commandes qui réécrivent le démarrage. La comptabilité de la dernière semaine n'est pas sauvegardée : elle doit être protégée avant toute action lourde.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="« grub rescue> » après un nettoyage de partitions",
        question_type="long_answer",
        requirement_ids=("AP-09", "AP-13", "AP-C03"),
        kind=KIND_PROCEDURE,
        context=(
            "Un étudiant a un PC à double démarrage Windows/Linux (Ubuntu). Pour « gagner de la "
            "place », il a supprimé depuis la Gestion des disques de Windows une partition sans "
            "lettre qu'il pensait inutile. Au redémarrage : « error: no such partition. Entering "
            "rescue mode... grub rescue> ». Ses cours sont dans son dossier personnel Linux, "
            "sans sauvegarde."
        ),
        instructions=(
            "Interprète le message et indique ce qui a probablement été supprimé.",
            "Rédige une procédure prudente et ordonnée jusqu'à la validation, en signalant les étapes qui modifient le disque.",
        ),
        criteria=(
            _c("Interprétation", 1, "GRUB démarre mais ne trouve plus la partition qui contient ses fichiers (ou le système Linux) : la partition supprimée était probablement la partition Linux ou /boot."),
            _c("Données d'abord", 1, "Démarrer sur une clé Linux live, identifier les partitions restantes (lsblk, sans rien modifier), copier ce qui est encore accessible ; une partition supprimée peut parfois être récupérée par un outil spécialisé, à condition de ne rien écrire sur le disque avant."),
            _c("Procédure ordonnée", 1, "Clé live → lecture seule (lsblk, état des partitions) → sauvegarde → selon le cas : récupération de la partition par un spécialiste ou réinstallation de GRUB / de Linux, étapes signalées comme modifiant le disque, avec accord."),
            _c("Validation", 0.5, "Les deux systèmes démarrent depuis le menu, les données sont retrouvées ; conseil de sauvegarde et de ne pas supprimer une partition sans lettre."),
        ),
        correction=(
            "« no such partition » suivi de « grub rescue> » signifie que le chargeur GRUB s'est lancé mais ne trouve plus la partition qui contient ses fichiers ou le système Linux. La partition « sans lettre » supprimée dans Windows était très probablement la partition Linux : Windows n'attribue pas de lettre aux partitions ext4.",
            "1. Ne plus rien écrire sur ce disque. 2. Démarrer sur une clé Linux live et lister les partitions en lecture seule (lsblk). 3. Copier sur un support externe tout ce qui est encore accessible. 4. Une partition supprimée n'est pas forcément effacée : un outil de récupération des partitions, utilisé par une personne compétente, peut parfois la restaurer — c'est une opération qui modifie la table de partitions, à faire avec l'accord de l'étudiant.",
            "5. Si la partition est récupérée : réinstaller GRUB depuis la clé live (modifie le démarrage). Sinon : réinstaller Linux puis restaurer ce qui a pu être sauvé (modifie le disque).",
            "Validation : le menu de démarrage propose Windows et Linux, les deux démarrent, les cours sont retrouvés. Conseils : sauvegarde régulière, ne jamais supprimer une partition dont on ignore le rôle.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Windows Update échoue avec 0x80070070",
        question_type="long_answer",
        requirement_ids=("AP-09", "AP-13", "AP-15"),
        kind=KIND_PROCEDURE,
        context=(
            "Le PC portable d'une association (SSD de 128 Go) n'arrive plus à installer la mise "
            "à jour cumulative du mois : « Échec de l'installation — 0x80070070 ». Le journal "
            "WindowsUpdateClient indique le même code. La bénévole qui l'utilise stocke ses "
            "photos d'événements sur le bureau."
        ),
        instructions=(
            "Explique ce que le code indique et comment le confirmer.",
            "Rédige la procédure ordonnée jusqu'à la validation, sans supprimer de données personnelles sans accord.",
        ),
        criteria=(
            _c("Code", 1, "0x80070070 correspond à une erreur Windows « espace disque insuffisant » : la mise à jour n'a pas la place de se télécharger et de s'installer."),
            _c("Confirmation", 0.75, "Explorateur ou Paramètres > Stockage : espace libre de C: très faible ; identifier ce qui occupe la place."),
            _c("Procédure", 1.5, "Nettoyage des fichiers temporaires et des fichiers de mise à jour (Paramètres > Stockage, Nettoyage de disque) ; photos déplacées vers un support externe ou le cloud de l'association avec l'accord de la bénévole ; vider la corbeille avec accord ; relancer Windows Update."),
            _c("Validation", 0.75, "Mise à jour installée, historique sans échec, espace libre suffisant ; conseil : stockage des photos hors du disque système, nettoyage automatique (Assistant Stockage)."),
        ),
        correction=(
            "Le code 0x80070070 est l'erreur Windows « espace disque insuffisant » présentée sous forme de code de mise à jour : la mise à jour n'a pas la place de se télécharger et de s'installer. On le confirme dans Paramètres > Système > Stockage : C: est presque plein.",
            "1. Voir ce qui occupe la place (Paramètres > Stockage). 2. Supprimer les fichiers temporaires et les anciens fichiers de mise à jour (Stockage > Fichiers temporaires, ou Nettoyage de disque, option « Nettoyer les fichiers système »). 3. Avec l'accord de la bénévole, déplacer les photos vers un disque externe ou le stockage en ligne de l'association, en vérifiant la copie avant d'effacer l'original. 4. Vider la corbeille seulement avec son accord. 5. Relancer Windows Update.",
            "Validation : la mise à jour s'installe, l'historique ne montre plus d'échec et il reste un espace libre confortable. Conseil : stocker les photos ailleurs que sur le disque système et activer l'Assistant Stockage.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Événements « bad block » : chkdsk, mais pas n'importe comment",
        question_type="long_answer",
        requirement_ids=("AP-13", "AP-15", "AP-C03"),
        kind=KIND_PROCEDURE,
        context=(
            "Le PC d'un architecte se fige quelques secondes lors de l'ouverture de gros plans. "
            "Le journal Système contient plusieurs événements « disk », ID 7 : « Le périphérique "
            "\\Device\\Harddisk1\\DR1 a un bloc défectueux. » Le disque 1 est un disque dur "
            "mécanique de 2 To qui contient les archives des projets. Un forum conseille "
            "« chkdsk /r tout de suite »."
        ),
        instructions=(
            "Explique ce que l'événement indique et pourquoi chkdsk /r ne doit pas être la première action.",
            "Rédige la procédure ordonnée, en précisant le rôle de chkdsk sans paramètre, avec /f et avec /r.",
        ),
        criteria=(
            _c("Interprétation", 0.75, "Le disque 1 signale des secteurs illisibles : signe d'usure ou de panne qui peut s'aggraver ; les archives sont en danger."),
            _c("Données d'abord", 1, "Copier ou cloner les archives vers un support sain avant toute réparation ; si le disque fait des bruits ou se dégrade vite : arrêt et spécialiste."),
            _c("Rôle de chkdsk", 1.5, "Sans paramètre : vérification en lecture seule, rapport ; /f : corrige les erreurs du système de fichiers (volume verrouillé, éventuellement au redémarrage) ; /r : /f + recherche des secteurs défectueux et récupération des données lisibles, très long et très sollicitant pour un disque fragile."),
            _c("Suite", 0.75, "État SMART du disque ; après sauvegarde, remplacement du disque conseillé plutôt que réparation ; validation : archives accessibles sur le nouveau support, plus d'événement 7."),
        ),
        correction=(
            "L'événement disk 7 indique que le disque 1 contient des secteurs qu'il n'arrive plus à lire. C'est un signe d'usure ou de panne qui peut s'aggraver : les archives des projets sont en danger.",
            "chkdsk /r lit toute la surface du disque (des heures sur 2 To) et tente de déplacer les données des secteurs défectueux : sur un disque fragile, ce stress peut accélérer la panne, avant même que les archives soient sauvées. La sauvegarde passe donc en premier.",
            "Procédure : 1) copier les archives (ou cloner le disque avec un outil qui gère les erreurs de lecture) vers un support sain ; 2) relever l'état SMART du disque ; 3) chkdsk sans paramètre : vérification en lecture seule, qui ne modifie rien ; 4) si nécessaire et après la sauvegarde, chkdsk /f (corrige le système de fichiers, demande de verrouiller le volume) ou /r (inclut /f et recherche les secteurs défectueux, très long) ; 5) remplacer le disque, recommandé dès que des secteurs défectueux apparaissent.",
            "Validation : archives ouvertes depuis le nouveau support, plus aucun événement 7, ouverture des plans sans blocage.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Adresse en 169.254 : un poste ou tous les postes ?",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-37", "AP-15"),
        kind=KIND_CROSS,
        context=(
            "Dans une agence de voyage, le PC de l'accueil affiche « Aucun accès à Internet ». "
            "Les quatre autres postes, branchés sur le même switch, fonctionnent. Tu as relevé "
            "le document 1 sur le PC de l'accueil."
        ),
        instructions=(
            "Interprète l'adresse obtenue et ce qu'elle exclut ou non.",
            "Classe tes tests du plus simple au plus lourd, en séparant couche physique, configuration du poste et serveur DHCP.",
        ),
        documents=(
            _console(
                "Document 1 — ipconfig /all, extrait (fictif)",
                "Carte Ethernet Ethernet :",
                "   Description. . . . . . . . . . . . . . : Contrôleur Ethernet (fictif)",
                "   DHCP activé. . . . . . . . . . . . . . : Oui",
                "   Adresse d'autoconfiguration IPv4 . . . : 169.254.23.7(préféré)",
                "   Masque de sous-réseau. . . . . . . . . : 255.255.0.0",
                "   Passerelle par défaut. . . . . . . . . :",
            ),
        ),
        criteria=(
            _c("Interprétation", 1, "169.254.x.x/16 = adresse APIPA que Windows s'attribue quand aucun serveur DHCP n'a répondu ; le câble est vu comme branché (sinon « Média déconnecté »), mais aucun échange DHCP n'a abouti ; pas de passerelle, donc pas d'Internet."),
            _c("Périmètre", 0.75, "Un seul poste touché, les autres obtiennent leur adresse : le serveur DHCP fonctionne a priori ; la cause est plutôt entre ce poste et le switch, ou sur le poste."),
            _c("Tests ordonnés", 1.5, "Physique : câble et voyants, autre câble, autre port du switch ; poste : carte activée, pilote (Gestionnaire de périphériques), ipconfig /release puis /renew ; DHCP : plage d'adresses épuisée, filtrage d'adresses MAC, journal du routeur."),
            _c("Validation", 0.75, "Adresse dans la plage du réseau avec passerelle, ping de la passerelle puis d'un site par son nom."),
        ),
        correction=(
            "Une adresse 169.254.x.x avec le masque 255.255.0.0 est une adresse APIPA : Windows se l'attribue lui-même quand il n'a reçu aucune réponse d'un serveur DHCP. La carte est vue comme connectée (sinon ipconfig afficherait « Média déconnecté »), mais l'échange DHCP n'a pas abouti. Sans passerelle, aucun accès à Internet.",
            "Les quatre autres postes obtiennent une adresse : le serveur DHCP fonctionne a priori. La panne est plutôt entre ce poste et le switch, ou sur le poste lui-même.",
            "Tests : 1) physique : voyants de la prise et du port, autre câble, autre port du switch ; 2) poste : carte activée, pilote sans erreur dans le Gestionnaire de périphériques, puis ipconfig /release et ipconfig /renew (ces deux commandes modifient la configuration en cours, sans risque pour les données) ; 3) DHCP : plage d'adresses épuisée, filtrage des adresses MAC, journal du routeur.",
            "Validation : le poste reçoit une adresse du réseau de l'agence avec une passerelle, le ping de la passerelle répond, puis un site s'ouvre par son nom.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Imprimante « hors ligne » pour tout le monde",
        question_type="long_answer",
        requirement_ids=("AP-13", "AP-25", "AP-37"),
        kind=KIND_CROSS,
        context=(
            "Dans un cabinet d'avocats, l'imprimante réseau apparaît « Hors ligne » sur les six "
            "postes Windows depuis lundi. Le week-end, le fournisseur d'accès a remplacé la box "
            "(routeur) ; l'imprimante était installée sur les postes par son adresse IP "
            "192.168.1.50. Son écran affiche « Prête ». Le nouveau réseau distribue des adresses "
            "192.168.0.x."
        ),
        instructions=(
            "Formule l'hypothèse principale et explique pourquoi elle est plus probable qu'un problème de pilote.",
            "Décris les tests qui la confirment, la correction durable et la validation.",
        ),
        criteria=(
            _c("Hypothèse", 1.25, "Tous les postes sont touchés en même temps, juste après le changement de box : l'imprimante a changé d'adresse (ou est sur l'ancienne plage) ; les postes cherchent toujours 192.168.1.50 ; un pilote ne tomberait pas en panne sur six postes à la fois."),
            _c("Tests", 1.25, "Lire l'adresse actuelle sur l'écran ou la page de configuration de l'imprimante ; ping de cette adresse et de l'ancienne depuis un poste ; liste des appareils de la nouvelle box."),
            _c("Correction durable", 1, "Réservation DHCP (ou adresse fixe hors de la plage DHCP) pour l'imprimante, puis mise à jour du port de l'imprimante sur les postes."),
            _c("Validation", 0.5, "Page de test depuis plusieurs postes, état « Prête » partout ; adresse notée dans la documentation."),
        ),
        correction=(
            "Les six postes sont touchés en même temps, juste après le remplacement de la box, et l'imprimante est « Prête » : c'est la liaison réseau qui a changé. Le nouveau réseau est en 192.168.0.x ; l'imprimante a reçu une nouvelle adresse (ou garde une adresse de l'ancien réseau), alors que les postes cherchent toujours 192.168.1.50. Un pilote ne tomberait pas en panne sur six postes à la fois.",
            "Tests : lire l'adresse actuelle sur l'écran ou la page de configuration de l'imprimante ; depuis un poste, ping de l'ancienne adresse (pas de réponse) et de la nouvelle (réponse) ; vérifier la liste des appareils connectés à la box.",
            "Correction durable : réservation DHCP sur la box (ou adresse fixe hors de la plage distribuée) pour l'imprimante, puis mise à jour du port de l'imprimante (Propriétés de l'imprimante > Ports) sur chaque poste, ou réinstallation par la nouvelle adresse.",
            "Validation : page de test imprimée depuis plusieurs postes, état « Prête » partout ; nouvelle adresse notée dans la documentation du cabinet.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Gels intermittents : bâtir une chronologie",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-15", "AP-C01"),
        kind=KIND_CROSS,
        context=(
            "Le PC d'une graphiste se fige parfois une dizaine de secondes, puis repart. Elle "
            "pense à un virus. Tu as rassemblé ses notes et les événements correspondants "
            "(document 1)."
        ),
        instructions=(
            "Indique les éléments qui se répètent et ceux qui ne sont que des coïncidences.",
            "Propose l'hypothèse principale, les tests qui la confirment et la priorité de l'intervention.",
        ),
        documents=(
            _table(
                "Document 1 — Chronologie des gels (fictive)",
                ("Date et heure", "Ce que faisait la graphiste", "Événement Système au même moment", "Autre fait noté"),
                ("lun. 09:12", "Ouverture d'un dossier de photos sur D:", "disk, ID 153 : nouvelle tentative d'E/S sur le disque 1", "Antivirus à jour"),
                ("mar. 14:40", "Export d'une affiche sur D:", "disk, ID 153 : nouvelle tentative d'E/S sur le disque 1", "Pluie, orage"),
                ("mer. 10:05", "Navigation Internet seule", "aucun", "Mise à jour du navigateur"),
                ("jeu. 16:22", "Copie de photos sur D:", "disk, ID 153 puis disk, ID 7 (bloc défectueux) sur le disque 1", "Nouvelle souris"),
            ),
        ),
        criteria=(
            _c("Répétition et coïncidences", 1, "Trois gels sur quatre pendant un accès à D: (disque 1), chaque fois avec des événements disk sur le disque 1 ; orage, souris, navigateur et antivirus : coïncidences sans répétition ; le gel de mercredi n'a pas d'événement et reste à expliquer."),
            _c("Hypothèse", 1, "Disque 1 (D:) défaillant : nouvelles tentatives d'entrées/sorties puis bloc défectueux ; pas d'indice de virus."),
            _c("Tests", 1, "État SMART du disque 1 ; reproduire en lisant de gros fichiers sur D: en surveillant le journal ; vérifier le câble SATA (PC débranché) ; le gel de mercredi reste ouvert (autre cause possible)."),
            _c("Priorité", 1, "Sauvegarder immédiatement les données de D: avant tout test lourd ; remplacement du disque ensuite si l'hypothèse est confirmée."),
        ),
        correction=(
            "Ce qui se répète : trois gels sur quatre ont lieu pendant un accès au disque D:, et chaque fois le journal contient un événement disk sur le disque 1 (ID 153, nouvelle tentative d'entrée/sortie, puis ID 7, bloc défectueux). L'orage, la souris, le navigateur et l'antivirus n'apparaissent qu'une fois : ce sont des coïncidences. Le gel de mercredi, sans événement, reste à expliquer : on ne l'attribue pas d'office au disque.",
            "Hypothèse principale : le disque 1 (D:) devient défaillant ; ses lectures lentes et ses nouvelles tentatives bloquent le système quelques secondes. Rien n'oriente vers un virus.",
            "Tests : état SMART du disque 1 ; reproduire le gel en lisant de gros fichiers sur D: tout en surveillant le journal ; PC débranché, contrôler le câble SATA du disque.",
            "Priorité : sauvegarder tout de suite les données de D:, avant tout test lourd ; si l'hypothèse est confirmée, remplacer le disque et restaurer les données.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Linux passe en lecture seule",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-15", "AP-C03"),
        kind=KIND_CROSS,
        context=(
            "Sur le PC Linux (Ubuntu) d'une bibliothèque, plus aucun fichier ne peut être "
            "enregistré depuis ce matin, sur aucun compte. Un collègue veut lancer « fsck tout de "
            "suite, le système démarré ». Tu as relevé le document 1."
        ),
        instructions=(
            "Explique l'enchaînement des messages : qui a mis le système en lecture seule, et pourquoi.",
            "Indique pourquoi la proposition du collègue est dangereuse et rédige la démarche correcte.",
        ),
        documents=(
            _console(
                "Document 1 — Relevé (extrait fictif)",
                "$ touch essai.txt",
                "touch: cannot touch 'essai.txt': Read-only file system",
                "$ sudo dmesg -T | grep -i -e ext4 -e 'I/O error' | tail -3",
                "[Tue Mar 10 08:57:31 2026] I/O error, dev sda, sector 81920136 op 0x0:(READ) flags 0x0",
                "[Tue Mar 10 08:57:31 2026] EXT4-fs error (device sda2): ext4_find_entry:1658: inode #2: comm ls: reading directory lblock 0",
                "[Tue Mar 10 08:57:31 2026] EXT4-fs (sda2): Remounting filesystem read-only",
            ),
        ),
        criteria=(
            _c("Enchaînement", 1.25, "Erreur de lecture matérielle sur le disque sda, puis erreur du système de fichiers ext4 sur sda2 ; le noyau remonte la partition en lecture seule pour la protéger (option errors=remount-ro) ; ce n'est pas un problème de droits."),
            _c("Danger de la proposition", 1, "fsck ne doit jamais réparer un système de fichiers monté : risque de corruption grave ; de plus, avec des erreurs d'entrée/sortie, le disque lui-même est suspect."),
            _c("Démarche", 1.25, "Copier les données encore lisibles ; vérifier l'état SMART du disque ; démarrer sur un support externe pour que la partition soit démontée, puis fsck seulement après sauvegarde ; remplacer le disque si les erreurs matérielles se confirment."),
            _c("Validation", 0.5, "Système monté en lecture-écriture, plus d'erreur dans dmesg, enregistrement possible ; disque surveillé ou remplacé."),
        ),
        correction=(
            "La première ligne de dmesg est une erreur d'entrée/sortie matérielle : le disque sda n'a pas réussi à lire un secteur. Le système de fichiers ext4 de sda2 rencontre alors une erreur, et le noyau remonte la partition en lecture seule pour éviter de l'abîmer davantage (c'est l'option errors=remount-ro, courante sur Ubuntu). Ce n'est donc pas un problème de droits.",
            "Lancer fsck pour réparer un système de fichiers monté peut le corrompre gravement. Et comme le disque produit des erreurs d'entrée/sortie, c'est aussi le matériel qui est suspect : une réparation intensive peut aggraver la panne.",
            "Démarche : 1) copier les données encore lisibles vers un support sain ; 2) relever l'état SMART du disque ; 3) démarrer sur une clé live pour que la partition soit démontée, puis seulement lancer fsck, après la sauvegarde ; 4) remplacer le disque si les erreurs matérielles se confirment.",
            "Validation : la partition est montée en lecture-écriture, dmesg ne montre plus d'erreur, les enregistrements fonctionnent ; le disque est remplacé ou surveillé.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions × 2 points (onglet « Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Clone vers SSD : « Operating system not found »",
        question_type="short_answer",
        requirement_ids=("AP-09", "AP-13"),
        kind=KIND_SCENARIO,
        context=(
            "Un technicien a cloné l'ancien disque dur d'un PC Windows 10 (table de partitions "
            "MBR, démarrage en mode hérité) vers un SSD neuf. Pendant l'opération, il a remis le "
            "firmware « à zéro » : il est maintenant en mode UEFI seul, CSM désactivé. Au "
            "démarrage : « Operating system not found ». Le firmware détecte bien le SSD."
        ),
        instructions=(
            "Explique la cause la plus probable et propose deux solutions, en précisant celle qui modifie le disque et sa précaution.",
        ),
        criteria=(
            _c("Cause", 0.8, "Disque MBR prévu pour un démarrage hérité, firmware en UEFI seul : le firmware cherche une partition EFI (disque GPT) et ne trouve pas de chargeur."),
            _c("Solution réversible", 0.6, "Réactiver le mode hérité (CSM/Legacy) dans le firmware : aucun changement sur le disque."),
            _c("Solution qui modifie le disque", 0.6, "Convertir le disque en GPT (par exemple avec l'outil MBR2GPT de Windows, après sa validation) puis démarrer en UEFI : sauvegarde préalable obligatoire."),
        ),
        correction=(
            "Le disque cloné est en MBR et prévu pour un démarrage hérité ; le firmware, en UEFI seul, cherche un chargeur dans une partition EFI d'un disque GPT et n'en trouve pas.",
            "Solution 1, réversible : réactiver le CSM (mode hérité) dans le firmware. Solution 2 : convertir le disque en GPT (MBR2GPT, après sa vérification /validate) puis démarrer en UEFI ; elle modifie la table de partitions, donc sauvegarde préalable obligatoire.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Écrans bleus après ajout de mémoire",
        question_type="short_answer",
        requirement_ids=("AP-09", "AP-15"),
        kind=KIND_SCENARIO,
        context=(
            "Depuis qu'un client a ajouté lui-même une barrette de 8 Go à son PC (qui en avait "
            "déjà une de 8 Go), Windows affiche plusieurs fois par jour des écrans bleus aux "
            "codes différents : PAGE_FAULT_IN_NONPAGED_AREA, puis MEMORY_MANAGEMENT. Aucun autre "
            "changement n'a été fait."
        ),
        instructions=(
            "Donne ton hypothèse principale en t'appuyant sur les codes et la chronologie, puis la procédure de test qui la confirme.",
        ),
        criteria=(
            _c("Hypothèse", 0.8, "Mémoire : nouvelle barrette défectueuse ou incompatible avec la première (fréquence, tension, profil) ; des codes variés liés à la mémoire juste après un ajout de RAM vont dans ce sens, sans être une preuve."),
            _c("Procédure", 1.2, "Test mémoire hors système (plusieurs passes) ; retirer la nouvelle barrette et observer ; tester chaque barrette seule ; vérifier la compatibilité (manuel de la carte mère) ; réglages mémoire par défaut ; PC débranché et ESD à chaque manipulation."),
        ),
        correction=(
            "Les codes changent mais concernent tous la mémoire, et ils apparaissent juste après l'ajout d'une barrette : l'hypothèse principale est une barrette défectueuse ou incompatible avec la première (fréquence, tension, profil).",
            "Test : test mémoire hors système en plusieurs passes ; puis retirer la nouvelle barrette et observer ; tester chaque barrette seule ; vérifier dans le manuel de la carte mère la compatibilité ; laisser les réglages mémoire par défaut. PC débranché et protection ESD à chaque manipulation.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Webcam en Code 10 après une mise à jour",
        question_type="short_answer",
        requirement_ids=("AP-09", "AP-05"),
        kind=KIND_SCENARIO,
        context=(
            "Depuis la dernière mise à jour de Windows, la webcam intégrée d'un PC portable d'un "
            "télétravailleur n'apparaît plus dans ses visioconférences. Dans le Gestionnaire de "
            "périphériques, elle porte un triangle jaune et l'état « Ce périphérique ne peut pas "
            "démarrer. (Code 10) ». La date du pilote a changé le jour de la mise à jour."
        ),
        instructions=(
            "Indique ce que le code et la date du pilote t'apprennent, puis les actions ordonnées, de la plus réversible à la plus lourde, et la validation.",
        ),
        criteria=(
            _c("Interprétation", 0.6, "Le pilote ne parvient pas à démarrer le périphérique ; la date du pilote montre qu'il a été remplacé par la mise à jour : hypothèse d'un pilote inadapté, pas encore une preuve."),
            _c("Actions ordonnées", 1, "Restaurer le pilote précédent ; sinon pilote du fabricant du portable ; sinon désinstaller le périphérique et redémarrer ; vérifier aussi qu'un interrupteur ou un réglage de confidentialité ne bloque pas la caméra."),
            _c("Validation", 0.4, "État « fonctionne correctement », image dans l'application de caméra puis dans la visioconférence."),
        ),
        correction=(
            "Le code 10 indique que le pilote n'arrive pas à démarrer le périphérique ; la date du pilote montre qu'il a été remplacé lors de la mise à jour. L'hypothèse est un pilote inadapté — à confirmer.",
            "Actions : 1) Restaurer le pilote précédent ; 2) sinon, installer le pilote du fabricant du portable ; 3) sinon, désinstaller le périphérique et redémarrer pour qu'il soit redétecté. Vérifier aussi l'interrupteur ou le cache de la caméra et les paramètres de confidentialité. Validation : état « Ce périphérique fonctionne correctement » et image dans l'application Caméra puis dans la visioconférence.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Service de sauvegarde qui ne démarre plus",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-13"),
        kind=KIND_ANALYSIS,
        context=(
            "Dans une PME, le logiciel de sauvegarde d'un serveur Windows signale « service "
            "injoignable » depuis un changement de mot de passe du compte « svc-sauvegarde » "
            "vendredi. Le document 1 est un extrait du journal Système de lundi."
        ),
        instructions=(
            "Explique la cause à partir du document et décris la correction, puis la vérification.",
        ),
        documents=(
            _table(
                "Document 1 — Journal Système, lundi (fictif)",
                ("Niveau", "Heure", "Source", "ID", "Message"),
                ("Erreur", "07:00:12", "Service Control Manager", "7038", "Le service Agent Sauvegarde n'a pas pu ouvrir de session en tant que .\\svc-sauvegarde avec le mot de passe actuellement configuré (nom d'utilisateur ou mot de passe incorrect)."),
                ("Erreur", "07:00:12", "Service Control Manager", "7000", "Le service Agent Sauvegarde n'a pas pu démarrer en raison de l'erreur : le service n'a pas démarré en raison d'un échec de l'ouverture de session."),
            ),
        ),
        criteria=(
            _c("Cause", 0.8, "Le service démarre sous le compte svc-sauvegarde dont le mot de passe a changé vendredi ; le service garde l'ancien : échec d'ouverture de session (7038) puis échec de démarrage (7000)."),
            _c("Correction", 0.8, "services.msc > Propriétés du service > Connexion : saisir le nouveau mot de passe (ou utiliser un compte de service géré) ; démarrer le service ; type de démarrage Automatique."),
            _c("Vérification", 0.4, "Statut « En cours d'exécution », plus d'erreur 7038/7000, sauvegarde de test réussie."),
        ),
        correction=(
            "Le service « Agent Sauvegarde » ouvre une session sous le compte svc-sauvegarde. Son mot de passe a changé vendredi, mais le service a gardé l'ancien : l'ouverture de session échoue (7038), donc le démarrage aussi (7000).",
            "Correction : services.msc > Agent Sauvegarde > Propriétés > onglet Connexion, saisir le nouveau mot de passe ; démarrer le service et vérifier son type de démarrage (Automatique). Vérification : statut « En cours d'exécution », plus d'erreur 7038 ni 7000 au redémarrage suivant, sauvegarde de test réussie.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Mode d'urgence après le retrait d'un disque USB",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-13"),
        kind=KIND_ANALYSIS,
        context=(
            "Un mini-PC Linux (Debian) de vidéosurveillance enregistrait sur un disque USB monté "
            "automatiquement au démarrage par /etc/fstab. Le disque a été emporté pour être "
            "analysé. Depuis, le mini-PC ne démarre plus normalement (document 1)."
        ),
        instructions=(
            "Explique le blocage et propose une correction qui permette au mini-PC de démarrer, avec ou sans le disque, puis la validation.",
        ),
        documents=(
            _console(
                "Document 1 — Écran de démarrage (extrait fictif)",
                "[ TIME ] Timed out waiting for device dev-disk-by\\x2dlabel-VIDEOS.device.",
                "[DEPEND] Dependency failed for /mnt/videos.",
                "[DEPEND] Dependency failed for Local File Systems.",
                "You are in emergency mode. After logging in, type \"journalctl -xb\" to view",
                "system logs, \"systemctl reboot\" to reboot, \"systemctl default\" or \"exit\"",
                "to boot into default mode.",
            ),
        ),
        criteria=(
            _c("Explication", 0.8, "fstab exige le disque d'étiquette VIDEOS ; absent, le délai expire, le montage échoue et la cible Local File Systems échoue par dépendance : mode d'urgence."),
            _c("Correction", 0.8, "Après copie de /etc/fstab, ajouter l'option nofail (éventuellement x-systemd.device-timeout court) à la ligne /mnt/videos, ou la commenter tant que le disque est absent ; contrôle par mount -a ou findmnt --verify."),
            _c("Validation", 0.4, "Démarrage normal sans le disque ; disque rebranché : monté sur /mnt/videos, enregistrement repris."),
        ),
        correction=(
            "La ligne /mnt/videos de /etc/fstab exige le disque d'étiquette VIDEOS. Il est absent : le délai expire, le montage échoue, la cible Local File Systems échoue à son tour, et systemd passe en mode d'urgence.",
            "Correction : copier /etc/fstab, puis ajouter l'option nofail à la ligne (avec éventuellement un délai court x-systemd.device-timeout), ou la mettre en commentaire tant que le disque n'est pas revenu ; vérifier avec mount -a ou findmnt --verify. Validation : démarrage normal sans le disque ; disque rebranché, il est monté sur /mnt/videos et l'enregistrement reprend.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Script refusé : « Permission denied »",
        question_type="short_answer",
        requirement_ids=("AP-13", "AP-27"),
        kind=KIND_SCENARIO,
        context=(
            "Un administrateur a copié depuis une clé USB un script de sauvegarde sur un serveur "
            "Linux. En le lançant (./sauvegarde.sh), il obtient « bash: ./sauvegarde.sh: "
            "Permission denied ». ls -l affiche « -rw-r--r-- 1 admin admin 812 … sauvegarde.sh ». "
            "Un collègue lui dit de faire « chmod 777 sauvegarde.sh »."
        ),
        instructions=(
            "Explique la cause à partir des droits affichés et donne la correction adaptée, en justifiant pourquoi tu refuses la proposition du collègue.",
        ),
        criteria=(
            _c("Cause", 0.8, "Aucun droit d'exécution (x) n'est présent : rw- pour le propriétaire, r-- pour le groupe et les autres ; le shell refuse de lancer le fichier."),
            _c("Correction", 0.6, "Ajouter seulement l'exécution pour le propriétaire (chmod u+x sauvegarde.sh, ou 744 / 700 selon le besoin) après avoir lu le script, puis le relancer."),
            _c("Refus de 777", 0.6, "777 permet à tout compte de modifier le script ; s'il est exécuté avec des droits élevés, c'est une faille grave."),
        ),
        correction=(
            "Les droits -rw-r--r-- ne contiennent aucun x : personne n'a le droit d'exécuter ce fichier, d'où « Permission denied ».",
            "Correction : après avoir relu le script, ajouter uniquement l'exécution pour son propriétaire (chmod u+x sauvegarde.sh), puis le relancer. chmod 777 donnerait aussi l'écriture à tous les comptes : n'importe qui pourrait modifier un script de sauvegarde, souvent lancé avec des droits élevés — une faille grave.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Espace non libéré après suppression",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-15"),
        kind=KIND_ANALYSIS,
        context=(
            "Sur un serveur Linux, /var était plein (« No space left on device »). Un collègue a "
            "supprimé un journal de 20 Go (/var/log/app/app.log) écrit par l'application "
            "« app », toujours en marche. Pourtant, df indique toujours 100 % (document 1)."
        ),
        instructions=(
            "Explique pourquoi l'espace n'est pas revenu et comment le récupérer proprement, puis comment éviter que cela se reproduise.",
        ),
        documents=(
            _console(
                "Document 1 — Relevé (extrait fictif)",
                "$ df -h /var",
                "Filesystem      Size  Used Avail Use% Mounted on",
                "/dev/sda3        30G   29G     0 100% /var",
                "$ sudo lsof +L1 | grep app.log",
                "app  1342 app  3w  REG  8,3 21474836480  0 4194 /var/log/app/app.log (deleted)",
            ),
        ),
        criteria=(
            _c("Explication", 0.8, "Le fichier est supprimé du dossier mais encore ouvert en écriture par le processus app (lsof +L1 : « (deleted) ») : l'espace n'est libéré qu'à sa fermeture."),
            _c("Récupération", 0.7, "Redémarrer ou recharger proprement le service app (avec accord, à un moment acceptable) pour qu'il ferme le fichier ; vérifier ensuite df -h."),
            _c("Prévention", 0.5, "Rotation des journaux (logrotate) et surveillance de l'espace ; à l'avenir, vider un journal ouvert plutôt que le supprimer, après accord."),
        ),
        correction=(
            "Supprimer un fichier retire seulement son nom du dossier. Tant qu'un processus le garde ouvert, son contenu reste sur le disque : lsof +L1 le montre, marqué « (deleted) », ouvert en écriture par app (PID 1342). L'espace sera libéré à la fermeture du fichier.",
            "Récupération : redémarrer (ou recharger) proprement le service app, avec accord et à un moment où l'arrêt est acceptable, puis vérifier df -h. Prévention : rotation des journaux par logrotate, surveillance de l'espace libre ; à l'avenir, vider un journal ouvert plutôt que le supprimer.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Internet « en panne » : adresses oui, noms non",
        question_type="short_answer",
        requirement_ids=("AP-13", "AP-37"),
        kind=KIND_CROSS,
        context=(
            "Sur un PC Windows d'une boulangerie, aucun site ne s'ouvre. ipconfig montre une "
            "adresse 192.168.1.23 et la passerelle 192.168.1.1. ping 192.168.1.1 répond, ping "
            "8.8.8.8 répond, mais « ping www.exemple.be » affiche « La requête Ping n'a pas pu "
            "trouver l'hôte www.exemple.be. Vérifiez le nom et essayez à nouveau. »"
        ),
        instructions=(
            "Situe la panne en t'appuyant sur chaque test, puis indique les vérifications suivantes et la validation.",
        ),
        criteria=(
            _c("Situation de la panne", 1, "Adresse et passerelle correctes, réseau local et Internet joignables par adresse IP : couche physique, DHCP et routeur hors de cause ; seule la résolution des noms (DNS) échoue."),
            _c("Vérifications", 0.6, "Serveurs DNS affichés par ipconfig /all ; nslookup www.exemple.be ; DNS configuré à la main par erreur ou serveur DNS de la box en panne ; ipconfig /flushdns."),
            _c("Validation", 0.4, "nslookup renvoie une adresse, le site s'ouvre par son nom."),
        ),
        correction=(
            "L'adresse et la passerelle sont correctes ; le ping de la passerelle prouve le réseau local, celui de 8.8.8.8 prouve l'accès à Internet par adresse IP. Le câble, le DHCP et le routeur fonctionnent : seule la résolution des noms (DNS) échoue.",
            "Vérifications : serveurs DNS affichés par ipconfig /all (un DNS saisi à la main par erreur ?), nslookup www.exemple.be, état du DNS de la box ; vider le cache DNS (ipconfig /flushdns). Validation : nslookup renvoie une adresse et le site s'ouvre par son nom.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Profil temporaire à l'ouverture de session",
        question_type="short_answer",
        requirement_ids=("AP-09", "AP-13", "AP-C03"),
        kind=KIND_SCENARIO,
        context=(
            "Une secrétaire ouvre sa session Windows : le bureau est vide, et une notification "
            "indique « Vous êtes connecté avec un profil temporaire ». Le journal Application "
            "contient l'événement User Profile Service 1511 (« Windows ne trouve pas le profil "
            "local et vous connecte avec un profil temporaire »). Elle s'inquiète pour ses "
            "documents."
        ),
        instructions=(
            "Explique ce qui se passe, ce que tu dis à l'utilisatrice et la démarche prudente de correction.",
        ),
        criteria=(
            _c("Explication", 0.6, "Windows n'a pas pu charger le profil habituel et a créé un profil temporaire : ce qui est enregistré dans ce profil sera perdu à la déconnexion ; les documents du profil habituel sont en principe toujours dans C:\\Users\\<nom>."),
            _c("Consigne à l'utilisatrice", 0.5, "Ne rien enregistrer dans cette session et ne pas supprimer de dossier ; ses documents ne sont pas effacés."),
            _c("Démarche", 0.9, "Vérifier que le dossier du profil et les documents existent et les sauvegarder ; rechercher la cause (disque plein, erreurs de disque, fichier de profil corrompu) ; redémarrer une fois ; si le problème persiste, réparation du profil par un administrateur (ou nouveau profil et copie des données), après sauvegarde."),
        ),
        correction=(
            "Windows n'a pas pu charger le profil habituel de la secrétaire : il l'a connectée avec un profil temporaire, dont tout le contenu sera perdu à la déconnexion. Ses documents sont en principe toujours dans son dossier C:\\Users\\<nom>.",
            "À l'utilisatrice : « Vos documents ne sont pas effacés ; n'enregistrez rien dans cette session et ne supprimez rien. » Démarche : vérifier et sauvegarder le dossier du profil ; chercher la cause (disque plein, erreurs de disque, profil corrompu) ; redémarrer une fois ; si le problème persiste, un administrateur répare le profil, ou crée un nouveau profil et y copie les données, toujours après sauvegarde.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Rédiger le compte rendu d'une intervention",
        question_type="document_analysis",
        requirement_ids=("AP-13", "AP-C01"),
        kind=KIND_ANALYSIS,
        context=(
            "Tu viens de terminer une intervention pour le cabinet de kinésithérapie Dubois. Le "
            "document 1 rassemble tes notes brutes. Le responsable veut un compte rendu écrit "
            "qu'il pourra conserver."
        ),
        instructions=(
            "Rédige le compte rendu professionnel à partir des notes, en suivant les rubriques d'un rapport d'intervention.",
        ),
        documents=(
            _table(
                "Document 1 — Notes d'intervention (fictives)",
                ("Rubrique", "Note brute"),
                ("Demande", "Mardi 08:30, appel du responsable : le PC de l'accueil affiche un écran bleu au démarrage depuis ce matin."),
                ("Environnement", "PC de bureau Windows 11, agenda des patients en local, sauvegarde en ligne vérifiée la veille."),
                ("Symptôme et preuve", "Code d'arrêt INACCESSIBLE_BOOT_DEVICE à chaque démarrage, photo de l'écran prise."),
                ("Changement récent", "La veille au soir, un prestataire a « optimisé le BIOS » : mode du contrôleur SATA passé de AHCI à RAID."),
                ("Test", "Mode remis en AHCI dans le firmware (réglage réversible) : Windows démarre normalement."),
                ("Validation", "Trois redémarrages sans erreur, agenda des patients ouvert, impression d'un rendez-vous réussie."),
            ),
        ),
        criteria=(
            _c("Rubriques et faits", 0.8, "Demande, environnement, symptôme et preuve, cause retenue, action, validation présentes et fidèles aux notes, sans fait inventé."),
            _c("Lien cause → action", 0.6, "Cause : changement du mode du contrôleur de stockage (AHCI → RAID), le pilote de démarrage ne correspondait plus ; action : retour au réglage précédent, réversible, données préservées."),
            _c("Risque et recommandation", 0.6, "Ne pas modifier ce réglage sans préparation ; prévenir le prestataire ; garder la sauvegarde quotidienne ; clôture."),
        ),
        correction=(
            "Exemple de compte rendu : Demande : mardi 08:30, appel du responsable, écran bleu au démarrage du PC de l'accueil. Environnement : PC Windows 11, agenda des patients en local, sauvegarde en ligne vérifiée la veille. Symptôme et preuve : code d'arrêt INACCESSIBLE_BOOT_DEVICE à chaque démarrage (photo jointe).",
            "Cause retenue : la veille, le mode du contrôleur de stockage a été changé de AHCI à RAID dans le firmware ; Windows n'avait plus le pilote correspondant pour lire son disque au démarrage. Action : remise du mode AHCI (réglage réversible, aucune donnée touchée). Validation : trois redémarrages sans erreur, agenda ouvert, impression réussie.",
            "Risque résiduel et recommandation : ne plus modifier ce réglage sans préparer Windows ; informer le prestataire ; garder la sauvegarde quotidienne. Intervention clôturée.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
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
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

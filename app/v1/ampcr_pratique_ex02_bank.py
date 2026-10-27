"""EX02 « Examen blanc écrit — installation et dépannage des systèmes » — les 10 questions
notées /100 (ticket #231).

Épreuve autonome du module 2 (PR07 → PR12) : 10 questions de 10 points, **réponses libres**,
dans la réserve `exam` uniquement (`ampcr-pratique-ex02:exam`) — pas d'exercices
d'entraînement propres à EX02 : on s'entraîne dans les cours PR07 → PR12. Organisation :

- partie 1 (sans dossier) : choix du système, de l'édition et prérequis (X01), interface
  graphique, ligne de commande et service (X02) ;
- **dossier A** (bureau d'architectes Verhaegen, Windows) : installation propre sur un SSD
  neuf (X03), pilotes manquants (X04), comptes et groupe de travail (X05) ;
- **dossier B** (Repair Café « La Clé », Linux) : double démarrage (X06), mode d'urgence au
  démarrage (X07), permissions et sudo (X08) ;
- **dossier C** (agence immobilière Delvaux, Windows) : écran d'arrêt après une mise à jour
  de pilote (X09), sauvegarde vérifiée et choix de la restauration (X10).

Chaque question reprend les documents du dossier dont elle a besoin : elle se résout seule,
dans n'importe quel ordre. Valeurs et verdicts viennent de `app.v1.ampcr_pratique_ex02_figures`
(mêmes règles que les cours). Situations, références et relevés **fictifs** ; aucune question
n'est présentée comme officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex02_figures import (
    ACTIVATION,
    BACKUP_HASHES,
    BAD_COPIES,
    CREATED_PARTITIONS,
    CUPS_FIX,
    CUPS_SCREEN,
    DATA_UUID,
    DEVICE_VENDORS,
    DEVICES,
    DUAL_BOOT_RAM_GB,
    DUAL_BOOT_SWAP_GB,
    DUAL_BOOT_SWAP_HIBERNATION_GB,
    EMERGENCY_SCREEN,
    FAILED_DRIVER,
    FSTAB_BAD_LINE,
    FSTAB_FIXED_LINE,
    INSTALLER_FIGURE,
    INSTALLER_FIGURE_FILE,
    LICENCE_EDITION,
    LSBLK_SCREEN,
    NEW_DATA_NAME,
    OLD_DATA_NAME,
    PARTITIONS_FIGURE,
    PARTITIONS_FIGURE_FILE,
    PERMISSIONS_SCREEN,
    RESET_EFFECT,
    RESET_PRECAUTION,
    RESTORE_POINT_TO_USE,
    RESTORE_POINTS,
    SHARE_DIR_OCTAL,
    SHARE_FILE_FIXED_OCTAL,
    SHARE_FILE_OCTAL,
    SHARED_ACCOUNT_DECISION,
    STAFF,
    STATION_CHECKS,
    STATION_EDITIONS,
    STATIONS,
    STOP_CODE,
    STOP_FIGURE,
    STOP_FIGURE_FILE,
    TARGET_DISK,
    WINRE_SCREEN,
    station_rows,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item
from app.v1.ampcr_pratique_pr07_figures import W11_NO, W11_OK, W11_SETTINGS

EX02_CODE = "EX02"
EXAM_TOTAL_POINTS = 100
POINTS_PER_QUESTION = 10
KIND_DOC = "analyse de document"
KIND_CASE = "scénario"

# Partie ou dossier de chaque question (sujet imprimable, barème global).
PART_1 = "Partie 1 — Choix du système et outils"
DOSSIER_A = "Dossier A — Bureau d'architectes Verhaegen"
DOSSIER_B = "Dossier B — Repair Café « La Clé »"
DOSSIER_C = "Dossier C — Agence immobilière Delvaux"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


_S1, _S2, _S3 = (s.name for s in STATIONS)
assert STATION_CHECKS[_S1][0] == W11_SETTINGS and STATION_CHECKS[_S2][0] == W11_NO
assert STATION_CHECKS[_S3][0] == W11_OK


def _settings(name: str) -> str:
    return " ; ".join(STATION_CHECKS[name][2])


def _blockers(name: str) -> str:
    return " et ".join(STATION_CHECKS[name][1])


# --- Documents ---------------------------------------------------------------------------------

_P1_STATIONS = _table(
    "Document 1 — Relevé des trois postes (msinfo32, tpm.msc, Gestion des disques ; fictif)",
    ("Poste", "Processeur", "Mémoire", "Stockage", "Mode du firmware", "Démarrage sécurisé", "TPM", "Usage"),
    *station_rows(),
)
_P1_TASKS = _table(
    "Document 1 — Relevés demandés par le responsable de l'atelier",
    ("N°", "Relevé à faire sur un poste Windows 11 et sur un poste Ubuntu"),
    ("1", "Lister les disques et leurs partitions"),
    ("2", "Vérifier les pilotes des périphériques"),
    ("3", "Afficher la configuration réseau (adresse IP, passerelle, DNS)"),
    ("4", "Contrôler l'état d'un service et son lancement au démarrage"),
)
_P1_CUPS = _console("Document 2 — Poste Ubuntu de l'atelier : impression impossible (capture fictive)", *CUPS_SCREEN)

_A_REQUEST = _table(
    "Dossier A, document A1 — Fiche d'intervention",
    ("Rubrique", "Contenu"),
    ("Client", "Bureau d'architectes Verhaegen (5 personnes) ; gérante : Mme Anne Verhaegen"),
    ("Poste", "PC-DAO-01, tour de dessin assisté (DAO), Windows 10 Professionnel"),
    ("Demande", ("Installation propre de Windows 11 Professionnel sur un SSD NVMe de 1 To neuf, déjà monté. "
                 "L'ancien SSD SATA de 256 Go (Windows 10, lent, erreurs répétées) reste branché un mois, puis "
                 "sera effacé ; le disque dur de 2 To « PROJETS » est conservé tel quel.")),
    ("Licence", "Windows 10 Professionnel, licence numérique liée à ce PC (passage gratuit à Windows 11 Professionnel)"),
    ("Données", ("Projets sur le disque PROJETS, copiés chaque nuit sur le NAS du bureau ; Bureau, Documents et "
                 "réglages du logiciel de DAO dans le profil de l'ancien Windows (aucune copie)")),
    ("Autorisation", "Installation sur le SSD neuf signée ; effacement de l'ancien SSD : seulement dans un mois, sur nouvel accord écrit"),
)
_A_INVENTORY = _table(
    "Dossier A, document A2 — Inventaire du poste",
    ("Élément", "Relevé"),
    ("Firmware", "UEFI, démarrage sécurisé activé, TPM 2.0 activé, contrôleur de stockage en AHCI"),
    ("Processeur et mémoire", "64 bits, présent dans la liste de compatibilité ; 32 Go"),
    ("Disques", "SSD SATA 256 Go (GPT, Windows 10) ; disque dur 2 To (GPT, PROJETS) ; SSD NVMe 1 To neuf"),
    ("Réseau et affichage", "Carte Ethernet intégrée à la carte mère ; carte graphique dédiée"),
    ("Périphérique", "Imprimante multifonction laser en USB"),
    ("Logiciels", "Logiciel de DAO (licence liée au compte en ligne du bureau), suite bureautique, client du NAS"),
)
_A_INSTALLER = _schema(
    "Dossier A, document A3 — Écran de l'installateur au moment de choisir le disque (capture fictive)",
    INSTALLER_FIGURE.alt,
    INSTALLER_FIGURE_FILE,
)
_A_DEVICES = _console(
    "Dossier A, document A4 — Gestionnaire de périphériques après l'installation (capture fictive)",
    *(line for cat, name, msg, hw in DEVICES
      for line in (f"[{cat}] {name}", f"  État : {msg}", f"  ID du matériel : {hw}")),
)
_A_STAFF = _table(
    "Dossier A, document A5 — Personnes et situation actuelle des comptes",
    ("Personne", "Rôle"),
    *((person, role) for person, role, _need in STAFF),
    ("Situation actuelle", ("Tous ouvrent le même compte local « Bureau », administrateur, sans mot de passe. "
                            "Pas de serveur ni de contrôleur de domaine : un NAS pour les fichiers ; "
                            "chaque PC a ses propres comptes.")),
)

_B_REQUEST = _table(
    "Dossier B, document B1 — Demandes du Repair Café « La Clé » (asbl)",
    ("Demande", "Détail"),
    ("1. Portable de Nadia", (f"Windows 11 à garder (BitLocker actif sur C:) ; elle veut aussi Ubuntu 24.04 LTS en double "
                              f"démarrage. SSD 512 Go, {DUAL_BOOT_RAM_GB} Go de mémoire, pas besoin d'hibernation sous Linux. "
                              "Elle a déjà réduit C: depuis Windows. Documents copiés hier sur un disque externe, copie "
                              "vérifiée ; accord écrit signé.")),
    ("2. Serveur de fichiers", ("PC sous Debian qui partage /srv/partage. Hier, un bénévole y a branché un disque de 1 To "
                                "neuf (vide) pour de futures sauvegardes. Depuis, il ne démarre plus normalement.")),
    ("3. Nouvelle bénévole", ("Lucie a reçu un compte sur le serveur mais ne peut pas ouvrir le dossier des fiches de "
                              "réparation ; Marc peut l'ouvrir mais pas modifier l'inventaire.")),
)
_B_PARTITIONS = _schema(
    "Dossier B, document B2 — Disque du portable de Nadia avant l'installation (schéma fictif)",
    PARTITIONS_FIGURE.alt,
    PARTITIONS_FIGURE_FILE,
)
_B_EMERGENCY = _console("Dossier B, document B3 — Écran du serveur au démarrage (capture fictive)", *EMERGENCY_SCREEN)
_B_LSBLK = _console(
    "Dossier B, document B4 — Relevés en mode de maintenance, compte root (capture fictive)", *LSBLK_SCREEN
)
_B_PERMS = _console("Dossier B, document B5 — Sessions de Lucie et de Marc sur le serveur (capture fictive)", *PERMISSIONS_SCREEN)

_C_REQUEST = _table(
    "Dossier C, document C1 — Fiche d'intervention",
    ("Rubrique", "Contenu"),
    ("Client", "Agence immobilière Delvaux ; gérant : M. Delvaux"),
    ("Poste 1", ("PC-ACCUEIL, Windows 11 Professionnel. Hier à 18 h 40, la secrétaire a accepté l'installation du "
                 "nouveau pilote graphique proposée par l'utilitaire du fabricant de la carte graphique. Depuis, un "
                 "écran d'arrêt s'affiche à chaque démarrage, puis Windows lance la réparation automatique.")),
    ("Données du poste 1", "Dossiers de l'agence sur le NAS ; Bureau et Documents locaux copiés sur le NAS la semaine passée"),
    ("Autorisation", "Diagnostic et remise en état sans effacement ; toute réinitialisation : accord écrit"),
)
_C_STOP = _schema(
    "Dossier C, document C2 — Écran affiché au démarrage du poste 1 (capture fictive)",
    STOP_FIGURE.alt,
    STOP_FIGURE_FILE,
)
_C_WINRE = _console("Dossier C, document C3 — Après le deuxième échec de démarrage (capture fictive)", *WINRE_SCREEN)
_C_POINTS = _table(
    "Dossier C, document C4 — Points de restauration du poste 1 (relevés dans WinRE, fictifs)",
    ("Date et heure", "Description", "Type"),
    *RESTORE_POINTS,
)
_C_SECOND = _table(
    "Dossier C, document C5 — Poste 2 (PC-GESTION) : constats",
    ("Point observé", "Constat"),
    ("Symptôme", "Windows 11 démarre, mais l'Explorateur et les Paramètres se ferment seuls plusieurs fois par jour"),
    ("Disque", "SSD sain (relevé SMART sans défaut), 120 Go libres"),
    ("sfc /scannow", "« La protection des ressources Windows a trouvé des fichiers corrompus mais n'a pas pu en réparer certains. »"),
    ("DISM /Online /Cleanup-Image /RestoreHealth", "Échec : fichiers source introuvables"),
    ("Restauration du système", "Aucun point de restauration"),
    ("Logiciels", "Logiciel de gestion immobilière (licence et clé dans le contrat), suite bureautique, client du NAS"),
    ("Données", "Dossier « Agence » local de 40 Go ; tu viens de le copier sur un disque externe"),
)
_C_HASHES = _table(
    "Dossier C, document C6 — Empreintes SHA-256 (Get-FileHash) de trois fichiers, original et copie",
    ("Fichier", "Empreinte de l'original (poste 2)", "Empreinte de la copie (disque externe)"),
    *BACKUP_HASHES,
)

_ESP, _MSR, _WIN, _RECOVERY = CREATED_PARTITIONS
_GOOD_COPIES = ", ".join(name for name, *_h in BACKUP_HASHES if name not in BAD_COPIES)

# =============================================================================================
# Les 10 questions (10 points chacune)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    # ------------------------------------------------------------------ Partie 1
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Choisir le système et l'édition, vérifier les prérequis de trois postes",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-10", "AP-12"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Une petite entreprise veut équiper trois postes (document 1). Elle préfère Windows 11 "
            "quand c'est possible et utile, et accepte un autre système si un poste ne le permet pas. Le "
            "relevé a été fait avec Informations système (msinfo32), la console TPM (tpm.msc) et Gestion des "
            "disques ; la liste de compatibilité citée est celle des processeurs publiée par Microsoft."
        ),
        documents=(_P1_STATIONS,),
        instructions=(
            ("Pour chaque poste, conclus : compatible avec Windows 11 tel quel, compatible après réglages, ou "
             "non compatible ; cite les éléments du relevé qui justifient ta conclusion."),
            ("Recommande pour chaque poste un système et, pour Windows, une édition (Famille ou "
             "Professionnel) ; justifie par l'usage et la durée de support."),
            ("Pour le poste 1, rédige dans l'ordre les réglages à faire avant la mise à niveau et explique "
             "pourquoi cet ordre compte ; dis comment tu vérifies le résultat (outil graphique et ligne "
             "de commande)."),
        ),
        criteria=(
            _c("Verdicts justifiés", 3, f"Poste 1 : {W11_SETTINGS.lower()} (UEFI possible mais mode hérité, table MBR, TPM 2.0 désactivé) ; poste 2 : {W11_NO.lower()} ({_blockers(_S2)}) ; poste 3 : {W11_OK.lower()}. 1 point par poste, preuve citée."),
            _c("Système et édition", 3, f"Poste 1 : {STATION_EDITIONS[_S1]} suffit (usage courant). Poste 2 : pas de Windows 11 (Windows 10 n'est plus pris en charge depuis le 14 octobre 2025) → distribution Linux à support long (Ubuntu LTS, Linux Mint) ou ChromeOS Flex, possibles car usage web seulement ; ou remplacer le PC. Poste 3 : {STATION_EDITIONS[_S3]} (BitLocker et sa console, hôte Bureau à distance absents de Famille)."),
            _c("Réglages ordonnés et vérification", 4, f"Sauvegarde vérifiée ; {_settings(_S1)} — la conversion en GPT (mbr2gpt /validate puis /convert, avec /allowFullOS) se fait AVANT de passer en UEFI, sinon le PC ne démarre plus (un firmware UEFI ne démarre pas un disque MBR) ; vérification : msinfo32 « Mode BIOS : UEFI » et « État du démarrage sécurisé : Activé », tpm.msc version 2.0 ; en ligne de commande, PowerShell administrateur Confirm-SecureBootUEFI (True) et Get-Tpm (TpmPresent/TpmReady True)."),
        ),
        correction=(
            f"Poste 1 : {W11_SETTINGS.lower()} — le processeur est compatible, 8 Go et 256 Go suffisent, le firmware sait démarrer en UEFI mais tourne en mode hérité (CSM) avec un disque MBR, et le TPM 2.0 est présent mais désactivé. Poste 2 : {W11_NO.lower()} — {_blockers(_S2)} ; aucun réglage ne corrige cela. Poste 3 : {W11_OK.lower()}.",
            f"Poste 1 : {STATION_EDITIONS[_S1]} suffit pour l'agenda, le courrier et le traitement de texte. Poste 2 : Windows 10 n'est plus pris en charge depuis le 14 octobre 2025 ; comme l'usage se limite au navigateur, on installe une distribution Linux à support long (Ubuntu LTS ou Linux Mint) ou ChromeOS Flex, sinon on remplace le PC. Poste 3 : {STATION_EDITIONS[_S3]}, car le chiffrement BitLocker avec sa console et l'hôte Bureau à distance n'existent pas dans l'édition Famille.",
            f"Poste 1, dans l'ordre : sauvegarde vérifiée ; {_settings(_S1)}. On convertit d'abord le disque en GPT (mbr2gpt /validate puis /convert, avec /allowFullOS depuis Windows) parce qu'un firmware en mode UEFI ne démarre pas un disque MBR : changer le mode avant laisserait le PC sans démarrage. Vérification : msinfo32 affiche « Mode BIOS : UEFI » et « État du démarrage sécurisé : Activé », tpm.msc la version 2.0 ; en PowerShell administrateur, Confirm-SecureBootUEFI renvoie True et Get-Tpm indique un TPM présent et prêt. Ensuite seulement, la mise à niveau.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Utiliser l'interface graphique et la ligne de commande, relancer un service",
        question_type="document_analysis",
        requirement_ids=("AP-11", "AP-12", "AP-15"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Le responsable de l'atelier te demande quatre relevés sur un poste Windows 11 et sur un "
            "poste Ubuntu (document 1), puis de régler un problème : sur le poste Ubuntu, plus aucune impression "
            "ne part depuis le dernier redémarrage. Tu as tapé la commande du document 2 avec ton compte "
            "standard."
        ),
        documents=(_P1_TASKS, _P1_CUPS),
        instructions=(
            ("Pour chacun des quatre relevés du document 1, donne l'outil graphique et la commande sous "
             "Windows, puis l'équivalent sous Ubuntu."),
            ("Interprète le document 2 : quel est l'état du service d'impression, maintenant et au "
             "prochain démarrage ?"),
            ("Rédige la correction : commande exacte, droits nécessaires et pourquoi, puis les vérifications "
             "qui prouvent que c'est réglé, y compris après un redémarrage. Donne l'équivalent sous Windows."),
        ),
        criteria=(
            _c("Outils et commandes", 4, "1) Gestion des disques (diskmgmt.msc), diskpart puis list disk / Get-Disk ; Disques ou GParted, lsblk -f ou df -h. 2) Gestionnaire de périphériques (devmgmt.msc), pnputil /enum-drivers ou Get-PnpDevice ; Pilotes additionnels, lspci -k ou lsusb. 3) Paramètres > Réseau et Internet, ipconfig /all ; Paramètres > Réseau, ip a et ip route (DNS : resolvectl status). 4) Services (services.msc), sc query ou Get-Service ; systemctl status. 0,5 point par ligne complète (Windows et Linux)."),
            _c("Lecture de l'état", 2, "Service cups arrêté (inactive (dead)) et désactivé au démarrage (disabled), alors que le préréglage de la distribution est enabled : quelqu'un l'a désactivé ; il ne repartira pas seul au prochain démarrage."),
            _c("Correction, droits et vérification", 4, f"{CUPS_FIX} : sudo systemctl enable --now cups (ou enable puis start) ; sudo parce que modifier un service touche tout le système (compte administrateur, membre du groupe sudo ; systemctl status se lit sans droit) ; vérifier systemctl status cups (active (running), enabled), page de test imprimée, puis redémarrage et nouveau contrôle ; Windows : services.msc, Spouleur d'impression, type de démarrage Automatique puis Démarrer, page de test."),
        ),
        correction=(
            "Disques et partitions : Gestion des disques (diskmgmt.msc) ; diskpart puis list disk, ou Get-Disk en PowerShell ; sous Ubuntu, Disques ou GParted, et lsblk -f (df -h pour l'espace). Pilotes : Gestionnaire de périphériques (devmgmt.msc) ; pnputil /enum-drivers ou Get-PnpDevice ; sous Ubuntu, « Pilotes additionnels » et lspci -k, lsusb. Réseau : Paramètres > Réseau et Internet, ipconfig /all ; sous Ubuntu, Paramètres > Réseau, ip a et ip route (resolvectl status pour le DNS). Service : Services (services.msc), sc query ou Get-Service ; sous Ubuntu, systemctl status.",
            "Le document 2 montre le service cups « inactive (dead) » : il ne tourne pas, d'où l'impression impossible. Il est aussi « disabled » alors que le préréglage de la distribution est « enabled » : il a été désactivé, et ne démarrera pas au prochain démarrage.",
            f"Correction ({CUPS_FIX.lower()}) : sudo systemctl enable --now cups. Il faut un compte administrateur (membre du groupe sudo) car on modifie un service de tout le système ; lire l'état ne demande aucun droit. Vérifications : systemctl status cups affiche « active (running) » et « enabled » ; une page de test s'imprime ; après un redémarrage, le service est toujours actif. Sous Windows : services.msc, Spouleur d'impression, type de démarrage Automatique, Démarrer, puis page de test.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier A
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Préparer et réaliser l'installation propre de Windows 11 sur un SSD neuf",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-03", "AP-C03"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Au bureau d'architectes Verhaegen, tu dois installer Windows 11 Professionnel sur le SSD "
            "NVMe neuf du poste PC-DAO-01 (documents A1 et A2). Tu as démarré sur une clé d'installation : "
            "l'installateur affiche l'écran du document A3, avec les trois disques branchés."
        ),
        documents=(_A_REQUEST, _A_INVENTORY, _A_INSTALLER),
        instructions=(
            ("Rédige, dans l'ordre, la préparation que tu aurais dû faire avant de démarrer sur la clé "
             "(données, licence, logiciels, pilotes, clé d'installation, disques)."),
            ("Pour chaque disque de l'écran A3, dis ce que tu fais et pourquoi ; précise le disque et la "
             "zone que tu sélectionnes."),
            ("Cite les partitions que l'installateur crée sur ce disque (nom, système de fichiers, rôle) "
             "et explique le lien entre UEFI, GPT et la partition système EFI."),
            "Indique comment tu vérifies, après l'installation, le style du disque, le mode de démarrage et l'activation.",
        ),
        criteria=(
            _c("Préparation ordonnée", 3, "Copie du profil de l'ancien Windows (Bureau, Documents, réglages de DAO) vers le NAS ou un disque externe, vérifiée ; licence numérique : installer la même édition Professionnelle ; liste des logiciels et de leurs licences (compte du logiciel de DAO) ; pilotes réseau du fabricant sur une clé ; clé d'installation officielle de Microsoft ; débrancher l'ancien SSD et le disque PROJETS pendant l'installation (pas d'erreur de disque, partition EFI créée sur le SSD neuf)."),
            _c("Choix sur l'écran A3", 3, f"Disque 0 (ancien Windows 10, profil non sauvegardé, effacement non autorisé) : ne pas toucher ; disque 1 (PROJETS) : ne pas toucher ; {TARGET_DISK}, espace non alloué de 931,5 Go = SSD neuf de 1 To : le sélectionner et cliquer sur Suivant, sans Supprimer ni Formater ; les tailles sont en Gio, d'où 931,5 pour 1 To."),
            _c("Partitions et UEFI/GPT", 2, f"{_ESP[0]} ({_ESP[1]}, {_ESP[2]}, chargeur lu par le firmware), {_MSR[0]} ({_MSR[2]}), {_WIN[0]} ({_WIN[1]}), {_RECOVERY[0]} ({_RECOVERY[1]}, WinRE) ; en mode UEFI, Windows s'installe sur un disque GPT et le firmware démarre le fichier de la partition EFI (FAT32)."),
            _c("Vérification", 2, f"Gestion des disques : {TARGET_DISK} en GPT avec ses quatre partitions, C: dessus ; msinfo32 : « Mode BIOS : UEFI », démarrage sécurisé activé ; Paramètres > Système > Activation : Windows activé ({ACTIVATION[0].lower()}, {ACTIVATION[1]}) ; démarrage correct avec les deux autres disques rebranchés, données de PROJETS intactes."),
        ),
        correction=(
            f"Préparation : copier le profil de l'ancien Windows (Bureau, Documents, réglages du logiciel de DAO) vers le NAS ou un disque externe et vérifier la copie ; noter que la licence numérique active automatiquement la même édition, donc installer {LICENCE_EDITION} ; lister les logiciels et leurs licences (le logiciel de DAO se réactive avec le compte du bureau) ; copier sur une clé le pilote réseau du fabricant ; créer la clé d'installation avec l'outil officiel de Microsoft ; enfin, PC débranché, déconnecter l'ancien SSD et le disque PROJETS pour que seul le SSD neuf soit visible.",
            f"Sur l'écran A3, les disques 0 et 1 ne se touchent pas : le disque 0 contient l'ancien Windows et un profil sans copie, et son effacement n'est pas autorisé avant un mois ; le disque 1 contient les projets. Le SSD neuf est le {TARGET_DISK} (espace non alloué de 931,5 Go : Windows compte en Gio, 1 To ≈ 931 Gio). Je le sélectionne et je clique sur Suivant, sans Supprimer ni Formater.",
            f"L'installateur crée sur ce disque : {_ESP[0]} en {_ESP[1]} ({_ESP[2]}), qui contient le chargeur de démarrage lu par le firmware ; {_MSR[0]} ({_MSR[2]}) ; {_WIN[0]} en {_WIN[1]} ; {_RECOVERY[0]} en {_RECOVERY[1]} pour WinRE. En mode UEFI, Windows exige un disque GPT et le firmware lance le fichier de démarrage de la partition EFI ; si les trois disques restent branchés, cette partition pourrait être prise sur un autre disque.",
            f"Vérification : Gestion des disques montre le {TARGET_DISK} en GPT avec ses quatre partitions et C: ; msinfo32 affiche « Mode BIOS : UEFI » et le démarrage sécurisé activé ; Paramètres > Système > Activation indique Windows activé ({ACTIVATION[1]}). Je rebranche ensuite les deux disques et je vérifie que le PC démarre et que PROJETS est intact.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Identifier et installer les pilotes manquants après l'installation",
        question_type="document_analysis",
        requirement_ids=("AP-05", "AP-11", "AP-15"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Windows 11 est installé sur PC-DAO-01 (inventaire en A2). Il n'y a pas de réseau, l'affichage "
            "est en basse résolution et l'imprimante USB ne fonctionne pas. Le document A4 reprend ce que montre "
            "le Gestionnaire de périphériques (onglet Détails, ID du matériel)."
        ),
        documents=(_A_INVENTORY, _A_DEVICES),
        instructions=(
            ("Pour chaque périphérique du document A4, identifie le fabricant grâce à son identifiant et "
             "explique ce que son état indique."),
            ("Rédige ta procédure d'installation des pilotes : ordre, sources fiables, et comment obtenir le "
             "pilote réseau alors que le PC n'a pas de réseau."),
            "Cite une précaution à prendre avant d'installer un pilote, et une source à refuser.",
            "Indique comment tu vérifies que chaque périphérique fonctionne.",
        ),
        criteria=(
            _c("Identification", 3, f"PCI\\VEN_10EC → {DEVICE_VENDORS['Contrôleur Ethernet']} (carte Ethernet) ; USB\\VID_04F9 → {DEVICE_VENDORS['Périphérique inconnu']} (l'imprimante multifonction) ; PCI\\VEN_10DE → {DEVICE_VENDORS['Carte graphique de base Microsoft']} ; Code 28 = aucun pilote installé ; « Carte graphique de base Microsoft » = pilote générique de Windows, d'où la basse résolution, même si le périphérique « fonctionne correctement »."),
            _c("Procédure ordonnée et sources", 4, "Pilote réseau d'abord, téléchargé sur un autre PC depuis le site du fabricant de la carte mère ou de Realtek (modèle, Windows 11, 64 bits) et copié par clé USB ; puis Windows Update (mises à jour facultatives, pilotes) ; chipset avant la carte graphique ; pilote graphique du site NVIDIA ou de Windows Update ; pilote de l'imprimante sur le site de Brother (ou Windows Update)."),
            _c("Précaution et source refusée", 1, "Point de restauration avant d'installer ; refuser les sites « tous pilotes » et les logiciels de type « driver booster »."),
            _c("Vérification", 2, "Gestionnaire de périphériques sans point d'exclamation ni Code 28, « Ce périphérique fonctionne correctement » ; ipconfig /all (adresse IPv4 obtenue) et accès au NAS ; carte graphique à son nom réel, définition native de l'écran ; page de test de l'imprimante et numérisation ; versions notées dans le rapport."),
        ),
        correction=(
            f"Le contrôleur Ethernet (PCI\\VEN_10EC) est une carte {DEVICE_VENDORS['Contrôleur Ethernet']} ; le « périphérique inconnu » USB (VID_04F9) est un appareil {DEVICE_VENDORS['Périphérique inconnu']}, l'imprimante multifonction ; la carte graphique (VEN_10DE) est une {DEVICE_VENDORS['Carte graphique de base Microsoft']}. Le Code 28 signifie qu'aucun pilote n'est installé ; « Carte graphique de base Microsoft » est le pilote générique de Windows : l'écran fonctionne, mais en basse définition et sans accélération.",
            "Ordre : réseau d'abord. Sur un autre PC, je télécharge le pilote Ethernet sur le site du fabricant de la carte mère ou de Realtek (bon modèle, Windows 11, 64 bits) et je le copie par clé USB. Une fois le réseau présent, Windows Update (mises à jour facultatives, pilotes) ; le chipset avant la carte graphique ; le pilote graphique sur le site de NVIDIA ou par Windows Update ; celui de l'imprimante sur le site de Brother.",
            "Avant chaque installation, je crée un point de restauration. Je refuse les sites « tous pilotes gratuits » et les logiciels de type « driver booster », qui installent des pilotes non vérifiés.",
            "Vérification : plus aucun point d'exclamation ni Code 28 ; ipconfig /all montre une adresse IPv4 et le NAS est accessible ; la carte graphique apparaît sous son nom, à la définition native de l'écran ; une page de test et une numérisation réussissent ; je note les versions des pilotes dans le rapport.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Organiser les comptes du bureau : groupe de travail, comptes et groupes",
        question_type="document_analysis",
        requirement_ids=("AP-24", "AP-11", "AP-27"),
        kind=KIND_DOC,
        context=(
            "Dossier A. La gérante du bureau Verhaegen veut profiter de la réinstallation de PC-DAO-01 pour "
            "« mettre de l'ordre dans les comptes ». Le document A5 décrit les personnes et la situation actuelle."
        ),
        documents=(_A_STAFF,),
        instructions=(
            ("Le bureau doit-il passer à un domaine ou rester en groupe de travail ? Justifie, et explique ce "
             "que ton choix implique pour les comptes."),
            ("Dresse la liste des comptes à créer sur ce poste : nom, type de compte, groupe local ; justifie "
             "avec le principe du moindre privilège. Dis ce que tu fais du compte « Bureau »."),
            ("Écris les commandes qui créent un compte standard et le compte administrateur, sans faire "
             "apparaître le mot de passe, puis la commande de contrôle."),
            "Prévois la fin du stage de Léo.",
        ),
        criteria=(
            _c("Domaine ou groupe de travail", 2, "Pas de serveur ni de contrôleur de domaine (Active Directory) : groupe de travail, donc des comptes locaux (ou comptes Microsoft) créés sur chaque poste ; un domaine demanderait un serveur et l'édition Professionnelle, et centraliserait comptes et droits."),
            _c("Comptes et groupes", 4, f"Un compte standard (groupe Utilisateurs) pour Anne, Karim, Sofia et Léo ; un compte administrateur nominatif pour Thomas (groupe Administrateurs), utilisé seulement pour administrer ; chaque compte avec son propre mot de passe ; compte « Bureau » commun : {SHARED_ACCOUNT_DECISION.lower()}, désactivé puis supprimé après récupération de ses fichiers ; moindre privilège : un logiciel malveillant ouvert dans une session standard ne modifie pas le système, et chaque action est attribuable."),
            _c("Commandes", 3, "Invite de commandes en administrateur : net user karim * /add (le * fait demander le mot de passe) ; net user thomas * /add puis net localgroup Administrateurs thomas /add ; contrôle : net user karim (compte actif, groupe *Utilisateurs) ; ou Paramètres > Comptes > Autres utilisateurs."),
            _c("Fin du stage", 1, "Désactiver le compte de Léo le 31 janvier (net user leo /active:no, ou date d'expiration du compte), puis le supprimer après avoir rendu ses fichiers utiles."),
        ),
        correction=(
            "Le bureau n'a ni serveur ni contrôleur de domaine : il reste en groupe de travail. Les comptes sont donc locaux (ou des comptes Microsoft) et doivent être créés sur chaque poste. Un domaine (Active Directory) demanderait un serveur et des postes en édition Professionnelle ; il centraliserait les comptes et les droits, ce qui n'est pas justifié pour cinq personnes.",
            "Comptes : Anne, Karim, Sofia et Léo reçoivent chacun un compte standard (groupe Utilisateurs), avec un mot de passe personnel ; Thomas, le technicien, un compte administrateur nominatif (groupe Administrateurs), réservé aux tâches d'administration. Le compte commun « Bureau » est refusé : un compte par personne. Il est désactivé, puis supprimé une fois ses fichiers copiés. Moindre privilège : en session standard, un logiciel malveillant ou une erreur ne modifie pas le système, et chaque action est attribuable à une personne.",
            "Dans une invite de commandes en administrateur : net user karim * /add (le * fait demander le mot de passe sans l'afficher), de même pour anne, sofia et leo ; net user thomas * /add puis net localgroup Administrateurs thomas /add. Contrôle : net user karim (compte actif, membre de *Utilisateurs) et une connexion d'essai.",
            "Fin du stage : le 31 janvier, je désactive le compte de Léo (net user leo /active:no, ou une date d'expiration fixée dès maintenant), puis je le supprime après avoir récupéré ses fichiers utiles.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier B
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Installer Ubuntu en double démarrage à côté de Windows",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-03", "AP-C03"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Au Repair Café « La Clé », tu installes Ubuntu 24.04 LTS sur le portable de Nadia, à côté "
            "de son Windows 11 (document B1, demande 1). Le document B2 montre son disque après la réduction de C: "
            "faite depuis Windows. Tu utilises l'installation manuelle des partitions."
        ),
        documents=(_B_REQUEST, _B_PARTITIONS),
        instructions=(
            ("Rédige, dans l'ordre, ce que tu fais ou vérifies sous Windows et avant de démarrer sur la clé, "
             "et pourquoi."),
            ("Pour chacune des cinq zones du document B2, indique ce que tu en fais dans l'installateur ; "
             "propose les partitions de Linux (point de montage, système de fichiers, taille) et justifie la "
             "taille du swap."),
            "Indique ce que tu ferais si la copie des documents de Nadia n'avait pas été vérifiée.",
            "Rédige les vérifications après l'installation.",
        ),
        criteria=(
            _c("Préparation sous Windows", 3, "Copie vérifiée et accord écrit (présents) ; clé de récupération BitLocker relevée et conservée hors du PC (un changement du démarrage peut la demander) ; démarrage rapide de Windows désactivé ; image d'Ubuntu téléchargée sur le site officiel et contrôlée (sha256sum -c : OK) ; clé démarrée sur l'entrée « UEFI: », démarrage sécurisé laissé actif."),
            _c("Zones et partitions", 4, f"Zone 1 (ESP) : réutilisée sans formatage, montée sur /boot/efi ; zones 2, 3 et 4 (MSR, Windows, récupération) : ne pas toucher ; zone 5 (175 Go libres) : y créer / en ext4 (25 Go au moins, 40 à 60 Go confortable), un swap de {DUAL_BOOT_SWAP_GB:g} Go ({DUAL_BOOT_RAM_GB} Go de mémoire sans hibernation ; {DUAL_BOOT_SWAP_HIBERNATION_GB:g} Go avec hibernation ; un fichier d'échange est accepté) et éventuellement /home en ext4 pour le reste ; chargeur installé dans l'ESP existante."),
            _c("Sans copie vérifiée", 1, "Arrêter : ne rien créer ni modifier tant que la sauvegarde n'est pas vérifiée et l'accord écrit obtenu."),
            _c("Vérifications", 2, "Menu GRUB affichant Ubuntu et Windows ; les deux systèmes démarrent (clé BitLocker demandée une fois au besoin) ; fichiers de Nadia présents sous Windows ; sous Ubuntu, lsblk -f et df -h conformes au plan ; réseau, mises à jour (sudo apt update puis sudo apt upgrade) ; ordre de démarrage noté (efibootmgr)."),
        ),
        correction=(
            "Préparation : la copie vérifiée et l'accord écrit existent, je les note dans la fiche. Sous Windows, je relève la clé de récupération BitLocker et je la garde hors du PC (une modification du démarrage peut la faire demander), puis je désactive le démarrage rapide (sinon Windows ne s'arrête pas vraiment et sa partition reste verrouillée). Je télécharge l'image d'Ubuntu sur le site officiel, je contrôle son empreinte (sha256sum -c doit répondre OK), j'écris la clé et je démarre sur l'entrée « UEFI: » ; le démarrage sécurisé reste actif.",
            f"Dans l'installation manuelle : la zone 1, partition système EFI de Windows, est réutilisée sans la formater et montée sur /boot/efi ; les zones 2, 3 et 4 (MSR, Windows, récupération) ne se touchent pas. Dans la zone 5 libre (175 Go), je crée / en ext4 (par exemple 60 Go, 25 Go au minimum), un swap de {DUAL_BOOT_SWAP_GB:g} Go — avec {DUAL_BOOT_RAM_GB} Go de mémoire et sans hibernation, le repère du cours est une fois la mémoire ({DUAL_BOOT_SWAP_HIBERNATION_GB:g} Go s'il fallait hiberner) ; un fichier d'échange convient aussi — et /home en ext4 pour le reste. Le chargeur s'installe dans l'ESP existante.",
            "Si la copie n'avait pas été vérifiée, j'arrête : aucune partition ne se crée ni ne se modifie avant une sauvegarde vérifiée et un accord écrit.",
            "Vérifications : le menu GRUB propose Ubuntu et Windows ; les deux démarrent (Windows peut demander une fois la clé BitLocker) ; les fichiers de Nadia sont intacts sous Windows ; sous Ubuntu, lsblk -f et df -h correspondent au plan ; le réseau fonctionne et les mises à jour passent (sudo apt update puis sudo apt upgrade) ; je note l'ordre de démarrage (efibootmgr) dans le rapport.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Dépanner un serveur Linux bloqué en mode d'urgence",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-13", "AP-15"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Le serveur de fichiers Debian du Repair Café ne démarre plus normalement depuis l'ajout d'un "
            "disque neuf (document B1, demande 2). Le document B3 montre l'écran au démarrage ; tu t'es connecté avec "
            "le mot de passe root (mode de maintenance) et tu as relevé le document B4."
        ),
        documents=(_B_REQUEST, _B_EMERGENCY, _B_LSBLK),
        instructions=(
            ("Interprète les documents B3 et B4 : à quelle étape le démarrage s'arrête-t-il, quelle ligne de "
             "configuration est en cause, et pourquoi l'ajout d'un disque vide l'a-t-il cassée ?"),
            ("Rédige la correction dans l'ordre, avec les commandes, en écrivant la ligne corrigée complète, "
             "puis les vérifications."),
            "Explique ce que tu ne fais surtout pas, et pourquoi un UUID plutôt qu'un nom /dev/sdX.",
        ),
        criteria=(
            _c("Interprétation", 4, f"Le noyau et systemd ont démarré ; systemd attend /dev/{OLD_DATA_NAME} (délai dépassé), ne peut donc pas monter /srv/partage et local-fs.target échoue → mode d'urgence ; ligne en cause dans /etc/fstab : « {FSTAB_BAD_LINE} » ; le disque neuf vide a pris le nom sdb (aucune partition, donc pas de sdb1) et le disque de données PARTAGE est devenu {NEW_DATA_NAME} : les noms /dev/sdX dépendent de l'ordre de détection."),
            _c("Correction ordonnée", 4, f"Vérifier que / est accessible en écriture (sinon mount -o remount,rw /) ; copie de sauvegarde de fstab (cp /etc/fstab /etc/fstab.bak) ; remplacer la ligne par « {FSTAB_FIXED_LINE} » (UUID relevé par blkid) ; findmnt --verify ; systemctl daemon-reload ; mount -a (ou mount /srv/partage) ; findmnt /srv/partage et ls pour voir les fichiers ; redémarrage complet et contrôle du partage depuis un poste."),
            _c("Interdits et justification", 2, "Ne pas formater ni partitionner sdb ou sdc, ne pas supprimer la ligne sans comprendre, ne pas réinstaller ; l'UUID identifie le système de fichiers lui-même, quel que soit le port ou l'ordre des disques ; nofail laisse le serveur démarrer si ce disque manque (à vérifier après chaque démarrage)."),
        ),
        correction=(
            f"Le noyau et systemd ont démarré : systemd attend le périphérique /dev/{OLD_DATA_NAME}, abandonne au bout du délai, ne peut pas monter /srv/partage, et local-fs.target (les systèmes de fichiers locaux) échoue : d'où le mode d'urgence. La ligne en cause est « {FSTAB_BAD_LINE} » dans /etc/fstab. Le disque neuf, vide, a pris le nom sdb (sans partition, donc pas de sdb1) et le disque de données PARTAGE est devenu {NEW_DATA_NAME} : les noms /dev/sdX suivent l'ordre de détection des disques.",
            f"Correction : vérifier que / est accessible en écriture (sinon mount -o remount,rw /) ; cp /etc/fstab /etc/fstab.bak ; remplacer la ligne par « {FSTAB_FIXED_LINE} », avec l'UUID donné par blkid ({DATA_UUID}) ; findmnt --verify pour contrôler le fichier ; systemctl daemon-reload ; mount -a ; findmnt /srv/partage et ls /srv/partage pour voir les fichiers ; puis redémarrer et vérifier le partage depuis un poste.",
            "Je ne formate ni ne partitionne sdb ou sdc, je ne supprime pas la ligne sans comprendre et je ne réinstalle pas. L'UUID désigne le système de fichiers lui-même, quel que soit le port ou l'ordre des disques ; l'option nofail permet au serveur de démarrer même si ce disque manque, ce qui oblige à vérifier le partage après chaque démarrage.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Lire et corriger des permissions Linux sur un dossier partagé",
        question_type="document_analysis",
        requirement_ids=("AP-27", "AP-11", "AP-12"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Sur le serveur Debian du Repair Café, Lucie, nouvelle bénévole, n'ouvre pas le dossier des "
            "fiches de réparation, et Marc ne peut pas enregistrer l'inventaire (document B1, demande 3). Le "
            "document B5 reprend leurs sessions. Jean est le responsable informatique de l'asbl."
        ),
        documents=(_B_REQUEST, _B_PERMS),
        instructions=(
            ("Explique, droits à l'appui, pourquoi Lucie reçoit « Permission denied » et pourquoi Marc lit "
             "l'inventaire sans pouvoir le modifier ; traduis les deux droits en notation octale."),
            "Explique le refus de sudo pour Lucie : est-ce une panne ? Qui doit faire la modification ?",
            ("Écris les commandes de correction (en précisant qui les lance), puis les vérifications ; "
             "justifie avec le moindre privilège et cite une « solution » à refuser."),
        ),
        criteria=(
            _c("Lecture des droits", 4, f"Dossier drwxrwx--- ({SHARE_DIR_OCTAL}), propriétaire jean, groupe benevoles : Lucie n'est ni le propriétaire ni dans le groupe (id : seulement lucie) → droits des « autres » --- : pas de x, elle ne peut pas entrer dans le dossier ; fichier -rw-r----- ({SHARE_FILE_OCTAL}) : Marc est dans benevoles → r-- : lecture sans écriture."),
            _c("Refus de sudo", 2, "Normal : Lucie a un compte standard, hors du groupe sudo ; c'est voulu ; la modification revient à Jean, administrateur (membre de sudo)."),
            _c("Correction, vérification, refus", 4, f"Jean : sudo usermod -aG benevoles lucie (-a pour ajouter sans retirer les autres groupes), Lucie se reconnecte ; Jean (propriétaire) : chmod g+w /srv/partage/fiches/inventaire.ods ({SHARE_FILE_FIXED_OCTAL}) ; vérification : id lucie ou groups lucie montre benevoles, Lucie entre dans le dossier, Marc enregistre l'inventaire, ls -l montre -rw-rw----. Refuser chmod -R 777, donner sudo à tous ou travailler en root."),
        ),
        correction=(
            f"Le dossier est en drwxrwx--- ({SHARE_DIR_OCTAL}), propriétaire jean, groupe benevoles. Lucie n'en est pas propriétaire et id montre qu'elle n'appartient qu'au groupe lucie : ce sont donc les droits des « autres », ---, qui s'appliquent ; sans x, elle ne peut pas entrer dans le dossier. Le fichier inventaire.ods est en -rw-r----- ({SHARE_FILE_OCTAL}) : Marc est membre de benevoles, il reçoit r-- et peut lire, pas écrire.",
            "Le refus de sudo n'est pas une panne : Lucie a un compte standard, hors du groupe sudo, et c'est voulu. C'est Jean, administrateur (membre du groupe sudo), qui fait la modification.",
            f"Jean lance sudo usermod -aG benevoles lucie (-a ajoute le groupe sans retirer les autres) ; Lucie se déconnecte et se reconnecte. Jean, propriétaire du fichier, lance chmod g+w /srv/partage/fiches/inventaire.ods (soit {SHARE_FILE_FIXED_OCTAL}). Vérifications : groups lucie (ou id lucie) affiche benevoles ; Lucie ouvre le dossier ; Marc enregistre l'inventaire ; ls -l affiche -rw-rw----. Moindre privilège : on donne au groupe exactement le droit nécessaire. Je refuse chmod -R 777, sudo pour tout le monde ou le travail en root.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier C
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Dépanner un Windows qui s'arrête au démarrage après une mise à jour de pilote",
        question_type="document_analysis",
        requirement_ids=("AP-09", "AP-13", "AP-15"),
        kind=KIND_DOC,
        context=(
            "Dossier C. À l'agence immobilière Delvaux, le poste PC-ACCUEIL ne démarre plus depuis hier soir "
            "(document C1). Tu observes l'écran du document C2 à chaque démarrage, puis celui du document C3 après "
            "le deuxième échec ; le document C4 liste les points de restauration."
        ),
        documents=(_C_REQUEST, _C_STOP, _C_WINRE, _C_POINTS),
        instructions=(
            ("Interprète les documents : à quelle étape du démarrage la panne survient-elle, quelle est la "
             "cause la plus probable et quels indices le montrent ?"),
            ("Rédige ta procédure de réparation dans l'ordre, du geste le moins invasif au plus invasif, en "
             "nommant les options de WinRE que tu utilises et ce que chacune conserve."),
            "Explique pourquoi tu ne réinitialises pas le PC à ce stade.",
            "Rédige les vérifications et ce que tu fais pour que la panne ne revienne pas.",
        ),
        criteria=(
            _c("Interprétation", 3, f"Firmware et gestionnaire de démarrage passent, l'arrêt survient au chargement de Windows et de ses pilotes ; code {STOP_CODE}, fichier en cause {FAILED_DRIVER} (pilote graphique) ; installé hier à 18 h 40, juste avant la panne (C1, C4) ; deux échecs → réparation automatique, qui n'a pas réparé."),
            _c("Procédure ordonnée", 4, f"Options avancées → Paramètres → Redémarrer → 4 (mode sans échec : pilotes de base, le pilote graphique n'est pas chargé) → Gestionnaire de périphériques → carte graphique → Pilote → Restaurer le pilote (ou désinstaller le périphérique et son pilote) → redémarrage normal ; si le mode sans échec échoue : Restauration du système au point du {RESTORE_POINT_TO_USE[0]} (« {RESTORE_POINT_TO_USE[1]} ») : fichiers conservés, programmes et pilotes installés après retirés ; l'outil de redémarrage système a déjà échoué, la désinstallation des mises à jour ne vise pas ce pilote."),
            _c("Pas de réinitialisation", 1, "Cause identifiée et réversible ; une réinitialisation retirerait les applications (accord écrit et sauvegarde vérifiée exigés) pour un problème qui se règle en annulant le dernier changement."),
            _c("Vérification et prévention", 2, "Plusieurs démarrages normaux ; carte graphique sans erreur, définition correcte ; Observateur d'événements sans nouvelle erreur critique ; mise à jour automatique du pilote par l'utilitaire désactivée ou reportée, attente d'une version corrigée ; informer la secrétaire ; rapport."),
        ),
        correction=(
            f"Le firmware et le gestionnaire de démarrage passent : la panne survient pendant le chargement de Windows et de ses pilotes. L'écran d'arrêt donne le code {STOP_CODE} et le fichier {FAILED_DRIVER}, un pilote graphique ; il a été installé hier à 18 h 40, juste avant la panne (documents C1 et C4). Après deux échecs, Windows a lancé la réparation automatique, qui n'a rien réparé.",
            f"Procédure : Options avancées → Paramètres → Redémarrer, puis touche 4 pour le mode sans échec, qui ne charge que des pilotes de base. Dans le Gestionnaire de périphériques : carte graphique → Propriétés → Pilote → Restaurer le pilote (ou désinstaller le périphérique en supprimant ce pilote), puis redémarrage normal. Fichiers et programmes sont conservés. Si le mode sans échec ne démarre pas : Restauration du système au point du {RESTORE_POINT_TO_USE[0]}, créé avant l'installation du pilote — les fichiers restent, les programmes et pilotes installés depuis sont retirés. L'outil de redémarrage système a déjà échoué ; « Désinstaller des mises à jour » ne concerne pas ce pilote, venu de l'utilitaire du fabricant.",
            "Je ne réinitialise pas : la cause est identifiée et réversible. Une réinitialisation retirerait toutes les applications et demanderait une sauvegarde vérifiée et un accord écrit, pour une panne qui se règle en annulant le dernier changement.",
            "Vérifications : plusieurs démarrages normaux ; carte graphique sans erreur et à la bonne définition ; Observateur d'événements sans nouvelle erreur critique. Prévention : désactiver la mise à jour automatique du pilote dans l'utilitaire et attendre une version corrigée ; expliquer à la secrétaire ; noter tout dans le rapport.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Vérifier une sauvegarde et choisir la restauration d'un système endommagé",
        question_type="document_analysis",
        requirement_ids=("AP-C03", "AP-15", "AP-03"),
        kind=KIND_DOC,
        context=(
            "Dossier C. Le second poste de l'agence, PC-GESTION, a un Windows endommagé (document C5). Tu as copié le "
            "dossier « Agence » sur un disque externe et calculé les empreintes SHA-256 de trois fichiers de "
            "contrôle, sur l'original et sur la copie (document C6). Le gérant demande « de tout remettre à neuf »."
        ),
        documents=(_C_SECOND, _C_HASHES),
        instructions=(
            ("Interprète le document C6 : quelles copies sont fiables, que fais-tu pour les autres, et "
             "comment ces empreintes ont-elles été obtenues ?"),
            ("Le document C5 montre ce qui a déjà été tenté. Choisis l'intervention à essayer d'abord, puis "
             "celle de repli : pour chacune, ce qu'elle conserve et la précaution exigée."),
            "Rédige ton plan dans l'ordre, de la sauvegarde aux contrôles finaux.",
            "Rédige le court message (quatre ou cinq lignes) qui demande l'accord du gérant.",
        ),
        criteria=(
            _c("Empreintes", 3, f"Empreintes identiques → copie identique pour {_GOOD_COPIES} ; différente pour {', '.join(BAD_COPIES)} → recopier puis recalculer jusqu'à l'égalité (copie interrompue ou abîmée) ; obtenues avec Get-FileHash (SHA-256 par défaut) ou certutil -hashfile … SHA256, sur l'original et sur la copie ; même empreinte = même contenu."),
            _c("Choix de l'intervention", 3, f"sfc et DISM ont échoué, aucun point de restauration : d'abord « Résoudre les problèmes à l'aide de Windows Update » (réinstalle Windows, conserve fichiers et programmes ; sauvegarde à jour et accord) ; en repli, « Réinitialiser ce PC » → « Conserver mes fichiers » ({RESET_EFFECT.lower()} ; {RESET_PRECAUTION.lower()}) ; pas de « Supprimer tout » : rien ne justifie d'effacer les fichiers."),
            _c("Plan ordonné", 2, "Sauvegarde vérifiée (empreintes, ouverture d'essai), liste des logiciels et de leurs clés (logiciel de gestion immobilière), accord écrit, réinstallation via Windows Update, sinon réinitialisation en conservant les fichiers, puis pilotes, mises à jour, logiciels, connexion au NAS, contrôle des fichiers et des symptômes, rapport."),
            _c("Message au gérant", 2, "Clair et sans jargon : Windows est endommagé ; on essaie d'abord une réparation qui garde tout ; sinon une remise à neuf qui garde les fichiers mais retire les programmes, réinstallés ensuite ; données déjà copiées et contrôlées ; durée ; demande d'accord écrit."),
        ),
        correction=(
            f"Les empreintes sont identiques pour {_GOOD_COPIES} : ces copies sont identiques à l'original. Pour {', '.join(BAD_COPIES)}, elles diffèrent : la copie est incomplète ou abîmée ; je la refais puis je recalcule jusqu'à obtenir la même empreinte. Les empreintes viennent de Get-FileHash (SHA-256 par défaut) ou de certutil -hashfile … SHA256, calculées sur l'original et sur la copie : deux fichiers de même empreinte ont le même contenu.",
            f"sfc n'a pas tout réparé, DISM a échoué et il n'y a aucun point de restauration. J'essaie d'abord « Résoudre les problèmes à l'aide de Windows Update » (Paramètres → Système → Récupération) : il réinstalle Windows en conservant fichiers et programmes (sauvegarde à jour et accord). En repli, « Réinitialiser ce PC » → « Conserver mes fichiers » : {RESET_EFFECT.lower()} ; précaution : {RESET_PRECAUTION.lower()}. « Supprimer tout » n'est pas justifié : les fichiers ne sont pas en cause.",
            "Plan : sauvegarde complète et vérifiée (empreintes, ouverture de quelques fichiers) ; liste des logiciels et de leurs clés, dont le logiciel de gestion immobilière ; accord écrit du gérant ; réinstallation via Windows Update, sinon réinitialisation en conservant les fichiers ; pilotes et mises à jour ; réinstallation des logiciels et connexion au NAS ; contrôle du dossier « Agence » et absence des fermetures intempestives ; rapport.",
            "Message : « Le système Windows du poste de gestion est endommagé. Vos fichiers sont déjà copiés et contrôlés. Je propose d'abord une réparation qui garde tout ; si elle échoue, une remise à neuf qui garde vos fichiers mais retire les programmes, que je réinstallerai (environ une demi-journée). Pouvez-vous me donner votre accord écrit ? »",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()

# Partie ou dossier de chaque question, dans l'ordre du sujet.
ITEM_PARTS: dict[str, str] = {
    "X01": PART_1, "X02": PART_1,
    "X03": DOSSIER_A, "X04": DOSSIER_A, "X05": DOSSIER_A,
    "X06": DOSSIER_B, "X07": DOSSIER_B, "X08": DOSSIER_B,
    "X09": DOSSIER_C, "X10": DOSSIER_C,
}
# Cours où revoir la matière de chaque question.
ITEM_COURSES: dict[str, tuple[str, ...]] = {
    "X01": ("PR07",),
    "X02": ("PR10", "PR07"),
    "X03": ("PR08", "PR05"),
    "X04": ("PR10", "PR08"),
    "X05": ("PR10",),
    "X06": ("PR09", "PR05"),
    "X07": ("PR09", "PR11"),
    "X08": ("PR10", "PR09"),
    "X09": ("PR11", "PR12"),
    "X10": ("PR12",),
}
DOSSIER_DOCUMENTS: dict[str, tuple[ExerciseDocument, ...]] = {
    DOSSIER_A: (_A_REQUEST, _A_INVENTORY, _A_INSTALLER, _A_DEVICES, _A_STAFF),
    DOSSIER_B: (_B_REQUEST, _B_PARTITIONS, _B_EMERGENCY, _B_LSBLK, _B_PERMS),
    DOSSIER_C: (_C_REQUEST, _C_STOP, _C_WINRE, _C_POINTS, _C_SECOND, _C_HASHES),
}


def validate_items() -> list[str]:
    errors = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.total_points != POINTS_PER_QUESTION:
            errors.append(f"{item.key} : {item.total_points:g} points au lieu de {POINTS_PER_QUESTION}.")
        if item.question_type not in ("long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue.")
        if (item.question_type == "document_analysis") != bool(item.documents):
            errors.append(f"{item.key} : type et documents incohérents.")
    if sum(i.total_points for i in ALL_ITEMS) != EXAM_TOTAL_POINTS:
        errors.append("Total différent de 100 points.")
    return errors

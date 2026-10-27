"""PR09 « Installation complète de Linux — préparation et dépannage » — exercices corrigés et
mini-examen (ticket #209).

Même organisation que PR08 (`app.v1.ampcr_pratique_pr08_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 17 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (préparation, installation, finalisation), classements
  (symptôme → famille, points de montage, double démarrage, avant/pendant/après), terminaux
  fictifs (somme de contrôle, clé USB, efibootmgr, fstab, lspci, df), permissions, rapport,
  procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et terminaux sont **fictifs** ; procédures, partitions, swap, double démarrage,
dépannage et commandes viennent de `app.v1.ampcr_pratique_pr09_figures` (mêmes données que les
schémas). Sorties de terminal en anglais (voir ce module).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr09_figures import (
    DUAL_BOOT_ACTIONS,
    DUAL_BOOT_SCREEN,
    EFIBOOT_SCREEN,
    FINAL_STEPS,
    ISO_NAME,
    PK_DATA,
    PK_ESP,
    PK_FREE,
    PK_MSR,
    PK_RECOVERY,
    PK_WINDOWS,
    PREP_STEPS,
    SETUP_STEPS,
    TR_BOOT,
    TR_CATEGORIES,
    TR_DISK,
    TR_FSTAB,
    TR_NET,
    TR_PERM,
    TR_SPACE,
    checksum_verdict,
    dual_boot_action,
    first_boot_entry,
    swap_advice,
)

PR09_CODE = "PR09"

KIND_ORDER = "ordonnancement"
KIND_PREP = "préparation et choix"
KIND_INSTALL = "installation et partitions"
KIND_TROUBLE = "dépannage de l'installation"
KIND_POST = "finalisation et rapport"
KIND_ERROR = "repérage d'erreurs"

# Exigence officielle du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-10"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(PREP_STEPS)
E02_STEPS = _labels(SETUP_STEPS)
E03_STEPS = _labels(FINAL_STEPS)

E04_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("L'installateur d'Ubuntu signale Intel RST et ne propose aucun disque ; le firmware voit le SSD", TR_DISK),
    ("Après l'installation, le PC démarre toujours sous Windows, sans menu de choix", TR_BOOT),
    ("« grub rescue> » après la suppression d'une partition depuis Windows", TR_BOOT),
    ("« You are in emergency mode » depuis le remplacement du disque de données", TR_FSTAB),
    ("Aucun réseau Wi-Fi proposé ; lspci -nnk n'affiche aucun « Kernel driver in use » pour la carte", TR_NET),
    ("ip a affiche NO-CARRIER sur enp3s0", TR_NET),
    ("« Permission denied » en ouvrant un fichier copié par root dans le dossier personnel", TR_PERM),
    ("« marie is not in the sudoers file » en lançant sudo apt upgrade", TR_PERM),
    ("« No space left on device » ; df -h affiche 100 % pour /", TR_SPACE),
)

MP_ESP = "/boot/efi"
MP_ROOT = "/"
MP_HOME = "/home"
MP_SWAP = "swap"
E05_CATEGORIES = (MP_ESP, MP_ROOT, MP_HOME, MP_SWAP)
E05_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Le chargeur shim/GRUB lu par le firmware UEFI", MP_ESP),
    ("Partition FAT32 de 1 Go créée en tête de disque", MP_ESP),
    ("Le fichier de configuration /etc/fstab", MP_ROOT),
    ("Les logiciels installés par sudo apt install", MP_ROOT),
    ("Les photos et documents de l'utilisatrice", MP_HOME),
    ("La partition à conserver si l'on réinstalle le système", MP_HOME),
    ("L'image de la mémoire écrite lors de l'hibernation", MP_SWAP),
    ("La zone utilisée quand la mémoire vive est pleine", MP_SWAP),
)

# (zone affichée dans le partitionnement manuel, nature, sauvegarde vérifiée, accord écrit)
E06_CASES: tuple[tuple[str, str, bool, bool], ...] = (
    ("nvme0n1p1 — 100 Mo, vfat (partition système EFI de Windows)", PK_ESP, True, True),
    ("nvme0n1p2 — 16 Mo, sans système de fichiers (réservée Microsoft)", PK_MSR, True, True),
    ("nvme0n1p3 — 375 Go, ntfs, Windows réduit depuis Windows", PK_WINDOWS, True, True),
    ("nvme0n1p4 — 752 Mo, ntfs, WinRE", PK_RECOVERY, True, True),
    ("Espace libre de 100 Go libéré depuis Windows", PK_FREE, True, True),
    ("sda1 — 1 To, ntfs, « Photos » du client, disque dur interne", PK_DATA, True, True),
    ("Espace libre du portable d'une autre cliente, accord oral seulement, rien sauvegardé", PK_FREE, False, False),
)
E06_CORRECT = tuple(
    DUAL_BOOT_ACTIONS.index(dual_boot_action(kind, backup_verified=b, written_consent=w))
    for _d, kind, b, w in E06_CASES
)

WHEN_BEFORE = "Avant l'installation"
WHEN_DURING = "Pendant l'installation"
WHEN_AFTER = "Après l'installation"
E07_CATEGORIES = (WHEN_BEFORE, WHEN_DURING, WHEN_AFTER)
E07_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Relever la clé de récupération BitLocker de Windows", WHEN_BEFORE),
    ("Désactiver le démarrage rapide de Windows", WHEN_BEFORE),
    ("Contrôler l'ISO avec sha256sum -c", WHEN_BEFORE),
    ("Tester le Wi-Fi et le son en session live", WHEN_DURING),
    ("Cocher l'installation des logiciels tiers (pilotes, formats)", WHEN_DURING),
    ("Choisir /boot/efi pour l'ESP existante, sans la formater", WHEN_DURING),
    ("Lancer sudo apt update puis sudo apt upgrade", WHEN_AFTER),
    ("Vérifier systemctl --failed", WHEN_AFTER),
)

E08_FAILED_LINE = f"{ISO_NAME}: FAILED"
E08_VERDICT = checksum_verdict(E08_FAILED_LINE)

E11_FIRST_BEFORE = first_boot_entry(EFIBOOT_SCREEN[:7])
E11_FIRST_AFTER = first_boot_entry(EFIBOOT_SCREEN)

X02_SWAP = swap_advice(16, hibernation=False)
X02_SWAP_HIB = swap_advice(16, hibernation=True)
X01_SWAP = swap_advice(4, hibernation=False)

_FSTAB_OLD_UUID = "5b0e8f3a-9c2d-4e71-a6b4-2f8d1c7e9a10"
_FSTAB_NEW_UUID = "c41d7e22-08ab-4f3e-b915-7a6e0d2c5f83"

# =============================================================================================
# 17 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la préparation d'une installation de Linux",
        question_type="ordering",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Une maison de quartier veut installer Linux sur six PC de sa salle informatique, "
            "dont les données des animateurs doivent être conservées. Ton responsable prépare "
            "une fiche que les stagiaires suivront avant de démarrer sur une clé. Les six "
            "étapes de préparation ont été mélangées sur la fiche."
        ),
        instructions=("Remets les six étapes de préparation dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Demande et accord → inventaire → choix de la distribution → sauvegarde → ISO contrôlée → clé USB (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Recueillir la demande (usage, données à garder, Windows à conserver ou non) et l'accord écrit. 2. Inventorier le poste : mémoire, disques, firmware, puces réseau et graphique, BitLocker éventuel. 3. Choisir la distribution d'après l'usage et le matériel, en version à support long.",
            "4. Sauvegarder les données de tous les comptes sur un autre support et vérifier la copie. 5. Télécharger l'ISO sur le site officiel et la contrôler avec sha256sum -c (résultat « OK »). 6. Écrire la clé USB en vérifiant la cible avec lsblk : on n'écrit une clé qu'avec une image contrôlée.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (2, 4, 0, 5, 1, 3)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'installation, de la clé au bureau",
        question_type="ordering",
        requirement_ids=("AP-10",),
        kind=KIND_ORDER,
        context=(
            "La préparation du premier PC de la maison de quartier est terminée : données "
            "sauvegardées, accord signé, image Linux Mint contrôlée et clé écrite. Le stagiaire "
            "a noté les huit étapes de l'installation sur des post-it, tombés et mélangés."
        ),
        instructions=("Remets les huit étapes de l'installation dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Firmware → clé → langue, clavier, réseau → session live → type d'installation → partitions → compte et fuseau → copie et redémarrage (0,5 pt par étape)."),
        ),
        correction=(
            "1. Régler le firmware (UEFI, démarrage sécurisé laissé actif) et noter le mode du stockage. 2. Démarrer sur l'entrée « UEFI: » de la clé. 3. Choisir la langue, le clavier belge et le réseau. 4. Tester le matériel en session live (Wi-Fi, écran, son, disques vus par lsblk) avant de toucher au disque.",
            "5. Choisir le type d'installation (effacer, à côté de Windows ou manuel) et, si besoin, les logiciels tiers. 6. Définir les partitions : ESP sur /boot/efi, / en ext4, /home facultative, swap. 7. Créer le compte administrateur, le nom de la machine et le fuseau Europe/Brussels. 8. Laisser copier, puis retirer la clé au redémarrage.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (5, 2, 7, 0, 3, 6, 1, 4)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la finalisation avant de rendre le PC",
        question_type="ordering",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_ORDER,
        context=(
            "Linux Mint vient d'arriver au bureau sur le PC de l'accueil de la maison de "
            "quartier. Avant de rappeler la coordinatrice, il reste six opérations de "
            "finalisation, notées dans le désordre sur la fiche d'intervention."
        ),
        instructions=("Remets les six opérations dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Mises à jour → pilotes → réseau et services → comptes → démarrage → contrôle et rapport (0,5 pt par étape)."),
        ),
        correction=(
            "1. Mettre à jour (sudo apt update puis sudo apt upgrade) : les pilotes proposés ensuite tiennent compte du noyau à jour. 2. Installer les pilotes manquants (« Pilotes additionnels »), avec enrôlement de la clé MOK si le démarrage sécurisé est actif. 3. Contrôler le réseau (ip a, ping) et les services (systemctl --failed).",
            "4. Comptes : l'administrateur dans le groupe sudo, un compte standard pour l'usage quotidien. 5. Contrôler le démarrage (chaque système prévu démarre, ordre des entrées). 6. Passer la liste de contrôle avec la cliente et rédiger le rapport signé.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (3, 0, 5, 2, 4, 1)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Neuf symptômes pendant ou après l'installation : quelle famille ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-09", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "Ce mois-ci, l'atelier a installé Linux sur une vingtaine de postes ; neuf "
            "interventions ont posé un problème. Pour la réunion d'équipe, ton responsable veut "
            "ranger chaque symptôme relevé par les techniciens dans la famille de pannes du "
            "tableau de dépannage, afin de savoir quelle vérification faire en premier."
        ),
        instructions=("Range chaque symptôme dans la famille de pannes qui l'explique.",),
        criteria=(
            _c("Classement", 4.5, "Disque : Intel RST. Chargeur : démarrage direct sous Windows, grub rescue. fstab : mode d'urgence après remplacement du disque. Réseau : Wi-Fi sans pilote, NO-CARRIER. Permissions : Permission denied, sudoers. Espace : No space left (0,5 pt par élément)."),
        ),
        correction=(
            "Le message Intel RST alors que le firmware voit le SSD concerne le contrôleur de stockage : disque non vu. Démarrer sous Windows sans menu (ordre des entrées UEFI) et « grub rescue> » (GRUB ne trouve plus sa partition) relèvent du chargeur. Le mode d'urgence après un remplacement de disque vient d'une ligne de /etc/fstab qui désigne l'ancien UUID.",
            "Une carte sans « Kernel driver in use » et NO-CARRIER (pas de lien sur le câble) relèvent du réseau. « Permission denied » sur un fichier appartenant à root et « not in the sudoers file » relèvent des permissions et de sudo. « No space left on device » avec / à 100 % est un problème d'espace disque.",
        ),
        classification=Classification(
            categories=TR_CATEGORIES,
            elements=tuple(e for e, _c2 in E04_ELEMENTS),
            correct=tuple(TR_CATEGORIES.index(c) for _e, c in E04_ELEMENTS),
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Où se trouve chaque élément : /boot/efi, /, /home ou swap ?",
        question_type="classification",
        requirement_ids=("AP-10",),
        kind=KIND_INSTALL,
        context=(
            "Pour préparer le partitionnement manuel du PC d'une graphiste (SSD de 1 To, 16 Go "
            "de mémoire, Linux seul), tu expliques à un stagiaire ce que contiendra chaque "
            "partition. Il a noté huit éléments et doit dire, pour chacun, dans quelle partition "
            "(ou zone) il se trouvera une fois le système installé."
        ),
        instructions=("Range chaque élément dans la partition ou la zone où il se trouve.",),
        criteria=(
            _c("Classement", 4, "/boot/efi : chargeur shim/GRUB, partition FAT32 de tête. / : /etc/fstab, logiciels. /home : documents, partition à conserver. swap : image d'hibernation, débordement de la mémoire (0,5 pt par élément)."),
        ),
        correction=(
            "La partition système EFI, en FAT32 et montée sur /boot/efi, contient le chargeur (shim, GRUB) que lit le firmware UEFI. La racine / contient le système : /etc (dont /etc/fstab), /usr et les logiciels installés par apt.",
            "/home contient les dossiers personnels ; séparée, elle peut être conservée lors d'une réinstallation (sans être formatée). Le swap reçoit ce qui ne tient plus en mémoire vive et l'image de la mémoire lors de l'hibernation (il doit alors être au moins aussi grand que la mémoire utilisée).",
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
        title="Double démarrage : que faire de chaque zone du disque ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Un client veut garder Windows 11 et ajouter Ubuntu sur son PC. L'accord est signé, "
            "ses données sont sauvegardées et vérifiées, et Windows a été réduit depuis Windows "
            "pour libérer 100 Go. Dans le partitionnement manuel de l'installateur, tu décides "
            "du sort de chaque zone ; une dernière ligne concerne un autre PC de l'atelier."
        ),
        instructions=("Range chaque zone dans l'action à appliquer.",),
        criteria=(
            _c("Classement", 3.5, "Réutiliser sans formater : ESP de Windows. Ne pas toucher : MSR, Windows, WinRE, disque de photos. Créer : espace libre de 100 Go. Arrêter : accord oral sans sauvegarde (0,5 pt par élément)."),
        ),
        correction=(
            "L'ESP de Windows (100 Mo, vfat) est réutilisée : on lui donne le point de montage /boot/efi sans cocher le formatage, sinon le chargeur de Windows est effacé. Les partitions MSR, Windows et WinRE, et le disque de photos, ne sont pas touchés. Linux est créé dans l'espace libre de 100 Go libéré depuis Windows (racine en ext4, swap en fichier par défaut).",
            "Sur l'autre PC, un accord oral sans sauvegarde ne permet aucune modification du disque : on arrête, on sauvegarde, on obtient l'accord écrit.",
        ),
        classification=Classification(
            categories=DUAL_BOOT_ACTIONS,
            elements=tuple(d for d, *_r in E06_CASES),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Avant, pendant ou après l'installation ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Une collègue prépare son premier double démarrage Windows 11 + Ubuntu sur le "
            "portable d'un enseignant (disque chiffré par BitLocker, carte Wi-Fi récente). Elle a "
            "listé huit gestes sans savoir à quel moment les placer : avant de démarrer sur la "
            "clé, dans la session live et l'installateur, ou une fois Ubuntu au bureau."
        ),
        instructions=("Range chaque geste dans le moment où il se fait.",),
        criteria=(
            _c("Classement", 4, "Avant : clé BitLocker, démarrage rapide désactivé, ISO contrôlée. Pendant : test en session live, logiciels tiers, ESP sur /boot/efi sans formatage. Après : mises à jour, systemctl --failed (0,5 pt par élément)."),
        ),
        correction=(
            "Avant : tout ce qui se fait sous Windows ou sur l'image : relever la clé de récupération BitLocker (le firmware modifié peut la demander), désactiver le démarrage rapide (sinon la partition Windows reste « en hibernation ») et contrôler l'ISO.",
            "Pendant : tester le matériel en session live, cocher les logiciels tiers si un pilote non libre est nécessaire, attribuer /boot/efi à l'ESP existante sans la formater. Après : mises à jour (apt update puis apt upgrade) et contrôle des services en échec.",
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
        title="Une image ISO qui ne passe pas le contrôle",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Pour installer Ubuntu sur le PC d'un kinésithérapeute, un stagiaire a téléchargé "
            "l'image ISO pendant une coupure Wi-Fi, puis le fichier SHA256SUMS sur le site "
            "officiel. Il te montre le document 1 et propose d'écrire la clé quand même, « le "
            "fichier a la bonne taille »."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif, sortie en anglais)",
                "$ sha256sum -c SHA256SUMS --ignore-missing",
                E08_FAILED_LINE,
                "sha256sum: WARNING: 1 computed checksum did NOT match",
            ),
        ),
        instructions=("Interprète le résultat et rédige la marche à suivre.",),
        criteria=(
            _c("Lecture", 1, "FAILED : la somme calculée ne correspond pas à celle publiée ; image corrompue (téléchargement interrompu) ou modifiée ; la taille ne prouve rien."),
            _c("Marche à suivre", 1.5, "Supprimer l'image, la retélécharger depuis le site officiel ou un miroir listé, refaire sha256sum -c jusqu'à « OK » ; seulement ensuite écrire la clé."),
            _c("Justification", 0.5, "Une image corrompue donne une installation qui échoue ou un système défectueux ; une image modifiée peut contenir un logiciel malveillant."),
        ),
        correction=(
            f"« FAILED » signifie que la somme SHA-256 calculée sur le fichier ne correspond pas à celle publiée dans SHA256SUMS : l'image est corrompue (téléchargement interrompu) ou modifiée. Verdict : « {E08_VERDICT} ». Un fichier peut avoir à peu près la bonne taille et être abîmé ; seule la somme le prouve.",
            "On supprime l'image, on la retélécharge depuis le site officiel (ou un miroir qu'il liste), puis on relance sha256sum -c SHA256SUMS --ignore-missing jusqu'à obtenir « OK ». On n'écrit la clé qu'après : une image corrompue fait échouer l'installation ou donne un système défectueux, une image modifiée peut contenir un logiciel malveillant.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Écrire la clé avec dd sans effacer le mauvais disque",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-11", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Sur le PC Linux de l'atelier (SSD système et disque dur de 1 To d'archives des "
            "clients), tu dois écrire l'image d'Ubuntu, contrôlée « OK », sur une clé USB de 16 Go "
            "que tu viens de brancher. Le collègue qui te forme te demande d'abord d'identifier "
            "la clé dans le document 1, puis d'écrire la commande."
        ),
        documents=(
            _console(
                "Document 1 — Terminal de l'atelier (fictif)",
                "$ lsblk -d -o NAME,SIZE,TRAN,MODEL",
                "NAME      SIZE TRAN MODEL",
                "sda     931.5G sata ST1000DM010",
                "sdb      14.6G usb  DataTraveler 3.0",
                "nvme0n1 476.9G nvme Samsung SSD 970",
            ),
        ),
        instructions=(
            "Identifie la clé et justifie.",
            "Écris la commande dd complète et les précautions qui l'entourent.",
        ),
        criteria=(
            _c("Identification", 1, "sdb : 14,6 G (une clé de 16 Go), transport usb ; sda est le disque d'archives, nvme0n1 le SSD système."),
            _c("Commande", 1, f"sudo dd if={ISO_NAME} of=/dev/sdb bs=4M status=progress oflag=sync — sur le disque entier sdb, pas sur une partition sdb1."),
            _c("Précautions", 1, "Relire la cible avant Entrée (dd efface sans confirmation) ; démonter les partitions de la clé ; contrôle par lsblk après écriture ; un outil graphique (Etcher) limite le risque."),
        ),
        correction=(
            "La clé est sdb : 14,6 G correspond à une clé de 16 Go (capacité affichée en unités binaires) et son transport est usb. sda (931,5 G, sata) est le disque des archives des clients et nvme0n1 le SSD du système : une erreur de cible les effacerait sans confirmation.",
            f"Après avoir démonté les partitions éventuelles de la clé : sudo dd if={ISO_NAME} of=/dev/sdb bs=4M status=progress oflag=sync. On écrit sur le disque entier (/dev/sdb), pas sur une partition (/dev/sdb1). On relit la commande avant d'appuyer sur Entrée, puis on contrôle avec lsblk. Un outil graphique comme balenaEtcher, qui ne propose que les supports amovibles, réduit le risque.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Lire les partitions avant un double démarrage",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Une étudiante veut ajouter Ubuntu à côté de Windows 11 sur son portable. Accord "
            "signé, données sauvegardées et vérifiées ; tu as réduit la partition Windows depuis "
            "Windows (Gestion des disques) pour libérer 100 Go. En session live, tu relèves le "
            "document 1 avant de lancer le partitionnement manuel."
        ),
        documents=(_console("Document 1 — Session live (capture fictive)", *DUAL_BOOT_SCREEN),),
        instructions=(
            "Identifie le rôle de chaque partition de nvme0n1 et la clé.",
            "Rédige ce que tu attribues dans le partitionnement manuel, et ce que tu ne fais pas.",
        ),
        criteria=(
            _c("Lecture", 1.25, "nvme0n1p1 = ESP de Windows (100 Mo, vfat) ; p2 = MSR ; p3 = Windows (ntfs) ; p4 = WinRE ; sda = la clé (iso9660) ; l'espace libre n'est pas listé par lsblk."),
            _c("Attribution", 1.25, "p1 : point de montage /boot/efi sans formatage ; espace libre : / en ext4 (swap en fichier ou petite partition) ; chargeur installé dans l'ESP."),
            _c("À ne pas faire", 0.5, "Ne pas formater p1, ne pas toucher p2, p3, p4 ; ne pas choisir « effacer le disque »."),
        ),
        correction=(
            "nvme0n1p1 (100 Mo, vfat) est la partition système EFI de Windows ; p2 (16 Mo, sans système de fichiers) la partition réservée Microsoft ; p3 (ntfs, Windows) le système Windows réduit ; p4 (ntfs, WinRE) la récupération. sda, en iso9660, est la clé d'installation. Les 100 Go libérés ne sont pas une partition : lsblk ne les montre pas, l'installateur les affiche comme espace libre.",
            "Dans le partitionnement manuel : p1 reçoit le point de montage /boot/efi, case de formatage décochée ; dans l'espace libre, on crée la racine / en ext4 (le swap peut rester un fichier). On ne formate pas p1 (le chargeur de Windows serait effacé), on ne touche ni à p2, ni à p3, ni à p4, et on ne choisit pas « effacer le disque ».",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Le menu GRUB n'apparaît jamais",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_TROUBLE,
        context=(
            "Hier, tu as installé Ubuntu à côté de Windows 11 sur le PC d'un comptable. Ce matin, "
            "il appelle : le PC démarre directement sous Windows, Ubuntu « a disparu ». Depuis "
            "la session live de ta clé, tu relèves le début du document 1 (les deux dernières "
            "lignes sont la correction que tu proposes)."
        ),
        documents=(_console("Document 1 — efibootmgr (capture fictive)", *EFIBOOT_SCREEN),),
        instructions=(
            "Explique pourquoi Ubuntu ne démarre pas.",
            "Rédige la correction, son contrôle et ce que tu ne fais pas.",
        ),
        criteria=(
            _c("Explication", 1, f"Ubuntu est installé (entrée « ubuntu » présente) mais l'entrée démarrée en premier est « {E11_FIRST_BEFORE} » : le menu GRUB ne s'affiche pas."),
            _c("Correction", 1.5, f"sudo efibootmgr -o 0001,0000,0002 (ou ordre de démarrage du firmware) : « {E11_FIRST_AFTER} » en premier ; contrôle : redémarrage, menu GRUB proposant Ubuntu et Windows, les deux démarrent."),
            _c("À ne pas faire", 0.5, "Ne pas réinstaller Ubuntu ni toucher aux partitions ou à l'ESP."),
        ),
        correction=(
            f"L'entrée « ubuntu » existe : l'installation a réussi. Mais BootOrder commence par 0000, « {E11_FIRST_BEFORE} » : le firmware lance directement Windows et le menu GRUB, qui propose les deux systèmes, ne s'affiche jamais (certains firmwares remettent Windows en tête après une mise à jour).",
            f"On met l'entrée de Linux en premier : sudo efibootmgr -o 0001,0000,0002 (ou dans l'ordre de démarrage du firmware). « {E11_FIRST_AFTER} » passe en tête ; on redémarre et on vérifie que GRUB propose Ubuntu et Windows et que les deux démarrent. On ne réinstalle pas Ubuntu et on ne touche ni aux partitions ni à l'ESP.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Mode d'urgence après le remplacement du disque de données",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-09", "AP-13"),
        kind=KIND_TROUBLE,
        context=(
            "Sur le poste Linux d'un photographe, le disque dur de données (monté sur "
            "/mnt/photos) est tombé en panne. Un collègue l'a remplacé par un disque neuf, l'a "
            "formaté en ext4 et a restauré les photos depuis la sauvegarde. Au redémarrage, le "
            "PC affiche le mode d'urgence. Le document 1 rassemble ce que tu relèves."
        ),
        documents=(
            _console(
                "Document 1 — Démarrage, /etc/fstab et lsblk -f (fictif, abrégé)",
                f"[ TIME ] Timed out waiting for device /dev/disk/by-uuid/{_FSTAB_OLD_UUID}.",
                "[DEPEND] Dependency failed for /mnt/photos.",
                "[DEPEND] Dependency failed for Local File Systems.",
                "You are in emergency mode. After logging in, type \"journalctl -xb\" to view system logs,",
                "\"systemctl reboot\" to reboot, \"systemctl default\" or \"exit\" to boot into default mode.",
                "",
                "# grep photos /etc/fstab",
                f"UUID={_FSTAB_OLD_UUID} /mnt/photos ext4 defaults 0 2",
                "# lsblk -f /dev/sdb",
                "NAME   FSTYPE FSVER LABEL  UUID",
                "sdb",
                f"└─sdb1 ext4   1.0   photos {_FSTAB_NEW_UUID}",
            ),
        ),
        instructions=(
            "Explique la cause du mode d'urgence.",
            "Rédige la correction pas à pas, avec son contrôle et une précaution pour l'avenir.",
        ),
        criteria=(
            _c("Cause", 1, "Le formatage a créé un nouvel UUID ; /etc/fstab désigne encore l'ancien ; le montage de /mnt/photos échoue et bloque « Local File Systems »."),
            _c("Correction", 1.5, "Copie de sauvegarde de /etc/fstab ; remplacer l'UUID par celui de lsblk -f (c41d7e22-…) ; findmnt --verify puis mount -a ; systemctl daemon-reload ; redémarrage et contrôle de /mnt/photos."),
            _c("Précaution", 0.5, "Option nofail pour un disque de données non indispensable au démarrage ; mettre fstab à jour à chaque remplacement ou formatage."),
        ),
        correction=(
            "Formater le disque neuf lui a donné un nouvel UUID (c41d7e22-…), alors que /etc/fstab désigne encore l'UUID de l'ancien disque. Au démarrage, systemd attend ce disque introuvable : le montage de /mnt/photos échoue et, la ligne étant obligatoire, « Local File Systems » aussi : mode d'urgence. Le système et les photos ne sont pas en cause.",
            f"On se connecte (ou, si le compte root est verrouillé comme sous Ubuntu, on passe par la session live), on copie /etc/fstab (cp /etc/fstab /etc/fstab.bak), on remplace l'ancien UUID par {_FSTAB_NEW_UUID}, on vérifie avec findmnt --verify et mount -a, puis systemctl daemon-reload et redémarrage : /mnt/photos doit être monté. Pour un disque de données non indispensable au démarrage, l'option nofail évite le mode d'urgence ; on met fstab à jour à chaque remplacement.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Pas de Wi-Fi après l'installation",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-05"),
        kind=KIND_TROUBLE,
        context=(
            "Tu as installé Ubuntu sur un ancien MacBook Pro (Intel) qu'une association veut "
            "réutiliser. L'installation s'est faite sans réseau et sans cocher les logiciels "
            "tiers. Au bureau, aucun réseau Wi-Fi n'est proposé. Un adaptateur Ethernet USB et "
            "un câble sont disponibles. Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — lspci -nnk (fictif, abrégé)",
                "$ lspci -nnk | grep -A2 -i network",
                "03:00.0 Network controller [0280]: Broadcom Inc. and subsidiaries BCM4360 802.11ac Wireless Network Adapter [14e4:43a0] (rev 03)",
            ),
        ),
        instructions=(
            "Interprète le relevé.",
            "Rédige comment rétablir le Wi-Fi, avec le contrôle final.",
        ),
        criteria=(
            _c("Lecture", 1, "Carte Broadcom BCM4360 [14e4:43a0] ; aucune ligne « Kernel driver in use » : aucun pilote n'est chargé ; ce matériel demande un pilote non libre."),
            _c("Rétablir", 1.5, "Réseau par câble (adaptateur Ethernet) ; « Pilotes additionnels » (pilote Broadcom STA, paquet bcmwl-kernel-source) ou sudo apt install ; démarrage sécurisé : enrôler la clé MOK si demandé ; redémarrage."),
            _c("Contrôle", 0.5, "lspci -nnk affiche « Kernel driver in use: wl » ; réseaux Wi-Fi visibles ; connexion et ping."),
        ),
        correction=(
            "La carte réseau est une Broadcom BCM4360 (identifiant 14e4:43a0, 14e4 étant Broadcom). Sous la carte, aucune ligne « Kernel driver in use » : aucun pilote n'est chargé. Ce modèle demande un pilote non libre, qui n'est pas installé quand on décoche les logiciels tiers et qu'on installe sans réseau.",
            "On branche l'adaptateur Ethernet pour avoir Internet, puis on ouvre « Pilotes additionnels » et on choisit le pilote Broadcom STA (paquet bcmwl-kernel-source, installable aussi par sudo apt install) ; si le démarrage sécurisé est actif, on enrôle la clé MOK au redémarrage. Contrôle : lspci -nnk affiche « Kernel driver in use: wl », les réseaux Wi-Fi apparaissent, la connexion et un ping fonctionnent. Jamais de pilote d'un site inconnu.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="« Permission denied » sur ses propres fichiers",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_TROUBLE,
        context=(
            "Après l'installation de Debian sur le PC d'une traductrice, un stagiaire a restauré "
            "ses dossiers depuis le disque de sauvegarde avec sudo cp -r. Depuis, elle ne peut "
            "plus enregistrer ses traductions. Le stagiaire propose « chmod -R 777 sur tout le "
            "dossier personnel ». Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — Terminal de la traductrice (fictif)",
                "$ ls -l ~/Traductions",
                "-rw-r--r-- 1 root root 48213 Oct 14 09:12 contrat-2026.odt",
                "-rw-r--r-- 1 root root 31877 Oct 14 09:12 notice-pompe.odt",
                "$ touch ~/Traductions/test.odt",
                "touch: cannot touch '/home/anne/Traductions/test.odt': Permission denied",
            ),
        ),
        instructions=(
            "Explique la cause.",
            "Rédige la correction exacte et dis pourquoi tu refuses la proposition du stagiaire.",
        ),
        criteria=(
            _c("Cause", 0.75, "sudo cp -r a créé les fichiers au nom de root (propriétaire root, droits rw-r--r--) : anne peut lire mais pas écrire."),
            _c("Correction", 1, "sudo chown -R anne:anne /home/anne/Traductions (ou tout ce qui a été restauré) ; contrôle ls -l (propriétaire anne) et création d'un fichier ; à l'avenir, restaurer en tant qu'anne ou cp -a avec les bons propriétaires."),
            _c("Refus du 777", 0.25, "chmod -R 777 donne l'écriture à tous les comptes et rend les fichiers exécutables : faille et mauvaise pratique ; le problème est le propriétaire, pas les droits."),
        ),
        correction=(
            "ls -l montre que les fichiers appartiennent à root (propriétaire et groupe root, droits rw-r--r--) : restaurés avec sudo cp -r, ils ont été créés au nom de root. Anne peut les lire mais ni les modifier ni créer de fichier dans le dossier.",
            "On rend les fichiers à leur propriétaire : sudo chown -R anne:anne /home/anne/Traductions (et les autres dossiers restaurés), puis on contrôle (ls -l affiche anne, touch réussit). On refuse chmod -R 777 : il donnerait l'écriture à tous les comptes et rendrait tous les fichiers exécutables, alors que le problème est le propriétaire. À l'avenir, on restaure en tant qu'utilisatrice, ou on conserve les propriétaires (cp -a).",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Plus de place sur la racine",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "Un an après l'installation de Linux Mint sur le PC d'un club de football (racine de "
            "20 Go, choisie trop petite à l'époque), les mises à jour échouent. Le trésorier "
            "propose de supprimer « les gros dossiers de /usr ». Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — Terminal du club (fictif)",
                "$ sudo apt upgrade",
                "E: You don't have enough free space in /var/cache/apt/archives/.",
                "$ df -h /",
                "Filesystem      Size  Used Avail Use% Mounted on",
                "/dev/nvme0n1p2   20G   19G     0 100% /",
                "$ sudo du -sh /var/log /var/cache/apt /home",
                "4.2G    /var/log",
                "1.6G    /var/cache/apt",
                "9.8G    /home",
                "$ journalctl --disk-usage",
                "Archived and active journals take up 3.9G in the file system.",
            ),
        ),
        instructions=(
            "Interprète le relevé.",
            "Rédige le nettoyage sûr, dans l'ordre, puis la solution durable.",
        ),
        criteria=(
            _c("Lecture", 0.75, "Racine pleine (100 %, Avail 0) ; journaux 3,9 Go, cache apt 1,6 Go, /home 9,8 Go sur la même partition."),
            _c("Nettoyage", 1.5, "sudo apt clean ; sudo journalctl --vacuum-size=200M ; sudo apt autoremove ; puis apt upgrade ; contrôle df -h ; jamais de suppression dans /usr."),
            _c("Durable", 0.75, "Données de /home déplacées ou partition agrandie (session live, après sauvegarde) ; surveiller l'espace."),
        ),
        correction=(
            "La racine de 20 Go est pleine (Use% 100 %, Avail 0) : apt ne peut plus télécharger les paquets. Les journaux occupent 3,9 Go, le cache d'apt 1,6 Go et /home 9,8 Go, car /home est sur la même partition.",
            "Dans l'ordre : sudo apt clean (vide le cache des paquets téléchargés), sudo journalctl --vacuum-size=200M (réduit les journaux archivés), sudo apt autoremove (anciens noyaux et paquets inutiles), puis sudo apt upgrade et contrôle par df -h. On ne supprime rien dans /usr : le système deviendrait inutilisable. Solution durable : déplacer les données du club vers un autre support ou agrandir la partition depuis une session live, après sauvegarde vérifiée.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Rédiger le rapport d'intervention à partir des notes",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_POST,
        context=(
            "Tu as installé Ubuntu LTS à côté de Windows 11 sur le portable d'une journaliste. "
            "Tes notes : « accord signé le 21/10 ; 38 Go copiés sur disque USB, vérifiés ; clé "
            "BitLocker relevée ; démarrage rapide désactivé ; C: réduite de 120 Go depuis "
            "Windows ; ISO contrôlée OK ; ESP réutilisée non formatée ; / ext4 120 Go, swap en "
            "fichier ; à jour ; Wi-Fi OK ; Windows et Ubuntu démarrent ; batterie à 64 % »."
        ),
        instructions=("Rédige le rapport d'intervention en rubriques, à partir de ces notes.",),
        criteria=(
            _c("Rubriques", 1, "Demande et accord, poste, sauvegarde, actions, contrôles, remise, recommandations."),
            _c("Contenu", 1.5, "Chaque note à sa place sans rien inventer : accord du 21/10, 38 Go vérifiés, BitLocker et démarrage rapide, réduction de C:, ISO contrôlée, ESP non formatée, partitions, mises à jour, Wi-Fi, double démarrage contrôlé."),
            _c("Recommandations", 0.5, "Batterie usée (64 %) à surveiller ; sauvegarde régulière ; mises à jour des deux systèmes."),
        ),
        correction=(
            "Demande : ajout d'Ubuntu LTS à côté de Windows 11, accord écrit signé le 21/10. Poste : portable de la cliente (marque, modèle, numéro de série). Sauvegarde : 38 Go copiés sur disque USB, copie vérifiée ; clé de récupération BitLocker relevée. Actions : démarrage rapide désactivé, C: réduite de 120 Go depuis Windows, ISO contrôlée (sha256sum : OK), ESP existante réutilisée sans formatage, racine ext4 de 120 Go, swap en fichier.",
            "Contrôles : mises à jour installées, Wi-Fi fonctionnel, Windows et Ubuntu démarrent depuis le menu. Remise : explication du menu de démarrage et des mises à jour ; données vérifiées avec elle. Recommandations : batterie à 64 % de sa capacité d'origine, à surveiller ; sauvegarde régulière ; mises à jour des deux systèmes. Date et signatures.",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Corriger la procédure d'un collègue",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a installé Ubuntu à côté de Windows sur le PC d'un architecte et propose "
            "sa procédure comme modèle pour l'atelier. Ton responsable te demande de la relire "
            "avant de l'afficher. Elle est reproduite dans le document 1."
        ),
        documents=(
            _table(
                "Document 1 — Procédure proposée (fictive)",
                ("N°", "Étape"),
                ("1", "ISO téléchargée sur un site de partage, pas de contrôle : « c'est plus rapide »"),
                ("2", "Démarrage sécurisé désactivé « parce que Linux ne le supporte pas »"),
                ("3", "Dans le partitionnement manuel, ESP de Windows formatée « pour repartir propre »"),
                ("4", "Pas de sauvegarde : « on ne touche pas à Windows »"),
                ("5", "Travail quotidien du client dans une session root, « plus pratique »"),
                ("6", "chmod -R 777 /home « pour éviter les problèmes de droits »"),
                ("7", "PC rendu sans vérifier que Windows démarre encore"),
            ),
        ),
        instructions=("Relève les erreurs et rédige, pour chacune, la pratique correcte.",),
        criteria=(
            _c("Préparation", 1, "1 : image officielle, sha256sum -c « OK » ; 4 : sauvegarde vérifiée et accord écrit, un partitionnement peut toujours échouer."),
            _c("Installation", 1, "2 : Ubuntu, Debian, Fedora et Mint démarrent avec le démarrage sécurisé (shim signé) : le laisser actif ; 3 : ESP réutilisée sans formatage (sinon Windows ne démarre plus)."),
            _c("Remise", 1, "5 : compte personnel avec sudo, jamais de session root ; 6 : droits par défaut, propriétaires corrects (chown si besoin) ; 7 : contrôle des deux systèmes et liste de contrôle."),
        ),
        correction=(
            "1. Une image d'un site de partage peut être modifiée : image du site officiel, contrôlée par sha256sum -c (« OK »). 4. Même sans toucher volontairement à Windows, le partitionnement peut échouer : sauvegarde vérifiée et accord écrit d'abord. 2. Les grandes distributions démarrent avec le démarrage sécurisé grâce au chargeur shim signé : on le laisse actif. 3. Formater l'ESP de Windows efface son chargeur : on la réutilise sur /boot/efi sans formatage.",
            "5. Une session root permet de tout casser par erreur : compte personnel, sudo seulement pour l'administration. 6. chmod -R 777 /home donne à chacun l'accès aux fichiers des autres : on garde les droits par défaut et on corrige un propriétaire par chown si besoin. 7. On vérifie devant le client que Windows et Linux démarrent, on passe la liste de contrôle et on rédige le rapport.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions, 2 points chacune (réponses libres)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Choisir la distribution et le partitionnement d'un PC ancien",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-08"),
        kind=KIND_PREP,
        context=(
            "Une école de devoirs reçoit en don quatre PC de 2015 (processeur 64 bits, 4 Go de "
            "mémoire, SSD de 240 Go, firmware UEFI) dont Windows n'est plus maintenu. Les "
            "enfants y feront de la bureautique et des recherches sur Internet ; la coordinatrice "
            "veut un système gratuit, simple et maintenu plusieurs années. Les disques ont été "
            "effacés avec accord écrit."
        ),
        instructions=("Propose une distribution justifiée et le plan de partitions (avec le swap).",),
        criteria=(
            _c("Distribution", 1, "Distribution à support long avec un bureau léger (ex. Linux Mint Xfce, base Ubuntu LTS), justifiée par la mémoire de 4 Go, la simplicité et la durée de support."),
            _c("Partitions", 1, f"GPT en UEFI : ESP FAT32 sur /boot/efi, / en ext4 (au moins 25 Go, ici tout le reste ou / + /home), swap ≈ {X01_SWAP:g} Go (repère : autant que la mémoire, sans hibernation) en partition ou fichier."),
        ),
        correction=(
            "Une distribution à support long avec un bureau léger convient : par exemple Linux Mint Xfce (base Ubuntu LTS), gratuite, simple, maintenue plusieurs années et sobre en mémoire avec 4 Go.",
            f"Plan en GPT (firmware UEFI) : une partition système EFI en FAT32 montée sur /boot/efi, la racine / en ext4 (au moins 25 Go ; ici le reste du disque, ou / et /home séparées), et un swap d'environ {X01_SWAP:g} Go (repère du cours : autant que la mémoire entre 2 et 8 Go, sans hibernation), en partition ou en fichier.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Plan de partitions d'un poste de développement",
        question_type="long_answer",
        requirement_ids=("AP-10",),
        kind=KIND_INSTALL,
        context=(
            "Un développeur indépendant fait installer Linux seul sur un PC neuf (SSD NVMe de "
            "1 To, 16 Go de mémoire, firmware UEFI). Il veut pouvoir réinstaller le système plus "
            "tard sans toucher à ses projets, et n'utilise jamais l'hibernation. Tu dois remettre "
            "un plan de partitionnement manuel justifié."
        ),
        instructions=("Rédige le plan (partition, système de fichiers, point de montage, taille) et justifie chaque choix.",),
        criteria=(
            _c("Plan", 1.25, f"GPT ; ESP FAT32 ≈ 300 Mo-1 Go sur /boot/efi ; / ext4 (ex. 60-100 Go) ; /home ext4 pour le reste ; swap ≈ {X02_SWAP:g} Go (sans hibernation) en partition ou fichier."),
            _c("Justification", 0.75, f"/home séparée : réinstaller en reformatant / seulement ; ESP lue par le firmware ; swap modeste car pas d'hibernation (avec hibernation, ≈ {X02_SWAP_HIB:g} Go)."),
        ),
        correction=(
            f"Disque en GPT (UEFI). 1) Partition système EFI en FAT32, ≈ 300 Mo à 1 Go, montée sur /boot/efi : le firmware y lit le chargeur. 2) Racine / en ext4, par exemple 60 à 100 Go pour le système et les outils de développement. 3) /home en ext4 sur le reste du disque. 4) Swap d'environ {X02_SWAP:g} Go, en partition ou en fichier.",
            f"/home séparée permet de réinstaller en reformatant uniquement / et en remontant /home sans la formater (après sauvegarde quand même). Avec 16 Go de mémoire et sans hibernation, un swap modeste suffit (repère du cours : au moins 4 Go) ; avec hibernation, il faudrait environ {X02_SWAP_HIB:g} Go.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Préparer un double démarrage avec un Windows chiffré",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Une infirmière veut garder Windows 11 (chiffré par BitLocker, SSD de 512 Go dont "
            "300 Go libres) et ajouter Ubuntu pour ses études. Elle a signé l'accord. Un "
            "collègue propose de démarrer directement sur la clé et de choisir « Installer à côté "
            "de Windows » sans autre préparation."
        ),
        instructions=("Rédige la préparation complète, dans l'ordre, avant de démarrer sur la clé, en justifiant.",),
        criteria=(
            _c("Données", 0.75, "Sauvegarde vérifiée des données (un redimensionnement peut échouer) ; clé de récupération BitLocker relevée hors du PC."),
            _c("Windows", 1.25, "Désactiver le démarrage rapide ; réduire C: depuis Windows (Gestion des disques, ex. 100 Go) ; image ISO officielle contrôlée ; ensuite seulement la clé, ESP réutilisée sans formatage."),
        ),
        correction=(
            "1) Sauvegarder ses données sur un support externe et vérifier la copie : modifier les partitions peut échouer. 2) Relever la clé de récupération BitLocker et la conserver hors du PC : changer le démarrage peut la faire demander. 3) Désactiver le démarrage rapide de Windows, qui laisse la partition dans un état d'hibernation.",
            "4) Réduire C: depuis Windows (Gestion des disques, « Réduire le volume », par exemple 100 Go), ce que Windows sait faire, même sur un volume chiffré. 5) Télécharger l'image officielle et la contrôler (sha256sum -c ou équivalent : OK). Ensuite seulement : démarrer sur la clé, installer dans l'espace libre et réutiliser l'ESP sans la formater.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="L'installateur ne voit pas le SSD",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "Sur un portable récent, Windows 11 est à supprimer (accord écrit, données "
            "sauvegardées) pour une installation de Linux seul. L'installateur d'Ubuntu affiche "
            "un avertissement « Intel RST » et ne propose aucun disque. Le firmware liste "
            "pourtant le SSD NVMe ; le contrôleur est réglé sur « RAID / Intel RST »."
        ),
        instructions=("Explique la cause et la solution adaptée à ce cas, avec la précaution si Windows avait dû être gardé.",),
        criteria=(
            _c("Cause et solution", 1.25, "Le SSD est sain (vu par le firmware) ; le contrôleur en RAID/Intel RST masque le disque à l'installateur ; ici (Windows à supprimer, accord, sauvegarde) : passer le contrôleur en AHCI dans le firmware si la notice le permet, puis installer."),
            _c("Précaution", 0.75, "Windows à garder : préparer d'abord Windows au passage en AHCI (procédure Microsoft, démarrage en mode sans échec) ; sinon INACCESSIBLE_BOOT_DEVICE."),
        ),
        correction=(
            "Le firmware voit le SSD : il n'est pas en panne. Le contrôleur fonctionne en mode RAID / Intel RST, qui masque le disque à l'installateur. Ici, Windows est supprimé avec accord écrit et sauvegarde : on passe le contrôleur en AHCI dans le firmware (si la notice du fabricant le permet), puis on relance l'installation.",
            "Si Windows avait dû être gardé, on aurait d'abord préparé Windows au changement de mode selon la procédure de Microsoft (redémarrage en mode sans échec) ; changer le mode sans préparation l'empêche de démarrer (INACCESSIBLE_BOOT_DEVICE, PR08).",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Le pilote NVIDIA ne se charge pas",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-05"),
        kind=KIND_TROUBLE,
        context=(
            "Sur la station d'un vidéaste, tu as installé Ubuntu avec le démarrage sécurisé actif, "
            "puis le pilote NVIDIA par « Pilotes additionnels ». L'installation a demandé un mot "
            "de passe ; au redémarrage, un écran bleu « Perform MOK management » est apparu et le "
            "vidéaste a choisi « Continue boot ». Depuis, l'affichage reste en basse résolution "
            "et tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — Terminal (fictif)",
                "$ mokutil --sb-state",
                "SecureBoot enabled",
                "$ nvidia-smi",
                "NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.",
                "Make sure that the latest NVIDIA driver is installed and running.",
            ),
        ),
        instructions=("Explique la cause et rédige la correction, sans désactiver le démarrage sécurisé.",),
        criteria=(
            _c("Cause", 1, "Le module NVIDIA est signé avec une clé locale (MOK) non enrôlée, car « Continue boot » a sauté l'enrôlement ; avec le démarrage sécurisé actif, le noyau refuse de le charger."),
            _c("Correction", 1, "Relancer l'enrôlement (réinstaller le pilote par « Pilotes additionnels » ou sudo update-secureboot-policy --enroll-key), redémarrer, « Enroll MOK », saisir le mot de passe ; contrôle nvidia-smi ; démarrage sécurisé laissé actif."),
        ),
        correction=(
            "Le démarrage sécurisé est actif et le pilote NVIDIA, compilé sur le PC, est signé avec une clé locale (MOK) qui devait être enrôlée au redémarrage. En choisissant « Continue boot », le vidéaste a sauté l'enrôlement : le noyau refuse de charger un module signé par une clé inconnue, d'où l'échec de nvidia-smi et l'affichage de base.",
            "On relance l'enrôlement : réinstallation du pilote par « Pilotes additionnels » (ou, sous Ubuntu, sudo update-secureboot-policy --enroll-key), un mot de passe temporaire est demandé ; au redémarrage, dans « Perform MOK management », on choisit « Enroll MOK », on confirme et on saisit ce mot de passe. Contrôle : nvidia-smi affiche la carte, résolution native. On ne désactive pas le démarrage sécurisé.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Pas de réseau filaire après l'installation",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "Tu viens d'installer Debian sur un PC de bureau d'une librairie, relié au réseau par "
            "câble. Le bureau indique « Câble débranché » ; la libraire suggère de réinstaller en "
            "cochant d'autres options. Le PC voisin, branché sur la même prise murale avec un "
            "autre câble, a Internet. Tu relèves le document 1."
        ),
        documents=(
            _console(
                "Document 1 — ip a (fictif, abrégé)",
                "$ ip a",
                "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN",
                "    inet 127.0.0.1/8 scope host lo",
                "2: enp3s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN",
                "    link/ether 3c:7c:3f:1a:2b:4d brd ff:ff:ff:ff:ff:ff",
            ),
        ),
        instructions=("Interprète le relevé et rédige le diagnostic dans l'ordre, jusqu'au contrôle.",),
        criteria=(
            _c("Lecture", 0.75, "enp3s0 a un pilote (interface présente, adresse MAC) mais NO-CARRIER / state DOWN : aucun lien électrique ; pas d'adresse IPv4 ; ce n'est pas l'installation."),
            _c("Diagnostic", 1.25, "Couche physique d'abord : câble bien enfoncé, câble testé ou remplacé (celui du voisin), voyants du port ; puis lien UP, adresse obtenue par DHCP (ip a), passerelle (ip route), ping de la passerelle puis d'un nom ; pas de réinstallation."),
        ),
        correction=(
            "L'interface enp3s0 existe et a une adresse MAC : son pilote est chargé. Mais NO-CARRIER et state DOWN signifient qu'aucun lien n'est détecté sur le câble : la carte ne « voit » rien au bout. Elle n'a donc pas d'adresse IPv4. La prise murale fonctionne (le voisin a Internet) : on soupçonne le câble ou son branchement, pas l'installation.",
            "On procède par couches : câble bien enfoncé des deux côtés, voyants du port, câble remplacé (par exemple celui du voisin, qui fonctionne). Quand le lien est UP, on vérifie l'adresse obtenue par DHCP (ip a), la route par défaut (ip route), un ping de la passerelle puis d'un nom (DNS). On ne réinstalle pas : le système n'est pas en cause.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Une utilisatrice qui ne peut pas utiliser sudo",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_POST,
        context=(
            "Dans un cabinet de deux associés, tu as installé Ubuntu avec le compte "
            "administrateur de Paul, puis créé le compte de Marie, gérante du cabinet, qui doit "
            "pouvoir installer des logiciels. Elle obtient « marie is not in the sudoers file » "
            "en lançant sudo apt install. Le stagiaire veut lui donner le mot de passe de root."
        ),
        instructions=("Explique la cause et rédige la correction, avec son contrôle.",),
        criteria=(
            _c("Cause", 0.75, "Le compte de Marie n'est pas membre du groupe sudo : seul le compte créé à l'installation l'est par défaut."),
            _c("Correction", 1.25, "Depuis le compte de Paul : sudo usermod -aG sudo marie (ou Paramètres → Utilisateurs → administrateur) ; Marie se reconnecte ; contrôle groups ; pas de mot de passe root partagé ; seulement parce qu'elle doit administrer."),
        ),
        correction=(
            "Sous Ubuntu, seul le compte créé à l'installation est administrateur (membre du groupe sudo). Le compte de Marie, créé ensuite comme compte standard, ne figure pas dans ce groupe : sudo refuse.",
            "Puisqu'elle doit administrer, on l'ajoute au groupe depuis le compte de Paul : sudo usermod -aG sudo marie (ou Paramètres → Utilisateurs → type « Administrateur »). Elle se déconnecte puis se reconnecte ; groups doit afficher sudo. On ne partage pas de mot de passe root (sous Ubuntu, root n'a d'ailleurs pas de mot de passe utilisable) : chaque action reste au nom de la personne.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Un disque désigné par /dev/sdb1 dans fstab",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-09"),
        kind=KIND_TROUBLE,
        context=(
            "Sur un serveur Debian de partage de documents, un technicien avait ajouté le disque "
            "d'archives dans /etc/fstab (document 1). Depuis qu'un second disque a été ajouté, "
            "/srv/archives contient parfois les fichiers de l'autre disque, et un jour le "
            "serveur est resté en mode d'urgence."
        ),
        documents=(
            _console(
                "Document 1 — Extrait de /etc/fstab (fictif)",
                "# <file system> <mount point> <type> <options> <dump> <pass>",
                "UUID=8e2f41c0-6d3a-4b9e-91f7-0c5a2d7e3b64 / ext4 errors=remount-ro 0 1",
                "/dev/sdb1 /srv/archives ext4 defaults 0 2",
            ),
        ),
        instructions=("Explique le problème et rédige la correction sûre, avec son contrôle.",),
        criteria=(
            _c("Problème", 0.75, "Les noms /dev/sdX dépendent de l'ordre de détection : avec un second disque, sdb1 peut désigner l'autre disque ou ne pas exister ; d'où le mauvais montage et le mode d'urgence."),
            _c("Correction", 1.25, "Copie de /etc/fstab ; UUID du disque d'archives relevé par lsblk -f ou blkid ; ligne UUID=… /srv/archives ext4 defaults,nofail 0 2 ; findmnt --verify, mount -a, systemctl daemon-reload ; contrôle du contenu de /srv/archives et redémarrage."),
        ),
        correction=(
            "La ligne désigne le disque par /dev/sdb1. Ces noms suivent l'ordre de détection des disques : depuis l'ajout du second disque, sdb1 peut désigner l'autre disque (d'où les mauvais fichiers dans /srv/archives) ou ne pas exister au démarrage (d'où le mode d'urgence).",
            "On copie /etc/fstab, on relève l'UUID du système de fichiers d'archives (lsblk -f ou blkid), on remplace la ligne par UUID=<uuid relevé> /srv/archives ext4 defaults,nofail 0 2 (nofail : le serveur démarre même si ce disque manque). Contrôle : findmnt --verify, mount -a, systemctl daemon-reload, puis vérification du contenu de /srv/archives et redémarrage.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="La liste de contrôle avant de rendre un PC sous Linux",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_POST,
        context=(
            "Ton responsable veut une liste de contrôle à passer avec le client avant de rendre "
            "un PC où l'on a installé Linux (seul ou à côté de Windows). Elle doit tenir sur une "
            "demi-page, citer pour chaque point la commande ou l'outil utilisé et le résultat "
            "attendu, et servir de base au rapport d'intervention."
        ),
        instructions=("Rédige cette liste de contrôle (au moins six points : commande ou outil, et résultat attendu).",),
        criteria=(
            _c("Système", 1, "Démarrage (efibootmgr, redémarrages, Windows proposé si double démarrage) ; mokutil --sb-state ; lsblk -f / findmnt --verify ; df -h ; mises à jour à jour."),
            _c("Usage", 1, "Pilotes (lspci -k, Pilotes additionnels) ; réseau (ip a, ping) ; systemctl --failed ; comptes (groups, sudo pour l'administrateur seulement) ; données vérifiées avec le client."),
        ),
        correction=(
            "Système : démarrage contrôlé par plusieurs redémarrages et efibootmgr (entrée de Linux en premier, Windows proposé en double démarrage) ; mokutil --sb-state, « SecureBoot enabled » ; lsblk -f et findmnt --verify, partitions montées sans erreur ; df -h, espace libre suffisant ; sudo apt update && sudo apt upgrade, rien en attente.",
            "Usage : lspci -k, pilote chargé pour le réseau et le graphique ; ip a et ping, réseau et noms résolus ; systemctl --failed, aucun service en échec ; groups, sudo réservé à l'administrateur ; données et logiciels du client vérifiés devant lui. Chaque résultat est reporté dans le rapport.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="« Effacer le disque » pour un double démarrage",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Un client a demandé par écrit d'ajouter Linux Mint « à côté de Windows, sans rien "
            "perdre ». Au moment du type d'installation, la stagiaire sélectionne « Effacer le "
            "disque et installer Linux Mint » parce que l'option « à côté » n'apparaît pas. "
            "La sauvegarde des données n'a pas encore été faite."
        ),
        instructions=("Dis ce que tu fais immédiatement et rédige la marche à suivre, en justifiant.",),
        criteria=(
            _c("Arrêt", 1, "Arrêter avant de valider : « Effacer le disque » supprime Windows et les données, contraire à la demande écrite ; aucune modification sans sauvegarde vérifiée."),
            _c("Marche à suivre", 1, "Sauvegarde vérifiée ; chercher pourquoi l'option manque (pas d'espace libre, démarrage rapide/BitLocker, mode de démarrage de la clé ≠ Windows) ; réduire C: depuis Windows ; partitionnement manuel (ESP non formatée)."),
        ),
        correction=(
            "On arrête avant de valider : « Effacer le disque » supprimerait Windows et toutes les données, alors que la demande écrite est d'ajouter Linux sans rien perdre. Et rien ne se modifie sur le disque sans sauvegarde vérifiée.",
            "On sauvegarde d'abord et on vérifie la copie. On cherche ensuite pourquoi l'option « à côté » n'apparaît pas : pas d'espace libre, Windows en démarrage rapide ou chiffré, clé démarrée dans un autre mode que Windows (hérité au lieu d'UEFI). On réduit C: depuis Windows, on redémarre la clé en « UEFI: » et on utilise l'option « à côté » ou le partitionnement manuel (ESP réutilisée sans formatage).",
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

"""PR07 « Systèmes d'exploitation, GUI/CLI et prérequis d'installation » — exercices corrigés
et mini-examen (ticket #207).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item, et `app.v1.ampcr_pratique_pr04_bank`, dont il réutilise les
petits constructeurs) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre, classements (fonctions du système, édition de
  Windows, compatibilité Windows 11, installation propre ou mise à niveau), lecture de captures,
  choix d'un système, licences, architecture, média, pilotes, virtualisation, plan à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et captures sont **fictives** ; prérequis, verdicts, éditions et choix
d'installation viennent de `app.v1.ampcr_pratique_pr07_figures` (mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr07_figures import (
    BOOT_LEGACY_ENTRY,
    BOOT_UEFI_ENTRY,
    CHECK_STEPS,
    EDITION_FEATURES,
    EDITION_HOME,
    EDITION_PRO,
    FN_ACCOUNTS,
    FN_DRIVER,
    FN_FS,
    FN_INTERFACE,
    FN_KERNEL,
    FN_SERVICE,
    INSTALL_CHOICES,
    INSTALL_PLAN_STEPS,
    LIVE_CHECK_SCREEN,
    MEDIA_STEPS,
    W11_VERDICTS,
    PcSpec,
    edition_needed,
    install_type,
    usable_ram_gib,
    vm_plan,
    win11_check,
)

PR07_CODE = "PR07"

KIND_ORDER = "ordonnancement"
KIND_CHOICE = "choix du système et de l'installation"
KIND_PREREQ = "prérequis et firmware"
KIND_TOOLS = "outils GUI/CLI et captures"
KIND_ERROR = "repérage d'erreurs"

# Exigences officielles du cours (matrice #192, audit #236) : chaque item en cite au moins une.
REQ = frozenset({"AP-08", "AP-12"})

# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(INSTALL_PLAN_STEPS)
E02_STEPS = _labels(MEDIA_STEPS)
E03_STEPS = _labels(CHECK_STEPS)

E04_CATEGORIES = (FN_KERNEL, FN_DRIVER, FN_FS, FN_ACCOUNTS, FN_SERVICE, FN_INTERFACE)
E04_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Partage le temps du processeur entre le navigateur, le traitement de texte et l'antivirus", FN_KERNEL),
    ("Traduit les ordres du système pour la carte Wi-Fi d'un modèle précis", FN_DRIVER),
    ("Mémorise dans quels blocs du disque se trouve un fichier et qui peut le modifier", FN_FS),
    ("Empêche l'utilisateur « stagiaire » d'installer un programme sans mot de passe administrateur", FN_ACCOUNTS),
    ("Garde en file et envoie les impressions en arrière-plan, sans fenêtre", FN_SERVICE),
    ("Permet de taper ipconfig /all ou ip a pour lire la configuration réseau", FN_INTERFACE),
    ("Réserve une zone de mémoire vive à chaque programme et l'empêche de lire celle des autres", FN_KERNEL),
    ("Logiciel du fabricant à installer pour que l'imprimante soit reconnue", FN_DRIVER),
)

E05_CATEGORIES = (EDITION_HOME, EDITION_PRO)
E05_ELEMENTS: tuple[str, ...] = tuple(need for need, _home in EDITION_FEATURES)
E05_CORRECT = tuple(E05_CATEGORIES.index(edition_needed((need,))) for need in E05_ELEMENTS)


def _pc(cpu: str, *, listed: bool = True, bits64: bool = True, cores: int = 4, ghz: float = 2.5, ram: int = 8,
        storage: int = 256, uefi: bool = True, mode: str = "UEFI", sb: bool = True, tpm: float = 2.0,
        tpm_on: bool = True, table: str = "GPT") -> PcSpec:
    return PcSpec(cpu=cpu, cpu_64bit=bits64, cpu_listed=listed, cores=cores, ghz=ghz, ram_gb=ram,
                  storage_gb=storage, uefi_capable=uefi, firmware_mode=mode, secure_boot_on=sb,
                  tpm_version=tpm, tpm_enabled=tpm_on, disk_table=table)


# (description donnée au candidat, fiche correspondante)
E06_PCS: tuple[tuple[str, PcSpec], ...] = (
    ("Portable de 2023, processeur de la liste, 16 Go, SSD 512 Go, UEFI, démarrage sécurisé activé, TPM 2.0 actif",
     _pc("portable 2023", ram=16, storage=512)),
    ("Tour de 2019, processeur de la liste, 8 Go, SSD 256 Go, firmware UEFI réglé en mode hérité (CSM), disque MBR, TPM 2.0 actif",
     _pc("tour 2019", mode="Hérité", sb=False, table="MBR")),
    ("PC de 2014, processeur 64 bits absent de la liste, 8 Go, SSD 240 Go, UEFI, TPM 1.2",
     _pc("PC 2014", listed=False, tpm=1.2, storage=240)),
    ("Mini-PC de 2021, processeur de la liste, 8 Go, SSD 256 Go, UEFI, TPM intégré (fTPM) désactivé dans le firmware",
     _pc("mini-PC 2021", tpm_on=False)),
    ("Portable de 2022, processeur de la liste, 4 Go, eMMC de 32 Go, UEFI, TPM 2.0 actif",
     _pc("portable 2022", ram=4, storage=32)),
    ("PC de bureau de 2020, processeur de la liste, 16 Go, SSD 1 To, UEFI, TPM 2.0 actif, démarrage sécurisé désactivé",
     _pc("bureau 2020", ram=16, storage=1000, sb=False)),
)
E06_RESULTS = tuple(win11_check(pc) for _d, pc in E06_PCS)
E06_CORRECT = tuple(W11_VERDICTS.index(verdict) for verdict, _b, _s in E06_RESULTS)

# (situation, sauvegarde, prérequis, même famille et architecture, système sain, garder les programmes)
E07_CASES: tuple[tuple[str, bool, bool, bool, bool, bool], ...] = (
    ("PC compatible sous Windows 10 64 bits en bon état ; la cliente veut Windows 11 en gardant tous ses logiciels",
     True, True, True, True, True),
    ("PC sous Windows 10 32 bits avec 8 Go de mémoire ; passer à Windows 11, qui n'existe qu'en 64 bits",
     True, True, False, True, True),
    ("PC sous Windows 11 infecté, qui affiche des erreurs à chaque démarrage ; données sauvegardées",
     True, True, True, False, True),
    ("Ancien PC sous Windows à remplacer par Linux Mint pour une association",
     True, True, False, True, False),
    ("PC de 2013 (processeur absent de la liste, TPM 1.2) dont le client veut Windows 11",
     True, False, True, True, True),
    ("Nouveau disque SSD vide installé dans un PC compatible : le client veut « un Windows tout neuf »",
     True, True, True, True, False),
)
E07_CORRECT = tuple(
    INSTALL_CHOICES.index(install_type(backup_ok=b, requirements_ok=r, same_family_and_arch=f,
                                       system_healthy=h, keep_programs=k))
    for _s, b, r, f, h, k in E07_CASES
)

E11_USABLE = usable_ram_gib(8, 32)
E15_LEFT, E15_OK = vm_plan(16, (4, 2))

X02_PC = _pc("tour 2017", listed=False, tpm=2.0)
X02_VERDICT, X02_BLOCKERS, _X02_SETTINGS = win11_check(X02_PC)
X08_LEFT, X08_OK = vm_plan(8, (4,))

# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le plan d'installation d'un poste",
        question_type="ordering",
        requirement_ids=("AP-08", "AP-10", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Une agence de voyages remplace le système de son poste d'accueil. Ton responsable "
            "veut, dans le dossier d'intervention, le plan complet de l'installation, de la "
            "protection des données au rapport final. Le stagiaire a noté les huit étapes, "
            "mais dans le désordre."
        ),
        instructions=("Remets les huit étapes dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 4, "Sauvegarder → relever licences et pilotes → préparer le média → régler le firmware → installer → installer les pilotes → sécuriser → contrôler et documenter (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Sauvegarder et vérifier la copie, avec l'accord écrit du client : l'installation efface la partition du système. 2. Relever l'édition, la clé ou la licence numérique et préparer les pilotes réseau et stockage : sans eux, l'installateur peut ne voir ni disque ni réseau. 3. Préparer le média à partir d'une image officielle contrôlée. 4. Régler le firmware (UEFI, démarrage sécurisé, TPM, menu de démarrage).",
            "5. Installer sur le disque identifié ; l'installateur crée les partitions GPT et l'ESP. 6. Installer les pilotes manquants. 7. Sécuriser : compte administrateur et compte standard, mises à jour, antivirus, pare-feu, chiffrement. 8. Contrôler (activation, réseau, données restaurées) et rédiger le rapport.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (4, 1, 7, 2, 0, 6, 3, 5)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la préparation d'une clé d'installation",
        question_type="ordering",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_ORDER,
        context=(
            "Tu prépares une clé USB d'installation d'Ubuntu pour un PC UEFI de l'atelier. Le "
            "site de la distribution publie l'image ISO et sa somme SHA-256. La seule clé "
            "disponible contient les photos d'un collègue. Les étapes de ta fiche ont été "
            "mélangées."
        ),
        instructions=("Remets les cinq étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 2.5, "Télécharger l'image → contrôler la somme → préparer la clé (sauvegarde des photos) → écrire la clé → tester le démarrage (0,5 pt par étape)."),
        ),
        correction=(
            "1. Télécharger l'image sur le site officiel. 2. Calculer sa somme SHA-256 (Get-FileHash sous Windows, sha256sum sous Linux) et la comparer à celle publiée : une différence = image corrompue ou modifiée, on ne l'utilise pas. 3. Préparer la clé : les photos du collègue sont copiées ailleurs et vérifiées, car l'écriture efface tout.",
            "4. Écrire l'image sur la clé avec un outil adapté (Rufus en schéma GPT pour un PC UEFI, balenaEtcher, ou dd sous Linux). 5. Tester : dans le menu de démarrage, l'entrée « UEFI: » de la clé doit lancer l'installateur.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (3, 0, 4, 2, 1)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la vérification des prérequis",
        question_type="ordering",
        requirement_ids=("AP-08", "AP-17"),
        kind=KIND_ORDER,
        context=(
            "Un cabinet d'architectes demande si ses six PC de dessin peuvent passer à un "
            "nouveau système. Avant de répondre, tu rédiges la démarche de vérification que "
            "chaque technicien suivra pour chaque PC. Les six étapes ont été notées dans le "
            "désordre."
        ),
        instructions=("Remets les six étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Relever le besoin → relever le matériel → relever le firmware → comparer aux prérequis → vérifier les pilotes → conclure par écrit (0,5 pt par étape)."),
        ),
        correction=(
            "1. Le besoin d'abord (logiciel de dessin, périphériques, domaine) : il décide du système et de l'édition. 2. Relever le matériel (processeur 64 bits, cœurs, mémoire, stockage). 3. Relever le firmware (mode UEFI ou hérité, démarrage sécurisé, TPM). 4. Comparer à la page officielle de l'éditeur pour la version visée.",
            "5. Vérifier que le fabricant fournit les pilotes (carte graphique, réseau, traceur) pour ce système. 6. Conclure par écrit pour chaque PC : compatible, compatible après réglages, ou non compatible avec une alternative.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 5, 0, 3, 1, 4)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Quelle partie du système fait ce travail ?",
        question_type="classification",
        requirement_ids=("AP-08", "AP-05", "AP-12"),
        kind=KIND_TOOLS,
        context=(
            "Pour expliquer à un nouveau collègue comment fonctionne un système "
            "d'exploitation, tu prépares une fiche. Elle décrit huit tâches observées sur un "
            "PC de bureau ; il faut indiquer, pour chacune, quelle partie du système "
            "d'exploitation s'en charge."
        ),
        instructions=("Range chacune des huit tâches dans la partie du système qui l'assure.",),
        criteria=(
            _c("Classement", 4, "Noyau : temps processeur, mémoire protégée. Pilote : carte Wi-Fi, imprimante. Système de fichiers : emplacement et droits d'un fichier. Comptes et droits : stagiaire sans droit d'installer. Service : file d'impression. Interface : ipconfig / ip a (0,5 pt par élément)."),
        ),
        correction=(
            "Le noyau partage le processeur entre les programmes et réserve à chacun sa zone de mémoire, sans qu'un programme puisse lire celle d'un autre. Le pilote traduit les ordres du système pour un matériel précis : la carte Wi-Fi, l'imprimante. Le système de fichiers sait où se trouve chaque fichier et enregistre ses droits.",
            "La gestion des comptes empêche un compte standard d'installer un programme sans mot de passe administrateur. Le service d'impression (spouleur) travaille en arrière-plan sans fenêtre. La ligne de commande est une interface : on y tape ipconfig /all (Windows) ou ip a (Linux).",
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
        title="Windows 11 Famille suffit-il ?",
        question_type="classification",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Une PME achète des PC et hésite entre Windows 11 Famille, moins cher, et Windows "
            "11 Professionnel. Le gérant a listé huit besoins exprimés par ses employés. Pour "
            "chacun, il veut savoir si l'édition Famille suffit ou si l'édition "
            "Professionnel est nécessaire."
        ),
        instructions=("Range chaque besoin dans l'édition minimale qui le couvre.",),
        criteria=(
            _c("Classement", 4, "Famille : navigateur et bureautique, Defender et mises à jour, client Bureau à distance. Professionnel : domaine Active Directory, BitLocker et sa console, hôte Bureau à distance, Hyper-V, gpedit.msc (0,5 pt par élément)."),
        ),
        correction=(
            "L'édition Famille couvre l'usage courant : navigation, bureautique, jeux, sécurité de base (Microsoft Defender, pare-feu, Windows Update) et même la connexion à un autre PC avec le client Bureau à distance.",
            "Les fonctions d'entreprise demandent l'édition Professionnel : joindre un domaine Active Directory, gérer BitLocker, être pris en main comme hôte Bureau à distance, Hyper-V et l'Éditeur de stratégie de groupe locale. Une PME avec un serveur de domaine choisit donc Professionnel.",
        ),
        classification=Classification(categories=E05_CATEGORIES, elements=E05_ELEMENTS, correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Six PC face aux prérequis de Windows 11",
        question_type="classification",
        requirement_ids=("AP-08", "AP-02", "AP-17"),
        kind=KIND_PREREQ,
        context=(
            "Une école veut savoir quels PC de son parc peuvent passer à Windows 11. Rappel des "
            "prérequis publiés par Microsoft : processeur 64 bits de la liste de compatibilité "
            "(2 cœurs, 1 GHz), 4 Go de mémoire, 64 Go de stockage, firmware UEFI compatible "
            "démarrage sécurisé, TPM 2.0. Le démarrage sécurisé doit être pris en charge ; "
            "l'activer est recommandé."
        ),
        instructions=("Range chaque PC : compatible tel quel, compatible après réglages du firmware, ou non compatible.",),
        criteria=(
            _c("Classement", 3, "Tel quel : portable 2023, bureau 2020 (démarrage sécurisé seulement désactivé : à activer, recommandé). Après réglages : tour 2019 (mbr2gpt puis UEFI), mini-PC 2021 (activer le fTPM). Non compatible : PC 2014 (processeur hors liste, TPM 1.2), portable 2022 (4 Go mais 32 Go de stockage) (0,5 pt par élément)."),
        ),
        correction=(
            "Compatibles tels quels : le portable de 2023 ; le PC de bureau de 2020, dont le démarrage sécurisé est pris en charge mais désactivé : on recommande de l'activer, ce n'est pas un blocage. Compatibles après réglages : la tour de 2019 (disque converti en GPT avec mbr2gpt après sauvegarde, puis firmware en mode UEFI) et le mini-PC de 2021 (activer le TPM intégré dans le firmware).",
            "Non compatibles : le PC de 2014 (processeur absent de la liste, TPM 1.2 seulement) et le portable de 2022, dont le stockage de 32 Go est sous les 64 Go exigés. Pour eux : rester sur un système pris en charge, Linux, ou remplacement.",
        ),
        classification=Classification(
            categories=W11_VERDICTS,
            elements=tuple(d for d, _pc2 in E06_PCS),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Installation propre ou mise à niveau ?",
        question_type="classification",
        requirement_ids=("AP-08", "AP-10", "AP-C03"),
        kind=KIND_CHOICE,
        context=(
            "Six demandes arrivent à l'atelier. Pour chacune, les données ont déjà été "
            "sauvegardées et la copie vérifiée. Il reste à choisir la démarche : mise à "
            "niveau sur place (programmes et réglages conservés), installation propre "
            "(système neuf), ou ni l'une ni l'autre (le PC ne peut pas recevoir le système "
            "voulu)."
        ),
        instructions=("Range chaque demande dans la démarche à appliquer.",),
        criteria=(
            _c("Classement", 3, "Mise à niveau : Windows 10 64 bits sain vers Windows 11 en gardant les logiciels. Installation propre : 32 → 64 bits, PC infecté, passage à Linux Mint, SSD neuf. Ni l'une ni l'autre : PC de 2013 hors prérequis (0,5 pt par élément)."),
        ),
        correction=(
            "La mise à niveau sur place ne convient que si le PC est compatible, le système sain, la famille et l'architecture identiques, et que le client veut garder ses programmes : c'est le cas de la cliente sous Windows 10 64 bits.",
            "Installation propre : on ne passe pas de 32 à 64 bits ni de Windows à Linux par une mise à niveau ; un système infecté garderait ses problèmes ; un SSD vide n'a rien à mettre à niveau. Le PC de 2013 ne respecte pas les prérequis de Windows 11 : ni l'une ni l'autre, on propose un autre système ou un remplacement.",
        ),
        classification=Classification(
            categories=INSTALL_CHOICES,
            elements=tuple(s for s, *_rest in E07_CASES),
            correct=E07_CORRECT,
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Lire Informations système avant de passer à Windows 11",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-02", "AP-12"),
        kind=KIND_PREREQ,
        context=(
            "Un comptable veut passer son PC de bureau de Windows 10 à Windows 11 en gardant "
            "ses logiciels. L'application de contrôle de compatibilité indique que le PC "
            "« ne respecte pas la configuration requise ». Tu relèves les informations du "
            "document 1 avec msinfo32, tpm.msc et Gestion des disques."
        ),
        documents=(
            _console(
                "Document 1 — Relevé (capture fictive)",
                "Système d'exploitation   Windows 10 Professionnel",
                "Type du système          PC à base de x64",
                "Processeur               Intel Core i7-8700 (liste : oui)",
                "Mémoire physique (RAM)   16,00 Go",
                "Mode BIOS                Hérité",
                "État du démarrage sécurisé   Non pris en charge",
                "tpm.msc : Version de la spécification : 2.0",
                "Gestion des disques : Disque 0 — style MBR",
            ),
        ),
        instructions=(
            "Explique pourquoi le contrôle échoue alors que le matériel est récent.",
            "Rédige les étapes qui rendent la mise à niveau possible, dans l'ordre.",
        ),
        criteria=(
            _c("Analyse", 1, "Processeur, mémoire et TPM 2.0 conformes ; « Mode BIOS : Hérité » : le PC démarre en mode de compatibilité (CSM), où le démarrage sécurisé n'existe pas ; le disque est en MBR."),
            _c("Étapes", 1.5, "Sauvegarde vérifiée ; mbr2gpt /validate puis /convert /allowFullOS ; firmware en mode UEFI (CSM désactivé) ; démarrage sécurisé activé ; contrôle (msinfo32 : UEFI, Activé) ; nouveau contrôle de compatibilité, puis mise à niveau."),
            _c("Prudence", 0.5, "Ne pas changer le mode du firmware avant la conversion : Windows ne démarrerait plus (disque MBR en mode UEFI)."),
        ),
        correction=(
            "Le matériel est conforme (processeur de la liste, 16 Go, TPM 2.0). Le blocage vient du démarrage : « Mode BIOS : Hérité » signifie que le firmware UEFI fonctionne en mode de compatibilité (CSM) ; dans ce mode, le démarrage sécurisé n'existe pas, et Windows démarre depuis un disque MBR.",
            "Étapes : sauvegarde vérifiée ; dans Windows, mbr2gpt /validate /allowFullOS puis mbr2gpt /convert /allowFullOS (conversion sans perte, qui crée la partition EFI) ; redémarrer dans le firmware, désactiver le CSM (mode UEFI) et activer le démarrage sécurisé ; vérifier dans msinfo32 « Mode BIOS : UEFI » et « Activé » ; relancer le contrôle de compatibilité puis la mise à niveau. Basculer le firmware avant la conversion empêcherait Windows de démarrer.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Quel système pour l'ancien PC d'un retraité ?",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-12", "AP-17"),
        kind=KIND_CHOICE,
        context=(
            "Un retraité utilise son PC de 2011 pour le courrier, le navigateur et ses photos ; "
            "Windows 10 n'y reçoit plus de mises à jour de sécurité. Il refuse d'acheter un PC. "
            "Tu démarres le PC sur une clé Linux « live » (sans rien installer) et tu relèves "
            "le document 1. Le processeur ne figure pas dans la liste de Windows 11."
        ),
        documents=(_console("Document 1 — Terminal de la session live (fictif)", *LIVE_CHECK_SCREEN),),
        instructions=(
            "Interprète chaque relevé du document 1.",
            "Propose un système et une amélioration matérielle, en justifiant.",
        ),
        criteria=(
            _c("Lecture", 1, "x86_64 : processeur 64 bits ; 2 cœurs ; 3,8 Gio de mémoire ; sda ROTA 1 : disque dur rotatif de 500 Go ; pas de /sys/firmware/efi : la session a démarré en mode hérité (BIOS)."),
            _c("Choix", 1.5, "Windows 11 impossible (processeur hors liste, firmware ancien) ; Windows 10 sans mises à jour = risqué en ligne ; distribution Linux 64 bits à support long avec un bureau léger (ex. Linux Mint Xfce) : gratuite, mises à jour, usages couverts (navigateur, courrier, photos)."),
            _c("Amélioration", 0.5, "Remplacer le disque dur par un SSD SATA (gain de rapidité le plus net) ; sauvegarde des photos avant tout."),
        ),
        correction=(
            "x86_64 : le processeur est 64 bits. nproc : 2 cœurs. free -h : 3,8 Gio de mémoire (environ 4 Go). lsblk : sda, 465,8 Gio, ROTA = 1 : c'est un disque dur rotatif de 500 Go. Le dossier /sys/firmware/efi n'existe pas : la clé a démarré en mode hérité (BIOS), ce PC n'a pas d'UEFI ou ne l'utilise pas.",
            "Windows 11 est exclu (processeur hors liste, pas d'UEFI ni de TPM 2.0) et rester sous Windows 10 sans mises à jour expose ses courriers et ses mots de passe. On propose une distribution Linux 64 bits à support long avec un bureau léger (par exemple Linux Mint édition Xfce) : gratuite, mise à jour, suffisante pour le navigateur, le courrier et les photos. Amélioration la plus utile : un SSD SATA à la place du disque dur. Avant tout : sauvegarde vérifiée des photos.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Choisir le système de trois postes",
        question_type="long_answer",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Une petite école de musique équipe trois postes : (1) le secrétariat, qui utilise "
            "un logiciel de facturation disponible uniquement sous Windows et doit rejoindre "
            "le domaine Active Directory du serveur de l'école ; (2) un PC recyclé de 2015 "
            "(64 bits, 4 Go, TPM absent) pour les recherches des élèves ; (3) un serveur de "
            "partage de fichiers sans écran, administré à distance."
        ),
        instructions=("Pour chaque poste, propose un système (et l'édition si c'est Windows), en justifiant par le besoin et le matériel.",),
        criteria=(
            _c("Secrétariat", 1, "Windows 11 Professionnel : logiciel uniquement Windows, jonction au domaine impossible en édition Famille ; PC compatible à vérifier."),
            _c("PC recyclé", 1, "Pas de Windows 11 (pas de TPM 2.0) : distribution Linux légère à support long (ou ChromeOS Flex si le modèle est certifié) ; navigateur suffisant."),
            _c("Serveur", 1, "Distribution Linux serveur à support long (Debian, Ubuntu Server) sans interface graphique, administrée en ligne de commande par SSH ; gratuite et stable."),
        ),
        correction=(
            "1. Secrétariat : Windows 11 Professionnel. Le logiciel de facturation n'existe que sous Windows, et l'édition Famille ne peut pas rejoindre un domaine Active Directory. On vérifie d'abord que le PC respecte les prérequis. 2. PC recyclé : sans TPM 2.0, Windows 11 est exclu ; une distribution Linux à support long avec un bureau léger (ou ChromeOS Flex si le modèle est dans la liste certifiée) suffit pour la recherche sur le web.",
            "3. Serveur : une distribution Linux serveur à support long (Debian ou Ubuntu Server) sans interface graphique. Elle consomme peu, se met à jour longtemps, et s'administre en ligne de commande à distance (SSH) : c'est exactement le cas d'usage de la CLI.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="8 Go installés, 3,2 Go utilisables",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-02"),
        kind=KIND_PREREQ,
        context=(
            "Un client a fait ajouter de la mémoire : son PC compte maintenant 8 Go. Pourtant, "
            "la fenêtre Système affiche « Mémoire installée : 8,00 Go (3,20 Go utilisable) » et "
            "« Type du système : Système d'exploitation 32 bits, processeur x64 ». Il pense "
            "que la barrette est défectueuse."
        ),
        instructions=("Explique l'écart et rédige la solution, licence comprise.",),
        criteria=(
            _c("Cause", 1, f"Un système 32 bits n'adresse que 4 Gio au plus (2^32 octets), dont une partie réservée aux périphériques : {E11_USABLE:g} Gio au plus, ici 3,2 utilisables ; la barrette n'est pas en cause."),
            _c("Solution", 1, "Processeur x64 : installation propre d'un système 64 bits (pas de mise à niveau 32 → 64 bits), après sauvegarde vérifiée ; même édition, la licence reste valable ; programmes réinstallés en 64 bits."),
        ),
        correction=(
            f"Le système installé est en 32 bits : il ne peut adresser que 2^32 octets, soit {E11_USABLE:g} Gio, dont une partie est réservée aux périphériques (carte graphique, contrôleurs). D'où 3,2 Go utilisables. La barrette fonctionne.",
            "Le processeur est x64 : on peut passer à un système 64 bits, mais seulement par une installation propre (aucune mise à niveau de 32 à 64 bits). Sauvegarde vérifiée, installation de la même édition en 64 bits (la licence reste valable), réinstallation des programmes et restauration des données. Les 8 Go seront alors utilisés.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Licences : réinstaller, déplacer, activer",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Trois questions arrivent le même jour : (a) une cliente réinstalle Windows 11 "
            "Famille sur son portable vendu avec Windows préinstallé ; (b) un client veut "
            "déplacer la licence OEM de son vieux PC de marque vers le PC qu'il vient de "
            "monter ; (c) un indépendant a acheté une licence commerciale (boîte) pour son "
            "ancien PC et la veut sur son nouveau."
        ),
        instructions=("Réponds à chaque situation en une ou deux phrases justifiées.",),
        criteria=(
            _c("(a)", 0.75, "Même édition sur le même PC : activation automatique (licence numérique, clé OEM inscrite dans le firmware) ; installer l'édition Famille, pas Professionnel."),
            _c("(b)", 0.75, "Licence OEM liée au premier PC : non transférable ; acheter une licence pour le nouveau PC."),
            _c("(c)", 0.5, "Licence commerciale transférable si elle est retirée de l'ancien PC ; garder la clé ou la lier au compte Microsoft."),
        ),
        correction=(
            "(a) Réinstaller la même édition (Famille) sur le même PC suffit : la licence numérique est reconnue et la clé OEM est lue dans le firmware, Windows s'active seul une fois connecté. Installer l'édition Professionnel ne s'activerait pas avec cette licence. (b) Une licence OEM est liée au premier PC qui l'a reçue : elle ne se déplace pas ; le nouveau PC a besoin de sa propre licence.",
            "(c) Une licence commerciale (boîte ou achat en ligne) peut être transférée sur un autre PC à condition de ne plus l'utiliser sur l'ancien. On conserve la clé, ou on lie la licence au compte Microsoft pour faciliter la réactivation.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Deux entrées pour la même clé dans le menu de démarrage",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_PREREQ,
        context=(
            "Un collègue installe Windows 11 sur un PC UEFI neuf (SSD NVMe vide). Il a choisi "
            "la deuxième entrée de la clé dans le menu de démarrage (document 1) ; au moment "
            "de choisir le disque, l'installateur refuse : « Windows ne peut pas être installé "
            "sur ce disque. Le disque sélectionné est du style de partition GPT. »"
        ),
        documents=(
            _console(
                "Document 1 — Menu de démarrage F12 (capture fictive)",
                "  Windows Boot Manager",
                f"  {BOOT_UEFI_ENTRY}",
                f"  {BOOT_LEGACY_ENTRY}",
                "  UEFI: Réseau IPv4 (PXE)",
            ),
        ),
        instructions=("Explique le message et dis comment relancer l'installation correctement.",),
        criteria=(
            _c("Cause", 1, "L'entrée sans « UEFI: » démarre la clé en mode hérité : l'installateur veut alors un disque MBR et refuse le GPT."),
            _c("Correction", 1, "Redémarrer, choisir l'entrée « UEFI: » de la clé (CSM désactivé si possible) ; installation en GPT avec ESP ; ne pas convertir le disque en MBR (Windows 11 exige UEFI et GPT)."),
        ),
        correction=(
            "Le menu propose la même clé deux fois. L'entrée sans « UEFI: » la démarre en mode hérité (BIOS, CSM) : dans ce mode, l'installateur de Windows ne peut installer que sur un disque MBR, d'où le refus du disque GPT.",
            "On redémarre et on choisit « UEFI: Clé USB… » (au besoin, on désactive le CSM dans le firmware pour qu'il ne reste que les entrées UEFI). L'installation se fait alors en GPT avec une partition EFI. Convertir le disque en MBR serait une erreur : Windows 11 démarre en UEFI sur un disque GPT.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="L'installateur ne voit aucun disque",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-05", "AP-10"),
        kind=KIND_PREREQ,
        context=(
            "Sur un portable récent à processeur Intel, l'installateur de Windows affiche « Nous "
            "n'avons trouvé aucun lecteur. Pour obtenir un pilote de stockage, cliquez sur "
            "Charger un pilote. » Le SSD NVMe est pourtant listé dans le firmware, avec "
            "l'option « Intel VMD » activée. Le site du fabricant propose un pilote « Intel "
            "Rapid Storage Technology (F6) »."
        ),
        instructions=("Explique la cause et rédige la solution, sans toucher aux données d'autres disques.",),
        criteria=(
            _c("Cause", 1, "Le SSD est derrière le contrôleur Intel VMD/RST : l'installateur n'a pas ce pilote de stockage, il ne voit donc pas le disque (le disque n'est pas en panne : le firmware le voit)."),
            _c("Solution", 1, "Télécharger le pilote F6 du fabricant pour ce modèle, le décompresser sur une clé (fichiers .inf), « Charger un pilote », parcourir, choisir le contrôleur ; le disque apparaît. Désactiver VMD dans le firmware seulement si aucun RAID n'est utilisé et en connaissance de cause."),
        ),
        correction=(
            "Le firmware voit le SSD : il n'est pas en panne. Sur ce portable, le SSD est géré par le contrôleur Intel VMD (Rapid Storage Technology) et l'installateur de Windows ne contient pas ce pilote de stockage : il ne voit donc aucun lecteur.",
            "On télécharge le pilote « F6 » du fabricant pour ce modèle, on le décompresse sur une clé USB (fichiers .inf), puis « Charger un pilote » > Parcourir > contrôleur Intel RST VMD. Le SSD apparaît et l'installation continue. Désactiver VMD dans le firmware est une autre voie, seulement si aucun volume RAID n'est utilisé ; on le note dans le rapport.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Tester deux systèmes dans des machines virtuelles",
        question_type="long_answer",
        requirement_ids=("AP-08", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Un formateur veut tester Windows 11 et Ubuntu sans toucher à son PC Windows (16 Go "
            "de mémoire, SSD avec 200 Go libres). Il installe VirtualBox ; au démarrage de la "
            "première machine virtuelle, un message indique que la virtualisation matérielle "
            "(VT-x) est désactivée. Il prévoit 4 Go pour Windows 11 et 2 Go pour Ubuntu."
        ),
        instructions=(
            "Explique le message et ce qu'il faut régler.",
            "Vérifie le plan de mémoire (règle du cours : laisser au moins 4 Go à l'hôte) et cite deux réglages de la machine Windows 11.",
        ),
        criteria=(
            _c("Message", 1, "Les extensions de virtualisation du processeur (Intel VT-x, AMD-V) sont désactivées dans le firmware : les activer, enregistrer, redémarrer."),
            _c("Mémoire", 1, f"16 − 4 − 2 = {E15_LEFT:g} Go pour l'hôte quand les deux machines tournent : plan acceptable ({E15_LEFT:g} ≥ 4)."),
            _c("Réglages", 1, "Machine Windows 11 avec firmware EFI, démarrage sécurisé et TPM virtuel 2.0 ; disque virtuel d'au moins 64 Go ; image ISO officielle ; instantané avant les essais (un instantané n'est pas une sauvegarde)."),
        ),
        correction=(
            "VirtualBox utilise les extensions de virtualisation du processeur (Intel VT-x ou AMD-V). Elles sont désactivées dans le firmware : on les active (option « Intel Virtualization Technology » ou « SVM Mode »), on enregistre et on redémarre.",
            f"Mémoire : 16 − 4 − 2 = {E15_LEFT:g} Go restent au système hôte quand les deux machines tournent, au-dessus des 4 Go du cours : le plan convient. La machine Windows 11 doit respecter les prérequis du système : firmware EFI, démarrage sécurisé, TPM virtuel 2.0, au moins 4 Go et un disque virtuel de 64 Go ou plus. Un instantané avant les essais permet de revenir en arrière ; ce n'est pas une sauvegarde des données.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Corriger le plan d'installation d'un collègue",
        question_type="long_answer",
        requirement_ids=("AP-08", "AP-10", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Pour le poste du comptable d'une PME (domaine Active Directory, disque chiffré "
            "par BitLocker), un collègue a rédigé : « 1. Installer Windows 11 Famille, moins "
            "cher. 2. Démarrer la clé par l'entrée sans UEFI, ça marche toujours. 3. Désactiver "
            "le démarrage sécurisé et le TPM, par sécurité. 4. Ne pas sauvegarder : on garde "
            "D:. 5. Travailler ensuite avec le compte administrateur. »"
        ),
        instructions=("Relève l'erreur de chaque point et réécris le plan correct.",),
        criteria=(
            _c("Points 1-2", 1.5, "Édition Professionnel (domaine, BitLocker) ; entrée « UEFI: » de la clé (installation GPT, Windows 11 démarre en UEFI)."),
            _c("Point 3", 1, "Démarrage sécurisé et TPM 2.0 requis et utiles (BitLocker) : on les laisse actifs ; avant de toucher au firmware, clé de récupération BitLocker sauvegardée."),
            _c("Points 4-5", 1.5, "Sauvegarde vérifiée de toutes les données, même sur D:, accord écrit ; compte administrateur réservé à l'administration, compte standard au quotidien ; mises à jour et antivirus."),
        ),
        correction=(
            "1. L'édition Famille ne peut pas rejoindre le domaine ni gérer BitLocker : Windows 11 Professionnel. 2. L'entrée sans « UEFI: » démarre la clé en mode hérité : l'installateur refusera le disque GPT ; on choisit l'entrée « UEFI: ». 3. Windows 11 exige un firmware compatible démarrage sécurisé et un TPM 2.0, et BitLocker s'appuie sur le TPM : on ne les désactive pas. Avant toute modification du firmware, on sauvegarde la clé de récupération BitLocker.",
            "4. Une erreur de disque ou de manipulation peut effacer D: : sauvegarde de toutes les données, copie vérifiée, accord écrit. 5. Le compte administrateur sert à l'administration ; le comptable travaille avec un compte standard (ou de domaine) sans droits d'administration. On ajoute : mises à jour, antivirus actif, contrôle final et rapport.",
        ),
    ),
)

# =============================================================================================
# Mini-examen : 10 questions à réponse libre, 2 points chacune (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Quelle édition pour un cabinet médical ?",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_CHOICE,
        context=(
            "Un cabinet médical de quatre praticiens achète un nouveau PC pour l'accueil. Le "
            "PC doit rejoindre le domaine Active Directory du cabinet, son disque doit être "
            "chiffré avec BitLocker (dossiers de patients) et le prestataire veut pouvoir le "
            "prendre en main à distance par le Bureau à distance."
        ),
        instructions=("Choisis l'édition de Windows 11 et justifie par les trois besoins.",),
        criteria=(
            _c("Choix", 0.5, "Windows 11 Professionnel."),
            _c("Justification", 1.5, "Jonction au domaine, BitLocker avec sa console et hôte Bureau à distance : absents de l'édition Famille (0,5 pt par besoin)."),
        ),
        correction=(
            "Windows 11 Professionnel.",
            "Les trois besoins sont des fonctions d'entreprise absentes de l'édition Famille : rejoindre un domaine Active Directory, chiffrer et gérer le disque avec BitLocker, et être pris en main à distance comme hôte Bureau à distance (Famille ne contient que le client).",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Un PC de 2017 et Windows 11",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-02"),
        kind=KIND_PREREQ,
        context=(
            "Une cliente veut installer Windows 11 sur son PC de bureau de 2017. Tu relèves "
            "sa fiche (document 1). Rappel des prérequis : processeur 64 bits de la liste de "
            "compatibilité (2 cœurs, 1 GHz), 4 Go, 64 Go, firmware UEFI compatible démarrage "
            "sécurisé, TPM 2.0."
        ),
        documents=(
            _table(
                "Document 1 — Fiche du PC (relevé fictif)",
                ("Élément", "Relevé"),
                ("Processeur", "64 bits, 4 cœurs à 3,4 GHz, absent de la liste de compatibilité"),
                ("Mémoire", "8 Go"),
                ("Stockage", "SSD 256 Go"),
                ("Firmware", "UEFI, démarrage sécurisé activé"),
                ("TPM", "2.0, prêt"),
            ),
        ),
        instructions=("Donne ton verdict, justifie-le et propose une solution à la cliente.",),
        criteria=(
            _c("Verdict", 1, "Non compatible : seul blocage, le processeur absent de la liste de compatibilité ; le reste est conforme."),
            _c("Solution", 1, "Pas de contournement non pris en charge ; rester sur un système encore pris en charge, passer à Linux, ou remplacer le PC ; décision écrite avec la cliente."),
        ),
        correction=(
            "Verdict : non compatible. Mémoire, stockage, firmware et TPM sont conformes, mais le processeur ne figure pas dans la liste de compatibilité publiée par Microsoft : c'est un blocage matériel, qu'aucun réglage du firmware ne corrige.",
            "On ne propose pas d'installation non prise en charge (mises à jour non garanties). Options : passer à une distribution Linux à support long, ou remplacer le PC (ou le processeur, si la carte mère accepte un modèle de la liste). La décision est notée avec la cliente.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Mettre à niveau un PC instable ?",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-10", "AP-C03"),
        kind=KIND_CHOICE,
        context=(
            "Le PC d'un graphiste (compatible Windows 11, sous Windows 10 64 bits) affiche des "
            "fenêtres publicitaires et plante plusieurs fois par jour ; l'antivirus a trouvé "
            "des programmes malveillants sans tout supprimer. Le graphiste demande une "
            "« mise à niveau vers Windows 11 en gardant tout »."
        ),
        instructions=("Choisis la démarche, justifie-la et cite les précautions.",),
        criteria=(
            _c("Démarche", 1, "Installation propre et non mise à niveau : le système n'est pas sain, une mise à niveau garderait les programmes malveillants et les problèmes."),
            _c("Précautions", 1, "Sauvegarde des seuls fichiers de données (pas des programmes), analysée et vérifiée ; licences et installateurs des logiciels relevés ; accord écrit ; mots de passe à changer ensuite."),
        ),
        correction=(
            "Installation propre de Windows 11. Une mise à niveau sur place conserve les programmes et les réglages : elle conserverait aussi les programmes malveillants et l'instabilité.",
            "Précautions : sauvegarder uniquement les fichiers de données (projets, polices achetées, courrier), les analyser et vérifier la copie ; relever les licences et télécharger les installateurs officiels des logiciels ; obtenir l'accord écrit. Après l'installation, restaurer les données, réinstaller les logiciels et faire changer les mots de passe.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Relever un PC en graphique et en ligne de commande",
        question_type="short_answer",
        requirement_ids=("AP-12", "AP-11"),
        kind=KIND_TOOLS,
        context=(
            "Pour l'inventaire d'une école, tu dois noter pour chaque PC la version du système "
            "et la quantité de mémoire. Le parc mélange des PC Windows et des PC Linux ; "
            "certains PC Linux sont des serveurs sans interface graphique, que tu "
            "administres à distance."
        ),
        instructions=(
            "Donne, pour Windows puis pour Linux, un chemin graphique et une commande qui affichent ces informations.",
            "Explique quand la ligne de commande est préférable.",
        ),
        criteria=(
            _c("Windows", 0.75, "Graphique : Paramètres > Système > Informations système (ou msinfo32) ; commande : systeminfo (ou Get-ComputerInfo)."),
            _c("Linux", 0.75, "Graphique : Paramètres > À propos ; commandes : cat /etc/os-release et free -h."),
            _c("CLI", 0.5, "Serveur sans interface, accès à distance (SSH), résultat exact copiable dans le rapport, même commande répétée sur tous les PC (script)."),
        ),
        correction=(
            "Windows : Paramètres > Système > Informations système (ou msinfo32) en graphique ; systeminfo (ou Get-ComputerInfo dans PowerShell) en ligne de commande. Linux : Paramètres > À propos en graphique ; cat /etc/os-release (version) et free -h (mémoire) dans le terminal.",
            "La ligne de commande est préférable pour les serveurs sans interface graphique, pour travailler à distance (SSH), pour copier un résultat exact dans le rapport et pour répéter la même vérification sur tout le parc avec un script.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Faut-il désactiver le démarrage sécurisé pour Linux ?",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-10"),
        kind=KIND_PREREQ,
        context=(
            "Un stagiaire prépare l'installation d'Ubuntu (version à support long) sur un "
            "portable UEFI récent dont la carte graphique NVIDIA servira à du calcul ; le "
            "pilote NVIDIA propriétaire sera compilé sur le PC (DKMS). Il commence par "
            "désactiver le démarrage sécurisé dans le firmware, « parce que Linux ne démarre "
            "pas avec »."
        ),
        instructions=("Dis si c'est nécessaire et explique ce qui se passe pour le pilote NVIDIA compilé sur le PC.",),
        criteria=(
            _c("Démarrage sécurisé", 1, "Pas nécessaire : Ubuntu (comme Debian, Fedora, Linux Mint) démarre avec le démarrage sécurisé grâce à un chargeur signé (shim) ; le laisser actif protège le démarrage."),
            _c("Pilote NVIDIA", 1, "Module compilé sur le PC, donc non signé par la distribution : il est signé avec une clé locale, un mot de passe est demandé et, au redémarrage, on enregistre la clé (écran MOK, « Enroll MOK ») ; sinon le pilote ne se charge pas."),
        ),
        correction=(
            "Non. Les grandes distributions (Ubuntu, Debian, Fedora, Linux Mint) démarrent avec le démarrage sécurisé activé grâce à un petit chargeur signé (shim). Le désactiver retire une protection contre les programmes qui s'installent au démarrage.",
            "Le pilote NVIDIA compilé sur le PC (DKMS) est un module ajouté au noyau qui n'est pas signé par la distribution : il est signé avec une clé locale et un mot de passe est demandé ; au redémarrage, l'écran de gestion des clés (MOK) demande d'enregistrer cette clé (« Enroll MOK ») avec ce mot de passe. Sans cette étape, le pilote ne se charge pas. (Les modules NVIDIA précompilés fournis par Ubuntu sont déjà signés.)",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="La somme de contrôle ne correspond pas",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-12"),
        kind=KIND_TOOLS,
        context=(
            "Avant de préparer une clé d'installation, tu contrôles l'image ISO téléchargée "
            "sur un site de partage par un collègue. Le document 1 montre la commande lancée "
            "dans PowerShell et la somme publiée sur le site officiel de la distribution."
        ),
        documents=(
            _console(
                "Document 1 — PowerShell (capture fictive)",
                "PS> Get-FileHash .\\distribution.iso -Algorithm SHA256",
                "Algorithm  Hash",
                "SHA256     9C1E…77A0",
                "Somme publiée par l'éditeur : 4F2B…D913",
            ),
        ),
        instructions=("Interprète le résultat et rédige ce que tu fais.",),
        criteria=(
            _c("Lecture", 1, "Les deux sommes SHA-256 diffèrent : le fichier n'est pas celui publié (corrompu ou modifié, éventuellement piégé)."),
            _c("Action", 1, "Ne pas utiliser l'image ; la supprimer ; retélécharger depuis le site officiel ; recalculer et comparer ; ne préparer la clé que si les sommes sont identiques."),
        ),
        correction=(
            "Les sommes ne correspondent pas : le fichier n'est pas identique à celui publié par l'éditeur. Il est corrompu (téléchargement interrompu) ou a été modifié, peut-être pour y cacher un programme malveillant ; venant d'un site de partage, le risque est réel.",
            "On n'utilise pas cette image et on la supprime. On télécharge l'image sur le site officiel, on recalcule la somme (Get-FileHash, ou sha256sum sous Linux) et on ne prépare la clé que si elle est identique à la somme publiée.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Sécuriser un PC familial après l'installation",
        question_type="long_answer",
        requirement_ids=("AP-08", "AP-11", "AP-C03"),
        kind=KIND_CHOICE,
        context=(
            "Tu viens d'installer Windows 11 Famille sur le PC d'une famille : deux parents et "
            "deux enfants de 10 et 14 ans. Le père voulait un seul compte administrateur "
            "partagé par tous, sans mot de passe « pour aller plus vite ». Le PC portable "
            "quitte souvent la maison."
        ),
        instructions=("Rédige les réglages de sécurité initiale que tu appliques et justifie-les.",),
        criteria=(
            _c("Comptes", 1, "Un compte par personne ; un compte administrateur protégé par mot de passe pour un parent ; comptes standard (contrôle parental possible) pour les enfants ; jamais de compte sans mot de passe."),
            _c("Protection", 1, "Windows Update à jour, Microsoft Defender et pare-feu actifs ; chiffrement de l'appareil si disponible, clé de récupération sauvegardée hors du PC ; sauvegarde des données."),
        ),
        correction=(
            "Comptes : un compte par personne. Un parent garde un compte administrateur avec un mot de passe solide ; les autres membres, enfants compris, ont des comptes standard (les enfants avec le contrôle parental) : un programme ne peut alors s'installer qu'avec le mot de passe administrateur. Un compte sans mot de passe sur un portable qui voyage expose toutes les données.",
            "Protection : installer toutes les mises à jour, vérifier que Microsoft Defender et le pare-feu sont actifs, activer le chiffrement de l'appareil s'il est disponible et sauvegarder la clé de récupération hors du PC (compte Microsoft ou papier), mettre en place une sauvegarde des documents. On note les réglages dans le rapport.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Une machine virtuelle sur un portable de 8 Go",
        question_type="short_answer",
        requirement_ids=("AP-08", "AP-02"),
        kind=KIND_CHOICE,
        context=(
            "Une étudiante veut tester Linux dans une machine virtuelle VirtualBox sur son "
            "portable Windows de 8 Go de mémoire, sans toucher à Windows. Elle veut donner "
            "4 Go à la machine virtuelle. Règle du cours : laisser au moins 4 Go au système "
            "hôte."
        ),
        instructions=("Vérifie le plan de mémoire et cite les autres prérequis de la virtualisation.",),
        criteria=(
            _c("Mémoire", 1, f"8 − 4 = {X08_LEFT:g} Go pour Windows : juste à la limite du cours ({'acceptable' if X08_OK else 'insuffisant'}) ; fermer les autres programmes, ou 2 à 3 Go pour la VM si la distribution est légère."),
            _c("Prérequis", 1, "Extensions VT-x / AMD-V activées dans le firmware ; espace disque pour le disque virtuel (25 Go environ) ; image ISO officielle ; hyperviseur de type 2 installé sur Windows."),
        ),
        correction=(
            f"Mémoire : 8 − 4 = {X08_LEFT:g} Go restent à Windows, exactement la limite du cours : le plan est acceptable si l'on ferme les autres programmes pendant les essais ; avec une distribution légère, 2 à 3 Go suffisent à la machine virtuelle.",
            "Autres prérequis : extensions de virtualisation du processeur (Intel VT-x ou AMD-V) activées dans le firmware ; espace libre pour le disque virtuel (environ 25 Go pour Ubuntu) ; image ISO officielle contrôlée ; VirtualBox est un hyperviseur de type 2, installé comme un programme sur Windows, qui reste intact.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Passer d'un démarrage hérité à UEFI sans réinstaller",
        question_type="long_answer",
        requirement_ids=("AP-08", "AP-10", "AP-C03"),
        kind=KIND_PREREQ,
        context=(
            "Le PC compatible d'une libraire tourne sous Windows 10 64 bits, installé il y a "
            "des années en mode hérité sur un disque MBR. Pour passer à Windows 11 en gardant "
            "ses programmes, il faut démarrer en UEFI. Le firmware propose UEFI et CSM ; le TPM "
            "2.0 est actif."
        ),
        instructions=("Rédige la procédure dans l'ordre, avec les commandes et les contrôles.",),
        criteria=(
            _c("Préparation", 0.5, "Sauvegarde vérifiée ; accord écrit ; clé de récupération BitLocker si le chiffrement est actif."),
            _c("Conversion", 0.75, "mbr2gpt /validate /allowFullOS puis mbr2gpt /convert /allowFullOS (conversion sans perte, partition EFI créée)."),
            _c("Firmware et contrôle", 0.75, "Firmware : CSM désactivé (UEFI), démarrage sécurisé activé ; msinfo32 : Mode BIOS UEFI, démarrage sécurisé Activé ; puis mise à niveau vers Windows 11."),
        ),
        correction=(
            "1. Sauvegarde des données, copie vérifiée, accord écrit ; si BitLocker est actif, sauvegarder la clé de récupération. 2. Dans Windows, invite de commandes administrateur : mbr2gpt /validate /allowFullOS (contrôle), puis mbr2gpt /convert /allowFullOS : le disque passe en GPT sans perte de données et une partition EFI est créée.",
            "3. Redémarrer dans le firmware : désactiver le CSM (démarrage UEFI) et activer le démarrage sécurisé. 4. Contrôler dans msinfo32 : « Mode BIOS : UEFI », « État du démarrage sécurisé : Activé ». 5. Relancer le contrôle de compatibilité, puis la mise à niveau vers Windows 11. Changer le firmware avant la conversion empêcherait Windows de démarrer.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Lire un relevé Linux avant une mise à niveau",
        question_type="document_analysis",
        requirement_ids=("AP-08", "AP-12"),
        kind=KIND_TOOLS,
        context=(
            "Avant de passer le serveur de fichiers d'une association à la version à support "
            "long suivante de sa distribution, tu relèves en SSH les informations du document "
            "1. La procédure de l'éditeur demande au moins 5 Go libres sur la racine et une "
            "sauvegarde complète."
        ),
        documents=(
            _console(
                "Document 1 — Terminal SSH (capture fictive)",
                "$ grep PRETTY_NAME /etc/os-release",
                'PRETTY_NAME="Ubuntu 22.04.5 LTS"',
                "$ uname -m",
                "x86_64",
                "$ df -h /",
                "Sys. de fichiers  Taille Utilisé Dispo Uti% Monté sur",
                "/dev/sda2           30G     28G  1,2G  96% /",
            ),
        ),
        instructions=("Interprète le relevé et dis ce qu'il faut faire avant la mise à niveau.",),
        criteria=(
            _c("Lecture", 1, "Ubuntu 22.04 LTS (version à support long), 64 bits ; racine de 30 Go pleine à 96 %, 1,2 Go libres : moins que les 5 Go demandés."),
            _c("Avant", 1, "Sauvegarde complète vérifiée ; libérer de l'espace (sudo apt clean, sudo apt autoremove, journaux, fichiers déplacés) ou agrandir la partition ; recontrôler df -h (≥ 5 Go) avant de lancer la mise à niveau."),
        ),
        correction=(
            "Le serveur tourne sous Ubuntu 22.04 LTS (version à support long), en 64 bits (x86_64). La racine fait 30 Go, dont 28 utilisés (96 %) : il ne reste que 1,2 Go, bien moins que les 5 Go exigés par la procédure.",
            "Avant la mise à niveau : sauvegarde complète et vérifiée ; libérer de l'espace (sudo apt clean, sudo apt autoremove, journaux anciens, données déplacées vers un autre volume) ou agrandir la partition ; vérifier à nouveau avec df -h qu'au moins 5 Go sont libres, puis lancer la mise à niveau.",
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

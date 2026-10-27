"""PR08 « Installation complète de Windows — préparation et dépannage » — exercices corrigés et
mini-examen (ticket #208).

Même organisation que les cours pratiques déjà publiés (`app.v1.ampcr_pratique_pr06_bank`, dont
ce module réutilise le type d'item, et `app.v1.ampcr_pratique_pr04_bank`, dont il réutilise les
petits constructeurs) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (préparation, installation, finalisation), classements
  (symptôme → cause, partitions, activation, avant/pendant/après), fiche d'inventaire, captures
  de l'installateur et du Gestionnaire de périphériques, migration, rapport, procédure à corriger ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations et captures sont **fictives** ; procédures, règles des partitions, activation,
dépannage et fabricants viennent de `app.v1.ampcr_pratique_pr08_figures` (mêmes données que les
schémas).
"""

from app.v1.ampcr_pratique_format import validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr08_figures import (
    ACTIVATION_RESULTS,
    FINAL_STEPS,
    LIC_DIGITAL,
    LIC_OEM,
    LIC_RETAIL,
    MBR_ERROR_SCREEN,
    NO_DRIVE_SCREEN,
    PARTITION_ACTIONS,
    PREP_STEPS,
    SETUP_STEPS,
    TR_BOOT,
    TR_CATEGORIES,
    TR_DRIVER,
    TR_LICENCE,
    TR_PARTITION,
    TR_STORAGE,
    activation_result,
    partition_action,
    vendor_of,
)

PR08_CODE = "PR08"

KIND_ORDER = "ordonnancement"
KIND_PREP = "préparation et licences"
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
    ("« Nous n'avons trouvé aucun lecteur » sur un portable neuf dont le firmware affiche le SSD NVMe", TR_STORAGE),
    ("« Sur les systèmes EFI, Windows ne peut être installé que sur des disques GPT »", TR_PARTITION),
    ("Dans le menu de démarrage, la clé apparaît seulement sans la mention « UEFI: »", TR_BOOT),
    ("Après le premier redémarrage, l'écran de choix de la langue réapparaît", TR_BOOT),
    ("« Contrôleur Ethernet » avec un point d'exclamation ; aucune connexion réseau", TR_DRIVER),
    ("« Windows n'est pas activé » : licence OEM Famille, édition Professionnel installée", TR_LICENCE),
    ("Affichage en 1024 × 768 avec « Carte graphique de base Microsoft »", TR_DRIVER),
    ("Le PC ne démarre plus quand on débranche l'ancien disque, resté branché pendant l'installation", TR_PARTITION),
)

# (partition décrite au candidat, sur le disque cible, sauvegarde vérifiée, accord écrit)
E05_CASES: tuple[tuple[str, bool, bool, bool], ...] = (
    ("Partition C: de l'ancien Windows sur le SSD cible ; données copiées et vérifiées ; accord signé",
     True, True, True),
    ("Partition système EFI (100 Mo) du même SSD cible, dans la même situation", True, True, True),
    ("Partition « DONNEES » du disque dur de 1 To, que le client veut garder", False, True, True),
    ("Partition C: du SSD cible ; la cliente a dit au téléphone « effacez tout » ; rien n'est sauvegardé",
     True, False, False),
    ("Disque USB de sauvegarde du client resté branché pendant l'installation", False, True, True),
    ("Partition C: du SSD cible ; copie vérifiée, mais le gérant n'a pas encore signé l'accord", True, True, False),
)
E05_CORRECT = tuple(
    PARTITION_ACTIONS.index(partition_action(on_target_disk=t, backup_verified=b, written_consent=w))
    for _d, t, b, w in E05_CASES
)

_HOME = "Famille"
_PRO = "Professionnel"
# (situation, licence, édition de la licence, édition installée, même PC, retirée de l'ancien PC)
E06_CASES: tuple[tuple[str, str, str, str, bool, bool], ...] = (
    ("Portable vendu avec Windows 11 Famille (licence OEM), réinstallé en Famille sur le même portable",
     LIC_OEM, _HOME, _HOME, True, True),
    ("Même portable (licence OEM Famille), réinstallé en édition Professionnel « parce que c'est mieux »",
     LIC_OEM, _HOME, _PRO, True, True),
    ("Étiquette OEM Professionnel d'un vieux PC mis au rebut, utilisée pour un PC neuf",
     LIC_OEM, _PRO, _PRO, False, True),
    ("Clé commerciale Professionnel désinstallée de l'ancien PC du client, utilisée sur son nouveau PC en Pro",
     LIC_RETAIL, _PRO, _PRO, False, True),
    ("PC passé en Professionnel l'an dernier (licence numérique), réinstallé en Professionnel, même matériel",
     LIC_DIGITAL, _PRO, _PRO, True, True),
    ("Clé commerciale Famille saisie sur une installation Professionnel",
     LIC_RETAIL, _HOME, _PRO, True, True),
)
E06_RESULTS = tuple(
    activation_result(lic, edition, installed, same_pc=same, removed_from_old_pc=removed)
    for _s, lic, edition, installed, same, removed in E06_CASES
)
E06_CORRECT = tuple(ACTIVATION_RESULTS.index(result) for result, _why in E06_RESULTS)

WHEN_BEFORE = "Avant l'installation"
WHEN_DURING = "Pendant l'installation"
WHEN_AFTER = "Après l'installation"
E07_CATEGORIES = (WHEN_BEFORE, WHEN_DURING, WHEN_AFTER)
E07_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("Copier le dossier du pilote de stockage Intel VMD sur la clé", WHEN_BEFORE),
    ("Exporter les favoris du navigateur avec la cliente", WHEN_BEFORE),
    ("Relever la clé de récupération BitLocker de l'ancien système", WHEN_BEFORE),
    ("Choisir « Je n'ai pas de clé de produit »", WHEN_DURING),
    ("Supprimer les partitions de l'ancien Windows sur le disque cible", WHEN_DURING),
    ("Installer le pilote graphique du fabricant", WHEN_AFTER),
    ("Relever l'ID du matériel d'un périphérique inconnu", WHEN_AFTER),
    ("Créer un point de restauration une fois le poste prêt", WHEN_AFTER),
)

E11_IDS = ("PCI\\VEN_10DE&DEV_1F82", "PCI\\VEN_14E4&DEV_43A0")
E11_VENDORS = tuple(vendor_of(h) for h in E11_IDS)

X01_RESULT, X01_WHY = activation_result(LIC_OEM, _HOME, _PRO, same_pc=True)
X06_ID = "PCI\\VEN_10EC&DEV_8125"
X06_VENDOR = vendor_of(X06_ID)
X02_ACTIONS = (
    partition_action(on_target_disk=True, backup_verified=True, written_consent=True),
    partition_action(on_target_disk=False, backup_verified=True, written_consent=True),
)

# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la préparation d'une installation",
        question_type="ordering",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_ORDER,
        context=(
            "Un cabinet de kinésithérapie confie à l'atelier le PC de son accueil pour une "
            "réinstallation propre de Windows 11. Ton responsable veut une fiche de "
            "préparation que les stagiaires suivront avant de démarrer sur la clé. Les six "
            "étapes de la fiche ont été mélangées."
        ),
        instructions=("Remets les six étapes de préparation dans l'ordre professionnel.",),
        criteria=(
            _c("Ordre", 3, "Demande et accord → inventaire → compatibilité → sauvegarde → média → pilotes (0,5 pt par étape bien placée)."),
        ),
        correction=(
            "1. Recueillir la demande et l'accord écrit : on sait ce qu'il faut garder et l'effacement est autorisé. 2. Inventorier le poste (modèle, processeur, mémoire, disques, firmware, édition et licence). 3. Vérifier la compatibilité avec la version visée et la disponibilité des pilotes du fabricant.",
            "4. Sauvegarder les données et profils sur un autre support, copie vérifiée. 5. Préparer le média à partir d'une image officielle. 6. Copier sur la clé les pilotes de stockage et de réseau : sans eux, l'installateur peut ne voir ni disque ni réseau.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre l'installation, de la clé au bureau",
        question_type="ordering",
        requirement_ids=("AP-10",),
        kind=KIND_ORDER,
        context=(
            "La préparation du PC du cabinet est terminée : données sauvegardées, accord signé, "
            "clé d'installation contrôlée et pilotes copiés. Le stagiaire a noté les huit "
            "étapes de l'installation elle-même sur des post-it, qui se sont mélangés."
        ),
        instructions=("Remets les huit étapes de l'installation dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Firmware → démarrer sur la clé → langue et clavier → clé et édition → type d'installation → disque → copie et redémarrages → configuration initiale (0,5 pt par étape)."),
        ),
        correction=(
            "1. Régler le firmware (mode UEFI, démarrage sécurisé, TPM) et noter le mode du stockage. 2. Démarrer sur l'entrée « UEFI: » de la clé. 3. Choisir la langue, le format régional et le clavier. 4. Saisir la clé ou choisir « Je n'ai pas de clé », puis l'édition de la licence.",
            "5. Choisir l'installation personnalisée (installation propre). 6. Identifier le disque cible et sélectionner l'espace non alloué. 7. Laisser la copie et les redémarrages se faire (retirer la clé si l'installateur redémarre). 8. Configuration initiale : région, clavier, réseau, compte et mot de passe, confidentialité.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 7, 2, 0, 6, 3, 5)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la finalisation avant de rendre le PC",
        question_type="ordering",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_ORDER,
        context=(
            "Windows 11 vient d'arriver au bureau sur le PC du cabinet. Avant de rappeler la "
            "cliente, il reste six opérations de finalisation. Elles sont notées dans le "
            "désordre sur la fiche d'intervention."
        ),
        instructions=("Remets les six opérations dans l'ordre.",),
        criteria=(
            _c("Ordre", 3, "Pilotes → mises à jour → activation → sécurité → restauration → contrôle et rapport (0,5 pt par étape)."),
        ),
        correction=(
            "1. Pilotes : chipset, stockage, réseau puis graphique, jusqu'à ne plus avoir de périphérique inconnu (le réseau est nécessaire pour la suite). 2. Windows Update jusqu'à « Vous êtes à jour », mises à jour facultatives des pilotes comprises. 3. Vérifier l'activation.",
            "4. Sécurité : Defender et pare-feu actifs, compte standard pour le quotidien, chiffrement et clé de récupération. 5. Restaurer les données de la cliente et créer un point de restauration du poste propre. 6. Passer la liste de contrôle avec la cliente et rédiger le rapport signé.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (2, 5, 0, 4, 1, 3)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Huit symptômes pendant ou après l'installation : quelle cause ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-09", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "La semaine de l'atelier a été chargée : huit installations de Windows 11 ont posé "
            "un problème. Pour la réunion d'équipe, ton responsable veut ranger chaque "
            "symptôme relevé par les techniciens dans la famille de cause qui l'explique, "
            "afin de compléter la fiche de dépannage."
        ),
        instructions=("Range chaque symptôme dans la famille de cause la plus probable.",),
        criteria=(
            _c("Classement", 4, "Stockage : aucun lecteur alors que le firmware voit le SSD. Démarrage : clé sans « UEFI: », retour à l'écran de langue. Partitions : disque MBR refusé, chargeur sur l'ancien disque débranché. Pilote : contrôleur Ethernet, carte graphique de base. Licence : OEM Famille sur une installation Professionnel (0,5 pt par élément)."),
        ),
        correction=(
            "Le firmware voit le SSD mais l'installateur ne liste aucun lecteur : il manque le pilote du contrôleur de stockage (VMD, RST, RAID). La clé sans « UEFI: » démarre en mode hérité (clé écrite en MBR) ; l'installation qui recommence vient de l'ordre de démarrage (clé avant le disque).",
            "Le message GPT/EFI et le PC qui ne démarre plus sans l'ancien disque (sa partition EFI a reçu le chargeur) relèvent des partitions. Le point d'exclamation sur le contrôleur Ethernet et la carte graphique de base Microsoft sont des pilotes manquants. Une licence OEM Famille n'active pas une édition Professionnel : licence ou édition.",
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
        title="Que faire de chaque partition affichée par l'installateur ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Sur l'écran de choix de l'emplacement, l'installateur propose de supprimer ou de "
            "formater les partitions. Six situations rencontrées à l'atelier sont décrites. "
            "Règle de l'atelier : on ne supprime que sur le disque cible, après sauvegarde "
            "vérifiée et accord écrit du propriétaire."
        ),
        instructions=("Range chaque partition dans l'action à appliquer.",),
        criteria=(
            _c("Classement", 3, "Supprimer : C: et ESP du SSD cible (copie vérifiée, accord signé). Ne pas toucher : partition DONNEES du disque dur, disque USB de sauvegarde. Arrêter : accord seulement oral sans sauvegarde, accord pas encore signé (0,5 pt par élément)."),
        ),
        correction=(
            "Sur le SSD cible, avec copie vérifiée et accord signé, on supprime les partitions de l'ancien Windows (C:, partition EFI…) pour obtenir un espace non alloué : l'installateur recrée lui-même la disposition GPT.",
            "On ne touche jamais à un autre disque (données du client, disque de sauvegarde, qu'on aurait d'ailleurs dû débrancher). Un « effacez tout » au téléphone sans sauvegarde, ou une sauvegarde sans accord signé, ne suffit pas : on arrête et on régularise avant toute suppression.",
        ),
        classification=Classification(
            categories=PARTITION_ACTIONS,
            elements=tuple(d for d, *_r in E05_CASES),
            correct=E05_CORRECT,
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Windows s'activera-t-il après la réinstallation ?",
        question_type="classification",
        requirement_ids=("AP-10", "AP-08"),
        kind=KIND_PREP,
        context=(
            "Six réinstallations sont prévues cette semaine. Avant de les lancer, tu vérifies "
            "pour chacune si Windows s'activera, en comparant le type de licence, son édition, "
            "l'édition qui sera installée et le PC concerné. Un PC rendu non activé n'est pas "
            "une intervention terminée."
        ),
        instructions=("Range chaque situation : Windows s'active, ou ne s'active pas et il faut corriger.",),
        criteria=(
            _c("Classement", 3, "S'active : OEM Famille réinstallé en Famille, clé commerciale retirée de l'ancien PC, licence numérique sur le même matériel. Ne s'active pas : OEM Famille installé en Pro, étiquette OEM d'un autre PC, clé Famille sur une installation Pro (0,5 pt par élément)."),
        ),
        correction=(
            "Une licence OEM ou numérique reste liée au PC d'origine et réactive automatiquement la même édition : réinstaller en Famille un portable vendu en Famille, ou en Professionnel un PC passé en Professionnel avec le même matériel, s'active. Une clé commerciale se transfère si elle a été retirée de l'ancien PC.",
            "L'édition installée doit être celle de la licence : une licence Famille n'active ni une installation Professionnel, ni par la clé saisie. L'étiquette OEM d'un PC mis au rebut ne vaut pas pour un autre PC. Dans ces cas, on réinstalle la bonne édition ou on informe le client qu'il faut une licence.",
        ),
        classification=Classification(
            categories=ACTIVATION_RESULTS,
            elements=tuple(s for s, *_r in E06_CASES),
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
            "Un nouveau collègue prépare sa première installation de Windows 11 sur le portable "
            "d'une avocate (contrôleur Intel VMD, disque chiffré par BitLocker). Il a listé "
            "huit gestes, sans savoir à quel moment de l'intervention les placer : avant de "
            "démarrer sur la clé, dans l'installateur, ou une fois Windows au bureau."
        ),
        instructions=("Range chaque geste dans le moment où il se fait.",),
        criteria=(
            _c("Classement", 4, "Avant : pilote VMD sur la clé, favoris exportés, clé BitLocker relevée. Pendant : « Je n'ai pas de clé », suppression des partitions du disque cible. Après : pilote graphique, ID du matériel d'un inconnu, point de restauration (0,5 pt par élément)."),
        ),
        correction=(
            "Avant : tout ce qui dépend de l'ancien système ou qui serait perdu (favoris, clé de récupération BitLocker, utile si l'on doit relire l'ancien disque) et ce dont l'installateur aura besoin (pilote VMD sur la clé).",
            "Pendant : le choix de la clé ou de l'édition et la suppression des partitions de l'ancien Windows sur le disque cible. Après : pilotes du fabricant (graphique), identification des périphériques inconnus par leur ID du matériel, puis point de restauration une fois le poste prêt.",
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
        title="Lire une fiche d'inventaire avant de réinstaller",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-17", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Une agence immobilière demande une réinstallation propre de Windows 11 sur le PC "
            "de son gérant, devenu très lent. Il veut garder ses dossiers clients. Le "
            "technicien de la tournée a rempli la fiche d'inventaire du document 1. Tu dois "
            "préparer l'intervention à partir de cette fiche."
        ),
        documents=(
            _table(
                "Document 1 — Fiche d'inventaire (fictive)",
                ("Rubrique", "Relevé"),
                ("Poste", "Portable 2022, numéro de série relevé"),
                ("Système", "Windows 11 Famille, licence OEM (clé dans le firmware)"),
                ("Processeur, mémoire", "Intel Core i5 de 12e génération, 16 Go"),
                ("Stockage", "SSD NVMe 512 Go, GPT : C: 476 Go dont « Dossiers clients » (38 Go)"),
                ("Firmware", "UEFI, démarrage sécurisé activé, TPM 2.0, contrôleur Intel VMD activé"),
                ("Sécurité", "Chiffrement de l'appareil actif"),
                ("Réseau", "Wi-Fi Intel seulement, pas de port Ethernet"),
            ),
        ),
        instructions=(
            "Relève dans la fiche les quatre points qui changent ta préparation.",
            "Pour chacun, rédige ce que tu prépares avant de démarrer sur la clé.",
        ),
        criteria=(
            _c("Données et chiffrement", 1, "Dossiers clients sur C: : sauvegarde vérifiée sur un autre support, accord écrit ; chiffrement actif : clé de récupération relevée avant."),
            _c("Licence", 0.5, "OEM Famille : installer l'édition Famille, l'activation sera automatique."),
            _c("Stockage", 0.75, "Intel VMD : pilote de stockage du fabricant (dossier F6) copié sur la clé, sinon « aucun lecteur »."),
            _c("Réseau", 0.75, "Wi-Fi seul : pilote Wi-Fi du fabricant sur la clé (ou adaptateur Ethernet USB reconnu), nom et clé du Wi-Fi notés."),
        ),
        correction=(
            "1. Les dossiers clients sont sur C:, qui sera effacé : sauvegarde complète sur un autre support, copie vérifiée, accord écrit du gérant ; le chiffrement de l'appareil est actif : on relève la clé de récupération avant de toucher au poste. 2. Licence OEM Famille (clé dans le firmware) : on réinstalle l'édition Famille ; l'activation sera automatique.",
            "3. Contrôleur Intel VMD activé : l'installateur risque de ne voir aucun lecteur ; on copie le pilote de stockage du fabricant (dossier F6) sur la clé. 4. Pas de port Ethernet et Wi-Fi Intel : on prépare son pilote sur la clé (ou un adaptateur Ethernet USB reconnu) et on note le nom et la clé du Wi-Fi, nécessaires à la configuration initiale. Le matériel respecte les prérequis de Windows 11.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="« Aucun lecteur » sur un PC de bureau neuf",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-09", "AP-15"),
        kind=KIND_TROUBLE,
        context=(
            "Un bureau d'études reçoit un PC neuf livré sans système, avec la licence achetée à "
            "part. Pendant l'installation de Windows 11, le stagiaire tombe sur l'écran du "
            "document 1 et propose de renvoyer le PC au fournisseur pour « SSD défectueux ». "
            "Le fournisseur publie les pilotes du modèle sur son site."
        ),
        documents=(_console("Document 1 — Installateur et firmware (capture fictive)", *NO_DRIVE_SCREEN),),
        instructions=(
            "Explique pourquoi le SSD n'est pas en cause.",
            "Rédige la marche à suivre pour poursuivre l'installation.",
        ),
        criteria=(
            _c("Analyse", 1, "Le firmware détecte le SSD : il n'est pas mort ; le contrôleur Intel VMD est activé et l'installateur n'a pas son pilote."),
            _c("Procédure", 1.5, "Sur un autre PC : pilote de stockage du fabricant (Intel RST/VMD, version « F6 »), extrait sur la clé ; « Charger un pilote », parcourir, choisir le contrôleur ; le SSD apparaît ; poursuivre."),
            _c("Prudence", 0.5, "Ne pas renvoyer le PC ; ne pas changer le mode du contrôleur une fois Windows installé (il ne démarrerait plus) ; alternative AHCI seulement sur un disque vide et si la notice le permet."),
        ),
        correction=(
            "Le SSD est détecté par le firmware : il n'est pas en panne. Le contrôleur de stockage fonctionne en mode Intel VMD et l'installateur ne contient pas son pilote : il ne voit donc aucun lecteur.",
            "Sur un autre PC, on télécharge sur le site du fournisseur le pilote de stockage Intel RST/VMD (version à extraire, dite « F6 ») et on le copie sur la clé. Dans l'installateur : « Charger un pilote », parcourir jusqu'au dossier, choisir le contrôleur ; le SSD apparaît et l'installation continue. On ne renvoie pas le PC ; on ne change pas le mode du contrôleur après l'installation (Windows ne démarrerait plus). Passer en AHCI n'est envisageable que sur un disque vide, si la notice le permet.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Disque MBR refusé sur un PC reconditionné",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Une entreprise donne dix PC à une école et a fourni un bon signé autorisant "
            "l'effacement complet ; leurs données ont été archivées par son service "
            "informatique. Sur le premier PC (firmware UEFI, démarrage sécurisé actif), "
            "l'installateur de Windows 11 affiche le message du document 1 ; tu as ouvert une "
            "invite avec Maj+F10."
        ),
        documents=(_console("Document 1 — Installateur et diskpart (capture fictive)", *MBR_ERROR_SCREEN),),
        instructions=(
            "Interprète le message et la commande.",
            "Rédige la solution adaptée à ce PC et ce que tu ne fais pas.",
        ),
        criteria=(
            _c("Lecture", 1, "Le PC démarre en UEFI ; le disque 0 (476 Go) est en MBR (pas d'astérisque GPT) ; Windows 11 en UEFI exige GPT ; le disque 1 de 14 Go est la clé."),
            _c("Solution", 1.5, "Effacement autorisé par écrit et données archivées : supprimer toutes les partitions du disque 0 dans l'installateur (espace non alloué) ; l'installateur crée GPT, ESP, MSR, Windows et Récupération."),
            _c("À ne pas faire", 0.5, "Ne pas basculer en mode hérité ni désactiver le démarrage sécurisé ; ne pas toucher au disque 1 (la clé)."),
        ),
        correction=(
            "Le PC a démarré la clé en UEFI ; or le disque 0 (476 Go, sans astérisque dans la colonne GPT) est en MBR, et Windows ne s'installe en UEFI que sur un disque GPT. Le disque 1 (14 Go, GPT) est la clé d'installation.",
            "L'effacement est autorisé par un bon signé et les données sont archivées : dans l'installateur, on supprime toutes les partitions du disque 0 jusqu'à obtenir un espace non alloué, on le sélectionne, et l'installateur crée lui-même le style GPT et les partitions (ESP, MSR, Windows, Récupération). On ne passe pas en mode hérité et on ne désactive pas le démarrage sécurisé pour contourner le message ; on ne touche pas au disque 1.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Identifier les pilotes manquants par l'ID du matériel",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-05", "AP-11"),
        kind=KIND_TROUBLE,
        context=(
            "Après l'installation de Windows 11 sur le PC de jeu d'un étudiant (PC monté par "
            "lui-même, sans site de fabricant unique), le Wi-Fi ne fonctionne pas et l'écran "
            "reste en basse résolution. Le Gestionnaire de périphériques montre le document 1. "
            "Tu disposes d'un autre PC connecté à Internet."
        ),
        documents=(
            _console(
                "Document 1 — Gestionnaire de périphériques (capture fictive)",
                "v Autres périphériques",
                "    (!) Contrôleur de réseau",
                "v Cartes graphiques",
                "    Carte graphique de base Microsoft",
                "",
                "Carte graphique → ID du matériel :",
                f"  {E11_IDS[0]}",
                "Contrôleur de réseau → ID du matériel :",
                f"  {E11_IDS[1]}",
            ),
        ),
        instructions=(
            "Identifie le fabricant de chaque matériel.",
            "Rédige le plan d'installation des pilotes, dans l'ordre, avec la source à utiliser.",
        ),
        criteria=(
            _c("Identification", 1, f"VEN_10DE = {E11_VENDORS[0]} (carte graphique), VEN_14E4 = {E11_VENDORS[1]} (Wi-Fi) ; DEV précise le modèle."),
            _c("Plan", 1.5, "Pilote Wi-Fi d'abord (seul moyen d'avoir le réseau) : téléchargé sur l'autre PC chez le fabricant de la carte ou de la carte mère, copié par clé ; puis Windows Update ; puis pilote graphique du fabricant ; contrôle : plus de (!) ni carte de base."),
            _c("Sources", 0.5, "Sites des fabricants ou Windows Update, jamais un « pack de pilotes » d'un site inconnu."),
        ),
        correction=(
            f"Dans l'ID du matériel, VEN donne le fabricant et DEV le modèle : VEN_10DE est {E11_VENDORS[0]} (la carte graphique), VEN_14E4 est {E11_VENDORS[1]} (la carte Wi-Fi). On recherche ces identifiants pour trouver le pilote exact.",
            "Ordre : d'abord le pilote Wi-Fi (sans lui, pas de réseau ni de Windows Update), téléchargé sur l'autre PC chez le fabricant de la carte Wi-Fi ou de la carte mère et copié par clé USB ; ensuite Windows Update, mises à jour facultatives comprises ; puis le pilote graphique depuis le site de NVIDIA. Contrôle : plus aucun point d'exclamation, la carte graphique porte son nom et la résolution native est proposée. Jamais de « pack de pilotes » d'un site inconnu.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="La clé d'installation n'apparaît pas en « UEFI: »",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-09"),
        kind=KIND_TROUBLE,
        context=(
            "Un collègue a préparé une clé Windows 11 avec Rufus en laissant le schéma de "
            "partition sur « MBR » et la cible sur « BIOS ou UEFI-CSM ». Sur un portable "
            "récent réglé en UEFI seul (CSM désactivé), la clé n'apparaît pas dans le menu de "
            "démarrage. Il propose d'activer le CSM pour la faire démarrer."
        ),
        instructions=("Explique la cause et rédige la bonne solution.",),
        criteria=(
            _c("Cause", 1, "Clé écrite pour un démarrage hérité (schéma MBR, cible BIOS) : un firmware en UEFI seul ne la propose pas."),
            _c("Solution", 1, "Réécrire la clé depuis l'image officielle avec le schéma GPT / cible UEFI (ou l'outil de création de Microsoft) ; démarrer l'entrée « UEFI: » ; ne pas activer le CSM : Windows s'installerait en mode hérité sur MBR, refusé par Windows 11."),
        ),
        correction=(
            "La clé a été écrite pour un démarrage hérité (schéma MBR, cible BIOS) : un firmware réglé en UEFI seul ne la propose pas.",
            "On réécrit la clé depuis l'image officielle avec le schéma GPT et la cible UEFI (ou avec l'outil de création de Microsoft), puis on démarre l'entrée « UEFI: ». Activer le CSM ferait démarrer l'installateur en mode hérité : Windows serait installé sur un disque MBR, sans démarrage sécurisé, et Windows 11 refuserait la configuration.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Un PC à deux disques qui ne démarre plus",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-15"),
        kind=KIND_INSTALL,
        context=(
            "Hier, tu as installé Windows 11 sur le nouveau SSD (disque 1) d'un PC dont le "
            "disque dur de 2 To (disque 0) portait l'ancien Windows et sert désormais aux "
            "données ; il est resté branché. Aujourd'hui, le client a retiré le disque dur "
            "pour le mettre dans un boîtier externe : le PC affiche « Aucun périphérique de "
            "démarrage ». Gestion des disques montrait la partition système EFI sur le disque 0."
        ),
        instructions=("Explique la panne, la solution adaptée et la précaution pour la prochaine fois.",),
        criteria=(
            _c("Explication", 0.75, "L'installateur a réutilisé la partition système EFI déjà présente sur le disque 0 (ancien Windows) pour y placer le chargeur ; sans ce disque, le firmware ne trouve plus de chargeur."),
            _c("Solution", 0.75, "Installation d'hier : remettre le disque, sauvegarder ce qui a été ajouté, réinstaller avec le SSD seul branché (ou réparation du démarrage en PR11) ; ne rien supprimer sur le disque de données."),
            _c("Précaution", 0.5, "Débrancher les autres disques pendant l'installation ; vérifier dans Gestion des disques que l'ESP est sur le disque système."),
        ),
        correction=(
            "Le disque dur portait déjà une partition système EFI (celle de l'ancien Windows) : l'installateur l'a réutilisée pour y placer le chargeur de démarrage, et a installé Windows sur le SSD. Le disque dur retiré, le firmware ne trouve plus de chargeur.",
            "L'installation date d'hier : on remet le disque, on sauvegarde ce qui aurait déjà été ajouté, puis on réinstalle avec le seul SSD branché (une réparation du démarrage, vue en PR11, est l'autre voie) ; on ne supprime rien sur le disque de données sans l'accord du client. La prochaine fois : débrancher les autres disques pendant l'installation et vérifier dans Gestion des disques que l'ESP est sur le disque système.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Migrer les données vers une installation propre",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Une fleuriste remplace son vieux PC sous Windows 10 par un PC neuf sous Windows "
            "11. Elle utilise un navigateur avec ses favoris et mots de passe, un logiciel de "
            "caisse acheté (licence pour un seul PC), un courrier en fichier local (.pst) et un "
            "dossier C:\\Commandes en dehors de ses Documents. Elle compte sur toi pour « que "
            "tout soit comme avant »."
        ),
        instructions=("Rédige la liste de ce que tu migres, avec pour chaque élément la méthode et le contrôle.",),
        criteria=(
            _c("Fichiers", 1, "Profil (Documents, Bureau, Images…) et C:\\Commandes, copiés sur un disque externe, copie vérifiée (nombre et taille), restaurés."),
            _c("Applications", 1, "Favoris et mots de passe : synchronisation du navigateur ou export avec elle ; courrier : copie du .pst et import ; logiciel de caisse : clé relevée, licence désactivée sur l'ancien PC, réinstallé."),
            _c("Contrôle", 1, "Vérification avec la cliente (fichiers, courriers, caisse, imprimante) ; ancien PC conservé intact jusqu'à sa validation ; noté dans le rapport."),
        ),
        correction=(
            "Fichiers : les dossiers de son profil (Documents, Bureau, Images, Téléchargements) et le dossier C:\\Commandes, hors profil et donc facile à oublier, sont copiés sur un disque externe ; on vérifie la copie (nombre et taille des fichiers) puis on restaure sur le nouveau PC. Navigateur : synchronisation de son compte ou exportation des favoris et mots de passe, faite avec elle.",
            "Courrier : on copie le fichier .pst et on l'importe dans la messagerie du nouveau PC. Logiciel de caisse : on relève la clé, on désactive la licence sur l'ancien PC (limitée à un poste), on l'installe sur le nouveau. Contrôle avec la cliente : fichiers, courriers, caisse et imprimante testés ; l'ancien PC reste intact jusqu'à sa validation ; tout est noté dans le rapport.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Rédiger le rapport d'intervention à partir des notes",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_POST,
        context=(
            "Tu as réinstallé Windows 11 Famille sur le portable d'un traducteur indépendant. "
            "Tes notes : « accord signé le 14/10 ; 52 Go de documents copiés sur disque USB, "
            "vérifiés ; pilote VMD chargé ; Windows 11 Famille activé ; 2 pilotes réseau et "
            "graphique installés ; à jour ; Defender actif ; chiffrement activé, clé remise sur "
            "papier ; données restaurées et vérifiées avec lui ; batterie à 71 % de sa capacité "
            "d'origine »."
        ),
        instructions=("Rédige le rapport d'intervention en rubriques, à partir de ces notes.",),
        criteria=(
            _c("Rubriques", 1, "Demande et accord, poste, sauvegarde, actions, contrôles, remise, recommandations."),
            _c("Contenu", 1.5, "Chaque note à sa place, sans rien inventer : accord du 14/10, sauvegarde de 52 Go vérifiée, pilote VMD, édition Famille activée, pilotes, mises à jour, Defender, chiffrement et clé remise, données vérifiées."),
            _c("Recommandations", 0.5, "Batterie usée (71 %) à surveiller ou remplacer ; sauvegarde régulière."),
        ),
        correction=(
            "Demande : réinstallation propre de Windows 11, accord écrit signé le 14/10. Poste : portable du client (marque, modèle, numéro de série). Sauvegarde : 52 Go de documents sur disque USB, copie vérifiée. Actions : pilote de stockage VMD chargé dans l'installateur, Windows 11 Famille installé (édition de la licence), pilotes réseau et graphique installés.",
            "Contrôles : Windows activé, Windows Update à jour, Defender actif, chiffrement activé. Remise : données restaurées et vérifiées avec le client, clé de récupération remise sur papier. Recommandations : batterie à 71 % de sa capacité d'origine, à surveiller ou remplacer ; sauvegarde régulière des documents. Date et signatures.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Corriger la procédure d'un collègue",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_ERROR,
        context=(
            "Un collègue a réinstallé le PC d'une comptable (SSD système et disque dur de "
            "données) et propose sa procédure comme modèle pour l'atelier. Ton responsable te "
            "demande de la relire avant de l'afficher. Elle est reproduite dans le document 1."
        ),
        documents=(
            _table(
                "Document 1 — Procédure proposée (fictive)",
                ("N°", "Étape"),
                ("1", "Accord de la cliente au téléphone, pas de sauvegarde : « tout est sur le disque D: »"),
                ("2", "Image de Windows 11 téléchargée sur un site de partage, plus rapide"),
                ("3", "Démarrage sécurisé désactivé « pour que la clé démarre »"),
                ("4", "Suppression de toutes les partitions des deux disques, pour repartir propre"),
                ("5", "Édition Professionnel installée, la licence du PC étant une OEM Famille"),
                ("6", "Un seul compte administrateur sans mot de passe « pour la cliente »"),
                ("7", "PC rendu sans contrôle, la cliente vérifiera"),
            ),
        ),
        instructions=("Relève les erreurs et rédige, pour chacune, la pratique correcte.",),
        criteria=(
            _c("Données", 1, "1 et 4 : accord écrit et sauvegarde vérifiée ; on ne supprime que les partitions du disque cible, jamais celles de D: (données perdues)."),
            _c("Installation", 1, "2 : image officielle, somme contrôlée ; 3 : démarrage sécurisé laissé actif (clé officielle en UEFI) ; 5 : édition Famille, celle de la licence."),
            _c("Remise", 1, "6 : administrateur protégé par mot de passe, compte standard ; 7 : liste de contrôle et rapport, vérification avec la cliente."),
        ),
        correction=(
            "1. Un accord au téléphone ne suffit pas : accord écrit, et sauvegarde vérifiée même si les données sont « sur D: ». 4. Supprimer les partitions des deux disques a effacé D: : on ne supprime que celles du disque cible (le SSD), après identification par la taille. 2. Une image d'un site de partage peut être modifiée : image officielle et somme contrôlée.",
            "3. Une clé officielle démarre avec le démarrage sécurisé en choisissant l'entrée « UEFI: » : on le laisse actif. 5. Une licence OEM Famille n'active pas Professionnel : installer Famille. 6. Un compte administrateur sans mot de passe expose tout : administrateur protégé et compte standard au quotidien. 7. On passe la liste de contrôle avec la cliente et on rédige un rapport signé.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (10 questions de 2 points, uniquement dans « Examen blanc »)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Windows n'est pas activé après la réinstallation",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-08"),
        kind=KIND_PREP,
        context=(
            "Un stagiaire a réinstallé le portable d'une infirmière, vendu avec Windows 11 "
            "Famille préinstallé (licence OEM, clé dans le firmware). Il a choisi l'édition "
            "Professionnel « pour avoir plus de fonctions ». Paramètres affiche « Windows n'est "
            "pas activé ». L'infirmière n'a besoin d'aucune fonction de l'édition Professionnel."
        ),
        instructions=("Explique la cause et rédige ce que tu fais.",),
        criteria=(
            _c("Cause", 1, "Licence OEM Famille : elle n'active que l'édition Famille ; l'édition installée n'est pas celle de la licence."),
            _c("Action", 1, "Réinstaller l'édition Famille (l'activation est alors automatique) ; contrôler « Windows est activé » ; pas de clé ou d'activateur douteux ; acheter une mise à niveau seulement si le besoin existait."),
        ),
        correction=(
            f"Verdict : « {X01_RESULT} » ({X01_WHY}). Une licence OEM Famille n'active que l'édition Famille.",
            "On réinstalle l'édition Famille (sauvegarde vérifiée si des données ont déjà été ajoutées) : la clé du firmware l'active automatiquement ; on contrôle dans Paramètres → Système → Activation. Jamais de clé trouvée sur Internet ni d'activateur. L'édition Professionnel ne s'achète que si un vrai besoin existe (domaine, BitLocker…).",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Choisir l'emplacement sur un PC à deux disques",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_INSTALL,
        context=(
            "Tu réinstalles Windows 11 sur le PC d'un photographe, avec son accord écrit et une "
            "sauvegarde vérifiée de son ancien système. Il garde ses photos sur un second disque "
            "qu'il ne veut surtout pas perdre. L'installateur affiche le document 1 ; tu n'as "
            "pas pu ouvrir le boîtier pour débrancher le second disque."
        ),
        documents=(
            _console(
                "Document 1 — Installateur (capture fictive)",
                "Lecteur 0 Partition 1           100 Mo  Système",
                "Lecteur 0 Partition 2            16 Mo  MSR",
                "Lecteur 0 Partition 3: Windows  237 Go  Principale",
                "Lecteur 0 Partition 4           600 Mo  Récupération",
                "Lecteur 1 Partition 1: PHOTOS   1,8 To  Principale",
            ),
        ),
        instructions=("Indique le disque cible, les partitions que tu supprimes et ce que tu ne touches pas, en justifiant.",),
        criteria=(
            _c("Cible", 1, f"Lecteur 0 (SSD de 238 Go, ancien Windows) : supprimer ses 4 partitions ({X02_ACTIONS[0].lower()}), puis installer sur l'espace non alloué."),
            _c("Protection", 1, f"Lecteur 1 PHOTOS (1,8 To) : {X02_ACTIONS[1].lower()} ; vérifier ensuite que l'ESP a été créée sur le lecteur 0."),
        ),
        correction=(
            "Le disque cible est le lecteur 0 (environ 238 Go), qui porte l'ancien Windows (Système, MSR, Windows, Récupération) : avec l'accord écrit et la sauvegarde vérifiée, on supprime ses quatre partitions et on installe sur l'espace non alloué ; l'installateur recrée la disposition GPT.",
            "Le lecteur 1 (1,8 To, PHOTOS) est un autre disque : on n'y touche pas (ni suppression, ni formatage). Comme il est resté branché, on vérifie après l'installation, dans Gestion des disques, que la partition système EFI est bien sur le lecteur 0.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="L'installateur ne voit pas le SSD",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-09"),
        kind=KIND_TROUBLE,
        context=(
            "Sur un portable professionnel récent, l'installateur de Windows 11 affiche « Nous "
            "n'avons trouvé aucun lecteur ». Dans le firmware, l'onglet Stockage montre le SSD "
            "NVMe de 1 To, et l'option « Intel VMD » est activée. Le portable doit être rendu "
            "demain."
        ),
        instructions=("Explique la cause et rédige la marche à suivre.",),
        criteria=(
            _c("Cause", 1, "Le SSD est détecté par le firmware : pilote du contrôleur Intel VMD absent de l'installateur."),
            _c("Marche", 1, "Pilote de stockage du fabricant (F6) sur la clé, « Charger un pilote » ; le SSD apparaît ; poursuivre. Ne pas conclure à une panne."),
        ),
        correction=(
            "Le firmware voit le SSD : il n'est pas en panne. Le contrôleur fonctionne en mode Intel VMD et l'installateur n'a pas le pilote de ce contrôleur.",
            "On télécharge sur le site du fabricant du portable le pilote de stockage Intel RST/VMD (version F6 à extraire), on le copie sur la clé, puis « Charger un pilote » dans l'installateur : le SSD apparaît et l'installation se poursuit.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Préparer la réinstallation d'un poste de secrétariat",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Une école demande la réinstallation propre de Windows 11 Professionnel sur le PC du "
            "secrétariat, infecté par un logiciel publicitaire. Le PC contient les fichiers des "
            "inscriptions, un logiciel de gestion scolaire avec sa clé, et une imprimante "
            "multifonction est branchée en USB. L'intervention est prévue demain matin."
        ),
        instructions=("Rédige ta préparation, dans l'ordre, jusqu'au démarrage sur la clé.",),
        criteria=(
            _c("Données", 1, "Accord écrit de la direction ; inventaire (modèle, édition et licence, disques, firmware) ; sauvegarde vérifiée des fichiers d'inscription, sans y copier d'exécutables suspects (analyse antivirus de la copie)."),
            _c("Média et pilotes", 1, "Image officielle, somme contrôlée, clé de 8 Go ; pilotes stockage, réseau et imprimante du fabricant ; clé du logiciel scolaire relevée."),
        ),
        correction=(
            "1. Accord écrit de la direction. 2. Inventaire : modèle, édition et licence (Professionnel), disques, mode du firmware et du stockage. 3. Sauvegarde des fichiers d'inscription sur un support externe, copie vérifiée ; on ne sauvegarde que des données (pas de programmes) et on analyse la copie avec l'antivirus, le PC étant infecté.",
            "4. Image officielle de Windows 11 téléchargée sur le site de Microsoft, somme contrôlée, clé USB de 8 Go au moins. 5. Pilotes de stockage, de réseau et de l'imprimante multifonction téléchargés chez les fabricants et copiés sur la clé ; clé et installateur du logiciel scolaire relevés. L'installation propre se justifie : une mise à niveau garderait l'infection.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Windows installé en mode hérité par erreur",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-09"),
        kind=KIND_INSTALL,
        context=(
            "Un stagiaire a installé Windows 10 sur un PC compatible, prévu pour passer à "
            "Windows 11 plus tard. En contrôlant son travail, tu relèves le document 1. Il "
            "avait choisi, dans le menu de démarrage, l'entrée de la clé qui ne commençait pas "
            "par « UEFI: »."
        ),
        documents=(
            _console(
                "Document 1 — msinfo32 et Gestion des disques (fictif)",
                "Mode BIOS                     Hérité",
                "État du démarrage sécurisé    Non pris en charge",
                "Gestion des disques : Disque 0 — style MBR",
            ),
        ),
        instructions=("Interprète le relevé et rédige la correction la plus simple.",),
        criteria=(
            _c("Lecture", 1, "Clé démarrée en mode hérité : Windows installé sur un disque MBR, sans démarrage sécurisé ; Windows 11 refusera la mise à niveau."),
            _c("Correction", 1, "Installation récente : réinstaller en démarrant l'entrée « UEFI: » (le disque devient GPT) ; ou mbr2gpt /validate puis /convert /allowFullOS, puis firmware en UEFI et démarrage sécurisé activé ; contrôle dans msinfo32."),
        ),
        correction=(
            "La clé a démarré en mode hérité : Windows a été installé sur un disque MBR, sans démarrage sécurisé (« Non pris en charge »). Le PC ne pourra pas passer à Windows 11, qui exige l'UEFI.",
            "L'installation est récente, sans données : le plus simple est de réinstaller en choisissant l'entrée « UEFI: » de la clé (l'installateur crée un disque GPT). Autre voie sans réinstaller : mbr2gpt /validate /allowFullOS puis mbr2gpt /convert /allowFullOS, ensuite firmware en UEFI et démarrage sécurisé activé. Contrôle : msinfo32 affiche « UEFI » et « Activé ».",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Plus de réseau après l'installation",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-05"),
        kind=KIND_TROUBLE,
        context=(
            "Après une installation propre de Windows 11 sur le PC de bureau d'une boulangerie, "
            "aucune connexion n'est possible, ni par câble ni en Wi-Fi. Windows Update est donc "
            "inaccessible. Le Gestionnaire de périphériques affiche le document 1. Ton "
            "smartphone et le PC de l'atelier ont Internet."
        ),
        documents=(
            _console(
                "Document 1 — Gestionnaire de périphériques (fictif)",
                "v Autres périphériques",
                "    (!) Contrôleur Ethernet",
                "Contrôleur Ethernet → ID du matériel :",
                f"  {X06_ID}",
            ),
        ),
        instructions=("Identifie le matériel et rédige comment rétablir le réseau.",),
        criteria=(
            _c("Identification", 0.75, f"Contrôleur Ethernet sans pilote ; VEN_10EC = {X06_VENDOR} ; DEV précise la puce."),
            _c("Rétablir", 1.25, "Pilote du fabricant de la carte mère (ou de Realtek) téléchargé sur le PC de l'atelier, copié par clé USB, installé ; contrôle : plus de (!) et adresse obtenue (ipconfig /all) ; puis Windows Update."),
        ),
        correction=(
            "Le contrôleur Ethernet n'a pas de pilote (point d'exclamation). VEN_10EC désigne Realtek ; DEV_8125 précise le modèle de la puce réseau.",
            "Sur le PC de l'atelier, on télécharge le pilote réseau sur le site du fabricant de la carte mère (ou de Realtek), on le copie sur une clé USB et on l'installe. Contrôle : plus de point d'exclamation, adresse obtenue (ipconfig /all), navigation possible ; on lance ensuite Windows Update pour les autres pilotes et mises à jour.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="L'installation recommence sans fin",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-09"),
        kind=KIND_TROUBLE,
        context=(
            "Une stagiaire installe Windows 11 sur un PC dont elle a mis la clé USB en premier "
            "dans l'ordre de démarrage du firmware. Après la copie des fichiers, le PC redémarre "
            "et l'écran de choix de la langue réapparaît. Elle s'apprête à supprimer à nouveau "
            "les partitions pour « recommencer proprement »."
        ),
        instructions=("Explique ce qui se passe et ce qu'elle doit faire.",),
        criteria=(
            _c("Explication", 1, "Le PC redémarre sur la clé (premier dans l'ordre) au lieu du disque où l'installation continue ; rien n'a échoué."),
            _c("Action", 1, "Ne pas supprimer les partitions ; retirer la clé ou mettre « Windows Boot Manager » en premier ; redémarrer : l'installation continue."),
        ),
        correction=(
            "L'installation n'a pas échoué : après la copie, le PC redémarre sur le premier périphérique de l'ordre de démarrage, la clé, et relance l'installateur au lieu de poursuivre depuis le disque.",
            "Elle ne supprime rien (elle effacerait la copie déjà faite) ; elle retire la clé ou place « Windows Boot Manager » en premier dans le firmware, puis redémarre : l'installation se poursuit jusqu'à la configuration initiale.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="La liste de contrôle avant de rendre le PC",
        question_type="long_answer",
        requirement_ids=("AP-10", "AP-11"),
        kind=KIND_POST,
        context=(
            "Ton responsable veut une liste de contrôle à passer avec le client avant de rendre "
            "un PC réinstallé sous Windows 11. Elle doit tenir sur une demi-page, citer pour "
            "chaque point l'outil utilisé et le résultat attendu, et servir de base au rapport "
            "d'intervention."
        ),
        instructions=("Rédige cette liste de contrôle (au moins six points : outil et résultat attendu).",),
        criteria=(
            _c("Système", 1, "Activation (Paramètres → Activation : activé) ; msinfo32 (UEFI, démarrage sécurisé activé) ; Gestionnaire de périphériques (aucun inconnu) ; Windows Update (à jour)."),
            _c("Client", 1, "Sécurité Windows (antivirus, pare-feu), comptes (administrateur protégé, standard), réseau, données restaurées et logiciels testés avec le client, clé de récupération remise."),
        ),
        correction=(
            "Système : Paramètres → Système → Activation, « Windows est activé » ; msinfo32, « Mode BIOS : UEFI » et démarrage sécurisé « Activé » ; Gestionnaire de périphériques, aucun périphérique inconnu ; Windows Update, « Vous êtes à jour » ; Gestion des disques, GPT avec ESP, Windows et Récupération.",
            "Client : Sécurité Windows, antivirus et pare-feu actifs ; comptes, administrateur protégé et compte standard ; réseau, ipconfig /all et navigation ; données restaurées et logiciels, imprimante testés devant le client ; clé de récupération remise. Chaque résultat est reporté dans le rapport.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="« Effacez tout » au téléphone",
        question_type="short_answer",
        requirement_ids=("AP-10", "AP-C03"),
        kind=KIND_PREP,
        context=(
            "Un client dépose le PC familial et dit au téléphone : « effacez tout et réinstallez, "
            "c'est plus simple ». En faisant l'inventaire, tu découvres sur le bureau un compte "
            "au nom de son épouse contenant un dossier « Comptabilité indépendante 2026 ». Le "
            "client est injoignable jusqu'à demain."
        ),
        instructions=("Rédige ce que tu fais avant toute installation, en justifiant.",),
        criteria=(
            _c("Arrêt", 1, "Ne rien effacer : un accord oral ne suffit pas, et les données d'une autre personne sont concernées."),
            _c("Régulariser", 1, "Accord écrit précisant les données à garder ; sauvegarde de tous les profils, vérifiée ; confidentialité (pas de consultation des fichiers) ; noté dans le rapport."),
        ),
        correction=(
            "On n'efface rien : un « effacez tout » au téléphone n'est pas un accord écrit, et le PC contient les données professionnelles d'une autre personne, qui n'a rien autorisé.",
            "On attend l'accord écrit, en signalant le dossier découvert et en demandant ce qu'il faut garder ; par prudence, on sauvegarde tous les profils et on vérifie la copie, sans consulter les fichiers (confidentialité). On note tout dans le rapport ; l'installation n'a lieu qu'après l'accord.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Écran bleu après un réglage du firmware",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-13"),
        kind=KIND_TROUBLE,
        context=(
            "Hier, Windows 11 a été installé sur un PC de bureau dont le contrôleur de stockage "
            "était réglé en mode RAID (pilote chargé pendant l'installation). Ce matin, un "
            "collègue a passé le contrôleur en AHCI dans le firmware « pour gagner en "
            "performances ». Depuis, le PC affiche le document 1 à chaque démarrage."
        ),
        documents=(
            _console(
                "Document 1 — Écran au démarrage (fictif)",
                "Votre PC a rencontré un problème et doit redémarrer.",
                "Code d'arrêt : INACCESSIBLE_BOOT_DEVICE",
            ),
        ),
        instructions=("Explique la cause et rédige la correction.",),
        criteria=(
            _c("Cause", 1, "Windows démarre avec le pilote du contrôleur en mode RAID ; en AHCI, il ne trouve plus son disque de démarrage."),
            _c("Correction", 1, "Remettre le mode d'origine (RAID) dans le firmware ; Windows redémarre ; on ne change pas ce mode après l'installation (ou seulement avec la procédure de l'éditeur) ; noter le mode dans le rapport."),
        ),
        correction=(
            "INACCESSIBLE_BOOT_DEVICE : Windows ne peut plus accéder à son disque de démarrage. Il a été installé avec le pilote du contrôleur en mode RAID ; en AHCI, ce pilote ne correspond plus.",
            "On remet le contrôleur dans son mode d'origine (RAID) dans le firmware : Windows redémarre normalement. On ne change plus ce réglage après l'installation (sinon seulement selon la procédure documentée par Microsoft ou le fabricant) et on note le mode du stockage dans le rapport. Le dépannage des écrans d'arrêt est approfondi en PR11.",
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

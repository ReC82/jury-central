"""PR08 « Installation complète de Windows — préparation et dépannage » — données de
référence, règles de décision et schémas SVG (ticket #208).

Tout est construit **depuis des données** de ce module (tuples, fonctions), contrôlées par
`tests/test_ticket208_ampcr_pratique_pr08.py` :

- l'inventaire du poste (`INVENTORY_FIELDS`) et la migration des données (`MIGRATION_ITEMS`) ;
- les licences et l'activation (`activation_result`) ;
- la disposition standard d'un disque GPT après installation (`STANDARD_LAYOUT`) et la règle
  de prudence sur les partitions (`partition_action`) ;
- le dépannage de l'installation (`TROUBLESHOOTING`) : stockage non détecté, démarrage,
  partitionnement, pilotes manquants, activation ;
- l'identification d'un matériel par son identifiant (`VENDOR_IDS`, `vendor_of`) ;
- trois procédures illustrées (`PREP_STEPS`, `SETUP_STEPS`, `FINAL_STEPS`) : les mêmes tuples
  dessinent les schémas et alimentent les remises en ordre des exercices ;
- la liste de contrôle finale (`CHECKLIST`) et le plan du rapport d'intervention
  (`REPORT_SECTIONS`).

Les écrans de l'installateur cités sont ceux de **Windows 11 au moment de la rédaction
(octobre 2026)** ; leurs libellés changent selon la version : la documentation de Microsoft fait
foi. Les captures (installateur, Gestionnaire de périphériques, invite de commandes) sont
**fictives** et leurs libellés approximatifs ; aucun schéma ne vient d'une image générée ni
d'une photographie.
"""

from dataclasses import dataclass

from app.v1.ampcr_pratique_visuals import (
    Figure,
    PartitionSegment,
    decision_tree_svg,
    partition_map_svg,
    screen_svg,
    step_flow_svg,
)

SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR07)
WRITTEN_AT = "octobre 2026"
FICTIVE_LABEL = "Capture fictive — libellés approximatifs"

# =============================================================================================
# 1. Inventaire du poste avant l'intervention
# =============================================================================================

# (rubrique de la fiche, ce qu'on relève, pourquoi)
INVENTORY_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("Identification", "Marque, modèle, numéro de série, propriétaire",
     "Retrouver les pilotes du fabricant et tracer l'intervention."),
    ("Processeur et mémoire", "Modèle du processeur, 64 bits, quantité de mémoire",
     "Comparer aux prérequis de la version visée (PR07)."),
    ("Stockage", "Disques (type, capacité, style MBR ou GPT), partitions, données présentes",
     "Choisir le disque cible et repérer ce qu'il faut sauvegarder."),
    ("Firmware", "Mode UEFI ou hérité, démarrage sécurisé, TPM, mode du contrôleur (AHCI, RAID, VMD)",
     "Prévoir les réglages et le pilote de stockage."),
    ("Système et licence", "Version et édition installées, type de licence (OEM, commerciale, numérique)",
     "Réinstaller la même édition pour que l'activation réussisse."),
    ("Logiciels et périphériques", "Programmes à réinstaller et leurs clés, imprimantes, scanners",
     "Ne rien oublier après l'installation propre."),
    ("Réseau", "Carte Ethernet et Wi-Fi (modèle), nom et clé du Wi-Fi",
     "Disposer du réseau pendant la configuration initiale."),
)

# =============================================================================================
# 2. Licences et activation
# =============================================================================================

LIC_OEM = "OEM (préinstallée par le fabricant)"
LIC_RETAIL = "Commerciale (boîte ou clé achetée)"
LIC_DIGITAL = "Licence numérique (liée au matériel)"

ACTIVATES = "S'active (automatiquement ou avec la clé)"
NOT_ACTIVATED = "Ne s'active pas : corriger avant de rendre le PC"
ACTIVATION_RESULTS = (ACTIVATES, NOT_ACTIVATED)


def activation_result(licence: str, licence_edition: str, installed_edition: str, *,
                      same_pc: bool, removed_from_old_pc: bool = True) -> tuple[str, str]:
    """(résultat, raison) selon les règles du cours : l'édition installée doit être celle de
    la licence ; une licence OEM ou numérique reste liée au PC d'origine ; une licence
    commerciale se transfère si elle est retirée de l'ancien PC."""
    if licence not in (LIC_OEM, LIC_RETAIL, LIC_DIGITAL):
        raise ValueError(licence)
    if installed_edition != licence_edition:
        return NOT_ACTIVATED, "l'édition installée n'est pas celle de la licence"
    if licence in (LIC_OEM, LIC_DIGITAL) and not same_pc:
        return NOT_ACTIVATED, "une licence OEM ou numérique reste liée au PC d'origine"
    if licence == LIC_RETAIL and not same_pc and not removed_from_old_pc:
        return NOT_ACTIVATED, "la licence commerciale est encore utilisée sur l'ancien PC"
    return ACTIVATES, "licence et édition concordantes"


# =============================================================================================
# 3. Disque et partitions
# =============================================================================================


@dataclass(frozen=True)
class StandardPartition:
    key: str
    name: str
    filesystem: str
    size_label: str
    role: str


# Disposition créée par l'installateur sur un disque vide, en mode UEFI (documentation Microsoft
# « partitions de disque dur UEFI/GPT » ; tailles indicatives, variables selon la version).
STANDARD_LAYOUT: tuple[StandardPartition, ...] = (
    StandardPartition("esp", "Partition système EFI (ESP)", "FAT32", "≈ 100 Mo",
                      "Chargeur de démarrage lu par le firmware UEFI."),
    StandardPartition("msr", "Partition réservée Microsoft (MSR)", "aucun", "16 Mo",
                      "Réservée au système, sans lettre ni contenu visible."),
    StandardPartition("windows", "Windows (C:)", "NTFS", "le reste",
                      "Système, programmes et dossiers des utilisateurs."),
    StandardPartition("recovery", "Récupération", "NTFS", "≈ 0,5-1 Go",
                      "Environnement de récupération Windows (WinRE)."),
)

PART_DELETE = "Supprimer (sauvegarde vérifiée et accord écrit)"
PART_KEEP = "Ne pas toucher"
PART_STOP = "Arrêter : sauvegarde et accord d'abord"
PARTITION_ACTIONS = (PART_DELETE, PART_KEEP, PART_STOP)


def partition_action(*, on_target_disk: bool, backup_verified: bool, written_consent: bool) -> str:
    """Ce que le technicien fait d'une partition affichée par l'installateur : on ne supprime
    que sur le disque cible, après sauvegarde vérifiée ET accord écrit ; jamais ailleurs."""
    if not on_target_disk:
        return PART_KEEP
    if not (backup_verified and written_consent):
        return PART_STOP
    return PART_DELETE


# Libellés courts et largeurs relatives (lisibilité à 380 px ; pas à l'échelle).
_SHORT_NAMES = {"esp": "ESP", "msr": "MSR", "windows": "Windows C:", "recovery": "Récupération"}
_WEIGHTS = {"esp": 3, "msr": 2, "windows": 4, "recovery": 4}

LAYOUT_FIGURE = Figure(
    key="pr08-partitions-gpt",
    title="Disque système en GPT après une installation propre (mode UEFI)",
    alt=(
        "Plan de partitionnement d'un disque GPT, du début à la fin du disque : "
        + " ; ".join(f"{p.name}, {p.filesystem}, {p.size_label} : {p.role}" for p in STANDARD_LAYOUT)
        + ". Les largeurs ne sont pas à l'échelle."
    ),
    caption=(
        "Sur un espace non alloué, l'installateur crée lui-même ces quatre partitions et le style "
        "GPT. Tailles indicatives (documentation Microsoft) ; largeurs non à l'échelle."
    ),
    svg=partition_map_svg((
        ("Disque 0 — SSD 500 Go, style GPT",
         tuple(PartitionSegment(p.key, (_SHORT_NAMES[p.key], p.filesystem, p.size_label), _WEIGHTS[p.key])
               for p in STANDARD_LAYOUT)),
    )),
)

# =============================================================================================
# 4. Dépannage de l'installation
# =============================================================================================

TR_STORAGE = "Pilote de stockage (VMD, RST, RAID)"
TR_BOOT = "Mode ou ordre de démarrage"
TR_PARTITION = "Partitions : style MBR/GPT ou emplacement"
TR_DRIVER = "Pilote de périphérique manquant"
TR_LICENCE = "Licence ou édition"
TR_CATEGORIES = (TR_STORAGE, TR_BOOT, TR_PARTITION, TR_DRIVER, TR_LICENCE)


@dataclass(frozen=True)
class Trouble:
    category: str
    symptom: str
    check: str
    action: str
    never: str


TROUBLESHOOTING: tuple[Trouble, ...] = (
    Trouble(
        TR_STORAGE,
        "« Nous n'avons trouvé aucun lecteur » alors que le firmware affiche le SSD",
        "Firmware : contrôleur de stockage en mode RAID ou Intel VMD/RST ; notice du fabricant.",
        "« Charger un pilote » : pilote de stockage du fabricant (dossier F6) copié sur la clé ; "
        "ou, sur un disque sans données, mode AHCI si la notice le permet.",
        "Conclure « SSD en panne », ou changer le mode du contrôleur d'un Windows déjà installé.",
    ),
    Trouble(
        TR_STORAGE,
        "Le firmware lui-même ne voit aucun disque",
        "Branchement, câble SATA, port M.2 compatible (NVMe ou SATA), disque testé ailleurs.",
        "Diagnostic matériel (PR05, PR06) avant toute installation.",
        "Lancer l'installation en espérant que le disque « apparaîtra ».",
    ),
    Trouble(
        TR_BOOT,
        "La clé n'apparaît pas en « UEFI: » dans le menu de démarrage, ou rien ne démarre",
        "Clé écrite en schéma MBR seulement ; démarrage sécurisé refusant un média non officiel ; "
        "port USB.",
        "Réécrire la clé depuis l'image officielle (schéma GPT pour l'UEFI) ; démarrer l'entrée "
        "« UEFI: » ; autre port USB.",
        "Désactiver le démarrage sécurisé ou passer en mode hérité pour « forcer » Windows 11.",
    ),
    Trouble(
        TR_BOOT,
        "Après le premier redémarrage, l'installation recommence depuis le début",
        "Ordre de démarrage : la clé USB passe avant le disque.",
        "Retirer la clé au redémarrage ou mettre « Windows Boot Manager » en premier.",
        "Supprimer à nouveau les partitions et réinstaller.",
    ),
    Trouble(
        TR_PARTITION,
        "« Windows ne peut être installé que sur des disques GPT » (systèmes EFI)",
        "Gestion du disque dans l'installateur ou diskpart (list disk) : disque MBR, données ?",
        "Disque sans données ou sauvegardé avec accord écrit : supprimer ses partitions pour "
        "obtenir un espace non alloué (GPT créé par l'installateur) ; Windows à garder : mbr2gpt.",
        "Basculer le firmware en mode hérité, ou effacer sans sauvegarde ni accord.",
    ),
    Trouble(
        TR_PARTITION,
        "Le PC ne démarre plus quand on débranche le second disque",
        "Gestion des disques : la partition système EFI utilisée est sur l'autre disque (ancien système).",
        "Installation propre récente : réinstaller avec le seul disque cible branché ; "
        "sinon réparation du démarrage (PR11).",
        "Formater le second disque, qui contient le chargeur et peut-être des données.",
    ),
    Trouble(
        TR_DRIVER,
        "Pas de réseau ; « Contrôleur Ethernet » ou « Périphérique inconnu » avec un triangle",
        "Gestionnaire de périphériques → Propriétés → Détails → ID du matériel (VEN, DEV).",
        "Pilote du fabricant téléchargé sur un autre PC et copié par clé USB ; puis Windows Update "
        "(mises à jour facultatives).",
        "Installer un « pack de pilotes » d'un site inconnu.",
    ),
    Trouble(
        TR_DRIVER,
        "Affichage en basse résolution, « Carte graphique de base Microsoft »",
        "Gestionnaire de périphériques, Cartes graphiques ; modèle de la carte (ID du matériel).",
        "Pilote graphique du fabricant (ou Windows Update), après celui du chipset.",
        "Changer d'écran ou réinstaller Windows.",
    ),
    Trouble(
        TR_LICENCE,
        "« Windows n'est pas activé » après l'installation",
        "Paramètres → Système → Activation ; slmgr /xpr ; édition installée et type de licence.",
        "Installer l'édition de la licence, saisir la bonne clé ou lancer l'utilitaire de résolution "
        "des problèmes d'activation ; informer le client si la licence ne suit pas le PC.",
        "Utiliser un activateur ou une clé trouvée sur Internet.",
    ),
)

TROUBLES_BY_CATEGORY: dict[str, tuple[Trouble, ...]] = {
    c: tuple(t for t in TROUBLESHOOTING if t.category == c) for c in TR_CATEGORIES
}

NO_DRIVE_TREE: tuple[tuple[str, str], ...] = (
    ("Le firmware (UEFI) détecte-t-il le disque ?",
     "Matériel : branchement, câble, port M.2 compatible, disque (PR05, PR06)."),
    ("L'installateur liste-t-il le disque ?",
     "Pilote de stockage (VMD, RST, RAID) : « Charger un pilote » depuis la clé."),
    ("Le disque est-il en GPT, ou vide ?",
     "Disque MBR : sauvegarde et accord écrit, puis supprimer ses partitions (ou mbr2gpt)."),
    ("La cible est-elle libre (espace non alloué) ?",
     "Supprimer les partitions de l'ancien système après accord ; jamais celles des données."),
)
NO_DRIVE_FINAL = (
    "Sélectionner l'espace non alloué du disque cible : l'installateur crée ESP, MSR, Windows "
    "et Récupération."
)

NO_DRIVE_FIGURE = Figure(
    key="pr08-disque-introuvable",
    title="Arbre de décision — l'installateur ne propose pas le bon disque",
    alt=(
        "Arbre de décision en quatre questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(NO_DRIVE_TREE, start=1))
        + f" Si toutes les réponses sont oui : {NO_DRIVE_FINAL}"
    ),
    caption=(
        "On part du matériel (le firmware voit-il le disque ?) avant de toucher aux partitions. "
        "Aucune suppression sans sauvegarde vérifiée et accord écrit."
    ),
    svg=decision_tree_svg(NO_DRIVE_TREE, NO_DRIVE_FINAL),
)

# Identifiants de fabricants (PCI-SIG, liste publique des Vendor ID).
VENDOR_IDS: dict[str, str] = {
    "8086": "Intel",
    "10EC": "Realtek",
    "10DE": "NVIDIA",
    "1022": "AMD",
    "14E4": "Broadcom",
}


def vendor_of(hardware_id: str) -> str | None:
    """Fabricant d'après « PCI\\VEN_xxxx&DEV_yyyy… » (None si inconnu de la table du cours)."""
    marker = "VEN_"
    if marker not in hardware_id:
        return None
    code = hardware_id.split(marker, 1)[1][:4].upper()
    return VENDOR_IDS.get(code)


# =============================================================================================
# 5. Migration des données vers la nouvelle installation
# =============================================================================================

# (élément, où le trouver, comment le transférer)
MIGRATION_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("Documents, Bureau, Images, Téléchargements", "C:\\Users\\<nom> (un dossier par compte)",
     "Copie sur disque externe, vérifiée (nombre et taille des fichiers), puis restauration."),
    ("Dossiers hors profil", "Ex. C:\\Compta, D:\\Photos",
     "Demander au client et rechercher : un dossier hors profil s'oublie facilement."),
    ("Favoris et mots de passe du navigateur", "Profil du navigateur",
     "Synchronisation du compte du navigateur ou exportation chiffrée, avec le client."),
    ("Courrier", "Compte IMAP / Exchange, ou fichier de données local (.pst)",
     "Compte en ligne : reconfigurer ; fichier local : le copier puis l'importer."),
    ("Logiciels et licences", "Liste des programmes, clés, comptes des éditeurs",
     "Relever les clés ; désactiver une licence limitée à un nombre de PC sur l'ancien poste."),
    ("Imprimantes et réseau", "Modèles, pilotes, nom et clé du Wi-Fi",
     "Pilotes du fabricant ; reconnecter et faire une page de test."),
)

# =============================================================================================
# 6. Procédures illustrées
# =============================================================================================

# Procédure 1 — préparer l'installation.
PREP_STEPS: tuple[tuple[str, str], ...] = (
    ("Recueillir la demande", "Besoin, données à garder, accord écrit du client pour l'effacement."),
    ("Inventorier le poste", "Modèle, processeur, mémoire, disques, firmware, édition et licence."),
    ("Vérifier la compatibilité", "Prérequis de la version visée (PR07) ; pilotes du fabricant disponibles."),
    ("Sauvegarder", "Données et profils copiés sur un autre support ; copie vérifiée."),
    ("Préparer le média", "Image officielle, somme contrôlée, clé USB de 8 Go au moins."),
    ("Préparer les pilotes", "Stockage (dossier F6) et réseau copiés sur la clé ou une seconde clé."),
)

# Procédure 2 — installer Windows (de la clé au bureau).
SETUP_STEPS: tuple[tuple[str, str], ...] = (
    ("Régler le firmware", "Mode UEFI, démarrage sécurisé, TPM 2.0 ; mode du stockage noté."),
    ("Démarrer sur la clé", "Menu de démarrage (F12, F11, F8, Échap) : entrée « UEFI: »."),
    ("Langue, format et clavier", "Langue d'installation, format régional, clavier (ex. belge AZERTY)."),
    ("Clé et édition", "Clé saisie, ou « Je n'ai pas de clé » ; édition = celle de la licence."),
    ("Type d'installation", "Installation propre : « Personnalisée » (Windows uniquement)."),
    ("Disque et partitions", "Disque cible identifié par sa taille ; espace non alloué sélectionné."),
    ("Copie et redémarrages", "Laisser faire ; retirer la clé si l'installateur redémarre."),
    ("Configuration initiale", "Région, clavier, réseau, compte et mot de passe, confidentialité."),
)

# Procédure 3 — finaliser, sécuriser et valider.
FINAL_STEPS: tuple[tuple[str, str], ...] = (
    ("Pilotes", "Chipset, stockage, réseau puis graphique ; aucun périphérique inconnu."),
    ("Mises à jour", "Windows Update jusqu'à « Vous êtes à jour », mises à jour facultatives des pilotes."),
    ("Activation", "Paramètres → Système → Activation : « Windows est activé »."),
    ("Sécurité", "Defender et pare-feu actifs, compte standard, chiffrement et clé de récupération."),
    ("Restauration", "Données du client restaurées ; point de restauration ou lecteur de récupération."),
    ("Contrôler et documenter", "Liste de contrôle passée, client présent ; rapport d'intervention signé."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Préparer l'installation", PREP_STEPS),
    ("Installer Windows, de la clé au bureau", SETUP_STEPS),
    ("Finaliser, sécuriser et valider", FINAL_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


PREP_FIGURE = Figure(
    key="pr08-preparer",
    title="Procédure 1 — Préparer l'installation",
    alt=_procedure_alt("Préparation d'une installation de Windows.", PREP_STEPS),
    caption=(
        "Rien n'est effacé avant l'accord écrit et la sauvegarde vérifiée. Les pilotes de stockage "
        "et de réseau se préparent avant : sans eux, l'installateur peut ne voir ni disque ni réseau."
    ),
    svg=step_flow_svg(PREP_STEPS),
)

SETUP_FIGURE = Figure(
    key="pr08-installer",
    title="Procédure 2 — Installer Windows, de la clé au bureau",
    alt=_procedure_alt("Déroulement de l'installation de Windows.", SETUP_STEPS),
    caption=(
        "Les libellés des écrans varient selon la version de l'installateur ; l'ordre des "
        "décisions reste le même."
    ),
    svg=step_flow_svg(SETUP_STEPS),
)

FINAL_FIGURE = Figure(
    key="pr08-finaliser",
    title="Procédure 3 — Finaliser, sécuriser et valider",
    alt=_procedure_alt("Finalisation d'une installation de Windows.", FINAL_STEPS),
    caption=(
        "Un PC n'est rendu qu'activé, à jour, sans périphérique inconnu, avec les données du "
        "client restaurées et vérifiées devant lui."
    ),
    svg=step_flow_svg(FINAL_STEPS),
)

# =============================================================================================
# 7. Liste de contrôle et rapport d'intervention
# =============================================================================================

# (point contrôlé, où / comment, résultat attendu)
CHECKLIST: tuple[tuple[str, str, str], ...] = (
    ("Version et édition", "winver ; Paramètres → Système → Informations système", "Version et édition prévues"),
    ("Activation", "Paramètres → Système → Activation ; slmgr /xpr", "« Windows est activé »"),
    ("Démarrage", "msinfo32", "Mode BIOS : UEFI ; démarrage sécurisé : Activé"),
    ("Disque", "Gestion des disques", "GPT ; ESP, Windows, Récupération sur le disque cible"),
    ("Pilotes", "Gestionnaire de périphériques", "Aucun périphérique inconnu ni triangle"),
    ("Mises à jour", "Windows Update", "« Vous êtes à jour »"),
    ("Sécurité", "Sécurité Windows", "Antivirus et pare-feu actifs ; chiffrement, clé remise"),
    ("Réseau", "ipconfig /all ; navigateur", "Adresse obtenue, Internet accessible"),
    ("Comptes", "Paramètres → Comptes", "Administrateur protégé ; compte standard au quotidien"),
    ("Données et logiciels", "Avec le client", "Fichiers restaurés vérifiés ; logiciels et imprimante testés"),
)

REPORT_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Demande", "Client, date, besoin exprimé, accord écrit (date, effacement autorisé)."),
    ("Poste", "Marque, modèle, numéro de série ; état initial constaté."),
    ("Sauvegarde", "Support utilisé, contenu, vérification de la copie."),
    ("Actions", "Version et édition installées, disque et partitions, pilotes, réglages du firmware."),
    ("Contrôles", "Liste de contrôle et résultats (activation, pilotes, mises à jour, réseau)."),
    ("Remise", "Données restaurées et vérifiées avec le client ; clé de récupération remise."),
    ("Recommandations", "Sauvegarde régulière, mises à jour, matériel à surveiller ; signatures."),
)

# =============================================================================================
# 8. Captures fictives
# =============================================================================================

# Écran de choix de l'emplacement (cas 5 et exercice E05) : deux disques.
INSTALLER_DISKS_SCREEN: tuple[str, ...] = (
    "Où souhaitez-vous installer Windows ?",
    "",
    "Nom                           Taille    Libre  Type",
    "Lecteur 0 Partition 1         100 Mo    70 Mo  Système",
    "Lecteur 0 Partition 2          16 Mo    16 Mo  MSR",
    "Lecteur 0 Partition 3: Windows 237 Go  180 Go  Princip.",
    "Lecteur 0 Partition 4         600 Mo    90 Mo  Récup.",
    "Lecteur 1 Partition 1: DONNEES 931 Go  410 Go  Princip.",
    "",
    "[Supprimer] [Formater] [Nouveau] [Charger un pilote]",
)

NO_DRIVE_SCREEN: tuple[str, ...] = (
    "Où souhaitez-vous installer Windows ?",
    "",
    "Nous n'avons trouvé aucun lecteur. Pour obtenir un",
    "pilote de stockage, cliquez sur Charger un pilote.",
    "",
    "[Actualiser]                    [Charger un pilote]",
    "",
    "Firmware (onglet Stockage) : SSD NVMe 512 Go détecté",
    "Contrôleur : Intel VMD — Activé",
)

MBR_ERROR_SCREEN: tuple[str, ...] = (
    "Impossible d'installer Windows sur ce disque. Le",
    "disque sélectionné possède une table de partition",
    "MBR. Sur les systèmes EFI, Windows ne peut être",
    "installé que sur des disques GPT.",
    "",
    "X:\\Sources> diskpart",
    "DISKPART> list disk",
    "  N° disque  Statut    Taille   Libre    GPT",
    "  Disque 0   En ligne   476 Go   0 octet",
    "  Disque 1   En ligne    14 Go   0 octet   *",
)

DEVMGR_SCREEN: tuple[str, ...] = (
    "Gestionnaire de périphériques",
    "v Autres périphériques",
    "    (!) Contrôleur Ethernet",
    "    (!) Contrôleur de réseau",
    "    (!) Périphérique PCI",
    "v Cartes graphiques",
    "    Carte graphique de base Microsoft",
    "",
    "Contrôleur Ethernet → Détails → ID du matériel :",
    "  PCI\\VEN_10EC&DEV_8168",
    "Contrôleur de réseau → ID du matériel :",
    "  PCI\\VEN_8086&DEV_2725",
)

INSTALLER_DISKS_FIGURE = Figure(
    key="pr08-choix-disque",
    title="Choix de l'emplacement d'installation sur un PC à deux disques (fictif)",
    alt="Capture texte de l'installateur. " + " ; ".join(line.strip() for line in INSTALLER_DISKS_SCREEN if line.strip()) + ".",
    caption=(
        "Le lecteur 0 (SSD de 238 Go) porte l'ancien Windows ; le lecteur 1 (disque de 1 To) porte "
        "les données. On identifie le disque cible par sa taille. Capture fictive."
    ),
    svg=screen_svg(INSTALLER_DISKS_SCREEN, label=FICTIVE_LABEL),
)

NO_DRIVE_FIGURE_SCREEN = Figure(
    key="pr08-aucun-lecteur",
    title="Cas 2 — « Aucun lecteur » alors que le firmware voit le SSD (fictif)",
    alt="Capture texte. " + " ; ".join(line.strip() for line in NO_DRIVE_SCREEN if line.strip()) + ".",
    caption=(
        "Le firmware détecte le SSD mais le contrôleur Intel VMD est activé : l'installateur n'a "
        "pas le pilote de ce contrôleur. Capture fictive."
    ),
    svg=screen_svg(NO_DRIVE_SCREEN, label=FICTIVE_LABEL),
)

MBR_ERROR_FIGURE = Figure(
    key="pr08-disque-mbr",
    title="Cas 5 — Disque MBR refusé en mode UEFI, vérification avec diskpart (fictif)",
    alt="Capture texte. " + " ; ".join(line.strip() for line in MBR_ERROR_SCREEN if line.strip()) + ".",
    caption=(
        "Pas d'astérisque dans la colonne GPT pour le disque 0 : il est en MBR. Le disque 1 est la "
        "clé d'installation. Capture fictive (invite ouverte avec Maj+F10)."
    ),
    svg=screen_svg(MBR_ERROR_SCREEN, label=FICTIVE_LABEL),
)

DEVMGR_FIGURE = Figure(
    key="pr08-gestionnaire-peripheriques",
    title="Cas 4 — Gestionnaire de périphériques après l'installation (fictif)",
    alt="Capture texte. " + " ; ".join(line.strip() for line in DEVMGR_SCREEN if line.strip()) + ".",
    caption=(
        "Le point d'exclamation (!) signale un périphérique sans pilote ; l'identifiant VEN donne "
        "le fabricant (10EC : Realtek, 8086 : Intel). Capture fictive."
    ),
    svg=screen_svg(DEVMGR_SCREEN, label=FICTIVE_LABEL),
)

PR08_FIGURES: tuple[Figure, ...] = (
    PREP_FIGURE,
    SETUP_FIGURE,
    LAYOUT_FIGURE,
    NO_DRIVE_FIGURE,
    FINAL_FIGURE,
    INSTALLER_DISKS_FIGURE,
    NO_DRIVE_FIGURE_SCREEN,
    MBR_ERROR_FIGURE,
    DEVMGR_FIGURE,
)

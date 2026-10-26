"""Schémas et captures fictives du cours PR11 « Messages d'erreur Windows/Linux » (ticket #194).

Chaque figure est construite depuis les données de ce module (tuples), contrôlées par
`tests/test_ticket194_ampcr_pratique_pr11.py`. Les messages, codes et commandes repris dans
les captures sont ceux des systèmes réels (sources citées dans le bloc « Sources » du cours) ;
les noms de machines, de fichiers de pilote, les dates et les identifiants (UUID) sont
**fictifs**. Les captures sont des reconstitutions texte, **jamais** des copies d'écran
réelles ni des images générées : chacune porte la mention « Capture fictive ».
"""

from app.v1.ampcr_pratique_visuals import (
    Figure,
    PartitionSegment,
    decision_tree_svg,
    partition_map_svg,
    screen_svg,
    step_flow_svg,
)

# Largeur utile d'une ligne de capture (police à chasse fixe, 380 px de large) : au-delà, la
# ligne déborderait de l'écran dessiné. Vérifié par les tests.
SCREEN_MAX_CHARS = 56

# --- Stades d'apparition d'une erreur -----------------------------------------------------

# Les dix stades de la matière (section 1 du ticket), dans l'ordre du démarrage puis de
# l'utilisation.
STAGES: tuple[str, ...] = (
    "Firmware / POST",
    "Chargeur d'amorçage",
    "Noyau / système",
    "Ouverture de session",
    "Service",
    "Application",
    "Pilote",
    "Périphérique",
    "Stockage",
    "Réseau",
)

# (question fermée, piste si la réponse est « non »), dans l'ordre du démarrage.
STAGE_TREE: tuple[tuple[str, str], ...] = (
    (
        "Le logo ou l'écran du firmware (BIOS/UEFI) s'affiche-t-il ?",
        "Stade firmware / POST : matériel, bips, LED (manuel du fabricant), voir PR06.",
    ),
    (
        "Le chargeur démarre-t-il sans message ? (Windows Boot Manager, GRUB)",
        "Stade chargeur : disque détecté, ordre et mode UEFI/Legacy, partition EFI, BCD ou GRUB.",
    ),
    (
        "Le système démarre-t-il sans écran bleu, emergency mode ni (initramfs) ?",
        "Stade noyau / système : pilote de démarrage, stockage, /etc/fstab, UUID, dernière mise à jour.",
    ),
    (
        "L'ouverture de session aboutit-elle normalement ?",
        "Stade session : mot de passe, compte, profil (profil temporaire), droits.",
    ),
    (
        "Les services nécessaires sont-ils actifs ?",
        "Stade service : services.msc ou systemctl status, dépendances, journaux du service.",
    ),
    (
        "L'application démarre-t-elle et fonctionne-t-elle ?",
        "Stade application : message exact, journal Application, droits, espace disque, version.",
    ),
    (
        "Le matériel concerné est-il reconnu sans erreur ?",
        "Stade pilote / périphérique : Gestionnaire de périphériques (code), dmesg, câble, autre port.",
    ),
    (
        "Les données se lisent-elles et s'écrivent-elles sans erreur ?",
        "Stade stockage : espace et inodes, lecture seule, erreurs de disque ; données d'abord.",
    ),
    (
        "Le réseau répond-il (adresse, passerelle, DNS) ?",
        "Stade réseau : ipconfig / ip addr, ping de la passerelle, puis d'une IP publique, puis d'un nom.",
    ),
)
STAGE_TREE_FINAL = (
    "Toutes les réponses sont « oui » : relire le symptôme exact et la chronologie ; "
    "l'erreur est peut-être intermittente (journaux, conditions de reproduction)."
)

STAGE_TREE_FIGURE = Figure(
    key="pr11-arbre-stade-erreur",
    title="Arbre de décision « À quelle étape l'erreur survient-elle ? »",
    alt=(
        "Neuf questions en colonne, du démarrage à l'utilisation, chacune avec une piste si la "
        "réponse est non : "
        + " ; ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(STAGE_TREE, start=1))
        + f" Si toutes les réponses sont oui : {STAGE_TREE_FINAL}"
    ),
    caption=(
        "Arbre de décision : on descend tant que la réponse est « oui » ; le premier « non » "
        "indique le stade de l'erreur et les vérifications à faire (piste de droite). Lecture "
        "de haut en bas."
    ),
    svg=decision_tree_svg(STAGE_TREE, STAGE_TREE_FINAL),
)

# --- Flux « lire → hypothèse → test → action → validation » --------------------------------

ERROR_FLOW: tuple[tuple[str, str], ...] = (
    ("Lire", "Recopier le message exact, le code, l'heure, le contexte et ce qui a changé."),
    ("Hypothèse", "Proposer des causes possibles, sans conclure à partir du seul code."),
    ("Test", "Vérifier chaque hypothèse par un test non destructif, du plus simple au plus lourd."),
    ("Action", "Corriger la cause retenue, de façon réversible d'abord, avec accord si risque."),
    ("Validation", "Reproduire le scénario : l'erreur a disparu ; noter le résultat au compte rendu."),
)

ERROR_FLOW_FIGURE = Figure(
    key="pr11-flux-lire-tester-valider",
    title="Flux d'intervention sur un message d'erreur",
    alt=(
        "Cinq étapes reliées par des flèches, de haut en bas : "
        + " ; ".join(f"{i}. {name} — {detail}" for i, (name, detail) in enumerate(ERROR_FLOW, start=1))
    ),
    caption=(
        "Lire, faire une hypothèse, tester, agir, valider : si le test infirme l'hypothèse, on "
        "revient à l'étape 2 avec l'information obtenue. Lecture de haut en bas."
    ),
    svg=step_flow_svg(ERROR_FLOW, width=340),
)

# --- Captures fictives -----------------------------------------------------------------------

BCD_SCREEN: tuple[str, ...] = (
    "Récupération",
    "",
    "Votre PC/appareil doit être réparé",
    "",
    "Les données de configuration de démarrage de",
    "votre PC sont manquantes ou contiennent des erreurs.",
    "",
    "Fichier : \\EFI\\Microsoft\\Boot\\BCD",
    "Code d'erreur : 0xc000000f",
    "",
    "Vous devez utiliser des outils de récupération.",
    "",
    "Appuyez sur Entrée pour réessayer",
    "Appuyez sur F8 pour les paramètres de démarrage",
    "Appuyez sur Échap pour les paramètres UEFI",
)

BCD_SCREEN_FIGURE = Figure(
    key="pr11-ecran-windows-boot-manager",
    title="Windows Boot Manager : données de configuration de démarrage (capture fictive)",
    alt="Écran texte de récupération Windows : " + " / ".join(line for line in BCD_SCREEN if line) + ".",
    caption=(
        "Capture fictive reconstituée pour le cas 1. Le texte et le code 0xc000000f sont ceux "
        "qu'affiche le gestionnaire de démarrage Windows quand le magasin BCD est introuvable "
        "ou illisible ; la mise en page varie selon la version."
    ),
    svg=screen_svg(BCD_SCREEN, label="Capture fictive — Windows Boot Manager"),
)

# Menu « Options avancées » de l'environnement de récupération (WinRE). (libellé, rôle)
WINRE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("Outil de redémarrage système", "réparation automatique du démarrage"),
    ("Paramètres", "mode sans échec, désactiver le redémarrage auto"),
    ("Invite de commandes", "commandes de lecture et de réparation"),
    ("Désinstaller des mises à jour", "retirer la dernière mise à jour"),
    ("Paramètres du microprogramme UEFI", "ouvrir le firmware"),
    ("Restauration du système", "revenir à un point de restauration"),
)
WINRE_SCREEN: tuple[str, ...] = (
    "Options avancées",
    "",
    *(line for label, role in WINRE_OPTIONS for line in (f"> {label}", f"    {role}")),
)

WINRE_SCREEN_FIGURE = Figure(
    key="pr11-ecran-winre",
    title="Environnement de récupération Windows : options avancées (capture fictive)",
    alt=(
        "Menu Options avancées de WinRE : "
        + " ; ".join(f"{label} ({role})" for label, role in WINRE_OPTIONS)
        + "."
    ),
    caption=(
        "Capture fictive : WinRE (Dépannage > Options avancées). Les libellés changent un peu "
        "d'une version de Windows à l'autre (ex. « Outil de redémarrage système » ou "
        "« Réparation du démarrage ») ; leur rôle reste le même."
    ),
    svg=screen_svg(WINRE_SCREEN, label="Capture fictive — WinRE"),
)

BSOD_SCREEN: tuple[str, ...] = (
    ":(",
    "",
    "Votre PC a rencontré un problème et doit",
    "redémarrer. Nous collectons simplement des",
    "informations relatives aux erreurs, puis nous",
    "allons redémarrer à votre place.",
    "",
    "100 % effectué",
    "",
    "Code d'arrêt : DRIVER_IRQL_NOT_LESS_OR_EQUAL",
    "Ce qui a échoué : wlanxv64.sys",
)

BSOD_SCREEN_FIGURE = Figure(
    key="pr11-ecran-bleu",
    title="Écran bleu Windows avec code d'arrêt (capture fictive)",
    alt="Écran bleu Windows : " + " / ".join(line for line in BSOD_SCREEN if line) + ".",
    caption=(
        "Capture fictive pour le cas 2 : le code d'arrêt (ici DRIVER_IRQL_NOT_LESS_OR_EQUAL, "
        "0xD1) et le fichier cité sont les deux informations à recopier. Le nom de pilote "
        "« wlanxv64.sys » est inventé."
    ),
    svg=screen_svg(BSOD_SCREEN, label="Capture fictive — écran bleu (texte réel, nom de pilote inventé)"),
)

# Observateur d'événements, journal Système, du plus récent au plus ancien :
# (niveau, date et heure, source, ID, résumé du message).
EVENT_LOG: tuple[tuple[str, str, str, int, str], ...] = (
    ("Erreur", "12/03 08:14:05", "BugCheck", 1001, "redémarré après une vérification d'erreur 0x000000d1"),
    ("Erreur", "12/03 08:13:58", "EventLog", 6008, "l'arrêt système précédent était inattendu"),
    ("Critique", "12/03 08:13:52", "Kernel-Power", 41, "redémarré sans arrêt correct préalable"),
    ("Information", "11/03 17:42:10", "UserPnp", 20003, "service du pilote wlanxv64 ajouté"),
)
EVENT_SCREEN: tuple[str, ...] = (
    "Observateur d'événements > Journaux Windows > Système",
    "Niveau      Date et heure   Source        ID",
    *(f"{level:<11} {when:<15} {source:<13} {event_id}" for level, when, source, event_id, _m in EVENT_LOG),
    "",
    "Événement 1001, BugCheck (sélectionné) :",
    "L'ordinateur a redémarré après une vérification",
    "d'erreur. La vérification d'erreur était :",
    "0x000000d1 (...). Un vidage a été enregistré",
    "dans : C:\\Windows\\Minidump\\031226-7031-01.dmp.",
)

EVENT_SCREEN_FIGURE = Figure(
    key="pr11-observateur-evenements",
    title="Observateur d'événements, journal Système (capture fictive)",
    alt=(
        "Liste d'événements du journal Système, du plus récent au plus ancien : "
        + " ; ".join(f"{lvl} le {when}, source {src}, ID {eid} : {msg}" for lvl, when, src, eid, msg in EVENT_LOG)
        + ". Détail de l'événement 1001 : redémarrage après vérification d'erreur 0x000000d1, vidage enregistré dans le dossier Minidump."
    ),
    caption=(
        "Capture fictive pour le cas 2 : niveau, date et heure, source et ID permettent de "
        "reconstituer la chronologie. Kernel-Power 41 et EventLog 6008 disent seulement que "
        "l'arrêt n'était pas propre ; BugCheck 1001 donne le code d'arrêt."
    ),
    svg=screen_svg(EVENT_SCREEN, label="Capture fictive — Observateur d'événements"),
)

DEVICE_SCREEN: tuple[str, ...] = (
    "Gestionnaire de périphériques",
    "v Contrôleurs de bus USB",
    "    Concentrateur USB racine (USB 3.0)",
    "    (!) Périphérique USB inconnu (échec de la",
    "        demande de descripteur de périphérique)",
    "v Autres périphériques",
    "    (!) Contrôleur de communication simple PCI",
    "v Caméras",
    "    (v) Webcam intégrée",
    "",
    "Propriétés > État du périphérique :",
    "Windows a arrêté ce périphérique car il a",
    "signalé des problèmes. (Code 43)",
    "",
    "(!) triangle jaune = problème  (v) flèche = désactivé",
)

DEVICE_SCREEN_FIGURE = Figure(
    key="pr11-gestionnaire-peripheriques",
    title="Gestionnaire de périphériques (capture fictive)",
    alt="Gestionnaire de périphériques : " + " / ".join(line.strip() for line in DEVICE_SCREEN if line.strip()) + ".",
    caption=(
        "Capture fictive pour le cas 3 : le symbole (triangle jaune, flèche vers le bas) "
        "indique l'état, le code de l'onglet « État du périphérique » précise le problème. "
        "Ici, symboles écrits en toutes lettres pour une lecture sans couleur."
    ),
    svg=screen_svg(DEVICE_SCREEN, label="Capture fictive — Gestionnaire de périphériques"),
)

SYSTEMCTL_SCREEN: tuple[str, ...] = (
    "$ systemctl status ssh",
    "× ssh.service - OpenBSD Secure Shell server",
    "  Loaded: loaded (/lib/systemd/system/ssh.service;",
    "          enabled; preset: enabled)",
    "  Active: failed (Result: exit-code) since",
    "          Tue 2026-03-10 09:02:11 CET; 2min ago",
    "  Process: 812 ExecStartPre=/usr/sbin/sshd -t",
    "           (code=exited, status=255/EXCEPTION)",
    "",
    "$ journalctl -u ssh -b --no-pager | tail -4",
    "sshd[812]: /etc/ssh/sshd_config: line 14: Bad",
    "  configuration option: PermitRootLogn",
    "sshd[812]: /etc/ssh/sshd_config: terminating,",
    "  1 bad configuration options",
    "systemd[1]: ssh.service: Control process exited,",
    "  code=exited, status=255/EXCEPTION",
    "systemd[1]: Failed to start ssh.service - OpenBSD",
    "  Secure Shell server.",
)

SYSTEMCTL_SCREEN_FIGURE = Figure(
    key="pr11-terminal-systemctl-journalctl",
    title="Terminal Linux : systemctl status et journalctl (capture fictive)",
    alt="Terminal Linux : " + " / ".join(line.strip() for line in SYSTEMCTL_SCREEN if line.strip()) + ".",
    caption=(
        "Capture fictive pour le cas 4 (Debian/Ubuntu ; lignes longues repliées) : systemctl "
        "dit que le service est en échec, le journal du service dit pourquoi (option mal "
        "orthographiée ligne 14). Messages au format réel d'OpenSSH et de systemd."
    ),
    svg=screen_svg(SYSTEMCTL_SCREEN, label="Capture fictive — terminal Linux"),
)

# df -h puis df -i sur le serveur du cas 5 : (système de fichiers, taille, utilisé, dispo,
# utilisation %, monté sur). Valeurs cohérentes : utilisé + dispo ≈ taille (réserve ext4 de
# 5 % pour root : un volume plein affiche 100 % avec 0 disponible).
DF_H: tuple[tuple[str, str, str, str, int, str], ...] = (
    ("/dev/sda2", "48G", "46G", "0", 100, "/"),
    ("/dev/sda1", "511M", "6.1M", "505M", 2, "/boot/efi"),
)
DISK_FULL_SCREEN: tuple[str, ...] = (
    "$ cp rapport.pdf /srv/partage/",
    "cp: error writing '/srv/partage/rapport.pdf':",
    "  No space left on device",
    "$ df -h / /boot/efi",
    "Filesystem      Size  Used Avail Use% Mounted on",
    *(f"{fs:<15} {size:>4} {used:>5} {free:>5} {pct:>3}% {mount}" for fs, size, used, free, pct, mount in DF_H),
    "$ sudo du -xh -d1 /var | sort -h | tail -3",
    "1.2G    /var/cache",
    "31G     /var/log",
    "33G     /var",
    "$ sudo du -xh -d1 /var/log | sort -h | tail -2",
    "30G     /var/log/sauvegarde-agent",
    "31G     /var/log",
)

DISK_FULL_SCREEN_FIGURE = Figure(
    key="pr11-terminal-disque-plein",
    title="Terminal Linux : « No space left on device » et df -h (capture fictive)",
    alt="Terminal Linux : " + " / ".join(line.strip() for line in DISK_FULL_SCREEN if line.strip()) + ".",
    caption=(
        "Capture fictive pour le cas 5 : df -h montre la partition pleine, du -xh remonte "
        "jusqu'au dossier qui grossit (journal d'un agent de sauvegarde). Aucune suppression "
        "n'est faite à ce stade : on observe."
    ),
    svg=screen_svg(DISK_FULL_SCREEN, label="Capture fictive — terminal Linux"),
)

# --- Partitionnement --------------------------------------------------------------------------

# Disque système Windows démarrant en UEFI (GPT), disposition par défaut de l'installation
# de Windows 10/11 ; tailles d'un exemple fictif (la partition de récupération varie).
WINDOWS_GPT: tuple[PartitionSegment, ...] = (
    PartitionSegment("esp", ("EFI (ESP)", "FAT32", "100 Mo"), 78),
    PartitionSegment("msr", ("MSR", "réservée", "16 Mo"), 62),
    PartitionSegment("c", ("C: Windows", "NTFS", "475 Go"), 156),
    PartitionSegment("winre", ("Récupér.", "NTFS", "750 Mo"), 76),
)
# Disque Linux démarrant en UEFI (GPT), exemple fictif d'une installation Ubuntu/Debian.
LINUX_GPT: tuple[PartitionSegment, ...] = (
    PartitionSegment("esp", ("EFI (ESP)", "FAT32", "/boot/efi"), 90),
    PartitionSegment("root", ("/ (racine)", "ext4", "48 Go"), 190),
    PartitionSegment("swap", ("swap", "échange", "4 Go"), 92),
)

PARTITION_FIGURE = Figure(
    key="pr11-partitionnement-gpt",
    title="Partitionnement GPT d'un disque Windows et d'un disque Linux (exemple fictif)",
    alt=(
        "Deux barres, du début à la fin du disque. Disque Windows UEFI/GPT : "
        + ", ".join(" ".join(s.lines) for s in WINDOWS_GPT)
        + ". Disque Linux UEFI/GPT : "
        + ", ".join(" ".join(s.lines) for s in LINUX_GPT)
        + ". Largeurs non proportionnelles aux tailles."
    ),
    caption=(
        "Exemple fictif (tailles indicatives, cases non proportionnelles). En UEFI, le "
        "chargeur est un fichier de la partition EFI (ESP, FAT32) : la supprimer ou la "
        "formater empêche le démarrage même si C: ou / sont intacts."
    ),
    svg=partition_map_svg(
        (
            ("Disque 0 — Windows, UEFI, table GPT", WINDOWS_GPT),
            ("Disque 1 — Linux, UEFI, table GPT", LINUX_GPT),
        )
    ),
)

# lsblk et /etc/fstab du cas d'exercice E04 : l'UUID de /data dans fstab ne correspond à
# aucun disque présent (disque remplacé). UUID fictifs.
LSBLK_SCREEN: tuple[str, ...] = (
    "$ lsblk -o NAME,FSTYPE,UUID,MOUNTPOINTS",
    "NAME   FSTYPE UUID            MOUNTPOINTS",
    "sda",
    "├─sda1 vfat   4C1E-2A7B       /boot/efi",
    "└─sda2 ext4   9b2f…6c1d       /",
    "sdb",
    "└─sdb1 ext4   e41a…0b93",
    "$ grep data /etc/fstab",
    "UUID=7d3c…51fe  /data  ext4  defaults  0  2",
)

LSBLK_SCREEN_FIGURE = Figure(
    key="pr11-terminal-lsblk-fstab",
    title="Terminal Linux : lsblk et ligne /etc/fstab (capture fictive)",
    alt="Terminal Linux : " + " / ".join(line.strip() for line in LSBLK_SCREEN if line.strip()) + ".",
    caption=(
        "Capture fictive (UUID raccourcis) : la ligne de /etc/fstab cherche un UUID qu'aucun "
        "système de fichiers listé par lsblk ne porte : le montage de /data échoue au "
        "démarrage."
    ),
    svg=screen_svg(LSBLK_SCREEN, label="Capture fictive — terminal Linux"),
)

SCREENS: dict[str, tuple[str, ...]] = {
    "bcd": BCD_SCREEN,
    "winre": WINRE_SCREEN,
    "bsod": BSOD_SCREEN,
    "events": EVENT_SCREEN,
    "devices": DEVICE_SCREEN,
    "systemctl": SYSTEMCTL_SCREEN,
    "disk-full": DISK_FULL_SCREEN,
    "lsblk": LSBLK_SCREEN,
}

PR11_FIGURES: tuple[Figure, ...] = (
    STAGE_TREE_FIGURE,
    ERROR_FLOW_FIGURE,
    BCD_SCREEN_FIGURE,
    WINRE_SCREEN_FIGURE,
    BSOD_SCREEN_FIGURE,
    EVENT_SCREEN_FIGURE,
    DEVICE_SCREEN_FIGURE,
    SYSTEMCTL_SCREEN_FIGURE,
    DISK_FULL_SCREEN_FIGURE,
    PARTITION_FIGURE,
    LSBLK_SCREEN_FIGURE,
)

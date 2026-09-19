"""Lexique AMPCR — acronymes, abréviations et vocabulaire FR/EN (ticket #84).

Ressource pédagogique transverse, accessible depuis Informatique → AMPCR → Lexique /
Acronymes FR-EN. Chaque entrée reprend le contenu déjà enseigné dans les mini-cours
(`app.v1.ampcr_courses.AMPCR_COURSE_MARKDOWN`) — jamais une définition inventée (règle du
projet : « Claude ne redéfinit jamais le contenu pédagogique »). Les définitions,
contextes et pièges ci-dessous sont des reformulations FIDÈLES et COURTES du texte de
cours déjà validé, citant systématiquement le(s) MC d'origine.

§ 84.C : n'inclut QUE les acronymes réellement présents dans le programme AMPCR (vérifié
par recherche exhaustive dans `AMPCR_COURSE_MARKDOWN` + les objectifs `_OBJECTIVES_BY_CODE`
— voir le rapport `docs/claude-reports/2026-09-19_ticket-84_lexique-ampcr.md`). Six
acronymes de la liste minimale du ticket (ROM, WLAN, IPv6, FTP, CLI, GUI) n'apparaissent
nulle part dans le programme actuel et sont donc volontairement ABSENTS — les ajouter
« parce qu'ils sont connus en informatique » violerait explicitement la règle § 84.C.

§ 84.F : ce lexique est une ressource pédagogique AUTORISÉE au même titre qu'un cours de
MC — `app.v1.course_coverage.defined_notions_for_code` l'inclut systématiquement, donc
une question qui demande le développé d'un acronyme listé ici n'est jamais rejetée par la
garde § 83.B, même si le MC concerné ne l'explique pas lui-même en détail.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LexiconEntry:
    acronym: str
    english: str | None
    french_term: str | None
    definition: str
    context: str
    confusion: str | None
    mc_codes: tuple[str, ...]


@dataclass(frozen=True)
class LexiconTheme:
    key: str
    title: str
    entries: tuple[LexiconEntry, ...]


LEXICON_THEMES: tuple[LexiconTheme, ...] = (
    LexiconTheme(
        key="architecture",
        title="1. Architecture PC",
        entries=(
            LexiconEntry(
                "CPU", "Central Processing Unit", "Processeur",
                "Composant qui exécute les instructions et traite les données.",
                "Cœur du traitement, avec la RAM et le stockage (MC01) ; alimenté par le connecteur EPS (MC05).",
                None, ("MC01", "MC03", "MC05", "MC06"),
            ),
            LexiconEntry(
                "GPU", "Graphics Processing Unit", "Carte/processeur graphique",
                "Composant dédié au calcul et à l'affichage de l'image.",
                "Alimenté par des connecteurs PCIe 6/8 broches (MC05) ; suspect en priorité en cas d'absence d'image (MC29).",
                None, ("MC01", "MC05", "MC29"),
            ),
            LexiconEntry(
                "RAM", "Random Access Memory", "Mémoire vive",
                "Mémoire volatile qui stocke temporairement les données en cours de traitement.",
                "Effacée à l'extinction, contrairement au stockage (MC04) ; cause fréquente d'absence d'image si mal insérée (MC29).",
                None, ("MC01", "MC03", "MC04", "MC06", "MC29"),
            ),
            LexiconEntry(
                "PSU", "Power Supply Unit", "Bloc d'alimentation",
                "Convertit le courant secteur en plusieurs tensions continues (+12V, +5V, +3.3V) pour les composants.",
                "Caractérisé par sa puissance nominale (watts) et son rendement (certification 80 PLUS) — MC05.",
                None, ("MC05",),
            ),
            LexiconEntry(
                "PCIe", "PCI Express", None,
                "Bus utilisé par les cartes graphiques et les SSD NVMe pour un très haut débit.",
                "Connecteur d'alimentation carte graphique (6/8 broches, MC05) ; bus des SSD NVMe (MC04).",
                None, ("MC04", "MC05"),
            ),
            LexiconEntry(
                "USB", "Universal Serial Bus", None,
                "Interface standard pour connecter des périphériques et des supports amovibles.",
                "Clé USB bootable pour installer un OS (MC07/MC09) ; lecteurs USB souvent formatés en FAT32 (MC08).",
                None, ("MC07", "MC08", "MC09"),
            ),
        ),
    ),
    LexiconTheme(
        key="stockage",
        title="2. Stockage",
        entries=(
            LexiconEntry(
                "HDD", "Hard Disk Drive", "Disque dur",
                "Disque de stockage mécanique : plateaux magnétiques en rotation + tête de lecture/écriture mobile.",
                "Reste pertinent pour le stockage de masse à faible coût (archives, gros volumes) — MC04.",
                "HDD = mécanique ; SSD = flash NAND, sans pièce mobile (MC04).", ("MC04",),
            ),
            LexiconEntry(
                "SSD", "Solid State Drive", "Disque à mémoire flash",
                "Disque de stockage en mémoire flash NAND, sans pièce mobile.",
                "Plus rapide, plus silencieux, plus résistant aux chocs qu'un HDD (MC04).",
                "Ne jamais défragmenter un SSD (inutile, use la mémoire flash pour rien) — MC04.", ("MC04",),
            ),
            LexiconEntry(
                "SATA", None, None,
                "Interface/bus de stockage historique (disques et SSD 2,5\"), débit plafonné à environ 600 Mo/s.",
                "Un SSD au format M.2 peut être SATA ou NVMe selon le slot et le SSD — MC04.",
                "M.2 = connecteur (format physique) ; SATA/NVMe = protocoles possibles sur ce connecteur.", ("MC04",),
            ),
            LexiconEntry(
                "NVMe", "Non-Volatile Memory Express", None,
                "Protocole conçu pour le stockage sur bus PCIe, très haut débit et faible latence.",
                "Généralement utilisé en M.2 aujourd'hui ; performances dépendantes du SSD, du nombre de lignes PCIe et de la température — MC04.",
                "Confondre M.2 (format de connecteur) et NVMe (protocole) : un SSD M.2 SATA existe bel et bien.", ("MC04",),
            ),
            LexiconEntry(
                "M.2", None, None,
                "Format de connecteur pour SSD — pas un protocole en soi.",
                "Un SSD M.2 peut être SATA ou NVMe selon le slot et le SSD — MC04.",
                "Confondre M.2 (format) et NVMe (protocole).", ("MC04",),
            ),
            LexiconEntry(
                "SMART", "Self-Monitoring, Analysis and Reporting Technology",
                "Surveillance de l'état du disque",
                "Technologie de surveillance de l'état du stockage : température, secteurs/erreurs, heures de fonctionnement.",
                "Utile pour le diagnostic (MC04, MC30, MC32) — ne garantit pas de prédire toutes les pannes et ne remplace jamais une sauvegarde.",
                "Un SMART « vert » ne garantit pas l'absence de panne future.", ("MC04", "MC30", "MC32"),
            ),
            LexiconEntry(
                "TBW", "Terabytes Written", None,
                "Endurance garantie par le fabricant pour un SSD.",
                "Indicateur d'endurance de la mémoire flash NAND — MC04.",
                None, ("MC04",),
            ),
        ),
    ),
    LexiconTheme(
        key="bios-uefi",
        title="3. BIOS / UEFI",
        entries=(
            LexiconEntry(
                "BIOS", "Basic Input/Output System", None,
                "Ancien firmware de démarrage, interface simple, limité en fonctionnalités.",
                "Associé au partitionnement MBR — MC07/MC08.",
                "BIOS = ancien, MBR ; UEFI = moderne, GPT, plus rapide, Secure Boot (MC07).", ("MC07", "MC08"),
            ),
            LexiconEntry(
                "UEFI", "Unified Extensible Firmware Interface", None,
                "Firmware moderne qui remplace le BIOS, supporte les grands disques (GPT) et accélère le démarrage.",
                "Associé au partitionnement GPT — MC07/MC08.",
                "BIOS = ancien, MBR ; UEFI = moderne, GPT, plus rapide, Secure Boot (MC07).", ("MC07", "MC08"),
            ),
        ),
    ),
    LexiconTheme(
        key="systemes",
        title="4. Systèmes",
        entries=(
            LexiconEntry(
                "NTFS", None, None,
                "Système de fichiers natif de Windows, permissions avancées, pas de limite de taille de fichier pratique.",
                "Droits NTFS combinés aux droits de partage (le plus restrictif s'applique) — MC08/MC33.",
                None, ("MC08", "MC33"),
            ),
            LexiconEntry(
                "FAT32", None, None,
                "Système de fichiers très compatible (lecteurs USB, consoles...), mais limité à des fichiers de 4 Go maximum.",
                "Copier un fichier de 5 Go sur une clé USB en FAT32 échoue (limite 4 Go) — MC08.",
                "FAT32 limité à 4 Go par fichier ; exFAT et NTFS n'ont pas cette limite.", ("MC08",),
            ),
            LexiconEntry(
                "exFAT", None, None,
                "Successeur de FAT32 pour les supports amovibles, sans la limite de 4 Go.",
                "Adapté à un support partagé multi-OS — MC08.",
                None, ("MC08",),
            ),
        ),
    ),
    LexiconTheme(
        key="reseaux",
        title="5. Réseaux / TCP-IP / OSI",
        entries=(
            LexiconEntry(
                "LAN", "Local Area Network", "Réseau local",
                "Réseau local, à l'échelle d'un bâtiment/site.",
                "MC13.",
                "Confondre LAN et WAN pour une même infrastructure (un même bâtiment peut avoir un LAN connecté à un WAN via un routeur Internet).", ("MC13",),
            ),
            LexiconEntry(
                "WAN", "Wide Area Network", "Réseau étendu",
                "Réseau étendu reliant plusieurs sites — Internet en est l'exemple le plus courant.",
                "MC13.",
                "Confondre LAN et WAN pour une même infrastructure.", ("MC13",),
            ),
            LexiconEntry(
                "IP", "Internet Protocol", "Adresse IP",
                "Identifiant réseau d'un appareil au niveau de la couche Réseau.",
                "Base de l'adressage réseau — MC13/MC16/MC20/MC31.",
                "Confondre adresse IP et adresse MAC (MC16, voir MC20).", ("MC13", "MC16", "MC20", "MC31"),
            ),
            LexiconEntry(
                "IPv4", None, None,
                "Adresse réseau sur 32 bits, notée en 4 blocs décimaux séparés par des points.",
                "Se divise conceptuellement en une partie « réseau » et une partie « hôte », déterminée par le masque — MC16.",
                None, ("MC16", "MC17", "MC18"),
            ),
            LexiconEntry(
                "MAC", "Media Access Control", "Adresse MAC",
                "Adresse physique d'un appareil, utilisée au niveau de la couche Liaison.",
                "Apprise dynamiquement par la table MAC d'un switch (MC23) ; ARP traduit une adresse IP en adresse MAC (MC20).",
                "Confondre adresse IP et adresse MAC.", ("MC14", "MC20", "MC23", "MC25"),
            ),
            LexiconEntry(
                "DHCP", "Dynamic Host Configuration Protocol", None,
                "Protocole d'attribution automatique d'une adresse IP et des paramètres réseau associés.",
                "Séquence DORA (Discover, Offer, Request, Acknowledge) — MC19 ; sans réponse DHCP, un PC Windows s'auto-attribue une adresse APIPA.",
                "Ne jamais laisser deux serveurs DHCP actifs simultanément sur le même réseau par erreur.", ("MC19",),
            ),
            LexiconEntry(
                "DNS", "Domain Name System", None,
                "Traduit un nom de domaine (ex. exemple.com) en adresse IP.",
                "Le cache DNS peut contenir une entrée périmée à vider — MC20/MC31.",
                "DNS = nom → IP ; ARP = IP → MAC (réseau local uniquement) ; ICMP = test/contrôle (MC20).", ("MC20", "MC31"),
            ),
            LexiconEntry(
                "TCP", "Transmission Control Protocol", None,
                "Protocole de transport fiable, orienté connexion.",
                "Utilisé par HTTP/HTTPS/SSH/RDP — MC21.",
                "Confondre TCP (fiable, avec connexion) et UDP (rapide, sans connexion) — MC21.", ("MC13", "MC21"),
            ),
            LexiconEntry(
                "UDP", "User Datagram Protocol", None,
                "Protocole de transport rapide, sans connexion ni garantie de livraison.",
                "Utilisé par DNS et DHCP — MC21.",
                "Confondre TCP (fiable, avec connexion) et UDP (rapide, sans connexion) — MC21.", ("MC21",),
            ),
            LexiconEntry(
                "OSI", "Open Systems Interconnection", "Modèle OSI",
                "Modèle théorique à 7 couches (Physique, Liaison, Réseau, Transport, Session, Présentation, Application).",
                "Sert de référence pédagogique ; TCP/IP (4 couches) est le modèle réellement implémenté — MC13.",
                "OSI = 7 couches théoriques ; TCP/IP = 4 couches réellement utilisées.", ("MC13",),
            ),
            LexiconEntry(
                "NAT", "Network Address Translation", None,
                "Traduit une adresse IP privée en adresse IP publique pour accéder à Internet.",
                "MC22.",
                "Confondre NAT (traduction d'adresse générale) et PAT (partage d'une IP via les ports).", ("MC16", "MC22"),
            ),
            LexiconEntry(
                "VLAN", "Virtual LAN", "Réseau local virtuel",
                "Réseau local virtuel qui segmente logiquement un réseau physique en plusieurs réseaux distincts.",
                "Port access = un seul VLAN ; port trunk = plusieurs VLAN marqués 802.1Q — MC24.",
                "Sans VLAN, tous les appareils d'un même switch partagent le même domaine de broadcast.", ("MC23", "MC24", "MC26", "MC27"),
            ),
        ),
    ),
    LexiconTheme(
        key="cablage",
        title="6. Câblage / RJ45 / fibre",
        entries=(
            LexiconEntry(
                "RJ45", None, None,
                "Connecteur standard du câblage Ethernet en cuivre (paires torsadées).",
                "Sertissage d'un câble RJ45 selon T568A/T568B — MC15.",
                None, ("MC15", "MC37"),
            ),
            LexiconEntry(
                "UTP", "Unshielded Twisted Pair", None,
                "Câble à paires torsadées non blindées, le type le plus courant.",
                "MC15.",
                None, ("MC15",),
            ),
            LexiconEntry(
                "STP", "Shielded Twisted Pair", None,
                "Câble à paires torsadées blindées, utilisées en environnement électriquement bruyant.",
                "MC15.",
                None, ("MC15",),
            ),
        ),
    ),
    LexiconTheme(
        key="wifi",
        title="7. Wi-Fi",
        entries=(
            LexiconEntry(
                "SSID", "Service Set Identifier", None,
                "Nom du réseau Wi-Fi affiché aux utilisateurs.",
                "MC25.",
                None, ("MC25", "MC26", "MC31"),
            ),
            LexiconEntry(
                "BSSID", "Basic Service Set Identifier", None,
                "Adresse MAC du point d'accès qui diffuse un SSID donné.",
                "MC25.",
                None, ("MC25",),
            ),
            LexiconEntry(
                "WPA2", "Wi-Fi Protected Access 2", None,
                "Protocole de sécurité Wi-Fi, largement répandu.",
                "MC26.",
                "WEP = jamais ; WPA2/WPA3 = standards actuels.", ("MC26",),
            ),
            LexiconEntry(
                "WPA3", "Wi-Fi Protected Access 3", None,
                "Protocole de sécurité Wi-Fi, standard actuel recommandé.",
                "MC26.",
                "WEP = jamais ; WPA2/WPA3 = standards actuels.", ("MC26",),
            ),
        ),
    ),
    LexiconTheme(
        key="securite",
        title="8. Sécurité",
        entries=(
            LexiconEntry(
                "ESD", "ElectroStatic Discharge", "Décharge électrostatique",
                "Décharge d'électricité statique du corps humain vers un composant, invisible mais potentiellement destructrice.",
                "Se protéger (bracelet antistatique, contact avec une masse métallique) avant d'ouvrir un PC — MC05/MC06/MC29.",
                None, ("MC05", "MC06", "MC29"),
            ),
            LexiconEntry(
                "VPN", "Virtual Private Network", "Réseau privé virtuel",
                "Tunnel chiffré permettant un accès distant sécurisé.",
                "MC27.",
                "Confondre chiffrement (VPN) et simple filtrage (pare-feu/ACL) — ce sont deux mécanismes différents.", ("MC27",),
            ),
        ),
    ),
    LexiconTheme(key="depannage", title="9. Dépannage", entries=()),
    LexiconTheme(key="sauvegarde", title="10. Sauvegarde / données", entries=()),
    LexiconTheme(
        key="metier",
        title="11. Métier / support",
        entries=(
            LexiconEntry(
                "DEEE", "Déchets d'Équipements Électriques et Électroniques", None,
                "Matériel informatique en fin de vie, à collecter via une filière dédiée — jamais la poubelle ordinaire.",
                "MC35.",
                None, ("MC35",),
            ),
        ),
    ),
)


def all_entries() -> tuple[LexiconEntry, ...]:
    return tuple(entry for theme in LEXICON_THEMES for entry in theme.entries)


def lexicon_defined_notions() -> frozenset[str]:
    """Notions couvertes par le lexique (ticket #83 § F) — utilisé par
    `app.v1.course_coverage.defined_notions_for_code` comme source pédagogique autorisée
    transverse, en plus du cours propre à chaque MC."""
    return frozenset(entry.acronym.upper() for entry in all_entries())

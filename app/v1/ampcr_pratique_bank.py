"""Banque des cours du parcours « AMPCR — Pratique écrite » (ticket #193 : PR06 ; #194 : PR11 ;
#197 : PR15 ; #198 : PR16 ; #199 : PR20 ; #200 : PR24).

Branchement sur le moteur de sessions existant, sans nouveau système :
- un cours pratique est une UAA du module `AMPCR-PRATIQUE` (slug `ampcr-pratique-pr06`) ;
- `PRACTICAL_COURSES` liste les cours réellement rédigés (jamais un emplacement vide) et
  leur contexte pédagogique de correction (`PedagogicalContext`) ;
- les questions sont importées à la demande (`import_practical_bank`, idempotent), avec
  leurs documents structurés (tableaux) ;
- **réserves séparées** : `QuestionVersion.prompt_version` vaut
  `ampcr-pratique-<code>:practice` (exercices du cours, « S'entraîner ») ou
  `…:exam` (mini-examen, « Examen blanc ») ; `restrict_to_mode` filtre la sélection de la
  banque selon le mode de la session. Les questions des autres matières ne portent pas ce
  préfixe et ne sont jamais filtrées ;
- **pas de génération IA** pour ces cours (`is_practical_code`) : l'épreuve pratique exige
  des questions vérifiées, contextualisées et barémées ; la correction reste celle du moteur
  (IA batch avec le barème, correction locale pour la classification).
"""

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.schemas import PedagogicalContext
from app.models import UAA, Module
from app.v1 import question_types  # noqa: F401 — enregistre les types (#40) au chargement
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import PRACTICAL_MODULE_CODE
from app.v1.ampcr_pratique_pr06_bank import ALL_ITEMS as PR06_ITEMS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr11_bank import ALL_ITEMS as PR11_ITEMS
from app.v1.ampcr_pratique_pr15_bank import ALL_ITEMS as PR15_ITEMS
from app.v1.ampcr_pratique_pr16_bank import ALL_ITEMS as PR16_ITEMS
from app.v1.ampcr_pratique_pr20_bank import ALL_ITEMS as PR20_ITEMS
from app.v1.ampcr_pratique_pr24_bank import ALL_ITEMS as PR24_ITEMS
from app.v1.models import (
    GenerationSource,
    Question,
    QuestionVersion,
    create_question,
    create_source_document,
)
from app.v1.question_engine import validate_content

PROMPT_VERSION_PREFIX = "ampcr-pratique"
SHORT_ANSWER_MAX_LENGTH = 3000
LONG_ANSWER_MAX_LENGTH = 20000


@dataclass(frozen=True)
class PracticalCourse:
    code: str
    title: str
    items: tuple[PR06Item, ...]
    context: PedagogicalContext

    @property
    def slug(self) -> str:
        return f"ampcr-pratique-{self.code.lower()}"


_PR06_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr06",
    course_title="AMPCR pratique écrite — PR06 Diagnostic des pannes matérielles",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien, sans matériel réel"
    ),
    allowed_notions=[
        "recueil des symptômes, chronologie, changements récents, données et autorisations",
        "observation, hypothèse, test, résultat, conclusion ; du plus simple au plus invasif",
        "reproduction sans aggraver, un changement à la fois, configuration minimale, test croisé avec un composant connu fonctionnel",
        "sécurité : coupure secteur, décharge résiduelle, ESD, ne jamais ouvrir un bloc d'alimentation ni une batterie gonflée",
        "chaîne de démarrage : secteur, bloc d'alimentation, carte mère, POST, firmware BIOS/UEFI, stockage, chargeur, système",
        "PC inerte, ventilateurs sans image, absence de POST, « No boot device », redémarrages, écrans bleus, extinctions sous charge",
        "bips, LED et codes POST propres à chaque fabricant (manuel)",
        "RAM (barrette, slot, compatibilité, test mémoire, ECC), processeur et refroidissement (température, throttling, arrêt de protection)",
        "bloc d'alimentation (puissance, connecteurs ATX 24, EPS, PCIe, SATA, testeur), carte mère (condensateurs, VRM, liquide)",
        "affichage (écran, entrée, câble, sortie de la carte graphique ou iGPU), stockage (HDD, SSD, SATA, M.2 SATA/NVMe, SMART comme indice), périphériques et pilotes",
        "compatibilité : socket, génération DDR, format, alimentation, PCIe, SATA/M.2, firmware ; documentation du fabricant",
        "journaux (Kernel-Power 41, codes d'arrêt), indices et preuves, escalade, priorité aux données, compte rendu",
    ],
    competencies=[
        "Rédiger une démarche de diagnostic ordonnée et justifiée à partir d'un cas écrit",
        "Interpréter un document technique fictif (relevé, journal, manuel, rapport SMART, températures)",
        "Proposer une intervention sûre, sa vérification et un compte rendu professionnel",
    ],
    vocabulary=[
        "POST", "firmware", "UEFI", "CSM", "PWR_OK", "+5 VSB", "EPS", "configuration minimale",
        "test croisé", "SMART", "throttling", "Kernel-Power 41", "ESD",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question ; "
        "pénaliser une action dangereuse (sous tension, ouverture d'un bloc d'alimentation ou "
        "d'une batterie) ou destructive pour les données sans sauvegarde ni accord ; ne jamais "
        "valider une correspondance universelle de bips ou de codes POST."
    ),
)

_PR11_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr11",
    course_title="AMPCR pratique écrite — PR11 Messages d'erreur Windows/Linux",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de captures et de journaux fictifs"
    ),
    allowed_notions=[
        "recueil : texte exact, code, contexte, date, déclencheur, changements récents, périmètre, criticité, données à préserver",
        "stades : firmware/POST, chargeur, noyau/système, session, service, application, pilote, périphérique, stockage, réseau",
        "code d'erreur, cause probable, hypothèse, test de confirmation, résultat attendu, action corrective ; documentation fiable, pas de cause unique tirée d'un code ambigu",
        "ordre : sauvegarde, preuves, tests simples, réparation réversible, opération invasive avec autorisation, validation",
        "No bootable device / Operating system not found / Reboot and Select proper Boot device : détection, UEFI/GPT ou hérité/MBR, ordre de démarrage, câblage, partition EFI, chargeur",
        "Windows Boot Manager, BCD (0xc000000f), WinRE (réparation du démarrage, restauration, désinstallation de mises à jour, mode sans échec), prudence avec bootrec, bcdboot, diskpart",
        "GRUB rescue, initramfs (UUID introuvable), emergency mode, /etc/fstab, UUID, nofail, mount -a",
        "écrans bleus : code d'arrêt, fichier cité, BugCheck 1001, Kernel-Power 41, 6008, redémarrage automatique ; pilotes, RAM, disque, mise à jour, température comme hypothèses",
        "Gestionnaire de périphériques : périphérique inconnu, triangle, désactivé, Codes 10, 22, 28, 43, restaurer le pilote",
        "Observateur d'événements : Système, Application, niveau, source, ID, heure ; corrélation n'est pas causalité",
        "Gestion des disques (hors ligne, non initialisé, sans lettre, RAW, plein), services (statut, type de démarrage, compte, dépendances)",
        "ipconfig /all, ping, nslookup, tracert, sfc /scannow, DISM /RestoreHealth, chkdsk (lecture seule, /f, /r), gestionnaire des tâches, msconfig ; diagnostic ou modification",
        "Windows Update (0x80070070 espace insuffisant), profil temporaire (1511), droits, applications",
        "Linux : systemctl status/start/restart/enable, journalctl -b -u -p, dmesg, df -h, df -i, du, lsblk, mount, ip addr, ip route, ss, resolvectl/dig, lsof +L1",
        "droits rwx, propriétaire, groupe, chmod, chown, jamais chmod 777 ; apt et dnf selon la distribution",
        "réseau : APIPA 169.254, passerelle, DNS, conflit IP, imprimante hors ligne ; un poste ou tous",
        "pannes intermittentes : chronologie, conditions, changements, preuves, répétition",
        "compte rendu : demande, environnement, symptômes, preuves, hypothèses, tests, résultats, cause (ou non déterminée), action et autorisation, validation, risques, recommandation, clôture",
    ],
    competencies=[
        "Interpréter un message d'erreur, une capture ou un journal fictif et situer le stade de l'erreur",
        "Rédiger une procédure de diagnostic ordonnée et non destructive sous Windows et sous Linux",
        "Proposer une réparation réversible d'abord, avec sauvegarde et autorisation, sa validation et un compte rendu",
    ],
    vocabulary=[
        "BCD", "WinRE", "UEFI", "CSM", "GPT", "MBR", "ESP", "STOP code", "BugCheck",
        "Kernel-Power 41", "Code 43", "SFC", "DISM", "chkdsk", "GRUB", "initramfs", "fstab",
        "UUID", "systemd", "journalctl", "inode", "APIPA",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ni l'orthographe exacte d'une commande si "
        "l'outil et son rôle sont clairs ; suivre le barème de la question ; valoriser la "
        "méthode, la sécurité des données, les tests et la justification ; pénaliser un "
        "formatage, une réinstallation, une initialisation de disque, un chkdsk /r, un fsck sur "
        "un volume monté ou un chmod 777 proposés sans précaution ; ne jamais valider une cause "
        "unique affirmée à partir d'un seul code ou d'une simple coïncidence."
    ),
)

_PR15_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr15",
    course_title="AMPCR pratique écrite — PR15 Câblage RJ45 T568A/B",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de relevés de testeur et de "
        "situations de câblage fictifs"
    ),
    allowed_notions=[
        "câble à 4 paires torsadées, 8 conducteurs, rôle de la torsade, diaphonie, détorsadage limité à environ 13 mm",
        "U/UTP, F/UTP, U/FTP, S/FTP ; UTP, FTP, STP historiques ; blindage continu de bout en bout, mise à la terre selon l'installation",
        "Cat5e (100 MHz, 1 Gb/s sur 100 m), Cat6 (250 MHz, 10 Gb/s sur longueur réduite d'environ 37 à 55 m), Cat6A (500 MHz, 10 Gb/s sur 100 m)",
        "connecteur 8P8C dit RJ45, fiche, prise, keystone, panneau de brassage, cordon ; monobrin pour l'installation, multibrin pour les cordons ; fiches adaptées",
        "orientation : contacts dorés face à soi, languette dessous, câble vers le bas, broche 1 à gauche",
        "T568B : 1 blanc/orange, 2 orange, 3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert, 7 blanc/marron, 8 marron",
        "T568A : 1 blanc/vert, 2 vert, 3 blanc/orange, 4 bleu, 5 blanc/bleu, 6 orange, 7 blanc/marron, 8 marron",
        "A et B échangent les paires orange et verte (broches 1, 2, 3, 6) ; bleue (4-5) et marron (7-8) identiques ; positions de paire 1-2, 3-6, 4-5, 7-8 ; paire séparée (split pair)",
        "câble droit A-A ou B-B ; croisé A-B (1→3, 2→6, 3→1, 6→2) ; MDI/MDI-X ; Auto MDI-X et ses limites",
        "10/100BASE-TX sur deux paires (1-2 émission, 3-6 réception côté carte) ; 1000BASE-T sur quatre paires bidirectionnelles",
        "lien physique, négociation de vitesse et duplex, configuration IP : trois niveaux distincts",
        "fabrication : manchons, coupe, dénudage sans entailler, ordre, recoupe, butée, gaine sous la patte de maintien, sertissage, autre bout, test avant mise en service ; poinçonnage d'un keystone",
        "wiremap : circuit ouvert, court-circuit, paire inversée, paires croisées, paire séparée, défaut intermittent ; continuité, qualification, certification",
        "canal 100 m = 90 m de lien permanent + cordons ; atténuation, NEXT, blindage, rapport signal/bruit ; lien à 100 Mb/s si 4-5 ou 7-8 défectueuse",
        "chaîne baie, panneau, câble permanent, prise, cordon, PC ; étiquetage ; rapport : besoin, norme, schéma, outils, tests avant/après, résultats, défauts corrigés, validation",
    ],
    competencies=[
        "Appliquer et vérifier les brochages T568A/T568B, pour un câble droit ou croisé",
        "Interpréter un relevé de testeur ou un rapport de qualification/certification et proposer la correction",
        "Rédiger une procédure de fabrication, de raccordement ou de diagnostic et un compte rendu",
    ],
    vocabulary=[
        "8P8C", "RJ45", "T568A", "T568B", "keystone", "panneau de brassage", "monobrin",
        "multibrin", "wiremap", "split pair", "NEXT", "Auto MDI-X", "U/UTP", "F/UTP", "S/FTP",
        "Cat5e", "Cat6", "Cat6A",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question. Un "
        "ordre de couleurs, une broche ou une paire faux est toujours une erreur, même bien "
        "rédigé ; accepter « blanc-orange », « blanc/orange » ou « orange-blanc » pour le même "
        "fil. Ne jamais valider « Cat6 = 10 Gb/s sur 100 m », « un testeur de continuité "
        "certifie la catégorie » ni « le gigabit n'utilise que deux paires »."
    ),
)

_PR16_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr16",
    course_title="AMPCR pratique écrite — PR16 Câble coaxial et BNC",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de schémas de bus, de mesures et "
        "de situations de câblage coaxial fictifs"
    ),
    allowed_notions=[
        "câble coaxial : âme, diélectrique, blindage (feuille et/ou tresse), gaine ; protection EMI, atténuation selon longueur et fréquence, bande passante, souplesse, rayon de courbure, écrasement",
        "impédance caractéristique : dépend de la géométrie et de l'isolant, pas de la longueur ; ne se mesure pas à l'ohmmètre ; RG-58 50 Ω, coaxial épais 50 Ω, RG-59 et RG-6 75 Ω, RG-62 93 Ω ; lire le marquage",
        "50 Ω : 10BASE2, 10BASE5, radiofréquence ; 75 Ω : vidéo analogique, SDI, télévision, satellite ; câble, connecteur, terminaison et équipement de même impédance",
        "réflexions : Γ = (Zc − Z0)/(Zc + Z0) ; extrémité ouverte +1, court-circuit −1, adapté 0, 75 Ω sur 50 Ω 0,2 ; terminaison absente ou erronée, rupture, connecteur défectueux, câble écrasé ; collisions et erreurs sur un bus",
        "BNC : baïonnette quart de tour, mâle/femelle, T, terminateur, raccord ; variantes 50 Ω et 75 Ω qui s'emboîtent ; à sertir, à compression, à souder, à visser déconseillé ; connecteur prévu pour le câble",
        "10BASE2 : bus, 10 Mb/s, RG-58 A/U ou C/U 50 Ω, segment 185 m, 30 postes, 0,5 m entre T, T directement sur la carte, terminateur 50 Ω aux deux extrémités, terre en un seul point, répéteurs (5-4-3)",
        "10BASE5 : coaxial épais 50 Ω ≈ 10 mm, 10 Mb/s, segment 500 m, 100 transceivers, repères tous les 2,5 m, prise vampire, transceiver, câble AUI 15 broches ≤ 50 m, terminateurs 50 Ω sur connecteurs N ; distinct du 10BASE2",
        "liaisons vidéo 75 Ω point à point (caméra, SDI, RG-59, BNC 75 Ω), TV et satellite (RG-6, fiche F) ; la forme du connecteur ne définit ni le protocole ni l'impédance",
        "fabrication : matériel cohérent, notice et cotes du fabricant (pas de cotes universelles), manchon et bague d'abord, dénudage sans entailler, contact central serti en butée, corps, tresse sans brin vers l'âme, bague sertie",
        "contrôles : visuel, traction, continuité âme et blindage, âme/blindage infini, bus refermé ≈ 25 Ω réseau arrêté ; outils : coupe-câble, dénudeur coaxial calibré, pince et matrice adaptées, multimètre, testeur coaxial, réflectomètre",
        "lectures d'ohmmètre au T, réseau arrêté : 25 Ω normal, 50 Ω un seul terminateur vu (absent ou coupure), 0 Ω court-circuit, infini bus ouvert, 30 ou 37,5 Ω terminateur de mauvaise valeur ; écrasement et mauvais sertissage souvent invisibles",
        "diagnostic : perte totale, intermittence, réflexions, connecteur desserré, blindage rompu, câble écrasé, terminaison manquante ; dichotomie, réflectomètre (même sens = ouvert, inversé = court-circuit, d = VF × c × t / 2), réparation, vérification",
        "sécurité : réseau arrêté pour mesurer, prévenir avant d'ouvrir un bus, TV/satellite débranché ; rapport : demande, constats, hypothèses, tests et valeurs, cause, action, validation, recommandation dont migration",
    ],
    competencies=[
        "Lire, vérifier et corriger un schéma de bus coaxial 10BASE2 (T, terminaisons, impédance, limites)",
        "Choisir câble, connecteurs et terminaisons de même impédance selon l'usage (50 Ω / 75 Ω)",
        "Rédiger la fabrication d'une liaison BNC et un diagnostic avec mesures, réparation et compte rendu",
    ],
    vocabulary=[
        "coaxial", "âme", "diélectrique", "tresse", "impédance caractéristique", "BNC", "T BNC",
        "terminateur", "10BASE2", "10BASE5", "RG-58", "RG-59", "RG-6", "prise vampire",
        "transceiver", "AUI", "SDI", "réflexion", "réflectomètre", "TDR", "facteur de vélocité",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question. Une "
        "impédance fausse (75 Ω pour le 10BASE2, 50 Ω pour la vidéo SDI), un bus sans deux "
        "terminateurs 50 Ω, un T relié à la carte par un câble ou un câblage en étoile sont "
        "toujours des erreurs. Ne jamais valider « tous les BNC sont à 50 Ω », « l'ohmmètre "
        "mesure l'impédance du câble », des cotes de dénudage universelles, ni la confusion "
        "entre 10BASE5 et 10BASE2 ; pénaliser une mesure sur réseau en service ou l'ouverture "
        "d'un bus sans prévenir."
    ),
)

_PR20_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr20",
    course_title="AMPCR pratique écrite — PR20 IPv4, MAC, masques et passerelles",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de plans d'adressage, de relevés "
        "de commandes (ipconfig, ip addr, ip route) et de situations réseau fictifs"
    ),
    allowed_notions=[
        "réseau local : carte réseau (interface), liaison Ethernet ou Wi-Fi, switch (MAC), routeur, passerelle, serveur DHCP, serveur DNS, box ; connectivité physique puis logique",
        "adresse MAC : 48 bits, 12 chiffres hexadécimaux, OUI du fabricant + numéro de carte, rôle sur le lien local, unicité administrative, MAC aléatoires ou virtuelles (bit U/L à 1), modifiable ; MAC ≠ IP, MAC ≠ identité fiable, filtrage MAC ≠ sécurité ; ipconfig /all, getmac, ip link, arp -a, ip neigh",
        "IPv4 : 32 bits, 4 octets 0-255, notation décimale pointée, partie réseau / hôte, unicast, adresse de réseau, diffusion ; privées 10.0.0.0/8, 172.16.0.0/12 (jusqu'à 172.31.255.255), 192.168.0.0/16 ; 127.0.0.1 bouclage ; 169.254.0.0/16 APIPA ; 0.0.0.0 non spécifiée",
        "masque contigu, préfixe CIDR : /24 255.255.255.0 (254 hôtes), /25 .128 (126), /26 .192 (62), /27 .224 (30), /28 .240 (14), /30 .252 (2) ; réseau = IP ET masque, diffusion = bits d'hôte à 1, hôtes usuels = 2^(32−n) − 2 ; /31 et /32 en complément",
        "même sous-réseau (même réseau et même masque) = communication directe ; sinon routeur ; masques différents = vues incohérentes",
        "passerelle par défaut : routeur, dans le réseau du poste, sert à sortir du réseau ; route locale vs route par défaut 0.0.0.0/0 ; passerelle ≠ DNS",
        "DNS : nom → IP ; ping par IP OK et par nom KO = résolution de noms, pas panne Internet ; nslookup, ipconfig /flushdns",
        "DHCP : Discover, Offer, Request, Acknowledge ; bail ; options masque, passerelle, DNS ; statique vs dynamique ; réservation par MAC ; adresses fixes hors de l'étendue ; APIPA = aucun bail, indice et non preuve unique",
        "Windows : ipconfig, ipconfig /all, /release, /renew, ping, tracert, nslookup, arp -a, route print ; lecture vs modification ; fenêtre Protocole Internet version 4",
        "Linux : ip addr, ip route, ip neigh, ping -c, resolvectl si présent ; ip addr add / ip route add temporaires ; persistant via NetworkManager (nmcli), Netplan ou outil de la distribution, pas de commande universelle",
        "plan d'adressage de 2 à 6 postes et équipements : même masque, passerelle, DNS ; pas de doublon, ni adresse de réseau ou de diffusion, adresses fixes hors étendue ou réservations ; connexion directe de deux PC dans le même réseau, sans passerelle, Auto MDI-X",
        "diagnostic : lien, relevé, ping 127.0.0.1, propre IP, voisin ou passerelle, IP distante, nom ; ICMP parfois filtré par le pare-feu ; arp, routes, DHCP ; constat, hypothèse, test, résultat, action ; IP dupliquée, mauvais masque, mauvaise passerelle, DNS erroné, DHCP absent, APIPA, sous-réseaux incompatibles, câble débranché, carte désactivée, mauvaise interface",
        "compte rendu : contexte, plan avant/après, commandes et observations, hypothèses, cause, corrections, tests de validation, risques et recommandations",
    ],
    competencies=[
        "Calculer réseau, diffusion, plage et nombre d'hôtes ; convertir masque et préfixe ; dire si deux postes sont dans le même sous-réseau",
        "Relever et interpréter MAC, IP, masque, passerelle et DNS (Windows, Linux) ; configurer un poste et rédiger un plan d'adressage cohérent",
        "Diagnostiquer un défaut d'adressage en justifiant chaque test et rédiger le compte rendu",
    ],
    vocabulary=[
        "adresse MAC", "OUI", "IPv4", "masque", "préfixe", "CIDR", "adresse de réseau",
        "diffusion", "passerelle par défaut", "route par défaut", "DNS", "DHCP", "bail",
        "réservation", "étendue", "APIPA", "bouclage", "RFC 1918", "ARP", "ICMP",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation "
        "techniquement juste, sans exiger de mot-clé ; suivre le barème de la question ; "
        "accepter toute autre adresse libre et cohérente quand plusieurs choix sont possibles. "
        "Un calcul faux (réseau, diffusion, plage, nombre d'hôtes, masque ↔ préfixe), une "
        "passerelle hors du réseau du poste, une adresse de réseau ou de diffusion attribuée à "
        "un poste ou une adresse fixe placée dans l'étendue DHCP sont toujours des erreurs. Ne "
        "jamais valider « 172.32.x.x est privée », « l'APIPA prouve que le serveur DHCP est en "
        "panne », « ping par nom KO donc Internet en panne », « le filtrage MAC sécurise le "
        "réseau » ni une commande Linux présentée comme universelle pour une configuration "
        "persistante."
    ),
)

_PR24_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr24",
    course_title="AMPCR pratique écrite — PR24 Dépannage réseau et Internet",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de dossiers d'intervention fictifs "
        "(plan réseau, symptômes, relevés de commandes, journaux, état des équipements)"
    ),
    allowed_notions=[
        "méthode en couches : symptôme exact, périmètre (un poste ou tous, filaire ou Wi-Fi, local ou Internet), chronologie, changements récents, topologie, hypothèses, tests non destructifs, conclusion ; corrélation n'est pas preuve",
        "physique et liaison : câble cuivre ou fibre, RJ45, voyants, port du switch actif ou désactivé, prise brassée, négociation vitesse/duplex, désaccord de duplex (repli en half), erreurs CRC, blindage, 100 m, Auto MDI-X, alimentation et PoE (802.3af 15,4 W, 802.3at 30 W), NO-CARRIER, média déconnecté ; pas de diagnostic IP sans lien",
        "configuration IP : adresse du réseau, masque/CIDR, passerelle dans le réseau, route par défaut, MAC de la bonne carte, même sous-réseau, doublon d'adresse (arp -a), APIPA 169.254.0.0/16 = aucun bail (indice, pas preuve), statique hors étendue, réservation",
        "DHCP : DORA, bail et renouvellement, options passerelle (3) et DNS (6), étendue épuisée (no address available), serveur arrêté ou qui ignore une carte, postes déjà configurés qui fonctionnent sur leur bail, relais si serveur dans un autre réseau, second serveur DHCP, ipconfig /renew, /release qui coupe la connexion",
        "DNS : ping par IP OK et nom KO = résolution, pas Internet ; nslookup, dig, resolvectl ; réponse, NXDOMAIN (nom inexistant), délai dépassé (serveur injoignable) ; DNS interne vs public (noms internes) ; cache, ipconfig /flushdns, nslookup contourne cache et hosts",
        "passerelle et routage : hôte local, passerelle, IP distante ; tracert/traceroute, étoiles intermédiaires non bloquantes ; route par défaut absente (Network is unreachable) ; masque faux = passerelle hors réseau ; routeur entre sous-réseaux ; NAT de la box ; pare-feu, ACL, ICMP filtré : ping sans réponse n'est pas une preuve",
        "switch et VLAN : table MAC, port désactivé, port dans le mauvais VLAN = autre réseau ou APIPA ; access/trunk en complément ; pas de VLAN supposé sans indice",
        "Wi-Fi : SSID, BSSID, signal, bande 2,4/5 GHz, canal, interférences, répéteur (débit souvent divisé) ; association et authentification WPA2-Personnel (CCMP) / WPA3-Personnel (SAE), clé, profil obsolète, mode de transition ; DHCP après association ; radio, authentification et IP sont trois problèmes distincts",
        "partages et imprimantes : découverte du réseau, chemin UNC, 0x80070035 chemin introuvable, accès refusé, compte de domaine ou local en groupe de travail, identifiants mémorisés, droits de partage + NTFS (le plus restrictif), SMB port 445, Test-NetConnection -Port ; file d'impression, port de la file, service Spouleur",
        "outils Windows : ipconfig /all, ping, tracert -d, nslookup, arp -a, route print, netstat -an, Get-NetTCPConnection, Test-NetConnection, netsh wlan show interfaces ; lecture vs modification ; limites du ping",
        "outils Linux : ip addr, ip link, ip route, ip neigh, ping -c, traceroute, tracepath, dig, nslookup, ss, journalctl, nmcli, resolvectl ; outils pas toujours installés ; ip route add temporaire, persistance selon la distribution (NetworkManager, Netplan…)",
        "procédure : physique → IP/masque → passerelle → IP distante → DNS → service ; pannes combinées (câble + DNS, masque + passerelle, DHCP intermittent, LAN OK/Internet KO, Internet OK/partage KO, Wi-Fi associé sans IP, lenteur intermittente) ; revérifier après chaque correction",
        "sécurité : autorisation avant de modifier la production, état initial, retour arrière, une modification à la fois, prévenir des coupures, pas de scan intrusif non autorisé, pas de réinitialisation de box « pour voir », confidentialité des journaux",
        "rapport : contexte, symptômes, périmètre, schéma, hypothèses, tests et sorties, cause confirmée ou incertaine, correction et autorisation, tests finaux, prévention, restitution",
    ],
    competencies=[
        "Localiser méthodiquement une panne réseau ou Internet à partir d'un dossier écrit (périmètre, couche)",
        "Interpréter des relevés (ping, tracert, nslookup, ipconfig, journaux DHCP, état Wi-Fi, ports du switch) et choisir des tests discriminants non destructifs",
        "Proposer une correction autorisée avec retour arrière, la valider et rédiger le rapport d'intervention",
    ],
    vocabulary=[
        "APIPA", "DHCP", "DORA", "bail", "étendue", "relais DHCP", "DNS", "NXDOMAIN", "passerelle",
        "route par défaut", "NAT", "ICMP", "tracert", "VLAN", "duplex", "CRC", "PoE", "SSID",
        "BSSID", "WPA2", "WPA3", "UNC", "SMB", "NTFS", "spouleur",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et toute "
        "démarche techniquement justes, sans exiger de mot-clé ni l'orthographe exacte d'une "
        "commande si l'outil et son rôle sont clairs ; suivre le barème de la question. Une "
        "lecture fausse d'un relevé (perte, saut, réponse DNS, adresse) est toujours une erreur. "
        "Ne jamais valider « l'APIPA prouve que le serveur DHCP est en panne », « ping par nom KO "
        "donc Internet en panne », « un ping sans réponse prouve que la machine est éteinte », "
        "« des étoiles dans un tracert prouvent une panne » quand la destination est atteinte, "
        "ni une erreur de VLAN affirmée sans indice. Pénaliser une modification de production "
        "sans autorisation ni état initial, une réinitialisation de box, un scan non autorisé, "
        "un ipconfig /release à distance et une cause affirmée sans test."
    ),
)

PRACTICAL_COURSES: tuple[PracticalCourse, ...] = (
    PracticalCourse(
        code="PR06", title="Diagnostic des pannes matérielles", items=PR06_ITEMS, context=_PR06_CONTEXT
    ),
    PracticalCourse(
        code="PR11",
        title="Messages d'erreur Windows/Linux — diagnostic et interventions écrites",
        items=PR11_ITEMS,
        context=_PR11_CONTEXT,
    ),
    PracticalCourse(
        code="PR15",
        title="Câblage RJ45 T568A/B — fabrication, schémas et tests",
        items=PR15_ITEMS,
        context=_PR15_CONTEXT,
    ),
    PracticalCourse(
        code="PR16",
        title="Câble coaxial et BNC — impédance, fabrication et diagnostic écrit",
        items=PR16_ITEMS,
        context=_PR16_CONTEXT,
    ),
    PracticalCourse(
        code="PR20",
        title="IPv4, MAC, masques et passerelles — configuration et diagnostics écrits",
        items=PR20_ITEMS,
        context=_PR20_CONTEXT,
    ),
    PracticalCourse(
        code="PR24",
        title="Dépannage réseau et Internet — dossiers d'intervention écrits",
        items=PR24_ITEMS,
        context=_PR24_CONTEXT,
    ),
)
PRACTICAL_COURSES_BY_CODE: dict[str, PracticalCourse] = {c.code: c for c in PRACTICAL_COURSES}
PRACTICAL_COURSES_BY_SLUG: dict[str, PracticalCourse] = {c.slug: c for c in PRACTICAL_COURSES}


def get_practical_course_by_slug(uaa_slug: str) -> PracticalCourse | None:
    return PRACTICAL_COURSES_BY_SLUG.get(uaa_slug)


def is_practical_code(uaa_code: str | None) -> bool:
    return bool(uaa_code) and uaa_code in PRACTICAL_COURSES_BY_CODE


def get_practical_context(uaa_code: str | None) -> PedagogicalContext | None:
    course = PRACTICAL_COURSES_BY_CODE.get(uaa_code or "")
    return course.context if course else None


def usage_tag(code: str, usage: str) -> str:
    return f"{PROMPT_VERSION_PREFIX}-{code.lower()}:{usage}"


def restrict_to_mode(questions: list[Question], mode_value: str | None) -> list[Question]:
    """Garde, pour les questions du parcours pratique, celles de la réserve du mode
    (`practice`/`exam`). No-op pour toute autre question et quand `mode_value` est absent."""
    if mode_value is None:
        return questions
    return [q for q in questions if question_usage(q) in (None, mode_value)]


def _document_layout(document: ExerciseDocument) -> dict | None:
    if document.kind == "console":
        # Ticket #194 : capture de terminal ou extrait de journal, affiché en police à chasse
        # fixe, ligne à ligne (`_document_layouts.html`, mise en page « console »).
        return {
            "kind": "console",
            "lines": document.content_text.splitlines(),
            "notice": "Extrait fictif reconstitué pour l'exercice (messages au format réel).",
        }
    if document.kind != "tableau":
        return None
    rows = document.table_rows()
    return {"kind": "table", "columns": rows[0], "rows": rows[1:]}


def _create_documents(db: Session, module: Module, item: PR06Item) -> list[int]:
    ids = []
    for document in item.documents:
        layout = _document_layout(document)
        created = create_source_document(
            db,
            title=document.title,
            content_text=document.content_text,
            content_json={"layout": layout} if layout else None,
            module_id=module.id,
        )
        ids.append(created.current_version_id)
    db.flush()
    return ids


def item_content(item: PR06Item, document_version_ids: list[int]) -> dict:
    """Contenu `content_json` d'une question, au format d'un type existant."""
    content: dict = {"prompt": item.prompt}
    if item.question_type == "classification":
        assert item.classification is not None
        content.update(
            categories=list(item.classification.categories),
            elements=list(item.classification.elements),
            correct_categories=list(item.classification.correct),
            explanation=" ".join(item.correction),
        )
    elif item.question_type == "ordering":
        assert item.ordering is not None
        ids = [f"etape-{i + 1}" for i in range(len(item.ordering.steps))]
        content.update(
            items=[{"id": ids[i], "label": step} for i, step in enumerate(item.ordering.steps)],
            correct_order=[ids[i] for i in item.ordering.correct],
            explanation=" ".join(item.correction),
        )
    else:
        content["rubric"] = item.rubric()
        if item.question_type == "short_answer":
            content["max_length"] = SHORT_ANSWER_MAX_LENGTH
        else:
            content.update(
                expected_points=[c.expected for c in item.criteria],
                max_score=item.total_points,
                max_length=LONG_ANSWER_MAX_LENGTH,
            )
    if document_version_ids:
        content["source_document_version_id"] = document_version_ids[0]
        if len(document_version_ids) > 1:
            content["source_document_version_ids"] = list(document_version_ids)
    return content


def import_practical_bank(db: Session, module: Module, uaa: UAA) -> int:
    """Importe la banque d'un cours pratique (idempotent : rien si l'UAA a déjà ses
    questions importées)."""
    course = PRACTICAL_COURSES_BY_CODE.get(uaa.code)
    if course is None or module.code != PRACTICAL_MODULE_CODE:
        return 0
    already = (
        db.query(Question)
        .filter_by(uaa_id=uaa.id, generation_source=GenerationSource.IMPORTED)
        .count()
    )
    if already:
        return 0
    imported = 0
    for item in course.items:
        document_ids = _create_documents(db, module, item)
        content = item_content(item, document_ids)
        validate_content(item.question_type, 1, content)
        create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=item.question_type,
            content_json=content,
            generation_source=GenerationSource.IMPORTED,
            prompt_version=usage_tag(course.code, item.usage),
            source_program_version="Consignes AMPCR pratique 2026-2027/1",
            source_document_version_id=document_ids[0] if document_ids else None,
        )
        imported += 1
    db.flush()
    return imported


PRACTICAL_BANK_IMPORTERS: dict[str, Callable[[Session, Module, UAA], int]] = {
    course.slug: import_practical_bank for course in PRACTICAL_COURSES
}


def _version_usage(version: QuestionVersion | None) -> str | None:
    tag = (version.prompt_version if version else None) or ""
    if not tag.startswith(PROMPT_VERSION_PREFIX) or ":" not in tag:
        return None
    return tag.rsplit(":", 1)[1]


def question_usage(question: Question) -> str | None:
    """Réserve (`practice`/`exam`) d'une question du parcours pratique, `None` sinon. Lue
    sur la version courante, sinon sur la première version marquée : une nouvelle version
    créée plus tard (correction, administration) ne change jamais de réserve."""
    usage = _version_usage(question.current_version)
    if usage is None:
        for version in sorted(question.versions, key=lambda v: v.version):
            usage = _version_usage(version)
            if usage is not None:
                break
    return usage

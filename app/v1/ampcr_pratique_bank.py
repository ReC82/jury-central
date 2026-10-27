"""Banque des cours du parcours « AMPCR — Pratique écrite » (ticket #193 : PR06 ; #194 : PR11 ;
#197 : PR15 ; #198 : PR16 ; #199 : PR20 ; #200 : PR24 ; #202 : PR01 ; #203 : PR02 ; #204 : PR03 ;
#205 : PR04 ; #206 : PR05 ; #207 : PR07) et premier examen blanc de module (#230 : EX01, réserve `exam` seule).

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
from app.v1.ampcr_pratique_ex01_bank import ALL_ITEMS as EX01_ITEMS
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import PRACTICAL_MODULE_CODE
from app.v1.ampcr_pratique_pr01_bank import ALL_ITEMS as PR01_ITEMS
from app.v1.ampcr_pratique_pr02_bank import ALL_ITEMS as PR02_ITEMS
from app.v1.ampcr_pratique_pr03_bank import ALL_ITEMS as PR03_ITEMS
from app.v1.ampcr_pratique_pr04_bank import ALL_ITEMS as PR04_ITEMS
from app.v1.ampcr_pratique_pr05_bank import ALL_ITEMS as PR05_ITEMS
from app.v1.ampcr_pratique_pr06_bank import ALL_ITEMS as PR06_ITEMS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr07_bank import ALL_ITEMS as PR07_ITEMS
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

_PR01_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr01",
    course_title="AMPCR pratique écrite — PR01 Structure d'un PC et identification des composants",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir de descriptions, schémas, fiches "
        "produits fictives et relevés d'inventaire"
    ),
    allowed_notions=[
        "structure : unité centrale, composants internes, périphériques ; processeur, mémoire vive, stockage, carte mère, chipset, bloc d'alimentation (aucune donnée transportée)",
        "cheminement des données : RAM, PCIe x16 principal et souvent le premier M.2 reliés au processeur ; SATA, USB, réseau, audio, M.2 et PCIe secondaires par le chipset et sa liaison partagée",
        "formats ATX 305 × 244 mm (7 emplacements), microATX 244 × 244 mm (4), Mini-ITX 170 × 170 mm (1) ; carte plus petite dans un boîtier plus grand, jamais l'inverse ; limites du boîtier (longueur de carte graphique, hauteur de ventirad, bloc ATX/SFX) ; flux d'air",
        "carte mère : socket LGA/PGA (AM4 PGA DDR4, AM5 LGA DDR5, LGA1700 DDR4 ou DDR5 selon la carte, LGA1851), liste des processeurs pris en charge et version du firmware ; chipset ; VRM (+12 V de l'EPS vers la tension du processeur) ; emplacements DIMM, PCIe (taille mécanique et lignes électriques, rétrocompatibilité), M.2 (clé, NVMe/SATA, 2280), SATA 7 contacts ; connecteurs internes USB 2.0 9 broches, USB 3.x 19 broches, HD_AUDIO, CPU_FAN, façade, pile CMOS, puce du firmware",
        "processeur : socket, cœurs, fréquence, puissance thermique, mémoire prise en charge, partie graphique intégrée parfois absente ; cache volatile ; ventirad (socket, puissance dissipée, hauteur), pâte thermique, CPU_FAN",
        "mémoires : RAM volatile ; ROM = puce flash du firmware, non volatile, réinscriptible par mise à jour, ne contient ni système ni fichiers ; stockage de masse non volatile (SSD, HDD, clé) ; DIMM 133,35 mm / SO-DIMM ; DDR3 240/204, DDR4 288/260, DDR5 288/262 contacts ; encoches et tensions différentes ; capacité maximale ; double canal selon le manuel ; ECC",
        "firmware BIOS/UEFI (GPT, Secure Boot, CSM), POST, bips et LED selon le fabricant, pile CMOS (horloge, parfois réglages), effacement du CMOS sans perte de données, mise à jour sans coupure",
        "stockage : HDD 3,5/2,5 pouces SATA, SSD SATA 2,5 pouces, M.2 SATA, M.2 NVMe (PCIe) ; SATA 6 Gbit/s ≈ 600 Mo/s utiles, PCIe 3.0 x4 ≈ 3,9 Go/s, 4.0 x4 ≈ 7,9 Go/s ; M.2 SATA non détecté dans un M.2 NVMe seul ; port SATA désactivé par un M.2 en SATA ; unités décimales et binaires (500 Go = 465,7G)",
        "connecteurs du bloc : ATX 24 (20+4), EPS 8 (4+4) CPU, PCIe 6/8 (6+2), 16 broches 12V-2x6, SATA 15, Molex 4 ; EPS et PCIe 8 broches non interchangeables ; câbles modulaires d'origine uniquement",
        "carte graphique : PCIe x16, 75 W par l'emplacement, connecteurs PCIe, longueur, épaisseur, puissance recommandée, sorties ; écran sur la carte graphique, sorties de la carte mère seulement avec partie graphique intégrée",
        "ports : USB 2.0 480 Mbit/s, USB 3.2 Gen 1 5 Gbit/s, Gen 2 10 Gbit/s, Gen 2x2 20 Gbit/s, USB4 40 Gbit/s ; USB-C = forme, pas débit ; HDMI, DisplayPort, DVI, VGA ; RJ45 ; jacks vert sortie, rose micro, bleu clair entrée ligne ; PS/2",
        "périphériques d'entrée, de sortie, d'entrée et de sortie ; pilote : logiciel qui fait dialoguer le système et le matériel, propre au système et à l'architecture 32/64 bits, site du fabricant ou Windows Update, Gestionnaire de périphériques, lspci, lsusb",
        "compatibilité : physique, connecteur et détrompeur, interface électrique, alimentation, firmware/pilote/système ; « ça rentre » n'est pas « compatible » ; ne jamais inventer une caractéristique absente de la fiche",
        "démarche écrite : observer, nommer, rôle, relier, vérifier, noter l'inventaire ; comparer installé et détecté ; précautions : secteur débranché, décharge, bracelet antistatique, sachet, bords, ne jamais forcer, ne jamais ouvrir un bloc",
    ],
    competencies=[
        "Identifier et nommer exactement les composants et connecteurs d'un PC sur un schéma, une photo ou une description, et expliquer leur rôle et leurs liaisons",
        "Interpréter un inventaire (fiche, relevé de commande) et un symptôme simple",
        "Sélectionner une pièce compatible en justifiant chaque critère, et justifier le montage et les précautions ESD",
    ],
    vocabulary=[
        "ATX", "microATX", "Mini-ITX", "socket", "LGA", "PGA", "chipset", "VRM", "EPS", "DIMM",
        "SO-DIMM", "DDR4", "DDR5", "ROM", "UEFI", "POST", "CMOS", "SATA", "M.2", "NVMe", "PCIe",
        "USB-C", "pilote", "ESD",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation techniquement "
        "juste, sans exiger de mot-clé ni de sigle développé si le rôle est clair ; suivre le "
        "barème de la question. Une identification fausse (ROM confondue avec le stockage, DIMM "
        "avec SO-DIMM, EPS avec PCIe, USB-C présenté comme une vitesse) est toujours une erreur. "
        "Ne jamais valider « même socket donc compatible » sans la liste des processeurs et le "
        "firmware, « ça rentre donc c'est compatible », ni une caractéristique inventée absente "
        "de la fiche. Pénaliser une manipulation sous tension, l'absence de précaution "
        "antistatique et un composant forcé."
    ),
)

_PR02_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr02",
    course_title="AMPCR pratique écrite — PR02 Alimentation, connectique, compatibilité et sécurité",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : réponses rédigées de technicien à partir d'étiquettes de bloc, fiches "
        "produits fictives, devis, relevés de mesures et descriptions de montage"
    ),
    allowed_notions=[
        "secteur 230 V alternatif 50 Hz ; le bloc redresse, découpe et régule ; tensions continues +12 V (CPU par EPS et VRM, GPU, ventilateurs, moteurs), +5 V, +3,3 V, −12 V ; +5 VSB présente dès que le bloc est branché, PC éteint ; PS_ON# (vert) met en marche, PWR_OK (gris) signale des tensions stables",
        "tolérances ATX : ±5 % sur +12 V (11,40-12,60 V), +5 V et +5 VSB (4,75-5,25 V), +3,3 V (3,135-3,465 V) ; ±10 % sur −12 V ; testeur à vide ne prouve pas la tenue en charge ; bloc connu bon = test décisif",
        "puissance nominale = maximum fourni en continu, le bloc ne fournit que ce qui est demandé ; +12 V : P = 12 × I ; +3,3 V et +5 V combinés ; mono ou multi-rails ; rendement = fourni / absorbé, absorbée = fournie / rendement, pertes en chaleur ; 80 PLUS (115 V interne) Bronze 82/85/82, Gold 87/90/87, Platinum 90/92/89, Titanium 92/94/90 ; meilleur vers 50 % de charge",
        "connecteurs : ATX 24 (20+4) carte mère ; EPS 8 (4+4) « CPU » et ATX12V 4 broches processeur ; PCIe 6 broches 75 W, 8 broches (6+2) 150 W, emplacement x16 75 W ; 12V-2x6 (12VHPWR) 16 broches jusqu'à 600 W, enfoncé à fond ; SATA 15 broches (+3,3/+5/+12 V) ; Molex 4 broches (+12 V jaune, +5 V rouge) ; câble de données SATA 7 contacts sans alimentation",
        "interdits : EPS ↔ PCIe 8 broches (court-circuit), câbles modulaires d'un autre bloc, adaptateurs Molex/SATA → PCIe pour une carte puissante, forcer un connecteur ; formats de bloc ATX et SFX",
        "budget : somme des puissances maximales des fiches + marge 20-30 % → palier commercial supérieur → jamais sous la recommandation du fabricant de la carte graphique ; vérifier +12 V et connecteurs ; surdimensionnement inutile (prix, rendement)",
        "refroidissement : flux façade/bas → arrière/haut, flèche sur le cadre ; filtres ; CPU_FAN surveillé, SYS_FAN/CHA_FAN, AIO_PUMP ; 3 broches réglé en tension (DC), 4 broches en PWM ; répartiteur limité par le connecteur ; ventilateur de bloc semi-passif arrêté à faible charge = normal",
        "protections du bloc OVP, UVP, OCP, OPP, SCP, OTP (arrêt brutal) ; terre, différentiel, parafoudre (surtensions, pas coupures), onduleur off-line / line-interactive / on-line choisi en watts avec marge et autonomie",
        "sécurité : jamais ouvrir un bloc (condensateurs chargés) ; arrêter, interrupteur sur 0, débrancher, appuyer sur le bouton, bracelet antistatique au châssis, tapis, sachet, tenir par les bords ; batterie lithium-ion gonflée : ne plus charger, ne pas percer ni presser, outils non coupants, bac métallique ou sable, collecte (Bebat) ; outils : tournevis PH1/PH2, testeur, multimètre sur connecteurs, air sec en bloquant les ventilateurs",
        "USB : USB 2.0 480 Mbit/s, 3.2 Gen 1 5 Gbit/s, Gen 2 10 Gbit/s, Gen 2x2 20 Gbit/s, USB4 40 Gbit/s ; USB-C = forme, pas vitesse ; alimentation 2,5 W (USB 2.0), 4,5 W (USB 3), 15 W (USB-C 3 A), PD 100 W et 240 W (EPR) ; concentrateur non alimenté",
        "vidéo : HDMI 1.4 10,2 Gbit/s (4K 30 Hz), 2.0 18 Gbit/s (4K 60 Hz), 2.1 48 Gbit/s (4K 120 Hz) ; câbles High Speed / Premium High Speed / Ultra High Speed ; DisplayPort 1.2 (4K 60), 1.4 (4K 120), 2.1 (80 Gbit/s) ; son transporté ; DP++ vers HDMI passif, HDMI vers DP actif ; écran sur la carte graphique",
        "interne : SATA 6 Gbit/s ≈ 600 Mo/s, données + alimentation ; PCIe taille mécanique et lignes, rétrocompatible ; M.2 longueur (2280), clé (M, B+M, E) et interface NVMe/SATA ; M.2 SATA non détecté dans un emplacement NVMe uniquement ; port SATA désactivé par un M.2 en SATA",
        "compatibilité : DDR3/DDR4/DDR5 non interchangeables, DIMM/SO-DIMM ; AM4 DDR4, AM5 DDR5, LGA1700 DDR4 ou DDR5 selon la carte, LGA1851 DDR5 ; même socket ≠ compatible sans liste des processeurs et firmware ; ATX/microATX/Mini-ITX ; longueur GPU, hauteur ventirad ; « ça rentre » ≠ compatible ; ne rien supposer hors fiche",
        "symptômes : rien du tout, démarre une seconde puis s'arrête (EPS, court-circuit), s'éteint sous charge (bloc insuffisant, adaptateur), redémarrages, odeur de brûlé (débrancher) ; hypothèse ≠ preuve ; remplacement sûr : choisir format/puissance/connecteurs, couper, décharger, ESD, repérer, câbles du nouveau bloc, contrôler tensions et charge, compte rendu",
    ],
    competencies=[
        "Identifier les connecteurs d'alimentation et de données et lire les caractéristiques d'un bloc (puissance, +12 V, rendement)",
        "Calculer un budget de puissance avec marge et déterminer la compatibilité d'une configuration critère par critère",
        "Repérer un mauvais branchement, évaluer des symptômes d'alimentation et rédiger une procédure de remplacement sûre",
    ],
    vocabulary=[
        "AC", "DC", "+5 VSB", "PS_ON#", "PWR_OK", "ATX 24", "EPS", "PCIe 8 broches", "12V-2x6",
        "SATA", "Molex", "rendement", "80 PLUS", "OCP", "onduleur", "ESD", "PWM", "USB-C", "HDMI",
        "DisplayPort", "M.2", "NVMe", "DDR5", "socket",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et toute "
        "démarche techniquement justes, sans exiger de mot-clé ni de sigle développé si le rôle "
        "est clair ; suivre le barème de la question. Un calcul faux (P = U × I, rendement, "
        "tolérance, marge) ou un connecteur mal identifié est toujours une erreur ; un résultat "
        "juste avec une erreur d'arrondi minime reste juste. Ne jamais valider « on peut ouvrir "
        "le bloc », « éteint donc sans tension », « EPS et PCIe 8 broches sont interchangeables », "
        "« USB-C garantit la vitesse », « même socket donc compatible », « le plus gros bloc est "
        "le meilleur choix » ni une mesure à vide présentée comme une preuve. Pénaliser "
        "l'absence de mise hors tension ou de protection antistatique, un adaptateur Molex → "
        "PCIe, des câbles modulaires d'un autre bloc et toute manipulation dangereuse d'une "
        "batterie gonflée."
    ),
)

_PR03_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr03",
    course_title="AMPCR pratique écrite — PR03 Montage et démontage d'un PC — procédure écrite",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : procédures rédigées de technicien, repérage d'erreurs de montage et "
        "justifications à partir de bons de montage, relevés, observations et écrans fictifs"
    ),
    allowed_notions=[
        "préparation : sauvegarde vérifiée ou refus écrit, autorisation signée, état initial (photos, numéro de série, défauts), fiche d'intervention ; arrêt, interrupteur du bloc sur 0, câble secteur débranché (+5 VSB présent PC éteint), appui sur le bouton ; poste dégagé, tapis et bracelet antistatique relié au châssis, sachets, pièces tenues par les bords ; outillage PH1/PH2, bac à vis, photos avant de débrancher",
        "compatibilité vérifiée sur les fiches avant le montage (socket + liste des processeurs + firmware, DDR4/DDR5, format ATX/microATX/Mini-ITX, hauteur du ventirad, longueur de la carte graphique, M.2 NVMe/SATA, bloc) ; ne jamais forcer : ce qui résiste est mal orienté",
        "ordre recommandé : carte mère équipée hors du boîtier sur son carton (processeur, mémoire, M.2, pâte et ventirad) → entretoises et plaque d'E/S → carte mère vissée → bloc et disques → carte graphique → câbles → contrôle visuel → premier démarrage ; la notice peut adapter l'ordre (plaque arrière, AIO, gros ventirad, boîtier compact)",
        "processeur : LGA (broches sur la carte, capot de protection gardé) ou PGA AM4 (broches sous le processeur) ; triangle sur le repère, encoches, pose verticale sans pression ; pâte : petite noisette ou selon la notice, pâte pré-appliquée, film de la semelle retiré, serrage en croix, pâte neuve et nettoyage à l'alcool isopropylique à chaque démontage ; câble sur CPU_FAN, pompe sur AIO_PUMP",
        "mémoire : encoche, enfoncée jusqu'au clic, emplacements du manuel pour le double canal (souvent A2/B2) ; M.2 : entretoise à la longueur (2280), insertion à environ 30°, vis M2 ou loquet",
        "entretoises : une sous chaque trou de la carte, aucune ailleurs (entretoise en trop = court-circuit au dos de la carte, manquante = carte qui fléchit) ; plaque d'E/S avant la carte ; visserie courante : 6-32 (bloc, disques 3,5 pouces, carte mère le plus souvent, parfois M3), M3 (SSD 2,5 pouces), M2 (M.2) ; vis engagée à la main, jamais forcée",
        "câblage : ATX 24, EPS 8 « CPU » (sans lui pas de démarrage ou arrêt immédiat), PCIe/12V-2x6 tous branchés sans adaptateur, SATA données + alimentation ; façade F_PANEL d'après le manuel (disposition Intel : 1 HDD_LED+, 3 HDD_LED−, 2 PLED+, 4 PLED−, 5/7 Reset, 6/8 Power, 9 +5 V, 10 clé) ; LED polarisées (à l'envers : éteinte, sans dégât), boutons non polarisés ; USB 3 interne 19 broches, USB 2 9 broches, HD_AUDIO",
        "contrôle visuel PC débranché avec grille (fixations, aucune vis libre, ventirad, mémoire, carte graphique, alimentation, façade, câbles loin des pales) ; premier démarrage : POST, entraînement de la mémoire (écran noir plusieurs minutes, surtout DDR5 : ne pas couper), LED de diagnostic et bips selon le fabricant ; UEFI comparé au bon de montage (processeur, mémoire totale, disques, température, CPU_FAN, date) ; XMP/EXPO après stabilité",
        "tests : mémoire (MemTest86, Diagnostic de mémoire Windows, plusieurs passes), températures au repos et en charge comparées à la fiche (limite atteinte = baisse de fréquence puis arrêt), état SMART, ports, boutons, stabilité ; compte rendu avec les valeurs",
        "flux d'air avant/bas → arrière/haut, flèche du cadre ; câbles derrière le plateau, attachés, loin des pales",
        "démontage : ordre inverse, photos, étiquettes, vis triées, fiche ; loquet avant de tirer sur le connecteur, jamais sur les fils ; clip PCIe ouvert ; ventirad collé tourné doucement (pâte tiède), jamais arraché (PGA : processeur arraché, broches tordues) ; capot remis sur un socket LGA vide",
        "remplacement : panne et compatibilité confirmées, accord, hors tension, démonter le nécessaire, remonter, pâte neuve si ventirad retiré, tout retester, compte rendu (pièces et numéros de série)",
        "pannes au premier démarrage : montage soupçonné avant les pièces neuves ; rien (secteur, interrupteur, ATX 24, POWER SW), allumage d'une fraction de seconde (EPS, entretoise ou vis en court-circuit), pas d'image (barrette, écran sur la carte mère sans partie graphique, PCIe manquant), disque absent (câbles, M.2 non vissé, port partagé), surchauffe (film, pâte, serrage, CPU_FAN) ; correction PC débranché, un changement à la fois",
    ],
    competencies=[
        "Rédiger et justifier une procédure de préparation, de montage, de démontage ou de remplacement d'un composant",
        "Repérer les erreurs d'un montage décrit (entretoises, façade, câbles, refroidissement, mémoire) et indiquer conséquence et correction",
        "Contrôler un montage et interpréter le premier démarrage (UEFI, températures, tests) avant de rédiger le compte rendu",
    ],
    vocabulary=[
        "ESD", "bracelet antistatique", "entretoise", "plaque d'E/S", "socket", "LGA", "PGA",
        "pâte thermique", "ventirad", "CPU_FAN", "EPS", "F_PANEL", "POST", "UEFI", "XMP", "SMART",
        "M.2", "6-32", "M3",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste est "
        "clair ; suivre le barème de la question. Ne jamais valider « on peut forcer le "
        "processeur ou la barrette », « éteint donc sans tension », « la pâte peut être "
        "réutilisée », « on peut ouvrir le bloc », « tirer sur le ventirad collé », une "
        "entretoise sans trou en face, ni « ça démarre donc c'est validé » sans contrôle. "
        "Pénaliser l'absence de mise hors tension ou de protection antistatique, un démontage "
        "sans sauvegarde ni autorisation, et toute manipulation sous tension."
    ),
)

_PR04_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr04",
    course_title="AMPCR pratique écrite — PR04 Reconditionnement, entretien et contrôles après intervention",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : procédures rédigées de technicien, décisions de protection des données, "
        "lecture de relevés (SMART, batterie, températures) et formulaires à partir de fiches "
        "et de situations fictives"
    ),
    allowed_notions=[
        "quatre opérations : réparation (une panne, même client, données conservées), reconditionnement (PC complet remis en état pour un nouvel utilisateur : diagnostic, nettoyage, pièces, mises à jour, tests, étiquette), remise à zéro (« Réinitialiser ce PC », réinstallation : données supprimées mais pas forcément illisibles), effacement sécurisé (données rendues illisibles par une technique adaptée, vérifiée, certificat)",
        "réception : propriétaire, marque, modèle, numéro de série, étiquette d'inventaire, accessoires, état initial précis et photos datées, mots de passe (tests seulement), demande précise, données et accord écrit, signatures et copie",
        "diagnostic avant intervention : démarrage, UEFI, état SMART, test mémoire, batterie, ports, poussière ; ne pas réinstaller ni nettoyer avant de savoir si le disque est sain",
        "protection des données : seul le propriétaire décide, par écrit (pas un proche ni un vendeur) ; sauvegarde vérifiée (copie relue) ou refus signé avant toute opération risquée ; confidentialité (ne pas ouvrir les fichiers) ; même client : conserver ; PC qui change de main : effacement sécurisé ; recyclage : effacement ou destruction physique avec trace",
        "effacement : formatage rapide, suppression des fichiers ou des partitions et remise à zéro n'effacent pas ; NIST SP 800-88 effacer / purger / détruire ; disque dur : écrasement complet (une passe suffit sur un disque récent) ou ATA Secure Erase ; SSD SATA/NVMe : commande d'effacement sécurisé, Sanitize ou NVMe Format via l'outil du fabricant ou le firmware, effacement cryptographique si chiffré ; passes d'écrasement et défragmentation insuffisantes sur SSD (répartition de l'usure, cellules de réserve) ; support hors d'usage : destruction par filière agréée ; vérification et certificat (support, numéro de série, technique, date, technicien)",
        "nettoyage non destructif : PC débranché (batterie déconnectée si la notice le prévoit), bracelet, local aéré, filtres, pales bloquées, air sec par courtes impulsions bombe droite, pinceau antistatique, alcool isopropylique sur contacts et pâte ; ni aspirateur ménager ni eau ; bloc d'alimentation soufflé par ses grilles, jamais ouvert",
        "refroidissement : poussière et pâte sèche → chaleur → baisse de fréquence puis arrêt ; pâte neuve à chaque démontage ; mesures avant/après avec la même charge ; convention du cours : à surveiller à moins de 10 °C de la limite de la fiche, anormal à la limite",
        "pièces : mesure qui justifie l'échange, compatibilité sur fiche (SATA/NVMe, M.2 2280, DDR4/DDR5, DIMM/SO-DIMM, batterie de référence exacte, pile CR2032), accord, hors tension, test, références et numéros de série des pièces posées et retirées",
        "mises à jour : firmware seulement si utile (sécurité, stabilité, compatibilité), modèle et révision exacts, fichier du fabricant, notes lues, réglages UEFI notés, BitLocker suspendu (sinon clé de récupération demandée) puis repris, alimentation stable, portable sur chargeur, ne jamais couper ; système et pilotes à jour, point de restauration, pilotes du fabricant",
        "tests : RAM (MemTest86, Diagnostic de mémoire Windows), SMART (attributs, pas le résumé PASSED : HDD secteurs en attente ou illisibles > 0 → à remplacer, réalloués > 0 → à surveiller ; NVMe usure ≥ 100 %, erreurs du support ou réserve sous le seuil → à remplacer, usure ≥ 80 % → à surveiller), températures repos/charge, chaque port, 30 minutes de stabilité, rapport de batterie powercfg /batteryreport (capacité à pleine charge / capacité d'origine ; sous 80 % → à remplacer, convention du cours ; batterie gonflée remplacée)",
        "remise : check-list (tests chiffrés, système propre et à jour, données restaurées ou effacement certifié, propreté, accessoires, pièces, conseils, signature), démonstration au client",
        "déchets : DEEE (poubelle barrée, directive 2012/19/UE, Recupel en Belgique : recyparc, point de collecte, reprise en magasin), piles et batteries à part (Bebat), disque effacé ou détruit avant dépôt ; batterie lithium gonflée : ne plus charger, ne jamais percer ni écraser, isoler dans un contenant non inflammable, déposer rapidement",
        "rapport et traçabilité : identification et numéro de série, accord et certificat d'effacement, diagnostic initial, actions, pièces (numéros de série), valeurs des tests, déchets, conclusion signée, étiquette de reconditionnement, registre de l'atelier",
    ],
    competencies=[
        "Distinguer réparation, reconditionnement, remise à zéro et effacement sécurisé, et en déduire accord, sort des données et trace",
        "Décider du sort des données d'un PC confié et choisir une technique d'effacement adaptée au support (HDD, SSD SATA, SSD NVMe)",
        "Rédiger les procédures de reconditionnement, de nettoyage et de mise à jour, interpréter les contrôles après intervention et rédiger check-list et rapport",
    ],
    vocabulary=[
        "reconditionnement", "remise à zéro", "effacement sécurisé", "Sanitize", "effacement cryptographique",
        "certificat d'effacement", "SMART", "BitLocker", "UEFI", "pâte thermique", "DEEE", "Recupel", "Bebat",
        "numéro de série", "traçabilité",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste ou la "
        "décision est clair ; suivre le barème de la question. Ne jamais valider « le formatage "
        "rapide efface les données », « une remise à zéro suffit avant revente », « plusieurs "
        "passes d'écrasement effacent un SSD », « défragmenter efface », « PASSED donc disque "
        "sain », un effacement sur la demande d'un tiers ou sans accord écrit du propriétaire, "
        "une réinstallation sans sauvegarde vérifiée ni refus signé, l'ouverture d'un bloc "
        "d'alimentation, l'aspirateur dans le boîtier, une mise à jour du firmware sur batterie "
        "faible ou interrompue, ni une batterie percée ou jetée à la poubelle. Pénaliser "
        "l'absence de mise hors tension ou de protection antistatique et un rapport sans valeurs."
    ),
)

_PR05_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr05",
    course_title="AMPCR pratique écrite — PR05 Stockage, partitions, formatage et défragmentation",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : choix justifiés (support, table de partitions, système de fichiers, "
        "entretien), plans de partitions chiffrés, procédures non destructives rédigées et "
        "lecture de captures et de relevés fictifs"
    ),
    allowed_notions=[
        "disque dur (plateaux, têtes, 5 400/7 200 tr/min, 100 à 250 Mo/s, temps d'accès de plusieurs ms, sensible aux chocs, grande capacité à bas prix) ; SSD SATA (flash NAND, environ 550 Mo/s, limite de l'interface SATA 6 Gbit/s) ; SSD NVMe (PCI Express, environ 3 500 Mo/s en PCIe 3.0 x4, 7 000 Mo/s en PCIe 4.0 x4) ; système sur SSD, données volumineuses et sauvegardes sur disque dur",
        "interfaces : SATA (câble de données 7 broches, alimentation 15 broches, 2,5 ou 3,5 pouces) ; M.2 est un format (2280 = 22 × 80 mm) qui parle SATA ou NVMe ; l'emplacement M.2 peut n'accepter que SATA ou que NVMe et peut désactiver des ports SATA : la notice fait foi",
        "secteur 512 ou 4 096 octets ; cluster (unité d'allocation) 4 Kio par défaut en NTFS et ext4, un fichier occupe des clusters entiers ; SSD : écriture par pages, effacement par blocs, cycles d'écriture limités, endurance en TBW, répartition de l'usure (wear leveling) par le contrôleur, cellules de réserve, TRIM",
        "unités : 1 Go = 10^9 octets (fabricant), 1 Gio = 2^30 = 1 073 741 824 octets ; Windows affiche des Gio écrits « Go » ; 1 To ≈ 931,32 Gio, 500 Go ≈ 465,66 Gio, 2 To ≈ 1 862,65 Gio ; Gestion des disques demande des Mo qui sont des Mio (300 Gio = 307 200)",
        "MBR : 4 partitions principales ou 3 + 1 étendue, 2 Tio au plus (2^32 × 512 octets), démarrage BIOS hérité ; GPT : 128 partitions sous Windows, table de secours en fin de disque, démarrage UEFI, obligatoire pour Windows 11 ; Windows lit un disque de données GPT même sur un ancien PC ; conversion avec Gestion des disques ou diskpart sur disque vide (mbr2gpt pour un disque système)",
        "démarrage : UEFI + GPT → partition EFI (ESP, FAT32) contenant le chargeur ; BIOS + MBR → partition active ; le mode du firmware doit correspondre à la table (mode hérité/CSM sur un Windows GPT → « No bootable device ») ; plans : Windows UEFI = EFI 100 Mo FAT32, MSR 16 Mo, C: NTFS, récupération ≈ 750 Mo ; Windows BIOS = Réservé au système ≈ 500 Mo NTFS active + C: ; Linux UEFI = ESP 512 Mo /boot/efi, / ext4, swap (ou fichier d'échange)",
        "partition, volume (partition formatée avec lettre ou point de montage), initialiser = écrire une table vide ; formatage logique = système de fichiers vide ; rapide (structures seulement) ou complet (zéros et recherche des secteurs défectueux) ; formatage de bas niveau fait en usine ; formater n'efface pas de façon sûre (effacement sécurisé : PR04)",
        "NTFS (Windows, journal, droits, grands fichiers, macOS en lecture seule) ; FAT32 (fichier de 4 Gio moins 1 octet au plus, ESP, appareils anciens, l'outil graphique de Windows ne le propose que jusqu'à 32 Go) ; exFAT (échange Windows/macOS/Linux, grands fichiers, pas de journal ni de droits) ; ext4 (Linux, journal, droits, non lu par Windows sans outil)",
        "Windows : Gestion des disques (initialiser, nouveau volume simple, étendre si l'espace non alloué suit immédiatement, réduire, modifier la lettre, supprimer) ; diskpart (list disk, select disk, detail disk, convert gpt, create partition primary, format fs=ntfs quick, assign letter ; clean efface la table de tout le disque sélectionné)",
        "Linux : /dev/sdX, /dev/nvme0n1pN, lsblk -f, parted mklabel gpt, mkpart, mkfs.ext4 -L, mount, blkid, /etc/fstab par UUID (UUID=… point ext4 defaults 0 2), mount -a, df -h ; fdisk, gdisk et GParted équivalents",
        "avant toute opération : identifier le disque, lire SMART, sauvegarde sur un autre support (jamais le même disque), copie vérifiée, accord écrit, relevé de l'état, une opération à la fois, contrôle ; disque avec données non initialisé ou RAW : ne pas initialiser ni formater, récupérer d'abord (image si le disque faiblit)",
        "SMART : lire les attributs, pas le résumé PASSED ; secteurs en attente ou illisibles > 0 → à remplacer ; réalloués seuls → à surveiller (suivre l'évolution) ; UDMA_CRC_Error_Count > 0 → câble ou connecteur SATA ; NVMe usure ≥ 80 % surveiller, ≥ 100 % remplacer ; un bon relevé ne garantit pas l'absence de panne, la sauvegarde reste indispensable ; seuils = conventions du cours",
        "entretien : disque dur → défragmentation (optimisation planifiée de Windows, manuelle au-delà de 10 % fragmenté, convention du cours ; espace libre nécessaire ; jamais sur un disque qui a des secteurs en attente) ; SSD → TRIM (« découpage » dans Optimiser les lecteurs, fstrim.timer sous Linux), jamais de défragmentation ; ext4 se défragmente rarement",
        "symptômes : absent de l'UEFI → câbles, port, M.2 incompatible, disque mort ; non initialisé (neuf : initialiser ; avec données : récupérer) ; sans lettre → attribuer une lettre ; RAW → refuser le formatage, récupérer ; C: plein → mesurer (Stockage), corbeille, Nettoyage de disque, déplacer les données, jamais supprimer dans C:\\Windows ; démarrage impossible → détection, ordre de démarrage, mode UEFI/hérité, mode SATA (INACCESSIBLE_BOOT_DEVICE), réparation en PR11",
    ],
    competencies=[
        "Choisir et justifier un support, une table de partitions et un système de fichiers selon l'usage et la compatibilité du PC",
        "Établir un plan de partitions chiffré (Go/Gio) et rédiger les procédures Windows et Linux de création, formatage et montage",
        "Travailler de façon non destructive : sauvegarde vérifiée, lecture prudente de SMART, entretien adapté (défragmentation ou TRIM), diagnostic d'un disque absent, non initialisé, RAW, plein ou d'un démarrage impossible",
    ],
    vocabulary=[
        "HDD", "SSD", "NVMe", "M.2", "SATA", "secteur", "cluster", "TRIM", "wear leveling", "TBW", "Gio",
        "MBR", "GPT", "ESP", "UEFI", "NTFS", "FAT32", "exFAT", "ext4", "volume", "SMART", "défragmentation",
        "fstab", "UUID", "RAW",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le choix ou le "
        "geste est clair ; accepter les arrondis raisonnables des calculs Go/Gio ; suivre le "
        "barème de la question. Ne jamais valider « le formatage rapide efface les données », "
        "« défragmenter un SSD », FAT32 pour un fichier de plus de 4 Gio, MBR pour un disque de "
        "plus de 2 To ou le disque système d'un PC UEFI, l'initialisation ou le formatage d'un "
        "disque qui contenait des données avant récupération, une sauvegarde sur le même disque, "
        "« PASSED donc disque sain », la suppression de la partition EFI ou de fichiers de "
        "C:\\Windows, ni une commande diskpart clean ou parted sans identification du disque. "
        "Pénaliser l'absence de sauvegarde vérifiée avant une opération sur les partitions."
    ),
)

# Ticket #230 : EX01, examen blanc du module 1 (PR01 → PR06) — notions de ces six cours.
_EX01_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-ex01",
    course_title="AMPCR pratique écrite — EX01 Examen blanc écrit : maintenance et dépannage matériel",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : examen blanc /100 du module matériel, réponses rédigées de technicien à "
        "partir de dossiers fictifs (fiches, manuels, relevés, captures, schémas)"
    ),
    allowed_notions=[
        "identification sur plan : socket, VRM, emplacements DIMM, EPS 8 broches, ATX 24 broches, CPU_FAN, PCIe x16, M.2, SATA, chipset, pile CMOS, connecteurs de façade et USB internes ; liaisons processeur ou chipset vérifiées dans le manuel",
        "sécurité : éteint n'est pas hors tension (+5 VSB), interrupteur sur 0, câble débranché, bouton appuyé ; ESD : bracelet relié au châssis, tapis, sachets, pièces tenues par les bords, ni laine ni bijou ; bloc et batterie jamais ouverts",
        "outillage : PH1/PH2, bac à vis, étiquettes, lampe, pince, air sec en bombe tenue droite par impulsions, pinceau, alcool isopropylique, pâte thermique ; ni visseuse, ni aspirateur ménager, ni eau, ni lame",
        "POST : LED de diagnostic CPU, DRAM, VGA, BOOT dont le sens dépend du fabricant (manuel) ; ventilateurs qui tournent ne prouvent pas un démarrage ; premier démarrage après modification de la mémoire long (entraînement) ; barrettes mélangées à la vitesse de la plus lente ; kit identique et liste de compatibilité",
        "diagnostic : du plus simple au plus invasif, un changement à la fois, configuration minimale, test croisé, test mémoire ; pas de flash du firmware ni de réinstallation à l'aveugle",
        "compatibilité : socket, génération DDR (encoche DDR4/DDR5), capacité maximale, nombre d'emplacements, longueur et épaisseur de la carte graphique, connecteurs PCIe 8 broches, pas d'adaptateur Molex ou SATA vers PCIe",
        "bloc : total des fiches + 30 % de marge, palier de 50 W supérieur, jamais sous la recommandation du fabricant de la carte graphique",
        "montage et démontage : photos et étiquettes, ordre, bloc ventilateur vers le filtre, EPS jamais remplacé par un PCIe, carte graphique dans le premier PCIe x16, clip, équerre, barrettes selon le manuel, contrôle visuel, premier démarrage",
        "refroidissement : température comparée au maximum de la fiche, « à surveiller » à moins de 10 °C de ce maximum, throttling, arrêt de protection, ventilateur sur CPU_FAN en profil automatique, poussière, pâte thermique ; preuve par un test de charge d'au moins 30 minutes",
        "stockage : port SATA partagé avec un emplacement M.2 (manuel), disque absent du firmware = cause matérielle, câble de données et alimentation, disque neuf « Non initialisé » → GPT, volume NTFS, lettre ; jamais initialiser un disque qui contient des données",
        "SMART : secteurs en attente ou illisibles > 0 → remplacer, réalloués seuls → surveiller, CRC → câble ; « PASSED » ne garantit rien ; copie ou image d'abord vers un autre support, vérifiée ; ni chkdsk /r ni défragmentation avant ; sauvegarde 3-2-1 ; confidentialité et accord écrit",
        "vérification et compte rendu : contrôles prouvés (mémoire reconnue, test, démarrages, applications, températures), demande, constat, cause, actions, vérifications, résultat, recommandations",
    ],
    competencies=[
        "Interpréter les documents d'un dossier d'intervention matériel (fiche, manuel, relevés, captures, schéma)",
        "Rédiger une procédure de diagnostic, de montage ou de protection des données ordonnée, sûre et justifiée",
        "Vérifier une compatibilité, calculer un bloc d'alimentation et rédiger un compte rendu professionnel",
    ],
    vocabulary=[
        "POST", "UEFI", "LED de diagnostic", "DDR5", "EPS", "ATX 24 broches", "PCIe x16", "M.2", "SATA",
        "CPU_FAN", "throttling", "+5 VSB", "ESD", "SMART", "GPT", "NTFS", "pâte thermique",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien dans un examen blanc /100 (10 points par "
        "question) : accepter toute formulation techniquement juste, sans exiger de mot-clé ; "
        "suivre le barème de la question et noter en proportion. Pénaliser une manipulation sous "
        "tension, l'ouverture d'un bloc d'alimentation, un adaptateur Molex ou SATA vers PCIe, "
        "l'initialisation ou le formatage d'un disque contenant des données, un chkdsk /r ou une "
        "défragmentation avant copie, et toute conclusion catégorique non justifiée par un test. "
        "Une valeur calculée fausse (puissance du bloc, mémoire totale) est une erreur même bien "
        "rédigée ; un arrondi raisonnable est accepté."
    ),
)

_PR07_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr07",
    course_title="AMPCR pratique écrite — PR07 Systèmes d'exploitation, GUI/CLI et prérequis d'installation",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : choix justifiés d'un système et d'une édition, vérification des prérequis "
        "matériels et du firmware, lecture de relevés fictifs (Informations système, terminal, "
        "menu de démarrage) et plans d'installation rédigés"
    ),
    allowed_notions=[
        "rôle d'un système d'exploitation : noyau (temps processeur, mémoire protégée, accès au matériel), pilotes (un par matériel), système de fichiers (emplacement et droits), comptes et droits, services (arrière-plan : spouleur, mises à jour, systemd), interface graphique (GUI) ou ligne de commande (CLI) ; application → noyau → pilote → matériel",
        "systèmes du marché : Windows (propriétaire, OEM, fin de support publiée, Windows 10 plus pris en charge depuis le 14 octobre 2025 sauf mises à jour étendues payantes), distributions Linux libres (Ubuntu, Debian, Linux Mint, Fedora ; LTS ; GNOME, KDE Plasma, Xfce ; apt, dnf ; serveur sans interface graphique), macOS (Mac uniquement), ChromeOS et ChromeOS Flex ; choix : logiciels indispensables, domaine, matériel, durée de support",
        "éditions : Windows 11 Famille (usage courant, Defender, client Bureau à distance) ; Professionnel nécessaire pour jonction à un domaine Active Directory, BitLocker et sa console, hôte Bureau à distance, Hyper-V, gpedit.msc ; l'édition installée doit correspondre à la licence",
        "GUI et CLI : msinfo32, Gestion des disques, Gestionnaire de périphériques, services.msc, tpm.msc ; systeminfo, ipconfig /all, Get-ComputerInfo, Get-Tpm, Confirm-SecureBootUEFI, Get-FileHash ; cat /etc/os-release, uname -m, uname -r, nproc, free -h, lsblk, ip a, systemctl status, mokutil --sb-state, sha256sum, sudo, SSH ; CLI = exacte, reproductible, scriptable, à distance",
        "architecture : x64 (x86_64) ou ARM64 (aarch64) ; un système 32 bits adresse 4 Gio au plus (environ 3,2 à 3,5 Gio utilisables) ; Windows 11 uniquement 64 bits ; pas de mise à niveau de 32 à 64 bits",
        "firmware : UEFI + GPT + ESP ou mode hérité (CSM) + MBR ; démarrage sécurisé seulement en UEFI (« Non pris en charge » en mode hérité) ; TPM 2.0 (puce, Intel PTT, AMD fTPM, parfois désactivé) ; mbr2gpt /validate puis /convert /allowFullOS avant de basculer le firmware en UEFI ; shim signé : Ubuntu, Debian, Fedora, Mint démarrent avec le démarrage sécurisé ; pilote NVIDIA propriétaire → enregistrement d'une clé MOK ; clé de récupération BitLocker avant de toucher au firmware",
        "prérequis Windows 11 publiés (octobre 2026) : processeur 64 bits de la liste de compatibilité, 2 cœurs, 1 GHz, 4 Go, 64 Go, UEFI compatible démarrage sécurisé, TPM 2.0, DirectX 12 / WDDM 2.0, écran 9 pouces 720p, Internet et compte Microsoft pour Famille ; verdicts : compatible tel quel, après réglages du firmware (mode UEFI, TPM à activer), non compatible (processeur hors liste, TPM 1.2, mémoire ou stockage insuffisants) ; démarrage sécurisé désactivé mais pris en charge = recommandation, pas blocage ; pas de contournement d'un blocage matériel ; Ubuntu Desktop recommandé : 2 GHz double cœur, 4 Go, 25 Go",
        "avant l'installation : accord écrit, sauvegarde vérifiée sur un autre support, édition et licence relevées, logiciels et leurs clés, clé BitLocker ; licences OEM (liée au premier PC, non transférable, réactivation automatique de la même édition), commerciale (transférable si retirée de l'ancien PC), volume (organisation), Linux libre",
        "installation propre ou mise à niveau sur place : mise à niveau seulement si prérequis respectés, même famille et architecture, système sain, programmes à garder ; sinon installation propre (32 → 64 bits, passage à Linux, système infecté, disque neuf) ; prérequis non respectés → autre système ou matériel",
        "média : image ISO officielle, somme SHA-256 identique à celle publiée, clé USB d'au moins 8 Go effacée, outil de création, Rufus (GPT pour UEFI), balenaEtcher, dd ; FAT32 limite 4 Gio par fichier ; menu de démarrage ponctuel (F12, F11, F8, Échap selon le fabricant), entrée « UEFI: » de la clé ; entrée sans UEFI → mode hérité → l'installateur refuse un disque GPT",
        "partitions et pilotes : disposition standard créée par l'installateur (ESP, MSR, récupération ; ESP, racine, swap), partition de données séparée, double démarrage (Windows d'abord) ; pilote de stockage Intel VMD/RST « F6 » via « Charger un pilote » quand l'installateur ne voit aucun lecteur ; pilotes réseau sur clé ; chipset et graphique après ; Linux : pilotes dans le noyau, firmware, Pilotes additionnels",
        "sécurité initiale : un compte par personne, administrateur protégé par mot de passe, compte standard au quotidien, UAC, sudo, comptes du domaine en entreprise ; mises à jour, Microsoft Defender, pare-feu (ufw à activer sous Ubuntu), chiffrement (BitLocker, chiffrement de l'appareil, chiffrement de l'installateur Linux) et clé de récupération hors du PC",
        "virtualisation : hyperviseur type 2 (VirtualBox, VMware Workstation, sur un système hôte) ou type 1 (Hyper-V, Proxmox VE/KVM, ESXi) ; VT-x ou AMD-V à activer dans le firmware ; mémoire de l'hôte = totale − VM en marche, au moins 4 Go laissés à l'hôte (convention du cours) ; VM Windows 11 : EFI, démarrage sécurisé, TPM virtuel 2.0 ; instantané ≠ sauvegarde",
    ],
    competencies=[
        "Choisir et justifier un système d'exploitation et son édition selon les logiciels, l'environnement, le matériel et la durée de support",
        "Vérifier les prérequis matériels et du firmware à partir de relevés GUI ou CLI et conclure : compatible, après réglages ou non compatible",
        "Rédiger un plan d'installation sûr : sauvegarde, licences, démarche propre ou mise à niveau, média contrôlé, démarrage UEFI, pilotes, comptes et sécurité initiale",
    ],
    vocabulary=[
        "noyau", "pilote", "service", "GUI", "CLI", "PowerShell", "bash", "sudo", "distribution", "LTS",
        "édition", "OEM", "x64", "UEFI", "CSM", "Secure Boot", "TPM", "mbr2gpt", "ESP", "GPT", "SHA-256",
        "ISO", "MOK", "VMD", "hyperviseur", "VT-x",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le choix ou le "
        "geste est clair ; accepter d'autres distributions ou outils équivalents bien justifiés ; "
        "suivre le barème de la question. Ne jamais valider une installation sans sauvegarde "
        "vérifiée, l'édition Famille pour un domaine ou BitLocker, une mise à niveau de 32 à 64 "
        "bits ou d'un système infecté, la bascule du firmware en UEFI avant la conversion "
        "mbr2gpt, la désactivation du démarrage sécurisé ou du TPM « par sécurité », le "
        "contournement d'un blocage matériel de Windows 11, une image non officielle ou dont la "
        "somme ne correspond pas, ni un compte administrateur partagé sans mot de passe."
    ),
)

PRACTICAL_COURSES: tuple[PracticalCourse, ...] = (
    PracticalCourse(
        code="PR01",
        title="Structure d'un PC et identification des composants",
        items=PR01_ITEMS,
        context=_PR01_CONTEXT,
    ),
    PracticalCourse(
        code="PR02",
        title="Alimentation, connectique, compatibilité et sécurité",
        items=PR02_ITEMS,
        context=_PR02_CONTEXT,
    ),
    PracticalCourse(
        code="PR03",
        title="Montage et démontage d'un PC — procédure écrite",
        items=PR03_ITEMS,
        context=_PR03_CONTEXT,
    ),
    PracticalCourse(
        code="PR04",
        title="Reconditionnement, entretien et contrôles après intervention",
        items=PR04_ITEMS,
        context=_PR04_CONTEXT,
    ),
    PracticalCourse(
        code="PR05",
        title="Stockage, partitions, formatage et défragmentation",
        items=PR05_ITEMS,
        context=_PR05_CONTEXT,
    ),
    PracticalCourse(
        code="PR06", title="Diagnostic des pannes matérielles", items=PR06_ITEMS, context=_PR06_CONTEXT
    ),
    PracticalCourse(
        code="PR07",
        title="Systèmes d'exploitation, GUI/CLI et prérequis d'installation",
        items=PR07_ITEMS,
        context=_PR07_CONTEXT,
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
    PracticalCourse(
        code="EX01",
        title="Examen blanc écrit — maintenance et dépannage matériel",
        items=EX01_ITEMS,
        context=_EX01_CONTEXT,
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


def is_practical_exam_code(uaa_code: str | None) -> bool:
    """Examen blanc EX01-EX06 (ticket #230) : une réserve `exam` seule, pas d'entraînement."""
    return is_practical_code(uaa_code) and (uaa_code or "").startswith("EX")


def is_practical_exam_slug(uaa_slug: str) -> bool:
    course = PRACTICAL_COURSES_BY_SLUG.get(uaa_slug)
    return course is not None and is_practical_exam_code(course.code)


def _document_layout(document: ExerciseDocument) -> dict | None:
    if document.image:
        # Ticket #230 : schéma (fichier SVG statique) affiché dans la question, avec sa
        # description textuelle complète en dessous (lisible sans voir l'image).
        return {
            "kind": "figure",
            "src": f"/static/{document.image}",
            "alt": " ".join(document.content_text.splitlines()),
            "lines": document.content_text.splitlines(),
            "notice": "Schéma fictif reconstitué pour l'exercice (non officiel).",
        }
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

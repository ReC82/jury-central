"""Banque des cours du parcours « AMPCR — Pratique écrite » (ticket #193 : PR06 ; #194 : PR11 ;
#197 : PR15 ; #198 : PR16 ; #199 : PR20 ; #200 : PR24 ; #202 : PR01 ; #203 : PR02 ; #204 : PR03 ;
#205 : PR04 ; #206 : PR05 ; #207 : PR07 ; #208 : PR08 ; #209 : PR09 ; #214 : PR10 ; #215 : PR12 ; #216 : PR13 ; #217 : PR14 ; #218 : PR17 ; #219 : PR18 ; #220 : PR19) et examens blancs de module (#230 : EX01 ; #231 : EX02 ; #232 : EX03 ; réserve `exam` seule).

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
from app.v1.ampcr_pratique_ex02_bank import ALL_ITEMS as EX02_ITEMS
from app.v1.ampcr_pratique_ex03_bank import ALL_ITEMS as EX03_ITEMS
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
from app.v1.ampcr_pratique_pr08_bank import ALL_ITEMS as PR08_ITEMS
from app.v1.ampcr_pratique_pr09_bank import ALL_ITEMS as PR09_ITEMS
from app.v1.ampcr_pratique_pr10_bank import ALL_ITEMS as PR10_ITEMS
from app.v1.ampcr_pratique_pr11_bank import ALL_ITEMS as PR11_ITEMS
from app.v1.ampcr_pratique_pr12_bank import ALL_ITEMS as PR12_ITEMS
from app.v1.ampcr_pratique_pr13_bank import ALL_ITEMS as PR13_ITEMS
from app.v1.ampcr_pratique_pr14_bank import ALL_ITEMS as PR14_ITEMS
from app.v1.ampcr_pratique_pr15_bank import ALL_ITEMS as PR15_ITEMS
from app.v1.ampcr_pratique_pr16_bank import ALL_ITEMS as PR16_ITEMS
from app.v1.ampcr_pratique_pr17_bank import ALL_ITEMS as PR17_ITEMS
from app.v1.ampcr_pratique_pr18_bank import ALL_ITEMS as PR18_ITEMS
from app.v1.ampcr_pratique_pr19_bank import ALL_ITEMS as PR19_ITEMS
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

# Ticket #231 : EX02, examen blanc du module 2 (PR07 → PR12) — notions de ces six cours.
_EX02_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-ex02",
    course_title="AMPCR pratique écrite — EX02 Examen blanc écrit : installation et dépannage des systèmes",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : examen blanc /100 du module systèmes d'exploitation, réponses rédigées de "
        "technicien à partir de dossiers fictifs (relevés, écrans d'installation, captures de WinRE "
        "et du terminal Linux, plans de partitions, journaux)"
    ),
    allowed_notions=[
        "choix d'un système : Windows 11 (prérequis : processeur 64 bits de la liste de compatibilité, 4 Go, 64 Go, firmware UEFI compatible démarrage sécurisé, TPM 2.0), Windows 10 plus pris en charge depuis le 14 octobre 2025, distributions Linux à support long (Ubuntu LTS, Linux Mint, Debian), ChromeOS Flex ; Famille ou Professionnel (BitLocker et sa console, hôte Bureau à distance, jonction à un domaine, Hyper-V, gpedit : Professionnel)",
        "réglages avant Windows 11 : sauvegarde, mbr2gpt /validate puis /convert AVANT de passer le firmware en UEFI (CSM désactivé), activer le TPM (PTT, fTPM), démarrage sécurisé recommandé ; vérification msinfo32 (Mode BIOS, état du démarrage sécurisé), tpm.msc, Confirm-SecureBootUEFI, Get-Tpm",
        "outils graphiques et commandes : Gestion des disques, diskpart, Get-Disk, lsblk -f, df -h ; Gestionnaire de périphériques, pnputil, Get-PnpDevice, lspci -k, lsusb ; ipconfig /all, ip a, ip route ; services.msc, sc query, Get-Service, systemctl status, sudo systemctl enable --now",
        "installation propre de Windows : copie vérifiée du profil, même édition que la licence (licence numérique liée au PC), pilotes réseau sur clé, clé officielle, autres disques débranchés ou intouchés, sélection de l'espace non alloué du disque cible ; partitions créées : ESP FAT32 (≈ 100 Mo), MSR 16 Mo, C: NTFS, récupération NTFS ; UEFI ↔ GPT ; tailles affichées en Gio (1 To ≈ 931,5 Go)",
        "pilotes : ID du matériel (PCI VEN_10EC Realtek, VEN_10DE NVIDIA, VEN_8086 Intel ; USB VID_04F9 Brother), Code 28 = pas de pilote, carte graphique de base Microsoft = pilote générique ; réseau d'abord (pilote copié depuis un autre PC), Windows Update, site du fabricant, point de restauration ; jamais de site « tous pilotes »",
        "comptes : groupe de travail sans serveur (comptes locaux par poste), domaine Active Directory avec un contrôleur ; un compte par personne, standard par défaut (Utilisateurs), administrateur nominatif (Administrateurs), moindre privilège ; net user nom * /add, net localgroup Administrateurs nom /add, net user nom /active:no",
        "double démarrage : copie vérifiée et accord écrit, clé BitLocker relevée, démarrage rapide désactivé, réduction de C: depuis Windows, image contrôlée par sha256sum, entrée UEFI, démarrage sécurisé actif ; ESP réutilisée sans formatage (/boot/efi), partitions Windows intouchées, / ext4 (25 Go au moins), swap (repère : 1 × la mémoire jusqu'à 8 Go sans hibernation, 2 × avec), /home facultatif ; GRUB, efibootmgr",
        "mode d'urgence systemd : délai dépassé sur un périphérique de /etc/fstab, local-fs.target en échec ; noms /dev/sdX qui changent quand on ajoute un disque ; copie de fstab, ligne par UUID (blkid, lsblk -f), option nofail, findmnt --verify, systemctl daemon-reload, mount -a ; jamais formater un disque ni supprimer la ligne sans comprendre",
        "permissions Linux : propriétaire, groupe, autres (première classe qui correspond), r w x, notation octale (770, 640, 660) ; x nécessaire pour entrer dans un dossier ; sudo réservé au groupe sudo ; sudo usermod -aG groupe nom puis reconnexion, chmod g+w ; jamais chmod -R 777 ni sudo pour tous",
        "erreurs de démarrage Windows : écran d'arrêt (code d'arrêt, fichier en cause), réparation automatique après deux échecs, WinRE (outil de redémarrage système, paramètres et mode sans échec, invite de commandes, désinstaller des mises à jour, restauration du système, paramètres UEFI) ; restaurer le pilote en mode sans échec, puis point de restauration",
        "restauration : échelle du moins au plus invasif (annuler le dernier changement, sfc/DISM, restauration du système, réinstaller via Windows Update, réinitialiser en conservant les fichiers, réinstallation complète) avec leurs effets et précautions ; sauvegarde vérifiée par empreinte SHA-256 (Get-FileHash, certutil -hashfile, sha256sum) ; accord écrit avant une réinitialisation",
    ],
    competencies=[
        "Choisir et préparer l'installation d'un système (édition, prérequis, firmware, partitions) et la vérifier",
        "Interpréter un écran d'erreur, une capture de WinRE ou du terminal Linux et rédiger une réparation ordonnée, sûre et justifiée",
        "Organiser comptes, groupes et permissions selon le moindre privilège, et protéger les données du client avant toute restauration",
    ],
    vocabulary=[
        "UEFI", "GPT", "MBR", "ESP", "MSR", "TPM 2.0", "démarrage sécurisé", "WinRE", "mode sans échec",
        "point de restauration", "BitLocker", "GRUB", "fstab", "UUID", "systemd", "sudo", "chmod", "SHA-256",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien dans un examen blanc /100 (10 points par "
        "question) : accepter toute formulation, toute commande et tout ordre techniquement justes, "
        "sans exiger de mot-clé ni de libellé exact d'écran ; suivre le barème de la question et noter "
        "en proportion. Pénaliser la suppression ou le formatage d'une partition ou d'un disque qui "
        "n'est pas la cible ou sans sauvegarde vérifiée et accord écrit, le formatage de l'ESP, une "
        "réinitialisation ou une réinstallation proposée avant les gestes moins invasifs, la "
        "désactivation du démarrage sécurisé pour contourner un problème, un activateur ou une clé "
        "trouvée sur Internet, un site « tous pilotes », chmod 777, sudo pour tous ou un compte "
        "partagé, et une ligne fstab par /dev/sdX."
    ),
)

# Ticket #232 : EX03, examen blanc du module 3 (PR13 → PR17) — notions de ces cinq cours.
_EX03_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-ex03",
    course_title="AMPCR pratique écrite — EX03 Examen blanc écrit : câblage RJ45, BNC et fibre",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : examen blanc /100 du module câblage, réponses rédigées de technicien à partir "
        "de dossiers fictifs (fiche RJ45, rapport et affichage de testeur, relevé de pose, bus "
        "coaxial, mesures à l'ohmmètre et au photomètre, catalogue, trace de réflectomètre)"
    ),
    allowed_notions=[
        "brochages TIA/EIA-568 lus fiche vue côté contacts, languette dessous, broche 1 à gauche : T568A = blanc/vert, vert, blanc/orange, bleu, blanc/bleu, orange, blanc/marron, marron ; T568B = blanc/orange, orange, blanc/vert, bleu, blanc/bleu, vert, blanc/marron, marron ; paires sur 1-2, 3-6, 4-5, 7-8",
        "cordon droit (même norme aux deux bouts) ou croisé (A d'un côté, B de l'autre : 1→3, 2→6, 3→1, 6→2) ; MDI (carte : émet 1-2, reçoit 3-6 en 10/100) et MDI-X (switch) ; Auto MDI-X : un droit suffit ; 1 Gb/s utilise les 4 paires dans les deux sens",
        "testeur de câble (wiremap) : conforme, circuit ouvert, paire inversée, paires croisées, court-circuit, paires séparées (continuité correcte mais diaphonie NEXT en échec) ; un câble qui échoue au test ne se livre pas ; mélange T568A/T568B entre prise et panneau",
        "fabrication d'un cordon RJ45 : câble multibrin, fiches adaptées, 25 à 30 mm de gaine retirée, détorsadage minimal (≤ 13 mm), recoupe à 12-13 mm, fils en butée, gaine sous la patte, sertissage, test, étiquetage",
        "choix du câble : catégorie selon le débit (Cat5e 1 Gb/s, Cat6A 10 Gb/s sur 100 m ; Cat6 à 10 Gb/s ≤ 55 m après certification), blindage selon les perturbations et la mise à la terre (U/UTP, F/UTP, S/FTP ; lettre avant la barre = écran global, après = écran par paire), coaxial 75 Ω RG-59 et BNC 75 Ω pour la vidéo analogique, fibre au-delà de 100 m ou entre bâtiments",
        "pose : rayon de courbure ≥ 4 × diamètre (non écranté), 8 × (écranté), 10 × (coaxial sans fiche du fabricant) ; traction ≤ 110 N ; séparation EN 50174-2 selon la classe (a 300, b 100, c 50, d 10 mm) sauf cloison métallique ; lien permanent ≤ 90 m, cordons ≤ 10 m, canal ≤ 100 m",
        "10BASE2 : RG-58 50 Ω, 185 m, 30 stations, T BNC directement sur la carte, 0,5 m entre T, terminateur 50 Ω à chaque bout, terre en un seul point ; réflexion Γ = (Z − Z0)/(Z + Z0) ; ohmmètre au T réseau arrêté : 25 Ω normal, 50 Ω un seul terminateur vu, 0 Ω court-circuit, infini aucun terminateur",
        "câble BNC à sertir : câble et connecteur de même impédance, manchon et bague enfilés, dénudeur coaxial aux cotes de la notice, contact central serti, corps poussé sans brin vers l'âme, bague sertie, contrôles (traction, continuité, pas de court-circuit) ; 10BASE5 : coaxial épais 50 Ω, 500 m, 100 transceivers, prises vampires tous les 2,5 m, câble AUI ≤ 50 m, connecteurs N",
        "fibre : multimode OM1-OM4 (850/1 300 nm) et monomode OS2 (1 310/1 550 nm, gaine jaune) ; connecteurs LC (SFP), SC ; UPC (bleu) et APC (vert, 8°) non mélangeables ; modules 1000BASE-SX (OM2 550 m), 10GBASE-SR (OM2 82 m, OM3 300 m, OM4 400 m), 10GBASE-LR (OS2 10 km) ; mêmes modules aux deux bouts ; jamais de cuivre entre deux bâtiments",
        "bilan optique : fibre (km × dB/km : OS2 0,4 dB/km) + 0,75 dB par paire de connecteurs + 0,3 dB par épissure ; photométrie : perte = référence − lecture ; puissance reçue = émise − perte, comparée à la plage de la fiche ; inspecter, nettoyer, réinspecter ; ne jamais regarder une fibre",
        "réflectomètre : bobine amorce retranchée ; pic + petite perte = connecteur ; sans pic, même perte aux deux longueurs d'onde = épissure ; perte bien plus forte à 1 550 nm = courbure ; retombée dans le bruit = fin de fibre ou cassure ; polarité inversée = LOS des deux côtés ; rayon d'un câble optique 10 × Ø au repos, 20 × Ø au tirage, traction par l'aramide",
    ],
    competencies=[
        "Choisir le câble, le connecteur et le support adaptés au débit, à la distance et à l'environnement, et le justifier",
        "Décrire la réalisation et le contrôle d'un câble RJ45 et d'un câble BNC, et interpréter un test (wiremap, ohmmètre)",
        "Calculer et mesurer une liaison optique, interpréter un relevé (photomètre, réflectomètre) et rédiger une réparation sûre",
    ],
    vocabulary=[
        "T568A", "T568B", "Auto MDI-X", "wiremap", "paires séparées", "U/UTP", "F/UTP", "S/FTP",
        "lien permanent", "RG-58", "terminateur", "10BASE2", "10BASE5", "OS2", "OM4", "LC", "UPC",
        "APC", "SFP+", "photomètre", "réflectomètre",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien dans un examen blanc /100 (10 points par "
        "question) : accepter toute formulation, toute méthode et tout ordre techniquement justes, "
        "sans exiger de mot-clé ni de libellé exact ; suivre le barème de la question et noter en "
        "proportion ; un calcul juste avec une petite erreur d'arrondi reste juste. Pénaliser un "
        "brochage faux, la confusion de T568A et T568B ou de 50 et 75 Ω, un câble livré malgré un "
        "test en échec, des cordons raccourcis pour « rattraper » un lien permanent trop long, du "
        "cuivre entre deux bâtiments, le mélange UPC/APC ou multimode/monomode, et le fait de "
        "regarder une fibre ou un module."
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

_PR08_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr08",
    course_title="AMPCR pratique écrite — PR08 Installation complète de Windows — préparation et dépannage",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : procédures d'installation de Windows rédigées, lecture d'écrans fictifs de "
        "l'installateur, du Gestionnaire de périphériques et de diskpart, dépannage écrit et "
        "rapport d'intervention"
    ),
    allowed_notions=[
        "préparation : demande, accord écrit du propriétaire (un accord oral ne suffit pas, données d'autres personnes), confidentialité, fiche d'inventaire (modèle, numéro de série, processeur, mémoire, disques et style MBR/GPT, firmware UEFI, démarrage sécurisé, TPM, mode du contrôleur AHCI/RAID/Intel VMD, édition et licence, logiciels et clés, réseau)",
        "compatibilité : prérequis de la version visée (renvoi PR07), pilotes du fabricant pour la version (chipset, stockage, réseau, graphique), périphériques sans pilote signalés au client",
        "licences : OEM (clé dans le firmware, liée au PC), commerciale (transférable si retirée de l'ancien PC), licence numérique (même matériel, même édition) ; l'édition installée doit être celle de la licence ; « Je n'ai pas de clé de produit » ; slmgr /xpr, Paramètres → Système → Activation ; jamais d'activateur ni de clé trouvée sur Internet",
        "sauvegarde vérifiée de tous les profils, dossiers hors profil, courrier .pst, favoris ; clé de récupération BitLocker relevée ; installation propre, mise à niveau sur place (depuis Windows, système sain et compatible) ou migration (transfert des données, licences logicielles désactivées sur l'ancien PC)",
        "média : outil de création de Microsoft ou ISO officielle à somme contrôlée, clé ≥ 8 Go effacée, Rufus en schéma GPT / cible UEFI ; pilote de stockage F6 (Intel RST/VMD, RAID) et pilote réseau sur la clé ; jamais de pack de pilotes d'un site inconnu",
        "firmware et démarrage : UEFI, démarrage sécurisé, TPM 2.0 ; mode du contrôleur noté et plus modifié (sinon INACCESSIBLE_BOOT_DEVICE : remettre le mode d'origine) ; autres disques débranchés (sinon ESP sur l'autre disque) ; menu de démarrage F12/F11/F8/Échap, entrée « UEFI: » ; clé en premier → l'installation recommence : retirer la clé ou Windows Boot Manager en premier",
        "installateur : langue, format, clavier belge AZERTY, clé ou pas de clé, édition de la licence, installation personnalisée, disque cible identifié par sa taille ; supprimer seulement sur le disque cible après sauvegarde vérifiée et accord écrit, sinon arrêter ; autre disque : ne pas toucher ; espace non alloué → GPT avec ESP (FAT32 ≈ 100 Mo), MSR (16 Mo), Windows (NTFS), Récupération (WinRE)",
        "message « Windows ne peut être installé que sur des disques GPT » : disque MBR → supprimer ses partitions si autorisé, ou mbr2gpt /validate puis /convert /allowFullOS depuis le Windows à garder (partition de données conservée) ; jamais le mode hérité ni la désactivation du démarrage sécurisé ; diskpart list disk (astérisque GPT) via Maj+F10, jamais clean à l'aveugle",
        "« Nous n'avons trouvé aucun lecteur » : si le firmware voit le disque, pilote de stockage (Intel VMD/RST, RAID) par « Charger un pilote » ; si le firmware ne le voit pas, diagnostic matériel ; ne pas conclure à une panne du SSD",
        "configuration initiale : région, clavier, réseau (Internet demandé, pilote prévu), nom du PC, compte saisi par le client (compte Microsoft pour Famille, compte de l'organisation ou domaine pour Professionnel), confidentialité expliquée ; un compte par personne, administrateur protégé, compte standard",
        "finalisation : pilotes chipset → stockage/réseau → graphique, Gestionnaire de périphériques sans (!), ID du matériel VEN (8086 Intel, 10EC Realtek, 10DE NVIDIA, 1022 AMD, 14E4 Broadcom) et DEV, Carte graphique de base Microsoft ; Windows Update jusqu'à « Vous êtes à jour » ; activation ; Defender et pare-feu ; chiffrement et clé de récupération hors du PC ; données restaurées et vérifiées avec le client ; point de restauration (protection du système) ou lecteur de récupération, qui ne remplacent pas une sauvegarde",
        "liste de contrôle (version et édition, activation, msinfo32 UEFI et démarrage sécurisé, Gestion des disques GPT, pilotes, mises à jour, sécurité, réseau, comptes, données et logiciels avec le client) et rapport d'intervention en rubriques (demande et accord, poste, sauvegarde, actions, contrôles, remise, recommandations, signatures), sans mot de passe",
    ],
    competencies=[
        "Rédiger la préparation et le déroulement complet d'une installation de Windows sur un poste, de l'inventaire à la validation",
        "Lire les écrans et relevés d'une installation (installateur, diskpart, Gestionnaire de périphériques, msinfo32) et dépanner par écrit stockage, démarrage, partitions, pilotes et activation",
        "Protéger les données du client et rédiger une liste de contrôle et un rapport d'intervention",
    ],
    vocabulary=[
        "OEM", "licence numérique", "édition", "activation", "UEFI", "Secure Boot", "TPM", "GPT", "MBR", "ESP",
        "MSR", "WinRE", "mbr2gpt", "diskpart", "Intel VMD", "RST", "AHCI", "F6", "OOBE", "VEN", "DEV",
        "Windows Update", "BitLocker", "point de restauration",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste est clair ; "
        "accepter un autre outil équivalent bien justifié ; suivre le barème de la question. Ne "
        "jamais valider un effacement sans sauvegarde vérifiée ni accord écrit, la suppression ou "
        "le formatage d'un autre disque que le disque cible, une édition différente de celle de la "
        "licence, un activateur ou une clé trouvée sur Internet, une image non officielle, la "
        "désactivation du démarrage sécurisé ou le passage en mode hérité pour contourner un "
        "message, la conclusion « SSD en panne » quand le firmware voit le disque, le changement "
        "du mode du contrôleur après l'installation, un pack de pilotes d'un site inconnu, ni un "
        "compte administrateur sans mot de passe."
    ),
)

_PR09_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr09",
    course_title="AMPCR pratique écrite — PR09 Installation complète de Linux — préparation et dépannage",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : procédures d'installation de Linux rédigées, lecture de terminaux fictifs "
        "(sha256sum, lsblk, efibootmgr, /etc/fstab, lspci, ip, df), dépannage écrit et rapport "
        "d'intervention"
    ),
    allowed_notions=[
        "préparation : demande, accord écrit du propriétaire (un accord oral ne suffit pas), confidentialité, fiche d'inventaire (mémoire, disques, firmware UEFI, démarrage sécurisé, mode du contrôleur AHCI/RAID/Intel RST/VMD, puces Wi-Fi et graphique par lspci -nn, Windows à garder, BitLocker)",
        "distribution selon l'usage et le matériel, version à support long (LTS) ; Ubuntu LTS, Linux Mint (base Ubuntu LTS, bureau léger Xfce pour un PC ancien), Debian stable, Fedora Workstation (cycle court, Btrfs par défaut), Pop!_OS (systemd-boot) ; apt (Debian, Ubuntu, Mint) et dnf (Fedora)",
        "image ISO du site officiel ; sha256sum -c SHA256SUMS --ignore-missing → OK (FAILED : supprimer et retélécharger ; la taille ne prouve rien) ; Get-FileHash sous Windows ; signature GPG",
        "clé USB ≥ 8 Go effacée ; balenaEtcher, Rufus (GPT/UEFI) ou sudo dd if=image.iso of=/dev/sdX bs=4M status=progress oflag=sync sur le disque entier (pas sdX1), cible identifiée par lsblk -d (taille, transport usb) ; dd n'avertit pas",
        "firmware UEFI, démarrage sécurisé laissé actif (shim signé ; mokutil --sb-state) ; pilote compilé (NVIDIA, DKMS) signé par une clé MOK à enrôler (« Perform MOK management » → « Enroll MOK », update-secureboot-policy --enroll-key sous Ubuntu) ; menu de démarrage, entrée « UEFI: » ; session live pour tester Wi-Fi, écran, son, disques avant d'installer",
        "double démarrage : sauvegarde vérifiée, clé de récupération BitLocker relevée, démarrage rapide de Windows désactivé, C: réduite depuis Windows (Gestion des disques), clé démarrée en UEFI comme Windows ; ESP de Windows réutilisée sur /boot/efi sans formatage ; MSR, Windows, WinRE et données non touchés ; Linux dans l'espace libre ; jamais « Effacer le disque » ; récapitulatif relu",
        "partitions en GPT : ESP FAT32 ≈ 300 Mo-1 Go sur /boot/efi, racine / ext4 (≥ 25 Go), /home facultative (conservée lors d'une réinstallation, sans formatage), swap partition ou fichier (/swap.img) selon la mémoire et l'hibernation (repère Red Hat : ≤ 2 Go → 2× ; 2-8 Go → = mémoire ; 8-64 Go → au moins 4 Go ; hibernation → plus grand) ; points de montage",
        "/etc/fstab : partitions désignées par UUID (lsblk -f, blkid) plutôt que /dev/sdX ; reformater change l'UUID ; copie avant modification, findmnt --verify, mount -a, systemctl daemon-reload ; option nofail pour un disque de données ; mode d'urgence « You are in emergency mode » (journalctl -xb) ; root verrouillé sous Ubuntu → session live",
        "chargeur : GRUB (Ubuntu, Debian, Mint, Fedora ; EFI/ubuntu/shimx64.efi, grubx64.efi ; update-grub), systemd-boot ; entrées UEFI et ordre : efibootmgr, sudo efibootmgr -o ; PC qui démarre directement sous Windows = ordre des entrées ; grub rescue (renvoi PR11)",
        "comptes : premier compte membre du groupe sudo (wheel sous Fedora ; Debian avec mot de passe root : pas dans sudo), root sans mot de passe sous Ubuntu, sudo usermod -aG sudo nom puis reconnexion, groups, sudo -l ; compte standard au quotidien ; pas de session root ni de mot de passe partagé",
        "réseau : NetworkManager, ip a (NO-CARRIER = pas de lien), ip route, ping de la passerelle puis d'un nom ; mises à jour sudo apt update puis sudo apt upgrade, sudo dnf upgrade, autoremove, clean ; dépôts de la distribution, jamais de paquet d'un site inconnu",
        "pilotes : la plupart dans le noyau ; lspci -nnk « Kernel driver in use » ; Broadcom BCM4360 [14e4:43a0] → pilote STA wl (bcmwl-kernel-source) ; NVIDIA ; « Pilotes additionnels », ubuntu-drivers ; câble Ethernet ou partage de connexion USB pour télécharger",
        "services systemd : systemctl status, sudo systemctl enable --now, systemctl --failed (0 loaded units listed) ; n'activer que les services demandés",
        "dépannage : disque non vu (firmware le voit ? Intel RST/RAID → AHCI si Windows à supprimer, sinon préparer Windows d'abord : INACCESSIBLE_BOOT_DEVICE) ; permissions (ls -l, propriétaire root après sudo cp → sudo chown -R utilisateur:utilisateur ; jamais chmod -R 777) ; espace (df -h, df -i, du -sh, sudo apt clean, journalctl --vacuum-size, apt autoremove ; ext4 réserve ≈ 5 % à root ; jamais de suppression dans /usr) ",
        "liste de contrôle (os-release, efibootmgr et redémarrages, mokutil --sb-state, lsblk -f et findmnt --verify, df -h, mises à jour, lspci -k, ip a et ping, systemctl --failed, groups, données avec le client) et rapport d'intervention en rubriques (demande et accord, poste, sauvegarde, actions, contrôles, remise, recommandations, signatures), sans mot de passe",
    ],
    competencies=[
        "Rédiger la préparation et le déroulement complet d'une installation de Linux, seul ou en double démarrage, de l'inventaire à la validation",
        "Lire des sorties de terminal d'une installation (sha256sum, lsblk, efibootmgr, fstab, lspci, ip, df) et dépanner par écrit disque, chargeur, fstab/UUID, réseau, permissions et espace disque",
        "Protéger les données du client et rédiger une liste de contrôle et un rapport d'intervention",
    ],
    vocabulary=[
        "distribution", "LTS", "ISO", "SHA-256", "session live", "UEFI", "Secure Boot", "shim", "MOK", "GPT", "ESP",
        "ext4", "swap", "/home", "point de montage", "fstab", "UUID", "GRUB", "systemd-boot", "efibootmgr", "sudo",
        "apt", "dnf", "lspci", "NetworkManager", "systemctl", "double démarrage", "BitLocker",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste est clair ; "
        "accepter une autre distribution ou un autre outil équivalent bien justifié (Etcher, Rufus "
        "ou dd ; apt ou dnf selon la distribution) ; suivre le barème de la question. Ne jamais "
        "valider un effacement sans sauvegarde vérifiée ni accord écrit, une image non contrôlée "
        "ou non officielle, un dd vers un disque non identifié, le formatage de l'ESP de Windows "
        "ou « Effacer le disque » dans un double démarrage, la désactivation du démarrage sécurisé "
        "pour contourner un pilote, une réinstallation pour un simple ordre de démarrage, la "
        "suppression d'une ligne de fstab sans comprendre ou sans copie, chmod -R 777, une "
        "session root ou sudo donné à tous, la suppression de fichiers de /usr pour faire de la "
        "place, ni un pilote ou paquet d'un site inconnu."
    ),
)

_PR10_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr10",
    course_title="AMPCR pratique écrite — PR10 Comptes, pilotes, paramètres et commandes",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : comptes et droits, pilotes, paramètres, services et commandes de base de "
        "Windows et de Linux, lecture de consoles fictives (net user, ipconfig, ping, tracert, "
        "nslookup, sfc, tasklist, ip, systemctl, journalctl, lsblk, df, ls -l), dépannage écrit "
        "et rapport d'intervention"
    ),
    allowed_notions=[
        "comptes : local (un seul poste, .\\nom) et de domaine (contrôleur de domaine Active Directory, DOMAINE\\nom, droits par les groupes du domaine ; détails PR22) ; compte Microsoft ; standard (groupe Utilisateurs) et administrateur nominatif (groupe Administrateurs) ; Administrateur intégré désactivé par défaut ; root verrouillé sous Ubuntu ; un compte par personne, pas de compte commun",
        "groupes : Administrateurs, Utilisateurs, Utilisateurs du Bureau à distance, Invités ; Linux sudo (wheel sous Fedora), adm (journaux), lpadmin (imprimantes), dialout (ports série), groupe de projet ; droits donnés aux groupes",
        "création et contrôle : Paramètres → Comptes, net user nom * /add (mot de passe demandé, jamais en clair), net localgroup Administrateurs nom /add ou /delete, net user nom (Compte : actif, groupes locaux) ; sudo adduser nom, sudo usermod -aG groupe nom puis reconnexion, groups nom, id nom",
        "moindre privilège ; UAC : compte standard → invite demandant le nom et le mot de passe d'un administrateur ; administrateur → invite de consentement Oui / Non ; ne pas désactiver l'UAC ; sudo : mot de passe de l'utilisateur, membre de sudo, sinon « is not in the sudoers file » ; pas de session root",
        "permissions Linux : propriétaire, groupe, autres (première classe qui correspond), r = 4, w = 2, x = 1 ; sur un dossier, w crée/supprime et x permet d'entrer ; ls -l, ls -ld ; chmod 640, 750, 770, u+x, g+w (propriétaire ou sudo) ; sudo chown utilisateur:groupe ; jamais chmod -R 777 ni chown -R sur /etc ou /home",
        "pilotes : rôle ; sources Windows Update (mises à jour facultatives), site du fabricant du PC, du composant ; jamais de pack de pilotes ou de site inconnu ; compatibilité version de Windows, 64 bits (x64) ou ARM64, modèle exact, signature ; Linux : modules du noyau, lspci -k (Kernel driver in use), lsusb, Pilotes additionnels",
        "Gestionnaire de périphériques (devmgmt.msc) : Code 28 pilotes non installés (Autres périphériques, périphérique inconnu), Code 22 désactivé (flèche vers le bas), Code 10 ne peut pas démarrer, Code 43 arrêté car il a signalé des problèmes (USB : port, câble, hub non alimenté, autre PC) ; ID du matériel PCI\\VEN_xxxx&DEV_yyyy, USB\\VID_xxxx&PID_yyyy (VEN 8086 Intel, 10EC Realtek, 10DE NVIDIA, 1022 AMD, 14E4 Broadcom ; VID 046D Logitech, 04F9 Brother, 03F0 HP, 04A9 Canon, 0BDA Realtek)",
        "mettre à jour, Restaurer le pilote (grisé si aucune version précédente), désactiver/activer, désinstaller l'appareil, rechercher les modifications ; point de restauration avant ; ancien noyau depuis GRUB sous Linux",
        "paramètres : Paramètres (Win + I), devmgmt.msc, services.msc, eventvwr.msc, diskmgmt.msc, lusrmgr.msc (pas dans l'édition Famille), Gestionnaire des tâches → Applications de démarrage, msconfig ; Linux : paramètres du bureau, systemctl list-unit-files --state=enabled",
        "services : Windows État (En cours d'exécution, Arrêté) et Type de démarrage (Automatique, Automatique début différé, Manuel, Désactivé) ; Spouleur d'impression (spoolsv.exe, net stop/start spooler, file C:\\Windows\\System32\\spool\\PRINTERS) ; systemd enabled/disabled, active (running)/inactive (dead)/failed ; systemctl status, sudo systemctl start/stop/restart/enable --now, systemctl --failed, journalctl -u service -b ; cups ; ssh (sudo sshd -t)",
        "commandes Windows : ipconfig /all (lecture standard ; /release, /renew, /flushdns en administrateur, /release à distance coupe la connexion), ping (4 échos, Délai d'attente, statistiques, un pare-feu peut bloquer), tracert -d (sauts, * délai dépassé), nslookup (serveur interrogé, Non-existent domain, délai expiré), sfc /scannow et DISM /Online /Cleanup-Image /RestoreHealth en invite administrateur (DISM puis SFC, Internet, CBS.log), tasklist /fi \"imagename eq …\" (PID, mémoire), net user",
        "commandes Linux : ip a, ip route (default via = passerelle ; Network is unreachable sans route par défaut ; modification non persistante, NetworkManager pour durable), systemctl, journalctl (groupe adm ou sudo), lsblk -f (MOUNTPOINTS vide = non monté), df -h (Use%), chmod, chown, sudo apt update puis upgrade/install, dnf ; lire avant d'agir",
        "configuration réseau : lire la configuration, ping de la passerelle, d'une adresse Internet, nslookup d'un nom ; passerelle ou DNS mal saisis ; DHCP ; adresses de documentation RFC 5737 ; dépannage complet PR24",
        "liste de contrôle (comptes, élévation, pilotes, services, réseau, système) et rapport en rubriques (demande, constat, actions, contrôles, recommandations), sans mot de passe",
    ],
    competencies=[
        "Choisir et créer les comptes et groupes adaptés selon le moindre privilège, et expliquer l'UAC et sudo",
        "Installer, mettre à jour ou restaurer un pilote, identifier un périphérique inconnu et vérifier la compatibilité",
        "Utiliser les commandes de base de Windows et de Linux : syntaxe, rôle, sortie attendue, droits nécessaires et risques ; lire des consoles et dépanner par écrit comptes, pilotes, services, périphériques USB et configuration réseau",
    ],
    vocabulary=[
        "compte local", "compte de domaine", "contrôleur de domaine", "groupe", "UAC", "sudo", "moindre privilège",
        "chmod", "chown", "pilote", "ID du matériel", "VEN", "DEV", "VID", "PID", "Code 28", "point de restauration",
        "service", "systemd", "ipconfig", "ping", "tracert", "nslookup", "sfc", "DISM", "tasklist", "net user",
        "journalctl", "lsblk", "df", "apt", "dnf",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste est clair ; "
        "accepter un autre outil ou une autre commande équivalente bien justifiée (interface "
        "graphique ou ligne de commande, chmod en chiffres ou en lettres, apt ou dnf selon la "
        "distribution) ; suivre le barème de la question. Ne jamais valider un compte commun, un "
        "compte administrateur pour l'usage quotidien ou sans mot de passe, la désactivation de "
        "l'UAC, un mot de passe écrit en clair dans une commande ou un rapport, chmod -R 777 ou un "
        "chown -R sur un dossier système, un pilote d'un site inconnu ou d'une autre version ou "
        "architecture, une mise à jour de pilote sans retour arrière possible, la désactivation de "
        "services au hasard, ipconfig /release ou l'arrêt de ssh à distance sans précaution, ni une "
        "réinstallation du système pour un simple pilote, droit ou réglage."
    ),
)

_PR12_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr12",
    course_title="AMPCR pratique écrite — PR12 Dépannage logiciel et restauration du système",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : dépannage logiciel de Windows et de Linux, restauration du système, "
        "protection des données du client, lecture de relevés fictifs (Moniteur de fiabilité, "
        "profil temporaire, volumes de WinRE, systemctl, journalctl, nginx -t, dpkg, GRUB, df, "
        "du, empreintes SHA-256, ipconfig) et rapport d'intervention"
    ),
    allowed_notions=[
        "familles de causes : système d'exploitation, application, pilote/service/programme au démarrage, service, compte ou profil, logiciel malveillant, stockage (disque plein ou défaillant) ; isoler par élimination : stockage d'abord, autre programme, compte de test, mode sans échec, démarrage minimal (msconfig), analyse antivirus hors ligne ; pannes matérielles en PR06",
        "recueil : symptôme exact et message, depuis quand, reproductibilité (permanente, intermittente, durée d'observation), portée, changements récents, données et sauvegarde ; journaux : Observateur d'événements, Moniteur de fiabilité (perfmon /rel), Historique des mises à jour, journalctl -b -p err, journalctl -b -1 (journal conservé), systemctl --failed, /var/log/apt/history.log, dnf history",
        "protection des données : sauvegarde avant la première modification (d'abord si le disque faiblit), copier sans déplacer, robocopy, Historique des fichiers, rsync -a, cp -a ; vérification : nombre, taille, ouverture d'essai, empreinte SHA-256 (Get-FileHash, certutil -hashfile … SHA256, sha256sum, sha256sum -c) ; accord écrit avant réinitialisation ou réinstallation (ce qui est effacé, sauvegardé, à réinstaller, date, signature) ; confidentialité",
        "WinRE : Maj + Redémarrer, Paramètres → Récupération → Démarrage avancé, shutdown /r /o, après deux échecs de démarrage, clé → Réparer l'ordinateur ; Dépannage → Options avancées : outil de redémarrage système (réparation du démarrage), Paramètres (mode sans échec touche 4, 5 avec réseau), Désinstaller des mises à jour, Restauration du système, Invite de commandes (X: = WinRE, lettres différentes, dir avant d'agir, pas de diskpart clean), Réinitialiser ce PC, Paramètres du microprogramme UEFI",
        "point de restauration : système, registre, pilotes, programmes, pas les documents (ce n'est pas une sauvegarde) ; Protection du système à activer, Créer ; rstrui.exe ; dernier point antérieur à la panne ; Rechercher les programmes concernés ; programmes, pilotes et mises à jour installés après le point retirés ; annulable depuis Windows",
        "SFC et DISM : DISM /Online /Cleanup-Image /RestoreHealth puis sfc /scannow en administrateur ; hors ligne sfc /scannow /offbootdir=D:\\ /offwindir=D:\\Windows ; Restaurer le pilote ; mises à jour : Historique, Désinstaller des mises à jour, Revenir en arrière (dix jours), Suspendre puis reprendre, Résoudre les problèmes à l'aide de Windows Update (réinstalle en gardant fichiers et applications)",
        "profil corrompu : profil temporaire (événement 1511 User Profile Service), fichiers toujours dans C:\\Users\\nom, rien à enregistrer dans le profil temporaire ; sauvegarde depuis un compte administrateur, disque et DISM/SFC, nouveau profil, recopier Documents, Bureau, Images, favoris (pas tout AppData), clé ProfileList réservée à un technicien ; winword /safe et compléments pour un problème d'application propre à un profil",
        "logiciels malveillants : publicitaires (page d'accueil, extension), rançongiciel (.locked, note), isoler du réseau, ne pas brancher la sauvegarde, prévenir, ne pas payer, analyse hors ligne de Microsoft Defender, restauration depuis une sauvegarde saine antérieure, mots de passe changés depuis un appareil sain",
        "Linux : systemctl --failed, status, journalctl -u service -b, test de configuration (nginx -t, sshd -t, apache2ctl configtest) avant restart, copie du fichier avant modification ; GRUB : Maj (BIOS) ou Échap (UEFI), Advanced options, noyau précédent, recovery mode, update-grub, ne pas supprimer le noyau qui fonctionne ; dpkg --configure -a, apt --fix-broken install ; fsck seulement sur une partition démontée (clé live, mode de récupération), SMART ; df -h, df -i, du -xh -d1 /var | sort -h, journalctl --vacuum-size, apt clean, apt autoremove, corriger la cause ; chown -R utilisateur:groupe sur le seul dossier restauré, cp -a ou rsync -a",
        "échelle des interventions : annuler le dernier changement, réparer les fichiers système, restauration du système, réinstaller via Windows Update, réinitialiser en conservant les fichiers (applications retirées), réinstallation complète (tout effacé) ; un changement à la fois ; précautions : noter l'état, sauvegarde à jour et accord, sauvegarde vérifiée et accord écrit ; réinstallation justifiée en dernier recours ou système compromis",
        "réseau logiciel ou physique : Média déconnecté, NO-CARRIER, Wi-Fi coupé = physique ; 169.254 = DHCP ; passerelle, Internet, DNS, application/proxy/pare-feu ; comparer avec un autre poste ou navigateur ; dépannage complet PR24",
        "contrôles finaux (symptôme, deux redémarrages, journaux, intégrité, données, espace libre) et rapport (demande, constat, sauvegarde, actions, contrôles, recommandations), sans mot de passe",
    ],
    competencies=[
        "Situer la cause d'une panne logicielle (système, application, pilote, compte, service, logiciel malveillant, stockage) à partir des symptômes, des journaux, de la reproductibilité et des changements récents",
        "Réparer ou restaurer Windows et Linux par le geste le moins invasif (WinRE, mode sans échec, point de restauration, SFC/DISM, pilotes, mises à jour, profil ; systemd, journalctl, GRUB, permissions, paquets, système de fichiers, espace disque)",
        "Protéger les données du client : sauvegarde préalable vérifiée (empreintes), accord avant réinstallation, restauration et contrôle ; distinguer panne réseau logicielle et physique ; rédiger l'intervention",
    ],
    vocabulary=[
        "WinRE", "démarrage avancé", "mode sans échec", "démarrage minimal", "point de restauration",
        "restauration du système", "SFC", "DISM", "profil temporaire", "Moniteur de fiabilité",
        "Observateur d'événements", "Réinitialiser ce PC", "rançongiciel", "systemd", "journalctl", "GRUB",
        "dpkg", "fsck", "df", "du", "SHA-256", "empreinte", "sauvegarde", "accord écrit",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si le geste est clair ; "
        "accepter un autre outil équivalent bien justifié (interface graphique ou ligne de "
        "commande, Get-FileHash ou certutil, rsync ou cp -a) ; suivre le barème de la question. "
        "Valoriser le diagnostic justifié, l'ordre du moins invasif au plus invasif et la "
        "protection des données. Ne jamais valider une réinstallation ou une réinitialisation "
        "d'emblée, sans sauvegarde vérifiée ou sans accord du client, la confusion entre point de "
        "restauration et sauvegarde, le travail dans un profil temporaire, la suppression manuelle "
        "dans C:\\Windows, WinSxS, /var/lib ou /usr, un fsck sur une partition montée, le "
        "branchement de la sauvegarde sur un poste infecté, la désactivation de l'antivirus, "
        "plusieurs changements à la fois, des mises à jour suspendues sans date de reprise, ni "
        "chmod 777 ou chown -R sur un dossier système."
    ),
)

_PR13_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr13",
    course_title="AMPCR pratique écrite — PR13 Câbles UTP, FTP, STP et coaxial — choix et pose",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : choix d'un câble à paires torsadées ou coaxial selon les contraintes, "
        "blindage et mise à la terre, règles de pose, longueurs, repérage et réception ; lecture "
        "de marquages de gaine, de relevés de chantier et de fiches techniques fictifs"
    ),
    allowed_notions=[
        "câble 4 paires torsadées, 8 conducteurs (bleu, orange, vert, marron) ; transmission différentielle ; torsade contre les parasites et le rayonnement ; pas de torsade différents contre la diaphonie ; détorsadage ≤ 13 mm ; perturbations électromagnétiques (moteurs, variateurs, néons, câbles d'énergie) ; atténuation selon longueur et fréquence ; catégorie (MHz) différente du débit (Gb/s) ; détails chiffrés en PR14",
        "désignation ISO/IEC 11801 X/YTP : X = écran global, Y = écran de chaque paire ; U aucun, F feuille, S tresse, SF tresse et feuille ; U/UTP, F/UTP, U/FTP, S/FTP, SF/UTP, S/UTP, F/FTP ; noms historiques : UTP = U/UTP, FTP souvent F/UTP (parfois U/FTP), STP ambigu (S/FTP, S/UTP, F/FTP ; à l'origine IBM type 1 150 Ω), S/STP et PiMF = S/FTP ; faire préciser X/YTP",
        "écran utile seulement s'il est continu (keystones, panneau, cordons blindés, reprise à 360°) et relié à la terre par la baie (barrette de terre, équipotentialité, électricien) ; écran interrompu ou non relié : inutile, peut capter les parasites, préférer U/UTP ; terres différentes entre bâtiments : fibre ; contrôle de la continuité de l'écran au testeur",
        "catégories : Cat5e 100 MHz 1 Gb/s sur 100 m ; Cat6 250 MHz, 10 Gb/s sur longueur réduite ; Cat6A 500 MHz 10 Gb/s sur 100 m ; toute la chaîne de la même catégorie ; monobrin (/1) posé et poinçonné, multibrin (/7) pour les cordons, fiches selon le conducteur ; CCA non conforme ; marquage de gaine (catégorie, X/YTP, 4x2xAWG23/1, MHz, LSZH, classe de réaction au feu Dca, repère métrique)",
        "connectique : fiche 8P8C dite RJ45, prise, keystone poinçonné, panneau de brassage, cordon de brassage, cordon de poste, baie, switch ; lien permanent ≤ 90 m, cordons ≤ 10 m, canal ≤ 100 m ; brochage et sertissage en PR15",
        "coaxial : âme, diélectrique, blindage (tresse, feuille), gaine ; impédance fixée par la géométrie ; 50 Ω (RG-58 10BASE2, RG-8, radio, mesure, terminateurs 50 Ω, segment 185 m) ; 75 Ω (RG-59 vidéo analogique et SDI avec BNC 75 Ω, RG-6 TV et satellite avec fiches F) ; jamais de mélange (réflexions) ; écrasement par agrafe = impédance modifiée, réflexions ; fabrication BNC en PR16",
        "choix (convention du cours) : service (Ethernet, vidéo, TV, 10BASE2) → longueur ≤ 100 m sinon fibre (PR17) → perturbations faibles U/UTP, moyennes F/UTP, fortes S/FTP → écran seulement si terre et continuité possibles, sinon U/UTP et séparation renforcée (moyennes) ou fibre (fortes) → catégorie : Cat5e pour 1 Gb/s, Cat6A pour 10 Gb/s ; référence exacte consignée",
        "pose : EN 50174-2 distance aux câbles d'énergie sans cloison, jusqu'à 3 circuits : classe a 300 mm, b 100 mm, c 50 mm, d 10 mm, classe inconnue 300 mm ; cloison métallique ; croisement à angle droit ; rayon de courbure TIA-568 : 4 × Ø non écranté, 8 × Ø écranté, coaxial selon fabricant (cours : 10 × Ø) ; traction ≤ 110 N ; colliers non serrés ou bandes auto-agrippantes, jamais d'agrafe ; réserve de câble",
        "repérage : même repère aux deux bouts avant le tirage (cours : baie-panneau-port, B1-P1-07), plan de câblage et tableau de brassage ; réception : tests câblage broche à broche, longueur, performances de la catégorie, continuité de l'écran, résultats consignés et remis au client",
    ],
    competencies=[
        "Décrire et identifier un câble à paires torsadées (torsade, diaphonie, parasites, atténuation, catégorie, désignation X/YTP et noms historiques, conducteur, marquage) et un câble coaxial (structure, 50 ou 75 Ω, usages)",
        "Choisir et justifier par écrit un câble et sa connectique selon le service, la longueur, les perturbations et la possibilité de mise à la terre",
        "Poser et contrôler une installation : séparation électrique, rayon de courbure, traction, fixation, longueurs, continuité de l'écran, repérage et tests de réception ; proposer les corrections",
    ],
    vocabulary=[
        "paire torsadée", "diaphonie", "atténuation", "U/UTP", "F/UTP", "U/FTP", "S/FTP", "écran",
        "tresse", "feuille", "mise à la terre", "catégorie", "monobrin", "multibrin", "8P8C",
        "keystone", "panneau de brassage", "cordon", "lien permanent", "canal", "coaxial", "âme",
        "diélectrique", "impédance", "RG-58", "RG-59", "rayon de courbure",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si l'idée est claire ; "
        "accepter un choix plus exigeant que le minimum s'il est justifié (Cat6 au lieu de Cat5e, "
        "U/FTP au lieu de F/UTP avec une chaîne blindée reliée à la terre) ; accepter les noms "
        "historiques s'ils sont précisés ; suivre le barème de la question. Valoriser le choix "
        "justifié par les contraintes, la règle appliquée avec son calcul et le contrôle. Ne "
        "jamais valider un lien en paire torsadée au-delà de 100 m de canal ou 90 m de lien "
        "permanent, un câble écranté sans continuité de l'écran ni mise à la terre présenté comme "
        "protégé, le mélange de 50 et 75 Ω, un monobrin en cordon ou un multibrin en lien "
        "permanent, une goulotte partagée avec le 230 V sans distance ni cloison, un rayon de "
        "courbure ou une traction hors des règles, une fixation à l'agrafe, ni une installation "
        "sans repérage ni tests."
    ),
)

_PR14_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr14",
    course_title="AMPCR pratique écrite — PR14 Débits, distances, atténuation et impédance",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : calculs de débits et de durées avec unités, longueurs maximales selon la "
        "norme et le câble, décibels, lecture de rapports de testeur (affaiblissement, NEXT), "
        "impédance et réflexions, bilan d'une liaison optique, duplex et auto-négociation, "
        "diagnostic d'une liaison à 100 Mb/s au lieu de 1 Gb/s ; relevés fictifs"
    ),
    allowed_notions=[
        "bit (b) et octet (o, B) = 8 bits ; débits en b/s, kb/s, Mb/s, Gb/s avec préfixes décimaux (k = 10³, M = 10⁶, G = 10⁹) ; tailles en octets, préfixes binaires Ki, Mi, Gi = 2¹⁰, 2²⁰, 2³⁰ (Windows écrit Go pour Gio, 1 To ≈ 931 « Go ») ; 1 Gb/s ÷ 8 = 125 Mo/s ; 100 Mb/s ÷ 8 = 12,5 Mo/s",
        "durée = taille en bits / débit utile en b/s ; débit utile = débit nominal × rendement ; rendement TCP maximal sur Ethernet 1460/1538 ≈ 94,9 % (préambule 8, en-tête 14, FCS 4, intervalle 12 octets, IPv4 20, TCP 20) ; disques, processeur, petits fichiers, Wi-Fi, half duplex réduisent le débit utile ; accepter un arrondi raisonnable",
        "Ethernet cuivre : 10BASE-T 10 Mb/s Cat3 2 paires ; 100BASE-TX 100 Mb/s Cat5 2 paires (1-2, 3-6) ; 1000BASE-T 1 Gb/s Cat5e 4 paires ; 10GBASE-T 10 Gb/s Cat6A 100 m, Cat6 55 m au plus (37 m dans le pire cas de diaphonie exogène), à certifier ; canal ≤ 100 m = lien permanent ≤ 90 m + cordons ≤ 10 m, quelle que soit la catégorie ; 2,5G/5GBASE-T en complément",
        "coaxial historique : 10BASE2 RG-58 50 Ω segment 185 m, 10BASE5 coaxial épais 50 Ω segment 500 m, bus half-duplex, terminateurs 50 Ω ; affaiblissement d'un segment ≤ 8,5 dB à 10 MHz ; répéteur pour relier deux segments",
        "décibels : affaiblissement = 10 log10(Pentrée/Psortie) (20 log10 pour des tensions) ; 3 dB ≈ ÷ 2, 6 dB ≈ ÷ 4, 10 dB = ÷ 10, 20 dB = ÷ 100 ; les dB s'additionnent ; 0 dBm = 1 mW ; affaiblissement proportionnel à la longueur, croît avec fréquence et température ; câble seul à 100 MHz sur 100 m : Cat5e 22,0, Cat6 19,8, Cat6A 19,1 dB",
        "bruit, rapport signal sur bruit ; diaphonie : NEXT mesuré du côté de l'émetteur, FEXT à l'autre bout ; valeur en dB = affaiblissement du parasite : plus grand = meilleur ; ACR = NEXT − affaiblissement ; détorsadage > 13 mm, mauvais poinçonnage, écrasement dégradent le NEXT ; blindage continu et relié à la terre",
        "impédance caractéristique fixée par la géométrie : paire torsadée 100 Ω ± 15 Ω, coaxial réseau 50 Ω, vidéo et TV 75 Ω, IBM type 1 150 Ω ; non mesurable à l'ohmmètre ; Γ = (Zcharge − Zligne)/(Zcharge + Zligne) ; ouvert +1, court-circuit −1, adapté 0 ; puissance réfléchie Γ² ; affaiblissement de réflexion −20 log10 |Γ| ; 50 Ω sur 75 Ω : Γ = 0,2, 4 %, ≈ 14 dB",
        "fibre : multimode OM1 62,5 µm, OM2-OM4 50 µm, 850/1300 nm, 3,5 et 1,5 dB/km ; monomode OS1 1,0 dB/km, OS2 0,4 dB/km, ≈ 9 µm, 1310/1550 nm ; connecteur 0,75 dB, épissure 0,3 dB au plus ; perte = km × dB/km + connecteurs + épissures ; marge = budget du module − perte ; portée selon module et fibre : 1000BASE-SX 275 m OM1, 550 m OM2 ; 1000BASE-LX 5 km ; 10GBASE-SR 33 m OM1, 82 m OM2, 300 m OM3, 400 m OM4 ; 10GBASE-LR 10 km ; vérifier portée ET budget ; mesure au photomètre",
        "duplex : half (hub, coaxial, CSMA/CD, collisions) ou full (switch, sans collision) ; auto-négociation des deux côtés, obligatoire en 1000BASE-T ; auto face à forcé : vitesse détectée, half duplex → désaccord (collisions tardives côté half, erreurs CRC côté full) ; forcer les deux côtés à l'identique si nécessaire ; 100 Mb/s au lieu de 1 Gb/s : équipement limité, réglage forcé, ou paire 4-5 / 7-8 en défaut (rétrogradation) ; ethtool (Speed, Duplex, Link partner advertised), Get-NetAdapter (LinkSpeed)",
    ],
    competencies=[
        "Convertir bits et octets, débits et tailles, et calculer une durée de copie à partir du débit utile, unités écrites",
        "Vérifier un projet ou une installation : norme, catégorie, longueur, affaiblissement, NEXT, impédance, bilan optique, et conclure par écrit",
        "Diagnostiquer et corriger un problème de duplex, de négociation ou une liaison établie à 100 Mb/s au lieu de 1 Gb/s",
    ],
    vocabulary=[
        "bit", "octet", "débit nominal", "débit utile", "rendement", "canal", "lien permanent",
        "10BASE2", "10BASE5", "1000BASE-T", "10GBASE-T", "décibel", "dBm", "affaiblissement",
        "NEXT", "FEXT", "ACR", "impédance", "réflexion", "monomode", "multimode", "budget optique",
        "marge", "half duplex", "full duplex", "auto-négociation", "collision", "CSMA/CD",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si l'idée est claire ; "
        "accepter un arrondi raisonnable et une autre méthode de calcul juste (puissances de 10, "
        "dBm) ; valoriser le calcul posé avec ses unités, la règle appliquée et le diagnostic "
        "justifié ; un résultat juste sans unité ou sans justification ne reçoit qu'une partie des "
        "points ; suivre le barème de la question. Ne jamais valider la confusion bits/octets, un "
        "débit nominal présenté comme garanti, un canal cuivre de plus de 100 m, 10 Gb/s sur Cat6 "
        "au-delà de 55 m ou sans certification, une addition de pourcentages au lieu de dB, un NEXT "
        "faible présenté comme bon, le mélange de 50 et 75 Ω, un bilan optique qui oublie la portée "
        "du module ou les connecteurs, ni un seul côté forcé présenté comme une correction."
    ),
)

_PR17_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr17",
    course_title="AMPCR pratique écrite — PR17 Fibre optique — choix, raccordement et diagnostic",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : choix d'une fibre et d'un module optique, connecteurs et jarretières, "
        "raccordement (épissure, pigtail, tiroir), pose, comparaison avec le cuivre, contrôle "
        "(propreté, photométrie, réflectométrie), sécurité laser et éclats, diagnostic d'une "
        "liaison optique ; relevés et fiches de modules fictifs"
    ),
    allowed_notions=[
        "fibre de verre : cœur d'indice plus élevé que la gaine optique (125 µm), réflexion totale ; revêtement 250 µm, protection 900 µm, aramide ; lumière infrarouge invisible (850, 1300, 1310, 1550 nm) ; aucun courant : insensible aux parasites, isolation électrique entre bâtiments",
        "multimode : cœur 50 ou 62,5 µm, 850 nm, dispersion modale, centaines de m ; OM1 62,5 µm et OM2 50 µm (gaine orange), OM3 et OM4 50 µm optimisées laser (aqua, OM4 parfois violet) ; monomode : cœur ≈ 9 µm, 1310/1550 nm, km, OS1/OS2 (jaune) ; le marquage imprimé fait foi ; un seul type de fibre de bout en bout",
        "portée = module + fibre (IEEE 802.3) : 1000BASE-SX 275 m OM1, 550 m OM2 ; 1000BASE-LX 5 km OS2 ; 10GBASE-SR 33 m OM1, 82 m OM2, 300 m OM3, 400 m OM4 ; 10GBASE-LR 10 km OS2 ; vérifier la portée ET le budget",
        "connecteurs : LC férule 1,25 mm à clip (SFP/SFP+), SC 2,5 mm carré pousser-tirer, ST baïonnette ; polissage UPC (bleu en monomode) ou APC 8° (vert) : jamais APC sur UPC ; jarretière choisie selon connecteurs, polissage, type de fibre, duplex",
        "modules : SFP 1 Gb/s, SFP+ 10 Gb/s ; même module aux deux extrémités, de la famille de la fibre (SR/SX multimode, LR/LX monomode), reconnu par le switch ; TX d'un côté vers RX de l'autre ; polarité inversée (TX sur TX) : LOS des deux côtés avec des fibres bonnes, corriger en croisant les deux fibres à une seule extrémité",
        "pertes : km × dB/km (3,5 multimode à 850 nm, 0,4 OS2) + 0,75 dB par paire de connecteurs + 0,3 dB par épissure ; puissance reçue = émise − perte (dBm − dB) ; perte d'un sens = émise d'un côté − reçue de l'autre ; plage de réception de la fiche (sensibilité, maximum) ; saturation d'un module longue portée sur liaison courte : atténuateur ou module adapté ; LOS ≈ −30 à −40 dBm",
        "raccordement : épissure par fusion (clivage, arc, manchon, cassette, ≤ 0,3 dB, pas de réflexion), épissure mécanique, pigtail (connecteur posé en usine), tiroir optique, traversées, brassage par jarretières ; pose : rayon ≥ 10 × diamètre au repos et 20 × au tirage (convention du cours, fiche du câble), tirer par l'aramide, attaches non serrées, love de réserve, étiquettes",
        "contrôle : inspecter, nettoyer (à sec, alcool isopropylique si besoin), réinspecter avant de brancher ; photométrie : référence source + cordon, perte = référence − lecture, comparée à la perte admissible ; OTDR : bobine amorce, pente en dB/km, pic = connecteur, marche sans pic = épissure, perte plus forte à 1550 nm = courbure, pic puis bruit = fin ou cassure ; position d'un défaut = position lue − amorce",
        "sécurité : ne jamais regarder une fibre ou un connecteur, même supposé éteint ; vérifier au photomètre ; capuchons ; sonde d'inspection fibre déconnectée ; éclats : tapis sombre, lunettes, récipient fermé, ruban adhésif, ni manger ni boire, mains lavées",
        "comparaison : cuivre 100 m, PoE, bon marché, sensible aux parasites, relie électriquement ; coaxial historique ou vidéo ; fibre : distance, débit, parasites, isolation, mais modules, outillage et raccordement plus chers, fragile",
    ],
    competencies=[
        "Choisir et justifier une fibre, un module et des jarretières pour une liaison, en la comparant au cuivre",
        "Décrire par écrit le raccordement, la pose et le contrôle d'une liaison optique, en sécurité",
        "Diagnostiquer une liaison optique (polarité, connecteur sale, module, distance, casse) à partir de mesures",
    ],
    vocabulary=[
        "cœur", "gaine", "réflexion totale", "multimode", "monomode", "OM3", "OS2", "LC", "SC",
        "APC", "UPC", "SFP", "SFP+", "TX", "RX", "duplex", "polarité", "longueur d'onde",
        "atténuation", "dBm", "épissure", "pigtail", "jarretière", "tiroir optique",
        "rayon de courbure", "photomètre", "réflectomètre", "OTDR", "bobine amorce", "LOS",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si l'idée est claire ; "
        "accepter un arrondi raisonnable et une autre solution technique juste et justifiée (par "
        "exemple OM4 ou monomode au lieu d'OM3) ; valoriser le diagnostic justifié par les valeurs, "
        "le choix argumenté, la procédure et la sécurité ; suivre le barème de la question. Ne "
        "jamais valider : regarder une fibre pour voir la lumière, un module multimode sur fibre "
        "monomode ou l'inverse, deux modules différents aux deux bouts, un bilan qui oublie la "
        "portée du module, un APC raccordé sur un UPC, des fibres croisées aux deux extrémités, un "
        "câble cuivre au-delà de 100 m ou entre deux bâtiments présenté comme équivalent, ni des "
        "chutes de fibre balayées à la main."
    ),
)

_PR18_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr18",
    course_title="AMPCR pratique écrite — PR18 Installation physique d'un mini-réseau",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : analyse du besoin et du plan, implantation en étoile, choix du support, "
        "longueurs et repérage, séparation du courant fort, baie et panneau de brassage, PoE, "
        "nomenclature et devis, tests et certification, validation et recette ; plans, prix et "
        "relevés fictifs"
    ),
    allowed_notions=[
        "besoin : postes, imprimantes, téléphones, caméras, Wi-Fi (personnel et invités), usages, évolution ; deux prises par poste (convention du cours) ; plan relevé : cotes, arrivée de l'opérateur, local pour la baie, chemins, câbles électriques, perturbations",
        "topologie en étoile : un câble par prise jusqu'au switch ; box ou routeur à l'arrivée de l'opérateur, reliée au switch ; étoile étendue entre switchs ; baie dans un local fermé, ventilé, central (liens ≤ 90 m) ; point d'accès en hauteur au centre de la zone, alimenté en PoE",
        "support : cuivre paire torsadée ≤ 100 m dans un bâtiment (U/UTP si perturbations faibles, F/UTP ou S/FTP si terre assurée) ; fibre au-delà de 100 m, entre bâtiments ou perturbations fortes sans terre ; coaxial 75 Ω pour vidéo analogique et TV ; toute la chaîne de la même catégorie",
        "longueur (convention du cours) = parcours horizontal le long des murs (écart en x + écart en y) + 3 m + 2 m de réserve, arrondie au mètre supérieur ; lien permanent ≤ 90 m, cordons ≤ 10 m, canal ≤ 100 m ; boîtes de 305 m sans raboutage ; repère identique à la prise et au panneau (B1-P1-07)",
        "séparation EN 50174-2 sans cloison, ≤ 3 circuits : classe a 300 mm, b 100 mm, c 50 mm, d 10 mm, inconnue 300 mm ; cloison métallique ; croisement à angle droit ; détecteur avant de percer, coupe-feu refermés",
        "baie : panneau de brassage, passe-câbles, switch, étagère de la box, bandeau électrique ; 1 U = 44,45 mm ; 25 % d'unités libres (convention) ; keystones à la prise et au panneau (2 par lien avec panneau vide) ; une seule norme T568A ou T568B ; détorsadage ≤ 13 mm",
        "switch : liens + 20 % de réserve (arrondi au-dessus) + 1 port pour la box ; tailles 8, 16, 24, 48 ; PoE : classe 1 4 W, 2 7 W, 3 15,4 W, 4 30 W réservés ; 802.3af 15,4 W, at 30 W, bt 60-90 W ; somme ≤ budget PoE total du switch",
        "devis : quantité × prix unitaire HT, total HT, TVA belge 21 %, total TTC ; nomenclature : câble, keystones, panneaux, boîtiers, cordons de brassage et de poste, switch, baie, accessoires",
        "tests : testeur de continuité (8 fils, paires, longueur), certificateur (catégorie visée, PASS/FAIL, rapport) ; lecture dans l'ordre : câblage, longueur ≤ 90 m, performances (paradiaphonie, perte d'insertion : poinçonnage, câble abîmé, composant inférieur)",
        "validation dans l'ordre : lien (voyants), adresse (ipconfig, 169.254 = pas de DHCP), passerelle (ping box), autre poste, Internet par nom, partage ; le premier contrôle en échec désigne la piste ; recette : plans, plan de brassage, rapports, validation, PV signé",
    ],
    competencies=[
        "Concevoir par écrit l'installation physique d'un mini-réseau à partir d'un besoin et d'un plan (étoile, implantation, support, longueurs, sécurité)",
        "Établir le plan de brassage, la nomenclature et le devis d'une installation",
        "Tester, valider et réceptionner un mini-réseau en lisant rapports et relevés",
    ],
    vocabulary=[
        "topologie en étoile", "switch", "box", "routeur", "point d'accès", "baie", "panneau de brassage",
        "keystone", "passe-câbles", "cordon de brassage", "lien permanent", "canal", "repère",
        "chemin de câbles", "séparation", "PoE", "budget PoE", "nomenclature", "devis", "TVA",
        "certificateur", "PASS", "FAIL", "DHCP", "passerelle", "procès-verbal de réception",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si l'idée est claire ; "
        "accepter un arrondi raisonnable et une autre solution technique juste et justifiée (par "
        "exemple un autre emplacement de baie qui garde tous les liens sous 90 m, Cat6A au lieu de "
        "Cat6, un switch plus grand justifié) ; valoriser le choix justifié par un calcul, la "
        "procédure et la sécurité ; suivre le barème de la question. Ne jamais valider : un lien "
        "permanent de plus de 90 m, un câble cuivre entre deux bâtiments ou au-delà de 100 m, un "
        "câble réseau couché contre les câbles électriques sans la distance requise, un seul "
        "keystone par lien sur un panneau vide, un budget PoE qui dépasse celui du switch, une "
        "TVA autre que 21 % pour ce devis, ni une validation qui saute un contrôle en échec."
    ),
)

_PR19_CONTEXT = PedagogicalContext(
    course_key="ampcr-pratique-pr19",
    course_title="AMPCR pratique écrite — PR19 Topologies, OSI, TCP/IP, NetBEUI et équipements",
    level=(
        "CESS Professionnel, option AMPCR, épreuve pratique écrite (Laboratoire + T.P. et "
        "méthodes) : topologies, modèles OSI et TCP/IP, encapsulation, trame Ethernet, adresses "
        "MAC et IP, ARP, ports TCP/UDP, NetBEUI, équipements, domaines de collision et de "
        "diffusion, chemin d'un paquet, diagnostic par couche ; réseaux, adresses et relevés fictifs"
    ),
    allowed_notions=[
        "topologies : bus (câble commun, bouchons ; câble coupé ou bouchon absent : tout le segment s'arrête), étoile (un câble par poste ; câble coupé : un poste ; switch central : tout), anneau (de station en station, jeton ; simple : une coupure arrête tout ; double : rebouclage), maillage (plusieurs chemins ; complet : n × (n − 1) ÷ 2 liaisons) ; topologie physique et logique (hub = étoile physique, bus logique)",
        "modèle OSI : 1 physique (bits), 2 liaison de données (trames, MAC), 3 réseau (paquets, IP, ICMP), 4 transport (segments TCP, datagrammes UDP, ports), 5 session, 6 présentation, 7 application (HTTP, HTTPS, DNS, DHCP, SMTP, SMB) ; modèle TCP/IP : accès réseau (1-2), Internet (3), transport (4), application (5-7)",
        "encapsulation : données → segment (+ TCP 20 ou UDP 8 octets) → paquet (+ IPv4 20) → trame (+ Ethernet 14 + FCS 4) ; données de trame 46 à 1 500 octets (bourrage sous 46), trame 64 à 1 518 octets, préambule non compté ; champs : MAC destination, MAC source, type (0x0800 IPv4, 0x0806 ARP, 0x86DD IPv6), données, FCS ; FF-FF-FF-FF-FF-FF = diffusion",
        "adresses : MAC dans le réseau local, IP de bout en bout, port = programme ; ARP traduit IP → MAC (table arp -a) ; TCP fiable avec accusés de réception, UDP sans ; ports HTTP 80, HTTPS 443, DNS 53, DHCP 67/68, SMTP 25/587, IMAP 143/993, FTP 20/21, SSH 22, SMB 445, RDP 3389",
        "protocole = règles d'échange ; service = fonction rendue par un programme serveur sur un port ; équipement = matériel (peut héberger des services : DHCP de la box)",
        "NetBEUI : IBM puis Microsoft, transport de NetBIOS, noms NetBIOS sans adresse réseau, diffusion, non routable (ne traverse pas un routeur), remplacé par TCP/IP ; IPX/SPX routable, historique",
        "équipements : répéteur et hub couche 1 (recopient les bits, un seul domaine de collision) ; pont, switch (table MAC, un domaine de collision par port, ne sépare pas les diffusions sauf VLAN), point d'accès couche 2 ; routeur couche 3 (relie des réseaux IP, sépare les diffusions) ; modem (signal de la ligne : VDSL, DOCSIS ; ONT sur fibre) ; passerelle par défaut = adresse du routeur ; box = modem + routeur NAT + switch + point d'accès + DHCP/DNS",
        "chemin d'un paquet : destination locale → trame vers la MAC du destinataire ; sinon vers la MAC de la passerelle ; le switch ne change rien ; chaque routeur refait la trame (MAC changent) ; IP de destination inchangée ; la box remplace l'IP source privée par son IP publique (NAT)",
        "diagnostic de bas en haut avec preuve : 1 voyant, câble, testeur ; 2 port du switch, VLAN, arp -a ; 3 ipconfig, ping de la passerelle, tracert ; 4 port du service, pare-feu, Test-NetConnection -Port ; 7 nslookup, service, identifiants",
    ],
    competencies=[
        "Reconnaître une topologie, ses avantages, ses défauts et l'effet d'une panne",
        "Situer protocoles, équipements et pannes dans les modèles OSI et TCP/IP ; suivre l'encapsulation et le chemin d'un paquet",
        "Choisir et justifier un équipement réseau ; mener un diagnostic couche par couche",
    ],
    vocabulary=[
        "topologie", "bus", "étoile", "anneau", "maillage", "OSI", "TCP/IP", "encapsulation", "trame",
        "paquet", "segment", "MAC", "ARP", "port", "TCP", "UDP", "NetBEUI", "hub", "switch", "pont",
        "routeur", "passerelle", "modem", "point d'accès", "répéteur", "domaine de collision",
        "domaine de diffusion", "VLAN", "NAT",
    ],
    constraints=(
        "Correction d'une réponse écrite de technicien : accepter toute formulation et tout ordre "
        "techniquement justes, sans exiger de mot-clé ni de sigle développé si l'idée est claire ; "
        "accepter une autre solution technique juste et justifiée (par exemple un switch de couche 3 "
        "au lieu d'un routeur pour relier deux VLAN, un maillage partiel argumenté) ; valoriser le "
        "diagnostic prouvé par les relevés, le choix argumenté par la couche et le rôle, le calcul "
        "juste ; suivre le barème de la question. Ne jamais valider : un switch présenté comme "
        "capable de relier deux réseaux IP, un switch qui sépare les diffusions sans VLAN, un hub "
        "qui sépare les collisions, NetBEUI présenté comme routable, la MAC du serveur d'Internet "
        "dans la trame émise par le poste, DNS ou DHCP placés à la couche réseau, ni l'ouverture "
        "sans besoin de ports comme 445 ou 3389 vers Internet."
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
        code="PR08",
        title="Installation complète de Windows — préparation et dépannage",
        items=PR08_ITEMS,
        context=_PR08_CONTEXT,
    ),
    PracticalCourse(
        code="PR09",
        title="Installation complète de Linux — préparation et dépannage",
        items=PR09_ITEMS,
        context=_PR09_CONTEXT,
    ),
    PracticalCourse(
        code="PR10",
        title="Comptes, pilotes, paramètres et commandes",
        items=PR10_ITEMS,
        context=_PR10_CONTEXT,
    ),
    PracticalCourse(
        code="PR11",
        title="Messages d'erreur Windows/Linux — diagnostic et interventions écrites",
        items=PR11_ITEMS,
        context=_PR11_CONTEXT,
    ),
    PracticalCourse(
        code="PR12",
        title="Dépannage logiciel et restauration du système",
        items=PR12_ITEMS,
        context=_PR12_CONTEXT,
    ),
    PracticalCourse(
        code="PR13",
        title="Câbles UTP, FTP, STP et coaxial — choix et pose",
        items=PR13_ITEMS,
        context=_PR13_CONTEXT,
    ),
    PracticalCourse(
        code="PR14",
        title="Débits, distances, atténuation et impédance",
        items=PR14_ITEMS,
        context=_PR14_CONTEXT,
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
        code="PR17",
        title="Fibre optique — choix, raccordement et diagnostic",
        items=PR17_ITEMS,
        context=_PR17_CONTEXT,
    ),
    PracticalCourse(
        code="PR18",
        title="Installation physique d'un mini-réseau",
        items=PR18_ITEMS,
        context=_PR18_CONTEXT,
    ),
    PracticalCourse(
        code="PR19",
        title="Topologies, OSI, TCP/IP, NetBEUI et équipements",
        items=PR19_ITEMS,
        context=_PR19_CONTEXT,
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
    PracticalCourse(
        code="EX02",
        title="Examen blanc écrit — installation et dépannage des systèmes",
        items=EX02_ITEMS,
        context=_EX02_CONTEXT,
    ),
    PracticalCourse(
        code="EX03",
        title="Examen blanc écrit — câblage RJ45, BNC et fibre",
        items=EX03_ITEMS,
        context=_EX03_CONTEXT,
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

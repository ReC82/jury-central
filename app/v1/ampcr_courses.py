"""Cours de révision express AMPCR MC04→MC37 (ticket #58).

Remplace les stubs « contenu pas encore rédigé » du ticket #55 par un vrai cours court,
dense et orienté examen pour chacun des 34 mini-cours MC04 à MC37. Structure fixe à 8
sections (imposée par le ticket #58) : Ce qu'il faut savoir / Définitions essentielles /
Notions principales / Procédure-méthode / Exemple concret / Pièges fréquents / Vocabulaire
FR-EN / À retenir pour l'examen.

**Périmètre** : chaque cours reste strictement borné par l'objectif déjà validé du plan
AMPCR pour ce MC (`app.v1.ampcr_plan._OBJECTIVES_BY_CODE`, transmis verbatim par ChatGPT,
ticket #55/#56). Les notions techniques standard nécessaires pour expliquer cet objectif
sont utilisées (autorisé explicitement par le ticket #58, § 10) ; aucun chapitre hors
programme n'est ajouté.

**MC38** est un cas à part (voir `AMPCR_COURSE_MARKDOWN["MC38"]`) : son cours explique le
principe de la révision finale transversale (practice/exam tirent dans MC01→MC37) — un
contenu informatif légitime, distinct des QUESTIONS de quiz, qui elles ne doivent jamais
porter sur ce mécanisme (voir `app.v1.mc38_transversal`)."""

AMPCR_COURSE_MARKDOWN: dict[str, str] = {
    "MC04": """# Stockage : HDD, SSD SATA et NVMe

## 1. Ce qu'il faut savoir
Le stockage conserve les données de façon persistante (contrairement à la RAM, effacée à
l'extinction). Trois familles dominent aujourd'hui : le disque dur mécanique (HDD), le SSD
au format SATA, et le SSD NVMe sur bus PCIe. Le choix dépend du compromis capacité /
performance / fiabilité / budget.

## 2. Définitions essentielles
- **HDD** : plateaux magnétiques en rotation + tête de lecture/écriture mobile.
- **SSD** : mémoire flash NAND, aucune pièce mobile.
- **SATA** : interface/bus historique (disques et SSD 2,5"), débit plafonné (~600 Mo/s).
- **M.2** : un **format de connecteur**, pas un protocole — un SSD M.2 peut être SATA ou
  NVMe selon le slot et le SSD.
- **NVMe** : protocole conçu pour le stockage sur bus PCIe, très haut débit et faible
  latence, généralement en M.2 aujourd'hui.
- **SMART** : indicateurs de santé du disque (température, secteurs défectueux, heures de
  fonctionnement...) — une alerte, jamais une garantie ni une sauvegarde.
- **TBW** (Terabytes Written) : endurance garantie par le fabricant pour un SSD.

## 3. Notions principales
- Un SSD n'a pas de pièces mobiles : plus rapide, plus silencieux, plus résistant aux
  chocs qu'un HDD, mais historiquement plus cher au Go (écart qui se réduit).
- Le HDD reste pertinent pour le stockage de masse (archives, gros volumes) à faible coût.
- Performances réelles d'un NVMe : dépendent du SSD, du nombre de lignes PCIe du slot, de
  la plateforme, de la charge et de la température (throttling possible en cas de
  surchauffe).
- Usure de la mémoire NAND : chaque cellule supporte un nombre fini d'écritures ; le
  contrôleur répartit l'usure (*wear leveling*) et **TRIM** aide à maintenir les
  performances dans le temps.
- Fragmentation : propre au HDD (déplacement mécanique de la tête) — **ne jamais
  défragmenter un SSD**, c'est inutile et use la mémoire flash pour rien.

## 4. Procédure / méthode
Diagnostic d'un problème de stockage, dans l'ordre : (1) le disque est-il détecté par le
BIOS/UEFI ? (câblage, port SATA, compatibilité du slot M.2 sinon) ; (2) est-il détecté par
l'OS ? (partitionnement, lettre de lecteur, pilote — jamais reformater par réflexe) ; (3)
consulter le SMART pour des signes de défaillance imminente ; (4) sauvegarder avant toute
manipulation risquée.

## 5. Exemple concret
Un utilisateur se plaint de lenteurs alors que son disque a beaucoup d'espace libre : le
symptôme oriente d'abord vers la RAM (swap), pas vers le stockage — mais si le SSD est
proche de sa capacité maximale, ses performances d'écriture peuvent aussi chuter
nettement : les deux pistes sont à vérifier.

## 6. Pièges fréquents
- Confondre M.2 (format) et NVMe (protocole) : un SSD M.2 SATA existe bel et bien.
- Croire que SMART « vert » garantit l'absence de panne future.
- Défragmenter un SSD (inutile, voire nuisible).
- Confondre synchronisation cloud et sauvegarde réelle (voir MC28/MC32).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Disque dur | HDD (hard disk drive) |
| Disque à mémoire flash | SSD (solid state drive) |
| Débit | Throughput |
| Latence | Latency |
| Endurance | Endurance / TBW |
| Sauvegarde | Backup |

## 8. À retenir pour l'examen
- HDD = mécanique ; SSD = flash NAND, sans pièce mobile.
- M.2 = connecteur ; SATA/NVMe = protocoles possibles sur ce connecteur.
- SMART = surveillance, jamais une garantie ni une sauvegarde.
- Toujours vérifier détection BIOS puis détection OS avant toute action destructive.
""",
    "MC05": """# Alimentation, refroidissement, ESD et sécurité électrique

## 1. Ce qu'il faut savoir
L'alimentation (PSU) convertit le courant secteur en plusieurs tensions continues (+12V,
+5V, +3.3V) pour tous les composants. Le refroidissement évacue la chaleur produite par le
CPU/GPU. Les décharges électrostatiques (ESD) peuvent détruire silencieusement un
composant. La sécurité électrique protège le technicien.

## 2. Définitions essentielles
- **PSU** (Power Supply Unit) : bloc d'alimentation, caractérisé par sa puissance
  nominale (en watts) et son rendement (certification 80 PLUS).
- **Connecteur ATX 24 broches** : alimente la carte mère ; **EPS 4/8 broches** : alimente
  le CPU ; **PCIe 6/8 broches** : alimente une carte graphique.
- **Pâte thermique** : assure le contact thermique entre le CPU et son dissipateur (comble
  les micro-défauts de planéité, ne remplace pas un bon serrage).
- **ESD** (ElectroStatic Discharge) : décharge d'électricité statique du corps humain
  vers un composant, invisible mais potentiellement destructrice.

## 3. Notions principales
- Puissance : additionner les besoins réels des composants (CPU, GPU, stockage,
  ventilateurs) et garder une marge — jamais dimensionner au plus juste.
- Flux d'air : air froid qui entre, air chaud qui sort, sans zone stagnante ; un boîtier
  mal ventilé peut faire throttler un CPU/GPU pourtant correctement refroidi sur le papier.
- Protection ESD : bracelet antistatique relié à la masse, ou toucher une partie métallique
  non peinte du boîtier avant manipulation, travailler sur une surface non génératrice
  d'électricité statique.
- Sécurité électrique : débrancher l'alimentation (pas seulement éteindre) avant
  d'intervenir à l'intérieur du boîtier ; ne jamais ouvrir un bloc d'alimentation
  (condensateurs pouvant rester chargés).

## 4. Procédure / méthode
Avant toute intervention : (1) éteindre et débrancher le PC du secteur ; (2) se décharger
de l'électricité statique (bracelet ou contact avec une masse métallique) ; (3) manipuler
les composants par les bords, jamais par les broches/contacts dorés ; (4) reconnecter tous
les câbles d'alimentation nécessaires avant de rebrancher et rallumer.

## 5. Exemple concret
Un PC redémarre seul sous forte charge (jeu, rendu) : cause probable = alimentation
sous-dimensionnée ou vieillissante qui ne tient plus le pic de consommation — à vérifier
avant de soupçonner un composant plus coûteux.

## 6. Pièges fréquents
- Toucher directement les composants sans précaution ESD par temps sec.
- Sous-dimensionner l'alimentation « pour économiser ».
- Appliquer trop ou pas assez de pâte thermique.
- Oublier de débrancher le secteur avant d'ouvrir le boîtier.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Bloc d'alimentation | Power supply unit (PSU) |
| Décharge électrostatique | Electrostatic discharge (ESD) |
| Dissipateur thermique | Heatsink |
| Flux d'air | Airflow |

## 8. À retenir pour l'examen
- ATX 24 broches = carte mère ; EPS = CPU ; PCIe = carte graphique.
- Toujours débrancher le secteur et se protéger contre l'ESD avant d'ouvrir un PC.
- Un redémarrage sous charge oriente d'abord vers l'alimentation.
""",
    "MC06": """# Montage, démontage et reconditionnement d'un PC

## 1. Ce qu'il faut savoir
Monter ou démonter un PC suit toujours le même ordre logique, pour éviter d'endommager un
composant ou d'oublier une connexion. Le reconditionnement ajoute un contrôle qualité et
une remise à niveau (nettoyage, mise à jour, upgrade éventuel) avant réemploi.

## 2. Définitions essentielles
- **Reconditionnement** : remise en état d'un PC existant (nettoyage, vérification,
  parfois upgrade) en vue d'une réutilisation.
- **Upgrade** : remplacement d'un composant par un plus performant (RAM, stockage,
  parfois CPU/GPU si la plateforme le permet).
- **Validation** : vérification finale que le PC démarre, est stable et que tous les
  périphériques fonctionnent avant remise en service.

## 3. Notions principales
- Ordre de montage typique : boîtier préparé → alimentation → carte mère (CPU + RAM déjà
  montés dessus si plus pratique) → refroidissement → stockage → cartes d'extension →
  câblage → premier démarrage hors boîtier ou en boîtier ouvert avant fermeture complète.
- Ordre de démontage : inverse, en débranchant systématiquement l'alimentation secteur en
  premier (voir MC05).
- Outils de base : tournevis cruciforme adapté, bracelet antistatique, pinces, parfois
  pâte thermique de rechange.
- Contrôle avant remise en service : POST réussi, RAM détectée en totalité, stockage
  détecté, tous les ports/connecteurs utilisés, absence de bruit anormal.

## 4. Procédure / méthode
1. Préparer le poste de travail (surface dégagée, protection ESD).
2. Monter CPU + refroidisseur + RAM sur la carte mère avant de la fixer dans le boîtier
   (plus facile hors boîtier).
3. Fixer la carte mère, puis l'alimentation, puis le stockage.
4. Câbler alimentation et connectique frontale du boîtier.
5. Premier démarrage test avant de refermer complètement le boîtier.
6. Contrôle final (BIOS, RAM, stockage, périphériques) puis nettoyage et étiquetage si
   reconditionnement.

## 5. Exemple concret
Un PC reconditionné ne démarre pas après remontage : vérifier d'abord les connecteurs
d'alimentation carte mère (24 broches + EPS) et la RAM correctement enclenchée — cause la
plus fréquente d'un échec de démarrage après montage.

## 6. Pièges fréquents
- Oublier un connecteur d'alimentation (EPS CPU en particulier).
- Fermer le boîtier avant d'avoir testé le démarrage.
- Négliger la protection ESD « juste pour cette fois ».
- Réutiliser un composant sans le contrôler (RAM défectueuse, disque en fin de vie).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Reconditionnement | Refurbishment |
| Montage | Build / assembly |
| Mise à niveau | Upgrade |
| Test de démarrage | Boot test |

## 8. À retenir pour l'examen
- Toujours monter CPU/RAM sur la carte mère avant de la fixer dans le boîtier.
- Toujours tester le démarrage avant de refermer définitivement.
- Reconditionnement = nettoyage + contrôle + upgrade éventuel + validation finale.
""",
    "MC07": """# BIOS, UEFI, POST et démarrage

## 1. Ce qu'il faut savoir
Avant que le système d'exploitation ne démarre, un micrologiciel (firmware) initialise le
matériel et vérifie qu'il fonctionne : c'est le rôle du BIOS/UEFI et du POST. Comprendre
cette étape est indispensable pour diagnostiquer un PC qui ne démarre pas.

## 2. Définitions essentielles
- **BIOS** (Basic Input/Output System) : ancien firmware, interface simple, limité en
  taille de disque adressable (MBR).
- **UEFI** : firmware moderne qui remplace le BIOS, supporte les grands disques (GPT),
  démarre plus vite, offre une interface graphique et le Secure Boot.
- **POST** (Power-On Self-Test) : suite de vérifications matérielles au démarrage
  (RAM, CPU, cartes détectées...) avant de lancer le chargeur de démarrage.
- **Ordre de boot** : liste ordonnée des périphériques que le firmware essaie de démarrer
  (disque interne, clé USB, réseau...).
- **Secure Boot** : vérifie la signature numérique du système d'exploitation au démarrage
  pour empêcher le chargement d'un code non autorisé (rootkit de démarrage).

## 3. Notions principales
- Le POST peut échouer avant même l'affichage à l'écran : signaux sonores (bips) ou codes
  LED selon la carte mère indiquent alors la nature du problème.
- L'UEFI a remplacé le BIOS pour tirer parti du GPT (voir MC08) et accélérer le démarrage.
- Modifier l'ordre de boot est nécessaire pour démarrer sur une clé USB d'installation.
- Le Secure Boot peut bloquer le démarrage de certains systèmes (double-boot Linux mal
  configuré, clé USB non signée) — à connaître pour le diagnostic, pas à désactiver par
  réflexe.

## 4. Procédure / méthode
Dépannage d'un problème de démarrage : (1) le PC s'allume-t-il (ventilateurs, LED) ? sinon
voir MC05/MC29 ; (2) le POST se termine-t-il (bip unique, logo affiché) ? sinon isoler
RAM/GPU/carte mère ; (3) l'ordre de boot pointe-t-il vers le bon périphérique ? (4) un
message d'erreur de chargeur de démarrage apparaît-il (disque système non trouvé) ?

## 5. Exemple concret
Un PC affiche « Reboot and select proper boot device » : le firmware a terminé son POST
correctement mais ne trouve aucun système d'exploitation valide à démarrer — il faut
vérifier l'ordre de boot et la détection du disque système, pas soupçonner la RAM.

## 6. Pièges fréquents
- Confondre un échec de POST (rien ne s'affiche) avec un échec de démarrage de l'OS
  (le POST a réussi, mais aucun OS n'est trouvé).
- Désactiver le Secure Boot sans en comprendre la raison plutôt que diagnostiquer.
- Oublier de remettre l'ordre de boot correct après une installation par clé USB.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Micrologiciel | Firmware |
| Autotest de démarrage | POST (power-on self-test) |
| Ordre de démarrage | Boot order |
| Démarrage sécurisé | Secure Boot |

## 8. À retenir pour l'examen
- BIOS = ancien, MBR ; UEFI = moderne, GPT, plus rapide, Secure Boot.
- POST = vérification matérielle AVANT le chargement de l'OS.
- « Aucun périphérique de démarrage » = problème d'ordre de boot ou de disque système,
  pas de RAM.
""",
    "MC08": """# Partitionnement, GPT/MBR et formatage

## 1. Ce qu'il faut savoir
Un disque doit être partitionné puis formaté avant de pouvoir stocker un système
d'exploitation ou des fichiers. Le type de table de partitions (MBR ou GPT) et le système
de fichiers choisi ont un impact direct sur la compatibilité et les limites du disque.

## 2. Définitions essentielles
- **Partition** : division logique d'un disque physique, vue par l'OS comme un volume
  distinct.
- **MBR** (Master Boot Record) : ancien schéma de partitionnement, limité à 4 partitions
  primaires et 2 To par disque.
- **GPT** (GUID Partition Table) : schéma moderne, associé à l'UEFI, sans limite pratique
  de 2 To ni de 4 partitions.
- **Partition EFI** (EFI System Partition) : petite partition FAT32 requise par l'UEFI
  pour stocker les chargeurs de démarrage sur un disque GPT.
- **Formatage** : préparation d'une partition avec un système de fichiers (NTFS, FAT32,
  exFAT, ext4...) pour qu'elle puisse recevoir des données.

## 3. Notions principales
- **NTFS** : système de fichiers natif de Windows, permissions avancées, pas de limite de
  taille de fichier pratique.
- **FAT32** : très compatible (lecteurs USB, consoles...), mais limité à des fichiers de
  4 Go maximum.
- **exFAT** : successeur de FAT32 pour les supports amovibles, sans la limite de 4 Go.
- **ext4** : système de fichiers courant sous Linux.
- Un disque GPT destiné à démarrer en UEFI nécessite une partition EFI ; un disque MBR
  démarre en mode BIOS/legacy.

## 4. Procédure / méthode
Avant de partitionner/formater un disque : (1) vérifier qu'aucune donnée utile n'y est
présente (opération destructive) ; (2) choisir GPT pour un usage moderne (UEFI,
disque > 2 To), MBR seulement pour une compatibilité ancienne spécifique ; (3) choisir
le système de fichiers selon l'usage (NTFS pour Windows, exFAT pour un support partagé
multi-OS, ext4 pour Linux).

## 5. Exemple concret
Un disque de 4 To formaté en MBR ne peut utiliser que 2 To : le reste de l'espace est
invisible pour l'OS tant que le disque n'est pas reconverti en GPT (avec perte des
données, sauf outils spécialisés).

## 6. Pièges fréquents
- Copier un fichier de 5 Go sur une clé USB en FAT32 → échec (limite 4 Go).
- Installer Windows en UEFI sur un disque resté en MBR sans conversion préalable.
- Formater par réflexe un disque « non détecté par l'OS » alors qu'il s'agit peut-être
  d'un problème de pilote ou de lettre de lecteur (voir MC04).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Table de partition | Partition table |
| Partition système EFI | EFI system partition (ESP) |
| Formater | To format |
| Système de fichiers | File system |

## 8. À retenir pour l'examen
- GPT = moderne, UEFI, pas de limite de 2 To/4 partitions ; MBR = ancien, BIOS.
- FAT32 limité à 4 Go par fichier ; exFAT et NTFS n'ont pas cette limite.
- Partitionner/formater efface les données existantes : toujours vérifier avant.
""",
    "MC09": """# Installer Windows proprement

## 1. Ce qu'il faut savoir
Une installation propre de Windows suit une préparation rigoureuse (sauvegarde, média
d'installation, informations réseau/licence) puis une séquence standard : installation,
pilotes, mises à jour, création de compte, tests.

## 2. Définitions essentielles
- **Clé USB bootable** : support d'installation créé avec un outil officiel (Media
  Creation Tool ou équivalent) à partir d'une image ISO.
- **Installation propre** (*clean install*) : réinstallation complète, par opposition à
  une mise à niveau qui conserve les données/applications existantes.
- **Pilote** (*driver*) : logiciel permettant à l'OS de communiquer avec un composant
  matériel précis (voir MC12).

## 3. Notions principales
- Préparation : sauvegarder les données importantes, vérifier la licence/clé produit,
  disposer des pilotes réseau/chipset si besoin (surtout pour du matériel très récent).
- Séquence d'installation : démarrer sur la clé USB (ordre de boot, voir MC07), choisir
  la partition cible (voir MC08), copier les fichiers, redémarrages automatiques.
- Après installation : installer les pilotes manquants, effectuer les mises à jour
  Windows, créer le(s) compte(s) utilisateur avec les droits appropriés.
- Tests finaux : réseau fonctionnel, périphériques reconnus, mises à jour à jour, aucun
  point d'exclamation dans le Gestionnaire de périphériques.

## 4. Procédure / méthode
1. Sauvegarder les données existantes si le disque est réutilisé.
2. Créer la clé USB bootable à partir d'une image officielle.
3. Démarrer sur la clé, partitionner/formater le disque cible (voir MC08).
4. Suivre l'installation jusqu'au premier démarrage du bureau.
5. Installer les pilotes essentiels (chipset, réseau, GPU) puis les mises à jour Windows.
6. Créer le(s) compte(s) utilisateur, vérifier les droits.
7. Tester réseau, périphériques, stabilité générale.

## 5. Exemple concret
Après installation, le PC n'a pas d'accès réseau : cause fréquente = pilote de carte
réseau manquant (matériel très récent non reconnu nativement) — à installer avant de
pouvoir télécharger les mises à jour Windows automatiquement.

## 6. Pièges fréquents
- Oublier de sauvegarder avant une installation propre.
- Négliger l'installation des pilotes chipset/réseau après l'installation.
- Créer un compte avec des droits administrateur pour l'usage quotidien sans nécessité.
- Ne pas tester les périphériques avant de considérer l'installation terminée.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Installation propre | Clean install |
| Clé USB bootable | Bootable USB drive |
| Pilote | Driver |
| Mise à jour | Update |

## 8. À retenir pour l'examen
- Toujours sauvegarder avant une installation propre.
- Ordre après installation : pilotes → mises à jour → comptes → tests.
- Un souci réseau juste après installation = souvent un pilote réseau manquant.
""",
    "MC10": """# Windows : administration et commandes essentielles

## 1. Ce qu'il faut savoir
Un technicien doit savoir naviguer dans l'arborescence Windows, gérer les comptes/
permissions, contrôler les services et périphériques, et utiliser l'invite de commandes
(CMD) ou PowerShell pour diagnostiquer/administrer plus vite que par l'interface
graphique seule.

## 2. Définitions essentielles
- **Compte utilisateur/administrateur** : un compte standard a des droits limités, un
  compte administrateur peut modifier le système (principe du moindre privilège, voir
  MC27).
- **Service Windows** : programme qui tourne en arrière-plan, souvent au démarrage, sans
  interface utilisateur directe.
- **CMD** : invite de commandes historique de Windows.
- **PowerShell** : shell plus puissant, orienté objets, qui remplace progressivement CMD
  pour l'administration avancée.

## 3. Notions principales
- Arborescence : `C:\\Users\\` (profils utilisateurs), `C:\\Windows\\` (système),
  `C:\\Program Files\\` (applications 64 bits).
- Gestion des comptes : Panneau de configuration / Paramètres, ou `net user` en CMD.
- Gestion des services : `services.msc` (interface) ou `Get-Service`/`Set-Service` en
  PowerShell.
- Gestion des périphériques : Gestionnaire de périphériques (pilotes, conflits, voir
  MC12).
- Commandes de diagnostic courantes : `ipconfig` (config réseau), `ping`
  (connectivité), `tasklist`/`Get-Process` (processus actifs), `sfc /scannow`
  (intégrité des fichiers système, voir MC30).

## 4. Procédure / méthode
Pour diagnostiquer un problème Windows en ligne de commande : (1) ouvrir CMD ou
PowerShell en administrateur si l'action le nécessite ; (2) identifier le service/
processus concerné ; (3) consulter son état ; (4) agir (redémarrer un service, arrêter un
processus bloqué) ; (5) vérifier que le problème est résolu.

## 5. Exemple concret
Une imprimante réseau n'imprime plus : vérifier que le service *Spouleur d'impression*
est bien démarré (`services.msc` ou `Get-Service Spooler`) avant de réinstaller le
pilote — un service arrêté est une cause fréquente et facile à corriger.

## 6. Pièges fréquents
- Donner des droits administrateur par défaut à tous les comptes.
- Confondre un programme figé (à fermer) avec un service système (à ne pas arrêter sans
  comprendre son rôle).
- Utiliser CMD/PowerShell sans droits administrateur pour une commande qui les requiert.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Compte utilisateur | User account |
| Service | Service |
| Invite de commandes | Command prompt |
| Gestionnaire de périphériques | Device Manager |

## 8. À retenir pour l'examen
- Compte standard = droits limités ; compte administrateur = droits étendus.
- Un service arrêté explique souvent une fonctionnalité Windows qui ne répond plus.
- PowerShell est plus puissant que CMD pour l'administration moderne, sans le remplacer
  totalement.
""",
    "MC11": """# Linux : bases utiles au technicien PC-réseaux

## 1. Ce qu'il faut savoir
Un technicien PC-réseaux rencontre régulièrement Linux (serveurs, box, équipements
réseau, postes clients). Connaître l'arborescence, les droits, `sudo`, la gestion de
paquets et quelques commandes de diagnostic est suffisant à ce niveau.

## 2. Définitions essentielles
- **Arborescence Linux** : racine unique `/`, avec des répertoires standards (`/home`,
  `/etc` config, `/var/log` journaux, `/bin`/`/usr/bin` exécutables).
- **sudo** : exécute une commande avec les droits administrateur (root) ponctuellement,
  sans se connecter en permanence en tant que root.
- **Permissions** : chaque fichier a un propriétaire, un groupe, et des droits
  lecture/écriture/exécution pour chacun (`rwx`).
- **apt** : gestionnaire de paquets des distributions basées sur Debian/Ubuntu (installer/
  mettre à jour/supprimer des logiciels).

## 3. Notions principales
- `/home/utilisateur` : fichiers personnels, comparable à `C:\\Users\\` sous Windows.
- `/etc` : fichiers de configuration système.
- Droits `rwx` affichés par `ls -l` : lecture (read), écriture (write), exécution
  (execute), pour propriétaire / groupe / autres.
- Services sous Linux moderne : gérés par `systemctl` (`systemctl status`, `start`,
  `stop`, `restart`).
- Commandes de diagnostic courantes : `ping`, `ip a` (configuration réseau), `df -h`
  (espace disque), `top`/`htop` (charge système), `journalctl` (journaux système, voir
  MC30).

## 4. Procédure / méthode
Diagnostiquer un service Linux qui ne répond pas : (1) `systemctl status <service>` pour
voir son état ; (2) `journalctl -u <service>` pour consulter ses journaux récents ; (3)
`systemctl restart <service>` si pertinent ; (4) vérifier à nouveau son état.

## 5. Exemple concret
Un utilisateur n'arrive pas à modifier un fichier de configuration : `ls -l` montre que le
fichier appartient à `root` et n'est pas accessible en écriture pour son compte — il faut
utiliser `sudo` pour l'éditer, pas changer les permissions du fichier par réflexe.

## 6. Pièges fréquents
- Travailler en permanence connecté en `root` plutôt qu'utiliser `sudo` ponctuellement.
- Modifier des permissions en `chmod 777` pour « faire disparaître » une erreur d'accès.
- Confondre `apt update` (rafraîchit la liste des paquets disponibles) et `apt upgrade`
  (installe réellement les mises à jour).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Droits d'accès | Permissions |
| Répertoire personnel | Home directory |
| Journal système | Log |
| Gestionnaire de paquets | Package manager |

## 8. À retenir pour l'examen
- `sudo` = élévation ponctuelle de droits, pas une connexion permanente en root.
- `rwx` = lecture / écriture / exécution, pour propriétaire / groupe / autres.
- `systemctl status` puis `journalctl` = première démarche pour diagnostiquer un service.
""",
    "MC12": """# Pilotes, périphériques et logiciels

## 1. Ce qu'il faut savoir
Un pilote (*driver*) permet à l'OS de dialoguer avec un composant matériel précis. Un
périphérique non reconnu, un conflit de pilote ou un logiciel incompatible sont des
causes très fréquentes de dysfonctionnement, souvent confondues avec une panne matérielle.

## 2. Définitions essentielles
- **Pilote (driver)** : logiciel intermédiaire entre l'OS et un composant matériel
  (carte graphique, imprimante, carte réseau...).
- **Périphérique inconnu** : matériel détecté électriquement mais sans pilote correspondant
  installé — apparaît avec un point d'exclamation dans le Gestionnaire de périphériques.
- **Conflit de pilotes** : deux pilotes (ou versions) qui interfèrent, provoquant
  instabilité ou dysfonctionnement.
- **Compatibilité** : capacité d'un pilote/logiciel à fonctionner correctement avec une
  version précise d'OS et de matériel.

## 3. Notions principales
- Un périphérique physiquement fonctionnel peut sembler « en panne » simplement parce que
  son pilote est absent, corrompu ou incompatible.
- Sources de pilotes fiables : site officiel du fabricant, Windows Update ; éviter les
  sites tiers non officiels (risque de logiciels indésirables).
- Désinstallation propre d'un pilote avant réinstallation : évite les conflits de
  versions résiduelles.
- Un logiciel peut être incompatible avec une version d'OS (trop ancien ou trop récent) :
  vérifier la configuration requise avant d'installer.

## 4. Procédure / méthode
Diagnostic d'un périphérique qui ne fonctionne pas : (1) est-il détecté dans le
Gestionnaire de périphériques ? (2) un point d'exclamation ou un code d'erreur est-il
affiché ? (3) le pilote est-il à jour et officiel ? (4) désinstaller puis réinstaller
proprement le pilote si besoin ; (5) tester à nouveau.

## 5. Exemple concret
Un deuxième écran ne s'affiche plus après une mise à jour Windows : cause fréquente =
pilote graphique réinitialisé ou incompatible avec la mise à jour — à réinstaller depuis
le site du fabricant plutôt que de suspecter l'écran ou le câble en premier lieu.

## 6. Pièges fréquents
- Conclure à une panne matérielle avant d'avoir vérifié le pilote.
- Installer un pilote depuis une source non officielle.
- Ne pas redémarrer après l'installation d'un pilote qui le requiert.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Pilote | Driver |
| Périphérique | Device |
| Compatibilité | Compatibility |
| Conflit de pilote | Driver conflict |

## 8. À retenir pour l'examen
- Un périphérique « inconnu » = problème de pilote, pas forcément une panne matérielle.
- Toujours privilégier les pilotes officiels (fabricant, Windows Update).
- Désinstaller proprement avant de réinstaller en cas de conflit suspecté.
""",
    "MC13": """# Fondamentaux réseau : LAN, WAN, OSI et TCP/IP

## 1. Ce qu'il faut savoir
Tout dépannage réseau s'appuie sur une compréhension des types de réseaux et des couches
qui structurent la communication (modèle OSI et modèle TCP/IP). C'est la base de tous les
autres mini-cours réseau (MC14 à MC24).

## 2. Définitions essentielles
- **LAN** (Local Area Network) : réseau local, à l'échelle d'un bâtiment/site.
- **WAN** (Wide Area Network) : réseau étendu reliant plusieurs sites (Internet en est
  l'exemple le plus vaste).
- **Modèle OSI** : 7 couches théoriques (Physique, Liaison, Réseau, Transport, Session,
  Présentation, Application) décrivant les fonctions d'une communication réseau.
- **Modèle TCP/IP** : modèle pratique à 4 couches (Accès réseau, Internet, Transport,
  Application), réellement utilisé sur Internet.
- **Encapsulation** : chaque couche ajoute ses propres informations (en-têtes) aux
  données de la couche supérieure avant transmission.
- **Trame / paquet** : une trame est l'unité de la couche Liaison (Ethernet), un paquet
  celle de la couche Réseau (IP).

## 3. Notions principales
- OSI sert de référence pédagogique ; TCP/IP est le modèle réellement implémenté.
- Équivalences utiles : couche Physique/Liaison OSI ≈ Accès réseau TCP/IP ; couche
  Réseau OSI ≈ Internet TCP/IP ; couche Transport = identique dans les deux modèles ;
  couches Session/Présentation/Application OSI ≈ Application TCP/IP.
- L'encapsulation se fait à l'émission (ajout d'en-têtes couche par couche) et la
  désencapsulation à la réception (retrait des en-têtes).
- Les équipements réseau opèrent chacun à un niveau différent (voir MC14) : un switch au
  niveau Liaison, un routeur au niveau Réseau.

## 4. Procédure / méthode
Pour situer un problème réseau, se demander à quelle couche il se produit : câble
débranché → couche Physique ; adresse MAC/switch → Liaison ; adressage IP/routage →
Réseau ; port/service → Transport/Application (cette logique est reprise et détaillée en
MC31, dépannage réseau méthodique).

## 5. Exemple concret
Un PC ne peut pas joindre un serveur : le problème peut se situer à n'importe quelle
couche — câble débranché (Physique), mauvaise adresse IP (Réseau), port bloqué par un
pare-feu (Transport), ou service arrêté côté serveur (Application). Raisonner par couche
évite de chercher au hasard.

## 6. Pièges fréquents
- Confondre LAN et WAN pour une même infrastructure (un même bâtiment peut avoir un LAN
  connecté à un WAN via un routeur Internet).
- Confondre trame et paquet, ou croire qu'ils désignent la même chose.
- Oublier que l'encapsulation ajoute des en-têtes à CHAQUE couche traversée.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Réseau local | LAN (local area network) |
| Réseau étendu | WAN (wide area network) |
| Encapsulation | Encapsulation |
| Trame | Frame |
| Paquet | Packet |

## 8. À retenir pour l'examen
- OSI = 7 couches théoriques ; TCP/IP = 4 couches réellement utilisées.
- Trame = couche Liaison ; paquet = couche Réseau.
- Raisonner « par couche » pour localiser un problème réseau.
""",
    "MC14": """# Équipements réseau : switch, routeur, point d'accès, modem

## 1. Ce qu'il faut savoir
Chaque équipement réseau a un rôle précis et opère à un niveau différent du modèle OSI.
Les confondre est une erreur fréquente qui mène à un mauvais diagnostic.

## 2. Définitions essentielles
- **Switch (commutateur)** : relie plusieurs appareils d'un même réseau local, opère au
  niveau Liaison (adresses MAC, voir MC23).
- **Routeur** : relie plusieurs réseaux différents entre eux, opère au niveau Réseau
  (adresses IP, voir MC22).
- **Point d'accès (AP)** : donne un accès Wi-Fi à un réseau filaire existant (voir MC25).
- **Modem** : convertit le signal de l'opérateur (fibre, câble, ADSL) en signal
  exploitable par le réseau local ; souvent combiné à un routeur dans les box grand
  public.

## 3. Notions principales
- Un switch fait circuler le trafic à l'intérieur d'UN SEUL réseau local (table MAC, voir
  MC23) ; il ne route pas entre réseaux différents.
- Un routeur relie des réseaux différents (ex. réseau local ↔ Internet) et prend des
  décisions basées sur les adresses IP.
- Une « box » grand public combine généralement modem + routeur + switch + point d'accès
  Wi-Fi dans un seul boîtier.
- En entreprise, ces fonctions sont souvent séparées en équipements dédiés pour plus de
  contrôle et de performance.

## 4. Procédure / méthode
Pour identifier quel équipement pose problème : un appareil ne voit AUCUN autre appareil
du réseau local → suspecter le switch/câblage ; le réseau local fonctionne mais pas
l'accès Internet → suspecter le routeur/modem ; seul le Wi-Fi est concerné, le filaire
fonctionne → suspecter le point d'accès.

## 5. Exemple concret
Deux PC filaires communiquent entre eux sans problème, mais aucun n'accède à Internet :
le switch fonctionne (communication locale OK), le problème se situe donc plutôt au niveau
du routeur ou de la connexion vers le modem/Internet.

## 6. Pièges fréquents
- Confondre switch et routeur, ou croire qu'un switch peut à lui seul donner accès à
  Internet.
- Ignorer qu'une « box » combine plusieurs fonctions en un seul boîtier.
- Chercher un problème réseau global alors que seul le Wi-Fi (point d'accès) est en
  cause.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Commutateur | Switch |
| Routeur | Router |
| Point d'accès | Access point (AP) |
| Modem | Modem |

## 8. À retenir pour l'examen
- Switch = relie des appareils d'UN réseau local (niveau Liaison, table MAC).
- Routeur = relie plusieurs réseaux (niveau Réseau, adresses IP).
- Réseau local OK mais pas Internet → suspecter routeur/modem, pas le switch.
""",
    "MC15": """# Câblage Ethernet et RJ45 : T568A/T568B

## 1. Ce qu'il faut savoir
Le câblage Ethernet en cuivre (paires torsadées, connecteur RJ45) reste la base physique
de la plupart des réseaux locaux filaires. Connaître les normes de brochage et savoir
tester un câble est une compétence pratique essentielle.

## 2. Définitions essentielles
- **UTP** (Unshielded Twisted Pair) : câble à paires torsadées non blindées, le plus
  courant.
- **STP** (Shielded Twisted Pair) : paires torsadées blindées, utilisées en environnement
  avec plus d'interférences électromagnétiques.
- **Catégorie de câble** (Cat5e, Cat6, Cat6a...) : détermine le débit et la bande passante
  supportés (Cat5e ≈ 1 Gb/s, Cat6/6a permettent le 10 Gb/s sur de plus courtes/longues
  distances selon la catégorie).
- **T568A / T568B** : deux normes de brochage des 8 fils dans le connecteur RJ45,
  différant par l'ordre des paires orange et verte.

## 3. Notions principales
- Un câble « droit » (*straight-through*) utilise le même brochage (T568B le plus souvent)
  aux deux extrémités — utilisé pour relier un PC à un switch.
- Un câble « croisé » (*crossover*) utilise T568A à une extrémité et T568B à l'autre —
  historiquement nécessaire pour relier deux PC directement, aujourd'hui rendu inutile
  par la fonction *Auto-MDIX* présente sur la plupart des équipements modernes.
- Le sertissage consiste à fixer les 8 fils dans le bon ordre dans la fiche RJ45 avec une
  pince à sertir.
- Un testeur de câble permet de vérifier que les 8 fils sont correctement connectés et
  dans le bon ordre, sans erreur de continuité.

## 4. Procédure / méthode
Sertir un câble RJ45 : (1) dénuder la gaine externe sans endommager les fils ; (2)
détordre les paires et les ranger dans l'ordre T568A ou T568B choisi ; (3) couper les fils
à la même longueur ; (4) insérer dans la fiche RJ45 jusqu'en butée ; (5) sertir avec la
pince ; (6) tester avec un testeur de câble.

## 5. Exemple concret
Un câble fraîchement serti ne fonctionne pas alors que la connexion semble physiquement en
place : cause fréquente = un fil mal poussé jusqu'en butée avant sertissage, ou un ordre
de brochage incohérent entre les deux extrémités — à vérifier avec un testeur avant de
suspecter l'équipement réseau.

## 6. Pièges fréquents
- Mélanger T568A et T568B sur un câble censé être droit.
- Croire qu'un câble croisé est toujours nécessaire (obsolète grâce à l'Auto-MDIX).
- Ne pas tester le câble après sertissage.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Paire torsadée | Twisted pair |
| Câble droit | Straight-through cable |
| Câble croisé | Crossover cable |
| Sertir | To crimp |

## 8. À retenir pour l'examen
- T568A et T568B ne diffèrent que par l'ordre des paires orange/verte.
- Câble droit = même brochage aux deux bouts ; croisé = T568A d'un côté, T568B de l'autre.
- Toujours tester un câble serti avant de le mettre en service.
""",
    "MC16": """# IPv4 : adresses, masque, passerelle et plages privées

## 1. Ce qu'il faut savoir
L'adressage IPv4 permet d'identifier chaque appareil sur un réseau. Comprendre la
structure d'une adresse, le rôle du masque et de la passerelle est indispensable avant
d'aborder le subnetting (MC17/MC18).

## 2. Définitions essentielles
- **Adresse IPv4** : 32 bits, notée en 4 blocs décimaux séparés par des points (ex.
  192.168.1.10), chaque bloc entre 0 et 255.
- **Masque de sous-réseau** : détermine quelle partie de l'adresse identifie le réseau et
  quelle partie identifie l'hôte.
- **Passerelle par défaut** : adresse IP du routeur utilisé pour sortir du réseau local
  (voir MC22).
- **RFC 1918** : plages d'adresses privées, non routables sur Internet :
  10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.
- **Loopback** : 127.0.0.1, adresse qui désigne la machine elle-même.
- **APIPA** : plage 169.254.0.0/16, attribuée automatiquement par Windows quand aucun
  serveur DHCP ne répond (voir MC19) — signe révélateur d'un problème DHCP.

## 3. Notions principales
- Une adresse IPv4 se divise conceptuellement en une partie « réseau » et une partie
  « hôte », déterminée par le masque.
- Deux appareils sur le même réseau local doivent partager la même partie réseau pour
  communiquer directement, sans passer par un routeur.
- Les plages RFC 1918 sont réutilisables par tout le monde en interne car elles ne
  circulent jamais telles quelles sur Internet (voir NAT, MC22).
- Voir une adresse en 169.254.x.x est un symptôme classique : le PC n'a pas reçu de bail
  DHCP.

## 4. Procédure / méthode
Lire une configuration IP (`ipconfig` / `ip a`) : identifier l'adresse IP, le masque, la
passerelle, et vérifier leur cohérence (l'adresse et la passerelle doivent être sur le
même réseau selon le masque).

## 5. Exemple concret
Un PC affiche l'adresse 169.254.12.34 : aucun serveur DHCP n'a répondu à temps — le
problème n'est pas le PC lui-même mais l'obtention d'une adresse (câble débranché, DHCP en
panne, VLAN mal configuré...).

## 6. Pièges fréquents
- Croire qu'une adresse privée (RFC 1918) peut être jointe directement depuis Internet.
- Confondre adresse IP et adresse MAC (voir MC20).
- Ne pas reconnaître une adresse APIPA (169.254.x.x) comme un symptôme de panne DHCP.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Adresse IP | IP address |
| Masque de sous-réseau | Subnet mask |
| Passerelle par défaut | Default gateway |
| Adresse privée | Private address |

## 8. À retenir pour l'examen
- Une adresse IPv4 = partie réseau + partie hôte, déterminée par le masque.
- Plages privées RFC 1918 : 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.
- 169.254.x.x (APIPA) = symptôme d'un échec DHCP, pas une adresse normale.
""",
    "MC17": """# Subnetting 1 : masques et CIDR

## 1. Ce qu'il faut savoir
Le subnetting divise un réseau IPv4 en sous-réseaux plus petits. La notation CIDR (/24,
/25... /30) et le calcul du masque décimal, de l'incrément et du nombre d'hôtes utilisables
sont les bases indispensables, calculables mentalement avec la bonne méthode.

## 2. Définitions essentielles
- **CIDR** (Classless Inter-Domain Routing) : notation `/n` indiquant le nombre de bits
  réservés à la partie réseau d'une adresse (ex. /24 = 24 bits réseau, 8 bits hôte).
- **Masque décimal** : traduction du CIDR en 4 blocs décimaux (ex. /24 = 255.255.255.0).
- **Incrément** : écart entre deux sous-réseaux consécutifs dans l'octet concerné,
  calculé comme `256 − (valeur du dernier octet non-255 du masque)`.
- **Nombre d'adresses** dans un sous-réseau : `2^(nombre de bits hôte)`.
- **Nombre d'hôtes utilisables** : nombre d'adresses moins 2 (l'adresse réseau et
  l'adresse de broadcast ne sont jamais attribuées à un appareil), sauf cas particulier du
  /31.

## 3. Notions principales — table de référence /24 à /30
| CIDR | Masque décimal | Incrément | Adresses totales | Hôtes utilisables |
|---|---|---|---|---|
| /24 | 255.255.255.0 | 256 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 4 | 2 |

## 4. Procédure / méthode — la méthode mentale
1. Repérer le dernier octet non-255 du masque (ex. /27 → 224).
2. Incrément = 256 − cette valeur (256 − 224 = 32).
3. Adresses totales du sous-réseau = incrément (32 pour /27).
4. Hôtes utilisables = incrément − 2 (30 pour /27).
5. Les sous-réseaux successifs sautent par pas de l'incrément (0, 32, 64, 96... pour /27).

## 5. Exemple concret
Pour /28 : dernier octet du masque = 240 → incrément = 256 − 240 = 16. Sous-réseaux
possibles dans un /24 : .0, .16, .32, .48... Chaque sous-réseau /28 offre 16 adresses,
donc 14 hôtes utilisables (16 − 2).

## 6. Pièges fréquents
- Oublier de soustraire 2 pour les hôtes utilisables (adresse réseau + broadcast).
- Confondre incrément et nombre d'hôtes utilisables (l'incrément = nombre d'adresses
  TOTALES, pas utilisables).
- Se tromper d'octet en cherchant le « dernier octet non-255 » sur un masque à cheval sur
  deux octets (au-delà de /24, hors programme de ce mini-cours qui reste sur /24 à /30).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Masque de sous-réseau | Subnet mask |
| Notation CIDR | CIDR notation |
| Incrément | Block size / increment |
| Hôtes utilisables | Usable hosts |

## 8. À retenir pour l'examen
- Incrément = 256 − dernier octet non-255 du masque.
- Hôtes utilisables = incrément − 2.
- Connaître par cœur la table /24 à /30 (masque, incrément, hôtes).
""",
    "MC18": """# Subnetting 2 : réseau, broadcast et exercices avancés

## 1. Ce qu'il faut savoir
Une fois la méthode mentale de MC17 maîtrisée, il faut savoir identifier, pour une
adresse IP donnée, à quel sous-réseau elle appartient, quelle est l'adresse réseau, quelle
est l'adresse de broadcast, et quelle est la plage d'adresses utilisables.

## 2. Définitions essentielles
- **Adresse réseau** : première adresse d'un sous-réseau (partie hôte à 0), n'est jamais
  attribuée à un appareil — identifie le sous-réseau lui-même.
- **Adresse de broadcast** : dernière adresse d'un sous-réseau (partie hôte à tous 1),
  n'est jamais attribuée à un appareil — utilisée pour diffuser à tous les hôtes du
  sous-réseau.
- **Plage utilisable** : toutes les adresses entre l'adresse réseau et l'adresse de
  broadcast, exclues.
- **Même sous-réseau** : deux adresses appartiennent au même sous-réseau si elles partagent
  la même adresse réseau selon le masque appliqué.

## 3. Notions principales
- Pour une adresse et un masque donnés : trouver l'incrément (MC17), puis déterminer entre
  quels multiples de l'incrément l'adresse se situe → cela donne l'adresse réseau (borne
  inférieure) et l'adresse de broadcast (multiple suivant − 1).
- Deux appareils sont sur le même sous-réseau seulement si leur adresse réseau calculée
  est identique — sinon ils ont besoin d'un routeur pour communiquer (voir MC22).
- Le choix d'un masque dépend du nombre d'hôtes réellement nécessaires : ne pas
  surdimensionner (gaspillage d'adresses) ni sous-dimensionner (pas assez de place pour
  les appareils).

## 4. Procédure / méthode
Pour 192.168.1.77 /27 : incrément = 32 (voir MC17). Multiples de 32 : 0, 32, 64, 96...
77 se situe entre 64 et 96 → adresse réseau = 192.168.1.64, broadcast = 192.168.1.95,
plage utilisable = .65 à .94.

## 5. Exemple concret
Deux PC, 192.168.1.30/27 et 192.168.1.40/27 : incrément 32 → réseaux respectifs .0-.31 et
.32-.63 → adresses réseau différentes (.0 et .32) → PAS le même sous-réseau, ils ont besoin
d'un routeur pour communiquer même si les trois premiers octets sont identiques.

## 6. Pièges fréquents
- Croire que deux adresses avec les mêmes 3 premiers octets sont automatiquement sur le
  même sous-réseau (faux si le masque n'est pas /24).
- Inclure l'adresse réseau ou de broadcast dans la plage utilisable.
- Choisir un masque disproportionné par rapport au nombre réel d'appareils.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Adresse réseau | Network address |
| Adresse de diffusion | Broadcast address |
| Plage d'adresses | Address range |
| Même sous-réseau | Same subnet |

## 8. À retenir pour l'examen
- Adresse réseau = borne basse (hôte à 0) ; broadcast = borne haute (hôte à tous 1).
- « Même sous-réseau » se vérifie par le calcul, pas par ressemblance visuelle des octets.
- Choisir le masque selon le nombre réel d'hôtes nécessaires.
""",
    "MC19": """# DHCP : attribution automatique des paramètres IP

## 1. Ce qu'il faut savoir
DHCP attribue automatiquement une adresse IP et les paramètres réseau associés
(masque, passerelle, DNS) à un appareil qui se connecte, évitant une configuration
manuelle sur chaque poste.

## 2. Définitions essentielles
- **DHCP** (Dynamic Host Configuration Protocol) : protocole d'attribution automatique
  des paramètres IP.
- **Bail DHCP** (*lease*) : durée pendant laquelle une adresse est attribuée à un
  appareil, renouvelable avant expiration.
- **DORA** : les 4 étapes de l'échange DHCP — Discover (le client cherche un serveur),
  Offer (le serveur propose une adresse), Request (le client la demande formellement),
  Acknowledge (le serveur confirme l'attribution).
- **Réservation DHCP** : association fixe entre l'adresse MAC d'un appareil et une
  adresse IP précise, toujours attribuée à cet appareil via DHCP (pratique pour une
  imprimante, un serveur local...).

## 3. Notions principales
- Sans réponse DHCP, un PC Windows s'auto-attribue une adresse APIPA (169.254.x.x, voir
  MC16) — signe caractéristique d'un problème DHCP.
- Un appareil doit renouveler son bail avant expiration ; s'il ne le peut pas, il en
  redemande un nouveau (nouveau DORA).
- Une réservation DHCP combine la simplicité de DHCP avec la stabilité d'une adresse fixe,
  sans configuration manuelle sur l'appareil lui-même.
- Un seul serveur DHCP doit répondre par réseau : deux serveurs DHCP actifs sur le même
  réseau local provoquent des conflits d'adresses.

## 4. Procédure / méthode
Dépanner une absence d'adresse DHCP : (1) vérifier la connexion physique/Wi-Fi ; (2)
vérifier qu'un serveur DHCP est bien actif et accessible sur ce réseau/VLAN ; (3) forcer
un renouvellement de bail (`ipconfig /release` puis `/renew` sous Windows) ; (4) vérifier
l'absence de second serveur DHCP parasite si des adresses incohérentes apparaissent.

## 5. Exemple concret
Après le remplacement d'un routeur, plusieurs postes reçoivent une adresse Wi-Fi
169.254.x.x : le nouveau routeur n'a probablement pas son serveur DHCP activé — à
vérifier avant de suspecter chaque poste individuellement.

## 6. Pièges fréquents
- Diagnostiquer poste par poste un problème qui touche en réalité tout le réseau
  (serveur DHCP en panne).
- Oublier qu'une adresse APIPA n'est PAS une adresse réseau valide pour communiquer.
- Laisser deux serveurs DHCP actifs simultanément sur le même réseau par erreur.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Bail | Lease |
| Réservation | Reservation |
| Renouvellement | Renewal |
| Serveur DHCP | DHCP server |

## 8. À retenir pour l'examen
- DORA = Discover, Offer, Request, Acknowledge.
- APIPA (169.254.x.x) = symptôme d'un DHCP indisponible.
- Une réservation DHCP fixe une adresse à une adresse MAC, sans configuration manuelle.
""",
    "MC20": """# DNS, ARP et ICMP

## 1. Ce qu'il faut savoir
DNS traduit les noms de domaine en adresses IP, ARP traduit les adresses IP en adresses
MAC sur le réseau local, et ICMP permet de tester la connectivité (notamment via `ping`).
Trois protocoles de diagnostic incontournables.

## 2. Définitions essentielles
- **DNS** (Domain Name System) : traduit un nom (ex. exemple.com) en adresse IP.
- **Cache DNS** : mémoire locale des résolutions DNS déjà effectuées, pour accélérer les
  accès suivants et réduire les requêtes réseau.
- **ARP** (Address Resolution Protocol) : traduit une adresse IP en adresse MAC sur un
  même réseau local (indispensable pour qu'une trame Ethernet atteigne le bon appareil).
- **ICMP** (Internet Control Message Protocol) : protocole de contrôle utilisé notamment
  par `ping` (test d'accessibilité) et par les messages d'erreur réseau.

## 3. Notions principales
- Pour joindre un appareil du même réseau local, IP ne suffit pas : il faut l'adresse MAC
  correspondante, obtenue via une requête ARP.
- Le cache DNS peut contenir une entrée périmée (site déplacé, IP changée) : vider le
  cache DNS fait parfois partie du dépannage.
- `ping` envoie des paquets ICMP Echo Request et attend une réponse Echo Reply : un
  échec peut venir d'un pare-feu qui bloque ICMP, pas nécessairement d'une vraie panne
  réseau.
- Un nom qui ne se résout pas (« hôte inconnu ») pointe vers un problème DNS, distinct
  d'un problème de routage/connectivité pure.

## 4. Procédure / méthode
Diagnostiquer un accès impossible à un site : (1) `ping` l'adresse IP directement (si
connue) pour tester la connectivité pure, sans DNS ; (2) `ping` le nom de domaine pour
tester la résolution DNS ; (3) si l'IP répond mais pas le nom, le problème est DNS ; (4)
si rien ne répond, le problème est plus bas niveau (routage/connectivité, voir MC31).

## 5. Exemple concret
Un utilisateur ne peut plus accéder à un site précis mais tous les autres fonctionnent :
`ping` par IP directe fonctionne, mais `ping` par nom échoue → cache DNS périmé ou
serveur DNS ne résolvant pas ce nom → vider le cache DNS ou changer de serveur DNS.

## 6. Pièges fréquents
- Conclure à une panne réseau générale alors qu'ICMP est simplement bloqué par un
  pare-feu (un `ping` qui échoue ne prouve pas toujours une vraie coupure).
- Oublier que ARP fonctionne uniquement à l'intérieur d'un même réseau local.
- Ne pas penser à tester par IP directe pour isoler un problème DNS.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Résolution de noms | Name resolution |
| Antémémoire | Cache |
| Requête | Request |
| Test de connectivité | Connectivity test |

## 8. À retenir pour l'examen
- DNS = nom → IP ; ARP = IP → MAC (réseau local uniquement) ; ICMP = test/contrôle
  (`ping`).
- `ping` qui échoue ne prouve pas toujours une panne réelle (ICMP peut être bloqué).
- Tester par IP directe permet d'isoler un problème DNS d'un problème de connectivité.
""",
    "MC21": """# TCP, UDP et ports réseau

## 1. Ce qu'il faut savoir
TCP et UDP sont les deux protocoles de transport principaux d'Internet. Les ports
permettent à plusieurs services de cohabiter sur une même adresse IP. Connaître les
ports des services courants aide énormément au diagnostic.

## 2. Définitions essentielles
- **TCP** (Transmission Control Protocol) : protocole fiable, orienté connexion, avec
  accusés de réception et retransmission en cas de perte — utilisé quand la fiabilité
  prime (web, email, transfert de fichiers).
- **UDP** (User Datagram Protocol) : protocole rapide, sans connexion ni garantie de
  livraison — utilisé quand la vitesse prime sur la fiabilité (streaming, jeux en ligne,
  DNS).
- **Port** : numéro (0 à 65535) qui identifie un service précis sur une machine.
- **Socket** : combinaison adresse IP + port, qui identifie une communication réseau de
  façon unique.

## 3. Notions principales — ports courants à connaître
| Service | Port | Protocole |
|---|---|---|
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| DNS | 53 | UDP (et TCP) |
| DHCP | 67/68 | UDP |
| SSH | 22 | TCP |
| RDP | 3389 | TCP |

- TCP établit une connexion (négociation en trois étapes) avant d'échanger des données ;
  UDP envoie directement, sans négociation préalable.
- Un pare-feu peut bloquer un service précis simplement en filtrant son port, sans couper
  tout le réseau.

## 4. Procédure / méthode
Diagnostiquer un service inaccessible : (1) identifier le port utilisé par ce service ;
(2) vérifier la connectivité IP de base (voir MC20/MC31) ; (3) vérifier qu'aucun pare-feu
(poste ou réseau) ne bloque ce port précis ; (4) vérifier que le service écoute bien sur
ce port côté serveur.

## 5. Exemple concret
Un utilisateur ne peut plus se connecter en bureau à distance (RDP) alors qu'il peut
naviguer sur Internet normalement : le problème est probablement localisé au port 3389
(bloqué par un pare-feu ou service RDP arrêté), pas à la connectivité réseau générale.

## 6. Pièges fréquents
- Croire qu'un problème sur un service précis signifie une panne réseau totale.
- Confondre TCP (fiable, avec connexion) et UDP (rapide, sans connexion).
- Ne pas connaître les ports des services les plus courants (80, 443, 53, 22, 3389).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Port | Port |
| Connexion | Connection |
| Sans connexion | Connectionless |
| Prise (IP+port) | Socket |

## 8. À retenir pour l'examen
- TCP = fiable, avec connexion (web, email) ; UDP = rapide, sans connexion (streaming,
  DNS).
- Connaître les ports 80/443 (web), 53 (DNS), 22 (SSH), 3389 (RDP).
- Un service bloqué (port filtré) n'est pas toujours une panne réseau générale.
""",
    "MC22": """# Internet, NAT/PAT et routage de base

## 1. Ce qu'il faut savoir
Pour qu'un réseau local (souvent en adressage privé, voir MC16) accède à Internet, un
routeur effectue une traduction d'adresses (NAT/PAT) et utilise une route par défaut vers
la passerelle.

## 2. Définitions essentielles
- **Route par défaut** : règle de routage utilisée quand aucune route plus précise ne
  correspond à la destination — généralement « tout ce qui n'est pas local part vers la
  passerelle ».
- **NAT** (Network Address Translation) : traduit une adresse IP privée en adresse IP
  publique (et inversement) pour permettre l'accès à Internet.
- **PAT** (Port Address Translation) : variante de NAT qui permet à PLUSIEURS appareils
  internes de partager UNE SEULE adresse IP publique, en distinguant leurs connexions par
  numéro de port.
- **IP publique** : adresse routable sur Internet, unique mondialement.
- **IP privée** : adresse RFC 1918 (voir MC16), non routable directement sur Internet.

## 3. Notions principales
- Un PC avec une adresse privée (192.168.x.x par exemple) ne peut pas être joint
  directement depuis Internet : le routeur traduit son adresse via NAT/PAT pour qu'il
  puisse sortir, et inversement pour les réponses.
- PAT est la forme la plus courante à la maison : tous les appareils du réseau local
  partagent la même IP publique du routeur, différenciés par leurs ports.
- La passerelle par défaut (voir MC16) est l'adresse locale du routeur qui effectue cette
  traduction et transmet le trafic vers Internet.
- Le chemin complet : PC → passerelle (routeur local) → NAT/PAT → Internet → serveur
  distant, et le chemin inverse pour la réponse.

## 4. Procédure / méthode
Vérifier l'accès Internet d'un poste : (1) vérifier qu'une adresse IP privée cohérente est
attribuée (voir MC16/MC19) ; (2) vérifier que la passerelle par défaut est correcte et
joignable (`ping` de la passerelle) ; (3) vérifier que le routeur a lui-même un accès
Internet fonctionnel (IP publique active côté opérateur).

## 5. Exemple concret
Un PC peut joindre sa passerelle (`ping` réussi) mais pas un site externe : le problème se
situe entre le routeur et Internet (côté opérateur, ou configuration NAT/PAT), pas dans le
réseau local lui-même.

## 6. Pièges fréquents
- Croire qu'une adresse privée peut être jointe directement depuis l'extérieur sans NAT.
- Confondre NAT (traduction d'adresse générale) et PAT (partage d'une IP via les ports).
- Diagnostiquer le PC alors que le problème est situé plus loin, côté routeur/opérateur.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Traduction d'adresse réseau | Network address translation (NAT) |
| Traduction d'adresse de port | Port address translation (PAT) |
| Route par défaut | Default route |
| Adresse publique | Public address |

## 8. À retenir pour l'examen
- NAT/PAT traduit une adresse privée en adresse publique pour accéder à Internet.
- PAT permet à plusieurs appareils de partager UNE SEULE IP publique via les ports.
- `ping` réussi vers la passerelle mais pas au-delà → problème côté routeur/Internet.
""",
    "MC23": """# Switching, topologies et segmentation

## 1. Ce qu'il faut savoir
Un switch fait circuler le trafic à l'intérieur d'un réseau local en apprenant les
adresses MAC de chaque appareil connecté. Comprendre la table MAC et les notions de
domaine de collision/broadcast permet de raisonner sur la performance et la segmentation
d'un réseau.

## 2. Définitions essentielles
- **Table MAC** (table de commutation) : associe chaque adresse MAC connue à un port
  précis du switch, apprise automatiquement par l'observation du trafic.
- **Topologie en étoile** : chaque appareil est relié individuellement à un équipement
  central (switch) — topologie standard des réseaux Ethernet modernes.
- **Domaine de collision** : ensemble d'appareils qui pourraient entrer en collision s'ils
  émettaient en même temps ; un switch moderne isole chaque port dans son propre domaine
  de collision.
- **Domaine de broadcast** : ensemble d'appareils qui reçoivent tous un même message de
  diffusion (broadcast) ; un switch seul ne segmente PAS les domaines de broadcast
  (contrairement à un routeur ou à des VLAN, voir MC24).
- **Segmentation** : division d'un réseau en zones plus petites pour améliorer
  performance et sécurité.

## 3. Notions principales
- Quand un switch reçoit une trame vers une adresse MAC inconnue, il la diffuse sur tous
  ses ports (sauf celui d'origine) ; une fois la réponse reçue, il apprend l'association
  et n'a plus besoin de diffuser pour cette adresse.
- La topologie en étoile facilite le dépannage : un câble ou un appareil en panne
  n'affecte que sa propre branche, pas tout le réseau.
- Un grand réseau plat (sans segmentation) souffre d'un trafic de broadcast excessif à
  mesure qu'il grandit — d'où l'intérêt des VLAN (MC24).

## 4. Procédure / méthode
Pour vérifier si un problème vient du switch : isoler l'appareil concerné (le brancher sur
un autre port, voire un autre switch) et observer si le problème persiste — s'il
disparaît, le port ou le switch initial est en cause.

## 5. Exemple concret
Un réseau devient globalement plus lent à mesure que de nouveaux appareils sont ajoutés,
sans qu'aucun appareil précis ne soit en cause : signe possible d'un domaine de broadcast
devenu trop grand, justifiant une segmentation en VLAN (voir MC24).

## 6. Pièges fréquents
- Croire qu'un switch segmente les domaines de broadcast (faux — seul un routeur/VLAN le
  fait).
- Oublier que la table MAC est apprise dynamiquement, pas configurée manuellement.
- Confondre domaine de collision (quasiment résolu par le switch moderne) et domaine de
  broadcast (toujours présent sans segmentation).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Table de commutation | MAC address table |
| Topologie en étoile | Star topology |
| Domaine de diffusion | Broadcast domain |
| Segmentation | Segmentation |

## 8. À retenir pour l'examen
- La table MAC d'un switch s'apprend automatiquement par observation du trafic.
- Un switch isole les domaines de collision mais PAS les domaines de broadcast.
- La segmentation (VLAN) devient nécessaire quand le réseau grandit trop.
""",
    "MC24": """# VLAN, trunk et réseau invité

## 1. Ce qu'il faut savoir
Un VLAN divise logiquement un réseau physique en plusieurs réseaux distincts, sans
câblage supplémentaire. Le trunk 802.1Q permet de faire transiter plusieurs VLAN sur un
seul lien entre équipements.

## 2. Définitions essentielles
- **VLAN** (Virtual LAN) : réseau local virtuel, qui segmente logiquement un réseau
  physique en plusieurs domaines de broadcast distincts.
- **Port access** : port de switch qui n'appartient qu'à UN SEUL VLAN, généralement celui
  où se connecte un appareil final (PC, imprimante...).
- **Port trunk** : port qui transporte PLUSIEURS VLAN simultanément entre deux
  équipements (typiquement entre deux switches, ou switch-routeur).
- **802.1Q** : norme qui définit le marquage (*tagging*) des trames pour identifier à
  quel VLAN chacune appartient sur un lien trunk.
- **Réseau invité** : VLAN dédié aux visiteurs, isolé du réseau interne pour des raisons
  de sécurité.

## 3. Notions principales
- Sans VLAN, tous les appareils d'un même switch partagent le même domaine de broadcast
  (voir MC23), même si l'entreprise voudrait les séparer logiquement (comptabilité,
  production, invités...).
- Un port access appartient à un seul VLAN : les trames qui en sortent ne sont pas
  marquées (l'appareil final ne sait rien du VLAN).
- Un port trunk transporte plusieurs VLAN en ajoutant une étiquette 802.1Q à chaque trame,
  pour que l'équipement de l'autre côté sache à quel VLAN elle appartient.
- Un réseau invité en VLAN séparé empêche les visiteurs d'accéder aux ressources internes,
  tout en leur donnant un accès Internet.

## 4. Procédure / méthode
Mettre en place un cas simple : (1) créer les VLAN nécessaires sur le switch (ex. VLAN 10
= interne, VLAN 20 = invités) ; (2) configurer les ports des appareils finaux en mode
access sur le bon VLAN ; (3) configurer en trunk le port reliant deux switches (ou switch
et routeur) pour que les deux VLAN puissent y transiter ; (4) vérifier l'isolation entre
VLAN si voulue.

## 5. Exemple concret
Un ordinateur branché sur un port configuré par erreur en VLAN invité au lieu du VLAN
interne n'aura accès qu'à Internet, pas aux ressources internes (serveurs, imprimantes
internes) — un cas fréquent d'erreur de configuration de port à vérifier en priorité.

## 6. Pièges fréquents
- Brancher un appareil final sur un port trunk par erreur (il ne comprendra pas les
  trames marquées 802.1Q).
- Oublier de configurer le port trunk entre deux switches, coupant la communication d'un
  VLAN entre eux.
- Mélanger réseau invité et réseau interne sur le même VLAN par erreur de configuration.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Réseau local virtuel | Virtual LAN (VLAN) |
| Port d'accès | Access port |
| Port de jonction | Trunk port |
| Marquage | Tagging |

## 8. À retenir pour l'examen
- VLAN = segmentation logique d'un réseau physique en plusieurs domaines de broadcast.
- Port access = un seul VLAN ; port trunk = plusieurs VLAN marqués 802.1Q.
- Un réseau invité doit être isolé du réseau interne via un VLAN dédié.
""",
    "MC25": """# Wi-Fi : normes, bandes, canaux et couverture

## 1. Ce qu'il faut savoir
Le Wi-Fi repose sur les normes 802.11, utilise des bandes de fréquences et des canaux, et
sa qualité dépend fortement des interférences et de la couverture physique.

## 2. Définitions essentielles
- **802.11** : famille de normes Wi-Fi (802.11n, ac, ax...), chacune apportant débit et
  fonctionnalités supplémentaires.
- **Bande de fréquence** : 2,4 GHz (plus grande portée, plus sensible aux interférences,
  moins de canaux) ou 5 GHz/6 GHz (portée plus courte, moins d'interférences, plus de
  canaux, débits plus élevés).
- **Canal** : sous-division d'une bande de fréquence utilisée par un point d'accès pour
  émettre ; des canaux qui se chevauchent créent des interférences.
- **SSID** : nom du réseau Wi-Fi affiché aux utilisateurs.
- **BSSID** : adresse MAC du point d'accès qui diffuse ce SSID.
- **Roaming** : capacité d'un appareil à basculer d'un point d'accès à un autre du même
  réseau sans interruption perceptible.

## 3. Notions principales
- 2,4 GHz : meilleure portée à travers les murs mais bande plus encombrée (Bluetooth,
  micro-ondes, voisinage) et moins de canaux non-chevauchants disponibles (1, 6, 11 en
  Europe).
- 5 GHz/6 GHz : plus de canaux, moins d'interférences, débits plus élevés, mais portée
  physique réduite.
- La largeur de canal (20/40/80 MHz...) augmente le débit théorique mais augmente aussi le
  risque d'interférence avec les canaux voisins.
- Une bonne couverture nécessite parfois plusieurs points d'accès avec roaming, plutôt
  qu'un seul point d'accès très puissant.

## 4. Procédure / méthode
Diagnostiquer une mauvaise connexion Wi-Fi : (1) identifier la bande utilisée (2,4 ou
5 GHz) ; (2) vérifier l'encombrement du canal (voisinage, autres appareils) ; (3) évaluer
la distance/obstacles entre l'appareil et le point d'accès ; (4) envisager un changement
de canal ou l'ajout d'un point d'accès si la couverture est insuffisante.

## 5. Exemple concret
Dans un immeuble avec de nombreux réseaux Wi-Fi voisins, une connexion 2,4 GHz est lente
et instable alors que le débit Internet est normal : cause probable = interférences avec
les réseaux voisins sur la même bande/canal — passer sur 5 GHz ou changer de canal peut
résoudre le problème sans toucher au reste de l'installation.

## 6. Pièges fréquents
- Croire qu'un signal Wi-Fi « fort » garantit un bon débit (les interférences comptent
  autant que la puissance du signal).
- Utiliser systématiquement le canal par défaut sans vérifier l'encombrement local.
- Négliger le roaming dans un grand bâtiment avec plusieurs points d'accès mal configurés.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Point d'accès | Access point |
| Bande de fréquence | Frequency band |
| Canal | Channel |
| Interférence | Interference |

## 8. À retenir pour l'examen
- 2,4 GHz = portée, mais plus d'interférences ; 5/6 GHz = débit, mais portée réduite.
- Canaux non-chevauchants en 2,4 GHz : 1, 6, 11 (Europe).
- Une mauvaise connexion peut venir des interférences, pas seulement de la puissance du
  signal.
""",
    "MC26": """# Sécurité Wi-Fi : WPA2, WPA3, PSK, Enterprise

## 1. Ce qu'il faut savoir
Sécuriser un réseau Wi-Fi passe par le choix du bon protocole de chiffrement, du bon mode
d'authentification, et par des mesures complémentaires comme l'isolation des invités.

## 2. Définitions essentielles
- **WEP** : ancien protocole de sécurité Wi-Fi, aujourd'hui cassable en quelques minutes
  — à ne plus jamais utiliser.
- **WPA / WPA2 / WPA3** : protocoles successifs, chacun corrigeant les failles du
  précédent ; WPA2 reste largement répandu, WPA3 est le standard actuel recommandé.
- **PSK** (Pre-Shared Key) : mode d'authentification par mot de passe partagé, adapté au
  domicile/petite structure.
- **802.1X / RADIUS** : authentification individuelle (compte utilisateur) via un serveur
  dédié, adaptée à l'entreprise (mode « Enterprise »).
- **Isolation client** (*client isolation*) : empêche les appareils connectés à un même
  point d'accès de communiquer entre eux (utile sur un réseau invité).
- **WPS** (Wi-Fi Protected Setup) : méthode de connexion simplifiée par code PIN,
  historiquement vulnérable et souvent désactivée pour raisons de sécurité.

## 3. Notions principales
- WEP est obsolète et ne doit plus jamais être utilisé, même « pour du matériel ancien ».
- WPA2-PSK convient à un usage domestique ; WPA2/WPA3-Enterprise (802.1X/RADIUS) convient
  à une entreprise où chaque utilisateur doit avoir ses propres identifiants (traçabilité,
  révocation individuelle possible).
- Un réseau invité doit combiner VLAN dédié (voir MC24) et isolation client, pour éviter
  qu'un visiteur accède aux ressources internes ou aux autres appareils invités.
- WPS facilite la connexion mais est une faille de sécurité connue : à désactiver sur les
  réseaux qui n'en ont pas l'usage.

## 4. Procédure / méthode
Sécuriser un point d'accès : (1) choisir WPA2 ou WPA3 (jamais WEP/WPA) ; (2) choisir PSK
(domicile/petite structure) ou Enterprise avec RADIUS (organisation avec plusieurs
utilisateurs à distinguer) ; (3) isoler le réseau invité en VLAN séparé avec isolation
client ; (4) désactiver WPS si non nécessaire.

## 5. Exemple concret
Une entreprise veut que chaque employé se connecte avec son propre compte et puisse être
révoqué individuellement en cas de départ : PSK (mot de passe unique partagé par tous) ne
convient pas — il faut du 802.1X/RADIUS (mode Enterprise).

## 6. Pièges fréquents
- Utiliser encore WEP « parce que ça marche ».
- Mettre le réseau invité sur le même SSID/VLAN que le réseau interne.
- Laisser WPS activé sans raison sur un réseau sensible.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Clé pré-partagée | Pre-shared key (PSK) |
| Isolation client | Client isolation |
| Authentification par serveur | RADIUS authentication |
| Point d'accès | Access point |

## 8. À retenir pour l'examen
- WEP = jamais ; WPA2/WPA3 = standards actuels.
- PSK = domicile ; 802.1X/RADIUS (Enterprise) = comptes individuels en entreprise.
- Réseau invité = VLAN dédié + isolation client.
""",
    "MC27": """# Sécurité réseau traditionnelle

## 1. Ce qu'il faut savoir
Sécuriser un réseau repose sur plusieurs mécanismes complémentaires : filtrage
(pare-feu, ACL), segmentation, contrôle d'accès au port, VPN pour les accès distants, et
le principe du moindre privilège.

## 2. Définitions essentielles
- **Pare-feu** (*firewall*) : filtre le trafic réseau selon des règles (adresses, ports,
  protocoles autorisés ou bloqués).
- **ACL** (Access Control List) : liste de règles précises appliquées à une interface
  réseau ou un équipement pour autoriser/bloquer certains flux.
- **802.1X (port security réseau)** : authentification avant d'autoriser un appareil à
  utiliser un port réseau.
- **Port security** (sur switch) : limite/contrôle quelles adresses MAC peuvent utiliser
  un port physique donné.
- **VPN** (Virtual Private Network) : tunnel chiffré permettant un accès distant sécurisé
  à un réseau privé via Internet.
- **DMZ** (zone démilitarisée) : sous-réseau isolé hébergeant les services exposés à
  Internet (serveur web public...), séparé du réseau interne sensible.
- **Moindre privilège** : n'accorder à chaque utilisateur/service QUE les droits
  strictement nécessaires à sa fonction.

## 3. Notions principales
- Un pare-feu et une ACL remplissent un rôle similaire (filtrage) mais à des niveaux
  différents : le pare-feu est souvent un équipement/logiciel dédié, l'ACL une règle
  appliquée directement sur un routeur/switch.
- La segmentation (VLAN, voir MC24) limite la portée d'un incident de sécurité à une seule
  zone du réseau.
- Une DMZ évite qu'un serveur exposé à Internet, s'il est compromis, donne directement
  accès au réseau interne.
- Le VPN chiffre le trafic entre l'utilisateur distant et le réseau de l'entreprise,
  empêchant l'interception en clair sur un réseau public.

## 4. Procédure / méthode
Concevoir une architecture simple sécurisée : réseau interne sensible séparé (VLAN) →
DMZ pour les services publics → pare-feu entre chaque zone avec des règles minimales
(seuls les flux nécessaires autorisés) → VPN pour les accès distants au réseau interne.

## 5. Exemple concret
Un serveur web public compromis ne doit PAS permettre à l'attaquant d'accéder directement
aux postes internes de l'entreprise : le placer en DMZ, séparé par un pare-feu du réseau
interne, limite les dégâts en cas de compromission.

## 6. Pièges fréquents
- Placer un serveur exposé à Internet directement sur le réseau interne.
- Donner des droits larges « au cas où » plutôt qu'appliquer le moindre privilège.
- Confondre chiffrement (VPN) et simple filtrage (pare-feu/ACL) — ce sont deux mécanismes
  différents et complémentaires.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Pare-feu | Firewall |
| Liste de contrôle d'accès | Access control list (ACL) |
| Zone démilitarisée | Demilitarized zone (DMZ) |
| Réseau privé virtuel | Virtual private network (VPN) |

## 8. À retenir pour l'examen
- Pare-feu/ACL = filtrage ; VPN = chiffrement d'un accès distant.
- DMZ isole les services exposés à Internet du réseau interne sensible.
- Toujours appliquer le principe du moindre privilège.
""",
    "MC28": """# Menaces informatiques et protection des postes

## 1. Ce qu'il faut savoir
Un technicien doit reconnaître les menaces courantes (malware, phishing, attaques
réseau) et connaître les mesures de protection de base : mises à jour, sauvegardes,
authentification renforcée.

## 2. Définitions essentielles
- **Malware** : logiciel malveillant en général (virus, ver, cheval de Troie...).
- **Ransomware** (rançongiciel) : chiffre les données de la victime et exige une rançon
  pour les débloquer.
- **Phishing** (hameçonnage) : tentative de tromper l'utilisateur (email, message) pour
  lui voler des identifiants ou l'inciter à exécuter un fichier malveillant.
- **MITM** (Man-In-The-Middle) : un attaquant s'interpose entre deux parties pour
  intercepter ou modifier leurs échanges.
- **Evil Twin** : faux point d'accès Wi-Fi imitant un réseau légitime pour intercepter le
  trafic des victimes qui s'y connectent par erreur.
- **MFA** (authentification multifacteur) : exige plusieurs preuves d'identité (mot de
  passe + code, application, clé physique...) plutôt qu'un seul mot de passe.

## 3. Notions principales
- Le phishing reste le point d'entrée le plus fréquent des attaques (avant toute faille
  technique) : la vigilance humaine est une protection à part entière.
- Un ransomware rend les fichiers inutilisables : la meilleure protection reste une
  sauvegarde régulière, testée, et si possible déconnectée du système infecté (voir
  MC32).
- Le MFA protège même si un mot de passe est volé (via phishing par exemple), car
  l'attaquant ne possède pas le second facteur.
- Les mises à jour corrigent des failles de sécurité connues : un système non mis à jour
  reste vulnérable à des attaques déjà documentées.

## 4. Procédure / méthode
Réagir face à une suspicion de compromission : (1) isoler le poste du réseau (câble/Wi-Fi)
pour limiter la propagation ; (2) ne pas éteindre brutalement si une analyse est prévue
(perte de preuves en mémoire), sauf procédure contraire de l'organisation ; (3) alerter le
responsable/formateur ; (4) restaurer depuis une sauvegarde saine si nécessaire plutôt que
de payer une rançon.

## 5. Exemple concret
Un employé reçoit un email « urgent » de sa banque lui demandant de cliquer sur un lien et
saisir ses identifiants : caractéristiques classiques de phishing (urgence, lien suspect,
demande d'identifiants) — à vérifier via un canal officiel séparé avant toute action,
jamais en cliquant directement sur le lien du message.

## 6. Pièges fréquents
- Croire qu'un antivirus seul suffit à protéger contre toutes les menaces.
- Confondre une synchronisation cloud automatique avec une vraie sauvegarde contre un
  ransomware (un ransomware peut aussi chiffrer les fichiers synchronisés, voir MC04).
- Cliquer sur un lien ou ouvrir une pièce jointe sans vérifier l'expéditeur.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Rançongiciel | Ransomware |
| Hameçonnage | Phishing |
| Authentification multifacteur | Multi-factor authentication (MFA) |
| Mise à jour | Update / patch |

## 8. À retenir pour l'examen
- Phishing = principale porte d'entrée des attaques ; vigilance humaine essentielle.
- MFA protège même si le mot de passe est compromis.
- Face à un ransomware : restaurer depuis une sauvegarde saine, ne jamais compter sur la
  rançon.
""",
    "MC29": """# Dépannage matériel : méthode et pannes courantes

## 1. Ce qu'il faut savoir
Le dépannage matériel suit une méthode d'élimination, du plus simple/probable au plus
complexe, plutôt que de changer des pièces au hasard.

## 2. Définitions essentielles
- **PC mort** : aucune réaction à l'allumage (pas de ventilateur, pas de LED).
- **Pas d'image** : le PC démarre (ventilateurs, LED) mais rien ne s'affiche à l'écran.
- **Configuration minimale** : méthode de dépannage consistant à débrancher tout le
  superflu (périphériques, cartes d'extension non essentielles) pour isoler la panne aux
  composants strictement indispensables.

## 3. Notions principales
- PC mort : suspecter en premier l'alimentation secteur (prise, câble, interrupteur du
  bloc d'alimentation), puis le bloc d'alimentation lui-même, avant de suspecter la carte
  mère.
- Pas d'image : suspecter la RAM (mal insérée, défectueuse), la carte graphique (si
  dédiée), puis la carte mère — un signal sonore (bips) au démarrage oriente souvent
  précisément la cause (voir MC07).
- Surchauffe : un PC qui s'éteint seul sous charge, ou qui devient très bruyant
  (ventilateurs à pleine vitesse), oriente vers un problème de refroidissement (voir
  MC05/MC32).
- La configuration minimale (RAM essentielle, un seul bâton, carte graphique si intégrée
  disponible, débrancher le superflu) permet d'isoler une panne parmi plusieurs
  composants possibles.

## 4. Procédure / méthode
1. Identifier le symptôme précis (mort, pas d'image, redémarrage, surchauffe...).
2. Vérifier l'alimentation (secteur, connecteurs internes, voir MC05).
3. Tester en configuration minimale si le symptôme le justifie.
4. Réinsérer/tester la RAM un bâton à la fois si plusieurs sont présents.
5. Isoler la carte graphique (tester sur la sortie intégrée si disponible).
6. Documenter chaque test effectué et son résultat.

## 5. Exemple concret
Un PC émet des bips répétés au démarrage et n'affiche rien à l'écran : cause très probable
= RAM mal insérée ou défectueuse — réenclencher fermement les barrettes (voir MC05/ESD)
avant de suspecter la carte mère ou le CPU.

## 6. Pièges fréquents
- Changer plusieurs composants à la fois « pour aller plus vite » (rend le diagnostic
  impossible à interpréter).
- Négliger l'alimentation secteur (prise, multiprise) avant de suspecter le matériel
  interne.
- Ignorer les codes sonores/LED du POST qui orientent pourtant précisément le diagnostic.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Panne matérielle | Hardware failure |
| Configuration minimale | Minimal configuration |
| Surchauffe | Overheating |
| Diagnostic | Troubleshooting |

## 8. À retenir pour l'examen
- Toujours tester UN changement à la fois, jamais plusieurs simultanément.
- PC mort → alimentation d'abord ; pas d'image → RAM/GPU en priorité.
- Les bips/codes LED du POST orientent directement le diagnostic (voir MC07).
""",
    "MC30": """# Dépannage Windows et Linux

## 1. Ce qu'il faut savoir
Le dépannage logiciel s'appuie sur les journaux système, l'état des services/pilotes, et
des outils intégrés de réparation (SFC/DISM sous Windows, journalctl/systemctl sous
Linux).

## 2. Définitions essentielles
- **Journal d'événements** (Windows) / **journalctl** (Linux) : historique des
  événements système, utile pour identifier la cause d'un problème après coup.
- **SFC** (System File Checker) : vérifie et répare les fichiers système Windows
  corrompus (`sfc /scannow`).
- **DISM** : répare l'image système Windows elle-même, utilisé quand SFC seul ne suffit
  pas.
- **systemctl** : commande de gestion des services sous Linux moderne (voir MC11).

## 3. Notions principales
- Une lenteur généralisée a souvent plusieurs causes possibles : RAM insuffisante,
  disque presque plein, processus/service qui consomme trop de ressources, ou disque
  proche de la fin de vie (voir MC04/MC10) — le Gestionnaire des tâches / `top` aide à
  identifier le coupable.
- Des fichiers système corrompus peuvent provoquer des erreurs aléatoires ou des
  plantages : `sfc /scannow` tente une réparation automatique ; si l'image système
  elle-même est endommagée, `DISM /Online /Cleanup-Image /RestoreHealth` intervient en
  amont.
- Les journaux (Observateur d'événements / `journalctl`) permettent souvent de retrouver
  l'heure et la cause précise d'un plantage ou d'un redémarrage inattendu.
- Un pilote récemment mis à jour est une cause fréquente d'instabilité soudaine (voir
  MC12) : les journaux aident à corréler l'incident avec l'installation du pilote.

## 4. Procédure / méthode
Diagnostiquer une instabilité système : (1) consulter les journaux autour de l'heure du
problème ; (2) vérifier l'espace disque disponible et l'état SMART (voir MC04) ; (3)
vérifier la consommation mémoire/CPU des processus actifs ; (4) exécuter `sfc /scannow`
(Windows) si des fichiers système sont suspectés ; (5) vérifier les pilotes récemment
modifiés.

## 5. Exemple concret
Un PC redémarre seul de façon aléatoire depuis quelques jours : consulter l'Observateur
d'événements autour des heures de redémarrage révèle souvent une erreur précise
(matérielle, pilote, ou système) plutôt que de réinstaller l'OS par réflexe.

## 6. Pièges fréquents
- Réinstaller le système par réflexe sans avoir consulté les journaux ni tenté une
  réparation ciblée (SFC/DISM).
- Ignorer l'espace disque disponible comme cause possible de lenteur.
- Ne pas corréler un problème récent avec une mise à jour ou une installation de pilote
  récente.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Journal d'événements | Event log |
| Fichier système | System file |
| Processus | Process |
| Service | Service |

## 8. À retenir pour l'examen
- Toujours consulter les journaux avant de conclure sur la cause d'un incident.
- `sfc /scannow` répare les fichiers système ; DISM répare l'image système elle-même.
- Une lenteur généralisée a plusieurs causes possibles : RAM, disque, processus, service.
""",
    "MC31": """# Dépannage réseau méthodique

## 1. Ce qu'il faut savoir
Un problème réseau se diagnostique en suivant un ordre logique, couche par couche, plutôt
qu'au hasard. C'est l'application concrète, en dépannage, des notions vues en MC13 à
MC24.

## 2. Définitions essentielles
- **Méthode physique → application** : progression de vérification, de la couche la plus
  basse (câble, signal) à la plus haute (l'application elle-même), en s'arrêtant dès
  qu'une étape échoue.
- **Commande de test** : outil en ligne de commande utilisé à chaque étape pour vérifier
  objectivement l'état du réseau (`ipconfig`/`ip a`, `ping`, `tracert`/`traceroute`,
  `nslookup`).

## 3. Notions principales — les 6 étapes
1. **Physique** : le câble est-il branché ? le voyant du port réseau/switch est-il
   allumé ? le Wi-Fi est-il activé et connecté au bon SSID ?
2. **IP** : le poste a-t-il une adresse IP cohérente (pas d'APIPA, voir MC16/MC19) ?
   (`ipconfig`/`ip a`)
3. **Passerelle** : la passerelle par défaut répond-elle ? (`ping` de la passerelle,
   voir MC22)
4. **Internet** : une adresse publique connue répond-elle ? (`ping` d'une IP publique
   fixe, pour écarter un problème DNS à ce stade)
5. **DNS** : un nom de domaine se résout-il correctement ? (`ping`/`nslookup` d'un nom,
   voir MC20)
6. **Application** : le service précis répond-il (port ouvert, service actif côté
   serveur, voir MC21) ?

## 4. Procédure / méthode
S'arrêter à la PREMIÈRE étape qui échoue : c'est là que se situe le problème. Ne pas
sauter d'étape ni conclure trop vite : un `ping` de la passerelle qui échoue oriente vers
l'étape IP/passerelle, pas vers un problème applicatif plus haut.

## 5. Exemple concret
Un utilisateur ne peut pas accéder à un site interne. Étape 1 (câble) OK, étape 2 (IP
cohérente) OK, étape 3 (`ping` passerelle) OK, étape 4 (`ping` IP publique) OK, étape 5
(résolution DNS du nom interne) échoue : le problème est isolé au DNS, pas besoin de
vérifier le service applicatif tant que le nom ne se résout pas.

## 6. Pièges fréquents
- Sauter directement à « c'est le serveur qui est en panne » sans avoir vérifié les
  étapes précédentes.
- Tester le DNS/l'application avant d'avoir confirmé la connectivité IP de base.
- Oublier qu'un `ping` qui échoue peut être dû à un pare-feu bloquant ICMP plutôt qu'à une
  vraie coupure (voir MC20).

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Dépannage méthodique | Methodical troubleshooting |
| Test de connectivité | Connectivity test |
| Passerelle | Gateway |
| Résolution de noms | Name resolution |

## 8. À retenir pour l'examen
- Ordre fixe : Physique → IP → Passerelle → Internet → DNS → Application.
- S'arrêter à la première étape qui échoue : c'est là qu'est le problème.
- Toujours s'appuyer sur des commandes de test objectives, pas sur des suppositions.
""",
    "MC32": """# Maintenance préventive et entretien

## 1. Ce qu'il faut savoir
La maintenance préventive vise à éviter les pannes plutôt qu'à les réparer après coup :
nettoyage physique, surveillance des températures, mises à jour régulières, sauvegardes
et suivi d'inventaire.

## 2. Définitions essentielles
- **Maintenance préventive** : ensemble d'actions régulières visant à réduire le risque de
  panne (par opposition à la maintenance curative, qui répare après la panne).
- **Suivi/traçabilité** : enregistrement régulier de l'état du parc informatique
  (interventions, changements, incidents).

## 3. Notions principales
- Nettoyage physique : la poussière accumulée dans les ventilateurs/dissipateurs réduit
  l'efficacité du refroidissement et augmente le risque de surchauffe (voir MC05/MC29).
- Surveillance des températures : un suivi régulier permet de détecter une dérive avant
  qu'elle ne cause une panne (throttling, redémarrage, voir MC29).
- Mises à jour régulières : système, pilotes, firmware — corrigent des failles de sécurité
  et des bugs connus (voir MC28).
- Sauvegardes régulières et testées : condition indispensable pour se remettre rapidement
  d'un incident (panne matérielle, ransomware, voir MC04/MC28), en respectant la règle
  3-2-1 (3 copies, 2 supports différents, 1 copie hors site).
- Inventaire à jour (voir MC34) : facilite la planification du remplacement de matériel
  vieillissant avant panne.

## 4. Procédure / méthode
Plan de maintenance préventive type : (1) nettoyage physique périodique (dépoussiérage) ;
(2) vérification des températures et de l'état SMART des disques ; (3) application des
mises à jour système/pilotes/firmware ; (4) vérification que les sauvegardes s'exécutent
et sont restaurables ; (5) mise à jour de l'inventaire et note des anomalies constatées.

## 5. Exemple concret
Un parc de PC vieux de 5 ans n'a jamais reçu de dépoussiérage : les pannes liées à la
surchauffe augmentent progressivement — un plan de nettoyage régulier aurait limité ce
risque bien avant l'apparition des premières pannes.

## 6. Pièges fréquents
- Ne jamais tester la restauration d'une sauvegarde (une sauvegarde non testée n'est pas
  une garantie).
- Considérer la maintenance préventive comme optionnelle « tant que ça marche ».
- Ne pas documenter les interventions, rendant le suivi impossible dans le temps.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Maintenance préventive | Preventive maintenance |
| Maintenance curative | Corrective maintenance |
| Sauvegarde | Backup |
| Suivi / traçabilité | Tracking |

## 8. À retenir pour l'examen
- Maintenance préventive = éviter la panne ; maintenance curative = réparer après coup.
- Règle de sauvegarde 3-2-1 : 3 copies, 2 supports, 1 copie hors site.
- Une sauvegarde non testée n'est pas une garantie fiable.
""",
    "MC33": """# Partage de ressources, comptes, droits et permissions

## 1. Ce qu'il faut savoir
Partager des dossiers et imprimantes sur un réseau nécessite de gérer correctement
comptes, groupes et permissions, pour que chacun ait accès à ce dont il a besoin, sans
plus.

## 2. Définitions essentielles
- **Partage** : mise à disposition d'une ressource (dossier, imprimante) sur le réseau
  pour d'autres utilisateurs.
- **Compte utilisateur** : identité individuelle permettant de se connecter et d'accéder
  à des ressources.
- **Groupe** : ensemble de comptes utilisateurs, permettant de gérer les droits
  collectivement plutôt qu'un par un.
- **Droits NTFS** : permissions appliquées directement sur les fichiers/dossiers au
  niveau du système de fichiers (lecture, écriture, modification, contrôle total...).
- **Droits de partage** : permissions appliquées au niveau du partage réseau lui-même,
  qui s'ajoutent (et se combinent, la plus restrictive l'emportant) aux droits NTFS.

## 3. Notions principales
- Un utilisateur accédant à un dossier partagé via le réseau est soumis aux DEUX niveaux
  de droits (partage ET NTFS) ; le résultat effectif est toujours le plus restrictif des
  deux.
- Utiliser des groupes plutôt que d'attribuer des droits individuellement à chaque
  utilisateur facilite grandement la gestion (ajout/suppression d'un membre du groupe
  plutôt que reconfiguration de chaque ressource).
- Bonne pratique : appliquer le principe du moindre privilège (voir MC27) — chaque groupe
  n'a accès qu'aux ressources dont il a réellement besoin.
- Partage d'imprimante : fonctionne sur le même principe (droits d'utilisation, de gestion
  des documents, d'administration de l'imprimante).

## 4. Procédure / méthode
Mettre en place un partage sécurisé : (1) créer/identifier le groupe concerné ; (2)
créer le partage réseau du dossier ; (3) définir les droits de partage (généralement
larges, ex. Lecture/Écriture pour le groupe autorisé) ; (4) définir les droits NTFS plus
précis sur le dossier lui-même ; (5) vérifier que le résultat combiné correspond au besoin
réel.

## 5. Exemple concret
Un utilisateur a accès en Lecture/Écriture au niveau du partage réseau, mais ne peut
pourtant que lire les fichiers sans les modifier : cause probable = droits NTFS plus
restrictifs (Lecture seule) sur le dossier lui-même, qui l'emportent sur les droits de
partage plus larges.

## 6. Pièges fréquents
- Attribuer des droits individuellement à chaque utilisateur plutôt qu'à des groupes.
- Oublier que le droit effectif combine partage ET NTFS (le plus restrictif gagne).
- Donner un accès trop large « pour éviter les problèmes » plutôt qu'appliquer le moindre
  privilège.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Partage | Share |
| Groupe | Group |
| Droits d'accès | Permissions |
| Contrôle total | Full control |

## 8. À retenir pour l'examen
- Droit effectif sur un partage réseau = combinaison des droits de partage ET NTFS (le
  plus restrictif l'emporte).
- Gérer les droits par groupe, pas individuellement.
- Appliquer le principe du moindre privilège.
""",
    "MC34": """# Inventaire matériel et gestion simple des ressources

## 1. Ce qu'il faut savoir
Tenir un inventaire à jour du parc informatique permet de suivre l'état, la localisation
et le cycle de vie de chaque poste/composant, et facilite la planification et le support.

## 2. Définitions essentielles
- **Inventaire** : liste structurée et à jour de tout le matériel géré (postes,
  composants, périphériques).
- **Numéro de série** : identifiant unique gravé/étiqueté par le fabricant, indispensable
  pour le suivi, la garantie et le support.
- **État** : statut d'un équipement (en service, en réparation, en stock, à réformer).
- **Base de données simple** : structure organisée (tableur ou outil dédié) avec des
  champs cohérents (identifiant, type, modèle, numéro de série, état, localisation,
  utilisateur assigné, date d'acquisition).

## 3. Notions principales
- Un inventaire utile contient au minimum : identifiant unique, type d'équipement,
  modèle, numéro de série, état, localisation/utilisateur, date d'acquisition.
- Le suivi des numéros de série est indispensable en cas de panne (garantie fabricant) ou
  de vol/perte (déclaration, assurance).
- Un inventaire à jour facilite la planification du remplacement du matériel vieillissant
  (voir MC32) avant qu'il ne tombe réellement en panne.
- Les principes de base d'une organisation en tableau/base de données (une ligne = un
  équipement, des colonnes cohérentes, des identifiants uniques) évitent les doublons et
  incohérences.

## 4. Procédure / méthode
Mettre à jour l'inventaire lors d'une intervention : (1) identifier l'équipement (numéro
de série, étiquette d'inventaire) ; (2) noter l'intervention effectuée et la date ; (3)
mettre à jour l'état si nécessaire (ex. passage « en réparation » → « en service ») ; (4)
vérifier la cohérence des autres champs (localisation, utilisateur assigné).

## 5. Exemple concret
Un PC signalé en panne ne peut pas être identifié précisément faute de numéro
d'inventaire relevé lors de son installation : un inventaire à jour dès la mise en
service aurait évité cette perte de temps et permis de vérifier immédiatement sa garantie.

## 6. Pièges fréquents
- Ne mettre à jour l'inventaire qu'occasionnellement, le rendant rapidement obsolète.
- Oublier de relever le numéro de série lors de la mise en service d'un équipement.
- Dupliquer des identifiants ou laisser des champs incohérents dans la base.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Inventaire | Inventory |
| Numéro de série | Serial number |
| État (d'un équipement) | Asset status |
| Base de données | Database |

## 8. À retenir pour l'examen
- Un inventaire utile suit : identifiant, modèle, numéro de série, état, localisation,
  utilisateur, date.
- Le numéro de série est indispensable pour la garantie et le suivi en cas de perte/vol.
- Mettre à jour l'inventaire à CHAQUE intervention, pas occasionnellement.
""",
    "MC35": """# Ergonomie, sécurité, environnement et confidentialité

## 1. Ce qu'il faut savoir
Le métier de technicien PC-réseaux implique des responsabilités au-delà du strict
technique : sécurité physique/électrique, ergonomie du poste de travail, respect de
l'environnement, et confidentialité des données rencontrées.

## 2. Définitions essentielles
- **Risque électrique** : danger lié à la manipulation de matériel sous tension ou mal
  isolé (voir MC05).
- **Risque incendie** : danger lié à la surchauffe, aux courts-circuits, ou au stockage
  inapproprié de matériel/batteries.
- **Ergonomie** : aménagement du poste de travail pour limiter la fatigue physique
  (posture, hauteur d'écran, éclairage...).
- **Pictogramme de sécurité** : symbole normalisé signalant un risque (tension électrique,
  matière inflammable...) ou une consigne (protection obligatoire...).
- **DEEE** (Déchets d'Équipements Électriques et Électroniques) : matériel informatique en
  fin de vie, soumis à une filière de recyclage spécifique — ne se jette jamais avec les
  déchets ordinaires.
- **Confidentialité des données** : obligation de protéger les informations personnelles
  ou sensibles rencontrées lors d'une intervention (documents, fichiers clients...).

## 3. Notions principales
- Les pictogrammes de sécurité doivent être reconnus et respectés (tension, chaleur,
  matière inflammable, protection obligatoire).
- Le matériel informatique en fin de vie (DEEE) doit être collecté via une filière dédiée,
  jamais jeté avec les déchets ménagers, en raison de composants polluants (piles,
  certains composants électroniques).
- Un technicien intervenant chez un client/employeur a accès à des données potentiellement
  sensibles (documents, emails, fichiers clients) : il doit s'abstenir de les consulter
  au-delà de ce que nécessite l'intervention, et ne jamais les divulguer.
- Ergonomie de base : écran à hauteur des yeux, avant-bras horizontaux au clavier, pauses
  régulières lors d'un travail prolongé sur écran.

## 4. Procédure / méthode
Avant une intervention chez un client : (1) identifier les risques physiques/électriques
du poste de travail ; (2) respecter les consignes de sécurité affichées (pictogrammes) ;
(3) limiter l'accès aux données au strict nécessaire à l'intervention ; (4) orienter le
matériel remplacé vers la filière DEEE appropriée.

## 5. Exemple concret
En remplaçant un disque dur défectueux chez un client, le technicien découvre des
documents personnels : il ne doit ni les consulter au-delà de ce qui est nécessaire au
diagnostic, ni les mentionner à des tiers — la confidentialité s'applique même sur du
matériel en panne.

## 6. Pièges fréquents
- Jeter un vieux PC ou une batterie avec les déchets ménagers ordinaires.
- Ignorer les pictogrammes de sécurité affichés sur le matériel ou le lieu
  d'intervention.
- Consulter ou divulguer des données personnelles rencontrées lors d'une intervention.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Risque électrique | Electrical hazard |
| Déchet électronique | E-waste (WEEE) |
| Confidentialité | Confidentiality |
| Ergonomie | Ergonomics |

## 8. À retenir pour l'examen
- Le matériel informatique en fin de vie suit la filière DEEE, jamais la poubelle
  classique.
- La confidentialité des données rencontrées s'applique en toutes circonstances.
- Respecter systématiquement les pictogrammes de sécurité.
""",
    "MC36": """# Communication client et rapport technique

## 1. Ce qu'il faut savoir
Un bon technicien sait aussi communiquer : poser les bonnes questions à un client non
technique, expliquer simplement, et rédiger une fiche d'intervention claire et utile.

## 2. Définitions essentielles
- **Fiche d'intervention** : document qui résume le problème signalé, le diagnostic
  effectué, les actions réalisées et le résultat, pour traçabilité et suivi.
- **Rapport technique** : compte-rendu, écrit ou oral, de l'intervention, adapté au
  destinataire (client non technique vs collègue technicien).
- **Reformulation** : technique consistant à reformuler ce que dit le client pour vérifier
  qu'on a bien compris le problème avant d'intervenir.

## 3. Notions principales
- Face à un client non technique, éviter le jargon (ou l'expliquer immédiatement en
  termes simples) : préférer « votre ordinateur ne se connecte plus à Internet » à
  « échec de résolution DNS ».
- Bien questionner un client permet souvent d'orienter le diagnostic avant même
  d'intervenir techniquement : depuis quand, sur quels appareils, qu'est-ce qui a changé
  récemment (nouvelle installation, mise à jour, déménagement de matériel...).
- Une fiche d'intervention doit être compréhensible par un AUTRE technicien qui n'était
  pas présent : problème signalé, diagnostic, actions effectuées, résultat, éventuelles
  recommandations.
- Le vocabulaire technique FR/EN doit être maîtrisé pour lire la documentation (souvent en
  anglais) et l'expliquer en français au client.

## 4. Procédure / méthode
Structurer une fiche d'intervention : (1) description du problème signalé par le client
(dans ses propres mots) ; (2) constats/diagnostic technique effectués ; (3) actions
réalisées ; (4) résultat final (résolu / à suivre) ; (5) recommandations éventuelles pour
éviter que le problème ne se reproduise.

## 5. Exemple concret
Un client dit simplement « mon ordinateur est lent » : de bonnes questions
complémentaires (depuis quand ? tout le temps ou par moments ? après quel événement ?)
permettent d'orienter le diagnostic (RAM, disque, processus, voir MC29/MC30) avant même
d'ouvrir le PC.

## 6. Pièges fréquents
- Utiliser du jargon technique non expliqué face à un client non technique.
- Rédiger une fiche d'intervention trop vague pour être utile à un collègue.
- Ne pas reformuler le problème du client avant de conclure trop vite sur la cause.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Fiche d'intervention | Service report / work order |
| Rapport | Report |
| Reformulation | Rephrasing |
| Diagnostic | Diagnosis |

## 8. À retenir pour l'examen
- Adapter le vocabulaire à l'interlocuteur (client non technique vs collègue).
- Une bonne fiche d'intervention doit être compréhensible par un autre technicien.
- Bien questionner le client oriente souvent le diagnostic avant toute intervention.
""",
    "MC37": """# Laboratoire intégrateur PC + réseau

## 1. Ce qu'il faut savoir
Ce mini-cours mobilise ensemble les compétences des blocs précédents (matériel,
systèmes, réseau, Wi-Fi, sécurité, dépannage) dans un scénario complet et réaliste, avec
des pannes volontairement introduites à résoudre.

## 2. Définitions essentielles
- **Scénario intégrateur** : mise en situation combinant plusieurs domaines (montage,
  installation OS, câblage, adressage IP, partage, Wi-Fi, sécurité) plutôt qu'un exercice
  isolé sur un seul sujet.
- **Panne volontaire** (*fault injection*) : problème délibérément introduit dans un
  scénario pédagogique pour exercer la méthode de diagnostic (voir MC29/MC31).

## 3. Notions principales — ce que combine un scénario type
- **Matériel** : montage/vérification d'un poste (voir MC06).
- **Système** : installation ou configuration d'un OS (voir MC09/MC10/MC11).
- **Câblage** : sertissage/vérification d'un câble RJ45 (voir MC15).
- **Adressage IP** : configuration cohérente d'IP/masque/passerelle, éventuellement
  sous-réseau dédié (voir MC16 à MC18).
- **Partage** : mise en place d'un partage de dossier/imprimante avec droits appropriés
  (voir MC33).
- **Wi-Fi** : connexion et sécurisation d'un point d'accès (voir MC25/MC26).
- **Sécurité** : application de mesures de base (pare-feu, moindre privilège, voir
  MC27/MC28).
- **Pannes volontaires** : un ou plusieurs éléments du scénario sont délibérément mal
  configurés ou en panne, à identifier et corriger par une démarche méthodique.

## 4. Procédure / méthode
Face à un scénario intégrateur : (1) prendre connaissance de l'ensemble du contexte avant
d'agir ; (2) vérifier chaque brique dans un ordre logique (matériel → système → réseau
physique → adressage → services → sécurité) ; (3) appliquer la méthode de dépannage
adaptée à chaque symptôme rencontré (voir MC29 pour le matériel, MC31 pour le réseau,
MC30 pour le système) ; (4) documenter les pannes trouvées et les corrections apportées
(voir MC36).

## 5. Exemple concret
Un scénario présente un poste qui « ne voit pas le partage réseau » : la cause peut être
matérielle (câble, voir MC15), réseau (adressage incohérent, voir MC16/MC18), ou logicielle
(droits de partage insuffisants, voir MC33) — un scénario intégrateur entraîne
spécifiquement à ne pas se précipiter sur la première hypothèse venue.

## 6. Pièges fréquents
- Se concentrer sur un seul domaine (ex. réseau) en ignorant qu'un scénario intégrateur
  peut combiner plusieurs pannes de natures différentes.
- Corriger un symptôme sans avoir identifié sa cause réelle.
- Ne pas documenter la démarche suivie, rendant la correction difficile à vérifier.

## 7. Vocabulaire FR / EN
| FR | EN |
|---|---|
| Scénario intégrateur | Integrative scenario |
| Panne volontaire | Injected fault |
| Démarche méthodique | Methodical approach |
| Documentation d'intervention | Service documentation |

## 8. À retenir pour l'examen
- Un scénario intégrateur combine plusieurs domaines : ne jamais se limiter au premier
  indice trouvé.
- Suivre un ordre logique de vérification : matériel → système → réseau → services →
  sécurité.
- Toujours documenter la démarche et les corrections apportées.
""",
}


MC38_COURSE_MARKDOWN = """# Révision finale et examen blanc AMPCR

## Ce que couvre ce mini-cours

MC38 ne porte pas sur une matière technique propre : c'est la **synthèse transversale**
de tout le programme AMPCR (MC01 à MC37). Il n'ajoute aucune notion nouvelle — il
réutilise et recombine ce qui a déjà été vu dans les mini-cours précédents.

## Comment fonctionnent S'entraîner et S'évaluer pour MC38

- **S'entraîner (practice)** : chaque session pioche 10 questions **directement dans les
  mini-cours MC01 à MC37** (banque existante et génération bornée à ces mêmes mini-cours),
  en visant plusieurs catégories du programme (Hardware, Systèmes, Réseaux, Wi-Fi,
  Sécurité, Dépannage, Métier) plutôt qu'une seule.
- **S'évaluer (examen blanc)** : même principe, sur 20 questions, avec une répartition
  volontairement plus large entre catégories pour se rapprocher d'un vrai examen de
  qualification.
- Les questions posées sont donc des questions **techniques réelles** (subnetting,
  dépannage, sécurité Wi-Fi, partage de ressources...), jamais des questions sur la
  manière de réviser, sur l'organisation de l'étude, ou sur le fonctionnement du site.

## Comment l'utiliser efficacement

1. Avoir déjà pratiqué individuellement les mini-cours qui posent le plus de difficulté
   (MC01 à MC37) avant d'utiliser MC38 — MC38 sert à vérifier et consolider, pas à
   découvrir une matière pour la première fois.
2. Utiliser plusieurs sessions d'entraînement MC38 successives : chaque session ne peut
   pas couvrir tout le programme en 10 questions, mais plusieurs sessions permettent de
   couvrir une bonne partie des catégories dans le temps.
3. Réserver l'examen blanc (20 questions) pour une mise en conditions proches de
   l'épreuve réelle, une fois les mini-cours individuels déjà travaillés.
4. Après correction, revenir spécifiquement au mini-cours concerné (MC01 à MC37) en cas
   d'erreur, pour retravailler la notion précise plutôt que de refaire uniquement MC38.

## MC37 : le laboratoire intégrateur

MC37 (Laboratoire intégrateur PC + réseau) est particulièrement représentatif d'un examen
de qualification : il combine plusieurs domaines dans un même scénario. Les questions de
MC38 peuvent naturellement s'appuyer sur ce type de mise en situation transversale.

## À retenir

- MC38 = entraînement et examen **transversaux** sur MC01 à MC37, jamais une nouvelle
  matière en soi.
- Les questions restent toujours des questions d'informatique AMPCR concrètes.
- Travailler d'abord les mini-cours individuels, puis utiliser MC38 pour consolider et se
  mettre en situation d'examen.
"""

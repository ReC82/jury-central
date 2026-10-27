# Changelog

Historique des tranches livrées. Format : date, résumé, détail technique bref.

## 2026-10-27 — AMPCR pratique écrite : examen blanc global avancé EX06 « Examen blanc global avancé — dossiers complexes » (ticket #234)

UAA EX06 du module `AMPCR-PRATIQUE` (position 30, après EX05, 13 blocs : présentation, barème et
couverture comparée avec EX05, documents communs et dossiers A à D des deux variantes, méthode,
sources). 12 situations à réponse libre (8 ou 9 points, /100) sur quatre dossiers complexes ;
2 variantes de données vérifiées par les règles des cours ; 4 schémas SVG sans verdict
(`app/static/img/ampcr-pratique/ex06-v*-plan-{reseau,wifi}.svg`) ; réserve `exam` seule.
Moteur : `exam_variant_length` (`app/v1/ampcr_pratique_bank.py`) ; `session_length_options`
(`app/v1/session_service.py`) propose la longueur d'une variante pour un examen à variantes
(`app/v1/ampcr_pratique_ex06_*.py`, `tests/test_ticket234_ampcr_pratique_ex06.py`).

## 2026-10-27 — AMPCR pratique écrite : examen blanc global EX05 « Examen blanc global standard — épreuve pratique écrite » (ticket #201)

UAA EX05 du module `AMPCR-PRATIQUE` (position 30, après PR30, 9 blocs : présentation et barème,
dossier et questions des deux variantes, méthode, sources). Dossier d'une entreprise fictive de
6 postes, 10 situations de 10 points (/100) à réponse libre couvrant matériel, systèmes, câblage
RJ45/BNC, réseau et rapport ; 2 variantes de données vérifiées par les règles des cours ; 2 schémas
SVG sans verdict (`app/static/img/ampcr-pratique/ex05-v*-plan-reseau.svg`) ; réserve `exam` seule.
Moteur : `PracticalCourse.variants`, `select_exam_variant` et `has_exam_variants`
(`app/v1/ampcr_pratique_bank.py`), branchés dans `start_session` et `available_session_lengths`
(`app/v1/session_service.py`) ; repère « Variante n » dans `app/v1/prompt_layout.py`
(`app/v1/ampcr_pratique_ex05_*.py`, `tests/test_ticket201_ampcr_pratique_ex05.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR30 « Grand laboratoire écrit — installation et dépannage d'un réseau complet » (ticket #229)

Cours PR30 du parcours pratique (UAA PR30 du module `AMPCR-PRATIQUE`, position 30, après PR29,
16 blocs) : dossier intégrateur d'une PME fictive (2 salles, 6 postes Windows/Linux, switch, box,
point d'accès, imprimante, serveur de fichiers) ; inventaire, contraintes, budget indicatif par
postes de dépense sans prix ; câblage T568B, baie, repérage, recette des liens ; plan IPv4,
DHCP, DNS, VLAN invités ; groupe de travail ou domaine selon le scénario, comptes, groupes,
partages, matrice des droits ; installation Windows 11 Pro et Ubuntu 24.04 LTS ; panne
matérielle (mémoire) et logicielle (identifiant enregistré) ; Wi-Fi et sécurité ; recette,
verdict avec réserve, rapport en 14 rubriques ; 8 études de cas graduées et corrigées, reliées
aux exigences AP-xx ; 4 procédures, 10 figures SVG + 2 schémas à compléter
(`app/static/img/ampcr-pratique/pr30-*.svg`) ; 23 exercices, mini-examen 10 questions /20 sans
génération IA (`app/v1/ampcr_pratique_pr30_*.py`, `tests/test_ticket229_ampcr_pratique_pr30.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR29 « Contrôles finaux et rapport professionnel d'intervention » (ticket #228)

Cours PR29 du parcours pratique (UAA PR29 du module `AMPCR-PRATIQUE`, position 29, après PR28,
15 blocs) : critères d'acceptation avant / après (atteint, non atteint, non concluant ; verdict) ;
six familles de contrôles finaux et contrôles exigés par type d'intervention ; journal des
opérations et tests reproductibles ; retour arrière, restauration, réserve ; compte rendu en
14 rubriques (identité non sensible, demande, symptômes, hypothèses, relevés, tests, résultats,
action, pièces, validation, risques résiduels, recommandation, signature) ; vocabulaire,
confidentialité, communication au client, escalade, documentation ; 5 rapports modèles complets ;
4 procédures, 11 figures SVG + 2 schémas à compléter ; 3 formulaires A4 imprimables
(`app/static/print/ampcr-pratique/pr29-*.html`) ; 22 exercices, mini-examen 10 questions /20 sans
génération IA (`app/v1/ampcr_pratique_pr29_*.py`, `tests/test_ticket228_ampcr_pratique_pr29.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR28 « Outillage, sécurité et protection des données » (ticket #227)

Cours PR28 du parcours pratique (UAA PR28 du module `AMPCR-PRATIQUE`, position 28, après PR27,
15 blocs) : inventaire de l'outillage PC et réseau (usage, précaution, kit par intervention) ;
ESD selon la procédure, électricité, bloc jamais ouvert, débranchement ; batteries endommagées,
ventilation, risques mécaniques, laser et éclats de fibre, poste de travail ; données du client
(intégrité par empreintes SHA-256, confidentialité, chiffrement BitLocker et clé de récupération,
droits) ; règle 3-2-1 (complément) et prérequis avant effacement ou réinstallation ; filières de
fin de vie (DEEE, piles et batteries, supports de données) ; fiche sécurité, liste de contrôle,
gestion d'incident ; 5 interventions résolues ; 5 procédures, 14 figures SVG + 2 schémas à
compléter (`app/static/img/ampcr-pratique/pr28-*.svg`) ; 22 exercices, mini-examen 10 questions
/20 sans génération IA (`app/v1/ampcr_pratique_pr28_*.py`,
`tests/test_ticket227_ampcr_pratique_pr28.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR27 « Construire et justifier une procédure de diagnostic » (ticket #226)

Cours PR27 du parcours pratique (UAA PR27 du module `AMPCR-PRATIQUE`, position 27, après PR26,
15 blocs) : cycle hypothèse → test discriminant → résultat attendu → interprétation → action →
validation ; du moins au plus invasif (échelle 0 à 5 du cours), mesure d'impact et sécurité ;
approche par couches et isolation de variables ; test croisé, test négatif, faux positifs et
faux négatifs ; contrôle de configuration, journaux, conditions de reproduction ; 4 arbres de
décision (matériel, démarrage, système, réseau) ; conservation de preuves et plan de retour
arrière ; alternatives et escalade ; 6 dossiers entièrement résolus (démarrage, périphérique,
DHCP, DNS, partage, panne intermittente) ; 4 procédures, 12 figures SVG + 2 schémas à compléter
(`app/static/img/ampcr-pratique/pr27-*.svg`) ; 23 exercices dont 8 procédures à ordonner et
justifier, mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr27_*.py`,
`tests/test_ticket226_ampcr_pratique_pr27.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR26 « Analyser une demande d'intervention technique » (ticket #225)

Cours PR26 du parcours pratique (UAA PR26 du module `AMPCR-PRATIQUE`, position 26, après EX04,
16 blocs) : recueil de la demande, symptômes et interprétation ; contexte matériel / logiciel /
réseau, inventaire et références, date, changements récents, utilisateurs touchés ; observation
ou hypothèse, panne reproductible ou intermittente ; impact, urgence et priorisation (matrice du
cours) ; sauvegarde, consentement, confidentialité, risques et autorisation ; questions utiles et
reformulation ; fiche d'incident, vocabulaire technique et grille d'évaluation sur 20 ; critères
de réussite, plan d'action et estimation ; escalade ; 5 dossiers entièrement corrigés ;
3 procédures, 7 figures SVG + 2 schémas à compléter (`app/static/img/ampcr-pratique/pr26-*.svg`) ;
20 exercices, mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr26_*.py`,
`tests/test_ticket225_ampcr_pratique_pr26.py`).

## 2026-10-27 — AMPCR pratique écrite : examen blanc EX04 « réseau, configuration et dépannage » (ticket #233)

Quatrième examen blanc du parcours pratique (UAA EX04 du module `AMPCR-PRATIQUE`, après PR25, 7
blocs), même modèle que EX01–EX03 : 10 questions /100 à réponse libre — plan de réseau (topologie,
couches, domaines, trames, NetBEUI), calculs IPv4/CIDR et MAC, connexion directe, plan d'adressage
d'un mini-réseau, DNS contre connectivité IP, route manquante et DHCP épuisé, panne Internet et
rapport, Wi-Fi (sécurité, canal, répéteur), partages et NTFS, imprimante et SMB ; 3 schémas sans
verdict ; aucune génération IA (`app/v1/ampcr_pratique_ex04_*.py`,
`tests/test_ticket233_ampcr_pratique_ex04.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR25 « Wi-Fi : configuration, couverture, sécurité et diagnostic » (ticket #224)

Cours PR25 du parcours pratique, vingt-cinquième dans l'ordre pédagogique (UAA PR25 du module
`AMPCR-PRATIQUE`, position 25, après PR24, 16 blocs) : architecture (point d'accès, client,
routeur, répéteur, mesh, SSID/BSSID) ; normes 802.11 et bandes 2,4/5/6 GHz ; canaux, largeur et
interférences ; portée, obstacles, débit réel, répéteur et roaming ; association,
authentification, DHCP, DNS ; sécurité WEP/WPA-TKIP obsolètes, WPA2 AES-CCMP, WPA3 SAE, Personnel
ou Entreprise 802.1X/RADIUS, WPS, mot de passe fort, invités isolés ; configuration d'un point
d'accès ; diagnostics réseau invisible, mauvaise clé, mauvaise IP, connecté sans Internet,
interférence, répéteur mal placé ; 3 procédures, 13 figures SVG + 4 schémas à compléter (fichiers
statiques `app/static/img/ampcr-pratique/pr25-*.svg`) ; 5 cas résolus, 20 exercices, mini-examen
10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr25_*.py`,
`tests/test_ticket224_ampcr_pratique_pr25.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR23 « Partage de dossiers, imprimantes et permissions » (ticket #223)

Cours PR23 du parcours pratique, vingt-troisième dans l'ordre pédagogique (UAA PR23 du module
`AMPCR-PRATIQUE`, position 23, après PR22, avant PR24, 16 blocs) : partages SMB et chemins UNC ;
profil réseau, découverte, pare-feu et authentification ; permissions de partage et NTFS ;
combinaison effective, héritage et groupes ; Linux Samba, rwx et ACL ; imprimantes partagées
(file d'attente, pilotes, hôte) ; diagnostics « ping OK mais accès refusé », nom introuvable,
droits insuffisants, imprimante hors connexion ; protection des données et moindre privilège ;
3 procédures, 12 figures SVG + 4 schémas à compléter (fichiers statiques
`app/static/img/ampcr-pratique/pr23-*.svg`) ; 5 cas résolus, 20 exercices, mini-examen
10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr23_*.py`,
`tests/test_ticket223_ampcr_pratique_pr23.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR22 « Domaine, groupe de travail, comptes et groupes » (ticket #222)

Cours PR22 du parcours pratique, vingt-deuxième dans l'ordre pédagogique (UAA PR22 du module
`AMPCR-PRATIQUE`, position 22, après PR21, 16 blocs) : groupe de travail et comptes locaux ;
domaine Active Directory (contrôleur, DNS, Kerberos, comptes d'ordinateurs) ; domaine DNS et
domaine d'administration, noms de connexion ; jonction ; comptes et groupes, stratégies ; mots de
passe, moindre privilège, désactivation ; dépannage réseau/DNS/heure/compte/droits ;
organisations de 3 à 20 postes ; 3 procédures, 11 figures SVG + 4 schémas à compléter (fichiers
statiques `app/static/img/ampcr-pratique/pr22-*.svg`) ; 5 cas résolus, 20 exercices, mini-examen
10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr22_*.py`,
`tests/test_ticket222_ampcr_pratique_pr22.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR21 « Connexion directe de deux PC et mini-réseau » (ticket #221)

Cours PR21 du parcours pratique, vingt et unième dans l'ordre pédagogique (UAA PR21 du module
`AMPCR-PRATIQUE`, position 21, après PR20, 16 blocs) : carte réseau, câble droit ou croisé et
Auto MDI-X, voyants ; adresses statiques 192.168.10.1/24 et .2/24 sans passerelle ; ping, ARP et
pare-feu (profil réseau) ; partage et permissions ; extension à 3–6 PC via un switch ; DHCP ou
statique, box (passerelle, DNS), plan d'adressage ; erreurs liaison, DHCP, doublon, masque ;
mise en service et recette ; 3 procédures, 12 figures SVG + 4 schémas à compléter (fichiers
statiques `app/static/img/ampcr-pratique/pr21-*.svg`) ; 5 cas résolus, 20 exercices, mini-examen
10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr21_*.py`,
`tests/test_ticket221_ampcr_pratique_pr21.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR19 « Topologies, OSI, TCP/IP, NetBEUI et équipements » (ticket #220)

Cours PR19 du parcours pratique, dix-neuvième dans l'ordre pédagogique (UAA PR19 du module
`AMPCR-PRATIQUE`, position 19, après PR18, 16 blocs) : topologies et pannes ; OSI et TCP/IP ;
encapsulation et trame Ethernet ; MAC, ARP, IP, ports TCP/UDP ; protocole, service, équipement ;
NetBEUI non routable ; hub, répéteur, pont, switch, point d'accès, routeur, passerelle, modem ;
domaines de collision et de diffusion, VLAN ; chemin d'un paquet ; diagnostic par couche ;
3 procédures, 10 figures SVG + 6 schémas à compléter (fichiers statiques
`app/static/img/ampcr-pratique/pr19-*.svg`) ; 5 cas résolus, 20 exercices, mini-examen
10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr19_*.py`,
`tests/test_ticket220_ampcr_pratique_pr19.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR18 « Installation physique d'un mini-réseau » (ticket #219)

Cours PR18 du parcours pratique, dix-huitième dans l'ordre pédagogique (UAA PR18 du module
`AMPCR-PRATIQUE`, position 18, après PR17 et EX03, 18 blocs) : besoin et plan des locaux ;
étoile et implantation (baie, box, point d'accès, prises, chemins) ; choix du support ;
longueurs, cheminement, repérage ; séparation du courant fort ; baie, panneau, keystones ; PoE ;
plan de câblage, nomenclature, devis (TVA 21 %) ; tests et certification ; configuration de base
et validation ; documentation et recette ; 3 procédures, 8 figures SVG + 5 schémas à compléter
(fichiers statiques `app/static/img/ampcr-pratique/pr18-*.svg`) ; 5 cas résolus, 20 exercices,
mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr18_*.py`,
`tests/test_ticket219_ampcr_pratique_pr18.py`).

## 2026-10-27 — AMPCR pratique écrite : examen blanc EX03 « câblage RJ45, BNC et fibre » (ticket #232)

Troisième examen blanc du parcours pratique (UAA EX03 du module `AMPCR-PRATIQUE`, après PR17, 7
blocs), même modèle que EX01/EX02 : 10 questions /100 à réponse libre — fiche RJ45 à contrôler et
brochages T568A/B, droit/croisé/Auto MDI-X, choix des câbles (catégorie, blindage, coaxial 75 Ω,
fibre), rapport de test des liens, relevé de pose et fabrication d'un cordon, bus 10BASE2 et
réflexion, ohmmètre, BNC et 10BASE5, choix fibre/modules/jarretières, bilan et photométrie, panne
au réflectomètre ; 4 schémas sans verdict ; aucune génération IA (`app/v1/ampcr_pratique_ex03_*.py`,
`tests/test_ticket232_ampcr_pratique_ex03.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR17 « Fibre optique — choix, raccordement et diagnostic » (ticket #218)

Dix-neuvième cours du parcours pratique et dix-septième dans l'ordre pédagogique (UAA PR17 du
module `AMPCR-PRATIQUE`, position 17, après PR16, 18 blocs) : lumière guidée ; monomode ou
multimode, OM/OS, portée selon le module ; LC/SC, UPC/APC ; SFP/SFP+, TX/RX, polarité ; pertes
et puissance reçue ; épissure, pigtail, tiroir, brassage ; rayon de courbure ; comparaison avec
le cuivre et le coaxial ; propreté, photométrie, OTDR ; sécurité laser et éclats ; diagnostic ;
3 procédures, 9 figures SVG ; 5 cas résolus, 18 exercices, mini-examen 10 questions /20 sans
génération IA (`app/v1/ampcr_pratique_pr17_*.py`, `tests/test_ticket218_ampcr_pratique_pr17.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR14 « Débits, distances, atténuation et impédance » (ticket #217)

Dix-huitième cours du parcours pratique et quatorzième dans l'ordre pédagogique (UAA PR14 du
module `AMPCR-PRATIQUE`, position 14, après PR13, 16 blocs) : bits, octets, préfixes ; durée d'une
copie, débit utile et nominal ; Ethernet 10/100/1000/10G (canal 100 m, Cat6 à 10 Gb/s ≤ 55 m),
10BASE2 185 m, 10BASE5 500 m ; dB ; bruit, NEXT, ACR, blindage ; impédance et réflexions ;
fibre, pertes, portée selon le module, bilan ; duplex, auto-négociation, collisions ; liaison à
100 Mb/s au lieu de 1 Gb/s ; 3 procédures, 9 figures SVG ; 5 cas chiffrés, 19 exercices,
mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr14_*.py`,
`tests/test_ticket217_ampcr_pratique_pr14.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose » (ticket #216)

Dix-septième cours du parcours pratique et treizième dans l'ordre pédagogique (UAA PR13 du module
`AMPCR-PRATIQUE`, position 13, après EX02, 16 blocs) : 4 paires torsadées, torsade, diaphonie,
parasites, atténuation, catégorie ; X/YTP (U/UTP, F/UTP, U/FTP, S/FTP) et noms historiques ;
continuité de l'écran et mise à la terre ; Cat5e/6/6A, monobrin/multibrin, marquage ; 8P8C,
prises, cordons, baie ; coaxial 50/75 Ω, 10BASE2, vidéo ; règle de choix ; pose (EN 50174-2,
rayon 4/8 × Ø, 110 N), longueurs, repérage, tests ; 2 procédures, 9 figures SVG ; 5 cas de
sélection résolus, 17 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr13_*.py`, `tests/test_ticket216_ampcr_pratique_pr13.py`).

## 2026-10-27 — AMPCR pratique écrite : examen blanc EX02 « installation et dépannage des systèmes » (ticket #231)

Deuxième examen blanc du parcours pratique (UAA EX02 du module `AMPCR-PRATIQUE`, après PR12, 7
blocs), même modèle que EX01 : 10 questions /100 à réponse libre — prérequis de Windows 11 et
édition sur trois postes, GUI/CLI et service désactivé, installation propre sur un SSD neuf
(UEFI/GPT/ESP, choix du disque), pilotes manquants (ID du matériel), comptes et groupe de travail,
double démarrage Ubuntu, mode d'urgence systemd (fstab par UUID), permissions Linux et sudo, écran
d'arrêt après une mise à jour de pilote (WinRE, mode sans échec, restauration), sauvegarde
vérifiée par SHA-256 et choix de la restauration ; 3 schémas dans les documents de question ;
aucune génération IA (`app/v1/ampcr_pratique_ex02_*.py`,
`tests/test_ticket231_ampcr_pratique_ex02.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR12 « Dépannage logiciel et restauration du système » (ticket #215)

Seizième cours du parcours pratique et douzième dans l'ordre pédagogique (UAA PR12 du module
`AMPCR-PRATIQUE`, position 12, après PR11, 20 blocs) : familles de causes (système, application,
pilote, compte, service, logiciel malveillant, stockage) et isolement par élimination ; recueil
des faits, reproductibilité, changements et journaux ; sauvegarde préalable, vérification par
empreinte SHA-256 et accord écrit ; WinRE, mode sans échec, points de restauration, SFC/DISM (y
compris hors ligne), pilotes, mises à jour, profil temporaire ; logiciels malveillants ; systemd,
`journalctl`, GRUB, permissions, paquets (`dpkg --configure -a`), `fsck` démonté, espace disque ;
échelle des interventions et précautions ; panne réseau logicielle ou physique ; 5 procédures
illustrées, 11 figures SVG ; 5 cas résolus (démarrage, service, profil, mise à jour, espace
disque), 17 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr12_*.py`, `tests/test_ticket215_ampcr_pratique_pr12.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR10 « Comptes, pilotes, paramètres et commandes » (ticket #214)

Quinzième cours du parcours pratique et dixième dans l'ordre pédagogique (UAA PR10 du module
`AMPCR-PRATIQUE`, position 10, après PR09, 19 blocs) : comptes locaux et de domaine, standard et
administrateur, groupes, UAC et sudo, moindre privilège, permissions Linux (`chmod`, `chown`) ;
pilotes (sources fiables, compatibilité, codes 28/22/10/43 du Gestionnaire de périphériques, ID du
matériel VEN/DEV et VID/PID, mise à jour et restauration) ; paramètres, services Windows et
systemd, démarrage ; fiches des 16 commandes du ticket (`ipconfig`, `ping`, `tracert`, `nslookup`,
`sfc`, `DISM`, `tasklist`, `net user`, `ip`, `systemctl`, `journalctl`, `lsblk`, `df`, `chmod`,
`chown`, `apt`/`dnf` : syntaxe, rôle, sortie attendue, droits, risques) ; 4 procédures illustrées,
10 figures SVG ; 5 cas résolus, 17 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr10_*.py`, `tests/test_ticket214_ampcr_pratique_pr10.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR09 « Installation complète de Linux — préparation et dépannage » (ticket #209)

Quatorzième cours du parcours pratique et neuvième dans l'ordre pédagogique (UAA PR09 du module
`AMPCR-PRATIQUE`, position 9, après PR08, 19 blocs) : choix de la distribution selon l'usage,
ISO officielle et `sha256sum -c`, clé USB (Etcher, Rufus, `dd` sur la bonne cible), UEFI et
démarrage sécurisé (shim, MOK), session live, sauvegarde et double démarrage prudent (BitLocker,
démarrage rapide, réduction depuis Windows, ESP réutilisée sans formatage), partitions GPT (ESP,
/ ext4, /home facultative, swap selon besoin), fstab et UUID, GRUB / systemd-boot et
`efibootmgr`, comptes et sudo, réseau, `apt`/`dnf`, pilotes, services ; dépannage par six familles
(disque non vu, chargeur, fstab/UUID, réseau absent, permissions et sudo, espace disque) ;
3 procédures illustrées, 9 figures SVG ; 5 cas résolus, 17 exercices, mini-examen 10 questions /20
sans génération IA (`app/v1/ampcr_pratique_pr09_*.py`, `tests/test_ticket209_ampcr_pratique_pr09.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR08 « Installation complète de Windows — préparation et dépannage » (ticket #208)

Treizième cours du parcours pratique et huitième dans l'ordre pédagogique (UAA PR08 du module
`AMPCR-PRATIQUE`, position 8, après PR07, 20 blocs) : procédure complète sur poste vierge
(demande et accord écrit, inventaire, compatibilité et pilotes, licence et édition, sauvegarde,
installation propre / mise à niveau / migration, média USB et pilote F6, firmware UEFI et entrée
« UEFI: », installateur, disque cible et partitions GPT/ESP/MSR/Récupération, configuration
initiale, pilotes et ID du matériel, Windows Update, activation, sécurité, restauration, liste de
contrôle et rapport) ; dépannage par cinq familles (stockage non détecté, démarrage, partitions
MBR/GPT, pilotes manquants, licence) ; 3 procédures illustrées, 9 figures SVG ; 5 cas résolus,
16 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr08_*.py`, `tests/test_ticket208_ampcr_pratique_pr08.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR07 « Systèmes d'exploitation, GUI/CLI et prérequis d'installation » (ticket #207)

Douzième cours du parcours pratique et septième dans l'ordre pédagogique (UAA PR07 du module
`AMPCR-PRATIQUE`, position 7, après EX01, 21 blocs) : fonctions d'un système (noyau, pilotes,
système de fichiers, comptes, services, interface), systèmes du marché et éditions de Windows,
outils GUI/CLI Windows et Linux, 32/64 bits et ARM, UEFI/CSM, démarrage sécurisé, TPM 2.0 et
mbr2gpt, prérequis Windows 11 (verdicts tel quel / après réglages / non compatible) et Linux,
sauvegarde, licences, installation propre ou mise à niveau (arbre de décision), média contrôlé
par SHA-256, menu de démarrage UEFI, partitions et pilotes (VMD/RST), comptes et sécurité
initiale, virtualisation ; 3 procédures illustrées, 8 figures SVG depuis des données testées ;
4 scénarios corrigés, 16 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr07_*.py`, `tests/test_ticket207_ampcr_pratique_pr07.py`).

## 2026-10-27 — AMPCR pratique écrite : examen blanc EX01 « maintenance et dépannage matériel » (ticket #230)

Premier examen blanc du parcours pratique (UAA EX01 du module `AMPCR-PRATIQUE`, après PR06) :
sujet imprimable sans corrigé (7 blocs), 10 questions /100 à réponse libre — identification sur
plan lettré, sécurité/ESD, outillage, absence de POST après ajout de mémoire, vérification et
compte rendu, compatibilité et calcul du bloc (567 W → 750 W), procédure de démontage/remontage,
surchauffe, SSD non détecté (port SATA partagé avec M.2), SMART et protection des données ;
schéma dans les documents de question (mise en page `figure`), pas d'entraînement propre
(redirection vers l'examen), note /100 sur les résultats ; aucune génération IA
(`app/v1/ampcr_pratique_ex01_*.py`, `tests/test_ticket230_ampcr_pratique_ex01.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR05 « Stockage, partitions, formatage et défragmentation » (ticket #206)

Onzième cours du parcours pratique et cinquième dans l'ordre pédagogique (UAA PR05 du module
`AMPCR-PRATIQUE`, 21 blocs) : disque dur, SSD SATA et NVMe, interfaces SATA et M.2,
secteurs/clusters/pages et usure, unités Go/Gio, partitions et volumes, MBR/GPT, démarrage UEFI
et partition EFI, trois plans de partitions exacts, formatage logique et NTFS/FAT32/exFAT/ext4,
choix selon l'usage, Gestion des disques et diskpart, lsblk/parted/mkfs/fstab, sauvegarde
préalable et opérations non destructives, SMART interprété prudemment (dont erreurs CRC),
défragmentation contre TRIM, symptômes (disque absent, non initialisé, RAW, plein, démarrage
impossible) ; 5 procédures illustrées et 11 figures SVG depuis des données testées ; 4 cas
résolus, 16 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr05_*.py`, `tests/test_ticket206_ampcr_pratique_pr05.py`).

## 2026-10-27 — AMPCR pratique écrite : cours PR04 « Reconditionnement, entretien et contrôles après intervention » (ticket #205)

Dixième cours du parcours pratique et quatrième dans l'ordre pédagogique (UAA PR04 du module
`AMPCR-PRATIQUE`, 20 blocs) : réparation / reconditionnement / remise à zéro / effacement
sécurisé, réception (état initial, inventaire, numéros de série), diagnostic avant
intervention, protection des données (accord écrit, sauvegarde vérifiée, confidentialité),
effacement adapté au support (HDD, SSD SATA, SSD NVMe ; certificat), nettoyage non destructif,
poussière et refroidissement, remplacement de pièces, mises à jour firmware/système avec
précautions (BitLocker), tests RAM/SMART/températures/ports/stabilité/batterie, check-lists de
réception et de remise, déchets DEEE et batteries, rapport et traçabilité ; 5 procédures
illustrées et 9 figures SVG depuis des données testées (dont une vue annotée) ; 4 cas résolus,
16 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr04_*.py`, `tests/test_ticket205_ampcr_pratique_pr04.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR03 « Montage et démontage d'un PC — procédure écrite » (ticket #204)

Neuvième cours du parcours pratique et troisième dans l'ordre pédagogique (UAA PR03 du module
`AMPCR-PRATIQUE`, 20 blocs) : préparation du poste (outillage, ESD, inventaire, photos),
sauvegarde, autorisation et état initial, compatibilité avant montage, ordre de montage
justifié, processeur LGA/PGA, pâte thermique et ventirad, mémoire et M.2, entretoises et plaque
d'E/S, bloc, disques et carte graphique, câblage et connecteur de façade, contrôle visuel,
premier démarrage (POST, UEFI, tests mémoire/températures/SMART), câbles et flux d'air,
démontage documenté (visserie, pièces fragiles), remplacement d'un composant et pannes au
premier démarrage ; 5 procédures illustrées et 9 figures SVG depuis des données testées ;
4 cas résolus, 16 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr03_*.py`, `tests/test_ticket204_ampcr_pratique_pr03.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR02 « Alimentation, connectique, compatibilité et sécurité » (ticket #203)

Huitième cours du parcours pratique et deuxième dans l'ordre pédagogique (UAA PR02 du module
`AMPCR-PRATIQUE`, 19 blocs) : courant alternatif/continu et tensions du bloc (+5 VSB, PS_ON#,
PWR_OK, tolérances ATX), puissance, +12 V et rendement 80 PLUS, connecteurs ATX 24, EPS 4+4,
PCIe 6/8, 12V-2x6, SATA, Molex, budget de puissance et marges, ventilateurs et flux d'air,
protections et onduleur, sécurité électrique (mise hors tension, ESD, batteries gonflées,
interdiction d'ouvrir un bloc, outils), USB/HDMI/DisplayPort, SATA/PCIe/M.2, compatibilité
(DDR, socket, formats), symptômes d'alimentation et procédure de remplacement sûre ; 8 figures
SVG depuis des données testées ; 4 cas résolus, 16 exercices, mini-examen 10 questions /20 sans
génération IA (`app/v1/ampcr_pratique_pr02_*.py`, `tests/test_ticket203_ampcr_pratique_pr02.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR01 « Structure d'un PC et identification des composants » (ticket #202)

Septième cours du parcours pratique et premier dans l'ordre pédagogique (UAA PR01 du module
`AMPCR-PRATIQUE`, 19 blocs) : structure et cheminement des données, formats ATX/microATX/Mini-ITX,
carte mère (socket, chipset, VRM, emplacements, connecteurs internes), processeur et
refroidissement, RAM/ROM/stockage et barrettes DIMM/SO-DIMM, firmware BIOS/UEFI/POST/pile CMOS,
stockage HDD/SSD SATA/NVMe, connecteurs du bloc et carte graphique, ports, périphériques et
pilotes, grille de compatibilité, démarche écrite et précautions ESD ; 8 figures SVG (démarche,
schéma-bloc des liaisons, formats à l'échelle, tour, plan de carte numéroté, barrettes à
l'échelle, panneau arrière, arbre de compatibilité), tableaux de valeurs normalisées produits
depuis des données testées ; 4 cas résolus, 16 exercices, mini-examen 10 questions /20 sans
génération IA (`app/v1/ampcr_pratique_pr01_*.py`, `tests/test_ticket202_ampcr_pratique_pr01.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR24 « Dépannage réseau et Internet » (ticket #200)

Sixième cours du parcours pratique (UAA PR24 du module `AMPCR-PRATIQUE`, 18 blocs) : matière
1-15 du ticket (méthode en couches, physique/liaison, IP, DHCP, DNS, passerelle/routage,
switch/VLAN, Wi-Fi, partages, outils Windows et Linux, procédure, pannes combinées, sécurité,
rapport), 13 figures SVG (réseau de référence de l'atelier, ports du switch, procédure en
couches, 3 arbres de diagnostic, 7 documents de diagnostic fictifs) ; relevés (ping, tracert,
nslookup, dig, journal DHCP, Wi-Fi, ARP, routes) produits par code depuis le réseau de
référence ; 6 cas résolus, 6 tableaux symptôme → test discriminant → action, 20 exercices,
mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr24_*.py`,
`tests/test_ticket200_ampcr_pratique_pr24.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR20 « IPv4, MAC, masques et passerelles » (ticket #199)

Cinquième cours du parcours pratique (UAA PR20 du module `AMPCR-PRATIQUE`, 16 blocs) : matière
1-15 du ticket, 13 figures SVG (réseau de référence, MAC, bits /24 /26 /27, DORA, captures
fictives `ipconfig /all`, `ip addr`/`ip route` et fenêtre IPv4, démarche de ping, 3 arbres de
diagnostic) ; calculs d'adressage, plans et sorties de commandes produits par un modèle testé
(`ipaddress`) ; 5 cas résolus, 20 exercices, mini-examen 10 questions /20 sans génération IA
(`app/v1/ampcr_pratique_pr20_*.py`, `tests/test_ticket199_ampcr_pratique_pr20.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR16 « Câble coaxial et BNC » (ticket #198)

Quatrième cours du parcours pratique (UAA PR16 du module `AMPCR-PRATIQUE`, 15 blocs) : matière
1-12 du ticket, 14 figures SVG (coupe du coax, BNC éclaté, bus 10BASE2 conforme et 4 versions
fautives, comparaison 10BASE2/10BASE5/vidéo 75 Ω, cotes « de la notice », montage et contrôle
du BNC, lectures d'ohmmètre, 2 traces de réflectomètre) ; non-conformités, lectures et
distances calculées depuis un modèle de bus testé ; 4 exemples corrigés, 16 exercices,
mini-examen 10 questions /20 sans génération IA (`app/v1/ampcr_pratique_pr16_*.py`,
`tests/test_ticket198_ampcr_pratique_pr16.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR15 « Câblage RJ45 T568A/B » (ticket #197)

Troisième cours du parcours pratique (UAA PR15 du module `AMPCR-PRATIQUE`, 13 blocs) : matière
1-6 du ticket, 14 figures SVG calculées depuis les brochages T568A/T568B testés (aucune image
générée), 4 exemples corrigés, 16 exercices, mini-examen 10 questions /20 sans génération IA ;
tout ordre de couleurs cité dans le cours ou un corrigé est vérifié par test
(`app/v1/ampcr_pratique_pr15_*.py`, `tests/test_ticket197_ampcr_pratique_pr15.py`).

## 2026-10-26 — AMPCR pratique écrite : cours PR11 « Messages d'erreur Windows/Linux » (ticket #194)

Deuxième cours du parcours pratique (UAA PR11 du module `AMPCR-PRATIQUE`, 16 blocs) : matière
1-6 du ticket, 11 figures SVG sur données testées (arbre de décision par stade, flux
d'intervention, partitionnement GPT, 8 captures fictives Windows/Linux), 5 cas résolus,
16 exercices corrigés, mini-examen 10 questions /20 sans génération IA. Banque pratique :
documents « console » (nouvelle mise en page `console`) et remises en ordre `ordering`
(`app/v1/ampcr_pratique_pr11_*.py`, `app/v1/ampcr_pratique_bank.py`).

## 2026-10-26 — AMPCR pratique écrite : numérotation PR01–PR30 / EX01–EX06 alignée sur les tickets (ticket #236)

Audit des 36 tickets GitHub contre le plan installé : seuls PR01, PR06, PR11 et PR15 portaient
le sujet de leur ticket. `app/v1/ampcr_pratique_plan.py` reprend désormais code, titre, ticket
et matière de chaque ticket (5 modules ; EX01–EX04 examens de module, EX05/EX06 examens blancs
globaux, chacun avec ses exigences AP) ; complément AP-C03 (protection des données). Matrice,
accueil `/ampcr-pratique`, `docs/ampcr_pratique_tickets.md` et `docs/ampcr_pratique_v1.md`
mis à jour. PR06 (seul cours publié) inchangé ; aucune donnée en base modifiée.

## 2026-10-26 — AMPCR pratique écrite : cours PR06 « Diagnostic des pannes matérielles » (ticket #193)

Premier cours du parcours pratique : module `AMPCR-PRATIQUE` (matière Informatique) seedé avec
l'UAA PR06 (15 blocs, 8 schémas SVG vérifiés : chaîne de démarrage, arbre « PC ne démarre
pas », ATX 24, EPS 8, plan de carte mère, écran firmware fictif, courbe de températures,
configuration minimale ; 4 cas résolus ; 12 exercices corrigés). Banque : 12 exercices
(entraînement) + 10 questions de mini-examen (examen blanc, /20), réserves séparées par
`prompt_version`, sans génération IA (`app/v1/ampcr_pratique_bank.py`). Moteur : paramètre
`mode` de `select_bank_questions`/`available_session_lengths`, contexte de correction PR06,
note sur 20 dans les résultats du parcours pratique.

## 2026-10-26 — AMPCR pratique écrite : socle et matrice de couverture officielle (ticket #192)

Nouveau parcours distinct du théorique : `app/v1/ampcr_pratique_plan.py` (sources officielles
tracées par URL + SHA-256, consignes du jour, 38 exigences pp. 5-6 recopiées, 2 compléments,
6 modules, PR01–PR30, EX01–EX06, statut calculé depuis les UAA publiées du module
`AMPCR-PRATIQUE`), `app/v1/ampcr_pratique_format.py` (format d'exercice pratique écrit →
`document_analysis`/`long_answer` existants), routes `/ampcr-pratique[/matrice|/format-exercice]`,
liens depuis `/mon-parcours` et `/modules/ampcr`. Aucune table, aucun seed.

## 2026-09-17 — S'entraîner : rendre les 12 exercices MC01 répondables (ticket #29)

Termine la mise à niveau interactive de S'entraîner amorcée aux tickets #17/#21 : les 8
derniers exercices MC01 encore en Markdown statique (3, 4, 5, 6, 7, 8, 10, 12) sont migrés
en blocs `editorial_exercise` structurés, avec un contrôle de réponse réel et aucune
correction visible avant validation. **MC01 ne contient plus aucun bloc Markdown
d'exercice** — les 12 sont désormais des blocs `editorial_exercise`, tous en espace
PRACTICE. Contenu pédagogique strictement inchangé (question + grille de correction
reprises mot pour mot) : aucune simplification, aucune matière inventée.

**Nouveaux types** (`app/editorial_exercise.py`) : `long_answer` (réponse rédigée libre,
Ex3/5/6/7/8), `diagnostic` (composant en cause + justification, Ex4/10), `vocabulary`
(Ex12 — grille de correction IA, car l'exercice demande une explication en plus du terme
exact, pas seulement un mot). `short_answer`/`vocabulary` deviennent conditionnellement
locaux : corrigés localement si `accepted_answers` est fourni, sinon la correction bascule
en IA (`explanation` sert alors de grille de correction/rubric) — même règle que le
contrat questionnaire #23, désormais partagée par les deux socles.

**Correction sémantique IA sans second moteur** : nouveau pont
`app/editorial_ai_correction.py`, qui traduit un `EditorialExerciseItem` vers
`QuestionnaireQuestion` (#23) et appelle `AIProvider.correct_semantic_batch` — un seul
appel par question, jamais un second moteur IA. `points_max` vient toujours de l'item
(jamais de la réponse du fournisseur), `points_awarded` toujours borné à `[0, points_max]`
(`app.ai.questionnaire.validate_semantic_correction`, promue publique pour être réutilisée
ici). Nouveau champ `EditorialExerciseBlockConfig.context_key` (requis dès qu'un item du
bloc nécessite l'IA, validé à la construction).

**Route** (`app/practice.py`) : `/practice/api/editorial/{block_id}/verify` route
désormais localement ou vers l'IA selon `item.requires_ai_correction()` — jamais
d'appel IA pour ce qui peut être corrigé de façon fiable en local. Sans clé configurée :
503 propre (jamais la solution) ; erreur fournisseur : 502 ; réponse non textuelle pour un
type sémantique : 422.

**Widget JS** (`app/static/js/editorial_exercise.js`) : nouveau contrôle textarea +
bouton « Corriger » (libellé différent de « Vérifier », piloté par `item.requires_ai`,
jamais deviné depuis le titre/type) pour les types à réponse libre. **Corrige au passage
un gap identifié sur les types existants** : un échec réseau/503/502 laissait
auparavant le bouton désactivé indéfiniment, sans aucun message — désormais le champ est
réactivé et un message clair s'affiche (jamais la solution). Feedback enrichi
(points obtenus, points forts, erreurs, manquant) affiché après correction sémantique,
dégradé silencieusement pour une correction locale (champs absents/vides).

**Sécurité** : aucune correction, grille de correction ni réponse acceptée n'est jamais
transmise avant l'appel de vérification (`to_public_dict()` n'expose que `requires_ai:
bool` — la modalité de correction, jamais la solution). Réponse candidate toujours
transmise comme donnée délimitée à l'IA, jamais une instruction (même prompt système que
#23).

**Migration du staging déjà seedé, sans reset-db** : même mécanisme que #21/#22 — les 3
blocs Markdown restants (leurs titres, désormais dans `MC01_OBSOLETE_TITLES`) sont retirés
par `_seed_uaa(obsolete_titles=...)` au prochain `seed-db`, remplacés par les 8 nouveaux
blocs structurés (titres différents, garantissant l'idempotence des seeds ultérieurs).
Scénario testé explicitement (staging post-#22 reconstruit à la main → un seul `seed()` →
forme post-#29 complète).

**Découverte annexe corrigée en cours de développement** : `EditorialExerciseItem.check()`
et `correct_answer_display()` ne géraient pas le type `vocabulary` pour la correction
locale (seul `short_answer` était couvert) — trouvé et corrigé par les tests unitaires
avant tout usage réel, aucun impact en production.

**Tests** : +35 tests (431 au total) : `tests/test_editorial_exercise.py` (validation des
3 nouveaux types, `requires_ai_correction`, absence de fuite dans `to_public_dict()`,
validation de `context_key`) ; `tests/test_editorial_ai_correction.py` (nouveau — mapping
vers `QuestionnaireQuestion`, un seul appel par correction, sévérité, points bornés,
résultat manquant géré sans exception) ; `tests/test_ticket29_no_regression.py` (nouveau —
12/12 exercices présents et répondables, 0 correction visible au chargement,
classification/ordering non cassés, correction déterministe et IA via `FakeAIProvider`,
absence de clé → 503, erreur fournisseur → 502, points bornés, aucun doublon Markdown,
migration d'un staging pré-#29 sans reset, idempotence, MC02/MC03/Mathématiques non
affectés). Tests existants (#17/#21/#22) ajustés à la nouvelle réalité (12 exercices
structurés, plus 4) sans changer leur rôle de garde-fou. `ruff check .` : 36 erreurs,
identiques à `develop` (comparé via worktree isolé) — aucune nouvelle erreur.

**Documentation** : `docs/editorial_exercise_engine.md` (nouveaux types, correction
sémantique IA, `context_key`, codes d'erreur, widget) ; `docs/current_state.md` ;
`docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md` (rapport de
ticket).

## 2026-09-17 — Bug IA : migrer le provider OpenAI vers la Responses API (ticket #31)

Corrige un bug bloquant diagnostiqué en conditions réelles sur staging : avec
`OPENAI_MODEL=gpt-5.6-luna` (clé et modèle valides, confirmés par un appel direct à `POST
/v1/responses` réussissant en HTTP 200 depuis le même serveur), `POST
/practice/api/ai/generate` renvoyait HTTP 502, causé par un HTTP 400 d'OpenAI — le
provider appelait encore `/v1/chat/completions` avec `response_format: json_schema`, un
point d'entrée qui n'accepte plus ce modèle.

**Migration** : `OpenAIProvider` appelle désormais `POST https://api.openai.com/v1/responses`
pour les quatre opérations existantes (génération/correction exercice unique — #10 ;
génération questionnaire/correction sémantique groupée — #23). Adaptation de la seule
couche I/O — `app/ai/prompts.py` (messages, schémas JSON, contrats métier) est
**entièrement inchangé** :
- `messages` (`[{"role": "system"|"user", "content"}]`) → `instructions` (système) +
  `input` (utilisateur), séparés au niveau racine du payload ;
- `response_format: {"type": "json_schema", "json_schema": {...}}` →
  `text: {"format": {"type": "json_schema", "name", "strict", "schema"}}` (schéma
  aplati, sans la clé `json_schema` imbriquée) ;
- extraction du résultat : `choices[0].message.content` →
  `output[]` (recherche du premier item `type: "message"`, puis de son premier bloc
  `content[]` de `type: "output_text"`) — jamais un index fixe non validé, robuste à un
  item `reasoning` intercalé par un modèle de raisonnement.
- **`temperature` retirée du payload** : les modèles GPT-5 de raisonnement (dont
  `gpt-5.6-luna`) la rejettent avec un HTTP 400 (« Unsupported parameter: 'temperature' is
  not supported with this model ») — un second bug latent qui aurait persisté même après la
  migration d'endpoint si ce paramètre était resté envoyé inconditionnellement. Découvert
  par vérification de la documentation/du comportement actuel des modèles GPT-5, pas par
  simple transposition du payload Chat Completions.

**Diagnostic d'erreur amélioré** : sur un statut non-2xx, reprend désormais
`error.type`/`error.code`/`error.message` d'OpenAI (message tronqué à 200 caractères) dans
`AIResponseError`, sans jamais exposer les en-têtes, le payload ou la clé API.

**Sécurité inchangée** : timeout, absence de clé (`AINotConfiguredError` → 503), retry
borné de l'orchestrateur questionnaire, contexte pédagogique borné, réponse candidate
toujours traitée comme donnée — aucune de ces protections (#10/#23) n'est modifiée par
cette migration, uniquement la couche réseau.

**Découverte annexe corrigée** : `tests/conftest.py` ne forçait pas explicitement
`OPENAI_API_KEY=""` (seulement un `setdefault` sur d'autres variables) — inoffensif tant
qu'aucune vraie clé n'existait dans `/srv/jury-central/.env`, mais désormais qu'une vraie
clé y est configurée (ticket #31), `pytest` risquait de la lire directement depuis le
fichier `.env` réel et de l'utiliser dans un test qui suppose l'absence de configuration.
Corrigé par un force-set explicite (`os.environ["OPENAI_API_KEY"] = ""`) — garantit qu'
**aucun test ne peut jamais déclencher un appel réseau réel**, y compris sur cette
machine.

**Compatibilité** : routes `/practice/api/ai/generate`/`/correct` inchangées, bloc
`AI_EXERCISE` de MC01 (`block_id` à reconfirmer après déploiement, voir le rapport de
ticket) fonctionnel sans modification JS/template. Contrat questionnaire #23 non régressé.

**Tests** : +8 tests dans `tests/ai/test_openai_provider.py` (22 au total dans ce fichier) :
URL `/v1/responses`, `instructions`/`input`/`text.format` bien séparés du payload,
extraction avec item `reasoning` intercalé, `output` vide, item `message` absent, JSON de
contenu invalide, statuts 400 (avec message OpenAI repris et tronqué)/401/429/500 (corps
illisible), scénario exact du ticket (`gpt-5.6-luna`) — plus la correction de
`tests/conftest.py`. Tests existants (génération/correction exercice unique, génération
questionnaire, correction sémantique groupée) adaptés à la nouvelle enveloppe de réponse
sans changer leurs assertions métier. 394 tests au total, tous verts. `ruff check .` : 36
erreurs, identiques à `develop` (comparé via worktree isolé) — aucune nouvelle erreur.

**Documentation** : `docs/ai_exercise_engine.md` — tableau de migration Chat Completions →
Responses API, diagnostic d'erreur, extraction robuste, procédure de validation réelle
staging mise à jour (clé déjà configurée, test direct de `block_id` réel avec
génération **et** correction) ;
`docs/claude-reports/2026-09-17_ticket-31_responses-api.md` (rapport de ticket).

## 2026-09-16 — IA : configurer OpenAI et stabiliser le contrat de génération/correction (ticket #23)

Met réellement en service le moteur OpenAI côté serveur et stabilise un contrat générique
« questionnaire » (plusieurs questions, tous types, notation avec sévérité), destiné aux
tickets #24 (S'entraîner) et #25 (S'évaluer), pour toutes les matières. Même package
`app/ai/`, même fournisseur (`AIProvider`) : **aucun second moteur**. Le contrat à exercice
unique du ticket #10 (blocs `ai_exercise`, routes `/practice/api/ai/*`) reste inchangé.

**Contrat générique** : `generate_questionnaire(provider, request)` /
`correct_questionnaire(provider, questionnaire, answers, severity, contexts)`
(`app/ai/questionnaire.py`), avec 14 types de question stabilisés (`QUESTION_TYPES`) :
`single_choice`, `multiple_choice`, `true_false`, `short_answer`, `long_answer`,
`fill_blank`, `matching`, `classification`, `ordering`, `numeric`, `diagnostic`,
`procedure`, `vocabulary`. Sortie JSON stricte et validée côté serveur
(`Questionnaire`/`QuestionnaireQuestion`, chargement tolérant comme `editorial_exercise`).

**Correction locale vs IA** : les types déterministes (QCM, vrai/faux, matching,
classification, ordering, numeric, fill_blank, + short_answer/vocabulary avec
`accepted_answers`) sont corrigés localement (`app/ai/local_correction.py`), **jamais**
d'appel IA pour ceux-ci. Les questions sémantiques (long_answer, diagnostic, procedure, +
short_answer/vocabulary sans réponses acceptées) sont regroupées en **un seul** appel au
fournisseur, jamais un appel par question.

**Sévérité de notation** : trois niveaux stables (`lenient`/`standard`/`strict`, labels UI
futurs Bienveillante/Standard/Stricte) — changent l'exigence appliquée par le correcteur
sémantique, jamais les faits attendus ni `points_max`.

**Validation serveur des points** : `points_max` d'une question ne vient jamais de la
réponse IA (absent du schéma de correction demandé au modèle) ; `points_awarded` est
systématiquement borné à `[0, points_max]` après coup, quel que soit ce que renvoie le
fournisseur. Pour un questionnaire d'examen avec `total_points`, les `points_max` générés
sont recalés côté serveur pour que leur somme soit exacte.

**Sécurité** : réponse candidate toujours transmise comme donnée délimitée, jamais une
instruction (même mécanisme que le ticket #10, étendu à un lot de questions/réponses en un
seul appel) ; aucun secret dans le HTML/JS/logs/Git/rapport ; retry borné et documenté
(2 tentatives maximum) en cas de réponse invalide, jamais de boucle indéfinie ; site
fonctionnel sans clé configurée (`AINotConfiguredError`, jamais un 500).

**Configuration** : `OPENAI_API_KEY`, `OPENAI_MODEL` (`gpt-4o-mini` par défaut, déjà en
place depuis le ticket #10, entièrement configurable sans code), `AI_REQUEST_TIMEOUT_SECONDS`
— confirmées à jour (appel HTTP direct via `httpx`, sortie structurée stricte
`json_schema`, mécanisme actuellement documenté par OpenAI ; pas de paquet SDK `openai`
ajouté, cohérent avec la philosophie de dépendances minimales du projet).

**Statut** : ce ticket stabilise le contrat et ne branche encore aucune route HTTP
publique ni interface S'entraîner/S'évaluer — périmètre explicite des tickets #24/#25.

**Tests** : +98 tests au total (288 → 386), `tests/ai/` compte désormais 117 tests :
validation de configuration par type,
correction locale déterministe (tous les types, malformé jamais une exception), génération
(practice/exam, difficulté, types autorisés, contexte strictement borné aux modules
sélectionnés, retry borné, filtrage défensif), correction (routage local/IA, aucun appel IA
gaspillé pour un questionnaire purement déterministe, sévérité, bornes de points, injection
de prompt reproduisant l'exemple du ticket), fournisseur réel avec `httpx.post` intercepté
(succès, réponse vide, type inconnu toléré, timeout, erreur fournisseur, id de question
inconnu ignoré). Aucun appel réseau réel dans `pytest`. 386 tests au total, tous verts.
`ruff check .` : 36 erreurs, identiques à `develop` (comparé via worktree isolé) — aucune
nouvelle erreur.

**Documentation** : `docs/ai_exercise_engine.md` étendu (contrat questionnaire, correction
locale vs IA, sévérité, validation des points, configuration, procédure de validation
réelle sur staging avec une vraie clé) ;
`docs/claude-reports/2026-09-16_ticket-23_openai-contract.md` (rapport de ticket).

## 2026-09-16 — Refonte UX : séparer Cours, S'entraîner et S'évaluer (ticket #22)

Décision produit de ChatGPT : une page de module ne doit plus mélanger théorie, exercices
et examen dans le même flux. Chaque UAA expose désormais trois espaces génériques,
identiques pour toutes les matières :

- **Cours** (`/uaa/{slug}`) : théorie, exemples, tableaux, vocabulaire, fiche mémo.
- **S'entraîner** (`/uaa/{slug}/practice`) : exercices structurés (`editorial_exercise`),
  exercices historiques encore en Markdown, génération d'exercice par IA
  (`ai_exercise`) — prépare le ticket #24 (constructeur multi-modules).
- **S'évaluer** (`/uaa/{slug}/exam`) : examen final — prépare le ticket #25 (génération
  d'examen multi-modules).

**Classification explicite, pas déduite** : nouveau champ `LessonBlock.space`
(`BlockSpace` : `COURSE`/`PRACTICE`/`EXAM`), indépendant de `BlockType` (nature technique
du bloc) — jamais déduit du titre, de la position ou du type à l'exécution, conformément à
la décision explicite de ChatGPT. Valeur par défaut rétrocompatible : `COURSE`.

**Migration explicite du contenu connu** : chaque bloc de MC01/MC02/MC03 (72 blocs) porte
désormais une classification écrite en dur dans `app/seed.py` (théorie/exemples/fiche
mémo → COURSE, exercices Markdown + `editorial_exercise` + `ai_exercise` → PRACTICE,
examen final → EXAM). Mathématiques reste COURSE par défaut (aucune classification
spécifique demandée pour ce ticket).

**Migration de schéma sans Alembic** : le projet n'a pas de système de migrations : une
nouvelle colonne sur une table déjà existante (staging déjà seedé) n'est jamais créée par
`Base.metadata.create_all`. Nouvelle fonction `app.database.ensure_schema_migrations()`
(idempotente, `ALTER TABLE ... ADD COLUMN space ... DEFAULT 'COURSE'` si la colonne est
absente), appelée au démarrage de l'application et dans `seed()`.

**Migration du contenu déjà seedé (staging) sans reset-db** : `_seed_uaa()` accepte
désormais un paramètre `reclassified` qui met à jour EN PLACE la métadonnée `space` d'un
bloc déjà existant (matché par titre) dont la valeur diffère de celle désormais définie
dans `app/seed.py` — jamais son `content`. Un staging seedé avant ce ticket (où `space`
vaut COURSE partout, valeur posée par `ensure_schema_migrations`) reclasse donc
correctement ses exercices/examen vers PRACTICE/EXAM au prochain `seed-db`, sans perte ni
duplication de contenu. Scénario testé explicitement de bout en bout (base construite à la
main + `seed()` + vérification HTTP) et vérifié manuellement sur un serveur réel.

**Navigation** : nouveau partiel `_uaa_space_nav.html` (trois onglets de largeur égale,
`min-height: 44px`, testé aux largeurs mobiles 360/390/430 px), inclus par les trois
templates (`uaa_detail.html`, nouveaux `uaa_practice.html`/`uaa_exam.html`), tous
alimentés par le même partiel de rendu générique `_lesson_blocks.html` et la même fonction
`app.main._render_lesson_blocks` (aucune duplication de logique d'affichage par bloc).

**Tests** : +16 tests (`tests/test_ticket22_no_regression.py`, nouveau) : migration de
schéma (ajout de colonne idempotent, y compris sur une table absente), valeur par défaut
du modèle, filtrage strict par espace sur les trois routes, 404 cohérent (slug inconnu,
UAA non publiée) sur les trois routes, navigation (liens + état actif), scénario complet
de staging pré-#22 reclassé sans reset, répartition COURSE/PRACTICE/EXAM de MC01/MC02/MC03,
Mathématiques inchangé, idempotence. Ajustements de tests existants (conséquence directe
et attendue de la séparation, pas une régression) :
`tests/test_informatique_mc0{1,2,3}.py` et `tests/test_ticket{17,21}_no_regression.py`
pointent désormais vers `/practice`/`/exam` pour les exercices/examens, avec des tests
supplémentaires confirmant leur absence du flux Cours. 288 tests au total, tous verts.

**Ruff** : `ruff check .` → 36 erreurs, strictement identiques à `develop` (comparé via
worktree isolé) — 0 nouvelle erreur (2 nouvelles occurrences B008 sur les routes
`/practice`/`/exam`, neutralisées par `# noqa: B008`, même convention que le reste du
projet pour ce type d'appel `Depends()`).

**Documentation** : `docs/editorial_exercise_engine.md` implicitement à jour (aucun
changement de socle) ; `docs/current_state.md` (navigation publique, classification
explicite) ;
`docs/claude-reports/2026-09-16_ticket-22_separation-cours-practice-exam.md` (rapport de
ticket).

## 2026-09-16 — Classification et ordering dans les exercices éditoriaux (ticket #21)

Extension du socle `editorial_exercise` (ticket #17) avec deux nouveaux types :
`classification` (classer des éléments dans des catégories) et `ordering` (remettre des
éléments dans le bon ordre) — les deux à correction locale déterministe, sans note
partielle (correct/incorrect sur l'ensemble de l'item, comme les types existants).

**Migration MC01** : les exercices 1, 2 et 11 (classification) et 9 (ordering) migrent de
blocs Markdown statiques vers des blocs `editorial_exercise` interactifs, **sans
changement de leur contenu pédagogique** (mêmes catégories/éléments, même ordre correct,
mêmes explications, mot pour mot). Les 8 autres exercices (3, 4, 5, 6, 7, 8, 10, 12)
restent inchangés en Markdown — ils nécessitent `long_answer` (réponse rédigée + IA) ou
une réécriture qui dénaturerait l'énoncé, hors périmètre de ce ticket.

**UX** : entièrement au clic, aucun glisser-déposer requis (utilisable au tactile comme au
clavier). `classification` : un groupe de boutons de catégorie par élément (le choix actif
est mis en surbrillance) ; `ordering` : une liste numérotée avec boutons « monter »/
« descendre » sur chaque ligne. Correction toujours via la même route AJAX générique
(`POST /practice/api/editorial/{block_id}/verify`), jamais de rechargement de page, jamais
de solution dans le HTML avant l'appel de vérification.

**Migration du contenu déjà seedé (staging)** : les deux blocs Markdown modifiés
(désormais réduits aux exercices restants) portent des titres **différents** de leur
version pré-#21 ; leurs anciens titres sont listés dans `MC01_OBSOLETE_TITLES`
(`app/seed.py`) et retirés explicitement par `_seed_uaa(..., obsolete_titles=...)` au
prochain `seed-db` — sans `reset-db`, sans perte du reste du contenu. Ce mécanisme
(retrait par ancien titre + insertion sous un titre nouveau) est nécessaire car
`_seed_uaa` ne modifie jamais le contenu d'un bloc existant dont le titre correspond déjà
— un simple changement du texte Python n'aurait eu aucun effet sur un staging déjà seedé.
Scénario testé explicitement (`tests/test_ticket21_no_regression.py`), voir aussi
`docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md`.

**Tests** : +28 tests (241 → 269, tous verts) : validation de configuration, sérialisation,
absence de fuite de solution, correction correcte/incorrecte/incomplète/malformée pour les
deux nouveaux types (`tests/test_editorial_exercise.py`), route HTTP de bout en bout
(`tests/test_practice_editorial_routes.py`), migration MC01 sans doublon, non-régression
MC02/MC03/Mathématiques, idempotence du seed, et scénario de migration d'un staging
pré-#21 sans reset (`tests/test_ticket21_no_regression.py`, nouveau fichier). `ruff check .`
: 36 erreurs, identiques à `develop` (comparé via worktree isolé) — aucune nouvelle erreur.

**Documentation** : `docs/editorial_exercise_engine.md` mis à jour (types pris en charge,
UX classification/ordering, route `answer: Any`) ;
`docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md` (rapport de ticket).

## 2026-09-16 — Correction bug mobile : menu hamburger inerte (ticket #18)

Constaté sur le staging public depuis Chrome Android : le bouton hamburger de la navbar
était visible mais ne réagissait pas au toucher.

**Cause exacte** : l'attribut `integrity` (Subresource Integrity) du `<script>` chargeant
le bundle JS Bootstrap (`app/templates/base.html`) ne correspondait pas au contenu réel du
fichier servi par le CDN. Un navigateur qui détecte cet écart bloque **silencieusement**
l'exécution du script (aucune erreur visible pour l'utilisateur, uniquement dans la
console développeur) : le CSS Bootstrap (chargé séparément, intégrité vérifiée correcte)
affichait bien le bouton hamburger, mais son comportement (`data-bs-toggle="collapse"`)
ne s'activait jamais, faute de JS Bootstrap exécuté. Diagnostic confirmé en recalculant le
hash réel du fichier (`openssl dgst -sha384`) depuis l'URL exacte versionnée
(`bootstrap@5.3.3`, immuable) et en le comparant octet pour octet à celui du template —
écart net à partir du même préfixe. Le hash du CSS Bootstrap, vérifié par la même méthode,
était lui correct.

**Correction** : une seule ligne modifiée dans `app/templates/base.html` — l'attribut
`integrity` du bundle JS corrigé avec la valeur réellement calculée. Aucune modification
du markup navbar/collapse (déjà syntaxiquement correct), aucun second menu mobile
parallèle, aucune dépendance ajoutée.

**Tests** : +5 tests (`tests/test_navbar_mobile_menu.py`) — hash d'intégrité figé et
vérifié (régression directe sur la cause), absence de `defer`/`async` sur le script
Bootstrap, cohérence `data-bs-toggle`/`data-bs-target`/`aria-controls`/id du collapse, un
seul hamburger et une seule cible collapse (garde-fou contre un contournement par menu
parallèle), breakpoint `navbar-expand-md` confirmé (couvre les largeurs mobiles 360/390/
430 px demandées, toutes < 768px). 241 tests au total, tous verts. `ruff check .` : 36
erreurs, identiques à `develop` (comparé via worktree isolé) — aucune nouvelle erreur.

**Vérifié manuellement** : HTML servi par le serveur réel (plusieurs pages) contient
désormais le hash corrigé ; markup hamburger intact et cohérent
(`data-bs-target="#navbarNav"` = `aria-controls="navbarNav"` = `id="navbarNav"`) ; toutes
les pages clés (accueil, matières, MC01–MC03, Mathématiques) toujours 200. **Limite** :
aucun navigateur/outil d'automatisation n'étant disponible dans cet environnement serveur,
le clic réel sur les viewports 360/390/430 px n'a pas pu être vérifié visuellement — la
correction agit néanmoins exactement sur le mécanisme que le navigateur utilise
(vérification SRI octet pour octet), et le comportement d'ouverture/fermeture lui-même est
celui, déjà éprouvé, du composant Collapse de Bootstrap 5.3.3, non modifié par ce ticket.
Validation visuelle réelle recommandée sur staging après déploiement.

**Documentation** : `docs/claude-reports/2026-09-16_ticket-18_mobile-menu.md` (rapport de
ticket).

## 2026-09-16 — Socle générique des exercices éditoriaux interactifs (ticket #17)

Suite à l'audit UX/technique du même jour
(`docs/claude-reports/2026-09-16_audit_interactivite.md`), premier chantier
d'interactivité : les exercices éditoriaux (texte Markdown avec correction masquée/
affichée côté client, sans saisie ni vérification serveur) gagnent un socle générique
réutilisable dans toutes les matières, sur le patron déjà éprouvé par `value_table`/
`quiz`/`ai_exercise` (config JSON → route de vérification → widget AJAX).

**Nouveau type de bloc `editorial_exercise`** (`app/models.py::BlockType`, extension
minimale, aucun changement de schéma SQLite). Nouveau module `app/editorial_exercise.py` :
`EditorialExerciseBlockConfig` (`mode: practice|exam`, liste d'items),
`EditorialExerciseItem` (validation stricte à la construction, tolérance au chargement
depuis la base), première tranche de types — `single_choice`, `true_false`,
`short_answer` — à correction locale déterministe uniquement. Nouvelle fonction
`app/answer_checking.py::text_answer_matches` (comparaison textuelle normalisée casse/
espaces/accents, aucun `eval()`).

**Nouvelle route** `POST /practice/api/editorial/{block_id}/verify` — le serveur recharge
toujours la configuration complète depuis `LessonBlock.content` ; `to_public_dict()`
exclut structurellement la solution. Nouveau widget `app/static/js/editorial_exercise.js`
(AJAX, sans rechargement, contrôles `d-print-none`, tailles/contrôles adaptés au mobile).

**Démonstration** `/admin/editorial-exercise-demo` (+ route de vérification associée),
même principe que `/admin/value-table-demo` : un exercice fixe par type, indépendamment
de tout contenu réel.

**MC01 : aucune migration dans ce ticket.** Les 12 exercices existants ont été passés en
revue un par un : 8 nécessitent `long_answer` (réponse rédigée, correction IA — ticket
séparé), 3 nécessitent `classification`, 1 nécessite `ordering` — aucun ne peut être
honnêtement exprimé avec la première tranche de types sans dénaturer son contenu
pédagogique. Conformément au ticket #17 (« ne force pas artificiellement »), MC01 reste
donc intact dans ce ticket ; le détail exercice par exercice est dans
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md`.

**Tests** : +38 tests (`tests/test_editorial_exercise.py` : validation, sérialisation,
absence de fuite, correction ; `tests/test_practice_editorial_routes.py` : route HTTP de
bout en bout, IDs invalides, bloc non publié/mauvais type, absence de fuite dans le HTML
public, démo admin ; `tests/test_ticket17_no_regression.py` : confirme `app/seed.py`
inchangé, MC01/MC02/MC03/Mathématiques strictement intacts). 236 tests au total, tous
verts. `ruff check .` : 36 erreurs, identiques à `develop` (comparé via worktree isolé) —
aucune nouvelle erreur.

**Vérifié manuellement** sur une base SQLite temporaire isolée (jamais `jury_central.db`,
intégrité re-vérifiée par MD5) : MC01/MC02/MC03/Mathématiques inchangés, démo admin
accessible après connexion, réponse correcte/incorrecte/normalisée toutes vérifiées,
aucune fuite de solution dans le HTML brut de la page de démo.

**Documentation** : `docs/editorial_exercise_engine.md` (nouveau),
`docs/EXERCISE_TYPES.md`, `docs/admin.md`, `docs/current_state.md`, `docs/INDEX.md`,
`docs/README.md`,
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` (rapport de ticket).

## 2026-09-16 — Informatique AMPCR : mini-cours 03 « CPU et mémoire RAM » (ticket #14)

Troisième cours de la série Informatique AMPCR, contenu et périmètre pédagogique fournis
intégralement par ChatGPT dans le ticket #14. Réutilise **strictement** l'architecture des
tickets #10/#12 — aucun nouveau mécanisme, aucun second moteur IA.

**Matière/UAA** : nouvelle UAA `MC03` (« CPU et mémoire RAM ») sous le module `AMPCR`
existant, navigable depuis `/uaa/ampcr-mc03`, juste après MC02.

**Contenu** (`app/seed.py::MC03_BLOCKS`, 25 blocs) : plan, 17 sections de cours — CPU (rôle
et cycle d'exécution, cœurs/threads/SMT, fréquence base/boost, IPC, cache L1/L2/L3,
32/64 bits, socket/génération/compatibilité, TDP/refroidissement/throttling, graphique
intégré) puis RAM (rôle/capacité/latence, DDR3/DDR4/DDR5, DIMM/SO-DIMM/dual-channel,
capacité maximale, XMP/EXPO/ECC, RAM vs VRAM vs stockage) puis performances/diagnostic
(goulot d'étranglement, diagnostic RAM et CPU/thermique, unités et pièges d'examen),
vocabulaire FR/EN — 12 exercices progressifs (3 blocs) à correction masquée à la demande,
un bloc `ai_exercise` réutilisant le moteur du ticket #10, une fiche mémo, et l'examen
final (10 questions/20 points, aucune réponse visible, corrigé dans un bloc séparé
`is_published: False` — même mécanisme exactement qu'aux mini-cours 01/02).

**Nuances explicitement respectées** (exigées par le ticket #14, vérifiées par test) : TDP
présenté comme indicateur de conception thermique et non comme consommation électrique
exacte ; GHz explicitement insuffisant seul pour comparer deux CPU (IPC, cœurs, génération) ;
64 bits jamais assimilé à « deux fois plus rapide » que 32 bits ; DDR5 explicitement
distinguée d'une simple « DDR4 plus rapide » (incompatibilité de génération, pas seulement
une différence de vitesse).

**Contexte IA MC03** : nouvelle entrée
`app/ai/context.py::PEDAGOGICAL_CONTEXTS["ampcr-mc03"]` (notions, compétences 1.1.1–1.1.4/
2.3.2–2.3.3, vocabulaire, contraintes reprenant explicitement les nuances TDP/GHz/64 bits/
DDR5 ci-dessus pour que le moteur IA ne les reproduise pas non plus). Aucune autre
modification du moteur IA (`app/ai/`, routes `/practice/api/ai/*`).

**Examen** : bloc publié avec 10 questions/20 points, aucune réponse ; corrigé complet dans
un second bloc `is_published: False`, jamais servi côté public.

**Tests** : +8 tests (`tests/test_informatique_mc03.py` : navigation, matière obligatoire
(dont les nuances TDP/GHz/64 bits/DDR5), 12 exercices, examen sans correction visible,
corrigé non publié, contexte IA enregistré, génération/correction via le moteur partagé
avec le contexte MC03 spécifiquement vérifié, non-régression MC01/MC02/Mathématiques),
`test_seed_is_idempotent` mis à jour pour les nouveaux effectifs. 198 tests au total, tous
verts. Aucun appel OpenAI réel dans les tests.

`ruff check .` : 36 erreurs, identiques (mêmes fichiers, mêmes règles) à celles de
`develop` — comparé via un worktree isolé, aucune nouvelle erreur.

**Vérifié manuellement** sur une base SQLite temporaire isolée (jamais `jury_central.db`,
intégrité re-vérifiée par MD5) : toutes les routes répondent 200, corrigé absent de la
réponse publique, 12 exercices présents, MC01/MC02/Mathématiques inchangés. Seed additif et
idempotent, aucun reset staging.

**Documentation** : `docs/current_state.md`, `docs/changelog.md`,
`docs/content_plan_informatique_francais.md`.

## 2026-09-16 — Informatique AMPCR : mini-cours 02 « Carte mère, formats et connectiques » (ticket #12)

Deuxième cours de la série Informatique AMPCR, contenu et périmètre pédagogique fournis
intégralement par ChatGPT dans le ticket #12. Réutilise **strictement** l'architecture du
ticket #10 — aucun nouveau mécanisme, aucun second moteur IA.

**Matière/UAA** : nouvelle UAA `MC02` (« Carte mère, formats et connectiques ») sous le
module `AMPCR` existant, navigable depuis `/uaa/ampcr-mc02`, juste après MC01.

**Contenu** (`app/seed.py::MC02_BLOCKS`, 24 blocs) : plan, 16 sections de cours (rôle
détaillé de la carte mère, formats ATX/micro-ATX/Mini-ITX, socket et compatibilité,
chipset, slots RAM/DIMM, PCIe, stockage SATA/M.2, alimentation interne ATX/EPS, connecteurs
internes, connectique arrière, F_PANEL, BIOS/UEFI/POST, méthode de compatibilité,
diagnostic no-POST, sécurité/ESD, vocabulaire FR/EN), 12 exercices progressifs (3 blocs) à
correction masquée à la demande, un bloc `ai_exercise` réutilisant le moteur du ticket #10,
une fiche mémo, et l'examen final.

**Contexte IA MC02** : nouvelle entrée
`app/ai/context.py::PEDAGOGICAL_CONTEXTS["ampcr-mc02"]` (notions, compétences 1.1.1–1.1.4/
1.2.3/2.3.2–2.3.3/3.4.1–3.4.2, vocabulaire, contraintes reportant DDR/dual-channel au
mini-cours 03, SATA/NVMe détaillé au mini-cours 04, alimentation/refroidissement au
mini-cours 05). Aucune autre modification du moteur IA (`app/ai/`, routes
`/practice/api/ai/*`) : le bloc `ai_exercise` de MC02 référence simplement cette nouvelle
clé de contexte.

**Examen** : bloc publié avec 10 questions/20 points, aucune réponse ; corrigé complet dans
un second bloc `is_published: False`, jamais servi côté public — même mécanisme
exactement qu'au mini-cours 01.

**Tests** : +8 tests (`tests/test_informatique_mc02.py` : navigation, matière obligatoire,
12 exercices, examen sans correction visible, corrigé non publié, contexte IA enregistré,
génération/correction via le moteur partagé avec le contexte MC02 — vérifié explicitement
que `FakeAIProvider` reçoit `course_key == "ampcr-mc02"`, pas MC01 ; non-régression MC01 et
Mathématiques), `test_seed_is_idempotent` mis à jour pour les nouveaux effectifs. 190 tests
au total, tous verts. `ruff check .` : 36 erreurs, identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé, aucune nouvelle erreur.

**Vérifié** : seed idempotent (second appel = 0 création), MC01 et Mathématiques
inchangés, corrigé de l'examen absent de la réponse HTTP publique.

**Documentation** : `docs/current_state.md`, `docs/content_plan_informatique_francais.md`.

## 2026-09-16 — Moteur générique de génération d'exercices et de correction par IA (complément ticket #10)

ChatGPT a complété le ticket #10 en cours de réalisation : le mini-cours 01 ne doit pas
reposer uniquement sur des exercices figés. Ajout d'un moteur réutilisable de génération
d'exercices à la demande (difficulté facile/moyen/difficile) et de correction par IA (API
OpenAI, côté serveur uniquement), en plus des 12 exercices éditoriaux déjà livrés (conservés
tels quels comme entraînement de référence garanti). Voir
[docs/ai_exercise_engine.md](ai_exercise_engine.md) pour l'architecture complète.

**Nouveau package `app/ai/`** : `schemas.py` (structures JSON typées — jamais de texte libre
non structuré), `context.py` (registre `PEDAGOGICAL_CONTEXTS`, un contexte borné par cours,
rédigé à la main), `prompts.py` (messages + schémas JSON stricts, testable sans réseau),
`provider.py` (interface générique `AIProvider` + hiérarchie d'exceptions),
`openai_provider.py` (implémentation réelle, HTTP via `httpx`, clé API jamais journalisée),
`fake_provider.py` (déterministe, pour les tests), `factory.py` (point d'entrée unique),
`integrity.py` (signature HMAC des exercices générés, réutilise `settings.secret_key`).

**Nouveau type de bloc `ai_exercise`** (`app/models.py::BlockType`, extension minimale et
générique) : `app/ai_exercise_blocks.py::AIExerciseBlockConfig` (JSON `{context_key,
intro}`), rendu par `app/main.py::uaa_detail` + `app/templates/uaa_detail.html`, widget
`app/static/js/ai_exercise.js`. Aucun changement de schéma de base côté SQLite (`type` est
un simple `VARCHAR`, vérifié sur la base staging avant modification).

**Nouvelles routes `app/practice.py`** : `POST /api/ai/generate` (retourne un exercice signé
HMAC) et `POST /api/ai/correct` (vérifie la signature avant tout appel IA — rejette un
énoncé modifié côté client sans jamais interroger le fournisseur). Erreurs claires : 503 si
`OPENAI_API_KEY` absente, 502 en cas d'échec du fournisseur (timeout, réponse invalide), 400
si l'énoncé a été altéré, 404/422 pour les cas invalides — jamais de 500 brut.

**Sécurité** : clé API exclusivement serveur (`.env`, jamais Git, jamais journalisée, jamais
transmise au navigateur) ; réponse candidate toujours traitée comme donnée délimitée à
évaluer, jamais comme instruction (`app/ai/prompts.py`) ; sortie forcée en JSON strict
(`response_format: json_schema`) ; contexte pédagogique borné par cours, jamais l'ensemble
de la base ; aucune écriture automatique dans le contenu éditorial du cours.

**Mini-cours 01** : nouveau bloc « Architecture d'un PC — Génère ton propre exercice (IA) »
(`app/seed.py`), ajouté après les 3 blocs d'exercices éditoriaux et avant la fiche mémo —
les 12 exercices éditoriaux et l'examen final restent inchangés.

**Tests** : +26 tests (`tests/ai/` : prompts, contexte, fournisseur factice, intégrité,
fournisseur réel avec `httpx.post` intercepté — succès, timeout, réponse malformée,
non-fuite de la clé API ; `tests/test_practice_ai_routes.py` : routes de bout en bout avec
`FakeAIProvider`, cas « non configuré » sans aucun mock réseau). 182 tests au total, tous
verts. `ruff check .` : 2 nouvelles occurrences de B008 (`Depends()` en valeur par défaut),
motif déjà présent 4 fois dans le projet avant ce complément — non corrigées, cohérence avec
l'existant plutôt que correction isolée.

**Dépendance** : `httpx` promu de `dev` vers les dépendances principales (`pyproject.toml`)
— nécessaire à `OpenAIProvider` en runtime, déjà présent et vérifié dans le projet (utilisé
jusqu'ici par `TestClient`).

**Vérifié manuellement** : widget affiché sur `/uaa/ampcr-mc01`, `app/static/js/ai_exercise.js`
correctement servi, `POST /practice/api/ai/generate` renvoie 503 avec message clair en
l'absence de clé, 422 sur difficulté invalide, 404 sur bloc inconnu, aucune fuite de
clé/secret dans les réponses. Aucun appel réseau réel effectué (pas de clé API disponible
dans cet environnement) — conforme à l'exigence de tests sans consommation d'API réelle.

## 2026-09-16 — Informatique AMPCR : mini-cours 01 « Architecture générale d'un PC » (ticket #10)

Premier contenu réel pour Informatique AMPCR, cours pilote de la série prévue des 38
mini-cours. Contenu et périmètre pédagogique fournis intégralement par ChatGPT dans le
ticket GitHub #10 (référentiel officiel cité : programme 345/2007/249 AMPCR), implémentés
sans en changer la portée. Aucune régression sur Mathématiques.

**Matière/module/UAA** : `Informatique` (nouvelle matière) → module `AMPCR` → UAA `MC01`
(« Architecture générale d'un PC »), navigable depuis `/subjects`,
`/subjects/informatique`, `/modules/ampcr`, `/uaa/ampcr-mc01`, exactement comme
Mathématiques.

**Architecture (réutilisée, pas réinventée)** :
- `app/seed.py` : `_ensure_subject()`/`_ensure_modules()` extraits du code jusque-là
  spécifique à Mathématiques, pour un seed additif et idempotent **générique**,
  réutilisable par les mini-cours 02–38 et par Français. `seed()` appelle désormais ces
  helpers deux fois (Mathématiques, puis Informatique) au lieu d'un chemin unique câblé en
  dur. Aucun changement de schéma de base de données.
- `app/card_kind.py` : le mot-clé « examen » classe désormais un bloc en carte « exam » (au
  même titre que « mini-test »), pour que « Examen final — ... » réutilise directement
  `ExamCard` sans nouveau type de bloc.
- `app/static/css/design-system.css` : nouveau composant générique `.jc-flow` (schéma de
  flux en étapes reliées par des flèches, responsive, compatible impression) — voir
  `docs/UI_GUIDELINES.md`. Aucun changement JS, aucune nouvelle dépendance.
- Tous les autres mécanismes sont réutilisés tels quels : blocs `markdown`, classification
  de carte par titre, masquage de correction générique
  (`app/static/js/design_system.js::splitExerciseCorrections()`), blocs `is_published`.

**Contenu** : 18 blocs (`MC01_BLOCKS`) — plan, 9 sections de théorie (vue globale, carte
mère, CPU, RAM, stockage, GPU, PSU, périphériques E/S, vocabulaire FR/EN + vocabulaire
ancien du référentiel), 1 scénario d'interaction (ExampleCard), 12 exercices progressifs
répartis en 3 blocs (correction masquée à la demande, mécanisme existant), 1 fiche mémo, et
l'examen final.

**Examen — traçabilité stricte** : le bloc « Examen final... » (publié) contient les 10
questions et le barème (2 pts chacune) mais **aucune réponse**. Le corrigé/barème complet
vit dans un second bloc, « Examen final — Corrigé (réservé formateur, non publié) »,
`is_published: False` — jamais transmis à la route publique
(`app/main.py::uaa_detail` ignore les blocs non publiés), consultable/éditable uniquement
depuis `/admin`. Garantie serveur, pas seulement un masquage CSS/JS côté client.

**Tests** : +14 tests (`tests/test_card_kind.py`, `tests/test_informatique_mc01.py`,
mise à jour de `test_seed_is_idempotent` pour les nouveaux effectifs) — 156 tests au total,
tous verts. `ruff check .` : aucune nouvelle erreur (36 préexistantes, non liées à ce
ticket, déjà signalées avant ce ticket).

**Vérifié manuellement** : serveur démarré sur une base SQLite temporaire isolée (jamais
`jury_central.db`) — `/subjects`, `/subjects/informatique`, `/modules/ampcr`,
`/uaa/ampcr-mc01` répondent 200 ; les 12 exercices et les 5 types de cartes s'affichent
(`jc-card--theory/--example/--exercise/--summary/--exam`) ; le schéma `.jc-flow` est
présent ; le corrigé de l'examen n'apparaît jamais sur la page publique ; l'admin, une fois
connecté, voit bien le bloc corrigé non publié ; Mathématiques (`/uaa/mb32-uaa1`) reste
inchangé.

**Documentation** : `docs/content_workflow.md` (nouvelle section : contenu rédigé depuis un
cahier des charges de ticket, sans fichier `docs/sources_cours/`), `docs/UI_GUIDELINES.md`
(composant `.jc-flow`), `docs/components/ExamCard.md` (mot-clé « examen », variante examen
sans correction révélable), `docs/current_state.md`,
`docs/content_plan_informatique_francais.md` (mise à jour de statut).

## 2026-09-16 — Validation staging réelle du ticket #6 et correction de doc

Première exécution réelle de `scripts/deploy_staging.sh` contre le staging opérationnel,
à la demande explicite de l'utilisateur. Résultat : succès complet, sans interaction
`sudo`, sans échec — voir le rapport de validation transmis en session pour le détail des
vérifications (service, nginx, `/health`, HTTPS public, intégrité de `jury_central.db`).

Cette validation a révélé une inexactitude dans `docs/deployment_staging.md` § 1.1 : le
nom du fichier de configuration nginx documenté (« probablement
`jury-central.lodylands.com` ») ne correspondait pas au fichier réel
(`/etc/nginx/sites-available/jury-central`, sans le domaine dans le nom). Corrigé, avec la
définition systemd également confirmée mot pour mot (§ 1.2, plus besoin de « à
confirmer »). Aucune autre modification : script, comportement de l'application et tests
inchangés.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

## 2026-09-16 — Documenter et automatiser le déploiement staging (ticket #6)

Un environnement staging (`https://jury-central.lodylands.com`, installé manuellement sur
AWS) existe désormais. Ce ticket documente son architecture et ajoute un script de
déploiement prudent, sans toucher à l'infrastructure active (nginx, Certbot, systemd) ni
déployer quoi que ce soit.

**Nouveau `scripts/deploy_staging.sh`** : refuse toute branche autre que `develop`, refuse
un working tree sale, synchronise `origin/develop` en fast-forward uniquement (jamais de
force), installe les dépendances dans le `.venv` existant, exécute `pytest -q` (aucun
redémarrage si échec), ne touche jamais `jury_central.db`, redémarre
`jury-central.service` seulement après succès, puis vérifie que le service est `active` et
que `http://127.0.0.1:8100/health` répond. Ne lit, n'affiche ni ne modifie jamais `.env`.
Vérifié avec `bash -n` et `shellcheck` (aucune erreur), non exécuté contre le staging réel
dans ce ticket (interdit par son périmètre).

**Documentation**
- Nouveau `docs/deployment_staging.md` : architecture staging complète (domaine, nginx,
  systemd, port, `.env`, SQLite, logs), fonctionnement détaillé du script, commandes de
  diagnostic, et rappel explicite que `seed-db`/`reset-db` ne font jamais partie d'un
  déploiement.
- `docs/git_workflow.md` : nouvelle section « Après le merge : déploiement staging »,
  renvoyant vers le document ci-dessus.
- `docs/PROJECT_RULES.md` § 16 : ajout explicite de l'interdiction de modifier
  nginx/Certbot/systemd ou de déployer sans instruction explicite.
- `.env.example` : commentaire `DATABASE_URL` corrigé (la variable est bien lue par
  `app/database.py`, contrairement à ce qu'indiquait l'ancien commentaire).
- `docs/INDEX.md`, `docs/README.md` : référencement du nouveau document.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

## 2026-09-16 — Cadrage Informatique AMPCR et Français CESS P (ticket #4)

Changement de priorité produit : Informatique (AMPCR) devient la priorité n°1, Français
(CESS Professionnel) la priorité n°2, passant devant la suite des mathématiques (MB32
UAA3, MQ32, MQ34). Ticket de cadrage uniquement — **aucun import de contenu, aucun
changement fonctionnel**.

**Constat de l'inventaire** : ni source officielle ni brouillon ChatGPT pour ces deux
matières ne sont présents dans le dépôt (`docs/sources_cours/` ne contient que
Mathématiques ; `app/seed.py` ne définit que la matière Mathématiques). Les suites de
mini-cours Informatique et de 10 cours Français mentionnées comme déjà préparées avec
ChatGPT existent uniquement hors du dépôt à ce stade.

**Documentation**
- Nouveau `docs/content_plan_informatique_francais.md` : inventaire détaillé, cartographie
  proposée (structure Subject/Module/UAA à confirmer par les référentiels officiels
  manquants) pour Informatique puis Français, écarts/sources manquantes, règle de
  traçabilité officiel/brouillon ChatGPT (champ `source_type` proposé, emplacement dédié
  aux brouillons distinct de `docs/sources_cours/`), et neuf tickets atomiques proposés
  (A à I) avec dépendances explicites.
- `docs/current_state.md` et `docs/ROADMAP.md` : priorité et statuts VS004/VS007 mis à
  jour pour refléter ce nouvel ordre et renvoyer vers le plan.
- `docs/INDEX.md` et `docs/README.md` : référencement du nouveau document de planification.

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

**Point à clarifier** (signalé, non tranché — voir `docs/PROJECT_RULES.md` § 11) : la
suite Français ChatGPT est décrite comme « 10 cours » mais seuls 9 intitulés sont donnés
dans le ticket #4 ; à vérifier dès que les fichiers seront fournis.

## 2026-09-16 — Assainissement de la gouvernance documentaire (ticket #2)

Un audit de reprise a mis en évidence plusieurs contradictions documentaires (deux
fichiers de règles concurrents, roadmap désynchronisée, nombre de tests obsolète,
fichiers vides). Ce ticket fixe une source unique de vérité et le workflow
ChatGPT (chef de projet, tickets) → GitHub (source de vérité des tâches) → Claude Code
(développement), avant toute nouvelle fonctionnalité. Aucun changement fonctionnel de
l'application.

**Documentation**
- `docs/PROJECT_RULES.md` : source unique des règles du projet. Fusion du contenu
  pertinent et non contradictoire de l'ancien fichier fantôme `(PROJECT_RULES.md`
  (sécurité, UX, vertical slice, interdits explicites) ; § 6 (pilotage) et § 8 (Git)
  réécrits pour le workflow tickets GitHub ; § 7 et § 11 complétés (tests manuels,
  signalement des décisions produit). Numérotation des règles existantes préservée
  (§ 2 notamment, référencée depuis `docs/components/INDEX.md`).
- Suppression du fichier fantôme `./(PROJECT_RULES.md`, tracké à la racine et
  contradictoire avec `docs/PROJECT_RULES.md` (vision produit, stack, workflow Git
  différents). Contenu utile récupéré ci-dessus ; ce qui contredisait le stack réel
  (Python 3.13, Alembic, HTMX) n'a pas été repris — voir points ouverts.
- `docs/git_workflow.md` réécrit : branches `feature/<ticket>-<slug>` /
  `fix/<ticket>-<slug>` depuis `develop`, commit + push autorisés après tests et
  documentation, aucun merge ni déploiement sans validation explicite.
- `docs/ROADMAP.md` : statuts VS002 et VS003 corrigés pour refléter l'état réel du code
  (Design System livré sur les pages UAA, restant sur les listings ; composant
  `value_table` livré, 9 des 10 types de `EXERCISE_TYPES.md` restants ; automatisation de
  l'import de contenu non implémentée, distinguée de VS003).
- `README.md` : retrait du nombre de tests figé (« 87 tests ») au profit d'un renvoi à
  `pytest -q`, pour éviter une référence à maintenir manuellement à chaque évolution.
- Suppression de `TODO.md` et `docs/SEMANTIC_IMPORT_ENGINE.md` : fichiers vides, sans
  fonction actuelle ni référence ailleurs dans le projet (vérifié par recherche globale).

**Tests** : aucune modification de code applicatif ; suite complète toujours verte
(`pytest -q`).

**Points restant à valider** (signalés plutôt que tranchés, voir `docs/PROJECT_RULES.md`
§ 11) :
- Le fichier fantôme mentionnait HTMX et Alembic comme orientations techniques et
  Python 3.13 comme version cible ; non repris car contredits par le stack réellement
  implémenté et documenté (vanilla JS, pas de migrations, Python 3.12+). À confirmer que
  ce n'est pas une intention produit oubliée.
- `docs/README.md` (index du dossier `docs/`) décrit `development.md` comme la
  « roadmap du projet » et n'y mentionne pas `docs/ROADMAP.md` — incohérence préexistante,
  hors périmètre strict de ce ticket, à traiter séparément.

## 2026-07-14 — VS003.1 : renderer de contenu riche unique

Plusieurs écrans affichaient encore du texte brut (question de quiz, énoncé d'exercice
généré, indice, correction) même quand le contenu source contenait un tableau, une liste ou
une formule — par exemple une question de quiz décrivant un tableau en une phrase :
« Le tableau x : -1, 0, 1 → f(x) : 4, 4, 4 correspond à quelle fonction ? ». Cette tranche
fait passer tous ces écrans par le même renderer que les cours
(`app/content.py::render_markdown`), et convertit ce cas concret en un vrai tableau
Markdown.

**Serveur — un champ `*_html` ajouté à chaque endroit qui envoyait du texte brut** :
- `app/quiz.py` : `QuizConfig.to_public_dict()` ajoute `question_html`.
- `app/exercise_blocks.py` : `exercise_to_public_dict()`/`exercise_to_dict()` ajoutent
  `statement_html`, `hint_html`, `solution_steps_html`.
- `app/value_table.py` : nouvelle fonction `value_table_public_dict()` (`question_html`,
  `hint_html` — ne peut pas vivre dans `generators/exercise_types.py`, qui doit rester
  indépendant de FastAPI) ; `ValueTableCorrection.to_dict()` ajoute `explanation_html`.
- `app/practice.py` : `/api/reveal` et `/api/quiz/{id}/verify` renvoient aussi le HTML
  rendu de la correction/explication.
- `app/main.py` : le widget de quiz isolé utilise désormais `QuizConfig.to_public_dict()`
  (déjà utilisé par le parcours groupé) au lieu d'accéder directement au dataclass — même
  représentation partout, une seule méthode de rendu.

**Client — un seul point d'entrée pour insérer du contenu riche** :
- Nouveau `app/static/js/rich_content.js` : `renderRichContent(container, html)` — injecte
  le HTML déjà rendu, ré-applique les mêmes traitements que les cours (tableaux
  responsives, citations → WarningCard, cellules éditables) et relance MathJax scopé au
  conteneur (MathJax ne rescane pas seul le contenu inséré après le chargement initial).
- `app/static/js/design_system.js` : `wrapBlockquotesAsWarningCards`,
  `wrapTablesResponsively`, `makeEmptyCellsEditable` acceptent maintenant un `root` et sont
  regroupées dans `enhanceRichContent(root)`, appelée au chargement de la page **et** par
  `renderRichContent()` — plus de duplication entre le traitement initial et le traitement
  du contenu inséré dynamiquement.
- `quiz.js`, `exercise.js`, `value_table.js` : toute insertion de texte (`textContent`)
  remplacée par `renderRichContent()` avec le champ `*_html` correspondant.

**Contenu** : la question de quiz « Le tableau x : -1, 0, 1 → f(x) : 4, 4, 4 correspond à
quelle fonction ? » (`app/seed.py`, quiz Fonction constante) reformulée en question courte +
tableau Markdown (`| $x$ | -1 | 0 | 1 |` / `| $f(x)$ | 4 | 4 | 4 |`) — mêmes valeurs, même
bonne réponse, même explication, uniquement la présentation change.

**Tests** : 14 nouveaux tests (`tests/test_rich_content.py`) couvrant chaque champ `*_html`
ajouté, le rendu Markdown d'une question de quiz (tableau, liste, texte simple), et — cas
concret demandé — la vérification que cette question précise produit un `<table>` avec
`<td>4</td>` sur la page publique de MB32 UAA1 —, ainsi que les routes `/api/reveal` et
`/api/quiz/{id}/verify`. Un test existant (`test_quiz.py`) mis à jour pour le nouveau champ.
142 tests au total, `ruff check .` sans erreur.

Vérifié manuellement après `reset-db` : la question du quiz Fonction constante s'affiche
comme un vrai tableau (extrait et vérifié depuis le JSON `data-questions` de la page), les
routes `/api/reveal`, `/api/quiz/{id}/verify`, `/admin/value-table-demo/verify` renvoient
toutes leur champ `*_html`, `/admin/generators` bascule toujours correctement entre les deux
rendus, aucune régression sur les autres pages.

## 2026-07-14 — VS003 (suite) : branchement du composant value_table sur la fonction constante

Le composant `value_table` livré précédemment n'était utilisé nulle part (seulement une
démo admin fixe). Cette tranche le branche réellement : les exercices générés de la
fonction constante (MB32 UAA1) affichent désormais un vrai tableau interactif sur la page
publique, au lieu d'un énoncé texte à réponse unique.

**`generators/maths/constant_function.py`** — réécrit : retourne un `InteractiveExercise`
(`value_table`) au lieu d'un `GeneratedExercise`. Les quatre anciens types d'exercice
(image/table/find_p/match) sont unifiés en un seul format « tableau de valeurs de f(x) = p à
compléter » — la logique de difficulté (plage de p, `_random_p`) et le déterminisme par seed
sont inchangés. `find_p`/`match` (trouver p à partir d'un point/graphique) restent couverts
par le quiz et les exemples du cours, déjà présents dans MB32 UAA1.

**`generators/base.py`** — `ExerciseGenerator.__call__` retourne désormais
`GeneratedExercise | InteractiveExercise` : les deux moteurs coexistent, chaque appelant
détecte le type retourné plutôt que d'en supposer un seul. `maths.equations.linear_equation`
n'a pas été modifié.

**Suppression de la duplication** entre les deux moteurs :
- `generate_exercises()` (`app/exercise_blocks.py`) retourne désormais les objets bruts
  (plus de conversion en dict interne) : un seul endroit (la route `uaa_detail`) décide
  comment afficher chaque type, au lieu de dupliquer cette décision.
- `/practice/api/value-table/verify` (nouveau, générique) régénère l'exercice depuis
  `(generator, difficulty, seed)` et vérifie cellule par cellule — même principe que
  `/api/verify` pour l'ancien moteur, réutilise `check_value_table_answers()` déjà écrit
  pour la démo admin.
- `/admin/generators` (outil de debug) détecte le type retourné et affiche soit le composant
  interactif `value_table` (réutilisation totale de `value_table.js`), soit l'ancienne vue
  `<dl>` — un seul outil pour les deux moteurs plutôt que deux outils séparés.
- `app/static/js/value_table.js` : le payload de vérification inclut
  `generator`/`difficulty`/`seed` uniquement quand ces attributs sont présents sur le
  conteneur — un seul renderer sert à la fois la démo fixe et les exercices générés.
- Garde-fous ajoutés sur les routes de l'ancien moteur (`/api/generate`, `/verify`,
  `/reveal`) : erreur claire (400) si un générateur `value_table` y est appelé par erreur,
  plutôt qu'un plantage.

**Tests** : 13 nouveaux tests d'intégration
(`tests/test_practice_value_table.py`) couvrant la page publique de MB32 UAA1 (widget
value_table présent, ancien widget absent, aucune fuite de réponse), l'endpoint générique de
vérification (correct/incorrect), les garde-fous croisés entre les deux moteurs, et la
non-régression complète de `maths.equations.linear_equation` (génération, vérification,
outil admin). Tests existants adaptés : `tests/generators/test_constant_function.py`
(entièrement réécrit pour le nouveau format), `tests/generators/test_architecture.py` (le
test de contrat accepte maintenant les deux types), `tests/test_exercise_blocks.py`
(`generate_exercises()` retourne des objets, plus des dicts). 128 tests au total, `ruff
check .` sans erreur.

Vérifié manuellement après `reset-db` : `/uaa/mb32-uaa1` affiche 3 tableaux interactifs pour
la fonction constante (aucune trace de `exercise-widget` ni de réponse dans le HTML),
vérification cellule par cellule fonctionnelle avec un vrai seed extrait de la page,
`/admin/generators` bascule correctement entre les deux rendus selon le générateur choisi,
`/admin/value-table-demo` toujours fonctionnel, aucune régression sur les autres pages.

## 2026-07-14 — VS003 : premier composant d'exercice interactif officiel (value_table)

Démarrage de VS003 (voir `docs/ROADMAP.md`). Implémente le format officiel décrit dans
`docs/EXERCISE_TYPES.md` : « le générateur ne produit jamais de HTML, uniquement des
données ; le rendu appartient exclusivement au frontend. » Premier type construit :
`value_table` (tableau de valeurs à compléter, vérifié cellule par cellule). Aucun
générateur existant n'a été modifié — uniquement la nouvelle architecture, son renderer et
ses tests.

**`generators/exercise_types.py`** (nouveau) — `InteractiveExercise` : enveloppe générique
`{type, question, data, answer, hint, explanation, difficulty, seed}` commune à tous les
futurs types d'exercices interactifs. `to_public_dict()` exclut toujours `answer` ; seul
`to_full_dict()` (serveur / debug admin) l'inclut.

**`generators/value_table.py`** (nouveau) — `ValueTableRow`, `ValueTableData`
(colonnes + lignes, cellules éditables ou non), `build_value_table_exercise()`. La position
des cellules éditables (`editable_positions()`, ordre lignes puis colonnes) définit l'ordre
attendu de `answer["cells"]` — une liste à plat, conforme à l'exemple officiel du document
(une seule ligne éditable) et généralisée aux tableaux multi-lignes.

**`app/value_table.py`** (nouveau) — `check_value_table_answers()` : vérification cellule
par cellule, réutilise `app/answer_checking.py` (comparaison exacte via `Fraction`, aucun
`eval()`) comme les quiz et exercices générés existants.

**`app/static/js/value_table.js`** (nouveau) — construit entièrement le tableau (aucun HTML
reçu du serveur), champs de saisie sur les cellules éditables, bouton Vérifier, indice
optionnel, coloration verte/rouge cellule par cellule après vérification, correction
détaillée (explication, jamais un simple Correct/Incorrect). Aucune dépendance JS externe.

**`app/static/css/design-system.css`** — `.value-table` réutilise le style des tableaux de
VS002.1 (bordures, padding, en-tête ombré) pour rester homogène ; états `.jc-fill-input
--correct`/`--incorrect` ; règle d'impression dédiée (`@media print`) qui vide visuellement
les cellules de saisie sans afficher texte, couleur ni correction — conforme à
`docs/EXERCISE_TYPES.md` (« Mode impression : zones vides, aucune correction, aucune
interaction »).

**Outil de debug** : `/admin/value-table-demo` (admin uniquement) prévisualise le composant
avec un exercice fixe (`f(x) = 2x + 1`, une ligne donnée + une ligne à compléter), sans être
relié à un générateur — sert à tester l'architecture de bout en bout avant la prochaine
étape (brancher un vrai générateur, hors périmètre de cette tranche).

**Tests** : 28 nouveaux tests (`tests/test_value_table.py`) — structures de données,
validation, ordre des cellules éditables sur tableaux multi-lignes, vérification correcte/
incorrecte/partielle, formats numériques (virgule et point), `to_public_dict()` ne contient
jamais `answer`, protection admin de la démo. 115 tests au total, `ruff check .` sans
erreur. Vérifié manuellement : page de démo (aucune trace de la réponse dans le HTML
généré), vérification cellule par cellule via l'API, aucune régression sur les autres pages.

## 2026-07-14 — VS002.1 : véritables tableaux pédagogiques

Première petite fonctionnalité de la fin de VS002 (voir `docs/ROADMAP.md`). Objectif :
tous les tableaux de Jury Central doivent être lisibles, homogènes et utilisables sur
mobile, sans toucher aux quiz, à la navigation ni à l'impression.

**`app/static/css/design-system.css`**
- Style de tableau propre à Jury Central (bordures, padding `0.55rem 0.75rem`, en-tête
  ombré, lignes zébrées, padding réduit en mobile) plutôt que la classe utilitaire
  `table-sm` de Bootstrap, jugée trop dense pour des tableaux de formules/valeurs.
- Nouvelle classe `.jc-list-alpha` : liste `<ol>` stylée en `a, b, c...`
  (`list-style-type: lower-alpha`) pour les sous-questions numérotées par lettre.

**`app/static/js/design_system.js`**
- `wrapTablesResponsively()` n'ajoute plus `table-bordered`/`table-sm` (remplacés par le
  CSS ci-dessus) ; le défilement horizontal (`table-responsive`) est inchangé.

**`app/seed.py`**
- Trois exercices de MB32 UAA2 (Solides — Exercice « connaître », Solides — Exercice 1,
  Mini-test Question 2) énuméraient leurs sous-questions en `a) ... b) ... c) ...` dans un
  seul paragraphe Markdown (aucun marqueur de liste reconnu par le moteur Markdown). Reformatés
  en `<ol class="jc-list-alpha">` (HTML direct dans le Markdown, même procédé que le
  graphique SVG de la perspective cavalière) : mêmes lettres affichées, vraie liste HTML
  accessible. Texte inchangé, uniquement la structure de présentation.
- Audit du contenu : aucun autre exercice « à compléter » sans tableau réel, aucune autre
  liste lettrée orpheline.

**Tests** : 87 tests inchangés (aucune modification de logique métier), `ruff check .`
sans erreur. Vérifié manuellement après `reset-db` sur `/uaa/mb32-uaa1` et `/uaa/mb32-uaa2` :
les trois listes converties s'affichent en `<ol class="jc-list-alpha"><li>...`, le tableau à
compléter du mini-test garde ses 8 cellules éditables, aucune régression sur les quiz
(`quiz-run` inchangé) ni sur les autres pages.

## 2026-07-14 — Design System réutilisable (cartes, exercices interactifs, tableaux éditables)

Mise en œuvre de `docs/UI_GUIDELINES.md`. Objectif : transformer l'affichage d'une UAA — un
mur de blocs Markdown identiques — en une véritable expérience d'apprentissage, sans toucher
au contenu pédagogique existant (MB32 UAA1 et UAA2), uniquement sa présentation et son
interaction.

**Composants (`app/templates/_cards.html`)**
- Macro générique `card(meta, title)` + alias nommés `TheoryCard`, `ExampleCard`,
  `ExerciseCard`, `QuizCard`, `WarningCard`, `SummaryCard` — icône, libellé et couleur par
  type, conformes au code couleur de `UI_GUIDELINES.md` (bleu=information, vert=réussite,
  orange=méthode/exercice, rouge=attention, or=mémo).
- `app/card_kind.py` : classe un bloc de leçon en type de carte à partir de son **titre
  uniquement** (ex. « Solides — Cours » → théorie, « Solides — Exercices » → exercice,
  « Mini-test final » → exam, « Fiche mémo » → résumé) — aucune lecture ni modification du
  contenu.
- `app/static/css/design-system.css` : styles des cartes, tableaux, citations, champs
  éditables ; responsive (padding réduit en mobile) ; règles d'impression (cartes aplaties
  pour la fiche mémo imprimable existante).

**Interactions (`app/static/js/design_system.js`)**
- Citations Markdown (`> Piège...`) transformées automatiquement en WarningCard.
- Tableaux enveloppés dans `.table-responsive` (défilement horizontal) + classes Bootstrap.
- Cellules de tableau vides rendues éditables (`<input>` injecté) — couvre notamment le
  tableau à compléter du mini-test UAA2, sans marquage spécial dans le contenu.
- Exercices rédigés (blocs classés « exercice » ou « exam ») : la correction (repérée par un
  paragraphe `**Correction :**` ou un titre `## Correction...`) est déplacée dans un conteneur
  masqué, remplacée par un champ de réponse libre et un bouton « Afficher la correction ».
  Fonctionne aussi bien sur le nouveau contenu UAA2 (« Correction : » inline) que sur l'ancien
  contenu UAA1 (« ## Correction détaillée ») sans aucune modification de texte.
- Barre de progression de lecture de la leçon (scroll), sticky en haut du contenu.

**`app/static/js/quiz.js`**
- Le parcours de quiz groupé (`quiz-run`, utilisé par tous les quiz de UAA1 et UAA2)
  n'affichait que « Correct. »/« Incorrect. » après chaque réponse ; il affiche désormais
  systématiquement l'explication retournée par le serveur, comme le fait déjà le widget de
  quiz isolé. Feedback aligné sur `UI_GUIDELINES.md` (✅ Correct / ❌ Incorrect).

**`app/main.py` / `app/templates/uaa_detail.html`**
- Chaque bloc rendu (markdown, exercice généré, quiz, quiz groupé) est désormais enveloppé
  dans le composant carte correspondant, plutôt que dans une simple `<section>` Bootstrap.

**Décisions volontairement limitées à cette tranche**
- Les exercices rédigés restent en auto-évaluation (comparaison libre avec la correction) et
  non en correction automatique : la plupart n'ont pas de réponse unique vérifiable, et
  extraire une réponse par analyse de texte aurait été peu fiable. `answer_checking.py`
  continue d'être utilisé tel quel pour les quiz et exercices générés.
- Le mini-test reste un seul bloc à correction masquée plutôt qu'un parcours paginé
  question par question (Précédent/Suivant/Terminer) — voir `current_state.md`, Points
  ouverts.

**Tests** : 87 tests inchangés (aucune modification de logique métier), `ruff check .` sans
erreur. Vérifié manuellement sur `/uaa/mb32-uaa2` et `/uaa/mb32-uaa1` (aucune régression),
ainsi que `/`, `/subjects`, `/modules/mb32`, `/admin/login`, `/practice/equations`.

## 2026-07-14 — Import complet de MB32 UAA2 (Géométrie)

Import de la première UAA via le nouveau workflow décrit dans `docs/IMPORT_WORKFLOW.md`, à
partir de la source officielle unique
`docs/sources_cours/CESS/P/Mathématiques/MB32/UAA2/cours.html` (non modifiée). Contrairement à
MB32 UAA1 (une seule leçon détaillée, le reste en placeholders non publiés), UAA2 est intégrée
**intégralement** : aucune section du cours source n'est omise, résumée ni reformulée.

**Contenu**
- UAA `mb32-uaa2` (position 2 dans MB32, publiée), 38 blocs de leçon répartis en 6 leçons
  conformes à `docs/content_workflow.md` et `docs/REFERENCE_UAA.md` : Solides, Perspective
  cavalière, Patrons, Vues coordonnées, Aires, Volumes.
- Chaque leçon reprend, quand la source le permet : présentation, cours (vocabulaire, tableaux,
  formules), exemples résolus, exercices rédigés avec correction détaillée, et un court quiz
  auto-corrigé (2 à 3 questions par leçon, regroupées via `QuizConfig.group`) repris directement
  des exercices déjà présents dans le cours plutôt que d'un contenu inventé.
- Le schéma SVG de la perspective cavalière est repris tel quel (le rendu markdown laisse
  passer le HTML brut, comme pour `<div class="jc-graph-constant">` dans UAA1).
- Contenu transversal placé en fin d'UAA (comme dans la source) : mini-test final type examen
  avec sa correction, fiche mémo récapitulative, liste de ressources externes.
- Formules converties en LaTeX (`$...$`) pour un rendu MathJax cohérent avec UAA1 ; le texte du
  cours (théorie, énoncés, corrections) n'est ni résumé ni reformulé.

**Décision technique** : les questions de quiz numériques n'utilisent que des réponses exactes
(ex. `96`, `120`) car `answer_checking.py` compare des `Fraction` exactes sans tolérance ; les
résultats impliquant π (arrondis dans la source, ex. ≈791,7 cm²) sont posés en QCM plutôt qu'en
question numérique, pour éviter un quiz où la valeur exacte attendue diffère de l'arrondi
affiché.

**Code**
- `app/seed.py` : ajout de `UAA2_CODE`/`UAA2_TITLE`/`UAA2_BLOCKS` (même convention que UAA1).
  `seed()` refactorée pour appeler un helper `_seed_uaa()` commun aux deux UAA plutôt que de
  dupliquer la logique de création — reste strictement additif et idempotent.
- `tests/test_admin_content_hierarchy.py` : `test_seed_is_idempotent` mis à jour (2 UAA et
  `len(UAA1_BLOCKS) + len(UAA2_BLOCKS)` blocs désormais attendus après un seed).
- 87 tests au total (inchangé), `ruff check .` sans erreur.
- Vérifié manuellement : `/uaa/mb32-uaa2` (200, 30 sections, tableaux et SVG rendus, MathJax
  actif), `/modules/mb32` (liste UAA1 et UAA2), admin (`/admin/modules/1` liste les deux UAA),
  API `/practice/api/quiz/{id}/verify` (réponses correctes/incorrectes, QCM et numérique).

## 2026-07-14 — Gestion complète de la hiérarchie de contenu depuis l'admin

Objectif : supprimer la dépendance fonctionnelle à `app/seed.py` pour créer du contenu
pédagogique réel. Il est désormais possible de créer MB32 UAA2 (ou toute autre
matière/module/UAA) **entièrement depuis l'administration**, sans modifier de code ni
relancer `seed-db` — vérifié manuellement de bout en bout. Voir `docs/admin.md`, section
"Gérer la hiérarchie de contenu", et `docs/content_workflow.md`.

**Modèles (changement de schéma, nécessite `reset-db` en local)**
- `UAA.position` (entier, ordre d'affichage dans un module) et `UAA.is_published` (bool,
  défaut `False`) — mêmes conventions que sur `LessonBlock`.
- `Module.uaas` trié par `position` (comme `UAA.lesson_blocks` l'est déjà par `position`).

**Admin — nouvelles routes (15), réutilisant entièrement le panneau existant**
- Matières : créer, modifier, supprimer (`/admin/subjects/new`, `/admin/subjects/{id}/edit`,
  `/admin/subjects/{id}/delete`).
- Modules : créer, modifier, supprimer, imbriqués sous une matière.
- UAA : créer, modifier, supprimer, avec position et case "Publiée".
- Validation serveur : champs obligatoires, longueurs alignées sur les colonnes de la base,
  unicité des slugs et des noms vérifiée explicitement avant écriture (message clair plutôt
  qu'une erreur SQL brute), slug vide impossible. Aucun `eval()`.
- Suppression avec confirmation affichant le **nombre exact** d'éléments supprimés en
  cascade (modules/UAA/blocs), calculé côté serveur.
- Une UAA non publiée disparaît de la liste publique de son module et sa page renvoie 404.

**`app/seed.py` — rôle clarifié, plus jamais destructif silencieusement**
- Ne modifie plus le titre d'une UAA existante à chaque exécution (régression corrigée :
  cela aurait écrasé un titre édité depuis l'admin).
- Affiche un résumé clair (créé / conservé / retiré) à chaque exécution.
- Nouvelle commande **distincte et explicite** `reset-db` (supprime la base puis reseed) —
  jamais appelée automatiquement.
- `app/database.py` lit `DATABASE_URL` depuis l'environnement si définie (base de
  développement inchangée par défaut) — permet aux tests de ne jamais toucher
  `jury_central.db`.

**Tests — première suite `TestClient`**
- `tests/conftest.py` : base SQLite temporaire isolée, fixtures `client`/`admin_client`/
  `db_session`.
- `tests/test_admin_content_hierarchy.py` (17 tests) : CRUD des 3 niveaux, rejet de slug
  dupliqué, protections admin (redirection sans session), suppression en cascade,
  publication/dépublication, idempotence du seed, et garantie que le seed ne modifie jamais
  un titre ou un contenu édité manuellement.
- 87 tests au total (+17). `ruff check .` sans erreur.

## 2026-07-13 — Tranche verticale : MB32 UAA1 → Fonction constante

Première expérience étudiante complète de bout en bout (cours, graphique interactif,
exercices générés à l'infini, quiz noté, fiche mémo imprimable), plutôt qu'une UAA entière
esquissée superficiellement. Voir `docs/mb32-uaa1.md` pour le détail complet.

**Contenu pédagogique**
- Section "Fonction constante" de MB32 UAA1 entièrement rédigée : présentation, cours
  (MathJax), graphique interactif (Plotly, curseur sur $p$), 5 exemples résolus, 1 exercice
  guidé avec correction détaillée, exercices générés automatiquement, quiz de 10 questions
  (QCM, vrai/faux, numérique), fiche mémo imprimable.
- Ancien contenu placeholder/démo devenu obsolète supprimé au profit du vrai contenu
  (migration automatique dans `app/seed.py` via `OBSOLETE_DEMO_BLOCK_TITLES`).

**Nouveau générateur**
- `maths.functions.constant_function` : fonction constante $f(x) = p$, 4 formulations, 3
  niveaux, déterministe par seed. Ajout du champ `hint` (indice) sur `GeneratedExercise`,
  rétrocompatible.

**Validation des réponses (changement d'architecture)**
- Les réponses correctes ne sont plus jamais envoyées au navigateur avant que l'étudiant ait
  répondu (exercices générés et quiz). Nouveau module `app/answer_checking.py` (parsing et
  comparaison exacte via `Fraction`, aucun `eval()`). Trois nouvelles routes publiques dans
  `app/practice.py` : `POST /api/verify`, `POST /api/reveal`,
  `POST /api/quiz/{block_id}/verify`. `app/exercise_blocks.py` distingue désormais une
  représentation publique (sans réponse) et une représentation complète (réservée à l'outil
  de debug admin `/admin/generators`).

**Quiz : nouveaux modes**
- `QuizConfig` étendu (rétrocompatible) : `answer_type` (`choice` ou `numeric`),
  `correct_value`, `group`, `order_in_group`. Plusieurs blocs `quiz` partageant un `group`
  sont fusionnés côté public en un seul parcours interactif (une question à la fois, score,
  bouton "Recommencer") — sans changement de schéma de base de données.

**Graphiques interactifs**
- Plotly chargé via CDN, uniquement sur les pages qui en ont besoin. Un contenu Markdown
  active un graphique via un marqueur HTML (`<div class="jc-graph-constant">`), détecté et
  monté par `app/static/js/interactive_graph.js`. Pas de nouveau type de bloc, pas de
  dépendance Python.

**Admin**
- Formulaire de bloc quiz étendu : type de réponse, réponse numérique correcte, groupe et
  ordre dans le groupe.

**Tests**
- 70 tests au total (+41 depuis la dernière tranche) : générateur `constant_function` (10),
  contrat d'architecture étendu automatiquement (2 générateurs), `answer_checking` (11),
  `QuizConfig` étendu (5 nouveaux), séparation public/complet de `exercise_blocks` (2
  nouveaux).

**Décisions volontairement reportées** (voir `docs/mb32-uaa1.md`, limites restantes) : pas
de modèle `Chapter` dédié, pas d'Alembic, progression toujours au niveau de l'UAA entière —
aucune de ces décisions ne bloque le contenu actuel ni n'introduit de dette qui casserait
une évolution future.

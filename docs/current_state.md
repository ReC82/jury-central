# Jury Central - État actuel du projet

Ce document décrit l'état actuel du projet.

Il doit être mis à jour après chaque étape importante.

Il ne doit pas contenir d'historique détaillé (voir `changelog.md`) ni de documentation technique complète (voir `ARCHITECTURE.md`).

---

# Vision du projet

Jury Central est une plateforme de préparation aux examens des Jurys de la Fédération Wallonie-Bruxelles.

L'objectif est de permettre l'intégration rapide de nouveaux cours officiels et de proposer un environnement complet de préparation :

- cours
- quiz
- exercices
- examens
- suivi de progression

---

# État général

## Projet

Statut : En développement actif.

Le socle technique est en place.

Le développement se concentre actuellement sur l'import automatisé des contenus pédagogiques.

---

# Fonctionnalités disponibles

## Navigation publique

Disponible.

Navigation :

Matière → Module → UAA → Leçons.

Depuis le ticket #22, chaque UAA expose trois espaces distincts au lieu d'un flux unique
mélangeant théorie/exercices/examen : **Cours** (`/uaa/{slug}`, théorie/exemples/fiche
mémo uniquement), **S'entraîner** (`/uaa/{slug}/practice`, exercices structurés et
historiques, génération IA) et **S'évaluer** (`/uaa/{slug}/exam`, examen final). Une
navigation par onglets (`_uaa_space_nav.html`) indique toujours l'espace actif ; la
classification est un champ explicite `LessonBlock.space` (COURSE/PRACTICE/EXAM, jamais
déduit du titre ou du type à l'exécution) — voir
`docs/claude-reports/2026-09-16_ticket-22_separation-cours-practice-exam.md`.

Depuis le ticket #136, la navigation part d'un **parcours** : accueil (« Choisir mon
parcours » / « Continuer »), assistant Diplôme → Forme → Option (`/parcours`), tableau de
bord `/mon-parcours` (prochaine étape, reprise, tuiles de matières, progression réelle),
chemin de cours sur `/modules/{slug}` et cours en séquences courtes. Les routes historiques
restent servies. Voir `docs/parcours_v1.md`.

Composition des cours sur ordinateur (ticket #148) : la largeur de lecture n'est plus
portée par la prose (`.jc-prose` sans plafond) mais par la composition — théorie FSE
« explication + Les mots clés » côte à côte (`.jc-theory-layout`), théorie FSE02 en
groupes pédagogiques, et carte de texte seul réduite à une largeur de lecture
(`.jc-card--reading`, détection `app.content.is_text_only_html`). Voir
`docs/claude-reports/2026-10-21_ticket-148-composition-desktop.md`.

Documents sources composés (ticket #149) : entraînement, examen blanc, quiz, résultats et
page `/documents/{id}` rendent chaque document selon sa nature (mail, affiche, publication
de réseau social/groupe, page de média, forum, conversation, note sur papier à en-tête,
fiches numérotées, tableau, budget, circuit, chaîne de flux, bulletins) via un composant
unique `app/templates/_document_layouts.html`, alimenté par `app/v1/document_layouts.py`.
Une mise en page est liée au titre ET à l'empreinte du texte exact de la version (texte
modifié → rendu générique lisible) ; les 30 documents FSE installés sont couverts. Un
nouveau document peut être créé directement structuré (`content_json={"layout": {...}}`).
Les mentions entre crochets deviennent une note discrète, les renvois de cours et les
annotations-réponses listés dans `omitted` ne sont plus affichés (ils restent dans le texte
transmis à la correction). Voir `docs/claude-reports/2026-10-21_ticket-149-supports-visuels.md`.

Références documentaires résolvables (ticket #151) : `short_answer`, `long_answer`,
`classification` et `document_analysis` acceptent `source_document_version_ids` (tous les
documents du dossier à montrer, document principal inclus) — l'élève et le correcteur
voient la même liste. Résultats et export reprennent le libellé de session (« Document 3 :
Réactions des groupes concernés ») ; le correcteur reçoit le numéro réel dans le titre.
`app/v1/document_references.py` : liste des questions de dossier corrigées
(`dossier_repairs`), mise à niveau idempotente d'une banque déjà importée par nouvelle
version (`repair_dossier_references`, appelée par `app.seed`) et audit
(`audit_document_references`). Voir `docs/claude-reports/2026-10-22_ticket-151-references-documentaires.md`.

Consignes FSE autonomes (ticket #152) : `app/v1/prompt_clarity.py` est la seule liste des
consignes corrigées (`clarity_repairs`). Les 15 remises en ordre de méthode FSE02–FSE16
sont annoncées comme « Rappel de méthode (cours FSEnn « … », sans document à analyser) »
et ne gardent que des étapes à ordre réellement contraint. FSE16 « réactions » classe effet
attendu / limite ou coût, avec la proposition (document 1) affichée à côté du document 3.
FSE15 « aide au média » sépare deux actions (a)/(b). FSE09, FSE06 et FSE12 n'ont plus de
consigne « maintenant / ces trois autres / à présent ». Le document FSE09 servi en
entraînement/examen/quiz est une version d'examen qui décrit la matière sans nommer le
niveau de pouvoir (`FSE09_SITUATIONS_EXAM_TEXT`, mise en page dédiée) ; le cours garde le
texte d'origine. Banque neuve : `apply_clarity` dans chaque import FSE ; banque déjà
importée : `repair_prompt_clarity` (appelée par `app.seed`, nouvelles versions, idempotent).
Audit : `audit_prompt_clarity`. Remise en ordre (entraînement/examen) : un ordre n'est
enregistré que si chaque position 1..n est utilisée une fois ; sinon la question reste sans
réponse et les choix partiels sont conservés (`positions`). Voir
`docs/claude-reports/2026-10-22_ticket-152-consignes-fse-contexte.md`.
Ancienne session (retour du 22/10) : `session_question_document_ids` (`session_service`)
garde la version figée mais ajoute, signalés « ajouté », les documents de contexte que la
version courante de la même question montre en plus (documents figés tous conservés, même
type) ; élève, correction IA et résultats utilisent cette même liste.

Cas nouveaux FSE (ticket #129, lots 1-2 : FSE01→FSE08) : `app/v1/fse_cases.py` (mécanisme
commun) + `app/v1/fse01_cases.py` à `fse08_cases.py` (contenu). Chaque cas ajoute un document structuré
(`content_json["layout"]`) et ses questions (`GenerationSource.MANUAL`, import idempotent
par titre de document, appelé par `_ensure_bank_seeded` — FSE17 amorce les cas de
FSE01→FSE16). FSE01 : affiche d'un atelier de réparation (composant `poster_sheet` :
illustration SVG enregistrée comme `Asset` via `SourceDocumentVersion.asset_id` + texte
exact en HTML), conversation de groupe de futsal, note de service jargonneuse, trois
mini-situations à choix multiple — 17 questions. Sélection : après la difficulté demandée,
`case_ranker` fait passer les cas nouveaux jamais vus, puis les cas dont l'élève a déjà vu
le document, puis les exemples commentés du cours (`CourseExamples`) ; no-op pour les
matières sans exemples déclarés. Une question dont l'illustration est invalide ou absente
du disque n'est jamais servie (`unusable_document_question_ids`). Voir
`docs/claude-reports/2026-10-22_ticket-129-fse-cas-nouveaux-visuels.md`.

---

## AMPCR — Pratique écrite (ticket #192)

Socle du parcours de l'épreuve pratique écrite AMPCR (cycle 2026-2027/1) : `/ampcr-pratique`
(consignes du jour, 5 modules, emplacements PR01–PR30 / EX01–EX06 « à venir » sauf PR01, PR02, PR03, PR04, PR05, PR06, PR07, PR08, PR09, PR10, PR11, PR12, PR13, PR14, PR15, PR16, PR17, PR18, PR19, PR20, PR21, PR24, EX01, EX02 et EX03),
`/ampcr-pratique/matrice` (38 exigences officielles des pp. 5-6 + 3 compléments) et `/ampcr-pratique/format-exercice`. Voir `ampcr_pratique_v1.md`.

**Numérotation (audit #236, 2026-10-26)** : codes, titres et matières des 30 cours et 6 examens
blancs = ceux des tickets GitHub (#193–#234), qui font foi ; modules P1 matériel (PR01–PR06,
EX01), P2 systèmes (PR07–PR12, EX02), P3 câblage (PR13–PR17, EX03), P4 réseau (PR18–PR25,
EX04), P5 méthode (PR26–PR30) + examens globaux EX05/EX06. Test de non-régression :
`tests/test_ticket236_ampcr_pratique_numerotation.py`.

**Premier cours publié (ticket #193) : PR06 « Diagnostic des pannes matérielles »**
(`/uaa/ampcr-pratique-pr06`), module `AMPCR-PRATIQUE` de la matière Informatique, séparé du
module théorique `AMPCR` (cours, banque, sessions et progression distincts). Cours en 15 blocs
(matière A-D du ticket, 8 schémas SVG construits sur données vérifiées, 4 cas résolus,
12 exercices corrigés) ; « S'entraîner » = les 12 exercices, « Examen blanc » = mini-examen de
10 questions à réponse libre (2 points chacune, note affichée sur 20). Réserves séparées par
`QuestionVersion.prompt_version` (`ampcr-pratique-pr06:practice|exam`), strictement banque
(aucune génération IA). Voir `app/v1/ampcr_pratique_bank.py`.

**Deuxième cours publié (ticket #194) : PR11 « Messages d'erreur Windows/Linux — diagnostic et
interventions écrites »** (`/uaa/ampcr-pratique-pr11`), même module et même intégration que
PR06. 16 blocs (matière 1-6 du ticket : méthode universelle, démarrage et partitions, Windows,
Linux, réseau et pannes intermittentes, compte rendu), 11 figures SVG construites sur données
testées (arbre « à quelle étape l'erreur survient-elle ? », flux lire → valider, plan GPT,
8 captures fictives : Windows Boot Manager, WinRE, écran bleu, Observateur d'événements,
Gestionnaire de périphériques, terminaux Linux), 5 cas résolus, 16 exercices corrigés
(6 analyses de captures/journaux, 6 procédures dont 2 remises en ordre `ordering`, 4 cas
croisés), mini-examen de 10 questions /20. Nouveautés partagées : documents d'exercice
« console » (mise en page `console` de `_document_layouts.html`, police à chasse fixe) et
questions `ordering` dans la banque pratique (`Ordering`, `item_content`).

**Troisième cours publié (ticket #197) : PR15 « Câblage RJ45 T568A/B — fabrication, schémas et
tests »** (`/uaa/ampcr-pratique-pr15`), même intégration. 13 blocs (matière 1-6 du ticket :
supports et connecteurs, brochage et paires, droit/croisé et Auto MDI-X, fabrication, tests et
dépannage, contexte professionnel), 14 figures SVG **calculées depuis `T568A`/`T568B`**
(brochages orientés, comparaison A/B, ordre faux et paires séparées, câbles droit et croisé,
anatomie de fiche, sertissage, 4 affichages de testeur fictifs, chaîne baie → PC), 4 exemples
corrigés, 16 exercices (6 brochage, 4 testeur, 3 choix, 3 procédures), mini-examen 10 questions
/20 (`app/v1/ampcr_pratique_pr15_*.py`). Aucune image générée.

**Quatrième cours publié (ticket #198) : PR16 « Câble coaxial et BNC — impédance, fabrication et
diagnostic écrit »** (`/uaa/ampcr-pratique-pr16`), même intégration. 15 blocs (matière 1-12 du
ticket : structure du coax, impédance 50/75 Ω et réflexions, BNC/T/terminateurs, 10BASE2,
10BASE5, vidéo 75 Ω, fabrication et outils, schémas, diagnostic, sécurité et rapport), 14
figures SVG dont le bus 10BASE2 et ses versions fautives **dessinés depuis un modèle `Bus`**
(`bus_errors`, `ohmmeter_reading`, `tdr_distance_m` testés), 4 exemples corrigés, 16 exercices
(5 schémas, 4 choix, 3 procédures, 4 diagnostics), mini-examen 10 questions /20
(`app/v1/ampcr_pratique_pr16_*.py`). Aucune image générée.

**Cinquième cours publié (ticket #199) : PR20 « IPv4, MAC, masques et passerelles — configuration
et diagnostics écrits »** (`/uaa/ampcr-pratique-pr20`), même intégration. 16 blocs (matière 1-15
du ticket : réseau local, MAC, IPv4 et plages particulières, masque/CIDR, passerelle, DNS, DHCP,
commandes Windows et Linux, plan d'adressage, connexion directe, diagnostic, cas d'erreur,
compte rendu ; mémo et glossaire), 13 figures SVG (réseau de référence 4 postes + switch +
routeur + DHCP/DNS, MAC, bits /24 /26 /27, DORA, `ipconfig /all`, `ip addr`/`ip route`,
fenêtre IPv4 fictive, démarche de ping, 3 arbres de diagnostic). **Tous les calculs
d'adressage sont faits par code** (`ipaddress` : `subnet_facts`, `same_subnet`, `host_errors`,
`plan_errors`…) et recalculés indépendamment par les tests. 5 cas résolus, 20 exercices
(7 calculs, 5 diagnostics, 4 configurations, 4 comptes rendus/procédures), mini-examen 10
questions /20 (`app/v1/ampcr_pratique_pr20_*.py`). Aucune image générée.

**Sixième cours publié (ticket #200) : PR24 « Dépannage réseau et Internet — dossiers
d'intervention écrits »** (`/uaa/ampcr-pratique-pr24`), même intégration. 18 blocs (matière 1-15
du ticket : méthode en couches, physique et liaison, configuration IP, DHCP, DNS, passerelle et
routage, switch et VLAN, Wi-Fi, partages et imprimantes, outils Windows et Linux, procédure
ordonnée, pannes combinées, sécurité, rapport ; mémo et glossaire). Réseau de référence fictif
« l'atelier » (192.168.20.0/24, box, switch administrable, serveur DHCP/DNS dnsmasq, NAS,
imprimante, point d'accès PoE) ; 13 figures SVG (réseau, ports du switch, couches, arbres
général / Wi-Fi / partage, 7 documents : APIPA, ping, tracert, nslookup, journal DHCP, Wi-Fi,
Linux). **Tous les relevés sont produits par code** (`app/v1/ampcr_pratique_pr24_figures.py`)
et relus par les tests (statistiques, premier saut, réponses DNS, largeur mobile ≤ 56
caractères). 6 cas résolus, 6 tableaux symptôme → test discriminant → action, 20 exercices
(8 analyses de relevés, 5 arbres/procédures, 4 dossiers multi-postes, 3 rapports), mini-examen
10 questions /20 (`app/v1/ampcr_pratique_pr24_*.py`). Aucune image générée.

**Septième cours publié (ticket #202) : PR01 « Structure d'un PC et identification des
composants »** (`/uaa/ampcr-pratique-pr01`), même intégration, premier cours de l'ordre
pédagogique PR01 → PR30 demandé par le propriétaire. 19 blocs (13 chapitres : structure et
cheminement des données, formats et boîtier, carte mère, processeur et refroidissement,
RAM/ROM/stockage et barrettes, firmware, stockage, connecteurs du bloc et carte graphique, ports,
périphériques et pilotes, compatibilité, démarche écrite et ESD ; cas, pièges, exercices,
mini-examen, mémo, sources). 8 figures SVG ; valeurs normalisées (formats, contacts des
barrettes, débits PCIe/USB/SATA) et relevés d'inventaire fictifs (`lsblk`, `Get-CimInstance`)
**produits par code** (`app/v1/ampcr_pratique_pr01_figures.py`) et recalculés par les tests.
4 cas résolus, 16 exercices (identifications, inventaires, choix de pièces compatibles,
scénarios, procédures), mini-examen 10 questions /20 (`app/v1/ampcr_pratique_pr01_*.py`).
Fiches produits fictives ; aucune image générée.

**Huitième cours publié (ticket #203) : PR02 « Alimentation, connectique, compatibilité et
sécurité »** (`/uaa/ampcr-pratique-pr02`), même intégration, deuxième cours de l'ordre
pédagogique. 19 blocs (12 chapitres : AC/DC et tensions, caractéristiques et rendement,
connecteurs et brochages, budget de puissance, refroidissement, protections et onduleur,
sécurité électrique/ESD/batteries/outils, USB/HDMI/DisplayPort, SATA/PCIe/M.2, compatibilité,
symptômes d'alimentation, procédure de remplacement sûre ; cas, pièges, exercices, mini-examen,
mémo, sources). 8 figures SVG ; tolérances, puissances PCIe, rendements, budgets, grille de
compatibilité et relevés **calculés par code** (`app/v1/ampcr_pratique_pr02_figures.py`) et
recalculés par les tests. 4 cas résolus, 16 exercices, mini-examen 10 questions /20.
Fiches produits fictives ; aucune image générée.

**Neuvième cours publié (ticket #204) : PR03 « Montage et démontage d'un PC — procédure
écrite »** (`/uaa/ampcr-pratique-pr03`), même intégration, troisième cours de l'ordre
pédagogique. 20 blocs (13 chapitres : poste/ESD/inventaire, sauvegarde et autorisation,
compatibilité, ordre de montage, carte équipée hors boîtier, boîtier et entretoises, câblage et
façade, contrôle visuel, premier démarrage et tests, câbles et flux d'air, démontage documenté,
remplacement, pannes au premier démarrage ; cas, pièges, exercices, mini-examen, mémo, sources).
5 procédures illustrées, 9 figures SVG ; brochage de façade, entretoises, visserie, écarts
d'inventaire et seuils de température **définis par code** (`app/v1/ampcr_pratique_pr03_figures.py`)
et contrôlés par les tests. 4 cas résolus, 16 exercices, mini-examen 10 questions /20.
Situations fictives ; aucune image générée.

**Dixième cours publié (ticket #205) : PR04 « Reconditionnement, entretien et contrôles après
intervention »** (`/uaa/ampcr-pratique-pr04`), même intégration, quatrième cours de l'ordre
pédagogique. 20 blocs (13 chapitres : quatre opérations, réception, diagnostic, protection des
données, effacement HDD/SSD, nettoyage, refroidissement, pièces, mises à jour, tests, remise,
déchets, rapport ; cas, pièges, exercices, mini-examen, mémo, sources). 5 procédures illustrées,
9 figures SVG ; décision sur les données, techniques d'effacement par support, verdicts SMART,
batterie et températures, tri des déchets **définis par code**
(`app/v1/ampcr_pratique_pr04_figures.py`) et contrôlés par les tests. 4 cas résolus,
16 exercices, mini-examen 10 questions /20. Situations fictives ; aucune image générée.

**Onzième cours publié (ticket #206) : PR05 « Stockage, partitions, formatage et
défragmentation »** (`/uaa/ampcr-pratique-pr05`), même intégration, cinquième cours de l'ordre
pédagogique. 21 blocs (14 chapitres : supports HDD/SSD SATA/NVMe, interfaces SATA et M.2,
secteurs/clusters/usure, Go et Gio, MBR/GPT, démarrage UEFI et plans de partitions, formatage et
systèmes de fichiers, choix selon l'usage, partitions sous Windows et Linux, sauvegarde et
opérations non destructives, SMART prudent, défragmentation et TRIM, symptômes ; cas, pièges,
exercices, mini-examen, mémo, sources). 5 procédures illustrées, 11 figures SVG (dont 4 plans de
partitions exacts) ; conversions d'unités, choix MBR/GPT, système de fichiers, entretien et
lecture SMART (câble) **définis par code** (`app/v1/ampcr_pratique_pr05_figures.py`) et contrôlés
par les tests. 4 cas résolus, 16 exercices, mini-examen 10 questions /20. Situations fictives ;
aucune image générée.

**Premier examen blanc publié (ticket #230) : EX01 « Examen blanc écrit — maintenance et
dépannage matériel »** (`/uaa/ampcr-pratique-ex01`), juste après PR06 dans le parcours. La page
de l'UAA est le **sujet** (version candidat imprimable A4, sans corrigé : présentation, barème
global, partie 1, dossiers A fiduciaire / B studio vidéo / C clinique, méthode, sources) ; onglets
« Sujet » et « Examen blanc » seulement (« S'entraîner » redirige vers l'examen). 10 questions de
10 points, réponses libres, note /100 sur la page de résultats (plus le repère /20) ; corrigé et
barème après la remise. 3 schémas SVG (plan lettré de carte mère, LED de diagnostic, courbe de
température), dont 2 affichés dans les questions via des fichiers statiques identiques ; budget
d'alimentation, verdicts de température et SMART **calculés par code** avec les règles des cours
(`app/v1/ampcr_pratique_ex01_*.py`).

**Douzième cours publié (ticket #207) : PR07 « Systèmes d'exploitation, GUI/CLI et prérequis
d'installation »** (`/uaa/ampcr-pratique-pr07`), même intégration, septième cours de l'ordre
pédagogique (après EX01). 21 blocs (14 chapitres : rôle et fonctions d'un système, systèmes du
marché, éditions et cycle de vie, GUI/CLI, architecture 32/64 bits, firmware UEFI/CSM, démarrage
sécurisé et TPM, prérequis Windows 11 et Linux, sauvegarde et licences, installation propre ou
mise à niveau, média d'installation, démarrage sur le média, partitions et pilotes, comptes et
sécurité initiale, virtualisation ; 4 scénarios corrigés, pièges, exercices, mini-examen, mémo,
sources). 3 procédures illustrées et 8 figures SVG ; verdicts de compatibilité Windows 11,
édition nécessaire, limite 32 bits, choix propre/mise à niveau et plan de mémoire des machines
virtuelles **définis par code** (`app/v1/ampcr_pratique_pr07_figures.py`) et contrôlés par les
tests. 16 exercices, mini-examen 10 questions /20. Prérequis datés (octobre 2026), situations
fictives ; aucune image générée.

**Treizième cours publié (ticket #208) : PR08 « Installation complète de Windows — préparation
et dépannage »** (`/uaa/ampcr-pratique-pr08`), même intégration, huitième cours de l'ordre
pédagogique (après PR07). 20 blocs (13 chapitres : demande, accord écrit et inventaire,
compatibilité et pilotes, licence/édition/activation, sauvegarde et installation propre / mise à
niveau / migration, média USB et pilotes F6, firmware UEFI et démarrage, installateur, disque et
partitions GPT/ESP, configuration initiale, pilotes et mises à jour, activation/sécurité/
restauration, dépannage par cinq familles, liste de contrôle et rapport ; 5 cas résolus, pièges,
exercices, mini-examen, mémo, sources). 3 procédures illustrées et 9 figures SVG (plan GPT, arbre
« disque introuvable », 4 captures fictives) ; activation selon la licence, règle de suppression
des partitions, dépannage et codes fabricants **définis par code**
(`app/v1/ampcr_pratique_pr08_figures.py`) et contrôlés par les tests. 16 exercices, mini-examen
10 questions /20. Écrans datés (octobre 2026), situations fictives ; aucune image générée.

**Quatorzième cours publié (ticket #209) : PR09 « Installation complète de Linux — préparation
et dépannage »** (`/uaa/ampcr-pratique-pr09`), même intégration, neuvième cours de l'ordre
pédagogique (après PR08). 19 blocs (12 chapitres : demande, accord écrit et inventaire, choix de
la distribution selon l'usage, image ISO et contrôle d'intégrité, clé USB, firmware UEFI,
démarrage sécurisé et session live, sauvegarde et double démarrage, partitions ESP / racine /
/home / swap en ext4 et fstab/UUID, installateur et chargeur GRUB/systemd-boot, comptes et sudo,
réseau, mises à jour apt/dnf et pilotes, services et tests, dépannage par six familles, liste de
contrôle et rapport ; 5 cas résolus, pièges, exercices, mini-examen, mémo, sources). 3 procédures
illustrées et 9 figures SVG (deux plans de partitions, arbre « Linux ne démarre pas », 4 terminaux
fictifs) ; distributions et commandes, verdict de somme de contrôle, repère du swap, règle du
double démarrage, ordre des entrées UEFI et dépannage **définis par code**
(`app/v1/ampcr_pratique_pr09_figures.py`) et contrôlés par les tests. 17 exercices, mini-examen
10 questions /20. Sorties de terminal en anglais, installateurs datés (octobre 2026), situations
fictives ; aucune image générée.

**Quinzième cours publié (ticket #214) : PR10 « Comptes, pilotes, paramètres et commandes »**
(`/uaa/ampcr-pratique-pr10`), même intégration, dixième cours de l'ordre pédagogique (après
PR09). 19 blocs (12 chapitres : comptes locaux et de domaine et groupes, UAC, sudo et moindre
privilège, permissions Linux, pilotes et compatibilité, Gestionnaire de périphériques et
périphérique inconnu, installation/mise à jour/restauration d'un pilote, paramètres et démarrage,
services Windows et systemd, commandes réseau, commandes système Windows, commandes Linux, liste
de contrôle et rapport ; 5 cas résolus, pièges, exercices, mini-examen, mémo, sources).
4 procédures illustrées et 10 figures SVG (permissions, arbre « un périphérique ne fonctionne
pas », 4 captures fictives) ; comptes, élévation, permissions, états des périphériques et
identifiants matériels, actions sur les services et fiches des 16 commandes **définis par code**
(`app/v1/ampcr_pratique_pr10_figures.py`) et contrôlés par les tests. 17 exercices, mini-examen
10 questions /20. Windows en français, Linux en anglais, libellés datés (octobre 2026),
situations fictives ; aucune image générée.

**Seizième cours publié (ticket #215) : PR12 « Dépannage logiciel et restauration du système »**
(`/uaa/ampcr-pratique-pr12`), même intégration, douzième cours de l'ordre pédagogique (après
PR11). 20 blocs (13 chapitres : familles de causes et isolement, recueil des faits et journaux,
protection des données (sauvegarde, empreintes SHA-256, accord écrit), WinRE et mode sans échec,
points de restauration, SFC/DISM, pilotes et mises à jour, profil corrompu, logiciels
malveillants, systemd/journalctl/GRUB, permissions/paquets/fsck/espace disque, échelle des
interventions, panne réseau logicielle ou physique, contrôles et rapport ; 5 cas résolus :
démarrage, service, profil, mise à jour, espace disque ; pièges, exercices, mini-examen, mémo,
sources). 5 procédures illustrées et 11 figures SVG (arbre d'isolement, échelle des
interventions, arbre réseau, 3 captures fictives) ; causes, isolement, effets et précautions des
interventions, empreintes (calculées par `hashlib`), espace disque et diagnostic réseau **définis
par code** (`app/v1/ampcr_pratique_pr12_figures.py`) et contrôlés par les tests. 17 exercices,
mini-examen 10 questions /20. Windows en français, Linux en anglais, libellés datés (octobre
2026), situations fictives ; aucune image générée.

**Deuxième examen blanc publié (ticket #231) : EX02 « Examen blanc écrit — installation et
dépannage des systèmes »** (`/uaa/ampcr-pratique-ex02`), juste après PR12 dans le parcours, même
modèle que EX01 (sujet imprimable sans corrigé, onglets « Sujet » et « Examen blanc », 10
questions de 10 points à réponse libre, note /100, corrigé et barème après la remise). Partie 1
(choix du système et de l'édition sur trois postes, GUI/CLI et service `cups` désactivé), dossier
A bureau d'architectes (installation propre de Windows 11 sur un SSD neuf, pilotes manquants,
comptes et groupe de travail), dossier B Repair Café (double démarrage Ubuntu, mode d'urgence dû à
un `/dev/sdb1` dans fstab, permissions et sudo), dossier C agence immobilière (écran d'arrêt après
une mise à jour de pilote et WinRE, sauvegarde vérifiée par SHA-256 et choix de la restauration).
3 schémas SVG affichés dans les questions (écran de l'installateur, plan de partitions, écran
d'arrêt) + l'échelle des interventions de PR12 en rappel de méthode ; prérequis, éditions,
actions sur les partitions, swap, droits, empreintes **calculés par code** avec les règles des
cours PR07–PR12 (`app/v1/ampcr_pratique_ex02_*.py`).

**Dix-septième cours publié (ticket #216) : PR13 « Câbles UTP, FTP, STP et coaxial — choix et
pose »** (`/uaa/ampcr-pratique-pr13`), même intégration, treizième cours de l'ordre pédagogique
(position 13, après EX02 et avant PR15). 16 blocs (9 chapitres : paire torsadée, torsade,
diaphonie, parasites, atténuation ; désignation X/YTP U/UTP, F/UTP, U/FTP, S/FTP et noms
historiques ; continuité de l'écran et mise à la terre ; catégories 5e/6/6A, monobrin/multibrin,
marquage ; 8P8C, prises, cordons, baie ; coaxial 50/75 Ω, 10BASE2 et vidéo ; choix selon les
contraintes ; règles de pose (EN 50174-2, rayon de courbure, traction, fixation) ; longueurs,
repérage, tests ; 5 cas de sélection résolus, pièges, exercices, mini-examen, mémo, sources).
2 procédures illustrées et 9 figures SVG (coupes des quatre blindages dessinées depuis la
désignation, continuité de l'écran, coupe coaxiale, arbre de choix, chaîne baie → prise,
distances aux câbles d'énergie, rayons de courbure à l'échelle) ; désignation, règle de choix,
rayons, distances, longueurs et repères **définis par code**
(`app/v1/ampcr_pratique_pr13_figures.py`) et contrôlés par les tests. 17 exercices, mini-examen
10 questions /20 ; aucune image générée.

**Dix-huitième cours publié (ticket #217) : PR14 « Débits, distances, atténuation et
impédance »** (`/uaa/ampcr-pratique-pr14`), même intégration, quatorzième cours de l'ordre
pédagogique (position 14, après PR13 et avant PR15). 16 blocs (9 chapitres : bits, octets,
préfixes décimaux et binaires ; durée d'une copie, débit nominal et utile (rendement TCP calculé
depuis les en-têtes) ; Ethernet 10/100/1000/10G et coaxial 10BASE2/10BASE5, longueurs ; dB ;
bruit, NEXT/FEXT, ACR, blindage ; impédance 100/50/75 Ω et réflexions (Γ) ; fibre monomode ou
multimode, pertes, portée selon le module, bilan ; duplex, auto-négociation, collisions ;
diagnostic d'une liaison à 100 Mb/s au lieu de 1 Gb/s ; 5 cas chiffrés résolus, pièges,
exercices, mini-examen, mémo, sources). 3 procédures illustrées et 9 figures SVG ; tous les
calculs (durées, verdicts cuivre, dB, Γ, bilans optiques, négociation) **définis par code**
(`app/v1/ampcr_pratique_pr14_figures.py`) et contrôlés par les tests. 19 exercices, mini-examen
10 questions /20 ; aucune image générée.

**Dix-neuvième cours publié (ticket #218) : PR17 « Fibre optique — choix, raccordement et
diagnostic »** (`/uaa/ampcr-pratique-pr17`), même intégration, dix-septième cours de l'ordre
pédagogique (position 17, après PR16 et avant PR20 ; PR18 et PR19 non publiés). 18 blocs
(11 chapitres : lumière guidée dans le cœur et la gaine ; monomode ou multimode, types OM/OS,
code couleur et marquage, portée selon le module ; connecteurs LC/SC, polissage UPC/APC,
jarretières ; modules SFP/SFP+, TX/RX, duplex et polarité ; pertes, puissance reçue, plage de la
fiche, saturation ; épissure, pigtail, tiroir, brassage ; pose et rayon de courbure ; fibre,
cuivre ou coaxial ; contrôle : propreté, photométrie, OTDR ; sécurité laser et éclats ;
diagnostic ; 5 cas résolus : lien inversé, connecteur sale, mauvais module, distance, casse ;
pièges, exercices, mini-examen, mémo, sources). 3 procédures illustrées et 9 figures SVG ;
compatibilités, polarités, pertes, zones de réception, événements OTDR et rayons **définis par
code** (`app/v1/ampcr_pratique_pr17_figures.py`, valeurs d'affaiblissement et portées reprises
de PR14) et contrôlés par les tests. 18 exercices, mini-examen 10 questions /20 ; aucune image
générée.

**Troisième examen blanc publié (ticket #232) : EX03 « Examen blanc écrit — câblage RJ45, BNC et
fibre »** (`/uaa/ampcr-pratique-ex03`), juste après PR17 (module 3 = PR13 → PR17 ; PR18 appartient
au module 4), même modèle que EX01/EX02 (sujet imprimable sans corrigé, onglets « Sujet » et
« Examen blanc », 10 questions de 10 points à réponse libre, note /100, corrigé et barème après
la remise). Partie 1 (fiche RJ45 d'un stagiaire contre T568B et brochages A/B, cordon droit ou
croisé et Auto MDI-X), dossier A imprimerie (choix des câbles et du blindage, rapport de test des
liens : mélange A/B, lien trop long, ouvert, paires séparées, 10 Gb/s en Cat6 ; relevé de pose et
fabrication d'un cordon), dossier B musée (bus 10BASE2 non conforme et réflexion 75/50 Ω,
ohmmètre, fabrication d'un câble BNC, 10BASE5), dossier C brasserie (choix fibre/modules/jarretières,
bilan et photométrie, panne lue au réflectomètre et réparation). 4 schémas SVG **sans verdict**
dans les questions (fiche, testeur, bus, trace) ; toutes les valeurs **calculées par code** avec
les règles des cours PR13–PR17 (`app/v1/ampcr_pratique_ex03_*.py`).

**Vingtième cours publié (ticket #219) : PR18 « Installation physique d'un mini-réseau »**
(`/uaa/ampcr-pratique-pr18`), même intégration, position 18 (après PR17 et EX03, avant PR20).
18 blocs (11 chapitres : besoin et plan des locaux ; étoile et implantation ; choix du support ;
longueurs, cheminement, repérage ; sécurité et séparation du courant fort ; baie, panneau de
brassage, keystones ; PoE ; plan de câblage, nomenclature, devis ; tests et certification ;
configuration de base et validation ; documentation et réception ; 5 cas résolus ; pièges,
exercices, mini-examen, mémo, sources). 3 procédures, 8 figures SVG et 5 schémas à compléter
servis aussi en fichiers statiques ; longueurs, dimensionnement (switch, panneaux, baie, boîtes
de câble), budget PoE, devis, verdicts de recette et ordre de validation **définis par code**
(`app/v1/ampcr_pratique_pr18_figures.py`, règles de PR13/PR15 réutilisées) et contrôlés par les
tests. 20 exercices, mini-examen 10 questions /20 ; aucune image générée.

**Vingt et unième cours publié (ticket #220) : PR19 « Topologies, OSI, TCP/IP, NetBEUI et
équipements »** (`/uaa/ampcr-pratique-pr19`), même intégration, position 19 (après PR18, avant
PR20). 16 blocs (9 chapitres : topologies bus, étoile, anneau, maillage ; modèles OSI et TCP/IP ;
encapsulation et trame Ethernet ; adresses MAC et IP, ARP, ports ; NetBEUI non routable ;
équipements ; domaines de collision et de diffusion, VLAN ; chemin d'un paquet du PC à Internet ;
diagnostic couche par couche ; 5 cas résolus ; pièges, exercices, mini-examen, mémo, sources).
3 procédures, 10 figures SVG et 6 schémas à compléter servis aussi en fichiers statiques ; effet
des pannes par topologie, tailles d'encapsulation, domaines, adresses des trames et couche en
défaut **calculés par code** (`app/v1/ampcr_pratique_pr19_figures.py`) et contrôlés par les
tests. 20 exercices, mini-examen 10 questions /20 ; aucune image générée.

**Vingt-deuxième cours publié (ticket #221) : PR21 « Connexion directe de deux PC et
mini-réseau »** (`/uaa/ampcr-pratique-pr21`), même intégration, position 21 (après PR20, avant
PR24). 16 blocs (9 chapitres : carte réseau, câble droit ou croisé, Auto MDI-X ; voyants de lien ;
adresses statiques 192.168.10.1/24 et .2/24 sans passerelle ; ping, table ARP et pare-feu ;
partage et permissions ; extension à 3–6 PC via un switch ; DHCP ou statique, box, passerelle,
DNS, plan d'adressage ; erreurs liaison, DHCP, doublon, masque ; mise en service et recette ;
5 cas résolus ; pièges, exercices, mini-examen, mémo, sources). 3 procédures, 12 figures SVG et
4 schémas à compléter servis aussi en fichiers statiques ; câble selon les ports, résultat d'un
ping selon la configuration, plans d'adressage et ordre du diagnostic **calculés par code**
(`app/v1/ampcr_pratique_pr21_figures.py`, modèle d'adressage de PR20) et contrôlés par les tests.
20 exercices, mini-examen 10 questions /20 ; aucune image générée.

## Administration

Disponible.

Permet notamment :

- gérer les matières
- gérer les modules
- gérer les UAA
- gérer les blocs de contenu
- importer des quiz
- administrer la banque de questions V1 (`/admin/bank`, ticket #46) : statistiques par
  module, recherche/filtres, versions, modification (= nouvelle version), statuts
  (archiver/réactiver, invalide, obsolète, à revoir), variante IA, génération
  ACTIVE/PAUSED par module, signalements des élèves et usage IA estimé — voir
  `docs/admin.md`, § Banque de questions V1.
- gérer les visuels de la banque (`/admin/bank/assets`, ticket #48) : marquer un visuel
  incorrect (ses questions sortent du tirage), demander une régénération, réactiver.

La création complète d'un cours ne passe plus par l'administration.

---

## Exercices générés

Disponible. Deux moteurs coexistent (voir `docs/EXERCISE_TYPES.md`) :

- **Ancien moteur** (`GeneratedExercise`, énoncé texte + une réponse) : utilisé par
  `maths.equations.linear_equation`. Widget `.exercise-widget`
  (`app/static/js/exercise.js`), routes `/practice/api/generate`, `/verify`, `/reveal`.
- **Nouveau moteur** (`InteractiveExercise`, voir `docs/EXERCISE_TYPES.md`) : un générateur
  produit uniquement des données JSON, le composant frontend construit entièrement
  l'affichage. Premier type : `value_table` (tableau de valeurs à compléter, vérifié
  cellule par cellule) — `generators/exercise_types.py`, `generators/value_table.py`,
  `app/value_table.py`, `app/static/js/value_table.js`, route
  `/practice/api/value-table/verify`. Utilisé par `maths.functions.constant_function`
  depuis VS003 : les exercices générés de MB32 UAA1 (« Fonction constante — Exercices
  automatiques ») affichent un vrai tableau interactif sur la page publique, plutôt qu'un
  simple énoncé texte.

`generate_exercises()` (`app/exercise_blocks.py`) retourne les objets bruts (l'un ou l'autre
type) ; c'est l'appelant (route `uaa_detail`, outil `/admin/generators`) qui détecte le type
retourné et choisit le composant d'affichage — un générateur donné renvoie toujours la même
forme. `/admin/value-table-demo` reste disponible pour prévisualiser le composant sans
générateur réel (exercice fixe).

- **Moteur IA** (bloc `ai_exercise`, ticket #10 complément IA, voir
  `docs/ai_exercise_engine.md`) : génération à la demande (facile/moyen/difficile) et
  correction structurée via l'API OpenAI, appelée côté serveur uniquement, bornée à un
  contexte pédagogique par cours (`app/ai/context.py`). Complémentaire aux deux moteurs
  ci-dessus, pas un remplacement. Non configuré par défaut.
- **Socle des exercices éditoriaux interactifs** (bloc `editorial_exercise`, ticket #17,
  étendu aux #21/#29, voir `docs/editorial_exercise_engine.md`) : types disponibles —
  `single_choice`, `true_false`, `short_answer` (ticket #17), `classification`, `ordering`
  (ticket #21), `long_answer`, `diagnostic`, `vocabulary` (ticket #29). Correction locale
  déterministe pour les premiers ; correction sémantique via le fournisseur IA existant
  (#23, `app/editorial_ai_correction.py`, aucun second moteur) pour `long_answer`/
  `diagnostic`, et `short_answer`/`vocabulary` sans `accepted_answers`. Saisie +
  vérification AJAX + score, sans rechargement de page. Prévisualisable via
  `/admin/editorial-exercise-demo`. **Les 12 exercices de MC01 sont désormais tous migrés
  dans ce format** (plus aucun bloc Markdown d'exercice) — voir
  `docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md`. Servis sur
  l'espace S'entraîner (`/uaa/{slug}/practice`, ticket #22), jamais dans le flux de
  théorie ; aucune correction visible avant validation explicite.
- **Longueur de session au choix** (ticket #86) : l'écran de démarrage d'un entraînement
  ou d'une évaluation (par mini-cours, MC38, FSE17, parcours global AMPCR) propose
  « Nombre de questions » 10/20/30/40 (+ 50 pour MC38 et le parcours global AMPCR),
  présélection 10 en entraînement et 20 en évaluation. Sans génération possible
  (fournisseur absent, module en pause, FSE17), seules les longueurs couvertes par la
  banque sans doublon sont proposées. Le choix est persisté
  (`parameters_json["requested_question_count"]`, affiché dans l'historique/export s'il
  diffère du nombre réel). La génération manquante est découpée en lots de 20 (sessions de 30 à 50) ; la
  diversité catégories/mini-cours augmente avec la longueur (≥ 3/4/6 valeurs à 10/20/30+).

---

## Quiz

Disponible.

Les quiz sont intégrés au contenu pédagogique. Question et explication passent par le
renderer de contenu riche (voir plus bas) : un tableau ou une formule dans une question de
quiz s'affiche correctement plutôt qu'en texte brut.

Depuis le ticket #137, un espace **Quiz du parcours** (`/quiz`) propose des parties de 5, 10
ou 20 questions objectives (QCM, classement, remise en ordre) sur un cours, une matière,
plusieurs matières ou tout le parcours, avec récapitulatif avant départ, correction et
explication après chaque réponse validée, reprise exacte, résultat (points forts, cours à
relire), rejouer et reprise des erreurs. Activité distincte des entraînements et examens
blancs. Voir `docs/quiz_v1.md`.

Depuis le ticket #75, une page **Mes points faibles** (`/points-faibles`) calcule un niveau
de fragilité par cours (ou par notion si la question est étiquetée — `Question.concepts`)
à partir des réponses corrigées des entraînements, examens blancs et renforcements
(jamais deux fois la même réponse, quiz exclus) ; elle propose un **renforcement ciblé**
(`SessionMode.REINFORCEMENT`, une question objective à la fois, correction immédiate,
variante ajoutée après une erreur) et un **examen ciblé** (examen blanc de 10/20 questions
sur les notions faibles, sans correction avant la fin). Voir `docs/weakness_v1.md`.

Depuis le ticket #150, l'ordre des réponses d'un QCM (et des éléments d'une remise en
ordre) est tiré au sort pour chaque question servie — quiz, entraînement et examen blanc —
et persisté dans la session (`SessionQuestion.content_snapshot_json["display_order"]`,
`app/v1/display_order.py`) : stable à la reprise, banque inchangée, correction toujours
par identifiant. Les sessions antérieures gardent l'ordre de la banque.

Depuis le ticket #153, une remise en ordre (entraînement, examen blanc, quiz) s'affiche en
cartes réordonnables : glisser-déposer souris/tactile par la poignée (SortableJS 1.15.7,
MIT, vendorisé dans `app/static/vendor/sortablejs/`), boutons Monter/Descendre et
Alt + ↑/↓, annonce accessible. Gabarit partagé `app/templates/_ordering_cards.html`,
script `app/static/js/ordering_cards.js`. Contrat serveur inchangé (champs
`position__<id>`) ; l'ordre affiché n'est enregistré qu'après un déplacement ou
« Conserver cet ordre ». En entraînement/examen, sauvegarde automatique par identifiants
via `/api/v1/sessions/{id}/answers/{sq}` (permutation complète validée côté serveur) ; en
quiz, validation volontaire. Sans JavaScript, les listes de positions restent utilisables.

---

## Renderer de contenu riche (VS003.1)

Disponible.

Un seul renderer (`app/content.py::render_markdown` côté serveur,
`app/static/js/rich_content.js::renderRichContent()` côté client) est utilisé partout où du
texte pédagogique est affiché : cours, quiz (question et explication), exercices générés
(énoncé, indice, correction), value_table (question, indice, explication). Reconnaît
automatiquement tableaux Markdown, listes, citations (→ WarningCard), et laisse passer les
formules MathJax (`$...$`), retypesettées côté client après toute insertion dynamique
(MathJax ne rescane pas seul le contenu inséré après le chargement initial de la page).

Le HTML est toujours rendu côté serveur et transmis tel quel (champs `*_html` en plus des
champs texte bruts, ex. `question_html`, `statement_html`, `explanation_html`,
`solution_steps_html`) ; aucun parseur Markdown côté client, conforme à « aucune dépendance
JS externe ».

`app/static/js/design_system.js::enhanceRichContent(root)` (tableaux responsives, cellules
éditables, citations → WarningCard) est appliqué une fois au chargement de la page à tout
`.content-markdown`, et ré-appliqué par `renderRichContent()` à tout contenu inséré
ensuite — même traitement partout, aucune duplication.

---

## Progression

Disponible.

Progression locale de l'étudiant, complétée par une barre de progression de lecture par
leçon.

Rating adaptatif V1 (ticket #45) : niveau de l'utilisateur par module et difficulté
empirique des questions, recalculés après chaque questionnaire corrigé ; option
« Adaptatif » au démarrage d'un entraînement/évaluation. Voir `docs/rating_adaptatif_v1.md`.

---

## Design System

Disponible.

Composants de carte réutilisables (voir `docs/UI_GUIDELINES.md`) : TheoryCard, ExampleCard,
ExerciseCard, QuizCard, WarningCard, SummaryCard — `app/templates/_cards.html`,
`app/static/css/design-system.css`, `app/static/js/design_system.js`. Le type de carte d'un
bloc de leçon est déduit de son titre (`app/card_kind.py`), sans jamais lire ni modifier le
contenu pédagogique.

Rendu par ce système : tableaux responsives, cellules de tableau vides rendues éditables,
citations (pièges) transformées en WarningCard (voir « Renderer de contenu riche »
ci-dessus, dont ce système est maintenant un consommateur comme les autres écrans),
exercices rédigés dont la correction reste masquée jusqu'à demande explicite, quiz group
affichant toujours une explication après chaque réponse.

Appliqué automatiquement à toute UAA affichée, quel que soit l'espace
(`/uaa/{slug}`, `/uaa/{slug}/practice`, `/uaa/{slug}/exam` — ticket #22).

---

# Import des cours

Le nouveau workflow repose sur les sources officielles.

Les cours sont stockés dans :

docs/sources_cours/

Chaque UAA contient :

- cours.html
- cours.pdf
- metadata.yaml

L'objectif est que Claude puisse intégrer automatiquement une UAA complète.

---

# Contenu pédagogique

## Intégré

- **Questions visuelles Informatique (ticket #48)** : premières questions d'identification
  de composants dans la banque MC01 (RAM, CPU, alimentation, HDD, SSD, carte mère, carte
  graphique ; schéma de carte mère à repères A–F). Types `image_identification` et
  `diagram_labeling` désormais servis en entraînement/examen et corrigés localement. Assets
  réutilisables (photo réelle / illustration générée / schéma technique) avec source,
  licence et provenance — voir [docs/assets_visuels_v1.md](assets_visuels_v1.md).

- MB32 UAA1
- MB32 UAA2 (Géométrie — 6 leçons : Solides, Perspective cavalière, Patrons, Vues
  coordonnées, Aires, Volumes)
- **Informatique — AMPCR — mini-cours 01 « Architecture générale d'un PC »** (ticket #10,
  2026-09-16) : matière et module désormais navigables (`/subjects/informatique`,
  `/modules/ampcr`, `/uaa/ampcr-mc01`), 11 sections de cours, 12 exercices progressifs à
  correction masquée à la demande, examen final de 10 questions/20 points sans aucune
  correction visible côté candidat (corrigé dans un bloc séparé non publié). Cours pilote
  de la série des 38 mini-cours Informatique — voir
  [docs/content_plan_informatique_francais.md](content_plan_informatique_francais.md).
  Complète également le moteur générique de **génération d'exercices et de correction par
  IA** (API OpenAI, côté serveur uniquement) : difficulté sélectionnable
  (facile/moyen/difficile), contexte pédagogique borné par cours, correction structurée
  (JSON strict), aucune clé API exposée au client — voir
  [docs/ai_exercise_engine.md](ai_exercise_engine.md). Non configuré par défaut
  (`OPENAI_API_KEY` vide) : la fonctionnalité affiche un message clair plutôt que d'échouer
  silencieusement, tant qu'aucune clé n'est fournie.
- **Informatique — AMPCR — mini-cours 02 « Carte mère, formats et connectiques »**
  (ticket #12, 2026-09-16) : navigable après le mini-cours 01 (`/uaa/ampcr-mc02`), 16
  sections de cours, 12 exercices progressifs à correction masquée, examen final de 10
  questions/20 points (corrigé non publié), et son propre contexte pédagogique borné
  (`app/ai/context.py::PEDAGOGICAL_CONTEXTS["ampcr-mc02"]`) pour le **même** moteur IA
  générique introduit au ticket #10 — aucun second moteur, aucune logique IA dupliquée.
- **Informatique — AMPCR — mini-cours 03 « CPU et mémoire RAM »** (ticket #14,
  2026-09-16) : navigable après le mini-cours 02 (`/uaa/ampcr-mc03`), 17 sections de cours
  (CPU : rôle, cœurs/threads, fréquence, IPC, cache L1/L2/L3, 32/64 bits, socket, TDP,
  throttling ; RAM : rôle, DDR3/4/5, DIMM/SO-DIMM, dual-channel, XMP/EXPO, ECC, RAM vs
  VRAM vs stockage ; diagnostic et pièges d'unités), 12 exercices progressifs, examen
  final de 10 questions/20 points (corrigé non publié), et son propre contexte
  pédagogique borné (`PEDAGOGICAL_CONTEXTS["ampcr-mc03"]`) pour le même moteur IA — aucun
  second moteur.

- **Formation sociale et économique — CESS Professionnel — FSE01 « Communiquer : le
  schéma de communication »** (ticket #96, 2026-10-01) : nouvelle matière créée
  (`/subjects/formation-sociale-et-economique`, `/modules/fse`,
  `/uaa/fse-fse01`), premier mini-cours livré complet en réutilisant intégralement le
  moteur V1 existant (voir `docs/ampcr_v1_functional.md`/`docs/francais_v1_functional.md`
  pour le fonctionnement partagé) — théorie (schéma de communication appliqué à un mail,
  une affiche et une publication sur réseau social), 14 questions de banque, practice avec
  choix de difficulté, examen avec choix de difficulté ET de sévérité de cotation
  (paramètres distincts, appliqués et persistés côté serveur), correction hybride,
  résultats, historique. FSE02 à FSE17 restent au stade de plan documenté (voir
  [docs/content_plan_fse.md](content_plan_fse.md)), jamais présentés comme disponibles.

## En attente d'import

- MB32 UAA3, MQ32, MQ34 (derrière Informatique/Français/FSE, voir priorité ci-dessous)
- Mini-cours 04 à 38 Informatique AMPCR
- Formation sociale et économique FSE02 à FSE17 (voir
  [docs/content_plan_fse.md](content_plan_fse.md))

---

# Documentation

La documentation est organisée dans le dossier :

docs/

Chaque document possède une responsabilité unique.

---

# Priorité actuelle

Depuis le ticket #4 (2026-09-16), l'ordre de priorité produit est :

1. **Informatique — Assistant/Assistante de maintenance PC-réseaux (AMPCR)** ;
2. **Français — CESS Professionnel** ;
3. reste du contenu Mathématiques (MB32 UAA3, MQ32, MQ34) et autres matières.

Les mini-cours 01 (ticket #10), 02 (ticket #12) et 03 (ticket #14) Informatique AMPCR sont
livrés directement depuis un cahier des charges pédagogique fourni par ChatGPT dans chaque
ticket GitHub, sans fichier source déposé dans `docs/sources_cours/` (voir
`docs/content_workflow.md`, section « Contenu rédigé à partir d'un cahier des charges »).
Français CESS Professionnel : les 20 cours FR01→FR20 sont rédigés et seedés (ticket #94,
phases A–D, FR20 = examen blanc transversal ; voir
[docs/francais_v1_functional.md](francais_v1_functional.md)). Voir
[docs/content_plan_informatique_francais.md](content_plan_informatique_francais.md) pour
l'inventaire, la cartographie et le découpage en tickets restants.

---

# Points ouverts

Les améliorations suivantes sont prévues mais ne sont pas prioritaires :

- mini-test en parcours paginé (une question à la fois, Précédent/Suivant/Terminer) plutôt
  qu'un seul bloc à correction masquée ;
- vérification automatique des réponses des exercices rédigés (actuellement : comparaison
  libre avec la correction, pas de correction machine) ;
- CourseCard : appliquer le Design System aux pages de listing (matière, module), qui
  affichent encore de simples liens ;
- nouveaux types de blocs ;
- amélioration des générateurs d'exercices ;
- nouvelles statistiques ;
- amélioration de l'administration.

---

# Prochaine étape

Dépôt par l'utilisateur des sources officielles et/ou des brouillons ChatGPT pour
Informatique AMPCR (priorité 1), puis Français CESS Professionnel (priorité 2) — voir
[docs/content_plan_informatique_francais.md](content_plan_informatique_francais.md),
section « Tickets atomiques proposés ».

MB32 UAA3 reste importable depuis `docs/sources_cours/` dès que ces deux matières auront
avancé, mais n'est plus la priorité immédiate.
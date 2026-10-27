# AMPCR — Pratique écrite (cycle 2026-2027/1) : parcours, matrice et conventions (ticket #192)

Socle du parcours de l'**épreuve pratique** de l'option AMPCR (matières « Laboratoire » et
« T.P. et méthodes », évaluées ensemble, **uniquement par écrit**). Distinct du parcours
théorique MC01–MC38, qui reste inchangé.

## 1. Sources

| Document | URL | Version / date | Pages | SHA-256 |
|---|---|---|---|---|
| Consignes d'examen — pratique (fait foi) | [26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Consignes_specifiques/CESS/CESS_P/OBG/AMPCR/26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf) | cycle 2026-2027/1 (août 2026 → janvier 2027), PDF créé le 2026-07-13 | 6 | `7a93c3858ffd67b42620bc5364aa9b8e964a379bdf255bbcd126b50c4df095e1` |
| Programme 345/2007/249 (complément) | [AMPCR.pdf](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Programmes/CESS/CESS_P/OBG/AMPCR/AMPCR.pdf) | d'application depuis 2008-2009, PDF modifié le 2015-10-29 | 46 | `95e45949fc3c36d6e8ea82e7643791d323b7f1a668da54113c373f41a69bf14b` |

Récupérés le 2026-10-26 depuis la page « Matières du CESS P » du site des Jurys. **Le PDF
des consignes est versionné** dans
[`docs/references-officielles/ampcr/2026-2027-1/`](references-officielles/ampcr/2026-2027-1/README.md)
(copie identique, provenance, droits, contenu des 6 pages, transcription page par page ;
empreinte et texte des 38 exigences contrôlés par `tests/test_ticket192_ampcr_pratique_reference.py`).
Les tickets de cours et d'exercices citent ce chemin. Le programme (46 p.) reste référencé
par URL + empreinte seulement (complément, non transcrit). Le texte des
exigences et des consignes du jour est recopié dans `app/v1/ampcr_pratique_plan.py`
(extraction texte, espaces multiples réduits à un seul). Le programme est un complément :
les consignes rappellent qu'elles ne s'y substituent pas ; il n'est pas transcrit.
**Un nouveau cycle (2026-2027/2 : PDF pas encore publié) impose de recomparer l'empreinte et
le texte.**

## 2. Ce qui est en ligne

| URL | Contenu |
|---|---|
| `/ampcr-pratique` | accueil : consignes du jour (pp. 2-4), 5 modules, emplacements PR01–PR30 et examens blancs EX01–EX06 (« À venir » tant qu'ils n'existent pas), liens vers la théorie MC déjà publiée, état de la couverture |
| `/ampcr-pratique/matrice` | matrice de traçabilité, une ligne par exigence, imprimable |
| `/ampcr-pratique/format-exercice` | format d'un exercice pratique écrit + exemple **non officiel**, imprimable A4 (corrigé sur une page séparée) |

Accès : tuile « AMPCR — Pratique écrite » de `/mon-parcours` (option AMPCR) et bouton
« Pratique écrite » de `/modules/ampcr`. Aucune table, aucun seed, aucune migration :
le plan est du code (`app/v1/ampcr_pratique_plan.py`), lu en lecture seule.

### Cours publiés (ticket #193 et suivants)

| Cours | URL | Banque |
|---|---|---|
| PR01 — Structure d'un PC et identification des composants (#202) | `/uaa/ampcr-pratique-pr01` | 16 exercices (entraînement, dont 2 classements et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR02 — Alimentation, connectique, compatibilité et sécurité (#203) | `/uaa/ampcr-pratique-pr02` | 16 exercices (entraînement, dont 2 classements et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR03 — Montage et démontage d'un PC — procédure écrite (#204) | `/uaa/ampcr-pratique-pr03` | 16 exercices (entraînement, dont 4 remises en ordre et 2 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR04 — Reconditionnement, entretien et contrôles après intervention (#205) | `/uaa/ampcr-pratique-pr04` | 16 exercices (entraînement, dont 3 remises en ordre et 4 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR05 — Stockage, partitions, formatage et défragmentation (#206) | `/uaa/ampcr-pratique-pr05` | 16 exercices (entraînement, dont 3 remises en ordre et 3 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR06 — Diagnostic des pannes matérielles (#193) | `/uaa/ampcr-pratique-pr06` | 12 exercices (entraînement) + 10 questions de mini-examen /20 (examen blanc) |
| PR07 — Systèmes d'exploitation, GUI/CLI et prérequis d'installation (#207) | `/uaa/ampcr-pratique-pr07` | 16 exercices (entraînement, dont 3 remises en ordre et 4 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR08 — Installation complète de Windows — préparation et dépannage (#208) | `/uaa/ampcr-pratique-pr08` | 16 exercices (entraînement, dont 3 remises en ordre et 4 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR09 — Installation complète de Linux — préparation et dépannage (#209) | `/uaa/ampcr-pratique-pr09` | 17 exercices (entraînement, dont 3 remises en ordre et 4 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR10 — Comptes, pilotes, paramètres et commandes (#214) | `/uaa/ampcr-pratique-pr10` | 17 exercices (entraînement, dont 3 remises en ordre et 5 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR11 — Messages d'erreur Windows/Linux — diagnostic et interventions écrites (#194) | `/uaa/ampcr-pratique-pr11` | 16 exercices (entraînement, dont 2 remises en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR12 — Dépannage logiciel et restauration du système (#215) | `/uaa/ampcr-pratique-pr12` | 17 exercices (entraînement, dont 3 remises en ordre et 5 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR13 — Câbles UTP, FTP, STP et coaxial — choix et pose (#216) | `/uaa/ampcr-pratique-pr13` | 17 exercices (entraînement, dont 3 remises en ordre et 5 classements) + 10 questions de mini-examen /20 (examen blanc) |
| PR15 — Câblage RJ45 T568A/B — fabrication, schémas et tests (#197) | `/uaa/ampcr-pratique-pr15` | 16 exercices (entraînement, dont 3 classements et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR16 — Câble coaxial et BNC — impédance, fabrication et diagnostic écrit (#198) | `/uaa/ampcr-pratique-pr16` | 16 exercices (entraînement, dont 3 classements et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR20 — IPv4, MAC, masques et passerelles — configuration et diagnostics écrits (#199) | `/uaa/ampcr-pratique-pr20` | 20 exercices (entraînement, dont 3 classements et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |
| PR24 — Dépannage réseau et Internet — dossiers d'intervention écrits (#200) | `/uaa/ampcr-pratique-pr24` | 20 exercices (entraînement, dont 1 classement et 1 remise en ordre) + 10 questions de mini-examen /20 (examen blanc) |

Intégration d'un cours pratique (modèle posé par PR06, à réutiliser par PR11, PR15…) :

1. Contenu dans `app/v1/ampcr_pratique_prXX_course.py` (blocs titrés), schémas dans
   `…_figures.py` (SVG depuis des données testées), exercices et mini-examen dans `…_bank.py`
   (une seule source pour le cours et la banque).
2. Déclarer le cours dans `PRACTICAL_COURSES` (`app/v1/ampcr_pratique_bank.py`) avec son
   `PedagogicalContext` de correction : il devient automatiquement routable (S'entraîner /
   Examen blanc), importable et corrigé avec son contexte.
3. Seed : `_seed_uaa(db, practical_module, "PRxx", …)` dans `app/seed.py` (module
   `AMPCR-PRATIQUE`, jamais le module théorique `AMPCR`).
4. Réserves : `prompt_version = ampcr-pratique-prxx:practice|exam` ; la sélection banque
   (`select_bank_questions(mode=…)`) ne mélange jamais les deux ; aucune génération IA pour ces
   cours ; note ramenée sur 20 sur la page de résultats.
5. Documents d'exercice : `ExerciseDocument(kind="tableau")` (tableau), `kind="console"`
   (capture de terminal ou extrait de journal, affiché ligne à ligne en police à chasse fixe,
   mention « extrait fictif » — ticket #194) ou texte. Remise en ordre d'une procédure :
   `question_type="ordering"` + `Ordering(steps, correct)` (jamais affichée dans l'ordre
   attendu, correction locale). Schéma affiché dans la question (ticket #230) :
   `ExerciseDocument(kind="schéma", image="img/ampcr-pratique/….svg")` — fichier SVG statique
   identique au SVG du code (test), mise en page `figure` + description textuelle complète.

### Examens blancs publiés (ticket #230 et suivants)

| Examen | URL | Banque |
|---|---|---|
| EX01 — Examen blanc écrit — maintenance et dépannage matériel (#230) | `/uaa/ampcr-pratique-ex01` (sujet), `/uaa/ampcr-pratique-ex01/exam` | 10 questions de 10 points (note /100), réponses libres, partie 1 + 3 dossiers (A, B, C), réserve `exam` seule |
| EX02 — Examen blanc écrit — installation et dépannage des systèmes (#231) | `/uaa/ampcr-pratique-ex02` (sujet), `/uaa/ampcr-pratique-ex02/exam` | 10 questions de 10 points (note /100), réponses libres, partie 1 + 3 dossiers (A Windows, B Linux, C dépannage et restauration), 3 schémas dans les questions, réserve `exam` seule ; position 12, après PR12 |

Intégration d'un examen blanc (modèle posé par EX01, à réutiliser par EX02–EX06) : même
déclaration que pour un cours (`PRACTICAL_COURSES`, code `EXxx`) ; la page de l'UAA devient le
**sujet** (version candidat sans corrigé, lignes de réponse à l'impression A4) ; pas d'onglet
« S'entraîner » (`is_practical_exam_code` : `/practice` et `/practice/start` redirigent vers
`/exam`) ; la page de résultats affiche la note /100 en plus du repère /20 ; corrigé et barème
visibles seulement après la remise (moteur existant). Seed à la position du dernier cours du
module (EX01 : position 6, juste après PR06).

## 3. Statut d'une exigence

- **non traité** : aucun cours ni exercice lié publié ;
- **partiel** : au moins un élément lié publié, mais pas tous, ou pas encore validé ;
- **validé** : tous les cours PR **et** les examens blancs EX liés sont publiés **et** l'id figure
  dans `VALIDATED_REQUIREMENT_IDS` (ajouté par le ticket qui relit cours + exercice).

« Publié » = UAA `is_published` du module `AMPCR-PRATIQUE` portant le code de l'emplacement.
Les liens « théorie » (MCxx) indiquent seulement qu'un mini-cours existant aborde la notion
(contrôle textuel au ticket #192) ; ils ne valent jamais couverture de l'épreuve pratique.

## 4. Matrice (état à l'audit #236 du 2026-10-26 ; seul PR06 est publié)

| Id | Exigence (texte officiel) | Page | Nature | Cours prévus | Examens blancs | Théorie existante | Statut |
|---|---|---|---|---|---|---|---|
| AP-01 | La structure d’un ordinateur, ses composants et ses périphériques. | 5 | officiel | PR01 | EX01, EX05 | MC01 | non traité |
| AP-02 | Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). | 5 | officiel | PR01 | EX01 | MC01, MC02, MC03, MC07 | non traité |
| AP-03 | Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. | 5 | officiel | PR05 | EX01, EX02, EX06 | MC04, MC08 | non traité |
| AP-04 | Les caractéristiques d’une alimentation PC. | 5 | officiel | PR02 | EX01 | MC05 | non traité |
| AP-05 | Les périphériques d’entrée et de sortie et le rôle d'un pilote. | 5 | officiel | PR01, PR10 | EX02 | MC12 | non traité |
| AP-06 | Branchements, interfaces et connexions. | 5 | officiel | PR02 | EX01 | MC02 | non traité |
| AP-07 | La carte mère et ses éléments constitutifs. | 5 | officiel | PR01 | EX01 | MC02 | non traité |
| AP-08 | Les différents systèmes d’exploitation actuellement sur le marché. | 5 | officiel | PR07 | EX02 | MC09, MC11 | non traité |
| AP-09 | Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y afférant. *(Proche de AP-13 (les deux puces figurent au PDF).)* | 5 | officiel | PR11 | EX02 | MC07, MC29, MC30 | non traité |
| AP-10 | Installation complète des différents systèmes d’exploitation courants. | 5 | officiel | PR08, PR09 | EX02, EX05, EX06 | MC08, MC09 | non traité |
| AP-11 | Paramètres et commandes de base des systèmes d'exploitation courants. | 5 | officiel | PR10 | EX02 | MC10, MC11 | non traité |
| AP-12 | Interface graphique et interface de ligne de commande. | 5 | officiel | PR07, PR10 | EX02 | MC10, MC11 | non traité |
| AP-13 | Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment intervenir si possible. *(Proche de AP-09 (les deux puces figurent au PDF).)* | 5 | officiel | PR11 | EX02 | MC29, MC30 | non traité |
| AP-14 | Montage, démontage et reconditionnement d’un PC. | 5 | officiel | PR03, PR04 | EX01 | MC06 | non traité |
| AP-15 | Dépannage sur les dysfonctionnements courants (hardware ou software). | 5 | officiel | PR06, PR11, PR12, PR27 | EX01, EX02, EX05, EX06 | MC29, MC30 | non traité |
| AP-16 | Vocabulaire technique. *(Transversal : aucun cours dédié ; travaillé en rédaction (PR26, PR29) et dans le lexique AMPCR.)* | 5 | officiel | PR26, PR29 | EX05, EX06 | aucune | non traité |
| AP-17 | Notion de compatibilité. | 5 | officiel | PR01, PR02, PR06 | EX01, EX06 | MC04, MC12 | non traité |
| AP-18 | Les différents types de câbles : UTP, FTP, STP, Coax. *(FTP et coaxial absents de la théorie actuelle.)* | 5 | officiel | PR13, PR15, PR16 | EX03 | MC15 | non traité |
| AP-19 | Les débits binaires des câbles. | 6 | officiel | PR14 | EX03 | MC15 | non traité |
| AP-20 | Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. *(Atténuation et impédance absentes de la théorie actuelle.)* | 6 | officiel | PR13, PR14, PR15, PR16 | EX03 | MC15 | non traité |
| AP-21 | La fibre optique et ses caractéristiques : support d’information, débit binaire, longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, etc. *(La théorie actuelle ne fait que citer la fibre.)* | 6 | officiel | PR17 | EX03 | MC14 | non traité |
| AP-22 | Comparaison entre la fibre optique et les autres types de câbles. *(Aucune théorie existante.)* | 6 | officiel | PR17 | EX03 | aucune | non traité |
| AP-23 | Topologies de réseaux. | 6 | officiel | PR19 | EX04 | MC23 | non traité |
| AP-24 | Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs. *(Domaine / groupe de travail absents de la théorie actuelle.)* | 6 | officiel | PR22 | EX02 | MC33 | non traité |
| AP-25 | Partage de ressources (imprimantes, disques, répertoires…). | 6 | officiel | PR23 | EX04, EX05, EX06 | MC33 | non traité |
| AP-26 | Mise en partage sur un réseau informatique de documents et applications. | 6 | officiel | PR23 | EX04 | MC33 | non traité |
| AP-27 | Les notions de droit et de permission. | 6 | officiel | PR23 | EX02, EX04, EX06 | MC33, MC10 | non traité |
| AP-28 | Connexion de deux machines en direct. | 6 | officiel | PR21 | EX04 | MC15 | non traité |
| AP-29 | Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). *(NetBEUI absent de la théorie actuelle.)* | 6 | officiel | PR19 | EX04 | MC13, MC21 | non traité |
| AP-30 | L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. | 6 | officiel | PR20 | EX04, EX05, EX06 | MC16, MC20 | non traité |
| AP-31 | Hub, switch, passerelle, routeur, modem. *(Hub absent de la théorie actuelle.)* | 6 | officiel | PR19 | EX04 | MC14 | non traité |
| AP-32 | Connexions et interventions en cas de panne internet. | 6 | officiel | PR24 | EX04 | MC22, MC31 | non traité |
| AP-33 | WIFI : principe, sécurisation, cryptage, répéteur. *(Répéteur absent de la théorie actuelle.)* | 6 | officiel | PR25 | EX04, EX06 | MC25, MC26 | non traité |
| AP-34 | Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). | 6 | officiel | PR15 | EX03, EX05, EX06 | MC15 | non traité |
| AP-35 | Description de la réalisation d’un câble avec connecteurs BNC. *(Aucune théorie existante.)* | 6 | officiel | PR16 | EX03, EX05, EX06 | aucune | non traité |
| AP-36 | Câblage et installation physique d’un réseau informatique. | 6 | officiel | PR18, PR30 | EX05 | MC15, MC23 | non traité |
| AP-37 | Dépannage de problèmes simples d’accès au réseau. | 6 | officiel | PR24, PR30 | EX04, EX05 | MC31 | non traité |
| AP-38 | Création d’un mini réseau entre plusieurs machines. | 6 | officiel | PR18, PR21, PR30 | EX04 | MC16, MC37 | non traité |
| AP-C01 | Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. *(Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3).)* | — | complément pédagogique | PR26, PR27, PR29 | EX05, EX06 | MC36 | non traité |
| AP-C02 | Sécurité électrique et protection ESD lors d'une intervention sur un PC. *(Prérequis des interventions de montage/démontage (AP-14).)* | — | complément pédagogique | PR02, PR03, PR06, PR28 | EX01 | MC05 | non traité |
| AP-C03 | Protéger les données du client : sauvegarde préalable, confidentialité et autorisation avant tout effacement ou toute réinstallation. *(Ajouté à l'audit #236 : matière commune des tickets PR04, PR12 et PR28.)* | — | complément pédagogique | PR04, PR12, PR28 | EX02, EX06 | MC32 | non traité |

AP-01 → AP-18 : page 5 (18 puces) ; AP-19 → AP-38 : page 6 (20 puces). AP-09 et AP-13 sont
deux puces proches du PDF, conservées toutes les deux. AP-C01/AP-C02/AP-C03 sont des **compléments
pédagogiques** (absents des pp. 5-6), toujours affichés comme tels.

**Écarts de la théorie existante** relevés par l'audit (notion absente des MC publiés) :
FTP, câble coaxial et BNC, atténuation, impédance, comparaison fibre/cuivre (la fibre n'est
que citée en MC14), domaine / groupe de travail, NetBEUI, hub, répéteur Wi-Fi.

## 5. Modules, cours et examens blancs (alignés sur les tickets GitHub — audit #236)

Audit du 2026-10-26 (ticket #236) : les 30 tickets PR et les 6 tickets EX existent sur GitHub et
**font foi** (décision du propriétaire) pour le code, le titre et la matière. Le plan installé
jusqu'alors (proposition #192) ne plaçait le même sujet que pour PR01, PR06, PR11 et PR15 ;
`_COURSE_ROWS` / `_EXERCISE_ROWS` reprennent désormais les tickets, et les exigences AP sont
rattachées d'après la matière obligatoire de chaque ticket. Correspondance figée par
`tests/test_ticket236_ampcr_pratique_numerotation.py`. Seul PR06 (#193) est publié : code,
sujet et UAA inchangés, aucune progression déplacée.

| Module | Cours (ticket) | Examens blancs (ticket) |
|---|---|---|
| P1 — Matériel du PC : composants, montage et diagnostic | PR01 — Structure d'un PC et identification des composants (#202)<br>PR02 — Alimentation, connectique, compatibilité et sécurité (#203)<br>PR03 — Montage et démontage d'un PC — procédure écrite (#204)<br>PR04 — Reconditionnement, entretien et contrôles après intervention (#205)<br>PR05 — Stockage, partitions, formatage et défragmentation (#206)<br>PR06 — Diagnostic des pannes matérielles (#193) | EX01 — Examen blanc écrit — maintenance et dépannage matériel (#230) |
| P2 — Systèmes d'exploitation : installation et dépannage | PR07 — Systèmes d'exploitation, GUI/CLI et prérequis d'installation (#207)<br>PR08 — Installation complète de Windows — préparation et dépannage (#208)<br>PR09 — Installation complète de Linux — préparation et dépannage (#209)<br>PR10 — Comptes, pilotes, paramètres et commandes (#214)<br>PR11 — Messages d'erreur Windows/Linux — diagnostic et interventions écrites (#194)<br>PR12 — Dépannage logiciel et restauration du système (#215) | EX02 — Examen blanc écrit — installation et dépannage des systèmes (#231) |
| P3 — Câblage : cuivre, coaxial et fibre optique | PR13 — Câbles UTP, FTP, STP et coaxial — choix et pose (#216)<br>PR14 — Débits, distances, atténuation et impédance (#217)<br>PR15 — Câblage RJ45 T568A/B — fabrication, schémas et tests (#197)<br>PR16 — Câble coaxial et BNC — impédance, fabrication et diagnostic écrit (#198)<br>PR17 — Fibre optique — choix, raccordement et diagnostic (#218) | EX03 — Examen blanc écrit — câblage RJ45, BNC et fibre (#232) |
| P4 — Réseau : installation, configuration et dépannage | PR18 — Installation physique d'un mini-réseau (#219)<br>PR19 — Topologies, OSI, TCP/IP, NetBEUI et équipements (#220)<br>PR20 — IPv4, MAC, masques et passerelles — configuration et diagnostics écrits (#199)<br>PR21 — Connexion directe de deux PC et mini-réseau (#221)<br>PR22 — Domaine, groupe de travail, comptes et groupes (#222)<br>PR23 — Partage de dossiers, imprimantes et permissions (#223)<br>PR24 — Dépannage réseau et Internet — dossiers d'intervention écrits (#200)<br>PR25 — Wi-Fi : configuration, couverture, sécurité et diagnostic (#224) | EX04 — Examen blanc écrit — réseau, configuration et dépannage (#233) |
| P5 — Méthode d'intervention et examens blancs globaux | PR26 — Analyser une demande d'intervention technique (#225)<br>PR27 — Construire et justifier une procédure de diagnostic (#226)<br>PR28 — Outillage, sécurité et protection des données (#227)<br>PR29 — Contrôles finaux et rapport professionnel d'intervention (#228)<br>PR30 — Grand laboratoire écrit — installation et dépannage d'un réseau complet (#229) | EX05 — Examen blanc global standard — épreuve pratique écrite (#201) — global<br>EX06 — Examen blanc global avancé — dossiers complexes (#234) — global |

Exigences rattachées à chaque cours et examen : fiches de `docs/ampcr_pratique_tickets.md` § 4
et matrice `/ampcr-pratique/matrice`. Audit final de couverture : ticket #235.

## 6. Conventions pour les tickets de cours PR / d'exercices EX

1. **Un ticket par emplacement** (ou petit lot cohérent d'un même module), citant les ids
   d'exigences couverts. Toute exigence ajoutée/retirée d'un emplacement se fait dans
   `_COURSE_ROWS` / `_EXERCISE_ROWS` (le test `test_every_requirement_has_a_planned_course_and_exercise` garde
   l'exhaustivité).
2. **Base** : le premier ticket crée le module `AMPCR-PRATIQUE` (sujet Informatique) dans
   `app/seed.py` de façon idempotente. Une UAA par emplacement : code `PR01`…, slug
   `ampcr-pratique-pr01`. Une UAA non terminée reste `is_published=False` (jamais affichée).
3. **Cours** : même gabarit que les MC (théorie, définitions, méthode, exemples, pièges,
   mémo), orienté épreuve écrite : décrire une intervention, justifier, lire un document.
   Renvoyer vers les MC existants plutôt que dupliquer la théorie ; combler les écarts du § 4.
4. **Exercices** : format `app/v1/ampcr_pratique_format.py` (`PracticalExercise`) —
   situation suffisante, documents (`create_source_document`), consignes numérotées
   explicites, réponse libre, barème par critère, correction justifiée. `to_question_content`
   produit une question `document_analysis` (avec documents) ou `long_answer`, corrigée par
   le moteur existant (sessions, autosave, correction IA batch, historique).
   `validate_exercise` refuse : contexte trop court, barème vide, exigence inconnue, question
   de développé d'acronyme, titre « officiel ».
5. **Interdits** : présenter un exercice comme sujet ou extrait officiel ; inventer une durée,
   un barème officiel ou un nombre de questions d'examen (les consignes n'en donnent pas) ;
   questions artificielles « que signifie l'acronyme… » ; calculatrice supposée (elle est
   annoncée en début d'examen).
6. **Modèle de ticket** : chaque ticket PR/EX est un cahier des charges rédigé par le
   propriétaire (matière exhaustive à enseigner) ; la session n'improvise pas le programme.
   Amorces des 36 tickets, gabarit, exigences transversales, contrat de fin de ticket et
   checklist éditoriale/visuelle : `docs/ampcr_pratique_tickets.md` (généré par
   `python -m app.v1.ampcr_pratique_tickets`, synchronisé avec le plan par un test). Ces
   exigences s'appliquent à tout ticket PR/EX, même si son texte ne les recopie pas.
7. **Visuels** (§ 7) : schéma technique = SVG construit depuis des données vérifiées et
   testées ; image générée = scène ou geste uniquement.
8. **Validation** : quand tous les cours ET examens blancs d'une exigence sont publiés et relus, ajouter
   son id à `VALIDATED_REQUIREMENT_IDS`. La couverture n'est complète que si les 38 ids
   officiels y sont.

## 7. Supports visuels : capacités existantes et règles

Audit au 2026-10-26 :

| Besoin | Outil | État |
|---|---|---|
| Schéma technique exact (brochage, couleurs, flux, topologie, adressage, partitions) | SVG écrit en Python depuis des données vérifiées — `app/v1/ampcr_pratique_visuals.py` (`step_flow_svg`, `connector_pins_svg`, `Figure`, `render_figure`, `validate_figure`) | nouveau (#192), sans dépendance ; les cours FSE utilisaient déjà du SVG écrit à la main |
| Illustration d'ambiance (geste, outil, situation) | API d'images OpenAI côté serveur (`app/ai/image_provider.py`, `get_image_provider`) ; modèle `openai_image_model` | existant (#108, #136) : commande manuelle, ≤ 2 essais, fichier statique + JSON (prompt, modèle, date), WebP via Pillow ; jamais appelée à la consultation ni au seed ; clé jamais exposée |
| Composant interactif | JavaScript sans dépendance (`app/static/js/`) | existant ; pas de bibliothèque de diagrammes côté navigateur |
| Bibliothèques externes | Mermaid, Graphviz, etc. | **non installées** : Mermaid (rendu navigateur, plusieurs Mo de JS, texte mal maîtrisé à l'impression) et Graphviz (binaire système = infrastructure) ne sont pas justifiés à ce stade ; à réexaminer (licence, sécurité, poids, dépendances) par un ticket qui en aurait besoin |

Règles :

- tout schéma porteur d'une information technique est **dérivé de données** (ex. `T568A`,
  `T568B` dans `ampcr_pratique_visuals.py`) et un test vérifie ces données ; le texte de
  référence (tableau broche → couleur, étapes) reste affiché à côté du schéma ;
- l'orientation de lecture est écrite quand elle compte (`RJ45_ORIENTATION`) ;
- `render_figure` refuse un schéma sans texte alternatif (≥ 40 caractères), sans légende,
  sans `viewBox`, avec script ou ressource externe, ou présenté comme officiel à tort ; les
  figures portent `role="img"`, `<title>`, `<desc>` et la mention « schéma non officiel » ;
- mise en page : largeur fluide (mobile 360 px), pas de coupure de figure à l'impression
  A4 ; l'information ne repose jamais sur la seule couleur (fils blancs à bande rayés,
  numéros de broches, tableau texte) ;
- une image générée ne contient ni texte, ni valeur, ni brochage ; elle n'est jamais la
  seule source d'une information.

Démonstration en ligne : `/ampcr-pratique/format-exercice` (schémas des deux connecteurs de
l'exemple, construits depuis les mêmes données que le tableau du document 1, et démarche
d'intervention écrite en 6 étapes).

## 8. Contrat de fin de ticket PR/EX

Rapport daté dans `docs/claude-reports/`, email de fin de ticket envoyé par
l'orchestrateur `jcorch` (configuration SMTP existante, rapport joint, envoi journalisé),
commentaire GitHub de synthèse ; détail dans `docs/ampcr_pratique_tickets.md` § 2.

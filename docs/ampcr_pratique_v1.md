# AMPCR — Pratique écrite (cycle 2026-2027/1) : parcours, matrice et conventions (ticket #192)

Socle du parcours de l'**épreuve pratique** de l'option AMPCR (matières « Laboratoire » et
« T.P. et méthodes », évaluées ensemble, **uniquement par écrit**). Distinct du parcours
théorique MC01–MC38, qui reste inchangé.

## 1. Sources

| Document | URL | Version / date | Pages | SHA-256 |
|---|---|---|---|---|
| Consignes d'examen — pratique (fait foi) | [26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Consignes_specifiques/CESS/CESS_P/OBG/AMPCR/26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf) | cycle 2026-2027/1 (août 2026 → janvier 2027), PDF créé le 2026-07-13 | 6 | `7a93c3858ffd67b42620bc5364aa9b8e964a379bdf255bbcd126b50c4df095e1` |
| Programme 345/2007/249 (complément) | [AMPCR.pdf](https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Programmes/CESS/CESS_P/OBG/AMPCR/AMPCR.pdf) | d'application depuis 2008-2009, PDF modifié le 2015-10-29 | 46 | `95e45949fc3c36d6e8ea82e7643791d323b7f1a668da54113c373f41a69bf14b` |

Récupérés le 2026-10-26 depuis la page « Matières du CESS P » du site des Jurys. Les PDF ne
sont pas versionnés dans le dépôt (documents officiels, à re-télécharger). Le texte des
exigences et des consignes du jour est recopié dans `app/v1/ampcr_pratique_plan.py`
(extraction texte, espaces multiples réduits à un seul). Le programme est un complément :
les consignes rappellent qu'elles ne s'y substituent pas ; il n'est pas transcrit.
**Un nouveau cycle (2026-2027/2 : PDF pas encore publié) impose de recomparer l'empreinte et
le texte.**

## 2. Ce qui est en ligne

| URL | Contenu |
|---|---|
| `/ampcr-pratique` | accueil : consignes du jour (pp. 2-4), 6 modules, emplacements PR01–PR30 et EX01–EX06 (« À venir » tant qu'ils n'existent pas), liens vers la théorie MC déjà publiée, état de la couverture |
| `/ampcr-pratique/matrice` | matrice de traçabilité, une ligne par exigence, imprimable |
| `/ampcr-pratique/format-exercice` | format d'un exercice pratique écrit + exemple **non officiel**, imprimable A4 (corrigé sur une page séparée) |

Accès : tuile « AMPCR — Pratique écrite » de `/mon-parcours` (option AMPCR) et bouton
« Pratique écrite » de `/modules/ampcr`. Aucune table, aucun seed, aucune migration :
le plan est du code (`app/v1/ampcr_pratique_plan.py`), lu en lecture seule.

## 3. Statut d'une exigence

- **non traité** : aucun cours ni exercice lié publié ;
- **partiel** : au moins un élément lié publié, mais pas tous, ou pas encore validé ;
- **validé** : tous les cours PR **et** l'exercice EX liés sont publiés **et** l'id figure
  dans `VALIDATED_REQUIREMENT_IDS` (ajouté par le ticket qui relit cours + exercice).

« Publié » = UAA `is_published` du module `AMPCR-PRATIQUE` portant le code de l'emplacement.
Les liens « théorie » (MCxx) indiquent seulement qu'un mini-cours existant aborde la notion
(contrôle textuel au ticket #192) ; ils ne valent jamais couverture de l'épreuve pratique.

## 4. Matrice (état au ticket #192)

| Id | Exigence (texte officiel) | Page | Nature | Cours prévus | Exercice | Théorie existante | Statut |
|---|---|---|---|---|---|---|---|
| AP-01 | La structure d’un ordinateur, ses composants et ses périphériques. | 5 | officiel | PR01 | EX01 | MC01 | non traité |
| AP-02 | Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire RAM-ROM, carte mère, BIOS, UEFI, etc.). | 5 | officiel | PR01, PR02 | EX01 | MC01, MC02, MC03, MC07 | non traité |
| AP-03 | Les différents types de disque dur et unités de stockage, le formatage, la défragmentation. | 5 | officiel | PR03 | EX01 | MC04, MC08 | non traité |
| AP-04 | Les caractéristiques d’une alimentation PC. | 5 | officiel | PR04 | EX01 | MC05 | non traité |
| AP-05 | Les périphériques d’entrée et de sortie et le rôle d'un pilote. | 5 | officiel | PR10 | EX02 | MC12 | non traité |
| AP-06 | Branchements, interfaces et connexions. | 5 | officiel | PR05 | EX01 | MC02 | non traité |
| AP-07 | La carte mère et ses éléments constitutifs. | 5 | officiel | PR02 | EX01 | MC02 | non traité |
| AP-08 | Les différents systèmes d’exploitation actuellement sur le marché. | 5 | officiel | PR06 | EX02 | MC09, MC11 | non traité |
| AP-09 | Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y afférant. *(Proche de AP-13 (les deux puces figurent au PDF).)* | 5 | officiel | PR11, PR15 | EX03 | MC07, MC29, MC30 | non traité |
| AP-10 | Installation complète des différents systèmes d’exploitation courants. | 5 | officiel | PR07 | EX02 | MC08, MC09 | non traité |
| AP-11 | Paramètres et commandes de base des systèmes d'exploitation courants. | 5 | officiel | PR08 | EX02 | MC10, MC11 | non traité |
| AP-12 | Interface graphique et interface de ligne de commande. | 5 | officiel | PR09 | EX02 | MC10, MC11 | non traité |
| AP-13 | Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment intervenir si possible. *(Proche de AP-09 (les deux puces figurent au PDF).)* | 5 | officiel | PR11 | EX03 | MC29, MC30 | non traité |
| AP-14 | Montage, démontage et reconditionnement d’un PC. | 5 | officiel | PR12, PR13 | EX03 | MC06 | non traité |
| AP-15 | Dépannage sur les dysfonctionnements courants (hardware ou software). | 5 | officiel | PR14, PR15 | EX03 | MC29, MC30 | non traité |
| AP-16 | Vocabulaire technique. *(Transversal : lexique AMPCR existant.)* | 5 | officiel | PR30 | EX06 | aucune | non traité |
| AP-17 | Notion de compatibilité. | 5 | officiel | PR05, PR10, PR13 | EX01, EX02, EX03 | MC04, MC12 | non traité |
| AP-18 | Les différents types de câbles : UTP, FTP, STP, Coax. *(FTP et coaxial absents de la théorie actuelle.)* | 5 | officiel | PR16 | EX04 | MC15 | non traité |
| AP-19 | Les débits binaires des câbles. | 6 | officiel | PR17 | EX04 | MC15 | non traité |
| AP-20 | Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les connecteurs, etc. *(Atténuation et impédance absentes de la théorie actuelle.)* | 6 | officiel | PR17 | EX04 | MC15 | non traité |
| AP-21 | La fibre optique et ses caractéristiques : support d’information, débit binaire, longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, etc. *(La théorie actuelle ne fait que citer la fibre.)* | 6 | officiel | PR18 | EX04 | MC14 | non traité |
| AP-22 | Comparaison entre la fibre optique et les autres types de câbles. *(Aucune théorie existante.)* | 6 | officiel | PR18 | EX04 | aucune | non traité |
| AP-23 | Topologies de réseaux. | 6 | officiel | PR21 | EX05 | MC23 | non traité |
| AP-24 | Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs. *(Domaine / groupe de travail absents de la théorie actuelle.)* | 6 | officiel | PR26 | EX06 | MC33 | non traité |
| AP-25 | Partage de ressources (imprimantes, disques, répertoires…). | 6 | officiel | PR27 | EX06 | MC33 | non traité |
| AP-26 | Mise en partage sur un réseau informatique de documents et applications. | 6 | officiel | PR27 | EX06 | MC33 | non traité |
| AP-27 | Les notions de droit et de permission. | 6 | officiel | PR27 | EX06 | MC33, MC10 | non traité |
| AP-28 | Connexion de deux machines en direct. | 6 | officiel | PR28 | EX06 | MC15 | non traité |
| AP-29 | Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…). *(NetBEUI absent de la théorie actuelle.)* | 6 | officiel | PR22 | EX05 | MC13, MC21 | non traité |
| AP-30 | L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse IP. | 6 | officiel | PR23 | EX05 | MC16, MC20 | non traité |
| AP-31 | Hub, switch, passerelle, routeur, modem. *(Hub absent de la théorie actuelle.)* | 6 | officiel | PR24 | EX05 | MC14 | non traité |
| AP-32 | Connexions et interventions en cas de panne internet. | 6 | officiel | PR29 | EX06 | MC22, MC31 | non traité |
| AP-33 | WIFI : principe, sécurisation, cryptage, répéteur. *(Répéteur absent de la théorie actuelle.)* | 6 | officiel | PR25 | EX05 | MC25, MC26 | non traité |
| AP-34 | Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs). | 6 | officiel | PR19 | EX04 | MC15 | non traité |
| AP-35 | Description de la réalisation d’un câble avec connecteurs BNC. *(Aucune théorie existante.)* | 6 | officiel | PR20 | EX04 | aucune | non traité |
| AP-36 | Câblage et installation physique d’un réseau informatique. | 6 | officiel | PR21 | EX05 | MC15, MC23 | non traité |
| AP-37 | Dépannage de problèmes simples d’accès au réseau. | 6 | officiel | PR29 | EX06 | MC31 | non traité |
| AP-38 | Création d’un mini réseau entre plusieurs machines. | 6 | officiel | PR28 | EX06 | MC16, MC37 | non traité |
| AP-C01 | Rédiger une réponse écrite de technicien : décrire une intervention étape par étape et justifier chaque choix. *(Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3).)* | — | complément pédagogique | PR30 | EX06 | MC36 | non traité |
| AP-C02 | Sécurité électrique et protection ESD lors d'une intervention sur un PC. *(Prérequis des interventions de montage/démontage (AP-14).)* | — | complément pédagogique | PR12 | EX03 | MC05 | non traité |

AP-01 → AP-18 : page 5 (18 puces) ; AP-19 → AP-38 : page 6 (20 puces). AP-09 et AP-13 sont
deux puces proches du PDF, conservées toutes les deux. AP-C01/AP-C02 sont des **compléments
pédagogiques** (absents des pp. 5-6), toujours affichés comme tels.

**Écarts de la théorie existante** relevés par l'audit (notion absente des MC publiés) :
FTP, câble coaxial et BNC, atténuation, impédance, comparaison fibre/cuivre (la fibre n'est
que citée en MC14), domaine / groupe de travail, NetBEUI, hub, répéteur Wi-Fi.

## 5. Modules et emplacements (proposition de découpage)

| Module | Cours | Exercice |
|---|---|---|
| P1 — Matériel du PC | PR01 — Structure d'un ordinateur, composants et périphériques<br>PR02 — Carte mère, processeur, mémoire RAM-ROM, BIOS et UEFI<br>PR03 — Disques, unités de stockage, formatage et défragmentation<br>PR04 — Caractéristiques d'une alimentation PC<br>PR05 — Branchements, interfaces, connexions et compatibilité | EX01 |
| P2 — Systèmes d'exploitation | PR06 — Systèmes d'exploitation actuellement sur le marché<br>PR07 — Installation complète d'un système d'exploitation courant<br>PR08 — Paramètres et commandes de base<br>PR09 — Interface graphique et interface de ligne de commande<br>PR10 — Périphériques d'entrée et de sortie, rôle d'un pilote | EX02 |
| P3 — Intervention et dépannage du PC | PR11 — Messages d'erreur : interpréter et intervenir<br>PR12 — Montage et démontage d'un PC en sécurité<br>PR13 — Reconditionnement d'un PC<br>PR14 — Dépannage des dysfonctionnements matériels courants<br>PR15 — Dépannage des dysfonctionnements logiciels courants | EX03 |
| P4 — Câbles et supports de transmission | PR16 — Types de câbles : UTP, FTP, STP, coaxial<br>PR17 — Caractéristiques et débits des câbles<br>PR18 — La fibre optique et sa comparaison avec les câbles<br>PR19 — Réaliser un câble RJ45 : le code des couleurs<br>PR20 — Réaliser un câble à connecteurs BNC | EX04 |
| P5 — Réseau : architecture et adressage | PR21 — Topologies, câblage et installation physique d'un réseau<br>PR22 — Notions de base sur les protocoles<br>PR23 — Adressage IP et adresses MAC<br>PR24 — Hub, switch, passerelle, routeur, modem<br>PR25 — Wi-Fi : principe, sécurisation, cryptage, répéteur | EX05 |
| P6 — Partages, comptes et dépannage réseau | PR26 — Domaine, groupe de travail, comptes et groupes<br>PR27 — Partages, droits et permissions<br>PR28 — Connexion directe et mini réseau entre plusieurs machines<br>PR29 — Panne internet et problèmes simples d'accès au réseau<br>PR30 — Vocabulaire technique et rédaction d'une intervention | EX06 |

## 6. Conventions pour les tickets de cours PR / d'exercices EX

1. **Un ticket par emplacement** (ou petit lot cohérent d'un même module), citant les ids
   d'exigences couverts. Toute exigence ajoutée/retirée d'un emplacement se fait dans
   `_COURSE_ROWS` (le test `test_every_requirement_has_a_planned_course_and_exercise` garde
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
6. **Validation** : quand cours ET exercice d'une exigence sont publiés et relus, ajouter
   son id à `VALIDATED_REQUIREMENT_IDS`. La couverture n'est complète que si les 38 ids
   officiels y sont.

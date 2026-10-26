# Ticket #236 — Audit et harmonisation de la numérotation AMPCR pratique (PR01–PR30 / EX01–EX06)

- **Ticket** : #236 « [P0][AMPCR pratique] Audit et harmonisation de la numérotation PR01–PR30 / EX01–EX06 » — https://github.com/ReC82/jury-central/issues/236
- **État réel : Installé — à tester**
- **SHA installé** : `7d66de4` (develop, fusion de la PR #239)
- **PR** : https://github.com/ReC82/jury-central/pull/239
- **Date** : 2026-10-26

## 1. Résultat

Les 36 tickets GitHub (30 PR + 6 EX) ont été lus et comparés au plan installé
(`app/v1/ampcr_pratique_plan.py`, état `68eaf1f`). **Seuls PR01, PR06, PR11 et PR15 portaient le
sujet de leur ticket** ; les 26 autres cours et les 6 examens étaient en conflit. Comme décidé
par le propriétaire, les tickets font foi : le plan, la matrice, l'accueil du parcours, les
modèles de tickets et la documentation reprennent désormais **exactement le code, le n° de
ticket, le titre et la matière de chaque ticket**. Aucun cours n'a été réécrit, aucun ticket
créé, aucune donnée en base modifiée.

## 2. Tableau de correspondance définitif

« Matière du portail avant l'audit » = titre affiché sur `/ampcr-pratique` jusqu'au SHA `68eaf1f`.
Les exigences AP sont rattachées d'après la matière obligatoire de chaque ticket.

| ID | Ticket | Matière du ticket (fait foi) | Matière du portail avant l'audit | Constat | Exigences AP (après) |
|---|---|---|---|---|---|
| PR01 | #202 | Structure d'un PC et identification des composants | Structure d'un ordinateur, composants et périphériques | correspondance | AP-01, AP-02, AP-05, AP-07, AP-17 |
| PR02 | #203 | Alimentation, connectique, compatibilité et sécurité | Carte mère, processeur, mémoire RAM-ROM, BIOS et UEFI | **conflit → corrigé** | AP-04, AP-06, AP-17, AP-C02 |
| PR03 | #204 | Montage et démontage d'un PC — procédure écrite | Disques, unités de stockage, formatage et défragmentation | **conflit → corrigé** | AP-14, AP-C02 |
| PR04 | #205 | Reconditionnement, entretien et contrôles après intervention | Caractéristiques d'une alimentation PC | **conflit → corrigé** | AP-14, AP-C03 |
| PR05 | #206 | Stockage, partitions, formatage et défragmentation | Branchements, interfaces, connexions et compatibilité | **conflit → corrigé** | AP-03 |
| PR06 | #193 | Diagnostic des pannes matérielles | Diagnostic des pannes matérielles | correspondance (publié, inchangé) | AP-15, AP-17, AP-C02 |
| PR07 | #207 | Systèmes d'exploitation, GUI/CLI et prérequis d'installation | Montage et démontage d'un PC en sécurité | **conflit → corrigé** | AP-08, AP-12 |
| PR08 | #208 | Installation complète de Windows — préparation et dépannage | Reconditionnement d'un PC | **conflit → corrigé** | AP-10 |
| PR09 | #209 | Installation complète de Linux — préparation et dépannage | Systèmes d'exploitation actuellement sur le marché | **conflit → corrigé** | AP-10 |
| PR10 | #214 | Comptes, pilotes, paramètres et commandes | Installation complète d'un système d'exploitation courant | **conflit → corrigé** | AP-05, AP-11, AP-12 |
| PR11 | #194 | Messages d'erreur Windows/Linux — diagnostic et interventions écrites | Messages d'erreur Windows/Linux et démarches d'intervention | correspondance | AP-09, AP-13, AP-15 |
| PR12 | #215 | Dépannage logiciel et restauration du système | Paramètres et commandes de base | **conflit → corrigé** | AP-15, AP-C03 |
| PR13 | #216 | Câbles UTP, FTP, STP et coaxial — choix et pose | Interface graphique et interface de ligne de commande | **conflit → corrigé** | AP-18, AP-20 |
| PR14 | #217 | Débits, distances, atténuation et impédance | Périphériques d'entrée et de sortie, rôle d'un pilote | **conflit → corrigé** | AP-19, AP-20 |
| PR15 | #197 | Câblage RJ45 T568A/B — fabrication, schémas et tests | Câblage RJ45, normes T568A/B, réalisation et tests | correspondance | AP-18, AP-20, AP-34 |
| PR16 | #198 | Câble coaxial et BNC — impédance, fabrication et diagnostic écrit | Types de câbles et débits : UTP, FTP, STP, coaxial | **conflit → corrigé** | AP-18, AP-20, AP-35 |
| PR17 | #218 | Fibre optique — choix, raccordement et diagnostic | Caractéristiques des câbles : atténuation, impédance, parasites, longueurs | **conflit → corrigé** | AP-21, AP-22 |
| PR18 | #219 | Installation physique d'un mini-réseau | La fibre optique et sa comparaison avec les câbles | **conflit → corrigé** | AP-36, AP-38 |
| PR19 | #220 | Topologies, OSI, TCP/IP, NetBEUI et équipements | Réaliser un câble à connecteurs BNC | **conflit → corrigé** | AP-23, AP-29, AP-31 |
| PR20 | #199 | IPv4, MAC, masques et passerelles — configuration et diagnostics écrits | Topologies, câblage et installation physique d'un réseau | **conflit → corrigé** | AP-30 |
| PR21 | #221 | Connexion directe de deux PC et mini-réseau | Notions de base sur les protocoles | **conflit → corrigé** | AP-28, AP-38 |
| PR22 | #222 | Domaine, groupe de travail, comptes et groupes | Adressage IP et adresses MAC | **conflit → corrigé** | AP-24 |
| PR23 | #223 | Partage de dossiers, imprimantes et permissions | Hub, switch, passerelle, routeur, modem | **conflit → corrigé** | AP-25, AP-26, AP-27 |
| PR24 | #200 | Dépannage réseau et Internet — dossiers d'intervention écrits | Wi-Fi : principe, sécurisation, cryptage, répéteur | **conflit → corrigé** | AP-32, AP-37 |
| PR25 | #224 | Wi-Fi : configuration, couverture, sécurité et diagnostic | Domaine, groupe de travail, comptes et groupes | **conflit → corrigé** | AP-33 |
| PR26 | #225 | Analyser une demande d'intervention technique | Partages, droits et permissions | **conflit → corrigé** | AP-16, AP-C01 |
| PR27 | #226 | Construire et justifier une procédure de diagnostic | Connexion directe et mini réseau entre plusieurs machines | **conflit → corrigé** | AP-15, AP-C01 |
| PR28 | #227 | Outillage, sécurité et protection des données | Panne internet : connexions et interventions | **conflit → corrigé** | AP-C02, AP-C03 |
| PR29 | #228 | Contrôles finaux et rapport professionnel d'intervention | Dépannage de problèmes simples d'accès au réseau | **conflit → corrigé** | AP-16, AP-C01 |
| PR30 | #229 | Grand laboratoire écrit — installation et dépannage d'un réseau complet | Vocabulaire technique et rédaction d'une intervention | **conflit → corrigé** | AP-36, AP-37, AP-38 |
| EX01 | #230 | Examen blanc écrit — maintenance et dépannage matériel | Exercices pratiques écrits — Matériel du PC | **conflit → corrigé** | AP-01, AP-02, AP-03, AP-04, AP-06, AP-07, AP-14, AP-15, AP-17, AP-C02 |
| EX02 | #231 | Examen blanc écrit — installation et dépannage des systèmes | Exercices pratiques écrits — Intervention et dépannage matériel | **conflit → corrigé** | AP-03, AP-05, AP-08, AP-09, AP-10, AP-11, AP-12, AP-13, AP-15, AP-24, AP-27, AP-C03 |
| EX03 | #232 | Examen blanc écrit — câblage RJ45, BNC et fibre | Exercices pratiques écrits — Systèmes d'exploitation et messages d'erreur | **conflit → corrigé** | AP-18, AP-19, AP-20, AP-21, AP-22, AP-34, AP-35 |
| EX04 | #233 | Examen blanc écrit — réseau, configuration et dépannage | Exercices pratiques écrits — Câbles et supports de transmission | **conflit → corrigé** | AP-23, AP-25, AP-26, AP-27, AP-28, AP-29, AP-30, AP-31, AP-32, AP-33, AP-37, AP-38 |
| EX05 | #201 | Examen blanc global standard — épreuve pratique écrite | Exercices pratiques écrits — Réseau : architecture et adressage | **conflit → corrigé** | AP-01, AP-10, AP-15, AP-16, AP-25, AP-30, AP-34, AP-35, AP-36, AP-37, AP-C01 |
| EX06 | #234 | Examen blanc global avancé — dossiers complexes | Exercices pratiques écrits — Partages, comptes et dépannage réseau | **conflit → corrigé** | AP-03, AP-10, AP-15, AP-16, AP-17, AP-25, AP-27, AP-30, AP-33, AP-34, AP-35, AP-C01, AP-C03 |

### Modules (5, au lieu de 6)

Les tickets EX imposent 4 examens thématiques (matériel, systèmes, câblage, réseau) + 2 examens
blancs globaux : les modules suivent ce découpage.

| Module | Cours | Examens blancs |
|---|---|---|
| P1 — Matériel du PC : composants, montage et diagnostic | PR01–PR06 | EX01 |
| P2 — Systèmes d'exploitation : installation et dépannage | PR07–PR12 | EX02 |
| P3 — Câblage : cuivre, coaxial et fibre optique | PR13–PR17 | EX03 |
| P4 — Réseau : installation, configuration et dépannage | PR18–PR25 | EX04 |
| P5 — Méthode d'intervention et examens blancs globaux | PR26–PR30 | EX05, EX06 |

### Couverture des exigences (cours et examens prévus)

Les 38 exigences officielles (pp. 5-6 du PDF) et les 3 compléments ont chacun au moins un
cours ET un examen blanc prévus ; tous restent « non traité » ou « partiel » tant que rien n'est
validé (seul PR06 est publié).

| Exigence | Cours | Examens |
|---|---|---|
| AP-01 | PR01 | EX01, EX05 |
| AP-02 | PR01 | EX01 |
| AP-03 | PR05 | EX01, EX02, EX06 |
| AP-04 | PR02 | EX01 |
| AP-05 | PR01, PR10 | EX02 |
| AP-06 | PR02 | EX01 |
| AP-07 | PR01 | EX01 |
| AP-08 | PR07 | EX02 |
| AP-09 | PR11 | EX02 |
| AP-10 | PR08, PR09 | EX02, EX05, EX06 |
| AP-11 | PR10 | EX02 |
| AP-12 | PR07, PR10 | EX02 |
| AP-13 | PR11 | EX02 |
| AP-14 | PR03, PR04 | EX01 |
| AP-15 | PR06, PR11, PR12, PR27 | EX01, EX02, EX05, EX06 |
| AP-16 | PR26, PR29 | EX05, EX06 |
| AP-17 | PR01, PR02, PR06 | EX01, EX06 |
| AP-18 | PR13, PR15, PR16 | EX03 |
| AP-19 | PR14 | EX03 |
| AP-20 | PR13, PR14, PR15, PR16 | EX03 |
| AP-21 | PR17 | EX03 |
| AP-22 | PR17 | EX03 |
| AP-23 | PR19 | EX04 |
| AP-24 | PR22 | EX02 |
| AP-25 | PR23 | EX04, EX05, EX06 |
| AP-26 | PR23 | EX04 |
| AP-27 | PR23 | EX02, EX04, EX06 |
| AP-28 | PR21 | EX04 |
| AP-29 | PR19 | EX04 |
| AP-30 | PR20 | EX04, EX05, EX06 |
| AP-31 | PR19 | EX04 |
| AP-32 | PR24 | EX04 |
| AP-33 | PR25 | EX04, EX06 |
| AP-34 | PR15 | EX03, EX05, EX06 |
| AP-35 | PR16 | EX03, EX05, EX06 |
| AP-36 | PR18, PR30 | EX05 |
| AP-37 | PR24, PR30 | EX04, EX05 |
| AP-38 | PR18, PR21, PR30 | EX04 |
| AP-C01 | PR26, PR27, PR29 | EX05, EX06 |
| AP-C02 | PR02, PR03, PR06, PR28 | EX01 |
| AP-C03 | PR04, PR12, PR28 | EX02, EX06 |


## 3. Changements réalisés

- `app/v1/ampcr_pratique_plan.py` : `CourseSlot` / `ExerciseSlot` portent `ticket` ;
  `_COURSE_ROWS` réaligné sur les tickets ; nouveau `_EXERCISE_ROWS` (chaque examen a ses
  propres exigences, EX05/EX06 marqués `is_global`) ; `exercises_for_requirement` se base sur
  ces exigences (avant : déduit du module) ; 5 modules ; `PracticalModule.exercise_codes`
  (tuple) ; complément **AP-C03** « protection des données du client » (matière commune de
  PR04, PR12, PR28) ; note de AP-16 (vocabulaire) précisée ; `ticket_url()`.
- `app/v1/routes_ampcr_pratique.py`, `app/templates/ampcr_pratique_home.html` : plusieurs
  examens par module, mention « (tout le parcours) » pour EX05/EX06, « Les 5 modules »,
  compteur « examens blancs ».
- `app/templates/ampcr_pratique_matrix.html` : colonne « Examens blancs » (titre au survol).
- `app/templates/parcours_dashboard.html` : description de la carte du parcours.
- `app/v1/ampcr_pratique_tickets.py` + `docs/ampcr_pratique_tickets.md` (régénéré) : fiches
  des 36 tickets avec n° et lien GitHub, titres réels, exigences par examen, mode d'emploi mis
  à jour (les tickets existent et font foi).
- `docs/ampcr_pratique_v1.md` (§ 4 matrice, § 5 tableau modules/cours/examens avec tickets),
  `docs/current_state.md`, `docs/changelog.md`.
- Tests : nouveau `tests/test_ticket236_ampcr_pratique_numerotation.py` (25 tests) ;
  `tests/test_ticket192_ampcr_pratique*.py` adaptés (5 modules, AP-04 → PR02, en-têtes).

## 4. Contenu publié et progressions — aucune perte

Vérifié en lecture seule (`sqlite3 -readonly`) avant et après : le module `AMPCR-PRATIQUE`
ne contient qu'une UAA, **PR06 « Diagnostic des pannes matérielles »** (`ampcr-pratique-pr06`,
publiée). PR06 garde son code, son titre, son slug et ses exigences : aucune migration n'était
nécessaire et aucune n'a été faite. Le seed n'a pas changé (pas d'exécution). Compteurs
utilisateurs / sessions / réponses : 18 / 79 / 636 avant et après l'installation. Sauvegarde de
la base prise avant installation dans le dossier de sauvegardes de l'orchestrateur.

## 5. Liens pour tester

- https://jury-central.lodylands.com/ampcr-pratique — 5 modules, chaque cours/examen sous
  son code et le titre de son ticket ; EX05/EX06 marqués « (tout le parcours) » ; PR06 toujours
  cliquable.
- https://jury-central.lodylands.com/ampcr-pratique/matrice — colonnes « Cours prévus » /
  « Examens blancs » conformes au tableau ci-dessus ; ligne AP-C03.
- https://jury-central.lodylands.com/uaa/ampcr-pratique-pr06 — cours PR06 inchangé.
- https://jury-central.lodylands.com/modules/ampcr — théorie MC01–MC38 inchangée.

Procédure : ouvrir l'accueil, comparer 3–4 lignes au tableau du § 2 (ex. PR13 « Câbles UTP,
FTP, STP et coaxial », PR20 « IPv4, MAC… », EX03 « câblage RJ45, BNC et fibre »), puis la matrice.

## 6. Vérifications effectuées

- `pytest` : nouveaux tests #236 + fichiers AMPCR pratique #192/#193, parcours #136, quiz #137
  → **144 passed** ; `test_admin_content_hierarchy` + fichiers #192/#193 → 131 passed.
- `ruff check` sur les fichiers Python modifiés : aucune erreur.
- Après installation : 2 services actifs, `/health` local et public OK, pages
  `/ampcr-pratique`, `/matrice`, `/format-exercice`, `/uaa/ampcr-pratique-pr06` en HTTP 200 ;
  contenu public contrôlé (« Les 5 modules », PR13 et EX05 aux bons titres, 1 cours publié).
- Non effectué : suite complète (moteur partagé non touché) ; contrôle visuel navigateur.

## 7. Choix techniques faits seul

1. **Rattachement des exigences AP** : déduit de la matière obligatoire écrite dans chaque
   ticket (PR06, PR11, PR15 gardent exactement leurs exigences d'avant).
2. **Examens avec exigences propres** : les tickets EX définissent leur périmètre (ex. EX02
   inclut comptes/groupes et permissions) ; un examen n'est plus déduit du module.
3. **5 modules** : P1 matériel (PR01–PR06, EX01), P2 systèmes (PR07–PR12, EX02), P3 câblage
   (PR13–PR17, EX03), P4 réseau (PR18–PR25, EX04), P5 méthode d'intervention (PR26–PR30) avec
   les examens globaux EX05/EX06 — découpage dicté par les 4 examens thématiques.
4. **AP-C03** (complément, jamais compté comme officiel) : la protection des données revient
   dans PR04, PR12, PR28 et EX02/EX06 ; lien théorie MC32 (seul MC qui mentionne la sauvegarde).
5. **AP-16 « Vocabulaire technique »** : aucun ticket ne lui est dédié ; rattaché à PR26/PR29
   (rédaction) et EX05/EX06, avec une note explicite.
6. **Pas de migration de base** : seul PR06 existe et il ne change pas.
7. **Préfixe de priorité retiré** des fiches générées (les tickets réels ont P0, P1 ou P2).

## 8. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire. Point signalé (pas bloquant) : le cours publié PR06
contient dans ses « Sources et compléments » la phrase « traçabilité et compte rendu …
approfondis en PR30 » ; avec la numérotation des tickets, le rapport d'intervention est
**PR29** (#228). Le cours n'a pas été réécrit (hors périmètre) ; recommandation : corriger ce
renvoi lors du ticket #228 (PR29) ou par l'admin.

## 9. Reste à réaliser

- Rien pour #236. Les tickets de cours/examens (#194–#234) peuvent reprendre sur cette
  numérotation ; l'audit final de couverture reste #235.
- Suggestion (non implémentée) : afficher le n° de ticket GitHub à côté de chaque emplacement
  « à venir » dans l'admin.

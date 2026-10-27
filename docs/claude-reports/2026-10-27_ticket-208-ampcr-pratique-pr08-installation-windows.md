# Ticket #208 — [AMPCR pratique PR08] Installation complète de Windows — préparation et dépannage

- Ticket : https://github.com/ReC82/jury-central/issues/208
- **État réel : Installé — à tester**
- SHA installé : `436a4be42c4c24a8fdfac593777b7f7d7bf18361` (fusion de la PR #267 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR08 « Installation complète de Windows — préparation et dépannage »** est publié
dans le parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de
la théorie MC : cours, banque, examen et progression séparés ; liens croisés vers MC07, MC08,
MC09, MC10 et MC12 seulement). C'est le huitième cours de l'ordre pédagogique, placé juste après
PR07 (position 8). **Numérotation vérifiée** : l'emplacement PR08 du plan installé
(`_COURSE_ROWS`, numérotation définitive de #236) porte bien le sujet du ticket (« PR08, ticket
208, Installation complète de Windows — préparation et dépannage », exigence AP-10) : aucun
écart, aucun autre cours touché ni renuméroté.

Contenu (20 blocs) :

- **13 chapitres de théorie**, chacun avec objectifs, théorie, **procédure professionnelle à
  rédiger**, **erreur fréquente**, « à l'écrit », repère rapide et renvoi aux exercices liés :
  1. **demande, accord écrit et inventaire** (fiche d'inventaire en 7 rubriques : quoi relever
     et pourquoi) ;
  2. **compatibilité avec la version visée** (renvoi à PR07) et **pilotes du fabricant**
     (stockage et réseau d'abord) ;
  3. **licence, édition et activation** (OEM dans le firmware, commerciale, licence numérique ;
     « Je n'ai pas de clé » ; l'édition installée = celle de la licence ; `slmgr /xpr`) ;
  4. **sauvegarde vérifiée** ; **installation propre, mise à niveau ou migration** (tableau de
     migration : profils, dossiers hors profil, navigateur, courrier .pst, licences logicielles,
     imprimantes et Wi-Fi) ;
  5. **média USB** (outil de création ou ISO officielle à somme contrôlée, Rufus GPT/UEFI,
     FAT32) et **pilotes à emporter** (dossier F6 Intel RST/VMD, réseau) ;
  6. **firmware UEFI et démarrage** (démarrage sécurisé, TPM 2.0, mode du contrôleur noté et
     plus modifié, autres disques débranchés, menu de démarrage, entrée « UEFI: », installation
     qui recommence) ;
  7. **l'installateur** : langue, format, clavier belge, clé, édition, installation
     personnalisée ;
  8. **disque et partitions** : identifier le disque cible par sa taille, **règle de
     suppression** (supprimer seulement sur le disque cible après sauvegarde vérifiée et accord
     écrit ; ne pas toucher aux autres ; sinon arrêter), disposition **GPT standard** (ESP, MSR,
     Windows, Récupération), message « GPT sur systèmes EFI », `mbr2gpt`, `diskpart` (Maj+F10,
     sans `clean`) ;
  9. **configuration initiale** : réseau, nom, compte saisi par le client, confidentialité ;
  10. **pilotes et mises à jour** : ordre, Gestionnaire de périphériques, **ID du matériel
      VEN/DEV** (table des fabricants), Windows Update ;
  11. **activation, sécurité et restauration** (Defender, pare-feu, chiffrement + clé de
      récupération, point de restauration ≠ sauvegarde, lecteur de récupération) ;
  12. **dépannage de l'installation par cinq familles** (stockage non détecté, démarrage,
      partitions, pilotes manquants, licence) : symptôme, vérification, action, « ne jamais » ;
  13. **liste de contrôle finale** (10 points) et **rapport d'intervention** (7 rubriques).
- **3 procédures illustrées** : préparer (6 étapes), installer de la clé au bureau (8 étapes),
  finaliser/sécuriser/valider (6 étapes).
- **5 cas résolus** (exigence du ticket), un par variante demandée : installation propre
  complète **avec migration** ; **stockage non détecté** (Intel VMD) ; **échec de démarrage**
  (chargeur placé dans la partition EFI de l'ancien disque) ; **pilotes manquants** (ID du
  matériel) ; **partitionnement incorrect** (disque MBR avec partition de données à garder,
  sauvegarde puis `mbr2gpt`). Aucun ne recommande d'effacer sans autorisation.
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (ticket : ≥ 16) : **3 remises en ordre** (les trois procédures),
  **4 classements** auto-corrigés (symptôme → famille de cause, action sur chaque partition,
  activation selon la licence, avant / pendant / après l'installation), fiche d'inventaire,
  écran « aucun lecteur », disque MBR refusé + `diskpart`, ID du matériel, clé non « UEFI: »,
  PC à deux disques, migration, rapport à rédiger, procédure d'un collègue à corriger. Chacun :
  contexte complet, documents, consignes, barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc », jamais
  affiché dans le cours (activation après mauvaise édition, choix du disque sur un PC à deux
  disques, SSD non vu, préparation d'une réinstallation, Windows installé en mode hérité,
  réseau absent, installation qui recommence, liste de contrôle, « effacez tout » au téléphone,
  INACCESSIBLE_BOOT_DEVICE après changement du mode du contrôleur).
- **9 schémas SVG** produits depuis des données testées : 3 procédures, plan de partitions GPT,
  arbre « l'installateur ne propose pas le bon disque », 4 captures **clairement identifiées
  comme fictives** (choix de l'emplacement sur deux disques, « aucun lecteur », disque MBR +
  diskpart, Gestionnaire de périphériques). Alt complet, légende, mention « schéma non
  officiel », responsive. **Aucune image générée ni photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr08_figures.py` — inventaire, licences et `activation_result`,
  disposition GPT (`STANDARD_LAYOUT`), règle `partition_action`, tableau de dépannage
  (`TROUBLESHOOTING`), arbre « disque introuvable », codes fabricants (`vendor_of`), migration,
  3 procédures, liste de contrôle, rubriques du rapport, captures fictives, figures
- `app/v1/ampcr_pratique_pr08_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr08_course.py` — 20 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR08 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR08", …, position 8)` dans le module pratique (additif)
- `tests/test_ticket208_ampcr_pratique_pr08.py` (27 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket207_ampcr_pratique_pr07.py`
  (nombre de cours publiés)
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr08
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr08/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr08/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 13, cas résolus,
exercices) ; lancer une session « S'entraîner » (10 exercices tirés des 16, dont des remises en
ordre et des classements auto-corrigés) puis un « Examen blanc » (10 questions, note sur 20) ;
vérifier la correction et le barème après envoi. Dans l'accueil du parcours, PR08 apparaît après
PR07 (« 13 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket208_ampcr_pratique_pr08.py` : **27 passed** — activation
  recontrôlée (édition ≠ licence jamais activée, OEM/numérique liées au PC, commerciale
  transférable si retirée), règle des partitions (jamais de suppression hors disque cible ni
  sans sauvegarde vérifiée ET accord écrit), disposition GPT (ESP FAT32 ≈ 100 Mo, MSR 16 Mo,
  NTFS, WinRE), cinq familles de dépannage couvertes, codes fabricants PCI (8086, 10EC, 10DE,
  1022, 14E4), ordre des 3 procédures, liste de contrôle et rapport, captures (largeur mobile,
  disque 0 sans astérisque GPT), schémas (validité, accessibilité, étapes et partitions =
  données), remises en ordre et classements auto-corrigés, absence de question d'acronyme et
  d'affirmation fausse, matière du ticket présente, 5 cas résolus, examen absent du cours, liens
  (MC07-MC10, MC12, PR04-PR07, PR11 ; pas de lien vers PR09/PR10/PR12 non publiés), seed
  idempotent et position après PR07, réserves séparées, contexte de correction, pages, sessions
  entraînement/examen, note /20, aucune génération IA.
- Tests liés (socle #192, numérotation #236, PR04, PR05, PR07, EX01, hiérarchie admin) :
  **207 passed** avec PR08.
- **Suite complète** (une exécution, `seed.py` étant partagé) : **2 627 passed** en 21 min, aucun échec.
- `ruff check` sur les fichiers créés et modifiés : **All checks passed**.
- Contrôle visuel (navigateur sans interface, 440 px de large) des 9 schémas ; libellés du plan
  de partitions raccourcis après ce contrôle (chevauchement corrigé).
- Relecture technique : nuance corrigée avant livraison (cas du PC à deux disques : l'installateur
  réutilise une partition EFI **existante** d'un autre disque ; le scénario met donc en jeu
  l'ancien disque système, pas un disque vide).
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket208-20261027-030944.db`),
  fast-forward `65da46a → 436a4be`, seed idempotent (1 UAA créée ; les 72 blocs « créés » =
  20 blocs PR08 + le remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice et de PR07 en HTTP 200 (entraînement/examen : 303 vers la connexion,
  normal sans session), « 13 cours publiés sur 30 prévus » sur l'accueil, 16 cartes d'exercice et
  9 figures servies. Compteurs utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés ; les 9 schémas ont été
contrôlés visuellement à 440 px).

## 4. Choix techniques faits seul

- **Écrans de l'installateur non figés** : Microsoft change les libellés selon les versions ; le
  cours enseigne **l'ordre des décisions** et présente les captures comme **fictives, libellés
  approximatifs**, avec « la documentation de Microsoft fait foi ».
- **Règles codées et partagées** par les tableaux, les schémas, les classements et les
  corrigés : `activation_result` (licence × édition × PC), `partition_action` (disque cible ×
  sauvegarde vérifiée × accord écrit → supprimer / ne pas toucher / arrêter), tableau
  `TROUBLESHOOTING` (cinq familles = les cinq variantes du ticket), `vendor_of` (codes VEN de la
  liste publique PCI-SIG). Énoncé, cours et corrigé ne peuvent pas diverger.
- **Jamais d'effacement sans autorisation** (exigence du ticket) : chaque cas et chaque corrigé
  passent par l'accord écrit et la sauvegarde vérifiée ; le cas « partitionnement incorrect »
  conserve la partition de données (`mbr2gpt` après sauvegarde) ; un « effacez tout » au
  téléphone est traité comme insuffisant (X09).
- **Pas de contournement** : ni désactivation du démarrage sécurisé, ni mode hérité, ni
  activateur ; la configuration hors ligne de Windows 11 n'est pas enseignée (le cours fait
  préparer le pilote réseau).
- **Liste de contrôle (10 points) et rubriques du rapport (7)** signalées comme **conventions du
  cours**, pas comme une norme.
- **Recouvrement limité** : prérequis et choix du système renvoyés à PR07 (publié, lien),
  partitions à PR05, diagnostic disque à PR06, écrans d'arrêt à PR11 (publiés, liens) ; PR09
  (Linux), PR10 (comptes, commandes) et PR12 (restauration du système) cités **en texte
  seulement** (non publiés). Exigence AP-10 (plan installé) et complément AP-C03 ; statut
  « partiel » dans la matrice, jamais « validé ».
- Pas de photographie ni d'image générée : les sujets (procédures, partitions, écrans) sont
  techniques et produits en SVG depuis des données testées, avec les assistants existants
  (`step_flow_svg`, `partition_map_svg`, `decision_tree_svg`, `screen_svg`) ; aucun nouvel
  assistant partagé, aucune nouvelle dépendance ; constructeurs d'items réutilisés depuis la
  banque PR04, type d'item de PR06.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR09 « Installation complète de Linux » (#209).
- Améliorations repérées, non implémentées (hors périmètre) : (1) PR07 cite PR08 en texte
  seulement ; un lien vers `/uaa/ampcr-pratique-pr08` pourrait y être ajouté (le test de PR07
  vérifie aujourd'hui l'absence de ce lien et serait à adapter) ; (2) dans l'arbre de décision
  partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche sur mobile (déjà
  signalé pour PR02 à PR07, visible aussi sur l'arbre de PR08).

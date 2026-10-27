# Ticket #230 — [AMPCR pratique EX01] Examen blanc écrit — maintenance et dépannage matériel

- Ticket : https://github.com/ReC82/jury-central/issues/230
- **État réel : Installé — à tester**
- SHA installé : `7e093d6149ee50b46e98831e9142cd3f0c7d73d5` (fusion de la PR #263 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le **premier examen blanc** du parcours **Informatique AMPCR → Pratique écrite** est publié :
**EX01 « Examen blanc écrit — maintenance et dépannage matériel »**, épreuve autonome **/100**
du module 1 (cours PR01 → PR06, tous publiés). Il est placé juste après PR06 dans la
navigation, comme le demande l'ordre pédagogique du propriétaire (« EX01 après PR06 »).
L'emplacement EX01 du plan installé (`_EXERCISE_ROWS`, numérotation définitive de #236 :
« EX01, ticket 230 ») porte bien le sujet du ticket : aucun écart, aucun autre cours ni examen
touché. Module `AMPCR-PRATIQUE` uniquement : Théorie (MC) et Pratique restent séparées
(banques, sessions, progression).

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex01`, onglets « Sujet » et « Examen blanc ») —
  version candidat **sans aucun corrigé** :
  1. présentation, organisation et notation (10 questions × 10 points, réponses rédigées,
     barème analytique, corrigé après remise, durée conseillée de 2 h présentée comme repère
     personnel **et non comme durée officielle**), mode d'emploi, impression A4 ;
     **barème global** (question, partie, points, exigences AP, cours à revoir) ; exigences
     officielles évaluées ;
  2. **Partie 1** — plan lettré de carte mère + questions 1 à 3 ;
  3. **Dossier A — fiduciaire Mertens** (fiche d'intervention, LED de diagnostic, extrait du
     manuel, mémoire relevée ; journal d'intervention affiché seulement avant la question 5) ;
  4. **Dossier B — studio Lumen** (configuration, demande et offres, puissances des fiches,
     relevé de températures + courbe, observations) ;
  5. **Dossier C — clinique vétérinaire Les Saules** (demande, capture UEFI du stockage,
     extrait du manuel, relevé SMART) ;
  6. méthode pour répondre à un dossier écrit ; 7. sources et supports fictifs.
  À l'impression : 12 lignes de réponse sous chaque question, chaque dossier sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex01/exam`) : session de 10 questions, une par écran,
  chacune avec les documents de son dossier (les deux schémas s'affichent dans leur question,
  avec leur description écrite complète) ; **sauvegarde automatique et reprise** (moteur
  existant) ; barème et corrigé invisibles avant la remise ; page de résultats avec la **note
  /100** (et le repère /20 habituel), puis corrigé détaillé par question.
- « S'entraîner » n'existe pas pour un examen blanc : `/practice` (et `/practice/start`)
  redirigent vers l'examen (on s'entraîne dans PR01 → PR06).

### Les 10 questions (10 points chacune, barème en 3 à 5 critères, corrigé détaillé)

| N° | Partie | Question | Exigences |
|---|---|---|---|
| 1 | Partie 1 | Identifier 12 éléments sur un plan lettré de carte mère, branchements (EPS, CPU_FAN, façade, M.2), liaisons au processeur | AP-01, AP-02, AP-07, AP-06 |
| 2 | Partie 1 | Corriger une intervention dangereuse (PC branché, moquette, laine, bracelet non relié, contacts touchés) : sécurité électrique et ESD | AP-C02, AP-14 |
| 3 | Partie 1 | Choisir l'outillage d'un nettoyage + changement de bloc, écarter visseuse / aspirateur / eau / cutter, précautions de la bombe d'air | AP-14, AP-C02 |
| 4 | Dossier A | Absence de POST après ajout de mémoire (LED DRAM, barrette mal enclenchée, entraînement mémoire coupé à 30 s, barrettes mélangées) : procédure ordonnée | AP-15, AP-02, AP-17 |
| 5 | Dossier A | Contrôles de fin d'intervention, compte rendu à la gérante, explication DDR5-4800 (vitesse de la plus lente) | AP-15, AP-C01 |
| 6 | Dossier B | Compatibilité carte graphique / bloc / connecteurs / longueur et mémoire DDR4 ou DDR5 ; calcul du bloc **567 W → 737,1 W → 750 W** | AP-17, AP-04, AP-06 |
| 7 | Dossier B | Procédure écrite de démontage/remontage (bloc, carte graphique, mémoire), contrôles et premier démarrage | AP-14, AP-06, AP-C02 |
| 8 | Dossier B | Surchauffe : 98 °C « à surveiller », 100 °C « anormal », throttling, ventilateur sur SYS_FAN2 à vitesse fixe, poussière, pâte ; preuve par test de charge | AP-15, AP-14, AP-06 |
| 9 | Dossier C | SSD ajouté non détecté : SATA_5 désactivé par le SSD M.2 SATA dans M.2_2 ; correction, vérifications, initialisation GPT d'un disque neuf et vide | AP-03, AP-06, AP-15 |
| 10 | Dossier C | Relevé SMART « PASSED » mais 24 secteurs en attente/illisibles → à remplacer ; copie d'abord, actions interdites, message au client | AP-03, AP-15, AP-C03 |

Les 10 exigences de l'emplacement EX01 (AP-01, 02, 03, 04, 06, 07, 14, 15, 17, C02) sont toutes
évaluées ; aucune n'est déclarée « validée » (matrice : statut « partiel »).

### Fichiers

- `app/v1/ampcr_pratique_ex01_figures.py` — données des dossiers et schémas : plan lettré
  (géométrie du plan de PR01), LED, budget d'alimentation (`power_budget`/`recommended_psu`
  de PR02), températures (`temperature_verdict` de PR03), SMART (`smart_verdict` de PR04),
  écran UEFI, 3 figures SVG.
- `app/v1/ampcr_pratique_ex01_bank.py` — 10 questions, documents des dossiers, validation.
- `app/v1/ampcr_pratique_ex01_course.py` — 7 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex01-plan-carte-mere.svg`, `ex01-led-diagnostic.svg` —
  schémas affichés dans les questions (identiques au SVG du code, vérifié par test).
- `app/v1/ampcr_pratique_bank.py` — EX01 déclaré (contexte de correction spécifique),
  `is_practical_exam_code`, mise en page `figure` des documents à image.
- `app/v1/ampcr_pratique_format.py` — champ optionnel `ExerciseDocument.image`.
- `app/templates/_document_layouts.html` — mise en page `figure` (image + description).
- `app/templates/_uaa_space_nav.html`, `uaa_detail.html` — onglets « Sujet / Examen blanc »
  et libellé « examen blanc » pour un EX du parcours pratique (cours PR inchangés).
- `app/templates/v1_session_results.html` — note /100 pour une session EX.
- `app/main.py`, `app/v1/routes_sessions.py` — redirection de `/practice` vers `/exam` pour EX.
- `app/seed.py` — `_seed_uaa(…, "EX01", …, position 6)` (additif).
- `app/static/css/jc-theme.css` — styles du schéma de question et du sujet imprimable.
- `tests/test_ticket230_ampcr_pratique_ex01.py` (23 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md` (modèle d'intégration d'un examen
  blanc pour EX02–EX06), `docs/changelog.md`.

## 2. Liens pour tester

- Sujet (public) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex01
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex01/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le sujet, parcourir les séquences (présentation → partie 1 → dossiers
A, B, C) ; essayer l'aperçu avant impression (Ctrl + P : sujet complet, lignes de réponse,
aucun corrigé) ; lancer l'examen blanc, répondre à quelques questions, quitter et reprendre
(sauvegarde), remettre, puis vérifier la note /100, le barème et le corrigé de chaque question.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket230_ampcr_pratique_ex01.py` : **23 passed** — budget
  d'alimentation et bloc recalculés indépendamment (567 W, 737,1 W, 750 W ≥ 700 W), verdicts de
  température (98 °C à surveiller, 100 °C anormal, après intervention 77 °C normal) et SMART
  (à remplacer), LED, port SATA partagé, plan lettré cohérent avec la géométrie de PR01 ;
  figures valides et accessibles, fichiers statiques identiques au SVG du code ; 10 questions de
  10 points (= 100), réponses libres, 3 dossiers dont chaque document sert, matière du ticket
  présente, exigences de l'emplacement couvertes, pas de question d'acronyme ; sujet sans aucun
  corrigé ni barème détaillé, 10 zones de réponse imprimables ; seed idempotent, EX01 juste
  après PR06 ; réserve `exam` seule ; contexte de correction ; navigation sans « S'entraîner »
  (redirections), page d'accueil ; session d'examen : 10 questions, aucune génération IA,
  corrigé masqué avant remise, schémas affichés dans leurs questions, note /100 ; un cours PR
  garde uniquement le repère /20.
- **Suite complète : 2574 passed, 1 failed** (une exécution, le seed et les gabarits partagés
  étant touchés) ; l'échec venait d'un test de #236 qui supposait que seuls des cours PR étaient
  publiés : adapté (un examen publié garde aussi le code et le titre de son ticket), puis tests
  #236, #230 et hiérarchie relancés : 85 passed. Un premier passage s'était arrêté sur le
  comptage des UAA/blocs seedés (`test_admin_content_hierarchy.py`), adapté comme à chaque cours.
- `ruff check` sur les fichiers créés et les tests modifiés : aucune erreur ; fichiers partagés
  modifiés : aucune nouvelle erreur par rapport à `develop`.
- Contrôle visuel (navigateur sans interface) : les 3 schémas (corrigé après contrôle :
  l'étiquette du seuil de la courbe chevauchait la valeur 98 → « max. fiche 100 °C ») ; une
  question de session à 400 px de large (plan et description affichés) ; la page du sujet à
  1 280 px (séquences, barème global, dossiers, questions). Relecture : deux fuites de réponse
  corrigées (journal A5 affiché avant la question 4 ; valeurs de la question 6 dans l'énoncé de
  la question 7).
- Installation : arbre propre sur `develop`, sauvegarde
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket230-20261027-013750.db`),
  fast-forward `e63a677 → 7e093d6`, seed idempotent (1 UAA créée ; 59 blocs « créés » = 7 blocs
  EX01 + le remplacement habituel des 52 blocs FSE pilotés par le code), redémarrage des deux
  services (actifs), `/health` local et public OK ; sujet, accueil, matrice, PR05, PR06 et les deux
  SVG en HTTP 200 (examen et entraînement : 303 vers la connexion sans session, normal) ; sujet
  servi avec 10 questions et aucun « Corrigé de référence » ; accueil « 1 examens blancs sur 6 ».
  Compteurs utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; correction réelle par l'IA
(les tests utilisent `FakeAIProvider`) ; contrôle visuel de l'impression PDF page par page
(le PDF a été produit par le navigateur sans interface, mais aucun outil n'était disponible
pour l'afficher ; les règles d'impression sont celles décrites plus haut).

## 4. Choix techniques faits seul

- **10 questions de 10 points** (le ticket demande 10 à 14) : 10 est la longueur de session
  standard du moteur ; toutes les questions sont alors tirées, sans mécanisme nouveau, et le
  total vaut exactement 100.
- **Pas d'onglet « S'entraîner »** pour un examen blanc : le ticket ne prévoit pas d'exercices
  propres ; dupliquer les questions dans une réserve d'entraînement aurait dévoilé l'examen.
  On s'entraîne dans PR01 → PR06 (liens « À revoir » du barème global).
- **Sujet = page de l'UAA**, version candidat imprimable : c'est la « version candidat
  imprimable A4 » du ticket ; corrigés et barèmes détaillés n'y figurent jamais (test).
- **Questions autonomes** : le moteur présente les questions dans un ordre variable ; chacune
  reprend donc les documents de son dossier. Conséquence assumée : la question 5 (compte rendu)
  contient le journal d'intervention, qui révèle la solution de la question 4 si on la lit
  avant. Sur la page du sujet, ce journal n'apparaît qu'avant la question 5 ; la question 7
  a été rédigée sans donner les valeurs calculées en question 6.
- **Schémas dans les questions** : les types « réponse longue » n'acceptent pas d'asset
  visuel ; le schéma est donc un **document** de la question (mise en page `figure` ajoutée,
  fichier SVG statique + description textuelle complète, lisible sans l'image et transmise au
  correcteur IA). Pas d'image générée : un plan lettré, des LED et une courbe exacts sont mieux
  servis par un SVG construit sur des données testées.
- **Règles reprises des cours, signalées comme conventions de l'atelier** dans les énoncés :
  bloc = total + 30 %, palier de 50 W, jamais sous la recommandation du fabricant (PR02) ;
  « à surveiller » à moins de 10 °C du maximum de la fiche (PR03/PR04) ; lecture SMART (PR04).
- **Valeurs et références fictives** (LED, manuels, carte graphique, processeur LGA1700
  « 180 W / 100 °C »), présentées comme telles ; le sens des LED de diagnostic est donné par
  l'extrait de manuel du dossier, jamais comme une règle universelle.
- **Position 6** (même position que PR06, créé après lui) pour que EX01 suive PR06 dans la
  navigation et précède PR07 lorsqu'il sera publié.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle).
- Suite de l'ordre pédagogique : PR07 (#207) → … → PR12, puis EX02 (#231), qui peut réutiliser
  le modèle d'examen blanc posé ici (`docs/ampcr_pratique_v1.md`).
- Suggestion (hors périmètre, non implémentée) : permettre de fixer l'ordre des questions d'un
  examen blanc dans le moteur de sessions, pour suivre exactement l'ordre du sujet.

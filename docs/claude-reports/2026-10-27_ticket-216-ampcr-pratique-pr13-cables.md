# Ticket #216 — [AMPCR pratique PR13] Câbles UTP, FTP, STP et coaxial — choix et pose

- Ticket : https://github.com/ReC82/jury-central/issues/216
- **État réel : Installé — à tester**
- SHA installé : `e82cc37561923b4cdb7053dfbbee5ab7447483fd` (fusion de la PR #277 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR13 « Câbles UTP, FTP, STP et coaxial — choix et pose »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de
la théorie MC : son cours, sa banque, son examen et sa progression sont distincts. Le seul lien
vers la théorie renvoie à MC15. PR13 occupe la position 13 de l'ordre pédagogique : après EX02,
avant PR15.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive
de #236), l'emplacement PR13 porte bien le sujet du ticket :
- « PR13, ticket 216, Câbles UTP, FTP, STP et coaxial — choix et pose » ;
- exigences officielles AP-18 et AP-20.

Il n'y a aucun écart. Aucun autre cours n'a été touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres de théorie.** Chacun contient :
- les objectifs et la théorie ;
- la **procédure professionnelle à rédiger** et l'**erreur fréquente** ;
- ce qu'on attend « à l'écrit » et un repère rapide ;
- le renvoi vers les exercices liés.

Les chapitres :
1. **Paire torsadée** : 4 paires et 8 conducteurs, transmission différentielle, rôle de la
   torsade, diaphonie, perturbations électromagnétiques, atténuation, différence entre débit
   et catégorie.
2. **Blindage** :
   - notation X/YTP (ISO/IEC 11801) ;
   - U/UTP, F/UTP, U/FTP et S/FTP, plus SF/UTP, S/UTP et F/FTP ;
   - noms historiques UTP, FTP et STP, avec leurs ambiguïtés.
3. **Blindage efficace** : continuité de l'écran (keystones, panneau et cordons blindés, reprise
   à 360°) et mise à la terre selon le système (baie, barrette de terre, électricien). Un écran
   sans terre est inutile.
4. **Catégories et câble** :
   - catégories 5e, 6 et 6A ;
   - monobrin (/1) ou multibrin (/7) ;
   - câble CCA non conforme ;
   - lecture du marquage d'une gaine.
5. **8P8C, prises, keystones, cordons, baie et panneau de brassage** ; lien permanent et canal.
6. **Coaxial** :
   - âme, diélectrique, tresse et gaine ;
   - 50 Ω ou 75 Ω ;
   - usages : 10BASE2 (RG-58, terminateurs, 185 m), vidéo (RG-59 et BNC 75 Ω), télévision
     (RG-6 et fiches F).
7. **Choisir un câble selon les contraintes** : démarche, règle de choix, tableau comparatif.
8. **Règles de pose** :
   - distances aux câbles d'énergie (EN 50174-2) ;
   - rayon de courbure : 4 × Ø pour un câble non écranté, 8 × Ø pour un câble écranté ;
   - traction : 110 N au plus ;
   - fixation sans agrafe, détorsadage de 13 mm au plus.
9. **Longueurs, repérage et tests** :
   - longueurs : lien permanent de 90 m au plus, cordons de 10 m au plus, canal de 100 m au plus ;
   - même repère aux deux bouts ;
   - tests de réception.

**2 procédures illustrées** : choisir un câble ; poser un câble à paires torsadées.

**5 cas de sélection résolus**, chacun calculé par la règle du cours :
- bureaux calmes → U/UTP ;
- atelier industriel à 10 Gb/s → Cat6A S/FTP ;
- perturbations sans terre → U/UTP ;
- liaison de 150 m → fibre ;
- vidéosurveillance analogique → coaxial 75 Ω.

Viennent ensuite les **pièges**, la **fiche mémo et le glossaire**, puis les **sources et
compléments**.

**17 exercices corrigés** (le ticket en demande au moins 16). Chacun a un contexte complet,
des consignes, un barème et un corrigé :
- **3 remises en ordre** : la pose, le choix, la chaîne de la baie au PC ;
- **5 classements auto-corrigés** :
  - la construction d'après la désignation ;
  - le câble selon les contraintes (9 demandes) ;
  - la conformité de 8 tronçons posés (rayon, traction, distance) ;
  - monobrin ou multibrin ;
  - coaxial 50 Ω ou 75 Ω ;
- **5 exercices sur document** : marquage de gaine, longueurs d'un panneau, écran
  interrompu, rayon dans une goulotte, étiquetage ;
- **4 rédactions** : commande « FTP » ambiguë, comparatif pour une école, coaxial écrasé
  par des agrafes, fiche de pose d'un collègue à corriger.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres), dans l'onglet
« Examen blanc ». Il n'est jamais affiché dans le cours. Les questions :
- 3 choix justifiés : cabinet comptable, menuiserie à 10 Gb/s, deux bâtiments à 160 m ;
- un marquage multibrin ;
- une caméra branchée en RG-58 ;
- un câble posé contre le 230 V ;
- un rayon de courbure trop serré ;
- un lien permanent de 92 m ;
- un écran non raccordé ;
- le repérage et la réception.

**9 schémas SVG** produits depuis des données testées :
- coupes des quatre blindages, dessinées à partir de la désignation ;
- continuité de l'écran (✓/✗) ;
- coupe coaxiale ;
- arbre de choix ;
- 2 procédures ;
- chaîne baie → prise avec les longueurs ;
- distances par classe EN 50174-2 ;
- rayons de courbure à l'échelle.

Chaque schéma a un texte alternatif complet, une légende et la mention « schéma non
officiel ». **Aucune image générée, aucune photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr13_figures.py` — données et règles :
  - `parse_designation`, `structure_of`, `HISTORICAL` ;
  - `Need`/`choose`, `CHOICE_TREE` ;
  - `min_bend_radius_mm`, `SEPARATION_MM`, `Run`/`run_errors`, `channel_errors`, `label_for` ;
  - les figures.
- `app/v1/ampcr_pratique_pr13_bank.py` — 17 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr13_course.py` — les 16 blocs du cours.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR13 et contexte de correction IA propre au
  cours.
- `app/seed.py` — `_seed_uaa(…, "PR13", …, position 13)`, ajout seul.
- `tests/test_ticket216_ampcr_pratique_pr13.py` (26 tests).
- Comptages adaptés dans `tests/test_admin_content_hierarchy.py` et
  `tests/test_ticket215_ampcr_pratique_pr12.py` (nombre de cours publiés).
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr13
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr13/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr13/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :

1. Ouvrir le cours et parcourir les séquences : chapitres 1 à 9, cas résolus, exercices.
2. Lancer une session « S'entraîner » : 10 exercices tirés des 17.
3. Lancer un « Examen blanc » : 10 questions, note sur 20.
4. Après l'envoi, vérifier la correction et le barème.

Dans l'accueil du parcours, PR13 apparaît après EX02 (« 17 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

**Tests ciblés** `tests/test_ticket216_ampcr_pratique_pr13.py` : **26 passed**. Ils couvrent :
- **désignations** : X/YTP et construction de 7 désignations, rejet des désignations invalides ;
- **règle de choix** : chaque branche (service, longueur, perturbations, terre, catégorie) ;
- **rayons, traction, distances** : rayons 4/8/10 × Ø, traction, distances EN 50174-2, cloison ;
- **longueurs et repères** : 90/10/100 m, repères ;
- **procédures** : ordre des étapes ;
- **schémas** : validité, accessibilité, données dessinées (désignation, écrans, barres, rayons,
  chaîne) ;
- **exercices** :
  - remises en ordre et classements auto-corrigés, aucun classement trivial ;
  - aucune question d'acronyme ;
  - liste d'affirmations justes exigées et d'affirmations fausses interdites ;
- **cours** : matière du ticket point par point, 5 cas résolus, 2 procédures, examen absent du
  cours ;
- **liens** : MC15, PR15, PR16 ; aucun lien vers PR14 et PR17, non publiés ;
- **intégration** :
  - seed idempotent et position après EX02, réserves séparées ;
  - contexte de correction, pages ;
  - sessions d'entraînement et d'examen, note /20, aucune génération IA.

**Autres contrôles :**
- **Tests liés** (socle #192, numérotation #236, PR12, EX02, PR15, PR16, hiérarchie admin) avec
  PR13 : **225 passed**.
- **Suite complète** (une exécution, car `seed.py` est partagé) : **2 768 passed** en 22 min, aucun échec.
- **`ruff check`** sur les fichiers créés et modifiés : **All checks passed**.
- **Contrôle visuel** des 9 schémas (navigateur sans interface, 440 px) et de la page du cours
  (1 280 px) : rendu correct. Deux libellés tronqués dans la chaîne baie → prise ont été
  raccourcis.

**Installation :**
- arbre propre sur `develop` ;
- sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket216-20261027-064925.db`) ;
- avance rapide (fast-forward) `825d363 → e82cc37` ;
- seed idempotent : 1 UAA créée et 68 blocs « créés ». Ce sont les 16 blocs de PR13 et le
  remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon ;
- redémarrage des deux services (actifs), `/health` local et public OK ;
- pages du cours, de l'accueil, de la matrice, de PR12, de PR15 et d'EX02 en HTTP 200 ;
  entraînement et examen répondent 303 vers la connexion, ce qui est normal sans session ;
- 17 cartes d'exercice servies ; l'accueil affiche « 17 cours publiés sur 30 prévus » ;
- compteurs utilisateurs / sessions / réponses inchangés (18 / 81 / 638).

**Non effectué :**
- validation pédagogique humaine (au propriétaire) ;
- session réelle avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ;
- vérification sur le texte payant des normes. Les valeurs (TIA-568 : 4/8 × Ø, 110 N,
  90/100 m, 13 mm ; EN 50174-2 : 300/100/50/10 mm sans cloison jusqu'à 3 circuits) viennent
  de sources publiques et sont présentées avec « la fiche du fabricant et les normes en vigueur
  font foi ».

## 4. Choix techniques faits seul

**Périmètre réparti avec les cours voisins :**
- brochage, sertissage et testeurs → **PR15** ;
- fabrication et diagnostic BNC → **PR16** ;
- valeurs chiffrées d'atténuation et d'impédance → **PR14** (non publié, cité en texte) ;
- fibre → **PR17** (non publié, cité en texte).

PR13 traite la **construction**, le **choix** et la **pose**. Les données de PR15 (catégories,
longueurs, chaîne) et de PR16 (familles RG, coupe coaxiale) sont **réutilisées**, pas
recopiées.

**Conventions du cours**, signalées comme telles dans le texte :
- la **règle de choix** : écran seulement si la terre et la continuité sont possibles ; sinon
  U/UTP pour des perturbations moyennes, fibre pour des perturbations fortes ;
- le **rayon de courbure du coaxial** : 10 × Ø quand la fiche du fabricant manque ;
- le **repère** baie-panneau-port (`B1-P1-07`) ;
- l'**usage typique** de chaque blindage.

**Autres décisions :**
- **Catégorie minimale** : Cat5e pour 1 Gb/s, Cat6A pour 10 Gb/s sur 100 m. Une catégorie
  supérieure justifiée est acceptée par le barème et par le contexte de correction.
- **Marquages de gaine fictifs**, construits comme des marquages réels.
- **Exigences** : AP-18 et AP-20 (officielles). Statut « partiel » dans la matrice, jamais
  « validé ».
- **Pas de nouvelle dépendance**. Deux nouveaux types de schéma locaux : coupes de câble et
  barres ou rayons. Les autres réutilisent `step_flow_svg`, `decision_tree_svg`,
  `two_lists_svg`, `chain_svg` (PR15) et `coax_section_svg` (PR16).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR14 « Débits, distances, atténuation et impédance » (#217).
  Une fois PR14 et PR17 publiés, les renvois en texte de PR13 pourront devenir des liens.
- Défaut déjà signalé pour PR02 à PR12, non corrigé ici (hors périmètre) : dans l'arbre de
  décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche. C'est visible
  sur l'arbre de choix de PR13.

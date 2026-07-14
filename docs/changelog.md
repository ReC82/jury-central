# Changelog

Historique des tranches livrées. Format : date, résumé, détail technique bref.

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

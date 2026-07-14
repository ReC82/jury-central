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

---

## Administration

Disponible.

Permet notamment :

- gérer les matières
- gérer les modules
- gérer les UAA
- gérer les blocs de contenu
- importer des quiz

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

---

## Quiz

Disponible.

Les quiz sont intégrés au contenu pédagogique. Question et explication passent par le
renderer de contenu riche (voir plus bas) : un tableau ou une formule dans une question de
quiz s'affiche correctement plutôt qu'en texte brut.

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

Appliqué automatiquement à toute UAA affichée via `/uaa/{slug}` (MB32 UAA1 et UAA2 à ce
jour).

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

- MB32 UAA1
- MB32 UAA2 (Géométrie — 6 leçons : Solides, Perspective cavalière, Patrons, Vues
  coordonnées, Aires, Volumes)

## En attente d'import

- MB32 UAA3
- MQ32
- MQ34

---

# Documentation

La documentation est organisée dans le dossier :

docs/

Chaque document possède une responsabilité unique.

---

# Priorité actuelle

Valider complètement le workflow d'import automatique.

Une fois validé :

1. importer toutes les UAA de mathématiques ;
2. importer les autres matières ;
3. enrichir progressivement le contenu pédagogique.

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

Importer complètement MB32 UAA3 en utilisant exclusivement les sources présentes dans :

docs/sources_cours/
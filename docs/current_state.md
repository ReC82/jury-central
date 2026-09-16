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

- **Moteur IA** (bloc `ai_exercise`, ticket #10 complément IA, voir
  `docs/ai_exercise_engine.md`) : génération à la demande (facile/moyen/difficile) et
  correction structurée via l'API OpenAI, appelée côté serveur uniquement, bornée à un
  contexte pédagogique par cours (`app/ai/context.py`). Complémentaire aux deux moteurs
  ci-dessus, pas un remplacement. Non configuré par défaut.

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

## En attente d'import

- MB32 UAA3, MQ32, MQ34 (derrière Informatique/Français, voir priorité ci-dessous)
- Mini-cours 04 à 38 Informatique AMPCR
- Français CESS Professionnel (aucun contenu à ce jour)

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
Français CESS Professionnel n'a encore aucun contenu. Voir
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
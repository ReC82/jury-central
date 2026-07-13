# Changelog

Historique des tranches livrées. Format : date, résumé, détail technique bref.

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

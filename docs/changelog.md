# Changelog

Historique des tranches livrées. Format : date, résumé, détail technique bref.

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

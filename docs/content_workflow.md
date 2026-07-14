# Ajouter une nouvelle UAA — workflow de contenu

Ce document explique comment ajouter une nouvelle UAA (et son contenu) à Jury Central, en
s'appuyant sur l'exemple réel de **MB32 UAA1 — Tableaux, graphiques, formules** créée dans
`app/seed.py`.

## Rappel de la hiérarchie

```
Subject (matière)  →  Module  →  UAA  →  LessonBlock (bloc de leçon)
```

Chaque niveau a un `slug` unique utilisé dans les URLs publiques
(`/subjects/{slug}`, `/modules/{slug}`, `/uaa/{slug}`). Le slug d'une UAA est généré à
partir du code du module et du code de l'UAA (ex. module `MB32` + UAA `UAA1` →
`mb32-uaa1`), voir `app/slugify.py`.

## Ce que l'admin peut faire aujourd'hui

**Tout, depuis l'interface web** — matières, modules, UAA et blocs de leçon se créent,
modifient et suppriment entièrement depuis `/admin`, sans jamais toucher au code ni relancer
`seed-db`. Voir `docs/admin.md`, section "Gérer la hiérarchie de contenu", pour le détail
précis des formulaires et de la validation.

Ça n'a pas toujours été le cas : jusqu'à l'introduction de cette gestion complète, seule la
création de `LessonBlock` était possible depuis l'admin, et créer une matière/module/UAA
nécessitait de modifier `app/seed.py`. Ce n'est plus nécessaire.

## Créer une nouvelle UAA (ex. MB32 UAA2) — étape par étape, sans toucher au code

1. Se connecter à `/admin/login`.
2. `/admin/subjects` → ouvrir la matière (ex. Mathématiques) — ou "+ Nouvelle matière" si
   elle n'existe pas encore.
3. Sur la page de la matière → ouvrir le module (ex. MB32) — ou "+ Nouveau module" si
   nécessaire.
4. Sur la page du module → "+ Nouvelle UAA" → code, titre, slug (laisser vide pour le
   générer automatiquement, ex. `mb32-uaa2`), position, et cocher "Publiée" quand elle est
   prête à être vue par les étudiants (la laisser décochée pendant la préparation du
   contenu : la page restera en 404 côté public jusqu'à publication).
5. L'UAA créée apparaît immédiatement dans `/admin/uaa/{id}` pour y ajouter ses blocs de
   contenu (voir section suivante), exactement comme pour une UAA créée par le seed.

## Structurer le contenu d'une UAA (blocs de leçon)

1. **Développer une leçon à la fois (tranche verticale), pas toute l'UAA d'un coup.** Deux
   états possibles pour une section :

   **a) Placeholder** (section pas encore développée) : **1 bloc markdown, non publié**,
   listant les notions couvertes + une checklist (`- [ ] Théorie`, `- [ ] Exemples`,
   `- [ ] Exercices`, `- [ ] Quiz`). Voir les sections 1, 3-8 d'UAA1 dans `app/seed.py` pour
   des exemples actuels.

   **b) Leçon complète** (tranche verticale terminée) : une **séquence de plusieurs blocs
   publiés**, un par type de contenu. Pattern utilisé pour "Fonction constante" (voir
   `_CONSTANT_FUNCTION_*` dans `app/seed.py`) :

   | Bloc | Type | Contenu |
   |---|---|---|
   | Présentation et objectifs | `markdown` | Définition rapide, objectifs, prérequis |
   | Cours | `markdown` | Théorie, MathJax, "À retenir", "Erreurs fréquentes" |
   | Graphique interactif | `markdown` | Marqueur `<div class="jc-graph-constant">` (voir `docs/admin.md`) |
   | Exemples résolus | `markdown` | Au moins 5 exemples avec solution |
   | Exercice guidé | `markdown` | Énoncé + correction détaillée pas à pas |
   | Exercices automatiques | `generated_exercise` | Générateur dédié, exercices "infinis" |
   | Quiz | `quiz` × N | Voir "Regrouper un quiz de plusieurs questions" ci-dessous |
   | Fiche mémo | `markdown` | Synthèse imprimable (voir `docs/admin.md`) |

   Il n'y a pas de sous-type "théorie" ou "exemple" dans `LessonBlock` — chaque ligne du
   tableau ci-dessus reste un `markdown` (ou `generated_exercise`/`quiz`) ordinaire ; c'est
   uniquement le **titre du bloc** et l'ordre des `position` qui donnent la structure.

   **1 bloc "Plan de l'UAA"** en tête de l'UAA (markdown, toujours publié) sert de sommaire
   général listant toutes les sections, complètes ou non.

2. **Regrouper un quiz de plusieurs questions en un seul parcours.** Créer un bloc `quiz`
   par question (comme d'habitude, un `LessonBlock` = une question, depuis
   `/admin/uaa/{id}/blocks/new`), mais donner la **même valeur non vide au champ « Groupe de
   quiz »** sur tous les blocs concernés, avec un « Ordre dans le groupe » croissant
   (1, 2, 3...). Le rendu public (`app/main.py::uaa_detail`) détecte les blocs `quiz`
   consécutifs partageant un groupe et les fusionne en un seul widget "parcours" (une
   question à la fois, score, recommencer) au lieu de N widgets QCM isolés. Voir
   `_CONSTANT_FUNCTION_QUIZ_QUESTIONS` dans `app/seed.py` pour un exemple à 10 questions
   mêlant QCM, vrai/faux et réponses numériques. Laisser le groupe vide garde le
   comportement par défaut (un quiz autonome par bloc).

3. **Publier au fur et à mesure** : chaque bloc a sa propre case "Publié"
   (`/admin/uaa/{id}` → Modifier) — rédiger et tester un bloc avant de le publier, puis
   cocher "Publié" quand il est prêt. Aucun rechargement de code ni de base nécessaire.

## Rôle de `app/seed.py` maintenant que l'admin gère tout

`seed-db` reste utile, mais pour un usage différent de la création de contenu au quotidien :

- **initialiser une base de développement vide** (nouveau clone du dépôt, GitHub Codespaces) ;
- **fournir des données de démonstration reproductibles** pour les tests manuels et le
  développement (la matière Mathématiques, MB32/MQ32/MQ34, et la leçon "Fonction constante"
  complète) ;
- **servir de fixture pour les tests automatisés** (`tests/test_admin_content_hierarchy.py`
  appelle directement `seed()` contre une base de test isolée).

`seed-db` **n'est pas** un outil de création de contenu réel : passe par l'admin pour ça.
`seed()` est strictement additif et idempotent — il ne modifie ni ne supprime jamais un
contenu déjà créé ou édité depuis l'admin (voir `docs/development.md` pour le détail exact
de cette garantie et ses tests). Une exception ponctuelle et documentée existe
(`OBSOLETE_DEMO_BLOCK_TITLES` dans `app/seed.py`), réservée à la migration ponctuelle
d'anciens blocs de démonstration désormais obsolètes — pas un mécanisme à réutiliser pour
du contenu réel.

Pour repartir d'une base strictement vide (efface tout, y compris le contenu créé depuis
l'admin) : `reset-db`, une commande **distincte et explicite**, jamais déclenchée
automatiquement — voir `docs/development.md`.

## Rappel : pas de migration de schéma

`app/seed.py` ne fait que des `INSERT`/`UPDATE` de données, pas de changement de schéma.
Si un jour un nouveau **type** de bloc ou un nouveau **champ** est nécessaire (schéma
modifié dans `app/models.py` — c'était le cas pour `UAA.position` et `UAA.is_published`,
ajoutés pour la gestion admin de la hiérarchie), il faut supprimer `jury_central.db` en
local (ou lancer `reset-db`) — voir `docs/development.md`.

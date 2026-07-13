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

## Ce que l'admin peut faire aujourd'hui, et ce qu'il ne peut pas

- **Créer/modifier/supprimer une matière, un module ou une UAA : pas possible depuis
  l'admin** (voir `docs/admin.md`, section Limites connues). C'est une limite connue,
  pas un oubli de ce document.
- **Créer/modifier/supprimer les blocs de leçon (`LessonBlock`) d'une UAA existante : oui**,
  entièrement depuis `/admin/uaa/{id}` une fois l'UAA créée (titre, type, contenu, position,
  publié — voir `docs/admin.md`).

Conséquence pratique : la création d'une UAA se fait aujourd'hui **par script Python**
(`app/seed.py`), pas depuis l'interface web. Une fois l'UAA créée, tout son contenu se
gère normalement depuis l'admin.

## Ajouter une nouvelle UAA — étape par étape

1. **Vérifier si la matière/module existent déjà** dans `app/seed.py` (`SUBJECT_NAME`,
   `MODULE_CODES`). S'ils n'existent pas encore, les ajouter suit le même principe que pour
   l'UAA (voir le bloc `seed()` : `Subject(...)`, `Module(...)`, créés seulement s'ils
   n'existent pas déjà, avec un `slug` généré via `slugify()`).

2. **Créer l'UAA** avec son code, son titre et son slug :

   ```python
   uaa = next((u for u in module.uaas if u.code == "UAA2"), None)
   if uaa is None:
       uaa = UAA(
           code="UAA2",
           title="Titre de la nouvelle UAA",
           slug=slugify(f"{module.code}-UAA2"),
           module=module,
       )
       db.add(uaa)
       db.flush()
   ```

3. **Développer une leçon à la fois (tranche verticale), pas toute l'UAA d'un coup.** Deux
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

4. **Regrouper un quiz de plusieurs questions en un seul parcours.** Créer un bloc `quiz`
   par question (comme d'habitude, un `LessonBlock` = une question), mais donner la **même
   valeur non vide au champ `group`** de `QuizConfig` sur tous les blocs concernés, avec un
   `order_in_group` croissant (1, 2, 3...). Le rendu public (`app/main.py::uaa_detail`)
   détecte les blocs `quiz` consécutifs partageant un `group` et les fusionne en un seul
   widget "parcours" (une question à la fois, score, recommencer) au lieu de N widgets QCM
   isolés. Voir `_CONSTANT_FUNCTION_QUIZ_QUESTIONS` dans `app/seed.py` pour un exemple à 10
   questions mêlant QCM, vrai/faux et réponses numériques (`answer_type="numeric"`).
   Laisser `group` vide garde le comportement historique (un quiz autonome par bloc).

5. **Lancer le seed** :

   ```bash
   seed-db
   # ou : python -m app.seed
   ```

   `seed()` est additif et idempotent par défaut (ne recrée pas ce qui existe déjà, se
   base sur le `code` pour les matières/modules/UAA et sur le `title` pour les blocs).
   Aucune suppression de base nécessaire pour ajouter du contenu nouveau.

   Cas particulier : remplacer un ensemble de blocs existants (comme lors du remplacement
   des blocs de démonstration d'UAA1 par sa vraie structure) demande une étape de nettoyage
   explicite dans `seed()` — voir `OBSOLETE_DEMO_BLOCK_TITLES` dans `app/seed.py` pour
   l'exemple : les anciens blocs sont supprimés par leur titre avant l'insertion des
   nouveaux, pour ne pas mélanger ancien et nouveau contenu.

6. **Compléter le contenu progressivement depuis l'admin** : une fois l'UAA et ses blocs
   squelettes créés par le seed, un enseignant/créateur de contenu peut modifier chaque
   bloc (`/admin/uaa/{id}` → Modifier), rédiger la théorie, ajouter des exemples, configurer
   les exercices générés, écrire les quiz, puis cocher "Publié" section par section quand
   c'est prêt — sans avoir besoin de relancer le seed ni de toucher au code.

## Rappel : pas de migration de schéma

`app/seed.py` ne fait que des `INSERT`/`UPDATE` de données, pas de changement de schéma.
Si un jour un nouveau **type** de bloc ou un nouveau **champ** est nécessaire (schéma
modifié dans `app/models.py`), il faudra supprimer `jury_central.db` en local et relancer
`seed-db` — voir `docs/development.md`. Ce n'était pas nécessaire pour créer UAA1 : aucun
changement de modèle, seulement de nouvelles lignes de données.

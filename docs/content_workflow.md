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

3. **Structurer le contenu en petites sections**, pas tout le cours d'un coup. Pattern
   recommandé, utilisé pour UAA1 (voir `UAA1_BLOCKS` dans `app/seed.py`) :

   - **1 bloc "Plan de l'UAA"** (markdown, **publié**) : présente l'UAA et liste les
     sections à venir — un sommaire visible même avant que le contenu soit écrit.
   - **1 bloc markdown par section pédagogique** (regroupant plusieurs notions proches),
     **non publié** tant que le contenu réel n'est pas rédigé. Contenu = liste des notions
     couvertes + checklist de ce qui reste à faire (`- [ ] Théorie`, `- [ ] Exemples`,
     `- [ ] Exercices`, `- [ ] Quiz`). Ce n'est pas une convention imposée par le code
     (`LessonBlock` n'a pas de sous-type "section" ou "théorie" séparé) — c'est un choix
     éditorial : chaque section reste un bloc `markdown` unique, complété petit à petit.
   - **Au moins un exemple concret par type de contenu interactif disponible** (pour vérifier
     que le mécanisme fonctionne, sans écrire tout le cours) :
     - un bloc `generated_exercise` pointant vers un générateur déjà enregistré (voir
       `docs/exercise_generators.md`) ;
     - un bloc `quiz` avec une question de démonstration.
     Les deux marqués **non publiés** tant qu'ils ne sont pas prêts pour de vrai.
   - **1 bloc "Fiche mémo"** en fin d'UAA (markdown, non publié), réservé à la synthèse
     finale une fois les sections complétées.

   Chaque section obtient une **position** croissante (ordre d'affichage). Le bloc
   `is_published: False` garde le contenu invisible sur la page publique tant qu'il n'est
   pas prêt, sans empêcher de le préparer et de le tester dans l'admin.

4. **Lancer le seed** :

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

5. **Compléter le contenu progressivement depuis l'admin** : une fois l'UAA et ses blocs
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

# Générateurs automatiques d'exercices

## Principe

Pour les mathématiques, certaines notions ne nécessitent pas de banque de questions figées :
un exercice peut être **généré à la demande**, avec un résultat calculé par Python (pas écrit
à l'avance, pas d'IA). C'est le rôle du package `generators/`.

Exemples de notions concernées : équations, fonctions du premier degré, tableaux de valeurs,
intersections, puissances, intérêts, proportionnalité inverse. **Un seul générateur est
implémenté à ce jour** (équations du premier degré) — cette page documente l'architecture,
pas un inventaire de générateurs à venir.

## Où vit ce code, et pourquoi

```
generators/                  # package racine, indépendant de app/ et de FastAPI
├── base.py                    # dataclass GeneratedExercise + interface ExerciseGenerator
├── registry.py                  # registre id → fonction generate()
└── maths/
    └── equations.py              # premier générateur : équations ax + b = c
```

`generators/` est **à la racine du projet, pas sous `app/`**. C'est volontaire : ces
générateurs ne dépendent d'aucun module `app.*` (pas de FastAPI, pas de SQLAlchemy). Ils
pourraient être publiés comme package Python autonome, réutilisés par un script, un futur
CLI, ou une autre application, sans rien importer du framework web. `app/` (routes,
templates, base de données) est le *consommateur* de `generators/`, pas l'inverse — voir
`app/exercise_blocks.py` pour le pont entre les deux.

Cette architecture existait déjà avant cette étape (mise en place pour le premier générateur
d'équations). Elle remplit exactement ce qui était demandé : dataclass d'exercice, interface
commune, registre. Un doublon a été envisagé sous `app/exercises/` mais écarté pour éviter
deux systèmes parallèles à maintenir — un seul générateur enregistré, une seule source de
vérité.

## `GeneratedExercise` (le dataclass "Exercise")

Défini dans `generators/base.py` :

```python
@dataclass
class GeneratedExercise:
    statement: str                              # énoncé affiché à l'étudiant
    answer: Any                                  # réponse attendue (type libre : Fraction, int, str...)
    difficulty: int                              # niveau demandé au générateur
    seed: int                                    # seed effectivement utilisé (pour rejouer l'exercice)
    solution_steps: list[str] = field(...)       # étapes de correction, affichées à la demande
    metadata: dict[str, Any] = field(...)        # données internes utiles au debug/tests (ex. coefficients)
```

`answer` est volontairement typé `Any` : chaque générateur choisit le type le plus adapté
(`Fraction` pour un résultat exact, `int`, `str`...). Le consommateur (page publique,
vérification de réponse) est responsable de l'interpréter.

## Interface commune

Chaque générateur est une fonction — pas besoin d'une classe/héritage — respectant :

```python
def generate(difficulty: int, seed: int | None = None) -> GeneratedExercise:
    ...
```

Formalisée par un `Protocol` (typing structurel, pas d'héritage obligatoire) :

```python
class ExerciseGenerator(Protocol):
    def __call__(self, difficulty: int, seed: int | None = None) -> GeneratedExercise: ...
```

Règles à respecter par tout nouveau générateur :

- **Déterministe si un seed est fourni** : deux appels avec le même `(difficulty, seed)`
  doivent produire exactement le même énoncé et la même réponse. Si `seed=None`, le
  générateur choisit lui-même un seed aléatoire et **le renvoie** dans
  `GeneratedExercise.seed` (voir `generators/maths/equations.py`) — ça permet de rejouer
  n'importe quel exercice généré aléatoirement.
- **Résultat calculé, jamais écrit en dur** : utiliser du calcul Python (arithmétique,
  `random.Random(seed)`, SymPy si utile pour résoudre/vérifier — voir le générateur
  d'équations). Ne jamais coder une réponse en clair dans le générateur.
- **Éviter les cas ambigus** propres à la notion (ex. pour une équation : coefficient nul,
  équation impossible ou identité — voir les commentaires de
  `generators/maths/equations.py` pour un exemple concret de garde-fous).
- **Aucune IA** : génération procédurale uniquement.

## Le registre

`generators/registry.py` associe un identifiant texte à chaque fonction `generate` :

```python
REGISTRY: dict[str, ExerciseGenerator] = {
    "maths.equations.linear_equation": equations.generate,
}
```

Convention d'id : `domaine.module.nom` (ex. `maths.equations.linear_equation`). Deux
fonctions d'accès :

- `get_generator(generator_id: str) -> ExerciseGenerator` — lève `KeyError` si l'id est
  inconnu.
- `available_generators() -> list[str]` — liste triée de tous les id enregistrés. Utilisée
  par le panneau admin (choix du générateur pour un bloc `generated_exercise`) et par la
  page de debug (voir plus bas).

## Ajouter un nouveau générateur

Étapes (illustrées avec un générateur hypothétique de tableau de valeurs — non implémenté
ici, exemple uniquement) :

1. Créer le module, ex. `generators/maths/value_tables.py`, avec une fonction
   `generate(difficulty: int, seed: int | None = None) -> GeneratedExercise`.
2. L'enregistrer dans `generators/registry.py` :
   ```python
   from generators.maths import value_tables

   REGISTRY = {
       "maths.equations.linear_equation": equations.generate,
       "maths.functions.value_table": value_tables.generate,
   }
   ```
3. Ajouter des tests dans `tests/generators/` (voir `test_equations.py` pour un exemple
   complet). `tests/generators/test_architecture.py` valide **automatiquement** tout nouveau
   générateur enregistré (type de retour, déterminisme avec seed, format de l'id) — aucun
   test de contrat à réécrire.
4. C'est tout : le générateur devient immédiatement sélectionnable dans le panneau admin
   (`/admin/generators` pour le tester, et le formulaire de bloc `generated_exercise` pour
   l'utiliser sur une UAA) sans autre modification.

## Tester un générateur (page de debug admin)

`/admin/generators` (lien "Tester un générateur" depuis le tableau de bord) : formulaire
simple (générateur, difficulté, seed optionnel) qui appelle directement
`get_generator(id)(difficulty, seed)` et affiche le résultat brut — énoncé, réponse,
étapes de correction, métadonnées, et le seed effectivement utilisé (pour le rejouer à
l'identique). Pensé pour un créateur de contenu qui veut prévisualiser ce qu'un générateur
produit avant de configurer un bloc, ou pour déboguer un générateur en cours de
développement.

Existe aussi : `GET /practice/api/generate?generator=<id>&difficulty=<n>` — API JSON publique
équivalente, utilisée par le bouton "Nouvel exercice" des blocs `generated_exercise` (voir
`app/practice.py`).

## Où c'est consommé dans `app/`

- `app/exercise_blocks.py` — `ExerciseBlockConfig` (générateur + difficulté + nombre
  d'exercices + tags), stocké en JSON dans `LessonBlock.content` pour le type de bloc
  `generated_exercise`. `generate_exercises()` appelle le registre `count` fois.
- `app/main.py` — route `/uaa/{slug}` : génère les exercices à la volée pour chaque bloc
  `generated_exercise` publié.
- `app/practice.py` — page `/practice/equations` (entraînement libre) et l'API JSON de
  régénération.
- `app/admin.py` — formulaire de bloc (sélection du générateur) et page de debug
  `/admin/generators`.

## Lancer les tests

```bash
pytest tests/generators/
```

14 tests actuellement : 8 spécifiques au générateur d'équations
(`test_equations.py`), 3 sur le registre (`test_registry.py`), 3 de contrat d'architecture
(`test_architecture.py`, appliqués automatiquement à chaque générateur enregistré).

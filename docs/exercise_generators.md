# Générateurs automatiques d'exercices

## Principe

Pour les mathématiques, certaines notions ne nécessitent pas de banque de questions figées :
un exercice peut être **généré à la demande**, avec un résultat calculé par Python (pas écrit
à l'avance, pas d'IA). C'est le rôle du package `generators/`.

Exemples de notions concernées : équations, fonctions du premier degré, tableaux de valeurs,
intersections, puissances, intérêts, proportionnalité inverse. **Deux générateurs sont
implémentés à ce jour** (équations du premier degré, fonction constante) — cette page
documente l'architecture, pas un inventaire complet des générateurs à venir.

## Où vit ce code, et pourquoi

```
generators/                  # package racine, indépendant de app/ et de FastAPI
├── base.py                    # dataclass GeneratedExercise + interface ExerciseGenerator
├── registry.py                  # registre id → fonction generate()
└── maths/
    ├── equations.py              # équations ax + b = c
    └── constant_function.py       # fonction constante f(x) = p (4 formulations, 3 niveaux)
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
    hint: str = ""                               # indice optionnel, ne révèle pas la réponse
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

## Validation des réponses : jamais côté client

Depuis la leçon "Fonction constante" (MB32 UAA1), la réponse n'est **plus jamais** envoyée
au navigateur avant que l'étudiant ait répondu. Trois routes publiques dans `app/practice.py` :

- `GET /practice/api/generate?generator=<id>&difficulty=<n>` — renvoie uniquement
  `{statement, seed, hint}` (via `exercise_to_public_dict()` dans `app/exercise_blocks.py`).
  Utilisée pour l'affichage initial et le bouton "Nouvel exercice".
- `POST /practice/api/verify` — reçoit `{generator, difficulty, seed, answer}`, **régénère**
  l'exercice à partir du même seed côté serveur, compare via
  `app/answer_checking.py::answers_match` (parsing entier/décimal virgule-point/fraction,
  comparaison exacte via `Fraction`, jamais d'`eval()`), renvoie `{correct: bool}` — jamais
  la réponse.
- `POST /practice/api/reveal` — même principe, renvoie `solution_steps` + `answer_display`,
  appelée uniquement au clic explicite sur "Afficher la correction".

`exercise_to_dict()` (avec la réponse complète) reste utilisé **uniquement** par
`/admin/generators`, un outil de debug authentifié — jamais par une route publique.

## Où c'est consommé dans `app/`

- `app/exercise_blocks.py` — `ExerciseBlockConfig` (générateur + difficulté + nombre
  d'exercices + tags), stocké en JSON dans `LessonBlock.content` pour le type de bloc
  `generated_exercise`. `generate_exercises()` appelle le registre `count` fois et renvoie
  des dicts publics (sans réponse).
- `app/main.py` — route `/uaa/{slug}` : génère les exercices à la volée pour chaque bloc
  `generated_exercise` publié.
- `app/practice.py` — page `/practice/equations` (entraînement libre) et les 3 routes API
  ci-dessus (génération/vérification/correction).
- `app/admin.py` — formulaire de bloc (sélection du générateur) et page de debug
  `/admin/generators`.

## Lancer les tests

```bash
pytest tests/generators/
pytest tests/test_answer_checking.py
```

28 tests dans `tests/generators/` : 10 pour le générateur d'équations
(`test_equations.py`), 10 pour la fonction constante (`test_constant_function.py`), 3 sur le
registre (`test_registry.py`), 6 de contrat d'architecture (`test_architecture.py`, 3 règles
× 2 générateurs enregistrés — automatique pour tout nouveau générateur). Plus 11 tests pour
`app/answer_checking.py` (parsing et comparaison, hors du dossier `generators/` puisque
c'est un module `app/`, pas un générateur).

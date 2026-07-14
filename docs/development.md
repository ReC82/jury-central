# Environnement de développement — Jury Central

## Mise en place

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS

pip install -e ".[dev]"
cp .env.example .env        # puis éditer ADMIN_USERNAME / ADMIN_PASSWORD / SECRET_KEY
```

## Lancer l'application

```bash
seed-db                          # charge les données de démonstration (idempotent)
uvicorn app.main:app --reload    # http://127.0.0.1:8000
```

Le schéma SQLite (`jury_central.db`, à la racine, non versionné) est créé automatiquement
au démarrage via `Base.metadata.create_all()` (voir `app/main.py` et `app/seed.py`). **Il
n'y a pas de système de migration (pas d'Alembic)** : toute modification d'un modèle
existant (ajout/renommage de colonne) nécessite de supprimer `jury_central.db` en local (ou
`reset-db`, voir plus bas), sous peine d'incohérence entre le modèle Python et le fichier
SQLite déjà créé.

### Réinitialiser la base locale

```bash
reset-db      # supprime jury_central.db puis relance seed()
```

Commande **distincte et explicite** de `seed-db` — `seed()` seul ne supprime jamais rien.
`reset-db` est destructif (efface tout contenu, y compris ce qui a été créé/édité depuis
l'admin) et n'est **jamais** déclenché automatiquement (ni au démarrage de l'app, ni par
`seed()`). Voir `app/seed.py::reset()`.

### `DATABASE_URL` (configurable)

`app/database.py` lit la variable d'environnement `DATABASE_URL` si elle est définie, sinon
retombe sur `sqlite:///<racine du projet>/jury_central.db` (comportement historique,
inchangé par défaut). Utilisé principalement par `tests/conftest.py` pour pointer les tests
vers un fichier SQLite temporaire, séparé de la base de développement réelle.

## Lancer les tests

```bash
pytest
```

87 tests actuellement, tous dans `tests/` :
- `tests/generators/` — le moteur de génération d'exercices (`generators/`), 28 tests.
- `tests/test_answer_checking.py` — parsing/comparaison normalisée des réponses, 11 tests.
- `tests/test_exercise_blocks.py` — sérialisation JSON + séparation public/complet, 7 tests.
- `tests/test_quiz.py` — sérialisation JSON, modes choix/numérique, `to_public_dict`, 8 tests.
- `tests/test_quiz_import.py` — import CSV de quiz, 16 tests.
- `tests/test_admin_content_hierarchy.py` — CRUD matière/module/UAA via `TestClient`,
  protections admin, suppression en cascade, publication, idempotence et non-régression du
  seed, 17 tests.

### Base de test isolée (`tests/conftest.py`)

`tests/test_admin_content_hierarchy.py` est le premier ensemble de tests à utiliser
`fastapi.testclient.TestClient` (requêtes HTTP réelles contre l'application, sans lancer de
serveur). **Ne touche jamais `jury_central.db`** : `conftest.py` fixe `DATABASE_URL` sur un
fichier SQLite temporaire *avant* le premier import de `app.database`/`app.main`, donc
l'engine applicatif entier (y compris `Base.metadata.create_all()` exécuté au chargement de
`app.main`) est déjà lié à ce fichier de test dès le départ.

Fixtures disponibles :
- `client` — `TestClient` connecté à la base de test, tables recréées à neuf avant chaque
  test qui l'utilise.
- `admin_client` — `client`, déjà authentifié (identifiants `test-admin` / `test-password`,
  indépendants de `.env`).
- `db_session` — session SQLAlchemy directe sur la base de test, pour préparer des
  données ou vérifier un état sans passer par HTTP.

Piège classique en écrivant un nouveau test : après une action HTTP qui modifie la base
(passée par la session de la requête, pas celle du test), appeler
`db_session.expire_all()` avant de relire un objet déjà chargé dans `db_session`, sinon
SQLAlchemy renvoie la version encore en cache plutôt que l'état réel en base.

## Lint

```bash
ruff check .
```

Configuration dans `pyproject.toml` (`[tool.ruff]`), ligne à 100 caractères, cible Python 3.12.

## Conventions du projet

- **Stockage polymorphe** : `LessonBlock.content` est un champ texte libre dont le sens
  dépend de `LessonBlock.type`. Pour les types `generated_exercise` et `quiz`, c'est du JSON
  sérialisé via un dataclass dédié (`app/exercise_blocks.py::ExerciseBlockConfig`,
  `app/quiz.py::QuizConfig`) avec des méthodes `to_json()` / `from_json()`. Ce choix évite
  une migration de schéma à chaque nouveau type de bloc, au prix d'une validation qui se
  fait au niveau applicatif plutôt qu'au niveau base de données.
- **Générateurs d'exercices indépendants** : le package `generators/` (racine du projet, pas
  sous `app/`) ne dépend d'aucun module `app.*`. Chaque générateur expose une fonction
  `generate(difficulty: int, seed: int | None = None) -> GeneratedExercise` (interface
  définie dans `generators/base.py`) et s'enregistre dans `generators/registry.py` sous un
  id du type `domaine.module.nom` (ex. `maths.equations.linear_equation`). Aucune IA n'est
  utilisée : génération procédurale (Python + `random`) et vérification symbolique via
  SymPy.
- **JavaScript vanilla uniquement** : pas de framework front, pas de build step, pas de
  dépendance npm. Chaque fonctionnalité interactive a son propre fichier sous
  `app/static/js/` (`exercise.js`, `quiz.js`, `progress.js`), inclus globalement dans
  `base.html`.
- **Progression étudiant** : entièrement côté client (`localStorage`, clé
  `jury-central-progress`), aucune table ni route serveur associée — voulu tant qu'il n'y a
  pas de comptes étudiants.
- **Slugs** : générés via `app/slugify.py` (accents retirés, minuscules, tirets), utilisés
  comme clés d'URL publiques pour `Subject`, `Module`, `UAA`. Les routes admin utilisent les
  `id` numériques, pas les slugs.
- **Style des routes admin** : un unique routeur public (`/admin/login`) et un unique
  routeur protégé (`dependencies=[Depends(require_admin)]` posé au niveau du routeur, pas
  route par route) — voir `app/admin.py`.
- **Validation des réponses toujours côté serveur** : depuis la leçon "Fonction constante",
  aucune route publique n'envoie plus jamais une réponse correcte au navigateur avant que
  l'étudiant ait répondu (voir `docs/exercise_generators.md`, section "Validation des
  réponses"). `app/answer_checking.py` centralise le parsing (entier/décimal/fraction) et la
  comparaison, réutilisé par les exercices générés et les quiz — jamais d'`eval()`.
- **Graphiques interactifs via Plotly (CDN)** : pas de dépendance Python, un seul `<script>`
  chargé uniquement sur les pages qui en ont besoin (voir `needs_plotly` dans
  `app/main.py::uaa_detail`), suivant le même principe que MathJax/Bootstrap. Un contenu
  Markdown active un graphique en y collant un marqueur HTML (`<div class="jc-graph-...">`) —
  voir `docs/admin.md`.
- **`seed()` n'écrase jamais un contenu édité depuis l'admin** : additif et idempotent par
  construction (vérifie l'existence par `code`/`name` avant de créer une matière/module/UAA,
  par `title` avant de créer un bloc — ne touche jamais un objet déjà existant, sauf la
  création initiale). Voir `tests/test_admin_content_hierarchy.py::test_seed_does_not_...`
  pour la garantie testée. Seule exception ponctuelle : `OBSOLETE_DEMO_BLOCK_TITLES`, une
  migration de contenu de démonstration désormais obsolète, pas un mécanisme général.

## Commandes utiles

```bash
# Réinitialiser la base locale (équivalent à reset-db)
rm jury_central.db && seed-db

# Lancer un serveur sur un port différent (utile pour tester en parallèle)
uvicorn app.main:app --port 8001

# Inspecter le contenu d'un bloc généré/quiz stocké en base (JSON dans content)
python -c "from app.database import SessionLocal; from app.models import LessonBlock; \
db = SessionLocal(); [print(b.id, b.type, b.content) for b in db.query(LessonBlock).all()]"
```

## Ce qui n'est pas encore fait (hors périmètre de cette étape)

- Docker (explicitement hors périmètre pour l'instant).
- Migrations de schéma (Alembic ou équivalent) — toujours `rm jury_central.db && seed-db` /
  `reset-db` en local à chaque changement de modèle.
- Comptes étudiants / scoring global.
- Réorganisation par glisser-déposer (position saisie manuellement, voir `docs/admin.md`).
- Protection CSRF sur les formulaires admin.

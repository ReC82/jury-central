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
existant (ajout/renommage de colonne) nécessite de supprimer `jury_central.db` en local et
de relancer `seed-db`, sous peine d'incohérence entre le modèle Python et le fichier SQLite
déjà créé.

## Lancer les tests

```bash
pytest
```

19 tests actuellement, tous dans `tests/` :
- `tests/generators/` — le moteur de génération d'exercices (`generators/`), 11 tests.
- `tests/test_exercise_blocks.py` — sérialisation JSON des blocs `generated_exercise`, 5 tests.
- `tests/test_quiz.py` — sérialisation JSON des blocs `quiz`, 3 tests.

Aucun test automatisé ne couvre encore les routes FastAPI elles-mêmes (pas de `TestClient`)
— les routes ont été vérifiées manuellement (curl) à chaque étape de développement.

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

## Commandes utiles

```bash
# Réinitialiser la base locale
rm jury_central.db && seed-db

# Lancer un serveur sur un port différent (utile pour tester en parallèle)
uvicorn app.main:app --port 8001

# Inspecter le contenu d'un bloc généré/quiz stocké en base (JSON dans content)
python -c "from app.database import SessionLocal; from app.models import LessonBlock; \
db = SessionLocal(); [print(b.id, b.type, b.content) for b in db.query(LessonBlock).all()]"
```

## Ce qui n'est pas encore fait (hors périmètre de cette étape)

- Docker (explicitement hors périmètre pour l'instant).
- Migrations de schéma (Alembic ou équivalent).
- Comptes étudiants / scoring global.
- Gestion des matières/modules/UAA depuis l'admin (actuellement : script `seed.py` uniquement).
- Tests automatisés sur les routes FastAPI (`TestClient`).

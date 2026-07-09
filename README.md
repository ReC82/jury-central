# Jury Central

Plateforme pédagogique construite avec Python et FastAPI : contenu de cours organisé en
Matières → Modules → UAA → Blocs de leçon, panneau d'administration, exercices générés
automatiquement en Python, quiz interactifs et suivi de progression local (navigateur).

## Statut

En développement actif. Étapes 1 à 9 du plan initial terminées (voir
[docs/current_state.md](docs/current_state.md) pour le détail complet). Docker n'est pas
encore utilisé dans ce projet.

## Stack technique

- **Langage** : Python 3.12+
- **Framework web** : [FastAPI](https://fastapi.tiangolo.com/) + [Starlette](https://www.starlette.io/) (sessions)
- **Templates** : Jinja2 + [Bootstrap 5](https://getbootstrap.com/) (CDN) + [MathJax 3](https://www.mathjax.org/) (CDN)
- **Base de données** : SQLAlchemy 2.0 (style déclaratif `Mapped`) + SQLite (fichier local, pas de migrations Alembic)
- **Génération d'exercices** : [SymPy](https://www.sympy.org/) pour la résolution/vérification, générateurs 100 % Python (pas d'IA)
- **JavaScript** : vanilla JS uniquement (aucun framework, aucune dépendance npm)
- **Tests** : pytest (19 tests, tous dans `tests/`)

## Structure du projet

```
jury-central/
├── app/                    # Application FastAPI
│   ├── main.py              # Point d'entrée + routes publiques (accueil, matières, modules, UAA)
│   ├── admin.py              # Panneau admin (auth + CRUD des blocs de leçon)
│   ├── auth.py                # Vérification des identifiants + dépendance require_admin
│   ├── config.py               # Settings (pydantic-settings, lit .env)
│   ├── database.py              # Engine SQLAlchemy / SessionLocal / Base / get_db
│   ├── models.py                 # Modèles : Subject, Module, UAA, LessonBlock
│   ├── practice.py                # Page d'entraînement libre + API JSON de génération
│   ├── exercise_blocks.py          # Config JSON des blocs "generated_exercise"
│   ├── quiz.py                      # Config JSON des blocs "quiz"
│   ├── content.py                    # Rendu Markdown + extraction d'ID YouTube
│   ├── slugify.py                     # Génération de slugs (accents retirés, etc.)
│   ├── templating.py                   # Instance Jinja2Templates partagée
│   ├── seed.py                          # Script de données de démonstration
│   ├── templates/                        # Templates Jinja2 (voir docs/current_state.md)
│   └── static/{css,js}/                   # CSS custom + JS vanilla (exercise.js, quiz.js, progress.js)
├── generators/               # Moteur de génération d'exercices — indépendant de FastAPI
│   ├── base.py                 # GeneratedExercise (dataclass) + interface ExerciseGenerator
│   ├── registry.py              # Registre id → fonction generate()
│   └── maths/equations.py        # Générateur : équations du premier degré ax + b = c
├── tests/                    # Tests pytest (19 tests)
├── docs/                      # Documentation (ce dossier)
├── .env.example                # Modèle des variables d'environnement
├── pyproject.toml               # Dépendances et configuration du projet
└── jury_central.db               # Base SQLite locale (générée, non versionnée)
```

## Prérequis

- Python 3.12 ou supérieur
- `pip` (aucun outil externe requis)

## Installation

```bash
# Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS

# Installer les dépendances (app + dev/tests)
pip install -e ".[dev]"

# Copier le fichier d'environnement et adapter les valeurs
cp .env.example .env
```

Variables requises dans `.env` (voir `.env.example`) : `SECRET_KEY` (signature des cookies
de session admin), `ADMIN_USERNAME`, `ADMIN_PASSWORD` (identifiant admin unique — pas de
gestion multi-utilisateurs à ce stade).

## Lancer le projet

```bash
# 1. Charger des données de démonstration (Mathématiques, MB32/MQ32/MQ34, une UAA d'exemple)
seed-db
# ou : python -m app.seed

# 2. Démarrer le serveur de développement
uvicorn app.main:app --reload
```

L'application est alors disponible sur http://127.0.0.1:8000.

## Accéder au panneau admin

Voir [docs/admin.md](docs/admin.md) pour le détail complet (identifiants, fonctionnalités,
limites connues). En résumé : http://127.0.0.1:8000/admin/login avec les identifiants définis
dans `.env`.

## Tests

```bash
pytest
```

## Documentation

- [docs/current_state.md](docs/current_state.md) — état exact du projet (routes, modèles,
  templates, fonctionnalités présentes/absentes) — **à lire en premier** pour reprendre le
  développement.
- [docs/admin.md](docs/admin.md) — accès et usage du panneau admin.
- [docs/development.md](docs/development.md) — mise en place de l'environnement de
  développement, commandes utiles, conventions du projet.
- [docs/git_workflow.md](docs/git_workflow.md) — branches, convention de commits, comment
  pousser vers GitHub et récupérer le projet sur une autre machine.

## Licence

À définir.

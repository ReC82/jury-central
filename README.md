# Jury Central

Plateforme pédagogique construite avec Python et FastAPI : contenu de cours organisé en
Matières → Modules → UAA → Blocs de leçon, panneau d'administration, exercices générés
automatiquement en Python, quiz interactifs et suivi de progression local (navigateur).

## Statut

En développement actif, en tranches verticales (une leçon complète à la fois plutôt qu'une
UAA entière d'un coup). Dernières tranches terminées :

- **MB32 UAA1 → Fonction constante** : expérience étudiante complète (cours, graphique
  interactif, exercices générés à l'infini, quiz de 10 questions avec score, fiche mémo
  imprimable). Voir [docs/mb32-uaa1.md](docs/mb32-uaa1.md).
- **Gestion complète de la hiérarchie de contenu depuis l'admin** : créer/modifier/supprimer
  une matière, un module ou une UAA se fait entièrement depuis `/admin`, sans plus jamais
  toucher à `app/seed.py` ni relancer `seed-db`. Voir
  [docs/content_workflow.md](docs/content_workflow.md).
- **MB32 UAA2 → Géométrie**, importée intégralement depuis la source officielle
  (`docs/sources_cours/`), et **Design System réutilisable** (cartes Théorie/Exemple/
  Exercice/Quiz/Attention/Résumé, exercices rédigés interactifs, tableaux éditables, quiz
  avec explication systématique) appliqué à toutes les UAA affichées. Voir
  [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md) et [docs/changelog.md](docs/changelog.md).

Voir [docs/changelog.md](docs/changelog.md) pour l'historique daté complet. Docker n'est pas
utilisé dans ce projet.

## Stack technique

- **Langage** : Python 3.12+
- **Framework web** : [FastAPI](https://fastapi.tiangolo.com/) + [Starlette](https://www.starlette.io/) (sessions)
- **Templates** : Jinja2 + [Bootstrap 5](https://getbootstrap.com/) (CDN) + [MathJax 3](https://www.mathjax.org/) (CDN) + [Plotly](https://plotly.com/javascript/) (CDN, chargé uniquement sur les pages avec un graphique interactif)
- **Base de données** : SQLAlchemy 2.0 (style déclaratif `Mapped`) + SQLite (fichier local, pas de migrations Alembic)
- **Génération d'exercices** : [SymPy](https://www.sympy.org/) pour la résolution/vérification, générateurs 100 % Python (pas d'IA)
- **Validation des réponses** : côté serveur (`app/answer_checking.py`), jamais de réponse stockée dans le HTML, jamais d'`eval()`
- **JavaScript** : vanilla JS uniquement (aucun framework, aucune dépendance npm)
- **Tests** : pytest (87 tests, tous dans `tests/`), y compris des tests `TestClient` sur une base SQLite isolée (jamais `jury_central.db`)

## Structure du projet

```
jury-central/
├── app/                    # Application FastAPI
│   ├── main.py              # Point d'entrée + routes publiques (accueil, matières, modules, UAA)
│   ├── admin.py              # Panneau admin (auth + CRUD matière/module/UAA/blocs de leçon)
│   ├── auth.py                # Vérification des identifiants + dépendance require_admin
│   ├── config.py               # Settings (pydantic-settings, lit .env)
│   ├── database.py              # Engine SQLAlchemy / SessionLocal / Base / get_db
│   ├── models.py                 # Modèles : Subject, Module, UAA, LessonBlock
│   ├── practice.py                # Entraînement libre + API JSON génération/vérification/correction
│   ├── answer_checking.py          # Parsing/comparaison normalisée des réponses (validation serveur)
│   ├── exercise_blocks.py           # Config JSON des blocs "generated_exercise"
│   ├── quiz.py                       # Config JSON des blocs "quiz" (QCM, vrai/faux, numérique, groupes)
│   ├── content.py                     # Rendu Markdown + extraction d'ID YouTube
│   ├── card_kind.py                    # Classe un bloc de leçon en type de carte (Design System)
│   ├── slugify.py                      # Génération de slugs (accents retirés, etc.)
│   ├── templating.py                    # Instance Jinja2Templates partagée
│   ├── seed.py                           # Données de démonstration + contenu réel MB32 UAA1/UAA2
│   ├── templates/                         # Templates Jinja2 (voir docs/current_state.md), dont _cards.html (Design System)
│   └── static/{css,js}/                    # CSS custom (dont design-system.css) + JS vanilla (exercise.js, quiz.js, progress.js, design_system.js, interactive_graph.js)
├── generators/               # Moteur de génération d'exercices — indépendant de FastAPI
│   ├── base.py                 # GeneratedExercise (dataclass) + interface ExerciseGenerator
│   ├── registry.py              # Registre id → fonction generate()
│   └── maths/{equations,constant_function}.py  # Générateurs implémentés
├── tests/                    # Tests pytest (87 tests, dont TestClient — voir tests/conftest.py)
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
# 1. Charger des données de démonstration (Mathématiques, MB32/MQ32/MQ34, UAA1 complète)
seed-db
# ou : python -m app.seed

# 2. Démarrer le serveur de développement
uvicorn app.main:app --reload
```

L'application est alors disponible sur http://127.0.0.1:8000. Pour repartir d'une base
locale vide (destructif, jamais automatique) : `reset-db` — voir
[docs/development.md](docs/development.md). Toute nouvelle matière/module/UAA se crée
ensuite depuis l'admin, pas dans le code (voir [docs/content_workflow.md](docs/content_workflow.md)).

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
- [docs/exercise_generators.md](docs/exercise_generators.md) — architecture des générateurs
  automatiques d'exercices, comment en ajouter un nouveau.
- [docs/content_workflow.md](docs/content_workflow.md) — comment ajouter une nouvelle UAA
  et structurer son contenu.
- [docs/mb32-uaa1.md](docs/mb32-uaa1.md) — détail de la leçon "Fonction constante" (objectifs,
  générateur, quiz, données initiales, limites).
- [docs/changelog.md](docs/changelog.md) — historique des tranches livrées.

## Licence

À définir.

# État actuel du projet — Jury Central

Document d'audit. Reflète l'état du code au moment de sa rédaction (après le commit
`0282895 feat: add local student progress`, branche `develop`). À mettre à jour à chaque
étape significative.

## 1. Structure du projet

```
jury-central/
├── app/                     # Application FastAPI (voir détail plus bas)
├── generators/               # Moteur de génération d'exercices, indépendant de app/
├── tests/                     # Tests pytest (19 tests)
├── docs/                       # Documentation
├── .env / .env.example          # Configuration (SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, ...)
├── pyproject.toml                # Dépendances + config pytest/ruff/hatch
└── jury_central.db                # Base SQLite locale (non versionnée, régénérée par seed-db)
```

Pas de Docker, pas de migrations Alembic (le schéma est créé via
`Base.metadata.create_all()` au démarrage de l'app et dans le script de seed — **toute
modification de modèle nécessite de supprimer `jury_central.db` en local**, il n'y a pas de
système de migration).

## 2. Fonctionnalités déjà présentes

- Navigation publique du contenu pédagogique : Matières → Modules → UAA → Blocs de leçon.
- 4 types de blocs de leçon fonctionnels : `markdown` (rendu HTML + support LaTeX via
  MathJax), `youtube` (embed responsive), `generated_exercise` (exercices générés à la
  volée), `quiz` (QCM interactif JS).
- 2 types de blocs déclarés dans le modèle mais **sans rendu dédié** : `image`, `pdf`,
  `exercise` (statique, distinct de `generated_exercise`) — affichés avec un message
  générique « type non pris en charge ».
- Authentification admin simple (session cookie, un seul compte défini par variables
  d'environnement).
- Panneau admin : lecture de la hiérarchie Matières/Modules/UAA, CRUD complet sur les
  `LessonBlock`.
- Moteur de génération d'exercices Python (sans IA) avec un générateur implémenté :
  équations du premier degré.
- Page d'entraînement libre (`/practice/equations`), indépendante du contenu de cours.
- Progression étudiant locale (`localStorage`, sans compte) : statut à faire / en cours /
  terminé par UAA, agrégé au niveau module et matière.

## 3. Routes FastAPI existantes

### Routes publiques (`app/main.py`)

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/health` | Ping JSON `{"status": "ok"}` |
| GET | `/` | Page d'accueil (`home.html`) |
| GET | `/subjects` | Liste des matières |
| GET | `/subjects/{subject_slug}` | Détail d'une matière → liste de ses modules |
| GET | `/modules/{module_slug}` | Détail d'un module → liste de ses UAA |
| GET | `/uaa/{uaa_slug}` | Détail d'une UAA → blocs de leçon **publiés**, dans l'ordre de `position` |

### Routes d'entraînement (`app/practice.py`, préfixe `/practice`)

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/practice/equations` | Génère et affiche un exercice d'équation (paramètre `difficulty=1\|2\|3`) |
| GET | `/practice/api/generate` | JSON — régénère un exercice (`generator`, `difficulty`) ; utilisé par le bouton "Nouvel exercice" en AJAX |

### Routes admin (`app/admin.py`, préfixe `/admin`)

| Méthode | Route | Protégée ? | Rôle |
|---|---|---|---|
| GET/POST | `/admin/login` | Non | Formulaire de connexion |
| GET | `/admin/logout` | Oui | Déconnexion (vide la session) |
| GET | `/admin/dashboard` | Oui | Tableau de bord (compteurs matières/modules/UAA) |
| GET | `/admin/subjects` | Oui | Liste des matières (lecture seule) |
| GET | `/admin/subjects/{subject_id}` | Oui | Liste des modules d'une matière (lecture seule) |
| GET | `/admin/modules/{module_id}` | Oui | Liste des UAA d'un module (lecture seule) |
| GET | `/admin/uaa/{uaa_id}` | Oui | Liste des blocs de leçon d'une UAA (avec actions) |
| GET/POST | `/admin/uaa/{uaa_id}/blocks/new` | Oui | Créer un bloc |
| GET/POST | `/admin/blocks/{block_id}/edit` | Oui | Modifier un bloc |
| POST | `/admin/blocks/{block_id}/delete` | Oui | Supprimer un bloc |

Toutes les routes `/admin/*` sont protégées **sauf** `/admin/login` (dépendance
`require_admin` posée au niveau du routeur `protected_router`).

## 4. Modèles SQLAlchemy existants (`app/models.py`)

- **`Subject`** : `id`, `name` (unique), `slug` (unique). Relation 1—N vers `Module`
  (cascade delete).
- **`Module`** : `id`, `code`, `slug` (unique), `subject_id`. Relation 1—N vers `UAA`
  (cascade delete).
- **`UAA`** : `id`, `code`, `title`, `slug` (unique), `module_id`. Relation 1—N vers
  `LessonBlock` (cascade delete, triée par `position`).
- **`LessonBlock`** : `id`, `title`, `type` (enum `BlockType`), `content` (texte libre —
  **polymorphe selon le type**, voir ci-dessous), `position` (int), `is_published` (bool),
  `uaa_id`.
- **`BlockType`** (enum str) : `markdown`, `youtube`, `image`, `pdf`, `exercise`, `quiz`,
  `generated_exercise`.

### Convention importante : le champ `content` est polymorphe

Il n'y a pas de colonnes dédiées par type de bloc. `content` contient :
- du texte Markdown brut pour `markdown` ;
- une URL ou un ID YouTube pour `youtube` ;
- un objet JSON sérialisé pour `generated_exercise`
  (`app/exercise_blocks.py::ExerciseBlockConfig` : `generator`, `difficulty`, `count`,
  `tags`) ;
- un objet JSON sérialisé pour `quiz` (`app/quiz.py::QuizConfig` : `question`, `choices`,
  `correct_index`, `explanation`) ;
- non défini/à vérifier pour `image`, `pdf`, `exercise` (types déclarés mais jamais utilisés
  par le seed ni par un formulaire admin dédié).

## 5. Templates Jinja2 existants (`app/templates/`)

| Template | Utilisé par | Rôle |
|---|---|---|
| `base.html` | tous | Layout Bootstrap (navbar, footer), charge MathJax + `exercise.js`, `quiz.js`, `progress.js` |
| `home.html` | `GET /` | Page d'accueil |
| `subjects.html` | `GET /subjects` | Liste des matières + badge de progression agrégé |
| `subject_detail.html` | `GET /subjects/{slug}` | Liste des modules + badge de progression agrégé |
| `module_detail.html` | `GET /modules/{slug}` | Liste des UAA + badge de progression par UAA |
| `uaa_detail.html` | `GET /uaa/{slug}` | Rendu des blocs publiés (markdown/youtube/generated_exercise/quiz) + bouton "Marquer comme terminé" |
| `practice_equations.html` | `GET /practice/equations` | Page d'entraînement libre équations |
| `admin_login.html` | `GET/POST /admin/login` | Formulaire de connexion admin |
| `admin_dashboard.html` | `GET /admin/dashboard` | Tableau de bord admin |
| `admin_subjects.html` | `GET /admin/subjects` | Liste admin des matières |
| `admin_modules.html` | `GET /admin/subjects/{id}` | Liste admin des modules |
| `admin_uaa_list.html` | `GET /admin/modules/{id}` | Liste admin des UAA |
| `admin_uaa_blocks.html` | `GET /admin/uaa/{id}` | Liste admin des blocs (tableau + actions) |
| `admin_block_form.html` | création/édition de bloc | Formulaire unique gérant tous les types (générique + fieldsets dédiés `generated_exercise`/`quiz`) |

## 6. Pages publiques déjà utilisables

- `/` — Accueil.
- `/subjects` — Liste des matières.
- `/subjects/{slug}` — Détail d'une matière.
- `/modules/{slug}` — Détail d'un module.
- `/uaa/{slug}` — Détail d'une UAA (contenu réel, exercices, quiz, bouton progression).
- `/practice/equations` — Entraînement libre (indépendant du contenu de cours), avec
  sélection de niveau (1 à 3) et bouton "Nouvel exercice".

Toutes fonctionnelles avec les données du seed (`seed-db`).

## 7. Panneau admin existant

Voir [docs/admin.md](docs/admin.md) pour le détail complet (accès, capacités, limites).

## 8. Accéder au panneau admin

Voir [docs/admin.md](docs/admin.md#accès).

## 9. Ce qu'on peut faire actuellement dans le panneau admin

Voir [docs/admin.md](docs/admin.md#fonctionnalités-disponibles).

## 10. Limites actuelles du panneau admin

Voir [docs/admin.md](docs/admin.md#limites-connues).

## 11. Système de quiz : existe-t-il déjà ?

**Oui, fonctionnel.** Type de bloc `quiz` :
- Stockage : JSON dans `LessonBlock.content` via `app/quiz.py::QuizConfig` (question,
  liste de choix, index de la bonne réponse, explication).
- Admin : formulaire dédié (question, 4 champs réponse + case à cocher radio pour la bonne
  réponse, explication) dans `admin_block_form.html`, avec validation serveur (question
  obligatoire, ≥ 2 réponses non vides, réponse correcte valide).
- Public : rendu dans `uaa_detail.html`, interaction 100 % JS côté navigateur
  (`app/static/js/quiz.js`) — clic sur une réponse → coloration correct/incorrect +
  affichage de l'explication. Aucun appel serveur au moment de répondre.
- Limite connue : une seule bonne réponse possible (pas de QCM à réponses multiples), pas de
  historique/score des tentatives (cohérent avec l'absence de comptes étudiants).

## 12. Système d'exercices : existe-t-il déjà ?

**Oui, deux mécanismes distincts, à ne pas confondre :**

1. **`generated_exercise`** (bloc de leçon, intégré à une UAA) : configuré dans l'admin
   (générateur, difficulté par défaut, nombre d'exercices, tags pédagogiques), affiché sur
   la page publique de l'UAA avec énoncé, champ de réponse, bouton Vérifier (comparaison
   normalisée côté JS), bouton Afficher la correction, bouton Nouvel exercice (régénère via
   `/practice/api/generate` sans recharger la page).
2. **`/practice/equations`** : page d'entraînement libre, indépendante du contenu de cours,
   même moteur de génération, sélection de niveau de difficulté.

Type de bloc `exercise` (statique, sans génération) : **déclaré dans l'enum `BlockType` mais
non implémenté** — pas de rendu public, pas de champs admin dédiés, jamais utilisé par le
seed. À vérifier si ce type est encore pertinent ou s'il doit être retiré/renommé pour éviter
la confusion avec `generated_exercise`.

## 13. Générateurs Python d'exercices : existe-t-il déjà ?

**Oui**, package `generators/` (racine du projet, indépendant de `app/` et de FastAPI) :

- `generators/base.py` : dataclass `GeneratedExercise` (statement, answer, difficulty, seed,
  solution_steps, metadata) + interface `ExerciseGenerator` (Protocol) définissant
  `generate(difficulty: int, seed: int | None = None) -> GeneratedExercise`.
- `generators/registry.py` : registre `{id: fonction}` avec `get_generator()` et
  `available_generators()`.
- `generators/maths/equations.py` : **un seul générateur implémenté**, enregistré sous l'id
  `maths.equations.linear_equation` — équations du premier degré `ax + b = c`. Garantit
  `a ≠ 0` (jamais d'équation impossible ni d'identité), solutions entières forcées aux
  niveaux 1-2, fractions autorisées au niveau 3. Résolution et vérification via SymPy.

Aucune IA utilisée. Couvert par 11 tests unitaires (`tests/generators/`).

## 14. Documentation : existe-t-il déjà une documentation correcte ?

**Avant cette étape : non.** Le `README.md` datait de l'étape 1 (structure de projet vide,
« aucune fonctionnalité métier n'est encore implémentée ») et ne reflétait plus du tout
l'état réel du code. `docs/README.md` était un simple placeholder listant des intentions,
sans contenu réel.

**Après cette étape :**
- `README.md` — mis à jour (vue d'ensemble, installation, lancement).
- `docs/current_state.md` — ce document.
- `docs/admin.md` — accès et usage du panneau admin.
- `docs/development.md` — environnement de développement, commandes, conventions.
- `docs/README.md` — laissé tel quel (non demandé dans cette étape ; à fusionner ou
  supprimer plus tard, "à vérifier" avec le porteur du projet).

## Points "à vérifier" (incertitudes identifiées pendant l'audit)

- Utilité future des types de bloc `image`, `pdf`, `exercise` (déclarés, jamais implémentés
  côté admin ni côté rendu public) — à vérifier s'ils sont encore au plan.
- `jury_central.db` présent à la racine au moment de l'audit (fichier gitignored, généré
  localement par les tests manuels précédents) — à vérifier qu'aucune donnée qu'on veut
  garder n'y est stockée avant de le supprimer/régénérer.
- Pas de suite de tests automatisés sur les routes FastAPI elles-mêmes (`TestClient`) — les
  19 tests actuels couvrent uniquement `generators/` et les modules de config
  (`exercise_blocks.py`, `quiz.py`). Les routes ont été vérifiées manuellement à chaque
  étape (voir historique de commits) mais pas par une suite automatisée reproductible.

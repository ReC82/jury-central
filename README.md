# Jury Central

Application de gestion de jurys, construite avec Python et FastAPI.

## Statut

🚧 En cours de démarrage — structure initiale uniquement, aucune fonctionnalité métier n'est encore implémentée.

## Stack technique

- **Langage** : Python 3.12+
- **Framework** : [FastAPI](https://fastapi.tiangolo.com/)
- **Gestion de dépendances / build** : [pyproject.toml](pyproject.toml) (PEP 621)

## Structure du projet

```
jury-central/
├── app/            # Code source de l'application FastAPI
├── tests/          # Tests automatisés
├── docs/           # Documentation du projet
├── .env.example    # Modèle des variables d'environnement
├── pyproject.toml  # Configuration du projet et dépendances
└── README.md
```

## Prérequis

- Python 3.12 ou supérieur
- [uv](https://github.com/astral-sh/uv) ou `pip` pour la gestion des dépendances

## Installation

```bash
# Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS

# Installer les dépendances
pip install -e ".[dev]"

# Copier le fichier d'environnement
cp .env.example .env
```

## Lancement (à venir)

L'application n'étant pas encore implémentée, aucune commande de lancement n'est disponible pour le moment.

## Licence

À définir.

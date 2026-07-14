# Jury Central - Développement

Ce document décrit l'environnement de développement et les commandes utiles.

Les conventions générales du projet sont décrites dans `PROJECT_RULES.md`.

L'architecture est décrite dans `ARCHITECTURE.md`.

---

# Prérequis

- Python 3.12
- Git
- SQLite
- Environnement virtuel Python

---

# Installation

Créer l'environnement virtuel :

```bash
python -m venv .venv
```

Windows :

```bash
.venv\Scripts\activate
```

Linux / macOS :

```bash
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -e ".[dev]"
```

Créer le fichier de configuration :

```bash
cp .env.example .env
```

Configurer ensuite :

- ADMIN_USERNAME
- ADMIN_PASSWORD
- SECRET_KEY

---

# Lancer le projet

Initialiser les données :

```bash
seed-db
```

Lancer le serveur :

```bash
uvicorn app.main:app --reload
```

Application :

```
http://127.0.0.1:8000
```

---

# Base de données

La base locale est :

```
jury_central.db
```

Elle est créée automatiquement.

Aucun système de migration n'est utilisé actuellement.

Après une modification des modèles :

```bash
reset-db
```

---

# Tests

Lancer tous les tests :

```bash
pytest
```

Le projet doit rester avec tous les tests au vert.

---

# Lint

```bash
ruff check .
```

---

# Commandes utiles

Réinitialiser la base :

```bash
reset-db
```

Lancer un second serveur :

```bash
uvicorn app.main:app --port 8001
```

---

# Workflow de développement

Pour chaque fonctionnalité :

1. analyser le projet ;
2. réutiliser les composants existants ;
3. développer ;
4. écrire ou adapter les tests ;
5. vérifier que tous les tests passent ;
6. mettre à jour la documentation si nécessaire ;
7. faire un commit propre.

---

# Bonnes pratiques

Toujours :

- utiliser l'environnement virtuel ;
- lancer les tests avant un commit ;
- éviter les duplications ;
- privilégier la simplicité ;
- respecter les conventions du projet.

---

# Ce qui n'est pas encore implémenté

- Système de migration
- Comptes étudiants
- Synchronisation cloud de la progression
- Réorganisation des contenus par glisser-déposer
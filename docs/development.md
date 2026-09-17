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

# Serveur de test local sûr (ticket #35)

**Ne jamais lancer un second `uvicorn app.main:app ...` ad hoc pour une vérification
manuelle sur une machine où `/srv/jury-central/.env` contient une vraie clé (le serveur
staging) : `app.config.Settings` (pydantic-settings) retombe silencieusement sur la
lecture de `.env` dès qu'une variable comme `OPENAI_API_KEY` est absente du process — ce
qui a provoqué un appel OpenAI réel non intentionnel pendant le développement du ticket
#29.**

Utiliser à la place :

```bash
safe-local-server                     # http://127.0.0.1:8099, --reload possible
safe-local-server --port 8123 --reload
```

Cette commande force `OPENAI_API_KEY=""` dans le process avant même d'importer
l'application : la génération/correction IA répond systématiquement « non configurée »
(503), sans jamais pouvoir appeler l'API OpenAI réelle, quel que soit le contenu de
`.env`. Les autres réglages (base de données, identifiants admin, etc.) restent lus
normalement depuis `.env`/l'environnement — seule `OPENAI_API_KEY` est neutralisée. Voir
`app/safe_local_server.py` (docstring) et
`docs/claude-reports/2026-09-17_ticket-35_safe-openai-local-tests.md` pour le détail de
l'incident et de la correction.

Le service staging réel (`jury-central.service`, systemd) n'est pas concerné par ce
risque et n'utilise jamais cette commande : `EnvironmentFile=/srv/jury-central/.env`
positionne `OPENAI_API_KEY` comme une vraie variable d'environnement du process avant le
démarrage d'uvicorn, donc `Settings()` ne retombe jamais sur la lecture de `.env` dans ce
cas (une variable de process a toujours priorité).

---

# Commandes utiles

Réinitialiser la base :

```bash
reset-db
```

Lancer un second serveur, ou toute vérification manuelle ponctuelle (voir « Serveur de
test local sûr » ci-dessous) :

```bash
safe-local-server
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
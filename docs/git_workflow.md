# Workflow Git — Jury Central

Ce document décrit comment travailler sur ce dépôt depuis plusieurs machines, et plus tard
depuis GitHub Codespaces. Le dépôt est encore 100 % local à ce stade : aucun remote GitHub
n'est configuré, aucun push n'a été fait.

## État actuel du dépôt (au moment de la rédaction)

- Une seule branche existe localement : **`develop`**.
- Aucune branche `main` n'existe encore.
- Aucun remote n'est configuré (`git remote -v` ne retourne rien).
- Travail à faire avant tout push : décider quelle branche fait office de branche par défaut
  sur GitHub (recommandation ci-dessous), puis suivre la section
  [Premier push vers GitHub](#premier-push-vers-github).

## Branches recommandées

- **`main`** — branche stable, toujours déployable. C'est elle qui doit être la branche par
  défaut sur GitHub (celle que Codespaces ouvrira par défaut plus tard).
- **`develop`** — branche d'intégration continue du développement courant. C'est la branche
  utilisée jusqu'ici pour tout le travail de ce projet.
- **`feature/<nom-court>`** — une branche par fonctionnalité, créée à partir de `develop`,
  fusionnée dans `develop` une fois terminée (ex. `feature/quiz-blocks`,
  `feature/git-workflow`).

Projet simple, équipe réduite : pas besoin de branches `release/*` ou `hotfix/*` pour
l'instant. À introduire seulement si un besoin concret apparaît (ex. plusieurs versions en
prod en parallèle).

Comme `main` n'existe pas encore localement, deux options :

1. **Recommandé** : créer `main` à partir de l'état actuel de `develop` au moment du premier
   push, puis continuer à développer sur `develop` et fusionner vers `main` par pull request
   quand une étape est stable.
2. Continuer uniquement sur `develop` et ne créer `main` que plus tard. Fonctionne aussi,
   mais GitHub désignera `develop` comme branche par défaut tant que `main` n'existe pas.

## Convention de commits

Le projet suit déjà `type: description courte à l'impératif`, visible dans l'historique
existant (`feat: add quiz blocks`, `docs: document current project state...`). À conserver :

| Type | Usage |
|---|---|
| `feat` | nouvelle fonctionnalité |
| `fix` | correction de bug |
| `docs` | documentation uniquement |
| `chore` | maintenance, config, dépendances |
| `refactor` | changement de structure sans changement de comportement |
| `test` | ajout/modification de tests uniquement |

Règles :
- Message court (≤ 70 caractères) à l'impératif : `feat: add quiz blocks`, pas
  `feat: added quiz blocks` ni `feat: Ajout des quiz`.
- Un commit = un changement cohérent. Éviter les commits fourre-tout.
- Corps du message (optionnel, après une ligne vide) pour expliquer le **pourquoi** si ce
  n'est pas évident depuis le diff.

## Créer une branche feature

```bash
git checkout develop
git pull                              # une fois un remote configuré
git checkout -b feature/nom-court
```

Travailler, committer normalement (`git add`, `git commit`), puis :

```bash
git push -u origin feature/nom-court   # une fois un remote configuré
```

Ouvrir une pull request `feature/nom-court` → `develop` sur GitHub. Fusionner une fois
relu/testé, puis supprimer la branche feature.

## Comment pousser

### Premier push vers GitHub

Le remote n'existe pas encore. Voir la section dédiée
[Premier push vers GitHub](#premier-push-vers-github) plus bas — les commandes y sont
détaillées mais **pas exécutées automatiquement**, car elles impliquent de créer un
repository GitHub.

### Pousser une branche existante (une fois le remote configuré)

```bash
git push                          # branche déjà suivie (upstream configuré)
git push -u origin <nom-branche>  # première fois pour cette branche
```

## Récupérer le projet sur un autre PC

```bash
git clone <url-du-repo>
cd jury-central

python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS

pip install -e ".[dev]"
cp .env.example .env        # puis éditer ADMIN_USERNAME / ADMIN_PASSWORD / SECRET_KEY

seed-db
uvicorn app.main:app --reload
```

`jury_central.db` n'est pas versionné (généré localement par `seed-db`) : chaque machine a
sa propre base SQLite locale, indépendante des autres. `.env` non plus : à recréer sur
chaque machine à partir de `.env.example`.

## Premier push vers GitHub

Le remote GitHub n'existe pas encore. Voici les commandes exactes — **à exécuter toi-même**,
je ne les lance pas à ta place puisqu'elles nécessitent de créer un repository GitHub
(décision et action côté compte GitHub).

### 1. Créer le repository sur GitHub

Deux façons équivalentes :

**Via l'interface web** : https://github.com/new → nom `jury-central` → ne pas cocher
"Initialize with README" (le dépôt local a déjà du contenu) → Create repository.

**Via `gh` (GitHub CLI), si installé** :
```bash
gh repo create jury-central --private --source=. --remote=origin
```
(`gh repo create --source=.` avec `--remote=origin` fait aussi l'étape 2 ci-dessous en un
seul appel — dans ce cas, passer directement à l'étape 3.)

### 2. Ajouter le remote (si le repo a été créé via l'interface web)

```bash
git remote add origin https://github.com/<ton-compte>/jury-central.git
```

### 3. Pousser la branche

Option recommandée : créer `main` à partir de `develop` et la pousser en premier, pour
qu'elle devienne la branche par défaut sur GitHub.

```bash
git checkout develop
git checkout -b main
git push -u origin main

git checkout develop
git push -u origin develop
```

Sur GitHub, vérifier ensuite (Settings → Branches) que `main` est bien la branche par
défaut, et éventuellement activer une protection de branche.

Alternative plus simple si tu préfères garder `develop` comme branche principale pour
l'instant :

```bash
git push -u origin develop
```

## Codespaces (à venir)

Pas de devcontainer pour l'instant, comme demandé. Quand Codespaces sera activé, il faudra :

- s'assurer que `main` (ou la branche par défaut choisie) est à jour et propre ;
- créer un `.devcontainer/` minimal (Python 3.12, `pip install -e ".[dev]"` en
  `postCreateCommand`) — **à faire seulement le jour où Codespaces est explicitement
  demandé**, pas avant.

Aucune action Docker n'est nécessaire pour Codespaces à ce stade : GitHub fournit une image
de base, un devcontainer ne requiert pas nécessairement de Dockerfile custom pour un projet
aussi simple.

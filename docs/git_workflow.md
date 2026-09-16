# Jury Central - Workflow Git

Ce document décrit les conventions Git utilisées dans Jury Central.

Les décisions de fond (branches, merges, déploiement) sont fixées par
`docs/PROJECT_RULES.md` § 8 — ce document ne fait qu'en détailler l'usage pratique.

---

# Objectif

L'historique Git doit rester :

- propre ;
- lisible ;
- facilement compréhensible.

Chaque commit doit représenter une évolution cohérente.

---

# Pilotage

- **ChatGPT** est chef de projet : backlog, priorités, critères d'acceptation, via des
  tickets GitHub.
- **Claude Code** développe à partir d'un ticket, reste dans son périmètre, commit et
  push la branche du ticket.
- **GitHub** (issues) est la source de vérité pour les tâches et leur historique.

---

# Branches

## main

Branche stable. Ne contient que du code fonctionnel. Aucun développement direct dessus.

## develop

Branche d'intégration. Toutes les fonctionnalités y sont fusionnées avant `main`.

## feature/\<numero-ticket\>-\<slug\> et fix/\<numero-ticket\>-\<slug\>

Chaque ticket GitHub est développé dans une branche dédiée, créée depuis `develop` :

```
feature/12-import-mb32-uaa3
fix/7-quiz-scoring
```

`feature/` pour une nouvelle fonctionnalité, `fix/` pour une correction. Une branche =
un ticket.

---

# Workflow

```bash
git checkout develop
git pull
git checkout -b feature/<numero-ticket>-<slug>
```

1. Lire intégralement le ticket avant toute modification.
2. Développer strictement dans le périmètre du ticket.
3. Écrire/adapter les tests, exécuter `pytest`.
4. Mettre à jour la documentation concernée.
5. Committer (voir convention ci-dessous).
6. Pousser la branche sur `origin`.

**Aucun merge vers `develop` ou `main` sans validation explicite.**
**Aucun déploiement sans demande explicite.**

Le merge vers `develop`, puis vers `main`, reste une décision humaine, prise en dehors de
ce workflow automatisé.

---

# Commits

Convention :

```
type: description
```

Types utilisés :

| Type | Utilisation |
|-------|-------------|
| feat | nouvelle fonctionnalité |
| fix | correction |
| docs | documentation |
| refactor | amélioration interne |
| style | mise en forme, sans changement de comportement |
| test | tests |
| chore | maintenance |

Exemples :

```
feat: import MB32 UAA2

fix: correct quiz rendering

docs: update import workflow

refactor: simplify lesson renderer
```

---

# Bonnes pratiques

Toujours :

- faire des commits petits et cohérents ;
- écrire un message clair ;
- terminer une fonctionnalité avant de fusionner.

Éviter :

- les commits "WIP" ;
- les commits contenant plusieurs fonctionnalités ou plusieurs tickets ;
- les commits sans tests lorsque des tests sont nécessaires.

---

# Avant un commit

Toujours vérifier (voir `docs/PROJECT_RULES.md` § 7) :

- le projet compile ;
- les tests passent (`pytest`) ;
- aucun fichier inutile n'est ajouté ;
- la documentation est à jour si nécessaire.

---

# Avant un merge

Vérifier (revue humaine, hors périmètre de Claude Code sauf demande explicite) :

- absence de conflits ;
- fonctionnement de l'application ;
- cohérence avec les conventions du projet.

---

# Dépôt

Le dépôt Git constitue la source de vérité du projet.

Aucun fichier généré localement ne doit être versionné.

Exemples :

- base SQLite locale ;
- environnement virtuel ;
- fichiers temporaires.

---

# Historique

Préférer un historique simple.

Éviter les commits inutiles.

Chaque commit doit pouvoir être compris indépendamment.

---

# Objectif

Le workflow Git doit rester suffisamment simple pour permettre :

- un développement piloté par tickets GitHub, sur plusieurs machines (dont AWS via tmux) ;
- une maintenance facile ;
- une collaboration future entre plusieurs intervenants.

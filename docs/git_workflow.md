# Jury Central - Workflow Git

Ce document décrit les conventions Git utilisées dans Jury Central.

---

# Objectif

L'historique Git doit rester :

- propre ;
- lisible ;
- facilement compréhensible.

Chaque commit doit représenter une évolution cohérente.

---

# Branches

Le projet utilise les branches suivantes.

## main

Branche stable.

Elle contient uniquement du code fonctionnel.

---

## develop

Branche principale de développement.

Toutes les nouvelles fonctionnalités sont intégrées ici avant d'être fusionnées dans `main`.

---

## feature/<nom>

Chaque nouvelle fonctionnalité est développée dans une branche dédiée.

Exemples :

```
feature/import-workflow
feature/content-import
feature/exercise-generator
feature/admin-improvements
```

Une branche feature est fusionnée dans `develop` une fois terminée.

---

# Workflow

Créer une branche :

```bash
git checkout develop
git pull
git checkout -b feature/nom
```

Développer.

Committer régulièrement.

Fusionner dans `develop`.

Une fois une étape stable :

fusion de `develop` vers `main`.

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

- faire des commits petits ;
- faire des commits cohérents ;
- écrire un message clair ;
- terminer une fonctionnalité avant de fusionner.

Éviter :

- les commits "WIP" ;
- les commits contenant plusieurs fonctionnalités ;
- les commits sans tests lorsque des tests sont nécessaires.

---

# Push

Ne jamais pousser directement sur `main`.

Le développement se fait sur :

- feature/*
- develop

---

# Avant un commit

Toujours vérifier :

- le projet compile ;
- les tests passent ;
- aucun fichier inutile n'est ajouté ;
- la documentation est à jour si nécessaire.

---

# Avant un merge

Vérifier :

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

- un développement sur plusieurs machines ;
- un développement via Codespaces ;
- une maintenance facile ;
- une collaboration future.
# Jury Central - Générateurs d'exercices

Ce document décrit le fonctionnement des générateurs automatiques d'exercices.

Les générateurs constituent le moteur permettant de produire un nombre illimité d'exercices sans utiliser d'intelligence artificielle.

---

# Objectif

Un générateur produit automatiquement un exercice différent à chaque exécution.

Le résultat doit rester :

- cohérent ;
- reproductible ;
- déterministe lorsqu'un seed est fourni.

---

# Architecture

Les générateurs sont indépendants du reste de l'application.

Ils sont situés dans :

```
generators/
```

Ils ne dépendent jamais de :

- FastAPI
- SQLAlchemy
- Templates
- Base de données

Ils doivent pouvoir être utilisés comme une bibliothèque Python autonome.

---

# Organisation

```
generators/

base.py
registry.py

maths/
...
```

---

# Principe

Chaque générateur reçoit :

- une difficulté
- un seed optionnel

et retourne un objet `GeneratedExercise`.

---

# Interface

```python
generate(
    difficulty: int,
    seed: int | None = None
) -> GeneratedExercise
```

Tous les générateurs doivent respecter cette interface.

---

# GeneratedExercise

Le générateur retourne :

- énoncé
- réponse
- difficulté
- seed
- correction
- indice
- métadonnées

Le type de la réponse est libre.

---

# Déterminisme

Si un seed est fourni :

```
generate(2, 1234)
```

le résultat doit toujours être identique.

Cette règle est obligatoire.

---

# Ce qu'un générateur ne doit jamais faire

Un générateur ne doit jamais :

- accéder à la base de données ;
- appeler une API ;
- utiliser une IA ;
- dépendre de FastAPI ;
- écrire dans un fichier.

Il ne fait qu'un calcul.

---

# Registre

Tous les générateurs sont enregistrés dans :

```
generators/registry.py
```

Convention :

```
maths.equations.linear_equation
```

Le registre constitue la seule source de vérité.

---

# Ajouter un générateur

1. créer le module ;
2. implémenter `generate()` ;
3. enregistrer le générateur ;
4. ajouter les tests.

Aucune autre modification ne doit être nécessaire.

---

# Intégration

Les générateurs sont utilisés par :

- les exercices des cours ;
- le mode entraînement ;
- les pages de pratique ;
- l'administration.

---

# Validation

La validation des réponses est toujours réalisée côté serveur.

La réponse correcte n'est jamais envoyée au navigateur avant que l'étudiant ait répondu.

---

# Tests

Chaque générateur doit être testé.

Les tests vérifient notamment :

- le type retourné ;
- le déterminisme ;
- les cas limites ;
- la cohérence des réponses.

---

# Évolutions

À terme, des générateurs seront disponibles pour l'ensemble des matières.

Chaque nouveau générateur devra respecter les conventions définies dans ce document.
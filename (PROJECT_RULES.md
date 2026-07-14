# Jury Central - Project Bible

Version : 1.0
Auteur : Lloyd Malfliet
Chef de projet : ChatGPT
Développeur principal : Claude Code (VS Code)

---

# Vision

Jury Central est une plateforme permettant de préparer les examens du Jury Central belge.

La première version est exclusivement dédiée au CESS Professionnel.

Le projet devra cependant permettre l'ajout futur d'autres parcours sans refonte majeure.

Exemples :

- CESS Général
- CEB
- CE1D
- Permis de conduire
- CCNA
- Azure
- Linux
- ...

Le projet doit rester simple, rapide et maintenable.

Le but n'est pas de faire un LMS complexe mais un excellent outil d'apprentissage.

---

# Philosophie

Toujours privilégier :

- simplicité
- lisibilité
- maintenabilité
- modularité

Avant :

- optimisation
- fonctionnalités gadgets
- sophistication inutile

---

# Public cible

Étudiants préparant le Jury Central.

Le niveau pédagogique doit partir de zéro.

Les explications doivent être adaptées à une personne qui reprend ses études.

---

# Stack technique

Python 3.13

FastAPI

Jinja2

Bootstrap 5

SQLite

SQLAlchemy

Alembic

MathJax

Plotly

Markdown

Git

GitHub

GitHub Codespaces

Docker n'est PAS utilisé.

L'IA n'est PAS intégrée au site.

Claude sert uniquement au développement.

---

# Architecture

Le projet est découpé en plusieurs couches.

Presentation

↓

Application

↓

Domain

↓

Persistence

↓

Content

↓

Exercise Generators

Chaque couche doit rester indépendante.

---

# Structure générale

app/

templates/

static/

content/

generators/

tests/

docs/

---

# Contenu

Le contenu pédagogique ne contient aucun code Python.

Il est indépendant.

Chaque UAA contient :

- théorie
- exemples
- exercices
- quiz
- fiche mémo
- évaluation

---

# Générateurs

Principe fondamental :

Lorsque des exercices peuvent être générés automatiquement, aucune banque fixe ne doit être créée.

Chaque générateur doit produire un nombre illimité d'exercices.

Chaque générateur doit toujours être déterministe à partir d'une graine.

Chaque générateur retourne :

- énoncé
- paramètres
- réponse
- correction détaillée
- difficulté
- tags

Les calculs doivent être réalisés en Python.

Jamais par l'IA.

---

# Quiz

Les quiz sont indépendants des générateurs.

Ils peuvent être :

- importés
- exportés
- modifiés

L'administration devra permettre :

Télécharger un modèle

↓

Compléter sous Excel/CSV

↓

Importer

↓

Validation

↓

Publication

---

# Administration

Le panneau d'administration est destiné au créateur du contenu.

Il doit permettre :

Gestion des matières

Gestion des modules

Gestion des UAA

Gestion des chapitres

Gestion des blocs

Gestion des exercices

Gestion des quiz

Gestion des générateurs

Gestion des vidéos

Gestion des PDF

Gestion des images

Gestion de la publication

Chaque nouvelle fonctionnalité de l'administration doit être documentée.

---

# Documentation

La documentation est obligatoire.

Après chaque fonctionnalité :

README

Changelog

Documentation concernée

Tests

Architecture

Administration

Tout changement doit être documenté.

---

# Tests

Une fonctionnalité n'est jamais terminée tant que :

les tests automatiques passent

ET

les tests manuels sont fournis.

---

# Git

Aucun développement sur main.

Workflow :

feature

↓

develop

↓

main

Une fonctionnalité = une branche.

Une fonctionnalité = un commit.

Chaque commit utilise :

feat:

fix:

docs:

refactor:

style:

test:

chore:

Après validation :

git push

systématique.

---

# Vertical Slice

Nous ne développons plus une UAA entière.

Nous développons un chapitre complet.

Un chapitre terminé contient :

cours

exemples

générateur

quiz

progression

documentation

tests

admin

Une fois terminé :

commit

push

Puis seulement le chapitre suivant.

---

# UX

Toujours privilégier :

peu de clics

navigation simple

interface claire

responsive

lisibilité

accessibilité

L'étudiant doit toujours savoir :

où il est

ce qu'il lui reste

où continuer.

---

# Performance

Éviter toute complexité inutile.

Pas de framework JS lourd.

Préférer HTMX lorsque pertinent.

Bootstrap reste la base graphique.

---

# Sécurité

Aucun secret dans Git.

Validation serveur.

Aucun eval().

Protection CSRF.

Validation des entrées.

---

# Documentation développeur

Avant chaque développement Claude doit :

1. lire PROJECT_RULES.md

2. lire README.md

3. lire docs/

4. inspecter le projet

5. réutiliser l'existant

6. éviter les doublons

7. expliquer son plan

8. attendre validation

---

# Documentation après chaque livraison

Mettre à jour :

README

docs/changelog.md

docs/testing.md

docs/development.md

docs/admin-panel.md

docs/architecture.md

si nécessaire.

---

# Ce qu'il ne faut jamais faire

Créer un deuxième système existant déjà.

Créer des routes dupliquées.

Créer des modèles dupliqués.

Créer une banque fixe lorsqu'un générateur est possible.

Réécrire entièrement une fonctionnalité existante.

Supprimer une fonctionnalité sans migration.

Ajouter une dépendance lourde sans justification.

Introduire Docker.

Introduire de l'IA dans l'application.

---

# Décision de développement

En cas de doute :

privilégier

la solution

la plus simple

la plus lisible

la plus maintenable

et

la plus réutilisable.
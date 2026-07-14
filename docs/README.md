# Jury Central - Documentation

Ce dossier contient toute la documentation du projet Jury Central.

Avant toute modification du projet, commence toujours par lire ce fichier puis les documents indiqués ci-dessous.

---

# Ordre de lecture

Lis les documents dans cet ordre :

1. ARCHITECTURE.md
2. current_state.md
3. development.md
4. PROJECT_RULES.md
5. IMPORT_WORKFLOW.md

Les autres documents ne sont à consulter que si la tâche le nécessite.

---

# Documentation disponible

## ARCHITECTURE.md

Architecture technique du projet.

Contient notamment :

- structure générale
- organisation du code
- conventions techniques
- modèles de données
- composants principaux

---

## current_state.md

Décrit l'état actuel du projet.

Permet de connaître :

- les fonctionnalités terminées
- les fonctionnalités en cours
- les limitations actuelles
- les décisions déjà prises

---

## development.md

Roadmap du projet.

Contient :

- prochaines étapes
- priorités
- backlog

---

## PROJECT_RULES.md

Règles permanentes du projet.

Ces règles doivent toujours être respectées.

---

## IMPORT_WORKFLOW.md

Décrit la procédure d'import d'une nouvelle UAA.

À utiliser lorsqu'un nouveau cours doit être intégré.

---

## content_workflow.md

Organisation du contenu pédagogique.

Décrit :

- cours
- chapitres
- quiz
- exercices
- fiches mémo
- ressources

---

## UI_GUIDELINES.md

Règles d'interface utilisateur : cartes, couleurs, icônes, interactivité des exercices et
des quiz, responsive, accessibilité.

À consulter avant toute modification du rendu ou de l'interaction d'une page.

Les composants concrets qui implémentent ces règles sont documentés un par un dans
`docs/components/` (voir `docs/components/INDEX.md`).

---

## admin.md

Documentation de l'administration.

---

## exercise_generators.md

Fonctionnement des générateurs automatiques d'exercices.

---

## git_workflow.md

Conventions Git du projet.

---

## changelog.md

Historique des évolutions importantes.

---

# Sources des cours

Toutes les sources officielles sont stockées dans :

docs/sources_cours/

Chaque cours possède son propre dossier.

Exemple :

docs/sources_cours/
└── CESS/
    └── P/
        └── Mathématiques/
            └── MB32/
                └── UAA2/
                    ├── cours.html
                    ├── cours.pdf
                    └── metadata.yaml

Le fichier `cours.html` est toujours la source principale.

Le fichier `cours.pdf` sert uniquement de référence pour vérifier que le contenu n'a pas été perdu.

---

# Scripts

Les scripts d'automatisation sont stockés dans :

scripts/

Ils ne doivent pas être dupliqués.

---

# Objectif du projet

Jury Central a pour objectif de centraliser l'ensemble des cours, exercices, quiz et examens nécessaires à la préparation des Jurys de la Fédération Wallonie-Bruxelles.

Le projet doit être :

- simple à maintenir ;
- facilement extensible ;
- automatisable ;
- cohérent visuellement ;
- compatible avec une génération automatique de contenu à partir des sources officielles.

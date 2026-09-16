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

## EXERCISE_TYPES.md

Format officiel des exercices interactifs (structure JSON générateur → frontend, types
d'exercices, correction, impression).

À consulter avant de créer ou modifier un générateur, ou un composant d'exercice.

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

## content_plan_informatique_francais.md

Plan d'intégration des matières Informatique (AMPCR) et Français (CESS Professionnel) :
inventaire des sources, cartographie, écarts et découpage en tickets d'import proposés.

À consulter avant de créer ou de prendre en charge un ticket d'import pour ces deux
matières.

---

## ai_exercise_engine.md

Moteur générique de génération d'exercices et de correction par IA (API OpenAI, côté
serveur uniquement) : architecture, sécurité (clé API, injection, contexte pédagogique
borné), routes, et comment l'activer pour un nouveau cours.

À consulter avant d'ajouter ce moteur à un nouveau cours, ou de modifier `app/ai/`.

---

## deployment_staging.md

Architecture de l'environnement staging (`jury-central.lodylands.com`) : domaine, nginx,
systemd, port, `.env`, SQLite, logs, commandes de diagnostic, et fonctionnement du script
`scripts/deploy_staging.sh`.

À consulter avant tout déploiement ou diagnostic staging.

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

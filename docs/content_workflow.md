# Jury Central - Organisation du contenu pédagogique

Ce document décrit la manière dont le contenu pédagogique est organisé dans Jury Central.

Il ne décrit ni le processus d'import (voir `IMPORT_WORKFLOW.md`), ni le fonctionnement de l'administration (voir `admin.md`).

---

# Objectif

Chaque UAA doit suivre une structure identique afin de garantir :

- une navigation cohérente ;
- une maintenance simple ;
- une génération automatique du contenu ;
- une expérience identique pour tous les cours.

---

# Hiérarchie

Le contenu est organisé selon la hiérarchie suivante :

```
Niveau
    ↓
Orientation
    ↓
Matière
    ↓
Module
    ↓
UAA
    ↓
Leçons
    ↓
Blocs de contenu
```

Exemple :

```
CESS
└── Professionnel
    └── Mathématiques
        └── MB32
            └── UAA2
```

---

# Une UAA

Une UAA est composée de plusieurs leçons.

Chaque leçon traite une seule notion.

Exemple :

```
UAA2

- Solides
- Perspective cavalière
- Patrons
- Vues coordonnées
- Aires
- Volumes
```

---

# Une leçon

Toutes les leçons suivent la même organisation.

Ordre recommandé :

1. Introduction
2. Théorie
3. Exemples
4. Exercices guidés
5. Exercices générés
6. Quiz
7. Fiche mémo

---

# Les blocs

Chaque partie d'une leçon est composée d'un ou plusieurs blocs.

Types actuellement utilisés :

- markdown
- generated_exercise
- quiz

D'autres types pourront être ajoutés ultérieurement.

---

# Source officielle

Une leçon ne constitue jamais la source de vérité.

La source officielle est toujours :

```
docs/sources_cours/
```

Chaque UAA possède :

```
cours.html
cours.pdf
metadata.yaml
```

Le contenu affiché par Jury Central est issu de ces fichiers.

---

# Exercices

Les exercices peuvent être :

- rédigés ;
- générés automatiquement.

Les générateurs sont documentés dans :

```
docs/exercise_generators.md
```

---

# Quiz

Les quiz sont intégrés directement au contenu pédagogique.

Ils peuvent contenir plusieurs questions.

---

# Fiches mémo

Chaque leçon peut posséder une fiche mémo.

Elle reprend uniquement les éléments essentiels.

---

# Ressources

Une leçon peut également contenir :

- vidéos
- liens externes
- illustrations
- graphiques
- fichiers PDF

Ces ressources restent facultatives.

---

# Objectif à long terme

À terme, l'intégration d'une nouvelle UAA doit être entièrement automatique.

Le contenu sera généré à partir de :

- cours.html
- cours.pdf
- metadata.yaml

sans intervention manuelle sur la structure du site.
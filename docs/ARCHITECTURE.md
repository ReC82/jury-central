# Jury Central - Architecture

Ce document décrit l'architecture technique du projet.

Il ne doit contenir que des informations validées et réellement implémentées.

Aucune hypothèse ne doit être documentée ici.

---

# Objectifs

L'architecture doit permettre :

- l'ajout de nouveaux cours sans modifier le code ;
- l'import automatique des sources officielles ;
- une maintenance simple ;
- une séparation claire entre le contenu et le code ;
- une évolution progressive du projet.

---

# Principes

Le projet est organisé selon les principes suivants :

- une responsabilité par composant ;
- une seule source de vérité pour chaque information ;
- réutilisation maximale du code existant ;
- séparation entre le contenu pédagogique et la logique applicative.

---

# Organisation générale

Le projet est découpé en plusieurs parties :

## Application

Contient le code de l'application.

Elle gère notamment :

- les utilisateurs ;
- les cours ;
- les quiz ;
- les exercices ;
- les examens ;
- l'administration.

---

## Documentation

Toute la documentation technique est stockée dans :

```
docs/
```

---

## Sources officielles

Les sources des cours sont stockées dans :

```
docs/sources_cours/
```

Elles sont organisées par :

```
CESS
└── P
    └── Mathématiques
        ├── MB32
        ├── MQ32
        └── MQ34
```

Chaque UAA contient :

```
UAAx/
├── cours.html
├── cours.pdf
└── metadata.yaml
```

Le contenu de ce dossier est considéré comme immuable.

---

## Scripts

Les scripts d'automatisation sont stockés dans :

```
scripts/
```

Ils servent notamment à :

- importer les sources ;
- générer les métadonnées ;
- automatiser les tâches répétitives.

---

# Architecture du contenu

Le contenu pédagogique est indépendant du code.

L'objectif est de pouvoir intégrer une nouvelle UAA sans modifier l'application.

---

# Import des cours

L'import d'un cours repose sur :

1. les fichiers présents dans `docs/sources_cours`
2. les métadonnées de l'UAA
3. le workflow décrit dans `IMPORT_WORKFLOW.md`

---

# État actuel

Cette documentation sera complétée progressivement au fur et à mesure du développement.

Ne documenter ici que ce qui est réellement implémenté.
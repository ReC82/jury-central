# Jury Central - Administration

Ce document décrit le rôle de l'interface d'administration.

L'administration permet de gérer le contenu existant.

La création complète des cours est réalisée automatiquement à partir des sources officielles.

---

# Objectif

L'administration est destinée à :

- corriger un contenu ;
- compléter un contenu ;
- gérer les utilisateurs (à terme) ;
- gérer les quiz ;
- gérer les exercices ;
- effectuer des opérations de maintenance.

Elle n'est pas destinée à créer manuellement un cours complet.

---

# Accès

Configurer dans le fichier `.env` :

- ADMIN_USERNAME
- ADMIN_PASSWORD
- SECRET_KEY

Démarrer ensuite l'application.

Accès :

```
/admin/login
```

---

# Authentification

L'administration est protégée.

Toutes les routes `/admin/*` nécessitent une authentification.

---

# Contenu

L'administration permet de gérer :

- les matières ;
- les modules ;
- les UAA ;
- les leçons ;
- les blocs de contenu.

---

# Blocs disponibles

Types actuellement pris en charge :

- markdown
- generated_exercise
- quiz

D'autres types pourront être ajoutés progressivement.

---

# Quiz

L'administration permet :

- créer un quiz ;
- modifier un quiz ;
- supprimer un quiz ;
- importer un quiz depuis un fichier CSV.

Le fonctionnement détaillé des quiz est documenté dans :

```
docs/exercise_generators.md
```

---

# Exercices générés

L'administration permet :

- choisir un générateur ;
- configurer sa difficulté ;
- tester son fonctionnement.

Les générateurs sont documentés dans :

```
docs/exercise_generators.md
```

---

# Import des cours

Les cours ne sont plus créés depuis l'administration.

Le workflow officiel est décrit dans :

```
docs/IMPORT_WORKFLOW.md
```

Une fois une UAA importée, l'administration permet uniquement d'effectuer des corrections ponctuelles.

---

# Publication

Une UAA peut être :

- publiée ;
- dépubliée.

Une UAA non publiée n'est pas visible par les étudiants.

---

# Validation

L'administration vérifie notamment :

- les champs obligatoires ;
- l'unicité des slugs ;
- la cohérence de la hiérarchie.

---

# Bonnes pratiques

Utiliser l'administration uniquement pour :

- corriger une erreur ;
- compléter un contenu ;
- importer un quiz ;
- tester un générateur.

Éviter de créer manuellement une UAA complète.

Le contenu officiel doit toujours provenir des sources présentes dans :

```
docs/sources_cours/
```

---

# Évolutions prévues

L'administration évoluera progressivement.

À terme, elle permettra notamment :

- gérer les utilisateurs ;
- suivre la progression des étudiants ;
- gérer les examens ;
- visualiser les statistiques ;
- corriger les contenus importés automatiquement.
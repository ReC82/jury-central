# Panneau admin — Jury Central

## Accès

1. Configurer `ADMIN_USERNAME` et `ADMIN_PASSWORD` dans `.env` (voir `.env.example`) —
   c'est l'unique compte admin, il n'y a pas de gestion multi-utilisateurs.
2. Démarrer le serveur : `uvicorn app.main:app --reload`.
3. Ouvrir http://127.0.0.1:8000/admin/login et se connecter avec ces identifiants.

L'authentification repose sur une session cookie signée (`SECRET_KEY` dans `.env`), sans
hachage de mot de passe côté base — les identifiants viennent uniquement des variables
d'environnement, comparés en temps constant (`hmac.compare_digest`). Toutes les routes
`/admin/*` sont protégées, sauf `/admin/login`. Se déconnecter via `/admin/logout` ou le
bouton "Se déconnecter" du tableau de bord.

## Fonctionnalités disponibles

Depuis `/admin/dashboard` :

- **Compteurs** : nombre de matières, modules, UAA en base.
- **Navigation en lecture seule** : Matières (`/admin/subjects`) → Modules
  (`/admin/subjects/{id}`) → UAA (`/admin/modules/{id}`) → Blocs de leçon
  (`/admin/uaa/{id}`). Il n'existe **pas** de formulaire pour créer/modifier/supprimer une
  matière, un module ou une UAA — seul le contenu des UAA (les `LessonBlock`) est éditable.
- **CRUD complet sur les blocs de leçon** (`LessonBlock`), depuis la page d'une UAA :
  - Créer un bloc (`+ Ajouter un bloc`).
  - Modifier un bloc (titre, type, contenu, position, publié).
  - Supprimer un bloc (confirmation JS avant envoi).
- **Formulaire unique multi-type** (`admin_block_form.html`) qui s'adapte selon le type
  choisi dans le `<select>` :
  - `markdown` / `youtube` / `image` / `pdf` / `exercise` → champ "Contenu" (texte libre).
  - `generated_exercise` → fieldset dédié : générateur (liste des générateurs enregistrés
    dans `generators/registry.py`), difficulté par défaut (1-3), nombre d'exercices à
    afficher, tags pédagogiques (séparés par des virgules).
  - `quiz` → fieldset dédié : question, 4 champs de réponse + case radio pour désigner la
    bonne réponse, explication. Validation serveur : question obligatoire, au moins 2
    réponses non vides, la réponse cochée doit correspondre à un champ rempli (sinon `400`).
  - Champs communs à tous les types : **position** (ordre d'affichage dans l'UAA, entier
    libre — pas de réorganisation automatique des autres blocs) et **publié** (case à
    cocher ; seuls les blocs publiés apparaissent sur la page publique de l'UAA).

## Limites connues

- **Pas de gestion des matières/modules/UAA** dans l'admin : leur création passe
  uniquement par `app/seed.py` (script Python) ou une insertion manuelle en base. À faire
  si le projet a besoin d'ajouter du contenu au-delà du jeu de données de démonstration.
- **Pas de gestion multi-utilisateurs** : un seul compte admin défini par variables
  d'environnement ; pas de rôles, pas d'historique des modifications (qui a changé quoi).
- **Pas d'éditeur WYSIWYG** : le contenu Markdown est un textarea brut (voulu à ce stade,
  cf. consigne initiale).
- **Pas de prévisualisation** avant publication : il faut ouvrir la page publique dans un
  autre onglet pour voir le rendu réel d'un bloc.
- **Pas de protection CSRF** sur les formulaires admin (acceptable pour un compte unique en
  usage interne, mais à revoir avant toute exposition plus large).
- **Types `image`, `pdf`, `exercise` non implémentés** : sélectionnables dans le formulaire
  mais sans champs dédiés ni rendu public particulier (juste un textarea générique côté
  admin, et un message « type non pris en charge » côté page publique).
- **Position en doublon possible** : rien n'empêche d'attribuer la même position à deux
  blocs (l'ordre d'affichage suit alors l'ordre d'insertion en base pour les valeurs
  égales).

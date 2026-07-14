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
- **Navigation** : Matières (`/admin/subjects`) → Modules (`/admin/subjects/{id}`) → UAA
  (`/admin/modules/{id}`) → Blocs de leçon (`/admin/uaa/{id}`).
- **CRUD complet à tous les niveaux de la hiérarchie** — matière, module, UAA, bloc de
  leçon — entièrement depuis l'interface, sans jamais toucher au code ni relancer `seed-db`
  (voir "Gérer la hiérarchie de contenu" ci-dessous).
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
  - `quiz` → fieldset dédié : question, **type de réponse** (« Choix multiple / Vrai-Faux »
    ou « Réponse numérique »), 4 champs de réponse + case radio (mode choix), champ
    « Réponse numérique correcte » (mode numérique — accepte entier, décimal virgule/point,
    ou fraction `a/b`), explication, **groupe de quiz** + **ordre dans le groupe** (voir
    ci-dessous). Validation serveur : question obligatoire, au moins 2 réponses non vides en
    mode choix, réponse numérique valide en mode numérique (sinon `400`).
  - Champs communs à tous les types : **position** (ordre d'affichage dans l'UAA, entier
    libre — pas de réorganisation automatique des autres blocs) et **publié** (case à
    cocher ; seuls les blocs publiés apparaissent sur la page publique de l'UAA).

## Gérer la hiérarchie de contenu (matière → module → UAA)

Depuis cette version, **créer MB32 UAA2 (ou n'importe quelle matière/module/UAA) ne nécessite
plus de modifier `app/seed.py` ni de relancer `seed-db`.** Tout se fait depuis l'admin.

### Matières — `/admin/subjects`

- **Créer** : bouton "+ Nouvelle matière" → nom + slug (le slug se génère automatiquement à
  partir du nom si laissé vide).
- **Modifier** : bouton "Modifier" sur la liste → mêmes champs.
- **Supprimer** : bouton "Supprimer", avec une **confirmation qui indique le nombre exact**
  de modules, UAA et blocs de contenu qui seront supprimés en cascade (calculé côté serveur,
  affiché dans la boîte de dialogue de confirmation du navigateur). Suppression irréversible
  — pas de corbeille.
- La liste affiche, pour chaque matière : nom, slug, et un décompte
  (modules / UAA / blocs) pour visualiser l'impact avant de supprimer.

### Modules — depuis la page d'une matière (`/admin/subjects/{id}`)

- **Créer** : bouton "+ Nouveau module" → code (ex. `MQ32`) + slug (auto-généré depuis le
  code si vide).
- **Modifier** / **Supprimer** : mêmes principes que pour les matières (confirmation avec
  décompte UAA + blocs en cascade).

### UAA — depuis la page d'un module (`/admin/modules/{id}`)

- **Créer** : bouton "+ Nouvelle UAA" → code (ex. `UAA2`), titre, slug (auto-généré depuis
  `{code_module}-{code_uaa}`, ex. `mb32-uaa2`), **position** dans le module (ordre
  d'affichage), et case **"Publiée"**.
- **Modifier** / **Supprimer** : mêmes principes, avec décompte des blocs en cascade à la
  suppression.
- **Publier / dépublier** : une UAA non publiée (`is_published = False`, valeur par défaut
  à la création) n'apparaît **pas** dans la liste publique de son module
  (`/modules/{slug}`), et sa page publique (`/uaa/{slug}`) renvoie une **erreur 404** même
  si on connaît l'URL exacte. Utile pour préparer une UAA sans la montrer aux étudiants
  avant qu'elle soit prête. Les blocs de leçon publiés/non publiés à l'intérieur restent
  gérés indépendamment (une UAA publiée peut très bien n'avoir aucun bloc publié pour
  l'instant).

### Validation serveur (tous niveaux)

- Champs obligatoires (nom/code/titre) : rejetés vides après nettoyage des espaces (`400`).
- Longueur maximale alignée sur les colonnes de la base (nom ≤ 100, code ≤ 20, titre ≤ 150,
  slug ≤ 120 caractères) — évite une erreur de troncature silencieuse en base.
- **Unicité des slugs** vérifiée explicitement avant écriture (message clair, `400`) plutôt
  que de laisser remonter une erreur SQL brute.
- Unicité du **nom** de matière également vérifiée (contrainte déjà présente en base).
- Un slug qui se réduirait à une chaîne vide après nettoyage (ex. nom composé uniquement de
  caractères spéciaux) est rejeté.
- Aucun `eval()` nulle part dans le projet.

### Fil d'Ariane et liens vers le site public

Chaque page admin (liste, formulaire) affiche le fil d'Ariane complet
(Admin → Matière → Module → UAA) et un bouton "Voir la page publique" / "Voir" pointant
directement vers l'URL publique correspondante (nouvel onglet), pour vérifier immédiatement
le rendu après une modification.

### Regrouper plusieurs quiz en un seul parcours (score + une question à la fois)

Donner la **même valeur non vide** au champ « Groupe de quiz » sur plusieurs blocs `quiz`
les affiche comme un **seul** parcours interactif côté public (une question à la fois,
score final, bouton « Recommencer ») plutôt que comme des QCM isolés les uns sous les
autres. Le champ « Ordre dans le groupe » détermine l'ordre des questions au sein du
parcours (indépendamment du champ `position`, qui ne sert qu'à placer le groupe entier
parmi les autres blocs de l'UAA). Laisser le groupe vide (par défaut) garde le
comportement historique : un widget QCM autonome par bloc.

## Tester un générateur d'exercices (debug)

Page `/admin/generators` (lien "Tester un générateur" depuis le tableau de bord) :
sélectionner un générateur enregistré, une difficulté et, optionnellement, un seed, pour
prévisualiser l'exercice produit — énoncé, réponse, étapes de correction, indice,
métadonnées, et le seed utilisé (réutilisable pour reproduire exactement le même exercice).
Outil de debug uniquement : contrairement à l'affichage public, la réponse y est visible
immédiatement (voir `docs/exercise_generators.md`).

## Import de quiz par CSV

Page dédiée : `/admin/quiz` (lien "Importer des quiz (CSV)" depuis le tableau de bord).
Permet de créer plusieurs blocs `quiz` en une fois, sans passer par le formulaire un par un.

Il n'existe pas de table `Quiz`/`Question` dédiée en base — un quiz reste un `LessonBlock`
de type `quiz` dont le contenu JSON (`QuizConfig`) est identique à celui produit par le
formulaire manuel. L'import CSV et le formulaire manuel partagent la même fonction de
validation (`app/quiz.py::build_quiz_config`), donc les mêmes règles s'appliquent aux deux.

### Étapes

1. Cliquer sur **"Télécharger le template CSV"** — télécharge
   `docs/templates/quiz_template.csv`, qui contient l'en-tête attendu et deux exemples déjà
   remplis (utilisables tels quels avec les données de démonstration du seed).
2. Remplir une ligne par question dans un tableur (Excel, LibreOffice, Google Sheets...) et
   exporter en CSV (UTF-8).
3. Sur `/admin/quiz`, choisir le fichier et cliquer **"Importer"**.
4. Le résultat s'affiche immédiatement : nombre de quiz importés, et liste détaillée des
   lignes rejetées (numéro de ligne + raison).

### Colonnes du CSV

| Colonne | Obligatoire | Contenu |
|---|---|---|
| `subject_slug` | Oui | Slug de la matière cible (ex. `mathematiques`) |
| `module_slug` | Oui | Slug du module cible (ex. `mb32`) |
| `uaa_slug` | Oui | Slug de l'UAA cible (ex. `mb32-uaa1`) |
| `title` | Oui | Titre du bloc de leçon (affiché comme titre de section sur la page UAA) |
| `question` | Oui | Texte de la question |
| `choice_1`, `choice_2` | Oui | Au moins 2 réponses non vides requises |
| `choice_3`, `choice_4` | Non | Réponses supplémentaires (jusqu'à 4 au total) ; les cases vides sont ignorées |
| `correct_choice` | Oui | Numéro (1 à 4) du champ `choice_N` contenant la bonne réponse |
| `explanation` | Non | Texte affiché après la réponse de l'étudiant |
| `position` | Non | Ordre d'affichage dans l'UAA ; si vide, calculé automatiquement (après le dernier bloc existant, incrémenté ligne par ligne pour une même UAA dans le même fichier) |
| `is_published` | Non | `oui`/`true`/`1` pour publier immédiatement ; toute autre valeur (ou vide) = non publié |

Les slugs se trouvent dans l'URL des pages publiques correspondantes (ex. `/uaa/mb32-uaa1`
→ `uaa_slug = mb32-uaa1`), ou via la navigation en lecture seule de l'admin.

### Règles de validation

Pour chaque ligne, dans cet ordre :

1. Toutes les colonnes obligatoires doivent être non vides.
2. `subject_slug`, `module_slug`, `uaa_slug` doivent exister **et être correctement
   imbriqués** (le module doit appartenir à la matière indiquée, l'UAA au module indiqué —
   pas seulement exister quelque part en base).
3. `correct_choice` doit être un nombre entre 1 et 4, pointant vers un champ `choice_N` non
   vide.
4. Au moins 2 réponses non vides au total.
5. `position` (si renseigné) doit être un entier.

Si l'en-tête du fichier ne contient pas toutes les colonnes obligatoires, l'import s'arrête
immédiatement avec un message listant les colonnes manquantes (aucune ligne n'est lue).

**Import partiel assumé** : les lignes valides sont importées même si d'autres lignes du même
fichier sont invalides. Chaque ligne rejetée est signalée avec son numéro (ligne 1 = en-tête,
donc la première ligne de données est la ligne 2) et la raison précise. Aucune ligne
invalide n'est importée silencieusement.

### Limites actuelles de l'import

- CSV uniquement (encodage UTF-8, avec ou sans BOM). **Pas de support XLSX pour l'instant** —
  prévu pour une évolution future, non codé à ce stade.
- Une seule bonne réponse par question (pas de QCM à réponses multiples), comme pour le
  formulaire manuel.
- Pas d'aperçu avant import : les lignes valides sont importées directement en base dès la
  soumission du formulaire (pas d'étape de confirmation intermédiaire).
- Pas de mise à jour de quiz existants par CSV : chaque import crée de nouveaux blocs, il ne
  peut pas modifier un quiz déjà importé (à faire manuellement via le formulaire d'édition si
  besoin).

## Limites connues

- **Pas de réorganisation par glisser-déposer** : la position (blocs comme UAA) se règle en
  tapant un nombre, pas visuellement.
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
  blocs, ou à deux UAA d'un même module (l'ordre d'affichage suit alors l'ordre d'insertion
  en base pour les valeurs égales).
- **Suppression définitive, pas de corbeille** : supprimer une matière/module/UAA/bloc est
  irréversible. La confirmation affiche le nombre d'éléments supprimés en cascade, mais il
  n'y a pas de récupération possible après coup (pas de sauvegarde automatique).

## Insérer un graphique interactif dans un bloc markdown

Pas de type de bloc dédié : coller directement le marqueur HTML suivant dans le contenu
Markdown d'un bloc (Python-Markdown préserve le HTML brut tel quel) :

```html
<div class="jc-graph-constant" data-p="3" data-min="-10" data-max="10"></div>
```

`app/static/js/interactive_graph.js` détecte ce marqueur au chargement de la page et y
monte un graphique Plotly interactif (fonction constante $f(x) = p$, curseur pour faire
varier $p$). Le script Plotly (CDN) n'est chargé que sur les pages contenant au moins un tel
marqueur (voir `needs_plotly` dans `app/main.py`), pas globalement.

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
- ai_exercise (génération et correction d'exercices par IA — voir
  `docs/ai_exercise_engine.md`). Pas encore de formulaire admin dédié : se crée aujourd'hui
  via `app/seed.py`, ou en saisissant son JSON (`context_key`, `intro`) dans le champ
  contenu générique du formulaire de bloc.
- editorial_exercise (exercices éditoriaux structurés interactifs — single_choice,
  true_false, short_answer dans cette première tranche, voir
  `docs/editorial_exercise_engine.md`). Pas encore de formulaire admin dédié non plus ;
  `/admin/editorial-exercise-demo` permet de prévisualiser le composant avec un exercice
  fixe par type, indépendamment de tout contenu réel (même principe que
  `/admin/value-table-demo`).

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

# Composants d'exercices interactifs

Le moteur d'exercices interactifs (`value_table`, et d'autres types à venir) est documenté
dans :

```
docs/EXERCISE_TYPES.md
```

`/admin/value-table-demo` permet de prévisualiser le composant `value_table` avec un
exercice fixe, indépendamment de tout générateur — utile pour tester le rendu et la
vérification cellule par cellule sans dépendre d'un générateur réel.

Depuis VS003, `maths.functions.constant_function` produit un exercice `value_table` : le
sélectionner dans `/admin/generators` affiche le même composant interactif que la démo,
avec vérification réelle. Les autres générateurs (ex. `maths.equations.linear_equation`)
continuent d'utiliser l'ancien affichage (énoncé + réponse).

---

# Banque de questions V1 (ticket #46)

Accès : `/admin/bank` (lien « Banque de questions » du tableau de bord). Code :
`app/v1/bank_admin.py` (logique), `app/v1/routes_admin_bank.py` (routes),
`app/v1/feedback.py` (signalements), `app/v1/ai_usage.py` (usage IA),
`app/v1/generation_control.py` (pause de génération). Tests :
`tests/test_ticket46_admin_bank.py`.

Principe : **aucune suppression physique**. Une question retirée change de statut ;
seules les questions **actives** sont proposées aux élèves.

## Par module (`/admin/bank`)

- questions par statut (active, archivée, signalée, invalide, obsolète, à revoir),
  questions signalées et « à contrôler » ;
- rating empirique min / médian / max (questions déjà mesurées, ticket #45) ;
- tentatives (`times_served`) et réussite moyenne (`times_correct / times_served`) ;
- génération IA ACTIVE / PAUSED, avec bouton pour basculer ;
- questions générées par IA / importées, questions réutilisées (servies dans au moins
  2 sessions) et nombre de passages en session ;
- usage IA du mois et total : appels, questions générées, questions corrigées, jetons,
  coût **estimé** (tarifs `AI_COST_INPUT_PER_MILLION` / `AI_COST_OUTPUT_PER_MILLION`,
  USD par million de jetons, défauts 1,25 / 10 — une estimation, pas une facture).
  L'usage est compté depuis l'installation du ticket #46 (pas de reprise de l'historique).

« À contrôler » = statut « signalée » ou « à revoir », ou au moins un signalement élève
non traité.

## Questions (`/admin/bank/questions`)

Filtres : module, mini-cours, type, statut, rating min/max, texte de l'énoncé ou numéro,
« à contrôler ». Pagination par 50.

Détail d'une question :

- **versions** (contenu JSON de chacune, nombre de passages en session) ;
- **modifier** : le JSON de la version courante est éditable ; l'enregistrement crée une
  **nouvelle version** (jamais de modification en place), vérifiée par le registre des
  types (#40). Le type de question ne change pas. Les sessions passées gardent la version
  qu'elles ont servie ;
- **statut** : activer/réactiver, archiver, marquer signalée / invalide / obsolète / à
  revoir ;
- **régénérer une variante** : un appel IA crée une nouvelle question du même type et du
  même mini-cours (mêmes validations que toute génération), au statut « à revoir » —
  jamais servie avant activation. Indisponible pour FSE (banque rédigée à la main), MC38,
  les questions liées à un document source, les types non générables, et quand la
  génération du module est en pause ;
- **signalements** de la question, à marquer traités (ou rouvrir).

## Visuels (`/admin/bank/assets`, ticket #48)

Liste de tous les visuels (assets) de la banque : aperçu, nature (photo réelle,
illustration générée, schéma technique), origine, auteur, licence, lien source, statut, et
les questions qui l'utilisent. La fiche d'une question montre aussi les visuels de sa
version courante.

- **Marquer incorrect** (motif facultatif, case « demander une régénération / un
  remplacement ») : le visuel passe « invalide » et **toutes les questions qui
  l'utilisent ne sont plus proposées** dans les nouvelles sessions. Les sessions passées
  ne changent pas.
- **Réactiver** : remet le visuel en service (et ses questions dans le tirage).
- **Régénération** : seulement pour un visuel généré par IA dont la consigne est
  conservée, et jamais automatiquement : commande manuelle sur le serveur,
  `python -m app.v1.assets list-pending` puis `python -m app.v1.assets regenerate`
  (appel IA réel). Le nouveau fichier devient un nouveau visuel ; chaque question
  concernée reçoit une nouvelle version qui l'utilise. Une photo ou un schéma signalé se
  remplace manuellement (nouveau fichier livré par un ticket).
- Modifier une question visuelle (nouvelle version) conserve son image.

Les élèves peuvent signaler « image incorrecte » depuis les résultats (voir ci-dessous).

## Signalements (`/admin/bank/feedback`)

Les élèves signalent une question depuis la page de résultats d'une session (« Signaler
un problème sur cette question ») : trop facile, trop difficile, ambiguë, question ou
correction incorrecte, image incorrecte, réponse contestable, autre — avec un commentaire
facultatif. Le signalement vise la version exactement servie. Il ne change jamais le
statut de la question automatiquement : l'admin décide.

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
# Ticket #21 — Interactivité : classification et ordering dans les exercices éditoriaux

**Date** : 2026-09-16
**Branche** : `feature/21-classification-ordering`
**Ticket GitHub** : #21 « Interactivité — ajouter classification et ordering aux exercices
éditoriaux »
**Fait suite à** : `docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` (socle
`editorial_exercise`, première tranche de types)

---

## 1. Résumé

Extension du socle générique `editorial_exercise` (ticket #17) avec deux nouveaux types de
correction locale déterministe : `classification` (classer des éléments dans des
catégories) et `ordering` (remettre des éléments dans le bon ordre). Migration réelle de 4
des 12 exercices de MC01 (Ex1, Ex2, Ex9, Ex11) vers ces nouveaux blocs structurés, sans
aucune modification de leur contenu pédagogique. Les 8 exercices restants (3, 4, 5, 6, 7,
8, 10, 12) sont strictement inchangés.

Interaction 100 % au clic (aucun glisser-déposer requis), correction toujours serveur via
la route AJAX générique existante, jamais de solution dans le HTML avant vérification. Le
point le plus délicat du ticket — comment faire en sorte qu'un **staging déjà seedé**
(donc déjà en possession de l'ancien texte Markdown des exercices 1/2/9/11) se mette
réellement à jour au prochain `seed-db`, sans `reset-db` — est résolu et testé
explicitement (§ 6).

**RUFF_NOUVELLES_PAR_#21 = 0**, **PYTEST = 269 passed** (241 + 28 nouveaux).

---

## 2. Architecture : nouveaux types

`app/editorial_exercise.py` — `EditorialExerciseItem` gagne 5 champs, jamais présents dans
`to_public_dict()` avant correction pour les deux qui portent la solution :

```
categories: list[str]          # classification — public
elements: list[str]            # classification — public
correct_categories: list[int]  # classification — privé, un index de catégorie par élément
order_items: list[str]         # ordering — public (ordre de présentation initial)
correct_order: list[int]       # ordering — privé, permutation des index de order_items
```

**Validation** (`__post_init__`, échoue tôt à la construction directe — utilisée par
`app/seed.py` et les tests) :
- `classification` : au moins 2 catégories, au moins 2 éléments, `correct_categories` de
  même longueur que `elements`, chaque valeur dans les bornes de `categories`.
- `ordering` : au moins 2 éléments, `correct_order` doit être une permutation valide des
  index de `order_items` (mêmes valeurs, sans doublon, bonne longueur).

**Correction** (`check()`) — reçoit désormais `submitted: Any` (`str` pour les 3 types du
ticket #17, `list[int]` pour les 2 nouveaux) :
- `classification` : réponse = liste d'index de catégorie, un par élément, dans l'ordre de
  `elements`. Comparaison stricte à `correct_categories` — pas de note partielle,
  cohérent avec le fonctionnement binaire des autres types du socle.
- `ordering` : réponse = permutation des index de `order_items` proposée par l'étudiant.
  Comparaison stricte à `correct_order`. Une réponse qui n'est pas une permutation valide
  (mauvais type, mauvaise longueur, doublon, valeur hors bornes) est traitée comme
  **incorrecte**, jamais comme une exception serveur.

`correct_answer_display()` génère un texte Markdown (liste à puces pour classification,
liste numérotée pour ordering), rendu en HTML par `render_markdown()` comme les autres
types — aucun code de rendu spécifique ajouté côté route ou template.

`to_json()`/`from_json()` étendus symétriquement ; `from_json()` reste tolérant (un item
malformé est ignoré, jamais une exception qui casserait la page publique).

---

## 3. Route (`app/practice.py`)

`VerifyEditorialExerciseRequest.answer` passe de `str` à `Any` :

```python
class VerifyEditorialExerciseRequest(BaseModel):
    exercise_id: str
    answer: Any
```

Rétrocompatible : les types existants continuent d'envoyer une chaîne, Pydantic ne
contraint plus le type côté schéma — la validation de forme se fait désormais dans
`EditorialExerciseItem.check()`, par type. Aucune autre modification de route ni de
modèle de données (conforme à la recette d'extension documentée dans
`docs/editorial_exercise_engine.md`, § « Étendre le socle »).

---

## 4. UX : classification et ordering

Contrainte explicite du ticket : pas de glisser-déposer exclusif, utilisable au clic
comme au clavier/tactile. `app/static/js/editorial_exercise.js` :

- **`buildClassificationControl`** : un groupe de boutons (un par catégorie) sous chaque
  élément à classer. Cliquer un bouton le met en surbrillance (`.active`) parmi ses
  voisins et enregistre le choix ; le bouton « Vérifier » ne s'active que lorsque tous les
  éléments ont une catégorie choisie (modifiable jusqu'à validation). La réponse envoyée
  est la liste des index de catégorie, dans l'ordre de `elements`.
- **`buildOrderingControl`** : une liste `<ol class="list-group-numbered">`, chaque ligne
  avec deux boutons natifs « ↑ »/« ↓ » (`aria-label` explicite nommant l'élément déplacé,
  désactivés en butée haute/basse). Un clic échange la ligne avec sa voisine et
  ré-affiche la liste. « Vérifier » envoie la permutation courante des index de
  `order_items`.

Tous les contrôles sont des `<button type="button">` natifs (focusables, activables au
clavier par Entrée/Espace sans code supplémentaire) et marqués `d-print-none` (mode
impression : énoncé visible, contrôles interactifs masqués — même convention que
`value_table`/`short_answer`/`ai_exercise`). Aucun `<input type="range">`, aucune librairie
de glisser-déposer, aucune dépendance ajoutée.

`submitEditorialAnswer` envoie désormais `answer` tel quel (liste) pour ces deux types,
au lieu de le forcer en chaîne (`String(answer)`, conservé pour les types existants) —
seul changement de comportement réseau, rétrocompatible.

---

## 5. Les 4 exercices MC01 migrés

Contenu pédagogique repris mot pour mot de la version Markdown d'origine (voir `git log`
sur `_MC01_EXERCICES_1`/`_MC01_EXERCICES_3` dans `app/seed.py`) — seule la structure
technique change.

| Exercice | Ancien type | Nouveau type | Catégories / ordre correct |
|---|---|---|---|
| Ex1 — Matériel ou logiciel | Markdown | `classification` | Matériel / Logiciel |
| Ex2 — Unité centrale ou périphérique | Markdown | `classification` | Unité centrale / Périphérique |
| Ex9 — Lancement d'un programme | Markdown | `ordering` | Lecture SSD → chargement RAM → exécution CPU → affichage écran |
| Ex11 — Entrée, sortie ou mixte | Markdown | `classification` | Entrée / Sortie / Mixte |

Les 8 exercices restants (3, 4, 5, 6, 7, 8, 10, 12) demandent une réponse rédigée libre
(« explique... », « cite deux composants... ») — ils nécessitent le type `long_answer`
(correction IA), hors périmètre de ce ticket, et restent donc en Markdown, strictement
inchangés (vérifié explicitement par
`test_untouched_exercises_keep_their_exact_original_markdown_text`).

**Réorganisation mineure de l'ordre de présentation** : Ex10 et Ex12 (restés Markdown)
sont désormais regroupés dans un seul bloc, après Ex9 et Ex11 (devenus des blocs
structurés distincts), plutôt qu'intercalés dans l'ordre strict 9-10-11-12 d'origine. Ce
n'est qu'un réordonnancement d'affichage (les 12 exercices restent tous présents, une
seule fois chacun, avec leur numéro d'origine) — pas une modification de contenu.

**MC01_BLOCKS passe de 19 à 23 blocs** (4 nouveaux blocs structurés, et un bloc Markdown
en plus car `_MC01_EXERCICES_3` — qui contenait 4 exercices — est désormais scindé en un
bloc structuré (Ex9), un bloc structuré (Ex11) et un bloc Markdown réduit (Ex10 + Ex12) ;
`_MC01_EXERCICES_1` reste un seul bloc Markdown réduit (Ex3 + Ex4), en plus des deux
nouveaux blocs structurés Ex1/Ex2).

---

## 6. Migration du contenu déjà seedé (staging)

**Problème** : `_seed_uaa()` (mécanisme additif du projet) ne modifie **jamais** le
contenu d'un bloc existant dont le titre correspond déjà à un bloc du seed — il ne fait
que créer les blocs manquants (par titre) et laisser le reste intact, pour ne jamais
écraser un contenu édité depuis l'admin. Un simple changement du texte Python de
`_MC01_EXERCICES_1`/`_MC01_EXERCICES_3`, sans autre précaution, n'aurait donc eu **aucun
effet** sur un staging déjà seedé avant ce ticket : l'ancien bloc (même titre, ancien
texte contenant encore Ex1/Ex2/Ex9/Ex11) serait resté tel quel, et les 4 nouveaux blocs
structurés se seraient ajoutés à côté — doublon, explicitement interdit par le ticket.

**Solution retenue** : les deux blocs Markdown modifiés portent désormais un titre
**différent** de leur version pré-#21 :

| Ancien titre (pré-#21) | Nouveau titre |
|---|---|
| « Architecture d'un PC — Exercices (1/3 : composants et rôles) » | « Architecture d'un PC — Exercices (composants et rôles : suite) » |
| « Architecture d'un PC — Exercices (3/3 : scénario, diagnostic, vocabulaire) » | « Architecture d'un PC — Exercices (diagnostic et vocabulaire : suite) » |

Les deux anciens titres sont listés dans `MC01_OBSOLETE_TITLES` (`app/seed.py`, même
mécanisme déjà utilisé une fois pour nettoyer d'anciens blocs de démonstration MB32 —
`OBSOLETE_DEMO_BLOCK_TITLES`), passé à `_seed_uaa(..., obsolete_titles=MC01_OBSOLETE_TITLES)`
pour l'UAA MC01 :

```python
removed_obsolete += _seed_uaa(
    db, ampcr, MC01_CODE, MC01_TITLE, 1, MC01_BLOCKS, created, kept,
    obsolete_titles=MC01_OBSOLETE_TITLES,
)
```

`_seed_uaa()` retire d'abord, par titre, tout bloc existant dont le titre est dans
`obsolete_titles` — **avant** la passe additive habituelle. Concrètement, au prochain
`seed-db` :

1. **Staging jamais seedé (nouvelle installation)** : les anciens titres n'existent nulle
   part → le retrait est un no-op ; la passe additive insère directement les blocs à jour
   (4 structurés + 2 Markdown aux nouveaux titres).
2. **Staging déjà seedé avant le ticket #21** (cas réel visé) : les deux blocs Markdown
   portant encore l'ancien titre et l'ancien texte sont détectés et **supprimés** ; la
   passe additive insère ensuite les 7 blocs de remplacement (aucun titre en conflit,
   puisque tous nouveaux) — plus aucun texte obsolète, plus aucun doublon.
3. **Tout seed-db ultérieur** (après une première migration réussie, sur n'importe quelle
   base) : les anciens titres n'existent plus nulle part (déjà supprimés à l'étape 2, ou
   jamais présents à l'étape 1) → le retrait redevient un no-op, et les 7 blocs déjà
   présents sont conservés tels quels (jamais réécrits) — idempotence complète, y compris
   pour un contenu MC01 que le formateur aurait édité depuis l'admin entre deux
   `seed-db`.

**Aucun `reset-db` n'est nécessaire ni n'a été exécuté.** Ce scénario exact — un bloc
existant portant l'ancien titre et l'ancien texte, migré par un seul `seed()` — est
reproduit et vérifié par
`test_staging_already_seeded_before_ticket_21_is_migrated_without_reset`
(`tests/test_ticket21_no_regression.py`) : la base de test y est construite à la main avec
les deux anciens blocs Markdown (ancien titre, ancien texte factice), puis `seed()` est
appelé une seule fois ; le test vérifie que les anciens titres ont disparu, que les 4
blocs `editorial_exercise` sont bien présents, et que l'ancien texte factice n'apparaît
plus nulle part sur la page publique. L'idempotence après migration est vérifiée
séparément par `test_seed_is_idempotent_after_migration` (deux appels à `seed()`, aucun
bloc créé ni supprimé au second).

**Procédure de déploiement réelle** (à exécuter par ChatGPT/l'utilisateur après merge,
comme pour les tickets précédents) : `scripts/deploy_staging.sh` puis `seed-db` — exacte
même procédure que pour MC01/MC02/MC03 initialement, aucune étape manuelle
supplémentaire, aucune commande destructive.

---

## 7. Sécurité

Même principe que le reste du socle (`value_table`/`quiz`/`ai_exercise`) :
- Le serveur recharge toujours `EditorialExerciseBlockConfig` depuis `LessonBlock.content`
  avant de corriger — jamais confié au client.
- `to_public_dict()` exclut structurellement `correct_categories` et `correct_order` (
  testé unitairement et au niveau HTTP : ni la page `/uaa/{slug}` ni la réponse JSON avant
  correction ne les contiennent jamais).
- Aucun `eval()`. Aucune comparaison dynamique : `int(x) for x in submitted` avec
  `try/except` explicite, `sorted(...) == list(range(n))` pour valider une permutation.
- Toute réponse malformée (mauvais type, mauvaise longueur, valeurs non entières,
  permutation invalide) est traitée comme une réponse incorrecte — jamais une exception
  qui remonterait une trace serveur au client.

---

## 8. Tests

**Unitaires** (`tests/test_editorial_exercise.py`, +23 tests) : validation de
`classification`/`ordering` (catégories/éléments insuffisants, longueur incohérente,
index hors bornes, permutation invalide), sérialisation/désérialisation (roundtrip),
absence de fuite dans `to_public_dict()` (item et bloc), présence de `categories`/
`elements`/`order_items` publics, correction correcte/incorrecte/incomplète/malformée/
mauvais type pour les deux nouveaux types, id d'exercice inconnu.

**Intégration HTTP** (`tests/test_practice_editorial_routes.py`, +4 tests) : réponse
correcte/incorrecte pour `classification` et `ordering` via la route réelle
`/practice/api/editorial/{block_id}/verify`, garde-fou de non-fuite étendu aux nouvelles
clés (`correct_categories`, `correct_order`).

**Non-régression ticket #21** (`tests/test_ticket21_no_regression.py`, nouveau, 8 tests) :
exactement 4 blocs `editorial_exercise` dans MC01 avec les bons titres, absence de
doublon Markdown pour les 4 exercices migrés, contenu exact des 8 exercices non touchés,
nombre total de blocs MC01 (23), idempotence du seed après migration, **scénario complet
de migration d'un staging pré-#21 sans reset** (§ 6), non-régression MC02/MC03/
Mathématiques.

**Ajustements de tests existants** (conséquence directe et attendue de la migration, pas
une régression) :
- `tests/test_ticket17_no_regression.py::test_mc01_content_is_untouched_by_ticket_17` :
  l'assertion « 0 bloc editorial_exercise dans MC01 » devient « 4 » (docstring du module
  mis à jour pour expliquer le changement).
- `tests/test_informatique_mc01.py::test_mc01_has_twelve_exercises_with_hidden_corrections` :
  l'assertion « au moins 12 occurrences de "Correction :" dans le HTML initial » devient
  « au moins 8 » (les 4 exercices migrés n'affichent plus jamais leur correction dans le
  HTML statique — uniquement via l'appel AJAX de vérification, ce qui est l'amélioration
  de sécurité/pédagogie recherchée par ce ticket, pas une perte de couverture) ; garde-fou
  explicite ajouté (`correct_categories`/`correct_order` absents du HTML).

**Résultat** : `pytest -q` → **269 passed** (241 avant ce ticket + 28 nouveaux), 2
warnings préexistants (dépréciations `httpx`/`anyio`, sans lien avec ce ticket).

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé (`git worktree add
--detach`). **0 nouvelle erreur.**

**Vérification manuelle** (base SQLite temporaire isolée `/tmp/jc_manual_test.db`, jamais
`jury_central.db`, serveur `uvicorn` réel démarré sur un port de test) :
- `GET /uaa/ampcr-mc01` : 200, les 4 blocs `editorial-exercise-block` présents, JSON
  public inspecté champ par champ (`categories`/`elements` pour classification,
  `order_items` pour ordering — jamais `correct_categories`/`correct_order`), les 12
  intitulés d'exercice présents exactement une fois chacun, aucun ancien intitulé Markdown
  des exercices migrés.
- `POST /practice/api/editorial/{id}/verify` testé en conditions réelles pour
  `classification` (Ex1, réponse correcte et incorrecte) et `ordering` (Ex9, réponse
  correcte, incorrecte, et malformée — doublon/longueur incohérente) : réponses HTTP 200
  cohérentes dans tous les cas, correction rendue en HTML (liste à puces / liste
  numérotée) via `render_markdown`.
- `seed()` exécuté deux fois de suite sur la même base réelle : second appel = 0 créé,
  tout conservé (idempotence confirmée hors du cadre des fixtures pytest).
- `GET /uaa/ampcr-mc02`, `/uaa/ampcr-mc03`, `/uaa/mb32-uaa1` : 200, aucune régression.
- `node --check app/static/js/editorial_exercise.js` : syntaxe JS valide.
- `jury_central.db` (fichier de dev local, gitignoré) vérifié inchangé après la session.

**Non vérifié — limite explicite** : comme pour le ticket #18, aucun navigateur ni outil
d'automatisation n'est disponible dans cet environnement serveur — l'interaction réelle au
clic/toucher (boutons de catégorie, boutons monter/descendre) sur un vrai moteur de rendu
n'a pas pu être observée visuellement. Le widget a été vérifié par lecture directe du code
JS, par test de la route serveur qu'il appelle, et par inspection du JSON exact qu'il
reçoit — mais une validation visuelle sur staging (ou DevTools responsive, viewports
360/390/430 px) reste recommandée avant de considérer l'UX entièrement close.

---

## 9. Fichiers modifiés

- `app/editorial_exercise.py` — types `classification`/`ordering` (champs, validation,
  correction, représentation publique, affichage de la bonne réponse).
- `app/practice.py` — `VerifyEditorialExerciseRequest.answer: str → Any`.
- `app/static/js/editorial_exercise.js` — `buildClassificationControl`,
  `buildOrderingControl`, dispatch étendu, envoi de réponse liste (non forcée en chaîne).
- `app/seed.py` — import `EditorialExerciseItem`, `MC01_OBSOLETE_TITLES`, 4 nouvelles
  constantes d'exercice, `_MC01_EXERCICES_1`/`_MC01_EXERCICES_3` réduits (Ex1/Ex2/Ex9/Ex11
  retirés), `MC01_BLOCKS` restructuré (19 → 23 blocs, positions renumérotées), appel
  `_seed_uaa` pour MC01 avec `obsolete_titles=MC01_OBSOLETE_TITLES`.
- `tests/test_editorial_exercise.py`, `tests/test_practice_editorial_routes.py` — tests
  étendus pour les deux nouveaux types.
- `tests/test_ticket21_no_regression.py` — nouveau.
- `tests/test_ticket17_no_regression.py`, `tests/test_informatique_mc01.py` — assertions
  ajustées à la nouvelle réalité de MC01 (voir § 8).
- `docs/editorial_exercise_engine.md` — types pris en charge, UX, route, sécurité, tests,
  « étendre le socle ».
- `docs/changelog.md` — entrée de ticket.
- `docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md` — ce rapport.

---

## Statut

Implémentation, tests et documentation terminés jusqu'au commit + push. **Aucun merge,
aucun déploiement.** En attente de revue et de fusion par ChatGPT, puis d'un déploiement
staging explicitement autorisé (`scripts/deploy_staging.sh` + `seed-db`, voir § 6).

# Ticket #40 — Question Engine V1 : registre extensible des types de questions

**Date** : 2026-09-17
**Branche** : `feature/40-v1-question-engine`

---

## 1. Audit initial

- **`app/ai/schemas.py`** (ticket #23) : `QUESTION_TYPES` (13 types), `QuestionnaireQuestion`
  (dataclass générique tous types), `DETERMINISTIC_QUESTION_TYPES`/
  `CONDITIONALLY_LOCAL_QUESTION_TYPES`/`ALWAYS_SEMANTIC_QUESTION_TYPES` — trois
  frozensets codifiant déjà, de façon implicite, le concept de « mode de correction »
  repris explicitement par ce ticket (`CorrectionMode`).
- **`app/editorial_exercise.py`** (tickets #17/#21/#29) : `EDITORIAL_EXERCISE_TYPES` (8
  types), `EditorialExerciseItem.to_public_dict()`/`check()` — même philosophie
  « jamais la solution avant correction » déjà appliquée manuellement type par type ;
  ce ticket généralise ce principe via `public_payload()` unique pour 26 types.
- **`app/answer_checking.py`** : `text_answer_matches`/`normalize_text` (comparaison
  texte insensible à la casse/accents) et `parse_answer`/`answers_match` (comparaison
  numérique via `fractions.Fraction`, aucun `eval()`) — réutilisés tels quels par
  `app/v1/question_types.py` (`short_answer`, `vocabulary`, `formula`,
  `code_completion`, `numeric`, `calculation`, `graph_reading`), jamais réimplémentés.
- **`app/v1/models.py`** (ticket #38) : `QuestionVersion.schema_version`/`content_json`
  déjà présents comme colonnes dédiées — confirmé qu'aucun champ `schema_version`
  ne doit être dupliqué à l'intérieur de `content_json` (décision documentée, § 3).
  `AssetKind`, `SourceDocumentVersion` réutilisés tels quels (aucun second vocabulaire
  d'assets/documents).
- **`docs/EXERCISE_TYPES.md`** : document du moteur legacy `generators/` (Numeric, Text,
  Multiple Choice, True/False, Matching, Drag & Drop, Graph...) — même direction
  conceptuelle, aucun conflit de nommage machine (ce document ne fixe pas de `type_id`
  JSON), non touché par ce ticket.
- **Dépendance disponible** : `pydantic` (déjà utilisé directement dans `app/admin.py`/
  `app/practice.py` via FastAPI) — choisi pour `content_model`/`answer_model` plutôt que
  d'introduire un système de schéma maison ou une nouvelle dépendance.

Conclusion : aucun besoin d'ajouter de dépendance externe. Vocabulaire aligné sur
l'existant partout où le concept est déjà partagé (§ 2, décisions).

---

## 2. Décisions de conception

Détaillées et justifiées dans `docs/question_engine_v1.md`. Résumé :

1. **Pas de `single_choice` séparé** (consigne explicite) — `multiple_choice` avec
   `min_selections=max_selections=1` couvre ce cas. Déviation assumée par rapport aux
   vocabulaires existants (#17/#23), qui gardent `single_choice` pour leur périmètre déjà
   déployé, non migré par ce ticket.
2. **`true_false` reste séparé** de `multiple_choice` — vocabulaire Vrai/Faux figé,
   cohérent avec les deux vocabulaires existants.
3. **`calculation` distinct de `numeric`** — même mécanique de comparaison tolérante
   (`_check_numeric_value`, factorisée, jamais dupliquée), deux `type_id` séparés comme
   demandé.
4. **`content_json` n'embarque jamais `schema_version`** — `QuestionVersion.
   schema_version` (#38) reste l'unique source de vérité.
5. **Composition (`response_mode`) plutôt que prolifération de sous-types** pour
   `graph_reading`, `image_identification`, `code_reading` — un seul `type_id`, un champ
   qui sélectionne la forme de réponse attendue (numeric/text/multiple_choice ou
   choice/text).
6. **`QuestionTypeSpec.check_answer` retourne `None`** (jamais une exception) pour
   signaler qu'une correction sémantique est nécessaire — le ticket #44 route vers l'IA
   sur ce signal, ce module ne l'exécute jamais lui-même.

---

## 3. Architecture

`app/v1/question_engine.py` (289 lignes) — abstraction centrale :
- `Capability`, `CorrectionMode`, `SourceDocumentRequirement` (enums).
- `AssetContract` (dataclass frozen, `requires_asset` dérivé de `min_assets`).
- `QuestionTypeSpec` (dataclass frozen) — LE CONTRAT par type.
- `QuestionTypeRegistry` — `register()`/`get()`/`list_types()`, refuse un `type_id`
  dupliqué.
- API publique : `get_question_type`, `list_question_types`, `validate_content`,
  `validate_answer`, `public_payload`, `check_answer`.

`app/v1/question_types.py` (1419 lignes) — les 26 types, chacun avec :
- un modèle Pydantic `*Content` (validation structurelle, `@model_validator` pour les
  invariants inter-champs — ex. permutation valide pour `ordering`, couverture exacte
  des zones pour `diagram_labeling`) ;
- un modèle Pydantic `*Answer` ;
- une fonction `to_public` listant explicitement les champs publics ;
- un `check_answer` (ou `None` pour les types toujours `SEMANTIC_AI`) ;
- un enregistrement dans `QUESTION_TYPE_REGISTRY` avec son `AssetContract`/
  `SourceDocumentRequirement`/`capabilities`.

Aucun `if/elif` dispersé : toute consultation passe par le registre.

---

## 4. Fichiers

- `app/v1/question_engine.py` (nouveau)
- `app/v1/question_types.py` (nouveau)
- `docs/question_engine_v1.md` (nouveau)
- `docs/claude-reports/2026-09-17_ticket-40_question-engine-v1.md` (ce rapport)
- `tests/test_ticket40_question_engine.py` (nouveau, 282 tests)

Aucune modification de `app/editorial_exercise.py`, `app/ai/schemas.py`,
`app/v1/models.py`, `app/main.py`, `app/practice.py` — ce ticket pose uniquement le
contrat, sans brancher aucune route existante dessus (conforme au périmètre : « Ce
ticket doit fournir LE CONTRAT »).

---

## 5. Tests

`tests/test_ticket40_question_engine.py` (282 tests, dont de nombreux paramétrés sur
les 26 types) couvre explicitement :

- Le registre contient exactement les 26 types attendus ; `type_id` uniques (un
  enregistrement en double lève une erreur).
- `schema_versions` : version 1 supportée par tous ; version inconnue refusée ; type
  inconnu refusé.
- Contenu minimal valide accepté et contenu vide refusé, pour les 26 types.
- **Anti-fuite systématique** : un « canari » textuel injecté dans chaque champ privé
  d'un contenu minimal par type, puis vérifié absent du JSON de `public_payload()` —
  pour les 26 types, pas un échantillon. Complété par une vérification de la liste des
  clés privées connues (`correct_*`, `accepted_*`, `rubric`, `expected_*`, etc.),
  également absentes du payload pour les 26 types.
- `multiple_choice` : nombre variable d'options (2 à 6 testées), réponse unique
  (min=max=1), réponses multiples (min=2, max=3), rejet d'un `correct_option_ids`
  incohérent avec min/max.
- `classification` : nombre variable de catégories (5 testées, pas limité à 2/3).
- `ordering`, `matching` : correction locale, rejet d'une permutation invalide.
- `numeric` : tolérance absolue, tolérance relative, unité obligatoire, confirmation
  qu'une entrée type « injection de code » n'est jamais interprétée.
- `short_answer`/`vocabulary` : correction locale si `accepted_answers`, bascule
  sémantique (`None`) sinon.
- `long_answer`/`diagnostic`/`procedure`/`troubleshooting` : toujours `None` (jamais de
  correction locale).
- `document_analysis` : référence une vraie `SourceDocumentVersion` créée via
  `app.v1.models.create_source_document` (ticket #38) ; rejet d'un identifiant ≤ 0.
- `source_comparison` : au moins deux documents requis.
- `image_identification` : `asset_contract.requires_asset is True`.
- `hotspot` : coordonnées bornées à [0,1], résolution de points normalisés en
  identifiants de zone, préférence pour les IDs explicites.
- `diagram_labeling`, `table_completion` : correction locale + bascule sémantique si
  cellule non couverte par `accepted_answers`.
- `graph_reading`/`graph_interaction` : les trois `response_mode`, tolérance sur points
  placés et sur un jeu de paramètres.
- `code_reading`/`code_completion` : **confirmation active qu'aucune exécution n'a
  lieu** (un `code` contenant une commande shell réelle est soumis, un test vérifie
  qu'aucun effet de bord — création de fichier — ne s'est produit) ; analyse **AST**
  (pas une simple recherche de sous-chaîne, qui aurait été faussée par les docstrings
  mentionnant `eval()`/`exec()` en prose) confirmant l'absence de tout appel réel à
  `eval`/`exec` dans les deux modules.
- Compatibilité `QuestionVersion` (#38) : création réelle via `create_question`,
  relecture depuis la base, revalidation du `content_json` rechargé.
- `capabilities`/`correction_mode`/etc. sérialisables en JSON pour les 26 types.
- Aucune spécialisation par matière : aucun modèle de contenu ne référence
  `subject`/`module`/`module_id` ; un même schéma `classification` validé avec un
  scénario Informatique et un scénario Français ; scénarios dédiés `document_analysis`/
  `source_comparison` en Français avec de vraies `SourceDocumentVersion`.
- Chaque `answer_model` accepte une forme « vide » (état avant réponse), à l'exception
  documentée de `true_false` (un booléen n'a pas d'état vide sensé).

Aucun appel OpenAI réel : `check_answer` ne fait jamais l'appel IA lui-même, il retourne
`None` pour le signaler.

---

## 6. Résultat pytest

```
790 passed, 2 warnings in 117.10s
```

(508 avant ce ticket + 282 nouveaux, `tests/test_ticket40_question_engine.py`). Les 2
warnings sont préexistants (httpx/anyio), sans lien avec ce ticket.

---

## 7. Résultat Ruff

```
Found 36 errors.
```

Identique à la base `develop` (comparé via un worktree isolé). **0 nouvelle erreur.**
Ajustements mineurs pendant le développement : import inutilisé retiré, tri d'imports,
deux simplifications de conditions (`SIM102`/`SIM103`) dans `_check_numeric_value`.

---

## 8. `git diff --check`

```
$ git diff --check --cached
(aucune sortie, exit code 0)
```

---

## 9. Non-régression

Aucune route existante modifiée, aucun modèle existant modifié — le moteur
`app.editorial_exercise` (MC01/MC02/MC03) reste inchangé et opérationnel. La banque de
questions V1 n'est pas migrée par ce ticket (explicitement hors périmètre).

---

## 10. Limites

- **Aucun widget frontend construit** — le contrat expose `capabilities` pour qu'un
  futur renderer choisisse son composant, mais aucun composant JS/Plotly/KaTeX n'est
  livré ici (non nécessaire à la validation du contrat, entièrement vérifiée côté
  Python/Pydantic).
- **`schema_versions` figé à `{1}` pour tous les types** — le mécanisme de migration
  inter-versions n'est que structurel (le registre sait REFUSER une version inconnue),
  aucune logique de migration 1→2 n'est construite (non demandée : « ne crée pas encore
  une usine complexe »).
- **Correction locale de `table_completion`/`graph_interaction`/`hotspot` simplifiée** :
  tout-ou-rien (une cellule/un point manquant invalide toute la réponse) — le calcul
  d'un score partiel appartient à #44/#45.
- **`graph_config`/`code` sont des données opaques** (dict libre / texte) au niveau de
  ce contrat — leur rendu (Plotly, coloration syntaxique) est repoussé, comme demandé.
- **Pas de génération de distracteurs** pour `multiple_choice` — explicitement hors
  périmètre (« relève du générateur #43 »).

---

## 11. Prochaines dépendances

- **#41 (banque/sélection)** : consommera `list_question_types()`/`get_question_type()`
  pour filtrer par capacité/mode de correction lors de la sélection.
- **#43 (génération batch)** : générera des `content_json` conformes à
  `validate_content()`, y compris les distracteurs `multiple_choice`.
- **#44 (correction globale)** : appellera `check_answer()` pour la correction locale et
  routera vers l'IA batch exactement quand `check_answer()` retourne `None`.
- **#47 (Français final)** : `document_analysis`/`source_comparison` sont prêts,
  référencent déjà `SourceDocumentVersion` (#38) sans duplication de texte.
- **#48 (visuels avancés)** : `graph_reading`/`graph_interaction`/`hotspot`/
  `diagram_labeling`/`image_identification` ont leur contrat complet ; seul le rendu
  reste à construire.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` : 790 passed. Ruff : 36
erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI réel. Aucune
modification de la DB staging. Prêt pour commit/push. **Aucun merge, aucun déploiement.**

# Jury Central — Question Engine V1 (ticket #40)

Registre extensible des types de questions : LE CONTRAT que consommeront la banque
(#41), l'autosave (#42), la génération (#43), la correction (#44) et l'admin (#46).
Code : `app/v1/question_engine.py` (abstraction centrale) et `app/v1/question_types.py`
(les 26 types V1).

---

# 1. Philosophie

- **Un seul vocabulaire par concept partagé** — les identifiants de type déjà utilisés
  par `app.ai.schemas.QUESTION_TYPES` (ticket #23) et
  `app.editorial_exercise.EDITORIAL_EXERCISE_TYPES` (tickets #17/#21/#29) sont repris
  tels quels ici (`short_answer`, `long_answer`, `fill_blank`, `matching`,
  `classification`, `ordering`, `numeric`, `diagnostic`, `procedure`, `vocabulary`) —
  jamais un second nom pour le même concept.
- **Composition plutôt que prolifération de types** — `graph_reading`,
  `image_identification`, `code_reading` exposent un champ `response_mode`
  (`numeric`/`text`/`multiple_choice` ou `choice`/`text`) plutôt que trois types
  séparés par forme de réponse.
- **Pas de spécialisation par matière** — les mêmes classes Pydantic valident un
  exercice de classification Informatique (matériel/logiciel) et un exercice de
  classification Français (registre de langue) sans aucune branche conditionnelle sur
  la matière (voir `tests/test_ticket40_question_engine.py`, tests dédiés).
- **Pas de `if/elif` dispersé** — toute l'application interroge le registre
  (`get_question_type`, `validate_content`, `validate_answer`, `public_payload`,
  `check_answer`) au lieu de tester `question_type == "..."` dans chaque route/service.
- **Sécurité structurelle** — `public_payload()` liste EXPLICITEMENT les champs publics
  de chaque type (jamais une copie amputée des champs privés) : un nouveau champ de
  solution ajouté à un type ne peut donc jamais fuiter par oubli.

---

# 2. Le registre (`app/v1/question_engine.py`)

```python
QUESTION_TYPE_REGISTRY: QuestionTypeRegistry
```

Chaque entrée (`QuestionTypeSpec`) expose :

| Champ | Rôle |
|---|---|
| `type_id` | identifiant stable, unique dans le registre |
| `schema_versions` | ensemble des versions de `content_json` supportées (aujourd'hui `{1}` pour tous) |
| `correction_mode` | `LOCAL` / `SEMANTIC_AI` / `HYBRID` |
| `capabilities` | ensemble de `Capability` — ce que le frontend doit savoir afficher |
| `asset_contract` | `AssetContract(allowed_kinds, min_assets, max_assets)` |
| `source_document_requirement` | `NONE` / `OPTIONAL` / `REQUIRED` / `MULTIPLE` |
| `content_model` / `answer_model` | classes Pydantic (validation + (dé)sérialisation) |
| `to_public` | fonction `content → dict` public, jamais l'inverse d'un retrait |
| `check_answer` | fonction `(content, answer) → bool`, ou `None` si toujours sémantique |

API publique (Python, pas nécessairement des routes HTTP) :

```python
get_question_type(type_id) -> QuestionTypeSpec
list_question_types() -> list[QuestionTypeSpec]
validate_content(type_id, schema_version, content_json) -> BaseModel
validate_answer(type_id, schema_version, answer_json) -> BaseModel
public_payload(type_id, schema_version, content_json) -> dict
check_answer(type_id, schema_version, content_json, answer_json) -> bool | None
```

`validate_content`/`validate_answer` lèvent `QuestionEngineError` (type ou version
inconnue) ou `ContentValidationError` (JSON structurellement invalide — message sur la
forme uniquement, jamais sur la solution). `check_answer` retourne `None` quand ce
contenu précis nécessite une correction sémantique — signal pour #44, jamais exécuté par
ce module.

---

# 3. Liste complète des 26 types

| # | `type_id` | `correction_mode` | Capacités clés |
|---|---|---|---|
| 1 | `multiple_choice` | LOCAL | MULTI_SELECT |
| 2 | `true_false` | LOCAL | — |
| 3 | `short_answer` | HYBRID | TEXT_INPUT |
| 4 | `long_answer` | SEMANTIC_AI | TEXT_INPUT |
| 5 | `fill_blank` | LOCAL | TEXT_INPUT |
| 6 | `matching` | LOCAL | DRAG_DROP |
| 7 | `classification` | LOCAL | DRAG_DROP |
| 8 | `ordering` | LOCAL | ORDERABLE |
| 9 | `numeric` | LOCAL | TEXT_INPUT |
| 10 | `diagnostic` | SEMANTIC_AI | TEXT_INPUT |
| 11 | `procedure` | SEMANTIC_AI | TEXT_INPUT |
| 12 | `vocabulary` | HYBRID | TEXT_INPUT |
| 13 | `calculation` | LOCAL | TEXT_INPUT |
| 14 | `formula` | HYBRID | FORMULA, TEXT_INPUT |
| 15 | `graph_reading` | HYBRID | GRAPH, TEXT_INPUT |
| 16 | `graph_interaction` | LOCAL | GRAPH, DRAG_DROP |
| 17 | `diagram_labeling` | LOCAL | IMAGE, DRAG_DROP |
| 18 | `image_identification` | HYBRID | IMAGE, MULTI_SELECT, TEXT_INPUT |
| 19 | `hotspot` | LOCAL | IMAGE, HOTSPOT |
| 20 | `table_completion` | HYBRID | TABLE, TEXT_INPUT |
| 21 | `document_analysis` | SEMANTIC_AI | DOCUMENT, TEXT_INPUT |
| 22 | `source_comparison` | SEMANTIC_AI | DOCUMENT, TEXT_INPUT |
| 23 | `timeline` | LOCAL | ORDERABLE |
| 24 | `code_reading` | HYBRID | CODE, TEXT_INPUT |
| 25 | `code_completion` | HYBRID | CODE, TEXT_INPUT |
| 26 | `troubleshooting` | SEMANTIC_AI | TEXT_INPUT |

Tous les types portent en plus `LOCAL_GRADING` et/ou `SEMANTIC_GRADING` selon leur
`correction_mode` (voir tableau des capacités, § 4).

## 3.1 Décisions notables

- **Pas de `single_choice` séparé** (consigne explicite du ticket) : `multiple_choice`
  avec `min_selections=max_selections=1` couvre ce cas. Les vocabulaires existants
  (#17/#21/#23/#29), non touchés par ce ticket, gardent `single_choice` pour leur
  périmètre déjà déployé (MC01/MC02/MC03) — aucune migration de ce contenu ici.
- **`true_false` reste un type séparé** de `multiple_choice` : vocabulaire Vrai/Faux
  figé (pas des options arbitraires), cohérent avec les deux vocabulaires existants qui
  le traitent déjà séparément.
- **`calculation` distinct de `numeric`** : même mécanique de comparaison tolérante
  (`_check_numeric_value`, réutilisée par les deux, jamais dupliquée), mais deux
  `type_id` séparés comme demandé — `calculation` porte l'intention pédagogique « calcul
  à mener », `numeric` une simple valeur numérique attendue.
- **`content_json` n'embarque jamais son propre `schema_version`** : `QuestionVersion.
  schema_version` (ticket #38, colonne dédiée) est déjà l'unique source de vérité — un
  second champ interne aurait pu diverger.

---

# 4. Capacités (`Capability`)

`TEXT_INPUT`, `MULTI_SELECT`, `ORDERABLE`, `DRAG_DROP`, `IMAGE`, `SVG`, `GRAPH`,
`DOCUMENT`, `TABLE`, `CODE`, `FORMULA`, `HOTSPOT`, `SEMANTIC_GRADING`, `LOCAL_GRADING`.

Une question peut cumuler plusieurs capacités — exemples déjà couverts (§ 3) :

```
diagram_labeling    → IMAGE + DRAG_DROP + LOCAL_GRADING
document_analysis   → DOCUMENT + TEXT_INPUT + SEMANTIC_GRADING
```

Objectif : un futur frontend choisit son composant d'affichage à partir de cet
ensemble, jamais en testant la matière ou le `type_id` littéral dans un `if`.

---

# 5. Payload public / solution privée

Principe absolu : **`public_payload()` est le seul point d'entrée** qui transforme un
`content_json` interne en JSON envoyable au navigateur, et chaque type liste
EXPLICITEMENT ses champs publics (voir `app/v1/question_types.py`, chaque fonction
`to_public`/lambda). Jamais de `content.model_dump()` brut, jamais un retrait a
posteriori des champs privés d'une copie — cette dernière approche laisserait fuiter
tout nouveau champ de solution ajouté sans mise à jour de la fonction `to_public`.

Champs typiquement privés (jamais dans `public_payload()`) : `correct_option_ids`,
`correct_value`, `correct_categories`, `correct_order`, `correct_pairs`,
`correct_mapping`, `correct_zone_ids`, `accepted_answers`, `accepted_representations`,
`rubric`, `expected_points`, `critical_points`, `forbidden_claims`,
`expected_parameters`, `expected_steps`, `expected_value`, `tolerance_abs`,
`tolerance_rel`, `max_score`.

Testé systématiquement pour les 26 types (`tests/test_ticket40_question_engine.py`,
`test_public_payload_never_leaks_the_canary_secret` et
`test_public_payload_never_contains_known_private_field_names`) : un champ « canari »
distinctif est injecté dans chaque champ privé d'un contenu minimal, puis
`public_payload()` est sérialisé en JSON et vérifié comme ne contenant jamais ce
canari — pour chacun des 26 types, pas seulement un échantillon.

---

# 6. Modes de correction

```python
class CorrectionMode(str, enum.Enum):
    LOCAL = "local"
    SEMANTIC_AI = "semantic_ai"
    HYBRID = "hybrid"
```

Codifie explicitement ce qui n'existait jusqu'ici que comme des frozensets implicites
(`app.ai.schemas.DETERMINISTIC_QUESTION_TYPES`/`CONDITIONALLY_LOCAL_QUESTION_TYPES`/
`ALWAYS_SEMANTIC_QUESTION_TYPES`) — même concept, rendu interrogeable PAR TYPE plutôt
que par appartenance à un ensemble figé au niveau module.

Pour un type `HYBRID`, la décision LOCAL vs SEMANTIC_AI dépend du CONTENU précis (ex.
`short_answer` avec `accepted_answers` → local ; sans → sémantique) — voir
`QuestionTypeSpec.requires_semantic_correction(content)`, qui délègue à une méthode
`requires_semantic()` optionnelle du modèle de contenu.

---

# 7. Assets (`AssetContract`)

```python
@dataclass(frozen=True)
class AssetContract:
    allowed_kinds: frozenset[AssetKind] = frozenset()
    min_assets: int = 0
    max_assets: int = 0

    @property
    def requires_asset(self) -> bool: ...  # min_assets > 0
```

Réutilise `AssetKind` (`app.v1.models`, ticket #38) tel quel — pas de second
vocabulaire d'assets. Exemples :

- `image_identification`, `hotspot`, `diagram_labeling` → asset requis
  (`min_assets=1`).
- `graph_reading`, `graph_interaction`, `diagnostic`, `troubleshooting`,
  `multiple_choice`, `true_false` → asset optionnel (illustration facultative).
- `long_answer`, `matching`, `classification`, etc. → aucun asset (`NO_ASSET`).

---

# 8. SourceDocument

```python
class SourceDocumentRequirement(str, enum.Enum):
    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"
    MULTIPLE = "multiple"
```

- `document_analysis` → `REQUIRED`, un seul `source_document_version_id` (jamais de
  texte dupliqué dans `content_json` — voir ticket #38, § SourceDocumentVersion).
- `source_comparison` → `MULTIPLE`, `source_document_version_ids` (≥ 2).
- Tous les autres types → `NONE` (aucun champ de référence documentaire).

---

# 9. Versionnement

`validate_content(type_id, schema_version, content_json)` refuse explicitement :
- un `type_id` inconnu (`QuestionEngineError`) ;
- une `schema_version` non listée dans `spec.schema_versions` (`QuestionEngineError`) ;
- un JSON structurellement invalide pour son type (`ContentValidationError`, message
  sur la forme uniquement).

Tous les types V1 déclarent `schema_versions = frozenset({1})` aujourd'hui. Un futur
ticket ajoutant `schema_versions = frozenset({1, 2})` à un type devra fournir sa propre
logique de migration 1→2 (non construite ici — « ne crée pas encore une usine complexe »,
consigne du ticket).

---

# 10. Exemples JSON

## QCM à nombre variable d'options (réponse multiple)

```json
{
  "prompt": "Coche les périphériques de sortie.",
  "options": [
    {"option_id": "a", "label": "Écran"},
    {"option_id": "b", "label": "Clavier"},
    {"option_id": "c", "label": "Imprimante"},
    {"option_id": "d", "label": "Souris"}
  ],
  "min_selections": 2,
  "max_selections": 2,
  "correct_option_ids": ["a", "c"],
  "shuffle": true
}
```

## Classification (Informatique)

```json
{
  "prompt": "Classe chaque élément : matériel ou logiciel ?",
  "categories": ["Matériel", "Logiciel"],
  "elements": ["Carte graphique", "Navigateur", "Antivirus", "SSD"],
  "correct_categories": [0, 1, 1, 0]
}
```

## Diagnostic (Informatique)

```json
{
  "prompt": "Le PC démarre mais aucune image ne s'affiche. Que vérifies-tu et pourquoi ?",
  "rubric": "Doit mentionner le câble/la carte graphique et justifier le lien avec l'absence de signal vidéo.",
  "expected_points": ["câble vidéo débranché", "carte graphique mal fixée"],
  "critical_points": ["mentionner un composant lié à l'affichage"],
  "max_score": 2.0
}
```

## Analyse de texte (Français)

```json
{
  "prompt": "Quel est le sentiment dominant exprimé dans cet extrait ?",
  "source_document_version_id": 42,
  "rubric": "Doit identifier la mélancolie et citer un passage du texte.",
  "expected_points": ["mélancolie/tristesse", "citation à l'appui"],
  "max_score": 3.0
}
```

## Comparaison de deux sources (Français)

```json
{
  "prompt": "Compare le point de vue des deux auteurs sur ce sujet.",
  "source_document_version_ids": [42, 43],
  "rubric": "Doit identifier au moins un point de convergence et un point de divergence.",
  "expected_points": ["convergence identifiée", "divergence identifiée"],
  "max_score": 3.0
}
```

## Hotspot

```json
{
  "prompt": "Clique sur le processeur (CPU) sur cette photo de carte mère.",
  "zones": [
    {"zone_id": "cpu-socket", "x_min": 0.30, "y_min": 0.20, "x_max": 0.45, "y_max": 0.35},
    {"zone_id": "ram-slots", "x_min": 0.50, "y_min": 0.20, "x_max": 0.70, "y_max": 0.30}
  ],
  "correct_zone_ids": ["cpu-socket"],
  "min_selections": 1,
  "max_selections": 1
}
```

## Graphique (lecture, réponse numérique)

```json
{
  "prompt": "D'après ce graphique, quelle est la température maximale relevée ?",
  "graph_config": {"kind": "line", "x_label": "Heure", "y_label": "°C"},
  "response_mode": "numeric",
  "expected_value": 28.5,
  "tolerance_abs": 0.5,
  "unit": "°C",
  "unit_required": true
}
```

---

# 11. Compatibilité PostgreSQL / QuestionVersion (#38)

Aucune modification du modèle `QuestionVersion` (ticket #38) : `content_json`/
`answer_json` restent des colonnes `JSON` génériques, ce registre ne fait que les
valider et les transformer — voir
`tests/test_ticket40_question_engine.py::test_content_json_round_trips_through_question_version`.

---

# 12. Ce qui n'est pas construit par ce ticket

- Sélection/banque (#41), autosave (#42), génération batch (#43), correction globale
  (#44), rating (#45), admin (#46), UI Français finale (#47), reconnaissance d'image
  (#48).
- Aucun widget frontend construit — le contrat (`capabilities`, `public_payload`) est
  prêt à être consommé par un futur renderer, sans qu'aucun composant JS/Plotly/KaTeX
  ne soit ajouté ici (sauf ce qui était nécessaire à la validation du contrat, c'est-à-
  dire rien : tout est vérifié côté Python/Pydantic).
- Migration de schéma inter-versions (`schema_versions` à plusieurs valeurs) : non
  construite, seulement rendue possible structurellement.
- Non-régression : le moteur `app.editorial_exercise` (MC01/MC02/MC03) reste
  totalement inchangé et opérationnel — ce ticket n'y touche pas.

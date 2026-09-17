# Jury Central - Socle des exercices éditoriaux interactifs

Ce document décrit le socle générique `editorial_exercise`, introduit par le ticket #17
suite à l'audit UX/technique du 2026-09-16
(`docs/claude-reports/2026-09-16_audit_interactivite.md`), étendu par le ticket #21
(`docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md`) avec les types
`classification`/`ordering`, puis par le ticket #29
(`docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md`) avec
`long_answer`/`diagnostic`/`vocabulary` (correction sémantique IA, en réutilisant le
contrat #23 sans créer de second moteur — voir `app/editorial_ai_correction.py`).
Objectif : transformer les exercices éditoriaux (aujourd'hui du texte Markdown avec
correction masquée/affichée côté client) en véritables activités interactives, avec
saisie, vérification serveur et score — sans dupliquer l'architecture existante
(value_table, quiz, ai_exercise).

Depuis le ticket #29, **MC01 ne contient plus aucun bloc Markdown d'exercice** : les 12
exercices sont tous des blocs `editorial_exercise` structurés — ce socle n'est donc plus
seulement un composant parmi d'autres, mais le mécanisme d'entraînement complet de MC01.

Ne remplace ni les exercices générés par un générateur Python (`docs/EXERCISE_TYPES.md`)
ni les exercices générés/corrigés par IA (`docs/ai_exercise_engine.md`) : les trois
mécanismes coexistent, chacun dans son rôle.

---

# Principe

```
Bloc de leçon `editorial_exercise`
        ↓
Configuration structurée (mode + items), stockée en JSON dans LessonBlock.content
        ↓
Représentation publique (jamais la solution) envoyée au navigateur
        ↓
Widget générique (un composant par type d'item)
        ↓
Réponse de l'étudiant → POST /practice/api/editorial/{block_id}/verify
        ↓
Le serveur recharge la configuration complète depuis la base et corrige
        ↓
Correction affichée : ✓/✗, réponse attendue, explication
```

Le serveur ne fait jamais confiance au client pour la solution : la configuration
complète (y compris la solution) est toujours relue depuis `LessonBlock.content` au
moment de la correction, jamais transmise avant.

---

# Modèle (`app/editorial_exercise.py`)

```
EditorialExerciseBlockConfig
    mode: "practice" | "exam"     # "exam" réservé à un ticket futur (correction différée)
    context_key: str              # requis si un item nécessite l'IA (ticket #29), sinon ""
    items: [EditorialExerciseItem]

EditorialExerciseItem
    exercise_id: str               # stable au sein du bloc, unique
    type: str                      # voir "Types pris en charge" ci-dessous
    prompt: str                    # markdown, rendu serveur (prompt_html)
    points: float
    # selon le type — jamais dans to_public_dict() :
    choices: list[str]             # single_choice / true_false
    correct_index: int
    accepted_answers: list[str]    # short_answer / vocabulary (correction locale)
    categories: list[str]          # classification — public (proposé à l'étudiant)
    elements: list[str]            # classification — public (proposé à l'étudiant)
    correct_categories: list[int]  # classification — jamais public, un index par élément
    order_items: list[str]         # ordering — public (ordre de présentation initial)
    correct_order: list[int]       # ordering — jamais public, permutation d'order_items
    explanation: str               # réponse affichée après correction locale ; sert aussi
                                    # de grille de correction (rubric) transmise à l'IA pour
                                    # long_answer/diagnostic/vocabulary — jamais publique
```

`context_key` (ticket #29) : clé de `app.ai.context.PEDAGOGICAL_CONTEXTS`, requise dès
qu'au moins un item du bloc a `requires_ai_correction() == True` — validée à la
construction (`EditorialExerciseBlockConfig.__post_init__`), jamais laissée implicite.

- `to_json()` / `from_json()` : mêmes conventions que `ExerciseBlockConfig`
  (`app/exercise_blocks.py`) et `AIExerciseBlockConfig` (`app/ai_exercise_blocks.py`).
- `to_public_dict()` : ne contient jamais `correct_index`, `accepted_answers` ni
  `explanation`.
- `from_json()` est **tolérant** : un item structurellement invalide (contenu admin mal
  formé) est silencieusement ignoré plutôt que de faire échouer le rendu de la page
  publique. La construction directe (`EditorialExerciseItem(...)`, utilisée par
  `app/seed.py` et les tests) reste, elle, strictement validée (`__post_init__` lève
  `EditorialExerciseValidationError`) — les erreurs d'auteur sont détectées tôt.

## Types pris en charge

| Type | Correction | Détail |
|---|---|---|
| `single_choice` | Locale, déterministe | Index de la réponse choisie comparé à `correct_index` |
| `true_false` | Locale, déterministe | Même mécanisme que `single_choice`, avec `choices: ["Vrai", "Faux"]` |
| `short_answer` | Locale si `accepted_answers` fourni, sinon IA (#29) | Comparaison textuelle normalisée (casse, espaces, accents) — voir `app/answer_checking.py::text_answer_matches` ; sans `accepted_answers`, `explanation` sert de grille de correction IA |
| `classification` (#21) | Locale, déterministe | Réponse `list[int]` : un index de catégorie par élément (même ordre que `elements`), comparée telle quelle à `correct_categories` — pas de correction partielle |
| `ordering` (#21) | Locale, déterministe | Réponse `list[int]` : une permutation des index de `order_items` dans l'ordre proposé, comparée à `correct_order` ; une réponse qui n'est pas une permutation valide (doublon, valeur hors bornes, longueur incorrecte) est traitée comme incorrecte, jamais comme une erreur serveur |
| `long_answer` (#29) | Toujours IA | Réponse rédigée libre ; `explanation` (grille de correction) obligatoire, jamais publique |
| `diagnostic` (#29) | Toujours IA | Composant(s) en cause + justification ; même mécanisme que `long_answer` |
| `vocabulary` (#29) | Locale si `accepted_answers` fourni, sinon IA | Même règle que `short_answer` — utilisé pour du vocabulaire pur (terme exact) en local, ou une explication à apprécier semantiquement (IA) |

`short_answer`/`vocabulary` ne sont corrigés **localement** que lorsqu'une règle
déterministe **fiable** existe (`accepted_answers` non vide). Un exercice demandant une
réponse rédigée libre (« explique pourquoi... ») n'est **jamais** forcé dans un type
local — voir `docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` et
`docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md` pour la liste
précise des exercices MC01 concernés par chaque tranche.

`classification`/`ordering` envoient une réponse structurée (`list[int]`), pas une chaîne
— voir la route ci-dessous (`answer: Any`). La correction locale reste binaire
(correct/incorrect sur l'ensemble de l'item), sans note partielle. La correction
**sémantique** (IA, ticket #29) renvoie en plus un barème (`points_awarded`/`points_max`,
toujours borné côté serveur) et un détail (`strengths`/`errors`/`missing`) — voir
§ Correction sémantique IA ci-dessous.

## Correction sémantique IA (ticket #29)

`long_answer`/`diagnostic`, et `short_answer`/`vocabulary` sans `accepted_answers`, sont
corrigés via le fournisseur IA existant (`app/ai/`, ticket #23) — **jamais un second
moteur**. `app/editorial_ai_correction.py` fait le pont :

```
EditorialExerciseItem.requires_ai_correction()
        ↓ (vrai)
app.editorial_ai_correction.editorial_item_to_question(item)
        → QuestionnaireQuestion(question_id=item.exercise_id, points_max=item.points,
                                 accepted_answers=item.accepted_answers,
                                 rubric=item.explanation)
        ↓
AIProvider.correct_semantic_batch([question], {exercise_id: réponse}, severity, [contexte])
        ↓ (UN SEUL appel, pour cette seule question)
app.ai.questionnaire.validate_semantic_correction(question, résultat brut)
        → points_awarded toujours borné à [0, points_max] ; points_max toujours repris
          de `item.points`, jamais de la réponse du fournisseur
        ↓
EditorialExerciseCorrection (points_awarded, points_max, strengths, errors, missing en
plus des champs existants correct/correct_answer/explanation)
```

`item.explanation` sert de grille de correction (`rubric`) transmise au modèle — c'est
déjà le texte qui explique la bonne réponse à l'étudiant après correction, donc
naturellement adapté à guider une appréciation IA sans dupliquer de contenu ni ajouter un
nouveau champ d'auteurisation dans `app/seed.py`.

**Sévérité** : `app.editorial_ai_correction.DEFAULT_PRACTICE_SEVERITY = "standard"` — la
sélection de sévérité (bienveillante/standard/stricte, #23) par l'utilisateur est un choix
d'UX laissé aux tickets qui construiront une interface dédiée (#24/#25) ; S'entraîner
(#29) utilise ce défaut raisonnable et documenté, pas un choix arbitraire caché.

**Sans clé configurée** : `AINotConfiguredError` → HTTP 503 côté route
(`app/practice.py`), message clair, **jamais la solution**, la zone de saisie reste
utilisable côté client (voir § Widget). Erreur fournisseur (timeout, réponse invalide,
statut non-2xx) → HTTP 502, même principe.

## Types non encore pris en charge (tickets suivants)

- `matching` (appariement) — nécessite sa propre logique de correction locale et son
  propre composant d'interaction, ticket séparé (aucun exercice MC01 réel n'en a besoin
  à ce jour).
- `mode: "exam"` — correction différée jusqu'à une soumission finale groupée, ticket
  séparé (voir l'audit, section G).

---

# Route (`app/practice.py`)

`POST /practice/api/editorial/{block_id}/verify` — payload `{"exercise_id": str, "answer": Any}`.
`answer` est une `str` pour `single_choice`/`true_false`/`short_answer`/`vocabulary`/
`long_answer`/`diagnostic`, et une `list[int]` pour `classification`/`ordering`
(ticket #21) — voir la table des types ci-dessus. La route détermine le routage local/IA
via `item.requires_ai_correction()` avant tout appel (`app/practice.py`).

Réponse :

```json
{
  "exercise_id": "...",
  "correct": true,
  "correct_answer": "...",
  "correct_answer_html": "...",
  "explanation": "...",
  "explanation_html": "...",
  "points_awarded": null,
  "points_max": null,
  "strengths": [],
  "errors": [],
  "missing": []
}
```

`points_awarded`/`points_max`/`strengths`/`errors`/`missing` sont `null`/`[]` pour une
correction locale (types inchangés depuis #17/#21), renseignés pour une correction
sémantique IA (ticket #29) — même forme dans les deux cas, pas de branchement client
supplémentaire à écrire.

| Code | Cas |
|---|---|
| 200 | Réponse évaluée (correcte ou non), locale ou IA |
| 404 | `block_id` introuvable, type de bloc incorrect, bloc non publié, ou `exercise_id` introuvable dans le bloc |
| 422 | Réponse non textuelle pour un type nécessitant l'IA (ticket #29) |
| 500 | `context_key` du bloc sans contexte pédagogique enregistré (erreur d'auteurisation, jamais en usage normal) |
| 503 | Correction IA non configurée sur ce serveur (`AINotConfiguredError`, ticket #29) |
| 502 | Erreur du fournisseur IA (timeout, réponse invalide, statut non-2xx, ticket #29) |

---

# Widget (`app/static/js/editorial_exercise.js`)

Un conteneur `.editorial-exercise-block` porte `data-verify-url` et `data-items` (JSON
public). Le widget construit un composant par item selon son `type` (fonction dédiée par
type, pas de branchement géant) et affiche, après réponse :

- ✓ Correct / ✗ Incorrect ;
- la réponse attendue si la réponse est incorrecte ;
- l'explication pédagogique, si présente.

Aucun rechargement de page (AJAX, `fetch`). Aucune donnée de correction n'est présente
dans le DOM avant l'appel réseau de vérification. Contrôles marqués `d-print-none` (mode
impression : prompt visible, contrôles interactifs masqués — même convention que
`value_table`/`ai_exercise`). Contrôles Bootstrap standards (`list-group-item-action`,
`form-control`), pleine largeur/taille normale par défaut — pas de bouton `btn-sm` sur les
actions principales, pas de largeur fixe (seulement un `max-width` plafond sur le champ
`short_answer`, sans risque de débordement sur petit écran).

`classification` (`buildClassificationControl`) et `ordering` (`buildOrderingControl`,
ticket #21) sont exclusivement pilotés au clic — aucun glisser-déposer requis, utilisables
au tactile comme au clavier (chaque bouton est un `<button>` natif, focusable, avec
`aria-label` explicite pour monter/descendre) :

- **classification** : un groupe de boutons de catégorie par élément à classer ; le bouton
  actif se met en surbrillance (`.active`), le bouton « Vérifier » ne s'active que lorsque
  chaque élément a une catégorie choisie ; la réponse envoyée est la liste des index de
  catégorie, dans l'ordre de `elements`.
- **ordering** : une liste `<ol>` numérotée, chaque ligne avec deux boutons « ↑ »/« ↓ »
  (désactivés en butée haute/basse) qui échangent la ligne avec sa voisine ; la réponse
  envoyée est la permutation courante des index de `order_items`.

**Types à réponse libre** (`long_answer`, `diagnostic`, `vocabulary` sans
`accepted_answers` — ticket #29, `buildTextareaControl`) : une `<textarea>` + un bouton
« Corriger » (libellé différent de « Vérifier », reflète la correction IA — le libellé
est choisi via `item.requires_ai`, jamais deviné depuis le type ou le titre). Pendant
l'appel réseau : bouton et champ désactivés, indicateur « Un instant… » visible (même
convention que `ai_exercise.js`). En cas d'échec réseau/503/502 : le champ et le bouton
sont **réactivés** (`renderEditorialUnavailable`), un message clair s'affiche (jamais la
solution, jamais un plantage silencieux — corrige un gap identifié sur les types
existants au passage : avant #29, un échec HTTP quelconque laissait le bouton désactivé
indéfiniment sans aucun message).

Le feedback affiché après une correction sémantique inclut, en plus de ✓/✗ et de
l'explication : le barème obtenu (`points_awarded`/`points_max`, si présents), une liste
« Points forts », une liste « Erreurs », une liste « Manquant » (issues de la réponse IA,
absentes/vides pour une correction locale — dégradation silencieuse et automatique côté
JS, pas de branchement par type à maintenir).

---

# Démonstration (`/admin/editorial-exercise-demo`)

Comme `/admin/value-table-demo` (précédent exact), une route admin protégée prévisualise
le socle avec un exercice fixe par type (un `single_choice`, un `true_false`, un
`short_answer`), **indépendamment de tout contenu pédagogique réel**. Utile pour valider
visuellement l'architecture (rendu, saisie, AJAX, correction, mobile, impression) sans
dépendre d'un cours migré.

---

# Sécurité

- Le serveur recharge toujours `EditorialExerciseBlockConfig` depuis
  `LessonBlock.content` avant de corriger — jamais confié au client.
- `to_public_dict()` exclut structurellement `correct_index`, `accepted_answers` et
  `explanation` (testé explicitement, y compris au niveau HTTP : la page `/uaa/{slug}`
  ne contient jamais ces valeurs avant correction).
- Comparaison textuelle sans `eval()` (`app/answer_checking.py::text_answer_matches`,
  extension de la même logique de normalisation déjà utilisée pour les réponses
  numériques).
- Correction 100 % locale et déterministe pour `single_choice`/`true_false`/
  `classification`/`ordering`, et pour `short_answer`/`vocabulary` avec
  `accepted_answers` — aucun appel réseau, aucun appel IA pour ces types.
- `classification`/`ordering` (#21) : une réponse malformée (mauvais type, mauvaise
  longueur, valeurs non entières, ou — pour `ordering` — une liste qui n'est pas une
  permutation valide des index de `order_items`) est explicitement traitée comme une
  réponse incorrecte (`correct: false`), jamais comme une exception serveur — testé
  explicitement (`tests/test_editorial_exercise.py`).
- **Correction sémantique IA** (`long_answer`/`diagnostic`, et `short_answer`/
  `vocabulary` sans `accepted_answers`, ticket #29) : réutilise `AIProvider.
  correct_semantic_batch` (#23), jamais un second moteur. `points_max` ne vient jamais
  de la réponse du fournisseur (toujours `item.points`) ; `points_awarded` toujours
  borné à `[0, points_max]` (`app.ai.questionnaire.validate_semantic_correction`) — même
  garantie que le contrat questionnaire, jamais un second mécanisme de bornage écrit en
  parallèle. Réponse candidate toujours transmise comme donnée délimitée, jamais une
  instruction (même prompt système que #23, `CORRECT_SEMANTIC_SYSTEM_PROMPT`).
  `explanation` (grille de correction) n'est jamais transmise au client avant correction
  (absente de `to_public_dict()`, seul `requires_ai: bool` — la modalité de correction,
  jamais la solution — y figure).

---

# Tests

- `tests/test_editorial_exercise.py` — validation de configuration (dataclass,
  `__post_init__`), sérialisation/désérialisation, tolérance de `from_json` aux items
  invalides, absence de fuite dans `to_public_dict()`, correction (bonne/mauvaise
  réponse, id inconnu).
- `tests/test_practice_editorial_routes.py` — route HTTP de bout en bout (`TestClient`) :
  réponse correcte/incorrecte, `short_answer` normalisé, `block_id`/`exercise_id`
  invalides, bloc non publié, mauvais type de bloc, absence de fuite dans le HTML de
  `/uaa/{slug}`, route de démonstration admin (page + vérification + authentification
  requise).
- `tests/test_ticket17_no_regression.py` — confirme que `app/seed.py` n'était pas modifié
  par le ticket #17 (mis à jour au #21, voir docstring du module) : MC02/MC03/Mathématiques
  strictement inchangés, MC01 conserve ses 12 exercices accessibles quel que soit leur
  type de bloc.
- `tests/test_ticket21_no_regression.py` — les 4 exercices structurés du ticket #21
  (1/2/9/11) restent intacts après #29 (« ne pas casser #21 »), leur contenu pédagogique
  d'origine (prompt + grille de correction) est vérifié mot pour mot pour les 8 autres.
- `tests/test_editorial_ai_correction.py` — pont éditorial/IA (ticket #29) :
  `editorial_item_to_question` (mapping des champs), un seul appel au fournisseur par
  correction, sévérité respectée, points jamais lus depuis la réponse brute du
  fournisseur, résultat manquant traité comme 0 point sans exception.
- `tests/test_ticket29_no_regression.py` — les 12 exercices MC01 sont des blocs
  `editorial_exercise` en PRACTICE ; aucune correction visible au chargement (pour aucun
  des 12) ; classification/ordering toujours fonctionnels ; correction déterministe et
  IA (via `FakeAIProvider`, jamais un appel réel) ; réponse non textuelle rejetée (422)
  pour un type sémantique ; absence de clé → 503 propre ; erreur fournisseur → 502 ;
  points toujours bornés côté serveur ; aucun doublon Markdown ; scénario complet de
  migration d'un staging déjà seedé avant #29 (forme post-#22 : 23 blocs, 8 exercices
  encore en 3 blocs Markdown) vers la forme post-#29 (28 blocs), sans `reset-db` ;
  idempotence du seed ; MC02/MC03/Mathématiques non affectés.

---

# Étendre le socle (tickets suivants)

1. Ajouter le nouveau `type` à `EDITORIAL_EXERCISE_TYPES`.
2. Étendre `EditorialExerciseItem.__post_init__` (validation), `to_public_dict()`
   (données publiques propres au type), `check()` (correction) et
   `correct_answer_display()`.
3. Ajouter la fonction de construction du composant correspondant dans
   `editorial_exercise.js` (une fonction par type, pas de refonte du fichier).
4. Aucune modification de route ni de modèle de données n'est nécessaire pour un type à
   correction locale supplémentaire — tout passe par la même route `/verify` existante,
   à condition que la réponse reste sérialisable en JSON (`answer: Any` côté serveur
   depuis le ticket #21 : `str` pour un type existant, `list[int]` pour
   `classification`/`ordering` — un futur type pourrait réutiliser l'une de ces deux
   formes ou introduire la sienne sans casser les types déjà en place, chacun étant
   discriminé par son propre `if self.type == "...":` dans `check()`).

Cette recette a été suivie sans modification pour `classification`/`ordering` (ticket
#21) après une première validation avec `single_choice`/`true_false`/`short_answer`
(ticket #17) — le socle est donc confirmé réellement extensible, pas seulement en théorie.

Le ticket #29 (`long_answer`/`diagnostic`/`vocabulary`) a suivi la même recette, avec un
seul ajout structurel : une correction locale ne suffisant plus pour ces types, `item.
requires_ai_correction()` route la route (`app/practice.py`) vers
`app/editorial_ai_correction.py` plutôt que vers `check_editorial_answer()` — le module
`app/editorial_exercise.py` lui-même reste néanmoins totalement indépendant d'`app/ai/`
(aucun nouvel import), ce qui garde le socle testable et utilisable sans le moteur IA.

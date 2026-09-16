# Jury Central - Socle des exercices éditoriaux interactifs

Ce document décrit le socle générique `editorial_exercise`, introduit par le ticket #17
suite à l'audit UX/technique du 2026-09-16
(`docs/claude-reports/2026-09-16_audit_interactivite.md`). Objectif : transformer les
exercices éditoriaux (aujourd'hui du texte Markdown avec correction masquée/affichée côté
client) en véritables activités interactives, avec saisie, vérification serveur et score —
sans dupliquer l'architecture existante (value_table, quiz, ai_exercise).

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
    items: [EditorialExerciseItem]

EditorialExerciseItem
    exercise_id: str               # stable au sein du bloc, unique
    type: str                      # voir "Types pris en charge" ci-dessous
    prompt: str                    # markdown, rendu serveur (prompt_html)
    points: float
    # selon le type — jamais dans to_public_dict() :
    choices: list[str]             # single_choice / true_false
    correct_index: int
    accepted_answers: list[str]    # short_answer
    explanation: str
```

- `to_json()` / `from_json()` : mêmes conventions que `ExerciseBlockConfig`
  (`app/exercise_blocks.py`) et `AIExerciseBlockConfig` (`app/ai_exercise_blocks.py`).
- `to_public_dict()` : ne contient jamais `correct_index`, `accepted_answers` ni
  `explanation`.
- `from_json()` est **tolérant** : un item structurellement invalide (contenu admin mal
  formé) est silencieusement ignoré plutôt que de faire échouer le rendu de la page
  publique. La construction directe (`EditorialExerciseItem(...)`, utilisée par
  `app/seed.py` et les tests) reste, elle, strictement validée (`__post_init__` lève
  `EditorialExerciseValidationError`) — les erreurs d'auteur sont détectées tôt.

## Types pris en charge (première tranche, ticket #17)

| Type | Correction | Détail |
|---|---|---|
| `single_choice` | Locale, déterministe | Index de la réponse choisie comparé à `correct_index` |
| `true_false` | Locale, déterministe | Même mécanisme que `single_choice`, avec `choices: ["Vrai", "Faux"]` |
| `short_answer` | Locale, déterministe | Comparaison textuelle normalisée (casse, espaces, accents) à une liste `accepted_answers` — voir `app/answer_checking.py::text_answer_matches` |

`short_answer` n'est utilisé que lorsqu'une règle de correction déterministe **fiable**
existe (une réponse courte, sans ambiguïté formulable comme une liste de variantes
acceptées). Un exercice demandant une réponse rédigée libre (« explique pourquoi... »)
n'est **jamais** forcé dans ce type — voir
`docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` pour la liste précise
des exercices MC01 qui en ont besoin.

## Types non encore pris en charge (tickets suivants)

- `long_answer` (réponse rédigée) — nécessite une correction IA, ticket séparé.
- `classification`, `ordering`, `matching` — nécessitent chacun leur propre logique de
  correction locale et leur propre composant d'interaction, tickets séparés.
- `mode: "exam"` — correction différée jusqu'à une soumission finale groupée, ticket
  séparé (voir l'audit, section G).

---

# Route (`app/practice.py`)

`POST /practice/api/editorial/{block_id}/verify` — payload `{"exercise_id": str, "answer": str}`.

Réponse :

```json
{
  "exercise_id": "...",
  "correct": true,
  "correct_answer": "...",
  "correct_answer_html": "...",
  "explanation": "...",
  "explanation_html": "..."
}
```

| Code | Cas |
|---|---|
| 200 | Réponse évaluée (correcte ou non) |
| 404 | `block_id` introuvable, type de bloc incorrect, bloc non publié, ou `exercise_id` introuvable dans le bloc |

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
- Aucun appel réseau externe, aucun appel IA : correction 100 % locale et déterministe
  pour cette tranche de types.

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
- `tests/test_ticket17_no_regression.py` — confirme que `app/seed.py` n'est pas modifié
  par ce ticket : MC01/MC02/MC03/Mathématiques strictement inchangés.

---

# Étendre le socle (tickets suivants)

1. Ajouter le nouveau `type` à `EDITORIAL_EXERCISE_TYPES`.
2. Étendre `EditorialExerciseItem.__post_init__` (validation), `to_public_dict()`
   (données publiques propres au type), `check()` (correction) et
   `correct_answer_display()`.
3. Ajouter la fonction de construction du composant correspondant dans
   `editorial_exercise.js` (une fonction par type, pas de refonte du fichier).
4. Aucune modification de route ni de modèle de données n'est nécessaire pour un type à
   correction locale supplémentaire — tout passe par la même route `/verify` existante.

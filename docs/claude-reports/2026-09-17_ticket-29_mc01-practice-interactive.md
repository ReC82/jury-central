# Ticket #29 — Entraînement : rendre toutes les questions MC01 répondables

**Date** : 2026-09-17
**Branche** : `feature/29-mc01-practice-interactive`
**Ticket GitHub** : #29 « Entraînement — rendre toutes les questions répondables et
masquer les corrections »

---

## 1. Résumé

`/uaa/ampcr-mc01/practice` mélangeait deux générations de contenu : 4 exercices
interactifs (classification/ordering, ticket #21) et 8 exercices Markdown statiques
(3, 4, 5, 6, 7, 8, 10, 12) sans aucun contrôle de réponse, affichant leur correction
directement dans le HTML. Ce ticket migre les 8 restants vers le socle
`editorial_exercise`, avec les types appropriés à leur contenu réel
(`long_answer`/`diagnostic`/`vocabulary`), une correction sémantique via le fournisseur
IA existant (#23, aucun second moteur), et une correction locale conservée pour
classification/ordering (#21, non cassés). **MC01 ne contient plus aucun bloc Markdown
d'exercice** — les 12 sont désormais tous des blocs `editorial_exercise`, tous en
PRACTICE, tous répondables, aucune correction visible avant action explicite.

**RUFF_NOUVELLES_PAR_TICKET = 0**, **PYTEST = 431 passed** (396 + 35 nouveaux).

---

## 2. Audit — état AVANT modification (12 exercices MC01)

| N° | Titre (pré-#29) | Contenu actuel (résumé) | BlockType | space | Interactif | Correction visible au chargement | Type structuré cible |
|---|---|---|---|---|---|---|---|
| 1 | Exercice 1 — Matériel ou logiciel (classification) | Classer 5 éléments matériel/logiciel | EDITORIAL_EXERCISE | PRACTICE | Oui (#21) | Non | *(déjà migré — inchangé)* `classification` |
| 2 | Exercice 2 — Unité centrale ou périphérique (classification) | Classer 6 éléments unité centrale/périphérique | EDITORIAL_EXERCISE | PRACTICE | Oui (#21) | Non | *(déjà migré — inchangé)* `classification` |
| 3 | « ## Exercice 3 — expliquer » (dans le bloc Markdown « …composants et rôles : suite ») | Pourquoi un CPU n'est pas compatible avec n'importe quelle carte mère (réponse rédigée courte) | MARKDOWN | PRACTICE | **Non** | **Oui** | `long_answer` |
| 4 | « ## Exercice 4 — diagnostiquer » (même bloc Markdown) | PC démarre, écran noir : 2 composants à vérifier + pourquoi | MARKDOWN | PRACTICE | **Non** | **Oui** | `diagnostic` |
| 5 | « ## Exercice 5 — expliquer » (bloc Markdown « …RAM, stockage, GPU, PSU ») | Différence RAM/stockage en 2 points | MARKDOWN | PRACTICE | **Non** | **Oui** | `long_answer` |
| 6 | « ## Exercice 6 — expliquer une ambiguïté » (même bloc) | Ambiguïté « 32 Go » RAM vs stockage | MARKDOWN | PRACTICE | **Non** | **Oui** | `long_answer` |
| 7 | « ## Exercice 7 — expliquer » (même bloc) | GPU intégré vs dédié, VRAM | MARKDOWN | PRACTICE | **Non** | **Oui** | `long_answer` |
| 8 | « ## Exercice 8 — expliquer » (même bloc) | Sens de « 750 W », règle de sécurité PSU | MARKDOWN | PRACTICE | **Non** | **Oui** | `long_answer` |
| 9 | Exercice 9 — Lancement d'un programme (ordering) | Remettre 4 étapes dans l'ordre | EDITORIAL_EXERCISE | PRACTICE | Oui (#21) | Non | *(déjà migré — inchangé)* `ordering` |
| 10 | « ## Exercice 10 — diagnostiquer » (bloc Markdown « …diagnostic et vocabulaire : suite ») | PC ralentit à l'ouverture de plusieurs programmes : composant en cause | MARKDOWN | PRACTICE | **Non** | **Oui** | `diagnostic` |
| 11 | Exercice 11 — Entrée, sortie ou mixte (classification) | Classer 5 périphériques entrée/sortie/mixte | EDITORIAL_EXERCISE | PRACTICE | Oui (#21) | Non | *(déjà migré — inchangé)* `classification` |
| 12 | « ## Exercice 12 — vocabulaire » (même bloc que Ex10) | 4 termes FR → EN + explication brève chacun | MARKDOWN | PRACTICE | **Non** | **Oui** | `vocabulary` (IA — explication requise, pas seulement le terme) |

**8 exercices sur 12 n'avaient aucun contrôle de réponse et affichaient leur correction
sans aucune action** — exactement le constat du ticket, confirmé par cet audit avant toute
modification.

---

## 3. Mapping ancien format → nouveau type (justification par exercice)

| Exercice | Type retenu | Justification |
|---|---|---|
| 3, 5, 6, 7, 8 | `long_answer` | Réponse rédigée ouverte, aucune formulation unique correcte — forcer un `short_answer` aurait dénaturé l'exercice (interdit explicitement par le ticket). |
| 4, 10 | `diagnostic` | Demande explicitement un composant à identifier + une justification — correspond exactement à la définition du type `diagnostic` du contrat #23. |
| 12 | `vocabulary` (sans `accepted_answers`, donc IA) | L'énoncé demande le terme anglais **et** une explication brève de chacun des 4 termes : une correction locale par `accepted_answers` n'aurait validé que le terme exact, jamais l'explication — utiliser `vocabulary` sans `accepted_answers` (correction IA, grille = la correction d'origine) est la seule option qui n'ampute pas l'exercice de sa seconde exigence. |

Aucun des 8 n'a été forcé dans un type à correction locale simplifiée : chacun a été
évalué individuellement, comme lors des tickets #17/#21.

---

## 4. Contenu pédagogique préservé mot pour mot

`prompt` et `explanation` de chaque nouvel item reprennent exactement le texte des
anciens blocs Markdown (question et paragraphe « Correction : », sans le préfixe
« Correction : » lui-même — redondant avec la présentation du widget). Vérifié
explicitement par
`tests/test_ticket21_no_regression.py::test_exercises_3_to_12_pedagogical_content_preserved_after_ticket_29`
(comparaison d'extraits caractéristiques de chaque question et de chaque grille de
correction).

**Réorganisation** : les positions des 12 exercices dans `MC01_BLOCKS` ont été remises
dans l'ordre naturel 1→12 (le ticket #21 les avait laissés dans un ordre légèrement
réarrangé — 9, 11 puis 10/12 groupés — car Ex10/Ex12 restaient dans un même bloc Markdown
non séparable à l'époque). Ce n'est qu'un réordonnancement d'affichage, pas un changement
de contenu.

---

## 5. Architecture : correction sémantique IA sans second moteur

**Nouveau module `app/editorial_ai_correction.py`** — pont entre `app/editorial_exercise.py`
(persisté, #17/#21) et `app/ai/` (#23) :

```
EditorialExerciseItem.requires_ai_correction()  # nouvelle méthode, #29
        ↓ (vrai pour long_answer/diagnostic toujours, short_answer/vocabulary si
        ↓  accepted_answers absent)
editorial_item_to_question(item) -> QuestionnaireQuestion(
    question_id=item.exercise_id, points_max=item.points,
    accepted_answers=item.accepted_answers, rubric=item.explanation,
)
        ↓
AIProvider.correct_semantic_batch([question], {exercise_id: réponse}, severity, [contexte])
        ↓  (UN SEUL appel réseau, pour cette seule question — pas de second moteur)
app.ai.questionnaire.validate_semantic_correction(question, résultat brut)  # promue
        ↓  publique ce ticket, déjà utilisée par le contrat questionnaire #23
EditorialExerciseCorrection(points_awarded, points_max, strengths, errors, missing, ...)
```

`item.explanation` sert de grille de correction (`rubric`) — c'est déjà le texte qui
explique la bonne réponse à l'étudiant après correction, donc naturellement adapté à
guider une appréciation IA sans ajouter de nouveau champ d'auteurisation dans
`app/seed.py`.

**Nouveau champ `EditorialExerciseBlockConfig.context_key`** (mirroring
`AIExerciseBlockConfig.context_key`, #10) : requis dès qu'au moins un item du bloc
nécessite l'IA, validé à la construction — jamais implicite, jamais déduit.

**Sévérité** : `app.editorial_ai_correction.DEFAULT_PRACTICE_SEVERITY = "standard"` — un
défaut documenté, pas un choix arbitraire caché ; la sélection de sévérité par
l'utilisateur (#23) reste un choix d'UX pour les tickets #24/#25.

**Route** (`app/practice.py::api_verify_editorial_exercise`) : route désormais vers la
correction locale (inchangée) ou vers `correct_editorial_item_with_ai` selon
`item.requires_ai_correction()`, déterminé **avant** tout appel. Codes d'erreur ajoutés :
422 (réponse non textuelle pour un type sémantique), 500 (contexte pédagogique
introuvable — erreur d'auteurisation), 503 (`AINotConfiguredError`), 502
(`AIProviderError`) — mêmes codes que les routes AI_EXERCISE existantes (#10), pour la
cohérence.

---

## 6. UX / widget JS

`app/static/js/editorial_exercise.js` — nouveau `buildTextareaControl` (textarea + bouton
« Corriger », réutilisé pour `long_answer`/`diagnostic`/`vocabulary`) :

- Consigne, zone de réponse, bouton de validation, feedback : quatre zones toujours
  visuellement séparées (`<div class="content-markdown">` pour la consigne, `<textarea>`
  dans son propre conteneur, bouton dans une ligne d'action, `resultBox` distincte —
  jamais affichée avant réponse serveur).
- Bouton désactivé + indicateur « Un instant… » pendant la requête (même convention que
  `ai_exercise.js`) ; aucun rechargement de page (AJAX `fetch`).
- **Correction d'un gap identifié sur les types existants en cours de développement** :
  avant ce ticket, un échec réseau ou une réponse HTTP non-2xx laissait silencieusement
  le bouton désactivé indéfiniment (`onAnswer` retournait sans rien faire ni afficher).
  Corrigé pour **tous** les types (pas seulement les nouveaux) : `submitEditorialAnswer`
  retourne désormais un statut explicite, et chaque builder réactive ses contrôles + un
  message clair s'affiche (jamais la solution) en cas d'échec — testé indirectement via
  les routes (les corps de réponse restent propres, jamais de solution).
- Feedback enrichi après correction sémantique : barème obtenu, « Points forts »,
  « Erreurs », « Manquant » — absents/vides et donc invisibles pour une correction
  locale (dégradation automatique, pas de branchement par type supplémentaire).

Mobile-first : `<textarea>` en pleine largeur du conteneur (`form-control`), aucune
largeur fixe, cohérent avec les contrôles existants (`short_answer`) déjà validés sur
360/390/430 px lors des tickets précédents.

---

## 7. Migration du staging déjà seedé (sans reset-db)

Même mécanisme que #21/#22 : les 3 blocs Markdown restants de MC01 (« …composants et
rôles : suite », « …RAM, stockage, GPU, PSU », « …diagnostic et vocabulaire : suite »)
sont ajoutés à `MC01_OBSOLETE_TITLES` (désormais 5 titres au total, cumulés depuis #21) —
`_seed_uaa(obsolete_titles=...)` les retire par titre au prochain `seed-db`, puis les 8
nouveaux blocs structurés (titres différents des anciens, garantissant l'idempotence des
seeds ultérieurs) sont ajoutés. **Aucun `reset-db` requis.**

Scénario reproduit et vérifié explicitement
(`tests/test_ticket29_no_regression.py::test_staging_seeded_before_ticket_29_is_migrated_without_reset`)
: une UAA MC01 construite à la main dans l'état exact post-#22 (4 blocs structurés #21 +
3 blocs Markdown sous leurs anciens titres, `space=PRACTICE`) migre en un seul `seed()`
vers l'état complet post-#29 (12 blocs structurés, 0 bloc Markdown d'exercice), sans
perte ni doublon.

**Procédure de déploiement réelle** (à exécuter par ChatGPT/l'administrateur après merge,
identique aux tickets précédents) : `scripts/deploy_staging.sh` puis `seed-db`.

---

## 8. Découverte annexe corrigée en cours de développement

En écrivant les tests unitaires du nouveau type `vocabulary`, `EditorialExerciseItem.
check()` et `.correct_answer_display()` se sont révélés ne gérer que `short_answer` pour
la correction locale déterministe (branche `if self.type == "short_answer":` sans
`vocabulary`), alors que la validation (`__post_init__`) et `requires_ai_correction()`
traitaient déjà les deux types de façon symétrique. Un item `vocabulary` avec
`accepted_answers` aurait donc été accepté à la construction (aucune erreur) mais **jamais
corrigé correctement en local** (toujours `False`). Détecté par
`test_vocabulary_is_locally_corrected_when_accepted_answers_present`, avant tout usage
réel — corrigé (`("short_answer", "vocabulary")` dans les deux méthodes) avant la
migration de MC01, donc **sans impact en production**.

---

## 9. Tests

**Aucun appel OpenAI réel dans `pytest`** — `FakeAIProvider` uniquement ; `tests/conftest.py`
force déjà `OPENAI_API_KEY=""` (correction du ticket #31) — vérifié à nouveau pendant ce
ticket, cette protection a fonctionné comme prévu pour tous les nouveaux tests.

- `tests/test_editorial_exercise.py` (+15 tests) : validation de `long_answer`/
  `diagnostic` (explanation requise), `vocabulary` (conditionnellement locale),
  `requires_ai_correction()` pour les 3 nouveaux types, absence de fuite dans
  `to_public_dict()` (ni `explanation` ni `rubric`, `requires_ai` correctement exposé),
  validation de `EditorialExerciseBlockConfig.context_key` (requis si un item IA est
  présent, roundtrip JSON).
- `tests/test_editorial_ai_correction.py` (nouveau, 5 tests) : mapping vers
  `QuestionnaireQuestion`, un seul appel par correction, sévérité respectée, points
  jamais lus depuis la réponse brute du fournisseur, résultat manquant géré sans
  exception.
- `tests/test_ticket29_no_regression.py` (nouveau, 20 tests) : 12/12 exercices présents
  en PRACTICE et structurés ; 12/12 répondables (type + contrôle public cohérent) ;
  widget JS sait construire un contrôle pour les 5 types utilisés (garde-fou statique) ;
  0 correction visible au chargement (aucun texte de grille, aucune clé JSON sensible,
  pour aucun des 12) ; classification/ordering toujours corrects déterministement ;
  correction IA (`long_answer`/`diagnostic`/`vocabulary`) via `FakeAIProvider`, un seul
  appel par question ; absence de clé → 503 propre, solution jamais affichée ; erreur
  fournisseur → 502 ; réponse non textuelle pour un type sémantique → 422, provider
  jamais appelé ; points toujours bornés `[0, points_max]` même si le fournisseur
  réclame plus ; aucun doublon avec un ancien bloc Markdown ; scénario complet de
  migration d'un staging pré-#29 sans reset ; idempotence du seed ; MC02/MC03/
  Mathématiques non affectés.
- Tests existants ajustés (conséquence directe et attendue de la migration complète, pas
  une régression) : `tests/test_informatique_mc01.py`, `tests/test_ticket17_no_regression.py`,
  `tests/test_ticket21_no_regression.py`, `tests/test_ticket22_no_regression.py` — compte
  d'exercices structurés (4 → 12), absence totale de « Correction : » statique, nombre
  total de blocs MC01 (23 → 28), répartition PRACTICE (8 → 13, incluant le bloc IA).

**Résultat** : `pytest -q` → **431 passed** (396 avant ce ticket + 35 nouveaux), 2
warnings préexistants (dépréciations `httpx`/`anyio`, sans lien avec ce ticket).

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé. **0 nouvelle erreur.**

---

## 10. Vérification manuelle

Base SQLite temporaire isolée (`/tmp/...`, jamais `jury_central.db`), serveur `uvicorn`
réel démarré sur un port de test, **`OPENAI_API_KEY` explicitement vidée** pour cette
vérification (voir incident ci-dessous) :

- `GET /uaa/ampcr-mc01/practice` : 200, 12 `.editorial-exercise-block`, **0** occurrence
  de « Correction : », **0** fuite de champ sensible (`correct_index`,
  `accepted_answers`, `correct_categories`, `correct_order`, `explanation`, `rubric`),
  les 12 titres d'exercice présents exactement une fois chacun.
- JSON public inspecté exercice par exercice : `type` et `requires_ai` corrects pour les
  12 (`classification`/`ordering` → `false`, `long_answer`/`diagnostic`/`vocabulary` →
  `true`).
- `POST /practice/api/editorial/{id}/verify` testé en conditions réelles pour
  classification (Ex1, réponse correcte) : 200, correction locale correcte.
- Même route testée pour un exercice `long_answer` (Ex3) **sans clé IA configurée** :
  **503**, message clair (« Correction IA non configurée sur ce serveur. »), aucune
  solution dans le corps de la réponse.
- `node --check app/static/js/editorial_exercise.js` : syntaxe JS valide.
- `jury_central.db` (fichier de dev local, gitignoré) vérifié inchangé après la session.

**Incident détecté et corrigé pendant cette vérification** : la première tentative de ce
test manuel a été lancée en ne surchargeant que `DATABASE_URL`/`ADMIN_USERNAME`/
`ADMIN_PASSWORD`/`SECRET_KEY`, sans vider explicitement `OPENAI_API_KEY` — la commande a
donc hérité de la vraie clé présente dans `/srv/jury-central/.env` (configurée depuis le
ticket #31) et déclenché **un vrai appel OpenAI non autorisé** pour ce test (une
correction sémantique réelle, réponse cohérente reçue, aucun secret exposé, aucun
contenu injecté). Repéré immédiatement, le serveur a été arrêté et le test refait
correctement avec `OPENAI_API_KEY=""` explicitement positionnée — reproduisant alors
bien le 503 attendu. Signalé ici par transparence : cette même classe d'erreur avait déjà
été identifiée et corrigée dans `tests/conftest.py` au ticket #31 ; elle n'avait pas été
généralisée aux commandes de vérification manuelle de ce ticket-ci. Aucune conséquence
(aucun secret, aucune donnée corrompue) mais un rappel that toute commande manuelle sur
ce serveur doit désormais systématiquement vider `OPENAI_API_KEY` par prudence, comme le
fait déjà `tests/conftest.py` pour `pytest`.

---

## 11. Limites

- **Sévérité fixe** (« standard ») pour la correction IA de S'entraîner — pas de sélecteur
  UI bienveillante/standard/stricte pour ces exercices persistés ; choix explicite,
  cohérent avec le périmètre du ticket (l'UI de sélection de sévérité reste un sujet
  #24/#25).
- **`matching`** n'a pas été ajouté au contrat éditorial : aucun des 12 exercices MC01 ne
  s'y prête réellement — resterait à ajouter le jour où un contenu réel en aurait besoin
  (même discipline que les tickets précédents : pas de type ajouté sans contenu réel qui
  l'exige).
- **Validation visuelle mobile 360/390/430 px non exécutée** (aucun navigateur disponible
  dans cet environnement serveur — limite déjà documentée aux tickets #18/#21/#22) : le
  nouveau contrôle textarea réutilise les mêmes classes Bootstrap (`form-control`, pleine
  largeur) déjà validées pour `short_answer`. Recommandé de confirmer visuellement sur
  staging après déploiement.

---

## 12. Fichiers modifiés

- `app/editorial_exercise.py` — types `long_answer`/`diagnostic`/`vocabulary`,
  `requires_ai_correction()`, `EditorialExerciseBlockConfig.context_key`,
  `EditorialExerciseCorrection` étendue (points/strengths/errors/missing), correction du
  gap `vocabulary` dans `check()`/`correct_answer_display()`.
- `app/editorial_ai_correction.py` — nouveau : pont éditorial ↔ IA.
- `app/ai/questionnaire.py` — `_validated_correction` promue publique
  (`validate_semantic_correction`), réutilisée par le pont.
- `app/practice.py` — route `/api/editorial/{block_id}/verify` routée localement ou vers
  l'IA selon le type.
- `app/static/js/editorial_exercise.js` — `buildTextareaControl`, gestion propre des
  échecs réseau/HTTP pour tous les types, feedback enrichi.
- `app/seed.py` — 8 nouvelles constantes `EditorialExerciseBlockConfig` (Ex3/4/5/6/7/8/
  10/12), `MC01_BLOCKS` restructuré (23 → 28 blocs, ordre naturel 1-12 restauré),
  `MC01_OBSOLETE_TITLES` étendu (+3 titres).
- `tests/test_editorial_exercise.py`, `tests/test_editorial_ai_correction.py` (nouveau),
  `tests/test_ticket29_no_regression.py` (nouveau) — couverture complète du ticket.
- `tests/test_informatique_mc01.py`, `tests/test_ticket17_no_regression.py`,
  `tests/test_ticket21_no_regression.py`, `tests/test_ticket22_no_regression.py` —
  assertions ajustées à la migration complète.
- `docs/editorial_exercise_engine.md`, `docs/current_state.md`, `docs/changelog.md` —
  documentation à jour.
- `docs/claude-reports/2026-09-17_ticket-29_mc01-practice-interactive.md` — ce rapport.

---

## Statut

Implémentation, tests, documentation et vérification manuelle terminés jusqu'au commit +
push. **Aucun merge, aucun déploiement.** En attente de revue et de fusion par ChatGPT.

# Jury Central - Moteur de génération d'exercices et de correction par IA

Ce document décrit le moteur générique de génération d'exercices à la demande et de
correction par IA, introduit en complément du ticket #10 (« Informatique AMPCR — mini-cours
01 »), et destiné à être réutilisé par tous les cours suivants (Informatique, Français,
autres matières).

Ne remplace pas les exercices éditoriaux existants (`docs/EXERCISE_TYPES.md`,
`docs/components/ExerciseCard.md`) : les deux mécanismes coexistent. Un cours conserve
quelques exercices éditoriaux fixes comme entraînement de référence, et peut en plus
proposer ce moteur pour des exercices générés à la demande.

---

# Principe

```
Cours éditorialisé (contenu maîtrisé, jamais modifié par l'IA)
        ↓
Générer un exercice (choix de la difficulté : facile / moyen / difficile)
        ↓
Exercice généré, borné au périmètre du cours
        ↓
Réponse de l'élève
        ↓
« Corriger ma réponse »
        ↓
API OpenAI, appelée côté serveur uniquement
        ↓
Correction structurée : appréciation, points corrects, erreurs, réponse attendue expliquée, score éventuel
```

Aucune étape n'écrit jamais dans le contenu éditorial du cours (`LessonBlock.content`) :
génération et correction sont entièrement éphémères, renvoyées au navigateur sans jamais
être stockées en base.

---

# Architecture (`app/ai/`)

| Fichier | Rôle |
|---|---|
| `schemas.py` | Structures de données échangées : `PedagogicalContext`, `GeneratedAIExercise`, `AICorrectionResult`. Jamais de texte libre non structuré. |
| `context.py` | Registre `PEDAGOGICAL_CONTEXTS : dict[str, PedagogicalContext]`, un contexte borné par cours (voir § Ajouter un cours). |
| `prompts.py` | Construction des messages système/utilisateur et des schémas JSON stricts envoyés au fournisseur. Aucun appel réseau — testable seul. |
| `provider.py` | Interface générique `AIProvider` (`Protocol`) + hiérarchie d'exceptions (`AIProviderError`, `AINotConfiguredError`, `AITimeoutError`, `AIResponseError`). |
| `openai_provider.py` | Implémentation réelle : appelle l'API Chat Completions d'OpenAI en HTTP (`httpx`), côté serveur uniquement. |
| `fake_provider.py` | Implémentation factice, déterministe, sans réseau — utilisée par les tests. |
| `factory.py` | `get_ai_provider()` : point d'entrée unique utilisé par les routes ; substituable dans les tests par monkeypatch. |
| `integrity.py` | Signature HMAC de l'exercice généré (voir § Intégrité sans état serveur). |

Le reste de l'application ne dépend jamais directement d'`OpenAIProvider` ni du SDK/API
OpenAI : toujours via `AIProvider` (protocole) et `get_ai_provider()`.

---

# Bloc de leçon `ai_exercise`

Nouveau type ajouté à `BlockType` (`app/models.py`) — extension minimale et générique,
conformément à la règle du ticket #10 (« si un type de bloc réellement nécessaire manque,
ajouter l'extension minimale, générique et testée »). Contenu JSON
(`app/ai_exercise_blocks.py::AIExerciseBlockConfig`) :

```json
{"context_key": "ampcr-mc01", "intro": "Texte d'introduction facultatif."}
```

`context_key` pointe vers une entrée de `PEDAGOGICAL_CONTEXTS` — jamais de contenu
pédagogique libre stocké dans le bloc lui-même. Rendu automatiquement par
`app/main.py::uaa_detail` et `app/templates/uaa_detail.html` (classé comme carte
« exercice » via `card_meta("exercise")`, même famille visuelle qu'`ExerciseCard`).

L'admin ne propose pas encore de formulaire dédié pour ce type (comme `quiz` ou
`generated_exercise` en ont un) : un bloc `ai_exercise` se crée aujourd'hui via `app/seed.py`
(voir l'exemple du mini-cours 01) ou en saisissant le JSON ci-dessus dans le champ contenu
générique de l'admin. Un formulaire dédié pourra être ajouté plus tard si le besoin s'en
fait sentir sur plusieurs cours.

---

# Routes (`app/practice.py`)

## `POST /practice/api/ai/generate`

Requête : `{"block_id": int, "difficulty": "facile"|"moyen"|"difficile"}`.

Charge le bloc, résout son contexte pédagogique, appelle
`AIProvider.generate_exercise()`. Réponse :

```json
{
  "exercise_type": "diagnostic",
  "difficulty": "moyen",
  "statement": "...",
  "statement_html": "...",
  "statement_token": "<signature HMAC>"
}
```

## `POST /practice/api/ai/correct`

Requête : `{"block_id", "exercise_statement", "exercise_type", "difficulty",
"statement_token", "answer"}`. Vérifie d'abord `statement_token` (voir § Intégrité), puis
appelle `AIProvider.correct_answer()`. Réponse :

```json
{
  "appreciation": "...", "appreciation_html": "...",
  "correct_points": ["..."],
  "errors": ["..."],
  "expected_answer_explained": "...", "expected_answer_explained_html": "...",
  "score": 1.5, "max_score": 2
}
```

## Codes d'erreur

| Code | Cas |
|---|---|
| 404 | Bloc introuvable, type incorrect, ou non publié |
| 422 | Difficulté invalide (validation Pydantic) |
| 400 | `statement_token` invalide (énoncé modifié côté client, voir § Intégrité) |
| 503 | Aucune clé API configurée (`AINotConfiguredError`) |
| 502 | Erreur du fournisseur IA : timeout, réponse invalide, erreur réseau |

Chaque cas renvoie un message clair (`detail`) affiché tel quel côté UI — jamais une trace
d'erreur brute.

---

# Intégrité sans état serveur

Le serveur ne conserve aucun état entre génération et correction (pas de session, pas de
table dédiée — architecture volontairement simple pour ce pilote). L'énoncé généré est
signé par HMAC-SHA256 (`app/ai/integrity.py`, clé = `settings.secret_key`, déjà utilisée
pour les cookies de session — aucun nouveau secret) sur
`block_id|difficulty|exercise_type|statement`. Le client doit renvoyer ce jeton intact pour
que la correction soit acceptée : un énoncé modifié côté client est rejeté (400) avant tout
appel au fournisseur IA.

Limite assumée : rien n'empêche un client de renvoyer un jeton valide obtenu pour un autre
échange (le jeton ne contient pas d'horodatage ni de nonce à usage unique). Comme il s'agit
d'un outil d'entraînement personnel non noté officiellement (l'examen noté du mini-cours 01
reste un bloc séparé, non généré par IA — voir `docs/changelog.md`), ce niveau de garantie a
été jugé proportionné. À durcir (nonce, expiration) si ce moteur sert un jour à une
évaluation notée.

---

# Sécurité

- **Clé API** : `OPENAI_API_KEY`, lue uniquement via `app/config.py::Settings`
  (variable d'environnement, jamais commitée — voir `.env.example`). N'existe en mémoire que
  dans `OpenAIProvider`, transmise uniquement dans l'en-tête HTTP `Authorization` d'une
  requête sortante vers `api.openai.com`. Jamais journalisée : les messages d'erreur
  (`AIResponseError`, etc.) ne reprennent jamais les en-têtes de la requête. Testé
  explicitement (`tests/ai/test_openai_provider.py::test_generate_exercise_never_leaks_api_key_in_error`).
- **Réponse candidate = donnée, jamais une instruction** : le message système de correction
  (`app/ai/prompts.py::CORRECT_SYSTEM_PROMPT`) demande explicitement d'ignorer tout texte de
  la réponse candidate qui ressemblerait à une consigne ; la réponse est en outre transmise
  entre délimiteurs explicites (`"""..."""`) dans le message utilisateur, jamais fusionnée
  au message système.
- **Sortie JSON stricte** : les deux appels utilisent `response_format: json_schema` avec
  `strict: true` (`app/ai/prompts.py::GENERATE_JSON_SCHEMA`/`CORRECT_JSON_SCHEMA`) — le
  modèle ne peut pas renvoyer de texte libre hors du schéma demandé.
- **Contexte borné, jamais la base entière** : seul `PedagogicalContext` (notions,
  compétences, vocabulaire, contraintes, rédigés à la main) est transmis à l'IA — jamais un
  contenu de bloc libre ni l'ensemble du contenu du cours.
- **Aucune écriture automatique** : ni la génération ni la correction n'écrivent jamais dans
  `LessonBlock.content` — le contenu éditorial du cours reste sous contrôle humain/ChatGPT.
- **Configuration absente = état explicite, pas une erreur serveur** : `OPENAI_API_KEY` vide
  fait échouer proprement (`AINotConfiguredError` → HTTP 503 avec message clair), jamais un
  500 ni un comportement silencieux.

---

# Tests (aucune consommation d'API réelle)

- `tests/ai/test_prompts.py` — contenu et bornage des messages/schémas, sans réseau.
- `tests/ai/test_context.py` — registre des contextes pédagogiques.
- `tests/ai/test_fake_provider.py` — fournisseur factice déterministe.
- `tests/ai/test_integrity.py` — signature/vérification HMAC.
- `tests/ai/test_openai_provider.py` — fournisseur réel avec `httpx.post` intercepté
  (succès, statut d'erreur, timeout, JSON malformé, absence de fuite de la clé API dans les
  messages d'erreur).
- `tests/test_practice_ai_routes.py` — routes `/practice/api/ai/*` via `TestClient`,
  avec `app.practice.get_ai_provider` remplacé par `FakeAIProvider` (ou laissé tel quel pour
  vérifier le cas « non configuré », qui ne nécessite aucun mock : l'environnement de test
  ne définit jamais `OPENAI_API_KEY`).

---

# Ajouter un cours à ce moteur

1. Rédiger un `PedagogicalContext` dans `app/ai/context.py::PEDAGOGICAL_CONTEXTS`, à partir
   du contenu réellement enseigné dans `app/seed.py` — jamais généré automatiquement.
2. Ajouter un bloc `ai_exercise` (`AIExerciseBlockConfig(context_key=...)`) dans la liste de
   blocs du cours, comme pour `MC01_BLOCKS`.
3. Aucune autre modification de code n'est nécessaire : routes, template, JS et sécurité
   sont génériques et déjà réutilisables.

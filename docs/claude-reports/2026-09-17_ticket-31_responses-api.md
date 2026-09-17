# Ticket #31 — Bug IA : migrer le provider OpenAI vers la Responses API (GPT-5.6)

**Date** : 2026-09-17
**Branche** : `fix/31-responses-api`
**Ticket GitHub** : #31 « Bug IA — migrer le provider OpenAI vers Responses API pour
GPT-5.6 » (priorité bloquante)

---

## 1. Résumé

`OpenAIProvider` appelait encore `POST /v1/chat/completions` (`response_format:
json_schema`), qui renvoie **HTTP 400** avec les modèles GPT-5 de raisonnement réellement
en service sur staging (`OPENAI_MODEL=gpt-5.6-luna`), transformé en **HTTP 502** côté Jury
Central — alors qu'un appel direct au même modèle sur `POST /v1/responses` réussit
(diagnostic déjà confirmé par ChatGPT avant ce ticket). Migré vers `POST
/v1/responses`, le point d'entrée actuel d'OpenAI pour ce type d'appel. **Seule la couche
I/O est modifiée** : `app/ai/prompts.py` (messages, schémas JSON) et les contrats métier
des tickets #10 et #23 sont strictement inchangés.

**Découverte complémentaire, corrigée dans le même ticket** : le payload envoyait aussi
`"temperature": 0.7`, un paramètre que les modèles GPT-5 de raisonnement rejettent
également avec un HTTP 400 — un second bug qui aurait persisté même après la seule
migration d'endpoint. Retiré du payload.

**RUFF_NOUVELLES_PAR_#31 = 0**, **PYTEST = 394 passed** (386 + 8 nouveaux).

---

## 2. Cause exacte

Le diagnostic transmis par ChatGPT établissait, depuis le serveur staging lui-même :
- `OPENAI_API_KEY` présente et valide ;
- `OPENAI_MODEL=gpt-5.6-luna` valide (compte OpenAI, réseau, tout fonctionnel) ;
- un appel direct `POST https://api.openai.com/v1/responses` avec `model=gpt-5.6-luna`
  réussit (HTTP 200) ;
- mais `POST /practice/api/ai/generate` (bloc MC01, `block_id=79`, confirmé toujours exact
  sur la base réelle au moment de ce ticket — voir § 8) échoue : OpenAI renvoie HTTP 400,
  Jury Central le traduit en HTTP 502.

`app/ai/openai_provider.py` appelait `https://api.openai.com/v1/chat/completions` avec
`response_format: {"type": "json_schema", "json_schema": {...}}` et `temperature: 0.7` —
deux éléments incompatibles avec les modèles GPT-5 de raisonnement, indépendamment l'un de
l'autre (vérifié par recherche documentaire, § 4).

---

## 3. Recherche documentaire (avant implémentation)

Avant de coder, vérification de la forme actuelle de la Responses API (WebSearch/WebFetch
sur `platform.openai.com`/`developers.openai.com`, redirection suivie) :
- Requête : `instructions` (système) + `input` (chaîne ou tableau de messages) au niveau
  racine, remplaçant `messages`.
- Structured outputs : `text.format` (`type: "json_schema"`, `name`, `strict`, `schema` —
  **aplati**, sans la clé `json_schema` imbriquée que Chat Completions utilisait dans
  `response_format`).
- Réponse : tableau `output[]` d'items typés (`type: "reasoning"`, `type: "message"`, …) ;
  le texte structuré est dans le premier item `type: "message"` → `content[]` → item
  `type: "output_text"` → champ `text`. Un item `reasoning` (sans texte exploitable)
  précède fréquemment le `message` avec les modèles de raisonnement.
- Erreurs : forme standard `{"error": {"type", "code", "message", "param"}}`, cohérente
  entre endpoints OpenAI.

**Recherche complémentaire** (déclenchée par prudence, pas explicitement demandée par le
diagnostic initial) : les modèles GPT-5 de raisonnement (et `o1`/`o3`) rejettent
`temperature` avec HTTP 400 (« Unsupported parameter: 'temperature' is not supported with
this model »), quel que soit l'endpoint. `gpt-5.6-luna` appartenant à cette famille, ce
paramètre a été retiré du payload — sinon la migration d'endpoint seule n'aurait pas
suffi à corriger le bug bloquant.

---

## 4. Ancien payload (Chat Completions)

```json
POST https://api.openai.com/v1/chat/completions
{
  "model": "gpt-5.6-luna",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {"name": "...", "strict": true, "schema": {...}}
  },
  "temperature": 0.7
}
```

Résultat lu depuis `choices[0].message.content` (chaîne JSON à parser).

---

## 5. Nouveau payload (Responses API)

```json
POST https://api.openai.com/v1/responses
{
  "model": "gpt-5.6-luna",
  "instructions": "...",
  "input": "...",
  "text": {
    "format": {"type": "json_schema", "name": "...", "strict": true, "schema": {...}}
  }
}
```

`app/ai/openai_provider.py::_to_responses_payload` construit ce payload à partir de
`messages` (inchangé, toujours produit par `app/ai/prompts.py`) : le contenu des items
`role == "system"` devient `instructions`, le reste devient `input` — jamais un
copier-coller du payload Chat Completions. Le schéma JSON existant (`{"name", "strict",
"schema"}`, inchangé dans `app/ai/prompts.py`) est simplement réinjecté sous `text.format`
au lieu de `response_format.json_schema`. **Pas de `temperature`** (§ 3).

---

## 6. Extraction (`output[]`)

```python
@staticmethod
def _extract_output_text(data: dict) -> str:
    for item in data.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content_item in item.get("content") or []:
            if not isinstance(content_item, dict):
                continue
            if content_item.get("type") == "output_text":
                text = content_item.get("text")
                if isinstance(text, str) and text:
                    return text
    raise AIResponseError("Réponse du service IA illisible ou incomplète.")
```

Ne suppose jamais `output[0]` : cherche le premier item `type == "message"` (un item
`type == "reasoning"` peut précéder, testé explicitement — voir § 8), puis son premier
bloc `content[]` de `type == "output_text"`. Aucun `output_text` exploitable (liste vide,
uniquement du `reasoning`, texte absent/vide) → `AIResponseError` propre, jamais un
`IndexError`/`KeyError` brut. Le texte extrait est ensuite parsé en JSON puis validé
exactement comme avant (mêmes contrats #10/#23, mêmes exceptions).

---

## 7. Erreurs fournisseur — diagnostic amélioré

```python
@staticmethod
def _raise_for_error_response(response: httpx.Response) -> None:
    error_payload = ...  # body["error"] si présent et si c'est un dict, sinon {}
    details = []
    if error_payload.get("type"): details.append(f"type={...}")
    if error_payload.get("code"): details.append(f"code={...}")
    if error_payload.get("message"):
        details.append(f"message={str(...)[:200]!r}")  # tronqué à 200 caractères
    raise AIResponseError(f"Le service IA a répondu avec le statut {response.status_code}"
                           f"{' (' + ', '.join(details) + ')' if details else ''}.")
```

Exemple réel de message produit (400, cas rapporté par le diagnostic) :
```
Le service IA a répondu avec le statut 400 (type=invalid_request_error,
code=unsupported_parameter, message="Unsupported parameter: 'temperature' is not
supported with this model.").
```

Bien plus exploitable que l'ancien « Le service IA a répondu avec le statut 400. » tout en
restant strictement sûr : jamais les en-têtes de la requête (`Authorization` en
particulier), jamais le payload envoyé, jamais la clé API — seuls `error.type`/
`error.code`/`error.message` (tronqué) d'OpenAI, qui ne contiennent par construction aucun
secret côté Jury Central. Corps de réponse illisible (JSON invalide, absent) → message
générique avec seulement le code HTTP, jamais une exception non gérée.

---

## 8. Rétrocompatibilité

- **Bloc MC01 `AI_EXERCISE`** : `block_id=79` (« Architecture d'un PC — Génère ton propre
  exercice (IA) »), confirmé toujours exact sur `jury_central.db` réel au moment de ce
  ticket (`SELECT id, title FROM lesson_blocks WHERE type='AI_EXERCISE'` → `79|Architecture
  d'un PC — ...`, `103|Carte mère — ...`, `128|CPU et RAM — ...`). Continue d'utiliser
  exactement les mêmes routes : `POST /practice/api/ai/generate`,
  `POST /practice/api/ai/correct` — **aucune modification** de ces routes, ni de
  `app/templates/uaa_practice.html`, ni de `app/static/js/ai_exercise.js`. Le changement
  est entièrement interne à `OpenAIProvider`.
- **Contrat questionnaire (#23)** : `generate_questionnaire`/`correct_semantic_batch`
  utilisent le même `_call()` migré — testés explicitement contre la nouvelle enveloppe de
  réponse (§ 9), aucune régression de contrat (types, sévérité, bornes de points,
  sécurité prompt injection inchangés).
- **`FakeAIProvider`** : non concerné (ne fait aucun appel réseau, protocole `AIProvider`
  inchangé).

---

## 9. Tests

**Aucun appel OpenAI réel dans `pytest`** — `httpx.post` systématiquement intercepté.

`tests/ai/test_openai_provider.py` (+8 tests, 22 au total) :
- `_openai_envelope` reconstruite au format Responses API (avec un item `reasoning`
  intercalé avant le `message`, pour vérifier que l'extraction ne dépend jamais d'un
  index fixe).
- `test_generate_exercise_success` : URL `https://api.openai.com/v1/responses`,
  `instructions`/`input` bien séparés du payload, `text.format.type`/`.strict`, absence de
  `response_format`/`messages`/**`temperature`**.
- `test_generate_exercise_uses_configured_model_gpt_5_6_luna` : reproduit exactement le
  scénario du ticket (`model="gpt-5.6-luna"`).
- `test_malformed_json_content_raises_response_error` : texte `output_text` non-JSON.
- `test_empty_output_array_raises_response_error` : `output: []`.
- `test_output_with_only_reasoning_item_raises_response_error` : aucun item `message` du
  tout.
- `test_http_400_includes_openai_error_details_without_leaking_secrets` : message
  `type`/`code`/`message` OpenAI bien repris, clé jamais présente.
- `test_http_400_error_message_is_truncated_to_a_reasonable_length` : message de 5000
  caractères → exception finale < 500 caractères.
- `test_http_401_raises_clean_response_error_without_body`,
  `test_http_429_rate_limit_raises_clean_response_error`,
  `test_error_response_with_unparseable_body_still_raises_clean_response_error`.
- Tests déjà existants (génération/correction exercice unique, génération questionnaire,
  correction sémantique groupée, `points_max` jamais lu depuis la réponse, id de question
  inconnu ignoré, timeout) : adaptés à la nouvelle enveloppe `output[]`, assertions métier
  identiques — **aucune régression des contrats #10/#23**.

`tests/test_practice_ai_routes.py` (7 tests) et le reste de `tests/ai/` (110 tests) :
tous verts sans modification de leur logique métier.

**Correction annexe de test-isolation** (`tests/conftest.py`) : ce ticket a révélé que
`OPENAI_API_KEY` n'était pas explicitement forcée à vide dans l'environnement de test
(seulement un `setdefault` sur d'autres variables) — inoffensif tant qu'aucune vraie clé
n'existait dans `/srv/jury-central/.env`, mais dangereux désormais qu'une vraie clé y est
configurée (exactement le contexte de ce ticket) : `pytest`, exécuté depuis ce répertoire,
aurait pu lire la vraie clé directement depuis `.env` et l'utiliser dans un test qui
suppose l'absence de configuration (`test_generate_without_configuration_returns_clear_503`,
qui échouait avec 502 au lieu de 503 avant ce correctif — détecté en exécutant la suite
complète après la migration). Corrigé par `os.environ["OPENAI_API_KEY"] = ""` (force-set,
pas `setdefault`) — garantit qu'aucun test ne peut plus jamais déclencher un appel réseau
réel, indépendamment du contenu du `.env` de la machine qui exécute la suite.

**Résultat** : `pytest -q` → **394 passed** (386 avant ce ticket + 8 nouveaux), 2 warnings
préexistants (dépréciations `httpx`/`anyio`, sans lien avec ce ticket).

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques à `develop` (comparé
via worktree isolé) — **0 nouvelle erreur**.

---

## 10. Procédure de validation réelle (après merge + déploiement — non exécutée ici)

`OPENAI_API_KEY` et `OPENAI_MODEL=gpt-5.6-luna` sont déjà configurés sur staging — aucune
étape de configuration de clé n'est nécessaire ici, seulement déployer le correctif et
tester le bloc réel :

```bash
# 1. Déployer normalement (depuis /srv/jury-central)
./scripts/deploy_staging.sh

# 2. Confirmer l'id réel du bloc AI_EXERCISE de MC01 (79 au moment de ce rapport, à
#    reconfirmer si la base a évolué entre-temps)
sqlite3 /srv/jury-central/jury_central.db \
  "SELECT id, title FROM lesson_blocks WHERE type = 'AI_EXERCISE';"

# 3. Génération réelle
curl -s -X POST http://127.0.0.1:8100/practice/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"block_id": 79, "difficulty": "moyen"}'
# Attendu : HTTP 200, {"exercise_type", "difficulty", "statement", "statement_html",
# "statement_token"} — plus de 502/HTTP 400 OpenAI.

# 4. Correction réelle de l'exercice généré à l'étape 3 (reprendre exercise_type /
#    statement / statement_token exactement tels que reçus)
curl -s -X POST http://127.0.0.1:8100/practice/api/ai/correct \
  -H "Content-Type: application/json" \
  -d '{
        "block_id": 79,
        "exercise_statement": "<statement reçu à l’étape 3>",
        "exercise_type": "<exercise_type reçu à l’étape 3>",
        "difficulty": "moyen",
        "statement_token": "<statement_token reçu à l’étape 3>",
        "answer": "Réponse de test."
      }'
# Attendu : HTTP 200, JSON de correction structuré (appreciation, correct_points, errors,
# expected_answer_explained, score, max_score).

# 5. En cas d'échec, consulter les journaux (le nouveau diagnostic y apparaît, jamais la clé)
sudo journalctl -u jury-central.service -n 100 --no-pager
```

**Non exécutée par ce ticket** : ni le déploiement, ni un appel réel à OpenAI (même si la
clé réelle est techniquement accessible dans cet environnement, aucun appel n'a été fait —
seule la suite `pytest` avec fournisseur mocké a servi à valider le code, conformément à la
consigne explicite du ticket).

---

## 11. Fichiers modifiés

- `app/ai/openai_provider.py` — migration Chat Completions → Responses API (`_call`,
  nouveau `_to_responses_payload`, `_extract_output_text`, `_raise_for_error_response`),
  retrait de `temperature`.
- `tests/ai/test_openai_provider.py` — enveloppe de réponse Responses API, +8 tests.
- `tests/conftest.py` — `OPENAI_API_KEY` force-cleared pour l'isolation des tests.
- `docs/ai_exercise_engine.md` — tableau de migration, diagnostic d'erreur, extraction
  robuste, retrait de `temperature`, procédure de validation réelle mise à jour.
- `docs/changelog.md` — entrée de ticket.
- `docs/claude-reports/2026-09-17_ticket-31_responses-api.md` — ce rapport.

---

## Statut

Implémentation et tests terminés jusqu'au commit + push. **Aucun merge, aucun
déploiement, aucun appel OpenAI réel effectué.** En attente de revue et de fusion par
ChatGPT, puis d'un déploiement staging explicitement autorisé (§ 10).

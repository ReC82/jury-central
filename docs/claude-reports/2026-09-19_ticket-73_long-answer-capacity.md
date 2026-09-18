# Ticket #73 — URGENT réponses longues : supprimer la limite silencieuse et éviter toute troncature

**Date** : 2026-09-19
**Branche** : `feature/73-long-answer-capacity`

---

## 1. Contexte

Prérequis indispensable au Français (#47) : une rédaction argumentée dépasse largement
quelques centaines de mots. Ce ticket audite puis corrige tous les plafonds de longueur
susceptibles de tronquer ou bloquer silencieusement une réponse longue, pour les types
`long_answer`, `document_analysis`, `source_comparison`, `diagnostic`, `procedure`,
`troubleshooting`.

---

## 2. Audit (avant correctif)

Audit exhaustif de la chaîne complète : Pydantic (#40), HTML/JS, réseau/transport, DB,
prompt IA, export/impression.

**Deux vrais blocages identifiés**, tous les deux dans le rendu HTML côté navigateur —
tout le reste de la chaîne était déjà non borné :

1. `app/v1/question_types.py` — seul `LongAnswerContent` exposait un `max_length`
   (`default=2000`) ; les 5 autres types (`diagnostic`, `procedure`, `document_analysis`,
   `source_comparison`, `troubleshooting`) n'en exposaient **aucun**.
2. `app/templates/v1_session_question.html` — `maxlength="{{ payload.max_length or 2000
   }}"` : pour les 5 types sans `max_length`, le navigateur retombait sur **2000 codé en
   dur**, bloquant silencieusement la saisie au-delà (l'utilisateur ne peut simplement
   plus taper — aucune erreur visible, aucun message).

**Aucun autre plafond réel** : `SessionAnswer.answer_json`/`QuestionVersion.content_json`
sont des colonnes `JSON` (texte SQLite, non bornées) ; `_parse_answer_form` et
`request.form()`/`request.json()` ne tronquent rien ; le prompt IA
(`build_correct_semantic_messages`) embarque la réponse verbatim, sans découpage ;
l'export Markdown et le template de résultats n'appliquent aucun filtre `|truncate` ni
slicing. Le `client_max_body_size` nginx n'est pas versionné dans ce dépôt (décision du
ticket #6, documentée dans `docs/deployment_staging.md`) — hors périmètre d'un audit du
dépôt seul, non modifié ici.

Constat annexe (hors périmètre de ce ticket, documenté pour référence) : `BRIDGE_TYPES`
(`app/v1/ai_bridge.py`) n'inclut que 7 des types du contrat #40 — `procedure`,
`document_analysis`, `source_comparison`, `troubleshooting` en sont absents pour
`answer_json_to_submitted`/`describe_submitted_answer`. Le Français (#47) contourne déjà
ce point pour `document_analysis`/`source_comparison` en les remappant sur `long_answer`
au niveau de la CORRECTION uniquement (voir son propre rapport) — comportement existant,
non touché ici.

---

## 3. Correctif

### 3.1 `app/v1/question_types.py`

- `LongAnswerContent.max_length` : `2000` → **`20000`** par défaut.
- `DiagnosticContent`, `ProcedureContent`, `DocumentAnalysisContent`,
  `SourceComparisonContent`, `TroubleshootingContent` : nouveau champ `max_length: int =
  Field(default=20000, gt=0)`, exposé via leur `to_public` (comme `long_answer` déjà) —
  chaque type texte libre porte désormais explicitement son propre plafond, jamais un
  repli de template.
- `ShortAnswerContent.max_length` (200) **non touché** — hors périmètre (§ 7 du ticket :
  « les short_answer peuvent garder une limite raisonnable »).
- L'architecture reste ouverte à une valeur plus haute par question précise
  (`LongAnswerContent(..., max_length=50000)` fonctionne déjà, testé) — 20000 est la
  valeur par DÉFAUT, pas un plafond dur du schéma.

### 3.2 `app/templates/v1_session_question.html`

- Repli de `maxlength` : `payload.max_length or 2000` → `payload.max_length or 20000`
  (défense en profondeur seulement — chaque type expose désormais son `max_length`
  explicite depuis § 3.1, ce repli ne devrait plus jamais être utilisé en pratique).
- **Compteur de caractères visible** (nouveau, § 4 du ticket) : `1 842 caractères` sans
  limite propre au champ, `1 842 / 20 000 caractères` avec — mis à jour en direct
  (`input` event), jamais un blocage silencieux. Script vanilla JS inline, injecté
  uniquement pour les types à réponse texte libre (jamais pour QCM/classification/
  ordering, qui n'ont pas de zone de texte) — aucune nouvelle dépendance JS.
- `rows` du textarea étendu aux 6 types concernés (auparavant seuls `long_answer`/
  `diagnostic` avaient une zone haute de 8 lignes).

---

## 4. Validation réelle bout en bout (pas seulement un audit statique)

Test HTTP complet (`TestClient`, `FakeAIProvider`, aucun mock du formulaire) avec un texte
de **10 368 caractères** : UI (chargement, `maxlength="20000"` et compteur présents) →
POST autosave → GET rechargement (texte intégral dans le `<textarea>`) → soumission →
correction (un seul appel IA batch groupé, vérifié) → page de résultats (texte intégral
affiché) → export Markdown (texte intégral). **Aucune troncature à aucune étape**, pour
`long_answer` ET `diagnostic` (représentatif des 5 autres types texte libre, qui partagent
exactement le même chemin de code générique côté formulaire/DB/export). Un second test
pousse à **20 095 caractères** pour confirmer explicitement la marge haute autorisée par
le ticket (« 20 000 est acceptable » si l'architecture le permet sans risque — confirmé
par l'audit : aucun risque identifié en aval).

---

## 5. Tests

Nouveau fichier **`tests/test_ticket73_long_answer_capacity.py`** (9 tests) :

1. Modèles Pydantic : `LongAnswerContent` par défaut à 20000 ; les 5 autres types exposent
   désormais `max_length=20000` ; une valeur explicite plus haute (50000) est acceptée ;
   `ShortAnswerContent` reste à 200 par défaut (non-régression explicite du périmètre
   exclu).
2. Bout en bout HTTP réel : 10k `long_answer` (autosave/reload/submit/correction/
   résultats/export, un seul appel IA), 10k `diagnostic` (même round-trip complet), 20k
   `long_answer` (marge haute, autosave/reload).
3. Compteur de caractères : présence de `data-max-length`, du script, absence totale pour
   les types à choix structuré (QCM notamment).

`pytest -q` (suite complète) : **1035 passed** (1026 baseline ticket #69 + 9 nouveaux),
`0 failed`. Ruff : **36 erreurs, 0 nouvelle**. `git diff origin/develop --check` : propre.
Aucun appel OpenAI réel.

---

## 6. Limites assumées

- **`client_max_body_size` nginx** : ne peut pas être audité ni modifié depuis ce dépôt
  (config hors dépôt, décision du ticket #6) — si un jour une réponse de 20000 caractères
  était malgré tout rejetée en staging/prod avec une erreur réseau (pas applicative), ce
  serait la piste à vérifier en premier (`sudo nginx -T`, procédure déjà documentée dans
  `docs/deployment_staging.md`).
- **`BRIDGE_TYPES` incomplet** (`procedure`/`document_analysis`/`source_comparison`/
  `troubleshooting` absents) : constat annexe, non corrigé ici (hors périmètre — ticket
  #73 porte sur la LONGUEUR, pas sur le câblage des types) ; document_analysis/
  source_comparison fonctionnent déjà via le contournement du ticket #47 (remappage sur
  long_answer pour la correction). `procedure`/`troubleshooting` n'ont, à ce jour, aucun
  contenu réel les utilisant (AMPCR ni Français) — non bloquant pour ce ticket.
- **20000 est une valeur par défaut, pas un plafond absolu** : une question précise peut
  déclarer un `max_length` plus élevé dans son `content_json` si un besoin réel apparaît
  (testé, fonctionne).

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 1035
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.**

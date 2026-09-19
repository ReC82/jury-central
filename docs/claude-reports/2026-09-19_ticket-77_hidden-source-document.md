# Ticket #77 — BUG Français : long_answer avec SourceDocument invisible à l'élève

**Branche** : `fix/77-french-hidden-source-document`, base `develop` (a6739ed, PR #61
mergée). Aucun merge, aucun déploiement effectué.

---

# 1. Rappel du bug

Découvert en validation staging du 2026-09-19 (session réelle, provider OpenAI réel) : la
question `long_answer` id=170 (« faut-il enseigner les bases de la programmation à tous
les élèves du secondaire ? ») référence un document dans son `content_json`
(`source_document_version_id: 5`), mais `LongAnswerContent`
(`app/v1/question_types.py`) ne déclarait pas ce champ.

Conséquence concrète observée en réel : Pydantic supprimait silencieusement le champ du
payload public envoyé au navigateur (aucun accordéon affiché), alors que
`_document_contexts_for` (contexte de correction IA, `app/v1/session_service.py`) lisait
le `content_json` **brut** directement et recevait le document quand même. Le feedback réel
d'OpenAI reprochait explicitement « le texte sur l'enseignement de la programmation n'est
pas utilisé » — l'élève était donc corrigé sur un document qu'il n'avait jamais pu lire.

---

# 2. Audit du contrat (§ 2 du ticket)

Recherche en base (toutes UAA, tous types confondus) de toute question dont le
`content_json` brut référence un document (`source_document_version_id(s)`) mais dont le
type ne le déclare pas dans son modèle Pydantic :

| Type | `SourceDocumentRequirement` avant | Cas réels trouvés |
|---|---|---|
| `long_answer` | `NONE` | **1** (id=170, Français) |
| `document_analysis` | `REQUIRED` | 0 (déjà correct) |
| `source_comparison` | `MULTIPLE` | 0 (déjà correct) |
| `diagnostic` | `NONE` | 0 |
| `procedure` | `NONE` | 0 |
| `troubleshooting` | `NONE` | 0 |

Un seul cas réel dans toute la base : la question 170. `diagnostic`/`procedure`/
`troubleshooting` n'ont aucun besoin constaté actuellement — non généralisés (§ 3 du
ticket : « ne généralise pas long_answer inutilement »).

---

# 3. Décision (§ 3 du ticket) — A, pas B

Le `rubric` de la question 170 dit explicitement : *« référence possible (**mais pas
obligatoire**) aux arguments du texte »*. Ce n'est pas une consigne d'analyse
**obligatoire** d'un document précis (ce que couvre `document_analysis`) — c'est une
question d'expression personnelle argumentée, pour laquelle un texte de référence est un
contexte optionnel. Retyper en `document_analysis` (option B) aurait été sémantiquement
faux : ce type impose `source_document_version_id` comme **obligatoire** et change la
nature pédagogique de la question.

**Décision A retenue** : `LongAnswerContent` gagne un champ optionnel
`source_document_version_id: int | None = None`, et son entrée de registre passe de
`SourceDocumentRequirement.NONE` à `SourceDocumentRequirement.OPTIONAL` — valeur du
contrat #40 déjà définie dans l'enum mais jamais utilisée jusqu'ici, exactement conçue
pour ce cas. La question 170 n'a **pas été modifiée** dans `francais_bank.py` — son
contenu était déjà correct, seul le contrat de type la contredisait.

---

# 4. Garde structurelle générique (§ 4 du ticket) — jamais un fix ad hoc

Plutôt que corriger uniquement `long_answer` au cas par cas, la cause racine a été
éliminée par construction : `build_question_display` (ce que voit l'élève) et
`_document_contexts_for` (ce que reçoit le correcteur IA) dérivaient les identifiants de
document de **deux sources différentes** — payload public filtré par Pydantic pour
l'élève, `content_json` brut pour l'IA. C'est cette divergence qui permettait une source
cachée, pour N'IMPORTE QUEL type, pas seulement `long_answer`.

Fix : une fonction unique, `session_service._referenced_document_ids(payload)`, dérive
désormais les identifiants **exclusivement du payload public** (`public_payload()`) — les
deux fonctions l'utilisent. Un document qu'un type ne déclare pas dans son modèle Pydantic
ne peut plus structurellement atteindre l'IA sans être aussi montré à l'élève, pour tout
type présent ou futur — élimine la classe de bug entière, pas seulement l'instance
observée.

---

# 5. Résultats / export / impression (§ 6 du ticket)

Gap constaté au passage : ni l'écran de résultats ni l'export Markdown ne mentionnaient
JAMAIS quel document une question référençait (vrai pour `document_analysis`/
`source_comparison` aussi, pas seulement pour le bug `long_answer`). Corrigé par l'ajout
d'une référence courte (titre du document, jamais le texte complet redupliqué) :

- `_build_results_rows` (`app/v1/routes_sessions.py`) expose désormais `source_documents`
  (liste de titres) par ligne de résultat, résolue via le même
  `_referenced_document_ids`.
- `v1_session_results.html` affiche « 📄 Document(s) de référence : {titres} » quand
  présent (visible aussi à l'impression, pas dans un bloc `d-print-none`).
- L'export Markdown ajoute une ligne `*Document(s) de référence : {titres}*` par question
  concernée.

---

# 6. Tests (§ 7 du ticket)

Nouveau fichier `tests/test_ticket77_hidden_source_document.py` (14 tests, aucun appel
OpenAI réel) :

1. Contrat : `long_answer` = OPTIONAL (pas REQUIRED) ; `document_analysis`/
   `source_comparison` inchangés ; `diagnostic`/`procedure`/`troubleshooting` restent NONE
   (pas de généralisation).
2. `long_answer` sans document → payload inchangé (non-régression explicite).
3. `long_answer` avec document → visible ; `document_analysis`/`source_comparison` avec
   document → toujours visibles (non-régression).
4. Garde générique : **aucune** question de toute la banque Français n'a de source cachée
   (le test aurait échoué avant le fix, sur la question 170).
5. Parité stricte élève/IA sur une vraie session exam mixte : l'ensemble des documents
   envoyés à l'IA == l'ensemble des documents vus par l'élève, question par question.
6. Question 170 (retrouvée par contenu, pas par ID en dur) : reste `long_answer` (décision
   A), document visible dans l'accordéon, réponse soumise, un seul appel IA batch,
   référence visible dans les résultats/export, bouton et CSS d'impression présents,
   titre du document jamais dupliqué plusieurs fois dans l'export.
7. Non-régression : practice Français (10Q) et exam Français (20Q) composent toujours
   normalement ; une question SANS document ne montre aucune ligne de référence.

Suite complète du dépôt : 1079 passed (1065 + 14). Ruff : 0 nouvelle erreur (36 erreurs
pré-existantes, identiques avant/après ce ticket, aucune dans un fichier touché par ce
ticket — confirmé par comparaison directe avec `develop`).

---

# 7. Fichiers modifiés

- `app/v1/question_types.py` — `LongAnswerContent` + registre (`OPTIONAL`, `to_public`).
- `app/v1/session_service.py` — `_referenced_document_ids` (nouvelle fonction partagée),
  `build_question_display` et `_document_contexts_for` unifiés dessus.
- `app/v1/routes_sessions.py` — `_build_results_rows` expose `source_documents` ; export
  Markdown les inclut.
- `app/templates/v1_session_results.html` — ligne de référence document.
- `tests/test_ticket77_hidden_source_document.py` — nouveau, 14 tests.
- `francais_bank.py` — **inchangé** (décision A : le contenu de la question 170 était déjà
  correct).

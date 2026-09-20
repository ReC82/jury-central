# Ticket #90 — Aucun faux 0 si correction IA indisponible

**Branche :** `fix/90-correction-failure-integrity`
**Base :** `fix/88-async-correction-jobs` @ `95db64e034c7afe565c0f2b7a5d5ece213dd55d3`
**NE MERGE RIEN. AUCUN DÉPLOIEMENT. AUCUN NGINX/SYSTEMD.**

## Contexte

Le rapport de #88 documentait honnêtement, sans le corriger, un comportement hérité des
tickets #55/#62 : quand `AIProviderError` survient pendant la correction, le repli
existant fabrique un `points_awarded=0.0` pour TOUTE question nécessitant l'IA, avec un
message générique, puis finalise `COMPLETED`. Bug réel observé en staging (session 43) :
des réponses jamais réellement évaluées par l'IA se sont retrouvées avec un score
définitif de 0, présenté comme si la correction avait eu lieu.

## AI_FAILURE_FALSE_ZERO

**0** — plus aucun chemin de code ne fabrique de score pour une question dont la
notation dépend de l'IA quand celle-ci échoue. Vérifié par
`test_ai_provider_error_on_one_semantic_question_never_produces_a_zero` et
`test_ai_provider_error_on_four_semantic_questions_keeps_session_not_completed`.

## Root cause précise (deux mécanismes distincts, tous deux corrigés)

1. `app/v1/session_service.py::_correct_and_finalize_claimed_session` (#55/#62/#71) :
   `except AIProviderError` construisait un `QuestionCorrection(points_awarded=0.0, ...)`
   pour chaque question `requires_ai_correction()`, puis finalisait `COMPLETED`.
2. `app/ai/questionnaire.py::validate_semantic_correction` : retournait déjà, même en
   dehors de toute exception, `points_awarded=0.0` pour toute question absente de la
   réponse IA (lot partiel/malformé) — un second chemin vers le même bug, jamais visible
   via un simple `except AIProviderError`.

## ASYNC_ARCHITECTURE / correction résumable

`submit_session`/`_correct_and_finalize_claimed_session` (§ synchrone, #55/#62/#70/#71)
restent **strictement inchangées** — toujours directement testées et utilisées telles
quelles. Le job asynchrone (#88) appelle désormais un chemin séparé et résumable :

- `app/v1/hybrid_correction.py::correct_session_hybrid_resumable` (nouveau) : même
  catégorisation que `correct_session_hybrid` (semantic / rescorable / explain-only),
  mais accepte `already_corrected` (questions déjà acquises lors d'une tentative
  précédente, jamais renvoyées à l'IA) et retourne `(corrections, unresolved)` — les
  questions dont le SCORE dépend de l'IA et qui n'ont pas reçu de correction réelle
  (`AIProviderError` OU absente du lot renvoyé) restent dans `unresolved`, **jamais** un
  `QuestionCorrection` à 0 fabriqué. Les questions déterministes `explain_only`
  (score déjà verrouillé et correct par `correct_locally`, l'IA n'apporte qu'une
  explication pédagogique) gardent le repli textuel existant : leur score ne dépend
  jamais de l'IA, donc un échec IA ne les bloque jamais.
- `app/v1/session_service.py::_resolve_correction_job` (nouveau) : construit
  `already_corrected` depuis `SessionAnswer.correction_status == CORRECTED`, appelle
  `correct_session_hybrid_resumable`, persiste chaque résultat. Finalise
  (`SessionStatus.COMPLETED`, score calculé et verrouillé) **uniquement** si
  `unresolved` est vide ; sinon `SessionStatus.CORRECTION_INCOMPLETE`, score jamais
  calculé.
- `run_correction_job` : `job.status` devient `COMPLETED` ou `INCOMPLETE` selon le
  résultat de `_resolve_correction_job` — `FAILED` réservé aux erreurs techniques
  réellement inattendues (bug, base indisponible), plus jamais confondu avec une
  correction IA simplement indisponible.

## CORRECTION_INCOMPLETE_STATE

**YES** — nouveaux états `SessionStatus.CORRECTION_INCOMPLETE` et
`CorrectionJobStatus.INCOMPLETE` (`app/v1/models.py`). Une session dans cet état reste
verrouillée (réponses immuables, `is_locked()` déjà vrai pour tout statut ≠
`IN_PROGRESS`), n'affiche jamais de score comme définitif, et expose un bouton
« Réessayer la correction ».

## SEMANTIC_PENDING_NOT_ZERO

**YES** — `AnswerCorrectionStatus.FAILED` (déjà défini, jamais utilisé avant ce ticket)
marque une réponse en attente d'une vraie correction ; `points_awarded`/`feedback_json`
restent `None`, jamais écrasés par une valeur inventée.

## DETERMINISTIC_STILL_WORKS

**YES** — `correct_locally` inchangée ; une session 100 % déterministe (QCM/
classification/matching/ordering/numeric/commandes exactes) continue de se terminer
normalement même si le fournisseur IA est indisponible (son score ne dépend jamais de
l'IA) — `test_deterministic_only_session_still_completes_even_with_failing_provider`,
`test_deterministic_questions_remain_correctly_scored_despite_ai_failure`.

## TARGETED_RETRY

**YES** — `retry_correction_job` (renommé depuis `retry_failed_correction_job` de #88,
étendu aux statuts `FAILED` **et** `INCOMPLETE`) réutilise le même `CorrectionJob`,
repasse `session.status` à `CORRECTING` (réutilise telle quelle la page d'attente/le
polling de #88, aucun nouvel état d'interface). Le ciblage est structurel : le corps de
correction saute systématiquement tout `question_id` déjà `CORRECTED`
(`_existing_corrections_by_id`), donc un retry ne renvoie jamais à l'IA une question déjà
correctement notée — vérifié par `test_retry_targets_only_unresolved_questions_and_completes`
(un seul appel `correct_semantic_batch` malgré 2 tentatives) et
`test_retry_never_modifies_already_corrected_answers`.

## FINAL_SCORE_ONLY_WHEN_COMPLETE

**YES** — `session.score` reste `None` tant que `SessionStatus != COMPLETED`. Les
templates (`v1_session_results.html`, export Markdown) affichent explicitement
« CORRECTION INCOMPLÈTE » / « Score provisoire indisponible » plutôt qu'un score, y
compris à l'impression (bannière `alert-warning`, jamais masquée en `@media print`).

## INCREMENT_248_ANSWER

**1.0/1.0** — cas réel exact du ticket : « 256 - 248 = 8, donc 8 est l'incrément. »
Root cause : `_check_numeric` exigeait que la réponse ENTIÈRE soit un nombre nu
(`app.answer_checking.parse_answer`, `Fraction(...)` sur la chaîne complète). Correctif
structuré et borné (`app.answer_checking.extract_last_number`, § 8 du ticket) : si le
parse strict échoue, extrait le DERNIER nombre du texte — jamais « n'importe quel nombre
présent » (rejeté explicitement : une réponse qui mentionne la bonne valeur puis conclut
sur une autre reste fausse, voir `test_extract_last_number_rejects_a_wrong_final_conclusion`).
Tolère ordre des mots, accents, ponctuation, phrase explicative — jamais un fuzzy
matching général.

## SEMANTIC_SHORT_AUDIT

**YES** — nouvelle fonction partagée `app.answer_checking.is_semantic_short_answer_prompt`
(déclencheurs lexicaux : explique/justifie/compare/décris/démarche/pourquoi + motif
structurel « nombre + mot », ex. « Cite deux contrôles… »). Câblée dans
`QuestionnaireQuestion.requires_ai_correction()` (`app/ai/schemas.py`) : une
`short_answer`/`vocabulary` dont l'énoncé matche ce motif part TOUJOURS à l'IA, même si
`accepted_answers` est renseigné — jamais notée par égalité textuelle stricte. Module
partagé avec #85 (`app/v1/short_answer_limits.py`, refactoré pour déléguer à cette même
fonction — plus jamais deux listes de déclencheurs divergentes).

## PARTIAL_CREDIT

**YES, non régressé** — `_partial_credit_classification`/`_partial_credit_matching` (#70)
inchangés ; `test_classification_partial_credit_not_regressed_by_ticket_90` confirme
0.5/1.0 pour 1 élément correct sur 2, via le chemin asynchrone complet.

## HISTORY_STATES

**YES** — `/mes-sessions` distingue désormais explicitement « Correction en cours »
(`CORRECTING`), « Correction incomplète » (`CORRECTION_INCOMPLETE`) et « Terminé »
(`COMPLETED`), badge et bouton d'action par état.

## EXPORT_INCOMPLETE / PRINT_INCOMPLETE

**YES** — `GET /sessions/{id}/export.md` reste accessible pour `CORRECTION_INCOMPLETE`
(refusé seulement pour `IN_PROGRESS`/`CORRECTING`/`ABANDONED`, § 13 du ticket) : bannière
« CORRECTION INCOMPLÈTE » en tête de document, score remplacé par un texte explicite,
lignes de points par question remplacées par « En attente de correction ». Même bannière
visible à l'écran ET à l'impression (jamais `d-print-none` sur le texte d'avertissement
lui-même, seulement sur le bouton d'action).

## Tests (`tests/test_ticket90_correction_failure_integrity.py`, 22 tests)

Aucun faux 0 (1 puis 4 questions sémantiques en échec), questions déterministes
préservées, session 100 % déterministe non bloquée par un fournisseur en panne, retry
ciblé (1 seul appel IA malgré 2 tentatives), retry n'altère jamais une réponse déjà
corrigée, retry refusé sur un job ni FAILED ni INCOMPLETE, cas réel /29 (`extract_last_number`
+ `_check_numeric` + `correct_locally` bout en bout), détection sémantique vs factuelle
d'un short_answer, short_answer sémantique avec `accepted_answers` toujours envoyée à
l'IA bout en bout, non-régression crédit partiel #70, non-régression `submit_session`
(#55/#62/#70/#71), bannière + bouton retry sur la page de résultats, historique à 3
états, submit toujours non bloquant + double POST = 1 job (non-régression #88).

Deux tests hérités de #88 corrigés (leur prémisse — AIProviderError toujours absorbée en
un score inventé — était exactement le bug que ce ticket corrige) :
`test_ai_provider_error_on_semantic_question_is_incomplete_not_completed` (renommé
depuis `test_ai_provider_error_still_completes_via_existing_repli`) et
`test_unexpected_exception_marks_job_failed_not_ai_provider_error` (cible de monkeypatch
mise à jour : `correct_session_hybrid_resumable`, le nouveau chemin appelé par
`run_correction_job`).

Validation : `pytest -q` (suite complète) → 1267 passed, 0 failed. `ruff check .` → 36
erreurs, baseline `develop`/#88 inchangée, 0 nouvelle dette. `git diff --check` propre.
Aucun appel OpenAI réel (`FakeAIProvider` partout, `_FailingProvider` pour simuler
`AIProviderError`).

## Fichiers

- `app/answer_checking.py` (`extract_last_number`, `is_semantic_short_answer_prompt`)
- `app/ai/schemas.py` (`requires_ai_correction` consulte le prompt pour les types
  conditionnellement locaux)
- `app/ai/local_correction.py` (`_check_numeric` : repli sur le dernier nombre du texte)
- `app/v1/short_answer_limits.py` (délègue à la détection partagée, plus de duplication)
- `app/v1/hybrid_correction.py` (`correct_session_hybrid_resumable`, nouveau)
- `app/v1/session_service.py` (`_resolve_correction_job`, `_existing_corrections_by_id`,
  `run_correction_job` mis à jour, `retry_correction_job` renommé/étendu)
- `app/v1/routes_sessions.py` (`view_session`/`_build_results_rows`/
  `_build_session_export_markdown`/`export_session_markdown`/`retry_correction_route`
  mis à jour pour `CORRECTION_INCOMPLETE`)
- `app/v1/models.py` (`SessionStatus.CORRECTION_INCOMPLETE`,
  `CorrectionJobStatus.INCOMPLETE`)
- `app/templates/v1_session_results.html` (bannière incomplète, retry, points en attente)
- `app/templates/v1_history.html` (état « Correction incomplète »)
- `tests/test_ticket90_correction_failure_integrity.py` (nouveau, 22 tests)
- `tests/test_ticket88_async_correction_jobs.py` (2 tests corrigés pour refléter le
  comportement désormais correct)
- `docs/claude-reports/2026-09-19_ticket-90_correction-failure-integrity.md` (ce rapport)

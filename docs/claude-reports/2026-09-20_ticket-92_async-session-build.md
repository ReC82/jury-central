# Ticket #92 — Génération de session asynchrone (suppression des 504 au démarrage)

**Branche :** `fix/92-async-session-build`
**Base :** `develop` @ `8027d2d3746c0c237397562ce55914c05e7185dd` (merge PR #91, #88+#90)
**NE MERGE RIEN. AUCUN DÉPLOIEMENT. AUCUN NGINX/SYSTEMD.**

## ROOT_CAUSE

`504 Gateway Time-out` reproduit en staging sur `POST /uaa/ampcr-mc38/exam/start`. #88
avait rendu la CORRECTION asynchrone, mais la CRÉATION/GÉNÉRATION de session restait
entièrement synchrone : `start_practice_session`/`start_exam_session`/
`start_ampcr_global_practice`/`start_ampcr_global_exam` appelaient directement
`start_session()`, qui attend la sélection banque + génération IA (potentiellement
plusieurs appels) + validation + persistance + composition MC38 avant de répondre — un
POST pouvant dépasser le timeout nginx/upstream même quand le backend continue de
travailler.

## ASYNC_ARCHITECTURE — SessionBuildJob

Même principe que #88 (`CorrectionJob`), appliqué à la génération :

- `SessionBuildJobStatus` : `PENDING → RUNNING → READY` ou `FAILED`.
- `SessionBuildJob` (`app/v1/models.py`) : `user_id`, `mode`, `module_id`, `uaa_id`,
  `uaa_code`, `difficulty`, `question_count`, `status`, `created_at`/`started_at`/
  `completed_at`, `error_message`, `attempt_count`, `created_session_id`. Le champ
  `question_count` est déjà porté par le job (§ QUESTION_COUNT_PARAMETER_READY).
- `uaa_id_key` : copie non-FK de `uaa_id`, `0` par défaut. Nécessaire car SQLite traite
  chaque `NULL` comme distinct dans un index UNIQUE — sans ce sentinel, l'idempotence
  aurait silencieusement cassé pour les sessions globales AMPCR (`uaa_id=None`).
- `active_marker` : `"1"` tant que le job occupe une génération (PENDING/RUNNING/
  **FAILED inclus**, pour qu'un retry ne crée jamais un second job fantôme), `NULL` une
  fois `READY` — libère le créneau, les vérifications de session déjà existante
  (`_resumable_session_for_uaa`/`_is_unstarted`) reprennent alors la main normalement.
- `UniqueConstraint(user_id, module_id, uaa_id_key, mode, active_marker)` —
  `uq_session_build_job_active`.

`start_session()` (composition banque/génération/MC38/Français, #55/#58/#82/#90) reste
**strictement inchangée** — appelée telle quelle par `run_session_build_job`, jamais
dupliquée.

## FLUX

`POST /uaa/{slug}/{mode}/start` (et les routes globales AMPCR) ne font plus QUE : valider
les paramètres, vérifier une session déjà existante/en cours (logique #71/#55 inchangée),
créer/retrouver un `SessionBuildJob` (`enqueue_session_build`), `commit`, rediriger
immédiatement (303) vers `/session-build-jobs/{id}`. **Aucun appel IA, aucune génération
dans le cycle requête/réponse.**

## WAIT_PAGE

`app/templates/v1_session_build_waiting.html` (nouveau) : « Préparation de l'évaluation…
/ de l'entraînement… », « Génération des questions en cours. », « Merci de patienter
quelques secondes. », étapes `✓ Demande enregistrée / • Préparation des questions / ○
Évaluation (ou Entraînement) prête` — jamais de pourcentage fabriqué. État `FAILED` :
« La préparation … a échoué » + bouton « Réessayer » (POST `/session-build-jobs/{id}/retry`).

## STATUS_POLL

`GET /session-build-jobs/{job_id}` — rend la page d'attente, ou redirige (303) vers
`/sessions/{created_session_id}` si `READY`. `GET /session-build-jobs/{job_id}/status` —
JSON `{status, error_message, session_url}`, interrogé toutes les 2.5s en JS, redirige
côté client dès `ready`, bascule l'affichage sur `failed` sinon.

## DOUBLE_START_SINGLE_JOB / DOUBLE_START_SINGLE_SESSION

**YES / YES** — `enqueue_session_build` vérifie d'abord un job actif
(`_active_session_build_job`, filtré sur `active_marker="1"`) ; sinon `INSERT` avec
`try/except IntegrityError` en filet (course entre deux requêtes concurrentes). Deux POST
consécutifs (double-clic, refresh, deux onglets) retrouvent systématiquement le MÊME job
tant qu'il n'est pas `READY` — vérifié en HTTP réel (`test_double_post_practice_start_creates_a_single_job`)
et au niveau service (`test_enqueue_session_build_is_idempotent_at_service_level`). Une
fois résolu, un seul `QuestionnaireSession` existe pour ce job.

## MC38_SUPPORTED / FRENCH_SUPPORTED

**YES / YES** — `run_session_build_job` appelle l'unique `start_session()` existant, qui
route déjà en interne vers `_start_mc38_transversal_session` (`uaa_code == "MC38"`, banque
MC01-37, anti-méta #58) et vers `get_francais_plan_by_slug` pour le Français — **zéro
logique dupliquée**, zéro branchement spécifique à un type d'UAA dans le nouveau code.
Testé explicitement : `/uaa/ampcr-mc38/exam/start` (job → session MC38 réelle, 20
questions) et `/uaa/francais-c01/practice/start` (job → session Français réelle).

## QUESTION_COUNT_PARAMETER_READY

**YES** — `SessionBuildJob.question_count` déjà stocké et transmis à `start_session()` à
la résolution. #86 (10/20/30/40/50) pourra brancher sa valeur choisie sur ce champ
existant sans nouvelle migration ni nouvelle architecture — non commencé dans ce ticket
(hors scope explicite).

## WORKER_STRATEGY / WORKER_COMMAND / SYSTEMD_REQUIRED

**Option A (étendre le worker existant) / `python -m app.v1.correction_worker` (inchangé) / NO**

`app/v1/correction_worker.py` traite désormais DEUX files dans la même boucle :
`process_one_job`/`recover_stale_jobs_once` (CorrectionJob, #88, inchangés) et les
nouveaux `process_one_build_job`/`recover_stale_build_jobs_once` (SessionBuildJob, miroir
exact de leurs équivalents #88). `run_worker_loop` appelle les deux à chaque itération,
ne dort que si aucune des deux files n'avait de travail. Choisi plutôt qu'un second
processus séparé : un seul worker à opérer/superviser, aucune duplication de la boucle de
poll/arrêt propre (`SIGTERM`/`SIGINT`), et surtout **aucun changement systemd requis** —
le service déjà déployé lors de la mise en staging de #88/#90
(`jury-central-correction-worker.service`, `ExecStart=…python -m app.v1.correction_worker`)
traitera automatiquement les `SessionBuildJob` au prochain redéploiement de `develop`,
sans nouvelle unité ni modification d'unité existante.

## NGINX_CHANGE_REQUIRED

**NO** — non touché. Le correctif rend la requête courte (pas de génération IA dans le
cycle HTTP) au lieu d'agrandir un timeout.

## Blast radius — 13 fichiers de tests pré-existants mis à jour

Le changement de sémantique HTTP (`/start` retourne désormais `/session-build-jobs/{id}`
au lieu de `/sessions/{id}`) cassait toute assertion supposant la session immédiatement
créée. Même pattern que le blast radius de #88 (petit helper explicite, appelé juste
après le POST `/start`, jamais un vrai worker séparé dans les tests) :
`_resolve_build_job_url`/`_run_pending_build_job_and_get_session_id` réclament et
exécutent le job `PENDING` en appel direct (`claim_next_pending_build_job` +
`run_session_build_job`), en réutilisant le fournisseur déjà monkeypatché sur la route
(repli explicite sur `AINotConfiguredError` → `_UnconfiguredProvider`, comme le fait le
vrai worker).

Fichiers corrigés : `test_ticket47_francais_v1.py`, `test_ticket55_urgent_ampcr_full.py`
(dont un test réécrit : l'échec banque-vide-sans-IA était auparavant un 503 synchrone,
devient désormais un `SessionBuildJob` `FAILED` asynchrone — changement de comportement
assumé, pas une régression), `test_ticket58_ampcr_content_and_mc38.py`,
`test_ticket62_hybrid_correction_history_export.py`,
`test_ticket64_ampcr_question_quality.py`, `test_ticket70_regrading_partial_feedback.py`,
`test_ticket71_long_action_loading.py` (tests d'idempotence double-POST réécrits pour
vérifier l'idempotence au niveau du job puis de la session résolue, jamais deux sessions),
`test_ticket74_course_recommendations.py`, `test_ticket77_hidden_source_document.py`,
`test_ticket79_source_document_ui.py`, `test_ticket82_no_intrasession_duplicates.py`,
`test_ticket88_async_correction_jobs.py`, `test_ticket90_correction_failure_integrity.py`
(ces deux derniers avaient un risque réel de boucle infinie : leur pattern
`while True: … if status != 200: break` bouclerait indéfiniment sur une page d'attente
qui répond 200 tant que le job n'est pas résolu — corrigé en résolvant le job avant
d'entrer dans la boucle).

## Tests

`tests/test_ticket92_async_session_build.py` (nouveau, 23 tests) : POST non bloquant
malgré un `FakeAIProvider` délibérément ralenti (mock/`time.sleep` contrôlé, jamais un
vrai délai de 60s) pour practice et exam ; MC38 spécifiquement ; Français spécifiquement ;
practice/exam globaux AMPCR ; double enqueue au niveau service et au niveau HTTP (même
job, une seule session après résolution) ; UAA/mode différents → jobs indépendants ; page
d'attente survit au refresh ; redirection 303 quand `READY` ; état `FAILED` + bouton
retry ; retry réutilise le même job jusqu'au succès (jamais plus d'un
`SessionBuildJob` pour cet utilisateur/UAA/mode) ; retry refusé si le job n'est pas
`FAILED` ; job `RUNNING` périmé remis en `PENDING` puis `FAILED` après le nombre maximal
de tentatives ; anti-doublon intra-session (#82) toujours vérifié via le chemin
asynchrone ; logout/login reprend l'état d'attente ; `/mes-sessions` affiche « en
préparation » ; endpoint de statut 404 pour un non-propriétaire ; la boucle du worker
traite bien les deux files ; `process_one_build_job` retourne `False` à vide. Aucun appel
OpenAI réel.

Validation : `pytest -q` (suite complète) → **1290 passed, 0 failed**. `ruff check .` →
36 erreurs, baseline inchangée depuis `develop`, **0 nouvelle dette**. `git diff --check`
propre.

## Fichiers

- `app/v1/models.py` (`SessionBuildJobStatus`, `SessionBuildJob`)
- `app/v1/session_service.py` (`enqueue_session_build`, `claim_next_pending_build_job`,
  `run_session_build_job`, `recover_stale_build_jobs`, `retry_session_build_job`,
  `get_session_build_job`, `SessionBuildJobNotFailedError`)
- `app/v1/correction_worker.py` (`process_one_build_job`, `recover_stale_build_jobs_once`,
  `run_worker_loop` traite les deux files)
- `app/v1/routes_sessions.py` (`_enqueue_build_for_uaa` remplace `_start_session_for_uaa`,
  routes `start_practice_session`/`start_exam_session`/`start_ampcr_global_practice`/
  `start_ampcr_global_exam` simplifiées, nouvelles routes `/session-build-jobs/{id}`
  [+`/status`, +`/retry`], `my_sessions` affiche les jobs en préparation)
- `app/templates/v1_session_build_waiting.html` (nouveau)
- `app/templates/v1_history.html` (cartes « en préparation »/« préparation échouée »)
- `tests/test_ticket92_async_session_build.py` (nouveau, 23 tests)
- 13 fichiers de tests pré-existants mis à jour (voir § Blast radius)
- `docs/claude-reports/2026-09-20_ticket-92_async-session-build.md` (ce rapport)

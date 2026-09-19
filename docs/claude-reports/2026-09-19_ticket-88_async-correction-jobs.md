# Ticket #88 — BLOQUANT correction : supprimer les 504 avec une correction asynchrone persistée

**Branche :** `fix/88-async-correction-jobs`
**Base :** `develop` @ `c8d3753966db245d8df4addbe8c1f99b1f875fcb`
**NE MERGE RIEN. AUCUN DÉPLOIEMENT. AUCUN CHANGEMENT NGINX/SYSTEMD.**

## ROOT_CAUSE

`POST /sessions/{id}/submit` (`app/v1/routes_sessions.py::submit_session_route`)
appelait directement `app.v1.session_service.submit_session`, qui exécute l'appel IA
groupé (`correct_session_hybrid`) **de façon synchrone, dans le cycle requête/réponse
HTTP**. Ce lot peut prendre plusieurs dizaines de secondes. Si ce délai dépasse le
timeout de l'upstream/nginx, la connexion est coupée côté client (`504 Gateway
Time-out`) **alors que le traitement continue côté serveur** — un problème de MODÈLE
(requête/réponse synchrone appliquée à un traitement long), jamais résolu par une simple
augmentation de `proxy_read_timeout`.

## CURRENT_TIMEOUT_MODEL

Avant #88 : 1 requête HTTP = 1 appel IA complet, aucune séparation entre « la
soumission est acceptée » et « la correction est terminée ». Le ticket #71 (déjà mergé)
avait ajouté une réclamation atomique côté serveur et un état de chargement côté client,
mais n'avait pas changé ce modèle synchrone — un double clic ne déclenchait plus deux
corrections, mais la prembattre requête HTTP continuait d'attendre l'IA jusqu'au bout.

## ASYNC_ARCHITECTURE

`POST /sessions/{id}/submit` ne fait plus JAMAIS l'appel IA :

1. verrouille la session (`IN_PROGRESS` → nouveau statut `CORRECTING`, réclamation
   atomique — même mécanisme `UPDATE ... WHERE status = ...` que l'ancienne réclamation
   `IN_PROGRESS` → `COMPLETED` de #71) ;
2. crée (ou retrouve) un `CorrectionJob` `PENDING` (`app.v1.session_service.
   enqueue_correction`) ;
3. redirige IMMÉDIATEMENT vers `/sessions/{id}` (quelques millisecondes, prouvé par
   test avec un fournisseur artificiellement ralenti de 2 secondes — § TESTS).

La correction réelle (`app.v1.session_service.run_correction_job`, qui réutilise
`_correct_and_finalize_claimed_session` **INCHANGÉE** depuis #55/#62/#70/#71) est
exécutée par un worker séparé (`app.v1.correction_worker`), jamais dans une requête
HTTP. `submit_session()` (la fonction synchrone complète) reste elle-même intacte et
continue d'être directement testée/utilisée par #70/#71/#74 — aucune régression.

La page `/sessions/{id}` affiche désormais trois états distincts selon
`session.status` : `IN_PROGRESS` (question courante), `CORRECTING` (nouvelle page
d'attente `v1_session_correcting.html`, avec polling `GET /sessions/{id}/
correction-status` toutes les 2,5s), `COMPLETED`/`ABANDONED` (résultats, inchangé).

## JOB_STORAGE

Table `v1_correction_jobs` (déclarative SQLAlchemy, créée automatiquement par
`Base.metadata.create_all()` au démarrage — pas d'Alembic dans ce projet, aucune
migration manuelle requise). File **DB-backed**, pas de Redis/Celery (§ 8 du ticket,
« solution la plus simple »).

## JOB_STATES

`CorrectionJobStatus` : `PENDING` → `RUNNING` (`started_at`, `attempt_count`
incrémenté) → `COMPLETED` (`completed_at`) ou `FAILED` (`error_message`). Champs :
`session_id` (UNIQUE), `status`, `severity_ui`, `created_at`, `started_at`,
`completed_at`, `error_message`, `attempt_count`.

## DOUBLE_SUBMIT_PROTECTION

`CorrectionJob.session_id` est **UNIQUE en base** (contrainte DB, § 4 du ticket) — un
double clic, un refresh, un retour arrière/avant, un retry HTTP ou deux onglets
simultanés retombent tous sur le MÊME job : `enqueue_correction` cherche d'abord un job
existant avant toute tentative de réclamation, et la réclamation atomique de la session
garantit qu'un seul appelant peut créer le premier job. Testé au niveau service ET HTTP
(double POST réel) : 1 seul `CorrectionJob`, 1 seul appel IA après exécution du worker.

## CRASH_RECOVERY

`recover_stale_correction_jobs(stale_after_seconds=300, max_attempts=3)` : tout job
`RUNNING` depuis plus de 5 minutes est remis `PENDING` (s'il reste des tentatives) ou
basculé `FAILED` (au-delà de `max_attempts` — jamais de boucle infinie). Appelée
périodiquement par la boucle du worker (`run_worker_loop`, toutes les 30s par défaut),
indépendamment du traitement des jobs `PENDING`.

## FAILED_RETRY

`AIProviderError` reste géré par le repli EXISTANT (#55/#62, INCHANGÉ) — correction
locale + message explicite, le job termine `COMPLETED` avec un résultat honnête, jamais
`FAILED`. `FAILED` est réservé aux erreurs réellement inattendues (bug, base
indisponible...). Page d'attente : si `FAILED`, affiche « La correction n'a pas pu être
terminée. Tes réponses sont sauvegardées. » + bouton « Réessayer la correction »
(`POST /sessions/{id}/retry-correction`) qui réutilise le MÊME job (jamais un second),
remis `PENDING` avec `attempt_count` repartant de zéro (action humaine délibérée,
distincte d'une reprise automatique après incident).

## WORKER_COMMAND

```
.venv/bin/python -m app.v1.correction_worker
```

Processus séparé et longuement vivant (PAS une thread attachée à une requête ou au
worker web, qui serait tuée à son recyclage — § 8 du ticket). Ouvre/ferme une session DB
par job, jamais une session unique gardée ouverte sur toute la durée de vie du
processus. Gère `SIGTERM`/`SIGINT` proprement.

## SYSTEMD_REQUIRED

**Oui, à terme, pour un fonctionnement continu en production** — mais **AUCUN
changement systemd n'a été fait par ce ticket** (interdit explicitement, § 15). Prête
uniquement : le module worker (`app/v1/correction_worker.py`), la commande de
lancement ci-dessus, et cette documentation. **ChatGPT décidera du déploiement
systemd.**

## NGINX_CHANGE_REQUIRED

**Non, structurellement.** L'architecture rend `POST /sessions/{id}/submit`
indépendant de la durée de la correction — un timeout nginx classique (30-60s) reste
largement suffisant pour cette requête, qui répond désormais en quelques millisecondes.
Aucun changement nginx n'a été fait ni n'est requis par ce ticket.

## TESTS

`tests/test_ticket88_async_correction_jobs.py` (28 tests) + non-régression via les
suites existantes (#70/#71/#74, `submit_session` inchangée). Couvre : création de job
sans appel IA, réponse HTTP rapide avec fournisseur ralenti (2s, non attendu),
transitions PENDING→RUNNING→COMPLETED, résultats/feedback corrects, sévérité persistée,
double `enqueue_correction` = 1 job, double POST HTTP = 1 job = 1 appel IA, page
d'attente qui survit à un refresh, `/mes-sessions` affiche « Correction en cours »,
reprise après logout/login, erreur inattendue → `FAILED` (session reste `CORRECTING`,
jamais rouverte), `AIProviderError` → toujours `COMPLETED` via le repli existant, page
FAILED + bouton retry, retry réinitialise le job sans toucher les réponses, retry refusé
sur un job non-FAILED, retry ne duplique jamais une correction déjà réussie, job
`RUNNING` périmé requeue en `PENDING`, périmé + tentatives épuisées → `FAILED`, job
`RUNNING` récent non touché, réponses immuables une fois `CORRECTING`, autosave normal
non régressé, export Markdown fonctionne après correction asynchrone, endpoint de
polling (états + contrôle de propriété), boucle du worker (bornée pour les tests).

Aucun appel OpenAI réel (`FakeAIProvider` partout, y compris une variante délibérément
ralentie pour la preuve de non-blocage).

## Fichiers

- `app/v1/models.py` (`SessionStatus.CORRECTING`, `CorrectionJobStatus`, `CorrectionJob`)
- `app/v1/session_service.py` (`enqueue_correction`, `get_correction_job`,
  `claim_next_pending_correction_job`, `run_correction_job`,
  `recover_stale_correction_jobs`, `retry_failed_correction_job`,
  `CorrectionJobNotFailedError` — `submit_session`/`_correct_and_finalize_claimed_session`
  inchangées)
- `app/v1/routes_sessions.py` (`submit_session_route` réécrite non bloquante,
  `correction_status_route`, `retry_correction_route`, `view_session` : branche
  `CORRECTING`)
- `app/v1/correction_worker.py` (nouveau, module worker autonome)
- `app/templates/v1_session_correcting.html` (nouveau, page d'attente + polling)
- `app/templates/v1_history.html` (état « Correction en cours »)
- `app/templates/v1_session_submit_confirm.html` (texte/commentaire mis à jour)
- `tests/test_ticket88_async_correction_jobs.py` (nouveau, 28 tests)
- `docs/claude-reports/2026-09-19_ticket-88_async-correction-jobs.md` (ce rapport)

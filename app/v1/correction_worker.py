"""Worker de fond asynchrone — traite deux files DB-backed indépendantes, dans le MÊME
processus :

1. `CorrectionJob` (ticket #88) : créés par `POST /sessions/{id}/submit`, désormais non
   bloquant (voir `app.v1.session_service.enqueue_correction`).
2. `SessionBuildJob` (ticket #92) : créés par `POST /uaa/{slug}/practice|exam/start` et
   `POST /modules/ampcr/practice|exam/start`, désormais non bloquants (voir
   `app.v1.session_service.enqueue_session_build`) — même 504 Gateway Time-out réellement
   observé en staging, cette fois sur `/uaa/ampcr-mc38/exam/start` (sélection banque,
   génération IA, composition MC38, validation, persistance : potentiellement plusieurs
   secondes, largement au-delà de ce qu'un timeout nginx/upstream tolère).

Un seul worker plutôt que deux processus séparés (ticket #92 § 7, option A retenue :
« étendre le même worker pour traiter plusieurs types de jobs ») : les deux traitements
sont indépendants (deux tables, deux fonctions dédiées, jamais de logique partagée
risquée), la charge de chacun reste faible, et un seul processus/une seule unité systemd
à opérer est plus simple qu'une coordination entre deux workers — **aucun changement
systemd n'est donc nécessaire pour ce ticket**, l'unité déjà déployée (#88) couvre
désormais aussi la création de session dès que ce code est redéployé.

Volontairement le PLUS SIMPLE possible (§ 8 du ticket #88, toujours valable) : pas de
file de messages (Redis/Celery), une file DB-backed par type de job (tables déjà
utilisées pour la réclamation atomique côté web) que ce processus interroge par polling.
PAS une thread Python attachée à une requête ou au processus web (qui serait tuée si le
worker web recycle) : un processus SÉPARÉ et LONGUEMENT VIVANT, lancé indépendamment du
serveur web.

Lancement (inchangé) :

    .venv/bin/python -m app.v1.correction_worker

Boucle : à chaque itération, le worker (1) récupère les jobs `RUNNING` bloqués depuis
trop longtemps pour CHAQUE file (crash d'un worker précédent, remis `PENDING` ou `FAILED`
au-delà du nombre maximal de tentatives), (2) réclame ATOMIQUEMENT au plus un
`CorrectionJob` `PENDING` puis au plus un `SessionBuildJob` `PENDING`, (3) exécute chacun
en réutilisant `run_correction_job`/`run_session_build_job` (elles-mêmes basées sur
`_correct_and_finalize_claimed_session`/`start_session`, INCHANGÉES depuis les tickets
#55/#58/#62/#70/#71), (4) recommence, avec une courte pause seulement si aucune des deux
files n'avait de travail."""

import logging
import signal
import time

from app.ai.factory import get_ai_provider
from app.ai.provider import AINotConfiguredError, AIProviderError
from app.database import SessionLocal
from app.v1.session_service import (
    claim_next_pending_build_job,
    claim_next_pending_correction_job,
    recover_stale_build_jobs,
    recover_stale_correction_jobs,
    run_correction_job,
    run_session_build_job,
)

logger = logging.getLogger("app.v1.correction_worker")

DEFAULT_POLL_INTERVAL_SECONDS = 3
DEFAULT_STALE_CHECK_INTERVAL_SECONDS = 30
DEFAULT_STALE_AFTER_SECONDS = 300
DEFAULT_MAX_ATTEMPTS = 3


class _UnconfiguredProvider:
    """Même repli que `app.v1.routes_sessions._UnconfiguredProvider` (dupliqué
    délibérément — deux définitions minuscules et indépendantes plutôt qu'un import
    croisé routes/worker, § 8 « solution la plus simple »). Laisse
    `_correct_and_finalize_claimed_session` suivre son repli `AIProviderError` existant
    (correction locale, jamais un job bloqué faute de fournisseur configuré)."""

    def generate_questionnaire(self, request):
        raise AINotConfiguredError("Génération IA non configurée sur ce serveur.")

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        raise AINotConfiguredError("Correction IA non configurée sur ce serveur.")


def _get_provider_or_unconfigured():
    try:
        return get_ai_provider()
    except AINotConfiguredError:
        return _UnconfiguredProvider()


def process_one_job(*, max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> bool:
    """Réclame et exécute AU PLUS un job `PENDING`. Retourne `True` si un job a été
    traité (pour permettre au boucle appelante d'enchaîner sans pause), `False` sinon."""
    db = SessionLocal()
    try:
        job = claim_next_pending_correction_job(db, max_attempts=max_attempts)
        if job is None:
            return False
        logger.info("CORRECTION_JOB_CLAIMED session_id=%s job_id=%s attempt=%s", job.session_id, job.id, job.attempt_count)
        provider = _get_provider_or_unconfigured()
        try:
            result = run_correction_job(db, job=job, provider=provider)
        except AIProviderError as exc:
            # Ne devrait normalement jamais atteindre ce niveau (`_correct_and_finalize_
            # claimed_session` gère déjà `AIProviderError` avec un repli local) — filet de
            # sécurité supplémentaire si ce comportement change un jour en amont : jamais
            # un job silencieusement perdu.
            db.rollback()
            job.status = job.status.__class__.FAILED
            job.error_message = str(exc)[:2000]
            db.commit()
            logger.warning("CORRECTION_JOB_AI_PROVIDER_ERROR session_id=%s job_id=%s error=%s", job.session_id, job.id, exc)
            return True
        logger.info("CORRECTION_JOB_%s session_id=%s job_id=%s", result.status.value.upper(), job.session_id, job.id)
        return True
    finally:
        db.close()


def process_one_build_job(*, max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> bool:
    """Ticket #92 : réclame et exécute AU PLUS un `SessionBuildJob` `PENDING`. Même
    contrat que `process_one_job` (retourne `True` si un job a été traité)."""
    db = SessionLocal()
    try:
        job = claim_next_pending_build_job(db, max_attempts=max_attempts)
        if job is None:
            return False
        logger.info(
            "SESSION_BUILD_JOB_CLAIMED job_id=%s user_id=%s module_id=%s uaa_code=%s mode=%s attempt=%s",
            job.id, job.user_id, job.module_id, job.uaa_code, job.mode.value, job.attempt_count,
        )
        provider = _get_provider_or_unconfigured()
        result = run_session_build_job(db, job=job, provider=provider)
        logger.info(
            "SESSION_BUILD_JOB_%s job_id=%s created_session_id=%s",
            result.status.value.upper(), job.id, result.created_session_id,
        )
        return True
    finally:
        db.close()


def recover_stale_jobs_once(
    *, stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS, max_attempts: int = DEFAULT_MAX_ATTEMPTS
) -> dict[str, int]:
    db = SessionLocal()
    try:
        report = recover_stale_correction_jobs(db, stale_after_seconds=stale_after_seconds, max_attempts=max_attempts)
        if report["requeued"] or report["failed"]:
            logger.info("CORRECTION_JOB_STALE_RECOVERY requeued=%s failed=%s", report["requeued"], report["failed"])
        return report
    finally:
        db.close()


def recover_stale_build_jobs_once(
    *, stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS, max_attempts: int = DEFAULT_MAX_ATTEMPTS
) -> dict[str, int]:
    db = SessionLocal()
    try:
        report = recover_stale_build_jobs(db, stale_after_seconds=stale_after_seconds, max_attempts=max_attempts)
        if report["requeued"] or report["failed"]:
            logger.info("SESSION_BUILD_JOB_STALE_RECOVERY requeued=%s failed=%s", report["requeued"], report["failed"])
        return report
    finally:
        db.close()


def run_worker_loop(
    *,
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    stale_check_interval_seconds: float = DEFAULT_STALE_CHECK_INTERVAL_SECONDS,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    max_iterations: int | None = None,
) -> None:
    """Boucle principale du worker — ouvre/ferme une session DB par job (jamais une
    session unique gardée ouverte pendant toute la durée de vie du processus, potentiellement
    de plusieurs jours). `max_iterations` (réservé aux tests) borne la boucle ; `None` en
    production = boucle indéfiniment jusqu'à SIGTERM/SIGINT."""
    logger.info("CORRECTION_WORKER_STARTED poll_interval=%ss", poll_interval_seconds)
    stop = {"flag": False}

    def _handle_signal(signum, frame):
        logger.info("CORRECTION_WORKER_STOPPING signal=%s", signum)
        stop["flag"] = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    last_stale_check = 0.0
    iterations = 0
    while not stop["flag"]:
        now = time.monotonic()
        if now - last_stale_check >= stale_check_interval_seconds:
            recover_stale_jobs_once(stale_after_seconds=stale_after_seconds, max_attempts=max_attempts)
            recover_stale_build_jobs_once(stale_after_seconds=stale_after_seconds, max_attempts=max_attempts)
            last_stale_check = now

        # Ticket #92 : traite au plus un job de CHAQUE file par itération — ni file
        # jamais affamée par l'autre, ni logique de priorité complexe nécessaire (charge
        # faible des deux côtés).
        processed_correction = process_one_job(max_attempts=max_attempts)
        processed_build = process_one_build_job(max_attempts=max_attempts)
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
        if not processed_correction and not processed_build:
            time.sleep(poll_interval_seconds)

    logger.info("CORRECTION_WORKER_STOPPED")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_worker_loop()

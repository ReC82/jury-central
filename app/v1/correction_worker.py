"""Worker de correction asynchrone (ticket #88) — traite les `CorrectionJob` créés par
`POST /sessions/{id}/submit` (désormais non bloquant, voir `app.v1.session_service.
enqueue_correction`) HORS du cycle requête/réponse HTTP, seule façon de supprimer
structurellement le 504 Gateway Time-out réellement observé en staging (l'appel IA groupé
peut prendre plusieurs dizaines de secondes, largement au-delà de ce qu'un timeout nginx/
upstream tolère — augmenter ce timeout ne change rien au problème de MODÈLE : une requête
HTTP synchrone n'est pas le bon outil pour un traitement long).

Volontairement le PLUS SIMPLE possible (§ 8 du ticket) : pas de file de messages
(Redis/Celery), une file DB-backed (table `v1_correction_jobs`, déjà utilisée pour la
réclamation atomique côté web) que ce processus interroge par polling. PAS une thread
Python attachée à une requête ou au processus web (qui serait tuée si le worker web
recycle) : un processus SÉPARÉ et LONGUEMENT VIVANT, lancé indépendamment du serveur web.

Lancement (aucun changement systemd — décision de déploiement laissée à ChatGPT, § 8/§ 15
du ticket) :

    .venv/bin/python -m app.v1.correction_worker

Le worker :
1. récupère les jobs `RUNNING` bloqués depuis trop longtemps (crash d'un worker précédent,
   § 9 du ticket) et les remet `PENDING` (ou `FAILED` au-delà du nombre maximal de
   tentatives) ;
2. réclame ATOMIQUEMENT le prochain job `PENDING` (`claim_next_pending_correction_job`) ;
3. exécute la correction réelle (`run_correction_job`, qui réutilise `_correct_and_
   finalize_claimed_session`, INCHANGÉE depuis les tickets #55/#62/#70/#71) ;
4. recommence, avec une courte pause seulement s'il n'y avait rien à faire.
"""

import logging
import signal
import time

from app.ai.factory import get_ai_provider
from app.ai.provider import AINotConfiguredError, AIProviderError
from app.database import SessionLocal
from app.v1.session_service import (
    claim_next_pending_correction_job,
    recover_stale_correction_jobs,
    run_correction_job,
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
            last_stale_check = now

        processed = process_one_job(max_attempts=max_attempts)
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
        if not processed:
            time.sleep(poll_interval_seconds)

    logger.info("CORRECTION_WORKER_STOPPED")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_worker_loop()

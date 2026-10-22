"""Suivi d'usage IA (ticket #46) — compteurs pour l'administration de la banque.

`UsageTrackingProvider` enveloppe le fournisseur IA réellement utilisé (réel ou factice)
sans changer le protocole `app.ai.provider.AIProvider` : il compte les appels, les
questions générées et les questions corrigées par IA, et récupère les jetons consommés
quand le fournisseur sait les donner (`consume_usage()`, voir
`app.ai.openai_provider.OpenAIProvider` ; le fournisseur factice n'en donne pas → 0).

`record_ai_usage` écrit un `AIUsageEvent` (par module, pour l'admin) et met à jour
l'agrégat mensuel `AIUsage` de l'utilisateur. Le coût est une ESTIMATION à partir des
tarifs configurés (`settings.ai_cost_input_per_million`/`ai_cost_output_per_million`),
jamais un montant facturé. Un échec d'enregistrement n'interrompt jamais le flux métier
(savepoint annulé, erreur journalisée) — même principe que le rating (#45)."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.v1.models import AIUsage, AIUsageEvent

logger = logging.getLogger(__name__)

KIND_GENERATION = "generation"
KIND_CORRECTION = "correction"
KIND_ADMIN_VARIANT = "admin_variant"


class UsageTrackingProvider:
    """Délègue tout au fournisseur enveloppé ; ne modifie jamais une entrée ni un
    résultat. Les exceptions du fournisseur remontent telles quelles (l'appel est
    compté quand même : il a été tenté)."""

    def __init__(self, provider: Any) -> None:
        self._provider = provider
        self.calls = 0
        self.generated_questions = 0
        self.ai_corrections = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._provider, name)

    def generate_questionnaire(self, request):
        self.calls += 1
        questionnaire = self._provider.generate_questionnaire(request)
        self.generated_questions += len(getattr(questionnaire, "questions", []) or [])
        return questionnaire

    def correct_semantic_batch(self, questions, answers, severity, contexts):
        self.calls += 1
        results = self._provider.correct_semantic_batch(questions, answers, severity, contexts)
        self.ai_corrections += len(results or {})
        return results

    def consume_tokens(self) -> tuple[int, int]:
        consume = getattr(self._provider, "consume_usage", None)
        if not callable(consume):
            return 0, 0
        usage = consume() or {}
        return int(usage.get("input_tokens", 0) or 0), int(usage.get("output_tokens", 0) or 0)


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return round(
        input_tokens * settings.ai_cost_input_per_million / 1_000_000
        + output_tokens * settings.ai_cost_output_per_million / 1_000_000,
        6,
    )


def record_ai_usage(
    db: Session,
    tracker: UsageTrackingProvider,
    *,
    kind: str,
    module_id: int | None,
    user_id: int | None = None,
    session_id: int | None = None,
    failed: bool = False,
) -> AIUsageEvent | None:
    """Enregistre l'usage accumulé par `tracker` (rien si aucun appel IA n'a été fait).
    N'appelle jamais `commit` : à l'appelant de le faire dans sa transaction."""
    if tracker.calls == 0:
        return None
    input_tokens, output_tokens = tracker.consume_tokens()
    provider_name = getattr(tracker, "provider_name", None)
    model_name = getattr(tracker, "model_name", None)
    provider_name = provider_name if isinstance(provider_name, str) else None
    model_name = model_name if isinstance(model_name, str) else None
    cost = estimate_cost(input_tokens, output_tokens)
    try:
        with db.begin_nested():
            event = AIUsageEvent(
                module_id=module_id,
                user_id=user_id,
                session_id=session_id,
                kind=kind,
                provider=provider_name,
                model=model_name,
                calls=tracker.calls,
                generated_questions=tracker.generated_questions,
                ai_corrections=tracker.ai_corrections,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=cost,
                failed=failed,
            )
            db.add(event)
            if user_id is not None:
                period_key = datetime.now(UTC).strftime("%Y-%m")
                aggregate = (
                    db.query(AIUsage)
                    .filter_by(user_id=user_id, period_key=period_key, provider=provider_name, model=model_name)
                    .first()
                )
                if aggregate is None:
                    aggregate = AIUsage(
                        user_id=user_id, period_key=period_key, provider=provider_name, model=model_name,
                        generated_questions=0, ai_corrections=0, input_tokens=0, output_tokens=0,
                        estimated_cost=0.0,
                    )
                    db.add(aggregate)
                aggregate.generated_questions += tracker.generated_questions
                aggregate.ai_corrections += tracker.ai_corrections
                aggregate.input_tokens += input_tokens
                aggregate.output_tokens += output_tokens
                aggregate.estimated_cost = round(aggregate.estimated_cost + cost, 6)
            db.flush()
    except Exception:  # un compteur ne doit jamais casser une session
        logger.exception("AI_USAGE_RECORD_FAILED kind=%s module_id=%s", kind, module_id)
        return None
    return event

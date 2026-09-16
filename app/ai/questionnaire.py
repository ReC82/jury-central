"""Orchestrateur du contrat générique « questionnaire » (ticket #23).

Contient la POLITIQUE (retry borné, filtrage par types autorisés, recalage du barème sur
`total_points`, routage local/IA de la correction, validation serveur des points) —
indépendante du fournisseur utilisé (réel ou factice, voir `app/ai/provider.py`). Le
fournisseur ne fait que l'I/O (un appel réseau, une réponse structurée) ; toute décision
de robustesse ou de sécurité vit ici, dans du code entièrement testable sans réseau.

Destiné à être appelé par les tickets #24 (S'entraîner) et #25 (S'évaluer), pour toutes
les matières — voir `docs/claude-reports/2026-09-16_ticket-23_openai-contract.md`.
"""

import dataclasses

from app.ai.local_correction import correct_locally, requires_ai_correction
from app.ai.provider import AIProvider, AIResponseError
from app.ai.schemas import (
    SEVERITY_LEVELS,
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireCorrection,
    QuestionnaireQuestion,
    QuestionnaireRequest,
    QuestionnaireValidationError,
)

# Nombre maximal de tentatives de génération si la réponse du fournisseur est invalide ou
# vide (voir AIResponseError) — borné et documenté, jamais de boucle indéfinie.
MAX_GENERATE_ATTEMPTS = 2


def generate_questionnaire(provider: AIProvider, request: QuestionnaireRequest) -> Questionnaire:
    """Génère un questionnaire, avec un nombre borné de tentatives et une validation
    serveur systématique du résultat — jamais confiance aveugle dans la réponse du
    fournisseur, même après un JSON structurellement valide.

    Validation appliquée après chaque tentative :
    1. toute question dont le `type` n'est pas dans `request.allowed_types` est retirée
       (défense en profondeur : le schéma JSON et le prompt le demandent déjà, mais rien
       ne garantit que le modèle s'y conforme) ;
    2. si `request.total_points` est fourni, les `points_max` restants sont recalés
       proportionnellement pour que leur somme corresponde exactement à `total_points` —
       jamais la valeur brute proposée par le modèle, qui ne fait jamais foi seule.
    """
    last_error: AIResponseError | None = None
    for _ in range(MAX_GENERATE_ATTEMPTS):
        try:
            questionnaire = provider.generate_questionnaire(request)
        except AIResponseError as exc:
            last_error = exc
            continue

        filtered_questions = [
            question
            for question in questionnaire.questions
            if question.type in request.allowed_types
        ]
        if not filtered_questions:
            last_error = AIResponseError(
                "Aucune question du type demandé n'a pu être générée."
            )
            continue

        if request.total_points is not None:
            filtered_questions = _rescale_points(filtered_questions, request.total_points)

        return Questionnaire(mode=questionnaire.mode, questions=filtered_questions)

    assert last_error is not None  # au moins une tentative a été faite (MAX_GENERATE_ATTEMPTS >= 1)
    raise last_error


def _rescale_points(
    questions: list[QuestionnaireQuestion], total_points: float
) -> list[QuestionnaireQuestion]:
    """Recale `points_max` de chaque question pour que leur somme égale exactement
    `total_points`, au centime près (le dernier terme absorbe l'arrondi résiduel). Ne fait
    jamais confiance à la somme proposée par le modèle."""
    current_total = sum(question.points_max for question in questions)
    if current_total <= 0:
        # Ne peut pas répartir proportionnellement une somme nulle/négative : répartition
        # égale de secours, toujours mieux qu'une exception ici (défense en profondeur ;
        # ne devrait jamais arriver, points_max > 0 étant déjà validé à la construction).
        share = round(total_points / len(questions), 2)
        rescaled = [share] * len(questions)
    else:
        rescaled = [
            round(question.points_max / current_total * total_points, 2) for question in questions
        ]
    # Corrige l'arrondi résiduel sur le dernier élément pour une somme exacte.
    rescaled[-1] = round(total_points - sum(rescaled[:-1]), 2)

    result = []
    for question, points_max in zip(questions, rescaled, strict=True):
        result.append(_with_points_max(question, max(points_max, 0.01)))
    return result


def _with_points_max(question: QuestionnaireQuestion, points_max: float) -> QuestionnaireQuestion:
    """Reconstruit la question avec un `points_max` différent (dataclass, pas de mutation
    in place pour rester cohérent avec le reste du module)."""
    return dataclasses.replace(question, points_max=points_max)


def correct_questionnaire(
    provider: AIProvider,
    questionnaire: Questionnaire,
    answers: dict[str, object],
    severity: str,
    contexts: list[PedagogicalContext],
) -> QuestionnaireCorrection:
    """Corrige un questionnaire complet : les questions déterministes sont corrigées
    localement (jamais d'appel IA, voir `app.ai.local_correction`), les questions
    sémantiques sont regroupées en UN SEUL appel au fournisseur (jamais un appel par
    question). `points_max` vient toujours de `questionnaire`, jamais de la réponse du
    fournisseur ; `points_awarded` est toujours borné à `[0, points_max]` après coup, quel
    que soit ce que renvoie le fournisseur.
    """
    if severity not in SEVERITY_LEVELS:
        raise QuestionnaireValidationError(f"Sévérité inconnue : {severity!r}.")

    corrections: dict[str, QuestionCorrection] = {}
    semantic_questions: list[QuestionnaireQuestion] = []

    for question in questionnaire.questions:
        if requires_ai_correction(question):
            semantic_questions.append(question)
        else:
            submitted = answers.get(question.question_id)
            corrections[question.question_id] = correct_locally(question, submitted)

    if semantic_questions:
        semantic_answers = {
            question.question_id: answers.get(question.question_id)
            for question in semantic_questions
        }
        semantic_results = provider.correct_semantic_batch(
            semantic_questions, semantic_answers, severity, contexts
        )
        for question in semantic_questions:
            raw_correction = semantic_results.get(question.question_id)
            corrections[question.question_id] = _validated_correction(question, raw_correction)

    ordered_corrections = [
        corrections[question.question_id]
        for question in questionnaire.questions
        if question.question_id in corrections
    ]
    score = sum(correction.points_awarded for correction in ordered_corrections)
    max_score = sum(correction.points_max for correction in ordered_corrections)
    return QuestionnaireCorrection(
        score=round(score, 2), max_score=round(max_score, 2), questions=ordered_corrections
    )


def _validated_correction(
    question: QuestionnaireQuestion, raw_correction: QuestionCorrection | None
) -> QuestionCorrection:
    """`points_max` vient toujours de `question` (jamais de la réponse IA) ; `points_awarded`
    est toujours borné à `[0, points_max]`, quel que soit ce que le fournisseur a renvoyé —
    y compris si le fournisseur n'a renvoyé aucune correction pour cette question (traité
    comme 0 point, jamais une exception qui bloquerait tout le questionnaire)."""
    if raw_correction is None:
        return QuestionCorrection(
            question_id=question.question_id,
            points_awarded=0.0,
            points_max=question.points_max,
            correct=False,
            errors=["Le service de correction n'a pas traité cette question."],
            feedback="Correction indisponible pour cette question.",
        )

    points_awarded = max(0.0, min(raw_correction.points_awarded, question.points_max))
    return QuestionCorrection(
        question_id=question.question_id,
        points_awarded=points_awarded,
        points_max=question.points_max,
        correct=raw_correction.correct,
        strengths=raw_correction.strengths,
        errors=raw_correction.errors,
        missing=raw_correction.missing,
        feedback=raw_correction.feedback,
        expected_answer=raw_correction.expected_answer,
    )



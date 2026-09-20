"""Correction hybride (ticket #62) : le SCORE des types déterministes reste TOUJOURS
calculé et verrouillé localement (`app.ai.local_correction.correct_locally`, aucun appel
réseau, inchangé) — mais une question déterministe INCORRECTE est en plus soumise, dans le
MÊME et UNIQUE appel IA batch que les questions sémantiques, pour obtenir une explication
pédagogique réelle (pourquoi c'est faux, comment raisonner, quelle notion réviser) à la
place du message générique « Correction automatique déterministe (pas d'appel IA
nécessaire). ».

Aucune modification du contrat #23 (`app.ai.questionnaire`/`app.ai.schemas`/
`app.ai.prompts`) : une question déterministe est envoyée à `provider.correct_semantic_batch`
comme n'importe quelle question du lot, avec son `rubric` augmenté d'une instruction
explicite « le score est déjà fixé, n'explique que le raisonnement » — le format de
requête/réponse (`CORRECT_SEMANTIC_JSON_SCHEMA`) ne change pas, donc `editorial_ai_correction.py`
(seul autre appelant de `correct_semantic_batch`) n'est affecté en rien. Après la réponse,
seuls les champs textuels (`strengths`/`errors`/`missing`/`feedback`) de l'IA sont retenus
pour ces questions — `points_awarded`/`points_max`/`correct`/`expected_answer` restent
strictement ceux de la correction locale, quoi que l'IA renvoie (§ 3 du ticket :
« l'IA n'a PAS le droit de modifier ce score »).

Exception délibérée (ticket #64 § 7) : `short_answer`/`vocabulary` corrigées localement par
égalité textuelle normalisée (voir `app.answer_checking.text_answer_matches`) peuvent
produire un FAUX négatif — une formulation humaine correcte mais absente de
`accepted_answers` (ex. « l'écart entre deux débuts de sous-réseaux » vs. « le nombre entre
le début d'un sous-réseau et le début du suivant »). Pour ces deux types SEULEMENT, une
réponse locale INCORRECTE n'est donc pas verrouillée comme les autres types déterministes :
elle est envoyée en évaluation sémantique complète (score potentiellement réévalué par
l'IA, borné comme une question sémantique ordinaire via `validate_semantic_correction`) —
jamais ordering/classification/QCM/numeric/etc., qui restent strictement déterministes,
score inchangé (§ 7 : « Pour ordering/classification/QCM : score déterministe inchangé »).
Une réponse locale déjà CORRECTE pour ces deux types n'est, comme avant, jamais envoyée à
l'IA (aucun coût inutile)."""

import dataclasses

from app.ai.local_correction import correct_locally, requires_ai_correction
from app.ai.provider import AIProvider, AIProviderError
from app.ai.questionnaire import validate_semantic_correction
from app.ai.schemas import (
    CONDITIONALLY_LOCAL_QUESTION_TYPES,
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireCorrection,
    QuestionnaireQuestion,
)

# short_answer/vocabulary : voir docstring du module, § exception ticket #64 § 7. Pas
# d'autres types — une correction textuelle stricte reste voulue pour fill_blank (réponse
# attendue très contrainte, un seul mot/valeur), contrairement à short_answer/vocabulary où
# plusieurs formulations humaines équivalentes sont normales.
RESCORABLE_LOCAL_TYPES = CONDITIONALLY_LOCAL_QUESTION_TYPES


def _explanation_rubric(question: QuestionnaireQuestion, local: QuestionCorrection) -> str:
    verdict = "CORRECTE" if local.correct else "INCORRECTE"
    instruction = (
        f"IMPORTANT : cette question (type « {question.type} ») est déterministe et déjà "
        f"corrigée automatiquement côté serveur — verdict final : {verdict} "
        f"({local.points_awarded}/{local.points_max} point(s), déjà fixé, NE PAS le "
        "recalculer ni le contredire, quelle que soit ton analyse). "
        f"Réponse attendue : {local.expected_answer or '(voir énoncé ci-dessus)'}. "
        "Ta seule tâche : explique pédagogiquement, via les champs errors/missing/"
        "feedback, POURQUOI la réponse du candidat est incorrecte, COMMENT raisonner pour "
        "trouver la bonne réponse, et QUELLE notion réviser. Le champ points_awarded est "
        "requis par le format mais sera intégralement ignoré par le serveur — n'indique "
        "aucune note ni barème dans ton texte."
    )
    return f"{question.rubric}\n\n{instruction}" if question.rubric else instruction


def _semantic_rescoring_rubric(question: QuestionnaireQuestion, local: QuestionCorrection) -> str:
    """Grille pour la ré-évaluation sémantique d'un `short_answer`/`vocabulary` jugé
    incorrect par la comparaison textuelle locale (ticket #64 § 7) — explique à l'IA que
    cette comparaison stricte a pu produire un faux négatif et lui délègue un VRAI jugement
    sémantique, contrairement à `_explanation_rubric` qui ne demande qu'un texte."""
    accepted = ", ".join(f"« {answer} »" for answer in question.accepted_answers) or "(aucune listée)"
    instruction = (
        "IMPORTANT : une comparaison textuelle automatique a jugé cette réponse "
        f"INCORRECTE car elle ne correspond littéralement à aucune formulation acceptée "
        f"({accepted}), mais plusieurs formulations humaines équivalentes sont possibles "
        "pour ce type de question — n'impose JAMAIS une égalité textuelle stricte. "
        "Évalue réellement le sens de la réponse du candidat par rapport à la notion "
        "attendue : si elle est sémantiquement équivalente à une formulation acceptée, "
        "corrige-la comme correcte (score plein, dans la limite du barème indiqué), même "
        "si sa formulation diffère. Sinon, explique pourquoi et attribue un score "
        "cohérent avec la sévérité demandée."
    )
    return f"{question.rubric}\n\n{instruction}" if question.rubric else instruction


def _lock_score_keep_ai_explanation(
    local: QuestionCorrection, raw_correction: QuestionCorrection | None
) -> QuestionCorrection:
    """Le score/correct/points_max/expected_answer restent ceux de la correction LOCALE,
    verrouillés — jamais modifiés par l'IA. Seuls les champs textuels pédagogiques
    proviennent de l'IA si elle en a fourni, sinon la correction locale reste inchangée
    (repli explicite, ex. si le fournisseur n'a renvoyé aucune entrée pour cette
    question_id)."""
    if raw_correction is None:
        return local
    return QuestionCorrection(
        question_id=local.question_id,
        points_awarded=local.points_awarded,
        points_max=local.points_max,
        correct=local.correct,
        strengths=raw_correction.strengths or local.strengths,
        errors=raw_correction.errors or local.errors,
        missing=raw_correction.missing or local.missing,
        feedback=raw_correction.feedback or local.feedback,
        expected_answer=local.expected_answer,
    )


def correct_session_hybrid(
    provider: AIProvider,
    questionnaire: Questionnaire,
    answers: dict[str, object],
    human_readable_answers: dict[str, str],
    severity: str,
    contexts: tuple[PedagogicalContext, ...],
) -> QuestionnaireCorrection:
    """Corrige un questionnaire complet, en UN SEUL appel IA batch maximum, qui regroupe :
    (A) les questions sémantiques nécessitant une notation IA (comme
    `app.ai.questionnaire.correct_questionnaire`, inchangé) ;
    (B) les questions déterministes INCORRECTES, pour lesquelles seule une EXPLICATION
    pédagogique est demandée — leur score reste celui de `correct_locally`, jamais modifié.

    Une question déterministe CORRECTE n'est jamais envoyée à l'IA (§ 3 du ticket : pas
    besoin d'explication détaillée sur une bonne réponse).

    `human_readable_answers` (ticket #62 § batch) : description lisible de la réponse
    donnée pour les questions déterministes (ex. « SSD → RAM → écran → CPU » pour un
    ordering), utilisée à la place de la représentation interne brute (une liste d'index)
    pour que l'IA puisse réellement comprendre et expliquer l'erreur — voir
    `app.v1.ai_bridge.describe_submitted_answer`, déjà utilisé par l'écran de résultats.

    Peut lever `AIProviderError` (propagée telle quelle, voir `app.ai.provider`) — à
    l'appelant de gérer le repli explicite (voir `app.v1.session_service.submit_session`)."""
    corrections: dict[str, QuestionCorrection] = {}
    semantic_questions: list[QuestionnaireQuestion] = []
    explain_only_questions: list[QuestionnaireQuestion] = []
    rescorable_questions: list[QuestionnaireQuestion] = []

    for question in questionnaire.questions:
        if requires_ai_correction(question):
            semantic_questions.append(question)
            continue
        local = correct_locally(question, answers.get(question.question_id))
        corrections[question.question_id] = local
        if local.correct:
            continue
        if question.type in RESCORABLE_LOCAL_TYPES:
            # Voir docstring du module, § exception ticket #64 § 7 : short_answer/
            # vocabulary incorrects localement méritent une VRAIE ré-évaluation
            # sémantique (score potentiellement révisé), pas seulement une explication.
            rescorable_questions.append(
                dataclasses.replace(question, rubric=_semantic_rescoring_rubric(question, local))
            )
        else:
            explain_only_questions.append(
                dataclasses.replace(question, rubric=_explanation_rubric(question, local))
            )

    batch_questions = [*semantic_questions, *rescorable_questions, *explain_only_questions]
    if batch_questions:
        batch_answers: dict[str, object] = {
            q.question_id: answers.get(q.question_id) for q in semantic_questions
        }
        for q in rescorable_questions:
            batch_answers[q.question_id] = human_readable_answers.get(q.question_id, "")
        for q in explain_only_questions:
            batch_answers[q.question_id] = human_readable_answers.get(q.question_id, "")

        raw_results = provider.correct_semantic_batch(batch_questions, batch_answers, severity, contexts)

        for question in [*semantic_questions, *rescorable_questions]:
            corrections[question.question_id] = validate_semantic_correction(
                question, raw_results.get(question.question_id)
            )
        for question in explain_only_questions:
            local = corrections[question.question_id]
            corrections[question.question_id] = _lock_score_keep_ai_explanation(
                local, raw_results.get(question.question_id)
            )

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


def correct_session_hybrid_resumable(
    provider: AIProvider,
    questionnaire: Questionnaire,
    answers: dict[str, object],
    human_readable_answers: dict[str, str],
    severity: str,
    contexts: tuple[PedagogicalContext, ...],
    *,
    already_corrected: dict[str, QuestionCorrection] | None = None,
) -> tuple[dict[str, QuestionCorrection], frozenset[str]]:
    """Variante RÉSUMABLE de `correct_session_hybrid` (ticket #90) — utilisée par le job de
    correction asynchrone (`app.v1.session_service.run_correction_job`), JAMAIS par
    `submit_session` (§ 62/#70/#71, inchangée, continue d'utiliser `correct_session_hybrid`
    ci-dessus tel quel).

    Deux différences fondamentales avec `correct_session_hybrid` :

    1. **Jamais de faux 0** (§ 90.1) : si `provider.correct_semantic_batch` échoue
       (`AIProviderError`) ou ne renvoie pas de correction pour une question qui a
       RÉELLEMENT besoin d'une notation IA (`semantic_questions`/`rescorable_questions` —
       celles dont le SCORE dépend de l'IA), cette question est retournée dans
       `unresolved`, JAMAIS avec un `QuestionCorrection` à 0 point fabriqué. Les questions
       `explain_only_questions` (déterministes, score déjà verrouillé et correct par
       `correct_locally`, l'IA n'apporte qu'une explication pédagogique) restent gérées
       comme avant — leur score ne dépend jamais de l'IA, donc un échec IA ne les rend
       jamais `unresolved` : elles gardent le message de repli existant (§ 55/§ 62).

    2. **Résumable** (§ 90.4/90.5, retry ciblé) : `already_corrected` fournit les
       corrections déjà obtenues lors d'une tentative précédente (lues depuis
       `SessionAnswer.correction_status == CORRECTED` par l'appelant) — ces questions sont
       exclues de tout nouvel appel IA, jamais renvoyées à l'IA une seconde fois, jamais
       recalculées.

    Retourne `(corrections, unresolved)` — `corrections` couvre TOUTES les questions qui
    ont une correction réelle (déterministes + déjà acquises + nouvellement obtenues) ;
    `unresolved` est l'ensemble des `question_id` encore en attente d'une vraie correction
    IA. L'appelant ne finalise (`SessionStatus.COMPLETED`) que si `unresolved` est vide."""
    already_corrected = already_corrected or {}
    corrections: dict[str, QuestionCorrection] = dict(already_corrected)
    semantic_questions: list[QuestionnaireQuestion] = []
    explain_only_questions: list[QuestionnaireQuestion] = []
    rescorable_questions: list[QuestionnaireQuestion] = []

    for question in questionnaire.questions:
        if question.question_id in already_corrected:
            continue
        if requires_ai_correction(question):
            semantic_questions.append(question)
            continue
        local = correct_locally(question, answers.get(question.question_id))
        if local.correct or question.type not in RESCORABLE_LOCAL_TYPES:
            corrections[question.question_id] = local
        if local.correct:
            continue
        if question.type in RESCORABLE_LOCAL_TYPES:
            # Score-gating (§ 90.9) : une correction locale INCORRECTE pour ces deux types
            # n'est jamais définitive — jamais stockée dans `corrections` tant que l'IA ne
            # l'a pas confirmée/révisée (voir docstring du module, § exception ticket #64).
            rescorable_questions.append(
                dataclasses.replace(question, rubric=_semantic_rescoring_rubric(question, local))
            )
        else:
            explain_only_questions.append(
                dataclasses.replace(question, rubric=_explanation_rubric(question, local))
            )

    unresolved: set[str] = set()
    batch_questions = [*semantic_questions, *rescorable_questions, *explain_only_questions]
    if not batch_questions:
        return corrections, frozenset(unresolved)

    batch_answers: dict[str, object] = {q.question_id: answers.get(q.question_id) for q in semantic_questions}
    for q in rescorable_questions:
        batch_answers[q.question_id] = human_readable_answers.get(q.question_id, "")
    for q in explain_only_questions:
        batch_answers[q.question_id] = human_readable_answers.get(q.question_id, "")

    try:
        raw_results = provider.correct_semantic_batch(batch_questions, batch_answers, severity, contexts)
    except AIProviderError:
        # Score-gating : jamais de repli qui fabrique une note — reste `unresolved`.
        unresolved.update(q.question_id for q in [*semantic_questions, *rescorable_questions])
        # Non score-gating : le score déterministe reste celui déjà verrouillé ci-dessus ;
        # seule l'explication pédagogique manque — repli explicite existant (§ 55/§ 62),
        # jamais un blocage pour une question déjà correctement notée.
        for question in explain_only_questions:
            corrections[question.question_id] = correct_locally(question, answers.get(question.question_id))
        return corrections, frozenset(unresolved)

    for question in [*semantic_questions, *rescorable_questions]:
        raw = raw_results.get(question.question_id)
        if raw is None:
            # Réponse IA incomplète (question absente du lot renvoyé) — jamais un 0
            # fabriqué par `validate_semantic_correction` pour une question score-gating.
            unresolved.add(question.question_id)
            continue
        corrections[question.question_id] = validate_semantic_correction(question, raw)

    for question in explain_only_questions:
        local = corrections[question.question_id]
        corrections[question.question_id] = _lock_score_keep_ai_explanation(
            local, raw_results.get(question.question_id)
        )

    return corrections, frozenset(unresolved)

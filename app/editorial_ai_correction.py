"""Pont entre les exercices éditoriaux structurés persistés (`app/editorial_exercise.py`,
tickets #17/#21) et la correction sémantique IA existante (`app/ai/`, ticket #23) — ticket
#29.

Réutilise intégralement l'infrastructure IA déjà en place : `AIProvider.
correct_semantic_batch` (même protocole que le contrat questionnaire #23) et
`app.ai.questionnaire.validate_semantic_correction` (même validation serveur des points,
jamais dupliquée). Aucun second moteur IA, aucun appel réseau supplémentaire par rapport à
ce qu'un item nécessite réellement (un seul appel, pour un seul item à la fois — la
correction éditoriale se fait un exercice après l'autre, contrairement au questionnaire
#23 qui regroupe plusieurs questions en un seul appel).

`app/editorial_exercise.py` ne dépend jamais de ce module ni de `app/ai/` : seul ce pont
(et `app/practice.py`, qui l'appelle) connaît les deux mondes.
"""

from app.ai.provider import AIProvider
from app.ai.questionnaire import validate_semantic_correction
from app.ai.schemas import PedagogicalContext, QuestionnaireQuestion
from app.editorial_exercise import EditorialExerciseCorrection, EditorialExerciseItem

# Sévérité par défaut pour la correction IA d'un exercice éditorial de pratique — la
# sélection de sévérité (bienveillante/standard/stricte, ticket #23) est un choix d'UX
# laissé aux tickets qui construiront une interface dédiée (#24/#25) ; S'entraîner (#29)
# utilise un défaut raisonnable et documenté, pas un choix arbitraire caché.
DEFAULT_PRACTICE_SEVERITY = "standard"


def editorial_item_to_question(item: EditorialExerciseItem) -> QuestionnaireQuestion:
    """Traduit un `EditorialExerciseItem` (persisté, `LessonBlock.content`) vers le
    schéma générique `QuestionnaireQuestion` (#23) attendu par `correct_semantic_batch`.
    `item.explanation` sert de grille de correction (`rubric`) — c'est déjà le texte qui
    explique la bonne réponse aux étudiants, donc naturellement adapté à guider une
    appréciation IA sans dupliquer de contenu ni ajouter un nouveau champ d'auteurisation.
    """
    return QuestionnaireQuestion(
        question_id=item.exercise_id,
        type=item.type,
        prompt=item.prompt,
        points_max=item.points,
        accepted_answers=list(item.accepted_answers),
        rubric=item.explanation,
    )


def correct_editorial_item_with_ai(
    provider: AIProvider,
    item: EditorialExerciseItem,
    submitted: str,
    context: PedagogicalContext,
    severity: str = DEFAULT_PRACTICE_SEVERITY,
) -> EditorialExerciseCorrection:
    """Corrige un item éditorial dont le type nécessite une appréciation sémantique
    (`item.requires_ai_correction()` doit être vrai — vérifié par l'appelant, voir
    `app/practice.py`). `points_max` provient toujours de `item` (jamais de la réponse du
    fournisseur), `points_awarded` toujours borné à `[0, points_max]` — même garantie que
    le contrat questionnaire #23, via `validate_semantic_correction`, jamais un second
    mécanisme de bornage."""
    question = editorial_item_to_question(item)
    results = provider.correct_semantic_batch(
        [question], {item.exercise_id: submitted}, severity, [context]
    )
    validated = validate_semantic_correction(question, results.get(item.exercise_id))
    return EditorialExerciseCorrection(
        exercise_id=item.exercise_id,
        correct=validated.correct,
        correct_answer=validated.expected_answer,
        explanation=validated.feedback,
        points_awarded=validated.points_awarded,
        points_max=validated.points_max,
        strengths=validated.strengths,
        errors=validated.errors,
        missing=validated.missing,
    )

"""Fournisseur IA factice, déterministe, sans aucun appel réseau.

Utilisé par les tests (`tests/ai/`) pour vérifier les routes et le câblage sans consommer
d'API réelle, conformément au complément IA du ticket #10 (« prévoir tests avec provider
mock/fake, sans consommation réelle d'API dans pytest »).

Ticket #23 : ajoute `generate_questionnaire`/`correct_semantic_batch`, tracés de la même
façon (`questionnaire_calls`/`semantic_calls`) — permet notamment de vérifier qu'un
questionnaire purement déterministe (QCM, vrai/faux, ordering, ...) ne déclenche JAMAIS
`correct_semantic_batch` (voir `tests/ai/test_questionnaire.py`)."""

from typing import Any

from app.ai.schemas import (
    AICorrectionResult,
    GeneratedAIExercise,
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireQuestion,
    QuestionnaireRequest,
)


class FakeAIProvider:
    """Ne contacte jamais de service externe. Comportement déterministe et inspectable."""

    def __init__(self) -> None:
        self.generate_calls: list[tuple[PedagogicalContext, str]] = []
        self.correct_calls: list[tuple[PedagogicalContext, str, str, str, str]] = []
        self.questionnaire_calls: list[QuestionnaireRequest] = []
        self.semantic_calls: list[tuple[tuple[str, ...], str]] = []

    def generate_exercise(
        self, context: PedagogicalContext, difficulty: str
    ) -> GeneratedAIExercise:
        self.generate_calls.append((context, difficulty))
        return GeneratedAIExercise(
            exercise_type="mise en situation",
            difficulty=difficulty,
            statement=(
                f"[exercice factice — {context.course_title}, difficulté {difficulty}] "
                "Décris le rôle d'un composant de ce cours dans une situation concrète."
            ),
        )

    def correct_answer(
        self,
        context: PedagogicalContext,
        exercise_statement: str,
        exercise_type: str,
        difficulty: str,
        candidate_answer: str,
    ) -> AICorrectionResult:
        self.correct_calls.append(
            (context.course_key, exercise_statement, exercise_type, difficulty, candidate_answer)
        )
        return AICorrectionResult(
            appreciation="Correction factice (environnement de test).",
            correct_points=["Réponse reçue et prise en compte."],
            errors=[],
            expected_answer_explained="Réponse attendue factice, à titre d'exemple.",
            score=None,
            max_score=None,
        )

    def generate_questionnaire(self, request: QuestionnaireRequest) -> Questionnaire:
        self.questionnaire_calls.append(request)
        allowed = list(request.allowed_types)
        raw_points = [1.0] * request.question_count
        if request.total_points is not None:
            share = request.total_points / request.question_count
            raw_points = [share] * request.question_count

        questions = []
        for index in range(request.question_count):
            question_type = allowed[index % len(allowed)]
            questions.append(
                _fake_question(f"fake-q{index + 1}", question_type, raw_points[index])
            )
        return Questionnaire(mode=request.mode, questions=questions)

    def correct_semantic_batch(
        self,
        questions: list[QuestionnaireQuestion],
        answers: dict[str, Any],
        severity: str,
        contexts: list[PedagogicalContext],
    ) -> dict[str, QuestionCorrection]:
        self.semantic_calls.append((tuple(q.question_id for q in questions), severity))
        # "lenient"/"standard"/"strict" gardent leurs valeurs historiques (voir
        # tests/ai/test_questionnaire.py::test_correct_questionnaire_severity_changes_points_not_facts) ;
        # "very_lenient"/"very_strict" (ticket #62, échelle 1-5) étendent l'échelle sans
        # modifier les 3 valeurs déjà testées.
        factor = {
            "very_lenient": 1.0,
            "lenient": 1.0,
            "standard": 0.75,
            "strict": 0.5,
            "very_strict": 0.25,
        }[severity]

        results: dict[str, QuestionCorrection] = {}
        for question in questions:
            submitted = str(answers.get(question.question_id, ""))
            points_awarded = round(question.points_max * factor, 2) if submitted.strip() else 0.0
            results[question.question_id] = QuestionCorrection(
                question_id=question.question_id,
                points_awarded=points_awarded,
                points_max=question.points_max,
                correct=points_awarded >= question.points_max / 2,
                strengths=["Réponse factice prise en compte."] if submitted.strip() else [],
                errors=[] if submitted.strip() else ["Aucune réponse fournie."],
                missing=[],
                feedback=f"Correction factice (sévérité {severity}, environnement de test).",
                expected_answer="Réponse attendue factice, à titre d'exemple.",
            )
        return results


def _fake_question(
    question_id: str, question_type: str, points_max: float
) -> QuestionnaireQuestion:
    """Construit une question factice structurellement valide pour chaque type du contrat
    (voir `app.ai.schemas.QUESTION_TYPES`) — utilisée uniquement par `FakeAIProvider`."""
    common = {"question_id": question_id, "type": question_type, "points_max": points_max}
    if question_type in ("single_choice", "true_false"):
        choices = ["Vrai", "Faux"] if question_type == "true_false" else ["Option A", "Option B"]
        return QuestionnaireQuestion(
            **common, prompt="Question factice à choix.", choices=choices, correct_indexes=[0]
        )
    if question_type == "multiple_choice":
        return QuestionnaireQuestion(
            **common,
            prompt="Question factice à choix multiples.",
            choices=["Option A", "Option B", "Option C"],
            correct_indexes=[0, 2],
        )
    if question_type == "ordering":
        return QuestionnaireQuestion(
            **common,
            prompt="Remets ces étapes factices dans l'ordre.",
            order_items=["Étape A", "Étape B"],
            correct_order=[1, 0],
        )
    if question_type == "classification":
        return QuestionnaireQuestion(
            **common,
            prompt="Classe ces éléments factices.",
            categories=["Catégorie 1", "Catégorie 2"],
            elements=["Élément A", "Élément B"],
            correct_categories=[0, 1],
        )
    if question_type == "matching":
        return QuestionnaireQuestion(
            **common,
            prompt="Associe ces éléments factices.",
            pairs_left=["Gauche A", "Gauche B"],
            pairs_right=["Droite A", "Droite B"],
            correct_pairs=[0, 1],
        )
    if question_type == "numeric":
        return QuestionnaireQuestion(
            **common,
            prompt="Combien font 2 + 2 (factice) ?",
            numeric_answer=4,
            numeric_tolerance=0,
        )
    if question_type == "fill_blank":
        return QuestionnaireQuestion(
            **common,
            prompt="Complète : la ___ vive est volatile (factice).",
            accepted_answers=["mémoire"],
        )
    if question_type in ("short_answer", "vocabulary"):
        return QuestionnaireQuestion(
            **common,
            prompt="Question factice à réponse courte.",
            accepted_answers=["réponse factice"],
        )
    # long_answer / diagnostic / procedure : toujours sémantiques, nécessitent un rubric.
    return QuestionnaireQuestion(
        **common,
        prompt=f"Question factice de type {question_type}.",
        rubric="Grille de correction factice : vérifier la présence des notions clés.",
    )

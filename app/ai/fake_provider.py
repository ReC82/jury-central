"""Fournisseur IA factice, déterministe, sans aucun appel réseau.

Utilisé par les tests (`tests/ai/`) pour vérifier les routes et le câblage sans consommer
d'API réelle, conformément au complément IA du ticket #10 (« prévoir tests avec provider
mock/fake, sans consommation réelle d'API dans pytest »).
"""

from app.ai.schemas import AICorrectionResult, GeneratedAIExercise, PedagogicalContext


class FakeAIProvider:
    """Ne contacte jamais de service externe. Comportement déterministe et inspectable."""

    def __init__(self) -> None:
        self.generate_calls: list[tuple[PedagogicalContext, str]] = []
        self.correct_calls: list[tuple[PedagogicalContext, str, str, str, str]] = []

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

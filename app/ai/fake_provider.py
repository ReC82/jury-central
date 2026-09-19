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
                _fake_question(f"fake-q{index + 1}", question_type, raw_points[index], index)
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


def _variation_clause(index: int) -> str:
    """Ticket #82 : suffixe garanti distinct pour deux `index` différents, utilisé pour
    que deux questions factices du même type ne soient jamais un quasi-doublon (#64,
    seuil de recouvrement lexical 0.72 des mots significatifs de l'énoncé).

    UN SEUL jeton qui varie (ex. juste un numéro) reste insuffisant sur les prompts
    COURTS sans champ structurel comparable (`diagnostic`/`long_answer`/`procedure`/
    `troubleshooting`/`document_analysis`/`source_comparison` — aucune entrée dans
    `dedup._STRUCTURAL_FIELDS`, donc seul l'énoncé compte pour la comparaison) : avec un
    énoncé de base de 7 mots significatifs et seulement 1 mot qui diffère, le
    recouvrement reste à 7/9 ≈ 0.78, au-dessus du seuil. DEUX jetons indépendants (jamais
    un mot de vocabulaire partagé comme « repère »/« factice », qui gonflerait la partie
    commune) ramènent le recouvrement sous 0.64 dans tous les cas testés — vérifié pour le
    pire cas réaliste (types répétés jusqu'à 3 fois dans un lot de 20 avec les 7
    `BRIDGE_TYPES`)."""
    return f" #FQ{index + 1} #V{(index + 1) * 7 + 3}"


def _fake_question(
    question_id: str, question_type: str, points_max: float, index: int = 0
) -> QuestionnaireQuestion:
    """Construit une question factice structurellement valide pour chaque type du contrat
    (voir `app.ai.schemas.QUESTION_TYPES`) — utilisée uniquement par `FakeAIProvider`.

    Ticket #82 : chaque label/énoncé porte un suffixe dérivé de `index`
    (`_variation_clause`, ex. « Option A (repère factice atelier-7) ») — un vrai
    fournisseur IA ne produit jamais deux questions du même type strictement identiques au
    sein d'un même lot, contrairement à l'ancienne version de ce stub (contenu 100% fixe
    par type). Sans cette variation, deux appels de génération pour le même type (cycle
    `index % len(allowed_types)` dans `FakeAIProvider.generate_questionnaire`, courant dès
    que plus de questions sont demandées que de types autorisés) produisaient des
    questions structurellement ET textuellement identiques — exactement la classe de bug
    que la garde anti-doublon intra-session
    (`app.v1.session_service.deduplicate_intra_session`) doit détecter et rejeter, ce
    qu'elle faisait correctement mais qui n'était jusqu'ici jamais exercé par les tests
    utilisant ce stub (masqué par un contenu factice trop pauvre pour révéler le bug). La
    position de la bonne réponse (`correct_indexes`/`correct_categories`/`correct_pairs`/
    `correct_order`) reste inchangée par cette variation — seul le LIBELLÉ varie, jamais
    quel index est correct."""
    common = {"question_id": question_id, "type": question_type, "points_max": points_max}
    tag = _variation_clause(index)
    if question_type in ("single_choice", "true_false"):
        choices = ["Vrai", "Faux"] if question_type == "true_false" else [f"Option A{tag}", f"Option B{tag}"]
        return QuestionnaireQuestion(
            **common, prompt=f"Question factice à choix.{tag}", choices=choices, correct_indexes=[0]
        )
    if question_type == "multiple_choice":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Question factice à choix multiples.{tag}",
            choices=[f"Option A{tag}", f"Option B{tag}", f"Option C{tag}"],
            correct_indexes=[0, 2],
        )
    if question_type == "ordering":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Remets ces étapes factices dans l'ordre.{tag}",
            order_items=[f"Étape A{tag}", f"Étape B{tag}"],
            correct_order=[1, 0],
        )
    if question_type == "classification":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Classe ces éléments factices.{tag}",
            categories=[f"Catégorie 1{tag}", f"Catégorie 2{tag}"],
            elements=[f"Élément A{tag}", f"Élément B{tag}"],
            correct_categories=[0, 1],
        )
    if question_type == "matching":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Associe ces éléments factices.{tag}",
            pairs_left=[f"Gauche A{tag}", f"Gauche B{tag}"],
            pairs_right=[f"Droite A{tag}", f"Droite B{tag}"],
            correct_pairs=[0, 1],
        )
    if question_type == "numeric":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Combien font 2 + 2 (factice) ?{tag}",
            numeric_answer=4,
            numeric_tolerance=0,
        )
    if question_type == "fill_blank":
        return QuestionnaireQuestion(
            **common,
            prompt=f"Complète : la ___ vive est volatile (factice).{tag}",
            # `accepted_answers` est aussi un champ STRUCTUREL comparé par #64
            # (`dedup._STRUCTURAL_FIELDS`) — doit varier comme le prompt, sinon deux
            # instances de ce type restent un quasi-doublon malgré un prompt différent
            # (ticket #82 : découvert via `test_max_retries_respected_then_bank_fallback`
            # et les tests de comptage de questions AMPCR, qui généraient plusieurs
            # short_answer/vocabulary avec un `accepted_answers` strictement identique).
            accepted_answers=[f"mémoire{tag}"],
        )
    if question_type in ("short_answer", "vocabulary"):
        return QuestionnaireQuestion(
            **common,
            prompt=f"Question factice à réponse courte.{tag}",
            accepted_answers=[f"réponse factice{tag}"],
        )
    if question_type == "diagnostic":
        # Contient un marqueur concret (adresse IP factice) pour ne pas se faire rejeter
        # par `app.v1.quality_validation` (ticket #69, § « diagnostic autosuffisant ») —
        # ce garde-fou est un comportement RÉEL et voulu, pas une raison d'affaiblir le
        # contenu factice de test au point de ne plus ressembler à une vraie question.
        return QuestionnaireQuestion(
            **common,
            prompt=f"Poste factice à l'adresse 192.0.2.1. Quelle vérification effectues-tu ensuite ?{tag}",
            rubric="Grille de correction factice : vérifier la présence des notions clés.",
        )
    # long_answer / procedure : toujours sémantiques, nécessitent un rubric.
    return QuestionnaireQuestion(
        **common,
        prompt=f"Question factice de type {question_type}.{tag}",
        rubric="Grille de correction factice : vérifier la présence des notions clés.",
    )

"""Structures de données du moteur IA.

Toute donnée échangée avec un fournisseur IA passe par ces dataclasses : le reste de
l'application ne manipule jamais du texte libre non structuré renvoyé par un modèle de
langage (voir le complément IA du ticket #10 : « ne pas se contenter de texte libre si une
réponse JSON structurée peut rendre le système plus robuste »).

Le ticket #23 ajoute un contrat générique « questionnaire » (`QuestionnaireQuestion`,
`Questionnaire`, `QuestionnaireRequest`, `QuestionCorrection`, `QuestionnaireCorrection`),
destiné à être réutilisé par les tickets #24 (S'entraîner) et #25 (S'évaluer), pour toutes
les matières. Les structures à exercice unique (`GeneratedAIExercise`,
`AICorrectionResult`) introduites au ticket #10 restent inchangées : elles continuent
d'alimenter les blocs `ai_exercise` déjà déployés (MC01/MC02/MC03) — voir
`docs/claude-reports/2026-09-16_ticket-23_openai-contract.md` pour la justification de la
coexistence des deux contrats plutôt qu'un remplacement.
"""

import json
from dataclasses import dataclass, field
from typing import Any

from app.answer_checking import is_semantic_short_answer_prompt

DIFFICULTIES = ("facile", "moyen", "difficile")

EXERCISE_TYPES = (
    "réponse rédigée",
    "diagnostic",
    "classement",
    "calcul",
    "procédure",
    "mise en situation",
)

# --- Contrat générique « questionnaire » (ticket #23) ---------------------------------------

QUESTIONNAIRE_MODES = ("practice", "exam")

# Échelle interne à 5 niveaux (ticket #62, sélecteur UI 1-5) — "lenient"/"standard"/
# "strict" existaient déjà (ticket #23) et gardent leur sens/comportement inchangés ;
# "very_lenient"/"very_strict" étendent l'échelle aux deux extrêmes sans rien retirer.
SEVERITY_LEVELS = ("very_lenient", "lenient", "standard", "strict", "very_strict")

QUESTION_TYPES = (
    "single_choice",
    "multiple_choice",
    "true_false",
    "short_answer",
    "long_answer",
    "fill_blank",
    "matching",
    "classification",
    "ordering",
    "numeric",
    "diagnostic",
    "procedure",
    "vocabulary",
)

# Corrigés localement (jamais d'appel IA) : la réponse est structurée et la bonne réponse
# est connue à l'avance dans le rubric du questionnaire — voir app/ai/local_correction.py.
DETERMINISTIC_QUESTION_TYPES = frozenset(
    {
        "single_choice",
        "multiple_choice",
        "true_false",
        "fill_blank",
        "matching",
        "classification",
        "ordering",
        "numeric",
    }
)

# Corrigés localement UNIQUEMENT si leur rubric fournit `accepted_answers` (comparaison
# textuelle normalisée, comme `short_answer` dans app/editorial_exercise.py) ; sinon
# basculent en correction sémantique IA, comme les types ci-dessous — voir
# app/ai/local_correction.py::requires_ai_correction.
CONDITIONALLY_LOCAL_QUESTION_TYPES = frozenset({"short_answer", "vocabulary"})

# Toujours corrigés par appel IA : appréciation sémantique nécessaire, pas de réponse
# strictement déterministe possible.
ALWAYS_SEMANTIC_QUESTION_TYPES = frozenset({"long_answer", "diagnostic", "procedure"})


class QuestionnaireValidationError(ValueError):
    """Configuration de questionnaire structurellement invalide.

    Levée à la construction directe (auteurisation, tests) pour échouer tôt. Le chargement
    depuis une réponse IA (`Questionnaire.from_json`, JSON potentiellement mal formé ou
    hors contrat) ne la laisse jamais remonter : une question invalide est silencieusement
    ignorée plutôt que de faire échouer toute la génération — voir
    `Questionnaire.from_json`."""


@dataclass
class QuestionnaireQuestion:
    """Une question générique, toutes matières, tous types (voir `QUESTION_TYPES`).

    Champs spécifiques à un type — jamais transmis au candidat avant correction :
    `correct_indexes`, `correct_order`, `correct_categories`, `correct_pairs`,
    `numeric_answer`, `accepted_answers`, `rubric` (voir `to_public_dict`).
    """

    question_id: str
    type: str
    prompt: str
    points_max: float
    # single_choice / multiple_choice / true_false — public :
    choices: list[str] = field(default_factory=list)
    # single_choice / multiple_choice / true_false — privé (index dans `choices`) :
    correct_indexes: list[int] = field(default_factory=list)
    # ordering — order_items public, correct_order privé (permutation d'index) :
    order_items: list[str] = field(default_factory=list)
    correct_order: list[int] = field(default_factory=list)
    # classification — categories/elements publics, correct_categories privé :
    categories: list[str] = field(default_factory=list)
    elements: list[str] = field(default_factory=list)
    correct_categories: list[int] = field(default_factory=list)
    # matching — pairs_left/pairs_right publics, correct_pairs privé (un index dans
    # pairs_right par élément de pairs_left) :
    pairs_left: list[str] = field(default_factory=list)
    pairs_right: list[str] = field(default_factory=list)
    correct_pairs: list[int] = field(default_factory=list)
    # numeric — privé :
    numeric_answer: float | None = None
    numeric_tolerance: float = 0.0
    # short_answer / fill_blank / vocabulary — privé (voir CONDITIONALLY_LOCAL_QUESTION_TYPES) :
    accepted_answers: list[str] = field(default_factory=list)
    # long_answer / diagnostic / procedure / short_answer-vocabulary sans accepted_answers —
    # grille de correction transmise à l'IA, jamais au candidat :
    rubric: str = ""
    # commun — jamais transmis avant correction :
    explanation: str = ""

    def __post_init__(self) -> None:
        if not self.question_id:
            raise QuestionnaireValidationError("question_id est obligatoire.")
        if self.type not in QUESTION_TYPES:
            raise QuestionnaireValidationError(
                f"{self.question_id} : type de question inconnu : {self.type!r}."
            )
        if not self.prompt.strip():
            raise QuestionnaireValidationError(f"{self.question_id} : prompt vide.")
        if self.points_max <= 0:
            raise QuestionnaireValidationError(
                f"{self.question_id} : points_max doit être > 0."
            )

        if self.type in ("single_choice", "true_false"):
            if len(self.choices) < 2:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : au moins deux choix sont requis."
                )
            if len(self.correct_indexes) != 1 or not (
                0 <= self.correct_indexes[0] < len(self.choices)
            ):
                raise QuestionnaireValidationError(
                    f"{self.question_id} : correct_indexes invalide pour {self.type}."
                )
        elif self.type == "multiple_choice":
            if len(self.choices) < 2:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : au moins deux choix sont requis."
                )
            if not self.correct_indexes or any(
                not (0 <= i < len(self.choices)) for i in self.correct_indexes
            ):
                raise QuestionnaireValidationError(
                    f"{self.question_id} : correct_indexes invalide pour multiple_choice."
                )
        elif self.type == "ordering":
            if len(self.order_items) < 2:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : au moins deux éléments à ordonner sont requis."
                )
            if sorted(self.correct_order) != list(range(len(self.order_items))):
                raise QuestionnaireValidationError(
                    f"{self.question_id} : correct_order doit être une permutation valide."
                )
        elif self.type == "classification":
            if len(self.categories) < 2 or len(self.elements) < 2:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : au moins deux catégories et deux éléments sont "
                    "requis."
                )
            if len(self.correct_categories) != len(self.elements) or any(
                not (0 <= c < len(self.categories)) for c in self.correct_categories
            ):
                raise QuestionnaireValidationError(
                    f"{self.question_id} : correct_categories invalide."
                )
        elif self.type == "matching":
            if len(self.pairs_left) < 2 or len(self.pairs_right) < 2:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : au moins deux paires sont requises."
                )
            if len(self.correct_pairs) != len(self.pairs_left) or any(
                not (0 <= p < len(self.pairs_right)) for p in self.correct_pairs
            ):
                raise QuestionnaireValidationError(f"{self.question_id} : correct_pairs invalide.")
        elif self.type == "numeric":
            if self.numeric_answer is None:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : numeric_answer est requis pour numeric."
                )
            if self.numeric_tolerance < 0:
                raise QuestionnaireValidationError(
                    f"{self.question_id} : numeric_tolerance doit être >= 0."
                )
        elif self.type == "fill_blank" and not self.accepted_answers:
            raise QuestionnaireValidationError(
                f"{self.question_id} : accepted_answers est requis pour fill_blank."
            )
        elif self.type in ALWAYS_SEMANTIC_QUESTION_TYPES and not self.rubric.strip():
            raise QuestionnaireValidationError(
                f"{self.question_id} : rubric est requis pour {self.type}."
            )

    def requires_ai_correction(self) -> bool:
        if self.type in ALWAYS_SEMANTIC_QUESTION_TYPES:
            return True
        if self.type in CONDITIONALLY_LOCAL_QUESTION_TYPES:
            if not self.accepted_answers:
                return True
            # Ticket #90 § 2/9 : une short_answer/vocabulary qui demande une démarche/
            # justification/comparaison/explication ne doit JAMAIS être notée par égalité
            # textuelle stricte, même si accepted_answers est renseigné (SEMANTIC_SHORT,
            # à distinguer de DETERMINISTIC_SHORT — voir docstring de
            # `app.answer_checking.is_semantic_short_answer_prompt`).
            return is_semantic_short_answer_prompt(self.prompt)
        return False

    def to_public_dict(self) -> dict[str, Any]:
        """Représentation envoyée au candidat avant correction : jamais les champs de
        solution (`correct_*`, `numeric_answer`, `accepted_answers`, `rubric`,
        `explanation`)."""
        data: dict[str, Any] = {
            "question_id": self.question_id,
            "type": self.type,
            "prompt": self.prompt,
            "points_max": self.points_max,
        }
        if self.type in ("single_choice", "true_false", "multiple_choice"):
            data["choices"] = self.choices
        elif self.type == "ordering":
            data["order_items"] = self.order_items
        elif self.type == "classification":
            data["categories"] = self.categories
            data["elements"] = self.elements
        elif self.type == "matching":
            data["pairs_left"] = self.pairs_left
            data["pairs_right"] = self.pairs_right
        return data


@dataclass
class Questionnaire:
    mode: str
    questions: list[QuestionnaireQuestion] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.mode not in QUESTIONNAIRE_MODES:
            raise QuestionnaireValidationError(f"mode inconnu : {self.mode!r}.")
        ids = [question.question_id for question in self.questions]
        if len(ids) != len(set(ids)):
            raise QuestionnaireValidationError("question_id doit être unique dans un questionnaire.")

    @property
    def total_points_max(self) -> float:
        return sum(question.points_max for question in self.questions)

    def get_question(self, question_id: str) -> QuestionnaireQuestion | None:
        return next((q for q in self.questions if q.question_id == question_id), None)

    def to_json(self) -> str:
        return json.dumps(
            {
                "mode": self.mode,
                "questions": [
                    {
                        "question_id": q.question_id,
                        "type": q.type,
                        "prompt": q.prompt,
                        "points_max": q.points_max,
                        "choices": q.choices,
                        "correct_indexes": q.correct_indexes,
                        "order_items": q.order_items,
                        "correct_order": q.correct_order,
                        "categories": q.categories,
                        "elements": q.elements,
                        "correct_categories": q.correct_categories,
                        "pairs_left": q.pairs_left,
                        "pairs_right": q.pairs_right,
                        "correct_pairs": q.correct_pairs,
                        "numeric_answer": q.numeric_answer,
                        "numeric_tolerance": q.numeric_tolerance,
                        "accepted_answers": q.accepted_answers,
                        "rubric": q.rubric,
                        "explanation": q.explanation,
                    }
                    for q in self.questions
                ],
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, raw: str) -> "Questionnaire":
        """Chargement tolérant (réponse IA ou payload client re-soumis) : une question
        structurellement invalide est silencieusement ignorée plutôt que de faire échouer
        tout le questionnaire — voir `QuestionnaireValidationError`."""
        try:
            data = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}

        questions: list[QuestionnaireQuestion] = []
        for raw_question in data.get("questions", []):
            try:
                questions.append(
                    QuestionnaireQuestion(
                        question_id=raw_question.get("question_id", ""),
                        type=raw_question.get("type", ""),
                        prompt=raw_question.get("prompt", ""),
                        points_max=float(raw_question.get("points_max", 0) or 0),
                        choices=list(raw_question.get("choices") or []),
                        correct_indexes=list(raw_question.get("correct_indexes") or []),
                        order_items=list(raw_question.get("order_items") or []),
                        correct_order=list(raw_question.get("correct_order") or []),
                        categories=list(raw_question.get("categories") or []),
                        elements=list(raw_question.get("elements") or []),
                        correct_categories=list(raw_question.get("correct_categories") or []),
                        pairs_left=list(raw_question.get("pairs_left") or []),
                        pairs_right=list(raw_question.get("pairs_right") or []),
                        correct_pairs=list(raw_question.get("correct_pairs") or []),
                        numeric_answer=raw_question.get("numeric_answer"),
                        numeric_tolerance=float(raw_question.get("numeric_tolerance") or 0),
                        accepted_answers=list(raw_question.get("accepted_answers") or []),
                        rubric=raw_question.get("rubric", "") or "",
                        explanation=raw_question.get("explanation", "") or "",
                    )
                )
            except (QuestionnaireValidationError, TypeError, ValueError):
                continue

        mode = data.get("mode", "practice")
        if mode not in QUESTIONNAIRE_MODES:
            mode = "practice"
        try:
            return cls(mode=mode, questions=questions)
        except QuestionnaireValidationError:
            return cls(mode=mode, questions=[])

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "total_points_max": self.total_points_max,
            "questions": [question.to_public_dict() for question in self.questions],
        }


@dataclass(frozen=True)
class QuestionnaireRequest:
    """Entrée de `generate_questionnaire` — toujours bornée à un ou plusieurs contextes
    pédagogiques explicites, jamais à l'ensemble de la base (voir `PedagogicalContext`)."""

    contexts: tuple["PedagogicalContext", ...]
    mode: str
    difficulty: str
    question_count: int
    allowed_types: tuple[str, ...]
    total_points: float | None = None
    # Ticket #64 § 3 (anti-répétition, variantes réelles) : énoncés déjà vus par
    # l'utilisateur pour ce contexte, les plus récents en premier — transmis au prompt
    # (voir `app.ai.prompts.build_generate_questionnaire_messages`) pour que la génération
    # produise une VRAIE variante (autre scénario/valeur/matériel/symptôme/distracteurs/
    # ordre) plutôt qu'une question déjà couverte sous une autre forme. Optionnel et vide
    # par défaut : n'affecte aucun appelant existant (`app.editorial_ai_correction` ne
    # construit jamais de `QuestionnaireRequest`).
    avoid_prompts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.contexts:
            raise QuestionnaireValidationError("Au moins un contexte pédagogique est requis.")
        if self.mode not in QUESTIONNAIRE_MODES:
            raise QuestionnaireValidationError(f"mode inconnu : {self.mode!r}.")
        if self.difficulty not in DIFFICULTIES:
            raise QuestionnaireValidationError(f"difficulté inconnue : {self.difficulty!r}.")
        if self.question_count <= 0:
            raise QuestionnaireValidationError("question_count doit être > 0.")
        if not self.allowed_types or any(t not in QUESTION_TYPES for t in self.allowed_types):
            raise QuestionnaireValidationError("allowed_types contient un type inconnu ou est vide.")
        if self.total_points is not None and self.total_points <= 0:
            raise QuestionnaireValidationError("total_points doit être > 0 si fourni.")


@dataclass
class QuestionCorrection:
    question_id: str
    points_awarded: float
    points_max: float
    correct: bool
    strengths: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    feedback: str = ""
    expected_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "points_awarded": self.points_awarded,
            "points_max": self.points_max,
            "correct": self.correct,
            "strengths": self.strengths,
            "errors": self.errors,
            "missing": self.missing,
            "feedback": self.feedback,
            "expected_answer": self.expected_answer,
        }


@dataclass
class QuestionnaireCorrection:
    score: float
    max_score: float
    questions: list[QuestionCorrection] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.max_score <= 0:
            return 0.0
        return round(100 * self.score / self.max_score, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "questions": [question.to_dict() for question in self.questions],
        }


@dataclass(frozen=True)
class PedagogicalContext:
    """Contexte pédagogique borné transmis à l'IA — jamais l'ensemble de la base.

    Rédigé à la main pour chaque cours (voir `app/ai/context.py`) à partir du contenu
    réellement enseigné, jamais extrait automatiquement d'un bloc de contenu libre : ce sont
    les notions explicitement validées par ChatGPT (chef de projet, autorité pédagogique).
    """

    course_key: str
    course_title: str
    level: str
    allowed_notions: list[str]
    competencies: list[str]
    vocabulary: list[str]
    constraints: str = ""


@dataclass
class GeneratedAIExercise:
    exercise_type: str
    difficulty: str
    statement: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "exercise_type": self.exercise_type,
            "difficulty": self.difficulty,
            "statement": self.statement,
        }


@dataclass
class AICorrectionResult:
    appreciation: str
    correct_points: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    expected_answer_explained: str = ""
    score: float | None = None
    max_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "appreciation": self.appreciation,
            "correct_points": self.correct_points,
            "errors": self.errors,
            "expected_answer_explained": self.expected_answer_explained,
            "score": self.score,
            "max_score": self.max_score,
        }

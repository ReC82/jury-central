import json
from dataclasses import dataclass, field
from typing import Any

from app.answer_checking import answers_match, parse_answer
from app.content import render_markdown


@dataclass
class QuizConfig:
    question: str
    choices: list[str] = field(default_factory=list)
    correct_index: int = 0
    explanation: str = ""
    answer_type: str = "choice"  # "choice" (QCM / vrai-faux) ou "numeric" (réponse chiffrée)
    correct_value: str = ""  # utilisé seulement si answer_type == "numeric"
    group: str = ""  # regroupe plusieurs blocs quiz en un seul parcours (score, une question à la fois)
    order_in_group: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "question": self.question,
                "choices": self.choices,
                "correct_index": self.correct_index,
                "explanation": self.explanation,
                "answer_type": self.answer_type,
                "correct_value": self.correct_value,
                "group": self.group,
                "order_in_group": self.order_in_group,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, raw: str) -> "QuizConfig":
        try:
            data = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        return cls(
            question=data.get("question", ""),
            choices=list(data.get("choices", [])),
            correct_index=int(data.get("correct_index", 0)),
            explanation=data.get("explanation", ""),
            answer_type=data.get("answer_type", "choice"),
            correct_value=data.get("correct_value", ""),
            group=data.get("group", ""),
            order_in_group=int(data.get("order_in_group", 0)),
        )

    def check(self, submitted: str) -> bool:
        """Vérifie une réponse soumise. Ne révèle jamais la bonne réponse."""
        if self.answer_type == "numeric":
            expected = parse_answer(self.correct_value)
            if expected is None:
                return False
            return answers_match(expected, submitted)
        try:
            return int(submitted) == self.correct_index
        except (TypeError, ValueError):
            return False

    def to_public_dict(self, block_id: int) -> dict[str, Any]:
        """Données envoyées au navigateur : jamais la bonne réponse.

        `question_html` est le rendu du même contenu du Design System que le cours
        (`app/content.py::render_markdown`, voir docs/UI_GUIDELINES.md) : tableaux,
        listes et formules MathJax dans une question de quiz s'affichent correctement,
        au lieu d'une phrase brute.
        """
        return {
            "block_id": block_id,
            "question": self.question,
            "question_html": render_markdown(self.question),
            "choices": self.choices if self.answer_type == "choice" else [],
            "answer_type": self.answer_type,
        }


def build_quiz_config(
    question: str,
    choices: list[str],
    correct_raw_index: int,
    explanation: str = "",
) -> tuple[QuizConfig | None, str | None]:
    """Construit un QuizConfig QCM à partir de champs bruts (formulaire admin ou import CSV).

    `choices` peut contenir des entrées vides (elles sont filtrées). `correct_raw_index`
    est l'index (0-based) dans la liste brute `choices`, pas dans la liste filtrée.

    Retourne (config, None) si valide, ou (None, message_erreur) sinon.
    """
    question = question.strip()
    if not question:
        return None, "La question est obligatoire."

    filtered_choices = [c.strip() for c in choices if c.strip()]
    if len(filtered_choices) < 2:
        return None, "Il faut au moins deux réponses."

    if not (0 <= correct_raw_index < len(choices)):
        return None, "Le numéro de la réponse correcte est invalide."

    selected_raw = choices[correct_raw_index]
    if not selected_raw.strip():
        return None, "La réponse correcte doit correspondre à un choix rempli."

    correct_index = sum(1 for c in choices[:correct_raw_index] if c.strip())
    config = QuizConfig(
        question=question,
        choices=filtered_choices,
        correct_index=correct_index,
        explanation=explanation.strip(),
    )
    return config, None

import json
from dataclasses import dataclass, field


@dataclass
class QuizConfig:
    question: str
    choices: list[str] = field(default_factory=list)
    correct_index: int = 0
    explanation: str = ""

    def to_json(self) -> str:
        return json.dumps(
            {
                "question": self.question,
                "choices": self.choices,
                "correct_index": self.correct_index,
                "explanation": self.explanation,
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
        )


def build_quiz_config(
    question: str,
    choices: list[str],
    correct_raw_index: int,
    explanation: str = "",
) -> tuple[QuizConfig | None, str | None]:
    """Construit un QuizConfig à partir de champs bruts (formulaire admin ou import CSV).

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

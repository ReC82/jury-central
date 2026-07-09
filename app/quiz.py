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

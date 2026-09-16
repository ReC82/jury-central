"""Fournisseur IA réel : appelle l'API Chat Completions d'OpenAI, exclusivement côté
serveur.

La clé API n'est jamais transmise au navigateur ni journalisée : elle ne quitte cette
classe que dans l'en-tête HTTP `Authorization` d'une requête sortante vers OpenAI, jamais
dans un message d'erreur, une exception ou un log (voir `_headers`/`_call`). La sortie est
forcée en JSON strict (`response_format: json_schema`) : le modèle ne peut pas renvoyer de
texte libre non structuré (voir `app/ai/prompts.py`).
"""

import json
from typing import Any

import httpx

from app.ai.prompts import (
    CORRECT_JSON_SCHEMA,
    CORRECT_SEMANTIC_JSON_SCHEMA,
    GENERATE_JSON_SCHEMA,
    GENERATE_QUESTIONNAIRE_JSON_SCHEMA,
    build_correct_messages,
    build_correct_semantic_messages,
    build_generate_messages,
    build_generate_questionnaire_messages,
)
from app.ai.provider import AINotConfiguredError, AIResponseError, AITimeoutError
from app.ai.schemas import (
    AICorrectionResult,
    GeneratedAIExercise,
    PedagogicalContext,
    QuestionCorrection,
    Questionnaire,
    QuestionnaireQuestion,
    QuestionnaireRequest,
)

CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        if not api_key:
            raise AINotConfiguredError("OPENAI_API_KEY n'est pas configurée.")
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        # Ne jamais journaliser le résultat de cette méthode : il contient la clé API.
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _call(self, messages: list[dict[str, str]], json_schema: dict) -> dict:
        payload = {
            "model": self._model,
            "messages": messages,
            "response_format": {"type": "json_schema", "json_schema": json_schema},
            "temperature": 0.7,
        }
        try:
            response = httpx.post(
                CHAT_COMPLETIONS_URL,
                headers=self._headers(),
                json=payload,
                timeout=self._timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                "Le service de génération IA n'a pas répondu à temps."
            ) from exc
        except httpx.HTTPError as exc:
            # Le message de httpx.HTTPError ne contient jamais les en-têtes de la requête.
            raise AIResponseError(f"Erreur réseau vers le service IA : {exc}") from exc

        if response.status_code != 200:
            raise AIResponseError(
                f"Le service IA a répondu avec le statut {response.status_code}."
            )

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AIResponseError("Réponse du service IA illisible ou incomplète.") from exc

        if not isinstance(parsed, dict):
            raise AIResponseError("Réponse du service IA dans un format inattendu.")
        return parsed

    def generate_exercise(
        self, context: PedagogicalContext, difficulty: str
    ) -> GeneratedAIExercise:
        messages = build_generate_messages(context, difficulty)
        data = self._call(messages, GENERATE_JSON_SCHEMA)
        try:
            return GeneratedAIExercise(
                exercise_type=str(data["exercise_type"]),
                difficulty=difficulty,
                statement=str(data["statement"]),
            )
        except KeyError as exc:
            raise AIResponseError("Exercice généré incomplet.") from exc

    def correct_answer(
        self,
        context: PedagogicalContext,
        exercise_statement: str,
        exercise_type: str,
        difficulty: str,
        candidate_answer: str,
    ) -> AICorrectionResult:
        messages = build_correct_messages(
            context, exercise_statement, exercise_type, difficulty, candidate_answer
        )
        data = self._call(messages, CORRECT_JSON_SCHEMA)
        try:
            return AICorrectionResult(
                appreciation=str(data["appreciation"]),
                correct_points=[str(item) for item in data.get("correct_points") or []],
                errors=[str(item) for item in data.get("errors") or []],
                expected_answer_explained=str(data.get("expected_answer_explained", "")),
                score=data.get("score"),
                max_score=data.get("max_score"),
            )
        except KeyError as exc:
            raise AIResponseError("Correction incomplète.") from exc

    def generate_questionnaire(self, request: QuestionnaireRequest) -> Questionnaire:
        """Un seul appel. Ne filtre ni ne reclasse rien : la politique de retry borné, de
        filtrage par `allowed_types` et de recalage de `points_max` sur `total_points` vit
        dans l'orchestrateur `app/ai/questionnaire.py::generate_questionnaire`, identique
        quel que soit le fournisseur (réel ou factice)."""
        messages = build_generate_questionnaire_messages(request)
        data = self._call(messages, GENERATE_QUESTIONNAIRE_JSON_SCHEMA)
        # Réutilise le chargement tolérant déjà éprouvé pour les blocs `editorial_exercise`
        # (une question structurellement invalide est ignorée plutôt que de faire échouer
        # tout le questionnaire) : voir Questionnaire.from_json.
        questionnaire = Questionnaire.from_json(json.dumps(data))
        if not questionnaire.questions:
            # Réponse reçue mais aucune question exploitable (liste vide, ou toutes
            # invalides et filtrées par le chargement tolérant) : signalé comme une
            # réponse invalide — l'orchestrateur (app/ai/questionnaire.py) décide d'un
            # nombre borné de nouvelles tentatives, jamais un questionnaire vide silencieux.
            raise AIResponseError("Aucune question exploitable dans la réponse du service IA.")
        return questionnaire

    def correct_semantic_batch(
        self,
        questions: list[QuestionnaireQuestion],
        answers: dict[str, Any],
        severity: str,
        contexts: list[PedagogicalContext],
    ) -> dict[str, QuestionCorrection]:
        """Un seul appel pour tout le lot de questions sémantiques — jamais un appel par
        question (voir la contrainte de coût du ticket #23). `points_max` n'est jamais lu
        depuis la réponse du modèle : il est toujours repris de `questions` (source de
        vérité serveur, voir `app/ai/questionnaire.py`)."""
        messages = build_correct_semantic_messages(questions, answers, severity, tuple(contexts))
        data = self._call(messages, CORRECT_SEMANTIC_JSON_SCHEMA)
        points_max_by_id = {question.question_id: question.points_max for question in questions}

        results: dict[str, QuestionCorrection] = {}
        for raw_correction in data.get("corrections") or []:
            try:
                question_id = str(raw_correction["question_id"])
                points_max = points_max_by_id.get(question_id)
                if points_max is None:
                    continue  # id inconnu du lot envoyé — ignoré, jamais fait confiance
                points_awarded = float(raw_correction["points_awarded"])
                results[question_id] = QuestionCorrection(
                    question_id=question_id,
                    points_awarded=points_awarded,
                    points_max=points_max,
                    correct=bool(raw_correction.get("correct", False)),
                    strengths=[str(item) for item in raw_correction.get("strengths") or []],
                    errors=[str(item) for item in raw_correction.get("errors") or []],
                    missing=[str(item) for item in raw_correction.get("missing") or []],
                    feedback=str(raw_correction.get("feedback", "")),
                    expected_answer=str(raw_correction.get("expected_answer", "")),
                )
            except (KeyError, TypeError, ValueError):
                continue
        return results
